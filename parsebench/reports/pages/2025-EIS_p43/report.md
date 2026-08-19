# 2025-EIS_p43

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2025-EIS | `need_estimate` | 9 | 9 |

本页只有一张图（Figure 14），为EU27成员国在"Firm investments"维度的横向条形图，条形代表2025年得分，菱形和竖线分别叠加2018与2024年得分。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 150 | `Sweden` · `Innovation leaders` | 5% | f1 | the Sweden 2025 bar, read at the bar end just below the axis position of 150 | 否 | `Sweden` · `Score for dimension 2.2 in 2025 (indexed to the EU in 2018)` · `Firm investments` |
| 2 | 148 | `Sweden` · `Score in 2018` | 5% | f1 | the Sweden 2018 diamond, sitting slightly left of the bar end | 否 | `Sweden` · `Score in 2018` · `Firm investments` |
| 3 | 140 | `Sweden` · `Score in 2024` | 2% | f1 | the Sweden 2024 vertical tick marker, left of the diamond | 否 | `Sweden` · `Score in 2024` · `Firm investments` |
| 4 | 145 | `Belgium` · `Strong innovators` | 3% | f1 | the Germany 2025 bar end (Belgium's bar is nearly the same length, so the row label is essential) | 否 | `Germany` · `Score for dimension 2.2 in 2025 (indexed to the EU in 2018)` · `Firm investments` |
| 5 | 130 | `Malta` · `Moderate innovators` | 5% | f1 | the Malta 2025 bar end | 否 | `Malta` · `Score for dimension 2.2 in 2025 (indexed to the EU in 2018)` · `Firm investments` |
| 6 | 54 | `Malta` · `Score in 2018` | 5% | f1 | the Slovakia 2025 bar end, between the 40 and 60 ticks | 否 | `Slovakia` · `Score for dimension 2.2 in 2025 (indexed to the EU in 2018)` · `Firm investments` |
| 7 | 116 | `Czechia` · `Score in 2024` | 5% | f1 | the Czechia 2024 vertical tick marker, far right of its short bar | 否 | `Czechia` · `Score in 2024` · `Firm investments` |
| 8 | 16 | `Romania` · `Emerging innovators` | 10% | f1 | the Romania 2025 bar end, the shortest bar | 否 | `Romania` · `Score for dimension 2.2 in 2025 (indexed to the EU in 2018)` · `Firm investments` |
| 9 | 92 | `Estonia` · `Score in 2018` | 5% | f1 | the France 2025 bar end, just left of 100 | 否 | `France` · `Score for dimension 2.2 in 2025 (indexed to the EU in 2018)` · `Firm investments` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——6 of 9 predicted key sets miss a rule label: 150, 145, 130, 54, 16, 92
- 标了 dense_marks_100plus，但没有图达到 100 个图元——dense_marks_100plus claimed, densest figure has 84 marks

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | horizontal | 1 | 6 | 28 | 84 | 无 | 0, 20, 40, 60, 80, 100, 120, 140, 160 |

- **f1** Figure 14 / Innovation performance of the EU27 Member States in the Firm investments dimension / Firm investments　[图上方]　单位 `Score for dimension 2.2 in 2025 (indexed to the EU in 2018)`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | diamond markers and short vertical tick markers overlaid on the horizontal bars |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names on the y axis, coloured bars grow rightwards from 0 |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | bar fill denotes performance group: "Emerging innovators", "Moderate innovators", "Strong innovators", "Innovation leaders" |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend entry "Score in 2024" drawn as a short vertical dash on each bar row |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: All performance scores are relative to that of the EU in 2018 for each dimension." |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two rows of legend swatches sit under the axis title, outside the plot |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | "Firm investments" set in bold blue above the plot area, separate from the caption |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis title carries "(indexed to the EU in 2018)"; the axis itself shows bare 0-160 |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | "Score for dimension 2.2 in 2025 (indexed to the EU in 2018)" centred beneath the x axis |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | "indexed to the EU in 2018" and note "scores are relative to that of the EU in 2018" |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 28 country labels stacked down the y axis, from Sweden to Romania |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 28 rows times three marks (bar, diamond, 2024 tick) is 84 marks, just under 100 |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the "EU" row is drawn in dark blue, unlike all country group colours |

词表 65 项，本页出现 13 项，其中我们画不出来的 9 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `bullet_style_bar_with_two_overlaid_reference_marks` | f1 | each bar carries both a diamond (2018) and a vertical tick (2024) at their own score positions | 同一行有三个可读数值（2025条长、2018菱形、2024竖线），表格行必须同时指明国家与年份，否则读数无法唯一定位。 |
| `legend_two_row_grid` | f1 | legend laid out as a 2-row by 3-column grid: colour groups left, marker series right | 图例分两行排布，颜色组与标记序列混排，解析时容易把标记序列误当成条形类别。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

图上没有任何数字，一个数值需要同时锁定国家行（28行）与三种量之一（2025条形、Score in 2018菱形、Score in 2024竖线）。例如Sweden一行就有150/148/140三个值，若表格只按国家列出一列分数，148与140便无法被寻址；116属于Czechia的2024竖线，却画在远离其条形处，更易被误归到相邻行。相比之下取值精度尚可：刻度间隔20，5%容差在100附近约±5，约为四分之一格宽，肉眼可控。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | tick_marker_as_series 与 mixed_marks 的组合（条形上叠加菱形与竖线标记） | 图表族生成条件行：在horizontal_bars族中增加"overlay_marker_series"样式字段，指定标记形状（diamond/vertical tick）与所属年份 | 新增一行：条形+叠加标记序列 vs 纯条形，比较同一类别下多值寻址的正确率 |
| P6 | 一类出版方 | highlighted_category（EU 聚合行单独着色） | 样式字段中加入"aggregate_row_color"，并在记录中标注该类别为聚合项 | 新增一行：含聚合高亮行 vs 全同色，检验模型是否把聚合行误读为普通类别 |
| P7 | 通用 | axis_title_below_plot 与 unit_in_axis_or_title 的组合（"Score for dimension 2.2 in 2025 (indexed to the EU in 2018)"置于轴下） | 标题记录字段：拆出unit_text并允许placement=below-axis | 新增一行：单位仅出现在轴下标题 vs 出现在图题，测量导出表格是否保留指数基期信息 |
| new | 一类出版方 | 色块图例编码分组属性（Emerging/Moderate/Strong innovators、Innovation leaders） | 记录字段中为每个类别增加group属性，图例由group而非series驱动 | 新增一行：颜色编码额外属性 vs 颜色仅编码序列，检验表格是否额外输出分组列 |
