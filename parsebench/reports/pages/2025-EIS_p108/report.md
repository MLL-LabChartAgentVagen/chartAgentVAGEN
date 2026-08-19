# 2025-EIS_p108

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2025-EIS | `need_estimate` | 10 | 10 |

该页只有一幅图（Figure 42），为31个欧洲国家的横向堆叠条形图（GOODS/SERVICES占高技术使用比重），并叠加以顶部第二数值轴读取的HHI短竖线序列，图例置于图下并附Source行。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 9.2 | `Ireland` · `Non-EU high-tech imports of GOODS as % of total high-tech use` | 5% | f1 | the Ireland green GOODS segment, read on the bottom 0-60 axis | 否 | `Ireland` · `Non-EU high-tech imports of GOODS as % of total high-tech use` |
| 2 | 43.8 | `Ireland` · `Non-EU high-tech imports of SERVICES as % of total high-tech use` | 5% | f1 | the Ireland orange SERVICES segment (bar total ~53 minus the green part) | 否 | `Ireland` · `Non-EU high-tech imports of SERVICES as % of total high-tech use` |
| 3 | 0.28 | `Ireland` · `HHI of non-EU high-tech imports of GOODS` | 5% | f1 | the Ireland dash marker, at ~0.28 on the top axis | 否 | `Ireland` · `HHI of non-EU high-tech imports of GOODS` |
| 4 | 31.2 | `Slovenia` · `Non-EU high-tech imports of GOODS as % of total high-tech use` | 5% | f1 | the Slovenia green GOODS segment on the bottom axis | 否 | `Slovenia` · `Non-EU high-tech imports of GOODS as % of total high-tech use` |
| 5 | 0.30 | `Slovenia` · `HHI of non-EU high-tech imports of GOODS` | 5% | f1 | the Slovenia dash marker, just past 0.3 on the top axis | 否 | `Slovenia` · `HHI of non-EU high-tech imports of GOODS` |
| 6 | 20.3 | `Türkiye` · `Non-EU high-tech imports of GOODS as % of total high-tech use` | 5% | f1 | the Türkiye green GOODS segment ending at about 20 on the bottom axis | 否 | `Türkiye` · `Non-EU high-tech imports of GOODS as % of total high-tech use` |
| 7 | 0.49 | `Czechia` · `HHI of non-EU high-tech imports of GOODS` | 5% | f1 | the Czechia dash marker, far right at about 0.49 on the top axis | 否 | `Czechia` · `HHI of non-EU high-tech imports of GOODS` |
| 8 | 14.9 | `Switzerland` · `Non-EU high-tech imports of SERVICES as % of total high-tech use` | 5% | f1 | the Poland green GOODS segment ending just below 15 on the bottom axis | 否 | `Poland` · `Non-EU high-tech imports of GOODS as % of total high-tech use` |
| 9 | 0.55 | `Greece` · `HHI of non-EU high-tech imports of GOODS` | 5% | f1 | the Greece dash marker, rightmost of all, at about 0.55 on the top axis | 否 | `Greece` · `HHI of non-EU high-tech imports of GOODS` |
| 10 | 24.2 | `Slovakia` · `Non-EU high-tech imports of GOODS as % of total high-tech use` | 5% | f1 | the Hungary bar total (green plus orange), ending at about 24 on the bottom axis | 否 | `Hungary` · `Non-EU high-tech imports of GOODS as % of total high-tech use` · `Non-EU high-tech imports of SERVICES as % of total high-tech use` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——10 values given, 11 answered
- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 14.9, 24.2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | horizontal | 1 | 3 | 31 | 93 | 无 | 0.1, 0.2, 0.3, 0.4, 0.5, 0.6 (top); 0, 10, 20, 30, 40, 50, 60 (bottom) |
| f2 | `other · none present` | na | 0 | 0 | 0 | 0 | 无 | （不画值轴） |

- **f1** Figure 42 / Shares and concentration of non-EU imports in EU and neighbouring countries. / HHI of non-EU high-tech imports of GOODS　[图上方]　单位 `% of total high-tech use`
  - 来源行：Source: Eurostat FIGARO
- **f2** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each country bar is a green GOODS segment plus an orange SERVICES segment, total is bar length |
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | top axis 0.1-0.6 labelled 'HHI ...', bottom axis 0-60 labelled '% of total high-tech use' |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | short vertical dash markers drawn over the stacked bars in the same plot area |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names on y axis, bars grow rightwards from 0 to 60 |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend swatch is a short vertical dash: 'HHI of non-EU high-tech imports of GOODS' |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: Eurostat FIGARO' in italics below the legend |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | three legend rows with swatches printed under the plot, above the Source line |
| `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | f1 | **无** | 'Non-EU high-tech imports of SERVICES as % of total high-tech use' in legend |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bottom axis of bare 0,10..60 with '% of total high-tech use' written under it |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | '% of total high-tech use' set below the 0-60 tick row |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | 'HHI of non-EU high-tech imports of GOODS' sits above the 0.1-0.6 top ticks |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 31 country names stacked down the y axis, from 'Ireland' to 'Croatia' |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | faint vertical rules rise at 0,10,...,60 across the rows; no horizontal rules |

词表 65 项，本页出现 13 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `secondary_axis_on_top` | f1 | second value axis (0.1-0.6, HHI) drawn on the top edge of a horizontal-bar plot | 读数前必须先判断某个标记归属顶部0.1-0.6轴还是底部0-60轴，否则数值差两个量级。 |
| `marker_series_on_other_axis` | f1 | dash markers overlay the bars but are scaled by the top HHI axis, not the 0-60 axis | 同一像素位置在两套刻度下含义不同，HHI值必须按顶部刻度换算，不能沿用条形的百分比刻度。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数字标注，全部要靠像素对刻度换算。底轴0到60跨约620像素，即1个百分点约10像素；9.2的5%容差仅±0.46，也就是不到5像素，而堆叠色块边界本身就有1-2像素的过渡，Ireland绿/橙分界与43.8的差值读数几乎踩在容差边缘。顶部HHI轴0.1间隔约106像素，0.28的5%容差±0.014仅约15像素，而HHI标记只是3像素宽的短竖线，且与其下方的橙色条重叠，容易与色块边界混淆；再加上必须先判断该标记按顶轴（0.1-0.6）而非底轴（0-60）换算，取值环节最易出错。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 secondary_axis_on_top（横向条形图顶部的第二数值轴） | 图表样式条件行中新增 axis_side 维度（top/bottom/left/right）与 secondary_axis 标志位 | “第二数值轴位于顶部/底部 vs 左右两侧”一行，检验模型能否把标记映射到正确刻度 |
| new | 一类出版方 | 新组件 marker_series_on_other_axis（短竖线序列按另一套刻度读取） | 记录字段中为每个 series 增加 axis_ref 字段，并允许 tick_marker 型 mark | “覆盖标记与条形共用刻度 vs 使用副轴刻度”一行 |
| P7 | 一类出版方 | unit_in_series_name 与 axis_title_below_plot 的组合（单位既在图例名内又在轴标题下方） | 标题/单位位置样式字段：unit_position 允许取 legend_name 与 below_axis 并存 | “单位只在轴标题 vs 同时写进图例名”一行，检验表格行名是否保留单位 |
| P5 | 通用 | wrapped_category_labels 下的高类别数（31行国家名） | 密度条件行：横向条形的 category 数上限提升到30以上 | “类别数≤12 vs 25-35 的横向条形”一行，把类别密度作为受控变量 |
