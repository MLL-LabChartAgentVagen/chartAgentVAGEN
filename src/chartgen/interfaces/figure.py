"""02 内部的 ViewSpec 与 02 → 03 的 FigureSpec。

`Binding` 与 `ViewSpec` 分开，是为了让条件判定拿不到数据：`registry.conditions`
只接受 `Binding`，结构与语义条件因此在编译期就碰不到求值结果。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .table import Aggregate, Family

Layout = Literal["single", "side_by_side", "grid", "dual_axis"]

#: 多面板的五种关系，见 02_figure.md §4.1。
Relation = Literal[
    "facet",       # 同指标不同切面
    "drilldown",   # 下钻
    "time_split",  # 时间对照
    "dual_metric", # 双指标
    "part_whole",  # 整体与部分
]

SourceKind = Literal["intent", "panel", "rotation"]


@dataclass(frozen=True)
class Binding:
    """一条候选视图的列绑定。只引用列名，不含任何求值结果。

    `group_columns` 是 GROUP BY 的键顺序，也是记录里 `key` 元组的顺序：
    时间列在前，类别列按 P、S 顺序在后。
    """

    chart_type: str
    dims: tuple[str, ...] = ()        # 类别列，按角色顺序 P, S
    time: str | None = None           # 时间列
    measures: tuple[str, ...] = ()
    aggregate: Aggregate = "NONE"
    resample: str | None = None       # 时间轴重采样：daily / weekly / monthly

    @property
    def group_columns(self) -> tuple[str, ...]:
        return ((self.time,) if self.time else ()) + self.dims

    @property
    def n_group(self) -> int:
        return len(self.group_columns)


@dataclass(frozen=True)
class TimeWindow:
    """行过滤。只服务「时间对照」一种关系，配对时从锚点现场切出来。"""

    column: str
    start: str
    end: str
    label: str


@dataclass(frozen=True)
class Datum:
    """投影出的一条结果：一个键、一个值字典、它背后的原始行数。

    值字典的键由图元形状决定，见 chart_types.md §3。`rows` 就是 04 的 L2 层。
    """

    key: tuple[str, ...]
    values: dict[str, float]
    rows: int


@dataclass(frozen=True)
class ViewSpec:
    """一个面板要画的东西：绑定 + 行过滤 + 求值结果。"""

    binding: Binding
    data: tuple[Datum, ...]
    row_filter: TimeWindow | None = None
    sample_index: tuple[int, ...] = ()   # 逐行形态的确定性抽样索引

    @property
    def keys(self) -> frozenset[tuple[str, ...]]:
        return frozenset(d.key for d in self.data)


@dataclass(frozen=True)
class PanelSpec:
    panel_id: str
    view: ViewSpec


@dataclass(frozen=True)
class Sharing:
    """共享关系。`series_column` 只有共享图例时非空——各面板系列列必须相同。"""

    share_x: bool = False
    share_y: bool = False
    share_legend: bool = False
    series_column: str | None = None


@dataclass(frozen=True)
class Source:
    """这张图是怎么来的：意图构造 / 从锚点推导 / 按族采样。"""

    kind: SourceKind
    intent_index: int | None = None
    anchor_figure_id: str | None = None


@dataclass(frozen=True)
class FigureSpec:
    """02 → 03。决定哪些视图进同一张图、彼此什么关系、共享什么。"""

    figure_id: str
    scenario_id: str
    panels: tuple[PanelSpec, ...]
    layout: Layout = "single"
    sharing: Sharing = Sharing()
    relation: Relation | None = None
    source: Source = Source(kind="rotation")
    #: 列 → 单位。03 画轴标签与定数字格式要用，02 从 TableSchema 抄过来，
    #: 这样 03 不必认识表结构说明。
    column_units: dict[str, str] = field(default_factory=dict)

    @property
    def families(self) -> tuple[Family, ...]:
        from ..registry.charts import CHARTS
        return tuple(CHARTS[p.view.binding.chart_type].family for p in self.panels)
