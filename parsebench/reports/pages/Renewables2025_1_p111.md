# Renewables2025_1_p111

![Renewables2025_1_p111](../../data/pages/Renewables2025_1_p111.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `Renewables2025_1_p111` | Renewables2025_1 | 3d_chart+need_estimate | 10 | `parsebench/data/pages/Renewables2025_1_p111.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 一个无编号、蓝色两行标题（`Weighted average net margins of renewable energy companies and large utilities` / `(Q1 2023-Q2 2025)`）压在细横线下的图组；两个并排小图，各自带面板标题 `China`、`Outside of China`；每面板 10 个季度槽、最多 4 个系列的分组柱，正负双向，纵轴 `30%`…`-30%`，横轴两层刻度（`Q1 Q2 Q3 Q4` 上层，`2023`/`2024`/`2025` 下层带分隔）；左侧竖排轴标题 `Weighted average net margin`；两面板共用一行四项图例在下方；再加 `IEA. CC BY 4.0.`、Note、Source 三段小字。右面板完全没有 Polysilicon 系列，属于“面板间系列集合不同”的空槽。
> 
> **定位一个值难在哪**
> 以 28 为例：它是 China 面板 2023 年 Q1 的深灰 Polysilicon 柱。地址需要四段标签——面板名 + 年 + 季度 + 图例名，而年和季度分在两层刻度里，面板名只写在小图上方。数值未标注，网格每 10 个百分点一条，28 要在两条线之间目测；对 1.3 这种贴零柱，5% 容差约 0.07 个百分点，肉眼不可能。
> 
> **不确定的**
> 近零柱（0、2、1.3）具体属于哪个季度哪个系列无法确认；部分柱是缺失还是高度为零看不出；-7 在两面板各有一根相近的柱，无法唯一指认。

**gpt-5.6-sol**

> ### 画出来要什么
> 双面板分组柱图，每面板含季度与年份两层时间轴、重复的百分比纵轴、负值和加粗零线；共享四系列图例置于下方，并保留竖排轴题、面板标题、注释和来源行。
> 
> ### 定位一个值难在哪
> “1.3”需以“China / 2023 / Q4 / Solar PV integrated mfg”四键定位；数值未印出，而纵轴每格10个百分点，远大于其5%容差0.065。
> 
> ### 不确定的
> 零高度柱可能与缺值无法区分；若干精确值只能按柱端位置和给定数值反推。图中未见图号，标题第二行按副标题处理。

**gemini-3.1-pro**

> ### 画出来要什么
> 这是一个包含左右两个面板的柱状图，分别展示“China”和“Outside of China”的数据。每个面板均有独立的标题和底部的双层分类/时间轴（年份嵌套季度，季度间带有垂直分隔线）。两个面板共享同一个包含四个系列的底部图例，但各面板实际只展示了其中的三个系列（China面板没有Utilities，Outside of China没有Polysilicon）。Y轴标题旋转了90度，网格线仅有水平线，每10%一条，数值范围包含负数，图表中未直接标注数据标签。
> 
> ### 定位一个值难在哪
> 以值为 `-17` 的柱子为例，要准确寻址该值，需要组合面板标题“China”、X轴外层标签“2024”、内层标签“Q3”以及从图例映射颜色的系列名“Polysilicon”。困难在于，Y轴网格线间距为10%，柱子较细且没有数值标签，依靠肉眼将其与 `-15` 或 `-18` 区分并读到 5% 的容差范围内几乎不可能。
> 
> ### 不确定的
> 无法在图表或正文中找到值为 `28` 的准确对应项。另外，某些极小的柱形（如China面板中Q1 2023的Wind integrated mfg）具体值是 `1.3` 还是其他微小正数难以确切核实，只能合理猜测。图例项在底部分隔成两组的排版意图也无法完全确定。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | grouped_bar | 66 | — | above | none |
| gpt-5.6-sol | f1 | grouped_bar | 70 | — | above | none |
| gemini-3.1-pro | f1 | grouped_bar | 60 | — | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: up to four coloured bars sit side by side inside each quarter slot；gpt-5.6-sol: Multiple coloured bars stand side by side within each quarterly slot.；gemini-3.1-pro: bars are placed side by side for each quarter |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: horizontal rules at 30%, 20%, 10%, 0%, -10%, -20%, -30%; no vertical rules；gpt-5.6-sol: Only horizontal grey grid lines cross each plot area.；gemini-3.1-pro: horizontal grid lines at 10% intervals, with no vertical grid |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: legend row drawn beneath both plot areas, above 'IEA. CC BY 4.0.'；gpt-5.6-sol: The four legend entries form one row beneath the two plots.；gemini-3.1-pro: the legend is placed below the entire chart area |
| `missing_value_marker` | ✓ | — | — | opus-5: Outside of China panel draws no Polysilicon bar in any quarter slot |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: axis runs 30% to -30% and bars hang below the 0% line in both panels；gpt-5.6-sol: Bars extend below the 0% line toward ticks down to -30%.；gemini-3.1-pro: the y-axis extends down to -30% with bars hanging below zero |
| `nonstandard_time_ticks` | — | ✓ | — | gpt-5.6-sol: “Q1”, “Q2”, “Q3” and “Q4” are used as time ticks. |
| `panel_title_per_panel` | ✓ | ✓ | ✓ | opus-5: bold 'China' and 'Outside of China' centred above each plot；gpt-5.6-sol: “China” and “Outside of China” are centred above their respective panels.；gemini-3.1-pro: 'China' and 'Outside of China' are printed over the respective plot areas |
| `per_panel_axis_range` | ✓ | — | — | opus-5: each panel draws its own -30%..30% tick column rather than one shared axis |
| `reference_line` | — | ✓ | — | gpt-5.6-sol: A dark horizontal zero line crosses both panels at 0%. |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Weighted average net margin' set vertically along the left axis；gpt-5.6-sol: “Weighted average net margin” runs vertically beside the left panel.；gemini-3.1-pro: 'Weighted average net margin' is rotated vertically along the left axis |
| `shared_legend` | ✓ | ✓ | ✓ | opus-5: one legend row 'Polysilicon / Solar PV integrated mfg / Utilities / Wind integrated mfg' under both panels；gpt-5.6-sol: One four-item legend spans beneath both “China” and “Outside of China” panels.；gemini-3.1-pro: a single legend at the bottom covers both panels |
| `small_multiples_4` | ✓ | ✓ | — | opus-5: two panels of the same grouped bar chart, China and Outside of China；gpt-5.6-sol: The same quarterly grouped-bar construction repeats in two panels. |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: mfg = equipment manufacturing companies.' and 'Source: IEA analysis based on Bloomberg LP (2025)...'；gpt-5.6-sol: “Note: mfg = equipment manufacturing companies.” and “Source: IEA analysis based on Bloomberg LP…” appear below.；gemini-3.1-pro: Note and Source paragraphs are printed in small text under the figure |
| `two_level_x_ticks` | ✓ | ✓ | ✓ | opus-5: 'Q1 Q2 Q3 Q4' boxes over a second row reading '2023', '2024', '2025'；gpt-5.6-sol: Quarter labels Q1–Q4 sit above grouped year labels 2023–2025.；gemini-3.1-pro: quarters sit on top of grouped year labels |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `series_subset_per_panel` | opus-5 | 3 | China panel shows four legend series; Outside of China panel shows only three, Polysilicon absent |
| `unnumbered_figure_heading` | opus-5 | 3,4 | blue two-line heading under a rule, no 'Figure n' anywhere on the page |
| `rights_line_below_figure` | opus-5 | — | 'IEA. CC BY 4.0.' set right-aligned between the legend and the Note line |
| `unit_in_tick_labels` | gpt-5.6-sol | 2 | Every value tick includes “%”, from -30% through 30%; the axis title omits it. |
| `panel_specific_series_presence` | gpt-5.6-sol | 3 | Purple Utilities bars appear only in Outside of China although the shared legend lists Utilities. |
| `heterogeneous_series_by_panel` | gemini-3.1-pro | 1,3 | China panel lacks Utilities; Outside panel lacks Polysilicon |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 28 | China、2023、Q1、Polysilicon | China、2023、Q1、Polysilicon | China、2023、Q1、Polysilicon | not_found | ✓ | ✓ | ✗ | 过 |
| -17 | China、2024、Q4、Polysilicon | China、2024、Q4、Polysilicon | China、2024、Q4、Polysilicon | China、2024、Q3、Polysilicon | ✓ | ✓ | ✗ | 过 |
| 0 | China、2024、Q4、Wind integrated mfg | China、2024、Q1、Polysilicon | China、2024、Q4、Wind integrated mfg | Outside of China、2024、Q3、Wind integrated mfg | ✗ | ✓ | ✗ | 过 |
| -7 | China、2025、Q2、Solar PV integrated mfg | China、2023、Q4、Polysilicon | China、2025、Q2、Solar PV integrated mfg | China、2024、Q4、Solar PV integrated mfg | ✗ | ✓ | ✗ | 过 |
| 2 | Outside of China、2023、Q4、Utilities | China、2024、Q1、Wind integrated mfg | China、2023、Q3、Wind integrated mfg | China、2025、Q1、Wind integrated mfg | ✗ | ✗ | ✗ | 没过 |
| -7 | Outside of China、2023、Q4、Wind integrated mfg | Outside of China、2024、Q2、Wind integrated mfg | China、2023、Q4、Polysilicon | Outside of China、2023、Q2、Wind integrated mfg | ✗ | ✗ | ✗ | 过 |
| 7 | Outside of China、2024、Q4、Utilities | China、2023、Q3、Solar PV integrated mfg | China、2023、Q3、Polysilicon | Outside of China、2023、Q3、Solar PV integrated mfg | ✗ | ✗ | ✗ | 没过 |
| 1.3 | Outside of China、2024、Q4、Wind integrated mfg | Outside of China、2024、Q4、Utilities | China、2023、Q4、Solar PV integrated mfg | China、2023、Q1、Wind integrated mfg | ✗ | ✗ | ✗ | 没过 |
| 10 | Outside of China、2025、Q2、Utilities | Outside of China、2025、Q2、Utilities | Outside of China、2023、Q1、Polysilicon | Outside of China、2024、Q1、Utilities | ✓ | ✗ | ✗ | 过 |
| -5 | Outside of China、2025、Q2、Wind integrated mfg | Outside of China、2023、Q4、Wind integrated mfg | Outside of China、2024、Q3、Wind integrated mfg | Outside of China、2025、Q2、Wind integrated mfg | ✗ | ✗ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `density#f1` | "61–150" | "61–150" | "21–60" | 61–150（按中位数 66 个图元） | 三家数出的图元个数是 66 / 70 / 60，中位数 66，落在 61–150。三个数彼此相差不到一半，分歧是<档的边界>而不是读法：它们看的是同一张图，只是刚好被 20 / 60 / 150 / 400 这几条线切开。 |
