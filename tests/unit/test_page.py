"""Composing figures onto a page, and degrading the image without losing a box."""

import pytest

from chartgen.common import readback as rb
from chartgen.interfaces.figure import Binding, FigureSpec, PanelSpec, TextBlock
from chartgen.interfaces.style import Degradation
from chartgen.s02_figure.project import project
from chartgen.s03_render import degrade, page
from chartgen.s03_render.render import render
from chartgen.s03_render.style import default

UNITS = {"wait_minutes": "minutes", "cost": "USD"}


def bar_figure(er_table, er_schema, figure_id="f01", dims=("hospital",), **kw):
    binding = Binding("bar", dims=dims, measures=("wait_minutes",), aggregate="AVG",
                      key_sources=("axis_tick",) * len(dims))
    view = project(er_table.df, binding, er_schema)
    return FigureSpec(figure_id, "er", (PanelSpec("p0", (view,)),),
                      column_units=UNITS, **kw)


@pytest.fixture(scope="module")
def drawn(er_table, er_schema, tmp_path_factory):
    out = tmp_path_factory.mktemp("page")
    a = render(bar_figure(er_table, er_schema, "f01", texts=(
        TextBlock("title", "Wait by hospital", "figure", "above"),)), default(), out)
    b = render(bar_figure(er_table, er_schema, "f02", dims=("severity",), texts=(
        TextBlock("title", "Wait by severity", "figure", "above"),)), default(), out)
    return a, b, out


class TestPageComposition:
    def test_both_figures_end_up_on_one_image(self, drawn):
        a, b, out = drawn
        composed = page.compose([a, b], out, page_id="pg01", header="H", body="B" * 200,
                                footer="F", captions=["one", "two"])
        assert {r.image_path for r in composed} == {str(out / "pg01.png")}
        assert {r.page_id for r in composed} == {"pg01"}
        assert {r.image_size for r in composed} == {page.PAGE_SIZE}

    def test_every_mark_still_has_its_mark_underneath_it(self, drawn):
        a, b, out = drawn
        composed = page.compose([a, b], out, page_id="pg02", header="H", body="B" * 200)
        img = rb.load_image(composed[0].image_path)
        for record in composed:
            for mark in record.marks:
                result = rb.check_mark(img, mark, record.panel(mark.panel_id))
                assert result.has_content, (record.figure_id, mark.key)

    def test_the_values_still_read_back_off_the_pasted_geometry(self, drawn):
        from chartgen.registry import channels

        a, b, out = drawn
        composed = page.compose([a, b], out, page_id="pg03", header="H", body="B" * 200)
        img = rb.load_image(composed[0].image_path)
        for record in composed:
            panel = record.panels[0]
            slack = channels.geometric_slack(rb.axis_pair(panel.axis("y")))
            for mark in record.marks:
                assert rb.check_mark(img, mark, panel, slack=slack).ok, mark.key

    def test_the_page_furniture_is_recorded_with_its_category(self, drawn):
        a, b, out = drawn
        composed = page.compose([a, b], out, page_id="pg04", header="Report",
                                body="B" * 200, footer="page 1", captions=["c1", "c2"])
        categories = {e.category for e in composed[0].elements}
        assert {"Page-Header", "Page-Footer", "Text", "Picture"} <= categories

    def test_each_figure_keeps_its_own_title_and_the_page_keeps_both(self, drawn):
        a, b, out = drawn
        composed = page.compose([a, b], out, page_id="pg05", header="H", body="B" * 200)
        first = {e.text for e in composed[0].elements}
        second = {e.text for e in composed[1].elements}
        assert "Wait by hospital" in first and "Wait by hospital" not in second
        assert "Wait by severity" in second

    def test_a_figure_no_longer_fills_the_frame(self, drawn):
        """A bare image puts the chart across the whole picture, which makes
        localisation a question with one answer."""
        a, b, out = drawn
        composed = page.compose([a, b], out, page_id="pg06", header="H", body="B" * 200)
        picture = next(e for e in composed[0].elements if e.category == "Picture")
        assert picture.box.area < 0.4 * page.PAGE_SIZE[0] * page.PAGE_SIZE[1]


class TestOneFigureOnAPage:
    def test_it_takes_the_whole_width(self, drawn):
        """A page of one is still a page: its figure gets the full column, not half
        of it with a gap where the second would have gone."""
        a, b, out = drawn
        alone = page.compose([a], out / "one", page_id="p_alone", header="H", body="B")
        pair = page.compose([a, b], out / "two", page_id="p_pair", header="H", body="B")
        width_alone = _picture(alone[0]).width
        width_pair = _picture(pair[0]).width
        assert width_alone > width_pair * 1.5

    def test_its_marks_still_read_back(self, drawn):
        a, _, out = drawn
        alone = page.compose([a], out / "one_read", page_id="p_read",
                             header="H", body="B")[0]
        img = rb.load_image(alone.image_path)
        for mark in alone.marks:
            assert rb.check_mark(img, mark, alone.panels[0]).has_content, mark.key


def _picture(rendered):
    return next(e.box for e in rendered.elements if e.category == "Picture")


class TestWhatTheExporterSeesOfAPage:
    def test_both_figures_on_a_page_carry_the_whole_page(self, drawn):
        """Each figure knows only its own text blocks. Exported as it stands, every
        page-element target would be missing the other half of the page, which reads
        as a labelling error rather than as a split view."""
        from chartgen.s05_output import export as E

        a, b, out = drawn
        page_a, page_b = page.compose([a, b], out / "merged", page_id="pg",
                                      header="H", body="B",
                                      captions=["one", "two"])
        units = E.with_whole_page([E.build(_recorded(page_a, "f01")),
                                   E.build(_recorded(page_b, "f02"))])
        assert units[0].page_elements == units[1].page_elements
        assert len(units[0].page_elements) > len(page_a.elements)
        texts = {e["text"] for e in units[0].page_elements}
        assert "Wait by hospital" in texts and "Wait by severity" in texts


def _recorded(rendered, figure_id):
    """A render output finished into a record, without going back to the figure."""
    from chartgen.interfaces.record import Record

    return Record(**{f: getattr(rendered, f) for f in
                     ("figure_id", "scenario_id", "image_path", "image_size", "style",
                      "panels", "marks", "legend", "elements", "degradations",
                      "page_id", "variant", "caption")})


class TestDegradation:
    def test_a_lossy_encoding_leaves_every_box_where_it_was(self, drawn):
        a, _, _ = drawn
        out = degrade.apply_to(a, Degradation("jpeg", 0.5))
        assert [m.box.as_tuple() for m in out.marks] == [m.box.as_tuple() for m in a.marks]
        assert out.image_path.endswith(".jpg")
        assert out.degradations == (Degradation("jpeg", 0.5),)

    def test_noise_and_blur_leave_the_geometry_alone(self, drawn):
        a, _, _ = drawn
        for kind in ("noise", "blur"):
            out = degrade.apply_to(a, Degradation(kind, 0.4))
            assert [m.box.as_tuple() for m in out.marks] == [m.box.as_tuple()
                                                             for m in a.marks]

    def test_a_downscale_scales_the_boxes_by_the_same_factor(self, drawn):
        a, _, _ = drawn
        out = degrade.apply_to(a, Degradation("downscale", 0.0))
        factor = out.image_size[0] / a.image_size[0]
        for before, after in zip(a.marks, out.marks):
            assert after.box.x0 == pytest.approx(before.box.x0 * factor, abs=0.5)
            assert after.box.y1 == pytest.approx(before.box.y1 * factor, abs=0.5)

    def test_a_downscale_keeps_the_shape_of_the_image(self, drawn):
        """Both sides scale by the same factor. Scaled by the width twice, a page
        comes out square and every recorded box lands somewhere else."""
        a, _, _ = drawn
        assert a.image_size[0] != a.image_size[1]
        out = degrade.apply_to(a, Degradation("downscale", 0.5))
        assert out.image_size[0] != out.image_size[1]
        before = a.image_size[0] / a.image_size[1]
        assert out.image_size[0] / out.image_size[1] == pytest.approx(before, abs=0.02)
        from PIL import Image

        with Image.open(out.image_path) as img:
            assert img.size == out.image_size

    def test_the_marks_are_still_there_after_a_downscale(self, drawn):
        a, _, _ = drawn
        out = degrade.apply_to(a, Degradation("downscale", 0.3))
        img = rb.load_image(out.image_path)
        for mark in out.marks:
            assert rb.check_mark(img, mark, out.panels[0]).has_content, mark.key

    def test_the_axis_ranges_move_with_the_image(self, drawn):
        a, _, _ = drawn
        out = degrade.apply_to(a, Degradation("downscale", 0.0))
        factor = out.image_size[0] / a.image_size[0]
        before = a.panels[0].axis("y").pixel_range
        after = out.panels[0].axis("y").pixel_range
        assert after == pytest.approx(tuple(v * factor for v in before), abs=0.5)

    def test_a_rotation_maps_four_corners_and_takes_the_bounding_box(self, drawn):
        """A turned rectangle needs a slightly larger box than it had. That is known
        and bounded, and the record says which transform produced it."""
        a, _, _ = drawn
        out = degrade.apply_to(a, Degradation("rotate", 1.0))
        assert out.marks[0].box.width > a.marks[0].box.width
        assert out.degradations[-1].kind == "rotate"

    def test_a_shared_page_image_is_degraded_once_for_every_figure_on_it(self, drawn):
        """Degrading per figure would degrade the page as many times as it holds
        figures, and every record but the first would map through a spent transform."""
        a, b, out = drawn
        composed = page.compose([a, b], out, page_id="pg07", header="H", body="B" * 200)
        done = degrade.apply_to_all(composed, Degradation("downscale", 0.0))
        assert len({r.image_path for r in done}) == 1
        img = rb.load_image(done[0].image_path)
        for record in done:
            for mark in record.marks:
                assert rb.check_mark(img, mark, record.panel(mark.panel_id)).has_content

    def test_nothing_happens_when_nothing_is_asked_for(self, drawn):
        a, _, _ = drawn
        assert degrade.apply_to(a, Degradation("none", 0.0)) is a


class TestAPageLineNeverRunsOffTheEdge:
    """A page header is one line by design and a scenario title is as long as its
    subject needs. Left as it is, a long one runs past the right margin and off the
    page -- and the record then carries a box for text nobody can see, which is the
    one thing a record may never do."""

    def compose_with(self, drawn, **kw):
        a, _, out = drawn
        return page.compose([a], out, page_id="pgx", **kw), page.PAGE_SIZE

    def long_title(self):
        return ("Monthly clinical trial budget burn, milestone attainment and vendor "
                "invoice latency across contract research organisations and study "
                "phases, January 2022 through June 2024")

    def test_a_long_header_is_cut_to_the_page(self, drawn):
        out, (w, h) = self.compose_with(drawn, header=self.long_title())
        headers = [e for r in out for e in r.elements if e.category == "Page-Header"]
        assert headers
        for element in headers:
            assert element.box.x1 <= w + 0.5, element
            assert element.text.endswith("…"), "a cut line says where it was cut"

    def test_what_the_record_carries_is_what_was_drawn(self, drawn):
        """The string asked for and the string on the page are different once one was
        cut, and the record has to carry the second."""
        out, _ = self.compose_with(drawn, header=self.long_title())
        header = next(e for r in out for e in r.elements if e.category == "Page-Header")
        assert header.text != self.long_title()
        assert self.long_title().startswith(header.text[:20])

    def test_a_short_header_is_left_alone(self, drawn):
        out, _ = self.compose_with(drawn, header="Quarterly review")
        header = next(e for r in out for e in r.elements if e.category == "Page-Header")
        assert header.text == "Quarterly review"

    def test_every_page_element_stays_inside_the_page(self, drawn):
        out, (w, h) = self.compose_with(
            drawn, header=self.long_title(), body=self.long_title(),
            footer=self.long_title(), captions=[self.long_title()],
            closing=self.long_title())
        for record in out:
            for element in record.elements:
                x0, y0, x1, y1 = element.box.as_tuple()
                assert -0.5 <= x0 and -0.5 <= y0, element
                assert x1 <= w + 0.5 and y1 <= h + 0.5, element


class TestNothingOnAPageIsWrittenOverAPicture:
    """A figure is scaled to the width of its slot and its height follows from its own
    aspect ratio, which is a style dimension. At a fixed closing height, a page of two
    tall figures had its closing paragraph drawn across the picture -- and the record
    then carries a box for a line the picture covers."""

    def tall(self, er_table, er_schema, out):
        from dataclasses import replace as swap

        style = swap(default(), image_size=(720, 900))
        return [render(bar_figure(er_table, er_schema, f"f{i:02d}", texts=(
            TextBlock("title", f"Wait {i}", "figure", "above"),)), style, out / f"t{i}")
            for i in (1, 2)]

    def overlaps(self, record):
        pictures = [e.box for e in record.elements if e.category == "Picture"]
        return [(e.category, e.text) for e in record.elements
                if e.category in ("Text", "Page-Footer", "Page-Header")
                for p in pictures
                if min(e.box.x1, p.x1) - max(e.box.x0, p.x0) > 1
                and min(e.box.y1, p.y1) - max(e.box.y0, p.y0) > 1]

    def test_a_page_of_two_tall_figures_keeps_its_closing_text_clear(
            self, er_table, er_schema, tmp_path):
        drawn = self.tall(er_table, er_schema, tmp_path)
        composed = page.compose(drawn, tmp_path, page_id="tall", header="H",
                                body="B" * 200, footer="F", captions=["one", "two"],
                                closing="C" * 300)
        for record in composed:
            assert self.overlaps(record) == []

    def test_four_figures_wrap_into_rows_that_do_not_land_on_each_other(
            self, er_table, er_schema, tmp_path):
        drawn = self.tall(er_table, er_schema, tmp_path) * 2
        composed = page.compose(drawn, tmp_path, page_id="four", header="H", body="B",
                                closing="C" * 300)
        # Each record carries its own figure's elements, so the four pictures are
        # collected across the four records rather than off any one of them.
        boxes = [e.box for r in composed for e in r.elements if e.category == "Picture"]
        assert len(boxes) == 4
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                across = min(a.x1, b.x1) - max(a.x0, b.x0)
                down = min(a.y1, b.y1) - max(a.y0, b.y0)
                assert across <= 1 or down <= 1, (a, b)

    def test_every_picture_stays_inside_the_page(self, er_table, er_schema, tmp_path):
        drawn = self.tall(er_table, er_schema, tmp_path) * 2
        composed = page.compose(drawn, tmp_path, page_id="inside", header="H", body="B")
        w, h = page.PAGE_SIZE
        for record in composed:
            for e in record.elements:
                assert e.box.x1 <= w + 0.5 and e.box.y1 <= h + 0.5, e
