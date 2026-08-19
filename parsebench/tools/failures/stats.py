"""Everything both renderers need, computed once.

Two questions, and they take different denominators. *What does failure look like*
runs over all 568 pages, because the taxonomy needs only the parser's output and the
rule. *What makes a page hard* runs over the 192 pages the page analysis described,
because it needs the chart type, the mark count and whether the figure prints its
numbers. Keeping them in one object keeps the two denominators visible side by side
instead of being quoted as one number.

Every association in `components` is measured inside a control group -- points whose
figure prints no number at all -- because whether the number is printed on the
figure moves the pass rate by 19 points and would otherwise dominate every row.
"""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from pages import (PageProfile, Rate, density_band, group, join, rate,
                     separated, TEXT_BANDS, text_band)
from run import Rule, Run, Verdict
from taxonomy import Diagnosis, diagnose

#: A cell smaller than this is printed but never used to make a claim.
MIN_POINTS = 60


@dataclass
class Association:
    """One page feature, its pass rate with and without, inside the control group."""

    key: str
    pages: int
    documents: int
    present: Rate
    absent: Rate

    @property
    def delta(self) -> float:
        return self.present.value - self.absent.value

    @property
    def separated(self) -> bool:
        return separated(self.present, self.absent)

    def to_json(self) -> dict:
        return {"key": self.key, "pages": self.pages, "documents": self.documents,
                "with": [self.present.total, round(self.present.value, 4)],
                "without": [self.absent.total, round(self.absent.value, 4)],
                "delta": round(self.delta, 4), "separated": self.separated}


@dataclass
class Analysis:
    """The whole reading of one run."""

    run: str
    model: str
    pages: int
    points: int
    page_mean: float
    micro: float
    perfect: int
    zero: int
    diagnoses: dict[str, Diagnosis]
    kinds: Counter
    homes: Counter
    #: rule id -> the verdict, so a case can print the metric's own words.
    verdicts: dict[str, Verdict] = field(default_factory=dict)
    by_arity: dict[int, Rate] = field(default_factory=dict)
    by_tag: dict[str, Rate] = field(default_factory=dict)
    by_kind_arity: dict[int, Counter] = field(default_factory=dict)
    errors: list[float] = field(default_factory=list)
    analysed_pages: int = 0
    analysed_points: int = 0
    control_points: int = 0
    control_rate: float = 0.0
    by_type: dict[str, Rate] = field(default_factory=dict)
    by_printed: dict[str, Rate] = field(default_factory=dict)
    by_density: dict[str, Rate] = field(default_factory=dict)
    by_placement: dict[str, Rate] = field(default_factory=dict)
    by_panels: dict[str, Rate] = field(default_factory=dict)
    by_predicted_step: dict[str, Rate] = field(default_factory=dict)
    by_text_band: dict[str, Rate] = field(default_factory=dict)
    family_by_density: dict[str, Counter] = field(default_factory=dict)
    components: list[Association] = field(default_factory=list)
    worst_pages: list[tuple[str, float, int, Counter]] = field(default_factory=list)
    #: Page stem -> that page's official score, for picking illustrative pages.
    page_scores: dict[str, float] = field(default_factory=dict)
    #: Page stem -> the components the page analysis found on it.
    components_by_page: dict[str, set] = field(default_factory=dict)
    #: Failure form -> the pages where it did the most damage, worst first.
    pages_by_kind: dict[str, list[str]] = field(default_factory=dict)
    matcher_agreement: float = 0.0
    #: The page-average score every addressing failure would have to become for the
    #: long-table export to be worth what the taxonomy says it is worth.
    addressing_ceiling: float = 0.0

    def costly(self, limit: int = 12) -> list[Association]:
        return [a for a in self.components if a.delta < 0 and a.separated][:limit]

    def helpful(self, limit: int = 8) -> list[Association]:
        return [a for a in reversed(self.components) if a.delta > 0 and a.separated][:limit]


def _page_scores(run: Run) -> dict[str, float]:
    return {stem: sum(v.passed for v in vs) / len(vs)
            for stem, vs in run.by_page().items() if vs}


def analyse(run: Run, profiles: dict[str, PageProfile], rules: dict[tuple[str, str], Rule],
            agreement: float = 0.0, words: dict[str, int] | None = None) -> Analysis:
    siblings: dict[str, list[Rule]] = defaultdict(list)
    for rule in rules.values():
        siblings[rule.stem].append(rule)

    #: One entry per failing point, not per rule id -- ids repeat across pages.
    results = [(verdict, diagnose(verdict, run.pages[verdict.rule.stem],
                                  siblings[verdict.rule.stem]))
               for verdict in run.failures()]
    diagnoses = {(v.rule.stem, v.rule.id): d for v, d in results}
    verdicts = {(v.rule.stem, v.rule.id): v for v, d in results}

    scores = _page_scores(run)
    kinds = Counter(d.kind for _, d in results)
    homes = Counter(home for _, d in results for home in d.homes.values())

    by_arity = {a: Rate(len([v for v in run.verdicts if v.rule.arity == a]),
                        sum(1 for v in run.verdicts if v.rule.arity == a and v.passed))
                for a in (1, 2, 3, 4)}
    tag_names = {(): "untagged", ("need_estimate",): "need_estimate",
                 ("3d_chart", "need_estimate"): "3d_chart + need_estimate",
                 ("3d_chart",): "3d_chart"}
    by_tag = {}
    for tags, name in tag_names.items():
        chosen = [v for v in run.verdicts if tuple(sorted(v.rule.tags)) == tuple(sorted(tags))]
        by_tag[name] = Rate(len(chosen), sum(1 for v in chosen if v.passed))

    by_kind_arity: dict[int, Counter] = defaultdict(Counter)
    for verdict, diagnosis in results:
        by_kind_arity[verdict.rule.arity][diagnosis.kind] += 1

    errors = sorted(d.error for _, d in results
                    if d.error is not None and d.kind in
                    ("value_off", "series_swap", "stack_confusion"))

    joined = join(run.verdicts, profiles)
    control = [j for j in joined if j.figure and j.figure.values_printed == "none"]
    control_rate = rate(control)

    def figure_group(key):
        return group(joined, lambda j: key(j.figure) if j.figure else None)

    by_type = figure_group(lambda f: f.named_type)
    by_printed = figure_group(lambda f: f.values_printed)
    by_density = figure_group(lambda f: density_band(f.marks))
    by_placement = figure_group(lambda f: f.placement)
    by_panels = figure_group(lambda f: "1 面板" if f.panels <= 1 else
                             ("2 面板" if f.panels == 2 else "3+ 面板"))
    by_predicted_step = group(joined, lambda j: f"step {j.profile.hardest_step}"
                              if j.profile.hardest_step else None)

    family_by_density: dict[str, Counter] = defaultdict(Counter)
    for j in joined:
        if j.passed or not j.figure:
            continue
        band = density_band(j.figure.marks)
        key = (j.verdict.rule.stem, j.verdict.rule.id)
        if band and key in diagnoses:
            family_by_density[band][diagnoses[key].family] += 1

    words = words or {}
    by_text_band = {}
    for band in (name for _, _, name in TEXT_BANDS):
        chosen = [v for v in run.verdicts if text_band(words.get(v.rule.stem)) == band]
        if chosen:
            by_text_band[band] = Rate(len(chosen), sum(1 for v in chosen if v.passed))

    seen = Counter(key for profile in profiles.values() for key in profile.components)
    documents: dict[str, set] = defaultdict(set)
    for profile in profiles.values():
        for key in profile.components:
            documents[key].add(profile.document)
    associations = []
    for key, page_count in seen.items():
        present = rate(control, lambda j, k=key: k in j.profile.components)
        absent = rate(control, lambda j, k=key: k not in j.profile.components)
        if present.total < MIN_POINTS:
            continue
        associations.append(Association(key, page_count, len(documents[key]),
                                        present, absent))
    associations.sort(key=lambda a: a.delta)

    failures_by_page: dict[str, Counter] = defaultdict(Counter)
    for verdict, diagnosis in results:
        failures_by_page[verdict.rule.stem][diagnosis.kind] += 1
    worst = sorted(((stem, score, len(run.by_page()[stem]), failures_by_page[stem])
                    for stem, score in scores.items()), key=lambda row: (row[1], -row[2]))

    addressing_ids = {key for key, diagnosis in diagnoses.items()
                      if diagnosis.family == "addressing"}
    fixed = {stem: sum(1 for v in vs if v.passed
                       or (v.rule.stem, v.rule.id) in addressing_ids) / len(vs)
             for stem, vs in run.by_page().items() if vs}

    #: Pages ranked by how much of their loss one form accounts for, so a form
    #: without a hand-read case can still be shown on pages rather than asserted.
    pages_by_kind: dict[str, list[str]] = {}
    for kind in {diagnosis.kind for _, diagnosis in results}:
        ranked = sorted(failures_by_page,
                        key=lambda stem, k=kind: (-failures_by_page[stem][k],
                                                  scores.get(stem, 1.0)))
        pages_by_kind[kind] = [stem for stem in ranked if failures_by_page[stem][kind]][:6]

    total = len(run.verdicts)
    return Analysis(
        run=run.name, model=run.model, pages=len(run.pages), points=total,
        page_mean=statistics.mean(scores.values()) if scores else 0.0,
        micro=sum(1 for v in run.verdicts if v.passed) / total if total else 0.0,
        perfect=sum(1 for s in scores.values() if s == 1.0),
        zero=sum(1 for s in scores.values() if s == 0.0),
        diagnoses=diagnoses, kinds=kinds, homes=homes, verdicts=verdicts,
        by_arity=by_arity, by_tag=by_tag, by_kind_arity=dict(by_kind_arity),
        errors=errors,
        analysed_pages=len(profiles), analysed_points=len(joined),
        control_points=control_rate.total, control_rate=control_rate.value,
        by_type=by_type, by_printed=by_printed, by_density=by_density,
        by_placement=by_placement, by_panels=by_panels,
        by_predicted_step=by_predicted_step, by_text_band=by_text_band,
        family_by_density=dict(family_by_density),
        components=associations, worst_pages=worst[:20], page_scores=scores,
        components_by_page={stem: profile.components
                            for stem, profile in profiles.items()},
        pages_by_kind=pages_by_kind,
        matcher_agreement=agreement,
        addressing_ceiling=statistics.mean(fixed.values()) if fixed else 0.0)


def summary_json(analysis: Analysis) -> dict:
    """The machine-readable form, for the before/after comparison in group D."""
    def rates(table: dict) -> dict:
        return {str(k): [v.total, round(v.value, 4)] for k, v in table.items()}

    return {
        "run": analysis.run, "model": analysis.model,
        "pages": analysis.pages, "points": analysis.points,
        "page_mean": round(analysis.page_mean, 4), "micro": round(analysis.micro, 4),
        "perfect_pages": analysis.perfect, "zero_pages": analysis.zero,
        "kinds": dict(analysis.kinds.most_common()),
        "label_homes": dict(analysis.homes.most_common()),
        "by_arity": rates(analysis.by_arity), "by_tag": rates(analysis.by_tag),
        "by_kind_and_arity": {str(k): dict(v) for k, v in analysis.by_kind_arity.items()},
        "reading_error_quantiles": _quantiles(analysis.errors),
        "analysed_pages": analysis.analysed_pages,
        "analysed_points": analysis.analysed_points,
        "control": {"points": analysis.control_points,
                    "rate": round(analysis.control_rate, 4)},
        "by_chart_type": rates(analysis.by_type),
        "by_values_printed": rates(analysis.by_printed),
        "by_density": rates(analysis.by_density),
        "by_heading_placement": rates(analysis.by_placement),
        "by_panels": rates(analysis.by_panels),
        "by_predicted_hardest_step": rates(analysis.by_predicted_step),
        "by_page_words": rates(analysis.by_text_band),
        "failure_family_by_density": {k: dict(v) for k, v
                                      in analysis.family_by_density.items()},
        "components": [a.to_json() for a in analysis.components],
        "matcher_agreement": round(analysis.matcher_agreement, 5),
        "addressing_ceiling": round(analysis.addressing_ceiling, 4),
    }


def _quantiles(errors: list[float]) -> dict:
    if not errors:
        return {}
    def at(q: float) -> float:
        return round(errors[min(len(errors) - 1, int(q * len(errors)))], 4)
    return {"n": len(errors), "p25": at(0.25), "p50": at(0.5), "p75": at(0.75),
            "p90": at(0.9),
            "within": {str(b): sum(1 for e in errors if e <= b)
                       for b in (0.02, 0.05, 0.1, 0.2, 0.5, 1.0)}}


def matcher_agreement(run: Run) -> float:
    """How often the local matcher and the official metric agree on "is the value
    in a table at all".

    The local matcher decides nothing about pass or fail, but every sub-form in
    section 1 rests on it, so its error rate is reported rather than assumed.
    """
    from taxonomy import _value_cells

    agree = 0
    for verdict in run.verdicts:
        official = verdict.passed or "labels not associated" in verdict.explanation
        mine = bool(_value_cells(verdict.rule, run.pages[verdict.rule.stem]))
        agree += official == mine
    return agree / len(run.verdicts) if run.verdicts else 0.0


def negative_value_rate(run: Run) -> float:
    """Pass rate on the points whose annotated value is negative."""
    chosen = [v for v in run.verdicts if v.rule.value.strip().startswith(("-", "−", "–"))]
    return sum(1 for v in chosen if v.passed) / len(chosen) if chosen else 0.0
