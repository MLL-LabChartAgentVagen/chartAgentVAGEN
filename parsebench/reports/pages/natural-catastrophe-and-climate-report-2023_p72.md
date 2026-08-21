# natural-catastrophe-and-climate-report-2023_p72

![natural-catastrophe-and-climate-report-2023_p72](../../data/pages/natural-catastrophe-and-climate-report-2023_p72.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `natural-catastrophe-and-climate-report-2023_p72` | natural-catastrophe-and-climate-report-2023 | need_estimate | 10 | `parsebench/data/pages/natural-catastrophe-and-climate-report-2023_p72.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 
> 两张独立编号的堆叠柱图（Figure 42 / Figure 43），共用一个页面级大标题「Total Number of Billion-Dollar Events: Economic and Insured (1990–2023)」——图本身无标题，标题在页顶。每图 34 个年份柱、两段堆叠（Weather / Climate 深蓝，Other Natural Perils 浅蓝），共约 136 个 segment。x 轴只标偶数年（1990、1992…2022），奇数年柱无刻度。y 轴纯数字、无单位词，Figure 42 顶端 70、Figure 43 顶端 35，无网格线。图例居中置于绘图区下方，紧接一行加粗前缀的说明「**Figure 42:** … | **Data and Graphic:** Gallagher Re」。
> 
> ## 定位一个值难在哪
> 
> 以 Figure 43 的 57 为例：该图最高只到 34，57 只能落在 Figure 42 的 2020 年 Weather / Climate 段。但 2020 柱无刻度（刻度只到 2020 有、2021 无），且刻度间距为 10，5% 容差约 ±2.9 像素级读数；深浅两段界线在 57 与 60 之间，仅凭轴读极易与 56 混淆。地址需三个标签：图号、年份、系列名。
> 
> ## 不确定的
> 
> 无任何数值印在柱上；奇数年份需按位置推断，年份标签并非逐柱印出。y 轴单位（“events 数量”）全页未写明，只能从标题 “Total Number” 推得。

**gpt-5.6-sol**

> **画出来要什么**
> 页面含两个独立编号的年度堆叠柱图，各34年、两类灾害；需绘制隔年时间刻度、左侧数值轴、图下图例，以及同处图下的编号、标题和来源。
> 
> **定位一个值难在哪**
> 图42的2010年“Other Natural Perils”为7，只是总柱顶端的薄段；纵轴每10一格，须比较堆叠段上下端点，难达到±0.35。
> 
> **不确定的**
> 奇数年份和2023没有横轴刻度，只能按相邻柱位推断；极薄浅色段是否为零及精确高度无法从页面确认。

**gemini-3.1-pro**

> ### 画出来要什么
> 页面包含两个垂直排列的堆叠柱状图（图42和图43）。两个图表均具有位于底部的图例以及非标准的标题布局（图号、说明文字和数据来源放置在x轴的正下方）。绘图区没有任何水平或垂直的网格线，所有的参考完全依赖左侧的y轴和底部的x轴。x轴体现了稀疏时间刻度（`sparse_time_ticks`），每两年进行一次年份标注，但每年均有一根对应的数据柱。此外，整个页面最上方带有一个跨图表的统领性页面总标题。
> 
> ### 定位一个值难在哪
> 所有的数值都没有打印在图表上，必须隔着大片空白区域与左侧的y轴对齐估读。以图43中1997年的总数值为例（值为2），该图表的y轴最小间隔刻度为5。在这种没有参考网格线的情况下，要用肉眼将极小的柱体高度读取到5%的误差容限内（即±0.1的精度）是绝对不可能的。此外，目标值中有许多对应于未在x轴上显式打印出的年份（如1991、2009、2023），使得表格在匹配时缺少精准的定位主键。
> 
> ### 不确定的
> 最右侧的一根数据柱下方没有任何刻度标签。根据x轴每两年一次的递增规律（最后标出的刻度是2022），以及页面主标题提及的时间跨度（1990–2023），我推断最后一根柱子代表2023年。由于数值高度依赖粗略估算，我无法确定某些提供的值（如66、34）究竟代表堆叠的总计还是某一个具体的顶部段。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 68 | Figure 42 | above | none |
| opus-5 | f2 | stacked_bar | 68 | Figure 43 | above | none |
| gpt-5.6-sol | f1 | stacked_bar | 66 | Figure 42 | below | none |
| gpt-5.6-sol | f2 | stacked_bar | 47 | Figure 43 | below | none |
| gemini-3.1-pro | f1 | stacked_bar | 68 | Figure 42: | below | none |
| gemini-3.1-pro | f2 | stacked_bar | 68 | Figure 43: | below | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_starts_above_zero` | ✓ | — | — | opus-5: lowest printed tick is `5`; no zero tick label on the axis |
| `dense_marks_100plus` | ✓ | — | — | opus-5: two figures, 34 years each, two segments per bar: about 136 drawn segments |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: legend row sits between the x tick labels and the Figure 43 caption；gpt-5.6-sol: The two-item legend is centered between the plot and “Figure 43” caption.；gemini-3.1-pro: the legend sits below the x-axis for both figures |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: `Figure 42:` and `Figure 43:` captions under two separate plots on one page；gpt-5.6-sol: Two independent plots are captioned “Figure 42” and “Figure 43”.；gemini-3.1-pro: Figure 42 and Figure 43 share the page with distinct numbering |
| `source_note_lines` | ✓ | ✓ | — | opus-5: `Data and Graphic: Gallagher Re` printed under both plots；gpt-5.6-sol: The line below the legend reads “Data and Graphic: Gallagher Re”. |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: bars for every year, tick labels only 1990, 1992 ... 2022；gpt-5.6-sol: Yearly bars span 1990–2023, but labels appear every two years through “2022”.；gemini-3.1-pro: points are yearly but ticks are printed every two years |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: dark Weather / Climate base with light Other Natural Perils cap on each year bar；gpt-5.6-sol: Light “Other Natural Perils” segments sit atop dark “Weather / Climate” segments.；gemini-3.1-pro: both figures draw segments stacked inside one bar |
| `thin_segment_label` | ✓ | — | — | opus-5: 1997 and 1994 top segments are one-unit slivers, too thin to carry any label |
| `unit_in_axis_or_title` | ✓ | — | — | opus-5: axis shows bare 10..70; scale word only in caption `losses adjusted to 2023 USD` |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `page_title_shared_by_two_figures` | opus-5 | 3,4 | one heading `Total Number of Billion-Dollar Events: Economic and Insured (1990–2023)` sits above both Figure 42 and 43 |
| `caption_below_with_bold_label_prefix` | opus-5 | 3,4 | `Figure 42:` and `Data and Graphic:` set bold inside an otherwise grey caption line |
| `no_axis_line_or_gridlines` | opus-5 | 2 | only a thin baseline under the bars; no vertical axis rule, no grid lines drawn |
| `shared_page_title` | gpt-5.6-sol | 4 | “Total Number of Billion-Dollar Events: Economic and Insured (1990–2023)” spans both numbered figures. |
| `unlabeled_zero_baseline` | gpt-5.6-sol | 2 | Both plots draw a baseline, while their first y-axis labels are “10” and “5”. |
| `no_gridlines_at_all` | gemini-3.1-pro | 2 | the plot area lacks both vertical and horizontal reference lines |
| `page_level_title` | gemini-3.1-pro | 4 | a huge title governs the whole page above both independent figures |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 26 | 1991、Weather / Climate | Figure 42、1992、Weather / Climate | 1991、Weather / Climate | Weather / Climate、1991 | ✗ | ✓ | ✓ | 过 |
| 7 | 2010、Other Natural Perils | Figure 43、1998、Weather / Climate | 2010、Other Natural Perils | Weather / Climate、1998 | ✗ | ✓ | ✗ | 过 |
| 57 | 2020、Weather / Climate | Figure 42、2020、Weather / Climate | 2020、Weather / Climate | Weather / Climate、2020 | ✓ | ✓ | ✓ | 没过 |
| 66 | 2023、Weather / Climate | Figure 42、2023 | 2023、Total number of billion-dollar economic loss natural catastrophes; losses adjusted to 2023 USD | 2023 | ✗ | ✗ | ✗ | 过 |
| 9 | 1995、Weather / Climate | Figure 43、2009、Weather / Climate | 1995、Weather / Climate | Weather / Climate、2009 | ✗ | ✓ | ✗ | 过 |
| 2 | 2004、Other Natural Perils | Figure 43、1997、Weather / Climate | 1994、Weather / Climate | 1997 | ✗ | ✗ | ✗ | 过 |
| 20 | 2011、Weather / Climate | Figure 43、2011、Weather / Climate | 2011、Weather / Climate | Weather / Climate、2011 | ✓ | ✓ | ✓ | 过 |
| 23 | 2018、Weather / Climate | Figure 43、2011、Other Natural Perils | 2011、Total number of billion-dollar insured loss natural catastrophes; losses adjusted to 2023 USD | 2011 | ✗ | ✗ | ✗ | 过 |
| 32 | 2020、Weather / Climate | Figure 43、2020、Weather / Climate | 2020、Weather / Climate | Weather / Climate、2020 | ✓ | ✓ | ✓ | 过 |
| 34 | 2023、Weather / Climate | Figure 43、2023 | 2023、Total number of billion-dollar insured loss natural catastrophes; losses adjusted to 2023 USD | 2023 | ✗ | ✗ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `density#f2` | "61–150" | "21–60" | "61–150" | 61–150（按中位数 68 个图元） | 三家数出的图元个数是 68 / 47 / 68，中位数 68，落在 61–150。三个数彼此相差不到一半，分歧是<档的边界>而不是读法：它们看的是同一张图，只是刚好被 20 / 60 / 150 / 400 这几条线切开。 |
| `heading#f1` | [true, "above"] | [true, "below"] | [true, "below"] | below | opus 给这一页两张图记了<strong>同一个</strong>标题（`Total Number of Billion-Dollar Events…`）并记在上方——同一段文字不可能是两张图各自的标题，那是这一节的章标题。它记在 `subtitle` 里的那句才是这张图自己的题，而 gpt 与 gemini 正是把那句当标题、记在下方。三家在「有图号」上一致（Figure 42），分歧只在位置。 |
| `heading#f2` | [true, "above"] | [true, "below"] | [true, "below"] | below | 同上，这是同一页的第二张（Figure 43）。opus 记的上方标题与第一张完全相同，是章标题不是图题。 |
