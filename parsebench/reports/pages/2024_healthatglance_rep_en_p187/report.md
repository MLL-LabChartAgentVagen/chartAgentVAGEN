# 2024_healthatglance_rep_en_p187

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2024_healthatglance_rep_en | `untagged` | 10 | 0 |

本页为《Health at a Glance: Europe 2024》第185页，仅含一张编号图 Figure 7.5，由五个并列的横向条形小图组成，显示34个国家/地区五类卫生服务的公共与强制保险支出占比，数值全部直接标在条上。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 90 | `EU27` · `Inpatient care` | 1% | f1 | the EU27 bar in the Inpatient care panel (also 90% for Cyprus Pharmaceuticals and Germany Outpatient) | 是 | `EU27` · `Inpatient care` · `Figure 7.5.` |
| 2 | 84 | `Austria` · `Outpatient medical care` | 1% | f1 | the Austria bar in the Outpatient medical care panel (Iceland also 84% there) | 是 | `Austria` · `Outpatient medical care` · `Figure 7.5.` |
| 3 | 50 | `Bulgaria` · `Dental care` | 1% | f1 | the Bulgaria bar in the Dental care panel | 是 | `Bulgaria` · `Dental care` · `Figure 7.5.` |
| 4 | 75 | `Croatia` · `Pharmaceuticals` | 1% | f1 | the Croatia bar in the Pharmaceuticals panel | 是 | `Croatia` · `Pharmaceuticals` · `Figure 7.5.` |
| 5 | 41 | `Czechia` · `Therapeutic appliances` | 1% | f1 | the Finland bar in the Dental care panel (also Latvia Pharmaceuticals, Czechia and Norway Therapeutic appliances) | 是 | `Finland` · `Dental care` · `Figure 7.5.` |
| 6 | 93 | `Denmark` · `Outpatient medical care` | 1% | f1 | the Croatia bar in the Inpatient care panel (Denmark Outpatient is also 93%) | 是 | `Croatia` · `Inpatient care` · `Figure 7.5.` |
| 7 | 72 | `Germany` · `Dental care` | 1% | f1 | the Germany bar in the Dental care panel (Switzerland Outpatient is also 72%) | 是 | `Germany` · `Dental care` · `Figure 7.5.` |
| 8 | 89 | `Spain` · `Inpatient care` | 1% | f1 | the Spain bar in the Inpatient care panel (Luxembourg Outpatient is also 89%) | 是 | `Spain` · `Inpatient care` · `Figure 7.5.` |
| 9 | 82 | `Iceland` · `Therapeutic appliances` | 1% | f1 | the France bar in the Pharmaceuticals panel (Bosnia and Herzegovina Inpatient and Iceland Therapeutic appliances also 82%) | 是 | `France` · `Pharmaceuticals` · `Figure 7.5.` |
| 10 | 67 | `United Kingdom` · `Pharmaceuticals` | 1% | f1 | the France bar in the Dental care panel (Austria Pharmaceuticals, Belgium/Hungary Outpatient, United Kingdom Pharmaceuticals also 67%) | 是 | `France` · `Dental care` · `Figure 7.5.` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: 41, 93, 82, 67

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | horizontal | 5 | 1 | 34 | 163 | 全部 | （不画值轴） |

- **f1** Figure 7.5. / Healthcare coverage for selected services, 2022 (or nearest year) / Government and compulsory insurance spending as proportion of total health spending by type of services　[图上方]　（标题里没有单位）
  - 来源行：Source: OECD Health Statistics 2024.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names run down the left edge, bars grow rightwards in each of the five panels |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no numeric tick labels on any panel; only printed percentages such as "90%", "77%" |
| `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | f1 | **无** | "N/A" printed where bars are absent: Greece dental and therapeutic, Ireland, Italy, Portugal, Serbia, Finland |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | the country labels are printed once at the far left and serve all five panels |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f1 | **无** | five identical horizontal-bar panels side by side for five service types |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: Outpatient medical services mainly refer to..." and "Source: OECD Health Statistics 2024." below the plot |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | "Inpatient care", "Outpatient medical care", "Dental care", "Pharmaceuticals", "Therapeutic appliances" set above each panel |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | "StatLink" logo with "https://stat.link/1ubzf4" under the source line |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | percentages printed on the bars, e.g. "88%" inside Austria's inpatient bar |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | short bars push labels out: Latvia "12%", Romania "7%", Spain "2%" sit right of the bar |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 34 country names stacked down one axis, from "EU27" to "United Kingdom" |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | each of the five plot areas carries a light grey fill behind the bars |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 34 rows x 5 panels minus 7 N/A cells = about 163 bars |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the EU27 row is drawn in red/orange in all five panels while other rows are blue |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | faint vertical rules and edge ticks inside the grey panels; no horizontal rules between rows |

词表 65 项，本页出现 15 项，其中我们画不出来的 10 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `group_separator_gap_in_category_axis` | f1 | a blank unlabelled row between "Sweden" and "Bosnia and Herzegovina" splits EU from non-EU countries | 读值时要知道空行不是缺失数据，而是分组分隔；表格化时若把空行当作一个类别会整体错位一行。 |
| `unit_suffix_in_value_labels` | f1 | every printed value carries "%", e.g. "90%", "77%"; no axis or title states the unit symbol | 占位 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部以"90%"、"84%"形式印在条上，读数没有精度问题（第2步不成立，也无刻度标签可用）；真正的瓶颈是定位：10个待测值中有8个在页面上重复出现（例如90%同时属于EU27 Inpatient care、Cyprus Pharmaceuticals、Germany Outpatient；67%出现5次），所以每个值必须同时由国家行名与五个面板名之一（Inpatient care / Outpatient medical care / Dental care / Pharmaceuticals / Therapeutic appliances）联合寻址。解析器若把五个面板压平成一张34行的表而丢掉面板列名，或把面板标题只当作普通文本，就无法区分这些同值单元格；另外Sweden与Bosnia and Herzegovina之间的空行和7处"N/A"也容易让行对齐错位。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | 把面板维度写进寻址键（对应本页的panel_title_per_panel与shared_axis） | 记录字段中新增panel_key，条件行由(category, series)扩展为(panel, category, series) | 新增"去掉panel_key"一行：五面板小多重图在只有国家行名时的命中率对比 |
| new | 一类出版方 | missing_value_marker 与分组空行（group_separator_gap_in_category_axis） | 数据生成条件行加入"部分单元格为N/A"及"类别轴中插入无标签分隔行"两个开关 | 新增"含N/A单元格/含分隔空行"一行，检验行对齐是否发生整体偏移 |
| P6 | 通用 | 值标签位置随条长自适应（value_label_inside 与 value_label_outside 混用）+ 标签自带%后缀 | 样式字段value_label_placement增加auto_inside_outside，tick/label格式字段允许单位后缀 | 新增"短条标签外移"一行：极小值（2%、7%）标签溢出时的可读性对比 |
| P7 | 一类出版方 | 标题块五段拆分（figure_number / title / subtitle / 无独立unit / above） | 图元记录的heading字段，本页副标题"Government and compulsory insurance spending as proportion of total health spending by type of services"承载了比例含义 | 新增"标题与副标题分离导出"一行：单位仅存在于副标题时的上下文命中率 |
| P5 | 一类出版方 | 密度上限提升（dense_marks_100plus，本图约163个条） | 生成器的marks上限与34行类别标签堆叠的布局参数 | 新增">150个标记"一行，把密度作为受控变量检验寻址与读值退化 |
