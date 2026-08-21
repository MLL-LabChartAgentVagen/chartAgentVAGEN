"""Ask one model to report on its own sampled pages.

It is handed two things: the program's counts over the answers of all three models
-- its own column among them -- and its own page reports as it wrote them.
The counts are what the prose has to argue from; a report written from memory of its
own answers cannot be checked against anything.

`numbers_cited` is the reason the prose is worth putting in a schema at all. Every
number the report uses comes back as a field with the table it came from, so the
program can hold each one against its own table. That check does not exist unless
the models write reports.

Usage:
    python parsebench/tools/analysis/overview.py --model claude-opus-5
    python parsebench/tools/analysis/overview.py --model gpt-5.6-sol --via openrouter
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "parsebench" / "tools")]

from analysis import prompt as prompts                       # noqa: E402
from contract import format as contract                      # noqa: E402
from llmkit import LLM                                       # noqa: E402
from llmkit.providers import GATEWAYS, provider_for, provider_via   # noqa: E402
from report import tables                                    # noqa: E402

ANALYSIS = ROOT / "parsebench/data/analysis"
SUMMARY = ROOT / "parsebench/data/stats/analysis_summary.json"
CACHE = ROOT / "parsebench/data/cache/llm/overview"


def own_reports(model: str) -> str:
    """This model's own page reports, in page order, as it wrote them."""
    blocks = []
    for path in sorted((ANALYSIS / model).glob("*.json")):
        # The directory also holds this model's failure answers and its own overview.
        # Only per-page answers belong in the prompt, and only they carry `stem`.
        if path.name in ("failures.json", "overview.json"):
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        blocks.append(f"### {record['stem']}\n{record['answer']['report_md'].strip()}")
    return "\n\n".join(blocks)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True)
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--max-tokens", type=int, default=32000)
    ap.add_argument("--via", default="", choices=("", *GATEWAYS),
                    help="reach the model through an OpenAI-compatible gateway instead of "
                         "its own account; same model, same request")
    args = ap.parse_args()

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    reports = own_reports(args.model)
    user = prompts.overview_user(tables.brief_for_sample(summary), reports,
                                 n_pages=len(summary["pages"]))

    provider = provider_via(args.via) if args.via else provider_for(args.model)
    llm = LLM(args.model, provider=provider, effort=args.effort,
              max_tokens=args.max_tokens, cache_dir=CACHE)
    started = time.monotonic()
    answer = llm.json(prompts.OVERVIEW_SYSTEM, user, schema=contract.OVERVIEW_SCHEMA)
    seconds = round(time.monotonic() - started, 1)

    out = ANALYSIS / args.model / "overview.json"
    out.write_text(json.dumps({
        "model": args.model, "effort": args.effort, "via": args.via, "seconds": seconds,
        "usage": llm.usage.__dict__, "answer": answer,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{args.model}: {seconds}s  in={llm.usage.input_tokens} out={llm.usage.output_tokens}")
    print("  headline:", answer["headline"])
    for item in answer["ranked_items"]:
        print(f"    · {item['what']}  → {item['maps_to']}  affects={item['affects']}")
    print(f"  {len(answer['numbers_cited'])} numbers cited")
    print(f"written to {out}")


if __name__ == "__main__":
    main()
