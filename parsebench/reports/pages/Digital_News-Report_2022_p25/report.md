# Digital_News-Report_2022_p25

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Digital_News-Report_2022 | `untagged` | 3 | 0 |

本页顶部是一张按五个地区分列的社交网络新闻使用比例横向条形矩阵图，下方为正文、TikTok 手机截图配两个环形指标（40%/15%）以及一个市场排行小表格。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 57% | `Facebook` · `Latin America` | 1% | f1 | the Facebook bar in the Latin America column | 是 | `Latin America` · `Facebook` |
| 2 | 44% | `YouTube` · `Africa` | 1% | f1 | the YouTube bar in the Africa column | 是 | `Africa` · `YouTube` |
| 3 | 24% | `WhatsApp` · `Asia` | 1% | f1 | the WhatsApp bar in the Asia column | 是 | `Asia` · `WhatsApp` |

**程序核对**（模型没有看到左半的标签列）：

- 面板数与面板名个数不一致——f3: panels=2, 0 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | horizontal | 5 | 1 | 8 | 40 | 全部 | （不画值轴） |
| f2 | `donut` | na | 2 | 1 | 1 | 4 | 全部 | （不画值轴） |
| f3 | `other · labelled data table` | na | 2 | 2 | 6 | 12 | 全部 | （不画值轴） |

- **f1** PROPORTION THAT USED EACH SOCIAL NETWORK FOR NEWS IN THE LAST WEEK – SELECTED REGIONS　[图上方]　（标题里没有单位）
- **f2** （无标题）　[无标题]　（标题里没有单位）
- **f3** Markets with highest usage (all ages)　[图上方]　单位 `% for any purpose/for news`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | network names on the left, bars grow rightwards inside grey tracks |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f2 | **无** | `(Across all markets)` note beneath the two donut rings |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or gridlines; only printed labels like `40%`, `57%` give values |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | one shared row of category names (Facebook...TikTok) at left for all five columns |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f1 | **无** | five side-by-side region columns: Europe, North America, Asia, Latin America, Africa |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | regional bar matrix at top, donut pair mid-right, market usage table below it |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Q12B. Which, if any, of the following...` and `Note: Africa average is Kenya, South Africa, and Nigeria only` |
| `source_note_lines` | source / note 行在图下方 | f3 | 有 | `Q12a/b. Which, if any, ... Base: Total sample in each market (n = 2000).` |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f3 | 有 | bordered two-column table of flags, market names and `43%/15%` values under a caption |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f3 | 有 | colour-coded `% for any purpose/for news` sits above the table rows |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | coloured headers `Europe`, `North America`, `Asia`, `Latin America`, `Africa` above each column |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f2 | **无** | left column body text runs level with the TikTok phone image and donut figures |
| `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | f3 | **无** | heading reads `% for any purpose/for news` in the two matching series colours |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | `40%` and `15%` printed at the centre of each donut ring |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | percentages printed just right of each coloured bar end, on the grey track |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | each bar sits in a light grey full-width track behind the coloured bar |
| `icon_category_axis` | 类目轴用图标代替文字 | f1 | **无** | Facebook, YouTube, WhatsApp etc. brand logos precede each row label |
| `icon_category_axis` | 类目轴用图标代替文字 | f3 | **无** | national flag pictograms precede Kenya, Thailand, South Africa, Peru, Mexico |

词表 65 项，本页出现 16 项，其中我们画不出来的 9 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `row_track_full_scale` | f1 | each grey track is a fixed full-length 100% frame with the coloured bar inside it | 读数只能靠印出的百分比或与灰色满格轨道的长度比，缺少刻度会让像素估值误差放大。 |
| `panel_color_encodes_panel` | f1 | each region column uses its own single colour matching its header text colour | 颜色不是系列而是面板标识，表格行必须用地区名而非颜色来定位数值。 |
| `donut_progress_indicator` | f2 | single-value ring with big centre percentage and a caption sentence beside it | 这类单值环图没有类别轴，值只能来自中心数字，行标签需由旁边说明句提供。 |
| `paired_values_in_one_cell` | f3 | table cell prints `43%/15%` as two coloured numbers separated by a slash | 一个单元格含两个不同系列的值，解析时必须拆分斜杠才能各自定位。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

三个值都以文字印在条形旁，读数本身没有难度（步骤2可忽略）；真正的障碍是定位：f1 是 8 行 × 5 个地区列的矩阵，44% 只出现在 Africa 列的 YouTube 行，而 Africa 的 Facebook 是 59%、Twitter 是 34%，若解析器把五列拼成一行或丢掉列头，44% 与 24% 这类两位数在同页还会与 f3 的 `42%/22%`、`43%/15%` 混淆。因此每个值至少需要「地区列名 + 网络行名」两个键，而列头是彩色文字而非表头单元，最易在 markdown 中丢失。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | panel_title_per_panel 与 shared_axis 组合（面板维度进入键） | 记录字段增加 panel_key，把 Europe/North America/Asia/Latin America/Africa 作为列头写入表格首行 | 有/无 panel_key 时，多面板矩阵图数值定位准确率对比 |
| P6 | 一类出版方 | no_value_axis + value_label_outside 的组合样式 | 样式字段：允许关闭值轴，仅以印在灰色轨道内的数字标签承载数值 | 无值轴仅靠标签读数 vs 有刻度轴时的每标记精度 |
| new | 这份文档自己的习惯 | 新组件 paired_values_in_one_cell（`43%/15%` 斜杠双值） | data_table_as_figure 的单元格渲染条件行，以及系列名带单位的表头 | 单元格含两系列斜杠值时，拆分为两条记录的成功率 |
| P4 | 一类出版方 | 新组件 donut_progress_indicator（单值环图 + 旁注说明） | 图表家族权重向量中加入单值环形指标，并在标题字段中容纳说明句作为行名 | 单值指标图（无类别轴）在生成频次为 0 与非 0 时的抽取覆盖率 |
| P7 | 一类出版方 | unit_in_series_name（`% for any purpose/for news`）与无编号标题 | 标题结构字段：figure_number 可为空，unit_text 与彩色系列名同处一行 | 无编号图 + 单位写在系列名中时，标题/单位归属判定正确率 |
