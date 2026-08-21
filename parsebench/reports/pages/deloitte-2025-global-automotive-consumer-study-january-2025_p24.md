# deloitte-2025-global-automotive-consumer-study-january-2025_p24

![deloitte-2025-global-automotive-consumer-study-january-2025_p24](../../data/pages/deloitte-2025-global-automotive-consumer-study-january-2025_p24.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `deloitte-2025-global-automotive-consumer-study-january-2025_p24` | deloitte-2025-global-automotive-consumer-study-january-2025 | untagged | 6 | `parsebench/data/pages/deloitte-2025-global-automotive-consumer-study-january-2025_p24.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 本页两图无编号，各由三层文字引出：黑色加粗结论段 → 绿色图题 → 图形。图一是**横向百分比堆积条**，8 个国家 × 6 个频率段=48 段，全部数值印在段内，图例横排在图下方，无数值轴、无网格，仅左侧类别刻度（India…Japan）。图二是**纵向单系列柱**，8 根柱、值印在柱顶内侧，同样没有数值轴，只有一条基线。两图各自带独立的 Note/Q 编号/样本量小字块（"Q70. How often do you drive your current vehicle?"）。生成器还要能画极窄段（2%、3%）里的标签，并让两图使用同一批国家但**顺序与写法不同**（South Korea vs Rep. of Korea）。
> 
> ## 定位一个值难在哪
> 以 `11%` 为例：它在图一 India、Southeast Asia、US、China 四行同时出现，且都是 "1-2 times per week" 系列。要唯一命中，表格行必须同时给出国家与图例全称；只写 "11%" 或只写 "India" 都会撞上别的格子。`23%`、`25%`、`37%` 同样各出现两次以上。
> 
> ## 不确定的
> 没有图号，无法确认页面是否在别处编号；"%"是否算显式单位只能按标题文字判断；Japan 那个 `2%` 标签究竟落在段内还是溢出到相邻段，150 dpi 下难以确证；图二柱高只能靠印字，无轴可校验。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 页面含两个无编号图：八国六系列的横向百分比堆叠条，图例在下；以及八国单系列柱图。两图均无数值刻度，数值直接置于色块或柱内；标题上方另有粗体结论，图下有问题、样本量和注释。
> 
> **定位一个值难在哪**
> 
> 如 23% 要同时用“Southeast Asia”和“3-4 times per week”定位；图中另有 23%。11% 也重复出现，所以数字本身不足，但所需标签均明示。
> 
> **不确定的**
> 
> 两图均无图号；第一图没有标出 100% 的轴，只能凭等长堆叠及百分号判断为百分比堆叠。重复值的实例按阅读顺序取首次出现。

**gemini-3.1-pro**

> ### 画出来要什么
> 页面包含两张图表，均没有绘制任何数值轴或基线（`no_value_axis`），所有的百分比数值均直接打印在条形图内部（`value_label_inside`）。图1是水平方向的百分比堆叠条形图（`pct_stacked`, `horizontal_bars`），图例位于图表下方；图2是简单的垂直条形图。两图下方均附带了复杂的注释行和样本量说明（`source_note_lines`）。图表标题通过绿色字体与正文区分，并没有传统的“Figure 1”编号。生成器需要能够支持完全省略数值轴的渲染、水平堆叠布局，以及在不同宽度的色块内自适应居中打印数值标签。
> 
> ### 定位一个值难在哪
> 以图1中日本（Japan）的“Once every few months”对应的32%为例。该图没有任何数值轴可供映射，完全依赖读取色块内部的文本。如果解析器遗漏了内部的文本标签，或者无法将图例项准确映射到堆叠段的颜色上，整个数值表将无法重建。
> 
> ### 不确定的
> 图表标题仅为绿色加粗字体，缺乏显式的编号标识，不确定 Markdown 导出时这些标题是否能被识别为图表的 Caption，还是会被混入上下文的普通段落中。此外，部分 2% 和 3% 的色块极窄，不确定其文本在无引线的情况下能否被稳健提取并与色块绑定。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 48 | — | above | all |
| opus-5 | f2 | bar | 8 | — | above | all |
| gpt-5.6-sol | f1 | stacked_bar | 48 | — | above | all |
| gpt-5.6-sol | f2 | bar | 8 | — | above | all |
| gemini-3.1-pro | f1 | stacked_bar | 48 | — | above | all |
| gemini-3.1-pro | f2 | bar | 8 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | ✓ | — | opus-5: left axis labels read `US` and `UK` beside `Southeast Asia`；gpt-5.6-sol: The axis includes “US”, “UK”, and “Rep. of Korea”. |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: country names India…Japan sit on the left axis, bars grow rightward；gpt-5.6-sol: Country labels sit left of bars that extend horizontally to the right.；gemini-3.1-pro: bars grow to the right with categories on the left y-axis |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: row of six swatches "Every day … Once every few months" under the bars；gpt-5.6-sol: The six-item legend begins with “Every day” directly below the stacked bars.；gemini-3.1-pro: the legend sits below the horizontal plot area |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: two green-titled charts, each with its own Q number and sample-size block；gpt-5.6-sol: Two independent titled plots appear, each with its own question and sample-size lines.；gemini-3.1-pro: two distinct unnumbered figures with their own titles and notes |
| `no_value_axis` | ✓ | ✓ | ✓ | opus-5: bars sit on a bare baseline; no y ticks, values only as printed `70%`, `54%`；gpt-5.6-sol: Only a bottom baseline is drawn; bar values are available solely from printed labels.；gemini-3.1-pro: neither figure draws a value axis or baseline |
| `pct_stacked` | ✓ | ✓ | ✓ | opus-5: all eight bars end at the same right edge; note says "Percentages may not add up to 100 due to rounding"；gpt-5.6-sol: All eight stacks have equal full widths and their segment labels are percentages.；gemini-3.1-pro: every bar stack reaches the same full horizontal width |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: "Note: Percentages may not add up to 100 due to rounding."; "Sample size: n = 1,001 [China]…"；gpt-5.6-sol: The lines below begin “Q63.” and “Sample size: n = 261 [China]”.；gemini-3.1-pro: small print notes and sample sizes below both plots |
| `stacked_bar` | ✓ | ✓ | — | opus-5: each country row is one bar split into six coloured segments labelled 51%, 25%, 11%, 6%, 3%, 5%；gpt-5.6-sol: Each country has one horizontal bar divided into six coloured segments. |
| `thin_segment_label` | ✓ | ✓ | — | opus-5: Japan `2%` and China `2%` labels are as wide as their segments and crowd neighbours；gpt-5.6-sol: Labels “2%” and “3%” are compressed into very narrow stacked segments. |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: title reads "(% somewhat willing/willing/very willing)"; no axis carries a unit；gpt-5.6-sol: The title contains “(% somewhat willing/willing/very willing)”.；gemini-3.1-pro: the title includes (% somewhat willing/willing/very willing) |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: `70%`, `44%`, `35%` printed in white inside the top of each bar；gpt-5.6-sol: White labels from “70%” through “35%” appear inside the bars.；gemini-3.1-pro: percentages are printed inside the bar segments on both figures |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `bold_takeaway_above_title` | opus-5 | 4 | three-line bold sentence "Half of surveyed consumers in India, Southeast Asia, and the United States say they drive…" sits above the green title |
| `survey_question_and_sample_size_note` | opus-5 | 3,4 | "Q70. How often do you drive your current vehicle?" and "Sample size: n = 1,001 [China]…" under the plot |
| `same_categories_reordered_across_figures` | opus-5 | 3 | f1 order India, Southeast Asia, US, China…; f2 order India, China, Southeast Asia, US…, and `South Korea` becomes `Rep. of Korea` |
| `repeated_value_labels_within_figure` | opus-5 | 3 | `11%` printed on four different rows; `23%`, `25%`, `3%`, `5%` each printed more than once |
| `unit_in_value_labels` | gpt-5.6-sol | 2 | Every segment label carries a percent sign, including “51%” and “25%”. |
| `unit_in_value_labels` | gpt-5.6-sol | 2 | Every bar label carries a percent sign, including “70%” and “35%”. |
| `takeaway_text_above_figure` | gpt-5.6-sol | 4 | A bold paragraph above begins “Half of surveyed consumers in India, Southeast Asia, and the United States”. |
| `takeaway_text_above_figure` | gpt-5.6-sol | 4 | A bold paragraph above begins “Even though surveyed consumers in India drive a lot”. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 51% | India、Every day | India、Every day | India、Every day | India、Every day | ✓ | ✓ | ✓ | 过 |
| 23% | Southeast Asia、3-4 times per week | Southeast Asia、3-4 times per week | Southeast Asia、3-4 times per week | Japan、Every day | ✓ | ✓ | ✗ | 过 |
| 11% | US、1-2 times per week | India、1-2 times per week | India、1-2 times per week | India、1-2 times per week | ✗ | ✗ | ✗ | 过 |
| 12% | UK、Once every few months | UK、Once every few months | UK、Once every few months | UK、Once every few months | ✓ | ✓ | ✓ | 过 |
| 25% | South Korea、Every day | India、3-4 times per week | India、3-4 times per week | India、3-4 times per week | ✗ | ✗ | ✗ | 过 |
| 32% | Japan、Once every few months | Japan、Once every few months | Japan、Once every few months | Japan、Once every few months | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 3 | 3 | 4 | 未裁决 · 无实测证据 | 这一页 6 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 3 / 4 都无法证伪。 |
