# b3cd580a-3656-44ed-838a-5f2996ff6fc9_p23

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b3cd580a-3656-44ed-838a-5f2996ff6fc9 | `need_estimate` | 10 | 10 |

该页为《Industry outlook 2025》零售章节，含一段正文、一个左侧标题栏的分组柱状图（2024 与 2025 各地区零售销量增速）以及下方小标题与两栏正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 0.5 | `USMCA` · `2024` | 100% | f1 | the USMCA 2024 bar (dark blue, small positive) | 否 | `USMCA` · `2024` · `Retail sales volume growth rate, %` |
| 2 | 1.0 | `USMCA` · `2025` | 100% | f1 | the USMCA 2025 bar (red, small positive) | 否 | `USMCA` · `2025` · `Retail sales volume growth rate, %` |
| 3 | 2.3 | `Europe` · `2024` | 50% | f1 | the Europe 2024 bar, reaching just above the 2 gridline | 否 | `Europe` · `2024` · `Retail sales volume growth rate, %` |
| 4 | 1.3 | `Europe` · `2025` | 60% | f1 | the Europe 2025 bar (red, below the 2 gridline) | 否 | `Europe` · `2025` · `Retail sales volume growth rate, %` |
| 5 | 2.5 | `Asia-Pacific` · `2024` | 50% | f1 | the Asia-Pacific 2024 bar, tallest positive blue bar | 否 | `Asia-Pacific` · `2024` · `Retail sales volume growth rate, %` |
| 6 | 2.6 | `Asia-Pacific` · `2025` | 50% | f1 | the Asia-Pacific 2025 bar, tallest positive red bar | 否 | `Asia-Pacific` · `2025` · `Retail sales volume growth rate, %` |
| 7 | -7 | `South America` · `2024` | 20% | f1 | the South America 2024 bar, running down past −6 toward −8 | 否 | `South America` · `2024` · `Retail sales volume growth rate, %` |
| 8 | 0.5 | `South America` · `2025` | 100% | f1 | the South America 2025 bar, short red bar just above zero | 否 | `South America` · `2025` · `Retail sales volume growth rate, %` |
| 9 | 0.8 | `MEA` · `2024` | 100% | f1 | the MEA 2024 bar (dark blue) | 否 | `MEA` · `2024` · `Retail sales volume growth rate, %` |
| 10 | 1.0 | `MEA` · `2025` | 100% | f1 | the MEA 2025 bar (red) | 否 | `MEA` · `2025` · `Retail sales volume growth rate, %` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 1 | 2 | 5 | 10 | 无 | 4, 2, 0, −2, −4, −6, −8 |

- **f1** Asia will lead global retail sales growth, and South America will rebound in 2025　[与图并排]　单位 `Retail sales volume growth rate, %`
  - 来源行：Source: EIU.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | two bars per region slot, dark blue "2024" beside red "2025" at USMCA, Europe, etc. |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a heavy black horizontal rule at the 0 level runs across the plot, bars hang below it |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | South America 2024 bar drops below the zero baseline toward the −8 tick |
| `right_side_y_axis` | 唯一的值轴画在右侧 | f1 | **无** | the only value ticks "4, 2, 0, −2, −4, −6, −8" sit on the right edge |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: EIU." and "Copyright © The Economist Intelligence Unit 2024. All rights reserved." in small print |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f1 | 有 | "2024" and "2025" swatches stacked in the left column, level with the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | "Retail sales volume growth rate, %" under the title; axis shows bare numbers only |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | thin grey horizontal rules at 4, 2, −2, −4, −6, −8; no vertical rules |

词表 65 项，本页出现 8 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `left_metadata_column` | f1 | title, unit line, legend and source all stacked in a narrow left column beside the plot | 标题、单位、图例、来源都不在绘图区上方，解析成表格时容易与图分离，读值时需从左栏取回“%”与年份系列名。 |
| `category_labels_below_lowest_tick` | f1 | "USMCA ... MEA" printed under the −8 gridline, far from the zero baseline the bars sit on | 类别名与柱底不对齐（负值柱穿过标签区），把标签配到正确柱子需要额外的水平位置判断。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，网格线间距为 2 个百分点，而待评的多数值在 0.5–2.6 之间；按 5% 容差，0.5 只允许 ±0.025、0.8 只允许 ±0.04，相当于在 2 个百分点宽的网格间隔里辨认约 1/80 的高度，像素上不可能达到。相比之下标签只需“地区+年份”两个键（USMCA/Europe/Asia-Pacific/South America/MEA × 2024/2025），表格容易承载；标题虽在左栏但可作粗体行导出。因此读值是真正的瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | negative_values 与 reference_line（零线两侧柱子） | 样式条件行中加入“含负值且零线加粗、类别标签置于最低刻度下方”的组合 | 负值柱 + 零线位置：对比零线在中部与在底部时的读值误差 |
| P6 | 一类出版方 | right_side_y_axis（唯一值轴在右侧） | 图表样式字段 axis_side，允许值轴单独绘在右缘 | 值轴左置 vs 右置对刻度—柱对应关系判定的影响 |
| P7 | 这份文档自己的习惯 | 标题拆分为 number/title/unit_text 与 placement=beside（含 legend_beside_plot、left_metadata_column） | 记录字段 heading（title、unit_text、placement）与图例位置字段 | 标题+单位+图例位于左侧栏 vs 位于绘图区上方时，导出表格能否恢复单位“%” |
| P1 | 通用 | 无数值标签时的可达精度（value_label 缺失下的 P1 处理） | 评测条件行：values_printed=none 且网格间距为 2 单位时的容差定义 | 按刻度间距归一化的每标记可达精度，替代 5% 相对容差的布尔判定 |
