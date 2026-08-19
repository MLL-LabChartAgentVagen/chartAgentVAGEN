# World_Inequality_Report_2026_p18

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `need_estimate` | 6 | 6 |

本页为报告执行摘要第18页，顶部是编号为 Figure 6 的双面板柱状图（左为按性别的工作小时堆叠柱、右为女性时薪占男性比例），下方为解释与注释文字，页面下半是两栏正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 20 | `Women` · `Economic labor` | 10% | f1 | the Women bar's lower solid 'Economic labor' segment in the left panel | 否 | `Hours worked per week` · `Women` · `Economic labor` |
| 2 | 33 | `Women` · `Domestic labor` | 10% | f1 | the Women bar's upper dotted 'Domestic labor' segment (53 minus the economic part) | 否 | `Hours worked per week` · `Women` · `Domestic labor` |
| 3 | 33 | `Men` · `Economic labor` | 10% | f1 | the Men bar's lower solid 'Economic labor' segment in the left panel | 否 | `Hours worked per week` · `Men` · `Economic labor` |
| 4 | 10 | `Men` · `Domestic labor` | 10% | f1 | the Men bar's upper dotted 'Domestic labor' segment (43 minus the economic part) | 否 | `Hours worked per week` · `Men` · `Domestic labor` |
| 5 | 61 | `Conventional` · `Excluding domestic labor` | 1% | f1 | the 'Conventional' blue bar in the right panel, labelled 61% | 是 | `Women's hourly income (% of men's)` · `Conventional` · `Excluding domestic labor` |
| 6 | 32 | `Real` · `Including domestic labor` | 1% | f1 | the 'Real' orange bar in the right panel, labelled 32% | 是 | `Women's hourly income (% of men's)` · `Real` · `Including domestic labor` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 2 | 4 | 2 | 6 | 部分 | left panel: 0, 10, 20, 30, 40, 50, 60, 70; right panel: 0%, 10%, 20%, 30%, 40%, 50%, 60%, 70% |

- **f1** Figure 6. / After including domestic labor, women earn only 32% of men's hourly income / Gender gap including domestic labor hours, 2020–2025　[图上方]　（标题里没有单位）
  - 来源行：Sources and series: Andreescu et al. (2025).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | left panel bars split into a solid lower part and a dotted upper part, totals 53 and 43 |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left axis 0–70 hours, right axis 0%–70%, separate axes per panel |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | left bars green for Women, red for Men, while series identity is carried by dotted vs solid fill |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Interpretation.', 'Notes.' and 'Sources and series: Andreescu et al. (2025).' printed under the figure |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | both legend rows sit under the plots, below the 'Women / Men' and 'Conventional / Real' ticks |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | 'Domestic labor / Economic labor' for left panel, 'Excluding / Including domestic labor' for right |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | left panel stacked bars of hours, right panel plain single bars of percentages |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | 'Hours worked per week' and "Women's hourly income (% of men's)" set above each panel |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 0–70 explained only by rotated title '(hours per week)'; right panel '(% male hourly income)' |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'Average labor time (hours per week) (15–to–64–year–old) (2020–2025)' set vertically along left axis |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '53' and '43' printed above the bar tops; '61%' and '32%' above the right-panel bars |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | dotted horizontal rules at each 10-unit tick across both panels, no vertical rules |

词表 65 项，本页出现 12 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `pattern_fill_series` | f1 | legend swatches: dotted-hatch box for 'Domestic labor', empty white box for 'Economic labor' | 同一根柱的两段靠点状填充与空白填充区分，而颜色只表示性别，读某一段的数值必须先按填充纹理判断它属于哪个系列。 |
| `segment_boundary_only_readable` | f1 | only stack totals 53 and 43 are printed; the internal split must be read at the dotted boundary line | 堆叠段的数值只能通过段边界与0–70刻度比对推得，误差直接受10单位刻度间距限制。 |
| `category_is_series` | f1 | right panel: 'Conventional' bar is blue = 'Excluding domestic labor', 'Real' = 'Including domestic labor' | 右面板每个类别只有一根柱且与图例一一对应，定位一个值时类别名与系列名冗余，表格行可能只保留其中一个。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

六个目标值里只有 61% 和 32% 被印在图上，左面板四个堆叠段一个数字都没印：柱顶只标了 53 与 43。要得到 20、33、33、10 必须在 0,10,…,70 的刻度上量段边界，刻度间距10单位而 10 这个段 5% 容差只有 ±0.5 单位，约为一格的二十分之一；Men 柱的边界又与 30 到 40 之间的虚线网格错开，几乎无法在容差内读出。相比之下定位标签只需 3 个键（面板名+Women/Men+Domestic/Economic labor），面板标题以粗体形式存在，反而不是主要障碍。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | per_panel_axis_range 与 panel_title_per_panel 的组合（面板维度进入行键） | 记录字段中为每个 mark 增加 panel_key，并要求面板标题逐面板输出为加粗行首 | 有/无 panel_key 时，双面板不同单位（hours vs %）图的取值命中率对比 |
| P6 | 一类出版方 | new_components 中的 pattern_fill_series（点状填充 vs 空白填充区分系列） | 样式条件行新增 fill_pattern 维度，与颜色编码解耦 | 系列由纹理而非颜色区分时，堆叠段归属判定的准确率一行 |
| P1 | 一类出版方 | segment_boundary_only_readable：只标堆叠总量、不标分段值 | value-label 放置样式字段增加 total_only 选项（总量印在柱顶，分段不印） | 分段值印出 vs 仅印总量两种条件下，堆叠段读数在5%容差内的达成率 |
| P7 | 通用 | 标题五段切分（figure number / title / subtitle / 旋转轴标题里的单位） | P7 的标题记录字段，允许单位只存在于旋转的纵轴标题而非标题行 | 单位位于旋转轴标题 vs 位于副标题时，导出表能否携带正确单位一行 |
