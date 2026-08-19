# ac8b3538-en_p61

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ac8b3538-en | `3d_chart+need_estimate` | 10 | 10 |

该页为 OECD 就业展望附录图 1.C.1，用 15 个小倍图折线面板展示 2019 年 5 月至 2024 年 5 月各国名义与实际最低工资的累计百分比变化。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 5 | `Australia` · `Nominal minimum wage` · `May-21` | 20% | f1 | the Australia Real minimum wage line at May-24 | 否 | `Australia` · `Real minimum wage` · `May-24` |
| 2 | 9 | `Belgium` · `Real minimum wage` · `May-24` | 15% | f1 | the Ireland Real minimum wage line at its May-24 endpoint | 否 | `Ireland` · `Real minimum wage` · `May-24` |
| 3 | 53 | `Chile` · `Nominal minimum wage` · `May-24` | 5% | f1 | the Chile Nominal minimum wage line at its May-24 plateau | 否 | `Chile` · `Nominal minimum wage` · `May-24` |
| 4 | 9 | `Colombia` · `Real minimum wage` · `May-23` | 15% | f1 | the Estonia Real minimum wage line at May-24 | 否 | `Estonia` · `Real minimum wage` · `May-24` |
| 5 | 0 | `Costa Rica` · `Nominal minimum wage` · `May-19` | 1% | f1 | both series at the May-19 base point in every panel, e.g. Australia Nominal minimum wage at May-19 | 否 | `Australia` · `Nominal minimum wage` · `May-19` |
| 6 | 10 | `Estonia` · `Nominal minimum wage` · `May-21` | 5% | f1 | the Czechia Nominal minimum wage step plateau running from Nov-19 to Nov-21 | 否 | `Czechia` · `Nominal minimum wage` · `Nov-20` |
| 7 | 2 | `France` · `Real minimum wage` · `May-24` | 20% | f1 | the France Real minimum wage line at May-24, just above the zero rule | 否 | `France` · `Real minimum wage` · `May-24` |
| 8 | 36 | `Germany` · `Nominal minimum wage` · `May-24` | 5% | f1 | the Germany Nominal minimum wage line at its final May-24 level | 否 | `Germany` · `Nominal minimum wage` · `May-24` |
| 9 | 34 | `Hungary` · `Nominal minimum wage` · `Nov-22` | 5% | f1 | the Germany Nominal minimum wage step plateau after the Nov-22 riser | 否 | `Germany` · `Nominal minimum wage` · `Nov-22` |
| 10 | -1 | `Israel` · `Real minimum wage` · `May-24` | 20% | f1 | the Australia Real minimum wage line dipping just below the zero rule around Nov-22 | 否 | `Australia` · `Real minimum wage` · `Nov-22` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——7 of 10 predicted key sets miss a rule label: 5, 9, 9, 0, 10, 34

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 15 | 2 | 11 | 1830 | 无 | 60, 50, 40, 30, 20, 10, 0, -10, -20 (most panels); Canada Federal Jurisiction: 160, 120, 80, 40, 0, -40; Canada Weighted: 60, 40, 20, 0, -20; Hungary: 90, 75, 60, 45, 30, 15, 0, -15, -30 |

- **f1** Annex Figure 1.C.1. / Minimum wage evolution, May 2019 to May 2024 / Nominal and real minimum wage, cumulative percentage change since May 2019　[图上方]　单位 `cumulative percentage change since May 2019`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a black horizontal rule drawn at 0 across each panel |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | Estonia real line reaches about -10; ticks -10, -20 printed on most panels |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | Canada Federal Jurisiction runs -40 to 160, Hungary -30 to 90, others -20 to 60 |
| `step_line_series` | 阶梯线（水平段 + 垂直跳变），不是直连折线 | f1 | **无** | Nominal minimum wage moves in flat treads with vertical risers, e.g. Australia at May-22 |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one grey legend strip above all panels governing every panel |
| `small_multiples_5plus` | 同一张图按一维切成多面板（≥5 个） | f1 | **无** | 15 identical line panels in a 3-column grid, Australia through Israel |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | legend strip sits between the subtitle line and the first row of panels |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | each panel carries its own name above it: "Australia", "Belgium", "Chile", "Hungary" |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axes show bare numbers; "cumulative percentage change since May 2019" only in the heading line |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | "May-19".."May-24" tick text is turned about 45 degrees under every panel |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | time written as "May-19", "Nov-23" rather than ISO dates |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | lines move monthly but ticks appear only every six months, May and Nov |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | every plot area carries a light grey fill instead of white |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 15 panels x 2 monthly series x ~61 months of plotted points |

词表 65 项，本页出现 14 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `panel_title_two_line_qualifier` | f1 | "Canada" appears twice, disambiguated only by a second line: "Federal Jurisiction" and "Weighted" | 仅用面板主标题无法唯一定位数值，必须把第二行限定词一起作为寻址键，否则两个 Canada 面板会混淆。 |
| `stepped_and_sawtooth_series_pair` | f1 | nominal series is a pure step line while the real series is a sawtooth eroding between steps | 同一面板内两条线形态不同，读取某月数值时须先判断该系列是台阶平台还是持续下滑段。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

面板极小（每个绘图区高度约 130 px，覆盖 -20 到 60 共 80 个单位，10 个单位刻度间距仅约 16 px），要把 5 读到 ±0.25、把 2 读到 ±0.1、把 -1 判成负号而非 0，都远超像素分辨能力；Canada Federal Jurisiction 一格 40 个单位更甚。相比之下寻址虽需三个键（面板名+系列名+月份），但键都是印在页上的文字，仍可写入表格；真正卡住的是数值本身。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | per_panel_axis_range 与面板键（panel_key） | 记录字段中为每个面板单独存 y 轴范围与刻度序列，寻址键加入面板名 | 面板数 ≥12 且各面板轴范围不同时的数值命中率对比统一轴范围的小倍图 |
| P6 | 一类出版方 | step_line_series 作为线型风格维度 | 折线族的 style 字段增加 step/线性插值开关 | 台阶线 vs 直连线在同一取值任务下的读数误差行 |
| P3 | 一类出版方 | 新建 panel_title_two_line_qualifier（面板副标题） | 面板标题字段拆为 name + qualifier，并在导出的表格上方以粗体写出 | 面板主名重复、仅靠第二行限定词区分时的上下文命中率 |
| P1 | 通用 | 逐标记可达精度（readable 改为连续量） | 评分条件行：按面板像素高度/轴跨度计算容差，而非固定 5% | 面板高度 <150 px 且刻度间距 <20 px 时的可读性阈值行 |
| P7 | 通用 | 标题五分拆（编号/标题/副标题/单位/位置） | 图头记录字段，单位短语来自副标题而非轴 | 单位只出现在副标题时的单位识别行 |
