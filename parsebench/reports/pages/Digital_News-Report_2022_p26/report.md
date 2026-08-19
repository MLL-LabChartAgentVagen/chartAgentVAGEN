# Digital_News-Report_2022_p26

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Digital_News-Report_2022 | `untagged` | 3 | 0 |

路透新闻研究所《Digital News Report 2022》第26页，左栏为英国各平台

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 21% | `Facebook` · `Too much` | 1% | f1 | the Facebook 'Too much' top segment | 是 | `PROPORTION WHO THINK THEY SEE TOO MUCH NEWS ON EACH NETWORK – UK` · `Facebook` · `Too much` |
| 2 | 49% | `Politics` · `Africa` | 1% | f3 | the Africa bar in the Politics group | 是 | `PROPORTION WHO SAW FALSE OR MISLEADING INFORMATION ABOUT EACH TOPIC IN THE LAST WEEK – SELECTED REGIONS` · `Politics` · `Africa` |
| 3 | 9% | `Immigration` · `Asia` | 1% | f3 | the Asia bar in the Immigration group | 是 | `PROPORTION WHO SAW FALSE OR MISLEADING INFORMATION ABOUT EACH TOPIC IN THE LAST WEEK – SELECTED REGIONS` · `Immigration` · `Asia` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——3 values given, 4 answered

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 4 | 4 | 16 | 全部 | （不画值轴） |
| f2 | `other · ranked value table` | na | 2 | 1 | 10 | 10 | 全部 | （不画值轴） |
| f3 | `grouped_bar` | horizontal | 1 | 5 | 6 | 30 | 全部 | （不画值轴） |

- **f1** PROPORTION WHO THINK THEY SEE TOO MUCH NEWS ON EACH NETWORK – UK　[图上方]　（标题里没有单位）
  - 来源行：Q12_Social_rightsize ... Do you think that the amount of content you see from news outlets on <social network>. is too much, about right, or not enough? Base: All that use each social network: Facebook = 1501, Twitter = 685, Instagram = 859, TikTok = 270.
- **f2** Top markets saying too much　[图上方]　（标题里没有单位）
- **f3** PROPORTION WHO SAW FALSE OR MISLEADING INFORMATION ABOUT EACH TOPIC IN THE LAST WEEK – SELECTED REGIONS　[图上方]　（标题里没有单位）
  - 来源行：Q. FAKE_NEWS 2021a. Have you seen false or misleading information about any of the following topics, in the last week? Base: Total sample in each region: Europe = 48,836, North America = 4048, Asia = 20,349, Latin America = 12,104, Africa = 6057. Note: Africa average is Kenya, South Africa, and Nigeria only (English speakers in South Africa and Nigeria).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f3 | 有 | five regional bars sit side by side within each topic slot |
| `stacked_bar` | 堆叠条 | f1 | 有 | each platform bar stacks Too much / About right / Not enough / Don't know segments |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f1 | **无** | segments 21+55+3+20 and 11+73+3+13 each fill one full-height bar |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f3 | **无** | topics on the left axis, bars grow rightwards |
| `no_value_axis` | 没有值轴刻度，只有基线 | f3 | **无** | no ticks anywhere; only printed labels like '47%', '53%' give values |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only platform names under bars, no percentage scale drawn |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately captioned charts plus the 'Top markets' table on one page |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Q12_Social_rightsize ... Base: All that use each social network' small print below |
| `source_note_lines` | source / note 行在图下方 | f3 | 有 | 'Q. FAKE_NEWS 2021a. ... Note: Africa average is Kenya, South Africa, and Nigeria only' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Too much About right Not enough Don't know' swatch row under the platform icons |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f2 | 有 | bordered rows of market names with '23%', '26%' captioned 'Top markets saying too much' |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f3 | 有 | 'Europe North America Asia Latin America Africa' row between title and plot |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f2 | 有 | the boxed 'Top markets saying too much' column sits right of the stacked bars |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f2 | 有 | 'Twitter' and 'Facebook' banner rows with logos head each block of markets |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | body columns of prose run above and below the figures in the same two-column band |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | superscript 9 and 10 in body text with notes at page foot |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | '21%', '55%', '20%' printed on the segments themselves |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f3 | **无** | '47%', '54%' sit at bar ends inside the grey track beyond the coloured bar |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | '3%' labels squeezed in narrow Not enough segments of Facebook and Twitter |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f3 | **无** | 'Climate change' and 'Products (e.g. scams)' wrap onto two lines |
| `panel_background` | 绘图区带底色，不是白底 | f3 | **无** | each bar sits in a light grey full-width track behind it |
| `icon_category_axis` | 类目轴用图标代替文字 | f1 | **无** | Facebook, Twitter, Instagram, TikTok logos drawn under the category names |
| `icon_category_axis` | 类目轴用图标代替文字 | f2 | **无** | country flag icons stand beside each market name in the table rows |

词表 65 项，本页出现 20 项，其中我们画不出来的 10 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `bar_track_background` | f3 | every bar drawn inside a light grey full-length track ending at the plot right edge | 灰色轨道看似满值参考条，读数时须以彩色部分末端而非轨道长度为准，否则会误判比例。 |
| `repeated_category_across_panels` | f2 | 'Australia' appears once under Twitter (23%) and again under Facebook (20%) | 同名行出现两次，必须用所属平台分组名一起定位，否则23%与20%无法区分。 |
| `value_axis_absent_full_scale_stack` | f1 | stacks reach one common top with no 0–100% axis printed anywhere | 百分比只能靠标注文字读取，无法从像素高度校验，缺标注段即不可读。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

三张图的数字都直接印在图上，读数不成问题（无刻度轴反而使像素读取无从下手，但标注齐全）。真正的障碍是定位：f3的每个值需要

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 bar_track_background（灰色满长轨道背景） | 样式条件行中新增 |  |
| P2 | 一类出版方 | 新组件 repeated_category_across_panels（同名类别在不同分组中重复） | 记录字段需加入 panel_key，使 (panel, category) 共同构成主键 | 加入 |
| P1 | 一类出版方 | no_value_axis 与 value_label_inside/outside 组合（无刻度、全靠标注） | 样式字段中的 value-label placement 与 axis 绘制开关联动 | 新增 |
| P7 | 通用 | P7 的标题拆分：无编号、全大写多行标题、单位缺失（只有'%'在数值里） | 图题记录字段 figure_number 允许为空、title 支持多行换行 | 增加 |
