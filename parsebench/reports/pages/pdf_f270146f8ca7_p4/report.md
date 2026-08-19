# pdf_f270146f8ca7_p4

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| pdf_f270146f8ca7 | `need_estimate` | 10 | 10 |

这是《华尔街日报》2026年2月2日A4版新闻页，正文之间嵌有"Apple's Margins Threatened"报道配的两幅无编号图表：DRAM每GB价格季度柱状图与按市场板块的收入占比分组柱状图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 30% | `High Performance Computing*` · `2020` | 10% | f2 | an early High Performance Computing* bar (around the 2020 tick), read at the 30 gridline | 否 | `Proportion of revenue by market segment, quarterly` · `High Performance Computing*` · `2020` |
| 2 | 35% | `High Performance Computing*` · `'21` | 10% | f2 | a High Performance Computing* bar around the '21 tick, just above the 30 gridline | 否 | `Proportion of revenue by market segment, quarterly` · `High Performance Computing*` · `'21` |
| 3 | 41% | `High Performance Computing*` · `'22` | 10% | f2 | a High Performance Computing* bar around the '22 tick, just above the 40 gridline | 否 | `Proportion of revenue by market segment, quarterly` · `High Performance Computing*` · `'22` |
| 4 | 43% | `High Performance Computing*` · `'23` | 10% | f2 | a High Performance Computing* bar around the '23 tick, between the 40 and 50 gridlines | 否 | `Proportion of revenue by market segment, quarterly` · `High Performance Computing*` · `'23` |
| 5 | 48% | `High Performance Computing*` · `'24` | 10% | f2 | a High Performance Computing* bar around the '24 tick, just below the 50 gridline | 否 | `Proportion of revenue by market segment, quarterly` · `High Performance Computing*` · `'24` |
| 6 | 58% | `High Performance Computing*` · `'25` | 10% | f2 | the tallest High Performance Computing* bar, the last group at the right ('25) | 否 | `Proportion of revenue by market segment, quarterly` · `High Performance Computing*` · `'25` |
| 7 | 48% | `Smartphone` · `2020` | 10% | f2 | an early Smartphone bar (around the 2020 tick), just below the 50 gridline | 否 | `Proportion of revenue by market segment, quarterly` · `Smartphone` · `2020` |
| 8 | 45% | `Smartphone` · `'21` | 10% | f2 | a Smartphone bar in the '21-'22 span, between the 40 and 50 gridlines | 否 | `Proportion of revenue by market segment, quarterly` · `Smartphone` · `'21` |
| 9 | 33% | `Smartphone` · `'23` | 10% | f2 | a later Smartphone bar around the '24 tick, just above the 30 gridline | 否 | `Proportion of revenue by market segment, quarterly` · `Smartphone` · `'24` |
| 10 | 28% | `Smartphone` · `'25` | 10% | f2 | a Smartphone bar in the last group ('25), just below the 30 gridline | 否 | `Proportion of revenue by market segment, quarterly` · `Smartphone` · `'25` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: 33%

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 1 | 1 | 16 | 16 | 无 | $8, 6, 4, 2, 0 |
| f2 | `grouped_bar` | vertical | 1 | 2 | 24 | 48 | 无 | 60%, 50, 40, 30, 20, 10, 0 |

- **f1** Price per gigabyte for DRAM, the main system memory in AI servers and smartphones, quarterly　[图上方]　（标题里没有单位）
- **f2** Proportion of revenue by market segment, quarterly　[图上方]　（标题里没有单位）
  - 来源行：Sources: TechInsights (price per gigabyte for DRAM); TSMC (revenue)

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f2 | 有 | light and dark teal bars sit side by side in each quarter slot under the two-entry legend |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | the word "Projections" is set inside the plot area over the tinted right-hand region |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | a tinted vertical band covers the right-hand bars, labelled "Projections" |
| `right_side_y_axis` | 唯一的值轴画在右侧 | f1 | **无** | the only value axis is at the right edge, reading $8, 6, 4, 2, 0 |
| `right_side_y_axis` | 唯一的值轴画在右侧 | f2 | **无** | ticks 60%, 50, 40, 30, 20, 10, 0 drawn on the right edge of the plot |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately captioned charts stacked in the same column, each with its own title |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | "*Includes AI-related chips" and "Sources: TechInsights (price per gigabyte for DRAM); TSMC (revenue)" under the plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f2 | 有 | "High Performance Computing*" and "Smartphone" swatches sit between the title and the bars |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | news text columns run to the left and right of both charts in the same horizontal band |
| `footnote_marker` | 标题或标签里的脚注上标 | f2 | **无** | legend reads "High Performance Computing*" with "*Includes AI-related chips" printed below the plot |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | axis mixes "FY2023" with bare apostrophe years "'24", "'25", "'26" |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f2 | **无** | ticks written "2020", "'21", "'22", "'23", "'24", "'25" |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | bars are quarterly but ticks read only FY2023, '24, '25, '26 |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f2 | 有 | quarterly bar pairs with ticks only at 2020, '21, '22, '23, '24, '25 |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 2, 4, 6, 8 cross the bars; no vertical rules |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | horizontal rules at 10 through 60 cross the bars; no vertical rules |

词表 65 项，本页出现 12 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `unit_symbol_on_top_tick_only` | f1 | top tick prints "$8" and f2 prints "60%"; lower ticks are bare numbers 6, 4, 2, 0 | 刻度上唯一带单位的是最高刻度，读数时必须从顶端刻度把"$"或"%"补回其余数字，否则表格里的数值会失去量纲。 |
| `shared_source_line_two_figures` | page | "Sources: TechInsights (price per gigabyte for DRAM); TSMC (revenue)" sits under f2 but names both charts | 上图没有自己的来源行，来源需从下图脚注中按括号内说明分配，表格行的出处标注要跨图查找。 |
| `quarter_slots_without_labels` | f2 | 24 quarterly bar pairs but only 6 year ticks; individual quarters carry no printed name | 每个年份刻度下有四组柱子，任何一个数值都无法用页面上的文字唯一定位到某一季度。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

卡点在标签：f2 有约24个季度槽、每槽两根柱共48个标记，但横轴只印了2020、'21…'25 六个刻度，任何一根柱子在页面上都没有可逐字引用的季度名，表格只能用"High Performance Computing*"＋年份两个键去指认四根柱子中的一根。被打分的十个值又恰好在同一系列内多次接近：41% 与 43% 相差不到 5%，48% 出现两次（分属两个系列），仅靠系列名＋年份无法唯一寻址。相比之下读值本身还算可控——网格线每10个百分点一条，5% 容差在30%上是±1.5pp，约为一格的15%，尚在像素可分辨范围；真正无解的是缺失的季度键。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | 新组件 quarter_slots_without_labels（配合 sparse_time_ticks） | 记录字段：为每个类别槽增加"印在轴上的刻度文本"与"推导出的槽序号"两列，条件行中加入"刻度数<类别数"的时间轴设置 | 轴刻度密度：每个类别都有刻度 vs 每N个类别一个刻度（N=4），比较值定位命中率 |
| P7 | 一类出版方 | 新组件 unit_symbol_on_top_tick_only | 样式字段：unit_position 增加"仅附在最高刻度标签上"取值（如 $8 / 60%），其余刻度为裸数字 | 单位位置：轴标题 vs 副标题 vs 仅顶端刻度，测量导出数值是否带回量纲 |
| P3 | 这份文档自己的习惯 | 新组件 shared_source_line_two_figures 与 multi_figure_page 的组合 | 整页导出流程：来源/脚注行归属规则，允许一行来源同时挂到同栏两幅图 | 来源行归属：每图独立来源 vs 一行合并来源，检验图题与出处能否正确配对 |
| P6 | 一类出版方 | shaded_band 与 annotation_callout（"Projections"） | 条件行：在柱状图上叠加预测区间底纹并在图内放置文字标签的样式开关 | 预测区标注：无底纹 vs 底纹+图内文字，检验实际值与预测值是否被区分成两组行 |
