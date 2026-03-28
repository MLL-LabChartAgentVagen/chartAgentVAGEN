# Phase 2 Resolution Path and Execution Order

## 1. Executive Summary
- 若 Sprint 1–8 全部完成，项目只是在排期口径上达到 `8/8 = 100%`、在已排期可实现口径上达到 `73/73 = 100%`；按全量 Phase 2 口径仍仅为 `73/108 = 67.6%`，blocked wall 仍是 `24 BLOCKED + 10 SPEC_INCORRECT + 1 deferred NEEDS_CLARIFICATION`。
- 稳定交付的主路径应以 source-backed 依赖顺序为主：`1 -> 2 -> 3 -> 6 -> 4 -> 5 -> 7`；`2_phase2_gap_analysis.md` 的优先级顺序保留为风险优先级信号，但不应反转实际集成依赖。
- 纠偏 1：`A12` 已在 post-audit 中被重定义为“undeclared cross-group default semantics”，`generate()` 返回类型不是活跃 gap；`phase_2.md §2.8` 与 task hierarchy `1.1.3` 已明确 `Tuple[pd.DataFrame, dict]`。
- 纠偏 2：`C5` 不是“完全无定义”，而是顺序组合与预算边界未在权威 spec 中正式冻结；task hierarchy `11.1.4/11.1.5` 已给出 sequential / no-escalation / max-6 的实现合同，Stage 5 应把它回收为正式 patch，而不是继续当作纯空白问题。
- 纠偏 3：`D1` 阻塞的是 typed `ScenarioContext` 正式化，而不是基础 JSON injection；`3_phase2_implementation_alignment_map.md` 与 `4_phase2_sprint_plan.md` 都已明确现有 JSON path 存在。
- 纠偏 4：虽然 `4_phase2_sprint_plan.md` 的 Sprint 9 汇总文字把 deferred `8.1.3` 与 Blocker 1 一起列入后续集成，但同一源文件的 deferral note 与 alignment map 都明确 `8.1.3` 仍依赖 `B2/C6`；因此本计划按更具体的 source 依赖处理，`8.1.3` 不会在仅解决 metadata 后被视为完成。

## 2. Recommended Unlock Path (In Order)
| Order | Action First | Goal | Risk If Not Done | What It Unlocks |
|---|---|---|---|---|
| 1 | 先冻结 Metadata 核心 contract：完成 `P01 + P02` | 把 `schema_metadata` 从 example 升级为 versioned formal schema，并明确 validator / Phase 3 / soft-fail 的共享字段边界 | 继续按当前 example 写代码会制造 `KeyError`、false pass/fail、Phase 3 重建漂移，并让 `SPEC_INCORRECT` 长期伪装成“可补字段”问题 | `5.1.3 / 5.1.4 / 5.1.6`、`8.2.3`、`8.3.1 / 8.3.3 / 8.3.5` 的 metadata 依赖部分，以及后续 `9.3.1 / 11.1.1` 的共享输入面 |
| 2 | 完成 `P03`：冻结 `FormulaDSL` | 给 structural measure 的声明、DAG、执行、L2 residual 共用同一语义基础 | 若先写 parser / evaluator，后续 grammar 一旦冻结将导致 declaration-time validation、runtime eval、L2 residual 三处一起重写 | `1.5.2`、`4.2.5-4.2.8`、`8.3.4`；并为 formula-derived DAG edges 的完整集成铺路 |
| 3 | 完成 `P04 + P05`，并并行起草 `P09` | 冻结 stochastic measure 的 family table、`mixture`/`scale` 支持面与最小 sandbox 边界 | family 名称继续公开但无参数合同，会让 SDK、engine、L2 各自发明参数语义；`mixture` 尤其会成为高返工公开接口 | `1.4.3 / 1.4.4 / 1.5.4`、`4.2.1-4.2.4`、`8.3.1 / 8.3.2`；并把 `7.1.1` 从“仅能假设实现”推进到正式边界 |
| 4 | 提前完成 `P10`：冻结 `ScenarioContext` typed contract | 先消除 orchestrator 入口的一半 blocker，避免后面 pattern / auto-fix 都定好了却仍因跨阶段输入漂移无法集成 | 若把 D1 放到最后，Prompt / Pipeline 会绑定某一版 example JSON，最终集成时容易出现 silent drift 与回归 | `10.1.2`，并移除 `11.1.1` 的输入侧 blocker；为 Sprint 13 的正式入口准备稳定 contract |
| 5 | 完成 `P06`，并把 `P07` 作为 companion patch 一并收口 | 把 4 类未闭环 pattern 连同 `target` grammar、`group_by`、generalized generation safety 一次性冻结 | 若先分别写 params、injection、L3 或忽略 undeclared cross-group / target grammar，结果会是 pattern 可注入但不可验证，或可验证但语义不安全 | `1.8.4`、`4.3.3-4.3.6`、`8.4.2`、`8.4.4-8.4.7`，并为后续 `P08` 中的 L2/pattern 边界提供前提 |
| 6 | 完成 `P08`：冻结 Validation / Auto-Fix / Orchestration lifecycle | 正式定义 L2 看哪个 snapshot、fix mutate 什么对象、retry 如何持久化、§2.7/§2.9 如何组合、soft-fail 如何分级 | 若先集成 9.2.x / 9.3.1 / 11.1.x，只会把 isolated stubs 和伪代码冲突包装成“可运行但不稳定”的假完成 | `8.1.3`、`9.2.1-9.2.3` 的集成资格、`9.3.1`、`11.1.2-11.1.5`；并完成 `11.1.1` 的剩余组合语义 |
| 7 | 最后处理 `P11`：完成 `censoring` 与 realism cross-section policy | 补齐 realism 子链，不让 `censoring` 继续作为 opaque dict 存在 | 若过早实现 `censoring`，后续 metadata/L1/L2 policy 一变就会三方返工；若长期不定，则 realism 永远不是闭环能力 | `4.4.3`，以及与 `8.2.4 / 8.1.3` 相关的 realism-aware validator 行为 |

## 3. Shortest Path to Stable Delivery
从“Sprint 1–8 completed”走到“stable delivery”，最短路径不是继续堆实现，而是先把 blocked wall 前面的 spec patch 波次做完，然后再按 source-backed 集成顺序恢复实现。最小剩余路径应是：先完成 `P01/P02`（metadata + downstream quality contract），再完成 `P03`（FormulaDSL），然后完成 `P04/P05`（distribution family + `mixture/scale` 决策），接着提前完成 `P10`（typed `ScenarioContext`），随后完成 `P06/P07`（4 类 pattern triple + target / generalized generation safety），最后完成 `P08`（validation / auto-fix / orchestration lifecycle）；`P11` 可机会性插入，但不应先于主链。对应实现集成，可仍参考 Sprint Plan 的后半段形状：Sprint 9 收口 metadata emitter 与 validator 的 metadata 相关 `SPEC_INCORRECT`，Sprint 10 收口 formula / structural chain，Sprint 11 收口 stochastic family chain，Sprint 12 收口剩余 4 类 pattern，Sprint 13 收口 auto-fix retry loop、pipeline orchestrator 与 typed scenario injection。到这一步，`9.3.1` 与 `11.1.x` 才能被称为稳定闭环，而不是“有代码路径”的伪完成。

这个顺序里有几项依赖不能反转。`P01` 之前不能把 validator / auto-fix / orchestrator 当作稳定完成，因为 metadata 仍不是共享 contract；`P03` 之前不能完成 structural engine 与 L2 residual；`P04/P05` 之前不能完成 stochastic sampling、noise validation 与 KS path；`P06/P07` 之前不能完成剩余 4 类 pattern，也不能合理决定 `P08` 中 L2 对 pattern 的处理边界；`P08` 与 `P10` 没定之前，`9.3.1`、`11.1.1`、`11.1.2-11.1.5` 不能被称为稳定交付。纠偏说明：虽然 Sprint Plan 汇总段把 deferred `8.1.3` 放进 Blocker 1 解决后的 Sprint 9，但更具体的 deferral note 与 alignment map 都说明 `8.1.3` 仍受 `B2/C6` 约束，所以本计划不把它视为可在 metadata-only 波次中关闭。

## 4. Responsibility Split
| Role | Required Actions | Priority | Notes |
|---|---|---|---|
| Spec Owner | 批准并回写 `P01/P02/P03/P04/P05/P06/P10/P11` 的公开 contract；明确 `mixture`/`scale` 是保留还是移除；接受 `A12/C5/D1` 的 source-backed 纠偏 | P0 | 所有正式定义必须回流到权威 spec，而不是只留在 prior-stage output；结构/编号冲突时以当前 task hierarchy 编号为执行锚点 |
| Architect | 主持 `1 -> 2 -> 3 -> 6 -> 4 -> 5 -> 7` 依赖顺序；冻结 `P07/P08/P09` 的 cross-group default、target/security boundary、retry budget、no-escalation、soft-fail 分支 | P0 | 需要显式修正 `8.1.3` 的实际解锁条件，避免被 Sprint 汇总文字误导 |
| Validation / Rules Owner | 编写 FormulaDSL、distribution domain checks、pattern L3 统计规则、realism-aware L1 policy、L2 snapshot rule、soft-fail grading | P0 | pattern 必须按 “params + injection + validation” 三联体共设计；不能只补 validator 或只补 engine |
| Implementation Owner | 继续维护已完成的 Sprint 1–8 成果；为 Sprint 9–13 建立集成分支；保留 `9.2.x` isolated stubs、现有 JSON injection、LLMClient 复用边界，但不得把 blocker 项标记为 done | P1 | 可以并行准备测试/重构脚手架，但 `BLOCKED` 与 `SPEC_INCORRECT` 只能在对应 patch 落地后进入完成声明 |
| PM / Prioritization Owner | 组织第一波 owner decision session；把 patch 波次与 Sprint 9–13 集成波次拆开排期；决定哪些项 defer/remove/re-scope（如 `mixture`、`scale`、multi-column `on`、non-daily temporal、`censoring` 范围） | P0 | 需同时保留两种顺序：依赖顺序用于执行排程，gap-analysis 优先级用于资源优先级与风险沟通 |

## 5. What Can Continue vs What Must Pause
### Can continue now
- 立即继续的是 patch 文档工作本身：`P01/P02/P03/P04/P05/P06/P08/P10/P11` 的 owner review、字段表、reference table、state-machine 草案都可以并行推进，因为这部分本身就是解锁动作。
- 已属于 Sprint 1–8 非 blocker 路径的稳定交付物可继续测试与收口，例如 constructor / registries、`add_category()` / `add_temporal()` 的 ready 部分、`outlier_entity` / `trend_break` 的已指定路径、`7.1.2` 错误反馈格式、`LLMClient` 集成验证边界。
- 可继续做不改变公共语义的准备性工作：Sprint 9–13 分支切分、existing JSON scenario 字段盘点、metadata consumer test harness、stub-level unit tests。

### Can proceed only under assumptions
- `7.1.1` 可在“基础 exec namespace + timeout + error capture”假设下继续实现，但在 `P09` 前不得宣称 production-safe。
- `4.4.1 / 4.4.2`、`1.8.2`、`10.2.1`、`9.2.1-9.2.3` 可按现有 assumption-backed / isolated-stub 边界继续推进，但必须保留 `NEEDS_CLARIFICATION` 或 “isolated stubs” 标签。
- 非 daily temporal、dirty-value strategy、topo tie-break、multi-column `on`、`scale` 的临时处理都只能作为假设实现存在，不得被上升为正式 contract。

### Must pause pending patch / decision
- `5.1.3 / 5.1.4 / 5.1.6` 与所有依赖 validator-required metadata 字段的实现必须等 `P01/P02`。
- `1.5.2` 与 structural measure engine/L2 residual 主链必须等 `P03`；在 `FormulaDSL` 冻结前不应继续扩大 parser/evaluator 代码面。
- `1.4.3 / 1.4.4 / 1.5.4 / 4.2.1-4.2.4 / 8.3.1 / 8.3.2` 必须等 `P04/P05`；`1.8.4 / 4.3.3-4.3.6 / 8.4.2 / 8.4.4-8.4.7` 必须等 `P06/P07`。
- `8.1.3`、`9.3.1`、`11.1.1`、`11.1.2-11.1.5` 必须等 `P08` 与 `P10`；纠偏：`8.1.3` 不得因为 metadata patch 完成就提前关闭。
- `4.4.3` 必须等 `P11`；在 `censoring` schema 与 validator policy 未定前不应进入“已实现 realism”叙述。

### Should be deferred / removed / re-scoped
- 如果当前波次没有能力正式定义 `mixture`，应从支持面移除或明确延期，而不是保留 name-only family。
- 如果 `scale` 近期不会得到正式语义，应从公开 API 中移除，或至少被明确标注为未启用/不参与生成与验证。
- 若 stable-delivery 目标不需要复杂 realism，可将 `censoring` 限定为最小 left/right schema，或继续保持 `censoring=None` 为默认并把扩展能力后置。
- `multi-column on`、non-daily temporal、full dirty-value taxonomy 可以 re-scope 成 `single-column on`、`daily only`、minimal dirty perturbation，以换取主链尽快闭环。

## 6. Highest-Risk Wrong Execution Patterns
- **先写 metadata producer，再让 validator 逆向猜字段。** 这会把 `P01/P02` 之前的所有 validator/Phase 3 代码建立在错误 contract 上，后续不是补字段，而是系统性返工。
- **把示例公式或 `df.query()` 当正式 grammar。** 这会让 declaration、engine、L2、pattern runtime 分别形成不同语义，最终需要整体替换 parser、evaluator 和 target runtime policy。
- **把剩余 4 类 pattern 的 params、injection、L3 分开交付。** 这样最容易制造“能注入但不可验”或“能验但验错轴”的假完成，尤其会重演 `ranking_reversal` 的 `group_by` 与 `dominance_shift` 黑盒 helper 问题。
- **把 `9.2.x` isolated stubs、`8.1.3` deferred orchestrator 或基本 JSON injection 当成“已闭环 orchestrator”。** 这会掩盖 `P08/P10` 尚未解决的 lifecycle 与 typed-contract 问题，形成最难排查的集成返工。
- **继续沿用旧 `A12`/`C5`/`D1` 含义或旧 structural/L2 编号做排期。** 这会把已经纠偏过的问题重新当活跃 blocker，或把现行 task hierarchy 与其他文档的旧号混用，造成错误的依赖映射和完成声明。

## 7. Final Readiness Judgment
当前项目距离 stable delivery 仍差一整层“冻结后的公共 contract”，而不只是若干尚未编码的函数：metadata 仍不是正式共享 schema，FormulaDSL 尚未存在，distribution family / `mixture` / `scale` 仍无统一参数合同，4 类 pattern 仍未形成 params/injection/L3 三联体，validation / auto-fix / orchestration 的生命周期仍未回写为权威规则，Phase 1 -> Phase 2 的 `ScenarioContext` 也尚未版本化。最大的剩余不确定性是 `P08` 所代表的组合语义问题，即 L2、pattern、realism、auto-fix、soft-fail、retry budget 是否能被冻成一份不会振荡的生命周期合同；但单个最有价值的下一步仍然是立即完成 `P01` metadata core schema owner decision + patch，因为它是 validator、auto-fix、orchestrator、Phase 3 四条链同时共享的第一解锁点，也是后续所有“稳定交付”判断的最低真值基础。
