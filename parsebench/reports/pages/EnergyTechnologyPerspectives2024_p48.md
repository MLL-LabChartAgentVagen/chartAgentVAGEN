# EnergyTechnologyPerspectives2024_p48

![EnergyTechnologyPerspectives2024_p48](../../data/pages/EnergyTechnologyPerspectives2024_p48.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `EnergyTechnologyPerspectives2024_p48` | EnergyTechnologyPerspectives2024 | need_estimate | 10 | `parsebench/data/pages/EnergyTechnologyPerspectives2024_p48.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一张 18 行的横向百分比堆叠条形图：7 个填充系列（China、European Union、India、Japan、Korea、United States、RoW）每行都填满到 100%，再叠加第 8 个系列「China in 2021」的空心圆点标记，落在同一条 0%–100% 轴上。值轴画在**图顶**（0%、20% … 100%），只有竖向网格线。左侧类别轴是两级：竖排旋转的组名（Batteries、EV、Solar PV、Wind、Other、Materials）加上条目名，且「Cells」在 Batteries 与 Solar PV 下各出现一次。标题拆成「Figure 1.11」＋标题行；图下依次是图例、「IEA. CC BY 4.0.」、Note/Source 两行小字，最后是一句蓝色加粗结论句。
> 
> ## 定位一个值难在哪
> 以 53 为例：它只能是 Materials 组 Iron 行上那个「China in 2021」圆点，图上不印数字，最近的刻度间距是 20%（约 142 px）。要落在 ±5%（50.4–55.7）内，得把圆心在两条网格线之间目测到 1% 精度；而且行地址必须写成「Materials」+「Iron」+「China in 2021」三段，少了组名，「Cells」这类重名行就无法唯一定位。
> 
> ## 不确定的
> 所有数值都是按像素反推的，92/91/16/10/8 具体落在哪一段只能推测；极窄的 Japan、Korea 段是否为零无法分辨；组名括号栏是否属于轴刻度也说不准。

**gpt-5.6-sol**

> ### 画出来要什么
> 需绘制18行横向百分比堆叠条、7种地区颜色及叠加的“China in 2021”青色圆点；顶部百分比轴、分层类别标签、图下图例、注释、来源和加粗结论也需保留。
> 
> ### 定位一个值难在哪
> 例如“Electric cars—United States”的8来自窄堆叠段。顶轴每20个百分点一格，而5%容差仅0.4，无法可靠读准。
> 
> ### 不确定的
> 所有数值均未印在标记上；段值只能按边界估读。约100个堆叠段中部分极窄，具体段数和92对应的行存在判断不确定性。

**gemini-3.1-pro**

> ### 画出来要什么
> 生成器需要能够绘制带有两级分类轴的水平堆叠柱状图，且外层分类标签（如 "Batteries", "Solar PV"）需要逆时针旋转 90 度垂直居中显示。所有的柱子均需要撑满到 100%（最右侧的 "RoW" 分段颜色极浅，带有黑色描边）。
> 此外，图表使用了混合标记（mixed marks），生成器必须支持在特定的堆叠柱子上方（如代表 China 的红色分段），或者对应的绝对坐标处，叠加绘制散点标记（带有黑色描边的浅蓝色圆点，代表 "China in 2021"），并且该系列需要在图例中单独列出。图表顶部需要绘制从 0% 到 100% 的数值轴，且没有垂直网格线。
> 
> ### 定位一个值难在哪
> 以 `Wind -> Nacelles -> India` 的值 `8` 为例。这是一个位于堆叠中间的短分段，其起始位置约为 74%，结束位置约为 82%。要精确定位这个值，需要结合垂直旋转的外层分类名 "Wind"、内层分类名 "Nacelles" 以及通过图例颜色识别出的 "India"。
> 最难的地方在于读数（步骤2）：根据测试标准，读取容差为真实值的 5%，对于值 8 而言，容差仅为 ±0.4。在一个主刻度间距高达 20% 且没有任何垂直参考网格线的坐标系中，依靠肉眼判断中间悬空分段的起止点，绝对无法达到如此严苛的精度。
> 
> ### 不确定的
> 个别极短分段（如某些仅占 1-2% 的色块）极难通过肉眼辨认确切属于图例中的哪种颜色。此外，"RoW" 的浅灰色极度接近背景白，若不依靠边框，很容易在解析时被当作留白处理。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 144 | Figure 1.11 | above | none |
| gpt-5.6-sol | f1 | compound | 118 | Figure 1.11 | above | none |
| gemini-3.1-pro | f1 | stacked_bar | 144 | Figure 1.11 | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | — | — | opus-5: the outer group label reads 'EV'; legend reads 'RoW' |
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: 18 rows x 7 fill series plus 18 circle markers；gpt-5.6-sol: Approximately 100 stacked segments plus 18 cyan circles are drawn.；gemini-3.1-pro: 18 categories with up to 8 series marks each totals over 100 marks |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: category names sit on the left axis and bars grow rightwards from 0%；gpt-5.6-sol: Categories run vertically and every stacked bar extends to the right.；gemini-3.1-pro: categories sit on the left axis and the bars extend horizontally |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: one row under the plot: 'China, European Union, India, Japan, Korea, United States, RoW, China in 2021'；gpt-5.6-sol: The eight-entry legend from “China” through “China in 2021” sits below the bars.；gemini-3.1-pro: the color legend is placed at the bottom, outside the plot area |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: open circle markers 'China in 2021' drawn on top of each stacked bar；gpt-5.6-sol: Cyan circles labelled “China in 2021” are overlaid on stacked bars.；gemini-3.1-pro: circular markers for China in 2021 are drawn over the stacked bars |
| `pct_stacked` | ✓ | ✓ | ✓ | opus-5: every bar ends flush at the 100% gridline; top axis last tick reads 100%；gpt-5.6-sol: All 18 horizontal stacks end at the “100%” tick.；gemini-3.1-pro: every stacked bar reaches the full width of the 100% axis |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: RoW = Rest of World...' and 'Source: IEA analysis based on IEA (2024a); and IEA (2023b).'；gpt-5.6-sol: “Note: RoW = Rest of World.” and “Source: IEA analysis” appear below the plot.；gemini-3.1-pro: Note: ... Source: ... text is printed below the figure |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: each row, e.g. Blades, is built of red, blue, yellow, green and grey segments；gpt-5.6-sol: Each horizontal bar contains adjoining country and region coloured segments.；gemini-3.1-pro: segments for different regions are stacked inside one horizontal bar |
| `two_level_x_ticks` | ✓ | — | — | opus-5: left axis has an outer bracketed column (Batteries, EV, Solar PV, Wind, Other, Materials) beside item names |
| `vgrid_only` | ✓ | ✓ | — | opus-5: vertical rules at 20%, 40%, 60%, 80%; no horizontal rules in the plot；gpt-5.6-sol: Vertical grey gridlines follow the percentage ticks; no horizontal grid spans the plot. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `value_axis_on_top` | opus-5 | 2 | the 0%-100% tick row is drawn above the first bar, not below the last |
| `rotated_category_group_labels` | opus-5 | 3 | 'Batteries', 'Solar PV', 'Materials' set vertically in a bracketed column left of item labels |
| `duplicate_category_labels_across_groups` | opus-5 | 3 | 'Cells' appears twice, once under Batteries and once under Solar PV |
| `takeaway_caption_below_figure` | opus-5 | 4 | bold blue sentence under the source line: 'Manufacturing capacity for clean technologies and materials today is highly concentrated geographically...' |
| `licence_line_in_figure_area` | opus-5 | — | 'IEA. CC BY 4.0.' right-aligned between legend and the Note line |
| `hierarchical_category_axis` | gpt-5.6-sol | 3 | Rotated “Batteries”, “EV”, “Solar PV”, “Wind”, “Other”, “Materials” group the row labels. |
| `top_side_value_axis` | gpt-5.6-sol | 2 | The “0% 20% 40% 60% 80% 100%” value axis is above the bars. |
| `takeaway_line_below_notes` | gpt-5.6-sol | 4 | “Manufacturing capacity for clean technologies and materials today is highly concentrated geographically” is bold below the source. |
| `two_level_y_ticks` | gemini-3.1-pro | 3 | the left axis has inner category names and outer group names |
| `rotated_category_group_labels` | gemini-3.1-pro | 3 | the outer group labels on the left axis are rotated 90 degrees |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 92 | Anodes、China | Solar PV、Polysilicon、China | Solar PV、Cells、China | Batteries、Anodes、China | ✗ | ✗ | ✓ | 过 |
| 70 | Cathodes、China in 2021 | Batteries、Cathodes、China in 2021 | Batteries、Cathodes、China in 2021 | Solar PV、Modules、China in 2021 | ✓ | ✓ | ✗ | 过 |
| 16 | Electric cars、European Union | Wind、Blades、European Union | Wind、Nacelles、European Union | Wind、Blades、European Union | ✗ | ✗ | ✗ | 过 |
| 10 | Electric cars、United States | Wind、Blades、India | Wind、Blades、India | Materials、Ammonia、European Union | ✗ | ✗ | ✗ | 没过 |
| 91 | Polysilicon、China | Solar PV、Cells、China | Solar PV、Polysilicon、China | Solar PV、Polysilicon、China | ✗ | ✓ | ✓ | 没过 |
| 8 | Blades、India | Wind、Towers、RoW | EV、Electric cars、United States | Wind、Nacelles、India | ✗ | ✗ | ✗ | 没过 |
| 18 | Electrolysers、European Union | EV、Electric cars、European Union | EV、Electric cars、European Union | Other、Heat pumps、European Union | ✗ | ✗ | ✗ | 过 |
| 41 | Heat pumps、China in 2021 | Other、Heat pumps、China in 2021 | Other、Heat pumps、China in 2021 | Other、Electrolysers、China in 2021 | ✓ | ✓ | ✗ | 过 |
| 30 | Ammonia、China | Materials、Ammonia、China in 2021 | Materials、Ammonia、China in 2021 | Materials、Ammonia、China | ✓ | ✓ | ✓ | 没过 |
| 53 | Iron、China | Materials、Iron、China in 2021 | Materials、Iron、China in 2021 | Wind、Towers、China | ✓ | ✓ | ✗ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "stacked_bar" | "compound" | "stacked_bar" | compound | 按类型表自己的定义判：`compound` 是<strong>同一个面板里出现两种以上图元形状</strong>，所以决定它的是三家自己在 `components` 里记的 `mixed_marks`，不是它们给这张图起的名字。三家都同时记了 `stacked_bar`、`pct_stacked` 与 `mixed_marks`。 |
