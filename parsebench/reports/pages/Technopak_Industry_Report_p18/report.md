# Technopak_Industry_Report_p18

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Technopak_Industry_Report | `untagged` | 6 | 0 |

该页为印度净水器市场报告第18页，含一个由三个饼图（2019、2024、2029P）组成的Exhibit 3.5，展示品牌与非品牌份额，其余为正文段落。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 78 | `2019` · `Branded Play` | 1% | f1 | the 2019 Branded Play slice | 是 | `Exhibit 3.5` · `2019` · `Branded Play` |
| 2 | 22 | `2019` · `Unbranded Play` | 1% | f1 | the 2019 Unbranded Play slice (exploded, labelled outside) | 是 | `Exhibit 3.5` · `2019` · `Unbranded Play` |
| 3 | 83 | `2024` · `Branded Play` | 1% | f1 | the 2024 Branded Play slice | 是 | `Exhibit 3.5` · `2024` · `Branded Play` |
| 4 | 17 | `2024` · `Unbranded Play` | 1% | f1 | the 2024 Unbranded Play slice (exploded) | 是 | `Exhibit 3.5` · `2024` · `Unbranded Play` |
| 5 | 88 | `2029P` · `Branded Play` | 1% | f1 | the 2029P Branded Play slice | 是 | `Exhibit 3.5` · `2029P` · `Branded Play` |
| 6 | 12 | `2029P` · `Unbranded Play` | 1% | f1 | the 2029P Unbranded Play slice (exploded) | 是 | `Exhibit 3.5` · `2029P` · `Unbranded Play` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `pie` | na | 3 | 2 | 1 | 6 | 全部 | （不画值轴） |
| f1 | `pie` | na | 3 | 2 | 1 | 6 | 全部 | （不画值轴） |

- **f1** Exhibit 3.5 / Share of Branded Play in Indian Water Purifier (Product) Market- By Value (in %) (FY)　[图上方]　单位 `in %`
  - 来源行：Source: Technopak Analysis
- **f1** Exhibit 3.5 / Share of Branded Play in Indian Water Purifier (Product) Market- By Value (in %) (FY)　[图上方]　单位 `in %`
  - 来源行：Source: Technopak Analysis

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | pies draw no axis; 78%, 22%, 83%, 17%, 88%, 12% readable only as printed labels |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | single legend `Branded Play  Unbranded Play` below the middle pie serves all three |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | three pies side by side titled `2019`, `2024`, `2029P` under one exhibit number |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Source: Technopak Analysis` in italics under the figure |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend row sits beneath the pies, above the source line |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | each pie carries `2019`, `2024`, `2029P` in bold above itself |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title reads `- By Value (in %) (FY)` |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | `78%`, `83%`, `88%` printed inside the blue Branded Play slices |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | `22%` with a short leader line, `17%`, `12%` placed left of the orange slices |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | panel names `2019`, `2024`, `2029P` where `P` marks projection, with `(FY)` in title |

词表 65 项，本页出现 10 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `exploded_pie_slice` | f1 | the orange Unbranded Play wedge is pulled out from each pie's centre | 分离扇形改变了扇形位置与引线标注方式，读值时需把外置的22%/17%/12%正确归到被拉出的Unbranded Play扇形。 |
| `forecast_panel_suffix` | f1 | panel label `2029P` uses a suffix letter to mark a projected year | 表格行名必须保留`2029P`原样，否则无法区分实际年份与预测年份的88%/12%。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

六个数值全部印在图上且为整数百分比，读数不成问题（步骤2无难度）；真正的障碍是定位：每个值需要三重键——Exhibit 3.5、面板年份（2019/2024/2029P）与系列名（Branded Play/Unbranded Play）。但年份只写在各饼图上方、系列名只出现在中间饼图下的共享图例中，两者都不在任何表格结构内；解析器输出往往只得到`78% 22% 83% 17% 88% 12%`的孤立数字串，且78/83/88与文中正文的83%、78%、88%重复，无法区分。要唯一定址就必须把面板维度显式写成行/列键。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | panel_key：把面板年份（2019/2024/2029P）作为独立键写入导出表格 | 记录字段中新增panel_key，并在饼图小多联的导出模板里以列头形式呈现 | 有panel_key vs 无panel_key在3面板饼图上的数值定址命中率对比 |
| P6 | 一类出版方 | 新组件exploded_pie_slice（分离扇形）与其外置引线标签 | 饼图样式字段中增加explode与label_placement=outside_with_leader选项 | 分离扇形+外置标签 vs 常规扇形+内置标签的标签-扇形配对错误率 |
| P7 | 通用 | heading拆分：figure_number=`Exhibit 3.5`、title、unit_text=`in %`分列 | 图题字段结构与整页markdown导出中标题相对表格的位置 | 标题作为粗体标题行置于表上 vs 仅置于表下时的上下文命中率 |
| P3 | 通用 | shared_legend跨面板系列名解析（Branded Play / Unbranded Play只出现一次） | 布局条件行：单一图例服务多面板时的系列名回填规则 | 共享图例 vs 每面板图例条件下系列名正确归属率 |
