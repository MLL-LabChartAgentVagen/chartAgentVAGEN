# b263dc5d-en_p132

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b263dc5d-en | `need_estimate` | 10 | 10 |

该页主体为 Figure 3.16，一张按国家排列、每国三个标记（圆形/菱形/三角形）并用竖线相连的分数差异范围图，下附大量注释与来源说明及正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 32 | `Finland` · `Foreign-born, less than 10 years in country` | 5% | f1 | Finland, filled circle (highest marker on the chart) | 否 | `Finland` · `Foreign-born, less than 10 years in country` |
| 2 | 17 | `Finland` · `Native-born` | 5% | f1 | Finland, filled triangle just above the 10 gridline | 否 | `Finland` · `Native-born` |
| 3 | -44 | `Germany` · `Foreign-born, less than 10 years in country` | 5% | f1 | Germany, filled circle, the lowest marker on the chart | 否 | `Germany` · `Foreign-born, less than 10 years in country` |
| 4 | 8 | `Germany` · `Native-born` | 10% | f1 | Denmark, filled triangle just below the 10 gridline | 否 | `Denmark` · `Native-born` |
| 5 | 10 | `Norway` · `Native-born` | 10% | f1 | Denmark, filled diamond sitting on the 10 gridline | 否 | `Denmark` · `Foreign-born, more than 10 years in country` |
| 6 | 9 | `Czechia` · `Foreign-born, more than 10 years in country` | 10% | f1 | Czechia, hollow diamond just under the 10 gridline (could also be Sweden's triangle) | 否 | `Czechia` · `Foreign-born, more than 10 years in country` |
| 7 | 0 | `Canada` · `Foreign-born, less than 10 years in country` | 1% | f1 | Norway, hollow circle sitting on the zero rule | 否 | `Norway` · `Foreign-born, less than 10 years in country` |
| 8 | -18 | `New Zealand` · `Native-born` | 10% | f1 | Ireland, filled diamond between the -10 and -20 gridlines | 否 | `Ireland` · `Foreign-born, more than 10 years in country` |
| 9 | -19 | `Singapore` · `Foreign-born, more than 10 years in country` | 10% | f1 | France, filled diamond just above the -20 gridline | 否 | `France` · `Foreign-born, more than 10 years in country` |
| 10 | 19 | `Denmark` · `Foreign-born, less than 10 years in country` | 5% | f1 | Denmark, filled circle just below the 20 gridline | 否 | `Denmark` · `Foreign-born, less than 10 years in country` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 10 predicted key sets miss a rule label: 8, 10, 0, -18, -19

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `other · vertical dumbbell range plot` | vertical | 1 | 3 | 19 | 57 | 无 | 40, 30, 20, 10, 0, -10, -20, -30, -40, -50 |

- **f1** Figure 3.16. / Change in literacy proficiency between cycles, by immigrant background and years spent in the country / Difference in mean literacy scores between cycles (Cycle 2 minus Cycle 1)　[图上方]　单位 `Score-point difference`
  - 来源行：Source: OECD (2018[4]; 2015[5]; 2012[6]), Survey of Adult Skills (PIAAC) databases, http://www.oecd.org/skills/piaac/publicdataandanalysis/ (accessed on 23 September 2024); Table A.3.14 (L) in Annex A.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a heavy horizontal rule is drawn across the plot at 0 |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | axis runs 40 down to -50; Germany's circle sits near -44 below the zero rule |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | a pale grey vertical band separates Germany from Singapore, aligned with the Round 1 / 2 split |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | "Darker colours denote differences that are statistically significant at the 5% level."; legend shows open and filled glyphs |
| `range_connector_line` | 每个类目两个点用线段连成区间（哑铃图 / 区间图） | f1 | **无** | each country column has its three markers joined by one vertical segment |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: Adults aged 16-65..." and "Source: OECD (2018[4]; 2015[5]; 2012[6])..." below the plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | three legend rows sit between the subtitle line and the top of the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 40...-50; scale word only in "Score-point difference" and "Difference in mean literacy scores" |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "Score-point difference" set on two lines above the 40 tick, left of the axis |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | under the country names a grey band reads "Round, Cycle 1:" with cells "1" and "2" |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | country names Finland, Denmark ... New Zealand set vertically under the plot |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | axis labels "England (UK)" and "Flemish Region (BE)" printed in blue, the others in black |

词表 65 项，本页出现 12 项，其中我们画不出来的 9 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `marker_shape_encodes_series` | f1 | legend uses circle, diamond and triangle glyphs to name the three subgroups at each country | 取值时必须先按标记形状（圆/菱/三角）判定是哪一组，颜色不区分系列，只区分显著性。 |
| `dual_swatch_legend_entry` | f1 | each legend row carries two glyphs, one hollow and one filled, before a single series name | 同一系列名对应两种填充状态，表格若只写系列名会丢掉显著与不显著的区分。 |
| `category_group_band_below_axis` | f1 | grey banner under the axis labelled "Round, Cycle 1:" split into cells "1" and "2" | 国家还带一个“Cycle 1 轮次”属性，定位某一点可能需要该额外键。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

刻度每 10 分点约 34 像素，即 1 分点约 3.4 像素；而待核对的 8、9、10 三个值 5% 容差分别只有 ±0.4、±0.45、±0.5 分点，合 1.4-1.7 像素，肉眼与像素测量都无法把 Denmark 三角(≈8)、Czechia 菱形(≈9)、Denmark 菱形(≈10)、Sweden 三角(≈9-10)彼此分开；再加上 19 个国家×3 个标记共 57 点、无任何数值标签，值本身的读取是最硬的一关。相比之下标签只需“国家+系列名”两键，尚可承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P4 | 一类出版方 | range_connector_line 配合 marker_shape_encodes_series（新组件） | 图表族条件行中新增“每类别多标记+竖向连接段”的哑铃/区间图样式，标记形状作为系列编码字段 | 标记形状编码系列 vs 颜色编码系列时，逐点取值正确率对比 |
| P6 | 一类出版方 | color_encodes_extra_attribute（深浅表示 5% 显著性） | 记录字段中为每个 mark 增加一个与系列无关的填充状态属性（hollow/filled） | 填充状态是否进入 key 时，同名系列内两种点能否被分别定位 |
| P2 | 这份文档自己的习惯 | two_level_x_ticks 与新组件 category_group_band_below_axis | 类别轴样式字段：轴下增设带标题（如 "Round, Cycle 1:"）的分组灰条 | 有/无轴下分组带时，表格是否需要额外一列分组键 |
| P7 | 通用 | 标题四段拆分（figure_number / title / subtitle / unit_text = "Score-point difference"） | P7 标题字段化：单位既出现在副标题也以轴上方文本形式出现 | 单位置于轴上方文本 vs 置于副标题时，数值单位还原正确率 |
| P5 | 一类出版方 | dense_marks 相关的密度控制（57 点、19 类别、无数值标签） | 密度上限条件行：类别数×系列数上限从小样本提升到 20×3 | 类别数 19 且无数值标签时，逐点读数容差随密度下降的曲线 |
