# b263dc5d-en_p106

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b263dc5d-en | `3d_chart+need_estimate` | 10 | 10 |

本页只有一张图 Figure 3.1，用上下两个面板（A. Literacy / B. Numeracy）展示 27 个国家/经济体在两轮 PIAAC 之间的平均素养与数学能力分数差，柱形为未调整差异、菱形为人口结构调整后差异。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 17 | `A. Literacy` · `Finland` · `Before accounting for demographic changes` | 10% | f1 | the Finland diamond in panel A (After accounting for demographic changes) | 否 | `A. Literacy` · `Finland` · `After accounting for demographic changes` |
| 2 | 10 | `A. Literacy` · `Norway` · `After accounting for demographic changes` | 10% | f1 | the Denmark diamond in panel A (After accounting for demographic changes) | 否 | `A. Literacy` · `Denmark` · `After accounting for demographic changes` |
| 3 | -31 | `A. Literacy` · `Poland*` · `Before accounting for demographic changes` | 5% | f1 | the Poland* diamond in panel A, the lowest point on the figure | 否 | `A. Literacy` · `Poland*` · `After accounting for demographic changes` |
| 4 | -10 | `A. Literacy` · `Israel` · `After accounting for demographic changes` | 10% | f1 | the Israel bar in panel A (Before accounting for demographic changes) | 否 | `A. Literacy` · `Israel` · `Before accounting for demographic changes` |
| 5 | -29 | `A. Literacy` · `Lithuania` · `Before accounting for demographic changes` | 10% | f1 | the Lithuania diamond in panel A (After accounting for demographic changes) | 否 | `A. Literacy` · `Lithuania` · `After accounting for demographic changes` |
| 6 | 18 | `B. Numeracy` · `Finland` · `Before accounting for demographic changes` | 10% | f1 | the Singapore diamond in panel B (After accounting for demographic changes) | 否 | `B. Numeracy` · `Singapore` · `After accounting for demographic changes` |
| 7 | 13 | `B. Numeracy` · `Norway` · `After accounting for demographic changes` | 10% | f1 | the Finland bar in panel A (Before accounting for demographic changes) | 否 | `A. Literacy` · `Finland` · `Before accounting for demographic changes` |
| 8 | 20 | `B. Numeracy` · `Singapore` · `After accounting for demographic changes` | 10% | f1 | the Finland diamond in panel B (After accounting for demographic changes) | 否 | `B. Numeracy` · `Finland` · `After accounting for demographic changes` |
| 9 | -20 | `B. Numeracy` · `Poland*` · `Before accounting for demographic changes` | 5% | f1 | the Poland* bar in panel B (Before accounting for demographic changes) | 否 | `B. Numeracy` · `Poland*` · `Before accounting for demographic changes` |
| 10 | -15 | `B. Numeracy` · `New Zealand` · `After accounting for demographic changes` | 10% | f1 | the Hungary bar in panel A (Before accounting for demographic changes) | 否 | `A. Literacy` · `Hungary` · `Before accounting for demographic changes` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——9 of 10 predicted key sets miss a rule label: 17, 10, -31, -10, -29, 18

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 2 | 2 | 27 | 108 | 无 | 30, 20, 10, 0, -10, -20, -30, -40 |

- **f1** Figure 3.1. / Change in average literacy and numeracy proficiency between cycles, before and after accounting for demographic changes / Difference in mean proficiency scores between cycles, after reweighting Cycle 2 to match Cycle 1's distribution of age, immigrant background and gender (Cycle 2 minus Cycle 1)　[图上方]　单位 `Score-point difference`
  - 来源行：Source: OECD (2018[4]; 2015[5]; 2012[6]), Survey of Adult Skills (PIAAC) databases, http://www.oecd.org/skills/piaac/publicdataandanalysis/ (accessed on 23 September 2024); Tables A.3.1 (L) and A.3.1 (N) in Annex A.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | open/filled diamond markers overlaid on the light blue bars in both panels |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a heavier rule at the 0 tick from which bars grow up and down in both panels |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | bars run down to about -30 (Poland*, Lithuania); ticks -10, -20, -30, -40 |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | pale beige vertical bands between Poland* and Chile, and between Lithuania and Hungary |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | "Darker colours denote differences that are statistically significant at the 5% level"; legend shows light and dark glyph pairs |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | single legend row above both panels: "Before accounting for demographic changes" / "After accounting..." |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | one country axis serves both panels, labels drawn at the top and bottom edges only |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | two stacked panels "A. Literacy" and "B. Numeracy" of identical construction |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: Adults aged 16-65; ..." and "Source: OECD (2018[4]; 2015[5]; 2012[6])..." under the plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | legend row sits between the subtitle and the "Round, Cycle 1:" band |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | "A. Literacy" and "B. Numeracy" set in dark blue filled banners at the right of each panel |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | "Score-point difference" is the only scale word; axis shows bare 30, 20, 10, 0, -10 |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | category label "Poland*" with note "*Caution is required in interpreting results..." |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "Score-point difference" printed above the top tick label 30 at the left |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | grey band row "Round, Cycle 1:" with groups 1, 2, 3 above the rotated country names |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | all 27 country names set vertically at 90 degrees, top and bottom of the plot |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 27 countries x (bar + diamond) x 2 panels = about 108 drawn marks |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | "Flemish Region (BE)" and "England (UK)" axis labels printed in blue, other labels black |

词表 65 项，本页出现 18 项，其中我们画不出来的 10 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `duplicated_category_axis_labels` | f1 | the same 27 country names are printed vertically both above panel A and below panel B | 同一类别轴出现两次，解析器可能把同一列读成两行标签，取值时须判断哪一组标签对应哪个面板。 |
| `axis_group_band_with_row_title` | f1 | grey banner spanning categories, labelled 1 / 2 / 3, with row title "Round, Cycle 1:" at its left | 分组信息由带行标题的横向色带承载，读某国数值时需要额外带上其所属 Round 分组键。 |
| `dual_glyph_legend_entry` | f1 | each legend entry shows two glyphs (light+dark square, open+filled diamond) for one name | 一个图例名对应两种填色，取值时必须另判显著性深浅，否则无法唯一定位某个标记。 |
| `panel_label_banner_inside_plot` | f1 | "A. Literacy" / "B. Numeracy" in filled dark blue blocks occupying the right end of each plot band | 面板名在绘图区内右端，位置不在表格上方，导出为表格时面板上下文容易丢失。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，全部要靠像素对轴读数。每个面板纵向只有 170 像素左右覆盖 30 到 -40，即 10 分刻度约 22 像素，1 分不足 2.5 像素；对 10 或 13 这类小值，5% 容差只有 0.5–0.65 分，等于 1 个多像素，柱顶描边和叠在柱上的菱形本身就占 4–5 像素，落在容差内基本不可能。相比之下寻址虽然要 3 个键（A. Literacy / Finland / After accounting for demographic changes），加上深浅两种显著性色，仍可由表格列名承载；27 列 × 2 序列 × 2 面板共 108 个标记也让同一数字（如 13、-20）在两个面板重复出现，进一步放大读值歧义。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 一类出版方 | mixed_marks 中“菱形标记叠在柱上、共用同一数值轴”的组合（可视为 tick_marker_as_series 的近邻） | 图形族条件行：在 bar 面板上追加 overlay marker 序列的样式字段（marker 形状、是否空心） | 新增“柱+叠加点标记 vs 纯分组柱”一行，检验叠加标记是否降低每标记可达精度 |
| P6 | 一类出版方 | color_encodes_extra_attribute（浅/深填色表示 5% 显著性）与 dual_glyph_legend_entry | 样式字段：为每个标记增加 significance 属性并让图例每项渲染两个色块 | 新增“颜色承载第二变量 vs 颜色只表示序列”一行，检验寻址键数从 3 增到 4 时的检索命中率 |
| P3 | 这份文档自己的习惯 | panel_title_per_panel 以填色横幅置于绘图区右端，以及 duplicated_category_axis_labels | 记录字段：panel 名的位置枚举（above/inside-right）与类别轴标签是否上下重复 | 新增“面板名在表内标题行 vs 在绘图区内色块”一行，量化面板上下文丢失率 |
| P6 | 一类出版方 | two_level_x_ticks 的带行标题分组色带（"Round, Cycle 1:" 与 1/2/3） | 标签条件行：外层分组行增加行标题文本与色带样式 | 新增“分组行带行标题 vs 无行标题”一行，检验分组键是否被解析为额外表列 |
| P6 | 通用 | 负值与零线（negative_values + reference_line）在 -40…30 非对称轴上的组合 | 轴样式字段：零线加粗、上下不对称刻度范围 | 新增“零线两侧不对称范围 vs 从零起的单向轴”一行，检验负值读数误差是否系统性偏大 |
