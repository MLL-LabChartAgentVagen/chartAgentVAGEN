# b263dc5d-en_p119

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b263dc5d-en | `3d_chart+need_estimate` | 10 | 10 |

整页只有一张图：OECD《Figure 3.7》按受教育程度分组的三面板柱形+菱形标记图，显示两轮周期间识字能力平均分差，下方为长篇注释与来源。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 10 | `Below upper secondary` · `Sweden` · `Adjusted` | 10% | f1 | the Sweden Adjusted diamond in the 'Below upper secondary' panel, sitting on the 10 tick | 否 | `Below upper secondary` · `Sweden` · `Adjusted` |
| 2 | 3 | `Below upper secondary` · `Sweden` · `Unadjusted` | 50% | f1 | the short Sweden Unadjusted bar just above zero in the 'Below upper secondary' panel | 否 | `Below upper secondary` · `Sweden` · `Unadjusted` |
| 3 | 15 | `Upper secondary` · `Finland` · `Unadjusted` | 20% | f1 | the Finland Unadjusted bar rising to about 15 in the 'Upper secondary' panel | 否 | `Upper secondary` · `Finland` · `Unadjusted` |
| 4 | -9 | `Upper secondary` · `England (UK)` · `Adjusted` | 10% | f1 | the Israel Unadjusted bar ending just below -9 in the 'Below upper secondary' panel | 否 | `Below upper secondary` · `Israel` · `Unadjusted` |
| 5 | -36 | `Below upper secondary` · `Korea` · `Unadjusted` | 5% | f1 | the New Zealand Unadjusted bar reaching about -36 in the 'Below upper secondary' panel | 否 | `Below upper secondary` · `New Zealand` · `Unadjusted` |
| 6 | -45 | `Below upper secondary` · `Lithuania` · `Unadjusted` | 5% | f1 | the Lithuania Adjusted filled diamond near -45 in the 'Below upper secondary' panel | 否 | `Below upper secondary` · `Lithuania` · `Adjusted` |
| 7 | 14 | `Tertiary` · `Finland` · `Adjusted` | 10% | f1 | the Finland Unadjusted bar rising to about 14 in the 'Tertiary' panel | 否 | `Tertiary` · `Finland` · `Unadjusted` |
| 8 | -24 | `Upper secondary` · `Hungary` · `Adjusted` | 5% | f1 | the Hungary Unadjusted bar ending near -24 in the 'Below upper secondary' panel | 否 | `Below upper secondary` · `Hungary` · `Unadjusted` |
| 9 | -8 | `Below upper secondary` · `Israel` · `Unadjusted` | 20% | f1 | the Spain Unadjusted bar ending near -8 in the 'Tertiary' panel | 否 | `Tertiary` · `Spain` · `Unadjusted` |
| 10 | -10 | `Tertiary` · `Spain` · `Unadjusted` | 5% | f1 | the United States Unadjusted bar ending near -10 in the 'Tertiary' panel | 否 | `Tertiary` · `United States` · `Unadjusted` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: -9, -36, -8, -10

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 3 | 2 | 27 | 158 | 无 | 20, 10, 0, -10, -20, -30, -40, -50 |

- **f1** Figure 3.7. / Change in literacy proficiency between cycles, by educational attainment / Adjusted and unadjusted difference in mean literacy scores between cycles (Cycle 2 minus Cycle 1); 25-65 year-olds　[图上方]　单位 `Score-point difference`
  - 来源行：Source: OECD (2018[4]; 2015[5]; 2012[6]), Survey of Adult Skills (PIAAC) databases, http://www.oecd.org/skills/piaac/publicdataandanalysis/ (accessed on 23 September 2024); Table A.3.11 (L) in Annex A.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | legend '□■ Unadjusted ◇◆ Adjusted': diamond markers overlaid on each country's bar in all three panels |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a heavy horizontal rule drawn at 0 across the full width of each of the three panels |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | bars hang below a bold zero line down to ticks -10, -20, -30, -40, -50 |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | each panel prints its own 20 ... -50 tick column at the left edge |
| `missing_value_marker` | 缺失值用 `N/A` 或空位代替图元 | f1 | **无** | Chile and United States columns are empty in the 'Below upper secondary' panel; note: 'change ... is not reported' |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | note: 'Darker colours denote differences that are statistically significant at the 5% level' |
| `tick_marker_as_series` | 某一系列画成短横 / 尖角标记，叠在条上读同一根轴 | f1 | **无** | 'Adjusted' drawn as a small diamond at the country position, read against the same 20 to -50 axis |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one legend row above the top panel governs all three panels; no per-panel legend |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | country names drawn once above panel 1 and once below panel 3, serving all three panels |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | three stacked panels of the same chart: Below upper secondary, Upper secondary, Tertiary |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: Does not include adults who in Cycle 2 ...' and 'Source: OECD (2018[4]; ...' below the plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | 'Unadjusted / Adjusted' legend sits between the subtitle and the first panel |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | dark blue filled banner at the right of each panel reads 'Below upper secondary', 'Upper secondary', 'Tertiary' |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 20 ... -50; scale word only in axis title 'Score-point difference' |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | category label 'Poland*'; note: '*Caution is required in interpreting results ...' |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | 'Score-point difference' printed above the top tick '20' at the left of panel 1 |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | grey band labelled 'Round, Cycle 1:' with groups '1', '2', '3' above the country tick row |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | country names such as 'Flemish Region (BE)' set vertically at 90 degrees above and below the panels |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 27 vertical country labels stacked densely along the axis, e.g. 'Slovak Republic', 'New Zealand' |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 27 countries x 3 panels x 2 series ≈ 158 drawn bars and diamonds |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | 'Flemish Region (BE)' and 'England (UK)' axis labels printed in blue, all other country names in black |

词表 65 项，本页出现 21 项，其中我们画不出来的 12 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `vertical_group_separator_band` | f1 | pale beige vertical bands run through all three panels separating Round 1, Round 2 and Round 3 country blocks | 读值时必须先确认某国属于哪个 Round 分块，色带本身不携带数值，容易被误当作阴影区间或缺失列。 |
| `category_axis_repeated_top_and_bottom` | f1 | identical rotated country label row and 'Round, Cycle 1:' band appear both above panel 1 and below panel 3 | 同一套类别标签出现两次，解析出的表可能出现重复表头行，需要判断哪一行对应哪个面板。 |
| `panel_label_banner_right_side` | f1 | panel names sit in filled dark blue rectangles to the right of the plot, not above it | 面板名不在图上方而在右侧色块内，若解析器按上方标题抓取面板名，三个面板会失去区分键。 |
| `two_swatch_legend_for_one_series` | f1 | legend shows two squares for 'Unadjusted' and two diamonds for 'Adjusted' (light = not significant) | 一个系列名对应两种填色，读值时需额外判断显著性，否则同一名称下会有两类标记混淆。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上一个数字都没有印，纵轴刻度间隔为 10 分点，而每个面板只有约 190 px 高覆盖 20 到 -50 共 70 分点，即 1 分点≈2.7 px。要把 3、-8、-9 这类小值读到 5% 容差（±0.15、±0.4、±0.45 分点）等于要求亚像素精度，几乎不可能；即便是 -36、-45 这类大值，容差约 ±1.8-2.3 分点也只有 5-6 px，还要在 27 列密集竖条中分辨柱顶与菱形中心。其次才是标签：单个值需要面板名（右侧色块内）+国家名（90 度旋转）+Unadjusted/Adjusted 三个键才能唯一定位，共约 158 个标记。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | tick_marker_as_series 与 mixed_marks（柱+菱形叠加，且同名系列有深浅两种填色表示显著性） | 图表生成条件行中新增“柱形上叠加点标记系列”的 style 字段，并允许同一系列名带 significance 深浅两态 | 叠加点标记系列 开/关 时，模型区分 Unadjusted 柱与 Adjusted 菱形取值的准确率对比 |
| P2 | 这份文档自己的习惯 | panel_title_per_panel 的“右侧填色色块”变体（新组件 panel_label_banner_right_side） | 面板标题位置字段增加 right_banner 取值，并让 panel_key 进入记录键 | 面板名位于上方标题 vs 右侧色块 两种排布下，panel_key 是否被正确写入表行 |
| P1 | 通用 | per-mark 可读精度（约 158 个标记、刻度间隔 10 分点、无数值标签） | readable 判定从布尔门槛改为按标记给出可达精度，与刻度像素密度绑定 | 每分点像素数（2.7 px/分点）分档下，5% 容差命中率随密度衰减曲线 |
| P3 | 一类出版方 | two_level_x_ticks 与新组件 category_axis_repeated_top_and_bottom、vertical_group_separator_band | 类别轴样式字段：分组带（Round, Cycle 1: 1/2/3）、轴标签上下重复、分组分隔色带 | 类别轴重复/分组带 开关 时，解析表是否产生重复表头或错位的国家-面板对应 |
| P7 | 通用 | heading 五分拆：figure_number、title、subtitle、unit_text（Score-point difference，置于顶刻度之上） | 记录的标题字段拆成编号/标题/副标题/单位与单位位置（axis_title_above_axis） | 单位置于轴上方 vs 置于副标题 两种写法下，导出表是否保留分值单位 |
