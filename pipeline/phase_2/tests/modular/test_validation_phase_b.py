"""Tests for Phase B: degenerate-contingency-table skip in orthogonal independence check.

Mirrors the layout of test_validation_phase_a.py — one class per behavior,
fixtures inlined per test (no shared pytest fixtures), data built via
np.random.default_rng(seed) for reproducibility.

See docs/soft_failure_fix/validation/PINGYUE_OPENAI_CAL_ANALYSIS.md §4.2 +
§8.2 for the root cause of the 3 orthogonal_* failures
(campus×year 1×1 / campus×quarter 1×4 / year×university 3×1) — chi² requires
≥2×2 for non-zero d.f., so degenerate tables have no statistical power and
must soft-pass rather than hard-fail.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline.phase_2.validation.structural import (
    ORTHOGONAL_MIN_DIM,
    check_orthogonal_independence,
)


def _ortho_meta() -> dict:
    """Minimal meta dict declaring one orthogonal pair (root_a, root_b)."""
    return {
        "dimension_groups": {
            "g1": {"hierarchy": ["root_a"]},
            "g2": {"hierarchy": ["root_b"]},
        },
        "orthogonal_groups": [{"group_a": "g1", "group_b": "g2"}],
    }


# --------------------------------------------------------------------------
# Degenerate contingency tables (1×1 / 1×N / N×1) → soft-pass, not fail.
# --------------------------------------------------------------------------


class TestOrthogonalDegenerateSkip:
    """min(ct.shape) < ORTHOGONAL_MIN_DIM → passed=True + 'skipped' detail."""

    def test_one_x_one_table_skipped(self):
        # 1×1: both columns constant — mirrors agpds_33d84d2c9b campus×year.
        df = pd.DataFrame({
            "root_a": ["X"] * 50,
            "root_b": ["K"] * 50,
        })
        checks = check_orthogonal_independence(df, _ortho_meta())
        assert len(checks) == 1
        assert checks[0].passed is True
        detail = str(checks[0].detail).lower()
        assert "skipped" in detail
        assert "(1, 1)" in str(checks[0].detail)

    def test_one_x_n_table_skipped(self):
        # 1×4: root_a constant, root_b has 4 levels — mirrors agpds_503613ba96
        # campus×academic_quarter.
        df = pd.DataFrame({
            "root_a": ["X"] * 40,
            "root_b": (["Q1", "Q2", "Q3", "Q4"] * 10),
        })
        checks = check_orthogonal_independence(df, _ortho_meta())
        assert len(checks) == 1
        assert checks[0].passed is True
        assert "skipped" in str(checks[0].detail).lower()
        assert "(1, 4)" in str(checks[0].detail)

    def test_n_x_one_table_skipped(self):
        # 3×1: root_a has 3 levels, root_b constant — mirrors agpds_8180fe4e2c
        # year×university.
        df = pd.DataFrame({
            "root_a": (["2020", "2021", "2022"] * 10),
            "root_b": ["U"] * 30,
        })
        checks = check_orthogonal_independence(df, _ortho_meta())
        assert len(checks) == 1
        assert checks[0].passed is True
        assert "skipped" in str(checks[0].detail).lower()
        assert "(3, 1)" in str(checks[0].detail)

    def test_skip_detail_preserves_shape(self):
        # Detail must include shape so a postmortem reader can see which axis
        # collapsed without needing to re-query the master table.
        df = pd.DataFrame({
            "root_a": ["X"] * 20,
            "root_b": (["K", "L"] * 10),
        })
        checks = check_orthogonal_independence(df, _ortho_meta())
        assert "(1, 2)" in str(checks[0].detail)

    def test_skip_detail_mentions_threshold(self):
        # Detail must indicate the threshold so reader knows why we skipped
        # (mirrors Phase A's `skipped_cells=N (n<10)` convention).
        df = pd.DataFrame({
            "root_a": ["X"] * 10,
            "root_b": ["K"] * 10,
        })
        checks = check_orthogonal_independence(df, _ortho_meta())
        assert "2x2" in str(checks[0].detail) or "2×2" in str(checks[0].detail)


# --------------------------------------------------------------------------
# Non-degenerate path (chi² actually runs) — must be unchanged by Phase B.
# --------------------------------------------------------------------------


class TestOrthogonalNonDegenerateUnchanged:
    """ct.shape ≥ ORTHOGONAL_MIN_DIM × ORTHOGONAL_MIN_DIM path runs chi² as before."""

    def test_independent_data_still_passes(self):
        # Seeded independent random data → p > 0.05 → passed=True.
        # Mirrors test_validation_structural.py::test_passes_for_seeded_independent_data.
        rng = np.random.default_rng(20260507)
        df = pd.DataFrame({
            "root_a": rng.choice(["X", "Y"], size=400),
            "root_b": rng.choice(["K", "L"], size=400),
        })
        checks = check_orthogonal_independence(df, _ortho_meta())
        assert len(checks) == 1
        assert checks[0].passed is True
        # detail must come from chi² branch, not skip branch
        assert "skipped" not in str(checks[0].detail).lower()
        # Either χ² (unicode) or "p=" should be present.
        assert "p=" in str(checks[0].detail)

    def test_dependent_data_still_fails(self):
        # Hand-constructed strong dependence: root_a == "X" ⇒ mostly "K";
        # root_a == "Y" ⇒ mostly "L". Keeps both shape dims ≥ 2 while pushing
        # p far below 0.05.
        rows = (
            [("X", "K")] * 195 + [("X", "L")] * 5
            + [("Y", "L")] * 195 + [("Y", "K")] * 5
        )
        df = pd.DataFrame(rows, columns=["root_a", "root_b"])
        checks = check_orthogonal_independence(df, _ortho_meta())
        assert len(checks) == 1
        assert checks[0].passed is False
        # Must be the chi² fail branch, not a skip.
        assert "skipped" not in str(checks[0].detail).lower()
        assert "p=" in str(checks[0].detail)


# --------------------------------------------------------------------------
# Constant export contract — anyone importing the module gets the right value.
# --------------------------------------------------------------------------


class TestOrthogonalConstant:
    def test_min_dim_is_two(self):
        # chi² requires ≥2×2 for non-zero degrees of freedom. The constant
        # exists so it's a single-point edit if we ever need to widen
        # (e.g., to enforce textbook expected-count ≥ 5 by raising the floor).
        assert ORTHOGONAL_MIN_DIM == 2
