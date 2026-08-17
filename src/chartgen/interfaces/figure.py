"""What a figure is made of: the views inside it and how they relate.

A `Binding` names columns and an aggregate but holds no values, which is what
keeps the feasibility rules honest -- they take a binding and a schema, so they
structurally cannot look at data. A `ViewSpec` is a binding plus the values it
projects to. A `FigureSpec` is one or more views laid out together, with what they
share and where the figure came from.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .table import Aggregate, Family

Layout = Literal["single", "side_by_side", "grid", "dual_axis"]

#: How a second panel is derived from the first one.
Relation = Literal[
    "facet",       # same metric, a different slice
    "drilldown",   # one level deeper
    "time_split",  # the same view over two time windows
    "dual_metric", # the same grouping, the next metric
    "part_whole",  # comparison turned into composition
]

#: How a figure was chosen: built from an intent, derived from an anchor figure,
#: or sampled to widen chart-type coverage.
SourceKind = Literal["intent", "panel", "rotation"]


@dataclass(frozen=True)
class Binding:
    """The columns one candidate view would use. Names only, never values.

    `group_columns` is both the grouping order and the order of the key tuple in
    the records: the time column first, then category columns by role.
    """

    chart_type: str
    dims: tuple[str, ...] = ()        # category columns, primary then secondary
    time: str | None = None
    measures: tuple[str, ...] = ()
    aggregate: Aggregate = "NONE"
    resample: str | None = None       # daily, weekly or monthly for the time axis

    @property
    def group_columns(self) -> tuple[str, ...]:
        return ((self.time,) if self.time else ()) + self.dims

    @property
    def n_group(self) -> int:
        return len(self.group_columns)


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
    """What one panel draws: a binding, an optional row filter, and the values."""

    binding: Binding
    data: tuple[Datum, ...]
    row_filter: TimeWindow | None = None
    sample_index: tuple[int, ...] = ()   # rows kept when a per-row view is downsampled

    @property
    def keys(self) -> frozenset[tuple[str, ...]]:
        return frozenset(d.key for d in self.data)


@dataclass(frozen=True)
class PanelSpec:
    panel_id: str
    view: ViewSpec


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
    """One image to draw: which views go together, how they relate, what they share."""

    figure_id: str
    scenario_id: str
    panels: tuple[PanelSpec, ...]
    layout: Layout = "single"
    sharing: Sharing = Sharing()
    relation: Relation | None = None
    source: Source = Source(kind="rotation")
    #: Column to unit. The renderer needs it for axis labels and number formats,
    #: and copying it here means the renderer never has to read a table schema.
    column_units: dict[str, str] = field(default_factory=dict)

    @property
    def families(self) -> tuple[Family, ...]:
        from ..registry.charts import CHARTS
        return tuple(CHARTS[p.view.binding.chart_type].family for p in self.panels)
