"""Deciding what can be drawn from declarations alone."""

import ast
import inspect
from pathlib import Path

from dataclasses import replace

import pytest

from chartgen.common import serde
from chartgen.interfaces.figure import Binding
from chartgen.interfaces.table import Column, TableSchema
from chartgen.registry import conditions as C


@pytest.fixture
def er() -> TableSchema:
    """The schema of the worked example."""
    return serde.sample("TableSchema")


def bind(chart_type: str, **kw) -> Binding:
    return Binding(chart_type, **kw)


class TestStructuralConditions:
    def test_bar_on_one_category_and_one_measure_passes(self, er):
        assert C.check(bind("bar", dims=("hospital",), measures=("wait_minutes",),
                            aggregate="AVG"), er).ok

    def test_bar_rejects_cardinality_below_three(self, er):
        schema = TableSchema("s", "t", "c", columns=(
            Column("side", "category", 2, values=("Left", "Right")),
            Column("m", "measure", 100, unit="units", additive=True),
        ), n_rows=100)
        r = C.check(bind("bar", dims=("side",), measures=("m",), aggregate="AVG"), schema)
        assert not r.ok and "cardinality" in r.reason

    def test_bar_rejects_cardinality_above_thirty(self, er):
        schema = TableSchema("s", "t", "c", columns=(
            Column("sku", "category", 400, values=tuple(str(i) for i in range(400))),
            Column("m", "measure", 100, unit="units", additive=True),
        ), n_rows=100)
        assert not C.check(bind("bar", dims=("sku",), measures=("m",), aggregate="AVG"),
                           schema).ok

    def test_grouped_bar_needs_two_category_columns(self, er):
        r = C.check(bind("grouped_bar", dims=("hospital",), measures=("wait_minutes",),
                         aggregate="AVG"), er)
        assert not r.ok and "category columns" in r.reason

    def test_grouped_bar_product_must_be_between_six_and_twentyfour(self, er):
        assert C.check(bind("grouped_bar", dims=("hospital", "department"),
                            measures=("wait_minutes",), aggregate="AVG"), er).ok    # 3×4 = 12
        r = C.check(bind("grouped_bar", dims=("day_of_week", "month"),
                         measures=("wait_minutes",), aggregate="AVG"), er)          # 7×6 = 42
        assert not r.ok and "cardinality" in r.reason

    def test_the_same_column_cannot_take_two_roles(self, er):
        r = C.check(bind("grouped_bar", dims=("hospital", "hospital"),
                         measures=("wait_minutes",), aggregate="AVG"), er)
        assert not r.ok and "several roles" in r.reason

    def test_unknown_column_is_reported_by_name(self, er):
        r = C.check(bind("bar", dims=("visit_hour",), measures=("wait_minutes",),
                         aggregate="AVG"), er)
        assert not r.ok and "visit_hour" in r.reason

    def test_a_measure_cannot_fill_a_category_role(self, er):
        r = C.check(bind("bar", dims=("wait_minutes",), measures=("cost",),
                         aggregate="AVG"), er)
        assert not r.ok

    def test_line_needs_a_time_column_with_at_least_five_points(self, er):
        assert C.check(bind("line", time="visit_date", measures=("wait_minutes",),
                            aggregate="AVG"), er).ok
        assert not C.check(bind("line", dims=("hospital",), measures=("wait_minutes",),
                                aggregate="AVG"), er).ok

    def test_a_type_that_takes_no_time_column_refuses_one(self, er):
        """The count of time columns is checked in both directions. Checked in one,
        a bar drawn against a date axis passes the structural gate and is rejected
        much later, by the projection, as a chart with hundreds of categories."""
        assert C.check(bind("bar", dims=("hospital",), measures=("wait_minutes",),
                            aggregate="AVG"), er).ok
        assert not C.check(bind("bar", dims=("hospital",), time="visit_date",
                                measures=("wait_minutes",), aggregate="AVG"), er).ok

    def test_a_type_that_needs_a_time_column_refuses_to_go_without(self, er):
        assert not C.check(bind("windsock", dims=("hospital",),
                                measures=("wait_minutes",), aggregate="FIVE_NUM"), er).ok

    def test_a_monthly_column_counts_its_points_in_months(self):
        """Counting a monthly column's points as if they were days emptied the
        whole trend family for every scenario that is not daily."""
        monthly = TableSchema("s", "t", "c", columns=(
            Column("posting_month", "time", 36, group="calendar", freq="monthly"),
            Column("provision", "measure", 360, unit="USD", additive=True)), n_rows=360)
        assert C.check(bind("line", time="posting_month", measures=("provision",),
                            aggregate="SUM"), monthly).ok
        assert C.family_nonempty("trend", monthly)

    def test_resampling_only_coarsens_a_time_axis(self, er):
        assert C.check(bind("line", time="visit_date", measures=("wait_minutes",),
                            aggregate="AVG", resample="monthly"), er).ok      # 182 days -> 6
        short = TableSchema("s", "t", "c", columns=(
            Column("week", "time", 8, group="calendar", freq="weekly"),
            Column("m", "measure", 80, unit="units", additive=True)), n_rows=80)
        assert C.check(bind("line", time="week", measures=("m",), aggregate="SUM",
                            resample="daily"), short).ok                      # stays 8 weeks

    def test_line_allows_one_to_six_series(self, er):
        assert C.check(bind("line", time="visit_date", dims=("hospital",),
                            measures=("wait_minutes",), aggregate="AVG"), er).ok
        assert not C.check(bind("line", time="visit_date", dims=("day_of_week",),
                                measures=("wait_minutes",), aggregate="AVG"), er).ok  # seven series

    def test_histogram_needs_a_hundred_raw_rows(self, er):
        assert C.check(bind("histogram", measures=("wait_minutes",), aggregate="BIN_COUNT"), er).ok
        small = TableSchema("s", "t", "c", columns=(
            Column("m", "measure", 40, unit="units", additive=True),), n_rows=40)
        r = C.check(bind("histogram", measures=("m",), aggregate="BIN_COUNT"), small)
        assert not r.ok and "source rows" in r.reason

    def test_scatter_needs_exactly_two_measures(self, er):
        assert C.check(bind("scatter", measures=("wait_minutes", "satisfaction"),
                            aggregate="NONE"), er).ok
        assert not C.check(bind("scatter", measures=("wait_minutes",), aggregate="NONE"), er).ok

    def test_a_range_bar_reuses_the_five_number_projection(self, er):
        """Two rectangles' worth of edges come out of the same five numbers a box
        plot uses, so there is no RANGE aggregate to invent."""
        assert C.check(bind("range_bar", dims=("hospital",), measures=("wait_minutes",),
                            aggregate="FIVE_NUM"), er).ok
        assert not C.check(bind("range_bar", dims=("hospital",), measures=("wait_minutes",),
                                aggregate="AVG"), er).ok

    def test_a_windsock_needs_a_time_column_and_no_category(self, er):
        assert C.check(bind("windsock", time="visit_date", measures=("wait_minutes",),
                            aggregate="FIVE_NUM", resample="monthly"), er).ok
        assert not C.check(bind("windsock", dims=("hospital",), time="visit_date",
                                measures=("wait_minutes",), aggregate="FIVE_NUM"), er).ok

    def test_a_table_chart_answers_no_view_class_so_no_family_reaches_it(self, er):
        from chartgen.registry.charts import CHARTS, FAMILIES, familyless, in_family

        assert CHARTS["table_chart"].family is None
        assert "table_chart" in {c.name for c in familyless()}
        assert all("table_chart" not in {c.name for c in in_family(f)} for f in FAMILIES)
        assert C.check(bind("table_chart", dims=("department",), measures=("wait_minutes",),
                            aggregate="AVG"), er).ok

    def test_the_family_walk_reaches_the_family_less_types_through_none(self, er):
        got = list(C.iter_bindings_for_family(None, er))
        assert got and {b.chart_type for b in got} == {"category_line", "table_chart"}


class TestSemanticConditions:
    def test_pie_requires_an_additive_measure(self, er):
        assert C.check(bind("pie", dims=("department",), measures=("cost",),
                            aggregate="SUM"), er).ok
        r = C.check(bind("pie", dims=("department",), measures=("satisfaction",),
                         aggregate="AVG"), er)
        assert not r.ok and "additive" in r.reason

    def test_sum_over_a_non_additive_measure_is_never_legal(self, er):
        r = C.check(bind("bar", dims=("hospital",), measures=("satisfaction",),
                         aggregate="SUM"), er)
        assert not r.ok and "aggregates" in r.reason

    def test_median_is_legal_on_a_non_additive_measure(self, er):
        assert C.check(bind("bar", dims=("hospital",), measures=("satisfaction",),
                            aggregate="MEDIAN"), er).ok

    def test_median_is_not_in_the_additive_aggregate_set(self, er):
        assert not C.check(bind("bar", dims=("hospital",), measures=("wait_minutes",),
                                aggregate="MEDIAN"), er).ok

    def test_funnel_requires_a_stage_dimension(self, er):
        r = C.check(bind("funnel", dims=("severity",), measures=("wait_minutes",),
                         aggregate="SUM"), er)
        assert not r.ok and "stage" in r.reason

    def test_funnel_passes_when_the_dimension_is_a_stage(self):
        schema = TableSchema("s", "t", "c", columns=(
            Column("step", "category", 4, ordered="stage",
                   values=("Triage", "Exam", "Imaging", "Admission")),
            Column("n", "measure", 900, unit="visits", additive=True),
        ), n_rows=900)
        assert C.check(bind("funnel", dims=("step",), measures=("n",), aggregate="SUM"),
                       schema).ok

    def test_ordinal_is_not_a_stage(self, er):
        assert not C.check(bind("waterfall", dims=("severity",), measures=("cost",),
                                aggregate="SUM"), er).ok


class TestAggregateSet:
    def test_five_num_belongs_to_the_boxlike_shape_only(self, er):
        assert C.check(bind("box", dims=("department",), measures=("wait_minutes",),
                            aggregate="FIVE_NUM"), er).ok
        assert not C.check(bind("bar", dims=("hospital",), measures=("wait_minutes",),
                                aggregate="FIVE_NUM"), er).ok

    def test_per_row_shapes_take_aggregate_none(self, er):
        assert not C.check(bind("scatter", measures=("wait_minutes", "satisfaction"),
                                aggregate="AVG"), er).ok

    def test_count_needs_no_measure(self, er):
        assert C.check(bind("bar", dims=("hospital",), aggregate="COUNT"), er).ok

    def test_a_non_count_aggregate_needs_a_measure(self, er):
        assert not C.check(bind("bar", dims=("hospital",), aggregate="AVG"), er).ok


class TestCoverage:
    """Which families are non-empty, decided before any data exists."""

    def test_er_schema_has_five_of_six_families_non_empty(self, er):
        cov = C.coverage(er)
        assert cov == {"comparison": True, "trend": True, "composition": True,
                       "relation": True, "distribution": True, "process": False}

    def test_process_is_empty_without_a_stage_dimension(self, er):
        assert not C.family_nonempty("process", er)

    def test_composition_survives_without_an_additive_measure_via_count(self, er):
        """Counting rows needs no measure, so a share-of-total chart is still legal.

    Having no additive measure is a gap worth reporting, not an empty family.
        """
        no_additive = TableSchema("s", "t", "c", columns=(
            Column("hospital", "category", 3, values=("Mercy General", "St. Luke's", "Riverside")),
            Column("rate", "measure", 900, unit="%", additive=False),
            Column("score", "measure", 900, unit="points", additive=False),
        ), n_rows=900)
        assert C.family_nonempty("composition", no_additive)
        assert next(C.iter_bindings("pie", no_additive)).aggregate == "COUNT"

    def test_composition_is_empty_when_no_category_column_fits_the_cardinality(self):
        wide = TableSchema("s", "t", "c", columns=(
            Column("sku", "category", 400, values=tuple(str(i) for i in range(400))),
            Column("rate", "measure", 900, unit="%", additive=False),
        ), n_rows=900)
        assert not C.family_nonempty("composition", wide)

    def test_tier_limit_shrinks_coverage(self, er):
        assert C.family_nonempty("distribution", er, max_tier=1)      # histogram
        no_category = TableSchema("s", "t", "c", columns=(
            Column("wait", "measure", 40, unit="minutes", additive=True),
        ), n_rows=40)
        # A histogram needs a hundred source rows and nothing else at tier one can
        # group forty rows without a category column.
        assert not C.family_nonempty("distribution", no_category, max_tier=1)
        assert not C.family_nonempty("distribution", no_category, max_tier=2)

    def test_a_range_bar_covers_distribution_at_tier_one_where_only_a_box_used_to(self):
        few_rows = TableSchema("s", "t", "c", columns=(
            Column("hospital", "category", 3, values=("Mercy General", "St. Luke's", "Riverside")),
            Column("wait", "measure", 40, unit="minutes", additive=True),
        ), n_rows=40)
        assert C.family_nonempty("distribution", few_rows, max_tier=1)
        first = next(C.iter_bindings_for_family("distribution", few_rows, max_tier=1))
        assert first.chart_type == "range_bar"


class TestDeterministicBindings:
    """Building a figure from an intent takes the first binding this yields."""

    def test_first_binding_for_intent_one_is_a_bar(self, er):
        got = next(C.iter_bindings_for_family(
            "comparison", er, columns=("hospital", "wait_minutes"), aggregate="AVG"))
        assert got.chart_type == "bar"
        assert got.dims == ("hospital",) and got.measures == ("wait_minutes",)

    def test_grouped_bar_loses_because_the_intent_names_one_category_column(self, er):
        got = list(C.iter_bindings_for_family(
            "comparison", er, columns=("hospital", "wait_minutes"), aggregate="AVG"))
        assert {b.chart_type for b in got} == {"bar"}

    def test_iteration_order_is_stable_across_runs(self, er):
        a = [b for _, b in zip(range(20), C.iter_bindings("bar", er))]
        b = [b for _, b in zip(range(20), C.iter_bindings("bar", er))]
        assert a == b

    def test_every_yielded_binding_passes_check(self, er):
        for chart in ("bar", "grouped_bar", "line", "scatter", "pie", "heatmap", "box"):
            for _, b in zip(range(10), C.iter_bindings(chart, er)):
                assert C.check(b, er).ok, b

    def test_no_bindings_for_an_empty_family(self, er):
        assert next(C.iter_bindings("funnel", er), None) is None


class TestStaticGuarantees:
    def test_conditions_module_never_touches_data(self):
        src = Path(inspect.getfile(C)).read_text(encoding="utf-8")
        tree = ast.parse(src)
        imported = {
            n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
        } | {
            a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names
        }
        assert not {m for m in imported if m.split(".")[0] in {"pandas", "numpy"}}
        assert "FactTable" not in src, "deciding what is drawable must not touch data"

    def test_every_type_declares_value_keys_its_mark_shape_allows(self):
        from chartgen.registry.charts import CHARTS, SHAPE_VALUE_KEYS

        for c in CHARTS.values():
            assert c.value_keys, c.name
            for shape in c.mark:
                assert set(c.value_keys) <= SHAPE_VALUE_KEYS[shape], c.name

    def test_a_type_accepts_exactly_the_aggregates_its_shape_declares(self, er):
        """The shape decides the aggregate set, and `check` is what enforces it. A
        five-number shape takes FIVE_NUM and nothing else; a scalar shape takes the
        six that return one number and none of the three that name a shape."""
        from chartgen.registry.charts import CHARTS, SHAPE_AGGREGATES
        from chartgen.interfaces.table import Aggregate

        every = {a for group in SHAPE_AGGREGATES.values() for a in group}
        for name, spec in CHARTS.items():
            allowed = set(SHAPE_AGGREGATES[spec.shape])
            assert allowed, name
            legal = next((b for b in C.iter_bindings(name, er)), None)
            if legal is None:
                continue                    # this schema cannot draw the type at all
            for aggregate in every - allowed:
                verdict = C.check(replace(legal, aggregate=aggregate), er)
                assert not verdict, f"{name} accepted {aggregate}"
                assert spec.shape in verdict.reason or "aggregate" in verdict.reason.lower()

    def test_the_table_holds_seventeen_types_over_six_mark_shapes(self):
        from chartgen.registry.charts import CHARTS, FAMILIES

        assert len(CHARTS) == 17
        assert {c.family for c in CHARTS.values()} == {*FAMILIES, None}
        assert len({shape for c in CHARTS.values() for shape in c.mark}) == 6
        assert {c.tier for c in CHARTS.values()} == {1, 2}

    def test_every_cell_of_the_shape_product_is_either_filled_or_explained(self):
        """The table is the product of a projection shape and a mark shape. A gap
        is found by reading the grid, not by noticing it in someone else's data."""
        from chartgen.registry.charts import CHARTS, GRID, SHAPE_AGGREGATES, SHAPE_VALUE_KEYS

        cells = {(shape, mark) for shape in SHAPE_AGGREGATES for mark in SHAPE_VALUE_KEYS}
        assert set(GRID) == cells
        for cell, entry in GRID.items():
            assert isinstance(entry, (tuple, str)) and entry, cell
        filled = {t for e in GRID.values() if isinstance(e, tuple) for t in e}
        assert filled == set(CHARTS)

    def test_a_type_sits_in_the_cell_its_own_fields_put_it_in(self):
        from chartgen.registry.charts import CHARTS, GRID

        for c in CHARTS.values():
            entry = GRID[(c.shape, c.primary_mark)]
            assert isinstance(entry, tuple) and c.name in entry, c.name

    def test_every_family_has_at_least_one_type(self):
        from chartgen.registry.charts import FAMILIES, in_family

        for family in FAMILIES:
            assert in_family(family), family

    def test_no_two_types_share_all_four_condition_columns(self):
        """A type whose conditions, shape and values all match another is a style
        variant, not a separate type."""
        from dataclasses import astuple

        from chartgen.registry.charts import CHARTS

        seen = {}
        for c in CHARTS.values():
            fingerprint = astuple(c)[3:]     # everything but name, family and tier
            assert fingerprint not in seen, f"{c.name} matches {seen.get(fingerprint)} in every column"
            seen[fingerprint] = c.name
