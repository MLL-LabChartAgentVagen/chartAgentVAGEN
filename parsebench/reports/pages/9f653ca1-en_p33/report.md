# 9f653ca1-en_p33

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 9f653ca1-en | `need_estimate` | 7 | 7 |

该页为OECD经济展望正文页，中部为Figure 1.18（A、B两个面板的堆积柱状图，含三角形标记序列），下方有Note、Source与StatLink数据链接。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 4.5 | `World, %` · `2001-09` | 5% | f1 | Panel A, top of the 2001-09 stack (total contributions), essentially coinciding with the ▲ World, % marker | 否 | `A. Contributions to global trade growth` · `2001-09` · `World, %` |
| 2 | 0.6 | `North America` · `2011-14` | 80% | f1 | Panel B, the ▲ World, % marker at 2011-14, sitting just under the 0.5 tick line height | 否 | `B. Contributions to global current account balance` · `2011-14` · `World, %` |
| 3 | 0.4 | `China` · `2015-19` | 80% | f1 | Panel B, the ▲ World, % marker at 2022-25, just below 0.5 | 否 | `B. Contributions to global current account balance` · `2022-25` · `World, %` |
| 4 | 0.9 | `Europe` · `2022-25` | 20% | f1 | Panel A, the purple China segment of the 2001-09 bar (from ~0.4 to ~1.25); assignment uncertain, no labels printed | 否 | `A. Contributions to global trade growth` · `2001-09` · `China` |
| 5 | 0.4 | `South-East Asian economies` · `2026-27` | 50% | f1 | Panel B, the ▲ World, % marker at 2026-27, near 0.45 | 否 | `B. Contributions to global current account balance` · `2026-27` · `World, %` |
| 6 | 0.7 | `Rest of the World` · `2011-14` | 20% | f1 | Panel A, the dark-red North America segment of the 2015-19 bar (0 to ~0.7); assignment uncertain | 否 | `A. Contributions to global trade growth` · `2015-19` · `North America` |
| 7 | -0.1 | `India` · `2026-27` | 200% | f1 | Panel B, a thin negative segment (orange India / green Other advanced economies band) below the 0.0 line; too thin to attribute with confidence | 否 | `B. Contributions to global current account balance` · `India` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——6 of 7 predicted key sets miss a rule label: 0.6, 0.4, 0.9, 0.4, 0.7, -0.1

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 2 | 8 | 5 | 80 | 无 | Panel A: 5, 4, 3, 2, 1, 0; Panel B: 1.5, 1.0, 0.5, 0.0, -0.5, -1.0, -1.5 |

- **f1** Figure 1.18. / Trade patterns are evolving with emerging markets becoming a key driver of growth / Averages of annual growth　[图上方]　单位 `% pts \| % of nominal World GDP`
  - 来源行：Source: OECD Economic Outlook 118 database; and OECD calculations.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each period bar is built of seven coloured segments (North America, China, Europe, ... Rest of the World) |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | black triangle markers sit on top of / inside the stacked bars in both panels |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a bold black horizontal rule drawn across Panel B at the 0.0 tick |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | Panel B ticks run -1.5 to 1.5 and dark-red segments extend below 0.0 |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | Panel A axis 0 to 5 "% pts"; Panel B axis -1.5 to 1.5 "% of nominal World GDP" |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend entry "▲ World, %" drawn as a single triangle at each category position, same axis as bars |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one legend row spanning both panels above them; no legend inside either panel |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | two panels, same stacked-bar form, same 5 periods and same 7 region series |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: North America includes Canada, Mexico and the United States..." and "Source: OECD Economic Outlook 118 database..." |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | legend swatches sit between the panel titles and the plot areas |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | "A. Contributions to global trade growth" and "B. Contributions to global current account balance" above each panel |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | "StatLink  https://stat.link/mhq1ks" printed under the note and source lines |
| `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | f1 | **无** | legend entry reads "World, %" while the bars are contributions in % pts |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | "% pts" over Panel A axis and "% of nominal World GDP" over Panel B axis; ticks bare numbers |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "% pts" printed above the top tick "5"; "% of nominal World GDP" above "1.5" |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | category ticks are multi-year spans "2001-09", "2011-14", "2022-25", not single years |

词表 65 项，本页出现 16 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `diverging_stacked_bar` | f1 | Panel B bars have segments above and below the 0.0 line within one category slot | 同一柱内正负段各自从零线向两侧堆叠，段值不能用柱顶高度累减，必须分别测量正侧与负侧的累积边界。 |
| `marker_series_unit_differs_from_bars` | f1 | "World, %" triangle is a growth rate while bars are "% pts" contributions, on one axis | 三角标记与柱段共用一条刻度但含义/单位不同，读数时必须区分它是总量还是另一单位的序列。 |
| `legend_entries_split_over_two_panels` | f1 | North America/China/Europe/South-East Asian swatches sit over Panel A, Other advanced/India/Rest of the World over Panel B | 图例在版面上被两面板分割，容易被误读成各面板专属图例，从而错配颜色到序列。 |
| `segment_reaching_axis_bound` | f1 | Panel B 2001-09 dark-red segment runs from 0.0 down to the bottom tick -1.5 | 该段恰抵坐标下界，无法判断是否被截断，负向读数存在下限不确定性。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

数值全部未标注，必须靠像素对刻度换算。面板A刻度间距为1 % pt，面板B为0.5，在150 dpi下1个刻度间隔约40 px，因此0.4这样的值5%容差仅±0.02，相当于不足1 px；India、Other advanced economies等薄段在面板B里只有几个像素高，-0.1的正负归属都难以确定。面板B还是零线双向堆叠，段值需要用两个累积边界相减，误差叠加后基本无法落在容差内。相比之下寻址只需“面板标题+期间+序列名”三个键，面板标题已是加粗式小标题，风险明显小于读数。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 diverging_stacked_bar（零线双向堆叠） | 条件行中新增“堆叠方向”维度，样式字段允许同一柱内正负段分别从零线堆叠 | 正负混合堆叠 vs 纯正向堆叠：对比薄段取值的可复原率 |
| P6 | 一类出版方 | 新组件 marker_series_unit_differs_from_bars（三角标记序列与柱段单位不同） | 记录字段中为标记序列单独存单位，图例名允许含单位（如“World, %”） | 标记序列单位与柱段一致/不一致两行，检验是否把标记误当合计 |
| P2 | 通用 | 组件 per_panel_axis_range 与面板键 | 表格键中加入 panel_key，使用“A. …”“B. …”原文面板标题作为行前缀 | 含面板键 vs 不含面板键：两面板同期间同序列值的混淆率 |
| P7 | 通用 | 标题五分拆（含 axis_title_above_axis 的单位位置） | 标题字段拆为 figure_number/title/subtitle/unit，单位可置于顶刻度上方 | 单位在轴顶上方 vs 在轴标题处：单位可恢复率 |
| P1 | 通用 | 薄段可读性按每个mark给出可达精度 | 评测把 readable 从布尔门改为按段高像素给出容差 | 段高<5 px 的mark单独一行，报告其精度上限 |
