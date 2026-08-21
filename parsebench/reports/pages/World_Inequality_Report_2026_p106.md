# World_Inequality_Report_2026_p106

![World_Inequality_Report_2026_p106](../../data/pages/World_Inequality_Report_2026_p106.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `World_Inequality_Report_2026_p106` | World_Inequality_Report_2026 | need_estimate | 7 | `parsebench/data/pages/World_Inequality_Report_2026_p106.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一个编号图 `Figure 5.2`，标题两行加一条居中副标题 `Excess yield (assets–liabilities) as % of group GDP, 1970–2025`，下面并排两个折线面板，各有自己的面板标题（`By income group` / `By world region`）、自己的 % 刻度轴（3% 到 −6%）、自己的图例（左5条、右9条，图例排在面板下方两列）。左面板还有一条旋转的轴标题 `Excess yield (% of group GDP), MER`，右面板没有。两板都画一条 0% 的虚线零轴，1970–2025 逐年数据但刻度只到每十年一格。图下是一段带粗体引导词 `Interpretation.` 与 `Sources and series:` 的小字。
> 
> ## 定位一个值难在哪
> 以 2.1 为例：它只能是右面板 `NAOC` 红线 2024 前后的末端高点。图上没有任何数字，刻度 1% 一格，2.1 的 5% 容差约 ±0.1pp，即约刻度间距的十分之一；而 `NAOC`、`Europe`、`EASA (excl. China)` 三条线在 2020 后彼此交叠。一行表还必须同时带上面板名、图例缩写和年份三个键，年份还不是刻度上印着的。
> 
> ## 不确定的
> 面板内是否真有淡横向网格线看不清；各线的具体年份取值全靠目测；`RUCA`、`SSAF` 等缩写在本页没有展开说明。

**gpt-5.6-sol**

> ### 画出来要什么
> 两幅并列折线面板、各自标题与图例；14条年度序列共用−6%至3%的视觉尺度，并绘制负值、0%参考线、双向虚线网格及下方解释和来源段落。标题须拆分为编号、主标题、副标题和单位。
> 
> ### 定位一个值难在哪
> 例如0.8：纵轴相邻刻度相差1个百分点，而5%容差仅±0.04；折线无点标、无数值标签，且年份仅每十年标一次，无法唯一可靠定位。
> 
> ### 不确定的
> 线条顶点数按1970–2025逐年数据估算；给定七个数均未印在图中，多个年份和序列可能经过相同数值，因此未猜测其地址。

**gemini-3.1-pro**

> ### 画出来要什么
> 要绘制此页面，生成器需要支持：
> 1. **多面板折线图**：并排的两个独立面板，每个面板有自己的面板标题（`By income group`和`By world region`）、时间轴（相同的刻度）以及独立的Y轴刻度。
> 2. **分组的图例布局**：图例统一置于图表下方，但在视觉和逻辑上分为左右两个区块，分别对应上方不同的面板数据列。
> 3. **坐标轴与参考线**：左侧面板旁设置了旋转的纵轴标题（包含单位说明），两个面板的Y轴范围涵盖负值（-6%到3%），并在0%处绘制了水平的虚线参考线；X轴则是每10年一标的稀疏时间刻度。
> 4. **高密度多重线系**：支持十余条无数据标签且颜色相近、互相交织的细折线绘制。
> 
> ### 定位一个值难在哪
> 以定位“NAOC线在2025年的值（2.1）”为例，该点位于右侧面板红色折线的最末端。由于Y轴的总跨度高达9%（从-6%至3%），图表高度相对较小，且完全缺乏数据标签，试图通过肉眼将线条高度水平对齐到左侧Y轴并读出2.1的具体数值，是根本无法达到5%容差精度的。这会在数值读取步骤（Step 2）造成严重阻碍。
> 
> ### 不确定的
> 具体的折线数据采样频率。虽然X轴的标签为10年一跨度，且子标题标明1970-2025，但中间每年的微小波动并未绘制数据点标记（marker），因此只能推断其为年度数据而无法从图元特征上直接确证。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 784 | Figure 5.2. | above | none |
| gpt-5.6-sol | f1 | line | 784 | Figure 5.2. | above | none |
| gemini-3.1-pro | f1 | line | 770 | Figure 5.2. | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: 14 series over ~56 annual points across two panels；gpt-5.6-sol: Fourteen annual lines span 1970–2025 across two panels, approximately 784 vertices.；gemini-3.1-pro: 14 series lines spanning over 50 years |
| `hgrid_only` | ✓ | — | ✓ | opus-5: faint horizontal rules at each % tick inside both panels; no vertical rules；gemini-3.1-pro: horizontal dotted grid lines, no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: both legends sit in rows underneath their plot areas, outside them；gpt-5.6-sol: Both colour legends sit beneath their respective plotting areas.；gemini-3.1-pro: the legend row sits below the two panels |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: y ticks run 3%, 2%, 1%, 0%, −1% ... −6%; most lines sit below zero；gpt-5.6-sol: Both value axes extend from “-6%” through 0% to “3%”.；gemini-3.1-pro: the y-axis starts at -6% |
| `panel_title_per_panel` | ✓ | ✓ | ✓ | opus-5: 'By income group' above the left plot, 'By world region' above the right plot；gpt-5.6-sol: “By income group” and “By world region” are printed above the panels.；gemini-3.1-pro: titles 'By income group' and 'By world region' above panels |
| `per_panel_legend` | ✓ | ✓ | — | opus-5: left legend lists Bottom 20%...Top 20%; a separate right legend lists China...SSEA；gpt-5.6-sol: Income-group labels appear below the left panel; region labels below the right. |
| `reference_line` | ✓ | ✓ | ✓ | opus-5: a black dotted horizontal rule drawn at the 0% level across both panels；gpt-5.6-sol: A darker dotted horizontal rule crosses 0% in both panels.；gemini-3.1-pro: a horizontal dotted zero line across both panels |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Excess yield (% of group GDP), MER' set vertically along the left panel's y axis；gpt-5.6-sol: “Excess yield (% of group GDP), MER” runs vertically beside the left panel.；gemini-3.1-pro: the title 'Excess yield...' is vertical beside the left axis |
| `small_multiples_4` | ✓ | ✓ | — | opus-5: two line panels side by side, 'By income group' and 'By world region'；gpt-5.6-sol: Two adjacent line-chart panels repeat the same time and percentage structure. |
| `source_note_lines` | ✓ | ✓ | — | opus-5: 'Sources and series: wir2026.wid.world/methodology and Nievas and Sodano (2025).'；gpt-5.6-sol: The paragraph below the legends includes “Interpretation.” and “Sources and series:”. |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: annual lines 1970–2025 but ticks only at 1980, 1990, 2000, 2010, 2020；gpt-5.6-sol: Annual lines cover “1970–2025”, but visible ticks are only 1980, 1990, 2000, 2010, 2020.；gemini-3.1-pro: ticks every 10 years for annual data lines |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: 'as % of group GDP' in the subtitle; right panel ticks carry only '3%'...'−6%'；gpt-5.6-sol: The subtitle says “as % of group GDP”; the left axis repeats “(% of group GDP), MER”. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `abbrev_series_legend` | opus-5 | 3 | legend entries 'EASA (excl. China)', 'NAOC', 'RUCA', 'SSAF', 'SSEA' are undefined codes |
| `interpretation_paragraph_below_figure` | opus-5 | 4 | bold 'Interpretation.' opens an eight-line prose block between the legends and the body text |
| `panel_axis_title_on_first_panel_only` | opus-5 | 3 | left panel carries the rotated y title; the right panel's identical % axis carries none |
| `unequal_series_sets_by_panel` | gpt-5.6-sol | 3 | The left panel has five legend entries; the right panel has nine different entries. |
| `interpretation_caption_block` | gpt-5.6-sol | 4 | A substantial paragraph beginning “Interpretation.” sits between the legends and body text. |
| `panel_specific_legends_below_plot` | gemini-3.1-pro | 3 | the legend has two separate blocks aligned under their respective panels |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 0.8 | Top 20%、2010 | By income group、Top 20%、2010 | not_found | By income group、Top 20%、2010 | ✓ | ✗ | ✓ | 过 |
| -1.5 | Bottom 20%、2010 | By income group、Bottom 20%、2020 | not_found | By income group、Bottom 20%、2020 | ✗ | ✗ | ✗ | 过 |
| -2 | 60%−80%、2000 | By income group、60%–80%、2020 | not_found | By income group、40%-60%、2020 | ✗ | ✗ | ✗ | 过 |
| 2.1 | NAOC、2020 | By world region、NAOC、2020 | not_found | By world region、NAOC、2025 | ✓ | ✗ | ✗ | 过 |
| -3.2 | SSAF、2010 | By world region、LATA、2010 | not_found | By income group、60%-80%、2000 | ✗ | ✗ | ✗ | 没过 |
| 1.3 | Europe、2010 | By world region、Europe、2020 | not_found | By world region、NAOC、2015 | ✗ | ✗ | ✗ | 没过 |
| -3.5 | LATA、1990 | By income group、40%–60%、2020 | not_found | By world region、SSAF、2020 | ✗ | ✗ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
