# SPI_2025_Benchmark_Report_p198

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| SPI_2025_Benchmark_Report | `untagged` | 4 | 0 |

该页为《2025 Professional Services Maturity Benchmark》财务与运营支柱章节正文，页面中部为 Figure 31 三联面板柱状图，右上角有装饰性图标。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 96.2% | `Percent of annual revenue target achieved` · `2021` | 1% | f1 | the 2021 bar in the left panel | 是 | `Figure 31:` · `Finance & Operations Trends of Note` · `Percent of annual revenue target achieved` · `2021` |
| 2 | 88.8% | `Percent of annual margin target achieved` · `2022` | 1% | f1 | the 2022 bar in the middle panel | 是 | `Figure 31:` · `Finance & Operations Trends of Note` · `Percent of annual margin target achieved` · `2022` |
| 3 | 15.4% | `Profit (EBITDA %)` · `2023` | 1% | f1 | the 2023 bar in the right panel | 是 | `Figure 31:` · `Finance & Operations Trends of Note` · `Profit (EBITDA %)` · `2023` |
| 4 | 9.8% | `Profit (EBITDA %)` · `2024` | 1% | f1 | the 2024 bar in the right panel | 是 | `Figure 31:` · `Finance & Operations Trends of Note` · `Profit (EBITDA %)` · `2024` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——4 values given, 5 answered

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 3 | 1 | 5 | 15 | 全部 | left panel: 82%, 84%, 86%, 88%, 90%, 92%, 94%, 96%, 98%; middle panel: 84%, 85%, 86%, 87%, 88%, 89%, 90%, 91%, 92%, 93%; right panel: 0%, 2%, 4%, 6%, 8%, 10%, 12%, 14%, 16%, 18% |

- **f1** Figure 31: / Finance & Operations Trends of Note　[图上方]　（标题里没有单位）
  - 来源行：Source: SPI Research, February 2025

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left axis 82%-98%, middle 84%-93%, right 0%-18% |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | left panel lowest tick 82%, middle panel lowest tick 84%, no break glyph |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | three same-form yearly bar panels side by side under one figure number |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: SPI Research, February 2025" in italics under the figure frame |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | each panel headed "Percent of annual revenue target achieved", "Percent of annual margin target achieved", "Profit (EBITDA %)" |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | right panel titled "Profit (EBITDA %)"; titles read "Percent of annual ... target achieved" |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | "96.2%", "92.1%", "9.8%" printed in white boxes on the bar tops |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | whole figure sits in a pale green rounded frame, plot areas tinted green |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at each tick across all three panels, no vertical rules |

词表 65 项，本页出现 9 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `colored_keyword_in_panel_title` | f1 | in panel titles the words "revenue" and "margin" are set in green, rest in black | 面板标题中被着色的词是区分左右两个面板的唯一关键词，解析时若丢失颜色仍需保留完整标题文本，否则两个百分比面板无法区分。 |
| `figure_frame_box` | f1 | all three panels enclosed in one rounded green-outlined box separating them from body text | 整框把三个面板绑成一个 Figure 31，读值时须先确认三面板属同一图号，再用面板名定位。 |

## 5 · 难在哪

卡在 **第四步 · 表外上下文**。

四个目标值都印在柱上，读数误差为零，第2步不构成阻碍；真正的风险在面板名。左panel 2020 与中panel 2021 都写着 92.1%，只有面板标题能区分两者，而这三个标题是画在图形内部的小字（“Percent of annual revenue target achieved” 等），解析器多半只输出年份×数值的一张表或三张无名表，标题不会变成加粗行或小节标题；同时三面板轴范围不同（82–98%、84–93%、0–18%），跨面板无法用刻度反推归属，一旦面板名缺失，15.4% 与 9.8% 仍可靠 EBITDA 量级判断，但 88.8% 之类会失去唯一定位。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | per_panel_axis_range 与 panel_title_per_panel 组合下的 panel_key | 记录字段中加入 panel_key，并在条件行中要求同一图号内三面板各自独立刻度起点 | “同图多面板、面板名仅画在图内”一行：对比有/无 panel_key 时重复数值（如两处 92.1%）的定位准确率 |
| P7 | 通用 | 图题拆分为 number/title/unit 字段（Figure 31: + 标题 + 面板级单位 “Profit (EBITDA %)”） | 样式字段 heading，placement 设为 above，面板标题另存为 panel_title | “图号+标题+面板名三层上下文是否导出为加粗/标题文本”一行 |
| P6 | 一类出版方 | axis_starts_above_zero 与带 % 后缀刻度的组合 | 样式维度中的刻度格式与轴起点（最低刻度 82%/84%） | “轴不从零开始且刻度带单位后缀”一行：检验柱长与数值不成比例时的读数策略 |
| P6 | 一类出版方 | value_label_inside（白底标签压在柱顶） | 样式字段 value-label placement 增加 inside-at-bar-top 取值 | “标签内置于柱内 vs 柱外”一行：对比印值时是否仍需像素读数 |
