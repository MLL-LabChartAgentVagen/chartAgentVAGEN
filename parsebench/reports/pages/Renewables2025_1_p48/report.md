# Renewables2025_1_p48

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Renewables2025_1 | `untagged` | 9 | 0 |

本页为IEA《Renewables 2025》第48页，正文讨论NDC 3.0提交情况，中间为一个无编号复合图：左侧饼图（含展开的堆叠条）显示2023年燃料燃烧CO₂排放被NDC 3.0覆盖的份额，右侧柱状图显示各阶段国家数量。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 77 | `Not submitted` | 1% | f1 | the 'Not submitted' pie slice (left panel) | 是 | `Not submitted` · `Shares of fuel-combustion CO2 emissions in 2023 covered in NDC 3.0s (left)` |
| 2 | 23 | `Submitted` | 1% | f1 | the 'Submitted' pie slice (left panel) | 是 | `Submitted` · `Shares of fuel-combustion CO2 emissions in 2023 covered in NDC 3.0s (left)` |
| 3 | 19 | `Advanced` | 1% | f1 | the 'Advanced' segment of the exploded stacked bar | 是 | `Advanced` · `Submitted` · `Shares of fuel-combustion CO2 emissions in 2023 covered in NDC 3.0s (left)` |
| 4 | 4 | `Emerging and developing` | 1% | f1 | the 'Emerging and developing' segment of the exploded stacked bar | 是 | `Emerging and developing` · `Submitted` · `Shares of fuel-combustion CO2 emissions in 2023 covered in NDC 3.0s (left)` |
| 5 | 196 | `Total Parties in Paris Agreement` · `Number of parties` | 1% | f1 | the 'Total Parties in Paris Agreement' bar, read against the axis (approx 195) | 否 | `Total Parties in Paris Agreement` · `Number of parties` |
| 6 | 57 | `Submitted NDC3.0s` · `Number of parties` | 1% | f1 | the 'Submitted NDC3.0s' bar, read against the axis | 否 | `Submitted NDC3.0s` · `Number of parties` |
| 7 | 54 | `Mentioned "renewable" energy` · `Number of parties` | 1% | f1 | the 'Mentioned "renewable" energy' bar, read against the axis | 否 | `Mentioned "renewable" energy` · `Number of parties` |
| 8 | 14 | `Acknowledged COP28 tripling target` · `Number of parties` | 1% | f1 | the 'Acknowledged COP28 tripling target' bar, read against the axis | 否 | `Acknowledged COP28 tripling target` · `Number of parties` |
| 9 | 5 | `Contained 2030 renewable capacity target` · `Number of parties` | 1% | f1 | the 'Contained 2030 renewable capacity target' bar, read against the axis | 否 | `Contained 2030 renewable capacity target` · `Number of parties` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 2 | 1 | 5 | 9 | 部分 | 0, 50, 100, 150, 200, 250 |

- **f1** Shares of fuel-combustion CO2 emissions in 2023 covered in NDC 3.0s (left) and country progress in submitting updates as of 28 September 2025 (right)　[图上方]　单位 `Number of parties`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | the exploded 'Submitted 23%' slice is drawn as a bar of two stacked segments, Advanced and Emerging |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | left pie and its exploded bar carry no ticks; only the printed percentage labels |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left panel in % with no axis, right panel counts on a 0-250 axis |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Notes: NDC = Nationally Determined Contribution. On 20 January 2025, US Executive Order 14162...' |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | left panel is a pie with an exploded stacked bar; right panel is a vertical bar chart |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bar axis reads bare 0-250; the scale word appears only as 'Number of parties' |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'Number of parties' set vertically along the left value axis of the bar panel |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | 'Not submitted 77%', 'Submitted 23%', 'Advanced 19%', 'Emerging and developing 4%' on leader lines outside slices |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 'Contained 2030 renewable capacity target' wraps onto five lines under the axis |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 50, 100, 150, 200, 250 across the bar panel, no vertical rules |

词表 65 项，本页出现 10 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `exploded_slice_to_stacked_bar` | f1 | leader lines connect the 'Submitted 23%' pie slice to a two-segment stacked bar breaking it into 19% and 4% | 读值时必须知道该堆叠条只是饼图某一扇区的二级分解，19%与4%相加等于23%，否则会把它当成独立面板的绝对量。 |
| `figure_caption_without_number` | f1 | bold blue heading above plot but no 'Figure n' label anywhere near it | 表格行无法用图号定位，只能靠整段标题文字寻址，增加匹配难度。 |
| `licence_credit_line` | f1 | 'IEA. CC BY 4.0.' printed at bottom right of the plot area, above the notes | 该行不是Source行，解析时容易误当作来源说明，影响对注释文字的定位。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

右侧柱图完全没有数值标签，刻度间距为50，网格线仅5条；5%容差下14要求读到13.3–14.7、5要求读到4.75–5.25，即在50单位/约60像素的刻度间距上分辨不到1像素的差别，实际不可能达到；57与54两根柱高度仅差3（约3像素），彼此的容差区间（54.2–59.9与51.3–56.7）重叠，极易互换。相比之下左侧四个百分比全部印在图上，寻址键最多3个（Submitted+Advanced+面板标题），表格可以承载，因此瓶颈在读值而非标签。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | 新增 exploded_slice_to_stacked_bar（饼图扇区展开为堆叠条）构造 | 图表族生成条件行中增加 compound 类型：pie + 引出线 + 二级堆叠条，并在记录字段中标注父扇区键 | 有/无“扇区二级分解”时，子项（19%、4%）与父项（23%）能否被正确归属的准确率对比 |
| P1 | 通用 | 无数值标签且刻度间距为量程1/5的柱图（对应 no_value_axis 与刻度密度） | 样式字段：value_axis_tick_step 与 values_printed 的组合，作为可读精度的输入 | 按每个mark的“刻度间距/数值”比给出可达精度分档，替代当前readable布尔门限 |
| P7 | 这份文档自己的习惯 | 无编号但有长句粗体标题的图（figure_caption_without_number） | 标题字段行：figure_number 允许为空，title 作为唯一寻址文本，并规定其在导出markdown中作为粗体/标题行的位置 | 图号缺失、仅有长标题时，值与上下文匹配成功率的对比行 |
| P2 | 一类出版方 | heterogeneous_panel_types（一图内饼图与柱图并列） | 面板维度进入键：panel_key 需记录左/右面板名称与各自的单位体系 | 同图异型面板时，是否为每面板单独建表对值归属正确率的影响 |
| P6 | 通用 | wrapped_category_labels（五行折行的类别标签） | 标签样式字段：类别标签最大宽度与折行行数 | 类别标签折行1行 vs ≥3行时，解析器还原完整类别名的成功率 |
