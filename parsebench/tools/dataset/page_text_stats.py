"""Measure how much body text sits on a ParseBench chart page.

Every page in this split is a whole report page, so a chart never arrives alone:
it is surrounded by paragraphs, a figure caption, source and note lines. How much
text is a number the generator needs, because page composition has to hit the same
register -- a synthetic page carrying one figure and three lines of text is a
different object from the pages the benchmark scores.

The text comes out of the PDF text layer, not OCR: it is exact and free.

Usage:
    python parsebench/tools/dataset/page_text_stats.py
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PDF_DIR = REPO_ROOT / "parsebench" / "data" / "raw" / "docs" / "chart"
DEFAULT_OUT = REPO_ROOT / "parsebench" / "data" / "stats" / "page_text_stats.json"

#: Below this a page is a bare figure with a caption, not a page of a report.
BARE_PAGE_WORDS = 50


def word_count(pdf: Path) -> tuple[str, int]:
    proc = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True)
    return pdf.stem, len(proc.stdout.split())


def summarize(counts: list[int]) -> dict:
    ordered = sorted(counts)
    n = len(ordered)
    return {
        "pages": n,
        "words": {"min": ordered[0], "p25": ordered[n // 4], "median": ordered[n // 2],
                  "p75": ordered[3 * n // 4], "max": ordered[-1],
                  "mean": round(statistics.fmean(ordered))},
        "pages_at_least": {str(cut): sum(w >= cut for w in ordered)
                           for cut in (BARE_PAGE_WORDS, 100, 200, 400)},
        "bare_pages": sum(w < BARE_PAGE_WORDS for w in ordered),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    pdfs = sorted(args.pdf_dir.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs under {args.pdf_dir}. Run download_chart_split.py first.")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        counted = dict(pool.map(word_count, pdfs))

    summary = summarize(list(counted.values()))
    summary["thinnest_pages"] = [s for s, _ in sorted(counted.items(), key=lambda kv: kv[1])[:5]]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    words = summary["words"]
    print(f"{summary['pages']} pages | words per page: median {words['median']}, "
          f"p25 {words['p25']}, p75 {words['p75']}, max {words['max']}")
    for cut, count in summary["pages_at_least"].items():
        print(f"  >= {cut:>3} words: {count} ({count / summary['pages']:.0%})")
    print(f"  a bare figure page (< {BARE_PAGE_WORDS} words): {summary['bare_pages']}")
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
