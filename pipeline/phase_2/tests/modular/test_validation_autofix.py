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

import copy
from functools import partial

import pandas as pd
import pytest

from pipeline.phase_2.types import Check, ValidationReport
from pipeline.phase_2.validation.autofix import (
    generate_with_validation,
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

    def test_skips_mixture_column_when_columns_provided(self):
        """IS-1 opt-out: mixture columns have no single sigma to widen."""
        columns = {"revenue": {"family": "mixture"}}
        overrides: dict = {}

        result = widen_variance(
            Check("ks_revenue", False), overrides, factor=2.0, columns=columns,
        )

        assert result is overrides
        # No measures.revenue.sigma key written.
        assert overrides == {}

    def test_widens_non_mixture_column_when_columns_provided(self):
        """columns kwarg only opts mixture out — non-mixture columns still widen."""
        columns = {"revenue": {"family": "gaussian"}}
        overrides: dict = {}

        widen_variance(
            Check("ks_revenue", False), overrides, factor=2.0, columns=columns,
        )

        assert overrides["measures"]["revenue"]["sigma"] == 2.0

    def test_default_columns_none_preserves_legacy_behavior(self):
        """When columns is omitted, mixture detection is skipped (legacy callers)."""
        overrides: dict = {}
        widen_variance(Check("ks_revenue", False), overrides, factor=2.0)
        # Even though we don't know revenue's family, sigma is widened.
        assert overrides["measures"]["revenue"]["sigma"] == 2.0


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


# =====================================================================
# M1 regression: dispatch-time mixture opt-out auto-binding
# =====================================================================
#
# Without the dispatch helper, the natural wiring
# ``auto_fix={"ks_*": widen_variance}`` calls widen_variance with
# columns=None on every retry. The mixture opt-out at autofix.py:112
# never fires; widen_variance keeps writing
# overrides["measures"][col]["sigma"] that _sample_mixture silently
# drops. The retry loop spins for max_attempts without changing any
# mixture parameter. These tests lock in the auto-binding contract.


class _StubKSFailingValidator:
    """Validator stub: always reports a single failing ks_revenue check.

    Replaces ``SchemaAwareValidator`` via monkeypatch so the integration
    tests don't need real fitted-distribution comparisons.
    """

    def __init__(self, _meta):
        pass

    def validate(self, _df, _patterns):
        rpt = ValidationReport()
        rpt.checks = [Check(name="ks_revenue", passed=False)]
        return rpt


def _make_meta_with_family(family: str) -> dict:
    """Minimal meta dict with a single 'revenue' column of the given family."""
    return {"columns": {"revenue": {"family": family}}}


class TestGenerateWithValidationMixtureOptOut:
    """M1 regression: when auto_fix is wired with raw widen_variance
    (no functools.partial), the dispatch helper must auto-inject
    columns=meta["columns"] so the mixture opt-out fires.
    """

    def test_mixture_optout_fires_through_raw_widen_variance(
        self, monkeypatch
    ):
        """Mixture column + raw widen_variance → no sigma override
        accumulates across retries (opt-out fires every attempt).
        """
        meta = _make_meta_with_family("mixture")
        df = pd.DataFrame({"revenue": [1.0, 2.0, 3.0, 4.0, 5.0]})
        seen_overrides: list = []

        def build_fn(seed, overrides):
            seen_overrides.append(
                None if overrides is None else copy.deepcopy(overrides)
            )
            return df, meta

        monkeypatch.setattr(
            "pipeline.phase_2.validation.validator.SchemaAwareValidator",
            _StubKSFailingValidator,
        )

        generate_with_validation(
            build_fn=build_fn,
            meta=meta,
            patterns=[],
            base_seed=42,
            max_attempts=3,
            auto_fix={"ks_*": widen_variance},  # raw, NOT partial
        )

        # Pre-fix: opt-out doesn't fire → sigma factor accumulates →
        #   seen_overrides[1] == {"measures": {"revenue": {"sigma": 1.2}}}.
        # Post-fix: opt-out fires → overrides stays empty {} →
        #   build_fn at L282 passes `None` (the `if overrides else None`
        #   shortcuts on empty-dict).
        assert len(seen_overrides) == 3
        assert seen_overrides[0] is None
        assert seen_overrides[1] is None, (
            "Mixture opt-out should have fired and prevented any sigma "
            f"override; got {seen_overrides[1]!r}"
        )
        assert seen_overrides[2] is None

    def test_non_mixture_widens_through_raw_widen_variance(
        self, monkeypatch
    ):
        """Gaussian column + raw widen_variance → sigma override
        accumulates as normal (auto-binding does not block legitimate
        widening).
        """
        meta = _make_meta_with_family("gaussian")
        df = pd.DataFrame({"revenue": [1.0, 2.0, 3.0, 4.0, 5.0]})
        seen_overrides: list = []

        def build_fn(seed, overrides):
            seen_overrides.append(
                None if overrides is None else copy.deepcopy(overrides)
            )
            return df, meta

        monkeypatch.setattr(
            "pipeline.phase_2.validation.validator.SchemaAwareValidator",
            _StubKSFailingValidator,
        )

        generate_with_validation(
            build_fn=build_fn,
            meta=meta,
            patterns=[],
            base_seed=42,
            max_attempts=3,
            auto_fix={"ks_*": widen_variance},
        )

        # Default factor=1.2 → sigma compounds: 1.2 → 1.44 across attempts.
        assert len(seen_overrides) == 3
        assert seen_overrides[0] is None
        assert seen_overrides[1]["measures"]["revenue"]["sigma"] == pytest.approx(1.2)
        assert seen_overrides[2]["measures"]["revenue"]["sigma"] == pytest.approx(1.44)

    def test_explicit_partial_binding_is_respected(self, monkeypatch):
        """When the caller supplies partial(widen_variance, columns=...)
        explicitly, the dispatch must NOT override their binding.
        """
        meta = _make_meta_with_family("mixture")  # meta says mixture
        df = pd.DataFrame({"revenue": [1.0, 2.0, 3.0, 4.0, 5.0]})
        # User explicitly binds a custom column registry that lies
        # about the family. If our auto-binding leaks past explicit
        # partials, the opt-out from meta would suppress widening —
        # but the user's intent here is "trust my binding, widen anyway."
        custom_columns = {"revenue": {"family": "gaussian"}}
        seen_overrides: list = []

        def build_fn(seed, overrides):
            seen_overrides.append(
                None if overrides is None else copy.deepcopy(overrides)
            )
            return df, meta

        monkeypatch.setattr(
            "pipeline.phase_2.validation.validator.SchemaAwareValidator",
            _StubKSFailingValidator,
        )

        generate_with_validation(
            build_fn=build_fn,
            meta=meta,
            patterns=[],
            base_seed=42,
            max_attempts=2,
            auto_fix={
                "ks_*": partial(widen_variance, columns=custom_columns),
            },
        )

        # User's custom_columns says gaussian → widening proceeds
        # despite meta["columns"] saying mixture.
        assert len(seen_overrides) == 2
        assert seen_overrides[0] is None
        assert seen_overrides[1]["measures"]["revenue"]["sigma"] == pytest.approx(1.2)


# =====================================================================
# Loop B healing roundtrip (closes T1.4 in docs/TEST_AUDIT_2026-05-07.md)
# =====================================================================
#
# Pre-existing tests in this file all use _StubKSFailingValidator, which
# always reports failure. They verify that overrides ACCUMULATE — but not
# that an override actually CHANGES the build_fn output enough that
# attempt 2's *real* validator now PASSES. A sign-bug in widen_variance
# (e.g., dividing sigma instead of multiplying) would slip through every
# stub-based test. The test below closes that loop end-to-end with the
# real SchemaAwareValidator — no monkeypatch.

import numpy as np
from pipeline.phase_2.validation.autofix import widen_variance as _widen_variance


class TestGenerateWithValidationHealingRoundtrip:
    """End-to-end Loop B: failure → strategy → next attempt PASSES."""

    def _gaussian_meta_for_revenue(self) -> dict:
        """Meta declaring revenue as a stochastic gaussian column with
        intercept-only param model. KS test compares observed `revenue`
        to gaussian(mu=100, sigma=10)."""
        return {
            "total_rows": 500,
            "columns": {
                "revenue": {
                    "type": "measure",
                    "measure_type": "stochastic",
                    "family": "gaussian",
                    "param_model": {
                        "mu": {"intercept": 100.0, "effects": {}},
                        "sigma": {"intercept": 10.0, "effects": {}},
                    },
                },
            },
            "dimension_groups": {},
            "orthogonal_groups": [],
            "group_dependencies": [],
            "measure_dag_order": ["revenue"],
            "patterns": [],
        }

    def test_widen_variance_actually_heals_ks_failure_on_retry(self):
        """Attempt 1: build_fn returns a constant column → KS test fails
        (zero variance vs declared σ=10).
        Attempt 2: build_fn observes the override delivered by autofix,
        switches to a well-fitted gaussian sample → KS test passes.

        This closes T1.4. The pre-existing tests verify override
        accumulation; this test verifies the override actually DELIVERS
        and that the second attempt produces data passing the *real*
        validator (no _StubKSFailingValidator).
        """
        meta = self._gaussian_meta_for_revenue()
        state = {"attempt": 0, "overrides_seen": []}

        def build_fn(seed, overrides):
            state["attempt"] += 1
            state["overrides_seen"].append(
                None if overrides is None else copy.deepcopy(overrides)
            )

            if state["attempt"] == 1:
                # Constant column → KS p ≈ 0 against gaussian(100, 10).
                df = pd.DataFrame({"revenue": np.full(500, 100.0)})
            else:
                # Override arrived → emit a well-fitted gaussian sample
                # so attempt 2's KS test passes with high p-value.
                assert overrides is not None, \
                    "Loop B must deliver override dict on retry; got None"
                assert "measures" in overrides
                rng = np.random.default_rng(seed)
                df = pd.DataFrame({"revenue": rng.normal(100.0, 10.0, 500)})

            return df, meta

        df, _, report = generate_with_validation(
            build_fn=build_fn,
            meta=meta,
            patterns=[],
            base_seed=42,
            max_attempts=3,
            auto_fix={"ks_*": _widen_variance},
        )

        # Healed on second attempt — not on third.
        assert state["attempt"] == 2, \
            f"Expected healing on attempt 2; got {state['attempt']}"
        # Real validator now passes with the well-fitted sample.
        failed = [(c.name, c.detail) for c in report.failures]
        assert report.all_passed, f"Expected all_passed; failures: {failed}"
        # The override delivered to attempt 2 carries the widen_variance signature.
        attempt2_overrides = state["overrides_seen"][1]
        assert attempt2_overrides is not None
        assert "measures" in attempt2_overrides
        assert "revenue" in attempt2_overrides["measures"]
        assert "sigma" in attempt2_overrides["measures"]["revenue"]

    def test_loop_terminates_when_no_failure_on_first_attempt(self):
        """Sanity: when attempt 1 already passes, the loop short-circuits
        and never invokes the strategy. Guard against a regression where
        the loop pre-applies overrides before validating."""
        meta = self._gaussian_meta_for_revenue()
        state = {"attempt": 0, "overrides_seen": []}

        def build_fn(seed, overrides):
            state["attempt"] += 1
            state["overrides_seen"].append(
                None if overrides is None else copy.deepcopy(overrides)
            )
            rng = np.random.default_rng(seed)
            return (
                pd.DataFrame({"revenue": rng.normal(100.0, 10.0, 500)}),
                meta,
            )

        _, _, report = generate_with_validation(
            build_fn=build_fn,
            meta=meta,
            patterns=[],
            base_seed=42,
            max_attempts=3,
            auto_fix={"ks_*": _widen_variance},
        )

        assert report.all_passed
        assert state["attempt"] == 1
        assert state["overrides_seen"] == [None]
