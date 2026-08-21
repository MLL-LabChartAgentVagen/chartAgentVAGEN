# 2024_healthatglance_rep_en_p115

![2024_healthatglance_rep_en_p115](../../data/pages/2024_healthatglance_rep_en_p115.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `2024_healthatglance_rep_en_p115` | 2024_healthatglance_rep_en | untagged | 10 | `parsebench/data/pages/2024_healthatglance_rep_en_p115.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 三幅独立编号图共处一页:两幅「分组柱+菱形合计标记」(Figure 3.19、3.21)和一幅五条折线的时间序列(Figure 3.20)。生成器要能:图例置于灰色横带内、位于标题与绘图区之间;单位句(`Age-standardised rate per 100 000 population`、`% of population aged 50 and over with a score of 4 or higher`)单独一行压在最高刻度之上;国名 45° 斜排,并把 `EU27`/`EU26` 聚合项染成红色;3.19 在 Slovenia 与 Türkiye 之间留一个空槽把非欧盟国家分组;标签带脚注号 `United Kingdom1`;图下 Note/Source 与 StatLink 链接各一行。3.19 单图 34 类 × 3 系列 ≈ 102 个标记。
> 
> ## 定位一个值难在哪
> `10.5` 是 Figure 3.20 中 EU27 红线 2021 年的点:图上无数字,纵轴刻度间隔 5,而 5% 容差只有 ±0.53,约为一格的十分之一;还须先由图例(而非线旁标签)认出红线是 `EU27`,再在 18 个年份刻度中定位 2021。
> 
> ## 不确定的
> 所有数值均未印在图上,`11.0`、`22.0`、`28`、`12`、`20`、`40` 只能靠像素高度猜归属,可能落在相邻国家上;3.19 与 3.21 绘图区是否有浅灰底纹、菱形究竟属 Women 还是 Total 系列的叠放次序,均不能确证。

**gpt-5.6-sol**

> ### 画出来要什么
> 三个独立编号图均需上置拆分标题、单位行、灰底双向网格、横幅式图例、注释、来源及 StatLink。图3.19和3.21是并列柱叠加菱形总计，并突出 EU27/EU26；图3.20是五序列年度折线。
> 
> ### 定位一个值难在哪
> 图3.20的“2016—EU27—10.5”需同时匹配年份和图例。数值未印出，纵轴每5单位一格，而5%容差仅0.525，插值精度不足。
> 
> ### 不确定的
> 源数据小数不可见；20、28、40等高度在图3.21有多个候选标记。图3.19中“Slovenia”与“Türkiye”间留白的分组含义未标明。

**gemini-3.1-pro**

> ### 画出来要什么
> 本页包含三张图表，整体采用了统一的配色与排版风格：
> 1. **排版与标题**：图表编号、主标题在一行。Y轴的单位说明直接放置在坐标轴上方，而非纵向旋转。底部均附有Note和Source，以及一个StatLink连接。
> 2. **图表类型与标记**：图3.19和3.21为分组柱状图与散点（菱形）混合图。图例说明了颜色代表的不同性别（男、女、总计），分别对应不同颜色的柱子与独立悬浮的菱形标记。图3.20为普通的折线图。
> 3. **颜色编码**：具有聚合属性的特殊类别（EU27、EU26）在柱状图和折线图中被强制高亮显示为红色/橙色，而其他普通国家为蓝色。此特殊的颜色映射独立于图例之外。
> 4. **坐标轴与网格**：所有图表仅带有横向网格线。图3.19的X轴在使用倾斜标签时，在Slovenia和Türkiye之间保留了一格无柱子的空白区间，用于对国家进行视觉上的逻辑分组。
> 
> ### 定位一个值难在哪
> 以 `53` (图3.21，Portugal, Women) 为例。首先，数据点没有任何直接的文本数值标注，必须通过柱状图的高度水平对齐左侧Y轴来进行读数。该Y轴的刻度间隔为10（从0到60），53位于50和60之间，完全依赖视觉估算，极难保证5%以内的误差容忍度。其次，X轴标签十分密集且呈45度倾斜，增加了在长轴末端准确对应“Portugal”类别的难度。
> 
> ### 不确定的
> 图3.19X轴Slovenia与Türkiye之间的空白间隔，尚不确定是通过手动插入名为“空”的类别占位符来实现，还是依赖底层系统内建的分类间距(Gap)设置，这直接决定了在恢复数据表时是否会多出一行空值。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | grouped_bar | 102 | Figure 3.19. | above | none |
| opus-5 | f2 | line | 90 | Figure 3.20. | above | none |
| opus-5 | f3 | grouped_bar | 81 | Figure 3.21. | above | none |
| gpt-5.6-sol | f1 | compound | 102 | Figure 3.19 | above | none |
| gpt-5.6-sol | f2 | line | 90 | Figure 3.20 | above | none |
| gpt-5.6-sol | f3 | compound | 81 | Figure 3.21 | above | none |
| gemini-3.1-pro | f1 | grouped_bar | 102 | Figure 3.19. | above | none |
| gemini-3.1-pro | f2 | line | 90 | Figure 3.20. | above | none |
| gemini-3.1-pro | f3 | grouped_bar | 81 | Figure 3.21. | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | — | — | opus-5: 'EU26' printed as a category tick among full country names |
| `axis_title_above_axis` | ✓ | ✓ | ✓ | opus-5: unit line printed above the '40' tick, not alongside the axis；gpt-5.6-sol: The percentage scale phrase is printed above the plot’s left edge.；gemini-3.1-pro: the value axis titles sit above the top tick in all figures |
| `color_encodes_extra_attribute` | — | ✓ | ✓ | gpt-5.6-sol: Orange-red identifies EU26 as the aggregate, but that colour is absent from the legend.；gemini-3.1-pro: EU aggregates are red/orange while other countries are blue |
| `data_link_below_figure` | ✓ | ✓ | ✓ | opus-5: 'StatLink' logo with 'https://stat.link/x8j1n2' under Figure 3.19；gpt-5.6-sol: “StatLink” and “https://stat.link/1s9j6g” appear below the figure.；gemini-3.1-pro: StatLink URLs are placed at the bottom right of each figure |
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: 34 country slots times two bars plus a diamond, about 102 marks；gpt-5.6-sol: Thirty-four categories each contain two bars and one diamond, totalling 102 marks.；gemini-3.1-pro: f1 has 34 categories * 3 series = 102 marks |
| `footnote_marker` | ✓ | ✓ | ✓ | opus-5: tick reads 'United Kingdom1'; note says '1. The data for the United Kingdom relate to 2020'；gpt-5.6-sol: “United Kingdom¹” is keyed to “1. The data for the United Kingdom” below.；gemini-3.1-pro: United Kingdom has a superscript 1 footnote marker |
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: blue Men bar and cyan Women bar paired in each country slot；gpt-5.6-sol: Men and Women bars stand side by side in every country slot.；gemini-3.1-pro: f1 and f3 show grouped bars for Men and Women |
| `hgrid_only` | ✓ | — | ✓ | opus-5: horizontal rules at 10,20...60 only；gemini-3.1-pro: all figures only have horizontal grid lines |
| `highlighted_category` | ✓ | ✓ | ✓ | opus-5: EU27 line is red, the four country lines are shades of blue；gpt-5.6-sol: EU26 bars and diamond are orange-red while country marks use blue shades.；gemini-3.1-pro: EU27 and EU26 are coloured red/orange instead of blue |
| `legend_above_plot` | ✓ | ✓ | ✓ | opus-5: 'Men  Women  Total' row in a grey band above the plot；gpt-5.6-sol: The “Men”, “Women”, “Total” legend is between the title and plot.；gemini-3.1-pro: legends are placed below the titles but above the plot areas |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: 'Total' diamonds overlaid on the Men/Women bar pairs；gpt-5.6-sol: Two bars and a diamond-shaped Total marker share each country slot.；gemini-3.1-pro: bars for Men/Women and diamond point markers for Total in f1 and f3 |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: Figures 3.19, 3.20 and 3.21 each with own number, note and source；gpt-5.6-sol: Three separately numbered figures, “Figure 3.19”, “Figure 3.20” and “Figure 3.21”, appear vertically.；gemini-3.1-pro: three separate numbered figures on the same page |
| `panel_background` | ✓ | ✓ | — | opus-5: plot area behind the five lines carries a light grey tint；gpt-5.6-sol: The plot area has a light-grey fill with white grid lines. |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: country names such as 'Luxembourg' set at about 45 degrees；gpt-5.6-sol: Country labels from “Hungary” to “Lithuania” are diagonally rotated.；gemini-3.1-pro: category labels in f1 and f3 are rotated 45 degrees |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: The EU average is weighted...' and 'Source: Eurostat (hlth_cd_asdr2).' under each figure；gpt-5.6-sol: Lines beginning “Note:” and “Source: SHARE survey (wave 9).” sit below the plot.；gemini-3.1-pro: Note and Source texts are printed below each figure |
| `tick_marker_as_series` | ✓ | — | — | opus-5: legend entry 'Total' is a diamond glyph placed at the category position, same axis as bars |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: '% of population aged 50 and over with a score of 4 or higher' over bare 0-60 ticks；gpt-5.6-sol: “% of population aged 50 and over with a score of 4 or higher” fixes the scale. |
| `wrapped_category_labels` | ✓ | — | — | opus-5: 34 rotated country names stacked along one axis, e.g. 'Slovak Republic' |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `category_axis_group_gap` | opus-5 | 3 | an empty slot between 'Slovenia' and 'Türkiye' separates EU members from non-EU countries |
| `legend_band_background` | opus-5 | — | each legend row sits inside a full-width light grey band above the plot |
| `categories_sorted_by_series_value` | opus-5 | 3 | countries ordered ascending by the Total diamond, Hungary lowest to Lithuania highest |
| `unit_line_as_separate_text_row` | opus-5 | 4 | '% of population aged 50 and over with a score of 4 or higher' is a free text line, not an axis title |
| `category_group_gap` | gpt-5.6-sol | — | A wide blank category gap separates “Slovenia” from “Türkiye” on the x axis. |
| `legend_banner_background` | gpt-5.6-sol | — | Each legend sits inside a full-width light-grey horizontal banner above its plot. |
| `gap_in_category_axis` | gemini-3.1-pro | 3,4 | an empty slot separates Slovenia from Türkiye on the x-axis |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 35.0 | Lithuania、Men | Lithuania、Men、Age-standardised rate per 100 000 population | Lithuania、Men | Men、Lithuania | ✓ | ✓ | ✓ | 过 |
| 11.0 | EU27、Total | EU27、Total | Czechia、Total | Total、EU27 | ✓ | ✗ | ✓ | 过 |
| 43.0 | 2004、Lithuania | Lithuania、2004 | 2004、Lithuania | Lithuania、2004 | ✓ | ✓ | ✓ | 过 |
| 10.5 | 2021、EU27 | EU27、2021 | 2016、EU27 | EU27、2017 | ✓ | ✗ | ✗ | 过 |
| 22.0 | 2013、Slovenia | Slovenia、2009 | 2007、Cyprus | Slovenia、2012 | ✗ | ✗ | ✗ | 过 |
| 53 | Portugal、Women | Portugal、Women | Portugal、Women | Women、Portugal | ✓ | ✓ | ✓ | 过 |
| 28 | EU26、Total | Latvia、Women | Germany、Total | Men、Lithuania | ✗ | ✗ | ✗ | 过 |
| 12 | Hungary、Men | Cyprus、Men | Hungary、Men | Men、Cyprus | ✗ | ✓ | ✗ | 过 |
| 20 | Cyprus、Women | Portugal、Men | Croatia、Men | Women、Cyprus | ✗ | ✗ | ✓ | 过 |
| 40 | Lithuania、Total | Romania、Women | Lithuania、Total | Women、Romania | ✗ | ✓ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "grouped_bar" | "compound" | "grouped_bar" | compound | 按类型表自己的定义判：`compound` 是<strong>同一个面板里出现两种以上图元形状</strong>，所以决定它的是三家自己在 `components` 里记的 `mixed_marks`，不是它们给这张图起的名字。opus 与 gpt 都在这张图上记了 `mixed_marks`（分组条上叠了短横标记），opus 还记了 `tick_marker_as_series`。分组条是一种形状，叠上去的标记是第二种，合起来是 compound。三家数出的图元数都是 102，读法一致。 |
| `type#f3` | "grouped_bar" | "compound" | "grouped_bar" | compound | 同一页的第三张，与 f1 同因：三家图元数都是 81，opus 与 gpt 都记了 `mixed_marks`。 |
