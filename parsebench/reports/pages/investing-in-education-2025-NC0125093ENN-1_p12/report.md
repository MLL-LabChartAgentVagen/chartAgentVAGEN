# investing-in-education-2025-NC0125093ENN-1_p12

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| investing-in-education-2025-NC0125093ENN-1 | `3d_chart+need_estimate` | 10 | 10 |

该页为《Investing in Education 2025》第12页，包含图3与图4两张按国家排列的100%堆积柱状图（分别按教育层级和支出类别分布），下附注释、来源行及一段正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 64 | `SE` · `Pre-primary and primary education` · `Figure 3. Distribution of public expenditure on education by educational level (2023)` | 5% | f1 | the SE 'Pre-primary and primary education' bottom segment, top edge just above the 60% gridline | 否 | `Figure 3.` · `SE` · `Pre-primary and primary education` |
| 2 | 40 | `HU` · `Tertiary education` · `Figure 3. Distribution of public expenditure on education by educational level (2023)` | 5% | f1 | the IE 'Pre-primary and primary education' segment, top edge at about the 40% gridline | 否 | `Figure 3.` · `IE` · `Pre-primary and primary education` |
| 3 | 37 | `EU` · `Secondary education` · `Figure 3. Distribution of public expenditure on education by educational level (2023)` | 5% | f1 | the LU 'Pre-primary and primary education' segment, between the 30% and 40% gridlines | 否 | `Figure 3.` · `LU` · `Pre-primary and primary education` |
| 4 | 34 | `MT` · `Secondary education` · `Figure 3. Distribution of public expenditure on education by educational level (2023)` | 5% | f1 | the SK 'Pre-primary and primary education' segment, just above 30% | 否 | `Figure 3.` · `SK` · `Pre-primary and primary education` |
| 5 | 81 | `BE` · `Compensation of employees` · `Figure 4. Distribution of public expenditure on education by category (2023)` | 5% | f2 | the BE 'Compensation of employees' segment, top edge just above the 80% gridline | 否 | `Figure 4.` · `BE` · `Compensation of employees` |
| 6 | 43 | `SE` · `Compensation of employees` · `Figure 4. Distribution of public expenditure on education by category (2023)` | 5% | f2 | the SE 'Compensation of employees' segment, top edge between 40% and 50% | 否 | `Figure 4.` · `SE` · `Compensation of employees` |
| 7 | 20 | `EE` · `Intermediate consumption` · `Figure 4. Distribution of public expenditure on education by category (2023)` | 5% | f1 | the BG 'Pre-primary and primary education' segment, top edge at about the 20% gridline | 否 | `Figure 3.` · `BG` · `Pre-primary and primary education` |
| 8 | 21 | `ES` · `Other` | 10% | f1 | the LT 'Pre-primary and primary education' segment, just above 20% | 否 | `Figure 3.` · `LT` · `Pre-primary and primary education` |
| 9 | 8 | `EU` · `Gross capital formation` | 5% | f2 | the BE 'Intermediate consumption' segment, spanning roughly 81% to 89% of the stack | 否 | `Figure 4.` · `BE` · `Intermediate consumption` |
| 10 | 24 | `FI` · `Other` | 5% | f1 | the RO 'Pre-primary and primary education' segment, between the 20% and 30% gridlines | 否 | `Figure 3.` · `RO` · `Pre-primary and primary education` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——7 of 10 predicted key sets miss a rule label: 40, 37, 34, 20, 21, 8
- 规则需要的键比模型报出的图能提供的多——rules need 3 keys, the richest figure offers 2

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 4 | 28 | 112 | 无 | 0%, 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90%, 100% |
| f2 | `stacked_bar` | vertical | 1 | 4 | 28 | 112 | 无 | 0%, 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90%, 100% |

- **f1** Figure 3. / Distribution of public expenditure on education by educational level (2023)　[图上方]　（标题里没有单位）
  - 来源行：Source: European Commission services' calculations  based on Eurostat COFOG data. Online data code: [gov_10a_exp].
- **f2** Figure 4. / Distribution of public expenditure on education by category (2023)　[图上方]　（标题里没有单位）
  - 来源行：Source: European Commission services' calculations based on Eurostat COFOG data. Online data code: [gov_10a_exp].

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each country bar holds four colour segments from 'Pre-primary and primary education' up to 'Other' |
| `stacked_bar` | 堆叠条 | f2 | 有 | each country bar holds four segments: Compensation of employees, Intermediate consumption, Gross capital formation, Other |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f1 | **无** | every bar reaches the top tick and the axis ends at '100%' |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f2 | **无** | all 28 bars reach 100%, axis ticks '0%' to '100%' |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | 'Figure 3.' and 'Figure 4.' each with own banner title, notes and source lines |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Notes: Provisional data for BE, DE, ES, FR, PT, SK...' and 'Source: European Commission services' calculations' |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | 'Notes: ... 'Other' is the sum of the following items: subsidies...' plus 'Source:' line |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | four legend keys in a row under the category axis, below 'SE HR PL ... HU' |
| `legend_below_plot` | 图例在绘图区下方 | f2 | 有 | legend row 'Compensation of employees ... Other' sits under the BE...SE axis |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | axis reads country codes 'SE HR PL DK IE EE LV PT ES SI LU IT EU ...' |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f2 | 有 | axis reads 'BE CY BG IT PT IE FR LU LT EL ES CZ ... EU ... SE' |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at each 10% tick, no vertical grid lines in the plot |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f2 | 有 | only horizontal gridlines at the 10% steps cross the panel |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 28 country slots times 4 stacked segments = 112 segments |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f2 | **无** | 28 country slots times 4 stacked segments = 112 segments |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the 'EU' bar is drawn in hatched/striped fills, unlike the solid country bars |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f2 | **无** | the 'EU' bar sits mid-axis drawn with diagonal hatching instead of solid colour |

词表 65 项，本页出现 9 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `hatched_fill_for_aggregate` | page | the 'EU' bar in both figures uses diagonal hatch versions of the four series colours | 读数时需知道条纹填充与实色填充属于同一系列，否则会把EU聚合条误判为额外系列或缺失数据。 |
| `title_in_filled_banner` | page | 'Figure 3. Distribution of public expenditure...' printed white on a purple full-width band above the plot | 标题作为色块横幅存在，解析器可能丢失或不将其识别为标题层级，导致表格失去图号与年份(2023)语境。 |
| `categories_sorted_by_first_segment` | page | country order differs between figures, descending by the bottom segment share (SE 64% ... HU 19%) | 类别顺序本身编码了排名信息，同一国家在两图位置不同，取值时必须按国家代码而非位置定位。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

两图都是100%堆积、无任何数值标签，只有每10%一条网格线；段值必须由两条堆叠边界相减得到，误差是两次读数之和。对像8（BE的Intermediate consumption）或5左右的Other段，5%容差只有约±0.4个百分点，而10%刻度间距在150dpi下约33像素，即1个百分点≈3像素，堆积边界线宽本身已占1–2像素，几乎不可能达标。相比之下标签只需三个键（图号、国家代码、系列名），且28个国家代码都清楚印在轴上，寻址反而不是瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 hatched_fill_for_aggregate（聚合条用同色斜纹填充） | 样式字段中新增 series_fill_pattern，并在记录里标出被强调的类别（如EU） | “聚合条纹填充 开/关”一行：检验模型是否把条纹条误当额外系列或缺失值 |
| P1 | 通用 | P1 的按段可读精度：对100%堆积中厚度<10个百分点的段单独给出可达精度 | readable 判定从布尔改为按 mark 的 attainable_precision，并按段像素高度计算 | “薄段（<10pp）纳入/排除评分”一行：区分能力提升与容差放宽 |
| P5 | 一类出版方 | P5 的密度上限提升到 28 类别 × 4 系列 = 112 段 | 生成条件行的 categories/series 上限与横轴标签密度设置 | “每图 marks ≤48 / ≤112”一行：把密度作为受控变量 |
| P7 | 这份文档自己的习惯 | P7 的标题字段拆分：figure_number + title 位于填色横幅内 | 标题样式字段加入 banner 背景与 placement=above 的横幅变体 | “横幅式标题 / 普通粗体标题”一行：检验导出markdown是否保留图号与(2023)语境 |
| P6 | 通用 | 刻度格式：轴刻度自带百分号（0%…100%）而非纯数字加单位说明 | P6 的 tick_format 维度增加 percent_suffix 选项 | “刻度带%后缀 / 纯数字+标题单位”一行：检验单位来源对取值匹配的影响 |
