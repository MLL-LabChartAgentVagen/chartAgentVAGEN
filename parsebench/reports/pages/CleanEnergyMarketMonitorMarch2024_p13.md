# CleanEnergyMarketMonitorMarch2024_p13

![CleanEnergyMarketMonitorMarch2024_p13](../../data/pages/CleanEnergyMarketMonitorMarch2024_p13.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `CleanEnergyMarketMonitorMarch2024_p13` | CleanEnergyMarketMonitorMarch2024 | untagged | 10 | `parsebench/data/pages/CleanEnergyMarketMonitorMarch2024_p13.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 一页一个大标题「Solar PV capacity additions and avoided emissions」下放六个面板：World / China / European Union / United States / India 五个 2019–2023 的竖柱图（左轴竖排「GW」，刻度分别到 400、300、60、40、20，各自量程不同、零刻度标签省略、只有横向点状网格），加一个「Avoided emissions」横条图（类别在左，底轴 200/400/600，单位「Mt CO₂」写在轴下方，纵向点状网格，India 与 Rest of world 之间留了一个空槽）。数值全部白色粗体印在柱内；World 用橙色、其余用黄色、横条用青色。下方有 Notes 行与「IEA 2024. CC BY 4.0.」。
> 
> **定位一个值难在哪**
> 
> 以「12」为例：它同时是 India 面板 2019 年和 2023 年两根柱子的印刷值；「18」又同时出现在 European Union 2019 和 India 2022。因此一行必须同时带面板名与年份（India + 2023）才能唯一定位，只有「12 GW」无法区分。
> 
> **不确定的**
> 
> 无图号，不能确定这六块算一个图还是两个图；「Avoided emissions」的类别轴空行是否代表被省略的类别看不出；各竖柱面板基线是否严格为 0（零刻度未标注）只能由 India 的 5 柱高度推断。

**gpt-5.6-sol**

> **画出来要什么**
> 需绘制一个六面板复合柱图：五个地区面板按年份画竖柱，各用独立的 GW 刻度；“Avoided emissions”用横柱和 Mt CO₂ 刻度。所有柱内印白色数值，并分别使用横向或纵向点状网格。
> 
> **定位一个值难在哪**
> 印度的“12”同时出现在 2019 和 2023。定位目标值必须同时保留面板名“India”和年份，否则仅凭数值或面板无法唯一对应。
> 
> **不确定的**
> 页面未印图号。橙、黄、蓝三种柱色均无图例，无法确认颜色是否编码数据属性，还是仅作版式区分。

**gemini-3.1-pro**

> ### 画出来要什么
> 此页面需要绘制一个包含6个面板的组合图。前5个面板是垂直柱状图，共享x轴类别（年份）但y轴量程各自独立；第6个面板是水平柱状图，类别和单位与前五个完全不同。需要支持每个面板独立的标题（如“World”），y轴单位（“GW”）放置于最上方刻度的正上方，以及数值标签居于柱形内部。
> 
> ### 定位一个值难在哪
> 以“619”为例，它属于“Avoided emissions”面板下的“China”类别。由于6个面板类型和坐标轴不同，提取器必须将面板标题作为关键维度加入表格。如果没有面板名，系统无法将“China”作为国家的排放值与第二面板中“China”作为国家的光伏装机量区分开，导致键值碰撞。
> 
> ### 不确定的
> 前5个面板中，“World”面板的柱子使用了橙色，而其余国家/地区面板使用了黄色。图中并未提供图例说明这种颜色的差异是否代表了“总体”与“局部”的区别，生成时只能作为硬编码的特殊高亮处理。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | compound | 30 | — | above | all |
| gpt-5.6-sol | f1 | compound | 30 | — | above | all |
| gemini-3.1-pro | f1 | bar | 30 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_title_above_axis` | — | — | ✓ | gemini-3.1-pro: 'GW' is placed directly above the top tick of the left axes |
| `axis_title_below_plot` | ✓ | ✓ | — | opus-5: "Mt CO2" printed under the 200/400/600 tick row of the Avoided emissions panel；gpt-5.6-sol: “Mt CO₂” is centered below the avoided-emissions tick labels. |
| `heterogeneous_panel_types` | ✓ | — | ✓ | opus-5: five year-by-year column panels plus "Avoided emissions" horizontal bar panel in Mt CO2；gemini-3.1-pro: first 5 panels are vertical bars, the 6th is horizontal bars |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: dotted horizontal rules at 100/200/300/400 in the World panel, no vertical rules；gpt-5.6-sol: The five deployment panels draw dotted horizontal gridlines without vertical gridlines.；gemini-3.1-pro: panels 1 to 5 only have horizontal dotted grid lines |
| `highlighted_category` | ✓ | — | ✓ | opus-5: World panel bars drawn dark orange while China, EU, US, India bars are yellow；gemini-3.1-pro: World panel bars are orange, all other regions are yellow |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: Avoided emissions panel: China/European Union/United States/India/Rest of world on left, bars grow right；gpt-5.6-sol: Avoided emissions categories run vertically and bars extend right.；gemini-3.1-pro: the 'Avoided emissions' panel draws bars horizontally |
| `panel_title_per_panel` | ✓ | ✓ | ✓ | opus-5: each panel bold-titled above itself: "World", "China", "European Union", "United States", "India"；gpt-5.6-sol: Six headings include “World”, “China”, “India”, and “Avoided emissions” above their panels.；gemini-3.1-pro: titles like 'World', 'China' centered above each panel |
| `per_panel_axis_range` | ✓ | ✓ | ✓ | opus-5: top ticks are 400, 300, 60, 40 and 20 GW across the five country panels；gpt-5.6-sol: World ends at 400, China 300, EU 60, US 40, and India 20.；gemini-3.1-pro: World y-axis goes to 400, China goes to 300, India to 20 |
| `rotated_axis_title` | ✓ | ✓ | — | opus-5: "GW" set vertically beside the top of each country panel's left axis；gpt-5.6-sol: “GW” is rotated vertically beside each of the five deployment panels. |
| `small_multiples_5plus` | ✓ | ✓ | ✓ | opus-5: six panels under one title: World, China, European Union, United States, India, Avoided emissions；gpt-5.6-sol: World, China, European Union, United States, and India repeat five yearly bars.；gemini-3.1-pro: 6 panels sharing a main title, arranged in a grid |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: "Notes: "Avoided emissions" refers to avoided emissions in one year from cumulative deployment since 2019 to 2023."；gpt-5.6-sol: “Notes: ‘Avoided emissions’ refers to avoided emissions in one year from cumulative deployment since 2019 to 2023.”；gemini-3.1-pro: a 'Notes:' line sits at the bottom left of the page |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: bare numbers 100, 200, 300, 400; the scale word is only the rotated "GW"；gpt-5.6-sol: “GW” appears beside deployment axes and “Mt CO₂” beneath the avoided-emissions axis. |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: white bold numbers printed inside bar tops: "420", "261", "619"；gpt-5.6-sol: Every bar contains a bold white number, including “420” and “619”.；gemini-3.1-pro: numbers like '420' and '261' are printed inside the bar tops |
| `vgrid_only` | ✓ | ✓ | ✓ | opus-5: dotted vertical rules at 200, 400, 600 in the Avoided emissions panel；gpt-5.6-sol: The Avoided emissions panel draws dotted vertical gridlines without horizontal gridlines.；gemini-3.1-pro: panel 6 only has vertical dotted grid lines |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `zero_tick_label_omitted` | opus-5 | 2 | India panel ticks read 5, 10, 15, 20; bars stand on an unlabelled zero baseline |
| `spacer_slot_in_category_axis` | opus-5 | 3 | blank unlabelled slot between "India" and "Rest of world" rows in Avoided emissions |
| `credit_line_under_figure` | opus-5 | 4 | "IEA 2024. CC BY 4.0." printed right-aligned under the Avoided emissions panel |
| `panel_unit_differs_within_figure` | opus-5 | 3,4 | five panels in "GW", sixth panel in "Mt CO2" under one shared title |
| `mixed_bar_orientations` | gpt-5.6-sol | 3 | Five panels use vertical time bars; Avoided emissions uses horizontal category bars. |
| `mixed_panel_units` | gpt-5.6-sol | 3,4 | Five panels are labelled “GW”; the Avoided emissions panel is labelled “Mt CO₂”. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 420 | World、2023 | World、2023、GW | World、2023 | World、2023 | ✓ | ✓ | ✓ | 过 |
| 228 | World、2022 | World、2022、GW | World、2022 | World、2022 | ✓ | ✓ | ✓ | 过 |
| 261 | China、2023 | China、2023、GW | China、2023 | China、2023 | ✓ | ✓ | ✓ | 过 |
| 53 | European Union、2023 | European Union、2023、GW | European Union、2023 | European Union、2023 | ✓ | ✓ | ✓ | 过 |
| 32 | United States、2023 | United States、2023、GW | United States、2023 | United States、2023 | ✓ | ✓ | ✓ | 过 |
| 18 | India、2022 | India、2022、GW | India、2022 | India、2022 | ✓ | ✓ | ✓ | 过 |
| 12 | India、2023 | India、2023、GW | India、2023 | India、2019 | ✓ | ✓ | ✗ | 过 |
| 619 | China | Avoided emissions、China、Mt CO2 | Avoided emissions、China | Avoided emissions、China | ✓ | ✓ | ✓ | 过 |
| 221 | Rest of world | Avoided emissions、Rest of world、Mt CO2 | Avoided emissions、Rest of world | Avoided emissions、Rest of world | ✓ | ✓ | ✓ | 过 |
| 101 | European Union | Avoided emissions、European Union、Mt CO2 | Avoided emissions、European Union | Avoided emissions、European Union | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "compound" | "compound" | "bar" | bar | 按类型表自己的定义判：`compound` 是<strong>同一个面板里出现两种以上图元形状</strong>，所以决定它的是三家自己在 `components` 里记的 `mixed_marks`，不是它们给这张图起的名字。<strong>三家一个都没记 `mixed_marks`</strong>，只记了 `horizontal_bars`，图元数都是 30。opus 与 gpt 报 compound 的理由应当是这一页有 6 个面板——但面板数是版面属性，不是图元形状，按定义不构成 compound。 |
| `key_roles#f1` | ["category", "panel", "time"] | ["category", "panel"] | ["category", "panel"] | category × panel | gpt 与 gemini 一致：面板是国家（6 个），面板里的条是 2019 与 2023 两个离散槽位，按 <strong>时间轴的判据</strong>：等距排开的年 / 月刻度记 `time`；长度不等的区间带（`2001-09` `2011-14`）虽然等距排开，是有序类目，记 `category`（与 `timevalue_p9` 同一条）。记 category。opus 多记的 category（`Rest of world`）实际上是一个面板名。 |
