# COM_2025_26_F1_COMMUNICATION_FROM_COMMISSION_TO_INST_EN_V10_P1_3877708_p19

![COM_2025_26_F1_COMMUNICATION_FROM_COMMISSION_TO_INST_EN_V10_P1_3877708_p19](../../data/pages/COM_2025_26_F1_COMMUNICATION_FROM_COMMISSION_TO_INST_EN_V10_P1_3877708_p19.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `COM_2025_26_F1_COMMUNICATION_FROM_COMMISSION_TO_INST_EN_V10_P1_3877708_p19` | COM_2025_26_F1_COMMUNICATION_FROM_COMMISSION_TO_INST_EN_V10_P1_3877708 | need_estimate | 10 | `parsebench/data/pages/COM_2025_26_F1_COMMUNICATION_FROM_COMMISSION_TO_INST_EN_V10_P1_3877708_p19.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一张窄栏折线图，嵌在正文左栏，右侧是与之并排的正文段落（`Significant amounts of EU savers' money are either tied up in bank accounts or invested abroad.`）。图内需要：三条年度折线（蓝、绿、黄，2011–2023 共约 13 个点），但图例只画出两项 `EU`、`US`，绿线（按正文应为 UK）没有名字；图例置于绘图区内部约 y=20 处；左轴 `0`–`100`、每 10 一格、无网格线，单位 `%` 单独写在顶格 `100` 右侧；x 轴刻度斜排且只标奇数年 `2011 … 2023`；下方两段小字 `Note:` 与 `Source: European Commission, DG FISMA`；标题 `Figure 4:` 与标题句在图上方。
> 
> ## 定位一个值难在哪
> 以 EU 的 43 为例：图上没有任何数值标签，只能对着 10 单位一格的刻度读线；而 EU 线在 45→43 之间几乎水平，43 与 45 相差仅 4.4%，小于 5% 容差，等于说相邻年份互相可以冒充。再者 2022 这类偶数年根本没有刻度标签，行标签只能靠推。
> 
> ## 不确定的
> 绿线的名称（正文提到 UK 55%，图上无字）；十个给定值对应的具体年份是我按“末点=43/72”倒推的；是否存在极淡的横向网格线看不清。

**gpt-5.6-sol**

> ### 画出来要什么
> 单图折线图：蓝、绿、黄三条年度线，纵轴为0—100%，横轴为2011—2023；年度节点多于隔年显示的倾斜刻度。图例置于图内，标题、注释和来源位于图表上下，正文在右侧并延续至图下。
> 
> ### 定位一个值难在哪
> 例如“EU—2023”的43未直接印出，只能按纵轴读取。纵轴每10个百分点一格，且没有网格线或点标记；43的5%容差仅约±2.15。
> 
> ### 不确定的
> 绿色线没有图例名称；只能从正文推测可能代表UK，未据此命名。年度节点数按折线转折估为13，部分精确值无法从页面确认。

**gemini-3.1-pro**

> - **画出来要什么**
> 要重新绘制此页面，生成器需要能生成包含至少三条折线的折线图，并且允许其中一条线没有对应的图例。必须支持将图例放置在绘图区内部。X轴需要支持绘制稀疏且倾斜的年份刻度（仅显示奇数年份）。Y轴不仅不能有水平网格线，还需要支持将单位直接拼接到最高刻度文本内（如“100 %”）。图表下方需要支持追加Note和Source说明文本，并且整个图表块需要能与右侧的段落正文并排呈现。
> 
> - **定位一个值难在哪**
> 以US在2012年的值（71）为例，图中X轴仅打印了2011和2013的刻度，完全没有出现“2012”的标签。这意味着如果要用“2012”去定位这个单元格，就用到了页面上不存在的词，直接破坏了所见即所得的提取规则。
> 
> - **不确定的**
> 图中大约在55%的位置有一条明显的绿色折线，但图例只列出了EU和US，这导致从图表本身看，该系列的身份是不确定的（只能通过阅读右侧正文猜测它是UK）。此外，由于没有任何网格线作为参考，读取43、71这样的精确数据点时带有很大的猜测成分。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 39 | Figure 4: | above | none |
| gpt-5.6-sol | f1 | line | 39 | Figure 4: | above | none |
| gemini-3.1-pro | f1 | line | 39 | Figure 4: | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `axis_title_above_axis` | ✓ | ✓ | — | opus-5: `100 %` -- the percent sign sits beside the top tick, above the axis；gpt-5.6-sol: The “%” symbol is printed above and right of the top value-axis tick. |
| `footnote_marker` | ✓ | — | — | opus-5: superscript `94`, `95`, `96` attached to sentences naming Figure 4 and KPI 15 |
| `legend_inside_plot` | ✓ | ✓ | ✓ | opus-5: `EU` and `US` swatches drawn over the plot area at about the 20 level；gpt-5.6-sol: The “EU” and “US” legend sits above the baseline inside the plotting area.；gemini-3.1-pro: the EU and US legend sits within the plot area |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: `2011`, `2013` ... `2023` set at roughly 45 degrees under the plot；gpt-5.6-sol: Time labels from “2011” to “2023” are angled diagonally.；gemini-3.1-pro: the year labels on the x-axis are rotated at an angle |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: Body paragraph `Significant amounts of EU savers' money...` runs in a column level with the figure；gpt-5.6-sol: Running prose beginning “Significant amounts of EU savers’ money” occupies the column beside the figure.；gemini-3.1-pro: a column of body text runs alongside the right edge of the figure |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: `Note: Volumes of household savings in company bonds...` and `Source: European Commission, DG FISMA` below plot；gpt-5.6-sol: “Note:” and “Source: European Commission, DG FISMA” appear below the plot.；gemini-3.1-pro: Note: and Source: lines sit directly beneath the figure |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: lines bend yearly but ticks are only odd years 2011, 2013 ... 2023；gpt-5.6-sol: Lines have annual bends, but the axis labels only 2011, 2013, …, 2023.；gemini-3.1-pro: ticks are drawn every 2 years but the line data is clearly yearly |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: `%` is the only unit text, printed next to the top tick `100`；gpt-5.6-sol: A bare “%” supplies the unit while value ticks read 0 through 100. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `series_missing_from_legend` | opus-5 | 3 | a green line runs 65 down to ~57 but the legend lists only `EU` and `US` |
| `figure_in_narrow_text_column` | opus-5 | 1,4 | figure, Note and Source occupy the left half-column; body text fills the right half |
| `unlabelled_series` | gpt-5.6-sol | 3 | Three coloured lines are drawn, but the legend names only “EU” and “US”. |
| `unlabeled_series_line` | gemini-3.1-pro | 3 | a green line is plotted but is entirely missing from the legend |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 45 | EU、2011 | EU、2019 | EU、2011 | EU、2011 | ✗ | ✓ | ✓ | 过 |
| 70 | US、2011 | US、2019 | US、2011 | US、2011 | ✗ | ✓ | ✓ | 过 |
| 45 | EU、2013 | EU、2020 | EU、2013 | EU、2012 | ✗ | ✓ | ✗ | 过 |
| 71 | US、2013 | US、2020 | US、2013 | US、2012 | ✗ | ✓ | ✗ | 过 |
| 45 | EU、2017 | EU、2021 | EU、2019 | EU、2013 | ✗ | ✗ | ✗ | 过 |
| 72 | US、2017 | US、2021 | US、2019 | US、2013 | ✗ | ✗ | ✗ | 过 |
| 44 | EU、2021 | EU、2022 | EU、2021 | EU、2014 | ✗ | ✓ | ✗ | 过 |
| 70 | US、2021 | US、2022 | US、2021 | US、2014 | ✗ | ✓ | ✗ | 过 |
| 43 | EU、2023 | EU、2023 | EU、2023 | EU、2015 | ✓ | ✓ | ✗ | 过 |
| 72 | US、2023 | US、2023 | US、2023 | US、2015 | ✓ | ✓ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 2 | 2 | 3 | 未裁决 · 无实测证据 | 这一页 10 个抽查点全过，运行没有在任何一步卡住，三家的 2 / 2 / 3 都无法证伪。 |
