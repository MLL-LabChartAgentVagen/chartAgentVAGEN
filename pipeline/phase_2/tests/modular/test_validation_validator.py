"""
Tests for SchemaAwareValidator orchestration logic.

Tested class:
- SchemaAwareValidator
"""
from __future__ import annotations

import pytest
import pandas as pd
import numpy as np
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


class TestSchemaAwareValidatorRealE2E:
    """Run SchemaAwareValidator unmocked against real DataFrames.

    Closes T1.1 in `docs/TEST_AUDIT_2026-05-07.md`. Every existing test in
    this file mocks every L1/L3 check; if a regression in `_run_l1` swallowed
    an exception, mis-ordered args, or skipped the marginal_weights /
    measure_finiteness calls (validator.py:172-175), no test would catch it.
    These two tests run the real check chain end-to-end on a real DataFrame.
    """

    def test_validates_real_dataframe_end_to_end_passes(self):
        """A clean seeded DataFrame matching its metadata triggers all_passed."""
        rng = np.random.default_rng(42)
        n = 400
        df = pd.DataFrame({
            # 3-value categorical, marginals close to declared weights.
            "hospital": rng.choice(
                ["A", "B", "C"], size=n, p=[0.5, 0.3, 0.2]
            ),
            # finite, non-null gaussian measure.
            "revenue": rng.normal(100.0, 10.0, size=n),
        })
        meta = {
            "total_rows": n,
            "columns": {
                "hospital": {
                    "type": "categorical",
                    "values": ["A", "B", "C"],
                    "weights": [0.5, 0.3, 0.2],
                    "cardinality": 3,
                    "parent": None,
                    "group": "g1",
                },
                "revenue": {
                    "type": "measure",
                    "measure_type": "stochastic",
                    "family": "gaussian",
                    "param_model": {
                        "mu": {"intercept": 100.0, "effects": {}},
                        "sigma": {"intercept": 10.0, "effects": {}},
                    },
                },
            },
            "dimension_groups": {
                "g1": {"columns": ["hospital"], "hierarchy": ["hospital"]},
            },
            "orthogonal_groups": [],
            "group_dependencies": [],
            "measure_dag_order": ["revenue"],
            "patterns": [],
        }

        report = SchemaAwareValidator(meta).validate(df, patterns=[])

        # Surfacing failure names in the assertion makes regressions diagnosable.
        failed = [(c.name, c.detail) for c in report.failures]
        assert report.all_passed, f"Unexpected failures: {failed}"
        # At least one check from each L1 family must have run.
        check_names = {c.name for c in report.checks}
        assert "row_count" in check_names
        assert "cardinality_hospital" in check_names
        assert "measure_dag_acyclic" in check_names
        assert any(n.startswith("marginal_weights_") for n in check_names)
        assert any(n.startswith("finiteness_") for n in check_names)

    def test_validates_real_dataframe_catches_cardinality_mismatch(self):
        """When the DataFrame has only 2 unique values but meta declares 5,
        L1 cardinality check must fail with a name that points at the
        offending column."""
        df = pd.DataFrame({"hospital": ["A", "B"] * 50})
        meta = {
            "total_rows": 100,
            "columns": {
                "hospital": {
                    "type": "categorical",
                    "values": ["A", "B", "C", "D", "E"],
                    "weights": [0.2, 0.2, 0.2, 0.2, 0.2],
                    "cardinality": 5,
                    "parent": None,
                    "group": "g1",
                },
            },
            "dimension_groups": {
                "g1": {"columns": ["hospital"], "hierarchy": ["hospital"]},
            },
            "orthogonal_groups": [],
            "group_dependencies": [],
            "measure_dag_order": [],
            "patterns": [],
        }

        report = SchemaAwareValidator(meta).validate(df, patterns=[])

        assert not report.all_passed
        # The cardinality check is the one we expect to fail here.
        cardinality_failures = [
            c for c in report.failures if c.name == "cardinality_hospital"
        ]
        assert len(cardinality_failures) == 1
        assert "5" in str(cardinality_failures[0].detail) or \
               "cardinality" in str(cardinality_failures[0].detail).lower()
