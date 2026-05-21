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
