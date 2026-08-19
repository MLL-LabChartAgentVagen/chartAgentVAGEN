"""The Chinese the two renderers share.

Rule for every string in this file: a reader who has not read the metric spec must
understand it. `label_unlinked` is not "the label failed to associate", it is
"the number is right but the table never says whose number it is". The English key
stays as the identifier; the Chinese has to carry the meaning on its own.
"""

from __future__ import annotations

#: Failure forms, in the order the report walks them.
KIND_ORDER = ("label_unlinked", "value_off", "row_missing", "unit_mismatch",
              "series_swap", "stack_confusion", "value_absent", "no_table")

#: The short name. Says what went wrong, not what the metric calls it.
KIND_ZH = {
    "label_unlinked": "数字对，但表里说不清这个数字是谁的",
    "value_off": "数字读错了",
    "row_missing": "有个键压根没写进表",
    "unit_mismatch": "数字写在了错的量级上",
    "series_swap": "取了旁边一根柱子的数",
    "stack_confusion": "读的是柱顶累计，不是这一段",
    "value_absent": "键都在，就是没写这个数",
    "no_table": "整页没输出表",
}

#: One more sentence, still plain. This is what the card's subtitle prints.
KIND_NOTE = {
    "label_unlinked":
        "表里确实有这个数。但它那一行、那一列、那个表头，没有一个写着规则要的键——"
        "所以判分程序不知道这个数属于谁，判 0。",
    "value_off":
        "键指得对，格子也找得到，就是格子里的数与图上的真值差太远，超出了这个点的容差。",
    "row_missing":
        "某个键（系列名、面板名、图号）在整张表里一个字都没有。"
        "它通常只画在图例、线端或图题上，解析器没把它写成表的一部分。",
    "unit_mismatch":
        "同一个数写成了另一个量级。轴上写 101、图题写 BILLIONS，解析器写成 $101B——"
        "判分程序把 B 读成 ×10⁹，于是 101 和 1,010 亿对不上。",
    "value_absent":
        "所有键都在表里，但没有任何一格放着这个数。这个图元被跳过了。",
    "no_table":
        "整页输出连一张表都没有。判定第一步直接 0 分，正文里把数写得再准也不算。",
    "series_swap": "写下的数正好是同页另一个点的值，两个点只差一个键。",
    "stack_confusion": "写下的数等于本段加上同类目的另一段，读的是柱顶不是分段。",
}

#: What the pipeline would have to be able to do. Plain, and short enough for a chip.
POINTS_AT = {
    "label_unlinked": "导出成一行一个值、键写全（P3 · P2）",
    "value_off": "记下每个图元能读到多准，并且能画更密的图（P1 · P5）",
    "row_missing": "图号 / 面板名 / 系列名要能写进键（P7 · P2）",
    "unit_mismatch": "单位写在哪、刻度怎么写，要能调（P6）",
    "series_swap": "图例绑定：颜色要对得上系列名（新）",
    "stack_confusion": "分段值与累计值分开记（P1）",
    "value_absent": "太密的图元要么画得开，要么标出来读不了（P1 · P5）",
    "no_table": "输出格式的问题，不是看不看得懂图",
}

HOME_ZH = {
    "in_a_table_but_not_addressing": "就在同一张表里，只是不在这个数的行 / 列 / 表头上",
    "in_another_table_only": "写在了另一张表里",
    "plain_text_only": "在页面上，但只是一句普通正文",
    "absent_from_the_output": "整页输出里找不到这个键",
    "emphasised_after_the_table": "是粗体 / 标题，但排在表后面（判分只看表前面的）",
    "emphasised_before_a_table": "在表前面且是粗体 / 标题（这一条判分本该认）",
}

HOME_ORDER = ("in_a_table_but_not_addressing", "in_another_table_only",
              "plain_text_only", "absent_from_the_output",
              "emphasised_after_the_table", "emphasised_before_a_table")

FAMILY_ZH = {"addressing": "键对不上", "reading": "数读错了"}

PRINTED_ZH = {"all": "全部写出", "some": "部分写出", "none": "一个不写", "": "未记录"}

PLACEMENT_ZH = {"above": "图上方", "below": "图下方", "beside": "与图并排",
                "inside": "绘图区内", "none": "无标题", "": "未记录"}

#: Component keys, in the words a reader can picture.
COMPONENT_ZH = {
    "right_side_y_axis": "值轴画在右边",
    "legend_beside_plot": "图例竖在图的左右侧",
    "annotation_callout": "图里有批注框 / 引线说明",
    "reference_line": "图里有参考线（目标值、平均线）",
    "shared_legend": "多个面板共用一个图例",
    "nonstandard_time_ticks": "时间刻度写法特别（2015/2016、1Q-24）",
    "negative_values": "有负值，零线在中间",
    "axis_title_below_plot": "轴标题写在图下方",
    "sparse_time_ticks": "时间轴隔几格才标一个",
    "per_panel_axis_range": "每个面板的轴范围不一样",
    "side_text_bullets": "图旁边另有一栏文字",
    "rotated_axis_title": "轴标题是竖排的",
    "stacked_bar": "堆叠柱",
    "dense_marks_100plus": "图元超过一百个",
    "color_encodes_extra_attribute": "颜色编码的是第三个变量",
    "dual_axis": "左右两个值轴",
    "small_multiples_4": "四个小倍数面板",
    "mixed_marks": "柱和线混在一张图里",
    "rebased_index_values": "指数化数值（2011 = 100）",
    "vgrid_only": "只有竖网格线",
    "hgrid_only": "只有横网格线",
    "two_level_x_ticks": "类目轴分两层",
    "panel_title_per_panel": "每个面板各有标题",
    "unit_in_axis_or_title": "单位只写在轴标题 / 图题里",
    "source_note_lines": "图下方有 note / source 行",
    "rotated_x_ticks": "类目标签是斜的",
    "per_panel_legend": "每个面板各有图例",
    "tick_marker_as_series": "用刻度记号当一个系列",
    "inline_series_labels": "系列名写在线的旁边",
    "subtitle_above_plot": "图题分成多行",
    "shaded_band": "图里有阴影区间带",
    "footnote_marker": "标签上带脚注号",
    "legend_below_plot": "图例在图下方",
    "legend_above_plot": "图例在图上方",
    "highlighted_category": "某一个类目单独换色",
    "wrapped_category_labels": "类目标签换行",
    "abbrev_category_axis": "类目用缩写（IRL、DEU）",
    "grouped_bar": "分组柱",
    "horizontal_bars": "横向条形",
    "panel_background": "绘图区有底色",
    "missing_value_marker": "缺失值有专门标记",
    "axis_title_above_axis": "轴标题写在轴正上方",
}


def component_zh(key: str) -> str:
    return COMPONENT_ZH.get(key, key.replace("_", " "))
