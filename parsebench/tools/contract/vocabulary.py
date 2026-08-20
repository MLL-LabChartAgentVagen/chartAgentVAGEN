"""The fixed component vocabulary the page analysis reports against.

One list, two consumers: the English block that goes into the model prompt
(`name_en` and `hint`), and the Chinese tables of the report (`name_zh` and
`basis`). Keeping both renderings here is what lets a whole sample of pages be
summed into one frequency table -- a free-text component name cannot be counted.

It is part of the contract rather than of one analysis run: the same list is what
three models answer against, so a component's count means the same thing whoever
reported it. Every key here is a value domain of `format.PAGE_SCHEMA`.

`ours` says whether the generation pipeline can draw the component today; `affects`
says which of the four scoring steps it can change. Both are read off a written
definition -- `storyline/parsebench_chart/` and `review/02_chart_metric.md` -- never
decided while looking at a page, so the same answer appears in every report.
`CHART_TYPE_OURS` asks the `ours` question of chart types.

**The heading is not in this list.** Figure number, title, subtitle, unit and where
the block sits are five fields of `schema._HEADING`, recorded on every figure. Four
keys used to say the same thing a second time, per page instead of per figure, and
a page reporting both `figure_number_title` and `subtitle_above_plot` counted one
heading twice. They were removed; the report reads that struct instead.

Usage:
    python parsebench/tools/contract/vocabulary.py   # what is in the vocabulary
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Literal

Group = Literal["structure", "layout", "heading", "labels", "style"]

GROUP_TITLES: dict[Group, str] = {
    "structure": "结构",
    "layout": "版面",
    "heading": "标题与单位",
    "labels": "标签与刻度",
    "style": "风格",
}

#: The four steps of ParseBench's `ChartDataPointRule`, which `Component.affects`
#: points into. `parsebench/review/02_chart_metric.md` walks one rule through them.
STEP_NAMES: dict[int, str] = {
    1: "要有表",
    2: "找到值",
    3: "标签关联",
    4: "表外上下文",
}


@dataclass(frozen=True)
class Component:
    """One nameable chart component.

    `hint` is the criterion the model applies, not a definition -- what to look
    at on the page to decide present or absent.
    `basis` points at the spec line behind `ours`, so the answer can be rechecked
    without rereading all of `storyline/`.
    `affects` is which of the four judgement steps this component can change, and
    it is the reason the gap table is readable at all. A component can be on three
    quarters of the pages and still be invisible to the metric: the unit written
    into an axis title appears on 149 of 192 pages, and no rule's value or labels
    ever quote it -- 0 of 4,864 values carry a scale word. Frequency alone would
    rank that first. Empty tuple means the metric never looks at it, which makes it
    a question about how honest the generated data is, not about the score.
    Like `ours`, it is read off the metric definition before any page is seen.
    """

    key: str
    group: Group
    name_en: str
    hint: str
    name_zh: str
    ours: bool
    basis: str
    affects: tuple[int, ...]


VOCABULARY: tuple[Component, ...] = (
    # ------------------------------------------------------------- structure
    Component("grouped_bar", "structure", "grouped bars",
              "two or more bars side by side within each category slot",
              "分组条", True, "`chart_types.md` Tier 1 的 `grouped_bar`",
              (3,)),
    Component("stacked_bar", "structure", "stacked bars",
              "segments stacked inside one bar, the bar length is the total",
              "堆叠条", True, "`chart_types.md` Tier 1 的 `stacked_bar`",
              (2,)),
    Component("pct_stacked", "structure", "percent stacked",
              "every stack reaches the same full height and the axis ends at 100%; stacks of "
              "percentages that reach different heights are not this",
              "百分比堆叠（归一到 100%）", False,
              "堆叠只记 `value` 与 `cum_start`/`cum_end`；占比要像 pie 那样另记 `share`",
              (2,)),
    Component("stacked_and_grouped", "structure", "stacked and grouped together",
              "bars are both grouped side by side and stacked within each bar",
              "堆叠与分组出现在同一张图", False, "两个维度分别吃掉 P 与 S，第三维无处可放",
              (3,)),
    Component("dual_axis", "structure", "dual y axis",
              "two value axes, left and right, carrying different units",
              "双 y 轴，同面板两个量纲", True, "`chart_types.md` 的 `compound`",
              (2,)),
    Component("mixed_marks", "structure", "mixed marks in one panel",
              "two mark shapes in the same panel: bars and a line, or point markers "
              "overlaid on bars",
              "同面板混合图元（bar + line）", True, "`chart_types.md` 的 `compound`",
              (2,)),
    Component("stacked_area", "structure", "stacked area",
              "filled bands stacked over a time axis",
              "堆叠面积", True, "`chart_types.md` 的 `area`",
              (2,)),
    Component("reference_line", "structure", "reference line",
              "a horizontal or vertical rule marking a target, average, threshold or the "
              "zero line, often with its own legend entry",
              "参考线（水平/垂直虚线，含零线，常带独立图例项）", False,
              "参考线不是任何族的图元，`chart_types.md` 无此形状",
              ()),
    Component("negative_values", "structure", "negative values",
              "values below zero, or a centred zero line with bars going both ways",
              "负值 / 零线居中的分叉条", False,
              "`chart_types.md` 的矩形图元自零基线单向延伸，见 P6",
              (2,)),
    Component("error_bars", "structure", "error bars or confidence band",
              "whiskers on a mark, or a shaded band around a line",
              "误差棒 / 置信带", False, "五数只在 `box` 出现，其他类型的值字典只有 `value`",
              ()),
    Component("broken_axis", "structure", "broken axis",
              "the value axis is cut mid-range and the cut is drawn with a break glyph "
              "(a zigzag or a double slash) on the axis itself; an axis that merely starts "
              "above zero is `axis_starts_above_zero`, not this",
              "断轴：轴中间截断并画出断裂标记", False, "`03 §1` 冻结布局，值域到像素域是一段线性映射",
              (2,)),
    Component("log_axis", "structure", "log axis",
              "tick spacing is logarithmic",
              "对数轴", True, "`03 §3` 风格向量「轴」维的取值之一",
              (2,)),
    Component("horizontal_bars", "structure", "bars run horizontally",
              "categories sit on the y axis and the bars grow to the right",
              "横向条形（类目在 y 轴）", False, "`chart_types.md` 的条件表没有方向这一维",
              ()),
    Component("annotation_callout", "structure", "callout inside the plot area",
              "a boxed note, arrow or leader-line label drawn over the plot, explaining "
              "the data rather than being data",
              "绘图区内的说明框 / 引线注解", False,
              "说明框不是任何族的图元，`chart_types.md` 无此形状",
              ()),
    Component("no_value_axis", "structure", "no value axis",
              "no ticks on the value axis, just a baseline; the numbers are only "
              "readable from printed labels",
              "没有值轴刻度，只有基线", False, "`03 §3` 的轴维不含「不画值轴」这一取值",
              (2,)),
    Component("shaded_band", "structure", "shaded band over a range",
              "a tinted vertical or horizontal band marking a forecast window, a "
              "recession, or a target range",
              "阴影带标出某个区间（预测期 / 目标区）", False,
              "阴影区不是任何族的图元，`chart_types.md` 无此形状",
              ()),
    Component("per_panel_axis_range", "structure", "each panel on its own value range",
              "panels of one figure use different axis starts or scales, so a reading "
              "cannot be carried across panels",
              "各面板各自的值域，不共享刻度", True, "`02 §5` FigureSpec 的共享关系可以不共享 y 轴",
              (2,)),
    Component("missing_value_marker", "structure", "missing value shown as text",
              "a cell shows `N/A`, a dash, or an empty slot where a mark would be",
              "缺失值用 `N/A` 或空位代替图元", False, "投影后每格必有值，缺失不进候选，`02 §3`",
              (1,)),
    Component("right_side_y_axis", "structure", "the only value axis on the right",
              "a single value axis drawn on the right edge, not a second axis",
              "唯一的值轴画在右侧", False, "`chart_types.md` 只有 `compound` 用右轴，单值轴固定在左",
              ()),
    Component("axis_starts_above_zero", "structure", "value axis starts above zero",
              "the lowest tick is not zero and the axis is not cut -- bar lengths and the "
              "gaps between them are no longer proportional to the values",
              "值轴起点不是零，且没有断轴标记", False,
              "`03 §3` 的轴维没有「值轴起点」这一取值，矩形图元自零基线起算",
              (2,)),
    Component("step_line_series", "structure", "step line",
              "the line moves in horizontal treads and vertical risers instead of "
              "connecting points directly",
              "阶梯线（水平段 + 垂直跳变），不是直连折线", False,
              "`chart_types.md` 的 `line` 只有点间直连一种画法",
              (2,)),
    Component("color_encodes_extra_attribute", "structure",
              "colour carries a variable of its own",
              "fill colour or shade encodes something other than the series identity -- a "
              "region group, whether a difference is significant, above or below a target",
              "颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标）", False,
              "`03 §3` 配色按系列上色，颜色不承载数据列",
              (3,)),
    Component("tick_marker_as_series", "structure", "a series drawn as a tick marker",
              "one series is a short dash or caret placed at the category position, read "
              "against the same axis as the bars it sits on",
              "某一系列画成短横 / 尖角标记，叠在条上读同一根轴", False,
              "`chart_types.md §3` 的五种图元里没有「刻度标记」这一形状",
              (2, 3)),
    Component("range_connector_line", "structure", "two points joined into a range",
              "two markers per category joined by a segment -- a dumbbell or range plot, "
              "where the segment length is the quantity being compared",
              "每个类目两个点用线段连成区间（哑铃图 / 区间图）", False,
              "区间线段不是任何族的图元，`chart_types.md` 无此形状",
              (2, 3)),
    # ---------------------------------------------------------------- layout
    Component("shared_legend", "layout", "legend shared across panels",
              "two or more panels and one legend outside them governing all; a legend on a single-panel figure is not this",
              "跨面板共享图例", True, "`02 §4.2` 的 FigureSpec 硬约束",
              (3,)),
    Component("shared_axis", "layout", "axis shared across panels",
              "two or more panels sharing one axis, ticks drawn once at the edge",
              "跨面板共享坐标轴", True, "`02 §5` FigureSpec 的共享轴",
              (2,)),
    Component("small_multiples_4", "layout", "small multiples, at most 4 panels",
              "the same chart repeated over a slicing dimension, 2 to 4 panels",
              "同一张图按一维切成多面板（2–4 个）", True, "`02 §4.1`「同指标不同切面」2–4 面板",
              (3,)),
    Component("small_multiples_5plus", "layout", "small multiples, 5 or more panels",
              "the same repeat, but 5 panels or more",
              "同一张图按一维切成多面板（≥5 个）", False, "`02 §4.1` 面板数上限 4",
              (3,)),
    Component("multi_figure_page", "layout", "several independent figures on one page",
              "two or more figures with separate numbers and separate captions",
              "一页多张独立图，各自有图号", True, "`03 §5` 把单页多图列为可控的版面现象",
              (1, 3)),
    Component("source_note_lines", "layout", "source / note lines under the figure",
              "small print below the plot: `Source: ...`, `Note: ...`",
              "source / note 行在图下方", True, "`03 §5` 图注即图下方的 Text 元素",
              ()),
    Component("legend_below_plot", "layout", "legend under the plot area",
              "the legend sits below the plot, outside it",
              "图例在绘图区下方", True, "`03 §3`「版面细节 · 图例外置」维的取值",
              ()),
    Component("legend_inside_plot", "layout", "legend inside the plot area",
              "the legend is drawn over the plot area itself",
              "图例画在绘图区内部", False, "`03 §3` 的图例位置只有外置与每面板一个，没有绘图区内",
              ()),
    Component("per_panel_legend", "layout", "one legend per panel",
              "each panel carries its own legend rather than sharing one",
              "每个面板各有一个图例", True, "`03 §3`「版面细节 · 图例…每面板一个」",
              (3,)),
    Component("heterogeneous_panel_types", "layout", "panels of different chart types",
              "one numbered figure whose panels are different families, e.g. a stacked "
              "bar beside a range chart",
              "同一图号下各面板类型不同", True, "`03 §3`「多面板类型 · 混类型」",
              (1,)),
    Component("data_table_as_figure", "layout", "a plain table presented as a figure",
              "a bordered table with headers, numbered and captioned like a chart",
              "一块带表头的表格当作图收录", True, "`03 §5` 页面元素类别含 Table",
              (1,)),
    Component("legend_above_plot", "layout", "legend above the plot area",
              "the legend sits between the heading and the plot",
              "图例在绘图区上方（标题与图之间）", True, "`03 §3`「版面细节 · 图例外置」维的取值",
              ()),
    Component("legend_beside_plot", "layout", "legend to the left or right of the plot",
              "the legend is a column beside the plot rather than a row above or below it",
              "图例在绘图区左侧或右侧，排成一列", True, "`03 §3`「版面细节 · 图例外置」维的取值",
              ()),
    Component("panel_title_per_panel", "layout", "each panel titled above itself",
              "every panel carries its own name above it, or in a filled banner, in "
              "addition to (or instead of) the figure title",
              "每个面板上方各有一个面板标题 / 色块标题条", True,
              "`02 §5` FigureSpec 的每个面板带名字，`03` 画在面板上方",
              (4,)),
    Component("side_text_bullets", "layout", "running text in a column beside the figure",
              "a narrow column of body text or pull quotes runs alongside the figure, so "
              "the figure and the prose share one horizontal band of the page",
              "图旁另有一栏正文 / 提要文字，与图并排占同一横带", False,
              "`03 §5` 的页面元素是纵向堆叠的块，没有与图并排的文字栏",
              (1,)),
    Component("data_link_below_figure", "layout", "a data or download link under the figure",
              "a line under the figure pointing at the underlying data -- `StatLink`, a "
              "download link, a QR code -- distinct from the source line",
              "图下方另有取数链接（StatLink / download / 二维码），与 source 行分开", False,
              "`03 §5` 的图下文本只有图注一种",
              ()),
    # --------------------------------------------------------------- heading
    Component("unit_in_series_name", "heading", "unit written into the series name",
              "a legend or series label carrying the unit, currency or scale of its own "
              "numbers -- `Operating Cash Flow ($B)`, `Premiums, % change`. A qualifier "
              "that only names the subject (`Personal property premiums`) is not a unit",
              "单位写在系列名里（例：`Operating Cash Flow ($B)`）", False,
              "unit 在 `01` 的 measure 声明里，不参与标签渲染，见 P6",
              (3,)),
    Component("unit_in_axis_or_title", "heading", "unit written into an axis title or heading",
              "the unit lives in the axis title, the subtitle or the figure title -- "
              "`% of GDP`, `in USD billion (2022 prices)` -- and not in the series name. "
              "The usual case is a value axis of bare numbers (0, 25, 50) whose scale word "
              "is recoverable only from that line",
              "单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字", False,
              "unit 在 `01` 的 measure 声明里，轴标题与图题都不带它，见 P6",
              ()),
    Component("axis_title_below_plot", "heading", "axis title under the plot",
              "the value-axis title sits below the plot rather than beside the axis",
              "值轴标题写在图下方", False, "轴标题位置不是风格向量的维",
              ()),
    Component("rotated_axis_title", "heading", "rotated axis title",
              "the axis title is set vertically along the axis",
              "轴标题竖排", True, "y 轴标题竖排是渲染器默认，`03 §3` 的轴维已含标签旋转",
              ()),
    Component("footnote_marker", "heading", "footnote markers in titles or labels",
              "superscript digits or symbols attached to a title, a label or a category",
              "标题或标签里的脚注上标", False, "标签渲染不带脚注标记",
              (3,)),
    Component("axis_title_above_axis", "heading", "axis title above the axis",
              "the value-axis title or its bare unit symbol (`%`, `USD bn`) is set above "
              "the top tick instead of running alongside the axis",
              "值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排", False,
              "轴标题位置不是风格向量的维",
              ()),
    Component("rebased_index_values", "heading", "values are an index with a stated base",
              "the numbers are an index, not the quantity itself, and the base is written "
              "out somewhere -- `2011 = 100`, `Index, 2015 = 1.0`",
              "数值是指数，基期写在标题里（例：`2011 = 100`）", False,
              "`01` 的 measure 声明有 unit，没有「指数 + 基期」这种口径",
              ()),
    # ---------------------------------------------------------------- labels
    Component("value_label_inside", "labels", "value labels inside the mark",
              "the number is printed on top of the bar or segment",
              "数值标签写在图元内部", True, "`03 §6` 的 `labeled`",
              (2,)),
    Component("value_label_outside", "labels", "value labels outside the mark",
              "the number sits beyond the mark, sometimes on a leader line or in a box",
              "数值标签在图元外 / 带引线 / 带边框", False, "`03 §6` 的 `labeled` 只记布尔，不记位置，见 P6",
              (2,)),
    Component("two_level_x_ticks", "labels", "two level x tick labels",
              "an inner tick row and an outer grouping row, usually with separators",
              "x 轴两级标签（年在内、分组在外，带分隔线）", False, "轴标签是一维取值列表",
              (3,)),
    Component("rotated_x_ticks", "labels", "rotated x tick labels",
              "tick text is turned 30 to 90 degrees",
              "x 刻度标签旋转", True, "`03 §3` 风格向量「轴 · 标签旋转」",
              ()),
    Component("abbrev_category_axis", "labels", "abbreviation codes on the category axis",
              "categories written as codes: `IRL`, `EU-27`, `NAM`",
              "类目轴用缩写码（例：`IRL` `EU-27`）", True, "缩写码是 `01` 声明的 `dim` 取值写法本身",
              (3,)),
    Component("nonstandard_time_ticks", "labels", "non ISO time ticks",
              "time written as `2022:06`, `1Q-2024`, or a bare `08`",
              "非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`）", False,
              "`time` 列由 start/end/freq 声明，刻度格式化方式不是风格向量的维，见 P6",
              (3,)),
    Component("sparse_time_ticks", "labels", "fewer ticks than data points",
              "points are yearly but ticks are every two or three years, so a single "
              "point has to be located between ticks",
              "刻度比数据点稀，读某点要自己内插", True, "`03 §3` 风格向量「轴 · 刻度密度」",
              (3,)),
    Component("thin_segment_label", "labels", "labels crowding in thin segments",
              "value labels in narrow stacked segments overlap, shrink, or move outside "
              "the segment",
              "窄分段里的数值标签互相挤压或外移", False,
              "`03 §6` 的 `labeled` 只记布尔，不处理拥挤与外移，见 P6",
              (2,)),
    Component("inline_series_labels", "labels", "series named beside the mark",
              "no legend: the series name is written next to the line or at its endpoint",
              "没有图例，系列名直接标在线旁", False,
              "系列名只通过图例呈现，`03 §3` 的图例维无「直标」取值",
              (3,)),
    Component("wrapped_category_labels", "labels", "long category labels, wrapped or stacked",
              "category names wrap onto two lines, or dozens of them stack down one axis",
              "类目名折行，或几十个类目排成长列", False,
              "`chart_types.md §2` 的类目基数上限 30，且标签不折行",
              (3,)),
    Component("total_row_below_axis", "labels", "a totals row under the axis",
              "a line of totals printed below the category axis, aligned to it but not a tick",
              "轴下方一行合计值，与类目对齐", False, "记录里没有「轴外的一行汇总值」这种元素",
              (3,)),
    # ----------------------------------------------------------------- style
    Component("panel_background", "style", "panel background fill",
              "the plot area itself carries a tint instead of white; a tinted text box beside "
              "the figure is not this",
              "绘图区带底色，不是白底", False, "`03 §3` 的「图形细节」与「配色」两维都不含面板底色",
              ()),
    Component("hgrid_only", "style", "horizontal grid lines only",
              "horizontal rules across the panel, no vertical ones",
              "只有水平网格线，没有垂直网格线", True, "`03 §3`「图形细节 · 网格线」维的取值",
              ()),
    Component("dense_marks_100plus", "style", "100 or more marks in one figure",
              "count panels times categories times series across the whole figure",
              "单张图 ≥100 个图元", False,
              "`chart_types.md §2` 的 \\|P\\|·\\|S\\| 上限 24 / 20，见 P5",
              (2,)),
    Component("highlighted_category", "style", "one category coloured apart",
              "a single bar, row or series drawn in another colour -- or its axis label set "
              "in bold -- to mark it as the aggregate, the reference, or the subject",
              "某一个类目单独换色或标签加粗（汇总行 / 重点对象）", False,
              "`03 §3` 配色按系列上色，没有单类目高亮这一取值",
              ()),
    Component("icon_category_axis", "style", "icons on the category axis",
              "pictograms stand in for category names",
              "类目轴用图标代替文字", False, "类目轴只渲染 `dim` 的字符串取值",
              (3,)),
    Component("vgrid_only", "style", "vertical grid lines only",
              "vertical rules across the panel, no horizontal ones; common on "
              "horizontal bars",
              "只有垂直网格线，没有水平网格线", True, "`03 §3`「图形细节 · 网格线」维的取值",
              ()),
    Component("dashed_line_series", "style", "line style separates series",
              "one series is dashed and another solid, so line style carries the "
              "series identity as much as colour does",
              "用线型（虚 / 实）区分系列", False, "`03 §3` 的图形细节维有填充纹理，没有线型",
              ()),
)

BY_KEY: dict[str, Component] = {c.key: c for c in VOCABULARY}
KEYS: tuple[str, ...] = tuple(c.key for c in VOCABULARY)

#: The same `ours` question, asked of chart types instead of components.
#:
#: A type the benchmark shows and the condition table has no row for is a gap of
#: exactly the kind the component table lists, and leaving it out made the gap
#: table look complete when a twelfth of the figures were forms we cannot draw.
#: Keys are `schema.CHART_TYPES`; read off `storyline/parsebench_chart/` before
#: any page was looked at, like every other `ours`.
CHART_TYPE_OURS: dict[str, tuple[bool, str]] = {
    "bar": (True, "`chart_types.md` Tier 1 的 `bar`"),
    "grouped_bar": (True, "Tier 1 的 `grouped_bar`"),
    "stacked_bar": (True, "Tier 1 的 `stacked_bar`"),
    "line": (True, "Tier 1 的 `line`"),
    "area": (True, "Tier 1 的 `area`"),
    "pie": (True, "Tier 1 的 `pie`"),
    "donut": (True, "`pie` 的风格变体，同一条件行（见 CLAUDE.md「视觉变体」）"),
    "scatter": (True, "Tier 1 的 `scatter`"),
    "heatmap": (True, "Tier 2 的 `heatmap`"),
    "box": (True, "Tier 2 的 `box`"),
    "histogram": (True, "Tier 1 的 `histogram`"),
    "waterfall": (True, "Tier 1 的 `waterfall`"),
    "funnel": (True, "Tier 1 的 `funnel`"),
    "compound": (True, "Tier 1 的 `compound`"),
    "map": (False, "地理投影不是六族中的任何一族，图元也不在 `§3` 的五种形状里"),
    "radar": (False, "极坐标不在条件表里，`§3` 的五种图元没有极角形状"),
    "treemap": (False, "嵌套矩形的面积编码不在 `§4` 的画法里"),
    "gauge": (False, "仪表盘不在条件表里"),
    "other": (False, "模型报 `other` 时自拟名字，见「新类型」"),
}


def prompt_block() -> str:
    """The vocabulary as the model sees it: one line per key, grouped."""
    lines: list[str] = []
    for group in GROUP_TITLES:
        lines.append(f"[{group}]")
        lines += [f"  {c.key} = {c.name_en}: {c.hint}"
                  for c in VOCABULARY if c.group == group]
    return "\n".join(lines)


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    have = sum(c.ours for c in VOCABULARY)
    scored = sum(bool(c.affects) for c in VOCABULARY)
    print(f"{len(VOCABULARY)} components: {have} we can draw, {len(VOCABULARY) - have} we cannot")
    print(f"{scored} can change a ParseBench step, {len(VOCABULARY) - scored} cannot")
    for group, title in GROUP_TITLES.items():
        keys = [c.key for c in VOCABULARY if c.group == group]
        print(f"  {group:<10} ({title}) {len(keys):2d}: {', '.join(keys)}")


if __name__ == "__main__":
    main()
