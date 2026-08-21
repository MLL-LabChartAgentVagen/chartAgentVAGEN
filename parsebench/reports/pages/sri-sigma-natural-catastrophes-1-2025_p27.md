# sri-sigma-natural-catastrophes-1-2025_p27

![sri-sigma-natural-catastrophes-1-2025_p27](../../data/pages/sri-sigma-natural-catastrophes-1-2025_p27.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `sri-sigma-natural-catastrophes-1-2025_p27` | sri-sigma-natural-catastrophes-1-2025 | need_estimate | 10 | `parsebench/data/pages/sri-sigma-natural-catastrophes-1-2025_p27.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 两幅同族图叠在一页,各自装在浅蓝底色的图框里(标题、图号、图例、Source 都在框内)。Figure 18:1970–2024 共 55 根年度堆叠柱,三段(Earthquake/tsunami、Weather-related catastrophes、Man-made disasters),约 130+ 个色块;横轴刻度每三年一格(1970、1973 … 2024),纵轴 0–250、每 50 一条横网格;plot 区上方叠着 11 个带引线的事件标注框("Hurricanes Katrina, Rita, Wilma"、"Hurricane Ian" 等),互相错层避让。Figure 19:同样 55 根两段堆叠柱,再叠一条只覆盖约 1995 年后的粉色 "Exponential trend (total natcat losses)" 曲线;轴标题 "Insured losses (USD bn)" 写在顶端刻度 200 的右侧。
> 
> **定位一个值难在哪**
> 取 145(Figure 18 的 2024 年柱总高)。图上一个数字都没印,只能靠 0/50/100/150 的网格内插;5% 容差只有 ±7,不到网格的七分之一。而且 145 是三段之和,读者要先认出柱顶,再确认 2024 这根确实对齐最后一个刻度;若取 55(1992)则该年根本没有刻度标签,须从 1991 往右数一格。
> 
> **不确定的**
> 所有测试值都不是印在图上的(137 只出现在正文 "USD 137 billion in 2024")。我对 75/76/81/56 归到哪根柱、哪一段只能按高度猜测,Figure 18 与 Figure 19 同年总高相近,极易错配。

**gpt-5.6-sol**

> ### 画出来要什么
> 页面含两幅浅蓝底年度图。Figure 18 是三系列堆叠柱图，并以方框、锚点和引线标注重大灾害；Figure 19 是两系列堆叠柱加洋红色指数趋势线。两图均有稀疏年份刻度、水平网格线、下置图例和来源行。
> 
> ### 定位一个值难在哪
> Figure 19 的2024年“Primary perils (incl secondary effects)”为56。它是上层段，须由总高减去约81的下层边界；纵轴每25一格，5%容差仅2.8。
> 
> ### 不确定的
> 柱段均未印数值。55、165、75、180、137等只能按边界估读；未标出的1992、2005、2011、2017须由相邻三年刻度定位。45被判断为1992年堆叠总高。

**gemini-3.1-pro**

> ### 画出来要什么
> 该页面包含两个高密度的堆叠柱状图。X轴为时间轴但刻度稀疏（`sparse_time_ticks`），需要图表引擎能够自动将分类数据对齐到未标出具体年份的位置。图18需要在绘图区内生成带有折线和圆点的文本注释框（`annotation_callout`）以精准指向特定的数据柱。图19是复合图表，在堆叠柱状图上叠加了一条平滑的指数趋势线（`mixed_marks`）。两个图表的图例均需要并排显示在图表底部。此外，图19的Y轴单位直接放置在顶部刻度数值的同一行。
> 
> ### 定位一个值难在哪
> 以图18中的“55”（2011年地震/海啸损失）为例，首先X轴并未标出“2011”的刻度标签，无法直接使用文本进行关联匹配；其次，该值位于总高度约165的柱子底部，Y轴的最大值为250且刻度间隔高达50，缺乏网格线的辅助，肉眼极难将其精确读取至5%的误差范围内。
> 
> ### 不确定的
> 图19中指数趋势线的具体平滑算法和数学公式未知。部分在正文文本中引用的数值（如2024年的1370亿自然灾害损失）实际上是图表中多个数据段（地震/海啸与气候相关灾害）的组合叠加，无法直接通过单一标志或图例拆解出来。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 135 | Figure 18 | above | none |
| opus-5 | f2 | compound | 140 | Figure 19 | above | none |
| gpt-5.6-sol | f1 | stacked_bar | 165 | Figure 18 | above | none |
| gpt-5.6-sol | f2 | compound | 140 | Figure 19 | above | none |
| gemini-3.1-pro | f1 | stacked_bar | 140 | Figure 18 | above | none |
| gemini-3.1-pro | f2 | compound | 165 | Figure 19 | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | ✓ | ✓ | opus-5: boxed notes over the plot: 'Hurricanes Katrina, Rita, Wilma', 'Hurricane Ian', with leader lines to bars；gpt-5.6-sol: Boxed event labels with vertical leaders mark Hurricane Andrew and other years.；gemini-3.1-pro: boxed notes like 'Hurricane Ian' drawn over the plot area |
| `axis_title_above_axis` | ✓ | ✓ | ✓ | opus-5: 'Insured losses (USD bn)' set beside the top tick '200', above the axis；gpt-5.6-sol: “Insured losses (USD bn)” is horizontal above the left-axis scale.；gemini-3.1-pro: Insured losses (USD bn) sits above the top tick 200 |
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: 55 yearly bars with two segments each plus a line, over 110 marks；gpt-5.6-sol: Two annual bar segments across 55 years plus the trend exceed 100 marks.；gemini-3.1-pro: both figures contain over 100 drawn marks across 55 years |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: horizontal rules at 0, 25 ... 200; no vertical rules；gpt-5.6-sol: Horizontal rules cross the plot at 25-unit ticks; no vertical gridlines appear.；gemini-3.1-pro: horizontal rules across the panel, no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'Secondary perils  Primary perils (incl secondary effects)  Exponential trend (total natcat losses)' under the axis；gpt-5.6-sol: The two bar series and trend legend sit below the plotting area.；gemini-3.1-pro: legend sits below the x-axis |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: pink 'Exponential trend (total natcat losses)' line drawn over the stacked bars；gpt-5.6-sol: Stacked annual bars are overlaid by a magenta exponential trend line.；gemini-3.1-pro: bars and a trend line in the same panel |
| `multi_figure_page` | ✓ | ✓ | — | opus-5: 'Figure 18' and 'Figure 19' with separate titles, captions and source lines on one page；gpt-5.6-sol: Two independent panels are numbered “Figure 18” and “Figure 19”. |
| `panel_background` | ✓ | ✓ | — | opus-5: pale blue tint fills the figure block and the plot area；gpt-5.6-sol: The complete chart panel and plot carry a pale blue fill. |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Source: Swiss Re Institute' in small print below the legend；gpt-5.6-sol: “Source: Swiss Re Institute” appears beneath the legend.；gemini-3.1-pro: Source: Swiss Re Institute below both plots |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: annual bars, ticks only 1970, 1973 ... 2024；gpt-5.6-sol: Annual bars span 1970–2024, but labels appear every three years.；gemini-3.1-pro: x-axis ticks are every 3 years but bars are yearly |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: each yearly bar has a dark 'Secondary perils' base and a light-green 'Primary perils' top；gpt-5.6-sol: Dark “Secondary perils” segments sit below light “Primary perils” segments.；gemini-3.1-pro: segments stacked inside one bar |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: title says 'in USD billion at 2024 prices'; ticks 0, 25 ... 200 are bare；gpt-5.6-sol: The heading says “in USD billion at 2024 prices”.；gemini-3.1-pro: unit in the title of f1 and axis of f2 |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `partial_span_series` | opus-5 | 2,3 | the pink exponential trend line starts near 1995 and covers only part of the 1970-2024 axis |
| `tiered_callout_layer` | opus-5 | 3,4 | eleven event boxes at several stacked heights, leader lines dropping to individual year bars |
| `figure_container_tint_box` | opus-5 | 4 | heading, plot, legend and source line all enclosed in one pale blue full-width box |
| `annotation_connector_line` | gemini-3.1-pro | 2,3 | lines with dots map floating annotation boxes to specific bars |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 55 | 1992、Weather-related catastrophes | Insured catastrophe losses, 1970 – 2024 (USD bn, 2024 prices)、1992 | 1992、Weather-related catastrophes | 2011、Earthquake/tsunami | ✗ | ✓ | ✗ | 过 |
| 165 | 2005、Weather-related catastrophes | Insured catastrophe losses, 1970 – 2024 (USD bn, 2024 prices)、2006 | 2005、Weather-related catastrophes | 2011、Total | ✗ | ✓ | ✗ | 过 |
| 75 | 2011、Earthquake/tsunami | 2024、Secondary perils | 2011、Earthquake/tsunami | 2024、Secondary perils | ✗ | ✓ | ✗ | 过 |
| 180 | 2017、Weather-related catastrophes | Insured catastrophe losses, 1970 – 2024 (USD bn, 2024 prices)、2018 | 2017、Weather-related catastrophes | 2017、Total | ✗ | ✓ | ✗ | 过 |
| 137 | 2024、Weather-related catastrophes | 2024、Earthquake/tsunami、Weather-related catastrophes | 2024、Weather-related catastrophes | 2024、Earthquake/tsunami、Weather-related catastrophes | ✓ | ✓ | ✓ | 过 |
| 45 | 1992、Primary perils (incl secondary effects) | Insured catastrophe losses, 1970 – 2024 (USD bn, 2024 prices)、2015 | 1992 | 1999、Total | ✗ | ✗ | ✗ | 过 |
| 145 | 2005、Primary perils (incl secondary effects) | 2024、Earthquake/tsunami、Weather-related catastrophes、Man-made disasters | 2005、Primary perils (incl secondary effects) | 2005、Total | ✗ | ✓ | ✗ | 过 |
| 76 | 2011、Secondary perils | 2012、Secondary perils | 2021、Secondary perils | 2022、Secondary perils | ✗ | ✗ | ✗ | 过 |
| 81 | 2024、Secondary perils | Global insured losses from primary and secondary perils, 1970 – 2024, in USD billion at 2024 prices、2012 | 2024、Secondary perils | 2023、Secondary perils | ✓ | ✓ | ✗ | 过 |
| 56 | 2024、Primary perils (incl secondary effects) | 2009、Secondary perils、Primary perils (incl secondary effects) | 2024、Primary perils (incl secondary effects) | 2008、Secondary perils | ✗ | ✓ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `density#f1` | "61–150" | "151–400" | "61–150" | 61–150（按中位数 140 个图元） | 三家数出的图元个数是 135 / 165 / 140，中位数 140，落在 61–150。三个数彼此相差不到一半，分歧是<档的边界>而不是读法：它们看的是同一张图，只是刚好被 20 / 60 / 150 / 400 这几条线切开。 |
| `density#f2` | "61–150" | "61–150" | "151–400" | 61–150（按中位数 140 个图元） | 三家数出的图元个数是 140 / 140 / 165，中位数 140，落在 61–150。三个数彼此相差不到一半，分歧是<档的边界>而不是读法：它们看的是同一张图，只是刚好被 20 / 60 / 150 / 400 这几条线切开。 |
