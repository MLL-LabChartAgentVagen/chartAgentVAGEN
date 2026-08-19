# deloitte-2025-global-automotive-consumer-study-january-2025_1_p15

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| deloitte-2025-global-automotive-consumer-study-january-2025_1 | `untagged` | 10 | 0 |

该页为德勤《2025 Global Automotive Consumer Study》焦点市场章节，含两张无编号图表：上方为八个市场

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 55% | `China` · `Yes` | 5% | f1 | the China 'Yes' segment (Japan 'Yes' is also 55%) | 是 | `China` · `Yes` · `Percentage of consumers whose prior vehicle was from the same brand as current vehicle` |
| 2 | 36% | `Japan` · `No` | 5% | f1 | the Japan 'No' segment | 是 | `Japan` · `No` |
| 3 | 4% | `Germany` · `Current car is my first vehicle` | 5% | f1 | the Germany 'Current car is my first vehicle' segment, boxed label above the bar | 是 | `Germany` · `Current car is my first vehicle` |
| 4 | 45% | `Southeast Asia` · `Yes` | 5% | f1 | the Germany 'No' segment (Southeast Asia 'Yes' is also 45%) | 是 | `Germany` · `No` |
| 5 | 51% | `UK` · `No` | 5% | f1 | the Germany 'Yes' segment (UK 'No' is also 51%) | 是 | `Germany` · `Yes` |
| 6 | 76% | `China` · `2025` | 5% | f2 | the China 2025 bar | 是 | `China` · `2025` · `Percentage of consumers intending to switch to another brand* of vehicle` |
| 7 | 78% | `India` · `2024` | 5% | f2 | the India 2024 bar | 是 | `India` · `2024` |
| 8 | 71% | `Southeast Asia` · `2025` | 5% | f2 | the Southeast Asia 2025 bar | 是 | `Southeast Asia` · `2025` |
| 9 | 51% | `US` · `2024` | 5% | f2 | the US 2024 bar | 是 | `US` · `2024` · `Percentage of consumers intending to switch to another brand* of vehicle` |
| 10 | 39% | `Japan` · `2025` | 5% | f2 | the Japan 2025 bar | 是 | `Japan` · `2025` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 45%, 51%

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 3 | 8 | 24 | 全部 | （不画值轴） |
| f2 | `grouped_bar` | vertical | 1 | 2 | 8 | 16 | 全部 | （不画值轴） |

- **f1** Percentage of consumers whose prior vehicle was from the same brand as current vehicle　[图上方]　单位 `Percentage of consumers`
  - 来源行：Q6. Was your prior vehicle from the same brand? Sample size: n = 852 [China]; 1,114 [Germany]; 646 [India]; 452 [Japan]; 618 [Republic of Korea]; 3,488 [Southeast Asia]; 1,044 [UK]; 821 [US]
- **f2** Percentage of consumers intending to switch to another brand* of vehicle　[图上方]　单位 `Percentage of consumers`
  - 来源行：*Includes switching to a different brand from the same parent or a different brand from a different sales parent. Q5. What brand is the vehicle you drive most often? Q26. What brand are you considering most for your next vehicle? [Brand switching percentage is based on a calculation involving these two questions.] Sample size: n = 830 [China]; 1,073 [Germany]; 633 [India]; 398 [Japan]; 589 [Republic of Korea]; 3,807 [Southeast Asia]; 959 [UK]; 786 [US]

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f2 | 有 | two bars per market side by side, dark 2025 next to light 2024, e.g. China 76% and 73% |
| `stacked_bar` | 堆叠条 | f1 | 有 | each market bar holds three stacked segments, e.g. China 55%/15%/31% |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f1 | **无** | all eight stacks reach the same top height and segments sum to ~100% |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only a baseline under the bars; no ticks or numbers on any value axis |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | bars sit on a bare baseline, no tick labels anywhere on the left edge |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two independent charts, each with its own green title line and its own note block |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Q6. Was your prior vehicle from the same brand?' and 'Sample size: n = 852 [China]...' under plot |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | '*Includes switching to a different brand from the same parent...' plus Q5/Q26 and sample-size lines |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Yes  No  Current car is my first vehicle' row under the category axis |
| `legend_inside_plot` | 图例画在绘图区内部 | f2 | **无** | '2025' / '2024' swatches drawn top-right over the plot area, above the short bars |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title 'Percentage of consumers whose prior vehicle was from the same brand as current vehicle' |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | title 'Percentage of consumers intending to switch to another brand* of vehicle' |
| `footnote_marker` | 标题或标签里的脚注上标 | f2 | **无** | title reads 'another brand* of vehicle' with matching '*Includes switching...' note |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | '55%', '15%', '31%' printed in white/black on top of their segments |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | '76%', '73%' printed inside the top of each bar |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '4%' and '5%' sit in white boxes above the bars, outside their thin top segments |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | Germany 4% and US 5% top segments too narrow, labels pushed out into boxed callouts |

词表 65 项，本页出现 13 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `takeaway_statement_above_title` | page | bold black sentence 'More than half of surveyed consumers in China owned the same brand...' sits above each green chart title | 图表标题上方还有一层加粗结论句，解析时容易把它当成标题或正文，导致图的真正标题（绿色行）与表格失联，读值时无法确定该值属于哪张图。 |
| `boxed_value_label_outside_segment` | f1 | '4%' and '5%' drawn in white rectangles with thin border, overlapping the bar top edge | 这两个值不在色块内部，靠白底方框浮在柱顶，需要额外判断它属于最上层 |
| `per_category_sample_size_note` | page | 'Sample size: n = 852 [China]; 1,114 [Germany]; 646 [India]...' lists n per axis category | 注释行按类别给出样本量，与坐标轴类别一一对应，可作为附加列；若被当成普通文字，则类别名的另一处出处丢失。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

两图所有数字都印在柱上，且没有任何刻度轴，所以第2步（读像素）几乎不成立；难点在寻址。f1 每个值需要

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | no_value_axis 与 value_label_inside/value_label_outside 组合（纯标签读数、无刻度轴） | 样式字段：value_axis 显示开关与 value_label 放置位置（inside / outside-boxed） | 新增一行 |
| P6 | 一类出版方 | thin_segment_label 与新提出的 boxed_value_label_outside_segment | 堆叠柱渲染条件行：当段占比 <8% 时标签外移并加白底边框方框 | 新增一行 |
| P7 | 这份文档自己的习惯 | 新提出的 takeaway_statement_above_title（加粗结论句 + 彩色图表标题的双层抬头） | heading 记录字段：拆出 lead_statement 与 title，并记录标题块相对绘图区的位置 | 新增一行 |
| P3 | 一类出版方 | footnote_marker 与 source_note_lines（标题带 * 且注释含 Q 编号与逐类别样本量） | 记录字段：note_lines 数组，允许多行注释与标题脚注标记配对 | 新增一行 |
