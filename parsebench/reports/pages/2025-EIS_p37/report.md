# 2025-EIS_p37

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2025-EIS | `need_estimate` | 9 | 9 |

该页只有一张图：Figure 11 横向条形图，展示EU27成员国在"Attractive research systems"维度的2025年得分，并以菱形和竖线叠加2018与2024年得分。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 245 | `Luxembourg` · `Strong innovators` | 5% | f1 | the Luxembourg 2025 bar (bar end) | 否 | `Luxembourg` · `Attractive research systems` · `Score for dimension 1.2 in 2025 (indexed to the EU in 2018)` |
| 2 | 215 | `Luxembourg` · `Score in 2018` | 5% | f1 | the Denmark 2025 bar (bar end) | 否 | `Denmark` · `Attractive research systems` · `Score for dimension 1.2 in 2025 (indexed to the EU in 2018)` |
| 3 | 214 | `Denmark` · `Innovation leaders` | 5% | f1 | the Netherlands 2025 bar (bar end) | 否 | `Netherlands` · `Attractive research systems` · `Score for dimension 1.2 in 2025 (indexed to the EU in 2018)` |
| 4 | 186 | `Cyprus` · `Moderate innovators` | 5% | f1 | the Cyprus 2025 bar (bar end) | 否 | `Cyprus` · `Attractive research systems` · `Score for dimension 1.2 in 2025 (indexed to the EU in 2018)` |
| 5 | 100 | `EU` · `Score in 2018` | 5% | f1 | the EU row's diamond, i.e. the EU Score in 2018 (the index base) | 否 | `EU` · `Score in 2018` · `Attractive research systems` |
| 6 | 182 | `Belgium` · `Score in 2018` | 5% | f1 | the Ireland 2025 bar (bar end) | 否 | `Ireland` · `Attractive research systems` · `Score for dimension 1.2 in 2025 (indexed to the EU in 2018)` |
| 7 | 167 | `Malta` · `Score in 2024` | 5% | f1 | the Austria 2025 bar (bar end) | 否 | `Austria` · `Attractive research systems` · `Score for dimension 1.2 in 2025 (indexed to the EU in 2018)` |
| 8 | 37 | `Bulgaria` · `Emerging innovators` | 5% | f1 | the Bulgaria 2025 bar (bar end) | 否 | `Bulgaria` · `Attractive research systems` · `Score for dimension 1.2 in 2025 (indexed to the EU in 2018)` |
| 9 | 215 | `Netherlands` · `Score in 2024` | 5% | f1 | the Denmark vertical stroke, i.e. Score in 2024 | 否 | `Denmark` · `Score in 2024` · `Attractive research systems` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——8 of 9 predicted key sets miss a rule label: 245, 215, 214, 186, 182, 167

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | horizontal | 1 | 6 | 28 | 84 | 无 | 0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260 |

- **f1** Figure 11 / Innovation performance of the EU27 Member States in the Attractive research systems dimension / Attractive research systems　[图上方]　单位 `Score for dimension 1.2 in 2025 (indexed to the EU in 2018)`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | diamond markers and short vertical bars are drawn on top of each horizontal bar |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names on the y axis, bars grow rightwards to a 0-260 axis at the bottom |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | "The colours denote each country's overall performance group based on the 2025 SII." |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend entry "Score in 2024" is a short vertical stroke placed on each country's bar |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | italic "Note: All performance scores are relative to that of the EU in 2018..." under the legend |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two-row legend with four colour swatches plus diamond and stroke glyphs sits under the axis title |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | blue bold "Attractive research systems" set above the plot area, below the figure caption |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 0-260; the scale phrase only in "Score for dimension 1.2 in 2025 (indexed to the EU in 2018)" |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | "Score for dimension 1.2 in 2025 (indexed to the EU in 2018)" printed under the 0-260 axis |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | "indexed to the EU in 2018"; note: "scores are relative to that of the EU in 2018" |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | page | **无** | Note line: "All performance scores are relative to that of the EU in 2018 for each dimension." |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 28 country names stacked down the left axis, one per row |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the "EU" row bar is drawn in dark royal blue, unlike the four legend group colours |

词表 65 项，本页出现 12 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `sorted_descending_categories` | f1 | bars run from Luxembourg (~245) at top down to Bulgaria (~37), ranked by the 2025 value | 行序由数值排名决定而非固定名单，读某一行的值时需先按排名定位，且相邻国家数值极接近（Denmark 与 Netherlands 仅差约1）易错行。 |
| `legend_mixed_glyph_types` | f1 | legend mixes four filled colour swatches with a diamond glyph and a vertical stroke glyph | 同一图例中颜色项标识"分组"而符号项标识"年份"，取值时必须区分颜色键与符号键，否则会把2018/2024值当成条形值。 |
| `marker_may_exceed_bar_end` | f1 | Belgium's and France's 2018 diamonds sit to the right of their 2025 bar ends | 标记可能落在条形之外，读值不能假设菱形在条内，需按轴独立定位该标记。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

取值精度是主要瓶颈：横轴0-260仅每20一格，格宽约52px；Bulgaria的37要求±1.85，即不到十分之一格宽，而条形末端与竖线笔画本身就有2-3px宽。Denmark 215 与 Netherlands 214 相差不足1个单位（<1px），几乎无法从像素分辨谁是哪个值；同一行上2025条形末端、2024竖线、2018菱形三者在Denmark处几乎重合，读出"215"到底属于条形还是竖线只能靠猜。相比之下，行标签（国家名）与图例名（Score in 2018 / Score in 2024）都是明文，标签寻址反而容易。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | tick_marker_as_series 与 mixed_marks 的组合：条形上叠加菱形（历史值）与短竖线（前一年值）作为独立系列 | 图表族条件行中新增"bar + point/tick overlay"样式字段，记录每个overlay系列的标记形状与是否可越出条形末端 | 有/无 overlay 标记系列时，条形自身取值命中率的差异（考察标记遮挡条形末端的影响） |
| P6 | 一类出版方 | color_encodes_extra_attribute：填色表示国家所属绩效分组而非系列身份 | 记录层新增 color_key 字段，与 series_key 分离；图例项按"颜色组"与"符号系列"两类生成 | 颜色语义=系列 vs 颜色语义=额外属性 两种条件下，表格行寻址正确率对比 |
| P4 | 通用 | 新组件 sorted_descending_categories（按值降序的排名条形） | 类别轴生成条件行增加"排序方式：按值降序"，并在导出表中保留排名列 | 类别按固定顺序 vs 按值排序时，相邻近似值（差<1%）行的错配率 |
| P7 | 一类出版方 | axis_title_below_plot 与 rebased_index_values（"indexed to the EU in 2018"位于轴下方而非标题） | 标题块字段拆分：unit/基准短语可落在图下轴标题位，与 figure_number/title/subtitle 分开存储 | 单位与基准短语位于标题 vs 位于图下轴标题时，markdown导出中单位随表输出的比例 |
| P6 | 通用 | highlighted_category（EU行用深蓝单独着色作为参考聚合行） | 样式字段新增 highlight_category 名单，并在记录中标记该行为 aggregate | 含/不含高亮聚合行时，聚合值被误当作普通类别的比例 |
