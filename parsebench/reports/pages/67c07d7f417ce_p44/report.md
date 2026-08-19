# 67c07d7f417ce_p44

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 67c07d7f417ce | `untagged` | 7 | 0 |

AXA 2024全年业绩演示第44页，用两幅无数值轴的自制图展示2025年不同巨灾成本水平下集团盈利偏离（左，双向条形分布）与平均预期巨灾费用2024/2025对比（右）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | -1.3 | `1/20y` | 1% | f1 | the deepest (leftmost) negative bar, labelled at the bottom left | 是 | `Group underlying earnings deviation to average Nat Cat charges in 2025` · `net of reinsurance, post-tax` · `1/20y` · `(95th)` · `€-1.3bn` |
| 2 | -0.8 | `1/10y` | 1% | f1 | a negative bar around the 1/10y (90th) position, labelled "€-0.8bn" | 是 | `Group underlying earnings deviation to average Nat Cat charges in 2025` · `1/10y` · `(90th)` · `€-0.8bn` |
| 3 | -0.4 | `1/5y` | 1% | f1 | a negative bar around the 1/5y (80th) position, labelled "€-0.4n" (printed without the b) | 是 | `Group underlying earnings deviation to average Nat Cat charges in 2025` · `1/5y` · `(80th)` · `€-0.4n` |
| 4 | 0.1 | `Median` | 1% | f1 | the first positive bar just right of the Median (50th) marker, labelled "€+0.1bn" | 是 | `Group underlying earnings deviation to average Nat Cat charges in 2025` · `Median` · `(50th)` · `€+0.1bn` |
| 5 | 0.6 | `1/5y` | 1% | f1 | a positive bar near the 1/5y (20th) position, labelled "€+0.6bn" | 是 | `Group underlying earnings deviation to average Nat Cat charges in 2025` · `1/5y` · `(20th)` · `€+0.6bn` |
| 6 | 0.7 | `1/10y` | 1% | f1 | a positive bar near the 1/10y (10th) position, labelled "€+0.7bn" | 是 | `Group underlying earnings deviation to average Nat Cat charges in 2025` · `1/10y` · `(10th)` · `€+0.7bn` |
| 7 | 0.8 | `1/20y` | 1% | f1 | the tallest, rightmost positive bar at 1/20y (5th), labelled "€+0.8bn" | 是 | `Group underlying earnings deviation to average Nat Cat charges in 2025` · `1/20y` · `(5th)` · `€+0.8bn` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 1 | 1 | 7 | 55 | 部分 | （不画值轴） |
| f2 | `bar` | vertical | 1 | 1 | 2 | 2 | 全部 | （不画值轴） |

- **f1** Group underlying earnings deviation to average Nat Cat charges in 2025 / net of reinsurance, post-tax　[图上方]　单位 `In Euro billion`
- **f2** Average expected Nat Cat charges / net of reinsurance, pre-tax　[图上方]　单位 `In Euro billion`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | bars hang below the horizontal rule down to the printed label "€-1.3bn" at bottom left |
| `broken_axis` | 断轴：轴中间截断并画出断裂标记 | f1 | **无** | double-slash break glyphs drawn on both horizontal arrow axes near their arrowheads |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | italic notes over plot: "More severe years / Negative deviation in ca. 40% of cases", "Less severe years..." |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only arrow axes and printed labels like "€+0.6bn"; no ticks on any value axis |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | two bars with "2.5" and "2.7" printed above them, no axis or ticks drawn |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately headed plots split by a vertical rule: "Group underlying earnings deviation..." and "Average expected Nat Cat charges" |
| `source_note_lines` | source / note 行在图下方 | page | 有 | small print under figures: "1. Natural catastrophe cost defined as Aggregate Exceedance Probability (AEP)..." |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | page | **无** | "In Euro billion" under the page title; bars carry bare numbers "2.5", "2.7" |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | page title reads "Nat Cat cost¹ in 2025" with superscript 1 keyed to bottom note |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | "ca. 4.5%" printed inside a grey pill and a blue pill below each bar |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | "€+0.8bn", "€+0.7bn", "€-0.8bn" sit beyond the bar tips, not on them |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | "2.5" and "2.7" printed above the tops of the grey and blue bars |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | "1/20y" over "(95th)", "1/10y" over "(90th)", "Median" over "(50th)" |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f2 | **无** | 2025 bar in dark blue with bold "2.7"; 2024 bar pale grey with regular "2.5" |

词表 65 项，本页出现 12 项，其中我们画不出来的 9 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `metric_row_below_axis_with_row_label` | f2 | "Estimated impact on GEP" at left, two pills "ca. 4.5%" aligned under the 2024 and 2025 bars | 这一行是位于类别轴下方、由左侧行标题寻址的第二个指标，读值时必须区分它与柱高值（2.5/2.7），否则4.5%会被错配给柱子。 |
| `exceedance_curve_as_bars` | f1 | ~55 unlabeled bars form a smooth exceedance profile; only 7 return-period ticks (1/20y…) mark positions | 绝大多数条形没有类别名，只有7个重现期刻度可定位，被打分的数值只能靠贴近的文字标签寻址，而非按条形逐一寻址。 |
| `bidirectional_arrow_axes` | f1 | one rule with a left arrow above the negative bars, a second lower rule with a right arrow under the positive bars | 两条各自带箭头的轴线让零基线与概率轴分离，判断某条形属正偏离还是负偏离需看它挂在哪条线上。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

七个被打分的数值全部以文字形式印在图上（€-1.3bn…€+0.8bn），所以像素读值不是瓶颈；真正卡住的是寻址。f1约55根条形只有7个重现期刻度（1/20y (95th)…1/20y (5th)），且左右两侧的"1/20y"、"1/10y"、"1/5y"文字完全重复，仅靠括号内的百分位（95th vs 5th）区分——一行表格至少要同时携带图标题、正/负偏离侧（"More severe years"/"Less severe years"）和百分位三把钥匙，才能让-0.8与+0.7不互相冲突。此外-0.4的标签印成"€-0.4n"，字符串匹配还需容错。条形数量因过密只能估计（约55根）。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 一类出版方 | P7式的五段标题拆分：图号为空、标题、副标题（"net of reinsurance, post-tax"）、单位（"In Euro billion"位于页标题下而非图内）、以及heading placement | 记录字段中新增 heading 结构，并允许 unit_text 归属于页级而非图级 | 单位短语在页标题层 vs 图标题层两种条件下，取值行能否被正确赋予比例尺 |
| P6 | 这份文档自己的习惯 | 新组件 metric_row_below_axis_with_row_label（"Estimated impact on GEP" + 两个"ca. 4.5%"药丸） | 样式字段增加"类别轴下方附加指标行"及其左侧行标题的开关 | 有/无轴下附加指标行时，柱值(2.5/2.7)与派生比例(4.5%)是否被混入同一列 |
| P6 | 一类出版方 | negative_values + no_value_axis 组合：仅靠印字标签读值、零基线上下双向条形 | 条件行中把"值轴刻度缺失"与"零线两侧条形"设为可组合的样式维度 | 无值轴且仅部分条形带标签时，per-mark 可达精度（values_printed=some）作为可控变量 |
| P5 | 这份文档自己的习惯 | 新组件 exceedance_curve_as_bars：约55根条形中仅7个位置有刻度名 | 密度上限与"每标记是否可寻址"的生成条件（未命名条形比例） | 可寻址标记占比 10% vs 100% 时的检索命中率 |
| P6 | 一类出版方 | broken_axis 的双斜线断轴符号出现在类别/概率轴而非值轴上 | 断轴样式字段允许作用于类别轴方向 | 断轴符号在值轴 vs 类别轴时，坐标到数值的映射是否被误判 |
