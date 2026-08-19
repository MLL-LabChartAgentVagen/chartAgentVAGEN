"""What both renderings share: the Chinese wording, and how a table cell is written.

`parsebench/reports/` is a Chinese document tree, so the documents written into it
are Chinese while the code that builds them is English. Holding the wording in one
file keeps that boundary in one place -- and keeps a finding code from being
described two different ways in the page report and in the index.
"""

from __future__ import annotations

STEP_ZH = {
    1: "第一步 · 要有表",
    2: "第二步 · 找到值",
    3: "第三步 · 标签关联",
    4: "第四步 · 表外上下文",
}

FINDING_ZH = {
    "no_figures": "模型在这一页上没有找到图",
    "reasked_after_an_empty_answer": "首次调用返回空答案，加一句追问后重问了一次",
    "retried_with_a_larger_budget": "首次调用没返回（输出被 max_tokens 截断），加大预算重问了一次",
    "keys_missing": "规则需要的键比模型报出的图能提供的多",
    "unattributed_rules": "有规则的标签对不上任何一张图的名字",
    "estimate_tag_but_values_printed": "标签组是 need_estimate，模型却说数值全写出",
    "no_estimate_tag_but_values_absent": "没有估读点，模型却说数值一个都没写",
    "dense_not_flagged": "有图超过 100 个图元，组件清单里没有 dense_marks_100plus",
    "dense_flagged_without_marks": "标了 dense_marks_100plus，但没有图达到 100 个图元",
    "component_without_the_layout_it_needs": "组件要求的版面在图表分解里不成立，已剔除",
    "component_on_an_unknown_figure": "组件挂在一个本页不存在的图号上",
    "component_without_evidence": "报了组件但没写出证据",
    "panel_names_count_mismatch": "面板数与面板名个数不一致",
    "series_names_count_mismatch": "系列数与系列名个数不一致",
    "spot_check_count_mismatch": "给了 N 个值，模型回了另一个数目",
    "values_not_placed": "有值没能落到任何一个图元上",
    "addressing_keys_wrong": "模型预测的定位标签漏掉了规则实际用的标签",
    "estimate_tag_but_every_value_printed": "标签组是 need_estimate，模型却说每个值都印在图上",
    "other_type_unnamed": "类型报了 other 但没给名字",
}

GENERALITY_ZH = {
    "general": "通用",
    "common": "一类出版方",
    "house_style": "这份文档自己的习惯",
}

def affects_zh(affects: tuple[int, ...]) -> str:
    """Which scoring steps a component can change, for a table cell."""
    from vocabulary import STEP_NAMES
    return " · ".join(f"第{n}步 {STEP_NAMES[n]}" for n in affects) if affects else "**不影响**"


PLACEMENT_ZH = {
    "above": "图上方", "beside": "与图并排", "below": "图下方",
    "inside": "绘图区内", "none": "无标题",
}

PRINTED_ZH = {"all": "全部", "some": "部分", "none": "无"}


def cell(text: str) -> str:
    """Markdown table cells cannot hold a pipe or a line break."""
    return str(text).replace("|", "\\|").replace("\n", " ").strip()
