"""Put the three models' attributions side by side, and weight them back to the run.

The sample is equal-sized per form, so a mechanism count over it is a count *within
a form*. A run-level number is that distribution weighted by the full-run form
counts, which the program computed over every failure and did not sample. Doing the
weighting here rather than in a report is what keeps the two numbers -- how often a
mechanism appeared in the sample, and what share of the run it stands for -- from
being printed as if they were the same number.

A case's mechanism is what at least two of three models called it. Where no two
agree the case is a conflict, counted and listed rather than resolved: the agent
adjudicates those against the page, and the verdict is data (`verdicts.json`), not
an edit to a model's answer.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1])]

from contract.format import MECHANISM_STEP, MECHANISMS           # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "parsebench/data/analysis"


def load(models: list[str]) -> dict[str, dict]:
    """Each model's failure answer, keyed by model. Missing models are skipped."""
    out = {}
    for model in models:
        path = ANALYSIS / model / "failures.json"
        if path.exists():
            out[model] = json.loads(path.read_text(encoding="utf-8"))
    return out


def build(models: list[str], failures: int) -> dict:
    """Per-model counts, the per-case consensus, and the run-level weighting."""
    answers = load(models)
    if not answers:
        return {}

    cases = {case["case_id"]: case for case in next(iter(answers.values()))["cases"]}
    said: dict[str, dict[str, str]] = defaultdict(dict)
    per_model: dict[str, Counter] = {model: Counter() for model in answers}
    evidence: dict[str, dict[str, str]] = defaultdict(dict)
    for model, answer in answers.items():
        for item in answer["answer"]["attributions"]:
            case_id = str(item["case_id"])
            if case_id not in cases:
                continue
            said[case_id][model] = str(item["mechanism"])
            evidence[case_id][model] = str(item.get("evidence") or "")
            per_model[model][item["mechanism"]] += 1

    consensus: dict[str, str] = {}
    conflicts: list[dict] = []
    for case_id, by_model in said.items():
        counts = Counter(by_model.values())
        mechanism, n = counts.most_common(1)[0]
        if n >= 2:
            consensus[case_id] = mechanism
        else:
            conflicts.append({"case_id": case_id, "page": cases[case_id]["page"],
                              "form": cases[case_id]["form"]["kind"],
                              "values": by_model, "evidence": evidence[case_id]})

    #: Sampled per form, so a within-form rate can be scaled by the full-run count.
    sampled = Counter(case["form"]["kind"] for case in cases.values())
    by_form: dict[str, Counter] = defaultdict(Counter)
    for case_id, mechanism in consensus.items():
        by_form[cases[case_id]["form"]["kind"]][mechanism] += 1

    return {
        "models": list(answers),
        "cases": len(cases),
        "per_model": {model: dict(counts) for model, counts in per_model.items()},
        "consensus": consensus,
        "unanimous": sum(1 for by_model in said.values() if len(set(by_model.values())) == 1),
        "majority": sum(1 for case_id in consensus
                        if len(set(said[case_id].values())) > 1),
        "conflicts": conflicts,
        "sampled_per_form": dict(sampled),
        "weighted": _weighted(by_form, sampled, failures),
        "agreement": {case_id: len({m for m in said[case_id].values()}) for case_id in said},
        "evidence": {case_id: evidence[case_id] for case_id in said},
        "case_pages": {case_id: case["page"] for case_id, case in cases.items()},
    }


def _weighted(by_form: dict[str, Counter], sampled: Counter,
              failures: int) -> dict[str, list]:
    """A mechanism's share of the whole run, not of the sample.

    Each form contributes its own full-run count times the mechanism's rate inside
    that form. Without this the equal-sized draw would make a mechanism of the rare
    forms look as common as one of `label_unlinked`, which is two thirds of the run.
    """
    full: dict[str, int] = {}
    for path in sorted((ROOT / "parsebench/data/stats").glob("failures_*.json")):
        full = json.loads(path.read_text(encoding="utf-8")).get("counts", {})
        break

    out: dict[str, list] = {}
    for mechanism in MECHANISMS:
        total = 0.0
        for form, counts in by_form.items():
            drawn = sampled.get(form, 0)
            if drawn:
                total += full.get(form, 0) * counts.get(mechanism, 0) / drawn
        if total:
            out[mechanism] = [round(total / failures, 4) if failures else 0.0, round(total, 1)]
    return dict(sorted(out.items(), key=lambda kv: -kv[1][1]))


def step_counts(mechanisms: dict) -> dict[int, float]:
    """The weighted mechanism counts rolled up to the four judgement steps."""
    out: dict[int, float] = defaultdict(float)
    for mechanism, (_, count) in mechanisms.get("weighted", {}).items():
        out[MECHANISM_STEP[mechanism]] += count
    return dict(out)
