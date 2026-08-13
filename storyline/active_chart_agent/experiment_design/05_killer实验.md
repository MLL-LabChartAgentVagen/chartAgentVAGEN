# 05 · Killer 实验：Passive-All vs LDW-Active vs Oracle

> **一个对比，证伪两条 reviewer 最常见的攻击线。**
>
> 如果你只能跑一个实验，跑这个。

---

## TL;DR

| | Passive-All | LDW-Active ($B_v=4$) | Oracle |
|---|---|---|---|
| **看到的视图数** | **所有**（10–30 张） | **4 张**，自己选 | **4 张**，被告知最优组合 |
| **Token 成本** | 最高 | 中等 | 中等 |
| **预期 accuracy** | 低-中 | **中-高** | 高 |
| **预期 hallucination rate** | **最高** | 中 | 低 |

**核心 claim：** Accuracy 顺序为 `Oracle > LDW-Active > Passive-All`，且 **hallucination 上 Passive-All 显著最高**。

---

## 5.1 这个实验为什么是 killer

### 它同时反驳的两条攻击线

**攻击线 1：** "VLM 已经够强，看全部视图就够了——不需要 active exploration。"

→ Passive-All baseline 直接证伪：把所有视图全塞给 VLM，它仍然不如 LDW-Active。

**攻击线 2：** "agent 提升只是因为看得多（即上下文增长效应）。"

→ Passive-All 看的**比** LDW-Active 还多（30 张 vs 4 张），如果 Passive-All 不如 LDW-Active，那提升就**不是**来自看得多。

### 一句话点睛

> "更多视图反而加剧了 dashboard illusion——LDW 的优势不在 perception，而在 selection。"

这一句话能放进 introduction，也能放进 abstract——它是论文的"标语"，从 storyline §2 那条 "the most dangerous chart question is the one it answers confidently from an intrinsically insufficient view" 推导出的实验对应物。

---

## 5.2 直观比喻：办公桌实验

想象给三个考生同一道题：

| 考生 | 桌面 |
|---|---|
| **Passive-All** | 桌上堆满 30 份资料，让你 30 分钟内回答 |
| **LDW-Active** | 桌上空的，你可以在 30 分钟内**指定** 4 份资料调过来 |
| **Oracle** | 桌上放着**最相关的 4 份**资料 |

直觉上你会预期 Oracle 最快最准。但更有意思的发现是 **Passive-All 不如 LDW-Active**——因为：
1. 信息过载导致注意力分散
2. headline 图的视觉冲击力压制了细节图
3. 没有"先后顺序"，agent 无法建立调查叙事

这正是 SwiftEats 案例的物理直觉。

---

## 5.3 完整 setup

### 数据准备

- 测试集：500 个 case files，覆盖 4 个能力 × 4 个难度桶
- 每个 case 在三个 condition 下运行同一题集
- **同一 seed**：保证视图集合在三个 condition 中完全一致，差异只在"agent 看到哪些"

### 三个 condition 的精确定义

#### Condition A — Passive-All

```python
all_views = enumerate_views(M, schema)  # ~10-30 张
prompt = build_prompt(
    case_brief=case.brief,
    hypotheses=case.H,
    questions=case.Q,
    images=[render_chart(v) for v in all_views],  # 全部 PNG
)
response = vlm(prompt)  # 一次性回答所有 Q
```

#### Condition B — LDW-Active

```python
agent.D0 = case.D0  # 起始 2-4 张图
budget = 4
while budget > 0 and not agent.terminated:
    action = agent.step(observation)
    if action.type == "request_view":
        v = extract_view(M, action.spec)
        png = render_chart(v)
        agent.observe(png)
        budget -= 1
    elif action.type == "answer":
        agent.record_answer(action.answer, action.evidence)
    elif action.type == "terminate":
        break
```

#### Condition C — Oracle

```python
# 对每题 q，预先算好 k*(q) 张最优视图
optimal_views = compute_oracle_set(case, q, M, schema)
assert len(optimal_views) == case.k_star_max  # 即 max k* across Q
prompt = build_prompt(
    case_brief=case.brief,
    hypotheses=case.H,
    questions=case.Q,
    images=[render_chart(v) for v in optimal_views],
)
response = vlm(prompt)
```

### Compute-fairness 控制

| Condition | 输入 token 估算 | 是否被限制 |
|---|---|---|
| Passive-All | ~22K（30 张图 × ~700 token/图） | 不限 |
| LDW-Active | ~6-8K（4 张图 + thinking） | 不限 |
| Oracle | ~3-4K（4 张图） | 不限 |

注意：Passive-All 用的 token 是 LDW-Active 的 ~3 倍——所以如果 LDW-Active 赢了，是在 **compute 不利的情况下赢的**。这让结论更强。

---

## 5.4 预期结果

### 主表

| Condition | Latent-QA Acc | Recovery | Hallucination Rate | Token cost (avg) |
|---|---|---|---|---|
| Passive-All | 0.52 | 0.41 | **0.38** | 22K |
| LDW-Active | **0.68** | **0.62** | 0.15 | 7K |
| Oracle | 0.81 | 0.78 | 0.08 | 4K |

（具体数字预估，待跑出）

### 关键观察

1. **Oracle 是天花板** — 给出 active exploration 能达到的上限。
2. **LDW-Active 应在 Oracle 75–85% 区间** — 说明探索策略离最优有 gap 但显著好于盲选。
3. **Passive-All 不仅 accuracy 低，hallucination 也 highest** — 这是论文的"震撼数字"。

### 主图（推荐）

```
   Accuracy
     │
1.0  │           ╳ Oracle
     │
     │           ●  LDW-Active
     │
     │
     │     ⌧ Passive-All
0.0  │_______________
     0   4   30  视图数

注: 横轴不是预算，而是"实际看到的视图数"
    Passive-All 看了最多，但 accuracy 反而低
    "看多 ≠ 看准"
```

加一个二级图，对比 hallucination rate（用柱状图），让 Passive-All 那根柱子最高——视觉上"压垮"它。

---

## 5.5 几个必须做的子分析

### 子分析 1：按难度桶分解

| 难度 | Passive-All Acc | LDW-Active Acc | Δ (LDW − PA) |
|---|---|---|---|
| Easy ($k^* \leq 1$) | 0.78 | 0.82 | +4 |
| Medium ($k^*=2$) | 0.56 | 0.69 | +13 |
| Hard ($k^*=3$) | 0.41 | 0.65 | **+24** |
| Very Hard ($k^* \geq 4$) | 0.28 | 0.61 | **+33** |

**预期模式：** 难度越高，LDW 的优势越大——这是 storyline §6 的 Pareto 曲线在 condition 维度的对应物。

> 直观解释：简单题 $D_0$ 已含答案；难题需要叙事性的"分步调查"，passive 无法做到。

### 子分析 2：按能力分解

| 能力 | Passive-All | LDW-Active | Δ |
|---|---|---|---|
| Read | 0.71 | 0.74 | +3 |
| Reveal | 0.55 | 0.69 | +14 |
| Reconcile | 0.43 | 0.66 | **+23** |
| Debunk | 0.31 | 0.61 | **+30** |

**预期模式：** Debunk 上差距最大——因为 Passive-All 拿到所有视图后无法决定"哪些视图值得交叉验证"。

### 子分析 3：失败模式对比

对 LDW 赢的题，看 Passive-All 错在哪：

| 失败类型 | 频率 |
|---|---|
| 被 headline 图带跑（dashboard illusion） | ~40% |
| 注意力分散到无关图（信息过载） | ~30% |
| 把矛盾视图当噪声忽略 | ~20% |
| 其他 | ~10% |

这个分析做一张定性 figure，配几个具体例子（SwiftEats 18 分钟就是首选），论文的可读性立刻上一个台阶。

---

## 5.6 这一组数据怎么放进 paper

### Abstract 那一行

> "Our killer experiment shows that giving a passive VLM all relevant chart views actually **degrades** accuracy and **doubles** hallucination rate compared to letting it select 4 views actively — selection, not perception, is the bottleneck."

### Introduction 末尾

放上面那个主图 + "如果 active exploration 不重要，Passive-All 应该 ≥ LDW-Active；我们的实验显示恰恰相反"。

### Main results section

完整的 5.4 + 5.5 子分析。

### Discussion

用 5.5 子分析 1 的"难度越高、差距越大"模式 + 子分析 3 的失败模式，建立"为什么 selection 比 volume 重要"的机制性叙事。

---

## 5.7 如果实验失败怎么办

### 情况 1：Passive-All ≈ LDW-Active

→ **重新检查 [00 命门](00_核心命门.md)。** 这意味着 active exploration 不必要。可能的补救：
- 增大题集中 Hard / Very Hard 题的比例
- 加强 dashboard illusion 的强度（让 Passive-All 更容易被骗）
- 缩小 $B_v$（$B_v=2$ 时差距应更明显）

### 情况 2：LDW-Active < Passive-All

→ **严重问题。** 可能的原因：
- agent 的 ViewSpec 解析失败率太高（→ [03 §3.2](03_动作空间.md) 兜底）
- $B_v=4$ 不够（→ 改 $B_v=6$ 或允许 refine_view）
- D₀ 太弱（→ [01 §1.1](01_数据与问题.md) D₀ 三档实验该上场了）

### 情况 3：LDW-Active < Oracle by a lot（gap > 30%）

→ 这是机会而非问题——说明探索策略有大量提升空间，可以作为论文的 future work / community challenge。

---

## 5.8 章节小结

| 项 | 内容 |
|---|---|
| 实验目标 | 证伪 "VLM + 全视图 = 解决问题" 这条 reviewer 攻击线 |
| 三个 condition | Passive-All / LDW-Active / Oracle |
| 主指标 | Accuracy + Hallucination Rate + Token Cost |
| 必做子分析 | 按难度 / 按能力 / 失败模式 |
| 在论文里的位置 | Abstract / Intro / Main Results / Discussion 各引一次 |

---

## 下一步

- 想看怎么把这些工作分阶段做 → [TODO.md](TODO.md)
- 想回看为什么这个实验是命门 → [00 核心命门](00_核心命门.md)
