"""
Shared data types for the AGPDS Phase 2 SDK.

Migrated from models.py (Sprint 1 dataclasses) and expanded with:
  - Check, ValidationReport (from validator.py)
  - ColumnDescriptor, PatternSpec, RealismConfig, DeclarationStore (new)

Every other module imports from here. This file contains no business logic —
only data structures and type definitions.

Implements: §2.1, §2.1.1, §2.1.2, §2.2, §2.9 (Check/ValidationReport)
"""
from __future__ import annotations

import logging
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


# =====================================================================
# Dimension Group (from models.py)
# =====================================================================

@dataclass
class DimensionGroup:
    """A named dimension group containing columns and an optional drill-down hierarchy.

    [Subtask 2.1.1]

    Represents the §2.2 dimension group abstraction. Each group has exactly
    one root column (no parent).

    For **categorical** groups, child columns form a conditional-sampling
    hierarchy (parent->child): both ``columns`` and ``hierarchy`` list the
    same members in root-first order.

    For the **temporal** (``"time"``) group, ``columns`` includes the
    temporal root *and* all derived feature columns (day_of_week, month,
    etc.), but ``hierarchy`` contains **only the root** because derived
    columns are deterministic transforms, not drill-down levels (§2.6).

    Attributes:
        name: Group name (e.g. "entity", "patient", "time").
        root: The root column name (the column with no parent).
        columns: All column names belonging to this group, in insertion order.
        hierarchy: Root-first ordering of columns that form the drill-down
                   chain. For categorical groups this mirrors ``columns``;
                   for the temporal group this is ``[root]`` only.
    """

    name: str
    root: str
    columns: list[str] = field(default_factory=list)
    hierarchy: list[str] = field(default_factory=list)

    def to_metadata(self) -> dict[str, Any]:
        """Serialize to the §2.6 metadata format for the dimension_groups block.

        [Subtask 2.1.1]

        Returns:
            Dict with keys "columns" and "hierarchy", matching the §2.6
            JSON inner value: {"columns": [...], "hierarchy": [...]}.
            The caller is responsible for keying this by group name.
        """
        # Return defensive copies so callers cannot mutate internal state
        return {
            "columns": list(self.columns),
            "hierarchy": list(self.hierarchy),
        }

    def __repr__(self) -> str:
        """Debugging repr — additive utility, not in interface sketch."""
        return (
            f"DimensionGroup(name={self.name!r}, root={self.root!r}, "
            f"columns={self.columns!r})"
        )


# =====================================================================
# Orthogonal Pair (from models.py)
# =====================================================================

@dataclass
class OrthogonalPair:
    """An order-independent declaration that two groups are statistically independent.

    [Subtask 2.2.1]

    §2.2 states that independence is declared between *entire groups*, not
    individual columns. The pair (A, B) is semantically identical to (B, A),
    so __eq__ and __hash__ are order-independent on the group names.

    The rationale field is metadata for the LLM prompt and §2.6 output; it
    does not participate in identity (two declarations of the same group pair
    with different rationales are the same pair).

    Attributes:
        group_a: First group name.
        group_b: Second group name.
        rationale: Human-readable justification for independence.
    """

    group_a: str
    group_b: str
    rationale: str

    def __eq__(self, other: object) -> bool:
        """Order-independent equality: OrthogonalPair(A,B) == OrthogonalPair(B,A).

        [Subtask 2.2.1]

        Only the group pair matters for identity — rationale is excluded because
        the same group pair should not be declared orthogonal twice regardless
        of rationale wording.
        """
        # Guard against comparison with non-OrthogonalPair types
        if not isinstance(other, OrthogonalPair):
            return NotImplemented

        # Order-independent comparison: frozenset ignores element order
        self_pair = frozenset((self.group_a, self.group_b))
        other_pair = frozenset((other.group_a, other.group_b))
        return self_pair == other_pair

    def __hash__(self) -> int:
        """Hash consistent with order-independent __eq__.

        [Subtask 2.2.1]

        Uses frozenset to ensure hash(Pair(A,B)) == hash(Pair(B,A)), which
        is required for correct set/dict behavior.
        """
        return hash(frozenset((self.group_a, self.group_b)))

    def to_metadata(self) -> dict[str, str]:
        """Serialize to §2.6 metadata format for the orthogonal_groups block.

        [Subtask 2.2.1]

        Returns:
            {"group_a": ..., "group_b": ..., "rationale": ...}
        """
        return {
            "group_a": self.group_a,
            "group_b": self.group_b,
            "rationale": self.rationale,
        }

    def involves_group(self, group_name: str) -> bool:
        """Check whether this pair involves a specific group.

        [Subtask 2.2.1] — Additive utility for Sprint 3 conflict detection.

        Args:
            group_name: The group to check membership for.

        Returns:
            True if group_name is either group_a or group_b.
        """
        return group_name in (self.group_a, self.group_b)

    def group_pair_set(self) -> frozenset[str]:
        """Return the unordered pair of group names as a frozenset.

        [Subtask 2.2.1] — Additive utility for efficient lookups.
        """
        return frozenset((self.group_a, self.group_b))


# =====================================================================
# Group Dependency (from models.py)
# =====================================================================

@dataclass
class GroupDependency:
    """A cross-group root-level dependency declaration.

    [Subtask 2.2.2]

    Represents the §2.2 cross-group dependency where a root column's
    distribution is conditional on root columns from other groups.
    The root-level dependency graph must be a DAG (§2.2 constraint).

    Attributes:
        child_root: The dependent root column name (e.g. "payment_method").
        on: List of parent root column names (e.g. ["severity"]).
            Currently restricted to single-column conditioning per assumption A7
            (Sprint 3), but stored as list for forward compatibility.
        conditional_weights: Mapping of parent values to child weight distributions.
            For single-column `on`: outer keys are values of the `on[0]` column,
            inner dicts map child values to weights.
            E.g. {"Mild": {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10}}
    """

    child_root: str
    on: list[str]
    conditional_weights: dict[str, dict[str, float]]

    def to_metadata(self) -> dict[str, Any]:
        """Serialize to §2.6 metadata format for the group_dependencies block.

        [Subtask 2.2.2]

        Returns:
            {"child_root": ..., "on": [...], "conditional_weights": {...}}
        """
        return {
            "child_root": self.child_root,
            "on": list(self.on),
            "conditional_weights": {
                k: dict(v) for k, v in self.conditional_weights.items()
            },
        }

    def __repr__(self) -> str:
        """Debugging repr — additive utility, not in interface sketch."""
        return (
            f"GroupDependency(child_root={self.child_root!r}, "
            f"on={self.on!r}, "
            f"conditional_weights=<{len(self.conditional_weights)} entries>)"
        )


# =====================================================================
# Validation Data Classes (from validator.py)
# =====================================================================

@dataclass
class Check:
    """A single validation check result.

    [Subtask 8.1.1]

    §2.9 L1 code: Check(name, passed=...).  The detail field carries
    human-readable context (e.g. "χ² p=0.34") for debugging and for
    the auto-fix loop to inspect failure reasons.

    Attributes:
        name: Check identifier (e.g. "row_count", "cardinality_hospital").
        passed: Whether this check passed.
        detail: Optional human-readable detail string.
    """

    name: str
    passed: bool
    detail: Optional[str] = None


@dataclass
class ValidationReport:
    """Aggregates Check results from one or more validation layers.

    [Subtask 8.1.2]

    §2.9 auto-fix loop uses report.all_passed and report.failures to
    decide whether to retry.  The checks list accumulates results from
    L1, L2, and L3 sequentially via add_checks().

    Attributes:
        checks: All Check objects from the validation run.
    """

    checks: list[Check] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        """True iff every check in the report passed.

        [Subtask 8.1.2]

        An empty report (no checks) is considered all-passed —
        vacuously true, consistent with "no failures found".
        """
        # All-passed is vacuously true when no checks exist, and is
        # the logical AND of all check.passed values otherwise
        return all(check.passed for check in self.checks)

    @property
    def failures(self) -> list[Check]:
        """List of Check objects where passed is False.

        [Subtask 8.1.2]

        Returns a new list each call — callers cannot corrupt internal
        state by mutating the returned list.
        """
        # Filter to only failing checks for the auto-fix loop to inspect
        return [check for check in self.checks if not check.passed]

    def add_checks(self, new_checks: list[Check]) -> None:
        """Append a batch of checks to this report.

        [Subtask 8.1.2]

        Used by the orchestrator (deferred 8.1.3) to accumulate results
        from L1, L2, L3 sequentially.

        Args:
            new_checks: List of Check objects to add.
        """
        # Extend rather than replace — reports accumulate across layers
        self.checks.extend(new_checks)


# =====================================================================
# New Types — DeclarationStore (progressive wrapper)
# =====================================================================

@dataclass
class PatternSpec:
    """A declared narrative-driven statistical pattern.

    [§2.1.2]

    Attributes:
        type: Pattern type string from the 6-type whitelist.
        target: DataFrame query expression string.
        col: Target measure column name.
        params: Type-specific parameters dict.
    """
    type: str
    target: str
    col: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to the raw dict format used by current engine code."""
        return {
            "type": self.type,
            "target": self.target,
            "col": self.col,
            "params": dict(self.params),
        }


@dataclass
class RealismConfig:
    """Configuration for realism injection (missing values, dirty data, censoring).

    [§2.1]

    Attributes:
        missing_rate: Fraction of cells to set to NaN, in [0, 1].
        dirty_rate: Fraction of categorical cells to corrupt, in [0, 1].
        censoring: Optional opaque dict for censoring configuration.
    """
    missing_rate: float = 0.0
    dirty_rate: float = 0.0
    censoring: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to the raw dict format used by current engine code."""
        return {
            "missing_rate": self.missing_rate,
            "dirty_rate": self.dirty_rate,
            "censoring": dict(self.censoring) if self.censoring is not None else None,
        }


class DeclarationStore:
    """Compound container for all declarations accumulated by the SDK.

    [§2.1 — Progressive wrapper]

    This is the single artifact that crosses the M1 boundary into M2 and M4.
    Currently wraps the existing OrderedDict-based registries for backward
    compatibility. Will be progressively migrated to typed ColumnDescriptor
    list in future batches.

    Lifecycle: accumulating → frozen (via freeze()). Once frozen, mutation
    methods raise RuntimeError.

    FactTableSimulator creates a DeclarationStore internally and aliases
    its registries. freeze() is called at the start of generate() to
    enforce immutability during pipeline execution.
    """

    def __init__(self, target_rows: int, seed: int) -> None:
        self.target_rows: int = target_rows
        self.seed: int = seed
        self._frozen: bool = False

        # Current registries — progressive wrapper preserves existing format
        self.columns: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.groups: dict[str, DimensionGroup] = {}
        self.orthogonal_pairs: list[OrthogonalPair] = []
        self.group_dependencies: list[GroupDependency] = []
        self.patterns: list[dict[str, Any]] = []
        self.realism_config: Optional[dict[str, Any]] = None
        self.measure_dag: dict[str, list[str]] = {}

    @property
    def is_frozen(self) -> bool:
        """Whether this store has been frozen (read-only)."""
        return self._frozen

    def freeze(self) -> None:
        """Transition from mutable to read-only. Idempotent."""
        self._frozen = True
        logger.debug("DeclarationStore frozen: %d columns, %d groups.",
                      len(self.columns), len(self.groups))

    def _check_mutable(self) -> None:
        """Raise if trying to mutate a frozen store."""
        if self._frozen:
            raise RuntimeError(
                "DeclarationStore is frozen. Cannot modify after freeze()."
            )


# Parameter overrides for Loop B auto-fix (P0-3)
# Structure: {"measures": {col_name: {param_key: factor}}, "patterns": {idx: patch},
#             "reshuffle": [col_name, ...]}
ParameterOverrides = dict[str, Any]


@dataclass
class SandboxResult:
    """Result of a single sandbox execution attempt.

    [Subtask 7.1.1]

    Attributes:
        success: ``True`` if ``build_fact_table()`` returned a valid
            ``(DataFrame, dict)`` tuple.
        dataframe: The generated DataFrame on success; ``None`` on failure.
        metadata: The schema metadata dict on success; ``None`` on failure.
        exception: The captured exception on failure; ``None`` on success.
        traceback_str: Formatted traceback on failure; ``None`` on success.
    """
    success: bool
    dataframe: Optional[pd.DataFrame] = None
    metadata: Optional[dict[str, Any]] = None
    raw_declarations: Optional[dict[str, Any]] = None
    exception: Optional[Exception] = None
    traceback_str: Optional[str] = None

@dataclass
class RetryLoopResult:
    """Result of the full 2.7 retry loop.

    [Subtask 7.1.3]

    Attributes:
        success: ``True`` if any attempt succeeded within the budget.
        dataframe: The generated DataFrame from the successful attempt.
        metadata: The schema metadata dict from the successful attempt.
        attempts: Total number of attempts made (1-based).
        history: list[SandboxResult] = field(default_factory=list)
    """
    success: bool
    dataframe: Optional[pd.DataFrame] = None
    metadata: Optional[dict[str, Any]] = None
    raw_declarations: Optional[dict[str, Any]] = None
    attempts: int = 0
    history: list[SandboxResult] = field(default_factory=list)
