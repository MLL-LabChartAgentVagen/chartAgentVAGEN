# (Web_version)_E-Government_Survey_2024_1392024_p63

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| (Web_version)_E-Government_Survey_2024_1392024 | `untagged` | 5 | 0 |

该页含图2.3（2022与2024全球及区域EGDI平均值的分组柱状图，带增长率箭头标注和全球平均参考虚线）以及表2.1（EGDI及其分项指数的全球与区域平均值表格）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 0.6382 | `193 UN Member States` · `2024` | 1% | f1 | the 2024 green bar for 193 UN Member States (also printed in Table 2.1 EGDI 2024 row) | 是 | `193 UN Member States` · `2024 for 193 UN Member States, Africa, Americas, Asia, Europe and Oceania` · `EGDI` · `2024` |
| 2 | 0.4054 | `Africa` · `2022` | 1% | f1 | the 2022 grey bar for Africa (also Table 2.1 Africa / 2022 / EGDI) | 是 | `Africa` · `2022` · `EGDI` |
| 3 | 0.6701 | `Americas` · `2024` | 1% | f1 | the 2024 purple bar for Americas (also Table 2.1 Americas / 2024 / EGDI) | 是 | `Americas` · `2024` · `EGDI` |
| 4 | 0.6493 | `Asia` · `2022` | 1% | f1 | the 2022 grey bar for Asia (also Table 2.1 Asia / 2022 / EGDI) | 是 | `Asia` · `2022` · `EGDI` |
| 5 | 0.8493 | `Europe` · `2024` | 1% | f1 | the 2024 navy bar for Europe (also Table 2.1 Europe / 2024 / EGDI) | 是 | `Europe` · `2024` · `EGDI` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——5 values given, 6 answered
- 系列数与系列名个数不一致——f1: series=8, 3 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 1 | 8 | 6 | 13 | 全部 | 0, 0.25, 0.5, 0.75, 1 |
| f2 | `other · data table` | na | 1 | 4 | 6 | 84 | 全部 | （不画值轴） |

- **f1** Figure 2.3 / Global and regional EGDI averages, 2022 and 2024　[图上方]　（标题里没有单位）
  - 来源行：Sources: 2022 and 2024 United Nations E-Government Surveys.
- **f2** Table 2.1 / Average global and regional values for the EGDI and its component indices, 2022 and 2024　[图上方]　（标题里没有单位）
  - 来源行：Sources: 2022 and 2024 United Nations E-Government Surveys.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | each category has a grey 2022 bar beside a coloured 2024 bar |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | dotted horizontal rule with legend 'Linear (global EGDI average 2024)' |
| `negative_values` | 负值 / 零线居中的分叉条 | f2 | **无** | HCI change column shows '-7.2%', '-12.1%', '-8.3%', '-4.8%', '-4.6%', '-9.5%' |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | green up-arrows with '4.6%', '4.8%', '4.1%', '7.7%', '2.3%', '4.1%' over the bars |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | each region's 2024 bar has its own colour: green, orange, purple, yellow, navy, blue |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | 'Figure 2.3' and 'Table 2.1' each numbered with own caption and source |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Sources: 2022 and 2024 United Nations E-Government Surveys.' under the plot |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | 'Sources: 2022 and 2024 United Nations E-Government Surveys.' under the table |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | '2022', dotted key and colour swatch row sit under the category axis |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f2 | 有 | bordered table headed 'Table 2.1' with 'Average values for:' / EGDI / OSI / TII / HCI |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | '0.6382', '0.4247', '0.6701' printed inside the coloured 2024 bars; 2022 values printed at bar base |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | '193 UN Member States' wraps onto two lines under the axis |
| `panel_background` | 绘图区带底色，不是白底 | f2 | **无** | table cells tinted green and pink instead of white |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f2 | **无** | '193 UN Member States' row set in bold with bold 2024/2022 values |

词表 65 项，本页出现 13 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `legend_entry_lists_multiple_swatches` | f1 | one legend row shows six colour swatches labelled '2024 for 193 UN Member States, Africa, Americas, Asia, Europe and Oceania' | 六个颜色共享一个图例标签，无法从图例逐一对应到某个区域，读值时必须靠柱子位置而非图例来定序列。 |
| `growth_rate_as_secondary_quantity` | f1 | arrow labels '4.6%', '7.7%' give percent change, not values on the 0-1 axis | 同一图内混有两种量纲（指数值与百分比变化），提取时须区分哪一数字属于纵轴刻度。 |
| `paired_year_rows_in_table` | f2 | each region row splits into '2024' and '2022' sub-rows across four index blocks | 定位一个数值需要区域名＋年份＋指数名三个键，表格行标签必须携带合并单元格信息。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身不难：五个被考数值都以四位小数直接印在柱上，且在表2.1中重复出现，读数误差为零，所以第2步不成问题。真正的瓶颈是标签：图2.3中同一年份的六个2024柱共用一条图例文字“2024 for 193 UN Member States, Africa, Americas, Asia, Europe and Oceania”，而0.6382与0.6102分别属于同一类别的两根柱，必须同时给出类别名（含换行的“193 UN Member States”）和年份两个键；到表2.1则还要再加“EGDI/OSI/TII/HCI”这一层列分组，即区域＋年份＋指数三键才能唯一定址，且区域名与年份在原表中是合并单元格，解析后极易丢失年份键，使0.4054与0.6102等同列数值互相混淆。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | 新组件 legend_entry_lists_multiple_swatches | 图例样式字段：允许一条图例文字对应多个色块（swatch 数 > 1） | 图例色块与标签一对多 vs 一对一，比较序列定址正确率 |
| P3 | 通用 | 新组件 paired_year_rows_in_table（表格式图的合并行键） | 记录字段：行键拆为 region + year 两级，列键拆为 index 分组 | 两级行键+两级列键的表 vs 单级键表的定址成功率 |
| P6 | 一类出版方 | annotation_callout 中的增长率箭头（与纵轴不同量纲的第二量） | 标注样式字段：为每根柱加可选的 delta 标注（箭头+百分比） | 含/不含第二量纲标注时，主数值抽取的混淆率 |
| P6 | 这份文档自己的习惯 | value_label_inside 与柱底外部标签并存的双位置标注 | 样式维度 value-label placement：同一图内 2022 系列标签在柱底、2024 系列在柱内 | 同图内标签位置按系列分化 vs 统一位置 |
| P7 | 通用 | unit_text 为空但数值为 0–1 指数的标题字段建模 | 标题字段：figure_number / title / subtitle / unit 四分，unit 允许为空 | 无单位行的图与有单位行的图，单位恢复率对比 |
