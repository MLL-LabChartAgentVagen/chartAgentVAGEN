"""D1 · 边画边记的最小实现，配 E3.1 / E3.2 两项自检。

这一组测试是整条流水线的正确性底线：框由绘图库自己的坐标变换算出，错了不会
抛异常，只会安静地产出偏移的框。所以判据不是「有没有框」，而是回读渲染出的
PNG，看框里有没有东西、框反算出的值对不对。
"""

import pytest

from chartgen.common import readback as rb
from chartgen.common.geometry import Box
from chartgen.interfaces import io
from chartgen.interfaces.style import StyleVector
from chartgen.s03_render.render import render

#: 03 §0 记下的几何，规格文档与样例文件里的数字都是这一组。
PLOT_RECT = (96.0, 60.0, 860.0, 520.0)
BAR_BOXES = {
    ("Mercy General",): (168.0, 196.0, 278.0, 520.0),
    ("St. Luke's",): (423.0, 245.0, 533.0, 520.0),
    ("Riverside",): (678.0, 305.0, 788.0, 520.0),
}


@pytest.fixture(scope="module")
def rendered(tmp_path_factory):
    spec = io.sample("FigureSpec")
    style = io.sample("StyleVector")
    return render(spec, style, tmp_path_factory.mktemp("render"))


class TestFrozenLayout:
    def test_the_image_has_exactly_the_declared_size(self, rendered):
        img = rb.load_image(rendered.image_path)
        assert img.shape[:2] == (600, 900)
        assert rendered.image_size == (900, 600)

    def test_the_plot_area_is_where_it_was_declared(self, rendered):
        assert rendered.panels[0].box.as_tuple() == pytest.approx(PLOT_RECT, abs=0.5)

    def test_the_y_axis_maps_zero_to_sixty_onto_the_plot_area(self, rendered):
        y = next(a for a in rendered.panels[0].axes if a.role == "y")
        assert y.value_range == pytest.approx((0.0, 60.0))
        assert y.pixel_range == pytest.approx((520.0, 60.0), abs=0.5)
        assert y.column == "wait_minutes"

    def test_the_x_axis_is_recorded_too(self, rendered):
        x = next(a for a in rendered.panels[0].axes if a.role == "x")
        assert x.column == "hospital"
        assert x.pixel_range == pytest.approx((96.0, 860.0), abs=0.5)


class TestMarksRecordedWhileDrawing:
    def test_one_mark_per_projected_value(self, rendered):
        assert len(rendered.marks) == 3
        assert [m.key for m in rendered.marks] == [("Mercy General",), ("St. Luke's",), ("Riverside",)]

    def test_each_mark_carries_its_value(self, rendered):
        assert [m.values["value"] for m in rendered.marks] == [42.3, 35.8, 28.1]

    def test_each_mark_box_matches_the_worked_example(self, rendered):
        for mark in rendered.marks:
            assert mark.box.as_tuple() == pytest.approx(BAR_BOXES[mark.key], abs=1.0), mark.key

    def test_bars_sit_on_the_baseline(self, rendered):
        assert [m.box.y1 for m in rendered.marks] == pytest.approx([520.0] * 3, abs=0.5)

    def test_the_channel_comes_from_the_type_table(self, rendered):
        assert {m.channel for m in rendered.marks} == {"length"}

    def test_no_value_labels_were_written(self, rendered):
        assert not any(m.labeled for m in rendered.marks)
        assert all(m.label_box is None for m in rendered.marks)

    def test_rows_and_readable_are_left_for_stage_04(self, rendered):
        assert all(m.rows is None and m.readable is None for m in rendered.marks)


class TestSelfCheckOne:
    """框里有没有东西——挡住框整体偏移、自动布局挪动绘图区、dpi 换算错。"""

    def test_every_recorded_box_actually_contains_ink(self, rendered):
        img = rb.load_image(rendered.image_path)
        for mark in rendered.marks:
            assert rb.box_has_content(img, mark.box), mark.key

    def test_a_box_moved_into_the_gap_between_bars_is_caught(self, rendered):
        img = rb.load_image(rendered.image_path)
        moved = Box(*(v + 145 for v in rendered.marks[0].box.as_tuple()[:1]),
                    rendered.marks[0].box.y0, 423.0, rendered.marks[0].box.y1)
        assert not rb.box_has_content(img, moved)

    def test_the_gap_between_two_bars_is_empty(self, rendered):
        img = rb.load_image(rendered.image_path)
        assert rb.ink_fraction(img, Box(300, 300, 400, 500)) < 0.05

    def test_a_box_moved_onto_the_next_bar_passes_check_one_and_fails_check_two(self, rendered):
        """两项自检分工：①只管框里有没有东西，②才管这块几何配不配这个值。"""
        img = rb.load_image(rendered.image_path)
        y = next(a for a in rendered.panels[0].axes if a.role == "y")
        slot = 764 / 3
        moved = Box(rendered.marks[0].box.x0 + slot, rendered.marks[0].box.y0,
                    rendered.marks[0].box.x1 + slot, rendered.marks[0].box.y1)
        assert rb.box_has_content(img, moved)
        r = rb.verify(img, box=moved, claimed_value=35.8,
                      axis=(y.value_range, y.pixel_range), anchor="top")
        assert r.has_content and not r.value_agrees


class TestSelfCheckTwo:
    """量出来的值对不对——挡住轴映射错误、负值与堆叠基线错误。"""

    def test_each_bar_reads_back_within_one_percent(self, rendered):
        y = next(a for a in rendered.panels[0].axes if a.role == "y")
        axis = (y.value_range, y.pixel_range)
        for mark in rendered.marks:
            measured = rb.value_from_box(mark.box, axis, anchor="top")
            assert rb.value_agrees(measured, mark.values["value"], 0.01), mark.key

    def test_a_wrong_axis_range_would_be_caught(self, rendered):
        wrong = ((0.0, 120.0), (520.0, 60.0))
        mark = rendered.marks[0]
        measured = rb.value_from_box(mark.box, wrong, anchor="top")
        assert not rb.value_agrees(measured, mark.values["value"], 0.01)


class TestDeterminism:
    def test_the_same_spec_and_style_render_byte_identical_images(self, tmp_path):
        spec, style = io.sample("FigureSpec"), io.sample("StyleVector")
        a = render(spec, style, tmp_path / "a")
        b = render(spec, style, tmp_path / "b")
        assert open(a.image_path, "rb").read() == open(b.image_path, "rb").read()
        assert io.to_dict(a.marks) == io.to_dict(b.marks)

    def test_the_render_output_round_trips_through_io(self, rendered, tmp_path):
        from chartgen.interfaces.record import RenderOutput

        io.save(rendered, tmp_path / "r.json")
        assert io.load(RenderOutput, tmp_path / "r.json") == rendered


class TestStyleDoesNotChangeTheAnswer:
    """风格与真值分离：换风格，键 → 值 必须一模一样。"""

    def test_labels_and_palette_do_not_move_the_values(self, tmp_path):
        spec = io.sample("FigureSpec")
        plain = render(spec, io.sample("StyleVector"), tmp_path / "a")
        fancy = render(spec, StyleVector(value_labels="all", palette="grayscale",
                                         gridlines=False, bar_width=0.8), tmp_path / "b")
        assert ({m.key: m.values for m in plain.marks}
                == {m.key: m.values for m in fancy.marks})

    def test_a_wider_bar_moves_the_box_but_not_the_value(self, tmp_path):
        spec = io.sample("FigureSpec")
        wide = render(spec, StyleVector(bar_width=0.8), tmp_path / "c")
        assert wide.marks[0].box.width == pytest.approx(0.8 / 0.432 * 110, abs=2)

    def test_writing_labels_records_a_label_box(self, tmp_path):
        spec = io.sample("FigureSpec")
        out = render(spec, StyleVector(value_labels="all"), tmp_path / "d")
        assert all(m.labeled for m in out.marks)
        assert all(m.label_box is not None for m in out.marks)

    def test_a_non_zero_baseline_changes_the_axis_but_not_the_values(self, tmp_path):
        spec = io.sample("FigureSpec")
        out = render(spec, StyleVector(zero_baseline=False), tmp_path / "e")
        y = next(a for a in out.panels[0].axes if a.role == "y")
        assert y.value_range[0] > 0
        assert [m.values["value"] for m in out.marks] == [42.3, 35.8, 28.1]
