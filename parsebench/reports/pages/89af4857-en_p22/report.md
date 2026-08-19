# 89af4857-en_p22

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 89af4857-en | `need_estimate` | 10 | 10 |

该页上半部为OECD《Economic Outlook Interim Report March 2025》的Figure 11分组柱状图（2007Q4与2024Q3各国政府总债务占GDP比重，日本单列并使用右侧不同刻度轴），下半部为第33段正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 38 | `TUR` · `2007Q4` | 10% | f1 | the TUR 2007Q4 green bar, read on the left axis | 否 | `TUR` · `2007Q4` · `% of GDP` |
| 2 | 27 | `TUR` · `2024Q3 or latest available` | 20% | f1 | the TUR 2024Q3 orange bar, read on the left axis | 否 | `TUR` · `2024Q3 or latest available` · `% of GDP` |
| 3 | 225 | `JPN` · `2024Q3 or latest available` | 5% | f1 | the JPN 2024Q3 orange bar, right of the divider, read on the right axis | 否 | `JPN` · `2024Q3 or latest available` · `% of GDP` |
| 4 | 152 | `JPN` · `2007Q4` | 5% | f1 | the JPN 2007Q4 green bar, right of the divider, read on the right axis | 否 | `JPN` · `2007Q4` · `% of GDP` |
| 5 | 122 | `USA` · `2024Q3 or latest available` | 5% | f1 | the USA 2024Q3 orange bar, just above the 120 gridline on the left axis | 否 | `USA` · `2024Q3 or latest available` · `% of GDP` |
| 6 | 64 | `USA` · `2007Q4` | 10% | f1 | the USA 2007Q4 green bar, just above the 60 gridline | 否 | `USA` · `2007Q4` · `% of GDP` |
| 7 | 135 | `ITA` · `2024Q3 or latest available` | 5% | f1 | the ITA 2024Q3 orange bar, the tallest bar left of the divider | 否 | `ITA` · `2024Q3 or latest available` · `% of GDP` |
| 8 | 87 | `CHN` · `2024Q3 or latest available` | 10% | f1 | the BRA 2024Q3 orange bar, just below the 90 gridline | 否 | `BRA` · `2024Q3 or latest available` · `% of GDP` |
| 9 | 88 | `BRA` · `2024Q3 or latest available` | 10% | f1 | the CHN 2024Q3 orange bar, just below the 90 gridline | 否 | `CHN` · `2024Q3 or latest available` · `% of GDP` |
| 10 | 64 | `DEU` · `2007Q4` | 10% | f1 | the FRA 2007Q4 green bar, slightly above the 60 gridline | 否 | `FRA` · `2007Q4` · `% of GDP` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 87, 88, 64

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 1 | 2 | 18 | 36 | 无 | 0, 30, 60, 90, 120, 150 (left); 0, 50, 100, 150, 200, 250 (right) |

- **f1** Figure 11. / Public debt levels have increased / Gross debt　[图上方]　单位 `% of GDP`
  - 来源行：Source: Eurostat; IMF Sovereign Debt Investor Base database; OECD Economic Outlook 116 database; Office for National Statistics; and OECD calculations.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | two bars, green and orange, side by side in each country slot such as TUR, IDN, MEX |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: The chart shows general government financial liabilities...' and 'Source: Eurostat; IMF Sovereign Debt Investor Base database; ...' |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | the '2007Q4' / '2024Q3 or latest available' key boxes are drawn over the plot area near the top |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 0-150 and 0-250; scale word only in '% of GDP' above the axes |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | '% of GDP' printed above the 150 tick on the left and above the 250 tick on the right |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | category axis reads TUR IDN MEX KOR AUS DEU ZAF IND CHN BRA GBR ESP CAN ARG FRA USA ITA JPN |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | thin horizontal rules at 30, 60, 90, 120 across the panel, no vertical grid |

词表 65 项，本页出现 7 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `secondary_scale_for_one_category` | f1 | JPN sits right of a vertical rule and is read on the right axis 0-250 while the others use left 0-150 | 同一单位（% of GDP）却有两套刻度：若把JPN的柱按左轴读，2024Q3会得到约135而非225，读数会整体偏低约40%。 |
| `vertical_panel_divider` | f1 | a thick black vertical rule between ITA and JPN splitting the plot area into two zones | 这条竖线是判定某柱该用左轴还是右轴的唯一线索，缺失时无法确定JPN两根柱的量级。 |
| `duplicated_axis_title_both_sides` | f1 | '% of GDP' appears twice, once above the left axis and once above the right axis | 两侧单位文字相同，容易让人误以为两轴同刻度，需靠刻度数字自行区分。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

柱上完全没有数值标注，全部10个目标值都要靠像素对刻度反推。左轴刻度间隔为30个百分点（约57px），TUR的27在5%容差下只允许±1.35pp，即约±2.5px，必须做亚刻度插值；CHN 88与BRA 87相差仅1pp（不到2px），二者的行几乎无法区分。更棘手的是JPN被竖线隔开后改用右轴（间隔50），225与152若误按左轴读只有约135与91，误差超过40%，远超容差；因此“读数”而非“标签”是主要障碍——寻址只需国家代码+图例名两个键。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | 新增组件 secondary_scale_for_one_category（离群类别单列并使用第二套刻度） | 条件行增加“同单位双刻度/分区轴”开关，样式字段记录分隔线位置与右轴刻度范围，记录字段需为每个mark标注所属刻度轴 | “单轴 vs 同单位双刻度（离群类别分区）”一行，比较模型是否把分区柱按错轴读出（如JPN 225被读成135） |
| P6 | 一类出版方 | 补充 axis_title_above_axis 与两侧重复单位文字（'% of GDP' 出现在左右轴顶端）的抽取 | 标题/单位位置样式字段：unit_position 增加 above_left_axis + above_right_axis 组合 | “单位置于轴顶且左右重复 vs 单位置于副标题”一行，检验单位归属与刻度对应是否被正确绑定 |
| P7 | 通用 | heading 五段拆分：figure_number 'Figure 11.'、title、subtitle 'Gross debt'、unit '% of GDP' | 记录字段把标题拆为编号/主标题/副标题/单位四项，并记录heading块位于plot之上 | “导出markdown中是否以粗体标题携带 Figure 11. + Gross debt 上下文”一行 |
| P1 | 通用 | 无数值标注（values_printed=none）下的每-mark可达精度 | 评测把readable从布尔门改为按刻度间隔（此图30pp/50pp）折算的每柱容差 | “刻度间隔30 vs 10时的柱高读数命中率”一行 |
