"""One file per sampled page: three models on the same image, and the grading.

A page gets one file holding all three readings rather than one file per model per
page. The three are read against each other and against the same picture, and
splitting them by model would mean opening three files to compare one page.

This is the adjudication surface. §2 puts the model's prediction, the annotation's
real labels and what the parser run actually did with that point on one line, which
is the only direct evidence of whether a model's reading of a page can be trusted;
§3 lists what the three disagreed about, with whatever verdict has been recorded.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1])]

from analysis.rules import Rule, keys_agree                       # noqa: E402
from report.tables import short, table                            # noqa: E402

ROOT = Path(__file__).resolve().parents[3]


def _figures(answer: dict) -> list[dict]:
    return answer.get("figures") or []


def _page_section(page: dict, answers: dict[str, dict], models: list[str]) -> str:
    rows = [[f"`{page['stem']}`", page["document"], page["tags"], page["rules"],
             f"`parsebench/data/pages/{page['stem']}.png`"]]
    out = ["## 1 · 三家怎么读这一页", "",
           table(["页名", "文档", "文档级 tags", "抽查点数", "页面图像"], rows), "",
           "### 每一家的报告（`report_md`，原样印出）", ""]
    for model in models:
        answer = answers.get(model)
        if not answer:
            continue
        out += [f"**{short(model)}**", "", "> " + answer["report_md"].strip().replace("\n", "\n> "), ""]

    out += ["### 图表分解", ""]
    rows = []
    for model in models:
        for index, figure in enumerate(_figures(answers.get(model) or {}), start=1):
            heading = figure.get("heading") or {}
            name = figure.get("type")
            if name == "other" and figure.get("type_other"):
                name = f"other · {figure['type_other']}"
            rows.append([short(model), f"f{index}", name, figure.get("marks"),
                         heading.get("figure_number") or "—",
                         heading.get("placement") or "—", figure.get("values_printed")])
    out += [table(["模型", "图序号", "类型", "图元数", "图号", "标题位置", "数值印不印"], rows), ""]

    out += ["### 组件命中", ""]
    reported = {model: {c["key"]: c.get("evidence", "")
                        for c in (answers.get(model) or {}).get("components") or ()}
                for model in models}
    keys = sorted({key for byname in reported.values() for key in byname})
    rows = []
    for key in keys:
        marks = ["✓" if key in reported[m] else "—" for m in models]
        evidence = "；".join(f"{short(m)}: {reported[m][key]}" for m in models if key in reported[m])
        rows.append([f"`{key}`", *marks, evidence])
    out += [table(["key", *[short(m) for m in models], "证据原文"], rows), ""]

    out += ["### 词表外的自拟名字", ""]
    rows = []
    for model in models:
        for item in (answers.get(model) or {}).get("new_components") or ():
            rows.append([f"`{item.get('name')}`", short(model),
                         ",".join(str(a) for a in item.get("affects") or ()) or "—",
                         item.get("evidence", "")])
    out += [table(["名字", "哪家报的", "affects", "证据原文"], rows), ""]
    return "\n".join(out)


def _spot_section(rules: list[Rule], answers: dict[str, dict], models: list[str],
                  passed: dict[str, bool]) -> str:
    rows = []
    for index, rule in enumerate(rules):
        cells: list[object] = [rule.value, "、".join(rule.labels)]
        marks = []
        for model in models:
            checks = (answers.get(model) or {}).get("spot_checks") or []
            if index >= len(checks):
                cells.append("—")
                marks.append("—")
                continue
            check = checks[index]
            predicted = [str(k) for k in (check.get("addressing_keys") or ())]
            placed = str(check.get("figure_id")) != "not_found"
            cells.append("、".join(predicted) if placed else "not_found")
            marks.append("✓" if placed and keys_agree(predicted, rule.labels) else "✗")
        verdict = passed.get(rule.id)
        rows.append([*cells, *marks,
                     "过" if verdict else ("没过" if verdict is False else "—")])
    return "\n".join([
        "## 2 · 抽查点", "",
        "值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` "
        "判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。", "",
        table(["值", "规则的真实标签", *[f"{short(m)} 预测的键" for m in models],
               *[f"{short(m)} 对错" for m in models], "失败运行里过没过"], rows), ""])


def _conflict_section(stem: str, summary: dict, verdicts: dict, models: list[str]) -> str:
    rows = []
    for item in summary["disagreements"]:
        if item["page"] != stem:
            continue
        recorded = verdicts.get(f"{stem}/{item['unit']}") or {}
        rows.append([f"`{item['unit']}`",
                     *[json.dumps(item["values"].get(m), ensure_ascii=False)
                       for m in models],
                     recorded.get("verdict", "未裁决"), recorded.get("reason", "")])
    return "\n".join(["## 3 · 分歧与裁决", "",
                      table(["量", *[short(m) for m in models], "人工裁决", "理由"], rows), ""])


def render(page: dict, rules: list[Rule], answers: dict[str, dict], models: list[str],
           summary: dict, verdicts: dict, passed: dict[str, bool]) -> str:
    return "\n".join([
        f"# {page['stem']}", "",
        f"![{page['stem']}](../../data/pages/{page['stem']}.png)", "",
        _page_section(page, answers, models),
        _spot_section(rules, answers, models, passed),
        _conflict_section(page["stem"], summary, verdicts, models),
    ])
