# r_qt1212e_p9

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| r_qt1212e | `need_estimate` | 10 | 10 |

该页上半部为 BIS《Reinsurance market developments》(Graph 6) 双面板图：左panel为再保险市场集中度折线图，右panel为再保险公司倒闭数的柱+点双轴图，下半部为正文与脚注。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 51 | `00` · `Top 10 market share¹` | 10% | f1 | the 04 point of the Top 10 market share line (plateau top) | 否 | `Reinsurance market concentration` · `Top 10 market share1` · `04` · `Per cent` |
| 2 | 48 | `01` · `Top 10 market share¹` | 10% | f1 | the 00 point of the Top 10 market share line (start of series) | 否 | `Reinsurance market concentration` · `Top 10 market share1` · `00` · `Per cent` |
| 3 | 53 | `04` · `Top 10 market share¹` | 10% | f1 | the 03 point of the Top 10 market share line (highest point) | 否 | `Reinsurance market concentration` · `Top 10 market share1` · `03` · `Per cent` |
| 4 | 42 | `08` · `Top 10 market share¹` | 10% | f1 | the 11 point of the Top 10 market share line (last point) | 否 | `Reinsurance market concentration` · `Top 10 market share1` · `11` · `Per cent` |
| 5 | 43 | `11` · `Top 10 market share¹` | 10% | f1 | the 09 point of the Top 10 market share line (local peak after the 08 trough) | 否 | `Reinsurance market concentration` · `Top 10 market share1` · `09` · `Per cent` |
| 6 | 0.1 | `85` · `Market share of failed companies²` | 20% | f1 | a red 'Market share of failed companies' dot sitting just under the 0.1 lhs rule (mid-1980s year and again in the last year) | 否 | `Failures of reinsurance companies` · `Lhs:` · `Market share of failed companies2` · `Per cent of premiums` |
| 7 | 3 | `92` · `Number of failures³` | 5% | f1 | a blue 'Number of failures' bar reaching the rhs value 3 (the two tall bars just after 92) | 否 | `Failures of reinsurance companies` · `Rhs:` · `Number of failures3` · `Number of companies` |
| 8 | 0 | `01` · `Market share of failed companies²` | 1% | f1 | red dots lying on the 0.0 lhs baseline in years with negligible failed-company market share | 否 | `Failures of reinsurance companies` · `Lhs:` · `Market share of failed companies2` · `Per cent of premiums` |
| 9 | 0.33 | `03` · `Market share of failed companies²` | 10% | f1 | the isolated red dot above the 0.3 rule near 03 (the two 2003 bankruptcies) | 否 | `Failures of reinsurance companies` · `Lhs:` · `Market share of failed companies2` · `03` · `Per cent of premiums` |
| 10 | 1 | `11` · `Number of failures³` | 5% | f1 | a short blue bar reaching the rhs value 1 (single-failure years, e.g. near 89 and near 10) | 否 | `Failures of reinsurance companies` · `Rhs:` · `Number of failures3` · `Number of companies` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——9 of 10 predicted key sets miss a rule label: 51, 48, 53, 42, 43, 0.1

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 2 | 3 | 32 | 42 | 无 | left panel: 60, 50, 40, 30; right panel lhs: 0.4, 0.3, 0.2, 0.1, 0.0; right panel rhs: 4, 3, 2, 1, 0 |

- **f1** Graph 6 / Reinsurance market developments　[图上方]　单位 `Per cent / Per cent of premiums / Number of companies`
  - 来源行：Sources: IAIS, based on industry data; authors’ calculations.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | right panel: 'Per cent of premiums' ticks 0.0–0.4 at left, 'Number of companies' ticks 0–4 at right |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | right panel draws blue bars and red round markers in the same plot area |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left panel 30–60 Per cent; right panel 0.0–0.4 and 0–4 |
| `right_side_y_axis` | 唯一的值轴画在右侧 | f1 | **无** | left panel's only value axis (60, 50, 40, 30) is printed on the right edge of the panel |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | left panel lowest tick is 30, not 0, with no break glyph |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | right panel bars and dots share the one category (year) axis drawn once at the bottom |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | numbered notes 1,2,3 and 'Sources: IAIS, based on industry data; authors’ calculations.' below the panels |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | both legends sit under their panels, below the year tick rows |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | left legend 'Top 10 market share1'; right legend 'Market share of failed companies2' and 'Number of failures3' |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | left panel is a single line series; right panel is bars plus point markers |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | 'Reinsurance market concentration' and 'Failures of reinsurance companies' set above each panel |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 30–60 and 0.0–0.4; scale word only in 'Per cent' / 'Per cent of premiums' headers |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | superscript 1 on 'Top 10 market share', 2 on 'Market share of failed companies', 3 on 'Number of failures' |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | 'Per cent', 'Per cent of premiums', 'Number of companies' printed above the top ticks |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | x ticks written as bare two-digit years '00 01 ... 11' and '80 83 ... 10' |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | right panel bars are yearly but ticks appear every three years: 80, 83, 86, 89, 92, 95, 98, 01, 04, 07, 10 |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | left panel plot area filled grey with white grid rules |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | right panel shows horizontal rules at 0.1, 0.2, 0.3, 0.4 and no vertical rules |

词表 65 项，本页出现 18 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `axis_assignment_in_legend` | f1 | legend rows prefixed 'Lhs:' above the red dot entry and 'Rhs:' above the blue bar entry | 读值前必须先由 Lhs/Rhs 前缀判定该系列归属哪条轴，否则 0.33 与 3 之类的数会被读到错误刻度上。 |
| `tick_row_without_gridline_per_year` | f1 | right panel baseline carries a small tick for every year while only every third year is labelled | 必须靠数无标签的小刻度来定位某根柱对应的年份，年份键无法直接从轴文字取得。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

右panel有32个年度槽位但只印11个标签（80、83、86…10），要把 0.33 或 3 这一根柱／点定到具体年份，必须数无标签小刻度；同时同一槽位上叠着两个系列、两条轴（Lhs 0.0–0.4 与 Rhs 0–4），所以一个值至少需要 panel名+Lhs/Rhs+系列名+年份 四个键才能唯一定位，普通解析表通常只给出 year 与一列数值，0.1 与 1 会互相混淆。左panel虽只需 panel名+系列名+年份，但值也只能靠像素读：刻度间距 10 个百分点，51 的 5% 容差仅 ±2.5，需要读到四分之一格。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 axis_assignment_in_legend（图例中以 Lhs:/Rhs: 声明系列归属的轴） | 样式字段：dual_axis 图例渲染方式，增加轴前缀分组行；记录字段中为每个系列加 axis 字段 | 双轴图：图例带 Lhs/Rhs 前缀 vs 不带前缀时，模型把值分配到正确轴的准确率 |
| P6 | 一类出版方 | right_side_y_axis 与 axis_starts_above_zero 的组合（左panel刻度在右侧且起点为30） | 条件行：value-axis 位置（left/right）与 axis_min（0 / 非0）两个维度交叉 | 值轴位于右侧且起点非零时的读数误差 vs 左侧零起点基线 |
| P6 | 通用 | sparse_time_ticks + 每年小刻度但三年一标签的时间轴 | 样式字段：tick_label_interval 与 tick_mark_interval 分离设置 | 标签间隔=3、数据点间隔=1 时，类别键（年份）定位正确率 vs 每点都有标签 |
| P3 | 这份文档自己的习惯 | panel_title_per_panel + per_panel_legend + 单一 Graph 号的多面板结构导出 | P3 的整页 markdown 导出：panel 名作为加粗行置于各自表格之上，Graph 号+标题作为上级标题 | panel 名写为表上加粗标题 vs 仅存于图内时，跨panel值定位（左51 vs 右0.33）的命中率 |
| P2 | 一类出版方 | heterogeneous_panel_types（折线panel与柱+点双轴panel同号） | 条件行：一个 figure 内允许不同 chart family 组合；panel_key 进入记录键 | 同号异类型面板 vs 同类型 small multiples 的抽值准确率对比 |
| P7 | 这份文档自己的习惯 | footnote_marker（系列名带上标 1/2/3 并对应下方编号注释） | P7 标题字段：series_name 中保留上标标记，并单列 note 文本 | 系列名含上标数字时，检索字符串匹配（'Top 10 market share1'）成功率 |
