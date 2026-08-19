# Consultancy-in-Spain.-The-industry-in-figures-2024_p15

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Consultancy-in-Spain.-The-industry-in-figures-2024 | `untagged` | 4 | 0 |

该页含两幅无编号折线图：上图为2015=100基准的人力、营收与生产力指数演变，下图为西班牙咨询公司人力、第三方雇员与知识密集型就业的年增长率（2015-2024）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 198 | `Workforce` · `2024` | 1% | f1 | the 2024 point of the Workforce line, label printed above the marker | 是 | `Workforce` · `2024` · `Evolution of the workforce, revenue and productivity` |
| 2 | 93 | `Productivity (revenue per employee)` · `2020` | 1% | f1 | the Productivity (revenue per employee) point at 2020 (also 2021 shows 93) | 是 | `Productivity (revenue per employee)` · `2020` · `Evolution of the workforce, revenue and productivity` |
| 3 | 14.1% | `Consulting firm workforce` · `2016` | 1% | f2 | the 2016 peak point of the Consulting firm workforce line | 是 | `Consulting firm workforce` · `2016` · `Workforce growth rate at Spanish consulting firms, of third-party employees in Spain and of employment in knowledge-intensive jobs in Spain` |
| 4 | 3.9% | `Knowledge-intensive employment` · `2022` | 1% | f2 | the Third-party employees registered with the Spanish Social Security system points at 2022 and 2023 (both labelled 3.9%) | 是 | `Third-party employees registered with the Spanish Social Security system` · `2022` · `Workforce growth rate at Spanish consulting firms, of third-party employees in Spain and of employment in knowledge-intensive jobs in Spain` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——4 values given, 5 answered
- 模型预测的定位标签漏掉了规则实际用的标签——1 of 4 predicted key sets miss a rule label: 3.9%

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 3 | 10 | 30 | 全部 | （不画值轴） |
| f2 | `line` | vertical | 1 | 3 | 10 | 30 | 全部 | （不画值轴） |

- **f1** Evolution of the workforce, revenue and productivity / (measured as revenue per employee) (2015= base of 100)　[图上方]　单位 `(2015= base of 100)`
  - 来源行：Source: AEC (Spanish Association of Consulting Firms)
- **f2** Workforce growth rate at Spanish consulting firms, of third-party employees in Spain and of employment in knowledge-intensive jobs in Spain / (2015-2024)　[图上方]　（标题里没有单位）
  - 来源行：Sources: Spanish consulting firm workforce: AEC (Spanish Association of Consulting Firms); third-party employees registered with the Spanish Social Security system in Spain: Spanish Ministry of Labor and Social Economy Statistics Annual; knowledge-intensive employment: Eurostat.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | vertical dashed rule drawn at 2016 across the plot area |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f2 | **无** | vertical dashed rule at 2016 through the plot area |
| `negative_values` | 负值 / 零线居中的分叉条 | f2 | **无** | "-2.1%" printed at 2020 for the third-party employees line, below the others |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only horizontal grid lines and year ticks; no numeric tick labels on the vertical axis |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | grid lines but no numeric labels on the vertical axis; values only as printed labels |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two independent titled charts with their own Source / Sources lines stacked on one page |
| `source_note_lines` | source / note 行在图下方 | page | 有 | "Source: AEC (Spanish Association of Consulting Firms)"; "Sources: ..."; "– – – Methodological change." |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | dot legend "Workforce  Revenue  Productivity (revenue per employee)" under the year axis |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | three-dot legend row under the year axis, above the Sources line |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | scale word only in the heading "(measured as revenue per employee) (2015= base of 100)" |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | heading reads "(2015= base of 100)" and 2015 values are all 100 |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | numbers 100, 114, 118, 129 ... printed above or below each point marker |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | "14.1%", "9.4%", "-2.1%" printed beside each plotted point |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f2 | **无** | legend entries wrap: "Third-party employees registered with / the Spanish Social Security system" |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules across the panel; the only vertical rule is the dashed 2016 marker |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | horizontal grid lines only, no vertical grid between year ticks |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | f1 | **无** | 2015-2017 segments of all three lines drawn dashed, keyed as "Methodological change" |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | f2 | **无** | 2015-2017 segments dashed while later segments are solid |

词表 65 项，本页出现 12 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `dash_style_legend_note` | page | a small key below the sources: "– – –  Methodological change." explaining the dashed segments | 虚线段的含义写在图外的小注中，读者需把线型与该注解对应才知2015-2017数据不可直接比较。 |
| `partial_series_dashing` | page | the same series switches from dashed to solid at 2017 within one line | 线型在同一条序列内变化，取值时不能靠线型区分序列，必须靠颜色与图例。 |
| `label_offset_alternating` | f1 | Workforce labels sit above points, Revenue labels below, to avoid overlap near 129/129 | , |
| `grid_without_ticks` | f2 | roughly ten horizontal grid lines drawn but no tick labels anywhere on them | 网格线无数值刻度，任何未打印标签的点都无法定量读出，只能依赖打印数字。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部打印在图上（198、93、14.1%、3.9%），读数不成问题；两图都没有数值轴刻度，所以能否定位靠标签。难点在寻址：3.9%在下图同一序列的2022与2023各出现一次，93在上图Productivity序列的2020与2021各出现一次，必须同时给出序列名（其中一个长达十余词的"Third-party employees registered with the Spanish Social Security system"）和年份两把钥匙才能唯一确定；再加上两图无编号、标题相似度高（都以2015-2024为横轴），表格若不带标题行就无法区分上下图的同名年份列。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | no_value_axis 与 value_label_outside 的组合条件行 | 样式字段：value_axis 设为隐藏刻度但保留水平网格，同时强制打印所有点标签 | 无数值刻度且全部点标签外置的折线图 vs 有刻度无标签，比较取值命中率 |
| new | 一类出版方 | 新组件 partial_series_dashing / dash_style_legend_note | 记录字段：为每条序列增加分段线型区间及其图外注解文本 | 同一序列内线型分段（含图外线型注解）vs 单一线型，检验序列识别是否退化 |
| P7 | 通用 | P7 的 unit/subtitle 拆分，覆盖 "(2015= base of 100)" 这类基准短语 | 条件行：heading 拆成 title / subtitle / unit_text，且允许 figure_number 为空 | 无编号图 + 基准短语位于副标题 vs 编号图 + 独立单位行，检验上下文命中 |
| P3 | 一类出版方 | 长序列名换行（wrapped_category_labels 用于图例） | 样式字段：legend_below_plot 允许条目内换行并限定列宽 | 图例条目换行的长序列名 vs 短名，检验寻址键是否被截断 |
