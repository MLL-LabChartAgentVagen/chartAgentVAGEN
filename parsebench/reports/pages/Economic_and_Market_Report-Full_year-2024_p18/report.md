# Economic_and_Market_Report-Full_year-2024_p18

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Economic_and_Market_Report-Full_year-2024 | `untagged` | 10 | 0 |

ACEA报告第18页：正文讨论2024年欧盟商用车按动力源的注册份额，下方为Figure 5单面板百分比堆叠柱状图（Vans/Trucks/Buses），数值以带指示箭头的深色标签框标出。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 6 | `Petrol` · `Vans` | 5% | f1 | the Vans Petrol segment | 是 | `Vans` · `Petrol` |
| 2 | 84.5 | `Diesel` · `Vans` | 5% | f1 | the Vans Diesel segment | 是 | `Vans` · `Diesel` |
| 3 | 6.1 | `Electrically chargeable vehicle (ECV)` · `Vans` | 5% | f1 | the Vans ECV segment | 是 | `Vans` · `Electrically chargeable vehicle (ECV)` |
| 4 | 2 | `Hybrid electric vehicle (HEV)` · `Vans` | 5% | f1 | the Vans HEV segment, labelled 'HEv, 2%' above the plot | 是 | `Vans` · `Hybrid electric vehicle (HEV)` |
| 5 | 95.1 | `Diesel` · `Trucks` | 5% | f1 | the Trucks Diesel segment | 是 | `Trucks` · `Diesel` |
| 6 | 2.3 | `Electrically chargeable vehicle (ECV)` · `Trucks` | 5% | f1 | the Trucks ECV segment | 是 | `Trucks` · `Electrically chargeable vehicle (ECV)` |
| 7 | 2.6 | `Others` · `Trucks` | 5% | f1 | the Trucks Others segment, labelled above the 100 line | 是 | `Trucks` · `Others` |
| 8 | 63.1 | `Diesel` · `Buses` | 5% | f1 | the Buses Diesel segment | 是 | `Buses` · `Diesel` |
| 9 | 18.5 | `Electrically chargeable vehicle (ECV)` · `Buses` | 5% | f1 | the Buses ECV segment | 是 | `Buses` · `Electrically chargeable vehicle (ECV)` |
| 10 | 9.8 | `Hybrid electric vehicle (HEV)` · `Buses` | 5% | f1 | the Buses HEV segment | 是 | `Buses` · `Hybrid electric vehicle (HEV)` |

**程序核对**（模型没有看到左半的标签列）：

- 组件要求的版面在图表分解里不成立，已剔除——shared_legend dropped: 1 figures, at most 1 panel(s)

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 5 | 3 | 15 | 部分 | 0, 20, 40, 60, 80, 100 |

- **f1** Figure 5. / New commercial vehicles registrations by power source　[图上方]　单位 `% SHARE`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each of the Vans, Trucks, Buses bars is built of Petrol/Diesel/ECV/HEV/Others segments |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f1 | **无** | all three bars top out at the 100 tick and the axis ends at 100 with '% SHARE' |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | 'Petrol  Diesel  Electrically chargeable vehicle (ECV) ...' row sits between the caption and the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis ticks are bare 0-100; the scale word appears only as '% SHARE' above the axis |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | '% SHARE' printed above the 100 tick at the top-left of the plot |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | boxed labels 'Diesel, 84.5%', 'ECV, 18.5%' drawn on top of their segments |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | 'Others, 1.5%', 'Others, 2.6%', 'Others, 8.5%' boxes sit above the 100 line with pointer arrows |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | labels for the thin Others and HEV bands are pushed above the plot and stacked ('Others, 1.5%' over 'HEv, 2%') |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 20, 40, 60, 80, 100; no vertical rules in the panel |

词表 65 项，本页出现 9 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `series_name_inside_value_label` | f1 | labels read 'Diesel, 84.5%', 'ECV, 6.1%', 'HEv, 2%' — series name and value in one box | 系列名写在数值标签里，且用缩写（ECV、HEv）而非图例全名，取值时必须把标签文字与图例项对应起来。 |
| `pointer_arrow_label_box` | f1 | each dark rounded label box has a small downward arrow tip touching its own segment | 箭头是标签与段的唯一归属线索；箭头方向决定该数值属于哪一段而不是相邻段。 |
| `unlabeled_minor_segments` | f1 | Trucks Petrol/HEV and Buses Petrol segments carry no printed value while others do | 同一图内部分段无数值，只能靠像素读数，且其厚度不足一格（20%）刻度，无法在5%容差内读出。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

十个被评分值全部印在图上，读数不是瓶颈；难点是定位。每个值都需要两把钥匙（车型 Vans/Trucks/Buses 加动力源），而图上只有 'Diesel, 84.5%' 这类合并文本，车型只写在类别轴上，解析器很容易把三组标签堆成一串而丢掉列归属。此外标签用缩写 'ECV'、'HEv' 而图例写作 'Electrically chargeable vehicle (ECV)'、'Hybrid electric vehicle (HEV)'，检索时两套名称不一致；'6'（Vans Petrol）与 '6.1'（Vans ECV）、'2'（Vans HEV）与 '2.3'、'2.6' 数字近似，缺了钥匙就无法唯一定位。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 series_name_inside_value_label（数值标签内含系列名且用缩写） | 标签样式字段：label_text_template 增加 '{series_abbrev}, {value}{unit}' 模式，并允许 legend 名与标签缩写不一致 | 标签文本是否携带系列名（纯数值 vs 名称+数值 vs 缩写名+数值）对定位准确率的影响 |
| P6 | 一类出版方 | value_label_outside 与 thin_segment_label 的组合：细段标签溢出到绘图区上方并带指示箭头 | 样式维度 value-label placement：新增 'overflow_above_plot_with_leader' 取值，触发条件为段高小于阈值 | 细段（<3% 高度）标签外移+引线 vs 直接省略，两种条件下该段取值可得率 |
| P7 | 一类出版方 | axis_title_above_axis 承载单位（'% SHARE' 置于顶端刻度之上） | 标题记录字段：unit 与其 placement 独立于 title/subtitle，可取 'above_top_tick' | 单位位置（轴上方 / 轴标题旁 / 副标题）三种条件下单位复原率 |
| P1 | 通用 | new_components 的 unlabeled_minor_segments：同图内部分段无数值标签 | 记录字段：per-mark label_printed 布尔，导出时区分“印出”与“需读像素” | 同一图内混合“已印数值段”与“未印数值段”时，未印段的可达精度单列一行 |
