# Digital_News-Report_2022_p26

![Digital_News-Report_2022_p26](../../data/pages/Digital_News-Report_2022_p26.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `Digital_News-Report_2022_p26` | Digital_News-Report_2022 | untagged | 3 | `parsebench/data/pages/Digital_News-Report_2022_p26.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 本页要同时画三块：左栏一张四列百分比堆叠柱（Facebook/Twitter/Instagram/TikTok，各段印 21%/55%/3%/20%，图例在下方，类别刻度下还叠了平台图标）；紧贴其右的一张“Top markets saying too much”排行表，按 Twitter、Facebook 分段，每行带国旗图标与百分比；右栏一张分组水平条（6 个主题 × 5 个地区），无数值轴，每根彩条压在一条贯穿全宽的灰色底槽上，图例在图上方。两图都无编号，标题为两到三行全大写，单位只靠标签里的“%”。注记行是问卷题干加各网络样本量。
> 
> ## 定位一个值难在哪
> “21%”在页面上至少出现三次：f1 中 Facebook 的 Too much 段、侧表 Facebook 组的 Hungary 与 UK 行，正文也写了“(21%)”。只有同时给出图标题、类别与系列三级标签才唯一；侧表那两处还需要“Facebook”这一分组标题来区分行。
> 
> ## 不确定的
> 侧表算 f1 的一部分还是独立图，无法判定；f3 短条的数字是画在条外还是槽内、灰槽是否代表 100% 基准，都只能从像素推测；f1 各段和为 99%（Facebook）还是取整误差，无轴可验。

**gpt-5.6-sol**

> **画出来要什么**：三种相邻构造：四个平台的等高百分比堆叠柱，带柱内数值、图例和平台标志；按 Twitter、Facebook 分组的无轴国家排名名单；五地区横向分组条，带灰色满宽轨道、上方图例及条端数值。
> 
> **定位一个值难在哪**：右图的 49% 必须同时用“Politics”和“Africa”定位；五条相邻同色序列只由上方共享图例命名。9%还在左图 TikTok 柱中重复出现。
> 
> **不确定的**：中间国家名单可能是左图的附属面板，而非独立图；其两组分别有五、六行。灰色轨道按背景处理，未计入数据标记。

**gemini-3.1-pro**

> ### 画出来要什么
> 本页包含三个图表。图1是100%堆叠柱状图，包含类别轴、图例以及段内数值标签，无数值轴，且底部带有社交媒体图标。图2是一个混合列表形式的水平柱状图，使用行内标题（Twitter、Facebook）进行面板分组，类别标签自带国旗图标，数值标在柱子外侧。图3是典型的分组水平柱状图，上方有图例，左侧为多行类别标签，同样没有数值轴。整体来看，生成器需要支持无数值轴的条形图、将面板标题直接作为行内分割插入，以及在类别标签处渲染自定义图标。
> 
> ### 定位一个值难在哪
> 以图3中的“49%”为例，图表完全省去了数值轴和网格线。虽然数值本身直接印在柱外，不需要估读，但要正确定位该值，必须将上方图例中的颜色（浅绿色代表Africa）与横向分组（Politics）关联。这种依赖“图例颜色映射+分组列表”的组合在排版紧凑时，解析器如果不能精准对齐每根柱子和对应类别的物理位置，很容易将颜色或标签分配到相邻组，导致提取错误。
> 
> ### 不确定的
> 图2中的Twitter和Facebook到底是作为两个独立的图里面板（panels），还是仅仅作为一个数据表中的行内分组标志？此处我将其视作两个面板处理，但它极简的列表排版模糊了表格与图表的边界。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 16 | — | above | all |
| opus-5 | f2 | other · ranked country list table | 10 | — | above | all |
| opus-5 | f3 | grouped_bar | 30 | — | above | all |
| gpt-5.6-sol | f1 | stacked_bar | 16 | — | above | all |
| gpt-5.6-sol | f2 | other · ranked lists | 11 | — | above | all |
| gpt-5.6-sol | f3 | grouped_bar | 30 | — | above | all |
| gemini-3.1-pro | f1 | stacked_bar | 16 | — | above | all |
| gemini-3.1-pro | f2 | bar | 11 | — | above | all |
| gemini-3.1-pro | f3 | grouped_bar | 30 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `data_table_as_figure` | ✓ | — | — | opus-5: bordered rows 'India 23% / Australia 23% / South Africa 19%' under a 'Twitter' header |
| `footnote_marker` | ✓ | — | — | opus-5: superscript 9 and 10 in body text keyed to footnotes at the page foot |
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: five coloured bars stacked one under another inside each topic slot, e.g. under 'Politics'；gpt-5.6-sol: Each topic contains five separate regional bars.；gemini-3.1-pro: multiple bars stacked horizontally for each topic |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: topic names on the left, bars grow rightwards from a common left baseline；gpt-5.6-sol: Topic labels sit left while all bars extend horizontally right.；gemini-3.1-pro: bars grow to the right from the topics |
| `icon_category_axis` | ✓ | — | ✓ | opus-5: national flag icons precede every country name; platform logos precede 'Twitter' and 'Facebook'；gemini-3.1-pro: country flags sit beside the category names |
| `legend_above_plot` | ✓ | ✓ | ✓ | opus-5: 'Europe  North America  Asia  Latin America  Africa' row sits between title and first topic；gpt-5.6-sol: The five-region legend sits between the heading and the COVID-19 bars.；gemini-3.1-pro: legend sits between the title and the plot |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'Too much  About right  Not enough  Don't know' row sits under the bars；gpt-5.6-sol: “Too much”, “About right”, “Not enough”, and “Don’t know” sit below the bars.；gemini-3.1-pro: legend items sit below the category names |
| `multi_figure_page` | ✓ | — | ✓ | opus-5: two captioned charts, each with its own question note: 'Q12_Social_rightsize ...' and 'Q. FAKE_NEWS 2021a.'；gemini-3.1-pro: three separate charts on one page |
| `no_value_axis` | ✓ | ✓ | ✓ | opus-5: no ticks or numbers along the bottom; only printed percentages at bar ends；gpt-5.6-sol: No numerical value ticks are drawn; every percentage is printed at a bar end.；gemini-3.1-pro: no value axis is drawn on the plot |
| `panel_title_per_panel` | — | ✓ | — | gpt-5.6-sol: “Twitter” and “Facebook” head the two ranked sections. |
| `pct_stacked` | ✓ | ✓ | ✓ | opus-5: all four bars reach the same top; Twitter reads 11+73+3+13 = 100；gpt-5.6-sol: All network stacks have equal height; printed segment percentages total approximately 100%.；gemini-3.1-pro: all bars reach the same total height |
| `side_text_bullets` | ✓ | — | — | opus-5: left column prose 'These data suggest the ambivalent relationship...' runs level with the right-column bar chart |
| `small_multiples_4` | — | ✓ | — | gpt-5.6-sol: Twitter and Facebook repeat the same ranked market-row layout. |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Note: Africa average is Kenya, South Africa, and Nigeria only (English speakers in South Africa and Nigeria).'；gpt-5.6-sol: “Q. FAKE_NEWS 2021a.”, “Base:”, and “Note:” appear below the plot.；gemini-3.1-pro: base note lines under the figure |
| `stacked_bar` | ✓ | ✓ | ✓ | opus-5: each platform bar holds four stacked segments, e.g. 21% / 55% / 3% / 20% on Facebook；gpt-5.6-sol: Four response segments are stacked within each network bar.；gemini-3.1-pro: stacked bars for each social network |
| `thin_segment_label` | ✓ | — | — | opus-5: Twitter's 3% magenta sliver is thinner than its own label, which touches the 13% below |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: '53%' set in white inside the right end of the orange North America COVID-19 bar；gpt-5.6-sol: Percentages including “21%”, “55%”, and “3%” are printed inside coloured segments.；gemini-3.1-pro: percentages printed inside the coloured segments |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: '9%' printed in magenta just beyond the short Asia Immigration bar；gpt-5.6-sol: Labels such as “49%” and “9%” sit just beyond the coloured bar ends.；gemini-3.1-pro: percentages printed to the right of the bars |
| `wrapped_category_labels` | ✓ | ✓ | — | opus-5: 'Climate change' and 'Products (e.g. scams)' each wrap onto two lines；gpt-5.6-sol: “Climate change” and “Products (e.g. scams)” are wrapped onto two lines. |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `bar_background_track` | opus-5 | 2 | each coloured bar sits on a light grey rectangle running the full plot width |
| `reference_table_beside_chart` | opus-5 | 1,3,4 | 'Top markets saying too much' ranked table shares the figure block, level with the stacked bars |
| `survey_question_and_base_note` | opus-5 | 4 | 'Q12_Social_rightsize ... Do you think that the amount of content ... Base: ... Facebook = 1501' |
| `grouped_rows_with_section_header` | opus-5 | 1,3 | country rows split under two bold platform headers, 'Twitter' then 'Facebook' |
| `category_logos_below_ticks` | gpt-5.6-sol | — | Four platform logos sit below the printed Facebook, Twitter, Instagram and TikTok labels. |
| `ranked_list` | gpt-5.6-sol | 1,3 | Two sections list flag, market name and right-aligned percentage without axes. |
| `country_flag_icons` | gpt-5.6-sol | — | Each market row begins with a national flag icon. |
| `unequal_panel_category_counts` | gpt-5.6-sol | 3 | Twitter lists five markets while Facebook lists six. |
| `background_bar_tracks` | gpt-5.6-sol | 2 | Every coloured bar overlays a full-width light-grey horizontal track. |
| `inline_panel_headings` | gemini-3.1-pro | 1,3 | Twitter and Facebook act as headers between rows |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 21% | Facebook、Too much | PROPORTION WHO THINK THEY SEE TOO MUCH NEWS ON EACH NETWORK – UK、Facebook、Too much | Facebook、Too much | Too much、Facebook | ✓ | ✓ | ✓ | 过 |
| 49% | Politics、Africa | PROPORTION WHO SAW FALSE OR MISLEADING INFORMATION ABOUT EACH TOPIC IN THE LAST WEEK – SELECTED REGIONS、Politics、Africa | Politics、Africa | Africa、Politics | ✓ | ✓ | ✓ | 过 |
| 9% | Immigration、Asia | PROPORTION WHO THINK THEY SEE TOO MUCH NEWS ON EACH NETWORK – UK、TikTok、Too much | Immigration、Asia | Asia、Immigration | ✗ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f2` | "other · ranked country list table" | "other · ranked lists" | "bar" | other · 排名列表（表格型图） | opus 记 `ranked country list table` 并勾了 `data_table_as_figure`，gpt 记 `ranked lists`；两家都读成「一列排好名次的数字」而不是画出来的条。gemini 的 `bar` 同时勾了 `no_value_axis`，也就是说它承认这上面没有值轴。<strong>又一条 P10 证据。</strong> |
| `hardest_step` | 3 | 3 | 1 | 未裁决 · 无实测证据 | 这一页 3 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 3 / 1 都无法证伪。 |
