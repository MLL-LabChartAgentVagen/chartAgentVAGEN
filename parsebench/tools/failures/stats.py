"""Every number the failure section of the report is allowed to print.

Two denominators, kept visibly apart. *What failure looks like* -- the form counts,
where the unassociable label went, the pass rate by how many keys a point needs, by
how much body text the page carries -- runs over all 568 pages, because it needs
only the parser's output, the rule and the PDF text layer. *What makes a page hard
to draw* -- density, whether the figure prints its numbers -- runs over the twenty
pages three models described, because that is where those attributes exist at all.

A figure attribute is only used when at least two of the three models read it the
same way. One model's mark count is that model's estimate; two models landing in the
same band is a property of the figure.

Every association between a component and failure is measured inside a control
group -- points whose figure prints no number at all -- because whether the number
is printed moves the pass rate by about 19 points and would otherwise dominate every
row.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1])]

from failures.forms import ADDRESSING, Form                     # noqa: E402
from failures.run import Run, Verdict                           # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "parsebench/data/analysis"
PDF_DIR = ROOT / "parsebench/data/raw/docs/chart"

#: Mark-count bands. The top one is where `chart_types.md` cannot currently reach.
DENSITY_BANDS = ((0, 20, "≤20"), (20, 60, "21–60"), (60, 150, "61–150"),
                 (150, 400, "151–400"), (400, 10 ** 9, ">400"))

#: Body-text bands, cut at the quartiles of the split's own distribution.
TEXT_BANDS = ((0, 240, "≤240 词"), (240, 360, "241–360 词"),
              (360, 500, "361–500 词"), (500, 10 ** 9, ">500 词"))

#: A cell smaller than this is not printed at all. It is deliberately low: with
#: twenty described pages the page-attribute rows are thin, and a thin row with
#: its interval printed says more than a row silently dropped.
MIN_POINTS = 25


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

    def to_json(self) -> dict:
        low, high = self.interval
        return {"n": self.total, "passed": self.passed, "rate": round(self.value, 4),
                "ci": [round(low, 4), round(high, 4)]}


def separated(a: Rate, b: Rate) -> bool:
    """True when the two intervals do not overlap -- the only claims worth making."""
    return a.interval[1] < b.interval[0] or b.interval[1] < a.interval[0]


def band(value: int, bands: tuple) -> str | None:
    if value <= 0:
        return None
    for low, high, name in bands:
        if low < value <= high:
            return name
    return None


def page_words(pdf_dir: Path = PDF_DIR) -> dict[str, int]:
    """Words on each page, from the PDF text layer -- exact and free, unlike OCR."""
    out: dict[str, int] = {}
    for path in sorted(pdf_dir.glob("*.pdf")):
        proc = subprocess.run(["pdftotext", str(path), "-"], capture_output=True, text=True)
        out[path.stem] = len(proc.stdout.split())
    return out


# --------------------------------------------------------------------------- #
# What three models said about the sampled pages                                #
# --------------------------------------------------------------------------- #

@dataclass
class Consensus:
    """What at least two of three models said about one sampled page.

    `figure_of` maps a spot-check point to the figure carrying it by position: the
    prompt lists the page's values in rule order and the schema answers one entry per
    value in that order, so the index is the join and no name matching is needed.
    """

    stem: str
    components: set[str]
    #: rule index -> the density band two models agree on, or None.
    density: dict[int, str | None]
    #: rule index -> `all` / `some` / `none`, or None when no two agree.
    printed: dict[int, str | None]
    #: rule index -> panels count two models agree on, or None.
    panels: dict[int, int | None]


def _agreed(values: list) -> object | None:
    """The value at least two of three gave, or None when all three differ."""
    counts = Counter(v for v in values if v is not None)
    if not counts:
        return None
    value, n = counts.most_common(1)[0]
    return value if n >= 2 else None


def load_answers(models: list[str]) -> dict[str, dict[str, dict]]:
    """`stem -> model -> answer`, over the models' page runs."""
    out: dict[str, dict[str, dict]] = defaultdict(dict)
    for model in models:
        for path in sorted((ANALYSIS / model).glob("*.json")):
            if path.name in ("overview.json", "failures.json"):
                continue                       # the two answers that are not a page
            record = json.loads(path.read_text(encoding="utf-8"))
            out[record["stem"]][model] = record["answer"]
    return out


def consensus(answers: dict[str, dict[str, dict]]) -> dict[str, Consensus]:
    """One `Consensus` per page, over whatever models answered it."""
    out: dict[str, Consensus] = {}
    for stem, by_model in answers.items():
        components: Counter = Counter()
        for answer in by_model.values():
            components.update({c["key"] for c in answer.get("components") or ()})
        checks = max((len(a.get("spot_checks") or ()) for a in by_model.values()), default=0)
        density: dict[int, str | None] = {}
        printed: dict[int, str | None] = {}
        panels: dict[int, int | None] = {}
        for i in range(checks):
            figures = []
            for answer in by_model.values():
                spot = (answer.get("spot_checks") or [None] * (i + 1))[i] \
                    if i < len(answer.get("spot_checks") or ()) else None
                if not spot:
                    figures.append(None)
                    continue
                figure = next((f for f in answer.get("figures") or ()
                               if str(f.get("id")) == str(spot.get("figure_id"))), None)
                figures.append(figure)
            density[i] = _agreed([band(int(f.get("marks") or 0), DENSITY_BANDS)
                                  for f in figures if f])
            printed[i] = _agreed([str(f.get("values_printed") or "") for f in figures if f])
            panels[i] = _agreed([int(f.get("panels") or 1) for f in figures if f])
        out[stem] = Consensus(stem, {k for k, n in components.items() if n >= 2},
                              density, printed, panels)
    return out


# --------------------------------------------------------------------------- #
# The tables                                                                    #
# --------------------------------------------------------------------------- #

def form_table(forms: dict[str, Form], failures: int) -> list[dict]:
    """One row per failure form: how many, what share, and where the label went."""
    homes: dict[str, Counter] = defaultdict(Counter)
    for key, form in forms.items():
        homes[form.kind].update(form.homes.values())
    counts = Counter(form.kind for form in forms.values())
    rows = []
    for kind in sorted(counts, key=lambda k: -counts[k]):
        rows.append({"form": kind, "count": counts[kind],
                     "share": round(counts[kind] / failures, 4) if failures else 0.0,
                     "homes": dict(homes[kind].most_common())})
    return rows


def single_variable(run: Run, agreed: dict[str, Consensus],
                    words: dict[str, int]) -> list[dict]:
    """Pass rate by one variable at a time, each with the denominator it can have."""
    by_page = run.by_page()
    rows: list[dict] = []

    def emit(variable: str, scope: str, buckets: dict[object, list[Verdict]],
             order: list | None = None) -> None:
        names = order or sorted(buckets, key=str)
        for name in names:
            got = buckets.get(name) or []
            if len(got) < MIN_POINTS:
                continue
            rate = Rate(len(got), sum(v.passed for v in got))
            rows.append({"variable": variable, "scope": scope, "bucket": str(name),
                         **rate.to_json()})

    arity: dict[object, list[Verdict]] = defaultdict(list)
    text: dict[object, list[Verdict]] = defaultdict(list)
    for verdict in run.verdicts:
        arity[verdict.rule.arity].append(verdict)
        bucket = band(words.get(verdict.rule.stem, 0), TEXT_BANDS)
        if bucket:
            text[bucket].append(verdict)
    emit("定位需要几个键", "全部 568 页", arity, sorted(arity))
    emit("整页文字量", "全部 568 页", text, [name for _, _, name in TEXT_BANDS])

    density: dict[object, list[Verdict]] = defaultdict(list)
    printed: dict[object, list[Verdict]] = defaultdict(list)
    panels: dict[object, list[Verdict]] = defaultdict(list)
    for stem, agreement in agreed.items():
        for index, verdict in enumerate(by_page.get(stem, [])):
            if agreement.density.get(index):
                density[agreement.density[index]].append(verdict)
            if agreement.printed.get(index):
                printed[agreement.printed[index]].append(verdict)
            if agreement.panels.get(index):
                panels[f"{agreement.panels[index]} 面板"].append(verdict)
    scope = f"抽样 {len(agreed)} 页"
    emit("图元个数", f"{scope} · 三家里两家同档", density, [n for _, _, n in DENSITY_BANDS])
    emit("数值是否印在图上", f"{scope} · 三家里两家同值", printed, ["all", "some", "none"])
    emit("面板数", f"{scope} · 三家里两家同值", panels)
    return rows


def component_deltas(run: Run, agreed: dict[str, Consensus]) -> list[dict]:
    """Inside the control group, the pass rate with and without each component.

    The control group is the points whose figure prints no number at all. Only rows
    whose two intervals do not overlap are worth reading, and the number of documents
    behind a row matters more than the number of points: a component that is one
    publisher's habit will separate on that publisher's pages and mean nothing.
    """
    by_page = run.by_page()
    control: list[tuple[str, Verdict]] = []
    for stem, agreement in agreed.items():
        for index, verdict in enumerate(by_page.get(stem, [])):
            if agreement.printed.get(index) == "none":
                control.append((stem, verdict))
    keys = sorted({key for agreement in agreed.values() for key in agreement.components})
    rows = []
    for key in keys:
        present = [v for stem, v in control if key in agreed[stem].components]
        absent = [v for stem, v in control if key not in agreed[stem].components]
        if len(present) < MIN_POINTS or len(absent) < MIN_POINTS:
            continue
        with_it, without = (Rate(len(present), sum(v.passed for v in present)),
                            Rate(len(absent), sum(v.passed for v in absent)))
        rows.append({"key": key,
                     "pages": sum(1 for a in agreed.values() if key in a.components),
                     "with": with_it.to_json(), "without": without.to_json(),
                     "delta": round(with_it.value - without.value, 4),
                     "separated": separated(with_it, without)})
    return sorted(rows, key=lambda row: row["delta"])


def ceiling(run: Run, forms: dict[str, Form]) -> float:
    """The page-average score if every addressing failure were fixed and nothing else.

    Page-averaged, the same way the benchmark averages, so it is comparable with the
    run's own headline number rather than with a micro average.
    """
    fixed = {key for key, form in forms.items() if form.kind in ADDRESSING}
    totals = []
    for stem, verdicts in run.by_page().items():
        if not verdicts:
            continue
        passed = sum(v.passed or f"{v.rule.stem}/{v.rule.id}" in fixed for v in verdicts)
        totals.append(passed / len(verdicts))
    return sum(totals) / len(totals) if totals else 0.0


# --------------------------------------------------------------------------- #
# The whole reading of one run, as one file                                     #
# --------------------------------------------------------------------------- #

def build(run_dir: Path, models: list[str]) -> dict:
    """Every program-computed number about one run, in the shape the reports print."""
    from failures.forms import classify_all, roll_up
    from failures.run import load_rules, load_run, run_model

    rules = load_rules(ROOT / "parsebench/data/raw/chart.jsonl")
    run = load_run(run_dir, rules, run_model(run_dir))
    forms = classify_all(run.failures(), run.pages)
    agreed = consensus(load_answers(models))
    words = page_words()

    by_page = run.by_page()
    page_mean = sum(sum(v.passed for v in vs) / len(vs)
                    for vs in by_page.values() if vs) / len(by_page)
    return {
        "run": run_dir.parent.name,
        "parser_model": run.model,
        "pages": len(run.pages),
        "points": len(run.verdicts),
        "failures": len(run.failures()),
        "page_mean": round(page_mean, 4),
        "ceiling": round(ceiling(run, forms), 4),
        "counts": dict(roll_up(forms)),
        "forms": form_table(forms, len(run.failures())),
        "single_variable": single_variable(run, agreed, words),
        "component_deltas": component_deltas(run, agreed),
        "sampled_pages_covered": sum(1 for stem in agreed if stem in run.pages),
    }


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", type=Path,
                    default=ROOT / "parsebench/data/runs/ppdoclayoutv3_lean_qwen/chart")
    ap.add_argument("--models", nargs="+",
                    default=["claude-opus-5", "gpt-5.6-sol", "gemini-3.1-pro-preview"])
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    summary = build(args.run, args.models)
    out = args.out or ROOT / f"parsebench/data/stats/failures_{summary['run']}.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{summary['run']}: {summary['points']} points, {summary['failures']} failures, "
          f"page mean {summary['page_mean']:.2%}, addressing ceiling {summary['ceiling']:.2%}")
    for row in summary["forms"]:
        print(f"  {row['form']:<16} {row['count']:4d}  {row['share']:5.1%}")
    print(f"  {len(summary['single_variable'])} single-variable rows, "
          f"{len(summary['component_deltas'])} component rows")
    print(f"\nwritten to {out}")


if __name__ == "__main__":
    main()
