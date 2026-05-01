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
    "outlier_entity", "trend_break", "ranking_reversal", "dominance_shift",
    "convergence", "seasonal_anomaly",
})

# Required params for fully-specified pattern types
PATTERN_REQUIRED_PARAMS: dict[str, frozenset[str]] = {
    "outlier_entity": frozenset({"z_score"}),
    "trend_break": frozenset({"break_point", "magnitude"}),
    # ranking_reversal: "metrics" required (list of 2 measure cols);
    # "entity_col" optional — falls back to first categorical root in
    # the columns registry inside engine.patterns.inject_ranking_reversal.
    "ranking_reversal": frozenset({"metrics"}),
    # dominance_shift: "entity_filter" (target entity value) and
    # "split_point" (date) required; "entity_col" optional (falls back
    # to first dim-group root via _resolve_first_dim_root); "rank_change"
    # optional (default 1, validator threshold); "magnitude" optional
    # (default 1.0, used by inject_dominance_shift to size the
    # peer-relative shift).
    "dominance_shift": frozenset({"entity_filter", "split_point"}),
    # convergence: all params optional. "split_point" defaults to temporal
    # median; "entity_col" falls back to first dim-group root via
    # _resolve_first_dim_root; "reduction" defaults to 0.3 (validator
    # threshold); "pull_strength" defaults to 1.0 (injector pull magnitude).
    "convergence": frozenset(),
    # seasonal_anomaly: "anomaly_window" ([start, end] date pair) and
    # "magnitude" required at declaration time. "z_threshold" optional
    # (default 1.5, validator threshold). The validator keeps a defensive
    # "last 10% of temporal range" fallback for anomaly_window in case
    # the gate is bypassed.
    "seasonal_anomaly": frozenset({"anomaly_window", "magnitude"}),
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
    conditional_weights: dict[Any, Any],
) -> None:
    """Declare a cross-group root-level dependency.

    [Subtask 1.7.1–1.7.4; DS-4 multi-column on]

    `conditional_weights` is a nested dict whose nesting depth equals
    `len(on)`. Outer keys index `on[0]` values, the next level indexes
    `on[1]` values, and so on. The innermost (leaf) dict maps child
    values to weights. Full Cartesian coverage is required across all
    parent value combinations; leaf weights are normalized per leaf
    (same rule as the single-column case).

    Example for `on=["severity", "hospital"]`:

        conditional_weights = {
            "Mild":     {"Xiehe": {"Insurance": 0.8, "Self-Pay": 0.2},
                         "Mayo":  {"Insurance": 0.7, "Self-Pay": 0.3}},
            "Moderate": {"Xiehe": {"Insurance": 0.6, "Self-Pay": 0.4},
                         "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
        }

    Args:
        columns: Column registry.
        groups: Group registry.
        group_dependencies: Dependencies list (mutated in place).
        orthogonal_pairs: Orthogonal pairs list (for conflict check).
        child_root: Dependent root column name.
        on: List of parent root column names.
        conditional_weights: Nested per-parent-value weight distributions
            (nesting depth = len(on)).
    """
    if not on:
        raise ValueError(
            f"'on' must contain at least one column, got empty list."
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

    # Check orthogonal conflict against every parent
    child_group = _groups.get_group_for_column(child_root, columns)
    for parent_col in on:
        parent_group = _groups.get_group_for_column(parent_col, columns)
        if child_group and parent_group:
            _check_orthogonal_conflict(
                child_group, parent_group, orthogonal_pairs,
            )

    # Check root DAG acyclicity for every parent edge
    for parent_col in on:
        _dag.check_root_dag_acyclic(
            group_dependencies, child_root, parent_col,
        )

    # Validate + normalize the nested conditional_weights dict
    if not conditional_weights:
        raise ValueError(
            f"conditional_weights for '{child_root}' -> {on} is empty."
        )

    parent_value_sets = [columns[p]["values"] for p in on]
    child_values = columns[child_root]["values"]
    normalized_cw = _validate_and_normalize_nested_weights(
        cw=conditional_weights,
        parent_value_sets=parent_value_sets,
        parent_cols=list(on),
        child_values=child_values,
        path=[],
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
        censoring: Optional per-column censoring config; see
            engine.realism.inject_censoring.

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

    if censoring is not None:
        if not isinstance(censoring, dict):
            raise ValueError(
                f"censoring must be a dict, got {type(censoring).__name__}."
            )
        for col, spec in censoring.items():
            if not isinstance(spec, dict):
                raise ValueError(
                    f"censoring[{col!r}] must be a dict, got {type(spec).__name__}."
                )
            if "type" not in spec:
                raise ValueError(
                    f"censoring[{col!r}] missing required key 'type'."
                )
            c_type = spec["type"]
            if c_type not in ("right", "left", "interval"):
                raise ValueError(
                    f"censoring[{col!r}].type must be one of "
                    f"'right', 'left', 'interval'; got {c_type!r}."
                )
            if c_type in ("right", "left") and "threshold" not in spec:
                raise ValueError(
                    f"censoring[{col!r}] requires 'threshold' for type {c_type!r}."
                )
            if c_type == "interval" and ("low" not in spec or "high" not in spec):
                raise ValueError(
                    f"censoring[{col!r}] requires both 'low' and 'high' for interval."
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
        if dep_child_group is None:
            continue
        for parent_col in dep.on:
            dep_parent_group = _groups.get_group_for_column(parent_col, columns)
            if dep_parent_group is None:
                continue
            dep_pair = frozenset((dep_child_group, dep_parent_group))
            if dep_pair == candidate_pair:
                raise ValueError(
                    f"Groups '{group_a}' and '{group_b}' already have a "
                    f"group dependency (child_root='{dep.child_root}', "
                    f"on={dep.on}). Cannot also declare them orthogonal "
                    f"(mutual exclusion per §2.2)."
                )


def _validate_and_normalize_nested_weights(
    cw: dict,
    parent_value_sets: list[list[Any]],
    parent_cols: list[str],
    child_values: list[Any],
    path: list[Any],
) -> dict:
    """Recursively validate that *cw* covers the Cartesian product of
    *parent_value_sets* and that each leaf covers *child_values*. Leaf
    weights are normalized via ``_val.normalize_weight_dict_values``.

    Args:
        cw: Nested conditional_weights dict at the current recursion level.
        parent_value_sets: Remaining parent value sets (one per remaining
            recursion level). Empty when ``cw`` is at the leaf.
        parent_cols: Remaining parent column names (parallel to
            *parent_value_sets*); used for error messages.
        child_values: Allowed child values at the leaf.
        path: Keys traversed so far (for error messages).

    Returns:
        New nested dict mirroring *cw* with leaves normalized to sum 1.0.

    Raises:
        ValueError: If any level is missing required keys, contains
            extra keys, has a non-dict value at a non-leaf level, or a
            leaf has a non-dict value / negative weight / all-zero
            weights.
    """
    path_repr = "".join(f"[{k!r}]" for k in path)

    # Leaf: cw should be {child_val: weight}
    if not parent_value_sets:
        if not isinstance(cw, dict):
            raise ValueError(
                f"conditional_weights{path_repr} expected a "
                f"{{child_value: weight}} dict at the leaf, got "
                f"{type(cw).__name__}."
            )
        provided = set(cw.keys())
        expected = set(child_values)
        missing = expected - provided
        if missing:
            raise ValueError(
                f"conditional_weights{path_repr} is missing child "
                f"values: {sorted(missing)}."
            )
        extra = provided - expected
        if extra:
            raise ValueError(
                f"conditional_weights{path_repr} contains keys not "
                f"in child values: {sorted(extra)}."
            )
        return _val.normalize_weight_dict_values(
            label=f"conditional_weights{path_repr}",
            weights=cw,
        )

    # Recursive level: cw should be {parent_val: <nested>}
    if not isinstance(cw, dict):
        raise ValueError(
            f"conditional_weights{path_repr} expected a nested dict at "
            f"depth {len(path)} (parent '{parent_cols[0]}'), got "
            f"{type(cw).__name__}."
        )
    expected = set(parent_value_sets[0])
    provided = set(cw.keys())
    missing = expected - provided
    if missing:
        raise ValueError(
            f"conditional_weights{path_repr} missing parent values "
            f"at depth {len(path)} (parent '{parent_cols[0]}'): "
            f"{sorted(missing)}."
        )
    extra = provided - expected
    if extra:
        raise ValueError(
            f"conditional_weights{path_repr} contains keys not in "
            f"parent '{parent_cols[0]}' values: {sorted(extra)}."
        )
    return {
        k: _validate_and_normalize_nested_weights(
            cw=cw[k],
            parent_value_sets=parent_value_sets[1:],
            parent_cols=parent_cols[1:],
            child_values=child_values,
            path=path + [k],
        )
        for k in cw
    }
