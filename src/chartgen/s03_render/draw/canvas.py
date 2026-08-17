"""The canvas, its panels, axes and legend, and the record they write as they draw.

Drawing and recording are the same step. A mark's box, key and value are written
together at the moment it is drawn, because that is the only moment all three are
in hand; the box comes from the plotting library's own coordinate transform, never
from parsing the finished image.

Three layout parameters are frozen: image size, dpi, and the plotting rectangle.
Auto-layout moves the plotting area after the drawing is done, which invalidates
every box already recorded -- and does so without raising anything.
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

#: Margins around the plotting area, in pixels.
MARGINS = {"left": 96.0, "top": 60.0, "right": 40.0, "bottom": 80.0}


@dataclass
class PanelCanvas:
    """One panel: a set of plotting axes, plus the axes and marks it has recorded."""

    panel_id: str
    ax: Axes
    rect: Box
    image_height: int
    chart_type: str
    axes: list[Axis] = field(default_factory=list)
    marks: list[Mark] = field(default_factory=list)
    _right_ax: Axes | None = None

    # ---- coordinates: data, through the library's transform, to pixels with a top-left origin

    def to_pixel(self, x: float, y: float, right: bool = False) -> tuple[float, float]:
        ax = self._right_ax if right and self._right_ax is not None else self.ax
        px, py = ax.transData.transform((x, y))
        return (float(px), float(self.image_height - py))

    def box_from_data(self, x0: float, y0: float, x1: float, y1: float,
                      right: bool = False) -> Box:
        a = self.to_pixel(x0, y0, right)
        b = self.to_pixel(x1, y1, right)
        return Box(a[0], a[1], b[0], b[1])

    # ---- recording

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
    """The canvas for one image. Owns the figure and hands out panels, legend entries
    and page elements."""

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

    # ---- panels

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
        """A second vertical axis. Each one records its own value and pixel range,
        because the same pixel height then means two different values."""
        panel._right_ax = panel.ax.twinx()
        panel._right_ax.spines["right"].set_visible(True)
        panel._right_ax.tick_params(colors=hex_of(TEXT_COLOR), labelsize=self.style.font_size)
        return panel._right_ax

    # ---- text and legend

    def text_box(self, artist) -> Box:
        """The pixel box of any piece of text."""
        renderer = self.fig.canvas.get_renderer()
        bbox = artist.get_window_extent(renderer)
        h = self.style.image_size[1]
        return Box(bbox.x0, h - bbox.y1, bbox.x1, h - bbox.y0)

    def add_legend_entry(self, box: Box, category: str, panels: tuple[str, ...]) -> None:
        self.legend.append(LegendEntry(box, category, panels))

    def add_element(self, box: Box, category: str) -> None:
        self.elements.append(Element(box, category))  # type: ignore[arg-type]

    # ---- saving

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.fig.savefig(path, dpi=self.style.dpi,
                         facecolor=self.fig.get_facecolor(),
                         metadata={"Software": "chartgen"})
        return path


@dataclass
class DrawContext:
    """Everything a drawing function needs. Every drawing function takes just this."""

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
