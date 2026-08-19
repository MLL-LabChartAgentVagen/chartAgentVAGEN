# sri-sigma-natural-catastrophes-1-2025_p26

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| sri-sigma-natural-catastrophes-1-2025 | `need_estimate` | 7 | 7 |

瑞士再保险sigma报告第26页附录，含两幅全宽图（Figure 16 灾难事件数量、Figure 17 受害者人数），均为绿色柱（人为灾难）+ 深色折线（自然巨灾）组合，Figure 17 使用对数纵轴并带7个事件注释框。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 228 | `2024` · `Natural catastrophes` | 5% | f1 | the 2024 point of the Natural catastrophes line (also stated in body text) | 否 | `Figure 16` · `Number of catastrophic events, 1970 – 2024` · `Natural catastrophes` · `2024` |
| 2 | 108 | `2024` · `Man-made disasters` | 10% | f1 | the 2024 Man-made disasters bar (also stated in body text) | 否 | `Figure 16` · `Number of catastrophic events, 1970 – 2024` · `Man-made disasters` · `2024` |
| 3 | 219 | `2023` · `Natural catastrophes` | 5% | f1 | the 2023 point of the Natural catastrophes line (also stated in body text) | 否 | `Figure 16` · `Number of catastrophic events, 1970 – 2024` · `Natural catastrophes` · `2023` |
| 4 | 115 | `2023` · `Man-made disasters` | 10% | f1 | the 2023 Man-made disasters bar (also stated in body text) | 否 | `Figure 16` · `Number of catastrophic events, 1970 – 2024` · `Man-made disasters` · `2023` |
| 5 | 260 | `2005` · `Man-made disasters` | 10% | f1 | the tallest Man-made disasters bar, at the mid-2000s slot near 2005, whose top sits just above the 250 gridline | 否 | `Figure 16` · `Number of catastrophic events, 1970 – 2024` · `Man-made disasters` · `2006` |
| 6 | 10 822 | `2024` · `Natural catastrophes` | 10% | f2 | the 2024 endpoint of the Natural catastrophes line, just above the 10 000 gridline (also stated in body text) | 否 | `Figure 17` · `Number of victims, 1970 - 2024` · `Natural catastrophes` · `2024` |
| 7 | 5 261 | `2024` · `Man-made disasters` | 10% | not_found | no such number on the page; the text gives 3 261 man-made victims for 2024, and no mark can be read as 5 261 | 否 | — |

**程序核对**（模型没有看到左半的标签列）：

- 有值没能落到任何一个图元上——1 of 7 values could not be put on a mark
- 模型预测的定位标签漏掉了规则实际用的标签——1 of 7 predicted key sets miss a rule label: 260

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 55 | 110 | 无 | 0, 50, 100, 150, 200, 250, 300 |
| f2 | `compound` | vertical | 1 | 2 | 55 | 110 | 无 | 1 000, 10 000, 100 000, 1 000 000, 10 000 000 |

- **f1** Figure 16 / Number of catastrophic events, 1970 – 2024　[图上方]　（标题里没有单位）
  - 来源行：Sources: Swiss Re Institute
- **f2** Figure 17 / Number of victims, 1970 - 2024　[图上方]　（标题里没有单位）
  - 来源行：Note: Scale is logarithmic: the number of victims increases tenfold per band. Source: Swiss Re Institute

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | green bars for "Man-made disasters" with a dark line "Natural catastrophes" over the same panel |
| `mixed_marks` | 同面板混合图元（bar + line） | f2 | 有 | teal bars plus a blue line in one panel, legend "Man-made disasters" / "Natural catastrophes" |
| `log_axis` | 对数轴 | f2 | 有 | ticks 1 000, 10 000, 100 000, 1 000 000, 10 000 000 equally spaced; note says "Scale is logarithmic" |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f2 | **无** | seven boxed notes over the plot, e.g. "2004: Indian Ocean Earthquake and tsunami", with thin leader lines to peaks |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f2 | **无** | lowest tick and bar baseline is 1 000, no axis break glyph drawn |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | "Figure 16" and "Figure 17" with separate captions and source lines on one page |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Sources: Swiss Re Institute" in small print under the legend |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | "Note: Scale is logarithmic: ... Source: Swiss Re Institute" under the legend |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | green square "Man-made disasters" and line swatch "Natural catastrophes" row under the x axis |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | legend row "Man-made disasters   Natural catastrophes" sits below the 1970-2024 axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | y axis reads bare 0, 50 ... 300; only the title says "Number of catastrophic events" |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | axis shows bare 1 000 ... 10 000 000; "Number of victims" appears only in the title |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | yearly bars 1970-2024 but ticks printed every three years: 1970, 1973, 1976 ... |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f2 | 有 | one bar per year, tick labels only 1970, 1973, 1976 ... 2024 |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole figure block including the plot area sits on a pale blue tint |
| `panel_background` | 绘图区带底色，不是白底 | f2 | **无** | plot area drawn on the same pale blue tinted block as the heading |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 50,100,150,200,250,300 across the panel, no vertical rules |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | horizontal rules at each decade band, no vertical grid lines |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 55 yearly bars plus 55 line points in one panel |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f2 | **无** | 55 yearly bars plus a 55-point line across 1970-2024 |

词表 65 项，本页出现 12 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `callout_year_prefixed_event_label` | f2 | each box begins with the year, e.g. "1976: Tangshan Earthquake, China", identifying the x slot it points at | 注释框本身携带年份键，读值时要用框内年份把引线锚回具体年份的折线点，而不是靠框的水平位置。 |
| `note_and_source_in_one_line` | f2 | single small-print line combines "Note: Scale is logarithmic: ..." and "Source: Swiss Re Institute" | 轴的刻度含义写在与来源同一行的说明里，解析时若只抓Source行会丢掉对数轴信息，导致读数被当成线性。 |
| `legend_glyph_matches_mark_type` | f1 | legend uses a filled square for the bar series and a short line stroke for the line series | 图例形状区分柱与线两种标记，判断某个数值属于柱还是折线要靠图例字形而非颜色。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

读数精度是瓶颈。Figure 16 纵轴刻度间隔50，5%容差对108只有±5.4，相当于要在一格刻度里判到1/10；而55根柱挤在约1000px宽的面板里，每根柱不足12px，2023与2024相邻柱几乎无法区分顶端。Figure 17 更严重：一个十倍带宽约85px，10 822与10 000在像素上相差不到2px，5%容差在对数轴上等于不到1.8px的垂直位移，肉眼与解析器都无法达到；而且图上完全没有数值标签（values_printed=none），唯一可核对的数字只存在于正文段落里。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 一类出版方 | log_axis 与 axis_starts_above_zero 组合（对数轴基线为1 000） | 样式条件行中的 value_axis 设置：增加 scale=log 且 baseline=首个十倍刻度的选项，并在记录字段写入刻度带含义 | 对数轴 vs 线性轴下每个标记可达精度的对比行（同一数据、同一像素高度） |
| new | 一类出版方 | annotation_callout 的引线式事件注释框（框内含年份） | 图形层增加 callout 记录字段：文本、目标(series, category)、框位置与引线 | 有/无覆盖式注释框时，被遮挡标记的读值与定位成功率行 |
| P4 | 通用 | mixed_marks（柱+线同轴）与图例字形随标记类型变化 | 图族权重向量中提高 bar+line 复合图的抽样比例，并在图例样式字段记录字形类型 | 复合图（柱+线）占比从低到高时，series 归属判定错误率行 |
| P7 | 通用 | 标题拆分为 figure_number / title / 年份区间，且单位只存在于标题（unit_in_axis_or_title） | 记录的 heading 字段拆成五段，导出markdown时把 "Figure 16" 作为粗体行置于表格上方 | 表外标题以粗体/普通文本呈现时，context 命中率对比行 |
| P5 | 通用 | dense_marks_100plus + sparse_time_ticks（55年逐年标记、每3年一刻度） | 密度上限参数与x轴刻度抽稀比例作为可控变量 | 刻度抽稀比(1:1 / 1:3)与标记密度(≤50 / ≥110)交叉的定位误差行 |
