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

from agpds.exceptions import (
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

        elif pattern_type in (
            "ranking_reversal",
            "dominance_shift",
            "convergence",
            "seasonal_anomaly",
        ):
            raise NotImplementedError(
                f"BLOCKED: [A8/B6] Pattern type '{pattern_type}' "
                f"injection algorithm is unspecified. Awaiting Blocker 4 "
                f"resolution."
            )

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
