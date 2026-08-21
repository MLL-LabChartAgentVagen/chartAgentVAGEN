# Digital_News-Report_2022_p63

![Digital_News-Report_2022_p63](../../data/pages/Digital_News-Report_2022_p63.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `Digital_News-Report_2022_p63` | Digital_News-Report_2022 | untagged | 4 | `parsebench/data/pages/Digital_News-Report_2022_p63.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 一页要同时画八块：①左右两个 16 行水平条形面板（TV, RADIO AND PRINT / ONLINE），每条含深浅两色（周触达 vs 每周 3 天以上），无数值轴，大条数字在条内、小条数字在条外，并在图内叠一个方框注释「BBC TV News: 44% / BBC Radio News: 18%」；②两张 10 年折线（4 线带图例、3 线只用笔记本/平板/手机图标区分），端点写值；③带洋红标题条的迷你折线＋巨大「34%」；④15 行 100% 堆叠信任条（0%–100%，中段 Neither 不标数）；⑤多个大数字 KPI（9%、25%、21%、20%）与图标；⑥带品牌图标的排名表。
> 
> ## 定位一个值难在哪
> 「18」在页面出现三次：ONLINE 面板 Guardian online 的条、注释框里的 BBC Radio News: 18%、以及 BRAND TRUST SCORES 中 ITV News 的 Don't trust。要唯一定位必须同时给面板名「ONLINE」＋类目「Guardian online」＋图例「Weekly use / online brands」，缺一即指向别处。
> 
> ## 不确定的
> 每条深浅两色究竟是相加堆叠还是「3天以上」作为子集叠在周触达之上，看不出来；印出的数字只有一个，另一段无法读到 5%。f4 三条线只有图标，无文字名；f7 灰色 Neither 段全无数字。

**gpt-5.6-sol**

> **画出来要什么**
> 需重建双面板“周使用总量＋高频使用子集”叠覆横条、两组多系列折线、图标代替系列名、信任度KPI卡、100%堆叠横条，以及左右分栏的数据表。
> 
> **定位一个值难在哪**
> “50”虽印在条内，仍须同时关联“TV, RADIO AND PRINT”“BBC News (TV & radio)”和“Weekly use”；共享图例远离标记，标签关联比读数更难。
> 
> **不确定的**
> 顶部深色条看似覆盖在浅色周使用总量上，而非可相加的堆叠段；设备折线只有图标、没有文字系列名。

**gemini-3.1-pro**

> ### 画出来要什么
> 页面包含多个独立图表。图1是水平分面条形图（可能是覆盖或堆叠），图例放置在左侧独立列，**完全没有绘制数值轴**，只在条形末端标有总值。图2和图3是折线图，其中图3的图例完全由纯图标（笔记本、平板、手机）组成，没有文字标签。图4是单线折线图，伴随巨大的“34%”标注作为数据呼出。图5是100%水平堆叠条形图，中间段（Neither）没有标注数值。图6是带有多列的数据表格。页面整体排版复杂，多图并列且夹杂着大字体的图文信息模块。
> 
> ### 定位一个值难在哪
> 以图1中的深色段（如“BBC News online”的 More than 3 days per week 频次）为例，由于该面板**完全没有绘制X轴**，且深色分段上也没有打印具体数值，导致无论是读者还是模型，都无从参考，完全无法读出该段的具体数值（在步骤2被阻断）。此外，图3的图例仅有图标，使得自动化表格很难准确地将颜色关联到具体的设备文本标签。
> 
> ### 不确定的
> 图1的条形到底是堆叠（深浅色独立相加）还是覆盖（浅色代表总数，深色代表其子集），仅从视觉上无法绝对判断；但因为标在末端的数值代表总触达率，推测应为覆盖，解析时容易被误认为标准堆叠。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | stacked_bar | 64 | — | beside | some |
| opus-5 | f2 | unreadable | 0 | — | beside | all |
| opus-5 | f3 | line | 40 | — | above | some |
| opus-5 | f4 | line | 30 | — | above | some |
| opus-5 | f5 | line | 8 | — | above | some |
| opus-5 | f6 | unreadable | 0 | — | above | all |
| opus-5 | f7 | stacked_bar | 45 | — | above | some |
| opus-5 | f8 | other · ranked data table | 0 | — | above | all |
| opus-5 | f9 | unreadable | 0 | — | below | all |
| gpt-5.6-sol | f1 | other · overlaid bars | 64 | — | beside | some |
| gpt-5.6-sol | f2 | line | 40 | — | above | some |
| gpt-5.6-sol | f3 | line | 30 | — | above | some |
| gpt-5.6-sol | f4 | line | 8 | — | above | some |
| gpt-5.6-sol | f5 | other · KPI cards | 4 | — | above | all |
| gpt-5.6-sol | f6 | stacked_bar | 45 | — | above | some |
| gpt-5.6-sol | f7 | other · data table | 24 | — | above | all |
| gemini-3.1-pro | f1 | stacked_bar | 60 | — | beside | some |
| gemini-3.1-pro | f2 | line | 40 | — | above | some |
| gemini-3.1-pro | f3 | line | 30 | — | above | some |
| gemini-3.1-pro | f4 | line | 8 | — | above | some |
| gemini-3.1-pro | f5 | stacked_bar | 45 | — | above | some |
| gemini-3.1-pro | f6 | other · data table | 12 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | — | ✓ | opus-5: '34%' and '=36/46 markets' drawn inside the panel beside the mini line chart；gemini-3.1-pro: BBC TV News: 44% is in a floating box |
| `data_table_as_figure` | ✓ | ✓ | ✓ | opus-5: Ruled table headed 'Rank  Brand  For News  For All' repeated in two blocks；gpt-5.6-sol: Ruled rows under “TOP SOCIAL MEDIA AND MESSAGING” have repeated column headers and numeric cells.；gemini-3.1-pro: TOP SOCIAL MEDIA is a formatted data table |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: Brand names down the left, bars run right to the 100% mark；gpt-5.6-sol: Brand names form the left category axis and stacks extend rightward.；gemini-3.1-pro: bars in WEEKLY REACH grow left to right from categories |
| `icon_category_axis` | ✓ | — | — | opus-5: Facebook, Twitter, WhatsApp, YouTube, Instagram, Messenger logos in the row-label column |
| `legend_above_plot` | ✓ | ✓ | — | opus-5: 'Online (incl. social media) / TV / Social media / Print' keyed right of the title, above the plot；gpt-5.6-sol: The four-item legend sits between “SOURCES OF NEWS” and the line plot. |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: 'Trust  Neither  Don't trust' swatches sit under the 0%/100% axis；gpt-5.6-sol: “Trust”, “Neither”, and “Don’t trust” appear below the 0%–100% axis.；gemini-3.1-pro: Trust, Neither, Don't trust is below the plot area |
| `legend_beside_plot` | ✓ | ✓ | ✓ | opus-5: Four-entry colour key stacked in the left column under 'TOP BRANDS'；gpt-5.6-sol: The weekly-use legend is a column to the left of both bar panels.；gemini-3.1-pro: legend is placed in a left column beside the charts |
| `multi_figure_page` | ✓ | — | ✓ | opus-5: Separate titled blocks: WEEKLY REACH OFFLINE AND ONLINE, SOURCES OF NEWS, DEVICES FOR NEWS, BRAND TRUST SCORES；gemini-3.1-pro: six distinct charts and tables share the same page |
| `no_value_axis` | ✓ | ✓ | ✓ | opus-5: No ticks or baseline numbers under the bars; only the printed figures 50, 27, 15...；gpt-5.6-sol: The bar panels have no numeric ticks; totals are available only from printed labels.；gemini-3.1-pro: the bar chart panels lack any value axis or ticks |
| `panel_title_per_panel` | ✓ | ✓ | ✓ | opus-5: Magenta filled banner reads 'Change over time 2015-2022' above the mini line；gpt-5.6-sol: “TV, RADIO AND PRINT” and “ONLINE” are printed above their respective panels.；gemini-3.1-pro: TV, RADIO AND PRINT and ONLINE are printed above panels |
| `pct_stacked` | ✓ | ✓ | ✓ | opus-5: Every bar spans the same width; axis under them reads '0%' to '100%'；gpt-5.6-sol: Every brand stack reaches the common “100%” endpoint.；gemini-3.1-pro: all bars in BRAND TRUST SCORES span exactly from 0 to 100% |
| `shared_legend` | ✓ | ✓ | — | opus-5: One left-column key covers both the TV/radio/print and ONLINE panels；gpt-5.6-sol: One four-entry legend at left governs both “TV, RADIO AND PRINT” and “ONLINE”. |
| `side_text_bullets` | ✓ | ✓ | — | opus-5: 'Public broadcasters such as the BBC, ITV, and Channel 4 remain...' runs in a column left of the trust charts；gpt-5.6-sol: The paragraph beginning “Public broadcasters such as the BBC” runs beside the trust graphics. |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Trust = % scored 6–10 on 10-point scale, Don't trust = 0–4, Neither = 5...'；gpt-5.6-sol: Small print below begins “Trust = % scored 6–10 on 10-point scale”.；gemini-3.1-pro: Trust = % scored 6-10 appears under the figure |
| `sparse_time_ticks` | ✓ | ✓ | — | opus-5: Only '2015' and '2022' ticked under a line with eight yearly points；gpt-5.6-sol: Eight annual points span 2015–2022, but only “2015” and “2022” are labelled. |
| `stacked_bar` | ✓ | ✓ | — | opus-5: Magenta, grey and cyan segments inside each brand bar；gpt-5.6-sol: Each brand bar contains magenta, grey, and teal segments. |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: '% Weekly usage' printed under TOP BRANDS, no unit anywhere near the bars；gpt-5.6-sol: The side heading explicitly reads “% Weekly usage”.；gemini-3.1-pro: % Weekly usage is written under the TOP BRANDS subtitle |
| `value_label_inside` | ✓ | ✓ | — | opus-5: '55' in the magenta segment and '26' in the cyan segment of BBC News；gpt-5.6-sol: Trust and Don’t trust numbers are printed inside their coloured segments. |
| `value_label_outside` | ✓ | ✓ | — | opus-5: '64%', '40%', '22%' set to the right of the last plotted points；gpt-5.6-sol: The large “34%” is placed to the right of the sparkline. |
| `wrapped_category_labels` | ✓ | — | — | opus-5: 'Local or regional newspaper', 'Daily Mail/MailOnline' among 15 stacked row labels |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `nested_subset_bar` | opus-5 | 2,3 | Darker tone inside the lighter bar reads as a subset ('More than 3 days per week'), not an additive segment |
| `icon_only_legend` | opus-5 | 3 | Laptop, tablet and smartphone pictograms above the plot are the only key to the three lines |
| `big_number_kpi_callout` | opus-5 | 1,4 | '9% pay for ONLINE NEWS', '25% listen to PODCASTS', '21% SHARE NEWS' set as display numbers with icons |
| `unlabelled_middle_segment` | opus-5 | 2 | Grey 'Neither' segment carries no number while the flanking Trust and Don't trust segments do |
| `prior_year_comparison_in_box` | opus-5 | 1,3 | '20%' with '34% in 2017' beneath it inside a tinted box titled 'Undue political influence' |
| `overlaid_subset_bars` | gpt-5.6-sol | 2,3 | Each dark frequent-use bar overlays a lighter weekly-use total; the printed number names the total. |
| `icon_only_series_labels` | gpt-5.6-sol | 3 | Laptop, tablet, and phone icons above the plot identify three coloured lines without text. |
| `kpi_comparison_cards` | gpt-5.6-sol | 3,4 | Two cards pair an unlabelled current “20%” with “34% in 2017” or “29% in 2017”. |
| `split_table_blocks` | gpt-5.6-sol | 3 | One table is split into side-by-side three-row blocks with duplicated headers. |
| `icon_legend` | gemini-3.1-pro | 3 | laptop, tablet, phone icons act as legend colors |
| `big_number_callout` | gemini-3.1-pro | 1,3 | 34% printed in huge font next to the line |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 50 | BBC News (TV & radio)、Weekly use | TV, RADIO AND PRINT、BBC News (TV & radio)、Weekly use | TV, RADIO AND PRINT、BBC News (TV & radio)、Weekly use | TV, RADIO AND PRINT、BBC News (TV & radio)、Weekly use TV, radio & print | ✓ | ✓ | ✓ | 没过 |
| 18 | Guardian online、Weekly use | ONLINE、Guardian online、Weekly use | ONLINE、Guardian online、Weekly use | ONLINE、Guardian online、Weekly use online brands | ✓ | ✓ | ✓ | 没过 |
| 53% | 2022、TV | SOURCES OF NEWS、TV、2022 | Online (incl. social media)、2022 | TV、2022 | ✓ | ✗ | ✓ | 过 |
| 12 | Sun、Trust | ONLINE、MailOnline、Weekly use | ONLINE、MailOnline、Weekly use | Sun、Trust | ✗ | ✗ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "stacked_bar" | "other · overlaid bars" | "stacked_bar" | stacked_bar | opus 与 gemini 都记 `stacked_bar`（图元数 64 / 60），gpt 记 `other · overlaid bars`——它自己的例子里写的是「subset and total overlap」，说的是同一种画法（一根条里两个深浅），只是读成叠放而不是堆叠。两家一致，按 stacked_bar 判。 |
| `type#f5` | "stacked_bar" | "other · kpi cards" | "stacked_bar" | stacked_bar | opus 与 gemini 的第 5 张都是同一张 45 个图元的堆叠条；gpt 的第 5 张是 4 个数的 KPI 方块，标的不同。按同一标的上的两家一致判。 |
| `type#f6` | "other · ranked data table" | "stacked_bar" | "other · data table" | 不裁 · 三家的第 6 张不是同一张 | opus 的是 0 个图元的排名文字块，gpt 的是 45 个图元的堆叠条，gemini 的是 12 个图元的表。这一页三家从第 5 张起切图就错开了。 |
| `printed#f5` | "some" | "all" | "some" | some | opus 与 gemini 的第 5 张都是同一张 45 个图元的堆叠条，都记 `some`；gpt 的第 5 张是 4 个数的 KPI 方块，是另一个标的。按同一标的上的两家一致判。 |
| `printed#f6` | "all" | "some" | "all" | 不裁 · 三家的第 6 张不是同一张 | opus 的是两个色块里的大字（0 个图元），gpt 的是 45 个图元的堆叠条，gemini 的是 12 个图元的表。这一页三家切出的图从第 5 张起就错开了，第 6 张无共同标的。 |
| `density#f1` | "61–150" | "61–150" | "21–60" | 61–150（按中位数 64 个图元） | 三家数出的图元个数是 64 / 64 / 60，中位数 64，落在 61–150。三个数彼此相差不到一半，分歧是<档的边界>而不是读法：它们看的是同一张图，只是刚好被 20 / 60 / 150 / 400 这几条线切开。 |
| `density#f5` | "21–60" | "≤20" | "21–60" | 不裁 | 不裁 · 切图粒度不同。三家在这一页上切出的图不是同一批：opus 的第 5 张是 8 个点的折线，gpt 的是 4 个数的 KPI 方块，gemini 的是 45 个图元的堆叠条。三个数描述的是三样东西，没有共同的标的可裁。 |
| `density#f6` | "未报" | "21–60" | "≤20" | 不裁 | 不裁 · 同上。opus 把第 6 块记成 `unreadable`（两个色块里的大字，0 个图元），gpt 记成 45 个图元的堆叠条，gemini 记成 12 个图元的表。仍然不是同一个标的。 |
| `hardest_step` | 3 | 3 | 2 | 3 | 以实测为准：4 个点只过 2 个，两个失败都是 label_unlinked，`weekly use` 只出现在正文里、没进任何表（第三步）。opus 与 gpt 报 3，都命中；gemini 报 2。 |
| `value_axes#f5` | 1 | 0 | 1 | 1 | opus 与 gemini 的第 5 张是同一张堆叠条，都记「底边一条值轴」；gpt 的第 5 张是 KPI 方块，标的不同。 |
| `value_axes#f6` | 0 | 1 | 0 | 不裁 · 三家的第 6 张不是同一张 | 与这一页的 `printed#f6` 同因。 |
| `key_roles#f4` | ["panel", "time"] | ["time"] | ["time"] | time | gpt 与 gemini 一致。opus 记的 panel 来自这张图自己的标题（`Change over time 2015-…`），这一张只有一个绘图区。<strong>panel 的判据</strong>：要有自己的绘图区，而且名字要印在页面上。`label_source` 是 `not_shown` 的段进不了键——键必须逐字可复制。 |
| `key_roles#f5` | ["category", "series"] | ["panel", "time"] | ["category", "series"] | category × series | opus 与 gemini 的第 5 张是同一张堆叠条，两家一致；gpt 的第 5 张是 KPI 方块，标的不同。 |
