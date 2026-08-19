# US_Professional_Services_Partner_Compensation_Survey_2024_p24

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| US_Professional_Services_Partner_Compensation_Survey_2024 | `untagged` | 5 | 0 |

本页为《2024 US Professional Services Partner Compensation Survey》第24页，左侧有一段说明文字，下方是一张按合伙人任期分三栏的横向分组条形图（2024 vs 2022），所有数值均直接标注在条上且无数值轴。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 26 | `2024` · `Less than 6 years` · `$400,000 or less` | 1% | f1 | the 2024 bar in the `$400,000 or less` row of the `Less than 6 years` panel | 是 | `Total cash compensation, by tenure as partner (%)` · `Less than 6 years` · `$400,000 or less` · `2024` |
| 2 | 45 | `2024` · `6–10 years` · `$1.01m–$2.00m` | 1% | f1 | the 2024 bar in the `$1.01m–$2.00m` row of the `6–10 years` panel | 是 | `Total cash compensation, by tenure as partner (%)` · `6–10 years` · `$1.01m–$2.00m` · `2024` |
| 3 | 4 | `2022` · `More than 10 years` · `More than $3.00m` | 1% | f1 | ambiguous: appears as 2024 `$400,000 or less` and 2024 `$801,000–$1.00m` and 2024/2022 `More than $3.00m` in `More than 10 years`, and 2024 `$801,000–$1.00m` in `6–10 years` | 是 | `Total cash compensation, by tenure as partner (%)` · `More than 10 years` · `$400,000 or less` · `2024` |
| 4 | 16 | `2024` · `More than 10 years` · `$2.01m–$3.00m` | 1% | f1 | ambiguous: 2024 `$401,000–$600,000` and 2024 `$601,000–$800,000`(=12) — the 16s are `6–10 years`/`$401,000–$600,000`/2024, `6–10 years`/`$601,000–$800,000`/2024, `More than 10 years`/`$401,000–$600,000`/2024, `More than 10 years`/`$2.01m–$3.00m`/2024 | 是 | `Total cash compensation, by tenure as partner (%)` · `6–10 years` · `$401,000–$600,000` · `2024` |
| 5 | 17 | `2022` · `Less than 6 years` · `$401,000–$600,000` | 1% | f1 | the 2022 bar in the `$401,000–$600,000` row of the `Less than 6 years` panel | 是 | `Total cash compensation, by tenure as partner (%)` · `Less than 6 years` · `$401,000–$600,000` · `2024 / 2022 legend: 2022` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——5 values given, 6 answered
- 模型预测的定位标签漏掉了规则实际用的标签——2 of 5 predicted key sets miss a rule label: 4, 16

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | horizontal | 3 | 2 | 7 | 42 | 全部 | （不画值轴） |

- **f1** Total cash compensation, by tenure as partner (%)　[图上方]　单位 `(%)`
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=155 Source: Heidrick & Struggles US professional services partner compensation survey, 2022, n=192

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | two bars per row, dark 2024 above cyan 2022, in each of the three tenure panels |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | compensation bands sit on the left as rows; bars grow rightward from a common left edge |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or gridlines anywhere; only printed numbers such as 26, 35, 45 read the bars |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | single legend `2024  2022` above the three panels governing all of them |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | row labels ($400,000 or less ... More than $3.00m) printed once at the left for all three panels |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | three panels: `Less than 6 years`, `6–10 years`, `More than 10 years`, same rows repeated |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Note: Numbers may not sum to 100%, because of rounding.` plus two `Source: Heidrick & Struggles...` lines |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | legend swatches for 2024 and 2022 sit between the title line and the panels |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f1 | 有 | legend row sits at far left, left of the first panel's column, above the row labels |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | each panel headed in bold above itself: `Less than 6 years`, `6–10 years`, `More than 10 years` |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title ends `by tenure as partner (%)`; bars themselves carry no unit |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | long bars carry the number inside their right end, e.g. `26`, `35`, `45`, `46` |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | short bars print the number to the right of the mark, e.g. `3`, `2`, `4`, `5` |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | seven long money-band row labels stacked down the left, e.g. `$401,000–$600,000` |

词表 65 项，本页出现 14 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `two_source_lines` | f1 | two separate `Source:` lines, one for 2024 n=155 and one for 2022 n=192 | 每个系列对应不同的样本与来源，读值时必须把 n 与年份系列配对，不能只引用单一来源行。 |
| `panel_local_bar_scale` | f1 | each panel's bars start at its own left edge with no ticks; 45 in panel 2 and 46 in panel 3 span different widths | 没有共享刻度线，跨面板的条长不可直接比较，必须依赖印刷数字才能取值。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

取值本身不难：42 个条全部印有数字，无需按刻度估读（也确实没有任何数值轴）。难点在寻址：一个值需要面板名（Less than 6 years / 6–10 years / More than 10 years）+ 行标签（7 个金额区间）+ 系列（2024 或 2022）三层键，共 42 个格子，而像 4 出现 5 次、16 出现 4 次、2 与 3 各出现多次，缺少任一层键就无法唯一定位。解析器通常把三个面板压成一张宽表或拆成三张无标题小表，面板名一旦掉出表体（它只是加粗文字，不是表头），值与标签的配对即失效。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | panel_title_per_panel 与 shared_legend 组合下的 panel_key 维度 | 记录字段增加 panel_key，条件行中把三面板横向并置、行标签仅在最左侧出现一次的布局单列一行 | “面板名进入键 vs 不进入键”在同值重复（4 出现 5 次、16 出现 4 次）情形下的寻址准确率对比行 |
| P6 | 一类出版方 | no_value_axis 且 value_label_inside/outside 混用 | 样式字段：数值标签位置按条长阈值自动切换（长条内右端、短条外右侧） | “全部标签在内 / 按条长切换内外”对标签-条对应正确率的消融行 |
| P7 | 这份文档自己的习惯 | 新组件 two_source_lines（两条 Source 行，各带自己的 n） | 图注字段允许 source_line 为多行数组，并与系列名绑定 | “单一来源行 vs 每系列一条来源行”对系列元数据抽取的消融行 |
| P3 | 通用 | side_text_bullets 之外的整页导出（标题为加粗行、面板名为加粗行、表体在下） | P3 的整页 markdown 导出模板：标题/面板名相对表格的位置 | “标题与面板名写为加粗标题行 vs 仅存于图内”对上下文命中的消融行 |
