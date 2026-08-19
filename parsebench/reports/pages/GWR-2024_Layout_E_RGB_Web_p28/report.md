# GWR-2024_Layout_E_RGB_Web_p28

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| GWR-2024_Layout_E_RGB_Web | `need_estimate` | 10 | 10 |

本页上半部为图2.2（2006–24年政府总债务占GDP比重的柱线混合图，含世界柱与两条经济体分组折线），下半部为两栏正文并开始2.3节“Inflation rates”。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 122 | `Advanced economies` · `2020` | 1% | f1 | the 2020 point of the Advanced economies line (peak) | 是 | `Figure 2.2.` · `Advanced economies` · `2020` |
| 2 | 73 | `Advanced economies` · `2006` | 1% | f1 | the 2006 point of the Advanced economies line | 是 | `Figure 2.2.` · `Advanced economies` · `2006` |
| 3 | 109 | `Advanced economies` · `2024` | 1% | f1 | the 2023 (and 2024) points of the Advanced economies line | 是 | `Figure 2.2.` · `Advanced economies` · `2023` |
| 4 | 70 | `Emerging and developing economies` · `2024` | 1% | f1 | the 2024 point of the Emerging and developing economies line | 是 | `Figure 2.2.` · `Emerging and developing economies` · `2024` |
| 5 | 65 | `Emerging and developing economies` · `2020` | 1% | f1 | the 2020 point of the Emerging and developing economies line | 是 | `Figure 2.2.` · `Emerging and developing economies` · `2020` |
| 6 | 33 | `Emerging and developing economies` · `2008` | 1% | f1 | the 2008 point of the Emerging and developing economies line (trough) | 是 | `Figure 2.2.` · `Emerging and developing economies` · `2008` |
| 7 | 101 | `Advanced economies` · `2011` | 1% | f1 | the 2010 point of the Advanced economies line | 是 | `Figure 2.2.` · `Advanced economies` · `2010` |
| 8 | 44 | `Emerging and developing economies` · `2015` | 1% | f1 | the 2015 point of the Emerging and developing economies line | 是 | `Figure 2.2.` · `Emerging and developing economies` · `2015` |
| 9 | 89 | `World` · `2020` | 5% | f1 | the 2020 World bar, tallest blue bar, read against ticks between 80 and 90 | 否 | `Figure 2.2.` · `World` · `2020` |
| 10 | 86 | `World` · `2024` | 5% | f1 | the 2024 World bar, read against ticks just below 90 | 否 | `Figure 2.2.` · `World` · `2024` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 109, 101

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 3 | 19 | 57 | 部分 | 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130 |
| f1 | `compound` | vertical | 1 | 3 | 19 | 57 | 部分 | 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130 |

- **f1** Figure 2.2. / Government gross debt as a share of GDP, 2006–24　[图上方]　单位 `(percentage)`
  - 来源行：Source: IMF 2024b.
- **f1** Figure 2.2. / Government gross debt as a share of GDP, 2006–24　[与图并排]　单位 `Share of GDP (%)`
  - 来源行：Source: IMF 2024b.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | blue bars for World with two coloured lines (Advanced, Emerging) overlaid in the same panel |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest y tick is 30, bars begin at 30 not zero |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: IMF 2024b." in small print under the plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | World / Advanced economies / Emerging and developing economies row beneath the x tick labels |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | heading ends "(percentage)"; axis title reads "Share of GDP (%)" |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "Share of GDP (%)" set vertically along the left axis |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | no; not present |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | Emerging series labels 37, 36, 33, 38 sit over the blue World bars |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | line values 73, 122, 109, 33, 70 printed above/below their markers, off the line |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | year labels 2006...2024 set at about 45 degrees |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | whole figure block sits on a pale blue tinted panel |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each 10-unit tick, no vertical grid lines |

词表 65 项，本页出现 12 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `labels_on_lines_only_not_bars` | f1 | every line point carries a printed number; the 19 World bars carry none | 世界柱（如2020约89、2024约86）只能靠像素对照30–130刻度读取，与折线的印刷值精度不对等。 |
| `line_label_collision_with_bars` | f1 | Emerging labels 37, 36, 33, 38 printed inside the blue bar area, over bar fill | 这些数字视觉上落在柱体上，解析时易被错配给World系列而非Emerging系列。 |
| `partial_series_label_coverage` | f1 | Advanced line labels printed for all years; some later Emerging points (65,64,64,69,70) labelled, earlier ones too | 需判断哪一系列拥有该印刷数字，读值时必须结合位置而非仅数值。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

八个折线值都已印在图上，标签不难；真正卡住的是两个未标注的World柱（约89与86）。y轴每10个单位一格、跨度仅30–130，柱顶落在80–90格之间，且轴起点为30使柱长与数值不成比例，5%容差对86而言只有±4.3，肉眼对格易读成85或88；再加上37/36/33等Emerging标签压在柱体上，容易把柱值误取为这些数字。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | axis_starts_above_zero 与 mixed_marks 组合（柱+多折线且轴不从零起） | 图表生成条件行：为compound族增加“value axis lowest tick > 0”的样式开关 | 轴起点是否为零 × 柱值是否印刷，测量未标注柱的读数误差率 |
| P1 | 一类出版方 | 新组件 labels_on_lines_only_not_bars（同图内部分系列印值、部分不印） | 记录字段：value_label 从图级布尔改为按系列设置 | 每系列标签覆盖率（全印/仅折线/全不印）对应的可读精度 |
| P6 | 这份文档自己的习惯 | 新组件 line_label_collision_with_bars（折线数值标签落在柱体区域内） | 样式字段：标签避让策略允许与其他系列图元重叠 | 标签与异系列图元重叠时的系列归属正确率 |
| P7 | 通用 | P7式标题拆分：figure_number、title、括号单位“(percentage)”与旋转轴题“Share of GDP (%)”并存 | heading 记录字段增加 unit_text 与 rotated axis title 双载体 | 单位只在标题、只在轴题、二者并存三种情况下的单位识别率 |
