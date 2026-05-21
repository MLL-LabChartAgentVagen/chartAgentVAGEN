"""Tests for Phase A: n-aware group_dep_* / marginal_weights_* thresholds.

Mirrors the layout of test_validation_ks_path_d.py — one class per behavior,
fixtures inlined per test (no shared pytest fixtures), data built via
np.random.default_rng(seed) for reproducibility.

See docs/soft_failure_fix/validation/PINGYUE_OPENAI_CAL_ANALYSIS.md §6 + §8.1
for the §6 root cause of all 7 remaining drift failures and the design
rationale for the Wald 95% CI threshold.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline.phase_2.validation.statistical import (
    GROUP_DEP_BASE_DELTA,
    GROUP_DEP_MIN_CELL_SIZE,
    GROUP_DEP_Z_95,
    _wald_dev_threshold,
    check_group_dependency_transitions,
)
from pipeline.phase_2.validation.structural import check_marginal_weights


class TestWaldThreshold:
    """The Wald threshold is 0.10 + 1.96·√(p̂(1-p̂)/n)."""

    def test_threshold_at_p_half_n_30(self):
        # At p=0.5 n=30: 1.96·√(0.25/30) = 1.96·0.0913 = 0.1789
        # So threshold ≈ 0.10 + 0.1789 = 0.2789
        t = _wald_dev_threshold(n=30, p_hat=0.5)
        assert abs(t - 0.2789) < 1e-3

    def test_threshold_at_large_n_collapses_to_base(self):
        # n=10000, p=0.5: 1.96·√(0.25/10000) = 1.96·0.005 = 0.0098 ≈ 0
        # So threshold ≈ 0.10 + 0.01 = 0.11
        t = _wald_dev_threshold(n=10000, p_hat=0.5)
        assert 0.105 < t < 0.115

    def test_threshold_at_small_n_widens(self):
        # n=14 p=0.66: 1.96·√(0.66·0.34/14) = 1.96·0.1266 = 0.2481
        # threshold = 0.10 + 0.248 = 0.348 — the §6 root-cause case.
        t = _wald_dev_threshold(n=14, p_hat=0.66)
        assert 0.34 < t < 0.36

    def test_threshold_at_p_zero_floor_only(self):
        # p̂=0 → Wald term is 0 → threshold = base only.
        # Guards against zero-variance overconfidence on never-observed levels.
        t = _wald_dev_threshold(n=100, p_hat=0.0)
        assert abs(t - GROUP_DEP_BASE_DELTA) < 1e-9

    def test_threshold_at_zero_n_falls_back_to_base(self):
        # n=0 (pathological) should not divide by zero — fall back to base.
        t = _wald_dev_threshold(n=0, p_hat=0.5)
        assert t == GROUP_DEP_BASE_DELTA


# --------------------------------------------------------------------------
# check_group_dependency_transitions — per-(cell, child_level) Wald CI
# --------------------------------------------------------------------------

def _gd_meta(
    child_root: str,
    on: list[str],
    conditional_weights: dict,
) -> dict:
    """Minimal meta dict matching check_group_dependency_transitions contract."""
    return {
        "group_dependencies": [{
            "child_root": child_root,
            "on": on,
            "conditional_weights": conditional_weights,
        }]
    }


class TestGroupDepSmallCellSkipped:
    """Cells with n < GROUP_DEP_MIN_CELL_SIZE contribute no per-level checks."""

    def test_below_threshold_skipped_passes_overall(self):
        # 9 rows all parent="X" (n_cell=9 < 10), child highly skewed
        # vs declared 50/50 — would fail under 0.10 cutoff but skipped here.
        df = pd.DataFrame({
            "parent": ["X"] * 9,
            "child":  ["A"] * 9,
        })
        meta = _gd_meta("child", ["parent"], {"X": {"A": 0.5, "B": 0.5}})
        checks = check_group_dependency_transitions(df, meta)
        assert len(checks) == 1
        assert checks[0].name == "group_dep_child"
        assert checks[0].passed is True
        # Detail should record the skip transparently
        assert "skipped" in checks[0].detail.lower() or "n<" in checks[0].detail

    def test_at_threshold_tested(self):
        # n_cell=10 exactly → in scope
        # All A → dev=0.5, p̂=0.5, n=10 → threshold = 0.10 + 1.96·√(0.025) ≈ 0.41
        # 0.5 > 0.41 so should FAIL (real magnitude error, not noise)
        df = pd.DataFrame({
            "parent": ["X"] * 10,
            "child":  ["A"] * 10,
        })
        meta = _gd_meta("child", ["parent"], {"X": {"A": 0.5, "B": 0.5}})
        checks = check_group_dependency_transitions(df, meta)
        assert checks[0].passed is False


class TestGroupDepWaldClears:
    """Sampling-noise deviations within Wald CI pass (the Phase A win)."""

    def test_noise_within_wald_envelope_passes(self):
        # The §6 root-cause case in miniature:
        # n_cell=14, declared p=0.66, empirical = 5/14 = 0.357, dev=0.303.
        # Wald threshold at n=14 p=0.66 ≈ 0.348 → dev < threshold → PASS.
        df = pd.DataFrame({
            "parent": ["X"] * 14,
            "child":  ["A"] * 5 + ["B"] * 9,
        })
        meta = _gd_meta(
            "child",
            ["parent"],
            {"X": {"A": 0.66, "B": 0.34}},
        )
        checks = check_group_dependency_transitions(df, meta)
        assert checks[0].passed is True

    def test_aligned_distribution_passes_at_large_n(self):
        rng = np.random.default_rng(42)
        children = rng.choice(["A", "B"], size=1000, p=[0.3, 0.7])
        df = pd.DataFrame({"parent": ["X"] * 1000, "child": children})
        meta = _gd_meta("child", ["parent"], {"X": {"A": 0.3, "B": 0.7}})
        checks = check_group_dependency_transitions(df, meta)
        assert checks[0].passed is True


class TestGroupDepMagnitudeStillFails:
    """Large deviations break through Wald CI — true LLM bugs are caught."""

    def test_large_dev_at_n_100_fails(self):
        # n=100 p=0.5 → Wald threshold ≈ 0.10 + 1.96·0.05 = 0.198
        # All "A" → dev = 0.5 > 0.198 → FAIL
        df = pd.DataFrame({
            "parent": ["X"] * 100,
            "child":  ["A"] * 100,
        })
        meta = _gd_meta("child", ["parent"], {"X": {"A": 0.5, "B": 0.5}})
        checks = check_group_dependency_transitions(df, meta)
        assert checks[0].passed is False

    def test_huge_dev_at_n_14_still_fails(self):
        # n=14 p=0.50 → Wald threshold ≈ 0.10 + 1.96·0.1336 = 0.362
        # All "A" → dev=0.5 > 0.362 → FAIL.
        # Important: even n<30 shouldn't whitewash magnitude errors.
        df = pd.DataFrame({
            "parent": ["X"] * 14,
            "child":  ["A"] * 14,
        })
        meta = _gd_meta("child", ["parent"], {"X": {"A": 0.5, "B": 0.5}})
        checks = check_group_dependency_transitions(df, meta)
        assert checks[0].passed is False


class TestGroupDepAllPassAggregation:
    """One bad cell fails the whole Check (all-pass strict aggregation)."""

    def test_one_bad_cell_fails_aggregate(self):
        # parent=X cell aligned, parent=Y cell badly off (n=50, all A vs 50/50)
        df = pd.DataFrame({
            "parent": ["X"] * 100 + ["Y"] * 50,
            "child":  (["A"] * 30 + ["B"] * 70) + ["A"] * 50,
        })
        meta = _gd_meta(
            "child",
            ["parent"],
            {"X": {"A": 0.3, "B": 0.7}, "Y": {"A": 0.5, "B": 0.5}},
        )
        checks = check_group_dependency_transitions(df, meta)
        assert checks[0].passed is False
        assert "Y" in checks[0].detail


class TestGroupDepNestedParents:
    """Two-level parents (on=['p1','p2']) — leaf-cell n is what matters."""

    def test_nested_skip_only_small_leaf(self):
        # 4 leaf cells: (X,a)=n=20 aligned, (X,b)=n=5 skip, (Y,a)=n=20 aligned,
        # (Y,b)=n=20 aligned. With the small leaf skipped, whole Check passes.
        df = pd.DataFrame({
            "p1": ["X"] * 25 + ["Y"] * 40,
            "p2": ["a"] * 20 + ["b"] * 5 + ["a"] * 20 + ["b"] * 20,
            "child": (
                ["A"] * 6 + ["B"] * 14   # (X,a) ≈ 30/70
                + ["A"] * 5              # (X,b) skipped (n=5)
                + ["A"] * 6 + ["B"] * 14 # (Y,a) ≈ 30/70
                + ["A"] * 6 + ["B"] * 14 # (Y,b) ≈ 30/70
            ),
        })
        meta = _gd_meta(
            "child",
            ["p1", "p2"],
            {
                "X": {"a": {"A": 0.3, "B": 0.7}, "b": {"A": 0.3, "B": 0.7}},
                "Y": {"a": {"A": 0.3, "B": 0.7}, "b": {"A": 0.3, "B": 0.7}},
            },
        )
        checks = check_group_dependency_transitions(df, meta)
        assert checks[0].passed is True


class TestGroupDepDetailString:
    """Detail string must surface (n, dev, threshold) per offending cell."""

    def test_detail_contains_threshold_and_offender(self):
        df = pd.DataFrame({
            "parent": ["X"] * 100,
            "child":  ["A"] * 100,
        })
        meta = _gd_meta("child", ["parent"], {"X": {"A": 0.5, "B": 0.5}})
        checks = check_group_dependency_transitions(df, meta)
        detail = checks[0].detail
        assert "parent" in detail
        assert "n=100" in detail
        # Surfaces both the empirical deviation and the per-cell threshold
        assert "dev=" in detail
        assert "thresh=" in detail or "threshold=" in detail
