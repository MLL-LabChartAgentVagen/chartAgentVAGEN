"""Rectangular marks: the bar family, histograms, waterfalls and funnels.

One file per mark shape rather than per chart type. These types differ only in
which keys their value dictionary holds and where the base of the rectangle sits.
"""

from __future__ import annotations

from ...common.geometry import Box
from ..style import format_number, hex_of, nice_range
from .canvas import DrawContext

#: Distance from the top of a rectangle to its value label, in pixels.
LABEL_OFFSET_PX = 6.0


def _label_values(ctx: DrawContext, n: int) -> list[bool]:
    """Which marks get a written value: all, none, or every other one."""
    mode = ctx.style.value_labels
    if mode == "all":
        return [True] * n
    if mode == "none":
        return [False] * n
    return [i % 2 == 0 for i in range(n)]


def _write_label(ctx: DrawContext, x: float, top_value: float, text: str) -> Box:
    """Write the value above the rectangle and record the label box."""
    artist = ctx.panel.ax.annotate(
        text, xy=(x, top_value), xytext=(0, LABEL_OFFSET_PX),
        textcoords="offset points", ha="center", va="bottom",
        fontsize=ctx.style.font_size - 1, color="#212529",
    )
    ctx.canvas.fig.canvas.draw()
    return ctx.canvas.text_box(artist)


def draw_bar(ctx: DrawContext) -> None:
    """One rectangle per key, with the value encoded as length."""
    panel, style = ctx.panel, ctx.style
    data = ctx.view.data
    labels = [d.key[0] for d in data]
    values = [d.values["value"] for d in data]

    lo, hi, step = nice_range(min(values), max(values), style)
    panel.ax.set_xlim(-0.5, len(data) - 0.5)
    panel.ax.set_ylim(lo, hi)
    panel.ax.set_yticks(_ticks(lo, hi, step))
    panel.ax.set_xticks(range(len(data)), labels,
                        rotation=style.label_rotation,
                        ha="right" if style.label_rotation else "center")
    panel.ax.set_ylabel(ctx.measure_label(), fontsize=style.font_size)
    panel.ax.set_xlabel(ctx.axis_label(ctx.view.binding.group_columns[0]),
                        fontsize=style.font_size)

    colors = [ctx.series_colors.get(k, (31, 78, 121)) for k in labels]
    half = style.bar_width / 2
    panel.ax.bar(range(len(data)), [v - lo for v in values], bottom=lo,
                 width=style.bar_width,
                 color=[hex_of(c) for c in colors],
                 edgecolor="#ffffff" if style.edge_width else "none",
                 linewidth=style.edge_width, hatch=style.hatch)

    panel.record_axis("x", ctx.view.binding.group_columns[0])
    panel.record_axis("y", _measure_column(ctx))

    write = _label_values(ctx, len(data))
    for i, (datum, value) in enumerate(zip(data, values)):
        box = panel.box_from_data(i - half, lo, i + half, value).clip_to(panel.rect)
        label_box = None
        if write[i]:
            label_box = _write_label(ctx, i, value,
                                     format_number(value, style, _unit(ctx)))
        panel.add_mark(datum.key, dict(datum.values), box, "length",
                       labeled=write[i], label_box=label_box)


def _ticks(lo: float, hi: float, step: float) -> list[float]:
    out, v = [], lo
    while v <= hi + step * 1e-9:
        out.append(round(v, 10))
        v += step
    return out


def _measure_column(ctx: DrawContext) -> str | None:
    ms = ctx.view.binding.measures
    return ms[0] if ms else None


def _unit(ctx: DrawContext) -> str | None:
    col = _measure_column(ctx)
    return ctx.units.get(col) if col else None
