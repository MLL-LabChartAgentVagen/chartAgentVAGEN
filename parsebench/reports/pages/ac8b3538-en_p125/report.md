# ac8b3538-en_p125

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ac8b3538-en | `3d_chart+need_estimate` | 10 | 10 |

本页为 OECD Employment Outlook 2024 第123页，含一个两面板（A 绿色驱动职业、B 温室气体密集职业）的哑铃/区间点图，以及上一页图表遗留的 Source 与 StatLink 行。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 45 | `A. Green-driven occupations` · `SVK` · `Low` | 5% | f1 | the SVK `Low` dot in panel A, the highest point on the page | 否 | `A. Green-driven occupations` · `SVK` · `Low` |
| 2 | 25 | `A. Green-driven occupations` · `SVK` · `Total` | 5% | f1 | the FRA `Low` dot in panel A, sitting on the 25 gridline | 否 | `A. Green-driven occupations` · `FRA` · `Low` |
| 3 | 21 | `A. Green-driven occupations` · `DEU` · `High` | 10% | f1 | the DEU `Total` dash in panel A, just above the 20 gridline | 否 | `A. Green-driven occupations` · `DEU` · `Total` |
| 4 | 29 | `A. Green-driven occupations` · `EST` · `Medium` | 5% | f1 | the HUN `Medium` dot in panel A, near 29 | 否 | `A. Green-driven occupations` · `HUN` · `Medium` |
| 5 | 23 | `B. GHG-intensive occupations` · `POL` · `Low` | 5% | f1 | the DEU `Low` dot in panel A, the top of the first connector | 否 | `A. Green-driven occupations` · `DEU` · `Low` |
| 6 | 11 | `B. GHG-intensive occupations` · `POL` · `Total` | 10% | f1 | the CAN `Low` dot in panel B, top of the first connector | 否 | `B. GHG-intensive occupations` · `CAN` · `Low` |
| 7 | 17 | `B. GHG-intensive occupations` · `IRL` · `Low` | 10% | f1 | the IRL `Low` dot in panel B, just above 17 | 否 | `B. GHG-intensive occupations` · `IRL` · `Low` |
| 8 | 13 | `B. GHG-intensive occupations` · `LTU` · `Medium` | 10% | f1 | the LTU `Medium` dot in panel B, at about 13 | 否 | `B. GHG-intensive occupations` · `LTU` · `Medium` |
| 9 | 4.5 | `B. GHG-intensive occupations` · `CAN` · `High` | 10% | f1 | the CAN `High` dot in panel B, the lowest mark of the first connector | 否 | `B. GHG-intensive occupations` · `CAN` · `High` |
| 10 | 14 | `B. GHG-intensive occupations` · `AUS` · `Low` | 5% | f1 | the POL `Medium` dot in panel B, just under 14 | 否 | `B. GHG-intensive occupations` · `POL` · `Medium` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——6 of 10 predicted key sets miss a rule label: 25, 21, 29, 23, 11, 14

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `other · dumbbell range plot` | vertical | 2 | 4 | 30 | 240 | 无 | A: 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50; B: 0, 5, 10, 15, 20, 25 |

- **f1** Annex Figure 2.C.7. / GHG-intensive occupations are more likely low educated while green-driven occupations are more heterogeneous / Percentages, average 2015-19　[图上方]　单位 `%`
  - 来源行：Source: Secretariat's estimates based on version 24.1 of the O*NET database and the following country-specific sources: United States: Current Population Survey; All other countries: EU Labour Force Survey.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | panel A axis ends at 50, panel B at 25, both starting at 0 |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend shows `Total` as a short black dash; the dash sits on each country's connector line |
| `range_connector_line` | 每个类目两个点用线段连成区间（哑铃图 / 区间图） | f1 | **无** | three coloured dots per country joined by a thin vertical segment in both panels |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one legend strip `High  Medium  Low  Total` above panel A governs panels A and B |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | two panels of the same dumbbell construction, A and B |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Note: Countries are ranked by decreasing gap...` then `Source: Secretariat's estimates...` under panel B |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | grey legend band sits between the subtitle `Percentages, average 2015-19` and panel A |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | `A. Green-driven occupations` and `B. GHG-intensive occupations` printed above each plot |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | `StatLink` glyph with `https://stat.link/6nria2` under the source line |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | scale word only in `Percentages, average 2015-19` and the `%` head; ticks are bare numbers |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | `%` printed above the topmost tick (50 in A, 25 in B) at the axis head |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | country codes set at roughly 45 degrees under both panels |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | x labels are ISO codes: `DEU`, `CHE`, `CAN`, ... `OECD`, `SVK` |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | both plot areas carry a light grey tint against the white page |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 5-unit ticks, no vertical rules in either panel |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 2 panels x 30 countries x 4 series = about 240 dots and dashes |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the `OECD` slot's dots and dash are drawn with a heavy black outline in both panels |

词表 65 项，本页出现 17 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `orphan_source_block_from_previous_figure` | page | page opens with `Source: Source Secretariat's estimates...` and `StatLink https://stat.link/ai0tc1` for a figure not on this page | 页首的 Source/StatLink 不属于本页图，解析时若把它当作 2.C.7 的来源行，会给本页数值挂上错误的出处与数据链接。 |
| `three_point_distribution_with_aggregate_dash` | f1 | High/Medium/Low dots plus a `Total` dash share one vertical line per country slot | 同一横坐标位置上有四个不同语义的标记，取值必须同时指明国家、面板与教育水平（或 Total），否则一行表格会指向多个点。 |
| `ranking_rule_in_note` | f1 | `Note: Countries are ranked by decreasing gap of the share for high education compared to the total.` | 两面板的国家顺序不同且由注释规则决定，不能按字母或共同顺序对齐读数，须逐面板按打印顺序定位。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

面板 A 刻度间距为 5 个百分点（0–50），面板 B 同样是 5 个百分点（0–25），而图上没有任何数字标注，全部读数必须靠像素对齐网格线。以 21 为例，5% 容差只有 ±1.05，不到一个刻度格的四分之一；面板 B 的 4.5 更极端，±0.23 相当于一格的 1/22，在 150 dpi 下一格约十几像素，几乎无法分辨。加之每个国家槽位挤了 High/Medium/Low 三点加一个 Total 短划，30 个槽位横向仅约 30 px，点与点纵向常相隔 1–2 个百分点，先定位再读值的误差远超容差；标签虽然要三个键（面板名+国家代码+系列名）但都是印在页上的短词，相对可控。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P4 | 一类出版方 | range_connector_line 与 tick_marker_as_series 的组合（三点分布＋Total 短划） | 图表族生成条件行：新增 dumbbell/range 家族，并允许在同一类别槽位放 3 个点标记加 1 个 dash 系列 | 「同槽位多标记的区间图 vs 普通分组柱」在数值定位准确率上的对比行 |
| P2 | 通用 | per_panel_axis_range（A 轴到 50、B 轴到 25）与 panel_key | 记录字段中加入 panel_key，并在样式条件里允许各面板独立的轴上限 | 「带 panel_key 的导出 vs 面板名仅出现在表外」的取值命中率行 |
| P6 | 一类出版方 | axis_title_above_axis（`%` 置于顶端刻度之上）与 unit_in_axis_or_title | 样式字段 unit_position：新增 above_top_tick 选项，标题/副标题只承载 `Percentages, average 2015-19` | 「单位在轴头符号处 vs 在轴标题处」对单位恢复率的影响行 |
| P6 | 一类出版方 | highlighted_category（OECD 点带黑色描边） | 样式条件行：聚合类别的强调方式增加“描边而非换色” | 「聚合项以描边强调 vs 以异色强调」在聚合行识别上的对比行 |
| P3 | 这份文档自己的习惯 | new_components 中的 orphan_source_block_from_previous_figure | 整页 markdown 导出规则：页首孤立的 Source/StatLink 不得绑定到本页图号 | 「页首遗留来源行是否归属本页图」对来源/链接错配率的行 |
| P7 | 通用 | P7 的标题五分拆：`Annex Figure 2.C.7.` ＋长标题 ＋`Percentages, average 2015-19` ＋`%` ＋panel 标题 | figure 标题记录字段：number/title/subtitle/unit/placement 独立存放，panel 标题另存 | 「标题拆五段 vs 单行标题」在含面板名的上下文匹配上的行 |
