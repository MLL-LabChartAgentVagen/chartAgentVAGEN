"""The one summary document: what the pipeline has to gain, in what order.

This is the point of the exercise. A page report says what one page uses; this
says what the whole sample together demands, and it is ordered so the first row is
the first thing to build.

Three sections, split by question rather than by topic: what we have to build,
what the corpus actually looks like, and how far to trust the run. A chart type
we cannot draw belongs in the first with every other gap; the type mix belongs in
the second with every other description. Splitting by topic instead put the same
object in two places and made the reader hunt for which table was the to-do.

Regenerated on every run, so nothing in it can go stale. Editorial judgement
belongs in `parsebench/README.md`'s TODO, not here.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict

from checks import PageResult, components_of, evidence_of, keys_agree, keys_of
from markdown import FINDING_ZH, PLACEMENT_ZH, PRINTED_ZH, STEP_ZH, affects_zh, cell
from vocabulary import CHART_TYPE_OURS, GROUP_TITLES, VOCABULARY

#: Below this many pages, document spread says nothing: 3 pages can only ever be
#: 1 to 3 documents, and both readings are within sampling noise.
GENERALITY_FLOOR = 4

#: How much of a piece of evidence counts when ranking examples. Enough to tell a
#: sentence from a fragment; past it, longer is just wordier, and letting length
#: run free sends the reader to a page with a long axis title over one where the
#: whole criterion is spelled out.
EVIDENCE_CREDIT = 80


def countable_figures(page: PageResult) -> list[dict]:
    """The figures that are figures.

    A model that lists a decorative band or a note block as a figure says so in
    `unreadable`. Counting those in the type mix would put them in the table P4's
    weight vector is read off, so they come out here and the count of what came
    out is printed beside the table.
    """
    flagged = {u.get("figure_id") for u in (page.analysis.get("unreadable") or ())}
    return [f for f in (page.analysis.get("figures") or ()) if f.get("id") not in flagged]


def component_pages(pages: list[PageResult]) -> Counter:
    return Counter(k for p in pages for k in keys_of(p.analysis))


def component_documents(pages: list[PageResult]) -> dict[str, Counter]:
    """Which documents each component was seen in, and how many pages of each."""
    out: dict[str, Counter] = defaultdict(Counter)
    for page in pages:
        for key in keys_of(page.analysis):
            out[key][page.document] += 1
    return out


def generality(pages_seen: int, documents: Counter, total_documents: int) -> tuple[str, str]:
    """How far a component reaches beyond one publisher, and the number behind it.

    Document spread, not page count: 22 pages from 18 documents is a convention of
    the trade, 6 pages from 1 document is that document's own habit, and the page
    count alone cannot tell them apart.

    The spread is measured against the most documents those pages *could* have come
    from, `min(pages, documents in the sample)`. Dividing by the page count instead
    would mark every frequent component concentrated by construction: 145 pages drawn
    from a 70-document sample can never touch more than 70 of them, so the ratio would
    fall as the component got more common. Normalised this way, 1.0 means every page
    came from a different document.

    Under `GENERALITY_FLOOR` pages there are too few values to read, and it says so
    instead of guessing.
    """
    docs = len(documents)
    if pages_seen < GENERALITY_FLOOR:
        return "样本不足", f"{docs} 份"
    reach = min(pages_seen, total_documents)
    spread = docs / reach
    # The ratio is printed, not just the verdict: 0.44 and 0.46 land in different
    # buckets and a reader who cannot see which is which will read the cut as sharp.
    detail = f"{docs} / 最多 {reach} 份 = {spread:.2f}"
    if spread >= 0.7:
        return "通用", detail
    if spread >= 0.45:
        return "常见", detail
    return "集中", detail


#: `Component.basis` names the gap item when there is one -- "见 P6", "，见 P1".
_GAP_IN_BASIS = re.compile(r"\bP[1-7]\b")


#: How wide a band around the `常见` cut counts as "the number did not decide this".
#: 0.44 and 0.45 landing in different lists is the threshold talking, not the data.
BORDERLINE = 0.05

#: The four lists every gap falls into, and the rule that puts it there. Both tests
#: are measurements made before the list existed: `affects` off the metric definition,
#: the verdict off document spread. The fourth list is the one that matters most for
#: honesty -- it holds the rows the two tests could not decide, instead of pushing
#: them into `drop` where "we cannot tell" would read as "we decided against".
TRIAGE = (
    ("keep_score", "保留 · 能提分",
     "在这批页面上出现够多次，而且能改变四步判定的某一步。做完 ParseBench 的分数会动。"),
    ("keep_diversity", "保留 · 只提升真实性与视觉多样性",
     "度量看不见它，但真实的图普遍这么画。做完分数一格不动，"
     "生成的图会更像真实报告页——这是数据集本身的价值，不是刷分。"),
    ("undecided", "待定 · 数字没能决定",
     "两个原因之一：页数太少，文档分布读不出来；或者分布正好压在分界线上（0.40–0.50）。"
     "**这一档程序不替你决定**——看图，然后把决定写进 README 的 TODO。"),
    ("drop", "舍弃",
     "度量看不见它，而且它明确集中在少数几份文档里（分布 < 0.40）——"
     "那是某家出版方的排版习惯，不是通用画法。记录下来，不为它改条件表。"),
)


def triage(pages: list[PageResult]) -> dict[str, list[tuple]]:
    """Sort every gap into keep-for-score / keep-for-diversity / undecided / drop.

    Measured tests, applied in order, so each gap lands in exactly one list and none
    is left out.

    Too few pages comes first, and it is the whole reason the fourth list exists.
    `error_bars` on two pages is not "one publisher's habit" -- it is "this sample
    cannot tell", and the two were reading as the same verdict. Then `affects`: a
    component the four steps never look at cannot move the score whatever its
    frequency. Then document spread, with a band around the cut held back as
    undecided, because 0.44 and 0.45 landing in different lists is the threshold
    talking rather than the data.

    The rule is printed beside the lists wherever they are rendered: a list a reader
    cannot re-derive is an opinion wearing a table's clothes.
    """
    seen = component_pages(pages)
    docs = component_documents(pages)
    corpus = len({p.document for p in pages})
    out: dict[str, list[tuple]] = {name: [] for name, _, _ in TRIAGE}
    for component in sorted((c for c in VOCABULARY if not c.ours), key=lambda c: -seen[c.key]):
        count = seen[component.key]
        verdict, detail = generality(count, docs.get(component.key, Counter()), corpus)
        spread = len(docs.get(component.key, ())) / max(min(count, corpus), 1)
        if count < GENERALITY_FLOOR:
            bucket, why = "undecided", "页数太少"
        elif component.affects:
            bucket, why = "keep_score", ""
        elif abs(spread - 0.45) < BORDERLINE:
            bucket, why = "undecided", f"分布 {spread:.2f}，压在分界线上"
        elif verdict in ("通用", "常见"):
            bucket, why = "keep_diversity", ""
        else:
            bucket, why = "drop", ""
        gap = _GAP_IN_BASIS.search(component.basis)
        out[bucket].append((component, count, verdict, detail,
                            gap.group(0) if gap else "—", why))
    return out


def pick_examples(pages: list[PageResult], keys: list[str],
                  limit: int = 3) -> dict[str, list[PageResult]]:
    """One example page per key, chosen for evidence and spread across pages.

    Three things decide, in order. A page that has already been made the lead
    example for another key steps aside, so one simple page does not become the
    illustration for a dozen unrelated components. Then the evidence the model
    wrote for *this* key, credited up to `EVIDENCE_CREDIT` characters -- a two-word
    one shows nothing, and past a sentence more length is only more words. Then the
    fewest figures, so the reader lands on a page where the component is easy to
    find.

    Keys are taken rarest first: a key with three candidate pages must choose
    before a key with eighty, or it is left with whatever is unclaimed.
    """
    used: Counter = Counter()
    out: dict[str, list[PageResult]] = {}
    hits = {k: [p for p in pages if k in keys_of(p.analysis)] for k in keys}
    for key in sorted(keys, key=lambda k: (len(hits[k]), k)):
        ranked = sorted(hits[key],
                        key=lambda p: (used[p.stem],
                                       -min(len(evidence_of(p.analysis, key)), EVIDENCE_CREDIT),
                                       len(countable_figures(p)), p.stem))
        out[key] = ranked[:limit]
        if ranked:
            used[ranked[0].stem] += 1
    return out


def new_component_examples(pages: list[PageResult], name: str, limit: int = 3) -> list[PageResult]:
    def named(page: PageResult) -> bool:
        return any(str(c.get("name", "")).strip() == name
                   for c in (page.analysis.get("new_components") or ()))
    return sorted((p for p in pages if named(p)),
                  key=lambda p: (len(countable_figures(p)), p.stem))[:limit]


def type_counts(pages: list[PageResult]) -> Counter:
    return Counter(str(f.get("type")) for p in pages for f in countable_figures(p))


def type_examples(pages: list[PageResult]) -> list[tuple[str, int, PageResult, dict]]:
    """One page per chart type, simplest first, with the figure that carries it."""
    out: list[tuple[str, int, PageResult, dict]] = []
    for name, count in type_counts(pages).most_common():
        for page in sorted(pages, key=lambda p: (len(countable_figures(p)), p.stem)):
            match = next((f for f in countable_figures(page) if str(f.get("type")) == name), None)
            if match:
                out.append((name, count, page, match))
                break
    return out


def new_types(pages: list[PageResult]) -> Counter:
    """The names the model gave the figures no listed type fits."""
    return Counter(str(f.get("type_other", "")).strip().lower()
                   for p in pages for f in countable_figures(p)
                   if str(f.get("type")) == "other" and str(f.get("type_other", "")).strip())


#: How the `other` names sort, for display only. Two of the three buckets are not
#: chart families at all -- a table we already draw, and an entry that is not a
#: figure -- and listing all three together makes the residue look larger than the
#: number of forms actually missing from the condition table.
_TYPE_BUCKETS = (
    ("表格", ("table", "list", "grid", "tile"),
     "带表头的表格与列表。`data_table_as_figure` 已经是我们有的能力，不是缺口"),
    ("不是图", ("placeholder", "body text", "note line", "none", "duplicate", "ignore",
                "not a figure", "no figure", "not a chart"),
     "占位、正文块、重复条目。这些本该进 `unreadable`，落到这里说明那个字段还漏"),
    ("图形", (), "条件表里没有的画法。**只有这一栏是真的类型缺口**"),
)


def bucketed_types(forms: Counter) -> list[tuple[str, str, list[tuple[str, int]]]]:
    """The `other` names, split into table / not-a-figure / an actual chart form."""
    out = []
    for title, words, blurb in _TYPE_BUCKETS:
        if words:
            members = [(n, c) for n, c in forms.most_common() if any(w in n for w in words)]
        else:
            claimed = {n for _, ws, _ in _TYPE_BUCKETS if ws
                       for n, _ in forms.most_common() if any(w in n for w in ws)}
            members = [(n, c) for n, c in forms.most_common() if n not in claimed]
        out.append((title, blurb, members))
    return out


def step_examples(pages: list[PageResult]) -> dict[int, PageResult]:
    """One page per blocking step, simplest first."""
    ordered = sorted(pages, key=lambda p: (len(countable_figures(p)), p.stem))
    return {step: next((p for p in ordered if p.analysis.get("hardest_step") == step), None)
            for step in (1, 2, 3, 4)}


def new_components(pages: list[PageResult]) -> tuple[Counter, dict[str, str]]:
    """Every name the model coined, with the first explanation given for each."""
    counts: Counter = Counter()
    why: dict[str, str] = {}
    for page in pages:
        for component in page.analysis.get("new_components") or ():
            name = str(component.get("name", "")).strip()
            if name:
                counts[name] += 1
                why.setdefault(name, str(component.get("why_it_matters", "")))
    return counts, why


def suggestion_generality(pages: list[PageResult]) -> dict[str, Counter]:
    """The model's own verdict on how general each gap item is, by P number."""
    out: dict[str, Counter] = defaultdict(Counter)
    for page in pages:
        for s in page.analysis.get("suggestions") or ():
            out[str(s.get("maps_to"))][str(s.get("generality"))] += 1
    return out


def headings(pages: list[PageResult]) -> Counter:
    """Where the heading block sits, over every countable figure."""
    return Counter(str((f.get("heading") or {}).get("placement", "none"))
                   for p in pages for f in countable_figures(p))


def addressing_score(pages: list[PageResult]) -> tuple[int, int]:
    """How many placed values the model predicted the right addressing keys for.

    The model was given each value and never its labels, so this is the one number
    in the run that grades a prediction instead of counting a report. A value
    counts as right when every label the rule uses is covered by a predicted key.
    """
    right = total = 0
    for page in pages:
        checks = page.analysis.get("spot_checks") or []
        for rule, check in zip(page.rules, checks):
            if str(check.get("figure_id")) == "not_found":
                continue
            total += 1
            right += keys_agree(list(check.get("addressing_keys") or ()), rule.labels)
    return right, total


def band(count: int, total: int) -> str:
    if count >= total / 2:
        return "高"
    return "低" if count <= total / 12 else "中"


def _link(page: PageResult) -> str:
    """A markdown link to one page's report.

    Parentheses are percent-encoded: a stem like `(Web_version)_…` would otherwise
    close the link target at its first `)` and leave the rest as loose text.
    """
    href = page.stem.replace("(", "%28").replace(")", "%29")
    return f"[{page.stem}](pages/{href}/report.md)"


# --------------------------------------------------------------------- sections
#
# Three of them, and the boundary between them is a question, not a topic:
#   1 什么要改   -- only things we cannot draw. Components, chart types, heading
#                  dimensions all sit here together, because "which of these do we
#                  build" is one question however the thing is classified.
#   2 基准长什么样 -- description. What the corpus contains, whether or not we can
#                  draw it. Nothing here is a to-do.
#   3 能不能信   -- how the run was made, what graded it, and every page.
# A chart type appears in 1 when we cannot draw it and in 2 as part of the mix;
# those are different questions about the same object, not the same table twice.

def _intro(pages: list[PageResult], model: str) -> list[str]:
    total = len(pages)
    figures = [f for p in pages for f in countable_figures(p)]
    return [
        "# ParseBench 样例分析", "",
        f"**{total} 页均匀随机抽样** · {len({p.document for p in pages})} 份文档 · "
        f"{sum(len(p.rules) for p in pages)} 条抽查点 · {len(figures)} 张图 · 模型 `{model}`。"
        f"配图版：**[view.html](view.html)**，三个分区与本文一一对应，每一项配一页实例"
        f"与模型写下的证据原文。逐页报告在 [pages/](pages/)。", "",
        "三节，各答一个问题，互不重复：", "",
        "| 节 | 问题 | 里面是什么 |", "|---|---|---|",
        "| **1 要改什么** | 我们画不出来的东西，哪些保留、哪些舍弃 | 四份清单 + 组件缺口、类型缺口、标题维度缺口，"
        "同一张排序表 |",
        "| **2 基准长什么样** | 这批页面实际是什么样 | 类型配比、标题形态、数值写不写、"
        "难点分布、词表全表。**这一节没有待办** |",
        "| **3 能不能信** | 这些数字是怎么来的 | 调用方式、判分、交叉核对、逐页 |", "",
        "**两条独立的轴，贯穿全文。**一个组件可以出现在四分之三的页面上，而基准根本看不见它——"
        "「单位写在轴标题里」出现在 149 / 192 页，而 4,864 条规则里**没有一条**的值或标签引用"
        "过那个单位。所以每一行都带两列：", "",
        "- **影响得分**：它能改变[四步判定](../review/02_chart_metric.md)的哪一步，空就是"
        "**基准看不见它**。和「我们有没有」一样，看任何一页之前就按度量定义定死。",
        "- **通用度**：文档分布。同一份文档里出现 20 次是那家出版方的习惯，20 份文档里各一次"
        "才是通用惯例。", "",
        "两列合起来就是 §1.1 的四份清单：**能提分** · **只提升真实性与视觉多样性** · "
        "**待定**（数字没能决定：页数太少，或分布压在分界线上）· **舍弃**。", "",
        f"**频次按档位读，不按名次**（n = {total}，真实频次 10% 的 95% 置信区间约 ±6 个百分点）："
        f"高 ≥ {total // 2} 页 · 中 {total // 12 + 1}–{total // 2 - 1} · 低 ≤ {total // 12}。", "",
        "---", "",
    ]


def _section_build(pages: list[PageResult]) -> list[str]:
    """Section 1: everything we cannot draw, in one place."""
    total = len(pages)
    seen = component_pages(pages)
    docs = component_documents(pages)
    corpus = len({p.document for p in pages})
    missing = [c for c in VOCABULARY if not c.ours]
    picked = pick_examples(pages, [c.key for c in missing], 1)
    types = type_counts(pages)
    figures = sum(types.values())
    lists = triage(pages)

    out = ["## 1 · 要改什么", "",
           "**基准里出现、而 `storyline/parsebench_chart/` 没有定义的东西，全在这一节。**"
           "不分组件还是图表类型——「这个我们建不建」是同一个问题。", "",
           f"### 1.1 四份清单 · {len(missing)} 项缺口各归其一", "",
           "依次问三个已测的问题，所以每一项**恰好落在一份清单里**，没有重叠也没有遗漏：", "",
           f"1. **页数够读出文档分布吗？**（≥ {GENERALITY_FLOOR} 页）不够 → 第三份「待定」。",
           "2. **它能改变四步判定的某一步吗？**（`affects`，按度量定义定死）能 → 第一份。",
           "3. **它是通用画法吗？**（文档分布）是 → 第二份；压在分界线上 → 第三份；"
           "明确不是 → 第四份。", "",
           "第一份和第二份**之间没有汇率**，硬排成一列就得凭空发明一个换算率。", "",
           "| 清单 | 项数 | 判据 | 怎么处理 |", "|---|---|---|---|"]
    TEST = {"keep_score": f"页数 ≥ {GENERALITY_FLOOR} · `affects` 非空",
            "keep_diversity": f"页数 ≥ {GENERALITY_FLOOR} · `affects` 为空 · 分布 ≥ 0.50",
            "undecided": f"页数 < {GENERALITY_FLOOR}，或分布落在 0.40–0.50",
            "drop": "`affects` 为空 · 分布 < 0.40"}
    for name, title, blurb in TRIAGE:
        out.append(f"| **{title}** | {len(lists[name])} | {TEST[name]} | {blurb} |")
    out += ["", "**第三份清单是这套分类里最要紧的一格。**「读不出来」和「判定不要」是两回事，"
                "混在一起，`error_bars` 只出现 2 页就会被写成「某家出版方的习惯」。"
                "通用度那一列印的是比值本身（实际覆盖的文档数 / 这些页最多能覆盖的文档数），"
                "0.70 以上通用、0.45 以上常见；落在 0.40–0.50 的一律不判，"
                "因为 0.44 与 0.45 分到不同清单是**阈值在说话，不是数据在说话**。"]
    for name, title, blurb in TRIAGE:
        rows = lists[name]
        out += ["", f"**{title} · {len(rows)} 项**", "", blurb, "",
                "| # | key | 组件 | 页数 | 影响哪一步 | 通用度 | 归入 |",
                "|---|---|---|---|---|---|---|"]
        for i, (component, count, verdict, detail, gap, why) in enumerate(rows, 1):
            out.append(f"| {i} | `{component.key}` | {component.name_zh} "
                       f"| {count}（{count / total:.0%}）| {affects_zh(component.affects)} "
                       f"| {verdict}（{detail}）{f'　**{why}**' if why else ''} | {gap} |")
        if not rows:
            out.append("| — | | 空 | | | | |")

    out += ["", f"### 1.2 组件缺口全表 · {len(missing)} 项", "",
            "| 档 | key | 组件 | 页数 | 影响哪一步 | 通用度 | 我们为什么画不出来 | 实例与证据 |",
            "|---|---|---|---|---|---|---|---|"]
    for component in sorted(missing, key=lambda c: (-seen[c.key], c.key)):
        count = seen[component.key]
        sample = picked.get(component.key) or []
        verdict, detail = generality(count, docs.get(component.key, Counter()), corpus)
        example = "—"
        if sample:
            proof = cell(evidence_of(sample[0].analysis, component.key)).replace("`", "")
            example = f"{_link(sample[0])}<br>`{proof}`" if proof else _link(sample[0])
        out.append(f"| {band(count, total) if count else '—'} | `{component.key}` "
                   f"| {component.name_zh} | {count}（{count / total:.0%}）"
                   f"| {affects_zh(component.affects)} | {verdict} | {component.basis} "
                   f"| {example} |")

    ours_types = {t for t, (yes, _) in CHART_TYPE_OURS.items() if yes}
    absent = sorted(t for t in ours_types if not types.get(t))
    forms = new_types(pages)
    buckets = bucketed_types(forms)
    out += ["", "### 1.3 类型缺口", "",
            "同一个问题问图表类型：条件表里有没有这一族。**类型配比本身不在这里**——"
            "那是描述，在 §2。", "",
            "| 类型 | 图数 | 占比 | 依据 |", "|---|---|---|---|"]
    for name, count in types.most_common():
        can, basis = CHART_TYPE_OURS.get(name, (False, "不在条件表里"))
        if not can:
            out.append(f"| `{name}` | {count} | {count / max(figures, 1):.0%} | {basis} |")
    real = next(m for t, _, m in buckets if t == "图形")
    out += ["", f"`other` 这一格要拆开看。模型必须给它命名，命名之后分成三堆，"
                f"**只有第三堆是真的类型缺口**：", "",
            "| 分类 | 图数 | 是缺口吗 |", "|---|---|---|"]
    for title, blurb, members in buckets:
        out.append(f"| **{title}** | {sum(c for _, c in members)} | {blurb} |")
    out += ["", "**真正是新画法的：**"
            + ("、".join(f"`{cell(n)}`×{c}" if c > 1 else f"`{cell(n)}`" for n, c in real)
               if real else "无") + "。", "",
            f"反过来，条件表里有、这份抽样里一张都没出现的 {len(absent)} 种："
            + "、".join(f"`{t}`" for t in absent)
            + "。**这不是「白做」**——它们是为别的目标基准留的能力，"
              "只说明按 ParseBench 调权重时不该给它们配额（见 P4）。", ""]

    where = headings(pages)
    numbered, multiline, united, figs = 0, 0, 0, 0
    for page in pages:
        for figure in countable_figures(page):
            head = figure.get("heading") or {}
            figs += 1
            numbered += bool(str(head.get("figure_number", "")).strip())
            multiline += bool(str(head.get("subtitle", "")).strip())
            united += bool(str(head.get("unit_text", "")).strip())
    out += ["### 1.4 标题维度缺口", "",
            "**图题不是一个组件，是一个有五个字段的对象**：图号 / 主标题 / 副标题 / 单位 / 位置。"
            "词表里原来有四个 key 在重复记录同样的事（而且是按页记，不是按图记），已经删掉——"
            "现在每张图都直接记这五个字段，缺口按维度读：", "",
            "| 维度 | 实测 | 我们现在 | 归入 |", "|---|---|---|---|",
            f"| 图号 | {numbered} / {figs} 张图有（{numbered / max(figs, 1):.0%}）"
            "| FigureSpec 没有 `title` 字段，图号无处可编 | P7 |",
            f"| 副标题（标题不止一行） | {multiline} / {figs}（{multiline / max(figs, 1):.0%}）"
            "| 同上 | P7 |",
            f"| 单位写在标题里 | {united} / {figs}（{united / max(figs, 1):.0%}）"
            "| unit 在 measure 声明里，一个字都不画出来 | P6 / P7 |",
            "| 位置 | " + " · ".join(f"{PLACEMENT_ZH.get(k, k)} {v}" for k, v in where.most_common())
            + " | `03 §0` 图注固定在图下方 | P7 |", "",
            "**位置这一维是四值不是两值**：`2023-05-sigma-01-english_p23` 的 Figure 15 把图号、"
            "标题、副标题三行排在**左栏**、与绘图区并排。对第四步的上下文回退来说，侧栏标题在 "
            "markdown 里落在哪一段完全取决于解析器怎么切版面块。", "",
            "**注意**：这一节整体属于上面 1.1 的 B 半——图号出现在 54% 的图上，而 4,864 条规则里"
            "只有 14 条（0.14%）把图号当作定位标签。标题主要是**真实性**问题，不是**分数**问题。", ""]
    return out


def _section_portrait(pages: list[PageResult]) -> list[str]:
    """Section 2: what the corpus looks like. Nothing here is a to-do."""
    total = len(pages)
    seen = component_pages(pages)
    docs = component_documents(pages)
    corpus = len({p.document for p in pages})
    types = type_counts(pages)
    figures = [f for p in pages for f in countable_figures(p)]
    type_pages = {t: len({p.stem for p in pages
                          for f in countable_figures(p) if str(f.get("type")) == t})
                  for t in types}
    horizontal = sum(f.get("orientation") == "horizontal" for f in figures)
    printed = Counter(f.get("values_printed") for f in figures)
    excluded = sum(len(p.analysis.get("figures") or []) - len(countable_figures(p)) for p in pages)
    tags = sorted({p.tags for p in pages})
    arity = Counter(r.arity for p in pages for r in p.rules)
    checks = [c for p in pages for c in (p.analysis.get("spot_checks") or ())]
    placed = [c for c in checks if str(c.get("figure_id")) != "not_found"]
    predicted = Counter(len(c.get("addressing_keys") or ()) for c in placed)
    on_figure = sum(bool(c.get("printed_on_figure")) for c in placed)

    out = ["## 2 · 基准长什么样", "",
           "描述，不是待办。**我们画得出来的东西也在这一节**——「已经能画，而且基准上很常见」"
           "说明现有能力对得上，那不是缺口。", "",
           "### 2.1 词表、组件、类型是什么关系", "",
           "一张图 = **一个类型** + **若干个组件**。", "",
           "| | 是什么 | 一张图有几个 | 例子 |", "|---|---|---|---|",
           "| **类型** | 这张图的画法 | **恰好 1 个**（19 选 1，必填） | `bar` `line` `pie` "
           "`heatmap` `waterfall` |",
           f"| **组件** | 图上 / 页上还有哪些构造 | **0 到十几个**（{len(VOCABULARY)} 选 N） "
           "| 「有参考线」「有负值」「图例在下方」「刻度比数据点稀」 |",
           "| **词表** | 组件的那份**固定清单** | — | 就是这 "
           f"{len(VOCABULARY)} 个 key 本身 |", "",
           "打个比方：**类型是名词**（这是一辆车），**组件是形容词**（四门、天窗、手动挡）。"
           "一辆车只能是一种车，但可以同时有很多个形容词。", "",
           "**为什么词表要固定**：模型报组件时那个字段是 enum，只能从这 "
           f"{len(VOCABULARY)} 个里选，**且每选一个必须写出证据**（页面上的原话，或者画了什么、"
           f"画在哪）。固定是为了让 {total} 页的答案能相加——「有参考线」「画了条虚线基准」"
           "「reference line」如果各写各的，就数不出「参考线出现在 41 页」这句话。"
           "选不出来的写进**新组件**自拟名字（§3），一个自拟名字出现 ≥3 页就**并入词表**，"
           "下一轮起有自己的计数。", "",
           "**两者问同一个问题：我们画不画得出来。** 类型层面 `map` 画不出来（条件表没有地理"
           "投影这一族）；组件层面 `reference_line` 画不出来（参考线不是任何族的图元）。"
           "所以两者都在 §1，不因为分类不同就分两张表。", "",
           "**图题不在词表里**——它是每张图上记录的五个字段（图号 / 主标题 / 副标题 / 单位 / "
           "位置），见 §1.4。", "",
           "### 2.2 类型配比", "",
           "[P4](../review/04_pipeline_gap.md) 的权重向量要的就是这张表。"
           "画不出来的那几种在 §1.3 排过序了，这里只讲基准是什么样。", "",
           "| 类型 | 图数 | 页数 | 我们能画吗 |", "|---|---|---|---|"]
    out += [f"| `{name}` | {count} | {type_pages[name]} "
            f"| {'有' if CHART_TYPE_OURS.get(name, (False, ''))[0] else '**无**'} |"
            for name, count in types.most_common()]
    out += ["", f"共 {len(figures)} 张图，横向 {horizontal} 张"
                f"（{horizontal / max(len(figures), 1):.0%}，`chart_types.md` 没有方向这一维）；"
                f"数值写出："
            + "、".join(f"{PRINTED_ZH.get(k, k)} {v}" for k, v in printed.most_common()) + "。"
            + (f"另有 {excluded} 个条目被模型自己写进 `unreadable`（装饰色块、注释文字块、占位），"
               "不是图形，不计入。" if excluded else ""), "",
            "### 2.3 难在哪", "",
            "每页卡在[四步判定](../review/02_chart_metric.md)的哪一步。"
            "**这是模型的判断，属于待失败案例确认的假设，不是测量。**", "",
            "| 卡在哪一步 | " + " | ".join(f"`{t}`" for t in tags) + " | 合计 |",
            "|---" * (len(tags) + 2) + "|"]
    for step in (1, 2, 3, 4):
        row = [sum(p.analysis.get("hardest_step") == step and p.tags == tag for p in pages)
               for tag in tags]
        out.append(f"| {STEP_ZH[step]} | " + " | ".join(str(v) for v in row) + f" | {sum(row)} |")
    out += ["", "**定位一个值要几个键**——左边是规则实际用了几个标签（事实），右边是模型只看图"
                "预测要几个（预测，判分见 §3）。两列差得越远，说明「凭图猜寻址」越不可靠：", "",
            "| 键数 | 规则实际 | 模型预测 |", "|---|---|---|"]
    for n in sorted(set(arity) | set(predicted)):
        out.append(f"| {n} | {arity.get(n, 0)} | {predicted.get(n, 0)} |")
    out += ["", f"**规则有 {arity.get(2, 0)} 条只用两个标签"
                f"（{arity.get(2, 0) / max(sum(arity.values()), 1):.0%}）**——行头加列头，"
                f"markdown 表刚好装得下。真正需要第三个键的只有 {arity.get(3, 0)} 条，"
                f"那才是第三步的难处。落位的 {len(placed)} 个值里 {on_figure} 个"
                f"（{on_figure / max(len(placed), 1):.0%}）数字直接印在图上，其余要对着轴读。", "",
            "**这一条不要反过来改我们的记录。** ParseBench 只需要两个键，"
            "不代表我们记两个键就够——生成侧的输出单位是 `(键, 值, 区域)`，"
            "**键必须是完整的寻址元组**（面板 × 系列 × 类目），因为 provenance 与 bbox "
            "这类目标要求每个图元都能被唯一指到。把键结构裁到基准的最低要求，"
            "等于为了一个基准砍掉这份数据集自己的产物。这正是 "
            "[P2](../review/04_pipeline_gap.md) 要把面板维加进键的理由。", "",
            f"### 2.4 词表全表 · {len(VOCABULARY)} 项", "",
            "五组，每组按页数排。「影响哪一步」与「我们」两列都在看任何一页之前就定死了。", "",
            "| 组 | key | 组件 | 页数 | 文档 | 影响哪一步 | 我们 |",
            "|---|---|---|---|---|---|---|"]
    order = {c.key: i for i, c in enumerate(VOCABULARY)}
    for group, title in GROUP_TITLES.items():
        members = sorted((c for c in VOCABULARY if c.group == group), key=lambda c: -seen[c.key])
        for i, component in enumerate(members):
            out.append(f"| {title if i == 0 else ''} | `{component.key}` | {component.name_zh} "
                       f"| {seen[component.key]} | {len(docs.get(component.key, ()))} "
                       f"| {affects_zh(component.affects)} "
                       f"| {'有' if component.ours else '**无**'} |")
    out.append("")
    return out


def _section_trust(pages: list[PageResult]) -> list[str]:
    """Section 3: how the run was made, what graded it, and every page."""
    total = len(pages)
    findings = Counter(f.code for p in pages for f in p.findings)
    unreadable_pages = sum(bool(p.analysis.get("unreadable")) for p in pages)
    right, graded = addressing_score(pages)
    bare = sum(1 for p in pages for c in components_of(p.analysis)
               if len(str(c.get("evidence", ""))) < 8)
    counts, why = new_components(pages)
    repeated = [(n, c) for n, c in counts.most_common() if c >= 2]
    once = [n for n, c in sorted(counts.items()) if c == 1]
    forms = new_types(pages)
    suggestions = Counter(str(s.get("maps_to")) for p in pages
                          for s in (p.analysis.get("suggestions") or []))
    by_gap = suggestion_generality(pages)

    out = ["## 3 · 这些数字能不能信", "",
           "### 3.1 怎么跑的", "",
           "整页 PNG 150 dpi，一页一次结构化调用，effort `high`，`max_tokens` 12000，"
           "不发 temperature / top_p。不裁剪、不接 OCR、不做 agent、不做第二轮。"
           "设计见 [review/05](../review/05_analysis_design.md)。", "",
           "| 模型看得到 | 模型看不到 |", "|---|---|",
           "| 整页图像 | 抽查点的**标签** |",
           f"| {len(VOCABULARY)} 项组件词表（key + 英文判据） | 词表的「我们有没有」那一列 |",
           "| 这一页抽查点的**数值** | 「影响哪一步」那一列 |",
           "| P1–P7 的一行描述（意见要归类） | 流水线的结构、条件表、`(键, 值, 区域)` |", "",
           "### 3.2 判分：一个真正被打了分的预测", "",
           f"值给了模型、标签没给，所以模型说的「要哪些键才能定位」是**预测**，规则来判分："
           f"一个值算对，要求规则用的每个标签都被预测到的某个键覆盖（双向子串，与基准自己的"
           f"匹配方式一致）。**{graded} 个落位的值里对了 {right} 个"
           f"（{right / max(graded, 1):.0%}）。**", "",
           "这个数同时受两件事影响，报出来是为了可追查，不是当作模型能力的度量：一是模型确实"
           "读错了行或列（`2023-05-sigma-01-english_p23` 那张指数图 10 个值错了 7 个，两条线"
           "终点相差不足 2 px）；二是同一个格子在页面上常有不止一种叫法。**逐条可查**——"
           "每页 `report.md` 第 2 节把规则的标签与模型的预测并排放在同一行。", "",
           "### 3.3 交叉核对", "",
           f"{total} 页共出 {sum(findings.values())} 条矛盾。", "",
           "| 矛盾 | 页数 |", "|---|---|"]
    out += [f"| {FINDING_ZH.get(code, code)} | {count} |" for code, count in findings.most_common()]
    if not findings:
        out.append("| — | 0 |")
    out += ["", f"**证据**：每个组件都要带证据，没写出证据的共 {bare} 条。"
                f"**`unreadable`** 非空 {unreadable_pages} / {total} 页——要逐条读，"
                "「这张图看不清」与「这个条目根本不是图」是两回事。", "",
            "**意见归属**：schema 强制每条写全「加什么 / 改哪里 / 新增哪一行消融 / 通用度」，"
            "凑不出消融行的写不出来。模型自己判的通用度是**独立于文档分布的第二个估计**：", "",
            "| 归入 | 条数 | 通用 | 一类出版方 | 这份文档自己的习惯 |", "|---|---|---|---|---|"]
    for gap, count in suggestions.most_common():
        c = by_gap.get(gap, Counter())
        out.append(f"| {gap} | {count} | {c.get('general', 0)} | {c.get('common', 0)} "
                   f"| {c.get('house_style', 0)} |")

    out += ["", "### 3.4 词表本身还缺什么", "",
            f"词表装不下的，模型自拟名字写进 `new_components`，同样要带证据——"
            f"这一轮出现 {len(counts)} 个名字。**这是词表完整性的度量**：残差越干净，"
            f"说明词表越接近覆盖。出现 ≥3 页的下一轮并入。", "",
            "| 名字 | 页数 | 并表 | 说明 | 实例 |", "|---|---|---|---|---|"]
    for name, count in repeated:
        sample = new_component_examples(pages, name, 1)
        out.append(f"| `{cell(name)}` | {count} | {'✓' if count >= 3 else ''} "
                   f"| {cell(why[name])} | {_link(sample[0]) if sample else '—'} |")
    if not repeated:
        out.append("| — | 0 | | 没有一个名字出现在两页以上 | — |")
    if once:
        out += ["", f"<details><summary>只出现在 1 页的 {len(once)} 个</summary>", "",
                " · ".join(f"`{cell(n)}`" for n in once), "", "</details>"]
    out += ["", f"类型这一侧同样：{sum(forms.values())} 张图报了 `other` 并自己命名，"
                "分类见 §1.3。", "",
            "### 3.5 一页报告怎么读", "",
            "`pages/<stem>/` 三个文件：`report.md` 给人读，`analysis.json` 给汇总用，"
            "`page.png` 是指向 `data/pages/` 的链接。`report.md` 六节：", "",
            "| 节 | 内容 |", "|---|---|",
            "| 1 样本 | 来源文档、标签组、抽查点数与其中估读数 |",
            "| 2 抽查点与模型的定位 | 左半是规则（值 + 标签 + 容差），右半是模型只看图给的定位。"
            "**模型只拿到了左半的值** |",
            "| 3 图表分解 | 每张图：类型、方向、面板 / 系列 / 类目数、图元总数、值轴刻度原文，"
            "以及拆成五项的标题 |",
            "| 4 组件清单 | 本页出现的项，每项带模型写的证据；「我们」一列从词表照抄 |",
            "| 5 难在哪 | 卡在四步的哪一步，用本页的数字论证 |",
            "| 6 意见 | 加什么 / 改哪里 / 新增哪一行消融 / 通用度，归入 P1–P7 |", "",
            "schema 在 [`tools/analysis/schema.py`](../tools/analysis/schema.py)，"
            "词表的唯一定义处在 [`tools/analysis/vocabulary.py`](../tools/analysis/vocabulary.py)。",
            ""]
    return out


def render_index(pages: list[PageResult], model: str) -> str:
    out = (_intro(pages, model) + _section_build(pages) + _section_portrait(pages)
           + _section_trust(pages))
    return "\n".join(out) + "\n"


def summary_json(pages: list[PageResult], model: str) -> dict:
    """The index as data, so the reverse difference can subtract two of these."""
    seen = component_pages(pages)
    docs = component_documents(pages)
    counts, _ = new_components(pages)
    checks = [c for p in pages for c in (p.analysis.get("spot_checks") or ())]
    return {
        "model": model,
        "pages": len(pages),
        "documents": len({p.document for p in pages}),
        "rules": sum(len(p.rules) for p in pages),
        "figures": sum(len(countable_figures(p)) for p in pages),
        "component_pages": {c.key: seen[c.key] for c in VOCABULARY},
        "component_share": {c.key: round(seen[c.key] / len(pages), 4) for c in VOCABULARY},
        "component_documents": {c.key: len(docs.get(c.key, ())) for c in VOCABULARY},
        "component_generality": {
            c.key: generality(seen[c.key], docs.get(c.key, Counter()),
                              len({p.document for p in pages}))[0] for c in VOCABULARY},
        "chart_types": dict(type_counts(pages)),
        "new_chart_types": dict(new_types(pages)),
        "heading_placement": dict(headings(pages)),
        "orientation": dict(Counter(f.get("orientation") for p in pages
                                    for f in countable_figures(p))),
        "values_printed": dict(Counter(f.get("values_printed") for p in pages
                                       for f in countable_figures(p))),
        "hardest_step": dict(Counter(p.analysis.get("hardest_step") for p in pages)),
        "hardest_step_by_tags": {
            tag: dict(Counter(p.analysis.get("hardest_step") for p in pages if p.tags == tag))
            for tag in sorted({p.tags for p in pages})},
        "spot_checks": {
            "answered": len(checks),
            "placed": sum(str(c.get("figure_id")) != "not_found" for c in checks),
            "printed_on_figure": sum(bool(c.get("printed_on_figure")) for c in checks),
            "addressing_key_counts": dict(Counter(len(c.get("addressing_keys") or ())
                                                  for c in checks)),
        },
        "addressing_score": dict(zip(("right", "graded"), addressing_score(pages))),
        "triage": {name: [c.key for c, *_ in rows] for name, rows in triage(pages).items()},
        "suggestion_generality": {g: dict(c) for g, c in suggestion_generality(pages).items()},
        "new_components": dict(counts),
        "crosscheck": dict(Counter(f.code for p in pages for f in p.findings)),
        "unreadable_pages": sum(bool(p.analysis.get("unreadable")) for p in pages),
    }
