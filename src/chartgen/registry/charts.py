"""图表类型的唯一定义处：6 族 13 型。

四类条件按 [chart_types.md §2](../../../storyline/parsebench_chart/chart_types.md) 逐格抄下来，
分成三段字段：

    结构条件  只看列声明（角色个数、基数区间、原始行数）
    语义条件  只看列声明（可加、流程阶段、同量纲）
    数据条件  要求值之后才知道（变异、区分度、每格行数、图元数、单调、最小占比）

新增一个图表类型只在这里加一行，再加一个绘制分支；01、02、04、05 一行都不用改。
四类条件、图元形状、值字典逐项相同的视觉变体（实心饼与中空饼）不占一行——
它是 StyleVector 的一个字段。

`CHARTS` 的行顺序就是族内的确定性顺序：意图图「通过的按确定顺序取第一条」取的是它。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..interfaces.record import Channel
from ..interfaces.table import Family

#: 投影形态。决定值字典有几个键、聚合集是什么、准入检查查哪几项、L2 有没有信息量。
Shape = Literal["grouped_scalar", "grouped_fivenum", "binned_count", "per_row"]

#: 图元形状。绘制与记录的代码按形状分文件，不按图表类型分文件。
MarkShape = Literal["rect", "point", "sector", "cell", "boxlike"]

Bound = tuple[int, int | None]   # (下限, 上限)，上限 None 表示不设

UNBOUNDED: Bound = (0, None)


@dataclass(frozen=True)
class ChartType:
    name: str
    family: Family | None          # compound 不属于任何族，只由「双指标」关系推出
    tier: int
    shape: Shape
    mark: MarkShape
    channel: Channel
    value_keys: tuple[str, ...]

    # ---- 结构条件（声明期）
    n_cat: Bound = (0, 0)          # 类别列个数
    n_time: Bound = (0, 0)         # 时间列个数
    n_measure: Bound = (0, 0)      # 测度个数
    n_group: Bound | None = None   # 分组列总数；None 表示由 n_cat + n_time 隐含
    card: Bound | None = None      # 类别叉积的基数（无时间列时）
    points: Bound | None = None    # 时间点数（有时间列时）
    series: Bound | None = None    # 系列数 = 类别叉积（有时间列时）
    min_raw_rows: int = 0          # 事实表原始行数下限

    # ---- 语义条件（声明期）
    require_additive: bool = False
    require_stage: bool = False
    require_same_unit: bool = False

    # ---- 数据条件（求值后）
    check_variation: bool = False
    check_distinct: bool = False
    min_rows_per_cell: int = 0
    n_marks: Bound | None = None       # 图元数：散点点数、直方图箱数
    monotone_decreasing: bool = False
    min_share: float = 0.0             # 最小扇区占比

    @property
    def group_bound(self) -> Bound:
        if self.n_group is not None:
            return self.n_group
        hi = None if self.n_cat[1] is None or self.n_time[1] is None else self.n_cat[1] + self.n_time[1]
        return (self.n_cat[0] + self.n_time[0], hi)


def _t(**kw) -> ChartType:
    return ChartType(**kw)


#: Tier 1 · 矩形、点、扇形
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

#: Tier 2 · 格子、箱体
_TIER2 = [
    _t(name="heatmap", family="relation", tier=2, shape="grouped_scalar", mark="cell",
       channel="color", value_keys=("value",),
       n_cat=(2, 2), n_measure=(0, 1), card=(6, 100), min_rows_per_cell=3),
    _t(name="box", family="distribution", tier=2, shape="grouped_fivenum", mark="boxlike",
       channel="position", value_keys=("min", "q1", "median", "q3", "max"),
       n_cat=(1, 1), n_measure=(1, 1), card=(2, 10), min_rows_per_cell=15),
]

#: 名称 → 条目。插入顺序即族内确定性顺序。
CHARTS: dict[str, ChartType] = {c.name: c for c in (*_TIER1, *_TIER2)}

FAMILIES: tuple[Family, ...] = (
    "comparison", "trend", "composition", "relation", "distribution", "process",
)

#: 各形态接受的聚合集。分组标量的聚合集另由测度的可加性收窄，见 conditions.py。
SHAPE_AGGREGATES: dict[Shape, tuple[str, ...]] = {
    "grouped_scalar": ("SUM", "AVG", "MAX", "MIN", "MEDIAN", "COUNT"),
    "grouped_fivenum": ("FIVE_NUM",),
    "binned_count": ("BIN_COUNT",),
    "per_row": ("NONE",),
}

#: 图元形状 → 值字典必须有的键。A3.5 的自检拿它比对每一行。
SHAPE_VALUE_KEYS: dict[MarkShape, frozenset[str]] = {
    "rect": frozenset({"value", "cum_start", "cum_end", "count", "bin_lo", "bin_hi"}),
    "point": frozenset({"value", "cum_start", "cum_end", "x", "y"}),
    "sector": frozenset({"value", "share"}),
    "cell": frozenset({"value"}),
    "boxlike": frozenset({"min", "q1", "median", "q3", "max"}),
}


def in_family(family: Family) -> tuple[ChartType, ...]:
    """族内类型，按 `CHARTS` 的行顺序。"""
    return tuple(c for c in CHARTS.values() if c.family == family)


def by_tier(max_tier: int) -> tuple[ChartType, ...]:
    return tuple(c for c in CHARTS.values() if c.tier <= max_tier)


def within(value: float, bound: Bound | None) -> bool:
    if bound is None:
        return True
    lo, hi = bound
    return value >= lo and (hi is None or value <= hi)
