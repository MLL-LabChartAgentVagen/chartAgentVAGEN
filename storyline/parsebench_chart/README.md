# ParseBench-Oriented Chart Data Generation

> 本目录是对 [`../data_generation/`](../data_generation/) 的**改进方案**，不是替代。
> 现有 pipeline 的四阶段骨架、Code-as-DGP、Table Amortization 全部保留；改动集中在
> **任务目标从「图 → 答案」换成「图 → 结构化表 + 溯源」**，以及由此带来的重心转移。

---

## 1. 一句话目标

对准 ParseBench 的 Charts 与 Visual Grounding 两个维度：让模型把真实文档里的图表**忠实转录成表，并能指出每个值画在哪里**。这是 2026 年前沿模型真正没有解决的部分——推理那条轴上 ChartQA 已饱和、CharXiv 已超过人类基线。

---

## 2. 与现有 pipeline 的关系

| 现有组件 | 处置 | 原因 |
|---|---|---|
| Phase 0 域池 | **保留，不动** | 有效、便宜，是基础设施 |
| Phase 1 场景实例化 | **保留，加一个字段** | 新增 `analytical_intent`，用于驱动选图 |
| Phase 2 SDK / Code-as-DGP | **保留范式，精简接口** | 8 个方法 → 4 个；DAG 由表达式推断 |
| Phase 2 三层验证 + auto-fix | **移除，下移到视图层** | 检验对象错位（见 [03](03_fact_table.md)） |
| Phase 3 SQL 投影 | **保留，不动** | 跨图一致性的实现基础 |
| Phase 3 View 枚举 | **保留枚举，换过滤器** | 原过滤器是算子兼容性，去掉 QA 后失效 |
| Phase 3 算子代数 / 多跳 QA | **降优先级，暂缓** | 推理轴已拥挤，先做感知 |
| 渲染 | **从一行扩成一个阶段** | 图像多样性完全由这一层决定 |
| 溯源记录 | **新增** | 本方案的核心产出 |
| Chart Type Registry | **保留，补 compound** | ParseBench 四类图之一，现在缺 |

---

## 3. 流水线

```
 Phase 0  域池                              [ 不动 ]
    ▼
 Phase 1  场景实例化 + analytical_intent     [ 加一个字段 ]
    ▼
 Phase 2  原子事实表（精简 SDK）              [ 接口减半，验证下移 ]
    ▼
 Phase 3  选图：枚举 → 依意图选择 → 可读性过滤  [ 换过滤器 ]
    ▼
 Phase 4  渲染：版面 / 风格 / 退化 / 页面合成   [ 新增，工作量重心 ]
    ▼
 Phase 5  溯源记录 L0 / L1 / L2 → 训练目标     [ 新增，核心产出 ]
```

---

## 4. 文件索引

| 文件 | 内容 | 对应原 phase |
|---|---|---|
| [01_target.md](01_target.md) | 任务定义、输出规格、评测集 | 新增 |
| [02_scenario.md](02_scenario.md) | 域池与场景，唯一改动是分析意图 | phase_0 / phase_1 |
| [03_fact_table.md](03_fact_table.md) | SDK 精简，验证为何下移 | phase_2 |
| [04_figure_selection.md](04_figure_selection.md) | 选图的两个判据 | phase_3 前半 |
| [05_render.md](05_render.md) | 渲染的八个采样维度 | 新增 |
| [06_provenance.md](06_provenance.md) | 三层溯源模型与训练目标 | 新增 |

---

## 5. 三条不变式

贯穿全流程，任何改动不得违反：

1. **原子粒度** — 事实表每行是一个不可分事件。聚合只发生在 SQL 投影里。
2. **LLM 不生产数值** — LLM 只做两件事：写 DGP 程序、在确定性枚举出的选项中做选择。任何进入图表的数字都来自引擎计算。
   > 这条取代原 spec 的「Phase 3 不调用 LLM」。原规则真正保护的是算术完整性，而"选哪张图"不涉及任何数值。
3. **标注零成本且精确** — 所有 ground truth 由渲染器内部状态导出，不经过任何估计或人工标注。

---

## 6. 可证伪的主张

> 图表理解在 2026 年的失败是**感知与 grounding 失败**，不是推理失败。同时控制原子数据、聚合方式与渲染过程的生成器，能产出关于 grounding 与溯源的稠密且精确正确的监督信号——这类信号无法通过标注真实图表获得。用它训练能缩小真实基准上的差距。

验证与消融见 [01_target.md §4](01_target.md)。
