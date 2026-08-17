"""Whether a value can be read off the image, given how it is encoded."""

import pytest

from chartgen.registry import channels as ch

Y_460PX = ((0.0, 60.0), (520.0, 60.0))       # 60 units of value across 460 pixels
Y_SHARED = ((0.0, 6000.0), (520.0, 60.0))    # the same axis after sharing it with a larger panel


class TestThreeRules:
    def test_a_written_label_is_always_readable_with_zero_tolerance(self):
        assert ch.readable("angle", labeled=True, value=0.38, axis=None)
        assert ch.tolerance(labeled=True) == 0.0

    def test_angle_and_color_are_not_readable_without_a_label(self):
        for channel in ("angle", "color"):
            assert not ch.readable(channel, labeled=False, value=0.38, axis=Y_460PX)

    def test_length_is_readable_when_one_percent_spans_at_least_two_pixels(self):
        # 0.13 units per pixel; one percent of 42.3 is 0.42, about 3.2 pixels
        assert ch.readable("length", labeled=False, value=42.3, axis=Y_460PX)

    def test_the_same_bar_stops_being_readable_on_a_shared_axis(self):
        # 13 units per pixel; one percent of 42.3 is 0.03 pixels
        assert not ch.readable("length", labeled=False, value=42.3, axis=Y_SHARED)

    def test_position_follows_the_length_rule(self):
        for channel in ("position",):
            assert ch.readable(channel, labeled=False, value=42.3, axis=Y_460PX)
            assert not ch.readable(channel, labeled=False, value=42.3, axis=Y_SHARED)


class TestBoundary:
    def test_exactly_two_pixels_counts_as_readable(self):
        # one unit per pixel, so one percent of 200 is exactly two pixels
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
