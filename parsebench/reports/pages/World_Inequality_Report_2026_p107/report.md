# World_Inequality_Report_2026_p107

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `need_estimate` | 7 | 7 |

本页顶部为 Figure 5.3 的双面板折线图（按收入组与按世界区域的净外国资产占世界 GDP 比重，1970–2025），下方为两栏正文与 Interpretation/来源说明。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 4 | `Top 20%` · `1990` | 10% | f1 | the 2025 endpoint of the Europe line in the By world region panel, level with the 4% tick | 否 | `By world region` · `Europe` · `2020` |
| 2 | 2.6 | `Top 20%` · `2020` | 10% | f1 | the 1970 starting point of the Top 20% line in the By income group panel | 否 | `By income group` · `Top 20%` · `1970` |
| 3 | -2.2 | `60%–80%` · `1980` | 10% | f1 | the 2025 endpoint of the 40%–60% line in the By income group panel, just below -2% | 否 | `By income group` · `40%–60%` · `2020` |
| 4 | -17 | `NAOC` · `2020` | 10% | f1 | the 2025 endpoint of the NAOC line in the By world region panel, between -16% and -20% | 否 | `By world region` · `NAOC` · `2020` |
| 5 | 6.2 | `EASA (excl. China)` · `2010` | 10% | f1 | the EASA (excl. China) line in the By world region panel around 2015, between the 4% and 8% ticks | 否 | `By world region` · `EASA (excl. China)` · `2010` |
| 6 | 2 | `Europe` · `1970` | 30% | f1 | the 2025 endpoint of the Top 20% line, described in the note as 'nearly 2% of world GDP in 2025' | 否 | `By income group` · `Top 20%` · `2020` |
| 7 | 2 | `China` · `2010` | 30% | f1 | the 2025 endpoint of the 60%–80% line in the By income group panel, at about the 2% tick | 否 | `By income group` · `60%–80%` · `2020` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 7 predicted key sets miss a rule label: 4, 2.6, -2.2, 2, 2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 2 | 14 | 6 | 784 | 无 | left panel: -6%, -4%, -2%, 0%, 2%, 4%, 6%; right panel: -20%, -16%, -12%, -8%, -4%, 0%, 4%, 8% |

- **f1** Figure 5.3. / Privilege persists for the U.S. (and its region) despite negative net foreign asset positions / Net foreign assets as % of world GDP, 1970–2025　[图上方]　单位 `Net foreign assets (% of world GDP), MER`
  - 来源行：Sources and series: Nievas and Sodano (2025) and wir2026.wid.world/methodology.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a black dotted horizontal rule drawn at 0% across both panels |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | left axis runs to -6%, right axis to -20%; NAOC line sits far below the 0% rule |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left panel ticks -6%..6% by 2, right panel -20%..8% by 4 |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | two side-by-side panels of the same line chart: 'By income group', 'By world region' |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Interpretation. These panels show net foreign assets (NFA)...' and 'Sources and series: Nievas and Sodano (2025)...' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | both legends sit under their plots, below the x tick row |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | five income-group entries under the left plot, nine region entries under the right plot |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | 'By income group' and 'By world region' set in bold above each plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | subtitle 'Net foreign assets as % of world GDP, 1970–2025'; ticks read only '4%', '0%' |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'Net foreign assets (% of world GDP), MER' set vertically along the left panel axis |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | legend codes 'EASA (excl. China)', 'LATA', 'MENA', 'NAOC', 'RUCA', 'SSAF', 'SSEA' |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | lines are annual 1970–2025 but ticks appear only at 1970, 1980, 1990, 2000, 2010, 2020 |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 5 + 9 annual series over ~56 years, roughly 780 plotted points |

词表 65 项，本页出现 13 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `legend_multicolumn_grid` | f1 | right legend laid out as three columns x three rows: China/LATA/RUCA, EASA/MENA/SSAF, Europe/NAOC/SSEA | 图例按网格排布，读者需按列而非按行匹配颜色，解析器容易把同一行的三个不同系列名串成一条记录。 |
| `interpretation_note_block` | f1 | bold-lead paragraph 'Interpretation.' stating 'nearly 2% of world GDP in 2025' before the sources line | 图中不印数值，唯一可核对的数字（约 2%）只存在于这段解释文字里，取值必须回到正文而非图面。 |
| `abbrev_series_names` | f1 | series identified only by codes 'NAOC', 'RUCA', 'SSEA' with no expansion anywhere on the page | 表格行名若只写代码，无法确认其地理范围，定位某一条线的值时缺少可读的行标签。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

取值精度是真正的瓶颈：图上没有任何印刷数字，左面板刻度间距为 2 个百分点（约 30 px），要把 2.6 读到 5% 容差内即 ±0.13 个百分点，相当于约 2 px；-2.2 的容差只有 ±0.11 个百分点，而 40%–60%、20%–40%、Bottom 20% 三条线在 -1% 至 -2% 之间反复交叠。右面板刻度更粗（4 个百分点一档），-17 的容差 ±0.85 个百分点尚可，但 6.2 需在 4% 与 8% 之间内插到 ±0.31 个百分点。加之 x 轴每 10 年一个刻度、年度点须在刻度间定位，像素读数几乎不可能稳定达标。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | per_panel_axis_range 与 panel_title_per_panel 组合（面板名进入键） | 记录字段增加 panel_key，并允许每个面板独立的 value_axis 范围与刻度步长 | 新增一行：同一图内两面板刻度步长不同（2pp vs 4pp）时的取值命中率，对比强制共享刻度 |
| P7 | 一类出版方 | P7 式的标题五分拆：figure_number / title / subtitle / 旋转轴标题承载单位 | 标题样式字段中增加 unit 位置选项：rotated_axis_title 与 subtitle 同时出现 | 新增一行：单位只出现在竖排轴标题（'Net foreign assets (% of world GDP), MER'）时，单位识别率 |
| P5 | 通用 | dense_marks_100plus（约 780 个年度点、14 条系列） | 密度上限参数，允许 series×categories 达到 500 以上的折线生成 | 新增一行：单图 marks 从 100 提到 800 时，指定 (面板, 系列, 年份) 的取值误差分布 |
| P6 | 通用 | negative_values 与 0% 处 dotted reference_line 的组合，以及带 % 的刻度格式 | 样式维度中的零线绘制方式（虚线/实线）与刻度文本后缀（'4%' 而非 '4'） | 新增一行：零线为虚线且轴刻度带 % 后缀时，负值符号与数量级的读取错误率 |
| new | 一类出版方 | 新组件 legend_multicolumn_grid（三列网格图例）与 per_panel_legend | 图例布局字段增加列数参数，并允许每面板独立图例 | 新增一行：图例按 3 列网格排布 vs 单行排布时，系列名与颜色配对的正确率 |
