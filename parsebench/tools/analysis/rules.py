"""The spot-check rules of `chart.jsonl`, and which figure each one belongs to.

These rules never reach the model. They carry structural evidence of their own --
a rule needing three labels says the page has a third addressing key -- and that
is only worth something as an independent check, so they are loaded here and
compared against the answer afterwards, in `checks`.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Rule:
    """One spot-check point on a page: a value and the labels that must address it."""

    value: str
    labels: tuple[str, ...]
    tolerance: float
    max_diffs: int

    @property
    def arity(self) -> int:
        return len(self.labels)


def load_rules(jsonl: Path) -> dict[str, list[Rule]]:
    """Every spot-check point, grouped by page stem."""
    by_stem: dict[str, list[Rule]] = {}
    for line in jsonl.read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        payload = json.loads(record["rule"])
        by_stem.setdefault(Path(record["pdf"]).stem, []).append(
            Rule(value=str(payload["value"]),
                 labels=tuple(str(label) for label in payload.get("labels", [])),
                 tolerance=float(payload.get("relative_tolerance") or 0.01),
                 max_diffs=int(payload.get("max_diffs") or 0))
        )
    return by_stem


# ------------------------------------------------------- attribution and checks

_WORD = re.compile(r"[^0-9a-z]+")


def _normalize(text: str) -> str:
    return _WORD.sub("", text.lower())


def _figure_names(figure: dict) -> list[str]:
    heading = figure.get("heading") or {}
    names = [str(heading.get(k, "")) for k in ("title", "subtitle", "unit_text")]
    for key in ("panel_names", "series_names", "category_names"):
        names += [str(n) for n in figure.get(key) or ()]
    return [n for n in (_normalize(n) for n in names) if len(n) >= 2]


def attribute(rules: list[Rule], figures: list[dict]) -> list[str | None]:
    """Which figure each rule belongs to, by matching its labels against the names.

    One figure on the page takes every rule. Otherwise a label counts for a figure
    when it contains, or is contained in, one of that figure's printed names; the
    figure matching the most labels wins and a tie goes to the earlier figure. No
    match leaves the rule unattributed, which is itself reported.
    """
    if len(figures) == 1:
        return [figures[0].get("id", "f1")] * len(rules)

    names = [_figure_names(f) for f in figures]
    out: list[str | None] = []
    for rule in rules:
        scores = [
            sum(any(label in name or name in label for name in figure_names)
                for label in (_normalize(l) for l in rule.labels) if len(label) >= 2)
            for figure_names in names
        ]
        best = max(scores) if scores else 0
        out.append(figures[scores.index(best)].get("id") if best else None)
    return out
