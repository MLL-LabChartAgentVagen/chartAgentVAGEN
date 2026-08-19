# World_Inequality_Report_2026_p23

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `need_estimate` | 10 | 10 |

这一页是报告执行摘要第23页，包含两幅折线图：Figure 13（1970–2025各经济体超额收益占GDP比重，含零参考线与图内文字框）与Figure 14（1976–2022各货币占全球储备份额）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 2.2 | `United States` · `2025` | 10% | f1 | the United States line at 2025 (its endpoint) | 否 | `United States` · `2025` · `Excess yield as % of country GDP, MER` |
| 2 | 5.9 | `Japan` · `2025` | 2% | f1 | the Japan line at 2025 (its endpoint, near the 6% tick) | 否 | `Japan` · `2025` · `Excess yield as % of country GDP, MER` |
| 3 | -2.1 | `BRICS` · `2025` | 5% | f1 | the BRICS line at 2025, just below the –2% tick | 否 | `BRICS` · `2025` · `Excess yield as % of country GDP, MER` |
| 4 | -3.2 | `Russia` · `2000` | 5% | f1 | the Russia line at 2025, between the –3% and –4% ticks | 否 | `Russia` · `2025` · `Excess yield as % of country GDP, MER` |
| 5 | 1.0 | `Eurozone` · `2025` | 30% | f1 | the Eurozone line at 2025, at the 1% tick | 否 | `Eurozone` · `2025` · `Excess yield as % of country GDP, MER` |
| 6 | 78 | `U.S. dollar` · `1976` | 5% | f2 | the U.S. dollar line at 1976, just under the 80% tick | 否 | `U.S. dollar` · `1976` · `Share of global reserves by currency` |
| 7 | 11 | `Euro` · `1976` | 10% | f2 | the Euro (pre-euro legacy) line at 1976, just above the 10% tick | 否 | `Euro` · `1976` · `Share of global reserves by currency` |
| 8 | 65 | `U.S. dollar` · `2006` | 5% | f2 | the U.S. dollar line local peak around 2015-2016, between 60% and 70% ticks | 否 | `U.S. dollar` · `2016` · `Share of global reserves by currency` |
| 9 | 25 | `Euro` · `2006` | 5% | f2 | the Euro line around 2006, between the 20% and 30% ticks | 否 | `Euro` · `2006` · `Share of global reserves by currency` |
| 10 | 20 | `Euro` · `2016` | 5% | f2 | the Euro line at the right end (~2022), at the 20% tick | 否 | `Euro` · `2016` · `Share of global reserves by currency` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: -3.2, 65

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 6 | 12 | 336 | 无 | 7%, 6%, 5%, 4%, 3%, 2%, 1%, 0%, –1%, –2%, –3%, –4%, –5% |
| f2 | `line` | vertical | 1 | 7 | 5 | 329 | 无 | 90%, 80%, 70%, 60%, 50%, 40%, 30%, 20%, 10%, 0% |

- **f1** Figure 13. / The international financial system generates more inequality / Excess yield (assets–liabilities) as % of country GDP, 1970–2025　[图上方]　单位 `Excess yield as % of country GDP, MER`
  - 来源行：Sources and series: Nievas and Sodano (2025) and wir2026.wid.world/methodology.b8b}
- **f2** Figure 14. / Privileged countries face lower liability costs by political design, not market dynamics / Share of global reserves by currency, 1976–2022　[图上方]　单位 `Share of global reserves by currency`
  - 来源行：Sources and series: Nievas and Sodano (2025) and wir2026.wid.world/methodology.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a dotted horizontal rule drawn across the panel at the 0% level |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | y axis reads down to –5% and China/Russia lines sit below the zero rule |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | boxed note over the plot: "The centrality of the U.S. dollar, and now other currencies,..." |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | "Figure 13." and "Figure 14." each with own title, interpretation and sources block |
| `source_note_lines` | source / note 行在图下方 | page | 有 | "Interpretation.", "Notes.", "Sources and series: Nievas and Sodano (2025)" under both figures |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two rows of legend keys BRICS/Eurozone/Russia/China/Japan/United States below the plot |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | legend rows "U.S. dollar ... Other currencies" printed under the x axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | subtitle "Excess yield (assets–liabilities) as % of country GDP, 1970–2025" |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | subtitle "Share of global reserves by currency, 1976–2022" |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | vertical axis title "Excess yield as % of country GDP, MER" set along the y axis |
| `rotated_axis_title` | 轴标题竖排 | f2 | 有 | vertical axis title "Share of global reserves by currency" along the y axis |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | annual series but x ticks every five years: 1970, 1975 ... 2025 |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f2 | 有 | annual data 1976–2022 but ticks only every ten years: 1976, 1986, 1996, 2006, 2016 |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 6 series across 56 annual points each, roughly 336 plotted points |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f2 | **无** | 7 currency series across 47 annual points, roughly 330 plotted points |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | only vertical dotted rules at 1975, 1980 ... 2025; no horizontal grid lines |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f2 | 有 | vertical dotted rules at 1986, 1996, 2006, 2016 only, no horizontal grid |

词表 65 项，本页出现 11 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `axis_title_duplicates_subtitle_unit` | f1 | subtitle says "as % of country GDP" while y axis title repeats "Excess yield as % of country GDP, MER" | 单位信息在副标题与旋转轴标题中重复，解析器可能只抓到其中一处，且轴标题额外带有"MER"限定，影响值的口径识别。 |
| `values_only_in_interpretation_text` | f1 | "privilege of 2.2% in 2025", "1% by 2025", "5.9% by 2025", "burden of around 2.1%" only in prose | 这些被评分的数值只出现在图下说明文字里，图上无数据标签，表格必须从正文抓取才能对应到系列与年份。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

两图都是无数据标签的密集折线：Figure 13 每格1个百分点，5%容差意味着读2.2%时误差只能约±0.11个百分点，即刻度间距的十分之一；BRICS、China两条绿线在–2%附近几乎重合，Eurozone与Japan在2005–2015交叉缠绕，逐年取值几乎不可能。Figure 14 十年一个刻度而数据为年度，定位2006年的Euro值需要在两条竖线间内插，且Pound sterling、Chinese renminbi、Swiss franc三条线全都压在0–8%带内互相覆盖，5%相对容差在低值区（如1–2%）等于零点几个百分点，不可分辨。相比之下系列名与年份标签清晰，addressing_keys只需两个键，标签不是瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | annotation_callout（图内文字框）作为可控样式维度 | 折线图样式字段中新增"plot-area boxed note"选项，含文本框位置与遮挡程度 | 有/无图内文字框遮挡曲线时的取值精度对比行 |
| P6 | 通用 | reference_line + negative_values 组合（0%虚线加负值轴） | 条件行中加入"zero rule drawn dotted, axis spans –5% to 7%" | 零线明确绘制 vs 仅由刻度隐含时，负值系列读数正确率行 |
| P1 | 通用 | sparse_time_ticks（年度数据、十年刻度） | 时间轴刻度密度字段：tick_every ∈ {1, 5, 10} 年 | 刻度间隔年数与单点定位误差的关系行 |
| P7 | 这份文档自己的习惯 | 标题四分（figure_number / title / subtitle / unit_text）与旋转轴标题重复单位 | 记录字段中的heading结构，允许subtitle与axis_title各带一份单位文本 | 单位只在副标题 vs 同时在旋转轴标题时的单位识别行 |
| P5 | 通用 | dense_marks_100plus（每图300+点、6–7条缠绕曲线） | 密度上限参数，允许 series×points > 300 | 曲线条数与重叠程度作为受控变量的读数衰减行 |
