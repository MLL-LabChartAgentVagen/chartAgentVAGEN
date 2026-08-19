# 5._ESM_Staff_Report_on_Comprehensive_Review_p21

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 5._ESM_Staff_Report_on_Comprehensive_Review | `need_estimate` | 10 | 10 |

该页上部为 Figure 5 的散点式收益率对比图（8 个 SURE 发行分组、13 个期限档、两个系列的菱形标记），其余为正文与 2.1.5 小节文字。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | -0.2 | `10yr` · `European Commission: SURE` | 50% | f1 | the blue European Commission: SURE diamond at 10yr in the SURE #1 band | 否 | `SURE #1` · `20/10/20` · `10yr` · `European Commission: SURE` |
| 2 | -0.4 | `15yr` · `ESM Benchmark Yield of Equivalent Maturity` | 50% | f1 | the orange ESM benchmark diamond at 15yr in the SURE #3 band | 否 | `SURE #3` · `24/11/20` · `15yr` · `ESM Benchmark Yield of Equivalent Maturity` |
| 3 | 0.3 | `30yr` · `European Commission: SURE` | 40% | f1 | the pair at 30yr in the SURE #2 band (blue slightly above orange, near 0.3) | 否 | `SURE #2` · `10/11/20` · `30yr` · `European Commission: SURE` |
| 4 | -0.2 | `15yr` · `ESM Benchmark Yield of Equivalent Maturity` | 40% | f1 | the orange ESM benchmark diamond at 15yr in the SURE #5 band | 否 | `SURE #5` · `09/03/21` · `15yr` · `ESM Benchmark Yield of Equivalent Maturity` |
| 5 | 0.7 | `25yr` · `European Commission: SURE` | 30% | f1 | the lower (orange) diamond at 25.6yr in the SURE #7 band | 否 | `SURE #7` · `18/05/21` · `25.6yr` · `ESM Benchmark Yield of Equivalent Maturity` |
| 6 | 0.8 | `25.6yr` · `ESM Benchmark Yield of Equivalent Maturity` | 20% | f1 | the upper (blue) diamond at 25.6yr in the SURE #7 band | 否 | `SURE #7` · `18/05/21` · `25.6yr` · `European Commission: SURE` |
| 7 | 1.2 | `15yr` · `European Commission: SURE` | 20% | f1 | the upper (blue) diamond at 15yr in the SURE #8 band, the highest point on the chart | 否 | `SURE #8` · `29/03/22` · `15yr` · `European Commission: SURE` |
| 8 | 1.0 | `15yr` · `ESM Benchmark Yield of Equivalent Maturity` | 20% | f1 | the lower (orange) diamond at 15yr in the SURE #8 band | 否 | `SURE #8` · `29/03/22` · `15yr` · `ESM Benchmark Yield of Equivalent Maturity` |
| 9 | -0.5 | `7yr` · `European Commission: SURE` | 20% | f1 | the orange ESM benchmark diamond at 5yr in the SURE #2 band, the lowest point of that band | 否 | `SURE #2` · `10/11/20` · `5yr` · `ESM Benchmark Yield of Equivalent Maturity` |
| 10 | -0.1 | `15yr` · `European Commission: SURE` | 50% | f1 | the blue European Commission: SURE diamond at 15yr in the SURE #3 band, just under the zero line | 否 | `SURE #3` · `24/11/20` · `15yr` · `European Commission: SURE` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 0.7, 0.8, -0.5

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `scatter` | vertical | 1 | 2 | 13 | 26 | 无 | 2.0%, 1.5%, 1.0%, 0.5%, 0.0%, -0.5%, -1.0% |

- **f1** Figure 5. / Comparison of yields at issuance of SURE bond issuances with equivalent ESM benchmark yields　[图上方]　（标题里没有单位）
  - 来源行：Source: ESM, European Commission

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a black horizontal rule drawn across the plot at the 0.0% tick |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | diamonds sit below the 0.0% line; axis runs down to -1.0% |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | alternating light and darker grey vertical bands, one per SURE issuance, behind the markers |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: ESM, European Commission" in small print under the plot |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | "European Commission: SURE" and "ESM Benchmark Yield of Equivalent Maturity" in a row under the x labels |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | inner tick row "10yr 20yr 5yr..."; outer grouping row "SURE #1 20/10/20" ... "SURE #8 29/03/22" |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | group labels dated DD/MM/YY: "20/10/20", "26/01/21", "29/03/22" |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | whole plot area carries grey tints instead of white |

词表 65 项，本页出现 8 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `group_band_labels_inside_plot` | f1 | "SURE #1 20/10/20" etc. printed at the top inside the shaded bands, not below the axis | 外层分组名写在绘图区内部而非坐标轴下方，解析器易把它当作图内注记丢弃，导致 13 个期限档无法归属到各次发行。 |
| `duplicate_category_labels` | f1 | "15yr" appears three times, "5yr" and "30yr" twice on the same tick row | 单靠期限标签无法唯一定位一个点，必须同时用 SURE #n（及日期）才能锁定某一个标记。 |
| `coincident_markers_one_visible` | f1 | at 20yr, 7yr and 25yr only one orange diamond is visible; the blue one is hidden or absent | x |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，全部要靠像素对轴读数：0.5 个百分点的刻度间距仅约 35 px，一个像素约 0.014 pp。而待判定值多为 -0.1、-0.2 这类小量，5% 相对容差分别只有 0.005 和 0.01 pp，即不到一个像素，蓝橙两枚菱形还常常互相压叠（20yr、7yr、25yr 只看得到一枚），因此“读值”这一步最先失效；标签虽然也要三层键（SURE #n＋日期、期限、系列），但这些文字都在页面上可直接抄录。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | per-mark 可达精度（对 -0.1/-0.2 这类接近零的点放宽或改判） | 评分条件行的 readable 门限字段，改为按标记幅值给出容差 | 新增一行：小幅值标记（\|v\|<0.5 且无数值标签）单独统计命中率，与大幅值标记对比 |
| P2 | 一类出版方 | 新组件 duplicate_category_labels 与 group_band_labels_inside_plot（复合类别键：分组带标签＋期限） | 记录的 key 字段增加 group_key（带内标签），类别名允许重复 | 新增一行：类别名在同一轴上重复出现时，仅用类别名寻址 vs 用分组＋类别寻址的准确率 |
| P6 | 一类出版方 | shaded_band / panel_background 交替灰带作为分组编码 | 样式字段中加入“交替分组底色带”开关及带内顶部标签位置 | 新增一行：分组以交替底色带表示（无轴上分隔线）时的分组识别率 |
| P7 | 通用 | 标题块四段拆分（"Figure 5." 独立一行、彩色标题行、无单位短语、单位在刻度里带 %） | heading 记录字段：figure_number/title/unit_text 与 placement=above | 新增一行：单位仅出现在刻度标签（如 0.5%）而无单位短语时，导出表能否保留百分点语义 |
