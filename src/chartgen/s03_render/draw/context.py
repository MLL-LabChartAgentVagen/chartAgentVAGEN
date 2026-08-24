"""What one view needs while it is being drawn.

Every drawing function takes exactly this: the canvas to draw on, the panel to draw
in, the view to draw, and the four things that decide how it reads -- units, prose
names, colours, and which axis this layer is measured against. A drawing function
that reached for anything else would be reading the figure specification a second
time, and the two readings would eventually disagree.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ...interfaces.figure import ViewSpec
from ...interfaces.record import AxisRole
from ...interfaces.style import StyleVector
from ...interfaces.table import aggregate_phrase
from ..style import RGB, BACKGROUND, SHADOW, hex_of
from .canvas import Canvas, MAX_EDGE_SHARE, PanelCanvas

@dataclass
class DrawContext:
    """Everything a drawing function needs. Every drawing function takes just this."""

    canvas: Canvas
    panel: PanelCanvas
    view: ViewSpec
    units: dict[str, str] = field(default_factory=dict)
    names: dict[str, str] = field(default_factory=dict)
    series_colors: dict[str, RGB] = field(default_factory=dict)
    value_axis: AxisRole = "y"
    layer: int = 0                       # which view of an overlaid panel this is

    @property
    def style(self) -> StyleVector:
        return self.canvas.style

    @property
    def overlaid(self) -> bool:
        """Whether this plotting area holds more than one view.

        Read off the panel rather than off `layer`, because both layers of an
        overlay need the answer and the first one is layer zero like any other.
        """
        return len(self.panel.chart_types) > 1

    def label_of(self, column: str) -> str:
        return self.names.get(column, column)

    def measure_column(self) -> str | None:
        """The column the value axis carries.

        A view with no grouping puts one measure across the image and the other up
        it, so the value axis carries the second of the two, not the first.
        """
        from ...registry.charts import CHARTS

        ms = self.view.binding.measures
        if not ms:
            return None
        return ms[1] if CHARTS[self.view.binding.chart_type].shape == "per_row" else ms[0]

    def cross_column(self) -> str | None:
        """The column the category axis carries: a grouping column, or the first
        measure when a view draws one row per mark."""
        from ...registry.charts import CHARTS

        b = self.view.binding
        if CHARTS[b.chart_type].shape == "per_row":
            return b.measures[0] if b.measures else None
        return b.group_columns[0] if b.group_columns else None

    def unit(self) -> str | None:
        column = self.measure_column()
        return self.units.get(column) if column else None

    def value_label(self) -> str:
        from ...registry.charts import CHARTS

        b = self.view.binding
        if b.aggregate == "COUNT":
            return "Count of records"
        column = self.measure_column()
        if not column:
            return ""
        if CHARTS[b.chart_type].shape == "per_row":
            return self.label_of(column)
        text = aggregate_phrase(b.aggregate, self.label_of(column))
        return f"{text[:1].upper()}{text[1:]}".strip()

    def category_label(self) -> str:
        column = self.cross_column()
        return self.label_of(column) if column else ""

    def colour_for(self, key: tuple[str, ...]) -> RGB:
        """The colour of one mark.

        A view sharing a plotting area is one colour throughout -- what separates it
        from the other view is which series it is, not which category. Otherwise the
        series names the colour when there is one, and the category when there is not.
        """
        if self.view.prefix_names_a_series:
            name = self.view.key_prefix[0]
        else:
            name = key[-1] if len(key) > 1 else (key[0] if key else "")
        return self.series_colors.get(name, next(iter(self.series_colors.values()),
                                                 (31, 78, 121)))

    def shape_kwargs(self, rgb: RGB, thickness: float | None = None) -> dict:
        """Patch keywords every filled shape takes: edge, fill pattern, shadow.

        Collected in one place because the four shapes that take them would
        otherwise each grow their own copy of the same style branches.

        `thickness` is how many pixels across the shape is at its narrowest. The edge
        is drawn in the page background and is stroked half inside the shape, so on a
        shape thinner than about twice the edge width the edge paints the shape out
        entirely -- and the record still says there is a mark there, with a value that
        can be read off it. The edge is thinned to fit rather than the mark being
        dropped: what is drawn has to be what was recorded.
        """
        s = self.style
        width = s.edge_width
        if thickness is not None and width:
            width = min(width, max(0.0, thickness * 72.0 / self.style.dpi * MAX_EDGE_SHARE))
        out: dict = {
            "facecolor": hex_of(rgb),
            "edgecolor": hex_of(BACKGROUND) if width else "none",
            "linewidth": width,
            "hatch": s.hatch,
        }
        if s.shadow:
            from matplotlib.patheffects import withSimplePatchShadow

            # The shadow's own colour is given rather than derived from the fill.
            # Left to derive it, the effect reads the fill colour back out of the
            # renderer, and for a filled band that arrives as an array it cannot use.
            out["path_effects"] = [withSimplePatchShadow(
                offset=(2, -2), alpha=0.25, shadow_rgbFace=hex_of(SHADOW))]
        if s.pseudo_3d:
            out["edgecolor"] = hex_of(tuple(max(0, c - 45) for c in rgb))  # type: ignore[arg-type]
            out["linewidth"] = max(s.edge_width, 1.6)
        return out
