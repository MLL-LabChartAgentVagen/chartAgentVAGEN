"""Sector marks: the pie, drawn solid or as a ring.

One file per mark shape rather than per chart type. Only one type draws a sector,
and what makes it a shape of its own is not the outline but what carries the value:
the angle a wedge subtends. An angle is not an edge of anything, so a sector's box
says where the wedge is and never what it is worth -- which is why a pie's value is
either printed on it or estimated, and why a labelled sector is the only exact one.

The wedges are laid out in pixels rather than in data coordinates. A circle is round
only where one data unit is as many pixels across as it is down, and asking the
plotting library for that lets it resize the plotting area after the frame has
already recorded where it was.
"""

from __future__ import annotations

import math

from matplotlib.patches import Wedge
from matplotlib.transforms import IdentityTransform

from ...common.geometry import Box
from ..style import TEXT_COLOR, hex_of
from . import labels
from . import frame as frame_mod
from .frame import Frame

#: Radius of the pie, as a fraction of the shorter side of the plotting area. What
#: is left of that side is the room the category names are written in.
RADIUS = 0.36

#: Where the category name sits, as a multiple of the radius: just outside the arc.
#: A value label goes half way between the hole and the rim instead, which is the
#: middle of what was actually filled whether or not there is a hole.
NAME_RADIUS = 1.08

#: The hole in the middle of a ring, as a fraction of the radius. A ring and a solid
#: pie hold the same value in the same angle, so this is a style value and not a
#: second chart type.
DONUT_HOLE = 0.55

#: Where the first sector starts. Twelve o'clock, running clockwise from there, in
#: the order the values came out of the projection.
START_ANGLE = 90.0


def _at(centre: tuple[float, float], radius: float, degrees: float) -> tuple[float, float]:
    """A point on a circle, in pixels with the origin at the top left."""
    angle = math.radians(degrees)
    return (centre[0] + radius * math.cos(angle), centre[1] - radius * math.sin(angle))


def _wedge_box(centre: tuple[float, float], inner: float, outer: float,
               start: float, end: float) -> Box:
    """The axis-aligned bounds of one wedge, in pixels.

    Taken from the wedge rather than from the circle it was cut out of: a sector
    spanning a quarter of the circle covers a quarter of it, and a box holding the
    whole circle would be three quarters background. The bounds are reached either
    at one of the wedge's four corners or where its arc crosses a quarter turn,
    which is the furthest out an arc gets.
    """
    angles = [start, end]
    turn = math.ceil(start / 90.0) * 90.0
    while turn < end:
        angles.append(turn)
        turn += 90.0
    points = [_at(centre, r, a) for a in angles for r in (inner, outer)]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return Box(min(xs), min(ys), max(xs), max(ys))


def draw_pie(ctx, frame: Frame) -> None:
    """One wedge per key, around the centre of the plotting area, in data order.

    The tick furniture is taken down: a pie has nothing to measure along an axis, so
    ticks and spines would invite a reader to try. The axes themselves are still
    recorded, because the frame records one value axis for every panel, and the two
    axis titles it wrote stay on the page so that what the record says is on the page
    is what is drawn on it. A sector's value axis carries nothing measurable -- that
    is exactly why the channel is an angle.
    """
    ax = ctx.panel.ax
    frame_mod.bare(ax)

    rect = ctx.panel.rect
    centre = ((rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2)
    radius = RADIUS * min(rect.width, rect.height)
    hole = radius * DONUT_HOLE if ctx.style.donut else 0.0
    # The circle goes on the panel, because a wedge's value is an angle and an angle
    # needs a centre to be measured from. Without it the check that reads a value
    # back off the pixels has nothing to work with on a pie, and the readability rule
    # has no radius to pin the share against.
    ctx.panel.circle = (centre[0], centre[1], hole, radius)

    mask = labels.mask(ctx, len(ctx.view.data))
    entries = []
    turn = START_ANGLE
    for i, datum in enumerate(ctx.view.data):
        start, end = turn - 360.0 * datum.values["share"], turn
        mid = (start + end) / 2
        ax.add_patch(Wedge(
            (centre[0], ctx.panel.image_height - centre[1]), radius, start, end,
            width=radius - hole, transform=IdentityTransform(), zorder=2,
            **ctx.shape_kwargs(ctx.colour_for(datum.key))))
        box = _wedge_box(centre, hole, radius, start, end).clip_to(ctx.panel.rect)
        index = ctx.panel.add_mark(ctx.view.full_key(datum), datum.values, box, "angle",
                                   mark_shape="sector", value_axis=ctx.value_axis,
                                   key_src=ctx.view.key_src(datum))
        _name(ctx, _at(centre, radius * NAME_RADIUS, mid), mid, datum.key[0])
        if mask[i]:
            x, y = _in_data(ctx, _at(centre, (hole + radius) / 2, mid))
            entries.append((index, x, y, datum.values["value"],
                            ctx.colour_for(datum.key)))
        turn = start
    labels.write_value_labels(ctx, entries)


def _name(ctx, at: tuple[float, float], degrees: float, text: str) -> None:
    """The category name, written beside its sector and recorded where it landed.

    A pie has no legend and no category ticks, so the name printed next to the wedge
    is the only place its key can be read off the image. That is what the record's
    `inline_label` key source says, and this is the text it points at.
    """
    artist = ctx.panel.ax.annotate(
        text, xy=(at[0], ctx.panel.image_height - at[1]), xycoords="figure pixels",
        ha="left" if math.cos(math.radians(degrees)) >= 0 else "right", va="center",
        fontsize=ctx.style.font_size - 1, color=hex_of(TEXT_COLOR))
    ctx.canvas.defer(artist, lambda box: ctx.canvas.add_element(box, "legend_title", text))


def _in_data(ctx, at: tuple[float, float]) -> tuple[float, float]:
    """A pixel point in the data coordinates the label writer anchors to."""
    x, y = ctx.panel.ax.transData.inverted().transform(
        (at[0], ctx.panel.image_height - at[1]))
    return (float(x), float(y))
