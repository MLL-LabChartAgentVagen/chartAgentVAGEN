# The_State_of_UK_Competition_Report_2024_p21

![The_State_of_UK_Competition_Report_2024_p21](../../data/pages/The_State_of_UK_Competition_Report_2024_p21.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `The_State_of_UK_Competition_Report_2024_p21` | The_State_of_UK_Competition_Report_2024 | need_estimate | 10 | `parsebench/data/pages/The_State_of_UK_Competition_Report_2024_p21.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 单面板折线图：25 个年度点、约 8 条线（1 条粗深蓝 `Baseline` + 约 7 条细浅蓝 `Alternative approaches`），无图例，靠线内文字命名；两条灰色竖向事件带并在带内写 `Great Financial Crisis`、`Covid-19 Pandemic`；y 轴起点 80（非零），刻度 80/100/120/140/160，单位行 `Material markup (indexed to 1997 = 100)` 置于顶刻度之上；x 轴每 4 年一刻度（1997…2021），轴题 `Year` 在图下；图上方是编号标题加 5 行斜体方法说明，图下方是 3 行小字注释。
> 
> ## 定位一个值难在哪
> 以 141 为例：它是 2021 年最高的一条浅蓝线。页面只给了 `Alternative approaches` 一个标签，7 条线互相缠绕、颜色粗细一致，无法把 141 唯一定位到某条线；年份也需在 2017 与 2021 刻度间推断。相比之下 `Baseline` 1997 的 100 很好定位。
> 
> ## 不确定的
> 浅蓝线的确切条数（约 7 条，末端重叠）；是否真有淡横向网格线；灰带覆盖的确切年份区间（约 2006–2008、2019–2021）只能目测。

**gpt-5.6-sol**

> ### 画出来要什么
> 单幅年度折线图：上方分离显示图号、标题、长副标题；纵轴标题置于轴上方并声明“(indexed to 1997 = 100)”。约九条年度线中，Baseline以深蓝粗线突出，其余同为浅蓝细线；两段灰色事件带带有区内文字。还需稀疏年份刻度、水平网格及图下说明来源。
> 
> ### 定位一个值难在哪
> Baseline的111可由“Baseline”与“2021”唯一定位；但2021年的141只属于统称“Alternative approaches”的八条同色线之一，单条方法没有标签，因此关联最难。
> 
> ### 不确定的
> 浅蓝线重叠较多，估计为八条、全图约225个点。143与最后一个100的具体年份及所属替代方法只能按折点位置推断。

**gemini-3.1-pro**

> **画出来要什么**
> 生成器需要支持绘制多条密集的折线图，并在曲线旁添加内联文本标签（如“Baseline”），而非使用外部图例。X轴需支持稀疏时间刻度（刻度四年一次，但数据是逐年的）。Y轴的标题和单位说明需能够直接放置在最高刻度之上。此外，绘图区需要支持渲染带有内嵌说明文字的垂直阴影带，以标记特殊的历史时期。
> 
> **定位一个值难在哪**
> 以值 `141` 为例，它位于 2012 年左右的一条浅蓝色曲线上。其寻址难点在于：“Alternative approaches”标签被统一用于指示多条未区分的折线，导致在表格提取时无法用唯一的系列名来定位这条特定的线（步骤3阻断）。同时，由于2012年不在X轴的打印刻度上，读取其精确数值和年份也很难达到5%的精度要求（步骤2阻断）。
> 
> **不确定的**
> “Alternative approaches”具体涵盖了哪些不同的生产函数或加权方法，无法从图表的视觉元素中区分。由于多条浅蓝色折线高度密集且互相交织，在某些年份难以准确追踪单条折线的具体轨迹。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 200 | Figure 5 | above | none |
| gpt-5.6-sol | f1 | line | 225 | Figure 5 | above | none |
| gemini-3.1-pro | f1 | line | 250 | Figure 5: | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | — | — | opus-5: "Great Financial Crisis" and "Covid-19 Pandemic" text drawn over the plot above the grey bands |
| `axis_starts_above_zero` | ✓ | ✓ | — | opus-5: the y axis lowest tick reads 80, then 100, 120, 140, 160; no break glyph；gpt-5.6-sol: The left value axis begins at 80 without a break glyph. |
| `axis_title_above_axis` | ✓ | ✓ | ✓ | opus-5: "Material markup (indexed to 1997 = 100)" sits above the 160 tick, not alongside the axis；gpt-5.6-sol: “Material markup (indexed to 1997 = 100)” sits above the left axis.；gemini-3.1-pro: Material markup text sits above the top y-axis tick |
| `axis_title_below_plot` | — | ✓ | — | gpt-5.6-sol: “Year” is centred below the bottom axis. |
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: about eight lines over 25 annual points, roughly 200 plotted points；gpt-5.6-sol: Approximately nine lines each contain 25 annual points, about 225 marks.；gemini-3.1-pro: around 10 lines over 25 years gives 250 marks |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: faint horizontal rules at 100, 120, 140 across the panel; no vertical rules；gpt-5.6-sol: Horizontal grid lines cross the plot at 80, 100, 120, 140 and 160; no vertical grid appears.；gemini-3.1-pro: horizontal grid lines only, no vertical ones drawn |
| `highlighted_category` | ✓ | ✓ | — | opus-5: one thick dark-blue "Baseline" line among thin light-blue alternative lines；gpt-5.6-sol: Baseline is a thick dark-blue line while the alternatives are thin light-blue lines. |
| `inline_series_labels` | ✓ | ✓ | ✓ | opus-5: "Alternative approaches" in light blue and "Baseline" in dark blue written next to the lines; no legend；gpt-5.6-sol: “Alternative approaches” and “Baseline” are written directly beside their lines.；gemini-3.1-pro: Baseline and Alternative approaches text sits next to the lines |
| `legend_inside_plot` | ✓ | — | — | opus-5: series names are the only key and are drawn over the plot area itself |
| `rebased_index_values` | ✓ | ✓ | ✓ | opus-5: "(indexed to 1997 = 100)" above the y axis; all lines start at 100 in 1997；gpt-5.6-sol: The axis title explicitly states “indexed to 1997 = 100”.；gemini-3.1-pro: the axis title explicitly says indexed to 1997 = 100 |
| `shaded_band` | ✓ | ✓ | ✓ | opus-5: two grey vertical bands labelled "Great Financial Crisis" and "Covid-19 Pandemic" inside the plot；gpt-5.6-sol: Two grey vertical bands are labelled “Great Financial Crisis” and “Covid-19 Pandemic”.；gemini-3.1-pro: grey vertical bands behind the lines for crisis periods |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: small print under plot: "Markups are calculated following our baseline approach... Data from the Annual Respondents Database X (1997-2020)"；gpt-5.6-sol: “Markups are calculated following our baseline approach described in the report.” appears below the plot.；gemini-3.1-pro: Markups are calculated... text sits below the x axis |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: annual points 1997-2021 but ticks only at 1997, 2001, 2005, 2009, 2013, 2017, 2021；gpt-5.6-sol: Annual vertices span 1997–2021, but only seven four-year ticks are labelled.；gemini-3.1-pro: ticks are every four years for yearly data points |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: bare y ticks 80-160; scale given only by "Material markup (indexed to 1997 = 100)"；gpt-5.6-sol: The value-axis title reads “Material markup (indexed to 1997 = 100)”.；gemini-3.1-pro: indexed to 1997 = 100 sits in the axis title |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `series_bundle_single_label` | opus-5 | 3 | about seven light-blue lines carry one shared label "Alternative approaches"; no per-line name anywhere |
| `line_weight_encodes_primary_series` | opus-5 | 3 | baseline drawn as a thick dark line, alternatives thin, so stroke weight separates the headline series |
| `axis_title_below_time_axis` | opus-5 | — | "Year" printed centred below the 1997-2021 tick row |
| `multiple_unnamed_series` | gpt-5.6-sol | 3 | Eight light-blue lines share “Alternative approaches” without individual method labels. |
| `inline_event_band_labels` | gpt-5.6-sol | 4 | Plain text names each event inside its grey time band, without boxes, arrows or leaders. |
| `shaded_period_bands_with_text` | gemini-3.1-pro | — | grey bands with Great Financial Crisis text placed inside them |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 100 | Baseline、1997 | Baseline、1997 | Baseline、1997 | Baseline、1997 | ✓ | ✓ | ✓ | 过 |
| 98 | Baseline、2001 | Baseline、1999 | Baseline、2001 | Baseline、2001 | ✗ | ✓ | ✓ | 过 |
| 103 | Baseline、2005 | Baseline、2005 | Baseline、2005 | Baseline、2005 | ✓ | ✓ | ✓ | 过 |
| 103 | Baseline、2009 | Baseline、2010 | Baseline、2009 | Baseline、2009 | ✗ | ✓ | ✓ | 过 |
| 111 | Baseline、2013 | Baseline、2015 | Baseline、2013 | Baseline、2013 | ✗ | ✓ | ✓ | 过 |
| 104 | Baseline、2017 | Baseline、2017 | Baseline、2017 | Baseline、2017 | ✓ | ✓ | ✓ | 过 |
| 111 | Baseline、2021 | Baseline、2021 | Baseline、2021 | Baseline、2021 | ✓ | ✓ | ✓ | 过 |
| 141 | Alternative approaches、2021 | Alternative approaches、2021 | Alternative approaches、highest、2021 | Alternative approaches、2012 | ✓ | ✓ | ✗ | 过 |
| 143 | Alternative approaches、2013 | Alternative approaches、2013 | Alternative approaches、highest、2013 | Alternative approaches、2014 | ✓ | ✓ | ✗ | 没过 |
| 100 | Alternative approaches、1997 | Alternative approaches、1997 | Alternative approaches、lowest、2019 | Alternative approaches、1997 | ✓ | ✗ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
