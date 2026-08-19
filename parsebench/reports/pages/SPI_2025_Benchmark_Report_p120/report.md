# SPI_2025_Benchmark_Report_p120

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| SPI_2025_Benchmark_Report | `untagged` | 4 | 0 |

该页含 Figure 25（三面板柱状图，2020–2024 的三项客户关系 KPI 趋势）与 Table 117（客户关系支柱五年趋势数据表），以及正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 10.6% | `Year-over-year Change in PS Revenue` · `2021` | 1% | f1 | the 2021 bar in the "Year-over-year Change in PS Revenue" panel (also the 2021 cell of the same-named row in Table 117) | 是 | `Year-over-year Change in PS Revenue` · `2021` |
| 2 | 29.3% | `Percentage of New Clients` · `2022` | 1% | f1 | the 2022 bar in the "Percentage of New Clients" panel | 是 | `Percentage of New Clients` · `2022` |
| 3 | 7.6% | `Service discount given` · `2020` | 1% | f1 | the 2020 bar in the "Service discount given" panel | 是 | `Service discount given` · `2020` |
| 4 | 9.1% | `Service discount given` · `2024` | 1% | f1 | the 2024 bar in the "Service discount given" panel | 是 | `Service discount given` · `2024` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 3 | 1 | 5 | 15 | 全部 | 0%, 2%, 4%, 6%, 8%, 10%, 12% \| 25%, 26%, 27%, 28%, 29%, 30%, 31%, 32% \| 0%, 1%, 2%, 3%, 4%, 5%, 6%, 7%, 8%, 9%, 10% |
| f2 | `other · data table` | na | 1 | 6 | 4 | 24 | 全部 | （不画值轴） |

- **f1** Figure 25 / Client Relationships Trends of Note　[图上方]　（标题里没有单位）
  - 来源行：Source: SPI Research, February 2025
- **f2** Table 117 / Client Relationships Pillar 5-year Trend　[图上方]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left panel tops at 12%, middle runs 25%-32%, right runs 0%-10% |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | middle panel's lowest tick is "25%", bars for 28.2% and 31.3% look far apart |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | three same-form bar panels side by side, each with years 2020-2024 |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | "Figure 25:  Client Relationships Trends of Note" and "Table 117:  Client Relationships Pillar 5-year Trend" separately numbered |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: SPI Research, February 2025" in small bold italics under the figure frame |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f2 | 有 | bordered table with orange header row "Key Performance Indicator (KPI)", captioned "Table 117: ..." |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | bold small titles over each panel: "Year-over-year Change in PS Revenue", "Percentage of New Clients", "Service discount given" |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | "8.7%", "10.6%", "29.3%", "9.1%" printed inside the top of each bar |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f2 | **无** | row labels like "New logo clients - existing services" fill a wide left column |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole plot area behind the bars carries a cream/beige tint |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at each percent tick, no vertical rules in the panels |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f2 | **无** | the "5-year avg." column cells are tinted cream while other value cells are white/grey |

词表 65 项，本页出现 12 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `rounded_frame_around_panels` | f1 | an orange rounded-rectangle border encloses all three panels and their titles as one block | 边框把三个面板包成一个图形单元，读值时必须先按面板标题切分，否则会把三条不同量纲的轴混为一张表。 |
| `percent_sign_on_every_tick` | f1 | every tick reads "2%", "27%", "9%"; no separate unit line anywhere on the figure | 单位只存在于刻度文字里，表格导出时若丢掉百分号，数值 9.1 与 9.1% 无法区分。 |
| `table_column_header_band` | f2 | solid orange header band with white text: "Key Performance Indicator (KPI)  5-year avg.  2020 ... 2024" | 列头是唯一的年份定位键，若解析器把彩带当图像而非表头，行内数值将失去年份标签。 |

## 5 · 难在哪

卡在 **第四步 · 表外上下文**。

四个待测值都以标签形式印在柱上（10.6%、29.3%、7.6%、9.1%），读数本身不成问题；中间面板 1% 一格、轴从 25% 起，如果靠像素读 29.3% 误差会超过 5% 容差，但标签已给出。真正卡住的是上下文：三个面板的类别轴完全相同（2020–2024），要唯一定位 9.1% 必须同时带 "Service discount given" 与 "2024"，而面板标题只是图内小号粗体文字，既不是图题也不是表头；一旦解析器只输出一个 5 列表格而丢掉面板名，2020 列会同时对应 8.7%、28.2%、7.6% 三个值。此外 10.6% 在 Table 117 中另有一份带行名的副本，容易与图内标签串位。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | per_panel_axis_range 与 axis_starts_above_zero（中间面板 25%–32%） | 条件行中新增“同一图内各面板轴起点/量程不一致”的样式字段，并在记录里为每个面板单独存 axis_min/axis_max | 轴起点是否为零 × 各面板量程是否一致，对读值误差率的影响 |
| P2 | 通用 | panel_title_per_panel（面板名进入定位键） | 导出记录的 key 结构增加 panel_key，面板标题以粗体行写在对应子表之上 | 面板名作为表上方粗体标题 vs 作为表内一列 vs 缺失，三档对定位命中率的影响 |
| P7 | 通用 | 图题拆分字段（Figure 25 / 标题 / Source 行）与 data_table_as_figure（Table 117）并存 | 页面级 markdown 导出：图号+标题作为标题行、Source 作为图下小字行；表格类图形单独标记 | 同页“图+表”双编号时，标题块位置（表上/表下）对上下文匹配的影响 |
| P6 | 这份文档自己的习惯 | highlighted_category（表中 "5-year avg." 列单独着色） | 样式字段中加入“汇总列/行着色”开关，记录里标注该列为聚合而非时间点 | 是否存在着色汇总列，对模型误把均值当年度值的比例的影响 |
