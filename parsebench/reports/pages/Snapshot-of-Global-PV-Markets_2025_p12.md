# Snapshot-of-Global-PV-Markets_2025_p12

![Snapshot-of-Global-PV-Markets_2025_p12](../../data/pages/Snapshot-of-Global-PV-Markets_2025_p12.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `Snapshot-of-Global-PV-Markets_2025_p12` | Snapshot-of-Global-PV-Markets_2025 | need_estimate | 8 | `parsebench/data/pages/Snapshot-of-Global-PV-Markets_2025_p12.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 一个堆叠柱状图（FIGURE 4: SEGMENTATION OF PV INSTALLATION 2014-2024），11 个年度类别、2 个系列（ROOFTOP / UTILITY SCALE），图例在图下方一行。标题行与单位分离：`GWp` 单独写在左上角、位于 600 刻度之上，图号+标题在其右侧同一行。纵轴 0–600、每 100 一格，仅横向网格线，无任何数值标签。图下方有斜体 `Source: IEA PVPS, Becquerel Institute`。
> 
> **定位一个值难在哪**
> 
> 以 225 为例：它是 2024 年 ROOFTOP 段的高度。图上一个数字都没印，刻度间距 100 GWp，5% 容差只有 ±11 GWp，即约十分之一格；读数完全靠像素比对。更麻烦的是 375（2024 UTILITY SCALE），它是分段长度而非柱顶（柱顶约 600），需要先读总量再减去底段，任何解析器都得同时拿到两个未印出的数。
> 
> **不确定的**
> 
> 所有 8 个给定值均无印刷来源，段界位置只能目测；2018 与 2019 的柱高非常接近（约 103 与 113），无法确认哪一根对应 118 或 122；ROOFTOP 与 UTILITY SCALE 的棕/浅棕两色在小尺寸下区分度尚可，但薄段边界不清。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 需绘制2014—2024年双系列堆叠柱，左轴0—600 GWp、仅横向网格线；标题与单位置于图上方，图例和斜体来源置于图下方。
> 
> **定位一个值难在哪**
> 
> “2021”与“UTILITY SCALE”可定位93，但它是上层段，必须用堆叠顶端减去82对应的分界；100 GWp刻度难支持个位精度。
> 
> **不确定的**
> 
> 八个数值均未印在图上；只能依据柱边界读取，页面本身无法确认精确个位数。

**gemini-3.1-pro**

> ### 画出来要什么
> 一个单面板的堆叠柱状图，展示2014至2024年（横轴，分类时间序列）的ROOFTOP与UTILITY SCALE两类光伏装机量（系列，通过颜色区分，图例位于底部）。纵轴刻度为0到600，只有水平网格线，没有垂直网格线。特殊点在于，图表的标题居中，而单位“GWp”放置在标题同一行的最左侧、紧挨着左侧纵轴的上方。图表最下方有数据源“Source: IEA PVPS, Becquerel Institute”的斜体说明。
> 
> ### 定位一个值难在哪
> 以2024年UTILITY SCALE的值375为例，该数值本身并未在图表上标注。要在图表上定位它，需要依靠图例和横轴年份标签（`UTILITY SCALE`，`2024`）。但它是一个堆叠条形图的顶部段，纵轴刻度间隔大（每档100），读者需要目测柱子总高度（约600）并减去底部ROOFTOP的高度（约225）才能得出该值。肉眼估算读数的误差极大，完全无法保证5%的精度要求。
> 
> ### 不确定的
> 所有的值（如225, 375, 190等）在图上完全没有印刷出来，只能大致与柱体比例对应，可以确定这是生成图表的后台数据，但对于解析器或人类读者，只能给出粗略估值。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 22 | FIGURE 4 | above | none |
| gpt-5.6-sol | f1 | stacked_bar | 22 | FIGURE 4 | above | none |
| gemini-3.1-pro | f1 | stacked_bar | 22 | FIGURE 4: | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_title_above_axis` | ✓ | ✓ | ✓ | opus-5: `GWp` printed at top-left above the 600 tick, not alongside the axis；gpt-5.6-sol: “GWp” sits horizontally above the value-axis tick labels.；gemini-3.1-pro: GWp sits above the top tick of the y-axis |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: horizontal rules at 100...600 across the panel, no vertical rules；gpt-5.6-sol: Horizontal rules cross the plot at 0 through 600; no vertical grid lines are drawn.；gemini-3.1-pro: horizontal lines run across from the y-axis ticks, no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: `ROOFTOP` and `UTILITY SCALE` swatches in a row under the 2014-2024 tick row；gpt-5.6-sol: The “ROOFTOP” and “UTILITY SCALE” legend is centered below the time axis.；gemini-3.1-pro: ROOFTOP and UTILITY SCALE sit below the x-axis |
| `side_text_bullets` | ✓ | — | — | opus-5: body paragraph on utility scale sits directly above; heading `2 CUMULATIVE INSTALLED CAPACITY IN THE WORLD` below |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: italic line under the figure: `Source: IEA PVPS, Becquerel Institute`；gpt-5.6-sol: “Source: IEA PVPS, Becquerel Institute” appears below the legend.；gemini-3.1-pro: Source: IEA PVPS, Becquerel Institute below the legend |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: each year's bar has a dark brown lower segment and a tan upper segment；gpt-5.6-sol: Each yearly bar contains dark “ROOFTOP” and light “UTILITY SCALE” segments.；gemini-3.1-pro: bars are split vertically into two coloured segments |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: y ticks read 0,100,...600 bare; only `GWp` fixes the scale；gpt-5.6-sol: “GWp” is printed above the left value axis.；gemini-3.1-pro: GWp is placed beside the title above the axis |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `unit_label_left_of_title_line` | opus-5 | 3,4 | `GWp` and `FIGURE 4: SEGMENTATION OF PV INSTALLATION 2014-2024` share one line, unit at far left |
| `all_caps_series_names` | opus-5 | 3 | legend entries printed `ROOFTOP` and `UTILITY SCALE` in capitals |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 225 | 2024、ROOFTOP | 2024、ROOFTOP | 2024、ROOFTOP | ROOFTOP、2024 | ✓ | ✓ | ✓ | 过 |
| 375 | 2024、UTILITY SCALE | 2024、UTILITY SCALE | 2024、UTILITY SCALE | UTILITY SCALE、2024 | ✓ | ✓ | ✓ | 过 |
| 190 | 2023、ROOFTOP | 2023、ROOFTOP | 2023、ROOFTOP | ROOFTOP、2023 | ✓ | ✓ | ✓ | 过 |
| 265 | 2023、UTILITY SCALE | 2023、UTILITY SCALE | 2023、UTILITY SCALE | UTILITY SCALE、2023 | ✓ | ✓ | ✓ | 过 |
| 118 | 2022、ROOFTOP | 2022、ROOFTOP | 2022、ROOFTOP | ROOFTOP、2022 | ✓ | ✓ | ✓ | 过 |
| 122 | 2022、UTILITY SCALE | 2022、UTILITY SCALE | 2022、UTILITY SCALE | UTILITY SCALE、2022 | ✓ | ✓ | ✓ | 过 |
| 82 | 2021、ROOFTOP | 2021、ROOFTOP | 2021、ROOFTOP | ROOFTOP、2021 | ✓ | ✓ | ✓ | 过 |
| 93 | 2021、UTILITY SCALE | 2021、UTILITY SCALE | 2021、UTILITY SCALE | UTILITY SCALE、2021 | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
