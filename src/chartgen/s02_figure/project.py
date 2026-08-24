"""Turning one binding into values: always a single SELECT, in four shapes.

    grouped scalar    one number per group, plus how many rows it came from
    grouped fivenum   five numbers per group, and the rows outside the whiskers
    binned count      bin edges first, then how many rows fall in each
    per row           no grouping at all; one mark per row

The four branch here rather than in the drawing code because they differ in four
ways at once: how many keys the value dictionary holds, which aggregates apply,
which admission checks mean anything, and whether the provenance layer says
anything (a scatter point covers one row, a histogram bin covers exactly its count).

Row order never depends on how pandas happens to group: category values come out
in the order they were declared, time in chronological order. That is what makes
`(input, seed) -> output` hold for the keys as well as the numbers.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, replace
from typing import Sequence

import numpy as np
import pandas as pd

from ..common.rng import derive
from ..interfaces.figure import Binding, Datum, TimeWindow, ViewSpec
from ..interfaces.table import TableSchema
from ..registry.charts import CHARTS, DEFAULT_BAND, DensityBand, bound_at

STAGE = "s02_project"

#: Frequency to the label one time point is written as. The label is the key, so
#: it has to be stable and sortable.
TIME_LABEL: dict[str, str] = {"daily": "%Y-%m-%d", "weekly": "%Y-%m-%d",
                              "monthly": "%Y-%m", "yearly": "%Y"}

#: Bins a histogram aims for before the type's own bound clamps it.
TARGET_BINS = 12

#: How far past the quartiles a value has to sit to be drawn as its own mark.
WHISKER = 1.5


class ProjectionError(ValueError):
    """A binding cannot be projected: a column is missing or the filter empties it."""


@dataclass(frozen=True)
class Projection:
    """What one projection produced, before it is admitted or rejected."""

    data: tuple[Datum, ...]
    sample_index: tuple[int, ...] = ()

    def view(self, binding: Binding, row_filter: TimeWindow | None = None) -> ViewSpec:
        return ViewSpec(binding, self.data, row_filter, self.sample_index)


# ---------------------------------------------------------------- row selection

def select(df: pd.DataFrame, row_filter: TimeWindow | None) -> pd.DataFrame:
    """Apply the one row filter the pipeline has. It exists to show a view over two
    time windows and is cut from an anchor when that pairing is built."""
    if row_filter is None:
        return df
    column = pd.to_datetime(df[row_filter.column])
    keep = (column >= pd.Timestamp(row_filter.start)) & (column <= pd.Timestamp(row_filter.end))
    return df.loc[keep]


# ---------------------------------------------------------------- grouping keys

def time_labels(values: pd.Series, freq: str) -> pd.Series:
    """A time column to one label per row, coarsened to the requested frequency.

    Resampling only coarsens: a monthly column asked for weekly points stays
    monthly, because the finer label would name a day the data never carried.
    """
    stamps = pd.to_datetime(values)
    if freq == "yearly":
        return stamps.dt.strftime(TIME_LABEL["yearly"])
    if freq == "quarterly":
        # There is no strftime code for a quarter, and the label a reader expects is
        # `2023Q1` rather than the month it starts in.
        return stamps.dt.to_period("Q").astype(str)
    if freq == "monthly":
        return stamps.dt.strftime(TIME_LABEL["monthly"])
    if freq == "weekly":
        return (stamps - pd.to_timedelta(stamps.dt.weekday, unit="D")).dt.strftime(
            TIME_LABEL["weekly"])
    return stamps.dt.strftime(TIME_LABEL["daily"])


def _key_frame(df: pd.DataFrame, binding: Binding, schema: TableSchema) -> pd.DataFrame:
    """The grouping columns as strings, in key order: time first, then categories,
    then the colour group if there is one."""
    out = pd.DataFrame(index=df.index)
    if binding.time:
        freq = binding.resample or schema.column(binding.time).freq or "daily"
        out[binding.time] = time_labels(df[binding.time], freq)
    for name in binding.dims:
        out[name] = df[name].astype(str)
    if colour_map(df, binding) is not None:
        out[binding.colour_group] = df[binding.colour_group].astype(str)
    return out


def colour_map(df: pd.DataFrame, binding: Binding) -> dict[str, str] | None:
    """The grouping column's values to the colour group's, when that is a function.

    A colour group names a second variable each bar also belongs to -- which tier a
    country sits in, which region a site reports to. It does not group anything: the
    mark it colours already determines it, so adding it to the key changes what a
    mark is called without changing which rows it covers. When one grouping value
    maps to several colour values it is not that kind of column, and nothing is added.
    """
    name = binding.colour_group
    if not name or name in binding.group_columns or name not in df.columns:
        return None
    over = binding.dims[-1] if binding.dims else binding.time
    if not over or over not in df.columns:
        return None
    pairs = df[[over, name]].astype(str).drop_duplicates()
    if pairs[over].duplicated().any():
        return None
    return dict(zip(pairs[over], pairs[name]))


def _order_of(name: str, seen: Sequence[str], schema: TableSchema) -> list[str]:
    """Declared value order for a category column, sorted order for anything else."""
    declared = schema.column(name).values if schema.has(name) else ()
    if declared:
        rest = [v for v in seen if v not in declared]
        return [v for v in declared if v in seen] + sorted(rest)
    return sorted(seen)


def _key_order(keys: Sequence[tuple[str, ...]], binding: Binding,
               schema: TableSchema) -> list[tuple[str, ...]]:
    """Sort keys column by column, each in that column's own order."""
    columns = binding.group_columns
    ranks = [{v: i for i, v in enumerate(_order_of(c, {k[j] for k in keys}, schema))}
             for j, c in enumerate(columns)]
    return sorted(keys, key=lambda k: tuple(ranks[j].get(k[j], 0) for j in range(len(columns))))


def _grouping_width(df: pd.DataFrame, binding: Binding) -> int:
    """Key segments a grouped projection produces."""
    return binding.n_group + (1 if colour_map(df, binding) is not None else 0)


# ---------------------------------------------------------------- the aggregates

def _aggregate(series: pd.Series, how: str) -> float:
    return float({
        "SUM": series.sum, "AVG": series.mean, "MAX": series.max,
        "MIN": series.min, "MEDIAN": series.median, "COUNT": series.count,
    }[how]())


def _measure(df: pd.DataFrame, binding: Binding) -> pd.Series:
    if binding.aggregate == "COUNT" or not binding.measures:
        return pd.Series(np.ones(len(df)), index=df.index)
    return df[binding.measures[0]].astype(float)


# ---------------------------------------------------------------- grouped scalar

def grouped_scalar(df: pd.DataFrame, binding: Binding, schema: TableSchema) -> Projection:
    """One number per group, and how many rows went into it."""
    keys = _key_frame(df, binding, schema)
    values = _measure(df, binding)
    spec = CHARTS[binding.chart_type]

    groups: dict[tuple[str, ...], list[int]] = {}
    for pos, key in enumerate(map(tuple, keys.to_numpy())):
        groups.setdefault(key, []).append(pos)

    ordered = _key_order(list(groups), binding, schema)
    scalars = {}
    for key in ordered:
        rows = groups[key]
        chunk = values.iloc[rows]
        scalars[key] = (_aggregate(chunk, binding.aggregate)
                        if binding.aggregate != "COUNT" else float(len(rows)),
                        len(rows))

    data = [Datum(key, {"value": v}, rows) for key, (v, rows) in scalars.items()]
    if "share" in spec.value_keys:
        data = _with_shares(data)
    if "cum_start" in spec.value_keys:
        data = _with_cumulative(data, binding, schema)
    return Projection(tuple(data))


def _with_shares(data: Sequence[Datum]) -> list[Datum]:
    total = sum(d.values["value"] for d in data)
    return [Datum(d.key, {**d.values, "share": (d.values["value"] / total if total else 0.0)},
                  d.rows) for d in data]


def _with_cumulative(data: Sequence[Datum], binding: Binding,
                     schema: TableSchema) -> list[Datum]:
    """Where each mark's rectangle starts and ends.

    With two grouping columns the second one stacks inside the first, which is what
    a stacked bar and a stacked area draw. With one it accumulates along the
    sequence, which is what a waterfall draws. Both are decided by how many columns
    group the view, not by naming the chart type.
    """
    running: dict[tuple[str, ...], float] = {}
    out: list[Datum] = []
    # Stacked within the outer grouping columns, and only those. Taken as "all but
    # the last segment", a colour group -- which adds a segment without grouping
    # anything -- would make every anchor unique and every segment start at zero.
    outer = binding.n_group - 1 if binding.n_group >= 2 else 0
    for d in data:
        anchor = d.key[:outer]
        start = running.get(anchor, 0.0)
        end = start + d.values["value"]
        running[anchor] = end
        out.append(Datum(d.key, {**d.values, "cum_start": start, "cum_end": end}, d.rows))
    return out


# ---------------------------------------------------------------- grouped fivenum

def grouped_fivenum(df: pd.DataFrame, binding: Binding, schema: TableSchema) -> Projection:
    """Five numbers per group, and optionally the rows outside the whiskers.

    An outlier is its own mark, so it carries a key one segment longer than the
    group it belongs to. Everything that reasons about which entities a figure
    shows looks at the group keys, which is why the extra segment is what tells
    them apart.
    """
    keys = _key_frame(df, binding, schema)
    values = _measure(df, binding)
    spec = CHARTS[binding.chart_type]

    groups: dict[tuple[str, ...], list[int]] = {}
    for pos, key in enumerate(map(tuple, keys.to_numpy())):
        groups.setdefault(key, []).append(pos)

    out: list[Datum] = []
    for key in _key_order(list(groups), binding, schema):
        chunk = values.iloc[groups[key]].to_numpy(dtype=float)
        q1, median, q3 = (float(np.percentile(chunk, p)) for p in (25, 50, 75))
        lo_fence, hi_fence = q1 - WHISKER * (q3 - q1), q3 + WHISKER * (q3 - q1)
        inside = chunk[(chunk >= lo_fence) & (chunk <= hi_fence)]
        whisker_lo = float(inside.min()) if inside.size else float(chunk.min())
        whisker_hi = float(inside.max()) if inside.size else float(chunk.max())
        out.append(Datum(key, {"min": whisker_lo, "q1": q1, "median": median,
                               "q3": q3, "max": whisker_hi}, len(chunk)))
        if spec.outliers:
            # One mark per distinct value, not per row. Rows that share a value are
            # drawn on top of each other, so recording them separately would give
            # several keys the same box and no way to tell which of them a question
            # about that box is asking for. How many rows are behind the point is
            # what the row count is for.
            outside = Counter(sorted(float(v) for v in chunk
                                     if v < lo_fence or v > hi_fence))
            for i, (value, rows) in enumerate(outside.items()):
                out.append(Datum((*key, f"outlier{i}"), {"value": value}, rows))
    return Projection(tuple(out))


# ---------------------------------------------------------------- binned count

def binned_count(df: pd.DataFrame, binding: Binding, schema: TableSchema,
                 density: DensityBand = DEFAULT_BAND) -> Projection:
    """Bin edges first, then how many rows fall in each. `rows` equals the count."""
    spec = CHARTS[binding.chart_type]
    values = df[binding.measures[0]].astype(float).to_numpy()
    if values.size == 0:
        raise ProjectionError(f"{binding.measures[0]} has no rows to bin")
    lo, hi = float(values.min()), float(values.max())
    if not math.isfinite(lo) or not math.isfinite(hi) or hi <= lo:
        raise ProjectionError(f"{binding.measures[0]} does not vary, so it has no bins")

    least, most = bound_at(spec.n_marks, density) or (5, TARGET_BINS)
    n_bins = max(least, TARGET_BINS if most is None else min(most, TARGET_BINS))
    counts, edges = np.histogram(values, bins=n_bins, range=(lo, hi))
    return Projection(tuple(
        Datum((f"{edges[i]:.4g}-{edges[i + 1]:.4g}",),
              {"count": float(counts[i]), "bin_lo": float(edges[i]),
               "bin_hi": float(edges[i + 1])}, int(counts[i]))
        for i in range(n_bins)
    ))


# ---------------------------------------------------------------- per row

def per_row(df: pd.DataFrame, binding: Binding, schema: TableSchema, *, seed: int,
            density: DensityBand = DEFAULT_BAND) -> Projection:
    """One mark per row, no grouping. Above the type's point cap the rows are
    thinned by seed, and which rows survived is stored with the view so the same
    figure comes back with the same points."""
    spec = CHARTS[binding.chart_type]
    cap = (bound_at(spec.n_marks, density) or (0, None))[1]
    positions = np.arange(len(df))
    if cap is not None and len(df) > cap:
        rng = derive(seed, STAGE, binding.chart_type, *binding.measures)
        positions = np.sort(rng.choice(len(df), size=cap, replace=False))

    x_col, y_col = binding.measures[0], binding.measures[1]
    xs = df[x_col].astype(float).to_numpy()
    ys = df[y_col].astype(float).to_numpy()
    series = df[binding.dims[0]].astype(str).to_numpy() if binding.dims else None

    data = tuple(
        Datum(((series[p],) if series is not None else ()) + (f"row_{int(p):05d}",),
              {"x": float(xs[p]), "y": float(ys[p])}, 1)
        for p in positions
    )
    return Projection(data, tuple(int(p) for p in positions))


# ---------------------------------------------------------------- the one entry point

def project(df: pd.DataFrame, binding: Binding, schema: TableSchema, *,
            row_filter: TimeWindow | None = None, seed: int = 0,
            density: DensityBand = DEFAULT_BAND) -> ViewSpec:
    """One binding to one view. The shape decides which of the four paths runs.

    What comes out carries the value keys the type declares and no others. The
    five-number path returns all five whoever asked for it, but a range bar draws two
    of them, and a number that is not drawn cannot be read off the mark -- keeping it
    would put a value in the record that no question about the image can reach.
    """
    spec = CHARTS.get(binding.chart_type)
    if spec is None:
        raise ProjectionError(f"no such chart type: {binding.chart_type}")
    rows = select(df, row_filter)
    if rows.empty:
        raise ProjectionError(f"{binding.chart_type}: the row filter left no rows")

    if spec.shape == "grouped_scalar":
        out = grouped_scalar(rows, binding, schema)
    elif spec.shape == "grouped_fivenum":
        out = grouped_fivenum(rows, binding, schema)
    elif spec.shape == "binned_count":
        out = binned_count(rows, binding, schema, density)
    else:
        out = per_row(rows, binding, schema, seed=seed, density=density)
    return _declared(out, spec, binding).view(binding, row_filter)


def _declared(out: Projection, spec, binding: Binding) -> Projection:
    """Keep the value keys the type says it draws.

    A mark hung off a group -- a row outside the whiskers -- is its own shape carrying
    the one number it is, so it keeps what it has.
    """
    keys = set(spec.value_keys)
    width = binding.n_key
    return Projection(tuple(
        d if len(d.key) != width else replace(d, values={k: v for k, v in d.values.items()
                                                         if k in keys})
        for d in out.data), out.sample_index)


def group_keys(view: ViewSpec) -> frozenset[tuple[str, ...]]:
    """The keys of the groups a view shows, without the extra marks hung off them.

    An outlier is drawn separately but belongs to its group, so it carries one more
    segment than the grouping columns. Which entities a figure puts on the page is
    a question about the groups.
    """
    n = view.binding.n_key
    return frozenset(view.full_key(d) for d in view.data if len(d.key) == n) or view.keys
