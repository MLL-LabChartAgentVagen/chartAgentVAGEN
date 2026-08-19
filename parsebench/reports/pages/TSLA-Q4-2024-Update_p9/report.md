# TSLA-Q4-2024-Update_p9

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| TSLA-Q4-2024-Update | `need_estimate` | 10 | 10 |

这一页左侧是「VEHICLE CAPACITY」栏目的正文段落，右侧上方是一张「Current Installed Annual Vehicle Capacity」产能表格，下方是一张标题写在图下的三系列季度折线图「Market share of Tesla vehicles by region (TTM)」。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 1.1 | `US/Canada` · `Q1 2019` | 5% | f2 | the US/Canada point at Q1 2019 (line starts just above the 1% gridline) | 否 | `Market share of Tesla vehicles by region (TTM)` · `US/Canada` · `Q1 2019` |
| 2 | 4.0 | `US/Canada` · `Q4 2023` | 5% | f2 | the US/Canada peak point at Q4 2023, touching the 4% gridline | 否 | `Market share of Tesla vehicles by region (TTM)` · `US/Canada` · `Q4 2023` |
| 3 | 3.7 | `US/Canada` · `Q4 2024` | 5% | f2 | the last US/Canada point, Q4 2024 | 否 | `Market share of Tesla vehicles by region (TTM)` · `US/Canada` · `Q4 2024` |
| 4 | 0.4 | `Europe` · `Q1 2019` | 30% | f2 | the first Europe point at Q1 2019, just under the halfway mark between 0% and 1% | 否 | `Market share of Tesla vehicles by region (TTM)` · `Europe` · `Q1 2019` |
| 5 | 2.6 | `Europe` · `Q1 2024` | 10% | f2 | the Europe point on the post-peak decline, Q2 2024 | 否 | `Market share of Tesla vehicles by region (TTM)` · `Europe` · `Q2 2024` |
| 6 | 2.5 | `Europe` · `Q4 2024` | 5% | f2 | the last Europe point, Q4 2024 | 否 | `Market share of Tesla vehicles by region (TTM)` · `Europe` · `Q4 2024` |
| 7 | 0.1 | `China` · `Q1 2019` | 5% | f2 | the first China point at Q1 2019, hugging the 0% baseline | 否 | `Market share of Tesla vehicles by region (TTM)` · `China` · `Q1 2019` |
| 8 | 1.5 | `China` · `Q1 2022` | 10% | f2 | the China point at Q3 2021, midway between the 1% and 2% gridlines | 否 | `Market share of Tesla vehicles by region (TTM)` · `China` · `Q3 2021` |
| 9 | 2.4 | `China` · `Q4 2024` | 10% | f2 | the last China point, Q4 2024 | 否 | `Market share of Tesla vehicles by region (TTM)` · `China` · `Q4 2024` |
| 10 | 1.5 | `US/Canada` · `Q1 2021` | 10% | f2 | the Europe point at Q3 2021, where Europe and China cross near 1.5% | 否 | `Market share of Tesla vehicles by region (TTM)` · `Europe` · `Q3 2021` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 2.6, 1.5, 1.5

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `other · data table` | na | 1 | 4 | 9 | 36 | 全部 | （不画值轴） |
| f2 | `line` | vertical | 1 | 3 | 24 | 72 | 无 | 0%, 1%, 2%, 3%, 4% |

- **f1** Current Installed Annual Vehicle Capacity　[图上方]　（标题里没有单位）
- **f2** Market share of Tesla vehicles by region (TTM)　[图下方]　（标题里没有单位）
  - 来源行：Source: Tesla estimates based on latest available data from ACEA; Autonews.com; CAAM – light-duty vehicles only; TTM = Trailing twelve months_placeholder

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | f1 | **无** | Capacity cells read "-" for Cybercab, Tesla Semi and Roadster |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately captioned figures: capacity table and "Market share of Tesla vehicles by region (TTM)" chart |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | grey small print below table: "Installed capacity ≠ current production rate and there may be limitations..." |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | "Source: Tesla estimates based on latest available data from ACEA; Autonews.com; CAAM..." under the title |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f1 | 有 | grey header band "Region \| Model \| Capacity \| Status" over nine banded data rows, captioned above |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f2 | 有 | "US/Canada  Europe  China" line-key row sits between the table note and the 4% tick |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | left column prose "US: California, Nevada and Texas", "APAC: Shanghai" runs level with both figures |
| `rotated_x_ticks` | x 刻度标签旋转 | f2 | 有 | "Q1 2019" ... "Q4 2024" set at about 45 degrees under the axis |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f2 | **无** | time labelled as "Q1 2019", "Q4 2024" rather than ISO dates |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | faint horizontal rules at 1%, 2%, 3%, 4%; no vertical rules in the plot |

词表 65 项，本页出现 9 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `implicit_row_group_blank_cell` | f1 | Region cell empty on the "Model 3 / Model Y", "Cybertruck", "Cybercab" rows, inheriting California/Texas above | 取值时行的地区键不在本行，必须向上继承，否则 >550,000 与 >125,000 无法被唯一定位。 |
| `inequality_prefixed_values` | f1 | Capacity cells print ">550,000", ">950,000", ">375,000", ">250,000", ">125,000" | 数值带「>」前缀，纯数字匹配会失配，读数必须连同符号一起当作字符串处理。 |
| `bold_column_emphasis` | f1 | whole Model column set bold ("Model S / Model X", "Cybertruck"), Region and Status columns regular | 加粗只标示列而非某一行的重要性，解析成标题式强调会误判哪一列是行名。 |
| `figure_title_below_plot` | f2 | bold "Market share of Tesla vehicles by region (TTM)" printed under the rotated quarter ticks | 图题在图下且紧接 Source 行，markdown 里标题会落在表格之后，值与图名的绑定顺序颠倒。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

被评分的十个数全部来自 f2 折线图，且图上不印任何数值：y 轴只有 0%、1%、2%、3%、4% 五个刻度，1% 约占 47 像素，1 像素≈0.02 个百分点。对 0.1 这种小值，5% 容差只有 ±0.005，远小于线宽（线本身约 3 像素≈0.06），像素上根本不可能达标；0.4 的容差 ±0.02 也只有一个像素级别。24 个季度 × 3 条线共 72 个点密集重叠，Q3 2021 附近 Europe 与 China 交叉，连点归属都要靠颜色区分。相比之下寻址只需两个键（系列名 + 季度），f1 的数字全部印出反而容易，所以卡住的是从像素读值这一步。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P3 | 通用 | 新组件 implicit_row_group_blank_cell（表格中空白的分组单元格继承上一行） | 表格类图形的记录字段：为每行增加 group_key（继承得到的 Region）并在渲染时留空该单元格 | 「分组列留空 vs 每行重复分组值」对行寻址正确率的影响 |
| P7 | 一类出版方 | 新组件 figure_title_below_plot（图题置于绘图区下方，紧接 Source 行） | 标题样式字段 heading.placement 增加 below 并允许 legend_above_plot 同时出现 | 「标题在上 vs 标题在下」对 markdown 导出中值与图名绑定的影响 |
| P6 | 一类出版方 | 新组件 inequality_prefixed_values（>550,000 这类带符号数值） | 数值标签格式化字段：允许前缀符号（>、<、~）与千位分隔 | 「带前缀符号的数值 vs 纯数字」对数值字符串匹配命中率的影响 |
| P6 | 通用 | nonstandard_time_ticks + rotated_x_ticks（Q1 2019…Q4 2024 斜排 24 个季度刻度） | 时间轴刻度格式与旋转角度的样式维度 | 「季度式非 ISO 刻度 + 45° 旋转」对时间类别键抽取的影响 |
| P1 | 通用 | 每点可达精度（针对 0%–4% 轴上 0.1 这类小值） | readable 判定从布尔门改为按 mark 给出容差，纳入线宽与刻度间距 | 「小值点（<0.5%）在 1% 刻度间距下的可达精度」单独一行 |
