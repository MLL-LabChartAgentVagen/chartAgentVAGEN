# deloitte-2025-global-automotive-consumer-study-january-2025_p15

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| deloitte-2025-global-automotive-consumer-study-january-2025 | `untagged` | 10 | 0 |

这是德勤《2025 Global Automotive Consumer Study》焦点市场章节的一页，含两个无编号图表：上方为八个市场的百分比堆积柱状图（前车是否同品牌），下方为2025与2024对比的分组柱状图（打算换品牌的比例）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 55 | `China` · `Yes` | 5% | f1 | the China 'Yes' segment (also Japan 'Yes' is 55%) | 是 | `China` · `Yes` · `Percentage of consumers whose prior vehicle was from the same brand as current vehicle` |
| 2 | 31 | `China` · `Current car is my first vehicle` | 5% | f1 | the China 'Current car is my first vehicle' segment (India 'No' is also 31%) | 是 | `China` · `Current car is my first vehicle` · `Percentage of consumers whose prior vehicle was from the same brand as current vehicle` |
| 3 | 36 | `Japan` · `No` | 5% | f1 | the Japan 'No' segment | 是 | `Japan` · `No` |
| 4 | 4 | `Germany` · `Current car is my first vehicle` | 5% | f1 | the Germany 'Current car is my first vehicle' segment, boxed label above the bar | 是 | `Germany` · `Current car is my first vehicle` |
| 5 | 25 | `Southeast Asia` · `Current car is my first vehicle` | 5% | f1 | the Southeast Asia 'Current car is my first vehicle' segment | 是 | `Southeast Asia` · `Current car is my first vehicle` |
| 6 | 76 | `China` · `2025` | 5% | f2 | the China '2025' bar | 是 | `China` · `2025` · `Percentage of consumers intending to switch to another brand* of vehicle` |
| 7 | 78 | `India` · `2024` | 5% | f2 | the India '2024' bar | 是 | `India` · `2024` |
| 8 | 62 | `Southeast Asia` · `2024` | 5% | f2 | the Southeast Asia '2024' bar | 是 | `Southeast Asia` · `2024` |
| 9 | 46 | `Germany` · `2025` | 5% | f2 | the Germany '2025' bar | 是 | `Germany` · `2025` |
| 10 | 35 | `Japan` · `2024` | 5% | f2 | the Japan '2024' bar | 是 | `Japan` · `2024` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 3 | 8 | 24 | 全部 | （不画值轴） |
| f2 | `grouped_bar` | vertical | 1 | 2 | 8 | 16 | 全部 | （不画值轴） |

- **f1** Percentage of consumers whose prior vehicle was from the same brand as current vehicle　[图上方]　（标题里没有单位）
  - 来源行：Q6. Was your prior vehicle from the same brand? Sample size: n = 852 [China]; 1,114 [Germany]; 646 [India]; 452 [Japan]; 618 [Republic of Korea]; 3,488 [Southeast Asia]; 1,044 [UK]; 821 [US]
- **f2** Percentage of consumers intending to switch to another brand* of vehicle　[图上方]　（标题里没有单位）
  - 来源行：*Includes switching to a different brand from the same parent or a different brand from a different sales parent. Q5. What brand is the vehicle you drive most often? Q26. What brand are you considering most for your next vehicle? [Brand switching percentage is based on a calculation involving these two questions.] Sample size: n = 830 [China]; 1,073 [Germany]; 633 [India]; 398 [Japan]; 589 [Republic of Korea]; 3,807 [Southeast Asia]; 959 [UK]; 786 [US]

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f2 | 有 | two bars per market, dark '2025' beside light '2024' |
| `stacked_bar` | 堆叠条 | f1 | 有 | each market bar stacks 'Yes', 'No', 'Current car is my first vehicle' segments |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only a baseline under the bars; no ticks or numbers on any value axis |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | bars sit on a bare baseline, no tick labels anywhere |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately captioned charts with their own question and sample-size notes |
| `source_note_lines` | source / note 行在图下方 | page | 有 | 'Q6. Was your prior vehicle from the same brand? Sample size: n = 852 [China]...' under each chart |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Yes  No  Current car is my first vehicle' row under the category axis |
| `legend_inside_plot` | 图例画在绘图区内部 | f2 | **无** | '2025' and '2024' legend swatches drawn at the top right of the plot area |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | bold lead-in paragraphs sit directly above each chart title, not beside it |
| `footnote_marker` | 标题或标签里的脚注上标 | f2 | **无** | 'another brand* of vehicle' with '*Includes switching to a different brand...' below |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | '55%', '15%', '31%' printed white/dark inside their segments |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | '76%', '73%' printed inside the tops of the bars |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | Germany '4%' and US '5%' set in boxed labels above the bars |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | Germany 4% and US 5% top segments too thin, labels moved out into white boxes |

词表 65 项，本页出现 12 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `green_subtitle_as_chart_title` | page | green line 'Percentage of consumers whose prior vehicle was...' acts as title under a bold black narrative paragraph | 读值时必须区分黑色叙述句与绿色标题行，只有绿色行才是该图的量纲说明（percentage），否则会把结论句当成图题。 |
| `boxed_outside_label_with_leader` | f1 | '4%' and '5%' in white boxes with thin connector to the thin top segment | 这两个值不在段内，需靠白框与引线归属到对应柱的第三段，容易错配到相邻国家。 |
| `pct_stack_not_summing_to_100` | f1 | Germany 51+45+4=100 but Southeast Asia 45+31+25=101, bar tops differ slightly | 不能假定百分比堆积到满100%，读取时应以印刷标签为准而非按高度反推比例。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

所有10个待检值都以百分数印在柱上，读数不成问题（第2步不难）；两图也都没有值轴，所以像素读数根本不需要。真正的瓶颈是寻址：f1中55%在China和Japan各出现一次、31%既是China的'first vehicle'段又是India的'No'段，f2中54%既是US的2025也是UK的2024，因此一行必须同时携带国家名和系列名（Yes/No/Current car is my first vehicle 或 2025/2024）两个键，且两图共用同一批国家标签（China、Japan、India…），若解析器不把绿色图题写成加粗行区分两个表，同一对(China, 2025)与(China, Yes)会混淆。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | thin_segment_label 与新提的 boxed_outside_label_with_leader（细段值标签移出并加白框） | 样式字段中的 value-label placement：当段高低于阈值时切换为带白底框的外置标签并连引线 | 新增一行：细段（<6%）标签内置 vs 外置带框，比较该段值被正确归属到国家的准确率 |
| P1 | 一类出版方 | no_value_axis（无值轴、仅靠印刷标签读数） | 条件行中增加“隐藏值轴 + 全部标注数值”的组合开关 | 新增一行：有轴无标签 / 无轴全标签 / 两者兼有，对比每标记可达精度 |
| P7 | 这份文档自己的习惯 | 绿色副标题充当图题（green_subtitle_as_chart_title）与无编号图题 | 记录字段的 heading：number 允许为空，并区分 narrative lead-in 与 colored title 行 | 新增一行：图题为空编号且上方另有加粗叙述段时，表格上下文键的命中率 |
| P3 | 通用 | multi_figure_page（同页两图共用同一组国家类别名） | 整页 markdown 导出中要求每个表前置其绿色标题作为加粗标题行 | 新增一行：同页两表类别名完全重叠时，是否输出图题标题行对寻址正确率的影响 |
