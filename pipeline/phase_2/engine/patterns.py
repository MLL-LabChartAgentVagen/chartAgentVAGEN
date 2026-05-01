"""
Phase γ — Pattern injection extracted from FactTableSimulator.

This module applies declared patterns (outlier_entity, trend_break) to a
post-measure DataFrame.  Each injection function receives explicit parameters
rather than reading FactTableSimulator instance state.

Extracted during the Sprint 6 post-completion refactoring.
Original locations: FactTableSimulator._inject_patterns,
    FactTableSimulator._inject_outlier_entity,
    FactTableSimulator._inject_trend_break.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from ..exceptions import (
    DegenerateDistributionError,
    PatternInjectionError,
)

logger = logging.getLogger(__name__)


def inject_patterns(
    df: pd.DataFrame,
    patterns: list[dict[str, Any]],
    columns: dict[str, dict[str, Any]],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Phase γ: Apply all declared patterns to the post-measure DataFrame.

    [Subtask 4.3.1, 4.3.2]

    Pattern composition: patterns are applied in declaration order.
    Overlapping targets compose by sequential mutation — later patterns
    overwrite earlier ones on the same cells.

    Args:
        df: DataFrame with all columns populated.
        patterns: List of pattern spec dicts from FactTableSimulator._patterns.
        columns: Column registry for temporal column lookup.
        rng: Seeded NumPy random generator.

    Returns:
        DataFrame with patterns injected (modified in-place and returned).
    """
    for pattern in patterns:
        pattern_type = pattern["type"]

        if pattern_type == "outlier_entity":
            df = inject_outlier_entity(df, pattern)

        elif pattern_type == "trend_break":
            df = inject_trend_break(df, pattern, columns)

        elif pattern_type == "ranking_reversal":
            df = inject_ranking_reversal(df, pattern, columns)

        elif pattern_type == "dominance_shift":
            df = inject_dominance_shift(df, pattern, columns)

        elif pattern_type == "convergence":
            df = inject_convergence(df, pattern, columns)

        elif pattern_type == "seasonal_anomaly":
            df = inject_seasonal_anomaly(df, pattern, columns)

        else:
            raise ValueError(
                f"Unknown pattern type '{pattern_type}' encountered "
                f"during injection. This should have been rejected at "
                f"declaration time."
            )

        logger.debug(
            "inject_patterns: applied '%s' on col='%s'.",
            pattern_type,
            pattern.get("col"),
        )

    return df


def inject_outlier_entity(
    df: pd.DataFrame,
    pattern: dict[str, Any],
) -> pd.DataFrame:
    """Inject outlier_entity pattern: shift target subset mean.

    [Subtask 4.3.1]

    Algorithm:
      1. Evaluate pattern["target"] via df.eval() to get target mask.
      2. Compute global_mean and global_std of pattern["col"].
      3. Desired target mean = global_mean + z_score × global_std.
      4. Shift the target subset by (desired_mean − current_subset_mean).

    Args:
        df: Full DataFrame.
        pattern: Pattern spec dict with "target", "col", "params" keys.

    Returns:
        DataFrame with outlier values injected.
    """
    target_expr = pattern["target"]
    col = pattern["col"]
    z_score = pattern["params"]["z_score"]

    target_mask = df.eval(target_expr)
    target_idx = df.index[target_mask]

    if len(target_idx) == 0:
        raise PatternInjectionError(
            pattern_type="outlier_entity",
            detail=(
                f"Target '{target_expr}' matched zero rows. "
                f"Cannot inject outlier pattern on an empty subset."
            ),
        )

    if col not in df.columns:
        logger.warning(
            "inject_outlier_entity: column '%s' not in DataFrame "
            "(measures may not be generated yet). Skipping injection.",
            col,
        )
        return df

    global_mean = df[col].mean()
    global_std = df[col].std()

    if global_std == 0.0 or np.isnan(global_std):
        raise DegenerateDistributionError(
            column_name=col,
            detail=(
                "zero standard deviation — cannot compute outlier shift "
                "(z_score × 0 = 0 for any z_score)"
            ),
        )

    desired_mean = global_mean + z_score * global_std
    current_subset_mean = df.loc[target_idx, col].mean()
    shift = desired_mean - current_subset_mean

    df.loc[target_idx, col] = df.loc[target_idx, col] + shift

    logger.debug(
        "inject_outlier_entity: col='%s', z_score=%.2f, "
        "shift=%.4f, n_target=%d.",
        col, z_score, shift, len(target_idx),
    )
    return df


def inject_trend_break(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    columns: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    """Inject trend_break pattern: scale values after break_point.

    [Subtask 4.3.2]

    Algorithm:
      1. Evaluate pattern["target"] via df.eval() to get target mask.
      2. Parse break_point as a date.
      3. Find the temporal column from *columns*.
      4. Within target rows, select those where temporal_col >= break_point.
      5. Multiply their pattern["col"] values by (1 + magnitude).

    Args:
        df: Full DataFrame.
        pattern: Pattern spec dict.
        columns: Column registry for temporal column lookup.

    Returns:
        DataFrame with trend break injected.
    """
    target_expr = pattern["target"]
    col = pattern["col"]
    break_point_str = pattern["params"]["break_point"]
    magnitude = pattern["params"]["magnitude"]

    temporal_col: str | None = None
    for col_name, col_meta in columns.items():
        if col_meta.get("type") == "temporal":
            temporal_col = col_name
            break

    if temporal_col is None:
        raise PatternInjectionError(
            pattern_type="trend_break",
            detail=(
                "No temporal column declared. trend_break requires a "
                "temporal column for the before/after break_point split."
            ),
        )

    break_point = pd.to_datetime(break_point_str)

    target_mask = df.eval(target_expr)
    target_idx = df.index[target_mask]

    if len(target_idx) == 0:
        raise PatternInjectionError(
            pattern_type="trend_break",
            detail=(
                f"Target '{target_expr}' matched zero rows. "
                f"Cannot inject trend break on an empty subset."
            ),
        )

    if col not in df.columns:
        logger.warning(
            "inject_trend_break: column '%s' not in DataFrame "
            "(measures may not be generated yet). Skipping injection.",
            col,
        )
        return df

    temporal_values = pd.to_datetime(df[temporal_col])
    post_break_mask = target_mask & (temporal_values >= break_point)
    post_break_idx = df.index[post_break_mask]

    if len(post_break_idx) > 0:
        df.loc[post_break_idx, col] = (
            df.loc[post_break_idx, col] * (1.0 + magnitude)
        )

    logger.debug(
        "inject_trend_break: col='%s', break_point='%s', "
        "magnitude=%.2f, n_target=%d, n_post_break=%d.",
        col, break_point_str, magnitude,
        len(target_idx), len(post_break_idx),
    )
    return df


def inject_dominance_shift(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    columns: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    """Inject dominance_shift pattern: target entity's mean dominates
    peers post-split_point.

    [DS-2: pairs with check_dominance_shift in validation/pattern_checks.py]

    Algorithm (locked in docs/artifacts/phase_2_spec_decisions.md §DS-2):
      1. Resolve temporal_col from *columns* (mirror inject_trend_break).
      2. Evaluate pattern["target"] mask — these are the target entity's
         rows. params["entity_filter"] holds the entity *name* for the
         validator's groupby lookup; pattern["target"] is the row mask
         the engine uses to identify which rows to shift.
      3. Compute peer rows = (NOT target) AND (temporal >= split_point);
         derive peer_max and peer_std on pattern["col"].
      4. Compute desired post-split target mean = peer_max + magnitude *
         peer_std (with a positive-floor fallback when peer_std is 0/NaN).
      5. Additive shift target rows where temporal >= split_point.

    Pre-split target rows are NOT mutated, so per-side group means
    diverge across the split → check_dominance_shift sees a rank change.

    Args:
        df: Full DataFrame.
        pattern: Pattern spec dict with "target", "col", "params".
            params requires "split_point"; "magnitude" optional (default 1.0).
        columns: Column registry for temporal column lookup.

    Returns:
        DataFrame with the dominance shift applied (mutated in place).

    Raises:
        PatternInjectionError: empty target subset, no temporal column,
            empty peer set post-split, or empty post-split target subset.
    """
    target_expr = pattern["target"]
    col = pattern["col"]
    params = pattern["params"]
    split_point_str = params["split_point"]
    magnitude = params.get("magnitude", 1.0)

    temporal_col: str | None = None
    for col_name, col_meta in columns.items():
        if col_meta.get("type") == "temporal":
            temporal_col = col_name
            break

    if temporal_col is None:
        raise PatternInjectionError(
            pattern_type="dominance_shift",
            detail=(
                "No temporal column declared. dominance_shift requires a "
                "temporal column for the before/after split."
            ),
        )

    target_mask = df.eval(target_expr)
    if target_mask.sum() == 0:
        raise PatternInjectionError(
            pattern_type="dominance_shift",
            detail=(
                f"Target '{target_expr}' matched zero rows. "
                f"Cannot inject dominance shift on an empty subset."
            ),
        )

    if col not in df.columns:
        logger.warning(
            "inject_dominance_shift: column '%s' not in DataFrame "
            "(measures may not be generated yet). Skipping injection.",
            col,
        )
        return df

    sp = pd.to_datetime(split_point_str)
    temporal_values = pd.to_datetime(df[temporal_col])

    post_split_mask = temporal_values >= sp
    post_split_target_idx = df.index[target_mask & post_split_mask]
    peer_idx = df.index[(~target_mask) & post_split_mask]

    if len(post_split_target_idx) == 0:
        raise PatternInjectionError(
            pattern_type="dominance_shift",
            detail=(
                f"No target rows on or after split_point={split_point_str}. "
                f"Cannot apply dominance shift."
            ),
        )

    if len(peer_idx) == 0:
        raise PatternInjectionError(
            pattern_type="dominance_shift",
            detail=(
                f"No peer (non-target) rows on or after "
                f"split_point={split_point_str}. Cannot compute peer_max."
            ),
        )

    peer_values = df.loc[peer_idx, col]
    peer_max = float(peer_values.max())
    peer_std = float(peer_values.std()) if len(peer_values) >= 2 else 0.0

    # Floor the gap so target dominance is guaranteed even when peers
    # have zero variance or magnitude=0 was passed.
    if not np.isfinite(peer_std) or peer_std <= 0.0:
        gap = max(abs(peer_max) * 0.1, 1.0)
    else:
        gap = max(magnitude * peer_std, 1e-9)

    desired_mean = peer_max + gap
    current_mean = float(df.loc[post_split_target_idx, col].mean())
    shift = desired_mean - current_mean
    df.loc[post_split_target_idx, col] = (
        df.loc[post_split_target_idx, col] + shift
    )

    logger.debug(
        "inject_dominance_shift: col='%s', split_point='%s', "
        "magnitude=%.2f, n_target_post=%d, n_peer=%d, shift=%.4f.",
        col, split_point_str, magnitude,
        len(post_split_target_idx), len(peer_idx), shift,
    )
    return df


def inject_ranking_reversal(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    columns: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    """Inject ranking_reversal pattern: reverse rank order of two metrics.

    [DS-2: pairs with check_ranking_reversal in validation/pattern_checks.py]

    Algorithm — operates at the entity-mean level so it reliably triggers
    the validator (Spearman rank correlation < 0 over per-entity means):

      1. Resolve metrics m1, m2 from pattern["params"]["metrics"].
      2. Resolve entity_col: prefer pattern["params"]["entity_col"]; else
         fall back to first categorical column with no parent in
         *columns* (mirrors check_ranking_reversal's "first dim group
         root" fallback).
      3. Evaluate target mask via df.eval(pattern["target"]).
      4. Within target rows: rank entities ascending by mean(m1); assign
         each entity a desired m2 mean by reversing that rank order
         against the existing m2-mean distribution.
      5. Apply additive per-entity shift on m2 so each entity's mean
         lands at its desired position. Within-entity m2 variance is
         preserved (only the mean moves).

    Args:
        df: Full DataFrame.
        pattern: Pattern spec dict with "target", "params" keys.
            params must contain "metrics" (length-2 list of measure
            column names) and may contain "entity_col".
        columns: Column registry (used for entity_col fallback).

    Returns:
        DataFrame with ranking reversal injected.
    """
    target_expr = pattern["target"]
    params = pattern.get("params", {})
    metrics = params.get("metrics")

    if not isinstance(metrics, (list, tuple)) or len(metrics) != 2:
        raise PatternInjectionError(
            pattern_type="ranking_reversal",
            detail=(
                f"params['metrics'] must be a length-2 list of measure "
                f"column names, got {metrics!r}."
            ),
        )
    m1, m2 = metrics

    entity_col = params.get("entity_col")
    if not entity_col:
        for col_name, col_meta in columns.items():
            if (
                col_meta.get("type") == "categorical"
                and col_meta.get("parent") is None
            ):
                entity_col = col_name
                break

    if not entity_col:
        raise PatternInjectionError(
            pattern_type="ranking_reversal",
            detail=(
                "No entity_col in params and no categorical root column "
                "found in registry to use as fallback."
            ),
        )

    target_mask = df.eval(target_expr)
    target_idx = df.index[target_mask]

    if len(target_idx) == 0:
        raise PatternInjectionError(
            pattern_type="ranking_reversal",
            detail=(
                f"Target '{target_expr}' matched zero rows. "
                f"Cannot inject ranking reversal on an empty subset."
            ),
        )

    for needed_col in (entity_col, m1, m2):
        if needed_col not in df.columns:
            logger.warning(
                "inject_ranking_reversal: column '%s' not in DataFrame "
                "(measures may not be generated yet). Skipping injection.",
                needed_col,
            )
            return df

    target_df = df.loc[target_idx]
    entity_means_m1 = target_df.groupby(entity_col)[m1].mean()
    entity_means_m2 = target_df.groupby(entity_col)[m2].mean()

    if len(entity_means_m1) < 2:
        raise PatternInjectionError(
            pattern_type="ranking_reversal",
            detail=(
                f"Need >= 2 distinct entities in target subset to reverse "
                f"rankings, got {len(entity_means_m1)} "
                f"(entity_col='{entity_col}')."
            ),
        )

    # Entity with smallest m1 mean (rank 1) should receive the largest
    # m2 mean. Sort entities by m1 rank, then pair against m2 means
    # sorted descending.
    rank_m1 = entity_means_m1.rank(ascending=True, method="first")
    entities_low_to_high_m1 = rank_m1.sort_values().index
    sorted_m2_desc = sorted(entity_means_m2.values, reverse=True)
    desired_m2 = pd.Series(sorted_m2_desc, index=entities_low_to_high_m1)

    for entity, desired in desired_m2.items():
        rows_e = target_mask & (df[entity_col] == entity)
        rows_e_idx = df.index[rows_e]
        if len(rows_e_idx) == 0:
            continue
        current = df.loc[rows_e_idx, m2].mean()
        df.loc[rows_e_idx, m2] = df.loc[rows_e_idx, m2] + (desired - current)

    logger.debug(
        "inject_ranking_reversal: m1='%s', m2='%s', entity_col='%s', "
        "n_target=%d, n_entities=%d.",
        m1, m2, entity_col, len(target_idx), len(entity_means_m1),
    )
    return df


def inject_convergence(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    columns: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    """Inject convergence: pull target rows toward global_mean over time.

    [DS-2: pairs with check_convergence in validation/pattern_checks.py]

    Algorithm (locked in docs/stub_analysis/stub_blocker_decisions.md §DS-2):
      1. Resolve temporal_col from *columns* (mirror inject_trend_break).
      2. Compute global_mean of pattern["col"] over the full DataFrame
         (pre-injection, so the pull anchor is the unmutated mean).
      3. Normalize temporal_col to [0, 1] across the full DataFrame range.
      4. For each target row:
            factor = clip(norm_t * pull_strength, 0, 1)
            df[col] = df[col] * (1 - factor) + global_mean * factor
      5. pull_strength defaults to 1.0 (full convergence at t=tmax).

    For the matching validator (check_convergence) to pass, `target` should
    span multiple entities — typically a temporal-only or severity-style
    filter. A single-entity target has no inter-group variance to collapse.

    Args:
        df: Full DataFrame.
        pattern: Pattern spec dict with "target", "col", "params".
            params["pull_strength"] optional (default 1.0); must be > 0.
        columns: Column registry for temporal column lookup.

    Returns:
        DataFrame with convergence injected (mutated in place).

    Raises:
        PatternInjectionError: empty target subset, no temporal column,
            zero or non-finite temporal span, non-positive pull_strength,
            or all target rows have unparseable temporal values.
    """
    target_expr = pattern["target"]
    col = pattern["col"]
    params = pattern.get("params", {})
    pull_strength = float(params.get("pull_strength", 1.0))

    if pull_strength <= 0.0 or not np.isfinite(pull_strength):
        raise PatternInjectionError(
            pattern_type="convergence",
            detail=f"pull_strength must be > 0, got {pull_strength!r}.",
        )

    temporal_col: str | None = None
    for col_name, col_meta in columns.items():
        if col_meta.get("type") == "temporal":
            temporal_col = col_name
            break

    if temporal_col is None:
        raise PatternInjectionError(
            pattern_type="convergence",
            detail=(
                "No temporal column declared. convergence requires a "
                "temporal column to apply time-graded blending."
            ),
        )

    target_mask = df.eval(target_expr)
    target_idx = df.index[target_mask]
    if len(target_idx) == 0:
        raise PatternInjectionError(
            pattern_type="convergence",
            detail=(
                f"Target '{target_expr}' matched zero rows. "
                f"Cannot inject convergence on an empty subset."
            ),
        )

    if col not in df.columns:
        logger.warning(
            "inject_convergence: column '%s' not in DataFrame "
            "(measures may not be generated yet). Skipping injection.",
            col,
        )
        return df

    tval = pd.to_datetime(df[temporal_col], errors="coerce")
    valid_mask = tval.notna()
    valid_target_idx = df.index[target_mask & valid_mask]
    if len(valid_target_idx) == 0:
        raise PatternInjectionError(
            pattern_type="convergence",
            detail=(
                f"All target rows have unparseable temporal values "
                f"in column '{temporal_col}'."
            ),
        )

    tmin = tval.min()
    tmax = tval.max()
    if pd.isna(tmin) or pd.isna(tmax):
        raise PatternInjectionError(
            pattern_type="convergence",
            detail=(
                f"Temporal column '{temporal_col}' has no parseable values."
            ),
        )
    span = tmax - tmin
    if span.total_seconds() == 0:
        raise PatternInjectionError(
            pattern_type="convergence",
            detail=(
                f"Temporal column '{temporal_col}' has zero span; "
                f"cannot normalize to [0, 1]."
            ),
        )

    global_mean = float(df[col].mean())
    norm_t = ((tval - tmin) / span).astype(float)
    factor = (
        norm_t.loc[valid_target_idx] * pull_strength
    ).clip(lower=0.0, upper=1.0)
    df.loc[valid_target_idx, col] = (
        df.loc[valid_target_idx, col] * (1.0 - factor)
        + global_mean * factor
    )

    logger.debug(
        "inject_convergence: col='%s', pull_strength=%.2f, "
        "global_mean=%.4f, n_target=%d, n_target_valid=%d.",
        col, pull_strength, global_mean,
        len(target_idx), len(valid_target_idx),
    )
    return df


def inject_seasonal_anomaly(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    columns: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    """Inject seasonal_anomaly: scale values inside anomaly_window.

    [IS-4 / DS-2: pairs with check_seasonal_anomaly in validation/
    pattern_checks.py]

    Algorithm (locked in docs/stub_analysis/stub_blocker_decisions.md §DS-2,
    mirrors inject_trend_break with a finite [start, end] window):
      1. Resolve temporal_col from *columns*.
      2. Evaluate pattern["target"] mask.
      3. Multiply target rows whose temporal_col falls inside
         params["anomaly_window"] = [start, end] by (1 + magnitude).

    Args:
        df: Full DataFrame.
        pattern: Pattern spec dict with "target", "col", "params".
            params requires "anomaly_window" ([start, end] dates) and
            "magnitude" (per the SDK gate).
        columns: Column registry for temporal column lookup.

    Returns:
        DataFrame with seasonal anomaly injected (mutated in place).

    Raises:
        PatternInjectionError: empty target subset, no temporal column,
            or anomaly_window matching no target rows.
    """
    target_expr = pattern["target"]
    col = pattern["col"]
    params = pattern["params"]
    window = params["anomaly_window"]
    magnitude = params["magnitude"]

    temporal_col: str | None = None
    for col_name, col_meta in columns.items():
        if col_meta.get("type") == "temporal":
            temporal_col = col_name
            break

    if temporal_col is None:
        raise PatternInjectionError(
            pattern_type="seasonal_anomaly",
            detail=(
                "No temporal column declared. seasonal_anomaly requires a "
                "temporal column to apply the anomaly_window mask."
            ),
        )

    target_mask = df.eval(target_expr)
    target_idx = df.index[target_mask]

    if len(target_idx) == 0:
        raise PatternInjectionError(
            pattern_type="seasonal_anomaly",
            detail=(
                f"Target '{target_expr}' matched zero rows. "
                f"Cannot inject seasonal anomaly on an empty subset."
            ),
        )

    if col not in df.columns:
        logger.warning(
            "inject_seasonal_anomaly: column '%s' not in DataFrame "
            "(measures may not be generated yet). Skipping injection.",
            col,
        )
        return df

    win_start = pd.to_datetime(window[0])
    win_end = pd.to_datetime(window[1])
    temporal_values = pd.to_datetime(df[temporal_col])
    in_win = (
        target_mask
        & (temporal_values >= win_start)
        & (temporal_values <= win_end)
    )
    in_win_idx = df.index[in_win]

    if len(in_win_idx) == 0:
        raise PatternInjectionError(
            pattern_type="seasonal_anomaly",
            detail=(
                f"anomaly_window [{window[0]}..{window[1]}] matches no "
                f"target rows. Cannot apply seasonal anomaly."
            ),
        )

    df.loc[in_win_idx, col] = df.loc[in_win_idx, col] * (1.0 + magnitude)

    logger.debug(
        "inject_seasonal_anomaly: col='%s', window=[%s..%s], "
        "magnitude=%.2f, n_target=%d, n_in_window=%d.",
        col, window[0], window[1], magnitude,
        len(target_idx), len(in_win_idx),
    )
    return df
