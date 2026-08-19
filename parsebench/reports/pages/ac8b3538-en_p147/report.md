# ac8b3538-en_p147

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ac8b3538-en | `need_estimate` | 9 | 9 |

OECD《就业展望2024》第145页正文加一张图（Figure 3.4），为分行业「过去(2000-19)与预测(2019-30)」年均就业变化的双系列分组柱状图，含正负值与零线。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 0.8 | `Low emission` · `Past (2000-19)` | 10% | f1 | the Low emission Past (2000-19) bar, rising to about +0.8 | 否 | `Low emission` · `Past (2000-19)` |
| 2 | -2.3 | `High emission` · `Projections (2019-30)` | 10% | f1 | the High emission Projections (2019-30) bar, the dark teal bar reaching about -2.3 | 否 | `High emission` · `Projections (2019-30)` |
| 3 | 0.5 | `Electricity, gas, steam and air conditioning supply` · `Projections (2019-30)` | 10% | f1 | the Electricity, gas, steam and air conditioning supply Projections (2019-30) bar, above zero | 否 | `Electricity, gas, steam and air conditioning supply` · `Projections (2019-30)` |
| 4 | 0.3 | `Land transport and transport via pipelines` · `Past (2000-19)` | 20% | f1 | the Land transport and transport via pipelines Past (2000-19) bar, the small positive bar | 否 | `Land transport and transport via pipelines` · `Past (2000-19)` |
| 5 | -1.6 | `Water transport` · `Projections (2019-30)` | 10% | f1 | the Water transport Projections (2019-30) bar, reaching just past -1.5 | 否 | `Water transport` · `Projections (2019-30)` |
| 6 | -1.9 | `Air transport` · `Projections (2019-30)` | 10% | f1 | the Air transport Projections (2019-30) bar, just short of -2 | 否 | `Air transport` · `Projections (2019-30)` |
| 7 | -3.3 | `Mining and quarrying` · `Projections (2019-30)` | 5% | f1 | the Mining and quarrying Projections (2019-30) bar, just past -3 | 否 | `Mining and quarrying` · `Projections (2019-30)` |
| 8 | -3.9 | `Manufacture of chemicals` · `Projections (2019-30)` | 10% | f1 | the Manufacture of chemicals Projections (2019-30) bar, just short of -4 | 否 | `Manufacture of chemicals` · `Projections (2019-30)` |
| 9 | -5.2 | `Manufacture of coke and refined petroleum` · `Projections (2019-30)` | 5% | f1 | the Manufacture of coke and refined petroleum Projections (2019-30) bar, the longest bar | 否 | `Manufacture of coke and refined petroleum` · `Projections (2019-30)` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 1 | 2 | 13 | 26 | 无 | 2, 1, 0, -1, -2, -3, -4, -5, -6 |

- **f1** Figure 3.4. / The speed of employment declines in high-emission sectors is projected to increase significantly / Past average annual employment changes between 2000 and 2019 and projected average annual employment changes between 2019 and 2030 under a 55% emission reduction for EU countries relative to 1990 levels (Fit for 55), average across countries, percentage　[图上方]　单位 `%`
  - 来源行：Source: ENV-Linkages model.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | two bars per sector slot, legend "Past (2000-19)" and "Projections (2019-30)" |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a black horizontal rule drawn across the plot at 0 |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | axis runs 2 down to -6; most bars hang below the zero line |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: The figure shows historical changes..." and "Source: ENV-Linkages model." under plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | grey legend band with both series keys sits between subtitle and plot area |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | "StatLink" glyph and "https://stat.link/iadv1g" below the source line |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | subtitle ends "average across countries, percentage"; axis shows bare numbers |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "%" printed above the top tick "2" at the axis head |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | "Electricity, gas, steam and air conditioning supply" wraps over five lines |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | plot area filled light grey with white separating rules, not white |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | white horizontal rules at each tick across the grey panel; no vertical grid over values |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the High emission projections bar is dark teal while all other projections bars are bright green |

词表 65 项，本页出现 12 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `blank_category_slot_separator` | f1 | an empty slot separates "High emission" from "Electricity, gas, steam and air conditioning supply" | 轴上留空把两个汇总类别与11个细分行业分开，读数时必须按空隙判断柱子归属，否则会把细分行业的柱错配到汇总列。 |
| `aggregate_and_detail_in_one_axis` | f1 | "Low emission"/"High emission" aggregates share the axis with individual sector categories | 同一轴上混有汇总与成分，表格行必须标明层级，否则-2.3（High emission）会与某个细分行业数值混淆。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上无任何数值标签，刻度间距为1个百分点（约28像素），而被考核的值多为小量：0.3的5%容差只有±0.015、0.5为±0.025、0.8为±0.04，都远小于一个像素所代表的约0.036个百分点，靠像素读数几乎不可能落进容差；只有正文里出现的3.9、3.3、5.4等才有文字支撑。相比之下标签只需两个键（类别名+系列名），且系列名与类别名都完整印出，寻址不是瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 一类出版方 | 把标题拆成 figure_number/title/subtitle/unit 四个字段，并记录 unit 出现在副标题末尾（"percentage"）同时以 "%" 置于轴顶 | 记录层的 heading 结构字段与样式字段 unit_position（axis_head / subtitle_tail） | 新增一行：单位只写在副标题末尾 vs 写在轴顶 vs 两处都写，比较取值时单位归属的正确率 |
| P6 | 通用 | negative_values + reference_line（零线作为可见黑色规则）与柱子双向生长的组合 | 样式条件行中新增 zero_line_visible 与 value_range_spans_zero | 新增一行：含负值且零线可见 vs 全正值，比较符号错误率（如 0.3 与 -0.3 同一行业成对出现时） |
| new | 一类出版方 | 新组件 blank_category_slot_separator / aggregate_and_detail_in_one_axis | 类别轴生成条件：允许插入空槽并标记汇总类别层级 | 新增一行：类别轴含空槽分隔的汇总组 vs 连续类别轴，比较柱子—类别错配率 |
| P1 | 通用 | 把可读性改成每个mark的可达精度（1个百分点刻度下小于1的柱子精度上限） | 评测配置里 readable 的布尔门槛改为 per-mark tolerance 计算 | 新增一行：\|value\| < 1 个刻度单位的mark单独统计精度，与大值mark分开报告 |
| P6 | 这份文档自己的习惯 | highlighted_category（单根柱换成深青色） | 样式字段 series_color_override / emphasis_mark | 新增一行：有一根异色柱 vs 全系列同色，比较是否被误判为第三个系列 |
