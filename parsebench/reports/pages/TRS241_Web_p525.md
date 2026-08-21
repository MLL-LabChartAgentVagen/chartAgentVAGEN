# TRS241_Web_p525

![TRS241_Web_p525](../../data/pages/TRS241_Web_p525.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `TRS241_Web_p525` | TRS241_Web | need_estimate | 10 | `parsebench/data/pages/TRS241_Web_p525.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 一张手绘风格的折线图：同一侧叠放两条数值刻度轴——顶端分别标 `$/lb`（0…60）与 `$/kg`（20…120），二者共用同一条零线，只是单位换算；竖排轴标题 `Price in US $ per kg/lb U3O8`；x 轴 1968–1983 年份约 45° 斜排。两条序列靠线型区分：实线 `current dollars` 用引线标注，虚线由带箭头的框外注记 `Constant 1980 dollars (based on US GNP deflator)` 指入图内。图末（1983 之后）另悬四个无图例的点标记（◇ 与 ⊕），1968 处各一个。全图点线交叉的虚实网格，图号与标题在图下：`FIG.F.3. Uranium transaction values.`
> 
> **定位一个值难在哪**
> 取 1982 年的 `Constant 1980 dollars`≈21：该点无数字标注，虚线在此与实线几乎贴合；网格每 10 $/lb 一格，5% 容差只有约 1 $/lb，需在格内四分之一处目测；且同一像素高度在 `$/kg` 轴上读作 ≈46，行键必须写明读的是哪条刻度。
> 
> **不确定的**
> ◇ 与 ⊕ 两种标记代表什么（现货？合同？）页面未说明；1983 之后的点属于哪一年无刻度；95 究竟对应 1978 还是 1979（两点等高）无法分辨；页面无数据表可核对。

**gpt-5.6-sol**

> **画出来要什么**
> 需重建单面板双折线、逐年旋转刻度、纵横点状网格、虚实线型及圆形/菱形端点。图注置于图下。左侧同时绘制“$ / lb”0–60与“$ / kg”0–120换算刻度，系列名以引线直接标在线内。
> 
> **定位一个值难在哪**
> 例如1980年“95”并非印在标记上，而要从“$ / kg”刻度读取；两条线又在该年重合，必须同时给出年份、系列和单位。
> 
> **不确定的**
> 折线末端在“1983”附近似有同年多个观测，但没有更细时间标签。部分给定值只能按刻度近似匹配，端点数量估为34。

**gemini-3.1-pro**

> ### 画出来要什么
> 本页包含一个折线图，其主要挑战在于同一侧绘制了**双重刻度轴**。左侧Y轴同时显示了外侧的`$/lb`和内侧的`$/kg`两个完全不同的数值比例，并且图表的水平网格线仅与外侧的`$/lb`刻度对齐。图表没有传统的独立图例，而是通过带箭头的**引导线（callout）**将文本直接指向对应折线。X轴年份标签采用了倾斜显示。此外，在1968年和1983年的部分数据点上绘制了特殊的标记符号（如菱形和带十字的圆圈）。
> 
> ### 定位一个值难在哪
> 定位如 **95** 这样的值非常困难。该值属于1978年和1979年的`current dollars`系列，需要对照内侧的 `$/kg` 轴读取。由于内侧轴的刻度与图表上的水平网格线并不对应，且数据点距离左侧轴较远，视觉上很难将数据点准确水平对齐到内侧无网格线辅助的相应位置，读取误差极易超过5%的容忍度。
> 
> ### 不确定的
> 图中折线在1968年和1983年的起止数据点上标有特殊的符号，但不清楚这些符号是否仅作装饰，还是代表具有额外语义的数据（例如标注实际交易数据点或特殊基准点），因为图表中没有给出相关说明。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 36 | FIG.F.3. | below | none |
| gpt-5.6-sol | f1 | line | 34 | FIG.F.3. | below | none |
| gemini-3.1-pro | f1 | line | 32 | FIG.F.3. | below | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | — | ✓ | opus-5: 'Constant 1980 dollars (based on US GNP deflator)' with a long arrow drawn down onto the dashed line；gemini-3.1-pro: labels like 'current dollars' point directly to the lines |
| `axis_title_above_axis` | ✓ | — | ✓ | opus-5: '$/lb' and '$/kg' printed above the 60 and 120 ticks, not beside the axis；gemini-3.1-pro: $/lb and $/kg are written directly above the y-axis ticks |
| `dashed_line_series` | ✓ | ✓ | ✓ | opus-5: one series drawn dashed, the other a heavy solid line; both black；gpt-5.6-sol: “Constant 1980 dollars” is dashed, while “current dollars” is solid.；gemini-3.1-pro: the Constant 1980 dollars series is drawn as a dashed line |
| `inline_series_labels` | ✓ | ✓ | — | opus-5: 'current dollars' written inside the plot with a leader line to the solid line; no legend box；gpt-5.6-sol: “current dollars” and “Constant 1980 dollars” are written beside their lines. |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Price in US $ per kg/lb U3O8' set vertically along the left edge；gpt-5.6-sol: “Price in US $ per kg/lb U₃O₈” runs vertically beside the plot.；gemini-3.1-pro: the main left axis title is rotated 90 degrees |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: '1968' ... '1983' set at roughly 45 degrees under the axis；gpt-5.6-sol: Year labels “1968” through “1983” are angled beneath the plot.；gemini-3.1-pro: years from 1968 to 1983 are slanted on the bottom axis |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: scale words live only in '$/lb', '$/kg' and the rotated 'Price in US $ per kg/lb U3O8'；gpt-5.6-sol: The axis title reads “Price in US $ per kg/lb U₃O₈”.；gemini-3.1-pro: the main axis title specifies 'Price in US $ per kg/lb' |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `twin_same_side_unit_conversion_axes` | opus-5 | 2,3 | two left value axes, '$/lb' 0-60 and '$/kg' 20-120, same data, one converted scale |
| `off_axis_endpoint_markers` | opus-5 | 3 | diamond and circled-plus markers plotted at 1968 and to the right of the 1983 tick, unlabelled |
| `full_dotted_grid_both_directions` | opus-5 | — | dotted horizontal and vertical grid lines cross over the whole plot area |
| `marker_shape_only_series` | opus-5 | 3 | ◇ and ⊕ glyphs carry meaning but no legend or text names them anywhere on the page |
| `same_side_dual_unit_scale` | gpt-5.6-sol | 2,3 | Two left tick columns show 0–60 “$ / lb” and 0–120 “$ / kg”. |
| `intraperiod_multiple_points` | gpt-5.6-sol | 3 | Each line appears to have two late vertices around the single “1983” tick. |
| `series_specific_endpoint_markers` | gpt-5.6-sol | 3 | Dashed-line endpoints use circles; solid-line endpoints use diamonds. |
| `dual_scale_same_side` | gemini-3.1-pro | 2,3 | left y-axis has two different scales ($/lb and $/kg) printed side-by-side |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 7 | 1968、current dollars | current dollars、1968、$/lb | 1972、current dollars、$ / lb | current dollars、1973、$/lb | ✓ | ✗ | ✗ | 过 |
| 16 | 1975、current dollars | current dollars、1975、$/lb | 1975、current dollars、$ / lb | current dollars、1973、$/kg | ✓ | ✓ | ✗ | 没过 |
| 43 | 1978、current dollars | current dollars、1978、$/lb | 1980、current dollars、$ / lb | current dollars、1978、$/lb | ✓ | ✗ | ✓ | 过 |
| 22 | 1982、current dollars | current dollars、1982、$/lb | 1974、Constant 1980 dollars (based on US GNP deflator)、$ / kg | Constant 1980 dollars (based on US GNP deflator)、1973、$/kg | ✓ | ✗ | ✗ | 没过 |
| 12 | 1970、Constant 1980 dollars (based on US GNP deflator) | Constant 1980 dollars (based on US GNP deflator)、1983、$/lb | 1970、Constant 1980 dollars (based on US GNP deflator)、$ / lb | current dollars、1974、$/lb | ✗ | ✓ | ✗ | 过 |
| 21 | 1975、Constant 1980 dollars (based on US GNP deflator) | Constant 1980 dollars (based on US GNP deflator)、1982、$/lb | 1975、Constant 1980 dollars (based on US GNP deflator)、$ / lb | Constant 1980 dollars (based on US GNP deflator)、1983、$/lb | ✗ | ✓ | ✗ | 过 |
| 50 | 1978、Constant 1980 dollars (based on US GNP deflator) | Constant 1980 dollars (based on US GNP deflator)、1977、$/lb | 1982、current dollars、$ / kg | Constant 1980 dollars (based on US GNP deflator)、1978、$/lb | ✗ | ✗ | ✓ | 过 |
| 17 | 1983、Constant 1980 dollars (based on US GNP deflator) | current dollars、1983、$/lb | 1974、current dollars、$ / kg | current dollars、1982、$/lb | ✗ | ✗ | ✗ | 没过 |
| 95 | 1978、current dollars | current dollars、1978、$/kg | 1980、current dollars、$ / kg | current dollars、1978、$/kg | ✓ | ✗ | ✓ | 没过 |
| 95 | 1980、Constant 1980 dollars (based on US GNP deflator) | current dollars、1979、$/kg | 1980、Constant 1980 dollars (based on US GNP deflator)、$ / kg | current dollars、1979、$/kg | ✗ | ✓ | ✗ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 2 | 1 | 2 | 2 | 以实测为准：10 个点过 5 个，5 个失败里 4 个是 value_off（其中两个相对误差 53%、55%），1 个是 label_unlinked（第三步）。多数在第二步。opus 与 gemini 报 2，命中；gpt 报 1 不成立——这一页有表。 |
| `key_roles#f1` | ["series", "time"] | ["series", "time"] | ["category", "series", "time"] | series × time | opus 与 gpt 一致。gemini 多记的 category 例子是 `$/lb`——那是量纲，不是键的一段。 |
