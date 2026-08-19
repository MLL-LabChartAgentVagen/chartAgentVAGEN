# SSIF-Visa-Report_p6

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| SSIF-Visa-Report | `need_estimate` | 10 | 10 |

这是一份投资报告第6页，左侧为波特五力与行业趋势正文，右侧配一幅无编号折线图“Payment Instruments Preffered for Payment”，含Cash/Credit/Debit三条2016–2020的百分比序列。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 27% | `Cash` · `2016` | 10% | f1 | the 2016 Cash point (grey line, highest Cash value) | 否 | `Cash` · `2016` · `Payment Instruments Preffered for Payment` |
| 2 | 24% | `Credit` · `2016` | 10% | f1 | the 2017 Cash point | 否 | `Cash` · `2017` · `Payment Instruments Preffered for Payment` |
| 3 | 42% | `Debit` · `2016` | 5% | f1 | the 2016 Debit point (flat top navy line) | 否 | `Debit` · `2016` · `Payment Instruments Preffered for Payment` |
| 4 | 24% | `Cash` · `2017` | 10% | f1 | the 2016 Credit point (navy line starting just below Cash) | 否 | `Credit` · `2016` · `Payment Instruments Preffered for Payment` |
| 5 | 29% | `Credit` · `2017` | 10% | f1 | the 2017 Credit point (also 2018 and 2019 sit at 29%) | 否 | `Credit` · `2017` · `Payment Instruments Preffered for Payment` |
| 6 | 22% | `Cash` · `2018` | 10% | f1 | the 2018 Cash point | 否 | `Cash` · `2018` · `Payment Instruments Preffered for Payment` |
| 7 | 23% | `Cash` · `2019` | 10% | f1 | the 2019 Cash point | 否 | `Cash` · `2019` · `Payment Instruments Preffered for Payment` |
| 8 | 18% | `Cash` · `2020` | 10% | f1 | the 2020 Cash point (lowest grey point) | 否 | `Cash` · `2020` · `Payment Instruments Preffered for Payment` |
| 9 | 33% | `Credit` · `2020` | 10% | f1 | the 2020 Credit point (navy line rising at right) | 否 | `Credit` · `2020` · `Payment Instruments Preffered for Payment` |
| 10 | 43% | `Debit` · `2020` | 5% | f1 | the 2020 Debit point (top navy line rising slightly) | 否 | `Debit` · `2020` · `Payment Instruments Preffered for Payment` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 24%, 24%

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 3 | 5 | 15 | 无 | 0%, 5%, 10%, 15%, 20%, 25%, 30%, 35%, 40%, 45%, 50% |
| f1 | `line` | vertical | 1 | 3 | 5 | 15 | 无 | 0%, 5%, 10%, 15%, 20%, 25%, 30%, 35%, 40%, 45%, 50% |

- **f1** Payment Instruments Preffered for Payment　[图上方]　（标题里没有单位）
  - 来源行：Source: FRBSF
- **f1** Payment Instruments Preffered for Payment　[图上方]　（标题里没有单位）
  - 来源行：Source: FRBSF

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: FRBSF" printed in small text under the plot border |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | Cash, Credit, Debit legend row sits below the 2016-2020 axis, inside the chart frame |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | body paragraph on COVID-19 cash decline runs in a narrow left column level with the chart |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | "payments a consumer made.23" superscript note marker at end of body text |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | chart area enclosed in a light grey bordered box distinct from page white |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at each 5% tick, no vertical grid lines drawn |

词表 65 项，本页出现 6 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `title_typo_verbatim` | f1 | title reads "Payment Instruments Preffered for Payment" with misspelled "Preffered" | 检索时必须逐字匹配这个拼写错误，否则标题无法与表格行对齐。 |
| `percent_tick_labels_only_unit` | f1 | y ticks carry % signs (0%...50%); no unit text in title or axis label | 单位只存在于刻度文字中，导出表格若丢掉%号，数值将失去比例语义。 |
| `overlapping_marker_series` | f1 | Credit and Debit both dark navy with round markers; only vertical position distinguishes them | 两条深色序列颜色几乎相同，读值时须靠上下位置判定归属，易把29%与42%错配。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数据标签，全部15个点都要靠像素对刻度读出；刻度间隔为5%，而目标值多在18%–29%区间，5%的相对容差对22%只有约±1.1个百分点，即约刻度间距的五分之一，必须在两条网格线之间做细分插值。更棘手的是Credit与Debit同为深蓝圆点、线型一致，2016年Credit(24%)又几乎与Cash(27%)重叠，容易把序列判错，从而把值挂到错误的行上。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 通用 | 为无编号图形保留空figure_number并把标题原样（含拼写错误）作为独立字段导出 | 记录层的heading字段：figure_number/title/subtitle/unit分列，placement=above | “标题无编号 vs 有编号”一行，检验检索是否依赖Figure N前缀 |
| P6 | 一类出版方 | unit 仅存在于刻度文本（0%–50%）这一新构件percent_tick_labels_only_unit | 样式条件行的tick格式维度：百分号随刻度而非随标题 | “单位在刻度 vs 单位在标题/轴题”一行 |
| P1 | 一类出版方 | 同色系多序列（Credit与Debit同深蓝、同标记）的overlapping_marker_series | 配色/标记样式字段：允许同族色相与相同marker | “序列颜色可区分 vs 近似同色”一行，衡量序列归属错误率 |
| P3 | 一类出版方 | side_text_bullets：正文窄列与图并排占同一横带 | 页面版式条件行：图文并排 vs 图独占整宽 | “图旁有正文列 vs 无”一行，检验整页markdown导出时标题与表格的相邻关系 |
