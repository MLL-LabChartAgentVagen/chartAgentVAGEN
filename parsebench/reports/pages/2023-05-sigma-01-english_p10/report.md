# 2023-05-sigma-01-english_p10

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2023-05-sigma-01-english | `need_estimate` | 10 | 10 |

本页为 Swiss Re Institute sigma 1/2023 第10页，正文讨论自然灾害保险损失长期上升趋势，中部为 Figure 6：1992–2022 年全球自然灾害保险损失的堆叠柱状图叠加虚线趋势线。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 50 | `1992` · `Weather-related` | 5% | f1 | a y-axis tick label '50', and roughly the 2008 Weather-related bar top | 是 | `Figure 6` · `Weather-related` |
| 2 | 27 | `1994` · `Earthquakes` | 10% | not_found | no printed 27; could be a mid-1990s bar height but not resolvable to within 5% between 25 and 50 gridlines | 否 | — |
| 3 | 72 | `2004` · `Weather-related` | 10% | not_found | no printed value; possibly the 2011 Earthquakes segment top (~65-70) but not distinguishable at 5% tolerance | 否 | — |
| 4 | 155 | `2005` · `Weather-related` | 5% | f1 | the 2011 total bar (Earthquakes + Weather-related), just above the 150 gridline | 否 | `Figure 6` · `2012` · `Weather-related` · `Earthquakes` |
| 5 | 70 | `2011` · `Earthquakes` | 10% | f1 | the 2005 Weather-related bar lower portion / the 2011 Earthquakes segment near 65-70 | 否 | `Figure 6` · `Earthquakes` |
| 6 | 80 | `2011` · `Weather-related` | 10% | f1 | the 2012 bar top, just above the 75 gridline; also the 2018 bar near 90 | 否 | `Figure 6` · `2012` · `Weather-related` |
| 7 | 169 | `2017` · `Weather-related` | 5% | f1 | the 2017 bar, the tallest in the series, between 150 and 175 gridlines | 否 | `Figure 6` · `2018` · `Weather-related` |
| 8 | 95 | `2021` · `Trend` | 10% | f1 | the 2018 bar top, between the 75 and 100 gridlines | 否 | `Figure 6` · `2018` · `Weather-related` |
| 9 | 123 | `2022` · `Weather-related` | 5% | not_found | appears only in body text 'Verisk recently modeled the global insured average annual loss as USD 123 billion', not on the figure | 否 | — |
| 10 | 100 | `2022` · `Trend` | 10% | f1 | a y-axis tick label '100'; also body text 'more than USD 100 billion' | 是 | `Figure 6` |

**程序核对**（模型没有看到左半的标签列）：

- 有值没能落到任何一个图元上——3 of 10 values could not be put on a mark
- 模型预测的定位标签漏掉了规则实际用的标签——7 of 10 predicted key sets miss a rule label: 50, 155, 70, 80, 169, 95

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 3 | 31 | 93 | 无 | 0, 25, 50, 75, 100, 125, 150, 175, 200 |
| f1 | `compound` | vertical | 1 | 3 | 31 | 93 | 无 | 0, 25, 50, 75, 100, 125, 150, 175, 200 |

- **f1** Figure 6 / Growth in global natural catastrophe insured losses in USD billion (2022 prices)　[图上方]　单位 `USD billion (2022 prices)`
  - 来源行：Source: Swiss Re Institute
- **f1** Figure 6 / Growth in global natural catastrophe insured losses in USD billion (2022 prices)　[图上方]　单位 `USD billion (2022 prices)`
  - 来源行：Source: Swiss Re Institute

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | dark teal Earthquakes segments sit under light green Weather-related within one bar per year |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | dotted magenta Trend line drawn over the stacked bars in the same panel |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: Swiss Re Institute' printed under the legend |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Earthquakes  Weather-related  ...  Trend' row sits below the year axis |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | blue pull quotes 'We expect that average insured losses...' run in a left column beside body text |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title reads 'insured losses in USD billion (2022 prices)'; axis ticks are bare 0-200 |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | superscript 14 after 'USD 123 billion' with note '14 Global Modelled Catastrophe Losses, Verisk, 2022.' |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | bars appear yearly but ticks read 1992, 1994, 1996 ... 2022 every two years |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | whole figure block sits on a pale blue tint behind the plot area |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 25, 50, 75 ... 200 across the panel; no vertical rules |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | f1 | **无** | legend shows 'Trend' as a dotted line beside two filled square swatches |

词表 65 项，本页出现 11 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `year_axis_ticks_offset_from_bars` | f1 | 31 yearly bars but ticks only on even years; bars sit between labelled positions | 读取某一年（如2005或2011峰值）的数值时必须在两个刻度间数柱子，容易错位一年。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

网格线间距为25 USD billion，而5%容差在80附近仅约±4，即约六分之一格；柱顶多落在格线之间（如2017年约169、2018年约95），必须靠像素插值才能达标。加上31根柱子只有16个偶数年刻度，还要区分同一柱内极薄的 Earthquakes 深色段（1994、2010、2011、2016），定位与读值双重误差叠加，比缺表或缺标签更致命。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 一类出版方 | stacked_bar 中极薄底段（Earthquakes 仅在少数年份出现）的建模 | 记录字段：允许某序列在多数类别上为0或缺失，样式字段控制最小可见段高 | “稀疏序列段占总高<10%”一行，对比模型能否正确归属薄段数值 |
| P6 | 通用 | sparse_time_ticks（每两年一刻度、逐年数据） | 条件行：时间轴刻度密度与数据点密度之比作为独立变量 | “刻度数<类别数”一行，检验按年定位单根柱的正确率 |
| P7 | 通用 | 标题内含单位与价格基准 'in USD billion (2022 prices)' | P7 的 heading 结构：number/title/unit 分离，unit 嵌在 title 句中而非独立行 | “单位仅存在于标题句内、值轴为裸数字”一行 |
| P4 | 通用 | mixed_marks + dashed_line_series（柱上叠虚线趋势线，同一值轴） | 样式字段：允许一个 series 以点线形式渲染并共享左侧轴 | “同轴柱线混合，其中线为虚线”一行，检验趋势序列是否被误当作数据柱 |
