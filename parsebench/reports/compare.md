# 三家并排：全部数字

程序写的。100 页 × 3 家，外加两条控制。**这一份没有结论**——结论在 [INDEX.md](INDEX.md)，逐页的原始并排在 [pages/](pages/)。

## 1 · 缺口表

基准里有、而 `storyline/parsebench_chart/` 没有定义的东西。三家各报各的页数，永远不合并；`affects` 与「我们画得出」是看页面之前按定义定死的。

### 组件

| key | 中文名 | opus-5 页数 | gpt-5.6-sol 页数 | gemini-3.1-pro 页数 | 一致/两家/一家 | affects | 文档数（最多一家） | 我们画得出 |
|---|---|---|---|---|---|---|---|---|
| `source_note_lines` | source / note 行在图下方 | 88 | 87 | 81 | 81/6/1 | — | 40 | 是 |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | 85 | 74 | 43 | 43/30/13 | — | 39 | 否 |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | 55 | 50 | 64 | 43/15/10 | — | 30 | 是 |
| `legend_below_plot` | 图例在绘图区下方 | 48 | 48 | 48 | 47/1/1 | — | 24 | 是 |
| `rotated_x_ticks` | x 刻度标签旋转 | 32 | 32 | 32 | 32/0/0 | — | 14 | 是 |
| `mixed_marks` | 同面板混合图元（bar + line） | 29 | 31 | 28 | 26/3/4 | 2 | 16 | 是 |
| `rotated_axis_title` | 轴标题竖排 | 30 | 30 | 28 | 28/2/0 | — | 13 | 是 |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | 29 | 29 | 28 | 26/3/2 | — | 15 | 否 |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | 30 | 31 | 25 | 24/4/6 | 4 | 16 | 是 |
| `negative_values` | 负值 / 零线居中的分叉条 | 27 | 26 | 26 | 26/0/1 | 2 | 14 | 否 |
| `multi_figure_page` | 一页多张独立图，各自有图号 | 31 | 24 | 23 | 19/9/3 | 1,3 | 19 | 是 |
| `stacked_bar` | 堆叠条 | 25 | 25 | 18 | 18/7/0 | 2 | 18 | 是 |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | 25 | 29 | 11 | 11/14/4 | — | 15 | 否 |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | 22 | 23 | 19 | 17/5/3 | 2 | 14 | 否 |
| `horizontal_bars` | 横向条形（类目在 y 轴） | 20 | 20 | 20 | 20/0/0 | — | 10 | 否 |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | 20 | 20 | 20 | 19/1/1 | — | 10 | 是 |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | 22 | 20 | 18 | 18/2/2 | 3 | 12 | 是 |
| `footnote_marker` | 标题或标签里的脚注上标 | 32 | 13 | 12 | 12/1/19 | 3 | 20 | 否 |
| `grouped_bar` | 分组条 | 19 | 19 | 18 | 17/2/1 | 3 | 13 | 是 |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | 23 | 17 | 16 | 13/5/7 | — | 11 | 否 |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | 31 | 15 | 9 | 9/6/16 | 3 | 16 | 否 |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | 24 | 16 | 14 | 14/2/8 | 1 | 15 | 否 |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | 22 | 21 | 10 | 10/8/7 | 3 | 14 | 是 |
| `value_label_inside` | 数值标签写在图元内部 | 19 | 17 | 16 | 16/1/2 | 2 | 13 | 是 |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | 19 | 17 | 15 | 15/2/2 | 2 | 12 | 否 |
| `panel_background` | 绘图区带底色，不是白底 | 19 | 18 | 13 | 12/6/2 | — | 11 | 否 |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | 17 | 16 | 14 | 13/4/0 | — | 5 | 否 |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | 20 | 13 | 12 | 9/4/10 | 3 | 14 | 否 |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | 15 | 16 | 12 | 10/3/7 | 3 | 8 | 否 |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | 17 | 9 | 14 | 9/5/3 | — | 11 | 否 |
| `no_value_axis` | 没有值轴刻度，只有基线 | 18 | 11 | 11 | 11/0/7 | 2 | 11 | 否 |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | 16 | 12 | 12 | 11/1/5 | 2 | 9 | 是 |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | 20 | 12 | 7 | 7/4/10 | 3 | 12 | 是 |
| `shared_legend` | 跨面板共享图例 | 12 | 12 | 12 | 10/2/2 | 3 | 10 | 是 |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | 14 | 11 | 9 | 6/7/2 | 2 | 12 | 否 |
| `pct_stacked` | 百分比堆叠（归一到 100%） | 11 | 11 | 11 | 11/0/0 | 2 | 7 | 否 |
| `legend_inside_plot` | 图例画在绘图区内部 | 14 | 11 | 7 | 7/4/3 | — | 9 | 否 |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | 11 | 10 | 9 | 8/3/0 | — | 6 | 否 |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | 9 | 10 | 10 | 7/4/0 | 3 | 6 | 否 |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | 10 | 9 | 9 | 9/0/1 | — | 9 | 是 |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | 13 | 7 | 6 | 5/2/7 | 2,3 | 7 | 否 |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | 8 | 8 | 10 | 5/3/5 | — | 7 | 是 |
| `dual_axis` | 双 y 轴，同面板两个量纲 | 9 | 8 | 8 | 8/0/1 | 2 | 7 | 是 |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | 9 | 8 | 7 | 7/1/1 | 3 | 5 | 否 |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | 11 | 5 | 7 | 5/2/4 | — | 6 | 否 |
| `per_panel_legend` | 每个面板各有一个图例 | 8 | 8 | 6 | 6/1/2 | 3 | 5 | 是 |
| `axis_title_below_plot` | 值轴标题写在图下方 | 8 | 8 | 5 | 4/2/5 | — | 5 | 否 |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | 8 | 7 | 6 | 6/1/1 | — | 6 | 否 |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | 6 | 5 | 5 | 4/2/0 | 1 | 6 | 是 |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | 6 | 5 | 4 | 4/1/1 | 1 | 5 | 是 |
| `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | 7 | 4 | 4 | 4/0/3 | 3 | 4 | 否 |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | 10 | 3 | 0 | 0/2/9 | 2 | 9 | 否 |
| `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | 4 | 1 | 1 | 1/0/3 | 1 | 4 | 否 |
| `shared_axis` | 跨面板共享坐标轴 | 3 | 1 | 2 | 1/0/3 | 2 | 3 | 是 |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | 2 | 2 | 2 | 2/0/0 | 3 | 2 | 否 |
| `range_connector_line` | 每个类目两个点用线段连成区间（哑铃图 / 区间图） | 3 | 1 | 1 | 1/0/2 | 2,3 | 3 | 否 |
| `right_side_y_axis` | 唯一的值轴画在右侧 | 2 | 1 | 1 | 1/0/1 | — | 2 | 否 |
| `error_bars` | 误差棒 / 置信带 | 1 | 1 | 1 | 0/1/1 | — | 1 | 否 |
| `icon_category_axis` | 类目轴用图标代替文字 | 2 | 0 | 1 | 0/1/1 | 3 | 1 | 否 |
| `step_line_series` | 阶梯线（水平段 + 垂直跳变），不是直连折线 | 1 | 1 | 1 | 1/0/0 | 2 | 1 | 否 |
| `total_row_below_axis` | 轴下方一行合计值，与类目对齐 | 2 | 0 | 0 | 0/0/2 | 3 | 2 | 否 |

### 类型

| 类型 | opus-5 图数 | gpt-5.6-sol 图数 | gemini-3.1-pro 图数 | 条件表有这一族 |
|---|---|---|---|---|
| `line` | 37 | 36 | 36 | 是 |
| `stacked_bar` | 27 | 21 | 28 | 是 |
| `compound` | 22 | 32 | 5 | 是 |
| `bar` | 17 | 14 | 23 | 是 |
| `grouped_bar` | 18 | 16 | 19 | 是 |
| `other` | 11 | 12 | 17 | 否 |
| `pie` | 5 | 4 | 4 | 是 |
| `area` | 1 | 1 | 1 | 是 |
| `scatter` | 1 | 1 | 1 | 是 |
| `donut` | 1 | 1 | 1 | 是 |
| `treemap` | 1 | 1 | 1 | 否 |

### 词表外的自拟名字（出现 ≥2 页的）

| 自拟名字 | 出现页数 | 几家报过 | affects | 一条证据 |
|---|---|---|---|---|
| `marker_shape_encodes_series` | 7 | 2 | 3 | Diamonds identify mean gaps while triangles identify median gaps in the legend and plots. |
| `unit_in_tick_labels` | 6 | 1 | 2,4 | Left-axis ticks read “0%”, “20%”, through “100%”; no separate unit title appears. |
| `point_marker_as_series` | 3 | 1 | 2,3 | Diamond markers are identified in the legend as “Score in 2018”. |
| `legend_band_background` | 2 | 1 | — | each legend row sits inside a full-width light grey band above the plot |
| `legend_mixes_colour_groups_and_marker_series` | 2 | 1 | 3 | one legend block holds four colour swatches (performance groups) plus '◆ Score in 2018' and '| Score in 2024' |
| `narrative_data_box` | 2 | 1 | 1,3,4 | “Box 3” heads a blue panel containing seven country paragraphs with embedded values. |
| `numbered_text_box` | 2 | 2 | 1,4 | Box 5 behaves as a figure heading but wraps body text |
| `floating_range_bar` | 2 | 2 | 2,3 | Panel A green rectangles span quartile to quartile, not anchored to the zero baseline |
| `diverging_stacked_bar` | 2 | 2 | 2,3 | Panel B stacks contributions separately above and below the heavy zero line. |
| `value_axis_on_top` | 2 | 1 | 2,3 | the 0%-100% tick row is drawn above the first bar, not below the last |
| `zebra_striped_table_rows` | 2 | 1 | 1 | alternating grey/white row fills across `Technology`, `Strategy`, `People & Change` |
| `unnumbered_figure_heading` | 2 | 1 | 3,4 | blue two-line heading under a rule, no 'Figure n' anywhere on the page |
| `interpretation_paragraph_below_figure` | 2 | 2 | 4 | bold 'Interpretation.' opens an eight-line prose block between the legends and the body text |
| `interpretation_caption_block` | 2 | 1 | 4 | A substantial paragraph beginning “Interpretation.” sits between the legends and body text. |
| `category_group_separator_rules` | 2 | 2 | 3 | Panel B: vertical rules below the axis split Gender | Age | Occupation | Education | Urbanisation |
| `bidirectional_gridlines` | 2 | 1 | 2,3 | Both plots draw horizontal and vertical gridlines across each category slot. |
| `unit_in_value_labels` | 2 | 1 | 2,4 | Every segment label carries a percent sign, including “51%” and “25%”. |
| `title_in_filled_banner` | 2 | 1 | 3,4 | "Figure B.6: Growing number of concerns about SPS and TBT measures..." white text in a blue filled bar above plot |

## 2 · 基准长什么样

描述，没有待办。每一格三家并列。

### 数值印不印

| 数值印不印 | opus-5 | gpt-5.6-sol | gemini-3.1-pro |
|---|---|---|---|
| none | 85 | 83 | 83 |
| all | 48 | 46 | 42 |
| some | 8 | 10 | 11 |

### 稠密度档

| 稠密度档 | opus-5 | gpt-5.6-sol | gemini-3.1-pro |
|---|---|---|---|
| ≤20 | 52 | 47 | 49 |
| 21–60 | 44 | 51 | 47 |
| 61–150 | 32 | 28 | 27 |
| 151–400 | 6 | 7 | 8 |
| >400 | 6 | 6 | 5 |
| 未报 | 1 | 0 | 0 |

### 标题位置

| 标题位置 | opus-5 | gpt-5.6-sol | gemini-3.1-pro |
|---|---|---|---|
| above | 129 | 126 | 123 |
| below | 7 | 9 | 9 |
| beside | 3 | 3 | 3 |
| none | 2 | 1 | 1 |

### 图号有无

| 图号有无 | opus-5 | gpt-5.6-sol | gemini-3.1-pro |
|---|---|---|---|
| 有图号 | 83 | 83 | 81 |
| 无图号 | 58 | 56 | 55 |

### 卡在哪一步

| 步 | opus-5 报的页数 | gpt-5.6-sol 报的页数 | gemini-3.1-pro 报的页数 | 这批页在失败运行里实际卡住的步（按页多数） |
|---|---|---|---|---|
| 1 · there is no table at all | 3 | 16 | 11 | 0 |
| 2 · the value cannot be read to the tolerance | 67 | 61 | 65 | 16 |
| 3 · the labels cannot be associated with the cell | 30 | 22 | 22 | 36 |
| 4 · the context outside the table is not bold or a heading | 0 | 1 | 2 | 0 |

## 3 · 失败

运行 `ppdoclayoutv3_lean_qwen`（Qwen/Qwen3.8-27B-FP8），568 页 / 4864 个抽查点，按页平均 **82.8%**，896 个失败。形态由程序算，机制由三家归因。

### 失败形态（全部失败上算，不抽样）

| 形态 | 定义 | 个数 | 占失败 | 失联键的去向（前三） |
|---|---|---|---|---|
| `label_unlinked` | the value is in a table, but a label will not associate with its cell | 599 | 66.8% | in_a_table_but_not_addressing 627；plain_text_only 57；absent_from_the_output 46 |
| `value_off` | the addressed cell holds a different number | 196 | 21.9% | — |
| `row_missing` | one of the addressing labels is nowhere in the output | 48 | 5.4% | — |
| `unit_mismatch` | the addressed cell holds the same number at another scale | 36 | 4.0% | — |
| `value_absent` | the labels are all there, but that value was never written | 17 | 1.9% | — |

寻址失败（`label_unlinked` + `row_missing`）全部改对的上界：按页平均 82.8% → **95.4%**。

### 单变量通过率

前两条的分母是全部 568 页，后三条只能在三家描述过的样本页上算，n 因此小得多。

| 自变量 | 分母 | 档 | 通过率 | n | 95% 区间 |
|---|---|---|---|---|---|
| 定位需要几个键 | 全部 568 页 | 1 | 94.4% | 268 | [91.0%, 96.6%] |
| 定位需要几个键 | 全部 568 页 | 2 | 83.3% | 3847 | [82.0%, 84.4%] |
| 定位需要几个键 | 全部 568 页 | 3 | 69.0% | 715 | [65.5%, 72.2%] |
| 定位需要几个键 | 全部 568 页 | 4 | 55.9% | 34 | [39.5%, 71.1%] |
| 整页文字量 | 全部 568 页 | ≤240 词 | 79.2% | 1237 | [76.9%, 81.4%] |
| 整页文字量 | 全部 568 页 | 241–360 词 | 82.6% | 1231 | [80.4%, 84.6%] |
| 整页文字量 | 全部 568 页 | 361–500 词 | 84.7% | 1248 | [82.6%, 86.6%] |
| 整页文字量 | 全部 568 页 | >500 词 | 79.6% | 1148 | [77.2%, 81.8%] |
| 图元个数 | 抽样 100 页 · 三家里两家同档 | ≤20 | 91.9% | 247 | [87.8%, 94.7%] |
| 图元个数 | 抽样 100 页 · 三家里两家同档 | 21–60 | 83.9% | 323 | [79.5%, 87.5%] |
| 图元个数 | 抽样 100 页 · 三家里两家同档 | 61–150 | 75.5% | 233 | [69.6%, 80.6%] |
| 图元个数 | 抽样 100 页 · 三家里两家同档 | 151–400 | 87.0% | 46 | [74.3%, 93.9%] |
| 图元个数 | 抽样 100 页 · 三家里两家同档 | >400 | 69.8% | 43 | [54.9%, 81.4%] |
| 数值是否印在图上 | 抽样 100 页 · 三家里两家同值 | all | 99.0% | 204 | [96.5%, 99.7%] |
| 数值是否印在图上 | 抽样 100 页 · 三家里两家同值 | some | 63.9% | 36 | [47.6%, 77.5%] |
| 数值是否印在图上 | 抽样 100 页 · 三家里两家同值 | none | 79.6% | 652 | [76.3%, 82.5%] |
| 面板数 | 抽样 100 页 · 三家里两家同值 | 1 面板 | 83.8% | 634 | [80.7%, 86.4%] |
| 面板数 | 抽样 100 页 · 三家里两家同值 | 2 面板 | 89.9% | 169 | [84.5%, 93.6%] |
| 面板数 | 抽样 100 页 · 三家里两家同值 | 3 面板 | 75.0% | 40 | [59.8%, 85.8%] |

### 控制组（图上一个数值都不写的点）内，各组件的通过率差

控制组是样本页里数值一个不写的点。只有「区间不重叠」为「是」的行值得读。

| 组件 | 出现页数 | 有它的通过率 | n | 没有它的通过率 | n | 差 | 区间不重叠 |
|---|---|---|---|---|---|---|---|
| `horizontal_bars` | 20 | 57.1% | 49 | 81.4% | 603 | -24.3% | 是 |
| `vgrid_only` | 8 | 57.1% | 49 | 81.4% | 603 | -24.3% | 是 |
| `tick_marker_as_series` | 7 | 64.4% | 45 | 80.7% | 607 | -16.3% | 是 |
| `axis_title_below_plot` | 6 | 65.3% | 49 | 80.8% | 603 | -15.5% | 是 |
| `panel_background` | 18 | 68.1% | 116 | 82.1% | 536 | -14.0% | 是 |
| `shared_legend` | 12 | 68.8% | 77 | 81.0% | 575 | -12.2% | 否 |
| `negative_values` | 26 | 72.0% | 207 | 83.2% | 445 | -11.2% | 是 |
| `legend_above_plot` | 20 | 72.9% | 133 | 81.3% | 519 | -8.4% | 否 |
| `stacked_bar` | 25 | 73.4% | 139 | 81.3% | 513 | -7.9% | 否 |
| `nonstandard_time_ticks` | 13 | 73.2% | 108 | 80.9% | 544 | -7.7% | 否 |
| `panel_title_per_panel` | 28 | 74.9% | 211 | 81.9% | 441 | -7.0% | 否 |
| `color_encodes_extra_attribute` | 13 | 74.4% | 129 | 80.9% | 523 | -6.5% | 否 |
| `side_text_bullets` | 16 | 74.0% | 50 | 80.1% | 602 | -6.1% | 否 |
| `highlighted_category` | 18 | 75.5% | 159 | 80.9% | 493 | -5.5% | 否 |
| `dense_marks_100plus` | 17 | 75.5% | 151 | 80.8% | 501 | -5.3% | 否 |
| `rotated_axis_title` | 30 | 76.0% | 208 | 81.3% | 444 | -5.3% | 否 |
| `annotation_callout` | 14 | 75.5% | 98 | 80.3% | 554 | -4.8% | 否 |
| `dual_axis` | 8 | 76.3% | 59 | 79.9% | 593 | -3.7% | 否 |
| `rotated_x_ticks` | 32 | 77.7% | 296 | 81.2% | 356 | -3.5% | 否 |
| `shaded_band` | 7 | 76.9% | 65 | 79.9% | 587 | -3.0% | 否 |
| `reference_line` | 25 | 77.8% | 180 | 80.3% | 472 | -2.5% | 否 |
| `mixed_marks` | 29 | 78.0% | 227 | 80.5% | 425 | -2.5% | 否 |
| `per_panel_axis_range` | 12 | 78.1% | 105 | 79.9% | 547 | -1.8% | 否 |
| `small_multiples_4` | 18 | 78.4% | 134 | 79.9% | 518 | -1.6% | 否 |
| `unit_in_axis_or_title` | 73 | 79.3% | 507 | 80.7% | 145 | -1.4% | 否 |
| `rebased_index_values` | 11 | 79.8% | 109 | 79.6% | 543 | 0.3% | 否 |
| `wrapped_category_labels` | 15 | 80.0% | 45 | 79.6% | 607 | 0.4% | 否 |
| `abbrev_category_axis` | 11 | 80.5% | 87 | 79.5% | 565 | 1.0% | 否 |
| `legend_beside_plot` | 9 | 80.8% | 26 | 79.5% | 626 | 1.2% | 否 |
| `legend_below_plot` | 48 | 80.4% | 311 | 78.9% | 341 | 1.5% | 否 |
| `two_level_x_ticks` | 8 | 81.0% | 79 | 79.4% | 573 | 1.6% | 否 |
| `footnote_marker` | 13 | 81.2% | 80 | 79.4% | 572 | 1.9% | 否 |
| `source_note_lines` | 87 | 80.3% | 563 | 75.3% | 89 | 5.0% | 否 |
| `sparse_time_ticks` | 20 | 83.4% | 163 | 78.3% | 489 | 5.1% | 否 |
| `grouped_bar` | 19 | 85.5% | 69 | 78.9% | 583 | 6.6% | 否 |
| `dashed_line_series` | 7 | 86.4% | 59 | 78.9% | 593 | 7.5% | 否 |
| `data_link_below_figure` | 17 | 85.4% | 158 | 77.7% | 494 | 7.7% | 否 |
| `inline_series_labels` | 11 | 88.6% | 70 | 78.5% | 582 | 10.1% | 否 |
| `axis_title_above_axis` | 29 | 86.1% | 258 | 75.4% | 394 | 10.7% | 是 |
| `multi_figure_page` | 28 | 88.4% | 129 | 77.4% | 523 | 10.9% | 是 |
| `legend_inside_plot` | 11 | 90.7% | 86 | 77.9% | 566 | 12.8% | 是 |
| `data_table_as_figure` | 5 | 92.3% | 26 | 79.1% | 626 | 13.2% | 否 |
| `hgrid_only` | 58 | 84.4% | 437 | 69.8% | 215 | 14.7% | 是 |
| `unit_in_series_name` | 4 | 94.4% | 36 | 78.7% | 616 | 15.7% | 是 |
| `axis_starts_above_zero` | 13 | 92.7% | 110 | 76.9% | 542 | 15.8% | 是 |
| `per_panel_legend` | 7 | 93.8% | 65 | 78.0% | 587 | 15.8% | 是 |
| `heterogeneous_panel_types` | 6 | 96.7% | 30 | 78.8% | 622 | 17.9% | 是 |

### 机制

抽样 50 条，三家全同意 32 条、两家同意 13 条、三家各说各的 5 条。「折算到全运行」= 每种形态内的机制占比 × 该形态在全部 896 个失败里的个数，因为抽样是每形态等量抽，不是按比例抽。

| 机制 | 归入哪一步 | opus-5 条数 | gpt-5.6-sol 条数 | gemini-3.1-pro 条数 | 两家以上同意的条数 | 折算到全运行的占比 | 折算条数 | 一个实例 |
|---|---|---|---|---|---|---|---|---|
| `key_off_the_value_row` | 3 · the labels cannot be associated with the cell | 3 | 4 | 7 | 4 | 26.7% | 240 | `label_unlinked-01` / ADL_Future_of_automotive_mobility_2024_1_p13 |
| `key_only_in_another_table` | 3 · the labels cannot be associated with the cell | 2 | 1 | 1 | 1 | 6.7% | 60 | `label_unlinked-10` / us-global-outsourcing-survey-2024-report_p14 |
| `key_only_in_prose` | 3 · the labels cannot be associated with the cell | 4 | 4 | 7 | 5 | 15.0% | 134 | `label_unlinked-03` / aviva-plc-annual-report-and-accounts-2024_p143 |
| `series_identified_by_colour` | 3 · the labels cannot be associated with the cell | 2 | 1 | 0 | 1 | 6.7% | 60 | `label_unlinked-06` / b3cd580a-3656-44ed-838a-5f2996ff6fc9_p49 |
| `panel_name_dropped` | 3 · the labels cannot be associated with the cell | 1 | 3 | 1 | 1 | 0.5% | 5 | `row_missing-13` / employment_and_social_developments_in_europe_esde_2024_report_p41 |
| `value_read_off_wrong_mark` | 2 · the value cannot be read to the tolerance | 4 | 5 | 1 | 2 | 8.9% | 80 | `label_unlinked-09` / tdr2023ch1_en_p19 |
| `value_interpolated_off_axis` | 2 · the value cannot be read to the tolerance | 13 | 11 | 14 | 12 | 12.3% | 110 | `value_absent-32` / 2025-EIS_p47 |
| `stacked_total_vs_segment` | 2 · the value cannot be read to the tolerance | 1 | 0 | 1 | 1 | 2.2% | 20 | `value_off-46` / TRS241_Web_p525 |
| `scale_word_ignored` | 2 · the value cannot be read to the tolerance | 10 | 10 | 6 | 9 | 3.6% | 32 | `unit_mismatch-21` / 2025-EIS_p43 |
| `figure_not_transcribed` | 1 · there is no table at all | 4 | 3 | 2 | 3 | 7.8% | 70 | `label_unlinked-08` / pdf_f270146f8ca7_p25 |
| `other` | 映不回四步 | 6 | 8 | 10 | 6 | 2.2% | 20 | `row_missing-18` / semiconductor_sector_study_p22 |

**三家各说各的，agent 逐条裁决**（裁决在 [`verdicts.json`](../data/analysis/verdicts.json)，模型的原答案不改）

| case | 页 | 形态 | 三家各自的机制 | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `row_missing-15` | mts0625_p6 | `row_missing` | opus-5: `figure_not_transcribed`；gpt-5.6-sol: `panel_name_dropped`；gemini-3.1-pro: `key_only_in_prose` | key_only_in_prose | 规则的四个键里有一个是图号 `Figure 3.`，它写在图题里，任何表都不会有这一格。opus 的 figure_not_transcribed 不成立（页面有表，只是另一张累计表），gpt 的 panel_name_dropped 不成立（这一页没有面板）。这一条同时是 P7 与 P3 的交点：图号被当成定位键。 |
| `unit_mismatch-28` | ac8b3538-en_p161 | `unit_mismatch` | opus-5: `value_read_off_wrong_mark`；gpt-5.6-sol: `scale_word_ignored`；gemini-3.1-pro: `key_off_the_value_row` | value_interpolated_off_axis | [Age] 行解析出 -0.008，真值 -0.007，容差 0.1，差 12.5%，刚好越界；这一页数值不印在图上（need_estimate），是对轴内插读短了。三家给的三个机制都不对。**另记**：程序判的形态 `unit_mismatch` 在这一条上是误判——宽松标签匹配把 `Difference` 行的 -0.066 当成了被寻址的格。 |
| `value_off-42` | MonthlyTreasuryStatement_202509_p6 | `value_off` | opus-5: `value_interpolated_off_axis`；gpt-5.6-sol: `value_read_off_wrong_mark`；gemini-3.1-pro: `key_off_the_value_row` | value_interpolated_off_axis | Sep 2024 的 Deficit/Surplus 真值 100，解析器写 80，容差 0.1，差 20%；这一页不印数值。gemini 的 key_off_the_value_row 不成立（三个键都在，且指向的正是这一格）；gpt 的依据来自程序那一行「addressed cell holds 2025」，那是键本身是数字造成的诊断误差，不是机制。 |
| `value_off-44` | Renewables2025_1_p48 | `value_off` | opus-5: `value_read_off_wrong_mark`；gpt-5.6-sol: `other`；gemini-3.1-pro: `value_interpolated_off_axis` | value_interpolated_off_axis | 真值 57，解析器写 56，容差 0.01——**计数量在 1% 容差下等于要求逐个数对**。相邻行是 53 与 4，不是 56，所以不是读到邻近图元。 |
| `value_off-45` | Renewables2025_1_p48 | `value_off` | opus-5: `value_read_off_wrong_mark`；gpt-5.6-sol: `other`；gemini-3.1-pro: `value_interpolated_off_axis` | value_interpolated_off_axis | 真值 14，解析器写 13，同上，差一个。这两条一起说明 ε 必须与规则自己的容差比：整数计数的容差 1% 意味着 ε 必须为 0。 |

## 4 · 能不能信

### 调用口径

| 模型 | 控制 | effort | dpi | 调用次数 | 输入 token | 输出 token | 累计用时 | 空答案重问 | 走哪条通路 |
|---|---|---|---|---|---|---|---|---|---|
| opus-5 | — | high | 150 | 100 | 1,384,966 | 643,914 | 8183s | 0 | direct 100 |
| gpt-5.6-sol | — | high | 150 | 100 | 890,545 | 1,277,500 | 25454s | 0 | direct 78、openrouter 22 |
| gemini-3.1-pro | — | high | 150 | 100 | 532,648 | 1,062,218 | 7813s | 0 | direct 100 |
| gemini-3.1-pro | no_vocab | high | 150 | 100 | 317,548 | 780,545 | 5759s | 0 | direct 100 |
| gemini-3.1-pro | repeat | high | 150 | 100 | 532,648 | 1,053,531 | 7782s | 0 | direct 100 |

### 判分：预测的定位键 vs 规则的真实标签

这是十个对齐量里**唯一可核**的一个：值送进了 prompt、标签没有。

| 模型 | 落位的值数 | 抽查点数 | 预测对的数 | 命中率 |
|---|---|---|---|---|
| opus-5 | 890 | 894 | 617 | 69.0% |
| gpt-5.6-sol | 874 | 893 | 630 | 70.5% |
| gemini-3.1-pro | 884 | 894 | 572 | 64.0% |

**漏掉的是哪一个标签**（三家合计，一行是一个标签）

| 标签位置 | opus-5 漏掉几次 | gpt-5.6-sol 漏掉几次 | gemini-3.1-pro 漏掉几次 |
|---|---|---|---|
| 第 1 个标签 | 178 | 173 | 201 |
| 第 2 个标签 | 183 | 164 | 197 |
| 第 3 个标签 | 33 | 35 | 41 |

| 它是规则的第几个标签 | 标签 | 三家合计漏掉几次 | 报对几次 | 漏掉率 |
|---|---|---|---|---|
| 2 | `Fundraisings - Amount received by the company in its latest fundraising (GBP)` | 20 | 1 | 95.2% |
| 3 | `Technology manufacturing` | 18 | 0 | 100.0% |
| 4 | `Industrial market economies` | 18 | 6 | 75.0% |
| 2 | `% of Intrusions` | 17 | 1 | 94.4% |
| 1 | `2021` | 13 | 38 | 25.5% |
| 2 | `2023` | 13 | 50 | 20.6% |
| 3 | `Average Occupancy Rates` | 13 | 2 | 86.7% |
| 1 | `2020` | 12 | 27 | 30.8% |
| 3 | `Fossil fuel supply` | 12 | 0 | 100.0% |
| 2 | `Price-to-book valuation spreads` | 12 | 6 | 66.7% |
| 3 | `Q4` | 12 | 6 | 66.7% |
| 3 | `Average Rental Rates` | 12 | 3 | 80.0% |
| 2 | `From 18 to 64 years` | 11 | 4 | 73.3% |
| 1 | `Spain` | 11 | 7 | 61.1% |
| 1 | `2005` | 11 | 7 | 61.1% |
| 2 | `OECD average` | 11 | 4 | 73.3% |
| 1 | `Netherlands` | 10 | 11 | 47.6% |
| 2 | `Average` | 10 | 11 | 47.6% |
| 1 | `2022` | 9 | 53 | 14.5% |
| 1 | `France` | 9 | 27 | 25.0% |

### 一致率

分母是至少一家报过的项，分子是三家一致的项，按页算再平均。**一致不是要最大化的分数**——它只用来把「基准的性质」与「一家模型的读法」分开。

| 量 | 三家一致 | 两家 | 一家 | 冲突 | 一致率（按页平均） |
|---|---|---|---|---|---|
| 组件命中集合 | 809 | 195 | 217 | 0 | 67.1% |
| 图表类型判定 | 96 | 3 | 3 | 40 | 67.9% |
| 数值印不印 | 129 | 4 | 3 | 6 | 93.7% |
| 稠密度档 | 118 | 3 | 3 | 18 | 87.3% |
| 标题 | 132 | 4 | 3 | 3 | 95.5% |
| 卡在哪一步 | 70 | 0 | 0 | 30 | 70.0% |
| 同向两条值轴 | 128 | 4 | 3 | 7 | 93.9% |
| 键分量 | 95 | 2 | 3 | 42 | 67.6% |

### 三家各自的前三名

| 模型 | # | what | 归入哪条 P | affects |
|---|---|---|---|---|
| opus-5 | 1 | `readable` 布尔门（值不印 + 5% 容差）→ 每标记可达精度 | P1 | 2 |
| opus-5 | 2 | 单位位置 / 值标签位置 / 零线三维（`unit_in_axis_or_title`、`no_value_axis`、`value_label_outside`、`negative_values`） | P6 | 2 |
| opus-5 | 3 | 面板维度进键（`panel_title_per_panel`、`small_multiples_4`、`per_panel_axis_range`） | P2 | 2,3 |
| gpt-5.6-sol | 1 | P1：逐标记可达到精度 | P1 | 2 |
| gpt-5.6-sol | 2 | P9：axis_id＋mark_shape 定位键 | P9 | 2,3 |
| gpt-5.6-sol | 3 | P2：panel_key | P2 | 2,3 |
| gemini-3.1-pro | 1 | 读取精度 (value_label_inside) | P1 | 2 |
| gemini-3.1-pro | 2 | 复合图表 (compound) | P2 | 3 |
| gemini-3.1-pro | 3 | 混合标记 (mixed_marks) | P9 | 2,3 |

### 自报 vs 实测

三家 overview 里 `numbers_cited` 的每一条，查它在程序的表里存不存在。77 条里 5 条是带小数的比率或大计数（「可判别」= 是），其中 4 条找得到；其余是小整数，几百个格子里总能撞上一个，找到不算证据。「最接近的一格」按名字相似度猜，模型的答案里没有记它读了哪一格。

| 模型 | claim | 模型自报 | 程序表里有没有这个数 | 可判别 | 最接近的一格 |
|---|---|---|---|---|---|
| opus-5 | 本批页数 | 100 | 找到 | 否 | 抽样 / 页数 |
| opus-5 | 我这列卡在第 2 步的页数 | 67 | 找到 | 否 | 卡在哪一步 / claude-opus-5 / 2 |
| opus-5 | 我这列卡在第 3 步的页数 | 30 | 找到 | 否 | 组件表 `rotated_axis_title` / claude-opus-5 页数 |
| opus-5 | 我这列卡在第 1 步的页数 | 3 | 找到 | 否 | 组件表 `shared_axis` / claude-opus-5 页数 |
| opus-5 | 我这列卡在第 4 步的页数 | 0 | 找到 | 否 | 组件表 `thin_segment_label` / gemini-3.1-pro-preview 页数 |
| opus-5 | 数值一个都不印的图数（none） | 85 | 找到 | 否 | 数值印不印 / claude-opus-5 / none |
| opus-5 | `unit_in_axis_or_title` 页数 | 85 | 找到 | 否 | 组件表 `unit_in_axis_or_title` / claude-opus-5 页数 |
| opus-5 | `negative_values` 页数 | 27 | 找到 | 否 | 组件表 `negative_values` / claude-opus-5 页数 |
| opus-5 | `value_label_outside` 页数 | 22 | 找到 | 否 | 组件表 `value_label_outside` / claude-opus-5 页数 |
| opus-5 | `no_value_axis` 页数 | 18 | 找到 | 否 | 组件表 `no_value_axis` / claude-opus-5 页数 |
| opus-5 | `panel_title_per_panel` 页数 | 30 | 找到 | 否 | 组件表 `panel_title_per_panel` / claude-opus-5 页数 |
| opus-5 | `small_multiples_4` 页数 | 22 | 找到 | 否 | 组件表 `small_multiples_4` / claude-opus-5 页数 |
| opus-5 | `per_panel_axis_range` 页数 | 16 | 找到 | 否 | 组件表 `per_panel_axis_range` / claude-opus-5 页数 |
| opus-5 | `mixed_marks` 页数 | 29 | 找到 | 否 | 组件表 `mixed_marks` / claude-opus-5 页数 |
| opus-5 | 「同向两条值轴」三家冲突页数 | 7 | 找到 | 否 | 一致率表 同向两条值轴 / conflict |
| opus-5 | 残差 `marker_shape_encodes_series` 出现页数 | 7 | 找到 | 否 | 组件表 `unit_in_series_name` / claude-opus-5 页数 |
| opus-5 | `horizontal_bars` 页数 | 20 | 找到 | 否 | 组件表 `horizontal_bars` / claude-opus-5 页数 |
| opus-5 | compound 图数（我 / gpt / gemini） | 22 / 32 / 5 | 找到 | 否 | 类型 / claude-opus-5 / compound |
| opus-5 | 图表类型判定冲突页数 | 40 | 找到 | 否 | 一致率表 图表类型判定 / conflict |
| opus-5 | 标题位置 above 的图数 | 129 | 找到 | 否 | 标题位置 / claude-opus-5 / above |
| opus-5 | 标题位置 below 的图数 | 7 | 找到 | 否 | 标题位置 / claude-opus-5 / below |
| opus-5 | 组件命中集合按页平均一致率 | 67.1% | 找到 | 是 | 一致率表 组件命中集合 / rate |
| opus-5 | 我的定位键命中率 | 69.0% | **没找到** | 否 | — |
| opus-5 | `footnote_marker` 页数（我 / gpt / gemini） | 32 / 13 / 12 | 找到 | 否 | 组件表 `footnote_marker` / claude-opus-5 页数 |
| opus-5 | `wrapped_category_labels` 页数（我 / gpt / gemini） | 31 / 15 / 9 | 找到 | 否 | 组件表 `wrapped_category_labels` / claude-opus-5 页数 |
| opus-5 | 密度 61–150 档页数 | 32 | 找到 | 否 | 组件表 `rotated_x_ticks` / claude-opus-5 页数 |
| opus-5 | 密度 151–400 档页数 | 6 | 找到 | 否 | 组件表 `heterogeneous_panel_types` / claude-opus-5 页数 |
| opus-5 | 密度 >400 档页数 | 6 | 找到 | 否 | 组件表 `heterogeneous_panel_types` / claude-opus-5 页数 |
| opus-5 | `multi_figure_page` 页数 | 31 | 找到 | 否 | 组件表 `multi_figure_page` / claude-opus-5 页数 |
| opus-5 | `side_text_bullets` 页数 | 24 | 找到 | 否 | 组件表 `side_text_bullets` / claude-opus-5 页数 |
| opus-5 | `color_encodes_extra_attribute` 页数 | 15 | 找到 | 否 | 组件表 `color_encodes_extra_attribute` / claude-opus-5 页数 |
| opus-5 | `highlighted_category` 页数 | 23 | 找到 | 否 | 组件表 `highlighted_category` / claude-opus-5 页数 |
| gpt-5.6-sol | 卡在读值步骤的页数 | 61 | 找到 | 否 | 卡在哪一步 / gpt-5.6-sol / 2 |
| gpt-5.6-sol | 卡在标签关联步骤的页数 | 22 | 找到 | 否 | 卡在哪一步 / gpt-5.6-sol / 3 |
| gpt-5.6-sol | 卡在无表步骤的页数 | 16 | 找到 | 否 | 组件表 `side_text_bullets` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 卡在表外上下文步骤的页数 | 1 | 找到 | 否 | 组件表 `missing_value_marker` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 定位键命中率 | 70.5% | 找到 | 是 | 判分表 gpt-5.6-sol / 命中率 |
| gpt-5.6-sol | 预测正确的定位键数 | 630 | 找到 | 是 | 判分表 gpt-5.6-sol / correct |
| gpt-5.6-sol | 定位键抽查点数 | 893 | 找到 | 是 | 判分表 gpt-5.6-sol / points |
| gpt-5.6-sol | 完全不印数值的图数 | 83 | 找到 | 否 | 数值印不印 / gpt-5.6-sol / none |
| gpt-5.6-sol | 全部打印数值的图数 | 46 | 找到 | 否 | 数值印不印 / gpt-5.6-sol / all |
| gpt-5.6-sol | 部分打印数值的图数 | 10 | 找到 | 否 | 数值印不印 / gpt-5.6-sol / some |
| gpt-5.6-sol | 复合图数 | 32 | 找到 | 否 | 组件表 `rotated_x_ticks` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 混合图元页数 | 31 | 找到 | 否 | 组件表 `mixed_marks` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 带面板标题的页数 | 31 | 找到 | 否 | 组件表 `mixed_marks` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 一页多张独立图的页数 | 24 | 找到 | 否 | 组件表 `multi_figure_page` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 二至四个小多图的页数 | 21 | 找到 | 否 | 组件表 `small_multiples_4` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 带侧栏正文的页数 | 16 | 找到 | 否 | 组件表 `side_text_bullets` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 单位位于轴标题或图题的页数 | 74 | 找到 | 否 | 组件表 `unit_in_axis_or_title` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 含负值的页数 | 26 | 找到 | 否 | 组件表 `negative_values` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 外置数值标签页数 | 23 | 找到 | 否 | 组件表 `value_label_outside` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 高密组件的图元阈值 | ≥100 | 找到 | 否 | 调用口径 gpt-5.6-sol / calls |
| gpt-5.6-sol | 单图至少百个图元的页数 | 17 | 找到 | 否 | 组件表 `highlighted_category` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 中高密度档范围 | 151–400 | **没找到** | 否 | — |
| gpt-5.6-sol | 中高密度档图数 | 7 | 找到 | 否 | 稠密度档 / gpt-5.6-sol / 151–400 |
| gpt-5.6-sol | 最高密度档范围 | >400 | **没找到** | 是 | — |
| gpt-5.6-sol | 最高密度档图数 | 6 | 找到 | 否 | 稠密度档 / gpt-5.6-sol / >400 |
| gpt-5.6-sol | 颜色编码第三变量的页数 | 16 | 找到 | 否 | 组件表 `side_text_bullets` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 单类高亮的页数 | 17 | 找到 | 否 | 组件表 `highlighted_category` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 百分比堆叠页数 | 11 | 找到 | 否 | 组件表 `no_value_axis` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 横向条形页数 | 20 | 找到 | 否 | 组件表 `horizontal_bars` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 参考线页数 | 29 | 找到 | 否 | 组件表 `axis_title_above_axis` / gpt-5.6-sol 页数 |
| gpt-5.6-sol | 标题位于图上方的图数 | 126 | 找到 | 否 | 标题位置 / gpt-5.6-sol / above |
| gpt-5.6-sol | 折线图数 | 36 | 找到 | 否 | 类型 / gpt-5.6-sol / line |
| gpt-5.6-sol | 树图数 | 1 | 找到 | 否 | 组件表 `missing_value_marker` / gpt-5.6-sol 页数 |
| gemini-3.1-pro | 抽样评估的页面总数 | 100 | 找到 | 否 | 抽样 / 页数 |
| gemini-3.1-pro | 未印制数值标签的页面数 | 85 | 找到 | 否 | 数值印不印 / claude-opus-5 / none |
| gemini-3.1-pro | 阻断验证的步骤编号 | 2 | 找到 | 否 | 组件表 `axis_title_below_plot` / gemini-3.1-pro-preview 文档数 |
| gemini-3.1-pro | opus-5在第二步阻断的次数 | 67 | 找到 | 否 | 卡在哪一步 / claude-opus-5 / 2 |
| gemini-3.1-pro | 数值验证的误差容限 | 5 | 找到 | 否 | 组件表 `data_link_below_figure` / gemini-3.1-pro-preview 文档数 |
| gemini-3.1-pro | 标签映射步骤编号 | 3 | 找到 | 否 | 组件表 `abbrev_category_axis` / gemini-3.1-pro-preview 文档数 |
| gemini-3.1-pro | 复合图表类型次数 | 22 | 找到 | 否 | 类型 / claude-opus-5 / compound |
| gemini-3.1-pro | 小型多面板命中数 | 22 | 找到 | 否 | 卡在哪一步 / gemini-3.1-pro-preview / 3 |
| gemini-3.1-pro | 混合图元命中数 | 29 | 找到 | 否 | 组件表 `mixed_marks` / claude-opus-5 页数 |
| gemini-3.1-pro | 额外颜色编码次数 | 15 | 找到 | 否 | 组件表 `axis_title_above_axis` / gemini-3.1-pro-preview 文档数 |
| gemini-3.1-pro | 标签折行组件命中数 | 31 | 找到 | 否 | 组件表 `mixed_marks` / gpt-5.6-sol 页数 |
| gemini-3.1-pro | 负值结构命中次数 | 27 | 找到 | 否 | 组件表 `unit_in_axis_or_title` / gemini-3.1-pro-preview 文档数 |

### 词表控制

**无词表对照**（gemini-3.1-pro，同一批页面，prompt 不给词表）

| 有词表报出的 key 数 | 无词表自由命名映回词表后的 key 数 | 重合的 key 数 | 重合率（占有词表的） | 重合率（占映回的） |
|---|---|---|---|---|
| 882 | 456 | 266 | 30.2% | 58.3% |

映不回词表的自由名字 65 个：`abbreviated_years`、`bar_colours_vary`、`bar_fill_color`、`bar_with_overlay_point`、`baseline_highlight`、`chart_subtitle`、`coloured_heading_box`、`complex_heading_block`、`compound_bar_point`、`compound_chart`、`compound_figure`、`conditional_area_color`、`decimal_ticks_no_leading_zero`、`donut_chart_with_center_text`、`dotted_gridlines`、`dumbbell_with_line_connection`、`dynamic_label_color`、`explanatory_note`、`figure_heading`、`figure_notes`、`figure_notes_block`、`figure_number`、`floating_range_bar`、`floating_text_box`、`footer_notes`、`footer_notes_and_source`、`footer_notes_with_bold_prefix`、`heading_block`、`heading_block_above`、`heading_box`

**自身重跑**（gemini-3.1-pro，同一批页面同一 prompt 再答一次；这是本底噪声）

| 量 | 两次一致 | 只有一次报了 | 取值不同 | 一致率 |
|---|---|---|---|---|
| 组件命中集合 | 790 | 189 | 0 | 82.0% |
| 图表类型判定 | 108 | 3 | 26 | 76.8% |
| 数值印不印 | 130 | 3 | 4 | 95.7% |
| 稠密度档 | 125 | 3 | 9 | 91.8% |
| 标题 | 132 | 3 | 2 | 98.0% |
| 卡在哪一步 | 88 | 0 | 12 | 88.0% |
| 同向两条值轴 | 131 | 3 | 3 | 96.7% |
| 键分量 | 116 | 3 | 18 | 85.2% |

**词表外残差**：三家共报出 587 条词表没有的构造，去重后 538 个名字。
