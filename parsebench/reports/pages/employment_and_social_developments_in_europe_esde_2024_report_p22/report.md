# employment_and_social_developments_in_europe_esde_2024_report_p22

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| employment_and_social_developments_in_europe_esde_2024_report | `need_estimate` | 10 | 10 |

本页为《Employment and Social Developments in Europe 2024》第24页，包含正文段落与一个双面板图表 Chart 1.5（左侧为 EU/欧元区就业率折线加2030目标线，右侧为各成员国分组柱＋目标虚线标记）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 75.3 | `EU` · `2023` | 5% | f1 | the 2023 point of the 'EU' line in the left panel | 否 | `EU` · `2023` · `Employment rate (% of people aged 20-64)` · `Chart 1.5` |
| 2 | 74.7 | `Euro area` · `2023` | 2% | f1 | the 2023 point of the 'Euro area' line in the left panel | 否 | `Euro area` · `2023` · `Employment rate (% of people aged 20-64)` · `Chart 1.5` |
| 3 | 78.0 | `EU 2030 target` · `2023` | 1% | f1 | the flat 'EU 2030 target' line in the left panel (also the 78 tick level) | 否 | `EU 2030 target` · `Chart 1.5` |
| 4 | 66.3 | `IT` · `2023` | 2% | f1 | the 2023 bar of the first (lowest) country, IT, in the right panel | 否 | `IT` · `2023` · `Chart 1.5` |
| 5 | 59.8 | `IT` · `2012` | 2% | f1 | the 2012 yellow dot marker for IT in the right panel | 否 | `IT` · `2012` · `Chart 1.5` |
| 6 | 73.0 | `IT` · `Target` | 2% | f1 | cannot be uniquely placed: a mid-ranking country's 2022/2023 bar around 73 in the right panel, no printed value | 否 | `2023` · `Chart 1.5` |
| 7 | 81.1 | `DE` · `2023` | 2% | f1 | cannot be uniquely placed: one of the high-ranking countries' 2023 bars (e.g. DE/DK area) near 81, unlabelled | 否 | `2023` · `Chart 1.5` |
| 8 | 83.0 | `DE` · `Target` | 2% | f1 | cannot be uniquely placed: a 2023 bar among the rightmost countries (SE/NL region) near 83 | 否 | `2023` · `Chart 1.5` |
| 9 | 83.5 | `NL` · `2023` | 2% | f1 | cannot be uniquely placed: the tallest 2023 bar or a national 'Target' dash near 83.5 at the right edge | 否 | `2023` · `Chart 1.5` |
| 10 | 82.4 | `NL` · `Target` | 2% | f1 | cannot be uniquely placed: another right-edge 2023 bar / target marker near 82 with no printed value | 否 | `2023` · `Chart 1.5` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——6 of 10 predicted key sets miss a rule label: 78.0, 73.0, 81.1, 83.0, 83.5, 82.4
- 面板数与面板名个数不一致——f1: panels=2, 0 names
- 系列数与系列名个数不一致——f1: series=4, 7 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 2 | 4 | 12 | 150 | 无 | 80, 78, 76, 74, 72, 70, 68, 66 |

- **f1** Chart 1.5 / Employment rates reached historic levels in 2023, but growth is slowing　[图上方]　单位 `Employment rate (% of people aged 20-64)`
  - 来源行：Source: Eurostat [lfsi_emp_a].

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | right panel: two bars (2022, 2023) side by side per country code |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | right panel combines bars with yellow dot markers (2012) and red dash markers (Target) |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | left panel flat yellow line labelled 'EU 2030 target' near 78 |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left axis 66-80, right axis 40-90, different starts and scales |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | left lowest tick is 66; right lowest tick is 40 |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend entry 'Target' drawn as short red dash above each country's bars |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: Eurostat [lfsi_emp_a].' printed under the plots |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | left panel legend 'EU  Euro area  EU 2030 target' drawn over the plot area |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | each of the two panels carries its own legend block |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | left panel is a time-series line chart, right panel grouped bars with markers |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | right panel legend '2022 2023 2012 Target' sits above its plot |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | 'Click here to download chart.' line under the source line |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | 'Employment rate (% of people aged 20-64)' under the title; axes show bare numbers |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | body text carries superscript '(21)' and '(22)' with footnotes at page bottom |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | right panel country codes set vertically, rotated 90 degrees |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | right panel x labels are two-letter codes IT, EL, RO, ES, HR ... NL |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | left panel yearly ticks 2012-2023 but many plotted points crowded between them |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | both panels show faint horizontal gridlines only, no vertical rules |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 27 country slots x 4 series in the right panel plus 3 lines left |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | f1 | **无** | left panel 'EU 2030 target' drawn as a thin flat yellow/dashed line versus solid EU line |

词表 65 项，本页出现 20 项，其中我们画不出来的 9 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `two_panel_one_caption` | f1 | one 'Chart 1.5' heading governs both an untitled line panel and an untitled bar panel | 两个面板没有各自标题，读数时必须依赖面板位置（左/右）来定位，表格行需额外的面板键才能区分同名系列。 |
| `country_bars_sorted_ascending` | f1 | right panel bars ordered from lowest (IT, EL) to highest (SE, NL) employment rate | 类别顺序不是字母序而是按数值排序，读者只能靠位置推断相对大小，无法用国家代码顺序核对数值。 |
| `unlabeled_second_panel_axis_side` | f1 | right panel's 40-90 tick column is drawn at its left edge, separate from left panel axis | 页面上出现两组纵轴刻度并列，若解析器混用刻度会把右面板柱值错读到左面板量程上。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

右面板宽度约450 px 内塞入27个国家×4个系列（约110个标记），单柱宽仅3-4 px，纵轴刻度为40至90每5一格，5 pp间距在图上不足20 px，要把83.0与83.5或82.4区分开需优于0.5 pp即约0.6%的读数精度，远低于5%容差所能保证的像素分辨率；左面板刻度虽为2一格（66-80），但75.3与74.7相差0.6 pp也只有几个像素。图上无任何数值标签，柱与目标虚线彼此重叠，因此从像素读值是最主要障碍；其次是标签，因为一个值需要面板+国家代码+年份三个键，而国家代码是90度旋转的两字母缩写。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | tick_marker_as_series（目标短横作为独立系列叠在分组柱上） | 图形样式条件行中新增'series drawn as dash marker at category position'的绘制选项，与grouped_bar共存 | 含/不含 tick-marker 系列的分组柱图对比行，检验模型能否把短横读作独立系列而非误判为柱顶 |
| P2 | 一类出版方 | per_panel_axis_range + heterogeneous_panel_types（同一图号下折线面板与柱面板量程不同） | 记录字段加入 panel_key，并允许每个面板独立的 axis_min/axis_max 与图型 | 跨面板量程一致 vs 不一致（66-80 与 40-90）时的读数误差行 |
| P5 | 一类出版方 | dense_marks_100plus（27类别×4系列的高密度国家排序柱） | 密度上限参数，把类别数与系列数乘积作为受控变量 | 标记数 <40 / 40-110 / >110 三档下的单值定位成功率行 |
| P7 | 这份文档自己的习惯 | 新组件 two_panel_one_caption 与 data_link_below_figure | 标题块字段拆为 number/title/unit_text，并新增图下链接行（'Click here to download chart.'） | 面板无独立标题时，是否在markdown导出中以加粗行补出面板位置键的对比行 |
