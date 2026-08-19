# World_Manufacturing_Production_2024_Q3_p11

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Manufacturing_Production_2024_Q3 | `need_estimate` | 10 | 10 |

报告第3章开篇页，正文与两个带图标的侧栏引语之外，只有一幅折线图 Figure 3.1，展示按技术水平分组的全球制造业生产指数（2015=100）季度走势。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 99 | `Q1` · `2015` · `Medium-high and high tech` | 3% | f1 | the Q1 2015 point of the red "Medium-high and high tech" line, just under 100 | 否 | `Medium-high and high tech` · `Q1` · `2015` |
| 2 | 110 | `Q3` · `2017` · `Medium-high and high tech` | 2% | f1 | the Q1 2017 point of the red "Medium-high and high tech" line, on the 110 gridline | 否 | `Medium-high and high tech` · `Q1` · `2017` |
| 3 | 108 | `Q1` · `2020` · `Medium-high and high tech` | 2% | f1 | the Q3 2018 point of the teal "Other manufacturing industries" line | 否 | `Other manufacturing industries` · `Q3` · `2018` |
| 4 | 118 | `Q3` · `2020` · `Medium-high and high tech` | 2% | f1 | the Q3 2020 point of the red "Medium-high and high tech" line, the rebound above the dip | 否 | `Medium-high and high tech` · `Q3` · `2020` |
| 5 | 141 | `Q3` · `2024` · `Medium-high and high tech` | 2% | f1 | the last (Q3 2024) point of the red "Medium-high and high tech" line | 否 | `Medium-high and high tech` · `Q3` · `2024` |
| 6 | 98 | `Q1` · `2015` · `Other manufacturing industries` | 3% | f1 | the 2020 trough of the teal "Other manufacturing industries" line, one quarter before the Q3 2020 tick | 否 | `Other manufacturing industries` · `2020` |
| 7 | 102 | `Q1` · `2020` · `Other manufacturing industries` | 2% | f1 | the Q3 2016 point of the teal "Other manufacturing industries" line | 否 | `Other manufacturing industries` · `Q3` · `2016` |
| 8 | 106 | `Q3` · `2020` · `Other manufacturing industries` | 2% | f1 | the Q3 2020 point of the teal "Other manufacturing industries" line | 否 | `Other manufacturing industries` · `Q3` · `2020` |
| 9 | 112 | `Q3` · `2024` · `Other manufacturing industries` | 2% | f1 | the last (Q3 2024) point of the teal "Other manufacturing industries" line | 否 | `Other manufacturing industries` · `Q3` · `2024` |
| 10 | 133 | `Q3` · `2022` · `Medium-high and high tech` | 2% | f1 | the Q3 2022 point of the red "Medium-high and high tech" line | 否 | `Medium-high and high tech` · `Q3` · `2022` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: 110, 108, 98, 102
- 规则需要的键比模型报出的图能提供的多——rules need 3 keys, the richest figure offers 2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 2 | 39 | 78 | 无 | 90, 100, 110, 120, 130, 140 |

- **f1** Figure 3.1 / Global index of manufacturing production, industries by technology level　[图下方]　单位 `Index (2015 = 100)`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest tick is "90", no zero on the axis and no break glyph |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | "Medium-high and high tech" and "Other manufacturing industries" sit in a row above the plot area |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis reads bare 90...140; the scale word only in "Index (2015 = 100)" |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "Index (2015 = 100)" set vertically along the left value axis |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | axis title states the base: "Index (2015 = 100)" |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | inner row "Q1"/"Q3", outer row "2015" ... "2024" beneath the Q1 ticks |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | points are quarterly but ticks appear only at Q1 and Q3 of each year |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 100, 110, 120, 130, 140; no vertical rules |

词表 65 项，本页出现 8 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `marker_shape_encodes_series` | f1 | red line uses open circles, teal line uses open diamonds at plotted points | 在两线交叠的2015-2016段，颜色难分时只能靠标记形状（圆/菱形）判断某点属于哪个系列，从而决定该值归到哪一行。 |
| `markers_on_subset_of_points` | f1 | lines bend at every quarter but circular/diamond markers appear only about every second quarter | 有标记的点与折线顶点数量不一致，读数时需判断某个拐点是否为可寻址的数据点，未标记季度也没有对应刻度名。 |
| `icon_pull_quote_sidebar` | page | right column: robot-arm icon over "Higher-technology industries maintained their strong progress..." | 侧栏引语中的数字（如1.5、2.6 per cent）来自正文而非图，容易被误当作图上标注值。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

读数本身不难：刻度间距10个指数点，5%容差在110附近约±5.5，几乎等于半个格距，肉眼定位到±2以内即可通过。真正卡住的是寻址：39个季度点只有20个刻度标签，且标签被拆成上下两行（"Q1"+"2015"、"Q3"无年份），要唯一定位一个值需要系列名+季度+年份三个键，而像teal线2020年谷底（≈98）落在无刻度的季度上，页面上根本不存在可逐字引用的时间标签，表格无法为其写出行名。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | two_level_x_ticks 与 sparse_time_ticks 的组合（内层Q1/Q3、外层年份，且点多于刻度） | 时间轴样式字段：tick_level=2、tick_every=2个数据点，记录字段需保存每个点的完整时间键（year+quarter）而非仅刻度文本 | 新增一行：刻度标签数<数据点数时，逐点寻址成功率对比全标签时间轴 |
| new | 通用 | marker_shape_encodes_series（圆 vs 菱形） | 折线系列样式字段增加 marker_shape 维度，与颜色独立取值 | 新增一行：系列仅靠标记形状区分（同色系/交叠段）时的系列归属正确率 |
| P7 | 这份文档自己的习惯 | 标题块拆分：figure_number+title 位于图下、unit 位于旋转轴标题（Index (2015 = 100)） | heading 记录字段：placement=below、unit_text 独立成字段并可落在 rotated axis title 上 | 新增一行：标题在图下方且单位在旋转轴标题时，表格上下文（bold标题）命中率 |
| P1 | 通用 | axis_starts_above_zero（最低刻度90）配合 rebased_index_values | 数值轴条件行：y_min>0 且为指数基期数据 | 新增一行：轴不含零的指数图，读数绝对误差与容差(5%)的比值分布 |
