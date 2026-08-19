# pdf_d2e0103f64cd_p29

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| pdf_d2e0103f64cd | `3d_chart` | 10 | 0 |

该页为新加坡CBD办公楼市场章节，含两张无编号折线图：上方为2010至2013年第三季度的平均出租率（%），下方为平均租金（S$每平方英尺每月），均含三条区域序列、图例在图下方及来源说明。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 70.3 | `Marina Bay` · `2010` · `Average Occupancy Rates` | 1% | f1 | the 2010 point of the Marina Bay line, labelled '70.3%' below the point | 是 | `Average Occupancy Rates in the Singapore CBD (%)` · `Marina Bay` · `2010` |
| 2 | 96.8 | `Raffles Place` · `2010` · `Average Occupancy Rates` | 1% | f1 | the 2010 point of the Raffles Place line, labelled '96.8%' | 是 | `Average Occupancy Rates in the Singapore CBD (%)` · `Raffles Place` · `2010` |
| 3 | 91.2 | `Shenton Way/Robinson Rd/Cecil Street` · `2012` · `Average Occupancy Rates` | 1% | f1 | the 2012 point of the Raffles Place line region, labelled '91.2%' near the 2012 slot | 是 | `Average Occupancy Rates in the Singapore CBD (%)` · `Shenton Way/Robinson Rd/Cecil Street` · `2012` |
| 4 | 84.1 | `Marina Bay` · `Q3 2013` · `Average Occupancy Rates` | 1% | f1 | the Q3 2013 point of the Marina Bay line, labelled '84.1%(1)' | 是 | `Average Occupancy Rates in the Singapore CBD (%)` · `Marina Bay` · `Q3 2013` |
| 5 | 97.7 | `Shenton Way/Robinson Rd/Cecil Street` · `Q3 2013` · `Average Occupancy Rates` | 1% | f1 | the Q3 2013 point of the Shenton Way/Robinson Rd/Cecil Street line, labelled '97.7%' | 是 | `Average Occupancy Rates in the Singapore CBD (%)` · `Shenton Way/Robinson Rd/Cecil Street` · `Q3 2013` |
| 6 | 12.0 | `Marina Bay` · `2011` · `Average Rental Rates` | 1% | f2 | the 2011 point of the Marina Bay line, labelled '12.0' | 是 | `Average Rental Rates in the Singapore CBD (S$ per sq ft per month)` · `Marina Bay` · `2011` |
| 7 | 9.0 | `Raffles Place` · `2010` · `Average Rental Rates` | 1% | f2 | the 2010 point of the Raffles Place line, labelled '9.0' | 是 | `Average Rental Rates in the Singapore CBD (S$ per sq ft per month)` · `Raffles Place` · `2010` |
| 8 | 7.8 | `Shenton Way/ Robinson Rd/ Cecil Street` · `2011` · `Average Rental Rates` | 1% | f2 | the 2011 point of the Shenton Way/ Robinson Rd/ Cecil Street line, labelled '7.8' | 是 | `Average Rental Rates in the Singapore CBD (S$ per sq ft per month)` · `Shenton Way/ Robinson Rd/ Cecil Street` · `2011` |
| 9 | 11.0 | `Marina Bay` · `Q3 2013` · `Average Rental Rates` | 1% | f2 | the Q3 2013 point of the Marina Bay line, labelled '11.0' | 是 | `Average Rental Rates in the Singapore CBD (S$ per sq ft per month)` · `Marina Bay` · `Q3 2013` |
| 10 | 9.4 | `Raffles Place` · `Q3 2013` · `Average Rental Rates` | 1% | f2 | the Q3 2013 point of the Raffles Place line, labelled '9.4' | 是 | `Average Rental Rates in the Singapore CBD (S$ per sq ft per month)` · `Raffles Place` · `Q3 2013` |

**程序核对**（模型没有看到左半的标签列）：

- 规则需要的键比模型报出的图能提供的多——rules need 3 keys, the richest figure offers 2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 3 | 6 | 18 | 全部 | 65%, 70%, 75%, 80%, 85%, 90%, 95%, 100% |
| f2 | `line` | vertical | 1 | 3 | 6 | 17 | 全部 | 0, 2, 4, 6, 8, 10, 12, 14 |

- **f1** Average Occupancy Rates in the Singapore CBD (%)　[图上方]　单位 `(%)`
  - 来源行：Source: Independent Market Research Report.
- **f2** Average Rental Rates in the Singapore CBD (S$ per sq ft per month)　[图上方]　单位 `S$`
  - 来源行：Source: Independent Market Research Report.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest y tick is '65%', not zero, with no break glyph |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | Two separately titled graphs: 'Average Occupancy Rates...' and 'Average Rental Rates...', each with its own Source line |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note:' , '(1) Due to the completion of Asia Square Tower 2...' and 'Source: Independent Market Research Report.' below plot |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | 'Source: Independent Market Research Report.' in italics under the legend |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | Marina Bay / Raffles Place / Shenton Way/Robinson Rd/Cecil Street row sits under the category axis |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | legend row 'Marina Bay  Raffles Place  Shenton Way/ Robinson Rd/ Cecil Street' below the 2010–Q3 2013 axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | 'S$' set above the top tick 14 and '(S$ per sq ft per month)' in the title; ticks are bare numbers |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | '84.1%(1)' superscript on the label, keyed to 'Note: (1)' below the plot |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f2 | **无** | 'S$' printed above the '14' tick at the top of the value axis |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '96.8%', '70.3%', '84.1%' printed above or below the line vertices, off the line |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | '12.0', '9.8', '6.5' printed above or below their line points |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | x ticks mix years and quarters: '2010', '2011', '2012', 'Q1 2013', 'Q2 2013', 'Q3 2013' |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f2 | **无** | x ticks read '2010', '2011', '2012', 'Q1 2013', 'Q2 2013', 'Q3 2013' |

词表 65 项，本页出现 9 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `heading_rule_above_plot` | page | a full-width horizontal rule drawn between each title line and its plot area | 该横线是标题块与绘图区的分隔，解析时可能被当作表格边框，影响标题与图内数值的归属判断。 |
| `mixed_period_granularity_axis` | f1 | axis mixes annual points (2010–2012) with quarterly points (Q1–Q3 2013) at equal spacing | 同一横轴上年度与季度点等距排列，取值时必须用原样刻度标签定位，不能按时间比例推断。 |
| `note_marker_on_value_label` | f1 | '84.1%(1)' carries the footnote marker on the data label itself, not on a title | 数值字符串中带上标编号，检索该值时文本可能为'84.1%(1)'而非'84.1'，需容忍这种粘连。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

所有18+17个数值都以文字标签印在图上（如'96.8%'、'12.0'），因此读数不构成障碍（步骤2易过）；真正卡住的是定位：每个值需要三层键——图标题（两图均无编号，只能用'Average Occupancy Rates in the Singapore CBD (%)'与'Average Rental Rates...'区分）、序列名（两图的Shenton系列写法还不同：'Shenton Way/Robinson Rd/Cecil Street'与'Shenton Way/ Robinson Rd/ Cecil Street'）、以及混合粒度的横轴键（'2012'与'Q3 2013'）。上图2012年附近有'93.7%'、'91.2%'、'88.5%'三值紧邻且标签偏离各自线条，序列归属只能靠颜色判断；加上'84.1%(1)'带脚注上标，字符串匹配也易失配。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | footnote_marker 与新增的 note_marker_on_value_label（数值标签自带上标编号） | 记录字段中的数值标签渲染样式：允许在 value_label 后附加上标编号，并在图下生成对应 'Note: (1) ...' 行 | 数值标签带/不带脚注上标两种条件下的数值检索命中率对比 |
| P6 | 一类出版方 | unit_in_axis_or_title + axis_title_above_axis（'S$' 置于顶部刻度之上） | 样式字段 unit_position：新增 'above_top_tick' 取值，与 axis_side / in_title 并列 | 单位位于标题、轴旁、顶部刻度上方三种位置时单位可恢复率的对比行 |
| new | 一类出版方 | 新组件 mixed_period_granularity_axis（年度与季度刻度混排） | 类别轴生成条件：允许同一 category 序列混合 'YYYY' 与 'Qn YYYY' 标签 | 纯年度轴 vs 年度+季度混合轴条件下按列键定位数值的准确率 |
| P7 | 通用 | 无编号图的标题字段化（figure_number 为空，title 承担唯一标识） | 标题记录字段：number 可空，title/unit 独立成字段，并标注 placement=above 与标题下横线 | 同页两张无编号图时，仅凭标题文本区分数值归属的成功率 |
| P1 | 一类出版方 | axis_starts_above_zero（上图纵轴起于 65%） | 条件行中的 value axis 下界设定：折线图允许非零起点并记录该起点 | 轴起点为0 vs 非0时像素读数误差是否超过5%容差的分行统计 |
