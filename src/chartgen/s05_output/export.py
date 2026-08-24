"""Turning records into training targets.

Nine targets, one set of tuples. Seven of them read the same list of marks and
differ only in which direction the question runs and which marks are eligible; one
reads the page-element geometry and one the legend. Adding a target is adding a
projection, not a pipeline run.

Two things about the exported form are parameters rather than properties of the
record, because they are choices about what to ask a model rather than facts about
what was drawn:

    key_scope     how much of a mark's address to hand over -- what is inside the
                  plotting area, plus the panel it sits in, plus what only colour says
    granularity   one file per figure, per page, or per batch

Both are written into the artifact. A key the model returns has to land back on a
mark, and it cannot if the scope it was asked under is not recorded.

This module imports the record interface and the shared helpers, and nothing else.
A record that needed a stage module to be interpreted would not be self-sufficient.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Literal, Sequence

from ..common.geometry import Box
from ..interfaces.record import Mark, Record
from ..registry.channels import (
    RELATIVE_TOLERANCE, printed_tolerance, tolerance as tolerance_for,
)

KeyScope = Literal["mark", "panel", "full"]
Granularity = Literal["figure", "page", "batch"]
Format = Literal["json", "markdown", "both"]

#: Export settings a benchmark asks for, by name. A preset is these parameters and
#: nothing else: the record does not change, only which projection is taken and how
#: it is written out -- which is what keeps one pipeline able to serve more than one
#: benchmark without being shaped by any of them.
#:
#: `parsebench` reads the Charts dimension of ParseBench: one page is one image and
#: one answer, the answer is markdown, every table in it is searched, and a spot check
#: may need three keys to be addressed -- so the page is the unit, the format is
#: markdown, the long table is the only target, and the widest key scope is the one
#: that still names the panel and the colour group.
PRESETS: dict[str, dict[str, object]] = {
    "parsebench": {"granularity": "page", "key_scope": "full", "format": "markdown",
                   "targets": ("grounded_table",)},
}

#: Sources of key segments that name something inside the plotting area.
INSIDE_SOURCES = frozenset({"axis_tick", "legend", "inline_label", "heading", "not_shown"})

#: Sources of key segments carried by appearance rather than by any text.
APPEARANCE_SOURCES = frozenset({"colour_only", "mark_shape", "hatch"})

#: How many points the spot-check target asks for, matching the benchmark it aligns to.
SPOT_CHECKS = 10

#: The eight targets that are asked for by name. `key_source` is the ninth and
#: is always written: a key handed over under an unknown scope lands on no mark,
#: so where each of its segments was read from is part of the key rather than a
#: target a run may leave out.
TARGETS: tuple[str, ...] = (
    "grounded_table", "spot_check", "mark_locate", "mark_read", "drilldown",
    "page_elements", "legend_binding", "caption",
)


# ---------------------------------------------------------------- the exported key

def panel_title(record: Record, panel_id: str) -> str:
    """The name drawn above one panel, verbatim.

    Taken from the text that was actually drawn, which is what makes "the key must
    be copyable off the page" hold without anyone having to arrange it.
    """
    for element in record.elements:
        if element.panel_id == panel_id and element.category in ("title", "subtitle"):
            return element.text
    return ""


def exported_key(mark: Mark, record: Record, scope: KeyScope) -> tuple[str, ...]:
    """A mark's address, at the scope this export was asked for.

    A panel dimension is only added when the panel carries a title: without one
    there is nothing on the page for that segment to be read off, and a key that
    cannot be read off the page cannot be checked against it.
    """
    sources = mark.key_src or ("axis_tick",) * len(mark.key)
    inside = tuple(s for s, kind in zip(mark.key, sources) if kind in INSIDE_SOURCES)
    appearance = tuple(s for s, kind in zip(mark.key, sources) if kind in APPEARANCE_SOURCES)
    if scope == "mark":
        return inside
    title = panel_title(record, mark.panel_id)
    lead = (title,) if title else ()
    return lead + inside + (appearance if scope == "full" else ())


def key_sources(mark: Mark, record: Record, scope: KeyScope) -> tuple[str, ...]:
    sources = mark.key_src or ("axis_tick",) * len(mark.key)
    inside = tuple(k for k in sources if k in INSIDE_SOURCES)
    appearance = tuple(k for k in sources if k in APPEARANCE_SOURCES)
    if scope == "mark":
        return inside
    lead = ("panel_title",) if panel_title(record, mark.panel_id) else ()
    return lead + inside + (appearance if scope == "full" else ())


def value_column(record: Record, mark: Mark) -> str:
    """What to call the quantity this mark carries, in a question about it.

    The axis title first, because that is what the page says. A column identifier is
    the fallback rather than the answer: `turnaround_days` appears nowhere on the
    image, and a query written in it asks the reader to know the table.
    """
    axis = record.panel(mark.panel_id).axis(mark.value_axis)
    if axis is None:
        return "value"
    return axis.label or axis.column or "value"


def describe(mark: Mark, record: Record, scope: KeyScope) -> str:
    """A mark in words, which is the query side of every directed probe.

    A mark whose key holds a segment nothing on the page names -- a scatter point is
    addressed by a row identifier -- is described by its coordinates instead. Asking
    for `row_00317` would be asking a question whose answer is nowhere on the image,
    which is a question with no right answer rather than a hard one.
    """
    if "not_shown" in mark.key_src:
        pairs = ", ".join(f"{k} {v:g}" for k, v in sorted(mark.values.items()))
        named = [s for s, kind in zip(mark.key, mark.key_src) if kind != "not_shown"]
        return f"{' '.join(named)} the point at {pairs}".strip()
    return f"{' '.join(exported_key(mark, record, scope))} {value_column(record, mark)}".strip()


def _value(mark: Mark) -> float:
    """The number a value target asks for.

    The record stage wrote down which entry that is, beside deciding whether it can
    be read at all. Picking one here instead would ask a wedge for its value, which
    its angle does not give.
    """
    if mark.value_key and mark.value_key in mark.values:
        return float(mark.values[mark.value_key])
    for key in ("value", "count", "median", "y", "max"):
        if key in mark.values:
            return float(mark.values[key])
    return float(next(iter(mark.values.values()), 0.0))


def _box(box: Box) -> list[float]:
    return [round(v, 2) for v in box.as_tuple()]


# ---------------------------------------------------------------- the targets

@dataclass
class FigureTargets:
    """Every target one figure yields."""

    figure_id: str
    variant: int
    page_id: str
    image_path: str
    image_size: tuple[int, int]
    key_scope: str
    caption: str = ""
    #: The figure number and title that were drawn on the image, which is what names
    #: this figure's table in a page document. Empty when neither was written.
    heading: str = ""
    grounded_table: list[dict] = field(default_factory=list)
    spot_check: list[dict] = field(default_factory=list)
    mark_locate: list[dict] = field(default_factory=list)
    mark_read: list[dict] = field(default_factory=list)
    drilldown: list[dict] = field(default_factory=list)
    page_elements: list[dict] = field(default_factory=list)
    legend_binding: list[dict] = field(default_factory=list)
    key_source: list[dict] = field(default_factory=list)


def figure_heading(record: Record) -> str:
    """What this figure's table is called in a page document.

    The figure number and the title, taken from the text that was actually drawn on
    the image. That is what makes the heading usable as an address: a reader looking
    at the page can read it off, which the file identifier is not.
    """
    parts = [element.text for category in ("figure_number", "title")
             for element in record.elements
             if element.category == category and element.text and not element.panel_id]
    return ". ".join(parts)


def build(record: Record, *, key_scope: KeyScope = "mark",
          base_tolerance: float = RELATIVE_TOLERANCE) -> FigureTargets:
    """Every target of one figure, from the record alone."""
    out = FigureTargets(record.figure_id, record.variant, record.page_id,
                        record.image_path, record.image_size, key_scope, record.caption,
                        figure_heading(record))
    for mark in record.marks:
        key = list(exported_key(mark, record, key_scope))
        row = {"key": key, "values": {k: round(v, 6) for k, v in mark.values.items()},
               "box": _box(mark.box), "rows": mark.rows, "readable": mark.readable,
               "labeled": mark.labeled}
        out.grounded_table.append(row)
        out.mark_locate.append({"query": describe(mark, record, key_scope),
                                "box": _box(mark.box)})
        out.key_source.append({"key": key,
                               "sources": list(key_sources(mark, record, key_scope))})
        if mark.rows is not None:
            out.drilldown.append({"query": describe(mark, record, key_scope),
                                  "rows": mark.rows})
        if mark.readable:
            out.mark_read.append({"box": _box(mark.box), "value": round(_value(mark), 6)})

    for mark in [m for m in record.marks if m.readable][:SPOT_CHECKS]:
        entry = {"key": list(exported_key(mark, record, key_scope)),
                 "value": round(_value(mark), 6),
                 "tolerance": tolerance_for(mark.labeled, base_tolerance),
                 "box": _box(mark.box)}
        if mark.label_text:
            # A value that was printed is matched exactly, so what was printed is the
            # answer -- down to how it was written. Compared as a number instead, the
            # only answer anyone can read off the page is the rounded one, so the
            # tolerance is the rounding and nothing more: a bar of 4.86 labelled "5"
            # is answered with 5, and demanding 4.86 would mark that wrong.
            entry["printed"] = mark.label_text
            entry["tolerance"] = printed_tolerance(mark.label_text, _value(mark),
                                                   base_tolerance)
        out.spot_check.append(entry)

    # Tick labels are recorded but not exported here: the page-element target speaks
    # the benchmark's vocabulary, in which the whole chart is one Picture. Where a key
    # was read from is answered by the key-source target instead.
    out.page_elements = [{"box": _box(e.box), "category": e.category, "text": e.text}
                         for e in record.elements if e.category != "axis_tick"]
    out.legend_binding = [{"entry": e.maps_to_category, "panels": list(e.applies_to_panels)}
                          for e in record.legend]
    return out


# ---------------------------------------------------------------- grouping and writing

def merge_page_elements(units: Sequence[FigureTargets]) -> list[dict]:
    """One list of page elements per page, without repeats.

    Two figures on one page each know their own text blocks and neither knows the
    other's. Exporting them separately leaves each one's target missing half the
    page, which reads as a labelling error rather than as a split view.
    """
    seen: dict[tuple, dict] = {}
    for unit in units:
        for element in unit.page_elements:
            seen.setdefault((tuple(element["box"]), element["category"], element["text"]),
                            element)
    return list(seen.values())


def name_of(unit: FigureTargets) -> str:
    """What one figure's file is called. The style version is part of it: a figure
    is drawn more than once on purpose, and two versions writing to one name would
    leave one of the pair on disk."""
    return f"{unit.figure_id}_v{unit.variant}"


def group(units: Sequence[FigureTargets], granularity: Granularity) -> dict[str, list]:
    if granularity == "figure":
        return {name_of(u): [u] for u in units}
    if granularity == "batch":
        return {"batch": list(units)}
    out: dict[str, list] = defaultdict(list)
    for unit in units:
        out[unit.page_id or name_of(unit)].append(unit)
    return dict(out)


def as_markdown(name: str, units: Sequence[FigureTargets]) -> str:
    """One page as a document: a heading and a long table per figure.

    The heading is what tells two figures on one page apart. Side by side they carry
    the same category names, so a table without its own heading collides with the one
    beside it and neither can say which figure a row came from. It is written as a
    markdown heading and it carries the figure number and title that were drawn on the
    image -- the identifier `f08_v0` names a file and appears on the page nowhere, so
    a reader given the image could not have produced it.

    Every key segment gets its own column. A key folded into one cell reads as a
    single name, and a mark addressed by a panel, a category and a colour group is
    three names -- which is the form a long table exists to carry.
    """
    lines = [f"# {name}", ""]
    for unit in units:
        width = max((len(row["key"]) for row in unit.grounded_table), default=1)
        keys = [f"key {i + 1}" for i in range(width)]
        # The heading carries what is drawn on the image and nothing else. The caption
        # is a target of its own and says what cannot be read off the image, so a
        # document that folds it into the heading is asking to be produced from
        # something the reader was never shown.
        lines += [f"## {unit.heading or name_of(unit)}", "",
                  "| " + " | ".join([*keys, "value", "box", "rows", "readable"]) + " |",
                  "|" + "---|" * (width + 4)]
        for row in unit.grounded_table:
            value = row["values"].get("value", next(iter(row["values"].values()), ""))
            key = list(row["key"]) + [""] * (width - len(row["key"]))
            lines.append("| " + " | ".join(
                [*key, str(value), str(row["box"]), str(row["rows"]),
                 "yes" if row["readable"] else "no"]) + " |")
        lines.append("")
    lines += ["## page elements", "", "| box | category | text |", "|---|---|---|"]
    for element in merge_page_elements(units):
        lines.append(f"| {element['box']} | {element['category']} | {element['text']} |")
    return "\n".join(lines) + "\n"


def with_whole_page(units: Sequence[FigureTargets]) -> list[FigureTargets]:
    """Give every figure the page elements of the whole page it sits on.

    A figure knows its own text blocks and none of its neighbour's. Written out as
    it stands, its page-element target names half of what is on the page, and half a
    page of labels is not a smaller task -- it is a wrong answer. Merging by page is
    therefore not a property of the export granularity: it holds at every granularity,
    because it is a fact about the image the target points at.
    """
    by_page: dict[str, list[FigureTargets]] = defaultdict(list)
    for unit in units:
        by_page[unit.page_id].append(unit)
    for page, members in by_page.items():
        if not page or len(members) < 2:
            continue
        merged = merge_page_elements(members)
        for unit in members:
            unit.page_elements = merged
    return list(units)


def settings(get, preset: str | None = None) -> dict:
    """The four export parameters, with a preset filled in under whatever is set.

    `get` reads one configuration entry. A preset supplies a default for each of the
    four; anything set explicitly beside it wins, so a preset can be taken and one of
    its parts overridden without copying the rest.
    """
    base = dict(PRESETS.get(preset or "", {}))
    for key, fallback in (("key_scope", "mark"), ("granularity", "figure"),
                          ("format", "json"), ("targets", TARGETS)):
        value = get(key)
        if value is None:
            value = base.get(key, fallback)
        base[key] = value
    return base


def export(records: Sequence[Record], out_dir: str | Path, *,
           key_scope: KeyScope = "mark", granularity: Granularity = "figure",
           base_tolerance: float = RELATIVE_TOLERANCE,
           targets: Iterable[str] = TARGETS,
           format: Format = "json") -> list[Path]:
    """Write the training targets and return what was written.

    `format` is what the answer is asked for in, and it is separate from the
    granularity: one page as a document and one page as a structured payload are the
    same records projected twice.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    units = with_whole_page(
        [build(r, key_scope=key_scope, base_tolerance=base_tolerance) for r in records])
    wanted = set(targets)

    written: list[Path] = []
    for name, members in group(units, granularity).items():
        if format in ("json", "both"):
            payload = {
                "name": name,
                "key_scope": key_scope,
                "granularity": granularity,
                "figures": [_selected(u, wanted) for u in members],
                "page_elements": merge_page_elements(members),
            }
            path = out_dir / f"{name}.json"
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
            written.append(path)
        if format in ("markdown", "both"):
            page = out_dir / f"{name}.md"
            page.write_text(as_markdown(name, members), encoding="utf-8")
            written.append(page)
    return written


def _selected(unit: FigureTargets, wanted: set[str]) -> dict:
    """One figure's targets, with the ones this run does not ask for left out.

    Leaving a target out is how an ablation is run: the record does not change, the
    projection is simply not taken.
    """
    raw = asdict(unit)
    keep = {"figure_id", "variant", "page_id", "image_path", "image_size", "key_scope",
            "key_source"}
    return {k: v for k, v in raw.items() if k in keep or k in wanted}
