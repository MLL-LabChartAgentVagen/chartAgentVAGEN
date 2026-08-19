# employment_and_social_developments_in_europe_esde_2024_report_p84

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| employment_and_social_developments_in_europe_esde_2024_report | `need_estimate` | 10 | 10 |

该页为《Employment and Social Developments in Europe 2024》第88页,主体为正文与脚注,中部含一幅折线图 Chart 3.11,展示ESF+对各收入五分位就业影响的2021-2040年模拟路径。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 0.138 | `2027` · `Quintile 5` | 5% | f1 | the Quintile 5 point at its 2028 peak, just under the 0.14 gridline | 否 | `Chart 3.11` · `Quintile 5` · `2028` |
| 2 | 0.122 | `2027` · `Quintile 4` | 5% | f1 | the Quintile 4 point at its 2027 peak, just above 0.12 | 否 | `Chart 3.11` · `Quintile 4` · `2027` |
| 3 | 0.095 | `2027` · `Quintile 3` | 10% | f1 | the Quintile 2 point at its 2027 peak, between 0.08 and 0.10 | 否 | `Chart 3.11` · `Quintile 2` · `2027` |
| 4 | 0.09 | `2027` · `Quintile 1` | 10% | f1 | the Quintile 1 point at its 2027 peak, just below 0.10 | 否 | `Chart 3.11` · `Quintile 1` · `2027` |
| 5 | 0.078 | `2040` · `Quintile 5` | 5% | f1 | the Quintile 5 end point at 2040, just below 0.08 | 否 | `Chart 3.11` · `Quintile 5` · `2040` |
| 6 | 0.04 | `2040` · `Quintile 1` | 5% | f1 | the Quintile 1 end point at 2040, on the 0.04 gridline | 否 | `Chart 3.11` · `Quintile 1` · `2040` |
| 7 | 0.02 | `2021` · `Quintile 1` | 5% | f1 | the common 2021 starting point where all five lines converge at 0.02 | 否 | `Chart 3.11` · `Quintile 1` · `2021` |
| 8 | 0.11 | `2030` · `Quintile 5` | 10% | f1 | the Quintile 3 point at its 2027 peak; body text also states 'a peak of +0.11% in 2027' | 否 | `Chart 3.11` · `Quintile 3` · `2027` |
| 9 | 0.03 | `2030` · `Quintile 1` | 5% | f1 | the Quintile 1 trough around 2030, between the 0.02 and 0.04 gridlines | 否 | `Chart 3.11` · `Quintile 1` · `2030` |
| 10 | 0.10 | `2025` · `Quintile 5` | 5% | f1 | the Quintile 5 point around 2033 where the blue line crosses the 0.10 gridline | 否 | `Chart 3.11` · `Quintile 5` · `2033` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: 0.138, 0.095, 0.11, 0.10

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 5 | 20 | 100 | 无 | 0.00, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16 |

- **f1** Chart 3.11 / Investment in ALMPs is projected to increase employment during and after the investment period / Expected impact on employment of investment in labour supply increasing intervention fields of the ESF+, 2021-2027 programming period, by income quintile (% deviation from baseline)　[图上方]　单位 `% deviation from baseline`
  - 来源行：Source: JRC calculations based on RHOMOLO model.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Income quintile 5 indicates the richest quintile...' and 'Source: JRC calculations based on RHOMOLO model.' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | row of five entries 'Quintile 1 ... Quintile 5' with line swatches under the x tick row |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | 'Click here to download chart.' printed below the source line |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | subtitle ends '(% deviation from baseline)'; axis ticks are bare 0.00-0.16 |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | '% deviation from baseline' set vertically along the left value axis |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | body text carries superscript markers '(182)'...'(189)' resolved in the footnote block |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | dotted horizontal rules at each 0.02 tick, no vertical rules in the plot |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 5 quintile lines over 20 yearly ticks 2021-2040 = 100 plotted points |

词表 65 项，本页出现 8 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `unit_repeated_in_subtitle_and_axis` | f1 | '% deviation from baseline' appears both in the subtitle parenthesis and as the rotated axis title | 读数时单位有两处来源,表格若只保留其中一处仍可定标,但抽取器可能重复或漏掉该短语。 |
| `axis_ticks_finer_than_label_step` | f1 | tick labels step 0.02 while all curve movement lies within 0.02-0.14, no minor ticks | 每格0.02对应目标值(如0.138)的容差仅±0.007,须在格内做约1/3插值才能达标。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上无任何数值标签,五条线全靠像素对轴读取;刻度间距0.02,而目标值如0.138的5%容差只有±0.007,即约1/3格,0.095与0.09两值相差0.005(约1/4格),在2027年附近五条线密集交叠(2023-2025段几乎重合)时几乎无法分辨归属;此外2030年前后Quintile 1与Quintile 2骤降段斜率大,单年定位误差直接超出容差,因此取值精度是最大瓶颈,标签维度只需(季度线名+年份)两键,反而容易承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P5 | 通用 | dense_marks_100plus 与 无数值标签折线(values_printed=none)组合 | 生成条件表中提高每图标记数上限至100+,并把'折线无数值标签'设为独立取值维度 | 标记数≤40 vs ≥100 且无数值标签时的每点读数误差对比行 |
| P1 | 一类出版方 | new_components 中的 axis_ticks_finer_than_label_step(刻度步长相对数据幅度过粗) | 样式字段中新增 value_axis_tick_step 与数据量程之比这一参数 | 刻度步长/数据幅度 = 1/8 vs 1/2 时,5%容差内命中率对比行 |
| P6 | 通用 | rotated_axis_title 与 unit_in_axis_or_title 的单位位置组合 | 样式字段 unit_position:副标题括号内 / 竖排轴标题 / 两者并存 | 单位仅在副标题 vs 仅在竖排轴标题 vs 两处并存时的单位还原率行 |
| P3 | 这份文档自己的习惯 | data_link_below_figure(‘Click here to download chart.’)与 source_note_lines 的下方小字块 | 记录字段中把 note/source/download 链接作为三条独立行输出到表格下方 | 图注三行齐备 vs 仅 Source 行时,图题上下文匹配成功率行 |
| P7 | 通用 | 图题四段拆分(Chart 3.11 / 标题句 / 长副标题 / 单位短语) | 标题记录字段拆为 number、title、subtitle、unit 与 placement | 标题整块输出 vs 四段拆分输出时,值+标签联合检索命中率行 |
