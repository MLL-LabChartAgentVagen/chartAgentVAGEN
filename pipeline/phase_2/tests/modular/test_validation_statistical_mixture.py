"""Tests for DS-3 mixture KS test in validation.statistical.

Covers:
  - Mixture KS passes when samples come from the declared mixture.
  - Mixture KS fails when samples come from a different distribution.
  - Mixture with an unsupported component family soft-passes.
  - _compute_cell_params recursion produces the {"components": [...]} shape.
  - _MixtureFrozen.cdf is a valid CDF (monotone, [0,1]).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import scipy.stats

from pipeline.phase_2.engine.measures import _sample_mixture
from pipeline.phase_2.validation.statistical import (
    _MixtureFrozen,
    _compute_cell_params,
    _expected_cdf,
    _expected_cdf_mixture,
    check_stochastic_ks,
)


def _gaussian_component(mu: float, sigma: float, weight: float) -> dict:
    return {
        "family": "gaussian",
        "weight": weight,
        "param_model": {
            "mu": {"intercept": mu},
            "sigma": {"intercept": sigma},
        },
    }


def _build_meta(col_name: str, components: list[dict]) -> dict:
    return {
        "columns": {
            col_name: {
                "type": "measure",
                "measure_type": "stochastic",
                "family": "mixture",
                "param_model": {"components": components},
            },
        },
    }


class TestComputeCellParamsRecursion:
    def test_mixture_returns_components_shape(self):
        col_meta = {
            "param_model": {
                "components": [
                    _gaussian_component(1.0, 2.0, 0.6),
                    _gaussian_component(5.0, 1.0, 0.4),
                ],
            },
        }
        out = _compute_cell_params(col_meta, predictor_values={}, columns_meta={})
        assert "components" in out
        assert len(out["components"]) == 2
        assert out["components"][0]["family"] == "gaussian"
        assert out["components"][0]["weight"] == 0.6
        assert out["components"][0]["params"] == {"mu": 1.0, "sigma": 2.0}
        assert out["components"][1]["params"] == {"mu": 5.0, "sigma": 1.0}

    def test_mixture_with_predictor_effects_resolves_per_cell(self):
        col_meta = {
            "param_model": {
                "components": [
                    {
                        "family": "gaussian",
                        "weight": 0.5,
                        "param_model": {
                            "mu": {"intercept": 0.0,
                                   "effects": {"region": {"north": 5.0, "south": -5.0}}},
                            "sigma": {"intercept": 1.0},
                        },
                    },
                    _gaussian_component(20.0, 1.0, 0.5),
                ],
            },
        }
        north_params = _compute_cell_params(
            col_meta, predictor_values={"region": "north"}, columns_meta={},
        )
        assert north_params["components"][0]["params"]["mu"] == 5.0
        assert north_params["components"][1]["params"]["mu"] == 20.0

        south_params = _compute_cell_params(
            col_meta, predictor_values={"region": "south"}, columns_meta={},
        )
        assert south_params["components"][0]["params"]["mu"] == -5.0


class TestMixtureFrozenCDF:
    def test_cdf_is_monotone_and_in_unit_interval(self):
        d1 = scipy.stats.norm(loc=0.0, scale=1.0)
        d2 = scipy.stats.norm(loc=10.0, scale=1.0)
        m = _MixtureFrozen([(0.6, d1), (0.4, d2)])
        x = np.linspace(-5, 15, 200)
        y = m.cdf(x)
        assert (y >= 0).all() and (y <= 1).all()
        assert (np.diff(y) >= -1e-12).all()  # monotone non-decreasing

    def test_cdf_matches_weighted_sum(self):
        d1 = scipy.stats.norm(loc=0.0, scale=1.0)
        d2 = scipy.stats.norm(loc=5.0, scale=2.0)
        m = _MixtureFrozen([(0.7, d1), (0.3, d2)])
        x = np.array([-2.0, 0.0, 2.5, 5.0, 8.0])
        expected = 0.7 * d1.cdf(x) + 0.3 * d2.cdf(x)
        np.testing.assert_allclose(m.cdf(x), expected)


class TestExpectedCdfMixture:
    def test_returns_mixture_frozen(self):
        params = {
            "components": [
                {"family": "gaussian", "weight": 0.5, "params": {"mu": 0.0, "sigma": 1.0}},
                {"family": "gaussian", "weight": 0.5, "params": {"mu": 5.0, "sigma": 1.0}},
            ],
        }
        m = _expected_cdf_mixture(params)
        assert isinstance(m, _MixtureFrozen)

    def test_dispatches_through_expected_cdf(self):
        params = {
            "components": [
                {"family": "gaussian", "weight": 1.0, "params": {"mu": 0.0, "sigma": 1.0}},
            ],
        }
        m = _expected_cdf("mixture", params)
        assert isinstance(m, _MixtureFrozen)

    def test_unsupported_component_returns_none(self):
        # Poisson has no scipy CDF in _expected_cdf — disables the whole mixture.
        params = {
            "components": [
                {"family": "gaussian", "weight": 0.5, "params": {"mu": 0.0, "sigma": 1.0}},
                {"family": "poisson", "weight": 0.5, "params": {"mu": 3.0}},
            ],
        }
        assert _expected_cdf_mixture(params) is None

    def test_empty_components_returns_none(self):
        assert _expected_cdf_mixture({"components": []}) is None
        assert _expected_cdf_mixture({}) is None

    def test_zero_weight_total_returns_none(self):
        params = {
            "components": [
                {"family": "gaussian", "weight": 0.0, "params": {"mu": 0.0, "sigma": 1.0}},
            ],
        }
        assert _expected_cdf_mixture(params) is None

    def test_normalizes_weights(self):
        d1 = scipy.stats.norm(loc=0.0, scale=1.0)
        params = {
            "components": [
                {"family": "gaussian", "weight": 0.3, "params": {"mu": 0.0, "sigma": 1.0}},
                {"family": "gaussian", "weight": 0.2, "params": {"mu": 0.0, "sigma": 1.0}},
            ],
        }
        m = _expected_cdf_mixture(params)
        # Normalized to (0.6, 0.4) — both pointing to the same dist, so
        # cdf(x) should equal d1.cdf(x).
        x = np.array([-1.0, 0.0, 1.0])
        np.testing.assert_allclose(m.cdf(x), d1.cdf(x), atol=1e-9)


class TestCheckStochasticKsMixture:
    def _components(self):
        return [
            _gaussian_component(0.0, 1.0, 0.5),
            _gaussian_component(8.0, 1.0, 0.5),
        ]

    def test_passes_for_correctly_sampled_data(self):
        components = self._components()
        meta = _build_meta("y", components)
        col_meta = meta["columns"]["y"]
        rng = np.random.default_rng(0)
        n = 3000
        sample = _sample_mixture("y", col_meta, {"_dummy": np.arange(n)}, rng)
        df = pd.DataFrame({"y": sample})

        checks = check_stochastic_ks(df, "y", meta)
        assert any(c.passed for c in checks), \
            f"At least one cell should pass; got {[(c.name, c.passed, c.detail) for c in checks]}"
        # No cell-level KS failure is expected
        assert all(c.passed for c in checks), \
            f"All checks should pass, failures: {[c.detail for c in checks if not c.passed]}"

    def test_fails_for_mismatched_distribution(self):
        # Sample from N(0,1) but declare a far-apart 2-component mixture.
        components = self._components()
        meta = _build_meta("y", components)
        rng = np.random.default_rng(0)
        sample = rng.normal(0.0, 1.0, size=2000)
        df = pd.DataFrame({"y": sample})

        checks = check_stochastic_ks(df, "y", meta)
        assert any(not c.passed for c in checks), \
            f"Expected at least one KS failure; got {[(c.name, c.passed, c.detail) for c in checks]}"

    def test_unsupported_component_soft_passes(self):
        # Mix gaussian with poisson — _expected_cdf_mixture returns None,
        # which makes the per-cell KS skip with a soft-pass detail.
        components = [
            _gaussian_component(0.0, 1.0, 0.5),
            {
                "family": "poisson",
                "weight": 0.5,
                "param_model": {"mu": {"intercept": 3.0}},
            },
        ]
        meta = _build_meta("y", components)
        rng = np.random.default_rng(0)
        df = pd.DataFrame({"y": rng.normal(0.0, 1.0, size=200)})

        checks = check_stochastic_ks(df, "y", meta)
        assert all(c.passed for c in checks)
        assert any("KS CDF not available" in (c.detail or "") for c in checks)
