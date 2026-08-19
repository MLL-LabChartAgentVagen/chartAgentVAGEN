# GWR-2024_Layout_E_RGB_Web_p32

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| GWR-2024_Layout_E_RGB_Web | `untagged` | 10 | 0 |

本页为《Global Wage Report 2024–25》第12页，上半部为图3.1（2006–24年全球实际月工资年均增长率的分组柱状图，含负值），下半部为两栏正文与三条脚注。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 2.7 | `2006` · `Global` | 1% | f1 | the 2006 Global (blue) bar; also the 2024 Global bar reads 2.7 | 是 | `Figure 3.1.` · `2006` · `Global` |
| 2 | 2.1 | `2006` · `Global (without China)` | 1% | f1 | the 2006 Global (without China) red bar | 是 | `Figure 3.1.` · `2006` · `Global (without China)` |
| 3 | 3.1 | `2007` · `Global` | 1% | f1 | the 2007 Global blue bar | 是 | `Figure 3.1.` · `2007` · `Global` |
| 4 | 1.2 | `2008` · `Global` | 1% | f1 | the 2008 Global blue bar | 是 | `Figure 3.1.` · `2008` · `Global` |
| 5 | 0.6 | `2008` · `Global (without China)` | 1% | f1 | the 2008 Global (without China) red bar | 是 | `Figure 3.1.` · `2008` · `Global (without China)` |
| 6 | -0.9 | `2022` · `Global` | 1% | f1 | the 2022 Global blue bar, below zero | 是 | `Figure 3.1.` · `2022` · `Global` |
| 7 | -1.5 | `2022` · `Global (without China)` | 1% | f1 | the 2022 Global (without China) red bar, below zero | 是 | `Figure 3.1.` · `2022` · `Global (without China)` |
| 8 | 1.8 | `2023` · `Global` | 1% | f1 | the 2023 Global blue bar (also 2021 Global and 2010 red bar read 1.8) | 是 | `Figure 3.1.` · `2023` · `Global` |
| 9 | 2.7 | `2024` · `Global` | 1% | f1 | the 2024 Global blue bar | 是 | `Figure 3.1.` · `2024` · `Global` |
| 10 | 2.3 | `2024` · `Global (without China)` | 1% | f1 | the 2024 Global (without China) red bar | 是 | `Figure 3.1.` · `2024` · `Global (without China)` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 1 | 2 | 19 | 38 | 全部 | 4.0, 3.0, 2.0, 1.0, 0.0, -1.0, -2.0 |

- **f1** Figure 3.1. / Annual average global real monthly wage growth, 2006–24　[图上方]　单位 `(percentage)`
  - 来源行：Source: ILO estimates based on official national sources as recorded in ILOSTAT and the ILO Global Wage Database.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | two bars per year slot: blue 'Global' and red 'Global (without China)' |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a darker rule drawn at 0.0 from which bars rise and fall |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | 2022 bars drop below the 0.0 line, labelled -0.9 and -1.5 |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: ILO estimates based on official national sources as recorded in ILOSTAT...' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Global' and 'Global (without China)' swatches sit in a row under the x axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | '(percentage)' in the caption and 'Change (%)' on the axis; ticks are bare 4.0, 3.0... |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'Change (%)' set vertically along the left value axis |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | body text carries superscript 9, 10, 11 keyed to numbered footnotes below |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | each bar carries its number just above the bar top (below for negatives) |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | year labels 2006...2024 are set at roughly 45 degrees |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole figure block sits on a pale blue tinted band |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 1.0, 2.0, 3.0, 4.0 only; no vertical grid |

词表 65 项，本页出现 12 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `label_collision_offset_in_grouped_pair` | f1 | 2007 labels '3.1' and '2.4' offset vertically; red labels sit lower to avoid the blue label | 分组柱的两个数值标签互相避让，导致标签与柱的对应关系需按左右位置判断，容易把2.4误配给蓝柱。 |
| `heading_unit_in_parentheses_lighter_type` | f1 | '(percentage)' printed in lighter, non-bold type after the bold title on the same line | 单位与标题同一行但字重不同，解析器可能把它并入标题或丢弃，影响单位归属判断。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

所有38个数值都直接印在柱上，读数不成问题（步骤2容易）；难点在寻址：2.7出现在2006-Global与2024-Global，1.8出现在2021-Global、2023-Global与2010的红柱，1.9、1.5、1.4等重复更多，因此一个值必须同时带上年份与系列名（'Global' vs 'Global (without China)'）两个键才能唯一定位。19个年份×2系列意味着表格必须是完整的二维结构；若解析器把两系列合成一列或丢掉旋转的年份刻度，任何2.7/1.8都无法区分。负值行还需保留减号（-0.9、-1.5），否则与0.9混淆。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | grouped_bar 与 negative_values 组合下的系列×类别双键寻址（对应 value_label_outside 的负值下置） | 记录字段中为每个mark同时写入 series_name 与 category_name，并保留标签相对柱的上/下放置字段 | 新增一行：分组柱中数值在系列间重复（如2.7、1.8各出现≥2次）时，仅用类别键 vs 类别+系列双键的检索命中率对比 |
| P7 | 一类出版方 | 标题拆分为 number/title/unit 三段，其中单位以括号形式与标题同行且字重更轻（'(percentage)'） | 样式字段 heading：新增 unit_inline_parenthetical 与 unit_font_weight 选项 | 新增一行：单位在括号内同行 vs 单位独立成行时，单位归属被正确导出的比例 |
| P6 | 一类出版方 | new_components 中的 label_collision_offset_in_grouped_pair（分组柱标签垂直避让） | 渲染样式中加入标签避让开关，控制相邻系列标签的上下偏移量 | 新增一行：开启标签避让后，标签-柱配对错误率随组内柱间距变化的曲线 |
| P6 | 通用 | rotated_x_ticks 与19个时间类别的密集轴标签 | 条件行中类别数与刻度旋转角度联动（19类、45度） | 新增一行：类别数≥19且刻度旋转45度时，年份键被正确解析为表头的比例 |
