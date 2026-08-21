# TRS241_Web_p88

![TRS241_Web_p88](../../data/pages/TRS241_Web_p88.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `TRS241_Web_p88` | TRS241_Web | need_estimate | 10 | `parsebench/data/pages/TRS241_Web_p88.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 一页一个编号图 FIG.2.10,但由两组异质图形组成:上排四个单色阴影(hatch)饼图,面板标题为「1969」「1979」「2000」「2015」,六个扇区只用代码「EI」「MI」「C」「A」「E」「S」加箭头引出线标在圆外,数值全印(如「30.7%」);下方一个双值轴折线图,左轴「Overall GDP (10⁹ DA 1979)」0–700,右轴「Per capita GDP (10³ DA 1979)」0–28,时间轴「Years」刻度 1969, 1974, 1979, **1985**, 1990…2015(1979→1985 间隔为 6 年,非等距)。无图例:线名「Overall GDP (1)」「GDP per capita」直接写在线旁,一条实线一条点划线;图内还有 5 个带箭头的增长率注记「(7.97 %)」「(4.85 %)」和脚注「(1) Average annual growth rate…」。图号、标题与代码释义全部在图下方。
> 
> **定位一个值难在哪**
> 「12.5」在页面上出现两次:1979 饼的 MI 与 2000 饼的 EI。要唯一定位必须同时拿到面板年份和扇区代码,而代码含义只在图下一行「MI: Manufacturing industries.」给出;解析器若丢掉面板标题,两行会互相冒充。
> 
> **不确定的**
> 折线的实际数据点位置(只在端点画了菱形/圆点标记),以及 2000 年人均 GDP 具体读数;另外这四饼+一线究竟应算一图五面板还是两图,页面只给了一个图号一条题注。

**gpt-5.6-sol**

> **画出来要什么**
> 四个年份饼图置于双轴折线图上方；饼图用外置百分比、缩写和引线。主图需双纵轴、实线与点划线、内联系列名、增长率区间箭头，并把完整图题放在下方。
> 
> **定位一个值难在哪**
> “200”要定位为“Overall GDP”在“1985”的点。左轴每格100，而5%容差仅±10，必须插值到十分之一格，并区别于右轴。
> 
> **不确定的**
> 折线未逐点画出标记；按十个年份位置估计每条线十点、全图44个标记。异质面板无法共用单一类别数，填最大值10。

**gemini-3.1-pro**

> ### 画出来要什么
> 要重绘此页面，生成器需要具备处理复合面板（Compound Figure）的强大排版能力：
> 1. **异构图表组合**：上半部分为沿时间轴水平排列的四个饼图（分别对应不同年份），下半部分为一个双轴折线图，两者共享底部标题。
> 2. **饼图标签与引线**：饼图外部的百分比标签需通过极细的指示线（leader lines）连接到对应扇区，类别使用首字母缩写。
> 3. **折线图复杂标注**：包含双Y轴（左侧总体GDP，右侧人均GDP），线段上方有行内系列名称标签，且线段之间的特定区间带有指向性的箭头及括号内的年均增长率标注（如 `(7.97%)`）。
> 4. **图内脚注与长说明文字**：折线图底部包含解释说明的内置文本 `(1) Average annual...`，且整个图表的长标题段落兼作了类别缩写的图解字典。
> 
> ### 定位一个值难在哪
> 以 `30.7`（1969年EI部门比例）为例，它的直接标签是缩写 `EI`。由于缺乏独立的标准图例，解析模型必须从底部冗长的主标题段落中跨文本定位 `EI: Extractive industries.` 才能完整赋予该值业务含义，这种“标题充当图解”的做法极大增加了标签关联的难度。
> 
> ### 不确定的
> 图中折线段之间的增长率（如 `(4.85%)`）跨越了不同长度的时间窗口，由于不是标准的点位数据，解析模型可能很难判定这些额外指标到底该依附于哪个具体年份或时间段。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | pie | 24 | — | none | all |
| opus-5 | f2 | line | 20 | FIG.2.10. | below | none |
| gpt-5.6-sol | f1 | compound | 44 | FIG.2.10. | below | some |
| gemini-3.1-pro | f1 | compound | 36 | FIG.2.10. | below | some |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | ✓ | ✓ | opus-5: arrowed notes '(7.97 %)', '(7.3 %)', '(6.7 %)', '(6.2 %)', '(4.85 %)' drawn over the curve；gpt-5.6-sol: Arrowed interval brackets inside the plot carry labels including “(7.97 %)” and “(4.85 %)”.；gemini-3.1-pro: bracketed percentages with arrows pointing to segments between line points |
| `dashed_line_series` | ✓ | ✓ | — | opus-5: Overall GDP solid, GDP per capita drawn as a dash-dot line；gpt-5.6-sol: “GDP per capita” uses a dash-dot line while “Overall GDP” is solid. |
| `dual_axis` | ✓ | ✓ | ✓ | opus-5: left 'Overall GDP (10⁹ DA 1979)' 0-700, right 'Per capita GDP (10³ DA 1979)' 0-28；gpt-5.6-sol: Left axis reads “Overall GDP (10⁹ DA 1979)”; right reads “Per capita GDP (10³ DA 1979)”.；gemini-3.1-pro: left axis is up to 700, right axis is up to 28 |
| `footnote_marker` | ✓ | ✓ | ✓ | opus-5: 'Overall GDP (1)' with note '(1) Average annual growth rate of overall GDP compared to 1979 (in brackets).'；gpt-5.6-sol: “Overall GDP” carries “(1)”, explained by the note along the plot bottom.；gemini-3.1-pro: superscript (1) on Overall GDP inline label links to note below |
| `heterogeneous_panel_types` | ✓ | ✓ | ✓ | opus-5: one caption 'FIG.2.10.' covers four pies and one dual-axis line panel；gpt-5.6-sol: Four pie panels sit above one dual-axis line panel within the numbered figure.；gemini-3.1-pro: top section features four pie charts, bottom section is a line chart |
| `inline_series_labels` | ✓ | ✓ | ✓ | opus-5: 'Overall GDP (1)' and 'GDP per capita' written beside the two lines; no legend；gpt-5.6-sol: “Overall GDP” and “GDP per capita” are written directly beside their lines inside the plot.；gemini-3.1-pro: Overall GDP (1) and GDP per capita text floats beside the lines |
| `legend_inside_plot` | ✓ | — | — | opus-5: the '(1)' explanatory note sits inside the plot frame above the x axis |
| `mixed_marks` | — | — | ✓ | gemini-3.1-pro: line series use diamond and circular point markers on top of lines |
| `panel_title_per_panel` | ✓ | — | — | opus-5: '1969', '1979', '2000', '2015' printed above each pie |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: both value-axis titles set vertically along the left and right axes；gpt-5.6-sol: Both “Overall GDP” and “Per capita GDP” axis titles run vertically beside the plot.；gemini-3.1-pro: Overall GDP and Per capita GDP y-axis titles are rotated vertically |
| `small_multiples_4` | ✓ | ✓ | — | opus-5: four identical pies in a row titled 1969, 1979, 2000, 2015；gpt-5.6-sol: Four repeated sector pie charts are titled “1969”, “1979”, “2000”, and “2015”. |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: axis titles carry '(10⁹ DA 1979)' and '(10³ DA 1979)'；gpt-5.6-sol: Axis titles include “10⁹ DA 1979” and “10³ DA 1979” while ticks are bare numbers.；gemini-3.1-pro: units (10^9 DA 1979) and (10^3 DA 1979) appear within the axis titles |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: 'EI 30.7%', 'S 38.8%' set outside the circle on arrow leader lines；gpt-5.6-sol: Sector percentages and abbreviations are printed outside each pie and connected by leader lines.；gemini-3.1-pro: percentages sit completely outside the pie slices connected by leader lines |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `pie_small_multiples_over_time` | opus-5 | 2,3 | four pies whose panel titles are years 1969, 1979, 2000, 2015 sharing one sector code set |
| `leader_line_labels_outside_pie` | opus-5 | 3 | each '%' label joined to its slice by a long arrow, some arrows crossing the circle |
| `abbrev_key_in_caption` | opus-5 | 3,4 | 'A: Agriculture. MI: Manufacturing industries. C: Construction.' defines slice codes only below the figure |
| `irregular_time_axis_spacing` | opus-5 | 2 | x ticks 1969, 1974, 1979, 1985, 1990 - a 6-year gap among 5-year gaps |
| `hatch_fill_encodes_series` | opus-5 | 3 | monochrome slices distinguished by hatching, cross-hatch and dots; no colour, no legend |
| `caption_below_plot` | gpt-5.6-sol | 4 | The caption beginning “FIG.2.10.” is printed beneath the axes rather than above the figure. |
| `caption_acts_as_legend` | gemini-3.1-pro | 3,4 | the figure caption maps the pie chart abbreviations to full sector names |
| `interval_annotations_as_data` | gemini-3.1-pro | 1,2 | growth rates (e.g. 7.97%) are drawn bridging the intervals between discrete data points |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 30.7 | 1969、EI | 1969、EI | 1969、EI | 1969、EI | ✓ | ✓ | ✓ | 过 |
| 38.8 | 1969、S | 1969、S | 1969、S | 1969、S | ✓ | ✓ | ✓ | 没过 |
| 6.1 | 1979、A | 1979、A | 1979、A | 1979、A | ✓ | ✓ | ✓ | 过 |
| 12.3 | 1979、C | 1979、C | 1979、C | 1979、C | ✓ | ✓ | ✓ | 过 |
| 19.6 | 2000、MI | 2000、MI | 2000、MI | 2000、MI | ✓ | ✓ | ✓ | 过 |
| 7.1 | 2000、E | 2000、E | 2000、E | 2000、E | ✓ | ✓ | ✓ | 过 |
| 20.5 | 2015、C | 2015、C | 2015、C | 2015、C | ✓ | ✓ | ✓ | 过 |
| 41.2 | 2015、S | 2015、S | 2015、S | 2015、S | ✓ | ✓ | ✓ | 过 |
| 200 | 1985、Overall GDP (10⁹ DA 1979) | Overall GDP (10⁹ DA 1979) | Overall GDP、1985 | not_found | ✗ | ✓ | ✗ | 没过 |
| 12.5 | 2005、Per capita GDP (10³ DA 1979) | 1979、MI | 1979、MI | 1979、MI | ✗ | ✗ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "pie" | "compound" | "compound" | compound（异质面板：饼 + 双轴折线） | 按「一个图号 = 一张图」记。opus 的 pie 是把第一个饼面板当成了 f1，就那个面板而言它是对的。 |
| `printed#f1` | "all" | "some" | "some" | some | 四个饼每个扇区都印了百分比，下面的折线只印了括号里的年均增长率、没印序列值。整图算 some。opus 的 all 是对第一个饼面板说的。 |
| `heading#f1` | [false, "none"] | [true, "below"] | [true, "below"] | 有图号，在下方 | FIG.2.10 与整段说明印在图的下方；各个饼上方的 1969 / 1979 / 2000 / 2015 是面板标题，不是图标题。 |
| `hardest_step` | 3 | 2 | 1 | 2 与 3 各一半 | 实测 10 个点过 8 个，两个失败一个 value_off（第二步）一个 label_unlinked（第三步），没有多数。opus 的 3 与 gpt 的 2 各中一半，gemini 的 1 不成立（这一页有表）。 |
| `value_axes#f1` | 0 | 2 | 2 | 2 | 折线面板左轴 Overall GDP（10⁹ DA 1979）0–700、右轴 Per capita GDP（10³ DA 1979）0–28。opus 的 0 是对饼面板说的。 |
| `key_roles#f1` | ["category", "panel"] | ["series", "time"] | ["category", "time"] | category × panel × series（整图 5 个面板） | 一个图号 FIG.2.10 下是 5 个面板：4 个饼（1969 / 1979 / 2000 / 2015）+ 1 个双轴折线。饼要「扇区标签 × 年份面板」，折线要「年份 × 系列」，整图的键至少四段。opus 把每个面板当一张图（它的 f1 = 第一个饼），gpt 与 gemini 把整体当一张图——分歧是切图粒度，三家对画的是什么完全一致。 |
