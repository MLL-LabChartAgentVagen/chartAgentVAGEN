# ac8b3538-en_p247

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ac8b3538-en | `need_estimate` | 10 | 10 |

该页为OECD《Employment Outlook 2024》第245页，正文两段外含单幅折线图Figure 5.6，展示五个国家家庭消费排放按排放分位数的分布，并附注释、来源与StatLink链接。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 1.8 | `France` · `1` | 10% | f1 | the France line at emissions decile 2 (low-decile point read against the axis) | 否 | `France` · `2` · `Emissions decile` · `Tonne of CO2 per household` |
| 2 | 21.0 | `France` · `10` | 10% | f1 | the France line at emissions decile 10, the highest endpoint | 否 | `France` · `10` · `Emissions decile` · `Tonne of CO2 per household` |
| 3 | 6.8 | `Germany` · `5` | 10% | f1 | the Germany line at emissions decile 6 | 否 | `Germany` · `6` · `Emissions decile` · `Tonne of CO2 per household` |
| 4 | 18.0 | `Germany` · `10` | 10% | f1 | the Germany line at emissions decile 10 | 否 | `Germany` · `10` · `Emissions decile` · `Tonne of CO2 per household` |
| 5 | 1.0 | `Poland` · `1` | 10% | f1 | the Poland line at emissions decile 1, the lowest of the three upper lines | 否 | `Poland` · `1` · `Emissions decile` · `Tonne of CO2 per household` |
| 6 | 17.0 | `Poland` · `10` | 10% | f1 | the Poland line at emissions decile 10 | 否 | `Poland` · `10` · `Emissions decile` · `Tonne of CO2 per household` |
| 7 | 0.2 | `Mexico` · `1` | 10% | f1 | the Mexico line at emissions decile 1, hugging the zero baseline | 否 | `Mexico` · `1` · `Emissions decile` · `Tonne of CO2 per household` |
| 8 | 3.8 | `Mexico` · `10` | 10% | f1 | the Mexico line at emissions decile 10 | 否 | `Mexico` · `10` · `Emissions decile` · `Tonne of CO2 per household` |
| 9 | 0.2 | `Türkiye` · `1` | 10% | f1 | the Türkiye line at emissions decile 1, overlapping Mexico at the baseline | 否 | `Türkiye` · `1` · `Emissions decile` · `Tonne of CO2 per household` |
| 10 | 3.8 | `Türkiye` · `10` | 10% | f1 | the Türkiye line at emissions decile 10 | 否 | `Türkiye` · `10` · `Emissions decile` · `Tonne of CO2 per household` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 5 | 10 | 50 | 无 | 25, 20, 15, 10, 5, 0 |

- **f1** Figure 5.6. / Emissions from household consumption are very unequal across and within countries / Emissions from household consumption, tCO2 per household at different points in the national emissions distribution　[图上方]　单位 `Tonne of CO2 per household`
  - 来源行：Source: OECD calculations using IEA emissions factors for different fuels, World Input-Output Database (WIOD) as well as household budget surveys (2015 for EU countries, 2016 for Mexico, 2019 for Türkiye).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | small print below plot: "Note: Average emissions across the national emissions distribution..." and "Source: OECD calculations..." |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | grey legend strip with France, Germany, Mexico, Poland, Türkiye sits between subtitle and plot area |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | "StatLink" glyph with "https://stat.link/snwjx0" under the source line |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | subtitle reads "tCO2 per household at different points in the national emissions distribution"; axis shows bare 0–25 |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "Tonne of CO2 per household" printed above the top tick "25" |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the plot area itself is filled light grey behind the five lines |

词表 65 项，本页出现 6 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `category_axis_title_at_axis_end` | f1 | "Emissions decile" printed below the right end of the x tick row, not centred under the plot | 分位数轴的名称只在轴右端出现一次，表格若不带此标签，1–10这些纯数字刻度无法说明其含义。 |
| `subscript_unit_glyph` | f1 | unit written with subscript 2: "Tonne of CO2 per household" and "tCO2" in subtitle | 解析后可能变成"tCO 2"或"tCO2"，单位字符串匹配会失败，影响用单位定位数值。 |
| `duplicated_unit_text` | f1 | unit appears twice: "tCO2 per household" in subtitle and "Tonne of CO2 per household" above axis | 同一单位有两种写法，抽取时需判断以哪一处为准，否则表头单位与图不一致。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

纵轴0–25每5个单位一格（约26像素/格，即约0.19 tCO2/像素），且图上没有任何数值标签。要在5%容差内命中0.2这个点，允许误差仅±0.01 tCO2，相当于不到十分之一像素；Mexico与Türkiye两条线在1–8分位几乎重合在基线上，连区分两条线都困难。即便是21.0这样的大值，5%容差为±1.05，尚在半格以内可读，但十个待查值中有四个落在0.2–3.8区间，读值精度成为主要瓶颈；标签方面只需"国家名+分位数"两个键，反而不难。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | 把readable改为逐点可达精度（针对同一轴上量级相差百倍的折线，如0.2与21.0共用0–25轴） | 评测条件行中的readable门限字段，改为按mark记录axis_span与可达绝对误差 | 新增一行：同一数值轴上最小值/最大值比≤1/50时，低值点的容差按像素分辨率而非5%相对误差评分 |
| P6 | 一类出版方 | new_components中的category_axis_title_at_axis_end（"Emissions decile"置于x轴右端） | 样式字段新增category_axis_title位置选项（axis_end / centered_below / none） | 新增一行：类别轴标题仅出现在轴末端时，导出表格是否仍能给出类别列名 |
| P7 | 通用 | 标题五段拆分（figure_number / title / subtitle / unit_text / placement），本页单位同时出现在副标题与轴上方 | 记录字段中的heading结构，允许unit_text有两个落点（subtitle与above_axis） | 新增一行：单位只在副标题、只在轴上方、两处重复三种情形下的单位识别率 |
| P3 | 这份文档自己的习惯 | data_link_below_figure与source_note_lines同时存在时的整页markdown导出顺序 | 页面级导出模板：图题（粗体）→表格→Note→Source→StatLink链接 | 新增一行：图题作为标题行放在表上方与放在表下方时，值+标签联合命中率对比 |
