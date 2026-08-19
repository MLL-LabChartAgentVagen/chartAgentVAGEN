# employment_and_social_developments_in_europe_esde_2024_report_p80

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| employment_and_social_developments_in_europe_esde_2024_report | `need_estimate` | 10 | 10 |

本页为《Employment and Social Developments in Europe 2024》第84页，正文讨论ESF+技能投资的宏观影响，中部有一幅Chart 3.8柱状图叠加折线的混合图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 0.009 | `2021` · `Cohesion Expenditure` | 10% | f1 | the 2021 Cohesion Expenditure bar, just under the 0.01 gridline | 否 | `Chart 3.8` · `Cohesion Expenditure` · `2021` |
| 2 | 0.032 | `2027` · `Cohesion Expenditure` | 5% | f1 | the 2027 Cohesion Expenditure bar, slightly above the 0.03 gridline | 否 | `Chart 3.8` · `Cohesion Expenditure` · `2027` |
| 3 | 0.025 | `2028` · `Cohesion Expenditure` | 5% | f1 | the 2025 Cohesion Expenditure bar, between 0.02 and 0.03 | 否 | `Chart 3.8` · `Cohesion Expenditure` · `2025` |
| 4 | 0.003 | `2030` · `Cohesion Expenditure` | 20% | f1 | the 2030 Cohesion Expenditure bar, the last short bar near the baseline | 否 | `Chart 3.8` · `Cohesion Expenditure` · `2030` |
| 5 | 0.001 | `2021` · `Changes in GDP compared to baseline` | 20% | f1 | the 2021 point of the green 'Changes in GDP compared to baseline' line, just above zero | 否 | `Chart 3.8` · `Changes in GDP compared to baseline` · `2021` |
| 6 | 0.023 | `2026` · `Changes in GDP compared to baseline` | 5% | f1 | a mid-2020s point of the green GDP line, around 2026, between 0.02 and 0.03 | 否 | `Chart 3.8` · `Changes in GDP compared to baseline` · `2026` |
| 7 | 0.034 | `2029` · `Changes in GDP compared to baseline` | 5% | f1 | a point of the green GDP line around 2029-2030, between 0.03 and 0.04 | 否 | `Chart 3.8` · `Changes in GDP compared to baseline` · `2029` |
| 8 | 0.039 | `2036` · `Changes in GDP compared to baseline` | 1% | f1 | the peak of the green GDP line at 2036, cited in text as the 2036 peak | 否 | `Chart 3.8` · `Changes in GDP compared to baseline` · `2036` |
| 9 | 0.037 | `2040` · `Changes in GDP compared to baseline` | 5% | f1 | the 2040 endpoint of the green GDP line, slightly below 0.04 | 否 | `Chart 3.8` · `Changes in GDP compared to baseline` · `2040` |
| 10 | 0.038 | `2033` · `Changes in GDP compared to baseline` | 5% | f1 | a green GDP line point near 2034 (or 2039) on the plateau just under 0.04 | 否 | `Chart 3.8` · `Changes in GDP compared to baseline` · `2034` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 0.025, 0.038

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 20 | 30 | 无 | 0.00, 0.01, 0.02, 0.03, 0.04, 0.05 |

- **f1** Chart 3.8 / Investment in skills can lead to long-term GDP gains / Expenditure on skills-related ESF+ programmes over 2021-2027 programming period (% over baseline GDP) and expected impact of the investment on GDP (% deviation from baseline GDP)　[图上方]　单位 `% deviation from baseline`
  - 来源行：Source:   JRC calculations based on RHOMOLO model.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | Blue bars for 'Cohesion Expenditure' with a green line 'Changes in GDP compared to baseline' in one panel |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note:  'Baseline' constitutes a scenario with no additional investment." and "Source:  JRC calculations based on RHOMOLO model." |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | Blue swatch 'Cohesion Expenditure' and green line 'Changes in GDP compared to baseline' sit below the axis |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | "Click here to download chart." printed under the source line |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | Subtitle reads '(% over baseline GDP)' and '(% deviation from baseline GDP)'; ticks are bare 0.00-0.05 |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | '% deviation from baseline' set vertically along the left value axis |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | Body text carries superscripts (171), (172), (173), (174), (175) with footnotes below |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | Dotted horizontal rules at 0.01, 0.02, 0.03, 0.04, 0.05; no vertical rules |

词表 65 项，本页出现 8 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `bars_end_before_axis_end` | f1 | Blue bars stop at 2030 while the x axis and green line continue to 2040 | 读取2031-2040年时该系列没有柱子，是真实缺失而非零值，表格行须区分空白与0。 |
| `legend_swatch_shape_by_mark_type` | f1 | Legend uses a filled rectangle for bars and a short green line for the line series | 图例形状本身指示该值应按柱高还是按折线读取，影响定位具体标记。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

轴刻度只有0.00至0.05共6格，每格0.01约占80像素；5%容差在0.003这一档只有±0.00015，约1.2像素，柱顶线宽本身就超过该量。折线在2033-2040间几乎平坦（0.037-0.039），相邻年份差值0.001即8像素，但曲线无点标记，20个年份要靠刻度位置反推，区分0.038与0.039几乎不可能。相比之下标签只需系列名+年份两个键，图表编号与标题都以粗体样式印在图上方，寻址不成问题。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P4 | 通用 | mixed_marks（柱+线同轴）与图例形状区分 | 图表族权重向量中增加bar+line复合族，并在style字段中加入legend_swatch_shape | 复合族（柱线混合）占比0% vs 10%时，模型对同轴双系列取值的准确率对比 |
| new | 一类出版方 | new_components中的bars_end_before_axis_end（柱系列早于时间轴结束） | 记录字段中允许某系列在部分类别缺值，并与missing_value_marker区分 | 含部分年份缺柱的时间序列 vs 全覆盖序列，缺值年份被误报为0的比例 |
| P7 | 通用 | rotated_axis_title + unit_in_axis_or_title（'% deviation from baseline'竖排，副标题携带两套单位） | P7的heading字段拆分：unit_text可来自旋转轴标题或副标题，并标注归属系列 | 单位仅在副标题/竖排轴标题 vs 写入图例名时，导出表格单位缺失率 |
| P1 | 通用 | 小数刻度密度（0.00-0.05，步长0.01）下的每标记可达精度 | 将readable从布尔门改为按标记像素高度计算的容差，纳入P1 | 值小于最小刻度1/3的标记（如0.003）单独统计命中率 |
| P3 | 这份文档自己的习惯 | data_link_below_figure（'Click here to download chart.'） | 图下附注区新增下载链接行，与Source/Note并列 | 有/无下载链接行时，解析器把链接误当source_line的比例 |
