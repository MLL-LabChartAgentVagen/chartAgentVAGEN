# b263dc5d-en_p70

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b263dc5d-en | `need_estimate` | 10 | 10 |

该页为OECD报告第68页,仅含一幅编号图Figure 2.6,由A. Literacy、B. Numeracy、C. Adaptive problem solving三个纵向条形面板组成,横轴为32个国家/经济体,纵轴80–180的分数差,下方有Note与Source说明。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 167 | `A. Literacy` · `United States` | 5% | f1 | the tallest bar, United States, in Panel A. Literacy | 否 | `A. Literacy` · `United States` · `Score-point difference` |
| 2 | 141 | `A. Literacy` · `OECD average` | 5% | f1 | the OECD average bar in Panel A. Literacy, inside the blue band | 否 | `A. Literacy` · `OECD average` · `Score-point difference` |
| 3 | 109 | `A. Literacy` · `Slovak Republic` | 5% | f1 | the last, shortest bar, Slovak Republic, in Panel A. Literacy | 否 | `A. Literacy` · `Slovak Republic` · `Score-point difference` |
| 4 | 178 | `B. Numeracy` · `United States` | 5% | f1 | the tallest bar, United States, in Panel B. Numeracy | 否 | `B. Numeracy` · `United States` · `Score-point difference` |
| 5 | 146 | `B. Numeracy` · `OECD average` | 5% | f1 | the OECD average bar in Panel B. Numeracy (the neighbouring Hungary bar is nearly the same height) | 否 | `B. Numeracy` · `OECD average` · `Score-point difference` |
| 6 | 120 | `B. Numeracy` · `Lithuania` | 5% | f1 | the OECD average bar in Panel C. Adaptive problem solving | 否 | `C. Adaptive problem solving` · `OECD average` · `Score-point difference` |
| 7 | 147 | `C. Adaptive problem solving` · `New Zealand` | 5% | f1 | the tallest bar, New Zealand, in Panel C. Adaptive problem solving | 否 | `C. Adaptive problem solving` · `New Zealand` · `Score-point difference` |
| 8 | 119 | `C. Adaptive problem solving` · `OECD average` | 5% | f1 | the last bar, Lithuania, in Panel B. Numeracy (Slovak Republic beside it is within a point) | 否 | `B. Numeracy` · `Lithuania` · `Score-point difference` |
| 9 | 90 | `C. Adaptive problem solving` · `Slovak Republic` | 5% | f1 | the last, shortest bar, Slovak Republic, in Panel C. Adaptive problem solving | 否 | `C. Adaptive problem solving` · `Slovak Republic` · `Score-point difference` |
| 10 | 154 | `A. Literacy` · `Finland` | 5% | f1 | the Flemish Region (BE) bar in Panel B. Numeracy; Netherlands in B and Austria in A sit at the same height | 否 | `B. Numeracy` · `Flemish Region (BE)` · `Score-point difference` |

**程序核对**（模型没有看到左半的标签列）：

- 报了组件但没写出证据——no_value_axis
- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 120, 119, 154

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 3 | 1 | 32 | 96 | 无 | 80, 100, 120, 140, 160, 180 |

- **f1** Figure 2.6. / Inequality in the distribution of key information-processing skills / Difference between the 90th and 10th percentile of the national skills distribution for literacy, numeracy and adaptive problem solving (90th percentile minus 10th percentile)　[图上方]　单位 `Score-point difference`
  - 来源行：Source: Table A.2.1 (L, N, A) in Annex A.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** |  |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | pale blue vertical band running through all three panels over the OECD average bar |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest tick on all three panels is 80, no break glyph on the axis |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | the same country bar chart repeated in three stacked panels A, B, C |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: Adults aged 16-65..." and "Source: Table A.2.1 (L, N, A) in Annex A." below the panels |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | filled dark-blue banners read "A. Literacy", "B. Numeracy", "C. Adaptive problem solving" |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | "Score-point difference" is the only scale word; ticks read bare 80...180 |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | category label "Poland*" with "*Caution is required in interpreting results..." under the figure |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "Score-point difference" printed above the 180 tick at the top of each panel |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | all 32 country names set vertically, turned 90 degrees, under each panel |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 100, 120, 140, 160 across each panel; no vertical grid |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the "OECD average" tick label is set in bold in each panel |

词表 65 项，本页出现 12 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `label_color_encodes_subnational_entity` | f1 | "Flemish Region (BE)" and "England (UK)" tick labels printed in blue, all other countries in black | 取值时需知道蓝色标签只是标示次国家实体,不代表另一数据系列,否则会误判为分组或第二系列。 |
| `repeated_category_order_differs_per_panel` | f1 | each panel re-sorts the same 32 countries in descending order, so slot 3 is New Zealand in A, Portugal in B | 同一横轴位置在三个面板对应不同国家,必须按面板分别列表,不能跨面板按位置读值。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

值本身不难读:轴从80到180、每20一条网格线,5%容差在141处约±7分,而条高误差只有一两分,所以第2步不构成阻碍。真正卡住的是寻址:三个面板重复同一批32个国家(共96个条),"United States"、"OECD average"、"Slovak Republic"在A、B、C各出现一次且数值不同(167/178、141/146/120、109/90),因此每个值至少需要"面板名+国家名"两个键才能唯一定位;而面板名写在深蓝填充横幅里("A. Literacy"等),解析器很可能丢掉或不作为标题/粗体输出,使表格行无法携带面板维度,不同面板的同名国家行互相混淆。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | panel_title_per_panel 与面板维度进入行键(横幅式面板标题"A. Literacy") | 记录字段增加 panel_key,并在样式中加入"填充横幅面板标题"的渲染选项 | 同一批类别在多面板重复时,有/无 panel_key 的寻址正确率对比行 |
| P6 | 一类出版方 | axis_starts_above_zero(轴自80起且无断轴符) | 条件行中的值轴起点字段,允许非零最低刻度 | 值轴起点=0 与 起点>0 两种条件下每条读数精度的对比行 |
| P7 | 一类出版方 | axis_title_above_axis + unit_in_axis_or_title("Score-point difference"置于顶端刻度上方) | 标题块字段:number/title/subtitle/unit 四分,并新增 unit 位置=顶端刻度上方 | 单位位于轴上方 vs 轴旁 vs 副标题时,单位可恢复率的对比行 |
| P6 | 一类出版方 | highlighted_category 与 shaded_band 联合标注聚合类别(粗体"OECD average"+浅蓝竖带) | 样式字段:类别强调方式(标签加粗/背景竖带),并在记录中标记该类别为聚合项 | 聚合类别有/无高亮时,是否被误当作普通类别或被并入总计的对比行 |
| new | 这份文档自己的习惯 | new_components 中的 label_color_encodes_subnational_entity(蓝色标签) | 类别标签样式字段,增加"标签颜色分组"属性 | 标签着色仅表示分组而非系列时,系列数被高估的比例对比行 |
| P5 | 通用 | rotated_x_ticks 与32个类别的高密度类别轴 | 密度上限设置:单面板类别数上限提升至32以上,并允许90度旋转刻度 | 类别数 12/32 两档下类别名逐字匹配率的对比行 |
