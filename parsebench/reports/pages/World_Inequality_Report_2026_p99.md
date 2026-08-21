# World_Inequality_Report_2026_p99

![World_Inequality_Report_2026_p99](../../data/pages/World_Inequality_Report_2026_p99.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `World_Inequality_Report_2026_p99` | World_Inequality_Report_2026 | untagged | 10 | `parsebench/data/pages/World_Inequality_Report_2026_p99.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 两幅独立编号图共页。图4.10 是三条时间序列折线（High income / Low & middle income / World），2000–2025，y 轴 80%–105%、水平虚线网格，另有一条红色虚线参考线并在图内标注 "Gender parity"；y 轴标题竖排且分两行 "Female high school enrollment (as % of male high school enrollment)"；标题分成绿色编号+黑色标题行，再加一行加粗副标题 "Female high school enrollment as a share of male enrollment, 2000–2025"；图例在图下方。图4.11 是 8 组分组柱（Men/Women），每根柱顶印数值，y 轴 0%–14% 每 1% 一档，轴标题竖排 "Return to an additional year of schooling (%)"，类别标签换行（"Sub–Sah. Africa"、"Europe / U.S."）。两图下均有 **Interpretation.** 与 **Sources and series:** 段。
> 
> **定位一个值难在哪**
> 
> 101：图上没印，只能在图4.10 中读红线 2025 端点，网格每 5%，101% 与 100% 参考线仅差约 1/5 格；且它在正文里写作 "the ratio reached 101%"，表格若从曲线取值需同时给出 "High income" 与 "2025"，而 x 轴刻度每 5 年，2025 恰是末刻度。
> 
> **不确定的**
> 
> 折线实际逐年点数（按 26 点估计）；85 是否指 2000 年 Low & middle income 起点（图上读约 84.7%），无印值，存疑。

**gpt-5.6-sol**

> ### 画出来要什么
> 同页重建两幅独立图：三系列年度折线、100%“Gender parity”虚线、稀疏时间刻度；以及八组男女并列柱、柱外数值和换行类目。两图均有分层标题、旋转纵轴标题、图下图例及解释和来源文字。
> 
> ### 定位一个值难在哪
> “85”需同时锁定“2000”和“Low & middle income”，且未印在折线上，只能由5个百分点刻度估读；“12.1”则由“Europe / U.S.”与“Women”直接定位并印在柱外。
> 
> ### 不确定的
> 折线没有点标记，按2000–2025逐年数据估为每系列26个顶点；“85”和“101”是按图及解释文字取整，精确小数不可见。

**gemini-3.1-pro**

> ### 画出来要什么
> 页面包含两个图表：一个是多系列折线图，另一个是分组柱状图。
> - **折线图 (Figure 4.10)**：包含三条平滑的数据线，展示不同收入群体的比例。需要支持绘制Y轴起始值截断（从80%开始），并在100%处添加带有文本标签（Gender parity）的红色虚线参考线。Y轴标题为多行文本且需垂直排列放置于轴外侧。
> - **分组柱状图 (Figure 4.11)**：包含两个分类系列（Men 和 Women）。需要在每个柱子顶部外部居中显示精确数值标签。X轴类别标签需要原生支持多行折行排版（如 "Europe / U.S."），而不是简单截断或缩小字体。图例需水平排列位于图表下方。
> - 两个图表均采用了结构化的高级标题块（独立图号、主标题、副标题），且在图表下方附带了长段落的 "Interpretation." 解释文本以及来源说明。
> 
> ### 定位一个值难在哪
> 以 Figure 4.11 中的 `10`（Europe / U.S. 地区男性的数据）为例。其直接寻址依赖于X轴的类别标签，但该标签在页面上排版为带有换行符的 "Europe /\nU.S."。若解析器未严格保留换行或未统一使用特定的分隔符，而是直接提取为单行字符串，会导致基于精确字符串匹配的键名比对失效，从而阻塞在第3步。
> 
> ### 不确定的
> 折线图 (Figure 4.10) 的确切数据时间粒度。虽然X轴刻度是每5年一个（2000, 2005），但折线并非仅在这些年份转折，暗示数据可能是按年度绘制的，缺乏离散点标记使得这一判断无法百分之百确认。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 78 | Figure 4.10. | above | none |
| opus-5 | f2 | grouped_bar | 16 | Figure 4.11. | above | all |
| opus-5 | f3 | unreadable | 0 | — | none | none |
| gpt-5.6-sol | f1 | line | 78 | Figure 4.10. | above | none |
| gpt-5.6-sol | f2 | grouped_bar | 16 | Figure 4.11. | above | all |
| gemini-3.1-pro | f1 | line | 78 | Figure 4.10. | above | none |
| gemini-3.1-pro | f2 | grouped_bar | 16 | Figure 4.11. | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | — | — | opus-5: "MENA" and "Sub–Sah. Africa" written as codes/abbreviations |
| `annotation_callout` | ✓ | — | — | opus-5: red text "Gender parity" drawn inside the plot just under the dashed rule |
| `axis_starts_above_zero` | ✓ | ✓ | ✓ | opus-5: left axis lowest tick reads "80%", top "105%"；gpt-5.6-sol: The left scale begins at “80%” without an axis break.；gemini-3.1-pro: the lowest tick on the y-axis is 80%, not 0% |
| `dashed_line_series` | ✓ | — | — | opus-5: the parity rule is dashed while the three data lines are solid |
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: a red and a green bar side by side in each of eight region slots；gpt-5.6-sol: Red Men and green Women bars stand side by side in every region.；gemini-3.1-pro: bars for Men and Women are placed side by side |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: horizontal dotted rules at every 1% across the panel；gpt-5.6-sol: Horizontal dashed gridlines cross the plot; no vertical gridlines are drawn.；gemini-3.1-pro: only horizontal dotted grid lines are drawn |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: "Men  Women" swatch row sits below the category axis；gpt-5.6-sol: The “Men” and “Women” legend is centered beneath the category axis.；gemini-3.1-pro: the legend sits below the x-axis |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: "Figure 4.10." and "Figure 4.11." each with their own title and Interpretation block；gpt-5.6-sol: Separate headings read “Figure 4.10.” and “Figure 4.11.”；gemini-3.1-pro: Figure 4.10 and Figure 4.11 on the same page |
| `reference_line` | ✓ | ✓ | ✓ | opus-5: red dashed horizontal rule at 100% labelled "Gender parity"；gpt-5.6-sol: Red dashed horizontal rule at 100% is labeled “Gender parity”.；gemini-3.1-pro: red dashed line at 100% labeled Gender parity |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: "Return to an additional year of schooling  (%)" set vertically beside the axis；gpt-5.6-sol: “Return to an additional year of schooling (%)” runs vertically at left.；gemini-3.1-pro: y-axis titles run vertically along the left edge |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: "Sources and series: wir2026.wid.world/methodology." and "Sources and series: Gethin (2024)."；gpt-5.6-sol: “Sources and series: Gethin (2024).” appears below the plot.；gemini-3.1-pro: Sources and series: text blocks below each figure |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: ticks 2000, 2005, 2010, 2015, 2020, 2025 while the lines bend yearly；gpt-5.6-sol: Annual 2000–2025 lines have labels only at 2000, 2005, …, 2025.；gemini-3.1-pro: ticks every 5 years for what appears to be an annual line |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: axis title carries "(%)"; ticks read "0%" to "14%"；gpt-5.6-sol: The rotated axis reads “Return to an additional year of schooling (%)”.；gemini-3.1-pro: y-axis title ends with (%) |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: "4.2%", "12.1%" printed above the bar tops；gpt-5.6-sol: Every percentage, including “4.2%” and “12.1%”, is printed above its bar.；gemini-3.1-pro: percentages like 4.2% sit just above the bars |
| `wrapped_category_labels` | ✓ | ✓ | ✓ | opus-5: "Sub–Sah. Africa", "Latin America", "Europe / U.S." wrap onto two lines；gpt-5.6-sol: “Other Asia”, “Sub–Sah. Africa”, and “Latin America” wrap onto two lines.；gemini-3.1-pro: x-axis labels like Other Asia are split across two lines |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `interpretation_paragraph_block` | opus-5 | 4 | "Interpretation. This figure shows the evolution of the gender gap..." bold lead-in under each figure |
| `numbered_title_two_colour` | opus-5 | 3,4 | "Figure 4.10." in green bold, title text in black bold on the same line |
| `bold_subtitle_above_plot` | opus-5 | 4 | bold line "Female high school enrollment as a share of male enrollment, 2000–2025" between title and plot |
| `value_in_caption_text` | opus-5 | 1,2,3 | "in high–income countries, the ratio reached 101%" printed only in the Interpretation prose |
| `interpretation_paragraph` | gpt-5.6-sol | 4 | “Interpretation.” begins a prose paragraph beneath each legend. |
| `interpretation_text_block` | gemini-3.1-pro | 4 | Interpretation. paragraphs explaining the plot sit directly under each figure |
| `reference_line_annotation` | gemini-3.1-pro | 1,3 | Gender parity text is drawn inline next to the dashed reference line |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 85 | Low & middle income、2000 | Low & middle income、2000 | 2000、Low & middle income | Low & middle income、2000 | ✓ | ✓ | ✓ | 过 |
| 101 | High income、2000 | High income、2025 | 2025、High income | High income、2025 | ✗ | ✗ | ✗ | 过 |
| 4.2 | MENA、Men | MENA、Men | MENA、Men | Men、MENA | ✓ | ✓ | ✓ | 过 |
| 6.3 | MENA、Women | MENA、Women | MENA、Women | Women、MENA | ✓ | ✓ | ✓ | 过 |
| 8.3 | China、Men | China、Men | China、Men | Men、China | ✓ | ✓ | ✓ | 过 |
| 10.5 | China、Women | China、Women | China、Women | Women、China | ✓ | ✓ | ✓ | 过 |
| 7.6 | World、Men | World、Men | World、Men | Men、World | ✓ | ✓ | ✓ | 过 |
| 9.9 | World、Women | World、Women | World、Women | Women、World | ✓ | ✓ | ✓ | 过 |
| 10 | Europe / U.S.、Men | Europe / U.S.、Men | Europe / U.S.、Men | Men、Europe / U.S. | ✓ | ✓ | ✓ | 过 |
| 12.1 | Europe / U.S.、Women | Europe / U.S.、Women | Europe / U.S.、Women | Women、Europe / U.S. | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 2 | 1 | 3 | 未裁决 · 无实测证据 | 这一页 10 个抽查点全过，运行没有在任何一步卡住，三家的 2 / 1 / 3 都无法证伪。 |
