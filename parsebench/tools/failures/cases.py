"""The failures the models are asked about, and the text each one becomes.

Equal-sized per form rather than proportional (`format.CASE_SAMPLE`): the rare forms
are where an unknown mechanism would hide, and `label_unlinked` at two thirds of the
run would otherwise take the whole sample. The price is that a mechanism count over
this sample is a count *within a form*; a run-level number is that distribution
weighted by the full-run form counts, which the program computes over every failure
and does not sample at all.

A case shows the rule, the form the program computed, the metric's own words, and
the piece of parser output the failure is about -- the table the value landed in and
where each addressing label actually sits. Showing the whole page would make the
model do the search again, and what is being asked for is the mechanism, not the
search.
"""

from __future__ import annotations

import random
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1])]

from difflib import SequenceMatcher                                # noqa: E402

from failures.forms import Form, _label_cells, _value_cells       # noqa: E402
from failures.run import Run, Verdict                             # noqa: E402
from failures.tables import Page, Table                           # noqa: E402

#: Rows kept above and below the row the failure is on, and the widest table shown.
CONTEXT_ROWS = 3
MAX_COLUMNS = 8
MAX_CELL = 120


@dataclass(frozen=True)
class Case:
    """One failing spot-check point, as the model is shown it."""

    case_id: str
    stem: str
    verdict: Verdict
    form: Form

    @property
    def rule(self):
        return self.verdict.rule


def sample(run: Run, forms: dict[str, Form], per_form: int = 10,
           seed: int = 20260820) -> list[Case]:
    """Up to `per_form` failures of each form, drawn by seed, in a stable order."""
    by_form: dict[str, list[Verdict]] = defaultdict(list)
    for verdict in run.failures():
        key = f"{verdict.rule.stem}/{verdict.rule.id}"
        if key in forms:
            by_form[forms[key].kind].append(verdict)

    chosen: list[Case] = []
    rng = random.Random(seed)
    for kind in sorted(by_form):
        pool = sorted(by_form[kind], key=lambda v: f"{v.rule.stem}/{v.rule.id}")
        drawn = pool if len(pool) <= per_form else rng.sample(pool, per_form)
        for verdict in sorted(drawn, key=lambda v: f"{v.rule.stem}/{v.rule.id}"):
            key = f"{verdict.rule.stem}/{verdict.rule.id}"
            chosen.append(Case(f"{kind}-{len(chosen) + 1:02d}", verdict.rule.stem,
                               verdict, forms[key]))
    return chosen


def _clip(text: str, keep: bool = False) -> str:
    """Squeeze a cell onto one line. A cell an addressing label hit is never cut.

    Cutting one would invent the failure: a key that the parser wrote in full but
    misspelt, and a key the parser truncated, look identical once the renderer has
    put an ellipsis on it, and the mechanism asked for is exactly which of the two
    it was.
    """
    text = " ".join(str(text).split())
    return text if keep or len(text) <= MAX_CELL else text[:MAX_CELL] + "…"


def _excerpt(case: Case, page: Page) -> list[str]:
    """The table the failure is about, cut to the rows and columns that carry it."""
    rule = case.rule
    if not page.tables:
        return ["(the parser produced no table on this page)"]

    hits = _value_cells(rule, page)
    label_cells = _label_cells(rule, page)
    if hits:
        table, row, _ = hits[0]
    else:
        counts = {t.index: sum(1 for label in rule.labels
                               for cell in label_cells[label] if cell[0] is t)
                  for t in page.tables}
        table = max(page.tables, key=lambda t: (counts[t.index], -t.index))
        row = next((cell[1] for label in rule.labels for cell in label_cells[label]
                    if cell[0] is table), 0)

    marked = {(cell[1], cell[2]) for label in rule.labels
              for cell in label_cells[label] if cell[0] is table}
    return _render(table, row, marked)


def _render(table: Table, row: int, marked: set[tuple[int, int]]) -> list[str]:
    width = max((len(r) for r in table.rows), default=0)
    keep = sorted({0} | {c for _, c in marked})
    columns = keep if width > MAX_COLUMNS else list(range(width))
    for index in range(width):
        if len(columns) >= MAX_COLUMNS:
            break
        if index not in columns:
            columns.append(index)
    columns = sorted(columns)[:MAX_COLUMNS]

    low = max(0, row - CONTEXT_ROWS)
    order = ([0] if low > 0 else []) + list(range(low, min(len(table.rows),
                                                          low + 2 * CONTEXT_ROWS + 1)))
    lines = [f"(table {table.index}, {len(table.rows)} rows × {width} columns"
             + (f", showing columns {columns}" if len(columns) < width else "") + ")"]
    for r in order:
        cells = table.rows[r]
        rendered = []
        for c in columns:
            marks = (r, c) in marked
            text = _clip(cells[c], keep=marks) if c < len(cells) else ""
            rendered.append(f"[{text}]" if marks else text)
        lines.append("| " + " | ".join(rendered) + " |")
    return lines


def _nearest_cell(label: str, page: Page) -> tuple[str, float]:
    """The cell that comes closest to an addressing label the metric never matched.

    Without it a `row_missing` case cannot be attributed: a key the parser never
    wrote, a key it wrote into the prose instead, and a key it wrote into the header
    with one letter wrong all look the same from the outside, and those are three
    different things to fix upstream.
    """
    best, score = "", 0.0
    for table in page.tables:
        for _, _, cell in table.cells():
            ratio = SequenceMatcher(None, label.lower(), cell.lower()).ratio()
            if ratio > score:
                best, score = cell, ratio
    return best, score


def render(case: Case, page: Page) -> str:
    """One case as the model reads it. `[...]` marks a cell an addressing label hit."""
    rule, form = case.rule, case.form
    lines = [f"### {case.case_id}   page={case.stem}   form={form.kind}",
             f"value: {rule.value!r}   labels: {list(rule.labels)}   "
             f"tolerance: {rule.tolerance:g}   tags: {list(rule.tags) or '[]'}",
             f"metric: {' '.join(case.verdict.explanation.split())[:300]}"]
    if form.homes:
        lines.append("program: the label the metric could not associate sits "
                     + "; ".join(f"{label!r} -> {home}" for label, home in form.homes.items()))
    for label in form.absent_labels:
        nearest, score = _nearest_cell(label, page)
        lines.append(f"program: no table cell matches {label!r}; the closest one, at "
                     f"{score:.0%} similarity, reads {nearest!r}")
    if form.model_value is not None:
        detail = f"program: the addressed cell holds {form.model_value:g}"
        if form.error is not None:
            detail += f", a relative error of {form.error:.1%}"
        if form.scale is not None:
            detail += f" (the value at ×{form.scale:g})"
        lines.append(detail)
    lines += ["parser output, `[...]` marking a cell an addressing label hit:"]
    lines += _excerpt(case, page)
    return "\n".join(lines)
