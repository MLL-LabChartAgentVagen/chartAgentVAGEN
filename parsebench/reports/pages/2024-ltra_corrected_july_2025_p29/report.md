# 2024-ltra_corrected_july_2025_p29

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2024-ltra_corrected_july_2025 | `need_estimate` | 10 | 10 |

这是一页NERC《2024 Long-Term Reliability Assessment》正文页，左栏为天然气发电与管道容量的论述文字，右栏含一张编号Figure 16的堆叠柱状图（美国年度天然气管道容量新增，Interstate/Intrastate，2017–2024）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 16.2 | `2017` · `Interstate` | 50% | f1 | the 2017 Interstate segment (upper light segment, ~1.2 to ~17.4) | 否 | `2017` · `Interstate` |
| 2 | 1.2 | `2017` · `Intrastate` | 100% | f1 | the 2017 Intrastate segment (dark base of the 2017 bar) | 否 | `2017` · `Intrastate` |
| 3 | 21.2 | `2018` · `Interstate` | 40% | f1 | the 2018 Interstate segment (light segment above ~5.6 up to ~26.8) | 否 | `2018` · `Interstate` |
| 4 | 5.6 | `2018` · `Intrastate` | 20% | f1 | the 2018 Intrastate segment (dark base of the tallest bar) | 否 | `2018` · `Intrastate` |
| 5 | 10.8 | `2019` · `Interstate` | 30% | f1 | the 2019 Interstate segment (light segment from ~4.2 to ~15.0) | 否 | `2019` · `Interstate` |
| 6 | 4.2 | `2019` · `Intrastate` | 50% | f1 | the 2019 Intrastate segment (dark base of the 2019 bar) | 否 | `2019` · `Intrastate` |
| 7 | 8.7 | `2020` · `Interstate` | 20% | f1 | the 2020 Interstate segment (light segment from ~1.6 to ~10.3) | 否 | `2020` · `Interstate` |
| 8 | 1.6 | `2020` · `Intrastate` | 100% | f1 | the 2020 Intrastate segment (dark base of the 2020 bar) | 否 | `2020` · `Intrastate` |
| 9 | 8.5 | `2021` · `Interstate` | 30% | f1 | the 2021 Interstate segment (light segment from ~7.3 to ~15.8) | 否 | `2021` · `Interstate` |
| 10 | 7.3 | `2021` · `Intrastate` | 40% | f1 | the 2021 Intrastate segment (dark base of the 2021 bar) | 否 | `2021` · `Intrastate` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 2 | 8 | 14 | 无 | 0, 5, 10, 15, 20, 25, 30 |

- **f1** Figure 16 / Annual U.S. Natural Gas Pipeline Capacity Additions by Type (2017–2024)　[图下方]　单位 `Bcf/d`
  - 来源行：(Source: U.S. Energy Information Administration)

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each year is one bar with a dark 'Intrastate' base and light 'Interstate' segment above |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Interstate' and 'Intrastate' swatches in a row under the year axis |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f1 | **无** | left column of body text ('The 2024 LTRA projects...') runs level with the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis ticks are bare 0, 5 ... 30; 'Bcf/d' appears only in the caption |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'Pipeline Additions' set vertically along the left value axis |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 5, 10, 15, 20, 25, 30; no vertical rules |

词表 65 项，本页出现 6 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `source_in_caption_parenthetical` | f1 | caption ends '(Source: U.S. Energy Information Administration)' inside the bold figure caption, no separate source line | 来源与单位都被并入同一行粗体标题，解析器导出时容易把'Bcf/d'和来源一起当作标题文字，导致单位无法作为独立字段与数值绑定。 |
| `empty_series_slot_in_stack` | f1 | 2022 bar shows only light Interstate; 2024 shows only a sliver of dark Intrastate | 某些年份某一系列为零或极小，表格里该单元格是缺失还是零无法从图上区分，读值时需明确该槽位是否存在。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，刻度只有0/5/10/15/20/25/30，5个单位约占74像素，即1像素≈0.07 Bcf/d。要判定的十个值里有1.2、1.6、4.2这类小段，5%容差分别只有±0.06、±0.08、±0.21，几乎等于1–3像素，靠插值读不到；而Interstate段（16.2、21.2、10.8、8.7、8.5）并非从零起算的柱长，必须用堆叠顶端减去深色底段两次读数相减，误差叠加后更难落在5%内。相比之下寻址只需'2017'+'Interstate'两个键，标题为粗体独立行，第3、4步都不是瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | stacked_bar中分段（非从零起算）读数的可达精度评估 | 评测配置里readable的判定字段：把布尔门改为按mark给出的精度上限，并对堆叠中间段单独记录 | 新增一行：堆叠分段 vs 从零起算柱，在同一刻度密度下的5%命中率对比 |
| P6 | 一类出版方 | unit_in_axis_or_title（单位只在图题内、坐标轴为裸数字） | 样式条件表中的单位位置维度：增加“单位仅出现在图题末尾”的取值 | 新增一行：单位在轴标题 vs 单位在图题末尾时，数值+单位联合检索的召回差异 |
| P7 | 这份文档自己的习惯 | new_components中的source_in_caption_parenthetical（标题号+标题+单位+来源同一行且位于图下） | 记录字段：把figure heading拆成number/title/unit/source并标注placement=below | 新增一行：来源作为独立行 vs 内嵌括号在标题内时，标题字段抽取正确率 |
