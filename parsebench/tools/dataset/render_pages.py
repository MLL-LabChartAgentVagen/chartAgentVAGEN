"""Rasterize the ParseBench chart pages so they can be fed to a vision model.

ParseBench ships one single-page PDF per evaluated page. Our models consume
images, and every later probe (captioning, difficulty tagging, failure
analysis) reads the same rasters, so rendering happens once, here.

Usage:
    python parsebench/tools/dataset/render_pages.py --dpi 150
"""

from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PDF_DIR = REPO_ROOT / "parsebench" / "data" / "raw" / "docs" / "chart"
DEFAULT_OUT_DIR = REPO_ROOT / "parsebench" / "data" / "pages"


@dataclass(frozen=True)
class RenderJob:
    pdf: Path
    png: Path
    dpi: int


def render_one(job: RenderJob) -> tuple[Path, bool, str]:
    """Rasterize a single-page PDF with poppler's pdftoppm."""
    if job.png.exists():
        return job.png, True, "cached"
    job.png.parent.mkdir(parents=True, exist_ok=True)
    # pdftoppm appends the extension itself, so the -singlefile stem is passed.
    stem = job.png.with_suffix("")
    proc = subprocess.run(
        ["pdftoppm", "-r", str(job.dpi), "-png", "-singlefile", str(job.pdf), str(stem)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or not job.png.exists():
        return job.png, False, proc.stderr.strip() or "pdftoppm produced no output"
    return job.png, True, "rendered"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--dpi", type=int, default=150)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    pdfs = sorted(args.pdf_dir.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs under {args.pdf_dir}. Run dataset/download_chart_split.py first.")

    jobs = [RenderJob(pdf=p, png=args.out_dir / f"{p.stem}.png", dpi=args.dpi) for p in pdfs]
    failures: list[tuple[Path, str]] = []
    rendered = cached = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for png, ok, note in pool.map(render_one, jobs):
            if not ok:
                failures.append((png, note))
            elif note == "cached":
                cached += 1
            else:
                rendered += 1

    print(f"rendered {rendered}, cached {cached}, failed {len(failures)} -> {args.out_dir}")
    for png, note in failures[:10]:
        print(f"  FAIL {png.name}: {note}")


if __name__ == "__main__":
    main()
