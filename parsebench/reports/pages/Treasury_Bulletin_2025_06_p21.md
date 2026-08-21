# Treasury_Bulletin_2025_06_p21

![Treasury_Bulletin_2025_06_p21](../../data/pages/Treasury_Bulletin_2025_06_p21.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `Treasury_Bulletin_2025_06_p21` | Treasury_Bulletin_2025_06 | need_estimate | 8 | `parsebench/data/pages/Treasury_Bulletin_2025_06_p21.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一页两张独立图表。上图 CHART FFO-A：四条平滑无标记的折线（无数据点标记），左值轴 0.0–700.0（一位小数刻度、只有横向网格），横轴为 13 个裸月份缩写 Mar…Mar（首尾同名，跨两个财年），图例排在绘图区右侧成一列。下图 CHART FFO-B：7 组双色柱（2024/2025），轴 0–1200 步长 150，类别标签换行成最多四行（"Social insurance and retirement receipts"），图例在图下方，注记 "*Prior-year data are for the comparable year" 位于轴标签与图例之间。标题块须拆成编号行 "CHART FFO-A.—"、标题行与单位行 "(In billions of dollars)"。
> 
> ## 定位一个值难在哪
> 取 140：它落在 FFO-A 最右端 Mar 的 Off-budget outlays 上。图上无任何数字，网格间距 100，而 5% 容差只有 ±7；同一区域 Off-budget receipts 与 outlays 两条线在 90–140 间互相缠绕，且横轴两端都写 "Mar"，行标签 "Off-budget outlays / Mar" 无法唯一定位。
> 
> ## 不确定的
> 90 与 140 归属哪条线只能按曲线走向猜；35 可能是 Excise taxes 也可能是 Custom duties 的 2024 柱，两者都在 30–45 之间。FFO-B 没有任何单位文字，是否也是十亿美元只能推测。

**gpt-5.6-sol**

> **画出来要什么**：页面含两幅独立图：四条平滑月度曲线，图例置右；两年份分组柱图，图例和脚注置于下方。两图仅有水平网格线，第二图需支持多行类别标签。
> 
> **定位一个值难在哪**：`Custom duties`的`2024`值35没有印出，而纵轴每150一格；5%容差仅1.75，无法可靠精确估读。曲线图末端140还需把重复的`Mar`解释为2025年。
> 
> **不确定的**：所有目标数均由坐标轴估读。90按`Aug`的`Off-budget receipts`判断；第二图没有写明金额单位。

**gemini-3.1-pro**

> ### 画出来要什么
> 本页包含两张图表（FFO-A和FFO-B）。
> 生成器需要能够绘制：
> 1. **平滑折线图**：不带独立数据点标记的多系列折线图（使用了样条曲线插值），图例位于图表右侧，带有主标题和位于其下方作括号说明的单位文本。
> 2. **分组柱状图**：支持长分类标签的自动换行或多行文本对齐（如“Social insurance and retirement receipts”被分为四行展示），图例位于下方。
> 3. **独立脚注文本**：在分类轴右下角、图例上方能够悬浮添加独立注释说明（如带有星号的Prior-year说明）。
> 4. **共享网格线样式**：两张图都仅包含水平网格线，无垂直网格线。
> 
> ### 定位一个值难在哪
> 基于值 `1140`（FFO-B中2025年的“Individual income taxes”）。该柱状图的Y轴刻度间隔高达150，且没有印制具体数值。读者必须通过视觉估算柱子顶部在1050和1200之间的确切位置。要以5%的容错率（即误差在±57以内）在如此宽泛的网格间距中准确读出1140非常困难。
> 
> ### 不确定的
> 对于FFO-A中的折线图，由于采用了平滑曲线（spline）且没有垂直网格线辅助，无法确定每个类目（月份）对应的数据点是仅落在X轴的刻度处，还是包含了更高频率的采样。部分波峰或波谷是否恰好发生在月份刻度上也难以肉眼断定。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 52 | CHART FFO-A.— | above | none |
| opus-5 | f2 | grouped_bar | 14 | CHART FFO-B.— | above | none |
| gpt-5.6-sol | f1 | line | 52 | CHART FFO-A.— | above | none |
| gpt-5.6-sol | f2 | grouped_bar | 14 | CHART FFO-B.— | above | none |
| gemini-3.1-pro | f1 | line | 52 | CHART FFO-A.— | above | none |
| gemini-3.1-pro | f2 | grouped_bar | 14 | CHART FFO-B.— | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `grouped_bar` | ✓ | ✓ | — | opus-5: Blue and red bars side by side in each of seven category slots；gpt-5.6-sol: Blue and red bars stand side by side within each source category. |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: Horizontal rules at 150 intervals; no vertical rules；gpt-5.6-sol: Horizontal rules align with value ticks; no vertical grid lines are drawn.；gemini-3.1-pro: both charts have horizontal rules across the panel, no vertical ones |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: '2024  2025' swatches centred below the category labels and note；gpt-5.6-sol: The “2024” and “2025” legend is centered below the category labels.；gemini-3.1-pro: the legend for 2024 and 2025 sits below the x-axis |
| `legend_beside_plot` | ✓ | ✓ | ✓ | opus-5: Four legend entries in a right-hand column level with the plot, each with a colour rule；gpt-5.6-sol: Four series labels and line samples form a column right of the plot.；gemini-3.1-pro: the legend is a column on the right side of the plot |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: Two captioned charts, 'CHART FFO-A.—' and 'CHART FFO-B.—', stacked on one page；gpt-5.6-sol: Separate headings “CHART FFO-A.—” and “CHART FFO-B.—” identify two figures.；gemini-3.1-pro: there are two charts, CHART FFO-A and CHART FFO-B, on one page |
| `nonstandard_time_ticks` | ✓ | — | — | opus-5: Ticks read 'Mar Apr May Jun ... Feb Mar' with no year attached |
| `source_note_lines` | ✓ | ✓ | — | opus-5: '*Prior-year data are for the comparable year' printed under the category axis；gpt-5.6-sol: “*Prior-year data are for the comparable year” appears below the plot. |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: '(In billions of dollars)' under the title; y axis shows bare 0.0 ... 700.0；gpt-5.6-sol: “(In billions of dollars)” is printed directly below the title.；gemini-3.1-pro: the phrase '(In billions of dollars)' sits directly under the title |
| `wrapped_category_labels` | ✓ | ✓ | ✓ | opus-5: 'Social insurance and retirement receipts' wraps onto four lines under the axis；gpt-5.6-sol: “Social insurance and retirement receipts” wraps across four lines.；gemini-3.1-pro: x-axis labels like 'Individual income taxes' wrap onto three or four lines |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `repeated_time_tick_ambiguity` | opus-5 | 3 | 'Mar' appears as both the first and last tick, spanning two fiscal years |
| `smoothed_line_no_markers` | opus-5 | 2 | All four series drawn as smoothed splines with no point markers at the month ticks |
| `decimal_tick_labels` | opus-5 | 2 | Y ticks printed '0.0, 100.0, ... 700.0' with a trailing decimal on whole hundreds |
| `unit_absent_on_figure` | opus-5 | 4 | No unit phrase anywhere; axis reads bare 0 ... 1200 and title names no scale |
| `smoothed_line_series` | gpt-5.6-sol | 2 | All four monthly lines curve smoothly between tick positions rather than using straight segments. |
| `repeated_endpoint_time_label` | gpt-5.6-sol | 3 | The bottom axis begins and ends with the identical tick label “Mar”. |
| `smooth_line_spline` | gemini-3.1-pro | 2 | lines are drawn as smooth curves (splines) rather than straight segments connecting points |
| `duplicate_time_ticks` | gemini-3.1-pro | 3 | the x-axis begins with 'Mar' and ends with another 'Mar' |
| `floating_footnote_text` | gemini-3.1-pro | 4 | the note '*Prior-year data...' is placed to the bottom right of the categories, above legend |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 650 | Apr、On-budget receipts | On-budget receipts、Apr | On-budget receipts、Apr | On-budget receipts、Apr | ✓ | ✓ | ✓ | 过 |
| 565 | Aug、On-budget outlays | On-budget outlays、Aug | On-budget outlays、Aug | On-budget outlays、Aug | ✓ | ✓ | ✓ | 过 |
| 140 | Jun、Off-budget receipts | Off-budget outlays、Mar | Off-budget outlays、Mar 2025 | Off-budget outlays、Mar | ✗ | ✗ | ✗ | 过 |
| 90 | Dec、Off-budget outlays | Off-budget outlays、Dec | Off-budget receipts、Aug | Excise taxes、2024 | ✓ | ✗ | ✗ | 过 |
| 1140 | Individual income taxes、2025 | Individual income taxes、2025 | Individual income taxes、2025 | Individual income taxes、2025 | ✓ | ✓ | ✓ | 过 |
| 800 | Social insurance and retirement receipts、2024 | Social insurance and retirement receipts、2024 | Social insurance and retirement receipts、2024 | Social insurance and retirement receipts、2024 | ✓ | ✓ | ✓ | 过 |
| 165 | Corporate income taxes、2025 | Corporate income taxes、2025 | Corporate income taxes、2025 | Corporate income taxes、2025 | ✓ | ✓ | ✓ | 过 |
| 35 | Excise taxes、2024 | Excise taxes、2024 | Custom duties、2024 | Misc. Receipts、2025 | ✓ | ✗ | ✗ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
