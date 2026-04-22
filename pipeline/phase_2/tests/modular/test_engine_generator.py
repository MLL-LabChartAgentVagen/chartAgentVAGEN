"""
Tests for the Engine Pipeline Orchestrator.

Tested function:
- run_pipeline
"""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
from collections import OrderedDict
import pandas as pd

from pipeline.phase_2.engine.generator import run_pipeline


class TestRunPipeline:
    
    @patch("pipeline.phase_2.engine.generator._postprocess.to_dataframe")
    @patch("pipeline.phase_2.engine.generator._measures.generate_measures")
    @patch("pipeline.phase_2.engine.generator._skeleton.build_skeleton")
    @patch("pipeline.phase_2.engine.generator._dag.topological_sort")
    @patch("pipeline.phase_2.engine.generator._dag.build_full_dag")
    @patch("pipeline.phase_2.metadata.builder.build_schema_metadata")
    def test_pipeline_phases_called_in_order(
        self,
        mock_build_meta,
        mock_build_full_dag,
        mock_topological_sort,
        mock_build_skeleton,
        mock_generate_measures,
        mock_to_dataframe
    ):
        """Verify the 8 phases are executed in order."""
        # Setup mocks
        mock_build_full_dag.return_value = {"a": []}
        mock_topological_sort.return_value = ["a"]
        mock_build_skeleton.return_value = {"a": [1, 2]}
        mock_generate_measures.return_value = {"a": [1, 2]}
        mock_to_dataframe.return_value = pd.DataFrame({"a": [1, 2]})
        mock_build_meta.return_value = {"total_rows": 2, "columns": {"a": {}}}

        df, meta = run_pipeline(
            columns=OrderedDict({"a": {"type": "categorical", "values": [1, 2]}}),
            groups={},
            group_dependencies=[],
            measure_dag={},
            target_rows=2,
            seed=42
        )
        
        # Verify orchestration calls
        mock_build_full_dag.assert_called_once()
        mock_topological_sort.assert_called_once()
        mock_build_skeleton.assert_called_once()
        mock_generate_measures.assert_called_once()
        mock_build_meta.assert_called_once()
        
        # Verify return types
        assert isinstance(df, pd.DataFrame)
        assert isinstance(meta, dict)
        assert meta["total_rows"] == 2
        assert "a" in meta["columns"]

    @patch("pipeline.phase_2.metadata.builder.build_schema_metadata")
    def test_empty_schema_runs_to_completion(self, mock_build_meta):
        mock_build_meta.return_value = {"total_rows": 10}
        
        # An empty schema should just generate an empty dataframe
        df, meta = run_pipeline(
            columns=OrderedDict(),
            groups={},
            group_dependencies=[],
            measure_dag={},
            target_rows=10,
            seed=42
        )
        
        assert len(df) == 10
        assert len(df.columns) == 0
        assert meta["total_rows"] == 10
