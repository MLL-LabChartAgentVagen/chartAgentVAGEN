# semiconductor_sector_study_p22

![semiconductor_sector_study_p22](../../data/pages/semiconductor_sector_study_p22.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `semiconductor_sector_study_p22` | semiconductor_sector_study | need_estimate | 7 | `parsebench/data/pages/semiconductor_sector_study_p22.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 一张单栏堆叠柱状图：横轴是不连续年份刻度 `2007 2010 2013 2016 2017 2018 2019 2020 2021 2022 2023`（缺 2008、2009 等），每根柱由数十个同色（teal）细分段组成，段与段仅靠白色细缝区分——即“每家公司一笔融资”作为一个堆叠段，没有图例、没有数值标签。纵轴刻度 `0M`…`220M`，间隔 20M，旋转的轴标题 `Fundraisings - Amount received by the company in its latest fundraising (GBP)` 竖排在左侧。图题另起一行 `Figure 4.1 – Latest Fundraisings`，来源行在图下。
> 
> **定位一个值难在哪**
> 
> 以 218（2023 年柱总高）为例：图上不印任何数字，只能对着 20M 一格的网格读；5% 容差约 ±11M，尚可，但 189（2020）与 218 之间的差要靠像素判断。更糟的是“2”和“0”这类小值——2007 柱几乎贴基线，段内还再分层，任何行标签只有年份，无法唯一指向某一段。
> 
> **不确定的**
> 
> 每根柱究竟含多少个堆叠段无法数清（2023 目测 20+）；段所代表的公司名未在页面出现；`0` 是否对应 2016 年的空槽（几乎不可见）无法确认。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 单幅按年份排列的青绿色堆叠柱图，11个时间槽、约44个公司细分；纵轴为竖排标题、0M–220M、每20M一格，仅有水平网格线。图题置于图上方，来源行置于图下方。
> 
> **定位一个值难在哪**
> 
> 例如2007年的2M没有印值，只能由纵轴读取；20M刻度间隔远大于其±0.1M的5%容差。年份能定位总柱，但柱内公司没有名称或图例。
> 
> **不确定的**
> 
> 细分数量按正文“Forty-four companies”及分隔线估为44；极薄细分难以逐一辨认。0值对应无柱槽，页面未明确印出数值。

**gemini-3.1-pro**

> ### 画出来要什么
> 
> 生成器需要绘制一个柱形图，其X轴为分类的时间轴（跳过了没有数据的年份，但刻度间距保持一致）。特别地，图中的柱子需要被纯白色的水平细线切割成多个堆积的小段，且这些小段没有对应的图例。Y轴需要旋转轴标题，并在刻度数字后附加“M”作为单位后缀。
> 
> ### 定位一个值难在哪
> 
> 以2023年的值 `218` 为例，这个值是整根柱子的总高度。由于柱子被切分成大量无标签的小分段，一个标准的图表解析器很可能会试图提取各个小分段的值，而不会在最终表格中输出总和。如果没有总和列，这个目标值在表格中将完全缺失。
> 
> ### 不确定的
> 
> X轴跳过了某些年份（如2008、2009），不确定这在生成时是作为完全连续的时间轴处理但去掉了无数据点，还是纯粹将其视为一系列分类标签。此外，2022和2023年柱子中极薄的分段数量难以精确清点。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 70 | Figure 4.1 | above | none |
| opus-5 | f2 | unreadable | 0 | — | none | none |
| gpt-5.6-sol | f1 | stacked_bar | 44 | Figure 4.1 | above | none |
| gemini-3.1-pro | f1 | stacked_bar | 30 | Figure 4.1 | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `footnote_marker` | ✓ | — | — | opus-5: 'fundraisings^xii' superscript roman numeral in the body paragraph |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: faint horizontal rules at 20M intervals; no vertical rules in the plot；gpt-5.6-sol: Horizontal grid rules cross the plot at 20M intervals; no vertical grid rules appear.；gemini-3.1-pro: horizontal grid lines only across the plot |
| `nonstandard_time_ticks` | ✓ | — | — | opus-5: axis ticks '2007 2010 2013 2016 2017 2018 2019 2020 2021 2022 2023' skip years unevenly |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Fundraisings - Amount received by the company in its latest fundraising (GBP)' set vertically at left；gpt-5.6-sol: “Fundraisings - Amount received by the company in its latest fundraising (GBP)” runs vertically.；gemini-3.1-pro: the y axis title is set vertically |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Source: Beauhurst (all latest fundraisings, 2007 - 2023)' under the plot；gpt-5.6-sol: “Source: Beauhurst (all latest fundraisings, 2007 - 2023)” appears below the plot.；gemini-3.1-pro: Source: Beauhurst... printed below the chart |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: each year's bar is split by thin white lines into many same-colour segments；gpt-5.6-sol: Each yearly teal column is divided by thin horizontal segment boundaries.；gemini-3.1-pro: bars are sliced into multiple horizontal segments |
| `thin_segment_label` | ✓ | — | — | opus-5: segments in 2023 bar are 1-3 px tall; no label can fit inside them |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: '(GBP)' appears only in the rotated y-axis title; ticks read '0M'...'220M'；gpt-5.6-sol: The vertical axis title ends with “(GBP)”.；gemini-3.1-pro: the y axis title contains (GBP) |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `uniform_colour_stacked_segments` | opus-5 | 3 | all stacked segments share one teal fill; only hairline gaps separate them, no legend names any |
| `irregular_category_axis_gaps` | opus-5 | 3 | 2007, 2010, 2013, 2016 are equally spaced slots though years are 3 apart, then yearly |
| `near_zero_bar_at_baseline` | opus-5 | 2 | 2016 slot shows a hairline mark at 0M; 2007 bar is ~1M tall |
| `unlabelled_stack_segments` | gpt-5.6-sol | 3 | Teal stacks have segment boundaries, but no company names or legend. |
| `unlabelled_stacked_segments` | gemini-3.1-pro | 1,2 | bars are sliced into segments without a legend |
| `unit_suffix_on_ticks` | gemini-3.1-pro | 2 | Y-axis ticks have 'M' appended |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 2 | 2007、Fundraisings - Amount received by the company in its latest fundraising (GBP) | 2007、Fundraisings - Amount received by the company in its latest fundraising (GBP) | 2007 | 2007 | ✓ | ✗ | ✗ | 没过 |
| 0 | 2016、Fundraisings - Amount received by the company in its latest fundraising (GBP) | 2016、0M | 2010 | 2010 | ✗ | ✗ | ✗ | 没过 |
| 23 | 2017、Fundraisings - Amount received by the company in its latest fundraising (GBP) | 2017 | 2017 | 2017 | ✗ | ✗ | ✗ | 没过 |
| 189 | 2020、Fundraisings - Amount received by the company in its latest fundraising (GBP) | 2020 | 2020 | 2020 | ✗ | ✗ | ✗ | 没过 |
| 22 | 2021、Fundraisings - Amount received by the company in its latest fundraising (GBP) | 2021 | 2021 | 2021 | ✗ | ✗ | ✗ | 没过 |
| 84 | 2022、Fundraisings - Amount received by the company in its latest fundraising (GBP) | 2022 | 2022 | 2022 | ✗ | ✗ | ✗ | 没过 |
| 218 | 2023、Fundraisings - Amount received by the company in its latest fundraising (GBP) | 2023 | 2023 | 2023 | ✗ | ✗ | ✗ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `density#f1` | "61–150" | "21–60" | "21–60" | 不裁 | 2023 那一根柱里的细段肉眼数不清（每段是一家公司的融资额），三家给的 21–60 与 61–150 都在合理范围。数不清本身是 P5 的一个例子：这类图的图元数只能由生成端知道。 |
| `key_roles#f1` | ["series", "time"] | ["time"] | ["time"] | time | 堆叠段是一家家公司，但页面上没有任何文字标注它们，段与段之间只有一条细白线。按「能定位到唯一图元的标签」判，只有年份这一段键；opus 记的 series 在页面上没有可用的名字（正是 `label_source: not_shown` 的情形）。 |
