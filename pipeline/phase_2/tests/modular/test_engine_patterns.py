"""Tests for Phase 2 engine pattern injection — covers
``inject_ranking_reversal`` and the SDK declaration gate that admits it
(DS-2 / lowest-effort win).

Round-trip oracle: ``check_ranking_reversal`` from
``validation/pattern_checks.py`` is called on the post-injection
DataFrame and must report a negative Spearman rank correlation."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import pytest

from pipeline.phase_2.engine.patterns import (
    inject_convergence,
    inject_dominance_shift,
    inject_patterns,
    inject_ranking_reversal,
    inject_seasonal_anomaly,
)
from pipeline.phase_2.exceptions import PatternInjectionError
from pipeline.phase_2.sdk.relationships import inject_pattern
from pipeline.phase_2.validation.pattern_checks import (
    check_convergence,
    check_dominance_shift,
    check_ranking_reversal,
    check_seasonal_anomaly,
)


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

HOSPITALS = ["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"]


def _build_severe_df() -> pd.DataFrame:
    """5 hospitals × 12 severe rows; m1 ascending across hospitals,
    m2 also ascending (so pre-injection rank correlation is +1.0).
    Adds within-entity jitter so means are well-defined and variance
    > 0 within each group."""
    rng = np.random.default_rng(0)
    rows = []
    for i, hospital in enumerate(HOSPITALS):
        base_m1 = 10.0 * (i + 1)   # 10, 20, 30, 40, 50
        base_m2 = 1.0 * (i + 1)    #  1,  2,  3,  4,  5
        for _ in range(12):
            rows.append({
                "hospital": hospital,
                "severity": "Severe",
                "m1": base_m1 + rng.normal(0, 0.5),
                "m2": base_m2 + rng.normal(0, 0.05),
            })
    # Add some non-severe noise rows so target filters meaningfully.
    for _ in range(20):
        h = HOSPITALS[rng.integers(0, len(HOSPITALS))]
        rows.append({
            "hospital": h,
            "severity": "Mild",
            "m1": rng.normal(25, 5),
            "m2": rng.normal(3, 1),
        })
    return pd.DataFrame(rows)


def _columns_with_hospital_root() -> dict[str, dict]:
    """Column registry where 'hospital' is the first categorical root."""
    return {
        "hospital": {"type": "categorical", "parent": None, "group": "entity"},
        "severity": {"type": "categorical", "parent": None, "group": "patient"},
        "m1": {"type": "measure"},
        "m2": {"type": "measure"},
    }


def _ranking_pattern(entity_col: str | None = "hospital") -> dict:
    params: dict = {"metrics": ["m1", "m2"]}
    if entity_col is not None:
        params["entity_col"] = entity_col
    return {
        "type": "ranking_reversal",
        "target": "severity == 'Severe'",
        "col": "m1",
        "params": params,
    }


# ---------------------------------------------------------------------
# Engine-side injection
# ---------------------------------------------------------------------

class TestInjectRankingReversal:
    def test_round_trip_passes_validator(self):
        df = _build_severe_df()
        pattern = _ranking_pattern()
        columns = _columns_with_hospital_root()

        # Pre-injection: validator should fail (positive rank correlation).
        target_only = df[df["severity"] == "Severe"]
        pre_means = target_only.groupby("hospital")[["m1", "m2"]].mean()
        pre_corr = float(pre_means["m1"].rank().corr(pre_means["m2"].rank()))
        assert pre_corr > 0, "fixture should start with positive correlation"

        result = inject_ranking_reversal(df, pattern, columns)

        check = check_ranking_reversal(result, pattern, meta={})
        assert check.passed is True, f"validator failed: {check.detail}"
        assert "rank_corr=-" in check.detail or "< 0" in check.detail

    def test_entity_col_fallback_uses_first_root(self):
        df = _build_severe_df()
        pattern = _ranking_pattern(entity_col=None)
        columns = _columns_with_hospital_root()

        result = inject_ranking_reversal(df, pattern, columns)

        # Assert via validator with entity_col explicit (matches fallback).
        check_pattern = _ranking_pattern(entity_col="hospital")
        check = check_ranking_reversal(result, check_pattern, meta={})
        assert check.passed is True, f"validator failed: {check.detail}"

    def test_entity_col_fallback_skips_temporal_and_measure_columns(self):
        """Fallback must pick the first *categorical* root, not any
        column that happens to come earlier in the registry."""
        df = _build_severe_df()
        pattern = _ranking_pattern(entity_col=None)
        # 'visit_date' (temporal) and 'm0' (measure) come before
        # 'hospital' in iteration order; fallback should still pick
        # hospital because it's the first categorical root.
        columns = {
            "visit_date": {"type": "temporal"},
            "m0": {"type": "measure"},
            "hospital": {"type": "categorical", "parent": None, "group": "entity"},
            "severity": {"type": "categorical", "parent": None, "group": "patient"},
            "m1": {"type": "measure"},
            "m2": {"type": "measure"},
        }

        result = inject_ranking_reversal(df, pattern, columns)

        check = check_ranking_reversal(
            result, _ranking_pattern(entity_col="hospital"), meta={},
        )
        assert check.passed is True, f"validator failed: {check.detail}"

    def test_empty_target_raises(self):
        df = _build_severe_df()
        pattern = {
            "type": "ranking_reversal",
            "target": "severity == 'Nonexistent'",
            "col": "m1",
            "params": {"metrics": ["m1", "m2"], "entity_col": "hospital"},
        }
        columns = _columns_with_hospital_root()

        with pytest.raises(PatternInjectionError, match="ranking_reversal"):
            inject_ranking_reversal(df, pattern, columns)

    def test_single_entity_in_target_raises(self):
        df = _build_severe_df()
        pattern = {
            "type": "ranking_reversal",
            "target": "severity == 'Severe' & hospital == 'Xiehe'",
            "col": "m1",
            "params": {"metrics": ["m1", "m2"], "entity_col": "hospital"},
        }
        columns = _columns_with_hospital_root()

        with pytest.raises(PatternInjectionError, match=">= 2"):
            inject_ranking_reversal(df, pattern, columns)

    def test_missing_metric_column_warns_and_skips(self, caplog):
        df = _build_severe_df()
        pattern = {
            "type": "ranking_reversal",
            "target": "severity == 'Severe'",
            "col": "m1",
            "params": {"metrics": ["m1", "missing"], "entity_col": "hospital"},
        }
        columns = _columns_with_hospital_root()
        original_m1 = df["m1"].copy()

        with caplog.at_level(logging.WARNING, logger="pipeline.phase_2.engine.patterns"):
            result = inject_ranking_reversal(df, pattern, columns)

        # df returned unchanged (m1 not modified, no m2 to modify)
        pd.testing.assert_series_equal(result["m1"], original_m1)
        assert any(
            "missing" in rec.message and "Skipping injection" in rec.message
            for rec in caplog.records
        )

    def test_malformed_metrics_raises(self):
        df = _build_severe_df()
        columns = _columns_with_hospital_root()
        pattern = {
            "type": "ranking_reversal",
            "target": "severity == 'Severe'",
            "col": "m1",
            "params": {"metrics": ["m1"], "entity_col": "hospital"},
        }

        with pytest.raises(PatternInjectionError, match="length-2"):
            inject_ranking_reversal(df, pattern, columns)

    def test_no_categorical_root_in_columns_raises(self):
        df = _build_severe_df()
        pattern = _ranking_pattern(entity_col=None)
        columns = {
            "m1": {"type": "measure"},
            "m2": {"type": "measure"},
        }

        with pytest.raises(PatternInjectionError, match="entity_col"):
            inject_ranking_reversal(df, pattern, columns)


# ---------------------------------------------------------------------
# SDK declaration gate
# ---------------------------------------------------------------------

class TestRankingReversalDeclaration:
    def _columns_for_declaration(self) -> dict[str, dict]:
        return {
            "hospital": {"type": "categorical", "parent": None, "group": "entity"},
            "severity": {"type": "categorical", "parent": None, "group": "patient"},
            "m1": {"type": "measure"},
            "m2": {"type": "measure"},
        }

    def test_valid_declaration_succeeds(self):
        columns = self._columns_for_declaration()
        patterns: list[dict] = []

        inject_pattern(
            columns, patterns,
            type="ranking_reversal",
            target="severity == 'Severe'",
            col="m1",
            metrics=["m1", "m2"],
            entity_col="hospital",
        )

        assert len(patterns) == 1
        spec = patterns[0]
        assert spec["type"] == "ranking_reversal"
        assert spec["target"] == "severity == 'Severe'"
        assert spec["col"] == "m1"
        assert spec["params"] == {
            "metrics": ["m1", "m2"],
            "entity_col": "hospital",
        }

    def test_valid_declaration_without_optional_entity_col(self):
        columns = self._columns_for_declaration()
        patterns: list[dict] = []

        inject_pattern(
            columns, patterns,
            type="ranking_reversal",
            target="severity == 'Severe'",
            col="m1",
            metrics=["m1", "m2"],
        )

        assert len(patterns) == 1
        assert "entity_col" not in patterns[0]["params"]

    def test_missing_metrics_raises_value_error(self):
        columns = self._columns_for_declaration()
        patterns: list[dict] = []

        with pytest.raises(ValueError, match="metrics"):
            inject_pattern(
                columns, patterns,
                type="ranking_reversal",
                target="severity == 'Severe'",
                col="m1",
            )


# ---------------------------------------------------------------------
# inject_dominance_shift (DS-2)
# ---------------------------------------------------------------------


def _build_dominance_df() -> pd.DataFrame:
    """5 hospitals × 60 daily rows split into 30 pre / 30 post.
    Pre-injection target ('Xiehe') mean ≈ 5, peers ≈ 10 (target rank 5
    on both sides). After injection, target post-split should exceed
    peers, moving its post-split rank to 1."""
    rng = np.random.default_rng(0)
    rows = []
    pre_dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")
    post_dates = pd.date_range("2024-04-01", "2024-06-30", freq="D")
    for h in HOSPITALS[1:]:  # 4 peers, mean ≈ 10 both sides
        for d in pre_dates[:30]:
            rows.append({
                "hospital": h, "visit_date": d,
                "value": 10 + rng.normal(0, 0.5),
            })
        for d in post_dates[:30]:
            rows.append({
                "hospital": h, "visit_date": d,
                "value": 10 + rng.normal(0, 0.5),
            })
    for d in pre_dates[:30]:
        rows.append({
            "hospital": "Xiehe", "visit_date": d,
            "value": 5 + rng.normal(0, 0.5),
        })
    for d in post_dates[:30]:
        rows.append({
            "hospital": "Xiehe", "visit_date": d,
            "value": 5 + rng.normal(0, 0.5),
        })
    return pd.DataFrame(rows)


def _dominance_columns() -> dict[str, dict]:
    return {
        "hospital": {"type": "categorical", "parent": None, "group": "entity"},
        "visit_date": {"type": "temporal"},
        "value": {"type": "measure"},
    }


def _dominance_pattern() -> dict:
    return {
        "type": "dominance_shift",
        "target": "hospital == 'Xiehe'",
        "col": "value",
        "params": {
            "entity_filter": "Xiehe",
            "split_point": "2024-04-01",
            "entity_col": "hospital",
        },
    }


def _dominance_meta() -> dict:
    return {
        "dimension_groups": {
            "entity": {"columns": ["hospital"], "hierarchy": ["hospital"]},
            "time": {"columns": ["visit_date"], "hierarchy": ["visit_date"]},
        }
    }


class TestInjectDominanceShift:
    def test_round_trip_passes_validator(self):
        df = _build_dominance_df()
        pattern = _dominance_pattern()
        columns = _dominance_columns()

        # Pre-injection: validator should fail (target rank stable at 5).
        pre_check = check_dominance_shift(df, pattern, _dominance_meta())
        assert pre_check.passed is False, (
            f"fixture should start with stable rank; got {pre_check.detail}"
        )

        result = inject_dominance_shift(df, pattern, columns)

        post_check = check_dominance_shift(result, pattern, _dominance_meta())
        assert post_check.passed is True, (
            f"validator failed: {post_check.detail}"
        )

    def test_pre_split_values_unchanged(self):
        df = _build_dominance_df()
        pattern = _dominance_pattern()
        columns = _dominance_columns()
        pre_xiehe = df[
            (df["hospital"] == "Xiehe")
            & (df["visit_date"] < "2024-04-01")
        ]["value"].copy()

        result = inject_dominance_shift(df, pattern, columns)

        post_pre_xiehe = result[
            (result["hospital"] == "Xiehe")
            & (result["visit_date"] < "2024-04-01")
        ]["value"]
        pd.testing.assert_series_equal(
            pre_xiehe.reset_index(drop=True),
            post_pre_xiehe.reset_index(drop=True),
        )

    def test_post_split_target_exceeds_peer_max(self):
        df = _build_dominance_df()
        pattern = _dominance_pattern()
        columns = _dominance_columns()

        result = inject_dominance_shift(df, pattern, columns)

        post = result[result["visit_date"] >= "2024-04-01"]
        target_post_mean = post[post["hospital"] == "Xiehe"]["value"].mean()
        peer_post_max = post[post["hospital"] != "Xiehe"]["value"].max()
        assert target_post_mean > peer_post_max

    def test_empty_target_raises(self):
        df = _build_dominance_df()
        pattern = _dominance_pattern()
        pattern["target"] = "hospital == 'NonexistentHospital'"
        columns = _dominance_columns()
        with pytest.raises(PatternInjectionError, match="dominance_shift"):
            inject_dominance_shift(df, pattern, columns)

    def test_empty_post_split_target_raises(self):
        df = _build_dominance_df()
        # Target only exists pre-split — drop post-split target rows.
        df = df[
            ~(
                (df["hospital"] == "Xiehe")
                & (df["visit_date"] >= "2024-04-01")
            )
        ]
        pattern = _dominance_pattern()
        columns = _dominance_columns()
        with pytest.raises(PatternInjectionError, match="No target rows"):
            inject_dominance_shift(df, pattern, columns)

    def test_no_temporal_column_raises(self):
        df = _build_dominance_df()
        pattern = _dominance_pattern()
        columns = {
            "hospital": {
                "type": "categorical", "parent": None, "group": "entity",
            },
            "value": {"type": "measure"},
        }  # no temporal entry
        with pytest.raises(PatternInjectionError, match="temporal"):
            inject_dominance_shift(df, pattern, columns)


# ---------------------------------------------------------------------
# SDK declaration gate for dominance_shift
# ---------------------------------------------------------------------


class TestDominanceShiftDeclaration:
    def _columns_for_declaration(self) -> dict[str, dict]:
        return {
            "hospital": {
                "type": "categorical", "parent": None, "group": "entity",
            },
            "visit_date": {"type": "temporal"},
            "value": {"type": "measure"},
        }

    def test_valid_declaration_succeeds(self):
        columns = self._columns_for_declaration()
        patterns: list[dict] = []

        inject_pattern(
            columns, patterns,
            type="dominance_shift",
            target="hospital == 'Xiehe'",
            col="value",
            entity_filter="Xiehe",
            split_point="2024-04-01",
        )

        assert len(patterns) == 1
        spec = patterns[0]
        assert spec["type"] == "dominance_shift"
        assert spec["target"] == "hospital == 'Xiehe'"
        assert spec["col"] == "value"
        assert spec["params"] == {
            "entity_filter": "Xiehe",
            "split_point": "2024-04-01",
        }

    def test_missing_required_params_raises(self):
        columns = self._columns_for_declaration()
        patterns: list[dict] = []

        with pytest.raises(ValueError, match="entity_filter|split_point"):
            inject_pattern(
                columns, patterns,
                type="dominance_shift",
                target="hospital == 'Xiehe'",
                col="value",
                # missing both required params
            )


# ---------------------------------------------------------------------
# Convergence (DS-2 + IS-3): inject_convergence + round-trip + edge cases
# ---------------------------------------------------------------------


def _build_convergence_df() -> pd.DataFrame:
    """4 hospitals × 60 daily rows. Disparate per-entity baselines (2, 5,
    8, 11) on both sides of the temporal median → high pre-injection
    inter-group variance and stable spread (validator returns
    passed=False before injection). Low within-entity noise (σ=0.3)
    keeps per-entity sample means close to their baseline."""
    rng = np.random.default_rng(0)
    rows = []
    pre_dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")
    post_dates = pd.date_range("2024-04-01", "2024-06-30", freq="D")
    bases = {"H0": 2.0, "H1": 5.0, "H2": 8.0, "H3": 11.0}
    for h, base in bases.items():
        for d in pre_dates[:30]:
            rows.append({
                "hospital": h, "visit_date": d,
                "value": base + rng.normal(0, 0.3),
            })
        for d in post_dates[:30]:
            rows.append({
                "hospital": h, "visit_date": d,
                "value": base + rng.normal(0, 0.3),
            })
    return pd.DataFrame(rows)


def _convergence_columns() -> dict[str, dict]:
    return {
        "hospital": {"type": "categorical", "parent": None, "group": "entity"},
        "visit_date": {"type": "temporal"},
        "value": {"type": "measure"},
    }


def _convergence_pattern(**param_overrides) -> dict:
    p = {
        "type": "convergence",
        "target": "value == value",  # all rows
        "col": "value",
        "params": {},
    }
    p["params"].update(param_overrides)
    return p


def _convergence_meta() -> dict:
    return {
        "dimension_groups": {
            "entity": {"columns": ["hospital"], "hierarchy": ["hospital"]},
            "time": {"columns": ["visit_date"], "hierarchy": ["visit_date"]},
        }
    }


class TestInjectConvergence:
    def test_round_trip_passes_validator(self):
        df = _build_convergence_df()
        pattern = _convergence_pattern()
        columns = _convergence_columns()

        # Pre-injection: stable spread → validator should fail.
        pre = check_convergence(df, pattern, _convergence_meta())
        assert pre.passed is False, (
            f"fixture should start with stable spread; got {pre.detail}"
        )

        result = inject_convergence(df, pattern, columns)

        post = check_convergence(result, pattern, _convergence_meta())
        assert post.passed is True, (
            f"post-injection should converge; got {post.detail}"
        )
        assert "reduction=" in post.detail

    def test_late_means_pulled_toward_global_mean(self):
        df = _build_convergence_df()
        pattern = _convergence_pattern(pull_strength=1.0)
        columns = _convergence_columns()

        global_mean_pre = df["value"].mean()
        result = inject_convergence(df, pattern, columns)

        # Post-injection late half: per-entity means should be much closer
        # to the global mean than the pre-injection bases (2, 5, 8, 11).
        post_late = result[result["visit_date"] >= "2024-04-01"]
        late_means = post_late.groupby("hospital")["value"].mean()
        for entity_mean in late_means:
            # Pre-injection per-entity means range [2, 11], so |x - 6.5|
            # was up to 4.5; after pulling at avg factor ~0.75, the gap
            # should be < 2.0.
            assert abs(entity_mean - global_mean_pre) < 2.0

    def test_empty_target_raises(self):
        df = _build_convergence_df()
        pattern = _convergence_pattern()
        pattern["target"] = "value > 99999"
        columns = _convergence_columns()
        with pytest.raises(PatternInjectionError, match="zero rows"):
            inject_convergence(df, pattern, columns)

    def test_missing_temporal_column_raises(self):
        df = pd.DataFrame({
            "hospital": ["A", "B", "A", "B"],
            "value": [1.0, 2.0, 3.0, 4.0],
        })
        columns = {
            "hospital": {
                "type": "categorical", "parent": None, "group": "entity",
            },
            "value": {"type": "measure"},
        }  # no temporal entry
        pattern = _convergence_pattern()
        with pytest.raises(PatternInjectionError, match="temporal column"):
            inject_convergence(df, pattern, columns)

    def test_zero_temporal_span_raises(self):
        df = pd.DataFrame({
            "hospital": ["A", "B", "A", "B"],
            "visit_date": pd.to_datetime(["2024-01-01"] * 4),
            "value": [1.0, 2.0, 3.0, 4.0],
        })
        pattern = _convergence_pattern()
        columns = _convergence_columns()
        with pytest.raises(PatternInjectionError, match="zero span"):
            inject_convergence(df, pattern, columns)

    def test_negative_pull_strength_raises(self):
        df = _build_convergence_df()
        pattern = _convergence_pattern(pull_strength=-0.5)
        columns = _convergence_columns()
        with pytest.raises(PatternInjectionError, match="pull_strength"):
            inject_convergence(df, pattern, columns)

    def test_zero_pull_strength_raises(self):
        df = _build_convergence_df()
        pattern = _convergence_pattern(pull_strength=0.0)
        columns = _convergence_columns()
        with pytest.raises(PatternInjectionError, match="pull_strength"):
            inject_convergence(df, pattern, columns)


# ---------------------------------------------------------------------
# SDK declaration gate for convergence
# ---------------------------------------------------------------------


class TestConvergenceDeclaration:
    def _columns_for_declaration(self) -> dict[str, dict]:
        return {
            "hospital": {
                "type": "categorical", "parent": None, "group": "entity",
            },
            "visit_date": {"type": "temporal"},
            "value": {"type": "measure"},
        }

    def test_valid_declaration_with_no_params_succeeds(self):
        # convergence has no required params — declaration with just
        # type/target/col should succeed.
        columns = self._columns_for_declaration()
        patterns: list[dict] = []

        inject_pattern(
            columns, patterns,
            type="convergence",
            target="value == value",
            col="value",
        )

        assert len(patterns) == 1
        spec = patterns[0]
        assert spec["type"] == "convergence"
        assert spec["target"] == "value == value"
        assert spec["col"] == "value"
        assert spec["params"] == {}

    def test_valid_declaration_with_optional_params_succeeds(self):
        columns = self._columns_for_declaration()
        patterns: list[dict] = []

        inject_pattern(
            columns, patterns,
            type="convergence",
            target="value == value",
            col="value",
            reduction=0.4,
            pull_strength=1.5,
            split_point="2024-04-01",
        )

        assert len(patterns) == 1
        spec = patterns[0]
        assert spec["params"] == {
            "reduction": 0.4,
            "pull_strength": 1.5,
            "split_point": "2024-04-01",
        }

    def test_sdk_constants_register_convergence(self):
        from pipeline.phase_2.sdk.relationships import (
            VALID_PATTERN_TYPES, PATTERN_REQUIRED_PARAMS,
        )
        assert "convergence" in VALID_PATTERN_TYPES
        assert PATTERN_REQUIRED_PARAMS["convergence"] == frozenset()


# ---------------------------------------------------------------------
# Seasonal anomaly (IS-4 + DS-2): inject_seasonal_anomaly + round-trip
# ---------------------------------------------------------------------


def _build_seasonal_df() -> pd.DataFrame:
    """Daily 2024-H1 rows with stable per-row noise around mean=5.
    Pre-injection, the May-15 → Jun-30 window mean ≈ baseline → validator
    fails; post-injection, in-window values are scaled by (1 + magnitude)
    so the window mean diverges → validator passes."""
    rng = np.random.default_rng(0)
    dates = pd.date_range("2024-01-01", "2024-06-30", freq="D")
    rows = [
        {"visit_date": d, "value": 5.0 + rng.normal(0, 0.5)}
        for d in dates
    ]
    return pd.DataFrame(rows)


def _seasonal_columns() -> dict[str, dict]:
    return {
        "visit_date": {"type": "temporal"},
        "value": {"type": "measure"},
    }


def _seasonal_pattern(**param_overrides) -> dict:
    p = {
        "type": "seasonal_anomaly",
        "target": "value == value",
        "col": "value",
        "params": {
            "anomaly_window": ["2024-05-15", "2024-06-30"],
            "magnitude": 0.8,
        },
    }
    p["params"].update(param_overrides)
    return p


def _seasonal_meta() -> dict:
    return {
        "dimension_groups": {
            "time": {"columns": ["visit_date"], "hierarchy": ["visit_date"]},
        }
    }


class TestInjectSeasonalAnomaly:
    def test_round_trip_passes_validator(self):
        df = _build_seasonal_df()
        pattern = _seasonal_pattern()
        columns = _seasonal_columns()

        # Pre-injection: stable mean → validator should fail.
        pre = check_seasonal_anomaly(df, pattern, _seasonal_meta())
        assert pre.passed is False, (
            f"fixture should start without anomaly; got {pre.detail}"
        )

        result = inject_seasonal_anomaly(df, pattern, columns)

        post = check_seasonal_anomaly(result, pattern, _seasonal_meta())
        assert post.passed is True, (
            f"post-injection should detect anomaly; got {post.detail}"
        )

    def test_out_of_window_values_unchanged(self):
        df = _build_seasonal_df()
        pattern = _seasonal_pattern()
        columns = _seasonal_columns()
        pre_out = df[df["visit_date"] < "2024-05-15"]["value"].copy()

        result = inject_seasonal_anomaly(df, pattern, columns)

        post_out = result[result["visit_date"] < "2024-05-15"]["value"]
        pd.testing.assert_series_equal(
            pre_out.reset_index(drop=True),
            post_out.reset_index(drop=True),
        )

    def test_empty_target_raises(self):
        df = _build_seasonal_df()
        pattern = _seasonal_pattern()
        pattern["target"] = "value > 99999"
        columns = _seasonal_columns()
        with pytest.raises(PatternInjectionError, match="zero rows"):
            inject_seasonal_anomaly(df, pattern, columns)

    def test_window_matches_no_rows_raises(self):
        df = _build_seasonal_df()
        pattern = _seasonal_pattern(
            anomaly_window=["2030-01-01", "2030-01-31"],
        )
        columns = _seasonal_columns()
        with pytest.raises(PatternInjectionError, match="anomaly_window"):
            inject_seasonal_anomaly(df, pattern, columns)

    def test_missing_temporal_column_raises(self):
        df = pd.DataFrame({"value": [1.0, 2.0, 3.0, 4.0]})
        columns = {"value": {"type": "measure"}}  # no temporal entry
        pattern = _seasonal_pattern()
        with pytest.raises(PatternInjectionError, match="temporal column"):
            inject_seasonal_anomaly(df, pattern, columns)


# ---------------------------------------------------------------------
# SDK declaration gate for seasonal_anomaly
# ---------------------------------------------------------------------


class TestSeasonalAnomalyDeclaration:
    def _columns_for_declaration(self) -> dict[str, dict]:
        return {
            "visit_date": {"type": "temporal"},
            "value": {"type": "measure"},
        }

    def test_valid_declaration_succeeds(self):
        columns = self._columns_for_declaration()
        patterns: list[dict] = []

        inject_pattern(
            columns, patterns,
            type="seasonal_anomaly",
            target="value == value",
            col="value",
            anomaly_window=["2024-05-15", "2024-06-30"],
            magnitude=0.5,
        )

        assert len(patterns) == 1
        spec = patterns[0]
        assert spec["type"] == "seasonal_anomaly"
        assert spec["params"] == {
            "anomaly_window": ["2024-05-15", "2024-06-30"],
            "magnitude": 0.5,
        }

    def test_missing_anomaly_window_raises(self):
        columns = self._columns_for_declaration()
        patterns: list[dict] = []
        with pytest.raises(ValueError, match="anomaly_window"):
            inject_pattern(
                columns, patterns,
                type="seasonal_anomaly",
                target="value == value",
                col="value",
                magnitude=0.5,
            )

    def test_missing_magnitude_raises(self):
        columns = self._columns_for_declaration()
        patterns: list[dict] = []
        with pytest.raises(ValueError, match="magnitude"):
            inject_pattern(
                columns, patterns,
                type="seasonal_anomaly",
                target="value == value",
                col="value",
                anomaly_window=["2024-05-15", "2024-06-30"],
            )

    def test_sdk_constants_register_seasonal_anomaly(self):
        from pipeline.phase_2.sdk.relationships import (
            VALID_PATTERN_TYPES, PATTERN_REQUIRED_PARAMS,
        )
        assert "seasonal_anomaly" in VALID_PATTERN_TYPES
        assert PATTERN_REQUIRED_PARAMS["seasonal_anomaly"] == frozenset(
            {"anomaly_window", "magnitude"}
        )


# ---------------------------------------------------------------------
# Integration: all 6 pattern types dispatch through inject_patterns
# ---------------------------------------------------------------------


def _build_all_patterns_df() -> pd.DataFrame:
    """3 hospitals × 2 severities × ~60 daily rows with two measures
    (m1, m2). Designed so all 6 pattern types can fire without raising."""
    rng = np.random.default_rng(0)
    rows = []
    dates = pd.date_range("2024-01-01", "2024-06-30", freq="D")
    for i, hospital in enumerate(["Xiehe", "Huashan", "Ruijin"]):
        base_m1 = 10.0 * (i + 1)  # 10, 20, 30
        base_m2 = 1.0 * (i + 1)   # 1, 2, 3
        for severity in ["Mild", "Severe"]:
            sev_offset = 0.0 if severity == "Mild" else 5.0
            for d in dates[::3]:  # every 3rd day to keep test fast
                rows.append({
                    "hospital": hospital,
                    "severity": severity,
                    "visit_date": d,
                    "m1": base_m1 + sev_offset + rng.normal(0, 0.5),
                    "m2": base_m2 + rng.normal(0, 0.05),
                })
    return pd.DataFrame(rows)


def _all_patterns_columns() -> dict[str, dict]:
    return {
        "hospital": {"type": "categorical", "parent": None, "group": "entity"},
        "severity": {"type": "categorical", "parent": None, "group": "patient"},
        "visit_date": {"type": "temporal"},
        "m1": {"type": "measure"},
        "m2": {"type": "measure"},
    }


class TestAllSixPatternsIntegration:
    def test_all_six_patterns_dispatch_without_error(self):
        df = _build_all_patterns_df()
        columns = _all_patterns_columns()
        rng = np.random.default_rng(0)

        patterns = [
            {
                "type": "outlier_entity",
                "target": "hospital == 'Xiehe' & severity == 'Severe'",
                "col": "m1",
                "params": {"z_score": 2.0},
            },
            {
                "type": "trend_break",
                "target": "hospital == 'Huashan'",
                "col": "m1",
                "params": {"break_point": "2024-03-15", "magnitude": 0.4},
            },
            {
                "type": "ranking_reversal",
                "target": "severity == 'Severe'",
                "col": "m1",
                "params": {
                    "metrics": ["m1", "m2"],
                    "entity_col": "hospital",
                },
            },
            {
                "type": "dominance_shift",
                "target": "hospital == 'Ruijin'",
                "col": "m1",
                "params": {
                    "entity_filter": "Ruijin",
                    "split_point": "2024-04-01",
                    "entity_col": "hospital",
                },
            },
            {
                "type": "convergence",
                "target": "severity == 'Severe'",
                "col": "m1",
                "params": {"reduction": 0.3},
            },
            {
                "type": "seasonal_anomaly",
                "target": "severity == 'Severe'",
                "col": "m1",
                "params": {
                    "anomaly_window": ["2024-05-15", "2024-06-30"],
                    "magnitude": 0.5,
                },
            },
        ]

        # Should run end-to-end without raising NotImplementedError
        # or any other exception. Mutates df in place; no value-level
        # assertions — composition order makes per-pattern outcomes
        # path-dependent, and this test just verifies dispatch coverage.
        result = inject_patterns(df, patterns, columns, rng)
        assert result is not None
        assert len(result) == len(df)
