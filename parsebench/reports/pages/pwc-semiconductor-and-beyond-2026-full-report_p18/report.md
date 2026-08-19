# pwc-semiconductor-and-beyond-2026-full-report_p18

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| pwc-semiconductor-and-beyond-2026-full-report | `untagged` | 9 | 0 |

PwC《Semiconductor and beyond 2026》第18页：左侧两栏正文讲数据中心专用芯片与AI加速器，右侧灰底栏内一幅柱线组合双轴图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 98 | `Data center semiconductors` · `'24` | 1% | f1 | the '24 Data center semiconductors bar, just under the 100 gridline | 否 | `'24` · `Data center semiconductors` |
| 2 | 148 | `Data center semiconductors` · `'26F` | 1% | f1 | the '26F Data center semiconductors bar, just under 150 | 否 | `'26F` · `Data center semiconductors` |
| 3 | 270 | `Data center semiconductors` · `'30F` | 1% | f1 | the '30F Data center semiconductors bar, tallest, above 250 | 否 | `'30F` · `Data center semiconductors` |
| 4 | 180 | `Data center semiconductors` · `'27F` | 1% | f1 | the '27F Data center semiconductors bar, just under 200 | 否 | `'27F` · `Data center semiconductors` |
| 5 | 35 | `Portion of AI accelerator` · `'24` | 1% | f1 | the '24 point of the Portion of AI accelerator line, labelled '35%' | 是 | `'24` · `Portion of AI accelerator` · `(%)` |
| 6 | 52 | `Portion of AI accelerator` · `'30F` | 1% | f1 | the '30F point of the Portion of AI accelerator line, labelled '52%' | 是 | `'30F` · `Portion of AI accelerator` · `(%)` |
| 7 | 41 | `Portion of AI accelerator` · `'26F` | 1% | f1 | the '26F point of the Portion of AI accelerator line, read on the right axis between 40 and 50 | 否 | `'26F` · `Portion of AI accelerator` · `(%)` |
| 8 | 47 | `Portion of AI accelerator` · `'28F` | 1% | f1 | the '28F point of the Portion of AI accelerator line, read on the right axis below 50 | 否 | `'28F` · `Portion of AI accelerator` · `(%)` |
| 9 | 245 | `Data center semiconductors` · `'29F` | 1% | f1 | the '29F Data center semiconductors bar, just under 250 | 否 | `'29F` · `Data center semiconductors` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 7 | 14 | 部分 | 0, 50, 100, 150, 200, 250, 300 \| 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 |

- **f1** AI accelerators in the data center　[图上方]　单位 `(Unit: $ Billion)`
  - 来源行：Source: PwC analysis

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | left axis 0-300 for '$ Billion' bars, right axis 0-100 headed '(%)' for the orange line |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | grey bars per year with one orange line rising across them in the same panel |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: PwC analysis' in small print below the category axis |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | 'Data center semiconductors' swatch and 'Portion of AI accelerator' line sit between title and plot |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | two columns of body text ('As AI applications push...', 'By developing AI chips...') run level with the figure |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | '(Unit: $ Billion)' beside the title; left axis shows bare 0, 50 ... 300 |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | '(%)' printed above the right axis top tick '100' |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '35%' left of the first line point, '52%' above the last line point |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | ticks read "'24", "'25F", "'26F" ... "'30F", two-digit years with forecast suffix |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the plot area sits on the light grey fill of the right-hand column, not white |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules across the plot at 300, 250, 200, 150, 100, 50; no vertical rules |

词表 65 项，本页出现 11 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `unit_inline_beside_title` | f1 | '(Unit: $ Billion)' set in smaller type on the same line, right of the bold title | 单位不在副标题也不在轴上，而与标题同行，解析成markdown时容易与标题合并或丢失，读取柱值的量纲需回到该行。 |
| `forecast_suffix_category_labels` | f1 | '24 is actual while '25F–'30F carry an 'F' suffix marking forecast years | 同一序列内实际值与预测值仅靠刻度后缀区分，定位某年数值时必须连同F后缀原样引用，否则行标签无法唯一指向。 |
| `unit_split_between_axes` | f1 | dollar unit only in the title; percent unit only as '(%)' over the right axis | 两个序列的量纲写在两个不同位置，读线序列的41/47必须用右轴百分比，读柱必须用标题里的$ Billion，混用会整体错10倍以上。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

九个待核值里只有35%和52%写在图上，其余七个都得对着刻度量。左轴刻度间距为50，而98要落在±4.9内、148要落在±7.4内，等于要把一格50细分到十分之一；右轴刻度间距10，41要落在±2、47要落在±2.35内，也是格距的五分之一，而橙线本身线宽较粗、无点标记，端点以外无法确定具体年份对应的像素高度。相比之下标签只需“年份+序列名”两把钥匙，双轴虽会引起单位混淆但可由'(%)'与'(Unit: $ Billion)'区分，所以取数精度才是真正的瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | dual_axis 与 mixed_marks 的组合（柱+线共面、左右轴不同单位） | 条件行中新增“双轴柱线混合”样式，记录里为每个序列单独存 axis 侧与单位字段 | “单序列单轴”对比“双轴柱线混合”下的取值正确率，检验模型是否把线读到了左轴刻度上 |
| P6 | 一类出版方 | axis_title_above_axis：右轴顶端只写 '(%)' 作为单位 | 样式字段 unit_position 增加 above_top_tick 取值，并允许左右轴各自设定 | 单位写在轴标题旁 vs 写在顶端刻度上方时，百分比序列的量纲判定错误率 |
| P7 | 这份文档自己的习惯 | unit_inline_beside_title（新组件：单位与标题同行右侧小字） | 标题记录拆为 number/title/subtitle/unit 四段，并新增 unit_placement=inline_after_title | 单位在副标题行 vs 与标题同行时，导出markdown中单位被保留的比例 |
| P6 | 一类出版方 | forecast_suffix_category_labels（'24 与 '25F 混排的时间刻度） | 类别轴刻度格式字段增加“两位年份+预测后缀”，并在记录中保留原样字符串 | ISO年份刻度 vs 带撇号与F后缀刻度下，行标签逐字匹配成功率 |
