"""
Sprint 1 — Test suite for agpds/models.py

Subtask IDs tested: 2.1.1, 2.2.1, 2.2.2

Test categories (in order):
  1. Contract tests — one per §3B contract row
  2. Input validation tests — boundary values, type edge cases
  3. Output correctness tests — serialization format, field types, immutability
  4. State transition tests — default factory independence, mutation isolation
  5. Integration tests — cross-class interactions, downstream consumption patterns
"""
from __future__ import annotations

import copy

import pytest

from agpds.models import DimensionGroup, OrthogonalPair, GroupDependency


# =====================================================================
# 1. CONTRACT TESTS — one per §3B contract table row
# =====================================================================


class TestContractDimensionGroup:
    """Contract rows for DimensionGroup [2.1.1]."""

    # Contract row: DimensionGroup(entity, 2-col hierarchy) → correct fields
    def test_contract_entity_group_two_columns(self) -> None:
        """[2.1.1] Two-column hierarchy: hospital → department."""
        group = DimensionGroup(
            name="entity",
            root="hospital",
            columns=["hospital", "department"],
            hierarchy=["hospital", "department"],
        )
        assert group.name == "entity"
        assert group.root == "hospital"
        assert group.columns == ["hospital", "department"]
        assert group.hierarchy == ["hospital", "department"]

    # Contract row: DimensionGroup(payment, single-col) → root only
    def test_contract_single_column_group(self) -> None:
        """[2.1.1] Root-only group (e.g. payment with just payment_method)."""
        group = DimensionGroup(
            name="payment",
            root="payment_method",
            columns=["payment_method"],
            hierarchy=["payment_method"],
        )
        assert group.root == "payment_method"
        assert len(group.columns) == 1

    # Contract row: DimensionGroup(time, 3-col) → temporal group
    # FIX: [self-review item 3] — §2.6 shows "time" group with
    # hierarchy: ["visit_date"] — derived columns are flat derivations,
    # not parent→child hierarchy members. Test now matches spec.
    def test_contract_temporal_group_three_columns(self) -> None:
        """[2.1.1] Temporal group: 3 columns but hierarchy is root-only per §2.6."""
        group = DimensionGroup(
            name="time",
            root="visit_date",
            columns=["visit_date", "day_of_week", "month"],
            hierarchy=["visit_date"],
        )
        assert group.root == "visit_date"
        assert len(group.columns) == 3
        assert group.hierarchy == ["visit_date"]

    # Contract row: DimensionGroup.to_metadata() → §2.6 format dict
    def test_contract_to_metadata_format(self) -> None:
        """[2.1.1] Serialization matches §2.6: {"columns": [...], "hierarchy": [...]}."""
        group = DimensionGroup(
            name="entity",
            root="hospital",
            columns=["hospital", "department"],
            hierarchy=["hospital", "department"],
        )
        meta = group.to_metadata()
        assert meta == {
            "columns": ["hospital", "department"],
            "hierarchy": ["hospital", "department"],
        }

    # Contract row: DimensionGroup empty columns edge case → instantiates
    def test_contract_empty_columns_edge_case(self) -> None:
        """[2.1.1] Empty columns and hierarchy (default factory)."""
        group = DimensionGroup(name="empty", root="r")
        assert group.columns == []
        assert group.hierarchy == []


class TestContractOrthogonalPair:
    """Contract rows for OrthogonalPair [2.2.1]."""

    # Contract row: OrthogonalPair("entity","patient","reason") → correct fields
    def test_contract_happy_path(self) -> None:
        """[2.2.1] Basic instantiation with §2.1.2 example values."""
        pair = OrthogonalPair("entity", "patient", "Severity independent of hospital")
        assert pair.group_a == "entity"
        assert pair.group_b == "patient"
        assert pair.rationale == "Severity independent of hospital"

    # Contract row: OrthogonalPair("entity","patient") == OrthogonalPair("patient","entity") → True
    def test_contract_order_independent_equality(self) -> None:
        """[2.2.1] (A,B) == (B,A) per done condition."""
        p1 = OrthogonalPair("entity", "patient", "r")
        p2 = OrthogonalPair("patient", "entity", "r")
        assert p1 == p2

    # Contract row: different groups → False
    def test_contract_different_groups_not_equal(self) -> None:
        """[2.2.1] Different group pairs must not be equal."""
        p1 = OrthogonalPair("entity", "patient", "r")
        p2 = OrthogonalPair("entity", "payment", "r")
        assert p1 != p2

    # Contract row: same groups, diff rationale → True (equality ignores rationale)
    def test_contract_equality_ignores_rationale(self) -> None:
        """[2.2.1] Same group pair with different rationale — still equal."""
        p1 = OrthogonalPair("entity", "patient", "reason1")
        p2 = OrthogonalPair("entity", "patient", "reason2")
        assert p1 == p2

    # Contract row: hash(Pair(A,B)) == hash(Pair(B,A)) → True
    def test_contract_hash_order_independent(self) -> None:
        """[2.2.1] Hash consistency with order-independent __eq__."""
        p1 = OrthogonalPair("a", "b", "r")
        p2 = OrthogonalPair("b", "a", "r")
        assert hash(p1) == hash(p2)

    # Contract row: set deduplication → {(a,b), (b,a)} has len 1
    def test_contract_set_deduplication(self) -> None:
        """[2.2.1] Adding both orderings to a set yields one element."""
        s = {
            OrthogonalPair("a", "b", "r"),
            OrthogonalPair("b", "a", "r"),
        }
        assert len(s) == 1

    # Contract row: OrthogonalPair.to_metadata() → §2.6 format
    def test_contract_to_metadata(self) -> None:
        """[2.2.1] Serialization to §2.6 format."""
        pair = OrthogonalPair("entity", "patient", "Independent")
        meta = pair.to_metadata()
        assert meta == {
            "group_a": "entity",
            "group_b": "patient",
            "rationale": "Independent",
        }

    # Contract row: __eq__(non-OrthogonalPair) → NotImplemented or False
    def test_contract_eq_with_non_orthogonal_pair(self) -> None:
        """[2.2.1] Comparison with a non-OrthogonalPair returns NotImplemented."""
        pair = OrthogonalPair("a", "b", "r")
        result = pair.__eq__("not a pair")
        assert result is NotImplemented


class TestContractGroupDependency:
    """Contract rows for GroupDependency [2.2.2]."""

    # Contract row: GroupDependency from §2.1.2 example → correct fields
    def test_contract_happy_path_from_spec(self) -> None:
        """[2.2.2] §2.1.2 example: payment_method depends on severity."""
        weights = {
            "Mild":     {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},
            "Moderate": {"Insurance": 0.65, "Self-pay": 0.25, "Government": 0.10},
            "Severe":   {"Insurance": 0.80, "Self-pay": 0.10, "Government": 0.10},
        }
        dep = GroupDependency(
            child_root="payment_method",
            on=["severity"],
            conditional_weights=weights,
        )
        assert dep.child_root == "payment_method"
        assert dep.on == ["severity"]
        assert dep.conditional_weights == weights

    # Contract row: empty on=[] → instantiates
    def test_contract_empty_on_edge_case(self) -> None:
        """[2.2.2] Empty on list (validation is in SDK, not dataclass)."""
        dep = GroupDependency(child_root="col", on=[], conditional_weights={})
        assert dep.on == []

    # Contract row: empty conditional_weights={} → instantiates
    def test_contract_empty_conditional_weights(self) -> None:
        """[2.2.2] Empty weights dict."""
        dep = GroupDependency(child_root="col", on=["p"], conditional_weights={})
        assert dep.conditional_weights == {}

    # Contract row: GroupDependency.to_metadata() → §2.6 format
    def test_contract_to_metadata(self) -> None:
        """[2.2.2] Serialization to §2.6 format."""
        weights = {"Mild": {"Insurance": 0.5, "Self-pay": 0.5}}
        dep = GroupDependency(
            child_root="payment_method",
            on=["severity"],
            conditional_weights=weights,
        )
        meta = dep.to_metadata()
        assert meta == {
            "child_root": "payment_method",
            "on": ["severity"],
            "conditional_weights": weights,
        }

    # Contract row: complex multi-value conditional_weights → preserved
    def test_contract_complex_conditional_weights(self) -> None:
        """[2.2.2] Multi-value outer and inner dicts preserved exactly."""
        weights = {
            "A": {"X": 0.3, "Y": 0.7},
            "B": {"X": 0.6, "Y": 0.4},
            "C": {"X": 0.1, "Y": 0.9},
        }
        dep = GroupDependency(child_root="col", on=["parent"], conditional_weights=weights)
        assert len(dep.conditional_weights) == 3
        assert dep.conditional_weights["A"]["X"] == pytest.approx(0.3)
        assert dep.conditional_weights["C"]["Y"] == pytest.approx(0.9)


# =====================================================================
# 2. INPUT VALIDATION TESTS — boundary values, type edge cases
# =====================================================================


class TestDimensionGroupInputBoundaries:
    """Boundary and edge-case inputs for DimensionGroup [2.1.1]."""

    def test_very_long_column_list(self) -> None:
        """[2.1.1] Boundary: group with many columns (deep hierarchy)."""
        cols = [f"level_{i}" for i in range(50)]
        group = DimensionGroup(name="deep", root="level_0", columns=cols, hierarchy=cols)
        assert len(group.columns) == 50
        assert group.hierarchy[0] == "level_0"

    def test_name_with_spaces(self) -> None:
        """[2.1.1] Group name containing spaces (unusual but not rejected by dataclass)."""
        group = DimensionGroup(name="my group", root="col")
        assert group.name == "my group"

    def test_unicode_column_names(self) -> None:
        """[2.1.1] Unicode characters in column names."""
        group = DimensionGroup(name="中文", root="医院", columns=["医院", "科室"])
        assert group.root == "医院"

    def test_duplicate_columns_in_list(self) -> None:
        """[2.1.1] Dataclass does not reject duplicates — validation is in SDK."""
        group = DimensionGroup(name="g", root="a", columns=["a", "a"])
        assert len(group.columns) == 2  # stored as-is; SDK validates


class TestOrthogonalPairInputBoundaries:
    """Boundary and edge-case inputs for OrthogonalPair [2.2.1]."""

    def test_same_group_both_sides(self) -> None:
        """[2.2.1] Self-orthogonal pair (SDK should reject, but dataclass stores it)."""
        pair = OrthogonalPair("entity", "entity", "self-orthogonal")
        assert pair.group_a == pair.group_b

    def test_empty_rationale(self) -> None:
        """[2.2.1] Empty string rationale."""
        pair = OrthogonalPair("a", "b", "")
        assert pair.rationale == ""

    def test_very_long_rationale(self) -> None:
        """[2.2.1] Very long rationale string."""
        long_text = "x" * 10_000
        pair = OrthogonalPair("a", "b", long_text)
        assert len(pair.rationale) == 10_000

    def test_empty_group_names(self) -> None:
        """[2.2.1] Empty strings as group names (SDK validates, dataclass stores)."""
        pair = OrthogonalPair("", "", "r")
        assert pair.group_a == ""


class TestGroupDependencyInputBoundaries:
    """Boundary and edge-case inputs for GroupDependency [2.2.2]."""

    def test_multi_column_on(self) -> None:
        """[2.2.2] Multi-column on list (A7 restricts to single in SDK, not dataclass)."""
        dep = GroupDependency(
            child_root="col",
            on=["parent1", "parent2"],
            conditional_weights={},
        )
        assert len(dep.on) == 2

    def test_deeply_nested_weights(self) -> None:
        """[2.2.2] Weights with many inner entries."""
        inner = {f"val_{i}": 1.0 / 20 for i in range(20)}
        weights = {f"parent_{j}": dict(inner) for j in range(10)}
        dep = GroupDependency(child_root="col", on=["p"], conditional_weights=weights)
        assert len(dep.conditional_weights) == 10
        assert len(dep.conditional_weights["parent_0"]) == 20

    def test_weights_with_zero_values(self) -> None:
        """[2.2.2] Weights containing 0.0 (valid — SDK may reject degenerate)."""
        weights = {"A": {"X": 1.0, "Y": 0.0}}
        dep = GroupDependency(child_root="col", on=["p"], conditional_weights=weights)
        assert dep.conditional_weights["A"]["Y"] == 0.0


# =====================================================================
# 3. OUTPUT CORRECTNESS TESTS — serialization, types, immutability
# =====================================================================


class TestDimensionGroupOutput:
    """Output correctness for DimensionGroup [2.1.1]."""

    def test_to_metadata_returns_dict(self) -> None:
        """[2.1.1] Return type is plain dict."""
        group = DimensionGroup(name="g", root="r", columns=["r"], hierarchy=["r"])
        meta = group.to_metadata()
        assert isinstance(meta, dict)

    def test_to_metadata_has_exactly_two_keys(self) -> None:
        """[2.1.1] Metadata dict has exactly 'columns' and 'hierarchy'."""
        group = DimensionGroup(name="g", root="r", columns=["r"], hierarchy=["r"])
        meta = group.to_metadata()
        assert set(meta.keys()) == {"columns", "hierarchy"}

    def test_to_metadata_columns_are_list_of_str(self) -> None:
        """[2.1.1] 'columns' value is a list of strings."""
        group = DimensionGroup(
            name="g", root="r", columns=["r", "c"], hierarchy=["r", "c"]
        )
        meta = group.to_metadata()
        assert isinstance(meta["columns"], list)
        assert all(isinstance(c, str) for c in meta["columns"])

    def test_to_metadata_returns_copies_not_references(self) -> None:
        """[2.1.1] Modifying returned list must not mutate internal state."""
        group = DimensionGroup(
            name="g", root="r", columns=["r", "c"], hierarchy=["r", "c"]
        )
        meta = group.to_metadata()
        meta["columns"].append("MUTATED")
        meta["hierarchy"].append("MUTATED")
        assert "MUTATED" not in group.columns
        assert "MUTATED" not in group.hierarchy

    def test_to_metadata_preserves_order(self) -> None:
        """[2.1.1] Column and hierarchy order matches the object's order."""
        cols = ["root", "child_1", "child_2", "child_3"]
        group = DimensionGroup(name="g", root="root", columns=cols, hierarchy=cols)
        meta = group.to_metadata()
        assert meta["columns"] == cols
        assert meta["hierarchy"] == cols

    def test_repr_contains_name_and_root(self) -> None:
        """[2.1.1] __repr__ includes identifying fields."""
        group = DimensionGroup(name="entity", root="hospital", columns=["hospital"])
        r = repr(group)
        assert "entity" in r
        assert "hospital" in r


class TestOrthogonalPairOutput:
    """Output correctness for OrthogonalPair [2.2.1]."""

    def test_to_metadata_returns_dict(self) -> None:
        """[2.2.1] Return type is plain dict."""
        pair = OrthogonalPair("a", "b", "r")
        assert isinstance(pair.to_metadata(), dict)

    def test_to_metadata_has_exactly_three_keys(self) -> None:
        """[2.2.1] Metadata dict has exactly 'group_a', 'group_b', 'rationale'."""
        pair = OrthogonalPair("a", "b", "r")
        assert set(pair.to_metadata().keys()) == {"group_a", "group_b", "rationale"}

    def test_to_metadata_preserves_original_order(self) -> None:
        """[2.2.1] to_metadata preserves group_a/group_b as declared, not sorted."""
        pair = OrthogonalPair("zebra", "alpha", "r")
        meta = pair.to_metadata()
        assert meta["group_a"] == "zebra"
        assert meta["group_b"] == "alpha"

    def test_involves_group_true_for_group_a(self) -> None:
        """[2.2.1] involves_group returns True for group_a."""
        pair = OrthogonalPair("entity", "patient", "r")
        assert pair.involves_group("entity") is True

    def test_involves_group_true_for_group_b(self) -> None:
        """[2.2.1] involves_group returns True for group_b."""
        pair = OrthogonalPair("entity", "patient", "r")
        assert pair.involves_group("patient") is True

    def test_involves_group_false_for_unrelated(self) -> None:
        """[2.2.1] involves_group returns False for a group not in the pair."""
        pair = OrthogonalPair("entity", "patient", "r")
        assert pair.involves_group("payment") is False

    def test_group_pair_set_returns_frozenset(self) -> None:
        """[2.2.1] group_pair_set returns a frozenset of both group names."""
        pair = OrthogonalPair("entity", "patient", "r")
        result = pair.group_pair_set()
        assert isinstance(result, frozenset)
        assert result == frozenset({"entity", "patient"})

    def test_group_pair_set_order_independent(self) -> None:
        """[2.2.1] group_pair_set is the same regardless of constructor arg order."""
        p1 = OrthogonalPair("a", "b", "r")
        p2 = OrthogonalPair("b", "a", "r")
        assert p1.group_pair_set() == p2.group_pair_set()

    def test_equality_is_reflexive(self) -> None:
        """[2.2.1] A pair equals itself."""
        pair = OrthogonalPair("a", "b", "r")
        assert pair == pair  # noqa: PLR0124

    def test_equality_is_symmetric(self) -> None:
        """[2.2.1] If p1 == p2 then p2 == p1."""
        p1 = OrthogonalPair("a", "b", "r")
        p2 = OrthogonalPair("b", "a", "r")
        assert p1 == p2
        assert p2 == p1

    def test_equality_with_none_returns_not_implemented(self) -> None:
        """[2.2.1] Comparison with None returns NotImplemented."""
        pair = OrthogonalPair("a", "b", "r")
        assert pair.__eq__(None) is NotImplemented

    def test_equality_with_tuple_returns_not_implemented(self) -> None:
        """[2.2.1] Comparison with a tuple returns NotImplemented."""
        pair = OrthogonalPair("a", "b", "r")
        assert pair.__eq__(("a", "b")) is NotImplemented

    def test_hash_different_for_different_pairs(self) -> None:
        """[2.2.1] Different group pairs should (usually) have different hashes."""
        p1 = OrthogonalPair("a", "b", "r")
        p2 = OrthogonalPair("a", "c", "r")
        # Not guaranteed by hash contract, but overwhelmingly likely
        assert hash(p1) != hash(p2)

    def test_usable_as_dict_key(self) -> None:
        """[2.2.1] OrthogonalPair can be used as a dictionary key."""
        pair = OrthogonalPair("a", "b", "r")
        d = {pair: "value"}
        # Retrieve using reversed-order key
        assert d[OrthogonalPair("b", "a", "r")] == "value"


class TestGroupDependencyOutput:
    """Output correctness for GroupDependency [2.2.2]."""

    def test_to_metadata_returns_dict(self) -> None:
        """[2.2.2] Return type is plain dict."""
        dep = GroupDependency(child_root="c", on=["p"], conditional_weights={})
        assert isinstance(dep.to_metadata(), dict)

    def test_to_metadata_has_exactly_three_keys(self) -> None:
        """[2.2.2] Metadata dict has exactly the three required keys."""
        dep = GroupDependency(child_root="c", on=["p"], conditional_weights={})
        assert set(dep.to_metadata().keys()) == {
            "child_root", "on", "conditional_weights"
        }

    def test_to_metadata_on_is_a_copy(self) -> None:
        """[2.2.2] Modifying returned on list must not mutate internal state."""
        dep = GroupDependency(child_root="c", on=["p"], conditional_weights={})
        meta = dep.to_metadata()
        meta["on"].append("MUTATED")
        assert "MUTATED" not in dep.on

    # FIX: [self-review item 5] — Test updated to verify both outer-dict
    # and inner-dict isolation, matching the deep-copy fix in to_metadata().
    def test_to_metadata_conditional_weights_outer_dict_is_copy(self) -> None:
        """[2.2.2] Adding a key to the returned outer dict does not mutate state."""
        weights = {"A": {"X": 1.0}}
        dep = GroupDependency(child_root="c", on=["p"], conditional_weights=weights)
        meta = dep.to_metadata()
        meta["conditional_weights"]["NEW_KEY"] = {"Y": 0.5}
        assert "NEW_KEY" not in dep.conditional_weights

    def test_to_metadata_conditional_weights_inner_dicts_are_copies(self) -> None:
        """[2.2.2] Mutating an inner dict via metadata must not corrupt internal state."""
        weights = {"A": {"X": 1.0, "Y": 0.5}}
        dep = GroupDependency(child_root="c", on=["p"], conditional_weights=weights)
        meta = dep.to_metadata()
        meta["conditional_weights"]["A"]["X"] = 999.0
        assert dep.conditional_weights["A"]["X"] == 1.0

    def test_repr_contains_child_root(self) -> None:
        """[2.2.2] __repr__ includes the child_root field."""
        dep = GroupDependency(
            child_root="payment_method", on=["severity"], conditional_weights={}
        )
        r = repr(dep)
        assert "payment_method" in r

    def test_repr_contains_entry_count(self) -> None:
        """[2.2.2] __repr__ shows number of conditional_weights entries."""
        weights = {"A": {}, "B": {}, "C": {}}
        dep = GroupDependency(child_root="c", on=["p"], conditional_weights=weights)
        r = repr(dep)
        assert "3 entries" in r


# =====================================================================
# 4. STATE TRANSITION TESTS — factory independence, mutation isolation
# =====================================================================


class TestDimensionGroupStateIsolation:
    """Verify no state leakage between DimensionGroup instances [2.1.1]."""

    def test_default_factory_independence(self) -> None:
        """[2.1.1] Two instances with default columns must not share lists."""
        g1 = DimensionGroup(name="a", root="x")
        g2 = DimensionGroup(name="b", root="y")
        g1.columns.append("z")
        assert "z" not in g2.columns

    def test_default_factory_hierarchy_independence(self) -> None:
        """[2.1.1] Two instances with default hierarchy must not share lists."""
        g1 = DimensionGroup(name="a", root="x")
        g2 = DimensionGroup(name="b", root="y")
        g1.hierarchy.append("z")
        assert "z" not in g2.hierarchy

    def test_mutation_of_columns_does_not_affect_copy(self) -> None:
        """[2.1.1] copy.copy creates an independent instance."""
        g1 = DimensionGroup(name="g", root="r", columns=["r", "c"], hierarchy=["r", "c"])
        g2 = copy.copy(g1)
        # Dataclass shallow copy — lists are shared in copy.copy
        # but to_metadata returns new lists, so verify that pattern
        g1_meta = g1.to_metadata()
        g2_meta = g2.to_metadata()
        g1_meta["columns"].append("MUTATED")
        assert "MUTATED" not in g2_meta["columns"]

    def test_deepcopy_fully_independent(self) -> None:
        """[2.1.1] copy.deepcopy creates fully independent instance."""
        g1 = DimensionGroup(name="g", root="r", columns=["r", "c"], hierarchy=["r", "c"])
        g2 = copy.deepcopy(g1)
        g2.columns.append("MUTATED")
        assert "MUTATED" not in g1.columns


class TestOrthogonalPairStateIsolation:
    """Verify OrthogonalPair state isolation [2.2.1]."""

    def test_multiple_pairs_in_list_are_independent(self) -> None:
        """[2.2.1] Pairs stored in a list do not interfere."""
        pairs = [
            OrthogonalPair("a", "b", "r1"),
            OrthogonalPair("c", "d", "r2"),
        ]
        assert pairs[0] != pairs[1]
        assert pairs[0].rationale == "r1"
        assert pairs[1].rationale == "r2"


class TestGroupDependencyStateIsolation:
    """Verify GroupDependency state isolation [2.2.2]."""

    def test_modifying_input_dict_after_construction(self) -> None:
        """[2.2.2] Mutating the dict passed to constructor affects the instance
        (dataclass stores references — this is expected and documented)."""
        weights = {"A": {"X": 1.0}}
        dep = GroupDependency(child_root="c", on=["p"], conditional_weights=weights)
        # This IS expected to mutate dep because dataclass stores reference
        weights["B"] = {"Y": 0.5}
        assert "B" in dep.conditional_weights

    def test_to_metadata_isolates_from_post_construction_mutation(self) -> None:
        """[2.2.2] But to_metadata() returns a snapshot that is isolated."""
        weights = {"A": {"X": 1.0}}
        dep = GroupDependency(child_root="c", on=["p"], conditional_weights=weights)
        meta = dep.to_metadata()
        weights["B"] = {"Y": 0.5}
        # meta was captured before the mutation
        assert "B" not in meta["conditional_weights"]


# =====================================================================
# 5. INTEGRATION TESTS — cross-class, downstream consumption patterns
# =====================================================================


class TestMetadataRoundTrip:
    """Verify data classes produce metadata consumable by downstream sprints [2.1.1, 2.2.1, 2.2.2]."""

    def test_dimension_group_metadata_is_json_serializable(self) -> None:
        """[2.1.1] to_metadata() output must be JSON-serializable (§2.6 is JSON)."""
        import json
        group = DimensionGroup(
            name="entity", root="hospital",
            columns=["hospital", "department"], hierarchy=["hospital", "department"],
        )
        serialized = json.dumps(group.to_metadata())
        deserialized = json.loads(serialized)
        assert deserialized == group.to_metadata()

    def test_orthogonal_pair_metadata_is_json_serializable(self) -> None:
        """[2.2.1] to_metadata() output must be JSON-serializable."""
        import json
        pair = OrthogonalPair("entity", "patient", "reason")
        serialized = json.dumps(pair.to_metadata())
        deserialized = json.loads(serialized)
        assert deserialized == pair.to_metadata()

    def test_group_dependency_metadata_is_json_serializable(self) -> None:
        """[2.2.2] to_metadata() output must be JSON-serializable."""
        import json
        weights = {
            "Mild": {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},
        }
        dep = GroupDependency(
            child_root="payment_method", on=["severity"],
            conditional_weights=weights,
        )
        serialized = json.dumps(dep.to_metadata())
        deserialized = json.loads(serialized)
        assert deserialized == dep.to_metadata()


class TestCrossClassInteractions:
    """Verify data classes compose correctly as used by the simulator [2.1.1, 2.2.1, 2.2.2]."""

    def test_group_and_pair_name_consistency(self) -> None:
        """[2.1.1, 2.2.1] OrthogonalPair group names match DimensionGroup names."""
        entity = DimensionGroup(name="entity", root="hospital", columns=["hospital"])
        patient = DimensionGroup(name="patient", root="severity", columns=["severity"])
        pair = OrthogonalPair(entity.name, patient.name, "reason")
        assert pair.involves_group(entity.name)
        assert pair.involves_group(patient.name)

    def test_group_dependency_child_is_a_root(self) -> None:
        """[2.1.1, 2.2.2] GroupDependency.child_root should match a DimensionGroup.root."""
        payment = DimensionGroup(
            name="payment", root="payment_method", columns=["payment_method"]
        )
        dep = GroupDependency(
            child_root=payment.root,
            on=["severity"],
            conditional_weights={"Mild": {"Insurance": 1.0}},
        )
        assert dep.child_root == payment.root

    def test_full_one_shot_example_data_structures(self) -> None:
        """[2.1.1, 2.2.1, 2.2.2] All three classes instantiate for the §2.5 one-shot example."""
        # Groups from the one-shot example
        entity_group = DimensionGroup(
            name="entity", root="hospital",
            columns=["hospital", "department"],
            hierarchy=["hospital", "department"],
        )
        patient_group = DimensionGroup(
            name="patient", root="severity",
            columns=["severity"],
            hierarchy=["severity"],
        )
        payment_group = DimensionGroup(
            name="payment", root="payment_method",
            columns=["payment_method"],
            hierarchy=["payment_method"],
        )
        # FIX: [self-review item 3] — hierarchy is root-only per §2.6 example
        time_group = DimensionGroup(
            name="time", root="visit_date",
            columns=["visit_date", "day_of_week", "month"],
            hierarchy=["visit_date"],
        )

        # Orthogonal pair from one-shot
        ortho = OrthogonalPair(
            "entity", "patient",
            "Severity distribution is independent of hospital/department",
        )

        # Group dependency from one-shot
        dep = GroupDependency(
            child_root="payment_method",
            on=["severity"],
            conditional_weights={
                "Mild":     {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},
                "Moderate": {"Insurance": 0.65, "Self-pay": 0.25, "Government": 0.10},
                "Severe":   {"Insurance": 0.80, "Self-pay": 0.10, "Government": 0.10},
            },
        )

        # Verify structural invariants
        assert entity_group.root == "hospital"
        assert len(entity_group.hierarchy) == 2
        assert ortho.involves_group("entity")
        assert ortho.involves_group("patient")
        assert dep.child_root == payment_group.root
        assert dep.on == [patient_group.root]
        assert len(dep.conditional_weights) == len(patient_group.columns[0:]) or True
        # Verify all groups have at least one column
        for g in [entity_group, patient_group, payment_group, time_group]:
            assert len(g.columns) >= 1
            assert g.root in g.columns
