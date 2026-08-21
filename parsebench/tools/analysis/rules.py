"""The spot-check points of `chart.jsonl`, and how a predicted key set is scored.

These rules never reach the model: a page prompt carries the values and withholds
the labels, so `spot_checks[].addressing_keys` is a prediction and the annotation
grades it. That is the one quantity in the whole comparison where the question is
`who is right` rather than `who agrees with whom`.

The id alone does not identify a point -- 25 of the 4,864 rows repeat one, two of
them across different pages -- so a point is keyed by (page stem, rule id).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CHART_JSONL = ROOT / "parsebench/data/raw/chart.jsonl"

#: `relative_tolerance` when the rule leaves it out, from the benchmark's own default.
DEFAULT_TOLERANCE = 0.01


@dataclass(frozen=True)
class Rule:
    """One spot-check point: a value, and the labels a table row must carry to address it."""

    id: str
    stem: str
    value: str
    labels: tuple[str, ...]
    max_diffs: int
    tolerance: float
    tags: tuple[str, ...]

    @property
    def arity(self) -> int:
        return len(self.labels)


def load_rules(jsonl: Path = CHART_JSONL) -> dict[str, list[Rule]]:
    """Every spot-check point, grouped by page stem, in file order."""
    by_stem: dict[str, list[Rule]] = {}
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        payload = json.loads(row["rule"])
        stem = Path(row["pdf"]).stem
        by_stem.setdefault(stem, []).append(Rule(
            id=str(row["id"]),
            stem=stem,
            value=str(payload["value"]),
            labels=tuple(str(label) for label in payload.get("labels", ())),
            max_diffs=int(payload.get("max_diffs") or 0),
            tolerance=float(payload.get("relative_tolerance") or DEFAULT_TOLERANCE),
            tags=tuple(row.get("tags") or ()),
        ))
    return by_stem


_WORD = re.compile(r"[^0-9a-z]+")


def _normalize(text: str) -> str:
    return _WORD.sub("", str(text).lower())


def keys_agree(predicted: list[str], actual: tuple[str, ...]) -> bool:
    """Does a predicted key set cover every label the rule addresses the value by?

    Containment either way, which is how the benchmark matches a label to a cell:
    predicting `Weather-related losses` for the label `Weather-related` is right,
    and so is predicting `1992` for `1992`. Labels shorter than two characters
    after normalising carry no information and are skipped on both sides.
    """
    have = [_normalize(k) for k in predicted]
    have = [k for k in have if len(k) >= 2]
    want = [_normalize(label) for label in actual]
    return all(any(w in h or h in w for h in have) for w in want if len(w) >= 2)
