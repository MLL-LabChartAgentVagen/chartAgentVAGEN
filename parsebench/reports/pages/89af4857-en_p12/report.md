# 89af4857-en_p12

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 89af4857-en | `need_estimate` | 10 | 10 |

该页为OECD中期经济展望正文第10页，含两段贸易政策文字与一幅按国家分列的堆叠柱状图（Figure 3，商品出口量占GDP比重的目的地分布）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 26 | `MEX` · `United States` | 10% | f1 | the MEX United States segment (red base reaching about 26) | 否 | `MEX` · `United States` · `% of GDP` |
| 2 | 18 | `CAN` · `United States` | 10% | f1 | the CAN United States segment (red base reaching about 18-19) | 否 | `CAN` · `United States` · `% of GDP` |
| 3 | 10 | `KOR` · `China` | 20% | f1 | the KOR China segment (green band between roughly 5.5 and 16) | 否 | `KOR` · `China` · `% of GDP` |
| 4 | 3 | `CHN` · `United States` | 20% | f1 | the KOR European Union segment (thin blue band below the purple top) | 否 | `KOR` · `European Union` · `% of GDP` |
| 5 | 16 | `DEU` · `European Union` | 10% | f1 | the DEU European Union segment (tall blue band up to about 23.7) | 否 | `DEU` · `European Union` · `% of GDP` |
| 6 | 12 | `ITA` · `European Union` | 20% | f1 | the WLD European Union segment / the WLD stack up to about 12 | 否 | `WLD` · `European Union` · `% of GDP` |
| 7 | 19 | `SAU` · `Rest of the world` | 10% | f1 | the SAU Rest of the world segment (purple from about 10.3 to 30) | 否 | `SAU` · `Rest of the world` · `% of GDP` |
| 8 | 14 | `ESP` · `European Union` | 20% | f1 | the KOR Rest of the world segment (purple from about 20 to 35.5) | 否 | `KOR` · `Rest of the world` · `% of GDP` |
| 9 | 10 | `TUR` · `European Union` | 20% | f1 | the AUS China segment (large green band reaching about 9-10) | 否 | `AUS` · `China` · `% of GDP` |
| 10 | 3 | `USA` · `Canada and Mexico` | 30% | f1 | the CHN United States segment (red base of the CHN bar) | 否 | `CHN` · `United States` · `% of GDP` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——5 of 10 predicted key sets miss a rule label: 3, 12, 14, 10, 3

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 5 | 20 | 100 | 无 | 0, 5, 10, 15, 20, 25, 30, 35, 40 |

- **f1** Figure 3. / The direct impact of merchandise trade tensions varies across countries / Distribution of merchandise export volumes in 2024　[图上方]　单位 `% of GDP`
  - 来源行：Source: OECD Interim Economic Outlook 117 database; OECD Balanced International Merchandise Trade Statistics; and OECD calculations.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each country bar is built of five colour segments whose total height is the bar length |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Merchandise export volumes as a share of GDP volumes based on 2024 data...' and 'Source: OECD Interim...' |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | row of five swatches 'United States ... Rest of the world' sits between subtitle and plot area |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | y ticks are bare numbers 0,5,...,40; scale word only in '% of GDP' above the axis |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | '% of GDP' printed above the top tick '40' at the left of the plot |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | the three-letter country codes are set vertically under the bars |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | x axis reads MEX, CAN, KOR, CHN, DEU, WLD, ITA, ZAF, JPN, IND ... |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 5-unit intervals across the panel, no vertical rules |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 20 country bars times 5 stacked series segments = 100 drawn segments |

词表 65 项，本页出现 9 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `structurally_absent_segment` | f1 | CHN bar shows no China segment and USA bar shows no United States segment (self-trade excluded) | 读值时该系列在这些类别下并非0而是不存在，表格行若强制填0会造成错误配对。 |
| `aggregate_category_among_peers` | f1 | 'WLD' sits between DEU and ITA on the country axis with identical colouring | 世界合计与单国同轴且无视觉区分，取值时须靠标签区分总量与个体。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

刻度间隔为5个百分点、全轴仅0–40，一个像素带约0.1个百分点；而待核值里有两个3和两个10，5%容差意味着3要读到±0.15、10要读到±0.5。堆叠柱的段长必须由上下两个累积边界相减得到，且KOR、DEU等国的欧盟段仅3–4个百分点高（不到一格），像素误差直接超容差；相比之下寻址只需‘国家代码+系列名’两个键，标签并不是主要障碍。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | axis_title_above_axis 与 unit_in_axis_or_title 的组合（单位置于顶刻度上方而非轴旁） | 样式字段 unit_position 增加 above_top_tick 取值，并在标题记录中与 axis_title 分离 | 单位位置=轴上方 vs 轴标题内 vs 系列名内，对比解析器恢复‘% of GDP’的比例 |
| P7 | 通用 | 标题四段拆分（figure_number 'Figure 3.'、title、subtitle 'Distribution of merchandise export volumes in 2024'、unit '% of GDP'） | 记录的 heading 字段拆成 number/title/subtitle/unit 与 placement | 有无独立 subtitle 行时，表格上下文命中率的差异 |
| new | 一类出版方 | new_components 的 structurally_absent_segment（某类别下某系列结构性缺失） | 数据生成条件行：允许 series×category 矩阵存在合法空缺，且不渲染为0 | 含结构性缺失段 vs 全满矩阵，检验空值是否被误读为0 |
| P5 | 一类出版方 | dense_marks_100plus（20类别×5系列=100段） | 密度上限从当前值提升，并把 categories×series 作为受控变量 | 每图段数 20/50/100 三档下的每段读值精度 |
