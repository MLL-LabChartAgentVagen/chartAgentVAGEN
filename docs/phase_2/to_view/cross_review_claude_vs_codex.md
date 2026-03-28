# Phase 2 交叉审查报告：Claude (Opus 4.6) vs Codex (GPT-5.4)

**审查基准**：Claude 的3阶段输出为正确性基准；同时识别 Codex 的增量发现。

**Claude 输出**（3份）：

| 文件 | 阶段目标 |
|---|---|
| `blocker_analysis/01_phase2_current_state_map.md` | 现状建模：功能域 2A–2K × Sprint 8 后覆盖状态 |
| `blocker_analysis/02_phase2_blocker_decomposition.md` | Blocker 本质归因：8 个 blocker × 6 维分解 + 依赖图 + 5 类根因 |
| `blocker_analysis/03_phase2_decision_drilldown.md` | 决策下钻：每个 blocker 从系统层 → 抽象层 → 架构层 → 实现决策 + Option 分析 |

**Codex 输出**（5份）：

| 文件 | 阶段目标 |
|---|---|
| `outputs/01_evidence_matrix.md` | 多文档证据矩阵：按文档角色 × 主题抽取事实 |
| `outputs/02_delivery_state.md` | 交付状态评估：3 个完成度镜头 + 风险结论 |
| `outputs/03_blockers_and_spec_gaps.md` | Blocker 与 Spec Gap 结构建模：7 个 blocker + 缺失/矛盾分类 |
| `outputs/04_clarifications_and_spec_patches.md` | 澄清问题 + Spec Patch Backlog P01–P11 |
| `outputs/05_resolution_plan.md` | 解锁路径 + 责任切分 + 执行分类 |

---

# 第一部分：Codex 正确性审查

## 1.1 核心数字验证

| 指标 | Claude | Codex | 判定 |
|---|---|---|---|
| 总子任务数 | 108 | 108 | PASS |
| 可排期子任务 | 73 (40 SPEC_READY + 33 NEEDS_CLARIFICATION) | 73 (40 SPEC_READY + 33 NEEDS_CLARIFICATION) | PASS |
| BLOCKED 子任务 | 24 | 24 | PASS |
| SPEC_INCORRECT 子任务 | 10 | 10 | PASS |
| Deferred NEEDS_CLARIFICATION | 1 (8.1.3) | 1 (8.1.3) | PASS |
| Blocked wall 总计 | 35 (24+10+1) | 35 (24+10+1) | PASS |
| Sprint 完成率 | 8/8 = 100% | 8/8 = 100% | PASS |
| 已排期完成率 | 73/73 = 100% | 73/73 = 100% | PASS |
| 全量覆盖率 | 73/108 ≈ 67.6% | 73/108 = 67.6% | PASS |
| Critical Path Blockers 数量 | 7 (alignment map) + 1 (A12 独立提升) | 7 (alignment map 对齐) | PASS (差异在分析选择，不是事实错误) |

**结论**：Codex 的所有核心数字与 Claude 完全一致，均可追溯到 source docs。无数字层面的错误。

## 1.2 Blocker 识别对比

### Claude 的 8 个 Blockers

| 编号 | 名称 | 对应 Finding |
|---|---|---|
| 2.1 | Schema Metadata Contract | C3, C8, C9, C13, C3a, A2a |
| 2.2 | Formula DSL Grammar | A3 |
| 2.3 | Distribution Family Parameter Schema | A5, A5a, A1, A1b |
| 2.4 | Pattern Type Behavioral Triples | A8, B6, C1, C10 |
| 2.5 | Post-Processing Invariant Contract | B2, B3, B7, C5, C6 |
| 2.6 | Phase 1→Phase 2 Typed Interface | D1 |
| 2.7 | Cross-Group Default Semantics | A12 |
| 2.8 | Censoring Schema | A4 |

### Codex 的 7 个 Blockers

| 编号 | 名称 | 对应 Finding |
|---|---|---|
| 1 | Schema Metadata Completeness | C3, C8, C9, C13 |
| 2 | Formula DSL Grammar | A3 |
| 3 | Distribution Family Parameter Specification | A1, A5 |
| 4 | Pattern Type Full Specification | A8, B6, C1, C10 |
| 5 | L2 vs Pattern Injection + Auto-Fix Mutation Model | B2, B3, B7, C5, C6 |
| 6 | Phase 1→Phase 2 Interface Contract | D1 |
| 7 | Censoring Schema | A4 |

### 差异分析

**关键差异**：Claude 将 A12 (Cross-Group Default Semantics) 提升为独立 Blocker 2.7；Codex 将其降为 `Missing/Undefined Issues` 表中的 P1 级条目。

**判定**：Claude 的处理更合理。理由：
- A12 在 `2_phase2_gap_analysis.md` post-audit 版本中被标为 **CRITICAL** 级别
- 它影响 4.1.1（skeleton builder 采样逻辑），这是引擎的核心执行路径
- §2.2 的 "opt-in, not default" 措辞与当前唯一可行假设（默认独立采样）存在语义冲突
- Codex 虽然在 Stage 3 的 Missing/Undefined 表和 Stage 4 的 P07 中覆盖了这个问题，但没有给予独立的 blocker 级深度分析

**不过**：Codex 的判断并非错误，而是一种更保守的分类选择——它严格按 alignment map 的 7 个 Critical Path Blockers 来组织，将 A12 作为后续 patch 而非主链 blocker。这在操作层面是可接受的。

## 1.3 根因分析结构对比

### Claude：3 类根因 + 分层依赖

```
类型1: 缺失共享数据契约 (Metadata, Distribution, Phase 1 interface)
    ↓ 是基础
类型2: 未指定的行为三联体 (Pattern types, Auto-fix failure modes)
    ↓ 依赖类型1
类型3: 矛盾的组合行为 (Auto-fix self-contradiction, L2 vs pattern, L1 vs realism)
    ↓ 依赖类型1 + 类型2
```

**核心洞察**：这3类之间有严格的分层依赖关系，解决类型1（~5个契约级决策）可立即解锁约20个子任务，同时为类型2和类型3的解决提供前提。

### Codex：4 类问题本质

1. **Missing-definition class**：FormulaDSL, DistributionFamilySpec, PatternSpec, CensoringSpec, ScenarioContext, soft-fail policy
2. **Incomplete schema/contract class**：schema_metadata, distribution keys/domain, target grammar, multi-column on, scale, non-daily freq, dirty-value
3. **Cross-module conflict class**：metadata vs validator reads, pattern injection vs L2, realism vs L1, A12 标签漂移
4. **Validation/auto-fix/orchestration semantic class**：L2 pre/post-injection、mutation target、retry persistence、soft-fail policy

### 判定

两种分类都是正确的，但服务于不同目的：

- **Claude 的分类**更适合**战略决策**：它告诉你"先做什么类型的事能最大化解锁"
- **Codex 的分类**更适合**执行跟踪**：它告诉你"每个问题的本质类型是什么，应该用什么方式去解决"

Claude 的独特贡献在于发现了"3类根因之间的依赖关系"——这是 Codex 没有显式建立的结构性洞察。

## 1.4 Blocker 依赖关系分析

### Claude 的 ASCII 依赖图（核心洞察）

Claude 02 文档 §3 提供了完整的依赖结构图（此处简化复述）：

```
独立根因（可并行解决）：
  Blocker 1 (Metadata)    Blocker 2 (Formula DSL)    Blocker 3 (Distribution)
        ↓                         ↓                          ↓
        └─────────────────────────┼──────────────────────────┘
                                  ↓
                        Validator L2 被完全阻塞
                                  ↓
复合 Blocker：
  Blocker 4 (Pattern Triples) ───┤
                                  ↓
  Blocker 5 (Post-Processing Invariant + Auto-Fix Mutation)
                                  ↓
接口 Blocker：
  Blocker 6 (Phase 1 Contract) ──┤
                                  ↓
                        Pipeline Orchestrator (终端依赖)

孤立 Blocker（随时可解决）：
  Blocker 7 (Cross-Group Default)    Blocker 8 (Censoring)
```

### Codex 的处理

Codex 引用了 alignment map 的解锁顺序 `1→2→3→6→4→5→7`，但没有自己构建结构化的依赖分析。在 Stage 5 的 execution order 表中给出了 7 步顺序，理由是"source-backed 依赖顺序"，但未解释为什么 Blockers 1/2/3 可以并行。

### 判定

**Claude 显著胜出**。Claude 的依赖图是整个交叉审查中最具结构性洞察力的单一产出——它明确了：
- Blockers 1, 2, 3 是独立根因，可以并行解决（Codex 的线性顺序暗示了不必要的串行性）
- L2 Validator 是同时依赖3个根因的瓶颈节点
- Blocker 5 是最下游的复合 blocker，最后解决

## 1.5 Codex 纠偏声明验证

Codex 在 Stage 3/4/5 中反复提出 4 个纠偏，每个都需对照 source docs 验证：

### 纠偏 1：A12 已重定义

**Codex 声称**：`A12` 在 post-audit 中被重定义为 "undeclared cross-group default semantics"，不再表示 `generate()` 返回类型歧义。

**验证**：正确。`phase_2.md` §2.8 与 task hierarchy `1.1.3` 已明确 `generate(self) -> Tuple[pd.DataFrame, dict]`，返回类型不是活跃 gap。A12 的当前含义是 §2.2 的 "opt-in, not default" 与实际缺失默认语义之间的矛盾。

**Claude 对比**：Claude 在 Blocker 2.7 中也使用了 A12 的新含义（cross-group default semantics），但没有显式声明这是一个纠偏。

**判定**：PASS。Codex 的纠偏更严谨地标注了 finding 含义的版本变化。

### 纠偏 2：C5 不是"完全未定义"

**Codex 声称**：C5 的方向已由 task hierarchy `11.1.4/11.1.5` 给出（sequential composition, no escalation, max 6 attempts），不应继续表述为 "完全没有顺序定义"。

**验证**：正确。Task hierarchy 确实在 `11.1.4` 和 `11.1.5` 中把 sequential/no-escalation/max-6 写成了实现合同。问题在于这些规则没有被回写到 `phase_2.md` 这个权威 spec 中，所以是"跨文档未冻结"而非"纯空白"。

**Claude 对比**：Claude 在 Blocker 2.5 §C 中表述为 "The §2.7/§2.9 loop composition is inferable (sequential, per §2.7 step 3) but never formalized"，含义与 Codex 一致但措辞不同。

**判定**：PASS。两者结论一致，Codex 更明确地指出了具体的 source 锚点。

### 纠偏 3：D1 是 typed formalization 问题

**Codex 声称**：D1 阻塞的是 typed `ScenarioContext` 的正式化，不是基础 JSON 注入能力。

**验证**：正确。`3_phase2_implementation_alignment_map.md` 已明确现有 JSON injection path 存在。

**Claude 对比**：Claude 在 Blocker 2.6 §B 中做了完全相同的观察："This blocker is about **formalization**, not basic capability."

**判定**：PASS。两者完全一致。

### 纠偏 4：Subtask 编号在不同文档间不一致

**Codex 声称**：Task hierarchy 已更新为 `4.2.5-4.2.8` / `8.3.3-8.3.5`，但 alignment map 和 sprint plan 仍用旧号 `4.2.3/4.2.4/8.3.5`。

**验证**：正确。这是跨文档维护不同步的问题。

**Claude 对比**：Claude 全程使用与各 source doc 原文一致的编号，但没有显式指出这种跨文档不一致。

**判定**：PASS。这是 Codex 独有的增量发现。

## 1.6 决策选项分析对比

Claude Stage 3 为每个 blocker 提供了明确的 **Option 1/2/3** 和 trade-off 分析：

| Blocker | Claude 决策选项 | Codex 对应 |
|---|---|---|
| Metadata Schema | Option 1: 扩展§2.6 example / Option 2: typed Python model / Option 3: JSON Schema + auto-gen | P01/P02 列出 minimum completion criteria，但无 Option 对比 |
| Formula DSL | Option 1: 最小算术 DSL / Option 2: 扩展含函数白名单 / Option 3: Python expression subset | P03 列出 must-answer questions 问 Spec Owner，但无 Option 对比 |
| Distribution Families | Option 1: 7-family, defer mixture / Option 2: 7+mixture 分离 schema / Option 3: 采用 scipy 命名 | P04/P05 分别问 Rules Owner 和 Spec Owner，但无 Option 对比 |
| Pattern Types | Option 1: 全部4类现在 / Option 2: defer 全部4类 / Option 3: 选做2类 | P06 问 Rules Owner，但无 Option 对比 |
| Validation Phase | Option A: 分阶段验证 / Option B: 单次+排除掩码 / Option C: 双次生成 | P08 问 Architect/Validator Owner，但无 Option 对比 |
| Auto-Fix Mutation | Option X: mutate simulator / Option Y: post-process DataFrame / Option Z: modify script source | P08 同上 |

**判定**：Claude 在决策分析深度上**显著胜出**。Codex 的 Stage 4 把决策转化为"问题"给 owner，但没有像 Claude 那样预先分析各选项的 trade-off。对于需要做决策的人来说，Claude 的 Option 分析能更快推动决策收敛。

## 1.7 时间估算

Claude Stage 3 §4 提供了唯一的时间估算：

| 决策 | 设计工作量 | 解锁子任务数 |
|---|---|---|
| Metadata schema 字段规格 | ~1 天 | ~12 |
| Distribution family 参考表 | ~2 小时 | 7 |
| Formula DSL 运算符白名单 | ~1 小时 | 4+ |
| Validation phase assignment | ~30 分钟 | ~9 (与 metadata 重叠) |
| Auto-fix mutation model | ~30 分钟 | 修复 retry loop |
| **总计** | **~1–2 天设计规格工作** | **34→~9 blocked subtasks** |

Codex 没有提供任何时间估算。

**判定**：Claude 独有贡献。这些估算虽然是粗略的，但对项目管理决策（优先投入设计资源而非编码人力）非常关键。

---

# 第二部分：Claude 未能找到的部分（Codex 增量发现）

## 2.1 A13: Pattern `target` 表达式 grammar 缺失

**严重程度**：CRITICAL（Gap Analysis post-audit）
**价值评级**：HIGH

### Codex 的发现

Codex 在 `01_evidence_matrix.md` §4 中将 A13 列为独立 CRITICAL finding：

> §2.1.2, §2.9 使用 `df.query(target)`，但未定义允许的运算符、列类型、引用规则或安全边界。pattern injection 与 L3 都存在执行/安全不确定性。

Codex 在 `04_clarifications_and_spec_patches.md` 的 Blocker 4 / Theme 4 中进一步展开：

> `[Architect]` `target` 是否定义为受限过滤 DSL，而不是直接暴露 `df.query()`；若是，允许的比较运算、逻辑运算、列类型、引用方式、安全边界分别是什么？

并在 P06 patch 中将 target grammar 纳入 pattern triple 的 companion spec。

### Claude 的覆盖情况

Claude 在 Blocker 2.4 (Pattern Type Behavioral Triples) 的 §D.5 中仅简短提及 "LLM prompt guidance"，没有将 target grammar 作为独立安全问题分析。在功能区域 2J (LLM Code-Generation Prompt) 中也未涉及 target grammar 的安全边界。

### 为什么这很重要

`df.query()` 在 pandas 底层使用 `numexpr` 或 `eval()`，如果 `target` 字符串来自 LLM 生成的代码且未经过 grammar 限制，存在：
- **代码注入风险**：LLM 可能生成包含任意 Python 表达式的 target
- **执行不确定性**：不同 pandas 版本的 `query()` 行为可能不一致
- **Pattern injection 与 L3 的语义对齐**：如果 target 的解释在 engine 和 validator 中不一致，pattern 的注入范围与检测范围可能不匹配

## 2.2 A14: Sandbox Security Policy

**严重程度**：CRITICAL（Gap Analysis post-audit）
**价值评级**：HIGH

### Codex 的发现

Codex 在 `01_evidence_matrix.md` §4 中列出：

> §2.5, §2.7 只要求 pure valid Python，但没有 import/resource/time limit policy。sandbox 可执行边界不明确，存在代码执行风险。

在 `04_clarifications_and_spec_patches.md` 中设计了 **P09 (Sandbox Security Policy)** patch：

> `[Architect / Security Owner]` LLM-generated code 的 sandbox policy 是否要在 spec 中明确 import whitelist、timeout、resource limit、I/O / network boundary？

Minimum Completion Criteria：明确 allowed imports、I/O/network/process boundary、timeout、resource limits、error classification 与 audit expectations。

### Claude 的覆盖情况

Claude 在功能区域 2G (Execution-Error Feedback Loop) 的 "Still missing" 中简述：

> Security hardening (import whitelist, resource limits, timeout) — deferred until spec defines policy.

在 Blocker 分析中只是在 2G 状态描述中一笔带过 "A14: No security/sandbox policy specified"，没有为其设计独立 patch 或决策分析。

### 为什么这很重要

Phase 2 的核心工作流是 LLM 生成 Python 代码 → sandbox 执行。如果 sandbox 没有 import whitelist 和资源限制：
- LLM 可能生成 `import os; os.system(...)` 等危险代码
- 无超时限制可能导致无限循环消耗资源
- 无网络限制可能导致数据泄露

虽然 A14 不直接阻塞 data pipeline 的核心功能，但它是 **生产环境部署的硬性前提**。

## 2.3 Subtask 编号跨文档漂移

**价值评级**：MODERATE

### Codex 的发现

Codex 在 Stage 3/4/5 中反复指出（纠偏4）：

> `1_phase2_implementation_task_hierarchy.md` 已把 structural/L2 相关 subtasks 更新为 `4.2.5-4.2.8 / 8.3.3-8.3.5`；`3_phase2_implementation_alignment_map.md` 与 `4_phase2_sprint_plan.md` 中仍保留部分旧号 `4.2.3/4.2.4/8.3.5`。

### Claude 的覆盖情况

Claude 全程使用各 source doc 原文中的编号，没有发现或报告这种跨文档不一致。

### 为什么这很重要

如果在后续 Sprint 9–13 的排期中混用新旧编号，会导致：
- 依赖映射错误（某个 subtask 被认为已解锁但实际未解锁）
- 完成声明错误（标记了旧编号为完成，但对应的新编号仍在 blocked）
- 跨团队沟通混乱

Codex 建议以 task hierarchy 现行编号为执行锚点，是合理的。

## 2.4 C7: Validator Helper Contract 缺失

**价值评级**：MODERATE

### Codex 的发现

Codex 在 `01_evidence_matrix.md` §4 中列出 C7：

> §2.9 L2 直接调用 `_get_measure_spec()` 与 `iter_predictor_cells()` helper，但规范未定义 helper 接口与输出。stochastic L2 无法按规格实现。

在 `03_blockers_and_spec_gaps.md` §4 的 Missing/Undefined Issues 表中列为 P1：

> validator helper contract：`_get_measure_spec()`、`iter_predictor_cells()`、`_verify_dominance_change()` 的输入/输出 contract 未定义。

### Claude 的覆盖情况

Claude 在 Blocker 2.3 §D.4 中提到 `iter_predictor_cells` 依赖分布族参数，在 Blocker 2.4 §D.3 中提到 `_verify_dominance_change` 未定义。但没有将这3个 helper 统一归类为 "validator helper contract 缺失" 这一主题。

### 为什么这很重要

这些 helper 是 L2/L3 验证的核心子程序。缺少 contract 意味着即使 metadata schema 和 distribution family 都解决了，validator 的实现仍然需要对 helper 的行为做假设。将它们统一识别为一个主题有助于在 P01 (metadata) 和 P04 (distribution) patch 中同时定义这些 helper 的接口。

## 2.5 B1: 非 daily 时间频率语义

**价值评级**：LOW-MODERATE

### Codex 的发现

Codex 在 `01_evidence_matrix.md` §4 中列出 B1：

> §2.1.1, §2.4 只示例 `daily`。`weekly/monthly` 等频率无法一致实现。

### Claude 的覆盖情况

Claude 在功能区域 2A 的描述中提到 `add_temporal(name, start, end, freq, derive=[])` 的 derive 白名单，但没有单独提及非 daily 频率的缺失语义。

### 影响范围

影响 subtask 1.3.2（temporal column 存储 freq）和 4.1.4（temporal derivation 的引擎实现）。属于 NEEDS_CLARIFICATION 级别，不阻塞主链但影响完整性。

## 2.6 `dirty_rate` 语义缺失

**价值评级**：LOW

### Codex 的发现

Codex 在 `03_blockers_and_spec_gaps.md` §4 Missing/Undefined Issues 表中列出：

> dirty-value semantics：`dirty_rate` 的具体扰动策略与类型范围未定义。

### Claude 的覆盖情况

Claude 未单独提及。

### 影响范围

影响 Module 4.4 和 validator。但 `dirty_rate` 的注入（4.4.2）已排入 Sprint 6，说明实现者可以在假设下推进。低优先级。

## 2.7 Spec Patch Backlog (P01–P11) 结构化输出

**价值评级**：HIGH (操作性)

### Codex 的发现

Codex `04_clarifications_and_spec_patches.md` §4 创建了一个结构化的 11 个 Patch 条目，每个包含：

| 字段 | 说明 |
|---|---|
| Patch ID | P01–P11，可全局引用 |
| Theme | 所属主题域 |
| Section to Add/Revise | 需要修改的 spec 具体章节 |
| Patch Type | formal schema / decision note / algorithm / reference table 等 |
| Minimum Completion Criteria | 该 patch 最低完成标准 |
| Unlocks | 解锁的具体 subtask 列表 |
| Priority | P0 / P1 / P2 |

Codex 还在 §7 中提供了 **Minimum Unlock Patch Set**：P01 + P03 + P04 + P06 + P08 + P10（6 个核心 patches），以及 P05 作为 P04 的 companion patch。

### Claude 的对应

Claude 的建议分散在各 blocker 的 §F (Minimum decisions needed to unblock) 中，没有统一编号和 tracking 机制。Claude Stage 3 §4 的 "shortest path" 提供了线性步骤，但没有 patch ID、minimum criteria 或 section-to-revise 的精确指向。

### 为什么 Codex 的 Patch Backlog 更实用

- **可追踪**：P01–P11 编号可以直接在 issue tracker / task board 中使用
- **可验收**：每个 patch 有 minimum completion criteria
- **可分配**：每个 patch 指向了需要修改的 spec section
- **可排序**：优先级和 unlock chain 明确

## 2.8 按角色分配的澄清问题

**价值评级**：HIGH (操作性)

### Codex 的发现

Codex `04_clarifications_and_spec_patches.md` §2 为每个 blocker 设计了 **must-answer questions**，每个问题标注了责任方：

- `[Spec Owner]`：负责 spec 正式定义和回写
- `[Architect]`：负责跨模块边界和 lifecycle 决策
- `[Rules / Algorithm Owner]`：负责 DSL grammar、distribution domain、pattern injection 算法
- `[Validator Owner]`：负责 L1/L2/L3 检查语义和 threshold
- `[Implementation Owner]`：负责实现细节和集成
- `[Phase 1 Owner / Phase 3 Owner]`：负责跨 Phase 接口

### Claude 的对应

Claude 没有做角色分配。所有建议以 "define X" 的形式给出，没有指定谁应该做这个决策。

### 为什么这很重要

Phase 2 的 blockers 不是一个人能解决的——metadata schema 需要 Spec Owner 决策，formula DSL 需要 Rules Owner 定义，validation lifecycle 需要 Architect 拍板。没有角色分配，决策会陷入"所有人都觉得这不是自己的事"的困境。

## 2.9 "Can Continue / Must Pause / Should Defer" 执行分类

**价值评级**：HIGH (操作性)

### Codex 的发现

Codex `05_resolution_plan.md` §5 将所有工作分为 4 类：

**Can continue now**：
- Patch 文档工作本身（P01–P11 的 owner review、字段表、reference table）
- Sprint 1–8 非 blocker 路径的稳定交付物（constructor, registries, add_category/add_temporal ready 部分, outlier/trend_break 已指定路径）
- 准备性工作（分支切分, metadata consumer test harness, stub-level unit tests）

**Can proceed only under assumptions**：
- 7.1.1（基础 exec namespace + timeout）
- 4.4.1/4.4.2, 1.8.2, 10.2.1, 9.2.1–9.2.3（assumption-backed / isolated stubs）
- 非 daily temporal、dirty-value strategy、topo tie-break 等临时处理

**Must pause pending patch/decision**：
- 5.1.3/5.1.4/5.1.6 等 metadata 依赖项（等 P01/P02）
- 1.5.2 和 structural chain（等 P03）
- 1.4.3/1.4.4 等 stochastic chain（等 P04/P05）
- 8.1.3, 9.3.1, 11.1.1 等（等 P08 + P10）

**Should be deferred/removed/re-scoped**：
- `mixture` 如无法正式定义应从支持面移除
- `scale` 如无正式语义应从 API 移除
- `multi-column on`, non-daily temporal, full dirty-value taxonomy 可缩减范围

### Claude 的对应

Claude Stage 3 §4 提供了 "shortest path" 的 4 步线性计划，但没有对**当前在进行的工作**做 can/must/should 分类。

### 为什么这很重要

团队在等待 spec patch 的同时仍然需要继续工作。Codex 的分类告诉团队：
- 哪些事可以安全地继续做
- 哪些事虽然可以做但必须保留假设标签
- 哪些事绝对不能碰（否则会产生返工）
- 哪些事应该砍掉或缩减范围以加速主链

## 2.10 Highest-Risk Wrong Execution Patterns（反模式）

**价值评级**：MODERATE-HIGH

### Codex 的发现

Codex `05_resolution_plan.md` §6 列出 5 个反模式：

1. **先写 metadata producer，再让 validator 逆向猜字段**——会把 validator/Phase 3 建立在错误 contract 上
2. **把示例公式或 `df.query()` 当正式 grammar**——declaration、engine、L2、pattern runtime 会形成不同语义
3. **把 pattern 的 params、injection、L3 分开交付**——最容易制造"能注入但不可验"的假完成
4. **把 isolated stubs 当成已闭环 orchestrator**——掩盖 lifecycle 和 typed-contract 问题
5. **继续沿用旧编号做排期**——造成错误的依赖映射和完成声明

### Claude 的对应

Claude 没有专门列出反模式。Claude 的建议隐含了这些约束（例如 "define the complete metadata schema formally" 暗含了不要让 validator 猜字段），但没有将它们显式化为"不要做 X"。

### 为什么这很重要

反模式列表是一种防御性文档——它不是告诉你做什么，而是告诉你**绝对不要做什么**。对于大型团队协作，反模式警告通常比正向建议更有效地防止错误。

---

# 第三部分：综合评价

## 3.1 Claude 的核心优势

| 维度 | 说明 | 影响 |
|---|---|---|
| 根因分层依赖 | 发现 3 类根因之间的依赖关系 | 战略级洞察：先解决类型1（契约），再解决类型2（三联体），最后解决类型3（矛盾） |
| 依赖图结构化 | ASCII 图清晰展示 blocker 间因果关系 | Blockers 1/2/3 可并行，是最重要的执行优化 |
| 决策选项 + trade-off | 每个 blocker 2–3 个 Option + 推荐 | 直接加速 owner 决策收敛 |
| 时间估算 | 1–2 天设计工作解锁主链 | 纠正"需要大量编码"的认知偏差 |
| Cross-Group Default 独立分析 | A12 提升为独立 blocker | 确保 CRITICAL finding 不被降级遗漏 |
| 功能域 × 状态矩阵 | 11 个功能域 (2A–2K) 的详细状态 | 最完整的现状地图 |

## 3.2 Codex 的核心优势

| 维度 | 说明 | 影响 |
|---|---|---|
| P01–P11 Patch Backlog | 结构化、可追踪、可分配 | 直接可用于项目管理 |
| 按角色分配的澄清问题 | 每个问题标注 owner | 推动决策落地到具体负责人 |
| 纠偏严谨 | 4 个纠偏全部正确 | 防止基于过时 finding 含义做错误决策 |
| A13 + A14 安全问题 | target grammar + sandbox policy | 覆盖了 Claude 忽略的安全基线 |
| Can/Must/Should 分类 | 4 类工作状态分类 | 团队在等待 spec patch 时的行动指南 |
| 反模式警告 | 5 个 "不要做 X" | 防御性文档，防止常见执行错误 |
| 证据矩阵 Number/Evidence Pool | 结构化参考数据 | 后续任何评估的可靠基线 |
| 跨文档不一致识别 | subtask 编号漂移 + blocker 排序差异 | 防止排期错误 |

## 3.3 重要分歧点

### 分歧 1：Blockers 1/2/3 是否可并行

- **Claude**：明确指出 Blockers 1 (Metadata), 2 (Formula DSL), 3 (Distribution) 是**独立根因，可并行解决**
- **Codex**：给出线性顺序 `1→2→3→...`，暗示串行依赖

**判定**：Claude 正确。这3个 blocker 之间没有数据依赖——metadata schema 不需要 formula grammar，formula grammar 不需要 distribution 参考表。它们只是共同阻塞了 L2 Validator。如果有3位设计者，可以同时开始这3项工作，将关键路径从 ~3 天压缩到 ~1 天。

Codex 的线性顺序可能来自 alignment map 的 `1→2→3→6→4→5→7`，这是解锁优先级顺序（先做收益最大的），不是依赖顺序。

### 分歧 2：ScenarioContext (D1/P10) 的优先级

- **Claude**：将 Phase 1 contract 放在较低优先级（Step 4 of 4，"low priority"），理由是"partially mitigated by existing JSON injection path"
- **Codex**：将 P10 提前到 Order 4（在 P06 Pattern 之前），理由是"避免后面 pattern/auto-fix 都定好了却仍因跨阶段输入漂移无法集成"

**判定**：两种策略都有道理。Claude 侧重于"按解锁子任务数排优先级"，Codex 侧重于"消除集成风险"。对于追求最短路径的场景，Claude 更优（先解锁最多子任务）；对于追求稳健集成的场景，Codex 更优（早期消除接口漂移风险）。

### 分歧 3：`mixture` / `scale` 的处理

- **Claude**：视为 binary decision（defer vs include），推荐 defer
- **Codex**：创建独立的 P05 patch，要求与 P04 同步决策，强调"不同时裁决会保留残余歧义"

**判定**：Codex 更谨慎且更合理。`mixture` 和 `scale` 都已经出现在公开 API 签名中——如果只是 defer 而不显式从支持面移除或标注为未启用，LLM 仍可能生成 `family="mixture"` 的代码，导致运行时崩溃或静默错误。P05 的处理方式（要么正式支持，要么显式移除/延期）比 Claude 的"defer and revisit"更安全。

## 3.4 建议采纳策略

基于以上分析，推荐的综合策略是：

### 分析层面：以 Claude 为主干

- 采纳 Claude 的 **3类根因分层依赖模型**作为战略框架
- 采纳 Claude 的 **依赖关系图**确认 Blockers 1/2/3 可并行
- 采纳 Claude 的 **决策选项分析**作为 owner decision session 的输入材料
- 采纳 Claude 的 **时间估算**作为资源规划基线

### 操作层面：以 Codex 为执行工具

- 采纳 Codex 的 **P01–P11 Patch Backlog** 作为项目管理 tracking 系统
- 采纳 Codex 的 **按角色分配的澄清问题**驱动决策 session
- 采纳 Codex 的 **Can/Must/Should 分类**指导团队日常工作
- 采纳 Codex 的 **反模式警告**作为 team onboarding 文档

### 合并 Codex 的增量发现到 Claude 框架中

- 将 **A13 (target grammar)** 纳入 Claude 的 Blocker 2.4 (Pattern Types) 作为 companion safety issue
- 将 **A14 (sandbox policy)** 纳入 Claude 的 Blocker 2.7 系列作为独立安全基线 blocker
- 将 **C7 (validator helper contract)** 纳入 Blocker 2.1 (Metadata) 和 Blocker 2.3 (Distribution) 的解锁链中
- 将 **subtask 编号漂移**写入团队执行规范：以 task hierarchy 现行编号为锚点
- 将 Codex 的 **纠偏1–4** 作为 source doc 引用的最新诠释标准

### 修正 Codex 的不足

- **将 Blockers 1/2/3 标记为可并行**（覆盖 Codex 的线性顺序暗示）
- **为 A12 (Cross-Group Default) 补充独立 blocker 分析**（参照 Claude 的 Blocker 2.7）
- **在 P01–P11 中加入决策选项和 trade-off 分析**（参照 Claude 的 Option 1/2/3 格式）
- **为关键路径加入时间估算**（参照 Claude 的 1–2 天设计工作结论）

---

# 附录：审查方法论

本报告的审查方法：

1. **逐字段验证**：将 Codex 的每个数字、finding 引用、subtask 编号与 Claude 的对应位置对照
2. **结构性对比**：对比两者的分析框架（根因分类、依赖关系、优先级排序）
3. **增量扫描**：遍历 Codex 5份文档中的每个独立 finding / observation，检查 Claude 3份文档中是否有对应覆盖
4. **Source doc 回溯**：对于两者分歧的点，回溯到 5个权威 spec 文档验证谁更准确

**审查限制**：本报告未重新阅读全部 5个权威 spec 文档原文，而是基于两个工作流的输出进行交叉验证。如果两个工作流都遗漏了某个 spec 中的问题，本报告无法发现。
