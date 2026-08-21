# TSLA-Q4-2024-Update_p9

![TSLA-Q4-2024-Update_p9](../../data/pages/TSLA-Q4-2024-Update_p9.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `TSLA-Q4-2024-Update_p9` | TSLA-Q4-2024-Update | need_estimate | 10 | `parsebench/data/pages/TSLA-Q4-2024-Update_p9.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 本页是左文右图的双栏版式：右上是一张当作图表用的表格 `Current Installed Annual Vehicle Capacity`（Region/Model/Capacity/Status 四列、九行，表头深灰底、行间浅灰斑马纹，Region 列在续行留空，Capacity 用 `>550,000` 这类带不等号的写法，无容量处写 `-`）；右下是三线折线 `Market share of Tesla vehicles by region (TTM)`——标题**在图下方**、图例（US/Canada、Europe、China）在图**上方**，y 轴 0%–4% 只有四条水平网格线，x 轴 24 个 `Q1 2019`…`Q4 2024` 斜排刻度，无数据点标记、无数值标签。左侧整栏正文与图并排。
> 
> **定位一个值难在哪**
> `1.1`（US/Canada 在 Q1 2019）：图上没有任何数字，只能在 1% 与 2% 网格线之间目测；5% 容差只有 ±0.055 个百分点，而一格网格代表 1%，像素级读数根本达不到。而且它的地址需要「图例名 + 季度刻度」两段标签，季度刻度是旋转文字。
> 
> **不确定的**
> 两个 `1.5` 分别属于哪条线哪个季度无法确定；`2.6` 是 Europe 的峰值还是某季度值也只能猜。表格下方灰色小字是注释还是免责声明未标 `Note:`。

**gpt-5.6-sol**

> ### 画出来要什么
> 页面需并排组合正文、灰底容量表和三系列折线图。表格含合并式地区标签、粗体车型、下限符号及缺失值；折线图需绘制百分比刻度、季度斜排标签、上置图例、下置标题和来源行。
> 
> ### 定位一个值难在哪
> 例如 China、Q1 2019 的 0.1：数值未印出，纵轴相邻刻度相差1个百分点，而5%容差只有0.005，无法稳定读准。
> 
> ### 不确定的
> 折线顶点无标记、无数值标签；2.6、2.4等读数在相邻季度近乎重复，精确对应季度只能按折点位置估计。

**gemini-3.1-pro**

> ### 画出来要什么
> 生成器需要支持整页图文并排布局（左侧为正文栏，右侧放置表格和折线图）。对于折线图，需要支持将主标题居中置于x轴的下方，而图例悬浮于绘图区正上方。此外，x轴的时间标签需支持45度旋转，且图表仅保留横向网格线。页面上方的纯数据表格需支持图表样式的标题，并支持通过留空分类单元格来隐式表达行分组关系。
> 
> ### 定位一个值难在哪
> 以“1.1”为例（US/Canada系列在Q1 2019的值），折线图的纵轴主网格线间隔为1%，没有任何次级网格或数据点标签，由于线段走势平滑，仅凭视觉去估算曲线高度绝对无法保证读取误差控制在5%以内。
> 
> ### 不确定的
> 多个指定的抽查数据点（如0.4、1.5、2.4等）并未正好落在坐标轴的交叉刻度上。由于图表没有任何提示线，这部分数据只能依靠对折线所在大概季度位置及纵向高度的目测进行反推，其精确值存在一定的推测成分。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | other · data table | 36 | — | above | all |
| opus-5 | f2 | line | 72 | — | below | none |
| gpt-5.6-sol | f1 | other · data table | 36 | — | above | all |
| gpt-5.6-sol | f2 | line | 72 | — | below | none |
| gemini-3.1-pro | f1 | other · table | 18 | — | above | all |
| gemini-3.1-pro | f2 | line | 72 | — | below | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `data_table_as_figure` | ✓ | ✓ | ✓ | opus-5: Bordered table headed 'Region | Model | Capacity | Status' under a bold title, placed as a figure；gpt-5.6-sol: A titled grey table has headers “Region”, “Model”, “Capacity” and “Status”.；gemini-3.1-pro: table captioned 'Current Installed Annual Vehicle Capacity' |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: Horizontal rules at 0%, 1%, 2%, 3%, 4%; no vertical rules in the plot；gpt-5.6-sol: Horizontal rules appear at 0%, 1%, 2%, 3% and 4%; no vertical gridlines appear.；gemini-3.1-pro: horizontal lines mark percentages, no vertical lines |
| `highlighted_category` | ✓ | — | — | opus-5: Model column entries ('Model S / Model X', 'Cybertruck') set in bold, Region column not |
| `legend_above_plot` | ✓ | ✓ | ✓ | opus-5: 'US/Canada  Europe  China' with line keys sits between the note text and the plot；gpt-5.6-sol: The “US/Canada”, “Europe” and “China” legend sits above the plotting area.；gemini-3.1-pro: US/Canada, Europe, China legend sits above the plot |
| `missing_value_marker` | ✓ | ✓ | ✓ | opus-5: Capacity cells read '-' for Cybercab, Tesla Semi and Roadster；gpt-5.6-sol: Capacity cells for Cybercab, Tesla Semi and Roadster contain “-”.；gemini-3.1-pro: Capacity cells show a '-' dash for some models |
| `multi_figure_page` | ✓ | — | — | opus-5: Titled table 'Current Installed Annual Vehicle Capacity' above a separately captioned line chart |
| `nonstandard_time_ticks` | ✓ | ✓ | ✓ | opus-5: Time written as 'Q1 2019', 'Q4 2024' rather than ISO dates；gpt-5.6-sol: Time ticks use quarter-first labels such as “Q1 2019”.；gemini-3.1-pro: Q1 2019 format is not standard ISO |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: 'Q1 2019' ... 'Q4 2024' tick text set at roughly 45 degrees；gpt-5.6-sol: Quarter labels from “Q1 2019” to “Q4 2024” are diagonally rotated.；gemini-3.1-pro: Q1 2019 etc. labels are angled at 45 degrees |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: Left column body text 'US: California, Nevada and Texas' runs level with both figures；gpt-5.6-sol: Long prose headed “US: California, Nevada and Texas” runs beside the figures.；gemini-3.1-pro: prose is set in a column beside the figures |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Source: Tesla estimates based on latest available data from ACEA; Autonews.com; CAAM \u2013 light-duty vehicles only'；gpt-5.6-sol: “Source: Tesla estimates based on latest available data” appears below the title.；gemini-3.1-pro: 'Source: Tesla estimates...' at bottom of the page |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `figure_title_below_plot` | opus-5 | 3,4 | Bold 'Market share of Tesla vehicles by region (TTM)' printed under the x tick labels |
| `blank_cell_for_repeated_row_label` | opus-5 | 3 | Region column empty on 'Model 3 / Model Y' (California) and on 'Cybertruck', 'Cybercab' (Texas) rows |
| `inequality_prefixed_value` | opus-5 | 2 | Capacity cells read '>550,000', '>950,000', '>375,000' rather than plain numbers |
| `zebra_striped_table_rows` | opus-5 | 1 | Alternating white and light-grey row fills below a dark grey header band |
| `merged_row_group_label` | gpt-5.6-sol | 3 | “California” and “Texas” each govern several following model rows with blank Region cells. |
| `inequality_prefixed_values` | gpt-5.6-sol | 2 | Capacity entries include “>550,000”, “>950,000”, “>375,000”, “>250,000” and “>125,000”. |
| `figure_title_below_plot` | gpt-5.6-sol | 4 | “Market share of Tesla vehicles by region (TTM)” is centered beneath the x-axis ticks. |
| `tick_label_unit_suffix` | gpt-5.6-sol | 2,4 | Every value tick carries the suffix: “0%”, “1%”, “2%”, “3%”, “4%”. |
| `table_implied_row_grouping` | gemini-3.1-pro | 3 | empty Region cells under California imply the same region |
| `figure_title_below_plot` | gemini-3.1-pro | 4 | the main figure title sits below the x-axis |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 1.1 | US/Canada、Q1 2019 | US/Canada、Q1 2019 | US/Canada、Q1 2019 | US/Canada、Q1 2019 | ✓ | ✓ | ✓ | 过 |
| 4.0 | US/Canada、Q4 2023 | US/Canada、Q4 2023 | US/Canada、Q4 2023 | US/Canada、Q1 2024 | ✓ | ✓ | ✗ | 没过 |
| 3.7 | US/Canada、Q4 2024 | US/Canada、Q4 2024 | US/Canada、Q4 2024 | US/Canada、Q4 2024 | ✓ | ✓ | ✓ | 过 |
| 0.4 | Europe、Q1 2019 | Europe、Q1 2019 | Europe、Q2 2019 | Europe、Q3 2019 | ✓ | ✗ | ✗ | 过 |
| 2.6 | Europe、Q1 2024 | Europe、Q2 2023 | Europe、Q3 2024 | Europe、Q2 2024 | ✗ | ✗ | ✗ | 过 |
| 2.5 | Europe、Q4 2024 | Europe、Q4 2024 | Europe、Q4 2024 | Europe、Q4 2024 | ✓ | ✓ | ✓ | 过 |
| 0.1 | China、Q1 2019 | China、Q1 2019 | China、Q1 2019 | China、Q1 2019 | ✓ | ✓ | ✓ | 过 |
| 1.5 | China、Q1 2022 | US/Canada、Q2 2021 | Europe、Q4 2021 | US/Canada、Q1 2021 | ✗ | ✗ | ✗ | 没过 |
| 2.4 | China、Q4 2024 | China、Q4 2024 | China、Q4 2024 | China、Q4 2024 | ✓ | ✓ | ✓ | 过 |
| 1.5 | US/Canada、Q1 2021 | China、Q4 2021 | China、Q4 2021 | China、Q2 2022 | ✗ | ✗ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "other · data table" | "other · data table" | "other · table" | other · 表格型图 | 三家都记 `data_table_as_figure`，分歧只在写 `data table` 还是 `table`。这是同一个答案的两种写法，不是读法分歧。<strong>P10 证据。</strong> |
| `density#f1` | "21–60" | "21–60" | "≤20" | 21–60（按中位数 36 个图元） | 三家数出的图元个数是 36 / 36 / 18，中位数 36，落在 21–60。三个数相差超过一半，取中位数所在的档；差异来自把叠在一起的图元数成一层还是两层。 |
