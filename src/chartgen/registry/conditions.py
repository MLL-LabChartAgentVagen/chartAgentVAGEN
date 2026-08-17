"""Deciding whether a binding can be drawn, from declarations alone.

This module takes a binding and a schema and never sees data, which is what lets
the same rules run at two very different moments: before generation, to ask
whether a chart family is empty for this schema, and after it, to check one
concrete candidate. Both read the same chart table, so the two answers cannot
drift apart.

Conditions that need projected values -- variation, distinctness, rows per cell,
mark counts -- are decided elsewhere, once the values exist.
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

#: Divisor applied to a time column's point count when it is resampled.
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


# ---------------------------------------------------------------- cardinality

def _points(col: Column, resample: str | None) -> int:
    """Points left on the time axis after resampling."""
    divisor = RESAMPLE_DIVISOR.get(resample or col.freq or "daily", 1)
    return max(1, col.cardinality // divisor)


def _product(schema: TableSchema, names: Sequence[str]) -> int:
    out = 1
    for n in names:
        out *= schema.column(n).cardinality
    return out


# ---------------------------------------------------------------- the check

def check(binding: Binding, schema: TableSchema) -> Check:
    """Can this binding be drawn: roles, cardinality, semantics, aggregate."""
    spec = CHARTS.get(binding.chart_type)
    if spec is None:
        return _no(f"no such chart type: {binding.chart_type}")

    named = (*binding.dims, *binding.measures, *((binding.time,) if binding.time else ()))
    if len(set(named)) != len(named):
        return _no(f"one column fills several roles: {named}")
    for name in named:
        if not schema.has(name):
            return _no(f"undeclared column: {name}")

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
            return _no(f"{name} is not a category column, so it cannot group")
    if binding.time and schema.column(binding.time).kind != "time":
        return _no(f"{binding.time} is not a time column")
    for name in binding.measures:
        if schema.column(name).kind != "measure":
            return _no(f"{name} is not a numeric column")

    if not within(len(binding.dims), spec.n_cat):
        return _no(f"{spec.name} takes {spec.n_cat} category columns, got {len(binding.dims)}")
    if not within(1 if binding.time else 0, spec.n_time):
        return _no(f"{spec.name} takes {spec.n_time} time columns")
    if not within(len(binding.measures), spec.n_measure) and binding.aggregate != "COUNT":
        return _no(f"{spec.name} takes {spec.n_measure} measures, got {len(binding.measures)}")
    if not within(binding.n_group, spec.group_bound):
        return _no(f"{spec.name} takes {spec.group_bound} grouping columns, got {binding.n_group}")
    if schema.n_rows < spec.min_raw_rows:
        return _no(f"{spec.name} needs at least {spec.min_raw_rows} source rows, got {schema.n_rows}")
    return _OK


def _cardinality(binding: Binding, spec: ChartType, schema: TableSchema) -> Check:
    """Cardinality after grouping. With a time column it splits into points and series."""
    if binding.time:
        pts = _points(schema.column(binding.time), binding.resample)
        if not within(pts, spec.points):
            return _no(f"{spec.name} needs time points within {spec.points}, got {pts}")
        series = _product(schema, binding.dims)
        if not within(series, spec.series):
            return _no(f"{spec.name} needs series within {spec.series}, got {series}")
        return _OK
    if binding.dims:
        card = _product(schema, binding.dims)
        if not within(card, spec.card):
            return _no(f"{spec.name} needs cardinality within {spec.card}, got {card}")
    return _OK


def _semantics(binding: Binding, spec: ChartType, schema: TableSchema) -> Check:
    if spec.require_additive:
        for name in binding.measures:
            if not schema.column(name).additive:
                return _no(f"{spec.name} needs an additive measure, and {name} is not additive")
    if spec.require_stage:
        if not any(schema.column(n).ordered == "stage" for n in binding.dims):
            return _no(f'{spec.name} needs a dimension declared ordered="stage"')
    if spec.require_same_unit:
        units = {schema.column(n).unit for n in binding.measures}
        if len(units) > 1:
            return _no(f"{spec.name} needs its measures to share a unit, got {units}")
    return _OK


def _aggregate(binding: Binding, spec: ChartType, schema: TableSchema) -> Check:
    allowed = SHAPE_AGGREGATES[spec.shape]
    if binding.aggregate not in allowed:
        return _no(f"{spec.name} projects as {spec.shape}, whose aggregates are {allowed}")
    if spec.shape != "grouped_scalar":
        return _OK

    if binding.aggregate == "COUNT":
        return _OK if not binding.measures else _no("counting rows takes no measure")
    if not binding.measures:
        return _no(f"{binding.aggregate} needs a measure")
    for name in binding.measures:
        col = schema.column(name)
        legal = AGG_ADDITIVE if col.additive else AGG_NON_ADDITIVE
        if binding.aggregate not in legal:
            kind = "additive" if col.additive else "non-additive"
            return _no(f"{name} is {kind}, so its aggregates are {legal}, got {binding.aggregate}")
    return _OK


# ---------------------------------------------------------------- per family

def iter_bindings(chart_type: str, schema: TableSchema, *,
                  columns: Sequence[str] | None = None,
                  aggregate: str | None = None) -> Iterator[Binding]:
    """Yield bindings that pass `check`, lazily and in a fixed order.

    Nothing is projected or evaluated and no candidate list is built: the caller
    stops as soon as it has enough. `columns` narrows the pool, which is how an
    intent restricts the search to the columns it named.
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
    """Walk a family type by type, in tie-break order."""
    for spec in in_family(family):
        if spec.tier > max_tier:
            continue
        yield from iter_bindings(spec.name, schema, columns=columns, aggregate=aggregate)


def family_nonempty(family: Family, schema: TableSchema, max_tier: int = 3) -> bool:
    """Whether this family holds any legal binding. Short-circuits."""
    return next(iter_bindings_for_family(family, schema, max_tier=max_tier), None) is not None


def coverage(schema: TableSchema, max_tier: int = 3) -> dict[str, bool]:
    """Which families are non-empty for this schema. Needs no data."""
    from .charts import FAMILIES
    return {f: family_nonempty(f, schema, max_tier) for f in FAMILIES}
