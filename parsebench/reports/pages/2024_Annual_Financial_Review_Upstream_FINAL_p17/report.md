# 2024_Annual_Financial_Review_Upstream_FINAL_p17

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2024_Annual_Financial_Review_Upstream_FINAL | `need_estimate` | 10 | 10 |

该页为EIA财务评论幻灯片，含一幅无编号的堆积柱状图（2015–2024年各年探明储量增加量，含负值与灰点总量标记）以及右侧灰底说明文字栏。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 18.0 | `2024` · `total crude oil and natural gas reserve additions` | 5% | f1 | the 2024 total crude oil and natural gas reserve additions grey marker (~18) | 否 | `2024` · `total crude oil and natural gas reserve additions` · `Proved reserve additions for select energy companies` · `billion barrels of oil equivalent` |
| 2 | 12.5 | `2024` · `extensions and discoveries` | 5% | f1 | the 2016 extensions and discoveries segment, running from ~0.4 up to the bar top near 13 | 否 | `2016` · `extensions and discoveries` · `Proved reserve additions for select energy companies` |
| 3 | 5.0 | `2024` · `revisions` | 5% | f1 | the 2024 revisions segment, the dark block from 0 up to about 5 | 否 | `2024` · `revisions` · `Proved reserve additions for select energy companies` |
| 4 | 31.0 | `2021` · `total crude oil and natural gas reserve additions` | 5% | f1 | the 2021 total crude oil and natural gas reserve additions marker / stack top just above 30 | 否 | `2021` · `total crude oil and natural gas reserve additions` · `Proved reserve additions for select energy companies` |
| 5 | 14.0 | `2021` · `revisions` | 5% | f1 | the 2021 revisions segment, dark block from 0 to about 14 | 否 | `2021` · `revisions` · `Proved reserve additions for select energy companies` |
| 6 | 16.0 | `2015` · `extensions and discoveries` | 5% | f1 | the 2015 positive stack top (extensions and discoveries segment reaching ~16) | 否 | `2015` · `extensions and discoveries` · `Proved reserve additions for select energy companies` |
| 7 | -14.0 | `2015` · `revisions` | 5% | f1 | the 2015 revisions segment extending below zero to about -14 | 否 | `2015` · `revisions` · `Proved reserve additions for select energy companies` |
| 8 | 1.5 | `2017` · `improved recovery` | 5% | f1 | the small positive block above zero in 2020, read as improved recovery (~1.5); could also be the 2019 one | 否 | `2020` · `improved recovery` · `Proved reserve additions for select energy companies` |
| 9 | -1.0 | `2020` · `total crude oil and natural gas reserve additions` | 5% | f1 | the shallow 2019 revisions segment below zero (~-1); the 2020 grey total marker sits at a similar depth | 否 | `2019` · `revisions` · `Proved reserve additions for select energy companies` |
| 10 | 20.0 | `2018` · `extensions and discoveries` | 5% | f1 | the 2022 total crude oil and natural gas reserve additions marker / stack top near 19-20 | 否 | `2022` · `total crude oil and natural gas reserve additions` · `Proved reserve additions for select energy companies` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: 12.5, 1.5, -1.0, 20.0

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 4 | 10 | 40 | 无 | 35, 30, 25, 20, 15, 10, 5, 0, -5, -10, -15, -20 |
| f1 | `other · duplicate entry` | na | 1 | 0 | 0 | 0 | 无 | （不画值轴） |

- **f1** Proved reserve additions for select energy companies　[图上方]　单位 `billion barrels of oil equivalent`
  - 来源行：Data source: Evaluate Energy
- **f1** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each year's bar is built of gold, brown and near-black segments labelled extensions/improved recovery/revisions |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | grey round markers sit over each year's bar for "total crude oil and natural gas reserve additions" |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a heavy black horizontal rule is drawn at 0 across the whole plot width |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | 2015, 2016, 2019 and 2020 dark segments run below the baseline; ticks read -5, -10, -15, -20 |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Data source: Evaluate Energy" and "Note: Select energy companies includes 158 global oil and natural gas companies." |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f1 | 有 | the four series names form a column at the right edge of the plot band, level with the bars |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f1 | **无** | grey-tinted column right of the plot: "Organic proved reserve additions create new proved reserves from improved recovery..." |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | "billion barrels of oil equivalent" under the bold heading; value axis shows bare 35, 30 ... -20 |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | "improved recovery" band is a few pixels tall in 2022-2024, its name pushed outside to the right |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | f1 | **无** | colour-matched texts "extensions and discoveries", "improved recovery", "revisions" set beside the bars, no swatch legend |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | thin horizontal rules at every 5-unit tick, no vertical rules in the plot |

词表 65 项，本页出现 11 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `stack_spans_zero_with_total_marker` | f1 | revisions segments go below 0 while other segments go above; grey dot marks the net total instead of bar length | 柱长不再等于总量，读取任一分段都要分别定位零线上下的端点，总量只能由灰点读出。 |
| `headline_states_data_value` | f1 | slide title: "...totaled 18 billion barrels in 2024" restates the 2024 total marker value | 18这个数只写在页标题里而非图上，取值须把标题文字与2024年灰点对应起来。 |
| `series_label_leader_to_marker` | f1 | short horizontal rules run from "total crude oil and natural gas reserve additions" text toward the 2024 grey dots | 该系列名靠引出线而非色块与标记关联，解析时容易把它当作独立文字块而丢失系列身份。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数字标注，网格线间隔为5个单位（约38像素），要在5%误差内读数，1.5这类小分段容许误差只有±0.08（约0.6像素），2022–2024年的"improved recovery"带只有几像素高，根本无法分辨；另外堆积段必须由累积端点相减才能得到（如2016年12.5=柱顶12.9减去下方约0.4），而柱长又被零线上下的正负段拆开，总量只能由灰点单独读取。相比之下年份与系列名齐备（步骤3尚可），标题也是加粗文本（步骤4较轻）。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | stack_spans_zero_with_total_marker（新组件）与 negative_values + mixed_marks 的组合 | 条件行中新增"堆积柱跨零线且总量以散点标记"的样式字段，记录字段需分别存正段、负段与总量 | 跨零堆积（总量≠柱长）与常规同号堆积对比的取值准确率一行 |
| P6 | 一类出版方 | inline_series_labels / legend_beside_plot 的无色块彩色文字系列标注（含引出线） | 图例样式字段：位置=beside，形式=彩色文字无色块，可带引出线 | 系列名以色块图例 vs 彩色文字侧标注时，系列键被正确还原的比例一行 |
| P7 | 通用 | unit_in_axis_or_title：标题下独立的一行单位（"billion barrels of oil equivalent"） | 标题记录拆为 number/title/subtitle/unit_text/placement 五段，unit 单独成行置于标题下方 | 单位独立成行 vs 嵌入标题时，导出表能否携带刻度含义一行 |
| P3 | 这份文档自己的习惯 | side_text_bullets：图右侧灰底说明文字栏与图共占一个横带 | 页面版式行：图形宽度收窄并在右侧生成正文列，整页 markdown 导出需保持文字与表分离 | 有/无并列文字栏时，图表标题与表格相邻关系被正确导出的一行 |
| new | 一类出版方 | headline_states_data_value（新组件）：页标题内含图中数值"18 billion barrels in 2024" | 页级标题模板：允许标题句中嵌入某一标记的数值 | 关键值仅出现在页标题（不在图上）时能否被定位到对应标记的一行 |
