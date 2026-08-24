"""Measuring things back out of the rendered pixels.

Two questions, both answerable from an image and a claimed `(key, value, box)`
without any ground truth: is there anything inside the box, and does the box
geometry agree with the claimed value.

That is why there is one implementation and three callers. During generation the
claim comes from the renderer and a failure discards the figure. During training
the claim comes from the model and the same code is the reward. During evaluation
it yields a consistency metric on datasets that carry no box annotations at all.

Two things are read off the record rather than assumed. The axis is the one the
mark says it was measured against, because a panel may carry two of them and the
same pixel height then means two different values. The background is the panel's
own, because a tinted or banded panel would make "anything that is not white" true
everywhere and quietly turn the first check into a pass.
"""

from __future__ import annotations

import math

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np

from ..interfaces.record import Axis, Mark, MarkShape, Panel
from .geometry import Box, Range, pixel_to_value, value_to_pixel

Anchor = Literal["top", "bottom", "left", "right", "center_x", "center_y"]
AxisPair = tuple[Range, Range]             # (value_range, pixel_range)
Orientation = Literal["vertical", "horizontal"]
RGB = tuple[int, int, int]

#: Which axis a value key is measured against: the one the mark names, or the
#: category axis, which only a per-row view reads a value off.
VALUE_AXIS, CROSS_AXIS = "value", "x"

#: Per-channel distance from the target colour that still counts as that colour.
COLOR_TOLERANCE = 30

#: Per-channel distance from the background before a pixel counts as ink.
INK_TOLERANCE = 12

#: Fraction of a box that must be ink before the box counts as non-empty.
MIN_CONTENT_FRACTION = 0.15

#: The same, for a mark whose value is printed rather than drawn. What is inside
#: the box is a few glyphs, and glyphs never fill a cell.
MIN_TEXT_FRACTION = 0.02

#: The same, for a point. A point's box is a fixed square around where the marker was
#: drawn, deliberately: the value is read off the centre of the box, so the box may
#: not depend on which marker the style picked. A marker then fills whatever part of
#: that square its own shape covers -- a filled circle most of it, a tick a thin line
#: down the middle -- and the fraction is a fact about the marker, not about whether
#: anything was drawn.
#:
#: Measured over every marker at every dpi, on a scatter, where a point has no line
#: running through it to add ink: the thinnest case is a tick at seventy-two dots per
#: inch, which fills six percent. A box moved onto plain background fills none. Three
#: percent separates them.
MIN_POINT_FRACTION = 0.03

#: Absolute floor used instead of a proportional band when the claim is zero.
ABSOLUTE_FLOOR = 1e-6

#: How coarsely the panel is sampled when its background colour is looked for.
BACKGROUND_STEP = 3

#: The band of the panel the background colour is looked for in, as a fraction of
#: the panel: the strip along the top and a column down each side.
BACKGROUND_TOP = 0.14
BACKGROUND_SIDE = 0.06

#: How much of a panel its background has to cover before "is anything drawn here"
#: is a question with an answer. A heatmap paints every pixel of its plotting area,
#: so on one the first check has nothing to discriminate with and says so.
MIN_BACKGROUND_COVERAGE = 0.20

#: Pixels a box is padded out to before its content is looked at. A thin mark has
#: too few pixels of its own to judge, and waving it through would excuse exactly the
#: marks most likely to have been drawn away -- so the box is grown around its own
#: centre instead and the question is asked of that.
MIN_INTERIOR = 3.0

#: A mark of no extent at all: a histogram bin holding no rows is a rectangle of zero
#: height. There is nothing inside it because there was nothing to put there.
EMPTY_VALUE = 1e-9

#: Which pair of value keys spans the mark's box, in preference order. The pair is
#: a property of the shape, not of the numbers: a box plot's box runs between the
#: quartiles while its whiskers reach the extremes, so measuring `min` off the box
#: edge would read the quartile and call it the minimum.
SPANNING_KEYS: dict[MarkShape, tuple[tuple[str, str], ...]] = {
    "rect": (("cum_start", "cum_end"), ("min", "max")),
    # A stacked area is a point mark that spans its layer, so it takes the same
    # pair a stacked rectangle does, and for the same reason: its value is the
    # difference of two edges and sits on neither of them.
    "point": (("cum_start", "cum_end"), ("min", "max"), ("lo", "hi")),
    "boxlike": (("q1", "q3"),),
    "band": (("lo", "hi"), ("min", "max")),
}

#: Shapes whose single value sits on the edge away from the axis baseline.
BASELINE_SHAPES: frozenset[MarkShape] = frozenset({"rect"})

#: Shapes whose value is not on an edge of their box. A cell carries a colour, and a
#: colour scale is quantised and non-linear, so nothing about it can be measured. A
#: sector carries an angle, which is measured -- but around the panel's circle rather
#: than along one of its axes, so it takes its own path through the check.
NO_GEOMETRY: frozenset[MarkShape] = frozenset({"sector", "cell"})

#: Samples the arc walk takes around a full turn. The smallest share a wedge is
#: allowed to hold is two percent, which is a little over seven degrees, so a fifth
#: of a degree puts thirty-six samples inside the narrowest wedge that can be drawn.
ARC_SAMPLES = 1800

#: Radii the walk samples at, as the fraction of the way from the inner edge of the
#: filled band to its outer edge. Seven of them, and what is looked for is not one
#: colour but agreement: **a boundary between two wedges is radial, so it shows at
#: every radius**, while a hatch line, the stroke along the arc and a value label each
#: show at one radius and not at its neighbours. The middle of the band is left alone
#: because that is where a value label sits.
#: All six sit in the outer part of the band, and for two reasons: near the centre the
#: whole circle is a few dozen pixels around, so two boundaries land on the same pixel
#: and neither is found; and the value label sits at the middle of the band.
ARC_RADII = (0.62, 0.68, 0.74, 0.80, 0.86, 0.92)

#: How many of the radii have to change colour at the same angle before it counts as a
#: boundary. All six, because a wedge boundary really is at all six and nothing else
#: is: a dotted hatch puts a change at four of them often enough to be counted, and a
#: pie then comes back cut into three times as many pieces as it has.
BOUNDARY_RADII = len(ARC_RADII)

#: How far apart two radii may put the same boundary, in samples. A radial line is not
#: exactly radial once it is rasterised, and the seven radii are ten pixels apart.
BOUNDARY_SLOP = 3

#: The smallest share a pie may draw, from the chart table. A span below it is not a
#: wedge but what is left between two of them -- an edge stroke and its anti-aliasing.
MIN_SHARE = 0.02

#: The largest turn a wedge may span and still be identified by its box. Past half a
#: circle a wedge reaches every quadrant crossing, so its bounds are the bounds of the
#: whole circle and its neighbours' bounds are the same -- the box stops saying which
#: wedge it belongs to, and a measurement matched on it is a guess.
MAX_IDENTIFIABLE_TURN = 180.0

#: Pixels a measured wedge's bounds may sit away from the recorded box before the two
#: are taken to be different wedges.
#:
#: Tight on purpose. A measurement whose wedge was identified wrongly is worse than no
#: measurement at all, because the self-check discards a figure over it. Every pie one
#: run drew, each under forty style vectors -- six hundred wedges -- comes back as 366
#: measured (61%), 233 the walk says it cannot measure (39%), and one wrong (0.2%).
#: Widening this to eight pixels trades a handful of the second group for several times
#: as many of the third.
WEDGE_MATCH = 2.5


def load_image(path: str | Path) -> np.ndarray:
    """Load as RGB uint8, shaped (H, W, 3) and indexed [y, x]."""
    from PIL import Image

    return np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8)


def _crop(img: np.ndarray, box: Box) -> np.ndarray:
    h, w = img.shape[:2]
    x0, y0 = int(np.floor(max(box.x0, 0))), int(np.floor(max(box.y0, 0)))
    x1, y1 = int(np.ceil(min(box.x1, w))), int(np.ceil(min(box.y1, h)))
    if x1 <= x0 or y1 <= y0:
        return img[:0, :0]
    return img[y0:y1, x0:x1]


# ---------------------------------------------------------------- colour

def color_fraction(img: np.ndarray, box: Box, rgb: RGB,
                   tolerance: int = COLOR_TOLERANCE) -> float:
    """Fraction of the box close to this colour."""
    patch = _crop(img, box)
    if patch.size == 0:
        return 0.0
    close = np.all(np.abs(patch.astype(np.int16) - np.array(rgb, np.int16)) <= tolerance, axis=-1)
    return float(close.mean())


def background_of(img: np.ndarray, box: Box) -> RGB:
    """The panel's background colour: the most common colour inside it.

    Read off the image rather than off the style vector, because the same check runs
    on a model's answer, where there is no style vector. Taken over the whole panel
    rather than one strip of it: a stacked area fills the bottom, a heatmap fills
    everything, and any one strip is a guess about which part a figure leaves empty.
    """
    return background_coverage(img, box)[0]


def background_coverage(img: np.ndarray, box: Box) -> tuple[RGB, float]:
    """The panel's background colour and how much of the panel it covers.

    Looked for along the top and the two sides rather than over the whole panel: a
    plotting area fills from its baseline, so a stacked area can cover most of the
    panel while leaving that band empty, and taking the commonest colour overall
    would then call the fill the background and every mark drawn in it empty.

    The share is measured over the whole panel, and it matters as much as the colour.
    A panel painted edge to edge -- a heatmap -- has no background at all, and asking
    whether a box on it holds anything is a question with no discriminating answer.
    Better said outright than answered wrongly.
    """
    patch = _crop(img, box)
    if patch.size == 0:
        return ((255, 255, 255), 1.0)
    h, w = patch.shape[:2]
    top = max(1, int(h * BACKGROUND_TOP))
    side = max(1, int(w * BACKGROUND_SIDE))
    band = np.concatenate([patch[:top].reshape(-1, 3),
                           patch[top:, :side].reshape(-1, 3),
                           patch[top:, -side:].reshape(-1, 3)])
    values, counts = np.unique(band[::BACKGROUND_STEP], axis=0, return_counts=True)
    rgb = tuple(int(v) for v in values[int(np.argmax(counts))])
    whole = patch[::BACKGROUND_STEP, ::BACKGROUND_STEP].astype(np.int16)
    same = np.all(np.abs(whole - np.array(rgb, np.int16)) <= INK_TOLERANCE, axis=-1)
    return (rgb, float(same.mean()))  # type: ignore[return-value]


def ink_fraction(img: np.ndarray, box: Box, background: RGB = (255, 255, 255),
                 tolerance: int = INK_TOLERANCE) -> float:
    """Fraction of the box that is not background. Needs no knowledge of the mark colour."""
    patch = _crop(img, box)
    if patch.size == 0:
        return 0.0
    diff = np.abs(patch.astype(np.int16) - np.array(background, np.int16))
    return float(np.any(diff > tolerance, axis=-1).mean())


def box_has_content(img: np.ndarray, box: Box, rgb: RGB | None = None,
                    min_fraction: float = MIN_CONTENT_FRACTION,
                    background: RGB = (255, 255, 255)) -> bool:
    """Is there anything inside the box. With a colour, look for that colour; without
    one, look for anything that is not the background."""
    frac = color_fraction(img, box, rgb) if rgb is not None else ink_fraction(img, box, background)
    return frac >= min_fraction


# ---------------------------------------------------------------- geometry

def _at_least(box: Box, size: float) -> Box:
    """The box, grown around its own centre until it is at least this big.

    A mark one pixel across has too few pixels to judge on its own, and the ink
    around where it should be is the evidence that it was drawn at all.
    """
    dx = max(0.0, (size - box.width) / 2)
    dy = max(0.0, (size - box.height) / 2)
    return Box(box.x0 - dx, box.y0 - dy, box.x1 + dx, box.y1 + dy)


def _draws_nothing(mark: Mark) -> bool:
    """Whether this mark stands for nothing: a bin with no rows, a segment of zero."""
    for key in ("count", "value"):
        if key in mark.values:
            return abs(mark.values[key]) < EMPTY_VALUE
    return False


def _anchor_pixel(box: Box, anchor: Anchor) -> float:
    return {
        "top": box.y0,
        "bottom": box.y1,
        "left": box.x0,
        "right": box.x1,
        "center_x": (box.x0 + box.x1) / 2,
        "center_y": (box.y0 + box.y1) / 2,
    }[anchor]


def axis_pair(axis: Axis) -> AxisPair:
    return (axis.value_range, axis.pixel_range)


def axis_of(panel: Panel, mark: Mark) -> Axis | None:
    """The axis this mark says its value was measured against."""
    return panel.axis(mark.value_axis)


def value_edges(axis: Axis, orientation: Orientation = "vertical") -> tuple[Anchor, Anchor]:
    """Which edge of a box carries the lower value and which the higher.

    Read off the axis rather than assumed, because a value axis may run either way
    and a horizontal bar chart puts it across the image instead of up it.
    """
    (v0, v1), (p0, p1) = axis.value_range, axis.pixel_range
    grows_with_pixel = (p1 - p0) * (1.0 if v1 >= v0 else -1.0) > 0
    if orientation == "vertical":
        return ("top", "bottom") if grows_with_pixel else ("bottom", "top")
    return ("left", "right") if grows_with_pixel else ("right", "left")


def _baseline_pixel(axis: Axis, orientation: Orientation) -> float:
    """The pixel a rectangle grows out of: zero if the axis covers it, else the
    end of the axis nearest zero."""
    lo, hi = sorted(axis.value_range)
    base = min(max(0.0, lo), hi)
    return value_to_pixel(base, axis.value_range, axis.pixel_range, axis.scale)


def orientation_of(mark: Mark) -> Orientation:
    """Which way this mark's value runs, from the axis it says it was measured against.

    Read off the record rather than off the style, so that a type drawn across the
    image whatever the style asks -- a funnel -- is measured the way it was drawn.
    """
    return "horizontal" if mark.value_axis == "x" else "vertical"


def geometric_anchors(mark: Mark, axis: Axis | None,
                      orientation: Orientation | None = None) -> dict[str, tuple[str, Anchor]]:
    """Which of a mark's value keys sit on an edge of its box, and which edge.

    Only these keys can be checked against the pixels. A stacked segment's `value`
    is the difference between two edges rather than an edge; a histogram's bin
    edges would pin the bar width rather than the count; a sector's share is an
    angle. Leaving them out is what keeps the check from discarding figures over
    quantities its geometry was never going to reach.
    """
    if mark.mark_shape in NO_GEOMETRY or mark.channel == "printed" or axis is None:
        return {}
    orientation = orientation or orientation_of(mark)
    low, high = value_edges(axis, orientation)
    out: dict[str, tuple[str, Anchor]] = {}

    for small, large in SPANNING_KEYS.get(mark.mark_shape, ()):
        if small in mark.values and large in mark.values:
            a, b = (low, high) if mark.values[small] <= mark.values[large] else (high, low)
            return {small: (VALUE_AXIS, a), large: (VALUE_AXIS, b)}

    if mark.mark_shape in BASELINE_SHAPES:
        key = "count" if "count" in mark.values else "value"
        if key in mark.values:
            base = _baseline_pixel(axis, orientation)
            far = max((low, high), key=lambda e: abs(_anchor_pixel(mark.box, e) - base))
            out[key] = (VALUE_AXIS, far)
        return out

    centre: Anchor = "center_y" if orientation == "vertical" else "center_x"
    cross: Anchor = "center_x" if orientation == "vertical" else "center_y"
    if "y" in mark.values:                      # a per-row point carries both coordinates
        out["y"] = (VALUE_AXIS, centre)
        out["x"] = (CROSS_AXIS, cross)
    elif "value" in mark.values:
        out["value"] = (VALUE_AXIS, centre)
    return out


# ---------------------------------------------------------------- sectors

def _wedge_bounds(centre: tuple[float, float], inner: float, outer: float,
                  start: float, end: float) -> Box:
    """The axis-aligned bounds of a wedge, from the circle and the two angles.

    The same arithmetic the drawer used to record the box, repeated here so that a
    run of pixels found on the arc can be matched back to the mark it belongs to.
    Bounds are reached at one of the wedge's four corners or where its arc crosses a
    quarter turn, which is the furthest out an arc gets.
    """
    angles = [start, end]
    turn = math.ceil(start / 90.0) * 90.0
    while turn < end:
        angles.append(turn)
        turn += 90.0
    points = [(centre[0] + r * math.cos(math.radians(a)),
               centre[1] - r * math.sin(math.radians(a)))
              for a in angles for r in (inner, outer)]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return Box(min(xs), min(ys), max(xs), max(ys))


def _arc_reads(img: np.ndarray,
               circle: tuple[float, float, float, float]) -> list[np.ndarray]:
    """The colour at every step around the circle, once per radius."""
    cx, cy, inner, outer = circle
    h, w = img.shape[:2]
    radians = np.radians(np.arange(ARC_SAMPLES) * (360.0 / ARC_SAMPLES))
    reads = []
    for share in ARC_RADII:
        r = inner + share * (outer - inner)
        xs = np.clip(np.rint(cx + r * np.cos(radians)).astype(int), 0, w - 1)
        ys = np.clip(np.rint(cy - r * np.sin(radians)).astype(int), 0, h - 1)
        reads.append(img[ys, xs])
    return reads


def _boundaries(reads: list[np.ndarray]) -> list[int]:
    """Where one wedge ends and the next begins, as sample indices.

    **A boundary between two wedges is radial**, so a colour change there happens at
    every radius at the same angle. Everything else drawn on a wedge is not radial: a
    hatch line crosses one radius here and another there, the stroke along the arc
    touches only the outermost, and a value label sits at one radius band. Asking for
    agreement across the radii separates the two without knowing anything about what
    was drawn -- which is what makes it hold under a hatch, a shadow, an edge in a
    darkened fill colour, and any palette.

    Segmenting by colour instead worked until a fill and its own darkened edge both
    covered enough of the circle to look like two wedges, and then a pie came back cut
    into more pieces than it had.
    """
    votes = np.zeros(ARC_SAMPLES, dtype=int)
    for reads_at_radius in reads:
        changed = np.any(reads_at_radius != np.roll(reads_at_radius, 1, axis=0), axis=-1)
        near = np.zeros(ARC_SAMPLES, dtype=bool)
        for shift in range(-BOUNDARY_SLOP, BOUNDARY_SLOP + 1):
            near |= np.roll(changed, shift)
        votes += near
    strong = votes >= BOUNDARY_RADII
    if not strong.any() or strong.all():
        # Nothing changes colour anywhere, or everything does. A pie with one wedge
        # reads as the first, and a circle covered by a fine hatch or a colour ramp as
        # the second; neither leaves an interior a wedge could be measured across.
        return []
    # Each stretch of winning samples is one boundary, taken at its middle. The stretch
    # that straddles the start of the walk is one boundary too, so the walk is rotated
    # to begin on a sample that is not in one.
    start = int(np.flatnonzero(~strong)[0])
    rolled = np.roll(strong, -start)
    out: list[int] = []
    i = 0
    while i < ARC_SAMPLES:
        if not rolled[i]:
            i += 1
            continue
        j = i
        while j < ARC_SAMPLES and rolled[j]:
            j += 1
        out.append((start + (i + j - 1) // 2) % ARC_SAMPLES)
        i = j
    return sorted(out)


def _arc_runs(reads: list[np.ndarray], background: RGB) -> list[tuple[float, float]]:
    """The angular spans of the wedges the pixels show, in degrees.

    The stretches between neighbouring boundaries, with the ones too small to be a
    wedge folded into the neighbour they sit against: an edge stroke and its
    anti-aliasing produce a boundary at each side of themselves, and what lies between
    belongs to neither wedge. The smallest share a pie may draw is what "too small"
    means, so the number comes from the chart table rather than from tuning.
    """
    step = 360.0 / ARC_SAMPLES
    cuts = _boundaries(reads)
    if len(cuts) < 2:
        return []
    spans = [(cuts[i], cuts[i + 1] if i + 1 < len(cuts) else cuts[0] + ARC_SAMPLES)
             for i in range(len(cuts))]
    floor = MIN_SHARE * ARC_SAMPLES
    kept = [(a, b) for a, b in spans if b - a >= floor]
    if not kept:
        return []
    ink = np.array(background, np.int16)
    middle = reads[len(reads) // 2]
    kept = [(a, b) for a, b in kept
            if np.any(np.abs(middle[((a + b) // 2) % ARC_SAMPLES].astype(np.int16) - ink)
                      > INK_TOLERANCE)]
    if len(kept) < 2:
        return [(a * step, b * step) for a, b in kept]

    out: list[tuple[float, float]] = []
    for i, (a, b) in enumerate(kept):
        before = kept[i - 1][1] - (ARC_SAMPLES if i == 0 else 0)
        after = kept[(i + 1) % len(kept)][0] + (ARC_SAMPLES if i + 1 == len(kept) else 0)
        lo = a - (a - before) / 2 if a > before else float(a)
        hi = b + (after - b) / 2 if after > b else float(b)
        out.append((lo * step, hi * step))
    return out


def sector_share(img: np.ndarray, mark: Mark, panel: Panel,
                 background: RGB | None = None) -> float | None:
    """The share one wedge holds, measured off the pixels.

    Read the way a bar's height is read: from the page geometry the panel wrote down
    and the ink in the image, never from the value being checked. The circle is
    walked once, the runs of one colour on it are the wedges, and the run whose own
    bounds land on this mark's recorded box is this mark's. Its span over a full turn
    is the share.

    Nothing comes back when no run matches. Two neighbouring wedges given the same
    colour by a palette that ran out come back as one run, and one run standing for
    two wedges is a measurement of neither -- so the check says it could not measure
    rather than returning a number that is twice what it should be. Nothing comes back
    for a wedge past half a circle either: it reaches every quadrant crossing, so its
    bounds are the whole circle's and the box no longer says which wedge it is.
    """
    if panel.circle is None:
        return None
    if background is None:
        background = background_of(img, panel.box)
    cx, cy, inner, outer = panel.circle
    runs = _arc_runs(_arc_reads(img, panel.circle), background)
    matched: list[tuple[float, float]] = []
    for lo, hi in runs:
        if hi - lo > MAX_IDENTIFIABLE_TURN:
            continue
        bounds = _wedge_bounds((cx, cy), inner, outer, lo, hi).clip_to(panel.box)
        gap = max(abs(a - b) for a, b in zip(bounds.as_tuple(), mark.box.as_tuple()))
        matched.append((gap, (hi - lo) / 360.0))
    matched.sort()
    # Nothing near enough, or two runs both near enough: that is an identification and
    # not a measurement, and the span of whichever came first is not an answer.
    if not matched or matched[0][0] > WEDGE_MATCH:
        return None
    if len(matched) > 1 and matched[1][0] <= WEDGE_MATCH:
        return None
    return matched[0][1]


def value_from_box(box: Box, axis: AxisPair, anchor: Anchor,
                   scale: Literal["linear", "log"] = "linear") -> float:
    """Convert a box back into a value using the panel's value and pixel ranges."""
    value_range, pixel_range = axis
    return pixel_to_value(_anchor_pixel(box, anchor), value_range, pixel_range, scale)


def value_agrees(measured: float, claimed: float, slack: float) -> bool:
    """`slack` is absolute: what the pixels can resolve, not a fraction of the claim."""
    return abs(measured - claimed) <= max(slack, ABSOLUTE_FLOOR)


@dataclass(frozen=True)
class Verification:
    """The outcome of both geometric checks. Computable without ground truth."""

    has_content: bool
    value_agrees: bool | None            # None when nothing could be measured
    measured: dict[str, float] = None    # type: ignore[assignment]
    content_fraction: float = 0.0
    reason: str = ""

    def __post_init__(self) -> None:
        if self.measured is None:
            object.__setattr__(self, "measured", {})

    @property
    def ok(self) -> bool:
        return self.has_content and self.value_agrees is not False


def check_mark(img: np.ndarray, mark: Mark, panel: Panel, *,
               orientation: Orientation | None = None, slack: float | None = None,
               quantum: float = 0.0, background: RGB | None = None,
               coverage: float | None = None,
               min_fraction: float = MIN_CONTENT_FRACTION) -> Verification:
    """Both geometric checks on one claimed `(key, value, box)`.

    The renderer's record and a model's answer go through this same function; the
    only difference is who wrote the mark.

    With no `slack` given, each value key is judged against what its own axis can
    resolve. That has to be per key: a scatter point is measured against two axes at
    once, and one of them may be a hundred times finer than the other.
    """
    if background is None or coverage is None:
        background, coverage = background_coverage(img, panel.box)
    # A printed value is the glyphs, not the cell they sit in, so that is the box
    # its content is looked for in and glyph coverage is what it is judged against.
    printed = mark.channel == "printed" and mark.label_box is not None
    where = _at_least(mark.label_box if printed else mark.box, MIN_INTERIOR)
    frac = ink_fraction(img, where, background)
    if printed:
        min_fraction = MIN_TEXT_FRACTION
    elif mark.mark_shape == "point":
        min_fraction = MIN_POINT_FRACTION
    if _draws_nothing(mark):
        has_content, why = True, "the mark stands for nothing, so nothing was drawn"
    elif coverage < MIN_BACKGROUND_COVERAGE and not printed:
        has_content, why = True, "the panel is painted edge to edge, so it has no background"
    else:
        has_content, why = frac >= min_fraction, ""

    if mark.mark_shape == "sector" and not printed:
        return _check_sector(img, mark, panel, has_content, frac, why, background, slack)

    axis = axis_of(panel, mark)
    anchors = geometric_anchors(mark, axis, orientation)
    if not anchors:
        return Verification(has_content, None, {}, frac,
                            why or ("" if axis is not None else "the mark names no value axis"))

    measured: dict[str, float] = {}
    agrees = True
    readings = 2 if len(anchors) > 1 else 1
    for key, (which, anchor) in anchors.items():
        target = axis if which == VALUE_AXIS else panel.axis("x")
        if target is None:
            continue
        got = value_from_box(mark.box, axis_pair(target), anchor, target.scale)
        measured[key] = got
        allowed = slack if slack is not None else _slack(target, quantum, readings)
        agrees = agrees and value_agrees(got, mark.values[key], allowed)
    if not measured:
        return Verification(has_content, None, {}, frac, why or "no axis to measure against")
    return Verification(has_content, agrees, measured, frac, why)


def _check_sector(img: np.ndarray, mark: Mark, panel: Panel, has_content: bool,
                  frac: float, why: str, background: RGB,
                  slack: float | None) -> Verification:
    """The second check on a wedge: the share the pixels give against the share claimed.

    A wedge holds two numbers and only one of them is on the page. The angle gives
    the share; turning that into the value would need the total, which a pie writes
    nowhere -- so the share is what is checked and the value is left alone. A mark
    whose share the walk could not isolate returns no verdict, the same as one whose
    encoding cannot be measured at all.
    """
    from ..registry.channels import ABSOLUTE_FLOOR, angular_epsilon

    if "share" not in mark.values:
        return Verification(has_content, None, {}, frac, why or "the wedge claims no share")
    measured = sector_share(img, mark, panel, background)
    if measured is None:
        return Verification(has_content, None, {}, frac,
                            why or "no run of pixels on the circle matches this wedge")
    radius = panel.radius or 0.0
    allowed = slack if slack is not None else max(angular_epsilon(radius), ABSOLUTE_FLOOR)
    return Verification(has_content, value_agrees(measured, mark.values["share"], allowed),
                        {"share": measured}, frac, why)


def _slack(axis: Axis, quantum: float, readings: int) -> float:
    """What a value measured against this axis is allowed to be out by."""
    from ..registry.channels import geometric_slack

    return geometric_slack(axis_pair(axis), quantum=quantum, readings=readings)
