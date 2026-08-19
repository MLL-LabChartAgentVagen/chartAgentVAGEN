# sigma-1-2021-en_p9

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| sigma-1-2021-en | `need_estimate` | 10 | 10 |

该页上部为 Figure 3「Timeline of events against trends of various climate drivers」的双轴复合图（SAM 柱 + ENSO/IOD 折线 + 三条事件阴影带），下部为 Implications for insurance 正文及左侧蓝色边注。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 2.8 | `Jan 2019` · `SAM` | 10% | f1 | the tallest positive SAM bar near the start of the series, just after Jan 2019 | 否 | `SAM` · `Jan 2019` |
| 2 | 0.3 | `Jan 2019` · `ENSO` | 20% | f1 | a short positive SAM bar just above the zero line shortly after Jan 2020 | 否 | `SAM` · `Jan 2020` |
| 3 | 0.0 | `Jan 2019` · `IOD` | 1% | f1 | an ENSO line point sitting on the right-axis 0.0 gridline around Jan 2020; several points share this level | 否 | `ENSO` · `Jan 2020` |
| 4 | -0.1 | `May 2019` · `SAM` | 20% | f1 | the very short SAM bar dipping just below the zero line between Jan 2020 and May 2020 | 否 | `SAM` · `Jan 2020` |
| 5 | 2.0 | `Oct 2019` · `IOD` | 5% | f1 | the positive SAM bar reaching about the left-axis 2 gridline near Sep 2019 | 否 | `SAM` · `Sep 2019` |
| 6 | -4.5 | `Nov 2019` · `SAM` | 5% | f1 | the deepest negative SAM bar, between Sep 2019 and Jan 2020, ending between −4 and −5 | 否 | `SAM` · `Sep 2019` |
| 7 | -0.3 | `Feb 2020` · `SAM` | 20% | f1 | an IOD line point below the right-axis 0.0 line; cannot be pinned to one month, the dark-grey line crosses this level repeatedly | 否 | `IOD` |
| 8 | 0.3 | `Feb 2020` · `ENSO` | 20% | f1 | an ENSO line point between the right-axis 0.0 and 0.5 gridlines; the cyan line sits at this level over many months | 否 | `ENSO` |
| 9 | -0.2 | `Feb 2020` · `IOD` | 20% | f1 | an IOD (or ENSO) line point just under the right-axis 0.0 gridline; the two lines overlap there, so the series is ambiguous | 否 | `IOD` |
| 10 | 0.3 | `May 2020` · `ENSO` | 20% | f1 | a second reading at the same level on the right axis — either the ENSO line at another month or a short positive SAM bar; not uniquely placeable | 否 | `ENSO` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——9 of 10 predicted key sets miss a rule label: 0.3, 0.0, -0.1, 2.0, -4.5, -0.3

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 6 | 19 | 181 | 无 | left (SAM): 7, 6, 5, 4, 3, 2, 1, 0, −1, −2, −3, −4, −5; right (ENSO/IOD): 2.5, 2.0, 1.5, 1.0, 0.5, 0.0, −0.5, −1.0, −1.5 |

- **f1** Figure 3 / Timeline of events against trends of various climate drivers　[图上方]　（标题里没有单位）
  - 来源行：Sources: Bureau of Meteorology (for IOD and ENSO data), British Antarctic Survey (for SAM data), Insurance Council of Australia (for loss numbers), Swiss Re Institute

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | left axis labelled SAM with ticks 7 to −5, right axis labelled ENSO/IOD with 2.5 to −1.5 |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | blue SAM bars with cyan ENSO and dark-grey IOD lines drawn over the same panel |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | bars extend below the 0 gridline down past −4 on the left SAM axis |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | grey, green and yellow vertical tints span Jun 2019–Mar 2020, Jan 20 2020 and Feb 7–10 2020 |
| `right_side_y_axis` | 唯一的值轴画在右侧 | f1 | **无** | the ENSO/IOD scale 2.5...−1.5 is drawn only on the right edge of the plot |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Sources: Bureau of Meteorology (for IOD and ENSO data)...Swiss Re Institute' in small print below |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Climate index: SAM / ENSO / IOD' and 'Events:' swatch block sit under the time axis |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f1 | 有 | the 'Events:' swatch column sits to the right of 'Climate index:' in the same legend band |
| `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | f1 | **无** | legend entries read 'Bushfires: AUD 2.3 bn', 'ACT Hail: AUD 1.66 bn', 'East Coast Flood: AUD 0.97 bn' |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'SAM' set vertically at the left axis, 'ENSO/IOD' set vertically at the right axis |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | superscript 6 and 7 in body text keyed to footnotes 'Severe weather in a changing climate' and 'Insurance Council of Australia.' |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | ticks read Jan 2019, May 2019, Sep 2019, Jan 2020, May 2020 while bars appear roughly monthly |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at each left-axis tick, no vertical grid lines drawn |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | two continuous lines over ~19 months plus ~18 bars, well over 100 plotted points |

词表 65 项，本页出现 14 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `event_band_legend_with_date_and_loss` | f1 | each event swatch carries a date line plus a loss figure: 'Jan 20, 2020 / ACT Hail: AUD 1.66 bn' | 这些金额（2.3/1.66/0.97 bn）不在任何坐标轴上，只能从图例两行文字读出，表格必须把日期行和金额行一起作为行名，否则无法定位。 |
| `index_axis_without_unit` | f1 | axis titles are index names 'SAM' and 'ENSO/IOD'; no unit phrase anywhere on the figure | 数值是无量纲指数，读数时必须靠轴标题区分左右两套刻度（1 单位 vs 0.5 单位），否则同一个 0.3 会被指到错误的轴。 |
| `bar_and_line_share_time_axis_different_scales` | f1 | SAM bars read against left 1-unit grid, ENSO/IOD lines against right 0.5-unit grid, same x positions | 同一时间位置上有三个可读数，取值 0.3、−0.2 等必须先判定属于柱还是折线，行键需同时含系列名与月份。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

取值精度是最硬的门槛：左轴每格 1 个单位（7 到 −5），右轴每格 0.5 个单位（2.5 到 −1.5），在 150 dpi 下一格约 30 px；而待评分值里有 0.3、0.0、−0.1、−0.2 这类接近零的小数，5% 容差分别只有 ±0.015、±0.005、±0.01，靠像素读数根本达不到；图上没有任何数值标签（values_printed = none）。其次是标签（step 3）：柱与折线共用同一时间轴，x 轴只标 5 个月份，一个 0.3 需要同时给出系列名（SAM/ENSO/IOD）和月份才能唯一定位，而这些月份在页面上并未逐一印出。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | dual_axis 与 right_side_y_axis 的组合（左右刻度间距不同：1 vs 0.5） | 图表条件行中新增「双轴且两轴刻度步长不同」的样式字段，并在记录里为每个系列标注其所属轴 | 单轴 vs 双轴（同步长）vs 双轴（异步长）三档，比较取值被指到错误轴的比例 |
| P7 | 一类出版方 | 新提出的 event_band_legend_with_date_and_loss（阴影带作为图例系列并在图例中携带日期与金额） | 图例样式字段增加「band 型图例项」，并允许图例项文本为两行（日期行 + 数值行） | 事件带只有色块 vs 带日期 vs 带日期+金额，检验 markdown 导出能否保留轴外数值 |
| P3 | 通用 | sparse_time_ticks（月度柱但只标 Jan 2019/May 2019/Sep 2019/Jan 2020/May 2020） | 时间轴刻度密度字段：每 N 个数据点标一个刻度 | 刻度=数据点 vs 每 4 点一刻度，测量行键缺失月份时的定位失败率 |
| P1 | 通用 | P1 式的逐标记可达精度（本图无数值标签，柱与折线精度不同） | 把 readable 从布尔门槛改为按标记类型给出容差：柱端点较易读，密集折线点较难 | 柱标记 vs 折线标记的可达容差分档，替代统一 5% 门槛 |
| P4 | 通用 | mixed_marks（柱+两条折线共用一个面板） | 面板生成器允许在同一面板混合 bar 与 line 系列，并各自绑定左/右轴 | 纯柱、纯线、柱线混合三档，比较系列归属判断错误率 |
