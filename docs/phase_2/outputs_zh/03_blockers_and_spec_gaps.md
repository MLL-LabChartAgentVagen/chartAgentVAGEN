# Phase 2 阻塞项与规格缺口模型

## 1. 执行摘要
- Phase 2 当前的主问题不是“剩余实现量过大”，而是 `schema_metadata`、`formula`、distribution family、pattern triple、auto-fix / orchestration 等公共 contract 尚未冻结，导致多个模块只能停留在 assumption-backed 或 isolated-stub 状态。
- 7 个 critical path blockers 中，Blocker 1 和 Blocker 5 属于 `B. contradiction / contract inconsistency`；Blocker 2、3、4、6、7 属于 `A. missing / undefined`。按本阶段建模，Blocker 1–5 为 `P0`，Blocker 6 为 `P1`，Blocker 7 为 `P2`。
- `schema_metadata` 不是“字段稍后补齐”级别的问题，而是 producer example、validator consumer、Phase 3 contract、versioning 四层同时未冻结；它是 metadata emitter、validator、auto-fix、orchestrator 的共享公共接口。
- 公式 DSL、distribution family 参数、pattern `params_schema + injection + validation` 都是 typed interface 缺口；当前无法正确实现，根因不是算法复杂，而是输入 contract 本身不完整。
- 纠偏 1：以 source docs 为准，`A12` 在 `2_phase2_gap_analysis.md` 的 post-audit 版本中已被重定义为“undeclared cross-group default semantics”，不再表示 `generate()` 返回类型歧义；`phase_2.md` 已明确 `generate(self) -> Tuple[pd.DataFrame, dict]`。
- 纠偏 2：`C5` 不应再表述为“完全未定义”；Gap Analysis 已将其降为 `MODERATE`，且 Task Hierarchy `11.1.4 / 11.1.5` 已把 sequential composition、no escalation、max 6 attempts 写成实现合同。当前问题应被表述为跨文档 orchestration contract 未完全冻结，而不是纯缺失定义。

## 2. 关键路径阻塞项总览
| 顺序 | 阻塞项 | 问题类型 | 核心问题 | 直接阻塞 | 强行推进风险 | 解锁收益 | 优先级 |
|---|---|---|---|---|---|---|---|
| 1 | 元数据 schema 完整性 | incomplete schema / contract | `schema_metadata` example、validator 字段读取、Phase 3 consumer contract、schema versioning 未对齐 | `5.1.3 / 5.1.4 / 5.1.6 -> 8.2.3 / 8.2.4 / 8.3.1 / 8.3.3 / 8.3.4 / 8.3.6 -> 9.3.1 -> 11.1.1` | `KeyError`、false pass / fail、Phase 3 重建漂移、producer / consumer 双向返工 | 一次性解锁 metadata emitter、validator、auto-fix、orchestrator 主链 | P0 |
| 2 | Formula DSL Grammar | missing definition | structural measure 的公共输入 contract 缺 grammar、precedence、symbol resolution、allowed constructs | `1.5.2`；`4.2` structural-eval 子链；`8.3.5` | parser / evaluator / L2 各自发明 DSL，声明语义与执行语义分叉 | 解锁 structural measure 从声明、DAG、生成到 residual validation 的闭环 | P0 |
| 3 | Distribution Family Parameter Specification | incomplete schema / contract | distribution `family -> required keys -> domain rules -> sampling/validation compatibility` 未正式化，`mixture` 更是 name-only | `1.4.3 / 1.4.4 / 1.5.4 / 4.2.1 / 4.2.2 / 8.3.1 / 8.3.2` | engine、SDK、L2 各自选择参数名、link / domain 规则，后续统一时高返工 | 解锁 stochastic measure 声明、采样 dispatch、noise validation、KS validation | P0 |
| 4 | Pattern 类型完整规格 | missing definition | 4 类 pattern 缺 `params_schema + injection + validation` 三联体 contract | `1.8.4 / 4.3.3 / 4.3.4 / 4.3.5 / 4.3.6 / 8.4.4 / 8.4.5 / 8.4.6 / 8.4.7` | SDK、engine、L3 分别自创 pattern 语义，无法保证注入结果可被验证检测到 | 解锁 4 类 pattern 在声明、生成、L3 的完整闭环 | P0 |
| 5 | L2 与 Pattern 注入 + Auto-Fix 变异模型 | cross-module spec conflict | pattern 会故意改分布，但 L2 按声明分布做 KS；auto-fix 既可能撤销 pattern，又可能在 retry 中被丢失 | `9.3.1` 直接卡死，并劣化 `8.3.1 / 9.2.1 / 9.2.2 / 9.2.3 / 4.3.1 / 4.3.2 / 11.1.1 / 11.1.2` | validator 振荡、fix 不持久、pattern 叙事被修没、retry 预算语义漂移 | 解锁稳定的 pre / post-validation 边界、持久化 auto-fix、validator orchestrator | P0 |
| 6 | Phase 1 -> Phase 2 接口合同 | incomplete schema / contract | `scenario_context` 有注入入口，但 typed required / optional fields、serialization、versioning 未冻结 | `10.1.2 / 11.1.1` | prompt 绑定某一个示例形状，跨阶段字段变动即破坏 orchestration | 解锁稳定的 Phase 1 -> Phase 2 边界与 pipeline entry point | P1 |
| 7 | `Censoring` Schema | unresolved parameter / field definition | `censoring` 在签名与 pipeline 中出现，但 dict schema、metadata 表达、validator policy 都缺失 | `4.4.3` | 实现者自创 left / right / threshold / indicator 语义，后续 realism / validation 返工 | 解锁 realism 子链完整性与被截断分布的显式处理 | P2 |

## 3. 各阻塞项的深入解释
### Blocker 1: 元数据 schema 完整性
- 本质问题：`schema_metadata` 同时承担 Phase 2 -> Phase 3 输出接口、validator 输入接口，以及 auto-fix / orchestrator 的共享上下文，但 §2.6 只给出 example，§2.9 L1 / L2 / L3 却读取 example 中不存在的字段；Task Hierarchy `5.1.3 / 5.1.4 / 5.1.6` 又把这些缺口写成必须满足的实现合同。
- 阻塞机制：直接阻塞 `5.1.3 / 5.1.4 / 5.1.6`，并沿 `5.1.x -> 8.2.x / 8.3.x -> 9.3.1 -> 11.1.1` 传播。没有完整元数据，validator 无法稳定构造 root marginal、structural residual、group dependency、pattern params、soft-fail 报告等检查输入。
- 为什么当前无法正确实现：正确实现要求先冻结 required / optional、type、version，以及 categorical、group dependency、stochastic measure、structural measure、pattern `params` 的字段集合；否则实现者只能自行发明 schema，无法证明与 validator 和 Phase 3 同步。
- 强行推进风险：典型结果是 `KeyError`、false pass / fail、Phase 3 重建漂移，以及后续一次元数据补齐触发 emitter、validator、orchestrator 三处同时返工。
- 解锁链条：解决后会同时解锁 metadata emitter、依赖元数据的 L1 / L2 / L3 检查、`generate_with_validation()` retry loop，以及端到端 pipeline orchestrator。
- 所属规格问题类别：`B. contradiction / contract inconsistency`。它的本质不是“少几个字段”，而是 producer example 与 consumer contract 已经互相冲突。
- 优先级：`P0`

### Blocker 2: Formula DSL Grammar
- 本质问题：`formula` 是 structural measure 的公共输入 contract，但 source docs 只给了字符串示例，没有 formal grammar、operator whitelist、precedence、literal 规则、symbol resolution order，也没有定义 formula 与 effect symbol 的边界。
- 阻塞机制：直接阻塞 `1.5.2` 的 symbol resolution 与 measure DAG edge creation，并继续阻塞 `4.2` structural-eval 子链和 `8.3.5` residual validation，因为三处都依赖同一套 parser / evaluator 语义。
- 为什么当前无法正确实现：没有 grammar，就无法在 declaration 阶段做可重复的符号解析，也无法在 generation 阶段做安全求值，更无法在 L2 residual 检查时复用同一解释器。任何实现都只能把示例误当契约。
- 强行推进风险：parser、engine、validator 会各自实现“看起来像 Python”的局部子集，导致 declaration-time acceptance、runtime evaluation、L2 residual checking 三处语义分叉；一旦正式 grammar 冻结，DAG builder、formula evaluator、L2 residual 需要整体重写。
- 解锁链条：解决后可打通 structural measure 的 declaration validation、measure DAG、safe evaluation、noise composition、residual validation 整条链。
- 所属规格问题类别：`A. missing / undefined`。缺失的是对象级 `FormulaDSL` 定义，不是某个实现细节。
- 优先级：`P0`

### Blocker 3: 分布族参数规格
- 本质问题：distribution family 只给出了 family 名称列表，缺少 `family -> required keys -> domain rules -> sampling mapping -> validation compatibility` 的 typed interface；`mixture` 甚至没有子规格。
- 阻塞机制：直接阻塞 `1.4.3 / 1.4.4 / 1.5.4 / 4.2.1 / 4.2.2 / 8.3.1 / 8.3.2`。SDK 无法验证 `param_model` 与 `noise`，engine 无法 dispatch 到正确 sampler，L2 无法构造 expected parameters。
- 为什么当前无法正确实现：正确实现要求先知道每个 family 的 required keys、合法 domain，以及 `intercept + effects` 计算后的 domain 校验规则；没有这些前提，连“参数是否有效”都无法一致判定。
- 强行推进风险：SDK、engine、validator 会各自采用不同参数名和 domain 修正策略；`mixture` 更会迫使实现者自行发明 component schema，之后统一规范时将引发接口与测试双重返工。
- 解锁链条：解决后可同时解锁 stochastic measure declaration、noise validation、sampling dispatch、predictor-cell KS validation，以及与 `schema_metadata` 的 measure schema 对齐。
- 所属规格问题类别：`A. missing / undefined`。核心缺的是 typed family spec，而不是某一个 sampler 没写完。
- 优先级：`P0`

### Blocker 4: Pattern 类型完整规格
- 本质问题：6 类 pattern 中只有 `outlier_entity` 和 `trend_break` 有可执行示例；其余 4 类在 params、injection、L3 validation 三层均未形成闭环 contract。
- 阻塞机制：直接阻塞 `1.8.4 / 4.3.3 / 4.3.4 / 4.3.5 / 4.3.6 / 8.4.4 / 8.4.5 / 8.4.6 / 8.4.7`。没有 pattern-specific schema，SDK 不能校验；没有 injection algorithm，engine 不能注入；没有 L3 semantics，validator 不能验证。
- 为什么当前无法正确实现：pattern 的正确实现不是“先随便注入，再以后补 validator”，而是 `params_schema + injection + validation` 必须共同设计，否则无法保证 injected signal 与 validator check 对应的是同一个语义。
- 强行推进风险：SDK、engine、L3 会分别发明自己的 pattern 解释，造成注入结果不可检、L3 false fail / false pass，以及 Phase 2 narrative pattern 与 downstream 叙事脱节。
- 解锁链条：解决后可解锁剩余 4 类 pattern 的 declaration、engine γ、L3 checks，并为 Blocker 5 中的 validator / fix 语义收敛提供前提。
- 所属规格问题类别：`A. missing / undefined`。缺失的是 pattern 作为公共语义对象的完整定义。
- 优先级：`P0`

### Blocker 5: L2 与 Pattern 注入 + Auto-Fix 变异模型
- 本质问题：这是最典型的组合型 contract 冲突。pattern 注入的目的就是改变局部分布，但 L2 仍以 pre-injection 声明分布做 KS；同时 auto-fix 既可能削弱 pattern，又在 §2.9 伪代码中通过 `build_fn(seed=...)` 被重新生成覆盖。这里还需要纠偏：`C5` 不应被写成“完全未定义”，因为 source docs 已给出 sequential / no-escalation 的方向，只是没有与 auto-fix mutation model 完整对齐。
- 阻塞机制：直接卡死 `9.3.1`；间接劣化 `8.3.1 / 9.2.1 / 9.2.2 / 9.2.3 / 4.3.1 / 4.3.2 / 11.1.1 / 11.1.2`。即便单个组件可实现，组合后也不能稳定运行。
- 为什么当前无法正确实现：正确实现必须先冻结三个生命周期规则：L2 是看 pre-injection 还是 post-injection 数据、auto-fix 究竟 mutate simulator spec 还是 mutate already-built DataFrame、retry 时 fix 如何持久化并与 budget 组合。source docs 目前没有把这三件事写成同一份一致合同。
- 强行推进风险：validator 会在 “pattern 让 L2 失败 -> auto-fix 放宽分布或放大 pattern -> 下一轮重新生成覆盖 fix 或抵消 pattern” 的回路里振荡；实现者最终只能用大量 ad hoc 排除规则维持表面通过。
- 解锁链条：解决后会解锁稳定的 pre / post-validation boundary、持久化 mutation target、可证明的 retry semantics，以及 `validate(df, meta)` orchestrator 与 `generate_with_validation()` 的真实闭环。
- 所属规格问题类别：`B. contradiction / contract inconsistency`。问题不是函数缺失，而是 engine、validator、auto-fix、orchestrator 的生命周期语义互相打架。
- 优先级：`P0`

### Blocker 6: Phase 1 -> Phase 2 接口合同
- 本质问题：source docs 已承认存在可工作的 JSON 注入路径，但 `ScenarioContext` 仍然只有 example 级输入，没有正式的 typed required / optional fields、serialization contract、versioning，以及稳定的 Phase 1 -> Phase 2 边界定义。
- 阻塞机制：直接阻塞 `10.1.2 / 11.1.1`。prompt template 可以渲染某个示例，但无法证明对生产级 Phase 1 输出形状稳定兼容。
- 为什么当前无法正确实现：正确实现的关键不是“能不能把 JSON 串进 prompt”，而是要先冻结 `ScenarioContext` 的 schema，明确哪些字段是 producer 必须提供、哪些可选、哪些有默认，以及版本如何演进。
- 强行推进风险：prompt 集成会绑定到某一版示例字段；Phase 1 一旦增删字段、调整命名或嵌套结构，Phase 2 将在没有显式契约破坏提示的情况下 silently drift。
- 解锁链条：解决后可解锁稳定的 prompt population、跨阶段版本化 interface、pipeline entry point，以及后续 Phase 1 / Phase 2 的联调与测试。
- 所属规格问题类别：`A. missing / undefined`。已有的是输入示例，不是正式跨阶段 contract。
- 优先级：`P1`

### Blocker 7: `Censoring` Schema
- 本质问题：`censoring` 在 `set_realism()` 签名、engine δ phase 中都出现了，但 source docs 没有定义其 dict schema、metadata 表达方式、validator policy，也没有说明是 left / right / interval censoring，还是是否生成 indicator。
- 阻塞机制：直接阻塞 `4.4.3`，并间接影响 realism 与 L1 / L2 的兼容性建模。
- 为什么当前无法正确实现：不定义目标列、方向、阈值、表示形式，就无法写确定性的注入逻辑，也无法让 metadata 与 validator 理解“为什么分布被截断”。
- 强行推进风险：实现者只能自创 dict 形状与 truncation 语义；之后一旦正式 schema 冻结，realism injector、metadata、validator 三方都要迁移。
- 解锁链条：解决后可补齐 realism 子链、让 metadata 显式记录 `censoring`，并为 censored columns 的 L2 policy 提供依据。
- 所属规格问题类别：`A. missing / undefined`。缺失的是 `CensoringSpec` 对象级定义。
- 优先级：`P2`

## 4. 缺失 / 未定义问题
| 主题 | 具体缺失项 | 受影响模块 | 为什么会阻塞实现 | 优先级 |
|---|---|---|---|---|
| 元数据 schema | 正式 `schema_metadata` schema：required / optional、type、`schema_version` | Module 5、8、9、11、Phase 3 contract | 没有正式 schema，就无法证明 metadata producer 与 validator / Phase 3 consumer 使用同一 contract | P0 |
| Formula DSL | `formula` grammar、operator whitelist、precedence、symbol resolution | Module 1.5、3、4.2、8.3 | structural measure 的 declaration、DAG、eval、residual validation 都依赖同一解释语义 | P0 |
| 分布族 / 参数 schema | family-specific required keys、合法 domain、sampling / validation compatibility | Module 1.4、1.5.4、4.2、8.3 | SDK 无法验证参数；engine 无法 dispatch；L2 无法生成 expected params | P0 |
| `mixture` family | component schema、weights、sub-family composition 规则 | Module 1.4.4、4.2、8.3 | `mixture` 现在只是名字，无法解析、采样、验证 | P0 |
| Pattern 三联体 | `ranking_reversal / dominance_shift / convergence / seasonal_anomaly` 的 `params_schema + injection + validation` | Module 1.8、4.3、8.4 | 没有三联体 contract，就不能保证 pattern 既能注入又能被 L3 检出 | P0 |
| 目标表达式 grammar | `inject_pattern.target` 的允许运算符、列类型、literal 规则、安全边界 | Module 1.8.2、4.3、8.4 | pattern 注入与 L3 都依赖 `target` 解释；当前只有字符串示例，没有正式 grammar | P1 |
| Cross-group 默认语义 | 未声明 pair 的默认采样与默认验证语义 | Module 3.1、4.1、8.2 | 没有默认关系规则，engine 无法一致处理绝大多数未显式声明的 group pair | P1 |
| Validator helper 合同 | `_get_measure_spec()`、`iter_predictor_cells()`、`_verify_dominance_change()` 的输入 / 输出 contract | Module 8.3、8.4 | validator 代码引用了 helper，但 spec 没给 helper contract，L2 / L3 无法按规格完整落地 | P1 |
| Soft-fail 下游策略 | `return df, report` 之后何种失败可进入下游、如何携带质量标记 | Module 9.3、11.1、Phase 3 handoff | 没有 soft-fail policy，orchestrator 无法决定失败数据是否可继续消费 | P1 |
| Typed `ScenarioContext` | Phase 1 -> Phase 2 的 typed required / optional fields、serialization、versioning | Module 10.1.2、11.1.1 | 目前只有 example 和现有 JSON 路径，没有稳定的跨阶段 interface completeness | P1 |
| `censoring` schema | target columns、direction、threshold、indicator policy | Module 1.9、4.4.3、metadata、validator | 不定义 dict 结构，就无法实现 realism `censoring` 或解释其对分布的影响 | P2 |
| `scale` 语义 | `add_measure(..., scale=None)` 的真实含义与适用范围 | Module 1.4、5.1、8.3 | 参数已进入公开签名，但没有行为定义，会造成存储与验证策略漂移 | P2 |
| 多列 `on` schema | `add_group_dependency(on=[...])` 的 conditional weights 表达形式 | Module 1.7、4.1、8.3 | 当前只能依靠单列示例；多列条件分布没有正式 schema | P2 |
| 非 `daily` temporal 语义 | `weekly / monthly / ...` 的采样规则与衍生值语义 | Module 1.3、4.1 | declaration 可以存 `freq`，但 engine 没有一致采样语义 | P2 |
| Dirty-value 语义 | `dirty_rate` 的具体扰动策略与类型范围 | Module 4.4、validator | realism 声称支持 dirty data，但没有定义怎样“脏”以及对 validator 的影响 | P2 |

## 5. 矛盾 / 合同不一致点
| 主题 | 矛盾点 | 涉及模块 / 层 | 后果 | 优先级 |
|---|---|---|---|---|
| validator ↔ metadata 字段合同 | §2.6 metadata example 未给出 `values / weights / conditional_weights / param_model / formula / noise_sigma / pattern params`，但 §2.9 validator 直接读取这些字段 | `phase_2.md` §2.6 vs §2.9；Module 5 vs Module 8 | metadata producer 与 validator consumer contract 不一致，按 spec 实现会直接 `KeyError` 或导致错误校验 | P0 |
| Pattern 注入 vs 统计验证 | γ phase 故意改变分布，但 L2 仍把 post-injection 数据按 pre-injection 声明分布做 KS | Module 4.3、Module 8.3、pattern semantics | 合法 pattern 会被 validator 当成统计失败，形成系统性 false fail | P0 |
| Auto-fix 变异模型 vs retry 伪代码 | auto-fix strategy 已被调用，但随后 `build_fn(seed=...)` 重新生成，使 fix 不持久；同时 fix 还可能削弱 pattern | Module 9.2、Module 9.3、Module 4.3 | retry loop 无法证明真的在“修复”；系统可能反复回到原状态或擦除 narrative pattern | P0 |
| Realism vs 结构校验 | δ phase 允许 missing / `censoring`，L1 又要求 measure finite / non-null | Module 4.4、Module 8.2 | realism 一开启就可能与 structural validity 正面冲突，导致 validator orchestrator 无法稳定定义 pass / fail | P1 |
| 编排合同冻结状态 | Gap Analysis 将 `C5` 降为 `MODERATE` 且认为 sequential composition 可推断，但 Alignment Map / Sprint Plan 仍把 `11.1.1 / 11.1.2` 放在 blocker 语境中；Task Hierarchy `11.1.4 / 11.1.5` 又把 sequential / no-escalation / max-6 写成合同 | `2_phase2_gap_analysis.md` vs `3_phase2_implementation_alignment_map.md` vs `1_phase2_implementation_task_hierarchy.md` | 方向并非完全未知，但跨文档没有把 orchestration 语义冻结成同一份稳定 contract，导致实现与排期口径并不完全一致 | P1 |
| Finding 身份 / 接口标签 | `A12` 在 Gap Analysis post-audit 中已重定义为 undeclared cross-group default semantics，但 Alignment Map `10.2.2` 仍沿用旧的 “return type ambiguity” 标签；source `phase_2.md` 已明确 `generate(self) -> Tuple[pd.DataFrame, dict]` | `2_phase2_gap_analysis.md` patch log vs `3_phase2_implementation_alignment_map.md` 10.2.2 vs `phase_2.md` §2.8 | 若不纠偏，会把已解决的返回类型问题继续当成活跃 gap，并误导 blocker 建模与后续任务引用 | P2 |

## 6. 问题本质综合
### 6.1 缺失定义类
- 缺失的不是单个参数，而是完整对象定义：`FormulaDSL`、`DistributionFamilySpec`、4 类 `PatternSpec`、`CensoringSpec`、`ScenarioContext`、soft-fail policy。
- 这些对象一旦没有正式定义，SDK、engine、validator、Phase 3 就只能各自用示例或局部假设重建同一语义对象。
- 因此实现受阻的本质不是“代码还没写完”，而是上游没有提供可共享、可版本化、可验证的对象级 contract。

### 6.2 不完整 schema / contract 类
- `schema_metadata`、distribution parameter keys / domain rules、`target` grammar、多列 `on`、`scale`、非 `daily` `freq`、dirty-value semantics 都停留在 example 或签名层，没有 field-level schema。
- 这里缺的是 requiredness、type、domain、versioning，以及输入输出边界，而不是某个 helper 函数。
- 一旦 field-level contract 不完整，producer / consumer 就会在不同模块里各自补洞，最终形成难以兼容的接口分叉。

### 6.3 跨模块冲突类
- metadata example 与 validator reads、γ pattern injection 与 L2 KS、realism 与 L1 finite、`A12` 标签漂移，都是“上游 section 没有给下游 section 保证它所依赖的 contract”。
- 这些问题说明跨模块边界仍未冻结：一个模块假定的字段、阶段顺序或语义，在另一个模块并未被正式承诺。
- 因而即便把每个模块都编码出来，整体系统仍可能在集成点上表现为自相矛盾。

### 6.4 验证 / 自动修复 / 编排语义类
- 当前真正未冻结的是生命周期规则：L2 到底看 pre-injection 还是 post-injection、fix mutate 的目标是什么、retry 如何持久化、soft-fail 后能否继续下游。
- 这类问题不是缺少函数实现，而是缺少 stage-ordering、mutation boundary、retry budget、failure policy 等 orchestration semantics。
- 只要这些规则不冻结，validator、auto-fix、orchestrator 即使各自“可运行”，也不能被称为正确且稳定。

## 7. 最终判断
Phase 2 的首要问题更准确地应被表述为 **“未冻结的规格 / 合同”**，而不是“未完成的实现工作量”。未完成实现当然存在，但它更多是结果而不是根因：真正阻塞正确实现的是公共接口没有冻结、跨模块 contract 彼此冲突，以及 validation / auto-fix / orchestration 的生命周期语义没有在 source docs 中形成一致定义。换言之，当前缺的不是更多编码人力，而是先把 `schema_metadata`、`formula`、distribution family、pattern triple、Phase 1 -> Phase 2 boundary 与 retry semantics 这些规范边界正式冻结；否则继续推进实现只会把返工成本往后堆。
