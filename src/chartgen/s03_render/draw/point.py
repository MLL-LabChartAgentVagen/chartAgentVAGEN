"""Point and band marks: lines, scatters, stacked areas, error bars and spreads.

One file per mark shape rather than per chart type. Six types share these two, and
what separates them is what the box has to run between:

    line, category line   a marker on the value, joined to its neighbours
    scatter               a marker on a pair of coordinates, one row per mark
    area                  the running total before and after this layer
    error bar             the smallest and the largest value of the group
    windsock              the same two, filled in across the time axis

A marker has no extent of its own, so a point mark's box is a fixed square centred
on it and the value is read back off its centre. The other three carry two numbers
on two edges, and the box has to span exactly the pair `SPANNING_KEYS` names for
the shape -- a box drawn around the marker instead would leave both of them
outside the geometry the self-check measures.

Every mark is drawn and recorded in the same statement, so the box, the key and
the value are written from the same numbers. The line joining two points is not a
mark: it carries no value of its own, and what a reader measures is where a point
sits, so it is drawn once per series before the markers are.
"""

from __future__ import annotations

from typing import Sequence

from ...common.geometry import Box
from ...interfaces.figure import Datum, ViewSpec
from ...interfaces.record import MarkShape
from ...registry.charts import CHARTS
from ..style import RGB, hex_of
from . import labels
from .frame import Frame

#: Side of the box recorded around one point, in pixels. A point has no extent, so
#: the square is a constant rather than the size of whichever marker the style
#: picked: the value is read off the centre of the box, and a box that grew with
#: the marker would keep reading the same value while claiming a different shape.
POINT_SIZE = 9.0

#: Marker diameter and line thickness, in points, sized to sit inside that square.
MARKER_SIZE = 5.0
LINE_WIDTH = 1.8

#: Half-width of a box that spans two values, as a fraction of the gap between
#: adjacent category positions, and the widest it may grow to in pixels.
SPAN_HALF_WIDTH = 0.25
SPAN_MAX_WIDTH = 28.0

#: Width of the box around a whiskered point, in pixels. Narrow on purpose: the
#: box is mostly the whisker, and the content check reads what fraction of a box
#: is ink -- a wide box around a thin line is mostly background and fails it.
WHISKER_WIDTH = 12.0
WHISKER_LINE = 2.0

#: How much darker, per channel, the line drawn through a band is. A median drawn
#: in the band's own colour is invisible inside it.
BAND_LINE_DARKEN = 70

#: Marker names to what the plotting library calls them. The empty string is the
#: setting that draws the line alone.
MARKERS: dict[str, str] = {"line": "", "circle": "o", "diamond": "D",
                           "triangle": "^", "tick": "|", "square": "s"}

#: What a point series is drawn with when the style vector names nothing.
DEFAULT_MARKER = "o"


def marker_of(ctx, series_index: int, points: int = 2) -> str:
    """The marker one series is drawn with.

    `series_marks` changes the marker and never the mark shape: a diamond and a
    dot are both a point, and both stay measurable. It is a tuple rather than a
    single name because a figure with two series names them apart by shape as well
    as by colour, which is the one way a greyscale figure can still be read.

    `points` is how many points the series holds, and it matters for one value:
    `line` means the line carries the series and no marker is drawn on it, which
    draws nothing at all when the series is a single point. A view whose second key
    segment is a colour group is exactly that case -- a hub reports to one region, so
    every mark is its own group -- and the record would go on saying a mark is there.
    A series of one therefore always gets a marker.
    """
    names = ctx.style.series_marks
    if not names:
        return DEFAULT_MARKER
    name = names[series_index % len(names)]
    if name == "line" and points < 2:
        return DEFAULT_MARKER
    return MARKERS[name]


def name_beside_line(ctx, name: str, x: float, y: float, colour: RGB) -> None:
    """Write a series name at the end of its line, where the style asks for it.

    A line labelled at its own end needs no legend to be identified, and it is
    recorded as a legend title because that is the question it answers: which
    series is this one. Nothing is written for a view whose single series has no
    name to write.
    """
    if not ctx.style.series_name_beside_line or not name:
        return
    artist = _axes(ctx).annotate(
        name, xy=(x, y), xytext=(6, 0), textcoords="offset points",
        ha="left", va="center", fontsize=ctx.style.font_size - 1, color=hex_of(colour))
    ctx.canvas.defer(artist, lambda box: ctx.canvas.add_element(box, "legend_title", name))


# ---------------------------------------------------------------- geometry

def _axes(ctx):
    """The plotting axes this view's values were measured against. A panel with two
    value axes has two, and the same pixel height means two different values."""
    return ctx.panel.right_ax if ctx.value_axis == "y_right" else ctx.panel.ax


def _xy(frame: Frame, pos: float, value: float) -> tuple[float, float]:
    """A category position and a value as a point, whichever way the value runs.

    A point series is never turned on its own account -- the frame turns a panel
    only when its primary mark is a rectangle -- but a mixed multi-panel figure
    draws its later panels as a category line inside the frame the first panel's
    bars turned. So the swap is read off the frame rather than assumed away.
    """
    return (value, pos) if frame.horizontal else (pos, value)


def _pixels_per_step(ctx, frame: Frame) -> float:
    """Pixels one step of the category axis covers.

    Measured through the same transform the boxes come from, so a width asked for
    in pixels stays that width whatever the image size and however many categories
    there are.
    """
    axis = 1 if frame.horizontal else 0
    a = ctx.panel.to_pixel(*_xy(frame, 0.0, 0.0))[axis]
    b = ctx.panel.to_pixel(*_xy(frame, 1.0, 0.0))[axis]
    return abs(b - a)


def _half_width(ctx, frame: Frame, pixels: float) -> float:
    """A width given in pixels, halved and expressed in category positions."""
    return pixels / 2.0 / _pixels_per_step(ctx, frame)


def _point_box(ctx, x: float, y: float) -> Box:
    """The box of one marker: a fixed square centred on the point it is drawn at.

    Not trimmed at the edge of the plotting area, and the marker is drawn whole
    there for the same reason. A point's value is read off the centre of its box,
    so a box cut short on one side would move that centre and report a value the
    mark was never drawn at -- which is exactly what happens to the two rows of a
    scatter that sit on the ends of its axis.
    """
    px, py = ctx.panel.to_pixel(x, y, ctx.value_axis == "y_right")
    half = POINT_SIZE / 2.0
    return Box(px - half, py - half, px + half, py + half)


def _span_box(ctx, frame: Frame, pos: float, half: float, lo: float, hi: float) -> Box:
    """The box of a mark that runs between two values, at one category position."""
    x0, y0 = _xy(frame, pos - half, lo)
    x1, y1 = _xy(frame, pos + half, hi)
    return ctx.panel.box_from_data(
        x0, y0, x1, y1, ctx.value_axis == "y_right").clip_to(ctx.panel.rect)


# ---------------------------------------------------------------- drawing and recording

def _record(ctx, datum: Datum, box: Box, shape: MarkShape) -> int:
    """Write one mark, in the same statement that drew it.

    Nothing about labelling is written here: whether this mark ends up with a printed
    value is settled once the labels have been measured, because a label written
    across its neighbour is dropped and its mark then carries no printed answer.
    """
    return ctx.panel.add_mark(ctx.view.full_key(datum), datum.values, box, "position",
                              mark_shape=shape, value_axis=ctx.value_axis,
                              key_src=ctx.view.key_src(datum))


def _plot(ctx, frame: Frame, pos: Sequence[float], values: Sequence[float], **kw) -> None:
    """A polyline through (position, value) pairs, whichever way the value runs."""
    points = [_xy(frame, p, v) for p, v in zip(pos, values)]
    _axes(ctx).plot([p[0] for p in points], [p[1] for p in points], **kw)


def _marker(ctx, x: float, y: float, marker: str, colour: RGB) -> None:
    """One marker, drawn where its box is about to be recorded.

    Drawn whole even where it overhangs the plotting area, so that the ink and the
    recorded box say the same thing about a point sitting on the end of its axis.
    """
    if not marker:
        return
    _axes(ctx).plot([x], [y], marker=marker, markersize=MARKER_SIZE,
                    color=hex_of(colour), markeredgecolor=hex_of(colour),
                    linestyle="none", zorder=4, clip_on=False)


def _fill(ctx, frame: Frame, pos: Sequence[float], lows: Sequence[float],
          highs: Sequence[float], colour: RGB) -> None:
    """One filled layer, between the two values it runs across the positions.

    The edge is thinned to the layer's own thickness: a stacked layer holding a small
    share is a few pixels tall, and an edge drawn in the page background at full width
    paints it out while the record goes on saying a mark is there.
    """
    thin = min((abs(ctx.panel.to_pixel(0.0, hi)[1] - ctx.panel.to_pixel(0.0, lo)[1])
                for lo, hi in zip(lows, highs)), default=None)
    ax, kwargs = _axes(ctx), ctx.shape_kwargs(colour, thin)
    if frame.horizontal:
        ax.fill_betweenx(list(pos), list(lows), list(highs), zorder=2, **kwargs)
    else:
        ax.fill_between(list(pos), list(lows), list(highs), zorder=2, **kwargs)


def _darker(colour: RGB) -> RGB:
    return tuple(max(0, c - BAND_LINE_DARKEN) for c in colour)  # type: ignore[return-value]


def _series_name(view: ViewSpec, datum: Datum) -> str:
    """Which series a datum belongs to: the segment a legend would name it by.

    A grouped view puts the category first and the series second. A per-row view
    has no category axis, so its first segment is the series and the last is the
    row the mark was drawn for.
    """
    if CHARTS[view.binding.chart_type].shape == "per_row":
        return datum.key[0] if len(datum.key) > 1 else ""
    return datum.key[1] if len(datum.key) >= 2 else ""


def _series_groups(ctx) -> dict[str, list[Datum]]:
    """The data split into the series drawn as one line, in the order it came out.
    A view with a single series lands under the empty name."""
    out: dict[str, list[Datum]] = {}
    for datum in ctx.view.data:
        out.setdefault(_series_name(ctx.view, datum), []).append(datum)
    return out


def _colour_of(ctx, data: Sequence[Datum]) -> RGB:
    """The colour of a whole series, taken from the first mark in it.

    A point series is one colour throughout. Asking per mark would give a plain
    line over twelve months twelve colours, because without a series column the
    palette is keyed by the category and the category is the month.
    """
    return ctx.colour_for(data[0].key)


# ---------------------------------------------------------------- the types

def draw_line(ctx, frame: Frame) -> None:
    """Lines over time and over categories: a marker per point, joined per series."""
    mask = labels.mask(ctx, len(ctx.view.data))
    entries: list[tuple] = []
    i = 0

    for series_index, (name, data) in enumerate(_series_groups(ctx).items()):
        colour = _colour_of(ctx, data)
        marker = marker_of(ctx, series_index, len(data))
        positions = [frame.position(d.key[0]) for d in data]
        values = [d.values["value"] for d in data]
        _plot(ctx, frame, positions, values, color=hex_of(colour),
              linewidth=LINE_WIDTH, zorder=3)
        for pos, datum in zip(positions, data):
            x, y = _xy(frame, pos, datum.values["value"])
            _marker(ctx, x, y, marker, colour)
            index = _record(ctx, datum, _point_box(ctx, x, y), "point")
            if mask[i]:
                entries.append((index, x, y, datum.values["value"], colour))
            i += 1
        name_beside_line(ctx, name, *_xy(frame, positions[-1], values[-1]), colour)
    labels.write_value_labels(ctx, entries, horizontal=frame.horizontal)


def draw_area(ctx, frame: Frame) -> None:
    """Stacked areas: one filled layer per series, one mark per point of it.

    The box spans the running total before and after the layer rather than sitting
    on the point, because that is the pair a stacked mark is measured between: its
    value is the difference of two edges and sits on neither of them.
    """
    half = min(SPAN_HALF_WIDTH, _half_width(ctx, frame, SPAN_MAX_WIDTH))
    mask = labels.mask(ctx, len(ctx.view.data))
    entries: list[tuple] = []
    i = 0

    for name, data in _series_groups(ctx).items():
        colour = _colour_of(ctx, data)
        positions = [frame.position(d.key[0]) for d in data]
        lows = [d.values["cum_start"] for d in data]
        highs = [d.values["cum_end"] for d in data]
        _fill(ctx, frame, positions, lows, highs, colour)
        for pos, datum in zip(positions, data):
            box = _span_box(ctx, frame, pos, half,
                            datum.values["cum_start"], datum.values["cum_end"])
            index = _record(ctx, datum, box, "point")
            if mask[i]:
                entries.append((index, *_xy(frame, pos, datum.values["cum_end"]),
                                datum.values["value"], colour))
            i += 1
        name_beside_line(ctx, name,
                         *_xy(frame, positions[-1], (lows[-1] + highs[-1]) / 2), colour)
    labels.write_value_labels(ctx, entries, horizontal=frame.horizontal)


def draw_scatter(ctx, frame: Frame) -> None:
    """One marker per row, at the two coordinates that row carries.

    Both numbers are read off the box, so the box is centred on the point and the
    marker is drawn inside it. A row is not a series: the colour and the marker
    name the group a row belongs to, which is why they are taken once per group
    rather than per row.
    """
    groups = list(_series_groups(ctx).items())
    colours = {name: _colour_of(ctx, data) for name, data in groups}
    markers = {name: marker_of(ctx, index, len(data)) or DEFAULT_MARKER
               for index, (name, data) in enumerate(groups)}
    mask = labels.mask(ctx, len(ctx.view.data))
    entries: list[tuple] = []

    for i, datum in enumerate(ctx.view.data):
        name = _series_name(ctx.view, datum)
        x, y = _xy(frame, datum.values["x"], datum.values["y"])
        _marker(ctx, x, y, markers[name], colours[name])
        index = _record(ctx, datum, _point_box(ctx, x, y), "point")
        if mask[i]:
            entries.append((index, x, y, datum.values["y"], colours[name]))
    labels.write_value_labels(ctx, entries, horizontal=frame.horizontal)


def draw_error_bar(ctx, frame: Frame) -> None:
    """A marker at the median of each group, whiskered out to its extremes.

    The box spans the whiskers and not the marker: a point carrying a range is
    measured off `min` and `max`, so a box drawn around the median would put both
    of them outside the geometry that is checked. The caps are what the two edges
    of that box are drawn as.
    """
    half = _half_width(ctx, frame, WHISKER_WIDTH)
    marker = marker_of(ctx, 0) or DEFAULT_MARKER
    mask = labels.mask(ctx, len(ctx.view.data))
    entries: list[tuple] = []

    for i, datum in enumerate(ctx.view.data):
        pos = frame.position(datum.key[0])
        lo, hi, mid = (datum.values[k] for k in ("min", "max", "median"))
        colour = hex_of(ctx.colour_for(datum.key))
        _plot(ctx, frame, (pos, pos), (lo, hi), color=colour,
              linewidth=WHISKER_LINE, zorder=3)
        for edge in (lo, hi):
            _plot(ctx, frame, (pos - half, pos + half), (edge, edge), color=colour,
                  linewidth=WHISKER_LINE, zorder=3)
        _marker(ctx, *_xy(frame, pos, mid), marker, ctx.colour_for(datum.key))
        index = _record(ctx, datum, _span_box(ctx, frame, pos, half, lo, hi), "point")
        if mask[i]:
            entries.append((index, *_xy(frame, pos, mid), mid, ctx.colour_for(datum.key)))
    labels.write_value_labels(ctx, entries, horizontal=frame.horizontal)


def draw_windsock(ctx, frame: Frame) -> None:
    """A filled band between the extremes of each time point, median drawn through it.

    The band is its own mark shape. A marker's box would not contain the two edges
    the spread is measured between, and the fill is what makes those edges visible
    in the first place, so the mark is the slice of the band at one point.
    """
    data = list(ctx.view.data)
    if not data:
        return
    colour = _colour_of(ctx, data)
    half = min(SPAN_HALF_WIDTH, _half_width(ctx, frame, SPAN_MAX_WIDTH))
    positions = [frame.position(d.key[0]) for d in data]
    _fill(ctx, frame, positions, [d.values["min"] for d in data],
          [d.values["max"] for d in data], colour)
    _plot(ctx, frame, positions, [d.values["median"] for d in data],
          color=hex_of(_darker(colour)), linewidth=LINE_WIDTH, zorder=3)

    mask = labels.mask(ctx, len(data))
    entries: list[tuple] = []
    for i, (pos, datum) in enumerate(zip(positions, data)):
        box = _span_box(ctx, frame, pos, half, datum.values["min"], datum.values["max"])
        index = _record(ctx, datum, box, "band")
        if mask[i]:
            entries.append((index, *_xy(frame, pos, datum.values["median"]),
                            datum.values["median"], colour))
    labels.write_value_labels(ctx, entries, horizontal=frame.horizontal)
