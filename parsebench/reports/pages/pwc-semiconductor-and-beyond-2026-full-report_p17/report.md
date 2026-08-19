# pwc-semiconductor-and-beyond-2026-full-report_p17

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| pwc-semiconductor-and-beyond-2026-full-report | `need_estimate` | 10 | 10 |

PwC《Semiconductor and beyond 2026》第17页，左栏为正文，右半灰底区域是一张'19–'30F 全球数据中心用电量的堆叠柱状图（AI 驱动需求／传统需求）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 22 | `'19` · `Conventional demand` | 10% | f1 | the ’19 Conventional demand (grey) segment | 否 | `’19` · `Conventional demand` · `Global data center power consumption` · `(Unit: GW)` |
| 2 | 1 | `'19` · `AI-driven demand` | 10% | f1 | the ’19 AI-driven demand (orange) sliver on top of the ’19 bar | 否 | `’19` · `AI-driven demand` · `Global data center power consumption` · `(Unit: GW)` |
| 3 | 46 | `'22` · `Conventional demand` | 10% | f1 | the ’22 Conventional demand (grey) segment | 否 | `’22` · `Conventional demand` · `Global data center power consumption` · `(Unit: GW)` |
| 4 | 11 | `'22` · `AI-driven demand` | 10% | f1 | the ’22 AI-driven demand (orange) segment, from ~46 to ~57 | 否 | `’22` · `AI-driven demand` · `Global data center power consumption` · `(Unit: GW)` |
| 5 | 62 | `'25F` · `Conventional demand` | 10% | f1 | the ’25F Conventional demand (grey) segment | 否 | `’25F` · `Conventional demand` · `Global data center power consumption` · `(Unit: GW)` |
| 6 | 33 | `'25F` · `AI-driven demand` | 10% | f1 | the ’25F AI-driven demand (orange) segment, from ~62 to ~95 | 否 | `’25F` · `AI-driven demand` · `Global data center power consumption` · `(Unit: GW)` |
| 7 | 80 | `'28F` · `Conventional demand` | 10% | f1 | the ’28F Conventional demand (grey) segment | 否 | `’28F` · `Conventional demand` · `Global data center power consumption` · `(Unit: GW)` |
| 8 | 62 | `'28F` · `AI-driven demand` | 10% | f1 | the ’28F AI-driven demand (orange) segment, from ~80 to ~142 | 否 | `’28F` · `AI-driven demand` · `Global data center power consumption` · `(Unit: GW)` |
| 9 | 96 | `'30F` · `Conventional demand` | 10% | f1 | the ’30F Conventional demand (grey) segment | 否 | `’30F` · `Conventional demand` · `Global data center power consumption` · `(Unit: GW)` |
| 10 | 68 | `'30F` · `AI-driven demand` | 10% | f1 | the ’30F AI-driven demand (orange) segment, from ~96 to ~164 | 否 | `’30F` · `AI-driven demand` · `Global data center power consumption` · `(Unit: GW)` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 2 | 12 | 24 | 无 | 0, 20, 40, 60, 80, 100, 120, 140, 160, 180 |

- **f1** Global data center power consumption　[图上方]　单位 `(Unit: GW)`
  - 来源行：Source: IEA, PwC analysis

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each year bar has a grey lower segment and an orange upper segment, total is bar height |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | pale pink filled envelope drawn between bar tops across categories in addition to the bars |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | bold text over plot: "Rising AI data center power consumption signals growing AI compute demand and chipset needs" |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: IEA, PwC analysis" in small print below the plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | orange/grey swatches with "AI-driven demand" and "Conventional demand" sit level with the title, above the plot |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | three body paragraphs run in a left column level with the chart, sharing one horizontal band |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | "(Unit: GW)" printed right of the title; y axis shows bare 0–180 |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | ticks written as ’19, ’20 … ’30F rather than full years |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole figure area including plot is filled light grey, not white |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 20-unit steps across the panel, no vertical rules |

词表 65 项，本页出现 10 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `bar_top_connector_area` | f1 | pale pink fill joins the grey-segment tops and the total tops from ’19 to ’30F behind the bars | 这条粉色带不是独立数据序列，读者可能把它当第三个序列或折线读数；实际数值只能从柱段本身对轴读取。 |
| `forecast_suffix_on_time_ticks` | f1 | ticks ’25F–’30F carry an F suffix while ’19–’24 do not, marking forecast years | 行名必须逐字保留 F（如“’25F”），否则无法把预测年与历史年的同一段数值区分开。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上一个数字都没印，全部 20 个受测数值都要靠像素对轴读；轴刻度间距为 20 GW，约 60 px，即 1 px≈0.33 GW。堆叠段还必须用两次读数相减：’19 的 AI 段只有约 1 GW（2–3 px 高），5% 容差即 ±0.05 GW，远低于像素分辨率；’22 的 11 GW（±0.55 GW≈1.7 px）同样卡在噪声级。相比之下标签只需 2 个键（年份 + 序列名），并不构成瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | 新组件 bar_top_connector_area（连接柱顶的浅色包络填充） | 堆叠柱样式字段中增加“柱顶包络填充”开关及其配色/透明度 | 带柱顶包络填充 vs 纯堆叠柱：段值抽取误差与“是否被误判为额外面积序列”的比例 |
| P7 | 一类出版方 | unit_in_axis_or_title：单位以“(Unit: GW)”形式紧随标题右侧而非置于轴上 | heading 记录字段拆分为 number/title/subtitle/unit，并新增 unit 位置=title_inline | 单位在标题行内 vs 单位在轴标签处：导出表格中单位是否随行名一同出现 |
| P6 | 一类出版方 | nonstandard_time_ticks 与新组件 forecast_suffix_on_time_ticks（’25F–’30F） | 时间轴刻度格式字段：加入撇号缩写年与预测后缀两种渲染 | ’25F 型刻度 vs 2025 型刻度：值+行名同时命中的比例 |
| P3 | 通用 | annotation_callout：绘图区内三行加粗说明文字 | 图内注释文本块的位置与字重样式字段 | 有图内加粗注释 vs 无：注释文字被误当作标题或序列名的比例 |
