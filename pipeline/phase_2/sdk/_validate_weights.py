"""
Weight validators for categorical column declarations.

Covers flat per-value weights and per-parent conditional weight dicts.
The dict form delegates to the flat form internally.
"""
from __future__ import annotations

from typing import Any

from ..exceptions import WeightLengthMismatchError


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
