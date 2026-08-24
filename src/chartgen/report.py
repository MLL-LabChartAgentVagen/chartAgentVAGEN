"""Human-readable views of what a stage produced: a terminal summary and a diagram page.

One section per stage. A new stage adds a section here rather than a script of its
own, so that whatever a run produced can be read without knowing which tool to run.

A table schema holds three graphs that JSON hides: the dimension hierarchies (a
forest), the dependencies between numeric columns (a directed graph), and which
analysis intent points at which columns. `page()` writes all three as Mermaid,
which renders in most Markdown viewers with no extra dependency; `summary()` and
`tree()` put the same content in a terminal.

Nothing here is on the production path, but the data stage writes the page beside
every schema it saves, so a run always leaves something to look at.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .interfaces.figure import FigureSpec
from .interfaces.record import Record
from .interfaces.table import Column, FactTable, TableSchema
from .s01_data.validate import densest_cross, feasibility

MEASURE_SHAPE = "([{label}])"
CATEGORY_SHAPE = "[{label}]"
TIME_SHAPE = "[/{label}/]"

#: Rows of the generated table to show in the terminal summary.
PREVIEW_ROWS = 5


# ---------------------------------------------------------------- diagrams

def _node(column: Column) -> str:
    if column.kind == "measure":
        return column.name + MEASURE_SHAPE.format(label=f"{column.name}<br/>{column.unit}")
    label = f"{column.name}<br/>{column.cardinality}"
    shape = TIME_SHAPE if column.kind == "time" else CATEGORY_SHAPE
    return column.name + shape.format(label=label)


def hierarchy(schema: TableSchema) -> str:
    """Dimension groups as a forest: a chain of boxes per group.

    A solid edge is a declared parent, a dashed edge a calendar field read off a
    time column.
    """
    lines = ["flowchart LR"]
    for group in schema.groups:
        lines.append(f"  subgraph {group.name}")
        lines += [f"    {_node(schema.column(name))}" for name in group.columns]
        lines.append("  end")
    for column in schema.columns:
        if column.parent:
            lines.append(f"  {column.parent} --> {column.name}")
        elif column.derived_from:
            lines.append(f"  {column.derived_from} -.-> {column.name}")
    return "\n".join(lines)


def dependencies(schema: TableSchema) -> str:
    """Numeric columns and what each one is computed from."""
    return "\n".join(["flowchart LR", *(f"  {_node(c)}" for c in schema.measures),
                      *(f"  {src} --> {dst}" for src, dst in schema.dependencies)])


def intents(schema: TableSchema) -> str:
    """Which analysis intent points at which columns."""
    lines = ["flowchart LR"]
    for intent in schema.intents:
        node = f"i{intent.index}"
        lines.append(f'  {node}(["{intent.family}<br/>{intent.aggregate}"])')
        lines += [f"  {node} --> {name}" for name in intent.columns]
    return "\n".join(lines)


def origin_line(schema: TableSchema) -> list[str]:
    """Which entry of the domain pool this scenario was written for.

    Worth a line of its own because nothing else says it: the title is the model's
    and names neither the sub-topic nor the tier it was drawn under, so without this
    a batch cannot be described as covering one part of the pool and not another.
    """
    origin = schema.origin
    if not origin.domain:
        return []
    cell = " / ".join(x for x in (origin.subject, origin.register) if x)
    return ["", f"Drawn from `{origin.domain_id}` {origin.domain} "
                f"-- {origin.topic}"
                + (f" ({cell})" if cell else "")
                + f", {origin.complexity_tier}"]


def markdown(schema: TableSchema, *, max_tier: int = 3) -> str:
    """The three diagrams, plus the two numbers that decide whether a scenario is
    worth rendering: which chart families it can draw, and how thinly its rows
    spread over the densest pair of category columns."""
    drawable = feasibility(schema, max_tier=max_tier)
    pair, density = densest_cross(schema)
    families = ["| family | drawable |", "|---|---|"]
    families += [f"| {f} | {'yes' if ok else 'no'} |" for f, ok in drawable.families.items()]
    cross = (f"{pair[0]} x {pair[1]} at {density:.1f} rows per cell"
             if pair else "no two category columns cross into a chartable size")
    return "\n".join([
        f"# {schema.scenario_title}", "", schema.data_context, "",
        f"`{schema.scenario_id}` -- {schema.n_rows} rows, {len(schema.columns)} columns",
        *origin_line(schema),
        "", "## Dimensions", "", "```mermaid", hierarchy(schema), "```",
        "", "## Numeric columns", "", "```mermaid", dependencies(schema), "```",
        "", "## Intents", "", "```mermaid", intents(schema), "```",
        "", "## What can be drawn", "", *families,
        "", f"Densest two-column cross: {cross}.",
        *(["", "Gaps:", ""] + [f"- {g}" for g in drawable.gaps] if drawable.gaps else []),
    ])


def page(schema: TableSchema, path: str | Path, *, max_tier: int = 3) -> Path:
    """Write the diagram page beside the schema it describes."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown(schema, max_tier=max_tier) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------- terminal

def tree(schema: TableSchema) -> str:
    """The dimension forest and the numeric columns, short enough for a terminal."""
    out: list[str] = []
    for group in schema.groups:
        out.append(group.name)
        for i, name in enumerate(group.columns):
            column = schema.column(name)
            lead = "  " * (1 + _depth(schema, column))
            out.append(f"{lead}{'`-' if i == len(group.columns) - 1 else '|-'} "
                       f"{name} ({column.cardinality})")
    out.append("measures")
    for column in schema.measures:
        sources = [a for a, b in schema.dependencies if b == column.name]
        out.append(f"  |- {column.name} [{column.unit}] "
                   f"{'<- ' + ', '.join(sources) if sources else 'root'}")
    return "\n".join(out)


def _depth(schema: TableSchema, column: Column) -> int:
    depth, cursor = 0, column
    while cursor.parent:
        cursor, depth = schema.column(cursor.parent), depth + 1
    return depth


def summary(table: FactTable, schema: TableSchema, *, max_tier: int = 3) -> str:
    """Everything the data stage decided, in one screen: the scenario, the columns
    it declared, the intents it bound, what those declarations can draw, and the
    first rows of the table that came out."""
    drawable = feasibility(schema, max_tier=max_tier)
    lines = [f"scenario   {schema.scenario_title}", f"           {schema.data_context}"]
    if schema.origin.domain:
        cell = " / ".join(x for x in (schema.origin.subject, schema.origin.register) if x)
        lines.append(f"drawn from {schema.origin.domain} "
                     f"({', '.join(x for x in (schema.origin.topic, cell,
                                               schema.origin.complexity_tier) if x)})")
    lines.append("")
    for group in schema.groups:
        parts = [f"{n}({schema.column(n).cardinality})" for n in group.columns]
        chain = all(schema.column(b).parent == a
                    for a, b in zip(group.columns, group.columns[1:]))
        lines.append(f"dimensions {group.name:12s} " + (" -> " if chain else " . ").join(parts))
    for m in schema.measures:
        deps = [a for a, b in schema.dependencies if b == m.name]
        lines.append(f"measure    {m.name:20s} {str(m.unit):14s} "
                     f"{'additive    ' if m.additive else 'non-additive'} "
                     f"{'from ' + ', '.join(deps) if deps else 'root'}")
    lines.append("")
    for i in schema.intents:
        lines.append(f"intent {i.index + 1}   {i.family:12s} {i.aggregate:6s} "
                     f"{' x '.join(i.columns)}   {i.sentence}")
    lines += ["", "drawable   " + "  ".join(
        f"{f}:{'yes' if ok else 'no '}" for f, ok in drawable.families.items()),
        f"           {drawable.nonempty}/6 families"
        + (f"\n           {drawable.feedback()}" if drawable.gaps else ""),
        "", f"table      {table.n_rows} rows x {len(table.df.columns)} columns",
        table.df.head(PREVIEW_ROWS).to_string(index=False)]
    return "\n".join(lines)


# ---------------------------------------------------------------- view selection

def figure_flow(specs: Sequence["FigureSpec"]) -> str:
    """How each figure was chosen: from an intent, from an anchor, or by drawing."""
    lines = ["flowchart LR"]
    for spec in specs:
        label = "<br/>".join(dict.fromkeys(spec.chart_types))
        lines.append(f'  {spec.figure_id}["{spec.figure_id}<br/>{label}"]')
    for spec in specs:
        if spec.source.kind == "intent" and spec.source.intent_index is not None:
            node = f"i{spec.source.intent_index}"
            lines.append(f'  {node}(["intent {spec.source.intent_index + 1}"])')
            lines.append(f"  {node} --> {spec.figure_id}")
        elif spec.source.anchor_figure_id:
            lines.append(f"  {spec.source.anchor_figure_id} -.{spec.relation}.-> "
                         f"{spec.figure_id}")
        else:
            lines.append(f'  r(["rotation"]) --> {spec.figure_id}')
    return "\n".join(lines)


def figure_table(specs: Sequence["FigureSpec"]) -> list[str]:
    rows = ["| figure | chosen by | relation | layout | types | marks | keys read from |",
            "|---|---|---|---|---|---|---|"]
    for spec in specs:
        marks = sum(len(v.data) for v in spec.views)
        sources = sorted({s for v in spec.views for d in v.data for s in v.key_src(d)})
        rows.append(f"| {spec.figure_id} | {spec.source.kind} | {spec.relation or '-'} | "
                    f"{spec.layout} | {', '.join(dict.fromkeys(spec.chart_types))} | "
                    f"{marks} | {', '.join(sources)} |")
    return rows


def figure_summary(specs: Sequence["FigureSpec"], log: dict | None = None) -> str:
    """What view selection produced, and what it turned away."""
    out = ["## Figures", "", *figure_table(specs), "",
           "```mermaid", figure_flow(specs), "```", ""]
    if log:
        counts = log.get("counts", {})
        out += ["| path | figures |", "|---|---|"]
        out += [f"| {k} | {v} |" for k, v in counts.items()]
        out += ["", f"Density band `{log.get('density_band')}`, family weights "
                    f"`{(log.get('family_weights') or {}).get('preset')}`, "
                    f"titles {'; '.join(log.get('titles') or ['not written'])}.", ""]
        if layout := log.get("layout"):
            out += ["| layout | figures |", "|---|---|"]
            out += [f"| {k.replace('_', ' ')} | {v} |" for k, v in layout.items()] + [""]
        if log.get("rejected"):
            out += ["Candidates turned away:", ""]
            out += [f"- {k}: {v}" for k, v in log["rejected"].items()]
            out.append("")
        if log.get("skipped"):
            out += ["Nothing produced by:", ""] + [f"- {s}" for s in log["skipped"]] + [""]
    return "\n".join(out)


# ---------------------------------------------------------------- records

def readability_by_type(records: Sequence["Record"]) -> list[str]:
    """How many marks keep a value target, per chart type.

    Low is the expected reading for an angle or a colour, and for anything drawn
    densely. It is reported per type so that a figure carrying no value targets is
    read as the rule working rather than as a figure that failed.
    """
    tally: dict[str, tuple[int, int]] = {}
    for record in records:
        for panel in record.panels:
            for chart_type in panel.chart_types:
                marks = [m for m in record.marks if m.panel_id == panel.panel_id]
                seen, ok = tally.get(chart_type, (0, 0))
                tally[chart_type] = (seen + len(marks),
                                     ok + sum(1 for m in marks if m.readable))
    rows = ["| chart type | marks | value targets | share |", "|---|---|---|---|"]
    for name, (seen, ok) in sorted(tally.items()):
        rows.append(f"| {name} | {seen} | {ok} | {ok / seen:.0%} |" if seen else
                    f"| {name} | 0 | 0 | - |")
    return rows


def record_summary(records: Sequence["Record"],
                   dropped: Sequence[tuple[str, str]] = ()) -> str:
    """The self-checks, and what came through them."""
    rows = ["| figure | marks | value targets | box content | value readback | restyled |",
            "|---|---|---|---|---|---|"]
    verdict = lambda v: {True: "pass", False: "FAIL", None: "not run"}[v]
    for record in records:
        readable = sum(1 for m in record.marks if m.readable)
        s = record.selfcheck
        rows.append(f"| {record.figure_id} v{record.variant} | {len(record.marks)} | {readable} | "
                    f"{verdict(s.box_content)} | {verdict(s.value_readback)} | "
                    f"{verdict(s.style_invariant)} |")
    out = ["## Records", "", *rows, "", "### Value targets by chart type", "",
           *readability_by_type(records), ""]
    if dropped:
        out += ["### Figures discarded", ""]
        out += [f"- `{name}`: {why}" for name, why in dropped] + [""]
    return "\n".join(out)


# ---------------------------------------------------------------- targets

def target_summary(records: Sequence["Record"], key_scope: str = "mark") -> str:
    """How much of each training target one batch yields."""
    from .s05_output.export import TARGETS, build

    units = [build(r, key_scope=key_scope) for r in records]
    rows = ["| target | entries |", "|---|---|"]
    for name in (*TARGETS, "key_source"):
        if name == "caption":
            rows.append(f"| caption | {sum(1 for u in units if u.caption)} |")
            continue
        rows.append(f"| {name} | {sum(len(getattr(u, name, [])) for u in units)} |")
    example = next((u for u in units if u.grounded_table), None)
    out = ["## Training targets", "", f"Key scope `{key_scope}`.", "", *rows, ""]
    if example is not None:
        row = example.grounded_table[0]
        out += ["One row of one figure, seen through six of them:", "", "```",
                f"record      key={row['key']} values={row['values']} "
                f"box={row['box']} rows={row['rows']} readable={row['readable']}",
                *[f"{name:12s}{_first(getattr(example, name, []))}"
                  for name in ("grounded_table", "spot_check", "mark_locate",
                               "mark_read", "drilldown", "page_elements")],
                f"{'caption':12s}{example.caption[:110]}", "```", ""]
    return "\n".join(out)


def _first(entries) -> str:
    return str(entries[0]) if entries else "(none)"


# ---------------------------------------------------------------- the whole run

def run_summary(stats: dict) -> str:
    rows = ["| | |", "|---|---|"]
    rows += [f"| {k} | {v} |" for k, v in stats.items() if k != "reasons"]
    out = ["## Run", "", *rows, ""]
    if stats.get("reasons"):
        out += ["What stopped a figure or a candidate:", ""]
        out += [f"- {k}: {v}" for k, v in stats["reasons"].items()] + [""]
    return "\n".join(out)
