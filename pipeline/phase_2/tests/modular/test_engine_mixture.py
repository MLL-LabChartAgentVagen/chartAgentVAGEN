"""Tests for IS-1 mixture distribution sampling in engine.measures.

Covers:
  - Weighted-mean correctness for 2-component mixtures.
  - 3-component samples pass scipy KS against the matching mixture CDF.
  - Auto-normalization of unnormalized weights.
  - Predictor effects propagated through per-component param_models.
  - Skewed weights / single-component / empty-rows edge cases.
  - Post-refactor: existing 7-family path still works through _sample_stochastic.
"""
from __future__ import annotations

import numpy as np
import pytest
import scipy.stats

from pipeline.phase_2.engine.measures import (
    _sample_family,
    _sample_mixture,
    _sample_stochastic,
)
from pipeline.phase_2.validation.statistical import _MixtureFrozen, _expected_cdf


def _rows(n: int) -> dict[str, np.ndarray]:
    return {"_dummy": np.arange(n)}


def _gaussian_component(mu: float, sigma: float, weight: float) -> dict:
    return {
        "family": "gaussian",
        "weight": weight,
        "param_model": {
            "mu": {"intercept": mu},
            "sigma": {"intercept": sigma},
        },
    }


def _mixture_meta(components: list[dict]) -> dict:
    return {
        "type": "measure",
        "measure_type": "stochastic",
        "family": "mixture",
        "param_model": {"components": components},
    }


class TestTwoComponentMean:
    def test_weighted_mean_matches_within_5_percent(self):
        # 60% N(0,1) + 40% N(10,1)  →  weighted mean = 4.0
        components = [
            _gaussian_component(mu=0.0, sigma=1.0, weight=0.6),
            _gaussian_component(mu=10.0, sigma=1.0, weight=0.4),
        ]
        col_meta = _mixture_meta(components)
        rng = np.random.default_rng(42)
        n = 10_000
        out = _sample_mixture("y", col_meta, _rows(n), rng)

        assert out.shape == (n,)
        empirical_mean = float(out.mean())
        assert abs(empirical_mean - 4.0) / 4.0 < 0.05


class TestThreeComponentKS:
    def test_samples_pass_self_ks(self):
        components = [
            _gaussian_component(mu=-5.0, sigma=1.0, weight=0.3),
            _gaussian_component(mu=0.0, sigma=0.5, weight=0.5),
            _gaussian_component(mu=5.0, sigma=2.0, weight=0.2),
        ]
        col_meta = _mixture_meta(components)
        rng = np.random.default_rng(7)
        n = 5000
        sample = _sample_mixture("y", col_meta, _rows(n), rng)

        # Build the exact same mixture CDF used by DS-3 and KS-test against it.
        weights = np.array([c["weight"] for c in components], dtype=float)
        weights /= weights.sum()
        frozen_components = [
            (float(w), _expected_cdf(c["family"], {"mu": c["param_model"]["mu"]["intercept"],
                                                    "sigma": c["param_model"]["sigma"]["intercept"]}))
            for w, c in zip(weights, components)
        ]
        mixture_cdf = _MixtureFrozen(frozen_components)

        stat, p_value = scipy.stats.kstest(sample, mixture_cdf.cdf)
        assert p_value > 0.05, f"KS test should pass, got p={p_value:.4f}, D={stat:.4f}"

    # ---------------------------------------------------------------------
    # T2.3 of TEST_AUDIT_2026-05-07.md.
    #
    # The pre-existing test uses a single weight configuration (0.3, 0.5, 0.2).
    # A regression in `_sample_mixture` that handled balanced mixtures fine
    # but mishandled skewed weights would slip through. The parametrized
    # variants below cover the extremes.
    # ---------------------------------------------------------------------

    @pytest.mark.parametrize("weights", [
        [0.1, 0.1, 0.8],   # heavily skewed toward one component
        [0.34, 0.33, 0.33],  # near-uniform
        [0.05, 0.475, 0.475],  # one tiny + two equal
    ])
    def test_self_ks_passes_across_weight_configurations(self, weights):
        components = [
            _gaussian_component(mu=-5.0, sigma=1.0, weight=weights[0]),
            _gaussian_component(mu=0.0, sigma=0.5, weight=weights[1]),
            _gaussian_component(mu=5.0, sigma=2.0, weight=weights[2]),
        ]
        col_meta = _mixture_meta(components)
        rng = np.random.default_rng(123)
        n = 5000
        sample = _sample_mixture("y", col_meta, _rows(n), rng)

        norm_weights = np.array(weights, dtype=float) / sum(weights)
        frozen_components = [
            (float(w), _expected_cdf(c["family"], {
                "mu": c["param_model"]["mu"]["intercept"],
                "sigma": c["param_model"]["sigma"]["intercept"],
            }))
            for w, c in zip(norm_weights, components)
        ]
        mixture_cdf = _MixtureFrozen(frozen_components)
        stat, p_value = scipy.stats.kstest(sample, mixture_cdf.cdf)
        assert p_value > 0.05, (
            f"KS failed for weights={weights}: p={p_value:.4f}, D={stat:.4f}"
        )


class TestComponentProportions:
    """T2.3 of TEST_AUDIT_2026-05-07.md.

    Pre-existing `TestTwoComponentMean` verifies the weighted *mean* matches
    expectation — but a sampler that always assigned every row to component
    0 would still produce a mean close to expectation when the marginal
    means are similar. The proportion check below directly verifies that
    the COUNT of rows assigned to each component matches the declared
    weights within a binomial 95% CI.

    Trick: the per-component samplers use disjoint mu and tight sigma so
    we can recover the latent component label from each sample's value.
    Component 0: N(-100, 0.5) → values ≈ -100. Component 1: N(0, 0.5).
    Component 2: N(+100, 0.5). With sigma=0.5 the components don't overlap.
    """

    def test_two_component_proportions_match_declared_weights(self):
        # Disjoint means + tight sigma so component labels are recoverable
        # from sample values via thresholding.
        components = [
            _gaussian_component(mu=-100.0, sigma=0.5, weight=0.6),
            _gaussian_component(mu=100.0, sigma=0.5, weight=0.4),
        ]
        col_meta = _mixture_meta(components)
        rng = np.random.default_rng(42)
        n = 10_000
        sample = _sample_mixture("y", col_meta, _rows(n), rng)

        # Recover component labels: sign separates the two means cleanly.
        n_comp0 = int((sample < 0).sum())
        n_comp1 = int((sample > 0).sum())
        assert n_comp0 + n_comp1 == n, "every sample must classify"

        # Binomial 95% CI for n=10000, p=0.6 → ±~96. Allow ±200 for safety.
        # Width chosen so a 50/50 sampler (broken) would fail loudly.
        expected_comp0 = int(0.6 * n)
        expected_comp1 = int(0.4 * n)
        assert abs(n_comp0 - expected_comp0) < 200, (
            f"Component 0 count {n_comp0} too far from expected "
            f"{expected_comp0} (declared weight=0.6)"
        )
        assert abs(n_comp1 - expected_comp1) < 200, (
            f"Component 1 count {n_comp1} too far from expected "
            f"{expected_comp1} (declared weight=0.4)"
        )

    def test_three_component_proportions_match_declared_weights(self):
        components = [
            _gaussian_component(mu=-100.0, sigma=0.5, weight=0.5),
            _gaussian_component(mu=0.0,    sigma=0.5, weight=0.3),
            _gaussian_component(mu=100.0,  sigma=0.5, weight=0.2),
        ]
        col_meta = _mixture_meta(components)
        rng = np.random.default_rng(42)
        n = 10_000
        sample = _sample_mixture("y", col_meta, _rows(n), rng)

        # Three disjoint clusters; threshold at ±50 to recover labels.
        n_low  = int((sample < -50).sum())
        n_mid  = int((abs(sample) <= 50).sum())
        n_high = int((sample > 50).sum())
        assert n_low + n_mid + n_high == n

        # Binomial 95% CI band ±200 for n=10k.
        for observed, expected, weight in [
            (n_low,  5000, 0.5),
            (n_mid,  3000, 0.3),
            (n_high, 2000, 0.2),
        ]:
            assert abs(observed - expected) < 200, (
                f"Observed {observed} for weight={weight} differs from "
                f"expected {expected} by more than 200 (n={n})"
            )


class TestWeightNormalization:
    def test_unnormalized_weights_match_normalized(self):
        # Same seed, two equivalent component weight specs → identical samples.
        unnorm = [
            _gaussian_component(0.0, 1.0, weight=0.3),
            _gaussian_component(10.0, 1.0, weight=0.2),
        ]
        norm = [
            _gaussian_component(0.0, 1.0, weight=0.6),
            _gaussian_component(10.0, 1.0, weight=0.4),
        ]
        n = 1000
        out_unnorm = _sample_mixture(
            "y", _mixture_meta(unnorm), _rows(n), np.random.default_rng(123),
        )
        out_norm = _sample_mixture(
            "y", _mixture_meta(norm), _rows(n), np.random.default_rng(123),
        )
        np.testing.assert_array_equal(out_unnorm, out_norm)


class TestPredictorEffectsInComponent:
    def test_per_region_means_align_with_mixture_expectation(self):
        # Component 0: gaussian(mu = intercept + region_effect, sigma=1), w=0.7.
        # Component 1: gaussian(mu=20, sigma=1), w=0.3.
        # Effective mixture mean per region: 0.7*(0 + region_eff) + 0.3*20 = 0.7*region_eff + 6.
        # north → 0.7*5 + 6 = 9.5; south → 0.7*(-5) + 6 = 2.5.
        components = [
            {
                "family": "gaussian",
                "weight": 0.7,
                "param_model": {
                    "mu": {"intercept": 0.0, "effects": {"region": {"north": 5.0, "south": -5.0}}},
                    "sigma": {"intercept": 1.0},
                },
            },
            _gaussian_component(20.0, 1.0, weight=0.3),
        ]
        col_meta = _mixture_meta(components)

        n = 8000
        # half north, half south
        region = np.array(["north"] * (n // 2) + ["south"] * (n // 2))
        rows = {"region": region, "_dummy": np.arange(n)}
        rng = np.random.default_rng(0)
        out = _sample_mixture("y", col_meta, rows, rng)

        north_mean = float(out[region == "north"].mean())
        south_mean = float(out[region == "south"].mean())
        assert abs(north_mean - 9.5) < 0.5, f"north mean {north_mean} != 9.5"
        assert abs(south_mean - 2.5) < 0.5, f"south mean {south_mean} != 2.5"


class TestSkewedWeights:
    def test_extremely_skewed_weights_do_not_crash(self):
        components = [
            _gaussian_component(0.0, 1.0, weight=0.999),
            _gaussian_component(100.0, 1.0, weight=0.001),
        ]
        col_meta = _mixture_meta(components)
        rng = np.random.default_rng(0)
        out = _sample_mixture("y", col_meta, _rows(50), rng)
        assert out.shape == (50,)
        # Most rows draw from component 0 (mean ≈ 0).
        assert out.mean() < 5.0


class TestSingleComponent:
    def test_weight_one_single_gaussian_matches_base_family(self):
        components = [_gaussian_component(3.0, 2.0, weight=1.0)]
        col_meta = _mixture_meta(components)
        rng = np.random.default_rng(0)
        n = 5000
        sample = _sample_mixture("y", col_meta, _rows(n), rng)

        # KS-test against scipy.stats.norm(3, 2).
        stat, p_value = scipy.stats.kstest(
            sample, scipy.stats.norm(loc=3.0, scale=2.0).cdf,
        )
        assert p_value > 0.05, f"single-component mixture should match N(3,2); p={p_value:.4f}"


class TestDispatchThroughSampleStochastic:
    def test_mixture_dispatched_via_sample_stochastic(self):
        components = [
            _gaussian_component(0.0, 1.0, weight=0.5),
            _gaussian_component(5.0, 1.0, weight=0.5),
        ]
        col_meta = _mixture_meta(components)
        rng = np.random.default_rng(1)
        out = _sample_stochastic("y", col_meta, _rows(1000), rng)
        assert out.shape == (1000,)
        # rough mean check
        assert 1.0 < out.mean() < 4.0


class TestSampleFamilyExtraction:
    """Post-refactor: _sample_family is the single dispatch point for all
    non-mixture families. Smoke-test each."""

    def test_gaussian(self):
        rng = np.random.default_rng(0)
        params = {"mu": np.zeros(100), "sigma": np.ones(100)}
        out = _sample_family("x", "gaussian", params, 100, rng)
        assert out.shape == (100,)

    def test_lognormal(self):
        rng = np.random.default_rng(0)
        params = {"mu": np.zeros(100), "sigma": np.ones(100) * 0.5}
        out = _sample_family("x", "lognormal", params, 100, rng)
        assert (out > 0).all()

    def test_gamma(self):
        rng = np.random.default_rng(0)
        params = {"mu": np.full(100, 2.0), "sigma": np.full(100, 1.0)}
        out = _sample_family("x", "gamma", params, 100, rng)
        assert (out >= 0).all()

    def test_beta(self):
        rng = np.random.default_rng(0)
        params = {"mu": np.full(100, 2.0), "sigma": np.full(100, 5.0)}
        out = _sample_family("x", "beta", params, 100, rng)
        assert ((out >= 0) & (out <= 1)).all()

    def test_uniform(self):
        rng = np.random.default_rng(0)
        params = {"mu": np.zeros(100), "sigma": np.full(100, 10.0)}
        out = _sample_family("x", "uniform", params, 100, rng)
        assert ((out >= 0) & (out <= 10.0)).all()

    def test_poisson(self):
        rng = np.random.default_rng(0)
        params = {"mu": np.full(100, 3.0), "sigma": np.ones(100)}
        out = _sample_family("x", "poisson", params, 100, rng)
        assert (out >= 0).all()
        assert out.dtype == np.float64

    def test_exponential(self):
        rng = np.random.default_rng(0)
        params = {"mu": np.full(100, 2.0), "sigma": np.ones(100)}
        out = _sample_family("x", "exponential", params, 100, rng)
        assert (out >= 0).all()

    def test_unknown_family_raises(self):
        rng = np.random.default_rng(0)
        params = {"mu": np.zeros(10), "sigma": np.ones(10)}
        with pytest.raises(ValueError, match="Unknown distribution family"):
            _sample_family("x", "weibull", params, 10, rng)


class TestEdgeCases:
    def test_empty_rows_returns_empty_array(self):
        components = [_gaussian_component(0.0, 1.0, weight=1.0)]
        col_meta = _mixture_meta(components)
        rng = np.random.default_rng(0)
        out = _sample_mixture("y", col_meta, {}, rng)
        assert out.shape == (0,)

    def test_missing_components_raises(self):
        col_meta = {"family": "mixture", "param_model": {}}
        rng = np.random.default_rng(0)
        with pytest.raises(ValueError, match="components"):
            _sample_mixture("y", col_meta, _rows(10), rng)

    def test_zero_weight_sum_raises(self):
        # Bypassing the validator — sampler must still defend itself.
        col_meta = {
            "family": "mixture",
            "param_model": {
                "components": [
                    {"family": "gaussian", "weight": 0.0,
                     "param_model": {"mu": {"intercept": 0.0}, "sigma": {"intercept": 1.0}}},
                ],
            },
        }
        rng = np.random.default_rng(0)
        with pytest.raises(ValueError, match="weight sum"):
            _sample_mixture("y", col_meta, _rows(10), rng)
