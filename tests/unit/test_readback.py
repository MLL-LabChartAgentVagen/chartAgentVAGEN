"""Measuring values back out of pixels: one implementation, used at generation,
training and evaluation time."""

import numpy as np
import pytest

from chartgen.common import readback as rb
from chartgen.common.geometry import Box
from chartgen.interfaces.record import Axis, Mark, Panel

BLUE = (31, 78, 121)
BAR = Box(168, 196, 278, 520)
Y_AXIS = ((0.0, 60.0), (520.0, 60.0))
Y = Axis("y", (0.0, 60.0), (520.0, 60.0), column="wait_minutes")
X = Axis("x", (0.0, 5.0), (96.0, 860.0), column="satisfaction")
PANEL = Panel("p0", Box(96, 60, 860, 520), (X, Y), ("bar",))


def bar_mark(values, shape="rect", box=BAR):
    channel = {"sector": "angle", "cell": "color"}.get(shape, "length")
    return Mark("m0", "p0", ("Mercy General",), values, box, channel, mark_shape=shape)


@pytest.fixture
def canvas() -> np.ndarray:
    """A white canvas with one blue bar drawn on it."""
    img = np.full((600, 900, 3), 255, np.uint8)
    img[196:520, 168:278] = BLUE
    return img


class TestBoxContent:
    def test_a_box_over_the_bar_is_almost_entirely_that_colour(self, canvas):
        assert rb.color_fraction(canvas, BAR, BLUE) == pytest.approx(1.0, abs=0.01)

    def test_ink_fraction_sees_the_bar(self, canvas):
        assert rb.ink_fraction(canvas, BAR) == pytest.approx(1.0, abs=0.01)

    def test_an_empty_region_has_no_ink(self, canvas):
        assert rb.ink_fraction(canvas, Box(600, 60, 700, 150)) == 0.0

    def test_a_box_shifted_off_the_bar_fails_the_content_check(self, canvas):
        assert rb.box_has_content(canvas, BAR)
        assert not rb.box_has_content(canvas, Box(300, 196, 410, 520))

    def test_a_half_covering_box_is_reported_as_half(self, canvas):
        assert rb.color_fraction(canvas, Box(223, 196, 333, 520), BLUE) == pytest.approx(0.5, abs=0.01)

    def test_a_different_colour_does_not_count(self, canvas):
        assert rb.color_fraction(canvas, BAR, (200, 30, 30)) == 0.0

    def test_a_box_outside_the_image_is_clipped_not_crashed(self, canvas):
        assert rb.ink_fraction(canvas, Box(880, 580, 1200, 900)) == 0.0

    def test_a_box_fully_outside_the_image_has_no_content(self, canvas):
        assert not rb.box_has_content(canvas, Box(1000, 700, 1100, 800))


class TestValueFromBox:
    def test_the_top_edge_of_a_bar_reads_back_the_recorded_value(self):
        got = rb.value_from_box(BAR, Y_AXIS, anchor="top")
        assert got == pytest.approx(42.3, abs=0.3)

    def test_the_baseline_edge_reads_zero(self):
        assert rb.value_from_box(BAR, Y_AXIS, anchor="bottom") == pytest.approx(0.0, abs=0.1)

    def test_a_point_mark_reads_its_centre(self):
        dot = Box(400, 250, 408, 258)
        assert rb.value_from_box(dot, Y_AXIS, anchor="center_y") == pytest.approx(
            rb.value_from_box(Box(400, 254, 408, 254), Y_AXIS, anchor="top"))

    def test_horizontal_bars_read_their_right_edge(self):
        x_axis = ((0.0, 60.0), (96.0, 860.0))
        assert rb.value_from_box(Box(96, 100, 634, 140), x_axis, anchor="right") == pytest.approx(
            42.2, abs=0.3)


class TestAgreement:
    """How far a measured value may sit from a claimed one. The slack is absolute:
    what the pixels can resolve, not a fraction of the claim."""

    def test_inside_the_slack_passes(self):
        assert rb.value_agrees(42.26, 42.3, slack=0.13)

    def test_outside_the_slack_fails(self):
        assert not rb.value_agrees(39.0, 42.3, slack=0.13)

    def test_zero_slack_demands_an_exact_match(self):
        assert rb.value_agrees(42.3, 42.3, slack=0.0)
        assert not rb.value_agrees(42.31, 42.3, slack=0.0)

    def test_a_claimed_zero_still_has_a_floor_under_it(self):
        assert rb.value_agrees(0.0, 0.0, slack=0.0)
        assert not rb.value_agrees(5.0, 0.0, slack=0.0)


class TestBackground:
    def test_a_white_panel_reads_back_as_white(self, canvas):
        assert rb.background_of(canvas, Box(96, 60, 860, 520)) == (255, 255, 255)

    def test_a_tinted_panel_reads_back_as_its_tint(self):
        img = np.full((600, 900, 3), 255, np.uint8)
        img[60:520, 96:860] = (245, 247, 250)
        img[196:520, 168:278] = BLUE
        assert rb.background_of(img, Box(96, 60, 860, 520)) == (245, 247, 250)

    def test_ink_against_a_tint_would_otherwise_read_as_full(self):
        """Judging ink against white makes every box on a tinted panel look full,
        which turns the first self-check into a pass that never fails."""
        img = np.full((600, 900, 3), 255, np.uint8)
        img[60:520, 96:860] = (230, 234, 240)
        empty = Box(600, 200, 700, 300)
        assert rb.ink_fraction(img, empty) == pytest.approx(1.0)
        assert rb.ink_fraction(img, empty, background=(230, 234, 240)) == 0.0


class TestValueEdges:
    def test_a_y_axis_puts_the_larger_value_on_top(self):
        assert rb.value_edges(Y, "vertical") == ("bottom", "top")

    def test_an_x_axis_puts_the_larger_value_on_the_right(self):
        x = Axis("x", (0.0, 60.0), (96.0, 860.0))
        assert rb.value_edges(x, "horizontal") == ("left", "right")

    def test_an_inverted_axis_swaps_them(self):
        flipped = Axis("y", (0.0, 60.0), (60.0, 520.0))
        assert rb.value_edges(flipped, "vertical") == ("top", "bottom")


class TestGeometricAnchors:
    def test_a_plain_bar_anchors_its_value_to_the_edge_away_from_the_baseline(self):
        mark = bar_mark({"value": 42.3})
        assert rb.geometric_anchors(mark, Y) == {"value": ("value", "top")}

    def test_a_stacked_segment_anchors_both_cumulative_edges_and_not_its_value(self):
        mark = bar_mark({"value": 12.0, "cum_start": 20.0, "cum_end": 32.0})
        got = rb.geometric_anchors(mark, Y)
        assert got == {"cum_start": ("value", "bottom"), "cum_end": ("value", "top")}

    def test_a_histogram_bin_anchors_its_count_and_not_its_bin_edges(self):
        """Checking the bin edges would pin the bar width rather than the count."""
        mark = bar_mark({"count": 88.0, "bin_lo": 30.0, "bin_hi": 35.0})
        assert set(rb.geometric_anchors(mark, Y)) == {"count"}

    def test_a_scatter_point_reads_one_coordinate_off_each_axis(self):
        mark = bar_mark({"x": 38.0, "y": 3.4}, shape="point")
        assert rb.geometric_anchors(mark, Y) == {
            "y": ("value", "center_y"), "x": ("x", "center_x")}

    def test_a_sector_and_a_cell_have_no_geometry_to_measure(self):
        for shape in ("sector", "cell"):
            assert rb.geometric_anchors(bar_mark({"value": 1.0}, shape=shape), Y) == {}

    def test_a_printed_value_is_not_measured_off_geometry(self):
        mark = Mark("m0", "p0", ("a",), {"value": 1.0}, BAR, "printed", mark_shape="cell")
        assert rb.geometric_anchors(mark, Y) == {}


class TestCheckMark:
    """The same check with the claim coming from a model instead of the renderer."""

    def test_a_correct_mark_passes_both_geometric_checks(self, canvas):
        r = rb.check_mark(canvas, bar_mark({"value": 42.3}), PANEL, slack=0.3)
        assert r.has_content and r.value_agrees and r.ok
        assert r.measured["value"] == pytest.approx(42.3, abs=0.3)

    def test_an_invented_region_fails_the_first_check(self, canvas):
        mark = Mark("m0", "p0", ("a",), {"value": 42.3}, Box(600, 60, 700, 150), "length")
        r = rb.check_mark(canvas, mark, PANEL, slack=0.3)
        assert not r.has_content and not r.ok

    def test_a_wrong_value_on_a_real_region_fails_the_second(self, canvas):
        r = rb.check_mark(canvas, bar_mark({"value": 12.0}), PANEL, slack=0.3)
        assert r.has_content and not r.value_agrees and not r.ok

    def test_a_panel_without_the_named_axis_measures_nothing(self, canvas):
        bare = Panel("p0", Box(96, 60, 860, 520), (), ("bar",))
        r = rb.check_mark(canvas, bar_mark({"value": 42.3}), bare, slack=0.3)
        assert r.has_content and r.value_agrees is None and r.ok

    def test_a_mark_measured_against_the_right_hand_axis_uses_that_one(self, canvas):
        """A panel with two value axes means one pixel height stands for two values,
        so a mark that names the wrong axis reads back a different number."""
        right = Axis("y_right", (0.0, 600.0), (520.0, 60.0), column="cost")
        panel = Panel("p0", Box(96, 60, 860, 520), (Y, right), ("bar", "line"))
        mark = Mark("m0", "p0", ("a",), {"value": 423.0}, BAR, "length", value_axis="y_right")
        assert rb.check_mark(canvas, mark, panel, slack=3.0).value_agrees
        wrong = Mark("m0", "p0", ("a",), {"value": 423.0}, BAR, "length", value_axis="y")
        assert not rb.check_mark(canvas, wrong, panel, slack=3.0).value_agrees


class TestAWedgeIsMeasuredAroundItsCircle:
    """A sector used to come back as "cannot measure": the value is an angle and the
    check only knew how to read an edge of a box. That left the pie the one chart type
    whose recorded values nothing could confirm -- and grading an angle by what its
    radius pins it to is worth nothing while nothing can check the result.

    The measurement is the same kind the other shapes get: page geometry the panel
    wrote down, plus the ink in the image, and never the value being checked.
    """

    def pie(self, er_table, er_schema, tmp_path, **style):
        from dataclasses import replace

        from chartgen.interfaces.figure import Binding, FigureSpec, PanelSpec
        from chartgen.s02_figure.project import project
        from chartgen.s03_render.render import render
        from chartgen.s03_render.style import default

        view = project(er_table.df, Binding("pie", dims=("hospital",),
                                            measures=("wait_minutes",), aggregate="SUM",
                                            key_sources=("inline_label",)), er_schema)
        spec = FigureSpec("f01", "er", (PanelSpec("p0", (view,)),),
                          column_units={"wait_minutes": "minutes"})
        return render(spec, replace(default(), **style), tmp_path / "pie")

    def test_the_panel_records_the_circle_its_wedges_were_cut_from(self, er_table,
                                                                   er_schema, tmp_path):
        out = self.pie(er_table, er_schema, tmp_path)
        circle = out.panels[0].circle
        assert circle is not None
        cx, cy, inner, outer = circle
        assert inner == 0.0 and outer > 0.0
        assert out.panels[0].box.x0 < cx < out.panels[0].box.x1
        assert out.panels[0].radius == outer

    def test_a_bar_panel_records_no_circle(self, er_table, er_schema, tmp_path):
        from chartgen.interfaces.figure import Binding, FigureSpec, PanelSpec
        from chartgen.s02_figure.project import project
        from chartgen.s03_render.render import render
        from chartgen.s03_render.style import default

        view = project(er_table.df, Binding("bar", dims=("hospital",),
                                            measures=("wait_minutes",), aggregate="AVG",
                                            key_sources=("axis_tick",)), er_schema)
        out = render(FigureSpec("f01", "er", (PanelSpec("p0", (view,)),)),
                     default(), tmp_path / "bar")
        assert out.panels[0].circle is None
        assert out.panels[0].radius is None

    def test_every_wedge_reads_back_to_the_share_recorded_for_it(self, er_table,
                                                                 er_schema, tmp_path):
        from chartgen.common.readback import load_image, sector_share
        from chartgen.registry.channels import angular_epsilon

        out = self.pie(er_table, er_schema, tmp_path)
        img = load_image(out.image_path)
        panel = out.panels[0]
        allowed = angular_epsilon(panel.radius)
        for mark in out.marks:
            got = sector_share(img, mark, panel)
            assert got is not None, mark.key
            assert abs(got - mark.values["share"]) <= allowed, (mark.key, got)

    def test_a_ring_is_measured_the_same_way_a_filled_pie_is(self, er_table, er_schema,
                                                             tmp_path):
        """A ring and a pie hold the same value in the same angle, which is why the
        hole is a style value rather than a second chart type."""
        from chartgen.common.readback import load_image, sector_share
        from chartgen.registry.channels import angular_epsilon

        out = self.pie(er_table, er_schema, tmp_path, donut=True)
        assert out.panels[0].circle[2] > 0.0
        img = load_image(out.image_path)
        allowed = angular_epsilon(out.panels[0].radius)
        for mark in out.marks:
            got = sector_share(img, mark, out.panels[0])
            assert got is not None and abs(got - mark.values["share"]) <= allowed

    def test_a_share_claimed_wrong_is_caught(self, er_table, er_schema, tmp_path):
        from dataclasses import replace

        from chartgen.common.readback import check_mark, load_image

        out = self.pie(er_table, er_schema, tmp_path)
        img = load_image(out.image_path)
        mark = out.marks[0]
        assert check_mark(img, mark, out.panels[0]).value_agrees is True
        wrong = replace(mark, values={**mark.values, "share": mark.values["share"] * 1.5})
        assert check_mark(img, wrong, out.panels[0]).value_agrees is False

    def test_a_cell_still_comes_back_with_no_verdict(self, er_table, er_schema, tmp_path):
        """Colour is the one encoding with no closed form for its step, so a heatmap
        cell is still answered with "could not measure" rather than a verdict."""
        from chartgen.common.readback import load_image, check_mark
        from chartgen.interfaces.figure import Binding, FigureSpec, PanelSpec
        from chartgen.s02_figure.project import project
        from chartgen.s03_render.render import render
        from chartgen.s03_render.style import default

        view = project(er_table.df, Binding("heatmap", dims=("hospital", "severity"),
                                            measures=("wait_minutes",), aggregate="AVG",
                                            key_sources=("axis_tick", "axis_tick")),
                       er_schema)
        out = render(FigureSpec("f01", "er", (PanelSpec("p0", (view,)),)),
                     default(), tmp_path / "heat")
        img = load_image(out.image_path)
        assert check_mark(img, out.marks[0], out.panels[0]).value_agrees is None


class TestAMarkerFillsWhatItsOwnShapeCovers:
    """A point's box is a fixed square around where the marker was drawn, and that is
    deliberate: the value is read off the centre of the box, so the box may not depend
    on which marker the style picked. What then fills the square is a fact about the
    marker -- a filled circle most of it, a tick a line down the middle -- and asking a
    tick to fill as much as a bar does discards a figure that was drawn correctly.
    """

    def scatter(self, tmp_path, **style):
        import random
        from dataclasses import replace

        from chartgen.interfaces.figure import (
            Binding, Datum, FigureSpec, PanelSpec, ViewSpec,
        )
        from chartgen.s03_render.render import render
        from chartgen.s03_render.style import default

        rng = random.Random(7)
        binding = Binding("scatter", measures=("x", "y"), aggregate="NONE",
                          key_sources=("not_shown",))
        data = tuple(Datum((f"row_{i:05d}",), {"x": rng.uniform(1, 9),
                                               "y": rng.uniform(1, 9)}, rows=1)
                     for i in range(40))
        spec = FigureSpec("f01", "s", (PanelSpec("p0", (ViewSpec(binding, data),)),),
                          column_units={"x": "u", "y": "u"})
        return render(spec, replace(default(), **style), tmp_path / "scatter")

    def test_the_thinnest_marker_at_the_coarsest_dpi_still_passes(self, tmp_path):
        """The case that discarded a live figure: a tick has no line running through
        it on a scatter, and at seventy-two dots per inch it is a five-pixel stroke in
        an eighty-pixel square."""
        from chartgen.common.readback import check_mark, load_image

        out = self.scatter(tmp_path, series_marks=("tick",), dpi=72)
        img = load_image(out.image_path)
        for mark in out.marks:
            assert check_mark(img, mark, out.panels[0]).has_content, mark.key

    def test_a_box_moved_onto_plain_background_still_fails(self, tmp_path):
        """The threshold is lower for a point; it is not absent."""
        from dataclasses import replace

        from chartgen.common.geometry import Box
        from chartgen.common.readback import check_mark, load_image

        out = self.scatter(tmp_path, series_marks=("tick",), dpi=72)
        img = load_image(out.image_path)
        panel = out.panels[0]
        empty = Box(panel.box.x0 + 2, panel.box.y0 + 2, panel.box.x0 + 11,
                    panel.box.y0 + 11)
        moved = replace(out.marks[0], box=empty)
        assert not check_mark(img, moved, panel).has_content

    def test_a_bar_is_still_held_to_the_filled_shape_threshold(self, er_table,
                                                               er_schema, tmp_path):
        from chartgen.common.readback import MIN_CONTENT_FRACTION, MIN_POINT_FRACTION

        assert MIN_POINT_FRACTION < MIN_CONTENT_FRACTION


class TestAWedgePastHalfACircleCannotBeIdentified:
    """A run of pixels on the circle is matched back to a mark by the box it would
    have come out in. Past half a turn a wedge reaches every quadrant crossing, so
    its bounds are the whole circle's -- and so are its neighbours'. The box stops
    saying which wedge it belongs to, and a measurement matched on it is a guess.

    Found on a live batch: a wedge holding three fifths of a pie was measured at
    0.651, five points out and forty times the step its radius allows.
    """

    def dominated_pie(self, er_table, er_schema, tmp_path):
        from chartgen.interfaces.figure import Datum, ViewSpec
        from chartgen.interfaces.figure import Binding, FigureSpec, PanelSpec
        from chartgen.s03_render.render import render
        from chartgen.s03_render.style import default

        binding = Binding("pie", dims=("channel",), measures=("volume",),
                          aggregate="SUM", key_sources=("inline_label",))
        data = tuple(Datum((name,), {"value": share * 1000, "share": share}, rows=50)
                     for name, share in (("Electronic", 0.60), ("Paper", 0.25),
                                         ("Phone", 0.15)))
        spec = FigureSpec("f01", "s", (PanelSpec("p0", (ViewSpec(binding, data),)),),
                          column_units={"volume": "records"})
        return render(spec, default(), tmp_path / "dominated")

    def test_the_wedge_past_half_a_circle_comes_back_unmeasurable(
            self, er_table, er_schema, tmp_path):
        from chartgen.common.readback import load_image, sector_share

        out = self.dominated_pie(er_table, er_schema, tmp_path)
        img = load_image(out.image_path)
        big = next(m for m in out.marks if m.values["share"] > 0.5)
        assert sector_share(img, big, out.panels[0]) is None

    def test_its_neighbours_are_still_measured(self, er_table, er_schema, tmp_path):
        from chartgen.common.readback import load_image, sector_share
        from chartgen.registry.channels import angular_epsilon

        out = self.dominated_pie(er_table, er_schema, tmp_path)
        img = load_image(out.image_path)
        allowed = angular_epsilon(out.panels[0].radius)
        for mark in (m for m in out.marks if m.values["share"] <= 0.5):
            got = sector_share(img, mark, out.panels[0])
            assert got is not None, mark.key
            assert abs(got - mark.values["share"]) <= allowed, (mark.key, got)

    def test_the_check_says_it_could_not_measure_rather_than_wrong(
            self, er_table, er_schema, tmp_path):
        from chartgen.common.readback import check_mark, load_image

        out = self.dominated_pie(er_table, er_schema, tmp_path)
        img = load_image(out.image_path)
        big = next(m for m in out.marks if m.values["share"] > 0.5)
        result = check_mark(img, big, out.panels[0])
        assert result.has_content and result.value_agrees is None


class TestACircleThatChangesColourEverywhere:
    """The walk around the circle finds the wedge boundaries, then rotates itself to
    start off one so the stretch straddling the start is not cut in two. When every
    sample is a boundary there is no such starting point, and the rotation asked for
    the first one and got an empty array.

    A fine hatch and a colour ramp both do it: the colour differs from its neighbour
    at every angle, at every radius. Neither leaves an interior a wedge could be
    measured across, so the answer is the same one an unchanging circle gets -- no
    wedges -- and it has to be returned rather than raised.
    """

    def reads(self, colours):
        return [np.array(colours, dtype=np.uint8) for _ in range(rb.BOUNDARY_RADII)]

    def test_a_circle_whose_colour_changes_at_every_sample_yields_no_boundary(self):
        ramp = [(i % 256, (i * 7) % 256, (i * 13) % 256) for i in range(rb.ARC_SAMPLES)]
        assert rb._boundaries(self.reads(ramp)) == []

    def test_a_circle_of_one_colour_still_yields_no_boundary(self):
        flat = [(31, 78, 121)] * rb.ARC_SAMPLES
        assert rb._boundaries(self.reads(flat)) == []

    def test_two_wedges_are_still_found(self):
        half = rb.ARC_SAMPLES // 2
        split = [(31, 78, 121)] * half + [(200, 90, 40)] * (rb.ARC_SAMPLES - half)
        assert len(rb._boundaries(self.reads(split))) == 2
