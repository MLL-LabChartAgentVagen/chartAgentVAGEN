# World_Inequality_Report_2026_p83

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `untagged` | 10 | 0 |

该页顶部是Figure 3.8的百分比堆叠柱状图，展示2025年八个地区底层50%、中间40%和顶层10%（含top 1%与next 9%）的财富份额，下方为两栏正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 25 | `Top 1%` · `Europe` | 1% | f1 | the Europe Top 1% segment | 是 | `Europe` · `Top 1%` |
| 2 | 35 | `Next 9%` · `Europe` | 1% | f1 | the Europe Next 9% segment (also North America & Oceania Next 9% = 35%, and South & Southeast Asia Top 1% = 35%) | 是 | `Europe` · `Next 9%` |
| 3 | 37 | `Middle 40%` · `Europe` | 1% | f1 | the Europe Middle 40% segment (Middle East & North Africa Top 1% is also 37%) | 是 | `Europe` · `Middle 40%` |
| 4 | 3 | `Bottom 50%` · `Europe` | 1% | f1 | the Europe Bottom 50% segment (Latin America and Russia & Central Asia Bottom 50% also 3%) | 是 | `Europe` · `Bottom 50%` |
| 5 | 46 | `Top 1%` · `Russia & Central Asia` | 1% | f1 | the Russia & Central Asia Top 1% segment | 是 | `Russia & Central Asia` · `Top 1%` |
| 6 | 28 | `Next 9%` · `Russia & Central Asia` | 1% | f1 | the Russia & Central Asia Next 9% segment (Latin America Middle 40% is also 28%) | 是 | `Russia & Central Asia` · `Next 9%` |
| 7 | 23 | `Middle 40%` · `Russia & Central Asia` | 1% | f1 | the Russia & Central Asia Middle 40% segment | 是 | `Russia & Central Asia` · `Middle 40%` |
| 8 | 3 | `Bottom 50%` · `Russia & Central Asia` | 1% | f1 | the Russia & Central Asia Bottom 50% segment | 是 | `Russia & Central Asia` · `Bottom 50%` |
| 9 | 36 | `Top 1%` · `Sub-Saharan Africa` | 1% | f1 | the Latin America Top 1% segment (Sub–Saharan Africa Top 1% and Middle East & North Africa Next 9% also 36%) | 是 | `Latin America` · `Top 1%` |
| 10 | 1 | `Bottom 50%` · `Middle East & North Africa` | 1% | f1 | the North America & Oceania Bottom 50% segment (Sub–Saharan Africa and Middle East & North Africa Bottom 50% also 1%) | 是 | `North America & Oceania` · `Bottom 50%` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 36, 1

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 4 | 8 | 32 | 全部 | 0%, 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90%, 100% |
| f2 | `other · none present` | na | 0 | 0 | 0 | 0 | 无 | （不画值轴） |

- **f1** Figure 3.8. / Extreme wealth inequality is high in all regions / Bottom 50%, middle 40% and top 10% (top 1% and next 9%) wealth shares across the world, 2025　[图上方]　单位 `Share of personal wealth (%)`
  - 来源行：Sources and series: Arias–Osorio et al. (2025) and wir2026.wid.world/methodology.
- **f2** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each region bar stacks Bottom 50%, Middle 40%, Next 9%, Top 1% segments |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f1 | **无** | every bar reaches 100% and the axis top tick reads `100%` |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Interpretation. ...` and `Sources and series: Arias–Osorio et al. (2025)` under plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | `Top 1%  Next 9%  Middle 40%  Bottom 50%` row under the category labels |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | `Share of personal wealth (%)` carries the unit for the bare tick numbers |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | `Share of personal wealth (%)` set vertically along the left axis |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | body text `but for net household wealth.9` carries superscript 9 |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | `25%`, `35%`, `37%` printed inside the Europe bar segments |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | `3%`, `5%`, `1%` sit above/outside the very thin blue Bottom 50% slivers |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | `North America & Oceania`, `Middle East & North Africa` wrap onto three lines |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | dashed horizontal rules at each 10% tick, no vertical rules |

词表 65 项，本页出现 11 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `interpretation_note_paragraph` | f1 | `Interpretation. In Latin America, the top 1% captures 36% of national wealth...` worked example below plot | 该段落用文字复述了图中若干具体数值（如36%、33%、69%、60%），解析器可能从正文而非图表标签中抓到这些数字，导致定位到错误的标记。 |
| `aggregate_group_in_subtitle` | f1 | subtitle names `top 10% (top 1% and next 9%)` although only the two sub-series are drawn | 读者需自行把两个绘出的分段相加才能得到标题中提到的top 10%，表格行标签无法直接对应该聚合量。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

所有32个数值都直接印在段内，读数不成问题（步骤2无阻）；难点在于寻址：像`35`在图中出现三次（Europe Next 9%、North America & Oceania Next 9%、South & Southeast Asia Top 1%），`36`出现三次，`3%`与`1%`各出现三次，因此每个值必须同时携带地区名和分组名两个键才能唯一定位；而地区名在轴上被折成两三行（`North America & Oceania`、`Middle East & North Africa`），解析器容易把它们拆成不完整的列头，使4×8的表格无法用逐字标签把某一格与其他相同数字区分开。

整页原图判不出来的：
- `f2`（other）：该页除Figure 3.8外并无第二个图表，f2为占位记录，不存在可判读内容。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | wrapped_category_labels 与 pct_stacked 的组合条件 | 条件行：类别轴标签换行层数（1/2/3行）作为样式字段，配合百分比堆叠 | 新增一行：多行折叠的长类别名 vs 单行类别名，测量表格列头还原率 |
| P6 | 一类出版方 | thin_segment_label（极窄分段标签外移） | 记录字段：当分段占比≤5%时，标签放置由inside切换为outside/above | 新增一行：含≤5%薄分段的堆叠图 vs 全部分段≥10%，比较标签归属正确率 |
| P3 | 通用 | 重复数值的唯一寻址（同一值在多个类别重复出现） | 评分/键构造：要求同时给出类别名与系列名两个键 | 新增一行：数值在图中唯一 vs 数值重复≥3次时的定位准确率 |
| P3 | 这份文档自己的习惯 | interpretation_note_paragraph（图下解释性文字复述图中数字） | 页面级记录字段：图下注释文本是否包含图中数值 | 新增一行：有/无复述数值的解释段落，测量误抓正文数字的比例 |
| P7 | 通用 | rotated_axis_title 承载单位（`Share of personal wealth (%)`） | 标题块字段：unit_text 的位置枚举增加“旋转的纵轴标题” | 新增一行：单位在副标题 vs 单位在旋转轴标题时的单位还原率 |
