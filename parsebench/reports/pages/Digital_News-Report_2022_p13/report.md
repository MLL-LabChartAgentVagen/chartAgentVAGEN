# Digital_News-Report_2022_p13

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Digital_News-Report_2022 | `untagged` | 3 | 0 |

这是路透研究所《Digital News Report 2022》第13页,左栏为12个市场2017/2019/2022选择性回避新闻比例的水平分组条形图(含中央甜甜圈式平均值标注),右栏为以图标呈现的六个回避原因百分比图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 54 | `Brazil` · `2022` | 1% | f1 | the Brazil 2022 bar (longest, magenta) | 是 | `Brazil` · `2022` · `PROPORTION WHO SOMETIMES OR OFTEN ACTIVELY AVOID THE NEWS (2017–22) – SELECTED MARKETS` |
| 2 | 35 | `UK` · `2019` | 1% | f1 | the UK 2019 bar (orange), also the Spain 2022 bar reads 35 | 是 | `UK` · `2019` · `PROPORTION WHO SOMETIMES OR OFTEN ACTIVELY AVOID THE NEWS (2017–22) – SELECTED MARKETS` |
| 3 | 24 | `Germany` · `2017` | 1% | f1 | the UK 2017 bar (teal); the Germany 2017 bar also reads 24 | 是 | `UK` · `2017` · `PROPORTION WHO SOMETIMES OR OFTEN ACTIVELY AVOID THE NEWS (2017–22) – SELECTED MARKETS` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 3 predicted key sets miss a rule label: 24

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | horizontal | 1 | 3 | 12 | 36 | 全部 | 0%, 25%, 50%, 75% |
| f2 | `other · icon percentage grid` | na | 1 | 1 | 6 | 6 | 全部 | （不画值轴） |

- **f1** PROPORTION WHO SOMETIMES OR OFTEN ACTIVELY AVOID THE NEWS (2017–22) – SELECTED MARKETS　[图上方]　（标题里没有单位）
  - 来源行：Q1di_2017. Do you find yourself actively trying to avoid news these days? Base: Total 2017–22 samples (n=2000).
- **f2** MOST COMMON REASONS FOR NEWS AVOIDANCE – ALL MARKETS　[图上方]　（标题里没有单位）
  - 来源行：Q1di_2017ii. Why do you find yourself actively trying to avoid the news? Base: All who avoid the news often, sometimes, or occasionally. All markets = 64,120.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | three bars (2017, 2019, 2022) side by side in each country slot |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names on the left axis, bars grow rightwards to 0%–75% scale |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | donut ring with "38% All country average (was 29% in 2017)" drawn over the plot |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | only printed percentages 43%, 36%, 29%, 29%, 17%, 16%; no ticks or baseline |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separate captioned figures with own Q1di_2017 and Q1di_2017ii note lines |
| `source_note_lines` | source / note 行在图下方 | page | 有 | "Q1di_2017. Do you find yourself..." and "Q1di_2017ii. Why do you find yourself..." under each figure |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | 2017 / 2019 / 2022 swatches drawn at top right within the plot area |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | right column body text and pull quotes run level with the left-column bar chart |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | question codes "Q1di_2017." and "Q1di_2017ii." set bold before each note |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | numbers 27, 34, 54 printed in white at the right end inside each bar |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f2 | **无** | labels like "say there is nothing I can do with the information" wrap onto three lines |
| `icon_category_axis` | 类目轴用图标代替文字 | f2 | **无** | pictograms (virus, mood face, arguing heads) sit above each percentage label |

词表 65 项，本页出现 12 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `donut_average_badge` | f1 | a ring gauge inside the plot reading "38% All country average (was 29% in 2017)" | 该平均值不属于任何国家条形,读取时须作为独立聚合标记处理,否则会被误配到相邻的Italy/Germany行。 |
| `icon_stat_callout_grid` | f2 | 2×3 grid of icon + large coloured percentage + descriptive caption, no axis | 数值只能从印刷文字取得,表格必须以文字描述作行名,无法用类别轴或刻度定位。 |
| `series_color_per_stat` | f2 | each percentage printed in its own colour (teal, orange, magenta, navy, green, red) | 颜色不编码任何变量,若误当作系列会把六个独立统计错并为一个系列。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部印在条内(54、35、24),读数没有风险;刻度只有0%、25%、50%、75%四格也不必用。真正的障碍是定址:35同时出现在UK 2019与Spain 2022,24同时出现在UK 2017与Germany 2017,单靠数字无法唯一定位,必须同时携带国家名与年份两个键;而年份仅存在于绘图区内部的图例色块中,解析器若丢掉图例,三列就退化为无名列,任何一行都无法排除同值的另一格。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P3 | 一类出版方 | legend_inside_plot(绘图区内图例)作为系列名来源的独立条件 | 样式字段中图例位置维度增加 inside 取值,并要求导出时把图例文本写入表头 | 图例位于绘图区内 vs 位于图外时,分组条形图系列名可被正确解析的比例 |
| new | 这份文档自己的习惯 | 新组件 donut_average_badge(绘图区内的聚合环形标注) | 记录字段中新增“非类别聚合标记”条目,与普通类别行分开存放 | 含内嵌聚合标注的图表中,该聚合值被误并入相邻类别行的比例 |
| P4 | 一类出版方 | 新组件 icon_stat_callout_grid(图标+大字百分比网格) | 图表族权重向量中新增该无轴统计网格族 | 无值轴、仅有印刷数字的图标统计网格是否被生成为表格的比例 |
| P6 | 通用 | value_label_inside 与百分号刻度格式(0%, 25%, 50%, 75%)组合 | 样式维度中的数值标签位置与刻度格式两项 | 标签在条内且刻度带%时,数值与单位是否被同时保留 |
| P7 | 这份文档自己的习惯 | 无编号图的标题/副标题字段拆分(全大写两行标题) | 标题记录字段:figure_number 允许为空,title 允许跨两行 | 无编号但有全大写多行标题的图,标题是否以粗体或标题级文本落在表格上方 |
