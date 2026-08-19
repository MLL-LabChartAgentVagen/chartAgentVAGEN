# b263dc5d-en_p131

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b263dc5d-en | `3d_chart+need_estimate` | 10 | 10 |

该页为OECD报告第129页，含一幅编号图3.15，用两个上下堆叠的面板（本土出生/外国出生成人）以柱形加菱形标记展示25个国家两轮周期间读写能力平均分差（含调整与未调整值）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 18 | `Native-born adults, native-born parents` · `Unadjusted` · `Finland` | 10% | f1 | the Finland Unadjusted bar in the top panel | 否 | `Finland` · `Unadjusted` · `Native-born adults, native-born parents` |
| 2 | -22 | `Native-born adults, native-born parents` · `Unadjusted` · `Korea` | 10% | f1 | the Korea Unadjusted bar in the top panel | 否 | `Korea` · `Unadjusted` · `Native-born adults, native-born parents` |
| 3 | -28 | `Native-born adults, native-born parents` · `Unadjusted` · `Lithuania` | 10% | f1 | the Lithuania Unadjusted bar in the top panel (deepest bar there) | 否 | `Lithuania` · `Unadjusted` · `Native-born adults, native-born parents` |
| 4 | 18 | `Foreign-born adults, foreign-born parents` · `Unadjusted` · `Finland` | 10% | f1 | the Finland Adjusted diamond in the top panel | 否 | `Finland` · `Adjusted` · `Native-born adults, native-born parents` |
| 5 | 18 | `Foreign-born adults, foreign-born parents` · `Adjusted` · `Denmark` | 10% | f1 | the Denmark Adjusted diamond in the bottom panel, sitting above its bar | 否 | `Denmark` · `Adjusted` · `Foreign-born adults, foreign-born parents` |
| 6 | 4 | `Foreign-born adults, foreign-born parents` · `Unadjusted` · `Canada` | 10% | f1 | the Singapore Adjusted diamond in the top panel, the only marker clearly above 0 in the Round 2 block | 否 | `Singapore` · `Adjusted` · `Native-born adults, native-born parents` |
| 7 | -21 | `Foreign-born adults, foreign-born parents` · `Unadjusted` · `Germany` | 10% | f1 | the Slovak Republic Unadjusted bar in the top panel | 否 | `Slovak Republic` · `Unadjusted` · `Native-born adults, native-born parents` |
| 8 | -33 | `Foreign-born adults, foreign-born parents` · `Unadjusted` · `Korea` | 10% | f1 | the Korea Unadjusted bar in the bottom panel, the deepest bar on the figure | 否 | `Korea` · `Unadjusted` · `Foreign-born adults, foreign-born parents` |
| 9 | -30 | `Foreign-born adults, foreign-born parents` · `Unadjusted` · `New Zealand` | 10% | f1 | the New Zealand Unadjusted bar in the bottom panel | 否 | `New Zealand` · `Unadjusted` · `Foreign-born adults, foreign-born parents` |
| 10 | -25 | `Foreign-born adults, foreign-born parents` · `Unadjusted` · `Hungary` | 10% | f1 | the Hungary Unadjusted bar in the bottom panel (Round 3 block) | 否 | `Hungary` · `Unadjusted` · `Foreign-born adults, foreign-born parents` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 18, 4, -21

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 2 | 2 | 25 | 100 | 无 | 30, 20, 10, 0, -10, -20, -30, -40 |

- **f1** Figure 3.15. / Change in literacy proficiency between cycles, by immigrant background / Adjusted and unadjusted difference in mean literacy scores between cycles (Cycle 2 minus Cycle 1)　[图上方]　单位 `Score-point difference`
  - 来源行：Source: OECD (2018[4]; 2015[5]; 2012[6]), Survey of Adult Skills (PIAAC) databases, http://www.oecd.org/skills/piaac/publicdataandanalysis/ (accessed on 23 September 2024); Table A.3.14 (L) in Annex A.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | diamond markers for `Adjusted` overlaid on the `Unadjusted` bars in both panels |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a thick horizontal rule at 0 in each panel from which bars grow up and down |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | ticks run 30 down to -40; most bars hang below the 0 line in both panels |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | beige vertical bands between Korea and Lithuania and between New Zealand and Hungary |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | `Darker colours denote differences that are statistically significant at the 5% level.` |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | single `Unadjusted` / `Adjusted` legend above both panels |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | one set of country columns aligned through both panels, vertical separators continuous |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | two stacked panels of the same bar-plus-diamond chart, same 25 countries |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Note: Adults aged 16-65; ...` and `Source: OECD (2018[4]; ...` below the plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | legend row sits between the subtitle and the `Round, Cycle 1:` banner |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | dark blue filled boxes at the right read `Native-born adults, native-born parents` and `Foreign-born adults, foreign-born parents` |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis ticks are bare numbers 30...-40; scale word only in `Score-point difference` |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | `Score-point difference` printed above the top tick `30` at the left |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | grey banner `Round, Cycle 1:` with segments `1`, `2`, `3` above the country tick labels |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | country names set vertically, e.g. `Flemish Region (BE)`, `Slovak Republic` |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 25 vertical country labels stacked along the axis, longest `Flemish Region (BE)` |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 25 countries x 2 series x 2 panels = 100 drawn marks |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | `England (UK)` and `Flemish Region (BE)` tick labels printed in blue, others in black |

词表 65 项，本页出现 18 项，其中我们画不出来的 10 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `dual_glyph_legend_entry` | f1 | each legend entry shows two glyphs: pale+dark square for `Unadjusted`, hollow+filled diamond for `Adjusted` | 一个图例项对应两种填色，读值时必须把显著/不显著两种色调都归到同一系列，否则会误判为四个系列。 |
| `category_labels_at_both_panel_edges` | f1 | the 25 country names are printed vertically above the top panel and again below the bottom panel | 同一类别轴标签出现两次，解析成表格时可能被拆成两组行头，需确认哪一组对应哪个面板。 |
| `grouping_banner_row_label` | f1 | `Round, Cycle 1:` label at the left of the grey banner naming its `1`/`2`/`3` segments | 分组行本身带名称，定位一个国家的值时还需知道它属于第1/2/3轮，构成额外的键。 |
| `sort_order_stated_in_note` | f1 | `Countries and economies are ranked in descending order of the unadjusted change ... among foreign-born adults` | 类别顺序由下面板的数值决定，读上面板时不能假设其自身单调，避免按位置推断数值。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

两个面板的刻度都是 30,20,10,0,-10,-20,-30,-40，10 分一格在 150 dpi 下只有约 28 像素；要把 4 这样的小值读到 5% 即 ±0.2 分，相当于 0.6 像素，纯像素读值不可能，-21 与 -22 之间的差别也只有 2.8 像素，而本图 100 个标记全部无数字标注（values_printed=none）。相比之下第 3 步虽然每个值需要国家＋Unadjusted/Adjusted＋面板名三个键（外加显著性色调与 Round 分组），仍可由表头承载，因此读值是真正的瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | panel_title_per_panel 与面板名进入行键（此处为右侧深蓝填充框内的 `Native-born adults, native-born parents` / `Foreign-born adults, foreign-born parents`） | 记录字段增加 panel_key，样式字段允许面板名放在绘图区侧边填充色块中 | 有/无 panel_key 时，上下两面板同一国家同名系列值的错配率对比 |
| P6 | 一类出版方 | color_encodes_extra_attribute（浅/深两种填色表示 5% 显著性）与 dual_glyph_legend_entry | 条件行中系列定义允许一个图例项绑定两种填色；样式字段加入 significance_shading | 图例项含双glyph时，系列数被误判为 4 而非 2 的比例 |
| P7 | 通用 | axis_title_above_axis + unit_in_axis_or_title（`Score-point difference` 置于顶刻度 30 上方） | 标题块字段拆分：number/title/subtitle/unit 与 unit 位置（above_axis） | 单位置于轴顶上方 vs 置于副标题时，导出表格能否恢复“分数点差”量纲 |
| P1 | 通用 | dense_marks_100plus（25 类别×2 系列×2 面板=100 个标记，无数值标签） | 密度上限参数与 readable 的按标记精度定义 | 每格 10 单位、无数值标签时，各标记可达精度随类别数 25→50 的变化曲线 |
