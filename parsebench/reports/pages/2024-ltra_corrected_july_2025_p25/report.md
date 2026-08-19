# 2024-ltra_corrected_july_2025_p25

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2024-ltra_corrected_july_2025 | `need_estimate` | 9 | 9 |

该页为NERC《2024 Long-Term Reliability Assessment》第25页，左栏为Figure 11（海上风电规划容量堆积柱状图），右栏为Figure 12（电池资源现有及规划容量堆积柱状图，含ERCOT未显示数值文本框），其余为正文与脚注。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 3,500 | `NPCC-New England` · `Tier 1` | 10% | f1 | the NPCC-New England Tier 1 segment (dark bottom segment) | 否 | `Figure 11: Offshore Wind Capacity Planned through 2034` · `NPCC-New England` · `Tier 1` · `MW` |
| 2 | 2,000 | `NPCC-New York` · `Tier 1` | 50% | f1 | the NPCC-New York Tier 1 segment (dark bottom segment) | 否 | `Figure 11: Offshore Wind Capacity Planned through 2034` · `NPCC-New York` · `Tier 1` · `MW` |
| 3 | 2,800 | `NPCC-New York` · `Tier 3` | 25% | f1 | the PJM Tier 1 segment (dark bottom segment, top just under 3,000) | 否 | `Figure 11: Offshore Wind Capacity Planned through 2034` · `PJM` · `Tier 1` · `MW` |
| 4 | 5,200 | `MRO-SPP` · `Tier 3` | 15% | f2 | the NPCC-New York stack: top of the Tier 3 (yellow) segment, i.e. the area total | 否 | `Figure 12: Battery Resource Capacity Existing and Planned through 2034` · `NPCC-New York` · `Tier 3` · `MW` |
| 5 | 3,000 | `NPCC-Ontario` · `Tier 1` | 10% | f2 | the NPCC-Ontario Tier 1 segment, the only segment drawn for that area | 否 | `Figure 12: Battery Resource Capacity Existing and Planned through 2034` · `NPCC-Ontario` · `Tier 1` · `MW` |
| 6 | 44,000 | `PJM` · `Tier 2` | 5% | f2 | the PJM Tier 2 (grey) segment, the tallest bar reaching just under 45,000 | 否 | `Figure 12: Battery Resource Capacity Existing and Planned through 2034` · `PJM` · `Tier 2` · `MW` |
| 7 | 6,200 | `WECC-CAMX` · `Existing` | 10% | f2 | the WECC-CAMX Existing (blue) bottom segment, topping just above 5,000 | 否 | `Figure 12: Battery Resource Capacity Existing and Planned through 2034` · `WECC-CAMX` · `Existing` · `MW` |
| 8 | 15,000 | `WECC-NW` · `Tier 3` | 10% | f1 | the NPCC-New England stack total, top of the Tier 3 (light grey) segment | 否 | `Figure 11: Offshore Wind Capacity Planned through 2034` · `NPCC-New England` · `Tier 3` · `MW` |
| 9 | 3,500 | `WECC-SW` · `Tier 1` | 10% | f2 | the MRO-SPP Tier 1 (orange) segment, the lower block under the yellow Tier 3 | 否 | `Figure 12: Battery Resource Capacity Existing and Planned through 2034` · `MRO-SPP` · `Tier 1` · `MW` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 9 predicted key sets miss a rule label: 2,800, 5,200, 15,000, 3,500

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 3 | 3 | 9 | 无 | 0, 5,000, 10,000, 15,000, 20,000, 25,000, 30,000, 35,000 |
| f2 | `stacked_bar` | vertical | 1 | 4 | 9 | 30 | 部分 | 50,000, 45,000, 40,000, 35,000, 30,000, 25,000, 20,000, 15,000, 10,000, 5,000, - |

- **f1** Figure 11 / Offshore Wind Capacity Planned through 2034　[图下方]　单位 `MW`
- **f2** Figure 12 / Battery Resource Capacity Existing and Planned through 2034　[图下方]　单位 `MW`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each area's bar is built from Tier 1, Tier 2, Tier 3 segments stacked to the total |
| `stacked_bar` | 堆叠条 | f2 | 有 | bars stack Existing, Tier 1, Tier 2, Tier 3 segments, e.g. PJM grey segment tops near 45,000 |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f2 | **无** | boxed note over the plot: `ERCOT (Not shown) (MW) Existing: 7,335 Tier 1: 19,923 ...` |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | `Figure 11: Offshore Wind Capacity Planned through 2034` and `Figure 12: Battery Resource Capacity ...` |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | row `Tier 1  Tier 2  Tier 3` sits under the category axis, above the caption |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | row `Existing  Tier 1  Tier 2  Tier 3` sits below the rotated category labels |
| `legend_inside_plot` | 图例画在绘图区内部 | f2 | **无** | the ERCOT value box occupies the upper-left of the plot area as a bordered block |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f2 | **无** | left-column prose `Offshore wind plants are increasingly entering...` runs level with Figure 12's plot area |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | ticks read bare `0 ... 35,000`; scale word only in the rotated axis title `MW` |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | ticks read bare `- ... 50,000`; unit only from axis title `MW` and box `(MW)` |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | `MW` set vertically along the left value axis |
| `rotated_axis_title` | 轴标题竖排 | f2 | 有 | `MW` set vertically at the left of the plot beside the 25,000 tick |
| `rotated_x_ticks` | x 刻度标签旋转 | f2 | 有 | category labels `MRO-SPP`, `NPCC-New England` ... set at about 45 degrees |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f2 | 有 | axis codes `MRO-SPP`, `PJM`, `SERC-FP`, `WECC-CAMX`, `WECC-NW`, `WECC-SW` |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at every 5,000 across the panel, no vertical rules |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | horizontal rules at every 5,000 across the panel, no vertical rules |

词表 65 项，本页出现 11 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `offscreen_category_values_box` | f2 | `ERCOT (Not shown) (MW)` box lists Existing 7,335, Tier 1 19,923, Tier 2 97,960, Tier 3 47,404 | ERCOT这一类别没有柱子，四个数值只能从框内文字读取，表格若只列绘出的类别就会漏掉四个已印数值。 |
| `dash_as_zero_tick` | f2 | the lowest value-axis tick is printed as `-` instead of `0`, above it `5,000` | 零刻度写成短横，解析器可能把该刻度当作缺失或分隔符，影响基线定位与线性插值读数。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

两图除ERCOT文本框外全部没有数值标签，段值必须靠像素高度对刻度插值。Figure 12的值轴跨0–50,000只有11条5,000间隔的网格线，绘图区高度约340px，即约147 MW/px；2,800或3,000这类小段的5%容差仅±140–150 MW，等于1个像素，堆积段还要先做上下沿相减，误差翻倍。Figure 11刻度密一些（5,000/约50px，约100 MW/px），但3,500的±175 MW仍不到2px。相比之下第3步只需“图号+类别+Tier”三个键，表格容易承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | 新增 offscreen_category_values_box（图内列出未绘制类别数值的文本框） | 图表记录层增加“未绘制类别”条目字段，并在样式条件行中加入“annotation box carrying its own category+series values” | 有/无“框内未绘类别数值”条件下，表格是否能同时输出绘出类别与仅文本类别的数值 |
| P6 | 这份文档自己的习惯 | dash_as_zero_tick（零刻度以 `-` 表示的会计式刻度格式） | 样式字段 tick_format 增加 accounting/dash-zero 选项 | 零刻度写作 `0` 与写作 `-` 两种刻度格式下的基线定位与读数误差对比 |
| P1 | 通用 | 堆积段的可达精度（本页9个抽查值全部无标签，需按段高插值） | 把 readable 从布尔门槛改为按 mark 的精度上限，纳入“段高/像素密度”与“堆积需相减”两个因子 | 顶部单段 vs 中间堆积段（需上下沿相减）在同一像素密度下的5%命中率 |
| P7 | 一类出版方 | 标题块拆分与位置（figure_number/title 位于绘图区下方，单位只在旋转轴标题 `MW` 中） | 标题记录拆为 number/title/subtitle/unit/placement，placement 支持 below 且单位来源可为旋转轴标题 | 标题在图下方（caption-below）且单位仅在旋转轴标题时，导出表格能否携带图号与单位 |
