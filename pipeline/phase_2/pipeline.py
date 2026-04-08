"""
AGPDS Phase 2 top-level pipeline.

Connects Loop A (M3 ↔ M1) and Loop B (M5 → M2) into a unified
pipeline entry point.

Implements: §2.7, §2.9
"""
from __future__ import annotations

import copy
import logging
from typing import Any

import pandas as pd

from .exceptions import SkipResult
from .types import ParameterOverrides, ValidationReport

logger = logging.getLogger(__name__)


def run_phase2(
    scenario_context: dict[str, Any],
    max_loop_a_retries: int = 3,
    max_loop_b_retries: int = 2,
    auto_fix: dict[str, Any] | None = None,
    realism_config: dict[str, Any] | None = None,
    llm_client: "LLMClient | None" = None,
    api_key: str | None = None,
    model: str = "gemini-2.0-flash-lite",
    provider: str = "auto",
) -> tuple[pd.DataFrame, dict[str, Any], ValidationReport] | SkipResult:
    """Execute the full Phase 2 pipeline for one scenario.

    Pipeline:
      1. Loop A: LLM generates script → sandbox executes → produces DataFrame
      2. Loop B: Validator checks → auto-fix adjusts → re-generate

    Args:
        scenario_context: Context dict for the scenario.
        max_loop_a_retries: Max retries for Loop A (LLM script generation).
        max_loop_b_retries: Max retries for Loop B (validation auto-fix).
        auto_fix: Optional strategy map for Loop B auto-fix dispatch.
        realism_config: Optional realism config applied post-validation.
        llm_client: Pre-built LLMClient instance. If provided, api_key/model/
            provider are ignored.
        api_key: API key for LLM provider. Used only when llm_client is None.
        model: LLM model name (default: "gemini-2.0-flash-lite").
        provider: LLM provider ("auto", "openai", "gemini", "gemini-native",
            "azure", "custom"). Default "auto" detects from model name.

    Returns:
        Tuple of (DataFrame, metadata, ValidationReport) on success,
        or SkipResult if all retries are exhausted.
    """
    # ===== LLM Client Setup =====
    from .orchestration.llm_client import LLMClient as _LLMClient
    if llm_client is None:
        if api_key is None:
            raise ValueError(
                "Either llm_client or api_key must be provided to run_phase2()."
            )
        llm_client = _LLMClient(api_key=api_key, model=model, provider=provider)

    # ===== Loop A: LLM Orchestration =====
    loop_a_result = _run_loop_a(scenario_context, max_loop_a_retries, llm_client)
    if isinstance(loop_a_result, SkipResult):
        return loop_a_result

    df, metadata, raw_declarations = loop_a_result

    # ===== Loop B: Validation + Auto-fix =====
    return _run_loop_b(
        df,
        metadata,
        raw_declarations,
        max_retries=max_loop_b_retries,
        auto_fix=auto_fix,
        realism_config=realism_config,
    )


def _run_loop_a(
    scenario_context: dict[str, Any],
    max_retries: int,
    llm_client: Any,
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]] | SkipResult:
    """Execute Loop A: LLM → sandbox → basic validation.

    Delegates to orchestration.retry_loop.orchestrate().

    Args:
        scenario_context: Context dict.
        max_retries: Maximum retry count.
        llm_client: Configured LLMClient for code generation.

    Returns:
        Tuple of (DataFrame, metadata, raw_declarations) or SkipResult.

    .. note::
        raw_declarations now carries live simulator registries (columns,
        groups, group_dependencies, measure_dag, target_rows, patterns,
        seed) captured via _TrackingSimulator in the sandbox. Falls back
        to metadata when the simulator instance is not available.
    """
    from .orchestration.retry_loop import orchestrate

    result = orchestrate(scenario_context, llm_client=llm_client, max_retries=max_retries)
    if isinstance(result, SkipResult):
        return result

    return result


def _apply_pattern_overrides(
    patterns: list[dict[str, Any]],
    overrides: ParameterOverrides | None,
) -> list[dict[str, Any]]:
    """Merge pattern overrides into pattern specs for run_pipeline.

    The amplify_magnitude auto-fix strategy stores amplified z_score /
    magnitude in overrides["patterns"][idx]["params"]. run_pipeline reads
    pattern params from the pattern spec list directly, so this helper
    bridges the gap by deep-copying the patterns and merging overrides.

    Args:
        patterns: Original pattern spec list.
        overrides: Current ParameterOverrides dict (may be None or empty).

    Returns:
        New pattern list with overrides merged (or original if no overrides).
    """
    if not overrides or "patterns" not in overrides:
        return patterns

    pat_overrides = overrides["patterns"]
    if not pat_overrides:
        return patterns

    merged = copy.deepcopy(patterns)
    for idx, patch in pat_overrides.items():
        if isinstance(idx, int) and 0 <= idx < len(merged):
            if "params" in patch:
                merged[idx].setdefault("params", {}).update(patch["params"])
    return merged


def _run_loop_b(
    df: pd.DataFrame,
    metadata: dict[str, Any],
    raw_declarations: dict[str, Any],
    max_retries: int,
    auto_fix: dict[str, Any] | None = None,
    realism_config: dict[str, Any] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any], ValidationReport] | SkipResult:
    """Execute Loop B: validation → auto-fix → re-generate.

    Delegates to generate_with_validation() from validation/autofix.py,
    which handles the full retry loop with strategy-based auto-fix
    accumulation and validation-before-realism ordering.

    Args:
        df: Generated DataFrame (from Loop A, used as initial result).
        metadata: Schema metadata dict.
        raw_declarations: Raw declaration registries for re-generation.
            Required keys: columns, groups, group_dependencies, measure_dag,
            target_rows, patterns, seed.
        max_retries: Maximum auto-fix retry count.
        auto_fix: Optional strategy map (check name globs → callables).
        realism_config: Optional realism config applied post-validation.

    Returns:
        Tuple of (DataFrame, metadata, ValidationReport) or SkipResult
        if generation produces no output.
    """
    from .engine.generator import run_pipeline
    from .validation.autofix import generate_with_validation

    columns = raw_declarations["columns"]
    groups = raw_declarations["groups"]
    group_deps = raw_declarations["group_dependencies"]
    measure_dag = raw_declarations["measure_dag"]
    target_rows = raw_declarations["target_rows"]
    patterns = raw_declarations.get("patterns", [])
    base_seed = raw_declarations.get("seed", 42)
    orthogonal_pairs = raw_declarations.get("orthogonal_pairs", [])

    def build_fn(
        seed: int, overrides: ParameterOverrides | None,
    ) -> tuple[pd.DataFrame, dict[str, Any]]:
        effective_patterns = _apply_pattern_overrides(patterns, overrides)
        return run_pipeline(
            columns=columns,
            groups=groups,
            group_dependencies=group_deps,
            measure_dag=measure_dag,
            target_rows=target_rows,
            seed=seed,
            patterns=effective_patterns,
            realism_config=None,  # validation-before-realism ordering
            overrides=overrides,
            orthogonal_pairs=orthogonal_pairs,
        )

    result_df, result_meta, report = generate_with_validation(
        build_fn=build_fn,
        meta=metadata,
        patterns=metadata.get("patterns", []),
        base_seed=base_seed,
        max_attempts=max_retries + 1,
        auto_fix=auto_fix,
        realism_config=realism_config,
    )

    if result_df is None:
        return SkipResult(
            scenario_id=metadata.get("scenario_id", "unknown"),
            error_log=["Loop B produced no DataFrame after all attempts."],
        )

    logger.debug(
        "Loop B complete: passed=%s, failures=%d.",
        report.all_passed, len(report.failures),
    )

    return result_df, result_meta, report
