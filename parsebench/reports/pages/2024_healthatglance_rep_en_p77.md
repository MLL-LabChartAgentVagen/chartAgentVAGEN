# 2024_healthatglance_rep_en_p77

![2024_healthatglance_rep_en_p77](../../data/pages/2024_healthatglance_rep_en_p77.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `2024_healthatglance_rep_en_p77` | 2024_healthatglance_rep_en | need_estimate | 10 | `parsebench/data/pages/2024_healthatglance_rep_en_p77.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 本页两个图形对象。Table 2.2 是带编号、蓝色标题、双列表头（`People aged 18-64` / `People aged 65 or over`）、并带两条分组小标题行（`Behavioural risk factors`）的表格，单元格内混排文字与百分比（`3% (people aged < 70)`）。Figure 2.17 是 28 国的 range/dumbbell 图：每个国家一条竖线连接一个短横线标记（`From 18 to 64 years`）与一个圆点（`65 years or over`），图例在图上方一条灰带内，y 轴 0–80 无单位、单位文字 `% of people reporting to spend 150 minutes or more per week of physical activity` 单独一行置于轴顶，x 轴国名旋转约 45°，EU27 圆点被涂成红色以示聚合。
> 
> ## 定位一个值难在哪
> 取 EU27 的 22：图上不印数字，y 轴刻度间隔为 10，5% 容差约 ±1.1，需在刻度间目视插值；且它要同时用 `EU27` 与 `65 years or over` 两个标签定位，而红色这一“聚合项”属性没有任何文字说明。
> 
> ## 不确定的
> 各点精确值全靠读轴；Slovak Rep 等缩写是否与数据源写法一致无法确认；表格中 35 与 2 是否即评分所指值，只能按行列匹配推断。

**gpt-5.6-sol**

> ### 画出来要什么
> 页面含一张分组数据表，以及一张29国单面板范围图；后者须绘制圆点、短横、垂直连接线、灰色底板、双向网格、旋转国名、图上方图例及红色EU27重点值。
> 
> ### 定位一个值难在哪
> 例如38须同时绑定“Germany”和“65 years or over”。它没有数值标签，只能依据0–80轴及10点间隔估读，还要区别圆点与短横系列。
> 
> ### 不确定的
> 20和38在图中可能各有多个近似或相同值；按阅读顺序分别归于France老年圆点和Germany老年圆点。连接线计入marks。

**gemini-3.1-pro**

> ### 画出来要什么
> 本页包含一个数据表格（Table 2.2）和一个哑铃图（Figure 2.17）。
> 绘制表格需要支持标准的行列结构以及跨行的分组表头（如`Behavioural risk factors`），且需处理特定单元格内的后缀注释（如`2% (people aged < 70)`），这类注释实际上覆盖了对应的列名上下文。
> 绘制哑铃图需要支持将极短的横线（`-`）作为独立的数据点标记（而非连线），并用垂直线段连接同一分类下两个不同系列的标记。此外，需支持对特定分类（如`EU27`）的数据点应用不同的颜色（红色）以示强调。X轴的分类标签需支持倾斜排版以适应长文本。
> 
> ### 定位一个值难在哪
> 以图2.17中`EU27`的`From 18 to 64 years`系列的值（35）为例，模型需要将图例中极其微小的短横线（`-`）与图表中垂直线段底部的横线标记正确对应。多数解析器极易将其误认为误差线或普通线段而忽略，导致无法建立正确的标签关联或无法提取该系列的值。
> 
> ### 不确定的
> 图2.17中除文本提及的数值外，其余数据点的具体数值并未标注，需依赖视觉对齐左侧Y轴的网格线（间距为10）进行估算。例如Norway的圆点看起来略低于70，估算为69。对于18至64岁组的短横线，定位精度可能会受线段本身粗细和图表清晰度的干扰。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | other · data table | 16 | Table 2.2. | above | all |
| opus-5 | f2 | other · dumbbell range plot | 56 | Figure 2.17. | above | none |
| gpt-5.6-sol | f1 | other · data table | 16 | Table 2.2. | above | all |
| gpt-5.6-sol | f2 | other · range plot | 87 | Figure 2.17. | above | none |
| gemini-3.1-pro | f1 | unreadable | 16 | Table 2.2. | above | all |
| gemini-3.1-pro | f2 | other · dumbbell chart | 56 | Figure 2.17. | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | — | — | opus-5: Ticks read 'EU27' and 'Slovak Rep' among full country names |
| `axis_title_above_axis` | ✓ | ✓ | — | opus-5: Unit line sits above the '80' top tick, not alongside the axis；gpt-5.6-sol: The percentage axis title is horizontally printed above the top-left plot edge. |
| `color_encodes_extra_attribute` | ✓ | — | — | opus-5: Red fill marks EU27 as the aggregate; legend names only the two age series |
| `data_link_below_figure` | ✓ | ✓ | — | opus-5: 'StatLink' logo and 'https://stat.link/79bcw8' under the figure；gpt-5.6-sol: “StatLink https://stat.link/79bcw8” is printed below the figure. |
| `data_table_as_figure` | ✓ | ✓ | ✓ | opus-5: Bordered table captioned 'Table 2.2. Overview of behavioural and environmental risk factors...' with column headers；gpt-5.6-sol: “Table 2.2.” captions a ruled table with two age columns.；gemini-3.1-pro: Table 2.2 is a formatted data table with a title |
| `footnote_marker` | ✓ | — | — | opus-5: '(WHO, 2020[14])' subscript reference marker in body text |
| `hgrid_only` | ✓ | — | ✓ | opus-5: White horizontal rules at 10,20,...,80; no vertical rules；gemini-3.1-pro: Only horizontal grid lines are present across the panel |
| `highlighted_category` | ✓ | ✓ | ✓ | opus-5: The EU27 dot is red while all other country dots are blue；gpt-5.6-sol: The EU27 older-age point is red while other older-age points are blue.；gemini-3.1-pro: The EU27 dot is coloured red instead of blue |
| `legend_above_plot` | ✓ | ✓ | ✓ | opus-5: Grey legend strip with both entries sits between title and plot area；gpt-5.6-sol: The two-entry legend sits between the title and plotting area.；gemini-3.1-pro: The legend sits below the heading and above the plot |
| `mixed_marks` | — | ✓ | ✓ | gpt-5.6-sol: Blue circular points and black horizontal tick markers share one panel.；gemini-3.1-pro: Uses both circles and horizontal dashes as point markers |
| `multi_figure_page` | ✓ | ✓ | ✓ | opus-5: 'Table 2.2.' and 'Figure 2.17.' each numbered with their own captions and source lines；gpt-5.6-sol: “Table 2.2.” and “Figure 2.17.” have separate captions.；gemini-3.1-pro: The page contains both Table 2.2 and Figure 2.17 |
| `panel_background` | ✓ | ✓ | ✓ | opus-5: Plot area carries a light grey tint behind the markers；gpt-5.6-sol: The plotting area has a light grey fill.；gemini-3.1-pro: The plot area has a light grey background tint |
| `range_connector_line` | ✓ | ✓ | ✓ | opus-5: Each country has a dash and a dot joined by a vertical segment；gpt-5.6-sol: A vertical segment joins the two age-series markers for each country.；gemini-3.1-pro: A vertical line connects the two markers for each category |
| `rotated_x_ticks` | ✓ | ✓ | ✓ | opus-5: Country names 'Norway','Netherlands',... set at roughly 45 degrees；gpt-5.6-sol: Country labels from “Norway” to “Romania” are diagonally rotated.；gemini-3.1-pro: Country names on the x-axis are rotated |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: The EU average is weighted.' and 'Source: Eurostat (hlth_ehis_pe2e) (the data refer to 2019).'；gpt-5.6-sol: “Note: The EU average is weighted.” and “Source: Eurostat” appear below.；gemini-3.1-pro: Both figures have Note and Source lines beneath them |
| `tick_marker_as_series` | ✓ | ✓ | ✓ | opus-5: Legend '– From 18 to 64 years' drawn as a short horizontal dash at each country；gpt-5.6-sol: “From 18 to 64 years” is represented by short horizontal ticks.；gemini-3.1-pro: The 18-64 series is drawn as a short horizontal dash |
| `unit_in_axis_or_title` | ✓ | ✓ | — | opus-5: '% of people reporting to spend 150 minutes or more per week of physical activity' above axis; ticks bare 0-80；gpt-5.6-sol: “% of people reporting to spend 150 minutes or more per week of physical activity” fixes the scale. |
| `wrapped_category_labels` | ✓ | — | — | opus-5: Row labels like 'Physical inactivity (% reporting to spend less than 150 minutes per week)' run full width |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `table_section_header_row` | opus-5 | 1,3 | Bold rows 'Behavioural risk factors' and 'Environmental risk factors (mortality)' span the table as group headers |
| `cell_text_overrides_column_header` | opus-5 | 2,3 | Cells read '3% (people aged < 70)' under column 'People aged 18-64' |
| `legend_strip_background` | opus-5 | — | Legend entries sit inside a full-width light grey band above the plot |
| `table_row_group_headers` | gpt-5.6-sol | 3 | “Behavioural risk factors” and “Environmental risk factors (mortality)” divide the table into row groups. |
| `cell_parenthetical_subgroup_qualifier` | gpt-5.6-sol | 3 | Environmental cells append qualifiers such as “(people aged < 70)” after percentages. |
| `table_section_headers` | gemini-3.1-pro | 3 | Rows like Behavioural risk factors span the table to group rows |
| `inline_cell_annotation` | gemini-3.1-pro | 3,4 | Cell reads 2% (people aged < 70) overriding the column header |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 59 | Norway、65 years or over | Norway、65 years or over | Norway、65 years or over | Netherlands、65 years or over | ✓ | ✓ | ✗ | 过 |
| 69 | Norway、From 18 to 64 years | Norway、From 18 to 64 years | Norway、From 18 to 64 years | Norway、65 years or over | ✓ | ✓ | ✗ | 过 |
| 22 | EU27、65 years or over | EU27、65 years or over | Smoking rate (% smoking daily)、People aged 18-64 | EU27、65 years or over | ✓ | ✗ | ✓ | 过 |
| 35 | EU27、From 18 to 64 years | Nutrition (% not eating any vegetable or fruit a day)、People aged 18-64 | Nutrition (% not eating any vegetable or fruit a day)、People aged 18-64 | EU27、From 18 to 64 years | ✗ | ✗ | ✓ | 过 |
| 2 | Romania、65 years or over | Extreme temperature (% deaths attributable to heat or cold wave)、People aged 18-64 | Extreme temperature (% deaths attributable to heat or cold wave)、People aged 18-64 | Environmental risk factors (mortality)、Extreme temperature (% deaths attributable to heat or cold wave)、People aged 18-64 | ✗ | ✗ | ✗ | 没过 |
| 9 | Romania、From 18 to 64 years | Smoking rate (% smoking daily)、People aged 65 or over | Smoking rate (% smoking daily)、People aged 65 or over | Behavioural risk factors、Smoking rate (% smoking daily)、People aged 65 or over | ✗ | ✗ | ✗ | 过 |
| 55 | Netherlands、65 years or over | Netherlands、65 years or over | Netherlands、65 years or over | Sweden、65 years or over | ✓ | ✓ | ✗ | 过 |
| 52 | Germany、From 18 to 64 years | Physical inactivity (% reporting to do physical activity less than once a week)、People aged 65 or over | Physical inactivity (% reporting to do physical activity less than once a week)、People aged 65 or over | Behavioural risk factors、Physical inactivity (% reporting to do physical activity less than once a week)、People aged 65 or over | ✗ | ✗ | ✗ | 过 |
| 20 | France、65 years or over | France、65 years or over | France、65 years or over | France、65 years or over | ✓ | ✓ | ✓ | 过 |
| 38 | Spain、From 18 to 64 years | Spain、From 18 to 64 years | Germany、65 years or over | Germany、65 years or over | ✓ | ✗ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "other · data table" | "other · data table" | "other · dumbbell chart" | 不裁 · 三家的第一张图不是同一张 | gemini 没把那块「带图号的表格」收成一张图（16 个图元），它的第一张是 56 个图元的哑铃图。标的不同。 |
| `type#f2` | "other · dumbbell range plot" | "other · range plot" | null | other · 区间条 / 哑铃图 | opus 记 `dumbbell range plot`、gpt 记 `range plot`，两家都记了 `range_connector_line`；命名差一个词，画法是同一种：每个类目两个点用线段连成一段区间。<strong>这是 P10 的一条证据</strong>——类型表里没有这一行。 |
| `printed#f1` | "all" | "all" | "none" | 不裁 · 三家的第一张图不是同一张 | gemini 没把页面上那块「带图号的表格」收成一张图，于是它的第一张是 56 个图元的哑铃图（值不印），而 opus 与 gpt 的第一张是 16 个图元的表格（值全印）。两个答案说的是两样东西。这件事本身是 P10 的一条证据：`data_table_as_figure` 算不算一张图，三家没有共识。 |
| `density#f1` | "≤20" | "≤20" | "21–60" | ≤20（按中位数 16 个图元） | 三家数出的图元个数是 16 / 16 / 16，中位数 16，落在 ≤20。三个数彼此相差不到一半，分歧是<档的边界>而不是读法：它们看的是同一张图，只是刚好被 20 / 60 / 150 / 400 这几条线切开。 |
| `density#f2` | "21–60" | "61–150" | null | 21–60（按中位数 56 个图元） | 三家数出的图元个数是 56 / 87 / 56，中位数 56，落在 21–60。三个数相差超过一半，取中位数所在的档；差异来自把叠在一起的图元数成一层还是两层。 |
| `hardest_step` | 2 | 3 | 3 | 2 | 以实测为准：10 个点过 9 个，唯一的失败是 value_off，相对误差 50%（第二步）。opus 报 2，命中；gpt 与 gemini 报 3。 |
| `value_axes#f1` | 0 | 0 | 1 | 不裁 · 三家的第一张图不是同一张 | 与这一页的 `printed#f1` 同因：gemini 没把「带图号的表格」收成图，第一张因此错位。 |
| `key_roles#f1` | ["category", "panel", "series"] | ["category", "series"] | ["category", "series"] | category × series | opus 与 gpt 的第一张都是那块表（gemini 错位到了哑铃图）。两家都记了行头与列头两段；opus 多记的 panel 来自表中间那条分节带（`Environmental risk factors`），那是表内的分组行，没有自己的绘图区，<strong>panel 的判据</strong>：要有自己的绘图区，而且名字要印在页面上。`label_source` 是 `not_shown` 的段进不了键——键必须逐字可复制。 |
| `key_roles#f2` | ["category", "colour_group", "series"] | ["category", "series"] | null | category × series | <strong>colour_group 的判据</strong>：只由颜色承载、既不是系列也不是类目的<strong>第三个变量</strong>。单独给某一个类目换色（`highlighted_category`）不算；图例里列出的项是 series。 opus 记的 colour_group 例子是「red dot at EU27 (aggregate)」——那是把汇总行单独标红，属于 `highlighted_category`，不是第三个变量。 |
