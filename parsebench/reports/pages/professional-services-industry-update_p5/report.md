# professional-services-industry-update_p5

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| professional-services-industry-update | `untagged` | 4 | 0 |

这是KPMG专业服务并购市场评论页，上半部分为一个无数值轴、全部数值直接打印的季度交易量柱状图（下方蓝色条带另列交易金额），下半部分为近期交易的文字卡片列表。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 1,153 | `2024` · `Q2` · `Deal Volume (#)` | 1% | f1 | the last bar, Q2 2024 deal volume | 是 | `Q2` · `2024` · `Deal Volume (# of transactions)` |
| 2 | $56.8 | `2024` · `Q2` · `Deal Value ($)` | 1% | f1 | the last entry in the blue value strip, Q2 2024 deal value | 是 | `Q2` · `2024` · `Deal Value ($ in bn)` |
| 3 | 1,527 | `2022` · `Q1` · `Deal Volume (#)` | 1% | f1 | the eighth bar, Q1 2022 deal volume | 是 | `Q1` · `2022` · `Deal Volume (# of transactions)` |
| 4 | $28.1 | `2024` · `Q1` · `Deal Value ($)` | 1% | f1 | the sixteenth entry in the blue value strip, Q1 2024 deal value | 是 | `Q1` · `2024` · `Deal Value ($ in bn)` |

**程序核对**（模型没有看到左半的标签列）：

- 规则需要的键比模型报出的图能提供的多——rules need 3 keys, the richest figure offers 2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 1 | 2 | 17 | 17 | 全部 | （不画值轴） |

- **f1** Professional Services Announced Deal Volume and Value(1)　[图上方]　单位 `Deal Volume (# of transactions); Deal Value ($ in bn)`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or gridlines anywhere; bars sit on a blue band, numbers only readable from printed labels |
| `source_note_lines` | source / note 行在图下方 | page | 有 | '(1) Market statistics sourced from Capital IQ, Merger Market, Pitchbook, Wall Street research, press releases. Notes: ...' |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | line above plot: 'Deal Volume (# of transactions); Deal Value ($ in bn)'; bars carry bare counts |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | heading reads 'Professional Services Announced Deal Volume and Value(1)' with superscript (1) |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | 806, 1,090, 1,398, 1,528 printed in white inside the top of each blue bar |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | inner row Q2 Q3 Q4 Q1..., outer row 2020 2021 2022 2023 2024, separated by rule boxes |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | time written as bare 'Q2', 'Q3', 'Q4' with the year only in the grouping row below |
| `total_row_below_axis` | 轴下方一行合计值，与类目对齐 | f1 | **无** | blue strip under the bars prints $24.9, $81.3, $141.3 ... $28.1, $56.8 aligned to each bar |

词表 65 项，本页出现 8 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `series_as_text_row_only` | f1 | Deal Value series never drawn as a mark; it exists only as $ text in the blue strip | 第二组数据（$24.9…$56.8）没有任何图形标记，只能作为文本行读取，表格必须为它单列一行而非从柱高推算。 |
| `series_names_only_in_subtitle` | f1 | no legend; both series named once in 'Deal Volume (# of transactions); Deal Value ($ in bn)' | 要区分1,153与$56.8属于哪一系列，只能回到图上方那一行文字，标签不在标记附近。 |
| `implicit_baseline_under_value_band` | f1 | bar bottoms are covered by the value strip; no zero line or axis is visible | 柱底被遮住且无刻度，柱高与数值不成可验证比例，读数只能靠打印标签。 |
| `axis_row_drawn_as_table_cells` | f1 | quarter and year labels sit in bordered boxes forming a grid under the bars | 类别轴呈表格状，解析器可能把季度/年度行当成表格头，影响行键的拼接方式。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

四个目标值全部以文字印在图上（1,153、$56.8、1,527、$28.1），读数误差为零，所以第2步不构成障碍；难点是寻址：季度标签只有'Q1'…'Q4'且在17个槽位中重复4–5次，必须与下方分组行'2020…2024'拼合才能唯一定位（Q1单独出现4次，Q2出现5次）；同时两个系列的名称只在图上方一行'Deal Volume (# of transactions); Deal Value ($ in bn)'中出现，没有图例，$28.1与1,096同属Q1 2024这一列，若表格不区分系列行就无法把值指向唯一标记。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 series_as_text_row_only（可与 total_row_below_axis 配对） | 图表样式条件行中增加"第二系列仅以数值文本条带呈现、不绘制标记"的开关，并在记录字段中为该文本行单独保存系列名与单位 | 文本条带系列 开/关：比较"两系列均绘制标记"与"一系列仅为文本行"时值-标签配对准确率 |
| P3 | 通用 | two_level_x_ticks 与重复季度标签（nonstandard_time_ticks）的组合 | 类别轴样式字段：内层季度标签+外层年份分组行，并带单元格边框 | 单层时间轴 vs 两层（季度/年份）轴：统计需要两个键才能唯一寻址时的命中率 |
| P1 | 一类出版方 | no_value_axis + 全量 value_label_inside 的组合（无刻度、柱底被遮） | 值轴条件行：允许"不绘制值轴、数值全部内嵌于标记"，并记录基线是否可见 | 有刻度轴 vs 无刻度仅标签：检验读数精度指标在没有轴时如何退化为标签抽取任务 |
| P7 | 通用 | 标题拆分：无编号标题 + 上标脚注 (1) + 单位行独立于标题 | 标题记录字段拆为 number/title/subtitle/unit_text/placement，并支持标题内脚注标记 | 单位在独立行 vs 单位并入标题：检验单位与系列名归属的抽取正确率 |
