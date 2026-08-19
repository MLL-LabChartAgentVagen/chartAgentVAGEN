# 2024_healthatglance_rep_en_p45

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2024_healthatglance_rep_en | `need_estimate` | 10 | 10 |

该页为《Health at a Glance: Europe 2024》第43页，含正文与一张折线图 Figure 1.18，展示2012–2022年5个EU国家65岁及以上医生占比。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 27 | `2022` · `Italy` | 5% | f1 | the Italy point at 2022 (top end of the dark navy line, ~26.6 on the axis) | 否 | `Italy` · `2022` · `Share of doctors aged 65 and over` |
| 2 | 7 | `2012` · `Italy` | 5% | f1 | the Germany point at 2022 (lowest line, just above 7) | 否 | `Germany` · `2022` · `Share of doctors aged 65 and over` |
| 3 | 21 | `2022` · `Belgium` | 5% | f1 | the Italy point at 2019, where the navy line has just crossed 20 | 否 | `Italy` · `2019` · `Share of doctors aged 65 and over` |
| 4 | 14 | `2012` · `Belgium` | 5% | f1 | the Belgium point at 2012, the start of the medium-blue line just below 14 | 否 | `Belgium` · `2012` · `Share of doctors aged 65 and over` |
| 5 | 19 | `2022` · `France` | 5% | f1 | the France point at 2022 (light blue line ending just under 19) | 否 | `France` · `2022` · `Share of doctors aged 65 and over` |
| 6 | 11 | `2012` · `France` | 5% | f1 | the Italy point at 2015, where the navy line reaches about 10.5 | 否 | `Italy` · `2015` · `Share of doctors aged 65 and over` |
| 7 | 17 | `2022` · `Slovak Republic` | 5% | f1 | the Slovak Republic point at 2022 (mauve line ending just above 17) | 否 | `Slovak Republic` · `2022` · `Share of doctors aged 65 and over` |
| 8 | 8 | `2012` · `Slovak Republic` | 5% | f1 | the Slovak Republic point at 2012, start of the mauve line at about 8 | 否 | `Slovak Republic` · `2012` · `Share of doctors aged 65 and over` |
| 9 | 8 | `2022` · `Germany` | 5% | f1 | the Italy point at 2013, where the navy line rises to about 8 | 否 | `Italy` · `2013` · `Share of doctors aged 65 and over` |
| 10 | 4 | `2012` · `Germany` | 5% | f1 | the Germany point at 2012, start of the cyan line just above 4 | 否 | `Germany` · `2012` · `Share of doctors aged 65 and over` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: 7, 21, 11, 8

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 5 | 11 | 55 | 无 | 0, 5, 10, 15, 20, 25, 30 |

- **f1** Figure 1.18. / The share of doctors aged 65 and over has increased over the past decade in several EU countries　[图上方]　单位 `Share of doctors aged 65 and over`
  - 来源行：Source: Eurostat (hlth_rs_phys).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: Eurostat (hlth_rs_phys)." in small print under the plot |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | "StatLink" glyph with "https://stat.link/k5rgpc" printed below the source line |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis ticks are bare 0-30; "Share of doctors aged 65 and over" is the only scale phrase |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "Share of doctors aged 65 and over" sits above the top tick "30", left aligned |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | f1 | **无** | no legend; "Italy", "Belgium", "France", "Slovak Republic", "Germany" printed at the right end of each line |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the plot area is filled light grey while the page around it is white |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | pale horizontal rules run across the grey panel at 5, 10, 15, 20, 25 |

词表 65 项，本页出现 7 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `series_label_gutter_outside_plot` | f1 | the five series names sit in a right-hand margin outside the grey panel, level with each line end | 标签在绘图区之外的右侧留白列，读值时必须把标签水平投射回2022年端点，而不是在曲线旁就近取名。 |
| `empty_trailing_category_slot` | f1 | a lone "." is printed on the x axis to the right of the "2022" tick label | 轴上多出一个空类别位，使2022不是最右端点，按像素等分推年份会整体偏移一格。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，55个点全靠像素对轴读取；轴每5单位约57像素，即1单位≈11像素。对27这样的大值5%容差=1.35单位（约15像素）尚可，但被计分的4和7两个小值，5%仅0.2和0.35单位，合2–4像素，比线宽还窄，且Germany与Slovak Republic起点在同一区域，几乎无法稳定落在容差内。相比之下寻址只需“国家+年份”两个键，正文还直接写出Italy 27%，标签层面压力小得多。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P3 | 一类出版方 | inline_series_labels 与新提出的 series_label_gutter_outside_plot（端点标签置于绘图区右侧留白） | 折线图样式条件行中新增“图例位置=端点标签/右侧留白”，并在记录字段里保留 series 名与其端点年份的绑定 | “无图例、仅端点标签” vs “底部图例”下的系列-取值配对准确率对比行 |
| P7 | 一类出版方 | axis_title_above_axis 配合 unit_in_axis_or_title（“Share of doctors aged 65 and over”置于顶端刻度之上） | 标题/单位样式字段：单位文本位置枚举增加 above_top_tick，与 subtitle、rotated 轴标题并列 | 单位置于顶端刻度上方 vs 置于旋转轴标题时，导出表头能否带上单位的成功率行 |
| P6 | 这份文档自己的习惯 | 新组件 empty_trailing_category_slot（2022右侧多出的“.”刻度位） | 时间轴生成条件行：允许尾部存在空类别槽/占位刻度标签 | 轴末尾存在空槽时，年份↔取值对齐错位一格的发生率行 |
| P1 | 通用 | dense_marks_100plus 的下探版本：5系列×11年=55个无标签点的密度控制 | 密度上限参数改为可控变量，并按“每单位轴长像素”给出可达精度 | 每单位11像素、无数值标签时，按数值量级（<5、5–15、>20）分层的5%命中率行 |
