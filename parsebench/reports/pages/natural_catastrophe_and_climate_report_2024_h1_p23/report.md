# natural_catastrophe_and_climate_report_2024_h1_p23

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| natural_catastrophe_and_climate_report_2024_h1 | `need_estimate` | 10 | 10 |

该页为气候评述文章，正文双栏，页底为 Figure 12：1950–2025 年 Niño 3.4 区月度 ONI 海温异常的填色面积图，右侧附一幅标注“Niño3.4 Region”的定位地图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 2.6 | `2015` · `El Niño` | 10% | f1 | the tallest red peak, the 2015/16 El Niño maximum just left of the 2015 tick region | 否 | `Figure 12` · `El Niño` · `2015` |
| 2 | 2.4 | `1997` · `El Niño` | 10% | f1 | the red peak at the 1997/98 El Niño, between the 1995 and 2000 ticks | 否 | `Figure 12` · `El Niño` · `1995` |
| 3 | 2.2 | `1982` · `El Niño` | 10% | f1 | the red peak at the 1982/83 El Niño, just after the 1980 tick | 否 | `Figure 12` · `El Niño` · `1980` |
| 4 | -1.8 | `1955` · `La Niña` | 10% | f1 | a deep blue trough, most plausibly the 1973/74 La Niña between the 1970 and 1975 ticks; several troughs sit at this depth so it cannot be pinned uniquely | 否 | `Figure 12` · `La Niña` · `1975` |
| 5 | -0.8 | `1973` · `La Niña` | 20% | f1 | a shallow blue dip, e.g. the 2017/18 La Niña between the 2015 and 2020 ticks; many dips reach this depth | 否 | `Figure 12` · `La Niña` · `2015` |
| 6 | -1.3 | `1988` · `La Niña` | 10% | f1 | a moderate blue trough, e.g. the 2020/21 La Niña near the 2020 tick | 否 | `Figure 12` · `La Niña` · `2020` |
| 7 | 1.8 | `1972` · `El Niño` | 10% | f1 | a red peak reaching between the 1.0 and 2.0 ticks, e.g. the 1972/73 El Niño after the 1970 tick | 否 | `Figure 12` · `El Niño` · `1970` |
| 8 | -1.5 | `1999` · `La Niña` | 10% | f1 | a blue trough between the -1.0 and -2.0 ticks, e.g. the 2007/08 La Niña after the 2005 tick | 否 | `Figure 12` · `La Niña` · `2005` |
| 9 | 1.8 | `2024` · `El Niño` | 10% | f1 | a second red peak of the same height, e.g. the 2023/24 El Niño at the right end just before the 2025 tick | 否 | `Figure 12` · `El Niño` · `2020` |
| 10 | -1.6 | `2010` · `La Niña` | 10% | f1 | a blue trough near -1.6, e.g. the 2010/11 La Niña at the 2010 tick | 否 | `Figure 12` · `La Niña` · `2010` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——8 of 10 predicted key sets miss a rule label: 2.4, 2.2, -1.8, -0.8, -1.3, 1.8

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `area` | vertical | 1 | 3 | 16 | 890 | 无 | 3.0, 2.0, 1.0, 0.0, -1.0, -2.0, -3.0 |
| f2 | `map` | na | 1 | 1 | 1 | 1 | 无 | （不画值轴） |

- **f1** Figure 12 / Monthly view of the Oceanic Niño Index (ONI) sea surface temperature anomalies in the Niño 3.4 region　[图下方]　（标题里没有单位）
  - 来源行：Data: NOAA  \|  Graphic: Gallagher Re
- **f2** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a black horizontal rule drawn across the plot at the 0.0 tick, splitting red from blue fill |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | blue fill runs below the 0.0 line, axis ticks continue -1.0, -2.0, -3.0 |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f2 | **无** | dashed rectangle over the equatorial Pacific with a boxed label "Niño3.4 Region" |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | one index series filled red / grey / blue by ENSO phase: legend "El Niño  Neutral  La Niña" |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Figure 12: Monthly view of the Oceanic Niño Index ... \| Data: NOAA \| Graphic: Gallagher Re" under the plot |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | boxed legend with three dots sits over the plot area at lower right, above the 2015-2025 ticks |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | data are monthly but ticks read 1950, 1955, 1960 ... 2025, one per 60 points |
| `panel_background` | 绘图区带底色，不是白底 | f2 | **无** | the map panel is a light grey filled rectangle with grey landmasses, not white |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | monthly values from 1950 to 2025 form a continuous saw-toothed fill, roughly 890 points |

词表 65 项，本页出现 9 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `threshold_colored_fill` | f1 | fill switches red/grey/blue at the ±0.5 °C ENSO thresholds described in text, not at the zero line | 读数时颜色并非按符号切换，而是按 ±0.5 阈值分段，因此“Neutral”灰色段可对应 -0.4 到 +0.4 的正负两侧数值，靠颜色不能判断正负。 |
| `locator_map_inset_beside_chart` | page | a map panel sits level with the time-series plot and shares the single "Figure 12" caption | 同一图号下并存时间序列与地图两块画面，表格若只导出一块，标题与被读取的标记就会错配。 |
| `legend_label_above_marker` | f1 | the words "El Niño  Neutral  La Niña" are printed above their coloured dots, not to their right | 图例文字与色点上下对位，解析器容易把标签与色点拆成两行，导致系列名丢失。 |
| `outward_tick_dashes_no_gridlines` | f1 | each y label 3.0 ... -3.0 carries a short dash outside the axis; no grid lines cross the panel | 面板内无网格，峰值只能靠与刻度短横的水平目测对齐，抬高了 ±5% 精度的读数难度。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

最卡的是标注键。图上约 890 个月度点，x 轴只印 16 个五年刻度（每个刻度间隔含 60 个数据点），图上无任何数值标签，能用于寻址的词只有 "El Niño / Neutral / La Niña" 三个图例名加 1950…2025 的刻度年份。给定值里 1.8 出现两次、多个 -1.5/-1.6/-1.8 级别的谷底同时存在，用“系列名+五年刻度”这一组键根本无法把一行对到唯一一个月。读数本身相对宽松：刻度间距 1.0，5% 容差在 2.6 上是 ±0.13、约 6 像素，尚可目测；但 -1.6 与 -1.5 只差 0.1（约 4–5 像素），一旦寻址不唯一，误配比误读更致命。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 一类出版方 | unit_in_axis_or_title 的“缺失”对照：本页 y 轴只有 3.0…-3.0 裸数字，°C 只出现在正文而非图上 | 图头样式字段 unit_text 允许为空，并在记录里标记“单位仅存在于正文” | 新增一行：单位在图内 / 单位仅在正文 / 无单位，比较读值时的量纲错判率 |
| P6 | 一类出版方 | 新组件 threshold_colored_fill（按 ±0.5 阈值而非零线切换填色） | 面积图样式条件行增加“填色分段依据：符号 / 阈值” | 新增一行：填色按零线切换 vs 按阈值切换，检验系列名与数值正负的一致性 |
| P2 | 一类出版方 | 新组件 locator_map_inset_beside_chart（同一图号下地图面板与时序面板并列） | 版面条件行：panel_key 需容纳异质面板（时序 + 地图），并绑定同一 figure_number | 新增一行：单面板 vs 图号内含非数据地图面板，检验标题与表格的归属正确率 |
| P5 | 通用 | sparse_time_ticks 与 dense_marks_100plus 的联合上限（约 890 个月度点、16 个刻度） | 密度参数行：把每刻度承载点数（60）作为可控变量 | 新增一行：每刻度 1 点 / 12 点 / 60 点，测量单点可寻址率随密度下降的曲线 |
