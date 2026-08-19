"""Load one parser run: what the model wrote, and how the official metric scored it.

A run directory is what `parse-bench` leaves behind for one pipeline on one split:
`<stem>.result.json` per page plus `_evaluation_report.json` with a verdict per
spot-check point. The spot-check rules themselves come from the split's own
`chart.jsonl`, joined on the rule id, which the two files share.

Nothing here re-scores anything. `passed` is always the official value.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from tables import Page

#: `relative_tolerance` when the rule leaves it out (`rules_chart.py`).
DEFAULT_TOLERANCE = 0.01


@dataclass(frozen=True)
class Rule:
    """One spot-check point: a value, and the labels that address it."""

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


@dataclass(frozen=True)
class Verdict:
    """The official judgement on one rule."""

    rule: Rule
    passed: bool
    explanation: str


@dataclass
class Run:
    """One pipeline's output over one split, with the split's rules attached."""

    name: str
    model: str
    pages: dict[str, Page]
    verdicts: list[Verdict]

    @property
    def stems(self) -> list[str]:
        return sorted(self.pages)

    def by_page(self) -> dict[str, list[Verdict]]:
        out: dict[str, list[Verdict]] = {stem: [] for stem in self.pages}
        for verdict in self.verdicts:
            out.setdefault(verdict.rule.stem, []).append(verdict)
        return out

    def failures(self) -> list[Verdict]:
        return [v for v in self.verdicts if not v.passed]


def load_rules(jsonl: Path) -> dict[tuple[str, str], Rule]:
    """The split's spot-check points, keyed by (page stem, rule id).

    The id alone is not unique: 25 of the 4,864 rows repeat one, and two of those
    sit on different pages, so keying on the id alone silently moves a point to the
    wrong page and changes eight page scores.
    """
    out = {}
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rule = json.loads(row["rule"])
        out[(Path(row["pdf"]).stem, row["id"])] = Rule(
            id=row["id"],
            stem=Path(row["pdf"]).stem,
            value=str(rule["value"]),
            labels=tuple(str(label) for label in rule["labels"]),
            max_diffs=int(rule.get("max_diffs") or 0),
            tolerance=float(rule.get("relative_tolerance") or DEFAULT_TOLERANCE),
            tags=tuple(row.get("tags") or ()),
        )
    return out


def load_run(run_dir: Path, rules: dict[tuple[str, str], Rule], model: str = "") -> Run:
    """Read every page's markdown and every rule's verdict out of a run directory."""
    pages: dict[str, Page] = {}
    for path in sorted(run_dir.glob("*.result.json")):
        stem = path.name[: -len(".result.json")]
        payload = json.loads(path.read_text(encoding="utf-8"))
        markdown = (payload.get("output") or {}).get("markdown") or ""
        pages[stem] = Page.build(stem, markdown)

    report = json.loads((run_dir / "_evaluation_report.json").read_text(encoding="utf-8"))
    verdicts = []
    for example in report["per_example_results"]:
        stem = example["example_id"].split("/", 1)[-1]
        for metric in example["metrics"]:
            if metric["metric_name"] != "rule_pass_rate":
                continue
            for result in metric["metadata"]["rule_results"]:
                if result["type"] != "chart_data_point":
                    continue
                rule = rules.get((stem, result["id"]))
                if rule is None:
                    continue
                verdicts.append(Verdict(rule, bool(result["passed"]),
                                        result.get("explanation") or ""))
    return Run(run_dir.parent.name, model, pages, verdicts)


def run_model(run_dir: Path) -> str:
    """The model id recorded in the run's `_metadata.json`, if it is there."""
    meta = run_dir.parent / "_metadata.json"
    if not meta.exists():
        return ""
    payload = json.loads(meta.read_text(encoding="utf-8"))
    return str(((payload.get("pipeline") or {}).get("config") or {}).get("model") or "")
