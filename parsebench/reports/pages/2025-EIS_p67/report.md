# 2025-EIS_p67

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2025-EIS | `need_estimate` | 10 | 10 |

该页为《European Innovation Scoreboard 2025》第65页，上方是浅蓝底的国家表现文字框，中部为Figure 25（Moderate Innovators 表现，左右两个折线面板），下方是斜体Note和"Emerging Innovators"正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 99.7 | `Malta` · `'23` | 5% | f1 | a point on the unnamed average line in the left panel, at the '23/'24 plateau near 100 | 否 | `Figure 25: Performance Moderate Innovators` · `Summary innovation index` · `'24` |
| 2 | 106.4 | `Slovenia` · `'25` | 5% | f1 | the highest 2025 endpoint in the right panel, the line labelled Malta | 否 | `Figure 25: Performance Moderate Innovators` · `Malta` · `'25` |
| 3 | 102.6 | `Italy` · `'21` | 5% | f1 | a 2025 endpoint in the upper label cluster of the right panel, the line labelled Slovenia | 否 | `Figure 25: Performance Moderate Innovators` · `Slovenia` · `'25` |
| 4 | 102.4 | `Spain` · `'24` | 5% | f1 | a 2025 endpoint immediately below the previous one, the line labelled Italy | 否 | `Figure 25: Performance Moderate Innovators` · `Italy` · `'25` |
| 5 | 92.8 | `Portugal` · `'22` | 5% | f1 | a 2025 endpoint in the middle label cluster of the right panel; at this resolution it cannot be pinned between Portugal, Cyprus and Lithuania | 否 | `Figure 25: Performance Moderate Innovators` · `Portugal` · `'25` |
| 6 | 109.9 | `Cyprus` · `'23` | 5% | f1 | the Cyprus line at its '23 peak in the right panel; the number itself appears only in the blue text box ("peaking in 2023 (109.9)") | 否 | `Figure 25: Performance Moderate Innovators` · `Cyprus` · `'23` |
| 7 | 73.8 | `Lithuania` · `'18` | 5% | f1 | the Lithuania line's '18 starting point in the right panel | 否 | `Figure 25: Performance Moderate Innovators` · `Lithuania` · `'18` |
| 8 | 90.8 | `Czechia` · `'25` | 5% | f1 | the Czechia line's '25 endpoint in the right panel | 否 | `Figure 25: Performance Moderate Innovators` · `Czechia` · `'25` |
| 9 | 88.2 | `Greece` · `'24` | 5% | f1 | the Greece line's '24 point in the right panel | 否 | `Figure 25: Performance Moderate Innovators` · `Greece` · `'24` |
| 10 | 61.2 | `Croatia` · `'18` | 5% | f1 | the Croatia line's '18 starting point, the lowest mark in the right panel | 否 | `Figure 25: Performance Moderate Innovators` · `Croatia` · `'18` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 10 predicted key sets miss a rule label: 99.7, 106.4, 102.6, 102.4, 92.8
- 面板数与面板名个数不一致——f1: panels=2, 0 names
- 系列数与系列名个数不一致——f1: series=11, 10 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 2 | 11 | 8 | 88 | 无 | 50, 60, 70, 80, 90, 100, 110, 120 |

- **f1** Figure 25 / Performance Moderate Innovators　[图上方]　单位 `Summary innovation index`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest tick on both panels is "50" with no break glyph on the axis |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | italic four-line "Note: Performance is relative to that of the EU in 2018..." below the plots |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | left panel is one average line, right panel ten member-state lines under one figure number |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis ticks are bare 50–120; only "Summary innovation index" names the scale |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "Summary innovation index" set vertically along the y axis of both panels |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | Note: "Performance is relative to that of the EU in 2018" under the plot |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | x ticks read "'18", "'19", "'20", "'21", "'22", "'23", "'24", "'25" |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | f1 | **无** | right panel has no legend; "Malta", "Slovenia", "Italy", "Spain", "Portugal", "Cyprus", "Lithuania", "Czechia", "Greece", "Croatia" printed at line ends |

词表 65 项，本页出现 8 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `aggregate_panel_beside_members_panel` | f1 | Note: "The graph on the left shows the average performance of the Moderate Innovators"; right panel shows each state | 左面板的线没有任何系列名（只是组平均），取值时必须用"average of the Moderate Innovators"这类注释文字来定位，而不能靠图例或标签。 |
| `crowded_endpoint_label_stack` | f1 | "Malta/Slovenia/Italy/Spain/Portugal" labels stack and touch at right edge, matched to lines by colour only | 标签互相挤压且与线端点错位，读某一国2025年的点必须靠颜色配对，容易把102.6与102.4张冠李戴。 |
| `cross_figure_axis_span_note` | f1 | Note: "All vertical scales in Figure 23–Figure 26 span a range of 70.0%-points" | 说明纵轴范围是跨图统一约定（50–120共70点），提示不能按面板自适应缩放来估算刻度。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

右面板10条线在'23–'25之间全部挤进100–110这一格半的空间里，纵轴刻度间隔为10点，5%容差在100附近约为5点，即半格；但Malta 106.4、Slovenia 102.6、Italy 102.4三条线彼此相差不到2点（约0.2格），从像素上既分不出数值也分不清是哪一国的线，端点标签还叠在一起。图上没有任何数字标注（values_printed=none），左面板的平均线更连系列名都没有，只能靠Note里的一句话认领，因此"把数读到5%以内并归到正确系列"是最主要的障碍；88个点的密度也使逐点计数只能估算。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新增 crowded_endpoint_label_stack（行末标签堆叠、仅靠颜色配对系列） | 图例/标签样式字段：把 legend 关闭并启用 line-end 标注，允许标签间距小于文字高度而产生重叠 | 行末内联标签 vs 常规图例：在同一数据上比较系列归属的准确率 |
| P2 | 一类出版方 | 新增 aggregate_panel_beside_members_panel（左=组平均、右=成员国，同一图号下两种内容） | 面板维度条件行：panel_key 需要区分"aggregate"面板与"members"面板，且允许某面板系列无名 | 面板含未命名聚合序列时，取值行是否仍能被唯一定位 |
| P6 | 通用 | axis_starts_above_zero 与 rebased_index_values 组合（轴起于50、基准写在Note里） | 坐标轴样式行：最低刻度非零且不加断轴标记；单位/基准短语只出现在图下Note | 基准与单位位于Note而非标题时的单位可恢复率 |
| P7 | 通用 | 标题拆分（figure_number="Figure 25"、title、unit_text="Summary innovation index" 来自旋转轴标题） | 记录字段：把旋转轴标题作为 unit 字段单独导出，并记录 heading placement=above | 单位来自旋转轴标题（而非标题行）时的标题字段完整率 |
