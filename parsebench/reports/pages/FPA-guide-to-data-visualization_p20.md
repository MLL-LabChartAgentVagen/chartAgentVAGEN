# FPA-guide-to-data-visualization_p20

![FPA-guide-to-data-visualization_p20](../../data/pages/FPA-guide-to-data-visualization_p20.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `FPA-guide-to-data-visualization_p20` | FPA-guide-to-data-visualization | untagged | 10 | `parsebench/data/pages/FPA-guide-to-data-visualization_p20.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 本页要能画三件事：两张结构完全相同的饼图（8个扇区、全部带引线的"类别+百分比"外标签，标题行把名称与总额并排写成 `FY 14 Q2 Forecast  Total: $750,000`），以及一张"改造后"的水平条形图——刻度轴 `0% 10% … 70%` 画在图顶部、类别名在左侧且换行（`Depreciation, Interest and Maintenance`），深蓝条为 `FY14 Jan Actual`，橙色短竖线（不是条）为 `FY14 Q2 Forecast`，图例挤在绘图区右下角。左侧还有一整栏浅青底的正文，与三图共用同一横向版面。
> 
> ## 定位一个值难在哪
> `9`：它在 f1 是 `Contracts and Professional Fees 9%`，在 f2 却是 `Depreciation, Interest and Maintenance 9%`。两饼类别名逐字相同，只有标题 `FY 14 Q2 Forecast` / `FY 14 Jan Actual` 能区分，一行表若丢掉图标题，就无法只指向其中一个。f3 里同一个 9% 又以无数字的条长出现。
> 
> ## 不确定的
> f3 橙色刻度线的精确位置：无数值标签、刻度间距10%约45像素，7%与8%读不到5%容差；图例究竟算在绘图区内还是下方也只能按位置判断。饼图 `Total: $387,000k` 中的 `k` 是否笔误，无从核实。

**gpt-5.6-sol**

> ### 画出来要什么
> 页面并排放置说明文字与三幅图：两幅八切片饼图使用外置百分比标签和引线；第三幅图以横条表示实际值、橙色短刻线表示预测值，并把百分比轴置于上方、图例放在图内。
> 
> ### 定位一个值难在哪
> “61%”与“60.3%”都属于“Salaries and Benefits”，必须结合“FY 14 Q2 Forecast”和“FY 14 Jan Actual”两条粗体标题才能区分。横条图的小值还难以按10个百分点刻度读到5%误差内。
> 
> ### 不确定的
> 饼图标题中“Forecast/Actual”与“Total”之间的精确空格数难以确认；横条图橙色刻线的细小数值无法仅凭坐标轴精确读取。

**gemini-3.1-pro**

> ### 画出来要什么
> 
> 页面右侧包含三个图表：两个带有引线和外部标签的饼图（明确标注了百分比），以及一个水平分组柱状图。页面左侧是一长列带浅蓝色背景的正文，属于典型的图文多列并排布局。图表生成器需要支持使用引线（leader lines）将标签及对应数值干净地放置在饼图切片外部，并支持绘制带有顶部数值轴及垂直网格线的分组柱状图。
> 
> ### 定位一个值难在哪
> 
> 提取如“61”这类明确印在图上的数值并不困难，但在处理小切片时挑战较大。关键在于准确追踪饼图极细的引线。对于较小且密集的切片（如“Computer Services 2%”），引线的起点和终点极其靠近。视觉模型在关联文本标签与具体切片时，很容易发生错位，导致步骤3受阻。
> 
> ### 不确定的
> 
> 底部的新分组柱状图没有任何直接印出的数据标签，所有数值必须依靠顶部的刻度线（0%至70%）来估读。虽然本页被抽查的数值都来自清晰标注的饼图，但如果要求读取柱状图的具体数值（例如实际与预测的对比差值），凭借视觉估算的精度很可能达不到5%的误差要求。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | pie | 8 | — | above | all |
| opus-5 | f2 | pie | 8 | — | above | all |
| opus-5 | f3 | bar | 16 | — | above | none |
| gpt-5.6-sol | f1 | pie | 8 | — | above | all |
| gpt-5.6-sol | f2 | pie | 8 | — | above | all |
| gpt-5.6-sol | f3 | compound | 16 | — | above | none |
| gemini-3.1-pro | f1 | pie | 8 | — | above | all |
| gemini-3.1-pro | f2 | pie | 8 | — | above | all |
| gemini-3.1-pro | f3 | grouped_bar | 16 | — | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `footnote_marker` | ✓ | ✓ | ✓ | opus-5: Slice label reads 'Office Expenses and Other Costs*' with an asterisk；gpt-5.6-sol: The category axis reads “Office Expenses and Other Costs*”.；gemini-3.1-pro: asterisk on the Office Expenses and Other Costs label |
| `grouped_bar` | — | — | ✓ | gemini-3.1-pro: bars for actual and forecast are grouped side by side |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: Category names on the left, navy bars grow rightwards to the 0%-70% scale；gpt-5.6-sol: Category labels are at left and navy bars grow horizontally to the right.；gemini-3.1-pro: categories sit on the y axis and bars grow to the right |
| `legend_below_plot` | — | — | ✓ | gemini-3.1-pro: the legend with two coloured squares sits below the bar chart |
| `legend_inside_plot` | ✓ | ✓ | — | opus-5: 'FY14 Jan Actual  FY14 Q2 Forecast' sits in the plot area right of the Editing/Publishing row；gpt-5.6-sol: The two-item legend occupies unused space beside the bottom category row. |
| `mixed_marks` | ✓ | ✓ | — | opus-5: Navy bars and orange tick glyphs share one panel and one scale；gpt-5.6-sol: Navy horizontal bars and orange vertical tick markers occupy the same panel. |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: Three separately titled charts: two pies plus 'Data graphed after applying data visualization rules:'；gpt-5.6-sol: Three separately titled plots show forecast pie, actual pie, and combined horizontal comparison.；gemini-3.1-pro: three distinct figures on the right half of the page |
| `no_value_axis` | ✓ | — | — | opus-5: Pie has no scale at all; the 61%, 9%, 7% are readable only as printed labels |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: Tinted left column 'Pie charts' with bulleted prose runs level with all three figures；gpt-5.6-sol: A blue prose column headed “Pie charts” and bullet lists runs beside all plots.；gemini-3.1-pro: a narrow column of body text runs alongside the figures |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: Same note line repeated in small print directly below the bar chart；gpt-5.6-sol: Below the plot: “*Other costs category includes marketing and promotions costs.”；gemini-3.1-pro: note line explaining the asterisk category sits below the plot |
| `tick_marker_as_series` | ✓ | ✓ | — | opus-5: Orange short vertical dashes at each row, legended 'FY14 Q2 Forecast', on the bars' axis；gpt-5.6-sol: “FY14 Q2 Forecast” is encoded by short orange ticks at category positions. |
| `unit_in_axis_or_title` | ✓ | — | — | opus-5: Title line carries 'Total: $750,000', the only thing fixing what the percentages are of |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: 'Contracts and Professional Fees 10.1%' printed outside the pie on a leader line；gpt-5.6-sol: Percentages such as “60.3%” sit outside slices and connect by leaders.；gemini-3.1-pro: percentages are printed completely outside the pie slices |
| `vgrid_only` | — | — | ✓ | gemini-3.1-pro: vertical grid lines drawn downwards from the 10% interval ticks |
| `wrapped_category_labels` | ✓ | ✓ | — | opus-5: 'Depreciation, Interest / and Maintenance' and 'Travel and Business / Entertainment' wrap to two lines；gpt-5.6-sol: Long category-axis labels wrap across two or three lines. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `value_axis_on_top` | opus-5 | 2,3 | '0% 10% 20% 30% 40% 50% 60% 70%' printed above the first bar row, not below the plot |
| `before_after_redesign_pair` | opus-5 | 1,3 | Same eight expense shares drawn as two pies, then re-drawn as one bar chart with the same categories |
| `pie_leader_line_labels` | opus-5 | 3 | Category name and percentage stacked at the end of a leader line pointing to each slice |
| `total_in_title_line` | opus-5 | 4 | 'FY 14 Jan Actual  Total: $387,000k' puts the whole-of-pie total inside the title line |
| `pie_label_leader_lines` | gpt-5.6-sol | 3 | Thin black leaders connect every external category-and-percentage label to its pie slice. |
| `pie_label_leader_lines` | gpt-5.6-sol | 3 | Thin black leaders connect external labels to the corresponding actual-value slices. |
| `top_value_axis` | gpt-5.6-sol | 2 | Ticks “0%” through “70%” are drawn above the horizontal bars. |
| `leader_lines` | gemini-3.1-pro | 3 | thin lines connecting outside text labels to their respective pie slices |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 61 | Salaries and Benefits、FY14 Q2 Forecast | FY 14 Q2 Forecast  Total: $750,000、Salaries and Benefits | FY 14 Q2 Forecast、Salaries and Benefits | Salaries and Benefits | ✓ | ✓ | ✗ | 过 |
| 60.3 | Salaries and Benefits、FY14 Jan Actual | FY 14 Jan Actual  Total: $387,000k、Salaries and Benefits | FY 14 Jan Actual、Salaries and Benefits | Salaries and Benefits | ✓ | ✓ | ✗ | 过 |
| 9 | Contracts and Professional Fees、FY14 Q2 Forecast | FY 14 Q2 Forecast  Total: $750,000、Contracts and Professional Fees | FY 14 Q2 Forecast、Contracts and Professional Fees | Contracts and Professional Fees | ✓ | ✓ | ✗ | 过 |
| 10.1 | Contracts and Professional Fees、FY14 Jan Actual | FY 14 Jan Actual  Total: $387,000k、Contracts and Professional Fees | FY 14 Jan Actual、Contracts and Professional Fees | Contracts and Professional Fees | ✓ | ✓ | ✗ | 过 |
| 10 | Depreciation, Interest and Maintenance、FY14 Q2 Forecast | FY 14 Q2 Forecast  Total: $750,000、Depreciation, Interest and Maintenance | FY 14 Q2 Forecast、Depreciation, Interest and Maintenance | Depreciation, Interest and Maintenance | ✓ | ✓ | ✗ | 过 |
| 9 | Depreciation, Interest and Maintenance、FY14 Jan Actual | FY 14 Jan Actual  Total: $387,000k、Depreciation, Interest and Maintenance | FY 14 Jan Actual、Depreciation, Interest and Maintenance | Depreciation, Interest and Maintenance | ✓ | ✓ | ✗ | 过 |
| 7 | Office Expenses and Other Costs*、FY14 Q2 Forecast | FY 14 Q2 Forecast  Total: $750,000、Office Expenses and Other Costs* | FY 14 Q2 Forecast、Office Expenses and Other Costs* | Office Expenses and Other Costs* | ✓ | ✓ | ✗ | 过 |
| 8 | Office Expenses and Other Costs*、FY14 Jan Actual | FY 14 Jan Actual  Total: $387,000k、Office Expenses and Other Costs* | FY 14 Jan Actual、Office Expenses and Other Costs* | Office Expenses and Other Costs* | ✓ | ✓ | ✗ | 过 |
| 7 | Conference, Meetings and Exhibits、FY14 Q2 Forecast | FY 14 Q2 Forecast  Total: $750,000、Conference, Meetings and Exhibits | FY 14 Q2 Forecast、Conference, Meetings and Exhibits | Conference, Meetings and Exhibits | ✓ | ✓ | ✗ | 过 |
| 5 | Conference, Meetings and Exhibits、FY14 Jan Actual | FY 14 Jan Actual  Total: $387,000k、Conference, Meetings and Exhibits | FY 14 Jan Actual、Conference, Meetings and Exhibits | Conference, Meetings and Exhibits | ✓ | ✓ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f3` | "bar" | "compound" | "grouped_bar" | compound | 按类型表自己的定义判：`compound` 是<strong>同一个面板里出现两种以上图元形状</strong>，所以决定它的是三家自己在 `components` 里记的 `mixed_marks`，不是它们给这张图起的名字。opus 与 gpt 都记了 `mixed_marks` 与 `tick_marker_as_series`（条上叠了一条 3 像素宽的橙色短横）；gemini 只记了 `grouped_bar`，把那层标记当成了第二组条。三家图元数都是 16。 |
| `hardest_step` | 3 | 4 | 3 | 未裁决 · 无实测证据 | 这一页 10 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 4 / 3 都无法证伪。 |
| `key_roles#f1` | ["category", "panel"] | ["category", "panel"] | ["category"] | category × panel（图自己的小标题） | opus 与 gpt 都记了一段来自 `heading` 的 panel（`FY 14 Q2 Forecast`）。这一页并排两张图<strong>用的是同一批类目名</strong>（Salaries and Benefits…），只有小标题能把两张分开——所以这一段确实是定位所必需的。<strong>这正是 P3 与 P7 说的事</strong>：小标题必须跟着导出去，否则两张图的行会撞在一起。 |
| `key_roles#f2` | ["category", "panel"] | ["category", "panel"] | ["category"] | category × panel（图自己的小标题） | 同 f1，是并排的另一张。 |
