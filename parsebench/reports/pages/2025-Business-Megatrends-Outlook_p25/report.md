# 2025-Business-Megatrends-Outlook_p25

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2025-Business-Megatrends-Outlook | `untagged` | 5 | 0 |

这一页是报告6.3节正文加一张编号为Figure 1的百分比堆叠柱状图，展示11个国家/地区受访者气候变化担忧变化的三类占比。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 61% | `Overall` · `My concerns have intensifed/increased` | 1% | f1 | the Overall bar, bottom (intensified) segment | 是 | `Overall` · `My concerns have intensifed/increased` |
| 2 | 12% | `Germany` · `My concerns have subsided/decreased` | 1% | f1 | the Germany bar, top (subsided) segment | 是 | `Germany` · `My concerns have subsied/decreased` |
| 3 | 24% | `Italy` · `My concerns have not changed` | 1% | f1 | the Italy bar, middle (not changed) segment | 是 | `Italy` · `My concerns have not changed` |
| 4 | 78% | `Brazil` · `My concerns have intensifed/increased` | 1% | f1 | the Brazil bar, bottom (intensified) segment | 是 | `Brazil` · `My concerns have intensifed/increased` |
| 5 | 73% | `Indonesia` · `My concerns have intensifed/increased` | 1% | f1 | the Indonesia bar, bottom (intensified) segment | 是 | `Indonesia` · `My concerns have intensifed/increased` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 5 predicted key sets miss a rule label: 12%

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 3 | 11 | 33 | 全部 | 100%, 0 |

- **f1** Figure 1: / When asked, most consumers say their concerns about climate change have increased in the past two years / Q : How have your climate change concerns changed over the past two years?　[图上方]　单位 `Percentage of respondent`
  - 来源行：Source : Bain & Company, The Visionary CEO's Guide to Sustainability, 2024. 26

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each country bar holds three colour segments, e.g. Overall 61%, 31%, 8% stacked |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f1 | **无** | all eleven bars reach the same top and the axis top tick reads `100%` |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Source : Bain & Company, The Visionary CEO's Guide to Sustainability, 2024. 26` under the plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | three swatch entries in a row under the category axis, below `Overall ... Indonesia` |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | `Percentage of respondent` set over the plot; the axis itself only shows `100%` and `0` |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | superscript `26` after `personal experiences` and trailing the source line; `27` in later paragraph |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | `Percentage of respondent` printed above the `100%` top tick, not alongside the axis |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | `61%`, `31%`, `8%` printed on the segments of the Overall bar |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the first tick label `Overall` is set in bold while `US`, `UK`, ... are not |

词表 65 项，本页出现 9 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `survey_question_subtitle` | f1 | second heading line reads `Q : How have your climate change concerns changed over the past two years?` in bold | 该行是问卷题干而非图表标题，读数时需要靠它才能知道三个图例项属于同一道单选题、堆叠合计为100%。 |
| `stack_total_not_exactly_100` | f1 | Brazil segments print 78%, 17%, 4% = 99%; China 62%, 28%, 10% = 100% | 标签之和并不总等于100%，说明数值来自四舍五入而非从像素高度推算，取值必须用打印标签。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

取值本身不难：33个分段全部印了标签，无需按刻度估读（刻度只有`0`和`100%`两档，若靠像素读数5%容差几乎不可能，但这里不必）。真正的瓶颈是定位标签：同一数字在图中反复出现——`8%`出现在Overall、UK、France、Indonesia的顶段，`51%`出现在US与Germany，`62%`出现在Japan与China，`4%`出现在Japan与Brazil。因此一行必须同时携带国家名（`Germany`）和完整图例文本（`My concerns have subsied/decreased`），而这三段图例文字位于绘图区下方、与柱体无对应关系，解析器很容易只输出11列国家而丢掉系列名，或把三行折叠成一行。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | unit_in_axis_or_title 与 axis_title_above_axis 的组合（`Percentage of respondent` 置于 `100%` 顶刻度之上） | 样式字段中新增 unit_position 维度：axis_side / above_top_tick / in_title | 单位置于顶刻度上方 vs 置于轴标题处，比较导出表能否恢复百分比量纲 |
| P7 | 一类出版方 | survey_question_subtitle（题干作为第二行标题）与 figure_number `Figure 1:` 的拆分 | 记录字段中把标题拆成 number/title/subtitle/unit，并规定 subtitle 以粗体行落在表格上方 | 有无题干副标题时，模型能否把三条图例判定为同一单选题的互斥选项 |
| P3 | 通用 | 长图例文本作为系列键（`My concerns have intensifed/increased` 等三条置于绘图区下方） | 整页 markdown 导出规则：图例行必须成为表格列头而非游离文本 | 系列名长度（>30字符）与图例位置（下方 vs 内嵌）对定位重复数值成功率的影响 |
| P6 | 一类出版方 | highlighted_category（`Overall` 粗体作为汇总列） | 条件行中加入 aggregate_category 标记，仅以字体加粗而非配色区分 | 汇总类别仅用粗体标注时，能否与其余10个国家类别区分开 |
