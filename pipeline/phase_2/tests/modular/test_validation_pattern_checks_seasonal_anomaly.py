"""Tests for check_seasonal_anomaly (IS-4)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline.phase_2.validation.pattern_checks import check_seasonal_anomaly


HOSPITALS = ["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"]


def _meta_with_entity_and_time() -> dict:
    return {
        "dimension_groups": {
            "entity": {"columns": ["hospital"], "hierarchy": ["hospital"]},
            "time": {"columns": ["visit_date"], "hierarchy": ["visit_date"]},
        }
    }


def _build_df(
    baseline_mean: float = 5.0,
    window_mean: float = 5.0,
    sigma: float = 1.0,
) -> pd.DataFrame:
    """Daily rows over Jan–Jun 2024. Rows in the May 15 – Jun 30 window
    are sampled with `window_mean`; rows elsewhere with `baseline_mean`.
    Within-row noise sigma controls how detectable a window shift is.
    """
    rng = np.random.default_rng(0)
    dates = pd.date_range("2024-01-01", "2024-06-30", freq="D")
    win_start = pd.Timestamp("2024-05-15")
    win_end = pd.Timestamp("2024-06-30")
    rows = []
    for d in dates:
        if win_start <= d <= win_end:
            rows.append({"visit_date": d, "value": window_mean + rng.normal(0, sigma)})
        else:
            rows.append({"visit_date": d, "value": baseline_mean + rng.normal(0, sigma)})
    return pd.DataFrame(rows)


def _pattern(**param_overrides) -> dict:
    p = {
        "type": "seasonal_anomaly",
        "target": "value == value",
        "col": "value",
        "params": {
            "anomaly_window": ["2024-05-15", "2024-06-30"],
            "magnitude": 0.5,
        },
    }
    p["params"].update(param_overrides)
    return p


class TestCheckSeasonalAnomaly:
    def test_anomalous_window_passes(self):
        # Window mean 10 vs baseline mean 5 with σ≈1 → z >> 1.5.
        df = _build_df(baseline_mean=5.0, window_mean=10.0, sigma=1.0)
        result = check_seasonal_anomaly(
            df, _pattern(), _meta_with_entity_and_time()
        )
        assert result.passed is True
        assert "z=" in result.detail

    def test_stable_window_fails(self):
        # Window mean ≈ baseline → z ≈ 0 < 1.5 → fail.
        df = _build_df(baseline_mean=5.0, window_mean=5.0, sigma=1.0)
        result = check_seasonal_anomaly(
            df, _pattern(), _meta_with_entity_and_time()
        )
        assert result.passed is False
        assert "z=" in result.detail

    def test_empty_window_graceful_fail(self):
        df = _build_df(baseline_mean=5.0, window_mean=5.0, sigma=1.0)
        # Window in 2030 — outside the dataframe's range.
        pattern = _pattern(anomaly_window=["2030-01-01", "2030-01-31"])
        result = check_seasonal_anomaly(
            df, pattern, _meta_with_entity_and_time()
        )
        assert result.passed is False
        assert "matches no rows" in result.detail

    def test_missing_temporal_column_graceful_fail(self):
        df = _build_df()
        meta = {
            "dimension_groups": {
                "entity": {
                    "columns": ["hospital"], "hierarchy": ["hospital"],
                },
            }  # no "time" group
        }
        result = check_seasonal_anomaly(df, _pattern(), meta)
        assert result.passed is False
        assert "temporal_col" in result.detail

    def test_constant_column_graceful_fail(self):
        # Constant value everywhere → baseline_std = 0 → undefined.
        dates = pd.date_range("2024-01-01", "2024-06-30", freq="D")
        df = pd.DataFrame({"visit_date": dates, "value": 5.0})
        result = check_seasonal_anomaly(
            df, _pattern(), _meta_with_entity_and_time()
        )
        assert result.passed is False
        assert "Baseline std" in result.detail

    def test_custom_z_threshold_blocks_pass(self):
        # Modest shift (window=7, baseline=5) passes 1.5 but fails 50.
        df = _build_df(baseline_mean=5.0, window_mean=7.0, sigma=1.0)
        permissive = check_seasonal_anomaly(
            df, _pattern(z_threshold=1.5), _meta_with_entity_and_time()
        )
        strict = check_seasonal_anomaly(
            df, _pattern(z_threshold=50.0), _meta_with_entity_and_time()
        )
        assert permissive.passed is True
        assert strict.passed is False

    def test_default_window_uses_last_10_percent(self):
        # No anomaly_window provided. Spike the last ~10% of dates so the
        # defensive fallback exercises and reports a shift.
        rng = np.random.default_rng(0)
        dates = pd.date_range("2024-01-01", "2024-06-30", freq="D")
        tmin, tmax = dates.min(), dates.max()
        cutoff = tmin + (tmax - tmin) * 0.9
        rows = []
        for d in dates:
            if d >= cutoff:
                rows.append({"visit_date": d, "value": 10.0 + rng.normal(0, 0.5)})
            else:
                rows.append({"visit_date": d, "value": 5.0 + rng.normal(0, 0.5)})
        df = pd.DataFrame(rows)
        pattern = {
            "type": "seasonal_anomaly",
            "target": "value == value",
            "col": "value",
            "params": {"magnitude": 0.5},  # no anomaly_window
        }
        result = check_seasonal_anomaly(
            df, pattern, _meta_with_entity_and_time()
        )
        assert result.passed is True

    def test_baseline_too_small_graceful_fail(self):
        # Anomaly window covers everything except 1 row → baseline len < 2.
        dates = pd.date_range("2024-01-01", "2024-01-10", freq="D")
        df = pd.DataFrame({
            "visit_date": dates, "value": [1.0] + [5.0] * 9,
        })
        pattern = _pattern(anomaly_window=["2024-01-02", "2024-01-10"])
        result = check_seasonal_anomaly(
            df, pattern, _meta_with_entity_and_time()
        )
        assert result.passed is False
        assert "baseline rows" in result.detail
