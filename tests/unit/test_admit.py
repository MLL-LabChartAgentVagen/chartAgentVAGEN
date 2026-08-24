"""Admission: does a figure carry information, and does the batch already hold it."""

from chartgen.interfaces.figure import (
    Binding, Datum, FigureSpec, PanelSpec, Source, TextBlock, ViewSpec,
)
from chartgen.s02_figure import admit as A
from chartgen.s02_figure.project import project


def view(chart_type, values, *, keys=None, rows=40, **binding_kw):
    keys = keys or [(f"k{i}",) for i in range(len(values))]
    binding = Binding(chart_type, dims=("hospital",), measures=("wait_minutes",),
                      aggregate="AVG", **binding_kw)
    data = tuple(Datum(k, v if isinstance(v, dict) else {"value": float(v)}, rows)
                 for k, v in zip(keys, values))
    return ViewSpec(binding, data)


def figure(v, figure_id="f01", **kw):
    return FigureSpec(figure_id, "s", (PanelSpec("p0", (v,)),), **kw)


class TestDataConditions:
    def test_identical_heights_are_turned_away(self):
        v = view("bar", [10.0, 10.0, 10.0])
        assert not A.data_conditions(v)
        assert A.data_conditions(v).kind == "distinct"

    def test_a_flat_line_is_turned_away(self):
        v = view("bar", [10.0, 10.001, 10.002, 9.999])
        r = A.data_conditions(v)
        assert not r and r.kind in ("distinct", "variation")

    def test_how_many_distinct_heights_a_figure_has_to_have(self):
        """Half the marks, never fewer than two and never more than four. Both ends
        matter: without the floor a two-mark figure of one height passes, and without
        the ceiling a forty-mark figure would need twenty different heights, which
        turns away perfectly ordinary data."""
        from chartgen.s02_figure.admit import DISTINCT_CEILING

        assert A.data_conditions(view("bar", [1.0, 2.0, 1.0]))            # 2 of 3
        assert not A.data_conditions(view("bar", [1.0, 1.0]))             # 1 of 2
        assert A.data_conditions(view("bar", [1.0, 2.0]))                 # 2 of 2
        many = [float(i % DISTINCT_CEILING) for i in range(40)]
        assert A.data_conditions(view("bar", many)), "four heights are enough at forty"
        assert not A.data_conditions(view("bar", [float(i % 3) for i in range(40)]))

    def test_a_figure_with_real_spread_passes(self):
        assert A.data_conditions(view("bar", [42.3, 35.8, 28.1]))

    def test_cells_resting_on_too_few_rows_are_turned_away(self, er_table, er_schema):
        """Forty rows spread over a twelve-cell cross leave three rows a cell, which
        is a chart of noise however well the declarations screened it."""
        binding = Binding("grouped_bar", dims=("department", "severity"),
                          measures=("wait_minutes",), aggregate="AVG")
        thin = project(er_table.df.head(40), binding, er_schema)
        r = A.data_conditions(thin)
        assert not r and r.kind == "thin" and "rows per cell" in r.reason
        assert A.data_conditions(project(er_table.df, binding, er_schema))

    def test_a_funnel_needs_values_that_only_fall(self):
        v = view("funnel", [900.0, 720.0, 310.0, 64.0])
        assert A.data_conditions(v)
        assert not A.data_conditions(view("funnel", [900.0, 720.0, 800.0, 64.0]))

    def test_a_pie_needs_every_sector_above_the_floor(self):
        assert A.data_conditions(view("pie", [40.0, 30.0, 20.0, 10.0]))
        r = A.data_conditions(view("pie", [400.0, 300.0, 200.0, 1.0]))
        assert not r and r.kind == "share"

    def test_a_projection_with_no_marks_is_turned_away(self):
        assert not A.data_conditions(view("bar", []))

    def test_a_scatter_is_not_asked_about_rows_per_cell(self, er_table, er_schema):
        binding = Binding("scatter", measures=("wait_minutes", "satisfaction"), aggregate="NONE")
        assert A.data_conditions(project(er_table.df, binding, er_schema, seed=1))


class TestSignature:
    def test_two_views_with_the_same_keys_and_shape_share_a_signature(self):
        a = view("bar", [42.3, 35.8, 28.1])
        b = view("bar", [1.0, 2.0, 3.0])
        assert A.signature(a) == A.signature(b)

    def test_a_different_mark_shape_separates_them(self):
        a = view("bar", [42.3, 35.8, 28.1])
        b = view("pie", [42.3, 35.8, 28.1])
        assert A.signature(a) != A.signature(b)

    def test_different_keys_separate_them(self):
        a = view("bar", [42.3, 35.8, 28.1])
        b = view("bar", [42.3, 35.8, 28.1], keys=[("x",), ("y",), ("z",)])
        assert A.signature(a) != A.signature(b)

    def test_a_per_row_view_is_signed_by_its_columns_not_by_row_identifiers(
            self, er_table, er_schema):
        """Row identifiers describe which rows survived the thinning, not what the
        figure shows, so two scatters of the same pair of measures are the same
        figure and two of different pairs are not."""
        def scatter(*measures):
            return project(er_table.df, Binding("scatter", measures=measures, aggregate="NONE"),
                           er_schema, seed=1)

        assert A.signature(scatter("wait_minutes", "satisfaction")) == A.signature(
            scatter("wait_minutes", "satisfaction"))
        assert A.signature(scatter("wait_minutes", "satisfaction")) != A.signature(
            scatter("wait_minutes", "cost"))


class TestRedundancy:
    def test_the_second_figure_with_the_same_pair_is_rejected(self):
        batch = A.Batch()
        assert batch.admit(figure(view("bar", [42.3, 35.8, 28.1])))
        second = figure(view("bar", [980.0, 700.0, 610.0]), figure_id="f02")
        verdict = batch.admit(second)
        assert not verdict and verdict.kind == "redundant" and "f01" in verdict.reason

    def test_the_same_keys_in_another_shape_are_kept(self):
        batch = A.Batch()
        assert batch.admit(figure(view("bar", [42.3, 35.8, 28.1])))
        assert batch.admit(figure(view("pie", [42.3, 35.8, 28.1]), figure_id="f02"))

    def test_a_derived_figure_is_exempt_because_repeating_keys_is_its_point(self):
        batch = A.Batch()
        batch.admit(figure(view("bar", [42.3, 35.8, 28.1])))
        derived = figure(view("bar", [42.3, 35.8, 28.1]), figure_id="f02",
                         source=Source("panel", anchor_figure_id="f01"))
        assert batch.admit(derived)

    def test_two_figures_on_one_page_under_their_own_titles_are_exempt(self):
        """Side by side they carry the same category names, and only their titles
        tell their rows apart -- which is the layout the export has to handle."""
        batch = A.Batch()
        batch.admit(figure(view("bar", [42.3, 35.8, 28.1])))
        same_page = figure(view("bar", [10.0, 20.0, 30.0]), figure_id="f02", page_id="pg01",
                           texts=(TextBlock("title", "First half", "figure", "above"),))
        assert batch.admit(same_page)

    def test_a_page_without_a_title_gets_no_exemption(self):
        batch = A.Batch()
        batch.admit(figure(view("bar", [42.3, 35.8, 28.1])))
        assert not batch.admit(figure(view("bar", [1.0, 2.0, 3.0]), figure_id="f02",
                                      page_id="pg01"))

    def test_rejections_are_counted_by_kind(self):
        batch = A.Batch()
        batch.admit(figure(view("bar", [42.3, 35.8, 28.1])))
        batch.admit(figure(view("bar", [1.0, 2.0, 3.0]), figure_id="f02"))
        batch.admit(figure(view("bar", [5.0, 5.0, 5.0]), figure_id="f03"))
        assert batch.counts() == {"redundant": 1, "distinct": 1}
