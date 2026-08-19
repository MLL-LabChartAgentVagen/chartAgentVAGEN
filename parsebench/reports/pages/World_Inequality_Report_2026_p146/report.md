# World_Inequality_Report_2026_p146

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `need_estimate` | 9 | 9 |

本页为《Political Cleavages》第8章第146页，上半部是一幅双折线图（Figure 8.2，西方民主国家1960–2025年教育与收入分歧），下半部为双栏正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | -14 | `1960–64` · `(% of top 10% educated voting left) minus (% of bottom 90% educated voting left)` | 10% | f1 | the 1960–64 point of the red educated-divide line | 否 | `1960–64` · `(% of top 10% educated voting left) minus (% of bottom 90% educated voting left)` · `Education and income divides in Western democracies, 1960–2025` |
| 2 | -11 | `1960–64` · `(% of top 10% earners voting left) minus (% of bottom 90% earners voting left)` | 10% | f1 | the 1965–69 point of the red educated-divide line | 否 | `1965–69` · `(% of top 10% educated voting left) minus (% of bottom 90% educated voting left)` |
| 3 | -3 | `1980–84` · `(% of top 10% educated voting left) minus (% of bottom 90% educated voting left)` | 10% | f1 | the 1980–84 point of the red educated-divide line | 否 | `1980–84` · `(% of top 10% educated voting left) minus (% of bottom 90% educated voting left)` |
| 4 | -13 | `1980–84` · `(% of top 10% earners voting left) minus (% of bottom 90% earners voting left)` | 10% | f1 | the 1980–84 point of the blue income-divide line | 否 | `1980–84` · `(% of top 10% earners voting left) minus (% of bottom 90% earners voting left)` |
| 5 | -15 | `1985–89` · `(% of top 10% earners voting left) minus (% of bottom 90% earners voting left)` | 10% | f1 | the 1975–79 point of the blue income-divide line | 否 | `1975–79` · `(% of top 10% earners voting left) minus (% of bottom 90% earners voting left)` |
| 6 | 5 | `2000–04` · `(% of top 10% educated voting left) minus (% of bottom 90% educated voting left)` | 10% | f1 | the 2000–04 point of the red educated-divide line (peak near 6) | 否 | `2000–04` · `(% of top 10% educated voting left) minus (% of bottom 90% educated voting left)` |
| 7 | -9 | `2000–04` · `(% of top 10% earners voting left) minus (% of bottom 90% earners voting left)` | 10% | f1 | the 2010–14 point of the blue income-divide line | 否 | `2010–14` · `(% of top 10% earners voting left) minus (% of bottom 90% earners voting left)` |
| 8 | 11 | `2020–25` · `(% of top 10% educated voting left) minus (% of bottom 90% educated voting left)` | 10% | f1 | the 2020–25 point of the red educated-divide line | 否 | `2020–25` · `(% of top 10% educated voting left) minus (% of bottom 90% educated voting left)` |
| 9 | -7 | `2020–25` · `(% of top 10% earners voting left) minus (% of bottom 90% earners voting left)` | 10% | f1 | the 2020–25 point of the blue income-divide line | 否 | `2020–25` · `(% of top 10% earners voting left) minus (% of bottom 90% earners voting left)` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 9 predicted key sets miss a rule label: -11, -15, -9

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 2 | 13 | 26 | 无 | 15%, 10%, 5%, 0%, −5%, −10%, −15%, −20% |
| f2 | `other · none` | na | 0 | 0 | 0 | 0 | 无 | （不画值轴） |

- **f1** Figure 8.2. / Educated voters increasingly support the left, while high-income voters continue leaning right / Education and income divides in Western democracies, 1960–2025　[图上方]　单位 `Difference (pp): top 10% minus bottom 90% voting left`
  - 来源行：Sources and series: Gethin et al. (2021) and World Political Cleavages and Inequality Database (wpid.world).
- **f2** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a dotted horizontal rule drawn across the panel at 0% |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | axis reads down to −20% and both lines sit below 0% for most of the period |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | boxed red note 'Higher−educated voters voting for left−wing parties...' and blue box over plot |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Interpretation. In the 1960s...' and 'Sources and series: Gethin et al. (2021)' below the figure |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two marker+text legend entries sit in a row beneath the category axis |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | blue box 'Top−income voters voting for right−wing parties (other parties)' drawn inside the plot area |
| `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | f1 | **无** | legend entries read '(% of top 10% educated voting left) minus (% of bottom 90% educated voting left)' |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | y-axis title carries 'Difference (pp)'; ticks themselves read '15%' ... '−20%' |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'Difference (pp): top 10% minus bottom 90% voting left' set vertically along the y axis |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | none printed; not reported |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | '1960–64' ... '2020–25' set at roughly 45 degrees under the axis |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | time axis written as five-year spans '1975–79', '2020–25' rather than single years |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | legend labels wrap over two lines: '(% of top 10% educated voting left) minus / (% of bottom 90% ...)' |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each y tick, no vertical rules in the panel |

词表 65 项，本页出现 14 项，其中我们画不出来的 9 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `callout_color_matches_series` | f1 | red-bordered red-text box labels the red line; blue-bordered blue box labels the blue line | 标注框的颜色是唯一把说明文字绑定到某条折线的线索，取值时须靠颜色而非位置判断归属。 |
| `interpretation_paragraph_below_figure` | f1 | a full paragraph headed 'Interpretation.' sits between the legend and the source sentence | 该段落含'more than 10 percentage points'等数值性表述，解析时可能被误当作图内数据或与来源行混淆。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，26个点全靠对 15%~−20% 的刻度读数；刻度间距为5个百分点，而 −3 这类小值的5%容差仅0.15pp，相当于刻度间距的三十分之一，像素级读数几乎不可能落在容差内；同时 0% 附近的点（1990–94 约 −0.5）符号都可能读错，因此取值本身是最大阻碍，标签方面每个值只需'时段+图例长名'两个键即可定位，相对可控。

整页原图判不出来的：
- `f2`（other）：该条目为占位：页面下半部为双栏正文，不是图，无可判读内容。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | reference_line 与 negative_values 组合：零线为点线且系列跨越零线 | 样式条件行中新增'零线样式（点线/实线）+ 数据跨零'字段，并在记录中标注每点符号 | 折线跨零 vs 全正折线的读数符号正确率对比行 |
| new | 一类出版方 | 新组件 callout_color_matches_series（彩色标注框替代图例绑定系列） | 布局条件行：legend_inside_plot 之外增加'颜色一致的注释框'开关 | 注释框颜色与系列一致 vs 中性色注释框时的系列归属准确率行 |
| P7 | 通用 | unit_in_axis_or_title：单位分散在旋转的y轴标题（'Difference (pp)'）与百分号刻度两处 | heading 记录字段拆分：unit_text 独立于 title/subtitle，并记录 rotated_axis_title 位置 | 单位仅在轴标题 vs 单位在刻度上时的量纲还原行 |
| P3 | 一类出版方 | wrapped_category_labels / 超长两行图例名作为唯一寻址键 | 系列名生成器：允许含括号与'minus'的多行长标签 | 长换行系列名 vs 短系列名时的行寻址命中率行 |
| P6 | 一类出版方 | nonstandard_time_ticks：五年区间刻度（'1960–64'…'2020–25'） | 类别轴格式字段增加'区间型时间标签'选项 | 区间时间刻度 vs 单年刻度的时间键匹配行 |
