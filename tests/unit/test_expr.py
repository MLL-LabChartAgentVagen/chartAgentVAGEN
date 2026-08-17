"""Expressions: parsing, which columns they reference, and evaluating them.

An expression is the only place the model says how a number comes about, so two
things must hold: the same seed gives the same column, and an undefined symbol is
reported by name.
"""

import numpy as np
import pytest

from chartgen.s01_data import expr as E
from chartgen.s01_data.declare import DeclarationError

N = 6
SEVERITY = np.array(["Minor", "Moderate", "Severe", "Minor", "Severe", "Moderate"])
HOSPITAL = np.array(["Mercy General", "St. Luke's", "Riverside",
                     "Mercy General", "Mercy General", "Riverside"])
WAIT = np.array([10.0, 20.0, 30.0, 40.0, 50.0, 60.0])


@pytest.fixture
def env() -> dict[str, np.ndarray]:
    return {"severity": SEVERITY, "hospital": HOSPITAL, "wait_minutes": WAIT}


def ev(text: str, env: dict, seed: int = 7) -> np.ndarray:
    return E.parse(text).eval(env, np.random.default_rng(seed), N)


class TestReferencedColumns:
    def test_a_bare_column_name_is_a_reference(self):
        assert E.parse("wait_minutes * 12").columns == {"wait_minutes"}

    def test_an_indicator_references_its_category_column(self):
        assert E.parse("0.9*[severity=Severe]").columns == {"severity"}

    def test_a_lookup_references_the_column_it_indexes(self):
        assert E.parse("{'Minor': 80, 'Moderate': 260}[severity]").columns == {"severity"}

    def test_indicator_values_may_contain_spaces(self):
        assert E.parse("0.2*[hospital=Mercy General]").columns == {"hospital"}

    def test_distribution_names_are_not_columns(self):
        assert E.parse("gaussian(0, 30)").columns == set()

    def test_edges_keep_only_references_to_other_measures(self):
        edges = E.edges((("cost", "wait_minutes * 12 + [severity=Severe]"),
                         ("wait_minutes", "gaussian(30, 5)")))
        assert edges == (("wait_minutes", "cost"),)


class TestCategoryEffects:
    def test_an_indicator_is_one_where_the_value_matches(self, env):
        assert list(ev("[severity=Severe]", env)) == [0, 0, 1, 0, 1, 0]

    def test_a_lookup_maps_every_row_to_its_number(self, env):
        got = ev("{'Minor': 80, 'Moderate': 260, 'Severe': 700}[severity]", env)
        assert list(got) == [80, 260, 700, 80, 700, 260]

    def test_a_lookup_missing_a_value_names_the_value(self, env):
        with pytest.raises(DeclarationError) as exc:
            ev("{'Minor': 80}[severity]", env)
        assert "Moderate" in str(exc.value) and "severity" in str(exc.value)


class TestArithmeticAndClipping:
    def test_arithmetic_runs_on_the_whole_column_at_once(self, env):
        assert list(ev("wait_minutes * 12 + 100", env)) == [220, 340, 460, 580, 700, 820]

    def test_clip_bounds_both_ends(self, env):
        assert list(ev("clip(wait_minutes, 25, 45)", env)) == [25, 25, 30, 40, 45, 45]

    def test_where_selects_by_a_comparison(self, env):
        assert list(ev("where(wait_minutes > 30, 1, 0)", env)) == [0, 0, 0, 1, 1, 1]


class TestDistributions:
    def test_a_distribution_draws_one_value_per_row(self, env):
        assert ev("gaussian(0, 1)", env).shape == (N,)

    def test_the_same_seed_gives_the_same_column(self, env):
        assert list(ev("lognormal(mu=2.8, sigma=0.35)", env)) == \
               list(ev("lognormal(mu=2.8, sigma=0.35)", env))

    def test_a_different_seed_gives_a_different_column(self, env):
        assert list(ev("gaussian(0, 1)", env, seed=1)) != list(ev("gaussian(0, 1)", env, seed=2))

    def test_a_distribution_parameter_may_itself_be_a_column(self, env):
        """A distribution parameter may itself vary per row."""
        got = ev("lognormal(mu = 2.8 + 0.9*[severity=Severe], sigma = 0.01)", env)
        assert got[2] > got[0] and got[4] > got[3]

    def test_every_declared_distribution_family_evaluates(self, env):
        for text in ("gaussian(0, 1)", "lognormal(mu=1, sigma=0.2)", "gamma(2, 3)",
                     "beta(2, 5)", "uniform(1, 9)", "poisson(4)", "exponential(3)",
                     "mixture(0.3, 1, 100)"):
            assert ev(text, env).shape == (N,), text


class TestUndefinedSymbols:
    def test_an_undefined_name_is_reported_by_name(self, env):
        with pytest.raises(DeclarationError) as exc:
            ev("base_fee + 10", env)
        assert "base_fee" in str(exc.value)

    def test_an_unknown_function_is_reported_by_name(self, env):
        with pytest.raises(DeclarationError) as exc:
            E.parse("weibull(1, 2)").eval(env, np.random.default_rng(0), N)
        assert "weibull" in str(exc.value)

    def test_syntax_errors_are_reported_as_declaration_errors(self):
        with pytest.raises(DeclarationError):
            E.parse("2 * * 3")

    def test_attribute_access_and_imports_are_not_expressions(self):
        with pytest.raises(DeclarationError):
            E.parse("__import__('os').system('echo hi')").eval({}, np.random.default_rng(0), 1)
