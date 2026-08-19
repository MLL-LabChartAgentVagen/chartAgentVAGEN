# 9f653ca1-en_p31

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 9f653ca1-en | `need_estimate` | 10 | 10 |

本页为 OECD 经济展望的 Figure 1.17，含四个面板（A 世界及分组GDP增速折线、B 对全球增长贡献的堆叠柱、C 全球GDP增速三轮预测折线、D G20总体通胀三轮预测折线），下附注释、来源与 StatLink 链接及一段正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 3.3 | `World` · `2023` | 20% | f1 | the 2025 World point in Panel A (line sits just above the 3 gridline) | 否 | `A. GDP growth` · `World` · `2025` |
| 2 | 1.7 | `Advanced economies` · `2025` | 30% | f1 | the 2027 Advanced economies point in Panel A, slightly above the 1.6 level | 否 | `A. GDP growth` · `Advanced economies` · `2027` |
| 3 | 4.4 | `Emerging-market economies` · `2024` | 20% | f1 | the 2023 Emerging-market economies peak in Panel A, between 4 and 5 ticks | 否 | `A. GDP growth` · `Emerging-market economies` · `2023` |
| 4 | 4.0 | `Emerging-market economies` · `2027` | 20% | f1 | the 2022 Emerging-market economies point in Panel A at the 4 gridline | 否 | `A. GDP growth` · `Emerging-market economies` · `2022` |
| 5 | 1.8 | `Emerging Asia` · `2024` | 20% | f1 | the 2024 Emerging Asia segment in Panel B (stack from ~0.5 to ~2.3 % pts) | 否 | `B. Contributions to global growth` · `Emerging Asia` · `2024` |
| 6 | 0.4 | `OECD Europe` · `2025` | 100% | f1 | the 2024 Canada and United States segment in Panel B (blue base band) | 否 | `B. Contributions to global growth` · `Canada and United States` · `2024` |
| 7 | 0.4 | `Canada and United States` · `2026` | 100% | f1 | the 2027 Canada and United States segment in Panel B (blue base band) | 否 | `B. Contributions to global growth` · `Canada and United States` · `2027` |
| 8 | 0.5 | `Rest of the world` · `2027` | 80% | f1 | the 2024 Rest of the world segment in Panel B (orange top band, ~2.7 to ~3.2) | 否 | `B. Contributions to global growth` · `Rest of the world` · `2024` |
| 9 | 0.2 | `Latin America` · `2024` | 150% | f1 | the 2025 OECD Europe segment in Panel B (grey band just below the orange top) | 否 | `B. Contributions to global growth` · `OECD Europe` · `2025` |
| 10 | 0.1 | `OECD Asia-Pacific` · `2025` | 250% | f1 | the 2026 Latin America segment in Panel B (thin red band above the blue base) | 否 | `B. Contributions to global growth` · `Latin America` · `2026` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——9 of 10 predicted key sets miss a rule label: 3.3, 1.7, 4.4, 4.0, 0.4, 0.4
- 有图超过 100 个图元，组件清单里没有 dense_marks_100plus——densest figure has 106 marks
- 系列数与系列名个数不一致——f1: series=3, 12 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 4 | 3 | 6 | 106 | 无 | 0, 1, 2, 3, 4, 5, 6, 7 |

- **f1** Figure 1.17 / Global growth is projected to weaken before recovering gradually　[图上方]　（标题里没有单位）
  - 来源行：Source: OECD Economic Outlook 118 database; OECD Economic Outlook 117 database; OECD Interim Economic Outlook 118 database; and OECD calculations.  ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​ ​

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | Panel B bars stacked from Canada and United States up to Rest of the world, totals near 3.0-3.2 |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | Panel A has a grey tinted band from mid-2024 across 2025-2027 marking projections |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | Panel A 0-7, Panel B 0.0-4.5, Panel C 2.50-3.50, Panel D 2.0-4.5 |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | Panel C y axis lowest tick is 2.50; Panel D lowest tick is 2.0 |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | Four labelled panels A-D arranged 2x2 under one figure number |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: In Panel A, 'Advanced economies' include the OECD member countries...' and 'Source: OECD Economic Outlook 118 database;' |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | Panel A, C and D legends drawn over the plot area; Panel B legend in top strip of plot |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | Each of the four panels carries its own legend box with its own series names |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | Panel B is a stacked bar chart while Panels A, C, D are line charts |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | 'A. GDP growth', 'B. Contributions to global growth', 'C. Global GDP growth', 'D. G20 headline inflation' above each panel |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | 'StatLink' logo with 'https://stat.link/j3hlps' under the figure |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | Bare ticks 0-7 with only '%'; Panel B '% pts'; Panel C 'Y-o-y % changes' |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | '%' above top tick in Panel A and D, '% pts' in Panel B, 'Y-o-y % changes' in Panel C |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | Panels C and D plot quarterly points but ticks read only 2025, 2026, 2027 |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | Panel A plot area right portion carries a grey tint over 2025-2027 |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | Panels A, C, D show faint horizontal rules at ticks, no vertical rules |

词表 65 项，本页出现 16 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `truncated_series_ends_midway` | f1 | In Panels C and D the 'June 2025 projections' red line stops in early 2026 while others run to 2027 | 读值时必须确认某一时点是否存在该系列的点，否则会把三条线在同一横坐标全部填值，产生虚假数据。 |
| `overlapping_identical_series` | f1 | In Panel D the green and blue lines coincide from 2026 onward, drawn as one visible trace | 同一像素轨迹对应两个系列，单点读数无法区分September与December预测，需按重合处理。 |
| `stack_segment_gap_between_bars` | f1 | Panel B bars separated by thin white gaps with no axis line between year groups | 分段极薄（如0.1-0.2 % pts）时段边界与柱间空隙易混淆，影响薄层取值。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

最难在于读数精度：全图无任何数值标注，Panel B 刻度间距为 0.5 % pts，而待查值中 0.4、0.2、0.1 这类薄层只有约 4-8 像素高，5% 容差意味着 0.1 需读到 ±0.005 % pts，远超像素分辨；Latin America 与 OECD Asia-Pacific 的窄带甚至与柱间白缝混淆。Panel A 刻度间距 1 个百分点，要把 3.3 与 1.7 读到 ±0.17 与 ±0.09 也接近像素极限；Panel C/D 起点在 2.50 与 2.0 之上，进一步压缩了纵向可比性。标签方面每个值只需 3 个键（面板名+系列名+年份），相对容易。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | per_panel_axis_range 与 panel_key（面板维度进入行键） | 记录字段中为每个面板单独存轴范围与刻度，导出表以 panel_name 作为行键前缀 | 四面板不同轴起点（0/0.0/2.50/2.0）时，跨面板读值错配率对比统一轴的基线 |
| P1 | 一类出版方 | 薄段堆叠（如 0.1 % pts 段在 0.5 刻距下）的最小可读段高约束 | 条件行加入 min_segment_fraction，样式字段控制堆叠段最小像素高 | 段高<2% 图高的堆叠段，取值容差达标率 vs 段高>5% 的对照 |
| P3 | 一类出版方 | per_panel_legend 与 legend_inside_plot 组合 | 样式字段 legend_placement 允许每面板独立且置于绘图区内 | 每面板独立图内图例 vs 全图共享图例时，系列名归属正确率 |
| new | 通用 | new_components 中的 truncated_series_ends_midway（系列提前终止） | 数据记录允许系列在时间轴中途结束，不补插值 | 存在提前终止系列时，末端后时点被虚构填值的比例 |
| P7 | 通用 | heading 五段拆分（number/title/panel titles/unit 位置） | 标题记录字段：figure_number、title、panel_title、unit_text 及其放置位置（轴上方裸单位 '%'、'% pts'） | 单位仅以裸符号置于顶刻度上方时，单位识别率 vs 单位写入轴标题 |
