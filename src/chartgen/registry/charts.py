"""The one place chart types are defined: six families, seventeen types.

Each type carries three kinds of condition, and when they can be decided differs:

    structural  reads column declarations only (how many columns in which role,
                what cardinality range, how many source rows)
    semantic    reads column declarations only (additivity, stage ordering,
                whether several measures share a unit)
    data        needs projected values (variation, distinctness, rows per cell,
                how many marks, monotonicity, smallest share)

Adding a chart type means adding one row here and one drawing branch. Nothing
else in the pipeline changes. A visual variant whose conditions, mark shape and
value keys are all identical to an existing row -- a filled pie against a donut --
does not get a row; it is a field on the style vector.

The table is really the product of a projection shape and a mark shape. `GRID`
below fills that product in: every cell either names a type or says why it is
empty, so a missing kind of chart is found by reading a grid rather than by
noticing it in someone else's benchmark.

The insertion order of `CHARTS` is the tie-break order within a family: when
several types fit an intent, the first one listed wins.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..interfaces.record import Channel, MarkShape
from ..interfaces.table import Family

#: How a view is projected out of the fact table. It decides how many keys the
#: value dictionary holds, which aggregates apply, which data conditions are
#: checked, and whether the provenance layer carries information.
Shape = Literal["grouped_scalar", "grouped_fivenum", "binned_count", "per_row"]

Bound = tuple[int, int | None]   # (lower, upper); None as the upper means unbounded

UNBOUNDED: Bound = (0, None)


@dataclass(frozen=True)
class ChartType:
    """One row of the table.

    `mark` and `channel` are tuples because a single view may draw more than one
    shape -- a box plot with its outliers, a windsock with its centre line. A panel
    that overlays two views simply concatenates two rows' worth.
    """

    name: str
    family: Family | None          # a table-shaped chart answers no view class; it is
                                   # reachable through the type weights, not through a family
    tier: int
    shape: Shape
    mark: tuple[MarkShape, ...]
    channel: tuple[Channel, ...]
    value_keys: tuple[str, ...]

    # ---- structural conditions, decidable from declarations
    n_cat: Bound = (0, 0)          # category columns
    n_time: Bound = (0, 0)         # time columns
    n_measure: Bound = (0, 0)      # measures
    n_group: Bound | None = None   # grouping columns in total; None means n_cat + n_time
    card: Bound | None = None      # size of the category cross product, when there is no time column
    points: Bound | None = None    # points on the time axis, when there is one
    series: Bound | None = None    # series drawn over time, the category cross product
    min_raw_rows: int = 0          # source rows the fact table must have

    # ---- semantic conditions, decidable from declarations
    require_additive: bool = False
    require_stage: bool = False
    require_same_unit: bool = False

    # ---- data conditions, decidable only after projection
    check_variation: bool = False
    check_distinct: bool = False
    min_rows_per_cell: int = 0
    n_marks: Bound | None = None       # marks drawn: scatter points, histogram bins
    monotone_decreasing: bool = False
    min_share: float = 0.0             # smallest share a sector may hold

    # ---- what the projection has to produce beyond the value keys
    outliers: bool = False             # rows outside the whiskers, each its own mark

    @property
    def group_bound(self) -> Bound:
        if self.n_group is not None:
            return self.n_group
        hi = None if self.n_cat[1] is None or self.n_time[1] is None else self.n_cat[1] + self.n_time[1]
        return (self.n_cat[0] + self.n_time[0], hi)

    @property
    def primary_mark(self) -> MarkShape:
        return self.mark[0]

    @property
    def primary_channel(self) -> Channel:
        return self.channel[0]


def _t(**kw) -> ChartType:
    return ChartType(**kw)


#: Tier 1: rectangles, points, sectors.
_TIER1 = [
    _t(name="bar", family="comparison", tier=1, shape="grouped_scalar", mark=("rect",),
       channel=("length",), value_keys=("value",),
       n_cat=(1, 1), n_measure=(0, 1), card=(3, 30),
       check_variation=True, check_distinct=True),
    _t(name="grouped_bar", family="comparison", tier=1, shape="grouped_scalar", mark=("rect",),
       channel=("length",), value_keys=("value",),
       n_cat=(2, 2), n_measure=(0, 1), card=(6, 24),
       min_rows_per_cell=5, check_distinct=True),
    _t(name="stacked_bar", family="composition", tier=1, shape="grouped_scalar", mark=("rect",),
       channel=("length",), value_keys=("value", "cum_start", "cum_end"),
       n_cat=(2, 2), n_measure=(0, 1), card=(6, 20),
       require_additive=True, min_rows_per_cell=5),
    _t(name="histogram", family="distribution", tier=1, shape="binned_count", mark=("rect",),
       channel=("length",), value_keys=("count", "bin_lo", "bin_hi"),
       n_measure=(1, 1), min_raw_rows=100, n_marks=(5, 30)),
    _t(name="waterfall", family="process", tier=1, shape="grouped_scalar", mark=("rect",),
       channel=("length",), value_keys=("value", "cum_start", "cum_end"),
       n_cat=(1, 1), n_measure=(0, 1), card=(5, 15),
       require_additive=True, require_stage=True, check_variation=True),
    _t(name="funnel", family="process", tier=1, shape="grouped_scalar", mark=("rect",),
       channel=("length",), value_keys=("value",),
       n_cat=(1, 1), n_measure=(0, 1), card=(3, 8),
       require_stage=True, monotone_decreasing=True),
    _t(name="line", family="trend", tier=1, shape="grouped_scalar", mark=("point",),
       channel=("position",), value_keys=("value",),
       n_cat=(0, 1), n_time=(1, 1), n_measure=(0, 1),
       points=(5, None), series=(1, 6), check_variation=True),
    _t(name="area", family="trend", tier=1, shape="grouped_scalar", mark=("point",),
       channel=("position",), value_keys=("value", "cum_start", "cum_end"),
       n_cat=(1, 1), n_time=(1, 1), n_measure=(0, 1),
       points=(5, None), series=(2, 5),
       require_additive=True, min_rows_per_cell=3),
    _t(name="scatter", family="relation", tier=1, shape="per_row", mark=("point",),
       channel=("position",), value_keys=("x", "y"),
       n_cat=(0, 1), n_measure=(2, 2), n_marks=(30, 500)),
    _t(name="pie", family="composition", tier=1, shape="grouped_scalar", mark=("sector",),
       channel=("angle",), value_keys=("value", "share"),
       n_cat=(1, 1), n_measure=(0, 1), card=(3, 8),
       require_additive=True, min_share=0.02),
    # A pair of rectangles that do not start at zero: one bar spanning the smallest
    # and largest value of its group. It reuses the five-number projection rather
    # than inventing a RANGE aggregate, and draws two of the five keys.
    _t(name="range_bar", family="distribution", tier=1, shape="grouped_fivenum", mark=("rect",),
       channel=("length",), value_keys=("min", "max"),
       n_cat=(1, 1), n_measure=(1, 1), card=(2, 12), min_rows_per_cell=10),
    # The same five numbers drawn as a point with whiskers. The grid below
    # predicted this cell before any benchmark asked for it.
    _t(name="error_bar", family="distribution", tier=1, shape="grouped_fivenum", mark=("point",),
       channel=("position",), value_keys=("min", "q1", "median", "q3", "max"),
       n_cat=(1, 1), n_measure=(1, 1), card=(2, 12), min_rows_per_cell=10),
    # Point marks over a category axis. It answers no view class -- a line drawn
    # over unordered categories is not how a trend is shown -- but it is what a
    # second series overlaid on a bar chart is drawn as, and reports are full of it.
    _t(name="category_line", family=None, tier=1, shape="grouped_scalar", mark=("point",),
       channel=("position",), value_keys=("value",),
       n_cat=(1, 1), n_measure=(0, 1), card=(3, 30), check_variation=True),
    # A chart that prints its numbers instead of drawing them. It answers no view
    # class, so it is reachable only through the type weights, never through a family.
    _t(name="table_chart", family=None, tier=1, shape="grouped_scalar", mark=("cell",),
       channel=("printed",), value_keys=("value",),
       n_cat=(1, 2), n_measure=(0, 1), card=(3, 40), min_rows_per_cell=1),
]

#: Tier 2: cells, boxes, bands.
_TIER2 = [
    _t(name="heatmap", family="relation", tier=2, shape="grouped_scalar", mark=("cell",),
       channel=("color",), value_keys=("value",),
       n_cat=(2, 2), n_measure=(0, 1), card=(6, 100), min_rows_per_cell=3),
    # Two shapes: the box between the quartiles, and one point per row outside the
    # whiskers. That is what the tuple is for -- a row outside the whiskers is drawn
    # separately because that is what it is on the page.
    _t(name="box", family="distribution", tier=2, shape="grouped_fivenum",
       mark=("boxlike", "point"), channel=("position", "position"),
       value_keys=("min", "q1", "median", "q3", "max"),
       n_cat=(1, 1), n_measure=(1, 1), card=(2, 10), min_rows_per_cell=15,
       outliers=True),
    # A spread over time: a filled band between the low and high value of each
    # point. The band is its own mark shape, because a point's box is a marker and
    # would not contain the two edges the band is measured from.
    _t(name="windsock", family="trend", tier=2, shape="grouped_fivenum", mark=("band",),
       channel=("position",), value_keys=("min", "q1", "median", "q3", "max"),
       n_time=(1, 1), n_measure=(1, 1), points=(5, None), series=(1, 1),
       min_rows_per_cell=5),
]

#: Name to entry. Insertion order is the tie-break order within a family.
CHARTS: dict[str, ChartType] = {c.name: c for c in (*_TIER1, *_TIER2)}

FAMILIES: tuple[Family, ...] = (
    "comparison", "trend", "composition", "relation", "distribution", "process",
)

#: Aggregates each projection shape accepts. For grouped scalars the set is
#: narrowed further by whether the measure is additive.
SHAPE_AGGREGATES: dict[Shape, tuple[str, ...]] = {
    "grouped_scalar": ("SUM", "AVG", "MAX", "MIN", "MEDIAN", "COUNT"),
    "grouped_fivenum": ("FIVE_NUM",),
    "binned_count": ("BIN_COUNT",),
    "per_row": ("NONE",),
}

#: Mark shape to the value keys it may use. A self-check compares every row
#: against this, so a type cannot declare a shape whose values it does not fill.
SHAPE_VALUE_KEYS: dict[MarkShape, frozenset[str]] = {
    "rect": frozenset({"value", "cum_start", "cum_end", "count", "bin_lo", "bin_hi",
                       "min", "max"}),
    "point": frozenset({"value", "cum_start", "cum_end", "x", "y",
                        "min", "q1", "median", "q3", "max"}),
    "sector": frozenset({"value", "share"}),
    "cell": frozenset({"value"}),
    "boxlike": frozenset({"min", "q1", "median", "q3", "max"}),
    "band": frozenset({"value", "lo", "hi", "min", "q1", "median", "q3", "max"}),
}

#: The product the table is really made of. Every cell either names the types that
#: fill it or says why it is empty, so a missing kind of chart is found by reading
#: this grid rather than by noticing it somewhere else.
GRID: dict[tuple[Shape, MarkShape], tuple[str, ...] | str] = {
    ("grouped_scalar", "rect"): ("bar", "grouped_bar", "stacked_bar", "waterfall", "funnel"),
    ("grouped_scalar", "point"): ("line", "area", "category_line"),
    ("grouped_scalar", "sector"): ("pie",),
    ("grouped_scalar", "cell"): ("heatmap", "table_chart"),
    ("grouped_scalar", "boxlike"): "a box needs five numbers; one scalar cannot fill it",
    ("grouped_scalar", "band"): "a band needs a low and a high; one scalar cannot fill it",
    ("grouped_fivenum", "rect"): ("range_bar",),
    ("grouped_fivenum", "point"): ("error_bar",),
    ("grouped_fivenum", "sector"): "a sector encodes one share; five numbers do not fit",
    ("grouped_fivenum", "cell"): "a cell carries one colour; five numbers do not fit",
    ("grouped_fivenum", "boxlike"): ("box",),
    ("grouped_fivenum", "band"): ("windsock",),
    ("binned_count", "rect"): ("histogram",),
    ("binned_count", "point"): "a density curve; the value is a line, not a mark",
    ("binned_count", "sector"): "bins are ordered and adjacent; sectors are neither",
    ("binned_count", "cell"): "a two-dimensional histogram; not drawn yet",
    ("binned_count", "boxlike"): "a bin holds a count, not a five-number summary",
    ("binned_count", "band"): "a bin holds a count, not a range",
    ("per_row", "rect"): "a Gantt or timeline bar, one row per event; not drawn yet",
    ("per_row", "point"): ("scatter",),
    ("per_row", "sector"): "one row is one point, and a sector is a share of a whole",
    ("per_row", "cell"): "one row per cell puts the provenance layer at one everywhere",
    ("per_row", "boxlike"): "a box summarises many rows; one row has nothing to summarise",
    ("per_row", "band"): "one row has a single value, so there is no range to fill",
}


@dataclass(frozen=True)
class DensityBand:
    """How many marks a figure in this band draws, and what that costs upstream.

    The three cardinality bounds on a chart type were written for the sparsest
    band, which is why every generated figure used to hold a handful of marks. A
    band raises the ceiling; it never lowers a type's own floor.

    `min_rows` is what the fact table has to supply. Splitting a few hundred rows
    across four hundred cells leaves the long tail with one row each, and the
    structural check cannot see that -- so the band is lowered instead of the
    per-cell floor being relaxed.
    """

    name: str
    marks: Bound
    min_rows: int


#: Five bands, coarse on purpose: they are an ablation axis, not a tuning knob.
DENSITY_BANDS: tuple[DensityBand, ...] = (
    DensityBand("sparse", (1, 20), 200),
    DensityBand("normal", (21, 60), 400),
    DensityBand("dense", (61, 150), 900),
    DensityBand("very_dense", (151, 400), 2000),
    DensityBand("extreme", (401, None), 5000),
)

DEFAULT_BAND = DENSITY_BANDS[0]

BANDS_BY_NAME: dict[str, DensityBand] = {b.name: b for b in DENSITY_BANDS}


def band(name: str | None) -> DensityBand:
    return DEFAULT_BAND if name is None else BANDS_BY_NAME[name]


def band_for_rows(n_rows: int) -> DensityBand:
    """The densest band a table of this size supports."""
    ok = [b for b in DENSITY_BANDS if b.min_rows <= n_rows]
    return ok[-1] if ok else DENSITY_BANDS[0]


def bound_at(base: Bound | None, density: DensityBand) -> Bound | None:
    """Widen a declared bound to the band's ceiling, where that ceiling is about density.

    The floor never moves: three bars are the fewest worth comparing whatever the
    batch is meant to look like.

    The ceiling moves only for types that already accept more marks than the sparsest
    band draws. A ceiling below that is not a statement about density but about the
    encoding -- eight sectors is where a pie stops being readable, and a denser batch
    does not make a twenty-slice pie readable. A type that declares no ceiling at all
    is not given one here either: a band says how dense a figure may get, never how
    sparse it has to be.

    So the sparsest band reproduces every declared bound exactly, and no band turns a
    legible type into an illegible one.
    """
    if base is None:
        return None
    lo, hi = base
    if hi is None or hi < DEFAULT_BAND.marks[1]:
        return base
    top = density.marks[1]
    return (lo, None) if top is None else (lo, max(hi, top))


def in_family(family: Family) -> tuple[ChartType, ...]:
    """Types in one family, in tie-break order."""
    return tuple(c for c in CHARTS.values() if c.family == family)


def familyless() -> tuple[ChartType, ...]:
    """Types that answer no view class, so no family walk can reach them."""
    return tuple(c for c in CHARTS.values() if c.family is None)


def by_tier(max_tier: int) -> tuple[ChartType, ...]:
    return tuple(c for c in CHARTS.values() if c.tier <= max_tier)


def within(value: float, bound: Bound | None) -> bool:
    if bound is None:
        return True
    lo, hi = bound
    return value >= lo and (hi is None or value <= hi)
