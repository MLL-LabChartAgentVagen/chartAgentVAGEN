"""What a figure is made of: the views inside it, how they relate, and its text.

A `Binding` names columns and an aggregate but holds no values, which is what
keeps the feasibility rules honest -- they take a binding and a schema, so they
structurally cannot look at data. A `ViewSpec` is a binding plus the values it
projects to. A `PanelSpec` is one plotting area, which may hold more than one
view. A `FigureSpec` is one or more panels laid out together, with what they
share, where the figure came from, and the text drawn around it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .record import KeySource, TextRole
from .table import Aggregate, Family

#: How the panels of a figure are arranged. `overlay` is two views in one plotting
#: area; whether that needs a second value axis follows from the units, not from
#: the layout, so it is not part of this name.
Layout = Literal["single", "side_by_side", "grid", "overlay"]

#: How a second view is derived from the first one. The first six put it in its own
#: plotting area, the last three put it in the same one.
Relation = Literal[
    "facet",           # same metric, a different slice
    "small_multiples", # the same view repeated, one panel per value of a column
    "drilldown",       # one level deeper
    "time_split",      # the same view over two time windows
    "dual_metric",     # the same grouping, the next metric
    "part_whole",      # comparison turned into composition
    "overlay_metric",  # one grouping, two measures, one plotting area
    "overlay_slice",   # one measure, two row filters or two aggregates
    "overlay_range",   # a scalar and the spread around it
]

#: How a figure was chosen: built from an intent, derived from an anchor figure
#: into a second panel or into the same panel, or sampled to widen type coverage.
SourceKind = Literal["intent", "panel", "overlay", "page", "rotation"]

#: Where a block of text sits relative to what it belongs to.
Placement = Literal["above", "below", "left", "right", "inside"]

#: What a block of text belongs to.
TextScope = Literal["page", "figure", "panel"]


@dataclass(frozen=True)
class Binding:
    """The columns one candidate view would use. Names only, never values.

    `group_columns` is both the grouping order and the order of the key tuple in
    the records: the time column first, then category columns by role.

    `key_sources` runs parallel to `group_columns` and says where each segment of
    the key will be drawn -- an axis tick, a legend entry, a panel title. It is a
    property of the figure, not of the style: the same data drawn as two panels
    puts the hospital name in a panel title, drawn as one panel it goes in the
    legend, and the key is the same either way.

    `colour_group` names the column carried by colour. It belongs here and not on
    the style vector: if style chose it, restyling a figure would change its keys
    and the style self-check would have nothing left to compare.
    """

    chart_type: str
    dims: tuple[str, ...] = ()        # category columns, primary then secondary
    time: str | None = None
    measures: tuple[str, ...] = ()
    aggregate: Aggregate = "NONE"
    resample: str | None = None       # daily, weekly or monthly for the time axis
    colour_group: str | None = None
    key_sources: tuple[KeySource, ...] = ()

    @property
    def group_columns(self) -> tuple[str, ...]:
        return ((self.time,) if self.time else ()) + self.dims

    @property
    def n_group(self) -> int:
        return len(self.group_columns)

    @property
    def n_key(self) -> int:
        """Segments a key of this view holds. A colour group adds one without
        grouping anything: it is carried by an existing column, so it changes what
        a mark is called and not which rows it covers."""
        return len(self.key_sources) or self.n_group

    def source_of(self, column: str) -> KeySource:
        """Where one grouping column's segment of the key is drawn."""
        cols = self.group_columns
        if column not in cols:
            raise KeyError(f"{column} does not group this view")
        i = cols.index(column)
        return self.key_sources[i] if i < len(self.key_sources) else "axis_tick"


@dataclass(frozen=True)
class TimeWindow:
    """A row filter. It exists only to show one view over two time windows, and is
    cut from the anchor when that pairing is built."""

    column: str
    start: str
    end: str
    label: str


@dataclass(frozen=True)
class Datum:
    """One projected result: a key, a value dictionary, and how many rows it covers.

    Which keys the value dictionary holds follows from the mark shape. `rows` is
    the provenance layer of the records, carried along rather than recomputed.
    """

    key: tuple[str, ...]
    values: dict[str, float]
    rows: int


@dataclass(frozen=True)
class ViewSpec:
    """What one view draws: a binding, an optional row filter, and the values.

    `key_prefix` names this view apart from another one carrying the same grouping
    columns. Two overlaid series group by the same columns, so without it their marks
    would land on the same `(panel_id, key)` with different numbers and the record
    could not be joined. What the prefix says is what a combo chart's legend says:
    which measure, which window, which statistic.

    `prefix_source` says where a reader finds it, and that decides more than the
    record: a prefix read off a legend is the name of a series, and colours and
    slots follow it; a prefix read off a panel title or a figure heading names the
    plotting area instead, and every view under it is drawn the same way as its
    neighbours.
    """

    binding: Binding
    data: tuple[Datum, ...]
    row_filter: TimeWindow | None = None
    sample_index: tuple[int, ...] = ()   # rows kept when a per-row view is downsampled
    key_prefix: tuple[str, ...] = ()
    prefix_source: tuple[KeySource, ...] = ()

    def full_key(self, datum: Datum) -> tuple[str, ...]:
        return self.key_prefix + datum.key

    def key_src(self, datum: Datum) -> tuple[KeySource, ...]:
        """Where each segment of this datum's key is read from. Segments past the
        declared grouping columns -- an outlier's own index -- are not written
        anywhere on the page."""
        declared = self.binding.key_sources or ("axis_tick",) * self.binding.n_group
        extra = len(datum.key) - len(declared)
        return self.prefix_source + tuple(declared) + ("not_shown",) * max(0, extra)

    @property
    def prefix_names_a_series(self) -> bool:
        """Whether the prefix is a series name, and so drawn as one."""
        return bool(self.key_prefix) and self.prefix_source[:1] not in (
            ("panel_title",), ("heading",))

    @property
    def keys(self) -> frozenset[tuple[str, ...]]:
        return frozenset(self.full_key(d) for d in self.data)


@dataclass(frozen=True)
class TextBlock:
    """One block of text outside the plotting area.

    One class with eight roles rather than a title class plus scattered style
    dimensions: a source line and a figure number differ in what they say and
    where they sit, not in what kind of object they are.
    """

    role: TextRole
    text: str
    scope: TextScope = "figure"
    placement: Placement = "above"


@dataclass(frozen=True)
class PanelSpec:
    """One plotting area. `views` holds more than one entry when two views are
    overlaid, which is the only way a single plotting area gets two mark shapes."""

    panel_id: str
    views: tuple[ViewSpec, ...]
    texts: tuple[TextBlock, ...] = ()

    @property
    def view(self) -> ViewSpec:
        """The first view. Most panels hold exactly one."""
        return self.views[0]


@dataclass(frozen=True)
class Sharing:
    """What the panels of a figure share. `series_column` is set only when the
    legend is shared, which requires every panel to colour by the same column."""

    share_x: bool = False
    share_y: bool = False
    share_legend: bool = False
    series_column: str | None = None


@dataclass(frozen=True)
class Source:
    """Where this figure came from."""

    kind: SourceKind
    intent_index: int | None = None
    anchor_figure_id: str | None = None


@dataclass(frozen=True)
class FigureSpec:
    """One image to draw: which views go together, how they relate, what they share.

    `column_units` and `column_names` are copied in so the renderer never has to
    read a table schema: the unit decides the number format, the prose name is what
    an axis title and a legend actually say.
    """

    figure_id: str
    scenario_id: str
    panels: tuple[PanelSpec, ...]
    layout: Layout = "single"
    sharing: Sharing = Sharing()
    relation: Relation | None = None
    source: Source = Source(kind="rotation")
    column_units: dict[str, str] = field(default_factory=dict)
    column_names: dict[str, str] = field(default_factory=dict)
    texts: tuple[TextBlock, ...] = ()
    page_id: str = ""
    #: A sentence about what this figure is for. Not drawn on the image: it is a
    #: training target, and its value is that it says something the image does not.
    caption: str = ""

    @property
    def views(self) -> tuple[ViewSpec, ...]:
        return tuple(v for p in self.panels for v in p.views)

    @property
    def chart_types(self) -> tuple[str, ...]:
        return tuple(v.binding.chart_type for v in self.views)

    @property
    def families(self) -> tuple[Family, ...]:
        from ..registry.charts import CHARTS
        return tuple(CHARTS[t].family for t in self.chart_types if CHARTS[t].family)

    def text(self, role: TextRole) -> str:
        return next((t.text for t in self.texts if t.role == role), "")

    def label_of(self, column: str) -> str:
        """The prose name of a column, falling back to the column name itself."""
        return self.column_names.get(column, column)
