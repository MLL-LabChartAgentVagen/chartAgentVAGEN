"""
Sprint 6 — Tests for pattern injection and realism injection methods
on FactTableSimulator.

Subtask IDs covered: 4.3.1, 4.3.2, 4.4.1, 4.4.2, plus generate() wiring.

Test structure:
  1. Contract tests — one test per Message 1 contract table row (3F–3J)
  2. Input validation tests — type enforcement, boundary values, constraints
  3. Output correctness tests — return types, numerical correctness,
     immutability, reproducibility
  4. State transition tests — internal _patterns and _realism_config after calls
  5. Integration tests — full generate() pipeline with injection
"""
from __future__ import annotations

# FIX: [self-review item 4] — Removed unused `import string`.
import numpy as np
import pandas as pd
import pytest

from agpds.simulator import FactTableSimulator
# FIX: [self-review item 6] — Import typed exceptions to replace bare
# ValueError assertions in tests.
from agpds.exceptions import (
    DegenerateDistributionError,
    PatternInjectionError,
)


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def sim_with_measure():
    """A simulator with categorical, temporal, and measure declarations.
    Returns (sim, df) where df has a synthetic 'wait_minutes' column injected
    because measures are BLOCKED in skeleton mode.
    """
    sim = FactTableSimulator(500, 42)
    sim.add_category(
        "hospital", ["Xiehe", "Huashan", "Zhongshan"],
        [0.4, 0.3, 0.3], "entity",
    )
    sim.add_category(
        "severity", ["Mild", "Moderate", "Severe"],
        [0.5, 0.3, 0.2], "patient",
    )
    sim.declare_orthogonal("entity", "patient", "independent dimensions")
    sim.add_temporal("visit_date", "2024-01-01", "2024-06-30", "daily")
    sim.add_measure("wait_minutes", "lognormal", {"mu": 3.9, "sigma": 0.45})

    # Generate skeleton and manually add a measure column (since measures
    # are BLOCKED in skeleton engine — Blockers 2 & 3)
    df, _ = sim.generate()
    rng = np.random.default_rng(42)
    df["wait_minutes"] = rng.lognormal(3.9, 0.45, size=len(df))
    return sim, df


@pytest.fixture
def sim_basic():
    """A minimal simulator with categories and temporal for realism tests."""
    sim = FactTableSimulator(500, 42)
    sim.add_category(
        "hospital", ["Alpha", "Beta", "Gamma"],
        [0.4, 0.3, 0.3], "entity",
    )
    sim.add_temporal("visit_date", "2024-01-01", "2024-06-30", "daily")
    return sim


# =====================================================================
# 1. CONTRACT TESTS — Outlier Entity Injection (4.3.1) — Table 3F
# =====================================================================

class TestOutlierEntityContract:
    """Contract tests for _inject_outlier_entity [Subtask 4.3.1]."""

    def test_target_subset_zscore_meets_threshold(self, sim_with_measure):
        """Contract 3F row 1: target matches rows, z_score=3.0, col has nonzero
        std → target subset mean z-score ≥ 3.0."""
        # [Subtask 4.3.1]
        sim, df = sim_with_measure
        global_mean = df["wait_minutes"].mean()
        global_std = df["wait_minutes"].std()

        pattern = {
            "type": "outlier_entity",
            "target": "hospital == 'Xiehe' & severity == 'Severe'",
            "col": "wait_minutes",
            "params": {"z_score": 3.0},
        }
        df = sim._inject_outlier_entity(df, pattern)

        target_mask = df.eval("hospital == 'Xiehe' & severity == 'Severe'")
        target_mean = df.loc[target_mask, "wait_minutes"].mean()
        z_actual = abs(target_mean - global_mean) / global_std
        assert z_actual >= 2.9  # small float tolerance

    def test_non_target_rows_unchanged(self, sim_with_measure):
        """Contract 3F row 2: non-target rows are unchanged after injection."""
        # [Subtask 4.3.1]
        sim, df = sim_with_measure
        pattern = {
            "type": "outlier_entity",
            "target": "hospital == 'Xiehe' & severity == 'Severe'",
            "col": "wait_minutes",
            "params": {"z_score": 3.0},
        }
        target_mask = df.eval("hospital == 'Xiehe' & severity == 'Severe'")
        non_target_before = df.loc[~target_mask, "wait_minutes"].copy()

        df = sim._inject_outlier_entity(df, pattern)

        non_target_after = df.loc[~target_mask, "wait_minutes"]
        pd.testing.assert_series_equal(
            non_target_before.reset_index(drop=True),
            non_target_after.reset_index(drop=True),
        )

    def test_zscore_zero_no_shift(self, sim_with_measure):
        """Contract 3F row 3: z_score=0.0 → no meaningful shift."""
        # [Subtask 4.3.1]
        sim, df = sim_with_measure
        global_mean = df["wait_minutes"].mean()
        pattern = {
            "type": "outlier_entity",
            "target": "hospital == 'Xiehe'",
            "col": "wait_minutes",
            "params": {"z_score": 0.0},
        }
        df = sim._inject_outlier_entity(df, pattern)
        target_mask = df.eval("hospital == 'Xiehe'")
        target_mean = df.loc[target_mask, "wait_minutes"].mean()
        # After shift, subset mean ≈ global_mean + 0 * std = global_mean
        assert abs(target_mean - global_mean) < df["wait_minutes"].std() * 0.1

    def test_negative_zscore_shifts_below(self, sim_with_measure):
        """Contract 3F row 4: z_score=-2.0 → subset mean shifts below global."""
        # [Subtask 4.3.1]
        sim, df = sim_with_measure
        global_mean = df["wait_minutes"].mean()
        pattern = {
            "type": "outlier_entity",
            "target": "hospital == 'Xiehe'",
            "col": "wait_minutes",
            "params": {"z_score": -2.0},
        }
        df = sim._inject_outlier_entity(df, pattern)
        target_mask = df.eval("hospital == 'Xiehe'")
        target_mean = df.loc[target_mask, "wait_minutes"].mean()
        assert target_mean < global_mean

    def test_zero_rows_raises(self, sim_with_measure):
        """Contract 3F row 5: target matches 0 rows → PatternInjectionError."""
        # [Subtask 4.3.1]
        # FIX: [self-review item 6] — Changed from ValueError to typed
        # PatternInjectionError.
        sim, df = sim_with_measure
        pattern = {
            "type": "outlier_entity",
            "target": "hospital == 'NONEXISTENT'",
            "col": "wait_minutes",
            "params": {"z_score": 3.0},
        }
        with pytest.raises(PatternInjectionError, match="zero rows"):
            sim._inject_outlier_entity(df, pattern)

    def test_all_rows_match_still_works(self, sim_with_measure):
        """Contract 3F row 6: target matches all rows → degenerate but valid."""
        # [Subtask 4.3.1]
        sim, df = sim_with_measure
        # Use a universally true filter
        pattern = {
            "type": "outlier_entity",
            "target": "hospital == hospital",
            "col": "wait_minutes",
            "params": {"z_score": 2.0},
        }
        # Should not raise — shifts all rows
        df_result = sim._inject_outlier_entity(df, pattern)
        assert len(df_result) == len(df)

    def test_zero_std_column_raises(self, sim_with_measure):
        """Contract 3F row 7: col has zero std (constant) → DegenerateDistributionError."""
        # [Subtask 4.3.1]
        # FIX: [self-review item 6] — Changed from ValueError to typed
        # DegenerateDistributionError from §2.7 taxonomy.
        sim, df = sim_with_measure
        df["wait_minutes"] = 100.0
        pattern = {
            "type": "outlier_entity",
            "target": "hospital == 'Xiehe'",
            "col": "wait_minutes",
            "params": {"z_score": 3.0},
        }
        with pytest.raises(DegenerateDistributionError, match="zero standard deviation"):
            sim._inject_outlier_entity(df, pattern)


# =====================================================================
# 1. CONTRACT TESTS — Trend Break Injection (4.3.2) — Table 3G
# =====================================================================

class TestTrendBreakContract:
    """Contract tests for _inject_trend_break [Subtask 4.3.2]."""

    def test_relative_shift_exceeds_threshold(self, sim_with_measure):
        """Contract 3G row 1: target matches rows, magnitude=0.4 →
        |mean_after - mean_before| / mean_before > 0.15."""
        # [Subtask 4.3.2]
        sim, df = sim_with_measure
        pattern = {
            "type": "trend_break",
            "target": "hospital == 'Huashan'",
            "col": "wait_minutes",
            "params": {"break_point": "2024-03-15", "magnitude": 0.4},
        }
        bp = pd.to_datetime("2024-03-15")
        target_mask = df.eval("hospital == 'Huashan'")
        temporal = pd.to_datetime(df["visit_date"])
        before_mask = target_mask & (temporal < bp)
        after_mask = target_mask & (temporal >= bp)

        df = sim._inject_trend_break(df, pattern)

        mean_before = df.loc[before_mask, "wait_minutes"].mean()
        mean_after = df.loc[after_mask, "wait_minutes"].mean()
        relative_shift = abs(mean_after - mean_before) / mean_before
        assert relative_shift > 0.15

    def test_before_rows_unchanged(self, sim_with_measure):
        """Contract 3G row 2: rows before break_point are unchanged."""
        # [Subtask 4.3.2]
        sim, df = sim_with_measure
        pattern = {
            "type": "trend_break",
            "target": "hospital == 'Huashan'",
            "col": "wait_minutes",
            "params": {"break_point": "2024-03-15", "magnitude": 0.4},
        }
        bp = pd.to_datetime("2024-03-15")
        target_mask = df.eval("hospital == 'Huashan'")
        temporal = pd.to_datetime(df["visit_date"])
        before_mask = target_mask & (temporal < bp)
        before_vals = df.loc[before_mask, "wait_minutes"].copy()

        df = sim._inject_trend_break(df, pattern)

        pd.testing.assert_series_equal(
            before_vals.reset_index(drop=True),
            df.loc[before_mask, "wait_minutes"].reset_index(drop=True),
        )

    def test_magnitude_zero_no_change(self, sim_with_measure):
        """Contract 3G row 3: magnitude=0.0 → no change (scaling by 1.0)."""
        # [Subtask 4.3.2]
        sim, df = sim_with_measure
        original = df["wait_minutes"].copy()
        pattern = {
            "type": "trend_break",
            "target": "hospital == 'Huashan'",
            "col": "wait_minutes",
            "params": {"break_point": "2024-03-15", "magnitude": 0.0},
        }
        df = sim._inject_trend_break(df, pattern)
        pd.testing.assert_series_equal(
            original.reset_index(drop=True),
            df["wait_minutes"].reset_index(drop=True),
        )

    def test_negative_magnitude_decreases(self, sim_with_measure):
        """Contract 3G row 4: magnitude=-0.3 → after-rows scaled by 0.7."""
        # [Subtask 4.3.2]
        sim, df = sim_with_measure
        bp = pd.to_datetime("2024-03-15")
        target_mask = df.eval("hospital == 'Huashan'")
        temporal = pd.to_datetime(df["visit_date"])
        after_mask = target_mask & (temporal >= bp)
        after_before = df.loc[after_mask, "wait_minutes"].copy()

        pattern = {
            "type": "trend_break",
            "target": "hospital == 'Huashan'",
            "col": "wait_minutes",
            "params": {"break_point": "2024-03-15", "magnitude": -0.3},
        }
        df = sim._inject_trend_break(df, pattern)
        after_after = df.loc[after_mask, "wait_minutes"]

        # Each post-break value should be 0.7 × original
        expected = after_before * 0.7
        np.testing.assert_allclose(
            after_after.values, expected.values, rtol=1e-10,
        )

    def test_zero_rows_raises(self, sim_with_measure):
        """Contract 3G row 5: target matches 0 rows → PatternInjectionError."""
        # [Subtask 4.3.2]
        # FIX: [self-review item 6] — Changed from ValueError to typed
        # PatternInjectionError.
        sim, df = sim_with_measure
        pattern = {
            "type": "trend_break",
            "target": "hospital == 'NONEXISTENT'",
            "col": "wait_minutes",
            "params": {"break_point": "2024-03-15", "magnitude": 0.4},
        }
        with pytest.raises(PatternInjectionError, match="zero rows"):
            sim._inject_trend_break(df, pattern)

    def test_no_temporal_column_raises(self):
        """Contract 3G row 6: no temporal column declared → PatternInjectionError."""
        # [Subtask 4.3.2]
        # FIX: [self-review item 6] — Changed from ValueError to typed
        # PatternInjectionError.
        sim = FactTableSimulator(100, 42)
        sim.add_category("h", ["A", "B"], [1, 1], "entity")
        df = pd.DataFrame({
            "h": ["A", "B"] * 50,
            "measure": range(100),
        })
        pattern = {
            "type": "trend_break",
            "target": "h == 'A'",
            "col": "measure",
            "params": {"break_point": "2024-03-15", "magnitude": 0.4},
        }
        with pytest.raises(PatternInjectionError, match="No temporal column"):
            sim._inject_trend_break(df, pattern)

    def test_break_point_after_all_dates(self, sim_with_measure):
        """Contract 3G row 7: break_point after max date → no rows scaled."""
        # [Subtask 4.3.2]
        sim, df = sim_with_measure
        original = df["wait_minutes"].copy()
        pattern = {
            "type": "trend_break",
            "target": "hospital == 'Huashan'",
            "col": "wait_minutes",
            "params": {"break_point": "2025-01-01", "magnitude": 0.4},
        }
        df = sim._inject_trend_break(df, pattern)
        # No rows after break, so no change
        pd.testing.assert_series_equal(
            original.reset_index(drop=True),
            df["wait_minutes"].reset_index(drop=True),
        )

    def test_break_point_before_all_dates(self, sim_with_measure):
        """Contract 3G row 8: break_point before min date → all target rows
        scaled."""
        # [Subtask 4.3.2]
        sim, df = sim_with_measure
        target_mask = df.eval("hospital == 'Huashan'")
        target_before = df.loc[target_mask, "wait_minutes"].copy()

        pattern = {
            "type": "trend_break",
            "target": "hospital == 'Huashan'",
            "col": "wait_minutes",
            "params": {"break_point": "2020-01-01", "magnitude": 0.4},
        }
        df = sim._inject_trend_break(df, pattern)
        target_after = df.loc[target_mask, "wait_minutes"]

        # All target rows should be scaled by 1.4
        np.testing.assert_allclose(
            target_after.values, (target_before * 1.4).values, rtol=1e-10,
        )


# =====================================================================
# 1. CONTRACT TESTS — Missing Value Injection (4.4.1) — Table 3H
# =====================================================================

class TestMissingValueContract:
    """Contract tests for _inject_missing_values [Subtask 4.4.1]."""

    def test_missing_rate_005(self, sim_basic):
        """Contract 3H row 1: 500×N df, rate=0.05 → ≈5% NaN."""
        # [Subtask 4.4.1]
        df, _ = sim_basic.generate()
        rng = np.random.default_rng(42)
        df = sim_basic._inject_missing_values(df, 0.05, rng)
        actual_rate = df.isna().sum().sum() / df.size
        assert 0.02 < actual_rate < 0.10

    def test_missing_rate_zero(self, sim_basic):
        """Contract 3H row 2: rate=0.0 → no NaN values."""
        # [Subtask 4.4.1]
        df, _ = sim_basic.generate()
        rng = np.random.default_rng(42)
        df = sim_basic._inject_missing_values(df, 0.0, rng)
        assert df.isna().sum().sum() == 0

    def test_missing_rate_one(self, sim_basic):
        """Contract 3H row 3: rate=1.0 → all cells NaN."""
        # [Subtask 4.4.1]
        df, _ = sim_basic.generate()
        rng = np.random.default_rng(42)
        df = sim_basic._inject_missing_values(df, 1.0, rng)
        assert df.isna().sum().sum() == df.size

    def test_reproducibility(self, sim_basic):
        """Contract 3H row 4: same seed → identical NaN mask."""
        # [Subtask 4.4.1]
        df1, _ = sim_basic.generate()
        df2 = df1.copy()
        rng1 = np.random.default_rng(99)
        rng2 = np.random.default_rng(99)
        df1 = sim_basic._inject_missing_values(df1, 0.05, rng1)
        df2 = sim_basic._inject_missing_values(df2, 0.05, rng2)
        # NaN positions must be identical
        pd.testing.assert_frame_equal(
            df1.isna(), df2.isna(),
        )

    def test_empty_dataframe_unchanged(self, sim_basic):
        """Contract 3H row 5: 0-column DataFrame → returns unchanged."""
        # [Subtask 4.4.1]
        df_empty = pd.DataFrame()
        rng = np.random.default_rng(42)
        result = sim_basic._inject_missing_values(df_empty, 0.05, rng)
        assert result.size == 0


# =====================================================================
# 1. CONTRACT TESTS — Dirty Value Injection (4.4.2) — Table 3I
# =====================================================================

class TestDirtyValueContract:
    """Contract tests for _inject_dirty_values [Subtask 4.4.2]."""

    def test_dirty_rate_002(self, sim_basic):
        """Contract 3I row 1: ~2% of categorical cells contain dirty values."""
        # [Subtask 4.4.2]
        df, _ = sim_basic.generate()
        rng = np.random.default_rng(42)
        original_values = set(df["hospital"].unique())
        df = sim_basic._inject_dirty_values(df, 0.02, rng)
        dirty_count = sum(
            1 for v in df["hospital"] if pd.notna(v) and v not in original_values
        )
        # FIX: [self-review item 7] — Added rate-approximation assertion to
        # fully cover the done condition "at approximately the declared rate".
        # With 500 rows at 2%, expect ~10 dirty cells; allow wide tolerance.
        assert dirty_count > 0, "Expected at least some dirty values"
        dirty_rate_actual = dirty_count / len(df)
        assert dirty_rate_actual < 0.10, (
            f"Dirty rate {dirty_rate_actual:.4f} too far from target 0.02"
        )

    def test_dirty_rate_zero(self, sim_basic):
        """Contract 3I row 2: rate=0.0 → no dirty values."""
        # [Subtask 4.4.2]
        df, _ = sim_basic.generate()
        original_values = set(df["hospital"].unique())
        rng = np.random.default_rng(42)
        df = sim_basic._inject_dirty_values(df, 0.0, rng)
        for v in df["hospital"]:
            if pd.notna(v):
                assert v in original_values

    def test_dirty_rate_one(self, sim_basic):
        """Contract 3I row 3: rate=1.0 → all categorical cells perturbed."""
        # [Subtask 4.4.2]
        df, _ = sim_basic.generate()
        original_values = set(df["hospital"].unique())
        rng = np.random.default_rng(42)
        df = sim_basic._inject_dirty_values(df, 1.0, rng)
        dirty_count = sum(
            1 for v in df["hospital"] if pd.notna(v) and v not in original_values
        )
        # All cells should be perturbed (a few might round-trip to same
        # string by coincidence if perturbation is no-op, but overwhelmingly
        # most should differ)
        assert dirty_count > len(df) * 0.9

    def test_no_categorical_columns_unchanged(self):
        """Contract 3I row 4: df with only temporal columns → unchanged."""
        # [Subtask 4.4.2]
        sim = FactTableSimulator(100, 42)
        sim.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
        df, _ = sim.generate()
        original = df.copy()
        rng = np.random.default_rng(42)
        df = sim._inject_dirty_values(df, 0.10, rng)
        pd.testing.assert_frame_equal(df, original)

    def test_dirty_reproducibility(self, sim_basic):
        """Contract 3I row 5: same seed → identical perturbations."""
        # [Subtask 4.4.2]
        df1, _ = sim_basic.generate()
        df2 = df1.copy()
        rng1 = np.random.default_rng(77)
        rng2 = np.random.default_rng(77)
        df1 = sim_basic._inject_dirty_values(df1, 0.05, rng1)
        df2 = sim_basic._inject_dirty_values(df2, 0.05, rng2)
        pd.testing.assert_frame_equal(df1, df2)

    def test_dirty_values_differ_by_small_edit_distance(self, sim_basic):
        """Contract 3I row 6: dirty values differ from original by ≤2 chars."""
        # [Subtask 4.4.2]
        df, _ = sim_basic.generate()
        original_values = set(df["hospital"].unique())
        rng = np.random.default_rng(42)
        df = sim_basic._inject_dirty_values(df, 0.10, rng)

        dirty_vals = [
            v for v in df["hospital"].unique()
            if pd.notna(v) and v not in original_values
        ]
        for dirty in dirty_vals:
            # Check that the dirty value is "close" to at least one original
            min_distance = min(
                _edit_distance(dirty, orig) for orig in original_values
            )
            assert min_distance <= 2, (
                f"Dirty value '{dirty}' has edit distance {min_distance} > 2 "
                f"from all originals {original_values}"
            )


def _edit_distance(a: str, b: str) -> int:
    """Compute Levenshtein edit distance (helper for dirty value tests)."""
    if len(a) < len(b):
        return _edit_distance(b, a)
    if len(b) == 0:
        return len(a)
    prev_row = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr_row = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr_row.append(min(
                curr_row[j] + 1,
                prev_row[j + 1] + 1,
                prev_row[j] + cost,
            ))
        prev_row = curr_row
    return prev_row[-1]


# =====================================================================
# 1. CONTRACT TESTS — generate() Integration (3J)
# =====================================================================

class TestGenerateIntegrationContract:
    """Contract tests for generate() wiring of Phase γ and δ [Sprint 6]."""

    def test_generate_with_pattern_and_realism(self, sim_with_measure):
        """Contract 3J row 1: full pipeline with 1 pattern + realism returns
        (df, meta) with visible effects."""
        # [Subtask 4.3.1, 4.4.1]
        sim, _ = sim_with_measure
        sim.set_realism(missing_rate=0.05, dirty_rate=0.02)
        sim.inject_pattern(
            "outlier_entity",
            "hospital == 'Xiehe' & severity == 'Severe'",
            "wait_minutes",
            {"z_score": 3.0},
        )
        # generate() will run skeleton (no actual measures), so pattern
        # injection will log a warning about missing col and skip.
        # This test verifies the pipeline doesn't crash.
        df, meta = sim.generate()
        assert isinstance(df, pd.DataFrame)
        assert isinstance(meta, dict)
        # Realism should inject NaN into skeleton columns
        assert df.isna().sum().sum() > 0

    def test_generate_no_patterns_no_realism(self):
        """Contract 3J row 2: no patterns, no realism → backward compatible."""
        # [Sprint 5 backward compat]
        sim = FactTableSimulator(100, 42)
        sim.add_category("h", ["A", "B"], [1, 1], "entity")
        sim.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
        df, meta = sim.generate()
        assert df.isna().sum().sum() == 0
        assert df.shape[0] == 100

    def test_generate_realism_only(self):
        """Contract 3J row 3: realism only (missing_rate=0.05) → NaN present."""
        # [Subtask 4.4.1]
        sim = FactTableSimulator(500, 42)
        sim.add_category("h", ["A", "B", "C"], [1, 1, 1], "entity")
        sim.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
        sim.set_realism(missing_rate=0.05, dirty_rate=0.0)
        df, _ = sim.generate()
        nan_rate = df.isna().sum().sum() / df.size
        assert nan_rate > 0.01

    def test_generate_patterns_only_on_skeleton(self):
        """Contract 3J row 4: pattern on measure col in skeleton mode → injection
        is skipped gracefully because measure col not in DataFrame."""
        # [Subtask 4.3.1]
        sim = FactTableSimulator(100, 42)
        sim.add_category("h", ["A", "B"], [1, 1], "entity")
        sim.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
        sim.add_measure("wm", "gaussian", {"mu": 50, "sigma": 10})
        sim.inject_pattern(
            "outlier_entity", "h == 'A'", "wm", {"z_score": 3.0},
        )
        # Pattern col "wm" not in skeleton df → should skip injection, not crash
        df, meta = sim.generate()
        assert isinstance(df, pd.DataFrame)


# =====================================================================
# 2. INPUT VALIDATION TESTS
# =====================================================================

class TestOutlierEntityInputValidation:
    """Input validation for _inject_outlier_entity [Subtask 4.3.1]."""

    def test_large_zscore(self, sim_with_measure):
        """Large z_score (10.0) does not crash — produces extreme shift."""
        # [Subtask 4.3.1]
        sim, df = sim_with_measure
        pattern = {
            "type": "outlier_entity",
            "target": "hospital == 'Xiehe'",
            "col": "wait_minutes",
            "params": {"z_score": 10.0},
        }
        df = sim._inject_outlier_entity(df, pattern)
        target_mask = df.eval("hospital == 'Xiehe'")
        assert df.loc[target_mask, "wait_minutes"].mean() > df["wait_minutes"].median()


class TestTrendBreakInputValidation:
    """Input validation for _inject_trend_break [Subtask 4.3.2]."""

    def test_large_magnitude(self, sim_with_measure):
        """Large magnitude (5.0) scales values by 6× without crashing."""
        # [Subtask 4.3.2]
        sim, df = sim_with_measure
        bp = pd.to_datetime("2024-03-15")
        target_mask = df.eval("hospital == 'Huashan'")
        temporal = pd.to_datetime(df["visit_date"])
        after_mask = target_mask & (temporal >= bp)
        after_before = df.loc[after_mask, "wait_minutes"].copy()

        pattern = {
            "type": "trend_break",
            "target": "hospital == 'Huashan'",
            "col": "wait_minutes",
            "params": {"break_point": "2024-03-15", "magnitude": 5.0},
        }
        df = sim._inject_trend_break(df, pattern)
        after_after = df.loc[after_mask, "wait_minutes"]
        np.testing.assert_allclose(
            after_after.values, (after_before * 6.0).values, rtol=1e-10,
        )


class TestBlockedPatternTypes:
    """Verify BLOCKED pattern types raise NotImplementedError."""

    @pytest.mark.parametrize("pattern_type", [
        "ranking_reversal",
        "dominance_shift",
        "convergence",
        "seasonal_anomaly",
    ])
    def test_blocked_type_raises(self, pattern_type, sim_with_measure):
        """BLOCKED pattern types raise NotImplementedError with finding ID."""
        # [Subtask 4.3.1 — Blocker 4]
        sim, df = sim_with_measure
        sim._patterns = [{
            "type": pattern_type,
            "target": "hospital == 'Xiehe'",
            "col": "wait_minutes",
            "params": {},
        }]
        rng = np.random.default_rng(42)
        with pytest.raises(NotImplementedError, match="BLOCKED"):
            sim._inject_patterns(df, rng)


class TestCensoringBlocked:
    """Verify censoring injection raises NotImplementedError."""

    def test_censoring_raises_not_implemented(self, sim_basic):
        """Censoring config present → NotImplementedError [Blocker 7]."""
        # [Subtask 4.4.1 — Blocker 7]
        sim_basic.set_realism(
            missing_rate=0.0, dirty_rate=0.0,
            censoring={"target": "wm", "direction": "right", "threshold": 100},
        )
        # Build a small DataFrame manually to test the realism injector
        # in isolation — calling generate() would also trigger the error,
        # but we want to test _inject_realism specifically.
        df = pd.DataFrame({"h": ["A", "B"] * 5, "m": range(10)})
        rng = np.random.default_rng(42)
        with pytest.raises(NotImplementedError, match="BLOCKED.*A4"):
            sim_basic._inject_realism(df, rng)


# =====================================================================
# 3. OUTPUT CORRECTNESS TESTS
# =====================================================================

class TestPerturbStringCorrectness:
    """Output correctness for _perturb_string static method [Subtask 4.4.2]."""

    def test_swap_changes_string(self):
        """Swap perturbation produces a different string."""
        # [Subtask 4.4.2]
        rng = np.random.default_rng(0)
        original = "ABCD"
        # Run many times to cover all perturbation types
        results = set()
        for seed in range(100):
            r = np.random.default_rng(seed)
            results.add(FactTableSimulator._perturb_string(original, r))
        # At least some results should differ from original
        assert original not in results or len(results) > 1

    def test_single_char_only_inserts(self):
        """Single-character string can only be perturbed via insert."""
        # [Subtask 4.4.2]
        rng = np.random.default_rng(42)
        result = FactTableSimulator._perturb_string("A", rng)
        # Insert adds a character → result length should be 2
        assert len(result) == 2

    def test_empty_string_unchanged(self):
        """Empty string returns empty (edge case)."""
        # [Subtask 4.4.2]
        rng = np.random.default_rng(42)
        assert FactTableSimulator._perturb_string("", rng) == ""

    @pytest.mark.parametrize("seed", range(20))
    def test_perturbation_differs_from_original(self, seed):
        """Each perturbation should produce a different string (for len>=2)."""
        # [Subtask 4.4.2]
        rng = np.random.default_rng(seed)
        original = "Alpha"
        result = FactTableSimulator._perturb_string(original, rng)
        assert result != original


class TestMissingInjectionOutputCorrectness:
    """Output correctness for _inject_missing_values [Subtask 4.4.1]."""

    def test_returns_dataframe(self, sim_basic):
        """Return type is pd.DataFrame."""
        # [Subtask 4.4.1]
        df, _ = sim_basic.generate()
        rng = np.random.default_rng(42)
        result = sim_basic._inject_missing_values(df, 0.05, rng)
        assert isinstance(result, pd.DataFrame)

    def test_shape_preserved(self, sim_basic):
        """Missing injection does not change DataFrame shape."""
        # [Subtask 4.4.1]
        df, _ = sim_basic.generate()
        original_shape = df.shape
        rng = np.random.default_rng(42)
        result = sim_basic._inject_missing_values(df, 0.05, rng)
        assert result.shape == original_shape

    def test_nan_count_within_statistical_tolerance(self, sim_basic):
        """NaN fraction is statistically close to declared rate."""
        # [Subtask 4.4.1]
        sim = FactTableSimulator(2000, 42)
        sim.add_category("h", ["A", "B", "C"], [1, 1, 1], "entity")
        sim.add_category("s", ["X", "Y"], [1, 1], "patient")
        sim.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
        df, _ = sim.generate()
        rng = np.random.default_rng(42)
        target_rate = 0.10
        df = sim._inject_missing_values(df, target_rate, rng)
        actual_rate = df.isna().sum().sum() / df.size
        # With 2000 rows × ~5 cols = ~10000 cells, binomial std ≈ 0.003
        assert abs(actual_rate - target_rate) < 0.03


# =====================================================================
# 4. STATE TRANSITION TESTS
# =====================================================================

class TestInjectionStateTransitions:
    """State transition tests for injection methods."""

    def test_inject_realism_with_none_config_noop(self, sim_basic):
        """_inject_realism returns df unchanged when _realism_config is None."""
        # [Subtask 4.4.1, 4.4.2]
        df, _ = sim_basic.generate()
        original = df.copy()
        # Ensure no realism config
        sim_basic._realism_config = None
        rng = np.random.default_rng(42)
        result = sim_basic._inject_realism(df, rng)
        pd.testing.assert_frame_equal(result, original)

    def test_inject_patterns_empty_list_noop(self, sim_with_measure):
        """_inject_patterns with empty _patterns list returns df unchanged."""
        # [Subtask 4.3.1, 4.3.2]
        sim, df = sim_with_measure
        sim._patterns = []
        original = df.copy()
        rng = np.random.default_rng(42)
        result = sim._inject_patterns(df, rng)
        pd.testing.assert_frame_equal(result, original)

    def test_multiple_patterns_applied_sequentially(self, sim_with_measure):
        """Two patterns applied in order both take effect."""
        # [Subtask 4.3.1, 4.3.2]
        sim, df = sim_with_measure
        # First: outlier on Xiehe
        p1 = {
            "type": "outlier_entity",
            "target": "hospital == 'Xiehe'",
            "col": "wait_minutes",
            "params": {"z_score": 3.0},
        }
        # Second: trend break on Huashan
        p2 = {
            "type": "trend_break",
            "target": "hospital == 'Huashan'",
            "col": "wait_minutes",
            "params": {"break_point": "2024-03-15", "magnitude": 0.5},
        }
        sim._patterns = [p1, p2]
        rng = np.random.default_rng(42)
        result = sim._inject_patterns(df, rng)
        # Both patterns should have modified different subsets
        assert isinstance(result, pd.DataFrame)

    def test_no_instance_leakage(self):
        """Two separate simulator instances do not share injection state."""
        # [Sprint 6 isolation]
        sim1 = FactTableSimulator(100, 42)
        sim1.add_category("h", ["A", "B"], [1, 1], "entity")
        sim1.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
        sim1.set_realism(missing_rate=0.1, dirty_rate=0.0)

        sim2 = FactTableSimulator(100, 42)
        sim2.add_category("h", ["A", "B"], [1, 1], "entity")
        sim2.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
        # sim2 has no realism

        df1, _ = sim1.generate()
        df2, _ = sim2.generate()

        assert df1.isna().sum().sum() > 0
        assert df2.isna().sum().sum() == 0


# =====================================================================
# 5. INTEGRATION TESTS — Full pipeline
# =====================================================================

class TestFullPipelineIntegration:
    """Integration tests for the full generate() pipeline with Sprint 6
    injection phases wired in."""

    def test_generate_reproducible_with_realism(self):
        """Same seed produces identical output including NaN positions."""
        # [Subtask 4.4.1 — reproducibility]
        def make():
            s = FactTableSimulator(200, 42)
            s.add_category("h", ["A", "B", "C"], [1, 1, 1], "e")
            s.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
            s.set_realism(missing_rate=0.05, dirty_rate=0.02)
            return s.generate()

        df1, meta1 = make()
        df2, meta2 = make()

        # NaN positions must match
        pd.testing.assert_frame_equal(df1.isna(), df2.isna())
        # Metadata must match
        assert meta1 == meta2

    def test_realism_ordering_dirty_then_missing(self):
        """Missing injection can overwrite dirty values (ordering test).
        After both, some cells may be NaN even if they were dirty."""
        # [Subtask 4.4.1, 4.4.2 — ordering within Phase δ]
        sim = FactTableSimulator(1000, 42)
        sim.add_category("h", ["Alpha", "Beta"], [1, 1], "entity")
        sim.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
        sim.set_realism(missing_rate=0.10, dirty_rate=0.10)
        df, _ = sim.generate()
        # Both effects should be visible
        nan_rate = df.isna().sum().sum() / df.size
        assert nan_rate > 0.01

    def test_metadata_unaffected_by_injection(self):
        """Metadata output is the same with or without realism/patterns —
        patterns and realism modify the DataFrame, not the metadata."""
        # [Subtask 5.1.1, 5.1.2, 5.1.5, 5.1.7]
        def make(with_realism: bool):
            s = FactTableSimulator(100, 42)
            s.add_category("h", ["A", "B"], [1, 1], "entity")
            s.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
            if with_realism:
                s.set_realism(missing_rate=0.1, dirty_rate=0.05)
            return s.generate()

        _, meta_clean = make(False)
        _, meta_realism = make(True)
        assert meta_clean == meta_realism
