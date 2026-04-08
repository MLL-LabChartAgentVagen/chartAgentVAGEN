"""
SDK relationship declaration functions.

These functions implement the Step 2 declaration API (declare_orthogonal,
add_group_dependency, inject_pattern, set_realism) as standalone functions
that accept explicit store parameters.

Implements: §2.1.2
"""
from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Any, Optional

from ..exceptions import (
    NonRootDependencyError,
)
from ..types import DimensionGroup, OrthogonalPair, GroupDependency
from . import validation as _val
from . import dag as _dag
from . import groups as _groups

logger = logging.getLogger(__name__)

# §2.1.2 pattern types
VALID_PATTERN_TYPES: frozenset[str] = frozenset({
    "outlier_entity", "trend_break", "ranking_reversal",
    "dominance_shift", "convergence", "seasonal_anomaly",
})

# Required params for fully-specified pattern types
PATTERN_REQUIRED_PARAMS: dict[str, frozenset[str]] = {
    "outlier_entity": frozenset({"z_score"}),
    "trend_break": frozenset({"break_point", "magnitude"}),
    "ranking_reversal": frozenset({"metrics", "entity_col"}),
    "dominance_shift": frozenset({"entity_filter", "col", "split_point"}),
    # convergence: no required params (fully unspecified)
    # seasonal_anomaly: no required params (fully unspecified)
}


def declare_orthogonal(
    groups: dict[str, DimensionGroup],
    orthogonal_pairs: list[OrthogonalPair],
    group_dependencies: list[GroupDependency],
    columns: dict[str, dict[str, Any]],
    group_a: str,
    group_b: str,
    rationale: str,
) -> None:
    """Declare two groups as statistically orthogonal (independent).

    [Subtask 1.6.1–1.6.3]

    Args:
        groups: Group registry.
        orthogonal_pairs: Orthogonal pairs list (mutated in place).
        group_dependencies: Group dependencies list (for conflict check).
        columns: Column registry (for conflict check).
        group_a: First group name.
        group_b: Second group name.
        rationale: Human-readable justification.
    """
    # Validate groups exist
    if group_a not in groups:
        raise ValueError(f"Group '{group_a}' not found in registry.")
    if group_b not in groups:
        raise ValueError(f"Group '{group_b}' not found in registry.")
    if group_a == group_b:
        raise ValueError(
            f"Cannot declare a group orthogonal with itself ('{group_a}')."
        )

    # Check for dependency conflict
    _check_dependency_conflict(
        group_a, group_b, group_dependencies, columns,
    )

    # Check for duplicate orthogonal declaration
    new_pair = OrthogonalPair(
        group_a=group_a, group_b=group_b, rationale=rationale,
    )
    for existing in orthogonal_pairs:
        if existing == new_pair:
            raise ValueError(
                f"Groups '{group_a}' and '{group_b}' are already "
                f"declared orthogonal."
            )

    orthogonal_pairs.append(new_pair)

    logger.debug(
        "declare_orthogonal: '%s' ⊥ '%s' (rationale='%s').",
        group_a, group_b, rationale,
    )


def add_group_dependency(
    columns: OrderedDict[str, dict[str, Any]],
    groups: dict[str, DimensionGroup],
    group_dependencies: list[GroupDependency],
    orthogonal_pairs: list[OrthogonalPair],
    child_root: str,
    on: list[str],
    conditional_weights: dict[str, dict[str, float]],
) -> None:
    """Declare a cross-group root-level dependency.

    [Subtask 1.7.1–1.7.4]

    Args:
        columns: Column registry.
        groups: Group registry.
        group_dependencies: Dependencies list (mutated in place).
        orthogonal_pairs: Orthogonal pairs list (for conflict check).
        child_root: Dependent root column name.
        on: List of parent root column names.
        conditional_weights: Per-parent-value weight distributions.
    """
    # P2-4: Restrict to single-column `on` for v1
    if not on:
        raise ValueError(
            f"'on' must contain at least one column, got empty list."
        )
    if len(on) != 1:
        raise NotImplementedError(
            f"Multi-column 'on' is not supported in v1. "
            f"Got on={on} (length {len(on)}). Use a single column."
        )

    # Validate child_root is a root
    if child_root not in columns:
        raise ValueError(f"Column '{child_root}' not found in registry.")
    if not _groups.is_group_root(child_root, columns, groups):
        raise NonRootDependencyError(column_name=child_root)

    # Validate all on columns are roots
    for parent_col in on:
        if parent_col not in columns:
            raise ValueError(f"Column '{parent_col}' not found in registry.")
        if not _groups.is_group_root(parent_col, columns, groups):
            raise NonRootDependencyError(column_name=parent_col)

    # Check orthogonal conflict
    child_group = _groups.get_group_for_column(child_root, columns)
    parent_group = _groups.get_group_for_column(on[0], columns)
    if child_group and parent_group:
        _check_orthogonal_conflict(
            child_group, parent_group, orthogonal_pairs,
        )

    # Check root DAG acyclicity
    _dag.check_root_dag_acyclic(group_dependencies, child_root, on[0])

    # Validate and normalize conditional weights
    child_values = columns[child_root]["values"]
    parent_values = columns[on[0]]["values"]

    if not conditional_weights:
        raise ValueError(
            f"conditional_weights for '{child_root}' -> '{on[0]}' is empty."
        )

    # Validate all parent values are covered
    provided_keys = set(conditional_weights.keys())
    expected_keys = set(parent_values)
    missing = expected_keys - provided_keys
    if missing:
        raise ValueError(
            f"conditional_weights for '{child_root}' is missing keys "
            f"for parent values: {sorted(missing)}."
        )

    extra = provided_keys - expected_keys
    if extra:
        raise ValueError(
            f"conditional_weights for '{child_root}' contains keys "
            f"not in parent '{on[0]}' values: {sorted(extra)}."
        )

    # Normalize each row
    normalized_cw: dict[str, dict[str, float]] = {}
    for parent_val, child_weight_map in conditional_weights.items():
        # Validate child value coverage
        child_provided = set(child_weight_map.keys())
        child_expected = set(child_values)
        child_missing = child_expected - child_provided
        if child_missing:
            raise ValueError(
                f"conditional_weights['{parent_val}'] is missing child "
                f"values: {sorted(child_missing)}."
            )

        normalized_cw[parent_val] = _val.normalize_weight_dict_values(
            label=f"conditional_weights['{parent_val}']",
            weights=child_weight_map,
        )

    # Register dependency
    dep = GroupDependency(
        child_root=child_root,
        on=list(on),
        conditional_weights=normalized_cw,
    )
    group_dependencies.append(dep)

    logger.debug(
        "add_group_dependency: '%s' depends on %s.",
        child_root, on,
    )


def inject_pattern(
    columns: dict[str, dict[str, Any]],
    patterns: list[dict[str, Any]],
    type: str,
    target: str,
    col: str,
    **params: Any,
) -> None:
    """Declare a narrative-driven statistical pattern.

    [Subtask 1.8.1–1.8.4]

    Args:
        columns: Column registry.
        patterns: Pattern list (mutated in place).
        type: Pattern type string.
        target: DataFrame query expression.
        col: Target measure column name.
        **params: Type-specific parameters.
    """
    # Validate pattern type
    if type not in VALID_PATTERN_TYPES:
        raise ValueError(
            f"Unsupported pattern type '{type}'. "
            f"Supported: {sorted(VALID_PATTERN_TYPES)}"
        )

    # Validate target column exists and is a measure
    if col not in columns:
        raise ValueError(
            f"Pattern target column '{col}' not found in registry."
        )
    if columns[col].get("type") != "measure":
        raise ValueError(
            f"Pattern target column '{col}' is not a measure column."
        )

    # Validate required params for fully-specified types
    if type in PATTERN_REQUIRED_PARAMS:
        required = PATTERN_REQUIRED_PARAMS[type]
        missing = required - set(params.keys())
        if missing:
            raise ValueError(
                f"Pattern type '{type}' requires params: {sorted(missing)}."
            )

    # Register the pattern
    pattern_spec: dict[str, Any] = {
        "type": type,
        "target": target,
        "col": col,
        "params": dict(params),
    }
    patterns.append(pattern_spec)

    logger.debug(
        "inject_pattern: type='%s', target='%s', col='%s'.",
        type, target, col,
    )


def set_realism(
    realism_config_holder: list,
    missing_rate: float = 0.0,
    dirty_rate: float = 0.0,
    censoring: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Configure realism injection parameters.

    [Subtask 1.9.1]

    Args:
        realism_config_holder: Single-element list to hold config (mutated).
        missing_rate: Fraction of cells to NaN.
        dirty_rate: Fraction of categorical cells to corrupt.
        censoring: Optional censoring config (placeholder).

    Returns:
        The realism config dict.
    """
    if not (0.0 <= missing_rate <= 1.0):
        raise ValueError(
            f"missing_rate must be in [0, 1], got {missing_rate}."
        )
    if not (0.0 <= dirty_rate <= 1.0):
        raise ValueError(
            f"dirty_rate must be in [0, 1], got {dirty_rate}."
        )

    config: dict[str, Any] = {
        "missing_rate": missing_rate,
        "dirty_rate": dirty_rate,
        "censoring": censoring,
    }

    logger.debug(
        "set_realism: missing_rate=%.3f, dirty_rate=%.3f.",
        missing_rate, dirty_rate,
    )

    return config


# =====================================================================
# Conflict Detection Helpers
# =====================================================================

def _check_orthogonal_conflict(
    group_a: str,
    group_b: str,
    orthogonal_pairs: list[OrthogonalPair],
) -> None:
    """Raise ValueError if group pair has an existing orthogonal declaration."""
    candidate_pair = frozenset((group_a, group_b))
    for pair in orthogonal_pairs:
        if pair.group_pair_set() == candidate_pair:
            raise ValueError(
                f"Groups '{group_a}' and '{group_b}' are declared "
                f"orthogonal. Cannot also declare a dependency between "
                f"them (mutual exclusion per §2.2)."
            )


def _check_dependency_conflict(
    group_a: str,
    group_b: str,
    group_dependencies: list[GroupDependency],
    columns: dict[str, dict[str, Any]],
) -> None:
    """Raise ValueError if group pair has an existing dependency declaration."""
    candidate_pair = frozenset((group_a, group_b))
    for dep in group_dependencies:
        dep_child_group = _groups.get_group_for_column(dep.child_root, columns)
        dep_parent_group = _groups.get_group_for_column(dep.on[0], columns)
        if dep_child_group is None or dep_parent_group is None:
            continue
        dep_pair = frozenset((dep_child_group, dep_parent_group))
        if dep_pair == candidate_pair:
            raise ValueError(
                f"Groups '{group_a}' and '{group_b}' already have a "
                f"group dependency (child_root='{dep.child_root}', "
                f"on={dep.on}). Cannot also declare them orthogonal "
                f"(mutual exclusion per §2.2)."
            )
