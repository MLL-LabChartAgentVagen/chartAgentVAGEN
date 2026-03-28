"""
Sprint 1 — Test suite for agpds/simulator.py

Subtask IDs tested: 1.1.1, 1.1.2

Test categories (in order):
  1. Contract tests — one per §3C contract row
  2. Input validation tests — exhaustive type enforcement, boundary values
  3. Output correctness tests — attribute types, registry types
  4. State transition tests — registry isolation, no cross-instance leakage
  5. Integration tests — simulator uses data classes from models.py
"""
from __future__ import annotations

from collections import OrderedDict

import pytest

from agpds.models import DimensionGroup, OrthogonalPair, GroupDependency
from agpds.simulator import FactTableSimulator


# =====================================================================
# 1. CONTRACT TESTS — one per §3C contract table row
# =====================================================================


class TestContractConstructorHappyPath:
    """Contract rows for happy-path construction [1.1.1]."""

    # Contract row: FactTableSimulator(target_rows=500, seed=42)
    # → .target_rows == 500, .seed == 42
    def test_contract_one_shot_example(self) -> None:
        """[1.1.1] §2.5 one-shot example values."""
        sim = FactTableSimulator(target_rows=500, seed=42)
        assert sim.target_rows == 500
        assert sim.seed == 42

    # Contract row: FactTableSimulator(1, 0)
    # → .target_rows == 1, .seed == 0
    def test_contract_boundary_minimal_valid(self) -> None:
        """[1.1.1] Boundary: minimum valid target_rows=1, seed=0."""
        sim = FactTableSimulator(1, 0)
        assert sim.target_rows == 1
        assert sim.seed == 0

    # Contract row: FactTableSimulator(10_000_000, 99999)
    # → .target_rows == 10_000_000
    def test_contract_large_values(self) -> None:
        """[1.1.1] Large target_rows and seed."""
        sim = FactTableSimulator(10_000_000, 99999)
        assert sim.target_rows == 10_000_000
        assert sim.seed == 99999

    # Contract row: FactTableSimulator(500, -1) → accepted
    # NumPy default_rng accepts negative seeds
    def test_contract_negative_seed_accepted(self) -> None:
        """[1.1.1] Negative seed is valid (NumPy default_rng accepts it)."""
        sim = FactTableSimulator(500, -1)
        assert sim.seed == -1


class TestContractRegistriesExistAndEmpty:
    """Contract rows for registry initialization [1.1.2]."""

    @pytest.fixture()
    def sim(self) -> FactTableSimulator:
        return FactTableSimulator(target_rows=500, seed=42)

    # Contract row: _columns → isinstance(OrderedDict), len == 0
    def test_contract_columns_is_ordered_dict_and_empty(
        self, sim: FactTableSimulator
    ) -> None:
        """[1.1.2] _columns is an empty OrderedDict."""
        assert isinstance(sim._columns, OrderedDict)
        assert len(sim._columns) == 0

    # Contract row: _groups → isinstance(dict), len == 0
    def test_contract_groups_is_dict_and_empty(
        self, sim: FactTableSimulator
    ) -> None:
        """[1.1.2] _groups is an empty dict."""
        assert isinstance(sim._groups, dict)
        assert len(sim._groups) == 0

    # Contract row: _orthogonal_pairs → isinstance(list), len == 0
    def test_contract_orthogonal_pairs_is_list_and_empty(
        self, sim: FactTableSimulator
    ) -> None:
        """[1.1.2] _orthogonal_pairs is an empty list."""
        assert isinstance(sim._orthogonal_pairs, list)
        assert len(sim._orthogonal_pairs) == 0

    # Contract row: _group_dependencies → isinstance(list), len == 0
    def test_contract_group_dependencies_is_list_and_empty(
        self, sim: FactTableSimulator
    ) -> None:
        """[1.1.2] _group_dependencies is an empty list."""
        assert isinstance(sim._group_dependencies, list)
        assert len(sim._group_dependencies) == 0

    # Contract row: _patterns → isinstance(list), len == 0
    def test_contract_patterns_is_list_and_empty(
        self, sim: FactTableSimulator
    ) -> None:
        """[1.1.2] _patterns is an empty list."""
        assert isinstance(sim._patterns, list)
        assert len(sim._patterns) == 0

    # Contract row: _realism_config → is None
    def test_contract_realism_config_is_none(
        self, sim: FactTableSimulator
    ) -> None:
        """[1.1.2] _realism_config is None until set_realism() is called."""
        assert sim._realism_config is None

    # Contract row: _measure_dag → isinstance(dict), len == 0
    def test_contract_measure_dag_is_dict_and_empty(
        self, sim: FactTableSimulator
    ) -> None:
        """[1.1.2] _measure_dag is an empty dict."""
        assert isinstance(sim._measure_dag, dict)
        assert len(sim._measure_dag) == 0


class TestContractConstructorRejection:
    """Contract rows for constructor rejection [1.1.1]."""

    # Contract row: FactTableSimulator(0, 42) → ValueError
    def test_contract_zero_rows_raises_value_error(self) -> None:
        """[1.1.1] Zero rows rejected with ValueError."""
        with pytest.raises(ValueError, match="positive"):
            FactTableSimulator(0, 42)

    # Contract row: FactTableSimulator(-1, 42) → ValueError
    def test_contract_negative_rows_raises_value_error(self) -> None:
        """[1.1.1] Negative rows rejected with ValueError."""
        with pytest.raises(ValueError, match="positive"):
            FactTableSimulator(-1, 42)

    # Contract row: FactTableSimulator("500", 42) → TypeError
    def test_contract_string_target_rows_raises_type_error(self) -> None:
        """[1.1.1] String target_rows rejected with TypeError."""
        with pytest.raises(TypeError, match="target_rows must be an int"):
            FactTableSimulator("500", 42)  # type: ignore[arg-type]

    # Contract row: FactTableSimulator(500, "42") → TypeError
    def test_contract_string_seed_raises_type_error(self) -> None:
        """[1.1.1] String seed rejected with TypeError."""
        with pytest.raises(TypeError, match="seed must be an int"):
            FactTableSimulator(500, "42")  # type: ignore[arg-type]

    # Contract row: FactTableSimulator(500, 42.5) → TypeError
    def test_contract_float_seed_raises_type_error(self) -> None:
        """[1.1.1] Float seed rejected with TypeError."""
        with pytest.raises(TypeError, match="seed must be an int"):
            FactTableSimulator(500, 42.5)  # type: ignore[arg-type]

    # Contract row: FactTableSimulator(500.0, 42) → TypeError
    def test_contract_float_target_rows_raises_type_error(self) -> None:
        """[1.1.1] Float target_rows rejected with TypeError."""
        with pytest.raises(TypeError, match="target_rows must be an int"):
            FactTableSimulator(500.0, 42)  # type: ignore[arg-type]

    # Contract row: FactTableSimulator(500, None) → TypeError
    def test_contract_none_seed_raises_type_error(self) -> None:
        """[1.1.1] None seed rejected with TypeError."""
        with pytest.raises(TypeError, match="seed must be an int"):
            FactTableSimulator(500, None)  # type: ignore[arg-type]

    # Contract row: No AttributeError on any registry access
    def test_contract_no_attribute_error_on_any_registry(self) -> None:
        """[1.1.2] All 7 registries accessible without AttributeError."""
        sim = FactTableSimulator(500, 42)
        _ = sim._columns
        _ = sim._groups
        _ = sim._orthogonal_pairs
        _ = sim._group_dependencies
        _ = sim._patterns
        _ = sim._realism_config
        _ = sim._measure_dag


# =====================================================================
# 2. INPUT VALIDATION TESTS — exhaustive type enforcement
# =====================================================================


class TestConstructorTypeEnforcementTargetRows:
    """Exhaustive type checks for target_rows parameter [1.1.1]."""

    @pytest.mark.parametrize(
        "bad_value,type_name",
        [
            ("500", "str"),
            (500.0, "float"),
            (500.5, "float"),
            (None, "NoneType"),
            ([500], "list"),
            ((500,), "tuple"),
            ({500}, "set"),
            ({"rows": 500}, "dict"),
            (True, "bool"),
            (False, "bool"),
            (b"500", "bytes"),
            (complex(500, 0), "complex"),
        ],
        ids=[
            "str", "float_exact", "float_decimal", "none",
            "list", "tuple", "set", "dict", "bool_true", "bool_false",
            "bytes", "complex",
        ],
    )
    def test_rejects_non_int_target_rows(
        self, bad_value: object, type_name: str
    ) -> None:
        """[1.1.1] target_rows must be int — rejects {type_name}."""
        with pytest.raises(TypeError, match="target_rows must be an int"):
            FactTableSimulator(bad_value, 42)  # type: ignore[arg-type]


class TestConstructorTypeEnforcementSeed:
    """Exhaustive type checks for seed parameter [1.1.1]."""

    @pytest.mark.parametrize(
        "bad_value,type_name",
        [
            ("42", "str"),
            (42.0, "float"),
            (42.5, "float"),
            (None, "NoneType"),
            ([42], "list"),
            ((42,), "tuple"),
            (True, "bool"),
            (False, "bool"),
            (b"42", "bytes"),
        ],
        ids=[
            "str", "float_exact", "float_decimal", "none",
            "list", "tuple", "bool_true", "bool_false", "bytes",
        ],
    )
    def test_rejects_non_int_seed(
        self, bad_value: object, type_name: str
    ) -> None:
        """[1.1.1] seed must be int — rejects {type_name}."""
        with pytest.raises(TypeError, match="seed must be an int"):
            FactTableSimulator(500, bad_value)  # type: ignore[arg-type]


class TestConstructorValueBoundaries:
    """Boundary value checks for target_rows [1.1.1]."""

    @pytest.mark.parametrize(
        "rows",
        [-1_000_000, -1, 0],
        ids=["large_negative", "neg_one", "zero"],
    )
    def test_rejects_non_positive_target_rows(self, rows: int) -> None:
        """[1.1.1] target_rows ≤ 0 rejected with ValueError."""
        with pytest.raises(ValueError, match="positive"):
            FactTableSimulator(rows, 42)

    def test_accepts_target_rows_of_one(self) -> None:
        """[1.1.1] target_rows=1 is the minimum valid value."""
        sim = FactTableSimulator(1, 42)
        assert sim.target_rows == 1

    def test_accepts_target_rows_of_two(self) -> None:
        """[1.1.1] target_rows=2 — just above minimum."""
        sim = FactTableSimulator(2, 42)
        assert sim.target_rows == 2

    @pytest.mark.parametrize(
        "seed",
        [-2**31, -1, 0, 1, 2**31, 2**63 - 1],
        ids=["min_i32", "neg_one", "zero", "one", "max_i32", "large_i64"],
    )
    def test_accepts_various_seed_values(self, seed: int) -> None:
        """[1.1.1] Wide range of valid integer seeds."""
        sim = FactTableSimulator(100, seed)
        assert sim.seed == seed


class TestConstructorErrorMessageQuality:
    """Verify error messages are descriptive for §2.7 feedback [1.1.1]."""

    def test_type_error_includes_actual_type_name(self) -> None:
        """[1.1.1] TypeError message names the actual type received."""
        with pytest.raises(TypeError, match="float"):
            FactTableSimulator(500.0, 42)  # type: ignore[arg-type]

    def test_value_error_includes_actual_value(self) -> None:
        """[1.1.1] ValueError message includes the offending value."""
        with pytest.raises(ValueError, match="-5"):
            FactTableSimulator(-5, 42)

    def test_none_target_rows_error_includes_nonetype(self) -> None:
        """[1.1.1] TypeError for None mentions NoneType."""
        with pytest.raises(TypeError, match="NoneType"):
            FactTableSimulator(None, 42)  # type: ignore[arg-type]


# =====================================================================
# 3. OUTPUT CORRECTNESS TESTS — attribute types, registry types
# =====================================================================


class TestConstructorAttributeTypes:
    """Verify exact types of all public and private attributes [1.1.1, 1.1.2]."""

    @pytest.fixture()
    def sim(self) -> FactTableSimulator:
        return FactTableSimulator(target_rows=500, seed=42)

    def test_target_rows_is_int(self, sim: FactTableSimulator) -> None:
        """[1.1.1] target_rows stored as int, not coerced."""
        assert type(sim.target_rows) is int

    def test_seed_is_int(self, sim: FactTableSimulator) -> None:
        """[1.1.1] seed stored as int, not coerced."""
        assert type(sim.seed) is int

    def test_columns_exact_type(self, sim: FactTableSimulator) -> None:
        """[1.1.2] _columns is specifically OrderedDict, not plain dict."""
        assert type(sim._columns) is OrderedDict

    def test_groups_is_plain_dict(self, sim: FactTableSimulator) -> None:
        """[1.1.2] _groups is a plain dict (not OrderedDict)."""
        assert type(sim._groups) is dict

    def test_orthogonal_pairs_is_list(self, sim: FactTableSimulator) -> None:
        """[1.1.2] _orthogonal_pairs is a plain list."""
        assert type(sim._orthogonal_pairs) is list

    def test_group_dependencies_is_list(self, sim: FactTableSimulator) -> None:
        """[1.1.2] _group_dependencies is a plain list."""
        assert type(sim._group_dependencies) is list

    def test_patterns_is_list(self, sim: FactTableSimulator) -> None:
        """[1.1.2] _patterns is a plain list."""
        assert type(sim._patterns) is list

    def test_realism_config_is_none_type(self, sim: FactTableSimulator) -> None:
        """[1.1.2] _realism_config starts as None (NoneType)."""
        assert sim._realism_config is None

    def test_measure_dag_is_plain_dict(self, sim: FactTableSimulator) -> None:
        """[1.1.2] _measure_dag is a plain dict."""
        assert type(sim._measure_dag) is dict


class TestConstructorReturnsSelf:
    """Verify constructor produces a usable instance [1.1.1]."""

    def test_instance_type(self) -> None:
        """[1.1.1] Constructor returns a FactTableSimulator instance."""
        sim = FactTableSimulator(100, 0)
        assert isinstance(sim, FactTableSimulator)

    def test_multiple_instantiations(self) -> None:
        """[1.1.1] Multiple instances with different params coexist."""
        sim1 = FactTableSimulator(100, 1)
        sim2 = FactTableSimulator(200, 2)
        sim3 = FactTableSimulator(300, 3)
        assert sim1.target_rows == 100
        assert sim2.target_rows == 200
        assert sim3.target_rows == 300


# =====================================================================
# 4. STATE TRANSITION TESTS — registry isolation, no leakage
# =====================================================================


class TestRegistryIsolation:
    """Verify no state leakage between FactTableSimulator instances [1.1.2]."""

    def test_columns_isolated_across_instances(self) -> None:
        """[1.1.2] Mutating _columns on one instance does not affect another."""
        sim1 = FactTableSimulator(100, 1)
        sim2 = FactTableSimulator(200, 2)
        sim1._columns["test_col"] = {"type": "categorical"}
        assert "test_col" not in sim2._columns

    def test_groups_isolated_across_instances(self) -> None:
        """[1.1.2] Mutating _groups on one instance does not affect another."""
        sim1 = FactTableSimulator(100, 1)
        sim2 = FactTableSimulator(200, 2)
        sim1._groups["test_group"] = DimensionGroup(name="test", root="col")
        assert "test_group" not in sim2._groups

    def test_orthogonal_pairs_isolated_across_instances(self) -> None:
        """[1.1.2] Mutating _orthogonal_pairs on one does not affect another."""
        sim1 = FactTableSimulator(100, 1)
        sim2 = FactTableSimulator(200, 2)
        sim1._orthogonal_pairs.append(OrthogonalPair("a", "b", "r"))
        assert len(sim2._orthogonal_pairs) == 0

    def test_group_dependencies_isolated_across_instances(self) -> None:
        """[1.1.2] Mutating _group_dependencies on one does not affect another."""
        sim1 = FactTableSimulator(100, 1)
        sim2 = FactTableSimulator(200, 2)
        sim1._group_dependencies.append(
            GroupDependency(child_root="c", on=["p"], conditional_weights={})
        )
        assert len(sim2._group_dependencies) == 0

    def test_patterns_isolated_across_instances(self) -> None:
        """[1.1.2] Mutating _patterns on one does not affect another."""
        sim1 = FactTableSimulator(100, 1)
        sim2 = FactTableSimulator(200, 2)
        sim1._patterns.append({"type": "outlier_entity"})
        assert len(sim2._patterns) == 0

    def test_measure_dag_isolated_across_instances(self) -> None:
        """[1.1.2] Mutating _measure_dag on one does not affect another."""
        sim1 = FactTableSimulator(100, 1)
        sim2 = FactTableSimulator(200, 2)
        sim1._measure_dag["wait_minutes"] = ["cost"]
        assert "wait_minutes" not in sim2._measure_dag


class TestRegistrySequentialMutation:
    """Verify sequential mutations build state correctly [1.1.2]."""

    def test_columns_preserve_insertion_order(self) -> None:
        """[1.1.2] OrderedDict preserves the order of column insertions."""
        sim = FactTableSimulator(100, 42)
        sim._columns["hospital"] = {"type": "categorical"}
        sim._columns["department"] = {"type": "categorical"}
        sim._columns["severity"] = {"type": "categorical"}
        keys = list(sim._columns.keys())
        assert keys == ["hospital", "department", "severity"]

    def test_groups_accumulate_correctly(self) -> None:
        """[1.1.2] Multiple group insertions all persist."""
        sim = FactTableSimulator(100, 42)
        sim._groups["entity"] = DimensionGroup(name="entity", root="hospital")
        sim._groups["patient"] = DimensionGroup(name="patient", root="severity")
        assert len(sim._groups) == 2
        assert "entity" in sim._groups
        assert "patient" in sim._groups

    def test_patterns_accumulate_in_order(self) -> None:
        """[1.1.2] Patterns list preserves append order."""
        sim = FactTableSimulator(100, 42)
        sim._patterns.append({"type": "outlier_entity", "col": "wait_minutes"})
        sim._patterns.append({"type": "trend_break", "col": "cost"})
        assert len(sim._patterns) == 2
        assert sim._patterns[0]["type"] == "outlier_entity"
        assert sim._patterns[1]["type"] == "trend_break"

    def test_measure_dag_builds_adjacency_list(self) -> None:
        """[1.1.2] Measure DAG adjacency list accumulates edges."""
        sim = FactTableSimulator(100, 42)
        sim._measure_dag["wait_minutes"] = []
        sim._measure_dag["cost"] = []
        sim._measure_dag["wait_minutes"].append("cost")
        assert "cost" in sim._measure_dag["wait_minutes"]
        assert sim._measure_dag["cost"] == []


class TestRegistryCleanOnFreshInstantiation:
    """Verify fresh instances start clean even after prior instances were mutated [1.1.2]."""

    def test_fresh_after_heavy_mutation(self) -> None:
        """[1.1.2] Creating a new instance after mutating a prior one starts clean."""
        sim_old = FactTableSimulator(100, 1)
        sim_old._columns["x"] = {}
        sim_old._groups["g"] = DimensionGroup(name="g", root="r")
        sim_old._orthogonal_pairs.append(OrthogonalPair("a", "b", "r"))
        sim_old._group_dependencies.append(
            GroupDependency(child_root="c", on=["p"], conditional_weights={})
        )
        sim_old._patterns.append({"type": "test"})
        sim_old._realism_config = {"missing_rate": 0.05}
        sim_old._measure_dag["m"] = ["n"]

        # New instance must be completely clean
        sim_new = FactTableSimulator(200, 2)
        assert len(sim_new._columns) == 0
        assert len(sim_new._groups) == 0
        assert len(sim_new._orthogonal_pairs) == 0
        assert len(sim_new._group_dependencies) == 0
        assert len(sim_new._patterns) == 0
        assert sim_new._realism_config is None
        assert len(sim_new._measure_dag) == 0


# =====================================================================
# 5. INTEGRATION TESTS — simulator uses data classes from models.py
# =====================================================================


class TestSimulatorModelsIntegration:
    """Verify simulator registries accept data classes from models.py [1.1.1, 1.1.2, 2.1.1, 2.2.1, 2.2.2]."""

    def test_groups_registry_accepts_dimension_group(self) -> None:
        """[1.1.2, 2.1.1] _groups stores DimensionGroup instances."""
        sim = FactTableSimulator(500, 42)
        group = DimensionGroup(
            name="entity", root="hospital",
            columns=["hospital", "department"],
            hierarchy=["hospital", "department"],
        )
        sim._groups["entity"] = group
        assert sim._groups["entity"].root == "hospital"
        assert sim._groups["entity"].to_metadata() == {
            "columns": ["hospital", "department"],
            "hierarchy": ["hospital", "department"],
        }

    def test_orthogonal_pairs_registry_accepts_orthogonal_pair(self) -> None:
        """[1.1.2, 2.2.1] _orthogonal_pairs stores OrthogonalPair instances."""
        sim = FactTableSimulator(500, 42)
        pair = OrthogonalPair("entity", "patient", "reason")
        sim._orthogonal_pairs.append(pair)
        assert len(sim._orthogonal_pairs) == 1
        assert sim._orthogonal_pairs[0].involves_group("entity")

    def test_group_dependencies_registry_accepts_group_dependency(self) -> None:
        """[1.1.2, 2.2.2] _group_dependencies stores GroupDependency instances."""
        sim = FactTableSimulator(500, 42)
        dep = GroupDependency(
            child_root="payment_method",
            on=["severity"],
            conditional_weights={
                "Mild": {"Insurance": 0.5, "Self-pay": 0.5},
            },
        )
        sim._group_dependencies.append(dep)
        assert len(sim._group_dependencies) == 1
        assert sim._group_dependencies[0].child_root == "payment_method"

    def test_full_one_shot_example_population(self) -> None:
        """[1.1.1, 1.1.2] Populate all registries mimicking §2.5 one-shot example."""
        sim = FactTableSimulator(target_rows=500, seed=42)

        # Columns
        sim._columns["hospital"] = {"type": "categorical", "group": "entity"}
        sim._columns["department"] = {"type": "categorical", "group": "entity", "parent": "hospital"}
        sim._columns["severity"] = {"type": "categorical", "group": "patient"}
        sim._columns["payment_method"] = {"type": "categorical", "group": "payment"}
        sim._columns["visit_date"] = {"type": "temporal", "group": "time"}
        sim._columns["wait_minutes"] = {"type": "measure", "measure_type": "stochastic"}
        sim._columns["cost"] = {"type": "measure", "measure_type": "structural"}
        sim._columns["satisfaction"] = {"type": "measure", "measure_type": "structural"}

        # Groups
        sim._groups["entity"] = DimensionGroup(
            name="entity", root="hospital",
            columns=["hospital", "department"],
            hierarchy=["hospital", "department"],
        )
        sim._groups["patient"] = DimensionGroup(
            name="patient", root="severity",
            columns=["severity"], hierarchy=["severity"],
        )
        sim._groups["payment"] = DimensionGroup(
            name="payment", root="payment_method",
            columns=["payment_method"], hierarchy=["payment_method"],
        )
        # FIX: [self-review item 3] — hierarchy is root-only per §2.6 example
        sim._groups["time"] = DimensionGroup(
            name="time", root="visit_date",
            columns=["visit_date", "day_of_week", "month"],
            hierarchy=["visit_date"],
        )

        # Orthogonal
        sim._orthogonal_pairs.append(
            OrthogonalPair("entity", "patient", "Independent")
        )

        # Group dependency
        sim._group_dependencies.append(
            GroupDependency(
                child_root="payment_method", on=["severity"],
                conditional_weights={
                    "Mild": {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},
                    "Moderate": {"Insurance": 0.65, "Self-pay": 0.25, "Government": 0.10},
                    "Severe": {"Insurance": 0.80, "Self-pay": 0.10, "Government": 0.10},
                },
            )
        )

        # Patterns
        sim._patterns.append({"type": "outlier_entity", "col": "wait_minutes"})
        sim._patterns.append({"type": "trend_break", "col": "wait_minutes"})

        # Measure DAG
        sim._measure_dag["wait_minutes"] = ["cost", "satisfaction"]
        sim._measure_dag["cost"] = []
        sim._measure_dag["satisfaction"] = []

        # Verify the full state
        assert len(sim._columns) == 8
        assert len(sim._groups) == 4
        assert len(sim._orthogonal_pairs) == 1
        assert len(sim._group_dependencies) == 1
        assert len(sim._patterns) == 2
        assert sim._realism_config is None
        assert len(sim._measure_dag) == 3

        # Verify column order matches insertion order
        col_names = list(sim._columns.keys())
        assert col_names[0] == "hospital"
        assert col_names[-1] == "satisfaction"

        # Verify measure DAG structure
        assert "cost" in sim._measure_dag["wait_minutes"]
        assert "satisfaction" in sim._measure_dag["wait_minutes"]


class TestExitGateConditions:
    """Sprint 1 exit gate assertions from the sprint plan [1.1.1, 1.1.2]."""

    def test_exit_gate_constructor_attributes_and_empty_registries(self) -> None:
        """[1.1.1, 1.1.2] Exit gate: FactTableSimulator(500,42) has correct attributes
        and all registries are empty."""
        sim = FactTableSimulator(500, 42)
        assert sim.target_rows == 500
        assert sim.seed == 42
        assert len(sim._columns) == 0
        assert len(sim._groups) == 0
        assert len(sim._orthogonal_pairs) == 0
        assert len(sim._group_dependencies) == 0
        assert len(sim._patterns) == 0
        assert sim._realism_config is None
        assert len(sim._measure_dag) == 0


class TestImportSanity:
    """Verify clean imports with no circular dependencies."""

    def test_import_simulator_standalone(self) -> None:
        """[1.1.1] agpds.simulator imports cleanly."""
        import agpds.simulator  # noqa: F401

    def test_import_package(self) -> None:
        """[1.1.1] agpds package imports cleanly."""
        import agpds  # noqa: F401
        assert hasattr(agpds, "FactTableSimulator")
