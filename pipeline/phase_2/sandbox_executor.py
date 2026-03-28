"""
Sandbox Executor + Error Feedback Loop for AGPDS Phase 2.

Executes LLM-generated FactTableSimulator scripts in a restricted
namespace, captures exceptions as structured feedback, and orchestrates
retry loops for LLM self-correction.

Reference: phase_2.md §2.4
"""

import signal
import traceback
import textwrap
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

import numpy as np
import pandas as pd

from .fact_table_simulator import FactTableSimulator
from .schema_metadata import SchemaMetadata

if TYPE_CHECKING:
    from ..core.llm_client import LLMClient


# =========================================================================
# Result Container
# =========================================================================

@dataclass
class ExecutionResult:
    """Result of executing a FactTableSimulator script in the sandbox.

    On success: success=True, df and schema_metadata populated.
    On failure: success=False, error fields populated for LLM feedback.
    """
    success: bool
    df: Optional[pd.DataFrame] = None
    schema_metadata: Optional[dict] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    traceback_str: Optional[str] = None
    script: Optional[str] = None


# =========================================================================
# Timeout Helper
# =========================================================================

class _ExecutionTimeout(Exception):
    """Raised when script execution exceeds the time limit."""
    pass


def _timeout_handler(signum, frame):
    raise _ExecutionTimeout("Script execution timed out")


# =========================================================================
# Safe Import Whitelist (F-004)
# =========================================================================

_ALLOWED_MODULES = frozenset({
    "math", "datetime", "decimal", "fractions", "statistics", "random",
})


def _safe_import(name, *args, **kwargs):
    """Restricted import that only allows whitelisted modules."""
    if name not in _ALLOWED_MODULES:
        raise ImportError(
            f"Import of '{name}' is not allowed in the sandbox. "
            f"Permitted modules: {sorted(_ALLOWED_MODULES)}"
        )
    return __import__(name, *args, **kwargs)


# =========================================================================
# Sandbox Executor
# =========================================================================

# Builtins whitelisted for LLM-generated scripts.
_SAFE_BUILTINS = {
    "__import__": _safe_import,
    "__build_class__": __build_class__,
    # Types & constructors
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
    "bytes": bytes,
    "bytearray": bytearray,
    "complex": complex,
    "type": type,
    "object": object,
    # Numeric / math
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "divmod": divmod,
    # Iterators / sequences
    "range": range,
    "len": len,
    "sorted": sorted,
    "reversed": reversed,
    "enumerate": enumerate,
    "zip": zip,
    "map": map,
    "filter": filter,
    "all": all,
    "any": any,
    "next": next,
    "iter": iter,
    "slice": slice,
    # String / repr
    "repr": repr,
    "format": format,
    "chr": chr,
    "ord": ord,
    "isinstance": isinstance,
    "issubclass": issubclass,
    "hasattr": hasattr,
    "getattr": getattr,
    "setattr": setattr,
    # Print (useful for debugging scripts)
    "print": print,
    # Exceptions (so isinstance checks work in LLM code)
    "Exception": Exception,
    "ValueError": ValueError,
    "TypeError": TypeError,
    "KeyError": KeyError,
    "IndexError": IndexError,
    "RuntimeError": RuntimeError,
    "AttributeError": AttributeError,
    "StopIteration": StopIteration,
    "ZeroDivisionError": ZeroDivisionError,
}


class SandboxExecutor:
    """Execute LLM-generated FactTableSimulator scripts in a restricted
    namespace.

    The sandbox provides:
      - FactTableSimulator SDK
      - numpy, pandas, math, datetime (whitelisted)
      - Restricted __builtins__ (no os, sys, subprocess, open, etc.)
      - Signal-based timeout

    Usage::

        executor = SandboxExecutor(timeout_seconds=30)
        result = executor.execute(script_string, seed=42)
        if result.success:
            df, meta = result.df, result.schema_metadata
        else:
            feedback = format_error_feedback(result)
    """

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    def _build_namespace(self, seed: int = 42) -> dict:
        """Build a restricted execution namespace.

        Only safe libraries and the FactTableSimulator SDK are accessible.
        """
        import math
        import datetime

        namespace = {
            "__builtins__": _SAFE_BUILTINS,
            # SDK
            "FactTableSimulator": FactTableSimulator,
            # Whitelisted libraries
            "np": np,
            "numpy": np,
            "pd": pd,
            "pandas": pd,
            "math": math,
            "datetime": datetime,
            # Convenience: pre-set seed for scripts that use it
            "_default_seed": seed,
            "__name__": "__sandbox__",
        }
        return namespace

    def execute(self, script: str, seed: int = 42) -> ExecutionResult:
        """Execute a Python script string in the sandboxed namespace.

        The script MUST define a ``build_fact_table(seed=...)`` function
        that calls ``FactTableSimulator`` and returns ``sim.generate()``.

        Args:
            script: Python source code string.
            seed: Default seed to pass to ``build_fact_table()``.

        Returns:
            ExecutionResult: success with (df, meta) or failure with error
            details.
        """
        namespace = self._build_namespace(seed)

        # ---- Step 1: Compile (catches SyntaxError early) ----
        try:
            compiled = compile(script, "<llm_script>", "exec")
        except SyntaxError as e:
            return ExecutionResult(
                success=False,
                error_type="SyntaxError",
                error_message=str(e),
                traceback_str=traceback.format_exc(),
                script=script,
            )

        # ---- Step 2: Execute with timeout ----
        old_handler = None
        try:
            # Set timeout via SIGALRM (Unix only)
            old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(self.timeout_seconds)

            exec(compiled, namespace)

            # Reset alarm after successful exec
            signal.alarm(0)

        except _ExecutionTimeout:
            return ExecutionResult(
                success=False,
                error_type="TimeoutError",
                error_message=(
                    f"Script execution exceeded {self.timeout_seconds}s limit. "
                    "Simplify the data generation or reduce target_rows."
                ),
                traceback_str="",
                script=script,
            )
        except Exception as e:
            signal.alarm(0)
            return ExecutionResult(
                success=False,
                error_type=type(e).__name__,
                error_message=str(e),
                traceback_str=traceback.format_exc(),
                script=script,
            )
        finally:
            # Always restore original handler
            if old_handler is not None:
                signal.signal(signal.SIGALRM, old_handler)
                signal.alarm(0)

        # ---- Step 3: Call build_fact_table() ----
        build_fn = namespace.get("build_fact_table")
        if build_fn is None:
            return ExecutionResult(
                success=False,
                error_type="NameError",
                error_message=(
                    "Script must define a function `build_fact_table(seed=42)` "
                    "that returns sim.generate()."
                ),
                traceback_str="",
                script=script,
            )

        try:
            old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(self.timeout_seconds)

            result = build_fn(seed=seed)

            signal.alarm(0)

        except _ExecutionTimeout:
            return ExecutionResult(
                success=False,
                error_type="TimeoutError",
                error_message=(
                    f"build_fact_table() exceeded {self.timeout_seconds}s. "
                    "Reduce target_rows or simplify the schema."
                ),
                traceback_str="",
                script=script,
            )
        except Exception as e:
            signal.alarm(0)
            return ExecutionResult(
                success=False,
                error_type=type(e).__name__,
                error_message=str(e),
                traceback_str=traceback.format_exc(),
                script=script,
            )
        finally:
            if old_handler is not None:
                signal.signal(signal.SIGALRM, old_handler)
                signal.alarm(0)

        # ---- Step 4: Validate return type ----
        if not isinstance(result, tuple) or len(result) != 2:
            return ExecutionResult(
                success=False,
                error_type="TypeError",
                error_message=(
                    "build_fact_table() must return a tuple (DataFrame, dict) "
                    f"from sim.generate(). Got: {type(result).__name__}"
                ),
                traceback_str="",
                script=script,
            )

        df, meta = result
        if not isinstance(df, pd.DataFrame):
            return ExecutionResult(
                success=False,
                error_type="TypeError",
                error_message=(
                    f"First element must be pd.DataFrame, got {type(df).__name__}"
                ),
                traceback_str="",
                script=script,
            )

        return ExecutionResult(
            success=True,
            df=df,
            schema_metadata=meta,
            script=script,
        )


# =========================================================================
# Error Feedback Formatter
# =========================================================================

def format_error_feedback(result: ExecutionResult) -> str:
    """Format a failed ExecutionResult into structured feedback for the LLM.

    The output is designed to be appended to the LLM conversation so the
    model can self-correct its script.

    Args:
        result: A failed ExecutionResult (success=False).

    Returns:
        Human-readable error feedback string.
    """
    if result.success:
        return ""

    lines = [
        "=== EXECUTION ERROR ===",
        f"Error Type: {result.error_type}",
        f"Message: {result.error_message}",
    ]

    if result.traceback_str and result.traceback_str.strip():
        lines.append("")
        lines.append("Full Traceback:")
        lines.append(result.traceback_str.strip())

    lines.append("")
    lines.append(
        "Please fix your script to resolve this error. "
        "Make sure build_fact_table(seed) is defined and returns sim.generate()."
    )

    return "\n".join(lines)


# =========================================================================
# Orchestrator: LLM Code Gen → Sandbox → Error Feedback → Retry
# =========================================================================

# Default system prompt for Phase 2 code generation (from phase_2.md §2.2)
PHASE2_SYSTEM_PROMPT = textwrap.dedent("""\
    You are an expert Data Scientist Agent. Build an Atomic-Grain Fact Table
    using the `FactTableSimulator` Python SDK.

    INPUT:
    1. Scenario Context: real-world setting with entities, metrics, and temporal grain.
    2. SDK Reference: you may ONLY use the methods listed below.

    AVAILABLE SDK METHODS (declare columns FIRST, then relationships):
      sim = FactTableSimulator(target_rows=1000, seed=42)

      # --- Step 1: Column declarations ---
      sim.add_category(name, values, weights, group, parent=None)
      sim.add_temporal(name, start, end, freq)
      sim.add_measure(name, dist, params, scale=None)

      # --- Step 2: Relationships & patterns ---
      sim.add_conditional(measure, on, mapping)               # P(measure | category)
      sim.add_dependency(target, formula, noise_sigma)        # target: measure name string
      sim.add_correlation(col_a, col_b, target_r)
      sim.declare_orthogonal(group_a, group_b, rationale)
      sim.inject_pattern(pattern_type, target, col, params)   # pattern_type: string from PATTERN_TYPES. target: optional boolean query string. col: measure name.
      sim.set_realism(missing_rate, dirty_rate, censoring=None)

    SUPPORTED DISTRIBUTIONS AND PARAMS (must use exact keys):
       "gaussian": {"mu": mean, "sigma": std}
       "lognormal": {"mu": mean, "sigma": std}
       "gamma": {"shape": k, "scale": theta}
       "beta": {"alpha": a, "beta": b}
       "uniform": {"low": min, "high": max}
       "poisson": {"lam": lambda_val}
       "exponential": {"scale": beta_val}
       "mixture": {"components": [{"weight": w, "dist": name, "params": {}}, ...]}

    PATTERN_TYPES: "outlier_entity", "trend_break", "ranking_reversal",
                   "dominance_shift", "convergence", "seasonal_anomaly"
                   (DO NOT use "break_point" or "break-point" - use exactly "trend_break")

    HARD CONSTRAINTS — the script MUST satisfy ALL:
    1. ATOMIC_GRAIN: each row = one indivisible event.
    2. At least 2 dimension groups, each with ≥1 categorical column, plus ≥2 measures.
    3. All column declarations (Step 1) BEFORE any relationship declarations (Step 2).
    4. At least 1 declare_orthogonal() between genuinely independent groups.
    5. At least 1 add_correlation() and 2 inject_pattern() calls.
    6. Output must be pure, valid Python with NO class definitions. You MUST define exactly this function:
       def build_fact_table(seed=42):
           sim = FactTableSimulator(...)
           ...
           return sim.generate()
    7. DO NOT use any `import` statements. The modules `np`, `pd`, `math`, `datetime`, and the class `FactTableSimulator` are already pre-loaded in your execution environment. Do not try to import them.
    8. For add_conditional(..., mapping=...), each mapping value MUST be a flat params dict
       (e.g., {"mu": 4.5, "sigma": 0.4}). Do NOT use nested forms like
       {"dist": "...", "params": {...}}.
    9. Pattern parameter keys MUST use canonical names:
       - outlier_entity: params={"z_score": float}
       - trend_break: params={"break_point": "YYYY-MM-DD", "magnitude": float}
    10. Do NOT call add_correlation() on any dependency target column declared
        via add_dependency(); dependency target relationships are formula-derived.

    SOFT GUIDELINES — include when naturally fitting the domain:
    - Temporal dimension (if data has a time component).
    - Within-group hierarchy via parent (e.g., region → city → district).
    - 3+ measures (enables richer chart coverage).
    - Conditional distributions via add_conditional() when measures logically
      vary by category.
    - Numerical correlation pairs (at least 1 positive or negative).
""")


def run_with_retries(
    llm_client: "LLMClient",
    scenario_context: str,
    system_prompt: str = PHASE2_SYSTEM_PROMPT,
    max_retries: int = 3,
    seed: int = 42,
    timeout_seconds: int = 30,
) -> ExecutionResult:
    """Full Phase 2 agentic loop: LLM code gen → sandbox exec → error feedback.

    Flow:
      1. LLM generates a Python script via ``generate_code()``.
      2. ``SandboxExecutor.execute()`` runs the script.
      3. SUCCESS → return result immediately.
      4. FAILURE → format error feedback, append to conversation, retry.
      5. After ``max_retries`` failures → return last error result.

    Args:
        llm_client: Configured LLMClient instance with ``generate_code()``.
        scenario_context: The scenario description from Phase 1.
        system_prompt: System prompt for SDK code generation.
        max_retries: Maximum number of LLM retry attempts (default 3).
        seed: Base seed for FactTableSimulator.
        timeout_seconds: Per-execution time limit.

    Returns:
        ExecutionResult with success or final failure.
    """
    executor = SandboxExecutor(timeout_seconds=timeout_seconds)

    # Build initial user prompt
    user_prompt = f"[SCENARIO]\n{scenario_context}\n[AGENT CODE]"

    # Track conversation history for error feedback
    messages_history: list[dict] = []
    feedback_text: str = ""

    for attempt in range(max_retries):
        # ---- Generate code ----
        if attempt == 0:
            script = llm_client.generate_code(
                system=system_prompt,
                user=user_prompt,
            )
        else:
            # Append error feedback and request correction
            correction_prompt = (
                f"{feedback_text}\n\n"
                "Please output the COMPLETE corrected script. "
                "Remember: define build_fact_table(seed=42) returning sim.generate()."
            )
            script = llm_client.generate_code(
                system=system_prompt,
                user=correction_prompt,
            )

        # ---- Execute in sandbox ----
        result = executor.execute(script, seed=seed)

        if result.success:
            return result

        # ---- Format feedback for next attempt ----
        feedback_text = format_error_feedback(result)

        # Log the attempt
        print(
            f"  ⚠ Sandbox attempt {attempt + 1}/{max_retries} failed: "
            f"{result.error_type}: {result.error_message}"
        )

    # All retries exhausted
    return result
