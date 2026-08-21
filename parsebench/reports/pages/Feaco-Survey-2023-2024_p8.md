# Feaco-Survey-2023-2024_p8

![Feaco-Survey-2023-2024_p8](../../data/pages/Feaco-Survey-2023-2024_p8.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `Feaco-Survey-2023-2024_p8` | Feaco-Survey-2023-2024 | untagged | 4 | `parsebench/data/pages/Feaco-Survey-2023-2024_p8.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 
> 一页两个图形对象:上方是带表头底色(深绿)、隔行浅灰的六行三列数据表(`SERVICE LINE**` / `European panel trend in 2023*`);下方是灰底面板内的横向分组条形图,每个服务线三根条(2023/2022/2021),零线居中、有负值(-11.5%、-1.2%),仅垂直网格线,x 轴从 `-10.0%` 到 `35.0%`,所有条外侧标注百分比,图例在图下方三列排布。标题为独立蓝绿色粗体行,表下另有带边框的 Source/脚注框,含 `*`、`**` 脚注标记。
> 
> ## 定位一个值难在哪
> 
> `-11.5%`:图中它是 People & Change 的 2023 条,向左伸出零线;定位需要“类别 + 年份系列”两级,而年份只在图例色块里(`2023`),条上无年份文字。同一数值在上方表格里又出现一次(`People & Change` 行 / `European panel trend in 2023*` 列),两处列名写法不同,表格列名带 `*`。
> 
> ## 不确定的
> 
> 图表本身无编号(“Figure”字样不存在),故 figure_number 留空;灰底面板是否属于图的一部分只能从底色判断。轴标签 `0.0%` 处的零线是否为单独参考线无法确认。

**gpt-5.6-sol**

> ### 画出来要什么
> 页面先以六行、三年度的交替底色数据表呈现18个百分比，再用横向分组条形图重复展示。图表需支持负值越过加粗零线、5个百分点纵向网格、灰色面板、条端数值标签及图下年度图例；表格下还有带边框的来源与脚注框。
> 
> ### 定位一个值难在哪
> “22.0%”必须同时关联“Strategy”和“European panel trend in 2022*”；图中则需关联“Strategy”和图例“2022”。数值在表格与条形图中都直接印出，主要难点是保持行、列或图例的对应关系。
> 
> ### 不确定的
> 页面未印图号。顶部标题与表格之间夹有说明文字，因此只能推定其为表格标题；百分比单位没有独立单位标题，只作为各数值和刻度的后缀出现。

**gemini-3.1-pro**

> ### 画出来要什么
> 要绘制此页面，生成器需要具备以下能力：
> 1. **带背景的图表容器**：图表的标题、图例和绘图区均放置在一个完整的浅灰色背景面板中，而不是仅有绘图区带有底色。
> 2. **分组水平条形图**：支持类别轴在左侧、数值轴在下方的水平条形图结构，同时每个类别内包含三个代表不同年份的条形，并呈垂直分组排列。
> 3. **负值处理与标签放置**：数值轴需要能向左侧跨越零点（延伸至-10.0%），且针对负值条形，其数据标签需能够正确渲染在其条形的左端外部（如-11.5%）。
> 4. **垂直网格线**：只绘制穿过面板的垂直网格线，无水平网格线。
> 5. **独立表格排版**：页面同时包含具有复杂表头、单元格高亮及底部长文注释的数据表格。
> 
> ### 定位一个值难在哪
> 以 `-11.5%` 为例：该值在页面正文、图表和表格中均有出现，且均清晰印出。然而最大的解析难点在于（Step 4），由于表格缺乏紧贴的专属标题，主标题被一段长正文隔开，模型可能难以将页面最上方的主标题确认为下方表格或图表的全局上下文。
> 
> ### 不确定的
> 无法确定页面上方正文段落是作为整个报告的引言，还是应被视为表格特有的补充说明文本。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | other · data table | 18 | — | above | all |
| opus-5 | f2 | grouped_bar | 18 | — | above | all |
| gpt-5.6-sol | f1 | other · data table | 18 | — | above | all |
| gpt-5.6-sol | f2 | grouped_bar | 18 | — | above | all |
| gemini-3.1-pro | f1 | grouped_bar | 18 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `data_table_as_figure` | ✓ | ✓ | — | opus-5: bordered table with dark green header row `SERVICE LINE**` presented as the page's first figure；gpt-5.6-sol: “SERVICE LINE**” and three “European panel trend” headers form a bordered six-row table. |
| `footnote_marker` | ✓ | ✓ | — | opus-5: `SERVICE LINE**` and `European panel trend in 2023*` carry asterisk markers；gpt-5.6-sol: Headers include “SERVICE LINE**” and year labels ending with “*”. |
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: three bars (2023, 2022, 2021) stacked side by side within each service-line slot；gpt-5.6-sol: Each service line has adjacent bars for 2023, 2022 and 2021.；gemini-3.1-pro: three bars grouped together per service line |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: service-line names on the y axis, bars growing rightward to `30.6%`；gpt-5.6-sol: Service lines run down the left while bars extend horizontally.；gemini-3.1-pro: categories on the left, bars grow to the right |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: `2023  2022  2021` swatch row under the x axis at the panel bottom；gpt-5.6-sol: The “2023”, “2022” and “2021” legend is centered below the plot.；gemini-3.1-pro: legend with years sits below the plot area |
| `multi_figure_page` | ✓ | — | — | opus-5: a table with its own title and a bar chart with its own title on one page |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: bars for `-11.5%` and `-1.2%` run left of the 0.0% line；gpt-5.6-sol: Finance & Risk 2021 and People & Change 2023 extend left of zero.；gemini-3.1-pro: the -11.5% bar extends to the left of the zero line |
| `panel_background` | ✓ | ✓ | ✓ | opus-5: the whole lower figure sits on a light grey filled panel；gpt-5.6-sol: The chart and plot area use a light gray background.；gemini-3.1-pro: the entire chart area sits on a light grey background |
| `reference_line` | ✓ | ✓ | — | opus-5: a vertical rule at `0.0%` from which negative bars extend leftwards；gpt-5.6-sol: A darker vertical rule at “0.0%” separates negative and positive bars. |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: `Source: Our elaborations on MC turnover split by service lines – feaco survey 2021-2023.`；gpt-5.6-sol: “Source: Our elaborations on MC turnover split by service lines – feaco survey 2021-2023.” appears below.；gemini-3.1-pro: Source and note text with asterisks under the table |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: `20.7%`, `30.6%` printed just beyond each bar end；gpt-5.6-sol: Every percentage is printed beyond its bar end, including negative values on the left.；gemini-3.1-pro: numbers are printed at the ends of the bars |
| `vgrid_only` | ✓ | ✓ | ✓ | opus-5: vertical rules at each 5% tick; no horizontal grid lines drawn；gpt-5.6-sol: Vertical rules follow percentage ticks; no horizontal grid lines cross categories.；gemini-3.1-pro: vertical grid lines across the panel, no horizontal ones |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `table_and_chart_of_same_data` | opus-5 | 1,3 | the six-row table values 20.7%, 6.1%, 30.6% are re-drawn identically as the bars below |
| `boxed_footnote_block` | opus-5 | 4 | bordered box holding Source line plus `*` and `**` explanatory notes under the table |
| `zebra_striped_table_rows` | opus-5 | 1 | alternating grey/white row fills across `Technology`, `Strategy`, `People & Change` |
| `alternating_table_row_banding` | gpt-5.6-sol | 3 | Alternate service-line rows have light gray fill while intervening rows are white. |
| `companion_table_and_chart` | gpt-5.6-sol | 1,2,3 | The same six service lines and 18 percentages appear in both table and grouped bars. |
| `unit_suffix_on_ticks_and_labels` | gpt-5.6-sol | 2 | Every value label and bottom-axis tick carries a trailing percent sign. |
| `boxed_source_notes` | gpt-5.6-sol | 4 | Source and three note lines sit together inside a thin teal rectangular border. |
| `table_and_chart_redundancy` | gemini-3.1-pro | 3,4 | the same data is presented in a table and a chart |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 20.7% | Sales & Marketing、2023 | Sales & Marketing、2023 | Sales & Marketing、European panel trend in 2023* | Sales & Marketing、2023 | ✓ | ✓ | ✓ | 过 |
| 10.6% | Technology、2022 | Technology、2022 | Technology、European panel trend in 2022* | Technology、2022 | ✓ | ✓ | ✓ | 过 |
| 22.0% | Strategy、2022 | Strategy、2022 | Strategy、European panel trend in 2022* | Strategy、2022 | ✓ | ✓ | ✓ | 过 |
| -11.5% | People & Change、2023 | People & Change、2023 | People & Change、European panel trend in 2023* | People & Change、2023 | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "other · data table" | "other · data table" | "grouped_bar" | 不裁 · 三家的第一张图不是同一张 | opus 与 gpt 把页面上方那块 18 个数的表格收成第一张图，gemini 没收，它的第一张是下方的 grouped_bar。 |
| `hardest_step` | 3 | 3 | 4 | 未裁决 · 无实测证据 | 这一页 4 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 3 / 4 都无法证伪。 |
| `value_axes#f1` | 0 | 0 | 1 | 不裁 · 三家的第一张图不是同一张 | opus 与 gpt 把页面上方那块 18 个数的表格收成第一张图（没有轴），gemini 没收，于是它的第一张是下方那张 grouped_bar。错位一张，无共同标的。又一条 `data_table_as_figure` 的证据。 |
