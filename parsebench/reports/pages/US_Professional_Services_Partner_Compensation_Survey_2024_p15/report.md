# US_Professional_Services_Partner_Compensation_Survey_2024_p15

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| US_Professional_Services_Partner_Compensation_Survey_2024 | `untagged` | 5 | 0 |

Heidrick & Struggles 报告第15页「Attracting diverse talent」，左栏正文旁并列两个无编号横向条形图：2024/2022 分组对比与按公司类型的百分比堆叠。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 27 | `Yes` · `2024` | 1% | f1 | the 'Yes' row, dark navy 2024 bar; the same number also appears as the 'Overall' Yes segment in f2 | 是 | `Diverse talent (%)` · `Yes` · `2024` |
| 2 | 19 | `No` · `2022` | 1% | f1 | the 'No' row, cyan 2022 bar; 19 also appears twice in f2 (Management/advisory and Other, last segment) | 是 | `Diverse talent (%)` · `No` · `2022` |
| 3 | 36 | `Technology/IT consulting` · `Yes` | 1% | f2 | the 'Technology/IT consulting' Yes segment (first, navy) | 是 | `By firm type` · `Technology/IT consulting` · `Yes` |
| 4 | 55 | `Strategy consulting` · `No` | 1% | f2 | the 'Strategy consulting' No segment (second, cyan) | 是 | `By firm type` · `Strategy consulting` · `No` |
| 5 | 29 | `Management/advisory consulting` · `Yes` | 1% | f2 | the 'Management/advisory consulting' Yes segment (first, navy) | 是 | `By firm type` · `Management/advisory consulting` · `Yes` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | horizontal | 1 | 2 | 4 | 8 | 全部 | （不画值轴） |
| f2 | `stacked_bar` | horizontal | 1 | 4 | 5 | 20 | 全部 | （不画值轴） |

- **f1** Diverse talent (%) / In your most recent fiscal year, did your firm pay a premium to attract or retain diverse consultants at any level?　[图上方]　单位 `(%)`
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=144
- **f2** In your most recent fiscal year, did your firm pay a premium to attract or retain diverse consultants at any level? / By firm type　[图上方]　（标题里没有单位）
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=144

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | two bars per row, dark navy '2024' above cyan '2022', e.g. 27 over 49 at 'Yes' |
| `stacked_bar` | 堆叠条 | f2 | 有 | each row is one bar of four segments: 27 \| 40 \| 12 \| 21 for 'Overall' |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f2 | **无** | all five rows end at the same right edge and segments sum to 100 (27+40+12+21) |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | category names 'Yes', 'No' sit at left, bars grow rightward from a common baseline |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f2 | **无** | 'Overall', 'Strategy consulting' at left, stacks run right from a shared left edge |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or gridlines; numbers 27, 49, 40, 19 readable only as printed labels |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | no tick row under the stacks; only the printed segment numbers |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately captioned charts, each with its own legend, Note and Source lines |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Numbers may not sum to 100%, because of rounding.' and 'Source: Heidrick & Struggles US...' |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | same Note and Source pair printed under the five stacked rows |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | '2024  2022' swatch row between the question heading and the first bar |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f2 | 有 | 'Yes  No  It varied too much to say  Don't know/prefer not to say' row above 'Overall' |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | left column prose 'Meanwhile, significantly fewer respondents...' runs level with both charts |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title reads 'Diverse talent (%)' while bars carry bare numbers 27, 49 |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | 27, 49, 40, 19, 12, 8, 21, 23 printed within the coloured bars, right-aligned |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | each segment carries its number inside it, e.g. 18, 55, 7, 20 on 'Strategy consulting' |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 'It varied too much to say' and 'Don't know/prefer not to answer' each wrap onto two lines |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f2 | **无** | 'Management/advisory consulting' wraps onto two lines at the left of its bar |

词表 65 项，本页出现 12 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `question_text_as_figure_heading` | page | both charts headed by the bold survey question 'In your most recent fiscal year, did your firm pay a premium...' | 两图标题几乎逐字相同，只有 'Diverse talent (%)' 与 'By firm type' 能区分，取值时必须靠这两行定位所属图。 |
| `near_duplicate_series_labels_across_figures` | page | f1 says 'Don't know/prefer not to answer', f2 legend says 'Don't know/prefer not to say' | 同一含义的类别在两图用词差一字，按标签检索 21/23 与 19/28 时容易错配到另一图。 |
| `aggregate_row_not_highlighted` | f2 | 'Overall' is the first row, drawn in the same four colours as the firm-type rows | Overall 是总体而非一种公司类型，若不额外标注，27 会被误读成某类公司的值。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

所有数值都印在条上，读数无误差，第2步不构成障碍；难点是寻址。27 同时是 f1 的 Yes/2024 和 f2 的 Overall/Yes；19 出现三次（f1 No/2022、f2 Management/advisory 末段、f2 Other 末段）；31 在 Other 行连续出现两次，12、20、19 也重复。要唯一定位一个值，f1 需「类别+年份」两键，f2 需「行名+图例名」两键，而 f2 的四个图例名很长（'It varied too much to say'）且与 f1 的类别名几乎同文，解析器若只输出数字序列或把堆叠段落合成一行，就无法把 55 绑定到 'Strategy consulting'+'No'。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | pct_stacked 与 no_value_axis 组合（百分比堆叠、无刻度轴、全部标签内置） | 条件行中的 value_axis 开关与 value_label 位置字段（inside/outside） | 新增「百分比堆叠且不画值轴、数值只以内置标签呈现」一行，对照「画 0–100 刻度轴」，检验模型是否依赖轴刻度还是标签文本 |
| P7 | 一类出版方 | 无编号图的标题结构：figure_number 为空、问句作 title、'By firm type' 作 subtitle、'(%)' 作 unit | 标题记录字段拆分（number/title/subtitle/unit/placement）与页面级导出 | 新增「同页两图标题文本近乎相同，仅靠 subtitle 区分」一行，测量上下文键缺失时的错配率 |
| P3 | 一类出版方 | side_text_bullets（左侧正文栏与图并列同一横带） | 整页 markdown 导出的版式条件行：文本列 + 图表列 | 新增「图与正文同带排版」一行，检验表格上方的粗体标题是否仍被正确归到对应图 |
| new | 这份文档自己的习惯 | near_duplicate_series_labels_across_figures（两图类别名仅差一词） | 记录层的 series/category 名称生成，允许同页出现近似重复标签 | 新增「同页近似同名类别」一行，与「同页标签完全互异」对照，量化寻址混淆 |
