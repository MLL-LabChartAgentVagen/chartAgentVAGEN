"""Cell marks: the heatmap and the table chart.

One file per mark shape rather than per chart type. Both lay a grid over the
plotting area and put one rectangle in each cell; what separates them is what the
rectangle carries. A heatmap carries the value in the cell's colour, which is
quantised and non-linear and cannot be read back to one percent. A table chart
prints the number inside the cell, which is exact and needs no geometry at all.

Neither value can be measured off a box, so all a cell's box has to do is hold the
cell it claims. Both record the rectangle they drew, and the table chart records the
box of the printed number as well, because that number is the value.

The grid is laid out in pixels. A cell is a share of the plotting area rather than a
span of anything the axes measure, and laying it out in data coordinates would give
a heatmap rows of unequal height as soon as the style asked for a log axis.
"""

from __future__ import annotations

from typing import Any

from matplotlib.patches import Rectangle
from matplotlib.transforms import IdentityTransform

from ...common.geometry import Box
from ...interfaces.style import StyleVector
from ..style import PALETTES, RGB, TEXT_COLOR, hex_of
from . import labels
from . import frame as frame_mod
from .frame import Frame

#: Fraction of the plotting area left clear above the grid.
#:
#: A grid is the one thing that tiles a whole panel, and the content check looks for
#: the panel's background along its top and sides. Left flush to the top, a grid
#: leaves nothing there but cells; the strip of clear panel is what keeps that check
#: answering a question about this figure rather than about the palest cell in it.
HEADROOM = 0.15


def draw_heatmap(ctx, frame: Frame) -> None:
    """One rectangle per key, coloured by its value: the first key segment across the
    image, the second one down it.

    The first segment runs across because the frame has already written it on the
    category ticks, and the columns line up with those ticks exactly; the second
    segment names the rows, which get their tick labels here. The frame recorded a
    value axis, as it does for every panel, and nothing reads it back: a cell's value
    is a colour, which is why the channel is a colour and not a position.
    """
    # Both of a heatmap's axes name categories, so the spines and the value
    # gridlines are taken down: they would be lines drawn across a scale that is not
    # there. The tick labels stay, because they are where the key is read off.
    ctx.panel.ax.grid(False)
    for spine in ctx.panel.ax.spines.values():
        spine.set_visible(False)
    # The value title moves off the vertical axis and into the space above the grid.
    # That axis carries the rows here, not the values, and the fixed margin beside it
    # holds either a title or a row name and not both. The frame recorded the artist
    # rather than a position, so what the record says about this title stays true.
    ctx.panel.ax.yaxis.label.set(rotation=0, ha="left", va="top")
    ctx.panel.ax.yaxis.set_label_coords(0.0, 0.995, transform=ctx.panel.ax.transAxes)
    ctx.panel.placed_titles.add("y")

    columns = frame.categories or ("",)
    rows = frame.series or ("",)
    grid = _grid(ctx.panel.rect)
    values = [d.values["value"] for d in ctx.view.data]
    span = (min(values), max(values))

    for datum in ctx.view.data:
        box = _cell(grid, int(frame.position(datum.key[0])),
                    rows.index(datum.key[1]) if frame.series and len(datum.key) > 1 else 0,
                    len(columns), len(rows))
        _fill(ctx, box, _shade(ctx.style, datum.values["value"], span))
        ctx.panel.add_mark(ctx.view.full_key(datum), datum.values,
                           box.clip_to(ctx.panel.rect), "color", mark_shape="cell",
                           value_axis=ctx.value_axis, key_src=ctx.view.key_src(datum))

    height = grid.height / len(rows)
    ctx.panel.ax.set_yticks(
        [_data_y(ctx, grid.y0 + (i + 0.5) * height) for i in range(len(rows))],
        [_row_label(name) for name in rows], fontsize=ctx.style.font_size)


def draw_table_chart(ctx, frame: Frame) -> None:
    """One printed number per key, laid out as a table: the row names down the
    leading column, the column names across the header row.

    The first key segment names the rows because that is the segment a table always
    has -- with one grouping column the table is a column of names beside a column of
    numbers, and a second grouping column is what adds the header names.

    The tick furniture goes: this type has no value axis, and nothing is ever
    measured back off its geometry. What the frame recorded stays recorded, and the
    two axis titles it wrote stay on the page, because a page element the record
    names has to be a page element a reader can find.
    """
    frame_mod.bare(ctx.panel.ax)

    rows = frame.categories or ("",)
    columns = frame.series or (ctx.value_label(),)
    grid = _grid(ctx.panel.rect)
    across, down = len(columns) + 1, len(rows) + 1
    palette = PALETTES[ctx.style.palette]
    header, body = palette[-2], palette[-1]

    _fill(ctx, _cell(grid, 0, 0, across, down), header)
    for j, name in enumerate(columns):
        _name(ctx, _cell(grid, j + 1, 0, across, down), header, name)
    for i, name in enumerate(rows):
        _name(ctx, _cell(grid, 0, i + 1, across, down), header, name)

    for datum in ctx.view.data:
        box = _cell(grid, (columns.index(datum.key[1])
                           if frame.series and len(datum.key) > 1 else 0) + 1,
                    rows.index(datum.key[0]) + 1, across, down)
        _fill(ctx, box, body)
        index = ctx.panel.add_mark(ctx.view.full_key(datum), datum.values, box, "printed",
                                   mark_shape="cell", value_axis=ctx.value_axis,
                                   key_src=ctx.view.key_src(datum), labeled=True)
        # The number is placed here rather than by the label writer -- a cell is a
        # centred string, not one of its five offsets from a mark -- but where it
        # landed is attached to the mark by the same one function that attaches
        # every other label box.
        printed = labels.text_for(ctx, datum.values["value"])
        ctx.canvas.defer(_print(ctx, box, printed), labels._attach(ctx, index, printed))


def _shade(style: StyleVector, value: float, span: tuple[float, float]) -> RGB:
    """Where one value sits on the palette, from its lightest colour to its darkest.

    The scale is the palette read backwards rather than a ramp of its own between two
    colours: the palettes are written as ramps already, so a heatmap ends up in the
    same ink as every other figure in the batch.
    """
    ramp = PALETTES[style.palette][::-1]
    lo, hi = span
    fraction = (value - lo) / (hi - lo) if hi > lo else 0.5
    at = min(max(fraction, 0.0), 1.0) * (len(ramp) - 1)
    step = min(int(at), len(ramp) - 2)
    a, b, f = ramp[step], ramp[step + 1], at - step
    return (round(a[0] + (b[0] - a[0]) * f), round(a[1] + (b[1] - a[1]) * f),
            round(a[2] + (b[2] - a[2]) * f))


def _grid(rect: Box) -> Box:
    """The part of the plotting area the grid is laid over."""
    return Box(rect.x0, rect.y0 + rect.height * HEADROOM, rect.x1, rect.y1)


def _cell(grid: Box, column: int, row: int, columns: int, rows: int) -> Box:
    """One cell of the grid, in pixels."""
    width, height = grid.width / columns, grid.height / rows
    x0, y0 = grid.x0 + column * width, grid.y0 + row * height
    return Box(x0, y0, x0 + width, y0 + height)


def _fill(ctx, box: Box, rgb: RGB) -> None:
    """The cell's own rectangle, drawn where the box says it is.

    A table chart is filled rather than ruled for the same reason a heatmap is: the
    fill is what makes a cell a shape on the page instead of a region a reader has to
    infer from its neighbours, and a box holding nothing but a short number is
    mostly background.
    """
    ctx.panel.ax.add_patch(Rectangle(
        (box.x0, ctx.panel.image_height - box.y1), box.width, box.height,
        transform=IdentityTransform(), zorder=2, **ctx.shape_kwargs(rgb)))


def _print(ctx, box: Box, text: str, *, weight: str = "normal") -> Any:
    """One string, centred in a pixel box. The artist comes back so that whoever
    wrote it can have its box measured on the next flush."""
    return ctx.panel.ax.annotate(
        text, xy=((box.x0 + box.x1) / 2, ctx.panel.image_height - (box.y0 + box.y1) / 2),
        xycoords="figure pixels", ha="center", va="center",
        fontsize=ctx.style.font_size - 1, fontweight=weight, color=hex_of(TEXT_COLOR))


def _name(ctx, box: Box, rgb: RGB, text: str) -> None:
    """A header cell: the name, and the record of where it was printed.

    A table has neither a legend nor category ticks, so this is the only place a
    reader can read a key segment off the image -- the part a legend entry plays on
    every other kind of figure.
    """
    _fill(ctx, box, rgb)
    ctx.canvas.defer(_print(ctx, box, text, weight="bold"),
                     lambda got: ctx.canvas.add_element(got, "legend_title", text))


def _row_label(text: str) -> str:
    """A row name as it is written beside the grid, wrapped once if it is long.

    Wrapped whatever the style says, unlike a category tick. The margin left of the
    plotting area is a fixed width, and a heatmap's row name is the only place its
    key segment is written -- a name running off the edge of the image is a key no
    reader can recover.
    """
    head, space, tail = text.partition(" ")
    return f"{head}\n{tail}" if space and len(text) > 12 else text


def _data_y(ctx, y: float) -> float:
    """A pixel row in the data coordinates a tick is placed at."""
    return float(ctx.panel.ax.transData.inverted().transform(
        (0.0, ctx.panel.image_height - y))[1])
