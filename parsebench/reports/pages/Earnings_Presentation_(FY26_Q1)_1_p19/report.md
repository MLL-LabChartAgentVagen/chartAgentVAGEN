# Earnings_Presentation_(FY26_Q1)_1_p19

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Earnings_Presentation_(FY26_Q1)_1 | `untagged` | 10 | 0 |

沃尔玛财报演示第19页，展示Sam's Club U.S.同店销售的分组柱状图（含燃油/不含燃油），右侧配要点文字和一张生活场景照片。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 3.5% | `Q1 FY25` · `With fuel` | 1% | f1 | the Q1 FY25 'With fuel' bar | 是 | `Sam's Club U.S. comp sales` · `Q1 FY25` · `With fuel` |
| 2 | 4.4% | `Q1 FY25` · `Without fuel` | 1% | f1 | the Q1 FY25 'Without fuel' bar | 是 | `Sam's Club U.S. comp sales` · `Q1 FY25` · `Without fuel` |
| 3 | 4.6% | `Q2 FY25` · `With fuel` | 1% | f1 | the Q2 FY25 'With fuel' bar | 是 | `Sam's Club U.S. comp sales` · `Q2 FY25` · `With fuel` |
| 4 | 5.2% | `Q2 FY25` · `Without fuel` | 1% | f1 | the Q2 FY25 'Without fuel' bar | 是 | `Sam's Club U.S. comp sales` · `Q2 FY25` · `Without fuel` |
| 5 | 3.7% | `Q3 FY25` · `With fuel` | 1% | f1 | the Q3 FY25 'With fuel' bar | 是 | `Sam's Club U.S. comp sales` · `Q3 FY25` · `With fuel` |
| 6 | 7.0% | `Q3 FY25` · `Without fuel` | 1% | f1 | the Q3 FY25 'Without fuel' bar | 是 | `Sam's Club U.S. comp sales` · `Q3 FY25` · `Without fuel` |
| 7 | 5.3% | `Q4 FY25` · `With fuel` | 1% | f1 | the Q4 FY25 'With fuel' bar | 是 | `Sam's Club U.S. comp sales` · `Q4 FY25` · `With fuel` |
| 8 | 6.8% | `Q4 FY25` · `Without fuel` | 1% | f1 | the Q4 FY25 'Without fuel' bar | 是 | `Sam's Club U.S. comp sales` · `Q4 FY25` · `Without fuel` |
| 9 | 4.0% | `Q1 FY26` · `With fuel` | 1% | f1 | the Q1 FY26 'With fuel' bar | 是 | `Sam's Club U.S. comp sales` · `Q1 FY26` · `With fuel` |
| 10 | 6.7% | `Q1 FY26` · `Without fuel` | 1% | f1 | the Q1 FY26 'Without fuel' bar | 是 | `Sam's Club U.S. comp sales` · `Q1 FY26` · `Without fuel` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 1 | 2 | 5 | 10 | 全部 | （不画值轴） |

- **f1** Sam's Club U.S. comp sales　[图上方]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | two bars per quarter slot, dark 'With fuel' beside light 'Without fuel' |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no y-axis ticks or gridlines; only printed labels like '3.5%', '7.0%' above bars |
| `source_note_lines` | source / note 行在图下方 | page | 有 | "¹Comp sales for the 13-week period ended May 2, 2025 compared to the 13-week period ended May 3, 2024." |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'With fuel' and 'Without fuel' swatches sit in a row under the category axis |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f1 | **无** | bullet column 'Continued strength in grocery and health & wellness...' runs beside the chart |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | superscript 1 in "Sam's Club U.S. comp sales¹" tied to footnote at page bottom |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '3.5%', '4.4%', '7.0%' printed above the tops of the bars |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | category ticks read 'Q1 FY25', 'Q2 FY25' ... 'Q1 FY26' rather than ISO dates |
| `total_row_below_axis` | 轴下方一行合计值，与类目对齐 | f1 | **无** | row '+180 bps +230 bps +290 bps +280 bps +350 bps' under axis labelled 'eComm Cont. without fuel' |

词表 65 项，本页出现 9 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `annotated_row_with_row_label_box` | f1 | tinted box 'eComm Cont. without fuel' left of the bps row aligns it as a labelled data row | 该行有自己的行名与单位（bps），读取时须把'+290 bps'与'Q3 FY25'和该行名同时定位，否则会误当成柱值。 |
| `metric_in_title_not_unit` | f1 | title says 'comp sales' with no % unit line; scale only visible from '%' inside each label | 没有单位行和值轴，百分号只能从数值标签本身获得，表格导出时需自行补单位。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

十个值全部印在柱顶，且无值轴，所以读数不是问题（第2步不成立）。难点在寻址：每个值需要三个键——图标题"Sam's Club U.S. comp sales"、季度"Q1 FY25"…"Q1 FY26"、系列"With fuel"/"Without fuel"。若解析器只输出一行数字（如3.5 4.4 4.6 5.2…），4.6%与4.4%、6.7%与6.8%这类相近数值在5%容差内会互相混淆（4.4与4.6相差仅0.2个百分点，约4.5%相对差），系列名缺失就无法唯一定位；再加上轴下"+180 bps…+350 bps"这一行也按季度排列，容易被并入同一表格造成行名错配。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | total_row_below_axis（配合行名标签框） | 在样式条件行中增加"轴下附加指标行"字段，并在记录里为该行单独存行名与单位（bps） | 有/无轴下指标行时，主柱值与附加行值被互换的错误率对比 |
| P1 | 一类出版方 | no_value_axis + value_label_outside 组合 | 图表样式字段：value_axis=off 且 label_placement=outside | 无值轴仅靠标签的图，其数值命中率与有轴图的对比行 |
| P7 | 一类出版方 | unit 只存在于数值标签内的情况（metric_in_title_not_unit） | 标题记录的 unit 字段允许为空，同时标注 unit_carrier=label | 单位位置三态（标题/轴/标签内）对导出表单位补全正确率的影响 |
| P3 | 通用 | side_text_bullets（图旁正文列） | 页面版式条件行：图占页面左侧带，右侧为要点列 | 整页 markdown 导出时，旁栏要点是否被误并入图表表格的行 |
