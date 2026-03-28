"""
Sprint 1 — Exception hierarchy for the AGPDS FactTableSimulator SDK.
Sprint 6 — Added PatternInjectionError for generation-time pattern failures.

Subtask IDs: 6.1.1, 6.1.2, 6.1.3, 6.1.4
  Note on numbering: The sprint plan uses pre-merge IDs (6.1.1, 6.1.2,
  6.1.3, 6.1.4). The post-audit task hierarchy merged 6.1.1-6.1.3 into
  a single 6.1.1 and renumbered 6.1.4 to 6.1.2. This module uses SPRINT
  PLAN numbering throughout for traceability to the sprint that produced it.

All SDK exceptions inherit from SimulatorError, which itself inherits from
Exception. This allows callers to catch broad (SimulatorError) or narrow
(CyclicDependencyError) as needed. The §2.7 execution-error feedback loop
relies on typed exceptions to produce targeted repair instructions for the LLM.

Error taxonomy from §2.7:
  - CyclicDependencyError   -> DAG cycle in measures or root-level deps
  - UndefinedEffectError     -> effect map missing a categorical value
  - NonRootDependencyError   -> cross-group dep on a non-root column
  - InvalidParameterError    -> distribution param outside valid domain [A5a]
  - DuplicateColumnError     -> column name registered twice
  - EmptyValuesError         -> add_category called with empty values list
  - WeightLengthMismatchError-> values/weights length mismatch
  - DegenerateDistributionError -> params that collapse a distribution
  - ParentNotFoundError      -> parent column missing or wrong group
  - DuplicateGroupRootError  -> second root added to a group
  - PatternInjectionError    -> generation-time pattern injection failure
"""
# FIX: [self-review item 9] — Added numbering convention note to module
# docstring. Sprint plan IDs (6.1.1-6.1.4) are used in all docstrings
# for traceability; the post-audit task hierarchy renumbering is noted
# once here rather than duplicated on every class.

from __future__ import annotations


# ===== Base Exception =====

class SimulatorError(Exception):
    """Base exception for all FactTableSimulator SDK errors.

    [Subtask 6.1.1]

    Every SDK-specific exception inherits from this class so that the §2.7
    feedback loop can catch SimulatorError as a blanket handler, while still
    allowing narrow catches for specific error types.
    """


# ===== §2.7 Core Exception Classes =====

class CyclicDependencyError(SimulatorError):
    """Raised when a dependency cycle is detected in the measure or root-level DAG.

    [Subtask 6.1.1]

    The cycle path is stored and rendered into the message so the LLM receives
    the exact cycle for targeted repair (§2.7 step 4 example).

    Args:
        cycle_path: Ordered list of node names forming the cycle.
                    The first and last element should be the same node,
                    e.g. ["cost", "satisfaction", "cost"].
    """

    def __init__(self, cycle_path: list[str]) -> None:
        # Store the raw cycle path for programmatic access by the feedback loop
        self.cycle_path = cycle_path

        # Build the arrow-separated path string matching §2.7 example format:
        # "Measure 'cost' -> 'satisfaction' -> 'cost' forms a cycle."
        arrow_chain = " \u2192 ".join(f"'{node}'" for node in cycle_path)
        self.message = f"Measure {arrow_chain} forms a cycle."
        super().__init__(self.message)


class UndefinedEffectError(SimulatorError):
    """Raised when an effect references a categorical value with no definition.

    [Subtask 6.1.2]

    This catches incomplete effect tables at declaration time, preventing
    runtime KeyErrors during engine execution (§2.7 step 4 example).

    Args:
        effect_name: The name of the effect map (e.g. "severity_surcharge").
        missing_value: The categorical value lacking a definition (e.g. "Severe").
    """

    def __init__(self, effect_name: str, missing_value: str) -> None:
        # Store fields for programmatic access by the feedback formatter
        self.effect_name = effect_name
        self.missing_value = missing_value

        # Format matches §2.7 example exactly:
        # "'severity_surcharge' in formula has no definition for 'Severe'."
        self.message = (
            f"'{effect_name}' in formula has no definition for '{missing_value}'."
        )
        super().__init__(self.message)


class NonRootDependencyError(SimulatorError):
    """Raised when a cross-group dependency references a non-root column.

    [Subtask 6.1.3]

    The §2.2 root-only constraint restricts add_group_dependency to group
    root columns. This exception names the offending column so the LLM
    can switch to using the group's root (§2.7 step 4 example).

    Args:
        column_name: The non-root column that was incorrectly used.
    """

    def __init__(self, column_name: str) -> None:
        # Store for programmatic access
        self.column_name = column_name

        # Format matches §2.7 example:
        # "'department' is not a group root; cannot use in add_group_dependency."
        self.message = (
            f"'{column_name}' is not a group root; "
            f"cannot use in add_group_dependency."
        )
        super().__init__(self.message)


# ===== §2.7 Additional Validation Errors [Subtask 6.1.4] =====
# These cover "degenerate distributions" and other declaration-time
# validation failures mentioned in §2.7 but not given explicit class
# names in the spec.

class InvalidParameterError(SimulatorError):
    """Raised when a computed distribution parameter falls outside its valid domain.

    [Subtask 6.1.4 — Assumption A5a]

    Proactively covers parameter domain validation (e.g. sigma < 0, shape < 0)
    ahead of spec clarification. Downstream sprints (measure declarations,
    engine sampling) will raise this when intercept+effects produce out-of-domain
    parameter values.

    Args:
        param_name: Name of the parameter (e.g. "sigma").
        value: The invalid value that was computed or declared.
        reason: Why the value is invalid (e.g. "must be > 0").
    """

    def __init__(self, param_name: str, value: float, reason: str) -> None:
        # Store all fields for programmatic access by the feedback formatter
        self.param_name = param_name
        self.value = value
        self.reason = reason

        self.message = (
            f"Parameter '{param_name}' has invalid value {value}: {reason}."
        )
        super().__init__(self.message)


class DuplicateColumnError(SimulatorError):
    """Raised when a column name is registered more than once.

    [Subtask 6.1.4]

    Column name uniqueness is inferred from DAG semantics — every column
    is a node, and nodes must be unique. This catches the error at
    declaration time rather than letting it surface as a silent DAG
    corruption during generation.

    Args:
        column_name: The duplicate column name.
    """

    def __init__(self, column_name: str) -> None:
        self.column_name = column_name
        self.message = (
            f"Column '{column_name}' is already declared. "
            f"Each column name must be unique across all groups."
        )
        super().__init__(self.message)


class EmptyValuesError(SimulatorError):
    """Raised when add_category is called with an empty values list.

    [Subtask 6.1.4]

    §2.1.1 states add_category "rejects empty values". An empty categorical
    column would produce undefined sampling behavior in the engine.

    Args:
        column_name: The column whose values list was empty.
    """

    def __init__(self, column_name: str) -> None:
        self.column_name = column_name
        self.message = (
            f"Column '{column_name}' has an empty values list. "
            f"Categorical columns require at least one value."
        )
        super().__init__(self.message)


class WeightLengthMismatchError(SimulatorError):
    """Raised when the weights list length does not match the values list length.

    [Subtask 6.1.4]

    Each value must have exactly one corresponding weight for the categorical
    distribution to be well-defined.

    Args:
        column_name: The column name.
        n_values: Length of the values list.
        n_weights: Length of the weights list.
    """

    def __init__(self, column_name: str, n_values: int, n_weights: int) -> None:
        self.column_name = column_name
        self.n_values = n_values
        self.n_weights = n_weights
        self.message = (
            f"Column '{column_name}' has {n_values} values but {n_weights} weights. "
            f"These lengths must match."
        )
        super().__init__(self.message)


class DegenerateDistributionError(SimulatorError):
    """Raised when distribution parameters produce a degenerate distribution.

    [Subtask 6.1.4]

    §2.7 mentions "degenerate distributions" as a catchable semantic error.
    This covers cases like sigma=0 (point mass) or all-zero weights that
    would make sampling undefined or trivial.

    Args:
        column_name: The measure column.
        detail: Description of the degeneracy (e.g. "sigma=0 produces a point mass").
    """

    def __init__(self, column_name: str, detail: str) -> None:
        self.column_name = column_name
        self.detail = detail
        self.message = (
            f"Column '{column_name}' has a degenerate distribution: {detail}."
        )
        super().__init__(self.message)


class ParentNotFoundError(SimulatorError):
    """Raised when a parent column does not exist or is not in the same group.

    [Subtask 6.1.4]

    §2.1.1 states add_category "validates parent exists in same group".
    This is a declaration-time check that prevents orphaned hierarchy edges.

    Args:
        child_name: The child column being declared.
        parent_name: The parent that was not found.
        group: The group in which the parent was expected.
    """

    def __init__(self, child_name: str, parent_name: str, group: str) -> None:
        self.child_name = child_name
        self.parent_name = parent_name
        self.group = group
        self.message = (
            f"Parent '{parent_name}' not found in group '{group}' "
            f"when declaring child column '{child_name}'."
        )
        super().__init__(self.message)


class DuplicateGroupRootError(SimulatorError):
    """Raised when a second root column is added to a group that already has one.

    [Subtask 6.1.4]

    §2.2 states "each group has a root column" (singular), strongly implying
    uniqueness. A group with two roots would have an ambiguous hierarchy and
    undefined sampling semantics.

    Args:
        group_name: The group.
        existing_root: The existing root column name.
        attempted_root: The column attempting to become a second root.
    """

    def __init__(
        self, group_name: str, existing_root: str, attempted_root: str
    ) -> None:
        self.group_name = group_name
        self.existing_root = existing_root
        self.attempted_root = attempted_root
        self.message = (
            f"Group '{group_name}' already has root column '{existing_root}'. "
            f"Cannot add '{attempted_root}' as a second root."
        )
        super().__init__(self.message)


# ===== Sprint 6: Generation-Time Pattern Injection Errors =====

# FIX: [self-review item 6] — Added PatternInjectionError to replace bare
# ValueError in _inject_outlier_entity and _inject_trend_break. The §2.7
# error taxonomy covers declaration-time errors; these generation-time
# errors had no typed exception. Per the implementation principle "raise
# typed, descriptive exceptions (not bare ValueError)".

class PatternInjectionError(SimulatorError):
    """Raised when a pattern injection operation fails at generation time.

    [Sprint 6 — Subtask 4.3.1, 4.3.2]

    Covers runtime failures during Phase γ pattern injection that are not
    declaration-time errors (those are caught by inject_pattern validation).
    Examples: target expression matches zero rows, column has zero variance,
    no temporal column available for trend break.

    Args:
        pattern_type: The pattern type being injected (e.g. "outlier_entity").
        detail: Description of the failure.
    """

    def __init__(self, pattern_type: str, detail: str) -> None:
        self.pattern_type = pattern_type
        self.detail = detail
        self.message = (
            f"Pattern injection '{pattern_type}' failed: {detail}"
        )
        super().__init__(self.message)
