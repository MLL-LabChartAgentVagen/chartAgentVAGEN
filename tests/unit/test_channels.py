"""Whether a value can be read off the image, given how it is encoded."""

import pytest

from chartgen.registry import channels as ch

Y_460PX = ((0.0, 60.0), (520.0, 60.0))       # 60 units of value across 460 pixels
Y_SHARED = ((0.0, 6000.0), (520.0, 60.0))    # the same axis after sharing it with a larger panel


class TestFourRules:
    def test_a_written_label_is_always_readable_with_zero_tolerance(self):
        assert ch.readable("angle", labeled=True, value=0.38, axis=None)
        assert ch.tolerance(labeled=True) == 0.0

    def test_angle_and_color_are_not_readable_without_a_label(self):
        for channel in ("angle", "color"):
            assert not ch.readable(channel, labeled=False, value=0.38, axis=Y_460PX)

    def test_a_printed_value_is_readable_with_no_geometry_at_all(self):
        assert ch.readable("printed", labeled=False, value=42.3, axis=None)

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

    def test_an_unknown_encoding_is_an_error_rather_than_a_silent_false(self):
        with pytest.raises(ValueError):
            ch.readable("texture", labeled=False, value=1.0, axis=Y_460PX)


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


class TestToleranceIsAParameter:
    def test_unlabelled_values_carry_one_percent_by_default(self):
        assert ch.tolerance(labeled=False) == pytest.approx(0.01)

    def test_the_worked_example_tolerances(self):
        # 05 §0: Mercy General 42.3 +- 0.42
        assert 42.3 * ch.tolerance(labeled=False) == pytest.approx(0.423)

    def test_a_caller_may_pass_its_own_base(self):
        assert ch.tolerance(labeled=False, base=0.05) == pytest.approx(0.05)
        assert ch.tolerance(labeled=True, base=0.05) == 0.0

    def test_a_looser_tolerance_makes_a_shared_axis_readable_again(self):
        wide = ((0.0, 300.0), (520.0, 60.0))     # 0.65 units per pixel
        assert not ch.readable("length", labeled=False, value=42.3, axis=wide)
        assert ch.readable("length", labeled=False, value=42.3, axis=wide, tolerance=0.05)

    def test_a_pie_survives_at_five_percent_only_if_it_is_labelled(self):
        """The angle rule does not soften with the tolerance; only a label removes it."""
        assert not ch.readable("angle", labeled=False, value=0.38, axis=None, tolerance=0.05)
        assert ch.readable("angle", labeled=True, value=0.38, axis=None, tolerance=0.05)


class TestPixelsFor:
    def test_reports_how_many_pixels_the_tolerance_band_spans(self):
        assert ch.pixels_for(42.3, Y_460PX) == pytest.approx(3.24, abs=0.01)
        assert ch.pixels_for(42.3, Y_SHARED) == pytest.approx(0.032, abs=0.001)

    def test_epsilon_is_the_value_one_pixel_stands_for(self):
        assert ch.epsilon(Y_460PX) == pytest.approx(60 / 460)


class TestWhatAPrintedValueSays:
    """A label is the answer, and how it is written says how precisely: `5` claims
    less than `5.0`, and `4.9K` claims less than either."""

    def test_the_step_is_read_off_how_the_number_is_written(self):
        assert ch.printed_quantum("5") == 1.0
        assert ch.printed_quantum("5.0") == pytest.approx(0.1)
        assert ch.printed_quantum("1,234.56") == pytest.approx(0.01)
        assert ch.printed_quantum("(5)") == 1.0
        assert ch.printed_quantum("88%") == 1.0

    def test_a_magnitude_suffix_multiplies_it(self):
        assert ch.printed_quantum("4.9K") == pytest.approx(100.0)
        assert ch.printed_quantum("$3.4M") == pytest.approx(1e5)
        assert ch.printed_quantum("2B") == pytest.approx(1e9)

    def test_a_unit_written_after_the_number_is_not_a_suffix(self):
        """`12.5 MWh` is megawatt hours, not twelve and a half million: only a letter
        written against the digits scales them."""
        assert ch.printed_quantum("12.5 MWh") == pytest.approx(0.1)
        assert ch.printed_quantum("7 Kg") == 1.0

    def test_the_tolerance_is_the_rounding_and_nothing_more(self):
        assert ch.printed_tolerance("5", 4.862) == pytest.approx(0.5 / 4.862)
        assert ch.printed_tolerance("4.9", 4.862) == pytest.approx(0.05 / 4.862)

    def test_a_value_that_was_not_written_is_matched_exactly(self):
        assert ch.printed_tolerance("", 4.862) == 0.0

    def test_a_zero_falls_back_to_the_relative_tolerance(self):
        assert ch.printed_tolerance("0", 0.0) == ch.RELATIVE_TOLERANCE


class TestGeometricSlack:
    def test_slack_is_a_few_pixels_worth_of_value(self):
        assert ch.geometric_slack(Y_460PX) == pytest.approx(60 / 460 * 2.0)

    def test_a_value_taken_between_two_edges_gets_twice_the_slack(self):
        one = ch.geometric_slack(Y_460PX, readings=1)
        two = ch.geometric_slack(Y_460PX, readings=2)
        assert two == pytest.approx(2 * one)

    def test_a_printed_value_is_not_estimated_so_the_axis_does_not_matter(self):
        assert ch.geometric_slack(Y_460PX, labeled=True) == pytest.approx(ch.ABSOLUTE_FLOOR)

    def test_half_a_recording_step_is_a_floor_under_the_slack(self):
        """A column rounded to one decimal carries up to 0.05 of error, which on a
        satisfaction score near four is larger than one percent."""
        fine = ((0.0, 5.0), (520.0, 60.0))          # 0.011 units per pixel
        assert ch.geometric_slack(fine, quantum=0.1) == pytest.approx(0.05)
        assert ch.geometric_slack(fine, quantum=0.0) < 0.05

    def test_with_no_axis_only_the_recording_step_is_left(self):
        assert ch.geometric_slack(None, quantum=0.1) == pytest.approx(0.05)
        assert ch.geometric_slack(None) == pytest.approx(ch.ABSOLUTE_FLOOR)


class TestAnAngleIsGradedRatherThanRefused:
    """An angle used to sit beside colour as a flat refusal, which answered one
    question with a constant. What a wedge can be pinned to follows from the radius it
    was drawn at, exactly as a bar's follows from its value axis -- so the same shape
    of rule applies, and the answer depends on the tolerance being asked for."""

    RADIUS = 125.3      # a pie on a 900x600 image with the normal margins

    def readable_at(self, share, tolerance, radius=None):
        from chartgen.registry.channels import readable

        return readable("angle", labeled=False, value=share, axis=None,
                        tolerance=tolerance, radius=radius or self.RADIUS)

    def test_the_step_falls_as_the_radius_grows(self):
        from chartgen.registry.channels import angular_epsilon

        assert angular_epsilon(250.0) < angular_epsilon(125.0) < angular_epsilon(60.0)

    def test_a_pie_drawn_at_no_radius_at_all_pins_nothing(self):
        from chartgen.registry.channels import angular_epsilon

        assert angular_epsilon(0.0) == float("inf")

    def test_the_same_wedge_reads_differently_under_two_tolerances(self):
        """The whole point of grading: one wedge, two answers, because the callers
        mean different things by "close enough"."""
        assert not self.readable_at(0.24, 0.01)
        assert self.readable_at(0.24, 0.05)

    def test_a_wedge_too_narrow_for_its_radius_is_not_readable(self):
        assert not self.readable_at(0.02, 0.05)

    def test_a_wedge_with_its_value_printed_on_it_is_exact_whatever_the_angle(self):
        from chartgen.registry.channels import readable

        assert readable("angle", labeled=True, value=0.02, axis=None,
                        tolerance=0.01, radius=10.0)

    def test_an_angle_with_no_circle_recorded_cannot_be_read(self):
        """Without a centre there is nothing to measure the turn from."""
        from chartgen.registry.channels import readable

        assert not readable("angle", labeled=False, value=0.40, axis=None,
                            tolerance=0.05, radius=None)

    def test_a_colour_stays_refused_at_every_tolerance(self):
        from chartgen.registry.channels import readable

        for tolerance in (0.01, 0.05, 0.20):
            assert not readable("color", labeled=False, value=1.0, axis=None,
                                tolerance=tolerance)
