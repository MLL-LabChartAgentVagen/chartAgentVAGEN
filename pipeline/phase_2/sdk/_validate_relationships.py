"""
Relationship-level validators.

Currently holds the root-only check used by add_group_dependency to
enforce that group dependencies are declared on dimension-group roots.
"""
from __future__ import annotations

from typing import Any


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
