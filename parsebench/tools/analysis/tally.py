"""Every number the contract marks `program_measured`, computed from the raw answers.

The comparison is per page and per quantity, never per report: two reports that
agree on totals can disagree on every page and cancel out. So each quantity in
`format.SAMPLE_QUANTITIES` has a unit -- a (page, key), a (page, figure), a page --
and each unit falls into one of four classes: three models said the same thing, two
said it and the third was silent, one said it alone, or two or more said different
things.

Figures are aligned across models by reading order. Nothing else is available: the
schema has no figure identity beyond `f1, f2, ...` in reading order, and matching by
title would compare transcription rather than reading.

One quantity is not an agreement at all. The addressing keys were predicted with the
labels withheld, so `chart.jsonl` grades them, and the question there is who is
right rather than who agrees with whom. It is what calibrates the rest.

Usage:
    python parsebench/tools/analysis/tally.py --models claude-opus-5 gpt-5.6-sol ...
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "parsebench" / "tools")]

from analysis.rules import Rule, keys_agree, load_rules       # noqa: E402
from contract.vocabulary import BY_KEY                        # noqa: E402

ANALYSIS = ROOT / "parsebench/data/analysis"
SAMPLE = ROOT / "parsebench/data/stats/analysis_sample.json"
SUMMARY = ROOT / "parsebench/data/stats/analysis_summary.json"

#: Mark-count bands, the same cuts the failure analysis uses.
DENSITY_BANDS = ((0, 20, "≤20"), (20, 60, "21–60"), (60, 150, "61–150"),
                 (150, 400, "151–400"), (400, 10 ** 9, ">400"))

CLASSES = ("unanimous", "majority", "single", "conflict")


def density_band(marks: int) -> str:
    for low, high, name in DENSITY_BANDS:
        if low < marks <= high:
            return name
    return "未报"


# --------------------------------------------------------------------------- #
# Loading                                                                       #
# --------------------------------------------------------------------------- #

@dataclass
class Answers:
    """Every model's answer to every sampled page, plus the two control runs."""

    models: list[str]
    pages: list[dict]
    #: stem -> model -> the whole record, answer included.
    records: dict[str, dict[str, dict]] = field(default_factory=dict)
    controls: dict[str, dict[str, dict]] = field(default_factory=dict)

    def answer(self, stem: str, model: str) -> dict | None:
        record = self.records.get(stem, {}).get(model)
        return record["answer"] if record else None

    def answered(self, stem: str) -> list[str]:
        return [m for m in self.models if m in self.records.get(stem, {})]


#: The two answers in a model's directory that are not a page.
NOT_PAGES = ("overview.json", "failures.json")


def _page_files(directory: Path) -> list[Path]:
    return [p for p in sorted(directory.glob("*.json")) if p.name not in NOT_PAGES]


def load(models: list[str], controls: list[str]) -> Answers:
    pages = json.loads(SAMPLE.read_text())["pages"]
    out = Answers(models, pages)
    for model in models:
        for path in _page_files(ANALYSIS / model):
            record = json.loads(path.read_text(encoding="utf-8"))
            out.records.setdefault(record["stem"], {})[model] = record
    for name in controls:
        directory = ANALYSIS / name
        if not directory.exists():
            continue
        for path in _page_files(directory):
            record = json.loads(path.read_text(encoding="utf-8"))
            out.controls.setdefault(name, {})[record["stem"]] = record
    return out


# --------------------------------------------------------------------------- #
# One quantity at a time                                                        #
# --------------------------------------------------------------------------- #

@dataclass
class Item:
    """One comparable unit, and what each model said about it."""

    page: str
    unit: str
    values: dict[str, object]          # model -> its value, absent when silent

    @property
    def klass(self) -> str:
        """Relative to how many models were asked, not to a fixed three.

        Silence and a different answer are not the same thing: one is a model that
        did not report the unit, the other is a model that disagrees about it. So a
        differing value is a conflict even when a third model is silent.
        """
        said = [v for v in self.values.values() if v is not None]
        distinct = {json.dumps(v, ensure_ascii=False, sort_keys=True) for v in said}
        if len(distinct) > 1:
            return "conflict"
        if len(said) < 2:
            return "single"
        return "unanimous" if len(said) == len(self.values) else "majority"


def _figures(answer: dict) -> list[dict]:
    return [f for f in (answer.get("figures") or ()) if f.get("type") != "unreadable"]


def _figure_items(answers: Answers, name: str, read) -> list[Item]:
    """A quantity read off one figure, aligned across models by reading order."""
    items: list[Item] = []
    for page in answers.pages:
        stem = page["stem"]
        by_model = {m: _figures(answers.answer(stem, m) or {}) for m in answers.answered(stem)}
        for index in range(max((len(f) for f in by_model.values()), default=0)):
            values = {m: (read(figures[index]) if index < len(figures) else None)
                      for m, figures in by_model.items()}
            items.append(Item(stem, f"{name}#f{index + 1}", values))
    return items


def component_items(answers: Answers) -> list[Item]:
    """One item per (page, vocabulary key) any model reported."""
    items = []
    for page in answers.pages:
        stem = page["stem"]
        by_model = {m: {c["key"] for c in (answers.answer(stem, m) or {}).get("components") or ()}
                    for m in answers.answered(stem)}
        for key in sorted({k for keys in by_model.values() for k in keys}):
            items.append(Item(stem, key, {m: (key if key in keys else None)
                                          for m, keys in by_model.items()}))
    return items


def page_items(answers: Answers, name: str, read) -> list[Item]:
    items = []
    for page in answers.pages:
        stem = page["stem"]
        items.append(Item(stem, name, {m: read(answers.answer(stem, m) or {})
                                       for m in answers.answered(stem)}))
    return items


def quantities(answers: Answers) -> dict[str, list[Item]]:
    """The six per-page and per-figure quantities of `format.SAMPLE_QUANTITIES`."""
    return {
        "组件命中集合": component_items(answers),
        "图表类型判定": _figure_items(answers, "type", lambda f: (
            f"other · {str(f.get('type_other') or '').strip().lower()}"
            if f.get("type") == "other" else str(f.get("type")))),
        "数值印不印": _figure_items(answers, "printed", lambda f: str(f.get("values_printed"))),
        "稠密度档": _figure_items(answers, "density",
                                  lambda f: density_band(int(f.get("marks") or 0))),
        "标题": _figure_items(answers, "heading", lambda f: [
            bool(str((f.get("heading") or {}).get("figure_number") or "").strip()),
            str((f.get("heading") or {}).get("placement") or "")]),
        "卡在哪一步": page_items(answers, "hardest_step",
                                 lambda a: a.get("hardest_step") if a else None),
        "同向两条值轴": _figure_items(answers, "value_axes", lambda f: _value_axes(f)),
        "键分量": _figure_items(answers, "key_roles", lambda f: sorted(
            {str(part.get("role")) for part in (f.get("key_parts") or ())})),
    }


#: The two pairs of sides an axis can be drawn on. Two value axes matter only when
#: they are *parallel*: a scatter plot measures a quantity on both x and y and is not
#: ambiguous, while a left and a right value axis make one pixel height mean two
#: different numbers.
_PARALLEL = (("left", "right"), ("top", "bottom"))


def _value_axes(figure: dict) -> int:
    """How many value axes this figure draws on one pair of opposite sides.

    Two is the case the pipeline has no field for: a recorded value that does not say
    which of the two it was read against cannot be checked, and the pixel readback
    self-check has no definition on such a figure.
    """
    # Distinct *sides*, not axes. Small multiples draw one left axis per panel, and a
    # model that lists all fifteen of them is describing the same single-axis panel
    # fifteen times; counting axes would read that as the ambiguous case, which is
    # exactly backwards.
    sides = {str(axis.get("side")) for axis in (figure.get("axes") or ())
             if axis.get("role") == "value"}
    return max((len(sides & set(pair)) for pair in _PARALLEL), default=0)


def agreement(items: list[Item]) -> dict:
    """The four classes, and the rate averaged over pages the way the benchmark does."""
    counts = Counter(item.klass for item in items)
    per_page: dict[str, Counter] = defaultdict(Counter)
    for item in items:
        per_page[item.page][item.klass] += 1
    rates = [page["unanimous"] / sum(page.values()) for page in per_page.values()
             if sum(page.values())]
    return {**{name: counts[name] for name in CLASSES},
            "items": sum(counts.values()),
            "rate": round(sum(rates) / len(rates), 4) if rates else 0.0}


# --------------------------------------------------------------------------- #
# The one quantity the annotation can grade                                     #
# --------------------------------------------------------------------------- #

def key_predictions(answers: Answers, rules: dict[str, list[Rule]]) -> dict:
    """Every predicted key set, graded against the labels the rule actually uses."""
    per_model: dict[str, Counter] = defaultdict(Counter)
    per_point: list[dict] = []
    for page in answers.pages:
        stem = page["stem"]
        for index, rule in enumerate(rules.get(stem, ())):
            row = {"page": stem, "rule_id": rule.id, "value": rule.value,
                   "labels": list(rule.labels), "predictions": {}}
            for model in answers.answered(stem):
                checks = (answers.answer(stem, model) or {}).get("spot_checks") or []
                if index >= len(checks):
                    continue
                check = checks[index]
                predicted = [str(k) for k in (check.get("addressing_keys") or ())]
                placed = str(check.get("figure_id")) != "not_found"
                right = placed and keys_agree(predicted, rule.labels)
                missed = [label for i, label in enumerate(rule.labels)
                          if not keys_agree(predicted, (label,))]
                row["predictions"][model] = {"keys": predicted, "placed": placed,
                                             "correct": right, "missed": missed}
                per_model[model]["placed"] += placed
                per_model[model]["correct"] += right
                per_model[model]["points"] += 1
                for label in missed:
                    position = rule.labels.index(label)
                    per_model[model][f"missed_label_{position + 1}"] += 1
            per_point.append(row)
    return {"per_model": {m: dict(c) for m, c in per_model.items()},
            "missed_labels": _missed_labels(per_point),
            "points": per_point}


def _missed_labels(points: list[dict]) -> list[dict]:
    """Which rule label the models fail to predict, counted per label position.

    A rule addresses a value by two or three labels and the models get the first one
    -- the category on the axis -- almost always. What they leave out is the second,
    and what the second one *is* on these pages is the question P2 turns on.
    """
    rows: dict[tuple[int, str], Counter] = defaultdict(Counter)
    for point in points:
        for position, label in enumerate(point["labels"], start=1):
            for model, prediction in point["predictions"].items():
                rows[(position, label)][
                    "missed" if label in prediction["missed"] else "hit"] += 1
    out = []
    for (position, label), counts in rows.items():
        out.append({"position": position, "label": label, "hit": counts["hit"],
                    "missed": counts["missed"]})
    return sorted(out, key=lambda row: -row["missed"])


# --------------------------------------------------------------------------- #
# Counts, controls and cost                                                     #
# --------------------------------------------------------------------------- #

def component_counts(answers: Answers) -> list[dict]:
    """Per vocabulary key: each model's page count, the class, and the spread."""
    pages_by = {m: defaultdict(set) for m in answers.models}
    docs_by = {m: defaultdict(set) for m in answers.models}
    document = {p["stem"]: p["document"] for p in answers.pages}
    for page in answers.pages:
        stem = page["stem"]
        for model in answers.answered(stem):
            for component in (answers.answer(stem, model) or {}).get("components") or ():
                pages_by[model][component["key"]].add(stem)
                docs_by[model][component["key"]].add(document[stem])

    items = component_items(answers)
    classes: dict[str, Counter] = defaultdict(Counter)
    for item in items:
        classes[item.unit][item.klass] += 1

    rows = []
    for key in sorted({k for model in pages_by.values() for k in model}):
        component = BY_KEY.get(key)
        rows.append({
            "key": key,
            "name_zh": component.name_zh if component else "",
            "pages": {m: len(pages_by[m].get(key, ())) for m in answers.models},
            "documents": {m: len(docs_by[m].get(key, ())) for m in answers.models},
            "classes": dict(classes[key]),
            "affects": list(component.affects) if component else [],
            "ours": component.ours if component else None,
        })
    return sorted(rows, key=lambda row: -sum(row["pages"].values()))


def new_components(answers: Answers) -> list[dict]:
    """The vocabulary's residual: what the models named that it has no key for."""
    rows: list[dict] = []
    for page in answers.pages:
        stem = page["stem"]
        for model in answers.answered(stem):
            for item in (answers.answer(stem, model) or {}).get("new_components") or ():
                rows.append({"page": stem, "model": model, "name": item.get("name"),
                             "figure_id": item.get("figure_id"),
                             "evidence": item.get("evidence"),
                             "affects": item.get("affects") or []})
    return rows


#: Words that name the same construction in different vocabularies. The free run
#: says `bottom_legend` where the list says `legend_below_plot`, and a mapping that
#: misses that is measuring the mapper rather than the vocabulary.
SYNONYMS = {
    "bottom": "below", "top": "above", "under": "below", "over": "above",
    "right": "beside", "left": "beside", "side": "beside",
    "gridline": "grid", "gridlines": "grid", "grids": "grid",
    "tick": "ticks", "label": "labels", "bar": "bars", "panel": "panels",
    "title": "titles", "line": "lines", "mark": "marks", "value": "values",
    "angled": "rotated", "vertical": "rotated", "colour": "color",
    "coloured": "color", "colored": "color", "colors": "color",
    "categorical": "category", "categories": "category",
    "horizontal": "hgrid", "common": "shared", "chart": "", "plot": "",
    "axis": "axis", "y": "y", "x": "x",
}

#: A shared word this generic says nothing about which construction is meant.
STOPWORDS = {"", "the", "and", "with", "for", "chart", "plot", "figure", "page"}


def _stem(word: str) -> str:
    word = SYNONYMS.get(word, word)
    for suffix in ("ing", "ed", "es", "s"):
        if len(word) > 4 and word.endswith(suffix):
            return SYNONYMS.get(word[: -len(suffix)], word[: -len(suffix)])
    return word


def _stem_words(name: str) -> set[str]:
    words = str(name).lower().replace("-", "_").replace(" ", "_").split("_")
    return {_stem(w) for w in words if len(w) > 1} - STOPWORDS


def map_back(name: str) -> str | None:
    """Map a free component name onto a vocabulary key, by shared stem words.

    Deliberately generous, and it has to be: the control asks whether the free run
    *found the same constructions*, not whether it named them the same way, so
    `bottom_legend` has to reach `legend_below_plot`. Position and plural words are
    normalised before matching, and one shared word is enough when the two names are
    also lexically close. What survives unmapped is printed in full, because the
    residual is the finding and a mapper that swallowed it would hide the finding.
    """
    words = _stem_words(name)
    if not words:
        return None
    best, score = None, 0.0
    for key, component in BY_KEY.items():
        target = _stem_words(key) | _stem_words(component.name_en)
        shared = len(words & target)
        if not shared:
            continue
        closeness = SequenceMatcher(None, name.lower(), key.lower()).ratio()
        weight = shared + closeness
        if shared >= 2 or closeness >= 0.5:
            if weight > score:
                best, score = key, weight
    return best


def vocabulary_control(answers: Answers, model: str) -> dict:
    """The no-vocabulary run against the same model's vocabulary run, per page."""
    free = answers.controls.get(f"{model}__no_vocab", {})
    if not free:
        return {}
    rows, overlap, listed, mapped_total = [], 0, 0, 0
    for page in answers.pages:
        stem = page["stem"]
        with_list = {c["key"] for c in (answers.answer(stem, model) or {}).get("components") or ()}
        names = [str(c.get("key")) for c in (free.get(stem, {}).get("answer") or {}).get("components") or ()]
        mapped = {key for key in (map_back(n) for n in names) if key}
        rows.append({"page": stem, "with_vocabulary": len(with_list),
                     "free_names": len(names), "mapped_back": len(mapped),
                     "shared": len(with_list & mapped),
                     "unmapped": [n for n in names if map_back(n) is None]})
        overlap += len(with_list & mapped)
        listed += len(with_list)
        mapped_total += len(mapped)
    return {"model": model, "pages": rows,
            "keys_with_vocabulary": listed, "keys_mapped_back": mapped_total,
            "shared": overlap,
            "recall": round(overlap / listed, 4) if listed else 0.0,
            "precision": round(overlap / mapped_total, 4) if mapped_total else 0.0}


def repeat_control(answers: Answers, model: str) -> dict:
    """One model against itself: the noise floor a cross-model difference sits on."""
    again = answers.controls.get(f"{model}__repeat", {})
    if not again:
        return {}
    twin = Answers([model, f"{model}__repeat"], answers.pages)
    for page in answers.pages:
        stem = page["stem"]
        first = answers.records.get(stem, {}).get(model)
        second = again.get(stem)
        if first and second:
            twin.records[stem] = {model: first, f"{model}__repeat": second}
    return {"model": model,
            "quantities": {name: agreement(items)
                           for name, items in quantities(twin).items()}}


def call_cost(answers: Answers) -> list[dict]:
    """What each run cost: calls, tokens, seconds. Cached replies keep their usage."""
    rows = []
    runs = {m: answers.records for m in answers.models}
    for model in answers.models:
        records = [runs[model][stem][model] for stem in runs[model] if model in runs[model][stem]]
        rows.append(_cost_row(model, "", records))
    for name, by_stem in answers.controls.items():
        model, _, control = name.partition("__")
        rows.append(_cost_row(model, control, list(by_stem.values())))
    return rows


def _cost_row(model: str, control: str, records: list[dict]) -> dict:
    return {
        "model": model, "control": control, "calls": len(records),
        "effort": records[0]["effort"] if records else "",
        "dpi": records[0]["dpi"] if records else 0,
        "input_tokens": sum(r["usage"]["input_tokens"] for r in records),
        "output_tokens": sum(r["usage"]["output_tokens"] for r in records),
        "seconds": round(sum(r["seconds"] for r in records), 1),
        "re_asked": sum(bool(r.get("retried_on_empty")) for r in records),
        # A ceiling, not a target: raising it changes nothing for a reply that already
        # fit. Recorded as every distinct value the run used, because a page answered
        # under a different ceiling is a difference in conditions, and one nobody
        # could see if only the largest were printed.
        "max_tokens": sorted({r.get("max_tokens") or 0 for r in records} - {0}) or None,
        # Same reasoning as `max_tokens`: which route a call took is a condition of the
        # run, and one nobody could see if it were not written down. `direct` is the
        # vendor's own account; anything else is a gateway, same model and same request.
        "via": dict(Counter(r.get("via") or "direct" for r in records)),
    }


def mixes(answers: Answers) -> dict:
    """The descriptive mixes, one column per model -- never summed across models."""
    out: dict[str, dict[str, Counter]] = {k: defaultdict(Counter) for k in
                                          ("类型", "数值印不印", "稠密度档", "标题位置",
                                           "图号有无", "卡在哪一步")}
    for page in answers.pages:
        stem = page["stem"]
        for model in answers.answered(stem):
            answer = answers.answer(stem, model) or {}
            out["卡在哪一步"][model][str(answer.get("hardest_step"))] += 1
            for figure in _figures(answer):
                heading = figure.get("heading") or {}
                out["类型"][model][str(figure.get("type"))] += 1
                out["数值印不印"][model][str(figure.get("values_printed"))] += 1
                out["稠密度档"][model][density_band(int(figure.get("marks") or 0))] += 1
                out["标题位置"][model][str(heading.get("placement") or "none")] += 1
                out["图号有无"][model][
                    "有图号" if str(heading.get("figure_number") or "").strip() else "无图号"] += 1
    return {name: {model: dict(counts) for model, counts in by_model.items()}
            for name, by_model in out.items()}


# --------------------------------------------------------------------------- #
# What one figure takes to draw, and what one value takes to address             #
# --------------------------------------------------------------------------- #

def axis_facts(answers: Answers) -> dict:
    """Two value axes, and where the scale phrase is written.

    Counted per model and never summed across them: a figure two models call
    dual-axis and one calls single-axis is one figure, and the three columns say so.
    """
    per_model: dict[str, Counter] = defaultdict(Counter)
    dual: list[dict] = []
    for page in answers.pages:
        stem = page["stem"]
        said: dict[str, list[dict]] = {}
        for model in answers.answered(stem):
            figures = _figures(answers.answer(stem, model) or {})
            said[model] = figures
            for figure in figures:
                axes = figure.get("axes") or ()
                per_model[model]["图的张数"] += 1
                per_model[model]["左右（或上下）两条数值轴" if _value_axes(figure) >= 2
                                 else "只有一条数值轴"] += 1
                if sum(1 for a in axes if a.get("role") == "value") >= 2 \
                        and _value_axes(figure) < 2:
                    per_model[model]["两条互相垂直的数值轴（散点图）"] += 1
                if not axes:
                    per_model[model]["一条轴都没有"] += 1
                if any(str(axis.get("unit_text") or "").strip() for axis in axes):
                    per_model[model]["轴上写了单位"] += 1
        for index in range(max((len(f) for f in said.values()), default=0)):
            votes = {m: _value_axes(f[index]) for m, f in said.items() if index < len(f)}
            if sum(1 for n in votes.values() if n >= 2) >= 2:
                sides = {m: [f"{a.get('side')}:{a.get('serves')}"
                             for a in (said[m][index].get("axes") or ())
                             if a.get("role") == "value"]
                         for m in votes if votes[m] >= 2}
                dual.append({"page": stem, "figure": f"f{index + 1}",
                             "votes": votes, "axes": sides})
    return {"per_model": {m: dict(c) for m, c in per_model.items()}, "two_axis_figures": dual}


def key_part_facts(answers: Answers) -> dict:
    """How long the address of one value is, and which parts no key carries today."""
    roles: dict[str, Counter] = defaultdict(Counter)
    sources: dict[str, Counter] = defaultdict(Counter)
    length: dict[str, Counter] = defaultdict(Counter)
    worked: list[dict] = []
    for page in answers.pages:
        stem = page["stem"]
        for model in answers.answered(stem):
            for index, figure in enumerate(_figures(answers.answer(stem, model) or {})):
                parts = figure.get("key_parts") or ()
                length[model][str(len(parts))] += 1
                for part in parts:
                    roles[model][str(part.get("role"))] += 1
                    sources[model][str(part.get("label_source"))] += 1
                example = figure.get("worked_example") or {}
                if example.get("key"):
                    worked.append({"page": stem, "figure": f"f{index + 1}", "model": model,
                                   "key": list(example["key"]), "value": example.get("value"),
                                   "source": example.get("value_source"),
                                   "why_hard": example.get("why_hard", "")})
    return {"roles": {m: dict(c) for m, c in roles.items()},
            "label_sources": {m: dict(c) for m, c in sources.items()},
            "parts_per_figure": {m: dict(c) for m, c in length.items()},
            "worked_examples": worked}


def spot_check_facts(answers: Answers) -> dict:
    """The two per-value fields: is every addressing label printed, and what blocks it."""
    verbatim: dict[str, Counter] = defaultdict(Counter)
    blocked: dict[str, Counter] = defaultdict(Counter)
    not_verbatim: list[dict] = []
    for page in answers.pages:
        stem = page["stem"]
        for model in answers.answered(stem):
            for check in (answers.answer(stem, model) or {}).get("spot_checks") or ():
                if check.get("figure_id") == "not_found":
                    verbatim[model]["放不上图"] += 1
                    continue
                ok = bool(check.get("keys_verbatim"))
                verbatim[model]["逐字印在页上" if ok else "键不是原样印的"] += 1
                blocked[model][str(check.get("blocked_step"))] += 1
                if not ok:
                    not_verbatim.append({"page": stem, "model": model,
                                         "value": check.get("value"),
                                         "keys": list(check.get("addressing_keys") or ()),
                                         "mark": check.get("mark", "")})
    return {"keys_verbatim": {m: dict(c) for m, c in verbatim.items()},
            "blocked_step": {m: dict(c) for m, c in blocked.items()},
            "not_verbatim": not_verbatim}


def example_pool(answers: Answers) -> list[dict]:
    """Every quotable thing the models filed, with the change it was filed under.

    The report is built out of this list rather than out of prose: each entry names
    a page and a figure, so it can be shown beside the cut-out of that figure, and
    the quote is checkable against the image on its own.
    """
    pool = []
    for page in answers.pages:
        stem = page["stem"]
        for model in answers.answered(stem):
            for item in (answers.answer(stem, model) or {}).get("examples") or ():
                pool.append({"page": stem, "document": page["document"], "model": model,
                             "gap": str(item.get("gap")), "figure_id": str(item.get("figure_id")),
                             "quote": str(item.get("quote", "")).strip(),
                             "why": str(item.get("why", "")).strip()})
    return pool


def hardest_step_reasons(answers: Answers) -> list[dict]:
    """Each page's blocking step with the reason beside it, so a conflict can be settled."""
    rows = []
    for page in answers.pages:
        stem = page["stem"]
        rows.append({"page": stem, "said": {
            model: {"step": (answers.answer(stem, model) or {}).get("hardest_step"),
                    "why": (answers.answer(stem, model) or {}).get("hardest_step_why", "")}
            for model in answers.answered(stem)}})
    return rows


def build(models: list[str], vocab_control: str, repeat: str) -> dict:
    controls = [f"{vocab_control}__no_vocab", f"{repeat}__repeat"]
    answers = load(models, controls)
    rules = load_rules()
    items = quantities(answers)
    return {
        "models": models,
        "pages": [p["stem"] for p in answers.pages],
        "answered": {m: sum(1 for p in answers.pages if answers.answer(p["stem"], m))
                     for m in models},
        "agreement": {name: agreement(rows) for name, rows in items.items()},
        "disagreements": [
            {"page": item.page, "unit": item.unit, "class": item.klass,
             "values": {m: v for m, v in item.values.items()}}
            for rows in items.values() for item in rows if item.klass == "conflict"],
        "components": component_counts(answers),
        "new_components": new_components(answers),
        "axes": axis_facts(answers),
        "key_parts": key_part_facts(answers),
        "spot_check_facts": spot_check_facts(answers),
        "examples": example_pool(answers),
        "hardest_step_reasons": hardest_step_reasons(answers),
        "mixes": mixes(answers),
        "key_predictions": key_predictions(answers, rules),
        "vocabulary_control": vocabulary_control(answers, vocab_control),
        "repeat_control": repeat_control(answers, repeat),
        "cost": call_cost(answers),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--models", nargs="+",
                    default=["claude-opus-5", "gpt-5.6-sol", "gemini-3.1-pro-preview"])
    ap.add_argument("--vocabulary-control", default="gemini-3.1-pro-preview")
    ap.add_argument("--repeat-control", default="gemini-3.1-pro-preview")
    ap.add_argument("--out", type=Path, default=SUMMARY)
    args = ap.parse_args()

    summary = build(args.models, args.vocabulary_control, args.repeat_control)
    args.out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{len(summary['pages'])} pages, {len(summary['models'])} models")
    for model, answered in summary["answered"].items():
        scored = summary["key_predictions"]["per_model"].get(model, {})
        print(f"  {model:<24} {answered:2d} pages   "
              f"addressing keys {scored.get('correct', 0)}/{scored.get('points', 0)}")
    print("  agreement:")
    for name, stats in summary["agreement"].items():
        print(f"    {name:<12} {stats['rate']:.0%}  "
              f"unanimous={stats['unanimous']} majority={stats['majority']} "
              f"single={stats['single']} conflict={stats['conflict']}")
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
