"""Whether a value can be read off the image, and with what tolerance.

Three rules, applied in order:

    the value is written on the chart   readable, and it must match exactly
    otherwise, angle or colour          not readable
    otherwise, length or position       readable when one percent of the value is
                                        at least two pixels, within one percent

The record builder and the reward check both call this, so there is one rule and
one place it lives.
"""

from __future__ import annotations

from ..common.geometry import Range, value_per_pixel

#: Encodings a value can be measured back out of.
MEASURABLE = frozenset({"length", "position"})

#: Encodings that cannot reach one percent precision: an angle is too small to
#: measure on a small sector, and a colour scale is quantised and non-linear.
UNMEASURABLE = frozenset({"angle", "color"})

#: Pixels that one percent of the value must span before it counts as readable.
MIN_PIXELS_PER_PERCENT = 2.0

#: Relative tolerance when the value is not written on the chart.
RELATIVE_TOLERANCE = 0.01

Axis = tuple[Range, Range]     # (value_range, pixel_range)


def pixels_per_percent(value: float, axis: Axis) -> float:
    """How many pixels one percent of this value spans."""
    value_range, pixel_range = axis
    return abs(value) * RELATIVE_TOLERANCE / value_per_pixel(value_range, pixel_range)


def readable(channel: str, *, labeled: bool, value: float, axis: Axis | None) -> bool:
    if labeled:
        return True
    if channel in UNMEASURABLE:
        return False
    if channel not in MEASURABLE:
        raise ValueError(f"unknown encoding: {channel}")
    if axis is None:
        return False
    return pixels_per_percent(value, axis) >= MIN_PIXELS_PER_PERCENT


def tolerance(labeled: bool) -> float:
    """A written value must match exactly; an estimated one gets one percent."""
    return 0.0 if labeled else RELATIVE_TOLERANCE
