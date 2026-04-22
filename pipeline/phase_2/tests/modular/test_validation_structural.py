"""
Tests for L1 Structural Validation utilities.

Tested functions:
- check_row_count
- check_categorical_cardinality
- check_orthogonal_independence
- check_measure_dag_acyclic
"""
from __future__ import annotations

import pytest
import pandas as pd
import numpy as np

from pipeline.phase_2.validation.structural import (
    check_row_count,
    check_categorical_cardinality,
    check_orthogonal_independence,
    check_measure_dag_acyclic,
)


class TestCheckRowCount:
    def test_within_tolerance(self):
        df = pd.DataFrame({"A": range(950)}) # Within 10% of 1000
        meta = {"total_rows": 1000}
        check = check_row_count(df, meta)
        assert check.passed
        assert "deviation" in str(check.detail)

    def test_outside_tolerance(self):
        df = pd.DataFrame({"A": range(850)}) # 15% off 1000
        meta = {"total_rows": 1000}
        check = check_row_count(df, meta)
        assert not check.passed


class TestCheckCategoricalCardinality:
    def test_matches_declared_cardinality(self):
        # 3 unique values
        df = pd.DataFrame({"hospital": ["A", "B", "C", "A", "B"]})
        meta = {
            "columns": {
                "hospital": {"type": "categorical", "cardinality": 3}
            }
        }
        checks = check_categorical_cardinality(df, meta)
        assert len(checks) == 1
        assert checks[0].passed
        assert checks[0].name == "cardinality_hospital"

    def test_mismatches_declared_cardinality(self):
        df = pd.DataFrame({"hospital": ["A", "B", "A", "B"]})
        meta = {
            "columns": {
                "hospital": {"type": "categorical", "cardinality": 3}
            }
        }
        checks = check_categorical_cardinality(df, meta)
        assert not checks[0].passed


class TestCheckOrthogonalIndependence:
    def test_independent_features(self):
        # We need a large enough sample of independent distributions to avoid random failure of p-value >= 0.05
        # 400 samples of purely random uniform choices
        df = pd.DataFrame({
            "root_a": np.random.choice(["X", "Y"], size=400),
            "root_b": np.random.choice(["K", "L"], size=400)
        })
        meta = {
            "dimension_groups": {
                "g1": {"hierarchy": ["root_a"]},
                "g2": {"hierarchy": ["root_b"]}
            },
            "orthogonal_groups": [
                {"group_a": "g1", "group_b": "g2"}
            ]
        }
        checks = check_orthogonal_independence(df, meta)
        assert len(checks) == 1
        # Random failures are possible but extremely rare with N=400 independent coinflips. 
        # If it fails frequently we can seed the numpy array.
        assert checks[0].passed

    def test_degenerate_contingency_table(self):
        # Only 1 unique value in one of the columns
        df = pd.DataFrame({
            "root_a": ["X", "X", "X"],
            "root_b": ["K", "L", "K"]
        })
        meta = {
            "dimension_groups": {
                "g1": {"hierarchy": ["root_a"]},
                "g2": {"hierarchy": ["root_b"]}
            },
            "orthogonal_groups": [
                {"group_a": "g1", "group_b": "g2"}
            ]
        }
        checks = check_orthogonal_independence(df, meta)
        assert not checks[0].passed
        assert "Degenerate contingency table" in str(checks[0].detail)


class TestCheckMeasureDagAcyclic:
    def test_acyclic_dag_order(self):
        meta = {"measure_dag_order": ["A", "B", "C"]}
        check = check_measure_dag_acyclic(meta)
        assert check.passed

    def test_cyclic_dag_order_shows_duplicates(self):
        # A cycle during extraction emits the node twice if it was hacked or failed verification
        meta = {"measure_dag_order": ["A", "B", "C", "A"]}
        check = check_measure_dag_acyclic(meta)
        assert not check.passed
        assert "Duplicate nodes" in str(check.detail)
