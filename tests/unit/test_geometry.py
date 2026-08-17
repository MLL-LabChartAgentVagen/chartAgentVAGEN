"""几何：全流水线唯一一套坐标约定，以及退化 / 页面合成共用的框变换。"""

import math

import pytest

from chartgen.common import geometry as g


class TestBox:
    def test_box_is_x0_y0_x1_y1_with_origin_top_left(self):
        b = g.Box(168, 196, 278, 520)
        assert (b.x0, b.y0, b.x1, b.y1) == (168, 196, 278, 520)
        assert b.width == 110
        assert b.height == 324

    def test_box_normalises_swapped_corners(self):
        assert g.Box(278, 520, 168, 196).as_tuple() == (168.0, 196.0, 278.0, 520.0)

    def test_box_rejects_non_finite(self):
        with pytest.raises(ValueError):
            g.Box(0, 0, float("nan"), 10)

    def test_area_and_contains(self):
        b = g.Box(0, 0, 10, 20)
        assert b.area == 200
        assert b.contains(5, 5)
        assert not b.contains(11, 5)

    def test_intersection_over_union(self):
        a = g.Box(0, 0, 10, 10)
        b = g.Box(5, 0, 15, 10)
        assert g.iou(a, b) == pytest.approx(50 / 150)
        assert g.iou(a, g.Box(20, 20, 30, 30)) == 0.0


class TestTransforms:
    def test_identity_leaves_box_untouched(self):
        b = g.Box(168, 196, 278, 520)
        assert g.apply(g.identity(), b).as_tuple() == b.as_tuple()

    def test_scale_then_translate_matches_page_composition_example(self):
        # 03 §0 第三步：图表缩放 0.8 倍贴到 (120, 340)
        t = g.compose(g.translate(120, 340), g.scale(0.8, 0.8))
        assert g.apply(t, g.Box(0, 0, 900, 600)).as_tuple() == (120.0, 340.0, 840.0, 820.0)

    def test_rotation_takes_bounding_box_of_four_corners(self):
        b = g.Box(0, 0, 10, 0)          # 一条水平线段
        out = g.apply(g.rotate(90, cx=0, cy=0), b)
        assert out.as_tuple() == pytest.approx((0.0, 0.0, 0.0, 10.0), abs=1e-9)

    def test_rotated_box_is_never_smaller_than_the_original(self):
        b = g.Box(10, 10, 30, 50)
        out = g.apply(g.rotate(7, cx=20, cy=30), b)
        assert out.area >= b.area

    def test_homography_maps_corners_and_takes_bounding_box(self):
        h = g.homography(((0, 0), (100, 0), (100, 100), (0, 100)),
                         ((0, 0), (100, 10), (90, 100), (10, 90)))
        out = g.apply(h, g.Box(0, 0, 100, 100))
        assert out.x0 == pytest.approx(0.0, abs=1e-6)
        assert out.x1 == pytest.approx(100.0, abs=1e-6)
        assert out.y1 == pytest.approx(100.0, abs=1e-6)

    def test_compose_is_right_to_left(self):
        # 先缩放再平移
        t = g.compose(g.translate(5, 0), g.scale(2, 2))
        assert g.apply(t, g.Box(1, 1, 2, 2)).as_tuple() == (7.0, 2.0, 9.0, 4.0)

    def test_inverse_round_trips(self):
        t = g.compose(g.translate(120, 340), g.scale(0.8, 0.8))
        b = g.Box(3, 4, 30, 40)
        back = g.apply(g.invert(t), g.apply(t, b))
        assert back.as_tuple() == pytest.approx(b.as_tuple())


class TestAxisMapping:
    """值域 ↔ 像素域。04 的可读性判定与自检都只用这一个换算。"""

    def test_value_to_pixel_matches_the_worked_example(self):
        # y 值域 [0, 60] ↔ 像素域 520 (值 0) → 60 (值 60)
        assert g.value_to_pixel(42.3, (0, 60), (520, 60)) == pytest.approx(196.0, abs=0.5)
        assert g.value_to_pixel(0, (0, 60), (520, 60)) == 520.0

    def test_pixel_to_value_is_the_inverse(self):
        assert g.pixel_to_value(196.0, (0, 60), (520, 60)) == pytest.approx(42.26, abs=0.05)
        for v in (0.0, 12.5, 60.0):
            px = g.value_to_pixel(v, (0, 60), (520, 60))
            assert g.pixel_to_value(px, (0, 60), (520, 60)) == pytest.approx(v)

    def test_value_per_pixel(self):
        assert g.value_per_pixel((0, 60), (520, 60)) == pytest.approx(60 / 460)

    def test_log_scale_maps_decades_evenly(self):
        px_lo = g.value_to_pixel(1, (1, 1000), (500, 100), scale="log")
        px_mid = g.value_to_pixel(10, (1, 1000), (500, 100), scale="log")
        px_hi = g.value_to_pixel(100, (1, 1000), (500, 100), scale="log")
        assert px_lo - px_mid == pytest.approx(px_mid - px_hi)

    def test_zero_span_value_range_is_rejected(self):
        with pytest.raises(ValueError):
            g.value_to_pixel(1.0, (5, 5), (500, 100))


class TestFrozenLayout:
    def test_axes_rect_is_a_pure_function_of_size_and_margins(self):
        rect = g.axes_rect((900, 600), left=96, top=60, right=40, bottom=80)
        assert rect.as_tuple() == (96.0, 60.0, 860.0, 520.0)
        assert rect.as_tuple() == g.axes_rect((900, 600), left=96, top=60, right=40, bottom=80).as_tuple()

    def test_axes_rect_rejects_margins_that_leave_no_room(self):
        with pytest.raises(ValueError):
            g.axes_rect((100, 100), left=60, top=10, right=60, bottom=10)


def test_matplotlib_fraction_round_trip():
    """matplotlib 用左下原点的 0–1 figure 坐标，本项目用左上原点的像素。"""
    size = (900, 600)
    rect = g.axes_rect(size, left=96, top=60, right=40, bottom=80)
    frac = g.rect_to_mpl_fraction(rect, size)
    assert frac == pytest.approx((96 / 900, 80 / 600, 764 / 900, 460 / 600))
    assert g.mpl_fraction_to_rect(frac, size).as_tuple() == pytest.approx(rect.as_tuple())


def test_math_import_is_used_for_rotation_reference():
    assert math.isclose(g.rotate(90)[0][0], 0.0, abs_tol=1e-9)
