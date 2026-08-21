# investing-in-education-2025-NC0125093ENN-1_p14

![investing-in-education-2025-NC0125093ENN-1_p14](../../data/pages/investing-in-education-2025-NC0125093ENN-1_p14.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `investing-in-education-2025-NC0125093ENN-1_p14` | investing-in-education-2025-NC0125093ENN-1 | need_estimate | 10 | `parsebench/data/pages/investing-in-education-2025-NC0125093ENN-1_p14.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 本页要同时产出两类东西。图6是折线图：紫色 Nominal 与红色 Real 两条带点折线，17 个年份（2007–2023），Y 轴只印 100/110/…/160（起点非零、无单位词），刻度线为虚线横向网格，图例在绘图区下方，标题写在整幅宽的紫色反白横幅里，单位 “(index 2007=100)” 藏在标题括号内，下方另有 Notes 与 Source 两行小字（含 COFOG、AMECO 超链接）。图7实为一张“当作图来编号”的表：6 列（2019–2023 各列的表头分两行“2019”/“% of total”，末列橙底“2019-2023 / percentage point change”），10 行功能分类，含负值 -0.1/-0.3/-1.9，行底纹交替。
> 
> **定位一个值难在哪**
> 以 159（Nominal 2023）为例：图上无任何数值标签，只能按像素在 150 与 160 两条虚线之间读；网格间距 10，5% 容差在此约 ±8，尚可，但同法读 105 时，Real 2015 与 2016 相差不到 1 个单位，容差 ±5 反而无法确定它属于哪一年，行键就可能错配。
> 
> **不确定的**
> 各折线点的精确取值全靠目测；105、110 归属年份为推断。图7末列表头配色是否表示“强调”，以及 Online data code 链接算 Source 还是数据链接，无法确证。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 页面包含两种独立构造：图6是双系列带圆点折线图，横轴为2007—2023年，纵轴从100起，只有水平虚线网格，图例置于图下；图7是带两层列头、混合单位及交替底色的编号数据表。两图均有紫色标题条和下方来源文字。
> 
> **定位一个值难在哪**
> 
> 图6的“2023—Nominal—159”没有印数值，只能从略低于160刻度的点估读。一个值需要同时关联年份轴标签和图例系列名。
> 
> **不确定的**
> 
> 图6标题中的换行看似仅由版宽造成，因此未视为独立副标题。折线上的全部目标值均按刻度位置判断，页面未给出精确标签。

**gemini-3.1-pro**

> ### 画出来要什么
> 页面包含一个折线图（Figure 6）和一个数据表（Figure 7）。折线图需要绘制两条带标记点的实线，X轴为连续年份，Y轴从100起始，仅有水平虚线网格，图例位于图表底部；图表标题位于带底色的横幅中。表格需要呈现跨列和行列交错的结构，表头和行背景交替渲染颜色。两图底部均需支持添加多行的来源和注释说明，且表格下方附带带方括号的超链接代码。
> 
> ### 定位一个值难在哪
> 以2019年Real线的“109”为例，该值未在图表上直接标注，必须通过折线上的散点与间距为10的Y轴水平对齐来估算。尽管5%的容差范围较宽，但连续17年的长周期折线图极易导致解析模型在提取数据时出现遗漏或年份对齐错误。
> 
> ### 不确定的
> 折线图所有具体数值均无标签，完全依赖视觉刻度估算；表格中2019-2021年表头单元格左上角的微小绿色三角形缺乏图例说明，暂视为装饰元素处理。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 34 | Figure 6. | above | none |
| opus-5 | f2 | other · data table | 60 | Figure 7. | above | all |
| gpt-5.6-sol | f1 | line | 34 | Figure 6. | above | none |
| gpt-5.6-sol | f2 | other · data table | 60 | Figure 7. | above | all |
| gemini-3.1-pro | f1 | line | 34 | Figure 6. | above | none |
| gemini-3.1-pro | f2 | unreadable | 60 | Figure 7. | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_starts_above_zero` | ✓ | ✓ | ✓ | opus-5: lowest y tick printed is 100, no break glyph drawn on the axis；gpt-5.6-sol: The lowest y-axis tick is 100; no break glyph is drawn.；gemini-3.1-pro: the y-axis starts at 100 with no break symbol |
| `data_link_below_figure` | ✓ | — | ✓ | opus-5: 'Online data code: [gov_10a_exp]' underlined hyperlink on the line under the table；gemini-3.1-pro: under Figure 7 reads 'Online data code: [gov_10a_exp]' |
| `data_table_as_figure` | ✓ | ✓ | ✓ | opus-5: bordered grid of rows and year columns carrying the caption 'Figure 7. Public expenditure by function'；gpt-5.6-sol: “Figure 7.” captions a bordered table of functions, years and printed values.；gemini-3.1-pro: Figure 7 is a bordered data table with rows and columns |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: dashed horizontal rules at 100,110...160; no vertical rules in the plot；gpt-5.6-sol: Dashed horizontal grid lines cross the plot; no vertical grid lines appear.；gemini-3.1-pro: horizontal dashed lines at 10-unit intervals, no vertical lines |
| `highlighted_category` | ✓ | — | — | opus-5: '2019-2023 percentage point change' header cell filled orange while year headers are red |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'Nominal' and 'Real' swatch row drawn below the 2007-2023 tick row；gpt-5.6-sol: The “Nominal” and “Real” legend is centred beneath the x axis.；gemini-3.1-pro: the legend sits below the x-axis |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: Two banner captions: 'Figure 6. Evolution of nominal and real...' and 'Figure 7. Public expenditure by function (2019-2023)'；gpt-5.6-sol: Separate captions “Figure 6.” and “Figure 7.” introduce independent figures.；gemini-3.1-pro: the page contains Figure 6 and Figure 7 |
| `negative_values` | ✓ | — | — | opus-5: '-0.1', '-0.3', '-0.4', '-1.9' printed in the 2019-2023 percentage point change column |
| `rebased_index_values` | ✓ | ✓ | ✓ | opus-5: title ends '(index 2007=100)' and both lines start at 100 in 2007；gpt-5.6-sol: The title states “index 2007=100”.；gemini-3.1-pro: the title says '(index 2007=100)' |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Source: Eurostat COFOG data. Online data code: [gov_10a_exp].' under the table；gpt-5.6-sol: “Source: Eurostat COFOG data. Online data code: [gov_10a_exp].” appears below the table.；gemini-3.1-pro: Notes: and Source: lines printed under both figures |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: y ticks read bare '100'...'160'; scale word only in title '(index 2007=100)'；gpt-5.6-sol: The title ends with “(index 2007=100)”.；gemini-3.1-pro: the title contains '(index 2007=100)' |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `banner_caption_bar` | opus-5 | 3,4 | Both captions set white on a filled purple bar spanning the full text column above the plot |
| `unit_in_column_subheader` | opus-5 | 3 | Each year header carries a second line '% of total' below '2019', '2020', ... |
| `derived_change_column` | opus-5 | 3 | Last column '2019-2023 percentage point change' is computed from the 2019 and 2023 columns |
| `alternating_row_shading` | opus-5 | — | Rows alternate lilac and white fill down the ten function rows |
| `markers_on_every_line_point` | opus-5 | 2 | Round markers drawn at each of the 17 yearly points on both Nominal and Real lines |
| `multi_level_table_header` | gpt-5.6-sol | 3 | Column headers pair “2019” with “% of total”; the final column says “percentage point change” beneath “2019-2023”. |
| `alternating_row_shading` | gpt-5.6-sol | — | Table rows alternate lavender and white fills. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 100 | 2007、Nominal | Nominal、2007 | 2007、Nominal | Nominal、2007 | ✓ | ✓ | ✓ | 过 |
| 100 | 2007、Real | Real、2007 | 2007、Real | Real、2007 | ✓ | ✓ | ✓ | 过 |
| 110 | 2010、Nominal | Nominal、2010 | 2010、Nominal | Nominal、2011 | ✓ | ✓ | ✗ | 过 |
| 116 | 2015、Nominal | Nominal、2015 | 2015、Nominal | Nominal、2015 | ✓ | ✓ | ✓ | 过 |
| 105 | 2015、Real | Real、2016 | 2015、Real | Real、2015 | ✗ | ✓ | ✓ | 过 |
| 130 | 2019、Nominal | Nominal、2019 | 2019、Nominal | Nominal、2019 | ✓ | ✓ | ✓ | 过 |
| 109 | 2019、Real | Real、2019 | 2019、Real | Real、2019 | ✓ | ✓ | ✓ | 过 |
| 148 | 2022、Nominal | Nominal、2022 | 2022、Nominal | Nominal、2022 | ✓ | ✓ | ✓ | 过 |
| 159 | 2023、Nominal | Nominal、2023 | 2023、Nominal | Nominal、2023 | ✓ | ✓ | ✓ | 过 |
| 115 | 2023、Real | Real、2023 | 2023、Real | Real、2023 | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 2 | 2 | 1 | 未裁决 · 无实测证据 | 这一页 10 个抽查点全过，运行没有在任何一步卡住，三家的 2 / 2 / 1 都无法证伪。 |
| `key_roles#f2` | ["category", "series"] | ["category", "time"] | null | category × time | f2 是 Figure 7：一张带图号与紫色标题条的**表格型图**。行是公共支出职能（类目），列是 2019–2023 的年份（时间）加一列区间变化。opus 记的 series 指的是同一批列，但那些列就是年份，记 time 更准；gemini 只报了一张图，漏了 Figure 7。 |
