"""Read one parse-bench run and write the failure report beside it.

Nothing here calls a model and nothing re-scores: the inputs are the run directory
the harness produced, the split's `chart.jsonl`, and the page descriptions from the
earlier page analysis. Rerunning is free and deterministic.

Usage:
    python parsebench/tools/failures/analyze_failures.py
    python parsebench/tools/failures/analyze_failures.py --run ppdoclayoutv3_lean_qwen
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cases import write_cases  # noqa: E402
from index import render_index  # noqa: E402
from pages import load_profiles, page_words  # noqa: E402
from run import load_run, load_rules, run_model  # noqa: E402
from stats import analyse, matcher_agreement, negative_value_rate, summary_json  # noqa: E402
from viewer import illustrated_stems, render_viewer, write_assets  # noqa: E402

PARSEBENCH = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default="ppdoclayoutv3_lean_qwen",
                        help="a directory under parsebench/data/runs/")
    parser.add_argument("--runs-dir", type=Path, default=PARSEBENCH / "data" / "runs")
    parser.add_argument("--jsonl", type=Path,
                        default=PARSEBENCH / "data" / "raw" / "chart.jsonl")
    parser.add_argument("--pages-dir", type=Path, default=PARSEBENCH / "data" / "pages")
    parser.add_argument("--pdf-dir", type=Path,
                        default=PARSEBENCH / "data" / "raw" / "docs" / "chart",
                        help="read only, for the per-page body-text count")
    parser.add_argument("--profiles", type=Path,
                        default=PARSEBENCH / "reports" / "pages",
                        help="the page analysis, read only")
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--stats-dir", type=Path, default=PARSEBENCH / "data" / "stats")
    parser.add_argument("--no-assets", action="store_true",
                        help="skip the downscaled page images the viewer reads")
    args = parser.parse_args()

    run_dir = args.runs_dir / args.run / "chart"
    if not run_dir.exists():
        raise SystemExit(f"{run_dir} is missing. Unpack the run into data/runs/{args.run}/")
    out_dir = args.out_dir or (PARSEBENCH / "failures" / args.run)

    rules = load_rules(args.jsonl)
    run = load_run(run_dir, rules, run_model(run_dir))
    profiles = load_profiles(args.profiles)
    words = page_words(args.pdf_dir)
    analysis = analyse(run, profiles, rules, matcher_agreement(run), words)
    negative = negative_value_rate(run)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "INDEX.md").write_text(render_index(analysis, negative), encoding="utf-8")
    written = write_cases(out_dir / "cases", run, analysis, args.pages_dir)
    illustrated = illustrated_stems(written, analysis)
    assets = False if args.no_assets else write_assets(illustrated, out_dir, args.pages_dir)
    (out_dir / "view.html").write_text(
        render_viewer(analysis, written, negative, run, assets=assets), encoding="utf-8")

    args.stats_dir.mkdir(parents=True, exist_ok=True)
    summary = summary_json(analysis)
    summary["negative_value_rate"] = round(negative, 4)
    (args.stats_dir / f"failures_{args.run}.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    failures = sum(analysis.kinds.values())
    print(f"{args.run}: {analysis.pages} pages, {analysis.points} points, "
          f"{failures} failures, page mean {analysis.page_mean:.2%}")
    for kind, count in analysis.kinds.most_common():
        print(f"  {count:4d}  {kind}")
    print(f"-> {out_dir}/INDEX.md · view.html · {len(written)} cases · "
          f"{len(illustrated)} page images")
    print(f"-> {args.stats_dir}/failures_{args.run}.json")
    if not assets:
        print("  no assets written: view.html links ../../data/pages/")


if __name__ == "__main__":
    main()
