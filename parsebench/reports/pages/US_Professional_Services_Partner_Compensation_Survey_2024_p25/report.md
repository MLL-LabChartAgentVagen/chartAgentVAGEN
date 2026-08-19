# US_Professional_Services_Partner_Compensation_Survey_2024_p25

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| US_Professional_Services_Partner_Compensation_Survey_2024 | `untagged` | 5 | 0 |

本页上半为一段关于按在职年限划分的现金薪酬的正文，下半是一幅无编号的横向分组条形图，分四个在职年限面板、七个薪酬区间、2024与2022两个系列，全部数值直接标注。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 30 | `$400,000 or less` · `Less than 3 years` · `2024` | 1% | f1 | the 2024 bar for $400,000 or less in the Less than 3 years panel | 是 | `Less than 3 years` · `$400,000 or less` · `2024` |
| 2 | 57 | `$1.01m–$2.00m` · `6–10 years` · `2024` | 1% | f1 | the 2024 bar for $1.01m–$2.00m in the 6–10 years panel, the longest bar on the page | 是 | `6–10 years` · `$1.01m–$2.00m` · `2024` |
| 3 | 22 | `$801,000–$1.00m` · `3–5 years` · `2022` | 1% | f1 | the 2022 bar for $400,000 or less in the Less than 3 years panel; the same number also appears at Less than 3 years/$1.01m–$2.00m/2024, 3–5 years/$801,000–$1.00m/2022 and More than 10 years/$2.01m–$3.00m/2022 | 是 | `Less than 3 years` · `$400,000 or less` · `2022` |
| 4 | 5 | `More than $3.00m` · `More than 10 years` · `2024` | 1% | f1 | the 2022 bar for $400,000 or less in the 6–10 years panel; 5 also occurs at 3–5 years/$2.01m–$3.00m/2024 and at More than 10 years/More than $3.00m for both years | 是 | `6–10 years` · `$400,000 or less` · `2022` |
| 5 | 16 | `$2.01m–$3.00m` · `6–10 years` · `2022` | 1% | f1 | the 2024 bar for $401,000–$600,000 in the Less than 3 years panel; 16 recurs at Less than 3 years/$601,000–$800,000/2024, 3–5 years/$601,000–$800,000/2024, 6–10 years/$601,000–$800,000/2022 and 6–10 years/$2.01m–$3.00m/2022 | 是 | `Less than 3 years` · `$401,000–$600,000` · `2024` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——5 values given, 6 answered
- 模型预测的定位标签漏掉了规则实际用的标签——3 of 5 predicted key sets miss a rule label: 22, 5, 16

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | horizontal | 4 | 2 | 7 | 54 | 全部 | （不画值轴） |
| f1 | `other · duplicate placeholder` | na | 1 | 1 | 0 | 0 | 无 | （不画值轴） |

- **f1** Total cash compensation, by tenure at current firm (%)　[图上方]　单位 `(%)`
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=155 Source: Heidrick & Struggles US professional services partner compensation survey, 2022, n=192
- **f1** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | each pay-range row carries a dark 2024 bar above a cyan 2022 bar, e.g. 30 over 22 |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | pay ranges listed down the left, bars grow rightward from a common left edge |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or gridlines anywhere; only the printed numbers give magnitudes |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | single `2024` / `2022` swatch pair at top left governs all four panels |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | the seven pay-range labels are printed once at the far left for all four panels |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | four identical panels: Less than 3 years, 3–5 years, 6–10 years, More than 10 years |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Note: Numbers may not sum to 100%, because of rounding.` plus two `Source: Heidrick & Struggles...` lines |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | the `2024  2022` swatches sit between the title line and the panel titles |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | bold `Less than 3 years`, `3–5 years`, `6–10 years`, `More than 10 years` above each panel |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | `Total cash compensation, by tenure at current firm (%)` is the only place `%` appears |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | `30`, `57`, `33` printed within the dark bars; `22`, `27` within cyan bars |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | short bars label to the right: `3`, `2`, `5` beside stub bars in $801,000–$1.00m and More than $3.00m |

词表 65 项，本页出现 12 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `zero_value_label_no_bar` | f1 | `0` printed at the baseline for 2022 More than $3.00m (Less than 3 years) and 2024 (6–10 years) with no bar drawn | 零值只以文字出现、没有可测的图元，解析器若按条形抓取会漏掉该行，取值必须来自标签而非像素。 |
| `per_series_source_line` | f1 | two separate Source lines, one for the 2024 survey (n=155) and one for the 2022 survey (n=192) | 每个系列各有样本量来源，读数时需把n值与对应年份系列绑定，不能合并成单一来源行。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

取值本身不难：54个条形全部印了数字，无坐标轴也无需按像素估算，5%容差不成问题。真正的瓶颈是定位：一个数字需要面板（Less than 3 years / 3–5 years / 6–10 years / More than 10 years）、薪酬区间行（如 $401,000–$600,000）和年份系列（2024 / 2022）三个键才能唯一确定，而像 16 这样的数字在页面上出现五次、22 出现四次、5 出现四次。若解析器把四个面板压成一张表而丢掉面板名（面板名只是粗体文字、不在表格里），16 或 22 就无法与唯一一格对应。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | panel_title_per_panel 与 shared_axis 组合下的 panel_key | 记录字段增加 panel_key，条件行改为“四面板共享左侧类别标签、面板名仅以粗体出现在面板上方” | 有/无 panel_key 时，重复数值（16 出现5次、22 出现4次）的定位准确率对比 |
| P6 | 通用 | value_label_inside 与 value_label_outside 的混用（按条长自动切换） | 样式字段：value-label placement 增加“长条内置、短条外置”阈值选项 | 标签位置固定 vs 按长度切换时，短条（3、2、5）数值被正确归属到条形的比例 |
| P6 | 一类出版方 | 新组件 zero_value_label_no_bar | 数据记录允许 0 值并在样式中规定只画标签不画条 | 含零值行时，导出表是否保留该行（Less than 3 years / More than $3.00m / 2022 = 0） |
| P7 | 这份文档自己的习惯 | 无编号图题 + 单位写在标题括号内（unit_in_axis_or_title） | 标题字段拆分：figure_number 可空，unit 以 “(%)” 形式附于 title 末尾 | 标题带括号单位且无图号时，表格上下文命中率对比有图号的情形 |
| P3 | 这份文档自己的习惯 | new_component per_series_source_line（两条 Source 行分别对应两个系列） | 图注区支持多条 source 行，各绑定一个系列名与 n 值 | 单条 vs 多条来源行时，系列与样本量绑定是否被解析保留 |
