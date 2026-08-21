# World_Inequality_Report_2026_p78

![World_Inequality_Report_2026_p78](../../data/pages/World_Inequality_Report_2026_p78.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `World_Inequality_Report_2026_p78` | World_Inequality_Report_2026 | 3d_chart+need_estimate | 10 | `parsebench/data/pages/World_Inequality_Report_2026_p78.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一个编号图 Figure 3.3，三联面板折线图：面板标题连成一句公式「Net national wealth =」「Domestic capital +」「Net foreign assets」；8 条区域折线×约31年×3 面板，接近 750 个点。左两面板刻度 0%–750%，第三面板 0%–100%–200% 且线跌到 0% 以下（点线零参考线），即每面板各自量程与负值区。旋转的共享轴标题「Wealth as a % of national income」只画一次，服务三个面板；图例 8 项两行置于三面板下方；下方是 Interpretation./Notes./Sources and series: 的粗体引导注释块。
> 
> ## 定位一个值难在哪
> 以 -80 为例：它在「Net foreign assets」面板里 North America & Oceania 曲线约 2022 年的位置，但该面板 0% 以下完全没有刻度标签，最近标签间距 100%，5% 容差只有 ±4；且需要「面板名 + 图例名 + 年份」三层键，而 x 轴只印 1995/2005/2015/2025，年份并非逐点标注。
> 
> ## 不确定的
> 负值区实际下限（是否 -100%）看不到；线条在 400–500% 区间八色重叠，具体归属只能靠颜色猜；625、430 等值我只能给近似归属，无法确认属于哪条线哪一年。

**gpt-5.6-sol**

> ### 画出来要什么
> 需绘制三联年度折线图：每面板8条区域线，共享下方图例；面板标题组成“Net national wealth = Domestic capital + Net foreign assets”。前两面板同量程，第三面板含零线与负值；左侧纵排单位标题，图下有解释、注释和来源。
> 
> ### 定位一个值难在哪
> 例如“Net foreign assets / MENA / 2025”的30没有印数值，只能按相隔100个百分点的刻度估读；其5%容差仅1.5，难以可靠达到。
> 
> ### 不确定的
> 折线无点标记，年度点数按1995–2025逐年估为31；625、360等值及对应系列由端点位置推断。70在任何线条上均无法可靠定位。

**gemini-3.1-pro**

> ## 画出来要什么
> 该页面包含三面板折线图，共享底部图例，并在X轴上使用稀疏的时间刻度（每10年标注，但数据点为年度）。生成器需要支持为每个面板设置不同的Y轴范围和标题（面板3包含负值且Y轴范围较小），并处理极高密度的数据（超过700个数据点）。
> 
> ## 定位一个值难在哪
> 定位如2025年East Asia的“Domestic capital”的值极其困难。图表没有数据标签，Y轴刻度间距极大（250%），而容差为5%，完全无法精确读取，且数据线在部分区域甚至超出了顶部刻度。
> 
> ## 不确定的
> 由于缺乏具体数据标签，所有抽样检查的精确数值（如625、900等）只能根据曲线终点的粗略位置进行猜测和映射，无法完全确认这些值是否准确对应图中的2025年数据点。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 744 | Figure 3.3. | above | none |
| gpt-5.6-sol | f1 | line | 744 | Figure 3.3. | above | none |
| gemini-3.1-pro | f1 | line | 744 | Figure 3.3. | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: 8 region lines over ~31 years in each of 3 panels；gpt-5.6-sol: Eight annual series across 31 years and three panels imply about 744 plotted points.；gemini-3.1-pro: 8 series over 31 years across 3 panels is 744 points |
| `hgrid_only` | — | — | ✓ | gemini-3.1-pro: horizontal grid lines only in all panels |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: two legend rows sit under the panels, above the Interpretation block；gpt-5.6-sol: The eight regional legend entries are arranged below all three plots.；gemini-3.1-pro: the legend sits below the plot area |
| `multi_figure_page` | ✓ | — | — | opus-5: only Figure 3.3 is drawn; body text names Figure 3.2 and Figure 3.5 elsewhere |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: several lines in the third panel run below the 0% dotted line；gpt-5.6-sol: Several Net foreign assets lines run below the horizontal 0% line.；gemini-3.1-pro: lines in Net foreign assets panel drop below 0% |
| `panel_title_per_panel` | ✓ | ✓ | ✓ | opus-5: 'Net national wealth =', 'Domestic capital +', 'Net foreign assets' above each panel；gpt-5.6-sol: Panels are titled “Net national wealth =”, “Domestic capital +”, and “Net foreign assets”.；gemini-3.1-pro: Net national wealth =, Domestic capital +, Net foreign assets |
| `per_panel_axis_range` | ✓ | ✓ | ✓ | opus-5: left panels tick 0%,250%,500%,750%; right panel ticks 0%,100%,200%；gpt-5.6-sol: First two panels label 0%–750%; Net foreign assets labels 0%–200% and extends below zero.；gemini-3.1-pro: panel 3 max is 200%, others are 750% |
| `reference_line` | ✓ | ✓ | — | opus-5: a black dotted horizontal rule at 0% across the Net foreign assets panel；gpt-5.6-sol: The Net foreign assets panel has a horizontal 0% line separating positive and negative values. |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Wealth as a % of national income' set vertically at the far left；gpt-5.6-sol: “Wealth as a % of national income” is printed vertically along the left side.；gemini-3.1-pro: Wealth as a % of national income is set vertically |
| `shared_legend` | ✓ | ✓ | ✓ | opus-5: one 8-entry legend below all three panels: 'East Asia ... Sub–Saharan Africa'；gpt-5.6-sol: One eight-entry regional legend governs all three panels.；gemini-3.1-pro: one single legend row below all 3 panels |
| `small_multiples_4` | ✓ | ✓ | ✓ | opus-5: three line panels of the same form side by side under one figure number；gpt-5.6-sol: Three adjacent panels repeat regional lines over 1995–2025.；gemini-3.1-pro: 3 panels aligned side by side |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Sources and series: Bauluz et al. (2025) and wir2026.wid.world/methodology.'；gpt-5.6-sol: “Notes. Net national wealth = domestic capital + net foreign assets. Sources and series:” appears below.；gemini-3.1-pro: Interpretation and Sources notes below the figure |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: yearly lines but ticks only at 1995, 2005, 2015, 2025；gpt-5.6-sol: The 1995–2025 annual lines have labels only at 1995, 2005, 2015, and 2025.；gemini-3.1-pro: ticks are every 10 years but data points are yearly |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: scale word only in rotated axis title; ticks read bare '250%','500%'；gpt-5.6-sol: The rotated axis title reads “Wealth as a % of national income”. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `equation_across_panel_titles` | opus-5 | 3,4 | panel titles read as one identity: 'Net national wealth =' 'Domestic capital +' 'Net foreign assets' |
| `shared_axis_title_across_panels` | opus-5 | 3 | one rotated 'Wealth as a % of national income' at far left governs all three panels |
| `unlabelled_negative_axis_region` | opus-5 | 2 | third panel lines fall well below 0% but no tick label appears under 0% |
| `bold_runin_note_labels` | opus-5 | 4 | 'Interpretation.' ... 'Notes.' ... 'Sources and series:' bold run-in labels inside one note paragraph |
| `equation_linked_panel_titles` | gpt-5.6-sol | 3,4 | The three panel titles join with “=” and “+” to form an accounting identity. |
| `both_axis_gridlines` | gpt-5.6-sol | — | Dashed horizontal and vertical gridlines cross every panel. |
| `math_in_panel_titles` | gemini-3.1-pro | 3 | panel titles contain = and + to form an equation |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 625 | Net national wealth =、North America & Oceania、2025 | Net national wealth =、Europe、2025 | Net national wealth =、North America & Oceania、2025 | Domestic capital +、North America & Oceania、2025 | ✗ | ✓ | ✗ | 过 |
| 360 | Net national wealth =、Sub-Saharan Africa、2025 | Net national wealth =、Latin America、1995 | Net national wealth =、Latin America、1995 | Net national wealth =、Latin America、2025 | ✗ | ✗ | ✗ | 过 |
| 600 | Net national wealth =、East Asia、1995 | Domestic capital +、East Asia、1995 | Net national wealth =、Europe、2025 |  | ✗ | ✗ | ✗ | 过 |
| 900 | Domestic capital +、East Asia、2025 | Net national wealth =、East Asia、2025 | Net national wealth =、East Asia、2025 | Domestic capital +、East Asia、2025 | ✗ | ✗ | ✓ | 过 |
| 380 | Domestic capital +、Russia & Central Asia、1995 | Net national wealth =、Sub–Saharan Africa、2005 | Net national wealth =、Russia & Central Asia、1995 | Net national wealth =、MENA、2025 | ✗ | ✗ | ✗ | 过 |
| 430 | Domestic capital +、Latin America、2025 | Domestic capital +、Latin America、2015 | Net national wealth =、Latin America、2025 | Domestic capital +、Latin America、2025 | ✗ | ✗ | ✓ | 过 |
| 30 | Net foreign assets、MENA、2025 | Net foreign assets、Europe、2025 | Net foreign assets、MENA、2025 | Net foreign assets、East Asia、2025 | ✗ | ✓ | ✗ | 过 |
| 70 | Net foreign assets、East Asia、2025 | Net foreign assets、East Asia、2025 | not_found | Net foreign assets、MENA、2025 | ✓ | ✗ | ✗ | 过 |
| -80 | Net foreign assets、North America & Oceania、2025 | Net foreign assets、North America & Oceania、2025 | Net foreign assets、Sub–Saharan Africa、1995 | Net foreign assets、Latin America、2025 | ✓ | ✗ | ✗ | 过 |
| -60 | Net foreign assets、Sub-Saharan Africa、2025 | Net foreign assets、Sub–Saharan Africa、2015 | Net foreign assets、North America & Oceania、2025 | Net foreign assets、North America & Oceania、2025 | ✗ | ✗ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
