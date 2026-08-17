"""Draw a stratified sample of chart pages to analyse.

Analysing all 568 pages buys little: the strata are what differ, and one source
document contributes 52 pages, so a uniform draw would mostly describe that one
document's template. This draws proportionally across the four page strata and
caps how many pages any single document may contribute.

Usage:
    python parsebench/tools/sample_pages.py --size 48
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSONL = REPO_ROOT / "parsebench" / "data" / "raw" / "chart.jsonl"
DEFAULT_OUT = REPO_ROOT / "parsebench" / "data" / "stats" / "analysis_sample.json"

PAGE_SUFFIX = re.compile(r"_p\d+\.pdf$")


@dataclass(frozen=True)
class Page:
    """One evaluated page and everything the sampler needs to stratify it."""

    pdf: str
    document: str
    stratum: str
    rules: int
    needs_estimate: int

    @property
    def stem(self) -> str:
        return Path(self.pdf).stem


@dataclass
class Stratum:
    name: str
    pages: list[Page] = field(default_factory=list)


def load_pages(path: Path) -> list[Page]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for line in path.read_text().splitlines():
        if line.strip():
            record = json.loads(line)
            grouped[record["pdf"]].append(record)

    pages: list[Page] = []
    for pdf, records in sorted(grouped.items()):
        tags = sorted({t for r in records for t in r["tags"]})
        pages.append(
            Page(
                pdf=pdf,
                document=PAGE_SUFFIX.sub("", Path(pdf).name),
                stratum="+".join(tags) or "untagged",
                rules=len(records),
                needs_estimate=sum("need_estimate" in r["tags"] for r in records),
            )
        )
    return pages


def allocate(strata: list[Stratum], size: int) -> dict[str, int]:
    """Proportional allocation with a floor of one, so a 3-page stratum is not lost."""
    total = sum(len(s.pages) for s in strata)
    quota = {s.name: max(1, round(size * len(s.pages) / total)) for s in strata}
    # Rounding and the floor both push the total around; settle it on the largest strata.
    order = sorted(strata, key=lambda s: -len(s.pages))
    while sum(quota.values()) != size:
        step = 1 if sum(quota.values()) < size else -1
        for s in order:
            if 1 <= quota[s.name] + step <= len(s.pages):
                quota[s.name] += step
                break
        else:
            break
    return quota


def draw(pages: list[Page], size: int, per_document: int, seed: int) -> list[Page]:
    strata: dict[str, Stratum] = {}
    for page in pages:
        strata.setdefault(page.stratum, Stratum(page.stratum)).pages.append(page)
    ordered = sorted(strata.values(), key=lambda s: s.name)
    quota = allocate(ordered, size)

    rng = random.Random(seed)
    taken: list[Page] = []
    used: Counter[str] = Counter()
    for stratum in ordered:
        pool = sorted(stratum.pages, key=lambda p: p.pdf)
        rng.shuffle(pool)
        want = quota[stratum.name]
        # First pass honours the per-document cap; a second pass fills any shortfall.
        for capped in (True, False):
            for page in pool:
                if len([p for p in taken if p.stratum == stratum.name]) >= want:
                    break
                if page in taken:
                    continue
                if capped and used[page.document] >= per_document:
                    continue
                taken.append(page)
                used[page.document] += 1
    return sorted(taken, key=lambda p: p.pdf)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--size", type=int, default=48)
    parser.add_argument("--per-document", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260817)
    args = parser.parse_args()

    pages = load_pages(args.jsonl)
    sample = draw(pages, args.size, args.per_document, args.seed)

    payload = {
        "seed": args.seed,
        "size": len(sample),
        "per_document_cap": args.per_document,
        "population": {"pages": len(pages), "documents": len({p.document for p in pages})},
        "by_stratum": {
            name: {"sampled": sum(p.stratum == name for p in sample),
                   "population": sum(p.stratum == name for p in pages)}
            for name in sorted({p.stratum for p in pages})
        },
        "pages": [
            {"stem": p.stem, "pdf": p.pdf, "document": p.document, "stratum": p.stratum,
             "rules": p.rules, "needs_estimate": p.needs_estimate}
            for p in sample
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    print(f"sampled {len(sample)} of {len(pages)} pages "
          f"across {len({p.document for p in sample})} documents (seed {args.seed})")
    for name, counts in payload["by_stratum"].items():
        print(f"  {name:<26} {counts['sampled']:3d} / {counts['population']}")
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
