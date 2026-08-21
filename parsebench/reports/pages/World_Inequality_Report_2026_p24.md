# World_Inequality_Report_2026_p24

![World_Inequality_Report_2026_p24](../../data/pages/World_Inequality_Report_2026_p24.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `World_Inequality_Report_2026_p24` | World_Inequality_Report_2026 | need_estimate | 9 | `parsebench/data/pages/World_Inequality_Report_2026_p24.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 本页两幅独立编号折线图。Figure 15：标题分两行（`Figure 15.` + 标题）+ 图内主标题「Education and income divides in Western democracies, 1960–2025」；左侧竖排轴标题「Difference (pp) : top 10% minus bottom 90% voting left」；y 轴 −20%~15%，含 0% 处虚线零线；x 轴为旋转 45° 的五年段「1960–64」…「2020–25」；两条带方框彩色说明文字（红/蓝框）压在绘图区内；图例在图下、两行折行文本。Figure 16：绿线 1848–2022 + 红线尾段，y 轴 80%~180%，x 轴每 20 年一刻度而数据点几乎逐次选举，绘图区内有向上箭头 + 粗体方框注释「Urban voters vote more for left parties」。
> 
> ## 定位一个值难在哪
> 取 −16：Figure 15 蓝线 1985–89 的点。轴刻度间隔 5pp，容差按 5% 只有约 0.8pp，须在两条格线间目测；且该点无数值标注，键需「(% of top 10% earners voting left) minus (% of bottom 90% earners voting left)」整段图例文字 + 「1985–89」。
> 
> ## 不确定的
> Figure 16 的 138/140/112/118 属哪条线难判：红线仅覆盖 1994–2024 且与绿线在 2020 附近重叠，x 轴刻度稀疏（每 20 年），具体年份只能推测；红线的点数亦无法精确计数。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 两幅独立折线图，均需绘制点标记、双向网格、旋转年份、纵向轴题、图下图例、解释与来源段。图15另有负值、虚线零基准及红蓝框注；图16纵轴从80%起，并以稀疏年份刻度承载不规则选举年份。
> 
> **定位一个值难在哪**
> 
> 图15蓝线2020–25的−6需“时期＋完整系列公式”定位；纵轴每5个百分点一格，而5%容差仅0.3个百分点，且点上没有数值。图16的112还需推断未标出的2014。
> 
> **不确定的**
> 
> 图16约有43个点，密集处只能估数；138与140在图上都只能对应约140%的2024红色端点，无法凭像素区分。

**gemini-3.1-pro**

> ### 画出来要什么
> 本页包含两个带有折线和标记点的图表。图15包含一个带有负值域的Y轴（范围-20%至15%），以及一条独立的0%水平点阵虚线作为基准线；其X轴标签采用了“1960-64”这样的非标准时间段。图16的Y轴起始于80%，而其X轴每隔20年才有一个刻度标签，导致大部分数据点都悬浮于刻度之间。这两张图均仅使用了水平虚线作为网格，图例位于底部，并在图表内部叠加了多个自定义的解释性文本框，其中图16甚至带有粗实线箭头指向特定的图表特征。Y轴的标题都被旋转了90度且同时包含了单位说明，而X轴的刻度标签则倾斜了45度。页面底部包含非标准来源格式的详细大段“Interpretation”解读文本。
> 
> ### 定位一个值难在哪
> 以 `-14` 为例（图15中蓝线在1965-69年或1970-74年的数据点），由于图表上的数值并未直接标出，读者只能依托每隔5%的水平网格线（如-10%和-15%）去肉眼估算。在这个极小的视觉间距内读出精确的-14，且要保证误差在5%以内，是极难实现的。图16的问题更为严重，由于X轴时间刻度非常稀疏，不仅数值难以准确读出，连对应的年份也无法精准定位。
> 
> ### 不确定的
> 图表内的带有文字和箭头的批注框是依靠坐标硬编码绘制还是与特定数据点动态绑定无法仅从图片确认；图16中很多特定年份（如1994、2019）的数据点也只能基于先验知识或常理推断，图面未能提供精确对其。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 26 | Figure 15 | above | none |
| opus-5 | f2 | line | 65 | Figure 16 | above | none |
| gpt-5.6-sol | f1 | line | 26 | Figure 15. | above | none |
| gpt-5.6-sol | f2 | line | 43 | Figure 16. | above | none |
| gemini-3.1-pro | f1 | line | 26 | Figure 15. | above | none |
| gemini-3.1-pro | f2 | line | 37 | Figure 16. | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | ✓ | ✓ | opus-5: black arrow with boxed bold text 'Urban voters vote more for left parties' inside plot；gpt-5.6-sol: A boxed “Urban voters vote more for left parties” note has an upward arrow.；gemini-3.1-pro: text boxes and arrows placed inside the plot areas |
| `axis_starts_above_zero` | — | ✓ | ✓ | gpt-5.6-sol: The value axis begins at 80% without an axis-break glyph.；gemini-3.1-pro: the lowest tick on the y-axis is 80% |
| `hgrid_only` | ✓ | — | ✓ | opus-5: faint horizontal rules at each 5% level, no vertical rules in the panel；gemini-3.1-pro: only horizontal dashed grid lines are shown |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'European elections 1994–2024' / 'French legislative elections 1848–2022' below plot；gpt-5.6-sol: The two election-series labels sit beneath the plot.；gemini-3.1-pro: the legends sit below the x-axis on both figures |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: 'Figure 15.' and 'Figure 16.' each with own title and Interpretation block；gpt-5.6-sol: Separate headings “Figure 15.” and “Figure 16.” introduce independent charts.；gemini-3.1-pro: two numbered figures are presented independently on the page |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: y ticks read −20%, −15%, −10%, −5%, 0% with both lines mostly below zero；gpt-5.6-sol: Both lines extend below the labelled 0% rule.；gemini-3.1-pro: the y-axis values extend down to -20% |
| `nonstandard_time_ticks` | ✓ | — | ✓ | opus-5: time written as five-year spans '1975–79', '2020–25'；gemini-3.1-pro: x-axis labels use time ranges like 1960-64 |
| `reference_line` | ✓ | ✓ | ✓ | opus-5: a dotted horizontal rule drawn across the panel at 0%；gpt-5.6-sol: A black dotted horizontal rule crosses the plot at 0%.；gemini-3.1-pro: a dotted horizontal line marks the 0% zero baseline |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Left vote: urban 50% vs. rural 50% (% of national average)' set vertically at left；gpt-5.6-sol: The “Left vote” title is vertical along the left axis.；gemini-3.1-pro: y-axis titles on both figures are rotated 90 degrees |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: '1840' … '2020' set at about 45 degrees；gpt-5.6-sol: Year ticks from “1840” through “2020” are diagonally rotated.；gemini-3.1-pro: x-axis labels are rotated 45 degrees |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Sources and series: Gethin et al. (2021) and World Political Cleavages and Inequality Database (wpid.world).'；gpt-5.6-sol: The paragraph below includes “Sources and series: Cagé and Piketty (2025)”.；gemini-3.1-pro: interpretation notes and sources at the bottom of both figures |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: ticks every 20 years (1840,1860,…2020) but markers at nearly every election；gpt-5.6-sol: Many election points fall between the twenty-year ticks.；gemini-3.1-pro: data points are drawn between 20-year x-axis ticks |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: the pp scale is only stated in the vertical axis title, ticks read bare '15%'；gpt-5.6-sol: The y-axis title includes “(% of national average)”. |
| `unit_in_series_name` | ✓ | — | — | opus-5: legend reads '(% of top 10% educated voting left) minus (% of bottom 90% educated voting left)' |
| `wrapped_category_labels` | ✓ | — | — | opus-5: legend entries wrap onto two lines under the plot |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `series_beyond_last_tick` | opus-5 | 2,3 | red 'European elections 1994–2024' points continue right of the final 2020 tick |
| `partial_span_overlay_series` | opus-5 | 3 | red series covers only 1994–2024 while green spans 1848–2022 in the same panel |
| `colored_callout_matches_series` | opus-5 | 3 | red-bordered box explains the red line, blue-bordered box explains the blue line |
| `marker_shape_encodes_series` | gpt-5.6-sol | 3 | Red circles and blue squares distinguish the two line series. |
| `marker_shape_encodes_series` | gpt-5.6-sol | 3 | Red triangles and green squares distinguish the election series. |
| `interpretation_caption_block` | gpt-5.6-sol | 4 | Each chart is followed by a paragraph beginning “Interpretation.” |
| `percent_sign_on_every_value_tick` | gpt-5.6-sol | 2 | Value ticks retain percent signs, including “−20%”, “15%”, “80%”, and “180%”. |
| `text_paragraph_as_caption` | gemini-3.1-pro | 4 | an Interpretation paragraph acts as the figure caption and source note |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| -14 | 1960–64、(% of top 10% educated voting left) minus (% of bottom 90% educated voting left) | (% of top 10% educated voting left) minus (% of bottom 90% educated voting left)、1960–64 | 1960–64、(% of top 10% educated voting left) minus (% of bottom 90% educated voting left) | 1965–69、(% of top 10% earners voting left) minus (% of bottom 90% earners voting left) | ✓ | ✓ | ✗ | 过 |
| 11 | 2020–25、(% of top 10% educated voting left) minus (% of bottom 90% educated voting left) | (% of top 10% educated voting left) minus (% of bottom 90% educated voting left)、2020–25 | 2020–25、(% of top 10% educated voting left) minus (% of bottom 90% educated voting left) | 2020–25、(% of top 10% educated voting left) minus (% of bottom 90% educated voting left) | ✓ | ✓ | ✓ | 过 |
| -11 | 1960–64、(% of top 10% earners voting left) minus (% of bottom 90% earners voting left) | (% of top 10% educated voting left) minus (% of bottom 90% educated voting left)、1965–69 | 1960–64、(% of top 10% earners voting left) minus (% of bottom 90% earners voting left) | 1960–64、(% of top 10% earners voting left) minus (% of bottom 90% earners voting left) | ✗ | ✓ | ✓ | 过 |
| -16 | 1975–79、(% of top 10% earners voting left) minus (% of bottom 90% earners voting left) | (% of top 10% earners voting left) minus (% of bottom 90% earners voting left)、1985–89 | 1975–79、(% of top 10% earners voting left) minus (% of bottom 90% earners voting left) | 1975–79、(% of top 10% earners voting left) minus (% of bottom 90% earners voting left) | ✗ | ✓ | ✓ | 过 |
| -6 | 2020–25、(% of top 10% earners voting left) minus (% of bottom 90% earners voting left) | (% of top 10% earners voting left) minus (% of bottom 90% earners voting left)、2020–25 | 2020–25、(% of top 10% earners voting left) minus (% of bottom 90% earners voting left) | 2020–25、(% of top 10% earners voting left) minus (% of bottom 90% earners voting left) | ✓ | ✓ | ✓ | 没过 |
| 138 | 1860、French legislative elections 1848–2022 | French legislative elections 1848–2022、1860 | 2024、European elections 1994–2024 | 1994、European elections 1994–2024 | ✓ | ✗ | ✗ | 没过 |
| 140 | 1920、French legislative elections 1848–2022 | European elections 1994–2024、2020 | 2024、European elections 1994–2024 | 2019、European elections 1994–2024 | ✗ | ✗ | ✗ | 没过 |
| 112 | 2020、French legislative elections 1848–2022 | French legislative elections 1848–2022、1980 | 2014、European elections 1994–2024 | 2012、French legislative elections 1848–2022 | ✗ | ✗ | ✗ | 没过 |
| 118 | 2020、European elections 1994–2024 | French legislative elections 1848–2022、1900 | 2019、European elections 1994–2024 | 1960、French legislative elections 1848–2022 | ✗ | ✗ | ✗ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `density#f2` | "61–150" | "21–60" | "21–60" | 21–60（按中位数 43 个图元） | 三家数出的图元个数是 65 / 43 / 37，中位数 43，落在 21–60。三个数相差超过一半，取中位数所在的档；差异来自把叠在一起的图元数成一层还是两层。 |
