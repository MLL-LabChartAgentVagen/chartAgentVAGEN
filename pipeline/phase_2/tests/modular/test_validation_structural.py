"""
Tests for L1 Structural Validation utilities.

Tested functions:
- check_row_count
- check_categorical_cardinality
- check_orthogonal_independence
- check_measure_dag_acyclic
"""
from __future__ import annotations

import re

import pytest
import pandas as pd
import numpy as np

from pipeline.phase_2.validation.structural import (
    check_row_count,
    check_categorical_cardinality,
    check_orthogonal_independence,
    check_measure_dag_acyclic,
)


def _extract_chi2_p(detail: str) -> float:
    """Pull the float p-value out of a `χ² p=0.4321 (...)` detail string.

    The validator formats results as `χ² p={p_val:.4f} (>0.05 = independent)`
    in `validation/structural.py:171`. Anchoring on this format lets failure-
    side tests assert on the numeric p-value rather than just `passed`.
    """
    m = re.search(r"p=([\d.eE+-]+)", detail)
    assert m is not None, f"Could not extract p-value from detail: {detail!r}"
    return float(m.group(1))


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
    """Validate the §2.6 L1 chi-squared independence guarantee.

    Spec: `p > 0.05` ⇒ independent ([validation/structural.py:170](../../validation/structural.py#L170)).
    Both the passing and failing branches must have deterministic coverage —
    no flaky `np.random.choice(...)` without a seed.
    """

    def test_passes_for_seeded_independent_data(self):
        rng = np.random.default_rng(20260507)
        df = pd.DataFrame({
            "root_a": rng.choice(["X", "Y"], size=400),
            "root_b": rng.choice(["K", "L"], size=400),
        })
        meta = {
            "dimension_groups": {
                "g1": {"hierarchy": ["root_a"]},
                "g2": {"hierarchy": ["root_b"]},
            },
            "orthogonal_groups": [{"group_a": "g1", "group_b": "g2"}],
        }
        checks = check_orthogonal_independence(df, meta)
        assert len(checks) == 1
        assert checks[0].passed
        # Lock down the threshold semantic: passing branch must have p > 0.05.
        p_val = _extract_chi2_p(checks[0].detail)
        assert p_val > 0.05

    def test_fails_for_seeded_dependent_data(self):
        # Hand-constructed strongly-dependent contingency: when root_a == "X",
        # root_b is overwhelmingly "K"; when root_a == "Y", root_b is "L".
        # Adds two off-diagonal entries to keep both shape dims ≥ 2 while
        # still driving p far below 0.05.
        rows = (
            [("X", "K")] * 195 + [("X", "L")] * 5
            + [("Y", "L")] * 195 + [("Y", "K")] * 5
        )
        df = pd.DataFrame(rows, columns=["root_a", "root_b"])
        meta = {
            "dimension_groups": {
                "g1": {"hierarchy": ["root_a"]},
                "g2": {"hierarchy": ["root_b"]},
            },
            "orthogonal_groups": [{"group_a": "g1", "group_b": "g2"}],
        }
        checks = check_orthogonal_independence(df, meta)
        assert len(checks) == 1
        assert not checks[0].passed
        p_val = _extract_chi2_p(checks[0].detail)
        assert p_val <= 0.05

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
