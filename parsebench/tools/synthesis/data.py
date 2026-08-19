"""Everything the merged view reads, loaded once.

The merged report has two evidence bases and must not recompute either of them. The
page analysis already wrote one `analysis.json` per page and the failure analysis
already wrote one summary JSON, so both are read back rather than regenerated -- the
only thing rebuilt here is the failure run itself, because the parser's own table
excerpts are geometry that no summary keeps.

Reading back means this module reproduces `PageResult` from what `checks.to_json`
wrote. That is the one place the two directories touch, and it is read-only in both
directions: nothing here writes under `reports/` or `failures/`.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

PARSEBENCH = Path(__file__).resolve().parents[2]
#: Both tool packages use bare module names and both define an `index` and a
#: `viewer`. Analysis goes on first so those two resolve to the page analysis, which
#: is the one this module reads; nothing here imports either module from `failures/`.
for package in ("failures", "analysis"):
    sys.path.insert(0, str(PARSEBENCH / "tools" / package))

from checks import PageResult  # noqa: E402
from rules import Rule  # noqa: E402
import evidence as ev  # noqa: E402
from pages import load_profiles, page_words  # noqa: E402
from run import Run, load_rules, load_run, run_model  # noqa: E402
from stats import Analysis, analyse, matcher_agreement  # noqa: E402

ASSET_WIDTH = 900
ASSET_QUALITY = 78
DEFAULT_RUN = "ppdoclayoutv3_lean_qwen"


@dataclass
class Sources:
    """The two analyses plus the run, joined only by the page stem."""

    pages: list[PageResult]
    documents: int
    stats: dict
    run: Run
    analysis: Analysis

    def stat_component(self, key: str) -> dict | None:
        return next((c for c in self.stats["components"] if c["key"] == key), None)


def load_pages(reports_dir: Path) -> list[PageResult]:
    """The page analysis, read back from what it wrote under `reports/pages/`."""
    out: list[PageResult] = []
    for path in sorted(reports_dir.glob("*/analysis.json")):
        blob = json.loads(path.read_text(encoding="utf-8"))
        rules, attribution = [], []
        for row in blob.get("rules") or ():
            rules.append(Rule(value=str(row["value"]), labels=tuple(row.get("labels") or ()),
                              tolerance=float(row.get("tolerance") or 0.0),
                              max_diffs=int(row.get("max_diffs") or 0)))
            attribution.append(row.get("figure"))
        analysis = {k: v for k, v in blob.items()
                    if k not in ("stem", "document", "tags", "rules", "crosscheck")}
        out.append(PageResult(stem=blob["stem"], document=blob["document"],
                              tags=blob.get("tags", ""), analysis=analysis,
                              rules=rules, attribution=attribution))
    return out


def load_sources(run_name: str = DEFAULT_RUN) -> Sources:
    pages = load_pages(PARSEBENCH / "reports" / "pages")
    stats = json.loads((PARSEBENCH / "data" / "stats" / f"failures_{run_name}.json")
                       .read_text(encoding="utf-8"))
    run_dir = PARSEBENCH / "data" / "runs" / run_name / "chart"
    if not run_dir.exists():
        raise SystemExit(f"{run_dir} is missing. Unpack the run into data/runs/{run_name}/")
    rules = load_rules(PARSEBENCH / "data" / "raw" / "chart.jsonl")
    run = load_run(run_dir, rules, run_model(run_dir))
    analysis = analyse(run, load_profiles(PARSEBENCH / "reports" / "pages"), rules,
                       matcher_agreement(run),
                       page_words(PARSEBENCH / "data" / "raw" / "docs" / "chart"))
    return Sources(pages=pages, documents=len({p.document for p in pages}),
                   stats=stats, run=run, analysis=analysis)


def failure_evidence(sources: Sources, stem: str, kind: str):
    """The parser's own table around one failed point, plus what would have passed.

    Picks the failure whose diagnosis matches the form the page is illustrating, so
    a page shown under `unit_mismatch` does not open on its one unrelated `value_off`.
    """
    verdicts = sources.run.by_page()[stem]
    failed = [v for v in verdicts if not v.passed]
    if not failed:
        return None
    focus = next((v for v in failed
                  if sources.analysis.diagnoses[(v.rule.stem, v.rule.id)].kind == kind),
                 failed[0])
    diagnosis = sources.analysis.diagnoses[(focus.rule.stem, focus.rule.id)]
    item = ev.build(focus, sources.run.pages[stem], diagnosis)
    return focus, diagnosis, item, ev.expected(failed), len(verdicts) - len(failed), len(verdicts)


def write_assets(stems: list[str], out_dir: Path, pages_dir: Path) -> bool:
    """One downscaled JPEG per illustrated page, below the view. False without Pillow."""
    try:
        from PIL import Image
    except ImportError:
        return False
    directory = out_dir / "assets"
    directory.mkdir(parents=True, exist_ok=True)

    def convert(stem: str) -> None:
        source, target = pages_dir / f"{stem}.png", directory / f"{stem}.jpg"
        if target.exists() or not source.exists():
            return
        image = Image.open(source).convert("RGB")
        height = round(ASSET_WIDTH * image.height / image.width)
        image.resize((ASSET_WIDTH, height), Image.LANCZOS).save(
            target, quality=ASSET_QUALITY, optimize=True)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(convert, sorted(set(stems))))
    return True
