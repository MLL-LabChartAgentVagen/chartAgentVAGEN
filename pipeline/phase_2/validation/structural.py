"""
L1 Structural Validation Checks.

Standalone functions that take (df, meta) or (meta,) and return Check objects.
Extracted from phase_2/validator.py.

Implements: §2.9 L1
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
import scipy.stats

from ..types import Check

logger = logging.getLogger(__name__)


def check_row_count(
    df: pd.DataFrame,
    meta: dict[str, Any],
) -> Check:
    """L1: Row count within 10% of target.

    [Subtask 8.2.1]

    §2.9 L1: abs(len(df) - target) / target < 0.1

    Args:
        df: Generated DataFrame.
        meta: Schema metadata with "total_rows" key.

    Returns:
        Check named "row_count".
    """
    target = meta["total_rows"]
    actual = len(df)
    deviation = abs(actual - target) / target
    passed = bool(deviation < 0.1)
    detail = (
        f"actual={actual}, target={target}, "
        f"deviation={deviation:.4f} ({'<' if passed else '>='} 0.1)"
    )
    logger.debug("check_row_count: %s", detail)
    return Check(name="row_count", passed=passed, detail=detail)


def check_categorical_cardinality(
    df: pd.DataFrame,
    meta: dict[str, Any],
) -> list[Check]:
    """L1: Each categorical column's unique count matches declared cardinality.

    [Subtask 8.2.2]

    Args:
        df: Generated DataFrame.
        meta: Schema metadata.

    Returns:
        List of Checks, one per categorical column.
    """
    checks: list[Check] = []
    columns_meta = meta.get("columns")
    if columns_meta is None:
        logger.debug(
            "check_categorical_cardinality: no 'columns' key in meta, skipping."
        )
        return checks

    # Handle both dict and list formats for columns metadata
    if isinstance(columns_meta, dict):
        items = [
            {"name": name, **info} for name, info in columns_meta.items()
        ]
    else:
        items = columns_meta

    for col in items:
        if col.get("type") != "categorical":
            continue

        col_name = col.get("name", "")
        if not col_name:
            continue

        declared = col.get("cardinality")
        if declared is None:
            values = col.get("values")
            if values is not None:
                declared = len(values)
            else:
                continue

        if col_name not in df.columns:
            continue

        actual = df[col_name].nunique()
        passed = bool(actual == declared)
        detail = f"actual={actual}, declared={declared}"
        checks.append(Check(
            name=f"cardinality_{col_name}",
            passed=passed,
            detail=detail,
        ))

    return checks


def check_orthogonal_independence(
    df: pd.DataFrame,
    meta: dict[str, Any],
) -> list[Check]:
    """L1: Chi-squared independence test on root pairs of orthogonal groups.

    [Subtask 8.2.5]

    §2.9 L1: chi2_contingency on root cross-group pairs, p_val > 0.05.

    Args:
        df: Generated DataFrame.
        meta: Schema metadata with "orthogonal_groups" and "dimension_groups".

    Returns:
        List of Checks, one per orthogonal pair.
    """
    checks: list[Check] = []
    orthogonal_groups = meta.get("orthogonal_groups")
    if not orthogonal_groups:
        return checks

    dimension_groups = meta["dimension_groups"]

    for pair in orthogonal_groups:
        group_a_name = pair["group_a"]
        group_b_name = pair["group_b"]

        ga = dimension_groups[group_a_name]
        gb = dimension_groups[group_b_name]
        root_a = ga["hierarchy"][0]
        root_b = gb["hierarchy"][0]

        ct = pd.crosstab(df[root_a], df[root_b])

        if ct.shape[0] < 2 or ct.shape[1] < 2:
            checks.append(Check(
                name=f"orthogonal_{root_a}_{root_b}",
                passed=False,
                detail=(
                    f"Degenerate contingency table shape={ct.shape}; "
                    f"chi-squared requires at least 2×2."
                ),
            ))
            continue

        try:
            _, p_val, _, _ = scipy.stats.chi2_contingency(ct)
        except ValueError as exc:
            checks.append(Check(
                name=f"orthogonal_{root_a}_{root_b}",
                passed=False,
                detail=f"chi2_contingency raised: {exc}",
            ))
            continue

        passed = bool(p_val > 0.05)
        detail = f"χ² p={p_val:.4f} (>0.05 = independent)"
        checks.append(Check(
            name=f"orthogonal_{root_a}_{root_b}",
            passed=passed,
            detail=detail,
        ))

    return checks


def check_measure_dag_acyclic(
    meta: dict[str, Any],
) -> Check:
    """L1: Verify measure_dag_order is acyclic (defense-in-depth).

    [Subtask 8.2.6]

    Args:
        meta: Schema metadata with optional "measure_dag_order" key.

    Returns:
        Check named "measure_dag_acyclic".
    """
    dag_order = meta.get("measure_dag_order", [])
    unique_count = len(set(dag_order))
    total_count = len(dag_order)
    passed = unique_count == total_count

    if passed:
        detail = f"{total_count} measures, all unique — acyclic."
    else:
        seen: set[str] = set()
        duplicates: list[str] = []
        for name in dag_order:
            if name in seen:
                duplicates.append(name)
            seen.add(name)
        detail = f"Duplicate nodes in dag_order: {duplicates}"

    return Check(name="measure_dag_acyclic", passed=passed, detail=detail)


def check_marginal_weights(
    df: pd.DataFrame,
    meta: dict[str, Any],
) -> list[Check]:
    """L1: Observed value frequencies match declared weights within 0.10.

    [P0-1 M5 gap]

    For each root categorical column (has weights, no parent), compute
    observed frequencies and check max absolute deviation < 0.10.

    Args:
        df: Generated DataFrame.
        meta: Schema metadata with enriched "columns" dict.

    Returns:
        List of Checks, one per root categorical column with declared weights.
    """
    checks: list[Check] = []
    columns_meta = meta.get("columns")
    if not columns_meta or not isinstance(columns_meta, dict):
        return checks

    for col_name, col_info in columns_meta.items():
        if col_info.get("type") != "categorical":
            continue
        # Only root categoricals (no parent)
        if col_info.get("parent") is not None:
            continue
        weights = col_info.get("weights")
        if weights is None:
            continue
        values = col_info.get("values", [])
        if not values or col_name not in df.columns:
            continue

        observed = df[col_name].value_counts(normalize=True)
        max_dev = 0.0
        for value, declared_weight in zip(values, weights):
            obs_freq = observed.get(value, 0.0)
            dev = abs(obs_freq - declared_weight)
            if dev > max_dev:
                max_dev = dev

        passed = bool(max_dev < 0.10)
        detail = f"max_deviation={max_dev:.4f} ({'<' if passed else '>='} 0.10)"
        logger.debug("check_marginal_weights[%s]: %s", col_name, detail)
        checks.append(Check(
            name=f"marginal_weights_{col_name}",
            passed=passed,
            detail=detail,
        ))

    return checks


def check_measure_finiteness(
    df: pd.DataFrame,
    meta: dict[str, Any],
) -> list[Check]:
    """L1: All measure columns contain only finite, non-null values.

    [P0-1 M5 gap]

    For each measure column in metadata, check that every value is
    present (not NaN) and finite (not inf/-inf).

    Args:
        df: Generated DataFrame.
        meta: Schema metadata with enriched "columns" dict.

    Returns:
        List of Checks, one per measure column.
    """
    checks: list[Check] = []
    columns_meta = meta.get("columns")
    if not columns_meta or not isinstance(columns_meta, dict):
        return checks

    for col_name, col_info in columns_meta.items():
        if col_info.get("type") != "measure":
            continue
        if col_name not in df.columns:
            continue

        series = df[col_name]
        na_count = int(series.isna().sum())
        non_null = series.dropna()
        inf_count = int((~np.isfinite(non_null)).sum()) if len(non_null) > 0 else 0

        passed = bool(na_count == 0 and inf_count == 0)
        if passed:
            detail = f"all {len(series)} values finite and non-null"
        else:
            detail = f"na_count={na_count}, inf_count={inf_count}"
        logger.debug("check_measure_finiteness[%s]: %s", col_name, detail)
        checks.append(Check(
            name=f"finiteness_{col_name}",
            passed=passed,
            detail=detail,
        ))

    return checks
