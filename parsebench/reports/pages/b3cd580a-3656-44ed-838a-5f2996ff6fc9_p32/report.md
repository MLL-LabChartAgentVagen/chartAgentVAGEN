# b3cd580a-3656-44ed-838a-5f2996ff6fc9_p32

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| b3cd580a-3656-44ed-838a-5f2996ff6fc9 | `need_estimate` | 10 | 10 |

页面上半部是EIU《Industry outlook 2025》的正文两栏文字与一幅无编号折线图「Wind and solar are taking over」(六种电源2023–2033发电量, GWh, 数值轴在右侧), 下半部是新章节标题与正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 10200 | `Coal` · `2023` | 10% | f1 | the leftmost point of the black Coal line, at 2023 | 否 | `Coal` · `2023` · `Power generation by source; GWh` |
| 2 | 6500 | `Gas` · `2023` | 10% | f1 | the leftmost point of the gold Gas line, at 2023 (just above the 6,000 gridline) | 否 | `Gas` · `2023` · `Power generation by source; GWh` |
| 3 | 1800 | `Solar` · `2023` | 20% | f1 | the Solar (red) line in the mid-2020s, about the 2025 point | 否 | `Solar` · `2025` · `Power generation by source; GWh` |
| 4 | 2200 | `Wind` · `2023` | 20% | f1 | the leftmost point of the Wind (light green) line, at 2023 | 否 | `Wind` · `2023` · `Power generation by source; GWh` |
| 5 | 3800 | `Hydro` · `2023` | 15% | f1 | the rightmost point of the Solar (red) line, at 2033 | 否 | `Solar` · `2033` · `Power generation by source; GWh` |
| 6 | 9400 | `Coal` · `2033` | 10% | f1 | the rightmost point of the Coal (black) line, at 2033 | 否 | `Coal` · `2033` · `Power generation by source; GWh` |
| 7 | 7900 | `Gas` · `2033` | 10% | f1 | the rightmost point of the Gas (gold) line, at 2033 | 否 | `Gas` · `2033` · `Power generation by source; GWh` |
| 8 | 4200 | `Solar` · `2033` | 20% | f1 | the rightmost point of the Wind (light green) line, at 2033, the topmost of the lower bundle | 否 | `Wind` · `2033` · `Power generation by source; GWh` |
| 9 | 5000 | `Wind` · `2033` | 20% | not_found | no line passes near 5,000 at any year tick: the lower bundle tops out near 4,400 (Wind 2033) and Gas starts around 6,000 in 2023, leaving that band empty | 否 | — |
| 10 | 3700 | `Nuclear` · `2033` | 20% | f1 | the leftmost point of the Hydro (blue) line, at 2023, just under the 4,000 gridline | 否 | `Hydro` · `2023` · `Power generation by source; GWh` |

**程序核对**（模型没有看到左半的标签列）：

- 有值没能落到任何一个图元上——1 of 10 values could not be put on a mark
- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: 1800, 3800, 4200, 3700

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 6 | 11 | 66 | 无 | 12,000, 10,000, 8,000, 6,000, 4,000, 2,000, 0 |

- **f1** Wind and solar are taking over　[与图并排]　单位 `Power generation by source; GWh`
  - 来源行：Source: EIU.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `right_side_y_axis` | 唯一的值轴画在右侧 | f1 | **无** | the only value scale, 12,000 down to 0, is printed along the right edge of the plot |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: EIU.' with 'Copyright © The Economist Intelligence Unit 2024. All rights reserved.' below it |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f1 | 有 | two-column legend 'Coal Gas / Solar Wind / Hydro Nuclear' sits in the left side column level with the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | 'Power generation by source; GWh' above the legend; right-hand ticks are bare numbers 12,000...0 |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 12,000/10,000/8,000/6,000/4,000/2,000/0; no vertical rules between year ticks |

词表 65 项，本页出现 5 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `unnumbered_figure` | f1 | no 'Figure n' or 'Chart n' anywhere near the heading 'Wind and solar are taking over' | 表格行无法用图号定位, 只能靠标题文字作为上下文键, 抽取时易与正文标题混淆。 |
| `copyright_line_below_source` | f1 | 'Copyright © The Economist Intelligence Unit 2024. All rights reserved.' printed under 'Source: EIU.' | 图下小字有两块, 解析器可能把版权行当作注释或数据说明, 干扰对源行的识别。 |
| `crossing_line_bundle` | f1 | Solar, Wind, Hydro and Nuclear lines cross one another between 2029 and 2031 in a 2,000–4,500 band | 交叉区内四条线相距不足半格(1,000 GWh), 逐系列取值时极易串线, 影响读数归属。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

数值轴每格2,000 GWh, 全图高约286像素, 即1像素≈60 GWh, 而图上无任何数据标签、无点标记。对下方束(Solar/Wind/Hydro/Nuclear, 1,200–4,400)来说, 5%容差在3,700时只有±185 GWh, 折合约3像素; 而四条2px粗线在2029–2031区间彼此相距仅几像素并相互交叉, 逐年读数几乎无法稳定落在容差内。相比之下行标签只需「系列+年份」两个键, 图例六项与11个年份刻度都逐个印出, 定位并不难; 因此瓶颈在像素读值。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | right_side_y_axis(值轴只画在右侧) | 样式字段中的value_axis_side, 允许在折线图上把唯一刻度列放到绘图区右缘 | 「值轴位于右侧 vs 左侧」一行: 比较解析器把右缘刻度与线端对齐的成功率 |
| P7 | 这份文档自己的习惯 | P7的heading拆分, 特别是placement=beside与空figure_number | 图题记录: number/title/subtitle/unit分列, 且heading块可放在与绘图区并列的左侧栏 | 「标题+图例位于侧栏且无图号 vs 标题在上方带图号」一行 |
| P3 | 一类出版方 | legend_beside_plot(图例作为侧栏两列排布) | 布局条件行的legend_position增加beside_left, 并支持图例分两列 | 「图例在侧栏 vs 图例在下方」对六系列折线的系列名归属一行 |
| P1 | 通用 | 新组件crossing_line_bundle(多线在窄带内交叉) | 折线生成器的数据条件: 允许4条系列在小于1格的值域内互相交叉 | 「线间距<0.5刻度格 vs >1刻度格」一行, 使可读性成为每个标记的精度上限 |
