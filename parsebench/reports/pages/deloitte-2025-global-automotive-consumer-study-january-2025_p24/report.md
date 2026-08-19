# deloitte-2025-global-automotive-consumer-study-january-2025_p24

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| deloitte-2025-global-automotive-consumer-study-january-2025 | `untagged` | 6 | 0 |

本页为《2025 Global Automotive Consumer Study》第24页，含两个无编号图：上方是八个市场驾车频率的100%水平堆叠条形图，下方是18–34岁受访者愿意放弃车辆所有权比例的纵向柱形图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 51% | `India` · `Every day` | 5% | f1 | the India 'Every day' segment, first (dark blue) segment of the top bar | 是 | `India` · `Every day` |
| 2 | 23% | `Southeast Asia` · `3-4 times per week` | 5% | f1 | the Southeast Asia '3-4 times per week' segment (also South Korea 3-4 times per week and Japan 'Every day' are 23%) | 是 | `Southeast Asia` · `3-4 times per week` |
| 3 | 11% | `US` · `1-2 times per week` | 5% | f1 | the India '1-2 times per week' segment (same value also in Southeast Asia, US, China rows) | 是 | `India` · `1-2 times per week` |
| 4 | 12% | `UK` · `Once every few months` | 5% | f1 | the UK 'Once every few months' segment, last segment of the UK bar | 是 | `UK` · `Once every few months` |
| 5 | 25% | `South Korea` · `Every day` | 5% | f1 | the India '3-4 times per week' segment (South Korea 'Every day' is also 25%) | 是 | `India` · `3-4 times per week` |
| 6 | 32% | `Japan` · `Once every few months` | 5% | f1 | the Japan 'Once every few months' segment, last segment of the bottom bar | 是 | `Japan` · `Once every few months` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 6 predicted key sets miss a rule label: 11%, 25%

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | horizontal | 1 | 6 | 8 | 48 | 全部 | （不画值轴） |
| f2 | `bar` | vertical | 1 | 1 | 8 | 8 | 全部 | （不画值轴） |

- **f1** Frequency of driving personal vehicle　[图上方]　（标题里没有单位）
  - 来源行：Note: Percentages may not add up to 100 due to rounding. Q70. How often do you drive your current vehicle? Sample size: n = 1,001 [China]; 1,507 [Germany]; 1,000 [India]; 1,000 [Japan]; 1,012 [Republic of Korea]; 6,029 [Southeast Asia]; 1,505 [UK]; 1,002 [US]
- **f2** Willingness to give up vehicle ownership in favor of MaaS (% somewhat willing/willing/very willing) – 18- to / 34-year-old respondents　[图上方]　单位 `% somewhat willing/willing/very willing`
  - 来源行：Q63. To what extent would you be willing to give up vehicle ownership in favor of a fully available mobility-as-a-service (MaaS) solution going forward? Sample size: n = 261 [China]; 344 [Germany]; 404 [India]; 191 [Japan]; 246 [Republic of Korea]; 2,116 [Southeast Asia]; 392 [UK]; 286 [US]

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each market row is one bar of six coloured segments labelled 51%, 25%, 11%, 6%, 3%, 5% |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f1 | **无** | all eight bars end at the same right edge; segments sum to about 100% |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | market names India...Japan sit on the y axis, bars grow rightwards |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or gridlines on the length axis, only printed percentages inside segments |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | only a baseline under the bars; no percentage ticks drawn |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately captioned green-titled charts with their own Q70 and Q63 note blocks |
| `source_note_lines` | source / note 行在图下方 | page | 有 | 'Note: Percentages may not add up to 100 due to rounding.' and 'Q70.'/'Q63.' sample-size lines |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend row 'Every day ... Once every few months' sits below the bars |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | title carries '(% somewhat willing/willing/very willing)'; bars have no axis unit |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | 51%, 25%, 11% printed inside their coloured segments |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | 70%, 54%, 44%, 35% printed inside the tops of the teal bars |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | categories written as 'US', 'UK' on the y axis |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f2 | 有 | x tick labels 'US', 'UK', 'Rep. of Korea' |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | Japan's 2% and China's 2%, 4% labels crowd narrow segments and spill over borders |

词表 65 项，本页出现 11 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `question_id_in_note` | page | note lines begin 'Q70. How often do you drive your current vehicle?' and 'Q63. To what extent...' | 图表标题不含问题全文，取值的语义只能从注释中的问题编号与问句还原，表格若丢掉该行就无法唯一定位这组百分比。 |
| `per_category_sample_size_note` | page | 'Sample size: n = 1,001 [China]; 1,507 [Germany]; 1,000 [India]...' lists n per market | 每个市场的分母写在注释里而非轴标签上，读者需把注释中的市场名与轴上缩写（US/UK）对齐才能正确解释数值。 |
| `same_value_repeated_across_series` | f1 | '11%' appears in India, Southeast Asia, US and China rows; '3%' repeats in five rows | 同一数字在多行多段重复出现，检索时必须同时给出市场名与频率类别名，否则无法唯一定位。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部印在段内，读数不成问题（步骤2轻松），但六个待查值中有四个在同一图内重复出现：11% 出现在 India、Southeast Asia、US、China 四行的 '1-2 times per week'，23% 同时是 Southeast Asia 与 South Korea 的 '3-4 times per week' 以及 Japan 的 'Every day'，25% 同时是 India 的 '3-4 times per week' 与 South Korea 的 'Every day'。因此每个值至少需要市场名+频率类别两个键，解析器若把六段堆叠压成一列或丢掉图例名，就无法把 11% 唯一定位；再加上两图共用市场名（India/US/UK/Germany 在 f1 与 f2 都出现），还需图标题作为第三层键。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | pct_stacked 与 no_value_axis 组合：无长度轴的100%堆叠横条，所有段值仅以段内标签给出 | 图表生成条件行中增加 'horizontal pct_stacked + 无刻度轴 + 全段内标签' 样式；记录字段需保留 series_name 作为列键 | 新增一行：堆叠段仅靠段内标签取值（无轴刻度）时，是否仍能输出 行=类别、列=系列 的完整表格 |
| P2 | 通用 | 新组件 same_value_repeated_across_series（同一数字在多行多段重复） | 评分/寻址逻辑：spot_check 的 addressing_keys 必须同时含类别名与系列名，而非单键匹配 | 新增一行：当目标值在同图中出现≥3次时，仅有一个键 vs 两个键的定位正确率 |
| P7 | 这份文档自己的习惯 | 新组件 question_id_in_note / per_category_sample_size_note（问题编号与分市场样本量置于注释行） | 图注字段：把 note/question/sample-size 拆成独立记录字段并要求导出到表下 | 新增一行：题干与样本量写在注释行而非标题时，导出表能否保留其与表格的绑定 |
| P3 | 一类出版方 | 无编号图的标题-副标题跨行断裂（'– 18- to' / '34-year-old respondents'） | heading 记录字段：figure_number 允许为空，title 与 subtitle 允许在同一句中折行 | 新增一行：标题跨行且无图号时，标题上下文是否被识别为该表的加粗标题 |
