# 67c07d7f417ce_p17

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 67c07d7f417ce | `untagged` | 7 | 0 |

AXA 2024全年业绩演示第17页：一张无数值轴的两年堆叠柱图（GWP & Other Revenues，FY23对FY24，分三条业务线），右侧并列三列文字化百分比（Change / o/w pricing¹ / o/w volume²）以及一列要点文字。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 34.9 | `Commercial lines` · `FY24` | 1% | f1 | the FY24 Commercial lines segment of the stacked bar | 是 | `GWP & Other Revenues` · `FY24` · `Commercial lines` · `In Euro billion` |
| 2 | +6% | `Commercial lines` · `Change` | 1% | f1 | the Commercial lines row in the Change column | 是 | `Change` · `Commercial lines` |
| 3 | +3% | `Commercial lines` · `o/w pricing¹` | 1% | f1 | the Commercial lines row in o/w pricing¹ (the identical +3% also stands in o/w volume² on the same row) | 是 | `o/w pricing¹` · `Commercial lines` |
| 4 | 2.5 | `AXA XL Reinsurance` · `FY24` | 1% | f1 | the FY24 AXA XL Reinsurance segment, a thin band mid-bar | 是 | `GWP & Other Revenues` · `FY24` · `AXA XL Reinsurance` · `In Euro billion` |
| 5 | +10% | `AXA XL Reinsurance` · `Change` | 1% | f1 | the AXA XL Reinsurance row in the Change column (a second +10% sits in o/w pricing¹ on the Retail lines row) | 是 | `Change` · `AXA XL Reinsurance` |
| 6 | 19.1 | `Retail lines` · `FY24` | 1% | f1 | the FY24 Retail lines segment | 是 | `GWP & Other Revenues` · `FY24` · `Retail lines` · `In Euro billion` |
| 7 | -3% | `Retail lines` · `o/w volume` | 1% | f1 | the Retail lines row in the o/w volume² column | 是 | `o/w volume²` · `Retail lines` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 3 | 2 | 6 | 部分 | （不画值轴） |

- **f1** GWP & Other Revenues　[图上方]　单位 `In Euro billion`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | FY23 and FY24 bars each split into Commercial lines, AXA XL Reinsurance, Retail lines segments |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | '+7%' on a bracket with an arrow drawn from FY23 top to FY24 top |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or axis line beside the bars; only FY23/FY24 labels under them |
| `source_note_lines` | source / note 行在图下方 | page | 有 | 'Change at constant scope and FX.' / '1. Price effect. 2. Includes exposure adjustments and mix & other effects.' |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f1 | 有 | 'Commercial lines', 'AXA XL Reinsurance', 'Retail lines' set as a left column level with their segments |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f1 | **无** | right-hand column of ► bullets ('Continued favorable pricing and higher volumes…') level with the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | 'In Euro billion' under the page title fixes 53.0 / 56.5 / 34.9 scale |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | column headings 'o/w pricing¹' and 'o/w volume²' with superscript digits |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | '34.9', '2.5', '19.1' printed on the FY24 segments |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '53.0' and bold '56.5' printed above the FY23 and FY24 bar tops |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | FY24 bar drawn in saturated mid/navy blue while the FY23 bar is pale blue |

词表 65 项，本页出现 11 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `value_columns_aligned_to_stack_segments` | f1 | 'Change', 'o/w pricing¹', 'o/w volume²' columns print percentages on rows aligned with each stacked segment | 这些百分比不是图形标记，而是与堆叠段行对齐的文字列；要定位一个数值必须同时给出段名（行）和列名，否则+3%、+10%会重复无法区分。 |
| `negative_value_in_text_column` | f1 | '-3%' printed in the o/w volume² column for the Retail lines row, no axis or zero line | 负值只以文字出现，没有零线或轴可参照，解析时容易丢掉负号或与相邻的+10%串行。 |
| `bold_column_emphasis` | f1 | '+6%', '+10%', '+7%' in the Change column are bold; pricing/volume columns are light grey | 字重区分主列与分解列，是唯一提示'Change'列为汇总量的线索，纯文本导出后该层级消失。 |
| `tinted_column_panel` | f1 | a light grey rounded rectangle sits behind the whole 'Change' column of percentages | 底色把Change列圈成一个视觉块，读数时要靠它判断某个百分比属于Change而非旁边两列。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部印出（34.9、2.5、19.1、53.0、56.5和五个百分比），第2步几乎无风险——图上根本没有刻度轴，无需按像素读数。真正卡住的是寻址：+3%在Commercial lines行的o/w pricing¹和o/w volume²两列各出现一次，+10%同时是AXA XL Reinsurance的Change和Retail lines的o/w pricing¹，因此每个百分比至少需要'行=业务线'加'列=Change / o/w pricing¹ / o/w volume²'两把钥匙；而这三列只是与堆叠段对齐的文字，解析器很可能把它们并入柱图或拆成互不相连的碎片，列名还带上标¹²容易丢失。此外柱内数值需要第三把钥匙FY23/FY24才能与百分比区分。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | 新增 value_columns_aligned_to_stack_segments（图旁与堆叠段对齐的数值列） | 图形样式条件行：在stacked_bar族上增加'附带右侧对齐数值列'的开关，并在记录字段中为每列生成column_key | 有/无对齐数值列（列名参与寻址键）两组对比，检验重复百分比是否仍能唯一定位 |
| P6 | 一类出版方 | no_value_axis 配合 value_label_inside / value_label_outside 的组合 | 样式字段：数值标签位置（段内/柱顶外）与是否绘制数值轴解耦 | 无轴且仅部分段带标签（FY23各段无标签）时的可读性行 |
| P7 | 通用 | footnote_marker（列标题上标¹²）与 unit_in_axis_or_title（'In Euro billion'在页副标题） | 标题/表头字段：允许上标标记进入列名，单位与标题分列存放 | 单位与标题分离、且列名含上标时的表头还原行 |
| P6 | 一类出版方 | negative_value_in_text_column（无零线的负值） | 数值格式字段：允许带符号百分比作为纯文字单元，无零线参照 | 负号保留率一行（有零线的柱 vs 纯文字负值） |
| P3 | 这份文档自己的习惯 | side_text_bullets + annotation_callout（'+7%'跨柱箭头） | 页面版式行：图与右侧要点文字共占一条横带；柱顶间增加带箭头的比较标注 | 整页markdown导出时，图旁要点文字是否污染表格行的对比行 |
