"""01 → 02：事实表与表结构说明。

`TableSchema` 是 01 那一次 LLM 调用的全部产物：场景散文、列声明、依赖图、意图绑定。
它不含任何数据值——数值由 `FactTable` 承载。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import pandas as pd

ColumnKind = Literal["category", "time", "measure"]
Ordered = Literal["ordinal", "stage"]
Freq = Literal["daily", "weekly", "monthly"]

#: 六个视图类 / 图表族。与 chart_types.md 的族一一对应。
Family = Literal[
    "comparison",    # 比较
    "trend",         # 趋势
    "composition",   # 构成
    "relation",      # 关系
    "distribution",  # 分布
    "process",       # 流程
]

FAMILY_ZH: dict[str, str] = {
    "comparison": "比较",
    "trend": "趋势",
    "composition": "构成",
    "relation": "关系",
    "distribution": "分布",
    "process": "流程",
}
FAMILY_FROM_ZH: dict[str, str] = {v: k for k, v in FAMILY_ZH.items()}

#: 分组标量形态的聚合；后三个是别的形态的占位，不是 SUM/AVG/COUNT 一类。
Aggregate = Literal[
    "SUM", "AVG", "MAX", "MIN", "MEDIAN", "COUNT",
    "FIVE_NUM", "BIN_COUNT", "NONE",
]

#: 可加 / 不可加测度各自允许的聚合，见 chart_types.md §2。
AGG_ADDITIVE: tuple[str, ...] = ("SUM", "AVG", "MAX", "MIN")
AGG_NON_ADDITIVE: tuple[str, ...] = ("AVG", "MEDIAN", "MAX", "MIN")


@dataclass(frozen=True)
class Column:
    """一列的声明。基数与语义字段在声明期就定死，是可画性判定的全部输入。"""

    name: str
    kind: ColumnKind
    cardinality: int
    group: str | None = None          # 所属维度组
    parent: str | None = None         # 层级里的父列
    ordered: Ordered | None = None
    values: tuple[str, ...] = ()      # 类别列的取值列表
    unit: str | None = None           # 数值列
    additive: bool | None = None      # 数值列
    freq: Freq | None = None          # 时间列
    start: str | None = None
    end: str | None = None
    derived_from: str | None = None   # 日历派生列指向它的时间列


@dataclass(frozen=True)
class DimGroup:
    """一个维度组及其层级链，`columns` 按从根到叶排列。"""

    name: str
    columns: tuple[str, ...]


@dataclass(frozen=True)
class IntentBinding:
    """一条分析意图：一句话 + 目标列 + 聚合 + 族。02 拿它直接构造意图图。"""

    index: int
    sentence: str
    columns: tuple[str, ...]
    aggregate: Aggregate
    family: Family


@dataclass(frozen=True)
class TableSchema:
    """给 02 的数据接口。场景散文与意图绑定是它的字段，不占单独产物。"""

    scenario_id: str
    scenario_title: str
    data_context: str
    columns: tuple[Column, ...]
    groups: tuple[DimGroup, ...] = ()
    dependencies: tuple[tuple[str, str], ...] = ()   # 数值列之间的边 (src → dst)
    intents: tuple[IntentBinding, ...] = ()
    n_rows: int = 0

    def column(self, name: str) -> Column:
        for c in self.columns:
            if c.name == name:
                return c
        raise KeyError(f"未声明的列: {name}")

    def has(self, name: str) -> bool:
        return any(c.name == name for c in self.columns)

    def of_kind(self, kind: ColumnKind) -> tuple[Column, ...]:
        return tuple(c for c in self.columns if c.kind == kind)

    @property
    def categories(self) -> tuple[Column, ...]:
        return self.of_kind("category")

    @property
    def times(self) -> tuple[Column, ...]:
        return self.of_kind("time")

    @property
    def measures(self) -> tuple[Column, ...]:
        return self.of_kind("measure")

    def group_of(self, name: str) -> str | None:
        return self.column(name).group


@dataclass
class FactTable:
    """行级事件表。一行一件不可再分的事，聚合只发生在 02 的投影里。"""

    scenario_id: str
    df: pd.DataFrame = field(repr=False)

    @property
    def n_rows(self) -> int:
        return len(self.df)
