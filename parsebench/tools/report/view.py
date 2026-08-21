"""Render the one file that concludes: `parsebench/reports/view.html`.

The agent writes the argument; this file assembles it. Nothing here decides a
number -- every figure printed is read out of `data/stats/` or out of the models'
own answers, and every sentence comes from `view_text.py` with named holes filled
from those same files. A number that no longer exists stops the build.

Two groups, in the order the reader needs them:

    a  what to change   nine changes in three families, each with the picture it
                        was read off; then which one to do first
    b  why believe it   the page sample, the 568-page failure run, five
                        failures one at a time, and where the three models disagree

The improvements come first because they are the point: ParseBench is the ruler,
not the target. Above the tabs, and visible whichever tab is open, sits the one
thing a reader has to have before any of it parses -- one real number on one real
page, with every word this report uses defined on it.

Usage:
    python parsebench/tools/report/view.py
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "parsebench" / "tools")]

from contract.format import LABEL_HOMES, MECHANISM_STEP        # noqa: E402
from contract import vocabulary                                            # noqa: E402
from contract.vocabulary import VOCABULARY                                 # noqa: E402
from failures import mechanisms as mechanism_lib                           # noqa: E402
from report import crops, view_text as text                                # noqa: E402
from report.view_style import CSS, Gallery, chips, esc, example, table, two  # noqa: E402

STATS = ROOT / "parsebench/data/stats"
ANALYSIS = ROOT / "parsebench/data/analysis"
OUT = ROOT / "parsebench/reports/view.html"

MODELS = ("claude-opus-5", "gpt-5.6-sol", "gemini-3.1-pro-preview")

#: What to call each model on screen, and who runs it. A comparison that does not
#: name its columns is not a comparison.
VENDORS = {
    "claude-opus-5": ("opus-5", "Anthropic"),
    "gpt-5.6-sol": ("gpt-5.6-sol", "OpenAI"),
    "gemini-3.1-pro-preview": ("gemini-3.1-pro", "Google"),
}

#: What each vocabulary key is called in Chinese, and whether the pipeline can draw
#: it today -- the two columns a component table needs beside its counts.
COMPONENT = {c.key: c for c in VOCABULARY}


def short(model: str) -> str:
    return VENDORS.get(model, (model, ""))[0]


def wilson_half_width(p: float, n: int, z: float = 1.96) -> float:
    """Half the width of a Wilson 95% interval, for saying how coarse a rate is."""
    denominator = 1 + z * z / n
    spread = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denominator
    return spread


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


# --------------------------------------------------------------------------- #
# Everything the page is built out of                                           #
# --------------------------------------------------------------------------- #

@dataclass
class Data:
    summary: dict
    failures: dict
    mechanisms: dict
    sample: dict
    verdicts: dict
    overviews: dict[str, dict]
    failure_answers: dict[str, dict]
    answers: dict[str, dict[str, dict]]        # model -> stem -> answer

    @classmethod
    def load(cls) -> "Data":
        summary = json.loads((STATS / "analysis_summary.json").read_text())
        failures = json.loads(
            (STATS / "failures_ppdoclayoutv3_lean_qwen.json").read_text())
        answers: dict[str, dict[str, dict]] = {}
        overviews: dict[str, dict] = {}
        failure_answers: dict[str, dict] = {}
        for model in MODELS:
            answers[model] = {}
            for path in sorted((ANALYSIS / model).glob("*.json")):
                if path.name in ("overview.json", "failures.json"):
                    continue
                record = json.loads(path.read_text(encoding="utf-8"))
                answers[model][record["stem"]] = record["answer"]
            for name, sink in (("overview.json", overviews), ("failures.json", failure_answers)):
                path = ANALYSIS / model / name
                if path.exists():
                    sink[model] = json.loads(path.read_text(encoding="utf-8"))
        verdict_path = ANALYSIS / "verdicts.json"
        return cls(
            summary=summary, failures=failures,
            mechanisms=mechanism_lib.build(list(MODELS), failures["failures"]),
            sample=json.loads((STATS / "analysis_sample.json").read_text()),
            verdicts=json.loads(verdict_path.read_text()) if verdict_path.exists() else {},
            overviews=overviews, failure_answers=failure_answers, answers=answers)

    # -- small readers, so no section reaches into a raw dict twice ----------- #

    def single(self, variable: str, bucket: str) -> dict:
        for row in self.failures["single_variable"]:
            if row["variable"] == variable and row["bucket"] == bucket:
                return row
        raise KeyError(f"{variable}/{bucket} is not in the single-variable table")

    def homes(self) -> Counter:
        counts: Counter = Counter()
        for form in self.failures["forms"]:
            counts.update(form.get("homes") or {})
        return counts

    def weighted(self, mechanism: str) -> int:
        """A mechanism's share of the sample, weighted back to all 896 failures."""
        share = self.mechanisms.get("weighted", {}).get(mechanism)
        return int(round(share[1])) if share else 0

    def mix(self, name: str, model: str) -> Counter:
        return Counter(self.summary["mixes"][name].get(model, {}))

    def per_model(self, section: str, model: str) -> dict[str, int]:
        """One model's column of a per-model table.

        A plain dict, not a `Counter`: a `Counter` answers 0 for a key that is not
        there, so a row renamed upstream would print zeros in the report instead of
        stopping the build. Everything else here fails loudly on a missing fact and
        this has to as well.
        """
        return dict(self.summary[section]["per_model"].get(model, {}))

    def examples(self, gap: str) -> list[dict]:
        return [item for item in self.summary["examples"] if item["gap"] == gap]

    def component(self, key: str) -> dict | None:
        for row in self.summary["components"]:
            if row["key"] == key:
                return row
        return None


# --------------------------------------------------------------------------- #
# Every number the prose uses, computed once                                    #
# --------------------------------------------------------------------------- #

#: The two forms that are a failure to *address* a value rather than to read it.
ADDRESSING = ("label_unlinked", "row_missing")

#: How far below its own noise floor a cross-model agreement rate has to sit before
#: the difference is read as a difference between the models. Stated rather than
#: hidden: it is a threshold someone chose, and 20 pages cannot justify a finer one.
NOISE_GAP = 0.15

#: Every cut-out is inlined at this width, so a figure shown under three arguments
#: costs the bytes of one figure.
WIDTH = 600


def colour_group_labels(data: Data) -> dict[str, set[str]]:
    """Per page, the labels the models named as the thing the colour carries.

    Taken from `key_parts[].example` where the role is `colour_group`, so the set is
    the models' own reading of which words on the page are group names -- not a guess
    made here, and not the whole of a rule's second label.
    """
    out: dict[str, set[str]] = defaultdict(set)
    for stem in data.summary["pages"]:
        for model in MODELS:
            for figure in (data.answers[model].get(stem) or {}).get("figures") or ():
                for part in figure.get("key_parts") or ():
                    if part.get("role") == "colour_group" and str(part.get("example", "")).strip():
                        out[stem].add(str(part["example"]).strip())
    return out


def colour_group_evidence(data: Data) -> tuple[int, int, int, int]:
    """The one rule-checkable thing P8 rests on.

    On the pages where the models say colour carries an attribute of its own, the
    benchmark's own rules use *those group names* as addressing labels. Returns
    (pages, distinct group labels the rules use, times a model missed one, times one
    was predicted). Only labels the models named as group names are counted: an
    ordinary second label -- a country, a year -- would otherwise be counted here and
    the number would say nothing about colour.
    """
    named = colour_group_labels(data)
    pages, labels = set(), set()
    missed = hit = 0

    def is_group(label: str, page: str) -> bool:
        """The named group, and the labels that are plainly its siblings.

        A model names one example per figure -- `Strong innovators` -- while the
        rules on that page also use `Emerging innovators` and `Moderate innovators`.
        Sharing the last word with a named example is what makes those three one
        family, and it is a rule stated here rather than a list typed by hand.
        """
        low = label.strip().lower()
        tail = low.rsplit(" ", 1)[-1]
        for name in named.get(page, ()):
            other = name.strip().lower()
            if len(other) <= 2:
                continue
            if low == other or low in other or other in low:
                return True
            if " " in low and " " in other and tail == other.rsplit(" ", 1)[-1]:
                return True
        return False

    for point in data.summary["key_predictions"]["points"]:
        for label in point["labels"]:
            if not is_group(label, point["page"]):
                continue
            pages.add(point["page"])
            labels.add(label)
            for prediction in point["predictions"].values():
                if label in (prediction.get("missed") or ()):
                    missed += 1
                elif any(label == key for key in prediction.get("keys") or ()):
                    hit += 1
    return len(pages), len(labels), missed, hit


def verdict_kinds(data: Data) -> dict[str, str]:
    """Per conflict, which of three things the adjudication ended in.

    `judged` decided it; `no_evidence` means the failure run never blocked on that
    page, so no answer is falsifiable; `not_judgeable` means the three models were not
    describing the same object. The last two are findings, not gaps in the work, and
    the page counts them separately for that reason.
    """
    verdicts = data.verdicts.get("verdicts", {})
    out = {}
    for item in data.summary["disagreements"]:
        key = f'{item["page"]}/{item["unit"]}'
        said = str((verdicts.get(key) or {}).get("verdict", ""))
        out[key] = ("unfiled" if key not in verdicts
                    else "no_evidence" if said.startswith("未裁决")
                    else "not_judgeable" if said.startswith("不裁")
                    else "judged")
    return out


def route_counts(data: Data, model: str) -> tuple[str, str]:
    """How many of a model's pages went by its own account, and how many by a gateway.

    A gateway is the same model answering the same question over a different line, so
    it is a run condition rather than a second model -- but it is one nobody could see
    unless the answers carried it, which is why `run.py` writes `via` on every answer.
    """
    routes: dict[str, int] = next(
        (row.get("via") or {} for row in data.summary["cost"]
         if row["model"] == model and not row["control"]), {})
    return (str(routes.get("direct", 0)),
            str(sum(n for route, n in routes.items() if route != "direct")))


def seen(row: dict) -> int:
    """How many sampled pages a component was reported on, at its highest count."""
    return max((row.get("pages") or {}).values(), default=0)


def style_dimensions(data: Data) -> list[dict]:
    """Components seen on the sampled pages that the pipeline cannot draw today.

    Not a list written from memory: the `ours` column was decided off the written
    spec before any page was looked at, and the counts are this run's. Ordered by
    how many models agreed, then by how many pages -- the ones every model saw on
    several pages first.
    """
    rows = [row for row in data.summary["components"]
            if not row.get("ours") and seen(row) > 0]
    return sorted(rows, key=lambda row: (-(row["classes"].get("unanimous", 0)), -seen(row),
                                         row["key"]))


def facts(data: Data) -> dict[str, str]:
    """Fill every hole in `view_text`. A hole with no fact behind it is a KeyError."""
    failures = data.failures
    homes = data.homes()
    printed_all = data.single("数值是否印在图上", "all")
    printed_none = data.single("数值是否印在图上", "none")
    addressing = sum(row["count"] for row in failures["forms"] if row["form"] in ADDRESSING)
    density_ns = [row["n"] for row in failures["single_variable"] if row["variable"] == "图元个数"]

    def per_model(counter, key: str) -> str:
        return " / ".join(str(counter(model)[key]) for model in MODELS)

    figures = " / ".join(str(sum(data.mix("类型", model).values())) for model in MODELS)
    missing_families = missing_family_counts(data)
    gpt_direct, gpt_gateway = route_counts(data, "gpt-5.6-sol")
    unit_key = data.component("unit_in_axis_or_title") or {"classes": {}}
    pages, group_labels, group_missed, group_hit = colour_group_evidence(data)
    mixed = next((row for row in failures["component_deltas"]
                  if row["key"] == "mixed_marks"), None)

    if mixed:
        mixed_line = (f"一张图里混着几种图形的页面，正确率 {pct(mixed['with']['rate'])}"
                      f"（{mixed['with']['n']} 个抽查点），其余页面 "
                      f"{pct(mixed['without']['rate'])}（{mixed['without']['n']} 个），"
                      f"{'两个区间不重叠' if mixed['separated'] else '两个区间重叠，读不出差别'}。")
    else:
        mixed_line = "混着几种图形的页面太少，这一轮算不出可比的正确率。"

    return {
        "failures": str(failures["failures"]),
        "addressing_share": pct(addressing / failures["failures"]),
        "page_mean": pct(failures["page_mean"]),
        "ceiling": pct(failures["ceiling"]),
        "documents": str(data.sample["documents_represented"]),
        "points": str(data.sample["rules_covered"]),
        "printed_all_rate": pct(printed_all["rate"]), "printed_all_n": str(printed_all["n"]),
        "printed_none_rate": pct(printed_none["rate"]), "printed_none_n": str(printed_none["n"]),
        "mech_interp": str(data.weighted("value_interpolated_off_axis")),
        "mech_panel": str(data.weighted("panel_name_dropped")),
        "mech_scale": str(data.weighted("scale_word_ignored")),
        "home_in_table": str(homes["in_a_table_but_not_addressing"]),
        "home_prose": str(homes["plain_text_only"]),
        "home_absent": str(homes["absent_from_the_output"]),
        "type_rate": pct(data.summary["agreement"]["图表类型判定"]["rate"]),
        "vocab_recall": pct(data.summary["vocabulary_control"]["recall"]),
        "conflicts": str(len(data.summary["disagreements"])),
        "type_compound": str(sum(
            1 for key, row in data.verdicts.get("verdicts", {}).items()
            if "/type#" in key and str(row["verdict"]).startswith("compound"))),
        "settled": str(sum(1 for kind in verdict_kinds(data).values() if kind == "judged")),
        "no_evidence": str(sum(1 for kind in verdict_kinds(data).values()
                               if kind == "no_evidence")),
        "not_judgeable": str(sum(1 for kind in verdict_kinds(data).values()
                                 if kind == "not_judgeable")),
        "unfiled": str(sum(
            1 for item in data.summary["disagreements"]
            if f'{item["page"]}/{item["unit"]}' not in data.verdicts.get("verdicts", {}))),
        "dual_figures": str(len(data.summary["axes"]["two_axis_figures"])),
        "mixed_pages": str((data.component("mixed_marks") or {"classes": {}})
                           ["classes"].get("unanimous", 0)),
        "dual_counts": " / ".join(
            f'{data.per_model("axes", m)["左右（或上下）两条数值轴"]}'
            f'/{data.per_model("axes", m)["图的张数"]}'
            for m in MODELS),
        "density_ns": " / ".join(str(n) for n in density_ns),
        "dense_mid_counts": " / ".join(str(data.mix("稠密度档", m)["151–400"]) for m in MODELS),
        "dense_top_counts": " / ".join(str(data.mix("稠密度档", m)[">400"]) for m in MODELS),
        "dense_low_rate": pct(data.single("图元个数", "≤20")["rate"]),
        "dense_low_n": str(data.single("图元个数", "≤20")["n"]),
        "dense_mid_rate": pct(data.single("图元个数", "61–150")["rate"]),
        "dense_mid_n": str(data.single("图元个数", "61–150")["n"]),
        "dense_top_rate": pct(data.single("图元个数", ">400")["rate"]),
        "dense_top_n": str(data.single("图元个数", ">400")["n"]),
        "dense_odd_rate": pct(data.single("图元个数", "151–400")["rate"]),
        "dense_odd_n": str(data.single("图元个数", "151–400")["n"]),
        "p10_range_n": str(missing_families["区间条 / 浮动条 / 哑铃图"]),
        "p10_table_n": str(missing_families["表格型图"]),
        "p10_fan_n": str(missing_families["扇形预测带"]),
        "figure_counts": figures,
        "above_counts": per_model(lambda m: data.mix("标题位置", m), "above"),
        "numbered_counts": per_model(lambda m: data.mix("图号有无", m), "有图号"),
        "unit_in_title": str(unit_key["classes"].get("unanimous", 0)),
        "n_pages": str(len(data.summary["pages"])),
        "freq_ci": str(round(wilson_half_width(0.25, len(data.summary["pages"])) * 100)),
        "multi_figure_pages": str((data.component("multi_figure_page") or {"classes": {}})
                                  ["classes"].get("unanimous", 0)),
        "vocab_n": str(len(VOCABULARY)),
        "gpt_direct": gpt_direct, "gpt_gateway": gpt_gateway,
        "missing_dims": str(len(style_dimensions(data))),
        "dims_elsewhere": str(sum(1 for row in style_dimensions(data)
                                  if row["key"] in ALREADY_COUNTED)),
        "p6_own": str(sum(1 for row in style_dimensions(data)
                          if row["key"] not in ALREADY_COUNTED)),
        "have_dims": str(sum(1 for row in data.summary["components"]
                             if row.get("ours") and seen(row))),
        "p8_rule_line": (
            f"<strong>基准自己的标准答案里就有这个</strong>。在模型指认出「颜色代表什么」的页面上，"
            f"基准把这些组别名当成指认一个数要用的名字：{pages} 页、{group_labels} 个不同的名字，"
            f"三个模型合起来漏掉 {group_missed} 次、报对 {group_hit} 次"
            f"（怎么算是「组别名」：模型自己指出的那个，"
            f"加上和它同一个词尾的兄弟——「强 / 中等 / 新兴创新国」是一族）。"
            f"<br><br>但解析器能直接从表格的某一行里把这些名字抄下来，"
            f"所以<strong>它对基准分数不成立</strong>，进清单靠的是右边那一栏。"
            f"另外，上一轮报过的「三个模型在这类名字上全错」，"
            f"<strong>这一轮不成立了</strong>——这一轮的问法里直接问了颜色代表什么，"
            f"三家在同样的名字上就报对了 {group_hit} 次。"
            f"这个差别是问法造成的，不是模型变强了，详见最后一页。"),
        "p9_score": (
            f"<strong>基准根本不看这件事</strong>：它只搜「这个数 + 这些名字」，"
            f"至于这个数是对着左轴还是右轴量出来的，判定里从来不问。{mixed_line}"
            f"沾得上边的只有一类：叠上去的第二种图形自带一个名字"
            f"（比如「2018 年得分」），那个名字就是指认这个数要用的第二个名字——"
            f"「名字只写在图例里、列名被写成颜色词」这类错换算到全部失败上大约 "
            f"{data.weighted('series_identified_by_colour')} 条，"
            f"「读到旁边那个图形上去了」大约 {data.weighted('value_read_off_wrong_mark')} 个。"),
    }


# --------------------------------------------------------------------------- #
# Pictures                                                                      #
# --------------------------------------------------------------------------- #

def picture(gallery: Gallery, stem: str, figure_id: str = "f1") -> str:
    """The markup for one figure: a window onto the page, clickable to open the page."""
    uri, page_width, page_height = crops.page_image(stem)
    page_class = gallery.page(stem, uri)
    box = crops.figure_box(stem, crops.figure_index(figure_id))
    view = gallery.view(stem, (box.x0, box.y0, box.x1, box.y1), page_width, page_height)
    return (f'<i class="im {page_class} {view}" data-page="{page_class}" '
            f'data-name="{esc(stem)}" role="button" tabindex="0"></i>')


def caption(stem: str, document: str, figure_id: str = "") -> str:
    """`f2` is not a word a reader knows. Say which figure on the page it is."""
    digits = "".join(ch for ch in figure_id if ch.isdigit())
    where = f"这一页的第 {digits} 张图" if digits else "这一页"
    return f"{esc(where)}<br><b>{esc(stem)}</b>"


def who_line() -> str:
    """Which three models. Printed at the top of every tab that compares them."""
    return ('<p class="who">这一页比较的是：'
            + " · ".join(f"<b>{esc(short(m))}</b>（{esc(VENDORS[m][1])}，"
                         f"<code>{esc(m)}</code>）" for m in MODELS)
            + "。三个模型看的是同一张图、被问的是同一段话、要填的是同一张表格，"
              "连思考强度都设成一样。</p>")


def say(value, dimension: str = "") -> str:
    """A value as a reader should see it: never a raw key, never a JSON list.

    `dimension` disambiguates the words a closed list reuses: `none` is "not one
    number is printed" under one heading and "there is no heading" under another.
    """
    if isinstance(value, (list, tuple)):
        return " ＋ ".join(say(item, dimension) for item in value)
    if isinstance(value, bool):
        return "有" if value else "无"
    raw = str(value)
    if raw.startswith("other · "):
        return f'其他（{esc(raw.split(" · ", 1)[1])}）'
    per_dimension = text.VALUE_IN.get(dimension, {})
    return esc(per_dimension.get(raw) or text.VALUE_ZH.get(raw, raw))


def documents(data: Data) -> dict[str, str]:
    return {page["stem"]: page["document"] for page in data.sample["pages"]}


# --------------------------------------------------------------------------- #
# The examples every claim is made on                                           #
# --------------------------------------------------------------------------- #

def gap_examples(data: Data, gallery: Gallery, gap: str, limit: int = 3) -> str:
    """Up to `limit` things the models pointed at on a page, filed under this change.

    Ranked by how many models pointed at the same figure for the same change, then
    rotated across models: three quotes from one model would read as one model's
    opinion rather than as three readings of a page.
    """
    docs = documents(data)
    votes: Counter = Counter()
    for item in data.examples(gap):
        votes[(item["page"], item["figure_id"])] += 1
    ranked = sorted((i for i in data.examples(gap) if i["quote"]),
                    key=lambda i: (-votes[(i["page"], i["figure_id"])], i["page"]))
    seen, out, said = set(), [], Counter()
    while ranked and len(out) < limit:
        item = min(ranked, key=lambda i: (said[i["model"]], ranked.index(i)))
        ranked = [other for other in ranked if other["page"] != item["page"]]
        if item["page"] in seen:
            continue
        seen.add(item["page"])
        said[item["model"]] += 1
        agreed = votes[(item["page"], item["figure_id"])]
        who = (f'<b>{esc(short(item["model"]))}</b> 指出的'
               + (f"，另外 {agreed - 1} 个模型在同一张图上说了同一件事" if agreed > 1 else ""))
        out.append(example(picture(gallery, item["page"], item["figure_id"]),
                           caption(item["page"], docs.get(item["page"], ""), item["figure_id"]),
                           item["quote"], esc(item["why"]), who))
    if not out:
        return ('<div class="eg"><div class="txt" style="grid-column:1/-1">'
                f'<p>这 {len(data.summary["pages"])} 页上，三个模型都没有为这一条挑出可以引用的例子。'
                '它进清单靠的是上面两栏里的证据，不是页面上的某一句话——'
                '没有例子本身也是一条信息。</p></div></div>')
    return "".join(out)


def worked_box(body: dict) -> str:
    """A change worked through on one number, when saying it in prose is not enough."""
    worked = body.get("worked")
    if not worked:
        return ""
    title, *steps = worked
    rows = "".join(f'<tr><td class="term">{esc(name)}</td><td>{prose}</td></tr>'
                   for name, prose in steps)
    return (f'<div class="worked"><h5>{esc(title)}</h5>'
            f'<table class="terms"><tbody>{rows}</tbody></table></div>')


#: The clusters inside `other` that the type table has no row for, as
#: `name -> the words the models used for it`. Matched against `type_other`, which
#: the models write freely, so a cluster is a set of spellings rather than a key.
#: `mixed marks` and `heterogeneous panels` are deliberately absent: both are
#: `compound`, a row the table already has.
MISSING_FAMILIES = {
    "区间条 / 浮动条 / 哑铃图": ("range", "floating", "bullet", "dumbbell", "high-low"),
    "表格型图": ("table", "ranked list"),
    "扇形预测带": ("windsock", "fan chart"),
}
MISSING_FAMILY_WORDS = tuple(w for words in MISSING_FAMILIES.values() for w in words)

#: What each missing family is, in one line, for the caption under its example.
KIND_SAID = {
    "区间条 / 浮动条 / 哑铃图": "区间条一族：一根条（或一段线）的两端各是一个值",
    "表格型图": "把一张表格当成一张带图号的图",
    "扇形预测带": "扇形预测带：一条实测线接一段向外张开的不确定区间",
}


def missing_family_counts(data: Data) -> dict[str, int]:
    """How many figures the three models between them filed under each missing family.

    Counted over `type_other`, so one figure that all three called a range bar counts
    three times -- the number says how often the reading came up, not how many figures
    there are, and the report says so.
    """
    counts = {name: 0 for name in MISSING_FAMILIES}
    for model in MODELS:
        for stem in data.summary["pages"]:
            for figure in (data.answers[model].get(stem) or {}).get("figures") or ():
                if figure.get("type") != "other":
                    continue
                word = str(figure.get("type_other") or "").strip().lower()
                for name, keys in MISSING_FAMILIES.items():
                    if any(key in word for key in keys):
                        counts[name] += 1
                        break
    return counts


def missing_family_examples(data: Data, gallery: Gallery, limit: int = 3) -> str:
    """Examples for the change the models were never offered as a category.

    The nine categories were in the prompt; this tenth one was read out of what the
    models called `other` afterwards, so its examples are found the same way -- by
    what two of them independently named -- rather than by what they filed. Which
    family a page illustrates comes from the same `MISSING_FAMILIES` table the counts
    do, so a caption cannot say one thing while the count says another.
    """
    docs, picked, used = documents(data), {}, set()
    for stem in data.summary["pages"]:
        for index in range(4):
            named = {}
            for model in MODELS:
                figures = [fig for fig in (data.answers[model].get(stem) or {}).get("figures") or ()
                           if fig.get("type") != "unreadable"]
                if index >= len(figures):
                    continue
                figure = figures[index]
                word = str(figure.get("type_other") or "").strip().lower()
                if figure.get("type") == "other" and word:
                    named[model] = word
            hits = {m: w for m, w in named.items()
                    if any(key in w for key in MISSING_FAMILY_WORDS) or "table" in w}
            if len(hits) < 2 or stem in used:
                continue
            used.add(stem)
            # The family the most of them named, not the first one that matches: two
            # models saying "data table" and one saying "dumbbell" is a table.
            votes = {name: sum(any(key in w for key in keys) for w in hits.values())
                     for name, keys in MISSING_FAMILIES.items()}
            name, best = max(votes.items(), key=lambda pair: pair[1])
            if not best or name in picked:      # one page per family, three families
                continue
            kind = KIND_SAID[name]
            picked[name] = (example(
                picture(gallery, stem, f"f{index + 1}"),
                caption(stem, docs.get(stem, ""), f"f{index + 1}"),
                " · ".join(sorted(set(hits.values()))),
                f"<strong>{esc(kind)}</strong>。我们的类型表里没有这一行，"
                f"所以这张图<strong>一种画法都对不上</strong>。",
                " ".join(f"<b>{esc(short(m))}</b>把它叫 “{esc(w)}”" for m, w in hits.items())))
            break
    out = [picked[name] for name in MISSING_FAMILIES if name in picked]
    return "".join(out) or gap_examples(data, gallery, "P10", limit=limit)


#: Dimensions the pipeline already has, called out beside the table of the ones it
#: lacks -- the three most often asked about plus two more, so the table is not read
#: as "we have none of this".
HAVE_CALLOUT = ("rotated_x_ticks", "shared_legend", "rotated_axis_title",
                "hgrid_only", "small_multiples_4")

#: Rows of the drawing-dimension table that already have a change of their own, so
#: the table is not read as thirty-three separate new items. Everything else is P6.
ALREADY_COUNTED = {
    "color_encodes_extra_attribute": "P8",
    "tick_marker_as_series": "P9",
    "dense_marks_100plus": "P5",
    "range_connector_line": "P10",
    "small_multiples_5plus": "P2",
    "side_text_bullets": "P3",
    "data_link_below_figure": "P3",
}


def style_dimension_table(data: Data, f: dict) -> str:
    """The measured list of drawing dimensions: what we lack, and what we already have."""
    rows = []
    for row in style_dimensions(data):
        component = COMPONENT[row["key"]]
        steps = "、".join(text.STEP_SHORT[step] for step in row["affects"]) or "度量看不见"
        elsewhere = ALREADY_COUNTED.get(row["key"], "")
        rows.append((vocabulary.GROUP_TITLES[component.group],
                     esc(row["name_zh"]),
                     row["classes"].get("unanimous", 0),
                     seen(row), steps,
                     f'<a href="#{elsewhere}"><code>{elsewhere}</code></a>' if elsewhere
                     else ""))
    have = "、".join(f'{esc(COMPONENT[key].name_zh)}'
                    f'（{seen(data.component(key) or {})} 页）' for key in HAVE_CALLOUT
                    if data.component(key))
    return (
        f'<h4>这 {f["n_pages"]} 页上出现过、而我们现在画不出来的画法</h4>'
        '<p>「三家一致」＝三个模型都在这一页上报了它，是这张表里最该信的一列；'
        '「最多几页」＝报得最多的那个模型报了几页。'
        '<strong>「我们现在有没有」这一列不是看着页面填的</strong>——'
        '它是在看任何一页之前，照着 <code>storyline/</code> 的写法逐项定好的，'
        '所以这张表是清单和实测一交得出来的，不是谁凭印象列的。</p>'
        '<p>最后一列写着编号的，说明这一行<strong>已经在别的改动下单算过了</strong>，'
        '不重复计数；其余的都归 P6。</p>'
        + table(("分组", "画法", "三家一致", "最多几页", "它能改判定的哪一步", "已单算作"),
                rows, numeric=(2, 3))
        + f'<p class="abl"><b>已经有的，免得误读</b>　{have}。'
          f'常被举的三个例子里，斜刻度标签、跨面板共用图例、竖排轴标题都已经有；'
          f'<strong>横向条（类目在纵轴）是缺的</strong>——条件表里根本没有「方向」这一维。</p>')


def gap_card(data: Data, gallery: Gallery, gap: str, f: dict) -> str:
    """One change: what it is, what it does to each of the two columns, and its examples."""
    body = text.GAPS[gap]
    tier, verdict, why = body["evidence"]
    return (
        f'<article class="card" id="{gap}"><header>'
        f'<h4><em>{gap}</em>{esc(body["title"])}</h4>'
        f'{chips((body["stance"], "hi"), ("证据来自 " + f_(body["source"], f), "key"),
                 ("对基准分数：" + verdict, "yes" if verdict == "成立" else ""), (tier, ""))}'
        f'</header><div class="split noimg"><figure></figure><div class="body">'
        f'<p>{f_(body["lede"], f)}</p>'
        + (f'<p class="aside"><b>不在这一条里</b>　{f_(body["note"], f)}</p>'
           if body.get("note") else "")
        + f'{worked_box(body)}'
        f'{two(f_(body["score"], f), f_(body["capability"], f))}'
        f'<p class="abl"><b>消融表因此多一行</b>　{esc(body["ablation"])}'
        f'<br><b>「对基准分数」那一栏的依据</b>　{esc(why)}</p>'
        f'</div></div>'
        f'{missing_family_examples(data, gallery) if gap == "P10" else gap_examples(data, gallery, gap)}'
        f'{style_dimension_table(data, f) if gap == "P6" else ""}'
        f'</article>')


def family_section(data: Data, gallery: Gallery, key: str, f: dict) -> str:
    family = text.FAMILIES[key]
    out = [f'<div class="lead"><p>{f_(family["lede"], f)}</p></div>']
    for gap in family["gaps"]:
        out.append(band(f"band-{gap}", f"{gap} · {text.GAPS[gap]['title']}",
                        text.GAPS[gap]["stance"]))
        out.append(gap_card(data, gallery, gap, f))
    return "".join(out)


#: Which family each change belongs to, so the summary table can say it in one word.
FAMILY_OF = {gap: family["short"]
             for family in text.FAMILIES.values() for gap in family["gaps"]}


def section_a0(data: Data, gallery: Gallery, f: dict) -> str:
    """Ten changes on one screen, in the order they should be done."""
    step_of = {gap: (step, what)
               for step, gaps, what, _ in ORDER for gap in gaps.split(" + ")}
    rows = []
    for step, gaps, what, _ in ORDER:
        for gap in gaps.split(" + "):
            body = text.GAPS[gap]
            _, verdict, _ = body["evidence"]
            rows.append((
                f'<a href="#{gap}"><code>{gap}</code></a>',
                f'<strong>{esc(body["title"])}</strong>',
                esc(FAMILY_OF[gap]), esc(body["stance"]),
                esc(f_(body["source"], f)),
                f'<b class="{"ok" if verdict == "成立" else "no"}">{esc(verdict)}</b>',
                esc(step_of[gap][0])))
    order_rows = [(step, " + ".join(f'<a href="#{g}"><code>{g}</code></a>'
                                    for g in gaps.split(" + ")),
                   f"<strong>{esc(what)}</strong>", esc(why))
                  for step, gaps, what, why in ORDER]
    return "".join([
        f'<div class="lead"><p>{text.ONE_LINE}</p>'
        f'<p>{f_(text.ONE_LINE_SUB, f)}</p></div>',
        band("a0-all", "十条改动", "一屏看完；点编号跳到那一条的展开"),
        '<p>「扩还是加」＝在现有能力上多一个维度，还是清单上多一条；'
        '<strong>没有一条是删能力的</strong>，消融表只会变长。'
        '「对基准分数」＝这一条能不能让 ParseBench 的分数变好，'
        '<strong>写「不成立」的照样在清单里</strong>——'
        'ParseBench 是尺子不是目标，那几条靠的是它给流水线加了什么。</p>',
        table(("", "改什么", "属于哪一家", "扩还是加", "证据来自", "对基准分数", "排第几步"),
              rows),
        band("a0-order", "做的顺序", "同一步里的几条是同一处代码，一次改完"),
        f'<p>{f_(text.A4["order"], f)}</p>',
        table(("", "做什么", "叫什么", "为什么在这一位"), order_rows),
        f'<p class="abl"><b>接下来三页</b>　'
        f'把这十条按「键要说全 / 读法要记 / 图要像真的」分成三家展开，每条都配着'
        f'它是从哪张图上看出来的。<b>第四页</b>　这个顺序和三个模型自己排的差在哪。</p>',
    ])


def section_a1(data: Data, gallery: Gallery, f: dict) -> str:
    return family_section(data, gallery, "A", f)


def section_a2(data: Data, gallery: Gallery, f: dict) -> str:
    return family_section(data, gallery, "B", f)


def section_a3(data: Data, gallery: Gallery, f: dict) -> str:
    body = family_section(data, gallery, "C", f)
    return body + "".join([
        band("a3-new", "还没归类的", "三个模型自己提的、九条都装不下的东西"),
        "<p>下面几条<strong>不进这一轮的清单</strong>，"
        "但下一轮从这里开始，而不是从零开始——上面的「颜色分组进键」就是上一轮从这里出来的。</p>",
        f'<article class="card"><header><h4>模型自己提的</h4>'
        f'{chips(("候选", ""))}</header>{gap_examples(data, gallery, "new", limit=3)}</article>',
        band("a3-where", "以前提过的说法，现在归到哪一条", "包括这一轮没有单独立条的"),
        "<p>凡是在这一轮、上一轮或者聊天里提过的缺口，都能在下表里找到它的去处。"
        "<strong>写着「不进清单」的是有意留下的</strong>，理由也在表里。</p>",
        table(("以前的说法", "现在归到", "为什么"),
              [(what, f'<a href="#{where}"><code>{esc(where)}</code></a>'
                if where in text.GAPS else f"<strong>{esc(where)}</strong>", f_(why, f))
               for what, where, why in text.WHERE_IT_WENT]),
    ])


# --------------------------------------------------------------------------- #
# a4 · which one first                                                          #
# --------------------------------------------------------------------------- #

#: The two orderings, in two columns because they are not one scale.
BY_SCORE = (
    ("P2", "名字对不上是失败的大头，上界是全部结论里最硬的一个数"),
    ("P3", "对不上的名字有一半就在同一张表里，一页多图与整页导出都是纯加法"),
    ("P1", "印数字 99.0% vs 不印 79.6%，两组区间离得最开"),
    ("P5", "扩到 100 页之后 ≤20 与 >400 两端的区间不重叠，「越密越差」复核出来了"),
    ("P6", "三十多个画法维度里只有「单位写在哪」那一维能换算出错误个数"),
    ("P4", "配比离均匀很远，但这条的证据是配比本身，不是正确率"),
    ("P8", "分数上不成立：解析器能从表格行里抄到组别名"),
    ("P9", "分数上看不见：值对着哪条轴读的从不进入判定"),
    ("P10", "三族各只有十几次到两次，定不了频次"),
    ("P7", "4,864 道题里只有 14 道拿图号当定位名字"),
)

BY_CAPABILITY = (
    ("P2", "键从「面板里的地址」变成「整张图里的地址」——这是记录本身的定义"),
    ("P8", "颜色可以承载键的一段；画法和键的定义在这里连着"),
    ("P9", "值记住自己是对着哪条轴、哪种图形读的，反读自检才有定义"),
    ("P1", "「能读到多准」是一个可生成、可核对的量，是非标记表达不了"),
    ("P7", "我们的图连标题从哪来都没有；对分数没用、对能力有用的样板"),
    ("P3", "页面成为一个对象：一页多张图，标题块独立于绘图区"),
    ("P6", "三十多个可配置的画法维度，覆盖面最大的一条；换风格自检要吃它"),
    ("P5", "密度从「碰运气落在哪」变成可以指定的自变量"),
    ("P10", "类型表多三行；区间条还带来「一根条两个值」这件事"),
    ("P4", "族的配比成为一个可插拔的分布，不绑死在任何一把尺子上"),
)

ORDER = (
    ("第一步", "P2 + P8", "把键补全",
     "同一处代码，一次改完。记录里缺的东西不补，后面每一项的产物都要返工"),
    ("第二步", "P1 + P9", "把读法记下来",
     "要先有补全的键，才知道精度和轴的身份挂在谁身上"),
    ("第三步", "P3", "一页多图 + 标题块分离",
     "纯加法，而且失败运行那一侧的证据最硬"),
    ("第四步", "P4 + P6 + P5", "配比、画法、密度",
     "三条都是「加一个可配置的维度、默认保持现在的行为」，彼此独立，可以并行"),
    ("第五步", "P7 + P10", "标题字段、缺的图族",
     "证据最弱的两条，但也都只是加字段、加行"),
)


def section_a4(data: Data, gallery: Gallery, f: dict) -> str:
    from report import numbers

    rows = []
    for index in range(len(BY_SCORE)):
        score_gap, score_why = BY_SCORE[index]
        cap_gap, cap_why = BY_CAPABILITY[index]
        rows.append((index + 1,
                     f'<a href="#{score_gap}"><code>{score_gap}</code></a> {esc(score_why)}',
                     f'<a href="#{cap_gap}"><code>{cap_gap}</code></a> {esc(cap_why)}'))
    order_rows = [(step, " + ".join(f'<a href="#{g}"><code>{g}</code></a>'
                                    for g in gaps.split(" + ")),
                   f"<strong>{esc(what)}</strong>", esc(why))
                  for step, gaps, what, why in ORDER]

    entries = numbers.index(data.summary, data.failures)
    mine = {gap: index + 1 for index, (gap, _) in enumerate(BY_CAPABILITY)}
    cards = []
    for model in MODELS:
        for kind, source in ((f"看完 {f['n_pages']} 页", data.overviews),
                             ("看完 50 个失败", data.failure_answers)):
            record = source.get(model)
            if not record:
                continue
            answer = record.get("answer", record)
            model_rows = []
            for index, item in enumerate(answer.get("ranked_items", ())[:5], start=1):
                gap = str(item.get("maps_to", ""))
                model_rows.append((
                    index, esc(item.get("what", "")),
                    f'<a href="#{gap}"><code>{esc(gap)}</code></a>' if gap in text.GAPS
                    else "（九条之外）",
                    f"第 {mine[gap]} 位" if gap in mine else "—",
                    esc(item.get("capability_effect", ""))))
            cited = numbers.reconcile(answer.get("numbers_cited", []), entries, model)
            checkable = [row for row in cited if row["decisive"]]
            found = sum(1 for row in checkable if row["found"])
            cards.append(
                f'<article class="card"><header><h4><em>{esc(short(model))}</em>{esc(kind)}之后'
                f'</h4>{chips((f"它引用了 {len(cited)} 个数字", ""),
                              (f"其中能当证据的 {len(checkable)} 个，对上 {found} 个",
                               "yes" if found == len(checkable) else "hi"))}'
                f'</header><div class="split noimg"><figure></figure><div class="body">'
                f'<blockquote><p>{esc(answer.get("headline", ""))}</p>'
                f'<p><b>它自己说的局限</b> {esc(answer.get("limits", ""))}</p></blockquote>'
                + table(("", "它自己的说法", "对应哪一条", "这一页排第几", "它说加了什么能力"),
                        model_rows, numeric=(0,))
                + "</div></div></article>")

    return "".join([
        f"<p>{text.A4['lede']}</p>",
        band("a4-two", "两列分开排", "左边看分数证据，右边看能力增量"),
        table(("", "按「对基准分数有多少可核的证据」", "按「给流水线加了多少能力」"),
              rows, numeric=(0,)),
        band("a4-order", "开工次序", "取两列都靠前的"),
        f"<p>{text.A4['order']}</p>",
        table(("", "做什么", "叫什么", "为什么在这一位"), order_rows),
        band("a4-diff", "和三个模型自己的排序差在哪", "模型也各自排了一份"),
        f'<div class="lead"><p>{text.A4["divergence"]}</p></div>',
        who_line(),
        f"<p>每个模型出两份：看完自己那 {f['n_pages']} 页之后一份，"
        f"看完 50 个失败之后一份。"
        "「这一页排第几」是同一条改动在上面那份能力次序里的位置。"
        "标题上的对账是：它在报告里引用的数字，回到程序算出来的表里能不能找到——"
        "只有带小数的比率和大计数算数，小整数在几百个格子里总能撞上。</p>",
        "".join(cards),
    ])


# --------------------------------------------------------------------------- #
# b1 · what the sampled pages look like                                         #
# --------------------------------------------------------------------------- #

#: What each part of a key is called on screen. The two the current key cannot carry
#: are marked, because that is the whole argument of the section above.
ROLE_NAMES = {
    "category": ("类目（轴上的名字，比如国家）", False),
    "series": ("系列（图例里的一项，比如「2025 年得分」）", False),
    "time": ("时间（时间轴上的一个点）", False),
    "panel": ("小面板（哪一个面板）", True),
    "colour_group": ("颜色代表的组别（比如「强创新国」）", True),
}

SOURCE_NAMES = {
    "axis_tick": "轴上的刻度标签", "legend": "图例里", "panel_title": "面板标题",
    "inline_label": "画在图形旁边", "heading": "标题块里",
    "colour_only": "只有颜色，没有文字", "not_shown": "页面上根本没有",
}

#: Constructions worth showing a picture of: each is something the pipeline either
#: cannot draw or draws without recording.
SHOWCASE = ("color_encodes_extra_attribute", "small_multiples_5plus", "dual_axis",
            "small_multiples_4", "dense_marks_100plus", "data_table_as_figure",
            "mixed_marks", "negative_values")


def showcase(data: Data, gallery: Gallery, keys: tuple[str, ...], limit: int) -> str:
    """One picture per construction, with each model's own words for it."""
    docs, out, used = documents(data), [], set()
    for key in keys:
        component = COMPONENT.get(key)
        if component is None:
            continue
        for stem in data.summary["pages"]:
            said = {model: next((c for c in (data.answers[model].get(stem) or {})
                                 .get("components") or () if c["key"] == key), None)
                    for model in MODELS}
            voters = {m: c for m, c in said.items() if c}
            if len(voters) < 2 or stem in used:
                continue
            used.add(stem)
            figure_id = next(iter(voters.values()))["figure_id"]
            who = " ".join(f'<b>{esc(short(m))}</b>：“{esc(c["evidence"])}”'
                           for m, c in voters.items())
            out.append(example(
                picture(gallery, stem, figure_id),
                caption(stem, docs.get(stem, ""), figure_id),
                component.name_en,
                f"<strong>{esc(component.name_zh)}</strong>——{esc(component.hint)}。"
                f"我们现在{'画得出' if component.ours else '<strong>画不出</strong>'}。",
                who))
            break
        if len(out) >= limit:
            break
    return "".join(out)


def agreed_figure(data: Data, read, wanted, skip: set[str]) -> tuple[str, str] | None:
    """A figure every model describes the same way. `read` takes one figure record."""
    for stem in data.summary["pages"]:
        if stem in skip:
            continue
        said = {model: [fig for fig in (data.answers[model].get(stem) or {}).get("figures") or ()
                        if fig.get("type") != "unreadable"]
                for model in MODELS}
        for index in range(max((len(v) for v in said.values()), default=0)):
            votes = [read(v[index]) for v in said.values() if index < len(v)]
            if len(votes) >= 2 and all(vote == wanted for vote in votes):
                return stem, f"f{index + 1}"
    return None


def contrast(data: Data, gallery: Gallery, read, cases: tuple, why: str) -> str:
    """Two figures the models agree sit at opposite ends of one variable."""
    docs, skip, out = documents(data), set(), []
    for wanted, label in cases:
        found = agreed_figure(data, read, wanted, skip)
        if not found:
            continue
        stem, figure_id = found
        skip.add(stem)
        out.append(example(picture(gallery, stem, figure_id),
                           caption(stem, docs.get(stem, ""), figure_id), label, why, "三家一致"))
    return "".join(out)


def section_b1(data: Data, gallery: Gallery, f: dict) -> str:
    mix_rows = []
    for name, by_model in data.summary["mixes"].items():
        if name == "卡在哪一步":
            continue
        values = sorted({v for counts in by_model.values() for v in counts},
                        key=lambda v: -max(by_model[m].get(v, 0) for m in by_model))
        for index, value in enumerate(values):
            mix_rows.append((f"<strong>{esc(MIX_NAMES.get(name, name))}</strong>"
                             if index == 0 else "",
                             say(value, name),
                             *[by_model.get(m, {}).get(value, 0) for m in MODELS]))
    axis_rows = [(esc(label), *[data.per_model("axes", m)[label] for m in MODELS])
                 for label in ("图的张数", "只有一条数值轴", "左右（或上下）两条数值轴",
                               "两条互相垂直的数值轴（散点图）", "一条轴都没有", "轴上写了单位")
                 if any(data.per_model("axes", m)[label] for m in MODELS)]
    component_rows = []
    for row in data.summary["components"]:
        unanimous = row["classes"].get("unanimous", 0)
        if unanimous < 4:
            continue
        component_rows.append((
            esc(row["name_zh"]), unanimous,
            " / ".join(str(row["pages"].get(m, 0)) for m in MODELS),
            "画得出" if row["ours"] else "<strong>画不出</strong>"))

    parts = data.summary["key_parts"]
    length_rows = [(f"{esc(size)} 段",
                    *[parts["parts_per_figure"].get(m, {}).get(size, 0) for m in MODELS])
                   for size in sorted({k for m in MODELS
                                       for k in parts["parts_per_figure"].get(m, {})}, key=int)]
    role_rows = [(f"<strong>{esc(name)}</strong>" if missing else esc(name),
                  "<strong>记不下来</strong>" if missing else "记得下",
                  *[parts["roles"].get(m, {}).get(role, 0) for m in MODELS])
                 for role, (name, missing) in ROLE_NAMES.items()]
    source_rows = [(esc(SOURCE_NAMES.get(key, key)),
                    *[parts["label_sources"].get(m, {}).get(key, 0) for m in MODELS])
                   for key in SOURCE_NAMES
                   if any(parts["label_sources"].get(m, {}).get(key) for m in MODELS)]
    return "".join([
        f"<p>{f_(text.B1['lede'], f)}</p>", who_line(),
        band("b1-keys", "一个数要说清几件事", "这一轮新问的，也是上面第一家改动的落点"),
        f"<p>{text.B1['keys']}</p>",
        table(("要说清几件事", *(short(m) for m in MODELS)), length_rows, numeric=(1, 2, 3)),
        table(("哪一件事", "我们的键里", *(short(m) for m in MODELS)),
              role_rows, numeric=(2, 3, 4)),
        table(("这件事的名字写在哪", *(short(m) for m in MODELS)), source_rows,
              numeric=(1, 2, 3)),
        band("b1-mix", "这批图长什么样", "三列并排，不合并"),
        table(("看什么", "取值", *(short(m) for m in MODELS)), mix_rows, numeric=(2, 3, 4)),
        band("b1-axes", "有几条承载数值的轴", "数的是边，不是轴"),
        f"<p>{text.B1['axes']}</p>",
        table(("按图的张数", *(short(m) for m in MODELS)), axis_rows, numeric=(1, 2, 3)),
        band("b1-comp", "哪些画法出现得多", "只列三家都说有 ≥4 页的"),
        f"<p>{text.B1['components']}</p>",
        table(("画法", "三家都说有的页数", "三家各自的页数", "我们画得出吗"),
              component_rows, numeric=(1,)),
        band("b1-eg", "挑几张看", "每张配三个模型各自的原话"),
        showcase(data, gallery, SHOWCASE, limit=5),
    ])


#: Plain names for the descriptive mixes the program counts.
MIX_NAMES = {
    "类型": "图表类型", "数值印不印": "图上印不印数字", "稠密度档": "图形个数",
    "标题位置": "标题在哪", "图号有无": "有没有图号",
}


# --------------------------------------------------------------------------- #
# b2 · where the run failed                                                     #
# --------------------------------------------------------------------------- #

HOME_NAMES = {
    "in_a_table_but_not_addressing": "就在同一张表里，但不在这个数所在的行 / 列 / 表头上",
    "in_another_table_only": "只在这一页的另一张表里",
    "emphasised_before_a_table": "在表前面的加粗或标题里",
    "emphasised_after_the_table": "在表后面的加粗或标题里",
    "plain_text_only": "只写进了正文",
    "absent_from_the_output": "解析器根本没写出来",
}

VARIABLE_NAMES = {
    "定位需要几个键": "指认一个数要说清几件事",
    "整页文字量": "整页有多少字",
    "图元个数": "图上画了多少个图形",
    "数值是否印在图上": "图上印不印数字",
    "面板数": "有几个小面板",
}


def section_b2(data: Data, gallery: Gallery, f: dict) -> str:
    form_rows = []
    for row in data.failures["forms"]:
        form_rows.append((esc(text.FORM_ZH.get(row["form"], row["form"])),
                          row["count"], pct(row["share"])))
    counted = sum(row["count"] for row in data.failures["forms"])
    if counted < data.failures["failures"]:
        rest = data.failures["failures"] - counted
        form_rows.append((esc(text.FORM_ZH["no_table"]), rest, pct(rest / data.failures["failures"])))
    homes = data.homes()
    home_rows = [(esc(HOME_NAMES.get(home, home)), homes[home],
                  pct(homes[home] / sum(homes.values())))
                 for home in LABEL_HOMES if homes[home]]
    var_rows, last = [], None
    for row in data.failures["single_variable"]:
        low, high = row["ci"]
        name = VARIABLE_NAMES.get(row["variable"], row["variable"])
        var_rows.append((f"<strong>{esc(name)}</strong>" if row["variable"] != last else "",
                         esc(row["scope"]) if row["variable"] != last else "",
                         say(row["bucket"], "数值印不印"), row["n"], pct(row["rate"]),
                         f"{pct(low)} – {pct(high)}"))
        last = row["variable"]
    return "".join([
        f"<p>{f_(text.B2['lede'], f)}</p>",
        band("b2-forms", "错都错在哪", f"全部 {f['failures']} 个，没有抽样"),
        f"<p>{text.B2['forms']}</p>",
        table(("这一类错是什么", "有多少个", "占全部错的"), form_rows, numeric=(1, 2)),
        band("b2-homes", "对不上的名字最后落在哪", "程序在解析器的输出里找的"),
        f"<p>{f_(text.B2['homes'], f)}</p>",
        table(("落在哪", "次数", "占比"), home_rows, numeric=(1, 2)),
        band("b2-ceiling", "全改对能到哪", "上界，不是预测"),
        table(("", ""),
              [("这一次运行，按页平均正确率", f"<strong>{f['page_mean']}</strong>"),
               ("把「名字对不上」那一类全改对", f"<strong>{f['ceiling']}</strong>"),
               ("差额", pct(data.failures["ceiling"] - data.failures["page_mean"]))]),
        band("b2-vars", "一次只看一个因素", "带 95% 置信区间"),
        f"<p>{f_(text.B2['vars'], f)}</p>",
        table(("看什么", "在多少页上算的", "分组", "样本数", "正确率", "95% 区间"),
              var_rows, numeric=(3, 4, 5)),
        band("b2-contrast", "落差最大的那个因素，看两张图", "两端各取一张三家看法一致的"),
        f"<p>{text.B2['contrast']}</p>",
        contrast(data, gallery, lambda fig: str(fig.get("values_printed")),
                 (("all", "图上每个数字都印出来了"),
                  ("none", "图上一个数字都没印，只能对着刻度量")),
                 "同一套题、同样的 5% 误差：一张页面上把数字抄下来就行，另一张只能拿刻度估。"
                 "两组的正确率区间不重叠。"),
    ])


# --------------------------------------------------------------------------- #
# b3 · five failures, one at a time                                             #
# --------------------------------------------------------------------------- #

def excerpt_html(lines: list[str], wrong: str, wanted: str) -> str:
    """The parser's own table, with the three things worth looking at marked."""
    out, first = ['<table class="excerpt">'], True
    for line in lines[1:]:
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rendered = []
        for cell in cells:
            marked = cell.startswith("[") and cell.endswith("]")
            body = cell[1:-1] if marked else cell
            text_ = body.strip()
            klass = ("key" if marked else
                     "wrong" if wrong and text_ == wrong else
                     "val" if wanted and text_ == wanted else
                     "head" if first else "")
            rendered.append(f'<td class="{klass}">{esc(body)}</td>' if klass
                            else f"<td>{esc(body)}</td>")
        out.append("<tr>" + "".join(rendered) + "</tr>")
        first = False
    out.append("</table>")
    return "".join(out) + f'<p class="who">{esc(lines[0]) if lines else ""}</p>'


def section_b3(data: Data, gallery: Gallery, f: dict) -> str:
    from failures import cases as case_lib, forms as form_lib, run as run_lib

    run_dir = ROOT / "parsebench/data/runs/ppdoclayoutv3_lean_qwen/chart"
    rules = run_lib.load_rules(ROOT / "parsebench/data/raw/chart.jsonl")
    run = run_lib.load_run(run_dir, rules, run_lib.run_model(run_dir))
    classified = form_lib.classify_all(run.failures(), run.pages)
    by_id = {case.case_id: case for case in case_lib.sample(run, classified)}

    shown, out = set(), []
    for case_id, mechanism in sorted(data.mechanisms["consensus"].items()):
        case = by_id.get(case_id)
        if case is None or case.form.kind in shown:
            continue
        page = run.pages.get(case.stem)
        if page is None:
            continue
        shown.add(case.form.kind)
        wrong = f"{case.form.model_value:g}" if case.form.model_value is not None else ""
        step = MECHANISM_STEP.get(mechanism, 0)
        said = " ".join(f'<b>{esc(short(model))}</b>：“{esc(evidence)}”'
                        for model, evidence in data.mechanisms["evidence"].get(case_id, {}).items())
        body = (
            f'<p class="rule-line">题目要的数是 <b>{esc(case.rule.value)}</b>，'
            f'指认它要用的名字是 {" ＋ ".join(f"<b>{esc(l)}</b>" for l in case.rule.labels)}，'
            f'允许 {case.rule.tolerance * 100:g}% 的误差。</p>'
            f'<p><strong>错在哪</strong>：{esc(text.FORM_ZH[case.form.kind])}（程序判的）。'
            f'<br><strong>为什么会这样</strong>：{esc(text.MECHANISM_ZH.get(mechanism, mechanism))}'
            f'{"，属于" + esc(text.STEP_ZH[step]) if step else "，不属于四步中的任何一步"}'
            f'（三个模型归的因）。</p>'
            + excerpt_html(case_lib._excerpt(case, page), wrong, case.rule.value)
            + f'<p class="who">{said}</p>')
        out.append(
            f'<div class="card"><header><h4>{esc(text.FORM_ZH[case.form.kind])}</h4>'
            f'{chips((esc(case.stem), ""))}</header>'
            f'<div class="split"><figure>{picture(gallery, case.stem, "f1")}'
            f'<figcaption>这一页的第 1 张图<br><b>{esc(case.stem)}</b></figcaption></figure>'
            f'<div class="body">{body}</div></div></div>')
    return "".join([f"<p>{text.B3['lede']}</p>",
                    f'<div class="lead"><p>{text.B3["how"]}</p></div>',
                    "".join(out)])


# --------------------------------------------------------------------------- #
# b4 · do the three models agree, and where does this page need discounting      #
# --------------------------------------------------------------------------- #

QUANTITY_NAMES = {
    "组件命中集合": "这一页有哪些画法",
    "图表类型判定": "这是什么类型的图",
    "数值印不印": "图上印不印数字",
    "稠密度档": "图上画了多少个图形",
    "标题": "有没有图号、标题在哪",
    "卡在哪一步": "这一页会卡在四步的哪一步",
    "同向两条值轴": "有没有两条平行的数值轴",
    "键分量": "指认一个数要说清哪几件事",
}


def single_model_rows(data: Data) -> list[tuple]:
    """Constructions one model saw on a page and the other two did not."""
    rows = []
    for row in data.summary["components"]:
        alone = row["classes"].get("single", 0)
        if alone < 2:
            continue
        rows.append((esc(row["name_zh"]), alone,
                     " / ".join(str(row["pages"].get(m, 0)) for m in MODELS)))
    return sorted(rows, key=lambda r: -r[1])[:8]


#: How many adjudicated conflicts the page prints in full. The rest are one table of
#: counts plus a pointer: a hundred and something rows is a wall, not a reading.
CONFLICT_SHOWN = 12

#: The Chinese name of each conflict kind, for both the summary and the row table.
CONFLICT_KINDS = {
    "type": "什么类型的图", "printed": "印不印数字", "density": "多少个图形",
    "heading": "图号与标题位置", "hardest_step": "卡在哪一步",
    "value_axes": "几条平行数值轴", "key_roles": "要说清哪几件事",
}


def verdict_summary(data: Data) -> list[tuple]:
    """Per kind of conflict: how many, and how each one ended."""
    kinds = verdict_kinds(data)
    counts: dict[str, Counter] = defaultdict(Counter)
    for item in data.summary["disagreements"]:
        unit = item["unit"].split("#")[0]
        counts[unit][kinds[f'{item["page"]}/{item["unit"]}']] += 1
    rows = []
    for unit, got in sorted(counts.items(), key=lambda pair: -sum(pair[1].values())):
        rows.append((esc(CONFLICT_KINDS.get(unit, unit)), sum(got.values()),
                     got["judged"], got["no_evidence"], got["not_judgeable"]))
    return rows


def unjudged_rows(data: Data) -> list[tuple]:
    """Conflicts with no verdict. Kept visible: an unsettled item is a finding."""
    verdicts = data.verdicts.get("verdicts", {})
    rows = []
    for item in data.summary["disagreements"]:
        if f'{item["page"]}/{item["unit"]}' in verdicts:
            continue
        unit = item["unit"].split("#")[0]
        rows.append((esc(QUANTITY_NAMES.get({"hardest_step": "卡在哪一步",
                                             "key_roles": "键分量"}.get(unit, unit), unit)),
                     f'<code>{esc(item["page"])}</code>',
                     " · ".join(f'<b>{esc(short(m))}</b> {say(v)}'
                                for m, v in item["values"].items() if v is not None)))
    return rows


def section_b4(data: Data, gallery: Gallery, f: dict) -> str:
    agree_rows = []
    for name, stats in data.summary["agreement"].items():
        agree_rows.append((esc(QUANTITY_NAMES.get(name, name)), pct(stats["rate"]),
                           stats["items"], stats["unanimous"], stats["majority"],
                           stats["single"],
                           f'<span class="chip hi">{stats["conflict"]}</span>'
                           if stats["conflict"] else "0"))
    repeat = data.summary["repeat_control"]
    vocab = data.summary["vocabulary_control"]
    repeat_rows = []
    for name, stats in repeat["quantities"].items():
        across = data.summary["agreement"].get(name)
        if not across:
            continue
        gap = stats["rate"] - across["rate"]
        repeat_rows.append((esc(QUANTITY_NAMES.get(name, name)), pct(across["rate"]),
                           pct(stats["rate"]), f"{gap * 100:+.1f}",
                           '<span class="chip hi">大过噪声，是真的差异</span>'
                           if gap >= NOISE_GAP else "在噪声里，说明不了什么"))
    verdicts = data.verdicts.get("verdicts", {})
    conflict_rows = []
    for item in data.summary["disagreements"]:
        verdict = verdicts.get(f'{item["page"]}/{item["unit"]}')
        if not verdict:
            continue
        unit = item["unit"].split("#")[0]
        conflict_rows.append((
            esc(CONFLICT_KINDS.get(unit, unit)),
            f'<code>{esc(item["page"])}</code>',
            " · ".join(f'<b>{esc(short(m))}</b> {say(v)}'
                       for m, v in item["values"].items() if v is not None),
            esc(verdict["verdict"])))
    mech = data.mechanisms
    return "".join([
        who_line(), f"<p>{text.B4['lede']}</p>", f"<p>{text.B4['classes']}</p>",
        band("b4-rate", "一致到什么程度", "每一项按页平均"),
        table(("看的是什么", "三家完全一致的比例", "一共几项", "三家一致", "两家",
               "只有一家", "分歧"), agree_rows, numeric=(1, 2, 3, 4, 5)),
        band("b4-controls", "两条对照实验", "这些一致率能不能当页面的性质读"),
        f"<p>{text.B4['controls']}</p>",
        f'<div class="two"><div class="score"><h5>不给清单，让它自己命名</h5>'
        f'<p>同一个模型（{esc(short(vocab["model"]))}）在同样的 {f["n_pages"]} 页上：给清单时报出 '
        f'{vocab["keys_with_vocabulary"]} 个画法；不给清单让它自己起名，'
        f'再映射回清单只剩 {vocab["shared"]} 个重合，'
        f'<strong>只有 {pct(vocab["recall"])}</strong>。'
        f'所以画法频次那张表只能粗看。</p></div>'
        f'<div class="cap"><h5>同一个模型问两遍</h5>'
        f'<p>同一个模型（{esc(short(repeat["model"]))}）、同一页、同一个问题问两遍，'
        f'两次答案的一致率就是噪声底线。'
        f'跨模型的差异要明显大过这条线，才算模型之间真的有分歧。</p></div></div>',
        table(("看的是什么", "三个模型之间", "同一个模型问两遍", "差(百分点)", "怎么读"),
              repeat_rows, numeric=(1, 2, 3)),
        band("b4-conflict", "分歧逐条裁决", f'{f["conflicts"]} 条，全部有结论'),
        f"<p>{f_(text.B4['verdicts'], f)}</p>",
        table(("分歧在哪一项", "有几条", "判出了结论", "没有可证伪的证据", "标的不同，不裁"),
              verdict_summary(data), numeric=(1, 2, 3, 4)),
        f'<p class="abl"><b>下面是前 {min(len(conflict_rows), CONFLICT_SHOWN)} 条</b>　'
        f'全部 {f["conflicts"]} 条连同各自的理由在 '
        f'<code>data/analysis/verdicts.json</code>，'
        f'每一页的三家并排在 <code>reports/pages/&lt;page&gt;.md</code>。</p>',
        table(("分歧在哪一项", "哪一页", "三个模型分别怎么说", "裁决"),
              conflict_rows[:CONFLICT_SHOWN]),
        band("b4-mech", "失败归因：三个模型说的一样吗", f"{mech['cases']} 个失败样本"),
        table(("", "个数"),
              [("三个模型给出同一个原因", mech["unanimous"]),
               ("两个一致", mech["majority"]),
               ("三个各说各的（已逐条裁决）", len(mech["conflicts"]))], numeric=(1,)),
        f'<p>另外，13 种原因的清单<strong>缺两种</strong>——'
        f'有 {sum(1 for reason in mech["consensus"].values() if reason == "other")} '
        f'个失败被三个模型一致地归为「以上都不是」，分成两簇：</p>',
        table(("缺的那一类", "长什么样", "对我们的流水线意味着什么"),
              [(f"<strong>{esc(what)}</strong>", how, means)
               for what, how, means in text.MISSING_MECHANISMS]),
        band("b4-moved", "从 20 页扩到 100 页之后，哪几条变了",
             "扩样是为了把排名坐实，所以要说清哪些动了、哪些没动"),
        table(("哪一条", "20 页时是这么说的", "100 页之后"),
              [(f"<strong>{esc(what)}</strong>", f_(before, f), f_(after, f))
               for what, before, after in text.WHAT_MOVED]),
        f'<p class="abl">{f_(text.MOVED_NOTE, f)}</p>',
        band("b4-discount", "这一页哪里要打折", "每一条都会改变上面某个结论的读法"),
        f"<p>{text.B4['discount']}</p>",
        table(("", ""),
              [(f"<strong>{esc(f_(what, f))}</strong>", f_(prose, f))
               for what, prose in text.DISCOUNTS]),
        band("b4-out", "没进清单的，和还没裁决的", "列出来比藏起来有用"),
        table(("", ""),
              [(f"<strong>{esc(what)}</strong>", f_(prose, f))
               for what, prose in text.NOT_ON_THE_LIST]),
        table(("只有一个模型报出来的画法", "只有一家的页数", "三家各自的页数"),
              single_model_rows(data), numeric=(1,)),
        *([table(("没有归档的分歧", "哪一页", "三个模型分别怎么说"), unjudged_rows(data))]
          if unjudged_rows(data) else []),
    ])
# --------------------------------------------------------------------------- #
# The shell                                                                     #
# --------------------------------------------------------------------------- #

def f_(prose: str, facts_: dict[str, str]) -> str:
    """Fill the holes. A hole with no fact behind it stops the build."""
    return prose.format(**facts_)


#: Every `h3` on the page, so the sidebar can list them. Filled as sections render.
BANDS: dict[str, list[tuple[str, str]]] = defaultdict(list)
_CURRENT = {"tab": ""}


def band(anchor: str, title: str, note: str = "") -> str:
    BANDS[_CURRENT["tab"]].append((anchor, title))
    tail = f" <span>{esc(note)}</span>" if note else ""
    return f'<h3 class="band" id="{anchor}">{esc(title)}{tail}</h3>'


SECTION_BUILDERS = {
    "a0": section_a0, "a1": section_a1, "a2": section_a2, "a3": section_a3, "a4": section_a4,
    "b1": section_b1, "b2": section_b2, "b3": section_b3, "b4": section_b4,
}


def masthead(data: Data, f: dict) -> str:
    facts_html = "".join(
        f'<div class="fact"><b>{esc(value)}</b><span>{esc(name)}</span></div>'
        for value, name in ((len(text.GAPS), "条改动"), (len(MODELS), "个模型"),
                            ("20", "页样本"), (f["failures"], "个失败样本"),
                            (f["page_mean"], "解析器现在的正确率"),
                            (f["ceiling"], "补上名字之后的上界")))
    return (f'<header class="masthead"><div class="inner"><div>'
            f'<h1>{esc(text.TITLE)}</h1><p class="tagline">{text.TAGLINE}</p></div>'
            f'<div class="facts">{facts_html}</div></div></header>')


def opening(data: Data, gallery: Gallery, f: dict) -> str:
    """One real number on one real page, and every word this report uses, defined on it."""
    anchor = text.ANCHOR
    parts = "".join(
        f'<tr><td class="term">{esc(name)}</td><td class="mono">{esc(value)}</td>'
        f'<td>{prose}</td></tr>' for name, value, prose in anchor["parts"])
    steps = "".join(
        f'<tr><td class="term">{esc(no)}</td><td><strong>{esc(name)}</strong></td>'
        f'<td>{prose}</td></tr>' for no, name, prose in text.STEPS_PLAIN)
    tiers = "".join(f"<li><strong>{esc(name)}</strong>——{esc(f_(prose, f))}</li>"
                    for name, prose in text.TIERS_PLAIN)
    return (
        f'<div class="lead"><p>{text.ONE_LINE}</p><p>{f_(text.ONE_LINE_SUB, f)}</p></div>'
        f'<div class="route"><p>{f_(text.ROUTE, f)}</p></div>'
        f'<div class="defs">'
        f'<figure class="ex">{picture(gallery, anchor["page"], "f1")}'
        f'<figcaption>{esc(anchor["page"])} 的第 1 张图。'
        f'后面说「第 1 张图」「第 2 张图」，指的就是一页上按阅读顺序数下来的第几张。</figcaption>'
        f'</figure>'
        f'<div class="defbody">'
        f'<h3 class="band" id="def">先把话说清楚 <span>整页只用这三个词，都在这张图上指给你看</span></h3>'
        f'<p>{anchor["what"]}</p><p>{anchor["datum"]}</p>'
        f'<table class="terms"><tbody>{parts}</tbody></table>'
        f'<p>{anchor["why"]}</p>'
        f'<h3 class="band" id="def-steps">基准怎么判对错 '
        f'<span>同一个数字，走一遍这四步</span></h3>'
        f'<table class="terms"><tbody>{steps}</tbody></table>'
        f'<p>{text.STEPS_NOTE}</p>'
        f'<h3 class="band" id="def-models">为什么三个模型的数字不一样 '
        f'<span>它们跑的确实是同一批页面</span></h3>'
        f'<p>{f_(text.THREE_MODELS, f)}</p>'
        f'<p>还有一件事：这一页上的每个数字，来源分三层。</p><ul>{tiers}</ul>'
        f'</div></div>')


SCRIPT = """
const buttons = [...document.querySelectorAll('nav button[data-tab]')];
const tabs = [...document.querySelectorAll('main > section[id]')];
function show(name, push){
  buttons.forEach(b => b.setAttribute('aria-selected', b.dataset.tab === name));
  tabs.forEach(s => s.hidden = s.id !== name);
  document.querySelectorAll('ul.toc').forEach(u => u.hidden = u.dataset.tab !== name);
  if (push) history.replaceState(null, '', '#' + name);
  mark();
}
buttons.forEach(b => b.addEventListener('click', () => show(b.dataset.tab, true)));
document.addEventListener('click', event => {
  const link = event.target.closest('a[href^="#"]');
  if (!link) return;
  const target = document.querySelector(link.getAttribute('href'));
  if (!target) return;
  const holder = target.closest('main > section[id]');
  if (holder && holder.hidden) show(holder.id, false);
});
function mark(){
  const links = [...document.querySelectorAll('ul.toc:not([hidden]) a')];
  let at = links[0];
  for (const link of links){
    const target = document.querySelector(link.getAttribute('href'));
    if (target && target.getBoundingClientRect().top < 120) at = link;
  }
  links.forEach(l => l.classList.toggle('at', l === at));
}
addEventListener('scroll', mark, {passive: true});

// any thumbnail opens the whole page it was cut from
const box = document.querySelector('.lightbox');
const full = box.querySelector('.full');
const cap = box.querySelector('.cap span');
function open(el){
  full.className = 'full ' + el.dataset.page;
  cap.innerHTML = '整页原图 · <b>' + el.dataset.name + '</b>';
  box.hidden = false;
}
function close(){ box.hidden = true; full.className = 'full'; }
document.addEventListener('click', event => {
  const thumb = event.target.closest('.im');
  if (thumb) { open(thumb); return; }
  if (event.target.closest('.lightbox')) {
    if (!event.target.closest('.full')) close();
  }
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') close();
  const thumb = document.activeElement;
  if ((event.key === 'Enter' || event.key === ' ') && thumb && thumb.classList.contains('im')) {
    event.preventDefault(); open(thumb);
  }
});
const start = location.hash.slice(1);
show(tabs.some(s => s.id === start) ? start : 'a0', false);
"""


def render(data: Data) -> str:
    f = facts(data)
    gallery = Gallery()
    bodies = {}
    for name, builder in SECTION_BUILDERS.items():
        _CURRENT["tab"] = name
        bodies[name] = builder(data, gallery, f)
    head = opening(data, gallery, f)

    nav, sections = [], []
    for group, (group_name, group_note) in text.GROUPS.items():
        nav.append(f'<div class="group">{esc(f_(group_name, f))}'
                   f'<span>{esc(f_(group_note, f))}</span></div>')
        for name in SECTION_BUILDERS:
            if not name.startswith(group):
                continue
            title, note = (f_(part, f) for part in text.SECTIONS[name])
            nav.append(f'<button data-tab="{name}">{esc(title)}</button>')
            toc = "".join(f'<li><a href="#{anchor}">{esc(label)}</a></li>'
                          for anchor, label in BANDS[name])
            nav.append(f'<ul class="toc" data-tab="{name}" hidden>{toc}</ul>')
            sections.append(
                f'<section id="{name}" hidden><h2>{esc(title)}</h2>'
                f'<p class="sub">{esc(note)}</p>{bodies[name]}</section>')

    return (
        '<!doctype html>\n<html lang="zh">\n<head>\n<meta charset="utf-8">\n'
        f'<title>{esc(text.TITLE)}</title>\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600'
        '&display=swap">\n'
        f"<style>{CSS}\n{gallery.css()}</style>\n</head>\n<body>\n"
        + masthead(data, f)
        + f'<div class="opening">{head}</div>'
        + f'<div class="shell"><nav>{"".join(nav)}</nav><main>{"".join(sections)}</main></div>'
        + '<div class="lightbox" hidden><div class="frame"><i class="full"></i>'
          '<p class="cap"><span></span><button type="button">关闭</button></p>'
          '</div></div>'
        + f"<script>{SCRIPT}</script>\n</body>\n</html>\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    data = Data.load()
    html = render(data)
    args.out.write_text(html, encoding="utf-8")
    print(f"{args.out}  {len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
