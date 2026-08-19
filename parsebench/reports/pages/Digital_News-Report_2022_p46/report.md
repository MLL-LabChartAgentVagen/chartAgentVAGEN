# Digital_News-Report_2022_p46

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Digital_News-Report_2022 | `untagged` | 4 | 0 |

这是《Digital News Report 2022》第46页，左侧为2.4节正文，右侧一张无编号的横向条形图，展示42个市场上周通过邮件获取新闻的比例，并用橙色虚线标出17%的平均值。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 24 | `Austria` · `Percentage` | 1% | f1 | the Austria bar, the longest bar at the top | 是 | `PROPORTION WHO ACCESSED NEWS VIA EMAIL IN THE LAST WEEK – SELECTED MARKETS` · `Austria` |
| 2 | 22 | `USA` · `Percentage` | 1% | f1 | the USA bar (orange highlighted); Portugal directly below also reads 22 | 是 | `PROPORTION WHO ACCESSED NEWS VIA EMAIL IN THE LAST WEEK – SELECTED MARKETS` · `USA` |
| 3 | 11 | `Norway` · `Percentage` | 1% | f1 | the Croatia bar; Finland and Norway also read 11 | 是 | `PROPORTION WHO ACCESSED NEWS VIA EMAIL IN THE LAST WEEK – SELECTED MARKETS` · `Croatia` |
| 4 | 9 | `UK` · `Percentage` | 1% | f1 | the UK bar, the shortest bar at the bottom | 是 | `PROPORTION WHO ACCESSED NEWS VIA EMAIL IN THE LAST WEEK – SELECTED MARKETS` · `UK` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 4 predicted key sets miss a rule label: 24, 22, 11, 9
- 规则需要的键比模型报出的图能提供的多——rules need 2 keys, the richest figure offers 1

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | horizontal | 1 | 1 | 42 | 42 | 全部 | 0%, 25% |

- **f1** PROPORTION WHO ACCESSED NEWS VIA EMAIL IN THE LAST WEEK – SELECTED MARKETS　[图上方]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | orange dotted vertical rule crossing all bars at the 17% position, tick at top and bottom |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names down the left axis, bars grow rightwards from a 0% baseline |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | dotted orange box in plot area: "17% Average shown across all 42 markets" |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | small print below plot: "Q10. Thinking about how you got news online ... Base: Total sample in each market (n ≈ 2000)." |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | body prose column "In the last few years..." and "WEEKLY EMAIL CONSUMPTION" runs level with the chart |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | white numbers 24, 23, 22 ... 9 printed at the right end inside each bar |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 42 market names stacked down one axis, e.g. "Czech Republic", "Hong Kong", "South Korea" |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the USA bar is filled orange while all other 41 bars are teal |

词表 65 项，本页出现 8 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `endpoint_only_value_axis` | f1 | the value axis prints only "0%" and "25%" at the two ends, no intermediate ticks | 没有中间刻度时，未打印的数值只能靠两端插值，读数精度完全依赖条内标签。 |
| `percent_sign_on_tick_only` | f1 | axis ends read "0%" and "25%" while bar labels are bare numbers 24, 23, 22 | 单位只出现在刻度上，表格若只抄条内数字会丢掉百分号语义。 |
| `callout_annotates_reference_line` | f1 | the dotted box "17% Average shown across all 42 markets" sits on and explains the orange 17% rule | 17%这个值属于参考线而非任何条形，取值时须与42个国家行区分开。 |
| `unnumbered_figure_heading` | f1 | heading is all-caps two lines with no "Figure" or "Exhibit" number anywhere | 缺少编号意味着行标题只能靠标题文本定位，解析输出难以与正文交叉引用。 |
| `sorted_rank_order_rows` | f1 | bars run monotonically 24 down to 9 from Austria to UK, not alphabetical | 顺序本身承载排名信息，重复值（22、11）的行序需按图上顺序保留。 |

## 5 · 难在哪

卡在 **第一步 · 要有表**。

所有42个数值都以白字印在条内，读数不需要对轴插值（轴上只有0%和25%两个刻度，若靠像素读数，1个百分点约等于5%容差的边界），所以第2步不是瓶颈；单系列单面板，一个国家名即可唯一定位，重复值22（USA/Portugal）和11（Croatia/Finland/Norway）也只需国家名一列，第3步同样不难。真正的风险是这张图完全是位图且没有图号，解析器要么整块跳过，要么把42行国家名与数字挤成一段无结构文本，那么24、22、11、9连带国家标签都无从检索。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | reference_line 与 annotation_callout 的组合（虚线参考线自带文字框说明其数值与含义） | 图形样式条件行中新增“参考线+说明框”开关，记录里为参考线单独保存 value 与 label 字段 | 有/无“参考线数值单独成行”的表格导出对比，检验17%这类非条形数值是否被误当作某国数据 |
| P1 | 一类出版方 | endpoint_only_value_axis（仅两端刻度）与 percent_sign_on_tick_only | 轴刻度样式字段：tick 数量可降至2，并把单位符号只放在刻度而非标题 | 刻度密度（2刻度 vs 5刻度）× 是否打印条内数值，对可读精度的影响一行 |
| P5 | 一类出版方 | 42 类目的横向条形高密度排布（wrapped_category_labels 上限提高） | 生成条件中类目数上限，以及横向条形的画布高度自适应 | 类目数 12 / 25 / 42 三档下行标签召回率一行 |
| P7 | 这份文档自己的习惯 | unnumbered_figure_heading（图号为空、全大写两行标题） | 标题记录字段：figure_number 允许为空，title 支持换行且大写，placement=above | 有图号 vs 无图号时，标题作为粗体行随表导出的成功率一行 |
| P6 | 通用 | highlighted_category（单条橙色标出USA） | 样式字段中新增“单类目强调色”，并在记录中标记该类目为 highlighted | 强调色是否被误读成第二个系列的一行对比 |
