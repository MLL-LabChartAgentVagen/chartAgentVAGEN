# ac8b3538-en_p62

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ac8b3538-en | `3d_chart+need_estimate` | 10 | 10 |

该页是一张跨页延续的OECD小多图（15个国家面板），以阶梯折线比较2019年5月至2024年5月各国名义与实际最低工资的累计变化百分比，无图号、无标题、无资料来源行。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 10 | `Japan` · `Nominal minimum wage` · `Nov-22` | 10% | f1 | the Japan `Nominal minimum wage` tread between Nov-22 and May-23, at about 10 | 否 | `Japan` · `Nominal minimum wage` · `Nov-22` |
| 2 | 17 | `Latvia` · `Real minimum wage` · `May-24` | 10% | f1 | the Korea `Nominal minimum wage` end level at May-24, about 17 | 否 | `Korea` · `Nominal minimum wage` · `May-24` |
| 3 | 16 | `Lithuania` · `Nominal minimum wage` · `Nov-21` | 10% | f1 | the Lithuania `Real minimum wage` plateau around May-21, about 16 | 否 | `Lithuania` · `Real minimum wage` · `May-21` |
| 4 | 90 | `Mexico` · `Real minimum wage` · `May-24` | 10% | f1 | the Mexico `Real minimum wage` end level at May-24, near the 90 tick | 否 | `Mexico` · `Real minimum wage` · `May-24` |
| 5 | 42 | `Netherlands` · `Nominal minimum wage` · `May-24` | 5% | f1 | the Netherlands `Nominal minimum wage` end level at May-24, about 42 | 否 | `Netherlands` · `Nominal minimum wage` · `May-24` |
| 6 | 35 | `Poland` · `Real minimum wage` · `May-24` | 10% | f1 | the Portugal `Nominal minimum wage` end level at May-24, about 35-36 | 否 | `Portugal` · `Nominal minimum wage` · `May-24` |
| 7 | 38 | `Portugal` · `Nominal minimum wage` · `May-24` | 10% | f1 | the United Kingdom `Nominal minimum wage` end level at May-24, about 38 | 否 | `United Kingdom` · `Nominal minimum wage` · `May-24` |
| 8 | 9 | `Slovak Republic` · `Real minimum wage` · `May-24` | 10% | f1 | the Slovak Republic `Real minimum wage` end level at May-24, just under 10 | 否 | `Slovak Republic` · `Real minimum wage` · `May-24` |
| 9 | 700 | `Türkiye` · `Nominal minimum wage` · `May-24` | 10% | f1 | the Türkiye `Nominal minimum wage` end level at May-24, just under the 800 tick | 否 | `Türkiye` · `Nominal minimum wage` · `May-24` |
| 10 | 12 | `United Kingdom` · `Real minimum wage` · `May-24` | 10% | f1 | the United Kingdom `Real minimum wage` final riser at May-24, about 12-13 | 否 | `United Kingdom` · `Real minimum wage` · `May-24` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: 17, 16, 35, 38

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 15 | 2 | 61 | 1830 | 无 | Japan, Korea, Luxembourg, Netherlands, New Zealand, Portugal, Slovak Republic, Slovenia, Spain, United Kingdom: -20, -10, 0, 10, 20, 30, 40, 50, 60; Latvia, Lithuania: -30, -15, 0, 15, 30, 45, 60, 75; Mexico: -60, -30, 0, 30, 60, 90, 120, 150; Poland: -40, -20, 0, 20, 40, 60, 80, 100; Türkiye: -200, 0, 200, 400, 600, 800 |

- **f1** （无标题）　[无标题]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a heavy black horizontal rule at 0 crosses every panel |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | Latvia real line falls to about -10 below the zero rule; axes print -20, -30, -60, -200 |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | Japan tops at 60, Latvia at 75, Mexico at 150, Poland at 100, Türkiye at 800 |
| `step_line_series` | 阶梯线（水平段 + 垂直跳变），不是直连折线 | f1 | **无** | both lines move in flat treads and vertical risers at wage-uprating dates, e.g. Mexico, Poland |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one legend strip `Nominal minimum wage` / `Real minimum wage` at page top governs all 15 panels |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f1 | **无** | 15 identical time-series panels from `Japan` to `United Kingdom` in a 3-column grid |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | grey legend band sits above the first row of panels, outside them |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | each panel carries its own bold name above it: `Japan`, `Korea`, `Latvia`, ... `United Kingdom` |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | `May-19`, `Nov-19` ... `May-24` set at roughly 45 degrees under every panel |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | time written as `May-19`, `Nov-22`, `May-24` rather than ISO dates |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | monthly series but only 11 ticks, one every six months, from `May-19` to `May-24` |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | each plot area carries a light grey fill instead of white |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 15 panels x 2 series x ~61 monthly points is well over 1000 plotted points |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | faint white vertical rules at the six-month positions inside the grey panels, no horizontal rules |

词表 65 项，本页出现 14 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `continuation_panel_grid_without_heading` | f1 | page opens with legend and panels only; no figure number, title, unit line or Source line anywhere | 该页的单位（百分比变化）与图号只存在于前一页，本页任何取值都无法从本页文字确定量纲，表格行必须从跨页上下文补齐标题。 |
| `legend_band_spanning_page_width` | f1 | grey full-width strip at top holds the two legend entries centred over the three panel columns | 图例与面板分离且跨整页，解析器容易把它当作独立元素，导致系列名与面板数据在导出表中失联。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

面板上没有任何数字标注，全部取值必须对着刻度目测。多数面板刻度间距为10个百分点，而5%容差对小值极为苛刻：`9`只允许±0.45，即不足一个刻度格的1/22；`12`只允许±0.6。Türkiye面板刻度为0,200,400,600,800，一格200，读`700`需落在±35内，也就是一格的1/6，而阶梯线本身线宽已占数个百分点。加上15个面板五种不同量程（60/75/150/100/800），无法把一个面板的像素比例迁移到另一个面板，读数精度是最先失守的一环；相比之下面板名（粗体）与系列名（图例）都可直接抄录。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | per_panel_axis_range 与 panel_key 的联动：每个面板的量程写入记录键 | 记录字段增加 panel_key 与 per-panel value_axis_ticks，条件行按“同图多量程”生成 | 新增一行“15面板×5种不同量程 vs 全图统一量程”，比较跨面板迁移读数的错误率 |
| P7 | 一类出版方 | new_components 中的 continuation_panel_grid_without_heading（无图号/无标题的续页面板网格） | P7 的标题块字段允许全空，并在整页导出中标注“标题在上一页” | 新增一行“有完整标题块 vs 仅图例+面板名”的续页情形，检验上下文缺失时的定位能力 |
| P6 | 一类出版方 | step_line_series 作为独立线型维度（treads/risers） | 样式字段 line_interpolation 增加 step 选项，条件行区分 step 与直连折线 | 新增一行“阶梯线 vs 直连折线”，检验在同一横向段上读数点归属月份的准确性 |
| P5 | 通用 | dense_marks_100plus 的上限提高（本图约1800个点） | 密度上限参数，从每图上限提升到千级并记录 marks 实际值 | 新增一行“<200 marks vs >1500 marks”，把密度作为受控变量评估读数精度衰减 |
| P6 | 通用 | negative_values 与零参考线的组合（-200/-60/-30 起点＋黑色0线） | 样式维度“零线与负半轴”开关，及负向刻度步长设置 | 新增一行“含负值且绘零线 vs 纯正值”，检验符号误判率 |
| P1 | 通用 | 以“每标记可达精度”替代可读性布尔判定 | 评分条件行：按刻度间距/线宽推导每个标记的容差，而非统一5% | 新增一行“容差=5% vs 容差=刻度间距的1/4”，区分Türkiye(一格200)与Japan(一格10) |
