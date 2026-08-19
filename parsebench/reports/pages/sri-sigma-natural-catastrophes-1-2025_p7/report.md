# sri-sigma-natural-catastrophes-1-2025_p7

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| sri-sigma-natural-catastrophes-1-2025 | `need_estimate` | 10 | 10 |

该页为 Swiss Re Institute sigma 1/2025 第7页，正文讨论2024年巨灾损失，中部为 Figure 3 的水平堆积条形图（按灾种分解2024年与历年平均保险损失）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 5 | `30-year average (1994-2023)` · `Earthquakes` | 20% | f1 | the 30-year average Earthquakes segment (leftmost dark teal) | 否 | `30-year average (1994-2023)` · `Earthquakes` |
| 2 | 20 | `30-year average (1994-2023)` · `Severe convective storms` | 10% | f1 | the 30-year average Severe convective storms segment (dark blue) | 否 | `30-year average (1994-2023)` · `Severe convective storms` |
| 3 | 9 | `15-year average (2009-2023)` · `Earthquakes` | 20% | f1 | the 5-year average Floods segment (light blue) | 否 | `5-year average (2019-2023)` · `Floods` |
| 4 | 29 | `15-year average (2009-2023)` · `Tropical cyclones` | 10% | f1 | the 15-year average Tropical cyclones segment (light green) | 否 | `15-year average (2009-2023)` · `Tropical cyclones` |
| 5 | 32 | `10-year average (2014-2023)` · `Severe convective storms` | 10% | f1 | the 10-year average Severe convective storms segment (dark blue) | 否 | `10-year average (2014-2023)` · `Severe convective storms` |
| 6 | 7 | `10-year average (2014-2023)` · `Other secondary perils` | 20% | f1 | the 15-year average Floods segment (light blue) | 否 | `15-year average (2009-2023)` · `Floods` |
| 7 | 43 | `5-year average (2019-2023)` · `Severe convective storms` | 10% | f1 | the 5-year average Severe convective storms segment (long dark blue block) | 否 | `5-year average (2019-2023)` · `Severe convective storms` |
| 8 | 55 | `2024` · `Tropical cyclones` | 10% | f1 | the 2024 Tropical cyclones segment (light green block on the bottom bar) | 否 | `2024` · `Tropical cyclones` |
| 9 | 53 | `2024` · `Severe convective storms` | 10% | f1 | the 2024 Severe convective storms segment; the number appears only in body text ('USD 53 billion') | 否 | `2024` · `Severe convective storms` |
| 10 | 20 | `2024` · `Floods` | 10% | f1 | the 30-year average Tropical cyclones segment (light green) | 否 | `30-year average (1994-2023)` · `Tropical cyclones` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 9, 7, 20

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | horizontal | 1 | 7 | 5 | 35 | 无 | 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140 |

- **f1** Figure 3 / Global insured losses from natural catastrophes in 2024 and previous year averages　[与图并排]　单位 `(USD bn, 2024 prices)`
  - 来源行：Source: Swiss Re Institute

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each average row is one bar split into coloured peril segments, bar length is the total |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | category labels '30-year average (1994-2023)' ... '2024' on the left, bars grow rightward |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: Swiss Re Institute' in small print below the legend |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two legend rows 'Earthquakes ... Severe convective storms' / 'Floods  Other secondary perils' under the axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | heading line '(USD bn, 2024 prices)'; axis ticks are bare numbers 0 to 140 |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | wildfire and earthquake segments only a few pixels wide, no room for any label |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole figure block, plot area included, sits on a pale blue tint instead of white |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | vertical rules at 0,10,...,140 cross the bars; no horizontal grid lines drawn |

词表 65 项，本页出现 8 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `stacked_segment_requires_difference` | f1 | segment values readable only as the gap between two cumulative boundaries on the 0-140 axis | 每个分段值必须由两个累计边界相减得到，误差叠加，5-10 之类的小段几乎无法在5%内读出。 |
| `figure_container_tint_box` | f1 | figure number, heading, plot, legend and source all enclosed in one full-width pale blue box | 标题与图区共处一个彩色容器且左右并列，解析器容易把标题当成独立段落而与表格脱钩。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上无任何数值标签，全部要靠像素读数：0-140 的轴宽约 495 px，10 个单位仅约 35 px，即 1 单位≈3.5 px。而堆积段必须由两条累计边界相减，误差翻倍；对 5、7、9 这类小段，5% 容差分别只有 0.25、0.35、0.45 个单位，即不到 1.6 px，远小于分段边界与描边的宽度。相比之下行标签（'30-year average (1994-2023)' 等）与图例名称清晰，两个键即可唯一定位一个段，标签层压力小得多。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | stacked_segment_requires_difference（新键）：把堆积段的可读精度按段长与轴刻度密度逐段计算 | 评分条件行中的 readable 判定，改为每个 mark 的 attainable_precision 字段 | 新增一行：堆积条形中段长 < 轴跨度 5% 的分段，是否计入 5% 容差评分 |
| P7 | 一类出版方 | unit_in_axis_or_title 与 heading 五分拆（figure_number / title / unit_text / placement=beside） | 记录字段中的标题块结构与其相对图区的位置（本页为左侧并列列） | 新增一行：单位只出现在并列标题块（'(USD bn, 2024 prices)'）时，导出表能否携带该单位 |
| P6 | 这份文档自己的习惯 | vgrid_only 与 panel_background（整幅图置于淡蓝底色框内） | 样式字段：网格方向与图区/容器底色 | 新增一行：仅竖网格 + 有色容器底的水平堆积条形，识别率与白底横网格版本的对比 |
| P3 | 这份文档自己的习惯 | figure_container_tint_box（新构造）：图号、标题、图区、图例、来源同处一个整宽色块 | 整页 markdown 导出时标题与表格的相对位置规则 | 新增一行：标题在色块内左侧并列时，是否仍能作为加粗标题与表格绑定 |
