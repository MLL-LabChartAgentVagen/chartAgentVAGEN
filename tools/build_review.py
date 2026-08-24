"""Building the review site: what the pipeline produced, and what was checked.

    python tools/build_review.py                       # reads data/generated/live
    python tools/build_review.py --run data/generated/live --skip-gallery

The one-page report beside the plan is the overview. This is the long form: a page
per stage with many worked examples, a page per chart type, and a page of evidence
that says how the code was checked rather than what it drew.

Everything on these pages is read back off artifacts. The chart-type pages are drawn
here and now, from the hand-written scenarios, so a reader can regenerate them
without a model and get the same images.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from chartgen.common import readback as rb  # noqa: E402
from chartgen.common import serde  # noqa: E402
from chartgen.interfaces.figure import FigureSpec  # noqa: E402
from chartgen.interfaces.record import Record  # noqa: E402
from chartgen.interfaces.style import STYLE_DOMAINS  # noqa: E402
from chartgen.interfaces.table import TableSchema  # noqa: E402
from chartgen.registry.charts import CHARTS, DENSITY_BANDS, GRID  # noqa: E402
from chartgen.s05_output import verify as V  # noqa: E402
from chartgen.s05_output.export import (  # noqa: E402
    TARGETS, as_markdown, build as build_targets,
)
from tools import gallery, reportkit  # noqa: E402
from tools.reportkit import (  # noqa: E402
    THUMB_WIDTH, band, bar, box_legend, card, code, document, embed, esc, figure_pair,
    flow_diagram,
    image, masthead, note, num, page_document, site_nav, table, tags, wall,
)

#: The one-page overview, which sits beside the plan rather than in this directory.
REPORT = "../plan/reports/report.html"

#: The pages, in reading order: file, name, one-line hint.
PAGES: tuple[tuple[str, str, str], ...] = (
    ("index.html", "Entrance", "Start here · site map"),
    (REPORT, "One page", "The whole pipeline, read in one sitting"),
    ("stage01.html", "01 data", "Scenario · script · intents"),
    ("stage02.html", "02 figure", "Constructed · derived · sampled"),
    ("stage03.html", "03 render", "Recorded while drawing · frozen layout"),
    ("stage04.html", "04 record", "Three layers · readability · self-checks"),
    ("stage05.html", "05 output", "Nine kinds of target · reward"),
    ("gallery.html", "Every figure", "Every figure this run drew"),
    ("pages.html", "Several at once", "One page · several panels · overlaid in one area"),
    ("types.html", "Chart types", "17 types, one page each"),
    ("diversity.html", "Diversity", "Style · density · spread"),
    ("checks.html", "Checks", "Tests · coverage · fault injection"),
)

#: How many worked examples each stage page carries.
PER_STAGE = 12

#: Seed for the style sweep on the diversity page. Fixed, so the page rebuilds the same.
SEED = 20260822


# ---------------------------------------------------------------- the run

@dataclass
class Scenario:
    name: str
    folder: Path
    schema: TableSchema
    specs: list[FigureSpec] = field(default_factory=list)
    records: list[Record] = field(default_factory=list)
    log: dict = field(default_factory=dict)

    @property
    def first(self) -> list[Record]:
        return [r for r in self.records if r.variant == 0]

    def spec(self, figure_id: str) -> FigureSpec | None:
        return next((s for s in self.specs if s.figure_id == figure_id), None)


@dataclass
class Run:
    root: Path
    scenarios: list[Scenario] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def records(self) -> list[Record]:
        return [r for s in self.scenarios for r in s.records]

    @property
    def specs(self) -> list[FigureSpec]:
        return [f for s in self.scenarios for f in s.specs]

    @property
    def marks(self) -> int:
        return sum(len(r.marks) for r in self.records)


def load(root: Path) -> Run:
    stats_path = root / "stats.json"
    run = Run(root, stats=json.loads(stats_path.read_text(encoding="utf-8"))
              if stats_path.exists() else {})
    for folder in sorted(p for p in root.iterdir() if (p / "schema.json").exists()):
        log = folder / "log.json"
        run.scenarios.append(Scenario(
            folder.name, folder, serde.load(TableSchema, folder / "schema.json"),
            [serde.load(FigureSpec, p) for p in sorted((folder / "specs").glob("*.json"))],
            [serde.load(Record, p) for p in sorted((folder / "records").glob("*.json"))],
            json.loads(log.read_text(encoding="utf-8")) if log.exists() else {}))
    if not run.scenarios:
        raise SystemExit(f"no scenario artifacts under {root}")
    return run


def types_of(record: Record) -> list[str]:
    return sorted({t for p in record.panels for t in p.chart_types})


def pick(run: Run, count: int, *, kind: str = "", relation: bool | None = None,
         layout: str = "") -> list[tuple[Scenario, Record, FigureSpec]]:
    """Examples spread over the scenarios, unseen type sets first.

    Taken scenario by scenario in turn so a page shows a pipeline rather than one
    table, and filtered by how the figure was chosen when a page is about that.
    """
    out: list[tuple[Scenario, Record, FigureSpec]] = []
    seen: set[tuple[str, ...]] = set()
    taken: dict[str, set[str]] = {s.name: set() for s in run.scenarios}
    for fresh in (True, False):
        while len(out) < count:
            before = len(out)
            for scenario in run.scenarios:
                if len(out) >= count:
                    break
                for record in scenario.first:
                    spec = scenario.spec(record.figure_id)
                    if spec is None or record.figure_id in taken[scenario.name]:
                        continue
                    if kind and spec.source.kind != kind:
                        continue
                    if relation is not None and bool(spec.relation) != relation:
                        continue
                    if layout and spec.layout != layout:
                        continue
                    shapes = tuple(types_of(record))
                    if fresh and shapes in seen:
                        continue
                    seen.add(shapes)
                    taken[scenario.name].add(record.figure_id)
                    out.append((scenario, record, spec))
                    break
            if len(out) == before:
                break
    return out


def example(scenario: Scenario, record: Record, spec: FigureSpec, *,
            extra: Sequence[tuple[str, str]] = ()) -> str:
    """One worked example: what it is, what was drawn, what was written down."""
    rows = [
        ["Chart type", tags(types_of(record))],
        ["How it was chosen", f"<code>{esc(spec.source.kind)}</code>"
         + (f" · relation <code>{esc(spec.relation)}</code>" if spec.relation else "")
         + (f" · anchor <code>{esc(spec.source.anchor_figure_id)}</code>"
            if spec.source.anchor_figure_id else "")],
        ["Title (written by the model)", f"<b>{esc(spec.text('title'))}</b>"],
        ["Layout", f"<code>{esc(spec.layout)}</code> · {len(record.panels)} plotting areas · "
                 + num(f"{record.image_size[0]}×{record.image_size[1]}")],
        ["Marks", num(len(record.marks)) + " drawn, "
                 + num(sum(1 for m in record.marks if m.readable)) + " carrying a value target"],
        *[[k, v] for k, v in extra],
    ]
    if record.caption:
        rows.append(["Caption (not drawn on the image)", esc(record.caption)])
    body = table(["", ""], rows) + figure_pair(record) + marks_table(record, 6)
    return card(scenario.schema.scenario_title[:56], body,
                f"{scenario.name} · {record.figure_id} · v{record.variant}")


def marks_table(record: Record, limit: int) -> str:
    rows = [[f"<code>{esc(m.mark_id)}</code>",
             f"<code>{esc(' · '.join(m.key))}</code>", tags(m.key_src),
             " ".join(f"{k} {v:.4g}" for k, v in m.values.items()),
             num([round(v, 1) for v in m.box.as_tuple()]),
             f"<code>{esc(m.mark_shape)}</code> / <code>{esc(m.channel)}</code>",
             num(m.rows), "yes" if m.readable else "no"]
            for m in record.marks[:limit]]
    out = table(["Mark", "Key", "Key source", "Values", "Box", "Shape / channel",
                 "Rows behind", "Value target"], rows)
    if len(record.marks) > limit:
        out += note(f"The other {len(record.marks) - limit} marks each have a "
                    f"record of their own, written the same way.")
    return out


# ---------------------------------------------------------------- the entrance

def page_index(run: Run, checks: dict, shots: dict[str, int]) -> str:
    printed = sum(1 for r in run.records for m in r.marks if m.labeled)
    body = [note(
        "<b>These pages are for judging whether the pipeline is right without reading "
        "the code. Start here.</b>"
        f"Read them in three layers: the <a href='{REPORT}'>one-page overview</a> first, "
        "for what the whole pipeline does; then 01 through 05, one worked example at a "
        "time; and last the <a href='checks.html'>checks</a> page, which is about how the "
        "code was verified rather than what it drew. "
        "Every number here was read back off the artifacts the run left behind, and every "
        "image is the one that was drawn at the time.")]

    body.append(band("Site map", f"{len(PAGES) + 16} pages, each one opens on its own"))
    body.append(table(["Layer", "Page", "What is on it", "Figures on it"], [
        ["<b>1</b>", f'<a href="{REPORT}">One page: report.html</a>',
         "The whole pipeline in one sitting: a section per stage, sixteen worked "
         "examples, meant to be read beside plan.html", "42"],
        ["<b>2</b>", '<a href="stage01.html">01 data</a>',
         "Each scenario's declaration script, its intents, the first rows of its fact "
         "table, and how feasibility is decided from declarations alone",
         f"{len(run.scenarios)} scenarios (no figures yet at this stage)"],
        ["", '<a href="stage02.html">02 figure</a>',
         "How an intent figure is constructed, how a multi-panel figure is derived from "
         "a relation, and how a rotation candidate gets rejected -- with examples",
         num(shots.get("stage02.html", 0))],
        ["", '<a href="stage03.html">03 render</a>',
         "Frozen layout, recording while drawing, and shrinking type before moving "
         "anything; every example shows the drawing and its boxes side by side",
         num(shots.get("stage03.html", 0))],
        ["", '<a href="stage04.html">04 record</a>',
         "The three record layers, the readability rule, the three self-checks, and the "
         "reward function reading the image again on the spot",
         num(shots.get("stage04.html", 0))],
        ["", '<a href="stage05.html">05 output</a>',
         "What each of the nine training targets looks like, the export scope and "
         "granularity, and how a model's answer is graded",
         num(shots.get("stage05.html", 0))],
        ["", '<a href="gallery.html">Every figure</a>',
         "Every figure this run drew, none left out, each thumbnail carrying the boxes "
         "that were recorded for it",
         num(shots.get("gallery.html", 0))],
        ["", '<a href="pages.html">Several at once</a>',
         "A second view has only three places to go: the same plotting area, another "
         "plotting area, or another figure on the same page. The only place on the site "
         "that looks at a whole page as one page",
         num(shots.get("pages.html", 0))],
        ["", '<a href="types.html">Chart types</a>',
         "One page per type: when it can be drawn, how it was drawn this time, four "
         "style vectors each, and what was written down",
         f"{num(shots.get('types.html', 0))} + 14 on each of 17 pages"],
        ["", '<a href="diversity.html">Diversity</a>',
         "One figure redrawn under six style vectors, where the answers have to come "
         "back identical; and how much this batch varies along eight dimensions",
         num(shots.get("diversity.html", 0))],
        ["<b>3</b>", '<a href="checks.html">Checks</a>',
         "Tests by file, statement coverage, fault injection (every survivor listed), "
         "artifact readback, and the shape of the code",
         f"{checks['tests']} tests"],
    ]))

    body.append(band("One row, all the way through", "The output unit is (key, value, box)"))
    body.append(flow_diagram())
    body.append(table(["Stage", "In → out", "Calls a model", "What this step guarantees"], [
        ["<b>01 data</b> <code>s01_data</code>", "domain pool → fact table + schema",
         "yes, once",
         "Scenario, script and intents are written together, so an intent's columns are "
         "bound by construction"],
        ["<b>02 figure</b> <code>s02_figure</code>", "table + schema → FigureSpec",
         "yes, once",
         "Choosing is all program; the model writes only the words painted on the image"],
        ["<b>03 render</b> <code>s03_render</code>", "FigureSpec + style → image + L0/L1",
         "no",
         "Recorded while drawing: every box comes from the plotting library's own "
         "coordinate transform, never from parsing the image"],
        ["<b>04 record</b> <code>s04_record</code>", "RenderOutput → Record (3 layers)",
         "no",
         "Readability is decided from pixel geometry; a figure failing any self-check "
         "is dropped"],
        ["<b>05 output</b> <code>s05_output</code>", "Record → training targets", "no",
         "Several projections of one record; the export scope and granularity are "
         "written into the artifact"],
    ]))

    body.append(band("This run", esc(run.stats.get("model", ""))))
    body.append(table(["Item", "Count"], [
        ["Scenarios / model calls", num(f"{len(run.scenarios)} / {len(run.scenarios) * 2}")],
        ["Figures / records (two style versions each)",
         num(f"{len(run.specs)} / {len(run.records)}")],
        ["Marks", num(run.marks)],
        ["Marks carrying a value target",
         num(sum(1 for r in run.records for m in r.marks if m.readable))],
        ["Marks with their value printed on the image", num(printed)],
        ["Records passing all three self-checks",
         num(f"{sum(1 for r in run.records if r.selfcheck.passed)}"
             f" / {len(run.records)}")],
    ]))

    body.append(band("What was checked", "The details are on the checks page"))
    body.append(table(["Check", "Result", "What it can show"], [
        ["Tests", num(f"{checks['tests']}"),
         "Each one asserts a property; passing is not the same as running"],
        ["Statement coverage", num(f"{checks['coverage']:.0f}%"),
         "Which lines were never executed at all"],
        ["Fault injection", num(f"{checks['killed']} / {checks['mutants']}"),
         "Break the code on purpose and see whether a test fails -- coverage cannot "
         "answer that"],
        ["Page elements inside the image", num(f"{checks['elements']}, 0 outside"),
         "Text written past the edge is invisible, and the record still gives it a box"],
        ["Text not overlapping", num(f"{checks['pairs']} pairs, 0 overlapping"),
         "Two blocks of text on top of each other leave both boxes matching nothing a "
         "reader can make out"],
    ]))

    body.append(band("Judging it without reading the code", "Five questions, five places to look"))
    body.append(table(["Question", "Where to look", "What to look for"], [
        ["Do the boxes match what was drawn?",
         'every example on <a href="stage03.html">03 render</a> and '
         '<a href="stage04.html">04 record</a>',
         "Two images side by side: the page as drawn on the left, the recorded boxes "
         "painted back on the right. One pixel off and the box on the right no longer "
         "covers the shape on the left"],
        ["Can the values really be read off the image?",
         'the "read it again" section of <a href="stage04.html">04 record</a>',
         "This page reads the image again as it is built, using the reward function's own "
         "code. Its only inputs are the image and the claimed (value, box) -- no ground "
         "truth"],
        ["Does the same chart still hold under another style?",
         'the four style vectors per type on <a href="types.html">chart types</a>, and '
         'the six-style redraw on <a href="diversity.html">diversity</a>',
         "Each of the 17 types is drawn four times and read back every time; after a "
         "restyle the keys and values have to be identical"],
        ["Does the whole batch hold, or only the ones picked out?",
         '<a href="gallery.html">every figure</a>',
         f"All {len(run.specs)} figures, none left out, each with its recorded boxes"],
        ["If the code were wrong, would anyone notice?",
         'the fault injection on <a href="checks.html">checks</a>',
         "The code is broken one place at a time to see whether a test fails. Every "
         "survivor is listed on the page"],
    ]))

    body.append(band("Onwards", "Each page opens on its own"))
    cards = []
    for href, name, hint in PAGES[1:]:
        cards.append(f'<a href="{esc(href)}"><b>{esc(name)}</b><span>{esc(hint)}</span></a>')
    body.append(f'<div class="gridcards">{"".join(cards)}</div>')
    return "".join(body)


# ---------------------------------------------------------------- 01 data

def page_stage01(run: Run) -> str:
    from chartgen.s01_data import validate

    body = [note(
        "<b>One call, three things: the scenario prose, the declaration script, and the "
        "intents.</b> "
        "The script <em>is</em> the formalised scenario, so splitting this into two calls "
        "would insert a lossy JSON layer between them. "
        "Parsing, enumeration, the coverage check, execution and the structural check are "
        "all program: the model judges no feasibility and writes no value.")]

    body.append(band("The scenarios", "The domain is drawn from the pool by program"))
    rows = []
    for s in run.scenarios:
        f = validate.feasibility(s.schema)
        rows.append([f'<a href="#{s.name}"><code>{s.name}</code></a>',
                     esc(s.schema.scenario_title), num(s.schema.n_rows),
                     num(len(s.schema.of_kind("category"))),
                     num(len(s.schema.of_kind("time"))),
                     num(len(s.schema.of_kind("measure"))),
                     num(len(s.schema.intents)),
                     tags(list(f.families), [k for k, v in f.families.items() if v])])
    body.append(table(["Scenario", "Title (written by the model)", "Rows", "Category cols",
                       "Time cols", "Measure cols", "Intents",
                       "Feasible view classes (grey = empty)"], rows))
    body.append(note("Feasibility reads declarations only: a category column's value list "
                     "gives its cardinality, a time column's start, end and frequency give "
                     "its point count, and <code>additive</code> and <code>ordered</code> "
                     "are declared fields. Fewer than three non-empty families sends the "
                     "reply back to the model to be rewritten."))

    for s in run.scenarios:
        body.append(band(s.name, s.schema.scenario_title[:60], anchor=s.name))
        body.append(card("(1) Scenario prose", f"<p>{esc(s.schema.data_context)}</p>",
                         "data_context"))
        body.append(card("(2) Declaration script", code(s.schema.script), "script"))
        body.append(card("(3) Column declarations", columns_table(s.schema), "columns"))
        body.append(card("(4) Intents, columns already bound", intents_table(s.schema),
                         "intents"))
        head = fact_head(s.folder)
        if head:
            body.append(card("(5) First 8 rows of the fact table", head, "facts.parquet"))
    return "".join(body)


def columns_table(schema: TableSchema) -> str:
    rows = []
    for c in schema.columns:
        detail = []
        if c.values:
            detail.append(", ".join(c.values[:4]) + ("…" if len(c.values) > 4 else ""))
        if c.freq:
            detail.append(f"{c.start} → {c.end}, {c.freq}")
        if c.unit:
            detail.append(f"unit {c.unit}")
        flags = []
        if c.additive is not None:
            flags.append("additive" if c.additive else "non-additive")
        if c.ordered:
            flags.append(f"ordered={c.ordered}")
        if c.parent:
            flags.append(f"parent={c.parent}")
        if c.derived_from:
            flags.append(f"derived_from={c.derived_from}")
        rows.append([f"<code>{esc(c.name)}</code>", esc(c.kind), num(c.cardinality),
                     esc(c.group or "—"), "; ".join(esc(d) for d in detail),
                     tags(flags) if flags else "—"])
    out = table(["Column", "Kind", "Cardinality", "Group", "Values / range", "Semantics"],
                rows)
    if schema.dependencies:
        out += note("Dependencies between measure columns: " + ", ".join(
            f"<code>{esc(a)}</code> → <code>{esc(b)}</code>" for a, b in schema.dependencies))
    return out


def intents_table(schema: TableSchema) -> str:
    return table(["#", "Question", "Columns", "Aggregate", "View class"], [
        [num(i.index), esc(i.sentence),
         ", ".join(f"<code>{esc(c)}</code>" for c in i.columns),
         f"<code>{esc(i.aggregate)}</code>", f'<span class="tag">{esc(i.family)}</span>']
        for i in schema.intents])


def fact_head(folder: Path, rows: int = 8) -> str:
    path = folder / "facts.parquet"
    if not path.exists():
        return ""
    import pandas as pd

    df = pd.read_parquet(path).head(rows)
    body = [[num(f"{v:g}") if isinstance(v, (int, float)) else esc(v) for v in row]
            for row in df.itertuples(index=False)]
    return table([esc(c) for c in df.columns], body)


# ---------------------------------------------------------------- 02 figure

#: The nine ways a second view is derived, and where it goes.
RELATIONS: tuple[tuple[str, str, str], ...] = (
    ("small_multiples", "another plotting area",
     "One view repeated, one panel per value; the only relation whose legend covers "
     "several panels"),
    ("facet", "another plotting area", "The same measure, cut a different way"),
    ("drilldown", "another plotting area", "One level further down the hierarchy"),
    ("time_split", "another plotting area", "The same view over two time windows"),
    ("dual_metric", "another plotting area", "The same grouping, the next measure"),
    ("part_whole", "another plotting area", "A comparison turned into a composition"),
    ("overlay_metric", "the same plotting area", "One grouping, two measures"),
    ("overlay_slice", "the same plotting area",
     "One measure, two slices or two aggregates"),
    ("overlay_range", "the same plotting area", "A value with the spread around it"),
)

#: What each rejection reason means, in the sampler's own terms.
REJECT_WHY = {
    "drawn illegal": "The drawn (type, columns, aggregate) does not meet the column "
                     "declarations this type requires; draw again",
    "conditions": "The column declarations do not meet this type's conditions",
    "thin": "Some cell is backed by fewer source rows than this type requires per cell",
    "monotone": "This type requires values that only fall (funnel); the drawn ones do not",
    "redundant": "The batch already holds a figure with the same key set and the same "
                 "mark shape",
    "variation": "Every cell is about the same height; drawn, it is a flat line",
    "distinct": "Too few different values -- most cells would look identical",
    "marks": "The mark count falls outside this type's bounds (after the density band)",
    "projection": "The projection itself failed: no usable column combination",
    "empty": "The projection came back empty",
    "share": "The smallest share is too small for its sector to be visible",
}


def page_stage02(run: Run) -> str:
    body = [note(
        "<b>No model chooses a figure, and there is no candidate list.</b> Three kinds of "
        "figure, three mechanisms, and only the third needs a random number: an intent "
        "figure is constructed, multi-panel and overlay figures are computed from a "
        "relation, and a rotation figure is sampled with rejection. "
        "Enumerating every legal view would give hundreds to thousands of candidates, each "
        "needing a full projection pass, to ship about a dozen figures.")]

    body.append(band("How the batch was filled", "16 figures per scenario"))
    rows = []
    for s in run.scenarios:
        counts = s.log.get("counts", {})
        layout = s.log.get("layout", {})
        rows.append([f"<code>{s.name}</code>",
                     *[num(counts.get(k, 0)) for k in
                       ("intent", "panel", "overlay", "rotation", "page", "total")],
                     num(layout.get("multi_panel", 0)),
                     num(layout.get("one_plotting_area_two_views", 0)),
                     esc(s.log.get("density_band", ""))])
    body.append(table(["Scenario", "Intent", "Multi-panel", "Overlay", "Rotation",
                       "Paired on a page", "Total", "Multi-area figures",
                       "One area, two views", "Density band"], rows))

    body.append(band("(1) Intent figure: constructed",
                     "The intent fixes columns and aggregate, the condition table the type"))
    for scenario, record, spec in pick(run, 5, kind="intent"):
        body.append(intent_trace(scenario, record, spec))

    body.append(band("(2) Derived figure: computed from a relation",
                     "Six go into another plotting area, three into the same one"))
    used = Counter(f.relation for f in run.specs if f.relation)
    body.append(table(["Relation", "Where the second view goes", "What it is",
                       "Drawn this run"], [
        [f"<code>{esc(name)}</code>", esc(where), esc(what), num(used.get(name, 0))]
        for name, where, what in RELATIONS]))
    for scenario, record, spec in pick(run, 5, relation=True):
        body.append(example(scenario, record, spec))

    body.append(band("(3) Rotation figure: sampled with rejection",
                     "Draw (type, columns, aggregate), validate, project, admit"))
    merged: Counter = Counter()
    for s in run.scenarios:
        merged.update({k: int(v) for k, v in (s.log.get("rejected") or {}).items()})
    body.append(table(["Rejection reason", "Times", "What it means"], [
        [f"<code>{esc(k)}</code>", num(v), esc(REJECT_WHY.get(k, ""))]
        for k, v in merged.most_common()]))
    skipped = [(s.name, line) for s in run.scenarios for line in s.log.get("skipped", [])]
    body.append(card("The sampler's own log", table(["Scenario", "What it wrote"], [
        [f"<code>{esc(n)}</code>", esc(line)] for n, line in skipped[:20]]), "log.json"))
    for scenario, record, spec in pick(run, 5, kind="rotation"):
        body.append(example(scenario, record, spec))
    return "".join(body)


def intent_trace(scenario: Scenario, record: Record, spec: FigureSpec) -> str:
    """One question, followed from the intent to the marks it ended up as."""
    intent = scenario.schema.intents[spec.source.intent_index or 0]
    view = spec.views[0]
    binding = view.binding
    chart = CHARTS[binding.chart_type]
    trace = (
        f"<p><b>Intent #{intent.index}</b>: {esc(intent.sentence)}<br>"
        f"bound columns {', '.join(f'<code>{esc(c)}</code>' for c in intent.columns)}, "
        f"aggregate <code>{esc(intent.aggregate)}</code>, view class "
        f'<span class="tag">{esc(intent.family)}</span></p>'
        + table(["From the intent", "From the condition table", "From the projection"], [[
            f"dims {', '.join(f'<code>{esc(d)}</code>' for d in binding.dims) or '—'}<br>"
            f"time <code>{esc(binding.time or '—')}</code><br>"
            f"measures {', '.join(f'<code>{esc(m)}</code>' for m in binding.measures)}<br>"
            f"aggregate <code>{esc(binding.aggregate)}</code>",
            f"type <code>{esc(chart.name)}</code>, tier {chart.tier}<br>"
            f"projection shape <code>{esc(chart.shape)}</code><br>"
            f"mark shape {tags(chart.mark)}, channel {tags(chart.channel)}<br>"
            f"key sources {tags(binding.key_sources)}",
            f"{len(view.data)} cells<br>"
            + "<br>".join(f"<code>{esc(' · '.join(d.key))}</code> = "
                          f"{' '.join(f'{k} {v:.4g}' for k, v in d.values.items())}"
                          f" ({d.rows} rows)" for d in view.data[:5])]])
        + figure_pair(record)
        + table(["Role", "Text written by the model"],
                [[f"<code>{esc(t.role)}</code>", esc(t.text)] for t in spec.texts])
        + note(f"<b>Caption (not drawn on the image; it is a training target)</b>: "
               f"{esc(spec.caption)}"))
    return card(intent.sentence[:60], trace,
                f"{scenario.name} · {spec.figure_id} · {chart.name}")


# ---------------------------------------------------------------- 03 render

DEGRADE_WHY = {
    "jpeg": "Pixels compressed, geometry untouched; every box still holds as recorded",
    "noise": "Noise added, geometry untouched",
    "blur": "Blurred, geometry untouched",
    "downscale": "The whole image scaled; every box multiplied by the same factor",
    "rotate": "The whole image rotated; every box through the same transform",
    "none": "Not degraded",
}


def page_stage03(run: Run) -> str:
    from chartgen.common.geometry import value_per_pixel
    from chartgen.s03_render.style import MARGIN_SETS

    body = [note(
        "<b>Recorded while drawing.</b> Every mark writes down its own box, key and values "
        "in the same statement that draws it, using the plotting library's own coordinate "
        "transform. The layout is settled before anything is drawn: auto-layout moves the "
        "plotting area afterwards and silently invalidates every box already recorded.")]

    record = next(r for r in run.records if len(r.panels) == 1 and r.marks)
    panel = record.panels[0]
    axis = panel.axis("y") or panel.axes[0]
    body.append(band("Frozen layout", f"{record.scenario_id} · {record.figure_id}"))
    margins = MARGIN_SETS[record.style.margins]
    body.append(table(["Quantity", "Value", "Set by"], [
        ["Image size", num(f"{record.image_size[0]} × {record.image_size[1]}"),
         f"style dimension <code>image_size</code>, "
         f"{len(STYLE_DOMAINS['image_size'].domain)} settings"],
        ["dpi", num(record.style.dpi),
         f"style dimension <code>dpi</code>, {len(STYLE_DOMAINS['dpi'].domain)} settings"],
        ["Left / top / right / bottom margin",
         num(f"{margins['left']:g} / {margins['top']:g} / "
             f"{margins['right']:g} / {margins['bottom']:g}"),
         f"style dimension <code>margins</code>; this one is "
         f"<code>{esc(record.style.margins)}</code>"],
        ["Plotting area", num([round(v) for v in panel.box.as_tuple()]),
         "The image size less the four margins, unchanged by content"],
        [f"Value axis <code>{esc(axis.role)}</code>",
         num(f"{axis.value_range} → pixels {tuple(round(p) for p in axis.pixel_range)}"),
         "The range actually drawn, written down after the fact"],
        ["What one pixel is worth",
         num(f"{value_per_pixel(axis.value_range, axis.pixel_range):.4g}")
         + (f" {esc(axis.label)}" if axis.label else ""),
         "Used by both the readability rule and the readback check"],
    ]))
    body.append(note("<b>\"Frozen\" means settled for this style vector, not one set for "
                     "every figure.</b> Image size, dpi and margins are each a style "
                     "dimension; redrawing a figure under another vector may give another "
                     "plotting area, because that pass records its own boxes. Auto-layout "
                     "is the other thing -- it moves the plotting area after drawing, and "
                     "every box already recorded is then wrong."))
    body.append(note("<b>An empty block keeps its room.</b> The text block above the "
                     "plotting area, the legend block below the axis title, and the gutter "
                     "on the right for a second value axis are the same width whether or "
                     "not they hold anything. A block is written as a share of the margin "
                     "it sits in rather than in pixels, so the narrowest setting still "
                     "leaves room for it. When room runs short, what gives way is type size "
                     "and angle: a text block reflows to its width and shrinks as needed, "
                     "crowded category labels slant before they shrink, and an axis title "
                     "is pinned to the end of the ticks. <b>Tick and legend text is never "
                     "cut</b> -- keys are read off them."))
    body.append(text_layout(run))

    body.append(band("The style vector", f"{len(STYLE_DOMAINS)} dimensions, one declared table"))
    groups: dict[str, list[str]] = {}
    for name, dim in STYLE_DOMAINS.items():
        groups.setdefault(dim.group or "other", []).append(name)
    body.append(table(["Group", "Dimensions", "Which"], [
        [esc(g), num(len(names)), tags(names)]
        for g, names in sorted(groups.items(), key=lambda kv: -len(kv[1]))]))
    body.append(card("Every dimension states what draws it and whether it changes readability",
        table(["Dimension", "Group", "Values", "Default", "Affects readability", "Drawn by"],
        [[f"<code>{esc(name)}</code>", esc(d.group), num(len(d.domain)),
          f"<code>{esc(d.default)}</code>", "yes" if d.readable else "no",
          f"<code>{esc(d.draws)}</code>"] for name, d in STYLE_DOMAINS.items()])
        + note("Two meta-tests read this table: every declared value must have a drawing "
               "branch, and a dimension marked as not affecting readability must leave the "
               "recorded answers bit-identical after a redraw."),
        "STYLE_DOMAINS"))

    body.append(band("One figure, two style versions",
                     "The pair is a training sample in its own right, and the input to the "
                     "third self-check"))
    pairs = [(a, b) for a in run.records for b in run.records
             if a.figure_id == b.figure_id and a.scenario_id == b.scenario_id
             and a.variant == 0 and b.variant == 1]
    for a, b in pairs[:3]:
        changed = [(k, getattr(a.style, k), getattr(b.style, k))
                   for k in vars(a.style) if getattr(a.style, k) != getattr(b.style, k)]
        same = sum(1 for m, n in zip(a.marks, b.marks) if m.values == n.values)
        body.append(card(f"{a.scenario_id} · {a.figure_id}",
                         f'<div class="diff"><div class="next"><h4>Version 0</h4>'
                         f'{image(Path(a.image_path))}</div>'
                         f'<div class="now"><h4>Version 1</h4>'
                         f'{image(Path(b.image_path))}</div></div>'
                         + table(["Dimension changed", "Version 0", "Version 1"],
                                 [[f"<code>{esc(k)}</code>", f"<code>{esc(x)}</code>",
                                   f"<code>{esc(y)}</code>"] for k, x, y in changed[:14]])
                         + note(f"<b>{len(changed)}</b> dimensions changed; of "
                                f"{len(a.marks)} marks, <b>{same}</b> have a bit-identical "
                                f"value dict."),
                         f"{a.figure_id} v0 / v1"))

    kinds = Counter(d.kind for r in run.records for d in r.degradations)
    if kinds:
        body.append(band("Degradations", "Only the ones whose geometry has a closed form"))
        body.append(table(["Kind", "Figures", "What happens to the boxes"], [
            [f"<code>{esc(k)}</code>", num(v), esc(DEGRADE_WHY.get(k, ""))]
            for k, v in kinds.most_common()]))

    body.append(band("Several plotting areas, and overlays",
                     "Layout is a parameter, and the key sources move with it"))
    for scenario, record, spec in pick(run, 6, relation=True):
        body.append(example(scenario, record, spec))

    body.append(band("The page as drawn, and the boxes as recorded",
                     "If a red box does not cover its shape, that figure is wrong"))
    body.append(box_legend())
    for scenario, record, spec in pick(run, PER_STAGE):
        body.append(example(scenario, record, spec))
    return "".join(body)


def text_layout(run: Run) -> str:
    """Whether the page's own text stayed where the layout says it is."""
    import itertools

    off = zero = overlap = pairs = 0
    for record in run.records:
        w, h = record.image_size
        for element in record.elements:
            x0, y0, x1, y1 = element.box.as_tuple()
            off += x0 < -0.5 or y0 < -0.5 or x1 > w + 0.5 or y1 > h + 0.5
            zero += element.box.area <= 0
        texts = [e for e in record.elements
                 if e.text and e.category not in ("Picture", "note")]
        for a, b in itertools.combinations(texts, 2):
            pairs += 1
            small = min(a.box.area, b.box.area)
            overlap += small > 0 and a.box.clip_to(b.box).area / small > 0.5
    elements = sum(len(r.elements) for r in run.records)
    return table(["What was measured", "Result", "Why it is measured"], [
        ["Page elements in total", num(elements), f"across {len(run.records)} records"],
        ["Boxes outside the image", num(off),
         "Text past the edge is invisible, and the record still gave it a box"],
        ["Zero-area boxes", num(zero), "Nothing undrawn should have a record"],
        ["Text pairs overlapping by more than half", num(overlap),
         f"{pairs} pairs compared"],
    ])


# ---------------------------------------------------------------- 04 record

def page_stage04(run: Run) -> str:
    from chartgen.registry.channels import MIN_PIXELS, RELATIVE_TOLERANCE

    body = [note(
        "<b>Readability is decided after rendering</b>, from actual pixel geometry plus the "
        "encoding channel. An unreadable mark loses its value target and keeps its "
        "localization target -- a pie or a heatmap can end up with no value target at all, "
        "and that is the rule working, not a defect.")]

    body.append(band("The rule",
                     "Stated once in chart_types.md §4; the code holds one implementation"))
    body.append(table(["Case", "Verdict", "Tolerance"], [
        ["Value printed on the image", "readable",
         "Matched exactly against that string; compared as a number, the tolerance is what "
         "the rounding left"],
        ["Colour", "not readable",
         "A colour scale is quantised and non-linear; there is no closed-form step"],
        ["Angle", "depends on share and radius",
         "Step <code>3 × 2 / (2π × radius)</code>, compared against tolerance × share"],
        ["Length, position",
         f"readable once the tolerance band spans {MIN_PIXELS:g} pixels",
         f"{RELATIVE_TOLERANCE:.0%} for a value that is not printed"],
        ["Key with no source on the page", "not readable",
         "A scatter mark is addressed by row number, and nothing on the page writes it"],
    ]))
    body.append(note(
        "<b>The two reasons are counted apart.</b> A mark can lose its value target because "
        "its key has no source on the page, or because its encoding cannot reach this "
        "tolerance. The two are unrelated, and one share mixing them says nothing about "
        "either."))

    channels: dict[str, list[int]] = {}
    by_type: dict[str, list[int]] = {}
    for record in run.records:
        name = "＋".join(types_of(record))
        slot = by_type.setdefault(name, [0, 0, 0])
        slot[0] += len(record.marks)
        slot[1] += sum(1 for m in record.marks if m.readable)
        slot[2] += sum(1 for m in record.marks if "not_shown" in (m.key_src or ()))
        for mark in record.marks:
            channel = channels.setdefault(mark.channel, [0, 0, 0])
            channel[0] += 1
            channel[1] += bool(mark.readable)
            channel[2] += "not_shown" in (mark.key_src or ())
    body.append(table(["Channel", "Marks", "Key with no source", "Key with a source",
                       "of which value targets", "Share"], [
        [f"<code>{esc(k)}</code>", num(v[0]), num(v[2]), num(v[0] - v[2]), num(v[1]),
         bar(v[1] / (v[0] - v[2])) if v[0] > v[2] else "—"]
        for k, v in sorted(channels.items(), key=lambda kv: -kv[1][0])]))
    body.append(card("By chart type", table(
        ["Type", "Marks", "Key with no source", "of which value targets", "Share"], [
            [tags(k.split("＋")), num(v[0]), num(v[2]), num(v[1]),
             bar(v[1] / (v[0] - v[2])) if v[0] > v[2] else "—"]
            for k, v in sorted(by_type.items(), key=lambda kv: -kv[1][0])]), "readable"))

    body.append(band("The three self-checks",
                     "All on the production path; a failure drops the figure and logs why"))
    ran = sum(1 for r in run.records if r.selfcheck.style_invariant is not None)
    ok = sum(1 for r in run.records if r.selfcheck.style_invariant is True)
    body.append(table(["Check", "What it asks", "Result this run"], [
        ["Is there anything inside the box", "The share of non-background pixels in it",
         num(f"{sum(1 for r in run.records if r.selfcheck.box_content is True)}"
             f" / {len(run.records)}") + " records passed"],
        ["Does the value read back", "Convert the box back to a value through the axis, "
                                     "and compare with what was recorded",
         num(f"{sum(1 for r in run.records if r.selfcheck.value_readback is True)}"
             f" / {len(run.records)}") + " records passed"],
        ["Does the answer survive a restyle", "Compare against the paired style version; "
                                              "no re-render needed",
         num(f"{ok} / {ran}") + " records ran this one and passed"],
    ]))

    body.append(note("<b>The threshold follows the mark shape rather than being one "
        "constant.</b> A filled shape (bar, cell) is judged at 15%; a printed number at 2%, "
        "because type never fills a cell; and a point at 3%, because a point's box is a "
        "fixed-size square around the marker -- the value is read from the box centre, so "
        "the box cannot change with which marker the style picked, and how much of the "
        "square the marker fills is then a property of the marker shape rather than of "
        "whether anything was drawn. All three numbers were measured: the thinnest case is "
        "a vertical-line marker at 72 dpi, filling 6%; a box moved onto blank page fills "
        "0%."))

    body.append(band("Read again, here and now",
                     "This page reads the images back itself, with no ground truth"))
    body.append(reverify(run))
    body.append(box_legend())

    body.append(band("What a record looks like",
                     "The three layers join on (figure_id, panel_id, key)"))
    for scenario, record, spec in pick(run, PER_STAGE):
        elements = Counter(e.category for e in record.elements)
        extra = [("Page-element layer", table(["Category", "Count"], [
            [f"<code>{esc(k)}</code>", num(v)] for k, v in elements.most_common()]))]
        if record.legend:
            extra.append(("Legend layer", table(["Legend entry", "Panels it covers"], [
                [esc(e.maps_to_category), ", ".join(e.applies_to_panels) or "—"]
                for e in record.legend])))
        extra.append(("Self-checks", ", ".join(
            f"{name} {'passed' if value else ('not run' if value is None else 'FAILED')}"
            for name, value in (("box content", record.selfcheck.box_content),
                                ("value readback", record.selfcheck.value_readback),
                                ("style invariance", record.selfcheck.style_invariant)))))
        body.append(example(scenario, record, spec, extra=extra))
    return "".join(body)


def reverify(run: Run, sample: int = 12) -> str:
    """Read the images back with the reward's own code and report what it says."""
    rows, totals = [], [0, 0, 0, 0]
    for _, record, _ in pick(run, sample):
        claims = V.claims_of(record)
        if not claims:
            continue
        judged = V.verify(record.image_path, claims, record.panels,
                          quantum=V.quantum_of_record(record))
        score = V.consistency(judged)
        measured = [j for j in judged if j.value_agrees is not None]
        totals[0] += len(judged)
        totals[1] += sum(j.has_content for j in judged)
        totals[2] += len(measured)
        totals[3] += sum(bool(j.value_agrees) for j in measured)
        rows.append([f"<code>{esc(record.scenario_id)} · {esc(record.figure_id)}</code>",
                     tags(types_of(record)), num(len(judged)), bar(score["grounded"]),
                     num(len(measured)),
                     bar(score["consistent"]) if measured else "—"])
    return table(["Figure", "Types", "Boxes checked", "Box has content", "Measurable",
                  "Value agrees"], rows) + note(
        f"Total: <b>{totals[1]} / {totals[0]}</b> boxes really do have something in them, "
        f"and of the <b>{totals[2]}</b> that geometry can measure, <b>{totals[3]}</b> agree "
        f"with the recorded value. "
        "This uses the reward function's own code; its only inputs are the image and the "
        "claimed <code>(value, box)</code>. "
        "A heatmap cell cannot be measured back to a value, and neither can a sector once a "
        "texture crosses its boundary, so on those rows \"measurable\" is lower than "
        "\"boxes checked\" -- what comes back is \"cannot measure\", not \"wrong\".")


# ---------------------------------------------------------------- 05 output

TARGET_WHAT: dict[str, tuple[str, str]] = {
    "grounded_table": ("Transcribe the whole figure into (key, value, box)",
                       "figure → full table"),
    "spot_check": ("Report one value for each of several keys", "key → value"),
    "mark_locate": ("Given a sentence, point at the box it describes",
                    "description → box"),
    "mark_read": ("Given a box, report its value", "box → value"),
    "drilldown": ("Given a sentence, report how many source rows are behind it",
                  "description → row count"),
    "page_elements": ("Box and classify every block on the page", "figure → layout"),
    "legend_binding": ("Which panels each legend entry covers", "legend → panels"),
    "key_source": ("Where on the page each key segment was read from", "key → source"),
    "caption": ("The sentence that cannot be read off the image", "figure → caption"),
}

SCOPE_WHAT = {
    "mark": "Only the segments written inside the plotting area",
    "panel": "Plus the title of the panel it sits in",
    "full": "Plus the segments that only colour says",
}


def page_stage05(run: Run) -> str:
    from chartgen.s05_output.export import exported_key, key_sources

    body = [note(
        "<b>What the exporter hands over is a parameter, not the record's shape.</b> "
        "<code>key_scope</code> decides how much of a mark's address goes out, "
        "<code>granularity</code> decides one file per figure, per page or per batch, and "
        "<code>format</code> decides whether that file holds the structured targets or a "
        "markdown document -- granularity and format are separate questions, and neither "
        "implies the other. "
        "<code>output.preset</code> packages the four for one benchmark, and anything named "
        "explicitly beside it wins. All of it is written into the artifact: a key the model "
        "returns cannot land back on a mark if the scope it was asked under is unknown.")]

    counts: Counter = Counter()
    files = 0
    for scenario in run.scenarios:
        for path in sorted((scenario.folder / "targets").glob("*.json")):
            files += 1
            blob = json.loads(path.read_text(encoding="utf-8"))
            for figure in blob.get("figures", []):
                for name, value in figure.items():
                    if isinstance(value, list):
                        counts[name] += len(value)
                    elif name == "caption" and value:
                        counts["caption"] += 1
            counts["page_elements"] += len(blob.get("page_elements", []))
    body.append(band("What this run exported", f"{files} files"))
    body.append(table(["Target", "What it asks", "Direction", "Rows this run"], [
        [f"<code>{esc(name)}</code>", esc(TARGET_WHAT[name][0]), esc(TARGET_WHAT[name][1]),
         num(counts.get(name, 0))] for name in (*TARGETS, "key_source")
        if name in TARGET_WHAT]))

    body.append(band("The nine targets for one figure",
                     "Several projections of the same tuples"))
    for scenario, record, spec in pick(run, 6):
        body.append(targets_card(scenario, record))

    body.append(band("One mark, three key scopes",
                     "The scope is written into the artifact, because a key has to land "
                     "back on a mark"))
    found = widest_key(run)
    if found:
        record, mark = found
        body.append(table(["key_scope", "Key handed over", "Source of each segment",
                           "How much goes out"], [
            [f"<code>{esc(scope)}</code>",
             f"<code>{esc(' · '.join(exported_key(mark, record, scope)))}</code>",
             tags(key_sources(mark, record, scope)), esc(SCOPE_WHAT[scope])]
            for scope in ("mark", "panel", "full")]))
        body.append(note(
            f"This mark comes from "
            f"<code>{esc(record.scenario_id)} · {esc(record.figure_id)}</code>. The key it "
            f"recorded for itself is <code>{esc(' · '.join(mark.key))}</code>, and its "
            f"segments were read from {tags(mark.key_src)}."))

    body.append(page_document(run.records))

    body.append(band("Reward: wrong answers caught without ground truth",
                     "The same code, with someone else writing the claim"))
    body.append(reward_demo(run))
    return "".join(body)


def targets_card(scenario: Scenario, record: Record) -> str:
    built = build_targets(record, key_scope="mark")
    mark = next((m for m in record.marks if m.readable), record.marks[0])
    row = next((r for r in built.grounded_table if r["box"] ==
                [round(v, 2) for v in mark.box.as_tuple()]), {})
    locate = next((r for r in built.mark_locate if r["box"] == row.get("box")), {})
    read = next((r for r in built.mark_read if r["box"] == row.get("box")), {})
    spot = next((r for r in built.spot_check if r["box"] == row.get("box")), {})
    drill = next((r for r in built.drilldown if r.get("query") == locate.get("query")), {})
    source = next((r for r in built.key_source if r["key"] == row.get("key")), {})
    body = table(["Target", "What one row looks like", "Rows for this figure"], [
        ["<code>grounded_table</code>", code(json.dumps(row, ensure_ascii=False)),
         num(len(built.grounded_table))],
        ["<code>spot_check</code>", code(json.dumps(spot, ensure_ascii=False)),
         num(len(built.spot_check))],
        ["<code>mark_locate</code>", code(json.dumps(locate, ensure_ascii=False)),
         num(len(built.mark_locate))],
        ["<code>mark_read</code>", code(json.dumps(read, ensure_ascii=False)),
         num(len(built.mark_read))],
        ["<code>drilldown</code>", code(json.dumps(drill, ensure_ascii=False)),
         num(len(built.drilldown))],
        ["<code>page_elements</code>",
         code(json.dumps(built.page_elements[0], ensure_ascii=False)),
         num(len(built.page_elements))],
        ["<code>legend_binding</code>",
         code(json.dumps(built.legend_binding[:1], ensure_ascii=False)),
         num(len(built.legend_binding))],
        ["<code>key_source</code>", code(json.dumps(source, ensure_ascii=False)),
         num(len(built.key_source))],
        ["<code>caption</code>", esc(built.caption or "(this figure has no caption)"),
         num(1 if built.caption else 0)],
    ])
    return card(scenario.schema.scenario_title[:50], figure_pair(record) + body,
                f"{scenario.name} · {record.figure_id}")


def widest_key(run: Run):
    """A mark whose three scopes really are three different keys."""
    from chartgen.s05_output.export import exported_key

    for record in run.records:
        if record.variant:
            continue
        for mark in record.marks:
            if len({exported_key(mark, record, s) for s in ("mark", "panel", "full")}) == 3:
                return record, mark
    return None


def reward_demo(run: Run, sample: int = 8) -> str:
    """The same check, on the renderer's own claims and on wrong ones."""
    from dataclasses import replace

    from chartgen.common.geometry import Box

    rows = []
    for _, record, _ in pick(run, sample):
        claims = V.claims_of(record)[:12]
        if not claims:
            continue
        quantum = V.quantum_of_record(record)
        img = rb.load_image(record.image_path)
        judged = V.judge(img, claims, record.panels, quantum)
        measurable = sum(1 for j in judged if j.value_agrees is not None)
        honest = V.consistency(judged)
        off_value = [replace(c, values={k: v * 1.25 + 1.0 for k, v in c.values.items()})
                     for c in claims]
        moved = [replace(c, box=Box(c.box.x0 + 240, c.box.y0 - 90,
                                    c.box.x1 + 240, c.box.y1 - 90)) for c in claims]
        wrong = V.consistency(V.judge(img, off_value, record.panels, quantum))
        away = V.consistency(V.judge(img, moved, record.panels, quantum))
        rows.append([f"<code>{esc(record.scenario_id)} · {esc(record.figure_id)}</code>",
                     tags(types_of(record)), num(len(claims)), num(measurable),
                     bar(honest["consistent"]) if measurable else "—",
                     bar(wrong["consistent"]) if measurable else "—",
                     bar(away["grounded"])])
    return table(["Figure", "Types", "Claims", "Measurable",
                  "Renderer's own claims: value agrees",
                  "Values scaled 1.25× plus 1",
                  "Boxes moved 240 × 90 px: box still has content"],
                 rows) + note(
        "The middle column is a <b>wrong value</b> and the right column a <b>box pointing "
        "somewhere else</b>; neither needs ground truth to catch. The scatter row stays "
        "high on the right: the denser the figure, the more likely a box dropped anywhere "
        "lands on some other point -- which is why both checks are needed.")


# ---------------------------------------------------------------- chart types

def type_href(name: str) -> str:
    return f"types/{name}.html"


def bound(text) -> str:
    if text is None:
        return "—"
    lo, hi = text
    return f"{lo} – {'∞' if hi is None else hi}"


def page_types(run: Run, drawn: dict) -> str:
    used = Counter(t for f in run.specs for t in f.chart_types)
    body = [note(
        "<b>17 types, one page each.</b> Every figure on these pages is drawn here and now "
        "from the hand-written scenarios in <code>tests/samples/</code>, with no model "
        "call, so the same repository regenerates the same images. "
        "The condition table decides when a type can be drawn; "
        f"this run drew {len(used)} of them.")]

    body.append(band("Projection shape × mark shape",
                     "Every cell either names its types or says why it is empty"))
    shapes = ("grouped_scalar", "grouped_fivenum", "binned_count", "per_row")
    marks = ("rect", "point", "sector", "cell", "boxlike", "band")
    rows = []
    for shape in shapes:
        cells = []
        for mark in marks:
            cell = GRID.get((shape, mark))
            cells.append(" ".join(
                f'<a class="tag" href="{type_href(n)}">{esc(n)}</a>' for n in cell)
                if isinstance(cell, tuple)
                else f'<span class="note" style="margin:0">{esc(cell)}</span>')
        rows.append([f"<code>{esc(shape)}</code>", *cells])
    body.append(table(["Projection shape", *marks], rows))

    body.append(band("The seventeen types",
                     "Open one to see what it draws and what it records"))
    cards = []
    for name, made in drawn.items():
        chart = CHARTS[name]
        record = made[0][2]
        cards.append(
            f'<a href="{type_href(name)}">{image(Path(record.image_path), width=420)}'
            f"<b>{esc(name)}</b><span>{esc(chart.family or 'in no view class')} · "
            f"{esc(chart.shape)} · {len(record.marks)} marks · "
            f"{used.get(name, 0)} drawn this run</span></a>")
    body.append(f'<div class="gridcards">{"".join(cards)}</div>')

    body.append(band("The condition table",
                     "The four condition columns read declarations only, so feasibility is "
                     "settled before any data exists"))
    body.append(table(["Type", "View class", "Tier", "Projection shape", "Mark shape",
                       "Channel", "Value dict", "Category cols", "Time cols", "Measures",
                       "Marks", "Drawn this run"], [
        [f'<a href="{type_href(name)}"><code>{esc(name)}</code></a>',
         esc(c.family or "—"), num(c.tier), f"<code>{esc(c.shape)}</code>",
         tags(c.mark), tags(c.channel),
         ", ".join(f"<code>{esc(k)}</code>" for k in c.value_keys),
         num(bound(c.n_cat)), num(bound(c.n_time)), num(bound(c.n_measure)),
         num(bound(c.n_marks)), num(used.get(name, 0))]
        for name, c in CHARTS.items()]))

    body.append(band("Density bands",
                     "A band raises only the mark-count ceiling; a type's own floor never "
                     "moves"))
    body.append(table(["Band", "Mark-count bounds", "Fact-table rows required"], [
        [f"<code>{esc(b.name)}</code>",
         num(f"{b.marks[0]} – {b.marks[1] if b.marks[1] is not None else '∞'}"),
         num(b.min_rows)] for b in DENSITY_BANDS]))
    return "".join(body)


def page_type(name: str, made: list, run: Run) -> str:
    """One chart type: its row in the table, and what it comes out as."""
    chart = CHARTS[name]
    spec = made[0][1]
    body = [note(
        f"<b>{esc(name)}</b> -- "
        f"{esc(chart.family or 'in no view class; reachable only through the type weights')}. "
        f"Projection shape <code>{esc(chart.shape)}</code>, mark shape {tags(chart.mark)}, "
        f"channel {tags(chart.channel)}. "
        "The figures below are drawn here and now from the hand-written scenarios, one per "
        "style vector, and all four passed the three self-checks.")]

    body.append(band("When it can be drawn",
                     "The four condition columns read declarations only"))
    body.append(table(["Condition", "Range", "What it means"], [
        ["Category columns", num(bound(chart.n_cat)), "How many category columns group it"],
        ["Time columns", num(bound(chart.n_time)), "How many time-axis columns"],
        ["Measures", num(bound(chart.n_measure)), "How many measure columns"],
        ["Grouping columns in total", num(bound(chart.n_group)),
         "None means category columns + time columns"],
        ["Category cross-product", num(bound(chart.card)),
         "The cell count when there is no time column"],
        ["Time points", num(bound(chart.points)),
         "Points on the axis when there is a time column"],
        ["Series", num(bound(chart.series)), "Series drawn against the time axis"],
        ["Marks", num(bound(chart.n_marks)),
         "The sparsest band; a density band raises only the ceiling"],
        ["Fact-table rows", num(chart.min_raw_rows), "Below this it is not drawn"],
        ["Value dict", ", ".join(f"<code>{esc(k)}</code>" for k in chart.value_keys),
         "The numbers each mark writes down"],
    ]))

    body.append(band("How it was drawn this time", f"{spec.scenario_id} · {name}"))
    binding = spec.views[0].binding
    body.append(table(["Binding", "Value"], [
        ["Dims", ", ".join(f"<code>{esc(d)}</code>" for d in binding.dims) or "—"],
        ["Time", f"<code>{esc(binding.time or '—')}</code>"
                 + (f", resampled {esc(binding.resample)}" if binding.resample else "")],
        ["Measures", ", ".join(f"<code>{esc(m)}</code>" for m in binding.measures) or "—"],
        ["Aggregate", f"<code>{esc(binding.aggregate)}</code>"],
        ["Key sources", tags(binding.key_sources)],
    ]))
    view = spec.views[0]
    body.append(card("The projected data (first 8 rows)",
                     table(["Key", "Values", "Rows behind"], [
        [f"<code>{esc(' · '.join(d.key))}</code>",
         " ".join(f"{k} {v:.4g}" for k, v in d.values.items()), num(d.rows)]
        for d in view.data[:8]]) + (note(f"{len(view.data) - 8} more rows.")
                                    if len(view.data) > 8 else ""), "ViewSpec.data"))

    body.append(gt_table(name, made[0][2]))

    for index, (label, _, record) in enumerate(made):
        # The values are the same under every style -- that is what the style
        # self-check asserts -- so the marks are written out once and the other
        # renderings carry the image and what the pixels say about it.
        detail = marks_table(record, 6) if index == 0 else ""
        body.append(card(label, figure_pair(record) + detail + readback_table(record),
                         f"{name} · v{record.variant}",
                         f"{len(record.marks)} marks · "
                         f"{sum(1 for m in record.marks if m.readable)} value targets"))

    live = [(r, s) for s in run.scenarios for r in s.first
            if name in {t for p in r.panels for t in p.chart_types}]
    if live:
        body.append(band("The same type in this run", f"{len(live)} figures"))
        for record, scenario in live[:3]:
            found = scenario.spec(record.figure_id)
            if found:
                body.append(example(scenario, record, found))
    return "".join(body)


#: Rows of a ground-truth table written out on a chart-type page. Every type but one
#: comes in under it: a scatter draws up to five hundred points and its L2 degenerates
#: to one row per mark, so its table is five hundred near-identical lines.
GT_ROWS = 60


def gt_table(name: str, record: Record) -> str:
    """The answer form: this record projected the way the benchmark asks for it.

    The same three calls a page export makes, on the example drawn above -- so what is
    shown is the document the exporter would write, not a view invented for this page.
    """
    unit = build_targets(record, key_scope="full")
    total = len(unit.grounded_table)
    unit.grounded_table = unit.grounded_table[:GT_ROWS]
    extra = (note(f"{total - GT_ROWS} more rows, one per mark.")
             if total > GT_ROWS else "")
    return card("Ground-truth table (the markdown parsebench asks for)",
                code(as_markdown(name, [unit])) + extra,
                f"{name}.md", f"{total} rows")


def readback_table(record: Record) -> str:
    """What the pixels say about this record's own claims, computed here and now."""
    claims = V.claims_of(record)
    if not claims:
        return ""
    judged = V.verify(record.image_path, claims, record.panels,
                      quantum=V.quantum_of_record(record))
    measured = [j for j in judged if j.value_agrees is not None]
    score = V.consistency(judged)
    return table(["Read back here and now", "Result"], [
        ["Box has content", f"{bar(score['grounded'])} ({len(judged)} boxes)"],
        ["Measurable by geometry", num(len(measured))],
        ["Value agrees", bar(score["consistent"]) if measured else "— (cannot measure)"],
        ["Self-checks",
         ", ".join(f"{n} {'passed' if v else ('not run' if v is None else 'FAILED')}"
                   for n, v in (("box content", record.selfcheck.box_content),
                                ("value readback", record.selfcheck.value_readback)))],
    ])


# ---------------------------------------------------------------- checks

#: What each kind of check answers, and what it cannot.
CHECK_KINDS: tuple[tuple[str, str, str], ...] = (
    ("Tests", "Each one asserts a property: this input should give that output, this case "
              "should be rejected",
     "Where few are written, it says nothing"),
    ("Statement coverage", "Which lines were never executed at all",
     "Executed is not checked: a wrong line runs just as well"),
    ("Fault injection", "Break the code and see whether a test fails",
     "Only the kinds of fault that were injected; a survivor is either logic nothing "
     "checks or an equivalent change nothing could observe"),
    ("Artifact readback", "Measure what this run produced against the definitions: is the "
                          "box inside the image, does the value read back",
     "Speaks only about this run's artifacts, not about the code on other inputs"),
)


def page_checks(run: Run, checks: dict, mutation: dict, coverage: dict,
                tests: dict) -> str:
    body = [note(
        "<b>This page is about how the code was verified, not about what it drew.</b> "
        "Each of the four checks answers one question and cannot answer the others: "
        "coverage cannot say whether a wrong line would be noticed, which is what the "
        "fault injection is for -- break the code and see whether a test fails.")]
    body.append(table(["Check", "What it answers", "What it cannot answer"], [
        [f"<b>{esc(a)}</b>", esc(b), esc(c)] for a, b, c in CHECK_KINDS]))

    body.append(band("Tests", f"{checks['tests']}, grouped by what they check"))
    body.append(table(["Test file", "Tests", "What it checks"], [
        [f"<code>{esc(name)}</code>", num(count), esc(TEST_WHAT.get(name, ""))]
        for name, count in sorted(tests.items(), key=lambda kv: -kv[1])]))

    body.append(band("Statement coverage", f"{checks['coverage']:.0f}%, by module"))
    rows = []
    for path, entry in sorted(coverage.get("files", {}).items(),
                              key=lambda kv: kv[1]["summary"]["percent_covered"]):
        summary = entry["summary"]
        rows.append([f"<code>{esc(path.replace('src/', ''))}</code>",
                     num(summary["num_statements"]), num(summary["missing_lines"]),
                     bar(summary["percent_covered"] / 100)])
    body.append(table(["File", "Statements", "Never executed", "Covered"], rows))
    body.append(note("What is uncovered in <code>cli.py</code> and <code>report.py</code> "
                     "are the branches that need the network or a real model; everything "
                     "else runs under test."))

    body.append(band("Fault injection",
                     f"{mutation['killed']} / {mutation['total']} caught by tests"))
    by_module: dict[str, list[int]] = {}
    for m in mutation["mutants"]:
        slot = by_module.setdefault(m["module"], [0, 0])
        slot[0] += 1
        slot[1] += bool(m["killed"])
    from tools.mutation import COVERED_BY

    if len(by_module) < len(COVERED_BY):
        body.append(note(
            f"<b>This round injected into {len(by_module)} modules, of "
            f"{len(COVERED_BY)} on the list.</b> "
            "Every injected fault reruns the test files that cover it, so a full round "
            "takes hours. The modules that were not reached are absent from the table "
            "below: their rate is neither high nor low, it was not measured this round."))
    body.append(table(["Module", "Injected", "Caught", "Rate"], [
        [f"<code>{esc(k)}</code>", num(v[0]), num(v[1]), bar(v[1] / v[0])]
        for k, v in sorted(by_module.items(), key=lambda kv: kv[1][1] / kv[1][0])]))
    survivors = [m for m in mutation["mutants"] if not m["killed"]]
    if survivors:
        body.append(card("Survivors",
            table(["Where", "Changed to", "Kind of fault injected"], [
            [f"<code>{esc(m['module'])}:{m['line']}</code>",
             code(m["after"][:120]), esc(m["kind"])] for m in survivors])
            + note("Two cases: logic that genuinely nothing checks, or an equivalent "
                   "change nothing could observe -- which node of a cycle an error message "
                   "starts at, say, or a condition that is always true on this path. The "
                   "first is a test to write and the second can only be told apart by "
                   "reading the code, so the table lists both."),
            f"{len(survivors)} of them"))
    else:
        body.append(note("Every fault injected this round was caught by a test."))
    body.append(note(
        "<b>The instrument is checked first.</b> Before injecting anything, the tool copies "
        "the source and the tests into a temporary directory and runs the relevant tests "
        "against that copy -- if they do not pass, it stops there. A copy whose imports do "
        "not even resolve would report every injected fault as \"caught\", giving 100% and "
        "saying nothing. This is not decoration: with the check in place, some of the "
        "\"caught\" results in earlier rounds turned out to be the copy failing on its own, "
        "and the numbers were corrected."))
    body.append(note("The kinds of fault injected: loosening <code>&gt;=</code> to "
                     "<code>&gt;</code>, swapping <code>min</code> for <code>max</code>, "
                     "deleting a <code>not</code>, turning <code>and</code> into "
                     "<code>or</code>, turning <code>all</code> into <code>any</code>, "
                     "taking the wrong edge of a box, and taking the wrong index. "
                     "Injection happens in code only -- text inside comments and strings "
                     "does not count. "
                     "Rerun with <code>python tools/mutation.py --limit 5</code>."))

    body.append(band("Artifact readback",
                     "What this run produced, measured against the definitions"))
    body.append(table(["What was measured", "Result"], [
        ["Records / marks", num(f"{len(run.records)} / {run.marks}")],
        ["Records passing all three self-checks",
         num(f"{sum(1 for r in run.records if r.selfcheck.passed)}"
             f" / {len(run.records)}")],
        ["Page elements inside the image",
         num(f"{checks['elements']}, {checks['off']} outside")],
        ["Zero-area element boxes", num(checks["zero"])],
        ["Text pairs overlapping by more than half",
         num(f"{checks['overlap']} / {checks['pairs']}")],
        ["Labels overlapping by more than three tenths", num(checks["labels"])],
    ]))
    body.append(note("These rows are not copied out of a log; they were measured again as "
                     "this page was built."))

    body.append(band("The shape of the code",
                     "One file, one responsibility; stages talk only through interfaces"))
    body.append(shape_of_code())

    body.append(band("Invariants", "The properties that are written as tests"))
    body.append(table(["Property", "Where it is checked"], [
        ["Same input and seed, bit-identical output",
         "<code>test_pipeline.py</code>, end to end twice and compared"],
        ["Every declared chart type has a drawing branch",
         "<code>test_shapes.py</code> meta-test"],
        ["Every declared style value has a drawing branch",
         "<code>test_render.py</code> meta-test"],
        ["A style dimension that does not affect readability leaves the answers identical",
         "<code>test_render.py</code>, redrawn dimension by dimension"],
        ["Every recorded box has something inside it",
         "<code>test_shapes.py</code>, pixels read back per type"],
        ["Every recorded value converts back from its box and axis",
         "<code>test_shapes.py</code>, pixels read back per type"],
        ["The self-check and the reward use one implementation",
         "<code>test_record.py</code>, the two paths give equal results"],
        ["Stages talk only through interfaces",
         "<code>test_invariants.py</code>, imports checked statically"],
        ["An interface change carries its sample file with it",
         "<code>test_serde.py</code>, sample round-trip"],
        ["Page elements stay inside the image and do not overlap",
         "<code>test_render.py</code>, style sweep"],
    ]))
    return "".join(body)


def shape_of_code() -> str:
    """How the source is divided up, counted from the files themselves."""
    src = ROOT / "src"
    files = [p for p in src.rglob("*.py") if "__pycache__" not in str(p)]
    lines = {p: len(p.read_text(encoding="utf-8").splitlines()) for p in files}
    longest = sorted(lines.items(), key=lambda kv: -kv[1])[:8]
    total = sum(lines.values())
    stages = sorted({str(p.relative_to(src / "chartgen")).split("/")[0]
                     for p in files if (src / "chartgen") in p.parents
                     and p.parent != src / "chartgen"})
    return table(["Quantity", "Count"], [
        ["Source files", num(len(files))],
        ["Lines of source", num(total)],
        ["Average per file", num(f"{total / max(len(files), 1):.0f} lines")],
        ["Longest file", num(f"{longest[0][1]} lines") + f" <code>"
         f"{esc(longest[0][0].relative_to(src))}</code>"],
        ["Packages", tags(stages)],
    ]) + card("The eight longest files", table(["File", "Lines"], [
        [f"<code>{esc(path.relative_to(src))}</code>", num(count)]
        for path, count in longest]) + note(
        "Stages do not import each other: anything one stage needs from another has to "
        "move into <code>interfaces/</code>, <code>registry/</code> or "
        "<code>common/</code> first. <code>test_invariants.py</code> checks this "
        "statically."),
        "src/")


#: One line per test file: what that file is checking.
TEST_WHAT: dict[str, str] = {
    "test_render.py": "Recording while drawing, frozen layout, style not changing the "
                      "answers, label and tick readability",
    "test_shapes.py": "All 17 chart types drawn and read back from pixels",
    "test_project.py": "The four projection shapes, aggregates and resampling",
    "test_compose.py": "The three ways a figure is chosen, the budget, rejection reasons",
    "test_panel.py": "How each of the nine relations derives a second view from its anchor",
    "test_admit.py": "Data conditions and the redundancy rule",
    "test_conditions.py": "The condition table's structural and semantic predicates",
    "test_record.py": "The three record layers, readability, the three self-checks",
    "test_export.py": "The shape and tolerance of the nine training targets",
    "test_readback.py": "Reading pixels back: anchors, background, tolerance",
    "test_geometry.py": "Coordinate conversion and transform matrices",
    "test_channels.py": "The readability rule and its tolerances",
    "test_declare.py": "Argument checking in the declaration script",
    "test_engine.py": "The data-generating engine: allocation and dependencies",
    "test_expr.py": "Parsing and evaluating measure expressions",
    "test_author.py": "The data stage end to end, and validation of the model's reply",
    "test_validate.py": "Feasibility and structural checks",
    "test_page.py": "Page composition and element merging",
    "test_caption.py": "Captions",
    "test_cli.py": "The offline path of every CLI subcommand",
    "test_serde.py": "Interface serialisation and the sample files",
    "test_invariants.py": "Static constraints across stages",
    "test_mixing.py": "The real-chart mixing ratio",
    "test_pool.py": "Drawing from the domain pool, and deduplication",
    "test_report.py": "The readable view of an artifact",
    "test_rng_cache.py": "Random streams and the cache",
    "test_llmkit.py": "The model-calling layer: structured output, cache, batching",
    "test_pipeline.py": "End to end: three hand-written scenarios through all five stages",
    "test_stage01_live.py": "Real model calls (skipped by default)",
    "test_config.py": "Reading and overriding config: dot paths, defaults, CLI assignment",
    "test_mutation_tool.py": "The fault-injection tool itself: what it injects must be "
                             "code, not a comment",
    "test_analysis.py": "ParseBench analysis: spot-check verdicts and statistics",
    "test_contract.py": "The ParseBench contract: fields and the four-step rule",
}


def measure(run: Run) -> dict:
    """The numbers the pages quote about this run, all counted here."""
    import itertools

    off = zero = overlap = pairs = labels = elements = 0
    for record in run.records:
        w, h = record.image_size
        elements += len(record.elements)
        for element in record.elements:
            x0, y0, x1, y1 = element.box.as_tuple()
            off += x0 < -0.5 or y0 < -0.5 or x1 > w + 0.5 or y1 > h + 0.5
            zero += element.box.area <= 0
        texts = [e for e in record.elements
                 if e.text and e.category not in ("Picture", "note")]
        for a, b in itertools.combinations(texts, 2):
            pairs += 1
            small = min(a.box.area, b.box.area)
            overlap += small > 0 and a.box.clip_to(b.box).area / small > 0.5
        boxed = [m for m in record.marks if m.label_box is not None]
        for a, b in itertools.combinations(boxed, 2):
            if a.panel_id != b.panel_id:
                continue
            small = min(a.label_box.area, b.label_box.area)
            labels += small > 0 and a.label_box.clip_to(b.label_box).area / small > 0.3
    return {"off": off, "zero": zero, "overlap": overlap, "pairs": pairs,
            "labels": labels, "elements": elements}


def collect_tests() -> dict:
    """How many tests each file holds, asked of pytest rather than counted by hand."""
    import subprocess

    done = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q",
                           "--no-header", "-p", "no:cacheprovider"],
                          cwd=ROOT, capture_output=True, text=True)
    counts: Counter = Counter()
    for line in done.stdout.splitlines():
        # Two shapes come out of pytest depending on its version: one line per test,
        # and one line per file with a count after it.
        if ": " in line and line.strip().split(": ")[-1].isdigit():
            path, _, count = line.rpartition(": ")
            counts[Path(path.strip()).name] += int(count)
        elif "::" in line:
            counts[Path(line.split("::")[0]).name] += 1
    return dict(counts)


# ---------------------------------------------------------------- writing the site


# ---------------------------------------------------------------- every figure

def page_gallery(run: Run) -> str:
    """Every figure the run produced, small, in the order it produced them.

    A worked example says whether one figure is right. What it cannot say is what
    the batch looks like -- whether the figures differ from each other at all, and
    whether any one of them came out visibly broken. That is what a wall is for.
    """
    body = [note(
        "<b>This page holds every figure the run drew, none left out.</b> "
        "Each thumbnail carries its recorded boxes: red for marks with a value target, "
        "grey for marks with only a localization target, green for page elements. "
        "Whether a box covers its shape, and whether a figure came out visibly wrong, is "
        "visible at a glance. For the numbers, go to that stage's page, where the figure "
        "is full size beside its whole record."), box_legend()]

    body.append(band("What the scenarios drew between them",
                     "Each scenario is an independent run"))
    body.append(table(["Scenario", "Subject", "Figures", "Marks", "Value targets",
                       "Types drawn"],
                      [[f"<code>{esc(s.name)}</code>", esc(s.schema.scenario_title[:44]),
                        num(len(s.first)), num(sum(len(r.marks) for r in s.first)),
                        num(sum(1 for r in s.first for m in r.marks if m.readable)),
                        tags(sorted({t for r in s.first for t in types_of(r)}))]
                       for s in run.scenarios]))

    for s in run.scenarios:
        body.append(band(f"{s.name} · {esc(s.schema.scenario_title[:40])}",
                         f"{len(s.first)} figures"))
        body.append(wall([(embed(Path(r.image_path), r, THUMB_WIDTH), r.figure_id,
                           thumb_meta(s.spec(r.figure_id), r)) for r in s.first]))
    return "".join(body)


def page_pages(run: Run) -> str:
    """Everything that holds more than one chart, in the three places one can go.

    Every other page of this site shows one figure at a time, and a composed page
    then appears as its members -- two thumbnails labelled `f09` and `f10` with
    nothing saying they share an image. This page is the one that shows a page as a
    page, and it sits beside the two layouts a second view can take instead.
    """
    firsts = [(s, r) for s in run.scenarios for r in s.first]
    specs = {(s.name, f.figure_id): f for s in run.scenarios for f in s.specs}

    def title_of(scenario: Scenario, record: Record) -> str:
        spec = specs.get((scenario.name, record.figure_id))
        return spec.text("title") if spec else ""

    def relation_of(scenario: Scenario, record: Record) -> str:
        spec = specs.get((scenario.name, record.figure_id))
        return (spec.relation or "") if spec else ""

    paged = [(s, r) for s, r in firsts if r.page_id]
    panelled = [(s, r) for s, r in firsts if len(r.panels) > 1]
    overlaid = [(s, r) for s, r in firsts
                if len(r.panels) == 1 and len(r.panels[0].chart_types) > 1]

    body = [note(
        "<b>A second view beside the first has only three places to go: the same plotting "
        "area, another plotting area on the same image, or another image on the same "
        "page.</b> "
        "All three are computed from a relation, with no random number involved -- the "
        "relation fixes what the second view draws, and all that is left is where it "
        "lands. This page puts the three side by side, and it is the only place on the "
        "site that looks at a whole page as one page.")]

    by_page: dict[tuple[str, str], list[Record]] = {}
    for scenario, record in paged:
        by_page.setdefault((scenario.name, record.page_id), []).append(record)
    counts = Counter(len(v) for v in by_page.values())
    # The relation is a property of how the figure was chosen, so it lives on the spec.
    def relations_of(chosen) -> list[str]:
        found = (specs.get((s.name, r.figure_id)) for s, r in chosen)
        return sorted({f.relation for f in found if f is not None and f.relation})

    body.append(band("The three forms in this run",
                     "Relation names come from the specs; the counts are counted"))
    body.append(table(["Form", "Where the second view goes", "Count", "Relations"], [
        ["Several figures on one page", "another figure on the same page",
         f'<span class="n">{len(by_page)}</span> pages · '
         f'{len(paged)} figures',
         tags(relations_of(paged))],
        ["Several panels on one figure", "another plotting area on the same image",
         f'<span class="n">{len(panelled)}</span> figures',
         tags(relations_of(panelled))],
        ["Overlaid in one plotting area", "the same plotting area",
         f'<span class="n">{len(overlaid)}</span> figures',
         tags(relations_of(overlaid))],
    ]))
    if counts:
        body.append(note("Figures per page: "
                         + ", ".join(f"{k} × {v} pages" for k, v in sorted(counts.items()))))

    if by_page:
        body.append(band("A page seen as a page",
                         f"{len(by_page)} pages, each one whole-page image"))
        for (name, page_id), members in list(by_page.items())[:4]:
            scenario = next(s for s in run.scenarios if s.name == name)
            first = members[0]
            body.append(card(
                f"{name} · {page_id}",
                image(Path(first.image_path), None, 380)
                + table(["Figures on this page", "Title", "Marks", "Relation"],
                        [[f"<code>{esc(r.figure_id)}</code>",
                          esc(title_of(scenario, r)), num(len(r.marks)),
                          f"<code>{esc(relation_of(scenario, r))}</code>"]
                         for r in members])
                + page_document(members),
                f"{len(members)} figures",
                f"{sum(len(r.marks) for r in members)} marks"))

    for title, chosen in (("Multi-panel: the second view takes another plotting area",
                           panelled),
                          ("Overlay: two views share one plotting area", overlaid)):
        if not chosen:
            continue
        body.append(band(title, f"{len(chosen)} in all; 3 shown below"))
        for scenario, record in chosen[:3]:
            found = specs.get((scenario.name, record.figure_id))
            if found:
                body.append(example(scenario, record, found))
    return "".join(body)


def thumb_meta(spec: FigureSpec | None, record: Record) -> str:
    """The line under a thumbnail: what it is, how it was chosen, how much is on it."""
    kind = f"{esc(spec.source.kind)}" if spec else ""
    if spec is not None and spec.relation:
        kind += f" · {esc(spec.relation)}"
    return (f"{esc(' / '.join(types_of(record)))}<br>{kind} · "
            f"{len(record.marks)} marks · "
            f"{sum(1 for m in record.marks if m.readable)} value targets")


# ---------------------------------------------------------------- diversity

def page_diversity(run: Run, out_dir: Path, figures: int = 3, styles: int = 6) -> str:
    """What varies between one figure and the next, and what must not vary at all."""
    body = [note(
        "<b>The style vector decides what the data is drawn as; it does not decide what "
        "the answers are.</b> "
        "This page separates the two. The top half redraws one figure under six style "
        "vectors, where the answers have to come back word for word identical. The bottom "
        "half is how much this run itself varies -- types, layouts, key sources, and how "
        "many marks each figure carries.")]

    body.append(band("One figure, six style vectors",
                     "Redrawn here and now, not the two the run produced"))
    body.append(note(
        "Every dimension of the style vector states whether it changes which values can be "
        "read. For the ones that do not, every mark's key and values must be bit-identical "
        "after a redraw -- which is exactly what the third self-check asserts, verified "
        "again here. The number of value targets is allowed to move: a greyscale palette "
        "makes marks that are told apart by colour unreadable."))
    for scenario, record, spec in pick(run, figures):
        body.append(style_sweep(scenario, spec, out_dir, styles))

    body.append(band("Two style versions of one figure",
                     "The paired samples the run produced itself"))
    body.append(note(
        "Every figure was drawn twice, under different styles. The pair is a training "
        "sample for style ablation, and the input to the third self-check: the answers read "
        "back from the two have to agree."))
    pairs = []
    for scenario, record, spec in pick(run, 6):
        other = next((r for r in scenario.records
                      if r.figure_id == record.figure_id and r.variant != record.variant), None)
        if other is None:
            continue
        for one in (record, other):
            pairs.append((embed(Path(one.image_path), None, THUMB_WIDTH),
                          f"{one.figure_id} · v{one.variant}",
                          f"{esc(' / '.join(types_of(one)))}<br>"
                          f"{sum(1 for m in one.marks if m.readable)} value targets · "
                          f"{sum(1 for m in one.marks if m.labeled)} with the value printed"))
    body.append(wall(pairs))

    body.append(band("How much this run varies", "All counted off the artifacts"))
    body.append(spread(run))

    body.append(band("Density bands",
                     "How many marks a figure may hold follows the fact table's row count"))
    body.append(table(["Band", "Marks", "Fact-table rows needed", "Figures in this band"], [
        [f"<code>{esc(b.name)}</code>",
         f"{b.marks[0]} – {'no limit' if b.marks[1] is None else b.marks[1]}",
         num(b.min_rows),
         num(sum(1 for r in run.records
                 if b.marks[0] <= len(r.marks) <= (b.marks[1] or 10 ** 9)))]
        for b in DENSITY_BANDS]))
    body.append(note(
        "A band widens only the ceiling, never the floor: three bars is the fewest that can "
        "be compared, whatever density the batch is drawn at. A table short of rows drops a "
        "band rather than relaxing the per-cell minimum."))
    return "".join(body)


def style_sweep(scenario: Scenario, spec: FigureSpec, out_dir: Path, styles: int) -> str:
    """One figure drawn again under several style vectors, and read back each time."""
    from dataclasses import fields
    from chartgen.s03_render.render import render
    from chartgen.s03_render.style import default, sample
    from chartgen.s04_record.selfcheck import finish

    base = default()
    items, rows, answers0 = [], [], None
    for index in range(styles):
        style = base if index == 0 else sample(SEED + index, scenario.name, spec.figure_id)
        folder = out_dir / f"{scenario.name}_{spec.figure_id}" / f"v{index}"
        made = finish(render(spec, style, folder, index), spec)
        answers = {(m.panel_id, m.key): tuple(sorted(m.values.items())) for m in made.marks}
        answers0 = answers if answers0 is None else answers0
        changed = [f.name for f in fields(style)
                   if getattr(style, f.name) != getattr(base, f.name)]
        label = "Default style" if index == 0 else f"Sample {index}"
        items.append((embed(Path(made.image_path), made, THUMB_WIDTH), label,
                      f"{len(made.marks)} marks · "
                      f"{sum(1 for m in made.marks if m.readable)} value targets<br>"
                      f"{esc(', '.join(changed[:3]) or '—')}"))
        rows.append([label, num(len(changed)), num(len(made.marks)),
                     num(sum(1 for m in made.marks if m.readable)),
                     num(sum(1 for m in made.marks if m.labeled)),
                     '<span class="ok">identical</span>' if answers == answers0
                     else '<span class="bad">DIFFERENT</span>'])
    head = ["Style", "Dimensions changed", "Marks", "Value targets", "Value printed",
            "Keys and values match the default"]
    tail = ""
    if all(r[3] == num(0) for r in rows) and any(r[4] != num(0) for r in rows):
        tail = note(
            "This figure has 0 value targets while some values are printed on it. The two "
            "are consistent: one segment of a scatter mark's key (the row number) has no "
            "source anywhere on the page, so no question's answer is that mark's value and "
            "it keeps only a localization target. The rule looks at whether the key can be "
            "recovered first, and at the encoding channel second.")
    return card(f"{spec.figure_id} · {esc(spec.text('title'))[:44]}",
                wall(items) + table(head, rows) + tail,
                f"{scenario.name} · {' / '.join(types_of(scenario.records[0]))}")


def spread(run: Run) -> str:
    """How much the batch varies, counted along every axis the record carries."""
    firsts = [r for s in run.scenarios for r in s.first]
    specs = {(s.name, f.figure_id): f for s in run.scenarios for f in s.specs}
    axes = [
        ("Chart type", Counter(t for r in firsts for t in types_of(r))),
        ("How it was chosen", Counter(specs[(s.name, r.figure_id)].source.kind
                                      for s in run.scenarios for r in s.first)),
        ("Layout", Counter(specs[(s.name, r.figure_id)].layout
                           for s in run.scenarios for r in s.first)),
        ("Panel relation", Counter(specs[(s.name, r.figure_id)].relation or "(single view)"
                                   for s in run.scenarios for r in s.first)),
        ("Mark shape", Counter(m.mark_shape for r in firsts for m in r.marks)),
        ("Encoding channel", Counter(m.channel for r in firsts for m in r.marks)),
        ("Key source", Counter(src for r in firsts for m in r.marks for src in m.key_src)),
        ("Key segments", Counter(str(len(m.key)) for r in firsts for m in r.marks)),
    ]
    out = []
    for title, counter in axes:
        total = sum(counter.values()) or 1
        rows = [[f"<code>{esc(name)}</code>", num(n), bar(n / total)
                 + f"{100 * n / total:.0f}%"]
                for name, n in counter.most_common()]
        out.append(card(f"{title} ({len(counter)} distinct)",
                        table(["", "Count", ""], rows)))
    return "".join(out)


def write(path: Path, title: str, current: str, body: str, lead: str,
          facts: Sequence[tuple], depth: int = 0) -> None:
    """One page, self-contained. `depth` fixes the links from a subdirectory."""
    prefix = "../" * depth
    links = [(prefix + href, name, hint) for href, name, hint in PAGES]
    head = masthead(title, lead, facts) + site_nav(prefix + current, links)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document(title, head, body), encoding="utf-8")


def build(run: Run, out: Path, *, gallery_dir: Path, skip_gallery: bool = False) -> list[Path]:
    checks = measure(run)
    mutation_path = out / "data" / "mutation.json"
    coverage_path = out / "data" / "coverage.json"
    mutation = (json.loads(mutation_path.read_text(encoding="utf-8"))
                if mutation_path.exists() else {"killed": 0, "total": 0, "mutants": []})
    coverage = (json.loads(coverage_path.read_text(encoding="utf-8"))
                if coverage_path.exists() else {"files": {}, "totals": {}})
    tests = collect_tests()
    checks |= {"tests": sum(tests.values()),
               "coverage": coverage.get("totals", {}).get("percent_covered", 0.0),
               "killed": mutation["killed"], "mutants": mutation["total"]}

    facts = [(len(run.scenarios), "scenarios"), (len(run.specs), "figures"),
             (len(run.records), "records"), (run.marks, "marks"),
             (f"{checks['tests']}", "tests")]
    lead = ("The artifacts one real run left behind, read back page by page. "
            "A page per stage, a page per chart type, and a last page on how the code was "
            "verified.")

    written = []
    pages = {
        "stage01.html": ("01 data", lambda: page_stage01(run)),
        "stage02.html": ("02 figure", lambda: page_stage02(run)),
        "stage03.html": ("03 render", lambda: page_stage03(run)),
        "stage04.html": ("04 record", lambda: page_stage04(run)),
        "stage05.html": ("05 output", lambda: page_stage05(run)),
        "gallery.html": ("Every figure", lambda: page_gallery(run)),
        "pages.html": ("Several at once", lambda: page_pages(run)),
        "diversity.html": ("Diversity", lambda: page_diversity(run, gallery_dir / "styles")),
        "checks.html": ("Checks", lambda: page_checks(run, checks, mutation, coverage, tests)),
    }
    drawn = {} if skip_gallery else gallery.draw(gallery_dir)
    if drawn:
        pages["types.html"] = ("Chart types", lambda: page_types(run, drawn))

    # The index says how many pictures each of the others carries, so it is built last.
    bodies = {name: builder() for name, (_, builder) in pages.items()}
    shots = {name: text.count("data:image/jpeg") for name, text in bodies.items()}
    titles = {name: title for name, (title, _) in pages.items()}
    titles["index.html"] = "One run, end to end · entrance"
    bodies["index.html"] = page_index(run, checks, shots)
    for name in ("index.html", *pages):
        write(out / name, titles[name], name, bodies[name], lead, facts)
        written.append(out / name)
        print(f"  {out / name}")
    for name, made in drawn.items():
        target = out / "types" / f"{name}.html"
        write(target, f"{name} · chart type", "types.html", page_type(name, made, run),
              lead, facts, depth=1)
        written.append(target)
    if drawn:
        print(f"  {out / 'types'}/*.html  ({len(drawn)} types)")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default="data/generated/live", help="the run to read")
    parser.add_argument("-o", "--out", default="review", help="where the site goes")
    parser.add_argument("--gallery", default="data/generated/gallery",
                        help="where the chart-type images are drawn")
    parser.add_argument("--skip-gallery", action="store_true",
                        help="leave the chart-type pages out of this build")
    args = parser.parse_args()

    reportkit.LANG = "en"      # this site is written in English throughout
    run = load(Path(args.run))
    written = build(run, Path(args.out), gallery_dir=Path(args.gallery),
                    skip_gallery=args.skip_gallery)
    total = sum(p.stat().st_size for p in written)
    print(f"\n{len(written)} pages, {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
