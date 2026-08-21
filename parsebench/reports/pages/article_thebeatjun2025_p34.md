# article_thebeatjun2025_p34

![article_thebeatjun2025_p34](../../data/pages/article_thebeatjun2025_p34.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `article_thebeatjun2025_p34` | article_thebeatjun2025 | untagged | 10 | `parsebench/data/pages/article_thebeatjun2025_p34.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一张无编号的**区间条图**:每个类别一根从 Low 到 High 的洋红竖条(如 Russell 2000 从 15.2 到 63.5,轴要撑到 70.0),条上叠一个灰色圆点表示 Current,右侧另印洋红的 Average 数字;每格四个数字分别摆在条上方、下方、左侧(灰)、右侧(洋红)。还要画一条蓝色虚线基准线,行内标注 "MSCI World Current P/E"(19.1)。左侧是一个**示意图例**:一根缩小的条,四周写 High / Low / Current / Average。类别轴下再挂两行对齐的表格 "High Date" 8/20 与 "Low Date" 12/18。页头 "EQUITIES" 小标 + "Valuation Analysis" 大标 + 加粗图题三层。
> 
> ## 定位一个值难在哪
> 以 **12.1** 为例:它同时是 Russell 1000 Value 的 Low、MSCI EM 的 Current、以及 MSCI EM 的 Average。要唯一定位必须写成「MSCI EM · Average」,而 Average 与 Current 在同一格里只靠灰/洋红两种颜色和左右位置区分,角色名只出现在左上角的示意图例中,不在任何轴或图例文字行上。14.4、15.2、17.4 同样重复出现。
> 
> ## 不确定的
> 条形究竟是整根 Low→High 还是被 Average 分段(图例里似有分隔)看不清;Average 是否另有短刻度标记只能猜;"NTM P/E" 作为单位只写在图题里,纵轴 0.0–70.0 无单位字样。

**gpt-5.6-sol**

> ### 画出来要什么
> 要绘制十类资产的竖向浮动区间条：上下端表示 High/Low，中间断口表示 Average，灰点表示 Current；四类数值均置于标记外。还需蓝色虚线基准、左侧图例、两行折行类目，以及轴下对齐的“High Date”“Low Date”日期行。
> 
> ### 定位一个值难在哪
> “Russell 2000”的 23.3 是 Current，而相邻的 23.9 是 Average；必须同时保留类目和统计类型，不能只按邻近位置或数值匹配。
> 
> ### 不确定的
> Average 看起来是区间条中的白色断口，而非独立短横标记；因此 marks 数量取决于是否把上下两段分别计数。纵轴未明确写出单位。

**gemini-3.1-pro**

> ### 画出来要什么
> 需要能绘制范围浮动柱状图（Range Column），并在其上或其周围叠加散点（Current系列）和短横线（Average系列）。图例模块需要支持高度自定义，能够组合多种图元并带有指示线，作为一个“复合图解”放置在图表左侧。X轴的分类标签需要能支持多行颜色不同的文本，并且最关键的是，X轴正下方需要能拼接并对齐一个多行的数据表（包含“High Date”和“Low Date”）。数据标签需要具备极高的放置自由度，能针对同一柱体的不同系列分别定位在顶部、底部、左侧或右侧。
> 
> ### 定位一个值难在哪
> 以 `22.9` 为例，这是 S&P 500 的 High 值。该图表中每个分类（如S&P 500）周围都散布着四个没有任何指示线的数值标签（22.9, 21.3, 18.4, 14.4），解析器不仅要准确抓取这些离散数字，还必须理解左侧那张非标准的“复合图例”，才能在没有颜色映射或排版规律的情况下，将顶部数字正确识别为 High，左侧数字识别为 Current。
> 
> ### 不确定的
> 不确定现有的表格解析逻辑是否会将底部对齐的日期数据表与上方的图表视为同一个逻辑单元（带有扩展分类轴），还是会将其切割为独立的无用表格。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | other · high-low range bar | 20 | — | above | all |
| gpt-5.6-sol | f1 | other · range bar | 31 | — | above | all |
| gemini-3.1-pro | f1 | other · range column with markers | 41 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `highlighted_category` | — | ✓ | — | gpt-5.6-sol: “MSCI World” is blue while the other category labels are magenta. |
| `inline_series_labels` | ✓ | ✓ | ✓ | opus-5: "MSCI World / Current P/E" written in blue at the left end of the dashed line；gpt-5.6-sol: “MSCI World Current P/E” is written beside the blue dashed line.；gemini-3.1-pro: the text 'MSCI World Current P/E' beside the dashed line |
| `legend_beside_plot` | ✓ | ✓ | ✓ | opus-5: key with High/Current/Average/Low sits left of the value axis, level with the plot top；gpt-5.6-sol: The High, Current, Average, Low key sits left of the value ticks.；gemini-3.1-pro: legend diagram is on the left of the y-axis |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: grey circle markers overlaid on the crimson high-low bars in every category slot；gpt-5.6-sol: Floating magenta range bars are overlaid with grey circular Current markers.；gemini-3.1-pro: bars, circles, and short horizontal lines used together |
| `nonstandard_time_ticks` | ✓ | — | — | opus-5: High/Low Date cells read "8/20", "12/18", "1/21" rather than ISO dates |
| `reference_line` | ✓ | ✓ | ✓ | opus-5: blue dashed horizontal rule across the plot at ~19.1, labelled at left；gpt-5.6-sol: A blue dashed horizontal line is labeled “MSCI World Current P/E”.；gemini-3.1-pro: blue dashed line for MSCI World Current P/E |
| `source_note_lines` | ✓ | ✓ | — | opus-5: "Source: FactSet as of 5/31/25. NTM P/E is market price per share divided by expected earnings..."；gpt-5.6-sol: Below the figure begins “Source: FactSet as of 5/31/25.” |
| `tick_marker_as_series` | — | — | ✓ | gemini-3.1-pro: Average series is drawn as a short red horizontal tick |
| `total_row_below_axis` | ✓ | — | — | opus-5: rows "High Date" 8/20 6/20 ... and "Low Date" 12/18 9/22 ... aligned under the categories |
| `unit_in_axis_or_title` | ✓ | — | — | opus-5: left axis reads 0.0, 10.0 ... 70.0 with no unit; "Current NTM P/E" only in the title |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: "22.9" above and "14.4" below the S&P 500 bar, outside the mark；gpt-5.6-sol: High, Low, Average, and Current numbers are printed outside the bars and dots.；gemini-3.1-pro: values are printed around the composite marks |
| `wrapped_category_labels` | ✓ | ✓ | — | opus-5: "MSCI World ex / USA Small Cap" and "Russell 1000 / Growth" wrap onto two lines；gpt-5.6-sol: Labels including “Russell 1000 Growth” and “MSCI World ex USA Small Cap” wrap onto two lines. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `range_bar_with_point_marker` | opus-5 | 2,3 | each slot: a Low-to-High crimson bar, a grey Current dot on it, and a printed Average |
| `schematic_legend_key` | opus-5 | 3 | legend is a miniature bar with High, Low, Current, Average labelled around it, not colour swatches |
| `data_rows_under_category_axis` | opus-5 | 1,3 | two labelled rows "High Date" and "Low Date" of dates, banded grey, aligned to each category |
| `floating_range_bar_with_average_split` | gpt-5.6-sol | 2,3 | Each category has a floating Low–High bar split at Average, plus a Current dot. |
| `aligned_metadata_rows_below_axis` | gpt-5.6-sol | 3,4 | “High Date” and “Low Date” rows align dates beneath all ten categories. |
| `fixed_one_decimal_value_ticks` | gpt-5.6-sol | 2 | The value ticks run from “0.0” to “70.0”, consistently using one decimal. |
| `aligned_data_table_below_axis` | gemini-3.1-pro | 1,3 | table with High Date and Low Date aligned with categories |
| `custom_shape_legend` | gemini-3.1-pro | 3 | legend is drawn as a diagram of the composite mark itself |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 22.9 | S&P 500、High | S&P 500、High | S&P 500、High | S&P 500、High | ✓ | ✓ | ✓ | 过 |
| 23.3 | Russell 2000、Current | Russell 2000、Current | Russell 2000、Current | Russell 2000、Current | ✓ | ✓ | ✓ | 过 |
| 16.8 | Russell 1000 Growth、Low | Russell 1000 Growth、Low | Russell 1000 Growth、Low | Russell 1000 Growth、Low | ✓ | ✓ | ✓ | 过 |
| 15.2 | Russell 1000 Value、Average | Russell 2000、Low | Russell 1000 Value、Average | Russell 2000、Low | ✗ | ✓ | ✗ | 过 |
| 19.1 | MSCI World、Current | MSCI World、Current | MSCI World、Current | MSCI World、Current | ✓ | ✓ | ✓ | 过 |
| 19.7 | MSCI World ex USA Small Cap、High | MSCI World ex USA Small Cap、High | MSCI World ex USA Small Cap、High | MSCI World ex USA Small Cap、High | ✓ | ✓ | ✓ | 过 |
| 11.0 | MSCI EAFE、Low | MSCI EAFE、Low | MSCI EAFE、Low | MSCI EAFE、Low | ✓ | ✓ | ✓ | 过 |
| 12.1 | MSCI EM、Average | Russell 1000 Value、Low | MSCI EM、Average | Russell 1000 Value、Low | ✗ | ✓ | ✗ | 过 |
| 14.4 | MSCI Europe、Current | S&P 500、Low | MSCI Europe、Current | S&P 500、Low | ✗ | ✓ | ✗ | 过 |
| 17.4 | MSCI AC Asia Pac、High | MSCI Europe、High | MSCI AC Asia Pac、High | MSCI Europe、High | ✗ | ✓ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "other · high-low range bar" | "other · range bar" | "other · range column with markers" | other · 区间条（带标记） | 三家分别写 `high-low range bar` / `range bar` / `range column with markers`，都记了 `mixed_marks` 与 `reference_line`：一根不从零起算的条，两端各是一个值，上面再叠一个标记。三个名字说的是同一种画法。<strong>P10 证据，而且是「一根条两个值」那一类。</strong> |
| `density#f1` | "≤20" | "21–60" | "21–60" | 21–60（按中位数 31 个图元） | 三家数出的图元个数是 20 / 31 / 41，中位数 31，落在 21–60。三个数相差超过一半，取中位数所在的档；差异来自把叠在一起的图元数成一层还是两层。 |
