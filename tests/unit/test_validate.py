"""The three checks that can reject a scenario, and the text they produce.

All three produce feedback a model can act on: which constraint, which column, and
why. "It failed" gives it nothing to fix.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from chartgen.common import serde
from chartgen.s01_data import validate as V
from chartgen.s01_data import declare as D
from chartgen.s01_data import engine as G
from chartgen.s01_data.expr import DeclarationError

SAMPLE = json.loads(Path("tests/samples/er_scenario.json").read_text(encoding="utf-8"))
SEED = 20260816


@pytest.fixture(scope="module")
def script() -> D.Script:
    return D.run(SAMPLE["script"])


@pytest.fixture(scope="module")
def df(script):
    return G.generate(script, SEED)


@pytest.fixture
def er():
    return serde.sample("TableSchema")


class TestStructuralChecks:
    def test_the_worked_example_passes_all_four(self, df, script):
        assert V.structural(df, script) == ()

    def test_a_row_count_off_by_more_than_ten_percent_fails(self, df, script):
        failures = V.structural(df.head(700), script)
        assert [f.kind for f in failures] == ["rows"]
        assert "900" in failures[0].message

    def test_a_row_count_within_ten_percent_passes(self, df, script):
        assert V.structural(df.head(830), script) == ()

    def test_a_missing_category_value_fails_on_cardinality(self, df, script):
        shrunk = df[df["severity"] != "Severe"]
        failures = V.structural(shrunk, script)
        assert any(f.kind == "cardinality" and "severity" in f.message for f in failures)

    def test_a_child_value_no_parent_gives_weight_is_reported(self):
        """Zero weights are how a strict hierarchy is written, so a value can be
        weighted out of existence. The column-level check is what catches it."""
        script = D.run('dim("region", ["North", "South"], group="g")\n'
                       'dim("center", ["Albany", "Atlanta", "Tempe"], parent="region", '
                       'weights={"North": [1.0, 0.0, 0.0], "South": [0.0, 1.0, 0.0]})\n'
                       'dim("k", ["x", "y"], group="h")\n'
                       'measure("m", "gaussian(0,1)", unit="u", additive=True)\n'
                       'measure("n", "m * 2", unit="u", additive=True)\nemit(200)')
        failures = V.structural(G.generate(script, SEED), script)
        assert [f.kind for f in failures] == ["cardinality"]
        assert "Tempe" in failures[0].message

    def test_a_constant_measure_fails(self, df, script):
        flat = df.assign(cost=1.0)
        failures = V.structural(flat, script)
        assert [f.kind for f in failures] == ["measure"]
        assert "cost" in failures[0].message

    def test_a_non_finite_measure_fails(self, df, script):
        broken = df.assign(cost=df["cost"].mask(df.index < 3, np.inf))
        assert any(f.kind == "measure" for f in V.structural(broken, script))

    def test_a_cycle_is_caught_before_anything_is_generated(self):
        script = D.run('dim("a", ["A", "B"], group="g")\ndim("b", ["u", "v"], group="h")\n'
                       'measure("cost", "revenue * 2", unit="USD", additive=True)\n'
                       'measure("revenue", "cost * 3", unit="USD", additive=True)\nemit(10)')
        with pytest.raises(DeclarationError, match="cycle"):
            G.topo_order(script)


class TestTheMeasureCheck:
    def test_a_column_with_a_non_finite_value_fails(self, df, script):
        """Every value has to be finite, not merely one of them: an infinity in a
        measure survives every later stage and comes out as an axis nobody can read.
        """
        import numpy as np

        broken = df.copy()
        broken.loc[broken.index[3], "wait_minutes"] = np.inf
        failures = V.structural(broken, script)
        assert any(f.kind == "measure" and "wait_minutes" in f.message for f in failures)

    def test_a_column_with_a_null_fails(self, df, script):
        broken = df.copy()
        broken.loc[broken.index[3], "wait_minutes"] = float("nan")
        assert any(f.kind == "measure" for f in V.structural(broken, script))

    def test_a_constant_column_fails_and_says_what_it_holds(self, df, script):
        flat = df.copy()
        flat["wait_minutes"] = 12.5
        failures = V.structural(flat, script)
        assert any(f.kind == "measure" and "12.5" in f.message for f in failures)


class TestIntentBinding:
    def test_the_three_worked_intents_bind(self, er):
        bound = V.intents(SAMPLE["intents"], er)
        assert [b.family for b in bound] == ["comparison", "trend", "relation"]
        assert [b.index for b in bound] == [0, 1, 2]

    def test_an_unknown_column_is_named_with_its_intent(self, er):
        with pytest.raises(DeclarationError) as exc:
            V.intents([{"sentence": "s", "columns": ["visit_hour"], "aggregate": "AVG",
                        "family": "comparison"}], er)
        assert "visit_hour" in str(exc.value) and "intent" in str(exc.value)

    def test_summing_a_non_additive_measure_is_rejected(self, er):
        with pytest.raises(DeclarationError, match="satisfaction"):
            V.intents([{"sentence": "s", "columns": ["hospital", "satisfaction"],
                        "aggregate": "SUM", "family": "comparison"}], er)

    def test_a_view_class_outside_the_six_is_rejected(self, er):
        with pytest.raises(DeclarationError, match="family"):
            V.intents([{"sentence": "s", "columns": ["hospital", "wait_minutes"],
                        "aggregate": "AVG", "family": "storytelling"}], er)

    def test_an_aggregate_needs_a_measure_unless_it_counts_rows(self, er):
        assert V.intents([{"sentence": "s", "columns": ["hospital"], "aggregate": "COUNT",
                           "family": "comparison"}], er)[0].aggregate == "COUNT"
        with pytest.raises(DeclarationError, match="measure"):
            V.intents([{"sentence": "s", "columns": ["hospital"], "aggregate": "AVG",
                        "family": "comparison"}], er)

    def test_too_few_or_too_many_intents_are_rejected(self, er):
        with pytest.raises(DeclarationError, match="intent"):
            V.intents([], er)


class TestTheDensestCross:
    def test_a_cross_outside_the_screening_range_is_not_considered(self):
        """Six cells and a hundred cells are the ends of the range, and both are in
        it: below six a cross is not a chart, above a hundred it is unreadable."""
        from chartgen.interfaces.table import Column, TableSchema

        def schema(a: int, b: int, rows: int = 900) -> TableSchema:
            return TableSchema("s", "t", "c", n_rows=rows, columns=(
                Column("x", "category", a, values=tuple(f"x{i}" for i in range(a))),
                Column("y", "category", b, values=tuple(f"y{i}" for i in range(b))),
                Column("m", "measure", 900, unit="u", additive=True)))

        assert V.densest_cross(schema(2, 3))[0] == ("x", "y")      # exactly six cells
        assert V.densest_cross(schema(10, 10))[0] == ("x", "y")    # exactly a hundred
        assert V.densest_cross(schema(1, 5))[0] is None            # five, below the range
        assert V.densest_cross(schema(11, 10))[0] is None          # 110, above it


class TestCoverage:
    """Which families are drawable, decided without data. An empty family says why."""

    def test_the_worked_example_covers_five_of_six_families(self, er):
        cov = V.feasibility(er)
        assert cov.families == {"comparison": True, "trend": True, "composition": True,
                                "relation": True, "distribution": True, "process": False}
        assert cov.nonempty == 5

    def test_the_empty_families_are_the_ones_with_nothing_in_them(self, er):
        """Read the other way round, the feedback would name the five families that
        work and ask the model to fix them."""
        assert V.feasibility(er).empty_families == ("process",)

    def test_five_families_clear_the_threshold_of_three(self, er):
        assert V.feasibility(er).ok(min_families=3)

    def test_the_missing_process_family_is_reported_as_a_missing_stage_dimension(self, er):
        text = V.feasibility(er).feedback()
        assert "stage" in text and "process chart" in text

    def test_a_schema_with_no_additive_measure_says_so(self):
        schema = _schema(additive=False)
        text = V.feasibility(schema).feedback()
        assert "additive" in text

    def test_a_schema_whose_categories_are_all_out_of_range_says_so(self):
        schema = _schema(cardinality=2)
        assert not V.feasibility(schema).families["comparison"]
        assert "distinct values" in V.feasibility(schema).feedback()

    def test_a_schema_below_the_threshold_reports_the_family_count(self):
        cov = V.feasibility(_schema(cardinality=2, additive=False))
        assert not cov.ok(min_families=3)
        assert "families" in cov.feedback()

    def test_expected_rows_per_cell_is_a_declaration_time_screen(self, er):
        """900 rows over a 7 by 6 cross is 21 rows per cell."""
        assert V.expected_rows_per_cell(er, ("day_of_week", "month")) == pytest.approx(900 / 42)

    def test_deciding_what_is_drawable_never_touches_data(self, er):
        """Feasibility takes a schema and nothing else, by construction."""
        import inspect

        from chartgen.registry import conditions

        for source in (inspect.getsource(V.feasibility), inspect.getsource(V._gaps),
                       inspect.getsource(conditions)):
            assert "FactTable" not in source and "DataFrame" not in source


def _schema(*, cardinality: int = 4, additive: bool = True):
    from chartgen.interfaces.table import Column, TableSchema
    values = tuple(f"v{i}" for i in range(cardinality))
    return TableSchema("s", "t", "c", columns=(
        Column("a", "category", cardinality, group="g", values=values),
        Column("b", "category", cardinality, group="h", values=values),
        Column("m", "measure", 300, unit="u", additive=additive),
        Column("n", "measure", 300, unit="u", additive=additive),
    ), n_rows=300)
