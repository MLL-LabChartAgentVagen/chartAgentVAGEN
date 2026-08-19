# Renewables2025_1_p30

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Renewables2025_1 | `3d_chart+need_estimate` | 10 | 10 |

本页为IEA《Renewables 2025》第30页正文，中部含一幅无编号图：五个欧洲国家2021-2024年居民电价（柱、左轴EUR/MWh）与净新增装机（折线、右轴GW）的组合图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 290 | `Belgium` · `2021` | 5% | f1 | the Belgium 2021 bar (yellow, leftmost of the group) | 否 | `Belgium` · `2021` · `EUR/MWh` |
| 2 | 390 | `Germany` · `2024` | 5% | f1 | the Belgium 2022 bar (orange) | 否 | `Belgium` · `2022` · `EUR/MWh` |
| 3 | 350 | `Italy` · `2023` | 5% | f1 | the Italy 2023 bar (red), just under 360 | 否 | `Italy` · `2023` · `EUR/MWh` |
| 4 | 80 | `Netherlands` · `2022` | 10% | f1 | the Netherlands 2022 bar (orange), the shortest bar on the figure | 否 | `Netherlands` · `2022` · `EUR/MWh` |
| 5 | 230 | `Spain` · `2024` | 5% | f1 | the Italy 2021 bar (yellow); Spain 2023/2024 bars are also near this height | 否 | `Italy` · `2021` · `EUR/MWh` |
| 6 | 1.1 | `Belgium` · `2024` · `Net additions (right axis)` | 10% | f1 | a net-additions point on the right GW axis, e.g. the Belgium 2023 marker near the 1.0 gridline | 否 | `Belgium` · `2023` · `Net additions (right axis)` · `GW` |
| 7 | 3.5 | `Germany` · `2023` · `Net additions (right axis)` | 10% | f1 | the Germany 2023 net-additions marker, the highest point on the line (between 3.0 and 4.0) | 否 | `Germany` · `2023` · `Net additions (right axis)` · `GW` |
| 8 | 1.2 | `Italy` · `2022` · `Net additions (right axis)` | 10% | f1 | a net-additions marker slightly above 1.0, e.g. Italy 2022 | 否 | `Italy` · `2022` · `Net additions (right axis)` · `GW` |
| 9 | 1.3 | `Netherlands` · `2021` · `Net additions (right axis)` | 10% | f1 | a net-additions marker between 1.0 and 2.0, e.g. Belgium 2022 or Netherlands 2021 | 否 | `Netherlands` · `2021` · `Net additions (right axis)` · `GW` |
| 10 | 0.3 | `Spain` · `2024` · `Net additions (right axis)` | 20% | f1 | a low net-additions marker just above the 0.0 line, e.g. Spain 2021 | 否 | `Spain` · `2021` · `Net additions (right axis)` · `GW` |

**程序核对**（模型没有看到左半的标签列）：

- 组件要求的版面在图表分解里不成立，已剔除——shared_legend dropped: 1 figures, at most 1 panel(s)
- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: 390, 230, 1.1, 0.3
- 规则需要的键比模型报出的图能提供的多——rules need 3 keys, the richest figure offers 2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 5 | 5 | 40 | 无 | 0, 100, 200, 300, 400, 500, 600, 700, 800 |

- **f1** Residential sector retail electricity prices and annual capacity additions in selected European countries, 2021-2024　[图上方]　单位 `EUR/MWh`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | four coloured bars (2021, 2022, 2023, 2024) side by side within each country slot |
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | left axis 'EUR/MWh' 0-800, right axis 'GW' 0.0-4.0 for 'Net additions (right axis)' |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | bars plus a black line with open circle markers in the same panel |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'IEA. CC BY 4.0.' small print under the plot area |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend row '2024 2023 2022 2021 Net additions (right axis)' sits under the country axis |
| `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | f1 | **无** | legend entry reads 'Net additions (right axis)' pointing to the GW axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 0-800 and 0.0-4.0; scale only from 'EUR/MWh' and 'GW' axis titles |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'EUR/MWh' set vertically at left, 'GW' set vertically at right |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | country names under bracketed group separators spanning each set of four bars |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules across the plot at 100-unit steps, no vertical rules |

词表 65 项，本页出现 10 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `line_series_break_between_groups` | f1 | the net-additions line restarts within each country group, not connected across Belgium-Germany-Italy | 折线是每国内部四年的独立段，读点必须先定国家再定年份，否则会跨国错配数值。 |
| `license_credit_line` | f1 | 'IEA. CC BY 4.0.' printed right-aligned below the figure instead of a Source: line | 该图没有Source行，只有版权行；解析器若按Source定位图尾，会漏掉图注边界。 |
| `reversed_legend_order` | f1 | legend order 2024, 2023, 2022, 2021 while bars are drawn 2021 to 2024 left to right | 图例顺序与柱的绘制顺序相反，按图例次序取值会把年份系列整体颠倒。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

右轴GW只有0.0/1.0/2.0/3.0/4.0五个刻度，约1.0单位对应26像素；要把1.1、1.2、1.3区分到5%容差（即±0.06 GW）需分辨约1.5像素，而折线标记本身直径就有5像素以上，实际不可达；左轴柱虽有100间隔的水平网格，290与350这类值的5%容差（±15与±17.5）仍要求半格以内判读，且图上完全没有数值标签。相比之下标签只需三键（国家+年份+系列/单位），并不构成主要障碍。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | dual_axis 与 mixed_marks 的组合（柱+右轴折线）作为独立生成条件 | 图表族条件表中新增“双轴混合标记”一行，样式字段需指定右轴系列名带(right axis) | 左轴柱值 vs 右轴折线值分别计算命中率，检验解析器是否把折线点错读到左轴刻度 |
| new | 一类出版方 | new_components 中的 line_series_break_between_groups（分组内断开的折线） | 记录字段增加 group_id，使折线按类别组分段绘制 | 折线连续跨组 vs 按组断开两种设置下，点值定位到正确国家的准确率 |
| P1 | 通用 | 每个刻度间隔较大的次级轴（0.0–4.0仅5格）对应的 per-mark 可读精度评估 | 评测的 readable 判定改为按标记给出可达精度（依据像素/刻度比） | 按标记可达精度分档（≤2%、2–5%、>5%）分别统计得分 |
| P7 | 这份文档自己的习惯 | 无编号图但有粗体彩色标题+版权行的页面结构（含 rotated_axis_title 与 two_level_x_ticks） | 标题字段拆分为 number/title/subtitle/unit/placement，允许 number 为空、unit 落在旋转轴标题上 | 标题无编号且单位仅在旋转轴标题时，表格上下文命中率对比有编号图 |
