# World_Inequality_Report_2026_p20

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `3d_chart+need_estimate` | 10 | 10 |

本页为《Executive Summary》第20页，含Figure 8（收入与财富在各区域内部的不平等，双面板分组柱状图）及其解释注释，下方为

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 19 | `Income` · `EURO` · `Bottom 50%` | 5% | f1 | Income panel, EURO, blue Bottom 50% bar (just below the 20% gridline) | 否 | `Income` · `EURO` · `Bottom 50%` · `Share of national income (%)` |
| 2 | 42 | `Income` · `EASA` · `Middle 40%` | 5% | f1 | Income panel, EASA, green Middle 40% bar (just above 40%) | 否 | `Income` · `EASA` · `Middle 40%` · `Share of national income (%)` |
| 3 | 57 | `Income` · `LATA` · `Top 10%` | 5% | f1 | Income panel, MENA, red Top 10% bar (between 50% and 60%, level with LATA) | 否 | `Income` · `MENA` · `Top 10%` · `Share of national income (%)` |
| 4 | 10 | `Income` · `MENA` · `Bottom 50%` | 5% | f1 | Income panel, SSAF, blue Bottom 50% bar (at the 10% gridline) | 否 | `Income` · `SSAF` · `Bottom 50%` · `Share of national income (%)` |
| 5 | 73 | `Wealth` · `RUCA` · `Top 10%` | 5% | f1 | Wealth panel, MENA, red Top 10% bar (just above 70%) | 否 | `Wealth` · `MENA` · `Top 10%` · `Share of personal wealth (%)` |
| 6 | 59 | `Wealth` · `EURO` · `Top 10%` | 5% | f1 | Wealth panel, EURO, red Top 10% bar (the lowest red bar, at about 60%) | 否 | `Wealth` · `EURO` · `Top 10%` · `Share of personal wealth (%)` |
| 7 | 1 | `Wealth` · `LATA` · `Bottom 50%` | 10% | f1 | Wealth panel, NAOC, blue Bottom 50% hairline bar just above the baseline | 否 | `Wealth` · `NAOC` · `Bottom 50%` · `Share of personal wealth (%)` |
| 8 | 30 | `Wealth` · `SSEA` · `Middle 40%` | 5% | f1 | Wealth panel, SSEA, green Middle 40% bar (at the 30% gridline) | 否 | `Wealth` · `SSEA` · `Middle 40%` · `Share of personal wealth (%)` |
| 9 | 70 | `Wealth` · `EASA` · `Top 10%` | 5% | f1 | Wealth panel, EASA, red Top 10% bar (at the 70% gridline) | 否 | `Wealth` · `EASA` · `Top 10%` · `Share of personal wealth (%)` |
| 10 | 1 | `Wealth` · `NAOC` · `Bottom 50%` | 10% | f1 | Wealth panel, SSAF (or MENA), blue Bottom 50% hairline bar; the two are indistinguishable | 否 | `Wealth` · `SSAF` · `Bottom 50%` · `Share of personal wealth (%)` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 10 predicted key sets miss a rule label: 57, 10, 73, 1, 1

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 2 | 3 | 8 | 48 | 无 | 0%, 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80% |

- **f1** Figure 8. / Income and, even more, wealth are extremely concentrated at the top in every region / Inequality within regions, 2025　[图上方]　单位 `Share of national income (%)`
  - 来源行：Sources and series: wir2026.wid.world/methodology.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | three bars (blue, green, red) stand side by side in each region slot, e.g. over EURO |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one legend row 'Bottom 50% / Middle 40% / Top 10%' below both Income and Wealth panels |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | two side-by-side panels of the same grouped-bar design, titled 'Income' and 'Wealth' |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | small print below: 'Interpretation. ... Notes. EASA: East Asia ... Sources and series: wir2026.wid.world/methodology.' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend swatches sit centred beneath the two plots, above the 'Interpretation.' text |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | bold 'Income' above the left plot, bold 'Wealth' above the right plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | the '(%)' scale sits in the rotated axis titles; bars carry no printed numbers |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | 'Share of national income (%)' and 'Share of personal wealth (%)' set vertically along each y axis |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | bold lead-in markers 'Interpretation.', 'Notes.', 'Sources and series:' introduce the note block under the plots |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | region codes EURO, EASA, NAOC... are turned about 45 degrees under both axes |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | category axis reads codes 'EURO, EASA, NAOC, RUCA, SSAF, SSEA, MENA, LATA' |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | dotted horizontal rules at each 10% level in both panels, no vertical rules |

词表 65 项，本页出现 12 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `per_panel_category_order` | f1 | Income axis order EURO, EASA, NAOC, RUCA...; Wealth axis order EURO, SSEA, NAOC, LATA, EASA... | 同一区域在两个面板处于不同横轴位置，读值时不能按位置对应，必须同时用面板名与区域码定位，否则会把 Income 的第2槽误读为 Wealth 的第2槽。 |
| `sorted_by_one_series` | f1 | note says 'The figures are arranged according to top 10% shares'; red bars rise left to right in each panel | 类别顺序由 Top 10% 系列大小决定而非固定名单，读表时行序本身携带信息，重排会破坏与图的一致性。 |
| `near_zero_mark` | f1 | Wealth panel Bottom 50% bars for NAOC, SSAF, MENA are hairlines barely above the 0% baseline | 这些柱高不足一个像素级刻度间距的1/10，按5%相对容差读数不可行，只能标注为约0–1%。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

刻度间距为10个百分点，图上一格约27像素，故1个百分点≈2.7像素。Wealth 面板中 NAOC、SSAF、MENA 的 Bottom 50% 柱只有1–2像素高，要落在1的±5%（即0.95–1.05）区间内在物理上不可能；59、73 这类无标注的红柱也只能凭0%–80%共9条网格线目测，误差常达±1.5个百分点，对59而言容差仅±2.95，勉强边缘。相比之下定址虽需三键（面板名 Income/Wealth + 区域码 + 系列名），但这些标签都以粗体面板标题、旋转轴刻度和图例文字明确印出，可被表格承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | 新组件 per_panel_category_order（面板各自排序的类别轴） | 记录字段：为每个 panel 单独存 category order，并在 panel_key 中携带面板名 | 两面板类别顺序一致 vs 不一致时的取值命中率对比 |
| P1 | 通用 | 新组件 near_zero_mark（接近0的极细柱） | readable 判定：把每个 mark 的可达精度改为随柱高变化的连续量，而非整图布尔门 | 柱高<3像素的 mark 单独统计可读精度上限 |
| P3 | 通用 | panel_title_per_panel 与 rotated_axis_title 的表外语境 | 整页 markdown 导出：面板名以粗体小标题写在对应表格上方，轴标题作为单位列 | 面板名写为粗体标题 vs 仅在表头单元格内时的定址成功率 |
| P6 | 通用 | unit_in_axis_or_title（单位只存在于旋转轴标题的 '(%)'） | 样式维度：单位位置（轴标题/副标题/系列名）作为可控变量 | 单位在旋转轴标题 vs 在副标题时的单位恢复率 |
