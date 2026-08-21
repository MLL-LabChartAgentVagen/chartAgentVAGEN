"""Ask the models about the sampled pages, and keep every answer.

One call per (model, page): the whole page at 150 dpi, the page's spot-check values,
and `format.PAGE_SCHEMA` back. Three models answer the same sampled pages, so the
answers can be put side by side per page and per field.

Two of the runs are controls rather than observers, and neither is optional
(`format.CONTROLS`):

    no_vocab   one model, the same pages, no list of 65 component keys in the
               prompt. Its free names are mapped back to the vocabulary afterwards;
               a low overlap says the list is manufacturing the agreement.
    repeat     one model, the same pages and the same prompt, answered again. Two
               runs of one model disagree on `hardest_step` and `marks`, and that
               disagreement is the noise floor the cross-model differences sit on.

`repeat` gets its own cache directory rather than an altered prompt: the prompt has
to stay identical for the two runs to be the same question, and a cached reply would
otherwise return the first answer.

Usage:
    python parsebench/tools/analysis/run.py --model claude-opus-5
    python parsebench/tools/analysis/run.py --model gemini-3.1-pro-preview --control no_vocab
    python parsebench/tools/analysis/run.py --model gpt-5.6-sol --via openrouter
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "parsebench" / "tools")]

from analysis import prompt as prompts           # noqa: E402
from analysis.rules import load_rules            # noqa: E402
from contract import format as contract          # noqa: E402
from llmkit import LLM, Image                    # noqa: E402
from llmkit.providers import GATEWAYS, provider_for, provider_via   # noqa: E402

SAMPLE = ROOT / "parsebench/data/stats/analysis_sample.json"
PAGES = ROOT / "parsebench/data/pages"
ANSWERS = ROOT / "parsebench/data/analysis"
CACHE = ROOT / "parsebench/data/cache/llm"

#: The one exception the design allows: a reply that describes nothing. Every page in
#: this split carries spot-check points, so it carries a figure, and an empty
#: `figures` list is a degenerate reply rather than a finding about the page.
RETRY_NOTE = """

---

This page carries spot-check points, so it holds at least one figure. An empty
`figures` list is not an answer for it, and neither is a placeholder. Look again and
describe every figure on the page."""

CONTROLS = ("no_vocab", "repeat")


def sample_pages() -> list[dict]:
    return json.loads(SAMPLE.read_text())["pages"]


def run_dir(model: str, control: str) -> Path:
    """Where one run's answers live. A control is a run of its own, not an overwrite."""
    return ANSWERS / (f"{model}__{control}" if control else model)


def answer_page(llm: LLM, page: dict, values: tuple[str, ...], control: str,
                via: str = "") -> dict:
    """One page, one model. Returns the answer with the call's own cost beside it."""
    user = (prompts.page_user_free if control == "no_vocab" else prompts.page_user)(values)
    schema = prompts.free_page_schema() if control == "no_vocab" else contract.PAGE_SCHEMA
    image = Image.from_path(PAGES / f"{page['stem']}.png")

    started = time.monotonic()
    answer = llm.json(prompts.SYSTEM, user, schema=schema, images=[image])
    retried = False
    if not answer.get("figures"):
        retried = True
        answer = llm.json(prompts.SYSTEM, user + RETRY_NOTE, schema=schema, images=[image])
    return {
        "stem": page["stem"], "document": page["document"], "tags": page["tags"],
        "model": llm.model, "control": control, "effort": llm.effort, "dpi": 150,
        "via": via,
        "max_tokens": llm.max_tokens,
        "seconds": round(time.monotonic() - started, 1),
        "usage": llm.usage.__dict__, "retried_on_empty": retried,
        "answer": answer,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True)
    ap.add_argument("--control", default="", choices=("", *CONTROLS))
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--max-tokens", type=int, default=32000,
                    help="a ceiling, not a target: raising it changes nothing for a reply "
                         "that already fit. On Gemini it covers the thinking tokens too, "
                         "and one model needs twice the default to answer this schema")
    ap.add_argument("--via", default="", choices=("", *GATEWAYS),
                    help="reach the model through an OpenAI-compatible gateway instead of "
                         "its own account. Same model and same request; use it when a "
                         "direct account is unavailable, and the answers record it")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--redo", action="store_true", help="answer pages that already have a file")
    args = ap.parse_args()

    out = run_dir(args.model, args.control)
    out.mkdir(parents=True, exist_ok=True)
    rules = load_rules()
    pages = [p for p in sample_pages()
             if args.redo or not (out / f"{p['stem']}.json").exists()]
    if not pages:
        print(f"{out.name}: every page already answered")
        return

    # A control that reuses the cache would replay the first run instead of asking again.
    cache = CACHE / (args.control or "main")
    # The gateway is not part of the cache key: it is the same model answering the
    # same question, so a reply already on hand is the reply, whichever route it came by.
    provider = provider_via(args.via) if args.via else provider_for(args.model)

    def one(page: dict) -> str:
        llm = LLM(args.model, provider=provider, effort=args.effort,
                  max_tokens=args.max_tokens, cache_dir=cache)
        values = tuple(rule.value for rule in rules.get(page["stem"], ()))
        try:
            record = answer_page(llm, page, values, args.control, via=args.via)
        except Exception as exc:                     # one page must not stop the batch
            return f"  {page['stem']:<50} FAILED {type(exc).__name__}: {exc}"
        (out / f"{page['stem']}.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        answer = record["answer"]
        return (f"  {page['stem']:<50} {record['seconds']:6.1f}s  "
                f"figures={len(answer['figures']):<2} "
                f"components={len(answer['components']):<3} "
                f"new={len(answer['new_components'])}"
                + ("  (re-asked)" if record["retried_on_empty"] else ""))

    print(f"{args.model}{' · ' + args.control if args.control else ''}"
          f"{' · via ' + args.via if args.via else ''}: "
          f"{len(pages)} pages, {args.workers} at a time")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for line in pool.map(one, pages):
            print(line, flush=True)
    print(f"written to {out}")


if __name__ == "__main__":
    main()
