# TSLA-Q3-2023-Update-3_p8

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| TSLA-Q3-2023-Update-3 | `need_estimate` | 9 | 9 |

这是特斯拉季度更新报告第8页「CORE TECHNOLOGY」，左侧为三段正文，右侧上下并列两幅无编号图：FSD Beta累计里程折线图和单车销货成本柱状图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 525 | `Sep-23` | 5% | f1 | the Sep-23 end point of the line, just above the 500 grid line | 否 | `Cumulative miles driven with FSD Beta (millions)` · `Sep-23` |
| 2 | 300 | `Jun-23` | 5% | f1 | a y-axis tick label '300'; no data point sits on it - the line crosses it between Jun-23 and Jul-23 | 是 | `Cumulative miles driven with FSD Beta (millions)` · `300` |
| 3 | 150 | `Mar-23` | 10% | f1 | the Apr-23 point, just above the 100 grid line on the steep segment | 否 | `Cumulative miles driven with FSD Beta (millions)` · `Apr-23` |
| 4 | 90 | `Dec-22` | 10% | f1 | the Dec-22/Jan-23 point, a little below the 100 grid line | 否 | `Cumulative miles driven with FSD Beta (millions)` · `Jan-23` |
| 5 | 0 | `Mar-21` | 1% | f1 | the baseline tick '0'; the Mar-21 start of the line sits on it | 是 | `Cumulative miles driven with FSD Beta (millions)` · `Mar-21` |
| 6 | 39550 | `Q4 2022` | 1% | f2 | the Q4 2022 blue bar, top just above the $39,500 grid line | 否 | `Cost of goods sold per vehicle` · `Q4 2022` |
| 7 | 38500 | `Q1 2023` | 1% | f2 | the Q1 2023 blue bar, top level with the $38,500 grid line | 否 | `Cost of goods sold per vehicle` · `Q1 2023` |
| 8 | 37900 | `Q2 2023` | 1% | f2 | the Q2 2023 blue bar, top just under the $38,000 grid line | 否 | `Cost of goods sold per vehicle` · `Q2 2023` |
| 9 | 37500 | `Q3 2023` | 1% | f2 | the Q3 2023 red bar, top at the $37,500 grid line (body text says '~$37,500') | 否 | `Cost of goods sold per vehicle` · `Q3 2023` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 9 predicted key sets miss a rule label: 300, 150, 90
- 有规则的标签对不上任何一张图的名字——4 of 9 rules match no figure's printed names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 1 | 31 | 31 | 无 | 0, 100, 200, 300, 400, 500, 600 |
| f2 | `bar` | vertical | 1 | 1 | 5 | 5 | 无 | $36,000, $36,500, $37,000, $37,500, $38,000, $38,500, $39,000, $39,500, $40,000 |

- **f1** Cumulative miles driven with FSD Beta (millions)　[图下方]　单位 `(millions)`
- **f2** Cost of goods sold per vehicle　[图下方]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f2 | **无** | lowest tick is '$36,000' with no break glyph; bars are truncated stubs |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two independent charts stacked in the right half, each with its own caption below it, neither numbered |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | left column runs 'Artificial Intelligence Software and Hardware', 'Vehicle and Other Software', 'Battery, Powertrain & Manufacturing' beside both charts |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | y axis shows bare 0-600; scale word only in caption '...FSD Beta (millions)' |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | month labels 'Mar-21' ... 'Sep-23' set at roughly 45 degrees under the axis |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | ticks written 'Mar-21', 'Dec-22', 'Sep-23' rather than ISO dates |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 0,100,...,600 across the plot; no vertical grid lines |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | horizontal rules at each $500 tick; no vertical grid lines behind the five bars |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f2 | **无** | the 'Q3 2023' bar is red while Q3 2022-Q2 2023 bars are blue |

词表 65 项，本页出现 8 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `currency_symbol_in_tick_labels` | f2 | value ticks printed '$36,000' ... '$40,000'; no unit text elsewhere on the figure | 数值的货币单位只存在于刻度文本里，解析器若丢掉$号或千分位逗号，38500 与 $38,500 就无法匹配。 |
| `caption_below_plot_as_only_title` | page | 'Cumulative miles driven with FSD Beta (millions)' and 'Cost of goods sold per vehicle' printed under each plot, centred | 图名在图下方且无编号，表格上下文只能靠下文一行文字定位，两图标题极易被归到相邻图的表格。 |
| `dense_monthly_category_axis` | f1 | 31 consecutive monthly ticks Mar-21 to Sep-23, every one labelled, line has no point markers | 没有点标记而刻度逐月排列，读某一月的值必须靠刻度对位，行名与数值的绑定风险很高。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

两图都完全没有数据标签（values_printed=none），全部数值必须靠像素对刻度读出。f1 刻度间距为100，而待读的 90 只允许 ±4.5 的误差，即刻度间距的 4.5%，且折线无点标记、31 个逐月刻度旋转排列，连「哪一点是 Jan-23」都要靠横向对位；150 同理落在 100 与 200 之间无辅助线处。相比之下 f2 的 5% 容差（约 ±1900）比整个轴跨度 $36,000–$40,000 的 4000 还接近一半，反而宽松。因此瓶颈是把折线点读到 5% 以内，而不是标签或表格结构。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | axis_starts_above_zero 与新提的 currency_symbol_in_tick_labels 组合（$ 前缀+千分位、最低刻度 $36,000） | 样式字段中的刻度格式与值轴起点（tick_format / axis_min）条件行 | 「值轴不从零开始且刻度带货币前缀」对比「零起点裸数字刻度」时的取值正确率 |
| P7 | 一类出版方 | heading placement=below、无编号、单位写在标题括号内（(millions)） | 记录的标题字段拆分：figure_number 为空、title、unit_text、placement=below | 标题位于图下方 vs 图上方时，表格能否被正确关联到该图名 |
| P3 | 一类出版方 | multi_figure_page 加 side_text_bullets（一页两图并配左侧正文栏） | 整页导出条件行：同页多图与旁侧文字栏的版式设置 | 整页 markdown 导出中，两个无编号图的标题各自落在对应表格上方的比例 |
| P1 | 通用 | dense_monthly_category_axis（31 个逐月旋转刻度、折线无点标记） | 类别轴密度与点标记开关的条件行（rotated_x_ticks + marker=none） | 类别数 ≥30 且无点标记时，单点读数落在 5% 容差内的比例 |
