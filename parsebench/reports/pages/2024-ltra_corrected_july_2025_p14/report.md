# 2024-ltra_corrected_july_2025_p14

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2024-ltra_corrected_july_2025 | `need_estimate` | 10 | 10 |

该页左栏为MRO-SaskPower正文与Table 3结果表，右栏为Figure 5（MRO-SPP五年夏季规划备用容量率分组柱状图，含参考裕度短横线系列）及Table 4结果表。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 29.5 | `2025` · `Anticipated Reserve Margin (%)` | 10% | f2 | the 2025 Anticipated Reserve Margin (%) bar | 否 | `Figure 5: MRO-SPP Five-Year Planning Reserve Margin–Summer` · `2025` · `Anticipated Reserve Margin (%)` |
| 2 | 30.5 | `2025` · `Prospective Reserve Margin (%)` | 10% | f2 | the 2025 Prospective Reserve Margin (%) bar (the 2028 light bar reads about the same) | 否 | `Figure 5: MRO-SPP Five-Year Planning Reserve Margin–Summer` · `2025` · `Prospective Reserve Margin (%)` |
| 3 | 19.0 | `2025` · `Reference Margin Level (%)` | 10% | f2 | the Reference Margin Level (%) dash, drawn at the same height in all five year slots | 否 | `Figure 5: MRO-SPP Five-Year Planning Reserve Margin–Summer` · `2025` · `Reference Margin Level (%)` |
| 4 | 32.0 | `2026` · `Anticipated Reserve Margin (%)` | 10% | f2 | the 2026 Anticipated Reserve Margin (%) bar | 否 | `Figure 5: MRO-SPP Five-Year Planning Reserve Margin–Summer` · `2026` · `Anticipated Reserve Margin (%)` |
| 5 | 34.0 | `2026` · `Prospective Reserve Margin (%)` | 10% | f2 | the 2026 Prospective Reserve Margin (%) bar, tallest in the figure | 否 | `Figure 5: MRO-SPP Five-Year Planning Reserve Margin–Summer` · `2026` · `Prospective Reserve Margin (%)` |
| 6 | 31.0 | `2027` · `Anticipated Reserve Margin (%)` | 10% | f2 | the 2027 Anticipated Reserve Margin (%) bar | 否 | `Figure 5: MRO-SPP Five-Year Planning Reserve Margin–Summer` · `2027` · `Anticipated Reserve Margin (%)` |
| 7 | 32.5 | `2027` · `Prospective Reserve Margin (%)` | 10% | f2 | the 2027 Prospective Reserve Margin (%) bar | 否 | `Figure 5: MRO-SPP Five-Year Planning Reserve Margin–Summer` · `2027` · `Prospective Reserve Margin (%)` |
| 8 | 31.5 | `2028` · `Anticipated Reserve Margin (%)` | 10% | f2 | the 2028 Anticipated Reserve Margin (%) bar | 否 | `Figure 5: MRO-SPP Five-Year Planning Reserve Margin–Summer` · `2028` · `Anticipated Reserve Margin (%)` |
| 9 | 29.5 | `2029` · `Anticipated Reserve Margin (%)` | 10% | f2 | the 2029 Anticipated Reserve Margin (%) bar | 否 | `Figure 5: MRO-SPP Five-Year Planning Reserve Margin–Summer` · `2029` · `Anticipated Reserve Margin (%)` |
| 10 | 28.5 | `2029` · `Prospective Reserve Margin (%)` | 10% | f2 | the 2029 Prospective Reserve Margin (%) bar, shortest bar in the figure | 否 | `Figure 5: MRO-SPP Five-Year Planning Reserve Margin–Summer` · `2029` · `Prospective Reserve Margin (%)` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `other · data table` | na | 1 | 3 | 4 | 12 | 全部 | （不画值轴） |
| f2 | `grouped_bar` | vertical | 1 | 3 | 5 | 15 | 无 | 0.0%, 5.0%, 10.0%, 15.0%, 20.0%, 25.0%, 30.0%, 35.0%, 40.0% |
| f3 | `other · data table` | na | 1 | 3 | 4 | 12 | 全部 | （不画值轴） |

- **f1** Table 3 / MRO-SaskPower ProbA Summary of Results　[图上方]　（标题里没有单位）
- **f2** Figure 5 / MRO-SPP Five-Year Planning Reserve Margin–Summer　[图下方]　（标题里没有单位）
  - 来源行：','type_other':''
- **f3** Table 4 / MRO-SPP ProbA Summary of Results　[图上方]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f2 | 有 | two bars side by side in each year slot, dark and light blue, 2025 through 2029 |
| `mixed_marks` | 同面板混合图元（bar + line） | f2 | 有 | bars plus short horizontal dash markers overlaid on the same panel and axis |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f2 | **无** | legend entry "Reference Margin Level (%)" drawn as a short black dash at each year near 19% |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | "Table 3", "Figure 5" and "Table 4" each numbered and captioned separately on one page |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | italic small print under the table: "* Year 2026 Results from the 2022 ProbA provided for trending" |
| `source_note_lines` | source / note 行在图下方 | f3 | 有 | italic small print under the table: "* Year 2026 Results from the 2022 ProbA provided for trending" |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | legend row sits under the plot area, between plot and the "Figure 5" caption |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f1 | 有 | bordered table with blue banner "Table 3: MRO-SaskPower ProbA Summary of Results" and header row |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f3 | 有 | bordered table with blue banner "Table 4: MRO-SPP ProbA Summary of Results" and header row |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f2 | **无** | left column body text "MRO-SPP New resource capacity..." runs level with Figure 5's plot band |
| `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | f2 | **无** | legend reads "Anticipated Reserve Margin (%)", "Prospective Reserve Margin (%)", "Reference Margin Level (%)" |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | column header "2026*" with "* Year 2026 Results from the 2022 ProbA provided for trending" below |
| `footnote_marker` | 标题或标签里的脚注上标 | f3 | **无** | column header "2026*" and italic "* Year 2026 Results from the 2022 ProbA provided for trending" |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | row labels spelled out in full, e.g. "LOLH (hours per year)", "Operable On-Peak Margin" |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | faint horizontal rules across the plot at the 30.0%/35.0% levels, no vertical rules |

词表 65 项，本页出现 12 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `bold_value_columns` | f3 | the "2026" and "2028" data cells are bold (0.00, 6.61, 19.5%, 16.0%) while "2026*" cells are not | 加粗把当期ProbA结果与用于趋势对比的历史列区分开，读数时必须靠字重而非表头才能判断数值归属。 |
| `asterisked_duplicate_column_header` | f1 | two adjacent columns headed "2026*" and "2026" differing only by the asterisk | 同一行有两个2026值，定位某一个数必须把星号一起作为定位键，否则无法区分117.0与75.64。 |
| `screenshot_cursor_artifact` | f2 | a mouse arrow cursor is drawn inside the plot area next to the 2025 group | 图区内存在非数据像素，可能被误认作标记，读取2025组柱顶时需排除该干扰。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

Figure 5上没有任何数值标签，10根柱与5个参考横线全靠像素对轴读取；刻度为5.0%一格（约43像素/5%，即8.7像素/1个百分点）。待核的9个柱值挤在28.5–34.0之间，相邻类别之差常只有0.5个百分点（2027 Anticipated 31.0 与 2028 Anticipated 31.5，2025 Prospective 30.5 与 2028 Prospective 30.5几乎相同），要把某个数正确绑到某一年某一系列上，所需精度约±0.25pp，远严于5%容差（30.0的5%≈1.5pp）——容差内会同时命中多个柱，读数与归属都容易错配。相比之下标签只需“年份+图例名”两个键，标题也以粗体独立成行，不是主要瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | tick_marker_as_series（短横线作为独立系列，与分组柱共用同一数值轴） | 图表生成条件行中新增一个系列渲染类型字段（series_mark=dash_tick），并在记录中为该系列保留每类别数值 | “含短横线阈值系列 vs 仅分组柱”一行：比较该系列数值是否被抽取为独立表行 |
| P6 | 一类出版方 | unit_in_series_name（图例名内嵌“(%)”而数值轴刻度已带%） | 样式字段中单位位置维度：unit_position=series_name 且 tick_format=percent_with_decimal（0.0%） | “单位在图例名 vs 单位在轴标题”一行，检查导出表头是否保留(%) |
| P7 | 通用 | 标题块位于图下（placement=below，编号+标题合排一行“Figure 5: ...”） | 标题记录拆分为number/title/subtitle/unit与placement字段，并在页面导出中控制标题相对表格的位置 | “标题在表上方 vs 标题在表下方”一行，测context键能否被检索到 |
| P3 | 这份文档自己的习惯 | data_table_as_figure配合asterisked_duplicate_column_header与bold_value_columns | 新增“表格即图”的生成家族，其列头允许重复年份+脚注星号，单元格支持字重编码 | “列头唯一 vs 列头仅靠星号区分”一行，检验定位键是否足以唯一寻址 |
