"""Path D tests — sparse-cell + KS over-sensitivity in check_stochastic_ks.

Covers:
  - n<KS_MIN_CELL_SIZE cells are skipped (no per-cell Check; aggregate
    treats them as untested).
  - Cells at/above the threshold are tested against a Bonferroni-corrected
    alpha (KS_BASE_ALPHA / K).
  - Aggregate passes iff per-cell pass-rate ≥ KS_AGGREGATE_PASS_RATE.
  - All cells skipped → single passed-True Check ("no testable cells").
  - K=1 (no predictor cells) → alpha unchanged (no correction).
  - Detail string surfaces α, K, failed/passed cell labels with (n, D, p).

See docs/soft_failure_fix/PATH_D_KS_SPARSE_CELLS.md for design rationale.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from pipeline.phase_2.validation.statistical import (
    KS_AGGREGATE_PASS_RATE,
    KS_BASE_ALPHA,
    KS_DETAIL_CELL_CAP,
    KS_MIN_CELL_SIZE,
    check_stochastic_ks,
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _gaussian_meta(col: str = "y") -> dict:
    """Schema meta for a gaussian stochastic measure with no predictors
    (yields a single "global" cell)."""
    return {
        "columns": {
            col: {
                "type": "measure",
                "measure_type": "stochastic",
                "family": "gaussian",
                "param_model": {
                    "mu": {"intercept": 0.0},
                    "sigma": {"intercept": 1.0},
                },
            },
        },
    }


def _gaussian_meta_with_predictor(
    col: str = "y", predictor: str = "g", levels: tuple = ("a", "b"),
) -> dict:
    """Schema meta for a gaussian stochastic measure whose mu varies by
    a single categorical predictor — produces one cell per level."""
    return {
        "columns": {
            predictor: {"type": "categorical"},
            col: {
                "type": "measure",
                "measure_type": "stochastic",
                "family": "gaussian",
                "param_model": {
                    "mu": {
                        "intercept": 0.0,
                        "effects": {predictor: {lv: 0.0 for lv in levels}},
                    },
                    "sigma": {"intercept": 1.0},
                },
            },
        },
    }


def _fit_sample(n: int, mu: float = 0.0, sigma: float = 1.0, seed: int = 0) -> np.ndarray:
    return np.random.default_rng(seed).normal(mu, sigma, size=n)


def _outlier_sample(n: int, seed: int = 0) -> np.ndarray:
    """Sample drawn from a distribution far from declared N(0, 1) — KS
    should reject with p ≈ 0."""
    return np.random.default_rng(seed).normal(50.0, 1.0, size=n)


# --------------------------------------------------------------------------
# Skip behavior
# --------------------------------------------------------------------------

class TestSmallCellsSkipped:
    def test_below_threshold_skipped(self):
        """A global cell with n=KS_MIN_CELL_SIZE-1 yields no testable cells."""
        n = KS_MIN_CELL_SIZE - 1
        df = pd.DataFrame({"y": _fit_sample(n)})
        checks = check_stochastic_ks(df, "y", _gaussian_meta())
        assert len(checks) == 1
        c = checks[0]
        assert c.passed
        assert "no testable cells" in (c.detail or "").lower()
        assert "small-n" in (c.detail or "")

    def test_at_threshold_tested(self):
        """A global cell with n=KS_MIN_CELL_SIZE crosses the gate."""
        n = KS_MIN_CELL_SIZE
        df = pd.DataFrame({"y": _fit_sample(n, seed=42)})
        checks = check_stochastic_ks(df, "y", _gaussian_meta())
        assert len(checks) == 1
        c = checks[0]
        # detail should report K=1
        assert "K=1" in (c.detail or "")
        # alpha == base alpha when K=1 (no Bonferroni correction)
        m = re.search(r"α=([\d.eE+-]+)", c.detail or "")
        assert m is not None
        assert abs(float(m.group(1)) - KS_BASE_ALPHA) < 1e-9

    def test_all_cells_below_threshold_silent_pass(self):
        """Multi-cell scenario where every cell is small-n: aggregate
        emits a single passed-True Check noting the silent-pass."""
        # Predictor with 2 levels, each gets n=10 rows → both below 30.
        df = pd.DataFrame({
            "g": ["a"] * 10 + ["b"] * 10,
            "y": np.concatenate([_fit_sample(10, seed=1), _fit_sample(10, seed=2)]),
        })
        meta = _gaussian_meta_with_predictor()
        checks = check_stochastic_ks(df, "y", meta)
        assert len(checks) == 1
        c = checks[0]
        assert c.passed
        assert "no testable cells" in (c.detail or "").lower()


# --------------------------------------------------------------------------
# Bonferroni alpha
# --------------------------------------------------------------------------

class TestBonferroniAlpha:
    def test_alpha_with_multiple_cells(self):
        """K=2 cells → alpha = base / 2."""
        df = pd.DataFrame({
            "g": ["a"] * KS_MIN_CELL_SIZE + ["b"] * KS_MIN_CELL_SIZE,
            "y": np.concatenate([
                _fit_sample(KS_MIN_CELL_SIZE, seed=1),
                _fit_sample(KS_MIN_CELL_SIZE, seed=2),
            ]),
        })
        meta = _gaussian_meta_with_predictor()
        checks = check_stochastic_ks(df, "y", meta)
        assert len(checks) == 1
        c = checks[0]
        m = re.search(r"α=([\d.eE+-]+)", c.detail or "")
        assert m is not None
        assert abs(float(m.group(1)) - KS_BASE_ALPHA / 2) < 1e-9
        assert "K=2" in (c.detail or "")


# --------------------------------------------------------------------------
# Aggregate pass-rate
# --------------------------------------------------------------------------

class TestAggregatePassRate:
    def test_single_cell_fails_when_p_below_alpha(self):
        """K=1: outlier sample → single cell fails → aggregate fails."""
        df = pd.DataFrame({"y": _outlier_sample(KS_MIN_CELL_SIZE * 5)})
        checks = check_stochastic_ks(df, "y", _gaussian_meta())
        assert len(checks) == 1
        c = checks[0]
        assert not c.passed
        assert "Failed cells:" in (c.detail or "")

    def test_aggregate_passes_at_high_rate(self):
        """K=10 cells, 9 fit / 1 strong outlier → pass rate 0.9 ≥
        KS_AGGREGATE_PASS_RATE → aggregate passes."""
        levels = tuple(f"L{i}" for i in range(10))
        groups = []
        ys = []
        for i, lv in enumerate(levels):
            groups.extend([lv] * KS_MIN_CELL_SIZE)
            if i == 0:
                # one strong-outlier cell
                ys.extend(_outlier_sample(KS_MIN_CELL_SIZE, seed=i).tolist())
            else:
                ys.extend(_fit_sample(KS_MIN_CELL_SIZE, seed=100 + i).tolist())
        df = pd.DataFrame({"g": groups, "y": ys})
        meta = _gaussian_meta_with_predictor(levels=levels)
        checks = check_stochastic_ks(df, "y", meta)
        assert len(checks) == 1
        c = checks[0]
        # 9/10 passes → rate=0.9 ≥ threshold → overall passed
        assert c.passed, c.detail
        assert "9/10" in (c.detail or "")

    def test_aggregate_fails_when_rate_below_threshold(self):
        """K=10 cells, 7 fit / 3 outlier → rate=0.7 < threshold → fail."""
        levels = tuple(f"L{i}" for i in range(10))
        groups = []
        ys = []
        for i, lv in enumerate(levels):
            groups.extend([lv] * KS_MIN_CELL_SIZE)
            if i < 3:
                ys.extend(_outlier_sample(KS_MIN_CELL_SIZE, seed=i).tolist())
            else:
                ys.extend(_fit_sample(KS_MIN_CELL_SIZE, seed=100 + i).tolist())
        df = pd.DataFrame({"g": groups, "y": ys})
        meta = _gaussian_meta_with_predictor(levels=levels)
        checks = check_stochastic_ks(df, "y", meta)
        assert len(checks) == 1
        c = checks[0]
        assert not c.passed, c.detail
        assert "7/10" in (c.detail or "")


# --------------------------------------------------------------------------
# Detail observability
# --------------------------------------------------------------------------

class TestDetailString:
    def test_detail_contains_threshold_constants(self):
        """Sanity: detail should expose α, K, threshold so downstream
        readers can verify the semantic."""
        df = pd.DataFrame({"y": _fit_sample(KS_MIN_CELL_SIZE, seed=42)})
        c = check_stochastic_ks(df, "y", _gaussian_meta())[0]
        d = c.detail or ""
        assert "α=" in d
        assert "K=" in d
        assert "threshold" in d.lower()

    def test_detail_caps_failed_cell_listing(self):
        """When > KS_DETAIL_CELL_CAP cells fail, detail truncates and
        notes the overflow."""
        # Build 12 outlier cells so we have more failures than the cap.
        K = KS_DETAIL_CELL_CAP + 2
        levels = tuple(f"L{i}" for i in range(K))
        groups = []
        ys = []
        for i, lv in enumerate(levels):
            groups.extend([lv] * KS_MIN_CELL_SIZE)
            ys.extend(_outlier_sample(KS_MIN_CELL_SIZE, seed=i).tolist())
        df = pd.DataFrame({"g": groups, "y": ys})
        meta = _gaussian_meta_with_predictor(levels=levels)
        c = check_stochastic_ks(df, "y", meta)[0]
        assert not c.passed
        # Overflow marker should appear in the failed-cells section
        assert "+2 more" in (c.detail or "")
