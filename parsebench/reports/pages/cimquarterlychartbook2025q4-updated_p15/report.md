# cimquarterlychartbook2025q4-updated_p15

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| cimquarterlychartbook2025q4-updated | `untagged` | 10 | 0 |

整页是一张幻灯片式图表：S&P 500 1980–2024 年年度总回报柱状图叠加年内最大回撤黑点标记，并附平均值文本框与来源注释。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 32.5% | `Annual Total Return` · `1980` | 5% | f1 | the 1980 Annual Total Return bar | 是 | `1980` · `Annual Total Return` |
| 2 | -17.1% | `Annual Max Drawdown` · `1980` | 5% | f1 | the 1980 Annual Max Drawdown dot label | 是 | `1980` · `Annual Max Drawdown` |
| 3 | 31.7% | `Annual Total Return` · `1985` | 5% | f1 | the 1985 Annual Total Return bar (also printed for 1989) | 是 | `1985` · `Annual Total Return` |
| 4 | -7.7% | `Annual Max Drawdown` · `1985` | 5% | f1 | the 1985 Annual Max Drawdown boxed label | 是 | `1985` · `Annual Max Drawdown` |
| 5 | -3.1% | `Annual Total Return` · `1990` | 5% | f1 | the 1990 Annual Total Return bar (negative bar below zero) | 是 | `1990` · `Annual Total Return` |
| 6 | -19.9% | `Annual Max Drawdown` · `1990` | 5% | f1 | the 1990 Annual Max Drawdown boxed label | 是 | `1990` · `Annual Max Drawdown` |
| 7 | 37.6% | `Annual Total Return` · `1995` | 5% | f1 | the 1995 Annual Total Return bar, tallest on the chart | 是 | `1995` · `Annual Total Return` |
| 8 | -2.5% | `Annual Max Drawdown` · `1995` | 5% | f1 | the 1995 Annual Max Drawdown boxed label, smallest drawdown | 是 | `1995` · `Annual Max Drawdown` |
| 9 | 15.1% | `Annual Total Return` · `2010` | 5% | f1 | the 2010 Annual Total Return bar | 是 | `2010` · `Annual Total Return` |
| 10 | -33.9% | `Annual Max Drawdown` · `2020` | 5% | f1 | the 2020 Annual Max Drawdown boxed label | 是 | `2020` · `Annual Max Drawdown` |

**程序核对**（模型没有看到左半的标签列）：

- 标了 dense_marks_100plus，但没有图达到 100 个图元——dense_marks_100plus claimed, densest figure has 90 marks

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 45 | 90 | 全部 | 40.0%, 30.0%, 20.0%, 10.0%, 0.0%, -10.0%, -20.0%, -30.0%, -40.0%, -50.0% |

- **f1** S&P 500 Annual Total Return and Max Drawdown　[图上方]　（标题里没有单位）
  - 来源行：Source: Cetera Investment Management, FactSet, YCharts. The annual total return includes dividends. The annual max decline is the largest price decline in each calendar year. Return and max drawdown data based on closing prices. Data as of 12/31/2024.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | teal bars for Annual Total Return with black circular markers for Annual Max Drawdown in same panel |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a horizontal rule drawn at 0.0% separating positive bars from drawdown dots |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | bars fall below the 0.0% line (-4.9%, -37.0%) and all drawdown dots sit below zero |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | boxed note inside plot: "1980 - 2024 Average Annual Total Return: 13.5% Average Annual Max Drawdown: -14.1%" |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | small italic "Source: Cetera Investment Management, FactSet, YCharts..." under the plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | "Annual Total Return" and "Annual Max Drawdown" legend row beneath the x axis |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | bar percentages printed above bar tops; dot values in blue boxes on leader lines below dots |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | 45 yearly bars but x ticks only at 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020 |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 45 bars plus 45 dots plus 90 printed value labels crowd the panel |

词表 65 项，本页出现 9 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `leader_line_boxed_labels` | f1 | each black dot's value sits in a blue filled box connected by a thin white leader line | 数值不在标记处，需沿引线把蓝色标签框与对应黑点配对，错配会把回撤值归到相邻年份。 |
| `label_only_series_position` | f1 | black dots for drawdown are drawn against the same % axis but many labels displaced far from dot | 读值时若以标签垂直位置对轴读取会严重偏差，必须以黑点位置为准或直接采用印刷数字。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部印在图上（45 个柱标 + 45 个回撤标签），读数不成问题；轴刻度 10 个百分点一格也无需目测。真正的障碍是定位：x 轴只标 1980/1985/.../2020，中间 4 个年份没有刻度，表格要为每个值给出「年份 + 系列名（Annual Total Return / Annual Max Drawdown）」两个键，而 31.7% 在 1985 与 1989 重复出现，仅凭系列名无法区分，必须依赖被隐藏的年份键；同时蓝框标签靠引线连到黑点，解析器易把标签配到相邻年份列。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | leader_line_boxed_labels（新构件）与 value_label_outside 的引线变体 | 样式字段中的数值标签放置项，增加「带引线的填色标签框」选项及其与标记的配对关系记录 | 标签是否通过引线偏移放置 × 标记归属正确率 |
| P3 | 通用 | sparse_time_ticks 与隐含年份类别的显式记录 | 记录字段：category 列表保留全部 45 个年份，即使轴上只画 9 个刻度 | 类别数 ≫ 刻度数时，行标签补全率 |
| P4 | 一类出版方 | mixed_marks（柱 + 点同轴）作为独立图族权重 | 图族权重向量中新增 bar+point overlay 一类 | 混合标记图族生成频率 × 系列归属错误率 |
| P3 | 一类出版方 | annotation_callout（图内统计文本框） | 页面级样式条件行：是否在绘图区内放置带边框的汇总说明 | 图内文本框存在时，是否被误当作数据行导出 |
| P5 | 通用 | dense_marks_100plus 的密度上限提升 | 密度参数：单图 90 个标记 + 90 个数值标签 | 标记数 45/90/180 三档下的标签重叠与读取正确率 |
