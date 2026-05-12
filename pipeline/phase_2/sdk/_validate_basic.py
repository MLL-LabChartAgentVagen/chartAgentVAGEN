"""
Basic SDK validators: column name, parent, family, formula symbols.

Stateless leaf module — imported by other _validate_*.py topic modules
and re-exported by sdk/validation.py.
"""
from __future__ import annotations

import re
from typing import Any

from ..exceptions import (
    DuplicateColumnError,
    ParentNotFoundError,
)


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

# Regex pattern for extracting identifier symbols from arithmetic formulas.
IDENTIFIER_RE: re.Pattern[str] = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


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


def extract_formula_symbols(formula: str) -> set[str]:
    """Extract identifier symbols from an arithmetic formula string.

    [Subtask 1.5.1 helper]

    Returns all tokens matching [a-zA-Z_][a-zA-Z0-9_]*.
    """
    return set(IDENTIFIER_RE.findall(formula))
