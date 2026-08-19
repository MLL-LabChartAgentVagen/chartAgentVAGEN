# Earnings_Presentation_(FY26_Q1)_1_p9

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Earnings_Presentation_(FY26_Q1)_1 | `untagged` | 10 | 0 |

沃尔玛季度业绩幻灯片第9页，左侧为门店照片，右侧为「Returns to shareholders」堆叠柱状图（股息与股票回购，含轴下合计行）及两条侧边要点文字。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | $1.1 | `Share repurchases` · `Q1 FY25` | 1% | f1 | the Q1 FY25 Share repurchases segment (light blue top) | 是 | `Q1 FY25` · `Share repurchases` |
| 2 | $1.0 | `Share repurchases` · `Q3 FY25` | 1% | f1 | the Q2 FY25 Share repurchases segment (also $1.0 for Q3 FY25) | 是 | `Q2 FY25` · `Share repurchases` |
| 3 | $1.4 | `Share repurchases` · `Q4 FY25` | 1% | f1 | the Q4 FY25 Share repurchases segment | 是 | `Q4 FY25` · `Share repurchases` |
| 4 | $4.6 | `Share repurchases` · `Q1 FY26` | 1% | f1 | the Q1 FY26 Share repurchases segment; also quoted in the side bullet | 是 | `Q1 FY26` · `Share repurchases` |
| 5 | $1.7 | `Dividends` · `Q1 FY25` | 1% | f1 | the Q1 FY25 Dividends segment (same label repeats for Q2, Q3, Q4 FY25) | 是 | `Q1 FY25` · `Dividends` |
| 6 | $1.7 | `Dividends` · `Q4 FY25` | 1% | f1 | the Q2 FY25 Dividends segment | 是 | `Q2 FY25` · `Dividends` |
| 7 | $1.9 | `Dividends` · `Q1 FY26` | 1% | f1 | the Q1 FY26 Dividends segment | 是 | `Q1 FY26` · `Dividends` |
| 8 | $2.7 | `Returns to shareholders` · `Q1 FY25` | 1% | f1 | the Q1 FY25 entry of the 'Returns to shareholders' totals row (repeats for Q2 FY25) | 是 | `Q1 FY25` · `Returns to shareholders` |
| 9 | $2.6 | `Returns to shareholders` · `Q3 FY25` | 1% | f1 | the Q3 FY25 entry of the 'Returns to shareholders' totals row | 是 | `Q3 FY25` · `Returns to shareholders` |
| 10 | $6.4 | `Returns to shareholders` · `Q1 FY26` | 1% | f1 | the Q1 FY26 entry of the 'Returns to shareholders' totals row | 是 | `Q1 FY26` · `Returns to shareholders` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: $1.0, $1.7

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 2 | 5 | 10 | 全部 | （不画值轴） |

- **f1** Returns to shareholders / Dividends and share repurchases　[图上方]　单位 `Amounts in billions, except as noted. Dollar amounts may not recalculate due to rounding.`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each quarter bar has a dark blue 'Dividends' base and light blue 'Share repurchases' top segment |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only a horizontal baseline under the bars; no ticks or value-axis numbers drawn |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Dividends' and 'Share repurchases' swatch row sits below the category labels |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f1 | **无** | bullets 'Share repurchases during the quarter totaled $4.6 billion...' in a column right of the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | 'Amounts in billions, except as noted' printed under the title, no unit on plot |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | '$1.7' and '$1.1' printed inside the segments of the Q1 FY25 bar |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | category ticks read 'Q1 FY25', 'Q2 FY25' ... 'Q1 FY26' rather than dates |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | the total row label 'Returns to shareholders' wraps onto two lines in a tinted box |
| `total_row_below_axis` | 轴下方一行合计值，与类目对齐 | f1 | **无** | row labelled 'Returns to shareholders' below legend reads $2.7, $2.7, $2.6, $3.1, $6.4 |

词表 65 项，本页出现 9 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `unlabeled_total_row_header_box` | f1 | 'Returns to shareholders' label sits in a light grey filled box left of the totals row | 该合计行既是行名又重复了图表标题文字，解析时若丢失灰底行头，$2.7/$6.4 等数值将失去唯一标签。 |
| `bullet_text_duplicates_chart_value` | f1 | bullet says 'totaled $4.6 billion' matching the printed Q1 FY26 Share repurchases segment '$4.6' | 同一数值在图内与旁注两处出现，取值时需判断标签归属，避免把正文数字当作另一条记录。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

所有数值都印在图上（$1.7、$1.1、$4.6…），且没有值轴，读数不成问题，所以难点不是步骤2。难在标签：$1.7 在四个季度重复出现、$1.0 出现两次、$2.7 出现两次，任一数值必须同时带上季度（Q1 FY25…Q1 FY26）与系列（Dividends / Share repurchases）两个键才唯一；而 $2.7/$2.6/$6.4 属于轴下的合计行，其行名是灰底框中的「Returns to shareholders」，解析器很容易把它当成第三个系列或直接丢掉，从而无法把这三个数与其他 8 个数区分开。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | total_row_below_axis（轴下合计行，带灰底行头） | 堆叠柱条件行中新增「是否绘制轴下合计行」样式字段，并在记录中把合计行作为独立行名而非系列 | 有/无轴下合计行两组对照，衡量合计数值被误并入系列或丢失的比例 |
| P1 | 一类出版方 | no_value_axis + value_label_inside 组合 | 样式字段：值轴刻度可完全关闭，同时强制段内数值标签 | 「无值轴仅靠标签」与「有刻度轴」两行，检验取值是否依赖 OCR 标签而非像素测量 |
| P3 | 一类出版方 | side_text_bullets（图旁要点栏，且要点复述图内数值） | 页面布局行：图表与右侧文字列共享同一水平带；记录需标注哪些数值在正文中重复 | 含/不含数值复述型旁注两行，测量数值-标签匹配的假阳性率 |
| P7 | 通用 | unit_in_axis_or_title（'Amounts in billions, except as noted' 作为副标下的单位行） | 标题字段拆分为 number/title/subtitle/unit，并允许 unit 单独成行置于副标之下 | 单位行独立成行 vs 并入标题两行，检验导出表能否携带 billions 量级 |
