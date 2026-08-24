"""Drawing functions, one file per mark shape rather than per chart type.

`DRAWERS` is the one mapping from chart type to drawing function; a new type adds
one line here and one branch in the file its shape lives in.
"""

from __future__ import annotations

from typing import Callable

from .boxlike import draw_box
from .canvas import Canvas, PanelCanvas
from .context import DrawContext
from .cell import draw_heatmap, draw_table_chart
from .frame import Frame
from .point import (
    draw_area, draw_error_bar, draw_line, draw_scatter, draw_windsock,
)
from .rect import draw_bar, draw_funnel, draw_histogram, draw_range_bar, draw_waterfall
from .sector import draw_pie

Drawer = Callable[[DrawContext, Frame], None]

DRAWERS: dict[str, Drawer] = {
    "bar": draw_bar,
    "grouped_bar": draw_bar,
    "stacked_bar": draw_bar,
    "histogram": draw_histogram,
    "waterfall": draw_waterfall,
    "funnel": draw_funnel,
    "range_bar": draw_range_bar,
    "pie": draw_pie,
    "heatmap": draw_heatmap,
    "table_chart": draw_table_chart,
    "box": draw_box,
    "line": draw_line,
    "category_line": draw_line,
    "area": draw_area,
    "scatter": draw_scatter,
    "error_bar": draw_error_bar,
    "windsock": draw_windsock,
}

__all__ = ["Canvas", "DrawContext", "PanelCanvas", "Frame", "DRAWERS", "Drawer"]
