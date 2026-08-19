# b3cd580a-3656-44ed-838a-5f2996ff6fc9_p26

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b3cd580a-3656-44ed-838a-5f2996ff6fc9 | `need_estimate` | 10 | 10 |

这一页是《Industry outlook 2025》第26页，上方为两栏正文，中部为一张无编号的折线图（全球消费支出指数，2020=100，六条曲线以引线标注），下方为“What to watch”栏目文字。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 178 | `2025` · `Hotels & restaurants` | 5% | f1 | the 2025 endpoint of the topmost line, Hotels & restaurants, just under the 180 gridline | 否 | `Hotels & restaurants` · `2025` |
| 2 | 125 | `2025` · `Household goods & services` | 5% | f1 | a 2025 endpoint in the lower cluster, most plausibly Housing & household fuels (between the 120 and 130 gridlines) | 否 | `Housing & household fuels` · `2025` |
| 3 | 132 | `2025` · `Clothing & footwear` | 5% | f1 | the 2025 endpoint of the line the "Clothing & footwear" arrow points to, just above 130 | 否 | `Clothing & footwear` · `2025` |
| 4 | 128 | `2025` · `Food, beverages & tobacco` | 5% | f1 | a 2025 endpoint in the cluster, most plausibly Food, beverages & tobacco, below the 130 gridline | 否 | `Food, beverages & tobacco` · `2025` |
| 5 | 139 | `2025` · `Leisure & education` | 5% | f1 | the 2025 endpoint of the second-highest line, reached by the "Leisure & education" arrow, at the 140 gridline | 否 | `Leisure & education` · `2025` |
| 6 | 123 | `2025` · `Housing & household fuels` | 5% | f1 | the 2025 endpoint of the red line, Household goods & services, just above 120 | 否 | `Household goods & services` · `2025` |
| 7 | 100 | `2020` · `Hotels & restaurants` | 5% | f1 | the common 2020 origin on the 100 gridline, shared by all six lines (index base) | 否 | `2020` · `2020=100` |
| 8 | 156 | `2023` · `Hotels & restaurants` | 5% | f1 | the top line at the 2024 tick, Hotels & restaurants, between the 150 and 160 gridlines | 否 | `Hotels & restaurants` · `2024` |
| 9 | 125 | `2024` · `Clothing & footwear` | 5% | f1 | a 2024 value inside the 120-130 cluster; cannot be attributed to one line at this rendering (Leisure & education or Clothing & footwear) | 否 | `2024` |
| 10 | 124 | `2023` · `Leisure & education` | 5% | f1 | another 2024 value in the same 120-130 cluster, one gridline-fifth apart from the previous one | 否 | `2024` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——6 of 10 predicted key sets miss a rule label: 125, 123, 100, 156, 125, 124

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 6 | 6 | 36 | 无 | 100, 110, 120, 130, 140, 150, 160, 170, 180 |

- **f1** Consumer spending on household goods & furniture will be sluggish / Global consumer spending in US$, 2020=100　[与图并排]　单位 `US$, 2020=100`
  - 来源行：Source: EIU.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | six curved arrows drawn over the plot area running from each text label to its line |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | grey vertical tint from 2024 to 2025 marking the forecast window |
| `right_side_y_axis` | 唯一的值轴画在右侧 | f1 | **无** | the only value axis, 100 to 180, is printed down the right edge of the plot |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest tick printed is 100, no break glyph on the axis |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: EIU." and "Copyright © The Economist Intelligence Unit 2024. All rights reserved." in small print |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis shows bare 100...180; scale only in "Global consumer spending in US$, 2020=100" |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | heading line reads "Global consumer spending in US$, 2020=100" |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | ticks 2020...2025 while the curves are smoothed, so intermediate points sit between ticks |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | f1 | **无** | "Hotels & restaurants", "Clothing & footwear" etc. written in the plot with curved arrows to each line; no legend |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at each 10-unit tick across the panel, no vertical rules |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | one line drawn in red with its label "Household goods & services" bold red, others grey |

词表 65 项，本页出现 11 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `source_beside_plot` | f1 | "Source: EIU." and the copyright sit in the left side column level with the plot, not below it | 来源与版权行不在图下方而在左侧栏，解析器可能把它们并入正文，导致表格失去来源归属。 |
| `curved_leader_arrow_labels` | f1 | labels sit far from their lines and are attached by long curved arrows crossing other lines | 系列名与曲线的对应只能靠弯箭头判断，取值时容易把某年数值归到错误的系列。 |
| `series_converge_at_index_base` | f1 | all six lines start from one common point at 2020 on the 100 gridline | 2020=100 这一数值同时属于六个系列，无法用“系列+年份”唯一定位。 |
| `heading_in_side_column` | f1 | title and unit line occupy a narrow left column level with the plot, plot fills the right two-thirds | 标题不在图上方，导出的 markdown 中标题与表格可能被分离，读值缺少上下文。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数字，唯一的刻度在右侧、每格10个指数点（约35像素），必须靠像素插值。真正卡住的是：除 Hotels & restaurants（156/178）外，其余五条灰线在2024-2025年全部挤在120-140这20点区间内，而5%容差在125处约为±6点，相邻两条线（如124与125、128与132）的间距小于容差，读出的数值可以“对”但归属可能错；再加上没有图例、只靠弯箭头引线区分系列，2020年六条线又共汇于100，使“系列+年份”这一组键无法把单个数值唯一钉住。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 一类出版方 | heading 五分拆并支持 placement=beside（标题、含单位的副标题在左侧栏与图并列） | 图表记录的 heading 字段与版式条件行（heading_placement 增加 beside） | heading_placement=above vs beside 时标题/单位能否被正确挂到表格上 |
| P3 | 这份文档自己的习惯 | 新组件 source_beside_plot（来源与版权行位于侧栏而非图下） | 页面导出条件行：source/note 的位置字段 | source 在图下 vs 在侧栏两种排版下来源行的归属正确率 |
| P6 | 一类出版方 | right_side_y_axis 与 axis_starts_above_zero 组合（唯一值轴在右、最低刻度100） | 样式字段：value_axis_side 与 axis_min 起点 | 值轴在左/右、起点为0/非0时读数误差分布 |
| P6 | 一类出版方 | 新组件 curved_leader_arrow_labels / inline_series_labels（无图例，靠弯箭头标注系列） | 图例条件行：legend=none + leader_arrow 标注样式 | 有图例 vs 仅引线标注时系列归属（row key）正确率 |
| new | 通用 | 新组件 series_converge_at_index_base（指数基期年所有系列同值100） | 记录字段：允许同一 (series, category) 组多系列同值，评分需多键匹配 | 基期重合点是否要求列出全部系列行的可寻址性测试 |
