"""The written report: four sections, in the order the argument runs.

`1 失败长什么样` is the taxonomy over all 568 pages -- it needs only the parser's
output and the rule, so it takes the whole split. `2 什么样的图更容易失败` crosses
that with the 192 pages the page analysis described, so its denominator is smaller
and every row says so. `3 翻成流水线改动` is the only section with a to-do, and
every line in it carries the number from section 1 or 2 that priced it. `4 能不能信`
is the method, including the two failure forms this run could not separate.

The improvement list is written here rather than computed, because "what to build"
is a judgement; what is computed is the number beside each row, so a row whose
number stops matching the run reads as a contradiction inside one file.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

from cases import CASES
from stats import Analysis
from wording import (HOME_ORDER, HOME_ZH, KIND_NOTE, KIND_ORDER, KIND_ZH, POINTS_AT,
                     PRINTED_ZH)

#: The three reading forms are reported as one row: at this precision the two
#: neighbour-based ones cannot be told from an ordinary misread. See section 4.
READING_FORMS = ("value_off", "series_swap", "stack_confusion")


@dataclass(frozen=True)
class Improvement:
    """One change: what it means in plain words, the page that shows it, and its price."""

    name: str
    maps_to: str
    plain: str
    example: str
    price: str
    generality: str


#: `generality` answers one question only: would this change still be worth making
#: if ParseBench did not exist. `plain` has to be understandable without the spec.
IMPROVEMENTS: tuple[Improvement, ...] = (
    Improvement(
        "导出的时候，一行只放一个值，把它的所有键写在同一行", "P3",
        "现在把图转成表，习惯写成**宽表**——行是年份，列是系列，数字在交叉格里。"
        "判分程序查的是「这个数所在的**那一行、那一列、那个表头**里有没有出现这个键」，"
        "宽表一旦被拆开、或者表头写错，键就够不着了。"
        "改成**长表**：`年份 | 系列 | 值`，一行一条，键永远和值在同一行，"
        "怎么拆都拆不散。",
        "`Technopak_Industry_Report_p18` 三张饼拆成三张小表，年份和类目名分别丢；"
        "`pwc-…_p17` 列名写成了颜色。两页都是数字全对、全判 0。"
        "每张卡片右边那张绿色的表，就是长表长什么样。",
        "占全部失败的 {label_share}；其中 {home_share} 的键就在同一张表里，"
        "只是不在这个数的行 / 列 / 表头上",
        "通用"),
    Improvement(
        "多面板图，把面板名也当成一个键写出去", "P2",
        "小倍数图（一个图号下面并排好几张小图）里，「这是哪张小图」本身就是一个键。"
        "我们现在只给面板一个内部编号，导出的表里没有这一列，"
        "于是每张面板表都比规则少一个键。",
        "`Technopak_…_p18`（三张饼 = 三个面板名）· `ac8b3538-en_p62`（15 个国家面板，"
        "表头整体错位一格）。",
        "2 键 {k2} → 3 键 {k3} → 4 键 {k4}；3 键的点失败时 {a3} 是键对不上",
        "通用"),
    Improvement(
        "让模型学会「哪个颜色是哪个系列」", "新",
        "堆叠柱、多系列折线，系列名只写在图例的色块旁边。"
        "把色块和柱子对起来这件事，现在没有任何训练目标在教。"
        "我们画图时每个图元的颜色和系列名都是已知的，多导出一条配对是纯加法。",
        "`pwc-…_p17`：列名写成 `Gray` / `Orange`，十个数字一个不差，十个点全 0。",
        "图例离图越远越贵：`legend_beside_plot` {beside}、`shared_legend` {shared}"
        "（控制组内，95% 区间不重叠）",
        "通用"),
    Improvement(
        "能画更密的图", "P5",
        "`chart_types.md` 现在的上限是 grouped_bar 的 |面板|×|系列| ≤ 24、line 最多 6 条线，"
        "算下来全部落在「图元 ≤ 60」这一档——**也就是最容易的那一档**。"
        "基准里真正难的那些页在 400 图元以上，我们连一张都生成不出来。",
        "`ac8b3538-en_p62` 15 个面板 1,830 个图元；"
        "`World_Inequality_Report_2026_p79` 两个面板 4,000 个图元。",
        "≤20 图元 {d1} → >400 图元 {d5}，95% 区间不重叠",
        "通用"),
    Improvement(
        "记下每个图元能读到多准，还要记下这个量只能取整数", "P1",
        "现在 `readable` 只有能读 / 不能读两种。改成记一个数 ε——"
        "「这个图元在当前像素几何下能读到 ±3%」。"
        "但光有 ε 还不够：有些量**只能取整数**（比如「有多少年」），"
        "这条先验能直接把读数四舍五入回来。",
        "`sri-sigma-…_p10`：纵轴是年份个数，八个失败点每一个都正好低 0.5 格。"
        "四舍五入到整数就能救回其中几个。",
        "读错数的失败 {reading} 个，相对误差中位 {err_p50}，只有 {err_5} 落在 5% 以内",
        "通用"),
    Improvement(
        "刻度怎么写、单位写在哪，要能调", "P6",
        "刻度标签的写法直接决定读数的量级：`.4` 和 `0.4` 差十倍。"
        "单位写在图题里还是写在格子里，也决定了判分认不认。"
        "这一维现在完全不在风格向量里。",
        "`The_State_of_UK_Competition_…_p31`：刻度写 `.4`，整张图读大十倍；"
        "`Activate_…_p60`：图题写 BILLIONS、标注写 `$101B`，规则要 `101`。",
        "量级错的失败 {unit} 个，两种写法各有一整页的实例",
        "通用"),
    Improvement(
        "负值和零线", "P6",
        "三份规格都没写过零线：测度的值域能不能跨零、柱子能不能从零线往两边长。"
        "而基准里 399 条规则的值是负数。",
        "`05021ff2-en_p19` 右面板零线居中，柱子往左右两边长。",
        "负值的点通过率 {neg}，全体 {overall}（都按点算）；"
        "`negative_values` 在控制组内 {neg_comp}",
        "通用"),
    Improvement(
        "参考线、批注框、阴影带这些不是数据的东西", "新",
        "目标线、平均线、引线说明框、区间阴影——它们画在图里但不是任何一个数据点，"
        "`chart_types.md` 里没有这种形状。**它们不是装饰噪声，是会被当成数据的。**",
        "`pwc-…_p17` 把两根柱之间的浅橙色连接带当成了第三个数据系列。",
        "`annotation_callout` {callout}、`reference_line` {refline}"
        "（控制组内，95% 区间不重叠）",
        "通用"),
    Improvement(
        "图要有标题和图号", "P7",
        "94% 的真实图有标题、一半带 `Figure N`，而我们八张图里五张连标题文本的来源都没有。"
        "一页放两张图的时候，图号还会直接变成一个键。",
        "`mts0625_p6`：一页两张图的系列名完全相同（都是 Receipts / Outlays），"
        "规则只好用四个键，第四个键就是 `Figure 3.`。",
        "无标题的图 {h_none} vs 图上方 {h_above}——**这是相关不是因果**（见「能不能信」）",
        "通用，但这一行的数字不能当因果读"),
    Improvement(
        "页面文字量给个目标", "B3 第三项",
        "`03 §5 页面合成` 要求把图嵌进有正文的版面，但没给量。"
        "基准 568 页的整页文字量中位 355 词，94% 的页 ≥100 词。",
        "这一条这次**没有找到分数上的证据**：按文字量四分位分档，"
        "曲线是两端低中间高的非单调形状，查过的三个混淆项都解释不了它。",
        "{text_bands}——非单调，原因未定",
        "通用"),
)


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _rate(analysis: Analysis, table: str, key) -> str:
    entry = getattr(analysis, table).get(key)
    return f"{entry.value:.1%}" if entry else "—"


def _prices(analysis: Analysis, negative_rate: float) -> dict[str, str]:
    failures = sum(analysis.kinds.values()) or 1
    homes = sum(analysis.homes.values()) or 1
    reading = sum(analysis.kinds[kind] for kind in READING_FORMS)
    errors = analysis.errors
    within5 = sum(1 for error in errors if error <= 0.05) / len(errors) if errors else 0.0
    median = errors[len(errors) // 2] if errors else 0.0
    by_key = {entry.key: entry for entry in analysis.components}

    def delta(key: str) -> str:
        entry = by_key.get(key)
        return "—" if entry is None else f"{entry.delta:+.1%}（n={entry.present.total}）"

    arity3 = analysis.by_kind_arity.get(3, {})
    addressing3 = sum(count for kind, count in arity3.items()
                      if kind in ("label_unlinked", "row_missing"))
    return {
        "label_share": f"{analysis.kinds['label_unlinked'] / failures:.0%}",
        "home_share": f"{analysis.homes['in_a_table_but_not_addressing'] / homes:.0%}",
        "k2": _rate(analysis, "by_arity", 2), "k3": _rate(analysis, "by_arity", 3),
        "k4": _rate(analysis, "by_arity", 4),
        "a3": f"{addressing3 / max(sum(arity3.values()), 1):.0%}",
        "p1": _rate(analysis, "by_panels", "1 面板"),
        "p3": _rate(analysis, "by_panels", "3+ 面板"),
        "shared": delta("shared_legend"), "beside": delta("legend_beside_plot"),
        "d1": _rate(analysis, "by_density", "≤20"),
        "d5": _rate(analysis, "by_density", ">400"),
        "reading": str(reading), "err_p50": _pct(median), "err_5": _pct(within5),
        "unit": str(analysis.kinds["unit_mismatch"]),
        "neg": _pct(negative_rate), "overall": _pct(analysis.micro),
        "neg_comp": delta("negative_values"),
        "callout": delta("annotation_callout"), "refline": delta("reference_line"),
        "h_none": _rate(analysis, "by_placement", "none"),
        "h_above": _rate(analysis, "by_placement", "above"),
        "text_bands": " · ".join(f"{name} {entry.value:.1%}"
                                 for name, entry in analysis.by_text_band.items()) or "未测",
    }


def _section_forms(analysis: Analysis) -> list[str]:
    failures = sum(analysis.kinds.values())
    addressing = sum(analysis.kinds[kind] for kind in ("label_unlinked", "row_missing"))
    reading = sum(analysis.kinds[kind] for kind in READING_FORMS)
    homes = sum(analysis.homes.values()) or 1
    lines = [
        "## 1 失败长什么样",
        "",
        f"全部 {analysis.pages} 页、{analysis.points} 个抽查点，{failures} 个不通过。"
        f"官方报告只分两种——「值在任何表里都找不到」与「值找到了但标签关联不上」。"
        f"下表把这两种拆成能改的形状。"
        f"**{addressing / failures:.0%} 是寻址失败**——键找不到；"
        f"剩下 {(failures - addressing) / failures:.0%} 是读数侧，"
        f"其中读错数 {reading / failures:.0%}、量纲错 "
        f"{analysis.kinds['unit_mismatch'] / failures:.0%}。",
        "",
        "| 形态 | 个数 | 占失败 | 是什么 | 指向 |",
        "|---|---:|---:|---|---|",
    ]
    for kind in KIND_ORDER:
        if kind in READING_FORMS[1:]:
            continue
        count = reading if kind == "value_off" else analysis.kinds[kind]
        name = "数字读错了" if kind == "value_off" else KIND_ZH[kind]
        lines.append(f"| `{kind}` {name} | {count} | {count / failures:.1%} | "
                     f"{KIND_NOTE[kind]} | {POINTS_AT[kind]} |")
    lines += ["",
              f"**没有一页交白卷。** {analysis.pages} 页全都至少写出了一张表，"
              f"`no_table` 一例没有——榜单上 <6% 的那几个专用 OCR 全卡在这一步"
              f"（[01 §4](../../review/01_benchmark.md#4-榜单)）。", "",
              "### 1.1 关联不上的那个键，到底在哪", "",
              f"对 `label_unlinked` 的 {analysis.kinds['label_unlinked']} 个点，"
              f"把度量点名的那个键在解析器输出里再找一遍，{homes} 次落位：", "",
              "| 它在哪 | 次数 | 占比 |", "|---|---:|---:|"]
    for home in HOME_ORDER:
        count = analysis.homes.get(home, 0)
        if count:
            lines.append(f"| {HOME_ZH[home]} | {count} | {count / homes:.1%} |")
    lines += ["",
              f"**{analysis.homes['in_a_table_but_not_addressing'] / homes:.0%} 的失联键"
              f"就在同一张表里。** 解析器看见了这个键、也写下来了，"
              f"只是把它放在了宽表的另一个位置。这不是感知问题，是表的形状问题——"
              f"[02 §4 结论 1](../../review/02_chart_metric.md#4-三条对输出格式的直接结论) "
              f"说长表最稳，这里是它的价码。", ""]
    if analysis.addressing_ceiling:
        lines += [f"把这 {addressing} 个寻址失败全部改对，按页平均从 "
                  f"**{analysis.page_mean:.2%} 抬到 {analysis.addressing_ceiling:.2%}**。"
                  f"这是上界不是预测：它假设表换了形状而读数一个不变。", ""]

    errors = analysis.errors
    if errors:
        lines += ["### 1.2 读错的时候，错多少", "",
                  f"{len(errors)} 个读数失败，把解析器写在寻址格里的数与标注值相比：", "",
                  "| 相对误差 | 累计个数 | 累计占比 |", "|---|---:|---:|"]
        for bound, name in ((0.05, "5%"), (0.1, "10%"), (0.2, "20%"), (0.5, "50%")):
            count = sum(1 for error in errors if error <= bound)
            lines.append(f"| ≤ {name} | {count} | {count / len(errors):.0%} |")
        lines += ["",
                  f"中位 {errors[len(errors) // 2]:.0%}。"
                  f"**把容差放宽一倍救不回一半**——这一类多数不是「差一点」，"
                  f"是读到了别的东西。", ""]

    lines += ["### 1.3 十页实例", "",
              "一页一个机制，都对着渲染出来的原页读过；逐页在 [cases/](cases/)。", "",
              "| 页面 | 机制 | 形态 |", "|---|---|---|"]
    for case in CASES:
        lines.append(f"| [{case.stem}](cases/{quote(case.stem)}/case.md) | {case.title} | "
                     f"{KIND_ZH[case.kind]} |")
    return lines + [""]


def _section_what_is_hard(analysis: Analysis) -> list[str]:
    lines = [
        "## 2 什么样的图更容易失败",
        "",
        f"这一节分母变小：只有 {analysis.analysed_pages} 页有图表描述"
        f"（[reports/](../../reports/INDEX.md) 那一轮的产物），落在其上的 "
        f"{analysis.analysed_points} 个抽查点。**每一行都是相关，不是因果**，理由在第 4 节。",
        "",
        "### 2.1 三条能直接读的曲线",
        "",
        "| 自变量 | 分档 | 通过率 | 95% 区间 |", "|---|---|---:|---|",
    ]
    for keys in (2, 3, 4):
        entry = analysis.by_arity[keys]
        low, high = entry.interval
        lines.append(f"| 定位需要几个键（全 {analysis.pages} 页） | {keys} 键 | "
                     f"{entry.value:.1%} | n={entry.total} · [{low:.0%}, {high:.0%}] |")
    for band in ("≤20", "21–60", "61–150", "151–400", ">400"):
        entry = analysis.by_density.get(band)
        if entry:
            low, high = entry.interval
            lines.append(f"| 图元个数 | {band} | {entry.value:.1%} | "
                         f"n={entry.total} · [{low:.0%}, {high:.0%}] |")
    for printed in ("all", "some", "none"):
        entry = analysis.by_printed.get(printed)
        if entry:
            low, high = entry.interval
            lines.append(f"| 数值是否印在图上 | {PRINTED_ZH[printed]} | {entry.value:.1%} | "
                         f"n={entry.total} · [{low:.0%}, {high:.0%}] |")
    for name, entry in analysis.by_text_band.items():
        low, high = entry.interval
        lines.append(f"| 整页文字量（全 {analysis.pages} 页） | {name} | {entry.value:.1%} | "
                     f"n={entry.total} · [{low:.0%}, {high:.0%}] |")
    lines += ["",
              "前三条都单调，两端区间都不重叠。"
              "**第四条不单调**：最少文字与最多文字那两档都低，中间两档高，"
              "而两端与中间的区间并不重叠。图元个数、每页图数、数值是否印出，"
              "这三项在四档之间都没有对应的差别。**原因未定，不做推测。**"
              "**键数那一条用的是全量 568 页**，"
              "不依赖图表描述，是这次最硬的一条。", "",
              "### 2.2 面板数几乎不影响", "", "| 面板 | 点数 | 通过率 |", "|---|---:|---:|"]
    for name in ("1 面板", "2 面板", "3+ 面板"):
        entry = analysis.by_panels.get(name)
        if entry:
            lines.append(f"| {name} | {entry.total} | {entry.value:.1%} |")
    lines += ["",
              "**难的是键多，不是面板多。** 单面板图只要「类目 × 系列 × 测度」"
              "要三个键才能定位，就和小倍数一样难。P2 的说法要相应改成"
              "「键的全局唯一性」，而不是「多面板专用字段」。", "",
              "### 2.3 哪种画法最贵", "",
              f"控制组是**图上一个数值都不写**的那 {analysis.control_points} 个点"
              f"（通过率 {analysis.control_rate:.1%}）。数值印不印在图上单独就值 19 个点，"
              f"不控住它，每一行都在重复这同一件事。只列区间不重叠的。", "",
              "| 组件 | 页 | 文档 | 有 | 无 | 差 |", "|---|---:|---:|---:|---:|---:|"]
    for entry in analysis.costly(10):
        lines.append(f"| `{entry.key}` | {entry.pages} | {entry.documents} | "
                     f"{entry.present.value:.1%}（n={entry.present.total}） | "
                     f"{entry.absent.value:.1%} | **{entry.delta:+.1%}** |")
    lines += ["",
              "**「文档」这一列比「n」重要。** n 数的是抽查点，一页最多十个点，"
              "所以 n=60 有可能只来自六页、两份报告——那是一家出版方的习惯，"
              "不是一条通用的作图习惯。前两行正是这种情况。"]
    lines += ["",
              "反过来那一端（`axis_starts_above_zero`、`data_link_below_figure`、"
              "`figure_number_title`）不要当杠杆读：它们标记的是"
              "「这是一家会好好做图的出版方」，不是「加上这个组件会变好」。", "",
              "### 2.4 稠密的图失败在寻址，稀疏的图失败在读数", "",
              "| 图元个数 | 失败数 | 寻址 | 读数 |", "|---|---:|---:|---:|"]
    for band in ("≤20", "21–60", "61–150", "151–400", ">400"):
        counter = analysis.family_by_density.get(band)
        if not counter:
            continue
        total = sum(counter.values())
        lines.append(f"| {band} | {total} | {counter['addressing'] / total:.0%} | "
                     f"{counter['reading'] / total:.0%} |")
    return lines + ["",
                    "只有最稀疏那一档以读数失败为主。图一旦超过二十个图元，"
                    "失败就固定在四分之三是寻址——**这条链不是「越密越读不准」，"
                    "而是「越密越写不成一张对得上号的表」**。", ""]


def _section_changes(analysis: Analysis, negative_rate: float) -> list[str]:
    prices = _prices(analysis, negative_rate)
    lines = ["## 3 翻成流水线改动", "",
             "十项。前八项这次数据给出了价，第九项只给了相关，第十项没给证据但保留。"
             "**「通用」这一列问的是同一个问题：ParseBench 不存在，这条还值不值得做。**", "",
             "| # | 改动 | 归入 | 这次数据给的价 | 通用 |", "|---:|---|---|---|---|"]
    for number, item in enumerate(IMPROVEMENTS, 1):
        lines.append(f"| {number} | {item.name} | {item.maps_to} | "
                     f"{item.price.format(**prices)} | {item.generality} |")
    lines.append("")
    for number, item in enumerate(IMPROVEMENTS, 1):
        lines += [f"### {number} · {item.name}", "",
                  f"`{item.maps_to}` · {item.generality}", "",
                  item.plain.format(**prices), "",
                  f"**例子**：{item.example.format(**prices)}", "",
                  f"**价**：{item.price.format(**prices)}", ""]
    return lines


def _indistinct(analysis: Analysis) -> int:
    """Candidates for the two neighbour-based forms -- too few, and too coincidental."""
    return analysis.kinds["series_swap"] + analysis.kinds["stack_confusion"]


def _predicted(analysis: Analysis) -> str:
    parts = []
    for name in ("step 2", "step 3", "step 4"):
        entry = analysis.by_predicted_step.get(name)
        if entry:
            parts.append(f"{name} {entry.value:.0%}（n={entry.total}）")
    if not parts:
        return ""
    return ("它当时逐页预测过「这一页最难的是第几步」，按那个预测分组，实际通过率是 "
            + " · ".join(parts) + "——预测第二步（读值）最难的那些页，确实是最低的一档。")


def _section_trust(analysis: Analysis) -> list[str]:
    disagreements = round((1 - analysis.matcher_agreement) * analysis.points)
    return [
        "## 4 能不能信", "",
        "### 4.1 通过与否从来不是这里判的", "",
        "每个点的 `passed` 都取自运行目录里的 `_evaluation_report.json`——"
        "官方 metric 跑出来的原值，本目录一行都没有重判。"
        "这里只做一件事：**在解析器的输出里把这个值和这些键再找一遍，看它们落在哪**，"
        "好给失败起一个能改的名字。", "",
        f"那份「再找一遍」的实现是轻量的（`difflib` 而不是 `rapidfuzz`，不展开 colspan）。"
        f"它与官方在「值找没找到」这一问上的一致率是 **{analysis.matcher_agreement:.2%}**"
        f"（{analysis.points} 个点里分歧 {disagreements} 个），"
        f"第 1 节的分档误差因此在个位数量级。", "",
        "### 4.2 两种形态没能分出来", "",
        f"[六类归因](../../data/failure_cases/README.md)里，「串系列」与「读了累计值」"
        f"这次**没有分辨出来**。检测器在全量上只找到 {_indistinct(analysis)} 个候选，"
        f"而它们写下的数与真值都只差一格刻度——巧合能同样好地解释。"
        f"这些点已并入读数失败，不单列。**原因未定，不做推测。**", "",
        "### 4.3 第 2 节全部是相关", "",
        "组件之间高度共现（密集的图往往也有参考线、也不写数值），"
        "控制组只控住了最大的那一个混淆项——数值是否印在图上。"
        "「无标题的图通过率低二十个点」很可能是"
        "「无标题的图多半是仪表盘式的密集版面」，不是标题本身在起作用，"
        "**所以第 3 节第 9 行明写这条不能当因果读**。"
        "要变成因果只有一条路：我们自己按单变量生成两组图、其余维度固定，"
        "这正是消融行的定义"
        "（[05 §7](../../../storyline/parsebench_chart/05_output.md#7-消融)）。",
        "",
        "### 4.4 这一份跑的是什么", "",
        f"`{analysis.run}`：版面模型 PP-DocLayoutV3 lean + `{analysis.model}`，"
        f"200 dpi，verify_rounds=4，整页一次，中位 91 秒 / 页。"
        f"按页平均 **{analysis.page_mean:.2%}**，micro **{analysis.micro:.2%}**，"
        f"满分 {analysis.perfect} 页、零分 {analysis.zero} 页。", "",
        f"同口径下（同 {analysis.pages} 页、同 {analysis.points} 条规则、官方 metric），"
        f"这个分数**高于 [01 §4](../../review/01_benchmark.md#4-榜单) 榜单上的所有方法**"
        f"（最高 LlamaParse Agentic 78.11%）。榜单行是否用同一版评测代码算出来，"
        f"本目录无法核实，所以不写「新 SOTA」；能写的是——"
        f"**这里分析的这些失败，是一个已经很强的系统剩下的失败**。", "",
        "### 4.5 没有测的", "",
        "- **只有一个模型、一条流水线。** 形态分布是这一套系统的，"
        "不是「模型普遍如此」。第 3 节里凡是拿分布比例定优先级的，换一条流水线都要重跑。",
        "- **Visual Grounding 一维没碰。** 这次运行只有 parse 产物。",
        f"- **第 2 节的 {analysis.analysed_pages} 页与全量不独立**——"
        f"它是同一批页面的随机子集，那些相关只能提假设，不能当验收。",
        "- **图表描述本身来自另一个模型**（[reports/](../../reports/INDEX.md) 那一轮，"
        "claude-opus-5），它的错会原样传进第 2 节。有意思的是它可以反过来核："
        + _predicted(analysis),
        "",
    ]


def render_index(analysis: Analysis, negative_rate: float) -> str:
    failures = sum(analysis.kinds.values())
    addressing = sum(analysis.kinds[kind] for kind in ("label_unlinked", "row_missing"))
    homes = max(sum(analysis.homes.values()), 1)
    head = [
        f"# ParseBench Charts · 失败样本分析 · `{analysis.run}`", "",
        f"**这一份分析什么**：一次完整的 ParseBench chart 分片运行"
        f"（{analysis.pages} 页 / {analysis.points} 个抽查点 / "
        f"PP-DocLayoutV3 lean + `{analysis.model}`）的失败样本。目的只有一个——"
        f"[从失败形态倒推流水线缺哪类样本](../../data/failure_cases/README.md)。"
        f"页面特征描述取自 [reports/](../../reports/INDEX.md)，那一份不动。", "",
        "---", "", "## 一句话结论", "",
        f"这一跑按页平均 **{analysis.page_mean:.2%}**，"
        f"比 [01 §4](../../review/01_benchmark.md#4-榜单) 榜单上任何方法都高。"
        f"它剩下的 {failures} 个失败里，**{addressing / failures:.0%} 不是把数读错了，"
        f"而是那个数在表里找不到能对上的键**——其中 "
        f"{analysis.homes['in_a_table_but_not_addressing'] / homes:.0%} 的失联键"
        f"就写在同一张表里，只是不在值那一行。", "",
        f"所以对生成流水线，这次数据给出的第一顺位不是「画得更准」，而是"
        f"**「每个图元都带着它的全部键」**——那正是输出单位 `(键, 值, 区域)` 的定义。"
        f"第二顺位是稠密度：≤20 图元 {_rate(analysis, 'by_density', '≤20')} → "
        f">400 图元 {_rate(analysis, 'by_density', '>400')}，"
        f"而 `chart_types.md` 现在的上限全落在最容易那一档。", "",
        "| 节 | 问什么 | 分母 |", "|---|---|---|",
        f"| [1 失败长什么样](#1-失败长什么样) | {failures} 个失败各是什么形态 | "
        f"全部 {analysis.pages} 页 |",
        f"| [2 什么样的图更容易失败](#2-什么样的图更容易失败) | 哪种画法要付代价 | "
        f"有图表描述的 {analysis.analysed_pages} 页 |",
        "| [3 翻成流水线改动](#3-翻成流水线改动) | 每一条改动值多少 | — |",
        "| [4 能不能信](#4-能不能信) | 怎么算的、什么没测 | — |", "", "---", "",
    ]
    return "\n".join(head + _section_forms(analysis) + ["---", ""]
                     + _section_what_is_hard(analysis) + ["---", ""]
                     + _section_changes(analysis, negative_rate) + ["---", ""]
                     + _section_trust(analysis)) + "\n"
