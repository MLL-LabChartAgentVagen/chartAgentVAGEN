"""
Tests for SchemaAwareValidator orchestration logic.

Tested class:
- SchemaAwareValidator
"""
from __future__ import annotations

import pytest
import pandas as pd
from unittest.mock import patch

from pipeline.phase_2.validation.validator import SchemaAwareValidator
from pipeline.phase_2.types import Check, ValidationReport


class TestSchemaAwareValidator:
    
    @patch("pipeline.phase_2.validation.validator._l1.check_row_count")
    @patch("pipeline.phase_2.validation.validator._l1.check_categorical_cardinality")
    @patch("pipeline.phase_2.validation.validator._l1.check_orthogonal_independence")
    @patch("pipeline.phase_2.validation.validator._l1.check_measure_dag_acyclic")
    def test_validates_l1_layer(
        self,
        mock_acyclic,
        mock_orthogonal,
        mock_cardinality,
        mock_row_count
    ):
        """L1 checks are executed and aggregated."""
        # Setup mocks
        mock_row_count.return_value = Check("row_count", True)
        mock_cardinality.return_value = [Check("cardinality_a", True)]
        mock_orthogonal.return_value = []
        mock_acyclic.return_value = Check("measure_dag_acyclic", True)

        val = SchemaAwareValidator(meta={"total_rows": 100})
        df = pd.DataFrame()
        
        report = val.validate(df)
        
        # Verify calls
        mock_row_count.assert_called_once_with(df, val.meta)
        mock_cardinality.assert_called_once_with(df, val.meta)
        mock_orthogonal.assert_called_once_with(df, val.meta)
        mock_acyclic.assert_called_once_with(val.meta)
        
        # Verify aggregation
        assert isinstance(report, ValidationReport)
        assert len(report.checks) == 3
        assert report.all_passed is True

    @patch("pipeline.phase_2.validation.validator._l1.check_row_count")
    @patch("pipeline.phase_2.validation.validator._l3.check_outlier_entity")
    @patch("pipeline.phase_2.validation.validator._l3.check_trend_break")
    def test_validates_l3_layer_with_patterns(
        self,
        mock_trend_break,
        mock_outlier_entity,
        mock_row_count
    ):
        """L3 checks are executed when patterns are provided."""
        # Setup L1 pass
        mock_row_count.return_value = Check("row_count", True)
        
        # Setup L3 failures to test failure collection
        mock_outlier_entity.return_value = Check("pattern_outlier_entity_a", False, "Too small")
        mock_trend_break.return_value = Check("pattern_trend_break_b", False, "No break")
        
        patterns = [
            {"type": "outlier_entity", "col": "a"},
            {"type": "trend_break", "col": "b"}
        ]
        
        val = SchemaAwareValidator(meta={"total_rows": 100})
        df = pd.DataFrame()
        
        report = val.validate(df, patterns=patterns)
        
        # Verify L3 calls
        mock_outlier_entity.assert_called_once_with(df, patterns[0])
        mock_trend_break.assert_called_once_with(df, patterns[1], val.meta)
        
        # Verify failures collection
        assert not report.all_passed
        assert len(report.failures) == 2
        assert report.failures[0].name == "pattern_outlier_entity_a"
        assert report.failures[1].name == "pattern_trend_break_b"

    @patch("pipeline.phase_2.validation.validator._l1.check_row_count")
    def test_l3_exception_safety(self, mock_row_count):
        """If an L3 check raises an exception, it converts to a failed Check rather than crashing."""
        mock_row_count.return_value = Check("row_count", True)
        
        with patch("pipeline.phase_2.validation.validator._l3.check_outlier_entity") as mock_l3:
            mock_l3.side_effect = Exception("Runtime error in pandas during groupby")
            
            patterns = [{"type": "outlier_entity", "col": "a"}]
            val = SchemaAwareValidator(meta={"total_rows": 100})
            
            report = val.validate(pd.DataFrame(), patterns=patterns)
            
            assert not report.all_passed
            assert len(report.failures) == 1
            assert "Exception during L3 check" in str(report.failures[0].detail)
