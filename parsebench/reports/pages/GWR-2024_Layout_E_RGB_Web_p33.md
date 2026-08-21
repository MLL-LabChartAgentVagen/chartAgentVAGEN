# GWR-2024_Layout_E_RGB_Web_p33

![GWR-2024_Layout_E_RGB_Web_p33](../../data/pages/GWR-2024_Layout_E_RGB_Web_p33.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `GWR-2024_Layout_E_RGB_Web_p33` | GWR-2024_Layout_E_RGB_Web | untagged | 10 | `parsebench/data/pages/GWR-2024_Layout_E_RGB_Web_p33.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一张三系列分组柱图，19 个年份槽共 57 根柱，正负双向：零线居中，-2.8、-1.1、-0.8、-0.5、-0.3 五根柱向下。左轴 -4 到 10，只有横向网格；轴标题 `Change (%)` 竖排。每根柱都带竖排（旋转 90°）数值标签，正值贴柱顶、负值置于柱底之下。标题分两行：`Figure 3.2.  Annual average real monthly wage growth in the G20 countries, 2006–24` 与括号单位行 `(percentage)`，前置红色三角符号。图例三色一行置于 x 轴下方，x 轴年份斜排，下方 `Notes:` 与 `Source:` 两段小字，整块坐落于淡蓝底色面板中。
> 
> ## 定位一个值难在哪
> `2.7`：它在图上出现三次——2010 与 2013 的 G20 蓝柱、2020 的 G20 emerging countries 青柱。只有同时给出年份刻度与图例名才唯一；而 2020 组三根柱值为 2.2/1.8/2.7，竖排标签互相紧贴，行序容易错配。
> 
> ## 不确定的
> 淡蓝底是整块图框还是仅绘图区，边界不易分辨；数值标签究竟压在柱内还是浮于柱顶之上，逐柱不一致；零线是独立参考线还是轴基线，无法确认。

**gpt-5.6-sol**

> ### 画出来要什么
> 需重建单面板分组柱图：19年×3系列、负值跨越零线，浅蓝底、仅横网格、下置图例、倾斜年份刻度及柱端竖排数值；标题须拆分为“Figure 3.2.”、主标题、“(percentage)”和位置，并保留Notes与Source。
> 
> ### 定位一个值难在哪
> 例如“-2.8”须由“2022”刻度和“G20 advanced economies”图例共同定位。数值虽直接印出，但年份与数值均旋转，关联依赖空间位置。
> 
> ### 不确定的
> “2.7”出现不止一次；按给值顺序将其对应到最左侧的2010年G20柱。57根柱为逐项计数。

**gemini-3.1-pro**

> ## 画出来要什么
> 本页包含一个带有正负值的簇状柱形图（Figure 3.2）。图表上方有包含图号、主标题和单位说明的标题块。绘图区域填充了浅灰色背景，并带有白色的水平网格线。x轴为时间轴（2006-24），年份标签逆时针倾斜45度；y轴表示百分比变化，范围从-4到10。数据分为三个系列，图例位于x轴正下方。图表最显著的特征是其数据标签：所有的数值标签均放置在柱子的外部（正值在上方，负值在下方），并且由于柱子较窄，标签文本全部被垂直旋转了90度显示。图表的最底部附注了说明与数据来源文本。
> 
> ## 定位一个值难在哪
> 以2022年G20发达经济体的“-2.8”为例，该值不仅是一个跨越零轴的负数，其数值标签还被垂直倒置放置在向下的柱状图下方，且x轴的“2022”标签又是倾斜的。这种多重的旋转和紧凑的排版布局非常容易导致OCR识别减号失败，或者在关联数值坐标与年份、图例系列时产生严重的边界框干扰，从而导致解析失败。
> 
> ## 不确定的
> 深浅不同的蓝色、红色和青色在图例提取时高度依赖颜色识别的准确度；此外，现有的大多数PDF解析工具能否将垂直旋转90度的数据标签视作标准数字文本正确提取，仍存在一定的不确定性。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | grouped_bar | 57 | Figure 3.2. | above | all |
| opus-5 | f2 | unreadable | 0 | — | none | none |
| gpt-5.6-sol | f1 | grouped_bar | 57 | Figure 3.2. | above | all |
| gemini-3.1-pro | f1 | grouped_bar | 57 | Figure 3.2. | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_title_below_plot` | ✓ | — | — | opus-5: no such title; body text 'mated at 6.0 per cent, the highest value recorded' runs below the tinted block |
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: three coloured bars side by side in each year slot from 2006 to 2024；gpt-5.6-sol: Three coloured bars are drawn side by side for each year from 2006 to 2024.；gemini-3.1-pro: three bars are grouped side by side for each year |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: horizontal rules at 10, 8, 6, 4, 2, 0, -2, -4; no vertical rules；gpt-5.6-sol: White horizontal grid lines cross the panel; no vertical grid lines are drawn.；gemini-3.1-pro: white horizontal lines run across the plot, no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: legend row 'G20 | G20 advanced economies | G20 emerging countries' under the year axis；gpt-5.6-sol: The three-item legend sits below the x-axis and plot area.；gemini-3.1-pro: the three-item legend sits below the x-axis |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: bars drop below the zero line: -1.1, -0.3, -0.8, -2.8, -0.5；gpt-5.6-sol: Bars labelled “-1.1”, “-0.3”, “-0.8”, “-2.8” and “-0.5” extend below zero.；gemini-3.1-pro: bars pointing downwards for 2008 and 2022 with negative labels |
| `panel_background` | ✓ | ✓ | ✓ | opus-5: the plot area and its heading sit on a pale blue tinted block spanning the page；gpt-5.6-sol: The plot panel has a pale blue fill.；gemini-3.1-pro: the plot area has a light grey background fill |
| `rotated_axis_title` | ✓ | ✓ | — | opus-5: 'Change (%)' set vertically along the left axis；gpt-5.6-sol: “Change (%)” is set vertically along the left axis. |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: year labels 2006 ... 2024 set at roughly 45 degrees under the axis；gpt-5.6-sol: Year labels from “2006” through “2024” are angled diagonally.；gemini-3.1-pro: the year labels 2006 to 2024 are angled at 45 degrees |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Notes: Advanced G20 economies comprise Australia...' and 'Source: ILO estimates based on official national sources'；gpt-5.6-sol: “Notes:” and “Source:” lines appear below the legend.；gemini-3.1-pro: Notes: and Source: texts printed beneath the legend |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: '(percentage)' on the second heading line and 'Change (%)' on the axis；gpt-5.6-sol: The heading says “(percentage)” and the y-axis title reads “Change (%)”.；gemini-3.1-pro: (percentage) is in the heading and Change (%) on the y-axis |
| `value_label_inside` | ✓ | — | — | opus-5: '2.9', '3.2' printed vertically on the blue bars near their tops |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: '-1.1' and '-2.8' printed vertically below the ends of the downward bars；gpt-5.6-sol: Every number is printed beyond its bar end, including negative labels below the bars.；gemini-3.1-pro: numeric labels are placed just beyond the bar ends |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `rotated_value_labels` | opus-5 | 2,3 | every one of the 57 bar values is printed as 90-degree rotated text, e.g. '8.6', '-2.8' |
| `triangle_bullet_before_figure_number` | opus-5 | 4 | a red right-pointing triangle glyph precedes 'Figure 3.2.' and also precedes '3.2. Regional wage trends' |
| `repeated_value_across_slots` | opus-5 | 3 | '2.7' printed three times: 2010 G20, 2013 G20, 2020 emerging countries |
| `rotated_value_labels` | gpt-5.6-sol | 2,3 | All bar-end numbers, including “8.6” and “-2.8”, are rotated vertically. |
| `rotated_value_labels` | gemini-3.1-pro | 2,3 | the numbers printed on the bars are rotated 90 degrees vertically |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 2.9 | 2006、G20 | 2006、G20 | 2006、G20 | 2006、G20 | ✓ | ✓ | ✓ | 过 |
| 8.6 | 2007、G20 emerging countries | 2007、G20 emerging countries | 2007、G20 emerging countries | 2007、G20 emerging countries | ✓ | ✓ | ✓ | 过 |
| -1.1 | 2008、G20 advanced economies | 2008、G20 advanced economies | 2008、G20 advanced economies | 2008、G20 advanced economies | ✓ | ✓ | ✓ | 过 |
| 2.7 | 2010、G20 | 2010、G20 | 2010、G20 | 2010、G20 | ✓ | ✓ | ✓ | 过 |
| 6.4 | 2012、G20 emerging countries | 2012、G20 emerging countries | 2012、G20 emerging countries | 2012、G20 emerging countries | ✓ | ✓ | ✓ | 过 |
| 4.3 | 2021、G20 emerging countries | 2021、G20 emerging countries | 2021、G20 emerging countries | 2021、G20 emerging countries | ✓ | ✓ | ✓ | 过 |
| -0.8 | 2022、G20 | 2022、G20 | 2022、G20 | 2022、G20 | ✓ | ✓ | ✓ | 过 |
| -2.8 | 2022、G20 advanced economies | 2022、G20 advanced economies | 2022、G20 advanced economies | 2022、G20 advanced economies | ✓ | ✓ | ✓ | 过 |
| 6.0 | 2023、G20 emerging countries | 2023、G20 emerging countries | 2023、G20 emerging countries | 2023、G20 emerging countries | ✓ | ✓ | ✓ | 过 |
| 0.9 | 2024、G20 advanced economies | 2024、G20 advanced economies | 2024、G20 advanced economies | 2024、G20 advanced economies | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 3 | 1 | 3 | 未裁决 · 无实测证据 | 这一页 10 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 1 / 3 都无法证伪。 |
