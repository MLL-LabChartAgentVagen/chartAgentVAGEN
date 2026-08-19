# Whatnextfortheglobalcarindustry_p31

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Whatnextfortheglobalcarindustry | `need_estimate` | 10 | 10 |

这一页是IEA报告第31页正文加一幅无编号的双轴折线图，展示1964-1984年日本汽车在美进口占比与实际WTI油价，并在图内标注政治事件里程碑。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 22 | `Japanese imports as share of demand` · `1980` | 5% | f1 | the red import-share line at its 1980 peak, read on the left axis | 否 | `Japanese imports as share of demand` · `1980` |
| 2 | 145 | `WTI price` · `1980` | 5% | f1 | the blue WTI line at its 1980 spike, read on the right axis | 否 | `WTI price` · `1980` · `USD (2024)/bbl` |
| 3 | 8 | `Japanese imports as share of demand` · `1974` | 10% | f1 | the red import-share line on its plateau around 1976 | 否 | `Japanese imports as share of demand` · `1976` |
| 4 | 62 | `WTI price` · `1974` | 1% | f1 | the blue WTI line around 1976, between the 60 and 80 right-axis ticks | 否 | `WTI price` · `1976` · `USD (2024)/bbl` |
| 5 | 6 | `Japanese imports as share of demand` · `1970` | 10% | f1 | the red import-share line at its 1973 plateau just above 5% | 否 | `Japanese imports as share of demand` · `1973` |
| 6 | 25 | `WTI price` · `1970` | 1% | f1 | the top left-axis tick label "25%"; no drawn mark reaches it | 是 | `25%` |
| 7 | 18 | `Japanese imports as share of demand` · `1984` | 5% | f1 | the red import-share line on its steep 1979 rise, between 15% and 20% | 否 | `Japanese imports as share of demand` · `1979` |
| 8 | 95 | `WTI price` · `1984` | 5% | f1 | the blue WTI line around 1983, between the 80 and 100 right-axis ticks | 否 | `WTI price` · `1983` · `USD (2024)/bbl` |
| 9 | 7 | `Japanese imports as share of demand` · `1972` | 1% | f1 | the red import-share line around 1975, between the 5% and 10% ticks | 否 | `Japanese imports as share of demand` · `1975` |
| 10 | 75 | `WTI price` · `1978` | 5% | f1 | the blue WTI line at the 1984 right-hand end, just below the 80 tick | 否 | `WTI price` · `1984` · `USD (2024)/bbl` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——8 of 10 predicted key sets miss a rule label: 8, 62, 6, 25, 18, 95

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 2 | 11 | 254 | 无 | 0%, 5%, 10%, 15%, 20%, 25% (left); 0, 20, 40, 60, 80, 100, 120, 140, 160 (right) |

- **f1** Japanese car imports in the United States, oil price and political milestones, 1964-1984　[图上方]　单位 `USD (2024)/bbl`
  - 来源行：Sources: IEA analysis based on USITC (1985), FRED (2025).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | left axis reads 0%-25%, right axis reads 0-160 with title "USD (2024)/bbl" |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | two vertical dashed rules drawn at about 1971 and 1980 inside the plot |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | "10% Emergency Import Surcharge", "Voluntary Export Restrictions", "Honda Factory", "Toyota-GM JV" with arrows over plot |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Notes: JV = joint venture. WTI = West Texas Intermediate..." and "Sources: IEA analysis based on..." |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | "Japanese imports as share of demand" and "WTI price" in a row under the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | right axis bare numbers 0-160 get their scale only from "USD (2024)/bbl" |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "USD (2024)/bbl" set vertically along the right axis |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | ticks every two years 1964...1984 while the blue line moves month to month |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | plot area carries the same pale blue tint as the surrounding boxed section, not white |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | the WTI line has hundreds of sub-annual vertices across 1964-1984 |

词表 65 项，本页出现 10 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `event_marker_point_with_arrow` | f1 | two black square markers near 1982 and 1983, each tied by an arrow to "Honda Factory" / "Toyota-GM JV" | 这些方块不是任何图例系列的数据点，读值时必须判断它们只标事件时间而非纵轴数值，否则会误当第三系列去读高度。 |
| `percent_and_level_series_split_by_axis` | f1 | red series read as % on left, blue series read as USD/bbl on right, no per-series unit label | 两条线单位不同却无系列内单位标注，取值前必须先把系列绑定到正确的轴，否则数量级完全错。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，两条线都得靠像素对轴。右轴刻度间距是20 USD，5%容差对62来说只有约3 USD，即刻度间距的六分之一；左轴刻度间距5个百分点，5%容差对8%只有0.4个百分点，约刻度间距的十二分之一。加上横轴每两年一个刻度而蓝线是月度锯齿（1980前后一年内从120冲到145再回落），要定位某一年的点还得在刻度间插值，读数误差远超容差。相比之下系列只有两个、标签只需“系列+年份”两键，寻址不是瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | dual_axis 与 rotated_axis_title 的组合：右轴唯一单位靠竖排轴标题承载 | 样式字段中新增 axis_unit_position（竖排右轴标题 / 顶端裸单位 / 刻度内后缀），并允许左右轴单位不同 | “单位只写在竖排右轴标题上”对系列取值正确率的影响行 |
| new | 一类出版方 | new_components 的 event_marker_point_with_arrow（图内事件方块+箭头标签） | 记录字段增加 annotations 列表（时间位置、文字、是否带竖虚线/箭头），渲染层画在 plot 内 | “图内事件标注是否被误当数据系列”一行 |
| P5 | 通用 | sparse_time_ticks 与 dense_marks_100plus 同时出现（月度线配两年刻度） | 条件行中把刻度密度与数据点密度解耦，设 tick_every_n 参数 | 数据点数/刻度数比值（1 vs 12 vs 24）对读值精度的影响行 |
| P7 | 一类出版方 | unit_text 作为独立标题字段（本图编号为空、单位不在标题里） | P7 的标题记录：number 可为空串，unit 可置于轴而非标题块 | “无编号图 + 单位不在标题块”时标题上下文能否进入表格的一行 |
