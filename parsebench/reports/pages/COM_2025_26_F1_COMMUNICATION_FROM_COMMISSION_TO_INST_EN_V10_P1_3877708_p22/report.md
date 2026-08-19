# COM_2025_26_F1_COMMUNICATION_FROM_COMMISSION_TO_INST_EN_V10_P1_3877708_p22

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| COM_2025_26_F1_COMMUNICATION_FROM_COMMISSION_TO_INST_EN_V10_P1_3877708 | `need_estimate` | 10 | 10 |

本页为报告第20页「3.3 Energy」小节，含一个无编号的KPI彩色表格（KPI 17–19）、两段正文，以及Figure 8的五序列电价折线图和其Source行、脚注区。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 0.34 | `UK` · `2024` | 20% | f1 | the UK 2024 point, the highest point on the green line | 否 | `UK` · `2024` |
| 2 | 0.19 | `EU IC band` · `2024` | 20% | f1 | the EU IC band 2024 point (light blue line endpoint) | 否 | `EU IC band` · `2024` |
| 3 | 0.16 | `EU ID band` · `2024` | 20% | f1 | the EU ID band 2024 point (dark blue endpoint); the same figure also appears as text "EUR 0.16 per kWh (2024)" in the KPI table | 否 | `EU ID band` · `2024` |
| 4 | 0.13 | `Japan` · `2024` | 50% | f1 | the Japan 2024 point (light green endpoint, falling from 2023) | 否 | `Japan` · `2024` |
| 5 | 0.08 | `USA` · `2024` | 50% | f1 | the USA 2024 point, the highest point of the flat yellow line | 否 | `USA` · `2024` |
| 6 | 0.31 | `UK` · `2023` | 50% | f1 | the UK 2023 point on the steeply rising green line | 否 | `UK` · `2023` |
| 7 | 0.20 | `EU ID band` · `2023` | 50% | f1 | the EU ID band 2023 point (dark blue local peak); also printed as "EUR 0.20 per kWh (2023)" in the KPI table | 否 | `EU ID band` · `2023` |
| 8 | 0.18 | `EU IC band` · `2022` | 50% | f1 | the EU ID band 2022 point; the Japan 2023 point sits at the same height, so the height alone is ambiguous | 否 | `EU ID band` · `2022` |
| 9 | 0.15 | `UK` · `2015` | 50% | f1 | the Japan 2015 point, the start of the light green line | 否 | `Japan` · `2015` |
| 10 | 0.06 | `USA` · `2015` | 50% | f1 | the USA 2015 point at the start of the flat yellow line | 否 | `USA` · `2015` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 0.18, 0.15

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 5 | 10 | 50 | 无 | 0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4 |

- **f1** Figure 8 / Electricity prices for companies in the EU and other advanced economies.　[图上方]　单位 `EUR/kWh`
  - 来源行：Source: Eurostat, US Energy Information Administration (EIA), the UK Department for Energy Security and Net Zero (DESNZ) and the International Energy Agency (IEA)113.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: Eurostat, US Energy Information Administration (EIA), the UK Department..." under the plot |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | legend row "EU IC band  EU ID band  UK  USA  Japan" sits inside the plot, level with the 0.4 tick |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | y ticks are bare numbers 0.05 ... 0.4; only "EUR/kWh" fixes their scale |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | superscript 113 after "the International Energy Agency (IEA)" in the source line |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | table cell "Electricity as a share of the total energy consumption.107" carries superscript 107 |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "EUR/kWh" printed top-left inside the plot, level with the top tick 0.4, not beside the axis |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | year labels 2015 ... 2024 are set at roughly 45 degrees under the axis |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each 0.05 tick across the panel, no vertical rules drawn |

词表 65 项，本页出现 7 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `table_row_fill_encodes_status` | page | KPI 17 and KPI 18 rows filled yellow, KPI 19 row filled green, in the same bordered table | 行底色本身携带「是否有目标/是否达标」的额外信息，若解析成纯文本表格则该维度丢失，读者无法区分KPI 19与其他行的状态差异。 |
| `unnumbered_kpi_table` | page | bordered table with header row "KPI \| What it measures \| Target \| Latest EU value", no figure number or caption | 表中直接印有 "EUR 0.16 per kWh (2024)"、"EUR 0.20 per kWh (2023)" 等与Figure 8同源的数值，但无编号标题，取值时需靠列头而非图号来定位。 |
| `value_year_inside_cell` | page | cells read "21.3% (2022)" and "20.8% (2021)" — two year-tagged values stacked in one cell | 一个单元格内含两个带年份的取值，定位某一年数值需要同时用KPI名与括号内年份，普通行列键不足以唯一寻址。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

卡在读数。图上0到0.4共约348像素，每0.05刻度约43像素，5%容差对0.06只有0.003即约2.6像素、对0.16也只有0.008即约7像素，而线宽本身约3–4像素，所以USA、Japan这类低位序列基本无法读到容差内。更糟的是2015–2021段EU IC band、EU ID band与UK三条线挤在0.10–0.15之间且相互交叉，序列归属先于数值就已模糊；全图50个点无任何印刷数字，只有EU ID band的0.16与0.20在上方KPI表中以文字形式出现。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 一类出版方 | axis_title_above_axis 与独立的 unit 字段（"EUR/kWh" 悬浮于图内左上、与顶刻度齐平） | 图表样式条件行中的标题/单位位置字段，以及记录的 heading 结构（number/title/subtitle/unit/placement 分开存放） | 新增一行「单位不在标题也不在轴标签、而是图内浮动文字」，对比解析器能否把 EUR/kWh 绑定到裸小数刻度上 |
| P1 | 通用 | P1 式的按标记可达精度（小量级序列如 USA 0.06、Japan 0.13 的容差只有2–6像素） | readable 判定字段，由布尔门改为随刻度间距与线宽计算的每点精度 | 新增一行「值轴量程0–0.4、刻度步长0.05时，低位密集序列的可达精度」，区分能否读与读到几位 |
| P6 | 通用 | tick_format 维度：小数刻度 0, 0.05, 0.1 … 0.4 与旋转45°的年份刻度组合 | 样式字段中的刻度格式与x轴刻度旋转角 | 新增一行「小数值轴 + 旋转年份刻度」，检验解析输出中年份键与数值精度是否同时保住 |
| P3 | 这份文档自己的习惯 | new_components 里的 table_row_fill_encodes_status / unnumbered_kpi_table（黄绿底色行的无编号KPI表） | 整页markdown导出条件行：无图号表格的标题来源与行底色属性的落表方式 | 新增一行「同页存在无编号彩色表格且其文字值与折线图同源」，检验数值被归到表还是图 |
