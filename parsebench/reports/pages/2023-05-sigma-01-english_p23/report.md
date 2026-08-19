# 2023-05-sigma-01-english_p23

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2023-05-sigma-01-english | `need_estimate` | 10 | 10 |

该页为 Swiss Re Institute sigma 1/2023 第23页，正文讨论美国财产险风险敞口、赔付与保费，中部为 Figure 15 一幅柱线复合图（重置成本柱 + 两条保费指数线，2011 = 100）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 100 | `2011` · `Replacement cost of structures` | 5% | f1 | the 2011 Replacement cost of structures bar (index base) | 否 | `Figure 15` · `Replacement cost of structures` · `2011` |
| 2 | 100 | `2011` · `Personal property (homeowner) premiums` | 5% | f1 | the 2011 Personal property (homeowner) premiums point (index base) | 否 | `Figure 15` · `Personal property (homeowner) premiums` · `2011` |
| 3 | 118 | `2014` · `Replacement cost of structures` | 10% | f1 | the 2016 Replacement cost of structures bar | 否 | `Figure 15` · `Replacement cost of structures` · `2016` |
| 4 | 98 | `2016` · `Commercial property (fire & allied) premiums` | 10% | f1 | the 2016 Commercial property (fire & allied) premiums point, the dip just below the 100 gridline | 否 | `Figure 15` · `Commercial property (fire & allied) premiums` · `2016` |
| 5 | 122 | `2018` · `Personal property (homeowner) premiums` | 10% | f1 | the 2017 Replacement cost of structures bar | 否 | `Figure 15` · `Replacement cost of structures` · `2017` |
| 6 | 145 | `2019` · `Replacement cost of structures` | 5% | f1 | the 2020 Replacement cost of structures bar | 否 | `Figure 15` · `Replacement cost of structures` · `2020` |
| 7 | 125 | `2020` · `Commercial property (fire & allied) premiums` | 10% | f1 | the 2018 Personal property (homeowner) premiums point | 否 | `Figure 15` · `Personal property (homeowner) premiums` · `2018` |
| 8 | 175 | `2021` · `Replacement cost of structures` | 5% | f1 | the 2022 Personal property (homeowner) premiums point, the line endpoint | 否 | `Figure 15` · `Personal property (homeowner) premiums` · `2022` |
| 9 | 150 | `2022` · `Personal property (homeowner) premiums` | 5% | f1 | the 2021 Personal property (homeowner) premiums point | 否 | `Figure 15` · `Personal property (homeowner) premiums` · `2021` |
| 10 | 174 | `2022` · `Commercial property (fire & allied) premiums` | 5% | f1 | the 2022 Commercial property (fire & allied) premiums point, the line endpoint | 否 | `Figure 15` · `Commercial property (fire & allied) premiums` · `2022` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——6 of 10 predicted key sets miss a rule label: 118, 122, 145, 125, 175, 150

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 3 | 12 | 36 | 无 | 0, 50, 100, 150, 200 |

- **f1** Figure 15 / Exposure and premium growth, / US property, 2011 = 100　[与图并排]　单位 `2011 = 100`
  - 来源行：Source: US Bureau of Economic Analysis, S&P Global Capital IQ Pro, Swiss Re Institute

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | green bars for 2011-2022 with two overlaid lines in the same panel |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: US Bureau of Economic Analysis, S&P Global Capital IQ Pro, Swiss Re Institute" |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend rows sit under the year axis, above the Source line |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f1 | **无** | left column pull quote "The pandemic-induced surge in inflation has increased replacement costs in US property." level with figure |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis shows bare 0, 50, 100, 150, 200; scale word only in "2011 = 100" |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | heading reads "US property, 2011 = 100"; all series start near 100 in 2011 |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | plot area carries the same pale blue tint as the surrounding page block, not white |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 50, 100, 150, 200 only; no vertical rules |

词表 65 项，本页出现 8 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `multi_row_legend_mixed_glyphs` | f1 | first legend row a filled square for bars; second row two line dashes for the premium series | 读者需从图例符号形状判断哪一系列是柱、哪两条是线，否则无法把某年数值归到正确系列。 |
| `index_base_year_convergence` | f1 | all three series coincide near 100 at the 2011 slot by construction of the index base | 2011 处三条系列几乎重合，取值时靠像素无法区分系列，必须依赖基期=100的约定。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上无任何数值标签，刻度只有 0/50/100/150/200，即两条网格线之间跨 50 个指数点；要把 98 与 100、122 与 125 这类差 2–3 点的值读到 5% 容差（约 ±5–9 点）内，需要在约 1/20 格的精度上插值。更麻烦的是 2011–2013 三条系列与柱顶几乎重合（都在 97–103 之间），2022 年蓝线 175 与深绿线 174 仅差 1 点、在像素上交叠，值与系列的配对本身就会出错。相比之下寻址只需「系列名 + 年份」两个键，标题与来源行都完整可引。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P4 | 通用 | mixed_marks（柱+多条折线的复合图）作为独立图族权重 | 图族生成权重向量中新增 bar_plus_multiline 条目，并允许折线数≥2 | 去掉复合柱线族后，柱值与线值的系列归属错配率变化 |
| P7 | 一类出版方 | P7 的标题四分＋heading placement=beside（Figure 15 与标题、副标题在左侧栏与绘图区并排） | 记录层的 heading 字段（figure_number/title/subtitle/unit_text/placement）与样式层的侧栏排版 | 标题块置于绘图区左侧栏 vs 置于上方时，标题-数值绑定的准确率 |
| P6 | 一类出版方 | rebased_index_values（"2011 = 100" 指数基期写在标题行、值轴只有裸数字） | 单位位置样式维度：unit 只出现在副标题而非轴标签 | 单位仅在副标题 vs 单位在轴标题时，数值单位识别的差异 |
| new | 一类出版方 | 新组件 multi_row_legend_mixed_glyphs（图例分两行、方块与线段两种符号） | 图例样式字段：允许按符号类型分行排列的 legend 布局 | 多行异形符号图例 vs 单行同形图例时，系列名归属错误率 |
| P1 | 通用 | 提高刻度密度/可读精度设定（50 一格的稀疏刻度下按每个 mark 给出可达精度） | P1 的 readable 判定改为 per-mark 精度，并把刻度间距写入条件行 | 刻度间距 50 与 25 两档下，5% 容差内命中率对比 |
