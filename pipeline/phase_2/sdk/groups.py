"""
SDK dimension group graph construction.

Manages group registration, hierarchy tracking, and temporal special case.
The DimensionGroup dataclass is defined in types.py; this module provides
the operational logic for building and querying the group graph.

Implements: §2.2
"""
from __future__ import annotations

import logging
from typing import Any

from ..types import DimensionGroup

logger = logging.getLogger(__name__)


def register_categorical_column(
    groups: dict[str, DimensionGroup],
    group_name: str,
    column_name: str,
    is_root: bool,
) -> None:
    """Register a categorical column in its dimension group.

    If the group does not exist, creates it. If the column is a root,
    sets it as the group root. Non-root columns are appended to the
    group's columns and hierarchy lists.

    Args:
        groups: Group registry (mutated in place).
        group_name: Name of the dimension group.
        column_name: Column name to register.
        is_root: True if this column is the root (no parent).
    """
    if group_name not in groups:
        groups[group_name] = DimensionGroup(
            name=group_name,
            root=column_name if is_root else "",
            columns=[],
            hierarchy=[],
        )

    group = groups[group_name]

    if is_root:
        group.root = column_name

    if column_name not in group.columns:
        group.columns.append(column_name)
    if column_name not in group.hierarchy:
        group.hierarchy.append(column_name)


def register_temporal_group(
    groups: dict[str, DimensionGroup],
    group_name: str,
    root_col: str,
    derived_cols: list[str],
) -> None:
    """Register the temporal group with root and derived columns.

    For temporal groups, hierarchy contains only the root date column,
    while columns includes both root and derived features (§2.6).

    Args:
        groups: Group registry (mutated in place).
        group_name: Name for the temporal group (typically "time").
        root_col: Root temporal column name.
        derived_cols: List of derived column names.
    """
    all_cols = [root_col] + derived_cols

    groups[group_name] = DimensionGroup(
        name=group_name,
        root=root_col,
        columns=all_cols,
        hierarchy=[root_col],  # Hierarchy is root-only for temporal
    )


def get_roots(groups: dict[str, DimensionGroup]) -> list[str]:
    """Return root column names across all groups.

    Used by relationships.py for root-only validation.

    Args:
        groups: Group registry.

    Returns:
        List of root column names.
    """
    return [g.root for g in groups.values() if g.root]


def is_group_root(
    column_name: str,
    columns: dict[str, dict[str, Any]],
    groups: dict[str, DimensionGroup],
) -> bool:
    """Check if a column is the root of its dimension group.

    [Subtask 1.7.1 helper]

    Args:
        column_name: Column to check.
        columns: Column registry.
        groups: Group registry.

    Returns:
        True if column_name is the root of its group.
    """
    if column_name not in columns:
        return False

    col_group = columns[column_name].get("group")
    if col_group is None or col_group not in groups:
        return False

    return groups[col_group].root == column_name


def get_group_for_column(
    column_name: str,
    columns: dict[str, dict[str, Any]],
) -> str | None:
    """Return the group name a column belongs to, or None.

    [Subtask 1.7.1 helper]

    Args:
        column_name: Column to look up.
        columns: Column registry.

    Returns:
        Group name string, or None.
    """
    if column_name not in columns:
        return None
    return columns[column_name].get("group")
