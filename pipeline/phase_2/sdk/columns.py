"""
SDK column declaration functions.

These functions implement the declaration API (add_category, add_temporal,
add_measure, add_measure_structural) as standalone functions that accept
explicit store parameters. The FactTableSimulator class forwards to these
via thin delegation methods.

Implements: §2.1.1
"""
from __future__ import annotations

import logging
import re
from collections import OrderedDict
from datetime import date
from typing import Any, Optional

from ..exceptions import (
    CyclicDependencyError,
    DuplicateColumnError,
    DuplicateGroupRootError,
    EmptyValuesError,
    InvalidParameterError,
    NonRootDependencyError,
    ParentNotFoundError,
    UndefinedEffectError,
    WeightLengthMismatchError,
)
from ..types import DimensionGroup
from . import validation as _val
from . import dag as _dag
from . import groups as _groups

logger = logging.getLogger(__name__)


def add_category(
    columns: OrderedDict[str, dict[str, Any]],
    groups: dict[str, DimensionGroup],
    name: str,
    values: list[str],
    weights: list[float] | dict[str, list[float]],
    group: str,
    parent: Optional[str] = None,
) -> None:
    """Declare a categorical column.

    [Subtask 1.2.1–1.2.3]

    Validates inputs, normalizes weights, and registers the column
    in both the column registry and group registry.

    Args:
        columns: Column registry (mutated in place).
        groups: Group registry (mutated in place).
        name: Column name (must be unique).
        values: List of categorical values (non-empty).
        weights: Flat list or per-parent dict of weights.
        group: Dimension group name.
        parent: Parent column name (same group), or None for root.
    """
    # Validate column name uniqueness
    _val.validate_column_name(name, columns)

    # Validate non-empty values
    if not values or len(values) == 0:
        raise EmptyValuesError(column_name=name)

    # Validate parent if specified
    is_root = parent is None
    if parent is not None:
        _val.validate_parent(parent, group, columns)

    # Validate/normalize weights
    if isinstance(weights, dict):
        if parent is None:
            raise ValueError(
                f"Per-parent weight dict provided for root column '{name}'. "
                f"Root columns must use flat weight lists."
            )
        normalized_weights = _val.validate_and_normalize_dict_weights(
            name, values, weights, parent, columns,
        )
    else:
        normalized_weights = _val.validate_and_normalize_flat_weights(
            name, values, list(weights),
        )

    # Check temporal group name conflict
    if group == _val.TEMPORAL_GROUP_NAME:
        raise ValueError(
            f"Group name '{_val.TEMPORAL_GROUP_NAME}' is reserved for "
            f"temporal columns. Use a different group name."
        )

    # Check for duplicate root in group
    if is_root and group in groups and groups[group].root:
        raise DuplicateGroupRootError(
            group_name=group,
            existing_root=groups[group].root,
            attempted_root=name,
        )

    # Register the column
    col_meta: dict[str, Any] = {
        "type": "categorical",
        "values": list(values),
        "weights": normalized_weights,
        "group": group,
        "parent": parent,
    }
    columns[name] = col_meta

    # Register in group
    _groups.register_categorical_column(groups, group, name, is_root)

    logger.debug(
        "add_category: '%s' registered in group '%s' (parent=%s).",
        name, group, parent,
    )


def add_temporal(
    columns: OrderedDict[str, dict[str, Any]],
    groups: dict[str, DimensionGroup],
    name: str,
    start: str,
    end: str,
    freq: str,
    derive: Optional[list[str]] = None,
) -> None:
    """Declare a temporal column with optional derived features.

    [Subtask 1.3.1–1.3.4]

    Args:
        columns: Column registry (mutated in place).
        groups: Group registry (mutated in place).
        name: Root temporal column name.
        start: ISO-8601 start date string.
        end: ISO-8601 end date string.
        freq: Frequency string ("D", "W-MON"..."W-SUN", "MS").
        derive: List of derived features to create.
    """
    if derive is None:
        derive = []

    # Validate column name uniqueness
    _val.validate_column_name(name, columns)

    # Parse dates
    start_date = _parse_iso_date(start, "start")
    end_date = _parse_iso_date(end, "end")

    if start_date >= end_date:
        raise ValueError(
            f"Temporal column '{name}': start ({start}) must be before end ({end})."
        )

    # Validate derive list
    invalid_derive = set(derive) - _val.TEMPORAL_DERIVE_WHITELIST
    if invalid_derive:
        raise ValueError(
            f"Invalid derive features {sorted(invalid_derive)} for column '{name}'. "
            f"Supported: {sorted(_val.TEMPORAL_DERIVE_WHITELIST)}"
        )

    # Validate freq
    valid_freqs = {"D"} | {f"W-{d}" for d in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]} | {"MS"}
    if freq not in valid_freqs:
        raise ValueError(
            f"Unsupported freq '{freq}' for temporal column '{name}'. "
            f"Supported: {sorted(valid_freqs)}"
        )

    # Register root temporal column
    col_meta: dict[str, Any] = {
        "type": "temporal",
        "start": start,
        "end": end,
        "freq": freq,
        "derive": list(derive),
        "group": _val.TEMPORAL_GROUP_NAME,
        "parent": None,
    }
    columns[name] = col_meta

    # Register derived columns
    derived_col_names: list[str] = []
    for d in derive:
        derived_name = f"{name}_{d}"
        _val.validate_column_name(derived_name, columns)
        columns[derived_name] = {
            "type": "temporal_derived",
            "derivation": d,
            "source": name,
            "group": _val.TEMPORAL_GROUP_NAME,
            "parent": None,
        }
        derived_col_names.append(derived_name)

    # Register temporal group
    _groups.register_temporal_group(
        groups, _val.TEMPORAL_GROUP_NAME, name, derived_col_names,
    )

    logger.debug(
        "add_temporal: '%s' registered with freq='%s', derive=%s.",
        name, freq, derive,
    )


def add_measure(
    columns: OrderedDict[str, dict[str, Any]],
    name: str,
    family: str,
    param_model: dict[str, Any],
    scale: Optional[float] = None,
) -> None:
    """Declare a stochastic measure column.

    [Subtask 1.4.1–1.4.3]

    Args:
        columns: Column registry (mutated in place).
        name: Measure column name.
        family: Distribution family string.
        param_model: Distribution parameters dict.
        scale: Optional scale factor (stored, not yet used).
    """
    _val.validate_column_name(name, columns)
    _val.validate_family(family)
    _val.validate_param_model(name, family, param_model, columns)

    col_meta: dict[str, Any] = {
        "type": "measure",
        "measure_type": "stochastic",
        "family": family,
        "param_model": dict(param_model),
    }
    if scale is not None:
        col_meta["scale"] = scale
        logger.warning(
            "add_measure: 'scale' parameter (%.4f) for '%s' is stored but "
            "has no effect in the current implementation.",
            scale, name,
        )

    columns[name] = col_meta

    logger.debug(
        "add_measure: stochastic '%s' (family='%s') registered.",
        name, family,
    )


def add_measure_structural(
    columns: OrderedDict[str, dict[str, Any]],
    measure_dag: dict[str, list[str]],
    name: str,
    formula: str,
    effects: Optional[dict[str, dict[str, float]]] = None,
    noise: Optional[dict[str, Any]] = None,
) -> None:
    """Declare a structural measure column (formula-based).

    [Subtask 1.5.1–1.5.5]

    Args:
        columns: Column registry (mutated in place).
        measure_dag: Measure DAG (mutated in place).
        name: Measure column name.
        formula: Arithmetic formula string.
        effects: Optional effects dict.
        noise: Optional noise configuration dict.
    """
    if effects is None:
        effects = {}
    if noise is None:
        noise = {}

    _val.validate_column_name(name, columns)

    # Validate formula symbols resolve to declared measures or effects
    formula_symbols = _val.extract_formula_symbols(formula)
    effect_names = set(effects.keys())
    measure_deps: list[str] = []

    for sym in formula_symbols:
        if sym in effect_names:
            continue
        if sym in columns and columns[sym].get("type") == "measure":
            measure_deps.append(sym)
            continue
        # Might be a numeric-related keyword or operator — skip silently
        # The formula evaluator will catch truly invalid symbols at runtime

    # Validate effects if present
    if effects:
        _val.validate_structural_effects(name, formula, effects, columns)

    # Check measure DAG acyclicity
    if measure_deps:
        _dag.check_measure_dag_acyclic(measure_dag, name, measure_deps)

    # Register the column
    col_meta: dict[str, Any] = {
        "type": "measure",
        "measure_type": "structural",
        "formula": formula,
        "effects": dict(effects),
        "noise": dict(noise),
    }
    columns[name] = col_meta

    # Update measure DAG
    measure_dag.setdefault(name, [])
    for dep in measure_deps:
        measure_dag.setdefault(dep, [])
        measure_dag[dep].append(name)

    logger.debug(
        "add_measure_structural: '%s' registered (depends_on=%s).",
        name, measure_deps,
    )


def _parse_iso_date(date_str: str, field_name: str) -> date:
    """Parse an ISO-8601 date string to a datetime.date object.

    [Subtask 1.3.1]

    Args:
        date_str: ISO-8601 date string (e.g. "2024-01-01").
        field_name: Field name for error messages ("start" or "end").

    Returns:
        Parsed date object.

    Raises:
        ValueError: If the string is not a valid ISO-8601 date.
    """
    try:
        return date.fromisoformat(date_str)
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"Cannot parse '{field_name}' as ISO-8601 date: "
            f"'{date_str}'. Expected format: YYYY-MM-DD."
        ) from exc
