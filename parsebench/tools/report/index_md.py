"""The text version of the conclusion, generated from the same prose as the page.

`reports/view.html` is the report; this is the same argument in a file a diff can
read. It is generated rather than written so that the two cannot say different
things: both take their sentences from `view_text.py` and their numbers from
`data/stats/`, and neither has a number typed into it by hand.

Short on purpose. Every table of counts lives in `compare.md` and every picture in
`view.html`; repeating them here would only create a third place to go stale.

Usage:
    python parsebench/tools/report/index_md.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "parsebench" / "tools")]

from report import view, view_text as text                     # noqa: E402

OUT = ROOT / "parsebench/reports/INDEX.md"


def plain(html: str) -> str:
    """The prose without its markup. `<code>` becomes backticks; the rest is dropped."""
    html = re.sub(r"<code>(.*?)</code>", r"`\1`", html)
    html = re.sub(r"<strong>(.*?)</strong>", r"**\1**", html)
    html = re.sub(r'<a href="#([^"]+)">(.*?)</a>', r"\2", html)
    return re.sub(r"<[^>]+>", "", html).replace("&nbsp;", " ")


def render(data: view.Data) -> str:
    f = view.facts(data)
    out = [
        "# " + text.TITLE,
        "",
        "**先看图示版：[view.html](view.html)**——它自足，而且每一条都配着它是从哪张图上看出来的。"
        "本文件是同一份结论的纯文字版，由同一份文案与同一批数字生成，两边不会说不同的话。",
        "",
        "---",
        "",
        "## 一句话",
        "",
        plain(text.ONE_LINE),
        "",
        plain(view.f_(text.ONE_LINE_SUB, f)),
        "",
        "---",
        "",
        "## 要改什么",
        "",
        "十条改动，按做的顺序排。「扩还是加」＝在现有能力上多一个维度，还是清单上多一条；"
        "没有一条是删能力的。「对基准分数」写「不成立」的照样在清单里——"
        "ParseBench 是尺子不是目标，那几条靠的是它给流水线加了什么。",
        "",
        "| | 改什么 | 属于哪一家 | 扩还是加 | 证据来自 | 对基准分数 | 排第几步 |",
        "|---|---|---|---|---|---|---|",
    ]
    step_of = {gap: step for step, gaps, _, _ in view.ORDER
               for gap in gaps.split(" + ")}
    for step, gaps, _, _ in view.ORDER:
        for gap in gaps.split(" + "):
            body = text.GAPS[gap]
            _, verdict, _ = body["evidence"]
            out.append(f"| **{gap}** | {plain(body['title'])} | {view.FAMILY_OF[gap]} | "
                       f"{body['stance']} | {plain(view.f_(body['source'], f))} | "
                       f"{verdict} | {step_of[gap]} |")
    out.append("")
    for key, family in text.FAMILIES.items():
        out += [f"### {family['name']}", "", plain(view.f_(family["lede"], f)), "",
                "| 编号 | 改什么 | 扩还是加 | 对基准分数 | 依据在哪一层 |",
                "|---|---|---|---|---|"]
        for gap in family["gaps"]:
            body = text.GAPS[gap]
            tier, verdict, _ = body["evidence"]
            out.append(f"| **{gap}** | {plain(body['title'])} | {body['stance']} | "
                       f"{verdict} | {tier} |")
        out.append("")
        for gap in family["gaps"]:
            body = text.GAPS[gap]
            out += [f"**{gap} · {plain(body['title'])}**", "",
                    plain(view.f_(body["lede"], f)), "",
                    "- 对基准分数：" + plain(view.f_(body["score"], f)),
                    "- 对流水线的能力：" + plain(view.f_(body["capability"], f)),
                    "- 消融表因此多一行：" + plain(body["ablation"]), ""]
    out += [
        "---", "", "## 先做哪个", "",
        plain(text.A4["order"]), "",
        "| | 做什么 | 叫什么 | 为什么在这一位 |", "|---|---|---|---|",
    ]
    for step, gaps, what, why in view.ORDER:
        out.append(f"| {step} | {gaps} | **{what}** | {why} |")
    out += ["", plain(text.A4["divergence"]), "",
            "---", "", "## 从 20 页扩到 100 页之后，哪几条变了", "",
            "| 哪一条 | 20 页时是这么说的 | 100 页之后 |", "|---|---|---|"]
    for what, before, after in text.WHAT_MOVED:
        out.append(f"| **{what}** | {plain(view.f_(before, f))} | {plain(view.f_(after, f))} |")
    out += ["", plain(view.f_(text.MOVED_NOTE, f)), "",
            "---", "", "## 这一页哪里要打折", "",
            "| | |", "|---|---|"]
    for what, prose in text.DISCOUNTS:
        out.append(f"| **{plain(view.f_(what, f))}** | {plain(view.f_(prose, f))} |")
    out += ["", "没进清单的：", ""]
    for what, prose in text.NOT_ON_THE_LIST:
        out.append(f"- **{what}**——{plain(view.f_(prose, f))}")
    out += [
        "", "---", "", "## 产物", "",
        "| 文件 | 谁写的 | 内容 |", "|---|---|---|",
        "| [view.html](view.html) | agent | **唯一有结论的报告**，自足，配图 |",
        "| INDEX.md | agent | 本文件，同一份结论的纯文字版 |",
        "| [compare.md](compare.md) | 程序 | 全部数字，三家并列，没有结论 |",
        "| `<model>.md` | 模型 | 每个模型自己的两份报告与它自己的排序 |",
        "| `pages/<page>.md` | 程序 | 逐页三家并排 + 判分 + 裁决 |",
        "| [`verdicts.json`](../data/analysis/verdicts.json) | agent | 分歧裁决，是数据不是改写 |",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    args.out.write_text(render(view.Data.load()), encoding="utf-8")
    print(f"{args.out}")


if __name__ == "__main__":
    main()
