# TSLA-Q3-2023-Update-3_p18

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| TSLA-Q3-2023-Update-3 | `3d_chart+need_estimate` | 10 | 10 |

这是特斯拉季度更新演示第18页，标题为「KEY METRICS TRAILING 12 MONTHS (TTM) (Unaudited)」，页面左右并列两幅无编号折线图（YoY Revenue Growth 与 Operating Margin），各含 Tesla、Auto Industry、S&P 500 三条序列，横轴为 Q3-2019 至 Q3-2023 的季度。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 39 | `Tesla` · `Q3-2019` · `YoY Revenue Growth` | 5% | f1 | the Tesla point at Q3-2019, the series' first point just below the 40% gridline | 否 | `YoY Revenue Growth` · `Tesla` · `Q3-2019` |
| 2 | 73 | `Tesla` · `Q1-2022` · `YoY Revenue Growth` | 5% | f1 | the Tesla peak point at Q1-2022, above the 70% gridline | 否 | `YoY Revenue Growth` · `Tesla` · `Q1-2022` |
| 3 | -2.5 | `Auto Industry` · `Q2-2020` · `YoY Revenue Growth` | 10% | f1 | the S&P 500 trough point at Q1-2021, just below the 0% gridline | 否 | `YoY Revenue Growth` · `S&P 500` · `Q1-2021` |
| 4 | 7 | `S&P 500` · `Q3-2021` · `YoY Revenue Growth` | 5% | f1 | the S&P 500 point at Q3-2021, between the 0% and 10% gridlines | 否 | `YoY Revenue Growth` · `S&P 500` · `Q3-2021` |
| 5 | 16.5 | `Tesla` · `Q4-2022` · `Operating Margin` | 5% | f2 | the Tesla peak point at Q4-2022, between the 16% and 18% gridlines | 否 | `Operating Margin` · `Tesla` · `Q4-2022` |
| 6 | 16.2 | `S&P 500` · `Q1-2022` · `Operating Margin` | 5% | f2 | the S&P 500 peak point at Q1-2022, just above the 16% gridline | 否 | `Operating Margin` · `S&P 500` · `Q1-2022` |
| 7 | 5.5 | `Auto Industry` · `Q1-2021` · `Operating Margin` | 10% | f2 | the Auto Industry point at Q1-2021, on the rise between the 4% and 6% gridlines | 否 | `Operating Margin` · `Auto Industry` · `Q1-2021` |
| 8 | 0 | `Tesla` · `Q3-2019` · `Operating Margin` | 5% | f2 | the Tesla first point at Q3-2019, sitting on the 0% gridline | 否 | `Operating Margin` · `Tesla` · `Q3-2019` |
| 9 | 11 | `Tesla` · `Q3-2023` · `Operating Margin` | 5% | f2 | the Tesla last point at Q3-2023, between the 10% and 12% gridlines | 否 | `Operating Margin` · `Tesla` · `Q3-2023` |
| 10 | 10.5 | `S&P 500` · `Q4-2020` · `YoY Revenue Growth` | 5% | f2 | the S&P 500 point at Q4-2020, just above the 10% gridline | 否 | `Operating Margin` · `S&P 500` · `Q4-2020` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: -2.5, 10.5
- 规则需要的键比模型报出的图能提供的多——rules need 3 keys, the richest figure offers 2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 3 | 17 | 49 | 无 | 90%, 80%, 70%, 60%, 50%, 40%, 30%, 20%, 10%, 0%, -10%, -20% |
| f2 | `line` | vertical | 1 | 3 | 17 | 49 | 无 | 18%, 16%, 14%, 12%, 10%, 8%, 6%, 4%, 2%, 0%, -2%, -4% |

- **f1** YoY Revenue Growth　[图上方]　（标题里没有单位）
  - 来源行：Source: OEM financial disclosures, Bloomberg
- **f2** Operating Margin　[图上方]　（标题里没有单位）
  - 来源行：Source: OEM financial disclosures, Bloomberg

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | axis runs to "-20%"; Auto Industry line dips to about -14% around Q3-2020 |
| `negative_values` | 负值 / 零线居中的分叉条 | f2 | **无** | axis runs to "-4%"; Tesla line starts just below the 0% gridline at Q3-2019/Q4-2019 |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately titled charts side by side: "YoY Revenue Growth" and "Operating Margin", each with own axes |
| `source_note_lines` | source / note 行在图下方 | page | 有 | "Source: OEM financial disclosures, Bloomberg" plus two note lines "Auto Industry includes: ..." at page foot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | row "Tesla  Auto Industry  S&P 500" with line swatches under the rotated tick labels |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | row "Tesla  Auto Industry  S&P 500" with line swatches below the plot |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | quarter labels "Q3-2019" ... "Q3-2023" set vertically, turned 90 degrees under the axis |
| `rotated_x_ticks` | x 刻度标签旋转 | f2 | 有 | quarter labels "Q3-2019" ... "Q3-2023" set vertically under the axis |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | time written as "Q3-2019", "Q1-2022" rather than ISO dates |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f2 | **无** | time written as "Q2-2021", "Q4-2022" on the category axis |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at every 10% tick, no vertical rules in the plot |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | faint horizontal rules at every 2% tick, no vertical rules in the plot |

词表 65 项，本页出现 7 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `series_ends_before_axis_end` | page | Auto Industry and S&P 500 lines stop at Q2-2023 while the axis and Tesla continue to Q3-2023 | 最后一个季度只有 Tesla 有值，若表格把 Q3-2023 行的其余两列留空或误填，就会把 Q2-2023 的读数错配到 Q3-2023。 |
| `basis_in_page_header` | page | only the page header says "TRAILING 12 MONTHS (TTM)" and "(Unaudited)"; neither chart title repeats it | 每个读数的口径（TTM、未审计）只写在页眉，图内无任何标注，表格若不带页眉信息，数值含义无法确定。 |
| `percent_sign_on_every_tick` | page | ticks printed as "90%", "-20%", "18%", "-4%" so the unit rides on each tick label | 单位不在标题或轴题上，只能从刻度文本里取「%」，解析时若丢掉百分号，数值会被当作绝对量。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

两幅图 values_printed 都是 none，全部 98 个点必须靠像素对刻度量出来。f2 刻度间距只有 2 个百分点，而 5% 容差在小值上极窄：0 这个点容差为 0（Tesla 在 Q3-2019 实际约 -0.1%），5.5 只容许 ±0.28 个百分点，即不到刻度间距的七分之一；f1 中 -2.5 只容许 ±0.125 个百分点，而刻度间距是 10 个百分点，等于要求读到刻度格的 1/80。相比之下标签只需三键（图题 + 序列名 + 季度），且 17 个季度刻度逐点对应、序列名在图例中明写，寻址并不是主要障碍；真正卡住的是把无标注折线点读到 5% 以内。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | 新组件 series_ends_before_axis_end（序列比时间轴短，末列缺值且无 N/A 标记） | 记录层：每序列的时间跨度独立于面板的类别列表；条件行增加「序列末端截断」 | 「序列长度是否与类别轴一致」单独一行，比较末期缺值时的错配率 |
| P6 | 通用 | P6 中的刻度格式维度：把「%」直接写在每个刻度标签上（90%, -20%, 18%, -4%），而非放在轴题 | 样式字段 tick_format / unit_position，新增 unit_suffix_on_ticks 取值 | 「单位在刻度 vs 在轴题/标题」一行，检验解析出的数值是否保留百分号语义 |
| P7 | 一类出版方 | P7：无编号图的标题字段（figure_number 为空、title 为「YoY Revenue Growth」，口径词只在页眉） | 标题记录字段：number 允许为空，并新增 page_header_basis 与其相对表格的位置 | 「图题存在但无编号、口径词位于页眉」一行，检验上下文键能否被正确附加到表 |
| P1 | 通用 | P1：把折线点的可读精度按刻度间距/序列拥挤度建模（f2 三线在 Q2-2021 附近交叠于 8% 一带） | 条件行 readable 改为 per-mark attainable precision，输入含刻度间距与邻线间距 | 「小值（\|v\|<2）与线交叠区」两类点的可达精度对比一行 |
