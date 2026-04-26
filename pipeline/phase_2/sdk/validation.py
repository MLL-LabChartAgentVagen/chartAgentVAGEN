"""
SDK declaration-time validation rules.

Consolidated validation functions extracted from FactTableSimulator.
All functions are stateless — they accept explicit parameters.

Implements: §2.1.1, §2.1.2 validation rules
"""
from __future__ import annotations

import logging
import re
from typing import Any

from ..exceptions import (
    DuplicateColumnError,
    EmptyValuesError,
    InvalidParameterError,
    ParentNotFoundError,
    UndefinedEffectError,
    WeightLengthMismatchError,
)

logger = logging.getLogger(__name__)


# ===== Module-Level Constants =====

# §2.1.1: Supported distribution family whitelist
SUPPORTED_FAMILIES: frozenset[str] = frozenset({
    "gaussian", "lognormal", "gamma", "beta",
    "uniform", "poisson", "exponential", "mixture",
})

# Temporal derive feature names — used to hint the LLM when a formula
# references a derived feature before the temporal column declared it.
TEMPORAL_DERIVE_NAMES: frozenset[str] = frozenset({
    "day_of_week", "is_weekend", "month", "quarter",
})

# Param-model key contract per family. The engine's _sample_stochastic
# (engine/measures.py) reads only `mu`/`sigma` (or just `mu` for poisson and
# exponential); every other key is silently dropped. We enforce both
# required-presence and unknown-key rejection at declaration time so that
# misnamed keys (e.g. Beta with alpha/beta) fail loudly here instead of
# producing the misleading "mu == 0.0" error during sampling.
# Mixture (IS-1) is intentionally absent — its param_model schema is unspecified.
VALIDATED_PARAM_KEYS: dict[str, frozenset[str]] = {
    "gaussian":    frozenset({"mu", "sigma"}),
    "lognormal":   frozenset({"mu", "sigma"}),
    "gamma":       frozenset({"mu", "sigma"}),
    "beta":        frozenset({"mu", "sigma"}),
    "uniform":     frozenset({"mu", "sigma"}),
    "poisson":     frozenset({"mu"}),
    "exponential": frozenset({"mu"}),
}

# §2.1.1 whitelist: "Derived columns (day_of_week, month, quarter, is_weekend)"
TEMPORAL_DERIVE_WHITELIST: frozenset[str] = frozenset(
    {"day_of_week", "month", "quarter", "is_weekend"}
)

# [A10] The temporal group is auto-named "time"
TEMPORAL_GROUP_NAME: str = "time"

# Regex pattern for extracting identifier symbols from arithmetic formulas.
IDENTIFIER_RE: re.Pattern[str] = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


# =====================================================================
# Column Name Validation
# =====================================================================

def validate_column_name(
    name: str,
    columns: dict[str, dict[str, Any]],
) -> None:
    """Ensure column name is unique in the registry.

    Args:
        name: Column name to validate.
        columns: Current column registry.

    Raises:
        DuplicateColumnError: If name already exists in columns.
    """
    if name in columns:
        raise DuplicateColumnError(column_name=name)


# =====================================================================
# Parent Validation
# =====================================================================

def validate_parent(
    parent: str,
    group: str,
    columns: dict[str, dict[str, Any]],
) -> None:
    """Validate that parent exists and belongs to the same group.

    Args:
        parent: Parent column name.
        group: Expected group name.
        columns: Column registry.

    Raises:
        ParentNotFoundError: If parent not found or wrong group.
    """
    if parent not in columns:
        raise ParentNotFoundError(
            child_name="(new column)",
            parent_name=parent,
            group=group,
        )
    parent_group = columns[parent].get("group")
    if parent_group != group:
        raise ParentNotFoundError(
            child_name="(new column)",
            parent_name=parent,
            group=group,
        )


# =====================================================================
# Weight Validation & Normalization
# =====================================================================

def validate_and_normalize_flat_weights(
    column_name: str,
    values: list[str],
    weights: list[float],
) -> list[float]:
    """Validate a flat weight list and return normalized weights.

    [Subtask 1.2.1, 1.2.2]

    Checks length match, rejects negatives and all-zero vectors, then
    normalizes so weights sum to 1.0 (§2.1.1 "Auto-normalized").

    Args:
        column_name: Column name for error messages.
        values: The categorical values list (for length comparison).
        weights: Raw weight list to validate and normalize.

    Returns:
        Normalized weight list summing to 1.0.

    Raises:
        WeightLengthMismatchError: If len(weights) != len(values).
        ValueError: If any weight is negative.
        ValueError: If all weights are zero (non-normalizable).
    """
    if len(weights) != len(values):
        raise WeightLengthMismatchError(
            column_name=column_name,
            n_values=len(values),
            n_weights=len(weights),
        )

    for i, w in enumerate(weights):
        if not isinstance(w, (int, float)):
            raise TypeError(
                f"Weight at index {i} for column '{column_name}' "
                f"must be numeric, got {type(w).__name__}."
            )
        if w < 0:
            raise ValueError(
                f"Weight at index {i} for column '{column_name}' "
                f"is negative ({w}). Weights must be >= 0."
            )

    total = sum(weights)
    if total == 0:
        raise ValueError(
            f"All weights for column '{column_name}' are zero. "
            f"At least one weight must be positive for normalization."
        )

    return [w / total for w in weights]


def validate_and_normalize_dict_weights(
    column_name: str,
    values: list[str],
    weights: dict[str, list[float]],
    parent: str,
    columns: dict[str, dict[str, Any]],
) -> dict[str, list[float]]:
    """Validate per-parent conditional weight dict and return normalized form.

    [Subtask 1.2.3]

    Each key must be a value of the parent column. Each vector must
    have the same length as `values`. Each vector is independently
    normalized. All parent values must appear as keys ([A6]).

    Args:
        column_name: Column name for error messages.
        values: The child categorical values list.
        weights: Dict mapping parent value -> weight vector.
        parent: Parent column name (must already be in columns).
        columns: Column registry.

    Returns:
        Dict with same keys, each vector normalized to sum to 1.0.
    """
    if len(weights) == 0:
        raise ValueError(
            f"Per-parent weight dict for column '{column_name}' is empty. "
            f"Must contain one entry per parent value."
        )

    parent_values = set(columns[parent]["values"])

    provided_keys = set(weights.keys())
    missing_keys = parent_values - provided_keys
    if missing_keys:
        raise ValueError(
            f"Per-parent weight dict for column '{column_name}' is "
            f"missing keys for parent values: {sorted(missing_keys)}. "
            f"All parent values must be present ([A6])."
        )

    extra_keys = provided_keys - parent_values
    if extra_keys:
        raise ValueError(
            f"Per-parent weight dict for column '{column_name}' contains "
            f"keys not in parent '{parent}' values: {sorted(extra_keys)}."
        )

    normalized: dict[str, list[float]] = {}
    for parent_val, vec in weights.items():
        normalized[parent_val] = validate_and_normalize_flat_weights(
            column_name=f"{column_name}[{parent_val}]",
            values=values,
            weights=vec,
        )

    return normalized


def normalize_weight_dict_values(
    label: str,
    weights: dict[str, float],
) -> dict[str, float]:
    """Normalize a {value: weight} dict so values sum to 1.0.

    [Subtask 1.7.2 helper]

    Used by add_group_dependency to normalize conditional weight rows.
    Rejects negative weights and all-zero vectors.

    Args:
        label: Descriptive label for error messages.
        weights: Mapping of categorical values to numeric weights.

    Returns:
        New dict with the same keys, values normalized to sum to 1.0.
    """
    for key, w in weights.items():
        if not isinstance(w, (int, float)):
            raise TypeError(
                f"{label}: weight for '{key}' must be numeric, "
                f"got {type(w).__name__}."
            )
        if isinstance(w, bool):
            raise TypeError(
                f"{label}: weight for '{key}' must be numeric, got bool."
            )
        if w < 0:
            raise ValueError(
                f"{label}: weight for '{key}' is negative ({w}). "
                f"Weights must be >= 0."
            )

    total = sum(weights.values())
    if total == 0:
        raise ValueError(
            f"{label}: all weights are zero. At least one weight "
            f"must be positive for normalization."
        )

    return {k: v / total for k, v in weights.items()}


# =====================================================================
# Family Validation
# =====================================================================

def validate_family(family: str) -> None:
    """Check that family is in the supported whitelist.

    Args:
        family: Distribution family name.

    Raises:
        ValueError: If family is not supported.
    """
    if family not in SUPPORTED_FAMILIES:
        raise ValueError(
            f"Unsupported distribution family '{family}'. "
            f"Supported: {sorted(SUPPORTED_FAMILIES)}"
        )


# =====================================================================
# param_model Validation
# =====================================================================

def validate_param_model(
    name: str,
    family: str,
    param_model: dict[str, Any],
    columns: dict[str, dict[str, Any]],
) -> None:
    """Validate param_model for a stochastic measure.

    [Subtask 1.4.2]

    Dispatches between constant-parameter and intercept+effects forms.

    Args:
        name: Measure name for error messages.
        family: Distribution family.
        param_model: The param_model dict.
        columns: Column registry for effects validation.
    """
    if family in VALIDATED_PARAM_KEYS:
        allowed = VALIDATED_PARAM_KEYS[family]
        # Unknown-key check fires before missing-required so that a misnamed-
        # key case like {"alpha","beta"} for Beta produces the most actionable
        # message ("alpha not recognized; expected mu, sigma") rather than
        # "mu and sigma missing" (which doesn't tell the LLM to drop alpha/beta).
        unknown = sorted(set(param_model.keys()) - allowed)
        if unknown:
            raise InvalidParameterError(
                param_name=unknown[0],
                value=0.0,
                reason=(
                    f"unrecognized param key '{unknown[0]}' for family "
                    f"'{family}'. Expected keys: {sorted(allowed)}. "
                    f"Common confusion: Beta uses mu/sigma, not alpha/beta."
                ),
            )
        missing = allowed - set(param_model.keys())
        if missing:
            raise InvalidParameterError(
                param_name=sorted(missing)[0],
                value=0.0,
                reason=(
                    f"required param key(s) {sorted(missing)} missing "
                    f"for family '{family}'"
                ),
            )

    for key, value in param_model.items():
        validate_param_value(name, family, key, value, columns)


def validate_param_value(
    measure_name: str,
    family: str,
    param_key: str,
    value: Any,
    columns: dict[str, dict[str, Any]],
) -> None:
    """Validate a single param_model value (constant or intercept+effects).

    [Subtask 1.4.2 helper]

    A value is valid if it is:
      (a) A numeric scalar (int or float, not bool)
      (b) A dict with "intercept" (numeric) and optional "effects" (dict)
    """
    # Case A: Numeric Scalar
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return

    # Case B: Intercept+Effects Dict
    if isinstance(value, dict):
        if "intercept" not in value:
            if family in VALIDATED_PARAM_KEYS:
                raise InvalidParameterError(
                    param_name=param_key,
                    value=0.0,
                    reason=(
                        f"intercept+effects dict for '{param_key}' "
                        f"must contain 'intercept' key"
                    ),
                )
            return

        intercept = value["intercept"]
        if not isinstance(intercept, (int, float)) or isinstance(
            intercept, bool
        ):
            if family in VALIDATED_PARAM_KEYS:
                raise InvalidParameterError(
                    param_name=f"{param_key}.intercept",
                    value=0.0,
                    reason="intercept must be a numeric scalar",
                )
            return

        if "effects" in value:
            effects = value["effects"]
            if not isinstance(effects, dict):
                if family in VALIDATED_PARAM_KEYS:
                    raise InvalidParameterError(
                        param_name=f"{param_key}.effects",
                        value=0.0,
                        reason="effects must be a dict",
                    )
                return

            validate_effects_in_param(
                measure_name, param_key, effects, columns
            )
        return

    # Case C: Invalid Type
    if family in VALIDATED_PARAM_KEYS:
        raise InvalidParameterError(
            param_name=param_key,
            value=0.0,
            reason=(
                f"value must be a numeric scalar or an "
                f"intercept+effects dict, got {type(value).__name__}"
            ),
        )


def validate_effects_in_param(
    measure_name: str,
    param_key: str,
    effects: dict[str, dict[str, float]],
    columns: dict[str, dict[str, Any]],
) -> None:
    """Validate effects within a param_model intercept+effects form.

    [Subtask 1.4.2 helper]

    Each key in effects must be a declared categorical column name.
    Each inner dict's keys must match that column's value set exactly.

    Raises:
        UndefinedEffectError: Column not declared or value key missing.
    """
    for col_name, val_map in effects.items():
        if col_name not in columns:
            hint = ""
            if col_name in TEMPORAL_DERIVE_NAMES:
                hint = (
                    f" (hint: '{col_name}' is a temporal derive feature — "
                    f"declare it on the temporal column with "
                    f"`add_temporal(..., derive=['{col_name}'])` before "
                    f"referencing it in a formula)"
                )
            raise UndefinedEffectError(
                effect_name=col_name,
                missing_value=f"(column not declared){hint}",
            )

        col_meta = columns[col_name]
        if col_meta.get("type") != "categorical":
            raise UndefinedEffectError(
                effect_name=col_name,
                missing_value=(
                    f"(column '{col_name}' is type "
                    f"'{col_meta.get('type')}', not categorical)"
                ),
            )

        if not isinstance(val_map, dict):
            raise UndefinedEffectError(
                effect_name=col_name,
                missing_value="(effect values must be a dict)",
            )

        declared_values = set(col_meta["values"])
        provided_values = set(val_map.keys())
        missing_values = declared_values - provided_values
        if missing_values:
            first_missing = sorted(missing_values)[0]
            raise UndefinedEffectError(
                effect_name=col_name,
                missing_value=first_missing,
            )

        extra_values = provided_values - declared_values
        if extra_values:
            first_extra = sorted(extra_values)[0]
            raise UndefinedEffectError(
                effect_name=col_name,
                missing_value=(
                    f"('{first_extra}' is not a value of column "
                    f"'{col_name}')"
                ),
            )


# =====================================================================
# Structural Effects Validation
# =====================================================================

def validate_structural_effects(
    measure_name: str,
    formula: str,
    effects: dict[str, dict[str, float]],
    columns: dict[str, dict[str, Any]],
) -> None:
    """Validate the effects dict of a structural measure declaration.

    [Subtask 1.5.3]

    Each effect name must appear as a symbol in the formula.
    Inner dict keys must match the values of some declared categorical column.

    Raises:
        UndefinedEffectError: Effect name not in formula; or inner keys
                              don't match any declared categorical column.
    """
    formula_symbols = extract_formula_symbols(formula)

    for effect_name, val_map in effects.items():
        # Check 1: Effect name must appear in formula
        if effect_name not in formula_symbols:
            raise UndefinedEffectError(
                effect_name=effect_name,
                missing_value="(effect name not found in formula)",
            )

        # Check 2: Inner dict must be a non-empty dict
        if not isinstance(val_map, dict) or len(val_map) == 0:
            raise UndefinedEffectError(
                effect_name=effect_name,
                missing_value=(
                    "(effect values must be a non-empty dict of "
                    "categorical_value -> numeric)"
                ),
            )

        # Check 3: Inner keys must match some categorical column
        inner_keys = set(val_map.keys())
        matched_column: str | None = None

        for col_name, col_meta in columns.items():
            if col_meta.get("type") != "categorical":
                continue
            col_values = set(col_meta["values"])
            if col_values == inner_keys:
                matched_column = col_name
                break

        if matched_column is not None:
            continue

        # No exact match — find closest for error message
        best_col: str | None = None
        best_overlap = 0
        best_missing: set[str] = set()

        for col_name, col_meta in columns.items():
            if col_meta.get("type") != "categorical":
                continue
            col_values = set(col_meta["values"])
            overlap = len(col_values & inner_keys)
            if overlap > best_overlap:
                best_overlap = overlap
                best_col = col_name
                best_missing = col_values - inner_keys

        if best_col is not None and best_missing:
            first_missing = sorted(best_missing)[0]
            raise UndefinedEffectError(
                effect_name=effect_name,
                missing_value=first_missing,
            )

        raise UndefinedEffectError(
            effect_name=effect_name,
            missing_value=(
                f"(inner keys {sorted(inner_keys)} do not match any "
                f"declared categorical column's values)"
            ),
        )


# =====================================================================
# Formula Symbol Extraction
# =====================================================================

def extract_formula_symbols(formula: str) -> set[str]:
    """Extract identifier symbols from an arithmetic formula string.

    [Subtask 1.5.1 helper]

    Returns all tokens matching [a-zA-Z_][a-zA-Z0-9_]*.
    """
    return set(IDENTIFIER_RE.findall(formula))


# =====================================================================
# Root-Only Validation
# =====================================================================

def validate_root_only(
    col_name: str,
    columns: dict[str, dict[str, Any]],
) -> None:
    """Check that a column is a root (parent=None).

    Args:
        col_name: Column name to check.
        columns: Column registry.

    Raises:
        ValueError: If the column has a parent (is not a root).
    """
    if col_name not in columns:
        raise ValueError(f"Column '{col_name}' not found in registry.")
    if columns[col_name].get("parent") is not None:
        from ..exceptions import NonRootDependencyError
        raise NonRootDependencyError(column_name=col_name)
