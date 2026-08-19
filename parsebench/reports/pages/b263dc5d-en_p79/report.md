# b263dc5d-en_p79

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b263dc5d-en | `need_estimate` | 10 | 10 |

本页只有一个图（Figure 2.11），为各国/经济体高等教育成人数学能力得分的柱状图（STEM）叠加菱形标记（Non-STEM），下方有长段Note、斜体排序说明、Source行及两条编号脚注。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 338 | `Finland` · `STEM` | 5% | f1 | the Finland STEM bar, the tallest bar at the left edge | 否 | `Finland` · `STEM` · `Score points` |
| 2 | 312 | `Finland` · `Non-STEM` | 5% | f1 | the Finland Non-STEM diamond | 否 | `Finland` · `Non-STEM` · `Score points` |
| 3 | 330 | `Flemish Region (BE)` · `STEM` | 5% | f1 | the Flemish Region (BE) STEM bar (third slot), same height as Netherlands | 否 | `Flemish Region (BE)` · `STEM` · `Score points` |
| 4 | 330 | `Netherlands` · `STEM` | 5% | f1 | the Netherlands STEM bar (fourth slot) | 否 | `Netherlands` · `STEM` · `Score points` |
| 5 | 320 | `Germany` · `STEM` | 5% | f1 | the Switzerland STEM bar, just above the 320 grid line | 否 | `Switzerland` · `STEM` · `Score points` |
| 6 | 305 | `OECD average` · `STEM` | 5% | f1 | the OECD average STEM bar in the shaded slot | 否 | `OECD average` · `STEM` · `Score points` |
| 7 | 285 | `OECD average` · `Non-STEM` | 5% | f1 | the Hungary Non-STEM diamond (near 283-285) | 否 | `Hungary` · `Non-STEM` · `Score points` |
| 8 | 298 | `United States` · `STEM` | 5% | f1 | the United States STEM bar (or Portugal STEM bar, both near 298-299) | 否 | `United States` · `STEM` · `Score points` |
| 9 | 266 | `Poland*` · `STEM` | 5% | f1 | the Poland* STEM bar, a hollow bar near 265-266 | 否 | `Poland*` · `STEM` · `Score points` |
| 10 | 263 | `Chile` · `STEM` | 5% | f1 | the Chile STEM bar, the rightmost bar | 否 | `Chile` · `STEM` · `Score points` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 320, 285
- 标了 dense_marks_100plus，但没有图达到 100 个图元——dense_marks_100plus claimed, densest figure has 60 marks

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 30 | 60 | 无 | 220, 240, 260, 280, 300, 320, 340 |
| f1b | `other · placeholder duplicate entry` | na | 1 | 0 | 0 | 0 | 无 | （不画值轴） |

- **f1** Figure 2.11. / Average numeracy proficiency among tertiary-educated adults, by field of study　[图上方]　单位 `Score points`
  - 来源行：Source: Table A.2.6 (N) in Annex A.  ·  Note: Adults aged 25-65; ... Source: Table A.2.6 (N) in Annex A.:contentReference
- **f1b** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | vertical bars for STEM with black/white diamond markers overlaid at each country position for Non-STEM |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | pale blue vertical band spanning the OECD average slot from top of plot down through the label |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest tick on the value axis reads 220, not zero, and no break glyph is drawn |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | 'Darker colours denote differences that are statistically significant at the 5% level.' |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | Non-STEM drawn as a small diamond glyph at the category position, read against the same 220-340 axis |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Adults aged 25-65; ...' and 'Source: Table A.2.6 (N) in Annex A.' under the plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | 'STEM' and 'Non-STEM' key sits between the title line and the plot area |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | 'Score points' is the only scale phrase; axis ticks are bare numbers 220...340 |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | category label 'Poland*' with '*Caution is required in interpreting results due to the high share of respondents' |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | 'Score points' sits above the 340 tick at the top-left of the plot |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | country names like 'Flemish Region (BE)', 'Slovak Republic' set vertically at 90 degrees |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 30 rotated country names stacked along one axis, including 'Flemish Region (BE)', 'England (UK)' |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | whole figure box carries a beige/cream tint behind plot area and notes |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 240, 260, 280, 300, 320 across panel; no vertical grid lines |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 30 country slots times 2 series gives 60 marks, below 100 |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | 'OECD average' label in bold with a light blue vertical band behind its bar |

词表 65 项，本页出现 16 项，其中我们画不出来的 11 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `legend_dual_swatch_per_series` | f1 | legend shows two swatches per entry: hollow+filled square for STEM, hollow+filled diamond for Non-STEM | 同一系列有两种填充（深/浅）分别表示差异是否显著，读值时必须知道深浅不改变系列身份，只改变显著性标注。 |
| `axis_label_color_coding` | f1 | 'Flemish Region (BE)' and 'England (UK)' tick labels printed in blue while others are black | 轴标签颜色区分次国家实体，定位某一柱时需按颜色区分同类名称，避免误配到国家层级。 |
| `italic_ranking_note_line` | f1 | 'Countries and economies are ranked in descending order of the proficiency of tertiary-educated adults who studied STEM fields.' | 该行说明类别轴顺序由STEM值降序决定，可用于交叉验证读出的柱高排序是否自洽。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

值轴从220起、每格20分，整幅绘图高度仅覆盖120分，5%容差在300分附近约±15分，看似宽松；但真正的困难在于把菱形标记的中心与柱顶分别读到分数级：例如Portugal(299)与United States(298)、Flemish Region与Netherlands(均约330)差异只有1-2像素，无法区分；而且没有任何数值打印在图上，只能靠像素对齐网格线。相比之下标签只需2-3个键（国家名+STEM/Non-STEM），并不构成瓶颈。

整页原图判不出来的：
- `f1b`（other）：该条目为占位，实际本页只有一个图，无第二图可判读。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 一类出版方 | tick_marker_as_series（点标记系列叠加在柱上，共用同一数值轴） | 图表族生成条件行中新增“bar + point-overlay”混合标记样式字段 | 叠加点标记 vs 分组柱：同一对比数据两种画法下每个mark的可读精度差异 |
| P6 | 通用 | axis_starts_above_zero 与 axis_title_above_axis 组合 | 样式字段中的value_axis起点与单位文字位置（置于顶部刻度上方） | 轴起点非零且单位仅出现在顶部标签时，数值抽取正确率的下降幅度 |
| P3 | 一类出版方 | highlighted_category + shaded_band 表示聚合项（OECD average 加粗并带浅蓝竖带） | 类别记录中新增is_aggregate标记，驱动加粗标签与背景竖带渲染 | 含高亮聚合类别 vs 无高亮：聚合行是否被表格单独命名的命中率 |
| new | 这份文档自己的习惯 | new_components 中的 legend_dual_swatch_per_series（一个系列两个色块表示显著性） | legend样式字段：允许每个series携带多个swatch及其语义注释 | 颜色深浅另编码显著性时，系列身份识别错误率 |
| P7 | 通用 | footnote_marker（类别名 'Poland*' 与Note中的星号说明） | 类别名字段允许附带脚注符号，并在note行生成对应解释 | 类别名带脚注符号 vs 纯净名称：标签精确匹配率 |
