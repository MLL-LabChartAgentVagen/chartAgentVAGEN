"""
Sprint 8 — Sandbox execution and error feedback loop.

Subtask IDs covered: 7.1.1, 7.1.2, 7.1.3

This module implements the §2.7 execution-error feedback loop:

- ``execute_in_sandbox`` (7.1.1) compiles and executes LLM-generated
  Python code in a restricted ``exec()`` namespace, captures the
  ``(DataFrame, dict)`` result or any raised exception + traceback.

- ``format_error_feedback`` (7.1.2) assembles the four-component error
  payload (original code, exception class, traceback, fix instruction)
  that is fed back to the LLM on retry.

- ``run_retry_loop`` (7.1.3) orchestrates the full §2.7 loop: execute →
  on failure, format feedback → call LLM for new code → retry, up to
  ``max_retries`` times.

Security note (Finding A14):
    The sandbox uses a restricted ``__builtins__`` allowlist and injects
    only the SDK into the execution namespace.  Full process-level
    isolation (RestrictedPython, subprocess containers, resource cgroups)
    is deferred until Finding A14 is resolved.  The current approach is
    sufficient for trusted-LLM usage within the AGPDS pipeline.
"""
from __future__ import annotations

import logging
import threading
import traceback as tb_module
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import pandas as pd

from agpds.exceptions import InvalidParameterError, SimulatorError

logger: logging.Logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_TIMEOUT_SECONDS: int = 30
DEFAULT_MAX_RETRIES: int = 3

# Builtins allowlist — enough for SDK scripts to function but blocking
# dangerous primitives like __import__, eval, exec, open, compile.
# SPEC_AMBIGUOUS: Finding A14 notes that the security policy is
# unspecified.  This allowlist is a best-effort safe default pending
# formal policy resolution.
_SAFE_BUILTINS: dict[str, Any] = {
    # Constructors & type conversions
    "True": True,
    "False": False,
    "None": None,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "set": set,
    "frozenset": frozenset,
    "range": range,
    "len": len,
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "round": round,
    "sorted": sorted,
    "reversed": reversed,
    "enumerate": enumerate,
    "zip": zip,
    "map": map,
    "filter": filter,
    "isinstance": isinstance,
    "issubclass": issubclass,
    "type": type,
    "hasattr": hasattr,
    "getattr": getattr,
    "setattr": setattr,
    "print": print,  # Harmless; captured by exec namespace
    "repr": repr,
    "id": id,
    "hash": hash,
    "callable": callable,
    "iter": iter,
    "next": next,
    "super": super,
    "property": property,
    "staticmethod": staticmethod,
    "classmethod": classmethod,
    "object": object,
    "Exception": Exception,
    "ValueError": ValueError,
    "TypeError": TypeError,
    "KeyError": KeyError,
    "IndexError": IndexError,
    "AttributeError": AttributeError,
    "RuntimeError": RuntimeError,
    "StopIteration": StopIteration,
    "NotImplementedError": NotImplementedError,
    # __import__ is intentionally omitted — SDK modules are pre-injected
}


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class SandboxResult:
    """Result of a single sandbox execution attempt.

    [Subtask 7.1.1]

    Attributes:
        success: ``True`` if ``build_fact_table()`` returned a valid
            ``(DataFrame, dict)`` tuple.
        dataframe: The generated DataFrame on success; ``None`` on failure.
        metadata: The schema metadata dict on success; ``None`` on failure.
        exception: The captured exception on failure; ``None`` on success.
        traceback_str: Formatted traceback on failure; ``None`` on success.
    """
    # FIX: [self-review item 1] — dataclass field block now has comment
    # Result state fields: success flag and either data or error slots
    success: bool
    dataframe: Optional[pd.DataFrame] = None
    metadata: Optional[dict[str, Any]] = None
    exception: Optional[Exception] = None
    traceback_str: Optional[str] = None


@dataclass
class RetryLoopResult:
    """Result of the full §2.7 retry loop.

    [Subtask 7.1.3]

    Attributes:
        success: ``True`` if any attempt succeeded within the budget.
        dataframe: The generated DataFrame from the successful attempt.
        metadata: The schema metadata dict from the successful attempt.
        attempts: Total number of attempts made (1-based).
        history: Ordered list of per-attempt :class:`SandboxResult` s.
    """
    # Aggregate result fields: outcome, data, attempt tracking, and history
    success: bool
    dataframe: Optional[pd.DataFrame] = None
    metadata: Optional[dict[str, Any]] = None
    attempts: int = 0
    history: list[SandboxResult] = field(default_factory=list)


# =============================================================================
# Sandbox Namespace Builder
# =============================================================================

def _build_sandbox_namespace() -> dict[str, Any]:
    """Construct the execution namespace injected into ``exec()``.

    The namespace pre-loads the SDK import so the LLM script's
    ``from chartagent.synth import FactTableSimulator`` resolves without
    needing a real ``__import__`` builtin.  If the SDK is not importable
    in the current environment, the namespace still contains the safe
    builtins and the script will fail with a clear NameError.

    Returns:
        A dict suitable as the ``globals`` argument to ``exec()``.
    """
    # Start with restricted builtins — __import__ is intentionally absent
    namespace: dict[str, Any] = {
        "__builtins__": _SAFE_BUILTINS,
    }

    # Attempt to pre-inject the SDK so that `from chartagent.synth import
    # FactTableSimulator` works even without __import__.  We do this by
    # creating a minimal module shim in the namespace.
    try:
        # Try the real import path
        from agpds.simulator import FactTableSimulator
        namespace["FactTableSimulator"] = FactTableSimulator

        # Provide a custom __import__ that only allows the SDK package
        # so that the one-shot example's import statement resolves
        def _restricted_import(
            name: str,
            globals: dict | None = None,
            locals: dict | None = None,
            fromlist: tuple = (),
            level: int = 0,
        ) -> Any:
            """Import gate that only permits the SDK and its aliases."""
            # Allow the chartagent.synth alias used in the §2.5 one-shot
            if name in ("chartagent.synth", "chartagent", "agpds", "agpds.simulator"):
                import types
                mod = types.ModuleType(name)
                mod.FactTableSimulator = FactTableSimulator  # type: ignore[attr-defined]
                return mod
            raise ImportError(
                f"Import of '{name}' is not permitted in the sandbox. "
                f"Only the FactTableSimulator SDK is available."
            )

        namespace["__builtins__"]["__import__"] = _restricted_import

    except ImportError:
        # SDK not available in this environment (e.g. unit tests running
        # without the full package).  Leave namespace without the SDK;
        # the script will produce a NameError for FactTableSimulator which
        # the sandbox captures normally.
        logger.debug(
            "FactTableSimulator not importable — sandbox namespace will "
            "lack SDK pre-injection; scripts must self-provide."
        )

    return namespace


# =============================================================================
# Sandbox Executor (7.1.1)
# =============================================================================

class _SandboxThread(threading.Thread):
    """Worker thread that compiles and executes the LLM script.

    Using a thread (rather than ``signal.alarm``) allows timeouts to
    work regardless of whether the caller is the main thread — important
    for server / async contexts.
    """

    def __init__(self, source_code: str, namespace: dict[str, Any]) -> None:
        super().__init__(daemon=True)
        # FIX: [self-review item 1] — added comment for this init block
        # Store script and namespace; initialize result/error slots to
        # None so the caller can distinguish "not yet run" from "ran
        # and produced None"
        self.source_code = source_code
        self.namespace = namespace
        self.result: Any = None
        self.exception: Exception | None = None
        self.traceback_str: str | None = None

    def run(self) -> None:
        try:
            # Compile first so SyntaxErrors are caught cleanly
            compiled = compile(self.source_code, "<llm_script>", "exec")

            # Execute the full script — this defines build_fact_table()
            exec(compiled, self.namespace)  # noqa: S102 — intentional sandbox exec

            # Retrieve and call build_fact_table from the namespace
            build_fn = self.namespace.get("build_fact_table")
            if build_fn is None:
                raise RuntimeError(
                    "LLM script did not define a 'build_fact_table' function. "
                    "§2.5 requires 'def build_fact_table(seed=...)'."
                )

            # Call the user-defined function to get the result tuple
            self.result = build_fn()

        except Exception as exc:
            # Capture both the exception and formatted traceback so the
            # caller can include them in the §2.7 error feedback payload
            self.exception = exc
            self.traceback_str = tb_module.format_exc()


def execute_in_sandbox(
    source_code: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    # FIX: [self-review item 2] — additive parameter not in the Message 1
    # interface sketch; required because the default namespace builder
    # imports agpds.simulator.FactTableSimulator which doesn't exist yet.
    # Defaults to None (non-breaking).
    sandbox_namespace: dict[str, Any] | None = None,
) -> SandboxResult:
    """Execute LLM-generated code in a restricted sandbox.

    [Subtask 7.1.1]

    The sandbox workflow:

    1. Validates inputs (fail-fast on empty/invalid arguments).
    2. Builds a restricted execution namespace with safe builtins and
       the SDK pre-injected.
    3. Spawns a daemon thread that ``compile()`` s + ``exec()`` s the
       source code, then calls ``build_fact_table()``.
    4. Joins the thread with the specified timeout.
    5. On success, validates the return value is ``(DataFrame, dict)``
       and wraps it in a :class:`SandboxResult`.
    6. On any exception (including ``TimeoutError``), captures the
       exception object and traceback string.

    Args:
        source_code: Python source code string containing a
            ``def build_fact_table(...)`` function.
        timeout_seconds: Maximum wall-clock seconds for execution.
            Must be > 0.
        sandbox_namespace: Optional pre-built namespace dict.  If
            ``None``, :func:`_build_sandbox_namespace` is called.
            Exposed for testing.

    Returns:
        :class:`SandboxResult` with either the success tuple or the
        captured error.

    Raises:
        InvalidParameterError: If *source_code* is empty/None or
            *timeout_seconds* is <= 0.
    """
    # ===== Input Validation =====

    # Reject None source code
    if source_code is None:
        raise InvalidParameterError(
            param_name="source_code",
            value=0.0,
            reason="source_code must not be None",
        )

    # Reject non-string source code
    if not isinstance(source_code, str):
        raise InvalidParameterError(
            param_name="source_code",
            value=0.0,
            reason=f"source_code must be a str, got {type(source_code).__name__}",
        )

    # Reject empty source code
    if len(source_code.strip()) == 0:
        raise InvalidParameterError(
            param_name="source_code",
            value=0.0,
            reason="source_code must be a non-empty string",
        )

    # Reject non-positive timeout
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        raise InvalidParameterError(
            param_name="timeout_seconds",
            value=float(timeout_seconds) if isinstance(timeout_seconds, (int, float)) else 0.0,
            reason="timeout_seconds must be a positive number",
        )

    # ===== Namespace Setup =====

    # Build or reuse the restricted execution namespace
    namespace = sandbox_namespace if sandbox_namespace is not None else _build_sandbox_namespace()

    # ===== Threaded Execution =====

    worker = _SandboxThread(source_code, namespace)
    worker.start()

    # Block until the worker finishes or the timeout expires
    worker.join(timeout=timeout_seconds)

    # ===== Timeout Check =====

    # If the thread is still alive after join, it exceeded the budget
    if worker.is_alive():
        logger.debug(
            "Sandbox execution timed out after %d seconds", timeout_seconds
        )
        return SandboxResult(
            success=False,
            exception=TimeoutError(
                f"build_fact_table() exceeded the {timeout_seconds}s timeout."
            ),
            traceback_str=(
                f"TimeoutError: build_fact_table() exceeded the "
                f"{timeout_seconds}s execution timeout.\n"
                f"  The generated code may contain an infinite loop or "
                f"an excessively expensive computation."
            ),
        )

    # ===== Error Check =====

    # If the worker caught an exception, propagate it as a failed result
    if worker.exception is not None:
        logger.debug(
            "Sandbox execution failed: %s: %s",
            type(worker.exception).__name__,
            worker.exception,
        )
        return SandboxResult(
            success=False,
            exception=worker.exception,
            traceback_str=worker.traceback_str or str(worker.exception),
        )

    # ===== Result Validation =====

    raw_result = worker.result

    # The §2.8 contract requires build_fact_table to return (DataFrame, dict)
    # [Assumption A12].  Validate the shape of the return value.
    if raw_result is None:
        return SandboxResult(
            success=False,
            exception=TypeError(
                "build_fact_table() returned None. "
                "Expected Tuple[pd.DataFrame, dict]."
            ),
            traceback_str=(
                "TypeError: build_fact_table() returned None.\n"
                "  The function must return sim.generate(), which "
                "produces (DataFrame, schema_metadata)."
            ),
        )

    # Check that the result is a tuple-like with exactly 2 elements
    if not isinstance(raw_result, (tuple, list)) or len(raw_result) != 2:
        return SandboxResult(
            success=False,
            exception=TypeError(
                f"build_fact_table() returned {type(raw_result).__name__} "
                f"with {len(raw_result) if hasattr(raw_result, '__len__') else '?'} "
                f"elements. Expected Tuple[pd.DataFrame, dict]."
            ),
            traceback_str=(
                f"TypeError: build_fact_table() returned an unexpected type.\n"
                f"  Got: {type(raw_result).__name__}\n"
                f"  Expected: Tuple[pd.DataFrame, dict] from sim.generate()."
            ),
        )

    df_candidate, meta_candidate = raw_result

    # Validate the first element is a DataFrame
    if not isinstance(df_candidate, pd.DataFrame):
        return SandboxResult(
            success=False,
            exception=TypeError(
                f"build_fact_table()[0] is {type(df_candidate).__name__}, "
                f"expected pd.DataFrame."
            ),
            traceback_str=(
                f"TypeError: First element of return tuple is "
                f"{type(df_candidate).__name__}, not pd.DataFrame."
            ),
        )

    # Validate the second element is a dict
    if not isinstance(meta_candidate, dict):
        return SandboxResult(
            success=False,
            exception=TypeError(
                f"build_fact_table()[1] is {type(meta_candidate).__name__}, "
                f"expected dict."
            ),
            traceback_str=(
                f"TypeError: Second element of return tuple is "
                f"{type(meta_candidate).__name__}, not dict."
            ),
        )

    # ===== Success =====

    logger.debug(
        "Sandbox execution succeeded: DataFrame(%d rows, %d cols), "
        "metadata(%d keys)",
        len(df_candidate),
        len(df_candidate.columns),
        len(meta_candidate),
    )

    return SandboxResult(
        success=True,
        dataframe=df_candidate,
        metadata=meta_candidate,
    )


# =============================================================================
# Error Feedback Formatter (7.1.2)
# =============================================================================

# The fix instruction text matches §2.7 step 5 wording verbatim
_FIX_INSTRUCTION: str = (
    "The script above raised an error during sandbox execution. "
    "Adjust parameters to resolve the error. "
    "Return only the corrected Python script."
)


def format_error_feedback(
    original_code: str,
    exception: Exception,
    traceback_str: str,
) -> str:
    """Format error feedback for LLM retry prompt per §2.7 step 5.

    [Subtask 7.1.2]

    Assembles the four components specified by the task hierarchy:

    1. The original source code that failed.
    2. The exception class name (e.g. ``CyclicDependencyError``).
    3. The full traceback string.
    4. A natural-language fix instruction directing the LLM to adjust
       parameters.

    Args:
        original_code: The Python source code that raised the error.
        exception: The captured exception object.
        traceback_str: The formatted traceback string.

    Returns:
        A single formatted string containing all four components,
        delimited by clear section headers for LLM readability.

    Raises:
        InvalidParameterError: If any required argument is ``None``
            or empty.
    """
    # ===== Input Validation =====

    # Validate original_code is present
    if original_code is None or (isinstance(original_code, str) and len(original_code.strip()) == 0):
        raise InvalidParameterError(
            param_name="original_code",
            value=0.0,
            reason="original_code must be a non-empty string",
        )

    # Validate exception is present
    if exception is None:
        raise InvalidParameterError(
            param_name="exception",
            value=0.0,
            reason="exception must not be None",
        )

    # Validate traceback_str is present
    if traceback_str is None or (isinstance(traceback_str, str) and len(traceback_str.strip()) == 0):
        raise InvalidParameterError(
            param_name="traceback_str",
            value=0.0,
            reason="traceback_str must be a non-empty string",
        )

    # ===== Format the Four Components =====

    # Extract exception class name and message for the ERROR section
    exception_class = type(exception).__name__
    exception_message = str(exception)

    # Structure the feedback with clear section headers so the LLM can
    # parse each component unambiguously
    feedback = (
        "=== ORIGINAL CODE ===\n"
        f"{original_code}\n"
        "\n"
        "=== ERROR ===\n"
        f"Exception: {exception_class}: {exception_message}\n"
        "\n"
        "=== TRACEBACK ===\n"
        f"{traceback_str}\n"
        "\n"
        "=== INSTRUCTION ===\n"
        f"{_FIX_INSTRUCTION}"
    )

    logger.debug(
        "Formatted error feedback for %s (%d chars)",
        exception_class,
        len(feedback),
    )

    return feedback


# =============================================================================
# Retry Loop (7.1.3)
# =============================================================================

def run_retry_loop(
    initial_code: str,
    llm_generate_fn: Callable[[str, str], str],
    system_prompt: str,
    max_retries: int = DEFAULT_MAX_RETRIES,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    # FIX: [self-review item 2] — additive parameter not in the Message 1
    # interface sketch; required so tests can inject a namespace factory
    # that provides full builtins instead of the restricted set (which
    # depends on agpds.simulator not yet existing).  Defaults to None
    # (non-breaking).
    sandbox_namespace_factory: Callable[[], dict[str, Any]] | None = None,
) -> RetryLoopResult:
    """Execute the §2.7 error feedback retry loop.

    [Subtask 7.1.3]

    Algorithm:

    1. Execute *initial_code* in the sandbox.
    2. On success → return the result immediately (attempt 1).
    3. On failure → format error feedback, call *llm_generate_fn* with
       ``(system_prompt, feedback_prompt)`` to obtain new code.
    4. Repeat from step 1 with the new code, up to *max_retries* total
       attempts.
    5. On exhaustion → log the failure and return an unsuccessful
       :class:`RetryLoopResult` with the full attempt history.

    This loop implements **only** the §2.7 execution-error path.  It
    does not invoke §2.9 validation — that responsibility belongs to
    the pipeline orchestrator (11.1.x, currently BLOCKED per C5).

    Args:
        initial_code: First LLM-generated Python code string.
        llm_generate_fn: Callable ``(system_prompt, user_prompt) -> str``
            that calls the LLM and returns new code.  Typically
            ``LLMClient.generate_code`` (partially applied).
        system_prompt: The system prompt for retry LLM calls.
        max_retries: Maximum total attempts (default 3).  Must be > 0.
        timeout_seconds: Per-attempt execution timeout in seconds.
        sandbox_namespace_factory: Optional factory for sandbox
            namespaces.  Called once per attempt.  If ``None``, uses
            :func:`_build_sandbox_namespace`.

    Returns:
        :class:`RetryLoopResult` with the outcome and full history.

    Raises:
        InvalidParameterError: If *initial_code*, *system_prompt*, or
            *max_retries* fail validation.
    """
    # ===== Input Validation =====

    # Validate initial_code
    if initial_code is None or (isinstance(initial_code, str) and len(initial_code.strip()) == 0):
        raise InvalidParameterError(
            param_name="initial_code",
            value=0.0,
            reason="initial_code must be a non-empty string",
        )

    # Validate system_prompt
    if system_prompt is None or (isinstance(system_prompt, str) and len(system_prompt.strip()) == 0):
        raise InvalidParameterError(
            param_name="system_prompt",
            value=0.0,
            reason="system_prompt must be a non-empty string",
        )

    # Validate max_retries is a positive integer
    if not isinstance(max_retries, int) or max_retries <= 0:
        raise InvalidParameterError(
            param_name="max_retries",
            value=float(max_retries) if isinstance(max_retries, (int, float)) else 0.0,
            reason="max_retries must be a positive integer",
        )

    # Validate timeout_seconds is positive
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        raise InvalidParameterError(
            param_name="timeout_seconds",
            value=float(timeout_seconds) if isinstance(timeout_seconds, (int, float)) else 0.0,
            reason="timeout_seconds must be a positive number",
        )

    # ===== Retry Loop =====

    current_code = initial_code
    history: list[SandboxResult] = []

    # Resolve the namespace factory — default to the module-level builder
    ns_factory = sandbox_namespace_factory or _build_sandbox_namespace

    for attempt in range(1, max_retries + 1):

        logger.debug(
            "§2.7 retry loop: attempt %d/%d", attempt, max_retries
        )

        # Execute the current code in a fresh sandbox namespace so that
        # each attempt starts from a clean state
        sandbox_ns = ns_factory()
        result = execute_in_sandbox(
            source_code=current_code,
            timeout_seconds=timeout_seconds,
            sandbox_namespace=sandbox_ns,
        )
        history.append(result)

        # ===== Early Exit on Success =====

        if result.success:
            logger.debug(
                "§2.7 retry loop: succeeded on attempt %d", attempt
            )
            return RetryLoopResult(
                success=True,
                dataframe=result.dataframe,
                metadata=result.metadata,
                attempts=attempt,
                history=history,
            )

        # ===== Prepare Feedback for Next Attempt =====

        # Don't call the LLM after the final failed attempt — there is
        # no subsequent attempt to use the new code
        if attempt < max_retries:
            # Format the §2.7 step-5 error feedback payload
            feedback_prompt = format_error_feedback(
                original_code=current_code,
                exception=result.exception or RuntimeError("Unknown sandbox failure"),
                traceback_str=result.traceback_str or "No traceback available.",
            )

            logger.debug(
                "§2.7 retry loop: calling LLM for corrected code "
                "(attempt %d failed with %s)",
                attempt,
                type(result.exception).__name__ if result.exception else "unknown",
            )

            # Call the LLM to generate corrected code.  The LLM
            # receives the system prompt and the error feedback as the
            # user prompt.
            try:
                current_code = llm_generate_fn(system_prompt, feedback_prompt)
            except Exception as llm_exc:
                # If the LLM call itself fails, log and continue to the
                # next iteration with the same (broken) code — degraded
                # mode that avoids crashing the entire pipeline
                logger.debug(
                    "§2.7 retry loop: LLM call failed on attempt %d: %s",
                    attempt,
                    llm_exc,
                )

    # ===== Exhaustion =====

    logger.debug(
        "§2.7 retry loop: all %d attempts exhausted — returning failure",
        max_retries,
    )

    return RetryLoopResult(
        success=False,
        attempts=max_retries,
        history=history,
    )
