# Technopak_Industry_Report_p12

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Technopak_Industry_Report | `untagged` | 8 | 0 |

报告第12页正文讨论城镇化、气候变化与可再生能源，中部含一幅柱状图 Exhibit 2.4: Solar Energy Capacity Forecast (FY)，展示2020至2027P年太阳能装机容量及30%增长箭头注释。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 34.6 | `2020` | 1% | f1 | the 2020 bar | 是 | `Exhibit 2.4: Solar Energy Capacity Forecast (FY)` · `2020` |
| 2 | 40.1 | `2021` | 1% | f1 | the 2021 bar | 是 | `Exhibit 2.4: Solar Energy Capacity Forecast (FY)` · `2021` |
| 3 | 54.0 | `2022` | 1% | f1 | the 2022 bar | 是 | `Exhibit 2.4: Solar Energy Capacity Forecast (FY)` · `2022` |
| 4 | 65.0 | `2023` | 1% | f1 | the 2023 bar | 是 | `Exhibit 2.4: Solar Energy Capacity Forecast (FY)` · `2023` |
| 5 | 90.8 | `2024` | 1% | f1 | the 2024 bar | 是 | `Exhibit 2.4: Solar Energy Capacity Forecast (FY)` · `2024` |
| 6 | 113.3 | `2025P` | 1% | f1 | the 2025P bar | 是 | `Exhibit 2.4: Solar Energy Capacity Forecast (FY)` · `2025P` |
| 7 | 145.0 | `2026P` | 1% | f1 | the 2026P bar | 是 | `Exhibit 2.4: Solar Energy Capacity Forecast (FY)` · `2026P` |
| 8 | 185.6 | `2027P` | 1% | f1 | the 2027P bar | 是 | `Exhibit 2.4: Solar Energy Capacity Forecast (FY)` · `2027P` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 1 | 1 | 8 | 8 | 全部 | （不画值轴） |

- **f1** Exhibit 2.4: / Solar Energy Capacity Forecast (FY)　[图上方]　（标题里没有单位）
  - 来源行：Source: Secondary Research

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | a diagonal arrow across the plot from 2023 to 2027P labelled "30%" |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only a baseline under the bars; no value ticks drawn on either side of the plot |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: Secondary Research" in italics below the plot |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | bold numbers 34.6, 40.1 ... 185.6 printed above the tops of the bars |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | category ticks read "2025P", "2026P", "2027P" with a P suffix for projected years |

词表 65 项，本页出现 5 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `cagr_growth_arrow` | f1 | arrow spanning 2023 to 2027P bars carries "30%", a growth rate not a plotted bar value | 读者可能把箭头上的30%误当成某一年的数据点；它是跨类别的增长率注释，不属于任何单一柱子。 |
| `projection_suffix_in_ticks` | f1 | "2025P", "2026P", "2027P" mark forecast years while 2020-2024 are actuals | 同一系列内实际值与预测值只靠刻度后缀P区分，取值时必须连同后缀一起作为行标签。 |

## 5 · 难在哪

卡在 **第一步 · 要有表**。

八个数值全部以粗体印在柱顶，单一系列只需一个年份键即可定位，读数与标签都不构成障碍；真正的风险是解析器把这张无值轴的图当作散落文本，不生成任何表格——柱顶数字与年份刻度在版面上相距上百像素，年份行与数值行容易被拆成两串互不关联的文字，同时箭头上的"30%"会作为第九个数字混入同一串，使"185.6"与"2027P"无法配对。另外图题以斜体"Exhibit 2.4:"形式置于图上方的横线之间，若未被识别为标题，行上下文也会丢失。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | no_value_axis 与 value_label_outside 的组合（仅靠柱顶标签读数、无刻度轴） | 图表样式条件行：value_axis 显示开关与 value-label placement 字段 | 新增一行：无值轴且值标签外置的柱图，其数值召回率与有刻度轴版本对比 |
| new | 一类出版方 | annotation_callout 中的增长率箭头（cagr_growth_arrow） | 绘制记录中新增跨类别注释对象（起止类别 + 文本），并在导出时标记为非数据数字 | 新增一行：图内含非数据数字注释时，误把注释值当作某类别取值的比例 |
| P7 | 通用 | 图题拆分为编号、标题、单位与位置字段（"Exhibit 2.4:" + "Solar Energy Capacity Forecast (FY)"，无单位文本） | 图题记录字段：figure_number / title / unit_text / placement | 新增一行：图题以自定义编号前缀（Exhibit）且缺失单位文本时，上下文键的匹配率 |
| P6 | 一类出版方 | nonstandard_time_ticks 中的预测年后缀（2025P/2026P/2027P） | 类别轴刻度格式字段：时间刻度模板增加预测后缀选项 | 新增一行：刻度带预测后缀时，行标签逐字匹配（含P）与去后缀匹配的差异 |
