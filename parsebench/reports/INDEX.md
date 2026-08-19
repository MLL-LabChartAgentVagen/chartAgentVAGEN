# ParseBench 样例分析

**192 页均匀随机抽样** · 70 份文档 · 1658 条抽查点 · 265 张图 · 模型 `claude-opus-5`。配图版：**[view.html](view.html)**，三个分区与本文一一对应，每一项配一页实例与模型写下的证据原文。逐页报告在 [pages/](pages/)。

三节，各答一个问题，互不重复：

| 节 | 问题 | 里面是什么 |
|---|---|---|
| **1 要改什么** | 我们画不出来的东西，哪些保留、哪些舍弃 | 四份清单 + 组件缺口、类型缺口、标题维度缺口，同一张排序表 |
| **2 基准长什么样** | 这批页面实际是什么样 | 类型配比、标题形态、数值写不写、难点分布、词表全表。**这一节没有待办** |
| **3 能不能信** | 这些数字是怎么来的 | 调用方式、判分、交叉核对、逐页 |

**两条独立的轴，贯穿全文。**一个组件可以出现在四分之三的页面上，而基准根本看不见它——「单位写在轴标题里」出现在 149 / 192 页，而 4,864 条规则里**没有一条**的值或标签引用过那个单位。所以每一行都带两列：

- **影响得分**：它能改变[四步判定](../review/02_chart_metric.md)的哪一步，空就是**基准看不见它**。和「我们有没有」一样，看任何一页之前就按度量定义定死。
- **通用度**：文档分布。同一份文档里出现 20 次是那家出版方的习惯，20 份文档里各一次才是通用惯例。

两列合起来就是 §1.1 的四份清单：**能提分** · **只提升真实性与视觉多样性** · **待定**（数字没能决定：页数太少，或分布压在分界线上）· **舍弃**。

**频次按档位读，不按名次**（n = 192，真实频次 10% 的 95% 置信区间约 ±6 个百分点）：高 ≥ 96 页 · 中 17–95 · 低 ≤ 16。

---

## 1 · 要改什么

**基准里出现、而 `storyline/parsebench_chart/` 没有定义的东西，全在这一节。**不分组件还是图表类型——「这个我们建不建」是同一个问题。

### 1.1 四份清单 · 39 项缺口各归其一

依次问三个已测的问题，所以每一项**恰好落在一份清单里**，没有重叠也没有遗漏：

1. **页数够读出文档分布吗？**（≥ 4 页）不够 → 第三份「待定」。
2. **它能改变四步判定的某一步吗？**（`affects`，按度量定义定死）能 → 第一份。
3. **它是通用画法吗？**（文档分布）是 → 第二份；压在分界线上 → 第三份；明确不是 → 第四份。

第一份和第二份**之间没有汇率**，硬排成一列就得凭空发明一个换算率。

| 清单 | 项数 | 判据 | 怎么处理 |
|---|---|---|---|
| **保留 · 能提分** | 22 | 页数 ≥ 4 · `affects` 非空 | 在这批页面上出现够多次，而且能改变四步判定的某一步。做完 ParseBench 的分数会动。 |
| **保留 · 只提升真实性与视觉多样性** | 8 | 页数 ≥ 4 · `affects` 为空 · 分布 ≥ 0.50 | 度量看不见它，但真实的图普遍这么画。做完分数一格不动，生成的图会更像真实报告页——这是数据集本身的价值，不是刷分。 |
| **待定 · 数字没能决定** | 7 | 页数 < 4，或分布落在 0.40–0.50 | 两个原因之一：页数太少，文档分布读不出来；或者分布正好压在分界线上（0.40–0.50）。**这一档程序不替你决定**——看图，然后把决定写进 README 的 TODO。 |
| **舍弃** | 2 | `affects` 为空 · 分布 < 0.40 | 度量看不见它，而且它明确集中在少数几份文档里（分布 < 0.40）——那是某家出版方的排版习惯，不是通用画法。记录下来，不为它改条件表。 |

**第三份清单是这套分类里最要紧的一格。**「读不出来」和「判定不要」是两回事，混在一起，`error_bars` 只出现 2 页就会被写成「某家出版方的习惯」。通用度那一列印的是比值本身（实际覆盖的文档数 / 这些页最多能覆盖的文档数），0.70 以上通用、0.45 以上常见；落在 0.40–0.50 的一律不判，因为 0.44 与 0.45 分到不同清单是**阈值在说话，不是数据在说话**。

**保留 · 能提分 · 22 项**

在这批页面上出现够多次，而且能改变四步判定的某一步。做完 ParseBench 的分数会动。

| # | key | 组件 | 页数 | 影响哪一步 | 通用度 | 归入 |
|---|---|---|---|---|---|---|
| 1 | `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | 58（30%）| 第3步 标签关联 | 集中（26 / 最多 58 份 = 0.45） | — |
| 2 | `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | 53（28%）| 第2步 找到值 | 常见（32 / 最多 53 份 = 0.60） | P6 |
| 3 | `footnote_marker` | 标题或标签里的脚注上标 | 52（27%）| 第3步 标签关联 | 常见（32 / 最多 52 份 = 0.62） | — |
| 4 | `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | 44（23%）| 第1步 要有表 | 常见（23 / 最多 44 份 = 0.52） | — |
| 5 | `negative_values` | 负值 / 零线居中的分叉条 | 42（22%）| 第2步 找到值 | 常见（21 / 最多 42 份 = 0.50） | P6 |
| 6 | `no_value_axis` | 没有值轴刻度，只有基线 | 42（22%）| 第2步 找到值 | 常见（23 / 最多 42 份 = 0.55） | — |
| 7 | `dense_marks_100plus` | 单张图 ≥100 个图元 | 41（21%）| 第2步 找到值 | 常见（23 / 最多 41 份 = 0.56） | P5 |
| 8 | `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | 34（18%）| 第3步 标签关联 | 通用（26 / 最多 34 份 = 0.76） | P6 |
| 9 | `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | 26（14%）| 第3步 标签关联 | 集中（9 / 最多 26 份 = 0.35） | — |
| 10 | `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | 23（12%）| 第2步 找到值 | 通用（19 / 最多 23 份 = 0.83） | — |
| 11 | `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | 19（10%）| 第2步 找到值 · 第3步 标签关联 | 集中（7 / 最多 19 份 = 0.37） | — |
| 12 | `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | 19（10%）| 第2步 找到值 | 通用（14 / 最多 19 份 = 0.74） | P6 |
| 13 | `pct_stacked` | 百分比堆叠（归一到 100%） | 16（8%）| 第2步 找到值 | 通用（12 / 最多 16 份 = 0.75） | — |
| 14 | `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | 16（8%）| 第3步 标签关联 | 常见（10 / 最多 16 份 = 0.62） | — |
| 15 | `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | 12（6%）| 第3步 标签关联 | 常见（8 / 最多 12 份 = 0.67） | — |
| 16 | `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | 11（6%）| 第1步 要有表 | 通用（8 / 最多 11 份 = 0.73） | — |
| 17 | `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | 11（6%）| 第3步 标签关联 | 通用（11 / 最多 11 份 = 1.00） | P6 |
| 18 | `inline_series_labels` | 没有图例，系列名直接标在线旁 | 11（6%）| 第3步 标签关联 | 通用（10 / 最多 11 份 = 0.91） | — |
| 19 | `icon_category_axis` | 类目轴用图标代替文字 | 9（5%）| 第3步 标签关联 | 常见（5 / 最多 9 份 = 0.56） | — |
| 20 | `total_row_below_axis` | 轴下方一行合计值，与类目对齐 | 6（3%）| 第3步 标签关联 | 通用（5 / 最多 6 份 = 0.83） | — |
| 21 | `step_line_series` | 阶梯线（水平段 + 垂直跳变），不是直连折线 | 4（2%）| 第2步 找到值 | 通用（3 / 最多 4 份 = 0.75） | — |
| 22 | `range_connector_line` | 每个类目两个点用线段连成区间（哑铃图 / 区间图） | 4（2%）| 第2步 找到值 · 第3步 标签关联 | 常见（2 / 最多 4 份 = 0.50） | — |

**保留 · 只提升真实性与视觉多样性 · 8 项**

度量看不见它，但真实的图普遍这么画。做完分数一格不动，生成的图会更像真实报告页——这是数据集本身的价值，不是刷分。

| # | key | 组件 | 页数 | 影响哪一步 | 通用度 | 归入 |
|---|---|---|---|---|---|---|
| 1 | `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | 149（78%）| **不影响** | 通用（59 / 最多 70 份 = 0.84） | P6 |
| 2 | `panel_background` | 绘图区带底色，不是白底 | 49（26%）| **不影响** | 常见（25 / 最多 49 份 = 0.51） | — |
| 3 | `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | 43（22%）| **不影响** | 常见（22 / 最多 43 份 = 0.51） | — |
| 4 | `annotation_callout` | 绘图区内的说明框 / 引线注解 | 33（17%）| **不影响** | 常见（23 / 最多 33 份 = 0.70） | — |
| 5 | `legend_inside_plot` | 图例画在绘图区内部 | 21（11%）| **不影响** | 通用（17 / 最多 21 份 = 0.81） | — |
| 6 | `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | 19（10%）| **不影响** | 常见（10 / 最多 19 份 = 0.53） | — |
| 7 | `dashed_line_series` | 用线型（虚 / 实）区分系列 | 10（5%）| **不影响** | 通用（9 / 最多 10 份 = 0.90） | — |
| 8 | `right_side_y_axis` | 唯一的值轴画在右侧 | 6（3%）| **不影响** | 常见（4 / 最多 6 份 = 0.67） | — |

**待定 · 数字没能决定 · 7 项**

两个原因之一：页数太少，文档分布读不出来；或者分布正好压在分界线上（0.40–0.50）。**这一档程序不替你决定**——看图，然后把决定写进 README 的 TODO。

| # | key | 组件 | 页数 | 影响哪一步 | 通用度 | 归入 |
|---|---|---|---|---|---|---|
| 1 | `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | 45（23%）| **不影响** | 集中（20 / 最多 45 份 = 0.44）　**分布 0.44，压在分界线上** | — |
| 2 | `horizontal_bars` | 横向条形（类目在 y 轴） | 42（22%）| **不影响** | 常见（19 / 最多 42 份 = 0.45）　**分布 0.45，压在分界线上** | — |
| 3 | `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | 41（21%）| **不影响** | 常见（19 / 最多 41 份 = 0.46）　**分布 0.46，压在分界线上** | — |
| 4 | `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | 18（9%）| **不影响** | 常见（9 / 最多 18 份 = 0.50）　**分布 0.50，压在分界线上** | — |
| 5 | `error_bars` | 误差棒 / 置信带 | 2（1%）| **不影响** | 样本不足（2 份）　**页数太少** | — |
| 6 | `broken_axis` | 断轴：轴中间截断并画出断裂标记 | 2（1%）| 第2步 找到值 | 样本不足（2 份）　**页数太少** | — |
| 7 | `stacked_and_grouped` | 堆叠与分组出现在同一张图 | 0（0%）| 第3步 标签关联 | 样本不足（0 份）　**页数太少** | — |

**舍弃 · 2 项**

度量看不见它，而且它明确集中在少数几份文档里（分布 < 0.40）——那是某家出版方的排版习惯，不是通用画法。记录下来，不为它改条件表。

| # | key | 组件 | 页数 | 影响哪一步 | 通用度 | 归入 |
|---|---|---|---|---|---|---|
| 1 | `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | 21（11%）| **不影响** | 集中（6 / 最多 21 份 = 0.29） | — |
| 2 | `axis_title_below_plot` | 值轴标题写在图下方 | 17（9%）| **不影响** | 集中（5 / 最多 17 份 = 0.29） | — |

### 1.2 组件缺口全表 · 39 项

| 档 | key | 组件 | 页数 | 影响哪一步 | 通用度 | 我们为什么画不出来 | 实例与证据 |
|---|---|---|---|---|---|---|---|
| 高 | `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | 149（78%）| **不影响** | 通用 | unit 在 `01` 的 measure 声明里，轴标题与图题都不带它，见 P6 | [2024_Annual_Financial_Review_Upstream_FINAL_p19](pages/2024_Annual_Financial_Review_Upstream_FINAL_p19/report.md)<br>`"billion 2024 dollars" printed under the bold heading; axis shows only $0...$100` |
| 中 | `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | 58（30%）| 第3步 标签关联 | 集中 | `chart_types.md §2` 的类目基数上限 30，且标签不折行 | [(Web_version)_E-Government_Survey_2024_1392024_p172](pages/%28Web_version%29_E-Government_Survey_2024_1392024_p172/report.md)<br>`22 long labels stacked down the y axis, e.g. Online environment-related permit` |
| 中 | `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | 53（28%）| 第2步 找到值 | 常见 | `03 §6` 的 `labeled` 只记布尔，不记位置，见 P6 | [Economic_and_Market_Report-Full_year-2024_p18](pages/Economic_and_Market_Report-Full_year-2024_p18/report.md)<br>`'Others, 1.5%', 'Others, 2.6%', 'Others, 8.5%' boxes sit above the 100 line with pointer arrows` |
| 中 | `footnote_marker` | 标题或标签里的脚注上标 | 52（27%）| 第3步 标签关联 | 常见 | 标签渲染不带脚注标记 | [2025-Business-Megatrends-Outlook_p25](pages/2025-Business-Megatrends-Outlook_p25/report.md)<br>`superscript 26 after personal experiences and trailing the source line; 27 in later paragraph` |
| 中 | `panel_background` | 绘图区带底色，不是白底 | 49（26%）| **不影响** | 常见 | `03 §3` 的「图形细节」与「配色」两维都不含面板底色 | [Goldman_Sachs_BUY_report_p10](pages/Goldman_Sachs_BUY_report_p10/report.md)<br>`the figure sits inside a blue-bordered box with the title inset into its top border` |
| 中 | `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | 45（23%）| **不影响** | 集中 | `03 §3` 配色按系列上色，没有单类目高亮这一取值 | [5._ESM_Staff_Report_on_Comprehensive_Review_p37](pages/5._ESM_Staff_Report_on_Comprehensive_Review_p37/report.md)<br>`first bar's ESM and EFSF segments drawn with hatched/striped fill unlike other bars` |
| 中 | `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | 44（23%）| 第1步 要有表 | 常见 | `03 §5` 的页面元素是纵向堆叠的块，没有与图并排的文字栏 | [2023-05-sigma-01-english_p23](pages/2023-05-sigma-01-english_p23/report.md)<br>`left column pull quote "The pandemic-induced surge in inflation has increased replacement costs in US property." level with figure` |
| 中 | `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | 43（22%）| **不影响** | 常见 | 参考线不是任何族的图元，`chart_types.md` 无此形状 | [Digital_News-Report_2022_p46](pages/Digital_News-Report_2022_p46/report.md)<br>`orange dotted vertical rule crossing all bars at the 17% position, tick at top and bottom` |
| 中 | `horizontal_bars` | 横向条形（类目在 y 轴） | 42（22%）| **不影响** | 常见 | `chart_types.md` 的条件表没有方向这一维 | [2023-05-sigma-01-english_p6](pages/2023-05-sigma-01-english_p6/report.md)<br>`category labels '30-year average (1992−2021)' ... '2022' sit on the y axis, bars grow right` |
| 中 | `negative_values` | 负值 / 零线居中的分叉条 | 42（22%）| 第2步 找到值 | 常见 | `chart_types.md` 的矩形图元自零基线单向延伸，见 P6 | [GWR-2024_Layout_E_RGB_Web_p27](pages/GWR-2024_Layout_E_RGB_Web_p27/report.md)<br>`axis runs to -6; labels '-0.4', '-3.4', '-2.7', '-4.0', '-1.8' below the zero line` |
| 中 | `no_value_axis` | 没有值轴刻度，只有基线 | 42（22%）| 第2步 找到值 | 常见 | `03 §3` 的轴维不含「不画值轴」这一取值 | [2024_healthatglance_rep_en_p187](pages/2024_healthatglance_rep_en_p187/report.md)<br>`no numeric tick labels on any panel; only printed percentages such as "90%", "77%"` |
| 中 | `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | 41（21%）| **不影响** | 常见 | 轴标题位置不是风格向量的维 | [05021ff2-en_p19](pages/05021ff2-en_p19/report.md)<br>`'Total number of merger notifications' printed above the 14 000 tick, not alongside the axis` |
| 中 | `dense_marks_100plus` | 单张图 ≥100 个图元 | 41（21%）| 第2步 找到值 | 常见 | `chart_types.md §2` 的 \|P\|·\|S\| 上限 24 / 20，见 P5 | [Goldman_Sachs_BUY_report_p6](pages/Goldman_Sachs_BUY_report_p6/report.md)<br>`six panels x up to 3 series x quarterly points over 4-8 fiscal years, several hundred plotted points` |
| 中 | `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | 34（18%）| 第3步 标签关联 | 通用 | `time` 列由 start/end/freq 声明，刻度格式化方式不是风格向量的维，见 P6 | [7c6b23db-en_p57](pages/7c6b23db-en_p57/report.md)<br>`category ticks read '2016-2021' and '2023-2030', multi-year ranges rather than single years` |
| 中 | `annotation_callout` | 绘图区内的说明框 / 引线注解 | 33（17%）| **不影响** | 常见 | 说明框不是任何族的图元，`chart_types.md` 无此形状 | [Economic_and_Market_Report-Full_year-2024_p11](pages/Economic_and_Market_Report-Full_year-2024_p11/report.md)<br>`grey rounded boxes '+5.2%', '-6.2%', '-18.2%' with pointer tails drawn over the plot above each pair` |
| 中 | `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | 26（14%）| 第3步 标签关联 | 集中 | `03 §3` 配色按系列上色，颜色不承载数据列 | [2025-EIS_p39](pages/2025-EIS_p39/report.md)<br>`"The colours denote each country's overall performance group based on the 2025 SII"` |
| 中 | `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | 23（12%）| 第2步 找到值 | 通用 | `03 §3` 的轴维没有「值轴起点」这一取值，矩形图元自零基线起算 | [b263dc5d-en_p79](pages/b263dc5d-en_p79/report.md)<br>`lowest tick on the value axis reads 220, not zero, and no break glyph is drawn` |
| 中 | `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | 21（11%）| **不影响** | 集中 | `03 §5` 的图下文本只有图注一种 | [US50419123-White-Paper-Signature-Sept-2025_p16](pages/US50419123-White-Paper-Signature-Sept-2025_p16/report.md)<br>`'For an accessible version of the data in this figure, see Figure 4 Supplemental Data in Appendix 2.'` |
| 中 | `legend_inside_plot` | 图例画在绘图区内部 | 21（11%）| **不影响** | 通用 | `03 §3` 的图例位置只有外置与每面板一个，没有绘图区内 | [2024_Annual_Financial_Review_Upstream_FINAL_p14](pages/2024_Annual_Financial_Review_Upstream_FINAL_p14/report.md)<br>`seven colour-matched region names stacked as text over the plot area between the sales and Latin America bars` |
| 中 | `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | 19（10%）| **不影响** | 常见 | `01` 的 measure 声明有 unit，没有「指数 + 基期」这种口径 | [2025-EIS_p37](pages/2025-EIS_p37/report.md)<br>`"indexed to the EU in 2018"; note: "scores are relative to that of the EU in 2018"` |
| 中 | `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | 19（10%）| 第2步 找到值 | 通用 | `03 §6` 的 `labeled` 只记布尔，不处理拥挤与外移，见 P6 | [(Web_version)_E-Government_Survey_2024_1392024_p62](pages/%28Web_version%29_E-Government_Survey_2024_1392024_p62/report.md)<br>`8 (4.1%) and 7 (3.6%) sit in bottom segments only ~4 units tall, label taller than segment` |
| 中 | `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | 19（10%）| 第2步 找到值 · 第3步 标签关联 | 集中 | `chart_types.md §3` 的五种图元里没有「刻度标记」这一形状 | [2025-EIS_p86](pages/2025-EIS_p86/report.md)<br>`legend entry "Score in 2024" is a short vertical dash drawn at each bar's 2024 position` |
| 中 | `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | 18（9%）| **不影响** | 常见 | 阴影区不是任何族的图元，`chart_types.md` 无此形状 | [9f653ca1-en_p31](pages/9f653ca1-en_p31/report.md)<br>`Panel A has a grey tinted band from mid-2024 across 2025-2027 marking projections` |
| 中 | `axis_title_below_plot` | 值轴标题写在图下方 | 17（9%）| **不影响** | 集中 | 轴标题位置不是风格向量的维 | [2025-EIS_p12](pages/2025-EIS_p12/report.md)<br>`"Summary innovation index in 2025 (indexed to the EU in 2018)" printed under the 0-160 tick row` |
| 低 | `pct_stacked` | 百分比堆叠（归一到 100%） | 16（8%）| 第2步 找到值 | 通用 | 堆叠只记 `value` 与 `cum_start`/`cum_end`；占比要像 pie 那样另记 `share` | [SRI-Insights-August 2025_media_embargo_p4](pages/SRI-Insights-August 2025_media_embargo_p4/report.md)<br>`bands fill to the 100 tick every year on an axis reading 0 to 100, title ends ", %"` |
| 低 | `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | 16（8%）| 第3步 标签关联 | 常见 | 轴标签是一维取值列表 | [5._ESM_Staff_Report_on_Comprehensive_Review_p21](pages/5._ESM_Staff_Report_on_Comprehensive_Review_p21/report.md)<br>`inner tick row "10yr 20yr 5yr..."; outer grouping row "SURE #1 20/10/20" ... "SURE #8 29/03/22"` |
| 低 | `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | 12（6%）| 第3步 标签关联 | 常见 | `02 §4.1` 面板数上限 4 | [7c6b23db-en_p48](pages/7c6b23db-en_p48/report.md)<br>`six panels of the same bar chart: Electric cars, Fuel cell trucks, Heat pumps, Low-emission electricity, hydrogen, synthetic HF` |
| 低 | `inline_series_labels` | 没有图例，系列名直接标在线旁 | 11（6%）| 第3步 标签关联 | 通用 | 系列名只通过图例呈现，`03 §3` 的图例维无「直标」取值 | [2024_healthatglance_rep_en_p45](pages/2024_healthatglance_rep_en_p45/report.md)<br>`no legend; "Italy", "Belgium", "France", "Slovak Republic", "Germany" printed at the right end of each line` |
| 低 | `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | 11（6%）| 第1步 要有表 | 通用 | 投影后每格必有值，缺失不进候选，`02 §3` | [(Web_version)_E-Government_Survey_2024_1392024_p91](pages/%28Web_version%29_E-Government_Survey_2024_1392024_p91/report.md)<br>`Oceania 'Women' row shows only '71%' in the light segment; no Fully digitalized segment or number` |
| 低 | `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | 11（6%）| 第3步 标签关联 | 通用 | unit 在 `01` 的 measure 声明里，不参与标签渲染，见 P6 | [World_Inequality_Report_2026_p146](pages/World_Inequality_Report_2026_p146/report.md)<br>`legend entries read '(% of top 10% educated voting left) minus (% of bottom 90% educated voting left)'` |
| 低 | `dashed_line_series` | 用线型（虚 / 实）区分系列 | 10（5%）| **不影响** | 通用 | `03 §3` 的图形细节维有填充纹理，没有线型 | [Renewables2025_1_p32](pages/Renewables2025_1_p32/report.md)<br>`"REPowerEU target" drawn dashed while "Assessment of final updated NECPs" is solid red` |
| 低 | `icon_category_axis` | 类目轴用图标代替文字 | 9（5%）| 第3步 标签关联 | 常见 | 类目轴只渲染 `dim` 的字符串取值 | [Activate_Consulting_Technology_&_Media_Outlook_2026_(10)_p65](pages/Activate_Consulting_Technology_&_Media_Outlook_2026_%2810%29_p65/report.md)<br>`pictograms of phone, gamepad and desktop precede MOBILE, CONSOLE, PC in the side legend` |
| 低 | `right_side_y_axis` | 唯一的值轴画在右侧 | 6（3%）| **不影响** | 常见 | `chart_types.md` 只有 `compound` 用右轴，单值轴固定在左 | [b3cd580a-3656-44ed-838a-5f2996ff6fc9_p32](pages/b3cd580a-3656-44ed-838a-5f2996ff6fc9_p32/report.md)<br>`the only value scale, 12,000 down to 0, is printed along the right edge of the plot` |
| 低 | `total_row_below_axis` | 轴下方一行合计值，与类目对齐 | 6（3%）| 第3步 标签关联 | 通用 | 记录里没有「轴外的一行汇总值」这种元素 | [Earnings-Presentation-FY24-Q4_1_p9](pages/Earnings-Presentation-FY24-Q4_1_p9/report.md)<br>`row labelled "Returns to shareholders" with $2.7, $2.2, $2.0, $1.6, $3.0 under the axis` |
| 低 | `range_connector_line` | 每个类目两个点用线段连成区间（哑铃图 / 区间图） | 4（2%）| 第2步 找到值 · 第3步 标签关联 | 常见 | 区间线段不是任何族的图元，`chart_types.md` 无此形状 | [ac8b3538-en_p125](pages/ac8b3538-en_p125/report.md)<br>`three coloured dots per country joined by a thin vertical segment in both panels` |
| 低 | `step_line_series` | 阶梯线（水平段 + 垂直跳变），不是直连折线 | 4（2%）| 第2步 找到值 | 通用 | `chart_types.md` 的 `line` 只有点间直连一种画法 | [ac8b3538-en_p61](pages/ac8b3538-en_p61/report.md)<br>`Nominal minimum wage moves in flat treads with vertical risers, e.g. Australia at May-22` |
| 低 | `broken_axis` | 断轴：轴中间截断并画出断裂标记 | 2（1%）| 第2步 找到值 | 样本不足 | `03 §1` 冻结布局，值域到像素域是一段线性映射 | [67c07d7f417ce_p44](pages/67c07d7f417ce_p44/report.md)<br>`double-slash break glyphs drawn on both horizontal arrow axes near their arrowheads` |
| 低 | `error_bars` | 误差棒 / 置信带 | 2（1%）| **不影响** | 样本不足 | 五数只在 `box` 出现，其他类型的值字典只有 `value` | [FPA-guide-to-data-visualization_p8](pages/FPA-guide-to-data-visualization_p8/report.md)<br>`grey Scenarios bands fan from ~118-212 in Jan, text calls it "a statistical risk range"` |
| — | `stacked_and_grouped` | 堆叠与分组出现在同一张图 | 0（0%）| 第3步 标签关联 | 样本不足 | 两个维度分别吃掉 P 与 S，第三维无处可放 | — |

### 1.3 类型缺口

同一个问题问图表类型：条件表里有没有这一族。**类型配比本身不在这里**——那是描述，在 §2。

| 类型 | 图数 | 占比 | 依据 |
|---|---|---|---|
| `other` | 22 | 8% | 模型报 `other` 时自拟名字，见「新类型」 |
| `map` | 3 | 1% | 地理投影不是六族中的任何一族，图元也不在 `§3` 的五种形状里 |

`other` 这一格要拆开看。模型必须给它命名，命名之后分成三堆，**只有第三堆是真的类型缺口**：

| 分类 | 图数 | 是缺口吗 |
|---|---|---|
| **表格** | 13 | 带表头的表格与列表。`data_table_as_figure` 已经是我们有的能力，不是缺口 |
| **不是图** | 6 | 占位、正文块、重复条目。这些本该进 `unreadable`，落到这里说明那个字段还漏 |
| **图形** | 3 | 条件表里没有的画法。**只有这一栏是真的类型缺口** |

**真正是新画法的：**`dumbbell range plot`、`three-marker range plot`、`vertical dumbbell range plot`。

反过来，条件表里有、这份抽样里一张都没出现的 3 种：`box`、`funnel`、`heatmap`。**这不是「白做」**——它们是为别的目标基准留的能力，只说明按 ParseBench 调权重时不该给它们配额（见 P4）。

### 1.4 标题维度缺口

**图题不是一个组件，是一个有五个字段的对象**：图号 / 主标题 / 副标题 / 单位 / 位置。词表里原来有四个 key 在重复记录同样的事（而且是按页记，不是按图记），已经删掉——现在每张图都直接记这五个字段，缺口按维度读：

| 维度 | 实测 | 我们现在 | 归入 |
|---|---|---|---|
| 图号 | 149 / 265 张图有（56%）| FigureSpec 没有 `title` 字段，图号无处可编 | P7 |
| 副标题（标题不止一行） | 88 / 265（33%）| 同上 | P7 |
| 单位写在标题里 | 159 / 265（60%）| unit 在 measure 声明里，一个字都不画出来 | P6 / P7 |
| 位置 | 图上方 231 · 图下方 15 · 无标题 11 · 与图并排 8 | `03 §0` 图注固定在图下方 | P7 |

**位置这一维是四值不是两值**：`2023-05-sigma-01-english_p23` 的 Figure 15 把图号、标题、副标题三行排在**左栏**、与绘图区并排。对第四步的上下文回退来说，侧栏标题在 markdown 里落在哪一段完全取决于解析器怎么切版面块。

**注意**：这一节整体属于上面 1.1 的 B 半——图号出现在 54% 的图上，而 4,864 条规则里只有 14 条（0.14%）把图号当作定位标签。标题主要是**真实性**问题，不是**分数**问题。

## 2 · 基准长什么样

描述，不是待办。**我们画得出来的东西也在这一节**——「已经能画，而且基准上很常见」说明现有能力对得上，那不是缺口。

### 2.1 词表、组件、类型是什么关系

一张图 = **一个类型** + **若干个组件**。

| | 是什么 | 一张图有几个 | 例子 |
|---|---|---|---|
| **类型** | 这张图的画法 | **恰好 1 个**（19 选 1，必填） | `bar` `line` `pie` `heatmap` `waterfall` |
| **组件** | 图上 / 页上还有哪些构造 | **0 到十几个**（65 选 N） | 「有参考线」「有负值」「图例在下方」「刻度比数据点稀」 |
| **词表** | 组件的那份**固定清单** | — | 就是这 65 个 key 本身 |

打个比方：**类型是名词**（这是一辆车），**组件是形容词**（四门、天窗、手动挡）。一辆车只能是一种车，但可以同时有很多个形容词。

**为什么词表要固定**：模型报组件时那个字段是 enum，只能从这 65 个里选，**且每选一个必须写出证据**（页面上的原话，或者画了什么、画在哪）。固定是为了让 192 页的答案能相加——「有参考线」「画了条虚线基准」「reference line」如果各写各的，就数不出「参考线出现在 41 页」这句话。选不出来的写进**新组件**自拟名字（§3），一个自拟名字出现 ≥3 页就**并入词表**，下一轮起有自己的计数。

**两者问同一个问题：我们画不画得出来。** 类型层面 `map` 画不出来（条件表没有地理投影这一族）；组件层面 `reference_line` 画不出来（参考线不是任何族的图元）。所以两者都在 §1，不因为分类不同就分两张表。

**图题不在词表里**——它是每张图上记录的五个字段（图号 / 主标题 / 副标题 / 单位 / 位置），见 §1.4。

### 2.2 类型配比

[P4](../review/04_pipeline_gap.md) 的权重向量要的就是这张表。画不出来的那几种在 §1.3 排过序了，这里只讲基准是什么样。

| 类型 | 图数 | 页数 | 我们能画吗 |
|---|---|---|---|
| `line` | 57 | 45 | 有 |
| `compound` | 52 | 46 | 有 |
| `stacked_bar` | 45 | 37 | 有 |
| `bar` | 37 | 33 | 有 |
| `grouped_bar` | 34 | 31 | 有 |
| `other` | 22 | 21 | **无** |
| `pie` | 5 | 3 | 有 |
| `map` | 3 | 3 | **无** |
| `donut` | 3 | 3 | 有 |
| `area` | 3 | 3 | 有 |
| `scatter` | 2 | 2 | 有 |
| `waterfall` | 1 | 1 | 有 |
| `histogram` | 1 | 1 | 有 |

共 265 张图，横向 51 张（19%，`chart_types.md` 没有方向这一维）；数值写出：无 144、全部 98、部分 23。另有 4 个条目被模型自己写进 `unreadable`（装饰色块、注释文字块、占位），不是图形，不计入。

### 2.3 难在哪

每页卡在[四步判定](../review/02_chart_metric.md)的哪一步。**这是模型的判断，属于待失败案例确认的假设，不是测量。**

| 卡在哪一步 | `3d_chart` | `3d_chart+need_estimate` | `need_estimate` | `untagged` | 合计 |
|---|---|---|---|---|---|
| 第一步 · 要有表 | 0 | 0 | 1 | 4 | 5 |
| 第二步 · 找到值 | 0 | 16 | 97 | 3 | 116 |
| 第三步 · 标签关联 | 2 | 0 | 13 | 45 | 60 |
| 第四步 · 表外上下文 | 0 | 0 | 0 | 11 | 11 |

**定位一个值要几个键**——左边是规则实际用了几个标签（事实），右边是模型只看图预测要几个（预测，判分见 §3）。两列差得越远，说明「凭图猜寻址」越不可靠：

| 键数 | 规则实际 | 模型预测 |
|---|---|---|
| 0 | 0 | 3 |
| 1 | 83 | 10 |
| 2 | 1374 | 546 |
| 3 | 201 | 882 |
| 4 | 0 | 197 |
| 5 | 0 | 6 |

**规则有 1374 条只用两个标签（83%）**——行头加列头，markdown 表刚好装得下。真正需要第三个键的只有 201 条，那才是第三步的难处。落位的 1644 个值里 473 个（29%）数字直接印在图上，其余要对着轴读。

**这一条不要反过来改我们的记录。** ParseBench 只需要两个键，不代表我们记两个键就够——生成侧的输出单位是 `(键, 值, 区域)`，**键必须是完整的寻址元组**（面板 × 系列 × 类目），因为 provenance 与 bbox 这类目标要求每个图元都能被唯一指到。把键结构裁到基准的最低要求，等于为了一个基准砍掉这份数据集自己的产物。这正是 [P2](../review/04_pipeline_gap.md) 要把面板维加进键的理由。

### 2.4 词表全表 · 65 项

五组，每组按页数排。「影响哪一步」与「我们」两列都在看任何一页之前就定死了。

| 组 | key | 组件 | 页数 | 文档 | 影响哪一步 | 我们 |
|---|---|---|---|---|---|---|
| 结构 | `stacked_bar` | 堆叠条 | 48 | 33 | 第2步 找到值 | 有 |
|  | `mixed_marks` | 同面板混合图元（bar + line） | 47 | 20 | 第2步 找到值 | 有 |
|  | `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | 43 | 22 | **不影响** | **无** |
|  | `negative_values` | 负值 / 零线居中的分叉条 | 42 | 21 | 第2步 找到值 | **无** |
|  | `horizontal_bars` | 横向条形（类目在 y 轴） | 42 | 19 | **不影响** | **无** |
|  | `no_value_axis` | 没有值轴刻度，只有基线 | 42 | 23 | 第2步 找到值 | **无** |
|  | `grouped_bar` | 分组条 | 37 | 28 | 第3步 标签关联 | 有 |
|  | `annotation_callout` | 绘图区内的说明框 / 引线注解 | 33 | 23 | **不影响** | **无** |
|  | `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | 33 | 17 | 第2步 找到值 | 有 |
|  | `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | 26 | 9 | 第3步 标签关联 | **无** |
|  | `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | 23 | 19 | 第2步 找到值 | **无** |
|  | `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | 19 | 7 | 第2步 找到值 · 第3步 标签关联 | **无** |
|  | `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | 18 | 9 | **不影响** | **无** |
|  | `pct_stacked` | 百分比堆叠（归一到 100%） | 16 | 12 | 第2步 找到值 | **无** |
|  | `dual_axis` | 双 y 轴，同面板两个量纲 | 13 | 12 | 第2步 找到值 | 有 |
|  | `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | 11 | 8 | 第1步 要有表 | **无** |
|  | `right_side_y_axis` | 唯一的值轴画在右侧 | 6 | 4 | **不影响** | **无** |
|  | `step_line_series` | 阶梯线（水平段 + 垂直跳变），不是直连折线 | 4 | 3 | 第2步 找到值 | **无** |
|  | `range_connector_line` | 每个类目两个点用线段连成区间（哑铃图 / 区间图） | 4 | 2 | 第2步 找到值 · 第3步 标签关联 | **无** |
|  | `log_axis` | 对数轴 | 3 | 3 | 第2步 找到值 | 有 |
|  | `stacked_area` | 堆叠面积 | 2 | 2 | 第2步 找到值 | 有 |
|  | `error_bars` | 误差棒 / 置信带 | 2 | 2 | **不影响** | **无** |
|  | `broken_axis` | 断轴：轴中间截断并画出断裂标记 | 2 | 2 | 第2步 找到值 | **无** |
|  | `stacked_and_grouped` | 堆叠与分组出现在同一张图 | 0 | 0 | 第3步 标签关联 | **无** |
| 版面 | `source_note_lines` | source / note 行在图下方 | 168 | 60 | **不影响** | 有 |
|  | `legend_below_plot` | 图例在绘图区下方 | 94 | 39 | **不影响** | 有 |
|  | `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | 53 | 22 | 第4步 表外上下文 | 有 |
|  | `multi_figure_page` | 一页多张独立图，各自有图号 | 46 | 24 | 第1步 要有表 · 第3步 标签关联 | 有 |
|  | `legend_above_plot` | 图例在绘图区上方（标题与图之间） | 46 | 17 | **不影响** | 有 |
|  | `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | 44 | 23 | 第1步 要有表 | **无** |
|  | `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | 27 | 13 | 第3步 标签关联 | 有 |
|  | `shared_legend` | 跨面板共享图例 | 24 | 13 | 第3步 标签关联 | 有 |
|  | `legend_inside_plot` | 图例画在绘图区内部 | 21 | 17 | **不影响** | **无** |
|  | `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | 21 | 6 | **不影响** | **无** |
|  | `per_panel_legend` | 每个面板各有一个图例 | 18 | 12 | 第3步 标签关联 | 有 |
|  | `heterogeneous_panel_types` | 同一图号下各面板类型不同 | 17 | 14 | 第1步 要有表 | 有 |
|  | `shared_axis` | 跨面板共享坐标轴 | 16 | 9 | 第2步 找到值 | 有 |
|  | `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | 14 | 12 | **不影响** | 有 |
|  | `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | 12 | 8 | 第3步 标签关联 | **无** |
|  | `data_table_as_figure` | 一块带表头的表格当作图收录 | 12 | 10 | 第1步 要有表 | 有 |
| 标题与单位 | `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | 149 | 59 | **不影响** | **无** |
|  | `footnote_marker` | 标题或标签里的脚注上标 | 52 | 32 | 第3步 标签关联 | **无** |
|  | `rotated_axis_title` | 轴标题竖排 | 42 | 17 | **不影响** | 有 |
|  | `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | 41 | 19 | **不影响** | **无** |
|  | `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | 19 | 10 | **不影响** | **无** |
|  | `axis_title_below_plot` | 值轴标题写在图下方 | 17 | 5 | **不影响** | **无** |
|  | `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | 11 | 11 | 第3步 标签关联 | **无** |
| 标签与刻度 | `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | 58 | 26 | 第3步 标签关联 | **无** |
|  | `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | 53 | 32 | 第2步 找到值 | **无** |
|  | `value_label_inside` | 数值标签写在图元内部 | 46 | 25 | 第2步 找到值 | 有 |
|  | `rotated_x_ticks` | x 刻度标签旋转 | 43 | 16 | **不影响** | 有 |
|  | `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | 36 | 23 | 第3步 标签关联 | 有 |
|  | `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | 34 | 26 | 第3步 标签关联 | **无** |
|  | `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | 27 | 14 | 第3步 标签关联 | 有 |
|  | `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | 19 | 14 | 第2步 找到值 | **无** |
|  | `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | 16 | 10 | 第3步 标签关联 | **无** |
|  | `inline_series_labels` | 没有图例，系列名直接标在线旁 | 11 | 10 | 第3步 标签关联 | **无** |
|  | `total_row_below_axis` | 轴下方一行合计值，与类目对齐 | 6 | 5 | 第3步 标签关联 | **无** |
| 风格 | `hgrid_only` | 只有水平网格线，没有垂直网格线 | 94 | 46 | **不影响** | 有 |
|  | `panel_background` | 绘图区带底色，不是白底 | 49 | 25 | **不影响** | **无** |
|  | `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | 45 | 20 | **不影响** | **无** |
|  | `dense_marks_100plus` | 单张图 ≥100 个图元 | 41 | 23 | 第2步 找到值 | **无** |
|  | `vgrid_only` | 只有垂直网格线，没有水平网格线 | 25 | 15 | **不影响** | 有 |
|  | `dashed_line_series` | 用线型（虚 / 实）区分系列 | 10 | 9 | **不影响** | **无** |
|  | `icon_category_axis` | 类目轴用图标代替文字 | 9 | 5 | 第3步 标签关联 | **无** |

## 3 · 这些数字能不能信

### 3.1 怎么跑的

整页 PNG 150 dpi，一页一次结构化调用，effort `high`，`max_tokens` 12000，不发 temperature / top_p。不裁剪、不接 OCR、不做 agent、不做第二轮。设计见 [review/05](../review/05_analysis_design.md)。

| 模型看得到 | 模型看不到 |
|---|---|
| 整页图像 | 抽查点的**标签** |
| 65 项组件词表（key + 英文判据） | 词表的「我们有没有」那一列 |
| 这一页抽查点的**数值** | 「影响哪一步」那一列 |
| P1–P7 的一行描述（意见要归类） | 流水线的结构、条件表、`(键, 值, 区域)` |

### 3.2 判分：一个真正被打了分的预测

值给了模型、标签没给，所以模型说的「要哪些键才能定位」是**预测**，规则来判分：一个值算对，要求规则用的每个标签都被预测到的某个键覆盖（双向子串，与基准自己的匹配方式一致）。**1635 个落位的值里对了 1155 个（71%）。**

这个数同时受两件事影响，报出来是为了可追查，不是当作模型能力的度量：一是模型确实读错了行或列（`2023-05-sigma-01-english_p23` 那张指数图 10 个值错了 7 个，两条线终点相差不足 2 px）；二是同一个格子在页面上常有不止一种叫法。**逐条可查**——每页 `report.md` 第 2 节把规则的标签与模型的预测并排放在同一行。

### 3.3 交叉核对

192 页共出 195 条矛盾。

| 矛盾 | 页数 |
|---|---|
| 模型预测的定位标签漏掉了规则实际用的标签 | 129 |
| 给了 N 个值，模型回了另一个数目 | 15 |
| 规则需要的键比模型报出的图能提供的多 | 12 |
| 系列数与系列名个数不一致 | 8 |
| 面板数与面板名个数不一致 | 8 |
| 有值没能落到任何一个图元上 | 7 |
| 标了 dense_marks_100plus，但没有图达到 100 个图元 | 6 |
| 有图超过 100 个图元，组件清单里没有 dense_marks_100plus | 2 |
| 组件要求的版面在图表分解里不成立，已剔除 | 2 |
| 有规则的标签对不上任何一张图的名字 | 2 |
| 首次调用返回空答案，加一句追问后重问了一次 | 1 |
| 没有估读点，模型却说数值一个都没写 | 1 |
| 模型在这一页上没有找到图 | 1 |
| 报了组件但没写出证据 | 1 |

**证据**：每个组件都要带证据，没写出证据的共 1 条。**`unreadable`** 非空 4 / 192 页——要逐条读，「这张图看不清」与「这个条目根本不是图」是两回事。

**意见归属**：schema 强制每条写全「加什么 / 改哪里 / 新增哪一行消融 / 通用度」，凑不出消融行的写不出来。模型自己判的通用度是**独立于文档分布的第二个估计**：

| 归入 | 条数 | 通用 | 一类出版方 | 这份文档自己的习惯 |
|---|---|---|---|---|
| P6 | 277 | 77 | 181 | 19 |
| P7 | 184 | 83 | 63 | 38 |
| P3 | 104 | 26 | 41 | 37 |
| P1 | 100 | 68 | 31 | 1 |
| P2 | 74 | 31 | 39 | 4 |
| new | 66 | 6 | 47 | 13 |
| P5 | 34 | 20 | 13 | 1 |
| P4 | 26 | 9 | 17 | 0 |

### 3.4 词表本身还缺什么

词表装不下的，模型自拟名字写进 `new_components`，同样要带证据——这一轮出现 514 个名字。**这是词表完整性的度量**：残差越干净，说明词表越接近覆盖。出现 ≥3 页的下一轮并入。

| 名字 | 页数 | 并表 | 说明 | 实例 |
|---|---|---|---|---|
| `currency_prefixed_axis_ticks` | 4 | ✓ | 读值时需剥离 $ 符号，且刻度间距 $1 对应 5% 容差意味着必须在半格内定位。 | [2024_Annual_Financial_Review_Upstream_FINAL_p10](pages/2024_Annual_Financial_Review_Upstream_FINAL_p10/report.md) |
| `per_panel_unit_differs` | 3 | ✓ | 两联图单位不同，取值必须绑定所属面板，不能跨面板共用同一单位标注。 | [89af4857-en_p19](pages/89af4857-en_p19/report.md) |
| `marker_shape_encodes_series` | 3 | ✓ | 在两线交叠的2015-2016段，颜色难分时只能靠标记形状（圆/菱形）判断某点属于哪个系列，从而决定该值归到哪一行。 | [World_Manufacturing_Production_2024_Q3_p11](pages/World_Manufacturing_Production_2024_Q3_p11/report.md) |
| `cumulative_running_total_series` | 3 | ✓ | 每个点是累计值而非年度值，读出的480、280等必须理解为自1990年起的累积额，否则与上表的年度损失混淆。 | [sigma-1-2021-en_p20](pages/sigma-1-2021-en_p20/report.md) |
| `sorted_category_axis` | 2 |  | 类别顺序本身携带信息（排名），行标签无法从字母序推断；读值时需按排名定位，且相邻行数值差可小于1个单位。 | [2025-EIS_p12](pages/2025-EIS_p12/report.md) |
| `sorted_descending_categories` | 2 |  | 行序由数值排名决定而非固定名单，读某一行的值时需先按排名定位，且相邻国家数值极接近（Denmark 与 Netherlands 仅差约1）易错行。 | [2025-EIS_p37](pages/2025-EIS_p37/report.md) |
| `primary_series_named_only_in_axis_title` | 2 |  | 读取条形长度时无法从图例得到年份，必须借下方轴标题"...in 2025..."才能把数值定位到2025年这一列，否则条形值与2018/2024标记无法区分。 | [2025-EIS_p57](pages/2025-EIS_p57/report.md) |
| `bold_column_emphasis` | 2 |  | 字重区分主列与分解列，是唯一提示'Change'列为汇总量的线索，纯文本导出后该层级消失。 | [67c07d7f417ce_p17](pages/67c07d7f417ce_p17/report.md) |
| `near_zero_bar_invisible` | 2 |  | 这些接近零的柱几乎无高度，无法按5%容差读数，只能报告为约零。 | [7c6b23db-en_p48](pages/7c6b23db-en_p48/report.md) |
| `key_message_line_below_figure` | 2 |  | 图的核心结论（七倍、2023-2025）写在图外正文行里，取值时的语境需从该行而非表格获得。 | [7c6b23db-en_p57](pages/7c6b23db-en_p57/report.md) |
| `percent_tick_labels_only_unit` | 2 |  | 单位仅由刻度上的百分号承载，表格若只抄数字会丢失百分比语义，取值需补回 %。 | [7c6b23db-en_p58](pages/7c6b23db-en_p58/report.md) |
| `duplicated_axis_title_both_sides` | 2 |  | 两侧单位文字相同，容易让人误以为两轴同刻度，需靠刻度数字自行区分。 | [89af4857-en_p22](pages/89af4857-en_p22/report.md) |
| `series_ends_before_axis_end` | 2 |  | Jun–Dec 各月对 Forecast 与 Scenarios 无数据点，表格中这些格位应为空而非0。 | [FPA-guide-to-data-visualization_p8](pages/FPA-guide-to-data-visualization_p8/report.md) |
| `pattern_fill_series` | 2 |  | 仅靠填充图案（斜纹/空白）区分系列，读值时须先按图案而非颜色定位段落，否则会把顶部空白段并入下方柱体。 | [Renewables2025_1_p32](pages/Renewables2025_1_p32/report.md) |
| `unnumbered_figure` | 2 |  | 缺少图号时，只能用加粗标题行作为该表的唯一上下文键，若解析输出丢掉标题，数值就无法归属到任何图。 | [Renewables2025_1_p43](pages/Renewables2025_1_p43/report.md) |
| `percent_sign_on_every_tick` | 2 |  | 单位只存在于刻度文字里，表格导出时若丢掉百分号，数值 9.1 与 9.1% 无法区分。 | [SPI_2025_Benchmark_Report_p120](pages/SPI_2025_Benchmark_Report_p120/report.md) |
| `two_level_column_headers` | 2 |  | 取一个单元格需同时用上层分组名与下层列名，否则「Share of total (%)」有两列重名而无法唯一定位。 | [World_Inequality_Report_2026_p198](pages/World_Inequality_Report_2026_p198/report.md) |
| `per_panel_category_order` | 2 |  | 同一区域在两个面板处于不同横轴位置，读值时不能按位置对应，必须同时用面板名与区域码定位，否则会把 Income 的第2槽误读为 Wealth 的第2槽。 | [World_Inequality_Report_2026_p20](pages/World_Inequality_Report_2026_p20/report.md) |
| `dual_glyph_legend_entry` | 2 |  | 一个图例名对应两种填色，取值时必须另判显著性深浅，否则无法唯一定位某个标记。 | [b263dc5d-en_p106](pages/b263dc5d-en_p106/report.md) |
| `axis_group_band_with_row_label` | 2 |  | 每个国家还带一个'调查轮次'属性，表格行需要额外一列才能唯一定位该点。 | [b263dc5d-en_p118](pages/b263dc5d-en_p118/report.md) |
| `legend_swatch_pair_per_series` | 2 |  | 一个系列名对应两种填色，读值时必须知道深浅只表示显著性而非另一个系列，否则会把25个国家误判成4个系列。 | [b263dc5d-en_p120](pages/b263dc5d-en_p120/report.md) |
| `sort_order_stated_in_note` | 2 |  | 类别顺序由未调整值决定，可用相邻条形的单调性校验读数，也说明表格行序不是字母序。 | [b263dc5d-en_p120](pages/b263dc5d-en_p120/report.md) |
| `per_category_sample_size_note` | 2 |  | 注释行按类别给出样本量，与坐标轴类别一一对应，可作为附加列；若被当成普通文字，则类别名的另一处出处丢失。 | [deloitte-2025-global-automotive-consumer-study-january-2025_1_p15](pages/deloitte-2025-global-automotive-consumer-study-january-2025_1_p15/report.md) |

<details><summary>只出现在 1 页的 491 个</summary>

`abbrev_series_names` · `aggregate_and_detail_in_one_axis` · `aggregate_category_among_peers` · `aggregate_category_in_capitals` · `aggregate_group_in_subtitle` · `aggregate_inserted_in_ranking` · `aggregate_panel_beside_members_panel` · `aggregate_row_not_highlighted` · `aggregate_series_doubles_as_zero_line` · `annotated_row_with_row_label_box` · `anonymous_stack_segments` · `appended_subtable_different_columns` · `area_fill_under_line` · `arrow_range_timeline_panel` · `asterisked_duplicate_column_header` · `axis_assignment_in_legend` · `axis_assignment_in_series_name` · `axis_break_glyph_on_category_axis` · `axis_ends_at_series_ceiling` · `axis_group_band_with_row_title` · `axis_label_color_coding` · `axis_row_drawn_as_table_cells` · `axis_side_tag_in_series_name` · `axis_tick_percent_sign_on_every_tick` · `axis_ticks_finer_than_label_step` · `axis_title_duplicates_subtitle_unit` · `axis_title_governing_both_panels` · `axis_title_in_legend_row` · `banner_title_block` · `banner_title_reverse_text` · `bar_and_line_share_time_axis_different_scales` · `bar_to_marker_drop_line` · `bar_top_connector_area` · `bar_track_background` · `bar_track_to_full_scale` · `bars_end_before_axis_end` · `basis_in_page_header` · `bidirectional_arrow_axes` · `bin_edge_tick_labels` · `blank_category_slot` · `blank_category_slot_before_residual_row` · `blank_category_slot_separator` · `blank_cell_row_grouping` · `bold_emphasis_inside_caption` · `bold_value_columns` · `boxed_category_axis_cells` · `boxed_feature_local_figure_numbering` · `boxed_outside_label_with_leader` · `boxed_value_label_outside_segment` · `brand_icon_series_key` · `bubble_size_encodes_magnitude` · `bullet_style_bar_with_two_overlaid_reference_marks` · `bullet_text_duplicates_chart_value` · `cagr_growth_arrow` · `callout_annotates_reference_line` · `callout_boxes_outside_plot_top` · `callout_color_matches_series` · `callout_explains_shading` · `callout_year_prefixed_event_label` · `caption_below_plot_as_only_title` · `caption_carries_number_title_and_credit` · `caption_number_inline_with_title` · `caption_takeaway_below_figure` · `categories_sorted_by_first_segment` · `categories_sorted_by_series_value` · `category_axis_repeated_top_and_bottom` · `category_axis_title_at_axis_end` · `category_axis_title_below_plot` · `category_axis_title_below_ticks` · `category_group_band_below_axis` · `category_group_whitespace_separator` · `category_highlight_band` · `category_identified_by_legend_colour_only` · `category_is_series` · `category_labels_at_both_panel_edges` · `category_labels_below_lowest_tick` · `category_labels_in_filled_boxes` · `category_separator_gridlines` · `category_sorted_by_value` · `category_specific_bar_colors_no_legend` · `chart_title_below_plot` · `coincident_markers_one_visible` · `color_per_category_single_series` · `color_text_legend_no_swatch` · `colored_header_banner_cells` · `colored_keyword_in_panel_title` · `companion_panel_different_unit` · `constant_series_across_all_categories` · `continuation_panel_grid_without_heading` · `copyright_line_below_source` · `count_and_share_in_one_label` · `country_bars_sorted_ascending` · `cross_figure_axis_span_note` · `crossing_line_bundle` · `crowded_endpoint_label_stack` · `cumulative_top_only_readable` · `currency_symbol_in_tick_labels` · `curved_leader_arrow_labels` · `dash_as_zero_tick` · `dash_style_legend_note` · `dashed_outline_highlights_panel` · `decomposition_total_and_parts_rows` · `dense_monthly_category_axis` · `derived_change_callout_per_group` · `dimension_label_above_plot` · `distribution_percentile_series` · `diverging_stacked_bar` · `donut_average_badge` · `donut_progress_indicator` · `dotted_leader_category_labels` · `dual_swatch_legend_entry` · `duplicate_category_labels` · `duplicate_label_text_across_categories` · `duplicate_value_across_panels` · `duplicated_category_axis_labels` · `duplicated_unit_text` · `emphasised_value_labels_in_colour` · `empty_bin_slots` · `empty_series_slot_in_stack` · `empty_trailing_category_slot` · `encoding_explained_in_note` · `endpoint_and_startpoint_value_labels` · `endpoint_label_pair_collision` · `endpoint_latest_value_label` · `endpoint_only_value_axis` · `event_band_legend_with_date_and_loss` · `event_marker_point_with_arrow` · `exceedance_curve_as_bars` · `exhibit_number_separate_from_title` · `exploded_pie_slice` · `exploded_slice_to_stacked_bar` · `external_benchmark_marker_label` · `figure_caption_rule_bar` · `figure_caption_without_number` · `figure_container_tint_box` · `figure_frame_border` · `figure_frame_box` · `figure_frame_rules` · `figure_title_below_plot` · `flag_icon_beside_panel_title` · `flag_marker_constant_height` · `floating_bars_off_baseline` · `forecast_badge` · `forecast_panel_suffix` · `forecast_point_marker` · `forecast_suffix_category_labels` · `forecast_suffix_on_time_ticks` · `full_number_thousands_separator_ticks` · `full_scale_track_behind_bar` · `gap_annotation_between_bars` · `gapped_year_categories` · `green_subtitle_as_chart_title` · `grid_without_ticks` · `group_band_labels_inside_plot` · `group_band_under_axis` · `group_separator_gap_in_category_axis` · `group_separator_rules` · `group_tick_row_above_plot` · `grouped_stack_by_two_level_axis` · `grouped_thousands_tick_labels` · `grouping_banner_row_label` · `growth_rate_as_secondary_quantity` · `handdrawn_highlight_oval` · `hatched_fill_for_aggregate` · `hatched_segment_fill` · `heading_in_filled_banner` · `heading_in_side_column` · `heading_rule_above_plot` · `heading_unit_in_parentheses_lighter_type` · `headline_states_data_value` · `icon_identifies_data_scope` · `icon_panel_headers` · `icon_pull_quote_sidebar` · `icon_stat_callout_grid` · `identity_label_over_bar` · `implicit_baseline_under_value_band` · `implicit_row_group_blank_cell` · `inconsistent_category_capitalization` · `increment_segment_on_top` · `index_axis_without_unit` · `index_base_period_unstated` · `index_base_year_convergence` · `indexed_base_implicit` · `indian_digit_grouping` · `inequality_prefixed_values` · `inequality_qualified_values` · `interpretation_note_block` · `interpretation_note_paragraph` · `interpretation_note_with_inline_numbers` · `interpretation_paragraph_below_figure` · `irregular_time_axis_spacing` · `italic_ranking_note_line` · `kpi_big_number_panel` · `label_and_value_in_one_string` · `label_collision_offset_in_grouped_pair` · `label_collision_overlap` · `label_color_encodes_subnational_entity` · `label_offset_alternating` · `label_only_on_latest_series` · `label_only_series_position` · `label_unit_differs_from_axis` · `labelled_subset_of_marks` · `labels_on_lines_only_not_bars` · `leader_line_boxed_labels` · `left_metadata_column` · `legend_band_spanning_page_width` · `legend_dual_swatch_per_series` · `legend_entries_split_over_two_panels` · `legend_entry_lists_multiple_swatches` · `legend_glyph_matches_mark_type` · `legend_grid_two_columns` · `legend_label_above_marker` · `legend_labels_mismatch_data` · `legend_mixed_glyph_types` · `legend_mixed_swatch_and_glyph` · `legend_multicolumn_grid` · `legend_omits_extra_color` · `legend_period_overridden_by_note` · `legend_series_reused_as_table_rows` · `legend_swatch_only_series_names` · `legend_swatch_shape_by_mark_type` · `legend_two_row_grid` · `licence_credit_line` · `licence_line_below_figure` · `license_credit_line` · `license_credit_line_below_figure` · `license_credit_line_below_plot` · `license_line_below_figure` · `line_label_collision_with_bars` · `line_over_bar_label_conflict` · `line_series_break_between_groups` · `line_series_out_of_axis_range` · `locator_labels_not_data` · `locator_map_inset_beside_chart` · `logo_marker_on_reference_line` · `long_single_column_bar_list` · `marker_and_line_series` · `marker_dense_line_series` · `marker_may_exceed_bar_end` · `marker_on_line_series` · `marker_overlaps_bar_end` · `marker_series_on_other_axis` · `marker_series_shares_row_with_bar` · `marker_series_unit_differs_from_bars` · `marker_shape_per_series` · `markers_on_subset_of_points` · `matrix_row_label_column` · `metric_in_title_not_unit` · `metric_row_below_axis_with_row_label` · `mixed_period_and_average_categories` · `mixed_period_granularity_axis` · `mixed_weight_heading_line` · `multi_category_single_axis_panel` · `multi_row_legend_mixed_glyphs` · `multi_swatch_single_legend_entry` · `narrative_slide_title_above_figure_heading` · `near_duplicate_series_labels_across_figures` · `near_zero_bar` · `near_zero_bar_below_resolution` · `near_zero_mark` · `negative_value_in_text_column` · `nested_range_bands` · `no_unit_text_anywhere` · `note_and_source_in_one_line` · `note_and_source_same_line` · `note_excludes_one_time_point` · `note_line_beside_legend` · `note_line_defines_series_meaning` · `note_marker_on_value_label` · `numbers_only_in_note_text` · `numeric_categorical_x_axis` · `numeric_change_column_between_panels` · `offscreen_category_values_box` · `omitted_zero_segment` · `orphan_source_block_from_previous_figure` · `outward_tick_dashes_no_gridlines` · `overlapping_identical_series` · `overlapping_marker_series` · `overlapping_stack_segments` · `overlapping_value_labels` · `paired_values_in_one_cell` · `paired_year_rows_in_table` · `panel_as_column_matrix` · `panel_color_coded_bars` · `panel_color_encodes_panel` · `panel_covers_subset_of_categories` · `panel_designation_in_title` · `panel_fill_color_marks_aggregate` · `panel_group_header` · `panel_label_banner_inside_plot` · `panel_label_banner_right_side` · `panel_local_bar_scale` · `panel_named_in_title_only` · `panel_pair_shared_note` · `panel_row_of_bar_columns` · `panel_size_encodes_total` · `panel_specific_category_sets` · `panel_specific_series_colour` · `panel_title_in_frame_gap` · `panel_title_two_line_qualifier` · `panel_without_axis_unit` · `panel_zoom_connector` · `panels_with_different_x_dimensions` · `parenthesized_negative_ticks` · `partial_series_dashing` · `partial_series_label_coverage` · `partial_width_reference_line` · `pct_stack_not_summing_to_100` · `per_panel_baseline_rule` · `per_panel_category_axis` · `per_panel_category_reordering` · `per_panel_series_color` · `per_panel_source_line` · `per_panel_unit` · `per_panel_unit_change` · `per_series_source_line` · `percent_and_level_series_split_by_axis` · `percent_sign_in_value_labels` · `percent_sign_on_tick_only` · `percent_sign_on_ticks_and_labels` · `percent_sign_only_on_one_axis` · `percent_sign_only_on_ticks` · `percent_ticks_bare_value_labels` · `percent_ticks_on_all_labels` · `percent_ticks_with_symbol` · `percent_unit_only_in_value_labels` · `period_range_in_category_label` · `pictogram_growth_metaphor_over_bars` · `plot_area_frame_box` · `plot_frame_box` · `point_labels_with_leader_lines` · `point_series_label_color_coded` · `pointer_arrow_label_box` · `primary_series_unnamed_in_legend` · `prior_year_marker_offset` · `projection_suffix_in_ticks` · `qr_code_in_page_header` · `quarter_slots_without_labels` · `question_code_as_source_line` · `question_id_in_note` · `question_id_note_line` · `question_text_as_figure_heading` · `radial_fan_bar_chart` · `rank_index_column` · `ranking_rule_in_note` · `reading_guide_note` · `reading_line_states_values` · `repeated_category_across_panels` · `repeated_category_order_differs_per_panel` · `repeated_per_panel_axes` · `repeated_question_stem_heading` · `reversed_legend_order` · `reversed_series_order_vs_legend` · `rights_credit_line_below_figure` · `rounded_capsule_bars` · `rounded_frame_around_panels` · `row_label_in_tinted_box` · `row_track_full_scale` · `same_categories_across_untitled_figures` · `same_categories_different_measures_across_panels` · `same_value_repeated_across_series` · `screenshot_cursor_artifact` · `secondary_axis_on_top` · `secondary_scale_for_one_category` · `segment_boundary_only_readable` · `segment_label_right_aligned_in_segment` · `segment_reaching_axis_bound` · `segment_value_only_in_body_text` · `semantic_axis_endpoint_labels` · `series_as_text_row_only` · `series_color_per_stat` · `series_converge_at_index_base` · `series_label_gutter_outside_plot` · `series_label_leader_to_marker` · `series_legend_as_stacked_rows` · `series_name_differs_per_panel` · `series_name_inside_value_label` · `series_name_reused_across_panels` · `series_names_only_in_subtitle` · `series_shorter_than_axis` · `series_start_offset` · `series_starts_late_gap` · `series_starts_later_than_axis` · `shared_note_block_for_two_figures` · `shared_source_line_two_figures` · `sibling_figures_share_title_stem` · `signed_step_drawn_above_zero` · `significance_shading_paired_legend` · `single_series_marker_highlight` · `slice_color_order_only_key` · `slide_sentence_headline` · `slide_title_duplicates_figure_title` · `sorted_by_one_series` · `sorted_rank_order_rows` · `source_beside_plot` · `source_in_caption_parenthetical` · `source_inside_interpretation_paragraph` · `source_line_without_source_word` · `space_grouped_thousands_ticks` · `space_thousands_separator_ticks` · `split_scale_outlier_category` · `stack_segment_gap_between_bars` · `stack_spans_zero_with_total_marker` · `stack_total_not_exactly_100` · `stacked_segment_requires_difference` · `stacks_below_axis_maximum` · `stepped_and_sawtooth_series_pair` · `structurally_absent_segment` · `subnational_label_colour` · `subscript_in_axis_unit` · `subscript_unit_glyph` · `survey_question_subtitle` · `table_column_header_band` · `table_overlaid_on_plot` · `table_row_fill_encodes_status` · `takeaway_caption_below_figure` · `takeaway_sentence_above_figures` · `takeaway_statement_above_title` · `three_point_distribution_with_aggregate_dash` · `three_point_range_line` · `threshold_colored_fill` · `tick_labels_without_axis_line_marks` · `tick_row_without_gridline_per_year` · `time_axis_gap_ellipsis` · `tinted_column_panel` · `title_in_filled_banner` · `title_inset_in_frame_border` · `title_range_mismatch_axis_span` · `title_typo_verbatim` · `total_in_heading` · `total_row_duplicates_title_text` · `transform_noted_in_series_name` · `trend_series_without_own_axis_or_points` · `truncated_series_ends_midway` · `twin_log_axes_identical_ticks` · `two_panel_one_caption` · `two_source_lines` · `two_swatch_legend_for_one_series` · `unequal_bin_category_axis` · `unequal_time_axis_spacing` · `unit_absent_on_count_axis` · `unit_heading_shared_across_sibling_figures` · `unit_in_tick_labels` · `unit_inline_beside_title` · `unit_only_in_first_figure_title` · `unit_repeated_in_subtitle_and_axis` · `unit_split_between_axes` · `unit_suffix_in_value_labels` · `unit_symbol_in_value_label` · `unit_symbol_on_top_tick_only` · `unlabeled_axis_origin` · `unlabeled_minor_segments` · `unlabeled_second_panel_axis_side` · `unlabeled_total_row_header_box` · `unlabeled_zero_baseline` · `unlabelled_primary_series` · `unlabelled_reference_line` · `unnamed_panels_distinguished_by_categories` · `unnamed_primary_series` · `unnumbered_figure_bold_lead_in_title` · `unnumbered_figure_heading` · `unnumbered_figures` · `unnumbered_kpi_table` · `unsorted_axis_by_value_descending` · `unstacked_overlapping_area_and_line` · `value_axis_above_plot` · `value_axis_absent_full_scale_stack` · `value_columns_aligned_to_stack_segments` · `value_only_in_callout_text` · `value_sorted_categories` · `value_sorted_category_axis` · `value_year_inside_cell` · `values_only_in_annotation_text` · `values_only_in_interpretation_text` · `variant_suffix_category_slot` · `vertical_group_separator_band` · `vertical_jump_connector` · `vertical_panel_divider` · `waterfall_connector_line` · `year_axis_ticks_offset_from_bars` · `year_subcolumns_per_indicator` · `zebra_row_shading` · `zebra_striped_table_rows` · `zero_baseline_at_axis_top` · `zero_length_category_no_mark` · `zero_printed_without_mark` · `zero_tick_as_dash` · `zero_tick_label_omitted` · `zero_value_label_no_bar` · `zero_value_printed_without_bar` · `zero_valued_bar_absent`

</details>

类型这一侧同样：22 张图报了 `other` 并自己命名，分类见 §1.3。

### 3.5 一页报告怎么读

`pages/<stem>/` 三个文件：`report.md` 给人读，`analysis.json` 给汇总用，`page.png` 是指向 `data/pages/` 的链接。`report.md` 六节：

| 节 | 内容 |
|---|---|
| 1 样本 | 来源文档、标签组、抽查点数与其中估读数 |
| 2 抽查点与模型的定位 | 左半是规则（值 + 标签 + 容差），右半是模型只看图给的定位。**模型只拿到了左半的值** |
| 3 图表分解 | 每张图：类型、方向、面板 / 系列 / 类目数、图元总数、值轴刻度原文，以及拆成五项的标题 |
| 4 组件清单 | 本页出现的项，每项带模型写的证据；「我们」一列从词表照抄 |
| 5 难在哪 | 卡在四步的哪一步，用本页的数字论证 |
| 6 意见 | 加什么 / 改哪里 / 新增哪一行消融 / 通用度，归入 P1–P7 |

schema 在 [`tools/analysis/schema.py`](../tools/analysis/schema.py)，词表的唯一定义处在 [`tools/analysis/vocabulary.py`](../tools/analysis/vocabulary.py)。

