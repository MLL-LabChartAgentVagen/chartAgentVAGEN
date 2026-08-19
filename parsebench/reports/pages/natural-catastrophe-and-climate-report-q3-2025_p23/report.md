# natural-catastrophe-and-climate-report-q3-2025_p23

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| natural-catastrophe-and-climate-report-q3-2025 | `need_estimate` | 10 | 10 |

该页为「Major Event Reviews — US & Europe: Severe Convective Storm」章节，含四个要点栏、两栏正文和一幅折线图（Figure 14），展示2000至2025年YTD美国与世界其他地区的SCS保险损失累计曲线。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 648 | `2025` · `United States` | 1% | f1 | the endpoint label of the 'United States' dashed line at 2025 YTD | 是 | `United States` · `2024` · `Insured Loss (USD bn; Today's Dollars)` |
| 2 | 253 | `2025` · `Rest of World` | 1% | f1 | the endpoint label of the 'Rest of World' dashed line at 2025 YTD | 是 | `Rest of World` · `2024` · `Insured Loss (USD bn; Today's Dollars)` |
| 3 | 590 | `2024` · `United States` | 10% | f1 | the 'United States' line near 2024, read against the 600 tick | 否 | `United States` · `2024` |
| 4 | 245 | `2024` · `Rest of World` | 10% | f1 | the 'Rest of World' line near 2024, just under the 253 endpoint | 否 | `Rest of World` · `2024` |
| 5 | 480 | `2022` · `United States` | 10% | f1 | the 'United States' line at about 2022, between the 400 and 500 ticks | 否 | `United States` · `2022` |
| 6 | 210 | `2022` · `Rest of World` | 10% | f1 | the 'Rest of World' line at about 2022, just above the 200 tick | 否 | `Rest of World` · `2022` |
| 7 | 410 | `2020` · `United States` | 10% | f1 | the 'United States' line at about 2020, near the 400 tick | 否 | `United States` · `2020` |
| 8 | 165 | `2020` · `Rest of World` | 10% | f1 | the 'Rest of World' line around 2019-2020, between 100 and 200 | 否 | `Rest of World` · `2020` |
| 9 | 130 | `2010` · `United States` | 10% | f1 | the 'United States' line around 2010, near the sharp rise above 100 | 否 | `United States` · `2010` |
| 10 | 55 | `2010` · `Rest of World` | 20% | f1 | the 'Rest of World' line around 2010-2012, well below the 100 tick | 否 | `Rest of World` · `2010` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 648, 253

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 2 | 13 | 52 | 部分 | 100, 200, 300, 400, 500, 600, 700 |
| f1 | `line` | vertical | 1 | 2 | 13 | 52 | 部分 | 100, 200, 300, 400, 500, 600, 700 |

- **f1** Figure 14: / SCS insured losses from 2000 to 2025 YTD; US compared to the rest of the world / Loss Data & Graphic: Gallagher Re　[图下方]　单位 `Insured Loss (USD bn; Today's Dollars)`
  - 来源行：Figure 14: SCS insured losses from 2000 to 2025 YTD; US compared to the rest of the world   Loss Data & Graphic: Gallagher Re
- **f1** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest drawn tick is '100'; baseline sits below it with no zero tick label |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Previous year values in 2025 USD using US CPI ... Data is thru September 2025.' under plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'United States' and 'Rest of World' swatches sit in a row below the year axis |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | four ruled summary columns 'US SCS YTD: Economic losses reached USD61 billion...' above the two-column body text |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis title carries 'USD bn; Today's Dollars'; ticks read only 100...700 |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'Insured Loss (USD bn; Today's Dollars)' set vertically along the left axis |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '648' and '253' printed to the right of the two line endpoints |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | ticks every two years '2000, 2002, ... 2024' while data appears annual through 2025 |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | f1 | **无** | endpoint numbers 648 and 253 label each curve's terminus beside the mark |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | f1 | **无** | both curves drawn as dashed lines, dark navy 'United States' and pale blue 'Rest of World' |

词表 65 项，本页出现 10 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `tick_labels_without_axis_line_marks` | f1 | y ticks '700-','600-' drawn as small dashes with no axis rule or gridlines across the panel | 没有网格线，读取中间年份的数值只能靠与左侧短刻度对齐，误差被放大。 |
| `cumulative_running_total_series` | f1 | lines rise monotonically to 648 and 253, labelled 'SCS insured losses from 2000 to 2025 YTD' | 曲线是累计值而非年度值，若把某年读数当年度损失将完全错误。 |
| `note_line_beside_legend` | f1 | small note 'Previous year values in 2025 USD...' printed on same line to the right of legend | 注释与图例同行，解析时易被并入图例文本，单位口径（2025 USD）可能丢失。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

刻度间隔为100 USD bn，跨度约55像素，图内无网格线，仅左侧短刻度；要把中段读数（如410、165、55）控制在5%容差内意味着410只允许约±20 bn即约11像素的误差，而两条虚线本身线宽与虚线间断已达数像素，且x轴只每两年一个刻度，需在刻度间插值定位年份，双重误差使像素读数最难达标。相比之下标签只需系列名＋年份两个键，648与253已印在图上。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | 新增 cumulative_running_total_series（累计序列标记） | 记录字段中为序列增加 value_semantics 字段（annual / cumulative） | 累计曲线 vs 年度曲线：检验模型是否把累计终值误读为当年数值 |
| P1 | 通用 | 补充 sparse_time_ticks 与无网格线组合的精度衡量 | 样式条件行：gridline=none 且 x 轴刻度间隔为 2 年 | 有无水平网格线时中段点位读数误差分布 |
| P6 | 一类出版方 | inline_series_labels / value_label_outside 仅标端点的情形 | 标签样式字段：label_scope = endpoint_only | 仅端点带数值标签 vs 全点标注，对可检索值数量的影响 |
| P7 | 这份文档自己的习惯 | 标题块位于图下方且编号、标题、来源同行（Figure 14: ... Loss Data & Graphic: Gallagher Re） | 标题字段拆分：figure_number / title / source 并记录 placement=below | 标题在图下且与来源同行时，标题能否作为表格上方粗体上下文被导出 |
