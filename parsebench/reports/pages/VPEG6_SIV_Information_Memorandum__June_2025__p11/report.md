# VPEG6_SIV_Information_Memorandum__June_2025__p11

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| VPEG6_SIV_Information_Memorandum__June_2025_ | `need_estimate` | 5 | 5 |

该页展示一张未编号的柱状图：四个分位数(Quartile 1–4)的全球直投私募基金TVPI柱子，加一条代表Vantage 2.1x的青色横向参考线，右上角有黑底白字说明框。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 2.1 | `VANTAGE` · `Quartile 1` | 1% | f1 | the teal VANTAGE horizontal reference line (its value stated in the black callout) | 是 | `VANTAGE` · `Vantage vs Global Private Equity (Direct Buyout Funds) TVPI - 2009-2018` |
| 2 | 2.5 | `GLOBAL PRIVATE EQUITY` · `Quartile 1` | 1% | f1 | the Quartile 1 GLOBAL PRIVATE EQUITY bar, top at the 2.5x gridline | 否 | `GLOBAL PRIVATE EQUITY` · `Quartile 1` |
| 3 | 1.7 | `GLOBAL PRIVATE EQUITY` · `Quartile 2` | 5% | f1 | the Quartile 2 GLOBAL PRIVATE EQUITY bar, top between 1.5x and 2.0x | 否 | `GLOBAL PRIVATE EQUITY` · `Quartile 2` |
| 4 | 1.4 | `GLOBAL PRIVATE EQUITY` · `Quartile 3` | 5% | f1 | the Quartile 3 GLOBAL PRIVATE EQUITY bar, top just below 1.5x | 否 | `GLOBAL PRIVATE EQUITY` · `Quartile 3` |
| 5 | 1.0 | `GLOBAL PRIVATE EQUITY` · `Quartile 4` | 1% | f1 | the Quartile 4 GLOBAL PRIVATE EQUITY bar, top at about the 1.0x gridline | 否 | `GLOBAL PRIVATE EQUITY` · `Quartile 4` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 5 predicted key sets miss a rule label: 2.1

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 4 | 5 | 无 | 0.5x, 1.0x, 1.5x, 2.0x, 2.5x, 3.0x |

- **f1** Vantage has Generated Top Quartile Returns when Compared to Global Direct Private Equity Funds / Vantage vs Global Private Equity (Direct Buyout Funds) TVPI - 2009-2018　[图上方]　单位 `TVPI`
  - 来源行：Source: Based on global private equity returns on a Total Value Paid In basis from 2009-2018, Persistence in Alternative Strategies:  Private Equity Buyout, Preqin. Vantage TVPI based on VPEG2 and VPEG3 TVPI as at 31 March 2025.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | four grey vertical bars plus a full-width teal line with a round icon marker in one panel |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | teal horizontal rule spanning the plot just above the 2.0x gridline, legend entry "VANTAGE" |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | black box over the plot's top right: "Vantage has generated a 2.1x platform wide Net Multiple ... Direct Buyout" |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | two lines of small print under the plot beginning "Source: Based on global private equity returns..." |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f1 | 有 | "VANTAGE" and "GLOBAL PRIVATE EQUITY" stacked in a column at the left, level with the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | heading line reads "...(Direct Buyout Funds) TVPI - 2009-2018"; axis shows bare multiples "0.5x"–"3.0x" |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | thin horizontal rules at 0.5x through 3.0x across the panel; no vertical rules |

词表 65 项，本页出现 7 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `logo_marker_on_reference_line` | f1 | circular Vantage brand icon badge sits on the teal line above Quartile 1 and serves as the legend swatch | 该系列的值只能从横线高度读取，图标遮挡了线与2.0x刻度的关系，容易把2.1x误读成2.0x。 |
| `unlabeled_zero_baseline` | f1 | lowest printed tick is "0.5x"; bars rest on an unlabeled baseline well below it | 零点无刻度标签，读柱高时须自行外推半个刻度间距，绝对值容易系统性偏低或偏高。 |
| `value_only_in_callout_text` | f1 | the only number on the figure, "2.1x", appears inside the black note box, not as a data label | 表格若只抄柱子，2.1x会丢失；解析器须把标注框文字当作该系列的唯一数值来源。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

五个待核值里有四个完全没有印在图上，唯一印出的是标注框里的"2.1x"。刻度间距为0.5x，而5%容差在1.0x上只有±0.05，即刻度间距的十分之一；1.7x与1.4x都落在两条网格线之间，必须按像素内插，且最低标签是0.5x、零基线无标签，外推误差直接叠加。相比之下标签只需"GLOBAL PRIVATE EQUITY"+"Quartile n"两键即可唯一定位，并不构成瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | reference_line 作为独立图例系列（横贯全图、带品牌图标标记），其数值只出现在 annotation_callout 文本中 | 条件行增加"bars + 一条带图例的水平参考线"，样式字段增加 reference_line 的标记/标签方式，记录字段允许该系列值来自标注文本 | 有/无"数值仅存在于标注框的参考线系列"两组对比，看导出表是否仍能给出该系列的行 |
| P6 | 一类出版方 | 刻度后缀单位（0.5x…3.0x）与零基线不标注的组合，即 unlabeled_zero_baseline | 样式字段的 tick format（数字+后缀）与 axis 最低刻度是否打印零 | 零刻度打印 vs 省略零刻度两行，量化 5% 容差下的读数偏移 |
| P3 | 一类出版方 | legend_beside_plot（图例作为左侧竖列，圆形色块+图标） | 布局条件行的 legend 位置枚举增加 beside(left) | legend 在下方/上方/左侧三行，看系列名能否被正确绑定到表头 |
| P1 | 通用 | 整图零数据标签（values_printed = none）时的可达精度评估 | 评测中把 readable 从布尔门改为每个 mark 的可达精度，参考本图0.5x刻度 | 全部标注数值 / 仅标注框有一个数值 / 完全无数值三行 |
| P7 | 这份文档自己的习惯 | 图上方两级标题（青色小标题 + 黑色粗体图注）作为 heading 的 title/subtitle 拆分 | P7 的 heading 记录字段：number、title、subtitle、unit、placement | 单行标题 vs 彩色引导句+粗体图注两行，检验表格上方标题归属 |
