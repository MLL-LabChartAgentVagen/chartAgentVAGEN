# US_Professional_Services_Partner_Compensation_Survey_2024_p9

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| US_Professional_Services_Partner_Compensation_Survey_2024 | `untagged` | 5 | 0 |

本页是Heidrick & Struggles薪酬调查报告的第9页，左侧为一段说明文字，右侧为一个名为“Current role information (%)”的三面板水平条形图，比较2024与2022年三个问题的回答分布。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 38 | `2024` · `6–10 years` · `How many years have you been a partner at your current firm or any other firm?` | 1% | f1 | the 2024 bar in the '6–10 years' row of the first panel | 是 | `Current role information (%)` · `How many years have you been a partner at your current firm or any other firm?` · `6–10 years` · `2024` |
| 2 | 26 | `2024` · `1–3 years` · `How many years have you been with your current firm?` | 1% | f1 | the 2024 bar in the '1–3 years' row of the second panel | 是 | `Current role information (%)` · `How many years have you been with your current firm?` · `1–3 years` · `2024` |
| 3 | 42 | `2022` · `1–3 years` · `How many years have you been in your current role?` | 1% | f1 | the 2024 bar in the '1–3 years' row of the third panel (the 2022 bar also reads 42) | 是 | `Current role information (%)` · `How many years have you been in your current role?` · `1–3 years` · `2024` |
| 4 | 2 | `2024` · `Less than 1 year` · `How many years have you been a partner at your current firm or any other firm?` | 1% | f1 | the 2024 bar in the 'Less than 1 year' row of the first panel; also the 2022 'Prefer not to answer' bar in panel 2 | 是 | `Current role information (%)` · `How many years have you been a partner at your current firm or any other firm?` · `Less than 1 year` · `2024` |
| 5 | 29 | `2022` · `More than 10 years` · `How many years have you been with your current firm?` | 1% | f1 | the 2022 bar in the 'More than 10 years' row of the second panel | 是 | `Current role information (%)` · `How many years have you been with your current firm?` · `More than 10 years` · `2022` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 5 predicted key sets miss a rule label: 42

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | horizontal | 3 | 2 | 6 | 32 | 全部 | （不画值轴） |

- **f1** Current role information (%)　[图上方]　单位 `(%)`
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=149 \| Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=153 \| Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=151

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | each row shows a dark 2024 bar above a cyan 2022 bar in the same slot |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | category names 'Less than 1 year', '1–3 years' on the left, bars grow rightward |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or gridlines; only printed numbers like 38, 39 give the values |
| `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | f1 | **无** | 'N/A' printed in the 'Prefer not to answer' row of panels 2 and 3 |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | single '2024 / 2022' legend above all three panels |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | one column of row labels at left serves all three panels |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | three panels of the same grouped-bar chart, one per survey question |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Numbers may not sum to 100%, because of rounding.' plus three 'Source:' blocks |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | a separate 'Source: ... n=149 / n=153 / n=151' line under each panel |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | '2024' and '2022' swatches between the title and the panel headings |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | each panel headed in bold by its own question text above the rows |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f1 | **无** | left column prose 'In 2024, on average, the time from when respondents joined...' beside the figure |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title reads 'Current role information (%)'; bars carry bare numbers |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | '38', '39', '42' printed at the right end inside the dark bars |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '2' and '6' sit to the right of the very short bars in the first panel |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | panel question headings wrap over four to five lines above the rows |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | thin horizontal rules separate each category row across all three panels |

词表 65 项，本页出现 17 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `per_panel_source_line` | f1 | three separate 'Source: ... 2024, n=149 / n=153 / n=151' blocks, one under each panel | 每个面板的样本量不同，读数时必须把n值绑定到对应面板，不能用整图统一来源。 |
| `matrix_row_label_column` | f1 | one left label column shared by three question panels, rows aligned like a table | 图形实际是行=区间、列=问题的矩阵，取值需要行标签与面板标题两个键共同定位。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部印在条上（2、6、38、42等），读数没有精度问题，也没有刻度轴，所以第2步不构成障碍。真正的瓶颈是定位：一个值需要四个键——面板问题标题（如“How many years have you been with your current firm?”）、行区间（如“More than 10 years”）、年份系列（2024/2022），再加上图标题。像“42”在第三面板同一行的2024和2022都出现，“2”在第一面板“Less than 1 year”的2024与第二面板“Prefer not to answer”的2022同时出现，若解析器只输出行标签和数字而丢掉面板问题或年份，值就无法唯一寻址。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P3 | 一类出版方 | per_panel_source_line（新组件） | 记录字段中的source/note，改为可按面板存放的数组，并在样式条件中加入“每面板独立来源与n值”行 | 来源行：整图单行 vs 每面板一行（含不同n），检验模型能否把n绑定到正确面板 |
| P2 | 一类出版方 | matrix_row_label_column（新组件）与 panel_key 的组合 | 面板维度进入键值（panel_key），面板标题采用长问句并作为粗体列头 | 共享行标签列的多面板矩阵 vs 各面板独立轴标签，检验四键寻址的正确率 |
| P6 | 通用 | missing_value_marker | 数据记录允许缺失槽位并以文本“N/A”渲染在条位置上 | 缺失值渲染为N/A文本 vs 直接省略该行，检验表格是否保留空槽 |
| P6 | 一类出版方 | no_value_axis 搭配 value_label_inside/outside 混用 | 样式字段：值标签位置随条长自动内外切换，且不绘制值轴 | 无值轴+全标注 vs 有刻度轴+无标注，检验取值来源对精度门槛的影响 |
| P7 | 通用 | unit_in_axis_or_title（标题内的“(%)”） | 标题字段拆分为number/title/subtitle/unit，并记录heading为above | 单位仅在标题括号内 vs 单位在轴或系列名，检验导出表是否带回百分号 |
