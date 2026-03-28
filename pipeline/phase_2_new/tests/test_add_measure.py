"""
test_add_measure.py — Exhaustive test suite for FactTableSimulator.add_measure().

Sprint 3 Subtask IDs tested: 1.4.1, 1.4.2, 1.4.5

Structure:
  1. Contract tests (rows 3A-1 through 3A-26)
  2. Input validation (type enforcement, boundary, constraints)
  3. Output correctness (registry shape, numerical values, immutability)
  4. State transition (DAG growth, ordering, instance isolation)
  5. Integration (interaction with add_category/add_temporal from Sprint 2)
"""
from __future__ import annotations

import copy
import logging
import math

import pytest

from agpds.exceptions import (
    CyclicDependencyError,
    DuplicateColumnError,
    InvalidParameterError,
    UndefinedEffectError,
)
from agpds.simulator import FactTableSimulator


# ================================================================
# Fixtures
# ================================================================

@pytest.fixture
def sim() -> FactTableSimulator:
    """Bare simulator with categorical columns for the one-shot example."""
    s = FactTableSimulator(500, 42)
    s.add_category("hospital",
                   ["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],
                   [0.3, 0.25, 0.2, 0.15, 0.1], "entity")
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


_CONST_LN = {"mu": 2.8, "sigma": 0.35}
_CONST_G = {"mu": 36.5, "sigma": 0.8}
_FULL_EFFECTS = {
    "mu": {"intercept": 2.8, "effects": {
        "severity": {"Mild": 0.0, "Moderate": 0.4, "Severe": 0.9},
        "hospital": {"Xiehe": 0.2, "Huashan": -0.1, "Ruijin": 0.0,
                     "Tongren": 0.1, "Zhongshan": -0.1}}},
    "sigma": {"intercept": 0.35, "effects": {
        "severity": {"Mild": 0.0, "Moderate": 0.05, "Severe": 0.10}}},
}


# ================================================================
# 1. CONTRACT TESTS — one test per contract table row 3A-1..3A-26
# ================================================================

class TestAddMeasureContract:
    """Every row from the Sprint 3 contract table §3A."""

    # [3A-1] Subtask 1.4.1, 1.4.2, 1.4.5
    def test_3A_01_valid_lognormal_constant(self, sim: FactTableSimulator) -> None:
        """Valid lognormal with constant param_model registers column and DAG root."""
        sim.add_measure("wm", "lognormal", _CONST_LN)
        assert sim._columns["wm"]["type"] == "measure"
        assert sim._columns["wm"]["measure_type"] == "stochastic"
        assert sim._columns["wm"]["family"] == "lognormal"
        assert sim._columns["wm"]["param_model"] == _CONST_LN
        assert sim._measure_dag["wm"] == []

    # [3A-2] Subtask 1.4.1, 1.4.2
    def test_3A_02_valid_gaussian_constant(self, sim: FactTableSimulator) -> None:
        """Gaussian constant form stores correctly; scale is None."""
        sim.add_measure("t", "gaussian", _CONST_G)
        assert sim._columns["t"]["family"] == "gaussian"
        assert sim._columns["t"]["scale"] is None

    # [3A-3] Subtask 1.4.2 (A5 raw storage)
    def test_3A_03_gamma_raw_storage(self, sim: FactTableSimulator) -> None:
        """Gamma: raw dict stored without key validation [A5]."""
        sim.add_measure("g", "gamma", {"shape": 2.0, "rate": 1.0})
        assert sim._columns["g"]["family"] == "gamma"
        assert sim._columns["g"]["param_model"]["shape"] == 2.0

    # [3A-4] Subtask 1.4.2 (A5)
    def test_3A_04_beta_raw_storage(self, sim: FactTableSimulator) -> None:
        """Beta family stored raw."""
        sim.add_measure("b", "beta", {"alpha": 2, "beta": 5})
        assert "b" in sim._measure_dag

    # [3A-5] Subtask 1.4.2 (A5)
    def test_3A_05_uniform_raw(self, sim: FactTableSimulator) -> None:
        """Uniform family stored raw."""
        sim.add_measure("u", "uniform", {"low": 0, "high": 100})
        assert sim._columns["u"]["family"] == "uniform"

    # [3A-6] Subtask 1.4.2 (A5)
    def test_3A_06_poisson_raw(self, sim: FactTableSimulator) -> None:
        """Poisson family stored raw."""
        sim.add_measure("p", "poisson", {"mu": 5})
        assert sim._columns["p"]["family"] == "poisson"

    # [3A-7] Subtask 1.4.2 (A5)
    def test_3A_07_exponential_raw(self, sim: FactTableSimulator) -> None:
        """Exponential family stored raw."""
        sim.add_measure("e", "exponential", {"lambda": 0.5})
        assert sim._columns["e"]["family"] == "exponential"

    # [3A-8] Subtask 1.4.1
    def test_3A_08_unsupported_family(self, sim: FactTableSimulator) -> None:
        """Unsupported family 'weibull' raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported distribution family"):
            sim.add_measure("x", "weibull", {"k": 1.5})

    # [3A-9] Subtask 1.4.1
    def test_3A_09_empty_family(self, sim: FactTableSimulator) -> None:
        """Empty family string raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported"):
            sim.add_measure("x", "", {"mu": 1})

    # [3A-10] Subtask 1.4.1
    def test_3A_10_non_string_family(self, sim: FactTableSimulator) -> None:
        """Non-string family raises TypeError."""
        with pytest.raises(TypeError, match="family must be a str"):
            sim.add_measure("x", 123, {"mu": 1})  # type: ignore[arg-type]

    # [3A-11] Subtask 1.4.2
    def test_3A_11_gaussian_missing_sigma(self, sim: FactTableSimulator) -> None:
        """Gaussian missing 'sigma' raises InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            sim.add_measure("x", "gaussian", {"mu": 2.8})

    # [3A-12] Subtask 1.4.2
    def test_3A_12_lognormal_missing_mu(self, sim: FactTableSimulator) -> None:
        """Lognormal missing 'mu' raises InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            sim.add_measure("x", "lognormal", {"sigma": 0.3})

    # [3A-13] Subtask 1.4.2
    def test_3A_13_non_numeric_scalar(self, sim: FactTableSimulator) -> None:
        """Non-numeric scalar value in param_model raises InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            sim.add_measure("x", "gaussian", {"mu": "abc", "sigma": 0.3})

    # [3A-14] Subtask 1.4.1
    def test_3A_14_param_model_wrong_type(self, sim: FactTableSimulator) -> None:
        """param_model not a dict raises TypeError."""
        with pytest.raises(TypeError, match="param_model must be a dict"):
            sim.add_measure("x", "gaussian", "bad")  # type: ignore[arg-type]

    # [3A-15] Subtask 1.4.1 (A2)
    def test_3A_15_scale_stored_with_debug_log(
        self, sim: FactTableSimulator, caplog: pytest.LogCaptureFixture
    ) -> None:
        """scale=100 stored and DEBUG log emitted."""
        with caplog.at_level(logging.DEBUG):
            sim.add_measure("x", "lognormal", _CONST_LN, scale=100)
        assert sim._columns["x"]["scale"] == 100
        assert "scale=100" in caplog.text
        assert "ignored" in caplog.text

    # [3A-16] Subtask 1.4.1 (A2)
    def test_3A_16_scale_none_default(self, sim: FactTableSimulator) -> None:
        """scale=None (default) stored; no scale-warning log."""
        sim.add_measure("x", "lognormal", _CONST_LN, scale=None)
        assert sim._columns["x"]["scale"] is None

    # [3A-17] Subtask 1.4.1
    def test_3A_17_duplicate_measure(self, sim: FactTableSimulator) -> None:
        """Calling add_measure twice with same name raises DuplicateColumnError."""
        sim.add_measure("wm", "lognormal", _CONST_LN)
        with pytest.raises(DuplicateColumnError):
            sim.add_measure("wm", "gaussian", _CONST_G)

    # [3A-18] Subtask 1.4.1
    def test_3A_18_collision_with_category(self, sim: FactTableSimulator) -> None:
        """Measure name collides with existing category raises DuplicateColumnError."""
        with pytest.raises(DuplicateColumnError):
            sim.add_measure("hospital", "gaussian", _CONST_G)

    # [3A-19] Subtask 1.4.2
    def test_3A_19_intercept_effects_valid(self, sim: FactTableSimulator) -> None:
        """Full intercept+effects form with valid predictor columns stores correctly."""
        sim.add_measure("wm", "lognormal", _FULL_EFFECTS)
        assert "wm" in sim._columns
        assert "wm" in sim._measure_dag

    # [3A-20] Subtask 1.4.2
    def test_3A_20_effects_undeclared_column(self, sim: FactTableSimulator) -> None:
        """Effects referencing undeclared column raises UndefinedEffectError."""
        with pytest.raises(UndefinedEffectError):
            sim.add_measure("wm", "lognormal", {
                "mu": {"intercept": 2.8,
                       "effects": {"NONEXISTENT": {"A": 0.0}}},
                "sigma": 0.35,
            })

    # [3A-21] Subtask 1.4.2
    def test_3A_21_effects_unknown_value(self, sim: FactTableSimulator) -> None:
        """Effect value key not in column's value set raises UndefinedEffectError."""
        with pytest.raises(UndefinedEffectError):
            sim.add_measure("wm", "lognormal", {
                "mu": {"intercept": 2.8,
                       "effects": {"severity": {"Mild": 0.0, "Moderate": 0.4,
                                                "UNKNOWN_VALUE": 0.9}}},
                "sigma": 0.35,
            })

    # [3A-22] Subtask 1.4.1 (BLOCKED)
    def test_3A_22_mixture_blocked(self, sim: FactTableSimulator) -> None:
        """Mixture family raises NotImplementedError."""
        with pytest.raises(NotImplementedError, match="BLOCKED: 1.4.4"):
            sim.add_measure("x", "mixture", {"components": []})

    # [3A-23] Subtask 1.4.1
    def test_3A_23_non_string_name(self, sim: FactTableSimulator) -> None:
        """Non-string name raises TypeError."""
        with pytest.raises(TypeError, match="name must be a str"):
            sim.add_measure(123, "gaussian", _CONST_G)  # type: ignore[arg-type]

    # [3A-24] Subtask 1.4.1
    def test_3A_24_non_numeric_scale(self, sim: FactTableSimulator) -> None:
        """Non-numeric scale raises TypeError."""
        with pytest.raises(TypeError, match="scale must be"):
            sim.add_measure("x", "gaussian", _CONST_G, scale="bad")  # type: ignore[arg-type]

    # [3A-25] Subtask 1.4.2
    def test_3A_25_extra_keys_tolerated(self, sim: FactTableSimulator) -> None:
        """Extra param key for validated family is tolerated."""
        sim.add_measure("x", "gaussian", {"mu": 1, "sigma": 1, "extra": 99})
        assert sim._columns["x"]["param_model"]["extra"] == 99

    # [3A-26] Subtask 1.4.2
    def test_3A_26_mixed_form(self, sim: FactTableSimulator) -> None:
        """Mixed form: mu has effects, sigma is constant scalar."""
        sim.add_measure("x", "lognormal", {
            "mu": {"intercept": 2.8,
                   "effects": {"severity": {"Mild": 0.0, "Moderate": 0.4,
                                            "Severe": 0.9}}},
            "sigma": 0.35,
        })
        pm = sim._columns["x"]["param_model"]
        assert isinstance(pm["mu"], dict)
        assert isinstance(pm["sigma"], (int, float))


# ================================================================
# 2. INPUT VALIDATION TESTS — type enforcement, boundary, constraints
# ================================================================

class TestAddMeasureInputValidation:
    """Exhaustive type, boundary, and constraint checks. [Subtask 1.4.1]"""

    # ----- Type enforcement for every parameter -----

    @pytest.mark.parametrize("bad_name", [
        None, 123, 4.5, True, [], {"a": 1}, b"bytes",
    ])
    def test_name_type_enforcement(
        self, sim: FactTableSimulator, bad_name: object
    ) -> None:
        """name must be str; reject all non-str types. [Subtask 1.4.1]"""
        with pytest.raises(TypeError, match="name must be a str"):
            sim.add_measure(bad_name, "gaussian", _CONST_G)  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_family", [
        None, 123, 4.5, True, [], {"a": 1},
    ])
    def test_family_type_enforcement(
        self, sim: FactTableSimulator, bad_family: object
    ) -> None:
        """family must be str. [Subtask 1.4.1]"""
        with pytest.raises(TypeError, match="family must be a str"):
            sim.add_measure("x", bad_family, _CONST_G)  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_pm", [
        "string", 123, [1, 2], None, True,
    ])
    def test_param_model_type_enforcement(
        self, sim: FactTableSimulator, bad_pm: object
    ) -> None:
        """param_model must be dict. [Subtask 1.4.1]"""
        with pytest.raises(TypeError, match="param_model must be a dict"):
            sim.add_measure("x", "gaussian", bad_pm)  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_scale", [
        "bad", [1], {"a": 1}, True, False,
    ])
    def test_scale_type_enforcement(
        self, sim: FactTableSimulator, bad_scale: object
    ) -> None:
        """scale must be float/int/None; reject bool and non-numeric. [Subtask 1.4.1]"""
        with pytest.raises(TypeError, match="scale must be"):
            sim.add_measure("x", "gaussian", _CONST_G, scale=bad_scale)  # type: ignore[arg-type]

    # ----- Unsupported family strings -----

    @pytest.mark.parametrize("bad_fam", [
        "weibull", "cauchy", "Gaussian", "LOGNORMAL", " gaussian", "gaussian ",
    ])
    def test_unsupported_family_strings(
        self, sim: FactTableSimulator, bad_fam: str
    ) -> None:
        """Case-sensitive exact match required. [Subtask 1.4.1]"""
        with pytest.raises(ValueError, match="Unsupported"):
            sim.add_measure("x", bad_fam, {"mu": 1, "sigma": 1})

    # ----- Boundary: empty param_model -----

    def test_empty_param_model_validated_family(
        self, sim: FactTableSimulator
    ) -> None:
        """Empty param_model for gaussian raises InvalidParameterError. [Subtask 1.4.2]"""
        with pytest.raises(InvalidParameterError):
            sim.add_measure("x", "gaussian", {})

    def test_empty_param_model_non_validated_family(
        self, sim: FactTableSimulator
    ) -> None:
        """Empty param_model for gamma is accepted (raw storage). [Subtask 1.4.2]"""
        sim.add_measure("x", "gamma", {})
        assert sim._columns["x"]["param_model"] == {}

    # ----- Scale boundary values -----

    @pytest.mark.parametrize("scale_val", [0, 0.0, -1, -100.5, 1e-10, 1e10])
    def test_scale_numeric_boundary_values(
        self, sim: FactTableSimulator, scale_val: float
    ) -> None:
        """Any numeric scale is accepted and stored. [Subtask 1.4.1, A2]"""
        sim.add_measure("x", "lognormal", _CONST_LN, scale=scale_val)
        assert sim._columns["x"]["scale"] == scale_val

    # ----- NaN/Inf in param_model -----

    def test_nan_param_value_non_validated_family(
        self, sim: FactTableSimulator
    ) -> None:
        """NaN param value for non-validated family is stored raw. [Subtask 1.4.2]"""
        # SPEC_AMBIGUOUS: NaN in param values — no spec guidance
        sim.add_measure("x", "gamma", {"shape": float("nan")})
        assert math.isnan(sim._columns["x"]["param_model"]["shape"])

    def test_inf_param_value_non_validated_family(
        self, sim: FactTableSimulator
    ) -> None:
        """Inf param value for non-validated family is stored raw. [Subtask 1.4.2]"""
        sim.add_measure("x", "gamma", {"shape": float("inf")})
        assert math.isinf(sim._columns["x"]["param_model"]["shape"])


# ================================================================
# 3. OUTPUT CORRECTNESS TESTS — registry shape, immutability, values
# ================================================================

class TestAddMeasureOutputCorrectness:
    """Verify return values, registry shape, and immutability. [Subtask 1.4.5]"""

    def test_return_value_is_none(self, sim: FactTableSimulator) -> None:
        """add_measure returns None. [Subtask 1.4.1]"""
        result = sim.add_measure("x", "gaussian", _CONST_G)
        assert result is None

    def test_column_entry_has_all_required_keys(
        self, sim: FactTableSimulator
    ) -> None:
        """Column entry contains type, measure_type, family, param_model, scale. [Subtask 1.4.5]"""
        sim.add_measure("wm", "lognormal", _CONST_LN, scale=10)
        col = sim._columns["wm"]
        required_keys = {"type", "measure_type", "family", "param_model", "scale"}
        assert required_keys.issubset(col.keys())

    def test_dag_entry_is_empty_list(self, sim: FactTableSimulator) -> None:
        """DAG root has empty adjacency list (no downstream deps yet). [Subtask 1.4.5]"""
        sim.add_measure("wm", "lognormal", _CONST_LN)
        assert isinstance(sim._measure_dag["wm"], list)
        assert len(sim._measure_dag["wm"]) == 0

    def test_no_incoming_edges_for_root(self, sim: FactTableSimulator) -> None:
        """No other node in DAG lists the new root as a successor. [Subtask 1.4.5]"""
        sim.add_measure("m1", "gaussian", _CONST_G)
        sim.add_measure("m2", "gamma", {"shape": 2, "rate": 1})
        for node, succs in sim._measure_dag.items():
            assert "m1" not in succs or node == "m1"
            assert "m2" not in succs or node == "m2"

    def test_param_model_stored_by_reference_not_deep_copy(
        self, sim: FactTableSimulator
    ) -> None:
        """Mutating original param_model dict DOES affect stored value.

        This documents current behavior (no deep-copy). If immutability
        is required, a future sprint should add defensive copying.
        """
        pm = {"mu": 1.0, "sigma": 2.0}
        sim.add_measure("x", "gaussian", pm)
        pm["mu"] = 999.0
        # Verifies that the simulator stores the reference, not a copy
        assert sim._columns["x"]["param_model"]["mu"] == 999.0

    def test_numerical_correctness_scale_stored_exactly(
        self, sim: FactTableSimulator
    ) -> None:
        """Scale value stored with exact float representation. [Subtask 1.4.1]"""
        sim.add_measure("x", "lognormal", _CONST_LN, scale=3.14159)
        assert sim._columns["x"]["scale"] == pytest.approx(3.14159)


# ================================================================
# 4. STATE TRANSITION TESTS — DAG growth, ordering, isolation
# ================================================================

class TestAddMeasureStateTransitions:
    """Verify state after sequences of add_measure calls. [Subtask 1.4.5]"""

    def test_multiple_roots_coexist(self, sim: FactTableSimulator) -> None:
        """Multiple stochastic measures register as independent roots. [Subtask 1.4.5]"""
        sim.add_measure("m1", "gaussian", _CONST_G)
        sim.add_measure("m2", "lognormal", _CONST_LN)
        sim.add_measure("m3", "gamma", {"shape": 1, "rate": 1})
        assert len(sim._measure_dag) == 3
        for m in ["m1", "m2", "m3"]:
            assert sim._measure_dag[m] == []

    def test_columns_in_insertion_order(self, sim: FactTableSimulator) -> None:
        """Measure columns appear in _columns in declaration order. [Subtask 1.4.5]"""
        sim.add_measure("alpha", "gaussian", _CONST_G)
        sim.add_measure("beta", "lognormal", _CONST_LN)
        sim.add_measure("charlie", "gamma", {"shape": 1, "rate": 1})
        col_names = list(sim._columns.keys())
        # Categories come first (from fixture), then measures
        measure_names = [n for n in col_names if sim._columns[n]["type"] == "measure"]
        assert measure_names == ["alpha", "beta", "charlie"]

    def test_instance_isolation(self) -> None:
        """Two simulator instances have independent state. [Subtask 1.1.2]"""
        s1 = FactTableSimulator(100, 1)
        s2 = FactTableSimulator(200, 2)
        s1.add_category("a", ["X", "Y"], [1, 1], "g")
        s1.add_measure("m1", "gaussian", _CONST_G)
        assert "m1" not in s2._columns
        assert "m1" not in s2._measure_dag

    def test_failed_add_does_not_mutate_state(
        self, sim: FactTableSimulator
    ) -> None:
        """A failed add_measure leaves _columns and _measure_dag unchanged. [Subtask 1.4.1]"""
        n_cols_before = len(sim._columns)
        n_dag_before = len(sim._measure_dag)
        with pytest.raises(ValueError):
            sim.add_measure("x", "weibull", {"k": 1})
        assert len(sim._columns) == n_cols_before
        assert len(sim._measure_dag) == n_dag_before


# ================================================================
# 5. INTEGRATION TESTS — interaction with Sprint 2 modules
# ================================================================

class TestAddMeasureIntegration:
    """Cross-sprint boundary tests. [Subtask 1.4.2]"""

    def test_effects_validate_against_categories(
        self, sim: FactTableSimulator
    ) -> None:
        """Intercept+effects form validates column existence via Sprint 2 registry. [Subtask 1.4.2]"""
        sim.add_measure("wm", "lognormal", _FULL_EFFECTS)
        assert "wm" in sim._columns

    def test_effects_reject_temporal_column_as_predictor(
        self, sim: FactTableSimulator
    ) -> None:
        """Temporal column (non-categorical) in effects raises UndefinedEffectError. [Subtask 1.4.2]"""
        sim.add_temporal("visit_date", "2024-01-01", "2024-06-30", "daily")
        with pytest.raises(UndefinedEffectError):
            sim.add_measure("x", "gaussian", {
                "mu": {"intercept": 1, "effects": {"visit_date": {"2024-01-01": 0.1}}},
                "sigma": 1.0,
            })

    def test_effects_validate_against_temporal_derived(
        self, sim: FactTableSimulator
    ) -> None:
        """Temporal-derived column (non-categorical) in effects raises. [Subtask 1.4.2]"""
        sim.add_temporal("visit_date", "2024-01-01", "2024-06-30", "daily",
                         derive=["month"])
        with pytest.raises(UndefinedEffectError):
            sim.add_measure("x", "gaussian", {
                "mu": {"intercept": 1, "effects": {"month": {"1": 0.1}}},
                "sigma": 1.0,
            })

    def test_measure_name_cannot_collide_with_temporal(
        self, sim: FactTableSimulator
    ) -> None:
        """Measure name colliding with temporal column raises DuplicateColumnError. [Subtask 1.4.1]"""
        sim.add_temporal("visit_date", "2024-01-01", "2024-06-30", "daily")
        with pytest.raises(DuplicateColumnError):
            sim.add_measure("visit_date", "gaussian", _CONST_G)

    def test_measure_name_cannot_collide_with_derived(
        self, sim: FactTableSimulator
    ) -> None:
        """Measure name colliding with derived temporal column raises. [Subtask 1.4.1]"""
        sim.add_temporal("visit_date", "2024-01-01", "2024-06-30", "daily",
                         derive=["month"])
        with pytest.raises(DuplicateColumnError):
            sim.add_measure("month", "gaussian", _CONST_G)
