"""
Engine Phase α — Skeleton builder extracted from FactTableSimulator.

This module generates all non-measure columns (categorical roots, dependent
roots, child categories, temporal roots, derived temporal columns) in
topological order.  Functions accept explicit parameters instead of reading
FactTableSimulator instance state.

Extracted during the Sprint 6 post-completion refactoring.
Original locations: FactTableSimulator._build_skeleton and its sub-methods.

Note on declare_orthogonal:
    Cross-group orthogonality is consumed by the L1 chi-squared validator
    (validation/structural.py::check_orthogonal_independence) and Phase 3
    view enumeration; it is a no-op for generation. The skeleton defaults
    to independent sampling for any cross-group pair not explicitly linked
    by add_group_dependency. This matches storyline §2.2:
    "Cross-group independence is opt-in, not default."
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd

from ..exceptions import InvalidParameterError
from ..types import GroupDependency

logger = logging.getLogger(__name__)


# ================================================================
# Top-level dispatcher
# ================================================================

def build_skeleton(
    columns: dict[str, dict[str, Any]],
    target_rows: int,
    group_dependencies: list[GroupDependency],
    topo_order: list[str],
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Phase α: generate all non-measure columns in topological order.

    [Subtask 4.1.1, 4.1.2, 4.1.3, 4.1.4, 4.1.5]

    Args:
        columns: The full column registry (OrderedDict of name → metadata).
        target_rows: Number of rows to generate.
        group_dependencies: List of GroupDependency declarations.
        topo_order: Full DAG topological order.
        rng: Seeded NumPy random generator.

    Returns:
        Dict mapping column name → numpy array of length *target_rows*.
        Only non-measure columns are populated.
    """
    rows: dict[str, np.ndarray] = {}

    for col_name in topo_order:
        col_meta = columns[col_name]
        col_type = col_meta.get("type")

        if col_type == "categorical":
            parent = col_meta.get("parent")

            if parent is None:
                dep = _get_dependency_for_root(col_name, group_dependencies)

                if dep is None:
                    rows[col_name] = sample_independent_root(
                        col_name, col_meta, target_rows, rng,
                    )
                else:
                    rows[col_name] = sample_dependent_root(
                        col_name, col_meta, dep, rows, target_rows, rng,
                    )
            else:
                rows[col_name] = sample_child_category(
                    col_name, col_meta, rows, target_rows, rng,
                )

        elif col_type == "temporal":
            rows[col_name] = sample_temporal_root(
                col_name, col_meta, target_rows, rng,
            )

        elif col_type == "temporal_derived":
            rows[col_name] = derive_temporal_child(col_name, col_meta, rows)

        elif col_type == "measure":
            logger.debug(
                "build_skeleton: skipping measure column '%s' "
                "(blocked — Sprint 5 is skeleton-only).",
                col_name,
            )
            continue

        else:
            logger.warning(
                "build_skeleton: unknown column type '%s' for '%s', skipping.",
                col_type,
                col_name,
            )
            continue

    return rows


# ================================================================
# Categorical samplers
# ================================================================

def sample_independent_root(
    col_name: str,
    col_meta: dict[str, Any],
    target_rows: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample an independent categorical root from its marginal weights.

    [Subtask 4.1.1]
    """
    values = col_meta["values"]
    weights = col_meta["weights"]

    values_arr = np.array(values, dtype=object)
    weights_arr = np.array(weights, dtype=np.float64)

    result = rng.choice(values_arr, size=target_rows, p=weights_arr)

    logger.debug(
        "sample_independent_root: '%s' → %d values sampled.",
        col_name, len(result),
    )
    return result


def sample_dependent_root(
    col_name: str,
    col_meta: dict[str, Any],
    dep: GroupDependency,
    rows: dict[str, np.ndarray],
    target_rows: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample a cross-group dependent root conditioned on parent root values.

    [Subtask 4.1.2; DS-4 multi-column on]

    Walks ``dep.conditional_weights`` to ``len(dep.on)`` levels deep.
    For ``len(dep.on) == 1`` the original batched per-parent-value
    path is retained so RNG draw ordering is byte-identical to before.
    """
    cw = dep.conditional_weights
    child_values = col_meta["values"]
    child_arr = np.array(child_values, dtype=object)
    result = np.empty(target_rows, dtype=object)

    # Single-parent fast path: byte-identical RNG draw sequence to v1
    if len(dep.on) == 1:
        parent_col_name = dep.on[0]
        parent_values = rows[parent_col_name]

        for parent_val, child_weight_map in cw.items():
            mask = parent_values == parent_val
            n_matching = int(np.sum(mask))

            if n_matching == 0:
                continue

            weights_for_parent = np.array(
                [child_weight_map.get(cv, 0.0) for cv in child_values],
                dtype=np.float64,
            )

            weight_sum = weights_for_parent.sum()
            if weight_sum > 0:
                weights_for_parent = weights_for_parent / weight_sum

            sampled = rng.choice(
                child_arr, size=n_matching, p=weights_for_parent,
            )
            result[mask] = sampled

        logger.debug(
            "sample_dependent_root: '%s' conditioned on '%s' → %d values.",
            col_name, parent_col_name, target_rows,
        )
        return result

    # Multi-parent: walk per-row through the nested dict
    parent_arrays = [rows[p] for p in dep.on]
    for i in range(target_rows):
        node: Any = cw
        for arr in parent_arrays:
            node = node[arr[i]]
        # node is {child_val: weight} (already normalized at decl time)
        weights_for_row = np.array(
            [node.get(cv, 0.0) for cv in child_values],
            dtype=np.float64,
        )
        s = weights_for_row.sum()
        if s > 0:
            weights_for_row = weights_for_row / s
        result[i] = rng.choice(child_arr, p=weights_for_row)

    logger.debug(
        "sample_dependent_root: '%s' conditioned on %s → %d values.",
        col_name, list(dep.on), target_rows,
    )
    return result


def sample_child_category(
    col_name: str,
    col_meta: dict[str, Any],
    rows: dict[str, np.ndarray],
    target_rows: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample a within-group child category conditioned on its parent.

    [Subtask 4.1.3]
    """
    parent_name = col_meta["parent"]
    child_values = col_meta["values"]
    weights = col_meta["weights"]
    child_arr = np.array(child_values, dtype=object)

    if isinstance(weights, list):
        weights_arr = np.array(weights, dtype=np.float64)
        result = rng.choice(child_arr, size=target_rows, p=weights_arr)

        logger.debug(
            "sample_child_category: '%s' with flat weights → %d values.",
            col_name, len(result),
        )
        return result

    parent_values = rows[parent_name]
    result = np.empty(target_rows, dtype=object)

    for parent_val, weight_vec in weights.items():
        mask = parent_values == parent_val
        n_matching = int(np.sum(mask))

        if n_matching == 0:
            continue

        weights_arr = np.array(weight_vec, dtype=np.float64)
        weight_sum = weights_arr.sum()
        if weight_sum > 0:
            weights_arr = weights_arr / weight_sum

        sampled = rng.choice(child_arr, size=n_matching, p=weights_arr)
        result[mask] = sampled

    logger.debug(
        "sample_child_category: '%s' conditioned on '%s' → %d values.",
        col_name, parent_name, target_rows,
    )
    return result


# ================================================================
# Temporal samplers
# ================================================================

def sample_temporal_root(
    col_name: str,
    col_meta: dict[str, Any],
    target_rows: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample a temporal root column as uniform random dates.

    [Subtask 4.1.4]
    """
    start_raw = col_meta["start"]
    end_raw = col_meta["end"]
    freq: str = col_meta["freq"]

    # Handle both date objects and ISO-8601 strings from the SDK
    start_date = date.fromisoformat(start_raw) if isinstance(start_raw, str) else start_raw
    end_date = date.fromisoformat(end_raw) if isinstance(end_raw, str) else end_raw

    # Map SDK freq codes ("D", "W-*", "MS") to engine names
    FREQ_MAP = {"D": "daily", "MS": "monthly"}
    if freq.startswith("W-"):
        freq_key = "weekly"
    else:
        freq_key = FREQ_MAP.get(freq, freq)

    if freq_key == "daily":
        eligible_dates = enumerate_daily_dates(start_date, end_date)
    elif freq_key == "weekly":
        eligible_dates = enumerate_period_dates(
            start_date, end_date, snap_weekday=0,
        )
    elif freq_key == "monthly":
        eligible_dates = enumerate_monthly_dates(start_date, end_date)
    else:
        raise InvalidParameterError(
            param_name="freq",
            value=0.0,
            reason=(
                f"Unsupported temporal frequency '{freq}' for column "
                f"'{col_name}'. Supported: 'D'/'daily', 'W-*'/'weekly', 'MS'/'monthly'"
            ),
        )

    dates_as_dt64 = np.array(eligible_dates, dtype="datetime64[D]")
    indices = rng.integers(0, len(dates_as_dt64), size=target_rows)
    result = dates_as_dt64[indices]
    result = result.astype("datetime64[ns]")

    logger.debug(
        "sample_temporal_root: '%s' freq='%s' → %d dates from pool of %d.",
        col_name, freq, target_rows, len(dates_as_dt64),
    )
    return result


def enumerate_daily_dates(start: date, end: date) -> list[date]:
    """Build a list of all dates in [start, end] inclusive.

    [Subtask 4.1.4 helper]
    """
    n_days = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(n_days)]


def enumerate_period_dates(
    start: date, end: date, snap_weekday: int,
) -> list[date]:
    """Build a list of all dates with a specific weekday in [start, end].

    [Subtask 4.1.4 helper — weekly frequency]
    """
    days_ahead = (snap_weekday - start.weekday()) % 7
    current = start + timedelta(days=days_ahead)

    result: list[date] = []
    while current <= end:
        result.append(current)
        current += timedelta(days=7)
    return result


def enumerate_monthly_dates(start: date, end: date) -> list[date]:
    """Build a list of all 1st-of-month dates in [start, end].

    [Subtask 4.1.4 helper — monthly frequency]
    """
    result: list[date] = []

    if start.day == 1:
        current = start
    else:
        if start.month == 12:
            current = date(start.year + 1, 1, 1)
        else:
            current = date(start.year, start.month + 1, 1)

    while current <= end:
        result.append(current)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    return result


def derive_temporal_child(
    col_name: str,
    col_meta: dict[str, Any],
    rows: dict[str, np.ndarray],
) -> np.ndarray:
    """Derive a temporal child column from the temporal root.

    [Subtask 4.1.5]
    """
    # SDK stores the temporal root reference as "source", not "parent"
    parent_name = col_meta.get("source") or col_meta.get("parent")
    derivation = col_meta["derivation"]

    temporal_root = rows[parent_name]
    dt_index = pd.DatetimeIndex(temporal_root)

    if derivation == "day_of_week":
        result = dt_index.dayofweek.to_numpy(dtype=np.int64)
    elif derivation == "month":
        result = dt_index.month.to_numpy(dtype=np.int64)
    elif derivation == "quarter":
        result = dt_index.quarter.to_numpy(dtype=np.int64)
    elif derivation == "is_weekend":
        dow_values = dt_index.dayofweek.to_numpy(dtype=np.int64)
        result = (dow_values >= 5).astype(bool)
    else:
        raise ValueError(
            f"Unknown temporal derivation '{derivation}' for column "
            f"'{col_name}'. This should have been caught at declaration."
        )

    logger.debug(
        "derive_temporal_child: '%s' (derivation='%s') → %d values.",
        col_name, derivation, len(result),
    )
    return result


# ================================================================
# Internal helpers
# ================================================================

def _get_dependency_for_root(
    col_name: str,
    group_dependencies: list[GroupDependency],
) -> GroupDependency | None:
    """Look up a GroupDependency where *col_name* is the child_root.

    [Subtask 4.1.2 helper]
    """
    for dep in group_dependencies:
        if dep.child_root == col_name:
            return dep
    return None
