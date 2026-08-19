# 2025-EIS_p57

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2025-EIS | `need_estimate` | 9 | 9 |

该页只有一张图（Figure 21），是欧洲创新记分牌2025中EU27成员国在"Resource and labour productivity"维度上的横向条形图，条形为2025年得分，另叠加菱形（2018）与竖线（2024）两组标记，下方有图例与注释。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 250 | `Ireland` · `Strong innovators` | 5% | f1 | the Ireland 2025 bar (bar end, longest in the figure) | 否 | `Ireland` · `Score for dimension 4.3 in 2025 (indexed to the EU in 2018)` |
| 2 | 168 | `Ireland` · `Score in 2018` | 5% | f1 | the Ireland diamond marker (Score in 2018) | 否 | `Ireland` · `Score in 2018` |
| 3 | 238 | `Ireland` · `Score in 2024` | 5% | f1 | the Ireland vertical tick marker (Score in 2024) | 否 | `Ireland` · `Score in 2024` |
| 4 | 100 | `EU` · `Score in 2018` | 5% | f1 | the EU diamond marker (Score in 2018), sitting on the 100 gridline | 否 | `EU` · `Score in 2018` |
| 5 | 157 | `Germany` · `Strong innovators` | 5% | f1 | the Spain 2025 bar (bar end just under the 160 gridline) | 否 | `Spain` · `Score for dimension 4.3 in 2025 (indexed to the EU in 2018)` |
| 6 | 143 | `Germany` · `Score in 2024` | 5% | f1 | the Germany vertical tick marker (Score in 2024), just past the 140 gridline | 否 | `Germany` · `Score in 2024` |
| 7 | 36 | `Bulgaria` · `Emerging innovators` | 10% | f1 | the Bulgaria 2025 bar, the shortest bar in the figure | 否 | `Bulgaria` · `Score for dimension 4.3 in 2025 (indexed to the EU in 2018)` |
| 8 | 14 | `Bulgaria` · `Score in 2018` | 20% | f1 | the Bulgaria diamond marker (Score in 2018), left of the 20 gridline | 否 | `Bulgaria` · `Score in 2018` |
| 9 | 191 | `Denmark` · `Innovation leaders` | 5% | f1 | the Denmark 2025 bar (bar end just past the 180 gridline) | 否 | `Denmark` · `Score for dimension 4.3 in 2025 (indexed to the EU in 2018)` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 9 predicted key sets miss a rule label: 250, 157, 36, 191

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | horizontal | 1 | 6 | 28 | 84 | 无 | 0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260 |

- **f1** Figure 21 / Innovation performance of the EU27 Member States in the Resource and Labour productivity dimension / Resource and labour productivity　[图上方]　单位 `Score for dimension 4.3 in 2025 (indexed to the EU in 2018)`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | diamond markers and short vertical bars overlaid on each horizontal bar |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names down the left axis, bars grow rightwards to the 0-260 axis |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | 'The colours denote each country's overall performance group based on the 2025 SII.' |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend entry '\|  Score in 2024' drawn as a short vertical tick inside each bar |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: All performance scores are relative to that of the EU in 2018 for each dimension.' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two-row legend with four colour swatches plus diamond and tick, below the axis title |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | ticks are bare numbers 0...260; scale word only in 'Score for dimension 4.3 in 2025 (indexed to the EU in 2018)' |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | 'Score for dimension 4.3 in 2025 (indexed to the EU in 2018)' centred under the tick row |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | '(indexed to the EU in 2018)'; 'All performance scores are relative to that of the EU in 2018' |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 28 country names stacked down the left axis, one per row |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the 'EU' row is drawn in dark navy, unlike the four legend group colours |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | faint vertical rules at each 20-unit tick across the plot, no horizontal rules |

词表 65 项，本页出现 12 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `primary_series_named_only_in_axis_title` | f1 | legend names only the four colour groups plus 2018/2024 markers; the bar year 2025 appears only in the axis title | 读取条形长度时无法从图例得到年份，必须借下方轴标题"...in 2025..."才能把数值定位到2025年这一列，否则条形值与2018/2024标记无法区分。 |
| `marker_series_shares_row_with_bar` | f1 | each country row carries three values: bar end, diamond, vertical tick, all on one axis | 同一行有三个不同年份的数值，表格必须为每行提供三个列键，否则一个数字无法唯一定址。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数字标签，全部数值只能靠像素对轴读出。轴上每20个单位约51 px，即1 px≈0.39个单位。对大值还好（168的5%容差=±8.4单位≈21 px），但对小值几乎不可能：14的5%容差只有±0.7单位≈1.8 px，36的容差±1.8单位≈4.6 px，而菱形标记本身直径就有约6 px，中心定位误差已超过容差。次难是标签：一行里条形(2025)、菱形(2018)、竖线(2024)共享同一轴，而2025只写在图下轴标题里，表格要同时带国名和年份两级键才能唯一定址。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | tick_marker_as_series 与 mixed_marks 的组合（条形+菱形+短竖线三系列同轴叠加） | 图表生成条件行中新增"bar_with_overlaid_point_and_tick_markers"样式，并在记录字段里为每个category写出三个series值 | 标记型系列（菱形/竖线）叠加在条形上 vs 仅条形：比较同一行多系列时的定址与读数正确率 |
| P7 | 这份文档自己的习惯 | new_components: primary_series_named_only_in_axis_title（主系列年份只出现在轴标题） | heading 字段拆分中把 unit_text/轴标题作为独立字段，并允许图例缺失主系列条目 | 主系列在图例中命名 vs 仅在轴标题中命名：考察缺失图例条目时的行键还原 |
| P1 | 通用 | P1 式的按标记可达精度（小值标记的读数容差） | 评分条件行中将 readable 改为按标记数值大小给出容差，例如轴步长/像素比阈值 | 值域跨度大（14 至 250 同轴）时按标记设定容差 vs 全图统一5%容差 |
| P6 | 一类出版方 | color_encodes_extra_attribute + highlighted_category（颜色表示绩效组、EU行单独深蓝） | 样式字段中加入"fill encodes group attribute"与"aggregate row highlight color" | 颜色编码分组属性且含高亮聚合行 vs 单色条形：检验颜色是否被误当作系列名 |
| P3 | 通用 | axis_title_below_plot 与 rebased_index_values（"indexed to the EU in 2018"） | heading/unit 位置样式字段：unit 置于图下轴标题而非轴旁或标题内 | 单位与基期写在图下轴标题 vs 写在图题内：markdown 导出后单位能否与表格对应 |
