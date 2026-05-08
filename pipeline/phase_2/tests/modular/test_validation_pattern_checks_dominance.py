"""Tests for check_dominance_shift (IS-2)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pipeline.phase_2.validation.pattern_checks import check_dominance_shift


HOSPITALS = ["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"]


def _meta_with_entity_and_time() -> dict:
    return {
        "dimension_groups": {
            "entity": {"columns": ["hospital"], "hierarchy": ["hospital"]},
            "time": {"columns": ["visit_date"], "hierarchy": ["visit_date"]},
        }
    }


def _build_df(target_pre_mean: float, target_post_mean: float) -> pd.DataFrame:
    """Per-hospital sized rows. target_pre_mean and target_post_mean control
    only the *target* entity's pre- and post-split column values; the other
    4 entities have fixed per-side means so the target's rank movement is
    the variable under test."""
    rng = np.random.default_rng(0)
    rows = []
    pre_dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")
    post_dates = pd.date_range("2024-04-01", "2024-06-30", freq="D")
    # Non-target hospitals: stable mean=10 on both sides.
    for h in HOSPITALS[1:]:
        for d in pre_dates[:30]:
            rows.append(
                {"hospital": h, "visit_date": d, "value": 10 + rng.normal(0, 0.1)}
            )
        for d in post_dates[:30]:
            rows.append(
                {"hospital": h, "visit_date": d, "value": 10 + rng.normal(0, 0.1)}
            )
    # Target: Xiehe.
    for d in pre_dates[:30]:
        rows.append(
            {
                "hospital": "Xiehe",
                "visit_date": d,
                "value": target_pre_mean + rng.normal(0, 0.1),
            }
        )
    for d in post_dates[:30]:
        rows.append(
            {
                "hospital": "Xiehe",
                "visit_date": d,
                "value": target_post_mean + rng.normal(0, 0.1),
            }
        )
    return pd.DataFrame(rows)


def _pattern(**overrides) -> dict:
    p = {
        "type": "dominance_shift",
        "target": "hospital == 'Xiehe'",
        "col": "value",
        "params": {
            "entity_filter": "Xiehe",
            "split_point": "2024-04-01",
            "entity_col": "hospital",
        },
    }
    p["params"].update(overrides)
    return p


class TestCheckDominanceShift:
    def test_rank_shift_passes(self):
        # Pre: target mean=5 -> lowest of 5 (rank 5 descending).
        # Post: target=20 -> highest (rank 1). delta=4, threshold=1 → pass.
        df = _build_df(target_pre_mean=5.0, target_post_mean=20.0)
        result = check_dominance_shift(
            df, _pattern(), _meta_with_entity_and_time()
        )
        assert result.passed is True
        assert "delta=4" in result.detail

    def test_stable_rank_fails(self):
        # Target at mean=15 (distinctly above peers' 10) on BOTH sides →
        # target stays at rank 1 across split → delta=0 → fails threshold=1.
        # (Don't pick target_mean ≈ peer_mean: small per-side noise makes
        # ranks fluctuate among near-equal entities and produces flaky
        # deltas, not a genuine stable-rank test.)
        df = _build_df(target_pre_mean=15.0, target_post_mean=15.0)
        result = check_dominance_shift(
            df, _pattern(), _meta_with_entity_and_time()
        )
        assert result.passed is False
        assert "delta=0" in result.detail

    def test_missing_entity_filter_fails(self):
        df = _build_df(5.0, 20.0)
        pattern = _pattern()
        pattern["params"].pop("entity_filter")
        result = check_dominance_shift(
            df, pattern, _meta_with_entity_and_time()
        )
        assert result.passed is False
        assert "entity_filter" in result.detail

    def test_missing_split_point_fails(self):
        df = _build_df(5.0, 20.0)
        pattern = _pattern()
        pattern["params"].pop("split_point")
        result = check_dominance_shift(
            df, pattern, _meta_with_entity_and_time()
        )
        assert result.passed is False
        assert "split_point" in result.detail

    def test_target_absent_pre_split_fails(self):
        df = _build_df(5.0, 20.0)
        # Drop all pre-split target rows.
        df = df[
            ~((df["hospital"] == "Xiehe") & (df["visit_date"] < "2024-04-01"))
        ]
        result = check_dominance_shift(
            df, _pattern(), _meta_with_entity_and_time()
        )
        assert result.passed is False
        assert "Xiehe" in result.detail

    def test_missing_temporal_column_fails(self):
        df = _build_df(5.0, 20.0)
        meta = {
            "dimension_groups": {
                "entity": {"columns": ["hospital"], "hierarchy": ["hospital"]},
            }  # no "time" group
        }
        result = check_dominance_shift(df, _pattern(), meta)
        assert result.passed is False
        assert "temporal_col" in result.detail

    def test_entity_col_fallback_uses_first_dim_root(self):
        # Drop entity_col from params; meta's first dim group is "entity"
        # whose hierarchy root is "hospital" → should resolve correctly.
        df = _build_df(5.0, 20.0)
        pattern = _pattern()
        pattern["params"].pop("entity_col")
        result = check_dominance_shift(
            df, pattern, _meta_with_entity_and_time()
        )
        assert result.passed is True

    def test_custom_rank_change_threshold_blocks_pass(self):
        # Pre: target mean=8 -> rank 5 (last). Post: target=11 -> rank 1
        # (above peers at 10). delta=4. With threshold=5 → fail.
        df = _build_df(target_pre_mean=8.0, target_post_mean=11.0)
        pattern = _pattern(rank_change=5)
        result = check_dominance_shift(
            df, pattern, _meta_with_entity_and_time()
        )
        assert result.passed is False

    # ---------------------------------------------------------------------
    # T2.1 of TEST_AUDIT_2026-05-07.md.
    #
    # `check_dominance_shift` uses `abs(rank_after - rank_before)`
    # (pattern_checks.py:304), so direction does NOT change the verdict —
    # both upward (low→high) and downward (high→low) rank movements pass
    # given sufficient magnitude. The pre-existing tests only cover the
    # upward case (`target_pre_mean=5 → target_post_mean=20`, rank 5→1).
    # The two tests below pin the symmetric behavior so any future change
    # that adds direction-awareness (or breaks it) is caught.
    # ---------------------------------------------------------------------

    def test_downward_rank_movement_also_passes(self):
        """Target moves from rank 1 (highest) to rank 5 (lowest) — should
        pass since |delta|=4 ≥ threshold=1, regardless of direction."""
        df = _build_df(target_pre_mean=20.0, target_post_mean=5.0)
        result = check_dominance_shift(
            df, _pattern(), _meta_with_entity_and_time()
        )
        assert result.passed is True
        # Direction-agnostic: detail still reports delta=4.
        assert "delta=4" in result.detail
        # Specifically: rank_before=1 (highest), rank_after=5 (lowest).
        assert "rank_before=1" in result.detail
        assert "rank_after=5" in result.detail

    def test_rank_change_threshold_boundary(self):
        """Target moves from rank 5 to rank 4 (delta=1). With threshold=1 →
        pass; with threshold=2 → fail. Locks in the `>=` boundary."""
        # Pre: target=5 (rank 5). Post: target=10.05 vs peers at 10 (very
        # close) — target ends just barely on top, but with shared peer
        # mean=10, ranking ties make this fragile. Use a clean rank-1-step
        # construction instead: pre target=5 (rank 5), post target=11
        # (rank 1 — highest). That's delta=4, which is too large.
        # Instead, use post target=9.5 against peers at [10, 10, 10, 10] →
        # target still rank 5. So we need to construct intermediate ranks.
        # Simplest reliable construction: per-peer different means.
        rng = np.random.default_rng(0)
        pre_dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")[:30]
        post_dates = pd.date_range("2024-04-01", "2024-06-30", freq="D")[:30]
        rows = []
        # Distinct peer means so ranks 1-4 are stable.
        peer_means = {"Huashan": 14.0, "Ruijin": 13.0,
                      "Tongren": 12.0, "Zhongshan": 11.0}
        for h, m in peer_means.items():
            for d in list(pre_dates) + list(post_dates):
                rows.append({"hospital": h, "visit_date": d,
                             "value": m + rng.normal(0, 0.01)})
        # Target Xiehe: pre below all peers (rank 5), post just above
        # Zhongshan and Tongren but below Ruijin/Huashan → rank 3 (delta=2).
        for d in pre_dates:
            rows.append({"hospital": "Xiehe", "visit_date": d,
                         "value": 5.0 + rng.normal(0, 0.01)})
        for d in post_dates:
            rows.append({"hospital": "Xiehe", "visit_date": d,
                         "value": 12.5 + rng.normal(0, 0.01)})
        df = pd.DataFrame(rows)

        # threshold=2 (matches actual delta) → pass
        result_pass = check_dominance_shift(
            df, _pattern(rank_change=2), _meta_with_entity_and_time()
        )
        assert result_pass.passed is True, (
            f"delta=2 with threshold=2 must pass (>=); got {result_pass.detail}"
        )

        # threshold=3 (one above actual delta) → fail
        result_fail = check_dominance_shift(
            df, _pattern(rank_change=3), _meta_with_entity_and_time()
        )
        assert result_fail.passed is False, (
            f"delta=2 with threshold=3 must fail; got {result_fail.detail}"
        )
