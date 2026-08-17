"""Drawing functions, one file per mark shape rather than per chart type.

`DRAWERS` is the one mapping from chart type to drawing function; a new type adds
one line here.
"""

from __future__ import annotations

from typing import Callable

from .canvas import Canvas, DrawContext, PanelCanvas
from .rect import draw_bar

Drawer = Callable[[DrawContext], None]

DRAWERS: dict[str, Drawer] = {
    "bar": draw_bar,
}

__all__ = ["Canvas", "DrawContext", "PanelCanvas", "DRAWERS", "Drawer"]
