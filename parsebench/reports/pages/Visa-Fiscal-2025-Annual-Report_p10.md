# Visa-Fiscal-2025-Annual-Report_p10

![Visa-Fiscal-2025-Annual-Report_p10](../../data/pages/Visa-Fiscal-2025-Annual-Report_p10.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `Visa-Fiscal-2025-Annual-Report_p10` | Visa-Fiscal-2025-Annual-Report | untagged | 10 | `parsebench/data/pages/Visa-Fiscal-2025-Annual-Report_p10.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 两张无编号的百分比堆叠柱图，各自坐在浅灰卡片里：标题加粗置顶（`Share of Visa ecommerce transactions by checkout type`、`Tokenized share of Visa ecommerce transactions`），7 个年份 2019–2025，每柱两段合计 100%，无数值轴、无网格、无基线刻度，所有数值以白色粗体印在色块内（上段贴顶、下段贴底）。系列名不是常规图例，而是绘图区左侧的两行文字，下方各画一条对应颜色的短横线（`Card-on-file & "button" checkout` / `Manual entry guest checkout`）。图下有斜体 Note 两三行，正文分栏在图侧并行，正文里带上标脚注 ⁹ ¹⁰。
> 
> **定位一个值难在哪**
> 
> `74%`：它同时是 f1 2022 年的 Card-on-file 段和 f2 2022 年的 Non-tokenized 段。要唯一定位必须凑齐「哪张图的标题 + 2022 + 系列名」三层；而系列名只由左侧带色下划线的文字给出，没有图例框，解析器很容易把它丢成孤立文本行，行列标签便对不上格。
> 
> **不确定的**
> 
> 灰底是整张卡片还是仅绘图区无法分辨；系列文字算图例还是内联标注只能凭下划线色块判断；两图均无 Figure 编号，是否在别处编号看不到。

**gpt-5.6-sol**

> ### 画出来要什么
> 页面需重建两张灰底、七年份的百分比堆叠柱图：双段等高柱、段内百分比、底部年份、左侧折行系列名及彩色连接线，并在图下排注释。图旁还与正文栏并排。
> 
> ### 定位一个值难在哪
> “74%”出现两次：上图是2022年“Card-on-file & “button” checkout”，下图是2022年“Non-tokenized transactions”。数值均已印出，难点是同时关联图题、年份和左侧系列标签。
> 
> ### 不确定的
> 两图均无编号、图例或数值轴；“%”只随数值出现，因此将其视为单位。左侧彩色横线按直接标签连接线理解，而非图例。

**gemini-3.1-pro**

> ### 画出来要什么
> 
> 要绘制此页面上的图表，生成器需要支持以下特性：
> - **百分比堆叠柱状图**：两张图的每年柱体等高，代表100%，内部分别展示构成比例。
> - **隐藏数值轴**：图表完全没有Y轴的基线、刻度或标签，依赖数据标记传递信息。
> - **内部数据标签**：所有的百分比数值（如`56%`、`84%`）均居中打印在各色块内部。
> - **引线图例（特殊内联标签）**：没有独立的图例区块。系列的名称（如`Manual entry guest checkout`）置于图表左侧，通过一条与色块同色的水平指示线连接到第一组（2019年）的对应数据段上。
> - **图表背景色**：绘图区带有浅灰色的背景填充。
> - **侧边文本排版**：页面为双栏布局，正文内容与图表共享同一水平空间。
> 
> ### 定位一个值难在哪
> 
> 以定位第一张图2025年的`16%`为例：
> 年份`2025`明确标在X轴上，数值`16%`直接印在柱体内，但该色块的系列名称`Manual entry guest checkout`仅通过指示线连接在远处的2019年首个数据段上。对于2025年的数据，解析器必须跨越横向空间，通过提取颜色匹配将其与左侧远处的系列名称强关联。如果解析器不能识别这种仅附着于首个数据点的特殊图例形式，会导致其余年份的数值丢失“系列”维度，在步骤3卡住。
> 
> ### 不确定的
> 
> 无。排版规整，数值与分类文本清晰可见，无模糊或需要猜测的内容。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 14 | — | above | all |
| opus-5 | f2 | stacked_bar | 14 | — | above | all |
| gpt-5.6-sol | f1 | stacked_bar | 14 | — | above | all |
| gpt-5.6-sol | f2 | stacked_bar | 14 | — | above | all |
| gemini-3.1-pro | f1 | stacked_bar | 14 | — | above | all |
| gemini-3.1-pro | f2 | stacked_bar | 14 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `footnote_marker` | ✓ | — | — | opus-5: "Visa ecommerce transactions.⁹" and footnotes "⁹ Among Visa processed card-not-present transactions." |
| `inline_series_labels` | — | ✓ | ✓ | gpt-5.6-sol: “Non-tokenized transactions” and “Tokenized transactions” sit directly left of the bars.；gemini-3.1-pro: series labels point to the 2019 segments with horizontal leader lines |
| `legend_beside_plot` | ✓ | — | — | opus-5: "Non-tokenized transactions" / "Tokenized transactions" stacked left of the bars |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: two separately titled charts with their own Note lines on one page；gpt-5.6-sol: Two independent titled charts appear: “Share of Visa…” and “Tokenized share…”.；gemini-3.1-pro: there are two distinct, captioned figures on the page |
| `no_value_axis` | ✓ | ✓ | ✓ | opus-5: left side carries only series names, no value ticks；gpt-5.6-sol: No value ticks or y-axis are drawn; percentages are printed inside segments.；gemini-3.1-pro: there is no vertical y-axis line, ticks, or labels |
| `panel_background` | ✓ | ✓ | ✓ | opus-5: grey tint behind the plot area and note, white page around it；gpt-5.6-sol: The title, bars and note sit on a light-grey rectangular background.；gemini-3.1-pro: the chart area features a light gray background fill |
| `pct_stacked` | ✓ | ✓ | ✓ | opus-5: 96%+4% ... 46%+54%, every bar drawn to the same top；gpt-5.6-sol: Every yearly stack has equal height; paired percentage labels sum to 100%.；gemini-3.1-pro: bars are uniform height and segment values sum to 100 per column |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: body column "Farewell, guest checkout ..." runs left of f1; text column right of f2；gpt-5.6-sol: Running prose sits left of f1 and in a column to the right of f2.；gemini-3.1-pro: columns of body text run alongside the charts in a 2-column layout |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: "Note: Reflects Visa processed transactions... Excludes Russia, China and Visa Direct in Peru."；gpt-5.6-sol: “Note: Reflects Visa processed transactions, among card-not-present approved transactions.” appears below.；gemini-3.1-pro: Note: Reflects Visa processed transactions... |
| `stacked_bar` | ✓ | ✓ | — | opus-5: each 2019-2025 bar split into Tokenized and Non-tokenized segments；gpt-5.6-sol: Each year is one bar split into tokenized and non-tokenized stacked segments. |
| `thin_segment_label` | — | ✓ | — | gpt-5.6-sol: The white “4%” label is squeezed into the thin 2019 tokenized segment. |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: "96%" and "4%" printed within the two segments of the 2019 bar；gpt-5.6-sol: All percentages are printed inside their segments, including “4%” in the thinnest segment.；gemini-3.1-pro: percentages like 56% are written centrally inside the segments |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `legend_underline_swatch` | opus-5 | 3 | series names carry a short coloured rule underneath instead of a square swatch |
| `figure_card_background` | opus-5 | 4 | title, plot and note all enclosed in one grey rounded card block |
| `unnumbered_titled_figure` | opus-5 | 3,4 | both charts have bold titles but no "Figure n" label anywhere |
| `inline_label_connector_rules` | gpt-5.6-sol | 3 | Blue horizontal rules connect the two left-side series labels to their stack boundaries. |
| `inline_label_connector_rules` | gpt-5.6-sol | 3 | Blue horizontal rules connect the two left-side series labels to their stack boundaries. |
| `legend_via_first_mark_annotation` | gemini-3.1-pro | 3 | series labels connect only to the 2019 segments via leader lines |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 56% | Card-on-file & button checkout、2019 | Share of Visa ecommerce transactions by checkout type、2019、Card-on-file & "button" checkout | 2019、Card-on-file & “button” checkout | 2019、Card-on-file & “button” checkout | ✓ | ✓ | ✓ | 过 |
| 16% | Manual entry guest checkout、2025 | Share of Visa ecommerce transactions by checkout type、2025、Manual entry guest checkout | 2025、Manual entry guest checkout | 2025、Manual entry guest checkout | ✓ | ✓ | ✓ | 过 |
| 74% | Card-on-file & button checkout、2022 | Share of Visa ecommerce transactions by checkout type、2022、Card-on-file & "button" checkout | 2022、Card-on-file & “button” checkout | 2022、Card-on-file & “button” checkout | ✓ | ✓ | ✓ | 过 |
| 24% | Manual entry guest checkout、2023 | Share of Visa ecommerce transactions by checkout type、2023、Manual entry guest checkout | 2023、Manual entry guest checkout | 2023、Manual entry guest checkout | ✓ | ✓ | ✓ | 过 |
| 81% | Card-on-file & button checkout、2024 | Share of Visa ecommerce transactions by checkout type、2024、Card-on-file & "button" checkout | 2024、Card-on-file & “button” checkout | 2024、Card-on-file & “button” checkout | ✓ | ✓ | ✓ | 过 |
| 4% | Tokenized transactions、2019 | Tokenized share of Visa ecommerce transactions、2019、Tokenized transactions | 2019、Tokenized transactions | 2019、Tokenized transactions | ✓ | ✓ | ✓ | 过 |
| 54% | Tokenized transactions、2025 | Tokenized share of Visa ecommerce transactions、2025、Tokenized transactions | 2025、Tokenized transactions | 2025、Tokenized transactions | ✓ | ✓ | ✓ | 过 |
| 74% | Non-tokenized transactions、2022 | Tokenized share of Visa ecommerce transactions、2022、Non-tokenized transactions | 2022、Non-tokenized transactions | 2022、Non-tokenized transactions | ✓ | ✓ | ✓ | 过 |
| 93% | Non-tokenized transactions、2020 | Tokenized share of Visa ecommerce transactions、2020、Non-tokenized transactions | 2020、Non-tokenized transactions | 2020、Non-tokenized transactions | ✓ | ✓ | ✓ | 过 |
| 36% | Tokenized transactions、2023 | Tokenized share of Visa ecommerce transactions、2023、Tokenized transactions | 2023、Tokenized transactions | 2023、Tokenized transactions | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
