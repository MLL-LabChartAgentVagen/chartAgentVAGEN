# b263dc5d-en_p95

![b263dc5d-en_p95](../../data/pages/b263dc5d-en_p95.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `b263dc5d-en_p95` | b263dc5d-en | 3d_chart+need_estimate | 10 | `parsebench/data/pages/b263dc5d-en_p95.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一个编号图 `Figure 2.20`、一行副标题、三个带填色横幅的面板(`A. Literacy`/`B. Numeracy`/`C. Adaptive problem solving`),共用一个位于顶部的图例(方块 `Unadjusted` + 菱形 `Adjusted`)。每个面板 32 个国家、竖排 90° 旋转标签、条形上叠加菱形点(约 192 个 marks),y 轴 0–80、只有横向网格线,轴标题 `Score-point difference` 写在最高刻度之上。`OECD average` 用浅蓝竖带+加粗标签突出,`Flemish Region (BE)`、`England (UK)` 标签为蓝色,`Poland*` 带脚注星号。三个面板各自按本面板的 unadjusted 值降序重排,国家顺序不一致。
> 
> ## 定位一个值难在哪
> 以 `42` 为例:它是 A. Literacy 面板 Israel 的 Adjusted 菱形。要唯一定位需四个标签:图号/面板名 `A. Literacy`、类别 `Israel`、系列 `Adjusted`。图上没有任何数字,刻度间隔 10 分,5% 容差只有 ±2.1 分,只能靠像素在 40–45 间估读;而 Israel 在 B、C 面板同样有 ~34 的菱形,缺面板名就会串行。
> 
> ## 不确定的
> 所有数值均为按轴估读,±2 分内无法确定;`75`、`70`、`65` 究竟落在 A 面板 Germany/Switzerland 还是 B/C 面板的同名条上无法分辨;菱形中心位置在条形阴影中略被遮挡;页面无 StatLink 行(可能被裁掉)。

**gpt-5.6-sol**

> **画出来要什么**
> 三联小多图：每面板32个国家或地区，浅蓝柱叠加黑色菱形，共约192个标记。还需共享上方图例、蓝色面板标题条、横向网格、旋转国家标签、OECD average竖向高亮带，以及完整注释和来源。
> 
> **定位一个值难在哪**
> 例如“B. Numeracy—Japan—Adjusted”的18须同时依靠面板、国家和系列三层标签定位。数值未印出，纵轴每10分一格，而5%容差仅0.9分。
> 
> **不确定的**
> 所有给定值都只能按柱顶或菱形中心估读；75及重复的24可能对应其他非常接近的标记。

**gemini-3.1-pro**

> ### 画出来要什么
> 本页包含一个图表（Figure 2.20），它由三个子图（A. Literacy, B. Numeracy, C. Adaptive problem solving）组成的小多图（small multiples）构成。图表为混合标记（mixed marks），在每根代表“Unadjusted”的柱子上，都叠加了代表“Adjusted”的菱形散点，且散点带有垂直误差线。图例位于整个图表的顶部，各子图共享同一组图例和相似的坐标轴设置。需要特别注意的是，虽然三个子图的分类轴相同，但每个子图中的国家排列顺序是独立的（根据柱状图高度降序排列），并且参考类别（OECD average）在所有子图中均有贯穿全图的垂直浅蓝色高亮背景。
> 
> ### 定位一个值难在哪
> 以 Panel A 中的 `27`（United States, Adjusted）为例，难度在于图表中没有任何直接打印的数值标签（即触发步骤 2 的读取精度问题）。读者需要根据 0-80 范围、刻度间距为 10 的 Y 轴网格线进行视觉估算。此外，菱形散点本身就被一根很长的垂直误差线穿过，极大地干扰了对其中心位置的判定，导致极难将读数误差控制在 5% 的容忍度以内。
> 
> ### 不确定的
> 图表附注仅提到“所有差异在 5% 的水平上具有统计学显著性”，并未明确菱形散点附带的细黑线是置信区间还是标准差。另外，由于缺乏具体的数值表格，较低的刻度（如 Spain 的某些读数）存在较大的主观估读偏差。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | compound | 192 | Figure 2.20. | above | none |
| gpt-5.6-sol | f1 | compound | 192 | Figure 2.20. | above | none |
| gemini-3.1-pro | f1 | bar | 192 | Figure 2.20. | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | — | — | opus-5: category labels 'Flemish Region (BE)', 'England (UK)' carry bracketed country codes |
| `axis_title_above_axis` | ✓ | ✓ | ✓ | opus-5: 'Score-point difference' printed above the 80 tick at the top-left of each panel；gpt-5.6-sol: “Score-point difference” is printed horizontally above the top-left of each value axis.；gemini-3.1-pro: Score-point difference is placed above the top tick on the y-axis |
| `color_encodes_extra_attribute` | ✓ | — | — | opus-5: 'Flemish Region (BE)' and 'England (UK)' tick labels printed in blue, others black |
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: 3 panels x 32 countries x 2 series = about 192 marks；gpt-5.6-sol: Three panels each contain 32 bars and 32 diamonds, about 192 marks total.；gemini-3.1-pro: over 190 marks counted across 32 categories and 3 panels |
| `error_bars` | — | — | ✓ | gemini-3.1-pro: thin vertical lines extending through the diamond markers |
| `footnote_marker` | ✓ | ✓ | ✓ | opus-5: 'Poland*' on the category axis; note reads '*Caution is required in interpreting results'；gpt-5.6-sol: The category label “Poland*” is explained by “*Caution is required” in the note.；gemini-3.1-pro: an asterisk symbol is attached to Poland* |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: horizontal rules at 10,20,...,80 across each panel; no vertical grid；gpt-5.6-sol: Horizontal rules cross each plot at 10-point intervals; no vertical grid lines are drawn.；gemini-3.1-pro: horizontal gridlines drawn at 10-point intervals, with no vertical gridlines |
| `highlighted_category` | ✓ | ✓ | ✓ | opus-5: 'OECD average' label in bold with a pale blue column behind it in each panel；gpt-5.6-sol: “OECD average” is bold and backed by a pale blue strip in every panel.；gemini-3.1-pro: OECD average has a shaded blue background to distinguish it |
| `legend_above_plot` | ✓ | ✓ | ✓ | opus-5: legend row sits between the subtitle and the 'A. Literacy' panel；gpt-5.6-sol: The “Unadjusted” and “Adjusted” legend sits between the subtitle and panel A.；gemini-3.1-pro: the legend sits between the main heading and the first panel |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: black diamonds ('Adjusted') drawn on top of the light blue bars in every panel；gpt-5.6-sol: Pale vertical bars and black diamond markers overlap at every country in all three panels.；gemini-3.1-pro: grey bars and black diamond point markers overlaid |
| `panel_title_per_panel` | ✓ | ✓ | ✓ | opus-5: filled dark-blue banners 'A. Literacy', 'B. Numeracy', 'C. Adaptive problem solving'；gpt-5.6-sol: Each panel has a dark-blue banner carrying its own lettered title.；gemini-3.1-pro: A. Literacy, B. Numeracy, and C. Adaptive problem solving in blue banners |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: country names such as 'Slovak Republic' set vertically, rotated 90 degrees；gpt-5.6-sol: All country and economy labels are rotated vertically beneath the panels.；gemini-3.1-pro: country category labels are rotated 90 degrees vertically |
| `shaded_band` | ✓ | ✓ | ✓ | opus-5: pale blue vertical band spanning the plot height at the OECD average slot；gpt-5.6-sol: A pale blue vertical band spans the OECD average slot in every panel.；gemini-3.1-pro: vertical light blue band highlighting the OECD average across the plot |
| `shared_legend` | ✓ | ✓ | ✓ | opus-5: one legend 'Unadjusted  Adjusted' above panel A governs all three panels；gpt-5.6-sol: One “Unadjusted” and “Adjusted” legend governs all three panels.；gemini-3.1-pro: a single legend above panel A serves all three panels |
| `small_multiples_4` | ✓ | ✓ | ✓ | opus-5: three stacked panels A, B, C of the same bar+diamond chart；gpt-5.6-sol: Three repeated panels are titled “A. Literacy”, “B. Numeracy”, and “C. Adaptive problem solving”.；gemini-3.1-pro: three panels stacked vertically with similar structures |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: Adults aged 16-65...' and 'Source: Table A.2.12 (L, N, A) in Annex A.'；gpt-5.6-sol: “Note: Adults aged 16-65” and “Source: Table A.2.12 (L, N, A) in Annex A.” appear below.；gemini-3.1-pro: Note: Adults aged 16-65... Source: Table A.2.12... |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: bare ticks 0..80; scale word only in 'Score-point difference'；gpt-5.6-sol: “Score-point difference” appears above each left axis whose ticks read 0 through 80. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `per_panel_category_order` | opus-5 | 3 | 'ranked in descending order of the unadjusted difference'; Hungary is 5th in A, 4th in B, 3rd in C |
| `marker_shape_encodes_series` | opus-5 | 3 | legend shows a square for 'Unadjusted' and a diamond for 'Adjusted'; shape, not colour, separates them |
| `per_panel_category_order` | gpt-5.6-sol | 3 | Country order changes between “A. Literacy”, “B. Numeracy”, and “C. Adaptive problem solving”. |
| `per_panel_category_sort` | gemini-3.1-pro | 3 | the order of countries on the x-axis differs in each panel |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 75 | A. Literacy、Germany、Unadjusted | A. Literacy、Germany、Unadjusted | A. Literacy、Germany、Unadjusted | A. Literacy、Germany、Unadjusted | ✓ | ✓ | ✓ | 过 |
| 23 | A. Literacy、Spain、Adjusted | A. Literacy、Poland*、Adjusted | A. Literacy、France、Adjusted | A. Literacy、Spain、Unadjusted | ✗ | ✗ | ✓ | 过 |
| 24 | A. Literacy、OECD average、Adjusted | A. Literacy、Latvia、Adjusted | B. Numeracy、France、Adjusted | C. Adaptive problem solving、Slovak Republic、Unadjusted | ✗ | ✗ | ✗ | 没过 |
| 70 | B. Numeracy、United States、Unadjusted | A. Literacy、Switzerland、Unadjusted | A. Literacy、Switzerland、Unadjusted | B. Numeracy、United States、Unadjusted | ✗ | ✗ | ✓ | 过 |
| 18 | B. Numeracy、Japan、Adjusted | A. Literacy、Japan、Adjusted | B. Numeracy、Japan、Adjusted | B. Numeracy、Sweden、Adjusted | ✗ | ✓ | ✗ | 没过 |
| 27 | B. Numeracy、Spain、Unadjusted | A. Literacy、Chile、Adjusted | B. Numeracy、Canada、Adjusted | A. Literacy、United States、Adjusted | ✗ | ✗ | ✗ | 过 |
| 65 | C. Adaptive problem solving、Germany、Unadjusted | C. Adaptive problem solving、Germany、Unadjusted | B. Numeracy、Switzerland、Unadjusted | C. Adaptive problem solving、Germany、Unadjusted | ✓ | ✗ | ✓ | 过 |
| 24 | C. Adaptive problem solving、New Zealand、Adjusted | B. Numeracy、Croatia、Adjusted | A. Literacy、Spain、Unadjusted | A. Literacy、Flemish Region (BE)、Adjusted | ✗ | ✗ | ✗ | 过 |
| 25 | C. Adaptive problem solving、Netherlands、Adjusted | A. Literacy、OECD average、Adjusted | C. Adaptive problem solving、Canada、Adjusted | A. Literacy、Canada、Adjusted | ✗ | ✗ | ✗ | 没过 |
| 42 | C. Adaptive problem solving、OECD average、Unadjusted | A. Literacy、Israel、Adjusted | C. Adaptive problem solving、England (UK)、Unadjusted | C. Adaptive problem solving、OECD average、Unadjusted | ✗ | ✗ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "compound" | "compound" | "bar" | compound | 按类型表自己的定义判：`compound` 是<strong>同一个面板里出现两种以上图元形状</strong>，所以决定它的是三家自己在 `components` 里记的 `mixed_marks`，不是它们给这张图起的名字。三家都记了 `mixed_marks`，图元数都是 192。 |
