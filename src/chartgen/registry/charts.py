"""The one place chart types are defined: six families, thirteen types.

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

The insertion order of `CHARTS` is the tie-break order within a family: when
several types fit an intent, the first one listed wins.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..interfaces.record import Channel
from ..interfaces.table import Family

#: How a view is projected out of the fact table. It decides how many keys the
#: value dictionary holds, which aggregates apply, which data conditions are
#: checked, and whether the provenance layer carries information.
Shape = Literal["grouped_scalar", "grouped_fivenum", "binned_count", "per_row"]

#: The shape of one mark. Drawing code is split by shape, not by chart type:
#: thirteen types share five shapes.
MarkShape = Literal["rect", "point", "sector", "cell", "boxlike"]

Bound = tuple[int, int | None]   # (lower, upper); None as the upper means unbounded

UNBOUNDED: Bound = (0, None)


@dataclass(frozen=True)
class ChartType:
    name: str
    family: Family | None          # a compound chart belongs to no family; it only
                                   # arises from pairing one grouping with two measures
    tier: int
    shape: Shape
    mark: MarkShape
    channel: Channel
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

    @property
    def group_bound(self) -> Bound:
        if self.n_group is not None:
            return self.n_group
        hi = None if self.n_cat[1] is None or self.n_time[1] is None else self.n_cat[1] + self.n_time[1]
        return (self.n_cat[0] + self.n_time[0], hi)


def _t(**kw) -> ChartType:
    return ChartType(**kw)


#: Tier 1: rectangles, points, sectors.
_TIER1 = [
    _t(name="bar", family="comparison", tier=1, shape="grouped_scalar", mark="rect",
       channel="length", value_keys=("value",),
       n_cat=(1, 1), n_measure=(0, 1), card=(3, 30),
       check_variation=True, check_distinct=True),
    _t(name="grouped_bar", family="comparison", tier=1, shape="grouped_scalar", mark="rect",
       channel="length", value_keys=("value",),
       n_cat=(2, 2), n_measure=(0, 1), card=(6, 24),
       min_rows_per_cell=5, check_distinct=True),
    _t(name="stacked_bar", family="composition", tier=1, shape="grouped_scalar", mark="rect",
       channel="length", value_keys=("value", "cum_start", "cum_end"),
       n_cat=(2, 2), n_measure=(0, 1), card=(6, 20),
       require_additive=True, min_rows_per_cell=5),
    _t(name="histogram", family="distribution", tier=1, shape="binned_count", mark="rect",
       channel="length", value_keys=("count", "bin_lo", "bin_hi"),
       n_measure=(1, 1), min_raw_rows=100, n_marks=(5, 30)),
    _t(name="waterfall", family="process", tier=1, shape="grouped_scalar", mark="rect",
       channel="length", value_keys=("value", "cum_start", "cum_end"),
       n_cat=(1, 1), n_measure=(0, 1), card=(5, 15),
       require_additive=True, require_stage=True, check_variation=True),
    _t(name="funnel", family="process", tier=1, shape="grouped_scalar", mark="rect",
       channel="length", value_keys=("value",),
       n_cat=(1, 1), n_measure=(0, 1), card=(3, 8),
       require_stage=True, monotone_decreasing=True),
    _t(name="line", family="trend", tier=1, shape="grouped_scalar", mark="point",
       channel="position", value_keys=("value",),
       n_cat=(0, 1), n_time=(1, 1), n_measure=(0, 1),
       points=(5, None), series=(1, 6), check_variation=True),
    _t(name="area", family="trend", tier=1, shape="grouped_scalar", mark="point",
       channel="position", value_keys=("value", "cum_start", "cum_end"),
       n_cat=(1, 1), n_time=(1, 1), n_measure=(0, 1),
       points=(5, None), series=(2, 5),
       require_additive=True, min_rows_per_cell=3),
    _t(name="scatter", family="relation", tier=1, shape="per_row", mark="point",
       channel="position", value_keys=("x", "y"),
       n_cat=(0, 1), n_measure=(2, 2), n_marks=(30, 500)),
    _t(name="pie", family="composition", tier=1, shape="grouped_scalar", mark="sector",
       channel="angle", value_keys=("value", "share"),
       n_cat=(1, 1), n_measure=(0, 1), card=(3, 8),
       require_additive=True, min_share=0.02),
    _t(name="compound", family=None, tier=1, shape="grouped_scalar", mark="rect",
       channel="length", value_keys=("value",),
       n_cat=(0, 1), n_time=(0, 1), n_measure=(2, 2), n_group=(1, 1),
       card=(3, 30), points=(3, None), series=(1, 1), check_distinct=True),
]

#: Tier 2: cells, boxes.
_TIER2 = [
    _t(name="heatmap", family="relation", tier=2, shape="grouped_scalar", mark="cell",
       channel="color", value_keys=("value",),
       n_cat=(2, 2), n_measure=(0, 1), card=(6, 100), min_rows_per_cell=3),
    _t(name="box", family="distribution", tier=2, shape="grouped_fivenum", mark="boxlike",
       channel="position", value_keys=("min", "q1", "median", "q3", "max"),
       n_cat=(1, 1), n_measure=(1, 1), card=(2, 10), min_rows_per_cell=15),
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
    "rect": frozenset({"value", "cum_start", "cum_end", "count", "bin_lo", "bin_hi"}),
    "point": frozenset({"value", "cum_start", "cum_end", "x", "y"}),
    "sector": frozenset({"value", "share"}),
    "cell": frozenset({"value"}),
    "boxlike": frozenset({"min", "q1", "median", "q3", "max"}),
}


def in_family(family: Family) -> tuple[ChartType, ...]:
    """Types in one family, in tie-break order."""
    return tuple(c for c in CHARTS.values() if c.family == family)


def by_tier(max_tier: int) -> tuple[ChartType, ...]:
    return tuple(c for c in CHARTS.values() if c.tier <= max_tier)


def within(value: float, bound: Bound | None) -> bool:
    if bound is None:
        return True
    lo, hi = bound
    return value >= lo and (hi is None or value <= hi)
