# CleanEnergyMarketMonitorMarch2024_p19

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| CleanEnergyMarketMonitorMarch2024 | `untagged` | 5 | 0 |

IEA《Clean Energy Market Monitor – March 2024》第19页，用六个小图展示2019–2023年世界及主要市场电动汽车销量与各地区避免的排放量。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 13.7 | `World` · `2023` | 1% | f1 | the 2023 bar in the World panel | 是 | `World` · `2023` · `Million units` |
| 2 | 6.0 | `China` · `2022` | 1% | f1 | the 2022 bar in the China panel | 是 | `China` · `2022` · `Million units` |
| 3 | 1.7 | `European Union` · `2021` | 1% | f1 | the 2021 bar in the European Union panel | 是 | `European Union` · `2021` · `Million units` |
| 4 | 0.6 | `United States` · `2021` | 1% | f1 | the 2021 bar in the United States panel | 是 | `United States` · `2021` · `Million units` |
| 5 | 82 | `India` · `2023` | 1% | f1 | the 2023 bar in the India panel | 是 | `India` · `2023` · `Thousand units` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 6 | 1 | 5 | 30 | 全部 | World: 15, 10, 5; China: 9, 6, 3; European Union: 3, 2, 1; United States: 1.5, 1.0, 0.5; India: 90, 60, 30; Avoided emissions: 10, 20 |

- **f1** Electric car sales and avoided emissions　[图上方]　单位 `Million units / Thousand units / Mt CO₂`
  - 来源行：IEA 2024. CC BY 4.0.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | in "Avoided emissions" regions sit on the y axis, bars grow right to 22, 15, 14, 3, 7 |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | top ticks differ: World 15, China 9, European Union 3, United States 1.5, India 90 |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f1 | **无** | six panels: "World", "China", "European Union", "United States", "India", "Avoided emissions" |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Notes: "Avoided emissions" refers to avoided emissions in one year from cumulative deployment since 2019 to 2023." |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | "Avoided emissions" is horizontal bars by region; the other five are vertical bars by year |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | each panel carries a bold title above it, e.g. "United States", "India" |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 5/10/15 with scale only in axis title "Million units"; India "Thousand units" |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | "Mt CO₂" printed under the 10, 20 ticks of the "Avoided emissions" panel |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "Million units" and "Thousand units" set vertically along the left axes |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | "Mt CO₂" carries subscript 2 in the axis unit under the avoided-emissions panel |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | white numbers printed on the bars: "13.7", "8.1", "2.4", "1.4", "82", "22" |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | India 2019 "1" and 2020 "3" set in black above their near-invisible bars |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | dotted horizontal rules at each tick in the five sales panels, no vertical rules |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | "Avoided emissions" panel has dotted vertical rules at 10 and 20 only |

词表 65 项，本页出现 14 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `panel_fill_color_marks_aggregate` | f1 | "World" bars drawn dark orange, the four country/region panels yellow, avoided emissions teal | 颜色不区分系列而区分面板层级，读数时必须靠面板标题而非颜色定位，聚合面板（World）不能与分区面板混读。 |
| `blank_category_slot_before_residual_row` | f1 | an empty row gap separates "United Kingdom" from "Rest of world" in the avoided emissions panel | 类别轴上有一个无标签空槽，解析成表格时容易多出空行或错位，使 7 被错配到 United Kingdom。 |
| `per_panel_unit_change` | f1 | India axis reads "Thousand units" while other sales panels read "Million units" | 同一图内单位随面板变化，82 与 13.7 不能同尺度比较，取值必须连同该面板单位一起给出。 |

## 5 · 难在哪

卡在 **第四步 · 表外上下文**。

五个销量面板共用完全相同的类别轴 2019–2023，且数值大量重复："1.0" 同时是 European Union 2020 与 United States 2022，"0.3" 在 United States 出现两次，"1.1" 在 China 出现两次。因此仅靠 年份+数值 无法唯一定位，必须带上面板名 World/China/European Union/United States/India，而这些名字只是各面板上方的粗体小标题，位于任何解析出的表格之外；若导出时未把它们写成标题或粗体行，13.7 与 6.0 之类的值就无法被寻址。相反，数值本身全部印在柱上（13.7、8.1、82），第2步几乎不构成障碍，5% 容差与 5/10/15 的刻度间距无关。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | panel_title_per_panel 与 per_panel_axis_range 组合：把面板名并入检索键 | 记录字段中增加 panel_key，并在条件行里让同一份年份类别在多面板间重复 | 有/无 panel_key 时，重复类别轴（2019–2023×5面板）下数值寻址成功率对比 |
| P6 | 一类出版方 | 新组件 per_panel_unit_change（Million units vs Thousand units vs Mt CO₂） | 样式字段的单位位置维度，允许每面板独立的旋转轴标题与轴下单位 | 单位统一 vs 单位随面板变化时，数值+单位联合命中率一行 |
| P6 | 通用 | value_label_outside 与 value_label_inside 混用（India 的 1、3 在柱外，其余在柱内） | 样式字段 value-label placement 允许按柱高自动外移 | 极小柱（<轴上限4%）标签内置 vs 外置时的标签-柱归属正确率 |
| P4 | 一类出版方 | heterogeneous_panel_types（纵向时间柱 + 横向区域柱同图） | 图族权重向量中加入“同一图内混合族”的生成比例 | 纯同族小多图 vs 含异族面板页面的整页导出准确率 |
| P7 | 这份文档自己的习惯 | 标题块拆分：无编号标题 + 无副标题 + 单位在轴（P7 字段化） | 图题字段化为 number/title/subtitle/unit/placement，本页 figure_number 为空 | 无编号图题在整页 markdown 中作为标题输出与否的上下文命中率 |
