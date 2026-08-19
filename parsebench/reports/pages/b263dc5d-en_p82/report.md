# b263dc5d-en_p82

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b263dc5d-en | `need_estimate` | 10 | 10 |

该页主体是一幅图 Figure 2.13，用条形（未调整差异）加菱形标记（调整后差异）展示32个国家/经济体STEM毕业生男女数学能力得分差，下附长篇Note与Source，页面下半为正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 23 | `Sweden` · `Unadjusted` | 5% | f1 | the Sweden Unadjusted bar, tallest column, top just above 22 | 否 | `Sweden` · `Unadjusted` · `Score-point difference` |
| 2 | 14.5 | `Sweden` · `Adjusted` | 5% | f1 | the Sweden Adjusted diamond (filled), sitting just below the 15 tick | 否 | `Sweden` · `Adjusted` · `Score-point difference` |
| 3 | 20 | `Netherlands` · `Adjusted` | 5% | f1 | the Netherlands Adjusted diamond (filled), at the 20 gridline level | 否 | `Netherlands` · `Adjusted` · `Score-point difference` |
| 4 | 16 | `United States` · `Unadjusted` | 5% | f1 | the Poland* Unadjusted bar, top just under the 16 level | 否 | `Poland*` · `Unadjusted` · `Score-point difference` |
| 5 | 15 | `United States` · `Adjusted` | 5% | f1 | the United States Unadjusted bar, top at the 15 tick (its Adjusted diamond sits on the same level) | 否 | `United States` · `Unadjusted` · `Score-point difference` |
| 6 | 10 | `Spain` · `Unadjusted` | 1% | f1 | the Norway Unadjusted bar, top at about the 10 level; Spain and Switzerland bars sit at nearly the same height | 否 | `Norway` · `Unadjusted` · `Score-point difference` |
| 7 | 8 | `OECD average` · `Unadjusted` | 5% | f1 | the OECD average Unadjusted bar in the tinted slot, top a little above 8 | 否 | `OECD average` · `Unadjusted` · `Score-point difference` |
| 8 | 8 | `OECD average` · `Adjusted` | 5% | f1 | the Austria Adjusted diamond (open), at about the 8 level | 否 | `Austria` · `Adjusted` · `Score-point difference` |
| 9 | -9 | `Korea` · `Unadjusted` | 5% | f1 | the Korea Unadjusted bar, the only bar reaching near -9 below the zero line | 否 | `Korea` · `Unadjusted` · `Score-point difference` |
| 10 | -4 | `Korea` · `Adjusted` | 10% | f1 | the Korea Adjusted diamond (filled), between the -5 and 0 ticks | 否 | `Korea` · `Adjusted` · `Score-point difference` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 16, 10, 8

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 32 | 64 | 无 | 25, 20, 15, 10, 5, 0, -5, -10, -15 |

- **f1** Figure 2.13. / Gender differences in numeracy among STEM graduates / Adjusted and unadjusted differences in average numeracy scores between tertiary-educated men and women who studied STEM fields (men minus women)　[图上方]　单位 `Score-point difference`
  - 来源行：Source: Table A.2.9 (N) in Annex A.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | columns for "Unadjusted" with diamond markers for "Adjusted" overlaid at each country slot |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | heavy horizontal rule drawn at 0 separating men-higher from women-higher bars |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | Croatia, Slovak Republic and Korea bars hang below the zero line; axis runs to -15 |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | boxed notes inside plot: "Men score higher than women" and "Women score higher than men" |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | pale blue vertical band spanning the full height of the "OECD average" slot |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | "Darker colours denote differences that are statistically significant at the 5% level" |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: Adults aged 25-65..." and "Source: Table A.2.9 (N) in Annex A." below plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | "Unadjusted ◇◆ Adjusted" legend row sits between subtitle and plot area |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | ticks are bare numbers 25...-15; scale word only in "Score-point difference" |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | category "Poland*" and note "*Caution is required in interpreting results..." |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "Score-point difference" printed above the top tick "25" at the axis head |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | all 32 country names set vertically, 90 degrees, under the axis |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | whole figure box including the plot area carries a cream/beige tint |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | "OECD average" label bold and its column slot filled with a pale blue tint |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | vertical rules separate every country slot; no horizontal gridlines across the panel |

词表 65 项，本页出现 15 项，其中我们画不出来的 10 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `categories_sorted_by_series_value` | f1 | "Countries and economies are ranked in descending order of the unadjusted difference between men and women" | 类别顺序由未调整条形值决定，读者需按排序位置定位国家，且菱形序列不单调，不能靠顺序推断调整值。 |
| `legend_swatch_pair_per_series` | f1 | legend shows two square swatches for "Unadjusted" and two diamonds for "Adjusted" (light and dark) | 一个图例条目对应两种填色，读值时必须区分深浅只表示显著性而非另一个数据系列。 |
| `subnational_label_colour` | f1 | "Flemish Region (BE)" and "England (UK)" axis labels printed in blue, others in black | 轴标签颜色区分次国家实体，若表格丢失颜色信息，这两行仍需保留括号内的地区标识才能唯一定位。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

刻度每5分约占30像素，即1个得分点≈6像素；被打分的值多在8–10之间，5%容差只有0.4–0.5分，约2–3像素，而条顶与菱形中心本身就有2像素厚度，且无任何数值标签（values_printed=none），读数几乎无法稳定落入容差。相比之下定位标签只需两个键（国家名+Unadjusted/Adjusted），32个国家名逐字可读；负值区仅3个国家，方向不易混淆。另有多国数值接近（Norway 与 Spain、New Zealand 与 Switzerland 相差不足1分），像素读数还会把值配到错误的国家行上。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P4 | 一类出版方 | mixed_marks 中“菱形点覆盖在条形上、共用同一数值轴”的子类型（点叠加于条） | 图表族条件行：在 bar 家族下增加 overlay_point_series 样式字段，并让记录同时输出条与点两个系列 | 新增一行：bar_with_overlaid_point_series 开/关，对比同一类别下两系列取值的配对准确率 |
| P6 | 一类出版方 | color_encodes_extra_attribute（深浅填色表示5%显著性） | 样式字段中加入 fill_shade_encodes_flag，并在记录里增加 significant 布尔属性 | 新增一行：颜色额外编码 开/关，检验模型是否把深/浅误当成两个数据系列 |
| P7 | 一类出版方 | axis_title_above_axis + unit_in_axis_or_title（“Score-point difference”置于最高刻度之上） | 标题/单位字段：unit_position 增加 above_top_tick 取值，与 heading 块分离 | 新增一行：单位位置（轴上方 / 副标题 / 系列名）三档，对比带单位读数的正确率 |
| P6 | 通用 | negative_values 与零基准线（含正负双向条与两条方向说明标注） | 数值分布条件行：允许包含负值并强制绘制加粗零线，同时生成 annotation_callout 文字框 | 新增一行：含负值/零线标注 开/关，检验负号丢失率 |
| new | 这份文档自己的习惯 | 新组件 categories_sorted_by_series_value（按未调整差降序排列，并有 OECD average 高亮列） | 类别顺序字段：sort_by=series 值降序，并允许插入一个高亮的聚合类别 | 新增一行：类别排序（字母序 / 按值排序＋聚合列高亮），检验值与类别配对错位率 |
