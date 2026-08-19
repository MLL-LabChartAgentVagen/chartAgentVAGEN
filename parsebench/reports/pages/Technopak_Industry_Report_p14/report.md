# Technopak_Industry_Report_p14

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Technopak_Industry_Report | `untagged` | 7 | 0 |

本页顶部为一幅柱状图（Exhibit 2.5：印度历年通电村庄数量），其余为2.4节潜在增长领域的正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 3,061 | `1950` | 1% | f1 | the 1950 bar (effectively zero height) | 是 | `1950` · `Number of Villages Electrified in India (CY)` |
| 2 | 21,759 | `1961` | 1% | f1 | the 1961 bar | 是 | `1961` · `Number of Villages Electrified in India (CY)` |
| 3 | 73,739 | `1969` | 1% | f1 | the 1969 bar | 是 | `1969` · `Number of Villages Electrified in India (CY)` |
| 4 | 2,49,799 | `1980` | 1% | f1 | the 1980 bar | 是 | `1980` · `Number of Villages Electrified in India (CY)` |
| 5 | 4,70,838 | `1990` | 1% | f1 | the 1990 bar | 是 | `1990` · `Number of Villages Electrified in India (CY)` |
| 6 | 5,12,153 | `2002` | 1% | f1 | the 2002 bar | 是 | `2002` · `Number of Villages Electrified in India (CY)` |
| 7 | 5,97,464 | `2022` | 1% | f1 | the 2022 bar | 是 | `2022` · `Number of Villages Electrified in India (CY)` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 1 | 1 | 7 | 7 | 全部 | （不画值轴） |

- **f1** Exhibit 2.5 / Number of Villages Electrified in India (CY)　[图上方]　（标题里没有单位）
  - 来源行：Source: Press Information Bureau (PIB)

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only a thin baseline under the bars; no value ticks or gridlines drawn anywhere |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: Press Information Bureau (PIB)" in italics under the plot |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | each number, e.g. "5,97,464", printed in bold above the top of its bar |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | title says "(CY)" and ticks are unevenly spaced years 1950, 1961, 1969, 1980, 1990, 2002, 2022 |

词表 65 项，本页出现 4 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `indian_digit_grouping` | f1 | labels use lakh grouping: "2,49,799", "4,70,838", "5,12,153", "5,97,464" | 数字分组为印度记数法（2,49,799 而非 249,799），字符串匹配与数值解析都需按此格式处理，否则取值会失配。 |
| `unequal_time_axis_spacing` | f1 | category slots equally spaced though years jump 1950, 1961, 1969, 1980, 1990, 2002, 2022 | 时间轴按类别等距排列，不能按年份线性插值读数，只能逐个类别对应标签取值。 |
| `near_zero_bar_invisible` | f1 | 1950 bar (3,061) has no visible height; 1961 bar is a thin sliver above baseline | 最小两个柱几乎无像素高度，读值完全依赖印刷标签，无法从图形本身估计。 |

## 5 · 难在哪

卡在 **第一步 · 要有表**。

图中七个数值全部以粗体印在柱顶，无需读像素，第2步不构成障碍；寻址也只需「年份」一个键加图题，第3步很轻。真正的风险在第1步：该图无数值轴、无网格、无图例，只有一条基线和七个浮动数字标签，解析器极易把它当作散落文本或整体跳过，导致 3,061 与 1950 之间的行结构丢失。此外标签用印度记数法（2,49,799），若解析器重排千分位，匹配也会失败。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | no_value_axis 与 value_label_outside 组合（仅基线+柱顶标签的极简柱图） | 样式条件行：新增「无数值轴、无网格、标签全外置」的渲染档 | 有数值轴 vs 仅基线：比较解析器抽出可寻址表格的成功率 |
| P6 | 一类出版方 | 新组件 indian_digit_grouping（千分位分组格式作为刻度/标签格式维度） | 记录字段：数值标签的 number_format（含 lakh/crore 分组） | 西式 249,799 vs 印式 2,49,799 标签下的数值匹配命中率 |
| P4 | 一类出版方 | 新组件 unequal_time_axis_spacing（年份不等距但类别等距） | 数据生成条件行：时间类别取非等间隔年份序列 | 等间隔年份 vs 不等间隔年份类别轴对行寻址正确率的影响 |
| P7 | 通用 | 图题号与斜体标题、来源行的分离（Exhibit 2.5 + 标题 + Source 行） | 标题字段：figure_number/title/source 分列，及其相对表格的位置 | 图题作为粗体标题输出 vs 混入正文时，上下文键的可得性 |
