"""Draw a random sample of chart pages to analyse.

Analysing all 568 pages is not needed to find out which chart components our
pipeline cannot draw. This draws a plain uniform sample so the component
frequencies measured on it are unbiased estimates of the population's, which
is what makes the frequency table an ordering of what to build.

The tag groups are reported, not enforced: knowing how the draw came out
across them is useful, steering it would bias the frequencies.

Usage:
    python parsebench/tools/sample_pages.py --size 48
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSONL = REPO_ROOT / "parsebench" / "data" / "raw" / "chart.jsonl"
DEFAULT_OUT = REPO_ROOT / "parsebench" / "data" / "stats" / "analysis_sample.json"

PAGE_SUFFIX = re.compile(r"_p\d+\.pdf$")


@dataclass(frozen=True)
class Page:
    """One evaluated page: one single-page PDF, and the spot-check points on it."""

    pdf: str
    document: str
    tags: str
    rules: int
    needs_estimate: int

    @property
    def stem(self) -> str:
        return Path(self.pdf).stem


def load_pages(path: Path) -> list[Page]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for line in path.read_text().splitlines():
        if line.strip():
            record = json.loads(line)
            grouped[record["pdf"]].append(record)

    return [
        Page(
            pdf=pdf,
            document=PAGE_SUFFIX.sub("", Path(pdf).name),
            # Tags are assigned per document, so every rule on a page carries the same set.
            tags="+".join(sorted({t for r in records for t in r["tags"]})) or "untagged",
            rules=len(records),
            needs_estimate=sum("need_estimate" in r["tags"] for r in records),
        )
        for pdf, records in sorted(grouped.items())
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--size", type=int, default=48)
    parser.add_argument("--seed", type=int, default=20260817)
    args = parser.parse_args()

    pages = load_pages(args.jsonl)
    sample = sorted(random.Random(args.seed).sample(pages, args.size), key=lambda p: p.pdf)

    drawn, population = Counter(p.tags for p in sample), Counter(p.tags for p in pages)
    payload = {
        "seed": args.seed,
        "size": len(sample),
        "population": {"pages": len(pages), "documents": len({p.document for p in pages})},
        "drawn_by_tags": {t: {"sampled": drawn[t], "population": population[t]} for t in sorted(population)},
        "documents_represented": len({p.document for p in sample}),
        "rules_covered": sum(p.rules for p in sample),
        "pages": [
            {"stem": p.stem, "pdf": p.pdf, "document": p.document, "tags": p.tags,
             "rules": p.rules, "needs_estimate": p.needs_estimate}
            for p in sample
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    print(f"drew {len(sample)} of {len(pages)} pages, uniformly at random (seed {args.seed})")
    print(f"  {payload['documents_represented']} documents, {payload['rules_covered']} spot-check points")
    for tag, counts in payload["drawn_by_tags"].items():
        print(f"  {tag:<26} {counts['sampled']:3d} drawn / {counts['population']} in population")
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
