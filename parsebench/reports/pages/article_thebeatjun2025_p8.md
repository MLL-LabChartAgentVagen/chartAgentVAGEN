# article_thebeatjun2025_p8

![article_thebeatjun2025_p8](../../data/pages/article_thebeatjun2025_p8.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `article_thebeatjun2025_p8` | article_thebeatjun2025 | need_estimate | 10 | `parsebench/data/pages/article_thebeatjun2025_p8.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 单面板双线折线图,时间轴从 `Dec 2022` 到 `Mar 2025`(季度刻度、月度数据点,刻度稀疏)。y 轴 `0%`–`8%`,间隔 1%,无网格线。两条线用深蓝/浅蓝区分,图例在图下方一行。图内还要画两个粗箭头标注加彩色粗体说明文字(`Since 2022, public sector employment has grown substantially...`、`... crowding out the private sector`),箭头颜色与对应线条颜色一致。标题分三层:粗体图标题 + 斜体副标题 `Cumulative growth in total payrolls since 12/31/2022`,上方还有页面级 `TOP THEMES` 眉标与蓝色导语段。
> 
> ## 定位一个值难在哪
> 以 `6.2%` 为例:它必须在 `Public Sector Total Payrolls (Gov't, Education, Health Svcs)` 这条线上,沿时间轴插值找到某月(约 2024 年年中)。图上无任何数字标签,刻度 1% 一格,5% 容差约 0.31 个百分点,而两条曲线在该段近似直线,读数依赖像素;更麻烦的是刻度只到季度,月点要在 `Jun 2024` 与 `Sep 2024` 之间估算。
> 
> ## 不确定的
> 数据点是月频还是周频无法确定(约 29 个点为推测);`0.85%`、`0.3%` 等私营部门小值落在 1% 格内,具体月份无法确认;箭头是注释而非数据,已按 annotation 处理。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 单面板双折线图：29个月度位置、左侧0%—8%刻度、稀疏季度日期、下方双系列图例。图内还需绘制两组粗箭头和说明文字，并在图下排长篇来源及免责声明。
> 
> **定位一个值难在哪**
> 
> 例如0.3%的私人部门点没有数值标签；纵轴间隔为1%，但5%容差仅0.015个百分点。还必须同时用日期和完整系列名定位。
> 
> **不确定的**
> 
> 未标出的月份只能按月度折点和“As of April 30, 2025”推定；0.8%、6.2%、6.8%等点的确切月份及29个折点总数均含视觉估计。

**gemini-3.1-pro**

> **画出来要什么**
> 能够绘制带有两条数据线的单面板折线图，底部需支持稀疏的时间轴刻度（如按季度标记）。需要支持在绘图区域内添加自由浮动的文本注释（annotation callout）和带箭头的指示线。图例需放置在图表下方。
> 
> **定位一个值难在哪**
> 以0.85%为例，该数值未在图表中直接印出。Y轴的刻度间距高达1%，并且整个绘图区域没有任何水平或垂直网格线辅助对齐。由于线段本身存在一定的粗细，读者无法通过肉眼将该数值读取至5%的精度要求内。
> 
> **不确定的**
> 折线具体是按月还是按其他频率绘制的不确定，因为线上没有明显的数据点标记，只能根据非线性的弯折推测其频率高于季度。这也使得将给定的评分数值准确对应到某个确切的月份存在一定的猜测成分。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 58 | — | above | none |
| gpt-5.6-sol | f1 | line | 58 | — | above | none |
| gemini-3.1-pro | f1 | line | 54 | — | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | ✓ | ✓ | opus-5: Two thick arrows with bold text 'Since 2022, public sector employment has grown substantially...' drawn over plot；gpt-5.6-sol: Two thick arrows and explanatory text are drawn over the two lines.；gemini-3.1-pro: text blocks with arrows pointing to the lines |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: Legend row under the x axis: 'Private Sector Total Payrolls (ex Govt, Education, Health Svcs)'；gpt-5.6-sol: The two series swatches and names form a row below the x axis.；gemini-3.1-pro: the legend sits below the x-axis tick labels |
| `nonstandard_time_ticks` | ✓ | — | — | opus-5: Ticks read 'Mar 2023', 'Jun 2023', 'Sep 2023' rather than ISO dates |
| `side_text_bullets` | ✓ | — | — | opus-5: Blue intro paragraph 'Over recent years, the majority of payroll job gains...' above the figure |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Source: Bloomberg, MSIM. As of April 30, 2025. For illustrative purposes only.' below the plot；gpt-5.6-sol: “Source: Bloomberg, MSIM. As of April 30, 2025.” appears below the legend.；gemini-3.1-pro: Source and note paragraph at the bottom of the page |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: Ticks every quarter ('Dec 2022','Mar 2023',...) while the lines bend at monthly intervals；gpt-5.6-sol: Monthly line vertices run from Dec 2022 to Apr 2025, but only quarterly dates are labelled.；gemini-3.1-pro: ticks are quarterly but the lines bend between them, indicating more points |
| `unit_in_axis_or_title` | ✓ | — | — | opus-5: Subtitle 'Cumulative growth in total payrolls since 12/31/2022' fixes the % scale |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `arrow_trend_annotation` | opus-5 | 3 | Two thick tapered arrows drawn parallel to each line, coloured to match the series they describe |
| `deck_kicker_label` | opus-5 | 4 | 'TOP THEMES' set in small blue caps above the page headline |
| `bold_title_plus_italic_subtitle` | opus-5 | 4 | Bold chart title line followed by italic 'Cumulative growth in total payrolls since 12/31/2022' |
| `page_narrative_heading_and_deck` | gpt-5.6-sol | 4 | “TOP THEMES” and “Over the Past Three Years...” sit above a blue explanatory paragraph. |
| `no_gridlines` | gemini-3.1-pro | 2 | the plot area has neither horizontal nor vertical gridlines |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 0.3% | Mar 2023、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | Private Sector Total Payrolls (ex Govt, Education, Health Svcs)、Mar 2023 | Mar 2023、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | Mar 2023、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | ✓ | ✓ | ✓ | 过 |
| 1.5% | Mar 2023、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | Private Sector Total Payrolls (ex Govt, Education, Health Svcs)、Mar 2025 | May 2023、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | Mar 2023、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | ✗ | ✗ | ✓ | 没过 |
| 0.6% | Sep 2023、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | Private Sector Total Payrolls (ex Govt, Education, Health Svcs)、Jun 2023 | Dec 2023、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | Sep 2023、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | ✗ | ✗ | ✓ | 过 |
| 3% | Sep 2023、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | Public Sector Total Payrolls (Gov't, Education, Health Svcs)、Sep 2023 | Sep 2023、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | Sep 2023、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | ✓ | ✓ | ✓ | 过 |
| 0.8% | Mar 2024、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | Private Sector Total Payrolls (ex Govt, Education, Health Svcs)、Jun 2024 | Apr 2024、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | Mar 2024、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | ✗ | ✗ | ✓ | 过 |
| 6.2% | Mar 2024、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | Public Sector Total Payrolls (Gov't, Education, Health Svcs)、Jun 2024 | Aug 2024、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | Jun 2024、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | ✗ | ✗ | ✗ | 没过 |
| 0.85% | Sep 2024、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | Private Sector Total Payrolls (ex Govt, Education, Health Svcs)、Sep 2024 | Jun 2024、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | Sep 2024、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | ✓ | ✗ | ✓ | 过 |
| 6.8% | Sep 2024、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | Public Sector Total Payrolls (Gov't, Education, Health Svcs)、Dec 2024 | Nov 2024、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | Sep 2024、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | ✗ | ✗ | ✓ | 过 |
| 1.5% | Mar 2025、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | Private Sector Total Payrolls (ex Govt, Education, Health Svcs)、Mar 2025 | Apr 2025、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | Mar 2025、Private Sector Total Payrolls (ex Govt, Education, Health Svcs) | ✓ | ✗ | ✓ | 过 |
| 7.8% | Mar 2025、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | Public Sector Total Payrolls (Gov't, Education, Health Svcs)、Mar 2025 | Apr 2025、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | Mar 2025、Public Sector Total Payrolls (Gov't, Education, Health Svcs) | ✓ | ✗ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
