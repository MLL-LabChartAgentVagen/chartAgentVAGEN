"""Human-readable views of what a stage produced: a terminal summary and a diagram page.

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
    lines = [f"scenario   {schema.scenario_title}", f"           {schema.data_context}", ""]
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
