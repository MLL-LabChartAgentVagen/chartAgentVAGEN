"""
Pattern injection functions for FactTableSimulator.

Each pattern type modifies a subset of rows in the DataFrame to plant
a narrative-driven statistical anomaly that Phase 3 can detect and
use for QA generation.

Supported pattern types:
  - outlier_entity: Scale a filtered entity's metric values by z-score
  - trend_break: Shift metric values after a temporal breakpoint
  - ranking_reversal: Invert rank ordering between two metrics
  - dominance_shift: Swap top entity before/after temporal midpoint
  - convergence: Gradually reduce inter-entity gap over time
  - seasonal_anomaly: Add then invert seasonal pattern for target entity
"""

import numpy as np
import pandas as pd
from typing import Optional


PATTERN_TYPES = frozenset({
    "outlier_entity", "trend_break", "ranking_reversal",
    "dominance_shift", "convergence", "seasonal_anomaly",
})


def inject_pattern(
    df: pd.DataFrame,
    pattern_type: str,
    target: Optional[str],
    col: Optional[str],
    params: dict,
    temporal_col: Optional[str],
    root_entity_col: Optional[str],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Apply a pattern injection to the DataFrame (in-place when possible).

    Args:
        df: The DataFrame to modify.
        pattern_type: One of PATTERN_TYPES.
        target: Pandas query string to select affected rows (may be None).
        col: Target measure column (may be None for some patterns).
        params: Pattern-specific parameters.
        temporal_col: Name of the temporal column, if any.
        root_entity_col: Name of the root entity column (first dim group root).
        rng: NumPy random Generator.

    Returns:
        Modified DataFrame.
    """
    if pattern_type not in PATTERN_TYPES:
        raise ValueError(
            f"Unknown pattern type '{pattern_type}'. "
            f"Must be one of: {', '.join(sorted(PATTERN_TYPES))}"
        )
    handler = _PATTERN_HANDLERS[pattern_type]
    return handler(df, target, col, params, temporal_col, root_entity_col, rng)


def _evaluate_target(df: pd.DataFrame, target: str) -> pd.Series:
    """Evaluate target query and ensure it returns a boolean mask."""
    mask = df.eval(target)
    if not hasattr(mask, "dtype") or not pd.api.types.is_bool_dtype(mask):
        raise ValueError(f"Pattern target '{target}' must be a boolean query (e.g., \"col == 'value'\"), but returned {getattr(mask, 'dtype', type(mask))}.")
    return mask


# ---- Pattern handlers ----

def _inject_outlier_entity(
    df: pd.DataFrame,
    target: Optional[str],
    col: Optional[str],
    params: dict,
    temporal_col: Optional[str],
    root_entity_col: Optional[str],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Scale filtered entity's metric values to be z_score SDs above the mean.

    params: {"z_score": float}
    """
    if target is None or col is None:
        raise ValueError("outlier_entity requires both 'target' and 'col'")
    z_score = params.get("z_score", params.get("multiplier", 3.0))

    mask = _evaluate_target(df, target)
    if mask.sum() == 0:
        raise ValueError(f"outlier_entity filter '{target}' matched 0 rows")

    # Compute baseline statistics from NON-target rows so the z-score
    # is measured relative to the "normal" population, not inflated by
    # the boosted values themselves.
    non_target = df.loc[~mask, col]
    baseline_mean = non_target.mean()
    baseline_std = non_target.std()
    if baseline_std == 0 or np.isnan(baseline_std):
        return df

    # Set target rows to baseline_mean + z_score * baseline_std, with noise
    desired_mean = baseline_mean + z_score * baseline_std
    n_target = mask.sum()
    new_values = rng.normal(desired_mean, baseline_std * 0.15, n_target)
    df.loc[mask, col] = new_values

    return df


def _inject_trend_break(
    df: pd.DataFrame,
    target: Optional[str],
    col: Optional[str],
    params: dict,
    temporal_col: Optional[str],
    root_entity_col: Optional[str],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Apply a level shift to col values after a temporal breakpoint.

    params: {"break_point": str (date), "magnitude": float (fractional shift)}
    """
    if col is None:
        raise ValueError("trend_break requires 'col'")
    if temporal_col is None:
        raise ValueError("trend_break requires a temporal column in the data")

    if "break_point" not in params:
        raise ValueError("trend_break pattern requires 'break_point' (date string) in the 'params' dictionary")

    break_point = pd.to_datetime(params["break_point"])
    magnitude = params.get("magnitude", params.get("factor", 0.3))

    # Determine which rows are affected (optionally filtered by target)
    after_break = pd.to_datetime(df[temporal_col]) >= break_point
    if target is not None:
        entity_mask = _evaluate_target(df, target)
        mask = after_break & entity_mask
    else:
        mask = after_break

    if mask.sum() == 0:
        # If a target entity filter was specified but matched 0 rows,
        # that is a configuration error (spec §2.1: validates target non-empty).
        # If there is no entity filter, mask == after_break only — data may
        # simply all precede the break_point, which is a valid edge case.
        if target is not None:
            raise ValueError(
                f"trend_break: target filter '{target}' combined with "
                f"after_break condition (break_point={params['break_point']}) "
                f"matched 0 rows. Check that break_point falls within the "
                f"temporal range of rows matching the target query."
            )
        return df

    df.loc[mask, col] = df.loc[mask, col] * (1 + magnitude)
    return df


def _inject_ranking_reversal(
    df: pd.DataFrame,
    target: Optional[str],
    col: Optional[str],
    params: dict,
    temporal_col: Optional[str],
    root_entity_col: Optional[str],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Ensure the entity ranked highest on metric1 is ranked lowest on metric2
    (or vice versa), creating a ranking reversal.

    params: {"metrics": [metric1, metric2], "description": str}
    """
    metrics = params.get("metrics", [])
    if len(metrics) < 2:
        raise ValueError("ranking_reversal requires 'metrics' with ≥2 entries")
    if root_entity_col is None:
        raise ValueError("ranking_reversal requires a root entity column")

    m1, m2 = metrics[0], metrics[1]
    means = df.groupby(root_entity_col)[[m1, m2]].mean()

    # Find entity with highest m1
    top_m1_entity = means[m1].idxmax()
    # Find entity with lowest m2
    bottom_m2_entity = means[m2].idxmin()

    if top_m1_entity == bottom_m2_entity:
        # Already reversed — nothing to do
        return df

    # Boost m2 for top_m1_entity so it becomes the highest.
    # Cap boost_factor at 10× to prevent extreme value-domain inflation
    # that would corrupt other statistical properties (correlations, distributions).
    top_m1_mask = df[root_entity_col] == top_m1_entity
    current_max_m2 = means[m2].max()
    entity_mean_m2 = means.loc[top_m1_entity, m2]
    if entity_mean_m2 > 0:
        raw_factor = (current_max_m2 / entity_mean_m2) * 1.3
        boost_factor = min(raw_factor, 10.0)
    else:
        boost_factor = 2.0
    df.loc[top_m1_mask, m2] = df.loc[top_m1_mask, m2] * boost_factor

    return df


def _inject_dominance_shift(
    df: pd.DataFrame,
    target: Optional[str],
    col: Optional[str],
    params: dict,
    temporal_col: Optional[str],
    root_entity_col: Optional[str],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    The dominant entity (highest mean) on col switches at the temporal midpoint.

    params: {"magnitude": float (optional, default 0.5)}
    """
    if col is None or temporal_col is None or root_entity_col is None:
        raise ValueError("dominance_shift requires 'col', temporal, and entity columns")

    dates = pd.to_datetime(df[temporal_col])
    midpoint = dates.min() + (dates.max() - dates.min()) / 2

    means = df.groupby(root_entity_col)[col].mean()
    top_entity = means.idxmax()
    entities = means.index.tolist()
    # Pick second-highest entity
    runner_up = means.drop(top_entity).idxmax() if len(entities) > 1 else top_entity

    magnitude = params.get("magnitude", 0.5)

    # Before midpoint: suppress top entity, boost runner-up
    before = dates < midpoint
    top_before = (df[root_entity_col] == top_entity) & before
    runner_before = (df[root_entity_col] == runner_up) & before

    df.loc[top_before, col] = df.loc[top_before, col] * (1 - magnitude * 0.5)
    df.loc[runner_before, col] = df.loc[runner_before, col] * (1 + magnitude)

    return df


def _inject_convergence(
    df: pd.DataFrame,
    target: Optional[str],
    col: Optional[str],
    params: dict,
    temporal_col: Optional[str],
    root_entity_col: Optional[str],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Gradually reduce the gap between the top-2 entities' col values over time.

    params: {"convergence_rate": float (optional, default 0.8 = 80% convergence)}
    """
    if col is None or temporal_col is None or root_entity_col is None:
        raise ValueError("convergence requires 'col', temporal, and entity columns")

    dates = pd.to_datetime(df[temporal_col])
    date_min, date_max = dates.min(), dates.max()
    total_span = (date_max - date_min).total_seconds()
    if total_span == 0:
        return df

    means = df.groupby(root_entity_col)[col].mean()
    top_entity = means.idxmax()
    bottom_entity = means.idxmin()
    conv_rate = params.get("convergence_rate", 0.8)

    # For the bottom entity, gradually increase values toward the top
    bottom_mask = df[root_entity_col] == bottom_entity
    time_fraction = (dates[bottom_mask] - date_min).dt.total_seconds() / total_span
    boost = time_fraction * conv_rate * (means[top_entity] - means[bottom_entity])
    df.loc[bottom_mask, col] = df.loc[bottom_mask, col] + boost.values

    return df


def _inject_seasonal_anomaly(
    df: pd.DataFrame,
    target: Optional[str],
    col: Optional[str],
    params: dict,
    temporal_col: Optional[str],
    root_entity_col: Optional[str],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Add sinusoidal seasonality to col for all entities, then invert it
    for the target entity.

    params: {"amplitude": float (optional, fraction of mean, default 0.3),
             "period_days": int (optional, default 90)}
    """
    if col is None or temporal_col is None:
        raise ValueError("seasonal_anomaly requires 'col' and temporal column")

    dates = pd.to_datetime(df[temporal_col])
    amplitude = params.get("amplitude", 0.3) * df[col].mean()
    period_days = params.get("period_days", 90)
    day_offset = (dates - dates.min()).dt.total_seconds() / 86400.0

    # Add seasonal component to all rows
    seasonal = amplitude * np.sin(2 * np.pi * day_offset / period_days)
    df[col] = df[col] + seasonal

    # Invert for target entity
    if target is not None:
        target_mask = _evaluate_target(df, target)
        df.loc[target_mask, col] = df.loc[target_mask, col] - 2 * seasonal[target_mask]

    return df


_PATTERN_HANDLERS = {
    "outlier_entity": _inject_outlier_entity,
    "trend_break": _inject_trend_break,
    "ranking_reversal": _inject_ranking_reversal,
    "dominance_shift": _inject_dominance_shift,
    "convergence": _inject_convergence,
    "seasonal_anomaly": _inject_seasonal_anomaly,
}
