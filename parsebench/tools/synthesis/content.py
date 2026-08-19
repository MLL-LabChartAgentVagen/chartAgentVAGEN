"""The wording the merged view adds on top of the two analyses it reads.

Three things live here and nowhere else. **Which axis a gap belongs to** -- the whole
point of merging, and a judgement, so it is written down rather than derived. **The
English half of anything the two analyses only wrote in Chinese**: `Component.basis`
and the case notes, so the two languages can carry the same content. And **the field
labels of a card**, kept together so the Chinese and English pages cannot drift into
saying different things about the same box.

Everything that is a number stays out. Counts, rates and prices are read from the
page analysis and the failure summary at render time, so a rerun of either analysis
moves this page with it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Axis:
    """One capability axis: what it is, what it absorbs, what it newly annotates."""

    id: str
    zh: str
    en: str
    line_zh: str
    line_en: str
    yields_zh: str
    yields_en: str


AXES: tuple[Axis, ...] = (
    Axis("a1", "全地址键与键分量的落地", "Complete address keys, and grounding each key component",
         "每个图元带一个全局唯一的键元组；键的每一个分量在页面上由哪个构造写出、"
         "写在哪块像素，同样记下来。",
         "Every mark carries a globally unique key tuple, and for each key component the "
         "pipeline also records which construct on the page spells it out and in which pixels.",
         "键分量 → 它的字面出处的区域。现有工作 ground 的是结构元素或答案，"
         "没有把「键的每一个分量指回它的字面出处」当作训练目标。",
         "key component → the region of its literal source. Existing work grounds structural "
         "elements or answers; no work treats pointing each key component back to its literal "
         "source as a training target."),
    Axis("a2", "可读性是一个连续量", "Readability as a continuous quantity",
         "`readable` 从布尔改为 ε——该图元在当前像素几何下能达到的相对精度；"
         "稠密度从固定上限改为可控自变量。",
         "Change `readable` from a boolean to ε, the relative precision this mark can attain "
         "under its current pixel geometry, and density from a fixed ceiling into a controlled "
         "independent variable.",
         "每个图元的可达读数精度 ε。现有数据集只说这个值是多少，不说它在这张图上最多能读到多准。",
         "the attainable reading precision ε of every mark. Existing datasets state what the "
         "value is, never how precisely it can be read off this particular image."),
    Axis("a3", "数值的呈现语义", "Presentation semantics of a number",
         "一个图元表示的量，是数据里的那个数经过一条声明过的呈现链——比例因子、单位、"
         "基期、符号约定、数字格式——之后印出来的样子。这条链现在一个字段都没有。",
         "The quantity a mark denotes is the number in the data after a declared presentation "
         "chain: scale factor, unit, basis, sign convention, numeric format. That chain "
         "currently has no field anywhere.",
         "规范值与印刷字面的配对，外加单位的承载位置。现有 chart-to-table 数据集只留一个数，"
         "量级错误因此无法与读数错误分开统计。",
         "the pairing of canonical value with printed literal, plus the location of the unit "
         "carrier. Existing chart-to-table datasets keep one number, so magnitude errors cannot "
         "be counted separately from reading errors."),
    Axis("a4", "非数据图元与缺失", "Non-data ink and absence",
         "图上画着但不是任何一个数据点的形状——参考线、批注框、阴影带、高亮、误差棒、"
         "`N/A` 占位——现在一个都画不出来，因此这份数据集从来没有教过「哪些形状不要转录」。",
         "Shapes drawn on a figure that are not any data point -- reference lines, callouts, "
         "shaded bands, highlights, error bars, `N/A` placeholders -- cannot currently be drawn "
         "at all, so this dataset has never taught which shapes must not be transcribed.",
         "精确的负样本。真实图表上没有人会去标「这条线不是数据」，边画边记的生成器是唯一"
         "能零成本给出精确负样本的来源。",
         "exact negatives. Nobody annotates \"this line is not data\" on real charts; a "
         "record-while-drawing generator is the only zero-cost source of exact negatives."),
    Axis("a5", "图是页面对象", "The figure is a page object",
         "图有身份（图号 + 标题 + 副标题 + 单位 + 位置）、有版面、有呈现自由度；"
         "身份同时是一页多图时的寻址根，也是 60% 的真实图上单位与口径的唯一载体。",
         "A figure has an identity (figure number + title + subtitle + unit + position), a "
         "layout, and presentation degrees of freedom; that identity is both the addressing "
         "root on multi-figure pages and, on 60% of real figures, the only carrier of the unit.",
         "图身份把 L0 版面层与 L1 编码层连起来——页面上的每个文本块可以指认它属于"
         "哪张图的哪个字段。",
         "figure identity links the L0 layout layer to the L1 encoding layer: every text block "
         "on the page can be attributed to a field of a specific figure."),
)

#: Which axis each of the 39 gaps belongs to. The judgement the merge exists to make.
KEY_AXIS: dict[str, str] = {
    "wrapped_category_labels": "a1", "footnote_marker": "a1",
    "color_encodes_extra_attribute": "a1", "two_level_x_ticks": "a1",
    "small_multiples_5plus": "a1", "inline_series_labels": "a1",
    "icon_category_axis": "a1", "total_row_below_axis": "a1", "stacked_and_grouped": "a1",
    "value_label_outside": "a2", "no_value_axis": "a2", "dense_marks_100plus": "a2",
    "thin_segment_label": "a2", "tick_marker_as_series": "a2",
    "range_connector_line": "a2", "step_line_series": "a2",
    "unit_in_axis_or_title": "a3", "negative_values": "a3", "nonstandard_time_ticks": "a3",
    "axis_starts_above_zero": "a3", "rebased_index_values": "a3", "pct_stacked": "a3",
    "unit_in_series_name": "a3", "broken_axis": "a3",
    "highlighted_category": "a4", "reference_line": "a4", "annotation_callout": "a4",
    "shaded_band": "a4", "missing_value_marker": "a4", "error_bars": "a4",
    "panel_background": "a5", "side_text_bullets": "a5", "horizontal_bars": "a5",
    "axis_title_above_axis": "a5", "legend_inside_plot": "a5",
    "data_link_below_figure": "a5", "axis_title_below_plot": "a5",
    "dashed_line_series": "a5", "right_side_y_axis": "a5",
}

#: `Component.basis` in English -- why the current spec cannot draw this.
BASIS_EN: dict[str, str] = {
    "wrapped_category_labels": "`chart_types.md §2` caps category cardinality at 30, and "
                               "labels are never wrapped",
    "footnote_marker": "labels render without footnote markers",
    "color_encodes_extra_attribute": "`03 §3` colours by series; colour carries no data column",
    "two_level_x_ticks": "axis labels are a one-dimensional list of values",
    "small_multiples_5plus": "`02 §4.1` caps panels at 4",
    "inline_series_labels": "series names reach the page only through a legend; `03 §3` has no "
                            "inline value for the legend dimension",
    "icon_category_axis": "the category axis renders only the string values of a `dim`",
    "total_row_below_axis": "the record has no element for a row of totals outside the axes",
    "stacked_and_grouped": "the two dimensions consume P and S; the third has nowhere to go",
    "value_label_outside": "`labeled` in `03 §6` is a boolean and records no position",
    "no_value_axis": "the axis dimension in `03 §3` has no \"draw no value axis\" value",
    "dense_marks_100plus": "`chart_types.md §2` caps \\|P\\|·\\|S\\| at 24 / 20",
    "thin_segment_label": "`labeled` in `03 §6` is a boolean and handles neither crowding "
                          "nor displacement",
    "tick_marker_as_series": "none of the five mark shapes in `chart_types.md §3` is a "
                             "tick marker",
    "range_connector_line": "a range segment is no family's mark; `chart_types.md` has no "
                            "such shape",
    "step_line_series": "`line` in `chart_types.md` has one drawing method, straight between "
                        "points",
    "unit_in_axis_or_title": "unit sits in the measure declaration in `01`; neither axis title "
                             "nor figure title carries it",
    "negative_values": "rectangular marks in `chart_types.md` extend one way from a zero baseline",
    "nonstandard_time_ticks": "a `time` column is declared by start/end/freq, and tick "
                              "formatting is not a style-vector dimension",
    "axis_starts_above_zero": "the axis dimension in `03 §3` has no value-axis origin, and "
                              "rectangular marks start at zero",
    "rebased_index_values": "the measure declaration in `01` has a unit but no index-with-base",
    "pct_stacked": "stacking records `value` with `cum_start`/`cum_end`; a share needs its own "
                   "field the way `pie` has one",
    "unit_in_series_name": "unit sits in the measure declaration in `01` and takes no part in "
                           "label rendering",
    "broken_axis": "`03 §1` freezes the layout; value range to pixel range is one linear map",
    "highlighted_category": "`03 §3` colours by series and has no single-category highlight",
    "reference_line": "a reference line is no family's mark; `chart_types.md` has no such shape",
    "annotation_callout": "a callout is no family's mark; `chart_types.md` has no such shape",
    "shaded_band": "a shaded region is no family's mark; `chart_types.md` has no such shape",
    "missing_value_marker": "every cell after projection has a value; absence never enters the "
                            "candidates, `02 §3`",
    "error_bars": "five numbers appear only on `box`; every other type's value dict holds "
                  "`value` alone",
    "panel_background": "neither the graphic-detail nor the palette dimension of `03 §3` "
                        "includes a panel fill",
    "side_text_bullets": "page elements in `03 §5` are vertically stacked blocks, with no text "
                         "column beside the figure",
    "horizontal_bars": "the condition table in `chart_types.md` has no orientation dimension",
    "axis_title_above_axis": "axis title position is not a style-vector dimension",
    "legend_inside_plot": "legend position in `03 §3` is outside or one per panel, never inside "
                          "the plot area",
    "data_link_below_figure": "the only text under a figure in `03 §5` is the caption",
    "axis_title_below_plot": "axis title position is not a style-vector dimension",
    "dashed_line_series": "the graphic-detail dimension of `03 §3` has fill texture, not line style",
    "right_side_y_axis": "only `compound` uses a right axis in `chart_types.md`; a single value "
                         "axis is fixed on the left",
}


@dataclass(frozen=True)
class CaseNote:
    """One failure page: which axis it argues for, and what it argues."""

    stem: str
    kind: str
    axis: str
    mech_zh: str
    mech_en: str
    says_zh: str
    says_en: str


CASES: tuple[CaseNote, ...] = (
    CaseNote(
        "pwc-semiconductor-and-beyond-2026-full-report_p17", "label_unlinked", "a1",
        "列名写成了颜色：`Gray` / `Orange`，而图例上写的是 `Conventional demand` / "
        "`AI-driven demand`。十个数字一个不差，十个点全判 0。",
        "The column headers are colours -- `Gray` / `Orange` -- while the legend reads "
        "`Conventional demand` / `AI-driven demand`. Every one of the ten numbers is right and "
        "all ten points score 0.",
        "「哪个色块是哪个系列」现在没有任何训练目标在教，而画图时颜色与系列名都是已知的。"
        "同一页还把两根柱之间的浅橙色连接带写成了第三个系列——A4 的价，就在这一页上。",
        "Nothing in the current targets teaches which swatch is which series, although colour "
        "and series name are both known while drawing. The same page also wrote the pale orange "
        "connector band between two bars as a third series -- A4's price, on one page."),
    CaseNote(
        "Technopak_Industry_Report_p18", "label_unlinked", "a1",
        "同一图号下的三张饼（2019 / 2024 / 2029P）被拆成三张小表：两张只有数字没有类目名，"
        "一张有类目名没有年份。六个数字全对，六个点全判 0。",
        "Three pies under one figure number (2019 / 2024 / 2029P) became three small tables: two "
        "carry numbers without category names, one carries category names without the year. All "
        "six numbers are right and all six points score 0.",
        "面板名如果只是一个内部编号、不作为键写出去，每张面板表都比规则少一个键。"
        "这一页的数值全部印在图上，读数一处没错。",
        "When the panel name is only an internal index and is never exported as a key, every "
        "panel table is one key short of what the rule needs. Every value on this page is "
        "printed on the figure; not one reading is wrong."),
    CaseNote(
        "Digital_News-Report_2022_p46", "label_unlinked", "a1",
        "表的形状完全正确——43 行长表，一行一个国家。值那一列的表头写成了整段问卷题干，"
        "而规则的第二个键是 `Percentage`。",
        "The table shape is exactly right -- a 43-row long table, one country per row. The header "
        "over the value column is the full survey question, while the rule's second key is "
        "`Percentage`.",
        "值那一列的表头本身就是一个键，它的名字应该来自测度声明，"
        "而不是页面上离得最近的一句话。",
        "The header over the value column is itself a key. Its name should come from the measure "
        "declaration, not from the nearest sentence on the page."),
    CaseNote(
        "ac8b3538-en_p62", "label_unlinked", "a1",
        "15 个国家的小折线，1,830 个图元，一个数值都不写。国名进了表前的标题因此认得出，"
        "两条线的系列名却被写成页顶一行普通正文——9 个失败点里 7 个缺的是这个系列名。",
        "Fifteen country panels, 1,830 marks, not one printed value. The country names reached "
        "headings before the tables and were recognised; the two series names were written as one "
        "ordinary line of text at the top of the page -- 7 of the 9 failing points are missing "
        "exactly that series name.",
        "系列名必须跟着它那条线一起写进表，写成一行普通正文等于没写。"
        "这一页同时是 A2 的实例：现有上限画不到 1,830 个图元这一档。",
        "A series name has to travel into the table with its own line; written as a line of body "
        "text it is not written at all. The page is also an A2 instance: the current ceilings "
        "cannot reach 1,830 marks."),
    CaseNote(
        "VPEG6_SIV_Information_Memorandum__June_2025__p11", "row_missing", "a1",
        "系列名只画在图里当文字，一个字都没进表——整个键在输出里不存在。",
        "The series names are drawn inside the figure as text and never reach a table; the whole "
        "key is absent from the output.",
        "与上一页同一条链的极端形态：不是键放错了位置，是键根本没被写出来。"
        "键分量的落地要覆盖「画在绘图区里的文字」这一种承载形式。",
        "The extreme form of the same chain: the key is not misplaced, it was never written. "
        "Grounding key components has to cover text drawn inside the plot area as a carrier."),
    CaseNote(
        "mts0625_p6", "row_missing", "a1",
        "一页两张图都叫 Receipts，系列名完全相同，规则只好用四个键，第四个键是 `Figure 3.`。"
        "图号没进表，这些点就无法定位。",
        "Two figures on one page are both called Receipts with identical series names, so the "
        "rules need four keys and the fourth is `Figure 3.`. The figure number never reached a "
        "table, so those points cannot be addressed.",
        "一页多图时，图号本身是一个键分量——这是 A5 的图身份进入 A1 的寻址根的那一处接缝。",
        "On a multi-figure page the figure number is itself a key component -- the seam where "
        "A5's figure identity enters A1's addressing root."),
    CaseNote(
        "sri-sigma-natural-catastrophes-1-2025_p10", "value_off", "a2",
        "每根柱子都读低了正好半格：1→0、4→3.5、8→7.5。纵轴是「有多少年」，只能取整数。",
        "Every bar is read exactly half a gridline low: 1→0, 4→3.5, 8→7.5. The vertical axis "
        "counts years and can only take integers.",
        "取值格这一条先验能把这些读数直接吸附回合法值。它在 01 的列声明里本来就知道，"
        "现在没有任何字段记它。",
        "The value-lattice prior snaps these readings straight back onto legal values. It is "
        "already known in the column declarations in 01 and no field records it."),
    CaseNote(
        "World_Inequality_Report_2026_p79", "value_off", "a2",
        "表的形状完全正确，4,000 个图元照样只对了一个点。",
        "The table shape is exactly right, and with 4,000 marks only one point still passes.",
        "稠密度单独就足以让读数失败，与寻址无关。现有上限全部落在最容易的那一档，"
        "这一档我们连一张都生成不出来。",
        "Density alone is enough to break the reading, independent of addressing. The current "
        "ceilings all sit in the easiest bucket and cannot produce a single page like this one."),
    CaseNote(
        "The_State_of_UK_Competition_Report_2024_p31", "unit_mismatch", "a3",
        "刻度写的是 `.4` 不是 `0.4`，整张图读大了 10 倍。",
        "The ticks read `.4` rather than `0.4`, and the whole figure is read ten times too large.",
        "刻度标签的写法直接决定读数的量级，而它现在不是风格向量的任何一维。",
        "How a tick label is written decides the magnitude of the reading, and it is not a "
        "dimension of the style vector today."),
    CaseNote(
        "Activate_Consulting_Technology_&_Media_Outlook_2026_(10)_p60", "unit_mismatch", "a3",
        "图题写 BILLIONS、标注写 `$101B`，规则要 `101`——多写一个 B 就全错。",
        "The figure title says BILLIONS and the label says `$101B` while the rule wants `101`; "
        "one extra B and the point is wrong.",
        "同一个值的规范形与印刷形必须分开记录，单位写在哪也必须是一个采样维。",
        "The canonical and printed forms of one value have to be recorded separately, and where "
        "the unit is written has to be a sampled dimension."),
)

TYPE_GAPS = (
    ("map", "地理投影不是六族中的任何一族，图元也不在五种形状里。3 份文档，不为它改条件表。",
     "A geographic projection is none of the six families and its marks are none of the five "
     "shapes. Three documents; the condition table is not changed for it.",
     "不加", "do not add"),
    ("other", "模型报 `other` 时自拟名字。拆开看只有三张是真的新画法——"
              "哑铃 / 区间图的两种与一种竖排变体；其余是表格与非图条目。",
     "When the model reports `other` it names the figure itself. Split apart, only three are "
     "genuinely new drawing methods -- two dumbbell / range plots and a vertical variant; the "
     "rest are tables and non-figures.",
     "区间连接线加进图元形状", "add the range connector as a mark shape"),
)

#: Field labels of a card, and the few fixed strings around the galleries.
UI = {
    "evidence": ("这一页上的证据（模型写的原话）", "Evidence on this page, in the model's words"),
    "criterion": ("判据（送给模型的原话）", "The criterion, as sent to the model"),
    "why": ("我们为什么画不出来", "Why the current spec cannot draw it"),
    "figures": ("这一页的图（模型报的）", "The figures on this page, as the model reported them"),
    "also": ("另见", "Also on"),
    "pages": ("页", "pages"),
    "docs": ("份文档", "documents"),
    "price": ("失败分析测到的价", "Price measured by the failure analysis"),
    "no_price": ("未单独测到价", "no price measured separately"),
    "steps": ("影响判定第 {} 步", "affects judging step {}"),
    "nostep": ("基准看不见它", "invisible to the metric"),
    "wrote": ("✗ 解析器实际写的", "✗ What the parser actually wrote"),
    "pass": ("✓ 写成这样，这一页的失败点全过", "✓ Written this way, the page's failing points pass"),
    "long_note": ("一行一个值，所有键和值写在同一行——判定第三步一次通过，不用任何回退。"
                  "这正是记录层的形状：一个图元 = 一条 `(键, 值, 区域)`。",
                  "One value per row with every key on that row -- the third judging step passes "
                  "outright, with no fallback. This is the shape the record already has: one "
                  "mark = one `(key, value, box)`."),
    "rule_line": ("这一条规则要的是 {v}，定位键 {k}（容差 {t}）",
                  "This rule wants {v}, addressed by {k} (tolerance {t})"),
    "page_score": ("该页 {a} / {b} 通过", "this page passes {a} / {b}"),
    "mech": ("机制", "Mechanism"),
    "says": ("它说明什么", "What it says"),
    "verdict": ("判分程序的原话", "The metric's own words"),
    "gallery": ("它吃掉的每一项，逐项配例",
                "Every item it absorbs, one example each"),
    "axis_line": ("一句话", "In one line"),
    "axis_yield": ("新产出的标注量", "Newly produced annotation quantity"),
    "noimg": ("这张页面图没能加载。先跑 <code>tools/dataset/render_pages.py</code>，"
              "再跑 <code>tools/synthesis/build_view.py</code> 生成 <code>synthesis/assets/</code>。",
              "This page image did not load. Run <code>tools/dataset/render_pages.py</code>, then "
              "<code>tools/synthesis/build_view.py</code> to write <code>synthesis/assets/</code>."),
    "tagline": ("两份分析合并：基准页面特征 × 强解析器失败样本 → 生成流水线的能力轴。"
                "每一项都配这一页的原图与原话。",
                "Two analyses merged: benchmark page characteristics × one strong parser's failure "
                "sample → capability axes for the generation pipeline. Every item carries its own "
                "page and its own words."),
    "title": ("ParseBench 合并结论", "ParseBench Merged Conclusions"),
    "switch": (("English", "view.en.html"), ("中文", "view.html")),
    "source": (("INDEX.md", "纯文字版"), ("INDEX.en.md", "plain text")),
}

FACTS = {
    "zh": [("568", "基准页面"), ("4,864", "抽查规则"), ("896", "失败样本"),
           ("82.75%", "按页平均"), ("5 + 1", "能力轴")],
    "en": [("568", "benchmark pages"), ("4,864", "spot-check rules"), ("896", "failures"),
           ("82.75%", "page average"), ("5 + 1", "capability axes")],
}

#: The failure forms, in the order the gallery shows them. The fourth element is
#: every diagnosis counted under that form -- `series_swap` and `stack_confusion`
#: were not told apart from an ordinary misreading on this run, so they are counted
#: with it rather than given a line of their own.
FORMS: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    ("label_unlinked", "数字对，但表里说不清这个数字是谁的",
     "the number is right, but the table cannot say whose number it is",
     ("label_unlinked",)),
    ("row_missing", "有个键压根没写进表", "a key was never written into the table at all",
     ("row_missing",)),
    ("value_off", "数字读错了", "the number was read wrong",
     ("value_off", "series_swap", "stack_confusion")),
    ("unit_mismatch", "数字写在了错的量级上", "the number was written at the wrong magnitude",
     ("unit_mismatch",)),
)
