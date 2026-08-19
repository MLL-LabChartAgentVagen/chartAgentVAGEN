# Activate_Consulting_Technology_&_Media_Outlook_2026_(10)_p60

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Activate_Consulting_Technology_&_Media_Outlook_2026_(10) | `untagged` | 10 | 0 |

这是一页Activate Consulting的报告幻灯片，含一张按地区拆分的堆叠柱状图，展示2019/2021/2025E/2029E全球消费者游戏收入（美国与世界其他地区）及各段CAGR圆形标注。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 101 | `Rest of World` · `2019` | 1% | f1 | the 2019 REST OF WORLD segment, labelled "$101B" | 是 | `2019` · `REST OF WORLD` · `BILLIONS USD` |
| 2 | 35 | `U.S.` · `2019` | 1% | f1 | the 2019 U.S. segment, labelled "$35B" | 是 | `2019` · `U.S.` · `BILLIONS USD` |
| 3 | 121 | `Rest of World` · `2021` | 1% | f1 | the 2021 REST OF WORLD segment, labelled "$121B" | 是 | `2021` · `REST OF WORLD` · `BILLIONS USD` |
| 4 | 48 | `U.S.` · `2021` | 1% | f1 | the 2021 U.S. segment, labelled "$48B" | 是 | `2021` · `U.S.` · `BILLIONS USD` |
| 5 | 130 | `Rest of World` · `2025E` | 1% | f1 | the 2025E REST OF WORLD segment, labelled "$130B" | 是 | `2025E` · `REST OF WORLD` · `BILLIONS USD` |
| 6 | 50 | `U.S.` · `2025E` | 1% | f1 | the 2025E U.S. segment, labelled "$50B" | 是 | `2025E` · `U.S.` · `BILLIONS USD` |
| 7 | 155 | `Rest of World` · `2029E` | 1% | f1 | the 2029E REST OF WORLD segment, labelled "$155B" | 是 | `2029E` · `REST OF WORLD` · `BILLIONS USD` |
| 8 | 59 | `U.S.` · `2029E` | 1% | f1 | the 2029E U.S. segment, labelled "$59B" | 是 | `2029E` · `U.S.` · `BILLIONS USD` |
| 9 | 16 | `2019-2021 CAGR` · `U.S.` | 1% | f1 | the purple circle "16%" in the 2019-2021 gap on the U.S. row | 是 | `2019-2021 CAGR:` · `U.S.` |
| 10 | 10 | `2019-2021 CAGR` · `Rest of World` | 1% | f1 | the purple circle "10%" in the 2019-2021 gap on the REST OF WORLD row | 是 | `2019-2021 CAGR:` · `REST OF WORLD` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 2 | 4 | 8 | 全部 | （不画值轴） |
| f1 | `stacked_bar` | vertical | 1 | 2 | 4 | 8 | 全部 | （不画值轴） |

- **f1** CONSUMER VIDEO GAME REVENUE BY REGION¹, GLOBAL, 2019 VS. 2021 VS. 2025E VS. 2029E, BILLIONS USD　[图上方]　单位 `BILLIONS USD`
  - 来源行：Sources: Activate analysis, Newzoo, Omdia, PricewaterhouseCoopers, Statista
- **f1** （无标题）　[无标题]　（标题里没有单位）
  - 来源行：Sources: Activate analysis, Newzoo, Omdia, PricewaterhouseCoopers, Statista

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each bar splits into a dark lower segment ($35B) and a light upper segment ($101B), total $136B |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | black circles "11%", "2%", "4%" and purple circles "10%", "16%", "2%", "1%", "4%" over inter-bar gaps |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only a horizontal baseline under the bars; no value ticks anywhere, values only as printed labels |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "1. Excludes hardware and device sales, augmented/virtual reality content, and advertising." plus "Sources: Activate analysis, Newzoo..." |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | banner heading ends "BILLIONS USD"; no axis carries the scale |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | "BY REGION¹" superscript 1 with note "1. Excludes hardware and device sales..." |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | "$101B", "$35B", "$121B", "$48B" printed in white inside the segments |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | totals "$136B", "$169B", "$180B", "$214B" printed in black above each bar |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | f1 | **无** | arrow boxes at right edge label "REST OF WORLD" and "U.S." pointing at the 2029E segments |
| `total_row_below_axis` | 轴下方一行合计值，与类目对齐 | f1 | **无** | year labels "2019", "2021", "2025E", "2029E" under baseline; double-slash break glyphs also sit on the baseline |
| `icon_category_axis` | 类目轴用图标代替文字 | f1 | **无** | globe pictogram in the REST OF WORLD box, U.S. map pictogram in the U.S. box |

词表 65 项，本页出现 11 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `gap_annotation_between_bars` | f1 | CAGR circles "11%","10%","16%" sit on a grey vertical band between the 2019 and 2021 bars | 这些百分数不是柱体高度，而是相邻两柱之间的增长率标注，读值时必须按“起止年份对+系列”寻址，否则会被误当作某柱的数值。 |
| `axis_break_glyph_on_category_axis` | f1 | double-slash marks drawn on the horizontal baseline between adjacent year bars | none不截断而非数值轴截断，说明时间轴跳过2020、2022-2024，读者不能按等距年份插值。（时间不连续） |
| `forecast_badge` | f1 | "ACTIVATE FORECAST" logo badge placed inside the plot area top-left | 标明整图（含2025E/2029E）为预测数据，读值时需区分实际值与预测值。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

所有数值都以标签印在图上（$101B…$59B、10%/16%），且没有数值轴，所以第2步（读像素）几乎不成问题；难点在寻址。同一图里混着两类量纲：8个柱段是十亿美元，另外8个圆圈是CAGR百分比，且百分比的行标签（U.S./REST OF WORLD）只由箭头框在右侧给出、列标签是“2019-2021 CAGR:”这种跨列区间。要唯一定位“16”需要三个键（2019-2021、CAGR、U.S.），而黑色总CAGR圆（11%/2%/4%）与紫色分区圆共享同一列名，解析出的表格若不区分系列维度，4%会出现三次而无法辨别。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | 新组件 gap_annotation_between_bars（柱间增长率标注） | 记录字段增加 annotation 行类型，其寻址键为“起止类别对 + 系列”，与普通类别键并列 | 含/不含柱间区间标注的图：模型能否把区间百分比与柱值分表输出 |
| P6 | 一类出版方 | no_value_axis 与 value_label_inside/outside 的组合（全靠标签读数） | 样式条件行中加入“无数值轴+全部数值标签”配置 | 有轴刻度 vs 仅标签两种条件下取值精度对比 |
| P7 | 通用 | footnote_marker 与 unit_in_axis_or_title（标题横幅带¹与 BILLIONS USD） | 标题字段拆分：number/title/unit/footnote 分列，横幅式 placement=above | 单位位于横幅标题末尾时能否被写入表头单元 |
| P6 | 这份文档自己的习惯 | icon_category_axis / inline_series_labels（右侧带图标的系列箭头框代替图例） | 图例样式维度增加“右侧图标标注框”取值 | 图标式系列标注 vs 常规图例条件下系列名恢复率 |
| new | 一类出版方 | 新组件 axis_break_glyph_on_category_axis（类别轴上的双斜线断裂，年份跳跃） | 类别轴条件行加入“非等距/跳年”标志 | 时间轴不连续时是否仍按等距年份误插值 |
