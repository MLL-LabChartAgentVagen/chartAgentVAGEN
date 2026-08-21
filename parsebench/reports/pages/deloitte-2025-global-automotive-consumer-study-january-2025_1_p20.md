# deloitte-2025-global-automotive-consumer-study-january-2025_1_p20

![deloitte-2025-global-automotive-consumer-study-january-2025_1_p20](../../data/pages/deloitte-2025-global-automotive-consumer-study-january-2025_1_p20.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `deloitte-2025-global-automotive-consumer-study-january-2025_1_p20` | deloitte-2025-global-automotive-consumer-study-january-2025_1 | untagged | 6 | `parsebench/data/pages/deloitte-2025-global-automotive-consumer-study-january-2025_1_p20.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 三个无编号图形共处一页：两张并排的水平条形图（青色/绿色），各自带一行加粗混排的说明性标题（`Percentage of consumers concerned about **fully autonomous robotaxi services** operating where they live`），无数值轴、无刻度、无网格，数值全部白字印在条内右端；下半页一张 8 行百分比堆叠水平条（Not beneficial / Neutral / Beneficial），图例居下，上方另有一行绿色小标题 `Addition of artificial intelligence in vehicle systems`，其上又有一段加粗结论式正文。还需渲染 `Q56.`/`Q62.`/`Sample size: n = 939 [China]; ...` 多行脚注与页眉页脚。
> 
> ## 定位一个值难在哪
> `13%` 是 India 行的 Neutral 段：条内标签，但要唯一定位需 3 个键——行类别 `India`、系列 `Neutral`、以及区分它属于下方 AI 图而非上方两张图的图形名 `Addition of artificial intelligence in vehicle systems`。三张图都含 `India` 行，若解析后只留 `India | 13%`，与上图 `63%`/`74%` 同键冲突。
> 
> ## 不确定的
> 三图均无 `Figure` 编号，无法确认报告中是否另有编号；两张上部图是否算一个双面板图形还是两个独立图形不可判定；所有条形无轴刻度，无法验证条长与印刷值是否严格成比例。

**gpt-5.6-sol**

> ### 画出来要什么
> 页面含两个独立图形：上图为双面板水平条形图，每个国家值写在条内；下图为八国三段式百分比堆叠条形图，图例置于下方。两图均无可见数值刻度，并带问题及样本量说明。
> 
> ### 定位一个值难在哪
> 下图的 India 同时有 82%、13% 和 5%，定位 82% 必须联合国家“India”和图例项“Beneficial”；单凭数值或国家不足以确定分段。
> 
> ### 不确定的
> 页面未印图号；据独立标题和各自说明行判断为两个图。41%也见于上图 Japan，但给定序列整体对应下图 Germany–Beneficial。

**gemini-3.1-pro**

> ### 画出来要什么
> 本页包含两组基于正文段落作为标题的水平条形图。
> 图1包含左右两个并排的面板，各面板有独立的类别轴（受访国家排序不同），且无数值轴，数据标签直接印在条形内部；面板上方有各自较长的描述性标题作为面板名。
> 图2是一个100%堆叠水平条形图（`pct_stacked`），同样无数值坐标轴（`no_value_axis`），三个系列的图例位于图表下方。生成器需要支持水平条形（`horizontal_bars`）、内嵌数值标签（`value_label_inside`）以及无坐标轴的纯标签渲染模式。
> 
> ### 定位一个值难在哪
> 以图2中印度的“Beneficial”数值 `82` 为例。最大的困难在于图表没有任何数值刻度和坐标轴线。多数视觉解析器强依赖于检测坐标轴来确立图表区域与数据映射关系。对于只有条形色块和内部文字标签的图表，解析器往往无法识别其为有效图表，从而导致完全无法提取出任何数据表（Step 1容易失败）。
> 
> ### 不确定的
> 全页没有类似于“Figure X”的显式编号。两组图表的首段实际上是以较粗字体排版的总结性正文段落，是否应将其直接视为图表标题存在一定歧义，本报告将其全部作为标题处理。此外，图2的图例中存在拼写错误“Not benefical”（缺少第二个i）。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | bar | 8 | — | above | all |
| opus-5 | f2 | bar | 8 | — | above | all |
| opus-5 | f3 | stacked_bar | 24 | — | above | all |
| gpt-5.6-sol | f1 | bar | 16 | — | above | all |
| gpt-5.6-sol | f2 | stacked_bar | 24 | — | above | all |
| gemini-3.1-pro | f1 | bar | 16 | — | above | all |
| gemini-3.1-pro | f2 | stacked_bar | 24 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | — | — | opus-5: 'UK', 'US', 'Rep. of Korea' used as category labels |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: eight country rows at left, stacked segments run left to right；gpt-5.6-sol: Eight country stacks extend horizontally from a common left baseline.；gemini-3.1-pro: categories run down the left, bars extend to the right |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'Not beneficial  Neutral  Beneficial' row sits under the last bar；gpt-5.6-sol: “Not beneficial”, “Neutral”, and “Beneficial” appear in a row beneath the bars.；gemini-3.1-pro: the three-item legend is situated below the chart |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: two side-by-side bar charts with their own captions plus a separate stacked-bar figure below；gpt-5.6-sol: Upper Q56 and lower Q62 charts have separate headings and explanatory lines.；gemini-3.1-pro: two distinct chart blocks with their own note lines below |
| `no_value_axis` | ✓ | ✓ | ✓ | opus-5: no ticks or 0-100 scale under the stacked rows；gpt-5.6-sol: No value ticks are visible; every segment value is printed directly.；gemini-3.1-pro: no numerical axis line or ticks exist at the bottom |
| `panel_title_per_panel` | — | ✓ | ✓ | gpt-5.6-sol: Each panel begins with its own “Percentage of consumers concerned about” scenario heading.；gemini-3.1-pro: column headers act as separate panel titles |
| `pct_stacked` | ✓ | ✓ | ✓ | opus-5: every row reaches the same full width; 5%+13%+82% = 100%；gpt-5.6-sol: All eight stacks have equal full width and their printed segment percentages total 100%.；gemini-3.1-pro: stacked segments all add up to 100% of uniform length |
| `side_text_bullets` | ✓ | — | — | opus-5: bold lead-in paragraphs above each figure: 'Consumers surveyed in both India and the United Kingdom are more concerned...' |
| `small_multiples_4` | — | ✓ | — | gpt-5.6-sol: Two side-by-side panels repeat horizontal country bars for different autonomous-vehicle scenarios. |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: Percentages may not add up to 100 due to rounding.' and 'Q62. ...'；gpt-5.6-sol: “Note: Percentages may not add up to 100 due to rounding.” appears below.；gemini-3.1-pro: Q56, Q62 and note text sit below each figure |
| `stacked_bar` | ✓ | ✓ | — | opus-5: each row has three segments Not beneficial / Neutral / Beneficial；gpt-5.6-sol: Each country has one bar divided into Not beneficial, Neutral, and Beneficial segments. |
| `thin_segment_label` | ✓ | — | — | opus-5: '5%' and '6%' labels fill nearly the whole narrow dark-blue segment |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: 'Percentage of consumers concerned about fully autonomous robotaxi services operating where they live'；gpt-5.6-sol: Both panel headings begin “Percentage of consumers concerned about”. |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: '5%', '13%', '82%' printed within their segments；gpt-5.6-sol: Values from “5%” to “82%” are centered inside coloured segments.；gemini-3.1-pro: percentage values are printed inside the colored segments |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `bold_run_inside_caption` | opus-5 | 3,4 | 'concerned about **fully autonomous robotaxi services** operating where they live' — bold run mid-sentence in the caption |
| `colored_figure_subtitle` | opus-5 | 3,4 | 'Addition of artificial intelligence in vehicle systems' set in green bold above the plot |
| `paired_unnumbered_charts_one_footnote` | opus-5 | 1,3 | two separate charts share one 'Q56.' / 'Sample size' block spanning both columns |
| `repeated_category_set_across_figures` | opus-5 | 3 | India, UK, US, Southeast Asia, Rep. of Korea, China, Japan, Germany appear as rows in all three figures |
| `paragraph_as_title` | gemini-3.1-pro | 4 | Titles are 2-sentence long paragraphs above charts |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 82 | India、Beneficial | Addition of artificial intelligence in vehicle systems、India、Beneficial | India、Beneficial | India、Beneficial | ✓ | ✓ | ✓ | 过 |
| 13 | India、Neutral | Addition of artificial intelligence in vehicle systems、India、Neutral | India、Neutral | India、Neutral | ✓ | ✓ | ✓ | 过 |
| 77 | China、Beneficial | Addition of artificial intelligence in vehicle systems、China、Beneficial | China、Beneficial | China、Beneficial | ✓ | ✓ | ✓ | 过 |
| 45 | US、Beneficial | Addition of artificial intelligence in vehicle systems、US、Beneficial | US、Beneficial | US、Beneficial | ✓ | ✓ | ✓ | 过 |
| 41 | Germany、Beneficial | Addition of artificial intelligence in vehicle systems、Germany、Beneficial | Germany、Beneficial | Germany、Beneficial | ✓ | ✓ | ✓ | 过 |
| 31 | UK、Neutral | Addition of artificial intelligence in vehicle systems、UK、Neutral | UK、Neutral | UK、Neutral | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f2` | "bar" | "stacked_bar" | "stacked_bar" | 三张图：两张并排的横向条形 + 一张百分比堆叠条 | 看页面。上半页是左右并排的两张独立横条图（各 8 条，各有自己的副标题），下半页是 8 行三段的堆叠条。opus 与 gemini 的三图切分对；gpt 把并排的两张合成了一张（16 个图元）。 |
| `density#f2` | "≤20" | "21–60" | "21–60" | ≤20（8 个图元） | 承上一条的三图切分：第二张是 8 条的横条图。gpt 的 21–60 来自它把两张并排的图合成了一张。 |
| `hardest_step` | 3 | 3 | 1 | 未裁决 · 无实测证据 | 这一页 6 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 3 / 1 都无法证伪。 |
| `key_roles#f1` | ["category"] | ["category", "panel"] | ["category", "panel"] | category（按标题切图） | 切图粒度的分歧，和 TRS241_Web_p88 同类。这一页没有图号，按标题切成三张图：两张并排的横向条形各自只需要「国家」一段键。gpt 与 gemini 把并排的两张当成一张图的两个面板，于是多一段 panel——两种读法对页面本身的描述完全相同。 |
| `key_roles#f2` | ["category"] | ["category", "series"] | ["category", "series"] | category（按标题切图） | 同上。第二张仍是横向条形，只需要国家一段；gpt 与 gemini 记的 series 来自把并排两张合成一张之后的「哪一张」。 |
