# (Web_version)_E-Government_Survey_2024_1392024_p172

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| (Web_version)_E-Government_Survey_2024_1392024 | `untagged` | 5 | 0 |

本页为报告第147页，包含正文段落与一幅编号为 Figure 4.10 的横向分组条形图，比较2022与2024年城市门户网站服务提供指标的实施率。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 51% | `Waste and recycling information` · `2024` | 1% | f1 | the `Waste and recycling information` 2024 (orange) bar, top row | 是 | `Waste and recycling information` · `2024` |
| 2 | 47% | `Public tranportation information` · `2022` | 1% | f1 | the `Public tranportation information` 2022 (blue) bar | 是 | `Public tranportation information` · `2022` |
| 3 | 42% | `Online tax declaration` · `2024` | 1% | f1 | ambiguous: printed both for `Procurement platform` 2024 and `Online tax declaration` 2024 | 是 | `Procurement platform` · `2024` |
| 4 | 24% | `Online police declaration` · `2022` | 1% | f1 | ambiguous: `Online police declaration` 2022 bar and `Online marriage certificate` 2024 bar both read 24% | 是 | `Online police declaration` · `2022` |
| 5 | 12% | `Online vehicle registration` · `2024` | 1% | f1 | the `Online vehicle registration` 2024 (orange) bar, bottom row | 是 | `Online vehicle registration` · `2024` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 5 predicted key sets miss a rule label: 42%

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | horizontal | 1 | 2 | 22 | 44 | 全部 | 0%, 10%, 20%, 30%, 40%, 50% |

- **f1** Figure 4.10 / Implementation of services provision indicators in city portals　[图上方]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | two bars per row, blue `2022` above orange `2024`, in each indicator slot |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | indicator names on the y axis, bars grow rightwards to the 0%-50% axis |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | `2022` and `2024` swatches printed under the 0%-50% axis line |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis ticks themselves carry `%`: `0%, 10%, ... 50%` |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | `48%`, `51%` printed just beyond each bar end, e.g. top two rows |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 22 long labels stacked down the y axis, e.g. `Online environment-related permit` |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | vertical dotted rules at 10%, 20%, 30%, 40%, 50%; no horizontal rules |

词表 65 项，本页出现 7 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `percent_sign_on_ticks_and_labels` | f1 | every tick and every value label ends in `%`: `0%`...`50%`, `48%`, `12%` | 数值本身自带百分号，解析后文本为 `51%` 而非 `51`，检索时必须匹配带百分号的形式。 |
| `figure_caption_rule_bar` | f1 | a solid blue horizontal bar drawn between the caption line and the plot frame | 标题块与绘图区之间的装饰条可能被解析为分隔元素，影响标题与表格的归属判断。 |
| `plot_frame_box` | f1 | a thin rectangular border encloses the whole plot, labels and legend | 外框可能被误判为表格边界，使图形被当作表格结构提取。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值全部印在图上，读数不构成障碍（步骤2容易）；真正的瓶颈是定位：22个类别×2个年份共44个标记，而42%、24%、27%、21%、38%等数字在图中重复出现2次以上，因此每个值必须同时携带完整的指标名（如 `Online police declaration`）和年份列（`2022`/`2024`）才能唯一定位。若解析器只输出一列数字或把两年份合并，检索到的 42% 无法区分 Procurement platform 与 Online tax declaration。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P5 | 通用 | grouped_bar 与 horizontal_bars 组合下的高类别数（22行×2系列）生成条件 | 条件行中的 categories 上限与 orientation=horizontal 组合，marks 提升至44 | 新增一行：横向分组条形，类别数≥20，考察行标签唯一寻址成功率 |
| P6 | 一类出版方 | value_label_outside 且标签带百分号的样式维度 | style 字段中的 value-label 位置与 tick 格式（`0%`形式） | 新增一行：刻度与数值标签是否附带单位符号，对检索匹配率的影响 |
| P7 | 通用 | figure 标题块（`Figure 4.10` + 标题）作为独立字段并置于表格上方为粗体标题 | record 的 heading 字段拆分（number/title/unit/placement=above） | 新增一行：标题以粗体标题行输出 vs 仅存于图内，考察上下文命中率 |
| P6 | 一类出版方 | vgrid_only（横向条形常见的纵向网格）作为样式选项 | style 字段的网格方向开关 | 新增一行：网格方向与条形方向匹配/不匹配时的读数误差 |
