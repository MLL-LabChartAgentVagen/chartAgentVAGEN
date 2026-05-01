"""Tests for Phase 2 realism injection — covers ``inject_censoring``,
the ordering inside ``inject_realism``, and the schema validation that
``set_realism`` performs on the censoring config (DS-1)."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import pytest

from pipeline.phase_2.engine.realism import inject_censoring, inject_realism
from pipeline.phase_2.sdk.relationships import set_realism


class TestInjectCensoring:
    def test_right_censoring_masks_above_threshold(self):
        df = pd.DataFrame({"x": [10.0, 20.0, 30.0, 40.0, 50.0]})
        rng = np.random.default_rng(0)

        result = inject_censoring(
            df, {"x": {"type": "right", "threshold": 25.0}}, rng,
        )

        assert result["x"].isna().tolist() == [False, False, True, True, True]
        assert result["x"].iloc[0] == 10.0
        assert result["x"].iloc[1] == 20.0

    def test_left_censoring_masks_below_threshold(self):
        df = pd.DataFrame({"x": [10.0, 20.0, 30.0, 40.0, 50.0]})
        rng = np.random.default_rng(0)

        result = inject_censoring(
            df, {"x": {"type": "left", "threshold": 25.0}}, rng,
        )

        assert result["x"].isna().tolist() == [True, True, False, False, False]
        assert result["x"].iloc[2] == 30.0
        assert result["x"].iloc[4] == 50.0

    def test_interval_censoring_masks_out_of_range(self):
        df = pd.DataFrame({"x": [-1.0, 0.0, 5.0, 10.0, 11.0]})
        rng = np.random.default_rng(0)

        result = inject_censoring(
            df, {"x": {"type": "interval", "low": 0.0, "high": 10.0}}, rng,
        )

        # Endpoints (0.0 and 10.0) are inside the interval; only -1 and 11 NaN.
        assert result["x"].isna().tolist() == [True, False, False, False, True]
        assert result["x"].iloc[1] == 0.0
        assert result["x"].iloc[3] == 10.0

    def test_missing_column_warns_and_skips(self, caplog):
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
        rng = np.random.default_rng(0)

        with caplog.at_level(logging.WARNING, logger="pipeline.phase_2.engine.realism"):
            result = inject_censoring(
                df, {"missing_col": {"type": "right", "threshold": 0.0}}, rng,
            )

        assert result["x"].isna().sum() == 0
        assert any(
            "missing_col" in rec.message and "skipping" in rec.message
            for rec in caplog.records
        )

    def test_empty_config_is_noop(self):
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
        rng = np.random.default_rng(0)

        result = inject_censoring(df, {}, rng)

        pd.testing.assert_frame_equal(result, df)

    def test_unknown_type_raises(self):
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
        rng = np.random.default_rng(0)

        with pytest.raises(ValueError, match="Unknown censoring type"):
            inject_censoring(
                df, {"x": {"type": "bogus", "threshold": 0.0}}, rng,
            )

    def test_multiple_columns_independently_censored(self):
        df = pd.DataFrame({
            "a": [1.0, 2.0, 3.0, 4.0],
            "b": [10.0, 20.0, 30.0, 40.0],
            "c": [-5.0, 0.0, 5.0, 50.0],
        })
        rng = np.random.default_rng(0)

        result = inject_censoring(
            df,
            {
                "a": {"type": "right", "threshold": 2.5},
                "b": {"type": "left", "threshold": 25.0},
                "c": {"type": "interval", "low": 0.0, "high": 10.0},
            },
            rng,
        )

        assert result["a"].isna().tolist() == [False, False, True, True]
        assert result["b"].isna().tolist() == [True, True, False, False]
        assert result["c"].isna().tolist() == [True, False, False, True]


class TestInjectRealismOrdering:
    def test_censoring_runs_before_missing(self):
        """With missing_rate=0, censoring still applies via inject_realism."""
        df = pd.DataFrame({"x": [10.0, 20.0, 30.0, 40.0, 50.0]})
        rng = np.random.default_rng(0)

        result = inject_realism(
            df,
            {
                "censoring": {"x": {"type": "right", "threshold": 25.0}},
                "missing_rate": 0.0,
                "dirty_rate": 0.0,
            },
            columns={},
            rng=rng,
        )

        # Cells 30, 40, 50 should be NaN; cells 10, 20 untouched.
        assert result["x"].isna().sum() == 3
        assert result["x"].iloc[0] == 10.0
        assert result["x"].iloc[1] == 20.0

    def test_censoring_visible_through_missing_pipeline(self):
        """All values exceed the right-censor threshold, so all cells in
        the censored column are NaN regardless of missing_rate.  Verifies
        censoring ran first (otherwise some cells could survive the
        post-censor distribution and stay non-NaN with rate 0.0).
        """
        df = pd.DataFrame({"x": [100.0] * 50})
        rng = np.random.default_rng(0)

        result = inject_realism(
            df,
            {
                "censoring": {"x": {"type": "right", "threshold": 50.0}},
                "missing_rate": 0.5,
                "dirty_rate": 0.0,
            },
            columns={},
            rng=rng,
        )

        # Censoring NaN'd every cell; df.mask over already-NaN is still NaN.
        assert result["x"].isna().sum() == 50

    def test_no_censoring_key_is_backward_compatible(self):
        """Configs without a censoring key continue to behave as before."""
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0, 4.0, 5.0]})
        rng = np.random.default_rng(0)

        result = inject_realism(
            df,
            {"missing_rate": 0.0, "dirty_rate": 0.0},
            columns={},
            rng=rng,
        )

        pd.testing.assert_frame_equal(result, df)


class TestSetRealismCensoringValidation:
    def test_accepts_valid_right_spec(self):
        cfg = set_realism(
            [],
            missing_rate=0.0,
            dirty_rate=0.0,
            censoring={"x": {"type": "right", "threshold": 5.0}},
        )
        assert cfg["censoring"] == {"x": {"type": "right", "threshold": 5.0}}

    def test_accepts_valid_left_spec(self):
        cfg = set_realism(
            [],
            censoring={"x": {"type": "left", "threshold": 5.0}},
        )
        assert cfg["censoring"]["x"]["type"] == "left"

    def test_accepts_valid_interval_spec(self):
        cfg = set_realism(
            [],
            censoring={"x": {"type": "interval", "low": 0.0, "high": 10.0}},
        )
        assert cfg["censoring"]["x"]["high"] == 10.0

    def test_rejects_non_dict_censoring(self):
        with pytest.raises(ValueError, match="must be a dict"):
            set_realism([], censoring=[("x", "right")])  # type: ignore[arg-type]

    def test_rejects_non_dict_per_column_spec(self):
        with pytest.raises(ValueError, match="must be a dict"):
            set_realism([], censoring={"x": "right"})  # type: ignore[dict-item]

    def test_rejects_missing_type_key(self):
        with pytest.raises(ValueError, match="missing required key 'type'"):
            set_realism([], censoring={"x": {"threshold": 5.0}})

    def test_rejects_unknown_type(self):
        with pytest.raises(ValueError, match="must be one of"):
            set_realism([], censoring={"x": {"type": "bogus"}})

    def test_rejects_right_without_threshold(self):
        with pytest.raises(ValueError, match="requires 'threshold'"):
            set_realism([], censoring={"x": {"type": "right"}})

    def test_rejects_left_without_threshold(self):
        with pytest.raises(ValueError, match="requires 'threshold'"):
            set_realism([], censoring={"x": {"type": "left"}})

    def test_rejects_interval_without_bounds(self):
        with pytest.raises(ValueError, match="requires both 'low' and 'high'"):
            set_realism([], censoring={"x": {"type": "interval", "low": 0.0}})
