# SRI-Insights-August 2025_media_embargo_p4

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| SRI-Insights-August 2025_media_embargo | `need_estimate` | 10 | 10 |

这是瑞再研究院报告第4页，左右两栏正文之间嵌有三幅浅蓝底图：Figure 6（上半年雷暴损失柱状+趋势线）、Figure 7（上下半年占比堆叠面积）和 Figure 8（按季度与灾种的平均损失堆叠柱，并在柱上标注份额百分比）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 45 | `2023` · `First half SCS` | 10% | f1 | the taller of the two peak bars near 2022/2023, top just under the 45 mid-grid (≈43–44) | 否 | `First half SCS` · `Figure 6:` |
| 2 | 45 | `2024` · `First half SCS` | 10% | f1 | the second peak bar of the adjacent pair near 2022/2023, same height as its neighbour | 否 | `First half SCS` · `Figure 6:` |
| 3 | 33 | `2024` · `Trend` | 10% | f1 | the isolated tall bar around 2011, top level with the 33 line between grids 30 and 40 | 否 | `First half SCS` · `Figure 6:` |
| 4 | 32 | `2025` · `First half SCS` | 10% | f1 | the last bar, at the 2025 tick, top just above the 30 grid line | 否 | `First half SCS` · `2025` |
| 5 | 35 | `2025` · `Trend` | 10% | f1 | the right-hand end point of the "Trend" curve at 2025 | 否 | `Trend` · `2025` |
| 6 | 70% | `1996` · `First half` | 10% | f2 | a "First half" band top in the mid-1990s/early years sitting near the 70 level | 否 | `First half` · `1996` |
| 7 | 80% | `2024` · `First half` | 10% | f2 | a "First half" band peak year whose top reaches about 80 (one of the high spikes) | 否 | `First half` · `Figure 7:` |
| 8 | 12 | `Convective storms` · `2Q (22%)` | 15% | f3 | the total height of the 1Q stack (≈12, the 18% share bar) | 否 | `1Q` · `18%` |
| 9 | 22 | `Cyclones` · `3Q (44%)` | 10% | f3 | the share label "22%" printed above the 2Q stack | 是 | `2Q` · `22%` |
| 10 | 2 | `Earthquakes` · `4Q (16%)` | 20% | f1 | one of the smallest early bars (mid/late 1990s and around 2005), barely above the zero baseline | 否 | `First half SCS` · `1997` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——7 of 10 predicted key sets miss a rule label: 45, 45, 33, 80%, 12, 22

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 31 | 62 | 无 | 0, 10, 20, 30, 40, 50 |
| f2 | `area` | vertical | 1 | 2 | 29 | 58 | 无 | 0, 20, 40, 60, 80, 100 |
| f3 | `stacked_bar` | vertical | 1 | 4 | 4 | 16 | 部分 | 0, 5, 10, 15, 20, 25, 30, 35 |

- **f1** Figure 6: / Global insured losses from SCS in 1H (USD bn, 2025 prices)　[图上方]　单位 `USD bn, 2025 prices`
  - 来源行：Source: Swiss Re Institute
- **f2** Figure 7: / Global insured losses from SCS in 1H and 2H, %　[图上方]　单位 `%`
  - 来源行：Source: Swiss Re Institute
- **f3** Figure 8: / Average global insured losses (USD billion), and share of losses (%), from natural catastrophes by quarter and peril (1995–2024; 2025 prices)　[图上方]　单位 `USD billion`
  - 来源行：Source: Swiss Re Institute

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f3 | 有 | each quarter bar stacks Convective storms, Cyclones, Earthquakes, Floods segments |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f2 | **无** | bands fill to the 100 tick every year on an axis reading 0 to 100, title ends ", %" |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | dark teal bars plus a light green rising "Trend" line in the same panel |
| `stacked_area` | 堆叠面积 | f2 | 有 | dark "First half" band with light "Second half" band stacked over the year axis |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | three separately captioned figures: "Figure 6:", "Figure 7:", "Figure 8:" on one page |
| `source_note_lines` | source / note 行在图下方 | page | 有 | "Source: Swiss Re Institute" printed in small type under each of the three figures |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | "First half SCS" square and "Trend" line swatch in a row under the x axis |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | "First half" and "Second half" swatches in a row under the 1996–2024 axis |
| `legend_below_plot` | 图例在绘图区下方 | f3 | 有 | four swatches "Convective storms  Cyclones  Earthquakes  Floods" under the 1Q–4Q axis |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f3 | **无** | left column body text ("June marks the end...") runs level with Figure 8 in the right column |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis shows bare 0, 10 ... 50; scale only in title "(USD bn, 2025 prices)" |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | title "Global insured losses from SCS in 1H and 2H, %"; axis ticks are bare numbers |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f3 | **无** | caption carries "(USD billion)" and "2025 prices"; axis is bare 0–35 |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f3 | **无** | "18%", "22%", "44%", "16%" printed above the tops of the four stacks |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f3 | **无** | category axis reads "1Q", "2Q", "3Q", "4Q" with no year |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | about 31 yearly bars but ticks only 1997, 2001, 2005 ... 2025 |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f2 | 有 | yearly jagged vertices but ticks only at 1996, 2000, 2004 ... 2024 |
| `panel_background` | 绘图区带底色，不是白底 | page | **无** | each figure sits in a pale blue tinted block that includes the plot area, not white |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 10, 20, 30, 40, 50 only; no vertical rules |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f3 | 有 | horizontal rules at 5, 10 ... 35 across the panel, no vertical rules |

词表 65 项，本页出现 14 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `label_unit_differs_from_axis` | f3 | axis is USD billion 0–35 but printed labels 18%, 22%, 44%, 16% are shares of annual losses | 同一图上柱高与标签是两种量纲，读数时必须先判定 44% 不是 USD bn，而 30 左右的柱高才是金额，否则会把百分比当成数值填入表格。 |
| `trend_series_without_own_axis_or_points` | f1 | "Trend" is a smooth fitted curve with no markers, legend swatch is a line, same axis as bars | 趋势线没有可对齐的年度点位，取其 2025 年末端值（约35）只能靠曲线与网格线交点估读，行标签也只能借用柱子的年份刻度。 |
| `caption_number_inline_with_title` | page | "Figure 6:" in bold blue runs inline with the lighter-blue title on the same tinted line | 图号与标题同一行且同色系，解析出的markdown可能把二者合并成一段普通文字，导致表格上方缺少可识别的粗体标题。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

十个待测值中有八个没有印在图上。Figure 6 的价值轴只有 0,10,20,30,40,50 六个刻度，10 个单位约 50 px，要把顶峰柱读成 45（±2.25，即约 11 px）几乎落在描线粗细的量级内，实际柱高约 43–44，已接近 5% 边界；33 与 32 两根柱在同图上仅差 5 px，一次误判就同时报废两条记录。Figure 7 是 0,20,40,60,80,100 的百分比面积图，20 个单位约 50 px，读 70%/80%（±3.5 与 ±4）需要在无网格的绿色/深青分界上估位，而且 29 个年度顶点只配 8 个四年间隔刻度，还要先确定是哪一年。相比之下标签问题（步骤3）虽然存在——Figure 6 顶峰柱对应的 2023 年份在页面上根本没印——但数值本身能否落进 5% 已是更前置的阻塞。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 label_unit_differs_from_axis（柱上百分比标签 + USD bn 价值轴） | 样式字段中新增 value_label_unit，与 value_axis_unit 独立取值；记录字段区分 mark 数值与其标注文本 | 「标签量纲=轴量纲」对照「标签量纲≠轴量纲」时的数值抽取正确率 |
| P4 | 一类出版方 | pct_stacked 的面积形态（归一化堆叠面积到 100） | 图族权重向量中把 stacked_area 拆为 absolute 与 normalized 两档 | 归一化堆叠面积图在生成分布中占比 0% 与占比 10% 两种训练配置的对比行 |
| P7 | 通用 | 三行折行标题、图号内联、单位嵌在括号中（Figure 8 的 heading 拆分） | 标题记录拆成 number/title/subtitle/unit/placement 五字段，并允许 title 折行且 number 与 title 同行同色 | 标题为单行与折行三行（单位在括号内）两种情况下，表格上方能否输出可检索粗体标题 |
| P6 | 通用 | sparse_time_ticks（31 根年度柱只有每四年一个刻度） | 刻度格式样式维度增加 tick_every_n 参数，并要求记录保留未印出的类别名 | 每点一刻度与每四点一刻度时，按类别定位单个柱值的命中率 |
