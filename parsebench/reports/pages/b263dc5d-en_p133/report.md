# b263dc5d-en_p133

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b263dc5d-en | `need_estimate` | 10 | 10 |

本页为OECD报告第131页，主体是Figure 3.17，一张按国家排列的柱形加菱形标记组合图，显示非移民与移民识字能力差距的调整/未调整变化，配有注释与来源行。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 28 | `Germany` · `Unadjusted` | 5% | f1 | the Germany 'Unadjusted' bar, tallest bar reaching just below the 30 tick | 否 | `Germany` · `Unadjusted` |
| 2 | 17 | `Germany` · `Adjusted` | 10% | f1 | the Germany 'Adjusted' filled diamond between 10 and 20 | 否 | `Germany` · `Adjusted` |
| 3 | 19 | `Singapore` · `Unadjusted` | 5% | f1 | the United States 'Adjusted' filled diamond near 20 | 否 | `United States` · `Adjusted` |
| 4 | 12 | `Singapore` · `Adjusted` | 10% | f1 | the New Zealand 'Unadjusted' bar just above 10 | 否 | `New Zealand` · `Unadjusted` |
| 5 | 19 | `United States` · `Adjusted` | 5% | f1 | the Singapore 'Unadjusted' bar, near 20 (alternative to United States Adjusted) | 否 | `Singapore` · `Unadjusted` |
| 6 | -14 | `Lithuania` · `Unadjusted` | 5% | f1 | the Lithuania 'Unadjusted' bar extending below zero to about -14 | 否 | `Lithuania` · `Unadjusted` |
| 7 | -14 | `Italy` · `Adjusted` | 10% | f1 | the Italy 'Adjusted' filled diamond plotted near -14 | 否 | `Italy` · `Adjusted` |
| 8 | 18 | `Chile` · `Unadjusted` | 5% | f1 | the Chile 'Unadjusted' bar reaching just under 20 | 否 | `Chile` · `Unadjusted` |
| 9 | 9 | `Hungary` · `Unadjusted` | 5% | f1 | the Hungary 'Unadjusted' bar just below the 10 tick | 否 | `Hungary` · `Unadjusted` |
| 10 | 16 | `Flemish Region (BE)` · `Unadjusted` | 5% | f1 | the Flemish Region (BE) 'Unadjusted' bar around 16 | 否 | `Flemish Region (BE)` · `Unadjusted` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——10 values given, 11 answered
- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 19, 12, 19
- 系列数与系列名个数不一致——f1: series=4, 2 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 4 | 22 | 44 | 无 | 40, 30, 20, 10, 0, -10, -20 |

- **f1** Figure 3.17. / Change in the gap in literacy proficiency between non-immigrants and immigrants / Adjusted and unadjusted change between cycles in the mean score difference between native-born adults with native-born parents and foreign-born adults with foreign-born parents (Cycle 2 minus Cycle 1)　[图上方]　单位 `Score-point difference`
  - 来源行：Source: OECD (2018[4]; 2015[5]; 2012[6]), Survey of Adult Skills (PIAAC databases, http://www.oecd.org/skills/piaac/publicdataandanalysis/ (accessed on 23 September 2024); Tables A.3.15 (L) and A.3.16 (L) in Annex A.)

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | bars for 'Unadjusted' with diamond markers for 'Adjusted' overlaid in the same panel |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a heavy horizontal rule drawn at 0 across the whole plot |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | axis reads -10, -20 and bars for Italy, Czechia, Lithuania drop below the zero line |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | pale vertical tinted bands between Czechia/Singapore and Lithuania/Hungary separating rounds |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | 'Darker colours denote differences that are statistically significant at the 5% level.' |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | 'Adjusted' drawn as small open/filled diamonds at each country position on the same axis |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Adults aged 16-65; ...' and 'Source: OECD (2018[4]; 2015[5]; 2012[6])' under the plot |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | legend row sits at the top edge over the plot area, level with the 40 tick |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | 'Unadjusted' and 'Adjusted' legend keys sit between the subtitle and the plot top |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | 'Score-point difference' is the only scale word; ticks are bare 40, 30, 20 |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | 'OECD (2018[4]; 2015[5]; 2012[6])' subscript reference markers in the source line |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | 'Score-point difference' printed above the 40 tick at the axis top |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | country names plus an outer 'Round, Cycle 1:' band grouping them into 1, 2, 3 |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | country names 'Germany', 'Flemish Region (BE)' set vertically at 90 degrees |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 22 country names stacked vertically down the axis, 'Flemish Region (BE)' long label |
| `total_row_below_axis` | 轴下方一行合计值，与类目对齐 | f1 | **无** | 'Round, Cycle 1:' grey band under the axis reading 1, 2, 3 |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | 'Flemish Region (BE)' and 'England (UK)' axis labels set in blue, others black |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | vertical rules separate each country slot; no horizontal gridlines inside the panel |

词表 65 项，本页出现 18 项，其中我们画不出来的 13 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `significance_shading_paired_legend` | f1 | legend shows two swatches per series (white+shaded bar, open+filled diamond) for one name 'Unadjusted' | 同一系列名对应两种填色，读值时必须先判定该柱/菱形是深色还是浅色，否则会把显著性属性误当作第二个系列。 |
| `group_band_under_axis` | f1 | grey strip labelled 'Round, Cycle 1:' with segments 1, 2, 3 spanning country groups below labels | 该带是分组维度而非数值，定位某国数值时需附加其所属轮次，否则同名标签可能不唯一。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

数值全靠像素读取：刻度间距为10个分数点，绘图高度约200像素，一个刻度约33像素，而5%容差在数值为9或12时只有0.5左右分数点，约1.5像素，几乎无法分辨；更麻烦的是22个国家中菱形与柱顶常常重合（如Austria、France、Norway），Unadjusted与Adjusted只差1-2分数点，读值时极易互换，且没有任何数字印在图上。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | tick_marker_as_series（菱形标记系列叠加在柱上，共用同一数值轴） | 图表样式条件行中新增“同一类别内柱+点标记双系列”渲染模式，并在记录字段中区分 series_mark_shape | “柱与点标记重合时的系列归属正确率”一行，对比纯柱状图与柱+标记叠加图的取值错误率 |
| new | 一类出版方 | color_encodes_extra_attribute（深浅色表示5%显著性） | 记录字段增加与系列身份无关的 shade 属性，并在图例中生成成对色块 | “颜色承载额外属性时是否被误判为新系列”一行 |
| P2 | 这份文档自己的习惯 | total_row_below_axis / two_level_x_ticks（轴下 'Round, Cycle 1:' 分组带） | 类别轴样式字段增加轴下分组带层，并让 panel_key 包含分组名 | “轴下分组带是否进入寻址键”一行，比较仅国家名与国家名+轮次的命中率 |
| P7 | 通用 | P7 标题五分拆（Figure 3.17. + 标题 + 长副标题 + 'Score-point difference' 单位） | 图表标题字段拆为 number/title/subtitle/unit，并记录单位置于轴顶的位置 | “单位写在轴顶而非轴旁时，导出表是否保留单位”一行 |
