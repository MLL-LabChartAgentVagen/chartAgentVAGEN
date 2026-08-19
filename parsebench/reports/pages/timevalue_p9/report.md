# timevalue_p9

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| timevalue | `need_estimate` | 9 | 9 |

这是一张幻灯片式报告页，标题为"Holding Period and Value"，页面主体是一幅三条折线的图，比较$100投资在不同持有年限下的未来价值（股票、长期国债、短期国库券）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 3850 | `40` · `Stocks ($)` | 5% | f1 | the Stocks ($) point at holding period 40 | 否 | `Stocks ($)` · `40` · `Holding period (in years)` · `Future value of $100 investment` |
| 2 | 1550 | `30` · `Stocks ($)` | 5% | f1 | the Stocks ($) point at holding period 30 | 否 | `Stocks ($)` · `30` · `Holding period (in years)` · `Future value of $100 investment` |
| 3 | 620 | `20` · `Stocks ($)` | 5% | f1 | the Stocks ($) point at holding period 20 | 否 | `Stocks ($)` · `20` · `Holding period (in years)` · `Future value of $100 investment` |
| 4 | 240 | `10` · `Stocks ($)` | 5% | f1 | the Stocks ($) point at holding period 10, just above the baseline | 否 | `Stocks ($)` · `10` · `Holding period (in years)` · `Future value of $100 investment` |
| 5 | 700 | `40` · `Treasury Bonds ($)` | 10% | f1 | the Treasury Bonds ($) point at holding period 40 | 否 | `Treasury Bonds ($)` · `40` · `Holding period (in years)` · `Future value of $100 investment` |
| 6 | 420 | `30` · `Treasury Bonds ($)` | 5% | f1 | the Treasury Bonds ($) point at holding period 30 | 否 | `Treasury Bonds ($)` · `30` · `Holding period (in years)` · `Future value of $100 investment` |
| 7 | 250 | `20` · `Treasury Bonds ($)` | 5% | f1 | the Treasury Bonds ($) point at holding period 20 (could equally be the Treasury Bills ($) point at 30; the two sit within one gridline gap) | 否 | `Treasury Bonds ($)` · `20` · `Holding period (in years)` · `Future value of $100 investment` |
| 8 | 420 | `40` · `Treasury Bills ($)` | 10% | f1 | the Treasury Bills ($) point at holding period 40 | 否 | `Treasury Bills ($)` · `40` · `Holding period (in years)` · `Future value of $100 investment` |
| 9 | 280 | `30` · `Treasury Bills ($)` | 5% | f1 | the Treasury Bills ($) point at holding period 30 | 否 | `Treasury Bills ($)` · `30` · `Holding period (in years)` · `Future value of $100 investment` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 3 | 6 | 18 | 无 | 0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500 |

- **f1** Holding Period and Value　[图上方]　单位 `Future value of $100 investment`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f1 | 有 | "Stocks ($)", "Treasury Bonds ($)", "Treasury Bills ($)" stacked in a column at the right of the plot |
| `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | f1 | **无** | legend entries carry "($)": "Stocks ($)", "Treasury Bonds ($)", "Treasury Bills ($)" |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | y axis reads bare 0..4500; scale word only in axis title "Future value of $100 investment" |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "Future value of $100 investment" set vertically alongside the left value axis |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 500-intervals across the panel, no vertical rules |

词表 65 项，本页出现 5 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `category_axis_title_below_plot` | f1 | "Holding period (in years)" printed in bold under the x tick row | 类别轴的含义（年限）只写在图下方一行，表格若不带这行就无法说明列头"1,5,10..."是年数。 |
| `numeric_categorical_x_axis` | f1 | x ticks 1, 5, 10, 20, 30, 40 drawn at equal spacing though intervals differ | 横轴数值间距不等但等距绘制，不能按线性内插定位点，只能逐个类别读取。 |
| `marker_shape_per_series` | f1 | square markers on Stocks, star markers on Treasury Bonds, x markers on Treasury Bills, repeated in legend | 三线在低值区几乎重叠，只能靠标记形状区分是哪条序列的点。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

最大的障碍是读数精度：值轴每500一格（约52像素），而待核的九个值里有六个小于700，全挤在最低那一格半之内。240的5%容差只有±12，相当于1.2像素；250与280之间只差3像素，三条线在1–20年区间几乎重叠，连区分是Treasury Bonds ($)还是Treasury Bills ($)都要靠标记形状。图上没有任何数值标签，也没有Source行，全部数字必须靠像素对齐横向网格线推算，这比标签寻址（每个值只需序列名+年限两个键）困难得多。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 一类出版方 | unit_in_axis_or_title 与旋转轴标题作为独立的"标题拆分"字段（图号为空、标题来自页眉、单位来自轴标题） | 记录层的heading字段：figure_number/title/subtitle/unit_text/placement，允许figure_number为空且title取自幻灯片标题 | 新增一行：图无编号、单位只出现在旋转的纵轴标题中时，导出表格能否带出量纲 |
| new | 一类出版方 | 新组件 numeric_categorical_x_axis（1,5,10,20,30,40等距绘制） | 条件行中的类别轴生成器：允许数值型不等间距类别按等距摆放 | 新增一行：不等间距数值类别轴与真线性时间轴，对定位单点读数误差的影响对比 |
| P1 | 通用 | 低值区多序列重叠时的可读精度（per-mark attainable precision） | 评分侧的readable判定：按每个标记与网格间距的比值给出可达精度，而非全图布尔门 | 新增一行：标记值小于最小刻度间距一半时，5%容差下的命中率 |
| P6 | 通用 | 新组件 marker_shape_per_series（方块/星形/叉形区分三条线） | 样式字段：line marker shape 作为序列身份编码的一个维度，与颜色并列 | 新增一行：仅靠颜色区分序列 vs 颜色+标记形状区分，重叠线区域的序列归属正确率 |
