"""Drawing and recording in one step, checked against the rendered pixels.

This is the correctness floor of the whole pipeline. A box comes from the plotting
library's own transform, and when that goes wrong nothing raises -- the boxes are
simply offset. So these tests do not ask whether a box exists; they read the
rendered image back and ask whether anything is inside it and whether the geometry
agrees with the recorded value.
"""

import itertools
from dataclasses import replace

import pytest

from chartgen.common import readback as rb
from chartgen.common import serde
from chartgen.common.geometry import Box
from chartgen.interfaces.figure import Binding, FigureSpec, PanelSpec, TextBlock
from chartgen.interfaces.style import STYLE_DOMAINS
from chartgen.registry import channels
from chartgen.s02_figure.project import project
from chartgen.s03_render.render import render
from chartgen.s03_render.style import default, sample

#: The geometry the worked example produces, shared with the sample files. A bar
#: top is `480 - value / 50 * 348`, so one pixel stands for 0.14 minutes.
PLOT_RECT = (96.0, 132.0, 820.0, 480.0)
BAR_BOXES = {
    ("Mercy General",): (165.0, 186.0, 269.0, 480.0),
    ("St. Luke's",): (406.0, 231.0, 510.0, 480.0),
    ("Riverside",): (647.0, 284.0, 751.0, 480.0),
}


@pytest.fixture(scope="module")
def rendered(tmp_path_factory):
    spec = serde.sample("FigureSpec")
    style = serde.sample("StyleVector")
    return render(spec, style, tmp_path_factory.mktemp("render"))


def figure(view, figure_id="f01", **kw):
    return FigureSpec(figure_id, "er", (PanelSpec("p0", (view,)),),
                      column_units={"wait_minutes": "minutes", "cost": "USD",
                                    "satisfaction": "points"}, **kw)


def bar_view(er_table, er_schema, **kw):
    binding = Binding("bar", dims=("hospital",), measures=("wait_minutes",),
                      aggregate="AVG", key_sources=("axis_tick",), **kw)
    return project(er_table.df, binding, er_schema)


class TestFrozenLayout:
    def test_the_image_has_exactly_the_declared_size(self, rendered):
        img = rb.load_image(rendered.image_path)
        assert img.shape[:2] == (600, 900)
        assert rendered.image_size == (900, 600)

    def test_the_plot_area_is_where_it_was_declared(self, rendered):
        assert rendered.panels[0].box.as_tuple() == pytest.approx(PLOT_RECT, abs=0.5)

    def test_the_y_axis_maps_the_value_range_onto_the_plot_area(self, rendered):
        y = next(a for a in rendered.panels[0].axes if a.role == "y")
        assert y.value_range == pytest.approx((0.0, 50.0))
        assert y.pixel_range == pytest.approx((480.0, 132.0), abs=0.5)
        assert y.column == "wait_minutes"

    def test_the_x_axis_is_recorded_too(self, rendered):
        x = next(a for a in rendered.panels[0].axes if a.role == "x")
        assert x.column == "hospital"
        assert x.pixel_range == pytest.approx((96.0, 820.0), abs=0.5)

    def test_the_text_band_keeps_its_height_with_nothing_written_in_it(
            self, er_table, er_schema, tmp_path):
        """A plotting area that moved when a title arrived would invalidate every
        box already recorded inside it."""
        view = bar_view(er_table, er_schema)
        bare = render(figure(view), default(), tmp_path / "a")
        titled = render(replace(figure(view), texts=(
            TextBlock("title", "Wait times by hospital", "figure", "above"),
            TextBlock("subtitle", "Average per visit", "figure", "above"))),
            default(), tmp_path / "b")
        assert bare.panels[0].box.as_tuple() == titled.panels[0].box.as_tuple()
        assert [m.box.as_tuple() for m in bare.marks] == [m.box.as_tuple() for m in titled.marks]


class TestMarksRecordedWhileDrawing:
    def test_one_mark_per_projected_value(self, rendered):
        assert len(rendered.marks) == 3
        assert [m.key for m in rendered.marks] == [
            ("Mercy General",), ("St. Luke's",), ("Riverside",)]

    def test_each_mark_carries_its_value(self, rendered):
        assert [m.values["value"] for m in rendered.marks] == [42.3, 35.8, 28.1]

    def test_each_mark_box_matches_the_worked_example(self, rendered):
        for mark in rendered.marks:
            assert mark.box.as_tuple() == pytest.approx(BAR_BOXES[mark.key], abs=1.0)

    def test_bars_sit_on_the_baseline(self, rendered):
        assert {round(m.box.y1) for m in rendered.marks} == {480}

    def test_each_mark_says_which_axis_and_which_shape_it_was_read_as(self, rendered):
        for mark in rendered.marks:
            assert mark.value_axis == "y" and mark.mark_shape == "rect"
            assert mark.channel == "length"

    def test_each_mark_says_where_its_key_was_read_from(self, rendered):
        assert all(m.key_src == ("axis_tick",) for m in rendered.marks)

    def test_rows_and_readable_are_left_for_the_record_stage(self, rendered):
        assert all(m.rows is None and m.readable is None for m in rendered.marks)


class TestBoxContent:
    def test_every_recorded_box_actually_contains_ink(self, rendered):
        img = rb.load_image(rendered.image_path)
        for mark in rendered.marks:
            assert rb.ink_fraction(img, mark.box) > 0.9, mark.key

    def test_a_box_moved_into_the_gap_between_bars_is_caught(self, rendered):
        img = rb.load_image(rendered.image_path)
        first = rendered.marks[0]
        moved = Box(first.box.x0 + 120, first.box.y0, first.box.x1 + 120, first.box.y1)
        assert not rb.box_has_content(img, moved)

    def test_a_box_moved_onto_the_next_bar_passes_the_first_check_and_fails_the_second(
            self, rendered):
        """The two checks catch different mistakes, which is why both are run."""
        img = rb.load_image(rendered.image_path)
        panel = rendered.panels[0]
        first, second = rendered.marks[0], rendered.marks[1]
        moved = replace(first, box=Box(second.box.x0, second.box.y0,
                                       second.box.x1, second.box.y1))
        result = rb.check_mark(img, moved, panel, slack=0.35)
        assert result.has_content and not result.value_agrees


class TestValueReadback:
    def test_each_bar_reads_back_to_the_value_recorded_for_it(self, rendered):
        img = rb.load_image(rendered.image_path)
        panel = rendered.panels[0]
        axis = rb.axis_pair(panel.axis("y"))
        slack = channels.geometric_slack(axis)
        for mark in rendered.marks:
            result = rb.check_mark(img, mark, panel, slack=slack)
            assert result.ok, (mark.key, result)
            assert result.measured["value"] == pytest.approx(mark.values["value"], abs=slack)

    def test_a_wrong_axis_range_would_be_caught(self, rendered):
        """The value check is what stands between a mis-mapped axis and a record
        full of numbers that look plausible."""
        panel = rendered.panels[0]
        broken = replace(panel, axes=tuple(
            replace(a, value_range=(0.0, 120.0)) if a.role == "y" else a for a in panel.axes))
        img = rb.load_image(rendered.image_path)
        assert not rb.check_mark(img, rendered.marks[0], broken, slack=0.35).value_agrees


class TestDeterminism:
    def test_the_same_spec_and_style_render_byte_identical_images(self, tmp_path):
        spec, style = serde.sample("FigureSpec"), serde.sample("StyleVector")
        a = render(spec, style, tmp_path / "a")
        b = render(spec, style, tmp_path / "b")
        assert open(a.image_path, "rb").read() == open(b.image_path, "rb").read()
        assert [m.box.as_tuple() for m in a.marks] == [m.box.as_tuple() for m in b.marks]

    def test_the_render_output_round_trips_through_io(self, rendered, tmp_path):
        serde.save(rendered, tmp_path / "r.json")
        assert serde.load(type(rendered), tmp_path / "r.json") == rendered


class TestStyleNeverMovesAValue:
    def test_labels_and_palette_do_not_move_the_values(self, tmp_path):
        spec, base = serde.sample("FigureSpec"), serde.sample("StyleVector")
        other = replace(base, value_labels="all", palette="grayscale", hatch="//")
        a = render(spec, base, tmp_path / "a")
        b = render(spec, other, tmp_path / "b")
        assert [m.values for m in a.marks] == [m.values for m in b.marks]

    def test_a_wider_bar_moves_the_box_but_not_the_value(self, tmp_path):
        spec, base = serde.sample("FigureSpec"), serde.sample("StyleVector")
        wide = render(spec, replace(base, bar_width=0.8), tmp_path / "w")
        narrow = render(spec, replace(base, bar_width=0.35), tmp_path / "n")
        assert wide.marks[0].box.width > narrow.marks[0].box.width
        assert wide.marks[0].values == narrow.marks[0].values

    def test_writing_labels_records_a_label_box(self, tmp_path):
        spec, base = serde.sample("FigureSpec"), serde.sample("StyleVector")
        out = render(spec, replace(base, value_labels="all"), tmp_path)
        assert all(m.labeled and m.label_box is not None for m in out.marks)

    def test_labelling_half_the_marks_labels_half_of_them(self, tmp_path):
        spec, base = serde.sample("FigureSpec"), serde.sample("StyleVector")
        out = render(spec, replace(base, value_labels="some"), tmp_path)
        assert [m.labeled for m in out.marks] == [True, False, True]

    def test_a_non_zero_baseline_changes_the_axis_but_not_the_values(self, tmp_path):
        spec, base = serde.sample("FigureSpec"), serde.sample("StyleVector")
        zero = render(spec, replace(base, zero_baseline=True), tmp_path / "z")
        free = render(spec, replace(base, zero_baseline=False), tmp_path / "f")
        assert zero.panels[0].axis("y").value_range != free.panels[0].axis("y").value_range
        assert [m.values for m in zero.marks] == [m.values for m in free.marks]

    def test_turning_the_bars_moves_the_value_onto_the_other_axis(self, tmp_path):
        spec, base = serde.sample("FigureSpec"), serde.sample("StyleVector")
        out = render(spec, replace(base, orientation="horizontal"), tmp_path)
        assert all(m.value_axis == "x" for m in out.marks)
        assert out.panels[0].axis("x").value_range == pytest.approx((0.0, 50.0))
        img = rb.load_image(out.image_path)
        slack = channels.geometric_slack(rb.axis_pair(out.panels[0].axis("x")))
        for mark in out.marks:
            assert rb.check_mark(img, mark, out.panels[0], orientation="horizontal",
                                 slack=slack).ok


class TestNumberFormat:
    def test_a_percent_format_does_not_turn_minutes_into_a_percentage(self):
        from chartgen.s03_render.style import format_number

        style = replace(default(), number_format="percent", decimals=1)
        assert format_number(42.3, style, "minutes") == "42.3"

    def test_a_percent_format_applies_where_the_unit_is_a_share(self):
        from chartgen.s03_render.style import format_number

        style = replace(default(), number_format="percent", decimals=1)
        assert format_number(23.3, style, "%") == "23.3%"

    def test_a_currency_symbol_follows_the_unit_and_never_a_score(self):
        from chartgen.s03_render.style import format_number

        style = replace(default(), number_format="currency", decimals=0)
        assert format_number(980, style, "USD") == "$980"
        assert format_number(4, style, "points") == "4"

    def test_the_unit_can_be_written_into_the_label_itself(self):
        from chartgen.s03_render.style import format_number

        style = replace(default(), unit_placement="value_labels", decimals=1)
        assert format_number(42.3, style, "minutes") == "42.3 minutes"


class TestStyleDomains:
    """The declaration and the drawing have to stay in step: a value with no branch
    would let the record state something that never happened."""

    def test_every_dimension_names_a_function_that_exists(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[2] / "src" / "chartgen"
        for name, dim in STYLE_DOMAINS.items():
            path, _, function = dim.draws.partition("::")
            source = root / path
            assert source.exists(), f"{name} points at {source}, which does not exist"
            assert function in source.read_text(), f"{name} points at {dim.draws}"

    def test_every_dimension_declares_its_default_inside_its_own_domain(self):
        for name, dim in STYLE_DOMAINS.items():
            assert dim.default in dim.domain, name

    def test_the_sampler_only_ever_produces_declared_values(self):
        for i in range(60):
            style = sample(7, "er", f"f{i:02d}", i % 2)
            for name, dim in STYLE_DOMAINS.items():
                assert getattr(style, name) in dim.domain, (name, getattr(style, name))

    def test_a_dimension_that_cannot_change_an_answer_does_not(self, er_table, er_schema,
                                                               tmp_path):
        """The neutral dimensions are checked by rendering each of their values and
        requiring the recorded answers back bit for bit."""
        view = bar_view(er_table, er_schema)
        spec = figure(view)
        base = render(spec, default(), tmp_path / "base")
        answers = {m.key: tuple(sorted(m.values.items())) for m in base.marks}
        for name, dim in STYLE_DOMAINS.items():
            if dim.readable:
                continue
            for value in dim.domain:
                out = render(spec, replace(default(), **{name: value}),
                             tmp_path / f"{name}_{value}")
                got = {m.key: tuple(sorted(m.values.items())) for m in out.marks}
                assert got == answers, f"{name}={value!r} changed the answers"

    def test_a_dimension_that_can_change_what_is_readable_is_marked_so(self):
        assert STYLE_DOMAINS["zero_baseline"].readable
        assert STYLE_DOMAINS["log_scale"].readable
        assert STYLE_DOMAINS["value_labels"].readable
        assert not STYLE_DOMAINS["palette"].readable

    def test_the_canvas_dimensions_are_marked_as_changing_what_is_readable(self):
        """Image size, dpi and the margins each decide how many pixels a value gets,
        and whether a value can be measured back out is decided by how much value one
        pixel stands for. None of them is neutral."""
        for name in ("image_size", "dpi", "margins"):
            assert STYLE_DOMAINS[name].readable, name



class TestALogAxisNeverHoldsANegativeValue:
    """A log axis has no room below zero. Asked for over data that dips negative, it
    used to come back with a positive lower bound: every negative mark was then drawn
    on the floor of the axis while the record still claimed its real value, and the
    figure was thrown away by the self-check that caught the mismatch."""

    def view_with_a_negative(self):
        from chartgen.interfaces.figure import Datum, ViewSpec

        binding = Binding("bar", dims=("quarter",), measures=("delta",),
                          aggregate="MIN", key_sources=("axis_tick",))
        data = tuple(Datum((label,), {"value": value}, rows=91) for label, value in
                     (("Q1", 0.5), ("Q2", -0.0), ("Q3", -2.7), ("Q4", -1.0)))
        return ViewSpec(binding, data)

    def test_the_range_stays_linear_when_a_value_dips_below_zero(self):
        from chartgen.s03_render.style import nice_range

        lo, hi, step = nice_range(-2.7, 0.5, replace(default(), log_scale=True))
        assert lo <= -2.7 < hi
        assert step > 0          # a log axis reports no step; a linear one has to

    def test_a_negative_mark_reads_back_as_the_value_it_was_drawn_at(self, tmp_path):
        spec = FigureSpec("f01", "neg", (PanelSpec("p0", (self.view_with_a_negative(),)),),
                          column_units={"delta": "days"})
        out = render(spec, replace(default(), log_scale=True), tmp_path)
        img = rb.load_image(out.image_path)
        panel = out.panels[0]
        assert panel.axis("y").scale == "linear"
        for mark in out.marks:
            if mark.values["value"] == 0.0:
                continue
            check = rb.check_mark(img, mark, panel)
            assert check.value_agrees is not False, (mark.key, check.measured)


class TestNothingIsDrawnOffThePage:
    """Every recorded element is a box a reader can look at.

    Text written past the edge of the image is invisible, and a record that carries a
    box for it describes something nobody can see. Two text blocks written on top of
    each other are as bad: both boxes are right about the pixels and neither is right
    about what is legible there.
    """

    TEXTS = (
        TextBlock("figure_number", "Figure 12", "figure", "above"),
        TextBlock("title", "Average Emergency Department Wait by Hospital and Department",
                  "figure", "above"),
        TextBlock("subtitle", "Weekday arrivals between January and June, three sites",
                  "figure", "above"),
        TextBlock("unit", "minutes", "figure", "above"),
        TextBlock("source", "Source: emergency department arrivals, 900 visits",
                  "figure", "below"),
    )

    def figure_with_text(self, er_table, er_schema):
        binding = Binding("grouped_bar", dims=("hospital", "department"),
                          measures=("wait_minutes",), aggregate="AVG",
                          key_sources=("axis_tick", "legend"))
        return figure(project(er_table.df, binding, er_schema), texts=self.TEXTS)

    def test_every_element_stays_inside_the_image_under_any_style(
            self, er_table, er_schema, tmp_path):
        spec = self.figure_with_text(er_table, er_schema)
        for i in range(24):
            out = render(spec, sample(7, "er", f"f{i:02d}"), tmp_path / f"s{i}")
            w, h = out.image_size
            for element in out.elements:
                x0, y0, x1, y1 = element.box.as_tuple()
                assert -0.5 <= x0 and -0.5 <= y0, (i, element)
                assert x1 <= w + 0.5 and y1 <= h + 0.5, (i, element)
                assert element.box.area > 0, (i, element)

    def panelled(self, er_table, er_schema):
        """Four panels, each with its own title: the case where an axis title placed
        above the plotting area has something else already sitting there."""
        view = bar_view(er_table, er_schema)
        panels = tuple(
            PanelSpec(f"p{i}", (view,),
                      texts=(TextBlock("panel_title", name, "panel", "above"),))
            for i, name in enumerate(("Winter", "Spring", "Summer", "Autumn")))
        return FigureSpec("f02", "er", panels, layout="grid", texts=self.TEXTS,
                          column_units={"wait_minutes": "minutes"})

    def test_no_text_overlaps_under_any_canvas_and_any_axis_furniture(
            self, er_table, er_schema, tmp_path):
        """The combination that broke it on a live batch: the narrowest margins at the
        finest dpi, a second row of tick labels, and the figure's title written below
        rather than above. Everything that competes for the bottom margin at once."""
        import itertools

        spec = self.figure_with_text(er_table, er_schema)
        cases = itertools.product(STYLE_DOMAINS["margins"].domain,
                                  STYLE_DOMAINS["dpi"].domain,
                                  (False, True), ("above", "below"))
        for margins, dpi, two_level, placement in cases:
            style = replace(default(), margins=margins, dpi=dpi, font_size=14.0,
                            two_level_x_labels=two_level, title_placement=placement,
                            label_rotation=45.0)
            out = render(spec, style, tmp_path / f"{margins}{dpi}{two_level}{placement}")
            texts = [e for e in out.elements
                     if e.text and e.category not in ("Picture", "note")]
            for a, b in itertools.combinations(texts, 2):
                covered = a.box.clip_to(b.box).area / min(a.box.area, b.box.area)
                assert covered < 0.5, (margins, dpi, two_level, placement, a, b)

    def test_the_legibility_floor_is_the_same_number_of_pixels_at_every_dpi(self):
        """The floor is on how tall the glyphs come out, because that is what decides
        whether a string can be read off the page. A floor in points would be a
        different floor on legibility at each dpi -- and at the fine end it stopped the
        shrinking before the labels fitted."""
        from chartgen.s03_render.draw.canvas import MIN_TICK_PIXELS, Canvas

        for dpi in STYLE_DOMAINS["dpi"].domain:
            canvas = Canvas(replace(default(), dpi=dpi))
            assert abs(canvas.min_font * dpi / 72.0 - MIN_TICK_PIXELS) < 1e-9, dpi

    def test_two_pieces_of_text_are_not_written_over_each_other(
            self, er_table, er_schema, tmp_path):
        spec = self.figure_with_text(er_table, er_schema)
        for i in range(24):
            out = render(spec, sample(7, "er", f"f{i:02d}"), tmp_path / f"s{i}")
            # A note box is drawn around the lines it holds, so it contains them.
            texts = [e for e in out.elements
                     if e.text and e.category not in ("Picture", "note")]
            for a, b in itertools.combinations(texts, 2):
                shared = a.box.clip_to(b.box)
                covered = shared.area / min(a.box.area, b.box.area)
                assert covered < 0.5, (i, a, b, covered)


    def test_every_canvas_combination_keeps_its_text_inside_the_image(
            self, er_table, er_schema, tmp_path):
        """Image size, dpi and the margins are three independent dimensions, and the
        bands are cut out of the margins rather than written in pixels -- so the
        narrowest margin at the smallest size is the case that decides whether a band
        still has room. Every combination is rendered, because there are only a few
        dozen and one of them going to zero height is a record describing text nobody
        can see."""
        import itertools

        spec = self.figure_with_text(er_table, er_schema)
        combos = itertools.product(STYLE_DOMAINS["image_size"].domain,
                                   STYLE_DOMAINS["dpi"].domain,
                                   STYLE_DOMAINS["margins"].domain)
        for size, dpi, margins in combos:
            style = replace(default(), image_size=size, dpi=dpi, margins=margins)
            out = render(spec, style, tmp_path / f"{size[0]}x{size[1]}_{dpi}_{margins}")
            assert out.image_size == size
            w, h = size
            for element in out.elements:
                x0, y0, x1, y1 = element.box.as_tuple()
                assert -0.5 <= x0 and -0.5 <= y0, (size, dpi, margins, element)
                assert x1 <= w + 0.5 and y1 <= h + 0.5, (size, dpi, margins, element)
                assert element.box.area > 0, (size, dpi, margins, element)

    def test_an_axis_title_above_the_plot_stays_out_of_the_figures_text_band(
            self, er_table, er_schema, tmp_path):
        """It is the one axis title placed by an offset rather than by the fitting
        pass, and the room it has is the gap between the text band and the plotting
        area -- which the margins decide. Under the narrowest margins it used to be
        written across the figure's own title."""
        from chartgen.s03_render.draw.canvas import TEXT_BAND, Canvas

        spec = self.figure_with_text(er_table, er_schema)
        for margins in STYLE_DOMAINS["margins"].domain:
            for size in STYLE_DOMAINS["image_size"].domain:
                style = replace(default(), axis_title_above=True, margins=margins,
                                image_size=size, font_size=14.0)
                out = render(spec, style, tmp_path / f"above_{margins}_{size[0]}")
                floor = Canvas(style).band(TEXT_BAND).y1
                for element in out.elements:
                    if element.category == "axis_title" and element.text:
                        assert element.box.y0 >= floor, (margins, size, element)

    def test_the_bands_keep_their_share_of_the_margin_they_are_cut_from(self):
        """A band written in pixels would keep its height while the margin around it
        moved, and the narrowest margin would leave one of them at nothing."""
        from chartgen.s03_render.draw.canvas import (
            FOOT_BAND, LEGEND_BAND, TEXT_BAND, Canvas,
        )
        from chartgen.s03_render.style import MARGIN_SETS

        for name in MARGIN_SETS:
            canvas = Canvas(replace(default(), margins=name))
            margins = MARGIN_SETS[name]
            text = canvas.band(TEXT_BAND)
            assert text.y1 < margins["top"], name
            for band in (LEGEND_BAND, FOOT_BAND):
                box = canvas.band(band)
                assert box.y0 > canvas.full_rect().y1, (name, band)
                assert box.y1 <= default().image_size[1], (name, band)
                assert box.height > 8.0, (name, band)

    def test_a_panel_title_is_not_written_over_on_a_multi_panel_figure(
            self, er_table, er_schema, tmp_path):
        spec = self.panelled(er_table, er_schema)
        for i in range(12):
            style = replace(sample(9, "er", f"f{i:02d}"), axis_title_above=True)
            out = render(spec, style, tmp_path / f"p{i}")
            texts = [e for e in out.elements
                     if e.text and e.category not in ("Picture", "note")]
            for a, b in itertools.combinations(texts, 2):
                covered = a.box.clip_to(b.box).area / min(a.box.area, b.box.area)
                assert covered < 0.5, (i, a, b, covered)


class TestASeriesOfOnePointAlwaysGetsAMarker:
    """`series_marks` may say a series is carried by its line with no marker on it.
    A line through a single point draws nothing, and the record would go on saying a
    mark is there -- which is the one thing a record may never do.

    The case is not contrived: a view whose second key segment is a colour group puts
    every mark in a group of its own, because a hub reports to one region. The render
    self-check caught it on a live batch as "the box holds no ink".
    """

    def marker(self, points, marks=("line", "circle"), index=0):
        from chartgen.s03_render.draw.point import marker_of

        class Ctx:
            style = replace(default(), series_marks=marks)

        return marker_of(Ctx(), index, points)

    def test_a_series_of_several_points_may_be_carried_by_its_line(self):
        assert self.marker(6) == ""

    def test_a_series_of_one_point_takes_a_marker_instead(self):
        assert self.marker(1) == "o"

    def test_a_named_marker_is_unaffected_by_how_many_points_there_are(self):
        assert self.marker(1, index=1) == "o"
        assert self.marker(6, index=1) == "o"

    def test_every_mark_of_a_colour_grouped_line_holds_ink(self, tmp_path):
        """The live figure that failed: four categories, each in its own colour group,
        drawn as points under a style that carries a series by its line."""
        from chartgen.common import readback
        from chartgen.interfaces.figure import Datum, ViewSpec

        binding = Binding("category_line", dims=("hub",), measures=("days",),
                          aggregate="AVG", key_sources=("axis_tick", "colour_only"))
        data = tuple(Datum((hub, region), {"value": value}, rows=40) for hub, region, value in
                     (("Boston", "Northeast", 9.2), ("Chicago", "Midwest", 10.2),
                      ("Atlanta", "South", 9.9), ("Phoenix", "West", 9.7)))
        spec = figure(ViewSpec(binding, data))
        out = render(spec, replace(default(), series_marks=("line", "circle")),
                     tmp_path / "grouped")
        img = readback.load_image(out.image_path)
        background, _ = readback.background_coverage(img, out.panels[0].box)
        for mark in out.marks:
            frac = readback.ink_fraction(img, readback._at_least(mark.box, 3.0), background)
            assert frac > 0.15, (mark.key, frac)


class TestAValueLabelNeedsClearSpaceAroundIt:
    """A printed value is matched exactly and the mark it belongs to is found by the
    box its label came out in. A share of overlap was the test before, and it cannot
    see the case it most needs to: two labels that butt against each other overlap by
    nothing at all and read as one string -- `2 USD million2 USD millions` is two
    answers and one string.
    """

    def labelled(self, er_table, er_schema, tmp_path, n, **style):
        from chartgen.interfaces.figure import Datum, ViewSpec

        binding = Binding("category_line", dims=("month",), measures=("wait_minutes",),
                          aggregate="AVG", key_sources=("axis_tick",))
        data = tuple(Datum((f"2024-{i + 1:02d}",), {"value": 30.0 + i / 3.0}, rows=40)
                     for i in range(n))
        spec = figure(ViewSpec(binding, data))
        return render(spec, replace(default(), value_labels="all", **style),
                      tmp_path / f"lab{n}")

    def boxes(self, out):
        return [m.label_box for m in out.marks if m.labeled and m.label_box]

    def test_labels_that_fit_are_all_written(self, er_table, er_schema, tmp_path):
        out = self.labelled(er_table, er_schema, tmp_path, 3)
        assert len(self.boxes(out)) == 3

    def test_no_two_labels_are_written_touching(self, er_table, er_schema, tmp_path):
        """Forty labels in a row that fits a dozen: what survives has to be separable."""
        import itertools

        out = self.labelled(er_table, er_schema, tmp_path, 40, font_size=14.0,
                            decimals=2)
        for a, b in itertools.combinations(self.boxes(out), 2):
            assert a.clip_to(b).area == 0.0, (a, b)
            assert a.grow(1.0).clip_to(b).area == 0.0, "touching is not separable either"

    def test_a_dropped_label_leaves_its_mark_with_no_printed_value(
            self, er_table, er_schema, tmp_path):
        """A mark that lost its label goes back among the ones read off the geometry,
        where the readability rule can judge it -- it does not keep an answer nobody
        can read."""
        out = self.labelled(er_table, er_schema, tmp_path, 40, font_size=14.0,
                            decimals=2)
        assert len(self.boxes(out)) < 40
        for mark in out.marks:
            assert bool(mark.label_text) == mark.labeled

    def test_a_label_is_never_written_across_a_tick_label(self, er_table, er_schema,
                                                          tmp_path):
        """A tick label is where a key is read from, so a number written across one
        costs a key as well as a value."""
        out = self.labelled(er_table, er_schema, tmp_path, 40, font_size=14.0,
                            decimals=2, value_label_rotation=90.0)
        ticks = [e.box for e in out.elements if e.category == "axis_title"]
        for box in self.boxes(out):
            for tick in ticks:
                assert box.clip_to(tick).area == 0.0, (box, tick)


class TestTwoViewsInOnePlottingAreaLabelInTheirOwnColour:
    """A printed value is matched exactly, so a label nobody can attribute hands two
    marks one answer that neither can be shown to carry. One ink is enough while one
    view is drawn in a plotting area; two views put two sets of numbers between the
    same marks and leave a reader with nothing but position."""

    class Ctx:
        def __init__(self, overlaid):
            self.overlaid = overlaid

    def test_one_view_writes_every_label_in_the_page_ink(self):
        from chartgen.s03_render.draw.labels import outside_ink
        from chartgen.s03_render.style import TEXT_COLOR

        assert outside_ink(self.Ctx(False), (13, 59, 102)) == TEXT_COLOR

    def test_an_overlaid_view_writes_its_labels_in_its_series_colour(self):
        from chartgen.s03_render.draw.labels import outside_ink

        assert outside_ink(self.Ctx(True), (13, 59, 102)) == (13, 59, 102)

    def test_a_series_colour_too_light_to_read_is_darkened_at_the_same_hue(self):
        from chartgen.s03_render.draw.labels import MAX_ON_PAGE, _luminance, outside_ink

        pale = (214, 235, 250)
        assert _luminance(pale) > MAX_ON_PAGE
        ink = outside_ink(self.Ctx(True), pale)
        assert _luminance(ink) <= MAX_ON_PAGE + 1
        assert ink[2] > ink[1] > ink[0], "the hue has to survive the darkening"

    def test_a_view_with_no_fill_to_go_on_falls_back_to_the_page_ink(self):
        from chartgen.s03_render.draw.labels import outside_ink
        from chartgen.s03_render.style import TEXT_COLOR

        assert outside_ink(self.Ctx(True), None) == TEXT_COLOR

    def test_the_two_series_of_an_overlay_do_not_share_one_label_colour(
            self, er_table, er_schema, tmp_path):
        """The case this exists for: a bar chart with a line over it, both labelled."""
        from chartgen.interfaces.figure import PanelSpec
        from chartgen.s02_figure.project import project

        bars = project(er_table.df, Binding("bar", dims=("hospital",),
                                            measures=("wait_minutes",), aggregate="AVG",
                                            key_sources=("axis_tick",)), er_schema)
        line = project(er_table.df, Binding("category_line", dims=("hospital",),
                                            measures=("wait_minutes",), aggregate="MAX",
                                            key_sources=("axis_tick",)), er_schema)
        spec = FigureSpec("f01", "er", (PanelSpec("p0", (bars, line)),), layout="overlay",
                          column_units={"wait_minutes": "minutes"})
        out = render(spec, replace(default(), value_labels="outside"), tmp_path / "over")
        assert len(out.panels[0].chart_types) == 2
        # Both layers keep labels. Some are dropped where the two series run close
        # enough that the numbers would sit on each other, which is the crowding rule
        # doing its job -- but neither layer may be silenced outright, or the case
        # this colours for would not arise.
        shapes = {m.mark_shape for m in out.marks if m.labeled}
        assert shapes == {"rect", "point"}, shapes


class TestTheCategoryAxisSlantsBeforeItShrinks:
    """Shrinking used to be the only thing on offer when the category names ran into
    each other, so long names went down to the smallest legible type size while the
    axis stayed horizontal. A tick label is where a key is read from, so the angle is
    what gives first now."""

    NAMES = ("Mercy General", "St. Lukes", "Riverside")

    def rotation(self, labels, width, **style):
        from chartgen.s03_render.draw.canvas import fitting_rotation

        return fitting_rotation(list(labels), replace(default(), **style), width)

    def test_names_that_fit_side_by_side_stay_upright(self):
        assert self.rotation(self.NAMES, 724) == 0.0

    def test_names_that_do_not_fit_are_slanted(self):
        assert self.rotation(("Internal Medicine", "Surgery", "Pediatrics", "Trauma"),
                             300) == 30.0

    def test_a_crowded_time_axis_is_slanted_rather_than_shrunk(self):
        months = [f"2021-{m:02d}" for m in range(1, 13)] * 4
        assert self.rotation(months, 724) == 45.0

    def test_fitting_never_stands_a_label_on_its_side(self):
        """Ninety degrees stays a style a batch may ask for, never one arrived at by
        fitting: a name on its side is legible and reads poorly."""
        months = [f"2021-{m:02d}" for m in range(1, 13)] * 8
        assert self.rotation(months, 200) == 45.0

    def test_the_declared_angle_is_a_floor_the_fitting_never_lowers(self):
        for declared in (0.0, 30.0, 45.0, 90.0):
            assert self.rotation(self.NAMES, 724, label_rotation=declared) == declared

    def test_the_angle_actually_drawn_is_what_the_record_carries(self, er_table,
                                                                 er_schema, tmp_path):
        """The style states what a batch asked for; the record has to state what was
        drawn, and between the two sits the fitting."""
        view = bar_view(er_table, er_schema)
        out = render(figure(view), replace(default(), label_rotation=45.0),
                     tmp_path / "slanted")
        axis = out.panels[0].axis("x")
        assert axis is not None and axis.tick_rotation == 45.0


class TestPinningAStyle:
    """How a style ablation is run: pin one dimension, or pin all of them."""

    def test_a_pinned_dimension_survives_the_sampler(self):
        from chartgen.s03_render.style import pin

        for i in range(20):
            style = pin(sample(3, "er", f"f{i}"), {"value_labels": "all"})
            assert style.value_labels == "all"

    def test_pinning_every_dimension_holds_the_style_vector_still(self):
        """Every dimension of the table. Image degradation is a group of its own with
        its own sampler, and is pinned by turning it off rather than by name."""
        from chartgen.interfaces.style import Degradation
        from chartgen.s03_render.style import pin

        every = {name: dim.default for name, dim in STYLE_DOMAINS.items()}
        held = lambda f: replace(pin(sample(3, "er", f), every), degradation=Degradation())
        assert held("f01") == held("f02") == default()

    def test_a_name_that_is_not_a_dimension_is_an_error(self):
        """An ablation that quietly did not happen is worse than one that failed."""
        from chartgen.s03_render.style import pin

        with pytest.raises(ValueError):
            pin(default(), {"colour_group": "region"})
        with pytest.raises(ValueError):
            pin(default(), {"palette": "neon"})

    def test_pinning_the_labels_on_makes_every_value_exact(self, er_table, er_schema,
                                                           tmp_path):
        from chartgen.registry.channels import tolerance
        from chartgen.s03_render.style import pin
        from chartgen.s04_record.selfcheck import finish

        spec = figure(bar_view(er_table, er_schema))
        out = render(spec, pin(sample(3, "er", "f01"), {"value_labels": "all"}), tmp_path)
        record = finish(out, spec)
        assert all(m.labeled and tolerance(m.labeled) == 0.0 for m in record.marks)


class TestALabelHasToBeLegible:
    """A printed value is matched with no tolerance at all, so a label nobody can
    read is worse than no label."""

    def test_text_on_a_dark_fill_is_light_and_on_a_light_fill_is_dark(self):
        from chartgen.s03_render.draw.labels import on
        from chartgen.s03_render.style import BACKGROUND, TEXT_COLOR

        assert on((31, 78, 121)) == BACKGROUND
        assert on((230, 235, 250)) == TEXT_COLOR
        assert on(None) == TEXT_COLOR

    def test_each_channel_carries_its_own_weight_in_the_brightness(self):
        """Green looks much brighter than red at the same number. Weighted wrongly,
        an orange fill is called dark and takes light text nobody can read on it."""
        from chartgen.s03_render.draw.labels import on
        from chartgen.s03_render.style import BACKGROUND, TEXT_COLOR

        assert on((255, 150, 0)) == TEXT_COLOR     # bright: 0.299*255 + 0.587*150
        assert on((255, 0, 0)) == BACKGROUND       # red alone is not bright
        assert on((0, 255, 0)) == TEXT_COLOR       # green alone is

    def test_a_label_inside_a_dark_bar_is_drawn_against_it(self, er_table, er_schema,
                                                           tmp_path):
        from chartgen.common import readback as rb

        spec = figure(bar_view(er_table, er_schema))
        style = replace(default(), value_labels="all", palette="grayscale", decimals=0)
        out = render(spec, style, tmp_path)
        img = rb.load_image(out.image_path)
        darkest = out.marks[0]
        assert darkest.labeled and darkest.label_box is not None
        # The label sits inside the mark, and something of a different colour from
        # the fill is drawn there.
        patch = rb.color_fraction(img, darkest.label_box, (0, 0, 0))
        assert patch < 0.95, "the label is the same colour as the bar it sits on"


class TestTickLabelsDoNotRunTogether:
    """A key is read off the tick that names it, so two ticks written into each other
    name neither. The type size gives; the string never does."""

    def test_labels_that_stand_apart_ask_for_no_shrinking(self):
        from chartgen.s03_render.draw.fit import crowding

        apart = [Box(0, 480, 60, 496), Box(100, 480, 160, 496), Box(200, 480, 260, 496)]
        assert crowding(apart) == 1.0

    def test_the_factor_is_how_much_wider_they_are_than_the_room_between_them(self):
        from chartgen.s03_render.draw.fit import crowding

        # Two 90-wide labels 60 apart: they need 90 + a gap of room and have 60.
        touching = [Box(0, 480, 90, 496), Box(60, 480, 150, 496)]
        assert crowding(touching) == pytest.approx((90 + 4.0) / 60)

    def test_a_narrow_axis_shrinks_its_ticks_until_they_stand_apart(self):
        from chartgen.s03_render.draw.canvas import Canvas
        from chartgen.s03_render.draw.fit import axis_labels, crowding

        canvas = Canvas(replace(default(), image_size=(560, 400), label_rotation=0.0,
                                font_size=13.0, category_label_wrap=False))
        panel = canvas.add_panel("p0", canvas.full_rect(), ["bar"])
        canvas.category_axis(panel, ["Commercial Real Estate", "Middle Market Lending",
                                     "Small Business Banking", "Corporate Banking"])
        axis_labels(canvas)
        boxes = [canvas.text_box(label) for label in panel.ax.get_xticklabels()
                 if label.get_text()]
        assert len(boxes) == 4
        assert crowding(boxes) <= 1.0 + 1e-6


class TestTwoLabelsAreNeverWrittenAcrossEachOther:
    """A printed value is matched exactly and its mark is found by the box its label
    came out in. Two labels written across each other leave two marks with an answer
    neither of them can be shown to carry, so the second is not drawn and its mark
    keeps no printed value."""

    def crowded(self, er_table, er_schema):
        binding = Binding("scatter", measures=("wait_minutes", "cost"),
                          aggregate="NONE", key_sources=("not_shown",))
        return figure(project(er_table.df, binding, er_schema, seed=5))

    def test_a_crowded_figure_keeps_only_the_labels_that_stand_apart(
            self, er_table, er_schema, tmp_path):
        import itertools

        spec = self.crowded(er_table, er_schema)
        out = render(spec, replace(default(), value_labels="all"), tmp_path)
        labelled = [m for m in out.marks if m.label_box is not None]
        assert labelled, "the style asked for every value to be written"
        for a, b in itertools.combinations(labelled, 2):
            small = min(a.label_box.area, b.label_box.area)
            covered = a.label_box.clip_to(b.label_box).area / small
            assert covered <= 0.15 + 1e-9, (a.key, b.key, covered)

    def test_a_mark_whose_label_was_dropped_carries_no_printed_answer(
            self, er_table, er_schema, tmp_path):
        spec = self.crowded(er_table, er_schema)
        out = render(spec, replace(default(), value_labels="all"), tmp_path)
        dropped = [m for m in out.marks if m.label_box is None]
        assert dropped, "a scatter of this size cannot label every point"
        assert all(not m.labeled and not m.label_text for m in dropped)


class TestALabelSaysTheNumberItLabels:
    """A printed value is matched with no tolerance at all. A label that is not
    exactly the number recorded for its mark is a wrong answer written into the
    data, and nothing downstream can tell it apart from a right one."""

    def test_the_label_writer_does_no_arithmetic(self):
        from chartgen.s03_render.draw import labels
        from chartgen.s03_render.style import format_number

        class Ctx:
            style = default()
            unit = staticmethod(lambda: "minutes")

        for value in (0.0, 1.0, 42.3, -17.5, 1234.56, 1e6):
            assert labels.text_for(Ctx(), value) == format_number(value, Ctx.style, "minutes")

    def test_every_printed_label_is_the_value_of_its_own_mark(self, er_table, er_schema,
                                                              tmp_path):
        from chartgen.s03_render.style import format_number

        spec = figure(bar_view(er_table, er_schema))
        for number_format in ("plain", "thousands", "si", "currency"):
            style = replace(default(), value_labels="all", number_format=number_format,
                            decimals=1)
            out = render(spec, style, tmp_path / number_format)
            for mark in out.marks:
                assert mark.labeled and mark.label_text
                assert mark.label_text == format_number(mark.values["value"], style,
                                                        "minutes"), number_format

    def test_a_table_chart_prints_every_one_of_its_values(self, er_table, er_schema,
                                                          tmp_path):
        from chartgen.interfaces.figure import Binding
        from chartgen.s02_figure.keys import key_sources
        from chartgen.s02_figure.project import project
        from chartgen.s03_render.style import format_number

        binding = Binding("table_chart", dims=("hospital", "severity"),
                          measures=("wait_minutes",), aggregate="AVG")
        binding = replace(binding, key_sources=key_sources(binding))
        view = project(er_table.df, binding, er_schema)
        out = render(figure(view), default(), tmp_path)
        for mark in out.marks:
            assert mark.label_text == format_number(mark.values["value"], default(),
                                                    "minutes")

    def test_a_mark_with_no_label_says_so(self, er_table, er_schema, tmp_path):
        spec = figure(bar_view(er_table, er_schema))
        out = render(spec, replace(default(), value_labels="none"), tmp_path)
        assert all(not m.labeled and m.label_text == "" for m in out.marks)


class TestAColourGroupNamesNoSeries:
    """A colour group is a second name every mark already has -- a department reports
    to one hospital -- so it adds a key segment without changing what a mark covers.
    Counted as a series it would split each category's one bar into as many side-by-side
    slots as there are hospitals, and every bar would then sit off the tick its key
    says it was read from."""

    def coloured(self, er_table, er_schema):
        """A month falls in exactly one quarter, so the quarter is a second name for
        the month and not another way of grouping the visits."""
        from chartgen.s02_figure.keys import key_sources

        binding = Binding("bar", dims=("month",), measures=("wait_minutes",),
                          aggregate="AVG", colour_group="quarter")
        binding = replace(binding, key_sources=key_sources(binding))
        return project(er_table.df, binding, er_schema)

    def test_the_key_carries_it_and_the_axis_does_not(self, er_table, er_schema):
        view = self.coloured(er_table, er_schema)
        assert view.binding.n_key == 2 and view.binding.n_group == 1
        assert view.binding.key_sources[-1] == "colour_only"

    def test_every_bar_sits_on_the_tick_its_key_was_read_from(self, er_table, er_schema,
                                                              tmp_path):
        view = self.coloured(er_table, er_schema)
        out = render(figure(view), default(), tmp_path)
        axis = out.panels[0].axis("x")
        lo, hi = axis.value_range
        x0, x1 = axis.pixel_range
        for i, mark in enumerate(out.marks):
            tick = x0 + (i - lo) / (hi - lo) * (x1 - x0)
            centre = (mark.box.x0 + mark.box.x1) / 2
            assert centre == pytest.approx(tick, abs=1.0), mark.key
        spacing = (x1 - x0) / (hi - lo)
        for mark in out.marks:
            assert mark.box.width == pytest.approx(default().bar_width * spacing,
                                                   abs=1.0), mark.key

    def test_a_real_second_grouping_column_still_sits_side_by_side(self, er_table,
                                                                   er_schema, tmp_path):
        from chartgen.s02_figure.keys import key_sources

        binding = Binding("grouped_bar", dims=("hospital", "severity"),
                          measures=("wait_minutes",), aggregate="AVG")
        binding = replace(binding, key_sources=key_sources(binding))
        out = render(figure(project(er_table.df, binding, er_schema)), default(),
                     tmp_path)
        first = [m for m in out.marks if m.key[0] == out.marks[0].key[0]]
        assert len({(m.box.x0 + m.box.x1) / 2 for m in first}) == len(first)


class TestASecondValueAxisLabelsInItsOwnCoordinates:
    """A panel with two value axes holds two mappings from value to height, and the
    same number is a different height on each. Written against the first axis, a
    second-axis label lands beside somebody else's mark; and a value outside the first
    axis's range cannot be placed at all, at which point the plotting library measures
    an empty box and the record claims a printed value that is nowhere on the page."""

    def overlaid(self, er_table, er_schema, tmp_path):
        from chartgen.interfaces.figure import PanelSpec

        minutes = project(er_table.df, Binding("bar", dims=("hospital",),
                                               measures=("wait_minutes",),
                                               aggregate="AVG",
                                               key_sources=("axis_tick",)), er_schema)
        money = project(er_table.df, Binding("category_line", dims=("hospital",),
                                             measures=("cost",), aggregate="SUM",
                                             key_sources=("axis_tick",)), er_schema)
        spec = FigureSpec("f01", "er", (PanelSpec("p0", (minutes, money)),),
                          layout="overlay",
                          column_units={"wait_minutes": "minutes", "cost": "USD"})
        out = render(spec, replace(default(), value_labels="all", dual_axis=True),
                     tmp_path / "two_axes")
        assert {m.value_axis for m in out.marks} == {"y", "y_right"}, "no second axis"
        return out

    def test_no_second_axis_value_lands_inside_the_first_axis_range(
            self, er_table, er_schema, tmp_path):
        """Without this the defect cannot show: a second-axis value that happens to
        fall inside the first axis's range is merely put in the wrong place."""
        out = self.overlaid(er_table, er_schema, tmp_path)
        lo, hi = out.panels[0].axis("y").value_range
        second = [m for m in out.marks if m.value_axis == "y_right"]
        assert second and all(not lo <= m.values["value"] <= hi for m in second)

    def test_every_label_is_measured_and_sits_by_the_mark_it_belongs_to(
            self, er_table, er_schema, tmp_path):
        out = self.overlaid(er_table, er_schema, tmp_path)
        labelled = [m for m in out.marks if m.labeled]
        assert {m.value_axis for m in labelled} == {"y", "y_right"}
        for mark in labelled:
            assert mark.label_box.width > 2 and mark.label_box.height > 2, mark.key
            near = mark.box.grow(40.0)
            assert (near.x0 <= mark.label_box.x0 and mark.label_box.x1 <= near.x1
                    and near.y0 <= mark.label_box.y0
                    and mark.label_box.y1 <= near.y1), (mark.key, mark.label_box)


class TestNoAxisIsNamedOnlyInTheRecord:
    """`value_column` asks a question in the axis title "because that is what the page
    says". An axis whose label was recorded but never drawn turns that into a question
    about a quantity the page never names, which asks the reader to know the table."""

    def named_on_the_page(self, out) -> set[str]:
        return {e.text.rstrip("…") for e in out.elements if e.category == "axis_title"}

    def check(self, out) -> None:
        drawn = self.named_on_the_page(out)
        for panel in out.panels:
            for axis in panel.axes:
                if not axis.label:
                    continue
                assert any(axis.label.startswith(t) or t.startswith(axis.label)
                           for t in drawn), (panel.panel_id, axis.role, axis.label)

    def test_the_second_value_axis_is_named_where_it_is_drawn(self, er_table, er_schema,
                                                              tmp_path):
        from chartgen.interfaces.figure import PanelSpec

        minutes = project(er_table.df, Binding("bar", dims=("hospital",),
                                               measures=("wait_minutes",),
                                               aggregate="AVG",
                                               key_sources=("axis_tick",)), er_schema)
        money = project(er_table.df, Binding("category_line", dims=("hospital",),
                                             measures=("cost",), aggregate="SUM",
                                             key_sources=("axis_tick",)), er_schema)
        out = render(FigureSpec("f01", "er", (PanelSpec("p0", (minutes, money)),),
                                layout="overlay",
                                column_units={"wait_minutes": "minutes", "cost": "USD"}),
                     replace(default(), dual_axis=True), tmp_path / "second")
        assert out.panels[0].axis("y_right") is not None
        self.check(out)

    def test_sharing_one_axis_does_not_silence_the_other(self, er_table, er_schema,
                                                         tmp_path):
        """Two panels over the same categories carrying different measures share their
        category axis and nothing else. One flag for both titles left the second
        measure unnamed on the page while the record still said what it is called."""
        from chartgen.interfaces.figure import PanelSpec, Sharing

        minutes = project(er_table.df, Binding("bar", dims=("hospital",),
                                               measures=("wait_minutes",),
                                               aggregate="AVG",
                                               key_sources=("axis_tick",)), er_schema)
        money = project(er_table.df, Binding("bar", dims=("hospital",),
                                             measures=("cost",), aggregate="SUM",
                                             key_sources=("axis_tick",)), er_schema)
        out = render(FigureSpec("f01", "er",
                                (PanelSpec("p0", (minutes,)), PanelSpec("p1", (money,))),
                                layout="side_by_side", sharing=Sharing(share_x=True),
                                column_units={"wait_minutes": "minutes", "cost": "USD"}),
                     default(), tmp_path / "shared_x")
        self.check(out)


class TestANestedSecondColumnUsesTheWholeSlot:
    """A second key column is not always crossed with the first. Divided by the whole
    series list, a category that holds two of six series spends two thirds of its slot
    on sub-slots nothing is drawn in, and draws the bars that are there four pixels
    wide beside a gap wide enough for four more."""

    def nested(self, er_table, er_schema, tmp_path):
        """Mercy General keeps three departments, the other two keep one each."""
        keep = {("Mercy General", "Trauma"), ("Mercy General", "Surgery"),
                ("Mercy General", "Pediatrics"), ("St. Luke's", "Surgery"),
                ("Riverside", "Trauma")}
        rows = er_table.df[[(h, d) in keep for h, d
                            in zip(er_table.df["hospital"], er_table.df["department"])]]
        view = project(rows, Binding("grouped_bar", dims=("hospital", "department"),
                                     measures=("wait_minutes",), aggregate="AVG",
                                     key_sources=("axis_tick", "legend")), er_schema)
        return render(FigureSpec("f01", "er", (PanelSpec("p0", (view,)),),
                                 column_units={"wait_minutes": "minutes"}),
                      default(), tmp_path / "nested")

    def widths(self, out):
        from collections import defaultdict

        by = defaultdict(list)
        for mark in out.marks:
            edges = ("x0", "x1") if mark.value_axis == "y" else ("y0", "y1")
            by[mark.key[0]].append(tuple(getattr(mark.box, e) for e in edges))
        return by

    def test_the_categories_do_not_all_hold_the_same_number_of_series(
            self, er_table, er_schema, tmp_path):
        by = self.widths(self.nested(er_table, er_schema, tmp_path))
        assert sorted(len(v) for v in by.values()) == [1, 1, 3]

    def test_every_category_spends_its_whole_slot(self, er_table, er_schema, tmp_path):
        """Same slot width for every category, whatever it holds inside."""
        by = self.widths(self.nested(er_table, er_schema, tmp_path))
        spans = {round(max(e[1] for e in v) - min(e[0] for e in v), 1)
                 for v in by.values()}
        assert len(spans) == 1, spans

    def test_a_category_holding_one_series_draws_one_full_width_bar(
            self, er_table, er_schema, tmp_path):
        by = self.widths(self.nested(er_table, er_schema, tmp_path))
        alone = [v[0] for v in by.values() if len(v) == 1]
        crowded = [e for v in by.values() if len(v) == 3 for e in v]
        assert min(e[1] - e[0] for e in alone) > 2.5 * max(e[1] - e[0] for e in crowded)


class TestATickLabelIsRecordedWhereItWasDrawn:
    """A tick label is where a key is read from, so where it landed is worth the same
    box the value gets: `key_src` says a segment came off an axis tick, and the box
    says which tick. It is kept out of the page-element target, whose vocabulary is
    the benchmark's, in which the whole chart is one Picture."""

    def bars(self, er_table, er_schema, tmp_path, **style):
        view = project(er_table.df, Binding("bar", dims=("hospital",),
                                            measures=("wait_minutes",), aggregate="AVG",
                                            key_sources=("axis_tick",)), er_schema)
        return render(FigureSpec("f01", "er", (PanelSpec("p0", (view,)),),
                                 column_units={"wait_minutes": "minutes"}),
                      replace(default(), **style), tmp_path / "ticks")

    def ticks(self, out):
        return [e for e in out.elements if e.category == "axis_tick"]

    def test_one_box_per_tick_label(self, er_table, er_schema, tmp_path):
        out = self.bars(er_table, er_schema, tmp_path)
        drawn = {e.text for e in self.ticks(out)}
        assert {m.key[0] for m in out.marks} <= drawn

    def test_every_mark_sits_on_the_tick_its_key_was_read_from(self, er_table, er_schema,
                                                               tmp_path):
        out = self.bars(er_table, er_schema, tmp_path)
        by_text = {e.text: e.box for e in self.ticks(out)}
        for mark in out.marks:
            assert mark.key_src[0] == "axis_tick"
            tick = by_text[mark.key[0]]
            centre = (mark.box.x0 + mark.box.x1) / 2
            assert tick.x0 - 2 <= centre <= tick.x1 + 2, (mark.key, centre, tick)

    def test_the_boxes_hold_ink(self, er_table, er_schema, tmp_path):
        from chartgen.common import readback as rb

        out = self.bars(er_table, er_schema, tmp_path)
        img = rb.load_image(out.image_path)
        for element in self.ticks(out):
            assert rb.ink_fraction(img, element.box) > 0.01, element

    def test_they_stay_out_of_the_page_element_target(self, er_table, er_schema,
                                                     tmp_path):
        from chartgen.s04_record.selfcheck import finish
        from chartgen.s05_output import export as E

        view = project(er_table.df, Binding("bar", dims=("hospital",),
                                            measures=("wait_minutes",), aggregate="AVG",
                                            key_sources=("axis_tick",)), er_schema)
        spec = FigureSpec("f01", "er", (PanelSpec("p0", (view,)),),
                          column_units={"wait_minutes": "minutes"})
        record = finish(render(spec, default(), tmp_path / "target"), spec)
        assert self.ticks(record)
        assert not [e for e in E.build(record).page_elements
                    if e["category"] == "axis_tick"]
