# 2024-ltra_corrected_july_2025_p29

![2024-ltra_corrected_july_2025_p29](../../data/pages/2024-ltra_corrected_july_2025_p29.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `2024-ltra_corrected_july_2025_p29` | 2024-ltra_corrected_july_2025 | need_estimate | 10 | `parsebench/data/pages/2024-ltra_corrected_july_2025_p29.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一张单面板堆叠柱图：8 个年份槽（2017–2024），两段堆叠（Interstate 浅蓝在上、Intrastate 深蓝在下），左侧纵轴 0–30、步长 5，仅有水平网格线，纵轴标题「Pipeline Additions」竖排且不含单位；图例横排在绘图区下方；再往下是加粗居中的两行说明「Figure 16: Annual U.S. Natural Gas Pipeline Capacity Additions by Type (2017–2024) Bcf/d (Source: U.S. Energy Information Administration)」——编号、标题、年份范围、单位、来源挤在同一句里。整页还要能把这张图排进右栏，与左栏正文并列，图下继续接「Reliability Implications」小节。
> 
> ## 定位一个值难在哪
> 以 8.5（2021 年 Interstate）为例：图上一个数字都没写，该段悬在 7.3 与 15.8 之间，必须先读段顶再减段底；5% 容差只有 ±0.43，而两条网格线之间就是 5 个单位。更极端的 1.2（2017 Intrastate）容差仅 ±0.06，约等于一个像素。地址还需「2017」＋「Intrastate」两个标签，都只在轴刻度和图例里。
> 
> ## 不确定的
> 2022 年是否真有 Intrastate 段（看不到深蓝）、2024 年那条极薄的深蓝到底是哪一系列；纵轴单位是否就是标题里的「Bcf/d」也只能由说明文字推断。

**gpt-5.6-sol**

> **画出来要什么**：重建单面板堆叠柱图：2017–2024八个年份，Interstate与Intrastate两色堆叠；左轴0–30、每5一格，竖排“Pipeline Additions”，仅有横网格。图例、粗体图题、Bcf/d及来源均在图下；图左并排正文并以竖线分栏。
> 
> **定位一个值难在哪**：1.2对应“2017”与“Intrastate”的深蓝底段。图上不印数值；其5%仅0.06，而网格间隔为5，虽标签组合明确，精度仍难保证。
> 
> **不确定的**：柱段数按可见非零段计为14；2022无可见Intrastate、2024无可见Interstate，无法确认是零值还是未绘制。标题换行按语义合并，来源实际嵌在粗体图注中。

**gemini-3.1-pro**

> ### 画出来要什么
> 生成器需要支持绘制堆叠柱状图，并在图表下方放置图例和图表标题。Y轴标题“Pipeline Additions”需要支持90度旋转。图表区域只需要水平网格线。此外，页面布局需要支持左侧大段正文与右侧图表并排的排版方式。
> 
> ### 定位一个值难在哪
> 定位和读取数值非常困难，这会导致在Step 2卡住。以“2017 Interstate”的值（16.2）为例，图表中并未标注具体数值，必须根据堆叠的浅蓝色柱段上下端点对应到左侧Y轴进行估算。Y轴的刻度间隔为5，要求肉眼从浮空的柱段中读出精确到小数点后一位的数值（且满足5%的容差范围）是不可能的。
> 
> ### 不确定的
> 2024年的柱子非常低，仅能看到深蓝色部分，由于缺乏数据标签，无法确定2024年Interstate的值是否为0或者存在极其微小的数值。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 15 | Figure 16 | below | none |
| gpt-5.6-sol | f1 | stacked_bar | 14 | Figure 16 | below | none |
| gemini-3.1-pro | f1 | stacked_bar | 16 | Figure 16 | below | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: horizontal rules at 5,10,15,20,25,30 across the panel; no vertical rules；gpt-5.6-sol: Horizontal rules cross the plot at 0, 5, …, 30; no vertical gridlines are drawn.；gemini-3.1-pro: horizontal grid lines across the panel, no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'Interstate' and 'Intrastate' swatches sit in a row under the 2017–2024 tick row；gpt-5.6-sol: The Interstate and Intrastate legend is centered between the plot and caption.；gemini-3.1-pro: legend sits below the x-axis, above the figure title |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Pipeline Additions' set vertically along the left axis；gpt-5.6-sol: “Pipeline Additions” is rotated vertically along the left axis.；gemini-3.1-pro: Pipeline Additions is rotated 90 degrees along the left axis |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: left column of body text ('The 2024 LTRA projects...') runs level with the figure, divider rule between；gpt-5.6-sol: Running prose occupies the left column beside Figure 16, separated by a vertical rule.；gemini-3.1-pro: a main column of body text runs alongside the figure |
| `source_note_lines` | ✓ | — | — | opus-5: caption ends '(Source: U.S. Energy Information Administration)' |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: each year's bar has a dark lower segment and a light upper segment, total is the bar height；gpt-5.6-sol: Each year has light Interstate stacked above dark Intrastate segments.；gemini-3.1-pro: bars are divided into light and dark blue segments |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: y ticks read 0,5,...30 bare; 'Bcf/d' appears only in the caption line；gpt-5.6-sol: The below-plot caption includes “Bcf/d”; the value-axis title is “Pipeline Additions”.；gemini-3.1-pro: Bcf/d is written in the figure title |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `caption_bundles_number_title_unit_source` | opus-5 | 3,4 | 'Figure 16: ... by Type (2017–2024) Bcf/d (Source: U.S. Energy Information Administration)' is one bold sentence |
| `legend_order_reverses_stack_order` | opus-5 | 3 | legend lists 'Interstate' first but Interstate is drawn as the upper segment above 'Intrastate' |
| `series_absent_in_some_slots` | opus-5 | 2,3 | 2022 shows only a light bar; 2024 shows only a sliver near zero |
| `source_in_figure_caption` | gpt-5.6-sol | 4 | “(Source: U.S. Energy Information Administration)” is embedded in the bold caption rather than a separate note. |
| `vertical_column_divider` | gpt-5.6-sol | 4 | A vertical black rule separates the left prose column from the right figure and prose. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 16.2 | 2017、Interstate | 2017、Interstate | 2017、Interstate | Interstate、2017 | ✓ | ✓ | ✓ | 过 |
| 1.2 | 2017、Intrastate | 2017、Intrastate | 2017、Intrastate | Intrastate、2017 | ✓ | ✓ | ✓ | 过 |
| 21.2 | 2018、Interstate | 2018、Interstate | 2018、Interstate | Interstate、2018 | ✓ | ✓ | ✓ | 过 |
| 5.6 | 2018、Intrastate | 2018、Intrastate | 2018、Intrastate | Intrastate、2018 | ✓ | ✓ | ✓ | 过 |
| 10.8 | 2019、Interstate | 2019、Interstate | 2019、Interstate | Interstate、2019 | ✓ | ✓ | ✓ | 过 |
| 4.2 | 2019、Intrastate | 2019、Intrastate | 2019、Intrastate | Intrastate、2019 | ✓ | ✓ | ✓ | 过 |
| 8.7 | 2020、Interstate | 2020、Interstate | 2020、Interstate | Interstate、2020 | ✓ | ✓ | ✓ | 过 |
| 1.6 | 2020、Intrastate | 2020、Intrastate | 2020、Intrastate | Intrastate、2020 | ✓ | ✓ | ✓ | 过 |
| 8.5 | 2021、Interstate | 2021、Interstate | 2021、Interstate | Interstate、2021 | ✓ | ✓ | ✓ | 过 |
| 7.3 | 2021、Intrastate | 2021、Intrastate | 2021、Intrastate | Intrastate、2021 | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
