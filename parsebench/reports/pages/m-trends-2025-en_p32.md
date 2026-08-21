# m-trends-2025-en_p32

![m-trends-2025-en_p32](../../data/pages/m-trends-2025-en_p32.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `m-trends-2025-en_p32` | m-trends-2025-en | need_estimate | 10 | `parsebench/data/pages/m-trends-2025-en_p32.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一张无编号的分组柱状图：标题 **"LockBit vs. RANSOMHUB DLS Listings, 2024"** 置于图上方，左侧竖排轴标题 "Count of DLS Listings"，y 轴刻度 0/50/100/150/200，仅有水平网格线。x 轴 12 个月份槽（Jan…Dec，注意 "March"、"April"、"Sept" 混用长短写），每槽两根柱（黑=LockBit，蓝=RANSOMHUB），共 24 根，无数值标签。图例画在绘图区内部右上角。页面左侧另有一列窄栏文字（"Data leak sites (DLS) are websites…"）与图并排，正文含上标脚注 "UNC2165¹⁸"。
> 
> ## 定位一个值难在哪
> 以 175 为例：它是 May 的黑色 LockBit 柱，柱顶落在 150 与 200 刻度之间、无印数。刻度间距 50，5% 容差只有 ±8.75 像素级别，读者只能目测插值；且必须同时给出 "May"+"LockBit" 两个标签，图无编号，表格行难以与图关联。10 与 55 各出现两次（Jan/Feb 蓝柱；March 黑柱与 Dec 蓝柱），仅凭数字无法唯一定位。
> 
> ## 不确定的
> 所有数值均为轴读估计，无源注、无数据链接；图例颜色与系列名的对应靠色块判断；"55" 究竟指 March LockBit 还是 Dec RANSOMHUB 无法确定。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 需重建一个单面板分组柱状图：12个月、LockBit与RANSOMHUB两系列、24根柱；左侧纵排计数轴、仅水平网格线，图例置于绘图区右上角。标题位于图上方，页面左侧另有蓝色竖线和说明栏。
> 
> **定位一个值难在哪**
> 
> 例如“Jan—RANSOMHUB—10”必须同时依赖月份轴与图例。数值未印在柱上，纵轴每50一格；10的5%容差仅±0.5，难以由柱高稳定读准。
> 
> **不确定的**
> 
> 柱上没有数据标签，因此给定值与具体柱的对应及精确整数只能按柱高、月份顺序和图例推定；尤其多个矮柱都接近10。

**gemini-3.1-pro**

> ### 画出来要什么
> 本页需要生成一个簇状柱形图（Grouped Bar Chart）。需要支持：图例放置在绘图区内部右上角，直接覆盖在绘图区域上方；仅绘制水平网格线（以50为间隔）；左侧Y轴携带旋转90度的轴标题“Count of DLS Listings”；X轴为按月份排列的类别标签。此外，页面整体布局在左侧带有一列与主图文内容平行的蓝色补充说明文本，需要相应的多列图文混排版式支持。
> 
> ### 定位一个值难在哪
> 主要的困难在于从图表读取精确的非整十数值。以11月的“RANSOMHUB”柱子为例，其预期值为98，但图表上并未标注具体数字。Y轴的刻度间距高达50，该柱子的顶端在视觉上仅略低于100的网格线，要通过视觉估算将其读取并满足5%的容差（对于较小数值如10，其5%仅为0.5）是极其困难且不可靠的。这必然导致在数值提取的第二步（容差校验）失败。
> 
> ### 不确定的
> 大部分未对齐水平网格线的柱形数值（如35、68、82、98等），单纯依据坐标轴只能获得模糊区间，难以在没有参照数据的情况下得出精确值。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | grouped_bar | 24 | — | above | none |
| gpt-5.6-sol | f1 | grouped_bar | 24 | — | above | none |
| gemini-3.1-pro | f1 | grouped_bar | 24 | — | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `footnote_marker` | ✓ | — | — | opus-5: "UNC2165" carries superscript 18 in body text |
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: two bars side by side in each month slot, black and blue；gpt-5.6-sol: Black and blue bars are drawn side by side for each month.；gemini-3.1-pro: two bars per month category drawn side by side |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: horizontal rules at 50/100/150/200 across panel, no vertical rules；gpt-5.6-sol: Horizontal rules cross the plot at 0, 50, 100, 150 and 200; no vertical gridlines.；gemini-3.1-pro: horizontal grid lines at 50 unit intervals, no vertical ones |
| `legend_inside_plot` | ✓ | ✓ | ✓ | opus-5: LockBit / RANSOMHUB legend box drawn over upper-right of plot area；gpt-5.6-sol: The “LockBit” and “RANSOMHUB” legend is inside the upper-right plot area.；gemini-3.1-pro: the LockBit / RANSOMHUB legend sits in the top right over the grid |
| `nonstandard_time_ticks` | ✓ | — | — | opus-5: ticks mix "Jan", "March", "April", "Sept" abbreviations inconsistently |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: "Count of DLS Listings" set vertically along the left axis；gpt-5.6-sol: “Count of DLS Listings” is rotated vertically beside the left axis.；gemini-3.1-pro: the y axis title Count of DLS Listings is turned 90 degrees |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: narrow left column "Data leak sites (DLS) are websites that publish stolen data..." beside the figure band；gpt-5.6-sol: A narrow “Data leak sites (DLS)” explanatory column runs beside the figure area.；gemini-3.1-pro: a narrow column of blue text runs to the left of the main block |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: axis ticks read 0, 50, 100, 150, 200; scale word only in "Count of DLS Listings"；gpt-5.6-sol: The left axis title reads “Count of DLS Listings”. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `unnumbered_figure_title` | opus-5 | 3,4 | bold title "LockBit vs. RANSOMHUB DLS Listings, 2024" with no "Figure n" prefix anywhere |
| `inconsistent_month_abbreviations` | opus-5 | 3 | axis reads Jan, Feb, March, April, May, June, July, Aug, Sept, Oct, Nov, Dec |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 60 | Jan、LockBit | Jan、LockBit | Jan、LockBit | LockBit、Jan | ✓ | ✓ | ✓ | 过 |
| 10 | Jan、RANSOMHUB | Jan、RANSOMHUB | Jan、RANSOMHUB | RANSOMHUB、Jan | ✓ | ✓ | ✓ | 过 |
| 100 | Feb、LockBit | Feb、LockBit | Feb、LockBit | LockBit、Feb | ✓ | ✓ | ✓ | 过 |
| 55 | March、LockBit | March、LockBit | March、LockBit | LockBit、March | ✓ | ✓ | ✓ | 过 |
| 175 | May、LockBit | May、LockBit | May、LockBit | LockBit、May | ✓ | ✓ | ✓ | 过 |
| 35 | June、RANSOMHUB | June、RANSOMHUB | June、RANSOMHUB | RANSOMHUB、June | ✓ | ✓ | ✓ | 没过 |
| 68 | Aug、RANSOMHUB | Aug、RANSOMHUB | Aug、RANSOMHUB | RANSOMHUB、Aug | ✓ | ✓ | ✓ | 过 |
| 82 | Oct、RANSOMHUB | Oct、RANSOMHUB | Oct、RANSOMHUB | RANSOMHUB、Oct | ✓ | ✓ | ✓ | 过 |
| 98 | Nov、RANSOMHUB | Nov、RANSOMHUB | Nov、RANSOMHUB | RANSOMHUB、Nov | ✓ | ✓ | ✓ | 过 |
| 55 | Dec、RANSOMHUB | Dec、RANSOMHUB | Dec、RANSOMHUB | RANSOMHUB、Dec | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `key_roles#f1` | ["series", "time"] | ["series", "time"] | ["category", "series"] | series × time | <strong>时间轴的判据</strong>：等距排开的年 / 月刻度记 `time`；长度不等的区间带（`2001-09` `2011-14`）虽然等距排开，是有序类目，记 `category`（与 `timevalue_p9` 同一条）。 横轴是 Jan…May 的月份刻度，opus 与 gpt 都记 time；gemini 记成 category。 |
