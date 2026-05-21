"""Tests for DS-3 mixture KS test in validation.statistical.

Covers:
  - Mixture KS passes when samples come from the declared mixture.
  - Mixture KS fails when samples come from a different distribution.
  - Mixture with an unsupported component family soft-passes.
  - _compute_cell_params recursion produces the {"components": [...]} shape.
  - MixtureFrozen.cdf is a valid CDF (monotone, [0,1]).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import scipy.stats

from pipeline.phase_2.engine.distributions import (
    MixtureFrozen,
    expected_cdf,
    expected_cdf_mixture,
)
from pipeline.phase_2.engine.measures import _sample_mixture
from pipeline.phase_2.validation.statistical import (
    _compute_cell_params,
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
        m = MixtureFrozen([(0.6, d1), (0.4, d2)])
        x = np.linspace(-5, 15, 200)
        y = m.cdf(x)
        assert (y >= 0).all() and (y <= 1).all()
        assert (np.diff(y) >= -1e-12).all()  # monotone non-decreasing

    def test_cdf_matches_weighted_sum(self):
        d1 = scipy.stats.norm(loc=0.0, scale=1.0)
        d2 = scipy.stats.norm(loc=5.0, scale=2.0)
        m = MixtureFrozen([(0.7, d1), (0.3, d2)])
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
        m = expected_cdf_mixture(params)
        assert isinstance(m, MixtureFrozen)

    def test_dispatches_throughexpected_cdf(self):
        params = {
            "components": [
                {"family": "gaussian", "weight": 1.0, "params": {"mu": 0.0, "sigma": 1.0}},
            ],
        }
        m = expected_cdf("mixture", params)
        assert isinstance(m, MixtureFrozen)

    def test_unsupported_component_returns_none(self):
        # Poisson has no scipy CDF in expected_cdf — disables the whole mixture.
        params = {
            "components": [
                {"family": "gaussian", "weight": 0.5, "params": {"mu": 0.0, "sigma": 1.0}},
                {"family": "poisson", "weight": 0.5, "params": {"mu": 3.0}},
            ],
        }
        assert expected_cdf_mixture(params) is None

    def test_empty_components_returns_none(self):
        assert expected_cdf_mixture({"components": []}) is None
        assert expected_cdf_mixture({}) is None

    def test_zero_weight_total_returns_none(self):
        params = {
            "components": [
                {"family": "gaussian", "weight": 0.0, "params": {"mu": 0.0, "sigma": 1.0}},
            ],
        }
        assert expected_cdf_mixture(params) is None

    def test_normalizes_weights(self):
        d1 = scipy.stats.norm(loc=0.0, scale=1.0)
        params = {
            "components": [
                {"family": "gaussian", "weight": 0.3, "params": {"mu": 0.0, "sigma": 1.0}},
                {"family": "gaussian", "weight": 0.2, "params": {"mu": 0.0, "sigma": 1.0}},
            ],
        }
        m = expected_cdf_mixture(params)
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
        # Mix gaussian with poisson — expected_cdf_mixture returns None,
        # which makes the cell skip and surface as a "no testable cells"
        # aggregate Check (silent-pass, intentional under Path D).
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
        assert len(checks) == 1
        assert checks[0].passed
        assert "no-CDF" in (checks[0].detail or "")


class TestMixtureKsPValueExtraction:
    """T2.3 of TEST_AUDIT_2026-05-07.md (adapted for Path D aggregate Check).

    Pre-existing tests asserted `c.passed` only — the threshold semantic
    (`p > 0.05`, spec §2.6 L2) was invisible to tests. A regression that
    inverted the comparison to `p > 0.95` would still report `passed=True`
    for any well-fitted sample. After Path D the threshold becomes a
    Bonferroni-corrected alpha, listed in the aggregate detail alongside
    per-cell (n, D, p) tuples — extraction below re-locks the semantic.
    """

    def _components(self):
        return [
            _gaussian_component(0.0, 1.0, 0.5),
            _gaussian_component(8.0, 1.0, 0.5),
        ]

    def test_passing_check_has_p_value_above_alpha(self):
        """A correctly-sampled mixture: the aggregate Check passes, and
        every per-cell p in the detail is above the reported alpha."""
        import re
        components = self._components()
        meta = _build_meta("y", components)
        col_meta = meta["columns"]["y"]
        rng = np.random.default_rng(0)
        sample = _sample_mixture(
            "y", col_meta, {"_dummy": np.arange(3000)}, rng,
        )
        df = pd.DataFrame({"y": sample})

        checks = check_stochastic_ks(df, "y", meta)
        assert len(checks) == 1
        c = checks[0]
        assert c.passed

        # Extract alpha and per-cell p-values from detail.
        m_alpha = re.search(r"α=([\d.eE+-]+)", c.detail or "")
        assert m_alpha is not None, f"alpha not in detail: {c.detail}"
        alpha = float(m_alpha.group(1))
        assert alpha > 0 and alpha <= 0.05, (
            f"alpha {alpha} should be in (0, 0.05]"
        )

        p_values = [float(s) for s in re.findall(r"p=([\d.eE+-]+)", c.detail or "")]
        assert p_values, (
            f"Expected per-cell p-values in detail; got: {c.detail}"
        )
        for p in p_values:
            assert p > alpha, (
                f"Per-cell p={p} should exceed alpha={alpha} in a passing aggregate"
            )

    def test_failing_check_has_p_value_at_or_below_alpha(self):
        """When sampled data does NOT match the declared mixture, the
        aggregate Check fails and at least one per-cell p in detail is
        ≤ alpha."""
        import re
        components = self._components()
        meta = _build_meta("y", components)
        rng = np.random.default_rng(0)
        # Sample from N(0, 1) only — not the declared bimodal mixture.
        df = pd.DataFrame({"y": rng.normal(0.0, 1.0, size=3000)})

        checks = check_stochastic_ks(df, "y", meta)
        assert len(checks) == 1
        c = checks[0]
        assert not c.passed

        m_alpha = re.search(r"α=([\d.eE+-]+)", c.detail or "")
        assert m_alpha is not None
        alpha = float(m_alpha.group(1))

        # detail format separates "Failed cells:" and "Passed cells:" sections.
        failed_section = re.search(r"Failed cells:(.*?)(Passed cells:|$)", c.detail or "")
        assert failed_section is not None, (
            f"Expected a 'Failed cells:' section in failing aggregate; "
            f"got: {c.detail}"
        )
        failed_p_values = [
            float(s)
            for s in re.findall(r"p=([\d.eE+-]+)", failed_section.group(1))
        ]
        assert failed_p_values, (
            f"Expected at least one failed cell p-value; got: {c.detail}"
        )
        for p in failed_p_values:
            assert p <= alpha, (
                f"Failed cell p={p} should be ≤ alpha={alpha}"
            )
