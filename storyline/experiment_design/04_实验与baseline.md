# 04 · 实验设计与 baseline

> **回答的三个问题：**
> 1. Reviewer 必然要求的 baseline 有哪些？
> 2. 该报哪些 metric？
> 3. 怎么组织实验顺序，每个实验回答什么问题？

---

## TL;DR

- **8 个 baseline**（B0–B7），其中 **B3 (Passive-All)** 和 **B7 (Human-Junior)** 是新加但必须的。
- **6 个 metric**：在 storyline 已有 4 个之上补 **Bbox-Grounding** 和 **Hallucination Rate**。
- **6 个实验**（Exp A–F），其中 **Exp A (Channel Ablation)** 必须先做——它决定论文存在性。

---

## 4.1 Baseline 矩阵（按"反驳力"排序）

### 完整 8 个 baseline

| ID | 名字 | 协议设置 | 反驳的 reviewer 论点 | 是否已在 storyline |
|---|---|---|---|---|
| **B0** | Passive-VLM | 仅 $D_0$，无 action | "你确定 $D_0$ 不够吗？" | 已有 |
| **B1** | Random-Request | 每步均匀采样合法 ViewSpec | "agent 提升只是因为看得多" | 已有 |
| **B2** | Oracle-View-Set | 直接给 ground-truth $k^*$ 张最优视图 | "上限是什么" | 已有 |
| **B3** | **Passive-All** | 把所有 enumerate 出的视图一次性给 passive VLM | "VLM 已经够强，看全部就够了" — **killer baseline** | **新增** |
| **B4** | CSV-Channel | request_view 返回 CSV 表格而非 PNG | "你们测的是 chart 还是 SQL 规划" | 已有 |
| **B5** | PNG+CSV | 双模态都返回 | "视觉通道到底贡献多少" | **新增** |
| **B6** | ReAct-CoT | LangChain 标准 tool-augmented LLM，无 budget 概念 | "你们的协议比标准 agent loop 强吗" | **新增** |
| **B7** | Human-Junior | 招 5 个数据分析新手做 50 题 | "人类怎么样" | **新增** |

### 直观理解每个 baseline 在干什么

| Baseline | 比喻 |
|---|---|
| B0 | 把题目和**一张** PPT 截图给学生答 |
| B1 | 学生**随手翻**老师的资料夹 |
| B2 | 老师告诉学生**就看这 4 页** |
| B3 | 把老师全部的资料**一次性都给学生** |
| B4 | 把图都换成 Excel 表 |
| B5 | 图和表都给 |
| B6 | 学生用 ChatGPT + tools 自由发挥 |
| B7 | 找几个刚入行的数据分析师做盲测 |

### B7（人类 baseline）的具体安排

人类 baseline 是 reviewer 把 paper 当 benchmark 接受的硬数字——不能没有。但不需要大规模：

| 项 | 设置 |
|---|---|
| 题量 | 50 题（覆盖 4 个能力 × 4 个难度桶） |
| 人数 | 5 个 junior 数据分析师（< 3 年经验） |
| 每人时间 | 30 分钟 |
| 总成本 | 12.5 人时 ≈ 一天工作量 |
| 报告 | accuracy + 完成时间 + 每题用了几个视图 |

**值得做的理由：** "GPT-4o 用 $B_v = 4$ 达到人类 junior 水平的 78%" 这种数字一行字就堵了 reviewer 的 OOD 攻击。

---

## 4.2 Metric 体系

延续 [storyline §5](../storyline/research_storyline_zh.html) 已有的 4 个，补 2 个新的。

### 6 个 metric 总表

| Metric | 怎么算 | 为什么必报 |
|---|---|---|
| **Latent-QA Accuracy** | 按 [answer-schema](02_pipeline改进.md) 类型分别打分 | 主结果数字 |
| **Recovery@Schema** | F1 over (列存在性, 依赖边, 正交对) | World Recovery 的硬证据 |
| **Explanation Resolution** | $\{h_1, \ldots, h_4\}$ 上的 micro-F1（accept/reject） | Debunk 专属 |
| **Evidence Efficiency** | AUC of (accuracy vs $B_v$ used) | 同时奖励"答对"和"早停" |
| **Bbox-Grounding** | answer 引用的 bbox 与 GT bbox 的 IoU ≥ 0.5 比例 | **LDW 独有**，ChartMuseum 无对应 |
| **Hallucination Rate** | 在 Schema-Unanswerable 题上自信答非"insufficient"且 wrong 的比例 | **论文最有破坏力的数字** |

### 每个 metric 的具体公式

#### Latent-QA Accuracy

```
按题型分别算，最后取宏平均：
  Scalar:     |pred - truth| / truth <= tol  → 1，否则 0
  Ranking:    Kendall τ (pred, truth)
  Hypothesis: micro-F1 over (accept_set, reject_set)
  Existence:  1 if pred == "insufficient" else 0
```

#### Recovery@Schema

```
Recovery = F1(predicted_schema, true_schema)
  where each "fact" is one of:
    - column_existence:    (col_name, col_type)
    - dependency_edge:     (col_a, col_b)
    - orthogonal_pair:     (group_a, group_b)
```

#### Evidence Efficiency

```
对每个 model M:
  EE(M) = ∫₀^{B_max} accuracy(M, B_v=b) db / B_max

视觉上是 [Pareto 曲线下的面积]。
```

直观：**用同样预算更准** + **预算少时不掉太多** = 高 EE。这是论文图最有冲击力的一张（参考 [storyline §6](../storyline/research_storyline_zh.html) 的 Pareto 曲线）。

#### Bbox-Grounding

```
对每个 answer:
  cited_bboxes = answer.evidence
  gt_bboxes = ground_truth.evidence_bbox
  matches = [IoU(cb, gb) > 0.5 for cb, gb in pairs]
  grounding_score = mean(matches)
```

#### Hallucination Rate

```
仅在 [Schema-Unanswerable 题型](01_数据与问题.md) 上计算:
  hallucination = (confidence > 0.8) ∧ (answer != "insufficient") ∧ (answer wrong)
  rate = mean(hallucination)
```

这是**整篇论文最重要的单个数字**——直接对应 [00 命门](00_核心命门.md) 那句 "the most dangerous chart question is..."

---

## 4.3 Compute-fairness（强制要求）

**任何"agent 比 baseline 强"的对比，三个维度都要给数字。**

### 标准报告表（每个实验主表都附一张）

| Model × Protocol | Accuracy | Tokens (in/out) | API Cost ($) | Wall-clock (s) |
|---|---|---|---|---|
| GPT-4o / Passive-VLM | 0.42 | 1.2K / 0.3K | $0.008 | 1.5 |
| GPT-4o / Random-Request × $B_v=4$ | 0.51 | 8K / 2K | $0.072 | 18 |
| GPT-4o / LDW-Active × $B_v=4$ | **0.68** | 6.5K / 1.8K | $0.058 | 14 |
| GPT-4o / Passive-All | 0.55 | 22K / 2K | $0.180 | 45 |

观察这张表的设计：LDW 必须在 **token / cost / time 都 ≤ Passive-All** 的前提下，accuracy 严格 > Passive-All。

### 不报 compute 的代价

直接被打：
- "you spent 10x compute and got 5% gain"
- "your gains disappear when controlled for token budget"
- "this isn't an active exploration result, it's a more-compute result"

---

## 4.4 6 个实验的设计 + 顺序

### Exp A — Channel Ablation（**必须先做**）

| 项 | 内容 |
|---|---|
| **决定的事** | 论文是关于"chart understanding"还是"SQL planning" |
| **设置** | B4 (CSV-only) × B5 (PNG+CSV) × LDW (PNG-only) |
| **预期** | PNG > CSV-only on Latent-QA；CSV-only > PNG on pure value-retrieval 题 |
| **如果反着** | 论文转向 SQL-augmented agent，不再叫 chart understanding — **存在性危机** |

**这就是为什么必须先做。** 如果跑出来 CSV 完全压制 PNG，你需要重新思考整个 storyline。

### Exp B — Action Necessity

| 项 | 内容 |
|---|---|
| **设置** | model dim {GPT-4o, Claude, Qwen2-VL, ...} × protocol dim {B0, B1, B6, LDW} |
| **预期** | 协议轴的方差 > 模型轴的方差（参考 [VS-Bench](../storyline/research_storyline_zh.html#whynow)） |
| **核心数字** | 一张二维热力图，看清楚"动作策略 vs 模型规模"哪个 dominate |

### Exp C — Evidence Pareto

| 项 | 内容 |
|---|---|
| **设置** | $B_v \in \{2, 4, 8, 16, \infty\}$，分别报 accuracy + recovery |
| **预期** | LDW 在 $B_v = 16$ 仍达不到 oracle 在 $B_v = 4$ 的水平（参考 [storyline 预期图](../storyline/research_storyline_zh.html#experiments)） |
| **打点** | 这是论文里最有视觉冲击力的图 |

### Exp D — **Killer 实验**（详见 [05](05_killer实验.md)）

| 项 | 内容 |
|---|---|
| **设置** | B3 (Passive-All) vs LDW-Active × $B_v=4$ vs B2 (Oracle) |
| **预期** | LDW-Active > Passive-All 在 accuracy，且 hallucination 上差距更大 |
| **物理直觉** | 多视图反而加剧 dashboard illusion |

### Exp E — Capability Profile

| 项 | 内容 |
|---|---|
| **设置** | 把题集按 Read / Reveal / Reconcile / Debunk 4 类分别评估 |
| **回答** | 哪种能力最缺？现有 VLM 在哪个 capability 上掉得最厉害？ |
| **预期** | Debunk 最差，Read 最好——这是论文叙事链 |

### Exp F — OOD on Real Dashboards

| 项 | 内容 |
|---|---|
| **设置** | 50 张手工标注的真实 dashboard（Tableau Public / 政府开放数据） |
| **回答** | 合成 benchmark 能否泛化 |
| **预期** | LDW 在 OOD 上仍保持相对优势（差距收窄但单调） |

### 推荐执行顺序

```
Week 1-2:  Exp A (channel)         — 不通过则重新评估 storyline
Week 3-4:  Exp D (killer)          — 论文主结果
Week 5-6:  Exp B, C (necessity, pareto)  — 充实贡献
Week 7:    Exp E (capability)      — 叙事支撑
Week 8:    Exp F (OOD)             — 堵 generalization 攻击
全程:     Compute-fairness 表持续记录
```

---

## 4.5 章节小结

| 子主题 | 一句话 |
|---|---|
| Baseline | 8 个，重点是新增的 B3 (Passive-All) 和 B7 (Human-Junior) |
| Metric | 6 个，新增 Bbox-Grounding 和 Hallucination Rate |
| Compute-fairness | 强制每个主表附 token/cost/time |
| 实验顺序 | A → D → B,C → E → F |

---

## 下一步

- 想看 Exp D（killer 实验）的完整设计 → [05 killer 实验](05_killer实验.md)
- 想看可勾选的执行清单 → [TODO.md](TODO.md)
