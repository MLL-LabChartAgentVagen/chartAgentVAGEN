# 2025-EIS_p12

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2025-EIS | `need_estimate` | 9 | 9 |

该页为《European Innovation Scoreboard 2025》第10页，仅含Figure 2一幅横向条形图，展示EU27成员国2025年创新绩效（以2018年EU为基准的指数），条形按四类创新群体着色并叠加2024年得分的刻度标记。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 155 | `Sweden` · `Innovation leaders` | 5% | f1 | the Sweden 2025 bar (Innovation leaders), longest bar, ending just short of 160 | 否 | `Sweden` · `Innovation leaders` · `Summary innovation index in 2025 (indexed to the EU in 2018)` |
| 2 | 153 | `Sweden` · `Score in 2024` | 5% | f1 | the Denmark "Score in 2024" dash, drawn just beyond the end of the Denmark bar | 否 | `Denmark` · `Score in 2024` |
| 3 | 152 | `Denmark` · `Innovation leaders` | 5% | f1 | the Denmark 2025 bar (Innovation leaders), second longest | 否 | `Denmark` · `Innovation leaders` · `Summary innovation index in 2025 (indexed to the EU in 2018)` |
| 4 | 137 | `Ireland` · `Strong innovators` | 5% | f1 | the Belgium 2025 bar (Strong innovators), between the 120 and 140 gridlines | 否 | `Belgium` · `Strong innovators` · `Summary innovation index in 2025 (indexed to the EU in 2018)` |
| 5 | 129 | `Austria` · `Strong innovators` | 5% | f1 | the Luxembourg 2025 bar (Strong innovators), just past the mid-point between 120 and 140 | 否 | `Luxembourg` · `Strong innovators` · `Summary innovation index in 2025 (indexed to the EU in 2018)` |
| 6 | 108 | `Malta` · `Moderate innovators` | 5% | f1 | the Malta 2025 bar (Moderate innovators), first bar below the EU row | 否 | `Malta` · `Moderate innovators` · `Summary innovation index in 2025 (indexed to the EU in 2018)` |
| 7 | 109 | `Cyprus` · `Score in 2024` | 5% | f1 | the EU row: either the dark blue 2025 bar or its "Score in 2024" dash at the bar end; the two coincide within a pixel or two | 否 | `EU` · `Score in 2024` · `Summary innovation index in 2025 (indexed to the EU in 2018)` |
| 8 | 42 | `Romania` · `Emerging innovators` | 5% | f1 | the Romania 2025 bar (Emerging innovators), bottom row, ending just past 40 | 否 | `Romania` · `Emerging innovators` · `Summary innovation index in 2025 (indexed to the EU in 2018)` |
| 9 | 51 | `Bulgaria` · `Emerging innovators` | 10% | f1 | the Bulgaria 2025 bar (Emerging innovators), just past the mid-point between 40 and 60 | 否 | `Bulgaria` · `Emerging innovators` · `Summary innovation index in 2025 (indexed to the EU in 2018)` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 9 predicted key sets miss a rule label: 153, 137, 129, 109

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | horizontal | 1 | 5 | 28 | 56 | 无 | 0, 20, 40, 60, 80, 100, 120, 140, 160 |

- **f1** Figure 2 / Innovation performance of the EU27 Member States in 2025, indexed to the EU in 2018　[图上方]　单位 `Summary innovation index in 2025 (indexed to the EU in 2018)`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | bars plus overlaid short vertical dash markers in the same panel, on the same axis |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names sit on the y axis, bars grow rightwards to a 0-160 axis at the bottom |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | fill colour marks performance class: "Emerging innovators", "Moderate innovators", "Strong innovators", "Innovation leaders" |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend entry "Score in 2024" is a short vertical dash placed at each country's bar row |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | five legend entries in swatch columns below the axis title, outside the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 0...160; the scale word only in axis title "Summary innovation index in 2025 (indexed to the EU in 2018)" |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | "Summary innovation index in 2025 (indexed to the EU in 2018)" printed under the 0-160 tick row |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | title reads "indexed to the EU in 2018"; axis title repeats "(indexed to the EU in 2018)" |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 28 country labels stacked down the y axis, from "Sweden" to "Romania" |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the "EU" row is drawn in dark blue, unlike the four group colours around it |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | faint vertical rules at each 20-unit tick cross the bars; no horizontal rules |

词表 65 项，本页出现 11 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `sorted_category_axis` | f1 | countries ordered by 2025 value, Sweden top to Romania bottom, with EU inserted at its rank | 类别顺序本身携带信息（排名），行标签无法从字母序推断；读值时需按排名定位，且相邻行数值差可小于1个单位。 |
| `aggregate_inserted_in_ranking` | f1 | the "EU" aggregate row sits between "Estonia" and "Malta" inside the country ranking | 聚合值与成员国值混在同一序列中，表格若不额外标注会把EU当成一个国家行，影响定位与核对。 |
| `prior_year_marker_offset` | f1 | "Score in 2024" dash sometimes inside the bar (Malta, Italy), sometimes beyond it (Cyprus, Denmark) | 同一行有两个数值且相差仅1-6个单位，必须依靠标记相对条形端点的左右位置判断哪一个是2024年，否则两值互换。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

卡点在标签寻址。每个国家行有两个数值：2025年条形与"Score in 2024"刻度标记，两者差常在1-6个单位（Sweden 155 vs 153约1.3%，Romania 42 vs 42几乎重合），远小于5%容差，因此只给国家名的表格行会同时命中两个值而无法区分；必须同时携带国家名与系列名（"Score in 2024"或所属群体名如"Innovation leaders"）。此外条形颜色代表四类群体而非年份，颜色图例并不构成年份维度，解析器很容易把群体名当作唯一系列。相比之下读数本身较宽松：刻度每20单位、5%容差在108处约±5.4单位（约四分之一格间距），肉眼定位可达；28行×2值共56个marks也不算密。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | tick_marker_as_series（把某一系列画成置于类别位置的短刻度线，与条形共用同一数值轴） | 图表样式条件行中新增"prior-period marker"渲染选项，并在记录字段中为该系列单独保存series_name与数值 | 同一类别下"条形+刻度标记"两系列 vs 仅条形：考察系列名进入寻址键后取值正确率的变化 |
| P6 | 一类出版方 | color_encodes_extra_attribute（填色编码分组属性而非系列身份，图例项为"Emerging/Moderate/Strong innovators、Innovation leaders"） | 配色与图例生成条件行：增加group-colour映射字段，使图例项对应类别分组而不是数据系列 | 颜色=分组属性 vs 颜色=系列：检验模型是否把分组名误当年份/系列名写入表头 |
| new | 通用 | 新组件sorted_category_axis与aggregate_inserted_in_ranking（28行按值降序、EU聚合行插在Estonia与Malta之间并另用深蓝） | 类别轴排序与highlight字段：增加sort_by_value与aggregate_row位置参数 | 排序类别轴且含插入的聚合行 vs 固定顺序无聚合行：考察行定位与聚合值误配率 |
| P7 | 通用 | axis_title_below_plot + unit_in_axis_or_title（唯一的量纲说明位于刻度行下方的"Summary innovation index in 2025 (indexed to the EU in 2018)"） | 标题/单位版式字段：新增unit位置枚举值"below-axis"，与figure_number、title分离 | 单位置于轴下标题 vs 置于图题内：考察导出markdown表头是否保留指数基准信息 |
