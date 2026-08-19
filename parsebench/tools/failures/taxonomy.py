"""Name the reason one spot-check point failed.

The evaluation report gives two outcomes -- the value was not found in any table,
or it was found and a label would not associate. Neither is a lever. This turns the
first into "read the wrong number" / "wrote it at the wrong scale" / "never wrote
that series down", and the second into "the label is two columns away in the same
table" / "it is on the page but only as plain text" / "it is not there at all",
because those four are what a data-generation pipeline can actually answer.

The forms are the ones `parsebench/data/failure_cases/README.md` says to
distinguish, plus the two the run turned out to need: an addressing label that never
reached a table, and a number the model took from the neighbouring series.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from run import Rule, Verdict
from tables import (Page, Table, close, label_hits, numbers, ratio, relative_error,
                    threshold)

#: Powers of ten a scale mistake is looked for at, largest wrongness first.
SCALES = (1e-6, 1e-3, 1e-2, 1e-1, 1e1, 1e2, 1e3, 1e6, 1e9)

#: How close the neighbour and stacked-total detectors must land to be read as a
#: mechanism rather than a coincidence. The point's own tolerance is far too loose
#: here: at 10% a neighbouring series is within reach of almost any misread.
COINCIDENCE = 0.02

#: Where a label the metric could not associate turned out to live.
LABEL_HOMES = (
    "in_a_table_but_not_addressing",
    "in_another_table_only",
    "emphasised_before_a_table",
    "emphasised_after_the_table",
    "plain_text_only",
    "absent_from_the_output",
)

KINDS = (
    "no_table",
    "label_unlinked",
    "value_off",
    "series_swap",
    "stack_confusion",
    "unit_mismatch",
    "row_missing",
    "value_absent",
)


@dataclass
class Diagnosis:
    """Why one rule failed, in terms something upstream can be changed about."""

    kind: str
    detail: str = ""
    #: For `label_unlinked`: one entry per label the metric could not associate.
    homes: dict[str, str] = field(default_factory=dict)
    #: For the value forms: the number the model put at the addressed cell.
    model_value: float | None = None
    #: |model - truth| / max(|·|), against the point's own tolerance.
    error: float | None = None
    scale: float | None = None
    #: Labels that never reached any table.
    absent_labels: tuple[str, ...] = ()

    @property
    def family(self) -> str:
        """The two-way split the evaluation report itself reports."""
        return "addressing" if self.kind in ("label_unlinked", "row_missing") else "reading"

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


def _label_cells(rule: Rule, page: Page) -> dict[str, list[tuple[Table, int, int]]]:
    """Where each addressing label sits in the parser's tables.

    The metric accepts a label that is merely a substring of a cell, which is right
    for scoring and wrong for pointing: `-75%` is a substring of `175%`, so a
    histogram's tick column matches a label three rows away. When a label matches
    some cell exactly, only the exact matches are kept -- the loose ones are a
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


def _squash(text: str) -> str:
    """The metric's own comparison key: punctuation and case dropped.

    `-75%` and `75%` collapse to the same string here, which is why the literal
    tier runs first when the point of the lookup is to say *which* cell.
    """
    return "".join(ch for ch in text.lower() if ch.isalnum())


def addressed_cells(rule: Rule, page: Page,
                    label_cells: dict[str, list[tuple[Table, int, int]]]
                    ) -> list[tuple[Table, int, int, float]]:
    """The cells the labels jointly point at: one label's row, another's column.

    Pooling every label's rows with every label's columns is too generous -- it
    admits a cell addressed by one label twice, and picking the closest number out
    of that set flatters the parser. The pair has to be two *different* labels, the
    way a row header and a column header address a cell.
    """
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
                        if r < len(table.rows) and c < len(table.rows[r]):
                            for reading in numbers(table.rows[r][c]):
                                out.append((table, r, c, reading))
    return out


def _addressed(rule: Rule, page: Page,
               label_cells: dict[str, list[tuple[Table, int, int]]]) -> list[float]:
    return [reading for _, _, _, reading in addressed_cells(rule, page, label_cells)]


def _home(label: str, rule: Rule, page: Page,
          value_tables: set[int]) -> str:
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


def _missing_labels(explanation: str) -> list[str]:
    """The labels the metric named, taken from its own message.

    It lists one entry per candidate cell; the one with the fewest missing labels is
    the model's best attempt, and is the one worth explaining.
    """
    import ast
    import re

    found = re.findall(r"missing labels: (\[.*?\])", explanation)
    parsed = []
    for group in found:
        try:
            parsed.append([str(x) for x in ast.literal_eval(group)])
        except (ValueError, SyntaxError):
            continue
    return min(parsed, key=len) if parsed else []


def _neighbour(rule: Rule, siblings: list[Rule], model_value: float) -> Rule | None:
    """A point on the same page, one label different, whose value the model wrote."""
    for other in siblings:
        if other.id == rule.id or other.arity != rule.arity:
            continue
        differ = sum(1 for a, b in zip(rule.labels, other.labels) if a != b)
        if differ != 1:
            continue
        if any(close(n, model_value, COINCIDENCE) for n in numbers(other.value)):
            return other
    return None


def _stacked(rule: Rule, siblings: list[Rule], model_value: float) -> Rule | None:
    """A sibling whose value plus this one's makes the number the model wrote."""
    truth = numbers(rule.value)
    if not truth:
        return None
    for other in siblings:
        if other.id == rule.id or other.arity != rule.arity:
            continue
        if sum(1 for a, b in zip(rule.labels, other.labels) if a != b) != 1:
            continue
        for n in numbers(other.value):
            if close(truth[0] + n, model_value, COINCIDENCE):
                return other
    return None


def diagnose(verdict: Verdict, page: Page, siblings: list[Rule]) -> Diagnosis:
    """Why this rule failed. `siblings` are the other spot-check points on its page."""
    rule = verdict.rule
    if not page.tables:
        return Diagnosis("no_table")

    hits = _value_cells(rule, page)
    if "labels not associated" in verdict.explanation:
        value_tables = {table.index for table, _, _ in hits}
        missing = _missing_labels(verdict.explanation) or list(rule.labels)
        homes = {label: _home(label, rule, page, value_tables) for label in missing}
        return Diagnosis("label_unlinked", homes=homes)

    label_cells = _label_cells(rule, page)
    absent = tuple(label for label in rule.labels if not label_cells[label])
    if absent:
        return Diagnosis("row_missing", absent_labels=absent,
                         detail=", ".join(absent[:3]))

    targets = numbers(rule.value)
    addressed = _addressed(rule, page, label_cells)

    #: A scale mistake only counts when the wrongly-scaled number is sitting where
    #: the labels point. Scanning the whole page for `value × 10` finds coincidences.
    for reading in addressed:
        for scale in SCALES:
            if any(close(t * scale, reading, rule.tolerance) for t in targets):
                return Diagnosis("unit_mismatch", scale=scale, model_value=reading,
                                 detail=f"×{scale:g}")

    if addressed and targets:
        model_value = min(addressed, key=lambda n: relative_error(targets[0], n))
        error = relative_error(targets[0], model_value)
        neighbour = _neighbour(rule, siblings, model_value)
        if neighbour is not None:
            differing = next((b for a, b in zip(rule.labels, neighbour.labels) if a != b), "")
            return Diagnosis("series_swap", model_value=model_value, error=error,
                             detail=f"the value of `{differing}`")
        stacked = _stacked(rule, siblings, model_value)
        if stacked is not None:
            return Diagnosis("stack_confusion", model_value=model_value, error=error,
                             detail=f"this segment plus `{stacked.labels[-1]}`")
        return Diagnosis("value_off", model_value=model_value, error=error)

    for table in page.tables:
        for _, _, cell in table.cells():
            for reading in numbers(cell):
                for scale in SCALES:
                    if any(close(t * scale, reading, rule.tolerance) for t in targets):
                        return Diagnosis("unit_mismatch", scale=scale,
                                         model_value=reading, detail=f"×{scale:g}")
    return Diagnosis("value_absent")


def roll_up(diagnoses: list[Diagnosis]) -> Counter:
    return Counter(diagnosis.kind for diagnosis in diagnoses)
