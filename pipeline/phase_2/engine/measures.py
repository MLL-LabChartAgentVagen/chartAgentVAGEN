"""
Engine Phase β — Measure generation.

Stochastic and structural measure generation with:
  - Restricted AST-based formula evaluator (P0-2)
  - Per-row parameter computation with intercept+effects
  - Parameter clamping (P3-1)

Implements: §2.8 stage β, P0-2
"""
from __future__ import annotations

import ast
import logging
from typing import Any

import numpy as np

from ..exceptions import InvalidParameterError

logger = logging.getLogger(__name__)


# =====================================================================
# Allowed AST binary operators
# =====================================================================

_ALLOWED_BINOPS: dict[type, Any] = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a ** b,
}


# =====================================================================
# Safe Formula Evaluator (P0-2)
# =====================================================================

def _safe_eval_formula(formula: str, context: dict[str, float]) -> float:
    """Evaluate an arithmetic formula using a restricted AST walker.

    [P0-2]

    Allowed nodes: Expression, BinOp (+,-,*,/,**), UnaryOp (- only),
    Constant (int/float), Num (legacy), Name (resolved from context).
    All other AST node types raise ValueError.

    Args:
        formula: Arithmetic expression string.
        context: Variable name -> numeric value bindings.

    Returns:
        Scalar float result.

    Raises:
        ValueError: On syntax errors, disallowed nodes, or undefined symbols.
    """
    try:
        tree = ast.parse(formula, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid formula syntax: {exc}") from exc

    def _eval_node(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _eval_node(node.body)

        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError(
                    f"Non-numeric constant in formula: {node.value!r}"
                )
            return float(node.value)

        # ast.Num for Python < 3.8 compat
        if hasattr(ast, "Num") and isinstance(node, ast.Num):
            return float(node.n)

        if isinstance(node, ast.Name):
            name = node.id
            if name not in context:
                raise ValueError(
                    f"Undefined symbol '{name}' in formula"
                )
            return float(context[name])

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in _ALLOWED_BINOPS:
                raise ValueError(
                    f"Disallowed binary operator: {op_type.__name__}"
                )
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            return _ALLOWED_BINOPS[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, ast.USub):
                raise ValueError(
                    f"Disallowed unary operator: {type(node.op).__name__}"
                )
            return -_eval_node(node.operand)

        raise ValueError(f"Disallowed AST node: {type(node).__name__}")

    return float(_eval_node(tree))


# =====================================================================
# Effect Resolution for Structural Measures (P0-2)
# =====================================================================

def _resolve_effects(
    col_meta: dict[str, Any],
    row: dict[str, Any],
    columns: dict[str, dict[str, Any]],
) -> dict[str, float]:
    """Resolve effect values for a structural measure from a single row.

    [P0-2]

    For each effect name in col_meta["effects"], finds the categorical
    column whose value set matches the effect's keys, looks up the
    row's categorical value, and returns the corresponding numeric effect.

    Args:
        col_meta: Structural measure column metadata.
        row: Single-row dict mapping column name -> value.
        columns: Full column registry for categorical value matching.

    Returns:
        Dict mapping effect name -> resolved numeric value.

    Raises:
        ValueError: If effect cannot be resolved.
    """
    effects = col_meta.get("effects", {})
    resolved: dict[str, float] = {}

    for effect_name, val_map in effects.items():
        effect_keys = set(val_map.keys())

        # Find the categorical column whose declared values match effect keys
        matched_col: str | None = None
        for c_name, c_meta in columns.items():
            if c_meta.get("type") != "categorical":
                continue
            if set(c_meta.get("values", [])) == effect_keys:
                matched_col = c_name
                break

        if matched_col is None:
            raise ValueError(
                f"Cannot resolve effect '{effect_name}': no categorical "
                f"column matches keys {sorted(effect_keys)}"
            )

        row_value = row.get(matched_col)
        if row_value is None:
            raise ValueError(
                f"Row missing value for column '{matched_col}' "
                f"needed by effect '{effect_name}'"
            )

        row_value_str = str(row_value)
        if row_value_str not in val_map:
            raise ValueError(
                f"Value '{row_value_str}' not in effect '{effect_name}' map"
            )

        resolved[effect_name] = float(val_map[row_value_str])

    return resolved


# =====================================================================
# Structural Measure Evaluation (P0-2, P3-10)
# =====================================================================

def _eval_structural(
    col_name: str,
    col_meta: dict[str, Any],
    rows: dict[str, np.ndarray],
    rng: np.random.Generator,
    columns: dict[str, dict[str, Any]],
    overrides: dict | None = None,
) -> np.ndarray:
    """Evaluate a structural formula measure for all rows.

    [P0-2, P3-10]

    Per row: resolve effects, build context with effects + other measure
    values, evaluate formula, optionally add noise.

    Args:
        col_name: Column name.
        col_meta: Structural measure metadata (formula, effects, noise).
        rows: Current row arrays (previously generated columns).
        rng: Seeded NumPy generator.
        columns: Full column registry for effect resolution.
        overrides: Optional parameter overrides.

    Returns:
        ndarray of computed values.
    """
    formula = col_meta["formula"]
    noise_config = col_meta.get("noise", {})
    effects_spec = col_meta.get("effects", {})

    # Determine row count
    n_rows = 0
    for v in rows.values():
        n_rows = len(v)
        break
    if n_rows == 0:
        return np.array([], dtype=np.float64)

    # Pre-compute effect column mapping: effect_name -> (cat_col_name, val_map)
    effect_col_map: dict[str, tuple[str, dict[str, float]]] = {}
    for effect_name, val_map in effects_spec.items():
        effect_keys = set(val_map.keys())
        for c_name, c_meta in columns.items():
            if c_meta.get("type") != "categorical":
                continue
            if set(c_meta.get("values", [])) == effect_keys:
                effect_col_map[effect_name] = (c_name, val_map)
                break

    # Extract formula symbols via AST to build minimal per-row context
    tree = ast.parse(formula, mode="eval")
    formula_symbols = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    }
    # Identify which symbols are measure references (not effects)
    measure_symbols = formula_symbols - set(effect_col_map.keys())

    values = np.empty(n_rows, dtype=np.float64)

    for i in range(n_rows):
        context: dict[str, float] = {}

        # Resolve effects from categorical predictor values
        for effect_name, (cat_col, val_map) in effect_col_map.items():
            cat_val = str(rows[cat_col][i])
            context[effect_name] = float(val_map[cat_val])

        # Add referenced measure values (already computed per topo order)
        for sym in measure_symbols:
            if sym in rows:
                context[sym] = float(rows[sym][i])

        try:
            values[i] = _safe_eval_formula(formula, context)
        except ZeroDivisionError:
            zero_vars = sorted(k for k, v in context.items() if v == 0.0)
            raise InvalidParameterError(
                param_name="formula",
                value=0.0,
                reason=(
                    f"Structural measure '{col_name}': formula '{formula}' "
                    f"divided by zero at row {i}. "
                    f"Zero-valued symbols in context: {zero_vars}. "
                    f"Guard against zero in your effects or floor the "
                    f"denominator (e.g., 'a / max(b, 1e-6)')."
                ),
            ) from None

    # Apply noise (P3-10: noise={} means zero noise / deterministic)
    if noise_config:
        sigma = noise_config.get("sigma", 0.0)
        if sigma > 0:
            values = values + rng.normal(0, sigma, size=n_rows)

    return values


# =====================================================================
# Stochastic Measure Sampling (P0-2, P1-1, P3-1)
# =====================================================================

def _validate_distribution_params(
    col_name: str,
    family: str,
    mu: np.ndarray,
    sigma: np.ndarray,
) -> None:
    """Per-family pre-call validation of per-row distribution parameters.

    Converts the bare numpy errors that would otherwise surface (e.g.
    ``ValueError: a <= 0`` from ``rng.beta(0, ...)``) into a structured
    ``InvalidParameterError`` carrying the column name, family, offending
    parameter, first bad row, and a concrete fix hint. The sandbox retry
    loop feeds this straight to the LLM via ``format_error_feedback()``.

    Only covers conditions not already handled by the per-param clamp in
    ``_compute_per_row_params`` (which floors ``sigma`` / ``scale`` / ``rate``
    to ``1e-6``). That clamp makes sigma-based guards redundant for beta,
    gamma, and lognormal; what remains is the ``mu`` axis those distributions
    use as their first positional parameter.
    """
    if family in ("beta", "gamma"):
        bad = np.where(mu <= 0)[0]
        if len(bad) > 0:
            raise InvalidParameterError(
                param_name="mu",
                value=float(mu[bad[0]]),
                reason=(
                    f"Measure '{col_name}' (family='{family}'): parameter "
                    f"'mu' must be > 0 for all rows, got {float(mu[bad[0]])} "
                    f"at row {int(bad[0])}. Raise the intercept or effect "
                    f"values so every row has a positive mu."
                ),
            )
    elif family == "poisson":
        bad = np.where(mu < 0)[0]
        if len(bad) > 0:
            raise InvalidParameterError(
                param_name="mu",
                value=float(mu[bad[0]]),
                reason=(
                    f"Measure '{col_name}' (family='poisson'): parameter "
                    f"'mu' must be >= 0, got {float(mu[bad[0]])} at row "
                    f"{int(bad[0])}."
                ),
            )


def _sample_stochastic(
    col_name: str,
    col_meta: dict[str, Any],
    rows: dict[str, np.ndarray],
    rng: np.random.Generator,
    overrides: dict | None = None,
) -> np.ndarray:
    """Sample from a stochastic distribution for all rows.

    [P0-2, P1-1, P3-1]

    Computes per-row parameters from param_model (intercept + effects),
    clamps to valid ranges (P3-1), then dispatches to the appropriate
    numpy random generator by family.

    Args:
        col_name: Column name.
        col_meta: Stochastic measure metadata (family, param_model).
        rows: Current row arrays.
        rng: Seeded NumPy generator.
        overrides: Optional parameter overrides (P0-3).

    Returns:
        ndarray of sampled values.

    Raises:
        NotImplementedError: For mixture family (P1-1).
        ValueError: For unknown families.
    """
    family = col_meta.get("family", "")

    # TODO [M1-NC-1 / P1-1]: mixture distribution sampling deferred.
    if family == "mixture":
        raise NotImplementedError(
            "mixture distribution sampling not yet implemented. "
            "Expected param_model schema: {'components': [{'family': str, "
            "'weight': float, 'params': {...}}, ...]}"
        )

    # Determine row count
    n_rows = 0
    for v in rows.values():
        n_rows = len(v)
        break
    if n_rows == 0:
        return np.array([], dtype=np.float64)

    params = _compute_per_row_params(
        col_name, col_meta, rows, n_rows, overrides,
    )

    mu = params.get("mu", np.zeros(n_rows))
    sigma = params.get("sigma", np.ones(n_rows))

    # Raise structured errors with column/family/param/row context BEFORE
    # numpy would raise its own bare message (e.g. "a <= 0" for beta).
    _validate_distribution_params(col_name, family, mu, sigma)

    if family == "gaussian":
        return rng.normal(mu, sigma)
    elif family == "lognormal":
        return rng.lognormal(mu, sigma)
    elif family == "gamma":
        return rng.gamma(shape=mu, scale=sigma)
    elif family == "beta":
        return rng.beta(mu, sigma)
    elif family == "uniform":
        return rng.uniform(mu, sigma)
    elif family == "poisson":
        return rng.poisson(mu).astype(np.float64)
    elif family == "exponential":
        rate = np.maximum(mu, 1e-6)
        return rng.exponential(1.0 / rate)
    else:
        raise ValueError(f"Unknown distribution family: '{family}'")


def _compute_per_row_params(
    col_name: str,
    col_meta: dict[str, Any],
    rows: dict[str, np.ndarray],
    n_rows: int,
    overrides: dict | None = None,
) -> dict[str, np.ndarray]:
    """Compute per-row distribution parameters from param_model.

    [P0-2, P3-1]

    For each param key, computes theta = intercept + sum(effects) per row.
    Applies overrides if present (P0-3). Clamps to valid ranges (P3-1).

    Args:
        col_name: Column name (for logging).
        col_meta: Measure metadata with param_model.
        rows: Current row arrays.
        n_rows: Number of rows.
        overrides: Optional parameter overrides.

    Returns:
        Dict mapping param_key -> ndarray of per-row values.
    """
    param_model = col_meta.get("param_model", {})
    col_overrides: dict[str, Any] = {}
    if overrides:
        col_overrides = overrides.get("measures", {}).get(col_name, {})

    params: dict[str, np.ndarray] = {}

    for param_key, value in param_model.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            theta = np.full(n_rows, float(value))
        elif isinstance(value, dict):
            intercept = float(value.get("intercept", 0.0))
            theta = np.full(n_rows, intercept)

            for effect_col, effect_map in value.get("effects", {}).items():
                if effect_col not in rows:
                    continue
                cat_values = rows[effect_col]
                for cat_val, effect_num in effect_map.items():
                    mask = cat_values == cat_val
                    theta[mask] += float(effect_num)
        else:
            theta = np.zeros(n_rows)

        # Apply overrides (P0-3): multiplicative factor preserving per-row variation
        if param_key in col_overrides:
            theta *= float(col_overrides[param_key])

        # Clamp to valid ranges (P3-1)
        if param_key in ("sigma", "scale"):
            original = theta.copy()
            theta = np.maximum(theta, 1e-6)
            n_clamped = int((theta != original).sum())
            if n_clamped > 0:
                logger.warning(
                    "Clamped %s.%s: %d values clamped to 1e-6.",
                    col_name, param_key, n_clamped,
                )
        elif param_key == "rate":
            theta = np.maximum(theta, 1e-6)

        params[param_key] = theta

    return params


# =====================================================================
# Top-Level Measure Generation Orchestrator (P0-2)
# =====================================================================

def generate_measures(
    columns: dict[str, dict[str, Any]],
    topo_order: list[str],
    rows: dict[str, np.ndarray],
    rng: np.random.Generator,
    overrides: dict | None = None,
) -> dict[str, np.ndarray]:
    """Generate measure columns in topological order.

    [P0-2]

    Iterates topo_order, dispatches to _sample_stochastic or
    _eval_structural based on measure_type, stores results in rows.

    Args:
        columns: Column registry.
        topo_order: Full topological order (all columns).
        rows: Current row dict (mutated in place for measures).
        rng: Seeded NumPy generator.
        overrides: Optional parameter overrides for Loop B.

    Returns:
        Updated rows dict with measure columns populated.
    """
    for col_name in topo_order:
        col_meta = columns.get(col_name)
        if col_meta is None or col_meta.get("type") != "measure":
            continue

        measure_type = col_meta.get("measure_type")

        if measure_type == "stochastic":
            rows[col_name] = _sample_stochastic(
                col_name, col_meta, rows, rng, overrides,
            )
        elif measure_type == "structural":
            rows[col_name] = _eval_structural(
                col_name, col_meta, rows, rng, columns, overrides,
            )

        logger.debug(
            "generate_measures: generated '%s' (%s).",
            col_name, measure_type,
        )

    # Handle reshuffle overrides (P0-3)
    if overrides and "reshuffle" in overrides:
        for col_name in overrides["reshuffle"]:
            if col_name in rows:
                rows[col_name] = rng.permutation(rows[col_name])

    return rows
