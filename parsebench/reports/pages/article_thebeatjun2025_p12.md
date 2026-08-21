# article_thebeatjun2025_p12

![article_thebeatjun2025_p12](../../data/pages/article_thebeatjun2025_p12.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `article_thebeatjun2025_p12` | article_thebeatjun2025 | need_estimate | 5 | `parsebench/data/pages/article_thebeatjun2025_p12.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 一张满页幻灯片式版面:眉标 `TOP IDEAS`、大标题 `Overweight European High Yield Credit`、蓝色导语段,然后是无编号图表——粗体图题 `European HY Credit Offers the Highest Yield on USD-Hedged Basis` 加斜体副题 `Yield decomposition across major credit asset classes`。图本身是 5 类堆积柱,三个系列(Base Rate / Option-Adjusted Spread (OAS) / EURUSD 3m Hedging Income),图例横排在类别轴下方。关键在于:堆积段数不齐——`EM Hard Currency`、`USD High Yield`、`USD IG Corp` 只有两段,没有浅蓝对冲收益段;且柱顶只印合计 `8.1%`、`5.6%`,段内一个数字都不印。左轴 `0%`–`9%`,每 1% 一格,无网格线。
> 
> **定位一个值难在哪**
> 
> 以 `3.3%` 为例:它是 `EUR High Yield` 的 OAS 段,页面上没有这个数,必须读出该段下沿约 2.5% 与上沿约 5.8% 再相减。5% 容差只有 0.17 个百分点,而刻度间距是 1%,两个边界各自的读数误差就会吃掉容差。`2.3%` 更麻烦:`EUR High Yield` 与 `EUR IG Corp` 的浅蓝段高度相同,同一个数对应两个 mark。
> 
> **不确定的**
> 
> 没有图号,也没有独立的单位短语——单位只藏在轴刻度的百分号里。`2.3%` 究竟指哪一根柱无法判定;`4.4%` 与 `4.5%` 谁属 `USD High Yield`、谁属 `USD IG Corp`,只能靠像素高度猜。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 单面板竖向堆叠柱图：5个资产类别、3个图例系列、百分比轴；柱顶外置总收益标签，图例和长篇来源说明位于图下。标题须拆成主标题、斜体副标题和单位。
> 
> **定位一个值难在哪**
> 
> 以“EUR IG Corp”中“EURUSD 3m Hedging Income”的2.3%为例：段内没有数字，须按1个百分点刻度读取上下边界再相减；其±0.115个百分点容差很严。
> 
> **不确定的**
> 
> 2.3%未直接印出；两个欧元类别的青色对冲段视觉高度接近，其精确归属只能结合给定核查值判断。

**gemini-3.1-pro**

> **画出来要什么**
> 需要绘制一个无边框的堆叠柱状图。X轴为离散的分类类别，Y轴没有垂直实线，仅通过水平网格线标示刻度，刻度标签带有百分号（如 `9%`）。图例位于X轴下方。图表中的堆叠柱不在各分段内部标注数值，而是统一在每根柱子的顶端上方标注该柱的总和数值。底部需附带数据来源等小字注释。
> 
> **定位一个值难在哪**
> 以 EUR IG Corp 的 Base Rate 分段（对应值为 2.3%）为例。该数值未在图表中直接印出，必须通过观察它在Y轴上对应的高度来读取。然而Y轴刻度线间距高达 1%，凭肉眼和像素估算的难度极大，极易导致读取误差超过 5% 的容忍限度。
> 
> **不确定的**
> 由于缺乏具体分段的数值标注，所有非贴底的分段（如 Option-Adjusted Spread 所在的中间层）的上下边界都需要同时依靠视觉估算，其精确数值具有很强的不确定性，只能根据总和及其他已知成分进行近似推算。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 12 | — | above | some |
| gpt-5.6-sol | f1 | stacked_bar | 12 | — | above | some |
| gemini-3.1-pro | f1 | stacked_bar | 12 | — | above | some |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `hgrid_only` | — | — | ✓ | gemini-3.1-pro: horizontal grid lines at each percent, no vertical rules |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: legend row sits under the category tick labels: 'Base Rate', 'Option-Adjusted Spread (OAS)', 'EURUSD 3m Hedging Income'；gpt-5.6-sol: “Base Rate”, “Option-Adjusted Spread (OAS)” and “EURUSD 3m Hedging Income” sit below the x-axis.；gemini-3.1-pro: the three-item legend sits below the x-axis |
| `side_text_bullets` | ✓ | — | — | opus-5: blue intro paragraph above the chart: 'The reduction in global growth risks from the recent positive trade negotiation outcomes...' |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Source: Bloomberg, MSIM. As of May 22, 2025. For illustrative purposes only.' below the plot；gpt-5.6-sol: “Source: Bloomberg, MSIM. As of May 22, 2025.” appears below the figure.；gemini-3.1-pro: Source: Bloomberg... printed at the bottom of the page |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: each bar stacks Base Rate, OAS and hedging income; bar top equals the printed total；gpt-5.6-sol: Five vertical bars contain two or three coloured segments, with total height representing yield.；gemini-3.1-pro: bars are composed of up to three coloured segments |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: '8.1%', '7.9%', '7.6%', '5.6%', '5.4%' printed in bold above each bar top；gpt-5.6-sol: “8.1%”, “7.9%”, “7.6%”, “5.6%” and “5.4%” are printed above the stacks.；gemini-3.1-pro: total values are printed above the top of each bar |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `stack_total_label_only` | opus-5 | 2,3 | only the stack total ('8.1%') is printed; none of the three segments carries a number |
| `series_absent_in_some_stacks` | opus-5 | 3 | 'EM Hard Currency', 'USD High Yield', 'USD IG Corp' bars have no light-blue hedging segment at all |
| `duplicate_segment_heights_across_bars` | opus-5 | 2,3 | the hedging segment looks identical in height on 'EUR High Yield' and 'EUR IG Corp' |
| `unit_in_tick_labels` | gpt-5.6-sol | 2 | Every value tick includes “%”, from “0%” through “9%”; no separate axis title is drawn. |
| `stack_total_labels_only` | gpt-5.6-sol | 2,3 | Totals are printed above stacks, while none of the individual coloured segments carries a number. |
| `stacked_bar_total_label_only` | gemini-3.1-pro | 2,3 | only the total stack heights are printed above bars |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 2.5% | EUR High Yield、Base Rate | EUR High Yield、Base Rate | EUR High Yield、Base Rate | EUR IG Corp、EURUSD 3m Hedging Income | ✓ | ✓ | ✗ | 过 |
| 3.3% | EM Hard Currency、Option-Adjusted Spread (OAS) | EUR High Yield、Option-Adjusted Spread (OAS) | EM Hard Currency、Option-Adjusted Spread (OAS) | EM Hard Currency、Option-Adjusted Spread (OAS) | ✗ | ✓ | ✓ | 过 |
| 4.4% | USD High Yield、Base Rate | USD High Yield、Base Rate | USD High Yield、Base Rate | USD High Yield、Base Rate | ✓ | ✓ | ✓ | 过 |
| 2.3% | EUR IG Corp、EURUSD 3m Hedging Income | EUR IG Corp、EURUSD 3m Hedging Income | EUR IG Corp、EURUSD 3m Hedging Income | EUR IG Corp、Base Rate | ✓ | ✓ | ✗ | 过 |
| 4.5% | USD IG Corp、Base Rate | USD IG Corp、Base Rate | USD IG Corp、Base Rate | USD IG Corp、Base Rate | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
