"""Deciding whether a projected view is worth drawing, and whether the batch already has it.

Two groups of judgement, and they answer different questions:

    data conditions   does this figure carry any information -- do the values differ,
                      do they vary, does every cell rest on enough rows
    redundancy        does the batch already hold a figure with the same key set and
                      the same mark shape

The redundancy rule has no threshold to tune, and the pair it compares is the pair
the training target is made of: the key set decides which entities appear on the
page, the mark shape decides what the box looks like, how many numbers the value
dictionary holds and whether any of them can be measured off the pixels. Two
figures that match on both carry almost the same signal.

A count is not a substitute. Eight figures all shaped `bar(hospital x ...)` satisfy
any budget while teaching one thing.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field

from ..interfaces.figure import FigureSpec, ViewSpec
from ..registry.charts import CHARTS, DEFAULT_BAND, DensityBand, bound_at, within
from .project import group_keys

#: Coefficient of variation a figure has to reach before it is more than a flat line.
MIN_VARIATION = 0.02

#: Distinct values a figure needs, as a fraction of how many marks it draws, and the
#: point past which more marks stop needing more distinct values.
DISTINCT_FRACTION = 0.5
DISTINCT_CEILING = 4

RejectKind = str


@dataclass(frozen=True)
class Verdict:
    ok: bool
    reason: str = ""
    kind: RejectKind = ""

    def __bool__(self) -> bool:
        return self.ok


_OK = Verdict(True)


def _no(kind: RejectKind, reason: str) -> Verdict:
    return Verdict(False, reason, kind)


# ---------------------------------------------------------------- data conditions

#: Which number stands for a mark when its value dictionary holds several: the one
#: the reader takes off the value axis. A scatter point is its vertical coordinate,
#: a box its median, a range bar its upper edge.
SCALAR_KEYS: tuple[str, ...] = ("value", "count", "median", "y", "max", "hi", "cum_end")


def _scalars(view: ViewSpec) -> list[float]:
    """The one number per mark the data conditions are judged on."""
    out = []
    for d in view.data:
        for k in SCALAR_KEYS:
            if k in d.values:
                out.append(float(d.values[k]))
                break
        else:
            out.append(float(next(iter(d.values.values()), 0.0)))
    return out


def data_conditions(view: ViewSpec, *, density: DensityBand = DEFAULT_BAND) -> Verdict:
    """The three checks that need real values, plus the per-type ones.

    Which of them apply follows from the projection shape: a per-row view has one
    row behind every mark by construction, so asking it for rows per cell asks
    nothing.
    """
    spec = CHARTS[view.binding.chart_type]
    values = _scalars(view)
    if not values:
        return _no("empty", f"{spec.name} projected to no marks")

    n_marks = len(group_keys(view)) if spec.shape == "grouped_fivenum" else len(view.data)
    bound = bound_at(spec.n_marks, density)
    if not within(n_marks, bound):
        return _no("marks", f"{spec.name} draws {n_marks} marks, outside {bound}")

    if spec.check_distinct:
        distinct = len({round(v, 9) for v in values})
        needed = min(DISTINCT_CEILING, max(2, math.ceil(len(values) * DISTINCT_FRACTION)))
        if distinct < needed:
            return _no("distinct",
                       f"{spec.name} has {distinct} distinct values across {len(values)} "
                       f"marks, below {needed}: the marks would look the same height")

    if spec.check_variation:
        mean = sum(values) / len(values)
        sd = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
        cv = abs(sd / mean) if mean else 0.0
        if cv < MIN_VARIATION:
            return _no("variation",
                       f"{spec.name} varies by {cv:.4f}, below {MIN_VARIATION}: a flat figure")

    if spec.min_rows_per_cell and spec.shape != "per_row":
        thin = [d for d in view.data if d.rows < spec.min_rows_per_cell and
                len(d.key) == view.binding.n_key]
        if thin:
            return _no("thin",
                       f"{spec.name} needs {spec.min_rows_per_cell} rows per cell; "
                       f"{len(thin)} cells have fewer, the thinnest {min(d.rows for d in thin)}")

    if spec.monotone_decreasing:
        if any(b > a + 1e-9 for a, b in zip(values, values[1:])):
            return _no("monotone", f"{spec.name} needs values that only fall")

    if spec.min_share:
        total = sum(values)
        smallest = min(values) / total if total else 0.0
        if smallest < spec.min_share:
            return _no("share",
                       f"{spec.name} needs every sector above {spec.min_share:.0%}, "
                       f"smallest is {smallest:.1%}")
    return _OK


# ---------------------------------------------------------------- redundancy

Signature = tuple[frozenset, tuple[str, ...]]


def signature(view: ViewSpec) -> Signature:
    """What makes two views the same training signal: which entities appear, and
    what shape their marks are.

    A per-row view is signed by its columns instead of its keys. Its keys are row
    identifiers, which two scatter plots of different measures would share exactly,
    and which two scatter plots of the same measures would also share -- so the keys
    say nothing about what the figure shows.
    """
    spec = CHARTS[view.binding.chart_type]
    if spec.shape == "per_row":
        return (frozenset(view.binding.measures) | frozenset(view.binding.dims), spec.mark)
    return (group_keys(view), spec.mark)


def figure_signature(spec: FigureSpec) -> Signature:
    keys: frozenset = frozenset()
    marks: list[str] = []
    for view in spec.views:
        k, m = signature(view)
        keys = keys | k
        marks += [s for s in m if s not in marks]
    return (keys, tuple(marks))


@dataclass
class Batch:
    """The figures accepted so far, and the rule that keeps the next one from repeating them.

    Two exemptions, both because the figure's value is its layout rather than its
    data. A figure derived from an anchor repeats keys on purpose -- that repetition
    is what makes it a paired sample, and a shared legend is the only source of the
    legend-binding target. Two figures composed onto one page under different titles
    are told apart by their titles, and rejecting the second would rule out the
    side-by-side layout that puts the same categories in both.
    """

    signatures: dict[Signature, str] = field(default_factory=dict)
    rejected: Counter = field(default_factory=Counter)

    def exempt(self, spec: FigureSpec) -> bool:
        if spec.source.kind in ("panel", "overlay", "page") or len(spec.panels) > 1:
            return True
        return bool(spec.page_id) and bool(spec.text("title"))

    def check(self, spec: FigureSpec) -> Verdict:
        if self.exempt(spec):
            return _OK
        sig = figure_signature(spec)
        if (owner := self.signatures.get(sig)) is not None:
            return _no("redundant",
                       f"{owner} already draws these keys as {sig[1]}: same entities, "
                       "same mark shape, so the same signal")
        return _OK

    def add(self, spec: FigureSpec) -> None:
        self.signatures.setdefault(figure_signature(spec), spec.figure_id)

    def reject(self, verdict: Verdict) -> None:
        self.rejected[verdict.kind or "unknown"] += 1

    def admit(self, spec: FigureSpec, *, density: DensityBand = DEFAULT_BAND) -> Verdict:
        """Both groups of judgement, in the order that fails cheapest first."""
        for view in spec.views:
            if not (v := data_conditions(view, density=density)):
                self.reject(v)
                return v
        if not (v := self.check(spec)):
            self.reject(v)
            return v
        self.add(spec)
        return _OK

    def counts(self) -> dict[str, int]:
        """Why candidates were turned away. A kind that dominates is a design signal,
        not a number to tune away."""
        return dict(self.rejected)
