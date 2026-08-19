# World_Inequality_Report_2026_p36

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `need_estimate` | 10 | 10 |

该页顶部为编号图 Figure 1.1「The world is becoming richer」的双对数双纵轴折线图（人均国民收入与世界人口，1800–2025），下方为两栏正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 600 | `1800` · `National income` | 20% | not_found | the plot's lowest drawn level is near 800–900 (green line at 1800); no mark reaches 600 and the axis stops at 1,000 | 否 | — |
| 2 | 1000 | `1800` · `World population` | 5% | f1 | the World population point at 1800 (start of the red line, at the 1,000 gridline) | 否 | `World population` · `1800` · `World Population` |
| 3 | 1000 | `1850` · `National income` | 5% | f1 | the National income point around 1850, where the green line crosses the 1,000 gridline | 否 | `National income` · `1850` · `Yearly per capita national income € (at 2025 PPP), log scale` |
| 4 | 1250 | `1850` · `World population` | 5% | f1 | the World population point around 1850 (red line just above the 1,000 gridline) | 否 | `World population` · `1850` · `World Population` |
| 5 | 1800 | `1900` · `National income` | 5% | f1 | the National income point around 1900 (green line between the 1,000 and 2,000 gridlines) | 否 | `National income` · `1900` · `Yearly per capita national income € (at 2025 PPP), log scale` |
| 6 | 3500 | `1950` · `National income` | 5% | f1 | the National income point around 1960, between the 2,000 and 5,000 gridlines | 否 | `National income` · `1950` · `Yearly per capita national income € (at 2025 PPP), log scale` |
| 7 | 2400 | `1950` · `World population` | 5% | f1 | the World population point at 1950 (red line just above the 2,000 gridline) | 否 | `World population` · `1950` · `World Population` |
| 8 | 8500 | `2000` · `National income` | 5% | f1 | the World population endpoint at 2025 (red line ending just below the 10,000 gridline) | 否 | `World population` · `2025` · `World Population` |
| 9 | 13000 | `2025` · `National income` | 20% | f1 | the National income endpoint at 2025 (green line ending above the 10,000 gridline) | 否 | `National income` · `2025` · `Yearly per capita national income € (at 2025 PPP), log scale` |
| 10 | 8500 | `2025` · `World population` | 10% | f1 | the National income point around 2000, where the green line sits just under the 10,000 gridline | 否 | `National income` · `2000` · `Yearly per capita national income € (at 2025 PPP), log scale` |

**程序核对**（模型没有看到左半的标签列）：

- 有值没能落到任何一个图元上——1 of 10 values could not be put on a mark
- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 8500, 8500

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 2 | 10 | 452 | 无 | 10,000, 5,000, 2,000, 1,000 (left axis); 10,000, 5,000, 2,000, 1,000 (right axis) |
| f1 | `line` | vertical | 1 | 2 | 10 | 452 | 无 | 10,000, 5,000, 2,000, 1,000 (left axis); 10,000, 5,000, 2,000, 1,000 (right axis) |

- **f1** Figure 1.1 / The world is becoming richer / Per capita income and population, 1800–2025　[图上方]　单位 `Yearly per capita national income € (at 2025 PPP), log scale`
  - 来源行：Interpretation. World population increased from 1 billion in 1800 to 8 billion in 2025, corresponding to an average annual growth rate of about 0.9% per year. Yearly income per person increased from about €900 in 1800 to about €14,000 in 2025, a multiplication by about 16 (corresponding to average annual growth rate of about 1.2% per year). Sources and series: Gómez–Carrera et al. (2025), Nievas and Piketty (2025), and wir2026.wid.world/methodology.
- **f1** Figure 1.1 / The world is becoming richer / Per capita income and population, 1800–2025　[与图并排]　单位 `World Population`
  - 来源行：Interpretation. World population increased from 1 billion in 1800 to 8 billion in 2025, corresponding to an average annual growth rate of about 0.9% per year. Yearly income per person increased from about €900 in 1800 to about €14,000 in 2025, a multiplication by about 16 (corresponding to average annual growth rate of about 1.2% per year). Sources and series: Gómez–Carrera et al. (2025), Nievas and Piketty (2025), and wir2026.wid.world/methodology.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | left axis titled "Yearly per capita national income € (at 2025 PPP)", right axis titled "World Population" |
| `log_axis` | 对数轴 | f1 | 有 | axis title says "log scale"; ticks 1,000, 2,000, 5,000, 10,000 unevenly spaced |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | small print below plot: "Interpretation. ..." and "Sources and series: Gómez–Carrera et al. (2025)..." |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | "— National income  — World population" row sits under the x tick labels |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | scale word only in axis title "€ (at 2025 PPP), log scale"; ticks are bare 1,000–10,000 |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | both "Yearly per capita national income € (at 2025 PPP), log scale" and "World Population" set vertically |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | annual wiggles visible but x ticks only every 25 years: 1800, 1825, ... 2025 |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | dashed horizontal rules at 1,000, 2,000, 5,000, 10,000; no vertical rules in plot |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | two annual series spanning 1800–2025, roughly 226 points each |

词表 65 项，本页出现 9 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `twin_log_axes_identical_ticks` | f1 | left and right axes both print 1,000 / 2,000 / 5,000 / 10,000 but carry euros and population | 两侧刻度数字完全相同，读数时若不看轴标题就无法判断某点属于收入（€）还是人口（百万人），一个数值必须同时带上系列名与所属轴。 |
| `numbers_only_in_note_text` | f1 | "1 billion in 1800 to 8 billion in 2025", "about €900 ... to about €14,000" appear only in the Interpretation paragraph | 图上无数值标签，端点的权威数字只存在于注释文字中，抽取时必须把该段散文与折线端点对应起来。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，全部 10 个目标值都要靠像素反推。纵轴是对数刻度，仅有 1,000 / 2,000 / 5,000 / 10,000 四条虚线网格：1,000 与 2,000 之间约 55 像素要覆盖一倍量程，5% 容差（如 1,250±62、1,800±90）对应仅两三个像素，1,250 与 1,300 几乎无法区分；5,000–10,000 段更压缩，13,000 已在最高网格之上无刻度参照。加上时间轴每 25 年一格而数据为年度（约 226 点，marks 数为估算），要先在两格之间定位年份再在对数轴上插值，两重误差叠加使读数成为最硬的一步；相比之下系列名只需 2 个键（系列＋年份）即可寻址。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 一类出版方 | log_axis 与 dual_axis 组合（左右轴刻度标签相同但单位不同） | 条件行中增加「对数纵轴 × 双轴」组合；样式字段加 axis_scale=log 与 secondary_axis_unit | 对数轴 vs 线性轴下的每点可达精度对比行（含双轴刻度同值时的系列归属错误率） |
| P6 | 通用 | rotated_axis_title 与 unit_in_axis_or_title（单位只写在竖排轴标题里） | 标题/单位样式字段：unit_position=rotated_axis_title | 单位位置（轴标题竖排 / 副标题 / 系列名）对数值＋单位联合命中率的影响行 |
| P3 | 这份文档自己的习惯 | 新组件 numbers_only_in_note_text（关键端点数字仅出现在 Interpretation 注释段） | 记录字段新增 note_text 段，并规定其相对表格的位置（图下小字） | 注释段文字是否导出为表下正文，对端点值检索命中的增益行 |
| P6 | 通用 | sparse_time_ticks（年度数据、25 年一刻度） | 时间轴刻度密度字段 tick_every=25y 与数据频率 annual 的组合行 | 刻度间隔／数据点数比值对定位误差的敏感度行 |
| P7 | 通用 | 标题拆分为 figure_number / title / subtitle / unit（"Figure 1.1" + "The world is becoming richer" + "Per capita income and population, 1800–2025"） | 记录的 heading 字段拆五项，placement=above | 标题块整体作为一个字符串 vs 拆分五项时上下文命中率对比行 |
