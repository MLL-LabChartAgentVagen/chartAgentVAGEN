# Digital_News-Report_2022_p27

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Digital_News-Report_2022 | `untagged` | 4 | 0 |

本页为路透社数字新闻报告2022第27页，左栏正文加两个百分比堆叠横条图：按年龄的"多以文字阅读新闻"比例，以及全部46个市场的同题分布。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 17 | `18-24` · `Mostly watch` | 1% | f2 | several candidates: the UK 'Don't know' segment (17), Singapore 'Same' (17), Canada 'Same' (17), Malaysia 'Same' (17), Slovakia 'Same' (17), India 'Mostly watch' (17), South Korea 'Mostly watch' (17), Australia 'Same' is 11; also f1 18-24 'Mostly watch' = 17 | 是 | `PROPORTION WHO MOSTLY READ NEWS IN TEXT –` · `ALL MARKETS` · `UK` · `Don't know` |
| 2 | 85 | `Finland` · `Mostly read` | 1% | f2 | the Finland 'Mostly read' segment, largest read share on the chart | 是 | `PROPORTION WHO MOSTLY READ NEWS IN TEXT –` · `ALL MARKETS` · `Finland` · `Mostly read` |
| 3 | 25 | `Mexico` · `Same` | 1% | f2 | the Mexico 'Same' segment (bottom row); note 25% is also an axis tick label | 是 | `PROPORTION WHO MOSTLY READ NEWS IN TEXT –` · `ALL MARKETS` · `Mexico` · `Same` |
| 4 | 21 | `France` · `Don't know` | 1% | f2 | the France 'Don't know' segment (21), also Brazil 'Same' (21) and Austria 'Same' (21) | 是 | `PROPORTION WHO MOSTLY READ NEWS IN TEXT –` · `ALL MARKETS` · `France` · `Don't know` |

**程序核对**（模型没有看到左半的标签列）：

- 首次调用返回空答案，加一句追问后重问了一次——the first reply described no figure
- 给了 N 个值，模型回了另一个数目——4 values given, 5 answered
- 模型预测的定位标签漏掉了规则实际用的标签——1 of 4 predicted key sets miss a rule label: 17

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | horizontal | 1 | 4 | 4 | 16 | 全部 | 0%, 25%, 50%, 75%, 100% |
| f2 | `stacked_bar` | horizontal | 1 | 4 | 46 | 184 | 全部 | 0%, 25%, 50%, 75%, 100% |

- **f1** PROPORTION WHO MOSTLY READ NEWS IN TEXT – BY AGE / – ALL MARKETS　[图上方]　（标题里没有单位）
  - 来源行：OPTQ11D. In thinking about your online news habits, which of the following statements applies best to you? Base: Total sample; all markets = 93,432.
- **f2** PROPORTION WHO MOSTLY READ NEWS IN TEXT – / ALL MARKETS　[图上方]　（标题里没有单位）
  - 来源行：OPTQ11D. In thinking about your online news habits, which of the following statements applies best to you? Please select one. Showing net of different option statements. Base: Total sample in each market (n = 2000).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each age row is one bar of four coloured segments Mostly read/Same/Mostly watch/Don't know |
| `stacked_bar` | 堆叠条 | f2 | 有 | each market row stacks four coloured segments in one bar |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f1 | **无** | every bar spans the full width and axis reads 0%, 25%, 50%, 75%, 100% |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f2 | **无** | all 46 bars reach the same length, axis ends at 100% |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | age groups on the y axis, bars grow right to 100% |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f2 | **无** | market names down the left, bars grow rightwards |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately captioned charts, one left column, one right column |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'OPTQ11D. In thinking about your online news habits...' under the plot |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | 'OPTQ11D. ... Base: Total sample in each market (n = 2000).' below the bars |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | legend row 'Mostly read Same Mostly watch Don't know' sits between title and bars |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f2 | 有 | same four-key legend row placed above the plot area |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | left column body text runs alongside the tall all-markets chart in the right column |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | 'according to recent research.\u00b9\u00b9' with footnote 11 URL at page foot |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | numbers 67, 14, 11, 8 printed white inside each segment |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | 85, 7, 3, 6 printed inside Finland's segments |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f2 | **无** | Nigeria's '1' and Kenya's '1' and Greece's '3' are squeezed at segment edges |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f2 | **无** | 46 market names stack down the axis, 'Czech Republic', 'South Africa' etc. |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f2 | **无** | 46 markets \u00d7 4 segments = 184 drawn segments |

词表 65 项，本页出现 12 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `question_code_as_source_line` | page | note lines start with bold survey code 'OPTQ11D.' instead of 'Source:' | 表格导出时该行是题目编号与样本基数，不是数据来源；解析器需把它识别为注释行才能锁定图与值的对应。 |
| `percent_sign_only_on_ticks` | f2 | axis ticks read '0%, 25%, 50%, 75%, 100%' while in-bar labels are bare numbers 85, 7, 3, 6 | 读值时单位只存在于刻度上，表格若只抄条内数字会丢失百分号语义。 |
| `long_single_column_bar_list` | f2 | 46 country rows in one tall column spanning nearly the full page height | 行数极多且无分组标题，需靠国家名唯一定位每个数值。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部印在段内（85、25、21、17 皆可直接抄，无需按刻度估读，25%的刻度间距也远大于5%容差），所以第2步不构成障碍。真正的瓶颈是标签：f2 有 46 行 × 4 个系列共 184 个数字，像 17 在 UK 的 Don't know、Singapore/Canada/Malaysia/Slovakia 的 Same、India/South Korea 的 Mostly watch 上重复出现，21 在 France 的 Don't know、Brazil 与 Austria 的 Same 上重复；另外 f1（按年龄）也有 8、17 等相同数字。要唯一定位一个值必须同时给出图标题、市场/年龄组名与系列名三重键，而两图共用同一套图例名，解析出的表格若丢掉图标题或系列列头就无法区分。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P5 | 一类出版方 | pct_stacked 与 dense_marks_100plus 的组合：46 行 × 4 系列的超长百分比堆叠横条 | 生成条件行中的类别数上限与密度上限字段（categories/marks cap） | 新增一行\"类别数 ≥ 40 的单面板百分比堆叠横条\"，观察行名唯一定位与标签重复时的检索准确率 |
| P6 | 通用 | thin_segment_label（窄段内数字挤压/贴边，如 Nigeria 的 1、Greece 的 3） | 样式字段中的 value-label placement（inside vs 挤出段外）规则 | 新增一行\"最小段占比 <4% 时标签是否仍可读\"，比较标签位置策略对读数正确率的影响 |
| P7 | 这份文档自己的习惯 | 标题拆分：主标题带尾破折号、副标题为 'ALL MARKETS'，无图号 | 记录的 heading 字段（figure_number 可空、title/subtitle 分行） | 新增一行\"无编号且标题跨行的图，标题是否以粗体标题形式出现在表格上方\" |
| P3 | 这份文档自己的习惯 | new_components 中的 question_code_as_source_line（以 'OPTQ11D.' 开头的注释行） | 注释/来源行模板字段，允许以问卷题号+Base 样本量代替 'Source:' | 新增一行\"注释行不含 Source 关键字时能否仍被归为图注而非正文\" |
| P3 | 一类出版方 | 同页两图共用同一图例名集合时的上下文归属（multi_figure_page + 相同系列名） | 整页 markdown 导出中表格与其标题的相对位置 | 新增一行\"同页两表系列名完全相同时，值—标题绑定的正确率\" |
