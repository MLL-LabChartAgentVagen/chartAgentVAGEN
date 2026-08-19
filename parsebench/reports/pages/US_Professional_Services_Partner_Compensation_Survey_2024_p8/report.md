# US_Professional_Services_Partner_Compensation_Survey_2024_p8

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| US_Professional_Services_Partner_Compensation_Survey_2024 | `untagged` | 5 | 0 |

这一页是《2024 US Professional Services Partner Compensation Survey》第8页，包含三个图：按任职年限划分的个人收入目标横条图矩阵、当前角色环形图、以及额外领导角色的横条图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 24 | `$6.01m–$10.00m` · `2–3 years` | 1% | f1 | the `$6.01m–$10.00m` bar in the `2–3 years` column | 是 | `Personal revenue targets, by tenure in role` · `2–3 years` · `$6.01m–$10.00m` |
| 2 | 22 | `$1.00m–$3.00m` · `4–5 years` | 1% | f1 | the `$1.00m–$3.00m` bar in the `4–5 years` column | 是 | `Personal revenue targets, by tenure in role` · `4–5 years` · `$1.00m–$3.00m` |
| 3 | 24 | `More than $30.00m` · `More than 5 years` | 1% | f1 | the `More than $30.00m` bar in the `More than 5 years` column | 是 | `Personal revenue targets, by tenure in role` · `More than 5 years` · `More than $30.00m` |
| 4 | 93 | `Partner (or partner-equivalent)` | 1% | f2 | the `Partner (or partner-equivalent)` arc of the donut | 是 | `What is your current role?` · `Partner (or partner-equivalent)` |
| 5 | 30 | `No` | 1% | f3 | the `No` bar | 是 | `Do you have any additional firm leadership roles?` · `No` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | horizontal | 4 | 1 | 11 | 44 | 全部 | （不画值轴） |
| f2 | `donut` | na | 1 | 2 | 2 | 2 | 全部 | （不画值轴） |
| f3 | `bar` | horizontal | 1 | 1 | 4 | 4 | 全部 | （不画值轴） |

- **f1** Personal revenue targets (%) / Personal revenue targets, by tenure in role　[图上方]　单位 `(%)`
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=155
- **f2** Current role information (%) / What is your current role?　[图上方]　单位 `(%)`
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=187
- **f3** Do you have any additional firm leadership roles?　[图上方]　（标题里没有单位）
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=169

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | revenue-target bands on the left, bars grow rightwards in four tenure columns |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f3 | **无** | `Practice leader`, `Regional leader`, `Office leader`, `No` rows with bars growing right |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or baseline numbers; only printed labels like `18`, `21`, `24` |
| `no_value_axis` | 没有值轴刻度，只有基线 | f3 | **无** | bars for 54, 9, 7, 30 drawn with no value axis or ticks |
| `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | f1 | **无** | `0` printed with no bar drawn for `$25.01m–$30.00m` under `Less than 2 years` |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | each tenure column uses its own fill: navy, teal, teal, grey, not series identity |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | the revenue-band row labels are printed once at the left for all four columns |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | four tenure columns repeat the same bar chart over the same 11 rows |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | `Personal revenue targets (%)`, `Current role information (%)` with separate source lines |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Note: Numbers may not sum to 100%, because of rounding.` above the Source line |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f2 | 有 | `Partner (or partner-equivalent)` / `Pre-partner` swatches sit between subtitle and donut |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | `Less than 2 years`, `2–3 years`, `4–5 years`, `More than 5 years` head each column |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | left column body text `By tenure in their current role...` runs beside the figures |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | `Personal revenue targets (%)` carries the percent unit; bars have bare numbers |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | `Current role information (%)` supplies the unit for `7` and `93` |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | `18`, `21`, `24`, `22` printed inside the dark and teal bars |
| `value_label_inside` | 数值标签写在图元内部 | f3 | 有 | `54`, `9`, `7`, `30` printed inside the bars |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | `0` printed where no bar exists, e.g. `2–3 years` row `Less than $1.00m` |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | `7` above the small teal arc and `93` beside the dark ring, outside the donut |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | panel names wrap: `Less than` / `2 years`, `More than` / `5 years` |

词表 65 项，本页出现 15 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `panel_as_column_matrix` | f1 | four panels laid as adjacent columns sharing one left row-label list, like a table of bars | 读某个数值必须同时定位行（收入区间）与列（任职年限），单一行标签不足以唯一寻址。 |
| `per_panel_series_color` | f1 | navy for `Less than 2 years`, teal for `2–3 years` and `4–5 years`, grey for `More than 5 years` | 颜色不是图例项，无法用图例辨认列，只能靠列标题定位，增加误读列的风险。 |
| `zero_printed_without_mark` | f1 | `0` appears as text alone at bar origin, e.g. `$10.01m–$15.00m` under `4–5 years` | 零值行没有可测量的图元，抽取表格时容易漏行或错列对齐。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

所有数值都印在图上，读数不构成问题（第2步无难度）；难点在寻址：f1 是 4 列 × 11 行的矩阵，`24` 在图中出现两次（`2–3 years`/`$6.01m–$10.00m` 与 `More than 5 years`/`More than $30.00m`），必须同时携带列标题与行标签两个键才能唯一定位，而列标题本身还换行为两行（`Less than` / `2 years`），解析器很可能把它拆成表头碎片或丢掉；此外没有任何数值轴，若表格只保留一列数字，行与列的对应关系就完全失效。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | panel_as_column_matrix（新组件）与 small_multiples_4 的列式布局 | 图表布局条件行：允许把多个 panel 横向并列并共用左侧行标签，panel 名进入 panel_key | panel_key 在列式并列面板下的寻址成功率 vs 传统上下堆叠面板 |
| P1 | 一类出版方 | no_value_axis 搭配 value_label_inside 的纯标签读数模式 | 样式字段：value_axis 可置为 none，同时强制 values_printed=all | 无值轴仅靠印字标签时的每标记精度（P1 的布尔门槛替换） |
| P6 | 一类出版方 | zero_printed_without_mark（新组件） | 记录字段：零值应生成文字标签而非零长度条 | 含零值文字标签的行是否被导出表格保留 |
| P7 | 通用 | 标题拆分为 title / subtitle / unit（`Personal revenue targets (%)` 与 `Personal revenue targets, by tenure in role`） | heading 字段结构：两级标题且单位嵌在主标题括号内 | 单位仅存于主标题括号时的单位召回率 |
| P3 | 通用 | multi_figure_page 与各图独立 source（n=155 / n=187 / n=169） | 页面级导出：每图标题作为粗体或标题行紧邻其表格 | 同页三图导出时标题-表格归属正确率 |
