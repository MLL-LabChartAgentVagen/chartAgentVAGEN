# sigma-1-2021-en_p20

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| sigma-1-2021-en | `need_estimate` | 10 | 10 |

Swiss Re sigma 报告第18页，正文讨论主要与次要风险损失，页下方为 Figure 11 单幅面积+折线图（1970年以来累计保险损失）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 0 | `1970` · `Primary perils` | 1% | f1 | the bottom y-axis tick label, also both series' start level at 1970 | 是 | `Figure 11` · `1970` |
| 2 | 20 | `1980` · `Secondary perils` | 20% | f1 | the cumulative level of both curves around 1980, read against the axis | 否 | `Secondary perils` · `1980` |
| 3 | 80 | `1990` · `Primary perils` | 10% | f1 | the cumulative level around 1990 | 否 | `Primary perils` · `1990` |
| 4 | 200 | `2000` · `Secondary perils` | 10% | f1 | a printed y-axis tick label; the curves cross it near 2000-2001 | 是 | `Figure 11` · `2000` |
| 5 | 350 | `2005` · `Primary perils` | 10% | f1 | the Secondary perils line a couple of years after 2005 (approx. 2007-2008) | 否 | `Secondary perils` · `2005` |
| 6 | 300 | `2005` · `Secondary perils` | 10% | f1 | the Secondary perils line just after the 2005 step, around 2005-2006 | 否 | `Secondary perils` · `2005` |
| 7 | 450 | `2010` · `Primary perils` | 10% | f1 | the Secondary perils line around 2011-2012 | 否 | `Secondary perils` · `2010` |
| 8 | 600 | `2015` · `Secondary perils` | 5% | f1 | a printed y-axis tick label; the Primary perils area reaches it around 2016 | 是 | `Figure 11` · `2015` |
| 9 | 750 | `2020` · `Primary perils` | 10% | f1 | the top of the Primary perils filled area at 2020 | 否 | `Primary perils` · `2020` |
| 10 | 820 | `2020` · `Secondary perils` | 10% | f1 | the Secondary perils line endpoint at 2020, just above the 800 grid line | 否 | `Secondary perils` · `2020` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 10 predicted key sets miss a rule label: 0, 200, 350, 450, 600

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 11 | 102 | 无 | 1 000, 800, 600, 400, 200, 0 |

- **f1** Figure 11 / Cumulative insured losses from primary and secondary perils since 1970,　[图上方]　单位 `in USD billion at 2020 prices`
  - 来源行：Source: Swiss Re Institute

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | a light-blue filled area (Primary perils) and a dark blue line (Secondary perils) in one panel |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: Swiss Re Institute' in small print below the legend |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Primary perils' swatch and 'Secondary perils' line sample sit under the x axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | heading ends 'in USD billion at 2020 prices'; y ticks are bare numbers 0...1 000 |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | annual accumulation 1970-2020 but ticks only every five years: 1970, 1975 ... 2020 |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole plot area sits on a light grey tint instead of white |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules across the panel at 0, 200, 400, 600, 800, 1 000; no vertical rules |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | two series of ~51 annual points each spanning 1970 to 2020 |

词表 65 项，本页出现 8 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `cumulative_running_total_series` | f1 | title reads 'Cumulative insured losses ... since 1970'; both curves rise monotonically to 2020 | 每点是累计值而非当年值，读数必须按“到该年为止的累计”解释，否则数值含义完全错位。 |
| `space_thousands_separator_ticks` | f1 | top tick printed as '1 000' with a space, not '1,000' or '1000' | 解析器可能把 '1 000' 拆成两个数字，影响刻度识别与数值对齐匹配。 |
| `unstacked_overlapping_area_and_line` | f1 | the dark line runs above the filled area from 1970 onward; both measured from zero | 两条曲线都自零起算而非叠加，读折线值时不能减去面积高度。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，只能靠像素读数：网格线间距为 200 单位、约 50 px，即 1 px ≈ 4 USD billion。对 20 这类小值，5% 容差只有 ±1，远小于一个像素；对 80 也只有 ±4，几乎等于一个像素宽。加之横轴只在 1970/1975/.../2020 打点而数据是逐年累计，350、450 这类中间值落在两个刻度之间，无法确定归属年份，读数误差远超容差。相比之下命名（Primary perils / Secondary perils + 年份）反而清楚。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 一类出版方 | unit_in_axis_or_title 的细分：标题末尾以逗号续接的单位子句（'..., in USD billion at 2020 prices'） | 标题渲染样式字段：把 unit 作为标题同一行的逗号后缀，而不是独立副标题行 | 单位位置=标题同行逗号后缀 vs 独立副标题行 vs 轴上方，对单位召回率的影响 |
| new | 一类出版方 | 新组件 cumulative_running_total_series（累计序列） | 记录字段增加 value_semantics=cumulative，并在标题中体现 'Cumulative ... since 1970' | 累计值序列 vs 当年值序列，对数值-年份配对正确率的影响 |
| P6 | 一类出版方 | 新组件 space_thousands_separator_ticks（'1 000' 空格千分位） | 刻度格式样式维度：千分位符号 = 空格 / 逗号 / 无 | 刻度千分位格式三档，对刻度解析与数值匹配的影响 |
| P1 | 通用 | mixed_marks 中 area+line 的无标签精度评估（P1） | readable 判定改为按 mark 计算可达精度：以网格间距 200、绘图高度约 250 px 推算每点误差 | 无数值标签、网格间距/绘图高度比不同时，逐点可达精度分档 |
| P6 | 通用 | sparse_time_ticks 与逐年数据的组合 | 时间轴条件行：刻度密度 = 每点 / 每5点，配合 51 个年度点 | 刻度稀疏度（1:1 vs 1:5）对年份寻址正确率的影响 |
