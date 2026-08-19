# sri-sigma-natural-catastrophes-1-2025_p19

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| sri-sigma-natural-catastrophes-1-2025 | `need_estimate` | 9 | 9 |

本页为 Swiss Re Institute sigma 报告第19页，含正文两段、蓝底方框内的 Figure 11 折线图（加州 FAIR Plan 新签及续保保单占全部房主保单比例，2018–2023，两条序列）、章节小标题及四条脚注。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 1.5% | `2018` · `Statewide` | 20% | f1 | the Statewide point at an early year (around 2019/2020), read against the axis between 0% and 5% | 否 | `Statewide` · `2020` · `Figure 11` |
| 2 | 1.6% | `2018` · `Top 10 high fire risk counties` | 20% | f1 | another Statewide point on the near-flat dark line, indistinguishable from neighbouring years at this scale | 否 | `Statewide` · `2021` · `Figure 11` |
| 3 | 2.0% | `2019` · `Statewide` | 20% | f1 | a Statewide point in the later years, just above the 0% baseline | 否 | `Statewide` · `2022` · `Figure 11` |
| 4 | 13.0% | `2019` · `Top 10 high fire risk counties` | 10% | f1 | the Top 10 high fire risk counties point at 2019, between the 10% and 15% gridlines | 否 | `Top 10 high fire risk counties` · `2019` · `Figure 11` |
| 5 | 2.5% | `2020` · `Statewide` | 20% | f1 | the Statewide point at 2023, the right end of the dark line, halfway to the 5% gridline | 否 | `Statewide` · `2023` · `Figure 11` |
| 6 | 21.0% | `2020` · `Top 10 high fire risk counties` | 10% | f1 | the Top 10 high fire risk counties point at 2020, just above the 20% gridline | 否 | `Top 10 high fire risk counties` · `2020` · `Figure 11` |
| 7 | 3.0% | `2021` · `Statewide` | 10% | f1 | a Statewide value near the right end of the dark line, read against the 5% gridline | 否 | `Statewide` · `2023` · `Figure 11` |
| 8 | 23.0% | `2021` · `Top 10 high fire risk counties` | 10% | f1 | the Top 10 high fire risk counties point at 2021, between the 20% and 25% gridlines | 否 | `Top 10 high fire risk counties` · `2021` · `Figure 11` |
| 9 | 26.0% | `2022` · `Top 10 high fire risk counties` | 10% | f1 | the Top 10 high fire risk counties endpoint at 2022, just above the 25% gridline | 否 | `Top 10 high fire risk counties` · `2022` · `Figure 11` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 9 predicted key sets miss a rule label: 1.5%, 1.6%, 2.0%, 2.5%, 3.0%

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 2 | 6 | 12 | 无 | 0%, 5%, 10%, 15%, 20%, 25%, 30% |

- **f1** Figure 11 / Number of California Fair Plan new and renewed policies as share of total homeowner policies　[与图并排]　（标题里没有单位）
  - 来源行：Source: California Department of Insurance, Swiss Re Institute

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: California Department of Insurance, Swiss Re Institute" printed below the plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | "Statewide" and "Top 10 high fire risk counties" legend row sits under the x axis |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f1 | **无** | "Figure 11 / Number of California Fair Plan..." caption column at left, level with the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis ticks read "0%" to "30%"; title says "as share of total homeowner policies" |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | superscript 37, 38, 39, 40 in body text keyed to footnotes at page bottom |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole figure block including plot area sits on a pale blue tint |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 5%..30% across the panel, no vertical rules drawn |

词表 65 项，本页出现 7 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `series_shorter_than_axis` | f1 | green "Top 10 high fire risk counties" line ends at 2022; "Statewide" line runs to 2023 | 两条线覆盖的年份不同，读取2023年时只有 Statewide 有值，表格需允许该序列缺格而非误读为零。 |
| `axis_tick_percent_sign_on_every_tick` | f1 | every tick label carries "%": 0%, 5%, 10%, 15%, 20%, 25%, 30% | 单位随刻度重复出现，解析出的数值天然带百分号，匹配时须处理 "26.0%" 与 "26%" 的写法差异。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数字标注，网格间距为5个百分点（约50像素），而给定的 Statewide 数值全部落在 1.5%–3.0% 之间，即0%与5%之间那一格内：5%容差意味着 1.5% 只允许±0.075个百分点、约0.8像素的误差，深色线在该区间几乎贴着基线且逐年只抬升不到一格的1/10，1.5%、1.6%、2.0%、2.5%、3.0% 无法逐年区分。绿色线的 13%、21%、23%、26% 容差稍宽（±0.65–1.3个百分点，约7–13像素）尚可估读，但仍需靠年份刻度定位，且该序列在2022年就终止。相比之下标签只需「序列名+年份」两个键，图注也在图外的浅蓝侧栏中，均比读值容易。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | P1：把 readable 改为逐点可达精度，对压缩在单一网格格内的低值序列（Statewide 1.5%–3.0%）给出更宽的容差或标注为不可读 | 评分条件行中的 readable 门限字段，以及每个 mark 的 attainable_precision 记录字段 | 新增一行：同一图内高值序列与低值序列分别评分，检验「同轴共存的量级差」对读值成功率的影响 |
| new | 一类出版方 | new_components 中的 series_shorter_than_axis（序列早于时间轴结束） | 数据记录字段：允许某序列在部分类别上为空，并在生成条件行中加入 series_end_offset | 新增一行：含提前终止序列的折线图 vs 全覆盖折线图，考察缺值年份是否被误填 |
| P7 | 这份文档自己的习惯 | P7：把 Figure 11 的编号与标题作为独立字段，并记录标题位于图左侧栏（placement=beside） | 样式字段 heading_placement，新增 beside 取值；导出记录中拆出 figure_number/title | 新增一行：标题在图上方 vs 在左侧栏时，图题能否与表格绑定 |
| P6 | 通用 | P6：刻度格式维度，覆盖每个刻度都带 % 的写法（0%…30%） | 样式字段 tick_format（bare number / percent-suffixed） | 新增一行：刻度带单位符号 vs 单位只写在标题时，数值匹配的字符串一致率 |
