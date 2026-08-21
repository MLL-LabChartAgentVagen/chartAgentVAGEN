# US_Professional_Services_Partner_Compensation_Survey_2024_p19

![US_Professional_Services_Partner_Compensation_Survey_2024_p19](../../data/pages/US_Professional_Services_Partner_Compensation_Survey_2024_p19.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `US_Professional_Services_Partner_Compensation_Survey_2024_p19` | US_Professional_Services_Partner_Compensation_Survey_2024 | untagged | 5 | `parsebench/data/pages/US_Professional_Services_Partner_Compensation_Survey_2024_p19.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一张横向分组条形图：9 个长类别标签（如 "Rise of green resources and sustainable technology"）沿左侧排列，每槽 4 条彩色条（Strategy consulting / Management/advisory consulting / Technology/IT consulting / Other），共 36 个标记。没有任何数值轴、刻度或网格，只有全部印出的数字标签；标签会按条长在条内（81、72）或条外（0、2、7）切换位置。标题分两层：粗体主标题 "Key external factors influencing outlook (%)"，其下第二行粗体副标题含 "(Select all that apply)"，图例横排在副标题与绘图区之间，最下方是 Source 行。左侧还有一整栏正文与图并列。
> 
> ## 定位一个值难在哪
> 值 81 在 "Interest rates and their impact on the economy" 这一槽出现两次：Strategy consulting 与 Management/advisory consulting 都是 81。要唯一定位必须同时给出类别名 + 图例名，缺一就落到两个单元格。而百分号只在主标题里，行内不复现。
> 
> ## 不确定的
> 条长为 0 的项（Rise of industrial automation 的 Other）只有数字没有条，无法确认是真 0 还是缺失；也无法确认是否有隐藏的 0–100 基线。

**gpt-5.6-sol**

> ### 画出来要什么
> 需要绘制单面板横向分组条形图：9个因素、4类咨询公司、共36个数据槽；图例置于图上方，百分比单位写在标题中。数值全部直接标注，长条内标、短条外标，并保留左侧并排的正文栏及图下来源行。
> 
> ### 定位一个值难在哪
> 首行“Interest rates and their impact on the economy”有两个81；必须再用图例区分“Strategy consulting”和“Management/advisory consulting”，单靠类别和值无法唯一定位。
> 
> ### 不确定的
> 图中没有数值刻度或轴线，左侧类别文字按隐式类别轴处理。三个零值只有“0”而无可见条形；marks按9×4个数据槽计为36。

**gemini-3.1-pro**

> ### 画出来要什么
> 需要能够绘制带有顶部图例的水平分组条形图。图表无X坐标轴和垂直网格线，完全依赖于条形末端或内部的数值标签来传递信息。系统需支持根据条形长度动态调整数值标签的位置（如“81”在条形内部，“4”在条形外部），且当数值为0时，即使不绘制条形，也能在基线处保留“0”标签。此外，页面级别的重建需要支持多列混排布局，即左侧是一整列正文排版，右侧才是图表及其标题。
> 
> ### 定位一个值难在哪
> 以 `81` 为例。该图表完全没有提供数值坐标轴，所有数字均通过文本标签直接附着在条形上。定位这个值不仅需要读取较长的类别标签（如“Interest rates and their impact on the economy”），还需要准确地将位于图表上方较小的图例色块映射到具体的条形组中（如深蓝色对应“Strategy consulting”），这要求多模态大模型在缺乏网格线和坐标轴对齐辅助的情况下，做到精准的颜色与位置映射。
> 
> ### 不确定的
> 无法确认数值为“0”的项（如“Commercial real estate market”中的Technology/IT consulting系列）是否渲染了极细微的不可见占位符，视觉上只能看到独立的数字“0”。此外，部分图表区域底部的灰色文字与背景色的确切对比度无法判定。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | grouped_bar | 36 | — | above | all |
| opus-5 | f2 | unreadable | 0 | — | none | none |
| gpt-5.6-sol | f1 | grouped_bar | 36 | — | above | all |
| gemini-3.1-pro | f1 | grouped_bar | 36 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: four coloured bars stacked side by side within each category row, e.g. 65/51/60/40；gpt-5.6-sol: Each category row contains four adjacent horizontal bars keyed by the four-item legend.；gemini-3.1-pro: four bars are grouped side by side for each y-axis category |
| `hgrid_only` | ✓ | ✓ | — | opus-5: thin horizontal rules separate each category band across the plot width；gpt-5.6-sol: Horizontal rules separate category rows; no vertical grid lines are drawn. |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: category names sit at left and bars grow rightwards from a common left baseline；gpt-5.6-sol: All bars extend horizontally to the right from a common origin.；gemini-3.1-pro: categories sit on the left y-axis and bars grow to the right |
| `legend_above_plot` | ✓ | ✓ | ✓ | opus-5: legend row "Strategy consulting ... Other" between the subtitle and the first bar group；gpt-5.6-sol: The four-item legend sits between the subtitle and the first category row.；gemini-3.1-pro: the legend sits under the subtitle and above the horizontal bars |
| `missing_value_marker` | ✓ | — | — | opus-5: "0" printed with no bar drawn for Other on "Rise of industrial automation" |
| `no_value_axis` | ✓ | ✓ | ✓ | opus-5: no ticks or numbers under the bars; only printed labels give values；gpt-5.6-sol: No numeric value-axis ticks are drawn; every bar carries a printed number.；gemini-3.1-pro: no x-axis or ticks are drawn, only printed numbers are used |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: left column prose "When compared to respondents at other types of firms..." runs beside the chart；gpt-5.6-sol: “When compared to respondents at other types of firms” begins a prose column beside the chart.；gemini-3.1-pro: a column of body text starting 'When compared to...' runs alongside the figure |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: "Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=142"；gpt-5.6-sol: “Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=142” appears below.；gemini-3.1-pro: small print starting 'Source: Heidrick & Struggles...' is located below the plot |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: title reads "Key external factors influencing outlook (%)"; no unit near the bars；gpt-5.6-sol: The title reads “Key external factors influencing outlook (%)”.；gemini-3.1-pro: the unit (%) is written directly in the main title |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: "81", "72", "65" printed white inside the right end of the long bars；gpt-5.6-sol: “81” is printed inside the right end of the top dark bar.；gemini-3.1-pro: numbers like 81, 72, 65 are printed inside the bar segments |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: "0" and "2" sit to the right of the very short or absent bars；gpt-5.6-sol: “2” for “Commercial real estate market” sits beyond the short dark bar.；gemini-3.1-pro: numbers like 80, 40, 0 are printed just outside the marks |
| `wrapped_category_labels` | ✓ | — | — | opus-5: "Rise of green resources and sustainable technology" runs long across the left label column |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `zero_length_bar_with_label` | opus-5 | 2,3 | Other rows show "0" as a bare numeral with no rectangle at the baseline |
| `two_line_bold_title_stack` | opus-5 | 4 | a large bold title line plus a smaller bold two-line restatement with "(Select all that apply)" |
| `zero_value_label_without_bar` | gpt-5.6-sol | 2,3 | Three “0” labels appear at the bar origin with no visible bar length. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 81 | Interest rates and their impact on the economy、Strategy consulting | Interest rates and their impact on the economy、Strategy consulting | Interest rates and their impact on the economy、Strategy consulting | Interest rates and their impact on the economy、Strategy consulting | ✓ | ✓ | ✓ | 过 |
| 60 | Rise of AI、Technology/IT consulting | US presidential elections/geopolitical uncertainty、Technology/IT consulting | US presidential elections/geopolitical uncertainty、Technology/IT consulting | US presidential elections/geopolitical uncertainty、Technology/IT consulting | ✗ | ✗ | ✗ | 过 |
| 19 | Effects of hybrid work models on our organization、Management/advisory consulting | Effects of hybrid work models on our organization、Management/advisory consulting | Effects of hybrid work models on our organization、Management/advisory consulting | Effects of hybrid work models on our organization、Management/advisory consulting | ✓ | ✓ | ✓ | 过 |
| 5 | Increasing threat of cyberattacks、Strategy consulting | Increasing threat of cyberattacks、Strategy consulting | Increasing threat of cyberattacks、Strategy consulting | Increasing threat of cyberattacks、Strategy consulting | ✓ | ✓ | ✓ | 过 |
| 12 | Rise of green resources and sustainable technology、Strategy consulting | Increasing threat of cyberattacks、Management/advisory consulting | Increasing threat of cyberattacks、Management/advisory consulting | Rise of green resources and sustainable technology、Strategy consulting | ✗ | ✗ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
