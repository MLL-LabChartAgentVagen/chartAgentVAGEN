# employment_and_social_developments_in_europe_esde_2024_report_p55

![employment_and_social_developments_in_europe_esde_2024_report_p55](../../data/pages/employment_and_social_developments_in_europe_esde_2024_report_p55.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `employment_and_social_developments_in_europe_esde_2024_report_p55` | employment_and_social_developments_in_europe_esde_2024_report | need_estimate | 10 | `parsebench/data/pages/employment_and_social_developments_in_europe_esde_2024_report_p55.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 本页需要两个编号图(Chart 2.8、Chart 2.9),每图两块并列面板,面板自带小标题「a) Gender employment gap」「b) Cross-country variation in gender gap」。全部是折线:实线+虚线两条系列,面板各自带图例(「Gap in pp」/「Gap in %」/「Standard deviation」),图例画在绘图区内、x 轴上方。x 轴年份旋转约45°,2.8a 每两年一个刻度而数据逐年,2.8b 与 2.9 逐年。两图面板纵轴量程不同(0–20 与 0–35 / 0–6)。2.9a 绘图区内有红色双箭头与「Gender gap」标注,量的是两条线之间的距离。图下三行小字:Note、Source、「Click here to download chart.」。
> 
> **定位一个值难在哪**
> 
> 6.5 是 Chart 2.8 b) 的「Standard deviation」2010 年点。难点有二:同名系列「Standard deviation」在 a、b 两面板各出现一次,单位一为 pp 一为 %,不带面板名就指错格;而且它没有数字标注,纵轴刻度间隔为 2,5% 容差只有 ±0.33,必须在两条刻度线之间内插。
> 
> **不确定的**
> 
> 6.5 与 5.2 究竟属于 2.8b 的虚线还是 2.8a 的虚线(2.8a 在 2008/2012 附近亦接近 6.5),我按给值顺序判为 2.8b 起止两点。绘图区是否有浅色网格线在 150 dpi 下看不出;各面板 y 轴是否共享刻度也只能按画出的两套刻度判断。

**gpt-5.6-sol**

> **画出来要什么**：整页含两个独立编号折线图；每图均为左右双面板、面板标题、旋转年份刻度和图内图例。Chart 2.8还需实线/虚线区分系列；Chart 2.9需不同纵轴范围、逐点圆标及红色双向箭头“Gender gap”。两图下方都有Note、Source和下载链接。
> 
> **定位一个值难在哪**：例如Chart 2.8中“b) Gender pay gap—Standard deviation—2022”的5.2没有印出；纵轴每格2，5%容差仅0.26，端点位置难以足够精确地估读。
> 
> **不确定的**：Chart 2.8两面板分别覆盖21年和13年，categories按较长面板记21。目标值年份依据端点位置判断；6.5与5.2尤其难由图像确认。

**gemini-3.1-pro**

> ## 画出来要什么
> 本页包含两个带编号的图表，都是双面板的折线图。生成器需要支持：在同一页面绘制多个独立图表；每个面板上方具有独立的面板标题；各个面板独立的Y轴量程（例如Chart 2.9面板a为0-35，面板b为0-6）；时间轴刻度文本旋转90度；支持稀疏时间刻度（如2002, 2004，但数据点可能是年度的）；在同一个图表中同时使用实线和虚线来区分不同的数据系列；支持面板级别的独立图例（Chart 2.8中两个面板各自在底部带有图例）；以及在图表内部绘制跨越系列的标注（如Chart 2.9面板a中的红色双向箭头和文本说明）。此外还需处理图表底部的多行注释、数据来源和数据下载链接。
> 
> ## 定位一个值难在哪
> 定位数据值并不难，每个值可以通过面板名称、图例名称和年份唯一定位。核心难点在于**读取精度**。所有数值都没有直接标注在数据点上，且图表内缺乏任何辅助对齐的网格线，必须完全依靠Y轴进行估算。以 Chart 2.8 a) 的“Gap in pp”线在2022年的值为例，目标值是10.5，而Y轴刻度间距为2，5%的容忍度仅为0.525，在视觉上准确区分10.5与10或11几乎是不可能的。
> 
> ## 不确定的
> 图表中并未明确说明数据点是否为严格的年度频次，仅能通过线条的波动和上下文推测为逐年数据。Chart 2.9 b) 缺少图例，只能推断其唯一系列由面板标题直接代表。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 68 | Chart 2.8 | above | none |
| opus-5 | f2 | line | 48 | Chart 2.9 | above | none |
| gpt-5.6-sol | f1 | line | 68 | Chart 2.8 | above | none |
| gpt-5.6-sol | f2 | line | 48 | Chart 2.9 | above | none |
| gemini-3.1-pro | f1 | line | 68 | Chart 2.8 | above | none |
| gemini-3.1-pro | f2 | line | 48 | Chart 2.9 | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | ✓ | ✓ | opus-5: red double-headed arrow between the two lines labelled 'Gender gap' inside panel a；gpt-5.6-sol: A red double-headed arrow inside panel a is labelled “Gender gap”.；gemini-3.1-pro: red Gender gap arrow between two lines |
| `dashed_line_series` | ✓ | ✓ | ✓ | opus-5: 'Standard deviation' drawn as a dashed line, 'Gap in pp' solid, same colour family；gpt-5.6-sol: “Standard deviation” is dashed while each gap series is solid.；gemini-3.1-pro: Standard deviation drawn as a dashed line |
| `data_link_below_figure` | ✓ | ✓ | ✓ | opus-5: 'Click here to download chart.' under the Source line of Chart 2.9；gpt-5.6-sol: “Click here to download chart.” appears below the source.；gemini-3.1-pro: Click here to download chart. text below the source line |
| `footnote_marker` | ✓ | — | — | opus-5: superscript markers (95) (96) (97) (98) in the body text between the two charts |
| `legend_inside_plot` | ✓ | ✓ | — | opus-5: 'Men (%)  Women (%)' drawn inside panel a plot area above the axis；gpt-5.6-sol: The “Men (%)” and “Women (%)” legend sits inside panel a near zero. |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: 'Chart 2.8' and 'Chart 2.9' each with own title, Note and Source lines；gpt-5.6-sol: Two independent figures are numbered “Chart 2.8” and “Chart 2.9”.；gemini-3.1-pro: Chart 2.8 and Chart 2.9 appear on the same page |
| `panel_title_per_panel` | ✓ | ✓ | ✓ | opus-5: 'a) % of workers in education, health and social work by gender' above left panel；gpt-5.6-sol: Each panel has a separate wrapped title beginning “a)” or “b)”.；gemini-3.1-pro: a) Gender employment gap |
| `per_panel_axis_range` | ✓ | ✓ | ✓ | opus-5: panel a y axis 0 to 35 by 5; panel b y axis 0 to 6 by 1；gpt-5.6-sol: Panel a spans 0–35; panel b spans 0–6.；gemini-3.1-pro: y-axis is 0-35 in panel a, 0-6 in panel b |
| `per_panel_legend` | ✓ | ✓ | ✓ | opus-5: panel a legend 'Gap in pp / Standard deviation'; panel b 'Gap in % / Standard deviation'；gpt-5.6-sol: Each panel has its own two-entry legend near the bottom.；gemini-3.1-pro: legends under a) and b) separately in Chart 2.8 |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: '2008' to '2023' set vertically under both panels；gpt-5.6-sol: All yearly x-axis labels from “2008” to “2023” are rotated vertically.；gemini-3.1-pro: year ticks are turned 90 degrees on the x-axis |
| `small_multiples_4` | ✓ | ✓ | — | opus-5: two panels a) and b) side by side under one chart number；gpt-5.6-sol: Two side-by-side line panels are labelled “a)” and “b)”. |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: Break in the EU-LFS employment time series...' 'Source: DG EMPL calculations based on EU-LFS dataset lfsa_egan2'；gpt-5.6-sol: Lines beginning “Note:” and “Source:” appear below the panels.；gemini-3.1-pro: Note: ... Source: ... under both figures |
| `sparse_time_ticks` | ✓ | ✓ | ✓ | opus-5: panel a ticks '2002, 2004, 2006 ... 2022' while the line has yearly points；gpt-5.6-sol: Panel a plots annual data but labels alternate years from “2002” to “2022”.；gemini-3.1-pro: ticks read 2002, 2004... but the line fluctuates in between |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: panel title 'a) % of workers in education, health and social work by gender'; y ticks bare 0-35；gpt-5.6-sol: Panel title begins “a) % of workers in education,”. |
| `unit_in_series_name` | ✓ | ✓ | ✓ | opus-5: legend entries read 'Men (%)' and 'Women (%)'；gpt-5.6-sol: Legend entries are “Men (%)” and “Women (%)”.；gemini-3.1-pro: Gap in pp and Gap in % in legends |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `duplicate_series_name_across_panels` | opus-5 | 3 | 'Standard deviation' is the legend label in both panel a (pp) and panel b (%) |
| `per_panel_unit` | opus-5 | 3,4 | panel a measures 'Gap in pp', panel b 'Gap in %', on identical 0-20 axes |
| `between_series_distance_annotation` | opus-5 | 4 | red vertical double arrow spanning from Men line to Women line, labelled 'Gender gap' |
| `per_panel_time_range` | gpt-5.6-sol | 2,3 | Panel a spans 2002–2022, whereas panel b spans 2010–2022. |
| `point_markers_on_line` | gpt-5.6-sol | 2 | Panel b draws a circular marker at every yearly line point. |
| `panel_without_legend` | gemini-3.1-pro | 3 | panel b) has one line series but no legend drawn |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 18.0 | 2002、Gap in pp | a) Gender employment gap、Gap in pp、2002 | a) Gender employment gap、Gap in pp、2002 | a) Gender employment gap、Gap in pp、2002 | ✓ | ✓ | ✓ | 过 |
| 10.5 | 2022、Gap in pp | a) Gender employment gap、Gap in pp、2022 | a) Gender employment gap、Gap in pp、2022 | a) Gender employment gap、Gap in pp、2022 | ✓ | ✓ | ✓ | 过 |
| 9.5 | 2002、Standard deviation | a) Gender employment gap、Standard deviation、2002 | a) Gender employment gap、Standard deviation、2002 | a) Gender employment gap、Standard deviation、2002 | ✓ | ✓ | ✓ | 过 |
| 15.8 | 2010、Gap in % | b) Gender pay gap、Gap in %、2010 | b) Gender pay gap、Gap in %、2010 | b) Gender pay gap、Gap in %、2010 | ✓ | ✓ | ✓ | 过 |
| 12.8 | 2022、Gap in % | b) Gender pay gap、Gap in %、2022 | b) Gender pay gap、Gap in %、2022 | b) Gender pay gap、Gap in %、2022 | ✓ | ✓ | ✓ | 过 |
| 6.5 | 2010、Standard deviation | b) Gender pay gap、Standard deviation、2010 | b) Gender pay gap、Standard deviation、2010 | b) Gender pay gap、Standard deviation、2010 | ✓ | ✓ | ✓ | 过 |
| 5.2 | 2022、Standard deviation | b) Gender pay gap、Standard deviation、2022 | b) Gender pay gap、Standard deviation、2022 | b) Gender pay gap、Standard deviation、2022 | ✓ | ✓ | ✓ | 过 |
| 7.0 | 2008、Men (%) | a) % of workers in education, health and social work by gender、Men (%)、2008 | a) % of workers in education, health and social work by gender、Men (%)、2008 | a) % of workers in education, health and social work by gender、Men (%)、2008 | ✓ | ✓ | ✓ | 过 |
| 26.5 | 2008、Women (%) | a) % of workers in education, health and social work by gender、Women (%)、2008 | a) % of workers in education, health and social work by gender、Women (%)、2008 | a) % of workers in education, health and social work by gender、Women (%)、2008 | ✓ | ✓ | ✓ | 过 |
| 30.5 | 2023、Women (%) | a) % of workers in education, health and social work by gender、Women (%)、2023 | a) % of workers in education, health and social work by gender、Women (%)、2023 | a) % of workers in education, health and social work by gender、Women (%)、2023 | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
