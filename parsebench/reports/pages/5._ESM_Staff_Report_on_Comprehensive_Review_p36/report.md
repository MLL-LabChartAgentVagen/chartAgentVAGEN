# 5._ESM_Staff_Report_on_Comprehensive_Review_p36

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 5._ESM_Staff_Report_on_Comprehensive_Review | `need_estimate` | 7 | 7 |

本页为ESM报告第36页，含正文与一幅折线图 Figure 7「ESM remaining lending capacity」，两条曲线对比现行条约与2024年批准修订条约下的剩余贷款能力（2012–2069）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 422 | `2024` · `Under Current Treaty` | 5% | f1 | the 2024 point of the pre-branch / Under Current Treaty line (also cited in text as April 2024) | 否 | `ESM remaining lending capacity` · `Under Current Treaty` · `2024` |
| 2 | 445 | `2036` · `Under Current Treaty` | 5% | f1 | a point on the yellow Under Current Treaty line around 2044-2048, read between the 450 and 400 gridlines | 否 | `ESM remaining lending capacity` · `Under Current Treaty` · `2044` |
| 3 | 377 | `2036` · `Ratification of Revised Treaty in 2024` | 5% | f1 | a point on the blue Ratification of Revised Treaty in 2024 line around 2036-2040 | 否 | `ESM remaining lending capacity` · `Ratification of Revised Treaty in 2024` · `2036` |
| 4 | 475 | `2048` · `Under Current Treaty` | 5% | f1 | a point on the yellow Under Current Treaty line around 2056, between the 450 and 500 gridlines | 否 | `ESM remaining lending capacity` · `Under Current Treaty` · `2056` |
| 5 | 398 | `2048` · `Ratification of Revised Treaty in 2024` | 5% | f1 | a point on the blue Ratification of Revised Treaty in 2024 line around 2048, just below the 400 gridline | 否 | `ESM remaining lending capacity` · `Ratification of Revised Treaty in 2024` · `2048` |
| 6 | 500 | `2060` · `Under Current Treaty` | 1% | f1 | the plateau of the yellow Under Current Treaty line from about 2060 onward, on the top tick | 否 | `ESM remaining lending capacity` · `Under Current Treaty` · `2060` |
| 7 | 432 | `2060` · `Ratification of Revised Treaty in 2024` | 5% | f1 | the plateau of the blue Ratification of Revised Treaty in 2024 line from 2060 onward (text: "projected until 2060 (€432 billion)") | 否 | `ESM remaining lending capacity` · `Ratification of Revised Treaty in 2024` · `2060` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——7 values given, 8 answered
- 模型预测的定位标签漏掉了规则实际用的标签——2 of 7 predicted key sets miss a rule label: 445, 475

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 2 | 15 | 116 | 无 | 250, 300, 350, 400, 450, 500 |
| f2 | `other · not a figure` | na | 0 | 0 | 0 | 0 | 无 | （不画值轴） |

- **f1** Figure 7. / ESM remaining lending capacity　[图上方]　单位 `(in € billion)`
  - 来源行：Source: ESM
- **f2** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | grey tinted band from 2024 to the right edge marking the projection window |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest y tick is "250", no break glyph on axis |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: ESM" and "Note: The maximum lending volume of the ESM is €500 billion..." below plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | "Under Current Treaty" and "Ratification of Revised Treaty in 2024" swatches in a row under the axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | heading line "(in € billion)"; y axis shows bare 250...500 |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | body text ends "the facility is extended by then.41" with footnote 41 at page bottom |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | ticks every four years "2012 2016 2020 2024..." while the lines bend at yearly points |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 300, 350, 400, 450, 500; no vertical rules |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | two series over roughly 58 annual points each, ~116 plotted points |

词表 65 项，本页出现 9 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `vertical_jump_connector` | f1 | a dotted vertical segment at 2024 links ~422 down to ~353 where the revised-treaty series starts | 该虚线竖段不是数据点，而是标示两情形在2024年的€68 billion缺口；读值时须区分422（现行）与353（修订）两个端点。 |
| `series_starts_later_than_axis` | f1 | the blue "Ratification of Revised Treaty in 2024" branch only exists from 2024 onward; before 2024 one shared history line | 2024年之前只有一条历史曲线，表格若按两系列列出会在早期年份产生空值，定位某年数值需先判断该年是否已分叉。 |
| `axis_ends_at_series_ceiling` | f1 | the yellow line flattens exactly on the top tick "500" after 2060 | 曲线与顶端刻度重合，读取500时无法与轴线区分，需依赖注释"maximum lending volume of the ESM is €500 billion"确认。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标注，全部七个数都必须靠像素对刻度反推。y轴自250起、每50一格约60像素，即1 px≈0.85 €bn，而5%容差在430附近约21 €bn，看似宽松；但真正的障碍是横轴：刻度每四年一格（2012、2016…2068），而曲线是逐年折点，要定位「2044的445」或「2048的398」必须在两刻度间内插约1/4格宽度，而该区段曲线斜率约每四年5–10 €bn，选错一年即偏移接近容差上限。加之两线在2060后都变成水平且黄线正压在500刻度线上，读数与轴线难以区分。相比之下行标签只需系列名+年份两个键，注释与图题都是可检索的粗体文本，反而不是瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | shaded_band（预测期灰底）与新提出的 vertical_jump_connector | 折线图样式条件行：新增「预测区间背景色块」开关与「同一横轴位置的情形分叉虚线」标记 | 有/无预测底色与分叉连接线时，模型对分叉年份（2024）两个不同端点值的归属正确率 |
| P1 | 通用 | sparse_time_ticks（刻度四年一格、折点逐年） | 时间轴刻度密度字段：刻度间隔与数据点间隔解耦，记录 tick_every=4 | 刻度间隔=1 / 2 / 4 年三档下，非刻度年份取值的5%命中率 |
| P6 | 一类出版方 | axis_starts_above_zero（y轴自250起） | 数值轴范围字段：允许 axis_min 大于0且不画断轴符号 | 轴起点为0与非0时，读值偏差分布对比 |
| P7 | 通用 | 图题四段拆分（Figure 7. / ESM remaining lending capacity / (in € billion)）与 unit_in_axis_or_title | 标题记录字段：number、title、unit_text 三行独立，placement=above | 单位仅存于标题行时，导出表格是否保留€ billion量纲的比例 |
| new | 一类出版方 | 新增 series_starts_later_than_axis（系列在轴中段才出现） | 系列记录字段：为每个系列增加起止类别范围 | 系列覆盖全轴 vs 部分轴时，早期年份空值处理的正确率 |
