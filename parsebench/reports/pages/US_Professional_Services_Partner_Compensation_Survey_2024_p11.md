# US_Professional_Services_Partner_Compensation_Survey_2024_p11

![US_Professional_Services_Partner_Compensation_Survey_2024_p11](../../data/pages/US_Professional_Services_Partner_Compensation_Survey_2024_p11.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `US_Professional_Services_Partner_Compensation_Survey_2024_p11` | US_Professional_Services_Partner_Compensation_Survey_2024 | untagged | 5 | `parsebench/data/pages/US_Professional_Services_Partner_Compensation_Survey_2024_p11.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 一张横向分组条形图：6 个类别（Significantly lower … Prefer not to answer），每类两根条（2024 深蓝、2022 青色），图例在图上方一行。没有数值轴、没有刻度、没有网格，只有类别之间的浅色分隔横线；每根条右端印数字（长条为内侧白字，短条如 `1` 为外侧黑字）。标题分两层：`Partner turnover (%)` 与一整句问题式副标题。左侧另有一栏正文 `Partner turnover`，与图并排。图下两行小字 Note / Source。
> 
> **定位一个值难在哪**
> 
> 取 `6`：它在图上出现两次——`Significantly higher` 的 2022 条与 `Prefer not to answer` 的 2022 条。只有同时给出类别名与图例年份（`2022`）才能唯一定位；若解析器只输出「6」和一个类别名，就会指错行。数值本身是印刷的，读数不成问题。
> 
> **不确定的**
> 
> 图无编号，`Figure` 字样是否在别处出现无法判断；条长与数字是否严格成比例（无轴可校验）；`1` 那根深蓝条极短，是否还有更细的描边或标记无法看清。

**gpt-5.6-sol**

> ### 画出来要什么
> 需绘制单面板横向分组条形图：六个回答类别、2024与2022两个系列、十二个条形；全部数值直接标注，图例位于图上方。图旁还要并排放置“Partner turnover”说明文字，图下保留Note与Source。
> 
> ### 定位一个值难在哪
> “14”和“6”都各出现两次，单凭数值无法定位。例如目标“14”须同时写明“Lower”和“2022”，而不能只依赖颜色或数值。
> 
> ### 不确定的
> 图中没有数值轴、刻度或明确单位轴，只能依据标题中的“(%)”和条上标签判断。重复值按自上而下的首次出现对应抽查项。

**gemini-3.1-pro**

> ### 画出来要什么
> 要生成此页面，图表生成器需要支持水平分组条形图（horizontal grouped bars），并且能够完全移除数值轴（无刻度、无轴线），仅通过直接在条形上打印数据标签来展示数值。数据标签需要根据条形长度自适应位置：大部分标签位于条形内部右侧，但像“1”这样的极小值必须放置在条形外部。分类轴需要水平网格线（hgrid）分隔不同类别。
> 
> 在页面排版层面，需要支持将大段描述性文本与图表本体左右并排显示（side_text_bullets）。图表的标题模块需支持多行长句作为副标题，且图例放置在副标题与绘图区之间。
> 
> ### 定位一个值难在哪
> 以“35”为例，该图表完全没有任何数值轴作为参考，数值提取高度依赖于直接打印在条形上的标签。定位这个值要求解析器能够准确识别水平分组的条形组，并将其与上方的图例（2024）和左侧的长文本类别（Higher）进行精确的空间关联。由于标签位置不一（内/外），若解析器对相对位置判断存在偏差，容易将数值张冠李戴。
> 
> ### 不确定的
> 图例中“深蓝色”和“青蓝色”是否带有某种特定的品牌视觉规范映射，或是仅用作年份的随意区分，在当前上下文中无法确定。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | grouped_bar | 12 | — | above | all |
| opus-5 | f2 | unreadable | 0 | — | beside | none |
| gpt-5.6-sol | f1 | grouped_bar | 12 | — | above | all |
| gemini-3.1-pro | f1 | grouped_bar | 12 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: two bars per row, dark 2024 above light 2022, in each category slot；gpt-5.6-sol: Two bars, labelled “2024” and “2022”, appear side by side in every category.；gemini-3.1-pro: two bars for 2024 and 2022 sit side by side per category |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: thin horizontal rules separate each category row; no vertical rules；gpt-5.6-sol: Thin horizontal rules separate category rows; no vertical grid lines are drawn.；gemini-3.1-pro: horizontal lines separate the categories, with no vertical grid lines |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: category names on the left, bars grow rightward from a common left edge；gpt-5.6-sol: Category labels sit left while all bars extend horizontally to the right.；gemini-3.1-pro: categories sit on the y axis and the bars grow to the right |
| `legend_above_plot` | ✓ | ✓ | ✓ | opus-5: '2024' and '2022' swatches sit between the question subtitle and the first bar row；gpt-5.6-sol: The “2024” and “2022” legend sits between the question and the bars.；gemini-3.1-pro: the legend sits below the subtitle and above the plot area |
| `no_value_axis` | ✓ | ✓ | ✓ | opus-5: no ticks or numbers along any value axis; only printed labels give the numbers；gpt-5.6-sol: No numerical value-axis ticks are drawn; values are readable only from bar labels.；gemini-3.1-pro: there is no value axis or ticks drawn at the bottom or top |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: left column 'Partner turnover' plus paragraph runs level with the chart；gpt-5.6-sol: A “Partner turnover” prose column runs beside the chart in the same horizontal band.；gemini-3.1-pro: a column of text describing partner turnover runs left of the figure |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: Numbers may not sum to 100%, because of rounding.' and 'Source: Heidrick & Struggles US ... n=144'；gpt-5.6-sol: “Note: Numbers may not sum to 100%, because of rounding.” and “Source:” appear below.；gemini-3.1-pro: Note and Source text sit beneath the plot area |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: title reads 'Partner turnover (%)'; no unit appears anywhere on the plot；gpt-5.6-sol: The chart title reads “Partner turnover (%)”.；gemini-3.1-pro: the title includes the unit (%) |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: '27', '35', '45' printed in white at the right end inside the bars；gpt-5.6-sol: Labels including “9”, “27”, “35” and “45” are printed inside their bars.；gemini-3.1-pro: values like 9, 13, 27 are printed inside the bar segments |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: '1' printed in black just right of the very short dark 2024 bar；gpt-5.6-sol: The “1” label is printed just beyond the short 2024 bar.；gemini-3.1-pro: the value 1 is printed just outside its very short bar |
| `wrapped_category_labels` | ✓ | — | — | opus-5: long labels 'Significantly higher', 'Prefer not to answer' stacked down the left |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `unit_in_title_parenthetical` | opus-5 | 3,4 | 'Partner turnover (%)' — unit carried as a parenthetical suffix on the title line |
| `question_as_subtitle` | opus-5 | 4 | bold survey question 'In your most recent fiscal year, how much partner turnover...' set as the second heading line |
| `unnumbered_figure` | opus-5 | 3,4 | no 'Figure n' anywhere; the chart is identified only by its title |
| `row_separator_rules` | opus-5 | — | a light horizontal rule drawn between each category group rather than gridlines |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 9 | Significantly lower、2024 | Significantly lower、2024 | Significantly lower、2024 | Significantly lower、2024 | ✓ | ✓ | ✓ | 过 |
| 14 | Lower、2022 | Lower、2022 | Lower、2022 | Lower、2022 | ✓ | ✓ | ✓ | 过 |
| 27 | About the same、2024 | About the same、2024 | About the same、2024 | About the same、2024 | ✓ | ✓ | ✓ | 过 |
| 35 | Higher、2024 | Higher、2024 | Higher、2024 | Higher、2024 | ✓ | ✓ | ✓ | 过 |
| 6 | Significantly higher、2022 | Significantly higher、2022 | Significantly higher、2022 | Prefer not to answer、2022 | ✓ | ✓ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
