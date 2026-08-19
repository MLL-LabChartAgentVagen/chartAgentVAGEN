# US_Professional_Services_Partner_Compensation_Survey_2024_p14

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| US_Professional_Services_Partner_Compensation_Survey_2024 | `untagged` | 5 | 0 |

本页是Heidrick & Struggles 2024美国专业服务合伙人薪酬调查第14页，包含两组关于是否需要给初级顾问加薪的100%堆叠横条图（按公司类型和按公司营收划分），左侧配有说明性文字栏。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 49 | `Strategy consulting` · `No` | 1% | f1 | the 'Strategy consulting' row's 'No' segment | 是 | `Junior talent (%)` · `By firm type` · `Strategy consulting` · `No` |
| 2 | 54 | `Management/advisory consulting` · `Yes, to attract and/or retain them` | 1% | f1 | the 'Management/advisory consulting' row's 'Yes, to attract and/or retain them' segment | 是 | `By firm type` · `Management/advisory consulting` · `Yes, to attract and/or retain them` |
| 3 | 16 | `Technology/IT consulting` · `Don't know/prefer not to say` | 1% | f1 | the 'Technology/IT consulting' row's 'Don't know/prefer not to say' segment | 是 | `By firm type` · `Technology/IT consulting` · `Don't know/prefer not to say` |
| 4 | 36 | `Less than $1.00bn` · `No` | 1% | f2 | the 'Less than $1.00bn' row's 'No' segment | 是 | `By firm revenue` · `Less than $1.00bn` · `No` |
| 5 | 64 | `$5.01bn–$20.00bn` · `Yes, to attract and/or retain them` | 1% | f2 | the '$5.01bn–$20.00bn' row's 'Yes, to attract and/or retain them' segment | 是 | `By firm revenue` · `$5.01bn–$20.00bn` · `Yes, to attract and/or retain them` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | horizontal | 1 | 4 | 5 | 19 | 全部 | （不画值轴） |
| f2 | `stacked_bar` | horizontal | 1 | 4 | 5 | 19 | 全部 | （不画值轴） |

- **f1** Junior talent (%) / In your most recent fiscal year, did your firm have to pay junior consultants notably more than in prior years? By firm type　[图上方]　单位 `(%)`
- **f2** In your most recent fiscal year, did your firm have to pay junior consultants notably more than in prior years? / By firm revenue　[图上方]　（标题里没有单位）
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=143

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each row stacks No / Yes / It varied / Don't know segments into one bar |
| `stacked_bar` | 堆叠条 | f2 | 有 | rows such as 'Less than $1.00bn' stack 36, 45, 9, 9 in one bar |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f1 | **无** | heading 'Junior talent (%)'; segments 38+48+6+8 fill every bar to equal length |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f2 | **无** | every bar reaches the same right edge; 28+64+8 sums to 100 |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | category names sit at left, bars grow rightward from a common left edge |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f2 | **无** | 'More than $20.00bn' row bar runs left to right |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or baseline numbers; values only from printed segment labels |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | no percentage axis drawn under the bars at all |
| `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | f2 | **无** | '$5.01bn–$20.00bn' row shows only 28, 64, 8 — no 'It varied' segment or label |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separate question headings and bar blocks separated by a horizontal rule |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | 'Note: Numbers may not sum to 100%, because of rounding.' and 'Source: Heidrick & Struggles...' |
| `per_panel_legend` | 每个面板各有一个图例 | page | 有 | each of the two figures carries its own identical four-entry legend |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | four-key legend row sits between 'By firm type' and the Overall bar |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f2 | 有 | legend row repeated between 'By firm revenue' and the Overall bar |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | left column prose 'Strategy consulting respondents least often said...' runs level with the bars |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title reads 'Junior talent (%)' while bars carry bare numbers 38, 48, 6, 8 |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | 38, 48, 6 printed inside their segments; 8 inside pale segment |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | '28' and '64' set within the dark and cyan segments |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | '54 3 2' crowd in the Management/advisory row's narrow grey and pale segments |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 'Management/advisory consulting' wraps onto two lines at the left |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | 'Overall' row set apart above a gap as the aggregate of the four firm types |

词表 65 项，本页出现 15 项，其中我们画不出来的 9 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `repeated_question_stem_heading` | page | both figures print the same question 'did your firm have to pay junior consultants notably more...' with different 'By ...' lines | 两图标题几乎相同，只有'By firm type'与'By firm revenue'区分，取值时必须靠该副标题行才能定位到正确的表格。 |
| `omitted_zero_segment` | f2 | '$5.01bn–$20.00bn' bar has three segments only; the grey 'It varied' category is absent | 该行缺一个系列，表格里对应单元格应为0或空白，若按四段对齐读数会错位。 |
| `unit_only_in_first_figure_title` | f2 | '(%)' appears only in 'Junior talent (%)' above f1; f2 heading has no unit | 第二图的百分号需从上方第一图的标题继承，单独抽取f2时数值单位无从确定。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

所有数值都印在段内，读数不成问题（步骤2无风险，也无刻度轴可言）；难点在寻址：两图问题文字逐字相同，'Overall'和'38 48 6 8'在两图中完全重复，一个值至少需要三把钥匙——'By firm type'或'By firm revenue'、行名（如'$5.01bn–$20.00bn'）、以及四个冗长的图例名之一（'Yes, to attract and/or retain them'长达8个词）。若解析器只输出两张无标题的4列表，49与43、48这类重复数字将无法唯一定位；另外'$5.01bn–$20.00bn'行只有三段，列对齐一旦按位置推断就会把64错配到'It varied too much to say'。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | pct_stacked 与 no_value_axis 组合（100%堆叠横条、完全无数值轴、只靠段内标签） | 图表样式条件行中新增'无数值轴+全部段内数值标签'的横向百分堆叠样式 | 有刻度轴 vs 仅段内标签：检验取值是否依赖轴刻度而非印刷标签 |
| P7 | 这份文档自己的习惯 | 新组件 repeated_question_stem_heading / unit_only_in_first_figure_title（同页两图标题近乎相同，单位只在首图） | 记录字段中把heading拆为number/title/subtitle/unit，并允许同页多图共享标题前缀 | 副标题（By firm type / By firm revenue）是否随表输出：检验同题异切片图的可区分度 |
| P2 | 一类出版方 | 新组件 omitted_zero_segment（某行缺少一个系列段） | 数据记录字段允许系列值为空/0并在渲染时跳过该段 | 完整四段 vs 含缺段行：检验按位置对齐列时的错配率 |
| P3 | 一类出版方 | side_text_bullets（左侧文字栏与图并列成一个横带） | 页面布局条件行加入'图旁正文栏' | 有无并列文字栏：检验整页markdown导出时标题与表格的相对位置是否仍可恢复 |
| P6 | 通用 | thin_segment_label（'54 3 2'挤在窄段内） | 标签放置样式字段中加入窄段标签溢出/外移策略 | 窄段标签重叠 vs 正常间距：检验小数值（2、3）的抽取召回率 |
