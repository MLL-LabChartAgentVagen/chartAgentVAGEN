"""Join the run's verdicts to what the pages actually look like.

The evaluation report knows a point failed; it does not know the point sat on the
third panel of a stacked bar with 300 marks and no printed numbers. That
description exists already, for 192 of the 568 pages, in the page analysis under
`parsebench/reports/pages/`. Joining the two turns a failure count into a
statement about a drawing habit, which is the only form a data-generation pipeline
can act on.

The join is on the page stem, and inside a page on the spot-check point, so a
figure-level attribute (chart type, mark count, whether numbers are printed on the
figure) reaches the individual rule rather than being averaged over the page.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

from run import Rule, Verdict


@dataclass(frozen=True)
class Figure:
    """One figure as the page analysis described it."""

    stem: str
    id: str
    type: str
    type_other: str
    panels: int
    series: int
    categories: int
    marks: int
    values_printed: str
    placement: str
    orientation: str

    @property
    def named_type(self) -> str:
        return f"other · {self.type_other}" if self.type == "other" and self.type_other else self.type


@dataclass
class PageProfile:
    """One analysed page: its figures, its components, and the rule-to-figure map."""

    stem: str
    document: str
    tags: str
    hardest_step: int
    figures: dict[str, Figure] = field(default_factory=dict)
    components: set[str] = field(default_factory=set)
    #: (value, labels) -> figure id, as the page analysis attributed them.
    attribution: dict[tuple[str, tuple[str, ...]], str] = field(default_factory=dict)

    def figure_of(self, rule: Rule) -> Figure | None:
        key = (str(rule.value), tuple(rule.labels))
        figure_id = self.attribution.get(key)
        return self.figures.get(figure_id) if figure_id else None


def load_profiles(pages_dir: Path) -> dict[str, PageProfile]:
    """Every `analysis.json` written by the page analysis, keyed by stem."""
    out: dict[str, PageProfile] = {}
    for path in sorted(pages_dir.glob("*/analysis.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        profile = PageProfile(
            stem=data["stem"], document=data.get("document", ""),
            tags=data.get("tags", ""), hardest_step=int(data.get("hardest_step") or 0))
        for figure in data.get("figures") or ():
            heading = figure.get("heading") or {}
            profile.figures[str(figure.get("id"))] = Figure(
                stem=profile.stem, id=str(figure.get("id")),
                type=str(figure.get("type") or ""),
                type_other=str(figure.get("type_other") or ""),
                panels=int(figure.get("panels") or 1),
                series=int(figure.get("series") or 0),
                categories=int(figure.get("categories") or 0),
                marks=int(figure.get("marks") or 0),
                values_printed=str(figure.get("values_printed") or ""),
                placement=str(heading.get("placement") or ""),
                orientation=str(figure.get("orientation") or ""))
        profile.components = {str(c.get("key")) for c in data.get("components") or ()}
        for rule in data.get("rules") or ():
            key = (str(rule.get("value")), tuple(str(x) for x in rule.get("labels") or ()))
            if rule.get("figure"):
                profile.attribution[key] = str(rule["figure"])
        out[profile.stem] = profile
    return out


@dataclass
class Joined:
    """One verdict with whatever the page analysis knows about where it sits."""

    verdict: Verdict
    profile: PageProfile
    figure: Figure | None

    @property
    def passed(self) -> bool:
        return self.verdict.passed


def join(verdicts: list[Verdict], profiles: dict[str, PageProfile]) -> list[Joined]:
    out = []
    for verdict in verdicts:
        profile = profiles.get(verdict.rule.stem)
        if profile is None:
            continue
        out.append(Joined(verdict, profile, profile.figure_of(verdict.rule)))
    return out


# --------------------------------------------------------------------- counting


@dataclass(frozen=True)
class Rate:
    """A pass rate with the interval that says how much of it to believe."""

    total: int
    passed: int

    @property
    def value(self) -> float:
        return self.passed / self.total if self.total else 0.0

    @property
    def interval(self) -> tuple[float, float]:
        """Wilson, 95%. Reported because half these cells hold fewer than 100 points."""
        n = self.total
        if not n:
            return (0.0, 0.0)
        z, p = 1.96, self.value
        centre = (p + z * z / (2 * n)) / (1 + z * z / n)
        half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        return (max(0.0, centre - half), min(1.0, centre + half))

    @property
    def margin(self) -> float:
        low, high = self.interval
        return (high - low) / 2


def rate(items: list, predicate=lambda item: True) -> Rate:
    chosen = [item for item in items if predicate(item)]
    return Rate(len(chosen), sum(1 for item in chosen if item.passed))


def group(items: list, key) -> dict[object, Rate]:
    """Pass rate per value of `key`; entries whose key is None are dropped."""
    buckets: dict[object, list] = {}
    for item in items:
        value = key(item)
        if value is None:
            continue
        buckets.setdefault(value, []).append(item)
    return {name: Rate(len(rows), sum(1 for row in rows if row.passed))
            for name, rows in buckets.items()}


#: Body-text bands, cut at the quartiles of the split's own distribution.
TEXT_BANDS = ((0, 240, "≤240 词"), (240, 360, "241–360 词"),
              (360, 500, "361–500 词"), (500, 10 ** 9, ">500 词"))


def page_words(pdf_dir: Path) -> dict[str, int]:
    """Words on each page, from the PDF text layer. Empty without PyMuPDF.

    The page analysis already reported the distribution over the split; what is
    needed here is the per-page number, so the improvement list can say whether
    body-text volume is associated with failure instead of assuming it is not.
    """
    try:
        import pymupdf
    except ImportError:
        return {}
    out = {}
    for path in sorted(pdf_dir.glob("*.pdf")):
        with pymupdf.open(path) as document:
            out[path.stem] = len(document[0].get_text().split())
    return out


def text_band(words: int | None) -> str | None:
    if words is None:
        return None
    for low, high, name in TEXT_BANDS:
        if low < words <= high:
            return name
    return TEXT_BANDS[0][2]


#: Mark-count bands. The top one is where `chart_types.md` cannot currently reach.
DENSITY_BANDS = ((0, 20, "≤20"), (20, 60, "21–60"), (60, 150, "61–150"),
                 (150, 400, "151–400"), (400, 10 ** 9, ">400"))


def density_band(marks: int) -> str | None:
    if marks <= 0:
        return None
    for low, high, name in DENSITY_BANDS:
        if low < marks <= high:
            return name
    return None


def separated(a: Rate, b: Rate) -> bool:
    """True when the two intervals do not overlap -- the only claims worth making."""
    return a.interval[1] < b.interval[0] or b.interval[1] < a.interval[0]
