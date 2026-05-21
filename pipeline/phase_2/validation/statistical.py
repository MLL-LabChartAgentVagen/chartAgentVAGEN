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
import math
from typing import Any

import numpy as np
import pandas as pd
import scipy.stats

from ..engine.distributions import clamp_params, expected_cdf
from ..types import Check

logger = logging.getLogger(__name__)

# Path D — sparse-cell + KS over-sensitivity tunables. See
# docs/soft_failure_fix/PATH_D_KS_SPARSE_CELLS.md for the why.
KS_MIN_CELL_SIZE = 30          # KS unreliable below n=30
KS_BASE_ALPHA = 0.05
KS_AGGREGATE_PASS_RATE = 0.9   # ≥90% of tested cells must pass for aggregate to pass
KS_DETAIL_CELL_CAP = 10        # max number of per-cell entries listed in detail string

# Phase A — n-aware group_dep / marginal weight thresholds. See
# docs/soft_failure_fix/validation/PINGYUE_OPENAI_CAL_ANALYSIS.md §6 + §8.1.
# Per (cell, child_level): threshold = 0.10 + 1.96·√(p̂(1-p̂)/n)
# Skip cells with n < GROUP_DEP_MIN_CELL_SIZE (untestable for proportion drift).
# Used by check_group_dependency_transitions and check_marginal_weights.
GROUP_DEP_MIN_CELL_SIZE = 10
GROUP_DEP_BASE_DELTA = 0.10
GROUP_DEP_Z_95 = 1.96
GROUP_DEP_DETAIL_CELL_CAP = 10


def _wald_dev_threshold(
    n: int,
    p_hat: float,
    base: float = GROUP_DEP_BASE_DELTA,
    z: float = GROUP_DEP_Z_95,
) -> float:
    """Per-cell n-aware deviation threshold for proportion drift checks.

    threshold = base + z · √(p̂(1-p̂)/n)

    The base floor catches real magnitude errors that survive at n→∞;
    the Wald term absorbs binomial sampling noise at small n. See
    docs/soft_failure_fix/validation/PINGYUE_OPENAI_CAL_ANALYSIS.md §6.
    """
    if n <= 0:
        return base
    wald = z * math.sqrt(max(p_hat * (1.0 - p_hat), 0.0) / n)
    return base + wald


def max_conditional_deviation(
    observed: dict[Any, Any],
    declared: dict[Any, Any],
) -> float:
    """Compute the max absolute deviation between observed and declared
    conditional weight distributions.

    [Subtask 8.3.7; DS-4 multi-column on]

    Recurses through arbitrarily nested dicts of equal depth. At a
    leaf node the values are floats keyed by child value; at non-leaf
    nodes the values are nested dicts keyed by parent value.

    Args:
        observed: Normalized conditional distribution (nested dict).
        declared: Declared conditional weights (nested dict).

    Returns:
        Maximum absolute deviation across all cells.
    """
    all_keys = set(observed.keys()) | set(declared.keys())
    if not all_keys:
        return 0.0

    # Determine leaf vs recursive level by inspecting any present value.
    sample_val: Any = None
    for d in (observed, declared):
        if d:
            sample_val = next(iter(d.values()))
            break

    if not isinstance(sample_val, dict):
        # Leaf: {child_val: weight} on both sides.
        max_dev = 0.0
        for k in all_keys:
            obs_val = float(observed.get(k, 0.0))
            decl_val = float(declared.get(k, 0.0))
            dev = abs(obs_val - decl_val)
            if dev > max_dev:
                max_dev = dev
        return max_dev

    # Recursive level: drill into each parent value.
    max_dev = 0.0
    for k in all_keys:
        obs_inner = observed.get(k, {})
        decl_inner = declared.get(k, {})
        dev = max_conditional_deviation(obs_inner, decl_inner)
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

    # Collect all categorical columns referenced in effects.
    # For mixture (IS-1) param_models the effects live inside per-component
    # param_models, so walk recursively.
    predictor_cols: set[str] = set()
    _collect_predictor_cols(param_model, columns_meta, predictor_cols)

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


def _collect_predictor_cols(
    param_model: dict[str, Any],
    columns_meta: dict[str, Any],
    out: set[str],
) -> None:
    """Walk a param_model (recursively for mixture) and collect categorical
    predictor columns referenced in any `effects` block. Mutates `out`.
    """
    components = param_model.get("components")
    if isinstance(components, list):
        for comp in components:
            sub_pm = comp.get("param_model") if isinstance(comp, dict) else None
            if isinstance(sub_pm, dict):
                _collect_predictor_cols(sub_pm, columns_meta, out)
        return
    for _param_key, param_spec in param_model.items():
        if not isinstance(param_spec, dict):
            continue
        effects = param_spec.get("effects", {})
        for effect_col in effects:
            cat_meta = columns_meta.get(effect_col, {})
            if cat_meta.get("type") == "categorical":
                out.add(effect_col)


def _compute_cell_params(
    col_meta: dict[str, Any],
    predictor_values: dict[str, str],
    columns_meta: dict[str, Any],
) -> dict[str, Any]:
    """Compute expected distribution parameters for a predictor cell.

    For each param key in param_model, computes:
        theta = intercept + sum(effects for the cell's predictor values)

    For mixture (DS-3) param_models, recurses per component and returns the
    shape consumed by _expected_cdf_mixture:
        {"components": [{"family", "weight", "params": <recursive>}, ...]}.

    Args:
        col_meta: Column metadata with param_model.
        predictor_values: Dict of predictor_col -> value for this cell.
        columns_meta: Full columns metadata.

    Returns:
        Dict of param_key -> computed theta value, or the recursive mixture
        shape described above.
    """
    param_model = col_meta.get("param_model", {})

    # Mixture (DS-3): recurse per component.
    if "components" in param_model:
        return {
            "components": [
                {
                    "family": c["family"],
                    "weight": float(c["weight"]),
                    "params": _compute_cell_params(
                        {"param_model": c.get("param_model", {})},
                        predictor_values, columns_meta,
                    ),
                }
                for c in param_model["components"]
            ]
        }

    result: dict[str, float] = {}
    for param_key, param_spec in param_model.items():
        # param_spec may be a dict (intercept + effects) or a numeric scalar.
        if isinstance(param_spec, dict):
            intercept = param_spec.get("intercept", 0.0)
            theta = intercept
            effects = param_spec.get("effects", {})
            for effect_col, effect_map in effects.items():
                cell_val = predictor_values.get(effect_col)
                if cell_val is not None and cell_val in effect_map:
                    theta += effect_map[cell_val]
        else:
            theta = float(param_spec)
        result[param_key] = theta

    # Clamp positive-only params (sigma/scale/rate) before handing to scipy.
    return clamp_params(result)


def check_stochastic_ks(
    df: pd.DataFrame,
    col_name: str,
    meta: dict[str, Any],
    patterns: list[dict[str, Any]] | None = None,
) -> list[Check]:
    """L2: KS test for stochastic measure distribution fit.

    [P3-16; Path D — sparse-cell + multiple-testing correction]

    Enumerates predictor cells via Cartesian product of categorical
    columns referenced in param_model effects. For each cell:
    - Skip if fewer than ``KS_MIN_CELL_SIZE`` rows (KS unreliable for small n).
    - Skip if the family's expected CDF is unavailable.
    - Cap at 100 cells via ``_iter_predictor_cells``.

    For cells that pass the gate, KS p-values are compared against a
    Bonferroni-corrected alpha (``KS_BASE_ALPHA / K`` where K is the count
    of tested cells). The result is collapsed into a SINGLE aggregate
    Check named ``ks_<col>``: passed iff the per-cell pass rate meets
    ``KS_AGGREGATE_PASS_RATE``. The detail string lists per-cell stats
    so the original semantic (threshold, D, p) remains observable.

    Rows matching pattern targets on this column are excluded before
    testing (T9 fix), since pattern injection deliberately distorts the
    distribution.

    Args:
        df: Generated DataFrame.
        col_name: Stochastic measure column name.
        meta: Schema metadata with enriched "columns" dict.
        patterns: Optional pattern specs — rows matching targets on this
            column are excluded from KS testing.

    Returns:
        List containing exactly one aggregate Check named ``ks_<col>``.
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

    cells = _iter_predictor_cells(work_df, col_name, col_meta, columns_meta)
    if not cells:
        return [Check(
            name=f"ks_{col_name}",
            passed=True,
            detail="No predictor cells with sufficient rows to test.",
        )]

    # Stage 1: enumerate cells, skip those below the n threshold or with
    # no usable CDF. ``per_cell`` collects raw KS results pre-Bonferroni.
    per_cell: list[tuple[str, float, float, int]] = []  # (label, D, p, n)
    skipped_no_cdf = 0
    skipped_small = 0
    for predictor_values, cell_df in cells:
        cell_params = _compute_cell_params(col_meta, predictor_values, columns_meta)
        dist = expected_cdf(family, cell_params)

        cell_label = (
            ",".join(f"{k}={v}" for k, v in predictor_values.items())
            if predictor_values else "global"
        )

        if dist is None:
            skipped_no_cdf += 1
            continue

        sample = cell_df[col_name].dropna().values.astype(float)
        if len(sample) < KS_MIN_CELL_SIZE:
            skipped_small += 1
            continue

        stat, p_value = scipy.stats.kstest(sample, dist.cdf)
        per_cell.append((cell_label, float(stat), float(p_value), len(sample)))

    # Stage 2: Bonferroni + aggregate into a single Check.
    skipped_total = skipped_no_cdf + skipped_small
    K = len(per_cell)
    if K == 0:
        return [Check(
            name=f"ks_{col_name}",
            passed=True,
            detail=(
                f"No testable cells "
                f"(all n<{KS_MIN_CELL_SIZE} or family CDF unavailable). "
                f"{skipped_total} cell(s) skipped "
                f"({skipped_small} small-n, {skipped_no_cdf} no-CDF)."
            ),
        )]

    alpha = KS_BASE_ALPHA / K
    finalized: list[tuple[str, bool, float, float, int]] = [
        (label, p > alpha, D, p, n) for (label, D, p, n) in per_cell
    ]
    passed_cnt = sum(1 for r in finalized if r[1])
    rate = passed_cnt / K
    overall_passed = rate >= KS_AGGREGATE_PASS_RATE

    # Build observable detail: header + failed cells (capped) + leading
    # passed cells (capped) so a downstream reader can extract any
    # per-cell (n, D, p) for spot-checking the threshold semantic.
    parts = [
        f"{passed_cnt}/{K} cells passed @ α={alpha:.4f} "
        f"(Bonferroni K={K}, threshold {KS_AGGREGATE_PASS_RATE:.0%}); "
        f"{skipped_total} cells skipped "
        f"({skipped_small} small-n, {skipped_no_cdf} no-CDF)."
    ]
    failed = [r for r in finalized if not r[1]]
    if failed:
        head = "; ".join(
            f"{label} (n={n}, D={D:.4f}, p={p:.4f})"
            for (label, _ok, D, p, n) in failed[:KS_DETAIL_CELL_CAP]
        )
        more = max(0, len(failed) - KS_DETAIL_CELL_CAP)
        parts.append(
            f"Failed cells: {head}" + (f"; (+{more} more)" if more else "")
        )
    passed_examples = [r for r in finalized if r[1]]
    if passed_examples:
        head = "; ".join(
            f"{label} (n={n}, D={D:.4f}, p={p:.4f})"
            for (label, _ok, D, p, n) in passed_examples[:KS_DETAIL_CELL_CAP]
        )
        more = max(0, len(passed_examples) - KS_DETAIL_CELL_CAP)
        parts.append(
            f"Passed cells: {head}" + (f"; (+{more} more)" if more else "")
        )

    return [Check(
        name=f"ks_{col_name}",
        passed=overall_passed,
        detail=" ".join(parts),
    )]


def _get_formula_measure_deps(
    formula: str,
    col_name: str,
    columns_meta: dict[str, Any],
) -> set[str]:
    """Extract measure column names directly referenced in a structural formula.

    Parses the formula for identifier symbols, then filters to those
    that exist in columns_meta as measure-type columns (excluding the
    measure being validated itself).

    Args:
        formula: Arithmetic formula string.
        col_name: The structural measure being validated (excluded from result).
        columns_meta: The columns metadata dict.

    Returns:
        Set of measure column names that are direct formula dependencies.
    """
    from ..sdk.validation import extract_formula_symbols

    all_symbols = extract_formula_symbols(formula)
    dep_measures: set[str] = set()
    for sym in all_symbols:
        if sym == col_name:
            continue
        sym_meta = columns_meta.get(sym, {})
        if sym_meta.get("type") == "measure":
            dep_measures.add(sym)
    return dep_measures


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
    - Excludes rows matching pattern targets for this column or any
      upstream measure referenced in the formula (P3-8).  This prevents
      false residual inflation from patterns that modify formula inputs.

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
    # Exclude rows where patterns modify this column OR any upstream
    # measure referenced in the formula.  Upstream patterns cause
    # systematic residual inflation because downstream values were
    # computed from pre-pattern upstream values in Phase β.
    work_df = df
    if patterns:
        formula_deps = _get_formula_measure_deps(
            formula, col_name, columns_meta,
        )
        affected_cols = {col_name} | formula_deps

        pattern_mask = pd.Series(False, index=df.index)
        for p in patterns:
            if p.get("col") in affected_cols:
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

    Per (leaf cell, child_level), checks the empirical-vs-declared
    deviation against an n-aware Wald 95% CI threshold:
    ``threshold = 0.10 + 1.96·√(p̂(1-p̂)/n_cell)``. Cells with
    ``n_cell < GROUP_DEP_MIN_CELL_SIZE`` are skipped as untestable for
    proportion drift. All-pass aggregation: one offending (cell, level)
    fails the whole Check. See PINGYUE_OPENAI_CAL_ANALYSIS.md §6 + §8.1.

    [DS-4 multi-column on]: walks the full ``on`` tuple (not just
    ``on[0]``) so nested declared weights are compared against an
    equally-nested observed distribution at the leaf level.

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
        on_cols = list(dep["on"])
        declared_cw = dep["conditional_weights"]

        if not on_cols:
            continue

        missing_cols = [
            c for c in on_cols + [child_root] if c not in df.columns
        ]
        if missing_cols:
            checks.append(Check(
                name=f"group_dep_{child_root}",
                passed=False,
                detail=(
                    f"Columns {missing_cols} not found in DataFrame "
                    f"(group dep child='{child_root}', on={on_cols})."
                ),
            ))
            continue

        # Walk groupby at the leaf level of `on_cols`. pandas.groupby with
        # a list returns tuple keys even for length 1 — normalize uniformly.
        # For each leaf cell: walk declared_cw down cell_key to its
        # child→weight dict, then test each declared child_level against
        # its empirical frequency under the per-cell Wald threshold.
        per_cell_levels: list[tuple[tuple[str, ...], str, int, float, float]] = []
        # ^ (cell_path, child_level, n_cell, p_hat_declared, dev)
        skipped_cells: list[tuple[tuple[str, ...], int]] = []
        n_decl_lookups_missed = 0

        for raw_key, group_df in df.groupby(on_cols):
            cell_key_raw = raw_key if isinstance(raw_key, tuple) else (raw_key,)
            cell_key = tuple(str(k) for k in cell_key_raw)
            n_cell = len(group_df)

            # Walk declared_cw down to the leaf child→weight dict.
            node: Any = declared_cw
            lookup_ok = True
            for k in cell_key_raw:
                if isinstance(node, dict):
                    if str(k) in node:
                        node = node[str(k)]
                    elif k in node:
                        node = node[k]
                    else:
                        lookup_ok = False
                        break
                else:
                    lookup_ok = False
                    break
            if not lookup_ok or not isinstance(node, dict):
                n_decl_lookups_missed += 1
                continue

            if n_cell < GROUP_DEP_MIN_CELL_SIZE:
                skipped_cells.append((cell_key, n_cell))
                continue

            empirical = group_df[child_root].value_counts(normalize=True)
            emp_lookup = {str(k): float(v) for k, v in empirical.items()}
            for child_level, p_hat in node.items():
                emp = emp_lookup.get(str(child_level), 0.0)
                dev = abs(emp - float(p_hat))
                per_cell_levels.append(
                    (cell_key, str(child_level), n_cell, float(p_hat), dev)
                )

        offenders: list[
            tuple[tuple[str, ...], str, int, float, float, float]
        ] = []
        for cell_key, lvl, n_cell, p_hat, dev in per_cell_levels:
            t = _wald_dev_threshold(n_cell, p_hat)
            if dev >= t:
                offenders.append((cell_key, lvl, n_cell, p_hat, dev, t))

        passed = not offenders

        summary = (
            f"parents={on_cols}, child='{child_root}', "
            f"tested={len(per_cell_levels)} (cell,level), "
            f"skipped_cells={len(skipped_cells)} "
            f"(n<{GROUP_DEP_MIN_CELL_SIZE}), offenders={len(offenders)}"
        )
        if offenders:
            head = offenders[:GROUP_DEP_DETAIL_CELL_CAP]
            lines = [
                f"{'>'.join(ck)}->{lvl}: n={n}, "
                f"p_hat={ph:.3f}, dev={dv:.4f}, thresh={th:.4f}"
                for (ck, lvl, n, ph, dv, th) in head
            ]
            if len(offenders) > GROUP_DEP_DETAIL_CELL_CAP:
                lines.append(
                    f"...+{len(offenders) - GROUP_DEP_DETAIL_CELL_CAP} more"
                )
            detail = summary + " | " + "; ".join(lines)
        else:
            detail = summary
        if n_decl_lookups_missed:
            detail += f" | declaration lookup misses: {n_decl_lookups_missed}"

        checks.append(Check(
            name=f"group_dep_{child_root}",
            passed=passed,
            detail=detail,
        ))

    return checks
