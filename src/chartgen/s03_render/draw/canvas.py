"""The canvas, its panels, axes, legend and text, and the record they write as they draw.

Drawing and recording are the same step. A mark's box, key and value are written
together at the moment it is drawn, because that is the only moment all three are
in hand; the box comes from the plotting library's own coordinate transform, never
from parsing the finished image.

The layout is frozen: image size, dpi and every plotting rectangle are constants.
Auto-layout moves the plotting area after the drawing is done, which invalidates
every box already recorded -- and does so without raising anything. The bands above
and below the plotting area keep their height whether or not anything is written in
them, for the same reason: a figure that grew a subtitle would otherwise move every
mark it had already recorded.

Text is measured in one pass. Asking the library for the box of each label as it is
written redraws the whole figure once per label, which at four hundred marks is
four hundred full redraws; instead every label is deferred and `flush_text` draws
once and measures them all.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, Sequence

from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from ...common.geometry import Box, axes_rect, rect_to_mpl_fraction
from ...interfaces.figure import TextBlock
from ...interfaces.record import (
    Axis, AxisRole, Channel, Element, KeySource, Layout, LegendEntry, Mark, MarkShape,
    Panel,
)
from ...interfaces.style import StyleVector
from ..style import (
    BACKGROUND, GRID_COLOR, MARGIN_SETS, PANEL_TINTS, RGB, TEXT_COLOR, block_spans,
    gutters, hex_of, resolve_font,
)
from .layout import SIDES, Block, compose

#: The three blocks cut out of the image around the plotting area. Which edge each
#: one takes is settled by the style before anything is drawn; the geometry is in
#: `layout.compose`, and these are the names it is asked for by.
TEXT_BAND = "text"
LEGEND_BAND = "legend"
FOOT_BAND = "foot"

#: How wide a legend down the side of the image may grow, as a share of the image.
#: Past this it is taking room the plotting area needs more than the names do.
SIDE_LEGEND_CAP = 0.28

#: Height of the title strip reserved above each panel of a multi-panel figure.
PANEL_TITLE_HEIGHT = 22.0

#: How much of a shape's narrowest dimension its own edge may take up. Past this the
#: edge is what the reader sees and the fill is what is left.
MAX_EDGE_SHARE = 0.2

#: How tall a tick label's glyphs are never shrunk past, **in pixels**. Below this the
#: string is on the page but no longer legible, and a key that cannot be read off the
#: page cannot be checked against it.
#:
#: In pixels rather than in points because dpi is a style dimension and the margins
#: are pixels: the same type size comes out twice as tall at a hundred and fifty dots
#: per inch as at seventy-two, so a floor in points is a different floor on legibility
#: at each of them -- and at the coarse end it stops the shrinking before the labels
#: fit, which is how a second row of tick labels ended up written across the figure's
#: own title. Seven and a half pixels is the old floor of five and a half points at
#: the default hundred dots per inch.
MIN_TICK_PIXELS = 7.6

#: How close to the left edge anything an axis draws may come.
LEFT_EDGE = 3.0

#: How wide one character is, as a share of the type size. Used to decide whether the
#: category names fit side by side before anything is drawn: measuring them would cost
#: one full redraw per panel, and the fitting pass corrects the estimate afterwards.
CHAR_WIDTH = 0.55

#: Angles the category labels may be raised to when they do not fit. The style's own
#: value is the floor, so a batch that asks for slanted labels gets them whether or
#: not they were needed. Ninety degrees is not on the list: a name set on its side is
#: legible but reads poorly, so it is an angle a style may ask for and never one
#: arrived at by fitting.
ROTATION_STEPS = (0.0, 30.0, 45.0)

#: Clear pixels a value label needs on every side before it counts as separable from
#: what is already on the page. A share of overlap was the test before, and it cannot
#: see the case it most needs to: two labels that butt against each other overlap by
#: nothing and read as one string.
LABEL_GAP = 2.0

#: Clear pixels asked for between two neighbouring tick labels.
TICK_GAP = 4.0

#: Legend swatch geometry, in pixels.
SWATCH = (18.0, 12.0)
LEGEND_GAP = 18.0


@dataclass
class PanelCanvas:
    """One panel: a set of plotting axes, plus the axes and marks it has recorded."""

    panel_id: str
    ax: Axes
    rect: Box
    image_height: int
    chart_types: list[str] = field(default_factory=list)
    axes: list[Axis] = field(default_factory=list)
    marks: list[Mark] = field(default_factory=list)
    right_ax: Axes | None = None
    #: Whether a panel title is written in the strip above this plotting area. An
    #: axis title placed above would be written on top of it.
    has_title: bool = False
    #: The angle the category names ended up at. The style states what a batch asked
    #: for; this is what the fitting settled on, and it is what the record carries.
    tick_rotation: float = 0.0
    #: The circle wedges are cut from, when this panel holds a pie. Written by the
    #: sector drawer, because that is where the centre and the radii are decided.
    circle: tuple[float, float, float, float] | None = None
    #: The value-axis title when the style put it above the plotting area rather than
    #: beside it. Kept because it is the one axis title placed by an offset instead of
    #: by the fitting pass, and it is the one that can reach the figure's text band.
    above_title: Any = None
    #: Artists drawn below the category axis that are not tick labels -- the second
    #: row of tick labels. They are part of what has to fit above the next band.
    below: list[Any] = field(default_factory=list)
    #: Axes whose title a drawer has already placed somewhere of its own choosing. A
    #: heatmap puts its value title in the clear strip above the grid, because the
    #: axis it would otherwise sit beside carries row names here; moving it back
    #: would write it across the cells.
    placed_titles: set[str] = field(default_factory=set)

    # ---- coordinates: data, through the library's transform, to pixels with a top-left origin

    def to_pixel(self, x: float, y: float, right: bool = False) -> tuple[float, float]:
        ax = self.right_ax if right and self.right_ax is not None else self.ax
        px, py = ax.transData.transform((x, y))
        return (float(px), float(self.image_height - py))

    def box_from_data(self, x0: float, y0: float, x1: float, y1: float,
                      right: bool = False) -> Box:
        a = self.to_pixel(x0, y0, right)
        b = self.to_pixel(x1, y1, right)
        return Box(a[0], a[1], b[0], b[1])

    # ---- recording

    def record_axis(self, role: AxisRole, column: str | None = None,
                    scale: str = "linear", label: str = "") -> Axis:
        if role == "x":
            lo, hi = self.ax.get_xlim()
            pixel_range = (self.to_pixel(lo, 0)[0], self.to_pixel(hi, 0)[0])
        else:
            right = role == "y_right"
            source = self.right_ax if right else self.ax
            lo, hi = source.get_ylim()
            pixel_range = (self.to_pixel(0, lo, right)[1], self.to_pixel(0, hi, right)[1])
        axis = Axis(role, (float(lo), float(hi)), pixel_range, scale, column, label,
                    tick_rotation=self.tick_rotation)
        existing = self.axis(role)
        if existing is not None:
            # Two views sharing one value axis record it once. A second entry under
            # the same role would be a second axis in the record where the image has
            # one, and every reader takes the first anyway.
            return existing
        self.axes.append(axis)
        return axis

    def add_mark(self, key: tuple[str, ...], values: dict[str, float], box: Box,
                 channel: Channel, *, mark_shape: MarkShape, value_axis: AxisRole = "y",
                 key_src: Sequence[KeySource] = (), labeled: bool = False,
                 label_box: Box | None = None) -> int:
        """Write one mark and return where it sits, so a deferred label can find it."""
        self.marks.append(Mark(
            f"m{len(self.marks)}", self.panel_id, tuple(key), dict(values), box, channel,
            labeled=labeled, label_box=label_box, value_axis=value_axis,
            mark_shape=mark_shape, key_src=tuple(key_src)))
        return len(self.marks) - 1

    def axis(self, role: str) -> Axis | None:
        return next((a for a in self.axes if a.role == role), None)

    def to_panel(self) -> Panel:
        return Panel(self.panel_id, self.rect, tuple(self.axes), tuple(self.chart_types),
                     circle=self.circle)


class Canvas:
    """The canvas for one image. Owns the figure and hands out panels, legend entries,
    text blocks and page elements."""

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
        self._pending: list[tuple[Any, Callable[[Box], None]]] = []
        #: Value labels, held back from the measuring queue until it is known which
        #: of them a reader could tell apart. See `_resolve_label_overlaps`.
        self.labels: list[tuple[Any, PanelCanvas, Callable[[Box], None]]] = []
        #: Whether the legend took the band below the axis title. Recorded as it is
        #: drawn, because the legend's own entries are measured later and the axis
        #: titles have to be kept out of that band before anything is measured.
        self._legend_band_used = False
        #: The composed layout, and the measured width a side legend asked for. Both
        #: settled before the first panel: `add_panel` reads the plotting rectangle,
        #: and a block that moved afterwards would move every box drawn against it.
        self._layout: Layout | None = None
        self._side_thickness: float | None = None

    # ---- panels

    @property
    def min_font(self) -> float:
        """The smallest type size still legible at this dpi, in points.

        The floor is on how tall the glyphs come out in pixels, because that is what
        decides whether a string can be read off the page; a floor in points would be
        a different floor on legibility at each dpi.
        """
        return MIN_TICK_PIXELS * 72.0 / self.style.dpi

    @property
    def margins(self) -> dict[str, float]:
        """The budget each edge of the image has, in pixels.

        A style dimension rather than a constant: real reports vary how much white
        space they leave, and this is what decides how large the plotting area is at
        a given image size. What is cut out of each budget -- the room the axis keeps
        and the blocks stacked outside it -- is `layout.compose`'s business.
        """
        return MARGIN_SETS[self.style.margins]

    def _compose(self) -> Layout:
        """Cut the image into blocks. Called once, before anything is drawn.

        Which edge each block takes comes from the style. A block moved to a side
        brings its own thickness, because a side has no band it can take a share of:
        the left and right budgets are all gutter, held for tick labels and the axis
        title.
        """
        margins = self.margins
        spans = block_spans(margins)
        width = self.style.image_size[0]
        blocks: list[Block] = []
        for name in ("text", "legend", "foot"):
            edge = self._edge_of(name)
            lead, thickness, trail = spans[name]
            if edge in SIDES:
                thickness = min(self._side_thickness or thickness,
                                SIDE_LEGEND_CAP * width)
                lead, trail = 8.0, 8.0
            blocks.append(Block(name, edge, lead, thickness, trail,
                                occupied=name != "legend" or self.style.legend_placement
                                == "outside"))
        return compose(self.style.image_size, gutters(margins), blocks)

    def _edge_of(self, name: str) -> str:
        """Which edge a block takes on this rendering."""
        if name == "text":
            return "top" if self.style.title_placement == "above" else "bottom"
        if name == "foot":
            return "bottom" if self.style.title_placement == "above" else "top"
        return self.style.legend_edge

    @property
    def layout(self) -> Layout:
        if self._layout is None:
            self._layout = self._compose()
        return self._layout

    def full_rect(self) -> Box:
        return self.layout.plot

    def band(self, name: str) -> Box:
        """One block's box, in the coordinates of this image size and margin set.

        Fixed before anything is drawn and kept whether or not the block holds
        anything, because a block that appeared only when something needed it would
        move the plotting area and invalidate every box recorded against it.
        """
        found = self.layout.block(name)
        return found.box if found else Box(0.0, 0.0, 0.0, 0.0)

    def add_panel(self, panel_id: str, rect: Box, chart_types: Sequence[str],
                  has_title: bool = False) -> PanelCanvas:
        ax = self.fig.add_axes(rect_to_mpl_fraction(rect, self.style.image_size))
        panel = PanelCanvas(panel_id, ax, rect, self.style.image_size[1], list(chart_types),
                            has_title=has_title)
        self._style_axes(ax)
        self.panels.append(panel)
        return panel

    def _style_axes(self, ax: Axes) -> None:
        """Everything about a plotting area that no mark decides: its background, its
        gridlines, its spines, its tick size, and whether zero is drawn."""
        s = self.style
        ax.set_facecolor(hex_of(PANEL_TINTS.get(s.panel_bg, BACKGROUND)))
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            ax.spines[spine].set_color(hex_of(TEXT_COLOR))
            ax.spines[spine].set_linewidth(0.8)
        ax.tick_params(colors=hex_of(TEXT_COLOR), labelsize=s.font_size)
        if s.gridlines:
            ax.set_axisbelow(True)
            ax.grid(axis="y", color=hex_of(GRID_COLOR), linewidth=0.8)
        if s.panel_bg == "grid_band":
            ax.set_axisbelow(True)
            ax.grid(axis="y", color=hex_of(GRID_COLOR), linewidth=8.0, alpha=0.35)

    def zero_line(self, panel: PanelCanvas) -> None:
        """A line at zero, for a panel whose values cross it."""
        lo, hi = panel.ax.get_ylim()
        if self.style.zero_line and lo < 0 < hi:
            panel.ax.axhline(0.0, color=hex_of(TEXT_COLOR), linewidth=1.0)

    def add_twin(self, panel: PanelCanvas) -> Axes:
        """A second value axis. Each one records its own value and pixel range,
        because the same pixel height then means two different values."""
        panel.right_ax = panel.ax.twinx()
        panel.right_ax.spines["top"].set_visible(False)
        panel.right_ax.spines["right"].set_visible(True)
        panel.right_ax.spines["right"].set_color(hex_of(TEXT_COLOR))
        panel.right_ax.tick_params(colors=hex_of(TEXT_COLOR), labelsize=self.style.font_size)
        return panel.right_ax

    # ---- axis furniture

    def category_axis(self, panel: PanelCanvas, labels: Sequence[str], *,
                      horizontal: bool = False, is_time: bool = False,
                      groups: Sequence[str] = ()) -> None:
        """Tick labels on the category axis: how they read and how they are arranged.

        Which axis is the category axis is the frame's decision, not the style's. A
        point series is never turned however the style is sampled, and writing the
        categories down the side of one would overwrite the axis its values were
        measured against.
        """
        s = self.style
        shown = [_tick_text(t, s, is_time) for t in labels]
        rotation = s.label_rotation if horizontal else fitting_rotation(
            shown, s, panel.rect.width)
        setter = panel.ax.set_yticks if horizontal else panel.ax.set_xticks
        setter(range(len(labels)), shown, rotation=rotation,
               ha="right" if rotation and not horizontal else
                  ("right" if horizontal else "center"),
               fontsize=s.font_size)
        panel.tick_rotation = rotation
        # A tick label is where a key is read from, so where it landed is worth the
        # same box the value gets. Deferred like every other measurement: the fitting
        # pass may still shrink or slant these, and the box has to be the one drawn.
        for artist, text in zip(
                panel.ax.get_yticklabels() if horizontal else panel.ax.get_xticklabels(),
                shown):
            self.defer(artist, lambda box, text=text: self.add_element(box, "axis_tick", text))
        if s.two_level_x_labels and groups and not horizontal:
            self._second_level(panel, groups)

    def _second_level(self, panel: PanelCanvas, groups: Sequence[str]) -> None:
        """A second row of tick labels naming the group each tick belongs to."""
        seen: dict[str, list[int]] = {}
        for i, g in enumerate(groups):
            seen.setdefault(g, []).append(i)
        for name, positions in seen.items():
            centre = sum(positions) / len(positions)
            artist = panel.ax.annotate(
                name, xy=(centre, 0), xycoords=("data", "axes fraction"),
                xytext=(0, -34), textcoords="offset points", ha="center", va="top",
                fontsize=self.style.font_size - 1, color=hex_of(TEXT_COLOR))
            panel.below.append(artist)
            self.defer(artist, lambda box, text=name: self.add_element(box, "axis_title", text))

    def second_axis_title(self, panel: PanelCanvas, text: str,
                          unit: str | None = None) -> None:
        """The name of the second value axis, written down the right margin.

        The room on the right is held for this axis whether or not a figure has one,
        so writing the title there moves nothing already recorded. Without it the
        record names a quantity -- the axis carries a label either way -- that is
        written nowhere on the page, and a question asked in that name asks the reader
        to know the table.
        """
        if panel.right_ax is None or not text:
            return
        s = self.style
        written = text + (f" ({unit})" if unit and s.unit_placement == "axis_title" else "")
        written = self.fit(written, panel.rect.height, s.font_size)
        artist = panel.right_ax.set_ylabel(written, fontsize=s.font_size,
                                           color=hex_of(TEXT_COLOR))
        self.defer(artist, lambda box: self.add_element(box, "axis_title", written))

    def axis_title(self, panel: PanelCanvas, *, value: str, category: str,
                   unit: str | None = None, horizontal: bool = False) -> None:
        """The two axis titles, and where the unit is written.

        The unit has four homes and only one of them is the axis title. Which one it
        took is worth recording, because a value's unit is often written in exactly
        one place on a real page.
        """
        s = self.style
        value_text = value + (f" ({unit})" if unit and s.unit_placement == "axis_title" else "")
        # An axis title runs along the side of the panel it names, so that side is all
        # the room it has. Cut to it: unlike a tick label or a legend entry, no key is
        # ever read off an axis title, so shortening one costs nothing.
        along = panel.rect.width if horizontal else panel.rect.height
        value_text = self.fit(value_text, along, s.font_size)
        category = self.fit(category, panel.rect.height if horizontal else panel.rect.width,
                            s.font_size)
        if s.axis_title_above and not panel.has_title:
            artist = panel.ax.annotate(
                value_text, xy=(0.0, 1.0), xycoords="axes fraction", xytext=(0, 8),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=s.font_size, color=hex_of(TEXT_COLOR))
            panel.above_title = artist if value_text else None
            if value_text:
                self.defer(artist,
                           lambda box: self.add_element(box, "axis_title", value_text))
        else:
            setter = panel.ax.set_xlabel if horizontal else panel.ax.set_ylabel
            artist = setter(value_text, fontsize=s.font_size, color=hex_of(TEXT_COLOR))
            if value_text:
                self.defer(artist,
                           lambda box: self.add_element(box, "axis_title", value_text))
        other = panel.ax.set_ylabel if horizontal else panel.ax.set_xlabel
        artist = other(category, fontsize=s.font_size, color=hex_of(TEXT_COLOR))
        if category:
            # An axis with no title draws nothing, and an element recorded for it
            # would be an empty box at the row the title would have been on.
            self.defer(artist, lambda box: self.add_element(box, "axis_title", category))

    # ---- text

    def defer(self, artist: Any, then: Callable[[Box], None]) -> None:
        """Measure this artist on the next flush. One redraw serves every label."""
        self._pending.append((artist, then))

    def drop(self, artist: Any) -> None:
        """Take an artist off the page, and off the list of things to be measured.

        Clearing the text alone is not enough: the measurement was already queued and
        would record a box for a string nobody can see, which is the one thing a
        record may never carry.
        """
        artist.set_text("")
        self._pending = [(a, then) for a, then in self._pending if a is not artist]

    def defer_label(self, artist: Any, panel: PanelCanvas,
                    then: Callable[[Box], None]) -> None:
        """A value label, to be measured with the rest once the crowded ones are out."""
        self.labels.append((artist, panel, then))

    def keep(self, artist: Any, then: Callable[[Box], None]) -> None:
        """Put a held-back label back into the measuring queue."""
        self._pending.append((artist, then))

    def flush_text(self) -> None:
        """Draw once, then measure everything that was deferred."""
        if not self._pending:
            return
        self.fig.canvas.draw()
        pending, self._pending = self._pending, []
        for artist, then in pending:
            then(self.text_box(artist))

    def text_box(self, artist) -> Box:
        """The pixel box of any piece of text."""
        renderer = self.fig.canvas.get_renderer()
        bbox = artist.get_window_extent(renderer)
        h = self.style.image_size[1]
        return Box(bbox.x0, h - bbox.y1, bbox.x1, h - bbox.y0)

    def measure(self, text: str, size: float, weight: str = "normal") -> float:
        """How wide this string comes out, asked of the renderer that will draw it.

        Asked rather than estimated, because the layout has to hold before anything is
        drawn: a block laid out from a guessed width overruns the room it was given
        and is written over its neighbour.
        """
        from matplotlib.font_manager import FontProperties

        renderer = self.fig.canvas.get_renderer()
        prop = FontProperties(family=self.font, size=size, weight=weight)
        return float(renderer.get_text_width_height_descent(text, prop, False)[0])

    def text_height(self, text: str, size: float, weight: str = "normal") -> float:
        """How tall this string comes out, in pixels. Ascender to descender, because
        that is the box it will be measured in afterwards."""
        from matplotlib.font_manager import FontProperties

        renderer = self.fig.canvas.get_renderer()
        prop = FontProperties(family=self.font, size=size, weight=weight)
        width, height, descent = renderer.get_text_width_height_descent(text, prop, False)
        return float(height + descent)

    def fit(self, text: str, width: float, size: float, weight: str = "normal") -> str:
        """The text, cut to what this much room can hold, with an ellipsis where it
        was cut. What the record stores is the string that came out on the page."""
        if not text or self.measure(text, size, weight) <= width:
            return text
        room = max(1, int(len(text) * width / max(self.measure(text, size, weight), 1e-6)))
        while room > 1 and self.measure(text[:room - 1] + "\u2026", size, weight) > width:
            room -= 1
        return text[:room - 1].rstrip() + "\u2026" if room > 1 else "\u2026"

    def write_text(self, block: TextBlock, box: Box, *, size: float, weight: str = "normal",
                   colour: RGB = TEXT_COLOR, panel_id: str = "") -> None:
        """Put one block of text on the page and record what came out.

        What the record stores is the string that was drawn, not the string that was
        asked for: wrapping, truncation and a footnote marker all change it, and the
        page is the ground truth.
        """
        w, h = self.style.image_size
        text = block.text + ("*" if self.style.footnote_marker and
                             block.role in ("title", "unit") else "")
        text = self.fit(text, box.width, size, weight)
        artist = self.fig.text(box.x0 / w, 1.0 - box.y1 / h, text, ha="left", va="bottom",
                               fontsize=size, fontweight=weight, color=hex_of(colour))
        self.defer(artist, lambda got: self.add_element(
            got.clip_to(Box(0, 0, w, h)), block.role, text, panel_id))

    def add_element(self, box: Box, category: str, text: str = "",
                    panel_id: str = "") -> None:
        self.elements.append(Element(box, category, text, panel_id))  # type: ignore[arg-type]

    # ---- legend

    def draw_legend(self, colours: dict[str, RGB], governs: dict[str, tuple[str, ...]],
                    *, panel: PanelCanvas | None = None,
                    marker: dict[str, str] | None = None) -> None:
        """One legend, and the panels each of its entries governs.

        On a single-panel figure every entry governs that one panel and says nothing.
        It carries information when several panels share one legend, which is the
        whole content of the legend-binding target -- and which is why the figure, not
        the style, decides whether the panels may share one.
        """
        if not colours:
            return
        entries = [(name, colours[name]) for name in colours]
        if self.style.legend_placement == "per_panel":
            # One legend per panel, each listing only what its own panel draws. It is
            # what a figure whose panels do not share a series column has to fall back
            # to, and it is why a shared legend is worth a constraint of its own.
            for own in self.panels:
                mine = [(n, c) for n, c in entries if own.panel_id in governs.get(n, ())]
                self._legend_inside(mine, {n: (own.panel_id,) for n, _ in mine},
                                    own, marker or {})
            return
        if self.style.legend_placement == "inside" and panel is not None:
            self._legend_inside(entries, governs, panel, marker or {})
            return
        self._legend_band(entries, governs, marker or {})

    def _entry_size(self, names: Sequence[str], room: float, per_entry: bool,
                    height: float | None = None) -> float:
        """Type size for the legend: the largest that keeps every entry inside the room
        it has. A legend is a key source, so its text is never cut short while there
        is still a size that fits.

        `height` is the band's own height, and it binds as often as the width does: a
        type size is in points while a band is in pixels, so the same entry comes out
        twice as tall at a hundred and fifty dots per inch as at seventy-two, and a
        band sized for the coarse end is overflowed at the fine end -- upwards, into
        the row the category axis title sits on.
        """
        size = self.style.font_size - 1
        while size > self.min_font:
            widths = [SWATCH[0] + 5 + self.measure(n, size) for n in names]
            fits = (max(widths, default=0.0) if per_entry
                    else sum(w + LEGEND_GAP for w in widths)) <= room
            if height is not None:
                fits = fits and max((self.text_height(n, size) for n in names),
                                    default=0.0) <= height
            if fits:
                break
            size -= 0.5
        return size

    def plan_side_legend(self, names: Sequence[str]) -> None:
        """Measure how wide a legend down the side needs to be, before composing.

        Asked before the first panel exists, because the answer decides where the
        plotting area starts. What it measures is text, not an artist: a legend
        column is as wide as its longest entry, and that is known from the names.
        """
        if not names or self.style.legend_edge not in SIDES:
            return
        cap = SIDE_LEGEND_CAP * self.style.image_size[0]
        size = self.style.font_size - 1
        while size > self.min_font:
            want = SWATCH[0] + 5 + max(self.measure(n, size) for n in names)
            if want <= cap:
                self._side_thickness = want
                return
            size -= 0.5
        # Nothing legible fits down the side. The legend goes back to the bottom, and
        # `Layout.legend_edge` is what says so: the style states the request and the
        # record has to state the result.
        self._side_thickness = None
        self.style = replace(self.style, legend_edge="bottom")

    def _legend_band(self, entries, governs, marker) -> None:
        box = self.band(LEGEND_BAND)
        self._legend_band_used = bool(entries)
        if self.layout.edge_of(LEGEND_BAND) in SIDES:
            self._legend_column(entries, governs, box, marker)
            return
        size = self._entry_size([n for n, _ in entries], box.width, per_entry=False,
                                height=box.height)
        x = box.x0
        for name, rgb in entries:
            swatch = Box(x, box.y0, x + SWATCH[0], box.y0 + SWATCH[1])
            self._swatch(swatch, rgb, marker.get(name))
            shown = self.fit(name, box.x1 - swatch.x1 - 5, size)
            artist = self.fig.text(
                (swatch.x1 + 5) / self.style.image_size[0],
                1.0 - box.y1 / self.style.image_size[1] + 0.004,
                shown, ha="left", va="bottom", fontsize=size, color=hex_of(TEXT_COLOR))
            self.defer(artist, lambda got, n=name, s=swatch: self._legend_entry(
                Box(s.x0, min(s.y0, got.y0), got.x1, max(s.y1, got.y1)),
                n, governs.get(n, ())))
            x = swatch.x1 + 5 + self.measure(name, size) + LEGEND_GAP

    def _legend_column(self, entries, governs, box: Box, marker) -> None:
        """A legend down one side of the image: one entry per row, top down."""
        names = [n for n, _ in entries]
        size = self._entry_size(names, box.width, per_entry=True)
        self._legend_rows(entries, governs, box.x0, box.y0 + 4, box.x1, size, marker)

    def _legend_inside(self, entries, governs, panel: PanelCanvas, marker) -> None:
        names = [n for n, _ in entries]
        size = self._entry_size(names, panel.rect.width - 12, per_entry=True)
        widest = max((SWATCH[0] + 5 + self.measure(n, size) for n in names), default=0.0)
        # Pulled back from the right edge by as much as the longest entry needs, so a
        # legend of long series names stays inside the plotting area instead of
        # running off the image.
        x = max(panel.rect.x0 + 6, panel.rect.x1 - 6 - widest)
        self._legend_rows(entries, governs, x, panel.rect.y0 + 10,
                          panel.rect.x1 - 4, size, marker)

    def _legend_rows(self, entries, governs, x: float, y: float, right: float,
                     size: float, marker) -> None:
        """One entry per row, swatch then name, top down from `y`.

        Written twice before this: once for a legend inside the plotting area and
        once for one down the side of the image. They differ in where the column
        starts and in nothing else.
        """
        for name, rgb in entries:
            swatch = Box(x, y, x + SWATCH[0], y + SWATCH[1])
            self._swatch(swatch, rgb, marker.get(name))
            shown = self.fit(name, right - swatch.x1 - 5, size)
            artist = self.fig.text(
                (swatch.x1 + 5) / self.style.image_size[0],
                1.0 - (y + SWATCH[1]) / self.style.image_size[1],
                shown, ha="left", va="bottom", fontsize=size, color=hex_of(TEXT_COLOR))
            self.defer(artist, lambda got, n=name, s=swatch: self._legend_entry(
                Box(s.x0, min(s.y0, got.y0), got.x1, max(s.y1, got.y1)),
                n, governs.get(n, ())))
            y += SWATCH[1] + 8

    def _swatch(self, box: Box, rgb: RGB, marker: str | None) -> None:
        from matplotlib.patches import Rectangle

        w, h = self.style.image_size
        self.fig.patches.append(Rectangle(
            (box.x0 / w, 1.0 - box.y1 / h), box.width / w, box.height / h,
            transform=self.fig.transFigure, facecolor=hex_of(rgb),
            edgecolor="none", zorder=5))

    def _legend_entry(self, box: Box, name: str, panels: tuple[str, ...]) -> None:
        box = box.clip_to(Box(0, 0, *self.style.image_size))
        self.legend.append(LegendEntry(box, name, panels))
        self.add_element(box, "legend_title", name)

    # ---- saving

    def legend_in_band(self) -> bool:
        """Whether the legend took the band below the axis title."""
        return self._legend_band_used

    def shrink_ticks(self, factor: float) -> bool:
        """Take one step down in tick type size. False when there is no step left.

        The second row of tick labels shrinks with the first. It names the group each
        tick belongs to, so it is a tick label by every rule that matters here: it is
        read for a key, and what gives when the room runs out is its type size.
        """
        moved = False
        floor = self.min_font
        for panel in self.panels:
            for label in (*panel.ax.get_xticklabels(), *panel.ax.get_yticklabels(),
                          *panel.below):
                size = label.get_fontsize()
                new = max(floor, size / factor)
                if new < size - 1e-9:
                    label.set_fontsize(new)
                    moved = True
        return moved

    def flatten_ticks(self) -> bool:
        """Take one step out of the slant of the category labels. False when flat.

        The slant buys width and spends height. On one plotting area that trade is
        always worth making -- the room under the axis is a whole margin. On a grid it
        is not: under a panel on the first row sits the next row's title strip, and a
        forty-five degree name reaches into it. Names run together are two keys nobody
        can read; a name written across the panel title above the panel below is one
        key nobody can read, and the panel title is the segment saying which panel the
        marks belong to.
        """
        moved = False
        for panel in self.panels:
            if not panel.tick_rotation:
                continue
            steps = [r for r in ROTATION_STEPS if r < panel.tick_rotation]
            panel.tick_rotation = max(steps) if steps else 0.0
            for label in panel.ax.get_xticklabels():
                label.set_rotation(panel.tick_rotation)
                label.set_ha("right" if panel.tick_rotation else "center")
            moved = True
        return moved

    def shrink_axis_titles(self, factor: float) -> bool:
        """Take one step down in axis-title type size. False when there is none left.

        Asked for only once the tick labels have reached their floor. An axis title
        names the quantity, not a key, so it is the next thing to give -- and it
        already gets cut to the edge it runs along, which a tick label never does.
        """
        moved = False
        floor = self.min_font
        for panel in self.panels:
            for label in (panel.ax.xaxis.label, panel.ax.yaxis.label):
                if not label.get_text():
                    continue
                size = label.get_fontsize()
                new = max(floor, size / factor)
                if new < size - 1e-9:
                    label.set_fontsize(new)
                    moved = True
        return moved

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Imported here rather than at the top: the fitting passes are written
        # against the canvas, so the two modules would import each other.
        from . import fit

        fit.everything(self)
        self.flush_text()
        self.fig.savefig(path, dpi=self.style.dpi,
                         facecolor=self.fig.get_facecolor(),
                         metadata={"Software": "chartgen"})
        return path


def fitting_rotation(labels: Sequence[str], style: StyleVector, width: float) -> float:
    """The angle the category names are written at.

    Real reports slant a crowded category axis before they shrink it. Shrinking used
    to be the only thing on offer here, so long names went down to the smallest
    legible type size while the axis stayed horizontal. Rotation is tried first now,
    and the type size is what gives after that.

    A rotated label takes its own height across the axis rather than its length, so
    a steeper angle needs less room -- which is why the first angle that fits is the
    shallowest one that fits.
    """
    if not labels:
        return style.label_rotation
    slot = width / max(len(labels), 1)
    longest = max(len(t) for t in labels) * style.font_size * CHAR_WIDTH
    for angle in ROTATION_STEPS:
        if angle < style.label_rotation:
            continue
        across = longest if not angle else style.font_size * 1.2 / math.sin(math.radians(angle))
        if across <= slot:
            return angle
    return max(style.label_rotation, ROTATION_STEPS[-1])


def _tick_text(label: str, style: StyleVector, is_time: bool) -> str:
    """A tick label as it is drawn: shortened, wrapped, or left alone."""
    text = label
    if is_time and style.time_tick_format != "iso":
        text = _short_time(label, style.time_tick_format)
    if style.category_label_wrap and len(text) > 12 and " " in text:
        head, _, tail = text.partition(" ")
        text = f"{head}\n{tail}"
    return text


MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")




def _short_time(label: str, form: str) -> str:
    parts = label.split("-")
    if len(parts) < 2 or not parts[0].isdigit():
        return label
    month = MONTHS[int(parts[1]) - 1] if parts[1].isdigit() and 1 <= int(parts[1]) <= 12 else parts[1]
    if form == "compact":
        return f"{month} '{parts[0][2:]}"
    return f"{month} {parts[2]}" if len(parts) > 2 else month
