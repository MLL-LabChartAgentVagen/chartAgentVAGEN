# 7c6b23db-en_p58

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 7c6b23db-en | `need_estimate` | 9 | 9 |

本页为 IEA《Energy Technology Perspectives 2023》第58页，正文讨论清洁能源供应链投资需求，下方为图 1.12：三类大宗材料生产行业按国家/区域分组的资本成本水平横向分组条形图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 6.8 | `Iron & steel` · `Other emerging market and developing economies` | 20% | f1 | the Iron & steel blue bar (Other emerging market and developing economies) | 否 | `Iron & steel` · `Other emerging market and developing economies` |
| 2 | 3.1 | `Iron & steel` · `China` | 20% | f1 | the Iron & steel red bar (China) | 否 | `Iron & steel` · `China` |
| 3 | 3.3 | `Iron & steel` · `Advanced economies` | 25% | f1 | the Iron & steel yellow bar (Advanced economies) | 否 | `Iron & steel` · `Advanced economies` |
| 4 | 9.1 | `Chemicals` · `Other emerging market and developing economies` | 20% | f1 | the Chemicals blue bar (Other emerging market and developing economies) | 否 | `Chemicals` · `Other emerging market and developing economies` |
| 5 | 6.4 | `Chemicals` · `China` | 20% | f1 | the Chemicals red bar (China) | 否 | `Chemicals` · `China` |
| 6 | 4.0 | `Chemicals` · `Advanced economies` | 25% | f1 | the Chemicals yellow bar (Advanced economies) | 否 | `Chemicals` · `Advanced economies` |
| 7 | 8.4 | `Cement` · `Other emerging market and developing economies` | 10% | f1 | the Cement blue bar (Other emerging market and developing economies) | 否 | `Cement` · `Other emerging market and developing economies` |
| 8 | 5.6 | `Cement` · `China` | 15% | f1 | the Cement red bar (China) | 否 | `Cement` · `China` |
| 9 | 4.2 | `Cement` · `Advanced economies` | 20% | f1 | the Cement yellow bar (Advanced economies) | 否 | `Cement` · `Advanced economies` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | horizontal | 1 | 3 | 3 | 9 | 无 | 0%, 2%, 4%, 6%, 8%, 10% |
| f2 | `other · none (not a figure)` | na | 0 | 0 | 0 | 0 | 无 | （不画值轴） |

- **f1** Figure 1.12 / Cost of capital for bulk material production industries by country/regional grouping, 2020　[图上方]　（标题里没有单位）
  - 来源行：Source: Adapted from IEA (2021c).
- **f2** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | three bars (blue, red, yellow) side by side inside each of Iron & steel, Chemicals, Cement |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | categories Iron & steel / Chemicals / Cement on the y axis, bars grow rightwards to 0%-10% axis |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: Adapted from IEA (2021c)." and "IEA. CC BY 4.0." printed below the plot |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f1 | 有 | legend column with three entries sits to the right of the plot area, level with the bars |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | legend entry "Other emerging market and developing economies" wraps onto two lines |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | vertical rules at 2%, 4%, 6%, 8%, 10% only, no horizontal grid lines |

词表 65 项，本页出现 6 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `caption_takeaway_below_figure` | f1 | bold blue sentence below source: "Financing costs for bulk material production in the emerging economies can be more than twice..." | 该结论句在图下方且为粗体，解析后可能被误当作图题或正文，读值时需分清它不是坐标轴/系列标签。 |
| `percent_tick_labels_only_unit` | f1 | axis reads "0% 2% 4% 6% 8% 10%"; no unit word in title or axis title | 单位仅由刻度上的百分号承载，表格若只抄数字会丢失百分比语义，取值需补回 %。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上无任何数值标签，9 个条形全靠像素对轴读取；刻度间隔为 2 个百分点，在 150 dpi 下约 100 px，5% 容差对 3.1 只有 ±0.16 个百分点，即约 8 px，红色 Iron & steel 条（3.1）与黄色（3.3）差距仅约 10 px，极易互换或落到容差外。相比之下寻址只需 2 个键（行业 + 系列名），标签层不难；图题为粗体独立行，上下文也可获得。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | 为无数值标签的横向分组条形图设定 per-mark 可达精度（结合刻度间隔与条长像素） | 渲染条件行中的 values_printed=none 与 value_axis_ticks 间隔字段，评分侧改为按标记的容差 | 新增一行：values_printed=none × 刻度步长 2%（无次刻度） vs 有数值标签，比较读数命中率 |
| P6 | 一类出版方 | legend_beside_plot（右侧竖排图例，含换行长系列名） | 样式字段 legend_position，增加 right 且允许系列名折行 | 新增一行：图例在右侧 vs 下方时，系列名与行业名的配对正确率 |
| P6 | 通用 | 单位仅存在于刻度标签的百分号形式（percent_tick_labels_only_unit） | 刻度格式字段 tick_format=percent，且标题/轴标题不写单位 | 新增一行：单位在刻度 % vs 单位在标题，导出表中数值是否保留百分比语义 |
| P7 | 这份文档自己的习惯 | 图下方粗体结论句（caption_takeaway_below_figure）与 Source 行的区分 | 记录字段中增加 takeaway 文本槽，置于 source_line 之后 | 新增一行：图下含结论句 vs 仅含 Source 行，标题/上下文归属判定准确率 |
