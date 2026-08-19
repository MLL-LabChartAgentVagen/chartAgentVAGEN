# Digital_News-Report_2022_p24

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Digital_News-Report_2022 | `untagged` | 4 | 0 |

这是路透研究院《数字新闻报告2022》第24页，两栏正文之间嵌有三幅无编号的折线图，分别展示英国按年龄的新闻起点比例、英国18–24岁社交网络使用率，以及12国平均各社交网络新闻使用率。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 28% | `2022` · `18-24` | 1% | f1 | the 2022 endpoint of the 18-24 (turquoise) line | 是 | `PROPORTION WHO START THEIR NEWS JOURNEY WITH A NEWS WEBSITE OR APP – BY AGE – UK` · `18-24` · `2022` |
| 2 | 61% | `2022` · `YouTube` | 1% | f3 | the 2022 endpoint of the YouTube line | 是 | `PROPORTION THAT USED EACH SOCIAL NETWORK FOR ANY PURPOSE IN THE LAST WEEK (2014-22) – AVERAGE OF 12 MARKETS` · `YouTube` · `2022` |
| 3 | 68% | `2022` · `Instagram` | 1% | f2 | the 2022 endpoint of the Instagram line | 是 | `PROPORTION OF 18–24s (SOCIAL NATIVES) WHO USED EACH SOCIAL NETWORK FOR ANY PURPOSE IN THE LAST WEEK (2014–22) – UK` · `Instagram` · `2022` |
| 4 | 30% | `2022` · `Facebook` | 1% | f4 | the 2022 endpoint of the Facebook line | 是 | `PROPORTION THAT USED EACH SOCIAL NETWORK FOR NEWS IN THE LAST WEEK (2014-22) – AVERAGE OF 12 MARKETS` · `Facebook` · `2022` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——4 values given, 5 answered
- 标了 dense_marks_100plus，但没有图达到 100 个图元——dense_marks_100plus claimed, densest figure has 73 marks
- 系列数与系列名个数不一致——f4: series=9, 8 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 3 | 8 | 24 | 部分 | 0%, 25%, 50%, 75%, 100% |
| f2 | `line` | vertical | 1 | 4 | 9 | 32 | 部分 | 0%, 25%, 50%, 75%, 100% |
| f3 | `line` | vertical | 1 | 9 | 9 | 73 | 部分 | 0%, 25%, 50%, 75% |
| f4 | `line` | vertical | 1 | 9 | 9 | 73 | 部分 | 0%, 25%, 50% |

- **f1** PROPORTION WHO START THEIR NEWS JOURNEY WITH A NEWS WEBSITE OR APP – BY AGE – UK　[图上方]　（标题里没有单位）
- **f2** PROPORTION OF 18–24s (SOCIAL NATIVES) WHO USED EACH SOCIAL NETWORK FOR ANY PURPOSE IN THE LAST WEEK (2014–22) – UK　[图上方]　（标题里没有单位）
- **f3** PROPORTION THAT USED EACH SOCIAL NETWORK FOR ANY PURPOSE IN THE LAST WEEK (2014-22) – AVERAGE OF 12 MARKETS　[图上方]　（标题里没有单位）
- **f4** PROPORTION THAT USED EACH SOCIAL NETWORK FOR NEWS IN THE LAST WEEK (2014-22) – AVERAGE OF 12 MARKETS　[图上方]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f2 | **无** | boxed note "18-24 cliff edge started in 2018 which is when Instagram started to take over" with leader |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | "Coronavirus" virus icon over shaded band; "Gap opening up between 18-24s and the rest" |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | grey vertical band spanning 2020–2021 labelled "Coronavirus" |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | four separate unnumbered line charts, each with its own heading and Q10/Q12a/Q12b note |
| `source_note_lines` | source / note 行在图下方 | page | 有 | "Q10. Thinking about how you got news online ... Base: 2018–22; 18–24 ≈ 200" under each chart |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | "18-24  25-34  35+" swatches drawn inside the plot at the top left |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f2 | 有 | Facebook / Instagram / TikTok / WhatsApp swatch row between title and plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f3 | 有 | two rows of nine swatches sit between the heading and the plot area |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f4 | 有 | two-row legend Facebook ... TikTok between heading and plot |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | two-column body text runs beside and between the charts across one horizontal band |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | "Elon Musk8" superscript 8 with footnote URL at the page foot |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | "53% 52% 52%" at line starts and "49% 45% 28%" beyond the line ends |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | "78%", "20% 17%", "4%" and end labels "68% 62% 51% 32%" right of the lines |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f3 | **无** | "60% 53% 19% 17% 8% 5% 2%" at starts, "61% 60% 51% 40% 34% 21% 16% 12% 11%" at ends |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f4 | **无** | "36% 16% 9% 7% 2% 1%" at line starts and "30% 19% 15% 12% 11% 7% 4% 2%" at ends |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | f2 | **无** | brand icons (Instagram, WhatsApp, Facebook, TikTok) placed at the right end of each line |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 25%, 50%, 75%, 100%; no vertical rules |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | horizontal rules at each 25% tick, no vertical grid lines |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | page | **无** | four line charts with 9 years and up to 9 series each, roughly 200 plotted points total |
| `icon_category_axis` | 类目轴用图标代替文字 | f3 | **无** | YouTube, Facebook, WhatsApp, Instagram, Messenger, Twitter, TikTok, Snapchat logos at line endpoints |

词表 65 项，本页出现 13 项，其中我们画不出来的 9 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `brand_icon_series_key` | f3 | line endpoints carry platform logos (YouTube, Facebook, Instagram, Snapchat) instead of text labels | 要把末端数值（如61%、40%）对应到某个系列，必须识别图标而非文字，表格化时系列名可能丢失。 |
| `endpoint_and_startpoint_value_labels` | f4 | only first-year and last-year values printed ("36%" 2014, "30%" 2022); middle years bare | 中间年份只能靠像素读取，只有首末年份可直接取值，行键需含年份才能唯一定位。 |
| `question_id_note_line` | page | notes begin with bold "Q10.", "Q12a.", "Q12b." rather than "Source:" | 没有Source行，问卷题号与Base是唯一的来源信息，抽取时需当作source/note处理。 |

## 5 · 难在哪

卡在 **第四步 · 表外上下文**。

四个被评分的数字都印在线端（28%、61%、68%、30%），读数本身不难；难点在于四幅图都没有编号，标题是全大写的长句且分两三行折行，而61%与30%分别属于两张同样以"AVERAGE OF 12 MARKETS"结尾的图，仅靠系列名YouTube/Facebook与年份2022无法区分"FOR ANY PURPOSE"与"FOR NEWS"两图。若解析器不把这段折行标题作为粗体标题或表头输出，30%与19%等值就会落到错误的图上；同时f3中12%、11%、16%等标签在3–4像素间距内堆叠，也增加了系列归属的混淆。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 一类出版方 | unit_in_axis_or_title 与 no_value_axis 的替代：把无编号但多行大写标题（number为空、title折行）作为独立字段导出 | 记录字段的heading结构：figure_number允许为空，title保留折行原文，placement=above | 新增一行"无编号+多行标题"：对比有编号与无编号时值-标题配对准确率 |
| new | 这份文档自己的习惯 | 新组件 brand_icon_series_key（图标代替系列文字） | 样式条件行：系列末端标记形式（文本标签/图标/无） | 新增一行"系列以图标标识"：测量系列名可恢复率 |
| P6 | 一类出版方 | 新组件 endpoint_and_startpoint_value_labels（仅首末点标数值） | value-label placement 样式维度，增加"仅端点"取值 | 新增一行"仅端点标注 vs 全部标注"：中间年份读数误差分布 |
| P5 | 通用 | dense_marks_100plus 与拥挤端点标签（f3九系列、约73点，末端标签间距不足） | 密度上限参数：单图系列数上调至9并允许标签碰撞 | 新增一行"系列数≥8的折线图"：标签-系列错配率随密度变化 |
| new | 一类出版方 | annotation_callout + shaded_band（"Coronavirus"灰带与箭注框） | 条件行中加入注释层开关（带状阴影/带引线文本框） | 新增一行"含注释层"：注释文本被误当数据的比例 |
