"""Answer one real page against the contract, with one model.

A check on the contract, not an analysis: it asks whether a model can fill
`format.PAGE_SCHEMA` from a whole page image at all, and whether the three vendor paths
that have to be equivalent -- image in, one JSON schema back, reasoning effort set
-- work for the model named. The prompt here is the short version; the sampling,
the full instructions and the cross-model diff belong to the analysis run.

Replies are cached under `(prompt, image, provider, model)`, so re-running the
same model costs nothing and two models never overwrite each other.

Usage:
    python parsebench/tools/contract/try_page.py --model gemini-3.1-pro-preview
    python parsebench/tools/contract/try_page.py --model gpt-5.2 --effort medium
    python parsebench/tools/contract/try_page.py --model claude-opus-5 --page <stem>

`--base-url` with `--api-key-env` points the OpenAI path at a compatible gateway
instead of the vendor's own endpoint.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "parsebench" / "tools")]

from contract import format as contract, vocabulary   # noqa: E402
from llmkit import LLM, Image                  # noqa: E402

#: A page with two grouped-bar figures and five spot checks, all of them printed
#: on the figure -- enough structure to fill every field, small enough to read.
DEFAULT_PAGE = "(Web_version)_E-Government_Survey_2024_1392024_p170"

SYSTEM = ("You describe one page of a published report so that a chart-generation "
          "pipeline can be compared against it. Answer only in the given JSON schema. "
          "Every component you report carries the words on the page that show it.")

USER = """Here is one page of a report, rendered whole at 150 dpi.

Report every figure on it, every component from the fixed vocabulary below that is
present, and how each of the listed spot-check values would be addressed in a table.
The labels those values are addressed by are deliberately withheld: say which keys a
table row would need, from what you can see.

Spot-check values on this page: {values}

Vocabulary (key -- what to look for):
{vocab}
"""


def rules_for(stem: str) -> list[dict]:
    """This page's spot checks, straight out of the annotation file."""
    lines = (ROOT / "parsebench/data/raw/chart.jsonl").read_text().splitlines()
    return [json.loads(json.loads(line)["rule"]) for line in lines
            if stem in json.loads(line)["pdf"]]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True)
    ap.add_argument("--page", default=DEFAULT_PAGE)
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--max-tokens", type=int, default=32000,
                    help="on Gemini this covers the thinking tokens as well as the reply")
    ap.add_argument("--base-url", default=None,
                    help="an OpenAI-compatible endpoint other than the default")
    ap.add_argument("--api-key-env", default=None,
                    help="the environment variable holding the key for that endpoint")
    args = ap.parse_args()

    provider = None
    if args.base_url:
        import os

        from llmkit.providers.openai import OpenAIProvider
        provider = OpenAIProvider(api_key=os.environ[args.api_key_env] if args.api_key_env else None,
                                  base_url=args.base_url)

    rules = rules_for(args.page)
    llm = LLM(args.model, provider=provider, effort=args.effort, max_tokens=args.max_tokens,
              cache_dir=ROOT / "parsebench/data/cache/try_page")
    image = Image.from_path(ROOT / f"parsebench/data/pages/{args.page}.png")

    started = time.monotonic()
    answer = llm.json(SYSTEM,
                      USER.format(values=", ".join(r["value"] for r in rules),
                                  vocab=vocabulary.prompt_block()),
                      schema=contract.PAGE_SCHEMA, images=[image])
    took = time.monotonic() - started

    print(f"=== {args.model}  effort={args.effort}  {took:.1f}s  "
          f"in={llm.usage.input_tokens} out={llm.usage.output_tokens}")
    print("page_note :", answer["page_note"])
    for figure in answer["figures"]:
        heading = figure["heading"]
        print(f"  {figure['id']} {figure['type']:<12} marks={figure['marks']:<4} "
              f"printed={figure['values_printed']:<5} "
              f"heading={heading['figure_number']!r} @{heading['placement']}")
    print("components:", ", ".join(sorted({c["key"] for c in answer["components"]})))
    print("new       :", [(n["name"], n["affects"]) for n in answer["new_components"]])
    for check, rule in zip(answer["spot_checks"], rules):
        hit = "=" if check["addressing_keys"] == rule["labels"] else "≠"
        print(f"  {check['value']:>7} -> {check['figure_id']:<4} {hit} "
              f"predicted={check['addressing_keys']}  actual={rule['labels']}")
    print("hardest_step:", answer["hardest_step"])
    for suggestion in answer["suggestions"]:
        print(f"  {suggestion['maps_to']} affects={suggestion['affects']} | "
              f"分数 {suggestion['score_effect'][:36]} | 能力 {suggestion['capability_effect'][:36]}")


if __name__ == "__main__":
    main()
