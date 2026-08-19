# Consultancy-in-Spain.-The-industry-in-figures-2024_p16

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Consultancy-in-Spain.-The-industry-in-figures-2024 | `untagged` | 4 | 0 |

本页为西班牙咨询业2024年报告第16页，包含两幅无编号图表：上方为按性别分组的学历构成圆头柱状图，下方为STEM学位占比的堆叠圆头柱状图，中间夹有两栏正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 63.8% | `Men` · `University graduates` | 1% | f1 | the Men / University graduates bar | 是 | `Men` · `University graduates` |
| 2 | 13.9% | `Women` · `Vocational training` | 1% | f1 | the Women / Vocational training bar | 是 | `Women` · `Vocational training` |
| 3 | 69.8% | `men` · `Degree holders in STEM fields` | 1% | f2 | the men / Degree holders in STEM fields segment | 是 | `men` · `Degree holders in STEM fields` |
| 4 | 35.1% | `Total` · `Degree holders in other fields` | 1% | f2 | the Total / Degree holders in other fields segment | 是 | `Total` · `Degree holders in other fields` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 1 | 3 | 3 | 9 | 全部 | （不画值轴） |
| f2 | `stacked_bar` | vertical | 1 | 2 | 3 | 6 | 全部 | （不画值轴） |

- **f1** Most of the consultancy industry's professionals hold university degrees / (percentage in Spain)　[图上方]　单位 `(percentage in Spain)`
  - 来源行：Source: AEC (Spanish Association of Consulting Firms)
- **f2** University degree holders from STEM areas / (percentage in Spain)　[图上方]　单位 `(percentage in Spain)`
  - 来源行：Source: AEC (Spanish Association of Consulting Firms)

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | three rounded bars side by side in each of Men, Women, Total slots |
| `stacked_bar` | 堆叠条 | f2 | 有 | each category bar splits into a lower STEM segment and an upper other-fields segment |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f2 | **无** | segments per bar sum to 100% (69.8+30.2, 55.9+44.1, 64.9+35.1) at equal heights |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only a thin baseline under Men/Women/Total; no ticks or value labels on any axis |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | only a baseline above 'men Women Total'; no value ticks drawn |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately titled charts each with its own legend and Source line |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: AEC (Spanish Association of Consulting Firms)' in small print below legend |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | 'Source: AEC (Spanish Association of Consulting Firms)' printed under the legend |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'University graduates / Vocational training / Other' dots row under the baseline |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | 'Degree holders in STEM fields / Degree holders in other fields' row below plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | heading second line reads '(percentage in Spain)' |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | heading second line reads '(percentage in Spain)' |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | '30.2%', '69.8%' etc. printed in white inside each stacked segment |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '63.8%', '22.9%', '13.3%' printed above the tops of the rounded bars |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | third slot labelled 'Total' is the aggregate next to Men and Women |

词表 65 项，本页出现 11 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `rounded_capsule_bars` | f1 | bars drawn as pill/capsule shapes with fully rounded top and bottom caps | 胶囊两端的圆角使柱端位置模糊，且底端伸出基线，按像素读数会系统性偏差。 |
| `overlapping_stack_segments` | f2 | the lower STEM capsule overlaps and covers the bottom of the upper capsule | 两段互相重叠，段长不等于其数值比例，只能依赖印出的百分比读数。 |
| `inconsistent_category_capitalization` | f2 | axis labels read 'men' lowercase while 'Women' and 'Total' are capitalized | 行名需逐字照抄'men'，若按f1的'Men'匹配会导致检索失败。 |

## 5 · 难在哪

卡在 **第四步 · 表外上下文**。

四个数值全部以文字印在图上，读数不成问题（第2步无难度）；行列名也只需两个键（类别+图例项），表格容易承载。真正的障碍是上下文：两图都没有图号，标题'Most of the consultancy industry's professionals hold university degrees'与'University degree holders from STEM areas'只以彩色大字排在图上方，解析器很可能把它当普通段落而非粗体标题；且两图共用完全相同的Source行、都用'(percentage in Spain)'副标题、类别名也都是Men/Women/Total，若标题丢失，13.9%（f1）与35.1%（f2）之类数值无法区分归属哪张图。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 一类出版方 | unit_in_axis_or_title 与标题拆分（number/title/subtitle/unit/placement） | 图表记录的heading字段，新增subtitle与unit_text分离，并允许figure_number为空 | 无编号图 + 副标题即单位 的一行：考察缺少图号时标题能否作为表格上方粗体行导出 |
| P1 | 这份文档自己的习惯 | 新组件 rounded_capsule_bars（胶囊圆端柱） | 样式条件行中的bar端点形状字段（增加 capsule/rounded_cap 取值） | 圆端柱 vs 平端柱 的一行：在无数值轴时评估按像素读数的可达精度 |
| P6 | 这份文档自己的习惯 | 新组件 overlapping_stack_segments（重叠堆叠段） | 堆叠图样式字段：段间偏移/重叠量 | 重叠堆叠 vs 严格相接堆叠 的一行：段长与数值不成比例时是否必须依赖印出标签 |
| P6 | 通用 | no_value_axis 与 value_label_inside/outside 的组合 | 样式维度中的数值标签位置与是否绘制数值轴 | 无数值轴+全标签 vs 有轴无标签 的一行：区分'读数来自文本'与'读数来自像素' |
| P3 | 一类出版方 | multi_figure_page 下同源Source与相同类别名的消歧 | 整页markdown导出记录中，表格与其所属标题的相对位置 | 一页两图共用相同类别名 的一行：检验数值-标题绑定是否正确 |
