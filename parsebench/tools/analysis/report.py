"""One page's report: everything needed to judge that page without opening another file.

Six sections. The spot-check table carries both halves of the same row -- the
benchmark's value and labels, and what the model predicted for that value from the
image alone -- because the disagreement between them is the only place in this
pipeline where a claim is graded rather than counted.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from checks import PageResult, components_of, keys_of
from markdown import (FINDING_ZH, GENERALITY_ZH, PLACEMENT_ZH, PRINTED_ZH, STEP_ZH, cell)
from rules import Rule
from vocabulary import BY_KEY, VOCABULARY


def _tolerance(rule: Rule) -> str:
    return f"{rule.tolerance:.0%}" if rule.tolerance >= 0.01 else f"{rule.tolerance}"


def _heading(figure: dict) -> dict:
    return figure.get("heading") or {}


def _heading_line(figure: dict) -> str:
    """The heading as one line: number, title, subtitle, and where the block sits."""
    head = _heading(figure)
    parts = [str(head.get(k, "")).strip()
             for k in ("figure_number", "title", "subtitle") if str(head.get(k, "")).strip()]
    where = PLACEMENT_ZH.get(str(head.get("placement", "")), "?")
    unit = str(head.get("unit_text", "")).strip()
    tail = f"　单位 `{cell(unit)}`" if unit else "　（标题里没有单位）"
    return f"{cell(' / '.join(parts)) or '（无标题）'}　[{where}]{tail}"


def render_report(page: PageResult) -> str:
    analysis = page.analysis
    figures = analysis.get("figures") or []
    by_id = {str(f.get("id")): f for f in figures}
    estimated = len(page.rules) if "need_estimate" in page.tags else 0
    out: list[str] = [f"# {page.stem}", "", "![page](page.png)", ""]

    out += ["## 1 · 样本", "",
            "| 来源文档 | 标签组 | 抽查点 | 其中估读 |", "|---|---|---|---|",
            f"| {cell(page.document)} | `{page.tags}` | {len(page.rules)} | {estimated} |",
            "", cell(analysis.get("page_note", "")), ""]

    # ---------------------------------------------------------------- 2 · rules
    checks = analysis.get("spot_checks") or []
    out += ["## 2 · 抽查点与模型的定位", "",
            "左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——"
            "所以「需要哪些键」是预测，最后一列由程序判分。", "",
            "| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |",
            "|---|---|---|---|---|---|---|---|"]
    for i, (rule, figure_id) in enumerate(zip(page.rules, page.attribution), 1):
        check = checks[i - 1] if i - 1 < len(checks) else {}
        labels = " · ".join(f"`{cell(l)}`" for l in rule.labels)
        predicted = " · ".join(f"`{cell(k)}`" for k in (check.get("addressing_keys") or ())) or "—"
        printed = {True: "是", False: "否"}.get(check.get("printed_on_figure"), "—")
        out.append(f"| {i} | {cell(rule.value)} | {labels} | {_tolerance(rule)} "
                   f"| {cell(check.get('figure_id') or figure_id or '未归属')} "
                   f"| {cell(check.get('mark', '—')) or '—'} | {printed} | {predicted} |")
    if not page.rules:
        out.append("| — | | | | | | | |")
    out += ["", "**程序核对**（模型没有看到左半的标签列）：", ""]
    out += ([f"- {FINDING_ZH.get(f.code, f.code)}——{cell(f.detail)}" for f in page.findings]
            or ["- 无矛盾"])
    out.append("")

    # -------------------------------------------------------------- 3 · figures
    out += ["## 3 · 图表分解", "",
            "| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |",
            "|---|---|---|---|---|---|---|---|---|"]
    for figure in figures:
        kind = str(figure.get("type"))
        if kind == "other" and str(figure.get("type_other", "")).strip():
            kind = f"other · {figure['type_other']}"
        out.append(
            f"| {cell(figure.get('id'))} | `{cell(kind)}` "
            f"| {cell(figure.get('orientation'))} | {figure.get('panels')} "
            f"| {figure.get('series')} | {figure.get('categories')} | {figure.get('marks')} "
            f"| {PRINTED_ZH.get(figure.get('values_printed'), '?')} "
            f"| {cell(figure.get('value_axis_ticks') or '（不画值轴）')} |")
    out.append("")
    for figure in figures:
        out.append(f"- **{cell(figure.get('id'))}** {_heading_line(figure)}")
        source = str(figure.get("source_line", "")).strip()
        if source:
            out.append(f"  - 来源行：{cell(source)}")
    out.append("")

    # ----------------------------------------------------------- 4 · components
    present = components_of(analysis)
    lacking = sum(not BY_KEY[k].ours for k in keys_of(analysis))
    out += ["## 4 · 组件清单", "", "| key | 组件 | 在哪 | 我们 | 证据（模型写的） |",
            "|---|---|---|---|---|"]
    order = {c.key: i for i, c in enumerate(VOCABULARY)}
    for component in sorted(present, key=lambda c: order[c["key"]]):
        spec = BY_KEY[component["key"]]
        out.append(f"| `{spec.key}` | {spec.name_zh} | {cell(component.get('figure_id'))} "
                   f"| {'有' if spec.ours else '**无**'} | {cell(component.get('evidence'))} |")
    out += ["", f"词表 {len(VOCABULARY)} 项，本页出现 {len(keys_of(analysis))} 项，"
                f"其中我们画不出来的 {lacking} 项。", ""]

    out += ["### 新组件", "", "| 名字 | 在哪 | 证据 | 为什么要紧 |", "|---|---|---|---|"]
    new_components = analysis.get("new_components") or []
    out += ([f"| `{cell(c.get('name'))}` | {cell(c.get('figure_id'))} "
             f"| {cell(c.get('evidence'))} | {cell(c.get('why_it_matters'))} |"
             for c in new_components] or ["| — | | | 无 |"])
    out.append("")

    # ----------------------------------------------------------- 5 · difficulty
    step = analysis.get("hardest_step")
    out += ["## 5 · 难在哪", "", f"卡在 **{STEP_ZH.get(step, step)}**。", "",
            cell(analysis.get("difficulty_notes", "")), ""]
    unreadable = analysis.get("unreadable") or []
    if unreadable:
        out += ["整页原图判不出来的："] + \
               [f"- `{cell(u.get('figure_id'))}`（{cell((by_id.get(str(u.get('figure_id'))) or {}).get('type', '?'))}）"
                f"：{cell(u.get('reason'))}" for u in unreadable] + [""]

    # ---------------------------------------------------------- 6 · suggestions
    out += ["## 6 · 对 data pipeline 的意见", "",
            "| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |", "|---|---|---|---|---|"]
    suggestions = analysis.get("suggestions") or []
    out += ([f"| {s.get('maps_to')} | {GENERALITY_ZH.get(str(s.get('generality')), '—')} "
             f"| {cell(s.get('what_to_add'))} | {cell(s.get('where_to_change'))} "
             f"| {cell(s.get('new_ablation_row'))} |" for s in suggestions]
            or ["| — | | 无 | | |"])
    return "\n".join(out) + "\n"


def write_report(directory: Path, page: PageResult, page_png: Path) -> None:
    """A report directory: the markdown, the machine-readable form, and the page image.

    The image is linked rather than copied. `data/pages/` is regenerated from the
    PDFs and is not tracked, so a copy here would be 48 untracked megabytes that
    say nothing a link does not.
    """
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "report.md").write_text(render_report(page), encoding="utf-8")
    (directory / "analysis.json").write_text(
        json.dumps(page.to_json(), indent=2, ensure_ascii=False), encoding="utf-8")
    link = directory / "page.png"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(os.path.relpath(page_png, directory))
