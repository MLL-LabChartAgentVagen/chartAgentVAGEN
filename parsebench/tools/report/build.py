"""Write every file the program is the author of.

    reports/pages/<page>.md   one per sampled page: three models side by side,
                              plus the grading
    reports/<model>.md        3 files, one model's own two reports and its numbers
    reports/compare.md        every number

`reports/INDEX.md` and `reports/view.html` are not written here: they are the
agent's, and they are the only files that conclude anything.

Everything is rendered from `data/analysis/` and `data/stats/`, so any of it can be
thrown away and rebuilt. A verdict recorded in `data/analysis/verdicts.json`
survives a re-render for the same reason -- it is data, not an edit to a file.

Usage:
    python parsebench/tools/report/build.py
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "parsebench" / "tools")]

from analysis.rules import load_rules                            # noqa: E402
from failures import forms as form_lib                           # noqa: E402
from failures import mechanisms as mechanism_lib                 # noqa: E402
from failures import run as run_lib                              # noqa: E402
from report import compare, models as model_report, pages as page_report   # noqa: E402

ANALYSIS = ROOT / "parsebench/data/analysis"
STATS = ROOT / "parsebench/data/stats"
REPORTS = ROOT / "parsebench/reports"
RUN_DIR = ROOT / "parsebench/data/runs/ppdoclayoutv3_lean_qwen/chart"


def _answers(model: str) -> dict[str, dict]:
    """This model's page answers, keyed by page stem."""
    out = {}
    for path in sorted((ANALYSIS / model).glob("*.json")):
        if path.name in ("overview.json", "failures.json"):
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        out[record["stem"]] = record["answer"]
    return out


def _optional(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", type=Path, default=RUN_DIR)
    ap.add_argument("--out", type=Path, default=REPORTS)
    args = ap.parse_args()

    summary = json.loads((STATS / "analysis_summary.json").read_text(encoding="utf-8"))
    stats = json.loads((STATS / f"failures_{args.run.parent.name}.json").read_text())
    sample = json.loads((STATS / "analysis_sample.json").read_text())
    verdicts = _optional(ANALYSIS / "verdicts.json") or {"verdicts": {}}
    models = summary["models"]

    rules = load_rules()
    run_rules = run_lib.load_rules(ROOT / "parsebench/data/raw/chart.jsonl")
    run = run_lib.load_run(args.run, run_rules, run_lib.run_model(args.run))
    run_forms = form_lib.classify_all(run.failures(), run.pages)
    kinds: dict[str, list[str]] = defaultdict(list)
    for key, form in run_forms.items():
        kinds[key.split("/", 1)[0]].append(form.kind)
    passed = {stem: {v.rule.id: v.passed for v in verdict_list}
              for stem, verdict_list in run.by_page().items()}

    answers = {model: _answers(model) for model in models}
    (args.out / "pages").mkdir(parents=True, exist_ok=True)
    for page in sample["pages"]:
        stem = page["stem"]
        text = page_report.render(
            page, rules.get(stem, []),
            {model: answers[model].get(stem) for model in models}, models,
            summary, verdicts["verdicts"], passed.get(stem, {}))
        (args.out / "pages" / f"{stem}.md").write_text(text, encoding="utf-8")
    print(f"{len(sample['pages'])} page files -> {args.out / 'pages'}")

    overviews, failures = {}, {}
    for model in models:
        overview = _optional(ANALYSIS / model / "overview.json")
        failure = _optional(ANALYSIS / model / "failures.json")
        if overview:
            overviews[model] = overview["answer"]
        if failure:
            failures[model] = failure["answer"]
        text = model_report.render(model, overviews.get(model), failures.get(model),
                                   summary, stats)
        (args.out / f"{model}.md").write_text(text, encoding="utf-8")
        print(f"  {model}.md  overview={'有' if overview else '无'} "
              f"failures={'有' if failure else '无'}")

    mechanisms = mechanism_lib.build(models, stats["failures"])
    (args.out / "compare.md").write_text(
        compare.render(summary, stats, mechanisms, kinds, overviews,
                       verdicts.get("mechanisms")), encoding="utf-8")
    print(f"compare.md -> {args.out / 'compare.md'}")


if __name__ == "__main__":
    main()
