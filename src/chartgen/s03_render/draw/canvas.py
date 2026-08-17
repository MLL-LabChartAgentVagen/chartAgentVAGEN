"""画布、面板、轴、图例的公共记录。**画和记不分开。**

每画一个图元，就在同一处把它的框、键、值写进记录——只有在画的那一刻，
三者才同时在手。框由 matplotlib 自己的 `transData` 算出，不做事后解析图像。

**布局参数冻结**：图像尺寸、dpi、绘图区矩形三项写死。自动布局
（`tight_layout` / `constrained_layout` / `savefig(bbox_inches=...)`）会在画完
之后挪动绘图区，此时已经记下的框全部失效，而且不报错。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from ...common.geometry import Box, axes_rect, rect_to_mpl_fraction
from ...interfaces.figure import ViewSpec
from ...interfaces.record import Axis, Channel, Element, LegendEntry, Mark, Panel
from ...interfaces.style import StyleVector
from ..style import BACKGROUND, GRID_COLOR, RGB, TEXT_COLOR, hex_of, resolve_font

#: 绘图区四边留白（像素）。900×600 上得到 [96, 60, 860, 520]，与 03 §0 一致。
MARGINS = {"left": 96.0, "top": 60.0, "right": 40.0, "bottom": 80.0}


@dataclass
class PanelCanvas:
    """一个面板：一个 matplotlib Axes，加上它记下来的轴与图元。"""

    panel_id: str
    ax: Axes
    rect: Box
    image_height: int
    chart_type: str
    axes: list[Axis] = field(default_factory=list)
    marks: list[Mark] = field(default_factory=list)
    _right_ax: Axes | None = None

    # ---- 坐标：数据 →（绘图库的轴变换）→ 像素，原点左上

    def to_pixel(self, x: float, y: float, right: bool = False) -> tuple[float, float]:
        ax = self._right_ax if right and self._right_ax is not None else self.ax
        px, py = ax.transData.transform((x, y))
        return (float(px), float(self.image_height - py))

    def box_from_data(self, x0: float, y0: float, x1: float, y1: float,
                      right: bool = False) -> Box:
        a = self.to_pixel(x0, y0, right)
        b = self.to_pixel(x1, y1, right)
        return Box(a[0], a[1], b[0], b[1])

    # ---- 记录

    def record_axis(self, role: str, column: str | None = None,
                    scale: str = "linear") -> Axis:
        if role == "x":
            lo, hi = self.ax.get_xlim()
            pixel_range = (self.to_pixel(lo, 0)[0], self.to_pixel(hi, 0)[0])
        else:
            right = role == "y_right"
            source = self._right_ax if right else self.ax
            lo, hi = source.get_ylim()
            pixel_range = (self.to_pixel(0, lo, right)[1], self.to_pixel(0, hi, right)[1])
        axis = Axis(role, (float(lo), float(hi)), pixel_range, scale, column)
        self.axes.append(axis)
        return axis

    def add_mark(self, key: tuple[str, ...], values: dict[str, float], box: Box,
                 channel: Channel, labeled: bool = False,
                 label_box: Box | None = None) -> Mark:
        mark = Mark(f"m{len(self.marks)}", self.panel_id, key, values, box,
                    channel, labeled, label_box)
        self.marks.append(mark)
        return mark

    def axis(self, role: str) -> Axis | None:
        return next((a for a in self.axes if a.role == role), None)

    def to_panel(self) -> Panel:
        return Panel(self.panel_id, self.rect, tuple(self.axes), self.chart_type)


class Canvas:
    """一张图像的画布。持有 figure，产出面板、图例与 L0 元素。"""

    def __init__(self, style: StyleVector) -> None:
        self.style = style
        w, h = style.image_size
        self.fig = Figure(figsize=(w / style.dpi, h / style.dpi), dpi=style.dpi)
        FigureCanvasAgg(self.fig)
        self.fig.patch.set_facecolor(hex_of(BACKGROUND))
        self.font = resolve_font(style.font_family)
        self.panels: list[PanelCanvas] = []
        self.legend: list[LegendEntry] = []
        self.elements: list[Element] = []

    # ---- 面板

    def full_rect(self) -> Box:
        return axes_rect(self.style.image_size, **MARGINS)

    def add_panel(self, panel_id: str, rect: Box, chart_type: str) -> PanelCanvas:
        ax = self.fig.add_axes(rect_to_mpl_fraction(rect, self.style.image_size))
        self._style_axes(ax)
        panel = PanelCanvas(panel_id, ax, rect, self.style.image_size[1], chart_type)
        self.panels.append(panel)
        return panel

    def _style_axes(self, ax: Axes) -> None:
        s = self.style
        ax.set_facecolor(hex_of(BACKGROUND))
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            ax.spines[spine].set_color(hex_of(TEXT_COLOR))
            ax.spines[spine].set_linewidth(0.8)
        ax.tick_params(colors=hex_of(TEXT_COLOR), labelsize=s.font_size)
        if s.gridlines:
            ax.set_axisbelow(True)
            ax.grid(axis="y", color=hex_of(GRID_COLOR), linewidth=0.8)

    def add_twin(self, panel: PanelCanvas) -> Axes:
        """compound 的右轴。两条纵轴各记一份值域像素域。"""
        panel._right_ax = panel.ax.twinx()
        panel._right_ax.spines["right"].set_visible(True)
        panel._right_ax.tick_params(colors=hex_of(TEXT_COLOR), labelsize=self.style.font_size)
        return panel._right_ax

    # ---- 文字与图例

    def text_box(self, artist) -> Box:
        """任何文字图元的像素框。渲染一次拿 renderer。"""
        renderer = self.fig.canvas.get_renderer()
        bbox = artist.get_window_extent(renderer)
        h = self.style.image_size[1]
        return Box(bbox.x0, h - bbox.y1, bbox.x1, h - bbox.y0)

    def add_legend_entry(self, box: Box, category: str, panels: tuple[str, ...]) -> None:
        self.legend.append(LegendEntry(box, category, panels))

    def add_element(self, box: Box, category: str) -> None:
        self.elements.append(Element(box, category))  # type: ignore[arg-type]

    # ---- 落盘

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.fig.savefig(path, dpi=self.style.dpi,
                         facecolor=self.fig.get_facecolor(),
                         metadata={"Software": "chartgen"})
        return path


@dataclass
class DrawContext:
    """一个绘制函数需要的全部东西。按图元形状分文件的那些函数都收这一个参数。"""

    canvas: Canvas
    panel: PanelCanvas
    view: ViewSpec
    units: dict[str, str] = field(default_factory=dict)
    series_colors: dict[str, RGB] = field(default_factory=dict)

    @property
    def style(self) -> StyleVector:
        return self.canvas.style

    def axis_label(self, column: str) -> str:
        unit = self.units.get(column)
        return f"{column} ({unit})" if unit else column

    def measure_label(self) -> str:
        b = self.view.binding
        if b.aggregate == "COUNT":
            return "COUNT(*)"
        if not b.measures:
            return ""
        return f"{b.aggregate}({self.axis_label(b.measures[0])})"
