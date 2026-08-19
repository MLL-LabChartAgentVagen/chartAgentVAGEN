# ac8b3538-en_p36

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ac8b3538-en | `3d_chart+need_estimate` | 10 | 10 |

这一页是 OECD《Employment Outlook 2024》第34页，主体为图 1.12「Real negotiated wages in selected OECD countries」，双面板柱状图叠加菱形标记，并配有长篇 Note/Source 与 StatLink 行。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 4.2 | `A. All sectors` · `AUT` · `Q1 2024 or latest (↘)` | 40% | f1 | the tallest bar, AUT in panel A (the AUT bar in panel B is nearly identical, so the two panels are hard to separate) | 否 | `A. All sectors` · `AUT` · `Q1 2024 or latest (↘)` |
| 2 | -9.2 | `A. All sectors` · `ITA` · `Trough since Q4 2019` | 10% | f1 | the deepest diamond in panel A, at ITA | 否 | `A. All sectors` · `ITA` · `Trough since Q4 2019` |
| 3 | 3.2 | `B. Private sector` · `USA` · `Q1 2024 or latest (↘)` | 30% | f1 | the third bar of panel B, NLD (LS) | 否 | `B. Private sector` · `NLD (LS)` · `Q1 2024 or latest (↘)` |
| 4 | -9.5 | `B. Private sector` · `ITA` · `Trough since Q4 2019` | 10% | f1 | the deepest diamond of panel B, under USA | 否 | `B. Private sector` · `USA` · `Trough since Q4 2019` |
| 5 | 2 | `A. All sectors` · `EA20` · `Q1 2024 or latest (↘)` | 50% | f1 | the EA20 bar in panel A, level with the "2" tick | 否 | `A. All sectors` · `EA20` · `Q1 2024 or latest (↘)` |
| 6 | -1.8 | `B. Private sector` · `FRA` · `Trough since Q4 2019` | 40% | f1 | the shallowest diamond in panel B, sitting just below -2 at FRA | 否 | `B. Private sector` · `FRA` · `Trough since Q4 2019` |
| 7 | -3.5 | `B. Private sector` · `BEL` · `Trough since Q4 2019` | 40% | f1 | the diamond near -3.5 in panel B, at BEL | 否 | `B. Private sector` · `BEL` · `Trough since Q4 2019` |
| 8 | 1.5 | `B. Private sector` · `DEU (LS)` · `Q1 2024 or latest (↘)` | 50% | f1 | a short bar in the middle-right of panel B, DEU (LS) | 否 | `B. Private sector` · `DEU (LS)` · `Q1 2024 or latest (↘)` |
| 9 | -8.5 | `A. All sectors` · `SWE` · `Trough since Q4 2019` | 20% | f1 | the last diamond of panel B, under SWE | 否 | `B. Private sector` · `SWE` · `Trough since Q4 2019` |
| 10 | 3.8 | `A. All sectors` · `NLD` · `Q1 2024 or latest (↘)` | 30% | f1 | the second bar, NLD (present at almost the same height in both panels) | 否 | `A. All sectors` · `NLD` · `Q1 2024 or latest (↘)` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 3.2, -9.5, -8.5

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 2 | 2 | 10 | 46 | 无 | 6, 4, 2, 0, -2, -4, -6, -8, -10, -12 |

- **f1** Figure 1.12. / Real negotiated wages in selected OECD countries / Year-on-year percentage change in real negotiated wages (i.e. resulting from collective agreements)　[图上方]　单位 `%`
  - 来源行：Source: OECD calculations based on national data on negotiated wages, see Annex Table 1.C.3.in (Araki et al., 2023[11]) for further details; and OECD (2024), “Prices: Consumer prices”, Main Economic Indicators (database), https://doi.org/10.1787/0f2e8000-en (accessed on 28 June 2024).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | teal bars for "Q1 2024 or latest (↘)" with green diamond markers "Trough since Q4 2019" in the same panel |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | axis runs 6 down to -12; SWE and AUS bars sit below the zero line, all diamonds negative |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | the "Trough since Q4 2019" series is a single diamond glyph per country read on the same % axis |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one legend box above both panels A and B carrying the two entries |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | two side-by-side panels of the same bar-plus-diamond chart |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: International comparability of data..." and "Source: OECD calculations based on national data..." under the plots |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | legend box sits between the subtitle line and the panel titles "A. All sectors" / "B. Private sector" |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | "A. All sectors" and "B. Private sector" printed above each plot |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | "StatLink" logo with "https://stat.link/g6dcje" at the bottom right of the figure box |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | subtitle "Year-on-year percentage change in real negotiated wages" plus the "%" above the axis; ticks are bare numbers |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | a bare "%" printed above the top tick "6" on each panel |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | axis labels read AUT, NLD, DEU, EA20, ITA, CAN, AUS, SWE, USA, FRA, BEL |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | "NLD" / "(LS)", "DEU" / "(LS)", "USA" / "(LS)" set on two stacked lines |
| `panel_background` | 绘图区带底色，不是白底 | page | **无** | the whole figure and preceding paragraph sit in a beige tinted bordered box |

词表 65 项，本页出现 14 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `bar_to_marker_drop_line` | f1 | a thin vertical line drops from each bar down to that country's trough diamond | 读值时须区分这条连接线只是引导线，不代表数量；柱高与菱形要分别对着同一 % 轴各读一次。 |
| `value_sorted_categories` | f1 | legend reads "Q1 2024 or latest (↘)" and bars fall monotonically from AUT to SWE in both panels | 类别顺序由柱值降序决定而非固定国别顺序，两面板顺序不同，跨面板按位置对齐会错行。 |
| `panel_specific_category_sets` | f1 | panel A has 10 slots ending SWE; panel B has 13 including USA, USA (LS), FRA, BEL | 面板列数不同，无法用一张共享类别表承载，必须每面板单独建行键。 |
| `variant_suffix_category_slot` | f1 | "NLD" and "NLD (LS)" occupy separate slots; note defines "LS: wages including lump sums and/or special payments" | 同一国家出现两次，仅靠国别码无法唯一定位某个值，必须连同 (LS) 后缀一起作为键。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，刻度每 2 个百分点一格，绘图区高度约 215 px 覆盖 6 到 -12 共 18 个单位，即约 12 px/单位。要把 -1.8 读到 5% 容差就是 ±0.09，仅约 1 px；2.0 的容差 ±0.1、1.5 的容差 ±0.075 同样在一两个像素内，而菱形本身直径就有 6~7 px，中心定位误差已超容差。相比之下标签虽需三个键（面板名 + 国别码含 (LS) 后缀 + 系列名），仍可写进表头，因此像素读数才是真正的瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | tick_marker_as_series 与新提出的 bar_to_marker_drop_line（柱顶到点标记的引导线） | 图形样式条件行：在 bar 家族上增加“叠加单点标记 + 垂直引导线”的开关，并在记录里把标记系列单独成列 | “柱+点标记同轴（含引导线）”对比“纯柱”时，点标记系列的取值准确率 |
| P2 | 一类出版方 | panel_specific_category_sets（各面板类别集合与数量不同） | 面板维度进入键（panel_key），且类别列表按面板独立生成而非共享 | “面板类别集合不一致”对比“面板共享同一类别集合”时的行定位错误率 |
| P3 | 一类出版方 | variant_suffix_category_slot（NLD / NLD (LS) 同国重复出现） | 类别标签字段：允许同一基名加后缀限定符成为独立类别，并在 Note 中定义后缀 | “类别名存在重复基名+后缀”对比“类别名全互异”时的键唯一性命中率 |
| P4 | 通用 | value_sorted_categories（按值降序排列，图例写作“(↘)”） | 记录生成器的类别排序策略字段，以及图例名中携带排序符号 | “类别按值排序（各面板顺序不同）”对比“固定类别顺序”时的跨面板对齐错误 |
| P7 | 这份文档自己的习惯 | 标题五分拆：figure_number / title / subtitle / unit（“%”置于顶刻度之上）/ placement | 标题块字段，尤其 axis_title_above_axis 这种把单位放在轴顶的位置选项 | “单位仅出现在轴顶裸符号”对比“单位写在轴标题或副标题”时的量纲恢复率 |
