# natural-catastrophe-and-climate-report-2023_p54

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| natural-catastrophe-and-climate-report-2023 | `need_estimate` | 10 | 10 |

这是一份灾害年报的APAC区域回顾页，含Figure 36（亚洲与大洋洲两幅事件标注地图）与Figure 37（年度损失分组柱状图、累计损失折线图及四个大数字统计面板）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 410 | `2011` · `Economic Loss` | 10% | f2 | the light-blue Economic Loss line in "Aggregate APAC Weather / Climate Losses", around 2006-2007; between the $500B tick and the origin | 否 | `Aggregate APAC Weather / Climate Losses` · `Economic Loss` · `USD billion` |
| 2 | 100 | `2011` · `Insured Loss` | 10% | f2 | the tall dark Insured Loss bar at 2011 in "Annual APAC Natural Peril Losses", reaching the $100B gridline | 否 | `Annual APAC Natural Peril Losses` · `Insured Loss` · `2011` |
| 3 | 265 | `2008` · `Economic Loss` | 10% | f2 | the light Economic Loss bar at 2008, the second tallest bar in the left panel | 否 | `Annual APAC Natural Peril Losses` · `Economic Loss` · `2008` |
| 4 | 75 | `2023` · `Economic Loss` | 30% | f2 | a short light Economic Loss bar in the mid-2000s (about 2006) in the left panel; exact year not tick-labelled | 否 | `Annual APAC Natural Peril Losses` · `Economic Loss` · `2005` |
| 5 | 12 | `2023` · `Insured Loss` | 30% | f2 | one of the very short dark Insured Loss bars in the early 2000s; only ~1 pixel tall, year not resolvable | 否 | `Annual APAC Natural Peril Losses` · `Insured Loss` · `2000` |
| 6 | 2102 | `2023` · `Economic Loss` | 1% | f2 | the printed endpoint label "$2,102B" on the Economic Loss line of the aggregate panel | 是 | `Aggregate APAC Weather / Climate Losses` · `Economic Loss` |
| 7 | 243 | `2023` · `Insured Loss` | 1% | f2 | the printed endpoint label "$243B" on the Insured Loss line of the aggregate panel | 是 | `Aggregate APAC Weather / Climate Losses` · `Insured Loss` |
| 8 | 1900 | `2020` · `Economic Loss` | 10% | f2 | the Economic Loss line in the aggregate panel near 2020, just below the $2,000B gridline | 否 | `Aggregate APAC Weather / Climate Losses` · `Economic Loss` · `2020` |
| 9 | 220 | `2020` · `Insured Loss` | 10% | f2 | the dark Insured Loss line in the aggregate panel near 2021-2022, below its $243B endpoint | 否 | `Aggregate APAC Weather / Climate Losses` · `Insured Loss` · `2020` |
| 10 | 1300 | `2015` · `Economic Loss` | 10% | f2 | the Economic Loss line in the aggregate panel around 2014-2015, between the $1,000B and $1,500B gridlines | 否 | `Aggregate APAC Weather / Climate Losses` · `Economic Loss` · `2015` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 10 predicted key sets miss a rule label: 410, 75, 12, 2102, 243

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `map` | na | 2 | 1 | 9 | 9 | 部分 | （不画值轴） |
| f2 | `compound` | vertical | 3 | 2 | 24 | 100 | 部分 | $600B, $500B, $400B, $300B, $200B, $100B; $2,500B, $2,000B, $1,500B, $1,000B, $500B |

- **f1** Figure 36 / Map of notable Asia-Pacific (APAC) events in 2023　[图下方]　（标题里没有单位）
  - 来源行：Data and Graphic: Gallagher Re
- **f2** Figure 37 / Asia-Pacific (APAC) natural catastrophe statistics　[图下方]　单位 `USD billion`
  - 来源行：Data and Graphic: Gallagher Re

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f2 | 有 | left panel: a light "Economic Loss" bar and a dark "Insured Loss" bar side by side per year |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | orange event labels with leader lines over the maps, e.g. "Typhoon Doksuri ... Eco: USD18.5bn / Ins: 1.7bn" |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f2 | 有 | left axis tops at "$600B", right panel axis tops at "$2,500B" |
| `shared_legend` | 跨面板共享图例 | f2 | 有 | one legend "Economic Loss  Insured Loss" below the panels, colours reused by both bar and line panels |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | "Figure 36: Map of notable Asia-Pacific (APAC) events" and "Figure 37: Asia-Pacific (APAC) natural catastrophe statistics" both captioned |
| `source_note_lines` | source / note 行在图下方 | page | 有 | small print under each figure: "\| Data and Graphic: Gallagher Re" |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | the legend row sits under the plot area of the loss charts |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f2 | 有 | Figure 37 holds a bar panel, a two-line panel and a four big-number statistics panel |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | "Asia" above the left map, "Oceania" above the right map |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f2 | 有 | "Annual APAC Natural Peril Losses", "Aggregate APAC Weather / Climate Losses", "Notable Statistics in 2023" each above its panel |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | axis title "USD billion" carries the scale; no unit word in series names "Economic Loss"/"Insured Loss" |
| `rotated_axis_title` | 轴标题竖排 | f2 | 有 | "USD billion" set vertically along the left axis of both loss panels |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | "$2,102B" and "$243B" printed beyond the right ends of the two lines |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f2 | 有 | yearly bars and points but ticks only at 2000, 2005, 2010, 2015, 2020 |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | faint horizontal rules at each $100B / $500B tick, no vertical rules |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f2 | **无** | 24 years x 2 bars plus two 24-point lines, about 96 data marks in one figure |

词表 65 项，本页出现 15 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `kpi_big_number_panel` | f2 | "Notable Statistics in 2023": 5, 17, 744.8, 2 in huge type over wrapped explanatory captions | 这些数字没有任何坐标轴或标记，只能作为“标签+数值”对读取，表格需要把长说明文字当作行名。 |
| `values_only_in_annotation_text` | f1 | map values appear only inside callout prose: "Economic Loss: USD3.1bn / Insured Loss: USD1.9bn" | 地图上的量值不靠标记大小编码，取值完全依赖注释文本的解析，行名是事件名。 |
| `locator_labels_not_data` | f1 | small hollow circles labelled "Beijing", "Tokyo", "Perth", "Christchurch" alongside the orange event dots | 页面上大量圆点不是数据点，容易与9个橙色事件标记混淆，导致误读标记数量与归属。 |
| `caption_carries_number_title_and_credit` | page | one line below each figure: "Figure 37: Asia-Pacific (APAC) natural catastrophe statistics \| Data and Graphic: Gallagher Re" | 图号、标题与出处挤在图下同一行，标题不在表格上方，取值时的上下文需从该行回补。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

最卡的是读数。左面板刻度间距为$100B、全轴仅约300像素高，一格约55像素，则12这个保险损失值容许误差5%只有0.6B，约合0.3像素，深蓝小柱几乎与基线重合，根本无法读到5%以内；75与100两个值只差不到一格的一半，还要在24个未标注刻度的年份中定位。右面板刻度间距为$500B，5%容差对410只有±20B，即约3像素，1300与1900同样落在两条网格线之间，只有$2,102B与$243B是印上去的。相比之下行名（面板名+系列名+年份）虽然要三个键，但都能在页面上找到原文。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P4 | 一类出版方 | 新增 kpi_big_number_panel（大数字统计面板）作为可生成的面板类型 | 图形族权重向量与面板类型字段：允许同一图号下混入无坐标轴的数字面板，记录字段用长说明文字作为行名 | 含/不含无轴KPI面板时，整页数值命中率对比 |
| P2 | 通用 | 把 heterogeneous_panel_types 与 per_panel_axis_range 一起纳入 panel_key | 条件行中的 panel 维度：同图号三个面板（柱/线/KPI）各自独立轴范围与标题 | panel_key 是否进入寻址键：跨面板同名系列 Economic Loss 的混淆率 |
| new | 一类出版方 | 新增 values_only_in_annotation_text（地图注释内嵌数值） | 地图族记录字段：事件名为行名，Eco/Ins 数值来自注释文本而非标记几何 | 地图注释是否导出为表：Figure 36 九个事件数值的可检索率 |
| P6 | 通用 | 把 sparse_time_ticks 与刻度格式（$600B 这类带货币与量级后缀）列入样式维度 | 样式字段的刻度格式与刻度密度：24个年份仅5个刻度，刻度文本含 $ 与 B | 稀疏时间刻度下按年寻址的正确率与刻度格式解析失败率 |
| P7 | 这份文档自己的习惯 | 标题块拆分为图号/标题/出处一行置于图下（caption_carries_number_title_and_credit） | 标题字段与 placement 取值：placement=below，且 unit_text 只出现在旋转轴标题 "USD billion" | 标题位于表下且与出处同行时，上下文键匹配率 |
