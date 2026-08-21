# Quarterly-Sector-and-Investment-Research-Update-Q1-2025_p12

![Quarterly-Sector-and-Investment-Research-Update-Q1-2025_p12](../../data/pages/Quarterly-Sector-and-Investment-Research-Update-Q1-2025_p12.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `Quarterly-Sector-and-Investment-Research-Update-Q1-2025_p12` | Quarterly-Sector-and-Investment-Research-Update-Q1-2025 | need_estimate | 10 | `parsebench/data/pages/Quarterly-Sector-and-Investment-Research-Update-Q1-2025_p12.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 两幅并列、各自带小标题与副标题的图。左图:1990–2024 月度折线(约 410 点),纵轴 0–250、旋转纵轴标题 “Price-to-book valuation spreads”,x 轴年份旋转 90°、且刻度稀疏不均(1990、1992、1994、1995…),外加两条几乎不可见的浅灰竖向渐变带。右图:四根绿色柱,含负值与零线,y 轴 -3%–5%,类别标签两行折行(“Rates Rising/ Spreads Rising”),仅第三根柱印有 “4%” 且其背后有一块灰色渐变高亮块。页脚是加粗+正文混排的来源注。
> 
> **定位一个值难在哪**
> 
> “-2.3%”:它没有印在图上,只能靠 1% 一格的刻度目测,-2.3 与 -2.4 之间的差已接近 5% 容差;寻址还必须用完整折行标签 “Rates Rising/Spreads Rising”,而页面上它被换行成两行,表格里往往写成一行,导致标签对不上。
> 
> **不确定的**
> 
> 左图两块浅灰竖带的含义无任何图例说明(疑似 2016–2017、2022–2024 高亮期),我只能按颜色命名;折线点数按月频估算;右图第三根柱背后的灰块究竟是高亮还是阴影带无法确认。

**gpt-5.6-sol**

> **画出来要什么**：一页双图：左侧约407个月度点的单线图，配竖排稀疏年份刻度、纵轴标题和两段灰色时窗；右侧四根跨零柱，第三类别整列灰底，并在柱外标“4%”。还需页级说明和来源脚注。
> 
> **定位一个值难在哪**：右图“-2.3%”只能在每格1个百分点的轴上估读，而5%容差仅0.115点。左图“60”还对应多个没有月份标签的点。
> 
> **不确定的**：左图灰带含义未标；月度点数按脚注日期估为407。除“4%”外，右图柱值均需按轴估读；未给日期的左图值无法唯一定位。

**gemini-3.1-pro**

> ## 画出来要什么
> 要生成此页面，系统需要支持左右并排的多图表布局。左图是高密度的折线图，包含不规则间隔的垂直X轴时间标签，并带有表示特定时期的灰色背景阴影带；Y轴标题旋转90度。右图是包含负值的柱状图，0轴位于图表中间，部分柱子向下延伸；需要支持在特定分类背景加灰色高亮带，同时X轴类别标签需要自动换行，且只有个别柱子上方悬浮显示外部数据标签。此外，页面顶部有全局的主标题和描述，各图表带有各自独立的标题和副标题模块。
> 
> ## 定位一个值难在哪
> 以右图的 `-2.3%` 为例，该数值没有直接打印在图表上。Y轴的刻度间隔为 `1%`，依靠肉眼读取该向下的柱子高度时，很难精确判断它是 `-2.2%` 还是 `-2.3%`，这远超出了 5%（即约 `0.1%`）的容错范围，必然导致 Step 2 失败。左图的高密度连续折线图由于没有散点标记，同样不可能肉眼精确定位并读取特定时间点的值。
> 
> ## 不确定的
> 左图的X轴年份标签间隔极不规律（如 1990, 1992, 1994, 1995, 1997），无法确定这是生成器基于空间不足自动隐藏防重叠的逻辑结果，还是人为故意挑选展示特定年份的配置。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 410 | — | above | none |
| opus-5 | f2 | bar | 4 | — | above | some |
| gpt-5.6-sol | f1 | line | 407 | — | above | none |
| gpt-5.6-sol | f2 | bar | 4 | — | above | some |
| gemini-3.1-pro | f1 | line | 400 | — | above | none |
| gemini-3.1-pro | f2 | bar | 4 | — | above | some |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: Monthly line from December 1990 to October 2024, roughly 410 plotted points；gpt-5.6-sol: Monthly December 1990 to October 2024 data imply approximately 407 plotted points.；gemini-3.1-pro: the blue line plots ~400 monthly points continuously |
| `highlighted_category` | ✓ | ✓ | — | opus-5: Third bar sits on a grey shaded column and alone carries the printed '4%'；gpt-5.6-sol: The “Rates Falling/Spreads Falling” category slot has a grey background behind its green bar. |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: Two captioned charts side by side: 'Valuation spreads are wide' and 'Financials have benefited from falling rates...'；gpt-5.6-sol: Two separately titled plots sit side by side: valuation spreads and relative performance.；gemini-3.1-pro: two distinct independently titled figures sitting side by side |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: Three bars drop below the 0% line; axis runs to -3%；gpt-5.6-sol: First and fourth green bars extend below the horizontal 0% line.；gemini-3.1-pro: the y axis extends down to -3% with downward growing bars |
| `reference_line` | ✓ | ✓ | — | opus-5: A horizontal rule drawn at 0% across the plot with bars on both sides；gpt-5.6-sol: A horizontal zero baseline crosses all four bars at 0%. |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Price-to-book valuation spreads' set vertically along the left axis；gpt-5.6-sol: “Price-to-book valuation spreads” runs vertically beside the left axis.；gemini-3.1-pro: Price-to-book valuation spreads is rotated along the y axis |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: Year labels 1990, 1992 ... 2024 turned 90 degrees under the axis；gpt-5.6-sol: Year labels from “1990” through “2024” are rotated vertically.；gemini-3.1-pro: the year labels on the bottom axis are rotated 90 degrees |
| `shaded_band` | ✓ | ✓ | ✓ | opus-5: Two pale grey vertical bands over roughly 2016–2017 and 2022–2024 behind the line；gpt-5.6-sol: Vertical grey bands appear behind the line around 2016–2017 and 2022–2024.；gemini-3.1-pro: grey vertical bands highlight recession periods |
| `side_text_bullets` | ✓ | — | — | opus-5: Deck-style grey standfirst paragraph above both charts referencing '(left)' and '(right)' |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Sources: Haver Analytics, FactSet, Fidelity Investments, as of 11/30/24. LEFT: Valuation spread: ...'；gpt-5.6-sol: “Sources: Haver Analytics, FactSet, Fidelity Investments, as of 11/30/24.” appears below both plots.；gemini-3.1-pro: small print at the bottom reading Past performance is no guarantee... |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: Monthly data but ticks read 1990, 1992, 1994, 1995, 1997, 1998, 2000 — uneven gaps；gpt-5.6-sol: Monthly data are shown, but only selected years from “1990” to “2024” are labelled.；gemini-3.1-pro: axis labels irregularly skip years like 1994, 1995, 1997 |
| `unit_in_axis_or_title` | ✓ | — | — | opus-5: Bare axis numbers 0..250; scale word only in 'Price-to-book valuation spreads' |
| `value_label_inside` | ✓ | — | — | opus-5: '4%' printed in bold above the third bar inside the grey highlight block |
| `value_label_outside` | — | ✓ | ✓ | gpt-5.6-sol: “4%” sits above the third green bar.；gemini-3.1-pro: the 4% label is printed above the top of the green bar |
| `wrapped_category_labels` | ✓ | ✓ | ✓ | opus-5: 'Rates Rising/ Spreads Rising' wraps onto two lines under each bar；gpt-5.6-sol: Each category wraps across two lines, such as “Rates Rising/” over “Spreads Rising”.；gemini-3.1-pro: x-axis labels wrap to two lines, e.g., Rates Rising/ Spreads Rising |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `gradient_fill_band` | opus-5 | 4 | Grey bands fade from solid at top to white at the baseline, not a flat tint |
| `unlabelled_shaded_region` | opus-5 | 3,4 | Two grey vertical bands with no legend, note or annotation naming what they mark |
| `slash_compound_category_label` | opus-5 | 3 | Category names combine two conditions with a slash: 'Rates Falling/ Spreads Falling' |
| `left_right_figure_reference_in_prose` | opus-5 | 4 | Standfirst says 'near recessionary levels (left)' and 'historically (right)' to address the two charts |
| `inward_facing_ticks` | gemini-3.1-pro | — | y-axis tick marks are drawn inwards into the plot area |
| `category_background_highlight` | gemini-3.1-pro | — | a grey background rectangle spans the full height of one specific column |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 4% | Rates Falling/ Spreads Falling | Rates Falling/ Spreads Falling、NTM Average Relative Performance when Credit Spreads (HYOAS) or Rates (1-Yr Yield) Are Rising or Falling, 1980–Present | Rates Falling/
Spreads Falling | Rates Falling/ Spreads Falling | ✓ | ✓ | ✓ | 过 |
| -2.3% | Rates Rising/ Spreads Rising | Rates Rising/ Spreads Rising | Rates Rising/
Spreads Rising | Rates Rising/ Spreads Rising | ✓ | ✓ | ✓ | 过 |
| 0.5% | Rates Rising/ Spreads Falling | Rates Rising/ Spreads Falling | Rates Rising/
Spreads Falling | Rates Rising/ Spreads Falling | ✓ | ✓ | ✓ | 过 |
| -1.9% | Rates Falling/ Spreads Rising | Rates Falling/ Spreads Rising | Rates Falling/
Spreads Rising | Rates Falling/ Spreads Rising | ✓ | ✓ | ✓ | 没过 |
| 150 | 1990、Price-to-book valuation spreads | 1990、Price-to-book valuation spreads | 1990 | 1990 | ✓ | ✗ | ✗ | 过 |
| 90 | 2008、Price-to-book valuation spreads | 1992、Price-to-book valuation spreads |  | 2021 | ✗ | ✗ | ✗ | 没过 |
| 30 | 2005、Price-to-book valuation spreads | 1997、Price-to-book valuation spreads |  | 1997 | ✗ | ✗ | ✗ | 没过 |
| 75 | 2024、Price-to-book valuation spreads | 2024、Price-to-book valuation spreads |  | 2024 | ✓ | ✗ | ✗ | 过 |
| 60 | 1992、Price-to-book valuation spreads | 2011、Price-to-book valuation spreads |  | 1998 | ✗ | ✗ | ✗ | 过 |
| 60 | 2000、Price-to-book valuation spreads | 2022、Price-to-book valuation spreads |  | 2000 | ✗ | ✗ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `density#f1` | ">400" | ">400" | "151–400" | >400（按中位数 407 个图元） | 三家数出的图元个数是 410 / 407 / 400，中位数 407，落在 >400。三个数彼此相差不到一半，分歧是<档的边界>而不是读法：它们看的是同一张图，只是刚好被 20 / 60 / 150 / 400 这几条线切开。 |
| `key_roles#f1` | ["series", "time"] | ["time"] | ["time"] | time | gpt 与 gemini 一致。这张图只有一条线，单系列不需要一段 series 才唯一；opus 记的那一段来自 `heading`，是图的题名。 |
