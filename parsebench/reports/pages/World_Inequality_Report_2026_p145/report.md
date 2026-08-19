# World_Inequality_Report_2026_p145

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `need_estimate` | 7 | 7 |

本页为《政治分裂》章节第145页，上半部分是Figure 8.1（法国、英国、美国工人阶级议员占比1900–2025的三条折线图，含解释与来源说明），下半部分是两栏正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 17.5 | `United Kingdom` · `1965` | 5% | f1 | the United Kingdom point around 1950, the series' first and near-highest value | 否 | `United Kingdom` · `1950` · `Share of working–class MPs (%)` |
| 2 | 12.5 | `United Kingdom` · `1970` | 5% | f1 | the United Kingdom local trough around 1970 | 否 | `United Kingdom` · `1970` · `Share of working–class MPs (%)` |
| 3 | 0 | `United Kingdom` · `2020` | 10% | f1 | the United States points at the very start of the series, around 1900–1902, lying on the 0% baseline | 否 | `United States` · `1900` · `Share of working–class MPs (%)` |
| 4 | 5 | `France` · `1960` | 5% | f1 | the France points around 1958–1960, the series' first plateau just above 4% | 否 | `France` · `1960` · `Share of working–class MPs (%)` |
| 5 | 8 | `France` · `1980` | 5% | f1 | the France plateau around 1962–1968 near 7.8–8% | 否 | `France` · `1965` · `Share of working–class MPs (%)` |
| 6 | 4.0 | `France` · `2010` | 5% | f1 | the France points around 1986–1990 and again about 2005, sitting on the 4% line | 否 | `France` · `1990` · `Share of working–class MPs (%)` |
| 7 | 1.2 | `United States` · `1975` | 10% | f1 | a United States point around 1915 or in the 2000s, just above the 1% level | 否 | `United States` · `1915` · `Share of working–class MPs (%)` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 7 predicted key sets miss a rule label: 17.5, 0, 8, 4.0, 1.2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 3 | 26 | 210 | 无 | 0%, 2%, 4%, 6%, 8%, 10%, 12%, 14%, 16%, 18%, 20% |
| f2 | `other · referenced only` | na | 0 | 0 | 0 | 0 | 无 | （不画值轴） |

- **f1** Figure 8.1. / Working class representation has always been low and has further deteriorated in recent decades / Working class representation in Western democracies, 1900–2025　[图上方]　单位 `Share of working–class MPs (%)`
  - 来源行：Sources and series: Cagé (2024).
- **f2** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | f1 | **无** | France starts only at ~1958, United Kingdom at ~1950; earlier years simply have no marks |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Interpretation. The long–run decline in the share..." and "Sources and series: Cagé (2024)." below the plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | row "France  United Kingdom  United States" with line-marker keys sits below the x axis |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | two columns of body text below discuss Figure 8.3, but text does not run beside the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | the vertical axis title carries "(%)"; ticks read 0%...20% |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "Share of working–class MPs (%)" set vertically along the left axis |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | year labels 1900, 1905 ... 2025 are turned about 45 degrees |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | markers appear yearly but ticks only every 5 years (1900, 1905, 1910 ...) |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each 2% level, no vertical rules in the panel |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | three series of yearly point markers across 1900–2025, well over 100 plotted points |

词表 65 项，本页出现 10 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `series_start_offset` | f1 | United States spans 1900–2025 while United Kingdom begins ~1950 and France ~1958 | 取值时必须先确认某年该系列是否存在，否则会把邻近系列的点误读为缺失系列的值。 |
| `marker_and_line_series` | f1 | each series drawn as a connected line with a small point marker at every yearly observation | 逐年标记密集，读数需定位到具体标记而非线段中段，5年刻度间需内插。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上完全没有数值标签，纵轴刻度间隔为2个百分点，而多数待核值本身很小：1.2%的5%容差仅±0.06个百分点，相当于2%格距的3%，即约1像素；0与4.0的判读同样要求亚格精度。加之刻度每5年一格但点是逐年的（1900–2025约有126个年度位置），要把"1.2"锚定到具体年份还需在两个刻度间内插，横向定位误差会直接改变读到的数值。相比之下行标签只需系列名+年份两个键，表格容易承载。

整页原图判不出来的：
- `f2`（other）：正文提到的 Figure 8.3 并未出现在本页，只有文字引用，无法判读其构造。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 通用 | missing_value_marker 之外新增 series_start_offset（系列起始年份不一致） | 记录字段：为每个系列增加有效区间起止，生成条件行中允许各系列时间跨度不同 | 「系列起点错配 有/无」：对比全系列同起点与部分系列后期才出现时的取值命中率 |
| P5 | 一类出版方 | sparse_time_ticks 与逐年密集标记组合（marker_and_line_series） | 样式字段：刻度间隔与数据点间隔解耦（每5年一刻度、每1年一点） | 「刻度密度=数据密度 / 刻度密度=1/5数据密度」两行，测量横轴定位误差对数值命中的影响 |
| P7 | 通用 | rotated_axis_title 与 unit_in_axis_or_title（单位以"(%)"写在竖排轴标题内） | 标题/单位样式字段：单位位置枚举加入"竖排轴标题内" | 「单位在竖排轴标题 / 单位在副标题」：检验导出表格能否恢复百分比标度 |
| P6 | 通用 | 百分号刻度格式（0%…20%）作为刻度格式维度 | 样式字段 tick_format：数值刻度带百分号与否 | 「刻度带%号 / 纯数字刻度」：对比匹配"17.5"与"17.5%"时的检索命中差异 |
