# World_Inequality_Report_2026_p38

![World_Inequality_Report_2026_p38](../../data/pages/World_Inequality_Report_2026_p38.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `World_Inequality_Report_2026_p38` | World_Inequality_Report_2026 | untagged | 10 | `parsebench/data/pages/World_Inequality_Report_2026_p38.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一个编号图 `Figure 1.3` 下挂两块异构面板：左侧分组柱（Income/Wealth 各 3 根），右侧 100% 堆叠柱（每根 4 段）。标题分四层：`Figure 1.3.` + 主标题 `Income and wealth shares are distributed very unequally` + 副标题 `Global income and wealth inequality, 2025` + 每面板小标题 `By broad groups` / `More detail on the top 10%`。两侧各自绘制竖排轴标题 `Share of global income or wealth`，刻度 `0%`–`100%`，左面板带虚线水平网格。图例分两处置于各面板下方，但右面板的蓝、绿段只在左面板图例里被命名。数值标签一图两制：左面板在柱外顶端，右面板在段内，`2%` 因段太薄被挤到基线附近。
> 
> ## 定位一个值难在哪
> `38`：左面板 Income 的 Middle 40% 是 38%，右面板 Wealth 的 Next 9% 也是 38%，右面板 Income 绿段同样是 38%。要唯一定位必须同时给出面板小标题、类别（Income/Wealth）与图例名，缺一即错行。
> 
> ## 不确定的
> 右面板是否真的完全无网格线难以在 150 dpi 下确认；左右面板是否共用同一 y 轴刻度对象（各自都画了轴标题，我按两条轴记）；`Interpretation.` 段落算注释还是正文，我归入 source/note。

**gpt-5.6-sol**

> ### 画出来要什么
> 需绘制同一编号下的双面板复合图：左侧分组柱，右侧百分比堆叠柱；面板各有标题，共用颜色体系但图例分列两侧。还需支持虚线横网格、竖排轴题、柱外与段内数值标签，以及图下解释和来源行。
> 
> ### 定位一个值难在哪
> “38”出现两次：既是“By broad groups / Income / Middle 40%”，也是“More detail on the top 10% / Wealth / Next 9%”。必须保留面板、类别、组别三层键。
> 
> ### 不确定的
> 图例视觉上分成左右两块；我按分层共享图例处理。百分号只见于刻度和标签，未见独立单位行。

**gemini-3.1-pro**

> ## 画出来要什么
> 生成器需要支持并排绘制两个具有相同y轴刻度但分别拥有独立坐标系的百分比堆叠柱状图（`pct_stacked`），且能够为每个面板添加独立的标题（`panel_title_per_panel`）。图例需放置在图表底部统一区域（`shared_legend`），且允许某个面板复用另一组图例定义的颜色。y轴标题需支持垂直旋转显示（`rotated_axis_title`），数据标签需直接居中打印在对应颜色的堆叠段内（`value_label_inside`）。
> 
> ## 定位一个值难在哪
> 以右侧面板的“33”为例，其地址键需要包含面板名“More detail on the top 10%”、分类名“Income”和图例名“Next 9%”。难点在于全图图例虽然合并放在底部，但位置上分成了两组；解析器必须通过颜色匹配将“Bottom 50%”等左侧图例项与右侧面板中的对应色块正确绑定，并在表格中引入面板维度，否则无法区分两侧同名的Income分类段。
> 
> ## 不确定的
> 右侧面板底部的蓝绿段（8%和38%）对应的图例放置在左下方，读者能通过颜色自然关联，不确定解析器能否同样基于颜色进行跨区段的全局映射，或者会因为图例在视觉上更靠近左面板而忽略对右侧底色块的识别。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | compound | 14 | Figure 1.3. | above | all |
| gpt-5.6-sol | f1 | compound | 14 | Figure 1.3. | above | all |
| gemini-3.1-pro | f1 | stacked_bar | 14 | Figure 1.3. | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `grouped_bar` | ✓ | ✓ | — | opus-5: left panel: three coloured bars side by side over each of Income and Wealth；gpt-5.6-sol: “By broad groups” has three side-by-side bars for Income and Wealth. |
| `heterogeneous_panel_types` | ✓ | ✓ | — | opus-5: grouped bars under 'By broad groups' beside stacked bars under 'More detail on the top 10%'；gpt-5.6-sol: The left panel uses grouped bars; the right panel uses percent-stacked bars. |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: left panel shows dashed horizontal rules at each 10% tick, no vertical rules；gpt-5.6-sol: Dashed horizontal gridlines cross both panels; no vertical gridlines are drawn.；gemini-3.1-pro: horizontal dotted lines across plot, no vertical lines |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'Bottom 50% / Middle 40% / Top 10%' and 'Next 9% / Top 1%' rows sit under the plots；gpt-5.6-sol: Colour swatches and group names are placed below the two plot areas.；gemini-3.1-pro: legend items sit beneath the two panels |
| `panel_title_per_panel` | ✓ | ✓ | ✓ | opus-5: 'By broad groups' and 'More detail on the top 10%' set in bold above each panel；gpt-5.6-sol: “By broad groups” and “More detail on the top 10%” appear above their panels.；gemini-3.1-pro: By broad groups and More detail on the top 10% sit above their respective panels |
| `pct_stacked` | ✓ | ✓ | ✓ | opus-5: right panel stacks both reach the top tick '100%' (8+38+33+20; 2+23+38+37)；gpt-5.6-sol: Both right-panel stacks reach the 100% tick.；gemini-3.1-pro: bars are stacked and their segments sum to 100% |
| `per_panel_legend` | ✓ | — | — | opus-5: left legend has three keys, right legend only 'Next 9%' and 'Top 1%' |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Share of global income or wealth' set vertically along each left axis；gpt-5.6-sol: “Share of global income or wealth” is vertical beside each y axis.；gemini-3.1-pro: Share of global income or wealth is vertical along the y-axis |
| `shared_legend` | — | ✓ | ✓ | gpt-5.6-sol: Legend entries below both panels jointly identify the five colour groups.；gemini-3.1-pro: the bottom legend governs colors for both panels |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Interpretation. ... Sources and series: Arias–Osorio et al. (2025) and wir2026.wid.world/methodology.'；gpt-5.6-sol: “Interpretation.” and “Sources and series:” appear below the legends.；gemini-3.1-pro: Interpretation. and Sources and series: text below the figure |
| `stacked_bar` | ✓ | ✓ | — | opus-5: right panel: four coloured segments stacked inside each of the Income and Wealth bars；gpt-5.6-sol: “More detail on the top 10%” stacks four coloured segments in each bar. |
| `thin_segment_label` | ✓ | ✓ | — | opus-5: '2%' in the right panel Wealth stack sits on the baseline, segment too thin to hold it；gpt-5.6-sol: The “2%” label is squeezed into the thin Wealth bottom segment. |
| `unit_in_axis_or_title` | ✓ | — | — | opus-5: scale phrase 'Share of global income or wealth' only on the axis title; ticks read '0%'..'100%' |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: right panel: '20%', '33%', '38%', '37%' printed within their stacked segments；gpt-5.6-sol: Right-panel percentages such as “33%” and “37%” are printed inside segments.；gemini-3.1-pro: numbers like 8%, 38% are inside the coloured segments |
| `value_label_outside` | ✓ | ✓ | — | opus-5: left panel: '8%', '38%', '53%', '75%' printed above the bar tops；gpt-5.6-sol: Left-panel percentages such as “53%” and “75%” sit above the bars. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `legend_split_across_panels` | opus-5 | 3 | right panel's blue 8%/2% and green 38%/23% segments are named only by the left panel's legend |
| `same_value_repeated_across_panels` | opus-5 | 3 | '8%', '38%', '23%', '2%' each appear in both the grouped and the stacked panel |
| `full_width_figure_over_two_column_text` | opus-5 | 4 | figure and note span the page width; two columns of body text start below them |
| `split_hierarchical_legend` | gpt-5.6-sol | 3 | Broad-group legend entries sit left; “Next 9%” and “Top 1%” sit right. |
| `unit_in_tick_labels` | gpt-5.6-sol | 2,4 | Every value tick carries %, from “0%” through “100%”; no separate unit line appears. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 8 | Bottom 50%、Income | By broad groups、Income、Bottom 50% | By broad groups、Income、Bottom 50% | By broad groups、Income、Bottom 50% | ✓ | ✓ | ✓ | 过 |
| 38 | Middle 40%、Income | By broad groups、Income、Middle 40% | By broad groups、Income、Middle 40% | By broad groups、Income、Middle 40% | ✓ | ✓ | ✓ | 过 |
| 53 | Top 10%、Income | By broad groups、Income、Top 10% | By broad groups、Income、Top 10% | By broad groups、Income、Top 10% | ✓ | ✓ | ✓ | 过 |
| 2 | Bottom 50%、Wealth | By broad groups、Wealth、Bottom 50% | By broad groups、Wealth、Bottom 50% | By broad groups、Wealth、Bottom 50% | ✓ | ✓ | ✓ | 过 |
| 23 | Middle 40%、Wealth | By broad groups、Wealth、Middle 40% | By broad groups、Wealth、Middle 40% | By broad groups、Wealth、Middle 40% | ✓ | ✓ | ✓ | 过 |
| 75 | Top 10%、Wealth | By broad groups、Wealth、Top 10% | By broad groups、Wealth、Top 10% | By broad groups、Wealth、Top 10% | ✓ | ✓ | ✓ | 过 |
| 33 | Next 9%、Income | More detail on the top 10%、Income、Next 9% | More detail on the top 10%、Income、Next 9% | More detail on the top 10%、Income、Next 9% | ✓ | ✓ | ✓ | 过 |
| 20 | Top 1%、Income | More detail on the top 10%、Income、Top 1% | More detail on the top 10%、Income、Top 1% | More detail on the top 10%、Income、Top 1% | ✓ | ✓ | ✓ | 过 |
| 38 | Next 9%、Wealth | More detail on the top 10%、Wealth、Next 9% | More detail on the top 10%、Wealth、Next 9% | More detail on the top 10%、Wealth、Next 9% | ✓ | ✓ | ✓ | 过 |
| 37 | Top 1%、Wealth | More detail on the top 10%、Wealth、Top 1% | More detail on the top 10%、Wealth、Top 1% | More detail on the top 10%、Wealth、Top 1% | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "compound" | "compound" | "stacked_bar" | stacked_bar · 同时又分组 | 按类型表自己的定义判：`compound` 是<strong>同一个面板里出现两种以上图元形状</strong>，所以决定它的是三家自己在 `components` 里记的 `mixed_marks`，不是它们给这张图起的名字。<strong>三家一个都没记 `mixed_marks`</strong>，所以不是 compound。opus 与 gpt 同时记了 `stacked_bar`、`grouped_bar` 与 `pct_stacked`——也就是词表里的 `stacked_and_grouped`：条既并排分组、每根里又堆叠。那一项的 `ours` 是 false（两个维度分别吃掉 P 与 S，第三维无处可放），所以这一条同时是我们画不出来的一例。 |
| `hardest_step` | 3 | 1 | 3 | 未裁决 · 无实测证据 | 这一页 10 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 1 / 3 都无法证伪。 |
