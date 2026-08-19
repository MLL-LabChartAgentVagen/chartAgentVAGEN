# 2023-05-sigma-01-english_p27

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2023-05-sigma-01-english | `need_estimate` | 10 | 10 |

该页为 Swiss Re sigma 报告附录第27页，含两幅时间序列组合图：Figure 19「Number of catastrophic events, 1970–2022」与 Figure 20「Number of victims, 1970–2022」（对数刻度并带多个事件标注框）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 60 | `1970` · `Man-made disasters` | 10% | f1 | a Man-made disasters bar near 1971 read against the 50–100 gridlines | 否 | `Figure 19` · `Number of catastrophic events, 1970–2022` · `Man-made disasters` · `1970` |
| 2 | 115 | `1991` · `Natural catastrophes` | 10% | f1 | a Man-made disasters bar around 1988–1989 just above the 100 gridline | 否 | `Figure 19` · `Number of catastrophic events, 1970–2022` · `Man-made disasters` · `1988` |
| 3 | 255 | `2005` · `Man-made disasters` | 5% | not_found | the tallest bar (about 2005) reaches roughly 245, and no printed 255 appears anywhere on the page | 否 | — |
| 4 | 98 | `2022` · `Man-made disasters` | 10% | not_found | 98 appears only in body text '98 man-made disasters', not as a labelled mark on either figure | 否 | — |
| 5 | 187 | `2022` · `Natural catastrophes` | 10% | f1 | the Natural catastrophes line point at 2022, near 185 between the 150 and 200 gridlines | 否 | `Figure 19` · `Number of catastrophic events, 1970–2022` · `Natural catastrophes` · `2021` |
| 6 | 500 000 | `1970` · `Natural catastrophes` | 20% | f2 | the Natural catastrophes line peak around 1970 (Bangladesh Storm), between 100 000 and 1 000 000 | 否 | `Figure 20` · `Number of victims, 1970–2022` · `Natural catastrophes` · `1970` |
| 7 | 450000 | `1976` · `Natural catastrophes` | 20% | f2 | a Natural catastrophes peak in the 100 000–1 000 000 band, e.g. 1976 Tangshan Earthquake | 否 | `Figure 20` · `Number of victims, 1970–2022` · `Natural catastrophes` · `1976` |
| 8 | 300000 | `2004` · `Natural catastrophes` | 20% | f2 | a Natural catastrophes line point in the upper part of the 100 000 band, e.g. 2004 or 2010 peak | 否 | `Figure 20` · `Number of victims, 1970–2022` · `Natural catastrophes` · `2003` |
| 9 | 300 000 | `2010` · `Natural catastrophes` | 20% | f2 | same log-axis line peak as above, written with a space separator like the page's tick style | 否 | `Figure 20` · `Number of victims, 1970–2022` · `Natural catastrophes` · `2010: Haiti Earthquake` |
| 10 | 2 500 | `2022` · `Man-made disasters` | 20% | f2 | a Man-made disasters bar top just above the 1 000 tick (2022 victims, ~2500 per body text) | 否 | `Figure 20` · `Number of victims, 1970–2022` · `Man-made disasters` · `2021` |

**程序核对**（模型没有看到左半的标签列）：

- 有值没能落到任何一个图元上——2 of 10 values could not be put on a mark
- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 115, 300000

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 53 | 106 | 无 | 0, 50, 100, 150, 200, 250, 300 |
| f2 | `compound` | vertical | 1 | 2 | 53 | 106 | 无 | 10 000 000, 1 000 000, 100 000, 10 000, 1 000 |

- **f1** Figure 19 / Number of catastrophic events, 1970–2022　[图上方]　（标题里没有单位）
  - 来源行：Source: Swiss Re Institute
- **f2** Figure 20 / Number of victims, 1970–2022　[图上方]　（标题里没有单位）
  - 来源行：Note: Scale is logarithmic: the number of victims increases tenfold per band. Source: Swiss Re Institute

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | teal bars for 'Man-made disasters' with a blue line for 'Natural catastrophes' in one panel |
| `mixed_marks` | 同面板混合图元（bar + line） | f2 | 有 | teal bars plus blue line over same log axis panel |
| `log_axis` | 对数轴 | f2 | 有 | ticks 1 000, 10 000, 100 000, 1 000 000, 10 000 000 and note 'Scale is logarithmic' |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f2 | **无** | boxed leader-line notes e.g. '2008: Cyclone Nargis, Myanmar', '2015: Earthquake in Nepal' over plot |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f2 | **无** | lowest tick is '1 000' on the log axis, no zero |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | 'Figure 19' and 'Figure 20' each with own caption and source |
| `source_note_lines` | source / note 行在图下方 | page | 有 | 'Source: Swiss Re Institute' and 'Note: Scale is logarithmic: ... Source: Swiss Re Institute' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Man-made disasters' swatch and 'Natural catastrophes' line key row under the x axis |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | legend row below x axis above the note line |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | yearly bars but ticks every three years: 1970, 1973, 1976 ... 2021 |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f2 | 有 | ticks 1970, 1973, ... 2021 while bars are annual |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | whole figure block sits on a pale blue tinted panel |
| `panel_background` | 绘图区带底色，不是白底 | f2 | **无** | pale blue tinted background behind plot and legend |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 50,100,150,200,250,300; no vertical grid |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | horizontal rules at each decade band, no vertical lines |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 53 yearly bars plus 53 line points = about 106 marks |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f2 | **无** | 53 bars and 53 line points across 1970–2022 |

词表 65 项，本页出现 11 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `grouped_thousands_tick_labels` | f2 | ticks printed with space separators: '10 000 000', '1 000 000', '100 000' | 解析器可能把带空格的数字拆开或误读，导致刻度值与检索字符串不匹配。 |
| `note_and_source_same_line` | f2 | 'Note: Scale is logarithmic: ... per band. Source: Swiss Re Institute' printed as one line | 注释与来源合并在一行，提取时需从同一行内切分出单位/刻度说明与出处。 |
| `callout_boxes_outside_plot_top` | f2 | annotation boxes sit above the line, some overlapping the top axis area with pointer lines | 标注框占据绘图区上方，读峰值点时需沿引导线定位对应年份，易错配。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

最卡的是取值精度。Figure 19 网格线间距为50，53根柱子挤在约1000像素内，单柱宽不足10像素，要把115这类值读到5%（±5.75）几乎等于要求判读到1个网格的十分之一；Figure 20 更甚：对数轴一个色带跨十倍，500 000 与 450 000 在同一带内像素差不到2像素，300 000 与 450 000 的差距也远小于5%容差所需分辨力。加之两图完全没有数值标签（values_printed=none），刻度又只有3年一格（1970、1973…2021），连年份定位都要在两刻度间插值，因此即便解析器生成了表格，数值本身也难以落在容差内。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 一类出版方 | log_axis 与 axis_starts_above_zero 组合（对数轴最低刻度非零） | 条件行中的 value-axis 设置字段：新增 scale=log 及 tick 生成规则（1 000/10 000/…带空格千分位） | 对数轴 vs 线性轴下的逐点可达精度对比行 |
| P6 | 一类出版方 | annotation_callout（带引导线的事件标注框） | 样式字段新增 callout 层：文本框位置、指向年份的 leader line | 有/无标注框遮挡时峰值年份定位正确率行 |
| P4 | 通用 | mixed_marks（柱+线共用一个数值轴） | 图族权重向量中加入 bar+line compound 家族 | compound（柱线混合）家族生成频率行 |
| P3 | 这份文档自己的习惯 | new_components 中的 note_and_source_same_line | 记录字段：note 与 source 允许同一行输出并需切分 | 注释含刻度说明时单位/刻度还原正确率行 |
| P5 | 通用 | sparse_time_ticks（53点仅每3年一刻度）与 dense_marks_100plus | 密度参数：categories=53、tick 间隔=3 | 刻度稀疏度×类目密度的取值定位误差行 |
