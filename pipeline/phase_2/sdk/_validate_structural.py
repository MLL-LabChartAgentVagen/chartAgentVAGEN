"""
Structural measure effects validator.

Validates the effects dict of a structural measure declaration: every
effect name must appear as a symbol in the formula, and the inner dict
keys must match the values of some declared categorical column.
"""
from __future__ import annotations

from typing import Any

from ..exceptions import UndefinedEffectError
from ._validate_basic import extract_formula_symbols


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
