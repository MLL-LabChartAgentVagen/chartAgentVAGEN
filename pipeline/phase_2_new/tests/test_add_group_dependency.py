"""
test_add_group_dependency.py — Exhaustive test suite for
FactTableSimulator.add_group_dependency().

Sprint 3 Subtask IDs tested: 1.7.1, 1.7.2, 1.7.3

Structure:
  1. Contract tests (rows 3D-1 through 3D-20)
  2. Input validation (type enforcement, boundary, constraints)
  3. Output correctness (weights normalized, GroupDependency shape)
  4. State transition (root DAG growth, ordering, isolation)
  5. Integration (interaction with declare_orthogonal, categories)
"""
from __future__ import annotations

import math

import pytest

from agpds.exceptions import (
    CyclicDependencyError,
    InvalidParameterError,
    NonRootDependencyError,
)
from agpds.models import GroupDependency
from agpds.simulator import FactTableSimulator


# ================================================================
# Fixtures
# ================================================================

@pytest.fixture
def sim() -> FactTableSimulator:
    """Simulator with three groups (entity, patient, payment)."""
    s = FactTableSimulator(500, 42)
    s.add_category("hospital",
                   ["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],
                   [1, 1, 1, 1, 1], "entity")
    s.add_category("department",
                   ["Cardiology", "Neurology", "Oncology", "Pediatrics"],
                   {"Xiehe": [1, 1, 1, 1], "Huashan": [1, 1, 1, 1],
                    "Ruijin": [1, 1, 1, 1], "Tongren": [1, 1, 1, 1],
                    "Zhongshan": [1, 1, 1, 1]},
                   "entity", parent="hospital")
    s.add_category("severity", ["Mild", "Moderate", "Severe"],
                   [0.5, 0.35, 0.15], "patient")
    s.add_category("payment_method", ["Insurance", "Self-pay", "Government"],
                   [0.6, 0.3, 0.1], "payment")
    return s


# Reusable valid conditional weights: severity → payment_method
_CW_VALID = {
    "Mild": {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},
    "Moderate": {"Insurance": 0.65, "Self-pay": 0.25, "Government": 0.10},
    "Severe": {"Insurance": 0.80, "Self-pay": 0.10, "Government": 0.10},
}

# Unnormalized version (sums != 1.0)
_CW_UNNORM = {
    "Mild": {"Insurance": 1, "Self-pay": 2, "Government": 3},
    "Moderate": {"Insurance": 6, "Self-pay": 3, "Government": 1},
    "Severe": {"Insurance": 8, "Self-pay": 1, "Government": 1},
}


# ================================================================
# 1. CONTRACT TESTS — one test per contract table row 3D-1..3D-20
# ================================================================

class TestAddGroupDependencyContract:
    """Every row from the Sprint 3 contract table §3D."""

    # [3D-1] Subtask 1.7.1, 1.7.2
    def test_3D_01_valid_dependency(self, sim: FactTableSimulator) -> None:
        """Valid root-level dependency stores GroupDependency with normalized weights."""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        assert len(sim._group_dependencies) == 1
        dep = sim._group_dependencies[0]
        assert dep.child_root == "payment_method"
        assert dep.on == ["severity"]
        assert math.isclose(sum(dep.conditional_weights["Mild"].values()), 1.0)

    # [3D-2] Subtask 1.7.1
    def test_3D_02_child_not_root(self, sim: FactTableSimulator) -> None:
        """child_root is not a group root raises NonRootDependencyError."""
        with pytest.raises(NonRootDependencyError, match="department"):
            sim.add_group_dependency("department", on=["severity"],
                conditional_weights={
                    "Mild": {"Cardiology": .25, "Neurology": .25,
                             "Oncology": .25, "Pediatrics": .25},
                    "Moderate": {"Cardiology": .25, "Neurology": .25,
                                 "Oncology": .25, "Pediatrics": .25},
                    "Severe": {"Cardiology": .25, "Neurology": .25,
                               "Oncology": .25, "Pediatrics": .25}})

    # [3D-3] Subtask 1.7.1
    def test_3D_03_on_not_root(self, sim: FactTableSimulator) -> None:
        """on[0] not a group root raises NonRootDependencyError."""
        with pytest.raises(NonRootDependencyError, match="department"):
            sim.add_group_dependency("payment_method", on=["department"],
                                     conditional_weights={})

    # [3D-4] Subtask 1.7.2 (A7)
    def test_3D_04_multi_column_on(self, sim: FactTableSimulator) -> None:
        """Multi-column on raises ValueError [A7]."""
        with pytest.raises(ValueError, match="exactly one column"):
            sim.add_group_dependency("payment_method",
                                     on=["severity", "hospital"],
                                     conditional_weights={})

    # [3D-5] Subtask 1.7.2
    def test_3D_05_empty_on(self, sim: FactTableSimulator) -> None:
        """Empty on list raises ValueError."""
        with pytest.raises(ValueError, match="exactly one column"):
            sim.add_group_dependency("payment_method", on=[],
                                     conditional_weights={})

    # [3D-6] Subtask 1.7.1
    def test_3D_06_self_dependency(self, sim: FactTableSimulator) -> None:
        """child_root == on[0] raises ValueError."""
        with pytest.raises(ValueError, match="cannot depend on itself"):
            sim.add_group_dependency("severity", on=["severity"],
                                     conditional_weights={})

    # [3D-7] Subtask 1.7.2
    def test_3D_07_missing_outer_key(self, sim: FactTableSimulator) -> None:
        """Outer keys missing 'Severe' raises ValueError."""
        with pytest.raises(ValueError, match="missing keys"):
            sim.add_group_dependency("payment_method", on=["severity"],
                conditional_weights={
                    "Mild": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                    "Moderate": {"Insurance": .6, "Self-pay": .3, "Government": .1},
                })

    # [3D-8] Subtask 1.7.2
    def test_3D_08_missing_inner_key(self, sim: FactTableSimulator) -> None:
        """Inner dict missing 'Government' for 'Mild' raises ValueError."""
        with pytest.raises(ValueError, match="missing keys"):
            sim.add_group_dependency("payment_method", on=["severity"],
                conditional_weights={
                    "Mild": {"Insurance": 0.5, "Self-pay": 0.5},
                    "Moderate": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                    "Severe": {"Insurance": .8, "Self-pay": .1, "Government": .1},
                })

    # [3D-9] Subtask 1.7.2
    def test_3D_09_negative_weight(self, sim: FactTableSimulator) -> None:
        """Negative weight raises ValueError."""
        with pytest.raises(ValueError, match="negative"):
            sim.add_group_dependency("payment_method", on=["severity"],
                conditional_weights={
                    "Mild": {"Insurance": -0.5, "Self-pay": 1.0, "Government": 0.5},
                    "Moderate": {"Insurance": .6, "Self-pay": .3, "Government": .1},
                    "Severe": {"Insurance": .8, "Self-pay": .1, "Government": .1},
                })

    # [3D-10] Subtask 1.7.2
    def test_3D_10_all_zero_weights(self, sim: FactTableSimulator) -> None:
        """All-zero weights for one outer key raises ValueError."""
        with pytest.raises(ValueError, match="all weights are zero"):
            sim.add_group_dependency("payment_method", on=["severity"],
                conditional_weights={
                    "Mild": {"Insurance": 0, "Self-pay": 0, "Government": 0},
                    "Moderate": {"Insurance": .6, "Self-pay": .3, "Government": .1},
                    "Severe": {"Insurance": .8, "Self-pay": .1, "Government": .1},
                })

    # [3D-11] Subtask 1.7.3
    def test_3D_11_bidirectional_cycle(self, sim: FactTableSimulator) -> None:
        """Bidirectional root dependency A→B then B→A raises CyclicDependencyError."""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        with pytest.raises(CyclicDependencyError):
            sim.add_group_dependency("severity", on=["payment_method"],
                conditional_weights={
                    "Insurance": {"Mild": .5, "Moderate": .3, "Severe": .2},
                    "Self-pay": {"Mild": .6, "Moderate": .3, "Severe": .1},
                    "Government": {"Mild": .4, "Moderate": .4, "Severe": .2},
                })

    # [3D-12] Subtask 1.7.3
    def test_3D_12_three_node_cycle(self, sim: FactTableSimulator) -> None:
        """Three-node root DAG cycle A→B→C→A raises CyclicDependencyError."""
        sim.add_category("region", ["North", "South"], [.5, .5], "geography")
        # severity → payment_method
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        # payment_method → region
        sim.add_group_dependency("region", on=["payment_method"],
            conditional_weights={
                "Insurance": {"North": .6, "South": .4},
                "Self-pay": {"North": .5, "South": .5},
                "Government": {"North": .7, "South": .3},
            })
        # region → severity would close cycle
        with pytest.raises(CyclicDependencyError):
            sim.add_group_dependency("severity", on=["region"],
                conditional_weights={
                    "North": {"Mild": .5, "Moderate": .3, "Severe": .2},
                    "South": {"Mild": .4, "Moderate": .4, "Severe": .2},
                })

    # [3D-13] Subtask 1.6.3 (inverse)
    def test_3D_13_conflict_with_orthogonal(self, sim: FactTableSimulator) -> None:
        """Dependency after orthogonal raises conflict ValueError."""
        sim.declare_orthogonal("payment", "patient", "independent")
        with pytest.raises(ValueError, match="orthogonal"):
            sim.add_group_dependency("payment_method", on=["severity"],
                                     conditional_weights=_CW_VALID)

    # [3D-14] Subtask 1.7.2
    def test_3D_14_wrong_type_conditional_weights(
        self, sim: FactTableSimulator
    ) -> None:
        """conditional_weights not a dict raises TypeError."""
        with pytest.raises(TypeError, match="conditional_weights must be a dict"):
            sim.add_group_dependency("payment_method", on=["severity"],
                                     conditional_weights="bad")  # type: ignore[arg-type]

    # [3D-15] Subtask 1.7.1
    def test_3D_15_on_not_list(self, sim: FactTableSimulator) -> None:
        """on not a list (bare string) raises TypeError."""
        with pytest.raises(TypeError, match="on must be a list"):
            sim.add_group_dependency("payment_method",
                                     on="severity",  # type: ignore[arg-type]
                                     conditional_weights={})

    # [3D-16] Subtask 1.7.1
    def test_3D_16_same_group_via_non_root(self, sim: FactTableSimulator) -> None:
        """Non-root in same group hits NonRootDependencyError before same-group check."""
        with pytest.raises(NonRootDependencyError):
            sim.add_group_dependency("department", on=["hospital"],
                                     conditional_weights={})

    # [3D-17] Subtask 1.7.2
    def test_3D_17_auto_normalization(self, sim: FactTableSimulator) -> None:
        """Unnormalized weights are auto-normalized so each row sums to 1.0."""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_UNNORM)
        dep = sim._group_dependencies[0]
        # Verify Mild: 1/(1+2+3) = 1/6
        assert math.isclose(dep.conditional_weights["Mild"]["Insurance"], 1/6)
        assert math.isclose(dep.conditional_weights["Mild"]["Self-pay"], 2/6)
        assert math.isclose(dep.conditional_weights["Mild"]["Government"], 3/6)
        # All rows sum to 1.0
        for k, row in dep.conditional_weights.items():
            assert math.isclose(sum(row.values()), 1.0), f"Row '{k}' not normalized"

    # [3D-18] Subtask 1.7.2 (boundary)
    def test_3D_18_two_value_child(self, sim: FactTableSimulator) -> None:
        """Boundary: child root with only 2 values works. [Subtask 1.7.2]"""
        s = FactTableSimulator(100, 1)
        s.add_category("type", ["A", "B"], [1, 1], "g1")
        s.add_category("kind", ["X", "Y"], [1, 1], "g2")
        s.add_group_dependency("kind", on=["type"],
            conditional_weights={"A": {"X": .6, "Y": .4},
                                 "B": {"X": .3, "Y": .7}})
        dep = s._group_dependencies[0]
        assert math.isclose(dep.conditional_weights["A"]["X"], 0.6)

    # [3D-19] Subtask 1.7.2
    def test_3D_19_extra_outer_key(self, sim: FactTableSimulator) -> None:
        """Extra outer key not in on[0]'s values raises ValueError."""
        with pytest.raises(ValueError, match="not in"):
            sim.add_group_dependency("payment_method", on=["severity"],
                conditional_weights={
                    "Mild": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                    "Moderate": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                    "Severe": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                    "ExtraValue": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                })

    # [3D-20] Subtask 1.7.1
    def test_3D_20_non_string_child_root(self, sim: FactTableSimulator) -> None:
        """Non-string child_root raises TypeError."""
        with pytest.raises(TypeError, match="child_root must be a str"):
            sim.add_group_dependency(123, on=["severity"],  # type: ignore[arg-type]
                                     conditional_weights={})


# ================================================================
# 2. INPUT VALIDATION TESTS
# ================================================================

class TestAddGroupDependencyInputValidation:
    """Type enforcement, boundary, and constraint checks. [Subtask 1.7.1, 1.7.2]"""

    @pytest.mark.parametrize("bad_val", [
        None, 123, 4.5, True, [], {"a": 1},
    ])
    def test_child_root_type_enforcement(
        self, sim: FactTableSimulator, bad_val: object
    ) -> None:
        """child_root must be str. [Subtask 1.7.1]"""
        with pytest.raises(TypeError, match="child_root must be a str"):
            sim.add_group_dependency(bad_val, on=["severity"],  # type: ignore[arg-type]
                                     conditional_weights={})

    @pytest.mark.parametrize("bad_val", [
        None, "severity", 123, 4.5, True, {"a": 1},
    ])
    def test_on_type_enforcement(
        self, sim: FactTableSimulator, bad_val: object
    ) -> None:
        """on must be a list. [Subtask 1.7.1]"""
        with pytest.raises(TypeError, match="on must be a list"):
            sim.add_group_dependency("payment_method",
                                     on=bad_val,  # type: ignore[arg-type]
                                     conditional_weights={})

    @pytest.mark.parametrize("bad_val", [
        None, "bad", 123, [1, 2], True,
    ])
    def test_conditional_weights_type_enforcement(
        self, sim: FactTableSimulator, bad_val: object
    ) -> None:
        """conditional_weights must be dict. [Subtask 1.7.2]"""
        with pytest.raises(TypeError, match="conditional_weights must be a dict"):
            sim.add_group_dependency("payment_method", on=["severity"],
                                     conditional_weights=bad_val)  # type: ignore[arg-type]

    @pytest.mark.parametrize("on_len", [2, 3, 5])
    def test_on_length_greater_than_one(
        self, sim: FactTableSimulator, on_len: int
    ) -> None:
        """on with len > 1 raises ValueError [A7]. [Subtask 1.7.2]"""
        cols = ["severity"] * on_len
        with pytest.raises(ValueError, match="exactly one column"):
            sim.add_group_dependency("payment_method", on=cols,
                                     conditional_weights={})

    def test_inner_value_not_dict(self, sim: FactTableSimulator) -> None:
        """Inner value (for an outer key) must be a dict. [Subtask 1.7.2]"""
        with pytest.raises(TypeError):
            sim.add_group_dependency("payment_method", on=["severity"],
                conditional_weights={
                    "Mild": [0.5, 0.3, 0.2],  # list instead of dict
                    "Moderate": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                    "Severe": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                })

    def test_non_numeric_weight_value(self, sim: FactTableSimulator) -> None:
        """Non-numeric weight value raises TypeError. [Subtask 1.7.2]"""
        with pytest.raises(TypeError):
            sim.add_group_dependency("payment_method", on=["severity"],
                conditional_weights={
                    "Mild": {"Insurance": "bad", "Self-pay": 0.3, "Government": 0.2},
                    "Moderate": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                    "Severe": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                })

    def test_bool_weight_value(self, sim: FactTableSimulator) -> None:
        """Boolean weight value raises TypeError. [Subtask 1.7.2]"""
        with pytest.raises(TypeError):
            sim.add_group_dependency("payment_method", on=["severity"],
                conditional_weights={
                    "Mild": {"Insurance": True, "Self-pay": False, "Government": True},
                    "Moderate": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                    "Severe": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                })

    def test_extra_inner_key(self, sim: FactTableSimulator) -> None:
        """Inner dict with extra key not in child's values raises. [Subtask 1.7.2]"""
        with pytest.raises(ValueError, match="not in"):
            sim.add_group_dependency("payment_method", on=["severity"],
                conditional_weights={
                    "Mild": {"Insurance": .5, "Self-pay": .3, "Government": .1,
                             "ExtraKey": .1},
                    "Moderate": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                    "Severe": {"Insurance": .5, "Self-pay": .3, "Government": .2},
                })

    def test_undeclared_child_root(self, sim: FactTableSimulator) -> None:
        """Undeclared child_root column cannot be a group root. [Subtask 1.7.1]"""
        with pytest.raises(NonRootDependencyError):
            sim.add_group_dependency("nonexistent_col", on=["severity"],
                                     conditional_weights={})

    def test_undeclared_on_column(self, sim: FactTableSimulator) -> None:
        """Undeclared on[0] column cannot be a group root. [Subtask 1.7.1]"""
        with pytest.raises(NonRootDependencyError):
            sim.add_group_dependency("payment_method", on=["nonexistent_col"],
                                     conditional_weights={})

    def test_temporal_root_rejected_as_child(
        self, sim: FactTableSimulator
    ) -> None:
        """Temporal root is not categorical; rejected for dependency. [Subtask 1.7.1]"""
        sim.add_temporal("visit_date", "2024-01-01", "2024-06-30", "daily")
        # FIX: [self-review item 7] — Changed from ValueError to
        # InvalidParameterError to match updated implementation.
        with pytest.raises(InvalidParameterError, match="categorical"):
            sim.add_group_dependency("visit_date", on=["severity"],
                                     conditional_weights={})

    def test_temporal_root_rejected_as_on(
        self, sim: FactTableSimulator
    ) -> None:
        """Temporal root as on[0] rejected — not categorical. [Subtask 1.7.1]"""
        sim.add_temporal("visit_date", "2024-01-01", "2024-06-30", "daily")
        # FIX: [self-review item 7] — Changed from ValueError to
        # InvalidParameterError to match updated implementation.
        with pytest.raises(InvalidParameterError, match="categorical"):
            sim.add_group_dependency("payment_method", on=["visit_date"],
                                     conditional_weights={})


# ================================================================
# 3. OUTPUT CORRECTNESS TESTS
# ================================================================

class TestAddGroupDependencyOutputCorrectness:
    """Verify GroupDependency shape, normalization, and types. [Subtask 1.7.2]"""

    def test_return_value_is_none(self, sim: FactTableSimulator) -> None:
        """add_group_dependency returns None. [Subtask 1.7.1]"""
        result = sim.add_group_dependency("payment_method", on=["severity"],
                                          conditional_weights=_CW_VALID)
        assert result is None

    def test_stored_object_is_group_dependency(
        self, sim: FactTableSimulator
    ) -> None:
        """Stored object is a GroupDependency dataclass. [Subtask 1.7.1]"""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        assert isinstance(sim._group_dependencies[0], GroupDependency)

    def test_normalization_numerical_correctness(
        self, sim: FactTableSimulator
    ) -> None:
        """Hand-calculated normalization matches stored values. [Subtask 1.7.2]"""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_UNNORM)
        dep = sim._group_dependencies[0]
        # Moderate: 6+3+1 = 10
        assert math.isclose(dep.conditional_weights["Moderate"]["Insurance"], 0.6)
        assert math.isclose(dep.conditional_weights["Moderate"]["Self-pay"], 0.3)
        assert math.isclose(dep.conditional_weights["Moderate"]["Government"], 0.1)

    def test_already_normalized_weights_unchanged(
        self, sim: FactTableSimulator
    ) -> None:
        """Already-normalized weights preserved exactly. [Subtask 1.7.2]"""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        dep = sim._group_dependencies[0]
        assert dep.conditional_weights["Mild"]["Insurance"] == pytest.approx(0.45)
        assert dep.conditional_weights["Mild"]["Self-pay"] == pytest.approx(0.45)
        assert dep.conditional_weights["Mild"]["Government"] == pytest.approx(0.10)

    def test_to_metadata_correct(self, sim: FactTableSimulator) -> None:
        """to_metadata returns correct dict structure. [Subtask 1.7.1]"""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        meta = sim._group_dependencies[0].to_metadata()
        assert meta["child_root"] == "payment_method"
        assert meta["on"] == ["severity"]
        assert "Mild" in meta["conditional_weights"]

    def test_to_metadata_defensive_copy(self, sim: FactTableSimulator) -> None:
        """Mutating to_metadata() output does not mutate internal state. [Subtask 2.2.2]"""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        meta = sim._group_dependencies[0].to_metadata()
        meta["conditional_weights"]["Mild"]["Insurance"] = 999.0
        # Original internal state should be unchanged
        assert sim._group_dependencies[0].conditional_weights["Mild"]["Insurance"] != 999.0


# ================================================================
# 4. STATE TRANSITION TESTS
# ================================================================

class TestAddGroupDependencyStateTransitions:
    """Verify root DAG growth and isolation. [Subtask 1.7.3]"""

    def test_multiple_dependencies_accumulate(
        self, sim: FactTableSimulator
    ) -> None:
        """Multiple valid dependencies accumulate in list. [Subtask 1.7.1]"""
        sim.add_category("region", ["North", "South"], [.5, .5], "geography")
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        sim.add_group_dependency("region", on=["hospital"],
            conditional_weights={
                "Xiehe": {"North": .6, "South": .4},
                "Huashan": {"North": .5, "South": .5},
                "Ruijin": {"North": .4, "South": .6},
                "Tongren": {"North": .7, "South": .3},
                "Zhongshan": {"North": .3, "South": .7},
            })
        assert len(sim._group_dependencies) == 2

    def test_failed_dependency_does_not_mutate_state(
        self, sim: FactTableSimulator
    ) -> None:
        """Failed add_group_dependency leaves _group_dependencies unchanged. [Subtask 1.7.1]"""
        n_before = len(sim._group_dependencies)
        with pytest.raises(NonRootDependencyError):
            sim.add_group_dependency("department", on=["severity"],
                conditional_weights={
                    "Mild": {"Cardiology": .25, "Neurology": .25,
                             "Oncology": .25, "Pediatrics": .25},
                    "Moderate": {"Cardiology": .25, "Neurology": .25,
                                 "Oncology": .25, "Pediatrics": .25},
                    "Severe": {"Cardiology": .25, "Neurology": .25,
                               "Oncology": .25, "Pediatrics": .25}})
        assert len(sim._group_dependencies) == n_before

    def test_instance_isolation(self) -> None:
        """Two instances have independent dependency lists. [Subtask 1.1.2]"""
        s1 = FactTableSimulator(100, 1)
        s2 = FactTableSimulator(100, 2)
        s1.add_category("a", ["X", "Y"], [1, 1], "g1")
        s1.add_category("b", ["P", "Q"], [1, 1], "g2")
        s1.add_group_dependency("b", on=["a"],
            conditional_weights={"X": {"P": .6, "Q": .4},
                                 "Y": {"P": .3, "Q": .7}})
        assert len(s1._group_dependencies) == 1
        assert len(s2._group_dependencies) == 0

    def test_linear_chain_acyclic(self, sim: FactTableSimulator) -> None:
        """Linear chain A→B→C is acyclic and accepted. [Subtask 1.7.3]"""
        sim.add_category("region", ["North", "South"], [.5, .5], "geography")
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        sim.add_group_dependency("region", on=["payment_method"],
            conditional_weights={
                "Insurance": {"North": .6, "South": .4},
                "Self-pay": {"North": .5, "South": .5},
                "Government": {"North": .7, "South": .3},
            })
        assert len(sim._group_dependencies) == 2

    def test_dependencies_in_insertion_order(
        self, sim: FactTableSimulator
    ) -> None:
        """Dependencies stored in declaration order. [Subtask 1.7.1]"""
        sim.add_category("region", ["North", "South"], [.5, .5], "geography")
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        sim.add_group_dependency("region", on=["hospital"],
            conditional_weights={
                "Xiehe": {"North": .6, "South": .4},
                "Huashan": {"North": .5, "South": .5},
                "Ruijin": {"North": .4, "South": .6},
                "Tongren": {"North": .7, "South": .3},
                "Zhongshan": {"North": .3, "South": .7},
            })
        assert sim._group_dependencies[0].child_root == "payment_method"
        assert sim._group_dependencies[1].child_root == "region"


# ================================================================
# 5. INTEGRATION TESTS
# ================================================================

class TestAddGroupDependencyIntegration:
    """Cross-method boundary tests. [Subtask 1.7.3, 1.6.3]"""

    def test_dependency_blocks_orthogonal(
        self, sim: FactTableSimulator
    ) -> None:
        """After dependency(payment←severity), orthogonal(payment,patient) blocked. [Subtask 1.6.3]"""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        with pytest.raises(ValueError, match="mutual exclusion"):
            sim.declare_orthogonal("payment", "patient", "conflict")

    def test_orthogonal_blocks_dependency(
        self, sim: FactTableSimulator
    ) -> None:
        """After orthogonal(payment,patient), dependency(payment←severity) blocked. [Subtask 1.6.3]"""
        sim.declare_orthogonal("payment", "patient", "independent")
        with pytest.raises(ValueError, match="orthogonal"):
            sim.add_group_dependency("payment_method", on=["severity"],
                                     conditional_weights=_CW_VALID)

    def test_unrelated_orthogonal_does_not_block(
        self, sim: FactTableSimulator
    ) -> None:
        """Orthogonal(entity,patient) does not block dependency(payment←severity). [Subtask 1.6.3]"""
        sim.declare_orthogonal("entity", "patient", "independent")
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        assert len(sim._group_dependencies) == 1

    def test_cycle_error_contains_meaningful_path(
        self, sim: FactTableSimulator
    ) -> None:
        """CyclicDependencyError contains cycle_path attribute. [Subtask 1.7.3]"""
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        with pytest.raises(CyclicDependencyError) as exc_info:
            sim.add_group_dependency("severity", on=["payment_method"],
                conditional_weights={
                    "Insurance": {"Mild": .5, "Moderate": .3, "Severe": .2},
                    "Self-pay": {"Mild": .6, "Moderate": .3, "Severe": .1},
                    "Government": {"Mild": .4, "Moderate": .4, "Severe": .2},
                })
        # CyclicDependencyError has cycle_path attribute
        assert hasattr(exc_info.value, "cycle_path")
        assert len(exc_info.value.cycle_path) >= 3  # at least [A, B, A]

    def test_cycle_error_message_says_root_dependency(
        self, sim: FactTableSimulator
    ) -> None:
        """Root-level cycle message says 'Root dependency' not 'Measure'. [Subtask 1.7.3]

        FIX: [self-review item 1] — Verifies the corrected message prefix.
        """
        sim.add_group_dependency("payment_method", on=["severity"],
                                 conditional_weights=_CW_VALID)
        with pytest.raises(CyclicDependencyError) as exc_info:
            sim.add_group_dependency("severity", on=["payment_method"],
                conditional_weights={
                    "Insurance": {"Mild": .5, "Moderate": .3, "Severe": .2},
                    "Self-pay": {"Mild": .6, "Moderate": .3, "Severe": .1},
                    "Government": {"Mild": .4, "Moderate": .4, "Severe": .2},
                })
        # The overridden message should use "Root dependency", not "Measure"
        assert "Root dependency" in exc_info.value.message
        assert "Measure" not in exc_info.value.message

    def test_full_one_shot_sprint3_workflow(
        self, sim: FactTableSimulator
    ) -> None:
        """Full one-shot example workflow from §2.5 (Sprint 3 scope). [Integration]"""
        s = sim
        s.add_temporal("visit_date", "2024-01-01", "2024-06-30", "daily",
                       derive=["day_of_week", "month"])
        s.add_measure("wait_minutes", "lognormal", {
            "mu": {"intercept": 2.8, "effects": {
                "severity": {"Mild": 0.0, "Moderate": 0.4, "Severe": 0.9},
                "hospital": {"Xiehe": 0.2, "Huashan": -0.1, "Ruijin": 0.0,
                             "Tongren": 0.1, "Zhongshan": -0.1}}},
            "sigma": {"intercept": 0.35, "effects": {
                "severity": {"Mild": 0.0, "Moderate": 0.05, "Severe": 0.10}}}})
        s.add_measure_structural("cost",
            formula="wait_minutes * 12 + severity_surcharge",
            effects={"severity_surcharge": {"Mild": 50, "Moderate": 200, "Severe": 500}},
            noise={"family": "gaussian", "sigma": 30})
        s.add_measure_structural("satisfaction",
            formula="9 - 0.04 * wait_minutes + severity_adj",
            effects={"severity_adj": {"Mild": 0.5, "Moderate": 0.0, "Severe": -1.5}},
            noise={"family": "gaussian", "sigma": 0.6})
        s.declare_orthogonal("entity", "patient",
            rationale="Severity distribution is independent of hospital/department")
        s.add_group_dependency("payment_method", on=["severity"],
            conditional_weights=_CW_VALID)

        # Final assertions
        assert len(s._orthogonal_pairs) == 1
        assert len(s._group_dependencies) == 1
        assert "cost" in s._measure_dag["wait_minutes"]
        assert "satisfaction" in s._measure_dag["wait_minutes"]
        assert s._group_dependencies[0].child_root == "payment_method"
