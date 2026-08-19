"""The pages the report argues from, and the page-level file each one gets.

A frequency table says 599 points failed because a label would not associate. It
does not say what the parser wrote instead, and a failure form you cannot picture is
a form you cannot design against. Each case here is one page where a single
mechanism produced most of that page's zeros, with the page image, the rules, the
metric's own words, and the parser's table side by side.

The pages are pinned rather than picked by a rule. Every one of them was read
against its rendered page before its note was written, and the note says what is on
that page; a selector could rank pages by failure count but could not do that. The
count each note quotes is recomputed at render time, so a note that stops matching
the run shows up as a contradiction rather than as stale prose.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from stats import Analysis
from run import Run
from wording import KIND_ZH


@dataclass(frozen=True)
class Case:
    """One page, the form it demonstrates, and what it says about the pipeline."""

    stem: str
    kind: str
    title: str
    what_happened: str
    for_the_pipeline: str


CASES: tuple[Case, ...] = (
    Case(
        stem="pwc-semiconductor-and-beyond-2026-full-report_p17",
        kind="label_unlinked",
        title="**列名写成了颜色**：Gray / Orange，而图例上写的是 Conventional / AI-driven demand",
        what_happened=(
            "**十个数字一个不差，十个点全判 0。**\n"
            "图例在右上角，两个色块分别标着 `Conventional demand`（灰）与 "
            "`AI-driven demand`（橙）。解析器没有把色块和柱子对起来，"
            "列名直接写成了 `Gray` / `Orange`。"
            "规则要「`'19` 这一年的 `Conventional demand` 是多少」，"
            "而表里从头到尾没出现过 `Conventional demand` 这几个字。\n"
            "**还多出来一列。** 两根柱子之间那条浅橙色的连接带是装饰，不是数据，"
            "解析器把它当成第三个系列写成了 `Light orange band`。"),
        for_the_pipeline=(
            "**「哪个颜色是哪个系列」这件事，现在没有任何训练目标在教。**\n"
            "我们画图的时候，每个图元的颜色和它的系列名都是已知的，"
            "多导出一条「色块 → 系列名」的配对是纯加法，而现有 chart 数据集没有这项标注。\n"
            "顺带这一页也给「图里的装饰元素」定了价：一条不是数据的色带被当成数据列，"
            "代价是整页 0 分。"),
    ),
    Case(
        stem="Technopak_Industry_Report_p18",
        kind="label_unlinked",
        title="**三张饼拆成三张小表**，年份和类目名分别丢在不同的表里",
        what_happened=(
            "**六个数字全部写对，六个点全判 0。**\n"
            "页面上是同一个图号下的三张饼（2019 / 2024 / 2029P），"
            "年份写在每张饼的上方，`Branded Play` / `Unbranded Play` 的图例"
            "只画在中间那张饼下面。\n"
            "解析器照着版面输出了三张两列小表："
            "**2019 和 2029P 那两张只有数字，没有类目名；中间那张有类目名，没有年份。**"
            "每张表都少一个键，所以每个点都对不上。"),
        for_the_pipeline=(
            "**这就是 P2（面板名进键）要解决的情形。**"
            "面板名如果只是个 id、不作为键写出去，每张面板表都会少一个键。\n"
            "更值得注意的是：这一页的数值**全部印在图上**，读数根本没出错。"
            "读得准和写得对，在这个度量下是两件独立的事。"),
    ),
    Case(
        stem="Digital_News-Report_2022_p46",
        kind="label_unlinked",
        title="**值那一列的表头**写成了整段问卷题干，规则要的是 `Percentage`",
        what_happened=(
            "42 个国家的横向条形图，数字全部印在条末，解析器一行不差地抄进了一张 43 行的长表——"
            "**表的形状是对的**。\n"
            "问题在值那一列的表头：解析器写的是问卷原题 "
            "`Q10. Thinking about how you got news online…`，"
            "而规则的第二个键是 **`Percentage`**——标注者从百分数轴上取的测度名。\n"
            "国家名对上了，测度名对不上，四个点全判 0。"),
        for_the_pipeline=(
            "**值那一列的表头本身就是一个键。**\n"
            "它的名字应该来自测度声明（我们的 schema 里 measure 有名字有单位），"
            "而不是页面上离得最近的一句话。这也是 `unit_in_axis_or_title`"
            "（149 / 192 页，基准里最通用的组件）在判分侧的具体形态。"),
    ),
    Case(
        stem="ac8b3538-en_p62",
        kind="label_unlinked",
        title="**两条线的名字没进表**：图例被写成页顶一行普通文字，9 个失败点里 7 个卡在这里",
        what_happened=(
            "一页排了 15 个国家的小折线，每个面板一个国名，两条线（`Nominal minimum wage` / "
            "`Real minimum wage`），横轴 61 个半年刻度，**全页 1,830 个图元，一个数值都不写**。\n"
            "**结构其实选对了。** 一个面板一张表，行是时间、列是两条线，"
            "国名写成表前面的 `## **Japan**` 标题——判分程序就是靠这个标题认出 `Japan` 的，"
            "它的原话是 `title labels ['japan'] in context`。\n"
            "**挂在系列名上。** 图例那行 `Nominal minimum wage    Real minimum wage` "
            "被写成了页顶一行**普通正文**：既不在任何表头里"
            "（第一张表的表头写成了截断的 `Nomini`），也不是粗体或标题，"
            "所以表外回退那一步不认它。9 个失败点里 7 个的缺失键含这个系列名，"
            "其中 **4 个只缺这一个**。\n"
            "国名接错是次要的：`Japan` 那张表的表头写着 `Lithuania`、"
            "`Korea` 那张的第二列写着 `Luxembourg`，只影响 4 个点。\n"
            "唯一通过的那个点还是蒙对的——`**Real minimum wage**` 与 `Nominal minimum wage` "
            "的相似度 0.81，而回退只要 0.60，把「实际」当成「名义」放了过去。"),
        for_the_pipeline=(
            "**P2：系列名要能作为一个键导出去，不能只画在图例里。**\n"
            "我们记录层里系列名本来就是键的一维。这一页说明的是导出时它必须落进表头或标题，"
            "写成一行普通文字等于没写——这正好是可以拿来训的一条：图例上的名字，"
            "要跟着它那条线一起写进表。\n"
            "**P5：这一页我们一张也生成不出来。**"
            "`chart_types.md` 现在 line 的系列上限是 6、grouped_bar 的 |P|·|S| ≤ 24，"
            "画不到 1,830 个图元这一档。"),
    ),
    Case(
        stem="sri-sigma-natural-catastrophes-1-2025_p10",
        kind="value_off",
        title="**每根柱子都读低了正好半格**：1→0、4→3.5、8→7.5",
        what_happened=(
            "直方图的纵轴是「有多少年落在这个区间」，**只能是整数**。\n"
            "八个失败点，**每一个都正好比真值低 0.5**："
            "1→0 · 4→3.5 · 8→7.5 · 2→1.5 · 4→3.5 · 3→2.5 · 2→1.5 · 1→0.5。"
            "唯一通过的那个 5→4.5 也是同样的偏移，只是 10% 的容差刚好收住了它。\n"
            "**这不是噪声，是把柱顶读到了两条格线中间。**"),
        for_the_pipeline=(
            "**P1 还差一条：测度自己的取值域。**\n"
            "「这个图元能读到 ±3%」（可达精度 ε）描述不了「这个量只能取整数」。"
            "计数型测度四舍五入到整数，这八个点里有几个就能救回来。\n"
            "我们的 schema 里 measure 已经声明了类型，把它传进值目标与自检是零成本的，"
            "而现有工作没有这一项标注。"),
    ),
    Case(
        stem="World_Inequality_Report_2026_p79",
        kind="value_off",
        title="**表的形状完全正确**，4,000 个图元照样只对了一个点",
        what_happened=(
            "两个面板、9 条线、1800–2025，**4,000 个图元，一个数值都不写**。\n"
            "解析器这次把表写成了长表：`Year | Panel | 九个地区`——"
            "**面板维进了表，正是 P2 想要的形状**。\n"
            "十个点仍然只对了一个，剩下九个是数字本身落错了行或落错了列。"),
        for_the_pipeline=(
            "**这是唯一的反向证据：键写对了不等于能拿分。**\n"
            "长表导出能解决 599 个「键对不上」，解决不了稠密度。"
            "两件事要分开验收——P3 / P2 看键，P1 / P5 看这一档的读数。"),
    ),
    Case(
        stem="mts0625_p6",
        kind="row_missing",
        title="**一页两张图都叫 Receipts**，不写图号就分不清是哪一张",
        what_happened=(
            "页面上是 Figure 3（月度）和 Figure 4（累计），"
            "两张图的系列名一模一样：`Receipts` / `Outlays` / `Deficit(-)/Surplus`。\n"
            "所以规则用了**四个键**来定位一个值，第四个键就是 **`Figure 3.`**。\n"
            "解析器把两张图合并成了一张表，没有图号这一列，十个点全判 0。"),
        for_the_pipeline=(
            "**「一页多图」和「图号进键」是同一件事的两面。**\n"
            "只要一页上放两张系列名相同的图，图号就必须既画得出来、也导得进键。\n"
            "P7 原本的判断是「图号基本不影响分数」（4,864 条规则里只有 14 条拿图号当键）——"
            "这一页就是那 14 条里的一整页，结论不变，但它说明这条路是通的。"),
    ),
    Case(
        stem="VPEG6_SIV_Information_Memorandum__June_2025__p11",
        kind="row_missing",
        title="**系列名只画在图里当文字**，一个字都没进表",
        what_happened=(
            "两个系列 `VANTAGE` 和 `GLOBAL PRIVATE EQUITY`，"
            "在图上是绘图区里的两行文字标签，不是图例。\n"
            "解析器把它们原样抄成了表**外面**的两行普通正文，"
            "表头则自己起了名：`Quartile TVPI (x)` / `Vantage TVPI (x)`。\n"
            "**`GLOBAL PRIVATE EQUITY` 在整张表里一个字都没有**，四个点因此判 0；"
            "第五个点的值 2.1 只出现在一句加粗的句子里，表里根本没有。"),
        for_the_pipeline=(
            "**系列名画在哪里，决定了它会不会进表。**\n"
            "图例、线端文字、绘图区内标签——这三种画法现在不是风格向量的一维，"
            "而它们的后果完全不同。P6 的「标注形态」应该把系列名标签一起收进去。"),
    ),
    Case(
        stem="The_State_of_UK_Competition_Report_2024_p31",
        kind="unit_mismatch",
        title="**刻度写的是 `.4` 不是 `0.4`**，整张图读大了 10 倍",
        what_happened=(
            "横向系数点图（Stata 默认样式），系数轴的刻度标签是斜排的 "
            "`-.4  -.2  0  .2  .4  .6  .8  1`——**省掉了整数位的 0**。\n"
            "解析器写下 4.4 / 1.5 / −1.6 / −2.3，真值是 0.45 / 0.15 / −0.2 / −0.25："
            "**九个点整体差一个数量级，方向和相对大小全对。**"),
        for_the_pipeline=(
            "**刻度标签怎么写，直接决定读数的量级**，而风格向量里现在没有这一维。\n"
            "P6 的「刻度格式」要细到：省不省前导零、标签斜不斜、负号是 `-` 还是 `−`。\n"
            "另外这张图是横向系数点图（带误差棒），条件表里没有这一族。"),
    ),
    Case(
        stem="Activate_Consulting_Technology_&_Media_Outlook_2026_(10)_p60",
        kind="unit_mismatch",
        title="**图上写 $101B，规则要 101**，多写一个 B 就全错",
        what_happened=(
            "图题写着 `BILLIONS USD`，柱子上的标注写的是 `$101B`，而规则的值是 `101`。\n"
            "解析器照抄了柱子上的标注 `$101B`——**看起来完全忠实**，"
            "但判分程序把后缀 `B` 读成 ×10⁹，于是 101 和 101,000,000,000 对不上，八个点判 0。\n"
            "同一页两个 CAGR 百分点（16% / 10%）判对了，因为百分号不带量级。"),
        for_the_pipeline=(
            "**最通用的那个组件（单位只写在轴 / 图题里，149 / 192 页），"
            "造出来的失败恰恰是「解析器太老实」。**\n"
            "对我们的导出：格子里只写和轴刻度同尺度的裸数字，量纲写进表头或表前的标题。\n"
            "对训练数据：值和量纲必须是两个字段，不能拼成一个字符串。"),
    ),
)


def render_case(case: Case, run: Run, analysis: Analysis) -> str:
    """One case file: the page, its rules, and what the parser wrote."""
    verdicts = run.by_page()[case.stem]
    passed = sum(1 for v in verdicts if v.passed)
    lines = [f"# {case.stem}", "",
             f"**{case.title}** · {KIND_ZH[case.kind]} · "
             f"该页 {passed} / {len(verdicts)} 通过", "",
             "![page](page.png)", "",
             "## 这一页发生了什么", "", case.what_happened, "",
             "## 对流水线意味着什么", "", case.for_the_pipeline, "",
             "## 逐条抽查点", "",
             "| 判定 | 值 | 定位键 | 容差 | 归类 | 度量原话 |",
             "|---|---|---|---|---|---|"]
    for verdict in verdicts:
        diagnosis = analysis.diagnoses.get((verdict.rule.stem, verdict.rule.id))
        kind = "—" if verdict.passed else KIND_ZH.get(diagnosis.kind, diagnosis.kind)
        detail = ""
        if diagnosis and diagnosis.model_value is not None:
            detail = f"（表里是 {diagnosis.model_value:g}）"
        labels = " · ".join(f"`{label}`" for label in verdict.rule.labels)
        note = verdict.explanation.replace("|", "\\|")
        lines.append(f"| {'通过' if verdict.passed else '**不通过**'} | `{verdict.rule.value}` | "
                     f"{labels} | {verdict.rule.tolerance:g} | {kind}{detail} | "
                     f"{note[:160]} |")
    lines += ["", "## 解析器写下的整页 markdown", "", "```markdown",
              run.pages[case.stem].markdown[:4000], "```", ""]
    return "\n".join(lines)


def write_cases(out_dir: Path, run: Run, analysis: Analysis, pages_dir: Path) -> list[Case]:
    """A directory per case: the note, and a link to the page image."""
    written = []
    for case in CASES:
        if case.stem not in run.pages:
            continue
        directory = out_dir / case.stem
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "case.md").write_text(render_case(case, run, analysis),
                                           encoding="utf-8")
        link = directory / "page.png"
        source = pages_dir / f"{case.stem}.png"
        if link.is_symlink() or link.exists():
            link.unlink()
        if source.exists():
            link.symlink_to(os.path.relpath(source, directory))
        written.append(case)
    return written
