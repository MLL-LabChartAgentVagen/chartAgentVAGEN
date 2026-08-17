"""Generating the fact table: dependency graph, topological order, three passes.

Two things must hold. Declarations plus a seed reproduce bit for bit, and every
category column ends up with exactly the values it declared -- because which chart
families are drawable was decided from those declared counts.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from chartgen.s01_data import declare as D
from chartgen.s01_data import engine as G
from chartgen.s01_data.expr import DeclarationError

SAMPLE = json.loads(Path("tests/samples/er_scenario.json").read_text(encoding="utf-8"))
SEED = 20260816


@pytest.fixture(scope="module")
def script() -> D.Script:
    return D.run(SAMPLE["script"])


@pytest.fixture(scope="module")
def df(script) -> pd.DataFrame:
    return G.generate(script, SEED)


class TestTopologicalOrder:
    def test_a_measure_comes_after_what_it_references(self, script):
        order = G.topo_order(script)
        assert order.index("wait_minutes") < order.index("cost")
        assert order.index("wait_minutes") < order.index("satisfaction")

    def test_a_cycle_names_the_loop(self):
        script = D.run('dim("a", ["A", "B"], group="g")\ndim("b", ["u", "v"], group="h")\n'
                       'measure("cost", "revenue * 2", unit="USD", additive=True)\n'
                       'measure("revenue", "cost * 3", unit="USD", additive=True)\nemit(10)')
        with pytest.raises(DeclarationError) as exc:
            G.topo_order(script)
        assert "cost" in str(exc.value) and "revenue" in str(exc.value)


class TestOneRowIsOneEvent:
    def test_emit_fixes_the_row_count_exactly(self, df):
        assert len(df) == 900

    def test_every_declared_column_is_a_column_of_the_table(self, df):
        assert list(df.columns) == ["hospital", "department", "severity", "visit_date",
                                    "day_of_week", "month", "quarter", "is_weekend",
                                    "wait_minutes", "cost", "satisfaction"]

    def test_the_table_is_not_a_category_cross_product(self, df):
        """One row is one event, not one cell of a cross product."""
        assert len(df.groupby(["hospital", "department", "severity"], observed=True)) == 36
        assert len(df) > 36


class TestCardinalityMatchesTheDeclaration:
    """What was declared and what was generated must agree."""

    def test_every_declared_dimension_value_appears(self, df, script):
        for d in script.dims:
            assert set(df[d.name].unique()) == set(d.values), d.name

    def test_every_time_point_appears(self, df, script):
        assert df["visit_date"].nunique() == len(script.time.points())

    def test_the_derived_calendar_columns_match_their_declared_values(self, df, script):
        declared = D.calendar_values(script.time.points())
        for name, values in declared.items():
            assert set(df[name].unique()) == set(values), name


class TestEveryDeclaredValueGetsRows:
    """Allocation has to give every declared value at least one row."""

    def test_a_tiny_weight_still_gets_one_row(self):
        script = D.run('dim("a", ["A", "B", "C", "D", "E", "F", "G"], '
                       'weights=[0.40, 0.30, 0.15, 0.08, 0.04, 0.02, 0.001], group="g")\n'
                       'dim("b", ["u", "v"], group="h")\n'
                       'measure("m", "gaussian(0,1)", unit="u", additive=True)\n'
                       'measure("n", "m * 2", unit="u", additive=True)\nemit(378)')
        counts = G.generate(script, SEED)["a"].value_counts()
        assert len(counts) == 7 and counts.min() >= 1
        assert counts["A"] == pytest.approx(378 * 0.40, abs=3)

    def test_a_tiny_conditional_weight_still_gets_one_row(self):
        script = D.run('dim("p", ["P1", "P2"], weights=[0.9, 0.1], group="g")\n'
                       'dim("c", ["u", "v", "w"], parent="p", '
                       'weights={"P1": [0.98, 0.01, 0.01], "P2": [0.5, 0.3, 0.2]})\n'
                       'dim("k", ["x", "y"], group="h")\n'
                       'measure("m", "gaussian(0,1)", unit="u", additive=True)\n'
                       'measure("n", "m * 2", unit="u", additive=True)\nemit(200)')
        df = G.generate(script, SEED)
        assert set(df[df["p"] == "P1"]["c"].unique()) == {"u", "v", "w"}

    def test_more_values_than_rows_names_the_column(self):
        script = D.run('dim("a", ["A", "B", "C", "D", "E"], group="g")\n'
                       'dim("b", ["u", "v"], group="h")\n'
                       'measure("m", "gaussian(0,1)", unit="u", additive=True)\n'
                       'measure("n", "m * 2", unit="u", additive=True)\nemit(3)')
        with pytest.raises(DeclarationError, match="a"):
            G.generate(script, SEED)


class TestWeights:
    def test_root_weights_set_the_marginal(self, df):
        share = df["hospital"].value_counts(normalize=True)
        assert share["Mercy General"] == pytest.approx(0.40, abs=0.01)
        assert share["Riverside"] == pytest.approx(0.25, abs=0.01)

    def test_child_weights_are_conditional_on_the_parent(self, df):
        riverside = df[df["hospital"] == "Riverside"]["department"].value_counts(normalize=True)
        assert riverside["Internal Medicine"] == pytest.approx(0.30, abs=0.02)
        assert riverside["Pediatrics"] == pytest.approx(0.15, abs=0.02)

    def test_an_unweighted_dimension_is_uniform(self):
        script = D.run('dim("a", ["A", "B", "C", "D"], group="g")\n'
                       'dim("b", ["u", "v"], group="h")\n'
                       'measure("m", "gaussian(0,1)", unit="u", additive=True)\n'
                       'measure("n", "m * 2", unit="u", additive=True)\nemit(400)')
        counts = G.generate(script, SEED)["a"].value_counts()
        assert set(counts) == {100}


class TestCalendarDerivation:
    def test_day_of_week_agrees_with_the_date(self, df):
        stamps = pd.to_datetime(df["visit_date"])
        assert (df["day_of_week"] == stamps.dt.strftime("%a")).all()

    def test_month_and_quarter_agree_with_the_date(self, df):
        stamps = pd.to_datetime(df["visit_date"])
        assert (df["month"] == stamps.dt.strftime("%Y-%m")).all()
        assert (df["quarter"] == stamps.dt.year.astype(str) + "-Q"
                + stamps.dt.quarter.astype(str)).all()

    def test_is_weekend_is_a_string_so_keys_stay_strings(self, df):
        assert set(df["is_weekend"].unique()) == {"Yes", "No"}


class TestCalendarFieldsFollowTheSchema:
    def test_a_constant_calendar_field_is_not_generated_either(self):
        script = D.run('dim("a", ["A", "B"], group="g")\ndim("b", ["u", "v"], group="h")\n'
                       'time("wk", start="2023-01-02", end="2024-06-24", freq="weekly")\n'
                       'measure("m", "gaussian(0,1)", unit="u", additive=True)\n'
                       'measure("n", "m * 2", unit="u", additive=True)\nemit(300)')
        df = G.generate(script, SEED)
        assert "day_of_week" not in df.columns and "is_weekend" not in df.columns
        assert "month" in df.columns and "quarter" in df.columns


class TestMeasures:
    def test_the_category_effect_moves_the_mean(self, df):
        by_severity = df.groupby("severity", observed=True)["wait_minutes"].mean()
        assert by_severity["Severe"] > by_severity["Moderate"] > by_severity["Minor"]

    def test_a_dependent_measure_follows_its_parent(self, df):
        assert df["cost"].corr(df["wait_minutes"]) > 0.8
        assert df["satisfaction"].corr(df["wait_minutes"]) < -0.5

    def test_clip_bounds_are_respected_after_generation(self, df):
        assert df["satisfaction"].between(1, 5).all()

    def test_every_measure_is_finite_and_not_constant(self, df):
        for name in ("wait_minutes", "cost", "satisfaction"):
            assert np.isfinite(df[name]).all() and df[name].nunique() > 1

    def test_decimals_follow_the_unit(self, df):
        assert (df["cost"] == df["cost"].round(0)).all()          # an amount in USD is whole
        assert (df["wait_minutes"] == df["wait_minutes"].round(1)).all()
        assert df["wait_minutes"].round(0).ne(df["wait_minutes"]).any()

    def test_an_undefined_symbol_names_itself(self):
        script = D.run('dim("a", ["A", "B"], group="g")\ndim("b", ["u", "v"], group="h")\n'
                       'measure("m", "base_fee + 1", unit="u", additive=True)\n'
                       'measure("n", "gaussian(0,1)", unit="u", additive=True)\nemit(10)')
        with pytest.raises(DeclarationError, match="base_fee"):
            G.generate(script, SEED)


class TestDeterminism:
    def test_the_same_declaration_and_seed_give_the_same_table(self, script, df):
        pd.testing.assert_frame_equal(df, G.generate(script, SEED))

    def test_a_different_seed_gives_a_different_table(self, script, df):
        assert not df.equals(G.generate(script, SEED + 1))

    def test_adding_a_measure_does_not_move_the_existing_columns(self, script, df):
        text = SAMPLE["script"].replace(
            "emit(900)", 'measure("extra", "gaussian(0, 1)", unit="u", additive=True)\nemit(900)')
        grown = G.generate(D.run(text), SEED)
        for name in ("hospital", "visit_date", "wait_minutes", "cost"):
            pd.testing.assert_series_equal(df[name], grown[name])
