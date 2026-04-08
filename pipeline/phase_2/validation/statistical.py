"""
L2 Statistical Validation Checks.

Implements: §2.9 L2
- check_structural_residuals: residual analysis for structural measures (P3-15, P3-10, P3-8)
- check_stochastic_ks: KS test with predictor cell enumeration (P3-16)
- check_group_dependency_transitions: conditional weight distribution checks (stub)
"""
from __future__ import annotations

import itertools
import logging
from typing import Any

import numpy as np
import pandas as pd
import scipy.stats

from ..types import Check

logger = logging.getLogger(__name__)


def max_conditional_deviation(
    observed: dict[str, dict[str, float]],
    declared: dict[str, dict[str, float]],
) -> float:
    """Compute the max absolute deviation between observed and declared
    conditional weight distributions.

    [Subtask 8.3.7]

    Args:
        observed: Normalized conditional distribution (nested dict).
        declared: Declared conditional weights (nested dict).

    Returns:
        Maximum absolute deviation across all cells.
    """
    max_dev: float = 0.0
    all_parent_keys = set(observed.keys()) | set(declared.keys())

    for parent_key in all_parent_keys:
        obs_inner = observed.get(parent_key, {})
        decl_inner = declared.get(parent_key, {})
        all_child_keys = set(obs_inner.keys()) | set(decl_inner.keys())

        for child_key in all_child_keys:
            obs_val = obs_inner.get(child_key, 0.0)
            decl_val = decl_inner.get(child_key, 0.0)
            dev = abs(obs_val - decl_val)
            if dev > max_dev:
                max_dev = dev

    return max_dev


def _iter_predictor_cells(
    df: pd.DataFrame,
    col_name: str,
    col_meta: dict[str, Any],
    columns_meta: dict[str, Any],
    min_rows: int = 5,
    max_cells: int = 100,
) -> list[tuple[dict[str, str], pd.DataFrame]]:
    """Enumerate predictor cells for a stochastic measure via Cartesian product.

    [P3-16]

    1. Identify categorical columns referenced in param_model effects.
    2. Compute Cartesian product of those columns' value sets.
    3. Filter DataFrame rows for each cell.
    4. Skip cells with fewer than min_rows rows.
    5. Cap at max_cells (sorted by cell size descending — test largest first).

    Args:
        df: Generated DataFrame.
        col_name: Stochastic measure column name.
        col_meta: Column metadata with param_model.
        columns_meta: Full columns metadata dict.
        min_rows: Minimum rows per cell (default 5).
        max_cells: Maximum cells to return (default 100).

    Returns:
        List of (predictor_values_dict, filtered_df) tuples.
    """
    param_model = col_meta.get("param_model", {})

    # Collect all categorical columns referenced in effects
    predictor_cols: set[str] = set()
    for param_key, param_spec in param_model.items():
        effects = param_spec.get("effects", {})
        for effect_col in effects:
            cat_meta = columns_meta.get(effect_col, {})
            if cat_meta.get("type") == "categorical":
                predictor_cols.add(effect_col)

    if not predictor_cols:
        # No predictors — single global cell
        if len(df) >= min_rows:
            return [({}, df)]
        return []

    # Get value sets for each predictor column
    predictor_cols_sorted = sorted(predictor_cols)
    value_sets = []
    for pc in predictor_cols_sorted:
        pc_meta = columns_meta.get(pc, {})
        values = pc_meta.get("values")
        if values is None:
            values = sorted(df[pc].dropna().unique().tolist())
        value_sets.append(values)

    # Cartesian product
    cells: list[tuple[dict[str, str], pd.DataFrame]] = []
    for combo in itertools.product(*value_sets):
        predictor_dict = dict(zip(predictor_cols_sorted, combo))
        mask = pd.Series(True, index=df.index)
        for col, val in predictor_dict.items():
            mask &= df[col] == val
        cell_df = df[mask]
        if len(cell_df) >= min_rows:
            cells.append((predictor_dict, cell_df))

    # Sort by cell size descending, cap at max_cells
    cells.sort(key=lambda x: len(x[1]), reverse=True)
    return cells[:max_cells]


def _expected_cdf(family: str, params: dict[str, float]) -> Any:
    """Build a scipy frozen distribution for KS testing.

    Args:
        family: Distribution family name.
        params: Distribution parameters (mu, sigma, etc.).

    Returns:
        A scipy.stats frozen distribution, or None if unsupported.
    """
    mu = params.get("mu", 0.0)
    sigma = params.get("sigma", 1.0)

    if family == "gaussian":
        return scipy.stats.norm(loc=mu, scale=sigma)
    elif family == "lognormal":
        return scipy.stats.lognorm(s=sigma, scale=np.exp(mu))
    elif family == "exponential":
        rate = max(mu, 1e-6)
        return scipy.stats.expon(scale=1.0 / rate)
    elif family == "gamma":
        shape = max(mu, 1e-6)
        scale = max(sigma, 1e-6)
        return scipy.stats.gamma(a=shape, scale=scale)
    elif family == "beta":
        a = max(mu, 1e-6)
        b = max(sigma, 1e-6)
        return scipy.stats.beta(a, b)
    elif family == "uniform":
        low, high = mu, sigma
        if high <= low:
            return None
        return scipy.stats.uniform(loc=low, scale=high - low)
    elif family == "poisson":
        # KS test on discrete distributions is approximate
        return None
    return None


def _compute_cell_params(
    col_meta: dict[str, Any],
    predictor_values: dict[str, str],
    columns_meta: dict[str, Any],
) -> dict[str, float]:
    """Compute expected distribution parameters for a predictor cell.

    For each param key in param_model, computes:
        theta = intercept + sum(effects for the cell's predictor values)

    Args:
        col_meta: Column metadata with param_model.
        predictor_values: Dict of predictor_col -> value for this cell.
        columns_meta: Full columns metadata.

    Returns:
        Dict of param_key -> computed theta value.
    """
    param_model = col_meta.get("param_model", {})
    result: dict[str, float] = {}

    for param_key, param_spec in param_model.items():
        intercept = param_spec.get("intercept", 0.0)
        theta = intercept
        effects = param_spec.get("effects", {})
        for effect_col, effect_map in effects.items():
            cell_val = predictor_values.get(effect_col)
            if cell_val is not None and cell_val in effect_map:
                theta += effect_map[cell_val]
        # Clamp positive-only params
        if param_key in ("sigma", "scale", "rate"):
            theta = max(theta, 1e-6)
        result[param_key] = theta

    return result


def check_stochastic_ks(
    df: pd.DataFrame,
    col_name: str,
    meta: dict[str, Any],
    patterns: list[dict[str, Any]] | None = None,
) -> list[Check]:
    """L2: KS test for stochastic measure distribution fit.

    [P3-16]

    Enumerates predictor cells via Cartesian product of categorical
    columns referenced in param_model effects. For each cell:
    - Skip if fewer than 5 rows
    - Cap at 100 cells (largest first)
    - Run scipy.stats.kstest with expected distribution parameters
    - Pass threshold: p_value > 0.05

    Rows matching pattern targets on this column are excluded before
    testing, since pattern injection deliberately distorts the distribution.

    Args:
        df: Generated DataFrame.
        col_name: Stochastic measure column name.
        meta: Schema metadata with enriched "columns" dict.
        patterns: Optional pattern specs — rows matching targets on this
            column are excluded from KS testing.

    Returns:
        List of Checks, one per tested predictor cell.
    """
    # Exclude pattern-targeted rows (same logic as check_structural_residuals)
    work_df = df
    if patterns:
        pattern_mask = pd.Series(False, index=df.index)
        for p in patterns:
            if p.get("col") == col_name:
                try:
                    pattern_mask |= df.eval(p["target"])
                except Exception:
                    pass
        work_df = df[~pattern_mask]

    columns_meta = meta.get("columns", {})
    col_meta = columns_meta.get(col_name, {})
    family = col_meta.get("family")

    if family is None:
        return [Check(
            name=f"ks_{col_name}",
            passed=False,
            detail=f"No family found for stochastic measure '{col_name}'.",
        )]

    if family == "mixture":
        return [Check(
            name=f"ks_{col_name}",
            passed=True,
            detail="mixture distribution KS test not yet implemented",
        )]

    cells = _iter_predictor_cells(work_df, col_name, col_meta, columns_meta)
    if not cells:
        return [Check(
            name=f"ks_{col_name}",
            passed=True,
            detail="No predictor cells with sufficient rows to test.",
        )]

    checks: list[Check] = []
    for predictor_values, cell_df in cells:
        cell_params = _compute_cell_params(col_meta, predictor_values, columns_meta)
        dist = _expected_cdf(family, cell_params)

        cell_label = (
            ",".join(f"{k}={v}" for k, v in predictor_values.items())
            if predictor_values else "global"
        )

        if dist is None:
            checks.append(Check(
                name=f"ks_{col_name}",
                passed=True,
                detail=f"[{cell_label}] family='{family}' — KS CDF not available, skipped.",
            ))
            continue

        sample = cell_df[col_name].dropna().values.astype(float)
        if len(sample) < 5:
            continue

        stat, p_value = scipy.stats.kstest(sample, dist.cdf)
        passed = bool(p_value > 0.05)
        checks.append(Check(
            name=f"ks_{col_name}",
            passed=passed,
            detail=(
                f"[{cell_label}] n={len(sample)}, D={stat:.4f}, "
                f"p={p_value:.4f} ({'>' if passed else '<='} 0.05)"
            ),
        ))

    if not checks:
        checks.append(Check(
            name=f"ks_{col_name}",
            passed=True,
            detail="No testable predictor cells.",
        ))

    return checks


def check_structural_residuals(
    df: pd.DataFrame,
    col_name: str,
    meta: dict[str, Any],
    patterns: list[dict[str, Any]] | None = None,
) -> Check:
    """L2: Residual analysis for structural measures.

    [P3-15, P3-10, P3-8]

    Computes residuals between observed values and formula-predicted values.
    - When noise_sigma == 0: deterministic formula, residuals should be near-zero
      (std < 1e-6). Guards against divide-by-zero (P3-15).
    - When noise_sigma > 0: checks abs(residuals.std() - sigma) / sigma < 0.2.
    - Excludes rows matching pattern targets for the same column (P3-8).

    Args:
        df: Generated DataFrame.
        col_name: Structural measure column name.
        meta: Schema metadata with enriched "columns" dict.
        patterns: Optional pattern specs — rows matching targets on this
            column are excluded from residual computation (P3-8).

    Returns:
        Check named "residual_{col_name}".
    """
    from ..engine.measures import _safe_eval_formula, _resolve_effects

    columns_meta = meta.get("columns", {})
    col_meta = columns_meta.get(col_name, {})
    formula = col_meta.get("formula")

    if formula is None:
        return Check(
            name=f"residual_{col_name}",
            passed=False,
            detail=f"No formula found for structural measure '{col_name}'.",
        )

    # --- P3-8: Exclude pattern-targeted rows ---
    work_df = df
    if patterns:
        pattern_mask = pd.Series(False, index=df.index)
        for p in patterns:
            if p.get("col") == col_name:
                try:
                    pattern_mask |= df.eval(p["target"])
                except Exception:
                    pass  # If target expression fails, skip exclusion
        work_df = df[~pattern_mask]

    if len(work_df) == 0:
        return Check(
            name=f"residual_{col_name}",
            passed=False,
            detail="All rows excluded by pattern masks; no residuals to check.",
        )

    # --- Compute predicted values row by row ---
    effects_spec = col_meta.get("effects", {})
    predicted = np.empty(len(work_df), dtype=float)

    for i, (idx, row) in enumerate(work_df.iterrows()):
        context: dict[str, float] = {}
        # Add other measure values as context
        for other_col, other_info in columns_meta.items():
            if other_info.get("type") == "measure" and other_col != col_name:
                if other_col in work_df.columns:
                    context[other_col] = float(row[other_col])
        # Resolve effects
        if effects_spec:
            resolved = _resolve_effects(col_meta, dict(row), columns_meta)
            context.update(resolved)
        try:
            predicted[i] = _safe_eval_formula(formula, context)
        except Exception as exc:
            return Check(
                name=f"residual_{col_name}",
                passed=False,
                detail=f"Formula evaluation failed at row {idx}: {exc}",
            )

    observed = work_df[col_name].values.astype(float)
    residuals = observed - predicted

    # --- P3-15 / P3-10: divide-by-zero guard ---
    noise_sigma = col_meta.get("noise", {}).get("sigma", 0.0)

    if noise_sigma == 0 or not noise_sigma:
        # Deterministic formula — residuals should be near-zero
        residual_std = float(residuals.std())
        passed = bool(residual_std < 1e-6)
        detail = (
            f"noise_sigma=0 (deterministic), residual_std={residual_std:.8f} "
            f"({'<' if passed else '>='} 1e-6)"
        )
    else:
        residual_std = float(residuals.std())
        ratio = abs(residual_std - noise_sigma) / noise_sigma
        passed = bool(ratio < 0.2)
        detail = (
            f"noise_sigma={noise_sigma:.4f}, residual_std={residual_std:.4f}, "
            f"ratio={ratio:.4f} ({'<' if passed else '>='} 0.2)"
        )

    return Check(name=f"residual_{col_name}", passed=passed, detail=detail)


def check_group_dependency_transitions(
    df: pd.DataFrame,
    meta: dict[str, Any],
) -> list[Check]:
    """L2: Verify conditional weight distributions match declared weights.

    TODO [M5 SPEC_READY #9]: L2 group dependency conditional transition check.

    For each group dependency, computes the observed conditional distribution
    of the child_root column given each value of the parent (on[0]) column,
    then checks max absolute deviation < 0.10 against declared conditional_weights.

    Args:
        df: Generated DataFrame.
        meta: Schema metadata with "group_dependencies" key.

    Returns:
        List of Check results, one per group dependency.
    """
    checks: list[Check] = []
    group_deps = meta.get("group_dependencies", [])

    for dep in group_deps:
        child_root = dep["child_root"]
        on_cols = dep["on"]
        declared_cw = dep["conditional_weights"]

        if not on_cols:
            continue

        parent_col = on_cols[0]

        if parent_col not in df.columns or child_root not in df.columns:
            checks.append(Check(
                name=f"group_dep_{child_root}",
                passed=False,
                detail=(
                    f"Column '{parent_col}' or '{child_root}' "
                    f"not found in DataFrame."
                ),
            ))
            continue

        # Compute observed conditional distributions
        observed: dict[str, dict[str, float]] = {}
        for parent_val, group_df in df.groupby(parent_col):
            parent_val_str = str(parent_val)
            child_counts = group_df[child_root].value_counts(normalize=True)
            observed[parent_val_str] = {
                str(k): float(v) for k, v in child_counts.items()
            }

        dev = max_conditional_deviation(observed, declared_cw)
        passed = bool(dev < 0.10)
        detail = (
            f"parent='{parent_col}', child='{child_root}', "
            f"max_deviation={dev:.4f} ({'<' if passed else '>='} 0.10)"
        )
        checks.append(Check(
            name=f"group_dep_{child_root}",
            passed=passed,
            detail=detail,
        ))

    return checks
