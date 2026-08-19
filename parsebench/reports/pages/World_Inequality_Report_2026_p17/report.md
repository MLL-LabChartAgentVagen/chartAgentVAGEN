# World_Inequality_Report_2026_p17

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `need_estimate` | 10 | 10 |

本页上半部为“Figure 5”分组柱状图（1990–2025年八个地区女性劳动收入份额，含红色虚线性别平等参考线），下半部为两栏正文“Political cleavages and democracy”。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 16 | `Middle East & North Africa` · `2025` | 1% | f1 | the 2025 (green) bar of Middle East & North Africa, labelled "16%" | 是 | `Middle East & North Africa` · `2025` |
| 2 | 20 | `South & Southeast Asia` · `2025` | 1% | f1 | the 2025 (green) bar of South & Southeast Asia, labelled "20%" | 是 | `South & Southeast Asia` · `2025` |
| 3 | 28 | `Sub-Saharan Africa` · `2025` | 1% | f1 | the 2025 (green) bar of Sub–Saharan Africa, labelled "28%" | 是 | `Sub–Saharan Africa` · `2025` |
| 4 | 34 | `East Asia` · `2025` | 1% | f1 | the 2025 (green) bar of East Asia, labelled "34%" | 是 | `East Asia` · `2025` |
| 5 | 36 | `Latin America` · `2025` | 1% | f1 | the 2025 (green) bar of Latin America, labelled "36%" | 是 | `Latin America` · `2025` |
| 6 | 37 | `Russia & Central Asia` · `2025` | 1% | f1 | the 2025 (green) bar of Russia & Central Asia, labelled "37%" | 是 | `Russia & Central Asia` · `2025` |
| 7 | 40 | `Europe` · `2025` | 1% | f1 | the 2025 (green) bar of Europe, labelled "40%" | 是 | `Europe` · `2025` |
| 8 | 40 | `North America & Oceania` · `2025` | 1% | f1 | the 2025 (green) bar of North America & Oceania, labelled "40%" | 是 | `North America & Oceania` · `2025` |
| 9 | 15 | `Middle East & North Africa` · `1990` | 10% | f1 | an unlabelled Middle East & North Africa bar (1990/2000/2010/2020 all sit just above 15%), read against the axis | 否 | `Middle East & North Africa` · `1990` |
| 10 | 33 | `Europe` · `1990` | 5% | f1 | an unlabelled first bar near 33%: Europe 1990 (or North America & Oceania 1990), read against the axis | 否 | `Europe` · `1990` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——10 values given, 11 answered

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 1 | 5 | 8 | 40 | 部分 | 0%, 10%, 20%, 30%, 40%, 50%, 60% |
| f1 | `grouped_bar` | vertical | 1 | 5 | 8 | 40 | 部分 | 0%, 10%, 20%, 30%, 40%, 50%, 60% |

- **f1** Figure 5. / Women persistently receive lower labor income than men everywhere / Female labor income shares, 1990–2025　[图上方]　单位 `Female labor income share (%)`
  - 来源行：Sources and series: Neef and Robilliard (2021), Gabrielli et al. (2024), and wir2026.wid.world/methodology.
- **f1** Figure 5. / Women persistently receive lower labor income than men everywhere / Female labor income shares, 1990–2025　[图上方]　单位 `Female labor income share (%)`
  - 来源行：Sources and series: Neef and Robilliard (2021), Gabrielli et al. (2024), and wir2026.wid.world/methodology.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | five bars (1990, 2000, 2010, 2020, 2025) side by side in each region slot |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | red dashed horizontal rule at 50% labelled "Gender parity" |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | red text "Gender parity" drawn inside the plot above the dashed line |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Interpretation. ..." and "Sources and series: Neef and Robilliard (2021)..." below plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | colour swatches with 1990 2000 2010 2020 2025 in a row under the category axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis title reads "Female labor income share (%)"; ticks are 0%–60% |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "Female labor income share (%)" set vertically along the left axis |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | body text "broken down.3" carries a superscript footnote digit |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | "16%", "20%", "28%", "34%", "36%", "37%", "40%", "40%" printed above each group's 2025 bar |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | "Middle East & North Africa" and "North America & Oceania" wrap onto three lines |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | dotted horizontal grid lines at 10% steps, no vertical rules |

词表 65 项，本页出现 11 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `label_only_on_latest_series` | f1 | only the green 2025 bar of each group carries a printed % label; 1990–2020 bars unlabelled | 表格若只抄写打印标签，就只能得到2025年的八个值；其余32根柱必须靠像素对轴读数，取值键必须包含年份系列名。 |
| `legend_swatch_only_series_names` | f1 | legend entries are bare years "1990 2000 2010 2020 2025" acting as the only series names | 系列名即年份，定位一个值需要“地区+年份”两个键，缺一即无法唯一寻址。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

八个打印标签（16%–40%）容易抓取，真正卡住的是未标注的32根柱：网格线间距为10个百分点（约35像素），而5%容差在15%这一档只有±0.75个百分点，即不到3像素；同组五根柱宽约7像素且高度差常在1个百分点以内（如中东北非1990–2025几乎重叠于15–16%），像素读数无法稳定分辨15与16。相比之下寻址只需“地区+年份”两个键，标题与副标题也都在图上方以粗体呈现，风险小于取值。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 为分组柱图增加“仅最新系列带值标签”的样式维度（value_label_outside 只作用于一个系列） | 样式字段 value_label_placement 增加 per-series 开关；记录字段标注哪些 mark 有打印值 | “全部柱带标签 vs 仅一个系列带标签”对取值准确率的影响行 |
| P6 | 通用 | reference_line（带图内文字标注的水平阈值线，如 "Gender parity" 50%） | 条件行加入 reference_line + annotation_callout 组合，位置为轴内文本 | 有/无图内参考线与其文字标注时，模型误把参考线当数据系列的比例 |
| P7 | 一类出版方 | heading 五段拆分：figure_number "Figure 5."、title、副标题 "Female labor income shares, 1990–2025"、单位来自旋转轴标题 | P7 的标题字段中把 unit 来源允许指向 rotated axis title 而非副标题 | 单位位于旋转轴标题 vs 位于副标题时，导出表能否还原百分比刻度 |
| P3 | 通用 | wrapped_category_labels（三行换行的长地区名） | 类别标签渲染样式：允许多行换行与 en dash（"Sub–Saharan Africa"） | 类别名单行 vs 多行换行时，寻址键匹配成功率 |
