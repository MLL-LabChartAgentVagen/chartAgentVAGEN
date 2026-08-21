# pwc-semiconductor-and-beyond-2026-full-report_p18

![pwc-semiconductor-and-beyond-2026-full-report_p18](../../data/pages/pwc-semiconductor-and-beyond-2026-full-report_p18.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `pwc-semiconductor-and-beyond-2026-full-report_p18` | pwc-semiconductor-and-beyond-2026-full-report | untagged | 9 | `parsebench/data/pages/pwc-semiconductor-and-beyond-2026-full-report_p18.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 右栏一张灰底面板图：标题 `AI accelerators in the data center` 与单位 `(Unit: $ Billion)` 同一行并排；图例在图上方，含灰色方块 `Data center semiconductors` 与橙色粗线 `Portion of AI accelerator`。柱线混合、左右双值轴：左轴 0–300（无单位字），右轴 0–100 且轴顶写 `(%)`。x 轴为 `'24`…`'30F` 七个带撇号与 F 后缀的年份。只在折线首末标 `35%`、`52%`，其余 12 个标记无数字。下方 `Source: PwC analysis`。左侧两栏正文与图共处一条横带。
> 
> **定位一个值难在哪**
> `41`：它是 `'26F` 处折线的取值，折线不画点标记，必须在右轴 10 个单位一格的刻度间内插；5% 容差仅 ±2，相当于全轴 2%。同时该像素高度在左轴上还对应约 123，若表里不写清读的是哪条轴、哪种标记形状，值就无法核对。
> 
> **不确定的**
> 柱值全部未印，98/148/245/270 均为按 50 一格的横网格线目测；灰底究竟是整页右栏底色还是绘图区填充，无法从页面文字断定；折线是否真有 7 个数据点（只见一条平滑折线）只能推断。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 单面板柱线复合图：7根灰柱对应左侧十亿美元轴，橙线对应右侧百分比轴；图例在上方，右轴单位置于轴顶，仅端点标出“35%”“52%”。图旁并排两栏正文，底部有来源。
> 
> **定位一个值难在哪**
> 
> “’26F / Portion of AI accelerator / 41”须使用右轴；每格10个百分点，而5%容差仅±2.05，且41未直接印出，需要插值。
> 
> **不确定的**
> 
> 橙线没有可见点标记；按7个年份各含一个折点计数。柱值均按给定目标与轴位置配对。

**gemini-3.1-pro**

> ## 画出来要什么
> 这是一个带双Y轴的柱线混合图 (Combo Chart)。左侧Y轴为0-300，对应灰色柱状图（Data center semiconductors）；右侧Y轴为0-100，顶部带有“(%)”符号，对应橙色折线（Portion of AI accelerator）。X轴类别包含非标准的时间格式（'24, '25F等）。图例位于主标题与绘图区之间。折线仅在其首尾数据点（'24和'30F）印有数值标签（35%和52%），中间节点无标签。图表带有浅灰色的背景填充，且只绘制了水平网格线，没有垂直网格线。
> 
> ## 定位一个值难在哪
> 以测试值 `41` (对应 '26F, Portion of AI accelerator) 为例。该数值位于折线的中间部分，页面既没有标注出具体的数据，折线上也没有绘制数据点标记 (marker) 来辅助对齐。读者必须通过肉眼将平滑折线在柱子中轴线的交点向右平移，与间距为10的右侧百分比Y轴对比。在这种缺乏精确参考线的情况下，要在 5% 的容差范围内读出 41 非常困难。
> 
> ## 不确定的
> X轴年份中的“F”（如'25F）根据常识代表Forecast（预测），但图表中并没有显式的注脚或图例对此进行解释；对无标记折线中间点的值只能依靠所在的柱子中心线粗略推算横向位置。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | compound | 14 | — | above | some |
| gpt-5.6-sol | f1 | compound | 14 | — | above | some |
| gemini-3.1-pro | f1 | other · bar and line combo | 14 | — | above | some |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_title_above_axis` | ✓ | ✓ | ✓ | opus-5: `(%)` printed above the right axis top tick `100`；gpt-5.6-sol: “(%)” is printed above the right-side 100 tick.；gemini-3.1-pro: (%) sits above the top tick on the right axis |
| `dual_axis` | ✓ | ✓ | ✓ | opus-5: left ticks 0..300 for bars, right ticks 0..100 headed `(%)` for the orange line；gpt-5.6-sol: Left ticks run 0–300; right ticks run 0–100 with “(%)”.；gemini-3.1-pro: left axis is 0-300, right axis is 0-100 |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: faint horizontal rules run across the plot at 50-unit levels; no vertical rules；gpt-5.6-sol: Only horizontal rules cross the plot; no vertical grid lines are drawn.；gemini-3.1-pro: horizontal lines across the panel, no vertical ones |
| `legend_above_plot` | ✓ | ✓ | ✓ | opus-5: `Data center semiconductors` swatch and `Portion of AI accelerator` line sit between title and plot；gpt-5.6-sol: The two-item legend sits between the heading and plot.；gemini-3.1-pro: legend sits below the heading and above the plot |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: seven grey bars with one thick orange line drawn across the same plot；gpt-5.6-sol: Gray vertical bars and an orange line occupy the same panel.；gemini-3.1-pro: grey bars and an orange line in the same panel |
| `nonstandard_time_ticks` | ✓ | ✓ | ✓ | opus-5: ticks read `'24`, `'25F`, `'26F` ... `'30F`；gpt-5.6-sol: Time ticks use “’24”, then forecast labels such as “’25F” and “’30F”.；gemini-3.1-pro: x axis uses '24 and '25F |
| `panel_background` | ✓ | ✓ | ✓ | opus-5: the figure's whole right-hand column, plot area included, is filled light grey；gpt-5.6-sol: The plot area has a light-gray fill rather than white.；gemini-3.1-pro: the plot area carries a light grey tint |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: two columns of body text run left of the figure in the same horizontal band；gpt-5.6-sol: Two prose columns beginning “As AI applications…” run beside the figure.；gemini-3.1-pro: a text column runs alongside the figure on the left |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: `Source: PwC analysis` in small print under the category axis；gpt-5.6-sol: “Source: PwC analysis” appears below the plot.；gemini-3.1-pro: Source: PwC analysis below the figure |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: `(Unit: $ Billion)` beside the title; left axis shows bare 0, 50 ... 300；gpt-5.6-sol: The heading includes “(Unit: $ Billion)”; the right axis shows “(%)”.；gemini-3.1-pro: heading contains (Unit: $ Billion) and right axis has (%) |
| `value_label_outside` | ✓ | ✓ | — | opus-5: `35%` above the line start and `52%` above the line end, off the stroke；gpt-5.6-sol: “35%” and “52%” sit above the orange line. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `forecast_suffix_on_time_ticks` | opus-5 | 3 | `'24` actual then `'25F`...`'30F`: the F suffix marks forecast years inside the tick text |
| `endpoint_only_value_labels` | opus-5 | 2 | only the first (`35%`) and last (`52%`) line points carry numbers; five interior points bare |
| `unit_inline_right_of_title` | opus-5 | 4 | `(Unit: $ Billion)` set on the same baseline to the right of the bold title |
| `partial_value_labels` | gemini-3.1-pro | 2 | only 35% and 52% are printed on the line ends |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 98 | Data center semiconductors、'24 | Data center semiconductors、'24 | ’24、Data center semiconductors | '24、Data center semiconductors | ✓ | ✓ | ✓ | 没过 |
| 148 | Data center semiconductors、'26F | Data center semiconductors、'26F | ’26F、Data center semiconductors | '26F、Data center semiconductors | ✓ | ✓ | ✓ | 没过 |
| 270 | Data center semiconductors、'30F | Data center semiconductors、'30F | ’30F、Data center semiconductors | '30F、Data center semiconductors | ✓ | ✓ | ✓ | 没过 |
| 180 | Data center semiconductors、'27F | Data center semiconductors、'27F | ’27F、Data center semiconductors | '27F、Data center semiconductors | ✓ | ✓ | ✓ | 过 |
| 35 | Portion of AI accelerator、'24 | Portion of AI accelerator、'24 | ’24、Portion of AI accelerator | '24、Portion of AI accelerator | ✓ | ✓ | ✓ | 过 |
| 52 | Portion of AI accelerator、'30F | Portion of AI accelerator、'30F | ’30F、Portion of AI accelerator | '30F、Portion of AI accelerator | ✓ | ✓ | ✓ | 过 |
| 41 | Portion of AI accelerator、'26F | Portion of AI accelerator、'26F | ’26F、Portion of AI accelerator | '26F、Portion of AI accelerator | ✓ | ✓ | ✓ | 过 |
| 47 | Portion of AI accelerator、'28F | Portion of AI accelerator、'28F | ’28F、Portion of AI accelerator | '28F、Portion of AI accelerator | ✓ | ✓ | ✓ | 没过 |
| 245 | Data center semiconductors、'29F | Data center semiconductors、'29F | ’29F、Data center semiconductors | '29F、Data center semiconductors | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "compound" | "compound" | "other · bar and line combo" | compound | 图元数三家都是 14，都报 mixed_marks。 |
| `key_roles#f1` | ["series", "time"] | ["series", "time"] | ["category", "series"] | series × time | x 轴是 '24…'30F 的年份，是时间；两个系列一柱一线，分别对着左轴（$ Billion 0–300）与右轴（% 0–100）。gemini 记的 category 是把年份当类目，与另两家读的是同一张图。这一页是本轮最标准的双轴 + 混合图元实例。 |
