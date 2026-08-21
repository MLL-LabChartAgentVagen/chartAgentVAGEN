# (Web_version)_E-Government_Survey_2024_1392024_p177

![(Web_version)_E-Government_Survey_2024_1392024_p177](../../data/pages/(Web_version)_E-Government_Survey_2024_1392024_p177.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `(Web_version)_E-Government_Survey_2024_1392024_p177` | (Web_version)_E-Government_Survey_2024_1392024 | untagged | 5 | `parsebench/data/pages/(Web_version)_E-Government_Survey_2024_1392024_p177.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 一张横向分组条形图（`Figure 4.15 LOSI indicators as a proxy for progress towards smart city development`），4 个指标类别 × 2 个系列（2022 蓝、2024 橙），共 8 根条。类别轴在左侧，文字长且需换行/挤压（`Actual or intended use of emergent technologies`）；值轴在下方，刻度 `0%`—`60%`，每 10% 一格，只有竖向网格线。图例横排在图下方、值轴之下。每根条右端都印有百分比（`46%`、`49%`），标签在条形外侧。标题为蓝色，下方带一条蓝色横条装饰。整图外框为细线矩形。
> 
> **定位一个值难在哪**
> 
> `49%` 只需两个标签：`Existence of smart city initiatives` + `2024`。但 `2024` 只在图例中以色块+文字出现，条本身无文字；蓝橙两条同宽同槽，表格若只写 `49%` 而丢掉年份，就会与 `46%` 混淆。类别名很长，解析器常截断成 `Existence of smart city…`，使标签不再逐字匹配。
> 
> **不确定的**
> 
> 图下没有 Source/Note 行，未知数据来源；不确定 33% 出现两次（emergent technologies 与 data policy online）时解析器能否分辨；类别轴文字是否真为两行换行，从渲染看是单行。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 一个带蓝色标题和横线的单面板横向分组条形图：4个类别、2022与2024两组、共8条。底轴为0%–60%，仅有竖向网格线；数值全部置于条形末端外侧，图例位于绘图区下方，整体有黑色细框。
> 
> **定位一个值难在哪**
> 
> 顶部类别的33%需同时用“Actual or intended use of emergent technologies”和“2024”定位，因为图中另一类别也有33%。
> 
> **不确定的**
> 
> 题给33%在图中重复；按核查值顺序将其对应到顶部类别的2024条。未见来源、注释或独立单位标题。

**gemini-3.1-pro**

> ### 画出来要什么
> 生成器需要能够绘制水平分组柱状图（horizontal grouped bar chart），支持在Y轴上放置长文本分类标签，并在底部X轴绘制带有百分号的刻度标签（如`10%`、`20%`）。必须支持仅显示垂直网格线（vgrid_only），并将数值标签（如`30%`、`33%`）直接打印在对应的柱状图末端外部。此外，图例需支持放置在图表底部区域，并使用颜色映射来区分不同年份（2022和2024）。标题模块应独立置于图表上方，包含图表编号和主标题。
> 
> ### 定位一个值难在哪
> 定位 `30%` 这个值，需要依赖长达六个单词的Y轴类别标签 `Actual or intended use of emergent technologies`，以及底部的图例 `2022`。在将图表解析为Markdown表格时，过长的文本标签容易发生换行、截断，导致第三步（将标签与对应单元格关联）失败。
> 
> ### 不确定的
> 无法确定原始数据中小数点后的精度（当前均显示为整数百分比），以及图表边框线和网格线的具体颜色值和粗细比例（如十六进制色号或线宽磅数）。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | grouped_bar | 8 | Figure 4.15 | above | all |
| opus-5 | f2 | unreadable | 0 | — | none | none |
| gpt-5.6-sol | f1 | grouped_bar | 8 | Figure 4.15 | above | all |
| gemini-3.1-pro | f1 | grouped_bar | 8 | Figure 4.15 | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `footnote_marker` | ✓ | — | — | opus-5: body text 'Berlin,20' and 'Copenhagen Solutions Lab21' carry superscript note numbers |
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: two bars, blue and orange, side by side in each of four indicator rows；gpt-5.6-sol: Two bars, labelled by legend entries “2022” and “2024”, sit side by side for each category.；gemini-3.1-pro: two bars (2022 and 2024) are drawn side by side within each category slot |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: category names sit on the left axis and bars grow rightwards to the 0%-60% scale；gpt-5.6-sol: Category labels are on the left and all bars extend rightward.；gemini-3.1-pro: categories sit on the left y-axis and the bars grow to the right |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: '2022  2024' colour keys sit centred beneath the 0%-60% tick row；gpt-5.6-sol: The “2022” and “2024” legend is centred beneath the bottom axis.；gemini-3.1-pro: the legend with blue 2022 and orange 2024 squares sits directly beneath the x-axis |
| `unit_in_axis_or_title` | ✓ | — | — | opus-5: tick labels themselves read '0%','10%'...'60%'; no separate unit phrase anywhere |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: '46%' and '49%' printed just beyond the right end of each bar；gpt-5.6-sol: Each percentage is printed just beyond its bar’s right endpoint.；gemini-3.1-pro: numbers like 30% and 33% are printed just past the right ends of their respective bars |
| `vgrid_only` | ✓ | ✓ | ✓ | opus-5: vertical rules at 10%, 20% ... 50% across the panel; no horizontal rules；gpt-5.6-sol: Light vertical grid lines cross the plot; no horizontal grid lines are drawn.；gemini-3.1-pro: vertical grid lines are drawn from the x-axis ticks across the panel, with no horizontal grid lines |
| `wrapped_category_labels` | ✓ | — | — | opus-5: 'Actual or intended use of emergent technologies' runs the full width of the left label column |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `figure_title_rule_bar` | opus-5 | 3 | a solid blue horizontal bar drawn immediately under the 'Figure 4.15' title line, full plot width |
| `figure_outer_border_box` | opus-5 | — | a thin rectangle frames the whole chart including legend, separating it from body text |
| `duplicate_printed_values_same_series` | opus-5 | 3 | '33%' printed twice for 2024 (emergent technologies and data policy online) |
| `figure_caption_rule` | gpt-5.6-sol | — | A blue horizontal rule spans the figure width directly below the caption. |
| `outer_figure_border` | gpt-5.6-sol | — | A thin black rectangular frame encloses the plot and legend. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 30% | Actual or intended use of emergent technologies、2022 | Actual or intended use of emergent technologies、2022 | Actual or intended use of emergent technologies、2022 | Actual or intended use of emergent technologies、2022 | ✓ | ✓ | ✓ | 过 |
| 33% | Actual or intended use of emergent technologies、2024 | Actual or intended use of emergent technologies、2024 | Actual or intended use of emergent technologies、2024 | Actual or intended use of emergent technologies、2024 | ✓ | ✓ | ✓ | 过 |
| 31% | Open government data policy online、2022 | Open government data policy online、2022 | Open government data policy online、2022 | Open government data policy online、2022 | ✓ | ✓ | ✓ | 过 |
| 37% | Open government data sharing、2024 | Open government data sharing、2024 | Open government data sharing、2024 | Open government data sharing、2024 | ✓ | ✓ | ✓ | 过 |
| 49% | Existence of smart city initiatives、2024 | Existence of smart city initiatives、2024 | Existence of smart city initiatives、2024 | Existence of smart city initiatives、2024 | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
