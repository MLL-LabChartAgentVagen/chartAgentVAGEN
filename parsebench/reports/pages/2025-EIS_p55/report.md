# 2025-EIS_p55

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2025-EIS | `need_estimate` | 9 | 9 |

该页为《European Innovation Scoreboard 2025》第53页，仅含图20：EU27成员国在"Trade impacts"维度的横向条形图，条形为2025年得分，另叠加菱形（2018）与竖线（2024）标记，下方为图例与注释。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 107 | `Germany` · `Strong innovators` | 10% | f1 | the Germany 2025 bar (longest bar, top row) | 否 | `Germany` · `Trade impacts` · `Score for dimension 4.2 in 2025 (indexed to the EU in 2018)` |
| 2 | 87 | `Denmark` · `Score in 2018` | 5% | f1 | the France 2025 bar | 否 | `France` · `Trade impacts` · `Score for dimension 4.2 in 2025 (indexed to the EU in 2018)` |
| 3 | 93 | `Slovenia` · `Score in 2024` | 5% | f1 | the Ireland 2025 bar | 否 | `Ireland` · `Trade impacts` · `Score for dimension 4.2 in 2025 (indexed to the EU in 2018)` |
| 4 | 109 | `Ireland` · `Score in 2018` | 5% | f1 | the Germany diamond, i.e. Score in 2018 (rightmost diamond on the top row) | 否 | `Germany` · `Score in 2018` · `Trade impacts` |
| 5 | 95 | `Sweden` · `Innovation leaders` | 5% | f1 | the Slovenia 2025 bar | 否 | `Slovenia` · `Trade impacts` · `Score for dimension 4.2 in 2025 (indexed to the EU in 2018)` |
| 6 | 96 | `France` · `Score in 2018` | 5% | f1 | the Sweden 2025 bar | 否 | `Sweden` · `Trade impacts` · `Score for dimension 4.2 in 2025 (indexed to the EU in 2018)` |
| 7 | 74 | `Romania` · `Emerging innovators` | 5% | f1 | the Romania 2025 bar | 否 | `Romania` · `Trade impacts` · `Score for dimension 4.2 in 2025 (indexed to the EU in 2018)` |
| 8 | 58 | `Malta` · `Score in 2024` | 5% | f1 | the Luxembourg 2025 bar (bar ending just short of the 60 tick) | 否 | `Luxembourg` · `Trade impacts` · `Score for dimension 4.2 in 2025 (indexed to the EU in 2018)` |
| 9 | 44 | `Lithuania` · `Moderate innovators` | 10% | f1 | the Lithuania 2025 bar (shortest bar, bottom row) | 否 | `Lithuania` · `Trade impacts` · `Score for dimension 4.2 in 2025 (indexed to the EU in 2018)` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——9 of 9 predicted key sets miss a rule label: 107, 87, 93, 109, 95, 96

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | horizontal | 1 | 6 | 28 | 84 | 无 | 0, 20, 40, 60, 80, 100, 120 |

- **f1** Figure 20 / Innovation performance of the EU27 Member States in the Trade impacts dimension　[图上方]　单位 `Score for dimension 4.2 in 2025 (indexed to the EU in 2018)`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | a diamond and a short vertical dash are drawn on each bar row alongside the bar |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names sit on the y axis, coloured bars grow rightwards to the 0-120 axis |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | "The colours denote each country's overall performance group based on the 2025 SII" |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend entry "Score in 2024" is a short vertical dash placed on the bar row |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | italic "Note: All performance scores are relative to that of the EU in 2018..." under the figure |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two legend rows sit under the axis title, below the plot area |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | blue bold "Trade impacts" set above the plot area, repeating the dimension name |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis ticks are bare 0-120; scale word only in "Score for dimension 4.2 in 2025 (indexed to the EU in 2018)" |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | "Score for dimension 4.2 in 2025 (indexed to the EU in 2018)" printed under the tick row |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | "indexed to the EU in 2018"; "scores are relative to that of the EU in 2018" |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 28 country names stacked down the left axis, one per bar row |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the "EU" row bar is dark royal blue, unlike the four legend group colours |

词表 65 项，本页出现 12 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `unnamed_primary_series` | f1 | legend names only innovator groups plus "Score in 2018"/"Score in 2024"; the 2025 bar series has no legend entry | 条形本身（2025年得分）在图例中无名称，只能从轴标题"Score for dimension 4.2 in 2025"或注释推得，表格行要正确指向条形值需要外部文字。 |
| `marker_overlaps_bar_end` | f1 | e.g. Finland and Croatia rows: the 2018 diamond and 2024 dash sit within a few pixels of the bar end | 三个时间序列在同一行几乎重合（相差常小于2个刻度单位），肉眼难以把某个数值归到条形、菱形还是竖线上。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

定位数值本身不算最难：轴刻度每20单位约112像素，5%容差在100附近约有28像素余量，条形末端可读到±1单位。真正卡住的是标签：一行里有三个共享同一横轴的量（2025条形、Score in 2018菱形、Score in 2024竖线），而条形这个主序列在图例中根本没有名字，只能靠轴下方那行"Score for dimension 4.2 in 2025 (indexed to the EU in 2018)"命名；因此要唯一指向109就必须同时带上"Germany"+"Score in 2018"，要指向107则需"Germany"+一个图上没有作为图例项存在的2025列名，普通解析表格很难同时承载这三层键。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 一类出版方 | 新组件 unnamed_primary_series（主序列无图例名，仅靠轴标题命名） | 记录字段：为每个序列增加 series_label_source（legend / axis_title / note / none），条件行中允许主序列无图例项 | "主序列有图例名 vs 仅轴标题命名"一行，检验取值时能否正确归列 |
| P6 | 一类出版方 | tick_marker_as_series 与 mixed_marks 同时出现（菱形+竖线叠在条形上） | 样式字段：overlay_marker_shapes，允许在同一类别行放置1-2个与条形共轴的标记序列 | "条形单独 vs 条形+2个共轴标记序列"一行，量化重合标记造成的归属错误 |
| new | 一类出版方 | color_encodes_extra_attribute（颜色表示2025 SII绩效组，而非序列身份） | 条件行：为类别增加 group_attribute 字段，并由它驱动填色与图例 | "颜色=序列 vs 颜色=类别属性"一行，检验图例项数与序列数不一致时的解析 |
| P7 | 通用 | axis_title_below_plot 与 unit_in_axis_or_title、rebased_index_values 的组合 | 标题块字段：unit_text 独立于 title，placement 支持轴下方文本 | "单位在标题 vs 单位在轴下方独立行"一行，检验导出表能否带上指数基准 |
| P6 | 一类出版方 | highlighted_category（EU行用深蓝突出为聚合参考） | 样式字段：highlight_category 指定某一行使用图例外的颜色 | "含聚合高亮行 vs 不含"一行，检验聚合行是否被误当作新序列 |
