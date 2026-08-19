# employment_and_social_developments_in_europe_esde_2024_report_p56

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| employment_and_social_developments_in_europe_esde_2024_report | `need_estimate` | 10 | 10 |

该页为报告第59页正文,中部嵌入 Chart 2.10 双面板折线图(a 欧盟层面性别差距、b 跨国差异标准差),下附 Note、Source 与下载链接。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 26 | `2007` · `Unpaid care (% Men)` | 5% | f1 | the 2007 point of the dashed green 'Housework (% Men)' line in panel a) | 否 | `a) Gap at EU level` · `Housework (% Men)` · `2007` |
| 2 | 40 | `2007` · `Unpaid care (% Women)` | 5% | f1 | the 2007 point of the solid dark-blue 'Unpaid care (% Women)' line in panel a) | 否 | `a) Gap at EU level` · `Unpaid care (% Women)` · `2007` |
| 3 | 79 | `2007` · `Housework (% Women)` | 5% | f1 | the 2007 point of the solid green 'Housework (% Women)' line in panel a) | 否 | `a) Gap at EU level` · `Housework (% Women)` · `2007` |
| 4 | 38 | `2022` · `Housework (% Men)` | 5% | f1 | the 2016 point of the solid dark-blue 'Unpaid care (% Women)' line in panel a) | 否 | `a) Gap at EU level` · `Unpaid care (% Women)` · `2016` |
| 5 | 63 | `2022` · `Housework (% Women)` | 5% | f1 | the 2022 point of the solid green 'Housework (% Women)' line in panel a) | 否 | `a) Gap at EU level` · `Housework (% Women)` · `2022` |
| 6 | 11 | `2007` · `Housework` | 5% | f1 | the 2007 point of the green 'Housework' line in panel b) | 否 | `b) Cross-country variation` · `Housework` · `2007` |
| 7 | 5.5 | `2007` · `Unpaid care` | 5% | f1 | the 2007 point of the dark-blue 'Unpaid care' line in panel b) | 否 | `b) Cross-country variation` · `Unpaid care` · `2007` |
| 8 | 3.8 | `2012` · `Unpaid care` | 5% | f1 | the 2012 trough of the dark-blue 'Unpaid care' line in panel b) | 否 | `b) Cross-country variation` · `Unpaid care` · `2012` |
| 9 | 9.2 | `2022` · `Housework` | 5% | f1 | the 2022 point of the green 'Housework' line in panel b) | 否 | `b) Cross-country variation` · `Housework` · `2022` |
| 10 | 5.2 | `2022` · `Unpaid care` | 5% | f1 | the 2022 point of the dark-blue 'Unpaid care' line in panel b) | 否 | `b) Cross-country variation` · `Unpaid care` · `2022` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 26, 38

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 2 | 6 | 4 | 24 | 无 | a) 0, 10, 20, 30, 40, 50, 60, 70, 80, 90; b) 0, 2, 4, 6, 8, 10, 12, 14 |

- **f1** Chart 2.10 / Limited upward convergence in gender gaps in unpaid work / Daily involvement in unpaid care and housework by gender, and cross-country variation in gender gaps (standard deviation), 2007-2022, EU-27　[图上方]　（标题里没有单位）
  - 来源行：Source: DG EMPL calculations based on EIGE's Gender Statistics Database

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | panel a) axis tops at 90, panel b) axis tops at 14 |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Involvement in unpaid care defined as...' and 'Source: DG EMPL calculations based on EIGE's...' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend rows sit under the plot areas, below the 2007-2022 tick row |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | four-entry legend under panel a), separate two-entry legend under panel b) |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | 'a) Gap at EU level' and 'b) Cross-country variation' set above each plot |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | 'Click here to download chart.' printed under the source line |
| `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | f1 | **无** | legend reads 'Unpaid care (% Men)', 'Housework (% Women)' - % inside the series name |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | subtitle: 'cross-country variation in gender gaps (standard deviation)'; panel b axis is bare 0-14 |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | ticks 2007, 2012, 2016, 2022 are unequal 5/4/6-year steps drawn evenly spaced |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | f1 | **无** | 'Unpaid care (% Men)' and 'Housework (% Men)' drawn dashed, the women series solid |

词表 65 项，本页出现 10 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `series_name_reused_across_panels` | f1 | 'Unpaid care' and 'Housework' name series in panel b, also inside panel a legend labels | 同名系列在两个面板含义与量纲不同(% 与标准差),不带面板名的表行无法唯一定位某个数值。 |
| `irregular_time_axis_spacing` | f1 | only 2007, 2012, 2016, 2022 plotted, spaced as equal categorical slots on x | 折线斜率不代表逐年变化,读点必须按刻度标签而非按插值位置定位。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上无任何数值标签,全部要靠像素对刻度读数。面板 a 刻度间距为 10 个单位,而 26 的 5% 容差只有 ±1.3,即约 1/8 格;面板 b 刻度间距为 2,3.8 的容差 ±0.19 不足 1/10 格,且 2012 年的蓝线低点与 4 这条刻度线几乎贴合,极易读成 4.0(误差 5.3%)。此外面板 a 里四条线在 2016 年附近(约 34-38)相互交叠,分辨哪条线属于 'Unpaid care (% Women)' 还需依赖虚实线型,进一步放大读值风险;相比之下标签只需 3 个键(面板名+系列名+年份),表格可承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | per_panel_axis_range 与 per_panel_legend 组合(面板各自量纲+各自图例) | 条件行:双面板折线,面板 b 轴上限 14、面板 a 上限 90;记录字段加入 panel_key 与 panel 级 y 轴范围 | 含/不含 panel_key 时,同名系列('Unpaid care')跨面板取值的定位准确率对比 |
| P6 | 一类出版方 | unit_in_series_name 与 unit_in_axis_or_title 混用(a 面板 % 在图例内,b 面板标准差只在副标题) | 样式字段 unit_position:允许同一图内不同面板的单位落在不同位置 | 单位位置随面板变化 vs 单位统一在轴标题时,数值量纲还原正确率 |
| P7 | 通用 | heading 五段拆分:'Chart 2.10' + 标题行 + 长副标题(含 '(standard deviation), 2007-2022, EU-27') | 记录字段:figure_number/title/subtitle 分列,placement=above,并保留面板小标题为独立字段 | 副标题与面板小标题是否以粗体/标题形式导出时,上下文匹配得分差异 |
| P1 | 通用 | P1:按标记给出可达精度(无数值标签、刻度间距 10 与 2) | 评测条件行:values_printed=none 且刻度间距/容差比 >5 的折线点,精度阈值按格距比例设定 | 以像素精度上限代替 5% 硬门槛后,折线交叠区(2016 年四线聚集)得分变化 |
| new | 一类出版方 | new_components 中 irregular_time_axis_spacing(2007/2012/2016/2022 等距排布) | 类别轴生成规则:时间标签不等间隔但按分类槽等距布点 | 等间隔年份 vs 不等间隔年份标签时,单点定位到正确年份的准确率 |
