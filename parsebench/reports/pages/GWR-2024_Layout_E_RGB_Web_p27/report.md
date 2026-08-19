# GWR-2024_Layout_E_RGB_Web_p27

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| GWR-2024_Layout_E_RGB_Web | `untagged` | 10 | 0 |

这一页是《Global Wage Report 2024–25》第2章第6页，上半部分为图2.1（2006–24年以2015年不变价GDP衡量的年均经济增长，柱线混合图），下半部分为两栏正文并引出2.2节“Evolution of public debt”。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 5.3 | `2006` · `World` | 1% | f1 | the 2006 World bar (also printed on the 2007 World bar) | 是 | `Figure 2.1.` · `World` · `2006` |
| 2 | 3.1 | `2006` · `Advanced economies` | 1% | f1 | the 2006 Advanced economies line point (value also printed at 2010) | 是 | `Figure 2.1.` · `Advanced economies` · `2006` |
| 3 | 7.8 | `2006` · `Emerging and developing economies` | 1% | f1 | the 2006 Emerging and developing economies line point | 是 | `Figure 2.1.` · `Emerging and developing economies` · `2006` |
| 4 | -0.4 | `2009` · `World` | 1% | f1 | the 2009 World bar, drawn below the zero line | 是 | `Figure 2.1.` · `World` · `2009` |
| 5 | -3.4 | `2009` · `Advanced economies` | 1% | f1 | the 2009 Advanced economies line point, the series minimum for that decade | 是 | `Figure 2.1.` · `Advanced economies` · `2009` |
| 6 | 2.5 | `2009` · `Emerging and developing economies` | 1% | f1 | the 2009 Emerging and developing economies line point | 是 | `Figure 2.1.` · `Emerging and developing economies` · `2009` |
| 7 | -2.7 | `2020` · `World` | 1% | f1 | the 2020 World bar, extending below zero | 是 | `Figure 2.1.` · `World` · `2020` |
| 8 | 7.0 | `2021` · `Emerging and developing economies` | 1% | f1 | the 2021 Emerging and developing economies line point, label overlapping '6.6' | 是 | `Figure 2.1.` · `Emerging and developing economies` · `2021` |
| 9 | 3.2 | `2024` · `World` | 1% | f1 | the 2024 World bar | 是 | `Figure 2.1.` · `World` · `2024` |
| 10 | 1.8 | `2024` · `Advanced economies` | 1% | f1 | the 2024 Advanced economies line point (1.8 also printed at 2011) | 是 | `Figure 2.1.` · `Advanced economies` · `2024` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 3 | 19 | 57 | 全部 | -6, -4, -2, 0, 2, 4, 6, 8, 10 |

- **f1** Figure 2.1. / Annual average economic growth measured as GDP in constant 2015 prices, 2006–24　[图上方]　单位 `(percentage)`
  - 来源行：Source: IMF 2024b.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | blue 'World' bars with red and cyan lines plotted over them in one panel |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a zero rule drawn at 0 through which bars and lines cross |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | axis runs to -6; labels '-0.4', '-3.4', '-2.7', '-4.0', '-1.8' below the zero line |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: IMF 2024b.' in small print below the legend |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend row 'World  Advanced economies  Emerging and developing economies' under the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title ends '(percentage)'; axis title reads 'Real GDP growth (%)' |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'Real GDP growth (%)' set vertically along the left value axis |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | red and cyan point labels such as '3.1', '2.8', '2.5' sit on top of the blue bars |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '5.3', '2.9', '7.8', '8.1' printed above the bar tops and line markers |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | year ticks 2006 to 2024 set at about 45 degrees under the axis |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | '7.0' and '6.6' labels collide at 2021; '2.9'/'2.9' overlap near 2019 |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole figure block sits on a pale blue tinted band across the page |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at -6..10; no vertical grid lines in the plot |

词表 65 项，本页出现 13 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `label_collision_overlap` | f1 | at 2021 '7.0' (cyan) and '6.6' (blue bar) print on top of each other; '6.0' beside | 重叠标签使同一年份的三个系列数值难以归属，解析时可能把7.0误配给World柱或误读6.6。 |
| `line_over_bar_label_conflict` | f1 | red line labels (3.1, 2.8, 1.8...) printed inside blue bars of the same year | 数值印在别的系列的图形内部，读者必须靠颜色而非位置来分配数值到系列。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值全部印在图上，读数不成问题（步骤2轻松）；难点在于寻址：一个数要同时给出系列名（World / Advanced economies / Emerging and developing economies）和年份（2006–2024共19个），而柱与两条线共用同一年份槽，且线标签印在柱体内部，2021年的'7.0'与'6.6'、'6.0'几乎重叠。像'5.3'（2006与2007）、'3.1'（2006与2010）、'1.8'（2011与2024）在同一系列内重复出现，只有年份键能区分；解析器若把三系列压成一列或漏掉年份行头，值就无法唯一定位。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | mixed_marks（柱+多条折线叠加于同一面板）作为受控条件行 | 图表生成条件表中新增“bars_plus_n_lines”样式字段，允许折线数值标签落在柱体内部 | 同一面板柱+折线 vs 纯柱/纯折线，对比数值-系列配对准确率 |
| P1 | 一类出版方 | 新组件 label_collision_overlap（标签重叠） | 标签布局样式字段：允许关闭防碰撞、保留重叠标签 | 标签重叠 vs 无重叠时，同年份多系列数值的归属错误率 |
| P6 | 通用 | negative_values 与零线跨越（柱向下、折线跌至-4.0） | 数据记录字段允许负值，并在样式中固定绘制零参考线 | 含负值跨零 vs 全正值，对读数与符号丢失的影响 |
| P7 | 通用 | 标题五段拆分（Figure 2.1. / 标题 / 年份范围 / (percentage) 与竖排轴标题 Real GDP growth (%)） | 图注记录字段：figure_number、title、unit_text、rotated axis title 位置 | 单位仅在标题/仅在竖排轴标题/两处都有，导出表格是否携带单位 |
| P6 | 一类出版方 | sparse/rotated 类别轴（19个旋转年份刻度） | 类别轴样式行：刻度旋转角度与年份密度 | 旋转45度年份刻度 vs 水平刻度，对行标签抽取完整度 |
