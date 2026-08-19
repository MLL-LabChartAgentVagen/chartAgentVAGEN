# b263dc5d-en_p181

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b263dc5d-en | `need_estimate` | 10 | 10 |

该页是OECD报告第179页，仅含一个编号图 Figure 4.17，由A/B/C三个横向排列（上下堆叠）的国家排序柱状图面板组成，展示过度资格化可能性的百分点变化。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 2.5 | `A. Numeracy` · `Finland` | 5% | f1 | the tallest positive bar in Panel A, Finland | 否 | `A. Numeracy` · `Finland` · `Percentage points` |
| 2 | -1.3 | `A. Numeracy` · `OECD average` | 5% | f1 | the highlighted OECD average bar in Panel A, just below the zero line | 否 | `A. Numeracy` · `OECD average` · `Percentage points` |
| 3 | -4.9 | `A. Numeracy` · `England (UK)` | 5% | f1 | the last and lowest bar in Panel A, England (UK) | 否 | `A. Numeracy` · `England (UK)` · `Percentage points` |
| 4 | 16.5 | `B. Years of education` · `Italy` | 5% | f1 | the first and tallest bar in Panel B, Italy | 否 | `B. Years of education` · `Italy` · `Percentage points` |
| 5 | 10 | `B. Years of education` · `OECD average` | 10% | f1 | a mid-height Panel B bar around the 10 gridline; Japan is the closest, but Switzerland and Spain are indistinguishable at this scale | 否 | `B. Years of education` · `Japan` · `Percentage points` |
| 6 | 10 | `B. Years of education` · `Flemish Region (BE)` | 5% | f1 | the second Panel B bar of the same height, read as Spain (adjacent to Japan, same apparent top) | 否 | `B. Years of education` · `Spain` · `Percentage points` |
| 7 | 2.5 | `B. Years of education` · `Israel` | 5% | f1 | the last and shortest bar in Panel B, Israel | 否 | `B. Years of education` · `Israel` · `Percentage points` |
| 8 | 6.9 | `C. Older workers (Ref: Younger workers)` · `Lithuania` | 5% | f1 | the first and only large positive bar in Panel C, Lithuania | 否 | `C. Older workers (Ref: Younger workers)` · `Lithuania` · `Percentage points` |
| 9 | -2 | `C. Older workers (Ref: Younger workers)` · `OECD average` | 5% | f1 | a short negative bar in Panel C just right of OECD average, read as Canada; Panel A Czechia is a competing candidate | 否 | `C. Older workers (Ref: Younger workers)` · `Canada` · `Percentage points` |
| 10 | -7.6 | `C. Older workers (Ref: Younger workers)` · `Israel` | 5% | f1 | the last and deepest negative bar in Panel C, Israel | 否 | `C. Older workers (Ref: Younger workers)` · `Israel` · `Percentage points` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 10, 10, -2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | vertical | 3 | 1 | 32 | 96 | 无 | 4, 0, -4, -8 (Panel A); 20, 16, 12, 8, 4, 0 (Panel B); 8, 4, 0, -4, -8 (Panel C) |

- **f1** Figure 4.17. / Likelihood of over-qualification, by socio-demographic characteristics [1/2] / Change in likelihood of over-qualification (relative to reference category)　[图上方]　单位 `Percentage points`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a heavy horizontal rule at 0 in Panels A and C from which bars grow up and down |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | Panels A and C have a zero line with bars below it, ticks read -4 and -8 |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | Panel A tops at 4, Panel B runs 0 to 20, Panel C runs -8 to 8 |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | bars are either dark navy or pale blue with no legend, e.g. Ireland pale, Estonia dark, same panel |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | three panels of the same country bar chart, one per socio-demographic characteristic |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | dark banners read "A. Numeracy", "B. Years of education", "C. Older workers (Ref: Younger workers)" |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 4, 0, -4, -8 scaled only by "Percentage points" above the axis |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | category label reads "Poland*" in all three panels |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "Percentage points" printed above the top tick (4 / 20 / 8) at the left of each panel |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | all 32 country names set vertically, 90 degrees, under each panel baseline |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | category labels include "Flemish Region (BE)" and "England (UK)" as jurisdiction codes in parentheses |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | "OECD average" label set in bold with a pale blue band behind its bar in all three panels |

词表 65 项，本页出现 12 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `category_highlight_band` | f1 | a full-height pale blue vertical band spans the "OECD average" slot in each panel | 读数时必须知道该淡蓝竖带并非数据（如预测区间），而只是标记基准类别，否则会误读为额外系列或区间。 |
| `per_panel_category_reordering` | f1 | the same 32 countries appear in each panel but sorted descending by that panel's own value | 同一国家在三个面板中位置不同，取值必须同时用面板名和国家名定位，不能按轴位置跨面板对齐。 |
| `category_separator_gridlines` | f1 | a vertical rule is drawn between every country slot in addition to horizontal tick rules | 密集竖线使柱体边界与网格线混淆，影响细柱高度判读。 线格柱体同色时更难分辨。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

取值精度是最大障碍：图上无任何数字标签，A面板刻度仅4、0、-4、-8，4个百分点约合55像素，要把 -1.3（OECD average）读到5%容差即 ±0.065pp，相当于不到1像素；C面板同样4pp一格，-2 这样的小值容差仅 ±0.1pp。B面板虽有0-20共6个刻度（4pp一格约40像素），但France 10.6、Switzerland 10.5、Japan 10.4、Spain 10.4 四根柱在像素上几乎等高，10 这个值无法唯一归属，读值与定位互相纠缠。相比之下标签层只需“面板名+国家名”两个键，可由表格承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | panel_title_per_panel 与 per_panel_axis_range 组合（横幅式面板标题 + 各面板独立轴范围） | 条件行中的 panel 配置字段：为每个面板生成独立 y 轴范围与填充横幅标题 | “三面板同类别不同排序 + 各自轴范围”对比“单面板”时的取值命中率 |
| P7 | 一类出版方 | axis_title_above_axis（单位词置于最高刻度之上）与四段式标题拆分（number/title/subtitle/unit） | 样式字段 unit_position 增加 above_top_tick 选项；记录字段拆出 subtitle 与 unit_text | 单位放在轴上方而非轴标题处时，导出表格是否仍带上 “Percentage points” |
| P6 | 这份文档自己的习惯 | 新组件 category_highlight_band（基准类别的全高淡色竖带 + 粗体标签） | 样式字段新增 highlight_band，绑定到聚合类别（如 OECD average） | 存在高亮竖带时，模型是否把它误当作数据系列或区间 |
| P1 | 通用 | negative_values 与零线两侧柱体（A、C面板）的精度分级 | readable 判定改为按每根柱可达精度打分，小值柱（\|v\|<2，刻度4pp）单独一档 | 小幅负值柱在5%容差下的可达精度与放宽到绝对容差后的差异 |
| P6 | 一类出版方 | color_encodes_extra_attribute（深/浅蓝填充无图例，疑示显著性） | 样式字段 fill_by_attribute，并要求在记录中保存该属性列 | 颜色承载第二属性且无图例时，表格能否保留该属性列 |
