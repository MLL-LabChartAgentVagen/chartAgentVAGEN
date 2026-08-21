"""Which form each failure took, computed from the parser's own output.

The evaluation report gives two outcomes -- the value was not found in any table,
or it was found and a label would not associate. Neither is a lever. This splits the
first into `read the wrong number` / `wrote it at the wrong scale` / `never wrote
that value down`, and the second into where the unassociable label actually sits,
because those are what a data-generation pipeline can answer.

Nothing here re-scores anything: `passed` is the official value. The forms are
`format.FORMS` and the label homes `format.LABEL_HOMES`; the two candidate forms the
last round could not separate from an ordinary misread -- reading a neighbouring
series, reading a stacked total -- are not forms here. They come back as
*mechanisms*, where they are a claim about the drawing rather than a count.
"""

from __future__ import annotations

import ast
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1])]

from contract.format import FORMS                                   # noqa: E402
from failures.run import Rule, Verdict                              # noqa: E402
from failures.tables import (Page, Table, close, label_hits, numbers,  # noqa: E402
                             ratio, relative_error, threshold)

#: Powers of ten a scale mistake is looked for at.
SCALES = (1e-6, 1e-3, 1e-2, 1e-1, 1e1, 1e2, 1e3, 1e6, 1e9)

#: The two-way split the evaluation report itself reports.
ADDRESSING = ("label_unlinked", "row_missing")


@dataclass
class Form:
    """The form one failure took, and what the program could see about it."""

    kind: str
    detail: str = ""
    #: For `label_unlinked`: one entry per label the metric could not associate.
    homes: dict[str, str] = field(default_factory=dict)
    #: For the value forms: the number the parser put at the addressed cell.
    model_value: float | None = None
    #: |model - truth| / max(|·|).
    error: float | None = None
    scale: float | None = None
    #: Labels that never reached any table.
    absent_labels: tuple[str, ...] = ()

    @property
    def family(self) -> str:
        return "addressing" if self.kind in ADDRESSING else "reading"

    def to_json(self) -> dict:
        out: dict = {"kind": self.kind}
        if self.detail:
            out["detail"] = self.detail
        if self.homes:
            out["homes"] = self.homes
        if self.model_value is not None:
            out["model_value"] = self.model_value
        if self.error is not None:
            out["error"] = round(self.error, 4)
        if self.scale is not None:
            out["scale"] = self.scale
        if self.absent_labels:
            out["absent_labels"] = list(self.absent_labels)
        return out


def _value_cells(rule: Rule, page: Page) -> list[tuple[Table, int, int]]:
    """Cells holding the rule's value, by number or by string."""
    targets = numbers(rule.value)
    bar = threshold(rule.value, rule.max_diffs)
    out = []
    for table in page.tables:
        for r, c, cell in table.cells():
            if any(close(t, n, rule.tolerance) for t in targets for n in numbers(cell)):
                out.append((table, r, c))
            elif rule.value and ratio(rule.value, cell) >= bar:
                out.append((table, r, c))
    return out


def _squash(text: str) -> str:
    """The metric's own comparison key: punctuation and case dropped."""
    return "".join(ch for ch in text.lower() if ch.isalnum())


def _label_cells(rule: Rule, page: Page) -> dict[str, list[tuple[Table, int, int]]]:
    """Where each addressing label sits in the parser's tables.

    The metric accepts a label that is merely a substring of a cell, which is right
    for scoring and wrong for pointing: `-75%` is a substring of `175%`. When a label
    matches some cell exactly, only the exact matches are kept; the loose ones are a
    fallback for when nothing matched cleanly.
    """
    out: dict[str, list[tuple[Table, int, int]]] = {}
    for label in rule.labels:
        bar = threshold(label, rule.max_diffs)
        literal, squashed, loose = [], [], []
        want_literal, want_squashed = label.strip().casefold(), _squash(label)
        for table in page.tables:
            for r, c, cell in table.cells():
                if not label_hits(label, cell, bar):
                    continue
                if want_literal and cell.strip().casefold() == want_literal:
                    literal.append((table, r, c))
                elif want_squashed and _squash(cell) == want_squashed:
                    squashed.append((table, r, c))
                else:
                    loose.append((table, r, c))
        out[label] = literal or squashed or loose
    return out


def addressed_cells(rule: Rule, page: Page,
                    label_cells: dict[str, list[tuple[Table, int, int]]]
                    ) -> list[tuple[Table, int, int, float]]:
    """The cells the labels jointly point at: one label's row, another's column.

    The pair has to be two *different* labels, the way a row header and a column
    header address a cell. Pooling every label's rows with every label's columns
    would admit a cell addressed by one label twice and flatter the parser.

    A cell that is itself one of the addressing labels is skipped. When a key is a
    number -- a year, a decile -- the intersection of its own row and its own column
    is the key cell, and reading it back as `what the parser wrote for this value`
    turns a key into a misread value.
    """
    labelled = {(cell[0].index, cell[1], cell[2])
                for cells in label_cells.values() for cell in cells}
    out = []
    for table in page.tables:
        for row_label in rule.labels:
            rows = {cell[1] for cell in label_cells[row_label] if cell[0] is table}
            for column_label in rule.labels:
                if column_label == row_label and rule.arity > 1:
                    continue
                cols = {cell[2] for cell in label_cells[column_label] if cell[0] is table}
                for r in rows:
                    for c in cols:
                        if (table.index, r, c) in labelled:
                            continue
                        if r < len(table.rows) and c < len(table.rows[r]):
                            for reading in numbers(table.rows[r][c]):
                                out.append((table, r, c, reading))
    return out


def _home(label: str, rule: Rule, page: Page, value_tables: set[int]) -> str:
    """Where a label the metric would not associate actually sits in the output."""
    bar = threshold(label, rule.max_diffs)
    found = {table.index for table in page.tables
             for _, _, cell in table.cells() if label_hits(label, cell, bar)}
    if found:
        return ("in_a_table_but_not_addressing" if found & value_tables
                else "in_another_table_only")
    marks = [span.offset for span in page.emphasis if label_hits(label, span.text, bar)]
    if marks:
        first_table = min((table.start for table in page.tables), default=0)
        return ("emphasised_before_a_table" if min(marks) < first_table
                else "emphasised_after_the_table")
    if label_hits(label, page.markdown, bar):
        return "plain_text_only"
    return "absent_from_the_output"


_MISSING = re.compile(r"missing labels: (\[.*?\])")


def _missing_labels(explanation: str) -> list[str]:
    """The labels the metric named, taken from its own message.

    It lists one entry per candidate cell; the one with the fewest missing labels is
    the parser's best attempt, and is the one worth explaining.
    """
    parsed = []
    for group in _MISSING.findall(explanation):
        try:
            parsed.append([str(x) for x in ast.literal_eval(group)])
        except (ValueError, SyntaxError):
            continue
    return min(parsed, key=len) if parsed else []


def classify(verdict: Verdict, page: Page) -> Form:
    """The form this failure took. `page` is the parser's output for its page."""
    rule = verdict.rule
    if not page.tables:
        return Form("no_table")

    hits = _value_cells(rule, page)
    if "labels not associated" in verdict.explanation:
        value_tables = {table.index for table, _, _ in hits}
        missing = _missing_labels(verdict.explanation) or list(rule.labels)
        return Form("label_unlinked",
                    homes={label: _home(label, rule, page, value_tables) for label in missing},
                    detail=", ".join(missing[:3]))

    label_cells = _label_cells(rule, page)
    absent = tuple(label for label in rule.labels if not label_cells[label])
    if absent:
        return Form("row_missing", absent_labels=absent, detail=", ".join(absent[:3]))

    targets = numbers(rule.value)
    addressed = [reading for _, _, _, reading in addressed_cells(rule, page, label_cells)]

    # A scale mistake only counts when the wrongly-scaled number is sitting where the
    # labels point. Scanning the whole page for `value × 10` finds coincidences.
    for reading in addressed:
        for scale in SCALES:
            if any(close(t * scale, reading, rule.tolerance) for t in targets):
                return Form("unit_mismatch", scale=scale, model_value=reading,
                            detail=f"×{scale:g}")

    if addressed and targets:
        model_value = min(addressed, key=lambda n: relative_error(targets[0], n))
        return Form("value_off", model_value=model_value,
                    error=relative_error(targets[0], model_value))

    for table in page.tables:
        for _, _, cell in table.cells():
            for reading in numbers(cell):
                for scale in SCALES:
                    if any(close(t * scale, reading, rule.tolerance) for t in targets):
                        return Form("unit_mismatch", scale=scale, model_value=reading,
                                    detail=f"×{scale:g}")
    return Form("value_absent")


def classify_all(verdicts: list[Verdict], pages: dict[str, Page]) -> dict[str, Form]:
    """Every failure in a run, keyed by `(page stem, rule id)` joined with a slash."""
    return {f"{v.rule.stem}/{v.rule.id}": classify(v, pages[v.rule.stem])
            for v in verdicts if not v.passed}


def roll_up(forms: dict[str, Form]) -> Counter:
    counts = Counter(form.kind for form in forms.values())
    for kind in FORMS:
        counts.setdefault(kind, 0)
    return counts
