"""Executing a declaration script: dependency graph, topological order, three passes.

    non-numeric columns  root dimensions are allocated across the n rows by their
                         weights; a child dimension is allocated inside each parent
                         value's rows; the time column is allocated across its
                         points, and the calendar fields are derived from it
    numeric columns      evaluated in topological order, one whole column per
                         vector operation, never row by row
    post-processing      decimal places fixed by unit

Allocation and shuffle, not per-row sampling. Sampling row by row gives a
low-weight value some chance of never appearing, and the resulting column would
have fewer distinct values than its declaration promised -- but the feasibility
check decides which chart families are drawable from those declared counts.
Allocation guarantees every declared value gets rows and keeps the marginal
proportions; the randomness lives in which row gets which value.

Every column draws from its own random stream, derived from the root seed and the
column name. Adding a column therefore leaves the values of existing columns
untouched.
"""

from __future__ import annotations

from datetime import date
from typing import Sequence

import numpy as np
import pandas as pd

from ..common.rng import derive
from .declare import DERIVED, DimDecl, Script, TimeDecl, calendar_of, calendar_values
from .expr import DeclarationError, edges, parse

STAGE = "s01_engine"

#: Quantities in these units are recorded as whole numbers. Everything else gets
#: one decimal place, except columns that are already integral.
INTEGER_UNITS = frozenset({
    "usd", "eur", "cny", "rmb", "gbp", "jpy",
    "count", "counts", "visits", "orders", "units", "items", "people", "patients",
    "cases", "rows", "tickets", "calls", "transactions", "students", "employees",
})


def generate(script: Script, seed: int) -> pd.DataFrame:
    """Declarations plus a seed to a fact table. Reproducible bit for bit."""
    n = script.n_rows
    columns: dict[str, np.ndarray] = {}

    for d in script.dims:                     # declaration order puts parents first
        columns[d.name] = _draw_dim(d, columns, n, derive(seed, STAGE, d.name))

    env = dict(columns)
    if script.time is not None:
        days = _draw_time(script.time, n, derive(seed, STAGE, script.time.name))
        columns[script.time.name] = np.array([np.datetime64(d) for d in days])
        for name in calendar_values(script.time):
            i = DERIVED.index(name)
            columns[name] = np.array([calendar_of(d)[i] for d in days])
        env = dict(columns)
        origin = date.fromisoformat(script.time.start)
        env[script.time.name] = np.array([(d - origin).days for d in days], dtype=float)

    for name in topo_order(script):
        decl = next(m for m in script.measures if m.name == name)
        values = parse(decl.expr).eval(env, derive(seed, STAGE, name), n)
        values = np.round(values, _decimals(decl.unit, values))
        columns[name] = values
        env[name] = values

    return pd.DataFrame(columns)


# ---------------------------------------------------------------- dependency graph

def topo_order(script: Script) -> tuple[str, ...]:
    """Topological order of the numeric columns. A cycle is reported as a path."""
    names = [m.name for m in script.measures]
    graph = {n: [] for n in names}
    indegree = {n: 0 for n in names}
    for src, dst in edges(tuple((m.name, m.expr) for m in script.measures)):
        graph[src].append(dst)
        indegree[dst] += 1

    ready = [n for n in names if indegree[n] == 0]      # declaration order breaks ties
    out: list[str] = []
    while ready:
        node = ready.pop(0)
        out.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
    if len(out) != len(names):
        raise DeclarationError(
            f"numeric columns reference each other in a cycle: "
            f"{_cycle(graph, set(names) - set(out))}")
    return tuple(out)


def _cycle(graph: dict[str, list[str]], nodes: set[str]) -> str:
    """Find one cycle among the remaining nodes and write it as `a -> b -> a`."""
    start = sorted(nodes)[0]
    path, seen = [start], {start}
    node = start
    while True:
        nxt = next((m for m in graph[node] if m in nodes), None)
        if nxt is None:
            return " -> ".join(path)
        path.append(nxt)
        if nxt in seen:
            return " -> ".join(path)
        seen.add(nxt)
        node = nxt


# ---------------------------------------------------------------- non-numeric columns

def _allocate(n: int, weights: Sequence[float] | None, size: int, who: str,
              *, every_value: bool = True) -> np.ndarray:
    """Split n rows across `size` values by weight. Deterministic.

    `every_value` says whether all of them must come out non-empty. A column as a
    whole must show every value it declares, or its declared cardinality -- which
    is what decided the chart families -- would be a promise the data breaks. So
    when a weight is small enough that largest-remainder rounding leaves a value
    with nothing, one row moves over from the largest bucket.

    Inside one parent value it is the opposite: a weight of zero is how a strict
    hierarchy is written, where a child belongs to exactly one parent. Forcing a
    row in there would put every child under every parent.
    """
    w = np.full(size, 1.0) if weights is None else np.asarray(weights, dtype=float)
    wanted = size if every_value else int(np.count_nonzero(w))
    if n < wanted:
        raise DeclarationError(
            f"`{who}` needs {wanted} values but has only {n} rows to spread across "
            "them; raise the row count or declare fewer values")

    raw = w / w.sum() * n
    counts = np.floor(raw).astype(int)
    order = np.lexsort((np.arange(size), -(raw - counts)))
    takers = order if every_value else order[w[order] > 0]
    for i in range(n - int(counts.sum())):
        counts[takers[i % len(takers)]] += 1

    if every_value:
        for empty in np.flatnonzero(counts == 0):
            counts[int(np.argmax(counts))] -= 1
            counts[empty] = 1
    return counts


def _spread(values: Sequence[str], counts: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    return np.repeat(np.asarray(values, dtype=object), counts)[rng.permutation(int(counts.sum()))]


def _draw_dim(decl: DimDecl, columns: dict[str, np.ndarray], n: int,
              rng: np.random.Generator) -> np.ndarray:
    if decl.parent is None:
        weights = decl.weights if not isinstance(decl.weights, dict) else None
        return _spread(decl.values, _allocate(n, weights, len(decl.values), decl.name), rng)

    out = np.empty(n, dtype=object)
    parent = columns[decl.parent]
    for value in dict.fromkeys(parent):                    # parent values, first seen first
        idx = np.flatnonzero(parent == value)
        weights = decl.weights[value] if isinstance(decl.weights, dict) else decl.weights
        counts = _allocate(len(idx), weights, len(decl.values),
                           f"{decl.name} (within {decl.parent}={value})",
                           every_value=False)
        out[idx] = _spread(decl.values, counts, rng)
    return out


def _draw_time(decl: TimeDecl, n: int, rng: np.random.Generator) -> list[date]:
    points = decl.points()
    counts = _allocate(n, None, len(points), decl.name)
    return list(np.repeat(np.asarray(points, dtype=object), counts)[rng.permutation(n)])


# ---------------------------------------------------------------- post-processing

def _decimals(unit: str, values: np.ndarray) -> int:
    if unit.strip().lower() in INTEGER_UNITS:
        return 0
    return 0 if np.allclose(values, np.round(values)) else 1
