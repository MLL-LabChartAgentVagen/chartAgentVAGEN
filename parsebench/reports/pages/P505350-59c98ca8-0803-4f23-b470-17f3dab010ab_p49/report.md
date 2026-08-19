# P505350-59c98ca8-0803-4f23-b470-17f3dab010ab_p49

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| P505350-59c98ca8-0803-4f23-b470-17f3dab010ab | `3d_chart` | 10 | 0 |

该页上半部分是图 2.1「按国家收入组分类的移动网络覆盖率（2022 和 2024 年）」的堆叠柱状图（2G/3G/4G/5G），下半部分是关于卫星互联网的正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 32 | `Global` · `2022` · `5G` | 1% | f1 | the Global 2022 5G segment (top red) | 是 | `Global` · `2022` · `5G` |
| 2 | 51 | `Global` · `2024` · `5G` | 1% | f1 | the Global 2024 5G segment | 是 | `Global` · `2024` · `5G` |
| 3 | 75 | `HICs` · `2022` · `5G` | 1% | f1 | the HICs 2022 5G segment | 是 | `HICs` · `2022` · `5G` |
| 4 | 84 | `HICs` · `2024` · `5G` | 1% | f1 | the HICs 2024 5G segment | 是 | `HICs` · `2024` · `5G` |
| 5 | 49 | `UMICs` · `2022` · `4G` | 1% | f1 | the UMICs 2022 4G segment (green) | 是 | `UMICs` · `2022` · `4G` |
| 6 | 65 | `UMICs` · `2024` · `5G` | 1% | f1 | the UMICs 2024 5G segment | 是 | `UMICs` · `2024` · `5G` |
| 7 | 85 | `LMICs` · `2022` · `4G` | 1% | f1 | the LMICs 2022 4G segment | 是 | `LMICs` · `2022` · `4G` |
| 8 | 35 | `LMICs` · `2024` · `5G` | 1% | f1 | the LMICs 2024 5G segment | 是 | `LMICs` · `2024` · `5G` |
| 9 | 35 | `LICs` · `2022` · `3G` | 1% | f1 | the LICs 2022 3G segment (lavender) | 是 | `LICs` · `2022` · `3G` |
| 10 | 49 | `LICs` · `2024` · `4G` | 1% | f1 | the LICs 2024 4G segment | 是 | `LICs` · `2024` · `4G` |

**程序核对**（模型没有看到左半的标签列）：

- 规则需要的键比模型报出的图能提供的多——rules need 3 keys, the richest figure offers 2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 4 | 10 | 40 | 全部 | 0, 20, 40, 60, 80, 100 |

- **f1** FIGURE 2.1 / Mobile network coverage, by country income group, 2022 and 2024　[图上方]　单位 `Population covered by mobile network (%)`
  - 来源行：Source: Original figure for this publication using calculations from the International Telecommunication Union (https://datahub.itu.int/).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each year bar stacks 2G, 3G, 4G, 5G segments, e.g. Global 2022 shows 5, 3, 57, 32 |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Source: Original figure for this publication...` and `Note: HICs = high-income countries; LICs = ...` under the plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | `2G 3G 4G 5G` swatch row sits below the plot, under the `Region` axis title |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | ticks read bare `0, 20, 40, 60, 80, 100`; `(%)` appears only in the line above the axis |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | `Population covered by mobile network (%)` printed above the `100` top tick, left aligned |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | `75`, `84`, `85`, `57` printed on top of their segments |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | thin segments' numbers `3`, `2`, `0`, `4`, `1` sit outside the bar to its right or above it |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | inner row `2022 2024` under each block, outer row `Global`, `HICs`, `UMICs`, `LMICs`, `LICs` with dividing rules |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | HICs 2022 `1` and `0`, LMICs 2024 `2` and `4` crowd at the baseline and move outside the segment |

词表 65 项，本页出现 9 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `category_axis_title_below_ticks` | f1 | `Region` printed centred below the two-level x tick rows as a category-axis title | 该行是类别轴的名称而非数值轴单位，解析时若被当作单位或标题会错配；读值仍需靠上方的 (%) 行确定量纲。 |
| `group_separator_rules` | f1 | vertical rules inside the plot box split the ten bars into five income-group blocks | 分隔线让单面板看起来像五个小面板，决定表格是用一个『收入组』列还是五个面板键来定位某个值。 |
| `stacks_below_axis_maximum` | f1 | LICs 2022 stack sums 15+35+39+1=90 while axis ends at 100; stacks reach different heights | 不能假设总和为100去反推缺失分段，每个分段必须单独读取或依赖印刷数字。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

所有40个分段的数字都印在图上，读值本身不成问题（刻度20一格也足以复核）；难点在于定位：每个值需要三层键——收入组（Global/HICs/UMICs/LMICs/LICs）、年份（2022/2024）、制式（2G/3G/4G/5G）。而 35 出现两次（LMICs 2024 的 5G 与 LICs 2022 的 3G）、49 出现两次（UMICs 2022 的 4G 与 LICs 2024 的 4G），若表格只保留年份列和制式行、把收入组丢到表外或合并到表头，这四个值就无法唯一寻址；同时 `Region` 这个轴题与实际的收入组分层不一致，进一步增加行名对齐风险。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | two_level_x_ticks 的外层分组必须进入记录键（内层年份 + 外层收入组） | 记录字段增加 group_key/outer_tick 字段，条件行中启用『两级 x 轴 + 重复内层标签』 | 『重复的内层类别标签（2022/2024 各出现5次）是否必须由外层分组键消歧』一行 |
| P7 | 一类出版方 | axis_title_above_axis 与 unit_in_axis_or_title 的组合（单位只写在图顶一行，刻度为裸数字） | 样式字段 unit_position 增加 above_top_tick 取值，标题块拆分为 number/title/unit | 『单位行位于绘图区上方而非轴旁时，量纲能否被还原』一行 |
| P6 | 通用 | value_label_outside / thin_segment_label：细分段数字被挤到柱外 | 样式字段 value_label_placement 增加 auto_escape_thin_segment 规则 | 『0–4 这类极薄分段标签外移后，标签与分段的归属是否仍可判定』一行 |
| P3 | 这份文档自己的习惯 | new_components 中的 group_separator_rules（单面板内的分组竖线） | 布局字段增加 group_divider 开关，与面板化渲染做对照 | 『分组竖线的单面板 vs 真正五面板小多图，导出表结构是否相同』一行 |
