# 5._ESM_Staff_Report_on_Comprehensive_Review_p8

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 5._ESM_Staff_Report_on_Comprehensive_Review | `need_estimate` | 10 | 10 |

本页含一幅折线图（Figure 2，欧元区成员国公共债务比率的25分位、中位数、75分位分布）及其来源/注释行，下方为两段正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 45 | `2001` · `25th percentile` | 10% | f1 | the 2001 point on the 25th percentile line (~45%) | 否 | `25th percentile` · `2001` |
| 2 | 58 | `2001` · `Median` | 10% | f1 | the 2001 point on the Median line (~58%) | 否 | `Median` · `2001` |
| 3 | 30 | `2007` · `25th percentile` | 20% | f1 | the 2007 trough on the 25th percentile line (~30%) | 否 | `25th percentile` · `2007` |
| 4 | 104 | `2011` · `75th percentile` | 10% | f1 | the 2011 point on the 75th percentile line, first plateau above 100% (~104%) | 否 | `75th percentile` · `2011` |
| 5 | 82 | `2013` · `Median` | 10% | f1 | the 2011-2012 level of the Median line (~82%) | 否 | `Median` · `2011` |
| 6 | 44 | `2023` · `25th percentile` | 20% | f1 | the 2023 endpoint of the 25th percentile line (~44%) | 否 | `25th percentile` · `2023` |
| 7 | 67 | `2023` · `Median` | 15% | f1 | the 2023 endpoint of the Median line (~67%) | 否 | `Median` · `2023` |
| 8 | 40 | `2019` · `25th percentile` | 20% | f1 | the 2019 local low of the 25th percentile line (~40%) | 否 | `25th percentile` · `2019` |
| 9 | 78 | `2005` · `75th percentile` | 15% | f1 | the 2001 starting point of the 75th percentile line (~78%) | 否 | `75th percentile` · `2001` |
| 10 | 110 | `2021` · `75th percentile` | 10% | f1 | not placeable: the 75th percentile peak around 2020 reads ~115%, no mark sits at 110 | 否 | — |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 82, 78, 110

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 3 | 23 | 69 | 无 | 0%, 20%, 40%, 60%, 80%, 100%, 120% |
| f1 | `other · placeholder duplicate` | na | 0 | 0 | 0 | 0 | 无 | （不画值轴） |

- **f1** Figure 2. / Distribution of euro area member states' public debt ratios　[图上方]　（标题里没有单位）
  - 来源行：Source: European Commission, AMECO database Note: Euro area in rolling composition
- **f1** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: European Commission, AMECO database" and "Note: Euro area in rolling composition" below the plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend row "25th percentile / Median / 75th percentile" sits under the x axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | y tick labels themselves carry "%" (0%..120%); title says "public debt ratios" |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | x ticks every two years 2001, 2003 ... 2023 while data points are annual |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 20%..120%, no vertical grid lines |

词表 65 项，本页出现 5 项，其中我们画不出来的 1 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `percent_ticks_with_symbol` | f1 | every y tick printed with a percent sign: "0%", "20%", ... "120%" | 读数时刻度自带单位，表格中数值可能写成 45 或 45%，匹配需兼容两种形式。 |
| `distribution_percentile_series` | f1 | three series are 25th percentile, Median, 75th percentile of the same variable | 三条线是同一变量的分位数，寻址某个值必须同时指定年份与分位名称，否则会混淆。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

y 轴刻度间隔为 20 个百分点，跨约 35 像素带宽，单条折线三系列在 40%–80% 区间彼此靠近；要把 30、44、58 这类值读到 5% 容差（如 30 只允许 ±1.5 个百分点，约 2–3 像素）几乎超出像素分辨能力。加之图上无任何数值标签、x 轴每两年一刻度，2020 年这类奇数年点需在刻度之间定位，进一步放大读数误差；相比之下每个值只需“系列名+年份”两个键，寻址并不困难。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | 为折线图加入 sparse_time_ticks 与无数值标签组合的读数条件行 | 条件表中时间轴刻度密度字段（每 N 年一刻度）与 values_printed=none | 刻度间隔 vs 数据点间隔（1:1 / 1:2 / 1:3）下的逐点读数精度 |
| P6 | 一类出版方 | 新组件 percent_ticks_with_symbol（刻度自带 % 号） | 样式字段 tick_format：bare number / with unit symbol | 刻度带单位符号与不带时，数值匹配成功率对比 |
| P7 | 这份文档自己的习惯 | 标题块拆分：figure_number 单独一行加粗小字（"Figure 2."）与标题另起一行 | 记录字段 heading（number/title/unit/placement=above） | 编号与标题分行 vs 同行时上下文命中率 |
| new | 一类出版方 | 新组件 distribution_percentile_series（分位数系列） | 系列命名生成规则，引入分位数族系列名 | 同一变量多分位系列 vs 不同实体系列时的寻址键歧义率 |
