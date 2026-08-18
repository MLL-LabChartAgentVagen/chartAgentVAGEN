# 样例分析报告

**一页样本一份报告。** 报告要回答三件事：这一页用了哪些组件、其中哪些我们画不出来、由此该改流水线的什么。

样本清单由 [`tools/sample_pages.py`](../tools/sample_pages.py) 抽出，48 页，见 `data/stats/analysis_sample.json`。分析流程见 [review/05](../review/05_analysis_design.md)。

---

## 目录结构

```
reports/
  README.md                     本文件：格式与组件词表
  INDEX.md                      48 份的汇总（组件频次、缺口排名）
  <page_stem>/
    report.md                   人读的报告，六节，格式见下
    analysis.json               机读的结构化输出，用于汇总
    page.png                    整页 150 dpi，即 data/pages/<stem>.png
```

`<page_stem>` 用 PDF 的 stem，例如 `2023-05-sigma-01-english_p24`。

---

## report.md 的六节

### 1 · 样本

页面图、来源文档、标签组、抽查点数与其中估读点数。一句话说明这页上有什么。

### 2 · 抽查点

该页全部规则，逐条列出。这是判定这页得分的**全部**依据。

| # | 值 | 标签 | 容差 | 属于哪张图 |
|---|---|---|---|---|

### 3 · 图表分解

每张图一行：类型、面板数、系列数、类目数、图元总数、数值是否写在图上。

### 4 · 组件清单

**用 [§组件词表](#组件词表) 的固定名字**，只填「本页有无」；「我们有无」一列从词表照抄，不要现场判断。词表之外的组件写进 `新组件` 一节，那是这份报告最有价值的产出。

### 5 · 难在哪

对着 [02 §2](../review/02_chart_metric.md#2-四步判定走一遍这条规则) 的四步说，指明卡在哪一步：

- 第一步（要有表）——图表会不会被整个跳过
- 第二步（找到值）——估读精度够不够该点的容差
- 第三步（标签关联）——键有几个、宽表能不能表达
- 第四步（表外上下文）——图标题、面板名在页面上是什么形式

### 6 · 对 data pipeline 的意见

一条意见要能被执行，必须写全三项，写不全就不写：

| 项 | 内容 |
|---|---|
| **加什么** | 词表里的哪个 key，或哪个新组件 |
| **改哪里** | `chart_types.md` 的哪一行条件、风格向量的哪个字段、或某层记录加哪个字段 |
| **新增哪一行消融** | 改完之后 [05 §7](../../storyline/parsebench_chart/05_output.md#7-消融) 的消融表多出哪一行 |

第三项是硬约束：**改完之后消融表的行数只增不减**。凑不出第三项，说明这条改动只是在迎合基准而没有加能力，退回去重想（[04 §3](../review/04_pipeline_gap.md#3-与-storyline-的关系)）。

每条还要标出归属：归入 **P1–P6** 之一，或 **新增**。

---

## analysis.json

`report.md` 是给人看的，`analysis.json` 是给 `INDEX.md` 汇总的。同一份内容，机读形态：

```json
{
  "stem": "2023-05-sigma-01-english_p24",
  "document": "2023-05-sigma-01-english",
  "tags": "3d_chart+need_estimate",
  "figures": [
    {"id": "f1", "caption": "Figure 16 Combined ratios, US property lines",
     "type": "bar", "panels": 1, "series": 2, "categories": 12,
     "marks": 24, "values_printed": false}
  ],
  "components": ["reference_line", "shared_legend", "rotated_x_ticks"],
  "new_components": [{"name": "...", "why_it_matters": "..."}],
  "hardest_step": 2,
  "difficulty_notes": "...",
  "unreadable": [],
  "suggestions": [{"text": "...", "maps_to": "P5"}]
}
```

`components` 的取值必须来自词表的 key 列。

---

## 组件词表

固定词表，让 48 份报告能横向汇总。「我们有无」一列的依据是 `storyline/parsebench_chart/`；**待核实**表示规格里没写清楚，核实后回填。

### 结构

| key | 组件 | 我们有无 |
|---|---|---|
| `grouped_bar` | 分组条 | 有 |
| `stacked_bar` | 堆叠条 | 有 |
| `pct_stacked` | 百分比堆叠（归一到 100%） | 待核实 |
| `stacked_and_grouped` | 堆叠与分组出现在同一张图 | **无** |
| `dual_axis` | 双 y 轴，同面板两个量纲 | 有（`compound`） |
| `mixed_marks` | 同面板混合图元（bar + line） | 有（`compound`） |
| `stacked_area` | 堆叠面积 | 有（`area`） |
| `reference_line` | 参考线（水平/垂直虚线，常带独立图例项） | **无** |
| `negative_values` | 负值 / 零线居中的分叉条 | **无**（[P6](../review/04_pipeline_gap.md#p6--风格向量补三维)） |
| `error_bars` | 误差棒 / 置信带 | **无** |
| `broken_axis` | 断轴 | **无** |
| `log_axis` | 对数轴 | **无** |

### 版面

| key | 组件 | 我们有无 |
|---|---|---|
| `shared_legend` | 跨面板共享图例 | 有（FigureSpec 约束） |
| `shared_axis` | 跨面板共享坐标轴 | 有 |
| `small_multiples_4` | 小倍数，≤4 面板 | 有 |
| `small_multiples_5plus` | 小倍数，≥5 面板 | **无**（面板数上限 4） |
| `multi_figure_page` | 一页多张独立图，各自有图号 | 待核实（[03 §5](../../storyline/parsebench_chart/03_render.md#5-页面合成)） |
| `figure_number_title` | 图号 + 标题在图外上方 | 待核实 |
| `source_note_lines` | source / note 行在图下方 | 待核实 |

### 标签与刻度

| key | 组件 | 我们有无 |
|---|---|---|
| `value_label_inside` | 数值标签写在图元内部 | 有（`labeled` 布尔） |
| `value_label_outside` | 数值标签在图元外 / 带引线 | **无**（[P6](../review/04_pipeline_gap.md#p6--风格向量补三维)） |
| `unit_in_series_name` | 单位写在系列名里（`Operating Cash Flow ($B)`） | **无**（P6） |
| `two_level_x_ticks` | x 轴两级标签（年在内、分组在外，带分隔线） | **无** |
| `rotated_x_ticks` | x 刻度标签旋转 | 待核实（风格向量） |
| `abbrev_category_axis` | 类目轴用缩写码（`IRL` `EU-27`） | 待核实 |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（`2022:06` `1Q-2024` `08`） | **无**（P6） |

### 风格

| key | 组件 | 我们有无 |
|---|---|---|
| `panel_background` | 面板整体带底色 | 待核实（风格向量） |
| `hgrid_only` | 只有水平网格线、无纵轴线 | 待核实（风格向量） |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | **无**（[P5](../review/04_pipeline_gap.md#p5--稠密度上限抬高把稠密度变成一个可控自变量)） |

---

## report.md 模板

```markdown
# <page_stem>

![page](page.png)

## 1 · 样本
| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|

一句话说明这页上有什么。

## 2 · 抽查点
| # | 值 | 标签 | 容差 | 属于哪张图 |
|---|---|---|---|---|

## 3 · 图表分解
| 图 | 类型 | 面板 | 系列 | 类目 | 图元 | 数值写出 |
|---|---|---|---|---|---|---|

## 4 · 组件清单
| key | 本页 | 我们 |
|---|---|---|

### 新组件
词表里没有的，一条一段：是什么、为什么重要。

## 5 · 难在哪
卡在第几步，为什么。

## 6 · 对 data pipeline 的意见
- （P?／新增）……
```

---

## INDEX.md

48 份跑完后汇总，三张表：

1. **组件频次** —— 每个 key 在多少页出现，按「我们无」的频次降序。这张表给出改造顺序。
2. **新组件** —— 词表外发现的组件，出现页数与说明。出现 ≥3 次的并入词表。
3. **难点分布** —— `hardest_step` 的分布，按标签组拆开。它是模型的判断，属于**待失败案例确认的假设**，不是测量。

### 频次按档位读，不按名次

n = 48 时，真实频次 10% 的 95% 置信区间约 ±8.5 个百分点，25% 时约 ±12。名次分不出来，档位分得出来：

| 档 | 样本中出现 | 处理 |
|---|---|---|
| 高 | ≥ 24 页 | 常见形态，必须能画 |
| 中 | 5–23 页 | 值得加，排在高档之后 |
| 低 | 1–4 页 | 记录，暂不改 |

同档内不排名次。若同档两项的改造成本差很多、必须二选一，扩样到 `--size 96` 再看——缓存按 `(prompt, image, model)` 命中，扩样只跑新增的页。

---

## `unreadable`

整页原图判不出来的，模型写进 `unreadable`，一项一个图 id 加原因。这些页事后单独按框重渲染再问一次——是异常处理，不是流程的一环（[review/05 §1](../review/05_analysis_design.md#唯一的回退)）。这个字段本身也是一个测量：它非空的页面比例，就是"整页够不够用"的答案。
