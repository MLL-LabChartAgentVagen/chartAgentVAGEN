# natural-catastrophe-and-climate-report-2023_p41

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| natural-catastrophe-and-climate-report-2023 | `need_estimate` | 6 | 6 |

该页为报告第41页“Regional Recaps”章节，左栏为美国强对流风暴（SCS）损失的正文与项目符号，右栏为Figure 23：上部是SCS与热带气旋两张“Top 10最贵年份”排名表，下部是1990年以来累计保险损失折线图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 583 | `SCS` · `2023` | 1% | f2 | the printed endpoint label on the SCS (olive) trace at 2023 | 是 | `Cumulative US Insured Loss: SCS vs TC` · `SCS` · `USD billion` |
| 2 | 566 | `TC` · `2023` | 1% | f2 | the printed endpoint label on the TC (blue) trace at 2023 | 是 | `Cumulative US Insured Loss: SCS vs TC` · `TC` · `USD billion` |
| 3 | 480 | `SCS` · `2020` | 10% | f2 | the TC trace on its plateau after the late-2010s riser, read between the $400B and $500B grid lines | 否 | `Cumulative US Insured Loss: SCS vs TC` · `TC` · `USD billion` · `2020` |
| 4 | 480 | `TC` · `2020` | 10% | f2 | the SCS trace where it crosses the TC plateau near 2021, read between $400B and $500B | 否 | `Cumulative US Insured Loss: SCS vs TC` · `SCS` · `USD billion` · `2020` |
| 5 | 200 | `SCS` · `2010` | 10% | f2 | the SCS trace at the $200B grid line, roughly the 2011 point | 否 | `Cumulative US Insured Loss: SCS vs TC` · `SCS` · `USD billion` · `$200B` |
| 6 | 280 | `TC` · `2010` | 10% | f2 | the TC trace on its plateau just under $300B, between the 2010 and 2015 ticks | 否 | `Cumulative US Insured Loss: SCS vs TC` · `TC` · `USD billion` · `2010` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 6 predicted key sets miss a rule label: 583, 566, 200

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `other · ranked top-10 table` | na | 2 | 1 | 10 | 20 | 全部 | （不画值轴） |
| f2 | `line` | vertical | 1 | 2 | 8 | 68 | 部分 | $100B, $200B, $300B, $400B, $500B, $600B |

- **f1** Figure 23 / US Mainland / Top 10 Costliest Years: Insured Loss　[图上方]　（标题里没有单位）
- **f2** Cumulative US Insured Loss: SCS vs TC　[图上方]　单位 `USD billion`
  - 来源行：Data and Graphic: Gallagher Re

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `step_line_series` | 阶梯线（水平段 + 垂直跳变），不是直连折线 | f2 | **无** | TC trace moves in flat treads and vertical risers (e.g. jump near 2005, plateau to 2008) |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | The same rank/year/loss table repeated twice, once per peril, side by side |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | 'Figure 23: Top 10 costliest years ...' and 'Data and Graphic: Gallagher Re' below the plot |
| `legend_inside_plot` | 图例画在绘图区内部 | f2 | **无** | 'SCS' and 'TC' swatches drawn inside the plot area, lower right, above the 1990-2025 axis |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | page | 有 | Caption: 'Top 10 costliest years ... (top) and aggregated losses since 1990' - tables plus a line chart under one number |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f1 | 有 | Two 10-row tables of rank, year and '$59.7B'-style values, captioned as part of 'Figure 23' |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | 'Severe Convective Storm' and 'Tropical Cyclone' set above their own table blocks |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | Left column body text and bullets ('2023 became the costliest insured year...') run level with the figure block |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | Scale word appears only as the axis title 'USD billion'; series names are bare 'SCS', 'TC' |
| `rotated_axis_title` | 轴标题竖排 | f2 | 有 | 'USD billion' set vertically along the left value axis |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | '583' and '566' printed in bold at the right-hand line endpoints, outside the traces |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f2 | 有 | Ticks at 1990, 1995 ... 2025 while the traces move annually |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | Horizontal rules at $100B-$600B, no vertical grid lines in the plot |

词表 65 项，本页出现 13 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `currency_prefixed_axis_ticks` | f2 | Value ticks printed as '$600B', '$500B' with currency sign and magnitude suffix in every tick | 刻度自带货币与量级，读数时不能只用裸数字对齐，导出表格需保留$与B后缀才能唯一定位数值。 |
| `cumulative_running_total_series` | f2 | Title 'Cumulative US Insured Loss' with monotonically rising traces from 1990 to 583/566 | 每个点是累计值而非年度值，读出的480、280等必须理解为自1990年起的累积额，否则与上表的年度损失混淆。 |
| `endpoint_label_pair_collision` | f2 | '583' and '566' printed one directly beneath the other at the crowded 2023 endpoints | 两条线终点标签几乎重叠，需按上下位置与线色配对，才能判断583属SCS、566属TC。 |
| `rank_index_column` | f1 | Bold rank column 1-10 to the left of the year and value columns in both tables | 行既可用排名也可用年份寻址，导出表需同时保留排名与年份，否则两表同年份数值易混。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

折线图只印了终点的583与566，其余四个待核值（480、480、200、280）必须靠像素对齐读出：网格线间距为$100B，5%容差在480处仅±24B，即约四分之一格，而两条线在2020年前后几乎重合、TC又呈台阶状平台，容易把SCS的480读成TC的480。横轴只有1990/1995/…/2025每5年一个刻度，年度点需在两刻度间插值定位，年份错一格数值就偏几十亿。上部两张表数值全部印出（$59.7B等），寻址只需面板名+排名/年份两个键，反而不构成瓶颈；因此卡点在数值读取而非表格结构。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 一类出版方 | step_line_series 与新提出的 cumulative_running_total_series 组合 | 折线图生成条件行：新增“累计单调序列+台阶跳变”的数据生成器与样式字段 | 台阶式累计折线 vs 平滑年度折线，对比每点读数误差是否超过5% |
| P6 | 通用 | sparse_time_ticks（刻度间隔为数据点的5倍） | 时间轴样式字段：tick_every 与 data_every 解耦 | 刻度=数据点 vs 刻度每5点，对比年份定位正确率 |
| P6 | 一类出版方 | currency_prefixed_axis_ticks（$600B 形式刻度） | 刻度格式字段：前缀货币符号+量级后缀 | 裸数字刻度 vs 带$与B后缀刻度，对比单位复原正确率 |
| P2 | 一类出版方 | heterogeneous_panel_types + panel_title_per_panel（一个图号下两张表加一张折线） | 页面级记录：把 Figure 23 拆成多子块并把面板名写入 panel_key | 单类型多面板 vs 表格+折线混合面板，对比子块标题是否进入表头 |
| P4 | 一类出版方 | data_table_as_figure（排名表当图） | 图族权重向量中加入“排名表”族，含排名列与$xx.xB值列 | 排名表族权重0 vs 非0，对比表格型图的行寻址命中率 |
| P7 | 通用 | heading 五段拆分（US Mainland / Top 10 Costliest Years: Insured Loss / USD billion 分列不同位置） | 标题记录字段：number、title、subtitle、unit、placement 各自独立 | 单行标题 vs 标题+副标题+旋转单位分置，对比上下文键的召回 |
