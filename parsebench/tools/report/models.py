"""One file per model: the two reports it wrote, and its numbers held against ours.

This is the only file whose body is a model's own prose. It is printed as written --
`headline`, its own ordering, the report and its limits -- and every number in it
comes back in §3 beside the program's value for the same thing. A report that cites
numbers nobody can find is a readable finding about that report.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1])]

from contract.format import GAP_ITEMS                            # noqa: E402
from report import numbers                                       # noqa: E402
from report.tables import short, table                           # noqa: E402


def _ranked(items: list[dict]) -> str:
    rows = [[index, item["what"], item["why"],
             "、".join(item.get("evidence") or ()) or "—",
             ",".join(str(a) for a in item.get("affects") or ()) or "—",
             item["score_effect"], item["capability_effect"],
             item["new_ablation_row"], f"{item['maps_to']}"]
            for index, item in enumerate(items, start=1)]
    return table(["#", "what", "why", "证据页 / case", "affects", "对分数", "对能力",
                  "新增的消融行", "归入哪条 P"], rows)


def _overview(title: str, note: str, answer: dict | None) -> str:
    if not answer:
        return f"## {title}\n\n（这一家还没有这一份）\n"
    return "\n".join([
        f"## {title}", "", note, "",
        "**结论**：" + answer["headline"], "",
        "### 它的排序", "", _ranked(answer["ranked_items"]), "",
        "### 正文", "", answer["report_md"].strip(), "",
        "### 局限（它自己写的）", "", "> " + answer["limits"].strip(), ""])


def render(model: str, overview: dict | None, failure: dict | None,
           summary: dict, failure_stats: dict) -> str:
    entries = numbers.index(summary, failure_stats)
    cited = ((overview or {}).get("numbers_cited") or []) + \
            ((failure or {}).get("numbers_cited") or [])
    reconciled = numbers.reconcile(cited, entries, model)
    rows = [[row["claim"], row["value"], row["source"],
             row["status"] if row["found"] else f"**{row['status']}**",
             "是" if row["decisive"] else "否", row["where"] or "—"]
            for row in reconciled]
    sharp = [row for row in reconciled if row["decisive"]]
    hits = sum(1 for row in sharp if row["found"])

    gaps = "\n".join(f"- `{key}` = {text}" for key, text in GAP_ITEMS.items())
    return "\n".join([
        f"# {short(model)} 自己写的两份报告", "",
        f"模型 `{model}`。正文与排序原样印出，没有编辑；数字在第 3 节逐条对账。"
        f"「归入哪条 P」的取值域：\n\n{gaps}", "",
        _overview("1 · 样例 overview", "它读完自己那批页面之后写的。", overview),
        _overview("2 · 失败 overview", "它读完自己那批 case 的归因之后写的。", failure),
        "## 3 · 它引用的数字", "",
        f"逐条查这个数在程序的表里存不存在。全部 {len(rows)} 条里 {len(sharp)} 条是"
        f"带小数的比率或大计数（「可判别」= 是），其中 {hits} 条找得到；"
        f"其余是小整数，几百个格子里总能撞上一个，找到不算证据。"
        f"「最接近的一格」是按名字相似度猜的，模型的答案里没有记它读了哪一格。"
        f"找不到的**记录不改写**。", "",
        table(["claim", "模型自报的值", "它说的来源", "程序表里有没有这个数", "可判别",
               "最接近的一格"], rows), ""])
