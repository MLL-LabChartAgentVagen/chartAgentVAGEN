# (Web_version)_E-Government_Survey_2024_1392024_p94

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| (Web_version)_E-Government_Survey_2024_1392024 | `untagged` | 5 | 0 |

本页为《联合国电子政务调查》第2章第69页，含表2.8（各区域移动数据/语音可负担性、移动宽带与蜂窝订阅数及互联网使用率，2022与2024）与图2.28（2022-2024年全球与区域互联网使用率、移动宽带及蜂窝订阅百分比变化的分组柱状图）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 27.3 | `Africa` · `Percentage change in active mobile broadband subscriptions per 100 inhabitants` | 1% | f2 | the Africa bar in the "Percentage change in active mobile broadband subscriptions per 100 inhabitants" group | 是 | `Figure 2.28` · `Percentage change in active mobile broadband subscriptions per 100 inhabitants` · `Africa` |
| 2 | 0.1 | `Asia` · `Percentage change in mobile cellular telephone subscriptions per 100 inhabitants` | 1% | f2 | the Asia bar in the "Percentage change in mobile cellular telephone subscriptions per 100 inhabitants" group | 是 | `Figure 2.28` · `Percentage change in mobile cellular telephone subscriptions per 100 inhabitants` · `Asia` |
| 3 | 49.0 | `Oceania` · `Percentage change in Internet usage among individuals` | 1% | f2 | the Oceania bar in the "Percentage change in Internet usage among individuals" group | 是 | `Figure 2.28` · `Percentage change in Internet usage among individuals` · `Oceania` |
| 4 | -1.8 | `Oceania` · `Percentage change in active mobile broadband subscriptions per 100 inhabitants` | 1% | f2 | the Europe bar in the "Percentage change in active mobile broadband subscriptions per 100 inhabitants" group, below zero | 是 | `Figure 2.28` · `Percentage change in active mobile broadband subscriptions per 100 inhabitants` · `Europe` |
| 5 | 15.4 | `193 UN Member States` · `Percentage change in Internet usage among individuals` | 1% | f2 | the "193 UN Member States" bar in the "Percentage change in Internet usage among individuals" group | 是 | `Figure 2.28` · `Percentage change in Internet usage among individuals` · `193 UN Member States` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 5 predicted key sets miss a rule label: -1.8

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `other · data table` | na | 1 | 4 | 6 | 48 | 全部 | （不画值轴） |
| f2 | `grouped_bar` | vertical | 1 | 6 | 3 | 18 | 全部 | -10, 0, 10, 20, 30, 40, 50, 60 |

- **f1** Table 2.8 / Affordability of mobile data and voice services, mobile broadband and cellular subscriptions per 100 inhabitants, and percentage of individuals using the Internet, by region, 2022 and 2024　[图上方]　单位 `Mobile data and voice high consumption basket price (as a percentage of GNI per capita)`
  - 来源行：Sources: ITU, Statistics for individuals using the Internet (2022 and 2024), available at https://www.itu.int/en/ITU-D/Statistics/Pages/stat/default.aspx; ITU, "Mobile data and voice high-consumption basket", DataHub, available at https://datahub.itu.int/data/?i=34619.
- **f2** Figure 2.28 / Percentage change at the global and regional levels in Internet usage and in active mobile broadband and mobile cellular subscriptions per 100 inhabitants, 2022-2024　[图上方]　（标题里没有单位）
  - 来源行：Sources: 2022 and 2024 United Nations E-Government Surveys.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f2 | 有 | six coloured bars side by side within each of the three category slots |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f2 | **无** | a zero baseline is drawn across the plot with bars going above and one below it |
| `negative_values` | 负值 / 零线居中的分叉条 | f2 | **无** | Europe bar in first group drops below the zero line, labelled "-1.8"; axis tick "-10" |
| `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | f1 | **无** | the "2022" affordability column shows "-" for Africa, Americas, Asia, Europe, Oceania and 193 UN Member States |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | "Table 2.8" with its own caption above and "Figure 2.28" with its own caption below on the same page |
| `source_note_lines` | source / note 行在图下方 | page | 有 | "Sources: ITU, Statistics for individuals using the Internet..." and "Sources: 2022 and 2024 United Nations E-Government Surveys." |
| `legend_inside_plot` | 图例画在绘图区内部 | f2 | **无** | legend row "Africa Americas Asia Europe Oceania 193 UN Member States" drawn inside the plot frame near 50-60 |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f1 | 有 | bordered table with shaded header rows, captioned "Table 2.8 Affordability of mobile data and voice services..." |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | column header "Mobile data and voice high consumption basket price (as a percentage of GNI per capita)" |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | numbers "27.3", "10.4", "49.0", "-1.8" printed above (or below) the bar tops, not inside |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | header band "Affordability" over "Mobile data and voice high consumption basket price...", then a "2024 / 2022" row beneath each |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f2 | **无** | category labels wrap onto three lines, e.g. "Percentage change in active mobile broadband subscriptions per 100 inhabitants" |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the last row "193 UN Member States" and its numbers are set in bold |

词表 65 项，本页出现 13 项，其中我们画不出来的 9 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `legend_series_reused_as_table_rows` | page | Figure 2.28 legend entries "Africa ... 193 UN Member States" are the same labels as Table 2.8 row headers | 读数时须区分表格行标签与图例系列名同名的情况，取值必须同时指定图号与类别组，否则会与表2.8的数字混淆。 |
| `year_subcolumns_per_indicator` | f1 | each indicator header spans two sub-columns headed "2024" and "2022" | 一个数值需要指标名＋年份＋区域三个键才能唯一定位，缺一个就会指向另一格。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

五个待查值全部印在柱顶，读数不成问题（网格刻度每10单位，标注已给到0.1）。真正的障碍是定位：图2.28每个值需要三个键——类别组（三段长达三行的换行标签，如"Percentage change in active mobile broadband subscriptions per 100 inhabitants"）＋系列名（六个区域）＋图号，且系列名与表2.8的行名完全重合（Africa…193 UN Member States），同时0.1与2.5等小值紧邻，解析器若只输出两列表格就无法把15.4与表2.8中的数字区分开。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | grouped_bar 配合 wrapped_category_labels：生成三个换行三行的长类别标签＋六系列分组柱 | 样式字段中的类别标签换行策略与分组数（series=6, categories=3） | 新增一行：长换行类别标签下分组柱的类别键还原率（换行 vs 单行） |
| P6 | 通用 | negative_values 与零基准线（单个负柱及其标签置于柱下方） | 值域配置：允许负值并把 value_label_outside 在负柱时改为下方对齐 | 新增一行：含负柱时标签位置（上/下）对值符号识别的影响 |
| P3 | 一类出版方 | 新组件 year_subcolumns_per_indicator（表格式图：指标跨列＋年份子列＋"-"缺失符） | 记录字段中增加二级表头（指标→年份）与缺失值标记 | 新增一行：三键（指标＋年份＋区域）定位时的单元格命中率 |
| P3 | 一类出版方 | legend_inside_plot（图例置于绘图区内部顶端） | 图例放置条件行：inside 与 below/above 的对比 | 新增一行：图例位于绘图区内部时系列名与柱的绑定正确率 |
