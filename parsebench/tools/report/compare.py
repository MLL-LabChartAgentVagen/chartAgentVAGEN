"""Every number, in one file, with no conclusions in it.

The division of labour the contract fixes: the models write prose, the program
writes numbers, the agent writes the one file that concludes. This is the program's
file. Nothing here is ranked and nothing is recommended; a cell that holds three
models' answers keeps them in three columns rather than averaging them, because an
average of three readings of a page is not a reading of the page.

Four sections. What the benchmark has that our pipeline has no definition for; what
the benchmark looks like; what the parser run got wrong; and what any of it can be
believed on -- the call cost, the one graded prediction, the agreement rates, the
models' own numbers against these, and the two vocabulary controls.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1])]

from contract.format import MECHANISMS, STEPS                          # noqa: E402
from report import numbers                                             # noqa: E402
from report.tables import (agreement_table, component_gaps, control_table,   # noqa: E402
                           cost_table, delta_table, form_table, missed_label_table,
                           missed_position_table, mix_table, pct, residual_table,
                           scoring_table, short, table, type_gaps, variable_table)

#: Which judgement step a failure form belongs to, so the models' `hardest_step`
#: can be set against what the run actually blocked on for the same pages.
FORM_STEP = {"no_table": 1, "value_off": 2, "unit_mismatch": 2, "value_absent": 2,
             "label_unlinked": 3, "row_missing": 3}


def _actual_steps(summary: dict, run_forms: dict[str, list[str]]) -> dict[int, int]:
    """For each sampled page, the step its failures actually landed on, most first."""
    counts: Counter = Counter()
    for stem in summary["pages"]:
        kinds = run_forms.get(stem) or []
        if not kinds:
            continue
        steps = Counter(FORM_STEP[kind] for kind in kinds)
        counts[steps.most_common(1)[0][0]] += 1
    return dict(counts)


def _step_section(summary: dict, run_forms: dict[str, list[str]]) -> str:
    models = summary["models"]
    claimed = summary["mixes"]["卡在哪一步"]
    actual = _actual_steps(summary, run_forms)
    rows = [[f"{step} · {text}", *[claimed[m].get(str(step), 0) for m in models],
             actual.get(step, 0)]
            for step, text in STEPS.items()]
    return table(["步", *[f"{short(m)} 报的页数" for m in models],
                  "这批页在失败运行里实际卡住的步（按页多数）"], rows)


def _mechanism_section(stats: dict, mechanisms: dict, verdicts: dict) -> str:
    if not mechanisms:
        return "（三家的失败归因还没有跑完）"
    models = mechanisms["models"]
    rows = []
    for key, (step, text) in MECHANISMS.items():
        per_model = [mechanisms["per_model"].get(m, {}).get(key, 0) for m in models]
        weighted = mechanisms["weighted"].get(key)
        if not any(per_model) and not weighted:
            continue
        agreed = sum(1 for case, value in mechanisms["consensus"].items() if value == key)
        example = next((f"`{case}` / {mechanisms['case_pages'][case]}"
                        for case, value in mechanisms["consensus"].items() if value == key), "—")
        rows.append([f"`{key}`",
                     f"{step} · {STEPS[step]}" if step else "映不回四步",
                     *per_model, agreed,
                     pct(weighted[0]) if weighted else "—",
                     round(weighted[1]) if weighted else "—", example])
    head = table(["机制", "归入哪一步", *[f"{short(m)} 条数" for m in models],
                  "两家以上同意的条数", "折算到全运行的占比", "折算条数", "一个实例"], rows)

    conflicts = mechanisms["conflicts"]
    rows = []
    for item in conflicts:
        recorded = verdicts.get(item["case_id"]) or {}
        rows.append([f"`{item['case_id']}`", item["page"], f"`{item['form']}`",
                     "；".join(f"{short(m)}: `{v}`" for m, v in item["values"].items()),
                     recorded.get("verdict", "未裁决"), recorded.get("reason", "")])
    return "\n\n".join([
        f"抽样 {mechanisms['cases']} 条，三家全同意 {mechanisms['unanimous']} 条、"
        f"两家同意 {mechanisms['majority']} 条、三家各说各的 {len(conflicts)} 条。"
        f"「折算到全运行」= 每种形态内的机制占比 × 该形态在全部 896 个失败里的个数，"
        f"因为抽样是每形态等量抽，不是按比例抽。",
        head, "**三家各说各的，agent 逐条裁决**（裁决在 "
        "[`verdicts.json`](../data/analysis/verdicts.json)，模型的原答案不改）", table(
            ["case", "页", "形态", "三家各自的机制", "人工裁决", "理由"], rows)])


def render(summary: dict, stats: dict, mechanisms: dict,
           run_forms: dict[str, list[str]], overviews: dict[str, dict],
           verdicts: dict | None = None) -> str:
    models = summary["models"]
    entries = numbers.index(summary, stats)
    reconciled = []
    sharp = found = 0
    for model, overview in overviews.items():
        for row in numbers.reconcile(overview.get("numbers_cited") or [], entries, model):
            sharp += row["decisive"]
            found += row["decisive"] and row["found"]
            reconciled.append([short(model), row["claim"], row["value"],
                               row["status"] if row["found"] else f"**{row['status']}**",
                               "是" if row["decisive"] else "否", row["where"] or "—"])

    ranked = []
    for model, overview in overviews.items():
        for index, item in enumerate((overview.get("ranked_items") or [])[:3], start=1):
            ranked.append([short(model), index, item["what"], item["maps_to"],
                           ",".join(str(a) for a in item.get("affects") or ()) or "—"])

    return "\n".join([
        "# 三家并排：全部数字", "",
        f"程序写的。{len(summary['pages'])} 页 × {len(models)} 家，"
        f"外加两条控制。**这一份没有结论**——结论在 [INDEX.md](INDEX.md)，"
        f"逐页的原始并排在 [pages/](pages/)。", "",
        "## 1 · 缺口表", "",
        "基准里有、而 `storyline/parsebench_chart/` 没有定义的东西。"
        "三家各报各的页数，永远不合并；`affects` 与「我们画得出」是看页面之前按定义定死的。", "",
        "### 组件", "", component_gaps(summary), "",
        "### 类型", "", type_gaps(summary), "",
        "### 词表外的自拟名字（出现 ≥2 页的）", "", residual_table(summary), "",
        "## 2 · 基准长什么样", "",
        "描述，没有待办。每一格三家并列。", "",
        "### 数值印不印", "", mix_table(summary, "数值印不印"), "",
        "### 稠密度档", "", mix_table(summary, "稠密度档"), "",
        "### 标题位置", "", mix_table(summary, "标题位置"), "",
        "### 图号有无", "", mix_table(summary, "图号有无"), "",
        "### 卡在哪一步", "", _step_section(summary, run_forms), "",
        "## 3 · 失败", "",
        f"运行 `{stats['run']}`（{stats['parser_model']}），{stats['pages']} 页 / "
        f"{stats['points']} 个抽查点，按页平均 **{pct(stats['page_mean'])}**，"
        f"{stats['failures']} 个失败。形态由程序算，机制由三家归因。", "",
        "### 失败形态（全部失败上算，不抽样）", "", form_table(stats), "",
        f"寻址失败（`label_unlinked` + `row_missing`）全部改对的上界："
        f"按页平均 {pct(stats['page_mean'])} → **{pct(stats['ceiling'])}**。", "",
        "### 单变量通过率", "",
        "前两条的分母是全部 568 页，后三条只能在三家描述过的样本页上算，n 因此小得多。", "",
        variable_table(stats), "",
        "### 控制组（图上一个数值都不写的点）内，各组件的通过率差", "",
        "控制组是样本页里数值一个不写的点。只有「区间不重叠」为「是」的行值得读。", "",
        delta_table(stats), "",
        "### 机制", "", _mechanism_section(stats, mechanisms, verdicts or {}), "",
        "## 4 · 能不能信", "",
        "### 调用口径", "", cost_table(summary), "",
        "### 判分：预测的定位键 vs 规则的真实标签", "",
        "这是十个对齐量里**唯一可核**的一个：值送进了 prompt、标签没有。", "",
        scoring_table(summary), "",
        "**漏掉的是哪一个标签**（三家合计，一行是一个标签）", "",
        missed_position_table(summary), "",
        missed_label_table(summary), "",
        "### 一致率", "",
        "分母是至少一家报过的项，分子是三家一致的项，按页算再平均。"
        "**一致不是要最大化的分数**——它只用来把「基准的性质」与「一家模型的读法」分开。", "",
        agreement_table(summary), "",
        "### 三家各自的前三名", "",
        table(["模型", "#", "what", "归入哪条 P", "affects"], ranked), "",
        "### 自报 vs 实测", "",
        f"三家 overview 里 `numbers_cited` 的每一条，查它在程序的表里存不存在。"
        f"{len(reconciled)} 条里 {sharp} 条是带小数的比率或大计数（「可判别」= 是），"
        f"其中 {found} 条找得到；其余是小整数，几百个格子里总能撞上一个，找到不算证据。"
        f"「最接近的一格」按名字相似度猜，模型的答案里没有记它读了哪一格。", "",
        table(["模型", "claim", "模型自报", "程序表里有没有这个数", "可判别",
               "最接近的一格"], reconciled), "",
        "### 词表控制", "", control_table(summary), "",
    ])
