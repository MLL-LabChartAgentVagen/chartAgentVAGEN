# World_Inequality_Report_2026_p198

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `need_estimate` | 10 | 10 |

这是《世界不平等报告》越南国家页（第198页）：左栏为正文与地图，右栏含一个编号表格（Table 1 不平等概览）和一张编号折线图（Figure 1 前10%与后50%收入份额），下方各带 Interpretation 与 Sources 小字。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 48 | `Top 10%` · `1900` | 5% | f2 | the Top 10% line at the left edge of the series, near the 1900 tick | 否 | `Figure 1:` · `Top 10%` · `1900` · `Income share (% total)` |
| 2 | 16 | `Bottom 50%` · `1900` | 10% | f2 | the Bottom 50% line at the left edge of the series, near the 1900 tick | 否 | `Figure 1:` · `Bottom 50%` · `1900` · `Income share (% total)` |
| 3 | 49 | `Top 10%` · `1940` | 5% | f2 | the Top 10% local peak just before the 1940 tick | 否 | `Figure 1:` · `Top 10%` · `1940` · `Income share (% total)` |
| 4 | 16 | `Bottom 50%` · `1940` | 5% | f2 | the Bottom 50% line at about the 1940 tick | 否 | `Figure 1:` · `Bottom 50%` · `1940` · `Income share (% total)` |
| 5 | 45 | `Top 10%` · `1960` | 5% | f2 | the Top 10% line at about the 1960 tick, after the dip to 40% | 否 | `Figure 1:` · `Top 10%` · `1960` · `Income share (% total)` |
| 6 | 18 | `Bottom 50%` · `1960` | 10% | f2 | the Bottom 50% local peak between the 1940 and 1960 ticks | 否 | `Figure 1:` · `Bottom 50%` · `1960` · `Income share (% total)` |
| 7 | 45 | `Top 10%` · `1980` | 5% | f2 | the Top 10% plateau around the 1980-2000 ticks | 否 | `Figure 1:` · `Top 10%` · `1980` · `Income share (% total)` |
| 8 | 16 | `Bottom 50%` · `1980` | 10% | f2 | the Bottom 50% flat stretch around the 1980-2000 ticks | 否 | `Figure 1:` · `Bottom 50%` · `2000` · `Income share (% total)` |
| 9 | 43 | `Top 10%` · `2020` | 5% | f2 | the Top 10% line at the right end of the series (2024); the value 43% also appears in the Interpretation text and as 43.2% in Table 1 | 否 | `Figure 1:` · `Top 10%` · `2020` · `Income share (% total)` |
| 10 | 16 | `Bottom 50%` · `2020` | 10% | f2 | the Bottom 50% line at the right end of the series (2024); Table 1 gives 15.8% for Bottom 50% share of total income | 否 | `Figure 1:` · `Bottom 50%` · `2020` · `Income share (% total)` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: 16

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `other · bordered data table` | na | 1 | 4 | 5 | 24 | 全部 | （不画值轴） |
| f2 | `line` | vertical | 1 | 2 | 7 | 120 | 无 | 0%, 10%, 20%, 30%, 40%, 50%, 60% |

- **f1** Table 1: / Inequality outlook – Vietnam　[图上方]　（标题里没有单位）
  - 来源行：Sources and series: wir2026.wid.world/methodology.
- **f2** Figure 1: / Top 10% and bottom 50% income shares in Vietnam, / 1980-2024　[图上方]　单位 `Income share (% total)`
  - 来源行：Sources and series: wir2026.wid.world/methodology.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | "Table 1: Inequality outlook – Vietnam" and "Figure 1: Top 10% and bottom 50% income shares in Vietnam" separately captioned |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Interpretation: Country has a transparency index of 5/20..." and "Sources and series: wir2026.wid.world/methodology." |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | "Interpretation: The Top 10% income share is equal to 43% in 2024..." then "Sources and series:" line |
| `legend_inside_plot` | 图例画在绘图区内部 | f2 | **无** | both series-name boxes are drawn over the plot area itself |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f1 | 有 | bordered table with green/red header cells, captioned "Table 1: Inequality outlook – Vietnam" |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | left column prose "In Vietnam, inequality is moderate..." runs level with Table 1 and Figure 1 |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | scale word only in axis title "Income share (% total)" |
| `rotated_axis_title` | 轴标题竖排 | f2 | 有 | "Income share (% total)" set vertically along the left axis |
| `rotated_x_ticks` | x 刻度标签旋转 | f2 | 有 | year labels 1900...2020 turned about 45 degrees under the axis |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f2 | 有 | ticks every 20 years (1900, 1920, ... 2020) while the lines kink roughly yearly |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | f2 | **无** | boxed red "Top 10%" above the red line, boxed green "Bottom 50%" under the green line; no legend |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f2 | **无** | two lines spanning about 1900-2024 with near-yearly vertices, roughly 120 plotted points |

词表 65 项，本页出现 11 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `two_level_column_headers` | f1 | green "Income" and "Wealth" banners span red sub-headers "Avg. Income (PPP €)" / "Share of total (%)" | 取一个单元格需同时用上层分组名与下层列名，否则「Share of total (%)」有两列重名而无法唯一定位。 |
| `appended_subtable_different_columns` | f1 | below Top 1% a new banner row "Year \| 2014 \| 2024" with rows "Top 10% to Bot. 50% Income gap", "Female labor share" | 同一编号表内下半段换了列定义（年份而非收入/财富），读值时不能沿用上半段表头。 |
| `title_range_mismatch_axis_span` | f2 | title says "1980-2024" but x ticks run 1900 to 2020 with data from about 1900 | 按标题的年份区间去定位点会整体错位，必须以轴刻度而非标题判断横坐标。 |
| `qr_code_in_page_header` | page | QR code printed at top right beside the "VIETNAM" heading, not under either figure | 页面级数据入口不属于任一图的 source 行，导出时应与图注区分，否则会被误挂到 Figure 1。 |
| `colored_header_banner_cells` | f1 | green banners "Income", "Wealth", "Year" and red cells "2014", "2024", "Avg. Income (PPP €)" | 颜色区分表头层级而非数据，解析时需知道哪些带色单元格是标签行而非数值行。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

Figure 1 上没有任何数字标签，全部十个待测值都要用像素对轴读出。纵轴刻度间隔为10个百分点、整幅高度只覆盖0%–60%，而 Bottom 50% 约16%时5%的容差只有约0.8个百分点，相当于不足半个刻度间隔的十分之一；同时横轴只有1900/1920/.../2020七个每20年的刻度，近乎逐年的折线要在两刻度之间内插定位年份，年份错一格就跨过45→49这样超过容差的落差。相比之下 Table 1 已把43.2%、15.8% 等数字印全，标签也齐备，所以卡点在读值本身。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | inline_series_labels 与 legend_inside_plot 的组合（无图例、系列名以带框标签压在线上） | 图例样式字段：新增 legend_placement=inline_boxed，并在生成记录里把系列名写入绘图区注记而非图例块 | 「系列名仅以内嵌带框标签出现 vs 常规外置图例」下的系列识别正确率 |
| P3 | 一类出版方 | new_components 中的 two_level_column_headers 与 appended_subtable_different_columns | 表格型图（data_table_as_figure）的记录结构：列键改为（分组名，列名）二元组，并允许同一表内追加另一套列定义 | 「两级表头/追加子表 vs 单级表头」下单元格寻址键完整率 |
| P1 | 一类出版方 | sparse_time_ticks 与 title_range_mismatch_axis_span | 时间轴条件行：刻度间隔=20年而数据近逐年，且标题声明区间与轴跨度不一致 | 「刻度稀疏且标题年份区间与轴不符 vs 刻度覆盖每个数据点」下横坐标定位误差 |
| P7 | 通用 | 标题拆分：把 "Table 1:"/"Figure 1:" 编号、标题行、换行续行（"1980-2024"）与单位短语 "Income share (% total)" 分成独立字段 | heading 记录字段：figure_number / title / subtitle / unit_text / placement，且单位允许落在旋转轴标题上 | 「标题跨两行且单位只在旋转轴标题 vs 单行标题内含单位」下上下文匹配命中率 |
