"""Pull the piece of parser output that a failure is actually about.

A card that says "the label would not associate" and then shows a whole page of
markdown makes the reader do the search again. This finds the table the value
landed in, the window of rows around it, and where in that table each addressing
label actually sits -- so the card can show the value cell and the key cell side by
side and let the geometry make the argument.

When the key never reached a table at all, the line of page text carrying it is
pulled instead: that is the same fact, in the only place it exists.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from run import Verdict
from tables import Page, Table, label_hits, threshold
from taxonomy import Diagnosis, _label_cells, _value_cells, addressed_cells

#: Rows kept above and below the value's row, and the widest table shown whole.
CONTEXT_ROWS = 3
MAX_COLUMNS = 9


@dataclass
class Cell:
    text: str
    kind: str = ""          # "" | "hit" | "key" | "head"


@dataclass
class Evidence:
    """One excerpt of parser output, marked up for reading."""

    caption: str = ""
    rows: list[list[Cell]] = field(default_factory=list)
    elided_above: bool = False
    elided_right: bool = False
    note: str = ""
    #: Lines of page text carrying a key that never reached a table.
    context: list[str] = field(default_factory=list)


def _window(centre: int, count: int, span: int) -> range:
    low = max(0, centre - span)
    return range(low, min(count, low + 2 * span + 1))


def _columns(table: Table, keep: set[int]) -> tuple[list[int], bool]:
    width = max((len(row) for row in table.rows), default=0)
    if width <= MAX_COLUMNS:
        return list(range(width)), False
    chosen = sorted({0} | keep)
    for index in range(width):
        if len(chosen) >= MAX_COLUMNS:
            break
        if index not in chosen:
            chosen.append(index)
    return sorted(chosen)[:MAX_COLUMNS], True


def _lines_with(page: Page, label: str, bar: float, limit: int = 2) -> list[str]:
    out = []
    for line in page.markdown.splitlines():
        text = line.strip()
        if not text or text.startswith("|") or "<t" in text.lower():
            continue
        if label_hits(label, text, bar):
            out.append(text if len(text) <= 150 else text[:150] + " …")
        if len(out) >= limit:
            break
    return out


def build(verdict: Verdict, page: Page, diagnosis: Diagnosis) -> Evidence:
    """The excerpt for one failing point: where the value went, where the keys went."""
    rule = verdict.rule
    if not page.tables:
        return Evidence(note="整页输出里一张表都没有。")

    hits = _value_cells(rule, page)
    label_cells = _label_cells(rule, page)
    wrong: tuple[int, int] | None = None
    if hits:
        table, row, column = hits[0]
    else:
        counts = {t.index: sum(1 for label in rule.labels
                               for cell in label_cells[label] if cell[0] is t)
                  for t in page.tables}
        table = max(page.tables, key=lambda t: (counts[t.index], -t.index))
        column, row = None, 0
        for label in rule.labels:
            for cell in label_cells[label]:
                if cell[0] is table:
                    row = cell[1]
                    break
        wrong = _addressed_cell(rule, page, table, label_cells, diagnosis)
        if wrong:
            row = wrong[0]

    here = {(cell[1], cell[2]) for label in rule.labels
            for cell in label_cells[label] if cell[0] is table}
    keep = {c for _, c in here}
    if column is not None:
        keep.add(column)
    columns, elided_right = _columns(table, keep)
    kept_rows = _window(row, len(table.rows), CONTEXT_ROWS)

    evidence = Evidence(elided_above=kept_rows.start > 0, elided_right=elided_right)
    order = ([0] if kept_rows.start > 0 else []) + list(kept_rows)
    for r in order:
        line = table.rows[r]
        cells = []
        for c in columns:
            text = line[c] if c < len(line) else ""
            kind = "head" if r == 0 else ""
            if (r, c) in here:
                kind = "key"
            if wrong is not None and (r, c) == wrong:
                kind = "wrong"
            if column is not None and (r, c) == (row, column):
                kind = "hit"
            cells.append(Cell(text, kind))
        evidence.rows.append(cells)

    total = len(page.tables)
    where = f"解析器第 {table.index + 1} 张表" + (f"（共 {total} 张）" if total > 1 else "")
    evidence.caption = f"{where}，第 {order[0] + 1}–{order[-1] + 1} 行"

    missing = [label for label in rule.labels
               if diagnosis.kind != "label_unlinked" or label in diagnosis.homes]
    missing = [label for label in missing if not label_cells[label]] or \
              list(diagnosis.homes) or []
    for label in missing:
        bar = threshold(label, rule.max_diffs)
        evidence.context += [f"`{label}` → {line}" for line in _lines_with(page, label, bar)]

    written = (tidy(table.rows[wrong[0]][wrong[1]], 24)
               if wrong and wrong[1] < len(table.rows[wrong[0]]) else "")
    evidence.note = _note(rule, diagnosis, row, column, wrong, label_cells,
                          written)
    return evidence


def _addressed_cell(rule, page, table, label_cells, diagnosis) -> tuple[int, int] | None:
    """Where the number the diagnosis is talking about is sitting."""
    best = None
    for found, r, c, reading in addressed_cells(rule, page, label_cells):
        if found is not table:
            continue
        if diagnosis.model_value is None:
            return (r, c)
        gap = abs(reading - diagnosis.model_value)
        if best is None or gap < best[0]:
            best = (gap, (r, c))
    return best[1] if best else None


def _missing_names(rule, diagnosis) -> list[str]:
    """The labels the metric named, back in the rule's own spelling."""
    lowered = {label.lower(): label for label in rule.labels}
    return [lowered.get(name.lower(), name) for name in (diagnosis.homes or ())]


def _note(rule, diagnosis, row, column, wrong, label_cells,
          written: str = "") -> str:
    lost = _missing_names(rule, diagnosis)
    lost_lower = {name.lower() for name in lost}
    found = [label for label in rule.labels
             if label_cells[label] and label.lower() not in lost_lower]
    if column is not None:
        parts = [f"值落在第 {row + 1} 行第 {column + 1} 列"]
        if found:
            parts.append("、".join(f"`{label}`" for label in found) + " 在同一行")
        if lost:
            parts.append("、".join(f"`{label}`" for label in lost)
                         + " 不在这一行、这一列，也不在表头")
        return "；".join(parts)
    seat = f"第 {wrong[0] + 1} 行第 {wrong[1] + 1} 列" if wrong else "键指向的格子"
    shown = f"`{written}`" if written else (
        f"{diagnosis.model_value:g}" if diagnosis.model_value is not None else "")
    if diagnosis.kind == "row_missing":
        absent = "、".join(f"`{label}`" for label in diagnosis.absent_labels)
        return f"这个值不在任何表里；{absent} 一个字都没进表"
    if diagnosis.kind == "unit_mismatch":
        return (f"{seat} 写着 {shown}，标注值是 `{rule.value}`——"
                f"度量把它读成差 {_power(diagnosis.scale)}")
    if diagnosis.kind == "value_off" and diagnosis.model_value is not None:
        return (f"{seat} 写着 {shown}，标注值是 `{rule.value}`，"
                f"相对差 {diagnosis.error:.0%}，该点容差 {rule.tolerance:g}")
    return "定位键都在表里，但没有任何格子放着这个数"


_SUPER = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def _power(scale: float) -> str:
    """`×10⁹` rather than `×1e+09` -- the note is read, not parsed."""
    import math
    exponent = round(math.log10(scale))
    return f"×10{str(exponent).translate(_SUPER)}"


_SPACE = re.compile(r"\s+")


def tidy(text: str, limit: int = 42) -> str:
    """Cell text as it should read in a narrow column."""
    flat = _SPACE.sub(" ", text).strip()
    return flat if len(flat) <= limit else flat[:limit] + "…"


@dataclass
class Expected:
    """The table that would have scored: one row per point, every key on that row."""

    header: list[str]
    rows: list[list[str]]
    more: int = 0


def expected(verdicts, limit: int = 6) -> Expected:
    """Turn a page's failing points into the long table that would have passed.

    This is not a suggestion invented for the report -- it is what the metric's
    third step accepts without any fallback, and it is the shape our own records
    already have: one `(key, value)` per row. Printing it beside what the parser
    wrote is the shortest way to say what "export a long table" means.
    """
    chosen = list(verdicts)[:limit]
    if not chosen:
        return Expected([], [])
    arity = max(v.rule.arity for v in chosen)
    header = [f"键 {i + 1}" for i in range(arity)] + ["值"]
    rows = []
    for verdict in chosen:
        keys = list(verdict.rule.labels) + [""] * (arity - verdict.rule.arity)
        rows.append([tidy(key, 26) for key in keys] + [verdict.rule.value])
    return Expected(header, rows, more=max(0, len(list(verdicts)) - limit))
