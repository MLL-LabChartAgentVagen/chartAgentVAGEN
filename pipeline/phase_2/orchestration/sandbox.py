"""
Sprint 8 — Sandbox execution and error feedback loop.

Subtask IDs covered: 7.1.1, 7.1.2 (the 7.1.3 retry driver lives in
:mod:`pipeline.phase_2.orchestration.retry_loop` after Sprint D.2).

This module implements the §2.7 execution-error feedback loop primitives:

- ``execute_in_sandbox`` (7.1.1) compiles and executes LLM-generated
  Python code in a restricted ``exec()`` namespace, captures the
  ``(DataFrame, dict)`` result or any raised exception + traceback.

- ``format_error_feedback`` (7.1.2) assembles the four-component error
  payload (original code, exception class, traceback, fix instruction)
  that is fed back to the LLM on retry.

The full retry driver — ``run_retry_loop`` — is in
:mod:`pipeline.phase_2.orchestration.retry_loop`; it consumes the two
primitives above. The seed parameter still flows through both modules.

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

from ..exceptions import InvalidParameterError, SimulatorError
from ..types import SandboxResult

logger: logging.Logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_TIMEOUT_SECONDS: int = 30

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
        from ..sdk.simulator import FactTableSimulator

        # Capture simulator instances for raw_declarations extraction
        _sim_registry: list = []
        namespace["_sim_registry"] = _sim_registry

        class _TrackingSimulator(FactTableSimulator):
            """Thin subclass that registers instances for post-execution extraction."""
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                _sim_registry.append(self)

        namespace["FactTableSimulator"] = _TrackingSimulator

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
            if name in ("chartagent.synth", "chartagent", "phase_2", "phase_2.simulator", "phase_2.sdk.simulator"):
                import types
                mod = types.ModuleType(name)
                mod.FactTableSimulator = _TrackingSimulator  # type: ignore[attr-defined]
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

    def __init__(self, source_code: str, namespace: dict[str, Any], seed: int = 42) -> None:
        super().__init__(daemon=True)
        # Store script and namespace; initialize result/error slots to
        # None so the caller can distinguish "not yet run" from "ran
        # and produced None"
        self.source_code = source_code
        self.namespace = namespace
        self.seed = seed
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

            # Call the user-defined function with the explicit seed so the
            # AGPDSPipeline-level seed reaches FactTableSimulator. The LLM's
            # default in the script signature is overridden here.
            self.result = build_fn(seed=self.seed)

        except Exception as exc:
            # Capture both the exception and formatted traceback so the
            # caller can include them in the §2.7 error feedback payload
            self.exception = exc
            self.traceback_str = tb_module.format_exc()

def execute_in_sandbox(
    source_code: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    sandbox_namespace: dict[str, Any] | None = None,
    seed: int = 42,
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

    worker = _SandboxThread(source_code, namespace, seed=seed)
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

    # Extract raw_declarations from the last simulator instance if available
    raw_declarations = None
    sim_registry = namespace.get("_sim_registry", [])
    if sim_registry:
        sim = sim_registry[-1]  # last instantiated simulator
        raw_declarations = {
            "columns": sim._columns,
            "groups": sim._groups,
            "group_dependencies": sim._group_dependencies,
            "measure_dag": sim._measure_dag,
            "target_rows": sim.target_rows,
            "patterns": sim._patterns,
            "seed": sim.seed,
            "orthogonal_pairs": sim._orthogonal_pairs,
        }

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
        raw_declarations=raw_declarations,
        source_code=source_code,
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

# Stronger instruction used when prior failures are available — tells the LLM
# to avoid reintroducing any of the listed errors while fixing the current one.
_FIX_INSTRUCTION_WITH_HISTORY: str = (
    "The script above raised an error during sandbox execution. "
    "Adjust parameters to resolve the CURRENT error while ALSO avoiding every "
    "error listed under PRIOR FAILED ATTEMPTS. Return only the corrected Python script."
)

# Per-error-class corrective hints surfaced to the LLM when the raw exception
# message describes the symptom but not the schema fix. Each entry is
# (predicate, hint_text); the first matching predicate wins. Keep this list
# tight — broad predicates here mask real errors.
_YEARLY_GRAIN_HINT: str = (
    "HINT: For yearly-grain data, do NOT call add_temporal. "
    "The SDK does not support freq='YS' or derive=['year']. "
    "Declare year as a categorical column instead: "
    "add_category('year', values=[2019, 2020, ...], group='time'). "
    "Reference 'year' in measure effects like any other categorical."
)
_RESERVED_TIME_GROUP_HINT: str = (
    "HINT: The group name 'time' is reserved for columns declared via "
    "add_temporal. For a categorical year (or other calendar-like) column, "
    "use a different group name such as group='calendar'."
)
_TARGETED_HINTS: list[tuple[Callable[[str], bool], str]] = [
    (
        lambda m: "Invalid derive features" in m and "'year'" in m,
        _YEARLY_GRAIN_HINT,
    ),
    (
        lambda m: "Unsupported freq 'YS'" in m,
        _YEARLY_GRAIN_HINT,
    ),
    (
        lambda m: "'time' is reserved" in m,
        _RESERVED_TIME_GROUP_HINT,
    ),
]


def format_error_feedback(
    original_code: str,
    exception: Exception,
    traceback_str: str,
    prior_failures: list["SandboxResult"] | None = None,
) -> str:
    """Format error feedback for LLM retry prompt per §2.7 step 5.

    [Subtask 7.1.2]

    Assembles up to five components:

    1. (optional) A `PRIOR FAILED ATTEMPTS` section listing class + message
       of each earlier failed attempt — used to prevent whack-a-mole retries
       where the LLM fixes the shown error but reintroduces a previously-fixed one.
    2. The original source code that failed.
    3. The exception class name (e.g. ``CyclicDependencyError``).
    4. The full traceback string.
    5. A natural-language fix instruction directing the LLM to adjust parameters
       (strengthened to reference prior failures when any are present).

    Args:
        original_code: The Python source code that raised the error.
        exception: The captured exception object (current attempt).
        traceback_str: The formatted traceback string (current attempt).
        prior_failures: Optional list of earlier failed SandboxResult objects.
            Only `exception` is read from each; tracebacks are intentionally
            omitted to save tokens.

    Returns:
        A single formatted string containing all present components,
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

    # ===== Format the Components =====

    # Extract exception class name and message for the ERROR section
    exception_class = type(exception).__name__
    exception_message = str(exception)

    # Optional PRIOR FAILED ATTEMPTS section — class + message per prior failure
    prior_section = ""
    prior_list = [p for p in (prior_failures or []) if p.exception is not None]
    if prior_list:
        lines = [
            f"Attempt {i + 1}: {type(p.exception).__name__}: {p.exception}"
            for i, p in enumerate(prior_list)
        ]
        prior_section = (
            "=== PRIOR FAILED ATTEMPTS — DO NOT REINTRODUCE THESE ERRORS ===\n"
            + "\n".join(lines)
            + "\n\n"
        )

    instruction = _FIX_INSTRUCTION_WITH_HISTORY if prior_list else _FIX_INSTRUCTION

    # Targeted corrective hint — matched against the exception message. Sits
    # immediately above the INSTRUCTION block so the LLM sees it last.
    hint_section = ""
    for predicate, hint_text in _TARGETED_HINTS:
        if predicate(exception_message):
            hint_section = f"=== HINT ===\n{hint_text}\n\n"
            break

    # Structure the feedback with clear section headers so the LLM can
    # parse each component unambiguously
    feedback = (
        f"{prior_section}"
        "=== ORIGINAL CODE ===\n"
        f"{original_code}\n"
        "\n"
        "=== ERROR ===\n"
        f"Exception: {exception_class}: {exception_message}\n"
        "\n"
        "=== TRACEBACK ===\n"
        f"{traceback_str}\n"
        "\n"
        f"{hint_section}"
        "=== INSTRUCTION ===\n"
        f"{instruction}"
    )

    logger.debug(
        "Formatted error feedback for %s (%d prior, %d chars)",
        exception_class, len(prior_list), len(feedback),
    )

    return feedback

