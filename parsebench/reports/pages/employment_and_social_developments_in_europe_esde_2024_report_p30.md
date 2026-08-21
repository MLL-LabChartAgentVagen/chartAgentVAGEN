# employment_and_social_developments_in_europe_esde_2024_report_p30

![employment_and_social_developments_in_europe_esde_2024_report_p30](../../data/pages/employment_and_social_developments_in_europe_esde_2024_report_p30.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `employment_and_social_developments_in_europe_esde_2024_report_p30` | employment_and_social_developments_in_europe_esde_2024_report | 3d_chart+need_estimate | 9 | `parsebench/data/pages/employment_and_social_developments_in_europe_esde_2024_report_p30.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 
> 本页两幅图都需要复合构造。Chart 1.16 是「堆叠柱 + 两条折线」的混合标记：正负双向堆叠的六个贡献项（Compensation of employees…Taxes on income, wealth (negative)），叠加实线 Real GDHI 与虚线 Real GDP；x 轴是 Q1/Q3 两级刻度（内层季度、外层年份 2012–2023），共 48 个季度槽；图例排在右侧成一列。Chart 1.17 是 18 个 COICOP 类别 × 3 年的分组柱，类别标签旋转 90°并折行（如 “Retirement homes for elderly persons and residences for disabled persons”），图例置于绘图区内顶部，轴下限为 -10。两图都带 Note/Source 与 “Click here to download chart.” 链接行。
> 
> ## 定位一个值难在哪
> 
> 以 42.5 为例：它是 Chart 1.17 中 “Electricity, gas and other fuels” 的 2022 绿柱，图上不印数字，y 轴刻度间隔为 10，肉眼读到 42–43 已接近 5% 容差边界；且需同时锁定「类别 + 年份图例」两个标签，而类别名竖排折行，解析器很可能截断。
> 
> ## 不确定的
> 
> Chart 1.16 中细小的负向分段（如 -4.1 是否属于 Net social benefits 2021Q3）无法确证；季度堆叠段的具体归属与颜色在 150 dpi 下有混淆风险；6、3、1.2 等小数值在两图上都可能对应多个标记。

**gpt-5.6-sol**

> **画出来要什么**：一页两图。Chart 1.16 是48季度六色正负堆叠柱，叠加实线与虚线，采用双层时间轴和右侧图例；Chart 1.17 是18类、3年份的分组柱，带竖排长标签和图内图例。两图均有横网格、零线、注释、来源及下载链接。
> 
> **定位一个值难在哪**：例如 Chart 1.17 的 “Actual rentals paid by tenants”–“2021”=1.2，须同时匹配竖排类别和年份颜色；柱上未印数值，10单位刻度下5%容差仅0.06。
> 
> **不确定的**：Chart 1.16 的折线没有点标记，点数及堆叠段按48个季度估算；细小或零贡献段可能不可见。

**gemini-3.1-pro**

> ### 画出来要什么
> 本页包含两个复杂的统计图表。图表 1.16 是一个混合图表，在同一个左侧数值轴下，不仅包含了六个系列的堆叠柱状图（其中部分包含负值，且图例明确指出了“negative”属性），还叠加了两条分别用实线和虚线绘制的折线图（代表GDP和GDHI）。同时，该图采用了复杂的双层时间X轴，外层年份跨越多列，内层季度仅选择性地标注了 Q1 和 Q3，隐含了未标注的 Q2 和 Q4 的空间排布。
> 图表 1.17 是一个簇状柱形图，其X轴类别标签较长，不仅整体旋转了90度，且部分长文本折行显示（如“Retirement homes...”折成了三行）。图例直接放置在绘图区内部顶端。两个图表均仅依靠刻度线来定位数值，没有任何直接打印的数值标签，并且下方均带有独立的数据源说明和数据下载链接。
> 
> ### 定位一个值难在哪
> 以图表 1.17 中的 `["2022", "Electricity, gas and other fuels"]` 为例。该柱状图极高，对应值为 `42.5`。定位它的维度并不难，但在Y轴刻度间距高达 10（从 40 到 50）的情况下，肉眼或模型从没有任何辅助网格细分的柱子顶端对齐坐标轴，要读取精确到小数点后一位的数值（42.5）是完全不可能的，必定会被 5% 的误差容忍度判定为失败。
> 
> ### 不确定的
> 对于图表 1.16 中的图例“Taxes on income, wealth (negative)”，不确定图表引擎是否需要额外配置以强制该系列始终向坐标轴负方向绘制，还是完全依赖传入的底层负数值自动驱动。此外，副标题中分别提到了“pp”和“% change”，但整个图表共用同一个数值轴刻度，不确定这两者在底层数据处理时是否需要经过统一的缩放配置。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | compound | 384 | Chart 1.16 | above | none |
| opus-5 | f2 | grouped_bar | 54 | Chart 1.17 | above | none |
| gpt-5.6-sol | f1 | compound | 384 | Chart 1.16 | above | none |
| gpt-5.6-sol | f2 | grouped_bar | 54 | Chart 1.17 | above | none |
| gemini-3.1-pro | f1 | other · mixed marks | 384 | Chart 1.16 | above | none |
| gemini-3.1-pro | f2 | grouped_bar | 54 | Chart 1.17 | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `dashed_line_series` | ✓ | ✓ | ✓ | opus-5: legend shows 'Real GDP' as a dashed line, 'Real GDHI' solid；gpt-5.6-sol: Legend and plot draw “Real GDP” dashed and “Real GDHI” solid.；gemini-3.1-pro: the series Real GDP is rendered as a dashed line |
| `data_link_below_figure` | ✓ | ✓ | ✓ | opus-5: 'Click here to download chart.' printed under the source line；gpt-5.6-sol: “Click here to download chart.” appears below the source.；gemini-3.1-pro: both charts feature a 'Click here to download chart.' hyperlink |
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: 48 quarters times six segments plus two 48-point lines；gpt-5.6-sol: Approximately 288 stacked segments and 96 line points cover 48 quarters.；gemini-3.1-pro: 48 time points across 8 distinct series generate over 300 marks |
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: three bars 2021, 2022, 2023 side by side in each COICOP slot；gpt-5.6-sol: Three bars labelled “2021”, “2022” and “2023” stand side by side per category.；gemini-3.1-pro: bars for 2021, 2022, 2023 sit side by side |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: dotted horizontal rules at 50, 40, 30 ... -10 only；gpt-5.6-sol: Dotted horizontal gridlines cross the plot; no vertical gridlines are drawn.；gemini-3.1-pro: horizontal dotted grid lines are drawn, but no vertical ones |
| `highlighted_category` | ✓ | — | — | opus-5: 'All-items HICP' aggregate stands first in the category axis |
| `legend_beside_plot` | ✓ | ✓ | ✓ | opus-5: eight legend entries stacked in a right-hand column level with the plot；gpt-5.6-sol: The eight-entry legend forms a column to the right of the plot.；gemini-3.1-pro: the legend column is positioned to the right of the chart area |
| `legend_inside_plot` | ✓ | ✓ | ✓ | opus-5: '2021 2022 2023' legend row sits inside the plot area near the top；gpt-5.6-sol: The “2021 2022 2023” legend sits inside the plot near its top.；gemini-3.1-pro: legend items 2021 2022 2023 sit over the gridlines in top center |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: solid 'Real GDHI' and dashed 'Real GDP' lines drawn over the stacked bars；gpt-5.6-sol: Stacked bars are overlaid by solid “Real GDHI” and dashed “Real GDP” lines.；gemini-3.1-pro: stacked bars for components and lines for GDHI and GDP |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: Chart 1.16 and Chart 1.17 each with own number, title and captions；gpt-5.6-sol: “Chart 1.16” and “Chart 1.17” have separate headings and plots.；gemini-3.1-pro: Chart 1.16 and Chart 1.17 are independent figures with own numbers |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: axis lowest tick reads -10; one 2023 bar falls below zero；gpt-5.6-sol: The 2023 fuels bar extends below the horizontal tick labelled “0”.；gemini-3.1-pro: y-axis drops to -16 and bars point downwards |
| `nonstandard_time_ticks` | ✓ | ✓ | — | opus-5: time written as 'Q1', 'Q3' rather than dates；gpt-5.6-sol: The time axis uses quarter labels “Q1” and “Q3”. |
| `reference_line` | ✓ | ✓ | — | opus-5: a zero rule crosses the panel with bars going both ways；gpt-5.6-sol: A horizontal rule crosses the plot at the tick labelled “0”. |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: '% change on previous year' set vertically along the left axis；gpt-5.6-sol: “% change on previous year” is rotated along the left axis.；gemini-3.1-pro: the text '% change on previous year' runs vertically along the y-axis |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: category names set vertically, 90 degrees, under the axis；gpt-5.6-sol: All category labels are rotated vertically below the bars.；gemini-3.1-pro: category labels along the x-axis are turned 90 degrees |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: Consumption items selected from the classification...' and 'Source: Eurostat data [prc_hicp_aind].'；gpt-5.6-sol: “Note:” and “Source:” lines are printed directly below the chart.；gemini-3.1-pro: Note: and Source: lines appear beneath both charts |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: four quarters per year but only Q1 and Q3 ticks labelled；gpt-5.6-sol: Quarterly marks are drawn, but only “Q1” and “Q3” are labelled each year.；gemini-3.1-pro: only Q1 and Q3 are explicitly labelled while Q2 and Q4 positions are implicitly left blank |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: each quarter bar is built of six coloured contribution segments；gpt-5.6-sol: Six coloured contribution segments stack above and below zero in each quarter.；gemini-3.1-pro: components of GDHI are stacked atop each other |
| `two_level_x_ticks` | ✓ | ✓ | ✓ | opus-5: inner row 'Q1 Q3' with outer row '2012'...'2023' below separators；gpt-5.6-sol: Quarter labels “Q1” and “Q3” sit above a second row of years.；gemini-3.1-pro: quarters Q1 Q3 are arranged directly above years 2012 to 2023 |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: subtitle '(year-on-year change), by COICOP, HICP annual data, EU'; bare numeric ticks；gpt-5.6-sol: Subtitle states “% change on previous year” and “contribution of GDHI components (pp)”.；gemini-3.1-pro: the phrase '% change on previous year' serves as the axis title |
| `unit_in_series_name` | ✓ | — | — | opus-5: legend entry 'Taxes on income, wealth (negative)' carries the sign convention |
| `wrapped_category_labels` | ✓ | ✓ | ✓ | opus-5: 'Retirement homes for elderly persons and residences for disabled persons' wraps to three lines；gpt-5.6-sol: Long labels including “Fuels and lubricants for personal transport equipment” occupy multiple lines.；gemini-3.1-pro: long category labels like 'Passenger transport...' break into multiple lines |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `diverging_stacked_bar` | opus-5 | 2,3 | contribution segments stack upward and downward from zero within one quarter bar |
| `unit_differs_between_series_and_bars` | opus-5 | 2,4 | subtitle: lines in '% change on previous year', bars in 'contribution ... (pp)', one axis |
| `category_axis_labels_below_long_gap` | opus-5 | 3 | vertical category text hangs far below the baseline, detached from short bars |
| `mixed_units_shared_axis` | gpt-5.6-sol | 2,3 | Subtitle assigns “% change on previous year” to lines and “(pp)” to components on one scale. |
| `dual_unit_single_axis` | gemini-3.1-pro | 4 | the subtitle specifies both % change and pp measuring against the same left axis |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 3 | 2020、Q3、Net social benefits | Actual rentals paid by tenants、2023 | Actual rentals paid by tenants、2023 | 2023、Actual rentals paid by tenants | ✗ | ✗ | ✗ | 没过 |
| 1.2 | 2021、Q1、Real GDHI | not_found | Actual rentals paid by tenants、2021 | 2021、Clothing and footwear | ✗ | ✗ | ✗ | 过 |
| 6 | 2022、Q1、Real GDP | Motor cars、2022 | Water supply、2023 | 2023、Household furniture | ✗ | ✗ | ✗ | 过 |
| 6.4 | All-items HICP、2023 | Net social benefits、Q1、2020 | All-items HICP、2023 | 2023、All-items HICP | ✗ | ✓ | ✓ | 没过 |
| 11.9 | Food and non-alcoholic beverages、2022 | Food and non-alcoholic beverages、2022 | Electricity, gas and other fuels、2021 | 2022、Food and non-alcoholic beverages | ✓ | ✗ | ✓ | 过 |
| 42.5 | Electricity, gas and other fuels、2022 | Electricity, gas and other fuels、2022 | Electricity, gas and other fuels、2022 | 2022、Electricity, gas and other fuels | ✓ | ✓ | ✓ | 过 |
| 17.2 | Fuels and lubricants for personal transport equipment、2021 | Fuels and lubricants for personal transport equipment、2021 | Fuels and lubricants for personal transport equipment、2021 | 2021、Fuels and lubricants for personal transport equipment | ✓ | ✓ | ✓ | 过 |
| -4.1 | Fuels and lubricants for personal transport equipment、2023 | Fuels and lubricants for personal transport equipment、2023 | Fuels and lubricants for personal transport equipment、2023 | 2023、Fuels and lubricants for personal transport equipment | ✓ | ✓ | ✓ | 没过 |
| 2.5 | Passenger transport by underground and tram、2023 | Water supply、2022 | Motor cars、2021 | 2022、Clothing and footwear | ✗ | ✗ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "compound" | "compound" | "other · mixed marks" | compound | 按类型表自己的定义判：`compound` 是<strong>同一个面板里出现两种以上图元形状</strong>，所以决定它的是三家自己在 `components` 里记的 `mixed_marks`，不是它们给这张图起的名字。三家都同时记了 `stacked_bar` 与 `mixed_marks`，图元数都是 384。gemini 写的 `other · mixed marks` 说的就是 compound。 |
