# wtr24_ch2_e_p14

![wtr24_ch2_e_p14](../../data/pages/wtr24_ch2_e_p14.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `wtr24_ch2_e_p14` | wtr24_ch2_e | need_estimate | 10 | `parsebench/data/pages/wtr24_ch2_e_p14.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一张双轴组合图:29 个年度柱(浅蓝实心)叠加一条折线,柱读左轴「Number of low- and middle-income economies' SPS and TBT concerns」(0–80,刻度间隔 20),折线读右轴「Share of low- and middle-income economies' SPS and TBT concerns  addressed to high-income economies」(0%–100%,间隔 25%)。两条轴标题都竖排且折成两行;x 轴 1995–2023 年逐年、约 45° 旋转;图例在图下方一行两项,方块代表柱、短横线代表折线;标题写在蓝色实心横幅里,分两行;下方 Source/Note 两行小字。全图无任何数值标注,只有横向浅网格线。
> 
> ## 定位一个值难在哪
> 以 40%(2014 年折线点)为例:必须先判定它属于右轴而非左轴——同一像素高度在左轴上是 32 件。右轴只有 0%/25%/50%/75%/100% 五个刻度,5% 容差即 ±2 个百分点,约 6 像素,而折线未标点、未标值。定位它还需「2014」+「Share of concerns addressed to high-income economies」两个标签,而后者只出现在图例里。
> 
> ## 不确定的
> 折线各点的精确值全靠像素估读,2002、2016、2020 的低点区分度低;右轴标题中疑似双空格无法确认;标题横幅内是否另有单位文字看不清;网格线极浅,是否画到 80 一线不确定。

**gpt-5.6-sol**

> ### 画出来要什么
> 单面板柱线复合图：1995—2023共29个年份、29根柱和29个折线节点；左右双轴分别为0—80和0%—100%。还需蓝底白字标题条、竖排双轴标题、斜排年份、水平网格、图下图例及Source/Note。
> 
> ### 定位一个值难在哪
> 例如2015年的“Share of concerns addressed to high-income economies”为35%，没有数据标签或节点标记，只能在25%间隔的右轴上估读；5%容差仅1.75个百分点。
> 
> ### 不确定的
> 数值31似乎同时出现在2002和2011的柱上；折线及柱形均无印值，除100%贴合刻度外，其余指定值均由图形位置推断。

**gemini-3.1-pro**

> ### 画出来要什么
> 
> 需要绘制一个包含双Y轴的混合图表（柱状图和折线图）。X轴为倾斜45度显示的连续年份（1995-2023）。左侧Y轴为数值（0-80），带有多行换行且旋转90度的长文本标题；右侧Y轴为百分比（0%-100%），同样带有多行换行并旋转的标题。图表上方的标题区需要支持填充蓝色背景并以横幅形式展示（Figure B.6）。图例在底部，源和注释信息（Source/Note）在图表的最下方。背景仅包含水平方向的网格线，无垂直网格线。
> 
> ### 定位一个值难在哪
> 
> 以“66”为例（2020年柱子的数值），因为图表上没有任何打印的数据标签，必须通过左侧Y轴去读取。左侧Y轴的刻度步长高达20（0, 20, 40...），66介于60和80之间。在缺乏细分刻度线的情况下，5%的容差（±4的误差范围）对应到像素上非常小，极易因视觉估算偏差而读错，导致无法准确抽取该数值。
> 
> ### 不确定的
> 
> 折线点和柱状图共用X轴年份刻度，但受限于图像分辨率，无法完全确定折线的节点是严格居中于柱子之上，还是有极微小的分类对齐偏移。此外，顶部蓝色标题横幅的边距是否与主绘图区严格对齐也难以精准判定。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | compound | 58 | Figure B.6 | above | none |
| gpt-5.6-sol | f1 | compound | 58 | Figure B.6 | above | none |
| gemini-3.1-pro | f1 | other · bar and line | 58 | Figure B.6: | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `dual_axis` | ✓ | ✓ | ✓ | opus-5: left axis 0-80 counts, right axis 0%-100% share, both titled vertically；gpt-5.6-sol: Left ticks run 0–80; right ticks run 0%–100% for the line.；gemini-3.1-pro: a left value axis for counts and a right value axis for percentages |
| `footnote_marker` | ✓ | — | — | opus-5: body text carries superscripts "since 2014.12", "applied tariffs13", "high-income economies.14" |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: faint horizontal rules at 20, 40, 60, 80 across the plot; no vertical rules；gpt-5.6-sol: Horizontal rules cross the plot at value ticks; no vertical gridlines appear.；gemini-3.1-pro: horizontal grid lines are drawn across the plot, with no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: one legend row under the plot: square marker plus line marker with two names；gpt-5.6-sol: The two-entry legend is placed beneath the time axis.；gemini-3.1-pro: the legend entries are placed under the x-axis ticks |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: blue bars per year with a light-blue line drawn over them in the same panel；gpt-5.6-sol: Blue vertical bars and a light-blue line occupy the same panel.；gemini-3.1-pro: the panel contains both vertical bars and a line series |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: "Number of low- and middle-income economies' SPS and TBT concerns" set vertically along the left axis；gpt-5.6-sol: Both value-axis titles run vertically along the left and right edges.；gemini-3.1-pro: both left and right y-axis titles are rotated 90 degrees |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: year labels 1995 ... 2023 turned about 45 degrees under the axis；gpt-5.6-sol: Year labels 1995 through 2023 are angled diagonally.；gemini-3.1-pro: the year labels on the x-axis are rotated 45 degrees |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: "Source: Authors' calculations, based on WTO data..." and "Note: The figure displays the evolution..."；gpt-5.6-sol: “Source:” and “Note:” lines appear directly below the legend.；gemini-3.1-pro: Source and Note text printed below the chart and legend |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: bare ticks 0/20/40/60/80; the word "Number of" appears only in the axis title；gpt-5.6-sol: Axis titles begin “Number” and “Share”; right ticks carry percent signs. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `title_in_filled_banner` | opus-5 | 3,4 | "Figure B.6: Growing number of concerns about SPS and TBT measures..." white text in a blue filled bar above plot |
| `multiline_rotated_axis_title` | opus-5 | 3 | left axis title wraps onto two stacked vertical lines: "...economies' SPS" / "and TBT concerns" |
| `legend_marker_shape_matches_mark` | opus-5 | 3 | legend uses a small square for the bar series and a short line for the line series |
| `filled_heading_banner` | gpt-5.6-sol | 4 | The white “Figure B.6” heading sits inside a solid blue banner above the plot. |
| `heading_background_banner` | gemini-3.1-pro | 4 | the figure heading sits inside a solid blue banner stretching across the top |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 1 | 1995、Concerns raised by at least one low- or middle-income economy | 1995、Concerns raised by at least one low- or middle-income economy | 1995、Share of concerns addressed to high-income economies | Concerns raised by at least one low- or middle-income economy、1995 | ✓ | ✗ | ✓ | 过 |
| 100% | 1995、Share of concerns addressed to high-income economies | 1995、Share of concerns addressed to high-income economies | 2002、Concerns raised by at least one low- or middle-income economy | Share of concerns addressed to high-income economies、1995 | ✓ | ✗ | ✓ | 没过 |
| 31 | 2002、Concerns raised by at least one low- or middle-income economy | 2002、Concerns raised by at least one low- or middle-income economy | 2015、Share of concerns addressed to high-income economies | Concerns raised by at least one low- or middle-income economy、2001 | ✓ | ✗ | ✗ | 过 |
| 35% | 2002、Share of concerns addressed to high-income economies | 2002、Share of concerns addressed to high-income economies | 2014、Concerns raised by at least one low- or middle-income economy | Share of concerns addressed to high-income economies、2001 | ✓ | ✗ | ✗ | 过 |
| 46 | 2014、Concerns raised by at least one low- or middle-income economy | 2014、Concerns raised by at least one low- or middle-income economy | 2014、Share of concerns addressed to high-income economies | Concerns raised by at least one low- or middle-income economy、2013 | ✓ | ✗ | ✗ | 过 |
| 40% | 2014、Share of concerns addressed to high-income economies | 2014、Share of concerns addressed to high-income economies | 2020、Concerns raised by at least one low- or middle-income economy | Share of concerns addressed to high-income economies、2013 | ✓ | ✗ | ✗ | 没过 |
| 66 | 2020、Concerns raised by at least one low- or middle-income economy | 2020、Concerns raised by at least one low- or middle-income economy | 2016、Share of concerns addressed to high-income economies | Concerns raised by at least one low- or middle-income economy、2020 | ✓ | ✗ | ✓ | 过 |
| 30% | 2020、Share of concerns addressed to high-income economies | 2020、Share of concerns addressed to high-income economies | 2022、Concerns raised by at least one low- or middle-income economy | Share of concerns addressed to high-income economies、2020 | ✓ | ✗ | ✓ | 过 |
| 64 | 2022、Concerns raised by at least one low- or middle-income economy | 2022、Concerns raised by at least one low- or middle-income economy | 2022、Share of concerns addressed to high-income economies | Concerns raised by at least one low- or middle-income economy、2022 | ✓ | ✗ | ✓ | 过 |
| 70% | 2022、Share of concerns addressed to high-income economies | 2022、Share of concerns addressed to high-income economies | — | Share of concerns addressed to high-income economies、2022 | ✓ | — | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "compound" | "compound" | "other · bar and line" | compound | 图元数三家都是 58，都报 mixed_marks；gemini 的 other · bar and line 与 compound 同义。 |
