# 2023-05-sigma-01-english_p6

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2023-05-sigma-01-english | `need_estimate` | 10 | 10 |

这是Swiss Re Institute sigma 1/2023第6页，正文讨论2022年对流风暴、洪水、冬季风暴与干旱损失，中部为Figure 2——左侧为按灾种堆叠的水平条形（USD十亿），右侧为2022年损失高于各期平均值的百分比条形。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 115% | `30-year average (1992–2021)` · `2022 insured loss over previous year averages` | 1% | f1 | the purple bar on the 30-year average (1992−2021) row | 是 | `30-year average (1992−2021)` · `2022 insured loss over previous year averages` |
| 2 | 62% | `15-year average (2007–2021)` · `2022 insured loss over previous year averages` | 1% | f1 | the purple bar on the 15-year average (2007−2021) row | 是 | `15-year average (2007−2021)` · `2022 insured loss over previous year averages` |
| 3 | 54% | `10-year average (2012–2021)` · `2022 insured loss over previous year averages` | 1% | f1 | the purple bar on the 10-year average (2012−2021) row | 是 | `10-year average (2012−2021)` · `2022 insured loss over previous year averages` |
| 4 | 14% | `5-year average (2017–2021)` · `2022 insured loss over previous year averages` | 1% | f1 | the purple bar on the 5-year average (2017−2021) row | 是 | `5-year average (2017−2021)` · `2022 insured loss over previous year averages` |
| 5 | 61 | `2022` · `Tropical cyclones` | 10% | f1 | the long green Tropical cyclones segment in the 2022 row | 否 | `2022` · `Tropical cyclones` |
| 6 | 33 | `2022` · `Severe convective storms` | 10% | f1 | the blue Severe convective storms segment in the 2022 row (body text says 'At over USD 33 billion') | 否 | `2022` · `Severe convective storms` |
| 7 | 15 | `2022` · `Other secondary perils` | 20% | f1 | most likely the light-green Floods segment in the 2022 row, read as the gap between two segment edges | 否 | `2022` · `Floods` |
| 8 | 45 | `5-year average (2017–2021)` · `Tropical cyclones` | 10% | f1 | most likely the green Tropical cyclones segment in the 5-year average (2017−2021) row | 否 | `5-year average (2017−2021)` · `Tropical cyclones` |
| 9 | 13 | `10-year average (2012–2021)` · `Floods` | 20% | f1 | most likely the blue Severe convective storms segment in the 30-year average (1992−2021) row | 否 | `30-year average (1992−2021)` · `Severe convective storms` |
| 10 | 6 | `2022` · `Droughts` | 20% | f1 | most likely the dark-teal Earthquakes segment at the left end of the 30-year average (1992−2021) row | 否 | `30-year average (1992−2021)` · `Earthquakes` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 15, 13, 6
- 面板数与面板名个数不一致——f1: panels=2, 0 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | horizontal | 2 | 9 | 5 | 42 | 部分 | 0, 20, 40, 60, 80, 100, 120, 140 |

- **f1** Figure 2 / Global insured losses from natural catastrophes in 2022 by category, in USD billion at 2022 prices　[图上方]　单位 `in USD billion at 2022 prices`
  - 来源行：Source: Swiss Re Institute

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each row is one bar built of coloured peril segments whose total length is the loss |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | category labels '30-year average (1992−2021)' ... '2022' sit on the y axis, bars grow right |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | the purple bars on the right have no ticks or baseline numbers, only 115%, 62%, 54%, 14% |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one legend block below covers both the USD-billion stacks and '2022 insured loss over previous year averages' |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | row labels drawn once at the left serve both the stacked panel and the purple percentage panel |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: Swiss Re Institute' in small print below the legend |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two legend rows 'Earthquakes ... Droughts' printed under the axis tick row |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | left panel multi-segment USD stacks; right panel single percentage bars with printed labels, no axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | heading ends 'in USD billion at 2022 prices'; axis itself reads bare 0, 20 ... 140 |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '115%', '62%', '54%', '14%' printed to the right of each purple bar |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole figure block, plot area included, sits on a pale blue tint |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | vertical rules at 0, 20, 40 ... 140 cross the rows; no horizontal grid lines |

词表 65 项，本页出现 12 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `companion_panel_different_unit` | f1 | right panel bars are percentages ('115%') beside left panel USD billion stacks, one shared legend | 同一图号下两套单位：读数前必须先判定某个数字属于USD十亿面板还是百分比面板，否则115与115%会混淆。 |
| `panel_covers_subset_of_categories` | f1 | the '2022' row has no purple bar; only the four average rows carry percentages | 行标签在两面板间不是一一对应，表格若按行罗列会在2022行留空，需说明该空缺是设计而非缺数。 |
| `period_range_in_category_label` | f1 | row labels carry parenthetical ranges with an en dash: '30-year average (1992−2021)' | 定位115%等值必须逐字复制含破折号的括号区间，字符替换会导致标签匹配失败。 |
| `mixed_period_and_average_categories` | f1 | axis mixes multi-year averages with a single year: '5-year average (2017−2021)' and '2022' | 同一坐标轴上平均值与单年值并列，读某段长度时须先分清它是年度值还是均值。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

轴刻度只有0, 20, 40 ... 140，20个单位约合68像素，即1像素≈0.3 USD十亿。除四个百分比外全部数值都不印在图上，且堆叠段必须靠两条边界之差读出：6要求±0.3、13要求±0.65，也就是1–2像素的边界判定精度，而彩色段之间几乎没有分隔线；15与13这类窄段（约20–45像素宽）在双边界误差叠加后极易超出5%容差。相比之下标签只需“行名+灾种名”两个键，行名与图例都逐字印在页面上，反而不是瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | 新组件 companion_panel_different_unit（配套面板换单位） | 条件行中增加“同一图号内第二面板使用不同单位/无轴”的开关，并在记录字段里为每个面板单列 unit 与 panel_key | 单面板单单位 vs 复合面板双单位（USD十亿 + %）下的取值命中率对比 |
| P7 | 通用 | heading 五段拆分：figure_number=‘Figure 2’、标题行内嵌 unit_text=‘in USD billion at 2022 prices’ | 样式字段 heading.placement=above 与 unit 位置（并入标题行而非独立副标题） | 单位在独立副标题 vs 单位并入标题末尾时，导出表格能否恢复标度 |
| P6 | 一类出版方 | no_value_axis 配 value_label_outside（右侧百分比条只有外置标签） | 样式维度中的“值标签位置/是否绘制值轴”组合 | 有轴无标签 vs 无轴仅外置标签两种面板的读数正确率 |
| P2 | 一类出版方 | 新组件 panel_covers_subset_of_categories（副面板行数少于主面板） | 记录字段允许某面板在部分类别上无标记，并在导出表中标注空缺 | 面板类别完全对齐 vs 副面板缺一行时的行对位错误率 |
