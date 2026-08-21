# VPEG6_SIV_Information_Memorandum__June_2025__p11

![VPEG6_SIV_Information_Memorandum__June_2025__p11](../../data/pages/VPEG6_SIV_Information_Memorandum__June_2025__p11.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `VPEG6_SIV_Information_Memorandum__June_2025__p11` | VPEG6_SIV_Information_Memorandum__June_2025_ | need_estimate | 5 | `parsebench/data/pages/VPEG6_SIV_Information_Memorandum__June_2025__p11.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 一页一图：无编号，标题分两层——蓝灰色副标题「Vantage has Generated Top Quartile Returns when Compared to Global Direct Private Equity Funds」在上，粗体图题「Vantage vs Global Private Equity (Direct Buyout Funds) TVPI - 2009-2018」在下。图形是 4 根细灰柱（Quartile 1–4），左轴只画 0.5x–3.0x 的水平网格线、刻度带「x」后缀，柱子无任何数值标签。叠加一条青色参考线横贯全幅（约 2.0x），线上 Quartile 1 处放一枚 VANTAGE 圆形图标标记。图例是左侧竖排一列，色块之一是品牌图标而非纯色方块。右上角黑底白字注释框压在绘图区内。下方两行 Source 小字。
> 
> **定位一个值难在哪**
> 取 Quartile 2 的 1.7：柱顶落在 1.5x 与 2.0x 网格之间，网格间距 0.5x，而 5% 容差只有 ±0.085x，必须按像素插值；图上无任何印刷数字，行标只有轴刻度「Quartile 2」和图例「GLOBAL PRIVATE EQUITY」。另一值 2.1 根本不在任何标记上，只写在黑框注释「a 2.1x platform wide Net Multiple」里，与画在 2.0x 的青线并不重合。
> 
> **不确定的**
> 柱子基线是否为 0（0.5x 以下未标刻度）无法确证；青线到底代表 2.0x 还是 2.1x 只能猜；图例图标的含义仅靠文字「VANTAGE」推断。

**gpt-5.6-sol**

> **画出来要什么**
> 需重建单面板复合图：四根灰色柱、青色水平参考线、带马形标志的黑色点、左侧图例、横向网格及右上黑底注释框。标题与副标题在图上方，来源说明在图下方。
> 
> **定位一个值难在哪**
> “Quartile 4 / GLOBAL PRIVATE EQUITY”的1.0未标在柱上；纵轴每0.5x一格，而其5%容差仅0.05，主要难在读数精度。
> 
> **不确定的**
> 青线视觉上落在2.0x刻度，但注释写“2.1x”；其究竟表示2.0x门槛还是VANTAGE的2.1x数值不完全明确。

**gemini-3.1-pro**

> ## 画出来要什么
> 生成器需要绘制一个带有4个分类（Quartile 1至4）的柱状图。Y轴刻度从0.5x开始至3.0x，间距为0.5x。主要的图表类型是柱状图，但其中混合了其他元素：需要在`Quartile 1`上为另一个序列（Vantage）单独绘制一个黑底白标的数据点；并且需要在Y轴的2.0x高度处绘制一条贯穿整个绘图区的粗青色参考线。此外，在黑色的数据点旁需要连接一个带有引导线的黑色标注框，其中包含两行说明文字。图例需要放置在Y轴刻度标签的左侧，这在常规布局中较为少见。
> 
> ## 定位一个值难在哪
> 定位Quartile 2的值（1.7）和Quartile 3的值（1.4）非常困难。因为这些值没有作为数据标签直接印在图表上，必须通过柱子顶端对齐Y轴来读取。而Y轴的网格线间距达到了0.5x，且柱子顶端悬空在网格线之间，单纯依靠视觉插值读取这几个非整数倍的数据点，很难将误差控制在5%的容差范围内。
> 
> ## 不确定的
> 2.0x处的粗青色参考线没有对应的图例或文字说明，不确定它是否代表行业阈值。包含“2.1x”值的标注框不仅是数据标签，还承担了结论解释的作用，解析器可能无法自动将其提取并关联到对应的数据单元格中。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | compound | 6 | — | above | none |
| gpt-5.6-sol | f1 | compound | 6 | — | above | some |
| gemini-3.1-pro | f1 | bar | 5 | — | above | some |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | ✓ | ✓ | opus-5: black box over the plot: 'Vantage has generated a 2.1x platform wide Net Multiple ... Direct Buyout'；gpt-5.6-sol: Black boxed callout over the upper-right plot begins “Vantage has generated a 2.1x platform wide Net Multiple”.；gemini-3.1-pro: black text box pointing to the Vantage marker |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: horizontal rules drawn at 0.5x through 3.0x, no vertical grid lines；gpt-5.6-sol: Horizontal rules run across each 0.5x level; no vertical gridlines are drawn.；gemini-3.1-pro: horizontal lines at 0.5x intervals, no vertical lines |
| `legend_beside_plot` | ✓ | ✓ | ✓ | opus-5: 'VANTAGE' and 'GLOBAL PRIVATE EQUITY' stacked in a left column level with the plot；gpt-5.6-sol: The VANTAGE and GLOBAL PRIVATE EQUITY legend is a column left of the plot.；gemini-3.1-pro: legend items are positioned to the far left of the y-axis |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: four grey bars plus a cyan horizontal line carrying a round icon marker at Quartile 1；gpt-5.6-sol: Four grey bars are overlaid by a cyan horizontal line and black circular Vantage marker.；gemini-3.1-pro: grey bars combined with a black point marker for VANTAGE |
| `reference_line` | ✓ | ✓ | ✓ | opus-5: a cyan horizontal rule spans the plot at the 2.0x gridline, legend entry 'VANTAGE'；gpt-5.6-sol: A cyan horizontal rule crosses the plot at the 2.0x gridline.；gemini-3.1-pro: thick cyan horizontal line at 2.0x across all categories |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Source: Based on global private equity returns on a Total Value Paid In basis from 2009-2018 ... Preqin.'；gpt-5.6-sol: “Source: Based on global private equity returns on a Total Value Paid In basis from 2009-2018” appears below.；gemini-3.1-pro: small print starting with 'Source: Based on global private equity...' |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: title ends 'TVPI - 2009-2018'; axis ticks are bare multiples '2.5x', '3.0x'；gpt-5.6-sol: “Vantage vs Global Private Equity (Direct Buyout Funds) TVPI - 2009-2018” places TVPI in the subtitle. |
| `value_label_outside` | — | ✓ | — | gpt-5.6-sol: “2.1x” appears in the black box, away from the Vantage marker. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `icon_legend_swatch` | opus-5 | 3 | the 'VANTAGE' legend key is a black circular brand icon, not a line or colour patch |
| `callout_carries_series_value` | opus-5 | 1,2,3 | the only number for the Vantage series, '2.1x', appears solely in the black annotation box |
| `marker_on_reference_line` | opus-5 | 3 | a circular icon sits on the cyan 2.0x line above Quartile 1, marking the Vantage position |
| `pictogram_data_marker` | gpt-5.6-sol | 3 | The Vantage horse logo is used as both legend swatch and plotted point. |
| `single_point_series` | gemini-3.1-pro | 1,3 | the VANTAGE series only plots one marker on Quartile 1 |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 2.1 | VANTAGE、Quartile 1 | VANTAGE、Vantage vs Global Private Equity (Direct Buyout Funds) TVPI - 2009-2018 | VANTAGE | Quartile 1、VANTAGE | ✗ | ✗ | ✓ | 没过 |
| 2.5 | GLOBAL PRIVATE EQUITY、Quartile 1 | Quartile 1、GLOBAL PRIVATE EQUITY | Quartile 1、GLOBAL PRIVATE EQUITY | Quartile 1、GLOBAL PRIVATE EQUITY | ✓ | ✓ | ✓ | 没过 |
| 1.7 | GLOBAL PRIVATE EQUITY、Quartile 2 | Quartile 2、GLOBAL PRIVATE EQUITY | Quartile 2、GLOBAL PRIVATE EQUITY | Quartile 2、GLOBAL PRIVATE EQUITY | ✓ | ✓ | ✓ | 没过 |
| 1.4 | GLOBAL PRIVATE EQUITY、Quartile 3 | Quartile 3、GLOBAL PRIVATE EQUITY | Quartile 3、GLOBAL PRIVATE EQUITY | Quartile 3、GLOBAL PRIVATE EQUITY | ✓ | ✓ | ✓ | 没过 |
| 1.0 | GLOBAL PRIVATE EQUITY、Quartile 4 | Quartile 4、GLOBAL PRIVATE EQUITY | Quartile 4、GLOBAL PRIVATE EQUITY | Quartile 4、GLOBAL PRIVATE EQUITY | ✓ | ✓ | ✓ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "compound" | "compound" | "bar" | compound | 按类型表自己的定义判：`compound` 是<strong>同一个面板里出现两种以上图元形状</strong>，所以决定它的是三家自己在 `components` 里记的 `mixed_marks`，不是它们给这张图起的名字。三家都记了 `mixed_marks` 与 `reference_line`，图元数 6 / 6 / 5。 |
| `printed#f1` | "none" | "some" | "some" | some | 三家描述的是同一张 5–6 个图元的图，只在「印了几个数」上分歧，gpt 与 gemini 都记 `some`。按同一标的上的两家一致判。 |
| `hardest_step` | 1 | 2 | 2 | 3 | 以实测为准：5 个点全败，4 个 row_missing（`GLOBAL PRIVATE EQUITY` 这一行整张表都没有）+ 1 个 value_absent。多数在第三步。三家报 1 / 2 / 2，无一命中；opus 的 1 明确不成立——这一页产出了表。 |
