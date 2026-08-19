# article_thebeatjun2025_p36

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| article_thebeatjun2025 | `untagged` | 10 | 0 |

这是摩根士丹利《The BEAT》2025年6月刊第36页，标题“Corporate Earnings Growth”下有两幅同构图：上为“Regions/Styles”、下为“S&P 500 Sectors”，均以粉色柱表示Expected EPS Growth、灰色圆点表示2024 EPS Growth，并在页脚给出FactSet来源说明。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 33.37 | `Russell 2000` · `Expected EPS Growth` | 1% | f1 | the Russell 2000 Expected EPS Growth bar | 是 | `Regions/Styles` · `Russell 2000` · `Expected EPS Growth` |
| 2 | 1.31 | `Russell 2000` · `2024 EPS Growth` | 1% | f1 | the Russell 2000 2024 EPS Growth grey dot | 是 | `Regions/Styles` · `Russell 2000` · `2024 EPS Growth` |
| 3 | 28.97 | `Russell 1000 Growth` · `2024 EPS Growth` | 1% | f1 | the Russell 1000 Growth 2024 EPS Growth grey dot | 是 | `Regions/Styles` · `Russell 1000 Growth` · `2024 EPS Growth` |
| 4 | 13.18 | `MSCI World ex USA Small Cap` · `Expected EPS Growth` | 1% | f1 | the MSCI World ex USA Small Cap Expected EPS Growth bar | 是 | `Regions/Styles` · `MSCI World ex USA Small Cap` · `Expected EPS Growth` |
| 5 | 18.22 | `MSCI EM` · `2024 EPS Growth` | 1% | f1 | the MSCI EM 2024 EPS Growth grey dot label (left of the 12.85 bar label) | 是 | `Regions/Styles` · `MSCI EM` · `2024 EPS Growth` |
| 6 | 17.59 | `Info. Tech.` · `Expected EPS Growth` | 1% | f2 | the Info. Tech. Expected EPS Growth bar | 是 | `S&P 500 Sectors` · `Info. Tech.` · `Expected EPS Growth` |
| 7 | 23.85 | `Communications` · `2024 EPS Growth` | 1% | f2 | the Communications 2024 EPS Growth grey dot | 是 | `S&P 500 Sectors` · `Communications` · `2024 EPS Growth` |
| 8 | 14.52 | `Health Care` · `Expected EPS Growth` | 1% | f2 | the Health Care Expected EPS Growth bar | 是 | `S&P 500 Sectors` · `Health Care` · `Expected EPS Growth` |
| 9 | -10.24 | `Materials` · `2024 EPS Growth` | 1% | f2 | the Materials 2024 EPS Growth grey dot, below zero | 是 | `S&P 500 Sectors` · `Materials` · `2024 EPS Growth` |
| 10 | -13.03 | `Energy` · `Expected EPS Growth` | 1% | f2 | the Energy Expected EPS Growth bar, below zero | 是 | `S&P 500 Sectors` · `Energy` · `Expected EPS Growth` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 10 | 20 | 全部 | 50.0, 40.0, 30.0, 20.0, 10.0, 0.0, (10.0) |
| f2 | `compound` | vertical | 1 | 2 | 11 | 22 | 全部 | 30.0, 20.0, 10.0, 0.0, (10.0), (20.0) |

- **f1** Regions/Styles　[图上方]　（标题里没有单位）
- **f2** S&P 500 Sectors　[图上方]　（标题里没有单位）
  - 来源行：Source: FactSet as of 5/31/25. Expected EPS Growth is defined as the expected % change in the EPS growth from the beginning of the current calendar year though the end of the calendar year. 2024 EPS Growth is defined as the % change in EPS from the beginning of the year through the end of the year. Data provided is for informational use only. See end of report for important additional information. Forecasts/estimates are based on current market conditions, subject to change, and may not necessarily come to pass.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | pink bars for Expected EPS Growth with grey circular markers for 2024 EPS Growth in same panel |
| `mixed_marks` | 同面板混合图元（bar + line） | f2 | 有 | pink bars plus grey dot markers, e.g. dot at -13.03 over Energy bar |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f2 | **无** | a horizontal rule drawn at 0.0 across the plot with bars crossing it |
| `negative_values` | 负值 / 零线居中的分叉条 | f2 | **无** | Energy bar reaches -13.03 below the zero line; ticks read (10.0), (20.0) |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separate charts headed 'Regions/Styles' and 'S&P 500 Sectors' on one page |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | 'Source: FactSet as of 5/31/25...' small print below the lower chart |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | legend swatches 'Expected EPS Growth' / '2024 EPS Growth' sit at top right over plot area |
| `legend_inside_plot` | 图例画在绘图区内部 | f2 | **无** | legend at top right inside plot region above the bars |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | page | 有 | bold headings 'Regions/Styles' and 'S&P 500 Sectors' above each chart |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '33.37' printed above the Russell 2000 bar top, '1.31' beside its grey dot |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | '17.59' above Info. Tech. bar, '-10.24' left of the Materials grey dot |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f2 | 有 | category labels abbreviated: 'Info. Tech.', 'Discretionary', 'Staples' |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | negative axis ticks printed in parentheses style '(10.0)' rather than '-10.0' |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 'MSCI World ex USA Small Cap' and 'Russell 1000 Growth' wrap onto two lines |

词表 65 项，本页出现 11 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `parenthesized_negative_ticks` | f1 | value axis prints '(10.0)' for minus ten, accounting-style parentheses | 读负值刻度时需知道括号代表负号，否则会把(10.0)误读为正10，进而错判柱高与零线位置。 |
| `overlapping_value_labels` | f1 | '18.22' and '12.85' nearly touch at MSCI EM; '0.15','3.02','0.50' collide with axis | 两个系列的数字标签互相挤压，取值时必须靠颜色（粉/灰）区分归属，容易把点值与柱值配错。 |
| `point_series_label_color_coded` | f2 | grey labels ('23.85','18.74','16.84','2.17') belong to dots, pink labels to bars | 标签的颜色是唯一的系列归属线索，解析成表格时若丢失颜色，就无法判断该数属于哪一系列。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

所有10个待查值都直接印在图上，读数不是问题（步骤2无压力）；难点在寻址：每个值需要三层标签——图标题（Regions/Styles 或 S&P 500 Sectors）、类别名（如 MSCI World ex USA Small Cap）、系列名（Expected EPS Growth 还是 2024 EPS Growth）。两图共用同一对系列名，且 S&P 500 同时作为 f1 的一个类别和 f2 标题中的词，若表格缺少图级标题这一层，'S&P 500' 一行的 9.22 与 f2 各行会互相混淆；此外 f1 中 18.22/12.85、0.15/3.02/0.50 等粉灰标签几乎连写，解析器容易把点值与柱值串到同一单元格，使系列这一维丢失。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | tick_marker_as_series 的替代形式：point_overlay_on_bars（柱上叠加点标记系列）应作为独立风格维度纳入生成器 | 图表族条件行中新增 bar+point overlay 组合，style 字段增加 marker_shape 与 marker_color | 叠加点系列 vs 纯分组柱：在同一类别下模型区分两系列数值的准确率 |
| P6 | 一类出版方 | parenthesized_negative_ticks（会计式括号负号刻度格式） | 刻度格式化字段 tick_format 增加 accounting_parentheses 选项，与负值/零线维度联动 | 负值刻度写作 (10.0) 与 -10.0 时的取值符号错误率 |
| P6 | 这份文档自己的习惯 | overlapping_value_labels / 按颜色区分系列的数据标签（point_series_label_color_coded） | 标签布局字段：允许两系列标签在同一水平带内重叠，并以系列色着色 | 标签重叠且仅靠颜色区分系列时，系列归属判定的正确率 |
| P7 | 通用 | panel_title_per_panel 与图级标题作为独立字段（同页两图共用相同系列名） | 记录字段中将小标题（Regions/Styles、S&P 500 Sectors）提升为 heading.title，并在导出 markdown 时置于表格上方加粗 | 同页多图共用系列名时，标题是否写入表上方对寻址成功率的影响 |
