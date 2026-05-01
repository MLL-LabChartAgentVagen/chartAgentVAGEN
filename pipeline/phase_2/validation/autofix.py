"""
Auto-fix strategy dispatch and Loop B orchestrator.

Strategies produce parameter override entries (not declaration mutations).
generate_with_validation() runs the retry loop with validation-before-realism
ordering.

Implements: §2.9 auto-fix (Loop B), P0-3
"""
from __future__ import annotations

import fnmatch
import logging
from typing import Any, Callable, Optional

import numpy as np
import pandas as pd

from ..types import Check, ParameterOverrides, ValidationReport

logger = logging.getLogger(__name__)


# =====================================================================
# Strategy Matching
# =====================================================================

def match_strategy(
    check_name: str,
    auto_fix: dict[str, Any],
) -> Optional[Callable[[Check, ParameterOverrides], ParameterOverrides]]:
    """Glob-based matcher: find the first auto_fix key that matches check name.

    [Subtask 9.1.1]

    Args:
        check_name: The Check.name string.
        auto_fix: Dict mapping glob patterns to strategy callables.

    Returns:
        The matched strategy callable, or None.
    """
    for glob_pattern, strategy_fn in auto_fix.items():
        if fnmatch.fnmatch(check_name, glob_pattern):
            return strategy_fn
    return None


# =====================================================================
# Helper: extract column name from check name
# =====================================================================

def _extract_col_from_check_name(check_name: str) -> str:
    """Extract column name from a check name by stripping the first prefix.

    Examples:
        "ks_revenue"          -> "revenue"
        "outlier_wait_minutes" -> "wait_minutes"
        "marginal_weights_severity" -> "weights_severity"

    Args:
        check_name: Check name with prefix_column format.

    Returns:
        Column name portion after the first underscore.
    """
    if "_" in check_name:
        return check_name.split("_", 1)[1]
    return check_name


# =====================================================================
# Strategy: widen_variance (P0-3)
# =====================================================================

def widen_variance(
    check: Check,
    overrides: ParameterOverrides,
    factor: float = 1.2,
    columns: dict[str, dict[str, Any]] | None = None,
) -> ParameterOverrides:
    """Widen sigma/scale by a multiplicative factor in overrides.

    [P0-3]

    Extracts column name from check.name, then accumulates a
    multiplicative factor for sigma in overrides["measures"][col].
    The factor compounds across retries (1.2 -> 1.44 -> 1.728).

    Called as strategy(check, overrides) when factor uses the default,
    or via functools.partial for custom factors.

    Mixture opt-out (IS-1): when ``columns`` is provided and the resolved
    column has family == "mixture", returns overrides unchanged. Mixtures
    have no single sigma to widen — per-component widening is out of scope
    for v1. Wire via:

        from functools import partial
        auto_fix = {"ks_*": partial(widen_variance, columns=meta["columns"]), ...}

    Args:
        check: The failing Check object.
        overrides: Current overrides dict (mutated and returned).
        factor: Multiplicative factor for sigma/scale.
        columns: Optional column registry; enables the mixture opt-out check.

    Returns:
        Updated overrides dict.
    """
    col_name = _extract_col_from_check_name(check.name)

    if columns is not None:
        family = columns.get(col_name, {}).get("family")
        if family == "mixture":
            logger.debug(
                "widen_variance: skip mixture column '%s' "
                "(no single sigma to widen).",
                col_name,
            )
            return overrides

    measures = overrides.setdefault("measures", {})
    col_ov = measures.setdefault(col_name, {})

    # Accumulate multiplicative factor
    current = col_ov.get("sigma", 1.0)
    col_ov["sigma"] = current * factor

    logger.debug(
        "widen_variance: check='%s', col='%s', sigma factor: %.4f -> %.4f.",
        check.name, col_name, current, col_ov["sigma"],
    )
    return overrides


# =====================================================================
# Strategy: amplify_magnitude (P0-3)
# =====================================================================

def amplify_magnitude(
    check: Check,
    overrides: ParameterOverrides,
    patterns: list[dict[str, Any]] | None = None,
    factor: float = 1.3,
) -> ParameterOverrides:
    """Amplify pattern z_score/magnitude by a multiplicative factor.

    [P0-3]

    Extracts column name from check.name, finds the matching pattern
    by col, and stores amplified params in overrides["patterns"][idx].

    Must be bound with patterns via functools.partial before use in
    auto_fix dict, or called with patterns=None to store by column name.

    Args:
        check: The failing Check object.
        overrides: Current overrides dict (mutated and returned).
        patterns: Pattern spec list (needed to find matching index).
        factor: Multiplicative factor for z_score/magnitude.

    Returns:
        Updated overrides dict.
    """
    col_name = _extract_col_from_check_name(check.name)
    pat_overrides = overrides.setdefault("patterns", {})

    if patterns is not None:
        for idx, p in enumerate(patterns):
            if p.get("col") == col_name:
                pat_ov = pat_overrides.setdefault(idx, {})
                pat_params = pat_ov.setdefault("params", dict(p.get("params", {})))

                if "z_score" in pat_params:
                    old = pat_params["z_score"]
                    pat_params["z_score"] = old * factor
                    logger.debug(
                        "amplify_magnitude: check='%s', pattern[%d].z_score: "
                        "%.4f -> %.4f.",
                        check.name, idx, old, pat_params["z_score"],
                    )
                elif "magnitude" in pat_params:
                    old = pat_params["magnitude"]
                    pat_params["magnitude"] = old * factor
                    logger.debug(
                        "amplify_magnitude: check='%s', pattern[%d].magnitude: "
                        "%.4f -> %.4f.",
                        check.name, idx, old, pat_params["magnitude"],
                    )
                break

    return overrides


# =====================================================================
# Strategy: reshuffle_pair (P0-3)
# =====================================================================

def reshuffle_pair(
    check: Check,
    overrides: ParameterOverrides,
) -> ParameterOverrides:
    """Mark a column for reshuffling to destroy spurious correlation.

    [P0-3]

    Extracts column name from check.name and adds it to the
    overrides["reshuffle"] list. The engine applies permutation
    after measure generation.

    Args:
        check: The failing Check object.
        overrides: Current overrides dict (mutated and returned).

    Returns:
        Updated overrides dict.
    """
    col_name = _extract_col_from_check_name(check.name)
    reshuffle_list = overrides.setdefault("reshuffle", [])

    if col_name not in reshuffle_list:
        reshuffle_list.append(col_name)

    logger.debug(
        "reshuffle_pair: check='%s', added '%s' to reshuffle list.",
        check.name, col_name,
    )
    return overrides


# =====================================================================
# Loop B Orchestrator: generate_with_validation (P0-3)
# =====================================================================

def generate_with_validation(
    build_fn: Callable[[int, ParameterOverrides | None], tuple[pd.DataFrame, dict]],
    meta: dict[str, Any],
    patterns: list[dict[str, Any]],
    base_seed: int = 42,
    max_attempts: int = 3,
    auto_fix: dict[str, Any] | None = None,
    realism_config: dict[str, Any] | None = None,
) -> tuple[pd.DataFrame, dict, ValidationReport]:
    """Run generation with validation-retry loop (Loop B).

    [P0-3, P2-2, P2-3]

    Algorithm:
      1. Start with empty overrides
      2. For each attempt (up to max_attempts):
         a. seed = base_seed + attempt
         b. Call build_fn(seed, overrides) -> (df, meta)
            build_fn MUST call run_pipeline with realism_config=None
         c. Validate df against meta using SchemaAwareValidator
         d. If all checks pass: break
         e. For each failure: match strategy and accumulate overrides
      3. Apply realism post-validation (if configured)
      4. Return (df, meta, report)

    Args:
        build_fn: Callable(seed, overrides) -> (DataFrame, metadata).
            Must invoke run_pipeline with realism_config=None.
        meta: Initial schema metadata (overwritten by build_fn on each attempt).
        patterns: Pattern specs for L3 validation checks.
        base_seed: Base random seed (incremented per attempt).
        max_attempts: Maximum retry attempts.
        auto_fix: Optional dict mapping check name globs to strategy callables.
            Each strategy has signature (Check, ParameterOverrides) -> ParameterOverrides.
        realism_config: Optional realism config applied post-validation.

    Returns:
        Tuple of (DataFrame, metadata, ValidationReport).
    """
    from .validator import SchemaAwareValidator

    overrides: ParameterOverrides = {}
    df: pd.DataFrame | None = None
    report = ValidationReport()

    for attempt in range(max_attempts):
        seed = base_seed + attempt
        df, meta = build_fn(seed, overrides if overrides else None)

        report = SchemaAwareValidator(meta).validate(df, patterns)

        logger.debug(
            "generate_with_validation: attempt %d/%d, seed=%d, "
            "passed=%s, failures=%d.",
            attempt + 1, max_attempts, seed,
            report.all_passed, len(report.failures),
        )

        if report.all_passed:
            break

        # Accumulate overrides from failing checks
        if auto_fix:
            for check in report.failures:
                strategy = match_strategy(check.name, auto_fix)
                if strategy is not None:
                    overrides = strategy(check, overrides)

    # Apply realism post-validation (P0-3, P2-2, P2-3)
    if realism_config is not None and df is not None:
        from ..engine.realism import inject_realism
        realism_rng = np.random.default_rng(base_seed + max_attempts)
        columns_meta = meta.get("columns", {})
        df = inject_realism(df, realism_config, columns_meta, realism_rng)

    return df, meta, report
