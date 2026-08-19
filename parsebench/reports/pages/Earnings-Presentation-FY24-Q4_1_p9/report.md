# Earnings-Presentation-FY24-Q4_1_p9

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Earnings-Presentation-FY24-Q4_1 | `untagged` | 10 | 0 |

沃尔玛季度业绩演示第9页，左侧为员工照片，右侧标题「Returns to shareholders」下为一张按季度堆叠柱状图（股息与股票回购），图下有合计行，右侧配两条要点文字。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | $1.2 | `Share repurchases` · `Q4 FY23` | 1% | f1 | the Q4 FY23 Share repurchases (yellow) segment | 是 | `Q4 FY23` · `Share repurchases` |
| 2 | $1.5 | `Dividends` · `Q4 FY23` | 1% | f1 | the Q4 FY23 Dividends (blue) segment | 是 | `Q4 FY23` · `Dividends` |
| 3 | $2.7 | `Returns to shareholders (Total)` · `Q4 FY23` | 1% | f1 | the Q4 FY23 entry of the totals row under the axis | 是 | `Returns to shareholders` · `Q4 FY23` |
| 4 | $0.7 | `Share repurchases` · `Q1 FY24` | 1% | f1 | the Q1 FY24 Share repurchases (yellow) segment | 是 | `Q1 FY24` · `Share repurchases` |
| 5 | $1.5 | `Dividends` · `Q2 FY24` | 1% | f1 | the Q1 FY24 Dividends (blue) segment | 是 | `Q1 FY24` · `Dividends` |
| 6 | $0.5 | `Share repurchases` · `Q2 FY24` | 1% | f1 | the Q2 FY24 Share repurchases (yellow) segment | 是 | `Q2 FY24` · `Share repurchases` |
| 7 | $0.1 | `Share repurchases` · `Q3 FY24` | 1% | f1 | the Q3 FY24 Share repurchases segment, label printed above the thin segment | 是 | `Q3 FY24` · `Share repurchases` |
| 8 | $1.6 | `Returns to shareholders (Total)` · `Q3 FY24` | 1% | f1 | the Q3 FY24 entry of the totals row under the axis | 是 | `Returns to shareholders` · `Q3 FY24` |
| 9 | $1.5 | `Share repurchases` · `Q4 FY24` | 1% | f1 | the Q4 FY24 Share repurchases (yellow) segment, or the Q4 FY24 Dividends segment - both read $1.5 | 是 | `Q4 FY24` · `Share repurchases` |
| 10 | $3.0 | `Returns to shareholders (Total)` · `Q4 FY24` | 1% | f1 | the Q4 FY24 entry of the totals row under the axis | 是 | `Returns to shareholders` · `Q4 FY24` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: $1.5

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 2 | 5 | 10 | 全部 | （不画值轴） |

- **f1** Returns to shareholders / Through dividends and share repurchases　[图上方]　单位 `Amounts in billions, except as noted.  Dollar changes may not recalculate due to rounding.`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each quarter's bar has a blue Dividends segment below a yellow Share repurchases segment |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only a horizontal baseline under the bars; no ticks or gridlines on the value axis |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | "Dividends" and "Share repurchases" swatches sit in a row under the category axis |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f1 | **无** | bullets "Share repurchases during the quarter totaled $1,497 million" in a column right of the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | "Amounts in billions, except as noted." line under the title fixes the scale |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | "$1.5" printed inside each blue segment, "$1.2", "$0.7", "$0.5" inside yellow segments |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | "$0.1" sits above the thin Q3 FY24 yellow segment, outside the mark |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | category ticks read "Q4 FY23", "Q1 FY24" instead of ISO dates |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | the Q3 FY24 yellow segment is very thin so its "$0.1" label moved above it |
| `total_row_below_axis` | 轴下方一行合计值，与类目对齐 | f1 | **无** | row labelled "Returns to shareholders" with $2.7, $2.2, $2.0, $1.6, $3.0 under the axis |

词表 65 项，本页出现 10 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `row_label_in_tinted_box` | f1 | the "Returns to shareholders" total-row label sits in a light grey filled box left of the values | 合计行的行名在灰底方框内且与图标题同名，解析时容易被当作标题或漏掉，导致$2.7等合计值无行名可寻址。 |
| `total_row_duplicates_title_text` | f1 | the totals row label "Returns to shareholders" repeats the slide title verbatim | 同一字符串既是页标题又是行标签，检索合计值时无法区分上下文，需要额外的季度列名共同定位。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部印在图上（$1.5、$1.2、$0.1等），且没有值轴，所以读数不成问题；难点在寻址：Dividends 在五个季度里都是 $1.5，Q4 FY24 的两个分段又同为 $1.5，单靠数值无法区分，必须同时带上季度列名与系列名两把钥匙；此外 $2.7/$1.6/$3.0 属于轴下合计行，其行标签「Returns to shareholders」与页标题字面完全相同，解析器若把该行并入柱体表格或丢掉灰底行名，这三个值就没有唯一可用的行名。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P3 | 一类出版方 | total_row_below_axis（轴下合计行）作为独立的记录字段与样式维度 | 图表记录结构中新增 totals_row 字段（行名+每类别值），并在导出markdown时作为表格最后一行输出 | 有/无轴下合计行时，合计值（$2.7、$1.6、$3.0）被正确寻址的召回率对比 |
| P6 | 通用 | thin_segment_label（细分段标签外移）与 value_label_inside/outside 混用 | 样式字段中的 value-label placement 改为按分段高度自适应：低于阈值时移到分段外 | 标签一律置内 vs 细分段自动外移时，$0.1 这类小值的读取正确率对比 |
| P1 | 一类出版方 | no_value_axis（无值轴，仅基线）作为可控条件 | 条件行中增加「无刻度值轴+全部数值标注」这一组合 | 有刻度轴 vs 仅基线+全标注两种条件下的取值精度对比 |
| P7 | 通用 | 标题四段拆分（title / subtitle / unit_text «Amounts in billions, except as noted.»） | 标题记录字段拆为 number、title、subtitle、unit、placement 五项 | 单一标题串 vs 拆分标题时，单位「in billions」能否被关联到 $1.5 等数值 |
| P3 | 一类出版方 | side_text_bullets（图右侧要点文字栏） | 页面版式条件中新增「图与正文共享一条水平带」的布局行 | 有/无侧栏文字时，图内数值与正文数值（$1,497 million）是否被混淆的错配率 |
