# deloitte-2025-global-automotive-consumer-study-january-2025_p17

![deloitte-2025-global-automotive-consumer-study-january-2025_p17](../../data/pages/deloitte-2025-global-automotive-consumer-study-january-2025_p17.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `deloitte-2025-global-automotive-consumer-study-january-2025_p17` | deloitte-2025-global-automotive-consumer-study-january-2025 | untagged | 8 | `parsebench/data/pages/deloitte-2025-global-automotive-consumer-study-january-2025_p17.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 
> 三个图共处一页：顶部是 100% 横向堆叠条（8 个市场 × 4 个等级，32 段，段内白色/深色数值标签，图例在下方一行）；下方左右两个独立的单系列横向条形图，各带两行小标题（第二行加粗），条内右端印百分比，无数值轴、无网格、无刻度。还要能画：分组标题（绿色小标题「Importance of next vehicle to be manufactured locally」）、上方加粗导语段、图下 Note/Q31/Sample size 三行小字，以及两图共用一段问卷脚注。
> 
> ## 定位一个值难在哪
> 
> 「45%」是 Japan 行 Somewhat important 段。它没有图号、没有标题层级可用，行标签来自 y 轴刻度「Japan」，系列名只在底部图例「Somewhat important」，还需图上方绿色标题限定主题；同一页另一处 39% 出现两次（China、Rep. of Korea 的 Important），只靠数值搜索会撞车。
> 
> ## 不确定的
> 
> 三图都无编号，标题层级（导语粗体 vs 绿色小标题 vs 灰色两行小标题）谁属于哪张图只能靠版式推断；底部两图是否算一个双面板图不确定；条形是否有隐藏的 0–100 轴看不到。

**gpt-5.6-sol**

> **画出来要什么**
> 页面含一幅四系列横向百分比堆叠条形图，以及两幅并排的单系列横条图。所有数值置于条内；数值轴及刻度隐藏。首图图例在下方，三图均有分类轴和注释行。
> 
> **定位一个值难在哪**
> 首图的39%出现两次：China和Rep. of Korea均对应“Important”。唯一定位必须同时保留国家轴标签与图例系列名。
> 
> **不确定的**
> 下方两图共享说明文字且并排布局，也可能被设计者视为一个双面板图；这里按各自独立标题判作两幅图。

**gemini-3.1-pro**

> ## 画出来要什么
> 页面包含三个无编号的水平条形图，第一个为百分比堆积条形图，后两个为独立排序的简单水平条形图。三个图表均没有数值轴和任何网格线，数值全部直接以标签形式印在条形内部。需要生成器支持彻底隐去坐标轴、根据数值自动内部对齐文本标签、在图表下方放置图例和详细的注释行（Note和Sample size）。
> 
> ## 定位一个值难在哪
> 以41%（India，Very important）为例，该值完全依赖于条形段内部的文本。因没有任何数值轴作为基准，一旦解析模型未将其识别为图表或未能提取覆盖在色块上的文本，就无法得出任何数据。
> 
> ## 不确定的
> 底部的两个水平条形图在视觉上并排且分类相同，但不共用同一个Y轴（各自按降序独立排列）。这里将它们视为两个独立的无编号图表进行处理，而不视为单个图表的两个面板。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 32 | — | above | all |
| opus-5 | f2 | bar | 8 | — | above | all |
| opus-5 | f3 | bar | 8 | — | above | all |
| gpt-5.6-sol | f1 | stacked_bar | 32 | — | above | all |
| gpt-5.6-sol | f2 | bar | 8 | — | above | all |
| gpt-5.6-sol | f3 | bar | 8 | — | above | all |
| gemini-3.1-pro | f1 | stacked_bar | 32 | — | above | all |
| gemini-3.1-pro | f2 | bar | 8 | — | above | all |
| gemini-3.1-pro | f3 | bar | 8 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | ✓ | — | opus-5: 'US', 'UK', 'Rep. of Korea' on the y axis；gpt-5.6-sol: “UK” and “US” are category-axis abbreviations. |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: India, China... on y axis, green bars grow right to 82%；gpt-5.6-sol: Eight green bars extend rightward from the country labels.；gemini-3.1-pro: all bars grow horizontally from left to right |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'Not important / Somewhat important / Important / Very important' row under the plot；gpt-5.6-sol: The four-item legend sits in one row beneath the stacked bars.；gemini-3.1-pro: the legend sits below the stacked bars |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: three separate unnumbered charts with their own headings and their own question footnotes；gpt-5.6-sol: One stacked chart and two separately headed bar charts appear on the page.；gemini-3.1-pro: there are three distinct unnumbered figures on the page |
| `no_value_axis` | ✓ | ✓ | ✓ | opus-5: only a vertical baseline at left; no numeric ticks anywhere；gpt-5.6-sol: No numeric value ticks appear; each green bar carries its percentage.；gemini-3.1-pro: none of the three figures draws an axis line or ticks for values |
| `panel_title_per_panel` | ✓ | — | — | opus-5: lower charts each carry a two-line grey heading with bolded second line above themselves |
| `pct_stacked` | ✓ | ✓ | ✓ | opus-5: every row reaches the same right edge; segments read 10%+19%+31%+41%；gpt-5.6-sol: All eight stacks have equal full width and their segment labels are percentages.；gemini-3.1-pro: all stacked bars sum to roughly 100% and span full width |
| `side_text_bullets` | ✓ | — | — | opus-5: bold lead paragraphs 'As global trade policies shift...' sit directly above each chart block |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Q61...' 'Q60...' 'Sample size: n = 939 [China]; 1,306 [Germany]...' under the lower charts；gpt-5.6-sol: “Q60.” and the shared “Sample size” line appear beneath the lower charts.；gemini-3.1-pro: Note: and sample size notes appear below the figures |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: each market row split into four coloured segments totalling the full bar；gpt-5.6-sol: Each country has one bar divided into four adjoining response segments.；gemini-3.1-pro: segments are stacked left to right within each category |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: 'Percentage of surveyed consumers who would be interested in acquiring' above the plot；gpt-5.6-sol: The heading begins “Percentage of surveyed consumers”.；gemini-3.1-pro: the word Percentage starts the titles of f2 and f3 |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: '82%' printed inside the India bar；gpt-5.6-sol: Labels from “82%” through “32%” sit inside the green bars.；gemini-3.1-pro: numbers are printed inside the bar segments in all figures |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `paired_independent_charts_side_by_side` | opus-5 | 3,4 | two same-format bar charts side by side, different row order, sharing one footnote block |
| `bold_phrase_in_chart_subtitle` | opus-5 | 3,4 | 'insurance directly from the manufacturer' bolded inside an otherwise regular grey heading line |
| `question_id_caption` | opus-5 | 4 | 'Q31.', 'Q61.', 'Q60.' prefix the survey wording under the charts |
| `category_order_differs_between_panels` | opus-5 | 3 | left chart ends India...Japan; right chart ends India...Germany, UK above US |
| `adaptive_value_label_colour` | gpt-5.6-sol | — | Labels are white on dark segments but dark gray on the pale aqua segments. |
| `partial_heading_emphasis` | gpt-5.6-sol | 4 | “insurance directly from the manufacturer” is bold within an otherwise regular-weight heading. |
| `shared_note_block_across_figures` | gpt-5.6-sol | 4 | Q61, Q60 and one Sample size block sit beneath both lower charts. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 41 | India、Very important | India、Very important | India、Very important | India、Very important | ✓ | ✓ | ✓ | 过 |
| 39 | China、Important | China、Important | China、Important | China、Important | ✓ | ✓ | ✓ | 过 |
| 27 | Southeast Asia、Somewhat important | Southeast Asia、Somewhat important | Southeast Asia、Somewhat important | Southeast Asia、Somewhat important | ✓ | ✓ | ✓ | 过 |
| 28 | US、Not important | US、Not important | US、Not important | US、Not important | ✓ | ✓ | ✓ | 过 |
| 39 | Rep. of Korea、Important | Rep. of Korea、Important | Rep. of Korea、Important | Rep. of Korea、Important | ✓ | ✓ | ✓ | 过 |
| 45 | Japan、Somewhat important | Japan、Somewhat important | Japan、Somewhat important | Japan、Somewhat important | ✓ | ✓ | ✓ | 过 |
| 36 | Germany、Not important | Germany、Not important | Germany、Not important | Germany、Not important | ✓ | ✓ | ✓ | 过 |
| 49 | UK、Not important | UK、Not important | UK、Not important | UK、Not important | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 3 | 3 | 1 | 未裁决 · 无实测证据 | 这一页 8 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 3 / 1 都无法证伪。 |
| `value_axes#f1` | 1 | 0 | 0 | 0 | 三家都读成 India–UK 的横向堆叠条。opus 记了一条底边值轴，但它自己在 `serves` 里写的是「no ticks drawn; stack length only」——那条轴没有画出来。gpt 与 gemini 只记了左边的类目轴。按「画出来的值轴」判为 0，这正是词表里的 `no_value_axis`。 |
| `key_roles#f2` | ["category", "series"] | ["category"] | ["category"] | category | gpt 与 gemini 一致。opus 多记的一段来自 `heading`（这张图问的问题），而这一页已经按问题切成了几张图，图内只用国家一段就唯一。 |
| `key_roles#f3` | ["category", "series"] | ["category"] | ["category"] | category | 同 f2。 |
