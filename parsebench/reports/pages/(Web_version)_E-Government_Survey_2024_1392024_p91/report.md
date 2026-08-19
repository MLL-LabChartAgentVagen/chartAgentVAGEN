# (Web_version)_E-Government_Survey_2024_1392024_p91

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| (Web_version)_E-Government_Survey_2024_1392024 | `untagged` | 5 | 0 |

本页为《2024 UN E-Government Survey》第66页，上半为正文段落，下半为图2.25：一张由上下两组、共七个面板构成的水平堆叠条形图，展示2022与2024年及五大洲各弱势群体在线服务比例。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 21% | `Immigrants` · `2024` · `Fully digitalized` | 1% | f1 | the 2024 'Immigrants' Fully digitalized segment (also printed four times in the Oceania panel) | 是 | `193 UN Member States` · `2024` · `Fully digitalized` · `Immigrants` |
| 2 | -1.9% | `Youth` · `Percentage change since 2022` | 1% | f1 | the 'Youth' entry in the Percentage change since 2022 text column | 是 | `Percentage change since 2022` · `Youth` |
| 3 | 36% | `Older people` · `Asia` · `Fully digitalized` | 1% | f1 | the Asia 'Older people' Fully digitalized segment | 是 | `Asia` · `Fully digitalized` · `Older people` |
| 4 | 51% | `Youth` · `Europe` · `Fully digitalized` | 1% | f1 | appears six times; e.g. the Europe 'Older people' Available segment (also Americas Immigrants, Americas poverty line, Europe poverty line, Asia Women, Europe Youth Fully digitalized) | 是 | `Europe` · `Available` · `Older people` |
| 5 | 54% | `Persons with disabilities` · `Africa` · `Available` | 1% | f1 | the 2024 'Persons with disabilities' Available segment (also 2024 Women, Africa disabilities, Americas Women) | 是 | `193 UN Member States` · `2024` · `Available` · `Persons with disabilities` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 5 predicted key sets miss a rule label: 51%, 54%

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | horizontal | 7 | 2 | 6 | 83 | 全部 | （不画值轴） |

- **f1** Figure 2.25 / Percentage of countries offering services for people in vulnerable situations that can be completed partially or fully online, 2022 and 2024　[图上方]　（标题里没有单位）
  - 来源行：Sources: 2022 and 2024 United Nations E-Government Surveys.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each row bar carries a dark 'Fully digitalized' segment followed by a lighter 'Available' segment, e.g. '21%' then '52%' |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | category names 'Immigrants', 'Older people' sit at the left and bars extend rightwards |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or baseline numbers anywhere; every quantity is only the printed '21%', '52%' text |
| `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | f1 | **无** | Oceania 'Women' row shows only '71%' in the light segment; no Fully digitalized segment or number |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | hue marks the region: green 2024, grey 2022, orange Africa, purple Americas, yellow Asia, blue Europe, teal Oceania |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | category names printed once at the left of each block and shared by the panels to the right |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f1 | **无** | seven repeated bar blocks: '2024', '2022', 'Africa', 'Americas', 'Asia', 'Europe', 'Oceania' |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Sources: 2022 and 2024 United Nations E-Government Surveys.' printed under the framed plot |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | 'Fully digitalized   Available' repeated above every one of the seven panels |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | the 'Fully digitalized / Available' word pair sits between each panel title and its bars |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | '2024', '2022' above the top blocks; 'Africa', 'Americas', 'Asia', 'Europe', 'Oceania' above the lower blocks |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title opens 'Percentage of countries offering services...'; no unit sits on any axis |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | '26%', '50%' printed on top of the dark and light segments of each bar |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | Africa and Oceania rows: '6%', '4%', '14%' labels overflow the very narrow dark segments |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | long names such as 'Persons living below poverty line' run the full width of the left label column |

词表 65 项，本页出现 15 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `full_scale_track_behind_bar` | f1 | a pale grey track of equal length behind every bar, marking the unreached remainder to 100% | 灰色底槽本身不是数据，读数时必须只量彩色段，否则会把整条底槽误当作某个数值。 |
| `numeric_change_column_between_panels` | f1 | 'Percentage change since 2022' column of bare text values -13.5%, 2.7%, -8.3%, -1.3%, -8.6%, -1.9% between the 2024 and 2022 panels | 该列只有数字没有图形，且既非2024也非2022面板，需要单列标签才能唯一定位。 |
| `panel_group_header` | f1 | '193 UN Member States' printed above the 2024/2022 pair, naming the whole upper block | 上组两面板共享一个全球范围标题，缺它就无法区分全球行与区域行的同名类别。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值全部印在段内，读数不成问题（第2步无风险）；难在定址：图内 '21%' 出现5次、'51%' 出现6次、'54%' 出现4次，唯一定位一条数值必须同时给出面板（2024 / 2022 / Africa…Oceania，外加 '193 UN Member States' 这一组标题）、系列（Fully digitalized 或 Available）和行名（如 Persons with disabilities）三到四个键；而 'Percentage change since 2022' 那一列既无系列也不属于任一区域面板，需要第四类键。普通解析器往往把七个面板拉平成一张表，行名重复六次而列头只剩 Fully digitalized/Available，面板维度丢失后 51% 无法与其它五处区分。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | per_panel_legend 与 panel_title_per_panel 组合下的面板键（panel_key） | 记录字段中为每个数值增加 panel 维度，条件行区分'同一系列名在七个面板重复' | 有/无 panel_key 时，对同一系列名重复出现于5个以上面板的图，数值定址准确率对比 |
| P6 | 一类出版方 | 新组件 full_scale_track_behind_bar（条后满量程灰槽） | 样式字段增加'背景轨道'开关，用于水平堆叠条 | 绘制/不绘制灰色满量程轨道时，模型是否把轨道误读为第三个数据段 |
| new | 一类出版方 | 新组件 numeric_change_column_between_panels（面板之间的纯文本变化列） | 版面条件行：在两个面板之间插入一列只有文本的派生数值 | 含/不含纯文本派生列时，该列数值（如 -1.9%）能否被表格行正确命名 |
| P7 | 通用 | no_value_axis + value_label_inside 的组合以及标题内单位（Percentage of countries） | 样式字段：数值标签位置与单位位置；标题字段拆出 unit | 无值轴且单位只在标题时，导出表格是否保留百分号与单位语义 |
| P1 | 一类出版方 | missing_value_marker（Oceania Women 缺 Fully digitalized 段） | 记录字段允许某系列在个别类别为空，并在渲染时留白 | 含缺失段的堆叠条中，缺失位是否被错填为相邻数值 |
