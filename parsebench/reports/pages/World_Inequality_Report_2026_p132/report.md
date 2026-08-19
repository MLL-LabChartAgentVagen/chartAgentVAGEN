# World_Inequality_Report_2026_p132

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `need_estimate` | 9 | 9 |

本页上半部为 Figure 7.2 的多国折线图（按收入分位组的有效所得税率），下半部为两栏正文，图下有 Interpretation 与来源说明。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 9 | `United States` · `Billionaires` | 10% | f1 | the United States point at Billionaires (red line right endpoint, just above the 5%–10% band) | 否 | `United States` · `Billionaires` |
| 2 | 18 | `Netherlands` · `P80-90` | 5% | f1 | the United States point at P99–99.9, on the rise toward the red peak | 否 | `United States` · `P99–99.9` |
| 3 | 15 | `France` · `P95-99` | 5% | f1 | the France point at P95–99 (dark blue, level with the 15% grid line) | 否 | `France` · `P95–99` |
| 4 | 16 | `Spain` · `P99-99.9` | 5% | f1 | the France point at P99–99.9, the dark-blue peak just above 15% | 否 | `France` · `P99–99.9` |
| 5 | 18 | `United States` · `P99-99.9` | 5% | f1 | the Netherlands point at P80–90 (orange line approaching its plateau) | 否 | `Netherlands` · `P80–90` |
| 6 | 7 | `Brazil` · `P90-95` | 5% | f1 | the France point at P50–60 (dark blue, midway between 5% and 10%) | 否 | `France` · `P50–60` |
| 7 | 12.5 | `Netherlands` · `P50-60` | 5% | f1 | the France point at P90–95 (dark blue, between 10% and 15%) | 否 | `France` · `P90–95` |
| 8 | 15 | `France` · `P99.9-99.99` | 5% | f1 | the France point at P99.9–99.99, falling back from the peak | 否 | `France` · `P99.9–99.99` |
| 9 | 10 | `Spain` · `P99.99-P99.999` | 10% | f1 | the Brazil point at P95–99 (green line's maximum, at the 10% grid line) | 否 | `Brazil` · `P95–99` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——9 values given, 10 answered
- 模型预测的定位标签漏掉了规则实际用的标签——6 of 9 predicted key sets miss a rule label: 18, 16, 18, 7, 12.5, 10

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 5 | 16 | 77 | 无 | 0%, 5%, 10%, 15%, 20%, 25% |

- **f1** Figure 7.2. / The super-rich pay proportionately less than others / Effective income tax rates by income groups　[图上方]　单位 `Effective income tax rates by income groups  and for billionaires (% of pre–tax income)`
  - 来源行：Interpretation. This figure shows effective income tax rates by pre–tax income group and for U.S. dollar billionaires in Brazil, France, the Netherlands, Spain, and the United States. Income tax rates include only individual income taxes and equivalent levies. All values are expressed as a share of pre–tax income, defined as all national income before taxes and transfers, after pensions. P0–10 denotes the bottom 10% of the income distribution, P10–20 the next decile, etc. Sources and series: Artola et al. (2022), Bozio et al. (2024), Bozio et al. (2020), Bruil et al. (2024), Palomo et al. (2025), Saez and Zucman (2019), and Zucman (2024).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | boxed note over the plot: "99% of the population are located in the shaded area." |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | grey vertical tint spanning P0–10 through P95–99 behind the lines |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | small print below: "Interpretation. ... Sources and series: Artola et al. (2022), ..." |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | row under plot: "Brazil  France  Netherlands  Spain  United States" |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | scale phrase "(% of pre–tax income)" only in the rotated y-axis title |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | y-axis title set vertically: "Effective income tax rates by income groups and for billionaires (% of pre–tax income)" |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | category labels "P0–10" ... "Billionaires" turned about 45 degrees |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | axis reads percentile codes "P90–95", "P99.99–P99.999", explained only in the note |

词表 65 项，本页出现 8 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `unequal_bin_category_axis` | f1 | equal-width slots hold deciles then P90–95, P95–99, P99–99.9 ... and "Billionaires" | 横轴槽位宽度相同但代表的人口份额差异极大，读者不能按等距时间/等距类别方式插值，取值必须严格绑定到具体分位标签。 |
| `series_starts_late_gap` | f1 | Netherlands has no marker at P0–10; Spain's light-blue line begins near P20–30 | 某些序列在左端缺点位，若表格按类别逐行列出，需区分“缺失”与“接近0”，否则会把空槽误读成低值。 |
| `callout_explains_shading` | f1 | the boxed text names the tint: "99% of the population are located in the shaded area." | 阴影本身不是数据而是人口覆盖注释，读数时不能把带边界当作数值参考线。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

网格线只有 0%/5%/10%/15%/20%/25% 六档，档距 5 个百分点约 33 像素；要把 7 读到 ±0.35、把 12.5 读到 ±0.63，等于要在一格里分辨 1/14 到 1/8 的位置，且五条折线在 P95–99 到 P99.9–99.99 段互相交叠（France 16.5、Spain 15.5、United States 18 挤在同一片区域），标记直径本身就约等于 1 个百分点。图上完全没有数值标签（values_printed = none），因此像素读数的 5% 容差是主要瓶颈；相比之下寻址只需“序列名+分位标签”两个键，且两组名称都逐字印在图例与横轴上。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | shaded_band 与 annotation_callout 的组合：带状阴影加框内说明文字 | 样式条件行新增 band_annotation 字段（阴影起止类别 + 框内文本），并在渲染时置于绘图区上层 | 有/无“阴影带+框内注释”时，模型是否把注释框文字误当数据标签或把带边界误当参考线 |
| P1 | 通用 | 新组件 series_starts_late_gap（序列在左端缺点位） | 记录字段允许某序列在部分类别上为空，折线断开且不画标记 | 含缺失前导点的折线 vs 完整折线，导出表中空槽与 0 的区分正确率 |
| P7 | 一类出版方 | 把 unit_in_axis_or_title 与 rotated_axis_title 一并纳入标题字段化 | P7 标题记录：figure_number（"Figure 7.2."）、title、subtitle（"Effective income tax rates by income groups"）、unit_text 放入旋转的纵轴标题 | 单位仅出现在旋转纵轴标题（而非副标题）时，导出表能否恢复“%" of pre–tax income”的量纲 |
| new | 一类出版方 | 新组件 unequal_bin_category_axis（等宽槽位承载不等宽分位） | 类别轴生成器增加“分位/不等宽分组”类别名模板，并配合 rotated_x_ticks | 等距时间轴 vs 不等宽分位轴，取值是否被错误插值到相邻槽位 |
| P1 | 通用 | 按标记可达精度评分（5 档网格、无数值标签的折线） | P1 中把 readable 改为每个点的可达精度，用网格档距/标记直径估算 | 档距 5 个百分点、77 个标记的折线图上，容差 5% 与 10% 下的通过率对比 |
