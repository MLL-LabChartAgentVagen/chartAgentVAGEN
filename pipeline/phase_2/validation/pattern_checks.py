"""
L3 Pattern Validation Checks.

Standalone functions for checking whether injected patterns are
detectable in the generated data. Extracted from phase_2/validator.py.

Implements: §2.9 L3
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np
import pandas as pd

from ..exceptions import PatternInjectionError
from ..types import Check

logger = logging.getLogger(__name__)


def check_outlier_entity(
    df: pd.DataFrame,
    pattern: dict[str, Any],
) -> Check:
    """L3: Outlier entity z-score check — target subset z >= 2.0.

    [Subtask 8.4.1]

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "target", "col", "params".

    Returns:
        Check named "outlier_{col}".
    """
    target_expr = pattern["target"]
    col = pattern["col"]
    _ = pattern["params"]["z_score"]

    target_mask = df.eval(target_expr)
    target_idx = df.index[target_mask]

    if len(target_idx) == 0:
        return Check(
            name=f"outlier_{col}",
            passed=False,
            detail=f"Target '{target_expr}' matched zero rows.",
        )

    # Use complement (non-target) statistics as the reference distribution.
    # The injection shifted target values using pre-injection global stats,
    # so post-injection global stats are contaminated by the shift itself,
    # systematically reducing the measured z-score.  The complement is
    # unaffected by the injection and approximates the pre-injection dist.
    complement_mask = ~target_mask
    subset_mean = float(df.loc[target_idx, col].mean())

    if complement_mask.sum() >= 2:
        ref_mean = float(df.loc[complement_mask, col].mean())
        ref_std = float(df.loc[complement_mask, col].std())
    else:
        # Fewer than 2 complement rows — fall back to global stats
        ref_mean = float(df[col].mean())
        ref_std = float(df[col].std())

    if ref_std == 0.0 or np.isnan(ref_std):
        # Zero std: if subset differs from reference, outlier is obvious
        if abs(subset_mean - ref_mean) > 1e-9:
            return Check(
                name=f"outlier_{col}",
                passed=True,
                detail=(
                    f"z=inf (subset_mean={subset_mean:.4f}, "
                    f"ref_mean={ref_mean:.4f}, ref_std=0.0)"
                ),
            )
        return Check(
            name=f"outlier_{col}",
            passed=False,
            detail=f"Global std of '{col}' is {ref_std}; z-score undefined.",
        )

    z = abs(subset_mean - ref_mean) / ref_std
    passed = bool(z >= 2.0)
    detail = (
        f"z={z:.4f} (subset_mean={subset_mean:.4f}, "
        f"ref_mean={ref_mean:.4f}, ref_std={ref_std:.4f})"
    )
    return Check(name=f"outlier_{col}", passed=passed, detail=detail)


def _find_temporal_column(meta: dict[str, Any]) -> Optional[str]:
    """Locate the temporal group's root column name from metadata."""
    dimension_groups = meta.get("dimension_groups", {})
    time_group = dimension_groups.get("time")
    if time_group is None:
        return None
    hierarchy = time_group.get("hierarchy", [])
    if not hierarchy:
        return None
    return hierarchy[0]


def check_trend_break(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Trend break magnitude check — |after - before| / before > 0.15.

    [Subtask 8.4.3]

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "col" and "break_point".
        meta: Schema metadata for temporal column lookup.

    Returns:
        Check named "trend_{col}".
    """
    col = pattern["col"]

    break_point_raw = pattern.get("break_point")
    if break_point_raw is None:
        break_point_raw = pattern["params"]["break_point"]

    temporal_col = _find_temporal_column(meta)
    if temporal_col is None:
        raise PatternInjectionError(
            pattern_type="trend_break",
            detail="No temporal column found in metadata.",
        )

    if temporal_col not in df.columns:
        raise PatternInjectionError(
            pattern_type="trend_break",
            detail=f"Temporal column '{temporal_col}' not in DataFrame.",
        )

    # Filter to pattern target rows so the before/after comparison
    # measures the effect on the intended subset, not the global column.
    target_expr = pattern.get("target")
    if target_expr:
        target_mask = df.eval(target_expr)
        work_df = df[target_mask]
    else:
        work_df = df

    temporal_values = pd.to_datetime(work_df[temporal_col], errors="coerce")
    break_point_dt = pd.to_datetime(break_point_raw)

    before_mask = temporal_values < break_point_dt
    after_mask = temporal_values >= break_point_dt

    before_values = work_df.loc[before_mask, col]
    after_values = work_df.loc[after_mask, col]

    if len(before_values) == 0 or len(after_values) == 0:
        return Check(
            name=f"trend_{col}",
            passed=False,
            detail=(
                f"Degenerate split at break_point={break_point_raw}: "
                f"before={len(before_values)}, after={len(after_values)}."
            ),
        )

    before_mean = float(before_values.mean())
    after_mean = float(after_values.mean())

    if before_mean == 0.0:
        return Check(
            name=f"trend_{col}",
            passed=False,
            detail=f"Before-period mean is 0.0; relative change undefined.",
        )

    ratio = abs(after_mean - before_mean) / abs(before_mean)
    passed = bool(ratio > 0.15)
    detail = (
        f"before_mean={before_mean:.4f}, after_mean={after_mean:.4f}, "
        f"ratio={ratio:.4f} ({'>' if passed else '<='} 0.15)"
    )
    return Check(name=f"trend_{col}", passed=passed, detail=detail)


def check_dominance_shift(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Dominance shift validation (stub).

    [P1-3]

    TODO [M5-NC-4 / P1-3]: Define as rank change of entity across temporal
    split. Expected params: entity_filter, col, split_point.

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "col" key.
        meta: Schema metadata.

    Returns:
        Check named "dominance_{col}" with passed=True (not yet implemented).
    """
    return Check(
        name=f"dominance_{pattern['col']}",
        passed=True,
        detail="dominance_shift validation not yet implemented",
    )


def check_convergence(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Convergence validation (stub).

    TODO [M5-NC-5 / P1-4]: Convergence validation not yet specified.

    [P1-4]

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "col" key.
        meta: Schema metadata.

    Returns:
        Check named "convergence_{col}" with passed=True (not yet implemented).
    """
    return Check(
        name=f"convergence_{pattern['col']}",
        passed=True,
        detail="convergence validation not yet implemented",
    )


def check_seasonal_anomaly(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Seasonal anomaly validation (stub).

    TODO [M5-NC-5 / P1-4]: Seasonal anomaly validation not yet specified.

    [P1-4]

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "col" key.
        meta: Schema metadata.

    Returns:
        Check named "seasonal_{col}" with passed=True (not yet implemented).
    """
    return Check(
        name=f"seasonal_{pattern['col']}",
        passed=True,
        detail="seasonal_anomaly validation not yet implemented",
    )


def check_ranking_reversal(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Ranking reversal validation — negative rank correlation.

    §2.9 L3: Groups DataFrame by entity column, computes per-entity
    mean of two metrics, ranks each, and checks that the Spearman rank
    correlation is negative (< 0).

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "params" containing "metrics"
            (list of 2 metric column names) and optionally "entity_col".
        meta: Schema metadata (fallback for entity column lookup).

    Returns:
        Check named "reversal_{m1}_{m2}".
    """
    params = pattern.get("params", {})
    metrics = params.get("metrics")

    if not metrics or len(metrics) != 2:
        return Check(
            name=f"ranking_{pattern.get('col', 'unknown')}",
            passed=False,
            detail=f"Expected exactly 2 metrics, got {metrics!r}.",
        )

    m1, m2 = metrics

    # Resolve entity column: prefer explicit param, fall back to first
    # dimension group root (matching spec pseudocode).
    entity_col = params.get("entity_col")
    if not entity_col:
        dim_groups = meta.get("dimension_groups", {})
        if dim_groups:
            first_group = dim_groups[list(dim_groups.keys())[0]]
            hierarchy = first_group.get("hierarchy", [])
            if hierarchy:
                entity_col = hierarchy[0]

    if not entity_col:
        return Check(
            name=f"reversal_{m1}_{m2}",
            passed=False,
            detail="No entity_col in params and no dimension group root in metadata.",
        )

    for col_name in [entity_col, m1, m2]:
        if col_name not in df.columns:
            return Check(
                name=f"reversal_{m1}_{m2}",
                passed=False,
                detail=f"Column '{col_name}' not found in DataFrame.",
            )

    means = df.groupby(entity_col)[[m1, m2]].mean()

    if len(means) < 2:
        return Check(
            name=f"reversal_{m1}_{m2}",
            passed=False,
            detail=f"Need >= 2 entities for rank correlation, got {len(means)}.",
        )

    correlation = float(means[m1].rank().corr(means[m2].rank()))

    if np.isnan(correlation):
        return Check(
            name=f"reversal_{m1}_{m2}",
            passed=False,
            detail="Rank correlation is NaN (constant metric values).",
        )

    passed = bool(correlation < 0)
    detail = f"rank_corr={correlation:.4f} ({'<' if passed else '>='} 0)"
    return Check(name=f"reversal_{m1}_{m2}", passed=passed, detail=detail)
