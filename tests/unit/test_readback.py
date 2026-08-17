"""Measuring values back out of pixels: one implementation, used at generation,
training and evaluation time."""

import numpy as np
import pytest

from chartgen.common import readback as rb
from chartgen.common.geometry import Box

BLUE = (31, 78, 121)
BAR = Box(168, 196, 278, 520)
Y_AXIS = ((0.0, 60.0), (520.0, 60.0))


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
    """How far a measured value may sit from a claimed one."""

    def test_within_one_percent_passes(self):
        assert rb.value_agrees(measured=42.26, claimed=42.3, tolerance=0.01)

    def test_beyond_one_percent_fails(self):
        assert not rb.value_agrees(measured=39.0, claimed=42.3, tolerance=0.01)

    def test_zero_tolerance_demands_exact_match(self):
        assert rb.value_agrees(measured=42.3, claimed=42.3, tolerance=0.0)
        assert not rb.value_agrees(measured=42.31, claimed=42.3, tolerance=0.0)

    def test_a_claimed_zero_falls_back_to_an_absolute_floor(self):
        assert rb.value_agrees(measured=0.0, claimed=0.0, tolerance=0.01)
        assert not rb.value_agrees(measured=5.0, claimed=0.0, tolerance=0.01)


class TestVerifyTuple:
    """The same check with the claim coming from a model instead of the renderer."""

    def test_a_correct_tuple_passes_both_geometric_checks(self, canvas):
        r = rb.verify(canvas, box=BAR, claimed_value=42.3, axis=Y_AXIS, anchor="top")
        assert r.has_content and r.value_agrees and r.ok

    def test_an_invented_region_fails_the_first_check(self, canvas):
        r = rb.verify(canvas, box=Box(600, 60, 700, 150), claimed_value=42.3,
                      axis=Y_AXIS, anchor="top")
        assert not r.has_content and not r.ok

    def test_a_wrong_value_on_a_real_region_fails_the_second(self, canvas):
        r = rb.verify(canvas, box=BAR, claimed_value=12.0, axis=Y_AXIS, anchor="top")
        assert r.has_content and not r.value_agrees and not r.ok

    def test_without_an_axis_only_the_content_check_runs(self, canvas):
        r = rb.verify(canvas, box=BAR, claimed_value=42.3, axis=None, anchor="top")
        assert r.has_content and r.value_agrees is None and r.ok
