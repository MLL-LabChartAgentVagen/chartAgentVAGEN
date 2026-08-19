# Renewables2025_1_p43

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Renewables2025_1 | `need_estimate` | 10 | 10 |

本页为IEA《Renewables 2025》第43页，正文讨论拉美与加勒比可再生能源前景，中部为一幅2010-2030年按技术分的净新增装机分组柱状图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 10.0 | `2016` · `Hydropower` | 1% | f1 | the 2016 Hydropower bar, the tallest light-blue bar reaching the 10 gridline | 否 | `2016` · `Hydropower` · `Net additions (GW)` |
| 2 | 23.8 | `2024` · `Solar PV` | 2% | f1 | the 2024 Solar PV bar, the tallest red bar in the figure | 否 | `2024` · `Solar PV` · `Net additions (GW)` |
| 3 | 20.5 | `2023` · `Solar PV` | 2% | f1 | the 2023 Solar PV bar | 否 | `2023` · `Solar PV` · `Net additions (GW)` |
| 4 | 16.2 | `2022` · `Solar PV` | 5% | f1 | the 2022 Solar PV bar | 否 | `2022` · `Solar PV` · `Net additions (GW)` |
| 5 | 10.2 | `2021` · `Solar PV` | 5% | f1 | the 2021 Solar PV bar, just above the 10 gridline | 否 | `2021` · `Solar PV` · `Net additions (GW)` |
| 6 | 6.5 | `2023` · `Wind` | 10% | f1 | the 2023 Wind bar, the tallest green bar of the forecast years | 否 | `2023` · `Wind` · `Net additions (GW)` |
| 7 | 4.5 | `2014` · `Wind` | 10% | f1 | the 2025 Wind bar, near the 4.5 level between the 0 and 5 gridlines; the 2027 Wind bar is close in height | 否 | `2025` · `Wind` · `Net additions (GW)` |
| 8 | 22.8 | `2026` · `Solar PV` | 5% | f1 | the 2026 Solar PV bar | 否 | `2026` · `Solar PV` · `Net additions (GW)` |
| 9 | 22.5 | `2027` · `Solar PV` | 5% | f1 | the 2027 Solar PV bar | 否 | `2027` · `Solar PV` · `Net additions (GW)` |
| 10 | 16.8 | `2030` · `Solar PV` | 5% | f1 | the 2030 Solar PV bar, the last red bar; 2028 Solar PV (~17.3) is the nearest competitor | 否 | `2030` · `Solar PV` · `Net additions (GW)` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: 4.5

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 1 | 5 | 21 | 105 | 无 | 0, 5, 10, 15, 20, 25 |

- **f1** Net renewable capacity additions by technology in Latin America and the Caribbean, 2010-2030　[图上方]　单位 `Net additions (GW)`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | five thin bars sit side by side in each year slot from 2010 to 2030 |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | row `Hydropower  Bioenergy  Wind  Solar PV  Other renewables` under the category axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis ticks are bare `0, 5, 10 ... 25`; GW only appears in `Net additions (GW)` |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | `Net additions (GW)` set vertically along the left value axis |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 5, 10, 15, 20, 25 across the panel; no vertical rules |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 21 year slots x 5 technologies = 105 drawn bars |

词表 65 项，本页出现 6 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `rights_credit_line_below_figure` | f1 | `IEA. CC BY 4.0.` printed small at the lower right under the plot, no `Source:` line | 该行是版权署名而非数据来源，解析时容易被当作source行，导致图下唯一小字被误当作数据出处，实际图上没有任何来源或数据链接可辅助定位数值。 |
| `figure_frame_rules` | f1 | thin horizontal rules above the title and below the credit line box the whole figure | 图形块由上下两条横线界定而非编号，解析器需靠这两条线判断图与正文的边界，否则表格可能吞并周围正文。 |
| `unnumbered_figure` | f1 | heading starts directly with `Net renewable capacity additions by technology...`, no `Figure n` | 缺少图号时，只能用加粗标题行作为该表的唯一上下文键，若解析输出丢掉标题，数值就无法归属到任何图。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，唯一刻度是0/5/10/15/20/25，网格间距5 GW对应约55像素，即1 GW≈11像素。要落在5%容差内，4.5这个风电柱只允许±0.23 GW≈2.5像素误差，6.5允许±0.33 GW，而柱宽本身只有约4像素、且五个系列紧挨，柱顶抗锯齿就能吞掉这点差距；20以上的红柱容差稍宽（23.8允许±1.19 GW≈13像素）尚可读。相比之下标签只需“年份+技术”两个键，图例与年度刻度都完整印出，寻址不是瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | per-mark可达精度（针对无数值标签、刻度间距为量程1/5的密集分组柱） | 评测条件行中的readable判定，改为按柱高像素与刻度间距推算每个mark的容差 | 新增一行“无value_label且每系列柱宽<5px”的分组柱，对比其读数命中率与有标签图的差异 |
| P5 | 一类出版方 | dense_marks_100plus（21类×5系列=105个柱）作为受控密度维度 | 生成器的categories×series密度上限与样式字段（柱宽、系列间距） | 新增一行“单面板105+柱”的密度档，考察密度上升时逐柱寻址与读数的衰减 |
| P7 | 一类出版方 | unnumbered_figure与rotated_axis_title承载单位的标题拆分（title/unit分离、无figure_number） | 记录的heading字段：figure_number留空、unit_text取自旋转轴标题 | 新增一行“无图号且单位只在旋转轴标题中”的图，检验导出表能否带上标题与单位上下文 |
| P3 | 这份文档自己的习惯 | rights_credit_line_below_figure（图下仅有`IEA. CC BY 4.0.`而无Source行） | 图下小字行的记录字段，区分credit与source/note | 新增一行“图下只有版权署名、无来源行”的样式，检查解析器是否误把署名当作来源或表标题 |
