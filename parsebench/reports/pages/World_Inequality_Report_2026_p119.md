# World_Inequality_Report_2026_p119

![World_Inequality_Report_2026_p119](../../data/pages/World_Inequality_Report_2026_p119.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `World_Inequality_Report_2026_p119` | World_Inequality_Report_2026 | untagged | 8 | `parsebench/data/pages/World_Inequality_Report_2026_p119.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一个分组柱状图：4 个类别槽（`Bottom 50%`、`Middle 40%`、`Top 10%`、`Top 1%`），每槽 2 根柱（绿=`Consumption`，红=`Private ownership`），共 8 根。左轴竖排标题 `Share in total emissions`，刻度 `0%`–`90%` 每 10% 一档，虚线横向网格，无竖网格。图内绘图区上方另有一行图内标题 `Emissions shares by groups`，与编号标题 `Figure 6.2.` 两行大标题分属两层。图例位于绘图区下方居中。每根柱顶端外侧印带百分号的数值（`77%`、`3%`）。图下是十余行 `Interpretation.` 说明块，末尾接 `Sources and series:`，再下是双栏正文。
> 
> ## 定位一个值难在哪
> 以 `20%` 为例：它必须同时由类别刻度 `Middle 40%` 与图例项 `Private ownership` 两个标签共同定位；而类别名本身含百分数（`Top 10%`、`Top 1%`），检索值 `10` 或 `41`/`1%` 时会与轴标签文本相撞，表格即使含对的格子也可能被判错。
> 
> ## 不确定的
> 图内标题 `Emissions shares by groups` 是副标题还是面板标题，无法从图面判定；左轴标题是否被视为单位短语（刻度已带 `%`）也只能推断；`Interpretation.` 段落是否属于图的一部分（其宽度与图不同）无法确认。

**gpt-5.6-sol**

> ### 画出来要什么
> 需绘制单面板分组柱图：4个群体、2个系列、8根柱；0%—90%左轴、横向虚线网格、柱外百分比标签、图下图例。还要复现两行Figure标题、居中的“Emissions shares by groups”，以及图下解释与来源文字。
> 
> ### 定位一个值难在哪
> 例如77%需同时用“Top 10%”和“Private ownership”定位。数值及两个标签均清楚印出；真正障碍是原页没有数据表，需先把柱图转成表。
> 
> ### 不确定的
> Figure标题按可见换行拆为title与subtitle；“Emissions shares by groups”视为独立绘图区标题。百分号见于刻度和数值标签，没有独立单位行。

**gemini-3.1-pro**

> ### 画出来要什么
> 要重绘此页，需要支持标准的分组柱状图（Grouped Bar Chart）。主标题（带编号）和副标题居中置于图表上方。Y轴需显示范围 0%-90%，间隔 10%，并带有水平虚线网格，左侧有旋转的轴标题“Share in total emissions”。X轴包含四个类别，下方居中显示图例。每个柱子上方需直接绘制百分比数值标签（如 10%、77%）。
> 
> ### 定位一个值难在哪
> 以定位 77% 为例，需要结合 X 轴标签“Top 10%”和底部图例的红色标识“Private ownership”。由于数值直接印刷在柱体上方且对应关系清晰，不存在读取精度或标签关联的困难。难点仅在于解析器能否准确提取并成功输出为完整的 Markdown 表格，而不因为版式过于简单而忽略。
> 
> ### 不确定的
> 在类别轴上，“Top 1%”逻辑上属于“Top 10%”的子集，但在图表排版上被处理为与“Middle 40%”等平行的第四个类别。不确定生成器在构建数据模型时，是否需要通过某种层级结构来反映这种潜在的包含关系，还是仅需将其作为扁平的独立分类来处理即可。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | grouped_bar | 8 | Figure 6.2. | above | all |
| gpt-5.6-sol | f1 | grouped_bar | 8 | Figure 6.2. | above | all |
| gemini-3.1-pro | f1 | grouped_bar | 8 | Figure 6.2. | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: two bars, green then red, sit side by side inside each of the four category slots；gpt-5.6-sol: Two bars, Consumption and Private ownership, stand side by side within each group.；gemini-3.1-pro: bars for Consumption and Private ownership are placed side by side |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: dashed horizontal rules at every 10% tick; no vertical rules cross the panel；gpt-5.6-sol: Dashed horizontal grid lines cross the plot; no vertical grid lines are drawn.；gemini-3.1-pro: horizontal dashed lines are drawn, with no vertical rules |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: green and red swatches with `Consumption` and `Private ownership` centred under the category axis；gpt-5.6-sol: The Consumption and Private ownership legend is centered below the category axis.；gemini-3.1-pro: the legend sits at the bottom, under the x-axis |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: `Share in total emissions` set vertically along the left axis；gpt-5.6-sol: “Share in total emissions” is rotated vertically along the left axis.；gemini-3.1-pro: the y-axis title Share in total emissions is set vertically |
| `source_note_lines` | ✓ | ✓ | — | opus-5: `Interpretation.` paragraph then `Sources and series:` Bruckner et al. (2022) and Chancel and Rehm (2025b).；gpt-5.6-sol: “Sources and series:” appears in the interpretation paragraph below the plot. |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: `77%`, `47%`, `3%` printed just above the top of each bar, outside the mark；gpt-5.6-sol: All eight percentage labels are printed just above their bars.；gemini-3.1-pro: values like 10% and 77% are printed above their bars |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `inner_plot_title_under_figure_caption` | opus-5 | 3,4 | `Emissions shares by groups` sits above the plot, separate from the two-line `Figure 6.2.` caption |
| `percent_in_category_labels` | opus-5 | 3 | axis ticks read `Bottom 50%`, `Top 10%`, `Top 1%` while plotted values are also percentages |
| `interpretation_note_block` | opus-5 | 4 | ten-line block opening with bold `Interpretation.` explaining scope-1 and ownership definitions before the source line |
| `secondary_plot_title` | gpt-5.6-sol | 4 | “Emissions shares by groups” is centered between the figure heading and plot. |
| `interpretation_paragraph_below_plot` | gpt-5.6-sol | 4 | “Interpretation.” starts a full-width explanatory paragraph directly below the legend. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 10 | Consumption、Bottom 50% | Bottom 50%、Consumption | Bottom 50%、Consumption | Bottom 50%、Consumption | ✓ | ✓ | ✓ | 过 |
| 3 | Private ownership、Bottom 50% | Bottom 50%、Private ownership | Bottom 50%、Private ownership | Bottom 50%、Private ownership | ✓ | ✓ | ✓ | 过 |
| 43 | Consumption、Middle 40% | Middle 40%、Consumption | Middle 40%、Consumption | Middle 40%、Consumption | ✓ | ✓ | ✓ | 过 |
| 20 | Private ownership、Middle 40% | Middle 40%、Private ownership | Middle 40%、Private ownership | Middle 40%、Private ownership | ✓ | ✓ | ✓ | 过 |
| 47 | Consumption、Top 10% | Top 10%、Consumption | Top 10%、Consumption | Top 10%、Consumption | ✓ | ✓ | ✓ | 过 |
| 77 | Private ownership、Top 10% | Top 10%、Private ownership | Top 10%、Private ownership | Top 10%、Private ownership | ✓ | ✓ | ✓ | 过 |
| 15 | Consumption、Top 1% | Top 1%、Consumption | Top 1%、Consumption | Top 1%、Consumption | ✓ | ✓ | ✓ | 过 |
| 41 | Private ownership、Top 1% | Top 1%、Private ownership | Top 1%、Private ownership | Top 1%、Private ownership | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 3 | 1 | 1 | 未裁决 · 无实测证据 | 这一页 8 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 1 / 1 都无法证伪。 |
