# Renewables2025_1_p32

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Renewables2025_1 | `need_estimate` | 10 | 10 |

该页顶部是一张IEA无编号双面板图（左：2024/2030欧盟可再生装机堆积柱状图，单位GW；右：RED II/RED III可再生能源份额柱状图加两条目标参考线），下方为Note/Sources小字与正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 310 | `2024` · `Solar PV` | 1% | f1 | the 2024 Solar PV segment in the left panel | 否 | `2024` · `Solar PV` · `GW` |
| 2 | 230 | `2024` · `Wind` | 1% | f1 | the 2024 Wind segment in the left panel | 否 | `2024` · `Wind` · `GW` |
| 3 | 600 | `2030` · `Solar PV` | 1% | f1 | the 2030 Solar PV segment in the left panel | 否 | `2030` · `Solar PV` · `GW` |
| 4 | 370 | `2030` · `Wind` | 1% | f1 | the 2030 Wind segment in the left panel | 否 | `2030` · `Wind` · `GW` |
| 5 | 135 | `2030` · `Accelerated` | 1% | f1 | the 2030 Accelerated top segment in the left panel | 否 | `2030` · `Accelerated` · `GW` |
| 6 | 590 | `2030` · `Solar PV` | 3% | f1 | the 2030 REPowerEU Solar PV segment in the left panel | 否 | `2030 REPowerEU` · `Solar PV` · `GW` |
| 7 | 520 | `2030` · `Wind` | 1% | f1 | the 2030 REPowerEU Wind segment in the left panel ("520-GW REPowerEU ambition" appears only in the Sources text) | 否 | `2030 REPowerEU` · `Wind` · `GW` |
| 8 | 32 | `RED II` · `Binding target` | 1% | f1 | the RED II Binding target bar in the right panel, top near 32% | 否 | `RED II` · `Binding target` |
| 9 | 42.5 | `RED III` · `Binding target` | 1% | f1 | the RED III Binding target bar (solid blue part), top just above 42% | 否 | `RED III` · `Binding target` |
| 10 | 40 | `Assessment of final updated NECPs` | 1% | f1 | the red "Assessment of final updated NECPs" rule at 40% spanning both right-panel categories | 否 | `Assessment of final updated NECPs` · `RED III` |

**程序核对**（模型没有看到左半的标签列）：

- 面板数与面板名个数不一致——f1: panels=2, 0 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 2 | 8 | 3 | 15 | 无 | left: 0, 250, 500, 750, 1 000, 1 250, 1 500; right: 25%, 30%, 35%, 40%, 45%, 50% |

- **f1** EU installed renewable capacity in 2024 and 2030 vs REPowerEU 2030 targets (left) and shares of renewables in final energy consumption in 2030 (right)　[图上方]　单位 `GW`
  - 来源行：Sources: REPowerEU ambitions for total renewable capacity are from REPowerEU Plan SWD (2022) 230 final; wind and solar PV are from Implementing the REpowerEU Action Plan. The solar PV ambition is in AC, as it is similar to the "almost 600 MW by 2030" target identified in the EU Solar Energy Strategy SWD (2022) 148 final. The 2030 EU offshore wind ambition is from Delivering on the EU Offshore Renewable Energy Ambitions, and the onshore wind aim is the difference between the 520-GW REPowerEU ambition and the 111-GW offshore wind target in Delivering on the EU Offshore Renewable Energy Ambitions. All solar PV values are in AC, including for the main and accelerated cases, and all solar PV totals are calculated in AC. The member-state ambition is estimated from NECPs.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | left bars stack Solar PV, Wind, Other and Accelerated to totals near 690, 1 255, 1 236 GW |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | right panel: two bars plus a black dashed line at 45% and a red line at 40% |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | legend entries "REPowerEU target" (dashed) and "Assessment of final updated NECPs" (red rule) |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left axis 0-1 500 GW, right axis 25%-50%; no reading carries across |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | right value axis lowest tick is "25%", bars start at that baseline, no break glyph |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: RED = Renewable Energy Directive. NECP = National Energy and Climate Plan." then "Sources: ..." |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | both legend rows sit under their plot areas, below the category tick labels |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | left legend "Accelerated Other Wind Solar PV"; separate right legend "Binding target ... Assessment of final updated NECPs" |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | left: four-series GW stacked bars; right: two %-share bars overlaid with two target rules |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | left ticks are bare numbers 0-1 500; scale word only in the rotated "GW" axis label |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "GW" set vertically at the top left of the left value axis, beside tick "1 500" |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | right categories "RED II" and "RED III"; note explains "RED = Renewable Energy Directive" |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | third left category prints on two lines: "2030" over "REPowerEU" |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | f1 | **无** | "REPowerEU target" drawn dashed while "Assessment of final updated NECPs" is solid red |

词表 65 项，本页出现 14 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `pattern_fill_series` | f1 | "Aspirational target" segment drawn with diagonal hatching; "Accelerated" drawn as white outline-only block | 仅靠填充图案（斜纹/空白）区分系列，读值时须先按图案而非颜色定位段落，否则会把顶部空白段并入下方柱体。 |
| `panel_designation_in_title` | f1 | single title carries "(left)" and "(right)"; no panel titles above the two plots | 面板名不在图内，任何取值都要靠标题里的"(left)/(right)"来指认面板，表格若丢掉标题就无法区分GW与%两套值。 |
| `partial_width_reference_line` | f1 | dashed 45% rule and red 40% rule span only the bar region, not the full plot width | 参考线不贯穿画面，须判断它覆盖哪些类别；红线横跨两柱说明40%是整体评估值而非某一柱的值。 |
| `increment_segment_on_top` | f1 | "Accelerated" white segment sits above the 2030 stack, marking extra capacity to 1 255 GW | 顶段是情景增量而非同类构成，读总量时要区分主情景总计与含增量总计，否则2030柱高会被误读。 |
| `per_panel_unit` | f1 | left axis in GW, right axis in %; one figure, two incompatible value units | 同一图内两套单位，取值行必须带面板/单位标签，否则42.5与520这类数字无法判断量纲。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签（values_printed=none），十个待测值全靠像素反推。左面板刻度间距为250 GW，而Accelerated段约135 GW，5%容差只有±6.75 GW，相当于一个刻度间距的2.7%；Wind 370 GW的容差±18.5 GW也不到刻度间距的8%，且Wind、Other都必须用堆积上下边界相减得到，误差叠加。右面板轴起点为25%、间距5个百分点，42.5%与红线40%相差仅2.5点即半个刻度，肉眼分辨勉强。相比之下标签只需"面板+类别+系列"三个键（如"2030 REPowerEU"+"Wind"+"GW"），表格可以承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | 新组件 per_panel_unit 与 panel_designation_in_title | 记录字段中的 panel_key 与 heading 拆分：允许每个面板携带自己的单位，且面板名只以"(left)/(right)"写在总标题里 | 面板单位是否进入键：同图两套单位（GW / %）时，去掉 panel_key 后取值定位错误率对照行 |
| P6 | 一类出版方 | 新组件 pattern_fill_series（斜纹/空心填充区分系列） | 样式字段增加 fill_pattern 维度，作用于堆积段与图例样块 | 仅靠图案而非颜色区分系列时，段落归属识别准确率的对照行 |
| P6 | 一类出版方 | axis_starts_above_zero 与非零起点的刻度格式（25%…50%） | 条件行中的值轴范围设置：允许柱状图基线在非零刻度，并同时输出真实值与柱长 | 基线非零的柱图：柱长与数值不成比例时，读值误差随起点抬升的对照行 |
| P1 | 通用 | 堆积段差分精度（P1 的按段可达精度） | readable 判定改为逐段：以段高/刻度间距比给出可达容差，如135 GW 段对250 GW 刻度 | 薄段（段高<刻度间距的60%）的可达精度阈值行，取代整图布尔可读判定 |
| P7 | 这份文档自己的习惯 | 无编号图 + 标题/版权行/Note-Sources 的排版位置（new_components 中的 rights 与说明行） | 整页 markdown 导出：标题作为粗体/标题行置于表格之上，Note 与 Sources 各成一行置于表下 | 图无编号时，仅靠标题文本作为上下文键的命中率对照行 |
