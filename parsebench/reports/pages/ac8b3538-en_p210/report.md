# ac8b3538-en_p210

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ac8b3538-en | `need_estimate` | 6 | 6 |

该页为OECD《就业展望2024》第208页，包含Figure 4.8（A/B两个带95%置信区间误差线的负值柱状图）及其Note/Reading/Source小字和正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | -24 | `A. Formal` · `New green-driven occupations` | 5% | f1 | the New green-driven occupations bar in Panel A | 否 | `Figure 4.8.` · `A. Formal` · `New green-driven occupations` |
| 2 | -51 | `A. Formal` · `Established green-driven occupations` | 5% | f1 | the Established green-driven occupations bar in Panel A | 否 | `Figure 4.8.` · `A. Formal` · `Established green-driven occupations` |
| 3 | -31 | `A. Formal` · `GHG-intensive occupations` | 5% | f1 | the GHG-intensive occupations bar in Panel A | 否 | `Figure 4.8.` · `A. Formal` · `GHG-intensive occupations` |
| 4 | 15 | `B. Not formal` · `New green-driven occupations` | 5% | f1 | the New green-driven occupations bar in Panel B, the only bar above zero | 否 | `Figure 4.8.` · `B. Not formal` · `New green-driven occupations` |
| 5 | -19 | `B. Not formal` · `Established green-driven occupations` | 5% | f1 | the Established green-driven occupations bar in Panel B | 否 | `Figure 4.8.` · `B. Not formal` · `Established green-driven occupations` |
| 6 | -11 | `B. Not formal` · `GHG-intensive occupations` | 10% | f1 | the GHG-intensive occupations bar in Panel B | 否 | `Figure 4.8.` · `B. Not formal` · `GHG-intensive occupations` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 2 | 1 | 3 | 6 | 无 | 20, 10, 0, -10, -20, -30, -40, -50, -60 |

- **f1** Figure 4.8. / Workers in green-driven and GHG-intensive occupations train less than average / Point estimate of the percentage difference between workers that participate in training and those that do not participate, 2018　[图上方]　单位 `%`
  - 来源行：Source: OECD estimates based on version 24.1 of the O*NET database and the following country-specific sources: Australia: Table Builder of the Australian Bureau of Statistics (Labour Force: Characteristics of Employment); United States: Current Population Survey; All other countries: EU Structure of Earnings Surveys.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a thick black horizontal rule at 0 crosses each panel full width |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | five of six bars hang below the 0 line down to about -51; ticks run to -60 |
| `error_bars` | 误差棒 / 置信带 | f1 | **无** | whiskers on every bar top; Note says "(and 95% confidence intervals)" |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | each panel draws its own left axis and "%" label rather than one shared axis |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | two identical bar panels side by side over the same three occupation categories |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | small print below: "Note: Panel A and B report...", "Reading: ...", "Source: OECD estimates..." |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | "A. Formal" and "B. Not formal" set above their own plots |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | subtitle "Point estimate of the percentage difference..." fixes scale; axis shows bare 20, 10, 0, -10 |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | a bare "%" printed above the top tick "20" on each panel |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | "New green-driven / occupations" and "Established green- / driven occupations" wrap onto two lines |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | both plot areas carry a light grey fill instead of white |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | white vertical rules separate the three category slots; no horizontal grid lines inside the grey area |

词表 65 项，本页出现 12 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `category_specific_bar_colors_no_legend` | f1 | three bars in each panel are bright green, pale green and dark green with no legend anywhere | 颜色与x轴类别一一对应但无图例，读值时只能靠轴标签定位，颜色不提供额外键。 |
| `reading_line_states_values` | f1 | "Reading: ... 50% lower among employees who undertake formal training and 18% lower..." "31% ... 12%" | 小字Reading行给出与柱高接近但四舍五入不同的数字，可能与图上像素读数冲突，需说明取值来源。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，六个值全靠像素对轴读取。刻度间距为10个百分点（约33px），而-11这一根柱的5%容差只有±0.55，即约1.8px；15那根同样只有±0.75（约2.5px）。加之柱顶被误差线上下须遮盖，柱端真实位置本身模糊，读数精度难以达标。相比之下标签只需三个键（Figure 4.8. + A/B面板名 + 类别名），Reading行还给出50/18/31/12等参考数字，反而使标签与上下文相对可解。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 一类出版方 | error_bars（含95%置信区间须线）作为可控样式维度 | 样式字段新增 error_bar 开关及须长比例，条件行区分“有须/无须” | 有误差须 vs 无误差须时的每标记读值精度对比 |
| P2 | 通用 | panel_title_per_panel + 面板维度进入键（A. Formal / B. Not formal） | 记录字段加入 panel_key，导出表格行需带面板名 | 含 panel_key vs 仅类别键时的定位命中率 |
| P6 | 通用 | negative_values 与零参考线（reference_line at 0）组合 | 样式维度：零线绘制方式、负值刻度顺序（20…-60） | 含负值+零线的柱图 vs 全正值柱图的读值误差 |
| P7 | 一类出版方 | 标题四拆：figure_number/title/subtitle/unit（“%”置于顶刻度之上） | 图题记录结构拆成独立字段，unit 位置可选 above-axis | unit 位于轴上方 vs 位于副标题时的单位还原率 |
