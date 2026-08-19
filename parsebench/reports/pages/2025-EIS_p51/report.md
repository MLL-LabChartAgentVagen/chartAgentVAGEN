# 2025-EIS_p51

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2025-EIS | `need_estimate` | 10 | 10 |

该页是《European Innovation Scoreboard 2025》第49页，只有一幅图（Figure 18），用横向条形图加两种标记符号展示EU27成员国在“Intellectual assets”维度上2025年得分，并叠加2018与2024年得分。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 112 | `Austria` · `Strong innovators` | 5% | f1 | the Austria 2025 bar (longest bar, top row) | 否 | `Austria` · `Intellectual assets` · `Score for dimension 3.3 in 2025 (indexed to the EU in 2018)` |
| 2 | 125 | `Sweden` · `Score in 2018` | 5% | f1 | the Austria 'Score in 2024' vertical tick (near 126 on the axis); could also be the Germany 'Score in 2018' diamond | 否 | `Austria` · `Score in 2024` · `Intellectual assets` |
| 3 | 122 | `Denmark` · `Score in 2024` | 5% | f1 | the Denmark 'Score in 2024' vertical tick, just left of 120-140 | 否 | `Denmark` · `Score in 2024` · `Intellectual assets` |
| 4 | 100 | `EU` · `Score in 2018` | 5% | f1 | the Luxembourg 2025 bar, ending at the 100 tick | 否 | `Luxembourg` · `Intellectual assets` · `Score for dimension 3.3 in 2025 (indexed to the EU in 2018)` |
| 5 | 95 | `Netherlands` · `Innovation leaders` | 5% | f1 | the Netherlands 2025 bar | 否 | `Netherlands` · `Intellectual assets` · `Score for dimension 3.3 in 2025 (indexed to the EU in 2018)` |
| 6 | 92 | `Italy` · `Moderate innovators` | 5% | f1 | the Italy 2025 bar | 否 | `Italy` · `Intellectual assets` · `Score for dimension 3.3 in 2025 (indexed to the EU in 2018)` |
| 7 | 35 | `Romania` · `Emerging innovators` | 5% | f1 | the Romania 2025 bar (bottom row, shortest) | 否 | `Romania` · `Intellectual assets` · `Score for dimension 3.3 in 2025 (indexed to the EU in 2018)` |
| 8 | 119 | `Malta` · `Score in 2024` | 5% | f1 | the Malta 'Score in 2024' vertical tick, set far right of the Malta bar | 否 | `Malta` · `Score in 2024` · `Intellectual assets` |
| 9 | 46 | `Lithuania` · `Score in 2018` | 5% | f1 | the Lithuania 'Score in 2018' diamond, detached far left of its bar; the Croatia/Hungary 2025 bar ends nearby | 否 | `Lithuania` · `Score in 2018` · `Intellectual assets` |
| 10 | 82 | `Belgium` · `Score in 2024` | 5% | f1 | the EU 2025 bar (dark blue row) | 否 | `EU` · `Intellectual assets` · `Score for dimension 3.3 in 2025 (indexed to the EU in 2018)` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——7 of 10 predicted key sets miss a rule label: 112, 125, 100, 95, 92, 35

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | horizontal | 1 | 6 | 28 | 84 | 无 | 0, 20, 40, 60, 80, 100, 120, 140, 160 |

- **f1** Figure 18 / Innovation performance of the EU27 Member States in the Intellectual assets dimension / Intellectual assets　[图上方]　单位 `Score for dimension 3.3 in 2025 (indexed to the EU in 2018)`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | each row carries a coloured bar plus a diamond and a short vertical tick |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names on the y axis, bars grow rightwards to ticks 0 ... 160 |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | bar fill = 'Emerging innovators', 'Moderate innovators', 'Strong innovators', 'Innovation leaders' group |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | legend '\| Score in 2024' drawn as a short vertical dash on each bar row |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: All performance scores are relative to that of the EU in 2018 for each dimension...' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two rows of legend swatches sit under the axis title, outside the plot |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | blue bold 'Intellectual assets' set above the plot area, below the figure caption |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | x ticks are bare numbers 0-160; scale word only in '(indexed to the EU in 2018)' |
| `axis_title_below_plot` | 值轴标题写在图下方 | f1 | **无** | 'Score for dimension 3.3 in 2025 (indexed to the EU in 2018)' printed under the x ticks |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | 'indexed to the EU in 2018'; note: 'scores are relative to that of the EU in 2018' |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 28 country names stacked down the y axis, from Austria to Romania |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the 'EU' row bar is dark blue, unlike the four group colours around it |

词表 65 项，本页出现 12 项，其中我们画不出来的 8 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `primary_series_unnamed_in_legend` | f1 | legend names only the four colour groups plus 'Score in 2018'/'Score in 2024'; 2025 bars unnamed | 读条形长度得到的是2025年得分，但图例没有任何“2025”条目，只能从轴标题“Score for dimension 3.3 in 2025”推断，表格行若缺此键会与2018/2024标记混淆。 |
| `value_sorted_category_axis` | f1 | bars run monotonically from Austria (longest) down to Romania (shortest) | 排序本身给出取值上下界约束，可用相邻国家条长互相校验读数，减少±5%容差内的误配。 |
| `encoding_explained_in_note` | f1 | note states bars = 2025, diamonds = 2018, vertical bars = 2024 performance | 三种标记的年份含义只写在图下注释里，解析表格若丢掉注释就无法把数值绑定到正确年份。 |
| `legend_mixed_swatch_and_glyph` | f1 | legend row mixes filled colour squares with a diamond glyph and a dash glyph | 同一图例既编码类别配色又编码标记序列，读者必须区分“颜色=分组”与“形状=年份”两套映射。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

最难的是寻址。一行共有三个可读数的标记（2025条、Score in 2018菱形、Score in 2024竖线），而2025这一序列在图例里根本没有名字，只能借轴标题“Score for dimension 3.3 in 2025”命名，所以一个数值至少需要“国家名 + 年份序列 + Intellectual assets（维度3.3）”三个键。更糟的是数值在28行×3标记=84个标记中重复：46既接近Lithuania的2018菱形又接近Croatia/Hungary的2025条，100既可以是Luxembourg条又是Netherlands的2024竖线，125可对应Austria的2024竖线或Germany的2018菱形；缺一个键就会命中错误标记。读数本身相对宽松：刻度每20单位约84像素，5%容差在112上是±5.6单位≈23像素，肉眼可及，只有35这类小值容差仅±1.75单位≈7像素稍紧。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | tick_marker_as_series 与 mixed_marks 组合（条形+菱形+竖线三种标记共用同一数值轴） | 图表族条件行中新增“horizontal_bar + 两个点状/短划标记序列”的生成模板，series 记录需允许 mark_shape 字段 | 带/不带“短划标记序列”的横向条形图对比行，考察模型能否把竖线读成与条形同轴的独立序列 |
| P3 | 这份文档自己的习惯 | new_components 的 primary_series_unnamed_in_legend（主序列只在轴标题里被命名） | 记录字段中把 series_name 允许为空并由 axis_title 提供年份，导出时 P3 的表头需回填该名称 | 图例是否包含主序列名称的两种版本，检验寻址键从轴标题恢复的能力 |
| P7 | 通用 | panel_title_per_panel + axis_title_below_plot + rebased_index_values 的标题四拆（编号/正题/维度小标题/指数基准） | P7 的 heading 结构字段：figure_number、title、subtitle（“Intellectual assets”）、unit_text（“…indexed to the EU in 2018”）及 placement | 单位短语放在轴下方 vs 放进标题的两行对比，测量数值被赋予正确量纲的比例 |
| P6 | 一类出版方 | color_encodes_extra_attribute 与 highlighted_category（颜色=创新分组，EU行单独深蓝） | 样式条件行增加“填色编码分组变量 + 一行聚合高亮”，并在记录中区分 group 与 series | 颜色是否携带额外分组变量的对照行，考察模型不把颜色误当序列身份 |
| P5 | 通用 | new_components 的 value_sorted_category_axis（类别按值降序排列，28行） | 类别轴生成条件行中加入排序开关，并把类别数上限提高到28以上 | 排序/未排序 × 类别数28 的密度行，检验密集横向条形下读数与行名对齐 |
