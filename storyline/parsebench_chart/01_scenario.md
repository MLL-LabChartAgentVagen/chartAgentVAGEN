# 01 · 域池与场景

产出供 [02](02_fact_table.md) 使用的语义锚点：一个具体、真实、领域内的数据场景。不生成任何数据。

**本文**
1. [域池](#1-域池) → 2. [场景实例化](#2-场景实例化) → 3. [分析意图](#3-分析意图) → 4. [约束](#4-约束) → [附录：域池条目 schema](#附录域池条目-schema)

---

## 1. 域池

一次性构建、缓存复用的 200+ 细粒度子领域池。两级分类：Topic → Sub-topic。

每个子领域携带：名称、父 topic、复杂度层级（simple / medium / complex）、典型实体提示、典型指标提示（含单位）、时间粒度提示。

**生成方式**：先批量生成互不重叠的 topic，再逐 topic 生成 sub-topic。两级都要求"具体的分析情境"而非宽泛标签，并按复杂度三层均衡。

**质量控制**：embedding 余弦相似度去重（阈值 0.80）、复杂度三层均衡、topic 覆盖统计。同一个去重检查器供 topic、sub-topic、[§2](#2-场景实例化) 的场景三处使用。

**采样**：分层无放回。耗尽 80% 后重置。

---

## 2. 场景实例化

采样一个子领域 → 一次 LLM 调用产出场景上下文。

| 字段 | 内容 |
|---|---|
| `scenario_title` | 含时间段、机构、分析焦点的具体标题 |
| `data_context` | 谁收集、为何收集、何时收集 |
| `key_entities` | 3–8 个具名实体，使用真实世界名称 |
| `key_metrics` | 2–5 个可量化指标，含正确单位与合理取值范围 |
| `temporal_granularity` | hourly / daily / weekly / monthly / quarterly / yearly |
| `target_rows` | simple 200–500 · medium 500–1000 · complex 1000–3000 |
| `analytical_intent` | 见下节 |

**场景级去重**：对 `data_context` 做 embedding 去重（阈值 0.85），复用域池的同一个检查器。

**one-shot 示例**：prompt 中给一个完整的输入-输出样例。格式的稳定性直接决定 [02](02_fact_table.md) 能否可靠解析，示例的作用是限定输出结构。

---

## 3. 分析意图

2–4 条，每条是一个分析动作：这份数据被收集来回答什么问题。

它是 [03](03_figure.md) 选图的输入，也是 caption 的来源。

| 意图 | 蕴含的视图形态 |
|---|---|
| 识别瓶颈 / 找出表现最差的 | 排序比较 → 条形族 |
| 优化高峰时段 | 时间 × 实体 → 趋势族 / 热力图 |
| 理解构成变化 | 部分与整体随时间 → 构成族 |
| 检验两个指标是否相关 | 双数值 → 关系族 |

---

## 4. 约束

- 本阶段不出现任何图表类型词汇。数据源于业务需求，图表是数据的投影，选择权在 [03](03_figure.md)。
- 所有数字、实体、时间窗口须落在合理的真实世界范围内。
- 严格 JSON 输出，无附加说明。

---

## 附录：域池条目 schema

```json
{
  "id": "dom_001",
  "name": "ICU bed turnover analytics",
  "topic": "Healthcare",
  "complexity_tier": "complex",
  "typical_entities_hint": ["hospitals", "ICU wards", "patient categories"],
  "typical_metrics_hint": [
    {"name": "occupancy_rate", "unit": "%"},
    {"name": "length_of_stay", "unit": "days"}
  ],
  "temporal_granularity_hint": "daily"
}
```

池文件另存版本号、生成时间、复杂度分布与 topic 覆盖统计，用于检查均衡性。

复杂度层级的定义：

| 层级 | 含义 |
|---|---|
| simple | 单一实体类型，1–2 个指标，直接的时间序列 |
| medium | 多个相关指标，2 个以上实体类型 |
| complex | 嵌套层级，3 个以上相互依赖的指标 |
