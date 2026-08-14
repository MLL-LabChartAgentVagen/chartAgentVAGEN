# Chart Registry

图表类型的唯一定义处。[03](03_figure.md) 用它枚举视图并做可行性过滤，[04](04_render.md) 用它决定渲染与插桩，[05](05_provenance.md) 用它决定 mark 的形状与可恢复性。

**本文**
1. [三个字段族](#1-三个字段族) → 2. [分层](#2-分层) → 3. [注册表](#3-注册表) → 4. [编码通道与可恢复性](#4-编码通道与可恢复性)

---

## 1. 三个字段族

每个图表类型只声明三类信息，分别服务三个下游。

| 字段族 | 内容 | 消费者 |
|---|---|---|
| **结构** | 列角色要求、基数范围、格子占用下限 | [03](03_figure.md) 枚举与过滤 |
| **语义** | 是否要求测度可加、是否要求维度有序 | [03](03_figure.md) 过滤 |
| **视觉** | mark 形状（值字典的键）、编码通道 | [04](04_render.md) 插桩、[05](05_provenance.md) 可恢复性 |

旧版 registry 中的 `data_patterns` 与 `qa_capabilities` 已删除：本流水线不生成 QA。

---

## 2. 分层

L1 插桩的实现成本随图表类型线性增长，因此分三层交付。Tier 1 端到端跑通后再向下扩。

| 层 | 图表类型 | 依据 |
|---|---|---|
| **Tier 1** | bar · grouped_bar · stacked_bar · line · area · pie · donut · scatter · compound | ParseBench Charts 维度的实际构成（bar、line、pie、compound）加上枚举与配对所需的最小扩展 |
| **Tier 2** | histogram · heatmap · box | mark 形状与 Tier 1 同构（矩形 / 格子 / 矩形带五值），插桩增量小 |
| **Tier 3** | violin · treemap · radar · waterfall · funnel · bubble | mark 形状各异，每型需要独立插桩实现 |

---

## 3. 注册表

`P` = 主维度，`S` = 次维度，`T` = 时间，`M` = 测度。基数指聚合后的取值数量。

### Tier 1

| 类型 | 族 | 列角色 | 基数约束 | 语义要求 | mark 形状 | 编码通道 |
|---|---|---|---|---|---|---|
| `bar` | comparison | 1×(P\|S) + 1×M | 3–30 | — | rect{value} | length |
| `grouped_bar` | comparison | 2×(P,S) + 1×M | \|P\|·\|S\| ∈ [6,24]，每格 ≥5 行 | — | rect{value} | length |
| `stacked_bar` | composition | 2×(P,S) + 1×M | \|P\|·\|S\| ∈ [6,20] | 测度可加 | rect{value, cum_start, cum_end} | length |
| `line` | trend | 1×T + 0–1×(P\|S) + 1×M | 时间点 ≥5，系列 ∈ [1,6] | — | point{value} | position_y |
| `area` | trend | 1×T + 1×(P\|S) + 1×M | 时间点 ≥5，堆叠层 ∈ [2,5] | 测度可加 | point{value, cum_start, cum_end} | position_y |
| `pie` | composition | 1×(P\|S) + 1×M | 3–8 | 测度可加 | sector{value, share} | angle |
| `donut` | composition | 1×(P\|S) + 1×M | 3–8 | 测度可加 | sector{value, share} | angle |
| `scatter` | relationship | 2×M + 0–1×(P\|S) | 行数 ∈ [30,500] | — | point{x, y} | position_xy |
| `compound` | — | 1×(P\|S\|T) + 2×M | 见 bar / line | — | 见 bar / line | length + position_y |

`compound` 是同面板内 bar 与 line 的组合，左右两个纵轴，两个测度各绑定一侧。同一像素高度对应两个不同的值——ParseBench Charts 维度显式收录这一形态。

### Tier 2

| 类型 | 族 | 列角色 | 基数约束 | 语义要求 | mark 形状 | 编码通道 |
|---|---|---|---|---|---|---|
| `histogram` | distribution | 1×M | 原始行数 ≥100 | — | rect{count, bin_lo, bin_hi} | length |
| `heatmap` | relationship | 2×(P,S) + 1×M | \|P\|·\|S\| ∈ [6,100]，每格 ≥3 行 | — | cell{value} | color |
| `box` | distribution | 1×(P\|S) + 1×M | 每组 ≥15 行，组数 ∈ [2,10] | — | rect{min,q1,median,q3,max} + point{outlier} | position_y |

### Tier 3

| 类型 | 族 | 列角色 | 基数约束 | 语义要求 | mark 形状 | 编码通道 |
|---|---|---|---|---|---|---|
| `violin` | distribution | 1×(P\|S) + 1×M | 每组 ≥30 行 | — | path{median,q1,q3} + 密度多边形 | position_y |
| `treemap` | composition | 1–2×(P,S) + 1×M | 叶子 ∈ [8,50] | 测度可加 | rect{value, path} | area |
| `radar` | relationship | 1×(P\|S) + ≥4×M | 实体 ∈ [2,8] | 测度同量纲 | vertex{value} | position_radial |
| `waterfall` | flow | 1×(P\|S) + 1×M | 5–15 | 测度可加、维度有序 | rect{delta, cum_start, cum_end} | length |
| `funnel` | flow | 1×(P\|S) + 1×M | 3–8 | 维度有序、取值单调递减 | rect{value} | length |
| `bubble` | relationship | 3×M + 0–1×(P\|S) | 点数 ∈ [15,100] | 尺寸测度非负 | point{x, y, size} | position_xy + area |

---

## 4. 编码通道与可恢复性

编码通道决定一个值在没有数值标注时能否从像素读出。[05 §4](05_provenance.md) 用这张表决定哪些 mark 可以进入 spot-check 标注集。

| 通道 | 读值方式 | 无标注时可否达到 1% 相对精度 |
|---|---|---|
| `length` · `position_y` · `position_xy` | 像素坐标经轴映射反解 | **可以**，条件是 1% 的值域跨度 ≥ 2 像素。逐 mark 计算 |
| `angle` | 扇区角度反解占比 | **不可以**。3% 的扇区其 1% 相对误差约 0.1°，低于可测量下限 |
| `area` | 面积开方反解 | **不可以**。面积误差按平方放大 |
| `color` | 颜色查色标反解 | **不可以**。色标量化与感知非线性使精度不可控 |
| `position_radial` | 极坐标半径反解 | 依图而定，按 `position_y` 的逐 mark 判据处理 |

**结论**：`angle` / `area` / `color` 通道的值，只有在图上画出了数值标注时才进入标注集；否则该 mark 只贡献 `(键, 区域)`，不贡献值。这条规则由渲染后的几何直接判定，不需要在 [03](03_figure.md) 预测。
