"""Drawing a figure: a figure specification and a style vector to an image plus geometry.

No model is involved. The same specification and style always produce a
bit-identical image and identical geometry.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib import rc_context

from ..common.geometry import Box
from ..interfaces.figure import FigureSpec
from ..interfaces.record import RenderOutput
from ..interfaces.style import StyleVector
from ..registry.charts import CHARTS
from .draw import DRAWERS, Canvas, DrawContext
from .style import colors


class UnsupportedChartType(NotImplementedError):
    """The chart table lists this type, but no drawing branch exists for it yet."""


def panel_rects(spec: FigureSpec, canvas: Canvas) -> list[Box]:
    """Layout to one plotting area per panel."""
    if len(spec.panels) == 1:
        return [canvas.full_rect()]
    raise UnsupportedChartType(f"no multi-panel drawing for the {spec.layout} layout yet")


def series_palette(spec: FigureSpec, canvas: Canvas) -> dict[str, tuple[int, int, int]]:
    """Series to colour, shared across the whole figure so one legend can serve all panels."""
    keys: list[str] = []
    for panel in spec.panels:
        for datum in panel.view.data:
            name = datum.key[-1] if len(datum.key) > 1 else datum.key[0]
            if name not in keys:
                keys.append(name)
    return dict(zip(keys, colors(canvas.style, len(keys))))


def render(spec: FigureSpec, style: StyleVector, out_dir: str | Path) -> RenderOutput:
    """Draw one figure, recording each mark as it is drawn."""
    out_dir = Path(out_dir)
    canvas = Canvas(style)
    with rc_context({"font.family": [canvas.font], "axes.unicode_minus": False}):
        palette = series_palette(spec, canvas)
        for panel_spec, rect in zip(spec.panels, panel_rects(spec, canvas)):
            chart_type = panel_spec.view.binding.chart_type
            drawer = DRAWERS.get(chart_type)
            if drawer is None:
                raise UnsupportedChartType(chart_type)
            panel = canvas.add_panel(panel_spec.panel_id, rect, chart_type)
            drawer(DrawContext(canvas, panel, panel_spec.view,
                               units=dict(spec.column_units), series_colors=palette))
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
    )


def channel_of(chart_type: str) -> str:
    return CHARTS[chart_type].channel
