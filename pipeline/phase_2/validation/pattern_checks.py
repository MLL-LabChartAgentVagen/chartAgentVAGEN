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


def _resolve_first_dim_root(meta: dict[str, Any]) -> Optional[str]:
    """Return the hierarchy root of the first dimension group in meta.

    Shared entity-col fallback for IS-2/IS-3/IS-4 and check_ranking_reversal.
    Iteration uses dict insertion order — metadata/builder.py inserts groups
    in declaration order, so the first group is whichever the LLM declared
    first.
    """
    dim_groups = meta.get("dimension_groups", {})
    if not dim_groups:
        return None
    first_group = dim_groups[next(iter(dim_groups))]
    hierarchy = first_group.get("hierarchy", [])
    return hierarchy[0] if hierarchy else None


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
    """L3: Dominance shift — target entity's rank changes across split.

    [IS-2: pairs with inject_dominance_shift in engine/patterns.py]

    Algorithm (rank-change interpretation, locked in
    docs/artifacts/phase_2_spec_decisions.md §IS-2):
      1. Resolve entity_col (params["entity_col"] > first dim-group root
         via _resolve_first_dim_root).
      2. Resolve temporal_col via _find_temporal_column.
      3. Split at params["split_point"]; group each side by entity_col
         and compute mean of pattern["col"].
      4. Rank entities descending by mean (largest mean = rank 1) on
         each side.
      5. Pass if |rank_after - rank_before| of params["entity_filter"]
         >= params.get("rank_change", 1).

    Failure modes return passed=False with a descriptive detail rather
    than raising — the L3 dispatcher in validator.py wraps raises into
    failed checks anyway, but graceful returns are easier to interpret
    in ValidationReport.

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "col" and "params" keys.
            params requires "entity_filter" and "split_point";
            "entity_col" and "rank_change" optional.
        meta: Schema metadata for entity_col / temporal_col lookup.

    Returns:
        Check named "dominance_{col}".
    """
    col = pattern["col"]
    params = pattern.get("params", {})
    target_entity = params.get("entity_filter")
    split_point = params.get("split_point")
    rank_threshold = params.get("rank_change", 1)
    name = f"dominance_{col}"

    if not target_entity or not split_point:
        return Check(
            name=name, passed=False,
            detail=(
                f"Missing entity_filter={target_entity!r} or "
                f"split_point={split_point!r} in params."
            ),
        )

    entity_col = params.get("entity_col") or _resolve_first_dim_root(meta)
    temporal_col = _find_temporal_column(meta)
    if entity_col is None or temporal_col is None:
        return Check(
            name=name, passed=False,
            detail=(
                f"Cannot resolve entity_col={entity_col!r} or "
                f"temporal_col={temporal_col!r} from metadata."
            ),
        )

    if entity_col not in df.columns or col not in df.columns:
        return Check(
            name=name, passed=False,
            detail=(
                f"Required column missing in DataFrame "
                f"(entity_col={entity_col!r}, col={col!r})."
            ),
        )

    if temporal_col not in df.columns:
        return Check(
            name=name, passed=False,
            detail=f"Temporal column {temporal_col!r} not in DataFrame.",
        )

    sp = pd.to_datetime(split_point)
    tval = pd.to_datetime(df[temporal_col], errors="coerce")
    before_means = df[tval < sp].groupby(entity_col)[col].mean()
    after_means = df[tval >= sp].groupby(entity_col)[col].mean()

    if (
        target_entity not in before_means.index
        or target_entity not in after_means.index
    ):
        return Check(
            name=name, passed=False,
            detail=(
                f"Target entity {target_entity!r} missing on one side "
                f"of split_point={split_point}."
            ),
        )

    # Descending rank: largest mean = rank 1 (matches spec_decisions
    # §IS-2 "rank direction" decision and check_ranking_reversal).
    rank_before = float(before_means.rank(ascending=False)[target_entity])
    rank_after = float(after_means.rank(ascending=False)[target_entity])
    delta = abs(rank_after - rank_before)
    passed = bool(delta >= rank_threshold)
    return Check(
        name=name, passed=passed,
        detail=(
            f"rank_before={rank_before:.0f}, rank_after={rank_after:.0f}, "
            f"delta={delta:.0f} (threshold={rank_threshold})"
        ),
    )


def check_convergence(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Convergence — variance of per-entity means decreases over time.

    [IS-3: pairs with inject_convergence in engine/patterns.py]

    Algorithm (locked in docs/stub_analysis/stub_blocker_decisions.md §IS-3):
      1. Resolve entity_col (params["entity_col"] > _resolve_first_dim_root).
      2. Resolve temporal_col via _find_temporal_column.
      3. Split at params["split_point"] or tval.quantile(0.5).
      4. Per side, compute per-entity mean of pattern["col"].
      5. Compare variance-of-means: reduction = (early_var - late_var)/early_var.
      6. Pass if reduction >= params.get("reduction", 0.3).
    """
    col = pattern["col"]
    params = pattern.get("params", {})
    threshold = params.get("reduction", 0.3)
    name = f"convergence_{col}"

    entity_col = params.get("entity_col") or _resolve_first_dim_root(meta)
    temporal_col = _find_temporal_column(meta)
    if entity_col is None or temporal_col is None:
        return Check(
            name=name, passed=False,
            detail=(
                f"Cannot resolve entity_col={entity_col!r} or "
                f"temporal_col={temporal_col!r} from metadata."
            ),
        )

    if (
        entity_col not in df.columns
        or col not in df.columns
        or temporal_col not in df.columns
    ):
        return Check(
            name=name, passed=False,
            detail=(
                f"Required column missing in DataFrame "
                f"(entity_col={entity_col!r}, col={col!r}, "
                f"temporal_col={temporal_col!r})."
            ),
        )

    tval = pd.to_datetime(df[temporal_col], errors="coerce")
    sp = (
        pd.to_datetime(params["split_point"])
        if params.get("split_point")
        else tval.quantile(0.5)
    )

    early_means = df[tval < sp].groupby(entity_col)[col].mean()
    late_means = df[tval >= sp].groupby(entity_col)[col].mean()

    if len(early_means) < 2 or len(late_means) < 2:
        return Check(
            name=name, passed=False,
            detail=(
                f"Need >=2 entities per side, got "
                f"early={len(early_means)}, late={len(late_means)}."
            ),
        )

    early_var = float(early_means.var())
    late_var = float(late_means.var())

    if early_var == 0.0 or not np.isfinite(early_var):
        return Check(
            name=name, passed=False,
            detail=(
                f"Early-period inter-group variance is {early_var}; "
                f"reduction undefined."
            ),
        )

    reduction = (early_var - late_var) / early_var
    passed = bool(reduction >= threshold)
    return Check(
        name=name, passed=passed,
        detail=(
            f"early_var={early_var:.4f}, late_var={late_var:.4f}, "
            f"reduction={reduction:.3f} (threshold={threshold})"
        ),
    )


def check_seasonal_anomaly(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Seasonal anomaly — window-vs-baseline z-score.

    [IS-4: pairs with inject_seasonal_anomaly in engine/patterns.py]

    Algorithm (locked in docs/stub_analysis/stub_blocker_decisions.md §IS-4,
    interpretation (a)):
      1. Resolve temporal_col via _find_temporal_column.
      2. Determine [win_start, win_end] from params["anomaly_window"];
         fall back to last 10% of temporal range. The fallback is
         defensive — under normal flow the SDK gate
         (PATTERN_REQUIRED_PARAMS) guarantees anomaly_window is present.
      3. Compute window mean and out-of-window baseline mean+std on
         pattern["col"].
      4. z = |window_mean - baseline_mean| / baseline_std.
      5. Pass if z >= params.get("z_threshold", 1.5).

    Failure modes return passed=False with a descriptive detail rather
    than raising.
    """
    col = pattern["col"]
    params = pattern.get("params", {})
    z_threshold = params.get("z_threshold", 1.5)
    name = f"seasonal_{col}"

    temporal_col = _find_temporal_column(meta)
    if temporal_col is None:
        return Check(
            name=name, passed=False,
            detail="Cannot resolve temporal_col from metadata.",
        )

    if temporal_col not in df.columns or col not in df.columns:
        return Check(
            name=name, passed=False,
            detail=(
                f"Required column missing in DataFrame "
                f"(temporal_col={temporal_col!r}, col={col!r})."
            ),
        )

    tval = pd.to_datetime(df[temporal_col], errors="coerce")
    window = params.get("anomaly_window")
    if window is not None and len(window) == 2:
        win_start = pd.to_datetime(window[0])
        win_end = pd.to_datetime(window[1])
    else:
        # Defensive fallback — last 10% of temporal range.
        tmin, tmax = tval.min(), tval.max()
        if pd.isna(tmin) or pd.isna(tmax):
            return Check(
                name=name, passed=False,
                detail=(
                    f"Temporal column {temporal_col!r} has no parseable "
                    f"values; cannot derive default anomaly_window."
                ),
            )
        span = tmax - tmin
        win_start = tmin + span * 0.9
        win_end = tmax

    in_win = (tval >= win_start) & (tval <= win_end)
    window_vals = df.loc[in_win, col].dropna()
    baseline_vals = df.loc[~in_win, col].dropna()

    if len(window_vals) == 0:
        return Check(
            name=name, passed=False,
            detail=(
                f"Anomaly window [{win_start}..{win_end}] matches no rows."
            ),
        )
    if len(baseline_vals) < 2:
        return Check(
            name=name, passed=False,
            detail=(
                f"Need >=2 baseline rows outside window, got "
                f"{len(baseline_vals)}."
            ),
        )

    baseline_std = float(baseline_vals.std())
    if baseline_std == 0.0 or not np.isfinite(baseline_std):
        return Check(
            name=name, passed=False,
            detail=(
                f"Baseline std of {col!r} is {baseline_std}; "
                f"z-score undefined."
            ),
        )

    window_mean = float(window_vals.mean())
    baseline_mean = float(baseline_vals.mean())
    z = abs(window_mean - baseline_mean) / baseline_std
    passed = bool(z >= z_threshold)
    return Check(
        name=name, passed=passed,
        detail=(
            f"z={z:.3f} (window_mean={window_mean:.4f}, "
            f"baseline_mean={baseline_mean:.4f}, "
            f"baseline_std={baseline_std:.4f}, "
            f"threshold={z_threshold})"
        ),
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
    entity_col = params.get("entity_col") or _resolve_first_dim_root(meta)

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
