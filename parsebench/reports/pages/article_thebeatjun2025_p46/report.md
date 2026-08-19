# article_thebeatjun2025_p46

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| article_thebeatjun2025 | `untagged` | 10 | 0 |

这是摩根士丹利《The BEAT》2025年6月刊第46页，标题为“Local Sovereign Currency Yields”，页面并列两幅水平分组条形图，分别列出发达市场与新兴市场本币1年期利率的当前值与一年前值。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 4.12 | `U.S. Dollar (USD)` · `Current` | 1% | f1 | the U.S. Dollar (USD) `Current` bar | 是 | `Developed Market Local Interest Rates % (1 Year)` · `U.S. Dollar (USD)` · `Current` |
| 2 | 5.11 | `U.S. Dollar (USD)` · `1 Yr Prior` | 1% | f1 | the U.S. Dollar (USD) `1 Yr Prior` bar | 是 | `Developed Market Local Interest Rates % (1 Year)` · `U.S. Dollar (USD)` · `1 Yr Prior` |
| 3 | 3.83 | `British Pound (GBP)` · `Current` | 1% | f1 | the British Pound (GBP) `Current` bar | 是 | `Developed Market Local Interest Rates % (1 Year)` · `British Pound (GBP)` · `Current` |
| 4 | 5.02 | `New Zealand Dollar (NZD)` · `1 Yr Prior` | 1% | f1 | the New Zealand Dollar (NZD) `1 Yr Prior` bar | 是 | `Developed Market Local Interest Rates % (1 Year)` · `New Zealand Dollar (NZD)` · `1 Yr Prior` |
| 5 | -0.27 | `Swiss Franc (CHF)` · `Current` | 1% | f1 | the Swiss Franc (CHF) `Current` bar, extending left of the zero line | 是 | `Developed Market Local Interest Rates % (1 Year)` · `Swiss Franc (CHF)` · `Current` |
| 6 | 42.67 | `Turkish New Lira (TRY)` · `Current` | 1% | f2 | the Turkish New Lira (TRY) `Current` bar | 是 | `Emerging Market Local Interest Rates % (1 Year)` · `Turkish New Lira (TRY)` · `Current` |
| 7 | 20.70 | `Nigerian Naira (NGN)` · `1 Yr Prior` | 1% | f2 | the Nigerian Naira (NGN) `1 Yr Prior` bar | 是 | `Emerging Market Local Interest Rates % (1 Year)` · `Nigerian Naira (NGN)` · `1 Yr Prior` |
| 8 | 11.34 | `Mexican Peso (MXN)` · `1 Yr Prior` | 1% | f2 | the Mexican Peso (MXN) `1 Yr Prior` bar | 是 | `Emerging Market Local Interest Rates % (1 Year)` · `Mexican Peso (MXN)` · `1 Yr Prior` |
| 9 | 7.91 | `South African Rand (ZAR)` · `Current` | 1% | f2 | the South African Rand (ZAR) `Current` bar | 是 | `Emerging Market Local Interest Rates % (1 Year)` · `South African Rand (ZAR)` · `Current` |
| 10 | 1.54 | `Thai Baht (THB)` · `Current` | 1% | f2 | the Thai Baht (THB) `Current` bar | 是 | `Emerging Market Local Interest Rates % (1 Year)` · `Thai Baht (THB)` · `Current` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | horizontal | 1 | 2 | 11 | 22 | 全部 | -5.00, 0.00, 5.00, 10.00, 15.00 |
| f2 | `grouped_bar` | horizontal | 1 | 2 | 14 | 28 | 全部 | 0.00, 10.00, 20.00, 30.00, 40.00, 50.00 |

- **f1** Developed Market Local Interest Rates % (1 Year)　[图上方]　单位 `%`
  - 来源行：It is not possible to invest directly in an index. *German Rate. Source: Bloomberg as 5/31/25. Data provided is for informational use only. See end of report for important additional information.
- **f2** Emerging Market Local Interest Rates % (1 Year)　[图上方]　单位 `%`
  - 来源行：It is not possible to invest directly in an index. *German Rate. Source: Bloomberg as 5/31/25. Data provided is for informational use only. See end of report for important additional information.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | two bars per currency, grey `Current` above blue `1 Yr Prior` |
| `grouped_bar` | 分组条 | f2 | 有 | two bars per currency, grey `Current` above blue `1 Yr Prior` |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | vertical zero rule at 0.00 from which bars run both directions |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | Swiss Franc (CHF) Current bar reads -0.27 and extends left of 0.00 |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | currency names on the y axis, bars grow rightward from 0.00 |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f2 | **无** | currency names on the y axis, bars grow rightward from 0.00 |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately titled charts side by side: Developed Market and Emerging Market |
| `source_note_lines` | source / note 行在图下方 | page | 有 | `Past performance is no guarantee of future results.` and `Source: Bloomberg as 5/31/25.` below the plots |
| `per_panel_legend` | 每个面板各有一个图例 | page | 有 | each of the two charts carries its own `Current / 1 Yr Prior` legend |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | `Current  1 Yr Prior` swatches sit between the title and the plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f2 | 有 | `Current  1 Yr Prior` swatches sit between the title and the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title reads `Developed Market Local Interest Rates % (1 Year)`; ticks are bare `-5.00, 0.00...` |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f2 | **无** | title reads `Emerging Market Local Interest Rates % (1 Year)`; ticks are bare `0.00, 10.00...` |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | `Euro (EUR) *` carries an asterisk explained as `*German Rate.` |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | `4.12`, `5.11` printed beyond each bar end, right of the tip |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | `42.67`, `40.18` printed to the right of each bar end |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | codes in the labels: `(USD)`, `(NOK)`, `(GBP)`, `(CHF)` |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f2 | 有 | codes in the labels: `(TRY)`, `(NGN)`, `(BRL)`, `(THB)` |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f2 | **无** | 14 long labels such as `South African Rand (ZAR)` stacked down the axis |

词表 65 项，本页出现 13 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `panel_pair_shared_note` | page | single note block `*German Rate. Source: Bloomberg as 5/31/25.` serves both charts | 来源与脚注只出现一次，读某一图的数值时必须跨图借用脚注（如 EUR 的 *German Rate），表格行需外挂共享注释。 |
| `unsorted_axis_by_value_descending` | f1 | currencies ordered by Current value from 4.12 down to -0.27, not alphabetically | 类别顺序本身编码了排名信息，抽取表格若重排行序会丢失“按当前利率降序”的语义。 |

## 5 · 难在哪

卡在 **第四步 · 表外上下文**。

所有25个数值都以文字形式印在条端（4.12、5.11 … 1.54），像素读数几乎不构成障碍，5%容差远宽于需求；行标签也只需“货币名+Current/1 Yr Prior”两级即可唯一定位。真正卡住的是上下文：两图共用同一组图例名 Current 与 1 Yr Prior，且发达/新兴市场无编号，只有 `Developed Market Local Interest Rates % (1 Year)` 与 `Emerging Market Local Interest Rates % (1 Year)` 两行粗体小标题位于表格之外；若解析器不把这两行导出为标题或粗体，5.02 与 5.03（CLP Current）、4.26/4.29 这类跨图近似值就无法区分归属，同时 `%` 单位也只藏在这两行标题里。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 通用 | unit_in_axis_or_title 与图标题字段化（number/title/subtitle/unit/placement 分离） | 记录层的 heading 字段：把 `Developed Market Local Interest Rates % (1 Year)` 拆为 title 与 unit_text `%` | 新增“标题携带单位 vs 轴上标注单位”对照行，检验去掉标题后数值单位是否仍可恢复 |
| P2 | 一类出版方 | 多图同页且图例名重复时的 panel/figure 键 | 条件行：同页两图共用 series 名 Current / 1 Yr Prior，key 中必须含图标题 | 新增“同页重复图例名”行，比较带图键与不带图键时定位准确率 |
| P6 | 一类出版方 | negative_values 与零线（CHF -0.27 越过 0.00 向左） | 样式维度：横向条形图的零线位置与负值标签置于条外左侧 | 新增“含负值横条 vs 全正值横条”行，检验负号是否在导出表中保留 |
| P6 | 通用 | value_label_outside 的横向条端标注格式（两位小数，无%号） | 样式字段：标签位置=条端外侧，数字格式=0.00 | 新增“标签外置且轴刻度为 0.00/10.00 格式”行，考察标签与刻度格式一致性 |
| P3 | 这份文档自己的习惯 | new_components 中的 panel_pair_shared_note（脚注 `*German Rate.` 跨图共享） | 页面级导出：把共享注释与两图表格建立关联 | 新增“脚注标记跨图共享 vs 每图独立脚注”行 |
