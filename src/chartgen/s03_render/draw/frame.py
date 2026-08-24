"""The frame a panel draws inside: its axes, their ranges, and their labels.

A panel may hold more than one view, and both are drawn against the same axes. So
the ranges are decided once, for the whole panel, before any mark is drawn -- work
it out per view and the second view would widen an axis the first one had already
recorded its boxes against, and every one of those boxes would be silently wrong.

What the frame settles:

    which axis carries the categories, and what they are called
    what each value axis spans, and whether there are one or two of them
    whether the value runs up the image or across it
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Sequence

from matplotlib.ticker import NullLocator

from ...interfaces.figure import ViewSpec
from ...interfaces.record import AxisRole, MarkShape
from ...interfaces.style import StyleVector
from ...registry.charts import CHARTS
from ..style import nice_range, ticks

#: The number a mark is placed by when its value dictionary holds several.
VALUE_KEYS: tuple[str, ...] = ("value", "count", "median", "y", "max", "hi", "cum_end")

#: Shapes the value may run across the image for instead of up it.
TURNABLE: frozenset[MarkShape] = frozenset({"rect"})

#: Types drawn across the image whatever the style says. A funnel reads down a
#: column of stages, so its value has to run the other way.
ALWAYS_HORIZONTAL: frozenset[str] = frozenset({"funnel"})


@dataclass(frozen=True)
class Frame:
    """Everything both views of a panel have to agree on before either is drawn."""

    categories: tuple[str, ...] = ()
    series: tuple[str, ...] = ()
    groups: tuple[str, ...] = ()            # the second row of category labels
    numeric_x: tuple[float, float] | None = None
    ranges: dict[AxisRole, tuple[float, float, float]] = field(default_factory=dict)
    horizontal: bool = False
    is_time: bool = False
    roles: tuple[AxisRole, ...] = ("y",)    # one role per view, in view order

    def role_for(self, layer: int) -> AxisRole:
        return self.roles[min(layer, len(self.roles) - 1)]

    def limits(self, role: AxisRole) -> tuple[float, float]:
        lo, hi, _ = self.ranges[role]
        return (lo, hi)

    def step(self, role: AxisRole) -> float:
        return self.ranges[role][2]

    def position(self, category: str) -> float:
        return float(self.categories.index(category))


def categories_of(view: ViewSpec) -> list[str]:
    """The first segment of every key, once each, in the order the values came out."""
    out: list[str] = []
    for d in view.data:
        if d.key and d.key[0] not in out:
            out.append(d.key[0])
    return out


def series_of(view: ViewSpec) -> list[str]:
    """What a legend for this view would list.

    An inner grouping column names the series; without one, a view that shares its
    plotting area is named by the prefix it carries, which is exactly what a combo
    chart's legend says.

    A colour group is not an inner grouping column. It is a second name every mark
    already has -- a site reports to one region -- so it adds a key segment without
    changing what a mark covers, and a shape that places one mark per series would
    spread a category's single mark across as many slots as there are regions.
    """
    spec = CHARTS[view.binding.chart_type]
    if spec.shape == "per_row":
        return sorted({d.key[0] for d in view.data if len(d.key) > 1})
    if view.binding.n_group >= 2:
        out: list[str] = []
        for d in view.data:
            if len(d.key) >= 2 and d.key[1] not in out:
                out.append(d.key[1])
        return out
    return list(view.key_prefix) if view.prefix_names_a_series else []


def coarser(labels: Sequence[str]) -> tuple[str, ...]:
    """The coarser period each time label falls in: the year of a month, the month of
    a day. It is what a second row of tick labels names, and it only exists where the
    labels themselves have a coarser period to belong to.
    """
    parts = [label.split("-") for label in labels]
    if not parts or any(not p[0].isdigit() for p in parts):
        return ()
    depth = min(len(p) for p in parts)
    if depth < 2:
        return ()
    coarse = tuple("-".join(p[:depth - 1]) for p in parts)
    return coarse if len(set(coarse)) < len(coarse) else ()


def scalars_of(view: ViewSpec) -> list[float]:
    """Every number a mark of this view has to fit inside the value axis."""
    out: list[float] = []
    for d in view.data:
        picked = [d.values[k] for k in VALUE_KEYS if k in d.values]
        for key in ("min", "cum_start", "lo", "q1"):
            if key in d.values:
                picked.append(d.values[key])
        out += [float(v) for v in (picked or list(d.values.values()))]
    return out


def plan(views: Sequence[ViewSpec], style: StyleVector, *,
         two_axes: bool = False) -> Frame:
    """Settle the axes for a panel from every view that will draw on it."""
    first = CHARTS[views[0].binding.chart_type]
    horizontal = (first.name in ALWAYS_HORIZONTAL or
                  (style.orientation == "horizontal" and len(views) == 1
                   and first.primary_mark in TURNABLE
                   and first.shape not in ("per_row", "binned_count")))
    # A turned figure puts the value on the horizontal axis, so that is the axis a
    # mark says it was measured against. Two overlaid views stay upright: a second
    # value axis has nowhere to go once the categories are down the left side.
    roles: tuple[AxisRole, ...] = (("x",) if horizontal else
                                   tuple("y_right" if (two_axes and i) else "y"
                                         for i in range(len(views))))

    numeric_x = None
    categories: tuple[str, ...] = ()
    if first.shape == "per_row":
        xs = [d.values["x"] for v in views for d in v.data]
        numeric_x = (min(xs), max(xs)) if xs else (0.0, 1.0)
    elif first.shape == "binned_count":
        edges = [d.values["bin_lo"] for d in views[0].data] + [
            d.values["bin_hi"] for d in views[0].data]
        numeric_x = (min(edges), max(edges))
    else:
        categories = tuple(categories_of(views[0]))

    ranges: dict[AxisRole, tuple[float, float, float]] = {}
    for role in dict.fromkeys(roles):
        values = [v for view, r in zip(views, roles) if r == role for v in scalars_of(view)]
        ranges[role] = nice_range(min(values), max(values), style) if values else (0.0, 1.0, 0.5)

    is_time = bool(views[0].binding.time)
    return Frame(categories=categories,
                 series=tuple(dict.fromkeys(s for v in views for s in series_of(v))),
                 groups=coarser(categories) if is_time else (),
                 numeric_x=numeric_x, ranges=ranges, horizontal=horizontal,
                 is_time=is_time, roles=roles)


def unify(plans: Sequence[Frame], roles: Sequence[AxisRole]) -> list[Frame]:
    """Give every panel the same range on the axes the figure says they share.

    Planned per panel, each one gets the range its own numbers need, and panels drawn
    against different ranges cannot be compared by eye however alike they look. The
    figure says the axis is shared and the record says so too; both have to be true
    of the pixels, and this is where that is made so.

    Only the named axes. Two panels showing minutes and dollars share their category
    axis and nothing else, and forcing one value range on them would flatten the
    smaller of the two into the baseline.
    """
    if len(plans) < 2:
        return list(plans)
    merged = {}
    for role in roles:
        spans = [frame.ranges[role] for frame in plans if role in frame.ranges]
        if len(spans) < 2:
            continue
        merged[role] = (min(s[0] for s in spans), max(s[1] for s in spans),
                        max(s[2] for s in spans))
    return [replace(frame, ranges={**frame.ranges,
                                   **{r: v for r, v in merged.items() if r in frame.ranges}})
            for frame in plans]


def apply(ctx, frame: Frame, *, axis_titles: dict[str, bool] | None = None) -> None:
    """Put the frame onto the plotting area and record what it became.

    Recorded after it is applied rather than as it is asked for: the value range the
    readability rule reads has to be the one the marks were actually drawn against.
    """
    panel, style, canvas = ctx.panel, ctx.style, ctx.canvas
    role = ctx.value_axis
    value_ax = panel.right_ax if role == "y_right" else panel.ax
    lo, hi = frame.limits(role)

    # The scale goes on before the limits. Changing an axis's scale re-runs the
    # autoscaler, and at this point nothing has been drawn for it to scale to -- so
    # limits set first come back as whatever the empty axes defaulted to, and the
    # record would then describe an axis the marks were not drawn against.
    logarithmic = style.log_scale and lo > 0
    if logarithmic:
        (value_ax.set_xscale if frame.horizontal else value_ax.set_yscale)("log")

    if frame.horizontal:
        value_ax.set_xlim(lo, hi)
        panel.ax.set_ylim(-0.5, max(len(frame.categories) - 0.5, 0.5))
    else:
        value_ax.set_ylim(lo, hi)
        if frame.numeric_x is not None:
            panel.ax.set_xlim(*frame.numeric_x)
        else:
            panel.ax.set_xlim(-0.5, max(len(frame.categories) - 0.5, 0.5))

    if not logarithmic and (step := frame.step(role)) > 0:
        marks = ticks(lo, hi, step)
        (value_ax.set_xticks if frame.horizontal else value_ax.set_yticks)(marks)
    _format_ticks(ctx, value_ax, frame.horizontal)

    if ctx.layer == 0:
        if frame.categories:
            canvas.category_axis(panel, frame.categories, horizontal=frame.horizontal,
                                 is_time=frame.is_time, groups=frame.groups)
        # Each title is settled by the axis it names. A figure may share one axis and
        # not the other -- two panels over the same weeks carrying different measures
        # share the category axis and nothing else -- and one flag for both leaves the
        # second measure unnamed on the page while the record still says what it is
        # called.
        wanted = {"y": True, "x": True} if axis_titles is None else axis_titles
        value_on = wanted["x" if frame.horizontal else "y"]
        category_on = wanted["y" if frame.horizontal else "x"]
        if value_on or category_on:
            canvas.axis_title(panel,
                              value=ctx.value_label() if value_on else "",
                              category=ctx.category_label() if category_on else "",
                              unit=ctx.unit(), horizontal=frame.horizontal)
        canvas.zero_line(panel)
        panel.record_axis("y" if frame.horizontal else "x", ctx.cross_column(),
                          label=ctx.category_label())
    if role == "y_right":
        canvas.second_axis_title(panel, ctx.value_label(), ctx.unit())
    panel.record_axis(role, ctx.measure_column(), scale="log" if logarithmic else "linear",
                      label=ctx.value_label())


def _format_ticks(ctx, value_ax, horizontal: bool) -> None:
    """Write the value axis's ticks the way the value labels are written.

    One function formats both. A figure whose bars say `$1,240` above ticks reading
    `1240.0` is telling a reader that two different quantities are drawn, and the
    number format is a style decision that has to apply to the whole figure or to
    none of it.
    """
    from matplotlib.ticker import FuncFormatter

    from ..style import format_number

    unit = ctx.unit()
    axis = value_ax.xaxis if horizontal else value_ax.yaxis
    axis.set_major_formatter(FuncFormatter(
        lambda value, _pos: format_number(float(value), ctx.style, unit)))


def bare(ax) -> None:
    """Take every axis artist off a plotting area that measures nothing along an axis.

    A pie and a table chart carry their value in an angle and in a printed string, so
    a scale drawn beside either one invites a reader to measure something that is not
    there. Emptying the tick list is not enough on its own: a log axis keeps a minor
    locator of its own, and that one goes on drawing a ladder of ticks and labels
    after the major ticks are gone -- the value axis is a style dimension, so which
    figures this happens to is decided by the sampler.
    """
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_locator(NullLocator())
        axis.set_minor_locator(NullLocator())
    ax.tick_params(which="both", length=0, labelleft=False, labelbottom=False)
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)


def scale_of(ctx, frame: Frame) -> str:
    return "log" if ctx.style.log_scale and frame.limits(ctx.value_axis)[0] > 0 else "linear"
