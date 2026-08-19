# 2024-ltra_corrected_july_2025_p27

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2024-ltra_corrected_july_2025 | `need_estimate` | 10 | 10 |

这是NERC《2024 Long-Term Reliability Assessment》第27页，左右两栏各有一幅堆叠柱状图：Figure 13为各区域现有与规划的分布式太阳能容量，Figure 14为2024–2034年预计发电退役容量。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 23000 | `Existing` · `WECC-CAMX` | 10% | f1 | the WECC-CAMX 'Existing' segment, top near 23,000 | 否 | `WECC-CAMX` · `Existing` · `MW (dc)` · `Figure 13` |
| 2 | 16000 | `Planned` · `WECC-CAMX` | 15% | f1 | the WECC-CAMX 'Planned' segment thickness (from ~23,000 to ~39,000) | 否 | `WECC-CAMX` · `Planned` · `MW (dc)` · `Figure 13` |
| 3 | 20000 | `Planned` · `Texas RE-ERCOT` | 10% | f1 | the Texas RE-ERCOT 'Planned' segment thickness (from ~2,600 to ~22,600) | 否 | `Texas RE-ERCOT` · `Planned` · `MW (dc)` · `Figure 13` |
| 4 | 8200 | `Existing` · `PJM` | 20% | f1 | the PJM 'Existing' segment, top just above 8,000 | 否 | `PJM` · `Existing` · `MW (dc)` · `Figure 13` |
| 5 | 5600 | `Existing` · `NPCC-New York` | 30% | f1 | the NPCC-New York 'Existing' segment | 否 | `NPCC-New York` · `Existing` · `MW (dc)` · `Figure 13` |
| 6 | 7000 | `Confirmed` · `2024` | 30% | f2 | the 2024 'Confirmed' segment, the only bar for 2024 | 否 | `2024` · `Confirmed` · `MW` · `Figure 14` |
| 7 | 48000 | `Confirmed` · `2028` | 10% | f2 | the 2028 'Confirmed' segment top, just below 48,000 | 否 | `2028` · `Confirmed` · `MW` · `Figure 14` |
| 8 | 35000 | `Unconfirmed` · `2028` | 10% | f2 | the 2026 'Confirmed' segment top, near 35,000 | 否 | `2026` · `Confirmed` · `MW` · `Figure 14` |
| 9 | 78000 | `Confirmed` · `2034` | 5% | f2 | the 2034 'Confirmed' segment top, just under 80,000 | 否 | `2034` · `Confirmed` · `MW` · `Figure 14` |
| 10 | 37000 | `Unconfirmed` · `2034` | 10% | f2 | the 2034 'Unconfirmed' segment thickness (~78,000 to ~115,000) | 否 | `2034` · `Unconfirmed` · `MW` · `Figure 14` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: 35000

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 2 | 10 | 20 | 无 | 0, 5,000, 10,000, 15,000, 20,000, 25,000, 30,000, 35,000, 40,000 |
| f2 | `stacked_bar` | vertical | 1 | 2 | 7 | 14 | 无 | 0, 20,000, 40,000, 60,000, 80,000, 100,000, 120,000, 140,000 |

- **f1** Figure 13 / Solar PV DER Capacity Existing and Planned through 2034　[图下方]　单位 `MW (dc)`
- **f2** Figure 14 / Projected Generation Retirement Capacity through 2034　[图下方]　单位 `MW`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each area bar shows a dark 'Existing' base with lighter 'Planned' stacked above |
| `stacked_bar` | 堆叠条 | f2 | 有 | each year bar stacks 'Confirmed' dark below 'Unconfirmed' light blue |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f2 | **无** | short horizontal rule at ~117,000 tied to the '2023 LTRA Total Retirements' box |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f2 | **无** | grey box '2023 LTRA Total Retirements' with leader rule inside plot near 120,000 |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | Figure 13 and Figure 14 each with own numbered caption in separate columns |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Existing  Planned' legend row sits under the plot above the caption |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | 'Confirmed  Unconfirmed' legend row below the x axis |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | two-column body text runs above and beside each figure in the same page band |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 0..40,000 with scale word only in the axis title 'MW (dc)' |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | bare ticks 0..140,000, unit only from rotated axis title 'MW' |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'MW (dc)' set vertically along the left value axis |
| `rotated_axis_title` | 轴标题竖排 | f2 | 有 | 'MW' set vertically along the left value axis |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | area names such as 'NPCC-New England' are set at about 45 degrees |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | categories written as codes: 'PJM', 'SERC-E', 'WECC-CAMX', 'Texas RE-ERCOT' |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f2 | **无** | x axis reads 2024...2029 then ellipsis '...' then 2034, skipping years |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal gridlines across the panel, no vertical rules |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | horizontal gridlines only across the plot area |

词表 65 项，本页出现 12 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `time_axis_gap_ellipsis` | f2 | '2029 ⋯ 2034' — an ellipsis between tick labels marks omitted years 2030-2033 | 读取2034柱时必须知道它是累计末年而非2030，年份轴不连续，表格行标签需照抄含省略号的刻度顺序。 |
| `external_benchmark_marker_label` | f2 | grey boxed '2023 LTRA Total Retirements' marks a prior-report total, not a data series | 该水平标记的数值(约117,000)不属于任一柱，读值时不能把它当作某年数据。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

两图都没有任何数值标签，全部数字必须靠像素对轴读出。Figure 14刻度间距为20,000 MW，而5%容差对7,000这样的小柱只有±350 MW，即一个刻度格的1/57，约1个像素级别；Figure 13刻度为5,000 MW，读5,600需精确到±280 MW。更棘手的是堆叠段厚度（如WECC-CAMX的Planned 16,000、2034的Unconfirmed 37,000）必须由两个端点相减得到，误差叠加，几乎无法稳定落入5%以内。相比之下标签只需2个键（类别+系列），标题也已作为粗体caption存在，因此读值是真正的瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | stacked_bar 的分段厚度读值（配合 value_label_inside 缺失的情形） | 记录字段中为每个堆叠段同时存储 segment_value 与 cumulative_top，风格字段设 values_printed=none | 新增一行：堆叠段是否需由累计端点相减读出 vs 直接读段长，对比可达精度 |
| P6 | 一类出版方 | new_components 中的 time_axis_gap_ellipsis（年份轴省略号跳年） | 类别轴样式字段增加 tick_gap_glyph 选项，允许在刻度序列中插入 '⋯' | 新增一行：时间轴连续 vs 含省略号跳年时，年份行标签匹配准确率 |
| P6 | 一类出版方 | new_components 中的 external_benchmark_marker_label（图内基准标记框） | 条件行加入 annotation_callout + reference_line 组合，标记不进入数据表 | 新增一行：图内存在非数据基准标记时，模型误把标记值当作某类别值的比例 |
| P7 | 一类出版方 | 标题块置于图下方（placement=below）的编号+标题结构 | P7 标题字段中 placement 取值 below，并与 rotated_axis_title 承载单位配合 | 新增一行：标题在图下方且单位仅在旋转轴标题时，上下文键的召回率 |
