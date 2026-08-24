"""Choosing which figures a scenario yields, and what each of them draws.

Three ways a figure gets here, and only one of them draws a random number:

    built      one per analysis intent. The binding fixes the columns, the aggregate
               and the family; the chart table fixes which types those allow; the
               declaration order breaks the tie. Nothing is searched
    derived    from a figure already accepted on its own, by one of the relations in
               `panel.py`. At most one figure per relation per scenario
    sampled    a type, some columns and an aggregate drawn at random, validated,
               projected, then admitted or drawn again

The names say how a figure was chosen, not how important it is. There is no main
figure and no supplementary figure.

No candidate list is built. Enumerating every legal view of a schema runs to
hundreds or thousands of entries, each needing a full projection before anyone can
tell whether it passes, in order to ship about a dozen figures.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from typing import Sequence

import numpy as np

from ..common.rng import derive, seed_of
from ..config import Config
from ..interfaces.figure import (
    Binding, FigureSpec, PanelSpec, Sharing, Source, TextBlock, ViewSpec,
)
from ..interfaces.table import AGG_ADDITIVE, AGG_NON_ADDITIVE, FactTable, TableSchema
from ..registry.charts import (
    DENSITY_BANDS, SHAPE_AGGREGATES, DensityBand, band, band_for_rows,
)
from ..registry.conditions import RESAMPLE, check, iter_bindings_for_family
from . import caption, sampling, title
from .keys import key_sources
from .admit import Batch
from .panel import (
    OVERLAY_RELATIONS, PAGE_RELATIONS, PANEL_RELATIONS, Context, PanelRule,
)

STAGE = "s02_compose"


# ---------------------------------------------------------------- assembly

def _with_sources(view: ViewSpec) -> ViewSpec:
    """Fill in where each key segment is read from, when a rule has not already."""
    if view.binding.key_sources:
        return view
    return replace(view, binding=replace(view.binding, key_sources=key_sources(view.binding)))



def _figure(figure_id: str, schema: TableSchema, panels: Sequence[PanelSpec], *,
            source: Source, layout: str = "single", sharing: Sharing = Sharing(),
            relation=None, page_id: str = "") -> FigureSpec:
    return FigureSpec(
        figure_id=figure_id,
        scenario_id=schema.scenario_id,
        panels=tuple(PanelSpec(p.panel_id, tuple(_with_sources(v) for v in p.views), p.texts)
                     for p in panels),
        layout=layout,
        sharing=sharing,
        relation=relation,
        source=source,
        column_units={c.name: c.unit for c in schema.measures if c.unit},
        page_id=page_id,
    )


# ---------------------------------------------------------------- built from an intent

def intent_figures(ctx: Context, batch: Batch, schema: TableSchema,
                   start: int = 1) -> tuple[list[FigureSpec], list[str]]:
    """One figure per intent, or a logged reason why that intent yielded none."""
    out: list[FigureSpec] = []
    log: list[str] = []
    for intent in schema.intents:
        made = None
        for binding in iter_bindings_for_family(
                intent.family, schema, columns=intent.columns,
                aggregate=intent.aggregate, max_tier=ctx.max_tier, density=ctx.density):
            view = ctx.build(binding)
            if view is None:
                continue
            spec = _figure(f"f{start + len(out):02d}", schema, (PanelSpec("p0", (view,)),),
                           source=Source("intent", intent_index=intent.index))
            if batch.admit(spec, density=ctx.density):
                made = spec
                break
        if made is None:
            log.append(f"intent {intent.index + 1} ({intent.family}) yielded no figure: "
                       f"no type in that family fits {intent.columns} with "
                       f"{intent.aggregate}, or the values did not pass admission")
        else:
            out.append(made)
    return out, log


# ---------------------------------------------------------------- derived from an anchor

def derived_figures(anchors: Sequence[FigureSpec], ctx: Context, batch: Batch,
                    schema: TableSchema, start: int, *, rules: Sequence[PanelRule],
                    budget: int, offset: int = 0) -> tuple[list[FigureSpec], list[str]]:
    """At most one figure per relation, from the first anchor that supports it.

    The relations are tried in one order and the budget cuts the tail. Which relation
    the order starts at moves with the scenario, so a budget smaller than the list
    still reaches every relation across a batch. Fixed at the declared order, the last
    entries are never tried at all: with six panel relations and a budget of three,
    the sixth was drawn zero times in ninety-six figures.

    Panel relations and overlay relations are given separate budgets: they are tried
    in one list, so a shared budget would spend itself on the panel relations and
    the batch would never contain a figure with two views in one plotting area.
    """
    out: list[FigureSpec] = []
    log: list[str] = []
    turn = offset % len(rules) if rules else 0
    for rule in (*rules[turn:], *rules[:turn]):
        if len(out) >= budget:
            log.append(f"relation {rule.__name__} not tried: budget of {budget} spent")
            continue
        made = None
        for anchor in anchors:
            derivation = rule(anchor.panels[0].view, ctx)
            if derivation is None:
                continue
            kind = "overlay" if derivation.layout == "overlay" else "panel"
            spec = _figure(f"f{start + len(out):02d}", schema, derivation.panels,
                           source=Source(kind, anchor_figure_id=anchor.figure_id),
                           layout=derivation.layout, sharing=derivation.sharing,
                           relation=derivation.relation)
            if batch.admit(spec, density=ctx.density):
                made = spec
                break
        if made is None:
            log.append(f"relation {rule.__name__} produced nothing from "
                       f"{[a.figure_id for a in anchors]}")
        else:
            out.append(made)
    return out, log


# ---------------------------------------------------------------- several on one page

def _onto_a_page(derivation, anchor: FigureSpec, schema: TableSchema, *,
                 page_id: str, start: int) -> list[FigureSpec] | None:
    """One relation's panels, laid out as separate figures on one page.

    A relation puts a second view somewhere. Two of the three somewheres are the same
    plotting area and another plotting area on the same image; this is the third. The
    export has to keep the members apart: they carry the same category names, and only
    what is drawn on each of them says which is which.

    Where the panel titles named the panels, that name becomes the figure's subtitle
    and the first segment of every key under it, read off the figure's own heading --
    nothing else in a separate image says which half it holds. Where the panels differ
    by measure or by key already, no prefix is added: a segment that repeats what the
    key says is a segment with nothing in it.
    """
    if derivation.layout == "overlay":
        return None
    if any(len(panel.views) != 1 for panel in derivation.panels):
        return None
    # Whether the members need naming apart is a fact about their keys, not about the
    # relation. Two panels of the same categories under two windows carry identical
    # keys, and split into separate images nothing is left to join them by; two panels
    # grouped by different columns already differ, and a segment repeating what the
    # key says is a segment with nothing in it.
    every = [panel.view.keys for panel in derivation.panels]
    collide = any(a & b for i, a in enumerate(every) for b in every[i + 1:])
    out: list[FigureSpec] = []
    for i, panel in enumerate(derivation.panels):
        named = panel.view
        titles = [b for b in panel.texts if b.role == "title"]
        texts: tuple[TextBlock, ...] = ()
        if titles:
            texts = (TextBlock("subtitle", titles[0].text, "figure", "above"),)
        if collide:
            # The name has to be on this image and nowhere else on it. A panel title
            # is one; without one there is nothing to read the segment off, and the
            # page is not made rather than made unjoinable.
            if not titles:
                return None
            named = replace(named, key_prefix=(titles[0].text,),
                            prefix_source=("heading",))
        out.append(replace(
            _figure(f"f{start + i:02d}", schema, (PanelSpec("p0", (named,)),),
                    source=Source("page", anchor_figure_id=anchor.figure_id),
                    relation=derivation.relation, page_id=page_id),
            texts=texts))
    return out


def page_figures(anchors: Sequence[FigureSpec], ctx: Context, batch: Batch,
                 schema: TableSchema, start: int, *, rules: Sequence[PanelRule],
                 budget: int, offset: int = 0,
                 room: int = 99) -> tuple[list[FigureSpec], list[str]]:
    """Pages, one relation each, from the first anchor that supports it.

    Shaped like `derived_figures` and rotated the same way, so a budget shorter than
    the list still reaches every relation across a batch. A page is admitted or
    dropped whole: half a page is a figure whose partner says what it is.
    """
    out: list[FigureSpec] = []
    log: list[str] = []
    pages = 0
    turn = offset % len(rules) if rules else 0
    for rule in (*rules[turn:], *rules[:turn]):
        if pages >= budget:
            log.append(f"page from {rule.__name__} not tried: budget of {budget} spent")
            continue
        made: list[FigureSpec] | None = None
        for anchor in anchors:
            derivation = rule(anchor.panels[0].view, ctx)
            if derivation is None:
                continue
            start_here = start + len(out)
            members = _onto_a_page(derivation, anchor, schema,
                                   page_id=f"pg{start_here:02d}", start=start_here)
            if members is None or len(members) < 2 or len(out) + len(members) > room:
                continue
            if all(batch.admit(spec, density=ctx.density) for spec in members):
                made = members
                break
        if made is None:
            log.append(f"page from {rule.__name__} produced nothing from "
                       f"{[a.figure_id for a in anchors]}")
            continue
        out += made
        pages += 1
    return out, log


# ---------------------------------------------------------------- sampled

def draw_binding(slot, schema: TableSchema, rng: np.random.Generator, *,
                 max_tier: int, density: DensityBand,
                 seen: Sequence[str] = ()) -> Binding | None:
    """One candidate from a family: a type, some columns and an aggregate, drawn and
    then validated. Nothing is enumerated -- the candidate space of a wide schema runs
    to thousands, and every one of them would have to be projected to be judged.

    Types the batch does not hold yet are drawn from first, for the same reason the
    families are: this is the path that exists to widen coverage, and a family with
    four types in it would otherwise keep offering whichever one it happened to hit.
    """
    from ..registry.charts import familyless, in_family

    types = [c for c in (familyless() if slot is None else in_family(slot))
             if c.tier <= max_tier]
    fresh = [c for c in types if c.name not in set(seen)]
    types = fresh or types
    if not types:
        return None
    spec = types[int(rng.integers(len(types)))]

    # The semantic conditions narrow the pool before the draw rather than after it.
    # They read declarations only, so consulting them here costs nothing and stops
    # the sampler spending its attempts on candidates the condition table is certain
    # to reject -- a process chart drawn over a column that is not a sequence of
    # stages was never going to pass.
    cats = [c.name for c in schema.categories
            if not spec.require_stage or c.ordered == "stage"]
    times = [c.name for c in schema.times]
    measures = [c.name for c in schema.measures
                if not spec.require_additive or c.additive]
    n_cat = int(rng.integers(spec.n_cat[0], (spec.n_cat[1] or spec.n_cat[0]) + 1))
    if n_cat > len(cats) or (spec.n_time[0] and not times):
        return None
    dims = tuple(rng.choice(cats, size=n_cat, replace=False)) if n_cat else ()
    time = str(rng.choice(times)) if spec.n_time[1] and times and (
        spec.n_time[0] or rng.integers(2)) else None

    n_m = int(rng.integers(spec.n_measure[0], (spec.n_measure[1] or spec.n_measure[0]) + 1))
    if n_m > len(measures):
        return None
    ms = tuple(str(m) for m in rng.choice(measures, size=n_m, replace=False)) if n_m else ()
    binding = Binding(spec.name, dims=tuple(str(d) for d in dims), time=time, measures=ms,
                      aggregate=_aggregate(spec, ms, schema, rng),
                      resample=str(rng.choice(RESAMPLE)) if time else None)
    return binding if check(binding, schema, density=density) else None


def _aggregate(spec, measures: Sequence[str], schema: TableSchema,
               rng: np.random.Generator) -> str:
    """An aggregate the shape accepts and the measure allows.

    Which aggregates a measure allows is a declared field, so the draw is made from
    the legal set instead of from all of them and then thrown away.
    """
    allowed = list(SHAPE_AGGREGATES[spec.shape])
    if spec.shape != "grouped_scalar":
        return str(rng.choice(allowed))
    if not measures:
        return "COUNT"
    legal = set(AGG_ADDITIVE if schema.column(measures[0]).additive else AGG_NON_ADDITIVE)
    pool = [a for a in allowed if a in legal] or allowed
    return str(rng.choice(pool))


def rotation_figures(ctx: Context, batch: Batch, schema: TableSchema, rng: np.random.Generator,
                     *, start: int, budget: int, tries: int, weights: sampling.Weights,
                     seen: Sequence, types_seen: Sequence[str] = ()
                     ) -> tuple[list[FigureSpec], list[str]]:
    """Draw, validate, project, admit or draw again -- family by family, filling the
    ones the batch does not have yet, until the budget is spent or a whole round
    accepts nothing."""
    out: list[FigureSpec] = []
    log: list[str] = []
    families = list(seen)
    drawn: list[str] = list(types_seen)
    slots = sampling.slots(ctx.max_tier)

    while len(out) < budget:
        accepted_this_round = False
        for slot in sampling.rotation_order(slots, families, rng, weights):
            if len(out) >= budget:
                break
            made = None
            # What each attempt drew and where it died. A family that yields nothing
            # says nothing about which type was missed: a run can end with a declared
            # type drawn zero times, and "family process yielded nothing" does not
            # distinguish "no funnel was ever drawn" from "eight funnels were drawn
            # and every one was turned away".
            tried: Counter = Counter()
            for _ in range(tries):
                binding = draw_binding(slot, schema, rng, max_tier=ctx.max_tier,
                                       density=ctx.density, seen=drawn)
                if binding is None:
                    ctx.rejected["drawn illegal"] += 1
                    tried["(illegal)"] += 1
                    continue
                view = ctx.build(binding)
                if view is None:
                    tried[f"{binding.chart_type}: data"] += 1
                    continue
                spec = _figure(f"f{start + len(out):02d}", schema,
                               (PanelSpec("p0", (view,)),), source=Source("rotation"))
                if batch.admit(spec, density=ctx.density):
                    made = spec
                    break
                tried[f"{binding.chart_type}: redundant"] += 1
            if made is None:
                detail = ", ".join(f"{what} x{n}" for what, n in sorted(tried.items()))
                log.append(f"family {slot or 'family-less'} yielded nothing in "
                           f"{tries} draws ({detail})")
                continue
            out.append(made)
            families.append(slot)
            drawn += made.chart_types
            accepted_this_round = True
        if not accepted_this_round:
            break
    return out, log


# ---------------------------------------------------------------- the stage

def compose(table: FactTable, schema: TableSchema, seed: int, config: Config,
            *, llm=None) -> list[FigureSpec]:
    """The whole of view selection: build, derive, sample, then name."""
    figures, _ = compose_with_log(table, schema, seed, config, llm=llm)
    return figures


def compose_with_log(table: FactTable, schema: TableSchema, seed: int, config: Config,
                     *, llm=None) -> tuple[list[FigureSpec], dict]:
    """The figures, and what happened while choosing them.

    How many figures a scenario yields is a result, not a setting: the budget is an
    upper bound, the redundancy rule and the draw limit decide the rest. So the
    counts go in the log, per scenario.
    """
    density = _density(config, schema)
    ctx = Context(table.df, schema, seed=seed, density=density,
                  max_tier=int(config.get("scale.max_tier", 3)),
                  max_panels=int(config.get("figure.max_panels", 4)))
    batch = Batch()
    rng = derive(seed, schema.scenario_id, STAGE)
    weights = sampling.load(config.get("figure.family_weights"))

    built, log_built = intent_figures(ctx, batch, schema)
    # Where each list of relations starts is a property of the scenario id, not of the
    # seed: a derived figure is computed from its anchor, and only the rotation is
    # allowed to move when the seed does. Over a batch of scenarios every relation
    # comes up, which a fixed order and a budget shorter than the list never allow.
    turn = seed_of(0, schema.scenario_id, "s02_relations")
    panelled, log_panel = derived_figures(
        built, ctx, batch, schema, start=1 + len(built), rules=PANEL_RELATIONS,
        budget=int(config.get("figure.max_derived", 3)), offset=turn)
    overlaid, log_overlay = derived_figures(
        built, ctx, batch, schema, start=1 + len(built) + len(panelled),
        rules=OVERLAY_RELATIONS, budget=int(config.get("figure.max_overlays", 2)),
        offset=turn)
    derived = panelled + overlaid
    log_derived = log_panel + log_overlay

    figures = built + derived
    # A page's relations start where the panels' left off, so a scenario spends its
    # page on a relation its panels did not already take.
    paired, log_pages = page_figures(
        built, ctx, batch, schema, 1 + len(figures), rules=PAGE_RELATIONS,
        budget=int(config.get("figure.pages", 1)),
        offset=turn + int(config.get("figure.max_derived", 3)),
        room=max(0, int(config.get("figure.k_max", 12)) - len(figures)))
    figures += paired

    budget = max(0, int(config.get("figure.k_max", 12)) - len(figures))
    sampled, log_rotation = rotation_figures(
        ctx, batch, schema, rng, start=1 + len(figures), budget=budget,
        tries=int(config.get("figure.sample_tries", 8)), weights=weights,
        seen=[f for s in figures for f in s.families],
        types_seen=[t for s in figures for t in s.chart_types])
    figures += sampled

    words = llm if llm is not None else title.default_llm(config)
    written: list[str] = []
    figures = caption.attach(
        title.write(figures, schema, llm=words, report=written), schema)
    log = {
        "density_band": density.name,
        "titles": written,
        "family_weights": weights.to_dict(),
        "counts": {"intent": len(built), "panel": len(panelled), "overlay": len(overlaid),
                   "page": len(paired), "rotation": len(sampled),
                   "total": len(figures)},
        "chart_types": sorted({t for s in figures for t in s.chart_types}),
        "families": sorted({f for s in figures for f in s.families}),
        "layout": _layout_counts(figures),
        "rejected": {**ctx.rejected, **batch.counts()},
        "skipped": log_built + log_derived + log_rotation,
    }
    return figures, log


def _layout_counts(figures: Sequence[FigureSpec]) -> dict[str, int]:
    """How many figures can carry a legend-binding target at all.

    On a single-panel figure a legend entry governs that one panel and says nothing,
    so the share of figures with a legend covering several panels is the share of the
    batch that target can come from.
    """
    multi = [f for f in figures if len(f.panels) > 1]
    shared = [f for f in multi if f.sharing.share_legend and f.sharing.series_column]
    return {"figures": len(figures), "multi_panel": len(multi),
            "shared_legend": len(shared),
            "one_plotting_area_two_views": sum(1 for f in figures if f.layout == "overlay"),
            "on_a_shared_page": len({f.page_id for f in figures if f.page_id})}


def _density(config: Config, schema: TableSchema) -> DensityBand:
    """The density the batch is drawn at, lowered to what the table can support.

    A band that asks for more marks than the table has rows spreads the long tail
    to one row a cell, and the structural check cannot see that -- so the band comes
    down rather than the per-cell floor going up.
    """
    wanted = band(config.get("figure.density_band"))
    supported = band_for_rows(schema.n_rows)
    rank = {b.name: i for i, b in enumerate(DENSITY_BANDS)}
    return wanted if rank[wanted.name] <= rank[supported.name] else supported
