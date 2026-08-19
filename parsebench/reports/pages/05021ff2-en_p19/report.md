# 05021ff2-en_p19

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 05021ff2-en | `need_estimate` | 10 | 10 |

该页为OECD报告第17页,含Figure 2.2的双面板图(左为2015-2024年合并申报总量堆积柱状图,右为OECD与非OECD年均增长率横向条形图)及下方注释、来源与正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 7200 | `2015` · `OECD` | 5% | f1 | left panel, the 2015 OECD segment (bottom of the 2015 stack) | 否 | `Total number of merger notifications` · `OECD` · `2015` |
| 2 | 1000 | `2015` · `Non-OECD` | 5% | f1 | left panel, the 2015 Non-OECD segment on top of the 2015 stack | 否 | `Total number of merger notifications` · `Non-OECD` · `2015` |
| 3 | 10500 | `2021` · `OECD` | 5% | f1 | left panel, the 2021 OECD segment | 否 | `Total number of merger notifications` · `OECD` · `2021` |
| 4 | 1500 | `2021` · `Non-OECD` | 5% | f1 | left panel, the 2021 Non-OECD segment topping the tallest stack (~12 000 total) | 否 | `Total number of merger notifications` · `Non-OECD` · `2021` |
| 5 | 8500 | `2024` · `OECD` | 5% | f1 | left panel, the 2019 OECD segment | 否 | `Total number of merger notifications` · `OECD` · `2019` |
| 6 | 44 | `2020/2021` · `OECD` | 5% | f1 | right panel, the 2020/2021 OECD bar, the longest positive bar reaching past 40% | 否 | `Annual growth rate` · `OECD` · `2020/2021` |
| 7 | 22 | `2020/2021` · `Non-OECD` | 5% | f1 | right panel, the 2020/2021 Non-OECD bar ending just past 20% | 否 | `Annual growth rate` · `Non-OECD` · `2020/2021` |
| 8 | 3 | `2018/2019` · `Non-OECD` | 20% | f1 | right panel, the 2018/2019 Non-OECD bar, a short bar just right of 0% | 否 | `Annual growth rate` · `Non-OECD` · `2018/2019` |
| 9 | 4 | `2017/2018` · `Non-OECD` | 20% | f1 | right panel, the 2016/2017 OECD bar, a short bar under 5% | 否 | `Annual growth rate` · `OECD` · `2016/2017` |
| 10 | -19 | `2022/2023` · `OECD` | 5% | f1 | right panel, the 2022/2023 OECD bar extending left of zero toward -20% | 否 | `Annual growth rate` · `OECD` · `2022/2023` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 8500, 4
- 面板数与面板名个数不一致——f1: panels=2, 0 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | na | 2 | 2 | 10 | 38 | 无 | 0, 2 000, 4 000, 6 000, 8 000, 10 000, 12 000, 14 000 (left panel); -30%, -20%, -10%, 0%, 10%, 20%, 30%, 40%, 50% (right panel) |

- **f1** Figure 2.2. / Total merger notifications (left) and the average annual growth rate (right) for OECD and Non-OECD jurisdictions, 2015-2024　[图上方]　单位 `Total number of merger notifications`
  - 来源行：Source: OECD CompStats database

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | right panel: two bars, OECD and Non-OECD, side by side within each year-pair slot |
| `stacked_bar` | 堆叠条 | f1 | 有 | left panel: each year bar has a dark OECD segment with a pink Non-OECD segment stacked on top |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | right panel bars for 2022/2023 and 2021/2022 extend left of the 0% line toward -20% |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | right panel: labels 2015/2016 ... 2023/2024 on the y axis, bars run left and right |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left panel 0 to 14 000 counts, right panel -30% to 50% growth |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Data based on the 59 jurisdictions in the OECD CompStats database...' then 'Source: OECD CompStats database' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | both legends sit in a row below their plot areas, outside them |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | legend 'OECD Non-OECD' under left panel, separate legend under right panel |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | one figure number over a vertical stacked bar panel and a horizontal grouped bar panel |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | 'Total number of merger notifications' over the left plot; its ticks read bare '14 000' |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | 'Total number of merger notifications' printed above the 14 000 tick, not alongside the axis |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | right panel category labels read '2015/2016', '2020/2021', '2023/2024' |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | right panel has 9 year-pair rows while the value axis ticks are every 10% |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | left panel shows horizontal rules at 2 000 ... 14 000, no vertical rules |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | right panel shows vertical rules at -30% ... 50%, no horizontal rules |

词表 65 项，本页出现 15 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `axis_title_in_legend_row` | f1 | right panel legend row ends with 'Annual growth rate' with no colour swatch, acting as axis title | 读数时必须意识到该项不是数据系列,否则会误认为右图有三个系列并错配数值。 |
| `panel_named_in_title_only` | f1 | panels carry no titles; the caption says '(left)' and '(right)' to distinguish them | 要定位某个数值属于哪个面板,只能从图标题中的 (left)/(right) 推断,表格行需自行补出面板键。 |
| `per_panel_category_axis` | f1 | left panel categories are 2015-2024, right panel are nine year pairs 2015/2016-2023/2024 | 两个面板的类别轴不同,不能用同一套年份键跨面板寻址数值。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签,全部要靠像素对轴读取。左面板网格线间距为2 000,而待判定的Non-OECD分段本身只有约1 000–1 500,5%容差即±50–75,相当于网格间距的1/30,堆积段还须先读顶端总高再相减,误差叠加。右面板刻度每10%一格,3%和4%这两根短条的容差只有±0.15pp和±0.2pp,在150 dpi下条长仅十几像素,几乎无法区分。相比之下寻址(面板+系列+年份三键)与标题上下文虽也需补齐,但都能从页面文字逐字抄出。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | heterogeneous_panel_types 与 panel_named_in_title_only(新键) | 图形生成条件行中增加“同一编号图内左右面板类型不同、面板名仅写在标题括号中”的样式字段,并在记录字段里显式保存 panel_key | 有/无 panel_key 一行:当面板名只存在于图标题的 (left)/(right) 时,数值寻址准确率的变化 |
| P6 | 这份文档自己的习惯 | axis_title_in_legend_row(新键) | 图例样式字段:允许一个无色块的文字项(此处为 'Annual growth rate')混入图例行 | 图例中含非系列文字项 vs 纯系列图例,对系列数识别与错配率的影响 |
| P6 | 通用 | negative_values 配合 horizontal_bars 与居中零线 | 样式维度中加入“横向条形+零线两侧延伸、刻度带%号(-30%…50%)”的组合 | 含负值横条图 vs 仅正值柱图的读数精度对比行 |
| P7 | 一类出版方 | unit_in_axis_or_title / axis_title_above_axis | 标题字段拆分:number、title、unit_text 以及单位短语置于顶端刻度之上的位置标记 | 单位短语位于轴上方 vs 位于轴标题旁,对数值量纲判定正确率的影响 |
| P1 | 通用 | 堆积段极薄导致的读数精度问题(对应 stacked_bar 且无数值标签) | 评测中把 readable 改为按 mark 计算可达精度,依据段高与网格间距之比 | 段高/刻度间距 <1/2 的堆积段按可达精度评分 vs 布尔门槛 |
