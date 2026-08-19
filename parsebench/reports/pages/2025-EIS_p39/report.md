# 2025-EIS_p39

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2025-EIS | `need_estimate` | 10 | 10 |

本页是《European Innovation Scoreboard 2025》第37页，仅含Figure 12：EU27成员国在Digitalisation维度上的横向条形图，条形为2025年得分，另叠加菱形（2018）和竖线（2024）标记。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 215 | `Netherlands` · `Score in 2018` | 5% | f1 | the Netherlands diamond (Score in 2018) | 否 | `Netherlands` · `Score in 2018` · `Digitalisation` |
| 2 | 230 | `Netherlands` · `Innovation leaders` | 5% | f1 | the Netherlands bar end (2025 score, longest bar) | 否 | `Netherlands` · `Score for dimension 1.3 in 2025 (indexed to the EU in 2018)` · `Digitalisation` |
| 3 | 110 | `Germany` · `Score in 2024` | 5% | f1 | the Bulgaria bar end (2025 score, Emerging innovators colour) | 否 | `Bulgaria` · `Score for dimension 1.3 in 2025 (indexed to the EU in 2018)` · `Digitalisation` |
| 4 | 158 | `France` · `Strong innovators` | 5% | f1 | the Estonia bar end (2025 score) | 否 | `Estonia` · `Score for dimension 1.3 in 2025 (indexed to the EU in 2018)` · `Digitalisation` |
| 5 | 44 | `Greece` · `Score in 2018` | 5% | f1 | the Cyprus diamond (Score in 2018), leftmost diamond in the figure | 否 | `Cyprus` · `Score in 2018` · `Digitalisation` |
| 6 | 196 | `Malta` · `Moderate innovators` | 5% | f1 | the Spain bar end (2025 score) | 否 | `Spain` · `Score for dimension 1.3 in 2025 (indexed to the EU in 2018)` · `Digitalisation` |
| 7 | 132 | `Poland` · `Moderate innovators` | 5% | f1 | the Lithuania vertical tick (Score in 2024) | 否 | `Lithuania` · `Score in 2024` · `Digitalisation` |
| 8 | 153 | `Hungary` · `Emerging innovators` | 5% | f1 | the Hungary bar end (2025 score) | 否 | `Hungary` · `Score for dimension 1.3 in 2025 (indexed to the EU in 2018)` · `Digitalisation` |
| 9 | 75 | `Bulgaria` · `Score in 2018` | 5% | f1 | the Austria diamond (Score in 2018) | 否 | `Austria` · `Score in 2018` · `Digitalisation` |
| 10 | 100 | `EU` · `Score in 2018` | 5% | f1 | the EU diamond (Score in 2018), the index base sitting exactly on the 100 tick | 否 | `EU` · `Score in 2018` · `Digitalisation` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——8 of 10 predicted key sets miss a rule label: 230, 110, 158, 44, 196, 132

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | horizontal | 1 | 6 | 28 | 84 | 无 | 0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240 |

- **f1** Figure 12 / Innovation performance of the EU27 Member States in the Digitalisation dimension / Digitalisation　[图上方]　单位 `Score for dimension 1.3 in 2025 (indexed to the EU in 2018)`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | diamond markers and short vertical tick marks are overlaid on every horizontal bar |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names sit on the y axis, bars grow rightwards to the 0-240 axis |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | not applicable-omitted |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | "The colours denote each country's overall performance group based on the 2025 SII" |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend: "\| Score in 2024" drawn as a short vertical dash on each bar |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | italic "Note: All performance scores are relative to that of the EU in 2018..." under the legend |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two legend rows with colour swatches sit under the axis title, outside the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis line reads "Score for dimension 1.3 in 2025 (indexed to the EU in 2018)"; ticks bare numbers |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | the score axis title is printed below the 0-240 tick row, centred |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | "(indexed to the EU in 2018)"; note: "scores are relative to that of the EU in 2018" |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 28 country names stack down the y axis from Netherlands to Greece |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the "EU" row bar is dark blue, unlike the four legend group colours |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | faint vertical rules at the 20-unit ticks run up through the plot, no horizontal rules |

词表 65 项，本页出现 13 项，其中我们画不出来的 9 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `unlabelled_primary_series` | f1 | legend names only innovator groups plus "Score in 2018"/"Score in 2024"; the bar's own year appears only in the axis title | 条形本身（2025年得分）在图例中没有系列名，读者必须从坐标轴标题"Score for dimension 1.3 in 2025"推出年份，表格行难以只用图例词唯一定位该值。 |
| `dimension_label_above_plot` | f1 | bold blue "Digitalisation" sits left-aligned between the caption and the plot area | 该蓝色标签是维度名而非图题，若解析器把它当作独立标题或忽略，行标签与维度上下文会脱钩。 |
| `category_sorted_by_value` | f1 | rows run Netherlands 230 down to Greece, ordered by 2025 bar length | 类别顺序本身携带排名信息，读数时可用相邻行长度互相校验，也意味着行序不是字母序。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

最卡的是标签：一个值要同时被"国家名"+"哪一个系列"锁定，而28行中最长的条形（2025年得分）在图例里根本没有年份名——图例四个色块写的是"Emerging innovators"等绩效组，年份只出现在轴标题"Score for dimension 1.3 in 2025 (indexed to the EU in 2018)"里，因此Spain=196这类行必须借轴标题措辞才能与"Score in 2018"(=186附近的菱形)、"Score in 2024"(竖线)区分，三个数值在同一行内相距仅约10个单位。读数本身次难：刻度每20单位约56像素，5%容差对44而言只有±2.2单位≈6像素，对100以上的值反而宽松，所以主要风险仍在行/列命名而非像素。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | tick_marker_as_series（竖线刻度作为一个系列）与 mixed_marks 的组合 | 样式字段中新增 marker_style: tick / diamond，允许在同一条形上叠加两个点状系列 | "条形+叠加点/刻度系列" vs "纯条形"：比较同一行内多系列被正确归属的比例 |
| P7 | 这份文档自己的习惯 | unlabelled_primary_series（主系列年份只在轴标题中出现） | 记录字段：series_name 可为空，年份/口径信息只写入 axis_title 或 unit_text | "主系列有图例名" vs "主系列名仅存于轴标题"：检验 addressing_keys 的可构造性 |
| P6 | 一类出版方 | color_encodes_extra_attribute + highlighted_category（颜色表示绩效组、EU行单独着色） | 条件行中新增 color_meaning=group_attribute，并允许一行使用保留色（aggregate 行） | "颜色=系列身份" vs "颜色=额外分组属性"：看模型是否把色块图例误当作系列列 |
| P7 | 通用 | axis_title_below_plot 与 rebased_index_values 的单位承载位置 | 标题块字段：unit_text 独立成域，并记录其相对绘图区位置（below/beside） | "单位在轴旁" vs "单位在绘图区下方整句"：检验导出表格是否保留指数基期 |
| P5 | 一类出版方 | wrapped_category_labels 下的高密度类别（28行×3标记=84个mark） | 密度上限设置：把 categories 上限提到28以上，marks 到80以上 | "≤12类别" vs "25+类别横向条形"：按行数分层统计定位错行率 |
