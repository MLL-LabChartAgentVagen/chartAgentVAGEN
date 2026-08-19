# TSLA-Q3-2023-Update-3_p7

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| TSLA-Q3-2023-Update-3 | `need_estimate` | 10 | 10 |

这是特斯拉季度更新报告第7页「VEHICLE CAPACITY」，左侧为分区域产能说明文字，右侧上方是「Current Installed Annual Vehicle Capacity」表格，下方是三条曲线的市场份额折线图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 4.0 | `US/Canada` · `Q3 2023` | 5% | f2 | the US/Canada line at its final point Q3 2023, just under the 4% grid line | 否 | `US/Canada` · `Q3 2023` · `Market share of Tesla vehicles by region (TTM)` |
| 2 | 2.8 | `Europe` · `Q2 2023` | 5% | f2 | the Europe line endpoint at Q3 2023, rising above the 2% grid line | 否 | `Europe` · `Q3 2023` · `Market share of Tesla vehicles by region (TTM)` |
| 3 | 2.3 | `China` · `Q3 2023` | 5% | f2 | the China line endpoint at Q3 2023, slightly above 2% | 否 | `China` · `Q3 2023` · `Market share of Tesla vehicles by region (TTM)` |
| 4 | 0.2 | `US/Canada` · `Q3 2017` | 20% | f2 | the US/Canada first point at Q3 2017, just above the 0% line | 否 | `US/Canada` · `Q3 2017` · `Market share of Tesla vehicles by region (TTM)` |
| 5 | 0.15 | `Europe` · `Q3 2017` | 20% | f2 | the Europe first point at Q3 2017, a hair above the 0% line | 否 | `Europe` · `Q3 2017` · `Market share of Tesla vehicles by region (TTM)` |
| 6 | 0.1 | `China` · `Q3 2017` | 20% | f2 | the China first point at Q3 2017, lowest of the three at the left edge | 否 | `China` · `Q3 2017` · `Market share of Tesla vehicles by region (TTM)` |
| 7 | 2.4 | `US/Canada` · `Q4 2021` | 5% | f2 | the Europe point at Q2 2023, between the 2% and 3% grid lines | 否 | `Europe` · `Q2 2023` · `Market share of Tesla vehicles by region (TTM)` |
| 8 | 2.2 | `Europe` · `Q1 2023` | 5% | f2 | the China point at Q2 2023, just above the 2% grid line | 否 | `China` · `Q2 2023` · `Market share of Tesla vehicles by region (TTM)` |
| 9 | 1.7 | `China` · `Q2 2022` | 5% | f2 | the Europe point on the Q3 2022 plateau, between the 1% and 2% grid lines | 否 | `Europe` · `Q3 2022` · `Market share of Tesla vehicles by region (TTM)` |
| 10 | 1.2 | `US/Canada` · `Q1 2020` | 10% | f2 | the US/Canada local peak at Q3 2019, just above the 1% grid line | 否 | `US/Canada` · `Q3 2019` · `Market share of Tesla vehicles by region (TTM)` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 10 predicted key sets miss a rule label: 2.8, 2.4, 2.2, 1.7, 1.2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `other · data table` | na | 1 | 2 | 9 | 18 | 全部 | （不画值轴） |
| f2 | `line` | vertical | 1 | 3 | 25 | 75 | 无 | 0%, 1%, 2%, 3%, 4% |

- **f1** Current Installed Annual Vehicle Capacity　[图上方]　（标题里没有单位）
- **f2** Market share of Tesla vehicles by region (TTM)　[图下方]　（标题里没有单位）
  - 来源行：Source: Tesla estimates based on latest available data from ACEA; Autonews.com; CAAM – light-duty vehicles only

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | f1 | **无** | Capacity cells read '-' for 'Tesla Semi', 'Next Gen Platform' and 'Roadster' |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | capacity table and market-share line chart each carry their own caption and note lines |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | small grey note below table: 'Installed capacity ≠ current production rate and there may be limitations...' |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | 'Source: Tesla estimates based on latest available data from ACEA...' and 'TTM = Trailing twelve months' |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f1 | 有 | bordered table with grey header row 'Region \| Model \| Capacity \| Status' under its own bold caption |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f2 | 有 | 'US/Canada  Europe  China' row sits between the table note and the 4% tick |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | left column prose 'US: California, Nevada and Texas', 'China: Shanghai' runs level with both figures |
| `rotated_x_ticks` | x 刻度标签旋转 | f2 | 有 | 'Q3 2017'…'Q3 2023' tick labels set at roughly 45 degrees under the axis |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f2 | **无** | time written as 'Q3 2017', 'Q1 2018' rather than ISO dates |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | faint horizontal rules at 0%,1%,2%,3%,4%; no vertical grid lines drawn |

词表 65 项，本页出现 9 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `chart_title_below_plot` | f2 | 'Market share of Tesla vehicles by region (TTM)' printed under the x tick labels, above the source line | 图题在坐标轴下方且紧挨来源行，解析时容易被并入注释或归到下一个块，导致折线图的数值失去标题上下文。 |
| `inequality_qualified_values` | f1 | Capacity cells read '>950,000', '>250,000', '>125,000' rather than plain numbers | 数值带有大于号前缀，检索纯数字时无法精确匹配，读数还需保留“下限”这一语义。 |
| `blank_cell_row_grouping` | f1 | second California row and Cybertruck row leave the 'Region' cell empty, inheriting the row above | 区域标签靠空单元格继承，若不回填，'550,000' 与 '>125,000' 就无法唯一定位到 California / Texas。 |
| `zebra_row_shading` | f1 | alternating white and light-grey row bands under the dark grey header row | 行底色交替只是分行提示，不编码数据，但会影响表格边界识别与行对齐。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

全部被评分的数值都落在 f2 折线图上，图上无任何数字标签，纵轴只有 0%、1%、2%、3%、4% 五个刻度，1 个百分点约占 85 像素。要把 0.1、0.15、0.2 这类点读到 5% 相对误差，等于要求 0.005–0.01 个百分点的精度，即不到 1 像素，凭像素不可能达到；即便 4.0、2.8 这样的大值，5% 也只有 0.14–0.2 个百分点，约 12–17 像素，还得在 25 个横向密集季度刻度中先对准正确的 x 位置（相邻季度间距约 40 像素，标签又旋转 45 度）。相比之下标签只需「系列名 + 季度」两个键，表格容易承载；标题虽在图下方但为粗体，属可解决问题。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | 把 f2 这类无数值标签、刻度间隔 1% 的折线图纳入「按标记可达精度」评估，而不是一刀切的可读/不可读 | 评测条件行中的 readable 字段改为 per-mark tolerance（按该点占轴长比例计算） | 新增一行：无标签折线 + 刻度间隔=1/4 轴高 时，小值点（<0.25 刻度）与大值点分别的命中率对比 |
| P7 | 一类出版方 | 新增 chart_title_below_plot（图题位于绘图区下方、紧邻 source 行）作为标题位置维度 | 图表标题记录字段：number/title/subtitle/unit + heading placement 的取值加入 below | 新增一行：标题在表格上方 vs 在绘图区下方时，数值+标题联合检索的命中率差异 |
| P3 | 一类出版方 | 新增 inequality_qualified_values 与 blank_cell_row_grouping（表格中 '>950,000' 与空 Region 单元格继承） | data_table_as_figure 的样式/记录字段：单元格值前缀与行分组是否显式回填 | 新增一行：Region 列显式重复 vs 留空继承时，'550,000'、'>125,000' 能否被唯一定位 |
| P6 | 通用 | 刻度格式维度：纵轴刻度自带 '%' 而标题中不写单位（0%,1%,2%,3%,4%） | 样式字段 tick_format / unit_position 的取值组合 | 新增一行：单位在刻度内 vs 单位在标题/轴题时，数值抽取是否保留百分号量纲 |
| P5 | 一类出版方 | 提高单图密度上限，覆盖 3 系列 × 25 季度 = 75 点的密集折线 | 生成条件中的 categories 上限与 x 轴标签旋转开关 | 新增一行：25 个旋转季度刻度 vs 8 个刻度时，x 位置对齐错误率 |
