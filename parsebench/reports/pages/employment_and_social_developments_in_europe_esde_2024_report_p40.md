# employment_and_social_developments_in_europe_esde_2024_report_p40

![employment_and_social_developments_in_europe_esde_2024_report_p40](../../data/pages/employment_and_social_developments_in_europe_esde_2024_report_p40.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `employment_and_social_developments_in_europe_esde_2024_report_p40` | employment_and_social_developments_in_europe_esde_2024_report | need_estimate | 10 | `parsebench/data/pages/employment_and_social_developments_in_europe_esde_2024_report_p40.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一个编号为 `Chart 1` 的双面板折线图，标题与副标题分三行（`Chart 1` / 标题 / `Average and standard deviation of median net wealth, 2010 – 2021, euro area`），整体嵌在 `Box 2.1` 的浅底文本框里。左右两个面板各有自己的面板名（`Panel A: Median net wealth`、`Panel B: Dispersion of median wealth`）、自己的纵轴量纲（`€ 0`–`€ 180 000` 对 `0.5`–`0.66`，后者不从零起）和自己的图例（三条：14/19/21 countries，画在绘图区内部）。三条线起点不同：14 countries 从 2010 起，19 countries 从 2014 起，21 countries 只有 2017 与 2021 两点；x 轴四个刻度 2010、2014、2017、2021 时间间隔不等却等距排列。图下有 Notes 与 Source 两段小字，单位（2021 EUR PPS）只出现在 Notes 里。
> 
> ## 定位一个值难在哪
> 以 `120000` 为例：它可能是 `19 countries` 的 2014 点（约 118 000），也可能是 2017 年几乎重合的 `19 countries`（约 122 000）与 `21 countries`（约 121 000）。5% 容差为 6 000，而网格线间距 20 000，两条线的差距远小于容差，只能靠淡绿/黄两种颜色区分。一个值需要面板名＋系列名＋年份三重标签。
> 
> ## 不确定的
> 所有点值均无标注，只能靠轴读数；图例标记形状看不清；Panel A 的 19/21 countries 在 2021 年谁高谁低难以判定；面板绘图区是否有底色无法确认。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 一个双面板折线图：两面板各有独立标题、纵轴范围和内置图例，共用四个年份类别；Panel A 的欧元符号嵌入刻度，Panel B 使用小数刻度。图下还需 Notes 与 Source。
> 
> **定位一个值难在哪**
> 
> 例如 0.59 要由“Panel B: Dispersion of median wealth”“21 countries”“2017”三层标签定位；数值未印出，只能在 0.58 与 0.6 之间插读。
> 
> **不确定的**
> 
> 所有点值均未直接标注；160000、140000 等只能按坐标估读。marks 按可见数据点计数，未把连接线另算。

**gemini-3.1-pro**

> ### 画出来要什么
> 
> 要重新绘制此页面上的图表，生成器需要支持在一个图表（`Chart 1`）下放置两个平行的折线图面板（`Panel A`和`Panel B`）。每个面板都需要有自己的标题，并且拥有独立的Y轴（一个起点为0，另一个起点为0.5）和内置图例。X轴为时间，且年份间隔不一致（如2014到2017差3年，2017到2021差4年），但在图表上各类别的节点需等间距排列。同时需支持仅显示横向虚线网格线，并在图表区域下方渲染多行的注释与数据来源说明。
> 
> ### 定位一个值难在哪
> 
> 所有的值均为非打印值，完全依赖视觉对齐刻度线。以Panel A为例，Y轴最大范围达`180 000`且网格间隔达`20 000`，要在5%的容差内读取特定的数据点（如2014年的`145000`）难度极大，极其容易因肉眼读数偏差而阻塞在第2步。
> 
> ### 不确定的
> 
> Panel A中`19 countries`在2014年的折线节点目测略低于`120 000`的网格线（大约为115000），但由于这是提供的最接近考点`120000`的值，因此假设该点即为目标点。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 18 | Chart 1 | above | none |
| gpt-5.6-sol | f1 | line | 18 | Chart 1 | above | none |
| gemini-3.1-pro | f1 | line | 18 | Chart 1 | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_starts_above_zero` | ✓ | — | ✓ | opus-5: Panel B lowest tick reads 0.5, no break glyph on the axis；gemini-3.1-pro: Panel B left y-axis starts at 0.5 |
| `footnote_marker` | ✓ | — | — | opus-5: 'Household Finance and Consumption Survey (HFCS), (1)' with numbered footnotes at page foot |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: faint horizontal rules at each value tick in both panels, no vertical rules；gpt-5.6-sol: Both panels draw dotted horizontal grid lines and no vertical grid lines.；gemini-3.1-pro: only horizontal dashed grid lines are drawn |
| `legend_inside_plot` | ✓ | ✓ | ✓ | opus-5: legend rows drawn over the plot area just above the 2010–2021 tick row；gpt-5.6-sol: Each legend is drawn inside its panel immediately above the bottom time axis.；gemini-3.1-pro: legend items sit inside the plot area |
| `panel_title_per_panel` | ✓ | ✓ | ✓ | opus-5: 'Panel A: Median net wealth' and 'Panel B: Dispersion of median wealth' above each plot；gpt-5.6-sol: “Panel A: Median net wealth” and “Panel B: Dispersion of median wealth” are printed above their panels.；gemini-3.1-pro: Panel A and Panel B are titled individually |
| `per_panel_axis_range` | ✓ | ✓ | ✓ | opus-5: Panel A ticks '€ 0'–'€ 180 000'; Panel B ticks '0.5'–'0.66'；gpt-5.6-sol: Panel A spans € 0–€ 180 000; Panel B spans 0.5–0.66.；gemini-3.1-pro: Panel A and Panel B have different y-axis scales |
| `per_panel_legend` | ✓ | ✓ | ✓ | opus-5: each panel carries its own '14 countries / 19 countries / 21 countries' legend；gpt-5.6-sol: Both Panel A and Panel B repeat legends for “14 countries”, “19 countries”, and “21 countries”.；gemini-3.1-pro: each panel has its own legend inside |
| `small_multiples_4` | ✓ | — | — | opus-5: two line panels side by side under one 'Chart 1' heading |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Notes: Median household net wealth in 2021 EUR purchasing power standard (PPS)...' and 'Source: OECD calculations...'；gpt-5.6-sol: “Notes:” and “Source:” lines appear directly beneath the two panels.；gemini-3.1-pro: Notes: and Source: lines at the bottom |
| `unit_in_axis_or_title` | ✓ | — | — | opus-5: Panel B ticks bare 0.5...0.66; scale named only in subtitle 'standard deviation of median net wealth' |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `staggered_series_start` | opus-5 | 3 | '14 countries' spans 2010-2021, '19 countries' starts at 2014, '21 countries' only 2017 and 2021 |
| `panels_measure_different_quantities` | opus-5 | 2,3 | Panel A plots euro levels, Panel B plots a 0.5-0.66 dispersion index; not the same chart resliced |
| `uneven_time_ticks_evenly_spaced` | opus-5 | 3 | ticks 2010, 2014, 2017, 2021 drawn at equal horizontal spacing despite unequal intervals |
| `currency_symbol_in_tick_labels` | opus-5 | 2 | Panel A ticks written '€ 180 000', '€ 20 000' with euro prefix and space separator |
| `figure_inside_text_box` | opus-5 | 4 | chart sits inside a bordered tinted box headed 'Box 2.1: Convergence in national wealth levels and distribution' |
| `unit_in_tick_labels` | gpt-5.6-sol | 4 | Panel A ticks repeat the currency symbol, from “€ 0” to “€ 180 000”. |
| `marker_shape_encodes_series` | gpt-5.6-sol | 3 | Diamonds, triangles, and crosses distinguish the three country-count series in both legends and lines. |
| `uneven_time_spacing_drawn_evenly` | gemini-3.1-pro | — | time gaps 4, 3, 4 years are drawn visually equidistant |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 160000 | 2010、14 countries | Panel A: Median net wealth、14 countries、2010 | Panel A: Median net wealth、14 countries、2010 | Panel A: Median net wealth、14 countries、2010 | ✓ | ✓ | ✓ | 过 |
| 140000 | 2014、14 countries | Panel A: Median net wealth、14 countries、2014 | Panel A: Median net wealth、14 countries、2014 | Panel A: Median net wealth、21 countries、2021 | ✓ | ✓ | ✗ | 过 |
| 120000 | 2014、19 countries | Panel A: Median net wealth、19 countries、2014 | Panel A: Median net wealth、19 countries、2014 | Panel A: Median net wealth、19 countries、2014 | ✓ | ✓ | ✓ | 过 |
| 145000 | 2021、21 countries | Panel A: Median net wealth、19 countries、2021 | Panel A: Median net wealth、21 countries、2021 | Panel A: Median net wealth、14 countries、2014 | ✗ | ✓ | ✗ | 过 |
| 0.56 | 2010、14 countries | Panel B: Dispersion of median wealth、14 countries、2010 | Panel B: Dispersion of median wealth、14 countries、2010 | Panel B: Dispersion of median wealth、14 countries、2010 | ✓ | ✓ | ✓ | 过 |
| 0.64 | 2014、19 countries | Panel B: Dispersion of median wealth、19 countries、2014 | Panel B: Dispersion of median wealth、19 countries、2014 | Panel B: Dispersion of median wealth、19 countries、2014 | ✓ | ✓ | ✓ | 过 |
| 0.58 | 2017、14 countries | Panel B: Dispersion of median wealth、14 countries、2017 | Panel B: Dispersion of median wealth、14 countries、2017 | Panel B: Dispersion of median wealth、21 countries、2021 | ✓ | ✓ | ✗ | 过 |
| 0.59 | 2017、21 countries | Panel B: Dispersion of median wealth、21 countries、2017 | Panel B: Dispersion of median wealth、21 countries、2017 | Panel B: Dispersion of median wealth、14 countries、2017 | ✓ | ✓ | ✗ | 过 |
| 0.53 | 2021、14 countries | Panel B: Dispersion of median wealth、14 countries、2021 | Panel B: Dispersion of median wealth、14 countries、2021 | Panel B: Dispersion of median wealth、14 countries、2021 | ✓ | ✓ | ✓ | 过 |
| 0.56 | 2021、19 countries | Panel B: Dispersion of median wealth、19 countries、2021 | Panel B: Dispersion of median wealth、19 countries、2021 | Panel B: Dispersion of median wealth、19 countries、2021 | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 3 | 1 | 2 | 未裁决 · 无实测证据 | 这一页 10 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 1 / 2 都无法证伪。 |
