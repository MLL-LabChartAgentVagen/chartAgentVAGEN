# employment_and_social_developments_in_europe_esde_2024_report_p84

![employment_and_social_developments_in_europe_esde_2024_report_p84](../../data/pages/employment_and_social_developments_in_europe_esde_2024_report_p84.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `employment_and_social_developments_in_europe_esde_2024_report_p84` | employment_and_social_developments_in_europe_esde_2024_report | need_estimate | 10 | `parsebench/data/pages/employment_and_social_developments_in_europe_esde_2024_report_p84.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 一张单面板多线图：5 条彩色折线（Quintile 1–5），横轴逐年刻度 `2021`…`2040`（20 格，每年一刻度），纵轴 `0.00`–`0.16`、步长 0.02，只有横向点状网格线；纵轴标题竖排 `% deviation from baseline`；图例横排在绘图区下方。标题块分四层：`Chart 3.11`、蓝色标题句、灰色小字副标题（单位写在副标题括号里）、其后 `Note:` / `Source:` 与一行下载链接 `Click here to download chart.`。全图 100 个数据点，无任何数值标签。
> 
> **定位一个值难在哪**
> 
> 以 0.138 为例：它是 2027 年 Quintile 5 的峰值，没有印在图上。网格线间距 0.02，而 5% 容差只有 ±0.007，即需把一格目测到三分之一以内；且 2027 附近红线（Quintile 4，约 0.122）与蓝线相距不到一格半。行地址还需同时给出 `Quintile 5` 与 `2027`，图例只靠颜色区分五条线。
> 
> **不确定的**
> 
> 各线在 2021 全部汇聚于 0.02，无法判断 0.02 属于哪条序列；0.10 与 0.03 有多个可能落点（Quintile 5 约 2034 年、Quintile 1 约 2030 年低谷）；正文所述 “+0.11% in 2027” 未在图上标出，无法确认对应哪条曲线或均值。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 需绘制“Chart 3.11”的五条彩色年度折线、2021—2040逐年刻度、0.00—0.16纵轴、仅水平虚线网格，以及图下图例、Note、Source和下载链接。标题、副标题与“% deviation from baseline”纵轴标题均须保留。
> 
> **定位一个值难在哪**
> 
> 例如0.03需定位为“2031 / Quintile 1”。它没有数值标签，容差仅±0.0015，而纵轴每格0.02，且折线无点标，精读困难。
> 
> **不确定的**
> 
> 所有值均由坐标估读；2021附近多线重合，0.02的系列归属不清。0.04、0.10等也可能在其他年份或系列重复出现。

**gemini-3.1-pro**

> ### 画出来要什么
> 要重绘此页面，生成器需要支持标准的单面板折线图，包含多条数据线（共5个数据系列）。图表标题块包含图表编号、主标题、副标题，并且放置在图表正上方；其中y轴标题带有旋转文本，图表区域内部仅包含虚线的水平网格线，没有垂直网格线。同时，图表下方需要配置图例（按行排列），并在图表外部底部追加注释（Note）、来源（Source）以及额外的数据下载链接（Click here to download chart.）。
> 
> ### 定位一个值难在哪
> 以 0.138 为例（“Quintile 5”在2027年的峰值），难点完全在于缺乏数据标注。y轴的刻度间距为 0.02（如从 0.12 到 0.14），而 0.138 是一个处于这两条网格线之间、极为靠近 0.14 但又未接触的值。肉眼或视觉模型都极难在没有数据表的情况下精准读取到三位小数并满足5%的误差容忍度。
> 
> ### 不确定的
> 正文提到“reaching a peak of +0.11% in 2027 (Chart 3.11)”，但图表中仅显示了五个收入五等分组（Quintiles）的单独曲线，并未绘制表示总体平均 0.11% 的折线或标记。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 100 | Chart 3.11 | above | none |
| gpt-5.6-sol | f1 | line | 100 | Chart 3.11 | above | none |
| gemini-3.1-pro | f1 | line | 100 | Chart 3.11 | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `data_link_below_figure` | ✓ | ✓ | ✓ | opus-5: 'Click here to download chart.' printed under the Source line；gpt-5.6-sol: “Click here to download chart.” appears below the source line.；gemini-3.1-pro: `Click here to download chart.` below the source |
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: 5 quintile lines over 20 yearly points, 2021 to 2040；gpt-5.6-sol: Five lines each span 20 annual positions, totalling 100 plotted vertices.；gemini-3.1-pro: 5 series over 20 years yields exactly 100 marks |
| `footnote_marker` | ✓ | — | — | opus-5: bold lead-in 'active labour market policies (182)' with superscript note markers, footnotes listed at page foot |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: dotted horizontal rules at 0.02 intervals across the panel, no vertical rules；gpt-5.6-sol: Dotted horizontal grid lines cross the plot; no vertical grid lines are drawn.；gemini-3.1-pro: dotted horizontal grid lines, no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: row 'Quintile 1  Quintile 2  Quintile 3  Quintile 4  Quintile 5' under the x axis；gpt-5.6-sol: The Quintile 1–5 legend is centered below the time axis.；gemini-3.1-pro: the quintile legend sits under the x-axis |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: '% deviation from baseline' set vertically along the left axis；gpt-5.6-sol: “% deviation from baseline” is rotated vertically beside the left axis.；gemini-3.1-pro: the y-axis title is rotated vertically |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: Income quintile 5 indicates the richest quintile...' and 'Source: JRC calculations based on RHOMOLO model.'；gpt-5.6-sol: “Note:” and “Source: JRC calculations based on RHOMOLO model.” appear below the plot.；gemini-3.1-pro: contains Note and Source lines below the chart |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: subtitle ends '(% deviation from baseline)'; y ticks are bare 0.00-0.16；gpt-5.6-sol: The subtitle and y-axis title state “% deviation from baseline”.；gemini-3.1-pro: the subtitle specifies `(% deviation from baseline)` |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `converging_series_at_origin` | opus-5 | 2,3 | all five lines start at the same 0.02 point in 2021 and are indistinguishable there |
| `value_quoted_in_body_text` | opus-5 | 2,4 | 'reaching a peak of +0.11% in 2027 (Chart 3.11)' in the paragraph below the chart |
| `coincident_series_marks` | gpt-5.6-sol | 2,3 | Five coloured lines meet or nearly overlap around 0.02 at 2021. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 0.138 | 2027、Quintile 5 | Chart 3.11、Quintile 5、2027 | 2028、Quintile 5 | Quintile 5、2027 | ✓ | ✗ | ✓ | 过 |
| 0.122 | 2027、Quintile 4 | Chart 3.11、Quintile 4、2027 | 2027、Quintile 4 | Quintile 4、2027 | ✓ | ✓ | ✓ | 过 |
| 0.095 | 2027、Quintile 3 | Chart 3.11、Quintile 2、2027 | 2027、Quintile 2 | Quintile 3、2027 | ✗ | ✗ | ✓ | 没过 |
| 0.09 | 2027、Quintile 1 | Chart 3.11、Quintile 1、2027 | 2027、Quintile 1 | Quintile 2、2027 | ✓ | ✓ | ✗ | 过 |
| 0.078 | 2040、Quintile 5 | Chart 3.11、Quintile 5、2040 | 2025、Quintile 2 | Quintile 1、2027 | ✓ | ✗ | ✗ | 过 |
| 0.04 | 2040、Quintile 1 | Chart 3.11、Quintile 1、2040 | 2036、Quintile 1 | Quintile 1、2038 | ✓ | ✗ | ✗ | 过 |
| 0.02 | 2021、Quintile 1 | Chart 3.11、Quintile 1、2021 | 2021、Quintile 1 | Quintile 1、2021 | ✓ | ✓ | ✓ | 过 |
| 0.11 | 2030、Quintile 5 | Chart 3.11、Quintile 3、2027 | 2027、Quintile 3 | not_found | ✗ | ✗ | ✗ | 过 |
| 0.03 | 2030、Quintile 1 | Chart 3.11、Quintile 1、2030 | 2031、Quintile 1 | Quintile 1、2031 | ✓ | ✗ | ✗ | 没过 |
| 0.10 | 2025、Quintile 5 | Chart 3.11、Quintile 5、2034 | 2033、Quintile 5 | Quintile 5、2034 | ✗ | ✗ | ✗ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
