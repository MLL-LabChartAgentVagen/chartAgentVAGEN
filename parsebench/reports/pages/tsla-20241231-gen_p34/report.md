# tsla-20241231-gen_p34

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| tsla-20241231-gen | `need_estimate` | 10 | 10 |

本页顶部是一张60个月累计总回报对比折线图（Tesla、NASDAQ Composite 与同业公司组），下方为10-K中关于未注册股权销售、发行人购股与ITEM 6的正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 100 | `Dec-19` · `Tesla` | 1% | f1 | the Dec-19 starting point of the Motor Vehicles and Passenger Car Bodies Public Company Group line | 否 | `Comparison of 60 Months Cumulative Total Return` · `Motor Vehicles and Passenger Car Bodies Public Company Group` · `Dec-19` |
| 2 | 100 | `Dec-19` · `Motor Vehicles and Passenger Car Bodies Public Company Group` | 1% | f1 | the Dec-19 starting point of the Tesla line | 否 | `Comparison of 60 Months Cumulative Total Return` · `Tesla` · `Dec-19` |
| 3 | 100 | `Dec-19` · `NASDAQ Composite` | 1% | f1 | the Dec-19 starting point of the NASDAQ Composite line | 否 | `Comparison of 60 Months Cumulative Total Return` · `NASDAQ Composite` · `Dec-19` |
| 4 | 1450 | `Dec-24` · `Tesla` | 1% | f1 | the Dec-24 end point of the Tesla dotted line, the figure's maximum | 否 | `Comparison of 60 Months Cumulative Total Return` · `Tesla` · `Dec-24` |
| 5 | 1340 | `Oct-21` · `Tesla` | 1% | f1 | the Tesla peak around Nov-21 / Dec-21 (near $1,370 crest region) | 否 | `Comparison of 60 Months Cumulative Total Return` · `Tesla` · `Dec-21` |
| 6 | 285 | `Dec-24` · `Motor Vehicles and Passenger Car Bodies Public Company Group` | 5% | f1 | the Dec-24 end point of the solid Motor Vehicles and Passenger Car Bodies Public Company Group line | 否 | `Comparison of 60 Months Cumulative Total Return` · `Motor Vehicles and Passenger Car Bodies Public Company Group` · `Dec-24` |
| 7 | 230 | `Dec-24` · `NASDAQ Composite` | 5% | f1 | the Dec-24 end point of the dashed NASDAQ Composite line | 否 | `Comparison of 60 Months Cumulative Total Return` · `NASDAQ Composite` · `Dec-24` |
| 8 | 810 | `Dec-20` · `Tesla` | 5% | f1 | a Tesla trough around Jun-22 (the dip to roughly $800 after the $1,080 local peak) | 否 | `Comparison of 60 Months Cumulative Total Return` · `Tesla` · `Jun-22` |
| 9 | 450 | `Dec-22` · `Tesla` | 5% | f1 | the Tesla low point near Dec-22, the series minimum | 否 | `Comparison of 60 Months Cumulative Total Return` · `Tesla` · `Dec-22` |
| 10 | 610 | `Aug-20` · `Tesla` | 5% | f1 | the Tesla local peak around Aug-20 before the pullback to about $460 | 否 | `Comparison of 60 Months Cumulative Total Return` · `Tesla` · `Aug-20` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: 100, 100, 1340, 810

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 3 | 61 | 183 | 无 | $-, $100, $200, $300, $400, $500, $600, $700, $800, $900, $1,000, $1,100, $1,200, $1,300, $1,400, $1,500, $1,600 |

- **f1** Comparison of 60 Months Cumulative Total Return　[图上方]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend row "Motor Vehicles and Passenger Car Bodies Public Company Group / Tesla / NASDAQ Composite" under the x axis |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | all three series start near $100 at Dec-19; title says "60 Months Cumulative Total Return" |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | month ticks "Dec-19", "Feb-20" ... "Dec-24" set vertically under the axis |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | time labels written as "Dec-19", "Aug-22", "Dec-24" rather than ISO dates |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | monthly plotted points but tick labels only every second month, Dec-19 to Dec-24 |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | legend label "Motor Vehicles and Passenger Car Bodies Public Company Group" runs very long beside the line sample |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each $100 level, no vertical grid lines |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | three monthly series over 61 months, roughly 183 plotted points |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | f1 | **无** | Tesla drawn dotted, NASDAQ Composite dashed, company group solid, all in black |

词表 65 项，本页出现 9 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `currency_prefixed_axis_ticks` | f1 | value ticks printed with a dollar sign and zero as "$-" instead of "$0" | 读数需去掉货币符号，且零刻度写作"$-"，解析成数字时容易丢失或误判为缺失值。 |
| `indexed_base_implicit` | f1 | series all begin at $100 in Dec-19 but no "= 100" base statement is printed anywhere | 基期100只能由起点形状推断，表格若不注明基准，读出的值缺少刻度含义。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

网格线间距为$100，图高约640像素覆盖$0–$1,600，即约2.5美元/像素；Tesla在$1,340处的5%容差是±67美元（约27像素），尚可，但公司组与NASDAQ两条线在$100–$285区间几乎重叠，$285与$230相差仅约22像素，且两线在多处贴合，逐月取值时极易串线；再加上月度点密（61个刻度只标一半），要把某一具体月份的点定位到±5%（如230的±11.5美元≈4.6像素）实际不可达。相比之下标题与三条图例名称都是明文，寻址键并不构成主要障碍。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | dashed_line_series 与新键 currency_prefixed_axis_ticks | 样式字段：线型作为系列身份编码（全黑无彩），以及值轴刻度格式（"$-"、"$1,600"带货币前缀） | 新增一行"单色多线仅以实线/点线/虚线区分 + 货币前缀刻度"，检验模型在无颜色线索下的系列归属与刻度解析 |
| P6 | 通用 | sparse_time_ticks 与 rotated_x_ticks 组合（月度序列每两月一标、竖排） | 条件行：时间轴刻度密度与旋转角度；记录字段中类别数（61）与标注刻度数（31）分离 | 新增一行"数据点数为刻度标签数2倍且标签竖排"，衡量点—刻度对位误差 |
| P5 | 通用 | dense_marks_100plus（约183个点） | 密度上限：允许单图3系列×61时间点的折线 | 新增一行"单面板≥150点折线、系列间垂直间距<30像素"，将密度作为可控变量而非布尔门限 |
| P7 | 一类出版方 | 新键 indexed_index_base_implicit（基期100未书面声明）+ rebased_index_values | 标题/单位字段：unit_text 为空但数值是以Dec-19=100 的指数 | 新增一行"指数化数值但基期未印在标题或副标题"，检验单位缺失时的数值语义还原 |
| P3 | 通用 | legend_below_plot 与超长图例名（wrapped_category_labels） | 布局字段：图例位置在绘图区下方，且单条图例文本超过50字符 | 新增一行"图例位于图下且单条名称超长"，检验表格列名能否完整承载系列名 |
