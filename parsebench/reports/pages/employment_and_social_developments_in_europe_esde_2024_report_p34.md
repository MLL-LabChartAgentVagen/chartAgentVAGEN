# employment_and_social_developments_in_europe_esde_2024_report_p34

![employment_and_social_developments_in_europe_esde_2024_report_p34](../../data/pages/employment_and_social_developments_in_europe_esde_2024_report_p34.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `employment_and_social_developments_in_europe_esde_2024_report_p34` | employment_and_social_developments_in_europe_esde_2024_report | 3d_chart+need_estimate | 10 | `parsebench/data/pages/employment_and_social_developments_in_europe_esde_2024_report_p34.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 本页两个编号图（Chart 1.23、Chart 1.24），每个都是「一个编号+一个标题+一行说明副标题」，副标题里同时交代左右两个子图的口径（`Left chart: ... ; Right chart: ...`）。每图内含两个异构面板：折线面板与分组柱面板并列，各自独立的纵轴刻度（左 0–60 / 右 0–20；1.24 左侧还是双轴 0–30 与 0–200 的面积+折线混合）。还需要：面板内图例、面板下图例、旋转 90° 的类别刻度（`1st quintile`）、两层 x 轴刻度（`Above 60%` / `Single person with dependent children`）、以及把 `2012` 画成黄色圆点标记叠在柱子上。图下有 Note、Source 与 `Click here to download chart.` 链接行。
> 
> **定位一个值难在哪**
> 
> 以 22.2 为例：正文写「to 22.2% in 2023」，但 Chart 1.24 左图上并没有印数字，只能在 `Below 60% (lhs)` 绿线 2023 处对着左轴 0/10/20/30 读数，刻度间隔 10，5% 容差约 ±1.1，几乎读不准；且必须同时说明是左轴而非右轴（0–200 指数）。
> 
> **不确定的**
> 
> 1.23 右图各柱顶端无数值，19.0、8.2 等只能估读；1.24 左图米色填充带是否属于 rhs 指数系列的面积表现，图例仅给一行文字，无法确认；`Total` 柱是否含全人口亦未说明。

**gpt-5.6-sol**

> ### 画出来要什么
> 页面含两个双面板复合图：Chart 1.23组合折线与分组柱，Chart 1.24组合双轴面积/折线与“分组柱+圆点”。还需双层分类标签、旋转标签、上下分置及逐面板图例、横向虚线网格、来源与下载链接。
> 
> ### 定位一个值难在哪
> 8.2位于Chart 1.24左图的2023年“Above 60% (lhs)”折线。数值未印出，左轴每格5，5%容差仅0.41；同面板指数又须改读右轴。
> 
> ### 不确定的
> 所有目标值均需按轴估读；低值尤其难确认到小数位。Chart 1.24右图的重复“Above 60%/Below 60%”还必须结合外层家庭类型定位。

**gemini-3.1-pro**

> ## 画出来要什么
> 要重构该页面的图表，生成器必须具备处理**异构多子图（Heterogeneous Panels）**的能力。页面中的两个图表（Chart 1.23和1.24）均在一个图表编号和主标题下，并列放置了图表类型、X轴类别与图例完全不同的左右子图。生成器需能通过解析副标题（以分号分隔的“Left chart...; Right chart...”）来为各个子图分配独立的面板名称（Panel Key）。
> 
> 此外，生成器必须支持复杂的**混合标记与双Y轴（Mixed Marks & Dual Axis）**。如Chart 1.24左图同时绘制了面积图（Below 60%）和两条折线图，并使用了非对齐的左右双Y轴（0-30与0-200），需明确映射每个系列归属的Y轴；Chart 1.24右图不仅在X轴有两级嵌套分类（家庭类型与60%阈值上下），还在分组柱状图（2021-2023）上方叠加了代表2012年的散点，需能够渲染这种层级标签与异构标记的结合。
> 
> ## 定位一个值难在哪
> 以Chart 1.24左图中的值 `8.2` 为例。该值属于“Above 60% (lhs)”折线在2023年的数据点，需对齐左侧0-30的Y轴读取。由于该轴每5个单位才有一个刻度，容差5%（0.41）不到刻度间距的十分之一。在没有数据标签的情况下，极难从图形中提取出符合精度要求的值，严重受阻于读取精度（步骤2）。
> 
> ## 不确定的
> 图表中的折线和柱状图缺乏任何数值标签，所有测试值均需从刻度线上估算，部分值如8.2、6.8的实际精确小数位无法单凭图像验证。另外，系统解析副标题时是否会严格按分号拆分作为两个子面板的独立标题仍不确定。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | compound | 54 | Chart 1.23 | above | none |
| opus-5 | f2 | compound | 60 | Chart 1.24 | above | none |
| gpt-5.6-sol | f1 | compound | 54 | Chart 1.23 | above | none |
| gpt-5.6-sol | f2 | compound | 60 | Chart 1.24 | above | none |
| gemini-3.1-pro | f1 | other · heterogeneous panels | 54 | Chart 1.23 | above | none |
| gemini-3.1-pro | f2 | other · heterogeneous panels | 60 | Chart 1.24 | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `data_link_below_figure` | ✓ | ✓ | ✓ | opus-5: 'Click here to download chart.' under both charts；gpt-5.6-sol: “Click here to download chart.” appears beneath the source line.；gemini-3.1-pro: both figures have 'Click here to download chart.' below the source |
| `dense_marks_100plus` | ✓ | — | — | opus-5: two compound figures with roughly 54 and 60 marks combined over four panels |
| `dual_axis` | ✓ | ✓ | ✓ | opus-5: left panel has 0-30 axis at left and 0-200 axis at right；gpt-5.6-sol: The left panel has 0–30 ticks on the left and 0–200 ticks on the right.；gemini-3.1-pro: left panel has a 0-30 axis on the left and a 0-200 axis on the right |
| `footnote_marker` | ✓ | — | — | opus-5: '(49)' superscript in body text pointing to 'Eurostat [hbs_exp_t121]' |
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: right panel: 2021, 2022, 2023 bars side by side under each Above/Below 60% slot；gpt-5.6-sol: Bars for 2021, 2022 and 2023 stand side by side in each threshold slot.；gemini-3.1-pro: both right-hand panels use side-by-side grouped bars |
| `heterogeneous_panel_types` | ✓ | ✓ | ✓ | opus-5: area+line panel left, grouped bar panel right under Chart 1.24；gpt-5.6-sol: The left panel is a time-series area/line plot; the right is grouped bars with points.；gemini-3.1-pro: both figures pair differently formatted charts side-by-side |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: dotted horizontal rules at 10 and 20 in the left panel only；gpt-5.6-sol: Both panels use horizontal dotted grid lines without vertical grid lines.；gemini-3.1-pro: all four panels use horizontal dashed gridlines only |
| `legend_above_plot` | ✓ | ✓ | ✓ | opus-5: '2021 2022 2023' legend sits above the right panel bars；gpt-5.6-sol: “2021 2022 2023” is drawn above the right plot.；gemini-3.1-pro: the right panel legend 2021 2022 2023 sits above the chart area |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'Av. annual index (2015=100) ... (rhs)' legend lines below the left plot；gpt-5.6-sol: Both panel legends are drawn beneath their respective plot areas.；gemini-3.1-pro: f1 left, f2 left and f2 right have legends sitting under the plot |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: left panel: beige filled area plus two solid lines in one plot；gpt-5.6-sol: The left panel mixes lines with a filled area; the right mixes bars with yellow points.；gemini-3.1-pro: left panel mixes filled area and lines, right mixes bars and dots |
| `multi_figure_page` | ✓ | ✓ | — | opus-5: Chart 1.23 and Chart 1.24, each with its own title and source line；gpt-5.6-sol: Separate headings “Chart 1.23” and “Chart 1.24” identify two independent figures. |
| `per_panel_axis_range` | ✓ | — | — | opus-5: left panel axis 0-60, right panel axis 0-20 |
| `per_panel_legend` | ✓ | ✓ | ✓ | opus-5: left panel has its own three-line legend; right panel a separate '2021 2022 2023 2012' legend；gpt-5.6-sol: A line-series legend sits below the left panel and a year legend below the right.；gemini-3.1-pro: every panel has its own separate legend either above or below it |
| `rebased_index_values` | ✓ | ✓ | ✓ | opus-5: 'Av. annual index (2015=100) - Elec., gas and other fuels (rhs)'；gpt-5.6-sol: Both subtitle and legend explicitly state the index base “2015=100”.；gemini-3.1-pro: the legend carries 'Av. annual index (2015=100)' |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: '1st quintile' ... 'Total' set vertically under the right panel；gpt-5.6-sol: “1st quintile” through “Total” are rotated vertically beneath the bars.；gemini-3.1-pro: right panel x-axis labels '1st quintile' are turned vertically |
| `shaded_band` | ✓ | — | — | opus-5: beige filled band spanning 2012-2023 behind the two lines in the left panel |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: Year refers to EU-SILC survey year...' and 'Source: Eurostat, EU SILC ...'；gpt-5.6-sol: A line beginning “Source:” is printed below the figure.；gemini-3.1-pro: both figures have 'Source:' and/or 'Note:' small print below |
| `sparse_time_ticks` | ✓ | — | — | opus-5: left panel ticks 2015-2023 yearly but the line has a 2020 break annotated in the note |
| `tick_marker_as_series` | ✓ | — | — | opus-5: legend entry '2012' drawn as a single yellow dot above each bar group |
| `two_level_x_ticks` | ✓ | ✓ | ✓ | opus-5: inner row 'Above 60%' / 'Below 60%', outer row 'Single person with dependent children'；gpt-5.6-sol: Above/Below 60% labels sit above a second row of three household-composition groups.；gemini-3.1-pro: right panel nests 'Above 60% | Below 60%' under household types |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: subtitle says 'share of population ... (AROP rate)'; axes show bare 0-60；gpt-5.6-sol: The subtitle states “average annual index (2015=100)”.；gemini-3.1-pro: subtitle specifies '(AROP rate)' and '(SMSD rate)' |
| `unit_in_series_name` | ✓ | ✓ | ✓ | opus-5: legend entries end in '(lhs)' and '(rhs)' and carry '(2015=100)'；gpt-5.6-sol: The legend reads “Av. annual index (2015=100) - Elec., gas and other fuels (rhs)”.；gemini-3.1-pro: legend entry reads 'Av. annual index (2015=100)' |
| `wrapped_category_labels` | ✓ | ✓ | — | opus-5: 'HH without dependent children' wraps onto two lines under the axis；gpt-5.6-sol: “Single person with dependent children” and both household labels wrap across multiple lines. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `dual_panel_caption_split` | opus-5 | 3,4 | 'Left chart: ... ; Right chart: ...' one subtitle describing two different panels' units and periods |
| `series_axis_suffix_lhs_rhs` | opus-5 | 2,3 | legend labels carry '(lhs)' and '(rhs)' to bind each series to an axis |
| `area_series_on_secondary_axis` | opus-5 | 2 | beige area read against the right 0-200 axis while lines use the left 0-30 axis |
| `axis_side_in_series_label` | gpt-5.6-sol | 2,3 | The index legend ends “(rhs)”, while both poverty-threshold line labels end “(lhs)”. |
| `panel_descriptions_in_subtitle` | gpt-5.6-sol | 3,4 | Both subtitles use “Left chart:” and “Right chart:” instead of titles above individual panels. |
| `combined_subtitle_for_panels` | gemini-3.1-pro | 3 | subtitles merge descriptions for both panels via a semicolon 'Left chart: ...; Right chart: ...' |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 47 | 2023、Unemployed | Left chart、Unemployed、2015 | Left chart、2023、Unemployed | Left chart: share of population at-risk-of-poverty (AROP rate) for selected characteristics, 2015-2023, EU、2023、Unemployed | ✗ | ✓ | ✓ | 过 |
| 8.5 | 2023、In-work | Left chart、Above 60% (lhs)、2012 | Right chart、2nd quintile、2023 | Left chart: share of population at-risk-of-poverty (AROP rate) for selected characteristics, 2015-2023, EU、2023、In-work | ✗ | ✗ | ✓ | 过 |
| 19.0 | 1st quintile、2023 | Right chart、1st quintile、2021 | Right chart、1st quintile、2023 | Left chart: share of population at-risk-of-poverty (AROP rate) for selected characteristics, 2015-2023, EU、2023、Pensioners | ✗ | ✓ | ✗ | 过 |
| 6.8 | Total、2023 | Above 60%、Single person with dependent children、2021 | Right chart、Total、2023 | Right chart: share of population in severe material and social deprivation (SMSD rate) by income quintile, 2021-2023, EU、Total、2023 | ✗ | ✓ | ✓ | 过 |
| 22.2 | 2023、Below 60% (lhs) | Left chart、Below 60% (lhs)、2023 | Left chart、2023、Below 60% (lhs) | Left chart: share of population below/above the at-risk-of-poverty threshold unable to keep home adequately warm and average annual index (2015=100) for electricity, gas and other fuels, 2012-2023, EU、2023、Below 60% (lhs) | ✓ | ✓ | ✓ | 过 |
| 8.2 | 2023、Above 60% (lhs) | Right chart、2nd quintile、2022 | Left chart、2023、Above 60% (lhs) | Left chart: share of population below/above the at-risk-of-poverty threshold unable to keep home adequately warm and average annual index (2015=100) for electricity, gas and other fuels, 2012-2023, EU、2023、Above 60% (lhs) | ✗ | ✓ | ✓ | 过 |
| 165 | 2023、Av. annual index (2015=100) - Elec., gas and other fuels (rhs) | Av. annual index (2015=100) - Elec., gas and other fuels (rhs)、2023 | Left chart、2023、Av. annual index (2015=100) - Elec., gas and other fuels (rhs) | Left chart: share of population below/above the at-risk-of-poverty threshold unable to keep home adequately warm and average annual index (2015=100) for electricity, gas and other fuels, 2012-2023, EU、2022、Av. annual index (2015=100) - Elec., gas and other fuels (rhs) | ✓ | ✓ | ✓ | 过 |
| 28.5 | Single person with dependent children、Below 60%、2023 | Below 60%、Single person with dependent children、2023 | Right chart、Single person with dependent children、Below 60%、2023 | Right chart: share of population below/above the at-risk-of-poverty threshold unable to keep home adequately warm by household composition, 2021-2023, EU.、Single person with dependent children、Below 60%、2023 | ✓ | ✓ | ✓ | 过 |
| 23.5 | HH with dependent children、Below 60%、2023 | Below 60%、HH with dependent children、2023 | Right chart、HH without dependent children、Below 60%、2023 | Right chart: share of population below/above the at-risk-of-poverty threshold unable to keep home adequately warm by household composition, 2021-2023, EU.、HH with dependent children、Below 60%、2023 | ✓ | ✗ | ✓ | 过 |
| 9.5 | HH without dependent children、Above 60%、2023 | Above 60%、HH without dependent children、2023 | Right chart、HH with dependent children、Above 60%、2023 | Right chart: share of population below/above the at-risk-of-poverty threshold unable to keep home adequately warm by household composition, 2021-2023, EU.、HH without dependent children、Below 60%、2012 | ✓ | ✗ | ✗ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "compound" | "compound" | "other · heterogeneous panels" | compound · 同一图号下各面板类型不同 | 三家说的是同一件事：这一个图号下面的几个面板不是同一种图。gemini 直接写成 `other · heterogeneous panels`，opus 与 gpt 用了 compound。词表里 `heterogeneous_panel_types` 就是这一项，`ours` 为真。 |
| `type#f2` | "compound" | "compound" | "other · heterogeneous panels" | compound | 按类型表自己的定义判：`compound` 是<strong>同一个面板里出现两种以上图元形状</strong>，所以决定它的是三家自己在 `components` 里记的 `mixed_marks`，不是它们给这张图起的名字。三家都同时记了 `dual_axis` 与 `mixed_marks`，图元数都是 60。<strong>这是 P9 说的那种图</strong>：左右两套刻度加两种图元。 |
| `key_roles#f1` | ["category", "panel", "series"] | ["category", "panel", "series"] | ["panel", "series", "time"] | category × panel × series | opus 与 gpt 一致。横轴是 `1st quintile` `2nd quintile` 这样的分位组，是类目；gemini 把它读成时间轴。<strong>时间轴的判据</strong>：等距排开的年 / 月刻度记 `time`；长度不等的区间带（`2001-09` `2011-14`）虽然等距排开，是有序类目，记 `category`（与 `timevalue_p9` 同一条）。 |
