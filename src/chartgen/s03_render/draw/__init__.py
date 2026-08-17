"""按图元形状分文件的绘制函数。17 种类型只有 6 种图元形状。

`DRAWERS` 是图表类型 → 绘制函数的唯一映射。新增一个类型在这里加一行。
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
