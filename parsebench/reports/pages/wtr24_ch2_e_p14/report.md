# wtr24_ch2_e_p14

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| wtr24_ch2_e | `need_estimate` | 10 | 10 |

本页为WTO报告第43页，上方是Figure B.6双轴柱线组合图（低中收入成员提出的SPS/TBT关切数量与份额，1995-2023），下方是两栏正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 1 | `1995` · `Concerns raised by at least one low- or middle-income economy` | 10% | f1 | the 1995 bar, a sliver just above the baseline | 否 | `1995` · `Concerns raised by at least one low- or middle-income economy` |
| 2 | 100% | `1995` · `Share of concerns addressed to high-income economies` | 1% | f1 | the 1995 point of the share line, at the top of the right axis | 否 | `1995` · `Share of concerns addressed to high-income economies` |
| 3 | 31 | `2002` · `Concerns raised by at least one low- or middle-income economy` | 5% | f1 | the 2002 bar, reaching just above the 30 level | 否 | `2002` · `Concerns raised by at least one low- or middle-income economy` |
| 4 | 35% | `2002` · `Share of concerns addressed to high-income economies` | 10% | f1 | the 2002 dip of the share line, just above the 25% gridline level | 否 | `2002` · `Share of concerns addressed to high-income economies` |
| 5 | 46 | `2014` · `Concerns raised by at least one low- or middle-income economy` | 5% | f1 | the 2014 bar, the tallest of the mid-2010s | 否 | `2014` · `Concerns raised by at least one low- or middle-income economy` |
| 6 | 40% | `2014` · `Share of concerns addressed to high-income economies` | 10% | f1 | the 2015 point of the share line, between 25% and 50% | 否 | `2015` · `Share of concerns addressed to high-income economies` |
| 7 | 66 | `2020` · `Concerns raised by at least one low- or middle-income economy` | 5% | f1 | the 2020 bar, just above 60 | 否 | `2020` · `Concerns raised by at least one low- or middle-income economy` |
| 8 | 30% | `2020` · `Share of concerns addressed to high-income economies` | 10% | f1 | the 2020 trough of the share line, near 25%-30% | 否 | `2020` · `Share of concerns addressed to high-income economies` |
| 9 | 64 | `2022` · `Concerns raised by at least one low- or middle-income economy` | 5% | f1 | the 2022 bar, slightly above 60 | 否 | `2022` · `Concerns raised by at least one low- or middle-income economy` |
| 10 | 70% | `2022` · `Share of concerns addressed to high-income economies` | 10% | f1 | the 2022 peak of the share line, just below 75% | 否 | `2022` · `Share of concerns addressed to high-income economies` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: 40%

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 29 | 58 | 无 | 0, 20, 40, 60, 80, 0%, 25%, 50%, 75%, 100% |
| f1 | `compound` | vertical | 1 | 2 | 29 | 58 | 无 | 0, 20, 40, 60, 80, 0%, 25%, 50%, 75%, 100% |

- **f1** Figure B.6 / Growing number of concerns about SPS and TBT measures raised by low- and middle-income members, 1995-2023　[图上方]　（标题里没有单位）
  - 来源行：Source: Authors' calculations, based on WTO data on SPS and TBT trade concerns.
- **f1** Figure B.6 / Growing number of concerns about SPS and TBT measures raised by low- and middle-income members, 1995-2023　[图上方]　（标题里没有单位）
  - 来源行：Source: Authors' calculations, based on WTO data on SPS and TBT trade concerns.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | left axis 0-80 'Number of ... concerns', right axis 0%-100% 'Share of ... concerns addressed' |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | blue bars for counts and a light blue line for the share in the same panel |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: Authors' calculations...' and 'Note: The figure displays the evolution...' below plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two legend entries in a row under the year axis |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | title set in white on a solid blue banner directly above the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | left axis title names 'Number of ...concerns'; right axis ticks carry '%' |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | vertical titles 'Number of low- and middle-income economies' SPS and TBT concerns' on both sides |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | body text superscripts 'tariffs13', 'since 2014.12', 'economies.14' |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | year labels 1995...2023 set at about 45 degrees under the axis |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 20, 40, 60, 80; no vertical grid lines |

词表 65 项，本页出现 10 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `line_series_out_of_axis_range` | f1 | the share line at 1995 reaches 100% level at the very top, touching the axis maximum | 1995点贴在轴顶，读数只能等于上限刻度100%，无法判断是否被截断。 |
| `banner_title_reverse_text` | f1 | 'Figure B.6: Growing number of concerns...' printed white on a full-width blue band | 标题在色带内，解析器可能丢掉或与图分离，影响用标题定位表格行。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上无任何数值标签，左轴刻度间距为20（0/20/40/60/80），右轴为25个百分点一档；要把2002柱读到31（5%容差约±1.5）或把折线2015点读到40%（±2个百分点）都远小于半格，像素读数几乎不可能达到精度。加之双轴共用同一绘图区，折线点必须换算到右轴，误判轴归属会整列错。相比之下标签只需年份+系列名两个键，表格容易承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | dual_axis 与 mixed_marks 组合（柱+折线共存、右轴为百分比） | 条件行中新增“双轴混合标记”样式；记录字段需为每个系列标注所属轴（left/right）及其单位 | 有无系列到轴的显式映射时，百分比系列读数正确率的对比行 |
| P7 | 一类出版方 | rotated_axis_title（两侧竖排长轴标题承载单位） | 样式字段增加轴标题方向与位置（左竖排/右竖排），标题文本可多行换行 | 轴标题竖排 vs 置于顶端时，单位识别成功率的消融行 |
| P3 | 这份文档自己的习惯 | new_components 的 banner_title_reverse_text（蓝底反白标题带） | 整页导出时标题块的渲染与输出：标题需作为加粗标题行紧邻表格 | 标题在色带内 vs 普通黑字标题时，表格能否被正确归属图号的对比行 |
| P5 | 通用 | rotated_x_ticks 且29个年份类别（近满轴密度） | 密度上限与刻度旋转角度作为受控变量写入条件行 | 类别数29、刻度旋转45°时单点定位误差随密度变化的消融行 |
