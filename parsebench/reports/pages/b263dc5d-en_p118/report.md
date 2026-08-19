# b263dc5d-en_p118

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b263dc5d-en | `need_estimate` | 10 | 10 |

该页为OECD成人技能调查报告第116页，上半部为图3.6（27个国家/经济体三类受教育程度人口占比在两轮调查间的百分点差异范围图），下半部为正文文字。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 16 | `Korea` · `Tertiary` | 10% | f1 | the Korea Tertiary triangle, topmost marker of the first slot | 否 | `Figure 3.6.` · `Korea` · `Tertiary` |
| 2 | -15 | `Lithuania` · `Upper secondary` | 10% | f1 | the Ireland Below upper secondary dash at the bottom of its connector | 否 | `Figure 3.6.` · `Ireland` · `Below upper secondary` |
| 3 | -12 | `Ireland` · `Below upper secondary` | 10% | f1 | the Netherlands Below upper secondary dash | 否 | `Figure 3.6.` · `Netherlands` · `Below upper secondary` |
| 4 | -8 | `Denmark` · `Upper secondary` | 10% | f1 | the Estonia Upper secondary diamond, below the zero line | 否 | `Figure 3.6.` · `Estonia` · `Upper secondary` |
| 5 | 6 | `Hungary` · `Upper secondary` | 20% | f1 | the Czechia Tertiary triangle, just above the 0 line and below 10 | 否 | `Figure 3.6.` · `Czechia` · `Tertiary` |
| 6 | 2 | `Singapore` · `Below upper secondary` | 20% | f1 | the Norway Upper secondary diamond, slightly above the zero rule | 否 | `Figure 3.6.` · `Norway` · `Upper secondary` |
| 7 | 8 | `Italy` · `Upper secondary` | 10% | f1 | the Italy Tertiary triangle, just under the 10 gridline | 否 | `Figure 3.6.` · `Italy` · `Tertiary` |
| 8 | 10 | `Spain` · `Tertiary` | 5% | f1 | the Singapore Tertiary triangle, at about the 10 gridline | 否 | `Figure 3.6.` · `Singapore` · `Tertiary` |
| 9 | 13 | `France` · `Tertiary` | 10% | f1 | the Ireland Tertiary triangle, between the 10 gridline and 20 | 否 | `Figure 3.6.` · `Ireland` · `Tertiary` |
| 10 | -6 | `Slovak Republic` · `Below upper secondary` | 10% | f1 | the Korea Upper secondary diamond, below the zero rule | 否 | `Figure 3.6.` · `Korea` · `Upper secondary` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——9 of 10 predicted key sets miss a rule label: -15, -12, -8, 6, 2, 8
- 有图超过 100 个图元，组件清单里没有 dense_marks_100plus——densest figure has 108 marks

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `other · three-marker range plot` | vertical | 1 | 3 | 27 | 108 | 无 | 20, 10, 0, -10, -20 |

- **f1** Figure 3.6. / Change in educational attainment of the adult population between cycles / Difference in the shares of adults with below upper secondary, upper secondary and tertiary education (Cycle 2 minus Cycle 1); 25-65 year-olds　[图上方]　单位 `Percentage point difference`
  - 来源行：Source: OECD (2018[4]; 2015[5]; 2012[6]), Survey of Adult Skills (PIAAC) databases, http://www.oecd.org/skills/piaac/publicdataandanalysis/ (accessed on 23 September 2024); Table B.3.1 (Trend) in Annex B.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | dash, diamond and triangle markers plus vertical connector segments in one panel |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | thick horizontal rule drawn across the panel at the 0 tick |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | axis runs 20 to -20 with a heavy rule at 0; markers sit above and below it |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | beige vertical bands in the plot before 'Lithuania' and before 'Hungary' |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend shows 'Below upper secondary' as a short horizontal dash placed at the country position |
| `range_connector_line` | 每个类目两个点用线段连成区间（哑铃图 / 区间图） | f1 | **无** | a vertical segment per country joins its dash, diamond and triangle markers |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Does not include adults who in Cycle 2...' and 'Source: OECD (2018[4]...' below the plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | 'Below upper secondary  Upper secondary  Tertiary' row sits between subtitle and plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | 'Percentage point difference' is the only place the scale word appears; ticks read 20, 10, 0 |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | category 'Poland*' with note '*Caution is required in interpreting results...' |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | 'Percentage point difference' printed above the top tick 20, left of the plot |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | 'Round, Cycle 1:' grey banner under country names split into segments labelled 1, 2, 3 |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | country names 'Korea', 'Ireland', 'Flemish Region (BE)' set vertically under the axis |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | axis labels 'Flemish Region (BE)' and 'England (UK)' printed in blue, others black |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | vertical rules separate each country slot from 20 down through the label band |

词表 65 项，本页出现 15 项，其中我们画不出来的 10 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `marker_shape_encodes_series` | f1 | series distinguished by shape: dash, diamond, triangle, all read on the same value axis | 读值时必须先按标记形状判定系列，颜色几乎不携带信息，错认形状即错认系列。 |
| `axis_group_band_with_row_label` | f1 | grey banner under axis labelled 'Round, Cycle 1:' with cells '1', '2', '3' | 每个国家还带一个'调查轮次'属性，表格行需要额外一列才能唯一定位该点。 |
| `three_point_range_line` | f1 | one vertical segment per country spans three markers, not the usual two-point dumbbell | 连接线本身不代表某个量，读者需分别读三个标记，不能用线段长度推断数值。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，纵轴只有20/10/0/-10/-20五个刻度，10个百分点约占40像素，每像素≈0.25个百分点；要把'2'读到5%（±0.1个百分点）内在物理上不可能，'6''8'也需辨认到±0.3–0.4个百分点，而三种标记（短横、菱形、三角）在27个国家的窄槽中彼此重叠、部分被连接线遮挡，连判定某标记属于哪个系列都有风险。相比之下定位标签只需'国家名+系列名'两个键，表格容易承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 marker_shape_encodes_series 与 tick_marker_as_series 组合（形状区分系列的点/区间图） | 在样式条件表中新增'系列编码通道'字段（颜色/形状/线型），并允许短横标记作为一个系列 | 形状编码系列 vs 颜色编码系列，比较系列归属判定错误率 |
| P3 | 这份文档自己的习惯 | 新组件 axis_group_band_with_row_label（轴下带行标题的分组色带） | 记录字段增加 group_band 层级键，并在markdown导出中作为额外一列输出 | 有/无轴下分组带时，定位单个标记所需键数从2升到3的检索命中率 |
| P4 | 一类出版方 | three_point_range_line（每类目三个标记由一条竖线相连） | 图族权重向量中新增 range/dumbbell 家族，并允许每槽标记数>2 | 两点哑铃图 vs 三点区间图的逐标记读数精度 |
| P1 | 通用 | readable 改为逐标记可达精度（本页刻度间距10个百分点、无数值标签） | 评分条件行中的 readable 布尔门改为按标记像素/单位分辨率给出容差 | 以像素分辨率为容差 vs 固定5%容差时的通过率差异 |
| P7 | 通用 | 标题五段拆分（figure_number/title/subtitle/unit_text=Percentage point difference/placement=above） | 图元数据的heading字段与轴上方单位文本位置 | 单位置于轴上方 vs 置于副标题时，数值单位还原正确率 |
