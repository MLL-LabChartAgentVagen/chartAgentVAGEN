# 2025-EIS_p59

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2025-EIS | `untagged` | 10 | 0 |

本页为《European Innovation Scoreboard 2025》第57页，含一段正文与Figure 22：按创新维度分组的四类创新群体水平分组条形图，附图例与注释。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 141 | `Human resources` · `Innovation leaders` | 1% | f1 | the Human resources bar for Innovation leaders (topmost bar in that slot) | 是 | `Human resources` · `Innovation leaders` · `Adjusted score per dimension in 2025` |
| 2 | 42 | `Attractive research systems` · `Emerging innovators` | 1% | f1 | the Attractive research systems bar for Emerging innovators (bottom bar in that slot) | 是 | `Attractive research systems` · `Emerging innovators` |
| 3 | 102 | `Digitalisation` · `Strong innovators` | 1% | f1 | the Digitalisation bar for Strong innovators | 是 | `Digitalisation` · `Strong innovators` |
| 4 | 77 | `Finance and support` · `Moderate innovators` | 1% | f1 | the Finance and support bar for Moderate innovators | 是 | `Finance and support` · `Moderate innovators` |
| 5 | 144 | `Firm investments` · `Innovation leaders` | 1% | f1 | the Firm investments bar for Innovation leaders | 是 | `Firm investments` · `Innovation leaders` |
| 6 | 70 | `Investments in information technologies` · `Emerging innovators` | 1% | f1 | the Investments in information technologies bar for Emerging innovators | 是 | `Investments in information technologies` · `Emerging innovators` |
| 7 | 111 | `Innovators` · `Moderate innovators` | 1% | f1 | the Innovators bar for Moderate innovators | 是 | `Innovators` · `Moderate innovators` |
| 8 | 126 | `Linkages` · `Strong innovators` | 1% | f1 | the Linkages bar for Strong innovators | 是 | `Linkages` · `Strong innovators` |
| 9 | 72 | `Intellectual assets` · `Emerging innovators` | 1% | f1 | the Intellectual assets bar for Emerging innovators | 是 | `Intellectual assets` · `Emerging innovators` |
| 10 | 122 | `Sales and employment impacts` · `Innovation leaders` | 1% | f1 | the Sales and employment impacts bar for Innovation leaders (also Trade impacts Innovation leaders = 122, and Firm investments Strong innovators = 122) | 是 | `Sales and employment impacts` · `Innovation leaders` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | horizontal | 1 | 4 | 12 | 48 | 全部 | 0, 20, 40, 60, 80, 100, 120, 140, 160 |

- **f1** Figure 22 / Innovation performance of the innovation groups per dimension　[图上方]　单位 `Adjusted score per dimension in 2025`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | four bars per dimension slot, one per innovation group, e.g. 141/119/85/54 for Human resources |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | dimension names sit on the left axis and bars grow rightwards to the 0-160 scale |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Average scores for each performance group are defined as the unweighted average...' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | colour keys 'Emerging innovators ... Innovation leaders' in a row under the axis title |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | 'Adjusted score per dimension in 2025' under the axis; ticks are bare 0-160 |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | 'Adjusted score per dimension in 2025' set below the 0-160 tick row |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | note: 'adjusted such that the unweighted average of the four groups for each dimension equals 100' |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | numbers such as '151', '124', '83', '42' printed just past each bar end |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | long left-axis labels like 'Investments in information technologies', 'Resource and labour productivity' |

词表 65 项，本页出现 9 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `reversed_series_order_vs_legend` | f1 | bars within a slot run Innovation leaders (top) to Emerging innovators (bottom); legend lists the reverse order | 读值时若按图例顺序对应条形会错位，需按从上到下的实际绘制顺序把141归给Innovation leaders而非Emerging innovators。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

所有48个值都直接打印在条端，读数不成问题（步骤2无阻）；难点在寻址：一个值需要“维度名+群体名”两个键，而12×4的表必须同时给出12个长行名与4个列名；更关键的是122在图中出现三次（Sales and employment impacts/Innovation leaders、Trade impacts/Innovation leaders、Firm investments/Strong innovators），105、85、122、119等数字重复，若表格行列标签缺失或系列顺序按图例反排，就无法把122唯一定位到某一条。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新增 reversed_series_order_vs_legend（图例顺序与条形绘制顺序相反） | 在样式条件行中加入 series_draw_order 字段（与 legend_order 可独立取值） | 图例顺序=绘制顺序 vs 图例顺序反转，比较系列归属正确率 |
| P7 | 一类出版方 | unit_in_axis_or_title + axis_title_below_plot（单位短语作为轴下标题） | 标题记录字段：unit_text 与 unit_position=below_axis | 单位置于标题内 vs 置于轴下独立行时，导出表是否保留单位 |
| P3 | 通用 | horizontal_bars 搭配长换行类别标签（wrapped_category_labels） | 类别轴样式行：label_wrap=on，bar_direction=horizontal | 短代码类别轴 vs 12个长换行类别名的行名匹配率 |
| P6 | 通用 | value_label_outside 全量标注（12×4=48个数字）+ 重复值消歧 | 记录字段：value_label_placement=outside，并要求导出表带行列双键 | 值唯一 vs 值重复（122出现3次）时的定位准确率 |
