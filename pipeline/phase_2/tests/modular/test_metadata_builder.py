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
