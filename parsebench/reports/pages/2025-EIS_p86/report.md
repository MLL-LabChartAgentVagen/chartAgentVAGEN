# 2025-EIS_p86

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2025-EIS | `need_estimate` | 10 | 10 |

本页为《European Innovation Scoreboard 2025》第84页，含一幅横向条形图（Figure 33，EU与全球竞争者的创新绩效）及其图注和两段正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 152 | `South Korea` · `Innovation leaders` | 5% | f1 | the South Korea coloured bar (2025) | 否 | `South Korea` · `Summary innovation index in 2025 (indexed to the EU in 2018)` · `Innovation leaders` |
| 2 | 146 | `South Korea` · `Score in 2024` | 5% | f1 | the South Korea vertical dash marker | 否 | `South Korea` · `Score in 2024` |
| 3 | 133 | `Canada` · `Strong innovators` | 5% | f1 | the Canada coloured bar (2025) | 否 | `Canada` · `Summary innovation index in 2025 (indexed to the EU in 2018)` · `Strong innovators` |
| 4 | 134 | `Canada` · `Score in 2024` | 5% | f1 | the Canada vertical dash marker (higher than the 2025 bar, a decline) | 否 | `Canada` · `Score in 2024` |
| 5 | 133 | `China` · `Strong innovators` | 5% | f1 | the China coloured bar (2025) | 否 | `China` · `Summary innovation index in 2025 (indexed to the EU in 2018)` · `Strong innovators` |
| 6 | 112 | `Japan` · `Moderate innovators` | 5% | f1 | the EU navy bar (2025) | 否 | `EU` · `Summary innovation index in 2025 (indexed to the EU in 2018)` |
| 7 | 60 | `Brazil` · `Emerging innovators` | 5% | f1 | the Brazil coloured bar (2025) | 否 | `Brazil` · `Summary innovation index in 2025 (indexed to the EU in 2018)` · `Emerging innovators` |
| 8 | 54 | `India` · `Emerging innovators` | 5% | f1 | the India coloured bar (2025) | 否 | `India` · `Summary innovation index in 2025 (indexed to the EU in 2018)` · `Emerging innovators` |
| 9 | 41 | `Chile` · `Score in 2024` | 10% | f1 | the Chile vertical dash marker, set inside the bar whose end reads about 44 | 否 | `Chile` · `Score in 2024` |
| 10 | 31 | `Mexico` · `Emerging innovators` | 1% | f1 | the Mexico coloured bar (2025), with its 2024 dash almost at the same x | 否 | `Mexico` · `Summary innovation index in 2025 (indexed to the EU in 2018)` · `Emerging innovators` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: 112

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | horizontal | 1 | 5 | 12 | 24 | 无 | 0, 20, 40, 60, 80, 100, 120, 140, 160 |

- **f1** Figure 33 / Innovation performance of the EU and its global competitors　[图上方]　单位 `Summary innovation index in 2025 (indexed to the EU in 2018)`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | vertical dash markers overlaid on every horizontal bar in the same panel |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names sit on the y axis; bars grow rightwards to the 0-160 axis |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | fill colour names the group: "Emerging innovators", "Moderate innovators", "Strong innovators", "Innovation leaders" |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend entry "Score in 2024" is a short vertical dash drawn at each bar's 2024 position |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: All performance scores are relative to that of the EU in 2018. Coloured bars show ..." |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two rows of swatches sit under the axis title, outside the plot area |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 0-160; scale word only in axis title "Summary innovation index ... indexed to the EU in 2018" |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | "Summary innovation index in 2025 (indexed to the EU in 2018)" centred under the tick row |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | "(indexed to the EU in 2018)"; note: "All performance scores are relative to that of the EU in 2018" |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the EU bar is dark navy, unlike the four legend group colours around it |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | faint vertical rules at 20-unit ticks cross the bars; no horizontal rules |

词表 65 项，本页出现 11 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `primary_series_named_only_in_axis_title` | f1 | legend names colour groups and "Score in 2024" only; the 2025 bars' year comes from the axis title | 要区分同一国家的两个数值，2025这一序列名不在图例里，只能从轴标题"Summary innovation index in 2025"或注释"Coloured bars show countries' performance in 2025"里取，表格行标签容易缺失年份键。 |
| `legend_grid_two_columns` | f1 | legend laid out as a 2-row by 3-column grid, colour groups and marker glyph interleaved | 图例顺序不是序列绘制顺序（"Score in 2024"排在第一行第三列），按图例顺序解析会错配颜色与组别。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

刻度每20单位约83像素，即1单位约4.1像素，且条上无任何数字。要命中31这样的小值，5%容差仅±1.55，约6像素；而Mexico的2025条与2024短划几乎重合（相差不到1单位），South Africa的两值也只差1-2单位，像素上无法可靠区分是哪一个序列的值。Canada的133/134相差仅约4像素，Chile的41（短划）与约44（条端）相差约12像素但落在同一容差边缘之外，读数一旦偏一格就整行判错。相比之下国家名清晰可用（第3步只需国家+序列两个键），所以卡点在读数精度。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | tick_marker_as_series（短划序列叠加在条形上） | 条形图样式字段新增"叠加上一期短划标记"开关，并在记录中把该标记作为独立序列写入数值表 | 有/无短划叠加序列时，同类别两值的定位与配对正确率对比 |
| P6 | 一类出版方 | color_encodes_extra_attribute（颜色编码分组而非序列） | 图例生成条件行：图例项为类别分组名，而序列名另存于轴标题 | 图例项=序列名 vs 图例项=分组名（序列名在轴标题）两种条件下的行寻址成功率 |
| P7 | 这份文档自己的习惯 | 新组件 primary_series_named_only_in_axis_title | 标题字段拆分：把unit/axis_title作为独立字段，并允许序列名从中派生 | 序列年份写在图例 vs 只写在轴标题时，值+年份联合检索命中率 |
| P7 | 通用 | axis_title_below_plot 与 rebased_index_values（"indexed to the EU in 2018"） | heading/unit 位置枚举增加"轴标题在图下方"，记录中保留基期文本 | 基期说明位于轴标题下方 vs 位于副标题时，指数语义被表格保留的比例 |
