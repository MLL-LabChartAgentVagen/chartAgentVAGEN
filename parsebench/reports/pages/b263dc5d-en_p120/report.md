# b263dc5d-en_p120

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b263dc5d-en | `need_estimate` | 10 | 10 |

本页是OECD报告第118页，包含Figure 3.8一幅图：25个国家/经济体的识字能力差距变化（条形为未调整值，菱形为调整值），下附大段Note与Source，以及正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 34 | `Japan` · `Unadjusted` | 5% | f1 | the Japan Unadjusted bar (tallest bar, top just above the 30 gridline) | 否 | `Japan` · `Unadjusted` |
| 2 | 35 | `Japan` · `Adjusted` | 5% | f1 | the Japan Adjusted diamond, sitting on the 35 gridline | 否 | `Japan` · `Adjusted` |
| 3 | 29 | `Austria` · `Unadjusted` | 5% | f1 | the Austria Unadjusted bar, top just below 30 | 否 | `Austria` · `Unadjusted` |
| 4 | 19 | `Austria` · `Adjusted` | 5% | f1 | the Austria Adjusted diamond, between the 15 and 20 gridlines (could also be the Estonia Adjusted diamond near 20) | 否 | `Austria` · `Adjusted` |
| 5 | -4 | `Korea` · `Adjusted` | 10% | f1 | the Korea Adjusted hollow diamond below zero, near -4 | 否 | `Korea` · `Adjusted` |
| 6 | -17 | `Poland*` · `Unadjusted` | 5% | f1 | the Poland* Unadjusted bar, reaching down past -15 | 否 | `Poland*` · `Unadjusted` |
| 7 | 25 | `New Zealand` · `Unadjusted` | 5% | f1 | the New Zealand Unadjusted bar, top on the 25 gridline | 否 | `New Zealand` · `Unadjusted` |
| 8 | 15 | `New Zealand` · `Adjusted` | 5% | f1 | the Finland Adjusted hollow diamond, on the 15 gridline | 否 | `Finland` · `Adjusted` |
| 9 | -8 | `Israel` · `Adjusted` | 10% | f1 | the Israel Adjusted filled diamond below -5 (the Sweden Unadjusted bar bottom is at a similar depth) | 否 | `Israel` · `Adjusted` |
| 10 | 13 | `Hungary` · `Unadjusted` | 5% | f1 | the Hungary Unadjusted bar, top just above the 10 gridline (Flemish Region (BE) bar is similar) | 否 | `Hungary` · `Unadjusted` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: 15

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 25 | 50 | 无 | 40, 35, 30, 25, 20, 15, 10, 5, 0, -5, -10, -15, -20 |

- **f1** Figure 3.8. / Change in the gap in literacy proficiency between highly and low-educated adults / Adjusted and unadjusted change between cycles in the average score difference between adults with tertiary education and adults with below upper secondary education (Cycle 2 minus Cycle 1); 25-65 year-olds　[图上方]　单位 `Score-point difference`
  - 来源行：Source: OECD (2018[4]; 2015[5]; 2012[6]), Survey of Adult Skills (PIAAC) databases, http://www.oecd.org/skills/piaac/publicdataandanalysis/ (accessed on 23 September 2024); Tables A.3.12 (L) and A.3.13 (L) in Annex A.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | a diamond marker ("Adjusted") sits over each vertical bar ("Unadjusted") in the same panel |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a thick horizontal rule drawn at 0 across the whole plot width |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | bars for Spain, Slovak Republic, Sweden, Poland*, Israel hang below zero; axis runs to -20 |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | two pale vertical bands separate the New Zealand-Singapore and Israel columns from neighbours |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | "Darker colours denote differences that are statistically significant at the 5% level." |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: Does not include adults who in Cycle 2 were only administered the doorstep interview..." plus Source line |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | "Unadjusted   Adjusted" swatch row sits between the subtitle and the plot top |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | "Score-point difference" is the only place the scale of 40...-20 is named |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | category label "Poland*" with asterisk explained in the note: "*Caution is required..." |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "Score-point difference" printed above the top tick 40, left of the plot top |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | under the rotated country names a grey banner row "Round, Cycle 1:" with segments 1, 2, 3 |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | country names such as "Flemish Region (BE)" set vertically, turned 90 degrees |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 25 long names such as "Slovak Republic", "Flemish Region (BE)" stacked vertically down the axis |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | tick labels "England (UK)" and "Flemish Region (BE)" printed in green, unlike the black country names |

词表 65 项，本页出现 14 项，其中我们画不出来的 10 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `legend_swatch_pair_per_series` | f1 | each legend entry shows two swatches (light and dark square; hollow and filled diamond) for one name | 一个系列名对应两种填色，读值时必须知道深浅只表示显著性而非另一个系列，否则会把25个国家误判成4个系列。 |
| `sort_order_stated_in_note` | f1 | "Countries and economies are ranked in descending order of the unadjusted change in the gap." | 类别顺序由未调整值决定，可用相邻条形的单调性校验读数，也说明表格行序不是字母序。 |
| `axis_group_band_with_row_label` | f1 | grey band below axis labelled at left "Round, Cycle 1:" carrying group numbers 1, 2, 3 | 每个国家还带一个“Cycle 1轮次”属性，定位某个值时可能需要这第三个键。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上一个数字都没有印，网格线每5分一格，25个国家挤在约1000像素宽的绘图区内，5分格高约14像素。要满足5%容差：13分只允许±0.65分（约2像素），-4分只允许±0.2分（不到1像素），实际上无法从条形顶端或菱形中心读出。更糟的是同一图内多处重复量级——18.5与20.5都可四舍五入到19-20，Sweden条形与Israel菱形都落在-8附近，Flemish Region与Hungary条形都约13.5，光凭像素无法判定某个给定值属于哪一列。相比之下第3步只需“国家+Unadjusted/Adjusted”两个键，表格容易承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P4 | 一类出版方 | mixed_marks（条形上叠加菱形点标记，共用同一数值轴） | 图表族生成权重向量中新增“bar+overlaid point marker”组合，并在样式字段里加marker_shape/marker_fill | 仅条形 vs 条形+叠加点标记：同一类别两个系列时的取值配对准确率 |
| P6 | 一类出版方 | color_encodes_extra_attribute 与新提出的 legend_swatch_pair_per_series（同名系列深浅两色表示显著性） | 记录字段加per-mark的significant布尔值，图例渲染改为一名两色块 | 图例色块数=系列数 vs 图例色块数=2×系列数：系列识别错误率 |
| P6 | 这份文档自己的习惯 | two_level_x_ticks / axis_group_band_with_row_label（轴下灰色分组带“Round, Cycle 1: 1/2/3”） | 条件行增加“类别轴下分组带+左侧行标签”，并把分组值写入记录的附加键 | 有无轴下分组带：定位一个值所需键数由2升到3时的命中率 |
| P7 | 通用 | axis_title_above_axis + unit_in_axis_or_title（“Score-point difference”置于顶刻度之上） | 标题块字段拆分为number/title/subtitle/unit与unit位置枚举（above_axis/beside_axis/in_title） | 单位位于标题 vs 位于轴顶：导出表格是否保留刻度单位 |
| P6 | 通用 | negative_values + reference_line（零线两侧双向条形） | 样式维度加zero_line_weight与负值方向，数值轴范围允许负下限 | 全正值 vs 含负值且轴至-20：负号丢失与符号错误率 |
| P5 | 一类出版方 | dense_marks 类别数25、rotated_x_ticks 的密集轴 | 密度上限从常用10-15类提高到25类，并将旋转标签作为受控变量 | 12类 vs 25类旋转标签：类别名与marks对齐错位率 |
