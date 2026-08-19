# investing-in-education-2025-NC0125093ENN-1_p14

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| investing-in-education-2025-NC0125093ENN-1 | `need_estimate` | 10 | 10 |

本页含两个图：Figure 6 为 EU-27 教育公共支出名义与实际值的指数折线图（2007=100），Figure 7 为按功能分类的公共支出占比表格，下方为一段正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 100 | `2007` · `Nominal` | 1% | f1 | the 2007 Nominal point (both series start at 100) | 否 | `Nominal` · `2007` · `index 2007=100` |
| 2 | 100 | `2007` · `Real` | 1% | f1 | the 2007 Real point | 否 | `Real` · `2007` · `index 2007=100` |
| 3 | 110 | `2010` · `Nominal` | 1% | f1 | the 2010 Nominal point, on the 110 gridline | 否 | `Nominal` · `2010` · `index 2007=100` |
| 4 | 116 | `2015` · `Nominal` | 5% | f1 | the 2015 Nominal point, just above the 115 level | 否 | `Nominal` · `2015` · `index 2007=100` |
| 5 | 105 | `2015` · `Real` | 5% | f1 | the 2015 Real point, midway between 100 and 110 | 否 | `Real` · `2015` · `index 2007=100` |
| 6 | 130 | `2019` · `Nominal` | 5% | f1 | the 2019 Nominal point, on the 130 gridline | 否 | `Nominal` · `2019` · `index 2007=100` |
| 7 | 109 | `2019` · `Real` | 5% | f1 | the 2019 Real point, just under the 110 gridline | 否 | `Real` · `2019` · `index 2007=100` |
| 8 | 148 | `2022` · `Nominal` | 5% | f1 | the 2022 Nominal point, just below 150 | 否 | `Nominal` · `2022` · `index 2007=100` |
| 9 | 159 | `2023` · `Nominal` | 5% | f1 | the 2023 Nominal point, the top-right end of the line | 否 | `Nominal` · `2023` · `index 2007=100` |
| 10 | 115 | `2023` · `Real` | 5% | f1 | the 2023 Real point, the right end of the red line | 否 | `Real` · `2023` · `index 2007=100` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 2 | 17 | 34 | 无 | 100, 110, 120, 130, 140, 150, 160 |
| f2 | `other · data table` | na | 1 | 6 | 10 | 60 | 全部 | （不画值轴） |

- **f1** Figure 6. / Evolution of nominal and real public expenditure on education in the EU-27 (index 2007=100)　[图上方]　单位 `index 2007=100`
  - 来源行：Source:    European Commission services' calculations based on Eurostat COFOG data and AMECO data
- **f2** Figure 7. / Public expenditure by function (2019-2023)　[图上方]　单位 `% of total`
  - 来源行：Source:    Eurostat COFOG data. Online data code: [gov_10a_exp].

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `negative_values` | 负值 / 零线居中的分叉条 | f2 | **无** | change column shows "-0.1", "-0.3", "-0.4", "-1.9" |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest y tick printed is "100", not zero |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | "Figure 6." line chart and "Figure 7. Public expenditure by function (2019-2023)" table, separate captions |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Notes:  Real values are expressed at 2015 constant prices..." and "Source: European Commission services' calculations..." |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | "Source:    Eurostat COFOG data. Online data code: [gov_10a_exp]." under the table |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | "Nominal" and "Real" markers in a row centred below the x tick row |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f2 | 有 | bordered table with year column headers, captioned "Figure 7. Public expenditure by function (2019-2023)" |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f2 | **无** | "Online data code: [gov_10a_exp]" hyperlinked under the table |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | y axis shows bare 100-160; the scale word "index 2007=100" sits only in the title |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | column subheaders "% of total" and "percentage point change" carry the scale |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | title reads "(index 2007=100)" and both lines start at 100 in 2007 |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f2 | **无** | row labels such as "Housing and community amenities", "Recreation, culture and religion" run long in one column |
| `panel_background` | 绘图区带底色，不是白底 | f2 | **无** | alternating light-lilac row fills across the table body |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | dashed horizontal rules at 100 through 160, no vertical rules in the plot |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f2 | **无** | last column header "2019-2023 percentage point change" filled orange, unlike the red year headers |

词表 65 项，本页出现 13 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `two_level_column_headers` | f2 | header band has year "2019" above "% of total" in each column, two stacked rows | 读一个数值需要同时用年份和"% of total"两级列标题定位，单层表头无法唯一寻址。 |
| `marker_on_line_series` | f1 | 每个年份点上都画有圆形/方形标记，标记与线同色 | 标记明确了每年一个数据点的位置，便于在无数值标签时按刻度读数。 |
| `note_line_defines_series_meaning` | f1 | "Notes: Real values are expressed at 2015 constant prices by using the price deflator..." | "Real"这一系列的口径只在注释里说明，表格若丢失注释就无法区分两条线的含义。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

所有被评分的10个数值都来自 Figure 6，而该折线图完全没有数值标签，y 轴刻度间隔为10（100…160），5% 容差在110附近只有约±5.5、在159附近约±8，但要区分"105"与"109"这类同一系列相邻年份的值，必须在两条相距10单位的网格线之间做四分之一格的像素判读；再加上 y 轴从100起始且17个年份点密集排列（2010-2012 段名义值几乎平坦，110/111/110），解析器要把每个点读到个位数几乎不可能。相比之下标签只需"Nominal/Real + 年份"两个键，表格容易承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | rebased_index_values 与 axis_starts_above_zero 组合 | 折线图样式条件行：轴起点不为零且标题写明索引基期 | 新增"索引型折线（基期=100、轴起点=100）无数值标签"一行，检验模型是否会把轴起点误当零点 |
| P3 | 通用 | 两级列表头（two_level_column_headers）作为新组件 | data_table_as_figure 的表头字段，允许年份行 + 单位行两层 | 新增"表格类图形两级列表头 vs 单级表头"一行，检验寻址键数量对导出正确率的影响 |
| P7 | 一类出版方 | note_line_defines_series_meaning（注释定义系列口径） | 记录字段中的 notes 行，与 source 行分开存储 | 新增"含 Notes 行 vs 仅含 Source 行"一行，检验系列语义是否随注释丢失 |
| P5 | 通用 | sparse 与 dense 时间轴之间的中间档：17 个年份点全部标注刻度 | 时间轴刻度密度条件行 | 新增"每点一刻度但点间距<25px"一行，把刻度拥挤度作为可控变量 |
