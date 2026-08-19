"""Analyse the sampled ParseBench pages: one report per page, plus the index.

One call per page: the whole page at 150 dpi, one structured answer, no cropping,
no OCR, no tools, no second turn. What is being measured are large-scale
structural features -- a shared legend, a second value axis, a reference line, a
two-level tick row -- and those are legible on a whole page. The design and what
was tried instead: `parsebench/review/05_analysis_design.md`.

Each page's prompt carries that page's spot-check *values*, so the answer has to
be about this page rather than about report pages in general. The *labels* those
values are addressed by stay out, which is what keeps `checks.crosscheck` a grader
rather than an echo.

Replies are cached under `(prompt, image, model)`, so enlarging the sample only
calls the model for the pages that were added.

Usage:
    python parsebench/tools/analysis/analyze_pages.py --dry-run   # print the prompt, call nothing
    python parsebench/tools/analysis/analyze_pages.py --limit 3   # try three pages
    python parsebench/tools/analysis/analyze_pages.py             # the whole sample
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from llmkit import LLM, Image  # noqa: E402

from checks import Finding, PageResult, crosscheck, reconcile  # noqa: E402
from index import countable_figures, render_index, summary_json  # noqa: E402
from viewer import render_viewer, write_assets  # noqa: E402
from prompt import RETRY_NOTE, SYSTEM, user_prompt  # noqa: E402
from report import write_report  # noqa: E402
from rules import attribute, load_rules  # noqa: E402
from schema import SCHEMA  # noqa: E402

PARSEBENCH = REPO_ROOT / "parsebench"
DEFAULT_SAMPLE = PARSEBENCH / "data" / "stats" / "analysis_sample.json"
DEFAULT_JSONL = PARSEBENCH / "data" / "raw" / "chart.jsonl"
DEFAULT_PAGES = PARSEBENCH / "data" / "pages"
DEFAULT_REPORTS = PARSEBENCH / "reports"
DEFAULT_CACHE = PARSEBENCH / "data" / "cache" / "llm"
DEFAULT_SUMMARY = PARSEBENCH / "data" / "stats" / "analysis_summary.json"

#: The budget the second attempt gets. A handful of pages carry three dense
#: figures and run past the default; everything else fits well inside it.
#: Kept under the point where the SDK requires a streaming request -- this path
#: is a rescue for a few pages, not a reason to restructure the call.
RETRY_TOKENS = 16000


def page_image(pages_dir: Path, stem: str) -> Image:
    path = pages_dir / f"{stem}.png"
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing. Run parsebench/tools/dataset/render_pages.py")
    return Image.from_path(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, default=DEFAULT_SAMPLE)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL)
    parser.add_argument("--pages-dir", type=Path, default=DEFAULT_PAGES)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_REPORTS)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--model", default="claude-opus-5")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--max-tokens", type=int, default=12000,
                        help="output budget per page; part of the cache key")
    parser.add_argument("--limit", type=int, default=0, help="analyse only the first N pages")
    parser.add_argument("--only", nargs="*", default=None, help="analyse only these page stems")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the prompt and the first page's inputs, call nothing")
    args = parser.parse_args()

    sample = json.loads(args.sample.read_text())
    selected = sample["pages"]
    if args.only:
        selected = [p for p in selected if p["stem"] in set(args.only)]
    if args.limit:
        selected = selected[: args.limit]
    if not selected:
        raise SystemExit("no pages selected")

    rules_by_stem = load_rules(args.jsonl)
    prompts = {page["stem"]: user_prompt(tuple(r.value for r in rules_by_stem.get(page["stem"], [])))
               for page in selected}

    if args.dry_run:
        first = selected[0]["stem"]
        print(f"system ({len(SYSTEM)} chars)\n{'-' * 60}\n{SYSTEM}\n")
        print(f"user for {first} ({len(prompts[first])} chars)\n{'-' * 60}\n{prompts[first]}\n")
        print(f"{'-' * 60}\n{len(selected)} pages, first is {first} "
              f"with {len(rules_by_stem[first])} rules")
        return

    llm = LLM(model=args.model, effort=args.effort, cache_dir=args.cache_dir,
              max_tokens=args.max_tokens)
    images = [page_image(args.pages_dir, page["stem"]) for page in selected]
    failures: list[Exception] = []
    answers = llm.map([(SYSTEM, prompts[page["stem"]], (image,))
                       for page, image in zip(selected, images)],
                      workers=args.workers, schema=SCHEMA, on_error=failures.append)

    #: A page dense enough to run past the budget gets one more try with a larger
    #: one. `max_tokens` is part of the cache key, so this is a second key rather
    #: than a re-bill of the pages that already fit -- only the pages that failed
    #: are called again, and they stay cached under the larger budget afterwards.
    spacious: LLM | None = None
    results: list[PageResult] = []
    for page, answer, image in zip(selected, answers, images):
        reasked: list[Finding] = []
        if answer is None:
            print(f"  no reply, trying again with max_tokens={RETRY_TOKENS}: {page['stem']}")
            spacious = spacious or LLM(model=args.model, effort=args.effort,
                                       cache_dir=args.cache_dir, max_tokens=RETRY_TOKENS)
            try:
                answer = spacious.json(SYSTEM, prompts[page["stem"]],
                                       schema=SCHEMA, images=(image,))
            except Exception as error:  # noqa: BLE001 -- reported, not handled
                print(f"  FAIL {page['stem']}: {type(error).__name__}: {str(error)[:120]}")
                failures.append(error)
                continue
            reasked = [Finding("retried_with_a_larger_budget",
                               f"the first reply did not come back at max_tokens="
                               f"{args.max_tokens}")]
        if not (answer.get("figures") or []):
            # The only re-ask in this pipeline. Every page in this split carries
            # spot-check points, so an empty answer describes the reply, not the page.
            print(f"  empty answer, asking once more: {page['stem']}")
            second = llm.json(SYSTEM, prompts[page["stem"]] + RETRY_NOTE,
                              schema=SCHEMA, images=(image,))
            if second.get("figures"):
                answer = second
                reasked = reasked + [Finding("reasked_after_an_empty_answer",
                                             "the first reply described no figure")]
        rules = rules_by_stem.get(page["stem"], [])
        attribution = attribute(rules, answer.get("figures") or [])
        result = PageResult(
            stem=page["stem"], document=page["document"], tags=page["tags"],
            analysis=answer, rules=rules, attribution=attribution,
            findings=reasked + reconcile(answer)
            + crosscheck(answer, rules, page["tags"], attribution))
        results.append(result)
        write_report(args.out_dir / "pages" / page["stem"], result,
                     args.pages_dir / f"{page['stem']}.png")

    if not results:
        raise SystemExit(f"every page failed; first error: {failures[0] if failures else '?'}")

    summary = summary_json(results, args.model)
    # The index is a frequency table over the whole sample. Writing one from a
    # `--limit` or `--only` run would overwrite it with counts out of a different
    # denominator, and nothing in the file would say so.
    whole_sample = len(results) == len(sample["pages"])
    if whole_sample:
        (args.out_dir / "INDEX.md").write_text(render_index(results, args.model), encoding="utf-8")
        assets = write_assets(results, args.out_dir, args.pages_dir)
        (args.out_dir / "view.html").write_text(
            render_viewer(results, args.model, assets=assets), encoding="utf-8")
        if not assets:
            print("  no Pillow: view.html links ../data/pages/, which only resolves "
                  "on a plain file:// open")
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    usage = llm.usage
    print(f"analysed {len(results)} of {len(selected)} pages -> {args.out_dir}/pages")
    print(f"  {summary['rules']} spot-check points, {summary['figures']} figures, "
          f"{summary['unreadable_pages']} pages with an entry the model itself ruled out")
    if not whole_sample:
        print(f"  part of the {len(sample['pages'])}-page sample: INDEX.md and the summary "
              f"are left alone")
    print(f"  tokens: {usage.input_tokens} in, {usage.output_tokens} out "
          f"(a cache hit costs nothing and is not counted)")
    for error in failures[:5]:
        print(f"  error: {type(error).__name__}: {str(error)[:200]}")


if __name__ == "__main__":
    main()
