"""Draw the pages this round of the analysis runs on.

Uniform at random over the split's 568 pages, so a component's frequency on the
sample is an unbiased estimate of its frequency in the benchmark -- that table is
read as an ordering of what to build, and any steering of the draw would take that
reading away.

The draw is staged, and every stage keeps the ones before it. The first stage drew
twenty pages; the second widened the sample to a hundred. A stage draws uniformly
from the pages no earlier stage took, so the union is still a uniform sample of the
split -- and the pages already answered keep their answers, their adjudications and
their place in the report.

Adding a stage is one entry in `STAGES`. Never change an existing one: its seed is
what makes the pages already on disk reproducible.

Usage:
    python parsebench/tools/analysis/sample.py            # every stage in STAGES
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_JSONL = ROOT / "parsebench/data/raw/chart.jsonl"
DEFAULT_OUT = ROOT / "parsebench/data/stats/analysis_sample.json"

PAGE_SUFFIX = re.compile(r"_p\d+\.pdf$")

#: `(seed, how many this stage adds)`, oldest first. Append only.
STAGES: tuple[tuple[int, int], ...] = (
    (20260820, 20),
    (20260821, 80),
)


@dataclass(frozen=True)
class Page:
    """One evaluated page: one single-page PDF, and the spot-check points on it."""

    pdf: str
    document: str
    tags: str
    rules: int

    @property
    def stem(self) -> str:
        return Path(self.pdf).stem


def load_pages(path: Path) -> list[Page]:
    """Every page of the chart split, with its document-level tags."""
    grouped: dict[str, list[dict]] = defaultdict(list)
    for line in path.read_text().splitlines():
        if line.strip():
            record = json.loads(line)
            grouped[record["pdf"]].append(record)
    return [
        Page(pdf=pdf,
             document=PAGE_SUFFIX.sub("", Path(pdf).name),
             # Tags are assigned per document, so every rule on a page carries the same set.
             tags="+".join(sorted({t for r in records for t in r["tags"]})) or "untagged",
             rules=len(records))
        for pdf, records in sorted(grouped.items())
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--stages", type=int, default=len(STAGES),
                    help="how many stages of STAGES to draw; the default is all of them")
    args = ap.parse_args()

    pages = load_pages(args.jsonl)
    taken: list[Page] = []
    for seed, size in STAGES[:args.stages]:
        left = [page for page in pages if page not in taken]
        taken += random.Random(seed).sample(left, size)
    sample = sorted(taken, key=lambda p: p.pdf)

    drawn, population = Counter(p.tags for p in sample), Counter(p.tags for p in pages)
    payload = {
        "stages": [{"seed": seed, "adds": size} for seed, size in STAGES[:args.stages]],
        "seed": STAGES[0][0],
        "size": len(sample),
        "population": {"pages": len(pages), "documents": len({p.document for p in pages})},
        "drawn_by_tags": {tag: {"sampled": drawn[tag], "population": population[tag]}
                          for tag in sorted(population)},
        "documents_represented": len({p.document for p in sample}),
        "rules_covered": sum(p.rules for p in sample),
        "pages": [{"stem": p.stem, "pdf": p.pdf, "document": p.document,
                   "tags": p.tags, "rules": p.rules} for p in sample],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    stages = " + ".join(f"{size} (seed {seed})" for seed, size in STAGES[:args.stages])
    print(f"drew {len(sample)} of {len(pages)} pages, uniformly at random: {stages}")
    print(f"  {payload['documents_represented']} documents, "
          f"{payload['rules_covered']} spot-check points")
    for tag, counts in payload["drawn_by_tags"].items():
        print(f"  {tag:<26} {counts['sampled']:3d} drawn / {counts['population']} in population")
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
