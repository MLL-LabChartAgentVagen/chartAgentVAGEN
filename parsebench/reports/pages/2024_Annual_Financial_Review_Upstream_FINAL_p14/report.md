# 2024_Annual_Financial_Review_Upstream_FINAL_p14

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2024_Annual_Financial_Review_Upstream_FINAL | `need_estimate` | 10 | 10 |

这是一页EIA幻灯片式报告，含一个未编号的瀑布图，展示158家能源公司2024年已探明储量从年初到年末的变化，各步骤条按地区堆叠，纵轴带断轴符号。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 232.5 | `total proved reserves, start of year` | 5% | f1 | the first black bar, total at start of year, top just above the 230 gridline | 否 | `total proved reserves, start of year` |
| 2 | 232.4 | `total proved reserves, end of year` | 5% | f1 | the last black bar, total at end of year | 否 | `total proved reserves, end of year` |
| 3 | 6.5 | `improved recovery, extensions, discoveries, and revisions` · `United States` | 10% | f1 | the dark-blue United States segment at the base of the improved recovery / extensions bar | 否 | `improved recovery, extensions, discoveries, and revisions` · `United States` |
| 4 | 1 | `improved recovery, extensions, discoveries, and revisions` · `Canada` | 20% | not_found | a roughly one-unit thin band; several such bands exist (Europe/Canada in different step bars) and cannot be separated at this resolution | 否 | — |
| 5 | 8.5 | `purchases` · `United States` | 10% | f1 | the large dark-blue United States segment at the base of the purchases bar | 否 | `purchases` · `United States` |
| 6 | -7.5 | `sales` · `United States` | 10% | f1 | the dark-blue United States segment at the base of the production bar (bottom to about the 240 line) | 否 | `production` · `United States` |
| 7 | -6.5 | `production` · `United States` | 10% | f1 | the dark-blue United States segment of the sales bar, its dominant lower portion | 否 | `sales` · `United States` |
| 8 | -3.5 | `production` · `Asia Pacific, Russia, and Central Asia` | 20% | not_found | one of the gold/olive bands inside the production bar; the Middle East and Africa vs Asia Pacific bands are 2-4 px apart and cannot be told apart | 否 | — |
| 9 | -3.0 | `production` · `Middle East and Africa` | 10% | not_found | another ~3-unit band in the production or sales stack; region cannot be identified at this rendering | 否 | — |
| 10 | 2.0 | `improved recovery, extensions, discoveries, and revisions` · `Middle East and Africa` | 10% | not_found | a ~2-unit light-blue or grey band; occurs in more than one step bar, not resolvable to a single mark | 否 | — |

**程序核对**（模型没有看到左半的标签列）：

- 有值没能落到任何一个图元上——4 of 10 values could not be put on a mark
- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: -7.5, -6.5

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `waterfall` | vertical | 1 | 7 | 6 | 23 | 无 | 270, 260, 250, 240, 230, //, 0 |

- **f1** Change in proved reserves from beginning to end of year for select energy companies　[图上方]　单位 `billion barrels of oil equivalent`
  - 来源行：Data source: Evaluate Energy

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | the purchases, sales and production bars are split into colour-coded regional segments within one bar |
| `broken_axis` | 断轴：轴中间截断并画出断裂标记 | f1 | **无** | a `//` break glyph is drawn on the y axis between the 230 and 0 tick labels |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | bold `net -0.1 billion barrels of oil equivalent` printed inside the plot at the right |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Data source: Evaluate Energy` and `Note: Mergers and acquisitions between companies may affect net reserve changes...` below the plot |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | seven colour-matched region names stacked as text over the plot area between the sales and Latin America bars |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | `billion barrels of oil equivalent` under the bold heading; axis shows bare 270, 260, 250 |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | the unit line sits directly above the top tick `270`, left-aligned with the axis |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | `improved recovery, extensions, discoveries, and revisions` wraps onto four tick lines |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | thin horizontal rules at 270, 260, 250, 240, 230; no vertical rules |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the start-of-year and end-of-year total bars are solid black, unlike the colour-stacked step bars |

词表 65 项，本页出现 10 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `waterfall_connector_line` | f1 | thin blue horizontal lines join the top of each bar to the base of the next bar | 每个浮动条的数值必须由连接线给出的起点与条顶之差读出，而不是条顶的绝对刻度值。 |
| `floating_bars_off_baseline` | f1 | the four step bars hang between 232 and 260, none touches the 0 baseline | 读值时须先确定条的底部高度，长度即变化量；直接读顶端会得到累计储量而非该步骤的增减。 |
| `signed_step_drawn_above_zero` | f1 | sales and production are decreases yet drawn as positive-height bars above zero; only the callout shows a minus sign | 负号无法从图形几何判断，必须依据类别名（sales、production）为读出的段长补上负号。 |
| `narrative_slide_title_above_figure_heading` | page | large blue sentence `After net purchases and production... unchanged in 2024` above the bold figure heading | 标题层级有两层：结论句与图表标题，表格上下文若只取一层会丢失单位或主题定位。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

轴上10个单位约占57像素，即1单位≈5.7像素。两端的总量条（232.5、232.4）5%容差达±11.6单位，几乎无法读错；但被打分的其余数值是地区堆叠段，量级只有1到8.5，5%容差分别只有0.05到0.43单位，即0.3到2.5像素——薄段（1.0、2.0、-3.0、-3.5）的边界本身在这一渲染下就有1到2像素的不确定性，加之瀑布条悬空、需先由连接线定底部再取段高，取值精度根本达不到。相比之下标签虽需“类别名+地区名”两键，且地区名以彩色文字置于图内而非图例，尚可在表头中承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | waterfall 家族与 waterfall_connector_line / floating_bars_off_baseline（浮动条+连接线） | 图表族条件行中新增 waterfall 类型，样式字段加入“连接线开关”和“条底基准（零基/累计基）” | 有/无连接线与浮动条基准的瀑布图，对比每段取值误差与被跳过率 |
| P6 | 一类出版方 | broken_axis（`//` 断轴符号）与断轴下的刻度格式 | 轴样式字段增加 axis_break 位置与符号形状，刻度序列允许 230 与 0 之间断开 | 断轴 vs 起点非零 vs 全零基三种轴设置下的读值精度 |
| P6 | 一类出版方 | signed_step_drawn_above_zero（负向步骤仍画在零上方，符号只在类别名/批注里） | 记录字段增加 sign 与 geometry 分离标记；负值与零线样式维度 | 符号可见（穿越零线）与符号仅由标签给出的两类负值图，对比符号错判率 |
| new | 这份文档自己的习惯 | legend_inside_plot（七个彩色地区名以文字块置于绘图区内，无图例框） | 图例位置样式字段增加 inside_plot_colored_text 取值 | 图例在图内彩色文字 vs 图外方框图例时，系列名到段的绑定正确率 |
| P7 | 一类出版方 | 标题分层：叙述式幻灯片结论句 + 加粗图表标题 + 单位行（unit 位于顶刻度上方） | heading 记录拆分为 number/title/subtitle/unit/placement，并区分页级结论句 | 单位行在顶刻度上方 vs 轴旁 vs 系列名内三种位置下，单位还原率 |
| P1 | 通用 | per-mark 可读精度（薄堆叠段 1-2 单位 vs 总量条 232） | 评分条件行把 readable 改为按段高/像素比给出的可达精度 | 按段高分档（<2、2-5、>5 单位）统计 5% 容差内命中率 |
