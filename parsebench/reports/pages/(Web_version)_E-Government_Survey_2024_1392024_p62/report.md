# (Web_version)_E-Government_Survey_2024_1392024_p62

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| (Web_version)_E-Government_Survey_2024_1392024 | `untagged` | 5 | 0 |

该页为报告第37页，正文讨论各EGDI组国家数量变化，中部为唯一一幅图 Figure 2.2 的四系列纵向堆叠柱状图（2014–2024，每段标注

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 25 (13.0%) | `Very high EGDI` · `2014` | 1% | f1 | the 2014 Very high EGDI top segment | 是 | `2014` · `Very high EGDI` |
| 2 | 74 (38.3%) | `Middle EGDI` · `2014` | 1% | f1 | the 2014 Middle EGDI segment | 是 | `2014` · `Middle EGDI` |
| 3 | 73 (37.8%) | `High EGDI` · `2018` | 1% | f1 | ambiguous: the same text labels both the 2018 High EGDI segment and the 2022 High EGDI segment | 是 | `2018` · `2022` · `High EGDI` |
| 4 | 76 (39.4%) | `Very high EGDI` · `2024` | 1% | f1 | the 2024 Very high EGDI top segment | 是 | `2024` · `Very high EGDI` |
| 5 | 7 (3.6%) | `Low EGDI` · `2022` | 1% | f1 | the 2022 Low EGDI bottom segment | 是 | `2022` · `Low EGDI` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 4 | 6 | 24 | 全部 | 0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200 |

- **f1** Figure 2.2 / Number and percentage of countries in each EGDI group, 2014 to 2024　[图上方]　（标题里没有单位）
  - 来源行：Sources: 2014-2024 United Nations E-Government Surveys.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | four coloured segments stacked in each year's bar, e.g. 2024 stacks 11, 44, 62, 76 |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Sources: 2014-2024 United Nations E-Government Surveys.` in small italic-led print below the plot box |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | `Low EGDI  Middle EGDI  High EGDI  Very high EGDI` row under the 2014-2024 tick row |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis reads 0...200 bare; only the title says `Number and percentage of countries` |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | `25 (13.0%)`, `74 (38.3%)` printed on top of each segment |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | `8 (4.1%)` and `7 (3.6%)` sit in bottom segments only ~4 units tall, label taller than segment |

词表 65 项，本页出现 6 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `count_and_share_in_one_label` | f1 | every segment label pairs count and percent: `62 (32.1%)`, `44 (22.8%)` | 一个标签同时承载两个量（国家数与占比），取值时必须决定抽取哪一个，且括号内百分比与柱高无关，不能按坐标轴校验 |
| `duplicate_label_text_across_categories` | f1 | `73 (37.8%)` appears in both 2018 and 2022; `62 (32.1%)` in 2014 and 2024 | 同一字符串在图上出现两次，只搜数值无法定位，必须同时用年份和系列名两个键才能唯一指向某个段 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

读数不构成障碍：24个段全部印有`74 (38.3%)`这类标签，无需按20一格的刻度估读。真正卡住的是定位键：`73 (37.8%)`在2018与2022各出现一次，`62 (32.1%)`在2014与2024各出现一次，`32 (16.6%)`在2014与2016重复，因此任一行必须同时携带年份（六个之一）与EGDI组名（Low/Middle/High/Very high）两个键，缺一即无法与另一处同文本的段区分；而图例在绘图区下方、年份在x轴上，解析器若把标签展平成一列数字，键就丢了。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 count_and_share_in_one_label（标签内同时含计数与百分比） | 样式字段中的 value_label 格式项，增加“单标签双量”模板如 `{value} ({share}%)` | 标签为单一数值 vs 标签为“计数(占比%)”复合串时，数值抽取准确率对比 |
| P2 | 通用 | 新组件 duplicate_label_text_across_categories（同一标签文本跨类别重复） | 记录字段：生成数据时允许重复值，并要求评分行同时给出 category_key 与 series_key | 表内存在重复数值 vs 全部数值唯一时，定位所需键数（1键 vs 2键）的命中率对比 |
| P7 | 通用 | unit_in_axis_or_title（0–200 裸刻度，量纲只在标题“Number and percentage of countries”里） | 标题字段拆分：figure_number / title / subtitle / unit 及 placement=above | 量纲写在坐标轴 vs 只写在标题时，导出表格是否保留量纲信息 |
| P6 | 一类出版方 | thin_segment_label（`7 (3.6%)`挤在约4单位高的薄段中） | 样式条件行：堆叠段高度低于标签行高时的标签避让策略（内置/外移/引线） | 薄段标签内置 vs 外移时，该段数值被正确归属到对应系列的比例 |
