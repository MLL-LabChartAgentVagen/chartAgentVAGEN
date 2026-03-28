"""
Sprint 4 Test Suite — test_simulator_sprint4.py

Covers subtask IDs: 1.7.4, 1.8.1, 1.8.2, 1.8.3, 1.8.5, 1.9.1,
                     3.1.1, 3.1.2, 3.2.1

Sprint 4 modifies only agpds/simulator.py (no new modules), so this
is the single test file for the entire sprint.

Test categories (executed in this order):
  1. Contract tests — one per Message 1 contract row
  2. Input validation tests — exhaustive type/boundary/constraint checks
  3. Output correctness tests — return value shape, types, numerical accuracy
  4. State transition tests — internal registries after method calls
  5. Integration tests — cross-sprint boundary verification
"""
from __future__ import annotations

import math
import sys

sys.path.insert(0, "/home/claude")

import pytest

from agpds.exceptions import (
    CyclicDependencyError,
    DuplicateColumnError,
    InvalidParameterError,
    NonRootDependencyError,
)
from agpds.simulator import FactTableSimulator


# ================================================================
# Shared Fixtures
# ================================================================

@pytest.fixture
def fresh_sim() -> FactTableSimulator:
    """A bare simulator with zero declarations."""
    return FactTableSimulator(target_rows=500, seed=42)


@pytest.fixture
def sim_cats() -> FactTableSimulator:
    """Simulator with the one-shot example categorical columns only."""
    sim = FactTableSimulator(target_rows=500, seed=42)
    sim.add_category("hospital", values=["Xiehe","Huashan","Ruijin","Zhongshan","Tongji"], weights=[0.25,0.20,0.20,0.20,0.15], group="entity")
    sim.add_category("department", values=["Cardiology","Orthopedics","Neurology","Oncology"], weights={"Xiehe":[0.30,0.25,0.25,0.20],"Huashan":[0.20,0.30,0.30,0.20],"Ruijin":[0.25,0.25,0.25,0.25],"Zhongshan":[0.35,0.20,0.20,0.25],"Tongji":[0.25,0.25,0.30,0.20]}, group="entity", parent="hospital")
    sim.add_category("severity", values=["Mild","Moderate","Severe"], weights=[0.5,0.35,0.15], group="patient")
    sim.add_category("payment_method", values=["Insurance","Self-pay","Government"], weights=[0.6,0.3,0.1], group="payment")
    return sim


@pytest.fixture
def sim_temporal(sim_cats) -> FactTableSimulator:
    sim_cats.add_temporal("visit_date", start="2024-01-01", end="2024-06-30", freq="daily", derive=["day_of_week","month"])
    return sim_cats


@pytest.fixture
def sim_rels(sim_temporal) -> FactTableSimulator:
    sim_temporal.declare_orthogonal("entity","patient", rationale="Severity is independent of hospital/department")
    sim_temporal.add_group_dependency("payment_method", on=["severity"], conditional_weights={"Mild":{"Insurance":0.45,"Self-pay":0.45,"Government":0.10},"Moderate":{"Insurance":0.65,"Self-pay":0.25,"Government":0.10},"Severe":{"Insurance":0.80,"Self-pay":0.10,"Government":0.10}})
    return sim_temporal


@pytest.fixture
def sim_full(sim_rels) -> FactTableSimulator:
    sim_rels.add_measure("wait_minutes", family="gaussian", param_model={"mu":{"intercept":45.0,"effects":{"severity":{"Mild":-10.0,"Moderate":0.0,"Severe":20.0},"hospital":{"Xiehe":5.0,"Huashan":-3.0,"Ruijin":0.0,"Zhongshan":2.0,"Tongji":-4.0}}},"sigma":{"intercept":15.0,"effects":{"severity":{"Mild":-3.0,"Moderate":0.0,"Severe":5.0}}}})
    sim_rels.add_measure_structural("cost", formula="wait_minutes * 12 + severity_surcharge", effects={"severity_surcharge":{"Mild":50,"Moderate":200,"Severe":500}}, noise={"family":"gaussian","sigma":30})
    sim_rels.add_measure_structural("satisfaction", formula="100 - cost / 50", noise={"family":"gaussian","sigma":8})
    return sim_rels


# Helper for conditional weights in 1.7.4 tests
_CW = {"Mild":{"Insurance":0.5,"Self-pay":0.3,"Government":0.2},"Moderate":{"Insurance":0.6,"Self-pay":0.3,"Government":0.1},"Severe":{"Insurance":0.8,"Self-pay":0.1,"Government":0.1}}


# ################################################################
# 1. CONTRACT TESTS
# ################################################################

class TestContract_1_7_4:
    def test_ct_dependency_after_orthogonal_raises(self, sim_temporal):
        """[1.7.4 row 1]"""
        sim_temporal.declare_orthogonal("payment","patient", rationale="test")
        with pytest.raises(ValueError, match="orthogonal"):
            sim_temporal.add_group_dependency("payment_method", on=["severity"], conditional_weights=_CW)

    def test_ct_orthogonal_after_dependency_raises(self, sim_temporal):
        """[1.7.4 row 2]"""
        sim_temporal.add_group_dependency("payment_method", on=["severity"], conditional_weights=_CW)
        with pytest.raises(ValueError, match="dependency"):
            sim_temporal.declare_orthogonal("payment","patient", rationale="test")

    def test_ct_different_group_pairs_no_conflict(self, sim_temporal):
        """[1.7.4 row 3]"""
        sim_temporal.declare_orthogonal("entity","patient", rationale="independence")
        sim_temporal.add_group_dependency("payment_method", on=["severity"], conditional_weights=_CW)
        assert len(sim_temporal._group_dependencies) == 1


class TestContract_inject_pattern:
    def test_ct_valid_outlier_entity_stored(self, sim_full):
        """[1.8.1/1.8.5 row 1]"""
        sim_full.inject_pattern("outlier_entity", target="hospital == 'Xiehe' & severity == 'Severe'", col="wait_minutes", params={"z_score":3.0})
        assert len(sim_full._patterns) == 1
        assert sim_full._patterns[0]["type"] == "outlier_entity"

    def test_ct_valid_trend_break_stored(self, sim_full):
        """[1.8.1/1.8.5 row 2]"""
        sim_full.inject_pattern("trend_break", target="hospital == 'Huashan'", col="wait_minutes", params={"break_point":"2024-03-15","magnitude":0.4})
        assert len(sim_full._patterns) == 1

    def test_ct_convergence_arbitrary_params_stored(self, sim_full):
        """[1.8.1/1.8.5 row 3]"""
        sim_full.inject_pattern("convergence", target="hospital == 'X'", col="cost", params={"anything":1})
        assert sim_full._patterns[0]["params"] == {"anything":1}

    def test_ct_ranking_reversal_empty_params_stored(self, sim_full):
        """[1.8.1/1.8.5 row 4]"""
        sim_full.inject_pattern("ranking_reversal", target="hospital == 'X'", col="cost", params={})
        assert sim_full._patterns[0]["params"] == {}

    def test_ct_dominance_shift_stored(self, sim_full):
        """[1.8.1/1.8.5 row 5]"""
        sim_full.inject_pattern("dominance_shift", target="hospital == 'X'", col="cost", params={"x":1})
        assert len(sim_full._patterns) == 1

    def test_ct_seasonal_anomaly_stored(self, sim_full):
        """[1.8.1/1.8.5 row 6]"""
        sim_full.inject_pattern("seasonal_anomaly", target="hospital == 'X'", col="cost", params={"x":1})
        assert len(sim_full._patterns) == 1

    def test_ct_unknown_type_raises(self, sim_full):
        """[1.8.1 row 7]"""
        with pytest.raises(ValueError, match="Unknown pattern type"):
            sim_full.inject_pattern("unknown_type", target="a == 'b'", col="wait_minutes", params={})

    def test_ct_empty_type_raises(self, sim_full):
        """[1.8.1 row 8]"""
        with pytest.raises(ValueError, match="Unknown pattern type"):
            sim_full.inject_pattern("", target="a == 'b'", col="wait_minutes", params={})

    # FIX: [self-review item 7] — All TypeError tests now verify the
    # reported type name in the error message, not just the prefix.
    def test_ct_type_int_raises_typeerror(self, sim_full):
        """[1.8.1 row 9]"""
        with pytest.raises(TypeError, match=r"type must be a str, got int"):
            sim_full.inject_pattern(123, target="a == 'b'", col="wait_minutes", params={})

    def test_ct_target_int_raises_typeerror(self, sim_full):
        """[1.8.1 row 10] — FIX: [self-review item 7] verifies 'got int'."""
        with pytest.raises(TypeError, match=r"target must be a str, got int"):
            sim_full.inject_pattern("outlier_entity", target=123, col="wait_minutes", params={"z_score":3.0})

    def test_ct_col_int_raises_typeerror(self, sim_full):
        """[1.8.1 row 11]"""
        with pytest.raises(TypeError, match=r"col must be a str, got int"):
            sim_full.inject_pattern("outlier_entity", target="a == 'b'", col=123, params={"z_score":3.0})

    def test_ct_params_str_raises_typeerror(self, sim_full):
        """[1.8.1 row 12]"""
        with pytest.raises(TypeError, match=r"params must be a dict, got str"):
            sim_full.inject_pattern("outlier_entity", target="a == 'b'", col="wait_minutes", params="not_a_dict")

    def test_ct_params_list_raises_typeerror(self, sim_full):
        """[1.8.1 row 13]"""
        with pytest.raises(TypeError, match=r"params must be a dict, got list"):
            sim_full.inject_pattern("outlier_entity", target="a == 'b'", col="wait_minutes", params=[1,2])

    def test_ct_empty_target_raises(self, sim_full):
        """[1.8.2 row 14]"""
        with pytest.raises(ValueError, match="non-empty"):
            sim_full.inject_pattern("outlier_entity", target="", col="wait_minutes", params={"z_score":3.0})

    def test_ct_undeclared_col_raises(self, sim_full):
        """[1.8.3 row 15]"""
        with pytest.raises(ValueError, match="not declared"):
            sim_full.inject_pattern("outlier_entity", target="a == 'b'", col="nonexistent_col", params={"z_score":3.0})

    def test_ct_categorical_col_raises(self, sim_full):
        """[1.8.3 row 16]"""
        with pytest.raises(ValueError, match="not.*measure"):
            sim_full.inject_pattern("outlier_entity", target="a == 'b'", col="hospital", params={"z_score":3.0})

    def test_ct_temporal_col_raises(self, sim_full):
        """[1.8.3 row 17]"""
        with pytest.raises(ValueError, match="not.*measure"):
            sim_full.inject_pattern("outlier_entity", target="a == 'b'", col="visit_date", params={"z_score":3.0})

    def test_ct_outlier_entity_missing_zscore(self, sim_full):
        """[1.8.1 row 18]"""
        with pytest.raises(ValueError, match="z_score"):
            sim_full.inject_pattern("outlier_entity", target="a == 'b'", col="wait_minutes", params={})

    def test_ct_outlier_entity_extra_keys_accepted(self, sim_full):
        """[1.8.1 row 19]"""
        sim_full.inject_pattern("outlier_entity", target="a == 'b'", col="wait_minutes", params={"z_score":3.0,"extra":1})
        assert len(sim_full._patterns) == 1

    def test_ct_trend_break_missing_magnitude(self, sim_full):
        """[1.8.1 row 20]"""
        with pytest.raises(ValueError, match="magnitude"):
            sim_full.inject_pattern("trend_break", target="a == 'b'", col="wait_minutes", params={"break_point":"2024-03-15"})

    def test_ct_trend_break_missing_breakpoint(self, sim_full):
        """[1.8.1 row 21]"""
        with pytest.raises(ValueError, match="break_point"):
            sim_full.inject_pattern("trend_break", target="a == 'b'", col="wait_minutes", params={"magnitude":0.4})

    def test_ct_trend_break_wrong_keys(self, sim_full):
        """[1.8.1 row 22]"""
        with pytest.raises(ValueError, match="missing"):
            sim_full.inject_pattern("trend_break", target="a == 'b'", col="wait_minutes", params={"z_score":3})

    def test_ct_two_patterns_increment(self, sim_full):
        """[1.8.5 row 23]"""
        sim_full.inject_pattern("outlier_entity", target="a == 'b'", col="wait_minutes", params={"z_score":3.0})
        sim_full.inject_pattern("trend_break", target="c == 'd'", col="wait_minutes", params={"break_point":"2024-03-15","magnitude":0.4})
        assert len(sim_full._patterns) == 2

    def test_ct_type_none_raises(self, sim_full):
        """[1.8.1 row 24]"""
        with pytest.raises(TypeError):
            sim_full.inject_pattern(None, target="a == 'b'", col="wait_minutes", params={})

    def test_ct_target_none_raises(self, sim_full):
        """[1.8.1 row 25]"""
        with pytest.raises(TypeError):
            sim_full.inject_pattern("outlier_entity", target=None, col="wait_minutes", params={"z_score":3.0})


class TestContract_set_realism:
    def test_ct_valid_rates_no_censoring(self, fresh_sim):
        """[1.9.1 row 1]"""
        fresh_sim.set_realism(0.05, 0.02)
        cfg = fresh_sim._realism_config
        assert cfg["missing_rate"] == pytest.approx(0.05)
        assert cfg["dirty_rate"] == pytest.approx(0.02)
        assert cfg["censoring"] is None

    def test_ct_valid_rates_with_censoring(self, fresh_sim):
        """[1.9.1 row 2]"""
        fresh_sim.set_realism(0.05, 0.02, {"threshold":100})
        assert fresh_sim._realism_config["censoring"] == {"threshold":100}

    def test_ct_boundary_zero_rates(self, fresh_sim):
        """[1.9.1 row 3]"""
        fresh_sim.set_realism(0.0, 0.0)
        assert fresh_sim._realism_config["missing_rate"] == 0.0

    def test_ct_boundary_max_rates(self, fresh_sim):
        """[1.9.1 row 4]"""
        fresh_sim.set_realism(1.0, 1.0)
        assert fresh_sim._realism_config["missing_rate"] == 1.0

    def test_ct_missing_rate_above_1(self, fresh_sim):
        """[1.9.1 row 5]"""
        with pytest.raises(ValueError, match="missing_rate"):
            fresh_sim.set_realism(1.5, 0.0)

    def test_ct_dirty_rate_above_1(self, fresh_sim):
        """[1.9.1 row 6]"""
        with pytest.raises(ValueError, match="dirty_rate"):
            fresh_sim.set_realism(0.0, 1.5)

    def test_ct_missing_rate_negative(self, fresh_sim):
        """[1.9.1 row 7]"""
        with pytest.raises(ValueError, match="missing_rate"):
            fresh_sim.set_realism(-0.01, 0.0)

    def test_ct_dirty_rate_negative(self, fresh_sim):
        """[1.9.1 row 8]"""
        with pytest.raises(ValueError, match="dirty_rate"):
            fresh_sim.set_realism(0.0, -0.01)

    def test_ct_missing_rate_str(self, fresh_sim):
        """[1.9.1 row 9]"""
        with pytest.raises(TypeError, match="missing_rate"):
            fresh_sim.set_realism("0.05", 0.02)

    def test_ct_dirty_rate_str(self, fresh_sim):
        """[1.9.1 row 10]"""
        with pytest.raises(TypeError, match="dirty_rate"):
            fresh_sim.set_realism(0.05, "0.02")

    def test_ct_missing_rate_none(self, fresh_sim):
        """[1.9.1 row 11]"""
        with pytest.raises(TypeError, match="missing_rate"):
            fresh_sim.set_realism(None, 0.02)

    def test_ct_missing_rate_bool(self, fresh_sim):
        """[1.9.1 row 12]"""
        with pytest.raises(TypeError, match="bool"):
            fresh_sim.set_realism(True, 0.02)

    def test_ct_censoring_str(self, fresh_sim):
        """[1.9.1 row 13]"""
        with pytest.raises(TypeError, match="censoring"):
            fresh_sim.set_realism(0.05, 0.02, "not_dict")

    def test_ct_censoring_list(self, fresh_sim):
        """[1.9.1 row 14]"""
        with pytest.raises(TypeError, match="censoring"):
            fresh_sim.set_realism(0.05, 0.02, [1,2])

    def test_ct_second_call_overwrites(self, fresh_sim):
        """[1.9.1 row 15]"""
        fresh_sim.set_realism(0.05, 0.02)
        fresh_sim.set_realism(0.10, 0.08, {"x":1})
        cfg = fresh_sim._realism_config
        assert cfg["missing_rate"] == pytest.approx(0.10)
        assert cfg["dirty_rate"] == pytest.approx(0.08)
        assert cfg["censoring"] == {"x":1}


class TestContract_build_full_dag:
    def test_ct_one_shot_10_nodes_correct_edges(self, sim_full):
        """[3.1.1 row 1]"""
        dag = sim_full._build_full_dag()
        assert set(dag.keys()) == {"hospital","department","severity","payment_method","visit_date","day_of_week","month","wait_minutes","cost","satisfaction"}
        assert "department" in dag["hospital"]
        assert "payment_method" in dag["severity"]
        assert "day_of_week" in dag["visit_date"]
        assert "month" in dag["visit_date"]
        assert "wait_minutes" in dag["severity"]
        assert "wait_minutes" in dag["hospital"]

    def test_ct_minimal_root_plus_measure(self, fresh_sim):
        """[3.1.1 row 2]"""
        fresh_sim.add_category("c", ["A","B"], [1,1], "g")
        fresh_sim.add_measure("m", "gaussian", param_model={"mu":{"intercept":0,"effects":{"c":{"A":1,"B":-1}}},"sigma":1.0})
        dag = fresh_sim._build_full_dag()
        assert set(dag.keys()) == {"c","m"}
        assert "m" in dag["c"]

    def test_ct_empty_simulator(self, fresh_sim):
        """[3.1.1 row 3]"""
        assert fresh_sim._build_full_dag() == {}

    def test_ct_categories_only(self, sim_cats):
        """[3.1.1 row 4]"""
        dag = sim_cats._build_full_dag()
        assert "department" in dag["hospital"]
        assert dag["severity"] == []

    def test_ct_temporal_only(self, fresh_sim):
        """[3.1.1 row 5]"""
        fresh_sim.add_temporal("ts","2024-01-01","2024-12-31","daily",derive=["day_of_week","quarter"])
        dag = fresh_sim._build_full_dag()
        assert "day_of_week" in dag["ts"]
        assert "quarter" in dag["ts"]

    def test_ct_stochastic_two_categorical_effects(self, fresh_sim):
        """[3.1.1 row 6]"""
        fresh_sim.add_category("c1",["A","B"],[1,1],"g1")
        fresh_sim.add_category("c2",["X","Y"],[1,1],"g2")
        fresh_sim.add_measure("m","gaussian",param_model={"mu":{"intercept":0,"effects":{"c1":{"A":1,"B":-1},"c2":{"X":2,"Y":-2}}},"sigma":1.0})
        dag = fresh_sim._build_full_dag()
        assert "m" in dag["c1"]
        assert "m" in dag["c2"]

    def test_ct_structural_effects_edge(self, sim_full):
        """[3.1.1 row 7]"""
        dag = sim_full._build_full_dag()
        assert "cost" in dag["severity"]


class TestContract_topological_sort:
    def test_ct_one_shot_ordering(self, sim_full):
        """[3.1.2 row 1]"""
        dag = sim_full._build_full_dag()
        order = sim_full._topological_sort(dag)
        idx = {name:i for i,name in enumerate(order)}
        assert idx["hospital"] < idx["department"]
        assert idx["severity"] < idx["payment_method"]
        assert idx["visit_date"] < idx["day_of_week"]
        assert idx["visit_date"] < idx["month"]
        assert idx["wait_minutes"] < idx["cost"]
        assert idx["cost"] < idx["satisfaction"]

    def test_ct_lexicographic_tie(self, fresh_sim):
        """[3.1.2 row 2]"""
        assert fresh_sim._topological_sort({"B":[],"A":[],"C":[]}) == ["A","B","C"]

    def test_ct_single_node(self, fresh_sim):
        """[3.1.2 row 3]"""
        assert fresh_sim._topological_sort({"node":[]}) == ["node"]

    def test_ct_empty(self, fresh_sim):
        """[3.1.2 row 4]"""
        assert fresh_sim._topological_sort({}) == []

    def test_ct_cycle_raises(self, fresh_sim):
        """[3.1.2 row 5]"""
        with pytest.raises(CyclicDependencyError):
            fresh_sim._topological_sort({"A":["B"],"B":["A"]})

    def test_ct_linear_chain(self, fresh_sim):
        """[3.1.2 row 6]"""
        assert fresh_sim._topological_sort({"A":["B"],"B":["C"],"C":[]}) == ["A","B","C"]

    def test_ct_diamond(self, fresh_sim):
        """[3.1.2 row 7]"""
        assert fresh_sim._topological_sort({"A":["B","C"],"B":["D"],"C":["D"],"D":[]}) == ["A","B","C","D"]


class TestContract_measure_sub_dag:
    def test_ct_one_shot_measure_order(self, sim_full):
        """[3.2.1 row 1]"""
        dag = sim_full._build_full_dag()
        _, order = sim_full._extract_measure_sub_dag(dag)
        assert order == ["wait_minutes","cost","satisfaction"]

    def test_ct_no_measures(self, sim_temporal):
        """[3.2.1 row 2]"""
        dag = sim_temporal._build_full_dag()
        adj, order = sim_temporal._extract_measure_sub_dag(dag)
        assert adj == {} and order == []

    def test_ct_single_stochastic(self, sim_temporal):
        """[3.2.1 row 3]"""
        sim_temporal.add_measure("m","gaussian",{"mu":10.0,"sigma":1.0})
        dag = sim_temporal._build_full_dag()
        adj, order = sim_temporal._extract_measure_sub_dag(dag)
        assert order == ["m"] and adj == {"m":[]}

    def test_ct_two_independent_lexicographic(self, sim_temporal):
        """[3.2.1 row 4]"""
        sim_temporal.add_measure("z_m","gaussian",{"mu":1,"sigma":1})
        sim_temporal.add_measure("a_m","gaussian",{"mu":1,"sigma":1})
        dag = sim_temporal._build_full_dag()
        _, order = sim_temporal._extract_measure_sub_dag(dag)
        assert order == ["a_m","z_m"]

    def test_ct_structural_depends_on_stochastic(self, sim_temporal):
        """[3.2.1 row 5]"""
        sim_temporal.add_category("c",["X","Y"],[1,1],"g1")
        sim_temporal.add_measure("base","gaussian",{"mu":10,"sigma":1})
        sim_temporal.add_measure_structural("derived","base * 2")
        dag = sim_temporal._build_full_dag()
        adj, order = sim_temporal._extract_measure_sub_dag(dag)
        assert "derived" in adj["base"]
        assert order == ["base","derived"]


# ################################################################
# 2. INPUT VALIDATION TESTS
# ################################################################

class TestInputValidation_inject_pattern:
    # FIX: [self-review item 7] — All parametrized type tests now verify
    # the reported type name in the error message, not just the prefix.
    @pytest.mark.parametrize("bad_type,expected_name", [
        (123,"int"), (45.6,"float"), (True,"bool"), (False,"bool"),
        ([],"list"), ({},"dict"), (("tuple",),"tuple"), (b"bytes","bytes"),
    ])
    def test_type_param_rejects_non_str(self, sim_full, bad_type, expected_name):
        """[1.8.1] type rejects all non-str with correct reported name."""
        with pytest.raises(TypeError, match=f"got {expected_name}"):
            sim_full.inject_pattern(bad_type, target="a == 'b'", col="wait_minutes", params={})

    @pytest.mark.parametrize("bad_target,expected_name", [
        (123,"int"), (45.6,"float"), (True,"bool"), (False,"bool"),
        ([],"list"), ({},"dict"), (None,"NoneType"),
    ])
    def test_target_param_rejects_non_str(self, sim_full, bad_target, expected_name):
        """[1.8.2] target rejects all non-str with correct reported name."""
        with pytest.raises(TypeError, match=f"got {expected_name}"):
            sim_full.inject_pattern("outlier_entity", target=bad_target, col="wait_minutes", params={"z_score":3.0})

    @pytest.mark.parametrize("bad_col,expected_name", [
        (123,"int"), (45.6,"float"), (True,"bool"), (False,"bool"),
        ([],"list"), ({},"dict"), (None,"NoneType"),
    ])
    def test_col_param_rejects_non_str(self, sim_full, bad_col, expected_name):
        """[1.8.3] col rejects all non-str with correct reported name."""
        with pytest.raises(TypeError, match=f"got {expected_name}"):
            sim_full.inject_pattern("outlier_entity", target="a == 'b'", col=bad_col, params={"z_score":3.0})

    @pytest.mark.parametrize("bad_params,expected_name", [
        ("string","str"), (123,"int"), (45.6,"float"),
        (True,"bool"), (False,"bool"),
        ([1,2],"list"), (None,"NoneType"), (("tuple",),"tuple"),
    ])
    def test_params_param_rejects_non_dict(self, sim_full, bad_params, expected_name):
        """[1.8.1] params rejects all non-dict with correct reported name."""
        with pytest.raises(TypeError, match=f"got {expected_name}"):
            sim_full.inject_pattern("outlier_entity", target="a == 'b'", col="wait_minutes", params=bad_params)

    @pytest.mark.parametrize("empty_target", ["", "   ", "\t", "\n"])
    def test_empty_or_whitespace_target_raises(self, sim_full, empty_target):
        """[1.8.2] Empty/whitespace-only target raises ValueError."""
        with pytest.raises(ValueError, match="non-empty"):
            sim_full.inject_pattern("outlier_entity", target=empty_target, col="wait_minutes", params={"z_score":3.0})

    def test_col_temporal_derived_raises(self, sim_full):
        """[1.8.3] col='day_of_week' (temporal_derived) raises."""
        with pytest.raises(ValueError, match="not.*measure"):
            sim_full.inject_pattern("outlier_entity", target="a == 'b'", col="day_of_week", params={"z_score":3.0})

    def test_outlier_entity_requires_z_score_only(self, sim_full):
        """[1.8.1] outlier_entity with only unrelated key raises."""
        with pytest.raises(ValueError, match="z_score"):
            sim_full.inject_pattern("outlier_entity", target="a == 'b'", col="wait_minutes", params={"magnitude":0.4})

    def test_trend_break_requires_both_keys(self, sim_full):
        """[1.8.1] trend_break with neither required key raises."""
        with pytest.raises(ValueError, match="missing"):
            sim_full.inject_pattern("trend_break", target="a == 'b'", col="wait_minutes", params={"unrelated":True})

    @pytest.mark.parametrize("valid_type", [
        "outlier_entity","trend_break","ranking_reversal",
        "dominance_shift","convergence","seasonal_anomaly",
    ])
    def test_all_six_valid_types_accepted(self, sim_full, valid_type):
        """[1.8.1] Every valid type accepted with suitable params."""
        params = {}
        if valid_type == "outlier_entity": params = {"z_score":3.0}
        elif valid_type == "trend_break": params = {"break_point":"2024-03-15","magnitude":0.4}
        sim_full.inject_pattern(valid_type, target="a == 'b'", col="wait_minutes", params=params)
        assert sim_full._patterns[-1]["type"] == valid_type


class TestInputValidation_set_realism:
    @pytest.mark.parametrize("bad_val", ["0.05", [0.05], (0.05,), None, b"0.05"])
    def test_missing_rate_non_numeric(self, fresh_sim, bad_val):
        """[1.9.1]"""
        with pytest.raises(TypeError):
            fresh_sim.set_realism(bad_val, 0.02)

    @pytest.mark.parametrize("bad_val", ["0.02", [0.02], (0.02,), None, b"0.02"])
    def test_dirty_rate_non_numeric(self, fresh_sim, bad_val):
        """[1.9.1]"""
        with pytest.raises(TypeError):
            fresh_sim.set_realism(0.05, bad_val)

    @pytest.mark.parametrize("bool_val", [True, False])
    def test_missing_rate_bool_rejected(self, fresh_sim, bool_val):
        """[1.9.1]"""
        with pytest.raises(TypeError, match="bool"):
            fresh_sim.set_realism(bool_val, 0.02)

    @pytest.mark.parametrize("bool_val", [True, False])
    def test_dirty_rate_bool_rejected(self, fresh_sim, bool_val):
        """[1.9.1]"""
        with pytest.raises(TypeError, match="bool"):
            fresh_sim.set_realism(0.05, bool_val)

    @pytest.mark.parametrize("out_val", [-0.001, -1.0, 1.001, 2.0, 100.0, float("inf")])
    def test_missing_rate_out_of_range(self, fresh_sim, out_val):
        """[1.9.1]"""
        with pytest.raises(ValueError, match="missing_rate"):
            fresh_sim.set_realism(out_val, 0.0)

    @pytest.mark.parametrize("out_val", [-0.001, -1.0, 1.001, 2.0, 100.0, float("inf")])
    def test_dirty_rate_out_of_range(self, fresh_sim, out_val):
        """[1.9.1]"""
        with pytest.raises(ValueError, match="dirty_rate"):
            fresh_sim.set_realism(0.0, out_val)

    # FIX: [self-review item 2] — NaN was silently accepted because NaN
    # comparisons always return False. Now asserts rejection.
    def test_nan_missing_rate_rejected(self, fresh_sim):
        """[1.9.1] NaN missing_rate raises ValueError."""
        with pytest.raises(ValueError, match="NaN"):
            fresh_sim.set_realism(float("nan"), 0.02)

    def test_nan_dirty_rate_rejected(self, fresh_sim):
        """[1.9.1] NaN dirty_rate raises ValueError."""
        with pytest.raises(ValueError, match="NaN"):
            fresh_sim.set_realism(0.05, float("nan"))

    @pytest.mark.parametrize("bad_censor", ["string", 123, 45.6, True, [1,2], (1,)])
    def test_censoring_non_dict_non_none(self, fresh_sim, bad_censor):
        """[1.9.1]"""
        with pytest.raises(TypeError, match="censoring"):
            fresh_sim.set_realism(0.05, 0.02, bad_censor)

    @pytest.mark.parametrize("rate", [0, 0.0, 1, 1.0])
    def test_boundary_rates_accepted(self, fresh_sim, rate):
        """[1.9.1] Exact boundary values accepted."""
        fresh_sim.set_realism(rate, rate)
        assert fresh_sim._realism_config is not None


# ################################################################
# 3. OUTPUT CORRECTNESS TESTS
# ################################################################

class TestOutputCorrectness_inject_pattern:
    def test_return_value_is_none(self, sim_full):
        """[1.8.5]"""
        assert sim_full.inject_pattern("outlier_entity", target="a == 'b'", col="wait_minutes", params={"z_score":3.0}) is None

    def test_stored_spec_has_all_four_keys(self, sim_full):
        """[1.8.5]"""
        sim_full.inject_pattern("outlier_entity", target="X", col="wait_minutes", params={"z_score":3.0})
        assert set(sim_full._patterns[0].keys()) == {"type","target","col","params"}

    def test_stored_spec_field_types(self, sim_full):
        """[1.8.5]"""
        sim_full.inject_pattern("trend_break", target="T", col="cost", params={"break_point":"2024-03-15","magnitude":0.4})
        spec = sim_full._patterns[0]
        assert isinstance(spec["type"], str) and isinstance(spec["target"], str)
        assert isinstance(spec["col"], str) and isinstance(spec["params"], dict)

    def test_params_stored_as_defensive_copy(self, sim_full):
        """[1.8.5]"""
        original = {"z_score":3.0}
        sim_full.inject_pattern("outlier_entity", target="T", col="wait_minutes", params=original)
        original["z_score"] = 999.0
        assert sim_full._patterns[0]["params"] == {"z_score":3.0}

    def test_ordering_preserved_across_multiple_inserts(self, sim_full):
        """[1.8.5]"""
        for t, p in [("outlier_entity",{"z_score":3.0}),("trend_break",{"break_point":"2024-01-01","magnitude":0.5}),("convergence",{"anything":True})]:
            sim_full.inject_pattern(t, target="T", col="wait_minutes", params=p)
        assert [s["type"] for s in sim_full._patterns] == ["outlier_entity","trend_break","convergence"]


class TestOutputCorrectness_set_realism:
    def test_return_value_is_none(self, fresh_sim):
        """[1.9.1]"""
        assert fresh_sim.set_realism(0.05, 0.02) is None

    def test_config_dict_has_three_keys(self, fresh_sim):
        """[1.9.1]"""
        fresh_sim.set_realism(0.05, 0.02)
        assert set(fresh_sim._realism_config.keys()) == {"missing_rate","dirty_rate","censoring"}

    def test_rates_stored_as_float(self, fresh_sim):
        """[1.9.1]"""
        fresh_sim.set_realism(0, 1)
        assert isinstance(fresh_sim._realism_config["missing_rate"], float)
        assert isinstance(fresh_sim._realism_config["dirty_rate"], float)

    def test_censoring_stored_as_defensive_copy(self, fresh_sim):
        """[1.9.1]"""
        original = {"threshold":100}
        fresh_sim.set_realism(0.05, 0.02, original)
        original["threshold"] = 999
        assert fresh_sim._realism_config["censoring"]["threshold"] == 100


class TestOutputCorrectness_build_full_dag:
    def test_return_type_is_dict(self, sim_full):
        """[3.1.1]"""
        dag = sim_full._build_full_dag()
        assert isinstance(dag, dict)
        for key, val in dag.items():
            assert isinstance(key, str) and isinstance(val, list)
            assert all(isinstance(item, str) for item in val)

    def test_every_declared_column_is_a_node(self, sim_full):
        """[3.1.1]"""
        dag = sim_full._build_full_dag()
        for col in sim_full._columns:
            assert col in dag

    def test_no_duplicate_edges(self, sim_full):
        """[3.1.1]"""
        dag = sim_full._build_full_dag()
        for node, succs in dag.items():
            assert len(succs) == len(set(succs)), f"Duplicates in {node}"

    def test_numerical_edge_count_one_shot(self, sim_full):
        """[3.1.1] 9 edges hand-counted."""
        dag = sim_full._build_full_dag()
        assert sum(len(s) for s in dag.values()) == 9


class TestOutputCorrectness_topological_sort:
    def test_return_type_is_list_of_str(self, fresh_sim):
        """[3.1.2]"""
        order = fresh_sim._topological_sort({"A":["B"],"B":[]})
        assert isinstance(order, list) and all(isinstance(n, str) for n in order)

    def test_length_matches_node_count(self, sim_full):
        """[3.1.2]"""
        dag = sim_full._build_full_dag()
        assert len(sim_full._topological_sort(dag)) == len(dag)

    def test_every_edge_respected(self, sim_full):
        """[3.1.2]"""
        dag = sim_full._build_full_dag()
        order = sim_full._topological_sort(dag)
        idx = {name:i for i,name in enumerate(order)}
        for u, succs in dag.items():
            for v in succs:
                assert idx[u] < idx[v], f"Edge {u}→{v} violated"

    def test_deterministic_across_calls(self, fresh_sim):
        """[3.1.2]"""
        adj = {"Z":[],"A":[],"M":[],"B":[]}
        assert fresh_sim._topological_sort(adj) == fresh_sim._topological_sort(adj) == ["A","B","M","Z"]

    def test_handles_nodes_only_in_successor_lists(self, fresh_sim):
        """[3.1.2]"""
        order = fresh_sim._topological_sort({"A":["B"]})
        assert set(order) == {"A","B"}
        assert order.index("A") < order.index("B")


class TestOutputCorrectness_measure_sub_dag:
    def test_return_type_is_tuple(self, sim_full):
        """[3.2.1]"""
        result = sim_full._extract_measure_sub_dag(sim_full._build_full_dag())
        assert isinstance(result, tuple) and len(result) == 2

    def test_sub_dag_excludes_non_measure_nodes(self, sim_full):
        """[3.2.1]"""
        adj, order = sim_full._extract_measure_sub_dag(sim_full._build_full_dag())
        for node in list(adj.keys()) + order:
            assert sim_full._columns[node]["type"] == "measure"

    def test_sub_dag_excludes_categorical_to_measure_edges(self, sim_full):
        """[3.2.1]"""
        adj, _ = sim_full._extract_measure_sub_dag(sim_full._build_full_dag())
        all_m = set(adj.keys())
        for succs in adj.values():
            for s in succs:
                assert s in all_m


# ################################################################
# 4. STATE TRANSITION TESTS
# ################################################################

class TestState_inject_pattern:
    def test_patterns_list_empty_on_fresh_sim(self, fresh_sim):
        """[1.8.5]"""
        assert fresh_sim._patterns == []

    def test_pattern_appended_not_replaced(self, sim_full):
        """[1.8.5]"""
        sim_full.inject_pattern("outlier_entity", target="A", col="wait_minutes", params={"z_score":1.0})
        sim_full.inject_pattern("outlier_entity", target="B", col="cost", params={"z_score":2.0})
        assert sim_full._patterns[0]["target"] == "A" and sim_full._patterns[1]["target"] == "B"

    def test_columns_registry_unchanged(self, sim_full):
        """[1.8.5]"""
        cols_before = dict(sim_full._columns)
        sim_full.inject_pattern("outlier_entity", target="A", col="wait_minutes", params={"z_score":1.0})
        assert dict(sim_full._columns) == cols_before

    def test_failed_validation_leaves_no_residue(self, sim_full):
        """[1.8.1]"""
        count_before = len(sim_full._patterns)
        with pytest.raises(ValueError):
            sim_full.inject_pattern("unknown_type", target="A", col="wait_minutes", params={})
        assert len(sim_full._patterns) == count_before

    def test_duplicate_patterns_are_allowed(self, sim_full):
        """[1.8.5]"""
        for _ in range(2):
            sim_full.inject_pattern("outlier_entity", target="A", col="wait_minutes", params={"z_score":3.0})
        assert len(sim_full._patterns) == 2


class TestState_set_realism:
    def test_realism_config_none_on_fresh_sim(self, fresh_sim):
        """[1.9.1]"""
        assert fresh_sim._realism_config is None

    def test_realism_config_set_after_call(self, fresh_sim):
        """[1.9.1]"""
        fresh_sim.set_realism(0.01, 0.01)
        assert fresh_sim._realism_config is not None

    def test_overwrite_does_not_merge(self, fresh_sim):
        """[1.9.1]"""
        fresh_sim.set_realism(0.05, 0.02, {"key1":"a"})
        fresh_sim.set_realism(0.10, 0.08)
        assert fresh_sim._realism_config["censoring"] is None

    def test_failed_validation_preserves_previous_config(self, fresh_sim):
        """[1.9.1]"""
        fresh_sim.set_realism(0.05, 0.02)
        with pytest.raises(ValueError):
            fresh_sim.set_realism(1.5, 0.0)
        assert fresh_sim._realism_config["missing_rate"] == pytest.approx(0.05)


class TestState_build_full_dag:
    def test_dag_does_not_mutate_columns(self, sim_full):
        """[3.1.1]"""
        import copy
        snap = copy.deepcopy(dict(sim_full._columns))
        sim_full._build_full_dag()
        assert dict(sim_full._columns) == snap

    def test_dag_does_not_mutate_measure_dag(self, sim_full):
        """[3.1.1]"""
        import copy
        snap = copy.deepcopy(sim_full._measure_dag)
        sim_full._build_full_dag()
        assert sim_full._measure_dag == snap

    def test_no_leakage_between_instances(self):
        """[3.1.1]"""
        sim_a = FactTableSimulator(100, 1)
        sim_a.add_category("x", ["A","B"], [1,1], "g")
        sim_b = FactTableSimulator(100, 2)
        sim_b.add_category("y", ["C","D"], [1,1], "g")
        assert set(sim_a._build_full_dag().keys()) == {"x"}
        assert set(sim_b._build_full_dag().keys()) == {"y"}


# ################################################################
# 5. INTEGRATION TESTS
# ################################################################

class TestIntegration:
    def test_full_declaration_phase_to_dag(self, sim_full):
        """[3.1.1, 3.1.2, 3.2.1]"""
        sim_full.inject_pattern("outlier_entity", target="hospital == 'Xiehe' & severity == 'Severe'", col="wait_minutes", params={"z_score":3.0})
        sim_full.inject_pattern("trend_break", target="hospital == 'Huashan'", col="wait_minutes", params={"break_point":"2024-03-15","magnitude":0.4})
        sim_full.set_realism(0.05, 0.02)
        dag = sim_full._build_full_dag()
        order = sim_full._topological_sort(dag)
        _, m_order = sim_full._extract_measure_sub_dag(dag)
        assert len(dag) == 10 and len(order) == 10
        assert m_order == ["wait_minutes","cost","satisfaction"]
        assert len(sim_full._patterns) == 2
        assert sim_full._realism_config is not None

    def test_dag_with_no_measures_only_categories(self, sim_cats):
        """[3.1.1]"""
        assert "department" in sim_cats._build_full_dag()["hospital"]

    def test_dag_with_temporal_derivations(self, sim_temporal):
        """[3.1.1]"""
        dag = sim_temporal._build_full_dag()
        assert "day_of_week" in dag["visit_date"] and "month" in dag["visit_date"]

    def test_group_dependency_creates_dag_edge(self, sim_rels):
        """[3.1.1]"""
        assert "payment_method" in sim_rels._build_full_dag()["severity"]

    def test_measure_effects_create_dag_edges(self, sim_full):
        """[3.1.1]"""
        dag = sim_full._build_full_dag()
        assert "wait_minutes" in dag["hospital"] and "wait_minutes" in dag["severity"]

    def test_structural_measure_dag_edges(self, sim_full):
        """[3.1.1]"""
        dag = sim_full._build_full_dag()
        assert "cost" in dag["wait_minutes"] and "satisfaction" in dag["cost"]

    def test_structural_effects_resolve_to_categorical_predictor(self, sim_full):
        """[3.1.1]"""
        assert "cost" in sim_full._build_full_dag()["severity"]

    def test_inject_pattern_requires_sprint3_measure(self, sim_temporal):
        """[1.8.3]"""
        with pytest.raises(ValueError, match="not declared"):
            sim_temporal.inject_pattern("outlier_entity", target="a == 'b'", col="nonexistent_measure", params={"z_score":3.0})

    def test_orthogonal_pair_from_sprint3_does_not_affect_dag(self, sim_rels):
        """[3.1.1]"""
        dag = sim_rels._build_full_dag()
        assert "severity" not in dag["hospital"] and "hospital" not in dag["severity"]

    def test_cyclic_dependency_error_inherits_from_prior_sprint(self, fresh_sim):
        """[3.1.2]"""
        with pytest.raises(CyclicDependencyError) as exc_info:
            fresh_sim._topological_sort({"A":["B"],"B":["A"]})
        assert hasattr(exc_info.value, "cycle_path")

    def test_dag_determinism_across_fresh_instances(self):
        """[3.1.2]"""
        def build():
            s = FactTableSimulator(100, 42)
            s.add_category("z_col",["A","B"],[1,1],"gz")
            s.add_category("a_col",["X","Y"],[1,1],"ga")
            s.add_measure("m","gaussian",{"mu":0,"sigma":1})
            return s._topological_sort(s._build_full_dag())
        assert build() == build()

    def test_measure_sub_dag_order_matches_spec_example(self, sim_full):
        """[3.2.1]"""
        _, order = sim_full._extract_measure_sub_dag(sim_full._build_full_dag())
        assert order == ["wait_minutes","cost","satisfaction"]

    def test_three_cycle_detected_in_topo_sort(self, fresh_sim):
        """[3.1.2]"""
        with pytest.raises(CyclicDependencyError) as exc_info:
            fresh_sim._topological_sort({"A":["B"],"B":["C"],"C":["A"]})
        path = exc_info.value.cycle_path
        assert len(path) >= 3 and path[0] == path[-1]

    def test_wide_graph_many_roots(self, fresh_sim):
        """[3.1.2]"""
        names = [f"col_{chr(ord('a') + i)}" for i in range(20)]
        for name in names:
            fresh_sim.add_category(name, ["V1","V2"], [1,1], f"g_{name}")
        assert fresh_sim._topological_sort(fresh_sim._build_full_dag()) == sorted(names)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
