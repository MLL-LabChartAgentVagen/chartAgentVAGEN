"""Deriving a second view from one that was already accepted."""

import pytest

from chartgen.interfaces.figure import Binding
from chartgen.s02_figure import panel as PN
from chartgen.s02_figure.project import project


@pytest.fixture
def ctx(er_table, er_schema):
    return PN.Context(er_table.df, er_schema, seed=11)


@pytest.fixture
def anchor(er_table, er_schema):
    binding = Binding("bar", dims=("hospital",), measures=("wait_minutes",),
                      aggregate="AVG", key_sources=("axis_tick",))
    return project(er_table.df, binding, er_schema)


@pytest.fixture
def trend(er_table, er_schema):
    binding = Binding("line", time="visit_date", measures=("wait_minutes",),
                      aggregate="AVG", resample="monthly", key_sources=("axis_tick",))
    return project(er_table.df, binding, er_schema)


class TestSmallMultiples:
    def test_one_panel_per_value_with_the_same_view_inside(self, anchor, ctx):
        d = PN.small_multiples(anchor, ctx)
        assert d.relation == "small_multiples" and 2 <= len(d.panels) <= PN.MAX_PANELS
        assert len({p.view.binding for p in d.panels}) == 1
        assert {p.view.binding.dims[0] for p in d.panels} == {"hospital"}

    def test_every_panel_is_titled_with_the_value_it_holds(self, anchor, ctx):
        d = PN.small_multiples(anchor, ctx)
        titles = [p.texts[0].text for p in d.panels]
        assert len(set(titles)) == len(titles) and all(titles)

    def test_that_title_is_the_first_segment_of_every_key_under_it(self, anchor, ctx):
        """Four panels of the same three centres otherwise give one key three
        answers, and nothing in the record says which panel any of them came from."""
        d = PN.small_multiples(anchor, ctx)
        for panel in d.panels:
            assert panel.view.key_prefix == (panel.texts[0].text,)
            assert panel.view.prefix_source == ("panel_title",)
            assert all(k[0] == panel.texts[0].text for k in panel.view.keys)
        every = [k for p in d.panels for k in p.view.keys]
        assert len(set(every)) == len(every)

    def test_a_panel_title_is_not_a_series(self, anchor, ctx):
        """A prefix read off a legend names a series, and colour and slot follow it.
        Read off a panel title it names the plotting area, and every panel under it is
        drawn the same way as its neighbours."""
        d = PN.small_multiples(anchor, ctx)
        assert not any(p.view.prefix_names_a_series for p in d.panels)

    def test_it_deepens_the_view_so_that_one_legend_covers_every_panel(self, anchor, ctx):
        """Repeating a one-column view produces no legend at all: its names are on
        the axis. Deepened by a column every panel shares, the same repetition
        produces the one thing the legend-binding target can come from."""
        d = PN.small_multiples(anchor, ctx)
        assert all(p.view.binding.n_group == 2 for p in d.panels)
        assert d.sharing.share_legend
        assert len({PN.series_column(p.view.binding) for p in d.panels}) == 1
        assert d.sharing.series_column == PN.series_column(d.panels[0].view.binding)

    def test_it_falls_back_to_plain_repetition_when_it_cannot_deepen(
            self, er_table, er_schema):
        from chartgen.interfaces.figure import Binding
        from chartgen.s02_figure.project import project

        # No type in the distribution family takes two category columns, so there is
        # nothing to deepen this into and the panels stay as they are.
        narrow = PN.Context(er_table.df, er_schema, seed=1)
        binding = Binding("range_bar", dims=("hospital",), measures=("wait_minutes",),
                          aggregate="FIVE_NUM", key_sources=("axis_tick",))
        view = project(er_table.df, binding, er_schema)
        d = PN.small_multiples(view, narrow)
        assert d is not None and all(p.view.binding.n_group == 1 for p in d.panels)
        assert not d.sharing.share_legend


class TestFacet:
    def test_the_metric_stays_and_the_grouping_column_changes(self, anchor, ctx):
        d = PN.facet(anchor, ctx)
        assert [p.view.binding.dims[0] for p in d.panels][0] == "hospital"
        assert len({p.view.binding.dims[0] for p in d.panels}) == len(d.panels)
        assert {p.view.binding.aggregate for p in d.panels} == {"AVG"}

    def test_it_never_faces_a_column_onto_a_child_of_one_it_already_uses(self, anchor, ctx):
        d = PN.facet(anchor, ctx)
        assert "department" not in {p.view.binding.dims[0] for p in d.panels}

    def test_panels_stop_at_the_limit(self, anchor, ctx):
        assert len(PN.facet(anchor, ctx).panels) <= PN.MAX_PANELS


class TestDrilldown:
    def test_a_child_of_the_anchor_column_is_preferred(self, anchor, ctx):
        d = PN.drilldown(anchor, ctx)
        assert d.panels[1].view.binding.dims == ("hospital", "department")

    def test_the_deeper_panel_colours_by_the_column_it_added(self, anchor, ctx):
        d = PN.drilldown(anchor, ctx)
        assert d.panels[1].view.binding.colour_group == "department"
        assert d.panels[1].view.binding.key_sources == ("axis_tick", "legend")


class TestTimeSplit:
    def test_the_same_view_over_two_windows(self, anchor, ctx):
        d = PN.time_split(anchor, ctx)
        assert len(d.panels) == 2
        assert d.panels[0].view.keys == d.panels[1].view.keys
        assert d.panels[0].view.row_filter != d.panels[1].view.row_filter

    def test_the_windows_do_not_overlap_and_cover_the_span(self, anchor, ctx):
        a, b = (p.view.row_filter for p in PN.time_split(anchor, ctx).panels)
        assert a.end < b.start

    def test_together_they_hold_every_row_the_anchor_had(self, anchor, ctx):
        d = PN.time_split(anchor, ctx)
        split = sum(x.rows for p in d.panels for x in p.view.data)
        assert split == sum(x.rows for x in anchor.data)

    def test_each_panel_is_titled_with_its_window(self, anchor, ctx):
        d = PN.time_split(anchor, ctx)
        assert [p.texts[0].text for p in d.panels] == [p.view.row_filter.label
                                                       for p in d.panels]


class TestDualMetric:
    def test_the_grouping_stays_and_the_measure_moves_on(self, anchor, ctx):
        d = PN.dual_metric(anchor, ctx)
        assert d.panels[1].view.binding.dims == ("hospital",)
        assert d.panels[1].view.binding.measures != anchor.binding.measures

    def test_the_dependency_edge_is_preferred_over_the_column_order(self, er_schema):
        binding = Binding("bar", dims=("hospital",), measures=("wait_minutes",), aggregate="AVG")
        assert PN.next_measure(binding, er_schema) == "cost"

    def test_the_aggregate_follows_additivity(self, er_schema):
        assert PN.aggregate_for("cost", er_schema) == "SUM"
        assert PN.aggregate_for("satisfaction", er_schema) == "AVG"


class TestPartWhole:
    def test_a_comparison_becomes_a_composition(self, anchor, ctx):
        d = PN.part_whole(anchor, ctx)
        from chartgen.registry.charts import CHARTS
        assert CHARTS[d.panels[1].view.binding.chart_type].family == "composition"
        assert d.sharing.share_legend

    def test_it_declines_when_the_anchor_is_not_a_comparison(self, trend, ctx):
        assert PN.part_whole(trend, ctx) is None


class TestOverlay:
    def test_two_measures_land_in_one_plotting_area_with_different_shapes(self, anchor, ctx):
        from chartgen.registry.charts import CHARTS
        d = PN.overlay_metric(anchor, ctx)
        assert d.layout == "overlay" and len(d.panels) == 1
        base, over = d.panels[0].views
        assert {CHARTS[base.binding.chart_type].primary_mark,
                CHARTS[over.binding.chart_type].primary_mark} == {"rect", "point"}

    def test_each_overlaid_series_names_itself_in_its_key(self, anchor, ctx):
        """Two series group by the same column, so without a name of their own their
        marks would land on the same panel and key with different numbers."""
        base, over = PN.overlay_metric(anchor, ctx).panels[0].views
        assert base.key_prefix and over.key_prefix and base.key_prefix != over.key_prefix
        assert base.keys.isdisjoint(over.keys)
        assert base.prefix_source == ("legend",)

    def test_one_measure_over_two_windows_lands_in_one_plotting_area(self, anchor, ctx):
        d = PN.overlay_slice(anchor, ctx)
        base, over = d.panels[0].views
        assert base.binding.measures == over.binding.measures
        assert base.row_filter != over.row_filter

    def test_a_value_and_its_spread_use_different_shapes(self, anchor, ctx):
        from chartgen.registry.charts import CHARTS
        d = PN.overlay_range(anchor, ctx)
        base, over = d.panels[0].views
        assert over.binding.chart_type == "error_bar"
        assert CHARTS[base.binding.chart_type].primary_mark != CHARTS[
            over.binding.chart_type].primary_mark

    def test_a_spread_over_time_is_a_band_instead(self, trend, ctx):
        d = PN.overlay_range(trend, ctx)
        assert d is not None and d.panels[0].views[1].binding.chart_type == "windsock"


class TestAxisCount:
    def test_two_units_always_need_two_value_axes(self, anchor, ctx):
        d = PN.overlay_metric(anchor, ctx)
        base, over = d.panels[0].views
        assert PN.needs_two_axes(base, over, ctx.schema)
        assert not d.sharing.share_y

    def test_one_unit_at_a_similar_scale_shares_one_axis(self, anchor, ctx):
        d = PN.overlay_slice(anchor, ctx)
        base, over = d.panels[0].views
        assert not PN.needs_two_axes(base, over, ctx.schema)
        assert d.sharing.share_y

    def test_one_unit_twenty_times_apart_still_needs_two(self, anchor, ctx, er_schema):
        from dataclasses import replace
        big = replace(anchor, data=tuple(
            replace(d, values={"value": d.values["value"] * 100}) for d in anchor.data))
        assert PN.needs_two_axes(anchor, big, er_schema)


class TestRejection:
    def test_why_a_candidate_was_turned_away_is_counted(self, er_table, er_schema):
        ctx = PN.Context(er_table.df, er_schema, seed=1)
        assert ctx.build(Binding("bar", dims=("hospital", "department"),
                                 measures=("wait_minutes",), aggregate="AVG")) is None
        assert ctx.rejected["conditions"] == 1


class TestABarWithItsErrorBars:
    """`error_bar` shares four condition columns and a value dictionary with `box`,
    and keeps its own row because the mark shape differs -- which is half of what
    makes a figure a distinct sample. What it did not have was the layout it is
    usually seen in: the same five numbers drawn over the bar that summarises them."""

    def test_the_partner_of_a_bar_with_no_time_column_is_an_error_bar(self, anchor, ctx):
        d = PN.overlay_range(anchor, ctx)
        assert d is not None and d.layout == "overlay"
        types = [v.binding.chart_type for v in d.panels[0].views]
        assert types == ["bar", "error_bar"]

    def test_the_two_views_do_not_share_a_mark_shape(self, anchor, ctx):
        """Two overlaid views with one mark shape put their boxes on top of each
        other, and nothing in the record can tell them apart."""
        from chartgen.registry.charts import CHARTS

        d = PN.overlay_range(anchor, ctx)
        marks = {CHARTS[v.binding.chart_type].primary_mark for v in d.panels[0].views}
        assert len(marks) == 2, marks

    def test_over_a_time_column_the_partner_is_a_band_instead(self, trend, ctx):
        d = PN.overlay_range(trend, ctx)
        assert d is not None
        assert [v.binding.chart_type for v in d.panels[0].views] == ["line", "windsock"]

    def test_the_spread_view_carries_the_five_numbers(self, anchor, ctx):
        d = PN.overlay_range(anchor, ctx)
        spread = d.panels[0].views[1]
        assert set(spread.data[0].values) == {"min", "q1", "median", "q3", "max"}

    def test_the_budget_leaves_room_for_it(self):
        """It is the last of the three overlay relations in declared order, so a
        budget of two never reached it -- five of six scenarios logged exactly that."""
        from chartgen.config import Config

        assert int(Config.load().get("figure.max_overlays")) >= len(PN.OVERLAY_RELATIONS)
