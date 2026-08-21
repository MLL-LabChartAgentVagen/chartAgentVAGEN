# US_Professional_Services_Partner_Compensation_Survey_2024_p7

![US_Professional_Services_Partner_Compensation_Survey_2024_p7](../../data/pages/US_Professional_Services_Partner_Compensation_Survey_2024_p7.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `US_Professional_Services_Partner_Compensation_Survey_2024_p7` | US_Professional_Services_Partner_Compensation_Survey_2024 | untagged | 5 | `parsebench/data/pages/US_Professional_Services_Partner_Compensation_Survey_2024_p7.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 一个 10 行 × 4 列的条形矩阵：行是收入目标区间（`Less than $1.00m` … `Prefer not to answer`），列是四个分组（`Less than $1.00bn`…`More than $20.00bn`），每格一根向右的水平条，无数值轴、无刻度、无图例，数字全部印出——长条内白字（46、27、29），短条外黑字（5、3、2）。为 0 的格子只印 `0`，不画条。列首标题两行折行，颜色随列变化但不另表意。整页两张同构图（by firm size / by tenure at firm），共用上方标题 `Personal revenue targets (%)`，各自带 Note 与 Source 两行，左侧还有一栏正文。
> 
> **定位一个值难在哪**
> `13`：在 by firm size 图的 `$1.01bn–$5.00bn` 列里出现三次（`$1.00m–$3.00m`、`$10.01m–$15.00m`、`$15.01m–$20.00m`）。要唯一定位必须同时给出图小标题、行标签和折成两行的列标题；数字本身印在条旁，读数不难，难的是三层标签的绑定。`21`、`29` 同样跨两图重复。
> 
> **不确定的**
> `(%)` 是否管到第二张图（它只印在第一张之上）；列间的细竖线是分栏线还是每列的基线；无轴时条长与数值是否严格成比例。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 页面含两组无编号的横向条形矩阵；每组四个列面板，共享十个行标签。没有数值轴，百分比直接印在条内或条外；面板以不同颜色区分，图旁配说明文字，图下各有注释和来源。
> 
> **定位一个值难在哪**
> 
> 例如 13 必须同时落在“$1.01bn–$5.00bn”列和“$1.00m–$3.00m”行。该面板另有两个 13；数值虽清楚直印，若列标题、共享行名与单元格未保持关联，就会错配。
> 
> **不确定的**
> 
> 第二图未重复标出百分比单位，似乎承接上方“Personal revenue targets (%)”。零值只见数字、没有可见条形，因此 marks 未把零长度条计入。

**gemini-3.1-pro**

> ### 画出来要什么
> 页面包含两个图表，都采用了带有数据条的表格（或者说小多图形式的水平柱状图）布局。每个图表有一个共享的分类轴（位于左侧），右侧分为4个面板（列），代表不同的公司规模或任期。每个单元格内有一个水平柱子和对应的数值。图表没有绘制数值轴，数值直接标在柱子内部或外部，并且不同的面板使用不同的颜色。图表左侧有说明文字（侧边栏文本）。
> 
> ### 定位一个值难在哪
> 以"46"为例，它位于第一个图表的"Less than $1.00bn"列和"$1.00m-$3.00m"行的交叉处。定位它的主要难点在于解析器需要正确识别这种带有图形元素的表格结构。如果模型将其视为纯图表而未能输出带有行列表头的Markdown表格，则无法通过表格匹配来定位到该数值。
> 
> ### 不确定的
> 零值（如"0"）没有绘制任何图形，仅显示数字，不确定生成器是否能够处理这种条件渲染。图表颜色的选取似乎仅为了区分不同的列维度，没有额外的图例说明。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | bar | 32 | — | above | all |
| opus-5 | f2 | bar | 38 | — | above | all |
| gpt-5.6-sol | f1 | bar | 32 | — | above | all |
| gpt-5.6-sol | f2 | bar | 38 | — | above | all |
| gemini-3.1-pro | f1 | bar | 40 | — | above | all |
| gemini-3.1-pro | f2 | bar | 40 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: rows '$1.00m–$3.00m' etc. with bars extending right inside each tenure column；gpt-5.6-sol: Bars extend rightward within each tenure column.；gemini-3.1-pro: bars grow to the right from the categories |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: two captioned charts each with its own Note and Source lines, separated by a rule；gpt-5.6-sol: Two separately titled chart blocks each carry their own note and source lines.；gemini-3.1-pro: two distinct chart blocks with their own titles |
| `no_value_axis` | ✓ | ✓ | ✓ | opus-5: bars sit on bare vertical rules; no tick labels anywhere below or above the bars；gpt-5.6-sol: No value ticks are drawn; percentages are supplied by printed labels.；gemini-3.1-pro: no value axis ticks or lines are drawn, only printed labels |
| `panel_title_per_panel` | ✓ | ✓ | ✓ | opus-5: 'Less than\n3 years' and 'More than\n10 years' set above their own columns；gpt-5.6-sol: Each column has a tenure heading, from “Less than 3 years” to “More than 10 years”.；gemini-3.1-pro: column headers like Less than $1.00bn sit over each panel |
| `shared_axis` | ✓ | ✓ | ✓ | opus-5: row labels 'Less than $1.00m'…'Prefer not to answer' drawn once for four columns；gpt-5.6-sol: The category labels are printed once at left for all four tenure panels.；gemini-3.1-pro: categories listed once on the left for all four panels |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: left column reads 'By firm size, we saw a correlation between personal revenue targets and firm size...'；gpt-5.6-sol: A prose column beginning “We also saw a positive correlation” sits beside the chart.；gemini-3.1-pro: body text runs in a column alongside the figures |
| `small_multiples_4` | ✓ | ✓ | ✓ | opus-5: four columns headed 'Less than 3 years', '3–5 years', '6–10 years', 'More than 10 years'；gpt-5.6-sol: Four tenure columns repeat the same ten revenue-target rows.；gemini-3.1-pro: four columns of bars partitioned by firm size |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: same two-line Note and Source block printed under the tenure chart；gpt-5.6-sol: A note and “Source: Heidrick & Struggles” line appear beneath the plot.；gemini-3.1-pro: Note: Numbers may not sum to 100%... Source: Heidrick... |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: 'Personal revenue targets (%)' is the only place the percent scale is stated；gpt-5.6-sol: The heading reads “Personal revenue targets (%)”.；gemini-3.1-pro: (%) is printed in the figure title |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: '27', '14', '22', '24', '29' printed inside the coloured bars；gpt-5.6-sol: Values such as 27 and 29 are printed inside longer bars.；gemini-3.1-pro: 46 is printed inside the dark blue bar |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: '5', '2', '3' printed beside short bars, outside the mark；gpt-5.6-sol: Values such as 2 are printed outside narrow bars.；gemini-3.1-pro: 5 is printed to the right of a short bar |
| `vgrid_only` | ✓ | — | — | opus-5: four faint vertical rules separate the tenure columns; no horizontal rules in the plot |
| `wrapped_category_labels` | ✓ | — | — | opus-5: column headers wrap onto two lines: 'Less than' / '$1.00bn'; ten row labels stack down the left |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `crosstab_bar_matrix` | opus-5 | 1,3 | 10 row labels by 4 headed columns, one single bar per cell, no legend and no value axis |
| `zero_printed_without_mark` | opus-5 | 2,3 | '0' printed at the baseline for '$10.01m–$15.00m' under 'Less than $1.00bn' with no bar drawn |
| `shared_title_over_two_figures` | opus-5 | 3,4 | 'Personal revenue targets (%)' sits above both bold sub-headings and supplies the unit for both |
| `column_colour_matches_panel` | opus-5 | 3 | navy, cyan, teal and grey fills correspond one-to-one with the four column headers; no legend |
| `bar_matrix` | gpt-5.6-sol | 1,3 | Four panel columns share ten row labels, with one labeled horizontal-bar cell at each intersection. |
| `bar_matrix` | gpt-5.6-sol | 1,3 | Four tenure columns form a matrix against one shared set of revenue-target rows. |
| `printed_zero_without_bar` | gpt-5.6-sol | 2,3 | Several cells print “0” at the baseline without a visible bar. |
| `printed_zero_without_bar` | gpt-5.6-sol | 2,3 | The first 6–10 years cell and final More than 10 years cell print “0” without bars. |
| `data_bars_in_table` | gemini-3.1-pro | 1 | bars are drawn inside the columns of a table structure |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 46 | $1.00m–$3.00m、Less than $1.00bn | Personal revenue targets, by firm size、$1.00m–$3.00m、Less than $1.00bn | Less than $1.00bn、$1.00m–$3.00m | Less than $1.00bn、$1.00m-$3.00m | ✓ | ✓ | ✓ | 过 |
| 13 | $1.00m–$3.00m、$1.01bn–$5.00bn | Personal revenue targets, by firm size、$1.00m–$3.00m、$1.01bn–$5.00bn | $1.01bn–$5.00bn、$1.00m–$3.00m | $1.01bn-$5.00bn、$1.00m-$3.00m | ✓ | ✓ | ✓ | 过 |
| 27 | $1.00m–$3.00m、Less than 3 years | Personal revenue targets, by tenure at firm、$1.00m–$3.00m、Less than 3 years | Less than 3 years、$1.00m–$3.00m | Less than 3 years、$1.00m-$3.00m | ✓ | ✓ | ✓ | 过 |
| 21 | $6.01m–$10.00m、3–5 years | Personal revenue targets, by firm size、$6.01m–$10.00m、More than $20.00bn | 3–5 years、$6.01m–$10.00m | 3-5 years、$6.01m-$10.00m | ✗ | ✓ | ✓ | 过 |
| 29 | More than $30.00m、More than 10 years | Personal revenue targets, by tenure at firm、More than $30.00m、More than 10 years | More than 10 years、More than $30.00m | More than 10 years、More than $30.00m | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 3 | 3 | 1 | 未裁决 · 无实测证据 | 这一页 5 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 3 / 1 都无法证伪。 |
