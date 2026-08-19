# World_Inequality_Report_2026_p131

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `need_estimate` | 9 | 9 |

本页是报告第7章第131页，顶部为编号图 Figure 7.1（两个折线面板：美国慈善捐赠份额时间序列，以及法国与韩国按收入十分位的政治捐赠份额），下方为两栏正文「Regressivity at the top」。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 4.2 | `United States` · `1960` | 5% | f1 | an early-1960s point of the United States line, on the flat ~4% stretch | 否 | `United States` · `1960` · `Charitable donation share of the top 0.01% in the U.S.` |
| 2 | 8 | `United States` · `1990` | 5% | f1 | the flat 1990–1993 plateau of the United States line | 否 | `United States` · `1990` · `Charitable donation share of the top 0.01% in the U.S.` |
| 3 | 14 | `United States` · `2000` | 5% | f1 | a local peak of the United States line around 2000 | 否 | `United States` · `2000` · `Charitable donation share of the top 0.01% in the U.S.` |
| 4 | 14 | `United States` · `2010` | 5% | f1 | a second point of the United States line at the same height, in the mid-2000s dip/rise | 否 | `United States` · `2000` · `Charitable donation share of the top 0.01% in the U.S.` |
| 5 | 5 | `France` · `P50–P60` | 20% | f1 | the France point at the P70–P80 decile in the right panel | 否 | `France and South Korea` · `France` · `P70–P80` |
| 6 | 52 | `France` · `P90–P100` | 5% | f1 | the France point at the top decile P90–P100 | 否 | `France and South Korea` · `France` · `P90–P100` |
| 7 | 5 | `South Korea` · `P50–P60` | 5% | f1 | the South Korea point at the P70–P80 decile | 否 | `France and South Korea` · `South Korea` · `P70–P80` |
| 8 | 58 | `South Korea` · `P90–P100` | 5% | f1 | the South Korea point at the top decile P90–P100 | 否 | `France and South Korea` · `South Korea` · `P90–P100` |
| 9 | 17 | `France` · `P80–P90` | 5% | f1 | the South Korea point at P80–P90 (the two series nearly coincide there) | 否 | `France and South Korea` · `South Korea` · `P80–P90` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 9 predicted key sets miss a rule label: 14, 5, 5
- 标了 dense_marks_100plus，但没有图达到 100 个图元——dense_marks_100plus claimed, densest figure has 73 marks

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 2 | 3 | 10 | 73 | 无 | 0%, 2%, 4%, 6%, 8%, 10%, 12%, 14%, 16%, 18%, 20%, 22%, 24% (left panel); 0%, 10%, 20%, 30%, 40%, 50%, 60% (right panel) |

- **f1** Figure 7.1. / A more progressive tax system is needed in order to reduce political capture by the very rich / Donations in the U.S. (1960–2012) and France and South Korea (2013–2021)　[图上方]　单位 `Percentage of total political donations by income decile`
  - 来源行：Sources and series: Cagé (2024).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left y axis ends at 24% in 2% steps, right y axis ends at 60% in 10% steps |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | small print under the figure: "Interpretation. ... Sources and series: Cagé (2024)." |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | both legend rows sit under their plot areas, well below the x tick labels |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | left legend "United States"; separate right legend "France" "South Korea" |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | "United States" and "France and South Korea" set in bold above their own plots |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | rotated titles "Percentage of total political donations by income decile" and "Charitable donation share of the top 0.01%" |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "Charitable donation share of the top 0.01% in the U.S." set vertically along left axis |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | "1960"…"2010" and "P0–P10"…"P90–P100" tilted about 45 degrees |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | right panel categories written as decile codes "P0–P10" … "P90–P100" |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | left panel plots yearly markers 1960–2012 but ticks only at 1960, 1970, 1980, 1990, 2000, 2010 |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | left axis title wraps to two stacked lines beside the tick column |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | left panel shows ~53 yearly point markers on one line plus 20 points right; ~73 total |

词表 65 项，本页出现 12 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `panels_with_different_x_dimensions` | f1 | left panel x axis is years 1960–2010, right panel x axis is income deciles P0–P10…P90–P100 | 两个面板不是同一图的小倍数，行键必须先指明面板，年份键与十分位键不能混用，否则同一数值会指向错误的标记。 |
| `source_inside_interpretation_paragraph` | f1 | "Sources and series: Cagé (2024)." printed at the end of the bold "Interpretation." paragraph | 来源不是独立的 Source 行，解析器若只抓取以 Source 开头的行会丢失出处，读数时无法确认单位与年份口径。 |
| `marker_dense_line_series` | f1 | each yearly observation carries a square marker on the red line, markers nearly touch | 标记密集且相邻年份差值小于一个 2% 刻度间距，逐点定位单个年份的取值要靠刻度插值。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，全部要靠像素对刻度读取。右面板刻度间隔 10%，整段 0–60% 只占约 190 像素，1% 约 3 像素；对 5 这个值 5% 容差只有 ±0.25，即不到 1 像素，France 与 South Korea 在 P0–P70 段几乎重合，连区分两条线都困难。左面板刻度虽密（2% 一格，约 15 像素），但 1960–2012 有约 53 个年点而只有 6 个十年刻度，4.2 的 5% 容差为 ±0.21（约 1.6 像素），且要先在两个十年刻度之间定位到具体年份。相比之下面板名与系列名都是印在图上的粗体文字，标签寻址（3 个键：面板+系列+十分位）反而可控。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | per_panel_axis_range 与 panels_with_different_x_dimensions 的组合：同一编号图内两面板各自量程、各自横轴维度 | 图表条件行中新增 panel_axis_independent=true 且 panel_x_dimension 可逐面板取 time / category，记录字段加 panel_key | 「双面板异构横轴 + 各自量程」对比「共享轴小倍数」，看行键缺少 panel_key 时的错配率 |
| P3 | 一类出版方 | per_panel_legend（每面板各自图例，位于各自绘图区下方） | 样式字段 legend_scope=per_panel，legend_position=below | 「每面板独立图例」对比「跨面板共享图例」，测系列名归属到正确面板的准确率 |
| P7 | 通用 | heading 五段拆分：figure_number "Figure 7.1."、title、居中的 subtitle「Donations in the U.S. (1960–2012)…」与两个旋转轴标题承载单位 | 标题记录字段拆为 number/title/subtitle/unit/placement，并允许 unit 落在 rotated_axis_title 上 | 「单位只在旋转轴标题里」对比「单位在副标题里」，看导出表能否补回百分比口径 |
| P1 | 通用 | sparse_time_ticks + marker_dense_line_series：年度点、十年刻度 | 时间轴样式字段 tick_every=10 而数据步长为 1，并开启逐点 marker | 「刻度稀疏度 1:10」对比「每点一刻度」，把可达精度作为逐标记属性而非布尔门限 |
| P3 | 这份文档自己的习惯 | source_inside_interpretation_paragraph（来源嵌在粗体 Interpretation 段末） | 注释区字段允许 note_and_source_merged=true | 「来源嵌入注释段」对比「独立 Source: 行」，测整页 markdown 导出中出处能否被绑定到该图 |
