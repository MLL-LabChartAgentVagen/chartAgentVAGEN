# 2024-ltra_corrected_july_2025_p27

![2024-ltra_corrected_july_2025_p27](../../data/pages/2024-ltra_corrected_july_2025_p27.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `2024-ltra_corrected_july_2025_p27` | 2024-ltra_corrected_july_2025 | need_estimate | 10 | `parsebench/data/pages/2024-ltra_corrected_july_2025_p27.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 两张并列的堆叠柱状图，各自把编号标题印在图下方（`Figure 13: Solar PV DER Capacity Existing and Planned through 2034`、`Figure 14: Projected Generation Retirement Capacity through 2034`）。左图：10 个缩写类别（`NPCC-New England`…`WECC-SW`）旋转约 45°，纵轴旋转标题 `MW (dc)`，刻度 0–40,000，只画横向网格，图例 `Existing`/`Planned` 置于图下。右图：时间轴 2024–2029 后插入省略号 `⋯` 再跳到 2034，纵轴 `MW` 0–140,000，图内有一条自纵轴引出的参考线并连到灰底方框注记 `2023 LTRA Total Retirements`。两图都不印数值。
> 
> **定位一个值难在哪**
> 
> 以 WECC-CAMX 的 `Planned` 段约 16,000 为例：图上没有数字，需先读柱顶（≈39,000）再减去 `Existing` 顶（≈23,000）。左图网格间距 5,000，5% 容差只有 ±800，即约六分之一格；地址还需同时给出类别名与图例名两层键。
> 
> **不确定的**
> 
> NPCC-Ontario、SERC-E 两柱是否含极薄的 `Planned` 段看不清，故 marks 数为估计；右图参考线的确切数值（约 117,000–120,000）无刻度标注，只能猜。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 两幅单面板堆叠柱图并排排版，图题均置于图下，图例位于绘图区下方。Figure 13 还需旋转类别标签；Figure 14 需绘制灰色框注释、蓝色基准线，以及“2029”至“2034”间的省略号。
> 
> **定位一个值难在哪**
> 
> Figure 14 的“2024—Confirmed—7000”没有数值标签，只能依靠间隔为20,000 MW的纵轴读取；5%容差仅350 MW，因此最难保证精度。
> 
> **不确定的**
> 
> 所有指定数值均未印在柱段上，具体对应关系依据柱高判断。Figure 13 两个浅色零值段是否作为实际绘制标记无法确认；Figure 14 的省略号应表示省略年份。

**gemini-3.1-pro**

> ### 画出来要什么
> 页面展示了两个带有底部图例和标题的堆叠柱状图。生成器需要支持基础的堆叠柱状图绘制，并具备以下高级样式：图13的X轴标签需要支持特定角度旋转以防止长文本重叠；图14的X轴需支持自定义带省略号的时间刻度标签（如`2029 ... 2034`）。此外，需要在图14中支持绘制贯穿绘图区的水平参考线，并在该线上方居中位置绘制带背景色的文字注释框。
> 
> ### 定位一个值难在哪
> 以图14中2028年的“Confirmed”段（值为48000）为例，其难点在于图表中没有任何数据标签，必须对照左侧Y轴进行肉眼读取。由于Y轴的刻度间距高达20000，缺乏次级网格线辅助，读取悬空段或总高度时的误差极大概率会超过5%。
> 
> ### 不确定的
> 无法确切得知图14中带有“2023 LTRA Total Retirements”标签的水平参考线所代表的确切数值。从刻度线上估测大概在116,000到118,000之间，但页面文本中没有提供具体数值。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 20 | Figure 13 | below | none |
| opus-5 | f2 | stacked_bar | 14 | Figure 14 | below | none |
| gpt-5.6-sol | f1 | stacked_bar | 18 | Figure 13 | below | none |
| gpt-5.6-sol | f2 | stacked_bar | 14 | Figure 14 | below | none |
| gemini-3.1-pro | f1 | stacked_bar | 20 | Figure 13 | below | none |
| gemini-3.1-pro | f2 | stacked_bar | 14 | Figure 14 | below | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | ✓ | — | opus-5: category codes `PJM`, `SERC-E`, `SERC-FP`, `WECC-CAMX`, `WECC-SW`；gpt-5.6-sol: Category ticks include 'PJM', 'SERC-E', 'WECC-CAMX', and 'WECC-SW'. |
| `annotation_callout` | ✓ | ✓ | ✓ | opus-5: grey-filled box `2023 LTRA Total Retirements` drawn over the upper-left plot area；gpt-5.6-sol: A gray boxed '2023 LTRA Total Retirements' note is drawn inside the plot.；gemini-3.1-pro: a shaded box saying 2023 LTRA Total Retirements is over the plot |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: horizontal rules at each 20,000 tick, no vertical rules；gpt-5.6-sol: Horizontal gridlines cross the plot; no vertical gridlines are drawn.；gemini-3.1-pro: horizontal lines run across the plot area with no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: `Confirmed  Unconfirmed` swatch row under the year axis；gpt-5.6-sol: The 'Confirmed' and 'Unconfirmed' legend is centered below the time axis.；gemini-3.1-pro: the legend containing Existing and Planned sits below the categories |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: `Figure 13: Solar PV DER Capacity...` and `Figure 14: Projected Generation Retirement Capacity...` with separate captions；gpt-5.6-sol: Separate captions 'Figure 13' and 'Figure 14' identify two independent figures.；gemini-3.1-pro: Figure 13 and Figure 14 appear side by side on one page |
| `nonstandard_time_ticks` | — | — | ✓ | gemini-3.1-pro: a time tick label is written as 2029 ... 2034 |
| `reference_line` | ✓ | ✓ | ✓ | opus-5: short horizontal rule from the left axis near 118,000 leading into the callout box；gpt-5.6-sol: A blue horizontal benchmark line leads to '2023 LTRA Total Retirements'.；gemini-3.1-pro: a horizontal line runs across the panel to mark a total level |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: `MW` set vertically along the left axis；gpt-5.6-sol: The 'MW' title is vertical along the left axis.；gemini-3.1-pro: MW (dc) is printed rotated 90 degrees along the y-axis |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: `NPCC-New England`, `Texas RE-ERCOT` set at roughly 45 degrees；gpt-5.6-sol: All ten category labels are angled upward from left to right.；gemini-3.1-pro: labels such as NPCC-New England are tilted diagonally |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: Confirmed base and Unconfirmed top stacked in each yearly bar；gpt-5.6-sol: Dark 'Confirmed' and light 'Unconfirmed' segments are stacked within each year bar.；gemini-3.1-pro: the bars consist of stacked Existing and Planned segments |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: bare ticks 0…140,000; scale word only in axis title `MW`；gpt-5.6-sol: The left value-axis title reads 'MW'.；gemini-3.1-pro: the unit MW (dc) serves as the standalone axis title |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `elided_time_axis_ellipsis` | opus-5 | 3,2 | x tick row reads `2024 2025 2026 2027 2028 2029 ⋯ 2034`, omitted years shown as an ellipsis |
| `caption_below_plot_with_number` | opus-5 | 3,4 | bold `Figure 13: ...` and `Figure 14: ...` printed under each plot, not above |
| `time_axis_ellipsis` | gpt-5.6-sol | 2,3 | An ellipsis between '2029' and '2034' indicates omitted intervening years. |
| `vertical_page_separator` | gemini-3.1-pro | 4 | a vertical solid line visually separates the two figures and text columns |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 23000 | Existing、WECC-CAMX | WECC-CAMX、Existing | WECC-CAMX、Existing | WECC-CAMX、Existing | ✓ | ✓ | ✓ | 过 |
| 16000 | Planned、WECC-CAMX | WECC-CAMX、Planned | WECC-CAMX、Planned | WECC-CAMX、Planned | ✓ | ✓ | ✓ | 过 |
| 20000 | Planned、Texas RE-ERCOT | Texas RE-ERCOT、Planned | Texas RE ERCOT、Planned | Texas RE-ERCOT、Planned | ✓ | ✓ | ✓ | 过 |
| 8200 | Existing、PJM | PJM、Existing | PJM、Existing | PJM、Existing | ✓ | ✓ | ✓ | 过 |
| 5600 | Existing、NPCC-New York | NPCC-New York、Existing | NPCC-New York、Existing | NPCC-New York、Existing | ✓ | ✓ | ✓ | 过 |
| 7000 | Confirmed、2024 | 2024、Confirmed | 2024、Confirmed | 2024、Confirmed | ✓ | ✓ | ✓ | 过 |
| 48000 | Confirmed、2028 | 2028、Confirmed | 2028、Confirmed | 2028、Confirmed | ✓ | ✓ | ✓ | 过 |
| 35000 | Unconfirmed、2028 | 2026、Confirmed | 2029、Unconfirmed | 2026、Confirmed | ✗ | ✗ | ✗ | 过 |
| 78000 | Confirmed、2034 | 2034、Confirmed | 2034、Confirmed | 2029 ... 2034、Confirmed | ✓ | ✓ | ✓ | 过 |
| 37000 | Unconfirmed、2034 | 2034、Unconfirmed | 2034、Unconfirmed | 2029 ... 2034、Unconfirmed | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `key_roles#f2` | ["series", "time"] | ["series", "time"] | ["category", "series"] | series × time | <strong>时间轴的判据</strong>：等距排开的年 / 月刻度记 `time`；长度不等的区间带（`2001-09` `2011-14`）虽然等距排开，是有序类目，记 `category`（与 `timevalue_p9` 同一条）。 横轴是 2024–2034 的年份，opus 与 gpt 都记 time；gemini 记成 category。 |
