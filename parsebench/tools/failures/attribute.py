"""Ask each model why the sampled failures happened, and keep every answer.

One call per model, not one per case (`format.WORKLOAD`). The per-case answer has
to stay -- three models can only be compared case by case -- but a call per case
buys nothing: the cases are text, they fit in one context, and the model that has
just read all fifty is the one that should write the report over them. So the
attributions and that model's failure overview come back together.

The model is handed the program's counts over **every** failure in the run, then the
sampled cases. It supplies the mechanism and nothing else: `passed` is the official
value, the form is computed, and `affects` is derived from the mechanism's own step.

Usage:
    python parsebench/tools/failures/attribute.py --model claude-opus-5
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "parsebench" / "tools")]

from analysis import prompt as prompts                          # noqa: E402
from contract import format as contract                         # noqa: E402
from failures import cases as case_lib                          # noqa: E402
from failures import forms as form_lib                          # noqa: E402
from failures import run as run_lib                             # noqa: E402
from llmkit import LLM                                          # noqa: E402
from llmkit.providers import provider_for                       # noqa: E402
from report import tables                                       # noqa: E402

RUN_DIR = ROOT / "parsebench/data/runs/ppdoclayoutv3_lean_qwen/chart"
ANALYSIS = ROOT / "parsebench/data/analysis"
CACHE = ROOT / "parsebench/data/cache/llm/failures"
STATS = ROOT / "parsebench/data/stats"


def build_batch(run_dir: Path, per_form: int, seed: int) -> tuple[str, list[case_lib.Case]]:
    """The prompt's case block, and the cases behind it in the same order."""
    rules = run_lib.load_rules(ROOT / "parsebench/data/raw/chart.jsonl")
    run = run_lib.load_run(run_dir, rules, run_lib.run_model(run_dir))
    forms = form_lib.classify_all(run.failures(), run.pages)
    chosen = case_lib.sample(run, forms, per_form=per_form, seed=seed)
    text = "\n\n".join(case_lib.render(case, run.pages[case.stem]) for case in chosen)
    return text, chosen


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True)
    ap.add_argument("--run", type=Path, default=RUN_DIR)
    ap.add_argument("--per-form", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20260820)
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--max-tokens", type=int, default=48000)
    args = ap.parse_args()

    summary = json.loads((STATS / f"failures_{args.run.parent.name}.json").read_text())
    case_text, chosen = build_batch(args.run, args.per_form, args.seed)
    user = prompts.failure_user(tables.brief_for_failures(summary), case_text)

    llm = LLM(args.model, provider=provider_for(args.model), effort=args.effort,
              max_tokens=args.max_tokens, cache_dir=CACHE)
    started = time.monotonic()
    answer = llm.json(prompts.FAILURE_SYSTEM, user, schema=contract.FAILURE_SCHEMA)
    seconds = round(time.monotonic() - started, 1)

    out = ANALYSIS / args.model
    out.mkdir(parents=True, exist_ok=True)
    (out / "failures.json").write_text(json.dumps({
        "model": args.model, "run": args.run.parent.name, "effort": args.effort,
        "seconds": seconds, "usage": llm.usage.__dict__,
        "seed": args.seed, "per_form": args.per_form,
        "cases": [{"case_id": c.case_id, "page": c.stem, "rule_id": c.rule.id,
                   "value": c.rule.value, "labels": list(c.rule.labels),
                   "form": c.form.to_json()} for c in chosen],
        "answer": answer,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    given = {c.case_id for c in chosen}
    got = [a["case_id"] for a in answer["attributions"]]
    print(f"{args.model}: {seconds}s  in={llm.usage.input_tokens} out={llm.usage.output_tokens}")
    print(f"  {len(got)} attributions for {len(given)} cases"
          + ("" if set(got) == given else f"; ids not given back: {sorted(given - set(got))}"))
    print("  headline:", answer["headline"])
    for item in answer["ranked_items"][:3]:
        print(f"    · {item['what']}  → {item['maps_to']}")
    print(f"written to {out / 'failures.json'}")


if __name__ == "__main__":
    main()
