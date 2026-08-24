"""Writing the value next to a mark, and measuring where it landed.

A printed value is exact, so whether a mark got one changes what is asked of the
model reading it. Which marks get one is a style dimension with five settings, and
each of them is a different placement, not a different amount of the same thing.

Every label is deferred and measured in one pass. Asking the plotting library for
the box of a label as it is written redraws the whole figure, and a figure with
four hundred marks would redraw four hundred times.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Sequence

from matplotlib.patheffects import withStroke

from ...common.geometry import Box
from ..style import BACKGROUND, RGB, TEXT_COLOR, format_number, hex_of

#: Luminance below which a fill is dark enough that text on it has to be light.
DARK = 140.0

#: Luminance a label written on the page has to stay under. A series colour lighter
#: than this is darkened towards black at the same hue rather than used as it is: a
#: label nobody can read is worse than one that says nothing about which series it
#: belongs to.
MAX_ON_PAGE = 150.0

#: Distance from a mark to a label written just outside it, in points.
OUTSIDE_OFFSET = 5.0

#: Distance for the two settings that push the label clear of the mark.
CLEAR_OFFSET = 16.0

#: Width of the halo drawn behind a label written outside its mark, in points.
HALO = 2.5


def on(fill: RGB | None) -> RGB:
    """A text colour that can be read on this fill.

    A label printed inside a mark is claimed to be exact -- a written value is matched
    with no tolerance at all -- so a label nobody can read is worse than no label.
    The palettes run from dark to light, and one fixed ink disappears into half of them.
    """
    if fill is None:
        return TEXT_COLOR
    luminance = 0.299 * fill[0] + 0.587 * fill[1] + 0.114 * fill[2]
    return BACKGROUND if luminance < DARK else TEXT_COLOR


def _luminance(colour: RGB) -> float:
    return 0.299 * colour[0] + 0.587 * colour[1] + 0.114 * colour[2]


def outside_ink(ctx, fill: RGB | None) -> RGB:
    """The colour a label written clear of its mark is set in.

    One ink for the whole panel is enough while one view is drawn in it: every label
    sits beside the only kind of mark there is. Two views in one plotting area put
    two sets of labels between the same marks, and one ink leaves a reader with
    nothing but position to decide which label belongs to which -- on a bar with a
    line over it, the bar's number and the line's number land beside each other and
    neither can be shown to belong to either.

    That is not a matter of appearance. A printed value is matched exactly, so an
    unattributable label hands two marks one answer that neither can be shown to
    carry. On an overlaid panel the label therefore takes its series colour, and it
    is darkened when that colour is too light to read against the page.
    """
    if fill is None or not ctx.overlaid:
        return TEXT_COLOR
    lum = _luminance(fill)
    if lum <= MAX_ON_PAGE:
        return fill
    scale = MAX_ON_PAGE / lum
    return (int(round(fill[0] * scale)), int(round(fill[1] * scale)),
            int(round(fill[2] * scale)))


def mask(ctx, n: int) -> list[bool]:
    """Which of n marks get their value written on them."""
    mode = ctx.style.value_labels
    if mode == "none":
        return [False] * n
    if mode == "some":
        return [i % 2 == 0 for i in range(n)]
    return [True] * n


def text_for(ctx, value: float) -> str:
    """The string a label carries: the recorded value, formatted, and nothing else.

    No arithmetic happens here, ever. A printed value is ground truth with no
    tolerance at all, so a label that is not exactly the number recorded for its mark
    is a wrong answer written into the data rather than a badly formatted one.
    """
    return format_number(value, ctx.style, ctx.unit())


def write_value_labels(ctx, entries: Sequence[tuple],
                       *, horizontal: bool = False) -> None:
    """Write one label per entry and record its box on the mark it belongs to.

    An entry is `(mark index, x in data space, y in data space, value)`, optionally
    followed by the fill the label will sit on. The five settings differ in where the
    label sits: inside the mark near its value edge, just outside that edge, or clear
    of it with a leader line drawn back.
    """
    mode = ctx.style.value_labels
    if mode == "none" or not entries:
        return
    # The label is written in the coordinates its mark was drawn in. A panel with two
    # value axes has two of them, and the same number is a different height on each:
    # placed against the first axis, a second-axis label lands beside somebody else's
    # mark, and a value outside the first axis's range cannot be placed at all -- the
    # plotting library then measures an empty box and the record claims a printed
    # value that is nowhere on the page.
    axes = (ctx.panel.right_ax if ctx.value_axis == "y_right"
            and ctx.panel.right_ax is not None else ctx.panel.ax)
    inside = mode in ("all", "some")
    offset = OUTSIDE_OFFSET if mode in ("all", "some", "outside") else CLEAR_OFFSET
    leader = mode == "outside_leader"

    for entry in entries:
        index, x, y, value = entry[:4]
        fill = entry[4] if len(entry) > 4 else None
        text = text_for(ctx, value)
        ink = on(fill) if inside else outside_ink(ctx, fill)
        dx, dy = ((offset, 0.0) if horizontal else (0.0, offset))
        if inside:
            dx, dy = (-dx, -dy)
        artist = axes.annotate(
            text, xy=(x, y), xytext=(dx, dy), textcoords="offset points",
            ha="left" if horizontal and not inside else ("right" if horizontal else "center"),
            va="center" if horizontal else ("top" if inside else "bottom"),
            rotation=ctx.style.value_label_rotation,
            fontsize=ctx.style.font_size - 1,
            color=hex_of(ink),
            # A label written outside its mark is given a halo in the page background.
            # "Outside the mark" is not "over the background": on a band, an area or a
            # dense scatter the position just past one mark is over another one, and a
            # printed value is claimed to be exact -- so one nobody can read is a wrong
            # answer written into the data rather than an ugly one.
            path_effects=None if inside else [withStroke(
                linewidth=HALO, foreground=hex_of(BACKGROUND))],
            # The leader takes the label's own ink: it is the line drawn to say which
            # mark the number belongs to, and drawn in a third colour it says less
            # than the label already does.
            arrowprops={"arrowstyle": "-", "linewidth": 0.6,
                        "color": hex_of(outside_ink(ctx, fill))} if leader else None)
        ctx.canvas.defer_label(artist, ctx.panel, _attach(ctx, index, text))


def _attach(ctx, index: int, text: str):
    """Put the measured box and the printed string onto the mark they belong to."""
    def then(box: Box) -> None:
        marks = ctx.panel.marks
        marks[index] = replace(marks[index], labeled=True, label_box=box, label_text=text)
    return then
