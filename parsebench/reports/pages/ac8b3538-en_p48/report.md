# ac8b3538-en_p48

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ac8b3538-en | `need_estimate` | 10 | 10 |

该页为OECD《Employment Outlook 2024》第46页，含一幅两面板图（Figure 1.20：A 面板为带男女菱形标记的柱状图，B 面板为国家散点图），下方有注释、来源、StatLink 链接及正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 17.5 | `FRA` · `Both sexes` | 5% | f1 | the FRA "Both sexes" bar in Panel A (top of bar just under 18) | 否 | `A. Incidence of job strain` · `FRA` · `Both sexes` |
| 2 | 20.0 | `FIN` · `Women` | 5% | f1 | the FIN "Women" diamond in Panel A, highest marker on the panel | 否 | `A. Incidence of job strain` · `FIN` · `Women` |
| 3 | 18 | `GRC` · `Men` | 5% | f1 | the GRC "Women" diamond in Panel A, sitting far above the GRC bar | 否 | `A. Incidence of job strain` · `GRC` · `Women` |
| 4 | 12.5 | `Average` · `Both sexes` | 5% | f1 | the red "Average" bar in Panel A | 否 | `A. Incidence of job strain` · `Average` · `Both sexes` |
| 5 | 8.5 | `SVN` · `Women` | 5% | f1 | the EST "Both sexes" bar in Panel A, second from the right | 否 | `A. Incidence of job strain` · `EST` · `Both sexes` |
| 6 | 20.0 | `FIN` · `Women` | 5% | f1 | duplicate of the FIN "Women" diamond in Panel A (no other mark reaches 20) | 否 | `A. Incidence of job strain` · `FIN` · `Women` |
| 7 | 18 | `GRC` · `Men` | 5% | f1 | duplicate reading around 18: the GRC "Women" diamond in Panel A | 否 | `A. Incidence of job strain` · `GRC` · `Women` |
| 8 | 12.5 | `Average` · `Both sexes` | 5% | f1 | the FIN "Men" diamond in Panel A, low end of the FIN dotted connector | 否 | `A. Incidence of job strain` · `FIN` · `Men` |
| 9 | 11.5 | `NLD` · `Women` | 5% | f1 | the LTU "Both sexes" bar in Panel A | 否 | `A. Incidence of job strain` · `LTU` · `Both sexes` |
| 10 | 8 | `SVN` · `Both sexes` | 5% | f1 | the SVN "Both sexes" bar in Panel A, rightmost bar | 否 | `A. Incidence of job strain` · `SVN` · `Both sexes` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 8.5, 12.5, 11.5

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 2 | 3 | 26 | 104 | 无 | Panel A: 0, 5, 10, 15, 20, 25; Panel B y: 0, 1, 2, 3, 4, 5, 6, 7; Panel B x: 6, 7, 8, 9, 10, 11, 12, 13, 14 |

- **f1** Figure 1.20. / Job strain in OECD European countries, 2021 / Percentage of employees aged 16-64 in OECD European countries, 2021　[图上方]　单位 `%`
  - 来源行：Source: OECD calculations based on the European Working Conditions Telephone Survey (EWCTS) 2021 of the European Foundation for the Improvement of Living and Working Conditions (Eurofound).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | Panel A: green bars with light and dark diamond markers for "Men" and "Women" over each bar |
| `range_connector_line` | 每个类目两个点用线段连成区间（哑铃图 / 区间图） | f1 | **无** | Panel A: dotted vertical segments join the Men and Women diamonds, e.g. FIN from ~12.7 to ~20.2 |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: Countries are ordered in Panel A by descending order..." and "Source: OECD calculations based on..." |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | Panel A is bars with markers; Panel B is a scatter of countries on two % axes |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | grey legend strip "Both sexes / Men / Women" between subtitle and Panel A plot area |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | "A. Incidence of job strain" and "B. Degrees of job strain" set above each panel |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | "StatLink" icon with "https://stat.link/9qidkp" under the note block |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | subtitle "Percentage of employees aged 16-64..." plus bare-number axis 0, 5, 10, 15, 20, 25 |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | "% of employees moderately strained" printed under Panel B's x axis at the right |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | bare "%" printed above the top tick 25 in Panel A; "% of employees highly strained" above Panel B |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | Panel A country codes are turned about 45 degrees under the baseline |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | axis reads FRA, CZE, FIN, BEL, POL, DEU ... EST, SVN plus "Average" |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | f1 | **无** | Panel B has no legend; each point is named beside it: "CZE", "FRA", "SVN", "Average" |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | both plot areas carry a light grey fill instead of white |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 26 bars plus 26 Men and 26 Women diamonds plus 26 scatter points ≈ 104 marks |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the "Average" bar is red among green bars; "Average" is bold beside its point in Panel B |

词表 65 项，本页出现 16 项，其中我们画不出来的 9 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `point_labels_with_leader_lines` | f1 | Panel B labels GBR, NOR, SWE, ESP, DEU, AUT, GRC sit off the marker linked by short leader lines | 读值时必须沿引线把国家名与具体散点配对，标签位置与点位分离，错配会把两国的 x/y 值互换。 |
| `same_categories_different_measures_across_panels` | f1 | the same 26 codes (FRA, CZE, Average...) appear in Panel A as bars and in Panel B as points | 同一国家标签在两面板对应不同量（发生率% 与 高/中度应变%），不带面板名的表行无法唯一定位数值。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

定位一个数值至少需要三把钥匙：面板名（A. Incidence of job strain / B. Degrees of job strain）、国家代码、以及系列（Both sexes / Men / Women）；两面板共用同一批 26 个代码却量纲不同，若解析器把两面板合成一张表，FRA 的 17.5 与 Panel B 的 4.9 就无法区分。更麻烦的是 Panel A 里 12.5 同时可读为 Average 柱与 FIN 的 Men 菱形，8 可读为 SVN 柱与 GRC 的 Men 菱形，缺少系列列时同一数字对应多行。相比之下取值本身尚可：Panel A 刻度间距 5% 而 5% 容差对 17.5 约为 0.87，肉眼对齐足够；散点重叠与引线标签只影响配对而非精度。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | heterogeneous_panel_types 与新提出的 same_categories_different_measures_across_panels | 记录字段中加入 panel_key，并允许一个 figure 的两个面板使用不同图族与不同值轴单位 | 有/无 panel_key 时，跨面板复用同一类别标签的数值命中率对比 |
| P6 | 一类出版方 | tick_marker_as_series / range_connector_line（柱上叠加 Men、Women 菱形并用虚线连接） | 样式条件行中新增“柱状图叠加点标记系列 + 竖向连接线”这一混合标记选项 | 柱内叠加标记系列时，标记值与柱值的分辨准确率对比纯柱图 |
| P7 | 通用 | 标题五段拆分（figure_number / title / subtitle / unit_text 与 %、% of employees moderately strained 两处轴题位置） | P7 的标题记录字段，加入“单位置于顶刻度上方”与“轴题置于图下右侧”两个位置枚举 | 单位位置（轴上方 vs 副标题 vs 轴旁）对单位召回率的影响行 |
| P3 | 一类出版方 | point_labels_with_leader_lines（散点旁引线国家标签）与 inline_series_labels | 散点族的标签样式字段：无图例、逐点标注、可带引线偏移 | 引线偏移标签 vs 紧贴标签时，点—标签配对错误率对比 |
