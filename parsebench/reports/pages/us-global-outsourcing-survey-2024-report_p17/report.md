# us-global-outsourcing-survey-2024-report_p17

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| us-global-outsourcing-survey-2024-report | `untagged` | 5 | 0 |

本页为《Global Outsourcing Survey 2024》第17页，含六个图标要点列表、正文段落，以及两个无编号图表：一个水平条形图（扩展劳动力管理与治理归属）和一个饼图（VMO及流程成熟度）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 32% | `Procurement / Sourcing organization` | 1% | f1 | the longest bar, top row | 是 | `Extended Workforce Management and Governance Owner` · `Procurement / Sourcing organization` |
| 2 | 16% | `Risk organization` | 1% | f1 | the fourth bar from the top | 是 | `Extended Workforce Management and Governance Owner` · `Risk organization` |
| 3 | 31% | `Increase moderately` | 1% | f2 | the dark green slice on the upper left of the pie | 是 | `Maturity of Vendor Management Office (VMO) and Processes` · `Increase moderately` |
| 4 | 36% | `No change` | 1% | f2 | the mid-green slice at the bottom of the pie | 是 | `Maturity of Vendor Management Office (VMO) and Processes` · `No change` |
| 5 | 8% | `Decrease significantly` | 1% | f2 | the small teal slice at the top of the pie | 是 | `Maturity of Vendor Management Office (VMO) and Processes` · `Decrease significantly` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | horizontal | 1 | 1 | 5 | 5 | 全部 | （不画值轴） |
| f2 | `pie` | na | 1 | 4 | 4 | 4 | 全部 | （不画值轴） |

- **f1** Extended Workforce Management and Governance Owner　[图上方]　（标题里没有单位）
- **f2** Maturity of Vendor Management Office (VMO) and Processes　[图上方]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | category names sit on the left y axis; bars grow rightwards from a vertical baseline |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only a vertical baseline is drawn; no ticks or numbers along the value direction |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately titled charts: `Extended Workforce Management and Governance Owner` and `Maturity of Vendor Management Office (VMO) and Processes` |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f2 | 有 | four legend entries stacked in a column to the right of the pie |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | `31%`, `36%`, `25%`, `8%` printed in white inside the pie slices |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | `32%`, `20%`, `19%`, `16%`, `13%` printed just beyond each bar end |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | long labels like `Individual Functions / Business Units`, `Vendor / Supplier Management Office` fill the left axis column |
| `icon_category_axis` | 类目轴用图标代替文字 | page | **无** | six green circular pictograms stand beside the bullet statements above the figures |

词表 65 项，本页出现 8 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `legend_labels_mismatch_data` | f2 | legend reads Increase moderately / No change / Decrease moderately / Decrease significantly under a `Maturity` title | 图例文字与标题主题不一致，读取某一切片的数值时无法确定31%等应绑定哪个语义标签，需按颜色顺序推断。 |
| `slice_color_order_only_key` | f2 | pie slices carry only percentages; matching a slice to a legend entry requires colour comparison | 读值时颜色是唯一连接键，灰度或低分辨率下无法定位。目仰赖颜色顺序。 |

## 5 · 难在哪

卡在 **第四步 · 表外上下文**。

五个目标值全部印在图上（32%、16%、31%、36%、8%），读值毫无难度；条形图甚至没有数值轴，解析器只能取打印标签，因此第2步不构成障碍。第3步也简单：条形图一个类别名即可定位，饼图靠图例名即可。真正卡住的是第4步：两图都没有图号、没有Source行，标题`Extended Workforce Management and Governance Owner`与`Maturity of Vendor Management Office (VMO) and Processes`只是页面上的粗体行，位于图外；若解析器把标题当普通段落而与表格分离，32%与31%就无法归属到正确图表，而饼图图例词（Increase moderately等）与标题语义不符，进一步削弱上下文可辨性。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P7 | 一类出版方 | unit_in_axis_or_title 缺失情形——为无单位、无数值轴的图补上标题级单位记录字段 | 图表记录的 heading.unit_text 字段与样式条件行`no_value_axis` | 增加一行：无数值轴且单位仅存在于标签百分号中的图，考察模型能否仍输出%量纲 |
| P3 | 通用 | legend_beside_plot 与饼图组合（图例列位于右侧） | 布局条件行中的 legend placement 取值加入 beside | 增加一行：图例在右侧列 vs 图例在下方，比较类别键匹配准确率 |
| new | 这份文档自己的习惯 | 新组件 legend_labels_mismatch_data（图例语义与标题不一致） | 数据记录层：series_names 与 title 的语义一致性校验开关 | 增加一行：图例标签与标题主题一致/不一致时，值-标签绑定正确率对比 |
| P3 | 一类出版方 | 无编号图表（figure_number 为空）与粗体标题作为唯一上下文 | P3 的整页导出条件行：标题以粗体段落形式出现在表格之上 | 增加一行：有图号 vs 仅粗体标题时，上下文可检索性差异 |
