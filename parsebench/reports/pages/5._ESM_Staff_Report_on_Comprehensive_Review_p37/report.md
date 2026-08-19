# 5._ESM_Staff_Report_on_Comprehensive_Review_p37

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 5._ESM_Staff_Report_on_Comprehensive_Review | `need_estimate` | 8 | 8 |

该页为ESM报告第37页，上半为正文，下半为Figure 8堆叠柱状图（ESM及其他金融援助来源，单位十亿欧元），附来源与注释。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 200 | `ESM` · `Committed 2010-2018` | 5% | f1 | the Committed 2010-2018 ESM segment (bottom, ~185-200) or the Disbursed EFSF top edge; ambiguous, closest to Committed ESM segment top edge | 否 | `Committed 2010-2018` · `ESM` |
| 2 | 185 | `EFSF` · `Committed 2010-2018` | 10% | f1 | the Committed 2010-2018 ESM segment height read against axis (just under 200) | 否 | `Committed 2010-2018` · `ESM` |
| 3 | 115 | `IMF` · `Committed 2010-2018` | 15% | f1 | the Disbursed 2010-2018 ESM segment (bottom yellow, just over 100) | 否 | `Disbursed 2010-2018` · `ESM` |
| 4 | 108 | `ESM` · `Disbursed 2010-2018` | 10% | f1 | the Disbursed 2010-2018 ESM segment, alternative reading of the same bottom yellow segment | 否 | `Disbursed 2010-2018` · `ESM` |
| 5 | 180 | `EFSF` · `Disbursed 2010-2018` | 10% | f1 | the Disbursed 2010-2018 EFSF segment (dark blue, from ~110 to ~290) | 否 | `Disbursed 2010-2018` · `EFSF` |
| 6 | 90 | `IMF` · `Disbursed 2010-2018` | 15% | f1 | the Committed 2010-2018 IMF segment (pink, from ~385 to ~475) or Disbursed IMF segment | 否 | `Committed 2010-2018` · `IMF` |
| 7 | 240 | `ESM` · `COVID-19 Response (PCS+SURE) 2020-2022` | 10% | f1 | the COVID-19 Response ESM (PCS) segment, yellow up to ~240; also stated in the note '(€240 billion)' | 否 | `COVID-19 Response (PCS+SURE) 2020-2022` · `ESM` |
| 8 | 100 | `SURE` · `COVID-19 Response (PCS+SURE) 2020-2022` | 15% | f1 | the COVID-19 Response SURE segment (light blue top, ~240 to ~340); note says 'SURE envelope size of €100 billion' | 否 | `COVID-19 Response (PCS+SURE) 2020-2022` · `SURE` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 8 predicted key sets miss a rule label: 185, 115, 90

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 6 | 4 | 11 | 无 | 0, 100, 200, 300, 400, 500, 600, 700, 800 |

- **f1** Figure 8. / ESM and other financial assistance sources　[图上方]　单位 `(in € billion)`
  - 来源行：Source: ESM, European Commission, IMF, ECA

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each column is built of colour segments (ESM, EFSF, IMF, GLF, EFSM, SURE) totalling the bar height |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: ESM, European Commission, IMF, ECA' and 'Note: Amounts committed and disbursed are part of...' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend row 'ESM EFSF IMF GLF EFSM SURE' sits under the category labels |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | heading line '(in € billion)' while axis shows bare 0..800 |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 'ESM-EFSF Combined Maximum Lending Capacity' wraps onto three lines under the axis |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 100-intervals across the panel, no vertical rules |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | first bar's ESM and EFSF segments drawn with hatched/striped fill unlike other bars |

词表 65 项，本页出现 7 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `hatched_segment_fill` | f1 | first bar's yellow ESM and blue EFSF segments are drawn with vertical white stripes, others solid | 图案填充区分了“最大可贷能力”与实际承诺/发放，读值时须知同色但不同填充仍属同一系列，不应误判为新系列。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

轴刻度间距为100（0–800），一格约35像素，而多个待测值为薄段（如GLF、EFSM约50–60），5%容差在185上仅±9，等于不到4像素，且段值必须由上下边界相减得到，误差叠加；图上无任何数值标签，故读数精度是主要瓶颈。相对地，标签只需“类别+系列”两个键，容易承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | stacked_bar 中段值需相减读取的情形，应把 readable 改为按段的可达精度 | 评分条件行中的 readable 门槛字段，改为每个 mark 的容差比例 | 新增一行：堆叠段厚度<刻度间距60%时的读值命中率对比 |
| P6 | 一类出版方 | hatched_segment_fill（同系列不同填充图案） | 样式字段中新增 segment_fill_pattern 选项 | 新增一行：有/无图案填充时系列归并错误率 |
| P7 | 通用 | unit_in_axis_or_title 与标题三层拆分（编号/标题/单位行） | 记录的 heading 字段拆为 figure_number、title、unit_text | 新增一行：单位仅存于标题行时导出表格是否保留单位 |
| P3 | 一类出版方 | wrapped_category_labels（三行换行的长类别名） | 类别轴样式字段中的 label_wrap 设置 | 新增一行：类别名换行行数对标签匹配率的影响 |
