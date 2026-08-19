# (Web_version)_E-Government_Survey_2024_1392024_p79

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| (Web_version)_E-Government_Survey_2024_1392024 | `untagged` | 4 | 0 |

本页为《2024 UN E-Government Survey》第54页，含两个编号图（图2.11 立法框架半圆扇形图＋五大区域横向条形小多图；图2.12 国家门户内容提供的全球与区域横向条形图）以及2.5.4小节正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 48% | `Africa (54 countries)` · `Open government data` | 1% | f1 | the Africa (54 countries) "Open government data" bar; the Asia (47 countries) "Cloud" bar also reads 48% | 是 | `Figure 2.11` · `Africa (54 countries)` · `Open government data` |
| 2 | 30% | `Africa` · `Availability of web statistics on usage` | 1% | f2 | the Africa "Availability of web statistics on usage" bar in the regional row | 是 | `Figure 2.12` · `Africa` · `Availability of web statistics on usage` |
| 3 | 100% | `Asia` · `Availability of content in more than one official language of the country` | 1% | f2 | the Asia "Availability of content in more than one official language of the country" bar; Europe reads 100% too | 是 | `Figure 2.12` · `Asia` · `Availability of content in more than one official language of the country` |
| 4 | 98% | `Europe` · `Information provided about the results of government procurement or bidding online` | 1% | f2 | the Europe "Information provided about the results of government procurement or bidding online" bar | 是 | `Figure 2.12` · `Europe` · `Information provided about the results of government procurement or bidding online` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | horizontal | 6 | 1 | 12 | 37 | 全部 | （不画值轴） |
| f2 | `bar` | horizontal | 6 | 1 | 4 | 24 | 全部 | （不画值轴） |

- **f1** Figure 2.11 / Percentage of countries with legislative frameworks relevant to e-government development, 2024　[图上方]　单位 `Percentage of countries with specific legislation`
  - 来源行：Source: 2024 United Nations E-Government Survey.
- **f2** Figure 2.12 / Content provision on national portals, 2024 / (Percentage of countries, by region)　[图上方]　单位 `(Percentage of countries, by region)`
  - 来源行：Source: 2024 United Nations E-Government Survey.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | row labels "Open government data", "AI", "Cloud" at left; bars grow rightwards |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f2 | **无** | four wrapped row labels at left, green and coloured bars grow rightwards |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or gridlines anywhere; only printed percentages and grey tracks |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | bars sit on grey tracks with no tick labels or baseline numbers |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | Africa orange, Americas purple, Asia yellow, Europe blue, Oceania cyan; region names in matching colour |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f2 | **无** | same region colour scheme reused per column, no legend explaining it |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | row names printed once at far left, serving all five region columns |
| `shared_axis` | 跨面板共享坐标轴 | f2 | 有 | the four content labels printed once at left for all five region columns |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f1 | **无** | five region columns repeating the same five rows, plus the global panel |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f2 | **无** | five region columns repeating the same four rows, plus "193 UN Member States" |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | "Figure 2.11" and "Figure 2.12" each with own caption and source line on one page |
| `source_note_lines` | source / note 行在图下方 | page | 有 | "Source: 2024 United Nations E-Government Survey." printed under both figures |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | green key "Percentage of countries with specific legislation" under the fan, above region rows |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | radial fan of wedges above, horizontal bar panels below, one figure number |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | coloured headers "Africa (54 countries)" ... "Oceania (14 countries)" above each column |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f2 | 有 | "Africa", "Americas", "Asia", "Europe", "Oceania" set above each bar column |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | italic heading line "(Percentage of countries, by region)"; bars carry no axis |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title "Percentage of countries with legislative frameworks..." and legend give the scale |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | "48%", "28%", "15%" printed at the left end inside each regional bar |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | "86%", "47%", "100%", "98%" printed inside the bars |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | wedge labels "Digital ID, 78%", "Cybersecurity, 82%" set outside the fan |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | "Misinformation, disinformation or fake news" wrapped over two left-hand lines |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f2 | **无** | "Announcements of forthcoming procurement or bidding processes published on the portal" wraps two lines |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f2 | **无** | the "193 UN Member States" aggregate bars are green while all region bars are region-coloured |

词表 65 项，本页出现 15 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `radial_fan_bar_chart` | f1 | twelve wedges radiating from a centre over a half circle, length encodes the percentage | 扇形楔块没有半径刻度，只能依赖旁边文字标签读数，值与像素长度不可线性核对。 |
| `bar_track_to_full_scale` | page | every bar sits in a grey track of equal length representing 100 per cent | 灰色底槽充当隐含的0–100%轴，读数需以底槽全长为分母，而非任何刻度。 |
| `label_and_value_in_one_string` | f1 | wedge labels read "Open government data, 63%": name and value in one text run | 解析器抽出的行名会连带数值，表格里类别名与数值不再分离，检索键需处理逗号拼接。 |
| `panel_row_of_bar_columns` | page | five region columns laid side by side, each a stack of same-named rows | 同一数值（如100%）在多列重复，必须用列标题（Asia/Europe）作附加键才能唯一定位。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

两图所有数值都印在条内，读数本身不难（48%、30%、100%、98%均为印刷文本，无需按刻度估计）；真正卡住的是寻址：48%在图2.11同时出现于Africa的Open government data和Asia的Cloud，100%在图2.12同时属于Asia与Europe的同一行，因此一个数值至少需要三个键（图号＋区域列标题＋行名），而行名如"Information provided about the results of government procurement or bidding online"跨两行折排、区域列标题只是彩色小字而非表头，解析器很容易把5×4的列阵压成一列丢掉panel键。另外，两图都无任何刻度（value_axis_ticks为空），一旦数值文字丢失便完全无法回推。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | 新组件 radial_fan_bar_chart（半圆扇形径向条）与 bar_track_to_full_scale（灰色100%底槽） | 图表族生成器新增径向扇形样式，并在条形样式字段加入"底槽/剩余量"开关 | 有底槽 vs 无底槽、径向 vs 直角坐标下的读值精度对比行 |
| P2 | 通用 | panel_key 进入寻址（5个区域列＋1个全球面板共用左侧行名） | 记录字段增加 panel_name，条件行设为"同名行在多面板重复且数值可重复" | 重复数值（100%出现在Asia与Europe）在有/无panel键时的唯一定位成功率 |
| P7 | 通用 | 标题分块：figure_number、title、斜体单位副标题"(Percentage of countries, by region)" | 图2.12的heading字段拆分为number/title/subtitle/unit，placement=above | 单位仅存在于斜体副标题时，导出表格是否仍带单位一行 |
| P6 | 一类出版方 | value_label_inside 与 no_value_axis 组合（无刻度、只有条内标签） | 样式维度中的数值标签位置与刻度绘制开关 | 无刻度＋标签内嵌 vs 有刻度＋无标签两种条件下的数值召回率 |
| P6 | 这份文档自己的习惯 | label_and_value_in_one_string（"Digital ID, 78%"式合并标签） | 标签渲染字段增加"名称+数值同串"模式 | 合并标签 vs 分离标签时行名匹配的准确率 |
