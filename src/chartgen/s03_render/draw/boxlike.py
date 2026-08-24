"""Box marks: a five-number summary drawn as a box between the quartiles.

One file per mark shape rather than per chart type. What makes this shape its own is
which two of its five numbers the box spans. The rectangle runs between the
quartiles while the whiskers reach the extremes, so the recorded box is the
interquartile rectangle and nothing else: a box drawn out to the whisker tips would
be mostly empty, and reading its edges back would return the quartiles while the
record called them the smallest and the largest value.

Rows lying outside the whiskers are drawn one at a time. Each is its own mark, with
its own key and a single value, because that is exactly what it is on the page.
"""

from __future__ import annotations

from matplotlib.patches import Rectangle

from ...common.geometry import Box
from ...interfaces.figure import Datum
from ..style import BACKGROUND, RGB, TEXT_COLOR, hex_of
from .frame import Frame

#: Width of the cap on the end of a whisker, as a fraction of the box width. The
#: median line takes the full width, because it is one of the five numbers and the
#: caps are only there to say where a whisker stops.
CAP_WIDTH = 0.6

#: Side of the square recorded for an outlier, in pixels. It is the drawn marker's
#: own size: any larger and the box would be mostly background.
OUTLIER_SIZE = 8.0

#: Luminance below which a fill is dark enough that a line drawn on it has to be
#: light instead of dark.
DARK = 140.0


def draw_box(ctx, frame: Frame) -> None:
    """One box per group, with whiskers, plus one point per outlying row.

    No value is written beside a box. A box holds five numbers and a label next to it
    would name none of them in particular, so printing one would claim an exactness
    about a quantity a reader cannot tell apart from its four neighbours.

    The value always runs up the image: the frame turns rectangles and nothing else.
    """
    for datum in ctx.view.data:
        if "q1" in datum.values:
            _box(ctx, frame, datum)
        else:
            _outlier(ctx, frame, datum)


def _box(ctx, frame: Frame, datum: Datum) -> None:
    """The interquartile rectangle, its median, and the whiskers out to the extremes.

    Drawn and recorded from the same two numbers, and only those two: the rectangle
    is what the record's box says it is.
    """
    values = datum.values
    ax, width = ctx.panel.ax, ctx.style.bar_width
    at = frame.position(datum.key[0])
    colour = ctx.colour_for(datum.key)
    cap = width * CAP_WIDTH / 2

    for edge, quartile in ((values["min"], values["q1"]), (values["max"], values["q3"])):
        ax.plot([at, at], [quartile, edge], color=hex_of(TEXT_COLOR), linewidth=1.0, zorder=1)
        ax.plot([at - cap, at + cap], [edge, edge], color=hex_of(TEXT_COLOR),
                linewidth=1.0, zorder=1)
    ax.add_patch(Rectangle((at - width / 2, values["q1"]), width,
                           values["q3"] - values["q1"], zorder=2,
                           **ctx.shape_kwargs(colour)))
    ax.plot([at - width / 2, at + width / 2], [values["median"], values["median"]],
            color=hex_of(_on(colour)), linewidth=1.6, zorder=3)

    box = ctx.panel.box_from_data(at - width / 2, values["q1"], at + width / 2,
                                  values["q3"]).clip_to(ctx.panel.rect)
    ctx.panel.add_mark(ctx.view.full_key(datum), values, box, "position",
                       mark_shape="boxlike", value_axis=ctx.value_axis,
                       key_src=ctx.view.key_src(datum))


def _outlier(ctx, frame: Frame, datum: Datum) -> None:
    """One row outside the whiskers, drawn as its own point and boxed like one.

    It takes the colour of the group it belongs to rather than of its own key: the
    last segment of an outlier's key is its index within that group, which names
    nothing a palette could be keyed on and nothing that is written on the page.
    """
    at = frame.position(datum.key[0])
    value = datum.values["value"]
    ctx.panel.ax.plot([at], [value], marker="o", linestyle="none",
                      markersize=OUTLIER_SIZE * 72.0 / ctx.style.dpi,
                      color=hex_of(ctx.colour_for(datum.key[:-1])),
                      markeredgewidth=0.0, zorder=3)
    x, y = ctx.panel.to_pixel(at, value)
    half = OUTLIER_SIZE / 2
    ctx.panel.add_mark(ctx.view.full_key(datum), datum.values,
                       Box(x - half, y - half, x + half, y + half).clip_to(ctx.panel.rect),
                       "position", mark_shape="point", value_axis=ctx.value_axis,
                       key_src=ctx.view.key_src(datum))


def _on(rgb: RGB) -> RGB:
    """A line that shows up on this fill: the page background on a dark one, the text
    colour on a light one.

    The palettes run from dark to light, so a median line in any one fixed colour
    disappears into half the boxes of a batch.
    """
    return BACKGROUND if 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2] < DARK else TEXT_COLOR
