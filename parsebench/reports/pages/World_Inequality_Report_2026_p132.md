# World_Inequality_Report_2026_p132

![World_Inequality_Report_2026_p132](../../data/pages/World_Inequality_Report_2026_p132.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `World_Inequality_Report_2026_p132` | World_Inequality_Report_2026 | need_estimate | 9 | `parsebench/data/pages/World_Inequality_Report_2026_p132.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 一张单面板多线图：5 条带点标记的折线（Brazil / France / Netherlands / Spain / United States），x 轴 16 个不等宽的分位组（`P0–10` … `P99.999–P99.9999`、`Billionaires`），标签整体旋转约 45°；y 轴 `0%`–`25%`，只有水平虚网格；旋转的长轴标题 `Effective income tax rates by income groups and for billionaires (% of pre–tax income)`。还要能画：从 `P0–10` 到 `P95–99` 的灰色底纹带，带内一个带边框的说明框 `99% of the population are located in the shaded area.`；图号+标题一行、再单独一行加粗副标题 `Effective income tax rates by income groups`；图下居中图例与两段小字注（`Interpretation.` / `Sources and series:`）。
> 
> **定位一个值难在哪**
> 以 10（Brazil 在 `P95–99` 的峰值≈10.1）为例：图上无任何数字，网格每 5%，5% 容差只有 ±0.5，即约网格间距的 1/10；绿线此处正压在灰底纹边缘，且需同时给出系列名与分位标签两个键才能唯一定位。
> 
> **不确定的**
> 各线起点不同（Netherlands 似从 `P10–20`、Spain 似从 `P20–30` 开始），点数与总标记数为估算；红线峰值落在哪一个分位格无法确定；给定的 18、15 各出现两次，无法判断分别属于哪条线。

**gpt-5.6-sol**

> **画出来要什么**：单面板五系列折线图；顶部拆分图号、主标题和副标题；左侧纵排百分比轴，底部16个倾斜分位组标签。线条带不同点形，图内有灰色“99%”区间及方框说明，图例、解读和来源置于图下。
> 
> **定位一个值难在哪**：如 United States 的 P90–95 为12.5，必须同时匹配倾斜类别与下方图例；数值未印出，只能在10%和15%网格线之间估读。
> 
> **不确定的**：若干点和线可能重叠，约73个点为目测；给定的重复值18和15无法仅凭数值唯一反推指定点。

**gemini-3.1-pro**

> ### 画出来要什么
> 
> 生成器需要绘制一个折线图，包含5条跨越16个分类的折线。X轴为非线性的分类轴（代表人口百分比），所有刻度标签（如`P0-10`至`Billionaires`）需倾斜45度。图表左半部分（覆盖从`P0-10`到`P99-99.9`的分类）需带有灰色背景着色。此外，绘图区内需绘制一个带边框的文本框（内容为“99% of the population...”），并配有一条折线指示到该着色区域的右侧边界。Y轴标题包含换行符并整体垂直旋转放置，图例单行水平排列在图表下方。
> 
> ### 定位一个值难在哪
> 
> 全图没有任何数据点标注具体数值，所有值都必须通过Y轴刻度读取。以美国在 `P90-95` 处的值（约12.5%）为例，Y轴仅在 0%, 5%, 10%, 15% 等位置有水平网格线，要求将此点读数精确到5%的容差内（即11.875到13.125之间）在视觉上极具挑战，大部分取值会在这一步判定失败。
> 
> ### 不确定的
> 
> 由于缺乏数据标签，测试样例中的所有确切数值（如7、9、16、18）都只能近似对应到特定的国家和百分比区间节点，无法保证其就是原始数据中的精确值。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 77 | Figure 7.2. | above | none |
| gpt-5.6-sol | f1 | line | 73 | Figure 7.2. | above | none |
| gemini-3.1-pro | f1 | line | 80 | Figure 7.2. | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | — | — | opus-5: axis reads P0–10, P10–20 …; note says "P0–10 denotes the bottom 10%" |
| `annotation_callout` | ✓ | ✓ | ✓ | opus-5: boxed note inside plot: "99% of the population are located in the shaded area."；gpt-5.6-sol: Boxed note inside plot reads “99% of the population are located in the shaded area.”；gemini-3.1-pro: a boxed text '99% of the population...' pointing to the shaded area |
| `hgrid_only` | ✓ | — | ✓ | opus-5: dashed horizontal rules at 5%, 10%, 15%, 20%, 25%; no vertical rules；gemini-3.1-pro: horizontal grid lines at 5% intervals, no vertical lines |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: row "Brazil France Netherlands Spain United States" centred under the plot；gpt-5.6-sol: The Brazil-to-United States legend is centred below the rotated category labels.；gemini-3.1-pro: the legend with country names sits below the x-axis |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: vertical text "Effective income tax rates by income groups and for billionaires (% of pre–tax income)"；gpt-5.6-sol: The effective-income-tax axis title runs vertically along the left side.；gemini-3.1-pro: the four-line y-axis title runs vertically alongside the axis |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: P0–10 … Billionaires set at roughly 45 degrees under the axis；gpt-5.6-sol: Labels from “P0–10” through “Billionaires” are angled diagonally.；gemini-3.1-pro: x-axis labels like P0-10 are angled |
| `shaded_band` | ✓ | ✓ | ✓ | opus-5: grey tinted vertical band spanning P0–10 through P95–99 behind the lines；gpt-5.6-sol: A grey vertical band spans P0–10 through P95–99.；gemini-3.1-pro: grey background fill from P0-10 to P99-99.9 |
| `source_note_lines` | ✓ | ✓ | — | opus-5: "Interpretation. This figure shows..." and "Sources and series: Artola et al. (2022)..." below plot；gpt-5.6-sol: “Interpretation.” and “Sources and series:” introduce text directly beneath the legend. |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: "(% of pre–tax income)" written in the rotated left-axis title；gpt-5.6-sol: The vertical axis title ends “(% of pre-tax income)”.；gemini-3.1-pro: % of pre-tax income is written in the y-axis title |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `unequal_width_category_bins` | opus-5 | 3 | deciles P0–10…P70–80 then P90–95, P99–99.9, P99.999–P99.9999, Billionaires in equal-width slots |
| `bold_lead_in_note_paragraph` | opus-5 | 4 | note paragraph opens with bold run-in labels "Interpretation." and "Sources and series:" |
| `series_start_at_different_categories` | opus-5 | 1,3 | Netherlands line begins at P10–20 and Spain at P20–30; earlier slots have no marker |
| `marker_shape_encodes_series` | gpt-5.6-sol | 3 | Country lines use square, diamond, triangle, circle and hexagonal point markers, repeated in the legend. |
| `two_dimensional_grid` | gpt-5.6-sol | — | Dashed horizontal and vertical gridlines cross the plot. |
| `categorical_shaded_band` | gemini-3.1-pro | 1 | the shaded area spans a specific subset of categorical x-axis bins |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 9 | United States、Billionaires | United States、Billionaires | P70–80、United States | Spain、P70-80 | ✓ | ✗ | ✗ | 过 |
| 18 | Netherlands、P80-90 | United States、P99–99.9 | P99–99.9、United States | United States、P99-99.9 | ✗ | ✗ | ✗ | 过 |
| 15 | France、P95-99 | France、P95–99 | P60–70、Netherlands | France、P95-99 | ✓ | ✗ | ✓ | 过 |
| 16 | Spain、P99-99.9 | France、P99.9–99.99 | P70–80、Netherlands | France、P99-99.9 | ✗ | ✗ | ✗ | 过 |
| 18 | United States、P99-99.9 | Netherlands、P80–90 | P80–90、Netherlands | not_found | ✗ | ✗ | ✗ | 过 |
| 7 | Brazil、P90-95 | France、P40–50 | P90–95、Brazil | Brazil、P90-95 | ✗ | ✓ | ✓ | 过 |
| 12.5 | Netherlands、P50-60 | Spain、P99.99–P99.999 | P90–95、United States | United States、P90-95 | ✗ | ✗ | ✗ | 过 |
| 15 | France、P99.9-99.99 | Spain、P95–99 | P95–99、Spain | Spain、P95-99 | ✗ | ✗ | ✗ | 过 |
| 10 | Spain、P99.99-P99.999 | Brazil、P95–99 | P95–99、Brazil | Brazil、P95-99 | ✗ | ✗ | ✗ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 2 | 1 | 2 | 3 | 以实测为准：9 个点过 8 个，唯一的失败是 label_unlinked——`spain` 与 `p99.99-p99.999` 都写进了同一张表，只是不在这个值那一行（第三步）。三家报 2 / 1 / 2，无一命中。 |
