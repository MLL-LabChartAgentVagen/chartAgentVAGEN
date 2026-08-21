# 2024_Annual_Financial_Review_Upstream_FINAL_p28

![2024_Annual_Financial_Review_Upstream_FINAL_p28](../../data/pages/2024_Annual_Financial_Review_Upstream_FINAL_p28.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `2024_Annual_Financial_Review_Upstream_FINAL_p28` | 2024_Annual_Financial_Review_Upstream_FINAL | need_estimate | 10 | `parsebench/data/pages/2024_Annual_Financial_Review_Upstream_FINAL_p28.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 一张双线折线图：深蓝"all U.S. manufacturing"与浅蓝"energy companies"，无图例，系列名直接以粗体彩字写在绘图区内（一个在线上方、一个在线下方）。标题分三层：页面顶部蓝色衬线句式结论"...at 42% and 56%"，图上方粗体图题，其下小字"percentage"作单位行。纵轴 0%–80%、每 10% 一条水平网格线，横轴 2015–2024 每年一刻度；无数据点标记、无数值标签。图下两行小字 Data source / Note（Note 中"Select energy companies"为斜体）。
> 
> **定位一个值难在哪**
> 以 energy companies 2019 的 55 为例：图上没有任何印出的数字，也没有点标记，只能在 50% 与 60% 网格线之间目测折点；5% 容差约 ±2.8 个百分点，需把网格间距十分之一读准。另外 56 出现两次（energy 2015 与 manufacturing 2024），行标签必须同时含系列名与年份才能唯一定位。
> 
> **不确定的**
> 各年是否真为逐年数据点（线段转折推断）；42/56 只在页面结论句中出现，是否算"图上印出"存疑；系列颜色与文字标签的对应靠位置推断，无图例可核。

**gpt-5.6-sol**

> **画出来要什么**
> 单面板双折线：2015—2024十个年度、左轴0%—80%、仅横向网格线。两条线在图内直接标为“all U.S. manufacturing”和“energy companies”。图上方需依次呈现黑色图题与单位“percentage”，更上方还有蓝色结论式页面标题；图下有数据来源和注释。
> 
> **定位一个值难在哪**
> “2018 / energy companies”的46须由折线相对10个百分点刻度读取；5%容差仅2.3个百分点。定位还必须同时保留年份和图内系列名。
> 
> **不确定的**
> 蓝色标题印有42%和56%，但未贴在折线标记上，按页面标题而非数值标签处理。若只看曲线，重复出现的56、65和约42无法脱离年份唯一定位。

**gemini-3.1-pro**

> ### 画出来要什么
> 
> 页面包含一个单面板的折线图。图表生成器需要支持不渲染图例，而是将系列名称（如“all U.S. manufacturing”）直接作为内联标签（inline labels）绘制在对应的折线附近。图表的标题区需要支持多行结构，包括粗体的主标题以及下方的普通字体单位行“percentage”。坐标轴方面，X轴需要绘制为一条加粗的底线，并带有年份刻度；Y轴不绘制垂直的主干线，仅依靠左侧的百分比标签和贯穿绘图区的水平网格线来提供参考。绘图区下方需要支持排版多行的小字号文本以容纳数据来源和注释（Source 和 Note）。此外，页面顶部有一段大字号的蓝色导语文本，这超越了单一图表的范畴，属于页面级别的排版。
> 
> ### 定位一个值难在哪
> 
> 以“2022年 energy companies 的值”（43）为例，该折线图上没有任何直接标注的数据标签。读者必须将线条上的点水平对齐到左侧的Y轴来读取数值。由于Y轴的水平网格线间距为10%，在一个10%的跨度内靠视觉估算精确到个位数（如分辨43和45）十分困难，极容易超出5%的误差容忍度。
> 
> ### 不确定的
> 
> 导语文本中的“42% and 56%”没有明确指出对应哪个具体年份，只能通过查看折线图末端（2024年）的值来推断是最新年份的数据。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 20 | — | above | none |
| gpt-5.6-sol | f1 | line | 20 | — | above | none |
| gemini-3.1-pro | f1 | line | 20 | — | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_title_above_axis` | — | ✓ | — | gpt-5.6-sol: “percentage” is placed above the 80% top tick, not beside the y axis. |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: faint horizontal rules at 10%..80%; no vertical rules across the panel；gpt-5.6-sol: Horizontal rules cross the plot at percentage ticks; no vertical grid lines are drawn.；gemini-3.1-pro: the plot has horizontal rules at every 10% interval, but no vertical grid lines |
| `inline_series_labels` | ✓ | ✓ | ✓ | opus-5: bold coloured text 'all U.S. manufacturing' and 'energy companies' sit inside the plot, no legend；gpt-5.6-sol: “all U.S. manufacturing” and “energy companies” are written beside their lines.；gemini-3.1-pro: series names 'all U.S. manufacturing' and 'energy companies' are written right beside their respective lines |
| `legend_inside_plot` | ✓ | — | — | opus-5: both series names are drawn over the plot area itself, at 2018 and 2022 positions |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Data source: Evaluate Energy and U.S. Census Bureau' and 'Note: Select energy companies includes 158 global oil...'；gpt-5.6-sol: “Data source: Evaluate Energy and U.S. Census Bureau” and a “Note:” line appear below.；gemini-3.1-pro: two lines of small print starting with 'Data source:' and 'Note:' sit below the x-axis |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: 'percentage' printed on its own line under the bold figure title；gpt-5.6-sol: “percentage” appears directly beneath the chart title.；gemini-3.1-pro: the word 'percentage' sits just under the bold figure title |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `takeaway_headline_with_values` | opus-5 | 2,4 | blue serif page headline: 'was relatively flat for the energy companies and U.S. manufacturing companies, at 42% and 56%' |
| `italic_defined_term_in_note` | opus-5 | 4 | 'Note: Select energy companies includes 158 global oil and natural gas companies.' with the term set in italics |
| `series_label_offset_from_line` | opus-5 | 3 | 'energy companies' sits ~15 points below its line near 2022, not at an endpoint |
| `page_takeaway_headline` | gpt-5.6-sol | 4 | “The long-term debt-to-equity ratio was relatively flat” appears in large blue type above the figure. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 63 | 2015、all U.S. manufacturing | all U.S. manufacturing、2015 | 2015、all U.S. manufacturing | all U.S. manufacturing、2015 | ✓ | ✓ | ✓ | 过 |
| 56 | 2015、energy companies | energy companies、2015 | 2015、energy companies | energy companies、2015 | ✓ | ✓ | ✓ | 过 |
| 72 | 2020、all U.S. manufacturing | all U.S. manufacturing、2020 | 2020、all U.S. manufacturing | all U.S. manufacturing、2020 | ✓ | ✓ | ✓ | 过 |
| 69 | 2020、energy companies | energy companies、2020 | 2020、energy companies | energy companies、2020 | ✓ | ✓ | ✓ | 过 |
| 56 | 2024、all U.S. manufacturing | all U.S. manufacturing、2024 | 2024、all U.S. manufacturing | all U.S. manufacturing、2024 | ✓ | ✓ | ✓ | 过 |
| 42 | 2024、energy companies | energy companies、2024 | 2024、energy companies | energy companies、2024 | ✓ | ✓ | ✓ | 没过 |
| 65 | 2018、all U.S. manufacturing | all U.S. manufacturing、2019 | 2018、all U.S. manufacturing | all U.S. manufacturing、2018 | ✗ | ✓ | ✓ | 过 |
| 46 | 2018、energy companies | energy companies、2018 | 2018、energy companies | energy companies、2018 | ✓ | ✓ | ✓ | 过 |
| 55 | 2022、all U.S. manufacturing | energy companies、2019 | 2022、all U.S. manufacturing | all U.S. manufacturing、2022 | ✗ | ✓ | ✓ | 过 |
| 43 | 2022、energy companies | energy companies、2022 | 2022、energy companies | energy companies、2022 | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 2 | 1 | 2 | 3 | 以实测为准：10 个点过 9 个，唯一的失败是 label_unlinked——`2024` 这个键写进了同一张表，只是不在这个值那一行（第三步）。三家报 2 / 1 / 2，无一命中。 |
