"""Writing the words that get drawn on a batch of figures.

The pipeline's second and last model call. It runs after the figures are chosen,
and it chooses nothing: no feasibility is judged, no view is picked, and not one
value, key or box comes out of it. What comes out is the text that gets painted on
the page -- a title, a subtitle, a unit, and a readable name for every column.

Why every figure and not only the ones built from an intent. The intent split is
about the caption, which is a training target and says what cannot be read off the
image; a title is drawn on the image and every figure needs one. Filling three
titles from intents and five from a template would put two audibly different
registers in the corpus and teach the model that one register means one kind of
figure -- a signal we would have manufactured ourselves. A template title is also
guessable from the axes, and the point of recording the title block is that the
unit is often written nowhere else.

One call per scenario with every figure in it, not one call per figure: the batch
shares a scenario and its column names have to agree across figures.

Two things are checked on the way back. No numbers, because a title is painted on
the image and becomes ground truth there -- "wait times fell sharply" would be a
claim about data that may not hold. And a prose name for every column, because
without one the axis says `wait_minutes`, and axis ticks are where a reader gets
the key from.
"""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Any, Protocol, Sequence

from ..interfaces.figure import FigureSpec, TextBlock
from ..interfaces.table import TableSchema, aggregate_phrase

#: Numbers a title may contain: a year, a quarter, an ordinal decade. Everything
#: else is a claim about the data.
ALLOWED_NUMBER = re.compile(r"^(19|20)\d{2}$|^[Qq][1-4]$|^\d{2,4}s$")

WORD = re.compile(r"[A-Za-z]*\d[A-Za-z0-9]*")


class Writing(Protocol):
    def json(self, system: str, user: str, *, schema: dict) -> dict: ...


class TitleRejected(ValueError):
    """The answer would have painted something onto the image that is not true."""


def title_schema(columns: Sequence[str]) -> dict[str, Any]:
    """The output contract, built around the columns this batch actually draws.

    The names are declared one property at a time rather than as an open map.
    Structured output requires every object in a schema to be closed, so a map of
    arbitrary keys is refused before the request is sent -- and a call that can never
    be made is a fallback that always runs, silently.
    """
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["figures", "column_names"],
        "properties": {
            "figures": {"type": "array", "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["figure_id", "title", "subtitle", "unit"],
                "properties": {
                    "figure_id": {"type": "string"},
                    "title": {"type": "string"},
                    "subtitle": {"type": "string"},
                    "unit": {"type": "string"},
                }}},
            "column_names": {
                "type": "object",
                "additionalProperties": False,
                "required": list(columns),
                "properties": {c: {"type": "string"} for c in columns},
            },
        },
    }

SYSTEM = """You name figures. Given a scenario and a list of figures described by
their columns, you write a title, a subtitle and a unit for each, plus a readable
name for every column.

You name what is drawn. You never state a finding, a direction or a magnitude, and
you never write a number other than a year or a quarter -- the text you write is
painted onto the image and is read as ground truth there. Reply with JSON matching
the schema, no explanation and no code fences."""

USER = """## Scenario

{title}

{context}

## Columns

{declarations}

## Figures

{figures}

## What to write

| Field | Content |
|---|---|
| `title` | What the figure shows. Name the quantity and how it is broken down |
| `subtitle` | The qualifier: what each mark covers, over what period |
| `unit` | The unit the values are in, as it would be written on an axis |
| `column_names` | One readable name per column below, used on axes and in legends |

Columns to name: {columns}

Rules: no numbers except years and quarters; no findings, comparisons or
directions; no chart-type words; `title` at most 48 characters and `subtitle` at
most 60, counted as characters rather than words because that is what has to fit
across the width of the image."""


# ---------------------------------------------------------------- the request

#: Category values written out before the list is cut short. Enough for the shape of
#: the column to be visible; a forty-value column would otherwise fill the request
#: with names that no title mentions.
MAX_VALUES = 12


def declare(column) -> str:
    """One column as its declaration reads. Declarations only -- no value ever
    computed from the rows, because a title is painted on the image and a number in
    it is read as a claim about the data."""
    facts: list[str] = []
    if column.kind == "category":
        shown = ", ".join(column.values[:MAX_VALUES])
        if len(column.values) > MAX_VALUES:
            shown += f", and {len(column.values) - MAX_VALUES} more"
        facts.append(shown or f"{column.cardinality} values")
        if column.ordered:
            facts.append(f"ordered={column.ordered}")
    elif column.kind == "time":
        facts.append(f"{column.start} to {column.end}, {column.freq}")
    else:
        if column.unit:
            facts.append(f"unit {column.unit}")
        facts.append("additive" if column.additive else "non-additive")
    if column.parent:
        facts.append(f"within {column.parent}")
    if column.derived_from:
        facts.append(f"derived from {column.derived_from}")
    if column.group:
        facts.append(f"group {column.group}")
    return f"| `{column.name}` | {column.kind} | " + "; ".join(facts) + " |"


def declarations(specs: Sequence[FigureSpec], schema: TableSchema) -> str:
    """Every column the batch draws, as it was declared.

    The request used to carry column identifiers and nothing else, which left the
    model to guess what `processing_center` holds. What a column is called on an
    axis is exactly the question being asked, so the declarations are the input that
    answers it: the values a category takes, the window and step of a time column,
    the unit and additivity of a measure, and where a column sits in its hierarchy.
    None of it is a data value.
    """
    rows = [declare(schema.column(c)) for c in columns_of(specs) if schema.has(c)]
    return "\n".join(["| Column | Kind | Declared as |", "|---|---|---|", *rows])


def _view_lines(view, schema: TableSchema) -> tuple[str, str]:
    """One view as two lines, without the panel it is drawn in.

    Separated from the panel so that panels drawing the same thing can share one
    description. Small multiples repeat one view across four panels, and printed per
    panel the same two lines are sent four times.
    """
    b = view.binding
    units = ", ".join(sorted({schema.column(m).unit for m in b.measures} - {None, ""}))
    body = (f"{b.chart_type}, grouped by {', '.join(b.group_columns) or 'nothing'}, "
            f"{b.aggregate}({', '.join(b.measures) or '*'})"
            + (f", unit {units}" if units else "")
            # What tells this view apart from the other one in its plotting area. Two
            # overlaid views group by the same columns, so without it they arrive as
            # two identical lines differing only in chart type -- and naming a chart
            # type is the one thing the answer may not do.
            + (f", labelled {view.key_prefix[0]!r}" if view.prefix_names_a_series else ""))
    # Where each key segment is read from is what a subtitle is about: it says what
    # one mark covers, and a column read off a legend covers something different
    # from one read off a panel title.
    read = ""
    if b.key_sources and b.group_columns:
        read = "reads " + ", ".join(f"{c} off the {k.replace('_', ' ')}"
                                    for c, k in zip(b.group_columns, b.key_sources))
    return body, read


#: What a source line may run to before it is cut. Measured on the batch it replaced:
#: a scenario title is a sentence, and sixty of ninety-six source lines were cut short
#: on the page -- most of them in the middle of a word.
SOURCE_LIMIT = 72


def source_line(schema: TableSchema) -> str:
    """Where the figure says its numbers came from.

    A source line on a real page names a body and a collection, not the question the
    page is answering. The scenario title is that question and runs to a sentence, so
    the pool entry is used where there is one: it is shorter, and it names the same
    table.
    """
    origin = schema.origin
    named = ", ".join(p for p in (origin.topic, origin.domain) if p)
    text = named or schema.scenario_title
    if len(text) > SOURCE_LIMIT:
        text = text[:SOURCE_LIMIT].rstrip(" ,;") + "…"
    return f"Source: {text}"


def describe(spec: FigureSpec, schema: TableSchema) -> str:
    """One figure as the model sees it: columns, aggregates, layout. No values."""
    lines = [f"- `{spec.figure_id}`"]
    shared: dict[tuple[str, str], list[str]] = {}
    for panel in spec.panels:
        for view in panel.views:
            shared.setdefault(_view_lines(view, schema), []).append(panel.panel_id)
    for (body, read), where in shared.items():
        name = where[0] if len(where) == 1 else f"{where[0]}-{where[-1]} each"
        lines.append(f"    {name}: {body}")
        if read:
            lines.append(f"    {name} {read}")
    for panel in spec.panels:
        for text in panel.texts:
            lines.append(f"    {panel.panel_id} is titled {text.text!r}")
    for block in spec.texts:
        lines.append(f"    its {block.role} is already fixed as {block.text!r}")
    if spec.relation:
        lines.append(f"    the panels are related by: {spec.relation}")
    if spec.source.kind == "intent" and spec.source.intent_index is not None:
        intent = schema.intents[spec.source.intent_index]
        lines.append(f"    drawn to answer: {intent.sentence}")
    return "\n".join(lines)


def request(specs: Sequence[FigureSpec], schema: TableSchema) -> str:
    return USER.format(title=schema.scenario_title, context=schema.data_context,
                       declarations=declarations(specs, schema),
                       figures="\n".join(describe(s, schema) for s in specs),
                       columns=", ".join(f"`{c}`" for c in columns_of(specs)))


# ---------------------------------------------------------------- the check

def numbers_in(text: str) -> list[str]:
    """Tokens with a digit in them that a title is not allowed to carry."""
    return [w for w in WORD.findall(text) if not ALLOWED_NUMBER.match(w)]


def columns_of(specs: Sequence[FigureSpec]) -> list[str]:
    """Every column the batch draws, which is every column that needs a prose name."""
    return sorted({c for s in specs for v in s.views
                   for c in (*v.binding.group_columns, *v.binding.measures)})


def validate(payload: dict, specs: Sequence[FigureSpec]) -> dict:
    """Reject an answer that would paint a claim, or that leaves a column unnamed."""
    wanted = {s.figure_id for s in specs}
    got = {str(f.get("figure_id")) for f in payload.get("figures", [])}
    if got != wanted:
        raise TitleRejected(f"one entry per figure is needed: missing {sorted(wanted - got)}, "
                            f"unexpected {sorted(got - wanted)}")
    for entry in payload["figures"]:
        for field in ("title", "subtitle"):
            if bad := numbers_in(str(entry.get(field, ""))):
                raise TitleRejected(
                    f"{entry['figure_id']} {field} contains {bad}: a title is painted "
                    "on the image and is read as ground truth there, so it may name "
                    "what is drawn but never state a value")
    # Two figures with one title is one name for two different pictures. The batch is
    # written in one call precisely so this can be checked: the model sees all sixteen
    # at once, and a title that does not tell its figure from another one is an answer
    # that has not done its job.
    seen: dict[tuple[str, str], str] = {}
    for entry in payload["figures"]:
        pair = (str(entry.get("title", "")).strip().lower(),
                str(entry.get("subtitle", "")).strip().lower())
        if pair in seen:
            raise TitleRejected(
                f"{entry['figure_id']} and {seen[pair]} were given the same title and "
                f"subtitle ({entry.get('title')!r}). Every figure needs a title that "
                "tells it from the others in this batch")
        seen[pair] = str(entry["figure_id"])
    names = payload.get("column_names") or {}
    if not isinstance(names, dict):
        raise TitleRejected("column_names has to be a mapping from column to name")
    unnamed = [c for c in columns_of(specs) if not str(names.get(c, "")).strip()]
    if unnamed:
        raise TitleRejected(
            f"these columns were left unnamed: {unnamed}. An axis tick and a legend "
            "entry are where a reader gets a key from, so a column drawn under its "
            "raw name is a key that cannot be copied off the page")
    return payload


# ---------------------------------------------------------------- the fallback

def template(spec: FigureSpec, schema: TableSchema) -> tuple[str, str, str]:
    """Titles assembled by rule. This is what runs with no model reachable, so
    that development and the end-to-end tests do not need one -- it is not an
    option a batch would be generated under."""
    parts, units = [], []
    for view in spec.views:
        b = view.binding
        # No measure at all is the counting aggregate, and its phrase already says
        # what is counted: naming a column as well gives "the number of records
        # records".
        measure = b.measures[0] if b.measures else ""
        by = " and ".join(b.group_columns) or "all rows"
        parts.append(aggregate_phrase(b.aggregate, measure.replace("_", " "))
                     + f" by {by}".replace("_", " ").rstrip())
        if schema.has(measure) and schema.column(measure).unit:
            units.append(schema.column(measure).unit)
    title = " and ".join(dict.fromkeys(parts))
    title = f"{title[:1].upper()}{title[1:]}"
    detail = spec.relation or ("one panel" if len(spec.panels) == 1 else "panels")
    subtitle = f"{spec.figure_id}, {detail.replace('_', ' ')}"
    return (title, subtitle, " and ".join(dict.fromkeys(units)))


def template_names(schema: TableSchema) -> dict[str, str]:
    return {c.name: c.name.replace("_", " ").title() for c in schema.columns}


# ---------------------------------------------------------------- the entry point

def default_llm(config) -> Writing | None:
    """The model this call goes to, or nothing when there is none to reach.

    The same client and the same on-disk cache the data call uses, so one input
    gives one batch of titles however many times a run is repeated.
    """
    if not config.get("llm.titles", True):
        return None
    try:
        from llmkit import LLM, reachable

        model = str(config.get("llm.model"))
        if not reachable(model):
            return None
        return LLM(model=model, max_tokens=int(config.get("llm.max_tokens", 8000)),
                   effort=config.get("llm.effort", "high"),
                   cache_dir=config.get("llm.cache_dir"))
    except Exception:  # noqa: BLE001 -- no vendor package, no key: use the templates
        return None


def write(specs: Sequence[FigureSpec], schema: TableSchema, *,
          llm: Writing | None = None, retries: int = 2,
          report: list[str] | None = None) -> list[FigureSpec]:
    """Give every figure in the batch its text. One call, or the template fallback.

    `report` collects what happened, because "a model wrote these" and "the templates
    did" are different corpora and an artifact that cannot say which it is cannot be
    compared with another one.
    """
    payload: dict | None = None
    if llm is not None:
        feedback = ""
        for _ in range(retries + 1):
            try:
                payload = validate(llm.json(SYSTEM, request(specs, schema) + feedback,
                                            schema=title_schema(columns_of(specs))), specs)
                break
            except TitleRejected as exc:
                feedback = f"\n\n## The previous answer was rejected\n\n{exc}\n\nWrite it again."
                payload = None
            except Exception as exc:  # noqa: BLE001 -- unreachable model: use templates
                _note(report, f"the call failed, so the templates wrote the text: {exc!r}")
                payload = None
                break

    _note(report, "written by the model" if payload is not None
          else "written from the templates")
    names = dict(template_names(schema))
    written: dict[str, tuple[str, str, str]] = {}
    if payload is not None:
        names.update({k: str(v) for k, v in payload["column_names"].items()})
        written = {str(f["figure_id"]): (str(f["title"]), str(f["subtitle"]), str(f["unit"]))
                   for f in payload["figures"]}

    out = []
    for i, spec in enumerate(specs, 1):
        title, subtitle, unit = written.get(spec.figure_id) or template(spec, schema)
        out.append(replace(spec, column_names=names,
                           texts=_blocks(spec, title, subtitle, unit,
                                         number=f"Figure {i}",
                                         source=source_line(schema))))
    return out


def _note(report: list[str] | None, line: str) -> None:
    if report is not None:
        report.append(line)


def _blocks(spec: FigureSpec, title: str, subtitle: str, unit: str,
            number: str = "", source: str = "") -> tuple[TextBlock, ...]:
    """The text this figure will carry: what was written for it, what numbers it, what
    says where its data came from, and anything view selection had already fixed.

    A block that is already there stays. When two figures share a page, what tells
    their rows apart is the window written on each of them -- that is a fact about
    which rows the figure holds, not a phrase to be rewritten.

    The figure number and the source line are not written by a model. A number is
    assigned, and a source names the table the figure was drawn from; both are facts
    about the batch, and a model asked for them would invent them.
    """
    kept = {b.role: b for b in spec.texts if b.scope == "figure"}
    written = [TextBlock("figure_number", number, "figure", "above"),
               TextBlock("title", title, "figure", "above"),
               TextBlock("subtitle", subtitle, "figure", "above"),
               TextBlock("unit", unit, "figure", "above"),
               TextBlock("source", source, "figure", "below")]
    return tuple(kept.get(b.role, b) for b in written if kept.get(b.role, b).text)
