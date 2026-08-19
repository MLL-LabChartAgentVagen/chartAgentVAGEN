# Goldman_Sachs_BUY_report_p6

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Goldman_Sachs_BUY_report | `need_estimate` | 10 | 10 |

该页为报告第6页,标题“Business overview and drivers”,主体是“Exhibit 1 – GS revenue driver dashboard”,由F1–F6六个带边框小图组成的折线图仪表盘,每个小图有自己的图例、纵轴刻度和“Performance indexed to 100”副标题。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 70 | `FY2014` · `DCM deal value` | 10% | f1 | the FY2014 local peak of the 'DCM deal value' line in panel F1 | 否 | `F1: IB: DCM revenues` · `DCM deal value` · `FY2014` |
| 2 | 200 | `FY2010` · `Global IPO deal count` | 10% | f1 | the 'Global IPO deal count' line around FY2012 in panel F2, level with the '200' gridline | 否 | `F2: IB: ECM revenues` · `Global IPO deal count` · `FY2012` |
| 3 | 195 | `FY2015` · `Global IPO value` | 10% | f1 | the end-of-series point of 'Global IPO value' at the right edge of panel F2 | 否 | `F2: IB: ECM revenues` · `Global IPO value` · `FY2015` |
| 4 | 130 | `FY2015` · `Global M&A deal count` | 10% | f1 | the 'US corporate profits' line crossing the 130 level around FY2010 in panel F4 | 否 | `F4: IB: Overall investment banking revenues` · `US corporate profits` · `FY2010` |
| 5 | 74 | `FY2013` · `GS Financial advisory revenue` | 10% | f1 | a trough of 'Interest rate (US 10yr)' near FY2012 in panel F5, between the 50 and 100 gridlines | 否 | `F5: ICS: FICC revenues` · `Interest rate (US 10yr)` · `FY2012` |
| 6 | 60 | `FY2011` · `GS investment banking revenues` | 10% | f1 | the early dip of 'GS FICC revenues' near FY2010 in panel F5 | 否 | `F5: ICS: FICC revenues` · `GS FICC revenues` · `FY2010` |
| 7 | 155 | `FY2014` · `US corporate profits` | 10% | f1 | the FY2014 peak of 'US corporate profits' in panel F4, just above the 150 gridline | 否 | `F4: IB: Overall investment banking revenues` · `US corporate profits` · `FY2014` |
| 8 | 50 | `FY2014` · `High yield spread (inverted)` | 20% | f1 | a low point of 'GS FICC revenues' around FY2013 in panel F5, at the 50 gridline | 否 | `F5: ICS: FICC revenues` · `GS FICC revenues` · `FY2013` |
| 9 | 80 | `FY2011` · `GS FICC revenues` | 10% | f1 | the flat stretch of 'GS Financial advisory revenue' near FY2010-FY2011 in panel F3 | 否 | `F3: IB: Financial advisory revenues` · `GS Financial advisory revenue` · `FY2010` |
| 10 | 245 | `FY2011` · `Vix index` | 10% | f1 | the tall FY2011 spike of the 'Vix index' line in panel F6, above the 240 gridline | 否 | `F6: ICS: Equities revenues` · `Vix index` · `FY2011` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——6 of 10 predicted key sets miss a rule label: 200, 130, 74, 60, 50, 80

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 6 | 17 | 8 | 450 | 无 | F1: 200, 150, 100, 50, --; F2: 400, 300, 200, 100, --; F3: 225, 175, 125, 75, 25; F4: 170, 150, 130, 110, 90, 70, 50; F5: 200, 150, 100, 50, --; F6: 240, 190, 140, 90, 40 |

- **f1** Exhibit 1 / GS revenue driver dashboard / Performance indexed to 100　[图上方]　单位 `Performance indexed to 100`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | F1 tops at 200, F2 at 400, F3 runs 25-225, F4 50-170, F6 40-240 |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest ticks are '25' in F3, '50' in F4, '40' in F6 with no axis break drawn |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f1 | **无** | six boxed line panels F1 through F6 under one heading 'Exhibit 1 – GS revenue driver dashboard' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legends sit under each plot, below the FY tick row, inside the panel frame |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | each panel has its own legend row, e.g. 'Interest rate (US 10yr)', 'High yield spread (inverted)', 'GS FICC revenues' |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | each box carries its own name in the frame: 'F1: IB: DCM revenues', 'F5: ICS: FICC revenues' |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axes show bare numbers (200, 150, 100, 50); scale only from 'Performance indexed to 100' above the plot |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | every panel subtitled 'Performance indexed to 100' |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | F2, F3 and F4 print 'FY2008'...'FY2015' turned about 45 degrees |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | time axis labelled 'FY2012', 'FY2013', 'FY2014', 'FY2015' rather than calendar years |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | lines carry roughly four points per year but ticks read only FY2008 ... FY2015 |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each tick level in every panel, no vertical rules |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | six panels x up to 3 series x quarterly points over 4-8 fiscal years, several hundred plotted points |

词表 65 项，本页出现 13 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `zero_tick_as_dash` | f1 | in F1, F2 and F5 the bottom axis label is printed '--' instead of '0' | 最低刻度不是数字,读者需推断“--”代表0才能按比例换算纵轴位置,否则整段线的取值会被系统性抬高或压低。 |
| `panel_title_in_frame_gap` | f1 | each panel's border is interrupted at top-left by its caption, e.g. 'F3: IB: Financial advisory revenues' | 面板名嵌在边框缺口中而非普通标题行,解析器易把它当边框装饰丢弃,导致取值缺少面板键。 |
| `index_base_period_unstated` | f1 | 'Performance indexed to 100' given, but no base date such as 'FY2008 = 100' anywhere | 指数基期缺失,同一数值在不同面板(起点FY2008或FY2010)含义不同,跨面板对照读数会错。 |
| `transform_noted_in_series_name` | f1 | legend entry 'High yield spread (inverted)' states the series is plotted inverted | 该系列数值方向被反转,读出的100不代表原始利差水平,必须连同括注一起报告。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

取值最难。全页没有任何数字标签,F1/F5网格间距为50个指数点,5%容差对70这类值只有±3.5,即不到网格间距的1/14;F2跨度到400,单条网格代表100,读195须精确到±10以内。更糟的是三条折线在F3、F5中反复交叉重叠且颜色仅深蓝/中蓝/浅蓝三级,单点归属难辨;时间轴只有年度FY刻度而数据是季度点,想把某个峰值定位到具体季度也只能估算,使读数与标签同时失准。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | per_panel_axis_range 与 small_multiples_5plus 组合(6面板各自不同轴范围) | 条件行中加入 panel_key 维度,记录字段为每面板单独的 axis_min/axis_max | “同图多面板且各面板轴范围不同”对照“各面板共享轴”,比较取值命中率 |
| P6 | 这份文档自己的习惯 | new_components 中的 zero_tick_as_dash(最低刻度写作“--”) | 样式字段 tick_format 增加 zero_label 选项(0 / -- / 空) | “零刻度以破折号呈现”对照“零刻度写0”,检验基线定位误差 |
| P3 | 这份文档自己的习惯 | panel_title_per_panel + Exhibit 编号/副标题的三层拆分(Exhibit 1 – 标题、F1: … 面板名、Performance indexed to 100) | 记录字段将 heading 拆为 number/title/panel_name/unit,并规定面板名相对表格的位置 | “面板名写在边框缺口中”对照“面板名作为加粗标题行”,比较上下文键的可检索性 |
| P5 | 通用 | sparse_time_ticks 的加强版:季度数据点仅有年度刻度 | 条件行的时间轴设置增加 tick_every 与 points_per_tick 两个参数 | “每刻度含4个数据点”对照“每点一刻度”,检验时间键能否唯一定位一个点 |
| P7 | 一类出版方 | rebased_index_values 且基期缺失(index_base_period_unstated) | heading 的 unit_text 字段允许“有基值无基期”的取值 | “指数标注含基期”对照“仅标注indexed to 100”,检验跨面板数值解释一致性 |
