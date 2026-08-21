# article_thebeatjun2025_p35

![article_thebeatjun2025_p35](../../data/pages/article_thebeatjun2025_p35.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `article_thebeatjun2025_p35` | article_thebeatjun2025 | untagged | 10 | `parsebench/data/pages/article_thebeatjun2025_p35.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一张无编号的高低区间图：每个板块画一根从10年**High**到**Low**的实心竖条，条上叠一个灰色圆点(**Current**)和一条深红短横(**Average**)，四个角色的名字只在左侧一个「示意条」图例里给出。还要有蓝色虚线基准 `S&P 500 Current P/E`、括号式负刻度 `(10.0)` `(30.0)`、Energy 条冲出画面下沿并标 `-263.8 *Not to scale`，以及贴在类别轴下方、与各板块列对齐的 `High Date` / `Low Date` 两行小表。全部30个标记的数值都以颜色区分（灰=Current，深红=Average）印在图上。
> 
> ## 定位一个值难在哪
> `21.7` 是 Information Technology 的 Average。它印在条的右侧，紧挨着 Materials 的灰色 `20.1`，两数几乎连成 `21.7 20.1`；而「Average」这个词全图只出现一次——在左上角的示意图例里。要唯一定位它，需要板块名（来自表头）+ 角色名（来自图例）+ 颜色（深红而非灰）三重信息。
> 
> ## 不确定的
> Average 到底是短横线还是条内色块分界，分辨率下难判；灰色 `22.6`（Consumer Staples Current）与其 High `22.6` 是否同值无法核实；左轴是否有 0 刻度线未标出。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 需绘制十个从 Low 延伸至 High 的浮动区间柱，叠加 Current 圆点、Average 横刻，以及标为“S&P 500 Current P/E”的蓝色虚线；柱外打印四类数值。类别下方还需对齐“High Date”“Low Date”两行。
> 
> **定位一个值难在哪**
> 
> 例如 21.7 必须同时关联“Information Technology”和“Average”；同一类别周围另有 High、Low、Current 三个数值。-263.8 虽已打印，但其柱明确“*Not to scale”，无法凭轴高复核。
> 
> **不确定的**
> 
> Average 标记看似柱内白色短横或缺口；据此估算全图 31 个图形标记。日期行属于图内元数据，而非独立图表。

**gemini-3.1-pro**

> ### 画出来要什么
> 生成器需要支持悬浮范围柱状图（Floating Bar），表示从 High 到 Low 的区间，并在其柱体内外添加不同形状的标记（如圆点表示 Current，横线表示 Average）。要求同一类别中组合多种标记，并依靠标记及其对应文本标签的颜色（Current 为灰色，Average 为红色）来区分数据系列。需要支持绘制跨越整个绘图区的类别参考线（如 S&P 500 的蓝色虚线）。X轴需要支持下挂与其类别对齐的数据表格（High Date, Low Date）。此外，需要支持单一标记突破 Y 轴的物理限制，进行截断绘制并附加内联文本注释（如 Energy 极值 -263.8 下方的 `*Not to scale`）。
> 
> ### 定位一个值难在哪
> 以 `19.8` 为例，该数值作为 Consumer Discretionary 的 Average 系列标签，与其他类别的标签以及 Current 数值密集地挤在一起。页面上没有任何指示线（leader line）将文本与标记连接，唯一能将 `19.8` 归属于 Average 系列的依据是其字体的红色，解析器在丢失颜色映射且缺乏空间强绑定的情况下极易将其错配给相邻类别或系列。
> 
> ### 不确定的
> 由于 Consumer Discretionary 和 Consumer Staples 区域的文本和标记相互重叠，部分类别的 Top 或 Bottom 极值没有印出对应的数字，且个别圆点的位置难以明确分配给哪个扇区，仅能通过颜色和大概的Y轴位置推断其归属关系。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | other · high-low range bar | 31 | — | above | all |
| gpt-5.6-sol | f1 | other · range bar plot | 31 | — | above | all |
| gemini-3.1-pro | f1 | other · floating bar with markers | 33 | — | above | some |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | — | — | opus-5: '-263.8 *Not to scale' printed under the Energy bar inside the plot area |
| `footnote_marker` | ✓ | — | — | opus-5: asterisk in '*Not to scale' attached to the Energy low label |
| `highlighted_category` | — | — | ✓ | gemini-3.1-pro: the S&P 500 category is set apart on the left and styled in a different color |
| `inline_series_labels` | — | ✓ | ✓ | gpt-5.6-sol: “S&P 500 Current P/E” is printed directly beside the blue dashed rule.；gemini-3.1-pro: the blue dashed line is labeled directly with 'S&P 500' and 'Current P/E' |
| `legend_beside_plot` | ✓ | ✓ | ✓ | opus-5: schematic bar at far left with 'High', 'Current', 'Average', 'Low' pointing at its parts；gpt-5.6-sol: The High, Current, Average, and Low key sits left of the plotted categories.；gemini-3.1-pro: the legend indicating High, Current, Average, and Low sits vertically on the left |
| `mixed_marks` | ✓ | ✓ | — | opus-5: grey circle markers and short crimson ticks drawn over each crimson high-low bar；gpt-5.6-sol: Magenta range bars carry gray circles and short average tick markers. |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: axis ticks '(10.0)' and '(30.0)'; Energy low printed as '-263.8'；gpt-5.6-sol: Energy Low is printed “-263.8” below the positive portion of its range.；gemini-3.1-pro: the y-axis has ticks at (10.0) and (30.0), and the Energy bar drops to -263.8 |
| `nonstandard_time_ticks` | ✓ | — | — | opus-5: attached table cells read '8/20', '5/18', '4/16' rather than ISO dates |
| `range_connector_line` | ✓ | — | — | opus-5: each sector is one bar spanning its 10-year High to Low, e.g. 24.0 down to 10.0 |
| `reference_line` | ✓ | ✓ | ✓ | opus-5: blue dashed horizontal rule labelled 'S&P 500' / 'Current P/E' at the left edge；gpt-5.6-sol: A blue dashed horizontal rule is labelled “S&P 500 Current P/E”.；gemini-3.1-pro: a dashed blue line for S&P 500 Current P/E spans horizontally across the plot |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Source: FactSet as of 5/31/25. NTM P/E is market price per share divided by expected earnings per share...'；gpt-5.6-sol: Small print begins “Source: FactSet as of 5/31/25.” below the figure.；gemini-3.1-pro: Source text starting with 'FactSet as of...' appears at the bottom |
| `tick_marker_as_series` | ✓ | ✓ | — | opus-5: the Average series is a short horizontal tick across the bar, read on the same axis；gpt-5.6-sol: “Average” is represented by a short horizontal marker crossing each magenta range. |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: left axis reads 70.0, 50.0, 30.0, 10.0 with no unit; only the title says 'NTM P/E'；gpt-5.6-sol: The title states “Current NTM P/E” while value-axis ticks are bare numbers. |
| `value_label_outside` | ✓ | ✓ | — | opus-5: 24.0 above and 10.0 below the Communication Services bar; 16.6 beside the average tick；gpt-5.6-sol: High, Low, Current, and Average numbers are printed beside or beyond their marks. |
| `wrapped_category_labels` | ✓ | ✓ | — | opus-5: 'Communication Services' and 'Information Technology' wrap onto two lines；gpt-5.6-sol: “Communication Services” and “Information Technology” wrap onto two lines. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `clipped_out_of_range_mark` | opus-5 | 2 | Energy bar runs past the bottom of the axis; label reads '-263.8 *Not to scale' |
| `metadata_table_below_axis` | opus-5 | 1,3 | 'High Date' and 'Low Date' rows of dates aligned to the sector columns under the plot |
| `parenthesis_negative_ticks` | opus-5 | 2 | negative axis ticks printed as '(10.0)' and '(30.0)' instead of -10.0 |
| `schematic_key_diagram` | opus-5 | 3 | legend is a miniature example bar with High/Current/Average/Low labelling its parts |
| `floating_range_bar` | gpt-5.6-sol | 2,3 | Each magenta rectangle begins at Low and ends at High rather than starting at zero. |
| `category_aligned_metadata_rows` | gpt-5.6-sol | 3 | “High Date” and “Low Date” rows align ten dates beneath the category labels. |
| `out_of_scale_mark_without_axis_break` | gpt-5.6-sol | 2 | Energy Low reads “-263.8” with “*Not to scale”; no axis-break glyph is drawn. |
| `composite_range_legend` | gpt-5.6-sol | 3 | One sample range glyph jointly explains High, Low, Current circle, and Average tick. |
| `aligned_data_table` | gemini-3.1-pro | 1,3 | a table of High Date and Low Date is aligned directly under the category axis |
| `out_of_scale_mark` | gemini-3.1-pro | 2 | the Energy bar drops below the axis to -263.8 with an inline '*Not to scale' note |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 24.0 | Communication Services、High | Communication Services、High | Communication Services、High | S&P 500、High | ✓ | ✓ | ✗ | 过 |
| 16.9 | Consumer Discretionary、Low | Consumer Discretionary、Low | Consumer Discretionary、Low | Communication Services、Low | ✓ | ✓ | ✗ | 过 |
| 19.8 | Consumer Staples、Average | Consumer Staples、Average | Consumer Staples、Average | Consumer Discretionary、Average | ✓ | ✓ | ✗ | 过 |
| 77.2 | Energy*、High | Energy、High | Energy、High | Energy、High | ✓ | ✓ | ✓ | 过 |
| -263.8 | Energy*、Low | Energy、Low | Energy、Low | Energy、Low | ✓ | ✓ | ✓ | 过 |
| 16.7 | Financials、Current NTM P/E | Financials、Current | Financials、Current | Financials、Current | ✓ | ✓ | ✓ | 过 |
| 13.8 | Health Care、Low | Health Care、Low | Health Care、Low | Health Care、Low | ✓ | ✓ | ✓ | 过 |
| 23.7 | Industrials、Average | Industrials、Current | Industrials、Current | Industrials、High | ✗ | ✗ | ✗ | 过 |
| 21.7 | Information Technology、Current NTM P/E | Information Technology、Average | Information Technology、Average | Materials、Average | ✗ | ✗ | ✗ | 过 |
| 21.3 | Utilities、High | Utilities、High | Utilities、High | Utilities、High | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "other · high-low range bar" | "other · range bar plot" | "other · floating bar with markers" | other · 区间条 + 当前值标记 | 三家都判 other，自拟名字分别是 high-low range bar with current marker / range bar plot / range bar with markers，指同一种画法。这一条记为归一化没能合并三个自拟名字，不是读图分歧。 |
| `printed#f1` | "all" | "all" | "some" | all | opus 与 gemini 都说 all；gpt 答 some，但它自己的 report_md 写「所有目标数值均直接标注」，两处矛盾，取 all。 |
