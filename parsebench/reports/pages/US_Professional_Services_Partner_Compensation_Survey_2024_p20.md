# US_Professional_Services_Partner_Compensation_Survey_2024_p20

![US_Professional_Services_Partner_Compensation_Survey_2024_p20](../../data/pages/US_Professional_Services_Partner_Compensation_Survey_2024_p20.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `US_Professional_Services_Partner_Compensation_Survey_2024_p20` | US_Professional_Services_Partner_Compensation_Survey_2024 | untagged | 5 | `parsebench/data/pages/US_Professional_Services_Partner_Compensation_Survey_2024_p20.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 两幅无编号的水平百分比堆叠条形图，各 4 行 × 3 段（共 12 段）。要能画：两级标题（上层 `Key external factors influencing outlook (%)` 只出现在第一幅之上，单位 `(%)` 只在这一行；每幅自带粗体副标题 `…by firm type` / `…by firm revenue`）；图例置于绘图区上方一行；完全没有数值轴、没有刻度、没有网格，条端一律右对齐到同一位置；数字全部印在段内右侧；类别标签可折行（`Management/` `advisory consulting`）；每幅下方各有 `Note:` 与 `Source: … n=142` 两行；左侧还有一栏与图并排的正文。
> 
> ## 定位一个值难在哪
> `34` 是第一幅 `Management/advisory consulting` 行的 Pessimistic 段。数字本身印着，读数不难；难在寻址：该类别名在页面上被拆成两行，两幅图的图例词完全相同（Pessimistic/Neutral/Optimistic），且都没有图号，要靠副标题里的 `by firm type` 才能与 `by firm revenue` 那幅区分。
> 
> ## 不确定的
> 上层 `(%)` 标题是否也管辖第二幅，无法从版面确定；无数值轴，段长与数值的对应只能相信印出的标签；`$1.00bn–$5.00bn` 中的连接符是 en dash 还是 hyphen，从渲染图难以断定。

**gpt-5.6-sol**

> **画出来要什么**
> 一幅两面板横向百分比堆叠条形图：每面板4类、每条3段，共24段。需重现共同标题、逐面板标题与图例、段内数值、重复的Note/Source，以及左侧并排正文。
> 
> **定位一个值难在哪**
> “83”要由“by firm revenue”面板、“$1.00bn–$5.00bn”和“Optimistic”共同定位。数值清晰印在段内，但页面没有表格结构。
> 
> **不确定的**
> 把共同标题下的两块图视为一幅两面板图。图上没有数值轴或刻度；百分比堆叠依据等宽条形、标题“(%)”及段值总和判断。

**gemini-3.1-pro**

> ### 画出来要什么
> 页面包含两个水平排列的百分比堆叠条形图。图表本身没有数值轴（X轴），所有的数值（如“34”、“28”）都直接以白色字体印刷在对应的彩色条形数据段内。所有数据段加起来代表100%，条形图的右边界是对齐的。图表标题位于绘图区上方，图例（Pessimistic, Neutral, Optimistic）位于标题和数据区之间。每个类别的标签（如“Strategy consulting”）排列在条形图的左侧。页面整体采用了两栏布局：左侧是与图表相关的结论性正文段落，右侧是图表，图表底部还带有“Note”和“Source”注释行。
> 
> ### 定位一个值难在哪
> 以第一张图表中“Management/advisory consulting”类别的“Pessimistic”占比“34”为例。该数值没有数值轴可以作为空间映射参考，解析器必须直接通过OCR识别色块内的文本。由于该类别的名称在页面上是换行显示的（“Management/”和“advisory consulting”分列两行），模型需要具备强大的空间结构理解能力，才能将这个浮在橙色块内部的数值与左侧换行的类别名称以及上方的图例颜色准确关联。一旦行对齐出错，数值就会分配给错误的组别。
> 
> ### 不确定的
> 第二张图表（by firm revenue）没有显式地在标题或图表中包含单位“%”，虽然可以通过第一张图的标题以及条形图的堆叠特性推断出单位是百分比，但在单看该图表时单位的归属并不直接明显。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 12 | — | above | all |
| opus-5 | f2 | stacked_bar | 12 | — | above | all |
| gpt-5.6-sol | f1 | stacked_bar | 24 | — | above | all |
| gemini-3.1-pro | f1 | stacked_bar | 12 | — | above | all |
| gemini-3.1-pro | f2 | stacked_bar | 12 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: 'Less than $1.00bn' etc. on the left, bars run to the right；gpt-5.6-sol: Categories appear left of segmented bars extending horizontally to the right.；gemini-3.1-pro: categories sit on the left axis and bars grow horizontally to the right |
| `legend_above_plot` | ✓ | ✓ | ✓ | opus-5: Legend row of three swatches drawn above 'Less than $1.00bn'；gpt-5.6-sol: Each Pessimistic, Neutral, Optimistic legend sits between its panel title and bars.；gemini-3.1-pro: legends sit directly between the title area and the first category bar |
| `multi_figure_page` | ✓ | — | ✓ | opus-5: Two charts, each with its own bold caption and its own Note/Source pair；gemini-3.1-pro: two distinct figures plotted independently with separate titles |
| `no_value_axis` | ✓ | ✓ | ✓ | opus-5: Nothing below the bars but the Note and Source lines; no ticks；gpt-5.6-sol: No numeric value ticks or value-axis line appears; segment values are printed.；gemini-3.1-pro: neither chart draws an axis with numeric ticks, just the categories |
| `panel_title_per_panel` | — | ✓ | — | gpt-5.6-sol: Panels are titled “by firm type” and “by firm revenue” above their respective plots. |
| `pct_stacked` | ✓ | ✓ | ✓ | opus-5: All four bars terminate at one common right edge; 18+21+61=100；gpt-5.6-sol: Stacks have equal width; segment labels total 100 or 101 under the rounding note.；gemini-3.1-pro: all bars span the same full width ending in a straight line at 100% |
| `per_panel_legend` | — | ✓ | — | gpt-5.6-sol: The full three-item legend is repeated separately above both panels. |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: Left column paragraphs 'By firm type, technology and IT firms...' run level with both charts；gpt-5.6-sol: Running explanatory text occupies a left column beside both chart panels.；gemini-3.1-pro: paragraphs of text run in a narrow column to the left of the figures |
| `small_multiples_4` | — | ✓ | — | gpt-5.6-sol: The same stacked-bar construction repeats in two panels, by firm type and firm revenue. |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: Same two small-print lines repeated under the second chart；gpt-5.6-sol: Each panel has “Note: Numbers may not sum to 100%, because of rounding.” and a Source line.；gemini-3.1-pro: Note: and Source: lines appear beneath each plot |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: Each revenue band row is one bar of three coloured segments；gpt-5.6-sol: Each horizontal bar is split into Pessimistic, Neutral, and Optimistic segments.；gemini-3.1-pro: segments for pessimistic, neutral, optimistic are stacked within each bar |
| `thin_segment_label` | ✓ | — | — | opus-5: '9' and '9' crammed into two very narrow segments at the left of the $1.00bn–$5.00bn bar |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: 'Key external factors influencing outlook (%)' is the only place the percent unit appears；gpt-5.6-sol: The common heading reads “Key external factors influencing outlook (%)”.；gemini-3.1-pro: the main title ends with (%) |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: '36', '38', '26' sit within the coloured segments of the last bar；gpt-5.6-sol: Every number is printed inside its coloured stacked-bar segment.；gemini-3.1-pro: numbers like 23, 36, 41 are printed on top of the bar segments |
| `wrapped_category_labels` | ✓ | ✓ | — | opus-5: 'Management/' and 'advisory consulting' set on two lines as one category；gpt-5.6-sol: “Management/advisory consulting” wraps onto two lines beside the upper plot. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `super_title_over_multiple_figures` | opus-5 | 3,4 | 'Key external factors influencing outlook (%)' heads both charts; only the second-level lines say 'by firm type' / 'by firm revenue' |
| `pct_stacked_without_any_axis` | opus-5 | 2 | Bars all reach one common right edge but no 0-100 scale or tick is drawn anywhere |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 34 | Management/advisory consulting、Pessimistic | Key external factors influencing outlook for current fiscal year, by firm type、Management/advisory consulting、Pessimistic | Key external factors influencing outlook for current fiscal year, by firm type、Management/advisory consulting、Pessimistic | Management/advisory consulting、Pessimistic | ✓ | ✓ | ✓ | 过 |
| 28 | Technology/IT consulting、Optimistic | Key external factors influencing outlook for current fiscal year, by firm type、Technology/IT consulting、Optimistic | Key external factors influencing outlook for current fiscal year, by firm type、Technology/IT consulting、Optimistic | Technology/IT consulting、Optimistic | ✓ | ✓ | ✓ | 过 |
| 83 | $1.00bn–$5.00bn、Optimistic | Key external factors influencing outlook for current fiscal year, by firm revenue、$1.00bn–$5.00bn、Optimistic | Key external factors influencing outlook for current fiscal year, by firm revenue、$1.00bn–$5.00bn、Optimistic | $1.00bn-$5.00bn、Optimistic | ✓ | ✓ | ✓ | 过 |
| 38 | More than $20.00bn、Neutral | Key external factors influencing outlook for current fiscal year, by firm revenue、More than $20.00bn、Neutral | Key external factors influencing outlook for current fiscal year, by firm revenue、More than $20.00bn、Neutral | More than $20.00bn、Neutral | ✓ | ✓ | ✓ | 过 |
| 31 | $5.01bn–$20.00bn、Pessimistic | Key external factors influencing outlook for current fiscal year, by firm revenue、$5.01bn–$20.00bn、Pessimistic | Key external factors influencing outlook for current fiscal year, by firm revenue、$5.01bn–$20.00bn、Pessimistic | $5.01bn-$20.00bn、Pessimistic | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `density#f1` | "≤20" | "21–60" | "≤20" | ≤20（按中位数 12 个图元） | 三家数出的图元个数是 12 / 24 / 12，中位数 12，落在 ≤20。三个数相差超过一半，取中位数所在的档；差异来自把叠在一起的图元数成一层还是两层。 |
| `hardest_step` | 3 | 1 | 1 | 未裁决 · 无实测证据 | 这一页 5 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 1 / 1 都无法证伪。 |
| `key_roles#f1` | ["category", "series"] | ["category", "panel", "series"] | ["category", "series"] | category × series | opus 与 gemini 都读成一个绘图区；gpt 读成两个面板并多记一段 panel。两家一致。 |
