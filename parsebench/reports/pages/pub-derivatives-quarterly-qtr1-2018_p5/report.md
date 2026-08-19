# pub-derivatives-quarterly-qtr1-2018_p5

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| pub-derivatives-quarterly-qtr1-2018 | `need_estimate` | 10 | 10 |

该页仅有一张图（Figure 1），为2007年Q1至2018年Q1的季度柱状图，展示银行交易收入占控股公司合并交易收入的百分比，含负值。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 80.0% | `2007` · `Q1` | 10% | f1 | the 2007 Q2 bar, the second and tallest of the 2007 group | 否 | `2007` · `Q2` |
| 2 | -85.0% | `2007` · `Q3` | 10% | f1 | the 2007 Q3 bar, the deepest downward bar on the chart | 否 | `2007` · `Q3` |
| 3 | -70.0% | `2008` · `Q3` | 10% | f1 | the 2008 Q3 bar, the second downward bar in the 2008 group | 否 | `2008` · `Q3` |
| 4 | 45.0% | `2009` · `Q1` | 10% | f1 | the 2009 Q1 bar, first bar of the 2009 group just under the 50.0% line | 否 | `2009` · `Q1` |
| 5 | 90.0% | `2011` · `Q3` | 10% | f1 | the 2011 Q3 bar, the tallest bar in the whole figure | 否 | `2011` · `Q3` |
| 6 | 22.0% | `2012` · `Q2` | 15% | f1 | the 2012 Q2 bar, the shortest positive bar on the chart | 否 | `2012` · `Q2` |
| 7 | 75.0% | `2014` · `Q4` | 10% | f1 | the 2007 Q1 bar, the leftmost bar | 否 | `2007` · `Q1` |
| 8 | 52.0% | `2015` · `Q3` | 10% | f1 | the 2016 Q4 bar, the tallest of the 2016 group, just above the 50.0% line | 否 | `2016` · `Q4` |
| 9 | 50.0% | `2017` · `Q4` | 10% | f1 | the 2013 Q2 bar, sitting at the 50.0% gridline level (50.0% is also an axis tick label) | 否 | `2013` · `Q2` |
| 10 | 55.0% | `2018` · `Q1` | 10% | f1 | the 2015 Q3 bar, tallest of the 2015 group | 否 | `2015` · `Q3` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 10 predicted key sets miss a rule label: 80.0%, 75.0%, 52.0%, 50.0%, 55.0%
- 规则需要的键比模型报出的图能提供的多——rules need 2 keys, the richest figure offers 1

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 1 | 1 | 45 | 45 | 无 | 50.0%, 0.0%, -50.0% |

- **f1** Figure 1. / Bank Trading Revenue as a Percentage of Consolidated Holding Company Trading Revenue　[图上方]　（标题里没有单位）
  - 来源行：Source: Consolidated Financial Statements for Holding Companies—FR Y-9C (Schedule HI) and call report (Schedule RI)

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a horizontal rule drawn at the 0.0% tick with bars extending above and below it |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | bars for 2007 Q3 and 2008 Q1-Q3 hang below the 0.0% line; axis tick reads -50.0% |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Source: Consolidated Financial Statements for Holding Companies—FR Y-9C (Schedule HI) and call report (Schedule RI)` under the plot |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | outer row `2007 2008 ... 2018` in boxes, inner row `Q1 Q2 Q3 Q4` repeated under the plot |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | inner tick labels are bare `Q1`, `Q2`, `Q3`, `Q4`; the year only appears in the separate outer row |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | thin vertical rules separate each year group inside the plot; no horizontal grid lines drawn |

词表 65 项，本页出现 6 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `group_tick_row_above_plot` | f1 | year grouping row `2007 ... 2018` sits in boxes above the plot area, quarter row below it | 两级时间轴被拆到图的上下两侧，读某根柱子必须把下方的Q标签与上方的年份框对齐，表格化时年份与季度分别来自图的不同边。 |
| `plot_area_frame_box` | f1 | the plot area is enclosed by a full rectangular border, tick label rows drawn as adjacent boxed strips | 边框与分组框线容易被误认为网格或表格线，影响判断0.0%基线的位置与柱高读数。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，值轴只有 50.0% / 0.0% / -50.0% 三个刻度，50个百分点约占69像素，即1个百分点≈1.4像素。要把 22.0% 读到5%以内需精确到±1.1个百分点，也就是约1.5像素；而 45.0%、50.0%、52.0%、55.0% 这几根柱子（2009 Q1、2013 Q2、2016 Q4、2015 Q3）彼此只差2–5个百分点，在45根柱子挤在约900像素宽的面板里时，几乎无法把某个读数唯一地对应到某一根柱子。相比之下寻址虽然要两个键（年份框+Q标签），但标签本身是清晰印出的。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 group_tick_row_above_plot（分组刻度行置于绘图区上方） | 样式字段中x轴两级标签的放置方式，新增“外层分组行在上、内层行在下”的取值 | 两级时间轴同侧 vs 拆分到绘图区上下两侧时，年份键能否被正确附加到每个季度值上 |
| P6 | 通用 | negative_values 与零线基线（reference_line）的组合 | 条件行中加入“含负值且绘制0.0%基线、刻度对称为 50.0%/0.0%/-50.0%”的取值 | 全正值柱状图 vs 跨零柱状图时，负值柱（-85.0%、-70.0%）读数误差与符号丢失率 |
| P2 | 一类出版方 | 重复内层类别标签（Q1–Q4 重复12次）导致的寻址需两键 | 记录字段中类别键改为 (outer_group, inner_tick) 复合键 | 单键类别 vs 复合类别键（年份+季度）时，唯一定位一个值的成功率 |
| P1 | 通用 | 密度：45个无标签柱、仅3个值轴刻度 | 密度上限设置与刻度数量（value_axis_ticks 个数）作为可控变量 | 刻度间隔50个百分点 vs 25个百分点时，每根柱可达到的读数精度 |
| P7 | 通用 | 标题块拆分（`Figure 1.` 编号 + 换行折行的粗体标题，单位隐含在“as a Percentage of”中） | 标题记录拆为 figure_number / title / subtitle / unit_text 四个字段 | 标题作为整串 vs 拆分编号与单位时，导出表格上方能否保留可被检索的粗体上下文 |
