"""Every chart type, drawn and then measured back off its own pixels.

The pipeline's correctness floor. Each type is projected out of the worked
scenarios, rendered, and then read back: is there something inside every recorded
box, and does the geometry of that box agree with the number recorded for it.
"""

import json
from dataclasses import replace
from pathlib import Path

import pytest

from chartgen.common import readback as rb
from chartgen.config import Config
from chartgen.interfaces.figure import Binding, FigureSpec, PanelSpec
from chartgen.registry.charts import CHARTS
from chartgen.s01_data.author import compose as compose_data
from chartgen.s02_figure.project import project
from chartgen.s03_render.draw import DRAWERS
from chartgen.s03_render.render import render
from chartgen.s03_render.style import default
from chartgen.s04_record.selfcheck import finish
from tools.gallery import CASES

SAMPLES = Path(__file__).resolve().parents[1] / "samples"

@pytest.fixture(scope="module")
def tables(er):
    payload = json.loads((SAMPLES / "funnel_scenario.json").read_text(encoding="utf-8"))
    funnel = compose_data(payload, scenario_id="funnel", seed=20260816,
                          config=Config.load())
    return {"er": er, "funnel": funnel}


@pytest.fixture(scope="module")
def drawn(tables, tmp_path_factory):
    """Every type, rendered once at the default style."""
    out = tmp_path_factory.mktemp("shapes")
    made = {}
    for name, (scenario, binding_kw) in CASES.items():
        table, schema = tables[scenario]
        binding = Binding(name, **binding_kw)
        from chartgen.s02_figure.keys import key_sources

        binding = replace(binding, key_sources=key_sources(binding))
        view = project(table.df, binding, schema, seed=5)
        spec = FigureSpec(name, scenario, (PanelSpec("p0", (view,)),),
                          column_units={c.name: c.unit for c in schema.measures},
                          column_names={c.name: c.name.replace("_", " ").title()
                                        for c in schema.columns})
        made[name] = (spec, render(spec, default(), out / name))
    return made


def _modal_colour(img, box) -> tuple[int, int, int]:
    """The colour a mark is mostly painted in, taken off the pixels it covers."""
    import numpy as np

    patch = img[int(box.y0) + 1:max(int(box.y1) - 1, int(box.y0) + 2),
                int(box.x0) + 1:max(int(box.x1) - 1, int(box.x0) + 2), :3]
    flat = patch.reshape(-1, 3)
    values, counts = np.unique(flat, axis=0, return_counts=True)
    return tuple(int(v) for v in values[counts.argmax()])


def _along(value_axis: str) -> tuple[str, str]:
    """The two box edges the value is read between."""
    return ("y0", "y1") if value_axis == "y" else ("x0", "x1")


def _across(value_axis: str) -> tuple[str, str]:
    """The two box edges that place a mark along the category axis."""
    return ("x0", "x1") if value_axis == "y" else ("y0", "y1")


def test_every_declared_type_has_a_drawing_branch():
    assert set(CHARTS) == set(DRAWERS)


def test_every_declared_type_is_exercised_here():
    assert set(CHARTS) == set(CASES)


@pytest.mark.parametrize("name", sorted(CASES))
class TestEveryType:
    def test_it_draws_at_least_one_mark(self, drawn, name):
        _, out = drawn[name]
        assert out.marks, name

    def test_the_marks_use_the_shape_and_channel_the_table_declares(self, drawn, name):
        _, out = drawn[name]
        spec = CHARTS[name]
        shapes = {m.mark_shape for m in out.marks}
        assert shapes <= set(spec.mark), (name, shapes)
        assert {m.channel for m in out.marks} <= set(spec.channel)

    def test_the_value_keys_are_the_ones_the_table_declares(self, drawn, name):
        """Exactly the declared keys, not a subset of them: a mark that dropped one
        is a mark whose value dictionary the record describes wrongly.

        The one exception is a row drawn beside the summary it fell outside of. It is
        its own mark of its own shape, and it carries the one number it is."""
        _, out = drawn[name]
        declared = set(CHARTS[name].value_keys)
        for mark in out.marks:
            if mark.mark_shape != CHARTS[name].primary_mark:
                assert set(mark.values) == {"value"}, (name, mark.values)
                continue
            assert set(mark.values) == declared, (name, mark.key, mark.values)

    def test_every_recorded_box_has_something_in_it(self, drawn, name):
        _, out = drawn[name]
        img = rb.load_image(out.image_path)
        empty = [m.key for m in out.marks
                 if not rb.check_mark(img, m, out.panels[0]).has_content]
        assert not empty, (name, empty[:5])

    def test_whatever_can_be_measured_back_agrees_with_the_record(self, drawn, name):
        """Each value key is judged against its own axis: a scatter point is measured
        against two, and one of them may be far finer than the other."""
        _, out = drawn[name]
        img = rb.load_image(out.image_path)
        panel = out.panels[0]
        wrong = [(m.key, r.measured, m.values) for m in out.marks
                 if (r := rb.check_mark(img, m, panel)).value_agrees is False]
        assert not wrong, (name, wrong[:3])

    def test_it_passes_its_own_self_checks(self, drawn, name):
        spec, out = drawn[name]
        record = finish(out, spec)
        assert record.selfcheck.box_content, (name, record.selfcheck.reasons)
        assert record.selfcheck.value_readback, (name, record.selfcheck.reasons)

    def test_every_page_element_is_a_box_on_the_page(self, drawn, name):
        """An element written past the edge of the image is text nobody can see, and
        a record that carries a box for it describes something that is not there."""
        _, out = drawn[name]
        w, h = out.image_size
        for element in out.elements:
            x0, y0, x1, y1 = element.box.as_tuple()
            assert -0.5 <= x0 and -0.5 <= y0, (name, element)
            assert x1 <= w + 0.5 and y1 <= h + 0.5, (name, element)
            assert element.box.area > 0, (name, element)

    def test_the_key_of_every_mark_says_where_each_segment_was_read_from(self, drawn, name):
        _, out = drawn[name]
        for mark in out.marks:
            assert len(mark.key) == len(mark.key_src), (name, mark.key, mark.key_src)


class TestAHeatmapKeepsItsTitleOutOfTheGrid:
    """Both of a heatmap's axes name categories, so its value title goes in the clear
    strip above the grid. The fitting pass moves titles that ended up somewhere they
    do not fit -- and it has to leave this one where the drawer put it, or the title
    is written across the cells."""

    def test_the_value_title_sits_above_the_first_row_of_cells(self, drawn):
        _, out = drawn["heatmap"]
        titles = [e for e in out.elements if e.category == "axis_title"]
        value = next(e for e in titles if "Wait" in e.text)
        top_cell = min(m.box.y0 for m in out.marks)
        assert value.box.y1 <= top_cell + 0.5, (value.box.as_tuple(), top_cell)
        assert value.box.x0 >= out.panels[0].box.x0 - 0.5

    def test_no_cell_is_written_over_by_it(self, drawn):
        _, out = drawn["heatmap"]
        value = next(e for e in out.elements
                     if e.category == "axis_title" and "Wait" in e.text)
        for mark in out.marks:
            assert value.box.clip_to(mark.box).area == 0, mark.key


class TestWhatEachShapeMeasures:
    def test_an_angle_and_a_colour_are_not_measured_off_geometry(self, drawn):
        for name in ("pie", "heatmap"):
            _, out = drawn[name]
            axis = rb.axis_of(out.panels[0], out.marks[0])
            assert rb.geometric_anchors(out.marks[0], axis) == {}

    def test_a_printed_value_is_not_measured_off_geometry_either(self, drawn):
        _, out = drawn["table_chart"]
        axis = rb.axis_of(out.panels[0], out.marks[0])
        assert rb.geometric_anchors(out.marks[0], axis) == {}
        assert all(m.labeled for m in out.marks)

    def test_a_box_plot_is_measured_between_its_quartiles(self, drawn):
        _, out = drawn["box"]
        mark = next(m for m in out.marks if m.mark_shape == "boxlike")
        axis = rb.axis_of(out.panels[0], mark)
        assert set(rb.geometric_anchors(mark, axis)) == {"q1", "q3"}

    def test_a_range_bar_is_measured_between_its_extremes(self, drawn):
        _, out = drawn["range_bar"]
        axis = rb.axis_of(out.panels[0], out.marks[0])
        assert set(rb.geometric_anchors(out.marks[0], axis)) == {"min", "max"}

    def test_a_stacked_segment_is_measured_between_its_running_totals(self, drawn):
        for name in ("stacked_bar", "area"):
            _, out = drawn[name]
            axis = rb.axis_of(out.panels[0], out.marks[0])
            assert set(rb.geometric_anchors(out.marks[0], axis)) == {"cum_start", "cum_end"}

    def test_stacked_segments_share_one_slot_and_chain_end_to_end(self, drawn):
        """Stacking and side-by-side placement are alternatives, not a pair. Given
        both, a category's segments each start one step across from the one below and
        the column reads as a staircase -- which is what a waterfall looks like, and a
        waterfall is a different type carrying a different claim about the numbers."""
        _, out = drawn["stacked_bar"]
        for category in {m.key[0] for m in out.marks}:
            column = [m for m in out.marks if m.key[0] == category]
            assert len(column) > 1, category
            across = _across(column[0].value_axis)
            assert len({tuple(getattr(m.box, e) for e in across) for m in column}) == 1
            along = sorted((min(getattr(m.box, e) for e in _along(m.value_axis)),
                            max(getattr(m.box, e) for e in _along(m.value_axis)))
                           for m in column)
            for (_, end), (start, _) in zip(along, along[1:]):
                assert start == pytest.approx(end, abs=1.0), category

    def test_a_grouped_bar_puts_its_series_side_by_side(self, drawn):
        """The other half of the same decision: without stacking, a second key column
        is shown by position across the category, so the slots must not coincide."""
        _, out = drawn["grouped_bar"]
        category = out.marks[0].key[0]
        column = [m for m in out.marks if m.key[0] == category]
        across = _across(column[0].value_axis)
        assert len({tuple(getattr(m.box, e) for e in across) for m in column}) == len(column)

    def test_a_scatter_point_is_measured_on_both_axes(self, drawn):
        _, out = drawn["scatter"]
        axis = rb.axis_of(out.panels[0], out.marks[0])
        assert set(rb.geometric_anchors(out.marks[0], axis)) == {"x", "y"}

    def test_a_histogram_is_measured_on_its_count_and_not_on_its_bin_edges(self, drawn):
        _, out = drawn["histogram"]
        axis = rb.axis_of(out.panels[0], out.marks[0])
        assert set(rb.geometric_anchors(out.marks[0], axis)) == {"count"}

    def test_a_box_plot_draws_its_outliers_as_their_own_marks(self, drawn):
        _, out = drawn["box"]
        extra = [m for m in out.marks if m.mark_shape == "point"]
        assert extra and all(len(m.key) == 2 and set(m.values) == {"value"} for m in extra)
        assert all(m.key_src[-1] == "not_shown" for m in extra)


class TestAHistogramIsDrawnInOneInk:
    """A bin is named by where it sits on the value axis and by nothing else: its key
    is shown nowhere and no legend is drawn. A colour per bin therefore encodes
    nothing, and the palettes hold six entries against a type that allows thirty
    bins -- so two bins far apart on the axis end up in the same ink."""

    def test_every_bin_takes_the_same_colour(self, drawn, tmp_path):
        spec, _ = drawn["histogram"]
        out = render(spec, replace(default(), value_labels="none"), tmp_path)
        img = rb.load_image(out.image_path)
        tall = [m for m in out.marks if m.box.height > 6]
        inks = {_modal_colour(img, m.box) for m in tall}
        assert len(tall) > 6 and len(inks) == 1, inks

    def test_no_bin_carries_a_key_anything_could_read(self, drawn):
        """The other half of the same fact, stated on the record: nothing names a bin,
        so nothing about a bin can be encoded in its colour."""
        _, out = drawn["histogram"]
        assert all(m.key_src == ("not_shown",) for m in out.marks)
        assert out.legend == ()


class TestAChartWithNothingToMeasureDrawsNoScale:
    """A pie carries its value in an angle and a table chart prints it, so neither has
    anything to measure along an axis. Emptying the tick list is not enough on its own:
    a log axis keeps a minor locator, and that one goes on drawing a ladder of ticks
    and labels beside the plot after the major ticks are gone. Whether the axis is
    logarithmic is a style dimension, so the sampler decides which figures it happens
    to -- which is why this is checked on the pixels rather than left to the branch."""

    @pytest.mark.parametrize("name", ["pie", "table_chart"])
    def test_a_log_axis_leaves_the_picture_unchanged(self, tables, tmp_path, name):
        """The strongest form of the claim: if nothing is measured along the axis,
        asking for a logarithmic one may not put a single pixel anywhere."""
        from chartgen.s02_figure.keys import key_sources

        scenario, binding_kw = CASES[name]
        table, schema = tables[scenario]
        binding = replace(Binding(name, **binding_kw),
                          key_sources=key_sources(Binding(name, **binding_kw)))
        view = project(table.df, binding, schema, seed=5)
        spec = FigureSpec(name, scenario, (PanelSpec("p0", (view,)),),
                          column_units={c.name: c.unit for c in schema.measures})
        plain = render(spec, default(), tmp_path / f"{name}_plain")
        logged = render(spec, replace(default(), log_scale=True), tmp_path / f"{name}_log")
        assert (rb.load_image(plain.image_path) == rb.load_image(logged.image_path)).all()


class TestReadability:
    def test_an_angle_keeps_no_value_target_unless_it_is_printed(self, drawn):
        spec, out = drawn["pie"]
        assert not any(finish(out, spec).marks[i].readable for i in range(len(out.marks)))

    def test_a_printed_pie_keeps_all_of_them(self, drawn, tmp_path):
        spec, _ = drawn["pie"]
        out = render(spec, replace(default(), value_labels="all"), tmp_path)
        assert all(m.readable for m in finish(out, spec).marks)

    def test_a_colour_keeps_no_value_target(self, drawn):
        spec, out = drawn["heatmap"]
        assert not any(m.readable for m in finish(out, spec).marks)
        assert all(m.box.area > 0 for m in out.marks)

    def test_a_printed_table_is_exact(self, drawn):
        spec, out = drawn["table_chart"]
        record = finish(out, spec)
        assert all(m.readable for m in record.marks)
        from chartgen.registry.channels import tolerance

        assert all(tolerance(m.labeled) == 0.0 for m in record.marks)

    def test_a_measurable_type_keeps_most_of_its_value_targets(self, drawn):
        for name in ("bar", "line", "category_line"):
            spec, out = drawn[name]
            record = finish(out, spec)
            kept = sum(1 for m in record.marks if m.readable)
            assert kept >= 0.8 * len(record.marks), name

    def test_a_short_mark_on_a_tall_axis_loses_its_value_target(self, drawn):
        """One percent of a bar a quarter of the axis high is about one pixel. Marks
        like that drop out of the value targets and stay in the localisation ones,
        which is why the rate is reported per chart type rather than aimed at."""
        spec, out = drawn["grouped_bar"]
        record = finish(out, spec)
        lo, hi = record.panels[0].axis("y").value_range
        per_pixel = (hi - lo) / abs(record.panels[0].axis("y").pixel_range[1] -
                                    record.panels[0].axis("y").pixel_range[0])
        for mark in record.marks:
            expected = mark.values["value"] * 0.01 / per_pixel >= 2.0
            assert bool(mark.readable) is expected, (mark.key, mark.values)


#: Style combinations that have caught a shape out. A dimension on its own is
#: covered by the meta-test over `STYLE_DOMAINS`; these are the pairs, which no
#: per-dimension sweep reaches.
AWKWARD_STYLES: tuple[tuple[str, dict], ...] = (
    ("no edge with a shadow", {"edge_width": 0.0, "shadow": True}),
    ("printed on a tinted panel", {"value_labels": "all", "panel_bg": "tint"}),
    ("turned with rotated labels", {"orientation": "horizontal", "label_rotation": 45.0}),
    ("grey with a pattern", {"palette": "grayscale", "hatch": "//", "pseudo_3d": True}),
    ("labels outside on a log axis", {"value_labels": "outside_leader", "log_scale": True}),
    ("wrapped ticks with two levels", {"category_label_wrap": True,
                                       "two_level_x_labels": True}),
    ("named beside the line, legend inside", {"series_name_beside_line": True,
                                              "legend_placement": "inside"}),
    ("diamonds without a baseline", {"series_marks": ("diamond",), "zero_baseline": False}),
)


@pytest.mark.parametrize("name", sorted(CASES))
@pytest.mark.parametrize("described,overrides", AWKWARD_STYLES,
                         ids=[d for d, _ in AWKWARD_STYLES])
def test_every_type_survives_an_awkward_style(drawn, tmp_path, name, described, overrides):
    """Style never changes an answer, but it does reach every drawing branch, and a
    branch that only fails in combination fails on real data and nowhere else."""
    spec, base = drawn[name]
    out = render(spec, replace(default(), **overrides), tmp_path)
    assert len(out.marks) == len(base.marks), (name, described)
    assert [m.values for m in out.marks] == [m.values for m in base.marks]


class TestASummaryMarkIsAskedAboutANumberItsBoxCarries:
    """Five numbers and none of them is "the" value. The two the box runs between are
    the two a reader can take off the value axis; the median sits somewhere inside it
    with nothing on the page fixing it, so a value target asking for the median is one
    the reward path cannot check."""

    def test_the_key_asked_about_is_one_the_readback_has_an_anchor_for(self, drawn):
        from chartgen.common import readback as rb
        from chartgen.s04_record.readable import target_key

        for name in ("box", "error_bar", "windsock", "range_bar"):
            _, out = drawn[name]
            axis = rb.axis_of(out.panels[0], out.marks[0])
            for mark in out.marks:
                if len(mark.values) < 3:
                    continue          # a box plot's outliers carry one number
                anchors = rb.geometric_anchors(mark, axis)
                assert target_key(mark) in anchors, (name, mark.values, anchors)

    def test_a_box_plot_is_asked_about_its_upper_quartile(self, drawn):
        from chartgen.s04_record.readable import target_key

        _, out = drawn["box"]
        mark = next(m for m in out.marks if m.mark_shape == "boxlike")
        assert target_key(mark) == "q3"

    def test_an_error_bar_is_asked_about_its_maximum(self, drawn):
        from chartgen.s04_record.readable import target_key

        _, out = drawn["error_bar"]
        assert target_key(out.marks[0]) == "max"

    def test_a_plain_mark_is_still_asked_about_its_own_value(self, drawn):
        from chartgen.s04_record.readable import target_key

        for name, key in (("bar", "value"), ("histogram", "count"), ("scatter", "y"),
                          ("line", "value"), ("heatmap", "value")):
            _, out = drawn[name]
            assert target_key(out.marks[0]) == key, name
