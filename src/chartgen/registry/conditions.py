"""结构条件与语义条件的判定。**只读列声明，碰不到任何数据。**

01 用 `coverage` / `family_nonempty` 逐族判非空；02 用 `check` 逐条判候选，
用 `iter_bindings_for_family` 为意图图按确定顺序取第一条。两处读同一份 `charts.py`。

数据条件（变异、区分度、每格行数、图元数）要求值之后才知道，在 `s02_figure/admit.py`。
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Iterator, Sequence

from ..interfaces.figure import Binding
from ..interfaces.table import (
    AGG_ADDITIVE, AGG_NON_ADDITIVE, Column, Family, TableSchema,
)
from .charts import CHARTS, SHAPE_AGGREGATES, ChartType, in_family, within

#: 时间列重采样后的点数按这个比例折算。daily → weekly 是除以 7。
RESAMPLE_DIVISOR: dict[str, int] = {"daily": 1, "weekly": 7, "monthly": 30}


@dataclass(frozen=True)
class Check:
    ok: bool
    reason: str = ""

    def __bool__(self) -> bool:
        return self.ok


_OK = Check(True)


def _no(reason: str) -> Check:
    return Check(False, reason)


# ---------------------------------------------------------------- 基数

def _points(col: Column, resample: str | None) -> int:
    """时间列重采样后的点数。"""
    divisor = RESAMPLE_DIVISOR.get(resample or col.freq or "daily", 1)
    return max(1, col.cardinality // divisor)


def _product(schema: TableSchema, names: Sequence[str]) -> int:
    out = 1
    for n in names:
        out *= schema.column(n).cardinality
    return out


# ---------------------------------------------------------------- 主判定

def check(binding: Binding, schema: TableSchema) -> Check:
    """一条列绑定能不能画。结构条件 + 语义条件 + 聚合合法性。"""
    spec = CHARTS.get(binding.chart_type)
    if spec is None:
        return _no(f"没有这个图表类型: {binding.chart_type}")

    named = (*binding.dims, *binding.measures, *((binding.time,) if binding.time else ()))
    if len(set(named)) != len(named):
        return _no(f"同一列重复出现在多个角色上: {named}")
    for name in named:
        if not schema.has(name):
            return _no(f"声明里没有这一列: {name}")

    if (r := _roles(binding, spec, schema)) is not _OK:
        return r
    if (r := _cardinality(binding, spec, schema)) is not _OK:
        return r
    if (r := _semantics(binding, spec, schema)) is not _OK:
        return r
    return _aggregate(binding, spec, schema)


def _roles(binding: Binding, spec: ChartType, schema: TableSchema) -> Check:
    for name in binding.dims:
        if schema.column(name).kind != "category":
            return _no(f"{name} 不是类别列，填不了 P/S 角色")
    if binding.time and schema.column(binding.time).kind != "time":
        return _no(f"{binding.time} 不是时间列")
    for name in binding.measures:
        if schema.column(name).kind != "measure":
            return _no(f"{name} 不是数值列")

    if not within(len(binding.dims), spec.n_cat):
        return _no(f"{spec.name} 要 {spec.n_cat} 个类别列，给了 {len(binding.dims)} 个")
    if not within(1 if binding.time else 0, spec.n_time):
        return _no(f"{spec.name} 要 {spec.n_time} 个时间列")
    if not within(len(binding.measures), spec.n_measure) and binding.aggregate != "COUNT":
        return _no(f"{spec.name} 要 {spec.n_measure} 个测度，给了 {len(binding.measures)} 个")
    if not within(binding.n_group, spec.group_bound):
        return _no(f"{spec.name} 要 {spec.group_bound} 个分组列，给了 {binding.n_group} 个")
    if schema.n_rows < spec.min_raw_rows:
        return _no(f"{spec.name} 要原始行数 ≥ {spec.min_raw_rows}，只有 {schema.n_rows}")
    return _OK


def _cardinality(binding: Binding, spec: ChartType, schema: TableSchema) -> Check:
    """聚合后的基数。有时间列时分成「点数」与「系列数」两项。"""
    if binding.time:
        pts = _points(schema.column(binding.time), binding.resample)
        if not within(pts, spec.points):
            return _no(f"{spec.name} 要时间点数落在 {spec.points}，实际 {pts}")
        series = _product(schema, binding.dims)
        if not within(series, spec.series):
            return _no(f"{spec.name} 要系列数落在 {spec.series}，实际 {series}")
        return _OK
    if binding.dims:
        card = _product(schema, binding.dims)
        if not within(card, spec.card):
            return _no(f"{spec.name} 要基数落在 {spec.card}，实际 {card}")
    return _OK


def _semantics(binding: Binding, spec: ChartType, schema: TableSchema) -> Check:
    if spec.require_additive:
        for name in binding.measures:
            if not schema.column(name).additive:
                return _no(f"{spec.name} 要可加测度，{name} 不可加")
    if spec.require_stage:
        if not any(schema.column(n).ordered == "stage" for n in binding.dims):
            return _no(f'{spec.name} 要一个 ordered="stage" 的维度')
    if spec.require_same_unit:
        units = {schema.column(n).unit for n in binding.measures}
        if len(units) > 1:
            return _no(f"{spec.name} 要多测度同量纲，给了 {units}")
    return _OK


def _aggregate(binding: Binding, spec: ChartType, schema: TableSchema) -> Check:
    allowed = SHAPE_AGGREGATES[spec.shape]
    if binding.aggregate not in allowed:
        return _no(f"{spec.name} 是 {spec.shape} 形态，聚合只能取 {allowed}")
    if spec.shape != "grouped_scalar":
        return _OK

    if binding.aggregate == "COUNT":
        return _OK if not binding.measures else _no("COUNT(*) 不带测度")
    if not binding.measures:
        return _no(f"聚合 {binding.aggregate} 需要一个测度")
    for name in binding.measures:
        col = schema.column(name)
        legal = AGG_ADDITIVE if col.additive else AGG_NON_ADDITIVE
        if binding.aggregate not in legal:
            kind = "可加" if col.additive else "不可加"
            return _no(f"{name} {kind}，聚合只能取 {legal}，给了 {binding.aggregate}")
    return _OK


# ---------------------------------------------------------------- 逐族判非空

def iter_bindings(chart_type: str, schema: TableSchema, *,
                  columns: Sequence[str] | None = None,
                  aggregate: str | None = None) -> Iterator[Binding]:
    """按确定顺序惰性产出通过 `check` 的列绑定。

    只走列声明，不投影、不求值，也不materialize候选清单——调用方取够就停。
    `columns` 把可用列限制在意图绑定给的那几列上。
    """
    spec = CHARTS[chart_type]
    pool = schema.columns if columns is None else tuple(
        schema.column(n) for n in columns if schema.has(n))
    cats = tuple(c.name for c in pool if c.kind == "category")
    times = tuple(c.name for c in pool if c.kind == "time")
    measures = tuple(c.name for c in pool if c.kind == "measure")
    aggs = (aggregate,) if aggregate else SHAPE_AGGREGATES[spec.shape]

    for n_cat in _counts(spec.n_cat, len(cats)):
        for dims in permutations(cats, n_cat):
            for time in ((None,) if spec.n_time[0] == 0 else ()) + times:
                if time is not None and not within(1, spec.n_time):
                    continue
                for n_m in _counts(spec.n_measure, len(measures)):
                    for ms in permutations(measures, n_m):
                        for agg in aggs:
                            b = Binding(chart_type, dims=dims, time=time,
                                        measures=ms, aggregate=agg)
                            if check(b, schema).ok:
                                yield b


def _counts(bound, available: int) -> range:
    lo, hi = bound
    hi = available if hi is None else min(hi, available)
    return range(lo, hi + 1)


def iter_bindings_for_family(family: Family, schema: TableSchema, *,
                             columns: Sequence[str] | None = None,
                             aggregate: str | None = None,
                             max_tier: int = 3) -> Iterator[Binding]:
    """族内按 `charts.py` 的行顺序逐型产出。意图图取它的第一条。"""
    for spec in in_family(family):
        if spec.tier > max_tier:
            continue
        yield from iter_bindings(spec.name, schema, columns=columns, aggregate=aggregate)


def family_nonempty(family: Family, schema: TableSchema, max_tier: int = 3) -> bool:
    """这个族里有没有任何一条合法绑定。短路，不展开组合。"""
    return next(iter_bindings_for_family(family, schema, max_tier=max_tier), None) is not None


def coverage(schema: TableSchema, max_tier: int = 3) -> dict[str, bool]:
    """逐族判非空。01 §5 的覆盖度检查，不需要数据。"""
    from .charts import FAMILIES
    return {f: family_nonempty(f, schema, max_tier) for f in FAMILIES}
