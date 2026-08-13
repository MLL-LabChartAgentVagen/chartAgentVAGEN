# ChartAgent / LDW 实验设计

> **这是什么：** 一套针对 [research_storyline_zh.html](../storyline/research_storyline_zh.html) 中 LDW 协议的实验落地方案。
>
> **怎么读：** 建议先看 [00 核心命门](00_核心命门.md)（一页搞清楚论文的存在性命题），然后按维度 1→2→3→4 顺序看实施细节，最后看 [05 killer 实验](05_killer实验.md) 和 [TODO](TODO.md)。

---

## 一句话定位

**LDW 的整篇论文成立与否，取决于一个命题：**

> 在视图预算 $B_v$ 给定时，agent **选择"看什么"** 的能力，比 **"看了多少"** 更决定下游表现。

整套实验的任务就是**用数据把这一句话从 claim 变成事实**——同时排除两个最常见的反驳。详见 [00 核心命门](00_核心命门.md)。

---

## 一张图看懂实验栈

```
                  ┌────────────────────────────────────────────┐
                  │   命门：active selection > naive viewing     │
                  │   （00_核心命门.md）                          │
                  └────────────────────────────────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
       数据底料                    管线质量                    评估装置
            │                          │                          │
   ┌────────▼─────────┐      ┌─────────▼─────────┐      ┌─────────▼──────────┐
   │ 01_数据与问题      │      │ 02_pipeline改进   │      │ 03_动作空间          │
   │ • D₀ 三档           │      │ • leakage 隔离     │      │ • ViewSpec JSON    │
   │ • k* 难度          │      │ • 答案 schema     │      │ • bbox 渲染层       │
   │ • 25% 带毒题        │      │ • k* 配额          │      │ • 5 chart families │
   └────────┬─────────┘      └─────────┬─────────┘      └─────────┬──────────┘
            │                          │                          │
            └──────────────────────────┼──────────────────────────┘
                                       │
                              ┌────────▼─────────┐
                              │ 04_实验与baseline │
                              │ • 8 baseline     │
                              │ • 6 metric       │
                              │ • compute-fair   │
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │ 05_killer 实验    │
                              │ Passive-All      │
                              │  vs LDW-Active   │
                              │  vs Oracle       │
                              └──────────────────┘
```

---

## 4 个维度 + killer 实验 — 快速索引

| 文档 | 一句话 | 主要交付 |
|---|---|---|
| [01 数据与问题](01_数据与问题.md) | 把 D₀ 设计成实验变量，用 k\* 重新定义难度，强制混入 25% 带毒题 | 三档 D₀ 构造规则；k\* 自动计算；3 类 unanswerable 题型 |
| [02 pipeline 改进](02_pipeline改进.md) | 隔离 LLM 的角色，让答案空间可机评，给 k\* 留高难度配额 | hypothesis 反向规则化生成；answer-schema；500 题 human spot-check |
| [03 动作空间](03_动作空间.md) | request_view 输出 ViewSpec JSON，导出 element-level bbox，首发 8 种图 | matplotlib bbox collector；ViewSpec 解析兜底；refine_view 可选 |
| [04 实验与 baseline](04_实验与baseline.md) | 8 个 baseline + 6 个 metric + 必须的 compute-fairness 表 | B0–B7 全矩阵；含人类小样本 baseline；hallucination rate |
| [05 killer 实验](05_killer实验.md) | **一个对比就证伪两条 reviewer 攻击线**：Passive-All vs LDW-Active vs Oracle | 完整 setup + 预期结果 + 物理解释 |

---

## 整体实验矩阵（一图速览）

| 实验 | 名字 | 对比谁 | 主要回答 |
|---|---|---|---|
| **Exp A** | Channel Ablation | PNG-only / CSV-only / both | "我们测的是 chart 还是 SQL？" — **决定论文存在性，必须放主文** |
| **Exp B** | Action Necessity | passive / random / planned × VLM 家族 | "动作策略 vs 模型规模哪个更重要？" |
| **Exp C** | Evidence Pareto | $B_v \in \{2,4,8,16,\infty\}$ | "瓶颈在感知还是探索策略？" |
| **Exp D** | **Killer** | Passive-All / LDW-Active / Oracle | "看多 ≠ 看准；selection > volume" |
| **Exp E** | Capability Profile | Read / Reveal / Reconcile / Debunk 分别评估 | "哪种能力最缺？" |
| **Exp F** | OOD on Real Dashboards | 50 张手标真实 dashboard | "合成 benchmark 能 generalize 吗？" |

> **建议顺序：** Exp A（先做，能否继续做这篇论文取决于它）→ Exp D（killer，主结果）→ Exp B/C/E（充实贡献）→ Exp F（堵 OOD 问）

---

## 执行清单

📋 见 [TODO.md](TODO.md) ——按 P0 / P1 / P2 排序，可勾选。

---

## 命名约定

| 符号 | 含义 |
|---|---|
| $M$ | 隐藏主表（Master Table，agent 看不到） |
| $S$ | schema metadata（[phase 2 §2.6](../data_generation/phase_2.md) 输出） |
| $D_0$ | 初始仪表板（agent 起步时能看到的 2–4 张图） |
| $H = \{h_1, \ldots, h_4\}$ | 候选解释集 |
| $Q$ | 该 case 下要回答的问题集 |
| $B_v$ | 视图预算（request_view 次数上限） |
| $B_p$ | 数据点预算（point 次数上限） |
| **$k^*$** | **某个问题理论最小所需视图数** — 难度的真正度量 |

---

## 贯穿全文的 running example

整套文档都用 storyline 里的 **SwiftEats 18 分钟外卖奇迹** 案例做锚点：

> SwiftEats 上线新 AI 调度算法，headline："31 min → 18 min"。
> 真相：headline 只覆盖 pickup→dropoff、只算成功订单、外环被悄悄放弃。
> Agent 必须用 4 步视图请求（READ → REVEAL → RECONCILE → DEBUNK）拆穿这个 dashboard illusion。

每篇文档遇到抽象概念时都会回到这个例子做翻译。
