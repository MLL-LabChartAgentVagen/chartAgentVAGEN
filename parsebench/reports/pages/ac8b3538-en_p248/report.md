# ac8b3538-en_p248

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ac8b3538-en | `3d_chart+need_estimate` | 10 | 10 |

本页是OECD《Employment Outlook 2024》第246页，主体为Figure 5.7的六个小倍数折线图，比较五国及平均的按可支配收入十分位的家庭支出与CO2排放占比。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 20 | `Five-country average` · `Expenditure` · `10` | 5% | f1 | the decile 10 CO2 emissions point in the 'Five-country average' panel (just below 20) | 否 | `Five-country average` · `CO2 emissions` · `10` · `Income decile` |
| 2 | 5 | `Five-country average` · `CO2 emissions` · `1` | 10% | f1 | the lowest-decile CO2 emissions point in 'Poland', quoted as 'About 5% of emissions accrued to the lowest income decile' | 是 | `Poland` · `CO2 emissions` · `1` · `Income decile` |
| 3 | 15 | `France` · `CO2 emissions` · `10` | 10% | f1 | the decile 9 Expenditure point in 'Mexico', sitting on the 15 gridline | 否 | `Mexico` · `Expenditure` · `9` · `Income decile` |
| 4 | 19 | `Germany` · `Expenditure` · `10` | 10% | f1 | the decile 10 Expenditure point in 'Germany' (~18.7, between 15 and 20) | 否 | `Germany` · `Expenditure` · `10` · `Income decile` |
| 5 | 16 | `Germany` · `CO2 emissions` · `10` | 10% | f1 | the decile 10 CO2 emissions point in 'Germany' (~16) | 否 | `Germany` · `CO2 emissions` · `10` · `Income decile` |
| 6 | 34 | `Mexico` · `CO2 emissions` · `10` | 5% | f1 | the decile 10 CO2 emissions point in 'Mexico', close to the 35 tick | 否 | `Mexico` · `CO2 emissions` · `10` · `Income decile` |
| 7 | 4 | `Mexico` · `Expenditure` · `1` | 30% | f1 | the decile 1 Expenditure point in 'Germany' (~4.3, just below 5) | 否 | `Germany` · `Expenditure` · `1` · `Income decile` |
| 8 | 6 | `Poland` · `Expenditure` · `1` | 20% | f1 | the decile 1 Expenditure point in 'Poland', quoted as 'about 6% of total national expenditure' | 是 | `Poland` · `Expenditure` · `1` · `Income decile` |
| 9 | 16 | `Poland` · `CO2 emissions` · `10` | 10% | f1 | the decile 10 CO2 emissions point in 'Poland' (Reading line gives 16.5%) | 是 | `Poland` · `CO2 emissions` · `10` · `Income decile` |
| 10 | 17 | `Türkiye` · `Expenditure` · `10` | 10% | f1 | the decile 10 CO2 emissions point in 'Türkiye' (~16.8, just above the 15 gridline) | 否 | `Türkiye` · `CO2 emissions` · `10` · `Income decile` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 10 predicted key sets miss a rule label: 20, 5, 15, 4, 17

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 6 | 2 | 10 | 120 | 无 | 0, 5, 10, 15, 20, 25, 30, 35 |
| f1 | `line` | vertical | 6 | 2 | 10 | 120 | 无 | 0, 5, 10, 15, 20, 25, 30, 35 |

- **f1** Figure 5.7. / Carbon footprints are much bigger at high income levels, but in some countries low-income households consume greater shares of high-emission goods / Household expenditure and emissions shares of total, by (disposable) income decile　[图上方]　单位 `%`
  - 来源行：Source: OECD calculations using IEA emissions factors for different fuels, World Input-Output Database (WIOD) as well as household budget surveys (2015 for EU countries, 2016 for Mexico, 2019 for Türkiye).)
- **f1** Figure 5.7. / Carbon footprints are much bigger at high income levels, but in some countries low-income households consume greater shares of high-emission goods / Household expenditure and emissions shares of total, by (disposable) income decile　[图上方]　单位 `%`
  - 来源行：Source: OECD calculations using IEA emissions factors for different fuels, World Input-Output Database (WIOD) as well as household budget surveys (2015 for EU countries, 2016 for Mexico, 2019 for Türkiye).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `shared_legend` | 跨面板共享图例 | f1 | 有 | One legend band 'Expenditure' / 'CO2 emissions' above all six panels |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f1 | **无** | Six identical panels: Five-country average, France, Germany, Mexico, Poland, Türkiye |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Average expenditure (resp. emissions)...', 'Reading: in Poland...', 'Source: OECD calculations...' |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | Legend strip sits between the subtitle and the first row of panels |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | Bold 'Five-country average', 'France', 'Germany', 'Mexico', 'Poland', 'Türkiye' above each panel |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | 'StatLink' logo and 'https://stat.link/2jcm09' under the figure |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | '%' above axis; subtitle reads 'Household expenditure and emissions shares of total' |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | 'Income decile' printed under the x tick row of each panel |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | '%' printed above the top tick '35' on every panel's y axis |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | Each plot area filled light grey behind the two lines |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | White horizontal rules at 5,10,...35 inside grey panels; no vertical rules |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 6 panels x 10 deciles x 2 series = 120 plotted points |

词表 65 项，本页出现 12 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `reading_guide_note` | f1 | 'Reading: in Poland, expenditure from the lowest income decile accounts for about 6%...' | 该行以文字给出Poland面板的四个近似数值（6%、18%、5%、16.5%），是页面上唯一印出的数字，读值时可直接引用而不必靠像素测量。 |
| `repeated_per_panel_axes` | f1 | Every one of six panels redraws its own 0–35 y ticks and 1–10 x ticks | 轴刻度在每个面板重复而非共享，解析出的表格必须按面板名区分，否则十个十分位标签会在六组间混淆。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上除Reading行提到的Poland四个数外没有任何印出数值，y轴刻度间距为5个百分点（0,5,…,35），而多数点落在4–17区间；例如Germany第1十分位约4.3，5%容差只有±0.2个百分点，相当于5%刻度格的1/25，肉眼在这种小面板（高约170像素、每格约24像素）上几乎无法达到。两条线在第1–8十分位几乎重合（France、Türkiye处相差不到0.5个百分点），连区分Expenditure与CO2 emissions属于哪条都困难。相比之下标签只需三个键（面板名+系列名+十分位号），表格完全承载得住。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | small_multiples_5plus 与 panel_title_per_panel 组合（面板维度进入键） | 记录字段中增加 panel_key，条件行按“6面板、共享图例、每面板重复轴”生成 | 有无 panel_key 时六面板同名类别（1–10）读值命中率对比 |
| P6 | 一类出版方 | axis_title_above_axis（裸单位“%”置于顶端刻度之上）与 axis_title_below_plot（“Income decile”置于刻度行下方） | 样式字段的单位位置维度，新增“unit_above_top_tick”和“category_axis_title_below”两种取值 | 单位位置三取值（轴旁/标题内/顶端刻度上方）下单位识别正确率 |
| P1 | 通用 | 每标记可达精度（values_printed=none 且刻度间隔5%） | readable 判定从布尔改为按刻度间距/面板像素高度推出的容差 | 刻度间距/面板高度比与5%容差命中率的关系行 |
| P3 | 这份文档自己的习惯 | 新组件 reading_guide_note（Reading行内含具体百分数） | 图注字段增加“reading”行类型，与 Note/Source 并列输出到markdown | 导出含/不含 Reading 行时可核验数值数量的差异 |
| P7 | 通用 | heading 五段拆分（Figure 5.7. + 长标题 + 副标题 + “%” 单位 + above） | P7的标题字段结构，副标题单列并允许标题跨两行 | 标题块整体作为一串 vs 五字段拆分时的上下文匹配率 |
