"""Drawing a figure: a figure specification and a style vector to an image plus geometry.

No model is involved. The same specification and style always produce a
bit-identical image and identical geometry.

The order matters. Panel rectangles are laid out first and never move again; then
the frame of each panel is settled from every view that will draw on it; only then
is anything drawn. Working the other way -- draw, then let the library arrange what
it drew -- moves the plotting area after the boxes have been recorded against it,
and nothing raises.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Sequence

from matplotlib import rc_context

from ..common.geometry import Box
from ..interfaces.figure import FigureSpec, TextBlock, ViewSpec
from ..interfaces.record import RenderOutput
from ..interfaces.style import StyleVector
from ..registry.charts import CHARTS
from .draw import DRAWERS, Canvas, DrawContext, PanelCanvas
from .draw import frame as frames
from .draw.canvas import FOOT_BAND, PANEL_TITLE_HEIGHT, TEXT_BAND
from .style import RGB, colors

#: A panel's declared type, and what it is drawn as instead when the style asks for
#: mixed panels. Only pairs that group identically and hold the same value keys are
#: here: the swap must change how a value is drawn and not what it is.
MIXED_PARTNER: dict[str, str] = {"bar": "category_line"}


class UnsupportedChartType(NotImplementedError):
    """The chart table lists this type, but no drawing branch exists for it yet."""


# ---------------------------------------------------------------- layout

def panel_grid(spec: FigureSpec) -> int:
    """How many panels a row of this figure holds."""
    n = len(spec.panels)
    return n if spec.layout == "side_by_side" else math.ceil(math.sqrt(n))


def panel_rects(spec: FigureSpec, canvas: Canvas) -> list[Box]:
    """One plotting rectangle per panel, decided before anything is drawn.

    Panels of a multi-panel figure keep a title strip whether or not they are
    titled, for the same reason the figure keeps its text band: a rectangle that
    moved when a title arrived would invalidate every box recorded inside it.
    """
    full = canvas.full_rect()
    n = len(spec.panels)
    if n == 1:
        return [full]

    gap = canvas.style.panel_gap
    columns = panel_grid(spec)
    rows = math.ceil(n / columns)
    cell_w = (full.width - gap * full.width * (columns - 1)) / columns
    cell_h = (full.height - gap * full.height * (rows - 1)) / rows

    out = []
    for i in range(n):
        r, c = divmod(i, columns)
        x0 = full.x0 + c * (cell_w + gap * full.width)
        y0 = full.y0 + r * (cell_h + gap * full.height) + PANEL_TITLE_HEIGHT
        out.append(Box(x0, y0, x0 + cell_w, full.y0 + r * (cell_h + gap * full.height) + cell_h))
    return out


def panel_chart_type(view: ViewSpec, index: int, style: StyleVector) -> str:
    """What this panel is drawn as.

    With mixed panels the ones after the first swap to a partner type that groups
    the same way and holds the same value keys, so the figure asks a reader to
    change how they measure without changing what there is to measure.
    """
    declared = view.binding.chart_type
    if style.panel_types == "mixed" and index > 0:
        return MIXED_PARTNER.get(declared, declared)
    return declared


# ---------------------------------------------------------------- colour and legend

def legend_names(spec: FigureSpec) -> dict[str, tuple[str, ...]]:
    """The names a legend lists, each with the panels that actually draw it.

    Read off the key sources rather than off the chart type, which is what keeps the
    drawing and the record in step: a segment the record calls legend-sourced is a
    segment a legend was drawn for.

    Which panels an entry governs is the whole content of the legend-binding target,
    so it is collected per name rather than assumed to be all of them. On a figure
    whose panels group differently, an entry that named every panel would be saying
    something untrue about the ones that do not draw it.
    """
    out: dict[str, list[str]] = {}
    for panel in spec.panels:
        for view in panel.views:
            for datum in view.data:
                for segment, source in zip(view.full_key(datum), view.key_src(datum)):
                    if source != "legend":
                        continue
                    panels = out.setdefault(segment, [])
                    if panel.panel_id not in panels:
                        panels.append(panel.panel_id)
    return {name: tuple(panels) for name, panels in out.items()}


def series_palette(spec: FigureSpec, style: StyleVector) -> dict[str, RGB]:
    """Name to colour, fixed across the whole figure so one legend can serve every panel."""
    names = list(legend_names(spec))
    for view in spec.views:
        for datum in view.data:
            name = _colour_name(view, datum.key)
            if name not in names:
                names.append(name)
    return dict(zip(names, colors(style, len(names))))


def _colour_name(view: ViewSpec, key: tuple[str, ...]) -> str:
    if view.key_prefix:
        return view.key_prefix[0]
    return key[-1] if len(key) > 1 else (key[0] if key else "")


# ---------------------------------------------------------------- text

#: How much of a line's type size the line advance is, and how tall a line's box is.
LINE_ADVANCE = 1.9
LINE_HEIGHT = 1.7

#: Type sizes to try, as a fraction of the style's, when a band has to hold more
#: lines than it has room for. The last one is the floor: below it the text is on
#: the page but no longer readable, and dropping a block beats printing a smear.
SHRINK = (1.0, 0.86, 0.72, 0.6)

#: Space between two blocks that end up sharing a line.
BLOCK_GAP = 10.0


def _weight(block: TextBlock) -> str:
    return "bold" if block.role == "title" else "normal"


def _sizes(blocks: Sequence[TextBlock], style: StyleVector) -> list[float]:
    """The type size each block is written at. A title is the largest thing on the
    page and a unit the smallest; that ranking is what makes a page look like a page."""
    return [{"title": style.font_size + 3, "figure_number": style.font_size,
             "source": style.font_size - 2, "note": style.font_size - 2}
            .get(block.role, style.font_size - 1) for block in blocks]


def _pack(canvas: Canvas, blocks: Sequence[TextBlock], sizes: Sequence[float],
          band: Box) -> list[list[tuple[int, float]]]:
    """Blocks into lines: a new line each time, unless the next block still fits
    beside the last one. Returns the block indices and the width each one gets."""
    lines: list[list[tuple[int, float]]] = []
    used = 0.0
    for i, (block, size) in enumerate(zip(blocks, sizes)):
        want = canvas.measure(block.text, size, _weight(block))
        if lines and used + BLOCK_GAP + want <= band.width:
            lines[-1].append((i, want))
            used += BLOCK_GAP + want
        else:
            lines.append([(i, min(want, band.width))])
            used = min(want, band.width)
    return lines


def _lay_out(canvas: Canvas, blocks: Sequence[TextBlock], band: Box) -> float:
    """Write these blocks into this band, and say where the last line ended.

    The bands are frozen, so a band asked to hold more lines than it has room for is
    not a reason to move anything: the type shrinks first, and blocks share a line
    where they fit. A block written past the edge of the band would be text nobody
    can read recorded at a box that says otherwise, so it is not written at all.
    """
    if not blocks:
        return band.y0
    for shrink in SHRINK:
        sizes = [s * shrink for s in _sizes(blocks, canvas.style)]
        lines = _pack(canvas, blocks, sizes, band)
        height = sum(max(sizes[i] for i, _ in line) * LINE_ADVANCE for line in lines)
        if height <= band.height or shrink == SHRINK[-1]:
            break
    y = band.y0
    for line in lines:
        tall = max(sizes[i] for i, _ in line)
        if y + tall * LINE_HEIGHT > band.y1 + 1e-6:
            break               # out of band: the rest is not written at all
        x = band.x0
        for i, want in line:
            size = sizes[i]
            room = band.x1 - x if len(line) == 1 else want
            canvas.write_text(blocks[i], Box(x, y, x + room, y + size * LINE_HEIGHT),
                              size=size, weight=_weight(blocks[i]))
            x += room + BLOCK_GAP
        y += tall * LINE_ADVANCE
    return y


def draw_texts(canvas: Canvas, spec: FigureSpec) -> None:
    """The figure's own text: the band above the plotting area, and the foot of the page."""
    style = canvas.style
    above = [b for b in spec.texts if b.scope == "figure" and b.role in
             ("figure_number", "title", "subtitle", "unit")]
    below = [b for b in spec.texts if b.scope == "figure" and b.role in ("source", "note")]

    _lay_out(canvas, above,
             canvas.band(TEXT_BAND if style.title_placement == "above" else FOOT_BAND))
    foot = canvas.band(FOOT_BAND if style.title_placement == "above" else TEXT_BAND)
    line = _lay_out(canvas, below, foot)
    if style.note_box and below:
        canvas.add_element(Box(foot.x0 - 4, foot.y0 - 4, foot.x1, min(line, foot.y1)),
                           "note", " ".join(b.text for b in below))


def draw_panel_titles(canvas: Canvas, spec: FigureSpec, rects: Sequence[Box]) -> None:
    for panel, rect in zip(spec.panels, rects):
        for block in panel.texts:
            canvas.write_text(block, Box(rect.x0, rect.y0 - PANEL_TITLE_HEIGHT,
                                         rect.x1, rect.y0 - 4),
                              size=canvas.style.font_size, weight="bold",
                              panel_id=panel.panel_id)


# ---------------------------------------------------------------- the stage

def render(spec: FigureSpec, style: StyleVector, out_dir: str | Path,
           variant: int = 0) -> RenderOutput:
    """Draw one figure, recording each mark as it is drawn."""
    out_dir = Path(out_dir)
    canvas = Canvas(style)
    with rc_context({"font.family": [canvas.font], "axes.unicode_minus": False}):
        # How wide a legend down the side has to be is the one block thickness that
        # has to be measured, and it is measured from the names, which are a pure
        # function of the specification. Asked before the first panel: the answer
        # decides where the plotting area starts.
        canvas.plan_side_legend(list(legend_names(spec)))
        rects = panel_rects(spec, canvas)
        palette = series_palette(spec, style)
        # Two views in one plotting area need a second value axis when their units
        # differ, and may have one when they do not. The figure settles the first
        # case by not sharing its value axis; the style settles the second.
        overlaid = len(spec.panels) == 1 and len(spec.panels[0].views) > 1
        two_axes = overlaid and (not spec.sharing.share_y or style.dual_axis)

        columns = panel_grid(spec)
        plans = [frames.plan(p.views, style, two_axes=two_axes) for p in spec.panels]
        plans = frames.unify(plans, _shared_axes(spec))

        for index, (panel_spec, rect, frame) in enumerate(zip(spec.panels, rects, plans)):
            types = [panel_chart_type(v, index, style) for v in panel_spec.views]
            panel = canvas.add_panel(panel_spec.panel_id, rect, types,
                                     has_title=bool(panel_spec.texts))
            if two_axes and len(panel_spec.views) > 1:
                canvas.add_twin(panel)
            for layer, (view, chart_type) in enumerate(zip(panel_spec.views, types)):
                drawer = DRAWERS.get(chart_type)
                if drawer is None:
                    raise UnsupportedChartType(chart_type)
                ctx = DrawContext(canvas, panel, view, units=dict(spec.column_units),
                                  names=dict(spec.column_names), series_colors=palette,
                                  value_axis=frame.role_for(layer), layer=layer)
                frames.apply(ctx, frame, axis_titles=_titled(spec, index, columns, style))
                drawer(ctx, frame)
            _hide_repeated_ticks(spec, panel, index, style, columns)

        canvas.draw_legend({n: palette[n] for n in legend_names(spec)},
                           legend_names(spec),
                           panel=canvas.panels[0] if canvas.panels else None)
        draw_texts(canvas, spec)
        draw_panel_titles(canvas, spec, rects)
        canvas.add_element(canvas.full_rect(), "Picture", "")
        image_path = canvas.save(out_dir / f"{spec.figure_id}.png")

    return RenderOutput(
        figure_id=spec.figure_id,
        scenario_id=spec.scenario_id,
        image_path=str(image_path),
        image_size=style.image_size,
        style=style,
        panels=tuple(p.to_panel() for p in canvas.panels),
        marks=tuple(m for p in canvas.panels for m in p.marks),
        legend=tuple(canvas.legend),
        elements=tuple(canvas.elements),
        degradations=(),
        layout=canvas.layout,
        page_id=spec.page_id,
        variant=variant,
        caption=spec.caption,
    )


def _shared_axes(spec: FigureSpec) -> tuple[str, ...]:
    """Which axes every panel of this figure has to be drawn against one range of."""
    out: list[str] = []
    if spec.sharing.share_y:
        out += ["y", "y_right"]
    if spec.sharing.share_x:
        out.append("x")
    return tuple(out)


def _titled(spec: FigureSpec, index: int, columns: int,
            style: StyleVector) -> dict[str, bool]:
    """Which of this panel's axis titles it writes for itself, one answer per axis.

    A shared axis is named once beside the panel that carries its ticks. Named on
    every panel of a column, the titles land on top of each other. An axis this
    figure does not share is named on every panel, because there each panel names
    something different -- suppressing it leaves a quantity that the record says the
    axis carries written nowhere on the page.
    """
    once = style.repeat_shared_ticks or (index % columns == 0 and index < columns)
    return {"y": not spec.sharing.share_y or once,
            "x": not spec.sharing.share_x or once}


def _hide_repeated_ticks(spec: FigureSpec, panel: PanelCanvas, index: int,
                         style: StyleVector, columns: int) -> None:
    """A shared axis is drawn once per row unless the style asks for it everywhere.

    Once per row rather than once per figure: a panel on the second row has no
    neighbour to its left carrying the scale, and a panel of bars with no numbers
    anywhere near it is a panel nobody can read.
    """
    if style.repeat_shared_ticks:
        return
    if spec.sharing.share_y and index % columns:
        panel.ax.set_yticklabels([])
        panel.ax.set_ylabel("")
    if spec.sharing.share_x and index + columns < len(spec.panels):
        panel.ax.set_xticklabels([])


def channel_of(chart_type: str) -> str:
    return CHARTS[chart_type].primary_channel
