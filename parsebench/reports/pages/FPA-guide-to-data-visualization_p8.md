# FPA-guide-to-data-visualization_p8

![FPA-guide-to-data-visualization_p8](../../data/pages/FPA-guide-to-data-visualization_p8.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `FPA-guide-to-data-visualization_p8` | FPA-guide-to-data-visualization | need_estimate | 10 | `parsebench/data/pages/FPA-guide-to-data-visualization_p8.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一张无编号的「风向袋(windsock)」扇形图:标题 `Western Europe Net Sales Windsock` 在上,图例横排在标题与绘图区之间,含三个逗号分隔的灰色色块 + `Scenarios`、橙线 `Budget`、红线 `Prior Year`、深蓝线 `Forecast`。绘图区要能叠三层深浅不同的灰色情景带(从 Jan 的一点向右张开、到 May 截断),两条贯穿全年的水平参考线,一条只画到 May 的折线,以及 May 处一条无标签的竖向虚线。纵轴 100–220、每 20 一格、只有横向点状网格,单位 `$m` 写在最高刻度 220 之上;横轴首个刻度分两行写 `Jan` / `14`,其余只写月份。图上不印任何数值。
> 
> ## 定位一个值难在哪
> 以 `Forecast` 四月的 210 为例:它没有印在图上,210 落在 200 与 220 两条网格线中间,只能靠线宽约 3px 的深蓝线目测插值;地址需要「系列名 `Forecast` + 月份 `Apr`」两段标签,而灰带把线周围的背景填满,起止点也无标记点。
> 
> ## 不确定的
> 三个灰色色块各代表哪一档情景概率,页面只写 `Scenarios`,无从得知;May 处竖虚线的含义(实际/预测分界?)未标注;Budget 与 Prior Year 是否恰为 218 与 166 只能按刻度读;图下无 Source/Note 行。

**gpt-5.6-sol**

> ### 画出来要什么
> 重建一幅复合图：标题“Western Europe Net Sales Windsock”置于上方；左轴以“$m”为单位、范围100—220，底轴从“Jan 14”到“Dec”。图内包含三层灰色情景区间、Budget与Prior Year水平基准线、以及截至May的Forecast折线；图例位于图上方。
> 
> ### 定位一个值难在哪
> “Forecast—Feb—216”需同时依靠图例“Forecast”和横轴“Feb”定位。数值未印出，只能在200与220两条网格线之间估读。
> 
> ### 不确定的
> 三种灰色情景仅共用“Scenarios”标签，没有各层名称；情景区间的数据点数和边界含义只能据图形估计。

**gemini-3.1-pro**

> ### 画出来要什么
> 需要支持混合图表（折线图结合面积图）。x 轴需要支持时间刻度的特殊排版（如“Jan”下方换行显示“14”）。y 轴单位“$m”需放置在轴顶端刻度的正上方，且 y 轴从 100 起始。图例需要横向排列在标题和绘图区之间。最关键的是，需要能够将某个系列绘制为带有渐变或固定颜色的不规则阴影区域（Scenarios），以及将某些系列绘制为横跨整个坐标轴的水平参考线（Budget 和 Prior Year）。
> 
> ### 定位一个值难在哪
> 以 Forecast 在 Feb 的值 216 为例。图表中没有任何数据标签，必须依靠肉眼将数据点与 y 轴对齐。y 轴刻度间隔为 20，在 200 到 220 之间读取 216 需要高精度的视觉插值。此外，Scenarios 作为一个表示范围的阴影面，在图例中只有一个条目对应了两个不同颜色的色块，它在每个月对应上限和下限多个界限，这使得通过标准的“系列+时间”键值对来定位阴影区内特定的数值变得非常困难。
> 
> ### 不确定的
> Scenarios 阴影区域具体的上下限数值是未知的，只能大致估算。同时，Budget 和 Prior Year 表现为贯穿全年的水平线，无法确定它们在底层数据表里是作为一个单独的标量存储，还是在每个月都有一个相同数值的数据点。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | other · windsock fan chart | 8 | — | above | none |
| gpt-5.6-sol | f1 | compound | 25 | — | above | none |
| gemini-3.1-pro | f1 | other · windsock chart | 15 | — | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_starts_above_zero` | ✓ | ✓ | ✓ | opus-5: lowest y tick reads `100`, no break glyph on the axis；gpt-5.6-sol: The left value axis begins at 100 without a break glyph.；gemini-3.1-pro: the lowest tick on the y-axis is 100 |
| `axis_title_above_axis` | ✓ | ✓ | ✓ | opus-5: `$m` printed above the topmost tick `220`；gpt-5.6-sol: “$m” is positioned above the 220 tick.；gemini-3.1-pro: $m sits directly above the top y-axis tick label |
| `color_encodes_extra_attribute` | ✓ | ✓ | — | opus-5: three grey shades nested inside each other; legend names them all only `Scenarios`；gpt-5.6-sol: Three grey shades distinguish scenario levels, but all share the label “Scenarios”. |
| `error_bars` | ✓ | ✓ | — | opus-5: grey shaded scenario bands fan out around the forecast path from Jan to May；gpt-5.6-sol: Grey statistical scenario ranges form shaded uncertainty bands from Jan 14 through May. |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: dotted horizontal rules at 220,200,180,160,140,120,100; no vertical grid；gpt-5.6-sol: Dotted horizontal grid lines cross the plot; no vertical grid is drawn.；gemini-3.1-pro: only horizontal dashed grid lines are drawn |
| `legend_above_plot` | ✓ | ✓ | ✓ | opus-5: legend row sits between the title and the plot: `Scenarios  Budget  Prior Year  Forecast`；gpt-5.6-sol: The legend row sits between “Western Europe Net Sales Windsock” and the plot.；gemini-3.1-pro: legend sits horizontally between the title and the plot |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: filled grey band polygons and three plotted lines drawn in the same panel；gpt-5.6-sol: Three grey filled scenario bands share the panel with Budget, Prior Year, and Forecast lines.；gemini-3.1-pro: Forecast is a line segment, Scenarios is a shaded area |
| `nonstandard_time_ticks` | — | ✓ | ✓ | gpt-5.6-sol: “Jan” sits over “14”; later ticks show month abbreviations only.；gemini-3.1-pro: 14 is printed on a second line below Jan |
| `reference_line` | ✓ | ✓ | — | opus-5: orange rule at ~218 and red rule at ~166 span the full year, legend `Budget`, `Prior Year`；gpt-5.6-sol: Budget and Prior Year are straight horizontal comparison lines across the monthly plot. |
| `shaded_band` | ✓ | — | — | opus-5: tinted grey range spans Jan to May marking the statistical risk window |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: y ticks are bare numbers 100..220; only `$m` fixes the scale；gpt-5.6-sol: “$m” appears above the numbered left value axis.；gemini-3.1-pro: the unit $m is written on the axis |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `multi_swatch_single_legend_entry` | opus-5 | 3 | legend shows three grey squares separated by commas before the single word `Scenarios` |
| `unlabelled_vertical_cutoff_line` | opus-5 | 3,4 | dashed vertical rule at `May` where the forecast line and bands stop; no label or legend |
| `year_on_first_time_tick_only` | opus-5 | 3 | first x tick reads `Jan` with `14` on a second line; other ticks show month only |
| `series_truncated_mid_axis` | opus-5 | 1,3 | Forecast line and grey bands end at `May` while Budget and Prior Year run to `Dec` |
| `nested_uncertainty_bands` | gpt-5.6-sol | 2,3 | Three differently shaded grey scenario ranges are nested across Jan 14 through May. |
| `multi_swatch_legend_entry` | gpt-5.6-sol | 3 | Three separate grey swatches collectively precede the single legend label “Scenarios”. |
| `shaded_range_series` | gemini-3.1-pro | 1,2 | Scenarios series is drawn as a shaded area bounding a range |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 218 | Budget、Jan 14 | Budget、Jan | Budget、Jan
14 | Budget、Jan 14 | ✓ | ✓ | ✓ | 过 |
| 218 | Budget、Nov | Budget、Dec | Budget、Dec | Budget、Feb | ✗ | ✗ | ✗ | 过 |
| 166 | Prior Year、Jan 14 | Prior Year、Jan | Prior Year、Jan
14 | Prior Year、Jan 14 | ✓ | ✓ | ✓ | 过 |
| 166 | Prior Year、Jun | Prior Year、May | Prior Year、May | Prior Year、Feb | ✗ | ✗ | ✗ | 过 |
| 166 | Prior Year、Dec | Prior Year、Dec | Prior Year、Dec | Prior Year、Mar | ✓ | ✓ | ✗ | 过 |
| 218 | Forecast、Jan 14 | Forecast、Jan | Forecast、Jan
14 | Forecast、Jan 14 | ✓ | ✓ | ✓ | 过 |
| 216 | Forecast、Feb | Forecast、Feb | Forecast、Feb | Forecast、Feb | ✓ | ✓ | ✓ | 过 |
| 212 | Forecast、Mar | Forecast、Mar | Forecast、Mar | Forecast、Mar | ✓ | ✓ | ✓ | 过 |
| 210 | Forecast、Apr | Forecast、Apr | Forecast、Apr | Forecast、Apr | ✓ | ✓ | ✓ | 过 |
| 200 | Forecast、May | Forecast、May | Forecast、May | Forecast、May | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "other · windsock fan chart" | "compound" | "other · windsock chart" | other · 扇形预测带（windsock / fan chart） | opus 与 gemini 各自独立地写出 `windsock`，两家都记了 `mixed_marks` 与 `reference_line`：一条实测线接一段向外张开的灰色预测带。<strong>类型表里没有这一族</strong>——面积族画的是堆叠带，画不出以中线为轴向外张开的不确定带。这是 P10 在这一轮新添的一个族。 |
| `density#f1` | "≤20" | "21–60" | "≤20" | ≤20（按中位数 15 个图元） | 三家数出的图元个数是 8 / 25 / 15，中位数 15，落在 ≤20。三个数相差超过一半，取中位数所在的档；差异来自把叠在一起的图元数成一层还是两层。 |
| `key_roles#f1` | ["colour_group", "series", "time"] | ["series", "time"] | ["series", "time"] | series × time | <strong>colour_group 的判据</strong>：只由颜色承载、既不是系列也不是类目的<strong>第三个变量</strong>。单独给某一个类目换色（`highlighted_category`）不算；图例里列出的项是 series。 opus 记的 colour_group 例子是「Scenarios」——那是这张扇形预测带的灰色区间本身，不是一个有名字的第三变量。gpt 与 gemini 都只记了 series 与 time。 |
