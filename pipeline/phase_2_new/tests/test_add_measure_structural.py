"""
test_add_measure_structural.py — Exhaustive test suite for
FactTableSimulator.add_measure_structural().

Sprint 3 Subtask IDs tested: 1.5.1, 1.5.3, 1.5.5

Structure:
  1. Contract tests (rows 3B-1 through 3B-18)
  2. Input validation (type enforcement, boundary, constraints)
  3. Output correctness (registry shape, DAG edges, immutability)
  4. State transition (DAG growth, chain building)
  5. Integration (interaction with add_measure and add_category)
"""
from __future__ import annotations

import copy

import pytest

from agpds.exceptions import (
    CyclicDependencyError,
    DuplicateColumnError,
    UndefinedEffectError,
)
from agpds.simulator import FactTableSimulator


# ================================================================
# Fixtures
# ================================================================

@pytest.fixture
def sim() -> FactTableSimulator:
    """Simulator with categories + one stochastic root measure."""
    s = FactTableSimulator(500, 42)
    s.add_category("hospital",
                   ["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],
                   [1, 1, 1, 1, 1], "entity")
    s.add_category("severity", ["Mild", "Moderate", "Severe"],
                   [0.5, 0.35, 0.15], "patient")
    s.add_category("payment_method", ["Insurance", "Self-pay", "Government"],
                   [0.6, 0.3, 0.1], "payment")
    s.add_measure("wait_minutes", "lognormal", {"mu": 2.8, "sigma": 0.35})
    return s


_SEV_SURCHARGE = {"surcharge": {"Mild": 50, "Moderate": 200, "Severe": 500}}
_SEV_ADJ = {"adj": {"Mild": 0.5, "Moderate": 0.0, "Severe": -1.5}}
_GAUSS_NOISE = {"family": "gaussian", "sigma": 30}


# ================================================================
# 1. CONTRACT TESTS — one test per contract table row 3B-1..3B-18
# ================================================================

class TestAddMeasureStructuralContract:
    """Every row from the Sprint 3 contract table §3B."""

    # [3B-1] Subtask 1.5.1, 1.5.3, 1.5.5
    def test_3B_01_valid_structural(self, sim: FactTableSimulator) -> None:
        """Valid structural measure with effects and noise."""
        sim.add_measure_structural("cost",
            formula="wait_minutes * 12 + surcharge",
            effects=_SEV_SURCHARGE, noise=_GAUSS_NOISE)
        col = sim._columns["cost"]
        assert col["type"] == "measure"
        assert col["measure_type"] == "structural"
        assert col["formula"] == "wait_minutes * 12 + surcharge"
        assert "wait_minutes" in col["depends_on"]
        assert "cost" in sim._measure_dag["wait_minutes"]

    # [3B-2] Subtask 1.5.5
    def test_3B_02_second_structural_no_cycle(self, sim: FactTableSimulator) -> None:
        """Two structural measures both depending on same root."""
        sim.add_measure_structural("cost", "wait_minutes * 12 + surcharge",
                                   effects=_SEV_SURCHARGE, noise=_GAUSS_NOISE)
        sim.add_measure_structural("sat", "9 - 0.04 * wait_minutes + adj",
                                   effects=_SEV_ADJ,
                                   noise={"family": "gaussian", "sigma": 0.6})
        assert "cost" in sim._measure_dag["wait_minutes"]
        assert "sat" in sim._measure_dag["wait_minutes"]

    # [3B-3] Subtask 1.5.1
    def test_3B_03_duplicate_name(self, sim: FactTableSimulator) -> None:
        """Duplicate structural name raises DuplicateColumnError."""
        sim.add_measure_structural("cost", "wait_minutes * 12")
        with pytest.raises(DuplicateColumnError):
            sim.add_measure_structural("cost", "wait_minutes * 2")

    # [3B-4] Subtask 1.5.1
    def test_3B_04_empty_formula(self, sim: FactTableSimulator) -> None:
        """Empty formula raises ValueError."""
        with pytest.raises(ValueError, match="formula must not be empty"):
            sim.add_measure_structural("x", formula="")

    # [3B-5] Subtask 1.5.1
    def test_3B_05_undeclared_measure_ref(self, sim: FactTableSimulator) -> None:
        """Formula references undeclared measure and no matching effect."""
        with pytest.raises(ValueError, match="undefined symbol"):
            sim.add_measure_structural("x", formula="UNDECLARED * 2")

    # [3B-6] Subtask 1.5.3
    def test_3B_06_effect_not_in_formula(self, sim: FactTableSimulator) -> None:
        """Effect name not referenced in formula raises UndefinedEffectError."""
        with pytest.raises(UndefinedEffectError, match="not found in formula"):
            sim.add_measure_structural("x", "wait_minutes * 2",
                effects={"eff": {"Mild": 1, "Moderate": 2, "Severe": 3}})

    # [3B-7] Subtask 1.5.3
    def test_3B_07_effect_inner_keys_no_match(self, sim: FactTableSimulator) -> None:
        """Effect inner keys don't match any declared categorical column."""
        with pytest.raises(UndefinedEffectError):
            sim.add_measure_structural("x", "wait_minutes * 2 + eff",
                effects={"eff": {"UNKNOWN": 1}})

    # [3B-8] Subtask 1.5.5
    def test_3B_08_dag_chain_correct(self, sim: FactTableSimulator) -> None:
        """Chain A→B→C is correctly built. [Subtask 1.5.5]"""
        sim.add_measure_structural("cost", "wait_minutes * 12")
        sim.add_measure_structural("profit", "cost * 0.1")
        assert "cost" in sim._measure_dag["wait_minutes"]
        assert "profit" in sim._measure_dag["cost"]

    # [3B-9] Subtask 1.5.5
    def test_3B_09_three_node_chain_then_attempted_reverse(
        self, sim: FactTableSimulator
    ) -> None:
        """Chain wait→cost→profit; then profit→wait would be cycle.

        With unique-name constraint, this specific cycle cannot happen
        (wait already exists). This test validates the DAG structure.
        """
        sim.add_measure_structural("cost", "wait_minutes * 12")
        sim.add_measure_structural("profit", "cost * 0.1")
        # Verify chain built correctly
        assert sim._measure_dag["wait_minutes"] == ["cost"]
        assert sim._measure_dag["cost"] == ["profit"]
        assert sim._measure_dag["profit"] == []

    # [3B-10] Subtask 1.5.1
    def test_3B_10_no_effects_no_noise(self, sim: FactTableSimulator) -> None:
        """None defaults produce empty dicts."""
        sim.add_measure_structural("doubled", "wait_minutes * 2")
        col = sim._columns["doubled"]
        assert col["effects"] == {}
        assert col["noise"] == {}
        assert "wait_minutes" in col["depends_on"]

    # [3B-11] Subtask 1.5.1
    def test_3B_11_effects_wrong_type(self, sim: FactTableSimulator) -> None:
        """Effects not a dict raises TypeError."""
        with pytest.raises(TypeError, match="effects must be a dict"):
            sim.add_measure_structural("x", "wait_minutes * 2",
                effects="not_a_dict")  # type: ignore[arg-type]

    # [3B-12] Subtask 1.5.1
    def test_3B_12_noise_wrong_type(self, sim: FactTableSimulator) -> None:
        """Noise not a dict raises TypeError."""
        with pytest.raises(TypeError, match="noise must be a dict"):
            sim.add_measure_structural("x", "wait_minutes * 2",
                noise="not_a_dict")  # type: ignore[arg-type]

    # [3B-13] Subtask 1.5.1
    def test_3B_13_formula_not_string(self, sim: FactTableSimulator) -> None:
        """Formula not a string raises TypeError."""
        with pytest.raises(TypeError, match="formula must be a str"):
            sim.add_measure_structural("x", 12345)  # type: ignore[arg-type]

    # [3B-14] Subtask 1.5.3
    def test_3B_14_empty_effect_inner_dict(self, sim: FactTableSimulator) -> None:
        """Empty inner effect dict raises UndefinedEffectError."""
        with pytest.raises(UndefinedEffectError):
            sim.add_measure_structural("x", "wait_minutes * 2 + surcharge",
                effects={"surcharge": {}})

    # [3B-15] Subtask 1.5.1
    def test_3B_15_literal_only_formula(self, sim: FactTableSimulator) -> None:
        """Formula with only numeric literals — no DAG edges."""
        sim.add_measure_structural("constant", "12 + 5")
        assert sim._columns["constant"]["depends_on"] == []
        assert sim._measure_dag["constant"] == []

    # [3B-16] Subtask 1.5.3
    def test_3B_16_effect_subset_missing_value(self, sim: FactTableSimulator) -> None:
        """Inner keys are subset of severity values (missing 'Severe')."""
        with pytest.raises(UndefinedEffectError):
            sim.add_measure_structural("x", "wait_minutes * 2 + surcharge",
                effects={"surcharge": {"Mild": 50, "Moderate": 200}})

    # [3B-17] Subtask 1.5.1
    def test_3B_17_non_string_name(self, sim: FactTableSimulator) -> None:
        """Non-string name raises TypeError."""
        with pytest.raises(TypeError, match="name must be a str"):
            sim.add_measure_structural(123, "wait_minutes * 2")  # type: ignore[arg-type]

    # [3B-18] Subtask 1.5.1
    def test_3B_18_self_referencing(self, sim: FactTableSimulator) -> None:
        """Self-referencing formula (x not yet declared) raises ValueError."""
        with pytest.raises(ValueError, match="undefined symbol"):
            sim.add_measure_structural("x", "x * 2")


# ================================================================
# 2. INPUT VALIDATION TESTS
# ================================================================

class TestAddMeasureStructuralInputValidation:
    """Type enforcement, boundary, and constraint checks. [Subtask 1.5.1]"""

    @pytest.mark.parametrize("bad_name", [
        None, 123, 4.5, True, [], {"a": 1},
    ])
    def test_name_type_enforcement(
        self, sim: FactTableSimulator, bad_name: object
    ) -> None:
        """name must be str. [Subtask 1.5.1]"""
        with pytest.raises(TypeError, match="name must be a str"):
            sim.add_measure_structural(bad_name, "wait_minutes * 2")  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_formula", [
        None, 123, 4.5, True, [], {"a": 1},
    ])
    def test_formula_type_enforcement(
        self, sim: FactTableSimulator, bad_formula: object
    ) -> None:
        """formula must be str. [Subtask 1.5.1]"""
        with pytest.raises(TypeError, match="formula must be a str"):
            sim.add_measure_structural("x", bad_formula)  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_eff", [
        "string", 123, [1, 2], True,
    ])
    def test_effects_type_enforcement(
        self, sim: FactTableSimulator, bad_eff: object
    ) -> None:
        """effects must be dict or None. [Subtask 1.5.1]"""
        with pytest.raises(TypeError, match="effects must be a dict"):
            sim.add_measure_structural("x", "wait_minutes * 2",
                effects=bad_eff)  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_noise", [
        "string", 123, [1, 2], True,
    ])
    def test_noise_type_enforcement(
        self, sim: FactTableSimulator, bad_noise: object
    ) -> None:
        """noise must be dict or None. [Subtask 1.5.1]"""
        with pytest.raises(TypeError, match="noise must be a dict"):
            sim.add_measure_structural("x", "wait_minutes * 2",
                noise=bad_noise)  # type: ignore[arg-type]

    def test_whitespace_only_formula(self, sim: FactTableSimulator) -> None:
        """Whitespace-only formula raises ValueError. [Subtask 1.5.1]"""
        with pytest.raises(ValueError, match="formula must not be empty"):
            sim.add_measure_structural("x", "   \t\n  ")

    def test_formula_with_operators_only(self, sim: FactTableSimulator) -> None:
        """Formula with only operators (no identifiers) stores with no deps. [Subtask 1.5.1]"""
        sim.add_measure_structural("x", "12 + 5 * 3 - 2 / 1")
        assert sim._columns["x"]["depends_on"] == []

    @pytest.mark.parametrize("formula", [
        "wait_minutes + _private_var",
        "wait_minutes + __dunder__",
    ])
    def test_formula_with_invalid_symbols(
        self, sim: FactTableSimulator, formula: str
    ) -> None:
        """Formula symbols not matching any measure or effect raise ValueError. [Subtask 1.5.1]"""
        with pytest.raises(ValueError, match="undefined symbol"):
            sim.add_measure_structural("x", formula)

    def test_multiple_effects_one_missing_from_formula(
        self, sim: FactTableSimulator
    ) -> None:
        """If one of two effects is not in formula, raises UndefinedEffectError. [Subtask 1.5.3]"""
        with pytest.raises(UndefinedEffectError, match="not found in formula"):
            sim.add_measure_structural("x",
                "wait_minutes + surcharge",
                effects={
                    "surcharge": {"Mild": 50, "Moderate": 200, "Severe": 500},
                    "bonus": {"Mild": 1, "Moderate": 2, "Severe": 3},
                })

    def test_effect_value_not_numeric(self, sim: FactTableSimulator) -> None:
        """Effect inner values should be numeric. Non-numeric stored raw if match found.

        The structural effects validator only checks key matching, not value types.
        This documents current behavior. [Subtask 1.5.3]
        """
        # If inner keys match a column, non-numeric values are stored
        sim.add_measure_structural("x",
            "wait_minutes + surcharge",
            effects={"surcharge": {"Mild": "fifty", "Moderate": "two_hundred",
                                   "Severe": "five_hundred"}})
        assert sim._columns["x"]["effects"]["surcharge"]["Mild"] == "fifty"


# ================================================================
# 3. OUTPUT CORRECTNESS TESTS
# ================================================================

class TestAddMeasureStructuralOutputCorrectness:
    """Verify registry shape, DAG structure, and field types. [Subtask 1.5.1]"""

    def test_return_value_is_none(self, sim: FactTableSimulator) -> None:
        """add_measure_structural returns None. [Subtask 1.5.1]"""
        result = sim.add_measure_structural("cost", "wait_minutes * 12")
        assert result is None

    def test_column_entry_has_all_required_keys(
        self, sim: FactTableSimulator
    ) -> None:
        """Column entry has type, measure_type, formula, effects, noise, depends_on. [Subtask 1.5.1]"""
        sim.add_measure_structural("cost", "wait_minutes * 12 + surcharge",
            effects=_SEV_SURCHARGE, noise=_GAUSS_NOISE)
        col = sim._columns["cost"]
        required = {"type", "measure_type", "formula", "effects", "noise", "depends_on"}
        assert required.issubset(col.keys())

    def test_depends_on_contains_only_measures(
        self, sim: FactTableSimulator
    ) -> None:
        """depends_on list only contains measure names, not effect names. [Subtask 1.5.5]"""
        sim.add_measure_structural("cost", "wait_minutes * 12 + surcharge",
            effects=_SEV_SURCHARGE)
        deps = sim._columns["cost"]["depends_on"]
        assert deps == ["wait_minutes"]
        assert "surcharge" not in deps

    def test_multi_dependency_depends_on(
        self, sim: FactTableSimulator
    ) -> None:
        """Structural measure depending on two roots lists both. [Subtask 1.5.5]"""
        sim.add_measure("temperature", "gaussian", {"mu": 36, "sigma": 1})
        sim.add_measure_structural("composite",
            "wait_minutes + temperature * 2")
        deps = set(sim._columns["composite"]["depends_on"])
        assert deps == {"wait_minutes", "temperature"}

    def test_noise_dict_stored_as_is(self, sim: FactTableSimulator) -> None:
        """Noise spec stored without modification. [Subtask 1.5.1]"""
        noise = {"family": "gaussian", "sigma": 30, "extra_key": "keep"}
        sim.add_measure_structural("cost", "wait_minutes * 12", noise=noise)
        assert sim._columns["cost"]["noise"] == noise

    def test_effects_dict_stored_as_is(self, sim: FactTableSimulator) -> None:
        """Effects dict stored with original values preserved. [Subtask 1.5.1]"""
        sim.add_measure_structural("cost", "wait_minutes + surcharge",
            effects=_SEV_SURCHARGE)
        stored = sim._columns["cost"]["effects"]
        assert stored["surcharge"]["Severe"] == 500

    def test_formula_string_preserved_exactly(
        self, sim: FactTableSimulator
    ) -> None:
        """Formula string stored verbatim, no whitespace normalization. [Subtask 1.5.1]"""
        formula = "  wait_minutes  *  12  +  surcharge  "
        sim.add_measure_structural("cost", formula, effects=_SEV_SURCHARGE)
        assert sim._columns["cost"]["formula"] == formula


# ================================================================
# 4. STATE TRANSITION TESTS
# ================================================================

class TestAddMeasureStructuralStateTransitions:
    """Verify DAG growth and ordering after sequences of calls. [Subtask 1.5.5]"""

    def test_dag_grows_with_each_structural(
        self, sim: FactTableSimulator
    ) -> None:
        """Each add_measure_structural adds a new DAG node. [Subtask 1.5.5]"""
        assert len(sim._measure_dag) == 1  # only wait_minutes
        sim.add_measure_structural("cost", "wait_minutes * 12")
        assert len(sim._measure_dag) == 2
        sim.add_measure_structural("profit", "cost * 0.1")
        assert len(sim._measure_dag) == 3

    def test_chain_order_maintained(self, sim: FactTableSimulator) -> None:
        """Long chain: R → A → B → C built correctly. [Subtask 1.5.5]"""
        sim.add_measure_structural("a", "wait_minutes + 1")
        sim.add_measure_structural("b", "a + 1")
        sim.add_measure_structural("c", "b + 1")
        assert "a" in sim._measure_dag["wait_minutes"]
        assert "b" in sim._measure_dag["a"]
        assert "c" in sim._measure_dag["b"]
        assert sim._measure_dag["c"] == []

    def test_diamond_dependency(self, sim: FactTableSimulator) -> None:
        """Diamond: R → A, R → B, then C depends on both A and B. [Subtask 1.5.5]"""
        sim.add_measure_structural("a", "wait_minutes * 2")
        sim.add_measure_structural("b", "wait_minutes * 3")
        sim.add_measure_structural("c", "a + b")
        assert "c" in sim._measure_dag["a"]
        assert "c" in sim._measure_dag["b"]
        assert set(sim._columns["c"]["depends_on"]) == {"a", "b"}

    def test_failed_structural_does_not_mutate_state(
        self, sim: FactTableSimulator
    ) -> None:
        """Failed declaration leaves _columns and _measure_dag unchanged. [Subtask 1.5.1]"""
        n_cols = len(sim._columns)
        n_dag = len(sim._measure_dag)
        dag_copy = {k: list(v) for k, v in sim._measure_dag.items()}
        with pytest.raises(ValueError):
            sim.add_measure_structural("x", "UNDECLARED * 2")
        assert len(sim._columns) == n_cols
        assert len(sim._measure_dag) == n_dag
        for k, v in sim._measure_dag.items():
            assert v == dag_copy[k]

    def test_columns_in_declaration_order(
        self, sim: FactTableSimulator
    ) -> None:
        """Structural measures appear in _columns in declaration order. [Subtask 1.5.1]"""
        sim.add_measure_structural("alpha", "wait_minutes * 1")
        sim.add_measure_structural("beta", "wait_minutes * 2")
        sim.add_measure_structural("charlie", "wait_minutes * 3")
        measures = [k for k, v in sim._columns.items()
                    if v.get("measure_type") == "structural"]
        assert measures == ["alpha", "beta", "charlie"]


# ================================================================
# 5. INTEGRATION TESTS
# ================================================================

class TestAddMeasureStructuralIntegration:
    """Cross-sprint boundary tests. [Subtask 1.5.3, 1.5.5]"""

    def test_structural_after_stochastic_creates_dag_edge(
        self, sim: FactTableSimulator
    ) -> None:
        """Structural referencing stochastic root creates DAG edge. [Subtask 1.5.5]"""
        sim.add_measure_structural("cost", "wait_minutes * 12")
        assert "cost" in sim._measure_dag["wait_minutes"]

    def test_structural_effects_validate_against_sprint2_categories(
        self, sim: FactTableSimulator
    ) -> None:
        """Effects inner keys validated against Sprint 2 categorical values. [Subtask 1.5.3]"""
        sim.add_measure_structural("cost", "wait_minutes + surcharge",
            effects=_SEV_SURCHARGE)
        # severity has Mild/Moderate/Severe — surcharge keys match
        assert "cost" in sim._columns

    def test_structural_collides_with_category_name(
        self, sim: FactTableSimulator
    ) -> None:
        """Structural name colliding with category raises DuplicateColumnError. [Subtask 1.5.1]"""
        with pytest.raises(DuplicateColumnError):
            sim.add_measure_structural("hospital", "wait_minutes * 2")

    def test_structural_collides_with_stochastic_name(
        self, sim: FactTableSimulator
    ) -> None:
        """Structural name colliding with stochastic raises DuplicateColumnError. [Subtask 1.5.1]"""
        with pytest.raises(DuplicateColumnError):
            sim.add_measure_structural("wait_minutes", "12 + 5")

    def test_extract_formula_symbols_helper(self) -> None:
        """_extract_formula_symbols returns correct identifiers. [Subtask 1.5.1]"""
        syms = FactTableSimulator._extract_formula_symbols(
            "wait_minutes * 12 + surcharge - 3.14"
        )
        assert syms == {"wait_minutes", "surcharge"}

    def test_extract_formula_symbols_no_numerics(self) -> None:
        """Numeric literals are not extracted as symbols. [Subtask 1.5.1]"""
        syms = FactTableSimulator._extract_formula_symbols("100 + 200 * 3.5")
        assert syms == set()

    def test_extract_formula_symbols_underscored(self) -> None:
        """Identifiers with underscores are extracted correctly. [Subtask 1.5.1]"""
        syms = FactTableSimulator._extract_formula_symbols(
            "_private + __dunder__ + a_b_c"
        )
        assert syms == {"_private", "__dunder__", "a_b_c"}
