"""Deriving a second view from one that was already accepted.

Two views can sit in two plotting areas or in one. Both are derived, never sampled:
the anchor fixes the columns and a rule computes the rest, so the pair is
reproducible and the two views are guaranteed to share their arithmetic.

    small_multiples  the same view repeated, one panel per value of a column
    facet            the same metric grouped by a category the anchor does not use
    drilldown        one level deeper, preferring a child of a column the anchor groups by
    time_split       the same view over two windows cut out of the anchor
    dual_metric      the same grouping, the next measure
    part_whole       the same grouping, read as shares instead of as a comparison

    overlay_metric   two measures in one plotting area
    overlay_slice    one measure, two windows or two aggregates, in one plotting area
    overlay_range    a value and the spread around it

The anchor has to be a figure that was already accepted on its own. A view derived
from something that appears nowhere else gives away the layout pairing: the value
of the same view drawn once alone and once inside a multi-panel figure is that the
keys and values match while the pixels do not.

The row filter appears only here. It serves the two windows of a time comparison,
it is cut from the anchor at the moment the pair is built, and it is never one of
the dimensions a view is sampled over.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field, replace
from typing import Callable

import pandas as pd

from ..interfaces.figure import (
    Binding, Layout, PanelSpec, Relation, Sharing, TextBlock, TimeWindow, ViewSpec,
)
from ..interfaces.table import TableSchema
from ..registry.charts import CHARTS, DEFAULT_BAND, DensityBand
from ..registry.conditions import check
from .admit import data_conditions
from .keys import with_colour_group
from .project import ProjectionError, project

#: Panels a relation may produce.
MAX_PANELS = 4

#: Two measures on one value axis stay legible only while their ranges are within
#: this factor of each other. Past it the smaller series flattens onto the axis and
#: the value self-check throws the whole figure away.
RANGE_RATIO = 20.0


@dataclass(frozen=True)
class Derivation:
    """One derived figure: its panels, how they are laid out, and what they share."""

    relation: Relation
    panels: tuple[PanelSpec, ...]
    layout: Layout
    sharing: Sharing


@dataclass
class Context:
    """Everything a relation rule reads, and a tally of what it turned away.

    It never sees the figure batch: a rule decides whether a second view is legal,
    not whether the batch already has something like it.
    """

    df: pd.DataFrame
    schema: TableSchema
    seed: int = 0
    density: DensityBand = DEFAULT_BAND
    max_tier: int = 3
    max_panels: int = MAX_PANELS
    rejected: Counter = field(default_factory=Counter)

    def build(self, binding: Binding, row_filter: TimeWindow | None = None,
              rows: pd.DataFrame | None = None) -> ViewSpec | None:
        """Project one binding, or give up on it and record why.

        A relation that cannot produce a legal second view produces no figure rather
        than a degraded one. Why candidates fail is the main thing a run has to say
        about its own health, so every path out of here is counted.
        """
        if CHARTS[binding.chart_type].tier > self.max_tier:
            return self._no("tier")
        if not check(binding, self.schema, density=self.density):
            return self._no("conditions")
        binding = with_colour_group(binding, self.df, self.schema)
        try:
            view = project(self.df if rows is None else rows, binding, self.schema,
                           row_filter=row_filter, seed=self.seed, density=self.density)
        except ProjectionError:
            return self._no("projection")
        verdict = data_conditions(view, density=self.density)
        if not verdict:
            return self._no(verdict.kind)
        return view

    def _no(self, kind: str) -> None:
        self.rejected[kind] += 1
        return None


# ---------------------------------------------------------------- shared reading

def series_column(binding: Binding) -> str | None:
    """The column carried by colour: the innermost grouping column.

    A shared legend requires every panel to use the same one. That is a constraint
    on the figure, not a style setting -- with different series columns per panel
    the legend splits into one per panel and `applies_to_panels` says nothing,
    which is the whole reason a multi-panel figure is worth drawing.
    """
    columns = binding.group_columns
    return columns[-1] if columns else None


def next_measure(binding: Binding, schema: TableSchema) -> str | None:
    """The second measure of a two-metric pairing, by a fixed order of preference.

    A quantity and something computed from it is the pairing reports draw most
    often, so an edge in the dependency graph comes first. Then a measure of the
    other additivity, which is the total-and-rate shape. Then a different unit,
    because that is what a second axis is for -- two measures in one unit are better
    served by grouped bars. The column list breaks any remaining tie.
    """
    first = binding.measures[0] if binding.measures else None
    if first is None:
        return None
    others = [c for c in schema.measures if c.name != first]
    if not others:
        return None
    own = schema.column(first)
    linked = {b for a, b in schema.dependencies if a == first}
    linked |= {a for a, b in schema.dependencies if b == first}
    for wanted in (lambda c: c.name in linked,
                   lambda c: c.additive is not own.additive,
                   lambda c: c.unit != own.unit,
                   lambda c: True):
        for c in others:
            if wanted(c):
                return c.name
    return None


def aggregate_for(measure: str, schema: TableSchema) -> str:
    """An additive quantity is summed, anything else is averaged -- the same rule the
    declarations give the aggregate sets."""
    return "SUM" if schema.column(measure).additive else "AVG"


def needs_two_axes(a: ViewSpec, b: ViewSpec, schema: TableSchema) -> bool:
    """Whether an overlay needs a second value axis.

    Different units always do. The same unit usually does not -- but two series
    twenty times apart in magnitude flatten the smaller one onto the axis, and a
    flattened series fails the value self-check and takes the figure with it. So
    the axis count follows from the numbers, not from the name of the layout.
    """
    units = {schema.column(m).unit for v in (a, b) for m in v.binding.measures}
    if len(units) > 1:
        return True
    spans = [max((abs(x) for d in v.data for x in d.values.values()), default=0.0)
             for v in (a, b)]
    low, high = min(spans), max(spans)
    return high > RANGE_RATIO * low if low > 0 else high > 0


def _ancestors(column: str, schema: TableSchema) -> set[str]:
    """Every column above this one in its hierarchy."""
    out: set[str] = set()
    cursor = schema.column(column).parent if schema.has(column) else None
    while cursor:
        out.add(cursor)
        cursor = schema.column(cursor).parent
    return out


def _disjoint_categories(binding: Binding, schema: TableSchema) -> list[str]:
    """Category columns that would cut the data a different way from the anchor's.

    Three kinds are left out. One the anchor already groups by. One that is another
    name for a column it groups by -- a calendar field read off its time column says
    where a point falls, not how the rows are split. And one that sits above a column
    it groups by: every site reports to one region, so grouping by site and region
    produces exactly the groups grouping by site alone produces, and the second panel
    of the pair would be the first panel redrawn.
    """
    used = set(binding.group_columns)
    above = {a for name in used for a in _ancestors(name, schema)}
    return [c.name for c in schema.categories
            if c.name not in used and c.name not in above
            and c.derived_from not in used and c.parent not in used]


def _types_taking(n_cat: int, family: str | None, max_tier: int) -> list[str]:
    return [c.name for c in CHARTS.values()
            if c.family == family and c.tier <= max_tier
            and c.n_cat[0] <= n_cat <= (c.n_cat[1] if c.n_cat[1] is not None else n_cat)]


# ---------------------------------------------------------------- panel relations

def _with_a_series(binding: Binding, ctx: Context, split: str) -> list[Binding]:
    """The same view, deepened by one grouping column, in preference order.

    A view with one grouping column puts its names on the axis, so repeating it
    across panels produces no legend at all. Deepened by a column every panel shares,
    the same repetition produces one legend that covers all of them -- which is the
    only place a legend entry governing several panels comes from, and the whole
    content of that training target.
    """
    if binding.n_group != 1 or not binding.dims:
        return []
    parent = binding.dims[0]
    children = [c.name for c in ctx.schema.categories if c.parent == parent]
    family = CHARTS[binding.chart_type].family
    out = []
    for inner in children + _disjoint_categories(binding, ctx.schema):
        if inner == split:
            continue
        for chart_type in _types_taking(2, family, ctx.max_tier):
            out.append(replace(binding, chart_type=chart_type, dims=(parent, inner),
                               key_sources=("axis_tick", "legend"), colour_group=inner))
    return out


def small_multiples(anchor: ViewSpec, ctx: Context) -> Derivation | None:
    """The same view once per value of a column the anchor does not use.

    The only relation that puts the same series column in every panel, so it is the
    only one whose legend can cover more than one panel -- and a legend that covers
    several panels is the whole content of the legend-binding target.
    """
    binding = anchor.binding
    if CHARTS[binding.chart_type].shape == "per_row":
        return None
    for name in _disjoint_categories(binding, ctx.schema):
        values = [v for v in ctx.schema.column(name).values][:ctx.max_panels]
        if len(values) < 2:
            continue
        for inner in _with_a_series(binding, ctx, name) + [binding]:
            panels = []
            for i, value in enumerate(values):
                rows = ctx.df.loc[ctx.df[name].astype(str) == value]
                view = ctx.build(inner, rows=rows) if len(rows) else None
                if view is None:
                    panels = []
                    break
                # The panel title is where a reader finds which slice this is, so it
                # is a segment of the key. Without it every panel repeats the same
                # keys with different numbers: four panels of the same three centres
                # give one key three answers, and nothing in the record says which
                # panel any of them came from.
                named = replace(view, key_prefix=(value,),
                                prefix_source=("panel_title",))
                panels.append(PanelSpec(f"p{i}", (named,),
                                        texts=(TextBlock("title", value, "panel", "above"),)))
            if len(panels) >= 2:
                return Derivation("small_multiples", tuple(panels), "grid",
                                  Sharing(share_y=True,
                                          share_legend=inner.n_group >= 2,
                                          series_column=series_column(inner)))
    return None


def facet(anchor: ViewSpec, ctx: Context) -> Derivation | None:
    """The same metric grouped by a category the anchor does not use."""
    binding = anchor.binding
    if binding.n_group != 1 or CHARTS[binding.chart_type].shape != "grouped_scalar":
        return None
    panels = [PanelSpec("p0", (anchor,))]
    for name in _disjoint_categories(binding, ctx.schema):
        if len(panels) >= ctx.max_panels:
            break
        view = ctx.build(replace(binding, dims=(name,), time=None,
                                 key_sources=("axis_tick",)))
        if view is not None:
            panels.append(PanelSpec(f"p{len(panels)}", (view,)))
    if len(panels) < 2:
        return None
    shared = len({series_column(p.view.binding) for p in panels}) == 1
    return Derivation("facet", tuple(panels), "grid",
                      Sharing(share_y=True, share_legend=shared,
                              series_column=series_column(binding) if shared else None))


def drilldown(anchor: ViewSpec, ctx: Context) -> Derivation | None:
    """One level deeper: a child of a column the anchor groups by, else the next
    category column in declaration order."""
    binding = anchor.binding
    if binding.n_group != 1 or not binding.dims:
        return None
    parent = binding.dims[0]
    children = [c.name for c in ctx.schema.categories if c.parent == parent]
    family = CHARTS[binding.chart_type].family
    for name in children + _disjoint_categories(binding, ctx.schema):
        for chart_type in _types_taking(2, family, ctx.max_tier):
            deeper = replace(binding, chart_type=chart_type, dims=(parent, name),
                             key_sources=("axis_tick", "legend"), colour_group=name)
            view = ctx.build(deeper)
            if view is not None:
                return Derivation(
                    "drilldown", (PanelSpec("p0", (anchor,)), PanelSpec("p1", (view,))),
                    "side_by_side", Sharing(share_y=True))
    return None


def time_split(anchor: ViewSpec, ctx: Context) -> Derivation | None:
    """The same view over two windows, cut out of the anchor on the spot.

    The two panels carry the same keys with different numbers, which is what makes
    them a pair. What tells them apart is the panel, and the exporter is what
    decides whether the panel's name goes into the key it hands the model.
    """
    column = _time_column(anchor.binding, ctx.schema)
    if column is None:
        return None
    panels = []
    for i, window in enumerate(_halves(ctx.df, column)):
        view = ctx.build(anchor.binding, window)
        if view is None:
            return None
        panels.append(PanelSpec(f"p{i}", (view,),
                                texts=(TextBlock("title", window.label, "panel", "above"),)))
    return Derivation("time_split", tuple(panels), "side_by_side",
                      Sharing(share_x=True, share_y=True,
                              share_legend=True, series_column=series_column(anchor.binding)))


def dual_metric(anchor: ViewSpec, ctx: Context) -> Derivation | None:
    """The same grouping, the next measure, in its own plotting area."""
    second = next_measure(anchor.binding, ctx.schema)
    if second is None:
        return None
    view = ctx.build(replace(anchor.binding, measures=(second,),
                             aggregate=aggregate_for(second, ctx.schema)))
    if view is None:
        return None
    return Derivation("dual_metric",
                      (PanelSpec("p0", (anchor,)), PanelSpec("p1", (view,))),
                      "side_by_side", Sharing(share_x=True))


def part_whole(anchor: ViewSpec, ctx: Context) -> Derivation | None:
    """The same grouping and measure, read as shares instead of as a comparison."""
    binding = anchor.binding
    if CHARTS[binding.chart_type].family != "comparison" or not binding.measures:
        return None
    for chart_type in _types_taking(binding.n_group - (1 if binding.time else 0),
                                    "composition", ctx.max_tier):
        view = ctx.build(replace(binding, chart_type=chart_type,
                                 key_sources=("legend",) * binding.n_group))
        if view is not None:
            return Derivation("part_whole",
                              (PanelSpec("p0", (anchor,)), PanelSpec("p1", (view,))),
                              "side_by_side",
                              Sharing(share_legend=True, series_column=series_column(binding)))
    return None


PanelRule = Callable[[ViewSpec, Context], "Derivation | None"]

PANEL_RELATIONS: tuple[PanelRule, ...] = (
    small_multiples, facet, drilldown, time_split, dual_metric, part_whole,
)


# ---------------------------------------------------------------- overlay relations

def _named(view: ViewSpec, label: str) -> ViewSpec:
    """Put the series name at the front of every key in this view.

    Two views in one plotting area group by the same columns, so their marks would
    otherwise land on the same `(panel_id, key)` with different numbers. The name is
    what the combo chart's legend says, which is also where a reader gets it from.
    """
    return replace(view, key_prefix=(label,), prefix_source=("legend",))


def _overlay(relation: Relation, base: ViewSpec, over: ViewSpec,
             ctx: Context) -> Derivation:
    two = needs_two_axes(base, over, ctx.schema)
    return Derivation(relation, (PanelSpec("p0", (base, over)),), "overlay",
                      Sharing(share_x=True, share_y=not two,
                              share_legend=True, series_column=None))


def _point_partner(binding: Binding) -> str | None:
    """The type that draws the same grouping as points instead of rectangles.

    An overlay is readable only if its two layers have different mark shapes. Two
    sets of points in one plotting area sit on top of each other, their boxes
    coincide, and nothing in the record can tell them apart afterwards.
    """
    if binding.time:
        return "line"
    return "category_line" if binding.dims else None


def _measure_label(name: str, aggregate: str, schema: TableSchema) -> str:
    unit = schema.column(name).unit
    return f"{aggregate}({name})" + (f" [{unit}]" if unit else "")


def overlay_metric(anchor: ViewSpec, ctx: Context) -> Derivation | None:
    """Two measures over one grouping, in one plotting area.

    The additive one is the base, drawn as rectangles from the axis; the other goes
    over it as points. That is the total-and-rate figure every report has.
    """
    binding = anchor.binding
    if CHARTS[binding.chart_type].primary_mark != "rect":
        return None
    second = next_measure(binding, ctx.schema)
    partner = _point_partner(binding)
    if second is None or partner is None:
        return None
    aggregate = aggregate_for(second, ctx.schema)
    view = ctx.build(replace(binding, chart_type=partner, measures=(second,),
                             aggregate=aggregate))
    if view is None:
        return None
    return _overlay("overlay_metric",
                    _named(anchor, _measure_label(binding.measures[0], binding.aggregate,
                                                  ctx.schema)),
                    _named(view, _measure_label(second, aggregate, ctx.schema)), ctx)


def overlay_slice(anchor: ViewSpec, ctx: Context) -> Derivation | None:
    """One measure twice: two time windows, or two aggregates of the same column."""
    binding = anchor.binding
    partner = _point_partner(binding)
    if CHARTS[binding.chart_type].primary_mark != "rect" or partner is None:
        return None

    column = _time_column(binding, ctx.schema)
    if column is not None:
        early, late = _halves(ctx.df, column)
        base = ctx.build(binding, early)
        over = ctx.build(replace(binding, chart_type=partner), late)
        if base is not None and over is not None:
            return _overlay("overlay_slice", _named(base, early.label),
                            _named(over, late.label), ctx)

    if binding.aggregate == "AVG":
        over = ctx.build(replace(binding, chart_type=partner, aggregate="MAX"))
        if over is not None:
            return _overlay("overlay_slice", _named(anchor, "AVG"), _named(over, "MAX"), ctx)
    return None


#: Shapes an overlay may sit on. A second series is drawn against the base's value
#: axis, and a sector or a cell does not have one -- there is nothing for the
#: overlaid series to be measured against.
OVERLAY_BASES: frozenset[str] = frozenset({"rect", "point"})


def overlay_range(anchor: ViewSpec, ctx: Context) -> Derivation | None:
    """A value and the spread it summarises, drawn over each other."""
    binding = anchor.binding
    if not binding.measures or CHARTS[binding.chart_type].primary_mark not in OVERLAY_BASES:
        return None
    partner = "windsock" if binding.time else "error_bar"
    if CHARTS[partner].primary_mark == CHARTS[binding.chart_type].primary_mark:
        return None
    view = ctx.build(replace(binding, chart_type=partner, aggregate="FIVE_NUM"))
    if view is None:
        return None
    return _overlay("overlay_range", _named(anchor, binding.aggregate),
                    _named(view, "spread"), ctx)


OVERLAY_RELATIONS: tuple[PanelRule, ...] = (
    overlay_metric, overlay_slice, overlay_range,
)

#: Relations whose second view may go into another image on the same page rather
#: than into another plotting area on the same image. One relation, three places to
#: put it -- which is why a relation is a composition rule and not a row in the type
#: table.
#:
#: The overlay relations are absent because two views in one plotting area cannot
#: become two images: what they say is that these numbers are read against each
#: other, and a page separates them. `small_multiples` is absent for a different
#: reason: one legend covering several panels is the only source of the
#: legend-binding target, and it does not survive being split into separate images.
PAGE_RELATIONS: tuple[PanelRule, ...] = (
    time_split, dual_metric, part_whole, drilldown, facet,
)

ALL_RELATIONS: tuple[PanelRule, ...] = PANEL_RELATIONS + OVERLAY_RELATIONS


# ---------------------------------------------------------------- row filters

def _time_column(binding: Binding, schema: TableSchema) -> str | None:
    """The time column a window can be cut on: the one the view groups by, or the
    single declared one when the view groups by categories."""
    if binding.time:
        return binding.time
    times = schema.times
    return times[0].name if len(times) == 1 else None


def _halves(df: pd.DataFrame, column: str) -> tuple[TimeWindow, TimeWindow]:
    """The rows cut in two at the midpoint of the time span."""
    stamps = pd.to_datetime(df[column])
    start, end = stamps.min(), stamps.max()
    middle = start + (end - start) / 2
    fmt = "%Y-%m-%d"
    second = middle + pd.Timedelta(days=1)
    return (
        TimeWindow(column, start.strftime(fmt), middle.strftime(fmt),
                   f"{start.strftime(fmt)} to {middle.strftime(fmt)}"),
        TimeWindow(column, second.strftime(fmt), end.strftime(fmt),
                   f"{second.strftime(fmt)} to {end.strftime(fmt)}"),
    )
