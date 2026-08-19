# Whatnextfortheglobalcarindustry_p20

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Whatnextfortheglobalcarindustry | `3d_chart+need_estimate` | 10 | 10 |

本页为IEA报告第20页，正文讨论HEV/MHEV/FHEV定义与销量，中部有一幅无编号的百分比堆积柱状图《Car market shares by powertrain in selected markets, 2019 and 2024》，含两级x轴（2019/2024与China/Europe/United States/Japan/ROW）和图下注释与来源行。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 27 | `China` · `2024` · `BEV` | 5% | f1 | the China 2024 BEV segment, top edge just above 25% | 否 | `China` · `2024` · `BEV` |
| 2 | 20 | `China` · `2024` · `PHEV` | 5% | f1 | the China 2024 PHEV segment thickness (from ~27% to ~47%) | 否 | `China` · `2024` · `PHEV` |
| 3 | 15 | `Europe` · `2024` · `BEV` | 5% | f1 | the Europe 2024 BEV segment reaching about 15% | 否 | `Europe` · `2024` · `BEV` |
| 4 | 18 | `Europe` · `2024` · `MHEV` | 5% | f1 | the Europe 2024 FHEV segment (about 22% to 40%) | 否 | `Europe` · `2024` · `FHEV` |
| 5 | 76 | `United States` · `2024` · `Others` | 5% | f1 | the United States 2024 Others segment (from about 24% to 100%) | 否 | `United States` · `2024` · `Others` |
| 6 | 9 | `United States` · `2024` · `FHEV` | 5% | f1 | the United States 2024 BEV segment reaching about 9% | 否 | `United States` · `2024` · `BEV` |
| 7 | 35 | `Japan` · `2024` · `FHEV` | 5% | f1 | the Japan 2019 FHEV+MHEV total, cited in text as '35% in 2019' | 否 | `Japan` · `2019` · `FHEV` · `MHEV` |
| 8 | 19 | `Japan` · `2024` · `MHEV` | 5% | f1 | the Japan 2024 MHEV segment thickness within the yellow band | 否 | `Japan` · `2024` · `MHEV` |
| 9 | 84 | `ROW` · `2024` · `Others` | 5% | f1 | the ROW 2024 Others segment (about 16% to 100%) | 否 | `ROW` · `2024` · `Others` |
| 10 | 91 | `China` · `2019` · `Others` | 5% | f1 | the ROW 2019 Others segment, nearly the full bar above ~2% | 否 | `ROW` · `2019` · `Others` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: 18, 9, 35, 91
- 规则需要的键比模型报出的图能提供的多——rules need 3 keys, the richest figure offers 2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 5 | 10 | 50 | 无 | 0%, 20%, 40%, 60%, 80%, 100% |
| f1 | `stacked_bar` | vertical | 1 | 5 | 10 | 50 | 无 | 0%, 20%, 40%, 60%, 80%, 100% |

- **f1** Car market shares by powertrain in selected markets, 2019 and 2024　[图上方]　（标题里没有单位）
  - 来源行：Sources: IEA analysis based on Marklines and EV Volumes.
- **f1** Car market shares by powertrain in selected markets, 2019 and 2024　[图上方]　（标题里没有单位）
  - 来源行：Sources: IEA analysis based on Marklines and EV Volumes.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each year bar stacks BEV, PHEV, FHEV, MHEV, Others segments |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f1 | **无** | all ten bars reach the top and the axis ends at 100% |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Notes: ROW = Rest of World; ...' and 'Sources: IEA analysis based on Marklines and EV Volumes.' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | BEV PHEV FHEV MHEV Others legend row under the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis ticks carry '%' and title says 'Car market shares' |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | f1 | **无** | inner row '2019 2024', outer row 'China Europe United States Japan ROW' with separators |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | outer axis label 'ROW' with note 'ROW = Rest of World' |
| `panel_background` | 绘图区带底色，不是白底 | page | **无** | the whole text-and-figure block sits on a light blue tinted panel |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 20%,40%,60%,80%; no vertical grid |

词表 65 项，本页出现 9 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `license_credit_line_below_figure` | f1 | 'IEA. CC BY 4.0.' printed right-aligned between plot and notes | 该行不是来源也不是数据链接，解析时易与Source混淆，影响定位图注边界。 |
| `grouped_stack_by_two_level_axis` | f1 | pairs of stacked bars grouped under China/Europe/United States/Japan/ROW brackets | 每个数值需要市场+年份+系列三重键，否则无法唯一定位某个分段。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上无任何数值标签，纵轴刻度间隔为20个百分点（约47像素/20%），要把BEV约9%、MHEV约19%这类薄段读到5%相对误差（即±0.5个百分点）几乎不可能；更糟的是MHEV与FHEV同为黄色系、彼此边界在Japan 2024栏几乎不可辨，PHEV在Europe 2024仅约3个百分点厚。相比之下标签虽需三重键（市场+年份+系列），仍可由两级x轴与图例逐字给出。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | pct_stacked 与 two_level_x_ticks 的组合作为条件行 | 图表生成条件表中新增“百分比堆积+两级类别轴（分组×年份）”样式行，记录字段加入 outer_category 与 inner_category | 有/无外层分组轴时，模型能否为同一系列区分不同市场的数值 |
| P1 | 通用 | 薄段可读性分级（对应 thin_segment_label 缺失的情形：完全无标签的薄段） | readable 判定改为按每个 mark 的像素高度给出可达精度阈值 | 分段厚度<5%时按可达精度打分，与布尔式可读门限对比 |
| P3 | 这份文档自己的习惯 | license_credit_line_below_figure（如“IEA. CC BY 4.0.”） | 图注区渲染字段增加版权行，位于plot与Notes之间、右对齐 | 图下存在版权行时，解析器能否仍正确抓取 Sources/Notes 行 |
| P7 | 一类出版方 | 无编号图的标题字段（figure_number 为空、标题为加粗单行） | 标题块字段：number/title/subtitle/unit 与 placement=above | 图无编号时，标题能否作为表格上方粗体标题被检索到 |
