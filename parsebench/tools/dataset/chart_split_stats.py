"""Summarize the ParseBench chart annotations into a reproducible stats file.

Every claim in the review documents about the chart split — how many points
need visual estimation, how loose the tolerances are, how many keys it takes
to address a value — is produced here rather than typed by hand, so a dataset
refresh reprints the numbers instead of silently invalidating them.

Usage:
    python parsebench/tools/dataset/chart_split_stats.py
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_JSONL = REPO_ROOT / "parsebench" / "data" / "raw" / "chart.jsonl"
DEFAULT_OUT = REPO_ROOT / "parsebench" / "data" / "stats" / "chart_split_stats.json"

# The rule payload omits relative_tolerance when the annotator kept the default.
DEFAULT_TOLERANCE = 0.01
PAGE_SUFFIX = re.compile(r"_p\d+\.pdf$")


@dataclass(frozen=True)
class Rule:
    """One spot-check point: a value plus the labels that must address it."""

    pdf: str
    tags: tuple[str, ...]
    value: str
    labels: tuple[str, ...]
    tolerance: float

    @property
    def needs_estimate(self) -> bool:
        return "need_estimate" in self.tags

    @property
    def is_three_key(self) -> bool:
        return "3d_chart" in self.tags


def load_rules(path: Path) -> list[Rule]:
    rules: list[Rule] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        payload = json.loads(record["rule"])
        tolerance = payload.get("relative_tolerance")
        rules.append(
            Rule(
                pdf=record["pdf"],
                tags=tuple(sorted(record["tags"])),
                value=str(payload["value"]),
                labels=tuple(str(label) for label in payload.get("labels", [])),
                tolerance=DEFAULT_TOLERANCE if tolerance is None else float(tolerance),
            )
        )
    return rules


def quantiles(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    n = len(ordered)
    return {
        "min": ordered[0],
        "p25": ordered[n // 4],
        "median": ordered[n // 2],
        "p75": ordered[3 * n // 4],
        "max": ordered[-1],
        "mean": round(statistics.fmean(ordered), 4),
    }


def summarize(rules: list[Rule]) -> dict[str, Any]:
    per_page: dict[str, list[Rule]] = defaultdict(list)
    for rule in rules:
        per_page[rule.pdf].append(rule)

    documents = {PAGE_SUFFIX.sub("", Path(pdf).name) for pdf in per_page}
    rules_per_page = [len(v) for v in per_page.values()]
    page_tagsets = Counter(tuple(sorted({t for r in v for t in r.tags})) or ("(untagged)",) for v in per_page.values())

    value_text = [r.value for r in rules]
    decimals = Counter(len(v.split(".")[1]) if "." in v else 0 for v in value_text)

    return {
        "rules": len(rules),
        "pages": len(per_page),
        "documents": len(documents),
        "rules_per_page": {
            "mean": round(statistics.fmean(rules_per_page), 2),
            "median": statistics.median(rules_per_page),
            "max": max(rules_per_page),
        },
        "tags": {
            "rule_level": Counter(t for r in rules for t in r.tags),
            "page_level_combinations": {"+".join(k): v for k, v in page_tagsets.items()},
        },
        "needs_estimate": {
            "rules": sum(r.needs_estimate for r in rules),
            "share": round(sum(r.needs_estimate for r in rules) / len(rules), 4),
        },
        "labels_per_rule": dict(sorted(Counter(len(r.labels) for r in rules).items())),
        "labels_per_rule_by_three_key": {
            f"three_key={flag}": dict(sorted(Counter(len(r.labels) for r in rules if r.is_three_key == flag).items()))
            for flag in (True, False)
        },
        "tolerance_overall": quantiles([r.tolerance for r in rules]),
        "tolerance_by_estimate": {
            f"needs_estimate={flag}": quantiles([r.tolerance for r in rules if r.needs_estimate == flag])
            for flag in (True, False)
        },
        "value_formatting": {
            "percent_sign": sum("%" in v for v in value_text),
            "currency_sign": sum(any(c in v for c in "$€£¥") for v in value_text),
            "thousands_comma": sum("," in v for v in value_text),
            "negative": sum(v.strip().startswith("-") for v in value_text),
            "decimal_places": dict(sorted(decimals.items())),
        },
        "pages_per_document": quantiles(
            [float(c) for c in Counter(PAGE_SUFFIX.sub("", Path(p).name) for p in per_page).values()]
        ),
    }


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        f"rules {summary['rules']} | pages {summary['pages']} | documents {summary['documents']}",
        f"rules/page mean {summary['rules_per_page']['mean']} median {summary['rules_per_page']['median']}",
        f"need_estimate {summary['needs_estimate']['rules']} ({summary['needs_estimate']['share']:.1%})",
        f"labels/rule {summary['labels_per_rule']}",
        f"tolerance (needs_estimate=True) {summary['tolerance_by_estimate']['needs_estimate=True']}",
        f"tolerance (needs_estimate=False) {summary['tolerance_by_estimate']['needs_estimate=False']}",
        f"page tag combinations {summary['tags']['page_level_combinations']}",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    rules = load_rules(args.jsonl)
    summary = summarize(rules)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=dict))
    print(render_text(summary))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
