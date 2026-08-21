# employment_and_social_developments_in_europe_esde_2024_report_p100

![employment_and_social_developments_in_europe_esde_2024_report_p100](../../data/pages/employment_and_social_developments_in_europe_esde_2024_report_p100.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `employment_and_social_developments_in_europe_esde_2024_report_p100` | employment_and_social_developments_in_europe_esde_2024_report | need_estimate | 10 | `parsebench/data/pages/employment_and_social_developments_in_europe_esde_2024_report_p100.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一张双线折线图：标题分四层（`Chart A3.1` 编号行、蓝色粗体标题、灰色副标题“Absolute change in employment following ESF+ investment in skills”），左侧竖排斜体轴标题“Absolute change in employment”，y 轴 -20000 到 40000（含负值与零线），x 轴 2021–2039 隔年刻度（数据为逐年，刻度稀疏），仅横向虚线网格，图例在图下方两项。图下有 `Source:` 行与蓝色下载链接行。页面下半部为独立的 Box A3.3 文字框（带浅色底与公式），非图表。
> 
> ## 定位一个值难在哪
> 以 35500 为例：它是 Net receivers 线 2027 年附近的峰值，图上无任何数值标签，y 轴刻度间隔 10000，5% 容差约 ±1775，需在 30000 与 40000 两格间目测约 0.55 格；且 x 轴只标奇数年，峰值究竟属 2027 还是 2028 无法确定，行标签“2027”未必是真实键。
> 
> ## 不确定的
> 各年份是否逐年取值、峰值年份归属、-13000 与 -2000 的确切年份；下载链接指向的数据是否含数值表；线上点是否真有标记点（渲染中不可见）。

**gpt-5.6-sol**

> ### 画出来要什么
> 绘制两条含20个年度点的实线、跨越零线的负值、仅水平虚线网格、左侧旋转轴题、隔年年份标签、图下图例及来源和下载链接；另需还原编号文字框。
> 
> ### 定位一个值难在哪
> “Net contributors—2021”的3800未印在图上；纵轴刻度间隔10000，而5%容差仅190，靠线段位置无法可靠读准。
> 
> ### 不确定的
> 年度点没有标记；2038和2040未标年份，只能按相邻刻度推定。Box A3.3是说明文字框而非数据图。

**gemini-3.1-pro**

> ### 画出来要什么
> 
> 要生成此页，生成器需要绘制一个带有图表编号、主标题和副标题的折线图。图表包含两条折线，并带有下方图例。X轴为时间轴，需要支持稀疏刻度显示（数据点为每年一个，但标签每两年显示一次，如2021, 2023）。Y轴需要支持跨越零线的负数范围（-20000到40000，步长10000），并且左侧带有一个旋转了90度的垂直轴标题。图表区域内仅包含水平的点状网格线。图表最下方还需绘制来源说明文本。
> 
> ### 定位一个值难在哪
> 
> 以“Net contributors”在2021年的值3800为例。首先，折线图上没有任何直接标注的数值，完全依赖视线对齐Y轴来读取。其次，Y轴的刻度间隔高达10000，要在这样的宽泛尺度上肉眼准确分辨出3800，且误差保持在5%（即±190）以内是不可能的，这导致绝大多数数值由于无法满足精度要求而在解析的第2步被拦截。此外，某些年份（如2030年）的X轴标签并未直接打印在图表上，需要通过上下文插值推断，这也使得表头对齐变得困难。
> 
> ### 不确定的
> 
> 折线上并没有绘制明确的数据点标记（如圆点），因此数据点的确切密度（是严格按年还是有更细的粒度）只能依靠X轴上每年一个的刻度线推断为年度数据。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 40 | Chart A3.1 | above | none |
| opus-5 | f2 | unreadable | 0 | Box A3.3 | above | none |
| gpt-5.6-sol | f1 | line | 40 | Chart A3.1 | above | none |
| gpt-5.6-sol | f2 | unreadable | 0 | Box A3.3 | inside | none |
| gemini-3.1-pro | f1 | line | 38 | Chart A3.1 | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `data_link_below_figure` | ✓ | ✓ | — | opus-5: 'Click here to download chart.' in blue under the source line；gpt-5.6-sol: “Click here to download chart.” appears below the source line. |
| `footnote_marker` | ✓ | — | — | opus-5: superscript (1) after 'tax-benefit systems of the EU-27.' and (2) at end of box text |
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: dotted horizontal rules at 40000, 30000 ... -20000; no vertical grid lines；gpt-5.6-sol: Dotted horizontal grid lines cross the plot; no vertical grid lines are drawn.；gemini-3.1-pro: only horizontal dotted grid lines are drawn in the plot |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'Net contributors' and 'Net receivers' with line swatches sit under the x axis；gpt-5.6-sol: “Net contributors” and “Net receivers” form a legend row beneath the x axis.；gemini-3.1-pro: the legend is placed centrally below the x-axis |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: y axis ticks -10000 and -20000; green line dips to about -13000 below the zero line；gpt-5.6-sol: Both lines descend below 0; the green line reaches approximately -14000.；gemini-3.1-pro: the y-axis extends down to -20000 below the zero line |
| `reference_line` | ✓ | ✓ | — | opus-5: a solid horizontal rule drawn across the plot at the 0 tick；gpt-5.6-sol: A solid horizontal rule crosses the plot at the 0 tick. |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Absolute change in employment' set vertically along the left axis；gpt-5.6-sol: “Absolute change in employment” is rotated vertically beside the left axis.；gemini-3.1-pro: the y-axis title is rotated vertically along the left edge |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Source: JRC calculations based on RHOMOLO model.' below the plot；gpt-5.6-sol: “Source: JRC calculations based on RHOMOLO model.” appears below the chart.；gemini-3.1-pro: a Source line is printed below the plot and legend |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: ticks 2021, 2023, 2025 ... 2039 while the lines bend at intermediate years；gpt-5.6-sol: Annual points span 2021–2040, but labels show 2021, 2023, …, 2039.；gemini-3.1-pro: x-axis ticks are yearly but labels are printed every two years |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: subtitle 'Absolute change in employment following ESF+ investment in skills'; axis ticks are bare numbers；gpt-5.6-sol: The subtitle says “Absolute change in employment following ESF+ investment in skills”. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `box_text_panel_with_equation` | opus-5 | 1,4 | tinted bordered box 'Box A3.3: Calculating Income Stabilisation Coefficients' containing a displayed ISC formula |
| `section_heading_above_figure` | opus-5 | 4 | 'Simulation results' heading above Chart A3.1, separate from the chart title block |
| `multi_line_heading_block_with_number_row` | opus-5 | 3,4 | three stacked lines: 'Chart A3.1', bold blue title, grey subtitle, each in different type |
| `numbered_text_box` | gpt-5.6-sol | 1,4 | “Box A3.3: Calculating Income Stabilisation Coefficients” heads a bordered explanatory text panel. |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 3800 | Net contributors、2021 | Net contributors、2021 | Net contributors、2021 | Net contributors、2021 | ✓ | ✓ | ✓ | 过 |
| 15000 | Net receivers、2021 | Net receivers、2021 | Net receivers、2021 | Net receivers、2021 | ✓ | ✓ | ✓ | 过 |
| 4300 | Net contributors、2023 | Net contributors、2023 | Net contributors、2023 | Net contributors、2023 | ✓ | ✓ | ✓ | 过 |
| 31000 | Net receivers、2023 | Net receivers、2023 | Net receivers、2023 | Net receivers、2023 | ✓ | ✓ | ✓ | 过 |
| 35500 | Net receivers、2027 | Net receivers、2027 | Net receivers、2025 | Net receivers、2025 | ✓ | ✗ | ✗ | 过 |
| -2000 | Net contributors、2029 | Net contributors、2029 | Net receivers、2029 | Net contributors、2029 | ✓ | ✗ | ✓ | 过 |
| -13000 | Net receivers、2031 | Net receivers、2031 | Net receivers、2031 | Net receivers、2030 | ✓ | ✓ | ✗ | 过 |
| 11000 | Net contributors、2037 | Net contributors、2037 | Net receivers、2038 | Net contributors、2037 | ✓ | ✗ | ✓ | 过 |
| 11000 | Net receivers、2037 | Net receivers、2037 | Net contributors、2039 | Net receivers、2037 | ✓ | ✗ | ✓ | 没过 |
| 13800 | Net receivers、2039 | Net receivers、2039 | Net receivers、2040 | Net receivers、2039 | ✓ | ✗ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
