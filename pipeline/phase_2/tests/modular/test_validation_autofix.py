"""
Tests for Loop B Auto-fix strategies.

Tested functions:
- match_strategy         (unchanged signature)
- widen_variance         (REWRITTEN: new accumulator-based contract)
- amplify_magnitude      (REWRITTEN: requires patterns list)
- reshuffle_pair         (REWRITTEN: now only flags columns; engine reshuffles)

The old direct-mutation API (widen_variance(check, params, factor) -> new_params,
reshuffle_pair(check, df, col, rng) -> new_df) was replaced by the
ParameterOverrides accumulator pattern: each strategy mutates and returns an
overrides dict that run_pipeline later merges into the engine's parameters.
"""
from __future__ import annotations

from pipeline.phase_2.types import Check
from pipeline.phase_2.validation.autofix import (
    match_strategy,
    widen_variance,
    amplify_magnitude,
    reshuffle_pair,
)


class TestMatchStrategy:
    def test_exact_match(self):
        auto_fix = {"foo": "plan_a"}
        assert match_strategy("foo", auto_fix) == "plan_a"

    def test_glob_match(self):
        auto_fix = {"pattern_*": "plan_a"}
        assert match_strategy("pattern_outlier_region", auto_fix) == "plan_a"

    def test_no_match(self):
        auto_fix = {"pattern_*": "plan_a"}
        assert match_strategy("cardinality_geo", auto_fix) is None


class TestWidenVariance:
    def test_writes_sigma_factor_to_overrides(self):
        """widen_variance stores a multiplicative sigma factor under
        overrides['measures'][col]."""
        check = Check("ks_revenue", False)  # extracted col = "revenue"
        overrides: dict = {}

        result = widen_variance(check, overrides, factor=1.5)

        assert result is overrides  # mutated & returned same object
        assert overrides["measures"]["revenue"]["sigma"] == 1.5

    def test_compounds_across_retries(self):
        """Repeated calls compound: 1.5 * 1.5 = 2.25."""
        check = Check("ks_revenue", False)
        overrides: dict = {}

        widen_variance(check, overrides, factor=1.5)
        widen_variance(check, overrides, factor=1.5)

        assert overrides["measures"]["revenue"]["sigma"] == 2.25

    def test_isolated_per_column(self):
        """Different columns get independent sigma factors."""
        overrides: dict = {}
        widen_variance(Check("ks_revenue", False), overrides, factor=2.0)
        widen_variance(Check("ks_cost", False), overrides, factor=3.0)

        assert overrides["measures"]["revenue"]["sigma"] == 2.0
        assert overrides["measures"]["cost"]["sigma"] == 3.0


class TestAmplifyMagnitude:
    def test_amplifies_z_score_on_matching_pattern(self):
        check = Check("outlier_revenue", False)
        patterns = [{"col": "revenue", "params": {"z_score": 3.0}}]
        overrides: dict = {}

        result = amplify_magnitude(check, overrides, patterns=patterns, factor=1.5)

        assert result is overrides
        # Stored under patterns[0] since that's the matching index
        assert overrides["patterns"][0]["params"]["z_score"] == 4.5
        # Original pattern list is not mutated
        assert patterns[0]["params"]["z_score"] == 3.0

    def test_amplifies_magnitude_on_matching_pattern(self):
        # _extract_col_from_check_name splits on the FIRST underscore only,
        # so "outlier_sales" -> "sales".
        check = Check("outlier_sales", False)
        patterns = [{"col": "sales", "params": {"magnitude": 10}}]
        overrides: dict = {}

        amplify_magnitude(check, overrides, patterns=patterns, factor=2)

        assert overrides["patterns"][0]["params"]["magnitude"] == 20

    def test_skips_non_matching_patterns(self):
        """Only the pattern whose col matches the check's extracted col is updated."""
        check = Check("outlier_revenue", False)
        patterns = [
            {"col": "cost", "params": {"z_score": 3.0}},
            {"col": "revenue", "params": {"z_score": 3.0}},
        ]
        overrides: dict = {}

        amplify_magnitude(check, overrides, patterns=patterns, factor=2.0)

        # Only index 1 (revenue) is in overrides; index 0 (cost) is not.
        assert 0 not in overrides["patterns"]
        assert overrides["patterns"][1]["params"]["z_score"] == 6.0


class TestReshufflePair:
    def test_flags_column_for_reshuffle(self):
        check = Check("ks_revenue", False)  # extracted col = "revenue"
        overrides: dict = {}

        result = reshuffle_pair(check, overrides)

        assert result is overrides
        assert overrides["reshuffle"] == ["revenue"]

    def test_deduplicates_repeat_calls(self):
        """Calling twice for the same column does not add a duplicate."""
        check = Check("ks_revenue", False)
        overrides: dict = {}

        reshuffle_pair(check, overrides)
        reshuffle_pair(check, overrides)

        assert overrides["reshuffle"] == ["revenue"]

    def test_multiple_columns_accumulate(self):
        overrides: dict = {}
        reshuffle_pair(Check("ks_revenue", False), overrides)
        reshuffle_pair(Check("ks_cost", False), overrides)

        assert overrides["reshuffle"] == ["revenue", "cost"]
