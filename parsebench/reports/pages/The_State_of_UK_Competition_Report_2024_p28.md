# The_State_of_UK_Competition_Report_2024_p28

![The_State_of_UK_Competition_Report_2024_p28](../../data/pages/The_State_of_UK_Competition_Report_2024_p28.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `The_State_of_UK_Competition_Report_2024_p28` | The_State_of_UK_Competition_Report_2024 | need_estimate | 10 | `parsebench/data/pages/The_State_of_UK_Competition_Report_2024_p28.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 单面板折线图，7 条分位数序列（Top 5% / Top 10% / Top 25% / Mean / Median / Bottom 25% / Bottom 5%），1997–2021 逐年约 25 个点，共约 175 个标记。无图例：序列名以内联文字写在各线右端点。线型区分序列——6 条虚线（Top 5% 为橙黄粗虚线，其余浅蓝细虚线），Mean 为深蓝实线。两条灰色竖向事件带覆盖全高，带内上方写 “Great Financial Crisis”“Covid-19 Pandemic”。y 轴标题 “Markup” 置于最高刻度 2.5 之上，刻度为 .5、1、1.5、2、2.5；x 轴标题 “Year” 在图下，刻度每 4 年一次（1997…2021）。图下还有三行小字注释，且注释中书名为斜体。标题块在图上方，分为粗体斜体的 “Figure 10: …” 与一段斜体说明。
> 
> **定位一个值难在哪**
> 以 0.58 为例：它只能是 Bottom 5% 早期某年。图上没有任何数字，y 轴刻度间距 0.5，5% 容差仅 ±0.029，约为刻度间距的 6%；而该线是浅蓝虚线，线宽本身就接近这一量级。年份也不是刻度年，须在 1997 与 2001 之间内插，行标签无法逐字取自页面。
> 
> **不确定的**
> 浅色水平网格线是否真实存在、各年精确取点、以及 1.50 与 1.52 分别属于哪条线哪一年，均为推测。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 需绘制单面板七序列年度折线图：六条虚线、一条实线，末端直接标注系列；仅有横向网格，并叠加“Great Financial Crisis”和“Covid-19 Pandemic”两段灰色时间带。标题、长副标题和图下注释均需独立排版。
> 
> **定位一个值难在哪**
> 
> 例如 Bottom 5% 的 0.58 未印在点上；纵轴刻度间隔为 0.5，而其 5%容差仅约0.03。多个年度又都接近0.58，难以唯一配对。
> 
> **不确定的**
> 
> 所有目标值均由折线位置估读；未显示的年度标签及若干重复近似值只能依据顶点位置推断，无法确认精确年份。

**gemini-3.1-pro**

> ### 画出来要什么
> 此页面包含一个单面板折线图。要生成此类图表，渲染器需要具备以下能力：
> 1. **多重折线样式控制**：支持对单条折线独立设置颜色、粗细和虚实线型（如图中粗黄虚线、粗深蓝实线、细浅蓝虚线共存）。
> 2. **行内序列标签**：支持省略独立图例块，将系列名称直接标注在对应折线的末端右侧。
> 3. **背景阴影带标注**：支持在绘图区特定的 x 轴范围内绘制垂直阴影带，并在其上方直接显示说明文本（如“Great Financial Crisis”）。
> 4. **稀疏时间刻度**：能够按年绘制数据点，但自定义 x 轴刻度标签的显示频率（如每 4 年显示一次）。
> 5. **特定标题布局**：y 轴单位/标题放置在顶部刻度正上方，图表标题和较长的副标题段落位于图表正上方。
> 
> ### 定位一个值难在哪
> 以 1997 年 Bottom 5% 对应的数值 `0.58` 为例，主要难点在于该图表完全依赖轴刻度读数（无数据标签）。纵轴的刻度间隔高达 0.5，且缺乏垂直网格线辅助定位。对于 `0.58`，其 5% 的容差仅约为 0.029，在如此宽的刻度间距中，肉眼极难将其与 `0.6` 或其他相近值精确区分，无法满足严格的精度要求。
> 
> ### 不确定的
> 折线图内部的转折点显示数据是逐年记录的，但仅部分年份在 x 轴上标出，需通过平移推算未标出的年份位置。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 175 | Figure 10 | above | none |
| gpt-5.6-sol | f1 | line | 175 | Figure 10 | above | none |
| gemini-3.1-pro | f1 | line | 175 | Figure 10: | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | — | ✓ | opus-5: "Great Financial\nCrisis" and "Covid-19\nPandemic" set over the plot area above each band；gemini-3.1-pro: text labels Great Financial Crisis and Covid-19 Pandemic sit inside the shaded bands |
| `axis_title_above_axis` | ✓ | ✓ | ✓ | opus-5: "Markup" printed above the top tick 2.5, left of the plot top；gpt-5.6-sol: “Markup” is set horizontally above the left axis.；gemini-3.1-pro: the word Markup sits directly above the y-axis rather than alongside it |
| `axis_title_below_plot` | — | ✓ | — | gpt-5.6-sol: “Year” is centered below the horizontal axis. |
| `dashed_line_series` | ✓ | ✓ | ✓ | opus-5: six dashed quantile lines against one solid dark-blue "Mean" line；gpt-5.6-sol: “Mean” is solid; the six quantile lines are dashed.；gemini-3.1-pro: six of the seven series are drawn as dashed lines |
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: 7 series over 1997-2021 gives roughly 175 plotted points；gpt-5.6-sol: Seven lines each have 25 annual positions, totaling about 175 marks.；gemini-3.1-pro: 7 series across 25 years yields about 175 data points |
| `footnote_marker` | ✓ | — | — | opus-5: note lines set italic for "Annual Respondents Databes X" and "Annual Business Survey" titles |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: faint horizontal rules at 1, 1.5, 2 across the panel; no vertical rules；gpt-5.6-sol: Horizontal gridlines cross the plot at y ticks; no vertical gridlines are drawn.；gemini-3.1-pro: horizontal dashed grid lines are present, but there are no vertical ones |
| `highlighted_category` | ✓ | — | — | opus-5: "Mean" drawn thick solid dark blue while all other series are thin dashed |
| `inline_series_labels` | ✓ | ✓ | ✓ | opus-5: "Top 5%", "Top 10%", "Top 25%", "Mean", "Median", "Bottom 25%", "Bottom 5%" at line right ends；gpt-5.6-sol: “Top 5%” through “Bottom 5%” are written beside the line endpoints.；gemini-3.1-pro: series names like Top 5% and Mean are written directly beside the right ends of the lines |
| `shaded_band` | ✓ | ✓ | ✓ | opus-5: two grey full-height vertical bands over ~2006-2008 and ~2020-2021；gpt-5.6-sol: Grey vertical bands are labelled “Great Financial Crisis” and “Covid-19 Pandemic”.；gemini-3.1-pro: two gray vertical bands cover specific time ranges in the background |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: "Markups are calculated following our baseline approach... Data from the Annual Respondents Databes X"；gpt-5.6-sol: Small print below begins “Markups are calculated following our baseline approach” and cites data.；gemini-3.1-pro: Markups are calculated... note sits in small print below the x-axis |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: yearly data but ticks only 1997, 2001, 2005, 2009, 2013, 2017, 2021；gpt-5.6-sol: Twenty-five annual positions span 1997–2021, but only seven years are tick-labelled.；gemini-3.1-pro: ticks are printed every 4 years but line bends show annual data points |
| `unit_in_axis_or_title` | ✓ | — | — | opus-5: y ticks read .5, 1, 1.5, 2, 2.5 bare; only "Markup" names the quantity |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `event_band_with_inline_label` | opus-5 | 3,4 | grey band spans plot height with its name "Covid-19 Pandemic" printed inside the band top |
| `note_block_rendered_inside_figure_image` | opus-5 | 1,4 | three lines of small print sit inside the chart graphic below the "Year" axis title |
| `variable_line_thickness` | gemini-3.1-pro | — | the Top 5% and Mean lines are drawn noticeably thicker than the others |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 1.85 | 1997、Top 5% | Top 5%、2003 | 2004、Top 5% | Top 5%、2001 | ✗ | ✗ | ✗ | 过 |
| 0.58 | 1997、Bottom 5% | Bottom 5%、1997 | 2005、Bottom 5% | Bottom 5%、1997 | ✓ | ✗ | ✓ | 过 |
| 1.12 | 2005、Mean | Mean、2005 | 2005、Mean | Mean、2009 | ✓ | ✓ | ✗ | 过 |
| 1.52 | 2005、Top 10% | Top 10%、2007 | 2005、Top 10% | Top 10%、2005 | ✗ | ✓ | ✓ | 过 |
| 1.50 | 2009、Top 10% | Top 10%、2005 | 2009、Top 10% | Top 10%、2009 | ✗ | ✓ | ✓ | 过 |
| 1.08 | 2013、Median | Mean、2001 | 2013、Median | Median、2009 | ✗ | ✓ | ✗ | 过 |
| 1.30 | 2013、Top 25% | Top 25%、2013 | 2017、Top 25% | Top 25%、2009 | ✓ | ✗ | ✗ | 过 |
| 0.82 | 2017、Bottom 25% | Bottom 25%、2001 | 2007、Bottom 25% | Bottom 25%、2009 | ✗ | ✗ | ✗ | 过 |
| 2.10 | 2021、Top 5% | Top 5%、2016 | 2015、Top 5% | Top 5%、2017 | ✗ | ✗ | ✗ | 过 |
| 0.60 | 2021、Bottom 5% | Bottom 5%、2021 | 2014、Bottom 5% | Bottom 5%、2009 | ✓ | ✗ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 2 | 1 | 2 | 未裁决 · 无实测证据 | 这一页 10 个抽查点全过，运行没有在任何一步卡住，三家的 2 / 1 / 2 都无法证伪。 |
