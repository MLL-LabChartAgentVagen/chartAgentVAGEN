# FPA-guide-to-data-visualization_p20

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| FPA-guide-to-data-visualization | `untagged` | 10 | 0 |

本页为AFP数据可视化指南第17页，左侧是带项目符号的"Pie charts"正文栏，右侧自上而下有两个饼图（FY 14 Q2 Forecast 与 FY 14 Jan Actual）和一个把两组数据合并的水平条形图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 61 | `Salaries and Benefits` · `FY14 Q2 Forecast` | 1% | f1 | the Salaries and Benefits slice | 是 | `FY 14 Q2 Forecast` · `Salaries and Benefits` |
| 2 | 60.3 | `Salaries and Benefits` · `FY14 Jan Actual` | 1% | f2 | the Salaries and Benefits slice | 是 | `FY 14 Jan Actual` · `Salaries and Benefits` |
| 3 | 9 | `Contracts and Professional Fees` · `FY14 Q2 Forecast` | 1% | f1 | the Contracts and Professional Fees slice | 是 | `FY 14 Q2 Forecast` · `Contracts and Professional Fees` |
| 4 | 10.1 | `Contracts and Professional Fees` · `FY14 Jan Actual` | 1% | f2 | the Contracts and Professional Fees slice | 是 | `FY 14 Jan Actual` · `Contracts and Professional Fees` |
| 5 | 10 | `Depreciation, Interest and Maintenance` · `FY14 Q2 Forecast` | 1% | f1 | the Depreciation, Interest and Maintenance slice | 是 | `FY 14 Q2 Forecast` · `Depreciation, Interest and Maintenance` |
| 6 | 9 | `Depreciation, Interest and Maintenance` · `FY14 Jan Actual` | 1% | f2 | the Depreciation, Interest and Maintenance slice | 是 | `FY 14 Jan Actual` · `Depreciation, Interest and Maintenance` |
| 7 | 7 | `Office Expenses and Other Costs*` · `FY14 Q2 Forecast` | 1% | f1 | the Office Expenses and Other Costs* slice | 是 | `FY 14 Q2 Forecast` · `Office Expenses and Other Costs*` |
| 8 | 8 | `Office Expenses and Other Costs*` · `FY14 Jan Actual` | 1% | f2 | the Office Expenses and Other Costs* slice | 是 | `FY 14 Jan Actual` · `Office Expenses and Other Costs*` |
| 9 | 7 | `Conference, Meetings and Exhibits` · `FY14 Q2 Forecast` | 1% | f1 | the Conference, Meetings and Exhibits slice | 是 | `FY 14 Q2 Forecast` · `Conference, Meetings and Exhibits` |
| 10 | 5 | `Conference, Meetings and Exhibits` · `FY14 Jan Actual` | 1% | f2 | the Conference, Meetings and Exhibits slice | 是 | `FY 14 Jan Actual` · `Conference, Meetings and Exhibits` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `pie` | na | 1 | 1 | 8 | 8 | 全部 | （不画值轴） |
| f2 | `pie` | na | 1 | 1 | 8 | 8 | 全部 | （不画值轴） |
| f3 | `bar` | horizontal | 1 | 2 | 8 | 16 | 无 | 0%, 10%, 20%, 30%, 40%, 50%, 60%, 70% |

- **f1** FY 14 Q2 Forecast　[图上方]　单位 `Total: $750,000`
- **f2** FY 14 Jan Actual　[图上方]　单位 `Total: $387,000k`
  - 来源行：*Other costs category includes marketing and promotions costs.
- **f3** Data graphed after applying data visualization rules:　[图上方]　（标题里没有单位）
  - 来源行：*Other costs category includes marketing and promotions costs.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `horizontal_bars` | 横向条形（类目在 y 轴） | f3 | **无** | category names sit on the left, dark bars grow rightwards from a common left baseline |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | pie has no ticks anywhere; percentages readable only from the printed leader-line labels |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | no axis or ticks drawn; only printed labels such as "60.3%" give values |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f3 | **无** | "FY14 Q2 Forecast" is drawn as a short orange vertical dash on each navy bar |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | three separately titled charts: two pies plus "Data graphed after applying data visualization rules:" |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | small print below: "*Other costs category includes marketing and promotions costs." |
| `source_note_lines` | source / note 行在图下方 | f3 | 有 | small print below the bars repeats "*Other costs category includes marketing and promotions costs." |
| `legend_inside_plot` | 图例画在绘图区内部 | f3 | **无** | "FY14 Jan Actual  FY14 Q2 Forecast" keys sit in the plot area level with the Editing/Publishing row |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | tinted left column "Pie charts" with bullets runs alongside all three charts |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | category label reads "Office Expenses and Other Costs*" with an asterisk |
| `footnote_marker` | 标题或标签里的脚注上标 | f3 | **无** | row label reads "Office Expenses and Other Costs*" |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | each slice's name and percent, e.g. "Salaries and Benefits 61%", sits outside on a leader line |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | "Contracts and Professional Fees 10.1%" printed outside the pie with a leader line |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f3 | **无** | "Depreciation, Interest" / "and Maintenance" and "Travel and Business" / "Entertainment" wrap onto two lines |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | "Conference, Meetings" / "and Exhibits" / "7%" wraps across three lines outside the pie |

词表 65 项，本页出现 10 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `value_axis_above_plot` | f3 | the "0% 10% ... 70%" tick row is printed above the top bar, not below the plot | 读值时刻度行在图上方，解析器容易把它当成标题或独立文本行，条形长度与刻度的对应关系需要跨行重建。 |
| `total_in_heading` | f1 | heading line ends "Total: $750,000"; slices are labelled only in percent | 饼图各片只有百分比，绝对金额必须靠标题里的总额换算，标题若丢失则数值失去量纲。 |
| `same_categories_across_untitled_figures` | page | f1, f2 and f3 all use the identical eight expense category names, none numbered | 同一数字（如9）在多个图中重复出现，缺少图编号时无法仅凭类别名定位到唯一标记。 |

## 5 · 难在哪

卡在 **第四步 · 表外上下文**。

十个待测值全部印在两个饼图的引出标签上，读数不成问题（步骤2不卡）；类别名也齐全（步骤3只需两个键）。真正卡住的是图级上下文：f1与f2使用完全相同的八个类别名，且两图都没有图号，只有"FY 14 Q2 Forecast  Total: $750,000"与"FY 14 Jan Actual  Total: $387,000k"两行标题；而"9"同时是f1的Contracts and Professional Fees和f2的Depreciation, Interest and Maintenance，"7"在f1中出现两次。若解析器不把这两行标题作为粗体或标题级文本紧贴各自表格输出，任何行标签都无法把9或7锁定到唯一标记；f3又把同一组数字第三次以0%–10%间距的条形重现，进一步放大歧义。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P3 | 一类出版方 | 新组件 same_categories_across_untitled_figures 与 total_in_heading | 记录字段中为每张图增加 figure_title/unit_text 字段，并要求导出时标题以标题级文本紧贴表格上方 | "标题与表格相邻 vs 标题剥离到页首"两种导出方式下，重复类别名图组的定位准确率对比 |
| P4 | 一类出版方 | tick_marker_as_series（橙色短划作为FY14 Q2 Forecast系列） | 条形图样式条件行中增加"第二系列以刻度标记而非并列条绘制"选项 | 同一数据以grouped_bar绘制 vs 以条上刻度标记绘制时的取值成功率 |
| P6 | 一类出版方 | 新组件 value_axis_above_plot（刻度行位于绘图区上方） | 样式字段中的刻度位置维度，增加水平条形图刻度置顶 | 刻度在下 vs 刻度在上时，水平条形图无印值读数的可达精度 |
| P6 | 通用 | value_label_outside 配引出线且标签内含类别名与百分比 | 饼图样式条件行中的标签放置字段（内部百分比 vs 外部引出线"名称+百分比"） | 饼图标签内置 vs 外置引出线两种条件下的行标签匹配率 |
