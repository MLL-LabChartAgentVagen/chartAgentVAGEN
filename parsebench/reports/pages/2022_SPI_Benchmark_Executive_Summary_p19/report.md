# 2022_SPI_Benchmark_Executive_Summary_p19

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2022_SPI_Benchmark_Executive_Summary | `untagged` | 5 | 0 |

这一页是关于人员增长（Headcount growth）的报告页，左侧为正文段落与一张五年折线图，右侧为按成熟度等级分组的柱状图（带植物生长图示）以及一个问答式文字框。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 9.2% | `2017` | 1% | f2 | the 2017 point on the line | 是 | `5 years of bumpy headcount growth:` · `2017` |
| 2 | 5.5% | `2020` | 1% | f2 | the 2020 point, the trough of the line | 是 | `5 years of bumpy headcount growth:` · `2020` |
| 3 | 9.1% | `2021` | 1% | f2 | the 2021 end point of the line | 是 | `5 years of bumpy headcount growth:` · `2021` |
| 4 | 7.0% | `Initiated` | 1% | f1 | the Initiated bar, shortest bar at left | 是 | `Headcount growth across maturity levels` · `Initiated` |
| 5 | 13.4% | `Institutionalised` | 1% | f1 | the Institutionalised bar, fourth from left | 是 | `Headcount growth across maturity levels` · `Institutionalised` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 1 | 1 | 5 | 5 | 全部 | （不画值轴） |
| f2 | `line` | vertical | 1 | 1 | 5 | 5 | 全部 | （不画值轴） |

- **f1** Headcount growth across maturity levels / In the hunt for the best talent, mature companies manage to find and attract the people they need　[图上方]　（标题里没有单位）
- **f2** 5 years of bumpy headcount growth:　[图上方]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | bars sit on a baseline with category names only; no ticks or value axis drawn |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | line over year labels 2017-2021, no y ticks or gridlines anywhere |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately captioned charts: "Headcount growth across maturity levels" and "5 years of bumpy headcount growth:" |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | left column paragraphs "The job market was hotter than ever..." run beside the right-hand grey chart panel |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | "7.0%", "7.8%", "9.0%", "13.4%", "15.4%" printed in white inside each teal bar |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | "9.2%", "7.7%", "9.0%", "5.5%", "9.1%" printed above or beside each circle marker |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | "Institutionalised" label is long and set in small type under its bar |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole chart block sits on a light grey filled rectangle |
| `icon_category_axis` | 类目轴用图标代替文字 | f1 | **无** | seed, sprout, seedling, bud and sunflower drawn above each bar as growth-stage pictograms |

词表 65 项，本页出现 8 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `pictogram_growth_metaphor_over_bars` | f1 | plant-growth illustrations of increasing size drawn above bars, decorative but ordered with categories | 图示高度并非数据编码，读者可能误以为植物高度代表数值；实际数值只能从柱内印刷标签读取。 |
| `unnumbered_figure_bold_lead_in_title` | f2 | "5 years of bumpy headcount growth:" set in bold body text with a colon, no figure number | 标题以正文粗体行出现且无编号，解析后表格需靠这行粗体文字来定位数据行的上下文。 |
| `percent_unit_only_in_value_labels` | f1 | no axis or heading gives a unit; "%" appears only inside labels like "13.4%" | 单位信息只寄生在数值标签里，若解析器剥离百分号，数值将失去尺度依据。 |

## 5 · 难在哪

卡在 **第四步 · 表外上下文**。

两张图的数值都印在图上（7.0%…15.4%、9.2%…9.1%），读数不成问题（第2步无风险）；每个值只需两个键（图标题＋类别/年份），表格容易承载（第3步也不难）。真正卡住的是上下文：两图都没有图号，f1 的标题"Headcount growth across maturity levels"和副标题以灰底框内的小号粗体出现，f2 的标题"5 years of bumpy headcount growth:"只是正文粗体一行，解析器很可能把它们并入正文段落，导致 9.1%（同时出现在正文"9.1% in 2021"里）与 f1 的 9.0% 无法区分归属；另外页面顶部大标题"Headcount growth"与 f1 标题近乎同名，进一步混淆归属。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | unit_in_axis_or_title 的反面情形：单位只存在于数值标签（对应 new_components 的 percent_unit_only_in_value_labels） | 样式字段中的 unit_position 增加 "labels_only" 取值，并允许 value_axis_ticks 为空 | 单位位置=仅在数值标签 vs 在标题/轴，比较数值尺度还原准确率 |
| P7 | 一类出版方 | 无编号图＋粗体正文式标题（unnumbered_figure_bold_lead_in_title） | 标题记录字段：figure_number 允许为空，title 渲染为正文粗体一行且置于绘图区上方 | 有图号标题 vs 无图号粗体标题，测量导出表格能否绑定正确图上下文 |
| P1 | 一类出版方 | no_value_axis 且全部数值内嵌（value_label_inside + value_label_outside 并存于同页） | 条件行中加入"无值轴"配置，标签位置按图分别设为 inside / outside | 有刻度轴 vs 无轴仅标签，比较读值召回与标签位置解析 |
| P6 | 这份文档自己的习惯 | icon_category_axis / 装饰性图示叠加（pictogram_growth_metaphor_over_bars） | 样式字段加入 category_axis_icons 与 decorative_overlay 开关 | 类别轴带图示 vs 纯文字，测量类别名抽取错误率 |
| P3 | 通用 | 同页多图且正文与图并列（multi_figure_page + side_text_bullets） | 整页 markdown 导出条件行：一页两张无编号图＋左侧文字栏 | 单图页 vs 双无编号图页，检验标题—表格配对是否串图 |
