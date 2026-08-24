"""Rectangular marks: the bar family, histograms, waterfalls, funnels and range bars.

One file per mark shape rather than per chart type. Six types share this one, and
what separates them is only which two numbers the rectangle runs between:

    bar, grouped bar    the axis baseline and the value
    stacked bar         the running total before and after this segment
    waterfall           the same, along one sequence instead of inside a category
    histogram           the baseline and the count, across the width of the bin
    range bar           the smallest and the largest value of the group
    funnel              the baseline and the value, laid across a column of stages

Every rectangle is drawn and recorded in the same statement, so the box, the key and
the value are written from the same numbers.
"""

from __future__ import annotations

from typing import Sequence

from matplotlib.patches import Rectangle

from ...interfaces.figure import Datum
from . import labels
from .frame import Frame

#: Gap left between the bins of a histogram, as a fraction of the bin width.
BIN_GAP = 0.04


def _draw_rect(ctx, frame: Frame, *, pos: tuple[float, float],
               value: tuple[float, float], datum: Datum, colour) -> int:
    """One rectangle, drawn and recorded together.

    `pos` runs along the category axis and `value` along the value axis; which of
    them is horizontal is the frame's business, not this function's.
    """
    right = ctx.value_axis == "y_right"
    (x0, x1), (y0, y1) = ((value, pos) if frame.horizontal else (pos, value))
    box = ctx.panel.box_from_data(x0, y0, x1, y1, right).clip_to(ctx.panel.rect)
    ctx.panel.ax.add_patch(Rectangle(
        (x0, min(y0, y1)), x1 - x0, abs(y1 - y0),
        **ctx.shape_kwargs(colour, min(box.width, box.height)),
        transform=(ctx.panel.right_ax if right else ctx.panel.ax).transData, zorder=2))
    # `labeled` is not set here: whether this mark ends up with a printed value is
    # settled once the labels have been measured, because a label written across its
    # neighbour is dropped and its mark then carries no printed answer.
    return ctx.panel.add_mark(ctx.view.full_key(datum), datum.values, box, "length",
                              mark_shape="rect", value_axis=ctx.value_axis,
                              key_src=ctx.view.key_src(datum))


def _series_name(datum, series: Sequence[str]) -> str:
    """Which series a datum belongs to, empty when the panel draws only one."""
    return datum.key[1] if len(datum.key) >= 2 and series else ""


def _slots(ctx, series: Sequence[str],
           data: Sequence) -> dict[tuple[str, str], tuple[float, float]]:
    """Where each series sits inside one category slot, and how wide it is.

    A second key column is not always crossed with the first. A route belongs to one
    mode, so a mode's slot holds the routes under it and no others; divided by the
    whole series list, such a slot spends most of its width on sub-slots nothing is
    drawn in, and the bars that are there come out four pixels wide. Dividing by what
    the category actually holds gives bars of different widths between categories,
    which is what a nested second column looks like. Thickness across the category
    axis carries no value -- only length along the value axis does -- so no recorded
    answer moves with it.
    """
    width = ctx.style.bar_width
    here: dict[str, list[str]] = {}
    for datum in data:
        names = here.setdefault(datum.key[0], [])
        name = _series_name(datum, series)
        if name not in names:
            names.append(name)
    rank = {name: i for i, name in enumerate(series)}
    out: dict[tuple[str, str], tuple[float, float]] = {}
    for category, names in here.items():
        names.sort(key=lambda n: rank.get(n, len(rank)))
        each = width / len(names)
        for i, name in enumerate(names):
            out[(category, name)] = (-width / 2 + each * (i + 0.5), each)
    return out


def _baseline(frame: Frame, role: str) -> float:
    """The value a rectangle grows out of: zero if the axis covers it, else the end
    of the axis nearest zero."""
    lo, hi = frame.limits(role)
    return min(max(0.0, min(lo, hi)), max(lo, hi))


def draw_bar(ctx, frame: Frame) -> None:
    """The bar family: one rectangle per key, grown from the baseline or stacked."""
    data = [d for d in ctx.view.data]
    stacked = "cum_start" in ctx.view.data[0].values if data else False
    # Stacking and side-by-side placement are the two ways a second key column can be
    # shown, and they are alternatives: a stacked segment already says which series it
    # belongs to by where it sits in the column. Given a sub-slot as well, every
    # segment of a category starts one step to the right of the one below it and the
    # column reads as a staircase -- the shape a waterfall is drawn in.
    series = () if stacked else frame.series
    slots = _slots(ctx, series, data)
    base = _baseline(frame, ctx.value_axis)
    mask = labels.mask(ctx, len(data))
    entries = []

    for i, datum in enumerate(data):
        category = datum.key[0]
        name = _series_name(datum, series)
        centre, width = slots.get((category, name), (0.0, ctx.style.bar_width))
        pos = frame.position(category)
        lo, hi = ((datum.values["cum_start"], datum.values["cum_end"]) if stacked
                  else (base, datum.values["value"]))
        index = _draw_rect(ctx, frame, pos=(pos + centre - width / 2, pos + centre + width / 2),
                           value=(lo, hi), datum=datum,
                           colour=ctx.colour_for(datum.key))
        if mask[i]:
            entries.append(_entry(frame, index, pos + centre, hi, datum.values["value"],
                                  ctx.colour_for(datum.key)))
    labels.write_value_labels(ctx, entries, horizontal=frame.horizontal)


def draw_histogram(ctx, frame: Frame) -> None:
    """One rectangle per bin, across the width of the bin it counts.

    Every bin takes the same ink. A bin is named by where it sits on the value axis
    and by nothing else -- the key is not shown anywhere on the page and no legend is
    drawn -- so a colour per bin encodes nothing, and the palettes hold six entries
    against a type that allows thirty bins, which paints bins twenty-four units apart
    in the same ink. On a single-hue palette the run of shades also reads as an
    ordering of the counts that the counts do not have.
    """
    base = _baseline(frame, ctx.value_axis)
    mask = labels.mask(ctx, len(ctx.view.data))
    colour = ctx.colour_for(ctx.view.data[0].key) if ctx.view.data else None
    entries = []
    for i, datum in enumerate(ctx.view.data):
        lo, hi = datum.values["bin_lo"], datum.values["bin_hi"]
        gap = (hi - lo) * BIN_GAP
        index = _draw_rect(ctx, frame, pos=(lo + gap, hi - gap),
                           value=(base, datum.values["count"]), datum=datum,
                           colour=colour)
        if mask[i]:
            entries.append(_entry(frame, index, (lo + hi) / 2, datum.values["count"],
                                  datum.values["count"], colour))
    labels.write_value_labels(ctx, entries, horizontal=frame.horizontal)


def draw_waterfall(ctx, frame: Frame) -> None:
    """One rectangle per step, between the running total before and after it."""
    width = ctx.style.bar_width
    mask = labels.mask(ctx, len(ctx.view.data))
    entries = []
    for i, datum in enumerate(ctx.view.data):
        pos = frame.position(datum.key[0])
        lo, hi = datum.values["cum_start"], datum.values["cum_end"]
        index = _draw_rect(ctx, frame, pos=(pos - width / 2, pos + width / 2),
                           value=(lo, hi), datum=datum,
                           colour=ctx.colour_for(datum.key))
        if mask[i]:
            entries.append(_entry(frame, index, pos, hi, datum.values["value"],
                                  ctx.colour_for(datum.key)))
    labels.write_value_labels(ctx, entries, horizontal=frame.horizontal)


def draw_funnel(ctx, frame: Frame) -> None:
    """One rectangle per stage, laid across a column of stages.

    Drawn from the baseline rather than centred on it. A centred taper puts the two
    edges of every rectangle the same distance from zero, and then neither edge
    carries the value -- the width does, and a width cannot be read back off a box
    without knowing where the middle was meant to be.
    """
    draw_bar(ctx, frame)


def draw_range_bar(ctx, frame: Frame) -> None:
    """One rectangle per group, between its smallest and its largest value."""
    width = ctx.style.bar_width
    mask = labels.mask(ctx, len(ctx.view.data))
    entries = []
    for i, datum in enumerate(ctx.view.data):
        pos = frame.position(datum.key[0])
        index = _draw_rect(ctx, frame, pos=(pos - width / 2, pos + width / 2),
                           value=(datum.values["min"], datum.values["max"]), datum=datum,
                           colour=ctx.colour_for(datum.key))
        if mask[i]:
            entries.append(_entry(frame, index, pos, datum.values["max"],
                                  datum.values["max"], ctx.colour_for(datum.key)))
    labels.write_value_labels(ctx, entries, horizontal=frame.horizontal)


def _entry(frame: Frame, index: int, pos: float, edge: float, value: float, fill=None):
    """A label's anchor in data space, whichever way the value runs, and the fill it
    will be printed on."""
    at = (edge, pos) if frame.horizontal else (pos, edge)
    return (index, at[0], at[1], value, fill)
