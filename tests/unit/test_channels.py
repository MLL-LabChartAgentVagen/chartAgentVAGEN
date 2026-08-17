"""画法 → 值能不能读出。判据在 chart_types.md §4 定义一次，这里只是执行它。"""

import pytest

from chartgen.registry import channels as ch

Y_460PX = ((0.0, 60.0), (520.0, 60.0))       # 04 §0：值域 [0,60] ↔ 460 像素
Y_SHARED = ((0.0, 6000.0), (520.0, 60.0))    # 与另一面板共享 y 轴后的值域


class TestThreeRules:
    def test_a_written_label_is_always_readable_with_zero_tolerance(self):
        assert ch.readable("angle", labeled=True, value=0.38, axis=None)
        assert ch.tolerance(labeled=True) == 0.0

    def test_angle_and_color_are_not_readable_without_a_label(self):
        for channel in ("angle", "color"):
            assert not ch.readable(channel, labeled=False, value=0.38, axis=Y_460PX)

    def test_length_is_readable_when_one_percent_spans_at_least_two_pixels(self):
        # 每像素 0.13 分钟；42.3 的 1% 是 0.42 分钟 ≈ 3.2 像素
        assert ch.readable("length", labeled=False, value=42.3, axis=Y_460PX)

    def test_the_same_bar_stops_being_readable_on_a_shared_axis(self):
        # 每像素 13 分钟；42.3 的 1% 只有 0.03 像素
        assert not ch.readable("length", labeled=False, value=42.3, axis=Y_SHARED)

    def test_position_follows_the_length_rule(self):
        for channel in ("position",):
            assert ch.readable(channel, labeled=False, value=42.3, axis=Y_460PX)
            assert not ch.readable(channel, labeled=False, value=42.3, axis=Y_SHARED)


class TestBoundary:
    def test_exactly_two_pixels_counts_as_readable(self):
        # 值域跨度 100，像素跨度 100 → 每像素 1；值 200 的 1% 恰好 2 像素
        axis = ((0.0, 100.0), (100.0, 0.0))
        assert ch.readable("length", labeled=False, value=200.0, axis=axis)
        assert not ch.readable("length", labeled=False, value=199.0, axis=axis)

    def test_a_zero_value_has_no_measurable_one_percent(self):
        assert not ch.readable("length", labeled=False, value=0.0, axis=Y_460PX)

    def test_a_negative_value_uses_its_magnitude(self):
        assert ch.readable("length", labeled=False, value=-42.3, axis=Y_460PX)

    def test_a_length_mark_without_an_axis_is_not_readable(self):
        assert not ch.readable("length", labeled=False, value=42.3, axis=None)


class TestTolerance:
    def test_unlabelled_values_carry_one_percent_relative_tolerance(self):
        assert ch.tolerance(labeled=False) == pytest.approx(0.01)

    def test_the_worked_example_tolerances(self):
        # 05 §0：Mercy General 42.3 ± 0.42
        assert 42.3 * ch.tolerance(labeled=False) == pytest.approx(0.423)


class TestPixelsPerPercent:
    def test_reports_how_many_pixels_one_percent_spans(self):
        assert ch.pixels_per_percent(42.3, Y_460PX) == pytest.approx(3.24, abs=0.01)
        assert ch.pixels_per_percent(42.3, Y_SHARED) == pytest.approx(0.032, abs=0.001)
