# ac8b3538-en_p161

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ac8b3538-en | `need_estimate` | 10 | 10 |

该页为OECD《Employment Outlook 2024》第159页，含正文段落与一幅横向条形图 Figure 3.13（Oaxaca-Blinder分解，含正负值与零线），下附Note、Source及StatLink链接。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | -0.067 | `Difference` | 10% | f1 | the 'Difference' bar, longest bar extending left of zero | 否 | `Difference` · `Earnings relaitve to pre-displacement average, p.p.` |
| 2 | -0.033 | `Explained` | 10% | f1 | the 'Explained' bar | 否 | `Explained` · `Earnings relaitve to pre-displacement average, p.p.` |
| 3 | -0.035 | `Unexplained` | 10% | f1 | the 'Unexplained' bar | 否 | `Unexplained` · `Earnings relaitve to pre-displacement average, p.p.` |
| 4 | -0.007 | `Age` | 10% | f1 | the 'Age' bar | 否 | `Age` · `Earnings relaitve to pre-displacement average, p.p.` |
| 5 | 0.002 | `Gender` | 10% | f1 | the 'Gender' bar, short bar right of zero | 否 | `Gender` · `Earnings relaitve to pre-displacement average, p.p.` |
| 6 | -0.005 | `Tenure` | 10% | f1 | the 'Tenure' bar | 否 | `Tenure` · `Earnings relaitve to pre-displacement average, p.p.` |
| 7 | -0.014 | `Firm wage premia` | 5% | f1 | the 'Firm wage premia' bar | 否 | `Firm wage premia` · `Earnings relaitve to pre-displacement average, p.p.` |
| 8 | -0.011 | `Routine manual` | 5% | f1 | the 'Routine manual' bar | 否 | `Routine manual` · `Earnings relaitve to pre-displacement average, p.p.` |
| 9 | 0.001 | `Non-routine manual` | 10% | f1 | the 'Non-routine manual' bar, a tiny stub right of zero | 否 | `Non-routine manual` · `Earnings relaitve to pre-displacement average, p.p.` |
| 10 | 0.001 | `Routine cognitive` | 10% | f1 | the 'Routine cognitive' bar, a tiny stub right of zero (same magnitude as Non-routine manual) | 否 | `Routine cognitive` · `Earnings relaitve to pre-displacement average, p.p.` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | horizontal | 1 | 1 | 13 | 13 | 无 | -0.07, -0.06, -0.05, -0.04, -0.03, -0.02, -0.01, 0, 0.01 |

- **f1** Figure 3.13. / The concentration of manual routine occupations in high-emission industries contributes to higher earnings losses from job displacement / Oaxaca-Blinder Decomposition, difference in earnings losses between high- and low-emission sectors including occupational measures　[图上方]　单位 `Earnings relaitve to pre-displacement average, p.p.`
  - 来源行：Source: National linked employer employee data, see Annex Table 3.B.1 for details.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a darker vertical rule drawn at 0 from which all bars start |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | ticks run -0.07 to 0.01; most bars extend left of the 0 line |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | category names ('Difference' ... 'Routine cognitive') sit on the y axis, bars run left/right |
| `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | f1 | **无** | 'Worker FE', 'Firm size', 'Non-routine cognitive analytic' rows show an empty slot with no visible bar |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Average across Germany, Finland, Portugal, Hungary and Sweden...' and 'Source: National linked employer employee data...' |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | 'StatLink' logo with 'https://stat.link/w1n74g' under the source line |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | scale word 'p.p.' only in the axis title line under the plot; axis ticks are bare numbers |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | 'Earnings relaitve to pre-displacement average, p.p.' printed below the tick row |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | vertical rules at each tick across the plot, no horizontal grid lines |

词表 65 项，本页出现 9 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `decomposition_total_and_parts_rows` | f1 | 'Difference', 'Explained', 'Unexplained' rows are aggregates above the component rows on the same axis | 同一条轴上混排合计行与分项行，读值时必须区分-0.067（合计）与各分项，否则会把合计误当某一分项。 |
| `near_zero_bar_below_resolution` | f1 | 'Non-routine manual' and 'Routine cognitive' bars are 1-2 px stubs right of the zero line | 0.001量级的条几乎无长度，按像素读值无法达到5%容差，只能依赖数据链接或注释推断。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上无任何数值标签，唯一刻度间隔为0.01，整个绘图区约0.08宽度对应约640像素，即每像素约0.000125。要在5%容差内读出0.001（容差±0.00005）根本不可能——该条只有约8像素长，与线宽同级；0.002、-0.005、-0.007同样落在两条网格线之间且无中间刻度。相比之下行标签唯一（13个单一层级名称），寻址只需1个键加单位行，第3步不构成障碍。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | 以 new_components 的 near_zero_bar_below_resolution 为条件，为每个mark给出可达精度而非布尔可读 | 记录字段增加 per_mark_attainable_precision（按条长像素/轴刻度间隔计算） | 新增一行：仅评估条长>轴范围2%的mark vs 全部mark，对比命中率 |
| P6 | 通用 | reference_line（零线）与 negative_values 的组合作为样式维度 | 样式字段：zero_line_style + 轴范围跨零（min<0<max）的条件行 | 新增一行：跨零横向条形图 vs 全正条形图的读值误差 |
| P7 | 一类出版方 | axis_title_below_plot + unit_in_axis_or_title（'p.p.' 仅出现在图下轴标题） | 标题记录拆分为 number/title/subtitle/unit_text 四字段，并标注 unit 的位置为 below_plot | 新增一行：unit置于轴标题下方 vs 置于副标题时，导出表能否带出单位 |
| new | 一类出版方 | decomposition_total_and_parts_rows（合计行与分项行同轴混排） | 类别字段增加 role 标记（total/subtotal/component），并允许 highlighted_category 呈现 | 新增一行：含合计行的类别轴 vs 纯分项类别轴，值-标签配对准确率 |
| P3 | 这份文档自己的习惯 | data_link_below_figure（StatLink 行）与 source_note_lines 的整页导出位置 | 整页markdown导出模板中 Note/Source/StatLink 相对于表格的排布 | 新增一行：Source/StatLink置于表格前 vs 表格后，对上下文键命中的影响 |
