"""
param_model validators for stochastic measure declarations.

Covers:
  - Per-family param key contract (mu/sigma whitelist).
  - Constant-parameter and intercept+effects forms.
  - Mixture (IS-1) component schema with recursive component validation.
  - Effects validation against the categorical column registry.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from ..exceptions import (
    InvalidParameterError,
    UndefinedEffectError,
)
from ._validate_basic import SUPPORTED_FAMILIES, TEMPORAL_DERIVE_NAMES


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
    # Mixture (IS-1): validate the {"components": [...]} schema; recursively
    # validate each component's param_model under its own family. Returns
    # before the per-key validate_param_value loop, since "components" does
    # not match the constant/intercept+effects shape that loop expects.
    if family == "mixture":
        components = param_model.get("components")
        if not isinstance(components, list) or len(components) == 0:
            raise InvalidParameterError(
                param_name="components",
                value=0.0,
                reason=(
                    f"mixture measure '{name}' requires a non-empty 'components' "
                    f"list. Schema: {{'components': [{{'family': str, "
                    f"'weight': float, 'param_model': {{...}}}}, ...]}}."
                ),
            )
        non_mixture_families = sorted(SUPPORTED_FAMILIES - {"mixture"})
        for i, comp in enumerate(components):
            if not isinstance(comp, dict):
                raise InvalidParameterError(
                    param_name=f"components[{i}]",
                    value=0.0,
                    reason=(
                        f"mixture component must be a dict, "
                        f"got {type(comp).__name__}"
                    ),
                )
            cf = comp.get("family")
            if cf not in SUPPORTED_FAMILIES or cf == "mixture":
                raise InvalidParameterError(
                    param_name=f"components[{i}].family",
                    value=0.0,
                    reason=(
                        f"mixture component family '{cf}' is invalid. "
                        f"Must be one of {non_mixture_families}. "
                        f"Nested mixtures are not supported."
                    ),
                )
            w = comp.get("weight")
            if isinstance(w, bool) or not isinstance(
                w, (int, float, np.floating, np.integer)
            ):
                raise InvalidParameterError(
                    param_name=f"components[{i}].weight",
                    value=0.0,
                    reason=(
                        f"mixture component weight must be a number, "
                        f"got {type(w).__name__}"
                    ),
                )
            if float(w) <= 0:
                raise InvalidParameterError(
                    param_name=f"components[{i}].weight",
                    value=float(w),
                    reason="mixture component weight must be strictly positive",
                )
            sub_pm = comp.get("param_model")
            if not isinstance(sub_pm, dict):
                raise InvalidParameterError(
                    param_name=f"components[{i}].param_model",
                    value=0.0,
                    reason="mixture component param_model must be a dict",
                )
            validate_param_model(f"{name}.components[{i}]", cf, sub_pm, columns)
        return

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
