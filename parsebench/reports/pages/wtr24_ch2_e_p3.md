# wtr24_ch2_e_p3

![wtr24_ch2_e_p3](../../data/pages/wtr24_ch2_e_p3.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `wtr24_ch2_e_p3` | wtr24_ch2_e | need_estimate | 10 | `parsebench/data/pages/wtr24_ch2_e_p3.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 一张跨栏宽的组合图 Figure B.1:26 个年份槽(1996–2021),深蓝柱为「Speed of income convergence」读左轴 -1…8「percentage points」;绿线为「Trade participation」读右轴 40…160「(100=1996)」,即双值轴+柱线混合。柱内还有第二种浅蓝填色(2008、2009、2020),Note 说明它表示「a contribution of negative growth in high-income economies」,图例里没有这一项。2021 柱在零线以下,1998 槽根本没有柱。标题写在整幅宽的实心蓝色横幅里,轴标题竖排,年份刻度斜排,图例在图下,下面是 Source/Note 小字。
> 
> **定位一个值难在哪**
> 
> 7.7:它是 2009 年柱子的顶端,但顶端那截是浅蓝的。要唯一定位需要三个标签——年份 2009、系列名 Speed of income convergence、以及只在图下 Note 里出现的「light blue fill」;图例给不出这个名字。而且没有任何数字印在图上,只能靠 1 个单位间隔的横线内插。
> 
> **不确定的**
> 
> 线上的点全靠像素换算:128、138、125 分别归到 2003、2004、2009 属于推断,相邻年份差常不足 5%。2020 柱是否整根为浅蓝、1998 是零还是缺失,都看不确切。

**gpt-5.6-sol**

> ### 画出来要什么
> 需重建带蓝色横幅标题的双轴复合图：26个旋转年份、蓝色柱与青绿色折线、部分浅蓝堆叠、水平网格、下方图例，以及完整的Source和Note。
> 
> ### 定位一个值难在哪
> “2021 / Speed of income convergence”的-0.2须读左轴；刻度间隔为1，而5%容差仅0.01，短负柱难以达到该精度。
> 
> ### 不确定的
> 图中没有数值标签；1998的0.0没有可见柱，无法仅凭图形排除缺失值。浅蓝部分的边界也只能近似辨认。

**gemini-3.1-pro**

> ### 画出来要什么
> 需要支持在同一面板中混排柱状图与折线图，并能处理双侧Y轴配置，两侧拥有独立的刻度和量程。左、右Y轴标题需支持垂直旋转显示，X轴的年份标签需支持45度倾斜。图表顶部的标题区带有明显的蓝色背景填充，图例需整体置于X轴下方，而数据源与注释等文本段落需排布在图表最底部。
> 
> ### 定位一个值难在哪
> 定位“Trade participation”折线在2008年的值（约155）极其困难。由于图表没有任何直观的数据标签，读数完全依赖右侧Y轴；但右侧不仅刻度间隔极大（每档跨度为20），而且图表中缺乏对应的水平网格线作为视觉辅助对齐，纯靠目测使得读数误差极易超过5%的容许范围。
> 
> ### 不确定的
> 对于接近0轴的柱子（如1998、2020、2021年），其具体是完全等于0.0还是微小的负值（如-0.2），仅凭视觉判定存在一定的不确定性，无法做到绝对精确。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | compound | 54 | Figure B.1 | above | none |
| gpt-5.6-sol | f1 | compound | 53 | Figure B.1 | above | none |
| gemini-3.1-pro | f1 | compound | 52 | Figure B.1: | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_starts_above_zero` | ✓ | — | — | opus-5: right axis lowest tick is '40', not zero, and is not cut |
| `color_encodes_extra_attribute` | ✓ | ✓ | — | opus-5: Note: 'The light blue fill indicates a contribution of negative growth in high-income economies.'；gpt-5.6-sol: “The light blue fill indicates a contribution of negative growth in high-income economies.” |
| `dual_axis` | ✓ | ✓ | ✓ | opus-5: left axis '-1..8 Speed of income convergence (percentage points)', right axis '40..160 Trade participation (100=1996)'；gpt-5.6-sol: Left axis runs -1 to 8; right axis runs 40 to 160.；gemini-3.1-pro: a left axis for percentage points and a right axis for an index |
| `footnote_marker` | ✓ | — | — | opus-5: superscript markers in body text: 'global poverty rate1' and 'Cerdeiro and Komaromi, 2021).2' |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: faint horizontal rules at each left tick; no vertical rules in the plot area；gpt-5.6-sol: Horizontal rules cross the plot; no vertical grid lines are drawn.；gemini-3.1-pro: horizontal lines are drawn across the plot, with no vertical lines |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'Speed of income convergence' swatch and 'Trade participation' line sit in a row under the plot；gpt-5.6-sol: The two-item legend is centred beneath the year labels.；gemini-3.1-pro: the legend sits below the x-axis tick labels |
| `missing_value_marker` | ✓ | — | — | opus-5: the 1998 slot between the 1997 and 1999 bars is empty, no bar drawn |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: blue bars per year with a continuous green line drawn over them in the same panel；gpt-5.6-sol: Blue bars and a turquoise line occupy the same panel.；gemini-3.1-pro: bars are used for convergence speed, a line for trade participation |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: the 2021 bar hangs below the zero line; lowest left tick reads '-1'；gpt-5.6-sol: The 2021 blue bar extends below the zero line.；gemini-3.1-pro: the left axis starts at -1, and several bars drop below zero |
| `rebased_index_values` | ✓ | — | ✓ | opus-5: right axis title reads 'Trade participation (100=1996)'；gemini-3.1-pro: the right y-axis title indicates 100=1996 |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: both 'Speed of income convergence (percentage points)' and 'Trade participation (100=1996)' set vertically；gpt-5.6-sol: Both value-axis titles run vertically along the plot sides.；gemini-3.1-pro: both left and right axis titles are set vertically |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: year labels 1996 ... 2021 are turned about 45 degrees under the axis；gpt-5.6-sol: Year labels 1996 through 2021 are rotated diagonally.；gemini-3.1-pro: the year labels on the bottom axis are rotated diagonally |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Source: Authors' calculations, based on World Bank data...' and 'Note: The figure displays...' below the plot；gpt-5.6-sol: “Source:” and “Note:” lines are printed below the chart.；gemini-3.1-pro: Source: and Note: paragraphs are placed under the figure |
| `stacked_bar` | ✓ | ✓ | — | opus-5: 2008 and 2009 bars carry a light blue segment sitting on top of the dark blue part；gpt-5.6-sol: The 2008 and 2009 bars contain dark- and light-blue stacked sections. |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: '(percentage points)' sits in the left axis title; bars carry no printed numbers；gpt-5.6-sol: Axes read “percentage points” and “Trade participation (100=1996)”. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `title_in_filled_banner` | opus-5 | 3,4 | 'Figure B.1: Positive correlation between...' printed white on a solid blue band spanning the figure width |
| `segment_meaning_only_in_note` | opus-5 | 3 | legend lists only two series; the light blue bar segment is defined solely in the Note text |
| `title_in_colored_banner` | gemini-3.1-pro | 4 | the figure title and number are enclosed in a full-width blue rectangular banner |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 2.7 | 1996、Speed of income convergence | Speed of income convergence、1996 | 2001、Speed of income convergence | 1996、Speed of income convergence | ✓ | ✗ | ✓ | 过 |
| 100 | 1996、Trade participation | Trade participation、1996 | 1996、Trade participation | 1996、Trade participation | ✓ | ✓ | ✓ | 没过 |
| 0.0 | 1998、Speed of income convergence | Speed of income convergence、1998 | 1998、Speed of income convergence | 1998、Speed of income convergence | ✓ | ✓ | ✓ | 过 |
| 4.6 | 2008、Speed of income convergence | Speed of income convergence、2008 | 2008、Speed of income convergence | 2006、Speed of income convergence | ✓ | ✓ | ✗ | 过 |
| 155 | 2008、Trade participation | Trade participation、2008 | 2008、Trade participation | 2008、Trade participation | ✓ | ✓ | ✓ | 过 |
| 7.7 | 2009、Speed of income convergence | Speed of income convergence、2009、light blue fill | 2009、Speed of income convergence | 2009、Speed of income convergence | ✓ | ✓ | ✓ | 过 |
| 128 | 2009、Trade participation | Trade participation、2003 | 2014、Trade participation | 2011、Trade participation | ✗ | ✗ | ✗ | 没过 |
| 138 | 2010、Trade participation | Trade participation、2004 | 2012、Trade participation | 2006、Trade participation | ✗ | ✗ | ✗ | 没过 |
| -0.2 | 2021、Speed of income convergence | Speed of income convergence、2021 | 2021、Speed of income convergence | 2020、Speed of income convergence | ✓ | ✓ | ✗ | 没过 |
| 125 | 2021、Trade participation | Trade participation、2009 | 2009、Trade participation | 2021、Trade participation | ✗ | ✗ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `key_roles#f1` | ["colour_group", "series", "time"] | ["series", "time"] | ["series", "time"] | series × time | <strong>colour_group 的判据</strong>：只由颜色承载、既不是系列也不是类目的<strong>第三个变量</strong>。单独给某一个类目换色（`highlighted_category`）不算；图例里列出的项是 series。 opus 记的 colour_group 是「light blue fill」，`label_source` 为 `not_shown`——页面上没有名字，<strong>panel 的判据</strong>：要有自己的绘图区，而且名字要印在页面上。`label_source` 是 `not_shown` 的段进不了键——键必须逐字可复制。 |
