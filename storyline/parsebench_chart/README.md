# Grounded Transcription — Chart Data Generation

程序化生成图表数据，产出的每个数值都带着它被画在哪里的坐标。目标能力是 **grounded transcription**：把图表转成结构化表的同时，给出每个值读取自哪块像素区域。

> 本目录是 [`../data_generation/`](../data_generation/) 的 ParseBench 定向版本。

---

## 流水线

```
 01  域池与场景     领域 → 场景上下文 + 分析意图
      ▼
 02  原子事实表     LLM 写 DGP 程序 → 行级事件表 + Schema Metadata
      ▼
 03  选图           SQL 投影枚举 → 依意图选择 → 两个判据过滤 → FigureSpec
      ▼
 04  渲染           风格向量独立采样 → 页面图像
      ▼
 05  溯源记录       渲染器同时输出 L0 几何 / L1 编码 / L2 溯源
      ▼
 06  输出与评测     溯源记录 → 训练目标 → 基准
```

---

## 文件

| | 内容 |
|---|---|
| [01_scenario.md](01_scenario.md) | 域池、场景实例化、分析意图 |
| [02_fact_table.md](02_fact_table.md) | SDK、生成引擎、Schema Metadata |
| [03_figure.md](03_figure.md) | 视图枚举、两个判据、FigureSpec |
| [04_render.md](04_render.md) | 八个采样维度、页面合成、Chart Registry |
| [05_provenance.md](05_provenance.md) | 三层溯源记录 |
| [06_output.md](06_output.md) | 输出格式、训练目标、评测与消融 |
| [related_work.md](related_work.md) | 截至 2026-08 的相关工作与定位 |

---

## 不变式

1. **原子粒度** — 事实表每行是一个不可分事件；聚合只发生在 SQL 投影里。
2. **LLM 不生产数值** — LLM 只做两件事：写 DGP 程序、在确定性枚举出的选项中做选择。进入图表的每个数字都来自引擎计算。
3. **标注零成本且精确** — 所有 ground truth 由渲染器内部状态导出，不经过估计或人工标注。
4. **风格与真值分离** — ground truth 由 FigureSpec 决定，对风格向量不变。同一 FigureSpec 可渲染 N 个视觉版本共享一份答案。
