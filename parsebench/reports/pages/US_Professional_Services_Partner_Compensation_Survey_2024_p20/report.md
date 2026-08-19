# US_Professional_Services_Partner_Compensation_Survey_2024_p20

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| US_Professional_Services_Partner_Compensation_Survey_2024 | `untagged` | 5 | 0 |

该页为《2024 US PROFESSIONAL SERVICES PARTNER COMPENSATION SURVEY》第20页，左侧为两段正文，右侧并列两个无编号的百分比横向堆积条形图，分别按公司类型和公司收入拆分外部因素对前景的影响。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 34 | `Management/advisory consulting` · `Pessimistic` | 1% | f1 | the Management/ advisory consulting Pessimistic segment | 是 | `Key external factors influencing outlook for current fiscal year, by firm type` · `Management/ advisory consulting` · `Pessimistic` |
| 2 | 28 | `Technology/IT consulting` · `Optimistic` | 1% | f1 | the Technology/IT consulting Optimistic segment | 是 | `Key external factors influencing outlook for current fiscal year, by firm type` · `Technology/IT consulting` · `Optimistic` |
| 3 | 83 | `$1.00bn–$5.00bn` · `Optimistic` | 1% | f2 | the $1.00bn–$5.00bn Optimistic segment | 是 | `Key external factors influencing outlook for current fiscal year, by firm revenue` · `$1.00bn–$5.00bn` · `Optimistic` |
| 4 | 38 | `More than $20.00bn` · `Neutral` | 1% | f2 | the More than $20.00bn Neutral segment | 是 | `Key external factors influencing outlook for current fiscal year, by firm revenue` · `More than $20.00bn` · `Neutral` |
| 5 | 31 | `$5.01bn–$20.00bn` · `Pessimistic` | 1% | f2 | the $5.01bn–$20.00bn Pessimistic segment | 是 | `Key external factors influencing outlook for current fiscal year, by firm revenue` · `$5.01bn–$20.00bn` · `Pessimistic` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | horizontal | 1 | 3 | 4 | 12 | 全部 | （不画值轴） |
| f2 | `stacked_bar` | horizontal | 1 | 3 | 4 | 12 | 全部 | （不画值轴） |

- **f1** Key external factors influencing outlook (%) / Key external factors influencing outlook for current fiscal year, by firm type　[图上方]　单位 `(%)`
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=142
- **f2** Key external factors influencing outlook for current fiscal year, by firm revenue　[图上方]　（标题里没有单位）
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=142

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each row is one bar of three coloured segments, e.g. 23 \| 36 \| 41 for Strategy consulting |
| `stacked_bar` | 堆叠条 | f2 | 有 | each revenue row is one bar of three segments, e.g. 31 \| 35 \| 35 |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f1 | **无** | all four bars end at the same right edge; segments sum to 100 (23+36+41) |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f2 | **无** | all four bars reach the same full length; 18+21+61 = 100 |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | category names sit at the left, bars grow rightward from a common left edge |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f2 | **无** | `Less than $1.00bn` etc. on the left, bars run to the right |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or baseline numbers anywhere; values readable only from printed segment labels |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | no percentage axis drawn under or over the bars |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately captioned charts, `...by firm type` and `...by firm revenue`, each with own legend and source |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Note: Numbers may not sum to 100%, because of rounding.` and `Source: Heidrick & Struggles ...` below plot |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | identical Note and Source lines printed under the second chart |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | `Pessimistic Neutral Optimistic` swatch row between the subtitle and the first bar |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f2 | 有 | same three-swatch legend row sits above `Less than $1.00bn` |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | left column prose `By firm type, technology and IT firms...` runs level with each chart |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | `Key external factors influencing outlook (%)` is the only place the percent scale is stated |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | `23`, `36`, `41` printed inside their segments, right-aligned within each segment |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | `18`, `21`, `61` printed inside the segments of the first row |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f2 | **无** | in `$1.00bn–$5.00bn` the labels `9` and `9` crowd two very narrow segments |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | `Management/ advisory consulting` label wraps onto two lines beside its bar |

词表 65 项，本页出现 12 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `unit_heading_shared_across_sibling_figures` | page | `(%)` appears only in the top heading above f1; f2's own caption states no unit | 读第二张图的数字时，单位必须从页面上方另一张图的标题继承，若解析器按图切块，f2 的数值就失去 % 标度。 |
| `sibling_figures_share_title_stem` | page | both captions begin `Key external factors influencing outlook for current fiscal year, by ...` | 两图标题仅结尾 `by firm type` / `by firm revenue` 不同，定位某个数值时必须读到标题末尾才能区分归属。 |
| `segment_label_right_aligned_in_segment` | f1 | `36` sits at the right edge of the grey segment, close to the next segment's start | 标签紧贴分段边界，容易被误配到相邻系列，需要按颜色而非位置判断该数属于哪个系列。 |

## 5 · 难在哪

卡在 **第四步 · 表外上下文**。

数值本身全部印在分段内（34、28、83、38、31），没有刻度轴，读数误差为零，第2步不构成障碍；行列标签也只需 2 个键（类别＋Pessimistic/Neutral/Optimistic），一张表就能承载。真正卡住的是上下文：两图标题前 9 个词完全相同，只有 `by firm type` 与 `by firm revenue` 之别，而 `(%)` 单位只写在 f1 上方的总标题里；同时正文里已出现 `at only 28%` 和 `83% reported feeling optimistic`，检索时 28 与 83 可能命中散文而非图表行，只有当图标题以粗体/标题形式紧贴表格出现，才能把数值判给正确的那张图。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 一类出版方 | 新组件 unit_heading_shared_across_sibling_figures（同页多图共用一个带单位的总标题） | 标题记录字段：把 figure 级 heading 拆为 page_section_heading 与 figure_caption，unit 可继承自上层 | 单位写在本图标题内 vs 单位仅写在上一级共享标题内，比较数值＋单位同时命中率 |
| P3 | 这份文档自己的习惯 | 新组件 sibling_figures_share_title_stem（两图标题仅末尾修饰词不同） | 整页 markdown 导出条件行：同页生成两个标题前缀相同的图，标题作为表格上方粗体行 | 标题前缀相同 vs 完全不同的两图同页，测量数值归属错配率 |
| P6 | 通用 | thin_segment_label 与 value_label_inside 的组合（9\|9 这类窄段内标签） | 样式字段 value-label placement：新增窄段自动外移/保留段内两种取值 | 窄段标签保留段内 vs 移出段外，比较标签与系列的配对准确率 |
| P4 | 一类出版方 | no_value_axis + pct_stacked 的百分比堆积横条（无刻度、全靠印字） | 图族权重向量中提高“无轴百分比横向堆积条”的采样比例 | 有百分比刻度轴 vs 无轴仅印标签的堆积条，测量取值可得率 |
