# 7c6b23db-en_p57

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 7c6b23db-en | `3d_chart+need_estimate` | 10 | 10 |

该页为IEA《Energy Technology Perspectives 2023》第57页，正文两段加一幅编号图1.11，图内含三个异质面板：两个堆叠柱面板（Average yearly CAPEX、Cumulative CAPEX）和一个用双箭头表示投资决策可用时间的时间轴面板。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 7 | `Average yearly CAPEX` · `2016-2021` · `Copper mining` | 50% | not_found | no mark of this size can be isolated; '7' appears only as the footnote marker after 'USD 1.2 trillion' in body text | 否 | — |
| 2 | 40 | `Average yearly CAPEX` · `2016-2021` | 20% | f1 | total height of the 2016-2021 stacked bar in the left panel | 否 | `Figure 1.11` · `Average yearly CAPEX` · `2016-2021` · `Billion USD` |
| 3 | 35 | `Average yearly CAPEX` · `2023-2030` · `Copper mining` | 20% | f1 | the 2016-2021 'Clean technology manufacuring' (blue) segment in the left panel | 否 | `Figure 1.11` · `Average yearly CAPEX` · `2016-2021` · `Clean technology manufacuring` |
| 4 | 75 | `Average yearly CAPEX` · `2023-2030` · `Clean technology manufacuring` | 10% | f1 | the 2023-2030 'Clean technology manufacuring' (blue) segment in the left panel | 否 | `Figure 1.11` · `Average yearly CAPEX` · `2023-2030` · `Clean technology manufacuring` |
| 5 | 150 | `Average yearly CAPEX` · `2023-2030` | 10% | f1 | total height of the 2023-2030 stacked bar in the left panel (also a printed tick label '150') | 否 | `Figure 1.11` · `Average yearly CAPEX` · `2023-2030` · `Billion USD` |
| 6 | 250 | `Cumulative CAPEX` · `2023-2030` · `Copper mining` | 20% | f1 | the 'Copper mining' (red) segment of the 2023-2030 bar in the middle panel | 否 | `Figure 1.11` · `Cumulative CAPEX` · `2023-2030` · `Copper mining` |
| 7 | 150 | `Cumulative CAPEX` · `2023-2030` · `Other Critical mineral mining` | 20% | f1 | the 'Other Critical mineral mining' (orange) segment of the 2023-2030 bar in the middle panel | 否 | `Figure 1.11` · `Cumulative CAPEX` · `2023-2030` · `Other Critical mineral mining` |
| 8 | 150 | `Cumulative CAPEX` · `2023-2030` · `Critical mineral processing` | 20% | f1 | the 'Critical mineral processing' (yellow) segment of the 2023-2030 bar in the middle panel | 否 | `Figure 1.11` · `Cumulative CAPEX` · `2023-2030` · `Critical mineral processing` |
| 9 | 650 | `Cumulative CAPEX` · `2023-2030` · `Clean technology manufacuring` | 10% | f1 | the 'Clean technology manufacuring' (blue) segment of the 2023-2030 bar in the middle panel | 否 | `Figure 1.11` · `Cumulative CAPEX` · `2023-2030` · `Clean technology manufacuring` |
| 10 | 1200 | `Cumulative CAPEX` · `2023-2030` | 5% | f1 | total height of the 2023-2030 stacked bar in the middle panel (the 'USD 1.2 trillion' total) | 否 | `Figure 1.11` · `Cumulative CAPEX` · `2023-2030` · `Billion USD` |

**程序核对**（模型没有看到左半的标签列）：

- 有值没能落到任何一个图元上——1 of 10 values could not be put on a mark
- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: 35

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 3 | 4 | 2 | 16 | 无 | 0, 50, 100, 150, 200 (Average yearly CAPEX); 0, 500, 1 000, 1 500 (Cumulative CAPEX); x ticks 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030 (Time available for final investment decision) |

- **f1** Figure 1.11 / Global investment in selected clean energy supply chains needed to bring online enough capacity in 2030 in the NZE Scenario, by supply chain step　[图上方]　单位 `Billion USD`
  - 来源行：Sources: IEA analysis based on company announcement; Bartholomeusz (2022); S&P Capital (2022).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each bar in 'Average yearly CAPEX' and 'Cumulative CAPEX' stacks red, orange, yellow, blue segments |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left panel axis 0-200, middle panel axis 0-1 500; readings cannot be carried across |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one legend row under all three panels: 'Copper mining ... Clean technology manufacuring' |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Notes: CAPEX = capital expenditures...' and 'Sources: IEA analysis based on company announcement...' under the plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend sits below the three plots, above the 'IEA. CC BY 4.0.' line |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | two stacked-bar panels beside 'Time available for final investment decision' drawn as double-headed arrows |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | bold titles 'Average yearly CAPEX', 'Cumulative CAPEX', 'Time available for final investment decision' above each panel |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | ticks are bare numbers 0, 50, 100...; scale word only in axis title 'Billion USD' |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | 'Final investment decision year' printed under the 2023-2030 tick row of the third panel |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'Billion USD' set vertically along the left axis of the first two panels |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | superscript 7 after 'around USD 1.2 trillion,' with footnote 7 at page bottom |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | category ticks read '2016-2021' and '2023-2030', multi-year ranges rather than single years |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 50/100/150/200 and 500/1 000/1 500; no vertical rules |

词表 65 项，本页出现 13 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `arrow_range_timeline_panel` | f1 | third panel shows four double-headed arrows spanning 2023 to about 2025-2028 on a year axis | 读数不是柱高而是箭头两端的年份区间，行键必须给出起止年而非单一数值。 |
| `category_identified_by_legend_colour_only` | f1 | the four arrows carry no labels; only colour matches the legend series names | 第三面板每条箭头无文字标签，表格行只能靠图例颜色名称对应，解析器易漏掉该面板全部行。 |
| `key_message_line_below_figure` | f1 | bold blue line 'Most of the supply chain investments needed to meet NZE Scenario targets in 2030...' under sources | 图的核心结论（七倍、2023-2025）写在图外正文行里，取值时的语境需从该行而非表格获得。 |
| `licence_line_below_figure` | f1 | 'IEA. CC BY 4.0.' printed right-aligned between legend and the Notes block | 该行夹在图例与注释之间，容易被当作来源行，影响注释/来源的切分与定位。 |
| `space_grouped_thousands_ticks` | f1 | middle panel ticks printed '1 000' and '1 500' with a space separator | 千位用空格分隔，数值检索时'1 000'与'1000'不匹配，取值字符串需归一化。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

取值精度是最大瓶颈。中间面板轴刻度为0、500、1 000、1 500，四段共约200像素高，1个单位约0.4像素；要把150这一段读到±5%（即±7.5 Billion USD）只有约3像素余量，而三段150/150/250彼此仅相差约100单位（约40像素），颜色带又极窄，几乎无法在容差内区分。左面板刻度间隔50，读35与40（相差5，约6像素）同样紧张。标签层面虽然需要面板名+期间+图例名三个键（且150在三处重复），但这些标签都是页面上逐字可得的；第三面板箭头无数值可读，只能给区间。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | 新组件 arrow_range_timeline_panel（双箭头时间区间面板）与 heterogeneous_panel_types 的组合 | 图形族生成条件行：允许同一编号图内混合堆叠柱面板与箭头区间面板，并为箭头记录起止年字段 | 异质面板图（柱+箭头区间）开/关，对比含箭头面板时行键与数值召回率 |
| P2 | 通用 | per_panel_axis_range 与 panel_title_per_panel 一并进入行键（panel_key） | 记录字段：给每个数值加 panel_key='Average yearly CAPEX'/'Cumulative CAPEX' | panel_key 进入键 vs 不进入：同页出现三个数值均为150时的唯一定位成功率 |
| P6 | 通用 | unit_in_axis_or_title + rotated_axis_title（'Billion USD' 竖排轴标题，刻度为裸数字） | 样式字段：单位位置增加“竖排轴标题”选项，刻度不带单位 | 单位位置（竖排轴标题 / 标题内 / 刻度内）三档，对数值+单位联合检索命中率 |
| P6 | 一类出版方 | 刻度数字格式 space_grouped_thousands_ticks（'1 000'、'1 500'） | 样式字段 tick_format：千位分隔符可为空格、逗号或无 | 千位分隔符三档，对四位数值（1200、1 000）字符串匹配率的影响 |
| P7 | 这份文档自己的习惯 | 标题拆分与图外结论行（two-line 标题 + key_message_line_below_figure + 'IEA. CC BY 4.0.'） | heading 字段：figure_number/title/subtitle/unit 与结论行位置分别建模 | 标题块导出为粗体标题 vs 并入表格前后文：图号+双行标题的语境命中率 |
