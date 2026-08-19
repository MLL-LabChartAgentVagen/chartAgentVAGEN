# 7c6b23db-en_p48

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 7c6b23db-en | `need_estimate` | 10 | 10 |

本页为IEA《Energy Technology Perspectives 2023》第48页，正文讨论热泵成本，下方是Figure 1.6，由六个小面板柱状图组成，展示NZE情景下若干清洁能源技术2021/2030/2050年的全球部署量。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 90 | `Electric cars` · `2050` | 10% | f1 | the 2050 bar in the Electric cars panel | 否 | `Electric cars` · `2050` · `Million units/year` |
| 2 | 61 | `Electric cars` · `2030` | 10% | f1 | the 2030 bar in the Electric cars panel | 否 | `Electric cars` · `2030` · `Million units/year` |
| 3 | 2.6 | `Fuel cell trucks` · `2050` | 15% | f1 | the 2050 bar in the Fuel cell trucks panel | 否 | `Fuel cell trucks` · `2050` |
| 4 | 600 | `Heat pumps` · `2050` | 20% | f1 | the 2050 bar in the Heat pumps panel | 否 | `Heat pumps` · `2050` · `GWth` |
| 5 | 650 | `Solar PV` · `2030` | 15% | f1 | the 2030 Solar PV bar in the Low-emission electricity panel | 否 | `Low-emission electricity` · `Solar PV` · `2030` · `GW/year` |
| 6 | 650 | `Solar PV` · `2050` | 15% | f1 | the 2050 Solar PV bar in the Low-emission electricity panel | 否 | `Low-emission electricity` · `Solar PV` · `2050` · `GW/year` |
| 7 | 400 | `Wind` · `2030` | 10% | f1 | the 2030 Wind bar in the Low-emission electricity panel | 否 | `Low-emission electricity` · `Wind` · `2030` · `GW/year` |
| 8 | 350 | `Wind` · `2050` | 20% | f1 | the 2050 Wind bar in the Low-emission electricity panel | 否 | `Low-emission electricity` · `Wind` · `2050` · `GW/year` |
| 9 | 450 | `Low-emission hydrogen` · `2050` | 10% | f1 | the 2050 bar in the Low-emission hydrogen panel | 否 | `Low-emission hydrogen` · `2050` · `Mt/year` |
| 10 | 110 | `Low-emission synthetic HF` · `2050` | 10% | f1 | the 2050 bar in the Low-emission synthetic HF panel | 否 | `Low-emission synthetic HF` · `2050` · `Billion litres/year` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 6 | 2 | 3 | 21 | 无 | Electric cars: 0, 30, 60, 90; Fuel cell trucks: 0, 1, 2, 3; Heat pumps: 0, 250, 500, 750; Low-emission electricity: 0, 200, 400, 600, 800; Low-emission hydrogen: 0, 100, 200, 300, 400, 500; Low-emission synthetic HF: 0, 25, 50, 75, 100, 125 |

- **f1** Figure 1.6 / Global deployment of selected clean energy technologies in the NZE Scenario　[图上方]　单位 `Million units/year`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | in "Low-emission electricity" two bars (Solar PV, Wind) sit side by side in each year slot |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | axes read 0-90, 0-3, 0-750, 0-800, 0-500, 0-125 across the six panels |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f1 | **无** | six panels of the same bar chart: Electric cars, Fuel cell trucks, Heat pumps, Low-emission electricity, hydrogen, synthetic HF |
| `source_note_lines` | source / note 行在图下方 | page | 有 | "Notes: HF = hydrocarbon fuels" and "IEA. CC BY 4.0." printed under the figure |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | "Solar PV  Wind" legend row drawn below the Low-emission electricity plot area |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | the only legend, "Solar PV  Wind", sits under the Low-emission electricity panel alone |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | each panel carries its own bold title above it, e.g. "Heat pumps", "Low-emission hydrogen" |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 0/200/400/600/800 with the scale word only in the rotated axis title "GW/year" |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "Million units/year", "GWth", "GW/year", "Mt/year", "Billion litres/year" set vertically along the axes |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole figure block behind the six panels carries a faint grey tint rather than white |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each tick in every panel, no vertical rules |

词表 65 项，本页出现 11 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `panel_without_axis_unit` | f1 | "Fuel cell trucks" panel shows ticks 0, 1, 2, 3 with no rotated axis title or unit | 该面板的数值单位在图上完全缺失，读出的2.6只能靠正文或外部知识补单位，表格行无法从页面获得单位标签。 |
| `subscript_in_axis_unit` | f1 | the Heat pumps axis title is "GWth" with a subscript "th" after GW | 解析为纯文本时下标易丢失或变成"GWth"，影响单位标签与数值的对应校验。 |
| `near_zero_bar_invisible` | f1 | 2021 bars in Fuel cell trucks, hydrogen and synthetic HF are hairlines at the baseline | 这些接近零的柱几乎无高度，无法按5%容差读数，只能报告为约零。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

六个面板全部values_printed=none，只能靠像素对轴读数，而刻度间距相对容差过粗：Electric cars刻度间隔30，61的5%容差仅±3，即约刻度间距的1/10；Heat pumps刻度间隔250，600的5%容差±30，约1/8格；Fuel cell trucks刻度间隔1，2.6要读到±0.13。Low-emission electricity中Solar PV 2030(650)与2050(650)高度几乎相同，需在600与800刻度之间精确插值，稍偏即越界。相比之下标签只需2–3个键（面板名+年份+系列），面板名又是加粗小标题，较易被解析捕获。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | per_panel_axis_range 与面板级单位（新组件 panel_without_axis_unit） | 条件行中加入"每面板独立轴范围+每面板独立单位，且允许某面板缺单位"的样式字段 | 面板键是否进入行键：同一图六面板单位各异时，缺panel_key的表格行会把2050的90/2.6/600混为一行 |
| P2 | 一类出版方 | per_panel_legend（仅一个面板带图例、其余面板单系列） | 图例布局字段：从图级shared_legend扩展为panel-scoped legend | 系列键仅对部分面板存在时，行键长度不一致对检索命中率的影响 |
| P7 | 通用 | rotated_axis_title 与 unit_in_axis_or_title（含下标 GWth） | heading/unit 字段：单位位置枚举增加"竖排轴标题"，并保留下标文本 | 单位只存在于竖排轴标题时，导出表格是否仍能把单位写进列头 |
| P1 | 通用 | near_zero_bar_invisible（2021年几乎为零的柱） | readable 判定：把每个mark的可达精度改为按柱高像素给出的分级精度 | 高度<2px的mark是否计入评分，及其对整图平均误差的贡献 |
