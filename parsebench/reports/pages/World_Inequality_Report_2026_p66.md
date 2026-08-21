# World_Inequality_Report_2026_p66

![World_Inequality_Report_2026_p66](../../data/pages/World_Inequality_Report_2026_p66.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `World_Inequality_Report_2026_p66` | World_Inequality_Report_2026 | untagged | 10 | `parsebench/data/pages/World_Inequality_Report_2026_p66.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 
> 本页需两个独立编号图。**Figure 2.13** 是 8 类别分组柱状图，绿/红两系列，每根柱顶端印数值（19、10 … 72、50），左侧旋转轴标题 `Top 10% average to bottom 50% average income`，类别名换行成两三行（`North America & Oceania`），图例在图下。**Figure 2.14** 是两联小图，共享一条左侧旋转轴 `Reduction in top 10% to bottom 50% income ratio (%)`，每联各有自己的面板标题（`Tax progressivity` / `Redistribution considering taxes and transfers`），8 条彩色折线跨 1980–2025，含负值与 0 参考虚线，图例两行置于两联之下共享。
> 
> ## 定位一个值难在哪
> 
> 以 `36` 为例：它印在 Figure 2.13 中 `Russia & Central Asia` 的绿柱上方，要唯一定位需三段标签——图号、类别名（跨三行换行）、图例项 `Before redistribution`。类别文字被拆行，解析器易得到 `Russia &` / `Central` / `Asia` 三段，与数值的关联因而断裂。`50` 更麻烦：同一图中 `Middle East & North Africa` 与 `Latin America` 的红柱都是 50。
> 
> ## 不确定的
> 
> Figure 2.14 各折线无印刷值，只能按 10 一格的刻度读取，8 条线在 0–20 区间密集重叠，颜色（如 East Asia 紫 vs MENA 橙）难以区分；两联是否同一 y 轴范围看似一致但未标注。

**gpt-5.6-sol**

> ### 画出来要什么
> 同页两幅编号图：Figure 2.13 是8地区、2系列的分组柱，含柱外数值、换行类目和下置图例；Figure 2.14 是双面板、8系列的高密度年度折线，共享下置图例，并显示负值与零线。还需重建标题层级、面板标题、解释及来源段。
> 
> ### 定位一个值难在哪
> “50”出现两次：Middle East & North Africa 和 Latin America 的 After redistribution 柱均为50；必须同时保留地区与系列标签才能唯一定位。
> 
> ### 不确定的
> Figure 2.14 的年度折点无标记，按标题将1980–2025估为46期；末端年份及精确折点数无法由页面分辨率完全确认。

**gemini-3.1-pro**

> ### 画出来要什么
> 要重现此页，需要支持：带有顶部数据标签的分组柱状图（Figure 2.13），并能处理多行折叠的超长X轴分类标签；带有双面板（Small Multiples）的密集折线图（Figure 2.14），需支持面板各自的标题、共享的底部图例、包含负值的Y轴刻度以及独立样式的零基准线；此外还要支持Y轴标题整体旋转置于坐标轴左侧。
> 
> ### 定位一个值难在哪
> 以Figure 2.13中的数值“53”为例，虽然数值本身清晰打印在绿色柱子顶部（0步障碍），但其对应的X轴类别标签“Middle East & North Africa”被极度压缩且换行折叠为三行。传统的OCR或图表解析器在处理这种密集换行时，极易将其识别为多个独立的词块，或与相邻标签混淆，导致无法将单元格数据与正确的类别Key可靠关联（Step 3障碍）。
> 
> ### 不确定的
> Figure 2.14中的折线极其密集且有互相遮盖，部分年份甚至难以分辨某一特定颜色折线的具体纵坐标；图注部分以“Interpretation”开头而不是常规的“Note”，不确定解析管线是否能正确作为说明文本提取。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | grouped_bar | 16 | Figure 2.13. | above | all |
| opus-5 | f2 | line | 736 | Figure 2.14. | above | none |
| gpt-5.6-sol | f1 | grouped_bar | 16 | Figure 2.13. | above | all |
| gpt-5.6-sol | f2 | line | 736 | Figure 2.14. | above | none |
| gemini-3.1-pro | f1 | grouped_bar | 16 | Figure 2.13. | above | all |
| gemini-3.1-pro | f2 | line | 736 | Figure 2.14. | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: 8 series x ~46 years x 2 panels of annual line points；gpt-5.6-sol: Eight annual series run across 1980–2025 in each of two panels.；gemini-3.1-pro: eight series plotted over 45 years in each panel |
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: green and red bars side by side in each region slot；gpt-5.6-sol: Green and red bars stand side by side within each regional category.；gemini-3.1-pro: green and red bars sitting side by side for each region |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: faint horizontal rules at 10,20,30,40,50; no vertical rules；gpt-5.6-sol: Only horizontal dotted gridlines cross the bar plot.；gemini-3.1-pro: dashed horizontal reference lines, no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: two rows of colour swatches under both panels；gpt-5.6-sol: The regional series legend is outside and below both plots.；gemini-3.1-pro: legend items East Asia, Europe... sit at the bottom |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: Figure 2.13 and Figure 2.14 each numbered with their own captions；gpt-5.6-sol: Two separately numbered figures, “Figure 2.13.” and “Figure 2.14.”, occupy the page.；gemini-3.1-pro: two distinct figures numbered Figure 2.13 and Figure 2.14 |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: ticks −10 and −20; green and yellow lines run below zero；gpt-5.6-sol: Both y axes extend below zero to “−20”; several left-panel lines are negative.；gemini-3.1-pro: y-axis drops below zero to -10 and -20 |
| `panel_title_per_panel` | ✓ | ✓ | ✓ | opus-5: 'Tax progressivity' and 'Redistribution considering taxes and transfers' above each panel；gpt-5.6-sol: Panels are titled “Tax progressivity” and “Redistribution considering taxes and transfers”.；gemini-3.1-pro: titles 'Tax progressivity' and 'Redistribution considering taxes...' over panels |
| `reference_line` | ✓ | ✓ | — | opus-5: dotted horizontal rule drawn at 0 across both panels；gpt-5.6-sol: A darker dotted horizontal rule crosses both panels at 0. |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Reduction in top 10% to bottom 50% income ratio (%)' set vertically；gpt-5.6-sol: “Reduction in top 10% to bottom 50% income ratio (%)” runs vertically beside the panels.；gemini-3.1-pro: y-axis title 'Reduction in top 10% to...' runs vertically |
| `shared_axis` | ✓ | — | — | opus-5: rotated y title drawn once at far left serving both panels |
| `shared_legend` | ✓ | ✓ | ✓ | opus-5: one eight-entry legend below both panels: 'East Asia ... Sub–Saharan Africa'；gpt-5.6-sol: One eight-series legend spans beneath both line panels.；gemini-3.1-pro: one set of legend items under the entire figure serves both panels |
| `small_multiples_4` | ✓ | ✓ | ✓ | opus-5: two side-by-side line panels of the same chart form；gpt-5.6-sol: Two repeated line-chart panels are arranged side by side.；gemini-3.1-pro: two side-by-side line chart panels |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Interpretation. ... Sources and series: wir2026.wid.world/methodology and Chancel and Piketty (2021).'；gpt-5.6-sol: “Sources and series: wir2026.wid.world/methodology and Fisher–Post and Gethin (2025).” appears below.；gemini-3.1-pro: Interpretation and Sources lines under the legend |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: ticks every five years 1980..2020 but the lines are annual；gpt-5.6-sol: Annual line vertices are shown while labels appear every five years from 1980 to 2020.；gemini-3.1-pro: x-axis plots continuous years but labels only every 5 years |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: '(%)' appears only inside the rotated y-axis title；gpt-5.6-sol: The vertical title ends with “income ratio (%)”. |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: numbers 19, 10, 35, 28 ... printed just above each bar top；gpt-5.6-sol: Every number is printed just above its bar.；gemini-3.1-pro: numbers 19, 10, etc., sit right above the bars |
| `wrapped_category_labels` | ✓ | ✓ | ✓ | opus-5: 'North America & Oceania' wraps to three lines under the axis；gpt-5.6-sol: Labels including “North America & Oceania” wrap across multiple lines.；gemini-3.1-pro: 'North America & Oceania' wraps onto three lines |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `abbrev_series_name_in_legend` | opus-5 | 3 | legend reads 'MENA' while Figure 2.13 axis spells 'Middle East & North Africa' |
| `duplicate_value_within_series` | opus-5 | 3 | '50' printed twice: Middle East & North Africa and Latin America red bars |
| `interpretation_paragraph_below_figure` | opus-5 | 4 | 'Interpretation.' bolded lead-in paragraph explaining the reading before the sources line |
| `interpretation_paragraph_below_figure` | gpt-5.6-sol | 4 | A paragraph beginning “Interpretation.” sits between Figure 2.13 and Figure 2.14. |
| `interpretation_paragraph_below_figure` | gpt-5.6-sol | 4 | A paragraph beginning “Interpretation.” sits below the shared legend. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 19 | Europe、Before redistribution | Europe、Before redistribution | Europe、Before redistribution | Europe、Before redistribution | ✓ | ✓ | ✓ | 过 |
| 10 | Europe、After redistribution | Europe、After redistribution | Europe、After redistribution | Europe、After redistribution | ✓ | ✓ | ✓ | 过 |
| 28 | East Asia、After redistribution | East Asia、After redistribution | East Asia、After redistribution | East Asia、After redistribution | ✓ | ✓ | ✓ | 过 |
| 18 | North America & Oceania、After redistribution | North America & Oceania、After redistribution | North America & Oceania、After redistribution | North America & Oceania、After redistribution | ✓ | ✓ | ✓ | 过 |
| 36 | Russia & Central Asia、Before redistribution | Russia & Central Asia、Before redistribution | Russia & Central Asia、Before redistribution | Russia & Central Asia、Before redistribution | ✓ | ✓ | ✓ | 过 |
| 33 | Russia & Central Asia、After redistribution | Russia & Central Asia、After redistribution | Russia & Central Asia、After redistribution | Russia & Central Asia、After redistribution | ✓ | ✓ | ✓ | 过 |
| 52 | Sub-Saharan Africa、Before redistribution | Sub–Saharan Africa、Before redistribution | Sub–Saharan Africa、Before redistribution | Sub-Saharan Africa、Before redistribution | ✓ | ✓ | ✓ | 过 |
| 53 | Middle East & North Africa、Before redistribution | Middle East & North Africa、Before redistribution | Middle East & North Africa、Before redistribution | Middle East & North Africa、Before redistribution | ✓ | ✓ | ✓ | 过 |
| 72 | Latin America、Before redistribution | Latin America、Before redistribution | Latin America、Before redistribution | Latin America、Before redistribution | ✓ | ✓ | ✓ | 过 |
| 50 | Latin America、After redistribution | Middle East & North Africa、After redistribution | Latin America、After redistribution | Latin America、After redistribution | ✗ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 3 | 1 | 3 | 未裁决 · 无实测证据 | 这一页 10 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 1 / 1 都无法证伪。 |
