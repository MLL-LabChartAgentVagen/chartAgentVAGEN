"""
Group-level validators.

Currently a small module: the temporal group name constant ([A10]) and
the weight dict normalizer used by add_group_dependency.
"""
from __future__ import annotations


# [A10] The temporal group is auto-named "time"
TEMPORAL_GROUP_NAME: str = "time"


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
