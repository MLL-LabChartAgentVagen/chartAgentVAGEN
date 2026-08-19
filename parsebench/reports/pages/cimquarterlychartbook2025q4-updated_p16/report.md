# cimquarterlychartbook2025q4-updated_p16

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| cimquarterlychartbook2025q4-updated | `need_estimate` | 9 | 9 |

这是一页保险/投资类幻灯片，用三个上下排列的折线子图展示自1950年以来标普500的滚动5年、10年、15年年化回报率，右侧配一段说明文字。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 16.47 | `Rolling 5-Year Annualized Return (%)` · `2025` | 1% | f1 | the endpoint label of the 5-year line at 9/30/2025 | 是 | `Rolling S&P 500 Returns Since 1950` · `Rolling 5-Year Annualized Return (%)` · `2025` |
| 2 | 15.30 | `Rolling 10-Year Annualized Return (%)` · `2025` | 1% | f1 | the endpoint label of the 10-year line at 9/30/2025 | 是 | `Rolling S&P 500 Returns Since 1950` · `Rolling 10-Year Annualized Return (%)` · `2025` |
| 3 | 14.64 | `Rolling 15-Year Annualized Return (%)` · `2025` | 1% | f1 | the endpoint label of the 15-year line at 9/30/2025 | 是 | `Rolling S&P 500 Returns Since 1950` · `Rolling 15-Year Annualized Return (%)` · `2025` |
| 4 | 10.5 | `Rolling 5-Year Annualized Return (%)` · `1950` | 5% | f1 | the dashed black average line level in the top (5-year) panel, sitting just above the 10 tick | 否 | `Rolling 5-Year Annualized Return (%)` · `dashed black line` |
| 5 | 23 | `Rolling 5-Year Annualized Return (%)` · `1955` | 5% | f1 | a 5-year line peak around 1997-1998, read between the 20 and 30 ticks | 否 | `Rolling 5-Year Annualized Return (%)` · `1995` |
| 6 | 28 | `Rolling 5-Year Annualized Return (%)` · `2000` | 5% | f1 | the highest 5-year peak, around 1999-2000, just below the 30 tick | 否 | `Rolling 5-Year Annualized Return (%)` · `2000` |
| 7 | -1 | `Rolling 10-Year Annualized Return (%)` · `2010` | 20% | f1 | a 5-year trough below the grey zero line around 2002-2003 | 否 | `Rolling 5-Year Annualized Return (%)` · `2005` |
| 8 | 10 | `Rolling 15-Year Annualized Return (%)` · `1970` | 5% | f1 | the first plotted 5-year point at 1950, level with the 10 tick | 否 | `Rolling 5-Year Annualized Return (%)` · `1950` |
| 9 | 4.5 | `Rolling 15-Year Annualized Return (%)` · `2015` | 10% | f1 | the 15-year trough around 2015-2016, just below the 5 tick | 否 | `Rolling 15-Year Annualized Return (%)` · `2015` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 9 predicted key sets miss a rule label: 10.5, 23, -1, 10

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 3 | 3 | 300 | 900 | 部分 | top panel: 30, 20, 10, 0; middle panel: 25, 20, 15, 10, 5, 0, -5; bottom panel: 20, 15, 10, 5, 0 |

- **f1** Rolling S&P 500 Returns Since 1950　[图上方]　（标题里没有单位）
  - 来源行：Source: Cetera Investment Management, FactSet, Standard & Poor's. Total returns used. Past performance is not indicative of future results. Data as of 9/30/2025.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a dashed black horizontal rule near 11 in each panel; text: "average return ... represented by the dashed black line" |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | top and middle panels dip below the grey zero line; middle panel tick reads "-5" |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | top panel 0-30, middle -5 to 25, bottom 0-20 ticks |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | the 1950-2025 year ticks are drawn once, under the bottom panel only |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | three stacked panels of the same rolling-return line chart |
| `source_note_lines` | source / note 行在图下方 | page | 有 | "Source: Cetera Investment Management, FactSet, Standard & Poor's. ... Data as of 9/30/2025." under the chart |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | the swatch labels sit inside the bordered panel area, upper left of each panel |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | each panel carries its own swatch label, e.g. "Rolling 10-Year Annualized Return (%)" |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f1 | **无** | right-hand column of prose: "The chart shows the rolling 5, 10, and 15-year annualized returns..." |
| `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | f1 | **无** | legend entries end in "(%)": "Rolling 5-Year Annualized Return (%)" |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | teal numbers 16.47, 15.30, 14.64 printed beyond the right end of each line |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | quarterly points ("Returns are through the end of each quarter") but ticks only every 5 years |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | three panels of ~300 quarterly points each, 1950 to 2025 |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | faint vertical rules at the 5-year tick positions inside each panel; no horizontal rules |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | f1 | **无** | solid teal return line versus dashed black average line in the same panel |

词表 65 项，本页出现 15 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `slide_title_duplicates_figure_title` | page | "Rolling S&P 500 Returns Since 1950" printed as slide header and again bold inside the chart frame | 同一标题出现两次，解析后表格上方可能有两级重复标题，需判定哪一处是图题以正确定位面板与数值。 |
| `unlabelled_reference_line` | f1 | dashed black average line has no legend entry or value label; only the side text explains it | 该虚线的数值（约11）无任何印刷标签，只能靠像素读取，且无行名可寻址。 |
| `endpoint_latest_value_label` | f1 | only the final quarterly point of each line carries a number: 16.47, 15.30, 14.64 | 三条线里只有最后一个点有精确数字，其余全靠刻度估读，寻址时须区分“最新值”与其余点。 |
| `figure_frame_border` | f1 | a thin rectangle encloses title, all three panels and the year axis as one chart object | 框线界定了图与右侧文字列的边界，决定标题是否被算作图内文本。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

六个未印刷的值都要在极密的季度折线上读像素：底部面板刻度间隔为5（0,5,10,15,20），要把4.5读到±0.225（5%容差）几乎是一两个像素的事；顶部面板刻度更粗，间隔10（0,10,20,30），读23或28的容差只有±1.15/±1.4，且无水平网格线可插值，只有一条零线和一条虚线均值线。横轴每5年一格而数据为季度，2002-2003的-1谷值连年份都难以指定（-1的5%容差为±0.05，实际不可能达到）。相比之下面板名（三个legend文字）足以寻址，标题也在图框内，所以卡点在数值读取而非标签。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | per_panel_axis_range 与 panel_key 结合：同一图三个面板刻度分别为0-30、-5-25、0-20 | 记录字段中为每个面板单独存 axis_min/axis_max，并在行键中加入 panel 名（如“Rolling 10-Year Annualized Return (%)”） | 新增一行“跨面板不同量程时，是否强制行键带面板名”，对比不带面板名的抽取准确率 |
| P6 | 一类出版方 | unlabelled_reference_line（无图例的虚线均值线） | 样式条件行中增加“参考线是否带图例/数值标注”开关 | 新增一行“参考线有标注 vs 无标注”，检验模型能否输出该线的数值行 |
| P6 | 一类出版方 | endpoint_latest_value_label（只标最后一个点的 value_label_outside） | 标签放置样式字段增加 value_label_scope = last_point_only | 新增一行“全部点标注 / 仅末点标注 / 全无标注”三档，量化印刷标签比例对可读性的影响 |
| P5 | 通用 | dense_marks_100plus（每面板约300个季度点、全图约900个marks） | 密度上限参数从当前上限提升，并允许 marks 以“不可逐点寻址的连续序列”标记 | 新增一行“每序列点数 30 / 120 / 300 时的每点可达精度” |
| P7 | 这份文档自己的习惯 | slide_title_duplicates_figure_title 与图框内标题 | 标题块字段拆分：page_title 与 figure_title 分开存放，并记录 placement=above(inside frame) | 新增一行“页标题与图题重复时，表格上方以哪一级标题作为上下文” |
