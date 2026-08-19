# CleanEnergyMarketMonitorMarch2024_p13

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| CleanEnergyMarketMonitorMarch2024 | `untagged` | 10 | 0 |

IEA《Clean Energy Market Monitor – March 2024》第13页，用五个小倍数柱状图（World、China、European Union、United States、India，单位GW，2019–2023）加一个横向条形图（Avoided emissions，单位Mt CO₂）展示光伏新增装机与避免的排放。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 420 | `World` · `2023` | 1% | f1 | the 2023 bar in the World panel | 是 | `World` · `2023` · `GW` |
| 2 | 228 | `World` · `2022` | 1% | f1 | the 2022 bar in the World panel | 是 | `World` · `2022` · `GW` |
| 3 | 261 | `China` · `2023` | 1% | f1 | the 2023 bar in the China panel | 是 | `China` · `2023` · `GW` |
| 4 | 53 | `European Union` · `2023` | 1% | f1 | the 2023 bar in the European Union panel | 是 | `European Union` · `2023` · `GW` |
| 5 | 32 | `United States` · `2023` | 1% | f1 | the 2023 bar in the United States panel | 是 | `United States` · `2023` · `GW` |
| 6 | 18 | `India` · `2022` | 1% | f1 | the 2022 bar in the India panel; the European Union 2019 bar also prints 18 | 是 | `India` · `2022` · `GW` |
| 7 | 12 | `India` · `2023` | 1% | f1 | the 2019 bar in the India panel; the India 2023 bar also prints 12 | 是 | `India` · `2019` · `GW` |
| 8 | 619 | `China` | 1% | f1 | the China bar in the Avoided emissions panel | 是 | `Avoided emissions` · `China` · `Mt CO2` |
| 9 | 221 | `Rest of world` | 1% | f1 | the Rest of world bar in the Avoided emissions panel | 是 | `Avoided emissions` · `Rest of world` · `Mt CO2` |
| 10 | 101 | `European Union` | 1% | f1 | the European Union bar in the Avoided emissions panel | 是 | `Avoided emissions` · `European Union` · `Mt CO2` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: 12

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 6 | 1 | 5 | 30 | 全部 | World: 100, 200, 300, 400; China: 100, 200, 300; European Union: 20, 40, 60; United States: 10, 20, 30, 40; India: 5, 10, 15, 20; Avoided emissions: 200, 400, 600 |

- **f1** Solar PV capacity additions and avoided emissions　[图上方]　单位 `GW; Mt CO2`
  - 来源行：IEA 2024. CC BY 4.0.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | in the `Avoided emissions` panel `China`, `European Union`, `India` sit on the y axis, bars grow right |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | top ticks differ: 400 (World), 300 (China), 60 (EU), 40 (US), 20 (India) |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f1 | **无** | six panels in a 3x2 grid: World, China, European Union, United States, India, Avoided emissions |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Notes: "Avoided emissions" refers to avoided emissions in one year from cumulative deployment since 2019 to 2023.` |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | five vertical GW bar panels plus one horizontal Mt CO2 bar panel under one page title |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | bold `World`, `China`, `European Union`, `United States`, `India`, `Avoided emissions` above each plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 100/200/300/400 with the scale word only in the `GW` axis title |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | `Mt CO2` printed under the 200/400/600 axis of the Avoided emissions panel |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | `GW` set vertically alongside the left axis of each of the five bar panels |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | `420`, `228`, `261`, `619` printed in white on top of the bars themselves |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | dotted horizontal rules at each GW tick in the five bar panels, no vertical rules |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the World panel bars are drawn dark orange while all other country panels are yellow |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | Avoided emissions panel has dotted vertical rules at 200, 400, 600 only |

词表 65 项，本页出现 13 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `zero_tick_label_omitted` | f1 | World axis labels start at 100, India at 5; bars still rise from an unlabelled zero baseline | 读数时最低刻度不是0，容易误判为轴从100起，实际比例仍以基线0为准，插值必须补一个隐含的0刻度。 |
| `blank_category_slot` | f1 | an empty row separates `India` from `Rest of world` in the Avoided emissions panel | 类别轴上存在无条形的空槽，表格化时容易多出一行空行或把Rest of world错位到相邻类别。 |
| `per_panel_unit_differs` | f1 | five panels labelled `GW`, the sixth labelled `Mt CO2` under one shared title | 同一图内单位不统一，取值必须连同所属面板的单位一起标注，否则619会被当成GW。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部印在柱上（420、228、261、53、32、18、12、619、221、101），读像素不成问题，所以卡点不是第2步。真正的障碍是寻址：同一页有六个面板共用一个标题，18同时出现在India 2022和European Union 2019，12同时出现在India 2019和India 2023，因此任一取值至少需要「面板名+年份」两个键，Avoided emissions面板还要再加单位Mt CO2才能与GW面板区分。若解析器把六个面板拼成一张不带面板列的表，18和12就无法唯一定位；而面板名（World/China/…）只作为图上粗体小标题存在，是否能进入表格的行/列键决定成败。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | per_panel_axis_range 与新提出的 per_panel_unit_differs 组合：让同一图的各面板拥有独立刻度上限和独立单位 | 图表条件行中的 panel 配置字段（每面板 axis_max 与 unit），以及记录字段中的 panel_key | 「面板单位/量纲是否一致」作为一行：单位统一 vs 单位混合时的取值正确率 |
| P4 | 一类出版方 | heterogeneous_panel_types：一个标题下混合纵向柱与横向条形面板 | 多面板布局生成器的 panel_type 列表允许异构，并让横向面板自带 vgrid_only | 「同图面板类型是否同构」一行：同构小倍数 vs 异构面板的定位错误率 |
| P6 | 通用 | zero_tick_label_omitted（新组件）与 axis_title_below_plot / rotated_axis_title 的单位位置 | 样式字段：tick 标签是否输出0刻度；unit 位置在旋转轴标题 vs 图下方 | 「零刻度标签缺失」一行：显示0刻度 vs 省略0刻度时的比例读数偏差 |
| P3 | 通用 | panel_title_per_panel 加页级大标题的双层标题结构 | 整页 markdown 导出时，面板名以粗体小标题写在各子表之上，页标题写在最上层 | 「面板名是否作为表上粗体标题输出」一行：有/无面板级标题时的上下文命中率 |
| new | 这份文档自己的习惯 | blank_category_slot（新组件）：类别轴上出现无条形的空槽 | 横向条形图的类别列表允许插入空占位类别 | 「类别轴含空槽」一行：连续类别 vs 含空槽时的行对齐错误率 |
