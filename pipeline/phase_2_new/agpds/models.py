"""
Sprint 1 — Data classes for dimension groups and cross-group relations.

Subtask IDs: 2.1.1, 2.2.1, 2.2.2

These are pure data containers with serialization support. They hold the
structural declarations that the FactTableSimulator collects via its API
methods. Validation of the *values* stored in these classes happens in the
SDK class (simulator.py), not here — these classes trust their callers.

Design choice: Python dataclasses (not Pydantic) because these are internal
data structures with no user-facing deserialization needs. The spec does not
prescribe a specific class structure (§2.1.1 implementation design choice).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ===== Dimension Group =====

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

        # FIX: [self-review item 2] — Docstring now explicitly states that the
        # caller provides the group name as a dict key. The §2.6 format uses
        # group name as key: {"entity": {"columns": [...], "hierarchy": [...]}}.
        # This method returns only the inner value dict; the caller maps
        # group.name -> group.to_metadata() when building the full block.

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

    # FIX: [self-review item 4] — __repr__ was not in the interface sketch.
    # Retained as a debugging aid; documented as an additive utility not
    # part of the formal interface contract.
    def __repr__(self) -> str:
        """Debugging repr — additive utility, not in interface sketch."""
        return (
            f"DimensionGroup(name={self.name!r}, root={self.root!r}, "
            f"columns={self.columns!r})"
        )


# ===== Orthogonal Pair =====

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

    # FIX: [self-review item 4] — involves_group and group_pair_set were not
    # in the interface sketch. Retained as Sprint 3 utilities for conflict
    # detection (subtasks 1.6.3 / 1.7.4). Documented as additive.

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


# ===== Group Dependency =====

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
        # FIX: [self-review item 5] — Deep-copy inner dicts so callers cannot
        # mutate internal state via the returned metadata. Previously used
        # dict(self.conditional_weights) which only shallow-copied the outer
        # dict, leaving inner {str: float} dicts as shared references.
        return {
            "child_root": self.child_root,
            "on": list(self.on),
            "conditional_weights": {
                k: dict(v) for k, v in self.conditional_weights.items()
            },
        }

    # FIX: [self-review item 4] — __repr__ was not in the interface sketch.
    # Retained as a debugging aid; documented as additive.
    def __repr__(self) -> str:
        """Debugging repr — additive utility, not in interface sketch."""
        return (
            f"GroupDependency(child_root={self.child_root!r}, "
            f"on={self.on!r}, "
            f"conditional_weights=<{len(self.conditional_weights)} entries>)"
        )
