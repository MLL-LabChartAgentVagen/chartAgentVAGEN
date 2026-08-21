"""Markdown tables, each one a row-definition from `format.REPORTS`.

Two consumers, which is why they are here rather than inside a report: the report
files print them, and the overview prompts hand a subset of them to the model, so
its prose is written against the program's counts rather than against what it
remembers reporting. One renderer means the number the model was shown and the
number the report prints cannot drift apart.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1])]

from contract.format import FORMS, MECHANISMS, STEPS               # noqa: E402


def table(headers: list[str], rows: list[list[object]]) -> str:
    """A markdown table. An empty body still prints its header, which is a finding."""
    lines = ["| " + " | ".join(str(h) for h in headers) + " |",
             "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join("" if c is None else str(c) for c in row) + " |"
              for row in rows]
    return "\n".join(lines)


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def short(model: str) -> str:
    """A model name short enough to be a column header."""
    return model.split("/")[-1].replace("-preview", "").replace("claude-", "")


# --------------------------------------------------------------------------- #
# The sample                                                                    #
# --------------------------------------------------------------------------- #

def component_gaps(summary: dict, limit: int = 0) -> str:
    """One row per vocabulary key: each model's page count, the class, the spread."""
    models = summary["models"]
    rows = []
    for item in summary["components"][:limit or None]:
        classes = item["classes"]
        rows.append([
            f"`{item['key']}`", item["name_zh"],
            *[item["pages"][m] for m in models],
            f"{classes.get('unanimous', 0)}/{classes.get('majority', 0)}/"
            f"{classes.get('single', 0)}",
            ",".join(str(a) for a in item["affects"]) or "—",
            max(item["documents"].values()),
            "是" if item["ours"] else "否",
        ])
    return table(["key", "中文名", *[f"{short(m)} 页数" for m in models],
                  "一致/两家/一家", "affects", "文档数（最多一家）", "我们画得出"], rows)


def type_gaps(summary: dict) -> str:
    """One row per chart type: how many figures each model called it."""
    models = summary["models"]
    mix = summary["mixes"]["类型"]
    types = sorted({t for counts in mix.values() for t in counts},
                   key=lambda t: -sum(mix[m].get(t, 0) for m in models))
    rows = [[f"`{t}`", *[mix[m].get(t, 0) for m in models],
             "是" if _drawable(t) else "否"] for t in types]
    return table(["类型", *[f"{short(m)} 图数" for m in models], "条件表有这一族"], rows)


def _drawable(chart_type: str) -> bool:
    from contract.vocabulary import CHART_TYPE_OURS
    return bool(CHART_TYPE_OURS.get(chart_type, (False, ""))[0])


def mix_table(summary: dict, name: str) -> str:
    """One descriptive mix, one column per model. Never summed across models."""
    models = summary["models"]
    counts = summary["mixes"][name]
    values = sorted({v for by_model in counts.values() for v in by_model},
                    key=lambda v: -sum(counts[m].get(v, 0) for m in models))
    rows = [[value, *[counts[m].get(value, 0) for m in models]] for value in values]
    return table([name, *[short(m) for m in models]], rows)


def agreement_table(summary: dict) -> str:
    """One row per aligned quantity: the four classes and the rate."""
    rows = [[name, s["unanimous"], s["majority"], s["single"], s["conflict"], pct(s["rate"])]
            for name, s in summary["agreement"].items()]
    return table(["量", "三家一致", "两家", "一家", "冲突", "一致率（按页平均）"], rows)


def scoring_table(summary: dict) -> str:
    """The one graded quantity: predicted addressing keys against the rule's labels."""
    rows = []
    for model, counts in summary["key_predictions"]["per_model"].items():
        points, correct = counts.get("points", 0), counts.get("correct", 0)
        rows.append([short(model), counts.get("placed", 0), points, correct,
                     pct(correct / points) if points else "—"])
    return table(["模型", "落位的值数", "抽查点数", "预测对的数", "命中率"], rows)


def missed_label_table(summary: dict, limit: int = 20) -> str:
    """Which of a rule's labels the models fail to predict, most missed first.

    The companion to the score: knowing 70% of key sets are right says nothing about
    *which* key is wrong, and every row of the change list that touches addressing
    turns on that. One row is one label, counted over the three models together,
    because the question here is what the pages do, not which model reads them.
    """
    rows = [[row["position"], f"`{row['label']}`", row["missed"], row["hit"],
             pct(row["missed"] / (row["missed"] + row["hit"]))]
            for row in summary["key_predictions"]["missed_labels"][:limit]]
    return table(["它是规则的第几个标签", "标签", "三家合计漏掉几次", "报对几次", "漏掉率"],
                 rows)


def missed_position_table(summary: dict) -> str:
    """The same misses, rolled up to which position in the rule the label sits at."""
    models = summary["models"]
    rows = []
    for position in (1, 2, 3):
        counts = [summary["key_predictions"]["per_model"][m].get(
            f"missed_label_{position}", 0) for m in models]
        if any(counts):
            rows.append([f"第 {position} 个标签", *counts])
    return table(["标签位置", *[f"{short(m)} 漏掉几次" for m in models]], rows)


def cost_table(summary: dict) -> str:
    rows = [[short(row["model"]), row["control"] or "—", row["effort"], row["dpi"],
             row["calls"], f"{row['input_tokens']:,}", f"{row['output_tokens']:,}",
             f"{row['seconds']:.0f}s", row["re_asked"],
             "、".join(f"{route} {n}" for route, n in sorted((row.get("via") or {}).items()))]
            for row in summary["cost"]]
    return table(["模型", "控制", "effort", "dpi", "调用次数", "输入 token",
                  "输出 token", "累计用时", "空答案重问", "走哪条通路"], rows)


def control_table(summary: dict) -> str:
    """The two vocabulary controls and the noise floor, in one place."""
    lines = []
    free = summary.get("vocabulary_control") or {}
    if free:
        lines.append("**无词表对照**（" + short(free["model"]) + "，同一批页面，prompt 不给词表）\n")
        lines.append(table(
            ["有词表报出的 key 数", "无词表自由命名映回词表后的 key 数", "重合的 key 数",
             "重合率（占有词表的）", "重合率（占映回的）"],
            [[free["keys_with_vocabulary"], free["keys_mapped_back"], free["shared"],
              pct(free["recall"]), pct(free["precision"])]]))
        unmapped = sorted({n for page in free["pages"] for n in page["unmapped"]})
        lines.append(f"\n映不回词表的自由名字 {len(unmapped)} 个："
                     + ("、".join(f"`{n}`" for n in unmapped[:30]) or "无"))
    repeat = summary.get("repeat_control") or {}
    if repeat:
        lines.append("\n**自身重跑**（" + short(repeat["model"])
                     + "，同一批页面同一 prompt 再答一次；这是本底噪声）\n")
        lines.append(table(["量", "两次一致", "只有一次报了", "取值不同", "一致率"],
                           [[name, s["unanimous"] + s["majority"] * 0, s["single"],
                             s["conflict"], pct(s["rate"])]
                            for name, s in repeat["quantities"].items()]))
    residual = summary.get("new_components") or []
    lines.append(f"\n**词表外残差**：三家共报出 {len(residual)} 条词表没有的构造，"
                 f"去重后 {len({r['name'] for r in residual})} 个名字。")
    return "\n".join(lines)


def residual_table(summary: dict, min_pages: int = 2) -> str:
    """Free names proposed on more than one page -- the next round's candidate keys."""
    grouped: dict[str, dict] = {}
    for row in summary["new_components"]:
        item = grouped.setdefault(str(row["name"]), {"pages": set(), "models": set(),
                                                     "affects": set(), "evidence": ""})
        item["pages"].add(row["page"])
        item["models"].add(row["model"])
        item["affects"].update(row["affects"])
        item["evidence"] = item["evidence"] or str(row["evidence"])
    rows = [[f"`{name}`", len(item["pages"]), len(item["models"]),
             ",".join(str(a) for a in sorted(item["affects"])) or "—", item["evidence"]]
            for name, item in sorted(grouped.items(), key=lambda kv: -len(kv[1]["pages"]))
            if len(item["pages"]) >= min_pages]
    return table(["自拟名字", "出现页数", "几家报过", "affects", "一条证据"], rows)


# --------------------------------------------------------------------------- #
# The failure run                                                               #
# --------------------------------------------------------------------------- #

def form_table(stats: dict) -> str:
    rows = []
    for row in stats["forms"]:
        homes = "；".join(f"{home} {n}" for home, n in list(row["homes"].items())[:3])
        rows.append([f"`{row['form']}`", FORMS[row["form"]], row["count"],
                     pct(row["share"]), homes or "—"])
    return table(["形态", "定义", "个数", "占失败", "失联键的去向（前三）"], rows)


def variable_table(stats: dict) -> str:
    rows = [[row["variable"], row["scope"], row["bucket"], pct(row["rate"]), row["n"],
             f"[{pct(row['ci'][0])}, {pct(row['ci'][1])}]"]
            for row in stats["single_variable"]]
    return table(["自变量", "分母", "档", "通过率", "n", "95% 区间"], rows)


def delta_table(stats: dict) -> str:
    rows = [[f"`{row['key']}`", row["pages"], pct(row["with"]["rate"]), row["with"]["n"],
             pct(row["without"]["rate"]), row["without"]["n"], pct(row["delta"]),
             "是" if row["separated"] else "否"]
            for row in stats["component_deltas"]]
    return table(["组件", "出现页数", "有它的通过率", "n", "没有它的通过率", "n",
                  "差", "区间不重叠"], rows)


def mechanism_table(stats: dict, models: list[str]) -> str:
    """One row per mechanism: each model's count within the sample, and the class."""
    counts = stats.get("mechanisms", {})
    rows = []
    for key, (step, text) in MECHANISMS.items():
        per_model = [counts.get(m, {}).get(key, 0) for m in models]
        if not any(per_model):
            continue
        rows.append([f"`{key}`", STEPS.get(step, "映不回四步"), *per_model,
                     stats.get("mechanism_agreement", {}).get(key, "—"), text])
    return table(["机制", "归入哪一步", *[short(m) for m in models], "三家一致的条数", "定义"],
                 rows)


def mechanism_weighted(stats: dict) -> str:
    """The sample's mechanism counts weighted back by the full-run form counts."""
    rows = [[f"`{key}`", STEPS.get(MECHANISMS[key][0], "映不回四步"),
             f"{share:.1%}", round(count)]
            for key, (share, count) in stats.get("weighted", {}).items()]
    return table(["机制", "归入哪一步", "折算到全运行的占比", "折算条数"], rows)


def brief_for_sample(summary: dict) -> str:
    """The tables a model is handed before it writes its report of the sampled pages."""
    return "\n\n".join([
        "### 你自己那批答案里的组件计数（三家并列，你是其中一列）",
        component_gaps(summary, limit=40),
        "### 类型配比（三家并列）", type_gaps(summary),
        "### 数值印不印 / 稠密度档 / 标题位置 / 卡在哪一步（三家并列）",
        mix_table(summary, "数值印不印"), mix_table(summary, "稠密度档"),
        mix_table(summary, "标题位置"), mix_table(summary, "卡在哪一步"),
        "### 三家的一致率（这不是要最大化的分数，它只用来分开「基准的性质」与「一家的读法」）",
        agreement_table(summary),
        "### 唯一可核的量：预测的定位键 vs 规则真实标签", scoring_table(summary),
        "### 词表外残差（出现 ≥2 页的自拟名字）", residual_table(summary),
    ])


def brief_for_failures(stats: dict) -> str:
    """The tables a model is handed with the failure batch."""
    return "\n\n".join([
        f"这次运行：按页平均 {pct(stats['page_mean'])}，"
        f"{stats['points']} 个抽查点，{stats['failures']} 个失败。"
        f"寻址失败全部改对的上界是按页平均 {pct(stats['ceiling'])}。",
        "### 失败形态（全部失败上算，不抽样）", form_table(stats),
        "### 单变量通过率", variable_table(stats),
        "### 控制组（图上一个数值都不写的点）内，各组件的通过率差", delta_table(stats),
    ])
