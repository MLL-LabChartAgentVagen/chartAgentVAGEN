# sri-sigma-natural-catastrophes-1-2025_p20

![sri-sigma-natural-catastrophes-1-2025_p20](../../data/pages/sri-sigma-natural-catastrophes-1-2025_p20.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `sri-sigma-natural-catastrophes-1-2025_p20` | sri-sigma-natural-catastrophes-1-2025 | need_estimate | 10 | `parsebench/data/pages/sri-sigma-natural-catastrophes-1-2025_p20.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 两张独立编号图，都放在浅蓝色底的整块面板里，标题块（`Figure 12` + `US Construction cost indices`）位于绘图区**左侧一列**而非上方。图12是四条月度指数折线，y 轴 100–150（不从零起、无单位词、无 `2020=100` 基期说明），x 轴只有 2020…2025 六个年刻度，约 250 个数据点；图例四项在图下一行半排列。图13是**一条面积序列按正负换色**：0% 以上填深青 `Underwriting profit`，0% 以下填浅绿 `Underwriting loss`，y 轴 10% 到 −15%，负值与零线是主要构图。两图都只有横向网格线、图下 `Source:` 行。
> 
> ## 定位一个值难在哪
> 取 `-6%`：图13上没有任何数字标签，刻度间距 5 个百分点，而 2020、2022、2024 三年读数都落在 −5% 与 −7% 之间；5% 相对容差意味着要读到 ±0.3pp，靠像素无法区分这三年，且只能用 `Underwriting loss` + 年份两个标签寻址，而颜色本身又不区分年份。
> 
> ## 不确定的
> 图12哪条线对应哪个图例只能靠颜色深浅推断（`CPI` 深青最低线、`PPI, Final Demand, Construction` 深蓝最高线）；月度点的实际频率、指数基期日期、以及 138 属于哪两条线，均为推测。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 两个浅蓝底单面板图：图12绘制四条月度指数线、年度稀疏刻度和下置图例；图13绘制跨零轴、按盈亏换色的面积图。两图标题均在绘图区左侧，附下置来源行。
> 
> **定位一个值难在哪**
> 
> 图13的2019年“Underwriting profit”值2.5%没有印出；纵轴每格5个百分点，而5%容差仅0.125个百分点，难以准确轴读。
> 
> **不确定的**
> 
> 图12无数据点标记，月度类别数只能估计；100、102及两处138的具体月份和系列需按年度刻度附近的线位推断。

**gemini-3.1-pro**

> ### 画出来要什么
> 这个页面包含两个图表。Figure 12 是一个多线图，展示了四条折线，背景整个图表区域带有浅蓝色阴影，图表的编号和标题位于绘图区的左侧（左右并排布局）。x轴刻度为稀疏的年份刻度（2020到2025），但数据线呈现出更高频的波动（推测是月度或季度数据），y轴无明确单位，基准从100开始。Figure 13 是一个面积图，展示了包含负值的数据（从 -15% 到 10%），特殊之处在于它将0轴以上的区域填充为深绿色（代表 Underwriting profit），将0轴以下的区域填充为浅绿色（代表 Underwriting loss），并在底部的图例中分别标注了这两种状态。
> 
> ### 定位一个值难在哪
> 以 Figure 13 中的 **9%** 为例，它出现在2015年的峰值处。因为图表上没有任何直接打印的数值标签，且y轴的步长为5%，加上面积图的折点并不在网格线上，完全依靠肉眼去对齐左侧坐标轴，要在5%的误差容限内读出准确的9%是非常困难的。
> 
> ### 不确定的
> Figure 12 中由于只标注了年份，无法确定折线具体是月度还是季度数据；Figure 13 中连续的面积图不确定是由两个相互拼接的系列组成，还是单个数据系列在管线渲染时自动按正负值赋予了不同颜色。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 248 | Figure 12 | beside | none |
| opus-5 | f2 | area | 11 | Figure 13 | beside | none |
| gpt-5.6-sol | f1 | line | 248 | Figure 12 | beside | none |
| gpt-5.6-sol | f2 | area | 11 | Figure 13 | beside | none |
| gemini-3.1-pro | f1 | line | 240 | Figure 12 | beside | none |
| gemini-3.1-pro | f2 | area | 11 | Figure 13 | beside | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_starts_above_zero` | ✓ | ✓ | — | opus-5: lowest y tick is `100`, no break glyph drawn on the axis；gpt-5.6-sol: The lowest labelled value tick is “100”; no axis break is drawn. |
| `color_encodes_extra_attribute` | ✓ | ✓ | ✓ | opus-5: one continuous result series is filled dark teal above zero, green below, per profit/loss；gpt-5.6-sol: The same underwriting result is teal above zero and green below zero.；gemini-3.1-pro: profit is dark green and loss is light green |
| `dense_marks_100plus` | ✓ | ✓ | — | opus-5: four lines over roughly five years of monthly points, ~250 plotted points；gpt-5.6-sol: Four monthly lines span roughly 62 dates, about 248 plotted vertices. |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: horizontal rules at 10%,5%,0%,−5%,−10%,−15%; no vertical rules；gpt-5.6-sol: Horizontal rules cross the plot from “−15%” to “10%”; no vertical gridlines appear.；gemini-3.1-pro: both figures have horizontal rules and no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: `Underwriting profit` and `Underwriting loss` swatches sit below the 2014–2024 axis；gpt-5.6-sol: “Underwriting profit” and “Underwriting loss” appear below the time axis.；gemini-3.1-pro: the legends sit below the x-axis in both figures |
| `multi_figure_page` | ✓ | ✓ | — | opus-5: `Figure 12 US Construction cost indices` and `Figure 13 US homeowner insurance underwriting result` on one page；gpt-5.6-sol: Separate numbered graphics are headed “Figure 12” and “Figure 13”. |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: area drops to about −10% in 2023; axis runs to `−15%` below the 0% line；gpt-5.6-sol: The area extends below “0%” to near “−10%”.；gemini-3.1-pro: y-axis goes down to -15% with a zero baseline |
| `panel_background` | ✓ | ✓ | ✓ | opus-5: pale blue tinted block behind heading, plot, legend and source line；gpt-5.6-sol: The plot and surrounding figure panel have a pale blue fill.；gemini-3.1-pro: the entire figure block has a light blue tint |
| `reference_line` | ✓ | ✓ | — | opus-5: a rule at `0%` separates the dark profit fill above from the green loss fill below；gpt-5.6-sol: A horizontal “0%” line separates the profit and loss fills. |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: `Source: AM Best, Swiss Re Institute` printed under the legend；gpt-5.6-sol: “Source: AM Best, Swiss Re Institute”；gemini-3.1-pro: Source lines are printed below both figures |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: lines move month to month but ticks read only 2020, 2021, 2022, 2023, 2024, 2025；gpt-5.6-sol: Monthly line vertices appear between annual ticks “2020” through “2025”.；gemini-3.1-pro: ticks are yearly but the line fluctuates between them |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `sign_split_area_fill` | opus-5 | 3 | single area series whose fill flips colour at 0%; each colour gets its own legend entry |
| `index_base_unstated` | opus-5 | 4 | all four lines start at 100 in early 2020 but no `2020 = 100` phrase appears anywhere |
| `heading_block_in_left_margin_column` | opus-5 | 3,4 | `Figure 12` and its title sit in a narrow left column level with the plot, inside the tinted block |
| `heading_beside_plot` | gpt-5.6-sol | 4 | Both figure numbers and titles occupy left columns level with their plots. |
| `sign_split_area` | gpt-5.6-sol | 3 | One area switches fill at zero crossings, teal above and green below. |
| `heading_beside_plot` | gemini-3.1-pro | 4 | Figure number and title sit in a left column beside the plot area |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 100 | 2020、CPI | CPI、2020 | CPI、2021 | CPI、2020 | ✓ | ✗ | ✓ | 过 |
| 102 | 2021、PPI, Materials & Components for Construction | PPI, Final Demand, Construction、2020 | PPI Final Demand, Construction、2021 | CPI、2021 | ✗ | ✗ | ✗ | 过 |
| 138 | 2022、PPI, Final Demand, Construction | One-Family Houses under Construction, Census、2024 | PPI Final Demand, Construction、2024 | One-Family Houses under Construction, Census、2022 | ✗ | ✗ | ✗ | 过 |
| 138 | 2023、One-Family Houses under Construction, Census | PPI, Final Demand, Construction、2023 | One-Family Houses under Construction, Census、2024 | PPI, Final Demand, Construction、2023 | ✗ | ✗ | ✗ | 过 |
| 122 | 2025、CPI | CPI、2025 | CPI、2025 | CPI、2025 | ✓ | ✓ | ✓ | 过 |
| 9% | 2014、Underwriting profit | Underwriting profit、2014 | Underwriting profit、2014 | Underwriting profit、2015 | ✓ | ✓ | ✗ | 过 |
| -7% | 2017、Underwriting loss | Underwriting loss、2017 | Underwriting loss、2017 | Underwriting loss、2017 | ✓ | ✓ | ✓ | 过 |
| 2.5% | 2019、Underwriting profit | Underwriting profit、2019 | Underwriting profit、2019 | Underwriting profit、2019 | ✓ | ✓ | ✓ | 没过 |
| -10% | 2023、Underwriting loss | Underwriting loss、2023 | Underwriting loss、2023 | Underwriting loss、2023 | ✓ | ✓ | ✓ | 过 |
| -6% | 2024、Underwriting loss | Underwriting loss、2024 | Underwriting loss、2024 | Underwriting loss、2024 | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `key_roles#f2` | ["series", "time"] | ["series", "time"] | ["colour_group", "time"] | series × time | <strong>colour_group 的判据</strong>：只由颜色承载、既不是系列也不是类目的<strong>第三个变量</strong>。单独给某一个类目换色（`highlighted_category`）不算；图例里列出的项是 series。 gemini 把图例里的 `Underwriting profit` 记成了 colour_group——图例里列出来的项是 series。opus 与 gpt 都记 series。 |
