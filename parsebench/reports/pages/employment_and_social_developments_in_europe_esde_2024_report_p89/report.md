# employment_and_social_developments_in_europe_esde_2024_report_p89

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| employment_and_social_developments_in_europe_esde_2024_report | `need_estimate` | 10 | 10 |

页面上部为 Chart 3.14 双面板折线图（左：住房成本占可支配收入份额与跨国标准差，双轴；右：房价与房租指数 2015=100），下部为关于住房政策的正文与脚注。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 22.5 | `2014` · `EU average (left axis)` | 10% | f1 | the 2014 point of the EU average line in the left panel | 否 | `Share of housing costs` · `EU average (left axis)` · `2014` |
| 2 | 6.1 | `2014` · `Variation across countries (right axis)` | 5% | f1 | the 2014 point of the Variation across countries line, read on the right-hand 'Standard deviation' axis | 否 | `Share of housing costs` · `Variation across countries (right axis)` · `Standard deviation` · `2014` |
| 3 | 19.5 | `2023` · `EU average (left axis)` | 5% | f1 | the 2023 point of the EU average line in the left panel | 否 | `Share of housing costs` · `EU average (left axis)` · `2023` |
| 4 | 5.2 | `2023` · `Variation across countries (right axis)` | 5% | f1 | the 2023 point of the Variation across countries line on the right-hand axis | 否 | `Share of housing costs` · `Variation across countries (right axis)` · `Standard deviation` · `2023` |
| 5 | 100 | `2015` · `House prices` | 5% | f1 | the 2015 point of the House prices line (index base year) | 否 | `House prices and rents` · `House prices` · `Index (2015 =100)` · `2015` |
| 6 | 100 | `2015` · `Rents` | 5% | f1 | the 2015 point of the Rents line (index base year) | 否 | `House prices and rents` · `Rents` · `Index (2015 =100)` · `2015` |
| 7 | 150 | `2022` · `House prices` | 1% | f1 | the 2022 point of the House prices line, just above the 150 tick | 否 | `House prices and rents` · `House prices` · `Index (2015 =100)` · `2022` |
| 8 | 112 | `2022` · `Rents` | 5% | f1 | the 2022 point of the Rents line, between the 110 and 130 ticks | 否 | `House prices and rents` · `Rents` · `Index (2015 =100)` · `2022` |
| 9 | 149 | `2023` · `House prices` | 5% | f1 | the 2023 end point of the House prices line | 否 | `House prices and rents` · `House prices` · `Index (2015 =100)` · `2023` |
| 10 | 114 | `2023` · `Rents` | 5% | f1 | the 2023 end point of the Rents line | 否 | `House prices and rents` · `Rents` · `Index (2015 =100)` · `2023` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 2 | 4 | 10 | 40 | 无 | 40%, 30%, 20%, 10%, 0% (left chart left axis); 8, 6, 4, 2, 0 (left chart right axis); 170, 150, 130, 110, 90 (right chart) |

- **f1** Chart 3.14 / Share of housing costs in household disposable income declined but house prices increased sharply between 2014 and 2023 / Weighted EU average share of housing costs in household disposable income and variation across countries (in standard deviation, left chart), and house price index and rent index (right chart), 2014-2023　[图上方]　单位 `Index (2015 =100)`
  - 来源行：Source: Eurostat [ilc_mded01], [prc_hpi_a] and [prc_hicp_aind].

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | left panel: percent axis '40%...0%' at left, 'Standard deviation' axis '8,6,4,2,0' at right |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left panel percent axis starts at 0%, right panel index axis starts at 90 |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | right panel value axis lowest tick is '90', no break glyph drawn |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: In the left chart, 2021 data exclude France...' and 'Source: Eurostat [ilc_mded01]...' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | both legend rows sit under their plot areas, below the year ticks |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | left panel legend 'EU average / Variation across countries'; right panel legend 'House prices / Rents' |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | 'Share of housing costs' and 'House prices and rents' printed above each plot |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | 'Click here to download chart.' printed under the source line |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | subtitle: 'variation across countries (in standard deviation, left chart)'; axis title 'Index (2015 =100)' |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'Standard deviation' and 'Index (2015 =100)' set vertically along the axes |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | right panel axis title reads 'Index (2015 =100)' |

词表 65 项，本页出现 11 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `axis_assignment_in_series_name` | f1 | legend entries read 'EU average (left axis)' and 'Variation across countries (right axis)' | 读数前必须先按图例文字判断该线对哪一条轴刻度（0%–40% 还是 0–8），否则同一像素高度会给出完全不同的数值。 |
| `note_excludes_one_time_point` | f1 | Note: 'In the left chart, 2021 data exclude France, which did not report housing costs in 2021' | 2021 这一点的口径与其他年份不同，取值时需附带该限定，否则行标签无法唯一界定该数值。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，全部要靠像素对刻度换算，而两个面板的刻度都很稀疏：左面板主轴每格 10%（约 45 px），22.5 的 5% 容差只有 ±1.1，即约 5 px；右侧 'Standard deviation' 轴每格 2 个单位，6.1 的容差 ±0.3 折合仅 3–4 px，且必须先按图例 '(right axis)' 判断该线归属哪条轴，判错就会把 6.1 读成约 30%。右面板轴从 90 起、每格 20，112 与 114 之间只差约 4–5 px，几乎无法区分 2022 与 2023 的 Rents。相比之下标签只需 面板名+系列名+年份 三个键，都在页面上逐字可得。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 axis_assignment_in_series_name（图例名中写明左/右轴） | 双轴图的 style 字段与 series 记录中增加 axis_side 并允许把 '(left axis)'/'(right axis)' 拼进图例文本 | 双轴图：图例是否声明轴归属 vs. 不声明，比较取值被读到错轴的比例 |
| P2 | 通用 | per_panel_axis_range 与 axis_starts_above_zero 组合（0% 起的面板与 90 起的指数面板并置） | 多面板条件行中允许每个面板独立的轴起点/量程，并在记录里保存各面板 y 轴范围 | 面板轴量程一致 vs. 各面板独立起点，考察跨面板读数迁移错误 |
| P3 | 通用 | panel_title_per_panel + per_panel_legend 的面板键导出 | markdown 导出模板：把 'Share of housing costs' / 'House prices and rents' 作为表上方粗体小标题，图例名进列头 | 面板名进表头 vs. 仅图号进标题，测量数值+标签配对命中率 |
| P7 | 通用 | 标题五分拆（Chart 3.14 / 长标题 / 副标题 / 'Index (2015 =100)'）与 rebased_index_values | heading 记录新增 figure_number、subtitle、unit_text 字段，unit 可落在旋转轴标题上 | 单位在副标题 vs. 单位在旋转轴标题 vs. 无单位，检验单位归因正确率 |
| new | 这份文档自己的习惯 | note_excludes_one_time_point（注释限定单个年份口径） | note 记录支持指向具体 category 的限定语，并渲染在 Note 行 | 含单点口径注释 vs. 无注释，考察该点数值是否被误当同口径序列使用 |
