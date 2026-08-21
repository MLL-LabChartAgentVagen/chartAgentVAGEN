# Digital_News-Report_2022_p50

![Digital_News-Report_2022_p50](../../data/pages/Digital_News-Report_2022_p50.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `Digital_News-Report_2022_p50` | Digital_News-Report_2022 | untagged | 4 | `parsebench/data/pages/Digital_News-Report_2022_p50.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 单张百分比堆叠柱图：6 个国家 × 4 个分段 = 24 段，左轴刻度 `0%`、`25%`、`50%`、`75%`、`100%`，无网格线。每段内部印白色（灰段为深色）粗体数值，包括 Finland 顶部仅 5 个百分点的窄段。图例在图下方两行四项，与柱段仅靠颜色对应。全大写两行标题 `PROPORTION WHO PAY MOST ATTENTION TO NEWS BRANDS VERSUS JOURNALISTS – SELECTED MARKETS`，无图号；下方注释含题号与逐国样本量 `Base: Finland = 2064, Germany = 2002...`。整图还需与左栏正文并排，共享同一横向版面带。
> 
> ## 定位一个值难在哪
> `21` 在同一图上出现两次：USA 的橙色 `Specific journalists or commentators` 段，以及 France 的青色 `Specific news brands` 段。数值虽已印出、无需读轴，但要唯一定位必须同时拿到国家刻度名与图例名，而图例名只能通过颜色回溯——解析器若只抓到孤立的 “21”，行标签就落不到正确单元格上。
> 
> ## 不确定的
> 标题第二行是否算副标题（我按整体换行处理，subtitle 留空）；图内是否有极浅的水平网格线，150 dpi 下看不出；Finland 的 `5` 与 Brazil 的 `7` 标签是否真的溢出窄段，边界难判。

**gpt-5.6-sol**

> ### 画出来要什么
> 单幅六国、四系列的100%堆叠柱图；每段内印数值，左轴为0%至100%，图例、调查题及样本量置于图下。
> 
> ### 定位一个值难在哪
> “46”需同时关联“Brazil”和“Specific journalists or commentators”；虽可直接读数，但页面没有数据表承载这组键。
> 
> ### 不确定的
> 图表没有编号。25%间隔的浅色横网格在缩放图中较淡，部分线条可见性存在判断余地。

**gemini-3.1-pro**

> ### 画出来要什么
> 生成器需要支持百分比堆积柱状图（100% stacked bar），能够在各段内部居中显示无单位的数据值标签（如 `69`、`21` 等）。纵轴的刻度需要支持自带百分号格式（如 `25%`、`50%`）。图表下方需要能够绘制分为两行两列的长文本图例，最底部还需支持多行独立说明文本（source/note）。
> 
> ### 定位一个值难在哪
> 以定位 `46` 为例，该值代表巴西（Brazil）中“Specific journalists or commentators”的比例。提取难点在于：图例标签文本较长，且分为 2x2 网格直接放置在 X 轴标签下方。解析器进行文本分块时，容易将图例文本与紧邻的分类坐标轴文本混淆。此外，需要依赖颜色特征将图例和堆积块正确映射（橘色方块），这在非结构化图像解析时容易丢失层级信息。
> 
> ### 不确定的
> 虽然纵轴明确标示为 `100%` 且图表按百分比堆积拉齐，但个别柱子的内部数值加总并非绝对的 100（例如芬兰 69+7+20+5=101，可能是由于四舍五入导致的），系统若强制校验 `100%` 可能会误报错。另外，上方的文本“NEWS BRANDS OR JOURNALISTS?”和正文段落样式相似，且紧跟着图表的全大写标题，图表标题归属的确切边界会有判定不确定性。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 24 | — | above | all |
| gpt-5.6-sol | f1 | stacked_bar | 24 | — | above | all |
| gemini-3.1-pro | f1 | stacked_bar | 24 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `hgrid_only` | — | ✓ | ✓ | gpt-5.6-sol: Faint horizontal rules align with percentage ticks; no vertical grid lines are drawn.；gemini-3.1-pro: horizontal grid lines appear at 25%, 50%, and 75% |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: four legend keys in two rows under the category axis, starting `Specific news brands`；gpt-5.6-sol: The four-item legend is arranged in two rows directly below the bars.；gemini-3.1-pro: a 2x2 legend sits below the country names on the x-axis |
| `pct_stacked` | ✓ | ✓ | ✓ | opus-5: every bar reaches the `100%` tick; segments per country sum to 100；gpt-5.6-sol: All six stacks reach 100%; left ticks run from “0%” to “100%”.；gemini-3.1-pro: all bars reach exactly the 100% line on the y-axis |
| `side_text_bullets` | ✓ | ✓ | — | opus-5: left column body text runs level with the figure in the right column；gpt-5.6-sol: A long body-text column runs left of the chart at the same page height. |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: `Q_Journalists_1. When looking for news online... Base: Finland = 2064, Germany = 2002...`；gpt-5.6-sol: “Q_Journalists_1.” and country “Base” counts appear beneath the legend.；gemini-3.1-pro: small text beginning with 'Q_Journalists_1.' is printed at the very bottom |
| `stacked_bar` | ✓ | ✓ | — | opus-5: each country bar is built of four coloured segments, e.g. Germany 45/12/28/15；gpt-5.6-sol: Each country is one bar divided into four coloured segments. |
| `thin_segment_label` | ✓ | — | — | opus-5: Finland's top magenta band is 5 points tall and the `5` label nearly fills it |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: `69`, `7`, `20`, `5` printed inside the Finland segments；gpt-5.6-sol: All 24 numbers are printed in white inside their coloured segments.；gemini-3.1-pro: numbers like 69, 45, 37 are printed inside the colored bar segments |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `per_category_base_note` | opus-5 | 4 | note lists a sample size per country: `Base: Finland = 2064, Germany = 2002, UK = 2410, USA = 2036...` |
| `question_id_in_note` | opus-5 | 4 | note opens with survey item code in bold: `Q_Journalists_1.` before the question wording |
| `figure_without_number` | opus-5 | 3,4 | all-caps heading with no `Figure n`; chapter number `2.5` belongs to the section title |
| `tick_labels_carry_unit` | gemini-3.1-pro | 2 | y-axis ticks read 0%, 25%, 50% while values inside bars are bare numbers |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 69 | Finland、Specific news brands | Finland、Specific news brands | Finland、Specific news brands | Finland、Specific news brands | ✓ | ✓ | ✓ | 过 |
| 21 | USA、Specific journalists or commentators | USA、Specific journalists or commentators | France、Specific news brands | USA、Specific journalists or commentators | ✓ | ✗ | ✓ | 过 |
| 46 | Brazil、Specific journalists or commentators | Brazil、Specific journalists or commentators | Brazil、Specific journalists or commentators | Brazil、Specific journalists or commentators | ✓ | ✓ | ✓ | 过 |
| 24 | France、I don't use online news | France、I don't use online news | France、I don’t use online news | France、I don't use online news | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 3 | 1 | 3 | 未裁决 · 无实测证据 | 这一页 4 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 1 / 3 都无法证伪。 |
