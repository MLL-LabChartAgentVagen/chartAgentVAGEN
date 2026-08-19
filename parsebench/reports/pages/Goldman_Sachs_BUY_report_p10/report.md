# Goldman_Sachs_BUY_report_p10

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Goldman_Sachs_BUY_report | `untagged` | 10 | 0 |

页面为投资研究报告的"Strategic direction"章节，正文讨论高盛业务结构，中部为Exhibit 3的百分比堆叠柱状图"Historical revenue mix"，展示FY 2010A–FY 2015A六个财年六类业务收入占比。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 13% | `Investment management` · `FY 2010A` | 1% | f1 | the FY 2010A Investment management segment (top, dark green) | 是 | `Historical revenue mix` · `FY 2010A` · `Investment management` |
| 2 | 7% | `Investing and lending` · `FY 2011A` | 1% | f1 | ambiguous: FY 2010A Underwriting bottom segment 7%, FY 2011A Investing and lending 7%, FY 2011A Financial advisory 7%, FY 2014A Financial advisory 7% | 是 | `Historical revenue mix` · `FY 2010A` · `Underwriting` |
| 3 | 24% | `Equities` · `FY 2012A` | 1% | f1 | the FY 2012A FICC segment | 是 | `Historical revenue mix` · `FY 2012A` · `FICC` |
| 4 | 25% | `FICC` · `FY 2013A` | 1% | f1 | the FY 2013A Equities segment (also FY 2014A Equities is 25%) | 是 | `Historical revenue mix` · `FY 2013A` · `Equities` |
| 5 | 7% | `Financial advisory` · `FY 2014A` | 1% | f1 | the FY 2014A Financial advisory segment (repeats elsewhere) | 是 | `Historical revenue mix` · `FY 2014A` · `Financial advisory` |
| 6 | 11% | `Underwriting` · `FY 2015A` | 1% | f1 | the FY 2015A Underwriting segment (bottom, dark navy) | 是 | `Historical revenue mix` · `FY 2015A` · `Underwriting` |
| 7 | 21% | `Equities` · `FY 2010A` | 1% | f1 | the FY 2010A FICC segment (also FY 2013A FICC 21% and FY 2013A Investing and lending 21%) | 是 | `Historical revenue mix` · `FY 2010A` · `FICC` |
| 8 | 12% | `Underwriting` · `FY 2013A` | 1% | f1 | the FY 2013A Underwriting segment (FY 2014A Underwriting is also 12%) | 是 | `Historical revenue mix` · `FY 2013A` · `Underwriting` |
| 9 | 18% | `Investment management` · `FY 2015A` | 1% | f1 | the FY 2015A Investment management segment (top) | 是 | `Historical revenue mix` · `FY 2015A` · `Investment management` |
| 10 | 31% | `FICC` · `FY 2011A` | 1% | f1 | the FY 2011A Equities segment | 是 | `Historical revenue mix` · `FY 2011A` · `Equities` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 10 predicted key sets miss a rule label: 7%, 24%, 25%, 21%, 31%

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 6 | 6 | 36 | 全部 | （不画值轴） |

- **f1** Exhibit 3 / Historical revenue mix　[图上方]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each FY column is one bar split into six coloured segments labelled 13%, 19%, 35%, 21%, 5%, 7% |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f1 | **无** | all six FY bars reach identical height and segment labels sum to 100% per year |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no tick labels along the left edge; only faint horizontal rules and printed percentages |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two rows of legend entries "Underwriting ... Investment management" sit under the FY axis labels |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | percentages such as "31%", "29%", "12%" printed on top of each coloured segment |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | bottom segments "5%"/"7%" and "6%"/"12%" labels are squeezed into very narrow bands |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the figure sits inside a blue-bordered box with the title inset into its top border |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | light horizontal rules cross the plot; no vertical grid lines drawn |

词表 65 项，本页出现 8 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `title_inset_in_frame_border` | f1 | "Historical revenue mix" is set into a gap in the top line of the figure's border box | 标题嵌入边框线中而非独立标题行，解析器可能把它当作框线注释丢失，从而使表格失去图名上下文。 |
| `exhibit_number_separate_from_title` | f1 | "Exhibit 3" is a standalone blue heading above the framed box holding "Historical revenue mix" | 编号与图名被水平分割线分成两块，取值时需同时定位两处才能完整寻址该图。 |
| `no_unit_text_anywhere` | f1 | no "%" axis title or subtitle; scale recoverable only from the in-segment labels | 单位只能由标签自身的百分号推断，若解析器丢掉%号则数值失去量纲。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部印在色块内（13%、31%、11% 等），读数不成问题，也无刻度轴需要插值；但36个色块中重复值极多：7% 出现四次（FY 2010A Underwriting、FY 2011A Financial advisory、FY 2011A Investing and lending、FY 2014A Financial advisory），12%、21%、25%、17% 各出现两到三次，因此任何一个值必须同时携带年份键（FY 2013A）与业务键（Underwriting）两级标签才能唯一寻址；而图上没有值轴、图例分两行置于横轴下方，解析器很容易把六个系列名与年份的对应关系打散，只输出一串裸百分数，使行列标签无法成对。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | pct_stacked 与 no_value_axis 组合（无值轴的百分比堆叠） | 条件行中新增"堆叠且所有标签内嵌、无刻度"的样式组合，记录字段需强制输出 series×category 双键 | 有值轴 vs 完全无值轴的百分比堆叠图，比较取值命中率 |
| P7 | 这份文档自己的习惯 | new_components 中的 title_inset_in_frame_border 与 exhibit_number_separate_from_title | 标题样式字段：图号、图名分离，且图名嵌入边框线 | 图号与图名同处一行 vs 被分割线分离时，图名能否进入表格上下文 |
| P6 | 一类出版方 | thin_segment_label（窄段标签） | 样式字段中标签放置策略：段高<8%时标签仍内嵌并可能重叠 | 窄段标签内嵌 vs 外移引线时的数值可读性 |
| P2 | 通用 | 重复值的多键寻址要求（series+category 必须成对） | 记录字段：为每个 mark 生成 (category_name, series_name) 复合键而非单值 | 含重复数值的图（如 7% 出现四次）在单键 vs 双键寻址下的评分差异 |
