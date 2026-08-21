# pwc-semiconductor-and-beyond-2026-full-report_p17

![pwc-semiconductor-and-beyond-2026-full-report_p17](../../data/pages/pwc-semiconductor-and-beyond-2026-full-report_p17.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `pwc-semiconductor-and-beyond-2026-full-report_p17` | pwc-semiconductor-and-beyond-2026-full-report | need_estimate | 10 | `parsebench/data/pages/pwc-semiconductor-and-beyond-2026-full-report_p17.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 一张两段堆叠柱：12 个时间槽（`'19` 到 `'30F`），灰色 `Conventional demand` 在下、橙色 `AI-driven demand` 在上，共 24 个分段，柱上不印数字。左轴 `0`–`180`，每 20 一格，只有横向网格线；单位不在轴上，而写在标题右侧同一行的 `(Unit: GW)`。图例在标题行右端、绘图区之上。绘图区内部还有一段加粗说明文字 `Rising AI data center power consumption signals growing AI compute demand and chipset needs`。柱顶之间另铺了一条淡橙色的包络填充带（不是数据系列，也没有图例）。整页右半为浅灰底，左半是与图并排的正文栏，底部 `Source: IEA, PwC analysis`。
> 
> **定位一个值难在哪**
> 
> `'19` 的 `AI-driven demand` 约为 1 GW：刻度间距 20 GW，这段橙色只有一两个像素高，5% 容差意味着 ±0.05 GW，肉眼与轴对读根本不可能；且柱上无任何数值标签。相比之下 `'28F` 的 62 与 `'25F` 的 62 同值不同系列，行必须同时带时间刻度与图例名两个标签才能唯一定位。
> 
> **不确定的**
> 
> 淡橙包络带是总量面积还是纯装饰，无法判断；`F` 是否代表 forecast 页面上没有说明；灰橙两段的精确分界（如 `'30F` 的 96）只能凭网格线估读。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 需重建左右分栏整页：左侧标题与正文，右侧为灰底复合图。图中有12期两段堆叠柱、连接相邻柱段边界的浅桃色带、顶部图例、水平网格、图内粗体说明及来源行；标题、单位分开存放。
> 
> **定位一个值难在哪**
> 
> “’19 / AI-driven demand / 1”虽由时间刻度和图例唯一定位，但橙色段仅为20 GW刻度间距的1/20；5%容差只有0.05 GW，无法可靠轴读。
> 
> **不确定的**
> 
> 浅桃色带未单列于图例，无法确认它是重复编码AI需求的数据标记还是装饰性连接；因此总标记数按24个柱段加1条色带估为25。

**gemini-3.1-pro**

> ## 画出来要什么
> 本页主体为一个带有背景填充带的堆叠柱状图。生成器需要能够绘制堆叠的柱子，并在柱子后方生成两层填充阴影带，分别平滑连接各年份柱子不同分类段的顶部。x轴的时间刻度需要支持非标准缩写格式（如 `'19`、`'30F`）。标题区需要在同一行展示主标题与单位后缀 `(Unit: GW)`，并在该行最右侧并排对齐展示图例。图表绘图区中心需要能够悬浮绘制多行解释性文本框（Callout）。此外，页面左侧需要留出专门的布局空间，以放置多段正文文本（旁侧文本排版）。
> 
> ## 定位一个值难在哪
> 以 `'22` 年的 `AI-driven demand` 值（11）为例。本页图表没有任何直接的数据标签，必须依靠左侧 y 轴进行估读。由于该分类处于堆叠柱的上层，读者需用顶部总值减去底部分类值才能得出结果。y 轴跨度为 180，每格刻度代表 20，要在这样的绝对尺度上肉眼读取出 11 并满足 5%（±0.55）以内的精确度要求，在视觉上是完全无法实现的。
> 
> ## 不确定的
> 图表中央浮动文本框的绝对坐标位置，以及背景阴影带连接方式的底层逻辑（贝塞尔曲线还是折线相连）无法完全确定。对大部分未落于主网格线上的数据，只能依靠比例进行粗略估算。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 24 | — | above | none |
| gpt-5.6-sol | f1 | compound | 25 | — | above | none |
| gemini-3.1-pro | f1 | stacked_bar | 24 | — | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | — | ✓ | opus-5: bold text over the plot: 'Rising AI data center power consumption signals growing AI compute demand and chipset needs'；gemini-3.1-pro: text starting with 'Rising AI...' is placed inside the plot |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: faint horizontal rules at 20, 40 ... 180; no vertical rules；gpt-5.6-sol: Horizontal grid lines cross the plot; no vertical grid lines are drawn.；gemini-3.1-pro: only horizontal lines span the plot area |
| `legend_above_plot` | ✓ | ✓ | ✓ | opus-5: 'AI-driven demand' / 'Conventional demand' swatches at top right, above the plot area；gpt-5.6-sol: The two-item legend sits above the plot at upper right.；gemini-3.1-pro: legend sits in the top right above the plot grid |
| `mixed_marks` | — | ✓ | — | gpt-5.6-sol: Stacked bars are overlaid on a pale peach filled band connecting years. |
| `nonstandard_time_ticks` | ✓ | ✓ | ✓ | opus-5: ticks read "'19", "'20" ... "'25F", "'30F"；gpt-5.6-sol: “’19” through “’24” and “’25F” through “’30F” label the time axis.；gemini-3.1-pro: years are abbreviated with apostrophes and letters like '19 and '30F |
| `panel_background` | ✓ | ✓ | — | opus-5: the whole right half including the plot area carries a light grey tint；gpt-5.6-sol: The plot and surrounding chart panel have a light grey fill. |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: three body paragraphs in a left column level with the chart on the right half；gpt-5.6-sol: Three prose paragraphs run in a left column beside the chart.；gemini-3.1-pro: a column of body text runs alongside the figure |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Source: IEA, PwC analysis' in small print under the plot；gpt-5.6-sol: “Source: IEA, PwC analysis” appears below the plot.；gemini-3.1-pro: Source: IEA, PwC analysis is below the x axis |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: grey segment below, orange segment above in each bar; bar length is the total；gpt-5.6-sol: Each year has a grey “Conventional demand” base topped by orange “AI-driven demand”.；gemini-3.1-pro: bars are divided into orange and grey segments |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: '(Unit: GW)' set beside the title; the left axis shows bare 0, 20 ... 180；gpt-5.6-sol: The heading includes “(Unit: GW)” beside the title.；gemini-3.1-pro: (Unit: GW) is written in the heading line beside the title |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `total_envelope_area_behind_bars` | opus-5 | 1,3 | pale orange fill spans between successive bar tops, behind the bars, with no legend entry |
| `forecast_suffix_in_tick_label` | opus-5 | 3 | ticks '25F ... '30F carry an F suffix to mark forecast years instead of a shaded band |
| `area_connector_between_stacks` | gpt-5.6-sol | 2 | A pale peach band connects segment bases and totals between adjacent stacked bars. |
| `unboxed_plot_annotation` | gpt-5.6-sol | 4 | Bold multiline explanatory text is placed over the plot without a box, arrow, or leader. |
| `page_section_title` | gpt-5.6-sol | 4 | “Faster, bigger, smarter data centers” heads the prose-and-chart page. |
| `connecting_band_behind_marks` | gemini-3.1-pro | — | shaded area links the tops of corresponding segments across bars |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 22 | '19、Conventional demand | '19、Conventional demand | ’19、Conventional demand | '19、Conventional demand | ✓ | ✓ | ✓ | 没过 |
| 1 | '19、AI-driven demand | '19、AI-driven demand | ’19、AI-driven demand | '19、AI-driven demand | ✓ | ✓ | ✓ | 没过 |
| 46 | '22、Conventional demand | '22、Conventional demand | ’22、Conventional demand | '22、Conventional demand | ✓ | ✓ | ✓ | 没过 |
| 11 | '22、AI-driven demand | '22、AI-driven demand | ’22、AI-driven demand | '22、AI-driven demand | ✓ | ✓ | ✓ | 没过 |
| 62 | '25F、Conventional demand | '25F、Conventional demand | ’25F、Conventional demand | '25、Conventional demand | ✓ | ✓ | ✓ | 没过 |
| 33 | '25F、AI-driven demand | '25F、AI-driven demand | ’25F、AI-driven demand | '25、AI-driven demand | ✓ | ✓ | ✓ | 没过 |
| 80 | '28F、Conventional demand | '28F、Conventional demand | ’28F、Conventional demand | '28、Conventional demand | ✓ | ✓ | ✓ | 没过 |
| 62 | '28F、AI-driven demand | '28F、AI-driven demand | ’28F、AI-driven demand | '28、AI-driven demand | ✓ | ✓ | ✓ | 没过 |
| 96 | '30F、Conventional demand | '30F、Conventional demand | ’30F、Conventional demand | '30F、Conventional demand | ✓ | ✓ | ✓ | 没过 |
| 68 | '30F、AI-driven demand | '30F、AI-driven demand | ’30F、AI-driven demand | '30F、AI-driven demand | ✓ | ✓ | ✓ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "stacked_bar" | "compound" | "stacked_bar" | stacked_bar | 按类型表自己的定义判：`compound` 是<strong>同一个面板里出现两种以上图元形状</strong>，所以决定它的是三家自己在 `components` 里记的 `mixed_marks`，不是它们给这张图起的名字。opus 与 gemini 都只记了 `stacked_bar`，没有 `mixed_marks`；只有 gpt 记了。两家一致，按 stacked_bar 判。 |
