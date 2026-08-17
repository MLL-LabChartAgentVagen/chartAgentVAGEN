"""Fetch the ParseBench chart split from the Hugging Face dataset repo.

Only the chart dimension is pulled: the annotation file plus the 568 source
page PDFs, about 150 MB. The other four dimensions (tables, content
faithfulness, semantic formatting, visual grounding) are left alone.

Usage:
    python parsebench/tools/download_chart_split.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download

REPO_ID = "llamaindex/ParseBench"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DEST = REPO_ROOT / "parsebench" / "data" / "raw"

# README.md and eval.yaml document the rule schema and the tag vocabulary;
# the thumbnails are the paper's own illustrative chart pages.
PATTERNS = ["chart.jsonl", "docs/chart/*", "README.md", "eval.yaml", "thumbnails/chart_*"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    path = snapshot_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        local_dir=str(args.dest),
        allow_patterns=PATTERNS,
        max_workers=args.workers,
    )
    print(f"chart split at {path}")


if __name__ == "__main__":
    main()
