# ADL_Future_of_automotive_mobility_2024_1_p25

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ADL_Future_of_automotive_mobility_2024_1 | `untagged` | 10 | 0 |

该页含两幅并列的横向分组条形图（图17按8个地区分面、图18全球外中国原因排序）以及下方关于中国电动车品牌忠诚度的正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 51 | `Poor quality` · `EV or hybrid owners` | 5% | f2 | the 'Poor quality' bar for 'EV or hybrid owners' (51%) | 是 | `Poor quality` · `EV or hybrid owners` |
| 2 | 53 | `Poor quality` · `Conventional powertrain owners a) EV intenders` | 5% | f2 | the 'Poor quality' bar for 'Conventional powertrain owners a) EV intenders' (53%) | 是 | `Poor quality` · `Conventional powertrain owners a) EV intenders` |
| 3 | 40 | `Poor quality` · `Conventional powertrain owners b) EV non-intenders` | 5% | f2 | the 'Poor quality' bar for 'Conventional powertrain owners b) EV non-intenders' (40%) | 是 | `Poor quality` · `Conventional powertrain owners b) EV non-intenders` |
| 4 | 45 | `Challenges associated with service or purchase` · `EV or hybrid owners` | 5% | f2 | the 'Challenges associated with service or purchase' bar for 'EV or hybrid owners' (45%) | 是 | `Challenges associated with service or purchase` · `EV or hybrid owners` |
| 5 | 38 | `Brand reputation` · `EV or hybrid owners` | 5% | f2 | the 'Brand reputation' bar for 'EV or hybrid owners' (38%); 38% also occurs as 'Challenges...' EV non-intenders | 是 | `Brand reputation` · `EV or hybrid owners` |
| 6 | 42 | `Brand reputation` · `Conventional powertrain owners a) EV intenders` | 5% | f2 | the 'Brand reputation' bar for 'Conventional powertrain owners a) EV intenders' (42%) | 是 | `Brand reputation` · `Conventional powertrain owners a) EV intenders` |
| 7 | 37 | `Preference for domestic brands` · `EV or hybrid owners` | 5% | f2 | the 'Preference for domestic brands' bar for 'EV or hybrid owners' (37%) | 是 | `Preference for domestic brands` · `EV or hybrid owners` |
| 8 | 40 | `Preference for domestic brands` · `Conventional powertrain owners a) EV intenders` | 5% | f2 | the 'Preference for domestic brands' bar for 'Conventional powertrain owners a) EV intenders' (40%) | 是 | `Preference for domestic brands` · `Conventional powertrain owners a) EV intenders` |
| 9 | 22 | `Environmental, social & governance standards` · `EV or hybrid owners` | 5% | f2 | the 'Environmental, social & governance standards' bar for 'EV or hybrid owners' (22%) | 是 | `Environmental, social & governance standards` · `EV or hybrid owners` |
| 10 | 22 | `Vehicle design` · `EV or hybrid owners` | 5% | f2 | the 'Vehicle design' bar for 'EV or hybrid owners' (22%) | 是 | `Vehicle design` · `EV or hybrid owners` |

**程序核对**（模型没有看到左半的标签列）：

- 面板数与面板名个数不一致——f1: panels=8, 0 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | horizontal | 8 | 3 | 4 | 96 | 全部 | （不画值轴） |
| f2 | `grouped_bar` | horizontal | 1 | 3 | 6 | 18 | 全部 | （不画值轴） |

- **f1** Figure 17 / Factors encouraging EV purchase / What factors would encourage you to purchase an electric car?　[图上方]　单位 `(in %)`
  - 来源行：Source: Arthur D. Little
- **f2** Figure 18 / Reasons for not purchasing a Chinese EV / Why would you not be interested in purchasing an EV from a Chinese manufacturer?　[图上方]　（标题里没有单位）
  - 来源行：Source: Arthur D. Little

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | three bars (navy, blue, light blue) side by side in each row such as 'Environment' 76/76/71 |
| `grouped_bar` | 分组条 | f2 | 有 | 'Poor quality' row carries three bars labelled 51%, 53%, 40% |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | row labels 'Environment', 'Price' at left, bars grow rightwards from a vertical baseline |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f2 | **无** | 'Vehicle design', 'Brand reputation' on the y side, bars extend right |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f2 | **无** | tinted box right of the bars: 'GLOBAL OUTSIDE CHINA – 60% of respondents would not be interested...' |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only thin vertical baselines per panel; no tick labels anywhere for the bar lengths |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | a single vertical baseline at the left of the bars, no ticks or grid |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one legend row under all eight panels: 'EV or hybrid owners', 'Conventional powertrain owners a) EV intenders'... |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f1 | **无** | eight identical four-row bar panels repeated across icon-headed columns |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | 'Figure 17. Factors encouraging EV purchase' and 'Figure 18. Reasons for not purchasing a Chinese EV' |
| `source_note_lines` | source / note 行在图下方 | page | 有 | 'Source: Arthur D. Little' printed under each of the two figures |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend keys sit below the panel band, above 'Source: Arthur D. Little' |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f2 | 有 | three legend entries stacked in a right-hand column level with the lower bars |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | heading line '(in %)' under 'What factors would encourage you to purchase an electric car?' |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | numbers 76, 76, 71 printed to the right of each bar end, outside the fill |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | '51%', '53%', '40%' printed beyond each bar's right end |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 'More fun to drive than ICE cars (acceleration)' wraps onto three lines in its label box |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f2 | **无** | 'Challenges associated with service or purchase' wraps onto two right-aligned lines |
| `icon_category_axis` | 类目轴用图标代替文字 | f1 | **无** | small pictograms printed inside each row label box beside 'Environment', 'Price', 'Trend & technology front-runner' |

词表 65 项，本页出现 14 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `icon_panel_headers` | f1 | each of the eight panels is identified only by a circular globe or flag icon above it, no text | 面板维度没有任何文字键，读某一数值必须先把图标翻译成地区名，表格无法逐字引用面板名。 |
| `dashed_outline_highlights_panel` | f1 | a dashed blue rectangle encloses the first (globe) panel's four rows of bars | 虚线框把全球面板标为参照对象，读数时需知道该列是汇总口径而非某地区。 |
| `emphasised_value_labels_in_colour` | f1 | labels like '46 56 36', '53 53 37', '27 20 15', '52' set in bold red instead of grey | 同一图内数值标签有两种字体/颜色，解析时红色粗体值可能被当作强调文本而与所属条错配。 |
| `percent_sign_in_value_labels` | f2 | every label carries the unit itself: '51%', '47%', '19%'; no unit line in the heading | 图18没有单位副标题，单位只存在于标签内，抽表时数值须连百分号一起匹配。 |
| `category_labels_in_filled_boxes` | f1 | 'Environment', 'Price' etc. sit in dark navy filled label boxes at the left of the panel band | 行名以色块承载而非普通轴文本，解析器可能把它当图形而丢掉行键。 |
| `icon_identifies_data_scope` | f2 | a globe icon sits at the right of the heading line, matching figure 17's first panel icon | 整图口径（全球）只由图标表示，读数时的范围限定词不在文字中。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身不难：图18所有18个条都印有'51%'…'16%'，无需按轴读像素（两图都没有值轴）。真正卡住的是定址：22%、38%、40%、19%、30%在图18内各出现两次，因此每个值必须同时带上行名（最长的是'Challenges associated with service or purchase'，且在图上折成两行）和很长的系列名'Conventional powertrain owners b) EV non-intenders'——三个系列名前缀相同，仅靠'a)'/'b)'区分，解析器若把折行行名截断或把系列名压缩成'a)'，一行表就无法唯一指向某个值。图17更极端：面板只有图标，96个标签在markdown里连一个可引用的面板键都没有。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | icon_panel_headers（新组件）：面板标识仅为图标、无文字面板名 | 面板条件行增加'panel_label_modality = icon\|text'，记录字段中panel_key允许为空并给出图标语义别名 | 图标面板 vs 文字面板：当panel_key不可逐字引用时，值-标签匹配命中率的变化 |
| P6 | 这份文档自己的习惯 | emphasised_value_labels_in_colour（新组件）：同图内部分数值标签用红色粗体 | 样式字段value_label_style新增per_mark_emphasis（颜色/字重按阈值切换） | 标签统一样式 vs 部分标签加粗变色：抽取时标签与条的绑定错配率 |
| P6 | 通用 | percent_sign_in_value_labels（新组件）与unit_in_axis_or_title的对照 | 单位位置维度增加'unit_in_each_value_label'一档，与'(in %)'副标题档并列 | 单位在副标题 vs 单位随每个标签：数值字符串匹配（38 与 38%）的成功率 |
| P3 | 一类出版方 | legend_beside_plot 与长系列名（'Conventional powertrain owners a) EV intenders'）组合 | 图例布局条件行加入beside档，并允许系列名长度>30字符含'a)'/'b)'区分符 | 短系列名 vs 共前缀长系列名：唯一定址所需键数与错配率 |
| P1 | 通用 | no_value_axis + 全标签（两图均无刻度，只有基线） | readable判定改为按标签可得性给出per-mark精度，而非依赖是否存在值轴 | 有值轴无标签 vs 无值轴全标签：每个mark可达精度分布 |
