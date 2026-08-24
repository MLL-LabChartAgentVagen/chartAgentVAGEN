"""Whether a value can be read off the image, and with what tolerance.

Four rules, applied in order:

    the value is printed on the chart   readable, and it must match exactly
    otherwise, a colour                 not readable: a colour scale is quantised and
                                        non-linear, with no closed form for its step
    otherwise, an angle                 readable when the share the wedge holds is
                                        larger than what its radius pins it to
    otherwise, length or position       readable when the tolerance band spans at
                                        least two pixels

Angle used to sit beside colour as a flat refusal. That answered one question with
a constant: whether a wedge can be read depends on the share it holds, the radius it
was drawn at, and the tolerance being asked for -- and at a five percent tolerance
every wedge above a twentieth of a pie is comfortably inside it. What replaced the
refusal is the same shape of rule the other encodings already used: a step the
geometry gives, compared against the tolerance the caller means.

The tolerance is a parameter rather than a constant, because the three callers
mean different things by it and cannot borrow each other's number:

    the spot-check target   the benchmark's own terms: nothing written means one
                            percent, a written value means exact
    the render self-check   what the pixels can actually resolve, which is one
                            value-per-pixel step of the axis the mark was measured against
    the reward check        the same as the self-check, because it is the same code
                            reading a model's answer instead of the renderer's

Three situations move the step inside one figure, and none of them can be handled
by a single figure-wide number:

    a log axis          the step depends on where on the axis the mark sits, so it
                        is computed per mark
    a stacked segment   its value is a difference of two edges, so two readings go
                        into it and the slack doubles
    partial labelling   a mark that got a printed value has a step of zero while
                        its neighbours do not

The record builder and the reward check both call this, so there is one rule and
one place it lives.
"""

from __future__ import annotations

import math

from ..common.geometry import Range, value_per_pixel

#: Encodings a value can be measured back out of along an axis.
MEASURABLE = frozenset({"length", "position"})

#: Encodings measured as an angle rather than along an axis. A wedge's share is the
#: turn between its two edge rays, so what it can be pinned to follows from the
#: radius it was drawn at, the same way a bar's follows from its value axis.
ANGULAR = frozenset({"angle"})

#: Encodings with no closed form for what they can be pinned to. A colour scale is
#: quantised and non-linear, so a swatch cannot be turned back into a number at any
#: stated precision.
UNMEASURABLE = frozenset({"color"})

#: Encodings that write the number out. Nothing is measured, so nothing is estimated.
PRINTED = frozenset({"printed"})

#: Pixels the tolerance band must span before a value counts as readable.
MIN_PIXELS = 2.0

#: Relative tolerance when the value is not written on the chart. This is the
#: benchmark's number, and it is the default rather than a constant in the rule.
RELATIVE_TOLERANCE = 0.01

#: Pixels of slack the geometric checks allow: half a pixel of rounding at each
#: of the two edges the reading is taken between, plus one for anti-aliasing.
PIXEL_SLACK = 2.0

#: The same, for a reading taken around an arc rather than along an axis. Larger than
#: `PIXEL_SLACK` because a wedge boundary is not a step between fill and background:
#: it carries an edge stroke up to one and a half pixels wide, and the hatch, shadow
#: and near-neighbour palettes put their own colours across it.
#:
#: Measured rather than assumed. Every pie one run drew, each under forty style
#: vectors -- six hundred wedges -- puts the error at 0.5 arc pixels in the median,
#: 1.6 at the ninety-fifth percentile and 3.2 at the ninety-ninth, so three pixels for
#: each of the two rays covers everything a correctly drawn wedge does.
ARC_SLACK = 3.0

#: Used instead of a proportional band when the value being checked is zero.
ABSOLUTE_FLOOR = 1e-6

Axis = tuple[Range, Range]     # (value_range, pixel_range)


def epsilon(axis: Axis) -> float:
    """How much value one pixel of this axis stands for."""
    return value_per_pixel(*axis)


def pixels_for(value: float, axis: Axis, tolerance: float = RELATIVE_TOLERANCE) -> float:
    """How many pixels the tolerance band around this value spans."""
    return abs(value) * tolerance / epsilon(axis)


def angular_epsilon(radius: float, pixels: float = ARC_SLACK,
                    readings: int = 2) -> float:
    """The share a wedge can be pinned to, from the radius it was drawn at.

    A wedge's share is the turn between its two edge rays, and each ray can be placed
    to within a pixel or two where it meets the rim. Two readings go into one share,
    and dividing the arc error by the whole circumference turns it into a share:

        epsilon = pixels * readings / (2 * pi * radius)

    This is the angular counterpart of "how much value one pixel of this axis stands
    for", and it is why an angle is graded rather than refused outright. A wedge drawn
    at a hundred and twenty-five pixels is pinned to within three quarters of a percent
    of the whole, so at a five percent tolerance every wedge above a seventh of the pie
    can be read and at a one percent tolerance none of them can -- an answer a single
    verdict cannot give.
    """
    return pixels * readings / (2.0 * math.pi * radius) if radius > 0 else float("inf")


def readable(channel: str, *, labeled: bool, value: float, axis: Axis | None,
             tolerance: float = RELATIVE_TOLERANCE, radius: float | None = None) -> bool:
    """Whether this value can be recovered from the image within `tolerance`.

    `radius` is the pie's radius in pixels, and only a sector needs it: an angle has
    no value axis to be measured against, so the radius is what stands in for one.
    """
    if labeled or channel in PRINTED:
        return True
    if channel in UNMEASURABLE:
        return False
    if channel in ANGULAR:
        if radius is None:
            return False
        return angular_epsilon(radius) <= tolerance * abs(value)
    if channel not in MEASURABLE:
        raise ValueError(f"unknown encoding: {channel}")
    if axis is None:
        return False
    return pixels_for(value, axis, tolerance) >= MIN_PIXELS


def tolerance(labeled: bool, base: float = RELATIVE_TOLERANCE) -> float:
    """A written value must match exactly; an estimated one gets `base`."""
    return 0.0 if labeled else base


#: What a magnitude suffix multiplies a printed number by. Only a suffix written
#: directly against the digits counts: `12.5 MWh` is megawatt hours, not millions.
SUFFIX_SCALE: dict[str, float] = {"K": 1e3, "M": 1e6, "B": 1e9}


def printed_quantum(text: str) -> float:
    """The step a value was rounded to before it was written, read off how it reads.

    A label showing `5` says the value is nearer 5 than 4 or 6; one showing `4.9K`
    says it is within fifty of 4900. Read off the string rather than recomputed from
    the number format, so it stays right for whatever produced the string.
    """
    number, rest = "", ""
    for i, char in enumerate(text):
        if char.isdigit() or char == "." or (char == "," and number):
            number += char
        elif number:
            rest = text[i:]
            break
    decimals = len(number.replace(",", "").partition(".")[2])
    return 10.0 ** -decimals * SUFFIX_SCALE.get(rest[:1], 1.0)


def printed_tolerance(text: str, value: float, base: float = RELATIVE_TOLERANCE) -> float:
    """Relative tolerance for a value the chart writes out.

    A written value is matched exactly against the string, and that string is
    exported beside this number. Compared as a number instead, "exactly" means the
    rounding the printing did and nothing more: the answer a reader can give is the
    one on the page, and asking for the unrounded value would mark the only readable
    answer wrong.
    """
    if not text:
        return 0.0
    if not value:
        return base
    return printed_quantum(text) / 2.0 / abs(value)


def geometric_slack(axis: Axis | None, *, labeled: bool = False, quantum: float = 0.0,
                    readings: int = 1, pixels: float = PIXEL_SLACK) -> float:
    """Absolute slack for comparing a value measured off the pixels with a recorded one.

    `readings` is how many box edges the value was taken between: one for a bar
    whose base is the axis, two for a stacked segment, whose value is a difference.

    `quantum` is the step the value itself was recorded at. Half of it is a floor,
    because a column rounded to one decimal carries an error of up to 0.05, which
    on a satisfaction score near 4 is larger than one percent.
    """
    if labeled:
        return max(quantum / 2.0, ABSOLUTE_FLOOR)
    step = 0.0 if axis is None else epsilon(axis) * pixels * readings
    return max(step, quantum / 2.0, ABSOLUTE_FLOOR)
