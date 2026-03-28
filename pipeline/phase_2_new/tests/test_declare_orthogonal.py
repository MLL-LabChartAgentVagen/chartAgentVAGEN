"""
test_declare_orthogonal.py — Exhaustive test suite for
FactTableSimulator.declare_orthogonal().

Sprint 3 Subtask IDs tested: 1.6.1, 1.6.2, 1.6.3

Structure:
  1. Contract tests (rows 3C-1 through 3C-11)
  2. Input validation (type enforcement, boundary, constraints)
  3. Output correctness (pair shape, order-independence, immutability)
  4. State transition (pair accumulation, instance isolation)
  5. Integration (interaction with add_group_dependency)
"""
from __future__ import annotations

import pytest

from agpds.models import OrthogonalPair
from agpds.simulator import FactTableSimulator


# ================================================================
# Fixtures
# ================================================================

@pytest.fixture
def sim() -> FactTableSimulator:
    """Simulator with three categorical groups."""
    s = FactTableSimulator(500, 42)
    s.add_category("hospital", ["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],
                   [1, 1, 1, 1, 1], "entity")
    s.add_category("severity", ["Mild", "Moderate", "Severe"],
                   [0.5, 0.35, 0.15], "patient")
    s.add_category("payment_method", ["Insurance", "Self-pay", "Government"],
                   [0.6, 0.3, 0.1], "payment")
    return s


# Helper: valid conditional weights for severity→payment_method
_CW_SEV_PAY = {
    "Mild": {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},
    "Moderate": {"Insurance": 0.65, "Self-pay": 0.25, "Government": 0.10},
    "Severe": {"Insurance": 0.80, "Self-pay": 0.10, "Government": 0.10},
}


# ================================================================
# 1. CONTRACT TESTS — one test per contract table row 3C-1..3C-11
# ================================================================

class TestDeclareOrthogonalContract:
    """Every row from the Sprint 3 contract table §3C."""

    # [3C-1] Subtask 1.6.1, 1.6.2
    def test_3C_01_valid_declaration(self, sim: FactTableSimulator) -> None:
        """Valid orthogonal declaration stores pair with rationale."""
        sim.declare_orthogonal("entity", "patient", "Independent severity")
        assert len(sim._orthogonal_pairs) == 1
        pair = sim._orthogonal_pairs[0]
        assert pair.group_a == "entity"
        assert pair.group_b == "patient"
        assert pair.rationale == "Independent severity"

    # [3C-2] Subtask 1.6.2
    def test_3C_02_reverse_order(self, sim: FactTableSimulator) -> None:
        """Reverse argument order stores same canonical pair."""
        sim.declare_orthogonal("patient", "entity", "Reversed")
        pair = sim._orthogonal_pairs[0]
        assert pair == OrthogonalPair("entity", "patient", "anything")

    # [3C-3] Subtask 1.6.2
    def test_3C_03_order_independent_lookup(self, sim: FactTableSimulator) -> None:
        """Pair is findable by either order via __eq__."""
        sim.declare_orthogonal("entity", "patient", "test")
        pair = sim._orthogonal_pairs[0]
        assert pair == OrthogonalPair("entity", "patient", "")
        assert pair == OrthogonalPair("patient", "entity", "")

    # [3C-4] Subtask 1.6.1
    def test_3C_04_nonexistent_group_b(self, sim: FactTableSimulator) -> None:
        """group_b doesn't exist raises ValueError."""
        with pytest.raises(ValueError, match="does not exist"):
            sim.declare_orthogonal("entity", "NONEXISTENT", "test")

    # [3C-5] Subtask 1.6.1
    def test_3C_05_nonexistent_group_a(self, sim: FactTableSimulator) -> None:
        """group_a doesn't exist raises ValueError."""
        with pytest.raises(ValueError, match="does not exist"):
            sim.declare_orthogonal("NONEXISTENT", "entity", "test")

    # [3C-6] Subtask 1.6.1
    def test_3C_06_self_orthogonal(self, sim: FactTableSimulator) -> None:
        """Self-orthogonal raises ValueError."""
        with pytest.raises(ValueError, match="orthogonal to itself"):
            sim.declare_orthogonal("entity", "entity", "test")

    # [3C-7] Subtask 1.6.2
    def test_3C_07_duplicate_pair(self, sim: FactTableSimulator) -> None:
        """Declaring same pair twice raises ValueError."""
        sim.declare_orthogonal("entity", "patient", "first")
        with pytest.raises(ValueError, match="already declared orthogonal"):
            sim.declare_orthogonal("entity", "patient", "second")

    # [3C-8] Subtask 1.6.3
    def test_3C_08_conflict_with_dependency(self, sim: FactTableSimulator) -> None:
        """Orthogonal after dependency raises conflict ValueError."""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_SEV_PAY)
        with pytest.raises(ValueError, match="mutual exclusion"):
            sim.declare_orthogonal("payment", "patient", "conflicting")

    # [3C-9] Subtask 1.6.1
    def test_3C_09_non_string_group(self, sim: FactTableSimulator) -> None:
        """Non-string group_a raises TypeError."""
        with pytest.raises(TypeError, match="group_a must be a str"):
            sim.declare_orthogonal(123, "entity", "test")  # type: ignore[arg-type]

    # [3C-10] Subtask 1.6.1
    def test_3C_10_empty_rationale(self, sim: FactTableSimulator) -> None:
        """Empty rationale is valid — documentation, not logic."""
        sim.declare_orthogonal("entity", "patient", "")
        assert sim._orthogonal_pairs[0].rationale == ""

    # [3C-11] Subtask 1.6.1
    def test_3C_11_non_string_rationale(self, sim: FactTableSimulator) -> None:
        """Non-string rationale raises TypeError."""
        with pytest.raises(TypeError, match="rationale must be a str"):
            sim.declare_orthogonal("entity", "patient", 999)  # type: ignore[arg-type]


# ================================================================
# 2. INPUT VALIDATION TESTS
# ================================================================

class TestDeclareOrthogonalInputValidation:
    """Type enforcement, boundary, and constraint checks. [Subtask 1.6.1]"""

    @pytest.mark.parametrize("bad_val", [
        None, 123, 4.5, True, [], {"a": 1}, b"bytes",
    ])
    def test_group_a_type_enforcement(
        self, sim: FactTableSimulator, bad_val: object
    ) -> None:
        """group_a must be str. [Subtask 1.6.1]"""
        with pytest.raises(TypeError, match="group_a must be a str"):
            sim.declare_orthogonal(bad_val, "entity", "r")  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_val", [
        None, 123, 4.5, True, [], {"a": 1},
    ])
    def test_group_b_type_enforcement(
        self, sim: FactTableSimulator, bad_val: object
    ) -> None:
        """group_b must be str. [Subtask 1.6.1]"""
        with pytest.raises(TypeError, match="group_b must be a str"):
            sim.declare_orthogonal("entity", bad_val, "r")  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_val", [
        None, 123, 4.5, True, [],
    ])
    def test_rationale_type_enforcement(
        self, sim: FactTableSimulator, bad_val: object
    ) -> None:
        """rationale must be str. [Subtask 1.6.1]"""
        with pytest.raises(TypeError, match="rationale must be a str"):
            sim.declare_orthogonal("entity", "patient", bad_val)  # type: ignore[arg-type]

    def test_both_groups_nonexistent(self, sim: FactTableSimulator) -> None:
        """Both groups nonexistent raises on first check. [Subtask 1.6.1]"""
        with pytest.raises(ValueError, match="does not exist"):
            sim.declare_orthogonal("NOPE_A", "NOPE_B", "test")

    def test_duplicate_reversed_order(self, sim: FactTableSimulator) -> None:
        """Duplicate in reversed order also raises. [Subtask 1.6.2]"""
        sim.declare_orthogonal("entity", "patient", "first")
        with pytest.raises(ValueError, match="already declared orthogonal"):
            sim.declare_orthogonal("patient", "entity", "second")

    def test_long_rationale_accepted(self, sim: FactTableSimulator) -> None:
        """Very long rationale string is accepted. [Subtask 1.6.1]"""
        sim.declare_orthogonal("entity", "patient", "x" * 10000)
        assert len(sim._orthogonal_pairs[0].rationale) == 10000


# ================================================================
# 3. OUTPUT CORRECTNESS TESTS
# ================================================================

class TestDeclareOrthogonalOutputCorrectness:
    """Verify pair shape, types, and immutability. [Subtask 1.6.2]"""

    def test_return_value_is_none(self, sim: FactTableSimulator) -> None:
        """declare_orthogonal returns None. [Subtask 1.6.1]"""
        result = sim.declare_orthogonal("entity", "patient", "test")
        assert result is None

    def test_stored_pair_is_orthogonal_pair_instance(
        self, sim: FactTableSimulator
    ) -> None:
        """Stored object is an OrthogonalPair dataclass. [Subtask 1.6.2]"""
        sim.declare_orthogonal("entity", "patient", "test")
        assert isinstance(sim._orthogonal_pairs[0], OrthogonalPair)

    def test_pair_hash_is_order_independent(
        self, sim: FactTableSimulator
    ) -> None:
        """hash(Pair(A,B)) == hash(Pair(B,A)). [Subtask 1.6.2]"""
        p1 = OrthogonalPair("entity", "patient", "r1")
        p2 = OrthogonalPair("patient", "entity", "r2")
        assert hash(p1) == hash(p2)

    def test_pair_in_set_deduplication(self) -> None:
        """OrthogonalPairs with same groups deduplicate in sets. [Subtask 1.6.2]"""
        p1 = OrthogonalPair("A", "B", "r1")
        p2 = OrthogonalPair("B", "A", "r2")
        s = {p1, p2}
        assert len(s) == 1

    def test_to_metadata_correct(self, sim: FactTableSimulator) -> None:
        """to_metadata returns correct dict. [Subtask 1.6.2]"""
        sim.declare_orthogonal("entity", "patient", "test reason")
        meta = sim._orthogonal_pairs[0].to_metadata()
        assert meta == {
            "group_a": "entity",
            "group_b": "patient",
            "rationale": "test reason",
        }

    def test_group_pair_set_helper(self) -> None:
        """group_pair_set returns frozenset of group names. [Subtask 1.6.2]"""
        p = OrthogonalPair("entity", "patient", "r")
        assert p.group_pair_set() == frozenset({"entity", "patient"})


# ================================================================
# 4. STATE TRANSITION TESTS
# ================================================================

class TestDeclareOrthogonalStateTransitions:
    """Verify pair accumulation and isolation. [Subtask 1.6.2]"""

    def test_multiple_pairs_accumulate(self, sim: FactTableSimulator) -> None:
        """Multiple distinct pairs accumulate in _orthogonal_pairs. [Subtask 1.6.2]"""
        sim.declare_orthogonal("entity", "patient", "r1")
        sim.declare_orthogonal("entity", "payment", "r2")
        sim.declare_orthogonal("patient", "payment", "r3")
        assert len(sim._orthogonal_pairs) == 3

    def test_failed_declare_does_not_mutate(
        self, sim: FactTableSimulator
    ) -> None:
        """Failed declaration leaves _orthogonal_pairs unchanged. [Subtask 1.6.1]"""
        n_before = len(sim._orthogonal_pairs)
        with pytest.raises(ValueError):
            sim.declare_orthogonal("entity", "entity", "self")
        assert len(sim._orthogonal_pairs) == n_before

    def test_instance_isolation(self) -> None:
        """Two instances have independent orthogonal pair lists. [Subtask 1.1.2]"""
        s1 = FactTableSimulator(100, 1)
        s2 = FactTableSimulator(100, 2)
        s1.add_category("a", ["X", "Y"], [1, 1], "g1")
        s1.add_category("b", ["P", "Q"], [1, 1], "g2")
        s1.declare_orthogonal("g1", "g2", "test")
        assert len(s1._orthogonal_pairs) == 1
        assert len(s2._orthogonal_pairs) == 0

    def test_pairs_list_order_is_insertion_order(
        self, sim: FactTableSimulator
    ) -> None:
        """Pairs stored in declaration order. [Subtask 1.6.2]"""
        sim.declare_orthogonal("entity", "patient", "first")
        sim.declare_orthogonal("entity", "payment", "second")
        assert sim._orthogonal_pairs[0].rationale == "first"
        assert sim._orthogonal_pairs[1].rationale == "second"


# ================================================================
# 5. INTEGRATION TESTS
# ================================================================

class TestDeclareOrthogonalIntegration:
    """Cross-sprint and cross-method boundary tests. [Subtask 1.6.3]"""

    def test_conflict_bidirectional_dep_then_ortho(
        self, sim: FactTableSimulator
    ) -> None:
        """Dependency A→B blocks orthogonal(A,B). [Subtask 1.6.3]"""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_SEV_PAY)
        with pytest.raises(ValueError, match="mutual exclusion"):
            sim.declare_orthogonal("payment", "patient", "conflict")

    def test_conflict_reversed_group_names(
        self, sim: FactTableSimulator
    ) -> None:
        """Dependency A→B blocks orthogonal(B,A) too. [Subtask 1.6.3]"""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_SEV_PAY)
        with pytest.raises(ValueError, match="mutual exclusion"):
            sim.declare_orthogonal("patient", "payment", "conflict reversed")

    def test_unrelated_dependency_does_not_block_orthogonal(
        self, sim: FactTableSimulator
    ) -> None:
        """Dependency on A↔B does not block orthogonal(A,C). [Subtask 1.6.3]"""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_SEV_PAY)
        # entity has no dependency with patient — orthogonal should succeed
        sim.declare_orthogonal("entity", "patient", "ok")
        assert len(sim._orthogonal_pairs) == 1

    def test_orthogonal_with_temporal_group(
        self, sim: FactTableSimulator
    ) -> None:
        """Orthogonal with temporal group 'time' is valid. [Subtask 1.6.1]"""
        sim.add_temporal("visit_date", "2024-01-01", "2024-06-30", "daily")
        sim.declare_orthogonal("entity", "time", "hospitals independent of time")
        assert len(sim._orthogonal_pairs) == 1

    def test_orthogonal_requires_groups_from_add_category(
        self, sim: FactTableSimulator
    ) -> None:
        """Groups must be populated via add_category before orthogonal. [Subtask 1.6.1]"""
        # Fresh simulator with no categories
        s = FactTableSimulator(100, 1)
        with pytest.raises(ValueError, match="does not exist"):
            s.declare_orthogonal("entity", "patient", "test")
