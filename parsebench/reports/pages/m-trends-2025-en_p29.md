# m-trends-2025-en_p29

![m-trends-2025-en_p29](../../data/pages/m-trends-2025-en_p29.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `m-trends-2025-en_p29` | m-trends-2025-en | untagged | 10 | `parsebench/data/pages/m-trends-2025-en_p29.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 本页两图皆无图号,只有两行标题:`Observed Malware Families by Category, 2024` + `Ransomware-Related`。上图是一个 8 格的马赛克/树状图,格子里直接排版巨号数字(34、16、12、10、10、7、6、5),`%` 以上标小字紧贴数字右上;类别名 `Ransomware`、`Credential Stealer` 用大字,窄格 `Tunneler`、`Downloader`、`Dropper` 缩成小字;蓝色由深到浅随数值递减。下图是 6 根竖柱,左侧竖排轴题 `% of Intrusions`,刻度 0/5/10/15,只有横向网格,数值标在柱顶内侧,x 轴标签上下交错两行且 `REDBIKE (Akira)` 换行。两图右侧都紧贴一列正文,图文共占一个横带。
> 
> **定位一个值难在哪**
> 
> 下图 `REDBIKE (Akira)` 的 10% 与 `RANSOMHUB` 的 10% 等高,而上图 `Backdoor`、`Utility` 也都是 10%——同一页四个 10。要唯一定位必须同时带图标题、类别名,且类别名要按交错换行的原样写出。
> 
> **不确定的**
> 
> 上图格子面积是否严格与百分比成比例(Tunneler 7 的格子看着比 Downloader 6 窄一线)无法确认;蓝色深浅是否只是装饰、还是编码排名,也只能猜。评分给出的第 4 个 `10` 归 Backdoor 还是 Utility 无从判断。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 页面含两个无编号图：8块比例树图与6柱纵向条形图。需支持块内类别及百分比、随块缩放的文字、柱内数值、纵排单位轴题、仅横向网格线、交错及换行的横轴标签，并让正文栏与图并排。
> 
> **定位一个值难在哪**
> 
> 柱图的“10”出现于“RANSOMHUB”和“REDBIKE (Akira)”，必须依靠横轴类别区分；后者换行且标签上下交错。数值本身均直接印出，无需按刻度估读。
> 
> **不确定的**
> 
> 两图均无图号、图例、来源或注释行。树图蓝色深浅是否编码数值未明示；首组被抽查的10按面积排序判断为“Backdoor”，但“Utility”也印有10%。

**gemini-3.1-pro**

> ### 画出来要什么
> 页面包含一个树状图（Treemap）和一个柱状图，均无图号，标题块置于图表上方，且都分为主标题和副标题（如`Ransomware-Related`）。图1（树状图）没有坐标轴，不同类别的标签和数值（带有`%`符号）直接打印在各个矩形色块内部。图2（柱状图）具有左侧值轴（带有旋转90度的标题`% of Intrusions`）和底部类别轴，所有柱子内部顶端印有白色的数值标签，x轴类别标签`REDBIKE (Akira)`被换行显示。页面排版上，正文文本在右侧与这两个图表并排环绕。
> 
> ### 定位一个值难在哪
> 定位图2中的值`10`（对应REDBIKE）会在Step 3遇到困难。它的x轴标签在图上被分为两行（第一行`REDBIKE`，第二行`(Akira)`），文本提取工具很容易在这里插入换行符或者将其识别为两个独立的词，导致与标准表格中的键值无法精确匹配。
> 
> ### 不确定的
> 图1树状图中各个矩形色块的精确排列算法（是按面积降序从左到右、从上到下，还是有特定的行列约束）无法仅从这一张静态图面上推断得出。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | treemap | 8 | — | above | all |
| opus-5 | f2 | bar | 6 | — | above | all |
| gpt-5.6-sol | f1 | treemap | 8 | — | above | all |
| gpt-5.6-sol | f2 | bar | 6 | — | above | all |
| gemini-3.1-pro | f1 | treemap | 8 | — | above | all |
| gemini-3.1-pro | f2 | bar | 6 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: Horizontal rules at 5, 10, 15 across the plot; no vertical rules；gpt-5.6-sol: Horizontal rules cross the plot at value ticks; no vertical grid lines are drawn.；gemini-3.1-pro: Figure 2 features horizontal grid lines but no vertical ones |
| `multi_figure_page` | ✓ | ✓ | — | opus-5: Two separately captioned charts: 'Observed Malware Families by Category, 2024' and 'Most Frequently Seen Malware, 2024'；gpt-5.6-sol: Two separately titled graphics show malware categories and frequently seen malware. |
| `no_value_axis` | ✓ | — | — | opus-5: Mosaic cells carry only printed percentages; no ticks, no baseline drawn anywhere |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: '% of Intrusions' set vertically along the left axis；gpt-5.6-sol: “% of intrusions” is rotated vertically beside the left axis.；gemini-3.1-pro: the y-axis title '% of Intrusions' is rotated 90 degrees |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: Body column 'Compared to the overall metrics...' runs to the right of f1; another column beside f2；gpt-5.6-sol: A body-text column beginning “Compared to global metrics” runs beside the bar chart.；gemini-3.1-pro: paragraphs of body text flow in a column to the right of both figures |
| `thin_segment_label` | ✓ | — | — | opus-5: 'Tunneler', 'Downloader', 'Dropper' shrunk to small caps inside the narrow right-hand cells |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: Axis ticks read bare 0, 5, 10, 15; scale word only in '% of Intrusions'；gpt-5.6-sol: The left value-axis title reads “% of intrusions”.；gemini-3.1-pro: the y-axis title is % of Intrusions |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: '15%', '10%', '9%', '7%' printed just inside the top of each bar；gpt-5.6-sol: All six percentages are printed in white inside the blue bars.；gemini-3.1-pro: percentage values are printed inside the blocks and bars across both figures |
| `wrapped_category_labels` | ✓ | ✓ | ✓ | opus-5: 'REDBIKE' with '(Akira)' on the line below it on the category axis；gpt-5.6-sol: “REDBIKE (Akira)” is split over two lines below its bar.；gemini-3.1-pro: REDBIKE (Akira) is wrapped onto two lines on the x-axis |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `staggered_category_ticks` | opus-5 | 3 | BEACON, REDBIKE, LOCKBIT on an upper row; RANSOMHUB, BASTA, SYSTEMBC dropped to a lower row |
| `superscript_unit_glyph_on_value_label` | opus-5 | 2,3 | '%' set as a small superscript at the top right of each giant numeral, e.g. '34' then '%' |
| `sequential_shade_by_magnitude` | opus-5 | — | Blue darkens with cell size: Ransomware darkest, Dropper 5% palest, with no legend |
| `unnumbered_figure_heading` | opus-5 | 3,4 | Neither chart carries 'Figure N'; only a bold title line plus 'Ransomware-Related' |
| `unit_in_value_labels` | gpt-5.6-sol | 2,4 | Each printed treemap number is followed by a “%” inside its tile. |
| `unit_in_value_labels` | gpt-5.6-sol | 2,4 | Each white number inside a bar includes a percent sign. |
| `staggered_x_ticks` | gpt-5.6-sol | 3 | Category labels alternate between two vertical rows beneath the baseline. |
| `unit_in_value_label` | gemini-3.1-pro | 2 | printed values include the % sign directly on the mark |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 34 | Ransomware | Observed Malware Families by Category, 2024、Ransomware | Ransomware | Ransomware | ✓ | ✓ | ✓ | 过 |
| 16 | Other | Observed Malware Families by Category, 2024、Other | Other | Other | ✓ | ✓ | ✓ | 过 |
| 12 | Credential Stealer | Observed Malware Families by Category, 2024、Credential Stealer | Credential Stealer | Credential Stealer | ✓ | ✓ | ✓ | 过 |
| 10 | Backdoor | Observed Malware Families by Category, 2024、Backdoor | Backdoor | Backdoor | ✓ | ✓ | ✓ | 过 |
| 15 | BEACON、% of Intrusions | Most Frequently Seen Malware, 2024、BEACON、% of Intrusions | BEACON | BEACON | ✓ | ✗ | ✗ | 过 |
| 10 | RANSOMHUB、% of Intrusions | Most Frequently Seen Malware, 2024、RANSOMHUB | RANSOMHUB | RANSOMHUB | ✗ | ✗ | ✗ | 过 |
| 10 | REDBIKE (Akira)、% of Intrusions | Most Frequently Seen Malware, 2024、REDBIKE、(Akira) | REDBIKE (Akira) | REDBIKE (Akira) | ✗ | ✗ | ✗ | 过 |
| 9 | BASTA、% of Intrusions | Most Frequently Seen Malware, 2024、BASTA | BASTA | BASTA | ✗ | ✗ | ✗ | 过 |
| 9 | LOCKBIT、% of Intrusions | Most Frequently Seen Malware, 2024、LOCKBIT | LOCKBIT | LOCKBIT | ✗ | ✗ | ✗ | 过 |
| 7 | SYSTEMBC、% of Intrusions | Most Frequently Seen Malware, 2024、SYSTEMBC | SYSTEMBC | SYSTEMBC | ✗ | ✗ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 3 | 3 | 1 | 未裁决 · 无实测证据 | 这一页 10 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 3 / 1 都无法证伪。 |
