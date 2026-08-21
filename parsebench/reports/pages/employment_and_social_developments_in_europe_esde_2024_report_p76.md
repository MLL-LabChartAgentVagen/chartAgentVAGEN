# employment_and_social_developments_in_europe_esde_2024_report_p76

![employment_and_social_developments_in_europe_esde_2024_report_p76](../../data/pages/employment_and_social_developments_in_europe_esde_2024_report_p76.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `employment_and_social_developments_in_europe_esde_2024_report_p76` | employment_and_social_developments_in_europe_esde_2024_report | need_estimate | 10 | `parsebench/data/pages/employment_and_social_developments_in_europe_esde_2024_report_p76.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 两幅独立编号图。Chart 3.4 是 11 年份的堆叠柱（Pre-primary and primary / Secondary / Tertiary），y 轴 0%–100%、虚线水平网格，但堆叠总高只到约 87%，不是百分百堆叠；图例在图下一行。Chart 3.5 是双值轴混合图：深蓝柱读左轴 470–500，绿线读右轴 0–9，图例分两行且名称里自带 “(left axis)”“(right axis)”。两图都有 “Chart 3.x” 编号行、蓝色标题行、灰色副标题（含单位与年份范围）、Note/Source 与 “Click here to download chart.” 链接行。
> 
> **定位一个值难在哪**
> 
> 取 474：它是 Chart 3.5 中 2022 的深蓝柱，柱顶落在 470 与 480 之间偏低处，刻度间距 10、容差约 ±24，读数不难；难在必须声明它读的是左轴而非右轴——同一像素高度在右轴上约是 1.2。而值 1（右轴绿线终点附近）与值 7（右轴上无刻度，只有 0/3/6/9）都要求把“哪条轴、哪种标记”写进键。
> 
> **不确定的**
> 
> Chart 3.4 各段无数值标注，31.5/39.0/17.5 等只能按 20% 网格估读；堆叠顶部 87% 的缺口对应 Note 里列出的其它类别，图上无标记。绿线是否只有 4 个数据点无法完全确认。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 页面含两个独立图。Chart 3.4 是11年、3系列的非满额百分比堆叠柱，百分号直接写在刻度中。Chart 3.5 将柱和无点标记折线叠加，并配置470–500左轴与0–9右轴。两图均需标题分层、水平虚线网格、图下图例、注释、来源和下载链接。
> 
> **定位一个值难在哪**
> 
> Chart 3.4 的2012年“Tertiary”值17.5未印出；其5%容差仅0.875个百分点，而纵轴每格20个百分点，还须读取堆叠段上下边界。
> 
> **不确定的**
> 
> Chart 3.5 的折线没有点标记，7只能按2012位置和右轴估读。给定值1未见对应数据标记；页面仅在注释中出现“1 000”。

**gemini-3.1-pro**

> ### 画出来要什么
> 需要能够绘制常规的堆叠柱状图（图3.4），以及结合了柱状图与折线图的双Y轴混合图表（图3.5）。生成器应当能够处理非零起点的坐标轴（如左轴从470开始），并按需只绘制水平网格线。此外，还需要支持在图例内部直接通过文字声明系列所属的坐标轴（如“(left axis)”），并在图表外部的数据来源下方附加带下划线的功能性下载链接文本。
> 
> ### 定位一个值难在哪
> 页面所有图表均未直接打印具体数值。以图3.4中的 `17.5` 为例，这是一个位于上层的堆叠柱段（对应2014年Tertiary类别），定位后读者必须分别向左平视估算该段顶部和底部在Y轴上的绝对位置（约87.5%和70%），再进行相减得出结论。由于Y轴的主刻度步长高达20%且完全没有次级刻度线，加上堆叠带来的累计误差，要在这样的图表中实现5%以内的读取精度是极其困难的。
> 
> ### 不确定的
> 图3.4的Y轴最高刻度带有“%”单位符号，但各年份柱子的累加总高度均维持在85%左右，并未达到100%，页面中虽然有注释提到其他分类未包含，但并未在图上直观体现。此外，提取清单中给定的数值 `1` 在页面的任何图表、坐标轴刻度及明显正文中均无法找到，判定为无效或无法溯源的值。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 33 | Chart 3.4 | above | none |
| opus-5 | f2 | compound | 8 | Chart 3.5 | above | none |
| gpt-5.6-sol | f1 | stacked_bar | 33 | Chart 3.4 | above | none |
| gpt-5.6-sol | f2 | compound | 8 | Chart 3.5 | above | none |
| gemini-3.1-pro | f1 | stacked_bar | 33 | Chart 3.4 | above | none |
| gemini-3.1-pro | f2 | other · bar and line | 8 | Chart 3.5 | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_starts_above_zero` | ✓ | ✓ | ✓ | opus-5: left value axis lowest tick is 470, bars cut off below it；gpt-5.6-sol: The left bar axis begins at 470 without a break glyph.；gemini-3.1-pro: left y-axis of Chart 3.5 begins at 470, not zero |
| `data_link_below_figure` | ✓ | ✓ | ✓ | opus-5: 'Click here to download chart.' under the note and source lines；gpt-5.6-sol: “Click here to download chart.” appears under the source.；gemini-3.1-pro: 'Click here to download chart.' links appear beneath the source text |
| `dual_axis` | ✓ | ✓ | ✓ | opus-5: left ticks 470-500 for bars, right ticks 0-9 for the green line；gpt-5.6-sol: Left ticks run 470–500 while right ticks run 0–9.；gemini-3.1-pro: Chart 3.5 has axes from 470-500 on left and 0-9 on right |
| `footnote_marker` | ✓ | — | — | opus-5: body text '(Chart 3.5). (157)' superscript footnote marker before the chart |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: dotted horizontal rules at 470,480,490,500 across the panel；gpt-5.6-sol: Dashed horizontal grid lines are drawn at left-axis ticks only.；gemini-3.1-pro: horizontal dashed lines guide values, with no vertical gridlines present |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: two legend lines under the plot: 'PISA average score (left axis)'；gpt-5.6-sol: Both series labels are centred beneath the plot.；gemini-3.1-pro: legends are placed beneath the x-axis on both charts |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: four dark blue bars with a green line drawn across the same panel；gpt-5.6-sol: Four blue bars and one green line occupy the same panel.；gemini-3.1-pro: Chart 3.5 displays a line series plotted over a bar series |
| `multi_figure_page` | ✓ | ✓ | — | opus-5: 'Chart 3.4' and 'Chart 3.5' each with own title, note and source；gpt-5.6-sol: “Chart 3.4” and “Chart 3.5” head separate charts. |
| `right_side_y_axis` | ✓ | — | — | opus-5: a second value axis 0,3,6,9 drawn on the right edge of the plot |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Source: OECD PISA data for 2012, 2015, 2018, 2022.'；gpt-5.6-sol: “Note:” and “Source: OECD PISA data for 2012, 2015, 2018, 2022” appear below.；gemini-3.1-pro: Note: and Source: lines printed below the plot areas on both charts |
| `sparse_time_ticks` | ✓ | — | — | opus-5: x ticks only 2012, 2015, 2018, 2022 for a 2012-2022 span |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: three colour segments stacked inside each yearly bar, 2012 to 2022；gpt-5.6-sol: Each yearly bar contains blue, green, and yellow vertical segments.；gemini-3.1-pro: Chart 3.4 uses color-coded segments stacked vertically within each yearly bar |
| `unit_in_axis_or_title` | ✓ | — | — | opus-5: subtitle 'Weighted average EU share of government expenditure on education, by education level' |
| `unit_in_series_name` | ✓ | — | — | opus-5: legend reads 'PISA average score (left axis)' and 'PISA efficiency score (right axis)' |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `stack_below_full_height` | opus-5 | 2,4 | stacks top out near 87% on a 0-100% axis; Note lists the omitted categories |
| `axis_label_percent_suffix` | opus-5 | 2 | ticks printed '0%','20%'...'100%' with percent sign on every tick |
| `legend_entry_names_its_axis` | opus-5 | 3 | '(left axis)' / '(right axis)' inside legend text disambiguates the two value scales |
| `percent_formatted_value_ticks` | gpt-5.6-sol | 2 | The value ticks read “0%, 20%, 40%, 60%, 80%, 100%” without an axis title. |
| `line_without_point_markers` | gpt-5.6-sol | 2 | The green line connects four years without visible point symbols. |
| `axis_indicator_in_series_name` | gemini-3.1-pro | 3 | Chart 3.5 legend series explicitly state '(left axis)' and '(right axis)' |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 31.5 | 2012、Pre-primary and primary | 2012、Pre-primary and primary | 2012、Pre–primary and primary | 2012、Pre-primary and primary | ✓ | ✓ | ✓ | 过 |
| 39.0 | 2012、Secondary | 2012、Secondary | 2012、Secondary | 2012、Secondary | ✓ | ✓ | ✓ | 过 |
| 17.5 | 2012、Tertiary | 2012、Tertiary | 2012、Tertiary | 2014、Tertiary | ✓ | ✓ | ✗ | 过 |
| 34.0 | 2022、Pre-primary and primary | 2022、Pre-primary and primary | 2022、Pre–primary and primary | 2022、Pre-primary and primary | ✓ | ✓ | ✓ | 过 |
| 37.0 | 2022、Secondary | 2022、Secondary | 2022、Secondary | 2019、Secondary | ✓ | ✓ | ✗ | 过 |
| 17.0 | 2022、Tertiary | 2022、Tertiary | 2022、Tertiary | 2022、Tertiary | ✓ | ✓ | ✓ | 没过 |
| 492 | 2012、PISA average score (left axis) | 2012、PISA average score (left axis) | 2012、PISA average score (left axis) | 2012、PISA average score (left axis) | ✓ | ✓ | ✓ | 过 |
| 474 | 2022、PISA average score (left axis) | 2022、PISA average score (left axis) | 2022、PISA average score (left axis) | 2022、PISA average score (left axis) | ✓ | ✓ | ✓ | 过 |
| 7 | 2012、PISA efficiency score (right axis) | 2012、PISA efficiency score (right axis) | 2012、PISA efficiency score (right axis) | 2018、PISA efficiency score (right axis) | ✓ | ✓ | ✗ | 过 |
| 1 | 2022、PISA efficiency score (right axis) | not_found | not_found | not_found | ✗ | ✗ | ✗ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f2` | "compound" | "compound" | "other · bar and line" | compound | 按类型表自己的定义判：`compound` 是<strong>同一个面板里出现两种以上图元形状</strong>，所以决定它的是三家自己在 `components` 里记的 `mixed_marks`，不是它们给这张图起的名字。三家都记了 `dual_axis` 与 `mixed_marks`，图元数都是 8。gemini 写的 `other · bar and line` 就是 compound。 |
