# FPA-guide-to-data-visualization_p8

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| FPA-guide-to-data-visualization | `need_estimate` | 10 | 10 |

这是AFP数据可视化指南第5页，两栏正文讨论预测可信度与Metapraxis的“Windsock”图，页面下半是一张无编号的“Western Europe Net Sales Windsock”组合图（灰色情景带＋预算/去年/预测三条线）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 218 | `Budget` · `Jan 14` | 5% | f1 | the flat orange Budget line, read at Jan 14 | 否 | `Western Europe Net Sales Windsock` · `Budget` · `Jan 14` · `$m` |
| 2 | 218 | `Budget` · `Nov` | 5% | f1 | the same flat Budget line read at a later month (it is constant, e.g. Dec) | 否 | `Western Europe Net Sales Windsock` · `Budget` · `Dec` · `$m` |
| 3 | 166 | `Prior Year` · `Jan 14` | 5% | f1 | the flat red Prior Year line, read at Jan 14 | 否 | `Western Europe Net Sales Windsock` · `Prior Year` · `Jan 14` · `$m` |
| 4 | 166 | `Prior Year` · `Jun` | 5% | f1 | the flat red Prior Year line, read at a mid-year month (e.g. Jun) | 否 | `Western Europe Net Sales Windsock` · `Prior Year` · `Jun` · `$m` |
| 5 | 166 | `Prior Year` · `Dec` | 5% | f1 | the flat red Prior Year line, read at a late month (e.g. Dec) | 否 | `Western Europe Net Sales Windsock` · `Prior Year` · `Dec` · `$m` |
| 6 | 218 | `Forecast` · `Jan 14` | 5% | f1 | the Forecast line at its Jan 14 start, sitting on the Budget level | 否 | `Western Europe Net Sales Windsock` · `Forecast` · `Jan 14` · `$m` |
| 7 | 216 | `Forecast` · `Feb` | 5% | f1 | the Forecast line at Feb | 否 | `Western Europe Net Sales Windsock` · `Forecast` · `Feb` · `$m` |
| 8 | 212 | `Forecast` · `Mar` | 5% | f1 | the Forecast line at Mar | 否 | `Western Europe Net Sales Windsock` · `Forecast` · `Mar` · `$m` |
| 9 | 210 | `Forecast` · `Apr` | 5% | f1 | the Forecast line at Apr | 否 | `Western Europe Net Sales Windsock` · `Forecast` · `Apr` · `$m` |
| 10 | 200 | `Forecast` · `May` | 5% | f1 | the Forecast line endpoint at May, on the dashed vertical rule | 否 | `Western Europe Net Sales Windsock` · `Forecast` · `May` · `$m` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: 218

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 4 | 12 | 34 | 无 | 100, 120, 140, 160, 180, 200, 220 |

- **f1** Western Europe Net Sales Windsock　[图上方]　单位 `$m`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | grey filled `Scenarios` bands and three plotted lines (`Budget`, `Prior Year`, `Forecast`) share one panel |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | flat orange `Budget` rule at ~218 and red `Prior Year` rule at ~166 run the full width, each with a legend entry |
| `error_bars` | 误差棒 / 置信带 | f1 | **无** | grey `Scenarios` bands fan from ~118-212 in Jan, text calls it "a statistical risk range" |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest y tick printed is `100`, no break glyph on the axis |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | legend shows three grey shades separated by commas for one label `Scenarios`, shade = range level |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | legend row `Scenarios \| Budget \| Prior Year \| Forecast` sits between the title and the plot |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f1 | **无** | two-column body text runs above/around the chart, ending "(see below)" and describing the chart |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | only scale word on the figure is `$m` at the axis head; ticks are bare 100...220 |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | `$m` set above the top tick `220`, not alongside the axis |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | first x tick reads `Jan` with a bare `14` stacked beneath it |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint dotted horizontal rules at 120,140,...,220; no vertical grid across the panel |

词表 65 项，本页出现 11 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `multi_swatch_single_legend_entry` | f1 | legend reads three grey squares joined by commas then one label `Scenarios` | 一个图例条目对应三层不同灰度的带，读值时无法从图例区分内、中、外带各自的数值范围。 |
| `nested_range_bands` | f1 | three concentric grey bands fan out from a single Jan point, widening toward May | 同一月份存在三对上下边界值，取值必须先指明是哪一层情景带的上界或下界。 |
| `series_ends_before_axis_end` | f1 | `Forecast` line and grey bands stop at May, dashed vertical rule at May; axis continues to Dec | Jun–Dec 各月对 Forecast 与 Scenarios 无数据点，表格中这些格位应为空而非0。 |
| `constant_series_across_all_categories` | f1 | `Budget` ~218 and `Prior Year` ~166 are perfectly flat across Jan 14 to Dec | 同一数值在12个月份重复出现，行标签只靠月份无法唯一定位某个读数。 |

## 5 · 难在哪

卡在 **第一步 · 要有表**。

图上没有任何数字标注，也没有 Source/Note 行或数据表，解析器输出里根本不会出现 218、216、200 这些串——图形整体被跳过。相比之下读值本身不算最难：网格线每20 $m一条，5%容差在218处约±10.9 $m，等于半格，肉眼把 Forecast 的Feb读成216或218都在容差内。标签层也有麻烦但可解：Budget≈218与Prior Year≈166在Jan 14至Dec十二个月份完全水平，同一数值重复12次，行键必须靠系列名而非月份区分；而Jun–Dec对Forecast与Scenarios无数据，表格需留空。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | 新组件 nested_range_bands（多层灰阶情景带）与 multi_swatch_single_legend_entry | 条件行新增“带状区间系列”，样式字段增加 band_levels 与 legend_swatch_group | “单图例条目对应多层嵌套带”对 vs 关：考察每层带上下界能否被唯一寻址 |
| P1 | 一类出版方 | 新组件 series_ends_before_axis_end（系列在轴中途终止，配虚线分隔） | 记录字段允许某系列在部分类别上为 null，并可在断点画竖向 reference_line | “部分类别缺值 + 分界竖线”行：检验缺值是否被写成空格而非0 |
| P7 | 通用 | heading 拆分字段：无编号标题 + 轴头单位 `$m`（axis_title_above_axis） | 标题记录字段拆为 number/title/subtitle/unit 与 unit_placement=above_axis | “单位只出现在轴顶”行：无编号图的标题与单位是否随表格一起导出 |
| P6 | 一类出版方 | constant_series_across_all_categories（水平常量系列） | 数据生成器条件行加入常量参考系列（Budget/Prior Year 型） | “常量系列跨12类别重复同值”行：评测重复值的寻址键需求 |
