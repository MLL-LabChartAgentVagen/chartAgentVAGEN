# sri-sigma-natural-catastrophes-1-2025_p10

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| sri-sigma-natural-catastrophes-1-2025 | `need_estimate` | 10 | 10 |

该页为 Swiss Re Institute《sigma No 1/2025》第10页，主体是 Figure 6 的双系列直方图（1995–2024 年年度巨灾损失偏离趋势的分布），下方配有一段正文与左侧蓝色引言。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 5 | `-100%` · `Primary perils` | 10% | f1 | the tall light-green Primary perils bar in the –100% to –75% bin | 否 | `Primary perils` · `–100%` · `Number of years` |
| 2 | 1 | `-75%` · `Secondary perils` | 10% | f1 | the short teal Secondary perils bar just right of –100% | 否 | `Secondary perils` · `–100%` · `Number of years` |
| 3 | 4 | `-50%` · `Primary perils` | 5% | f1 | a teal Secondary perils bar of about 4 in the –50% region | 否 | `Secondary perils` · `–50%` · `Number of years` |
| 4 | 8 | `-25%` · `Secondary perils` | 5% | f1 | the teal Secondary perils bar reaching just under 8 at the –25% bin | 否 | `Secondary perils` · `–25%` · `Number of years` |
| 5 | 2 | `0%` · `Primary perils` | 5% | f1 | a light-green Primary perils bar of about 2 just left of 0% | 否 | `Primary perils` · `–25%` · `Number of years` |
| 6 | 4 | `25%` · `Secondary perils` | 5% | f1 | the teal Secondary perils bar of about 4 in the 25% to 50% bin | 否 | `Secondary perils` · `25%` · `Number of years` |
| 7 | 3 | `50%` · `Primary perils` | 10% | f1 | the light-green Primary perils bar of about 3 in the 50% to 75% bin | 否 | `Primary perils` · `50%` · `Number of years` |
| 8 | 0 | `125%` · `Primary perils` | 1% | f1 | an empty bin where no bar is drawn (e.g. the 350% slot); the zero is implied, not a mark, so it cannot be pinned to one slot | 否 | `Primary perils` · `350%` · `Number of years` |
| 9 | 2 | `225%` · `Primary perils` | 5% | f1 | the teal Secondary perils bar labelled '2011, 2017' at the 225% bin | 否 | `Secondary perils` · `225%` · `2011, 2017` |
| 10 | 1 | `675%` · `Primary perils` | 10% | f1 | the light-green Primary perils bar labelled '2005' at the 675% bin | 否 | `Primary perils` · `675%` · `2005` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: 1, 4, 0, 2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `histogram` | vertical | 1 | 2 | 34 | 18 | 无 | 0, 2, 4, 6, 8, 10, 12 |

- **f1** Figure 6 / Distribution of annual losses from primary and secondary perils in % deviation from trend (1995 – 2024)　[图上方]　单位 `Number of years`
  - 来源行：Source: Swiss Re Institute

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | light-green 'Primary perils' and teal 'Secondary perils' bars stand side by side inside the same bins |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | '2011', '1999', '2011, 2017', '2004', '2005' printed over the tall-tail bars inside the plot |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: Swiss Re Institute' in small print below the plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Primary perils'  'Secondary perils' swatch row sits under the x tick labels, above the source line |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | y ticks are bare 0,2,4,...,12; scale word only in 'Number of years' and 'in % deviation from trend' |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | 'Deviations from tend' centred beneath the rotated x tick labels |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | '12   Number of years' set on one line above the plot, level with the top tick |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | '–150%' through '700%' set at roughly 45 degrees along the category axis |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | category slots labelled only by signed percentage codes '–125%', '675%', no words |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole figure block including the plot area carries a pale blue tint |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 2, 4, 6, 8, 10, 12 across the panel; no vertical rules |

词表 65 项，本页出现 11 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `bin_edge_tick_labels` | f1 | 35 tick labels '–150%' ... '700%' mark bin boundaries; each bar sits between two labels, not on one | 读某根柱子时必须把它归到相邻两个刻度构成的区间（如 –100% 到 –75%），单个刻度标签无法唯一定位该柱，表格行名需要用区间或边界约定。 |
| `empty_bin_slots` | f1 | bins from 300% to 650% show no bar at all; zero years is implied by absence, no label or dash | 值为 0 的区间在图上完全没有图元，解析出的表格若不补零就丢失这些行，0 这个待查值也无法被唯一寻址。 |
| `identity_label_over_bar` | f1 | '2011', '1999', '2011, 2017', '2004', '2005' name the years behind tail bars, not their heights | 柱顶文字看似数值标签，实为年份标识；若被误当作值读取，会把 2011、2005 当成柱高，读数完全错位。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

寻址是瓶颈：值域只有 0–12 的小整数，而 34 个区间 × 2 个系列里数值大量重复——1 至少出现 5 次、4 出现 2 次、0 出现二十多次，所以任何一行都必须同时带系列名（Primary perils / Secondary perils）和区间标签才能唯一确定。而区间标签本身是边界刻度（–100%、–75%…675%），柱子落在两个刻度之间，表格行名到底写哪一个没有页面依据；空区间根本没有图元，0 这个待查值无从挂靠。相比之下读数不难：网格每 2 个单位约 49 px，1 个单位约 25 px，柱高本是整数，容差 5% 对 8 意味着 ±0.4（约 10 px），肉眼可判。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | 新组件 bin_edge_tick_labels（直方图刻度落在区间边界而非区间中心） | 图表条件表中新增 histogram 的 x 轴刻度模式字段（边界刻度 / 中心刻度），并在记录字段里同时保存区间下界与上界 | “边界刻度直方图 vs 中心刻度类别轴”一行，检验行名用区间边界时的匹配率 |
| P1 | 一类出版方 | 新组件 empty_bin_slots（缺失柱即 0，不画任何图元） | 数据记录字段：为无图元的类别槽显式写入 0，并在样式字段标记“零值不绘制” | “显式零行 vs 省略零行”一行，衡量 0 值是否可被寻址 |
| P6 | 一类出版方 | 新组件 identity_label_over_bar（柱顶文字是年份标识而非数值） | 标签样式字段增加“柱顶文本类型：值 / 标识”，与 value_label_outside 区分 | “柱顶为标识文本 vs 柱顶为数值”一行，检验解析器是否误把标识当值 |
| P7 | 这份文档自己的习惯 | axis_title_above_axis 与 axis_title_below_plot 同时出现（“12  Number of years”在顶，“Deviations from tend”在底） | 标题/单位位置字段允许纵轴单位置于顶刻度旁、横轴标题置于刻度下方的组合 | “单位在顶刻度行 vs 单位在标题行”一行，检验单位能否被带入表头 |
