# World_Inequality_Report_2026_p25

![World_Inequality_Report_2026_p25](../../data/pages/World_Inequality_Report_2026_p25.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `World_Inequality_Report_2026_p25` | World_Inequality_Report_2026 | need_estimate | 10 | `parsebench/data/pages/World_Inequality_Report_2026_p25.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 单面板折线图,两条序列(France、South Korea),各带方形/十字标记,10 个收入分位类别。标题需拆成三层:绿色 `Figure 17.` + 粗体标题「Without redistribution, political inequality will increase」,再加居中的图内副标题「Political donations by income decile, % of total」。左轴为竖排两行轴标题「Percentage of total political donations by income decile」,刻度 `0%`–`60%`,仅横向虚线网格。x 轴标签 `P0–P10`…`P90–P100` 旋转约 45°。图例在图下方一行,下面还有 **Interpretation.** 与 **Sources and series:** 两段小字。
> 
> **定位一个值难在哪**
> 
> 取 57.0:它是 South Korea 在 `P90–P100` 的端点,未标数值。刻度间距 10 个百分点,5% 容差约 ±2.85 个百分点,而两条线在该点相距仅约 5 个点且几乎重叠,读错序列就整体偏 5。地址需要三段:图号、序列名、分位名。
> 
> **不确定的**
> 
> 低分位(P0–P10 至 P30–P40)两线在 0–1% 内完全叠合,无法分辨谁在上;2.8、5.0、5.8 等值只能按视觉排序猜归属。也无法确认副标题是图内文本还是标题的第二行。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 单面板双系列折线图：10个倾斜的收入十分位标签、百分比纵轴、横纵网格、蓝色菱形与紫色方形点标记，以及图下图例。“Figure 17.”、主标题、副标题和单位均置于图上；下方另有“Interpretation.”及来源行。
> 
> **定位一个值难在哪**
> 
> 例如 South Korea 的“P50–P60”值2.8未印在图上。纵轴主刻度相隔10个百分点，而5%容差仅±0.14个百分点，必须依靠点位进行很细的插值。
> 
> **不确定的**
> 
> 所有给定数值都没有数据标签；8.0、5.8等具体归属依据点位、系列和给定值推定，无法从页面文字直接核实。

**gemini-3.1-pro**

> ### 画出来要什么
> 
> 本页包含一个标准的折线图。生成该图需要支持带数据点标记的折线绘制。X轴包含10个类别区间标签（如 `P0-P10` 等），这些标签呈约45度倾斜排列；Y轴范围为 `0%` 至 `60%`，间隔为10%，且带有垂直旋转的轴标题。图表内部只有水平虚线网格，无垂直网格线。图表上方有一个多行的标题区（包含图号、主标题、副标题），下方则是居中的图例，以及底部的解释说明（Interpretation）和数据来源（Sources and series）文本。
> 
> ### 定位一个值难在哪
> 
> 以值 `52.0` 为例，读者需要在图例中定位到表示 `France` 的蓝色折线，并在X轴上找到 `P90-P100` 类别。最大的难点在于该值没有直接标注，必须通过数据点相对于Y轴的位置进行估读。由于Y轴的刻度间距高达10%，从视觉上精确读出 52.0 并满足5%的误差容限是完全不可能的。
> 
> ### 不确定的
> 
> 较低收入组别（如 `P0-P10` 到 `P30-P40`）的两条折线几乎完全重合在近乎0%的位置，单凭视觉无法分辨它们的确切数值差异。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 20 | Figure 17. | above | none |
| gpt-5.6-sol | f1 | line | 20 | Figure 17. | above | none |
| gemini-3.1-pro | f1 | line | 20 | Figure 17. | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | — | — | opus-5: categories written as percentile codes "P40–P50", "P50–P60" |
| `hgrid_only` | ✓ | — | ✓ | opus-5: dotted horizontal rules at 10% intervals; no vertical rules inside the plot；gemini-3.1-pro: horizontal dashed grid lines are drawn, no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: a single row "France  South Korea" with markers sits under the x tick labels；gpt-5.6-sol: The “France” and “South Korea” legend is centered below the plot.；gemini-3.1-pro: the France and South Korea legend sits below the x-axis |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: "Percentage of total political donations by income decile" set vertically in two lines on the left；gpt-5.6-sol: “Percentage of total political donations by income decile” runs vertically along the left axis.；gemini-3.1-pro: the y-axis title 'Percentage of total...' is set vertically |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: "P0–P10" through "P90–P100" set at roughly 45 degrees below the axis；gpt-5.6-sol: Income-decile labels from “P0–P10” to “P90–P100” are diagonally rotated.；gemini-3.1-pro: category labels like P0-P10 are rotated roughly 45 degrees |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: "Interpretation. Average shares of total political donations..." and "Sources and series: Cagé (2024)." below plot；gpt-5.6-sol: “Sources and series: Cagé (2024).” appears below the figure.；gemini-3.1-pro: Interpretation and Sources lines appear below the legend |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: subtitle reads "Political donations by income decile, % of total"; ticks are "0%".."60%"；gpt-5.6-sol: “Political donations by income decile, % of total” appears above the plot.；gemini-3.1-pro: subtitle has '% of total' and y-axis has 'Percentage' |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `overlapping_series_at_baseline` | opus-5 | 2,3 | France and South Korea lines coincide within 1% across P0–P10 to P30–P40, markers overprinted |
| `colored_figure_number_prefix` | opus-5 | 4 | "Figure 17." printed in green, the title text following in black bold on the same line |
| `marker_shape_per_series` | opus-5 | 3 | France drawn with a small cross/plus marker, South Korea with a filled square marker |
| `marker_shape_encodes_series` | gpt-5.6-sol | 3 | France uses blue diamonds; South Korea uses magenta squares along their lines. |
| `interpretation_caption` | gpt-5.6-sol | 4 | A paragraph beginning “Interpretation.” sits between the legend and source line. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 52.0 | France、P90–P100 | France、P90–P100 | P90–P100、France | France、P90-P100 | ✓ | ✓ | ✓ | 过 |
| 57.0 | South Korea、P90–P100 | South Korea、P90–P100 | P90–P100、South Korea | South Korea、P90-P100 | ✓ | ✓ | ✓ | 过 |
| 17.5 | France、P80–P90 | France、P80–P90 | P80–P90、France | France、P80-P90 | ✓ | ✓ | ✓ | 过 |
| 16.5 | South Korea、P80–P90 | South Korea、P80–P90 | P80–P90、South Korea | South Korea、P80-P90 | ✓ | ✓ | ✓ | 过 |
| 10.5 | France、P70–P80 | France、P70–P80 | P70–P80、France | France、P70-P80 | ✓ | ✓ | ✓ | 过 |
| 8.2 | South Korea、P70–P80 | South Korea、P70–P80 | P70–P80、South Korea | South Korea、P70-P80 | ✓ | ✓ | ✓ | 过 |
| 8.0 | France、P60–P70 | France、P60–P70 | P60–P70、France | France、P60-P70 | ✓ | ✓ | ✓ | 没过 |
| 5.8 | South Korea、P60–P70 | France、P50–P60 | P50–P60、France | South Korea、P60-P70 | ✗ | ✗ | ✓ | 没过 |
| 5.0 | France、P50–P60 | South Korea、P60–P70 | P60–P70、South Korea | France、P50-P60 | ✗ | ✗ | ✓ | 过 |
| 2.8 | South Korea、P50–P60 | South Korea、P50–P60 | P50–P60、South Korea | South Korea、P50-P60 | ✓ | ✓ | ✓ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
