# Optimized prompt for Claude

**User:** Dingcheng Wang (dwang5460@gmail.com)  
**Created:** 3/27/2026 11:13:51  
**Updated:** 3/27/2026 16:38:46  
**Exported:** 3/27/2026 17:05:38  
**Link:** [https://chatgpt.com/g/g-p-69c44bd5798081918a0a51a646306d77-yuan-ti-shi-ci/c/69c6acaf-cc04-8332-a029-65828f5c1f59](https://chatgpt.com/g/g-p-69c44bd5798081918a0a51a646306d77-yuan-ti-shi-ci/c/69c6acaf-cc04-8332-a029-65828f5c1f59)  

## Response:
已思考若干秒

下面给你一套 **3-stage 线性执行的 Claude Chat 专用消息**，已经按你的新目标调整过：

你的目标不是只做“模块划分 + Sprint 8 状态检查”，而是：

1.  **搞清现状**
2.  **识别真正的 blockers**
3.  **把每个 blocker 从高层原因一路拆到细节决策**

所以这套 workflow 会把重点放在：

*   **现状建模**
*   **blocker 本质归因**
*   **从 abstract issue → implementation decision 的下钻**

并且每个 stage 都会产出一个 markdown 文档，方便你在 Claude Chat 里线性推进。

* * *

总体使用方式
======

按顺序执行：

1.  发 **Stage 1 message**
2.  等 Claude 生成 `01_phase2_current_state_map.md`
3.  开新 chat 或在同一 chat 继续发 **Stage 2 message**
4.  等 Claude 生成 `02_phase2_blocker_decomposition.md`
5.  再发 **Stage 3 message**
6.  等 Claude 生成 `03_phase2_decision_drilldown.md`

为了稳定，我建议：

*   **每个 stage 单独一个 chat**
*   把上一个 stage 的输出 markdown 作为当前 stage 的附加上下文贴进去
*   始终强调：**spec docs 优先于先前结论**

* * *

Stage 1
=======

目标
--

先把 **Phase 2 当前到底是什么状态** 讲清楚。  
这一步不要急着解决 blocker，而是建立一个可靠的“现状地图”。

输出文件
----

`01_phase2_current_state_map.md`

可直接复制的 Claude Chat 消息
---------------------

```
Use only the Phase 2 spec documents already available in project knowledge.

Your goal is to build a reliable current-state map of Phase 2 before doing any blocker diagnosis.

I do NOT want a generic summary. I want a document-grounded structural map of:
1. what Phase 2 is trying to achieve,
2. what its major functional areas are,
3. what has already been planned or developed through Sprint 8,
4. what remains incomplete, unclear, or blocked.

Please work in this order:

## Step 1 — Reconstruct the intended shape of Phase 2
Identify the major functional areas / major independent modules of Phase 2.
Group by functionality, not by sprint number, file name, or implementation artifact.

For each functional area, explain:
- what problem it is meant to solve
- what capabilities belong to it
- what other areas it depends on
- which source documents define it most clearly

## Step 2 — Map Sprint 1–8 coverage onto those functional areas
Using the sprint plan and alignment materials, determine for each functional area:
- what is already planned / developed by the end of Sprint 8
- what is only partially covered
- what is still missing
- what is blocked or deferred

## Step 3 — Clarify the current state
For each functional area, assign one of:
- Developed
- Partially developed
- Not developed
- Blocked / unresolved

Use these rules:
- “Developed” = meaningfully covered in Sprint 1–8 planning
- “Partially developed” = only some important sub-capabilities are covered
- “Not developed” = not covered by Sprint 8
- “Blocked / unresolved” = prevented by spec gaps, contradictions, or blocked backlog issues

If both “not developed” and “blocked” apply, prefer “Blocked / unresolved”.

## Required output
Write the result as a markdown document named:

# 01_phase2_current_state_map.md

Use exactly this structure:

# Phase 2 Current State Map

## 1. Phase 2 objective
A concise explanation of what Phase 2 is trying to build overall.

## 2. Major functional areas
For each area:
### [Functional area name]
- Purpose:
- Included capabilities:
- Dependencies:
- Main source basis:

## 3. Status after Sprint 8
For each area:
### [Functional area name]
- Status:
- Already covered by Sprint 8:
- Still missing:
- Blocked / unclear points:
- Evidence:

## 4. Cross-area observations
- Key architectural dependencies
- Main concentration of incomplete work
- Main concentration of blocked work
- Any document conflicts or ambiguity

## 5. Compact evidence table
| Functional area | Status after Sprint 8 | Why | Main source |

## Important constraints
- Use only project knowledge documents.
- Do not answer from intuition.
- Prefer implementation-specific documents when judging Sprint 8 coverage.
- If documents conflict, explicitly note the conflict and prefer the more implementation-specific source.
- Be precise and moderately detailed.
- Do not jump into solution design yet.
- Do not skip blocked items just because they are not implemented.
```

* * *

Stage 2
=======

目标
--

这一步不是重复 Stage 1，而是专门回答：

**这些 block 到底“本质上卡在哪”了？**

不是只说“这个没做”，而是把 blocker 拆成层级：

*   产品/系统层问题
*   规范层问题
*   抽象模型层问题
*   API/DSL/interface 层问题
*   执行/校验/错误恢复层问题

输出文件
----

`02_phase2_blocker_decomposition.md`

可直接复制的 Claude Chat 消息
---------------------

```
Use only the Phase 2 spec documents already available in project knowledge.

You should treat the goal of this stage as blocker diagnosis, not status reporting.

I want to understand the true nature of the blocked and unresolved parts of Phase 2.

Base your analysis on the Phase 2 documents, and if useful, use the current-state framing from the previous stage. However, if prior-stage conclusions conflict with source documents, prefer the source documents and explicitly correct the earlier conclusion.

Your job is to identify the major blockers and explain each blocker from high-level cause down to concrete implementation consequences.

## Task

Focus especially on items that are:
- blocked
- unresolved
- marked incorrect
- dependent on clarification
- deferred because the spec is not stable enough
- only partially implementable due to upstream ambiguity

For each blocker, do NOT just say “missing spec” or “not implemented”.
Instead, decompose it into layers.

For each blocker, explain:

1. **What the blocker is**
- The concrete blocked capability or area

2. **Why it is blocked at a high level**
- Missing system concept?
- Unstable product semantics?
- Unclear abstraction boundary?
- Contradictory requirements?
- Missing execution model?
- Missing validation model?
- Missing ownership of decisions?

3. **Where the ambiguity lives**
- In the conceptual model?
- In the SDK API?
- In the DSL / formula model?
- In metadata / schema semantics?
- In DAG / execution behavior?
- In validator or auto-fix behavior?
- In exception / retry / sandbox feedback semantics?
- In LLM integration assumptions?

4. **What implementation decisions are blocked by this**
- What specific coding or architecture decisions cannot be made safely yet?

5. **What partial work is still possible**
- What can still be implemented despite the blocker?

6. **What would need to be decided to unblock it**
- The minimum missing decisions required to move forward

## Required output
Write the result as a markdown document named:

# 02_phase2_blocker_decomposition.md

Use exactly this structure:

# Phase 2 Blocker Decomposition

## 1. Executive view
- What types of blockers dominate Phase 2
- Whether the blocked work is mostly conceptual, semantic, architectural, or implementation-detail related
- Which blockers are foundational vs downstream

## 2. Major blockers
For each blocker:

### [Blocker name]

#### A. Blocked capability
- ...

#### B. High-level cause
- ...

#### C. Exact ambiguity location
- ...

#### D. Downstream implementation decisions blocked
- ...

#### E. Partial implementation still possible
- ...

#### F. Minimum decisions needed to unblock
- ...

#### G. Evidence
- Cite the specific project documents / sections that support this diagnosis

## 3. Blocker dependency map
Show how blockers relate to one another:
- which blockers are root causes
- which blockers are downstream symptoms
- which blockers block multiple functional areas at once

## 4. Root-cause summary
Group blockers into a small number of root-cause categories, such as:
- conceptual model missing
- abstraction boundary unclear
- execution semantics unspecified
- API surface unstable
- validation / repair logic underdefined
- metadata semantics incomplete
- formula / expression system unresolved

For each category, explain:
- why it matters
- what it blocks
- how serious it is

## Important constraints
- This is not a generic risk list.
- Do not merely restate “blocked backlog” labels.
- Infer the actual reason each item is blocked from the documents.
- Distinguish root causes from symptoms.
- Prefer document-grounded diagnosis over broad speculation.
- Be explicit when multiple blocked items are actually caused by the same deeper problem.
```

* * *

Stage 3
=======

目标
--

这一步是你真正最想要的：

把每一个 blocker **从高层原因一路落到细节决策**。  
也就是把“我知道这里有问题”推进到：

*   到底缺哪个 mental model
*   哪个 abstraction 没定
*   哪个 API / DSL / schema decision 还没拍板
*   为什么不拍板就没法安全写代码
*   应该优先做哪类决策澄清

这一步最像 **从系统层 → operational model → implementation decision tree** 的桥接。

输出文件
----

`03_phase2_decision_drilldown.md`

可直接复制的 Claude Chat 消息
---------------------

```
Use only the Phase 2 spec documents already available in project knowledge.

This stage is a deep drilldown from blocker diagnosis into decision-level understanding.

I want each major blocker to be explained from:
high-level system reason → abstraction gap → architectural consequence → concrete implementation decisions that remain unsafe or undefined.

Base this analysis on the Phase 2 source documents. You may use the prior-stage blocker analysis as a starting point, but if prior-stage conclusions conflict with the source documents, prefer the source documents and explicitly correct the earlier conclusion.

## Task

For each major blocker, produce a decision drilldown that answers all of the following:

1. **System-level reason**
- Why does this issue exist at the product / system / conceptual level?
- What core mental model is missing, unstable, or contradictory?

2. **Abstraction-level gap**
- What abstraction has not been properly defined?
Examples:
- entity model
- declaration model
- formula / expression model
- dependency model
- execution model
- metadata model
- validator contract
- auto-fix contract
- exception handling contract
- sandbox feedback contract
- LLM responsibility boundary

3. **Architecture-level consequence**
- What component boundaries, data flows, or responsibility splits remain unclear because of that abstraction gap?

4. **Implementation-level decisions blocked**
- What concrete coding decisions remain unsafe?
Examples:
- class/interface design
- API signatures
- schema fields
- validation rules
- AST / DSL representation
- DAG node definitions
- retry / repair loop behavior
- prompt / LLM I/O contract
- error taxonomy
- metadata ownership
- serialization format

5. **Decision options**
- What are the plausible decision options implied by the documents?
- If the documents suggest multiple interpretations, list them clearly.

6. **Recommended decision focus**
- Which specific decisions should be clarified first?
- Which decisions are upstream and will unlock many downstream tasks?

## Required output
Write the result as a markdown document named:

# 03_phase2_decision_drilldown.md

Use exactly this structure:

# Phase 2 Decision Drilldown

## 1. Overall diagnosis
- What the Phase 2 blockers reveal about the current gap between system design and implementation design
- Which missing decisions are foundational
- Which missing decisions are secondary

## 2. Per-blocker drilldown

### [Blocker name]

#### A. System-level reason
- ...

#### B. Abstraction-level gap
- ...

#### C. Architecture-level consequence
- ...

#### D. Implementation-level decisions blocked
- ...

#### E. Plausible interpretation / decision options
- Option 1:
- Option 2:
- Option 3:

#### F. Recommended clarification priority
- What must be decided first
- What can wait
- Why

#### G. Evidence
- Ground this in the project knowledge documents

## 3. Cross-blocker synthesis
- Which blockers come from the same missing abstraction
- Which decisions would unlock the largest amount of implementation work
- Which areas are blocked because the system model is incomplete rather than because coding work is hard

## 4. Final takeaway
Summarize:
- the few deepest root problems
- the most important unresolved decisions
- the shortest path from current ambiguity to implementation-ready clarity

## Important constraints
- Do not give shallow advice.
- Do not jump directly to speculative redesign.
- Stay grounded in the source documents.
- Make the bridge from “high-level cause” to “low-level coding consequence” explicit.
- Be concrete enough that an engineer could use this output to guide the next clarification / design pass.
```

* * *

推荐执行策略
======

你这个任务其实很适合用下面这个线性节奏：

### 第一轮：建立地图

跑 Stage 1，得到：

*   Phase 2 的功能区块
*   Sprint 8 后的真实状态
*   哪些地方明显 incomplete / blocked

### 第二轮：识别根因

跑 Stage 2，得到：

*   blocker 列表
*   blocker 的根因分类
*   哪些是 root cause，哪些只是 symptom

### 第三轮：建立“从系统到代码”的桥

跑 Stage 3，得到：

*   mental model 缺口
*   abstraction gap
*   architecture consequence
*   implementation decisions blocked

这样你最终拿到的，不只是“哪里没做完”，而是：

**为什么没法做完，究竟是缺了哪层决策。**

* * *

给 Claude 的额外稳健补充句
=================

你可以在每个 stage 消息最后再追加这一小段，进一步减少跑偏：

```
Before writing the final document, silently check:
- Did I separate functional status from blocker diagnosis?
- Did I distinguish root causes from symptoms?
- Did I explicitly connect high-level ambiguity to implementation consequences?
- Did I rely on source documents rather than intuition?
```

* * *

模型建议
====

对这 3 个 stage，我建议这样用：

*   **Stage 1**：Sonnet
*   **Stage 2**：Sonnet，如果它开始泛化过度，再换 Opus
*   **Stage 3**：优先 Opus，如果你很在意“高层原因 → 细节决策”的质量

因为 Stage 3 是最吃推理质量的一步。

* * *

最后给你的一个判断
=========

如果你的真正目标是：

> “搞清现状，然后进一步梳理 block 的本质问题，每一个问题要说清高层原因到细节决策”

那么这 3-stage workflow 比之前那种“直接问一个总结问题”要强很多，因为它把任务分成了三个不同认知层次：

*   **State mapping**
*   **Blocker diagnosis**
*   **Decision drilldown**

这正好对应你现在最需要建立的理解路径。

我还可以继续把这 3 个 stage 再压缩成 **Claude Chat 最省上下文的 ultra-compact 版本**。



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)