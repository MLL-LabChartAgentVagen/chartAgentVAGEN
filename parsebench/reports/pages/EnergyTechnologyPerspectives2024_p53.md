# EnergyTechnologyPerspectives2024_p53

![EnergyTechnologyPerspectives2024_p53](../../data/pages/EnergyTechnologyPerspectives2024_p53.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `EnergyTechnologyPerspectives2024_p53` | EnergyTechnologyPerspectives2024 | 3d_chart+need_estimate | 10 | `parsebench/data/pages/EnergyTechnologyPerspectives2024_p53.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一张 100% 堆叠柱图：11 个类别（EV and battery … Oil）、6 个图例系列（China…Rest of World），共约 66 个堆叠段，全部不标数值。纵轴刻度自带百分号「0%、20%…100%」，没有轴标题。横轴是两层：内层技术名（多行折行，如「EV and battery」「Heat pumps」），外层用方括号分成「Technology manufacturing」与「Fossil fuel supply」。图例横排在绘图区下方，右下角有「IEA. CC BY 4.0.」，下面两行小字 Note/Source，再下面是一句加粗蓝色结论句。标题行为「Figure 1.14   Energy employment in selected energy technologies by region, 2022」，编号与标题同一行。
> 
> ## 定位一个值难在哪
> 以 20（Hydro 的 China 段）为例：柱高 100% 对应约 236 像素，1 个百分点仅 2.4 像素；5% 容差即 ±1pp，眼读几乎不可能稳定命中；而 Hydro 里 Middle East 那条橙色只有约 2pp，必须靠相邻边界相减才能得到，且顺序还得靠颜色对图例。地址需要三个标签：外层组、技术名、系列名。
> 
> ## 不确定的
> 绘图区是否有横向网格线看不清；Wind、Nuclear、Bioenergy 各段边界只能目测，19、38、37、40、25 归到哪一段属于推测；极薄段（如 Coal 的 European Union）是否真实存在无法确认。

**gpt-5.6-sol**

> **画出来要什么**
> 单面板百分比堆叠柱图：11种技术、6个地区，所有柱到100%。需画20个百分点横向网格、柱下两级分类及分组括线、图下共享图例、注释、来源和加粗结论。
> 
> **定位一个值难在哪**
> “Nuclear”中“Other Asia Pacific”的19需要同时用类别轴和图例定位，并由堆叠段上下边界相减。其5%容差仅0.95个百分点，远小于20个百分点的刻度间隔。
> 
> **不确定的**
> 图中没有数值标签；各给定值的位置按柱高和颜色判断。极薄或零值分段不可清楚区分，标记总数为估计。

**gemini-3.1-pro**

> ### 画出来要什么
> 这是一个百分比堆叠柱状图。Y轴显示百分比，刻度间隔为20%。X轴需要支持双层分组标签：内层是具体的11种技术类别（部分长标签如“EV and battery”需要换行），外层用“Technology manufacturing”和“Fossil fuel supply”对内层标签进行分组并添加顶部分隔线。图例包含6个系列，放置在X轴下方。图表主体有水平网格线，无垂直网格线。图表最下方有出处说明以及一段加粗的总结文本。
> 
> ### 定位一个值难在哪
> 以定位 Natural gas 的 Rest of World 值为例（数值为38）。它在图表中位于最顶端的悬空堆叠段，图上未直接标注数值。读者必须将其顶部（100%）和底部（约62%）分别水平对齐到左侧间隔宽达20%的Y轴上进行两次估读，然后再相减计算。这几乎不可能用肉眼将误差控制在5%（约1.9%）以内。
> 
> ### 不确定的
> 部分堆叠段（例如 Middle East 系列在 EV and battery 和 Battery storage 类别中）在图上未显示或极薄，无法从图中确切确认其数值是绝对的0还是极小的百分比值。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 66 | Figure 1.14 | above | none |
| gpt-5.6-sol | f1 | stacked_bar | 56 | Figure 1.14 | above | none |
| gemini-3.1-pro | f1 | stacked_bar | 66 | Figure 1.14 | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `footnote_marker` | ✓ | — | — | opus-5: 'Note: EV = electric vehicles.' expands the abbreviation used in the category label 'EV and battery' |
| `hgrid_only` | — | ✓ | ✓ | gpt-5.6-sol: Horizontal rules cross the plot at percentage ticks; no vertical grid lines are drawn.；gemini-3.1-pro: horizontal grid lines sit behind the bars, with no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'China  European Union  Middle East  North America  Other Asia Pacific  Rest of World' in a row under the axis；gpt-5.6-sol: The six-entry regional legend is arranged in one row below the category labels.；gemini-3.1-pro: the legend sits below the category axis and grouping labels |
| `pct_stacked` | ✓ | ✓ | ✓ | opus-5: axis ticks 0%, 20%, 40%, 60%, 80%, 100% and every bar tops out at 100%；gpt-5.6-sol: All eleven stacks reach “100%”; the left axis runs from “0%” to “100%”.；gemini-3.1-pro: the y axis ends at 100% and all bars reach the top tick |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: EV = electric vehicles.' and 'Source: Adapted from IEA (2023d).' under the plot；gpt-5.6-sol: “Note: EV = electric vehicles.” and “Source: Adapted from IEA (2023d).” appear below.；gemini-3.1-pro: Note: and Source: lines sit below the legend |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: each technology is one bar built of six coloured segments from China up to Rest of World；gpt-5.6-sol: Each technology is one vertical bar divided into regional colour segments.；gemini-3.1-pro: bars are divided into vertically stacked coloured segments |
| `two_level_x_ticks` | ✓ | ✓ | ✓ | opus-5: technology names row, below it brackets labelled 'Technology manufacturing' and 'Fossil fuel supply'；gpt-5.6-sol: Technology names sit above grouped labels “Technology manufacturing” and “Fossil fuel supply”.；gemini-3.1-pro: Technology manufacturing and Fossil fuel supply sit below the main categories |
| `wrapped_category_labels` | ✓ | ✓ | ✓ | opus-5: 'EV and battery', 'Battery storage', 'Heat pumps', 'Natural gas' wrap onto two lines；gpt-5.6-sol: “EV and battery”, “Battery storage”, “Heat pumps”, and “Natural gas” wrap onto two lines.；gemini-3.1-pro: EV and battery, Battery storage, and Heat pumps wrap onto two lines |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `bold_key_message_below_figure` | opus-5 | 4 | bold blue sentence under source lines: 'Most manufacturing jobs for electric vehicles and batteries, renewables and heat pumps are located in China...' |
| `rights_statement_line` | opus-5 | 4 | 'IEA. CC BY 4.0.' right-aligned between plot and note lines, repeated rotated in the page margin |
| `group_bracket_axis` | opus-5 | 3 | square-bracket rules under the tick row span bars 1-8 and bars 9-11 with a group name |
| `unit_in_tick_labels` | gpt-5.6-sol | 2 | Left-axis ticks read “0%”, “20%”, through “100%”; no separate unit title appears. |
| `bold_takeaway_below_figure` | gpt-5.6-sol | 4 | “Most manufacturing jobs for electric vehicles and batteries” begins a bold blue takeaway below the notes. |
| `figure_takeaway_text` | gemini-3.1-pro | 4 | bold text summarizing the chart sits below source lines |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 73 | China、EV and battery、Technology manufacturing | EV and battery、China | EV and battery、China | EV and battery、China | ✗ | ✗ | ✗ | 过 |
| 91 | China、Battery storage、Technology manufacturing | Battery storage、China | Battery storage、China | Battery storage、China | ✗ | ✗ | ✗ | 过 |
| 82 | China、Solar PV、Technology manufacturing | Solar PV、China | Solar PV、China | Solar PV、China | ✗ | ✗ | ✗ | 过 |
| 19 | European Union、Wind、Technology manufacturing | Natural gas、Middle East | Nuclear、Other Asia Pacific | EV and battery、European Union | ✗ | ✗ | ✗ | 过 |
| 38 | Other Asia Pacific、Coal、Fossil fuel supply | Natural gas、Rest of World | Oil、Rest of World | Natural gas、Rest of World | ✗ | ✗ | ✗ | 没过 |
| 37 | Rest of World、Oil、Fossil fuel supply | Oil、Rest of World | Coal、Other Asia Pacific | Oil、Rest of World | ✗ | ✗ | ✗ | 过 |
| 20 | North America、Heat pumps、Technology manufacturing | Hydro、China | Hydro、China | Hydro、China | ✗ | ✗ | ✗ | 过 |
| 40 | Other Asia Pacific、Hydro、Technology manufacturing | Nuclear、China | Hydro、Other Asia Pacific | Hydro、Other Asia Pacific | ✗ | ✗ | ✗ | 过 |
| 54 | China、Coal、Fossil fuel supply | Coal、China | Coal、China | Wind、China | ✗ | ✗ | ✗ | 过 |
| 25 | Middle East、Oil、Fossil fuel supply | Hydro、Rest of World | Oil、Middle East | Bioenergy、North America | ✗ | ✗ | ✗ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `density#f1` | "61–150" | "21–60" | "61–150" | 61–150（按中位数 66 个图元） | 三家数出的图元个数是 66 / 56 / 66，中位数 66，落在 61–150。三个数彼此相差不到一半，分歧是<档的边界>而不是读法：它们看的是同一张图，只是刚好被 20 / 60 / 150 / 400 这几条线切开。 |
