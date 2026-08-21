# (Web_version)_E-Government_Survey_2024_1392024_p93

![(Web_version)_E-Government_Survey_2024_1392024_p93](../../data/pages/(Web_version)_E-Government_Survey_2024_1392024_p93.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `(Web_version)_E-Government_Survey_2024_1392024_p93` | (Web_version)_E-Government_Survey_2024_1392024 | untagged | 5 | `parsebench/data/pages/(Web_version)_E-Government_Survey_2024_1392024_p93.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 一张水平分组条形图：14 条类别标签（如 "Portal can be found on search engine"、"Specific service transactions initiated through the portal can be saved and accessed later" 需换行），每类两根条（2024 深蓝、2022 黄），共 28 根条，每根条上都印百分比标签。类别被两处空行分成三组（无组标题），x 轴为 "0%…100%"，图例 "2024 / 2022" 置于绘图区内右下方。标题行为 "Figure 2.27  Number of Member States with portals incorporating the assessed technology features, 2022 and 2024"，下方绿色横条，图下有 "Sources: 2022 and 2024 United Nations E-Government Surveys."。
> 
> **定位一个值难在哪**
> 
> 取 50%：它是 "Individuals can  modify their own data online" 的 2022 黄条。标题说 "Number of Member States"，但轴与标签全是百分比，单位口径矛盾；类别名内含双空格，且 50 与同图 56、58 等值多次重复，缺少年份键就无法唯一定位。
> 
> **不确定的**
> 
> 三组之间的空行是否代表未印出的分组标题；图例是否恰好落在绘图框内；长标签的换行位置是否为原始文本的一部分。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 需绘制单面板横向分组条形图：14个长类别、2024与2022两系列、共28条；百分比标签置于条内，图例在绘图区右下，类别分成三个无标题区段。标题须拆分图号、主标题、副标题，并保留图框与来源行。
> 
> **定位一个值难在哪**
> 
> “71”出现两次：2022年的“There is a sitemap (or index)”和2024年的“Businesses can access their own data online”。唯一定位必须同时保留完整类别和年份。
> 
> **不确定的**
> 
> 题目未说明目标“71”指哪一处；spot check按2024年企业访问自身数据的条形记录。百分比单位仅见于刻度和数值标签，没有独立轴标题。

**gemini-3.1-pro**

> ### 画出来要什么
> 页面包含一个水平分组条形图。图表生成器需要支持绘制水平方向的分组条形，并且分类轴需要支持长文本标签的处理（包括自然换行）。绘图区背景仅包含垂直方向的网格线。同时，图例需要能够被放置在绘图区内部的右下角位置。数值标签需要支持根据条形长度动态判断：当条形较长时，标签放置在条形内部；当条形较短时，标签放置在条形外部。
> 
> ### 定位一个值难在哪
> 定位“50”需要对应的类别标签“Individuals can  modify their own data online”和年份系列“2022”。在原始图片中，该类别标签的“can”与“modify”之间存在明显的连续空格，且其他部分标签存在换行。这种非标准排版容易导致文本解析和提取时被规范化为单空格或丢失换行，从而在第三步严格匹配键值时发生阻断。
> 
> ### 不确定的
> 图表的标题提到了“Number of Member States”（成员国数量），但底部的X轴和所有的数据标签均显示为百分比（从0%到100%），由于页面没有提供各年份成员国总数的基数，无法确切知道每个百分比对应的绝对数量。这里只能假定百分比是其主要展示意图。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | grouped_bar | 28 | Figure 2.27 | above | all |
| opus-5 | f2 | unreadable | 0 | — | none | none |
| gpt-5.6-sol | f1 | grouped_bar | 28 | Figure 2.27 | above | all |
| gemini-3.1-pro | f1 | grouped_bar | 28 | Figure 2.27 | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: two bars per feature row, blue 2024 above yellow 2022, e.g. 98% and 98%；gpt-5.6-sol: Blue 2024 and yellow 2022 bars appear side by side for each category.；gemini-3.1-pro: two bars per category representing 2024 and 2022 |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: feature names on left axis, bars grow rightwards to the 0%-100% scale；gpt-5.6-sol: Category labels are left of bars growing horizontally toward 100%.；gemini-3.1-pro: categories lie on the left axis, bars grow rightwards |
| `legend_inside_plot` | ✓ | ✓ | ✓ | opus-5: '2024' and '2022' swatches drawn inside the plot frame at lower right；gpt-5.6-sol: The “2024” and “2022” legend is inside the lower-right plot area.；gemini-3.1-pro: the legend for 2024 and 2022 sits inside the bottom right of the plot |
| `panel_background` | ✓ | — | — | opus-5: whole chart sits inside a thin bordered white box under a green rule |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Sources: 2022 and 2024 United Nations E-Government Surveys.' below the frame；gpt-5.6-sol: “Sources: 2022 and 2024 United Nations E-Government Surveys.” appears below the figure.；gemini-3.1-pro: Sources: 2022 and 2024 United Nations E-Government Surveys... printed below the plot |
| `unit_in_axis_or_title` | ✓ | — | — | opus-5: axis ticks read '0%' ... '100%'; title says 'Number of Member States' |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: '98%' printed at right end of blue bar and left end of yellow bar, inside fill；gpt-5.6-sol: Percentages including “91%”, “83%” and “27%” are printed inside their bars.；gemini-3.1-pro: the 98% label sits inside the blue bar |
| `value_label_outside` | — | — | ✓ | gemini-3.1-pro: the 91% label sits just beyond the end of the blue bar |
| `vgrid_only` | — | — | ✓ | gemini-3.1-pro: vertical grid lines at 10% intervals, no horizontal lines |
| `wrapped_category_labels` | ✓ | ✓ | ✓ | opus-5: 'Specific service transactions initiated through the portal can be saved and accessed later' wraps to two lines；gpt-5.6-sol: “Specific service transactions initiated through the portal can be saved and accessed later” wraps onto two lines.；gemini-3.1-pro: the label for Specific service transactions... wraps onto two lines |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `blank_row_category_grouping` | opus-5 | 3 | two blank slots split the 14 rows into groups of 7, 4, 3 with no group titles |
| `title_unit_contradicts_axis` | opus-5 | 2,4 | title 'Number of Member States' but every label and tick is a percentage |
| `category_axis_line_as_group_bracket` | opus-5 | 3 | a short vertical rule runs beside each block of rows at the axis origin |
| `unlabeled_category_section_gaps` | gpt-5.6-sol | — | Blank horizontal gaps divide the 14 category rows into three groups without group labels. |
| `plot_frame_border` | gpt-5.6-sol | — | A thin black rectangle encloses the complete chart and legend area. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 91 | Portal is developed using responsive web design、2024 | Portal is developed using responsive web design、2024 | Portal is developed using responsive web design、2024 | Portal is developed using responsive web design、2024 | ✓ | ✓ | ✓ | 过 |
| 83 | Portal has been updated in the last month、2022 | Portal has been updated in the last month、2022 | Portal has been updated in the last month、2022 | Portal has been updated in the last month、2022 | ✓ | ✓ | ✓ | 过 |
| 71 | Businesses can access their own data online、2024 | Businesses can access their own data online、2024 | Businesses can access their own data online、2024 | Businesses can access their own data online、2024 | ✓ | ✓ | ✓ | 过 |
| 50 | Individuals can modify their own data online、2022 | Individuals can  modify their own data online、2022 | Individuals can modify their own data online、2022 | Individuals can  modify their own data online、2022 | ✓ | ✓ | ✓ | 过 |
| 27 | Portal offers AI-enabled chatbot functionality、2024 | Portal offers AI-enabled chatbot functionality、2024 | Portal offers AI-enabled chatbot functionality、2024 | Portal offers AI-enabled chatbot functionality、2024 | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
