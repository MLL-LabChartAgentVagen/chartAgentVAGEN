"""Tests for Phase D: seasonal_anomaly fail-detail enrichment.

Mirrors test_validation_phase_b.py: per-behavior class, inline data, no
shared fixtures. See
docs/soft_failure_fix/mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md
for context.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline.phase_2.validation.pattern_checks import check_seasonal_anomaly


def _meta() -> dict:
    return {
        "dimension_groups": {
            "time": {"columns": ["visit_date"], "hierarchy": ["visit_date"]},
        }
    }


def _high_cv_df(seed: int = 0) -> pd.DataFrame:
    """Library-checkout-style DF: baseline_mean ~8100, baseline_std ~7000
    (high CV ~0.86). Window June–Aug; injection magnitude 0.35 yields
    z ≈ 0.05 — same regime as the agpds_14b7f7487e production failure."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    rows = []
    win_start, win_end = pd.Timestamp("2024-06-01"), pd.Timestamp("2024-08-01")
    for d in dates:
        base = 8100 + rng.normal(0, 7000)
        if win_start <= d <= win_end:
            rows.append({"visit_date": d, "value": base * 1.35})
        else:
            rows.append({"visit_date": d, "value": base})
    return pd.DataFrame(rows)


def _pattern(**overrides) -> dict:
    p = {
        "type": "seasonal_anomaly",
        "target": "value == value",
        "col": "value",
        "params": {
            "anomaly_window": ["2024-06-01", "2024-08-01"],
            "magnitude": 0.35,
        },
    }
    p["params"].update(overrides)
    return p


class TestSeasonalFailDetailEnrichment:
    def test_fail_detail_includes_declared_magnitude(self):
        df = _high_cv_df()
        result = check_seasonal_anomaly(df, _pattern(), _meta())
        assert result.passed is False
        assert "declared_magnitude=0.35" in result.detail

    def test_fail_detail_includes_required_magnitude_at_threshold(self):
        df = _high_cv_df()
        result = check_seasonal_anomaly(df, _pattern(), _meta())
        assert result.passed is False
        # required = z_threshold * baseline_std / |baseline_mean|
        # 1.5 * 7000 / 8100 ≈ 1.30 ± rng noise; assert structure only
        assert "required_magnitude_at_threshold>=" in result.detail

    def test_fail_detail_uses_abs_for_negative_magnitude(self):
        """Negative magnitude: |M| in required, but declared shows the sign."""
        df = _high_cv_df()
        result = check_seasonal_anomaly(df, _pattern(magnitude=-0.35), _meta())
        assert result.passed is False
        assert "declared_magnitude=-0.35" in result.detail
        idx = result.detail.find("required_magnitude_at_threshold>=")
        assert idx >= 0
        after = result.detail[idx + len("required_magnitude_at_threshold>="):]
        assert not after.startswith("-")

    def test_fail_detail_omits_required_when_baseline_mean_zero(self):
        """Defensive: if baseline_mean == 0 exactly, division would explode; omit."""
        # 2024 is a leap year → 366 daily rows. Window Jun 1–Aug 1 = 62 days.
        # Baseline = 304 rows (even). Alternate +5/-5 → baseline_mean = 0 exactly,
        # baseline_std ≈ 5 (non-zero, so the earlier "baseline_std==0" branch
        # does not pre-empt our magnitude block).
        dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
        win_start, win_end = pd.Timestamp("2024-06-01"), pd.Timestamp("2024-08-01")
        rows = []
        baseline_idx = 0
        for d in dates:
            if win_start <= d <= win_end:
                rows.append({"visit_date": d, "value": 1.05})
            else:
                v = 5.0 if baseline_idx % 2 == 0 else -5.0
                rows.append({"visit_date": d, "value": v})
                baseline_idx += 1
        df = pd.DataFrame(rows)
        # Sanity-check the construction
        baseline_mean = df.loc[~df["visit_date"].between(win_start, win_end), "value"].mean()
        assert abs(baseline_mean) < 1e-12, f"setup error: baseline_mean={baseline_mean}"
        result = check_seasonal_anomaly(df, _pattern(magnitude=0.05), _meta())
        assert "declared_magnitude=0.05" in result.detail
        assert "required_magnitude_at_threshold" not in result.detail

    def test_fail_detail_omits_extra_when_no_magnitude_param(self):
        """If pattern lacks magnitude, omit both new fields gracefully."""
        df = _high_cv_df()
        pat = _pattern()
        del pat["params"]["magnitude"]
        result = check_seasonal_anomaly(df, pat, _meta())
        assert "declared_magnitude" not in result.detail
        assert "required_magnitude_at_threshold" not in result.detail
        assert "z=" in result.detail
        assert "baseline_std=" in result.detail

    def test_passing_seasonal_unchanged_detail_format(self):
        """Pass path: detail still starts with z= (backward compatible)."""
        rng = np.random.default_rng(0)
        dates = pd.date_range("2024-01-01", "2024-06-30", freq="D")
        win_start, win_end = pd.Timestamp("2024-05-15"), pd.Timestamp("2024-06-30")
        rows = []
        for d in dates:
            if win_start <= d <= win_end:
                rows.append({"visit_date": d, "value": 10.0 + rng.normal(0, 1)})
            else:
                rows.append({"visit_date": d, "value": 5.0 + rng.normal(0, 1)})
        df = pd.DataFrame(rows)
        result = check_seasonal_anomaly(df, _pattern(magnitude=1.0), _meta())
        assert result.passed is True
        assert result.detail.startswith("z=")
