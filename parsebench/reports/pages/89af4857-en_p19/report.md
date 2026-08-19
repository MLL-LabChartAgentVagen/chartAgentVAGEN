# 89af4857-en_p19

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 89af4857-en | `need_estimate` | 10 | 10 |

该页为OECD《经济展望中期报告2025年3月》第17页，上部是Figure 9的两联柱状图（A. GDP level与B. Consumer price inflation），下方为注释、来源行及第22–24段正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | -0.28 | `WLD` · `A. GDP level` | 10% | f1 | the WLD bar in panel A | 否 | `A. GDP level` · `WLD` · `Figure 9.` |
| 2 | -0.73 | `USA` · `A. GDP level` | 10% | f1 | the USA bar in panel A | 否 | `A. GDP level` · `USA` · `Figure 9.` |
| 3 | -0.64 | `CAN` · `A. GDP level` | 10% | f1 | the CAN bar in panel A | 否 | `A. GDP level` · `CAN` · `Figure 9.` |
| 4 | -1.30 | `MEX` · `A. GDP level` | 10% | f1 | the MEX bar in panel A | 否 | `A. GDP level` · `MEX` · `Figure 9.` |
| 5 | 0.38 | `WLD` · `B. Consumer price inflation` | 10% | f1 | the WLD bar in panel B | 否 | `B. Consumer price inflation` · `WLD` · `Figure 9.` |
| 6 | 0.70 | `USA` · `B. Consumer price inflation` | 5% | f1 | the USA bar in panel B | 否 | `B. Consumer price inflation` · `USA` · `Figure 9.` |
| 7 | 0.90 | `CAN` · `B. Consumer price inflation` | 10% | f1 | the CAN bar in panel B | 否 | `B. Consumer price inflation` · `CAN` · `Figure 9.` |
| 8 | 0.67 | `MEX` · `B. Consumer price inflation` | 5% | f1 | the MEX bar in panel B | 否 | `B. Consumer price inflation` · `MEX` · `Figure 9.` |
| 9 | 0.31 | `CHN` · `B. Consumer price inflation` | 10% | f1 | the CHN bar in panel B | 否 | `B. Consumer price inflation` · `CHN` · `Figure 9.` |
| 10 | 0.17 | `JPN` · `B. Consumer price inflation` | 20% | f1 | the JPN bar in panel B | 否 | `B. Consumer price inflation` · `JPN` · `Figure 9.` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 2 | 1 | 9 | 18 | 无 | 0.00, -0.25, -0.50, -0.75, -1.00, -1.25, -1.50 \| 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0 |

- **f1** Figure 9. / Further trade fragmentation would harm global growth prospects / Simulation of a rise of 10 percentage points in US tariffs on non-commodity imports from all countries and 10 percentage points higher tariffs on non-commodity imports from the United States by all countries　[图上方]　单位 `%`
  - 来源行：Source: OECD calculations using the NiGEM global macroeconomic model and the OECD METRO model.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | Panel A axis runs 0.00 down to -1.50; all nine bars hang below the 0.00 line |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | Panel A ticks 0.00 to -1.50 in 0.25 steps; Panel B ticks 0.0 to 1.0 in 0.1 steps |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | each panel draws its category axis once; the same nine codes align under both plots |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | two side-by-side bar panels A and B over the same nine country codes |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: Illustrative scenario of the impact of 10% US tariffs..." and "Source: OECD calculations..." below |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | "A. GDP level" and "B. Consumer price inflation" set in bold above each plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare numeric ticks; scale given only by "%" and "% pts" beside the axis tops |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "%" sits above the 0.00 tick in A; "% pts" above the 1.0 tick in B |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | x ticks read "WLD OECD USA EA JPN CHN IND CAN MEX" in both panels |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at each tick in both plots, no vertical grid lines |

词表 65 项，本页出现 10 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `zero_baseline_at_axis_top` | f1 | Panel A's 0.00 tick is the topmost gridline; bars are drawn downward from it | 读数方向反转：柱长要从顶部0.00向下量，若按常规自底向上会得到正号或错误量级。 |
| `per_panel_unit_differs` | f1 | Panel A labelled "%", Panel B labelled "% pts" above their axes | 两联图单位不同，取值必须绑定所属面板，不能跨面板共用同一单位标注。 |
| `panel_specific_series_colour` | f1 | Panel A bars are light blue, Panel B bars are purple, with no legend | 颜色不编码系列而区分面板，读者只能靠面板标题定位，不能靠图例辨认。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

全部18根柱子都没有数值标签，只能靠网格线量。A面板网格间距0.25，而-0.28要求5%容差即±0.014，相当于格距的1/18；B面板网格间距0.1，0.17的5%容差为±0.0085，不到格距的1/10，甚至0.90与0.9网格线重合才好读。像-0.73（介于-0.50与-0.75之间）、-1.30（在-1.25网格线略下方）这类值必须做亚像素插值才能落进容差，因此读数本身是最硬的一环；标签方面每个值只需“面板名+国别代码”两个键，表格容易承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | zero_baseline_at_axis_top（新键）与negative_values组合 | 样式条件行中的零线/轴方向字段：允许值轴自0向负方向递减、零线画在顶部 | “零线位于轴顶、全负柱向下”与“零线居中双向柱”两种负值布局分别统计读数误差 |
| P2 | 一类出版方 | per_panel_unit_differs（新键）与per_panel_axis_range | 记录字段中为每个panel单独存unit与轴刻度范围，而非图级共享 | 面板间单位/刻度一致 vs 不一致（% 对 % pts）时取值绑定正确率对比 |
| P6 | 一类出版方 | axis_title_above_axis（“%”、“% pts”置于顶端刻度上方） | 样式字段unit_position：新增“轴顶刻度上方的裸单位符号”选项 | 单位位于轴旁/副标题/轴顶上方三种位置时单位识别率一行 |
| P7 | 通用 | 标题四分（figure_number/title/subtitle/panel subtitle）与panel_title_per_panel | P7标题字段：图号“Figure 9.”、长副标题及每面板第二行说明（“Difference from baseline, year 3”）分别存储 | 面板副标题作为独立字段导出 vs 合并进面板名时上下文命中率一行 |
