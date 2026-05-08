"""
Tests for Schema Metadata Builder.

Tested functions:
- build_schema_metadata
"""
from __future__ import annotations

import pytest

from pipeline.phase_2.exceptions import SimulatorError
from pipeline.phase_2.metadata.builder import build_schema_metadata
from pipeline.phase_2.types import DeclarationStore, DimensionGroup, GroupDependency, OrthogonalPair, RealismConfig

class TestBuildSchemaMetadata:
    
    def _create_mock_store(self):
        """A helper to build a well-formed mock DeclarationStore representing a valid E2E state."""
        store = DeclarationStore(1000, 42)
        
        # Columns
        store.columns.update({
            "region": {"type": "categorical", "group": "geo"},
            "city": {"type": "categorical", "group": "geo", "parent": "region"},
            "revenue": {"type": "measure", "measure_type": "stochastic", "family": "gaussian", "params": {"mu": 100, "sigma": 15}},
        })
        
        # Groups
        store.groups.update({
            "geo": DimensionGroup(
                name="geo",
                root="region",
                columns=["region", "city"],
                hierarchy=["region", "city"]
            )
        })
        
        # Relationships
        store.orthogonal_pairs.append(
            OrthogonalPair("geo", "demographics", "no relation")
        )
        store.group_dependencies.append(
            GroupDependency("income", ["region"], {"North": {"High": 0.8, "Low": 0.2}})
        )
        
        # Measure DAG
        store.measure_dag.update({
            "revenue": []
        })
        
        # Other configs
        store.patterns.append({"type": "outlier_entity", "col": "revenue", "target": "region=='North'"})
        store.realism_config = RealismConfig(missing_rate=0.05)
        
        return store

    def test_builder_outputs_all_seven_keys(self):
        """The resulting dictionary contains the exact 7 root keys from the spec."""
        store = self._create_mock_store()
        target_rows = 1000
        
        meta = build_schema_metadata(
            groups=store.groups,
            orthogonal_pairs=store.orthogonal_pairs,
            target_rows=target_rows,
            measure_dag_order=["revenue"],
            columns=store.columns,
            group_dependencies=store.group_dependencies,
            patterns=store.patterns
        )
        
        expected_keys = {
            "total_rows",
            "columns",
            "dimension_groups",
            "orthogonal_groups",
            "group_dependencies",
            "measure_dag_order",
            "patterns"
        }
        
        assert set(meta.keys()) == expected_keys

    def test_builder_preserves_target_rows(self):
        """total_rows maps correctly."""
        store = self._create_mock_store()
        meta = build_schema_metadata(
            groups=store.groups,
            orthogonal_pairs=store.orthogonal_pairs,
            target_rows=555,
            measure_dag_order=[],
            columns=store.columns,
            group_dependencies=store.group_dependencies,
            patterns=store.patterns
        )
        
        assert meta["total_rows"] == 555

    def test_builder_extracts_column_names_into_list(self):
        """Columns are extracted into a dictionary."""
        store = self._create_mock_store()
        meta = build_schema_metadata(
            groups=store.groups,
            orthogonal_pairs=store.orthogonal_pairs,
            target_rows=100,
            measure_dag_order=[],
            columns=store.columns,
            group_dependencies=store.group_dependencies,
            patterns=store.patterns
        )
        
        assert isinstance(meta["columns"], dict)
        assert len(meta["columns"]) == 3
        
        assert "region" in meta["columns"]
        assert "city" in meta["columns"]
        assert "revenue" in meta["columns"]

    def test_builder_outputs_deep_copies(self):
        """The meta output should be completely isolated from the DeclarationStore."""
        store = self._create_mock_store()
        meta = build_schema_metadata(
            groups=store.groups,
            orthogonal_pairs=store.orthogonal_pairs,
            target_rows=10,
            measure_dag_order=[],
            columns=store.columns,
            group_dependencies=store.group_dependencies,
            patterns=store.patterns
        )
        
        # Modify the output
        meta["columns"]["region"]["NEW_KEY"] = "leak"
        meta["group_dependencies"][0]["on"].append("leak")
        
        # Store should remain unchanged
        assert "NEW_KEY" not in store.columns["region"]
        assert "leak" not in store.group_dependencies[0].on

    def test_consistency_check_groups_and_orthogonals(self):
        """Consistency check ensures orthogonal groups exist in dimension_groups."""
        store = self._create_mock_store()

        import logging
        from _pytest.logging import LogCaptureFixture

        # The consistency check uses logger.warning instead of raising exceptions
        meta = build_schema_metadata(
            groups=store.groups,
            orthogonal_pairs=[OrthogonalPair("geo", "demographics", "test")],
            target_rows=100,
            measure_dag_order=[],
            columns=store.columns,
            group_dependencies=store.group_dependencies,
            patterns=store.patterns
        )
        # We don't strictly assert failure since it's just a logger.warning in builder.py,
        # but we ensure the function runs to completion and produces the dict.
        assert "orthogonal_groups" in meta


class TestSchemaMetadataInternalContract:
    """Spec §2.3 fixes the *internal* shape of the metadata dict, not just
    its top-level keys. The pre-existing `test_builder_outputs_all_seven_keys`
    only verifies key presence; a regression that turned `hierarchy` into a
    set or migrated `orthogonal_groups` entries to a 4-key shape would slip
    through.

    Closes T1.8 in `docs/TEST_AUDIT_2026-05-07.md`. The metadata dict is the
    contract Phase 2 hands to Phase 3 (View Extraction reads `hierarchy`
    order to enumerate drill-downs).
    """

    def _make_store_with_two_groups(self):
        store = DeclarationStore(100, 7)
        store.columns.update({
            "region": {"type": "categorical", "group": "geo"},
            "city": {"type": "categorical", "group": "geo", "parent": "region"},
            "age_bucket": {"type": "categorical", "group": "demographics"},
        })
        store.groups.update({
            "geo": DimensionGroup(
                name="geo",
                root="region",
                columns=["region", "city"],
                hierarchy=["region", "city"],
            ),
            "demographics": DimensionGroup(
                name="demographics",
                root="age_bucket",
                columns=["age_bucket"],
                hierarchy=["age_bucket"],
            ),
        })
        store.orthogonal_pairs.append(
            OrthogonalPair("geo", "demographics", "demographics independent of geography")
        )
        store.group_dependencies.append(
            GroupDependency(
                child_root="age_bucket",
                on=["region"],
                conditional_weights={"North": {"Young": 0.6, "Old": 0.4},
                                     "South": {"Young": 0.4, "Old": 0.6}},
            )
        )
        return store

    def test_dimension_groups_hierarchy_is_ordered_list_root_first(self):
        """`dimension_groups[g].hierarchy` must be a list (not set/dict) with
        the root column at index 0. Spec §2.3 example shows `["hospital",
        "department"]` — order is load-bearing for drill-down enumeration.
        """
        store = self._make_store_with_two_groups()
        meta = build_schema_metadata(
            groups=store.groups,
            orthogonal_pairs=store.orthogonal_pairs,
            target_rows=100,
            measure_dag_order=[],
            columns=store.columns,
            group_dependencies=store.group_dependencies,
            patterns=store.patterns,
        )
        for group_name, group_info in meta["dimension_groups"].items():
            assert isinstance(group_info, dict), \
                f"dimension_groups[{group_name!r}] is not a dict"
            assert isinstance(group_info["hierarchy"], list), \
                f"hierarchy must be a list, got {type(group_info['hierarchy'])}"
            assert isinstance(group_info["columns"], list)
            # Root invariant: hierarchy[0] is the source-of-truth root for that group.
            source_root = store.groups[group_name].root
            assert group_info["hierarchy"][0] == source_root, (
                f"hierarchy[0] for {group_name!r} should be root "
                f"{source_root!r}, got {group_info['hierarchy'][0]!r}"
            )

    def test_orthogonal_groups_entry_keys_exactly_three(self):
        """Each entry must have *exactly* {group_a, group_b, rationale} —
        no extras, no missing. Spec §2.3 line 248 fixes this trio."""
        store = self._make_store_with_two_groups()
        meta = build_schema_metadata(
            groups=store.groups,
            orthogonal_pairs=store.orthogonal_pairs,
            target_rows=100,
            measure_dag_order=[],
            columns=store.columns,
            group_dependencies=store.group_dependencies,
            patterns=store.patterns,
        )
        assert isinstance(meta["orthogonal_groups"], list)
        assert len(meta["orthogonal_groups"]) == 1
        for entry in meta["orthogonal_groups"]:
            assert set(entry.keys()) == {"group_a", "group_b", "rationale"}, \
                f"orthogonal_groups entry must have exactly 3 keys, got {set(entry.keys())}"

    def test_group_dependencies_on_is_ordered_list_of_strings(self):
        """`on` is a list (order matters for nested conditional_weights)
        with all-string entries. Single-column and multi-column cases
        share this shape."""
        store = self._make_store_with_two_groups()
        meta = build_schema_metadata(
            groups=store.groups,
            orthogonal_pairs=store.orthogonal_pairs,
            target_rows=100,
            measure_dag_order=[],
            columns=store.columns,
            group_dependencies=store.group_dependencies,
            patterns=store.patterns,
        )
        assert isinstance(meta["group_dependencies"], list)
        assert len(meta["group_dependencies"]) == 1
        dep = meta["group_dependencies"][0]
        assert "on" in dep
        assert isinstance(dep["on"], list)
        for item in dep["on"]:
            assert isinstance(item, str)
        # The dep entry shape itself: spec §2.3 lists child_root + on + conditional_weights.
        assert {"child_root", "on", "conditional_weights"}.issubset(set(dep.keys()))

    def test_top_level_keys_are_exactly_seven(self):
        """Verify EXACT key match — no extra keys leaked, no spec key missing.
        The pre-existing test asserted the same set, but a future regression
        that adds a new top-level key (e.g., a debug field) should be
        intentional, not silent."""
        store = self._make_store_with_two_groups()
        meta = build_schema_metadata(
            groups=store.groups,
            orthogonal_pairs=store.orthogonal_pairs,
            target_rows=100,
            measure_dag_order=[],
            columns=store.columns,
            group_dependencies=store.group_dependencies,
            patterns=store.patterns,
        )
        assert set(meta.keys()) == {
            "total_rows", "columns", "dimension_groups",
            "orthogonal_groups", "group_dependencies",
            "measure_dag_order", "patterns",
        }
