# Phase 2 澄清问题与规格补丁设计

## 1. 执行摘要
- 当前真正缺的不是更多实现拆解，而是把 `schema_metadata`、`FormulaDSL`、distribution family contract、4 类 pattern triple、validation / orchestration lifecycle、`ScenarioContext`、`censoring` 等公共 contract 冻结成可执行规格。
- 按当前阻塞墙的最大解锁收益，优先顺序应先解决共享接口，再解决依赖其运行的算法：`metadata -> formula -> distribution -> pattern -> validation/orchestration -> ScenarioContext`；`censoring` 可后置。
- 纠偏 1：以 `2_phase2_gap_analysis.md` post-audit 为准，`A12` 表示“undeclared cross-group default semantics”，不再表示 `generate()` 返回类型歧义；`phase_2.md §2.8` 与 `1_phase2_implementation_task_hierarchy.md 1.1.3` 已明确 `generate() -> Tuple[pd.DataFrame, dict]`。
- 纠偏 2：`C5` 不是“完全没有顺序定义”，而是 §2.7 与 §2.9 的组合、预算、升级边界尚未在权威 spec 中正式冻结；`1_phase2_implementation_task_hierarchy.md 11.1.4 / 11.1.5` 已给出 sequential / no-escalation / max-6 的实现合同，可直接转为 spec patch。
- 纠偏 3：`D1` 阻塞的是 typed `ScenarioContext` 与 versioning 的正式化，而不是基本 JSON 注入能力；`3_phase2_implementation_alignment_map.md` 已明确现有 JSON injection path 存在。
- 纠偏 4：`1_phase2_implementation_task_hierarchy.md` 已把 structural / L2 相关 subtasks 更新为 `4.2.5-4.2.8 / 8.3.3-8.3.5`；`3_phase2_implementation_alignment_map.md` 与 `4_phase2_sprint_plan.md` 中仍保留部分旧号 `4.2.3 / 4.2.4 / 8.3.5`。本文所有 unlock 引用以 task hierarchy 现行编号为准。

## 2. 供 Owner 回答的澄清问题

### Blocker 1 / 主题 1：元数据 / Schema 完整性
#### 必答问题
1. `[Spec Owner / Architect]` 是否把 `phase_2.md §2.6` 的 `schema_metadata` 从 JSON example 升级为正式 typed contract；若是，顶层必填键是否固定为 `schema_version`、`dimension_groups`、`orthogonal_groups`、`group_dependencies`、`columns`、`measure_dag_order`、`patterns`、`total_rows`？
2. `[Spec Owner / Validator Owner]` categorical column metadata 是否必须显式包含 `values` 与 normalized `weights`；child categorical 与 `group_dependencies` 是否必须显式包含 `conditional_weights`，且 parent key 不完整时统一报错而不是回退默认？
3. `[Spec Owner / Validator Owner]` stochastic measure metadata 是否必须同时保留 `family`、原始 `param_model`、resolved parameter spec、可选 `scale`；structural measure metadata 是否必须包含 `formula`、`effects`、`noise` 或 `noise_sigma`？
4. `[Spec Owner / Phase 3 Owner]` validation soft-fail report、quality flags、pattern params 是否进入 metadata 主体；若进入，属于顶层字段还是独立 `validation_report` / `quality` block？

#### 附加建议确认项
1. `[Spec Owner]` 空集合语义是否统一为“空数组 / 空对象必须保留，不允许省略字段”，还是允许空字段省略？
2. `[Architect]` `schema_version` 是否采用语义化版本字符串，并要求 Phase 3 对未知版本 fail-fast？

### Blocker 2 / 主题 2：Formula DSL 与 Structural Measure 合同
#### 必答问题
1. `[Rules / Algorithm Owner]` `formula` 是否限定为受限 DSL，而非任意 Python 表达式；允许的 token 是否只包含 numeric literals、已声明 measure 标识符、已声明 effect symbol、`+ - * / ()` 与一元负号？
2. `[Rules / Algorithm Owner]` symbol resolution 的优先级是否固定为“measure columns first，effect symbols second”，并显式禁止函数调用、属性访问、索引、comparison、boolean operators？
3. `[Architect / Validator Owner]` generation 与 L2 residual 是否必须复用同一 `eval_formula()` 语义；遇到 `NaN` / missing / realism 后的值时，是 fail、propagate `NaN`，还是按 phase boundary 排除这些行？
4. `[Implementation Owner / Spec Owner]` declaration-time formula 错误是否统一映射到 typed exception，并在 §2.7 execution-error loop 中反馈给 LLM？

#### 附加建议确认项
1. `[Spec Owner]` temporal derived columns 是否允许出现在 structural `formula` 中，还是只允许作为 `param_model["effects"]` 的 predictor？
2. `[Architect]` 是否需要在 spec 中提供 EBNF / BNF 级 grammar，而不仅是 operator whitelist？

### Blocker 3 / 主题 3：分布参数与 Measure 参数域
#### 必答问题
1. `[Rules / Algorithm Owner]` 对 `gaussian / lognormal / gamma / beta / uniform / poisson / exponential / mixture`，是否为每个 family 固定 `required keys -> type -> valid domain -> sampling mapping` 参考表？
2. `[Spec Owner / Architect]` `mixture` 是本阶段必须正式支持，还是从 supported list 中暂时移除 / 延期；若保留，component schema、weights normalization、component family whitelist 是否本阶段一起冻结？
3. `[Rules / Algorithm Owner]` `intercept + effects` 计算出的参数若越界，例如 negative sigma、beta outside `(0,1)`、`lower >= upper`，规范要求是 hard fail、clip，还是通过 link function 映射回合法域？
4. `[Spec Owner]` `scale=None` 的语义是后处理缩放、family-specific alias，还是应从公开 API 删除；若保留，是否必须写入 metadata 并参与 L2 expected-parameter reconstruction？

#### 附加建议确认项
1. `[Rules / Algorithm Owner]` temporal predictors 在 `param_model["effects"]` 中的编码值域是否要显式列出，例如 `month=1..12`、`day_of_week=0..6`、`quarter=1..4`、`is_weekend=True/False`？
2. `[Validator Owner]` L2 KS test 的 predictor cell 最小样本量是否要写入规范；样本不足时是 skip、warn 还是 fail？

### Blocker 4 / 主题 4：Pattern 规格与 Target Grammar
#### 必答问题
1. `[Rules / Algorithm Owner]` `ranking_reversal`、`dominance_shift`、`convergence`、`seasonal_anomaly` 这四类 pattern 是否都要补齐 `params` 正式 schema，且字段名、类型、单位、默认值一次性冻结？
2. `[Rules / Algorithm Owner]` 每一类 pattern 是否都必须以“`params schema + injection algorithm + L3 validation rule` 三联体”形式写入 spec，并要求 L3 阈值与注入算法一一对应？
3. `[Architect]` `target` 是否定义为受限过滤 DSL，而不是直接暴露 `df.query()`；若是，允许的比较运算、逻辑运算、列类型、引用方式、安全边界分别是什么？
4. `[Validator Owner]` `ranking_reversal` 是否必须新增 `group_by` 参数替代“metadata 第一个 group”；`dominance_shift` 是否必须把 `_verify_dominance_change` 展开成可测试规则？

#### 附加建议确认项
1. `[Spec Owner]` pattern metadata 中是否同时保留原始 `params` 与 normalized params，还是只保留规范化结果？
2. `[Architect]` `convergence` 与 `seasonal_anomaly` 是否要求 temporal root 或 temporal derived columns 为必备依赖；若缺少时间轴是否应在声明期直接拒绝？

### Blocker 5 / 主题 5：生成边界、验证器 / 自动修复 / 编排
#### 必答问题
1. `[Architect / Validator Owner]` L2 应该运行在 pre-injection snapshot、post-injection data with exclusions，还是 mixed mode；若排除 rows，排除范围由 `pattern.target` 还是 pattern type-specific policy 决定？
2. `[Architect / Implementation Owner]` auto-fix 的 mutation target 是 simulator spec、pattern spec、resolved parameters，还是已生成的 DataFrame；规范是否要求 fixes 在 retry 之间持久化，且禁止通过重新执行原始 `build_fn(seed=...)` 丢失修复？
3. `[Spec Owner / Architect]` §2.7 与 §2.9 是否正式确认为 sequential composition、no cross-loop escalation、worst-case 6 attempts；若是，该规则是否必须回写到 `phase_2.md`，而不只留在 task hierarchy？
4. `[Spec Owner / Phase 3 Owner]` soft-fail policy 是否固定为“L1 fail 不下游；仅 L2 / L3 fail 可带 quality flag 下游”，还是采用别的分级规则？
5. `[Architect]` 当两个 group 既未 `declare_orthogonal()` 也未 `add_group_dependency()` 时，Skeleton builder 的默认 cross-group sampling 规则是什么；是独立采样、禁止生成，还是要求显式声明？
6. `[Architect / Security Owner]` LLM-generated code 的 sandbox policy 是否要在 spec 中明确 import whitelist、timeout、resource limit、I/O / network boundary？

#### 附加建议确认项
1. `[Validator Owner]` `missing_rate` / `dirty_rate` / future `censoring` 打开后，L1 `finite / non-null` 检查是否要改为 capped-rate / policy-aware check？
2. `[Rules Owner]` topo-sort tie-breaking 是否需要 canonical rule 以支撑 bit-for-bit determinism claim？

### Blocker 6 / 主题 6：Phase 1 -> Phase 2 Typed Contract / Versioning
#### 必答问题
1. `[Spec Owner / Architect]` `ScenarioContext` 的 required fields 是否至少固定为 `scenario_title`、`data_context`、`key_entities`、`key_metrics`、`temporal_granularity`、`target_rows`，以及每个字段的 type / allowed shapes？
2. `[Architect]` Phase 1 -> Phase 2 输入是 versioned JSON contract、typed dataclass serialization，还是二者并存；版本字段放在 payload 内还是 envelope 内？
3. `[Implementation Owner / Spec Owner]` 现有 JSON injection path 是否必须继续兼容；如果兼容，未知附加字段是透传、忽略还是 fail-fast？
4. `[Phase 1 Owner / Phase 2 Owner]` 由谁负责 contract validation 与 upgrade path；Phase 2 遇到旧版本 `ScenarioContext` 时是适配、拒绝还是降级运行？

#### 附加建议确认项
1. `[Architect]` `ScenarioContext` 的正式归属是 `phase_2.md`、共享 contract 附录，还是单独 schema section？
2. `[Spec Owner]` prompt template 是否允许从 `ScenarioContext` 推导默认值，还是所有 hard constraints 都需要上游显式提供？

### Blocker 7 / 主题 7：`Censoring` / Realism 策略
#### 必答问题
1. `[Rules / Algorithm Owner]` `censoring` dict schema 是否固定包含 `target_columns`、`direction`、`threshold`，以及是否支持 `indicator_column`；是否允许 multi-column / per-column thresholds？
2. `[Spec Owner / Validator Owner]` censored columns 是否必须在 metadata 中显式标记，并定义 L1 / L2 对这些列的处理策略，例如 skip、adjusted expectation、special-case validation？
3. `[Spec Owner]` realism 三件套 `missing_rate` / `dirty_rate` / `censoring` 的组合顺序是否固定为 δ phase 内的确定性顺序，还是 `censoring` 单独属于后续阶段？
4. `[Rules Owner]` `censoring` 是否仅支持 left / right censoring，还是要同时支持 interval / upper-lower bound forms？

#### 附加建议确认项
1. `[Spec Owner]` `dirty_rate` 的“脏值”语义是否按列类型分开定义，例如 categorical typo、numeric stringification、out-of-range sentinel？
2. `[Validator Owner]` 非 `daily` temporal frequencies 与 realism 同时存在时，季节 / 周期类检查是否必须基于 normalized time bucket，而不是 raw timestamps？

## 3. 主题澄清索引
### 3.1 元数据 / Schema
- `P01 / P02`：把 `schema_metadata` 从 example 升级为正式 typed contract，并补齐 `schema_version`、quality / validation report、empty-vs-omitted 规则。
- `P01`：补齐 validator 实际读取的字段，包括 `values`、`weights`、`conditional_weights`、`formula`、`effects`、`noise_sigma`、pattern params。
- 纠偏：`generate()` 返回 `(DataFrame, dict)` 已是 source-backed 定义，不应继续以旧 `A12` 标签当作活跃 gap。

### 3.2 Formula DSL
- `P03`：冻结 operator whitelist、precedence、symbol resolution、literal / identifier 规则、error model。
- `P03`：要求 declaration、engine、L2 residual 共用一套 evaluator 语义，避免三套局部 DSL 漂移。
- `P03 / P08`：明确 formula 在 missing / realism / `NaN` 条件下的处理边界。

### 3.3 分布参数
- `P04 / P05`：为 8 个 family 给出参数表、合法域、sampling mapping、L2 reconstruction 规则，并对 `mixture` 做保留或延期裁决。
- `P05`：补齐 `scale` 的正式语义或从 API 中移除，避免 metadata 与 validator 长期漂移。
- `P04`：把 temporal predictor 编码和值域写成 reference table，避免 `param_model` effects 依赖隐式约定。

### 3.4 Pattern 规格
- `P06`：为 `ranking_reversal`、`dominance_shift`、`convergence`、`seasonal_anomaly` 完成 `params + injection + L3` 三联体闭环。
- `P06`：修正 `ranking_reversal` 必须显式 `group_by`，`dominance_shift` 不能继续依赖黑盒 helper。
- `P06`：定义 `target` 过滤 grammar 与安全边界，避免把 `df.query()` 行为误当正式 contract。

### 3.5 验证器 / 自动修复 / 编排
- `P08`：冻结 L2 的 pre / post-injection 边界、auto-fix mutation target、retry persistence、soft-fail policy、§2.7 / §2.9 组合方式。
- `P07 / P08`：明确 undeclared cross-group default semantics、多列 dependency schema、topo tie-break 是否进入正式合同。
- `P09`：把 sandbox security policy 从“实现假设”提升为正式执行边界。

### 3.6 Typed Contract / Versioning / Downstream Policy
- `P02 / P10`：同时冻结 metadata versioning 与 `ScenarioContext` versioning，避免 Phase 1 -> Phase 2 -> Phase 3 的 producer / consumer 各自漂移。
- `P02 / P08`：定义 soft-fail 是否可下游、quality flags 如何传递、未知版本如何处理。
- `P11`：把 `censoring` 与 realism cross-section policy 补成正式 contract，而不是继续保留 opaque dict。

## 4. 规格补丁 Backlog
| 补丁 ID | 主题 | 需新增 / 修订的章节 | 补丁类型 | 最低完成标准 | 解锁内容 | 优先级 |
|---|---|---|---|---|---|---|
| P01 | 元数据核心 Schema | `phase_2.md §2.6` + `§2.9`；同步 `1_phase2_implementation_task_hierarchy.md 5.1.x / 8.2-8.3` | formal schema + validator contract | 顶层 metadata typed；`columns`、`group_dependencies`、`patterns`、`measure_dag_order` 字段集合冻结；validator 读取的字段全部在 schema 中有类型与 required / optional 定义；加入 `schema_version` | `5.1.3 / 5.1.4 / 5.1.6`，`8.2.3`，`8.3.1 / 8.3.3 / 8.3.5`，metadata-dependent 部分的 `9.3.1 / 11.1.1` | P0 |
| P02 | 元数据版本化与下游质量合同 | `phase_2.md §2.6` + `§2.9` + `§2.10` | decision note + validator contract | 明确 `schema_version` 格式、未知版本策略、`validation_report` / quality flags 的位置、empty-vs-omitted 规则、Phase 3 是否 fail-fast | Phase 3 consumer contract、soft-fail branch、`11.1.1` 下游兼容性 | P1 |
| P03 | Formula DSL Grammar | `phase_2.md §2.3` + `§2.9`；同步 `1_phase2_implementation_task_hierarchy.md 1.5.2 / 4.2.5-4.2.8 / 8.3.4` | grammar + algorithm | DSL grammar、token whitelist、precedence、symbol resolution、syntax / runtime error model、`NaN` policy 定义完整；声明期与 L2 共用同一 evaluator contract | `1.5.2`，`4.2.5-4.2.8`，`8.3.4`；纠偏：旧引用 `4.2.3 / 4.2.4 / 8.3.5` 以现行编号替换 | P0 |
| P04 | 分布族参数表 | `phase_2.md §2.1.1` + `§2.3` + `§2.9`；同步 `1_phase2_implementation_task_hierarchy.md 1.4.3 / 1.5.4 / 4.2.1-4.2.4 / 8.3.1-8.3.2` | reference table + validator contract | 每个 family 的 required keys、value type、legal domain、resolved-parameter validation、sampler mapping、L2 reconstruction rule 固定 | `1.4.3 / 1.5.4`，`4.2.1-4.2.4`，`8.3.1 / 8.3.2` | P0 |
| P05 | `mixture` 与 `scale` 决策补丁 | `phase_2.md §2.1.1` + `§2.5` | decision note + formal schema | 要么移除 / 延期 `mixture` 与 `scale`，要么分别给出 component schema / weights rule 与 `scale` 行为定义、metadata presence、validation rule | `1.4.4`，distribution dispatch completeness，prompt / metadata consistency | P0 |
| P06 | Pattern 三联体规格与 Target Grammar | `phase_2.md §2.1.2` + `§2.8` + `§2.9`；同步 `1_phase2_implementation_task_hierarchy.md 1.8.4 / 4.3.3-4.3.6 / 8.4.2 / 8.4.4-8.4.7` | reference table + grammar + algorithm + validator contract | 4 类未闭环 pattern 的 `params` schema、injection algorithm、L3 metric / threshold、metadata shape、`target` grammar 全部明确；`ranking_reversal.group_by` 与 `dominance_shift` 语义落地 | `1.8.4`，`4.3.3-4.3.6`，`8.4.2`，`8.4.4-8.4.7` | P0 |
| P07 | Cross-Group 默认规则与依赖 Schema | `phase_2.md §2.2` + `§2.4`；同步 `1_phase2_implementation_task_hierarchy.md 1.7.2 / 4.1.1 / 4.1.2` | algorithm + reference table + decision note | undeclared group pair 默认采样规则定义；`add_group_dependency(on=[...])` 的多列 `conditional_weights` schema 固定；per-parent missing-key 行为明确 | `1.7.2`，`4.1.1 / 4.1.2`，generalized skeleton correctness | P1 |
| P08 | 验证 / 自动修复 / 编排生命周期 | `phase_2.md §2.7-§2.9`；同步 `1_phase2_implementation_task_hierarchy.md 8.1.3 / 9.2.x / 9.3.1 / 11.1.4-11.1.5` | state machine / stage order + algorithm | L2 输入 snapshot 规则、auto-fix mutation target、retry persistence、sequential composition、no escalation、max 6 attempts、soft-fail grading、realism-aware L1 policy 明确 | `8.1.3`，`9.2.1-9.2.3`，`9.3.1`，`11.1.2-11.1.5` | P0 |
| P09 | Sandbox 安全策略 | `phase_2.md §2.5` + `§2.7` | decision note + executor contract | 明确 allowed imports、I/O / network / process boundary、timeout、resource limits、error classification 与 audit expectations | `7.1.1`，safe code execution，`11.1.1` 的执行边界 | P1 |
| P10 | `ScenarioContext` Typed Contract | `phase_2.md §2.5`；对齐 `3_phase2_implementation_alignment_map.md` Blocker 6 与 `4_phase2_sprint_plan.md` Blocker 6 | formal schema + metadata example + decision note | required / optional fields、types、serialization format、version field、unknown-field policy、backward compatibility 明确；保留现有 JSON injection path 的兼容策略 | `10.1.2`，`11.1.1` | P1 |
| P11 | `Censoring` 与 Realism 验证策略 | `phase_2.md §2.1.2` + `§2.6` + `§2.8` + `§2.9` | formal schema + validator contract | `censoring` schema、metadata representation、δ-phase order、L1 / L2 handling、indicator-column policy 明确；`dirty_rate` 语义至少给出最小 contract | `4.4.3`，`8.2.4`，realism completeness，`8.1.3` policy consistency | P2 |

## 5. 必须由 Spec Owner / Architect 决定的事项
| 主题 | 为什么需要 Owner 级决策 | 实现者无法单独决定的内容 |
|---|---|---|
| 元数据 schema 与版本化 | 这是 Phase 2 engine、validator、Phase 3 的公共 producer / consumer contract | 顶层字段集合、required / optional、`schema_version`、quality report 位置、unknown-version policy |
| Formula DSL | 这是 declaration、engine、L2 三处共享的安全语义边界 | token whitelist、grammar、`NaN` policy、error semantics、是否允许函数 / 比较 / 布尔表达式 |
| 分布族支持面 | 这是公开 API 的支持承诺，不是内部实现偏好 | 哪些 family 真正受支持、`mixture` 是否保留、`scale` 是否存在、domain violation policy |
| Pattern 三联体与 Target Grammar | 这同时定义了业务语义、validator 检查语义与执行安全边界 | 4 类 pattern 的正式 `params`、`group_by`、`target` grammar、L3 阈值与统计量 |
| 验证 / 自动修复 / 编排生命周期 | 这是跨模块 lifecycle contract，错误会直接导致系统振荡或预算失真 | pre / post-injection L2 边界、mutation target、retry persistence、escalation policy、soft-fail grading |
| Cross-group 默认语义 | 这是 generalized generation 的核心语义，不应由实现者自行发明默认规则 | undeclared group pair 的默认采样规则、多列 dependency schema、missing parent-key behavior |
| `ScenarioContext` 版本化输入 | 这是跨 Phase 的正式接口边界 | required fields、serialization contract、versioning、unknown-field policy、兼容责任归属 |
| `Censoring` / Realism 策略 | 这会改变统计分布与 validator 解释方式，属于公共语义 | `censoring` schema、delta 阶段顺序、indicator column、L1 / L2 exemptions 或替代检查 |

## 6. 可以留给实现设计的内容
| 主题 | 为什么可以下放 | 约束边界 |
|---|---|---|
| 元数据内部表示 | 只要最终 emitted metadata 满足 `P01 / P02` 的线格式合同，内部可用 dict、dataclass 或 helper builder | 不得改动公开字段名、类型、required / optional、versioning 语义 |
| Formula parser 实现 | 手写 parser、precedence parser、受限 AST 等都是实现手段 | 必须精确接受 / 拒绝 `P03` 定义的 grammar，并复用于 declaration / engine / L2 |
| Sampler 后端与向量化风格 | `numpy` / `scipy` 选择、批量化细节、缓存策略属于实现优化 | 必须遵守 `P04 / P05` 的 family table、domain checks、determinism contract |
| Pattern 注入执行细节 | groupby / vectorized / row-batch 方式不影响公开 contract | 必须产出 `P06` 规定的统计签名，并写出规范化 metadata |
| Validator helper 拆分 | helper 名称、report builder 拆分、日志文案都可由实现团队决定 | pass / fail 语义、quality flag、retry budget、soft-fail policy 必须遵守 `P08` |
| `LLMClient` 集成胶水 | fence stripping 复用、adapter glue、error message formatting 是工程实现细节 | 不得越过 `P09 / P10` 的 security boundary 与 wire contract |

## 7. 最小解锁补丁集
- 最小且最高收益的解锁集是：`P01 Metadata Core Schema`、`P03 Formula DSL Grammar`、`P04 Distribution Family Parameter Table`、`P06 Pattern Triple Specification and Target Grammar`、`P08 Validation / Auto-Fix / Orchestration Lifecycle`、`P10 ScenarioContext Typed Contract`。
- 这组补丁最大化移除了当前阻塞墙的主链：`metadata -> formula -> distribution -> pattern -> validator / orchestrator -> pipeline entry`，对应现有 `BLOCKED + SPEC_INCORRECT` 的最高密度区域。
- `P05` 实际上应与 `P04` 同步决策；若 `mixture` / `scale` 不同时裁决，stochastic measure 仍会保留残余歧义，因此它是最小集的伴随决策补丁。
- `P07` 是 post-audit 新增的 generalized generation safety patch；若目标场景经常出现“未显式声明的 group pair”或 `on=[a,b]`，它应立即插入 `P06` 之后，否则可作为第一批解锁后的下一项。
- `P09` 与 `P11` 都很重要，但不属于“最大化当前 blocker removal”的第一批：前者更多是执行边界硬化，后者在 `censoring=None` 默认下可后置，不应先于 metadata / formula / pattern 主链。

## 8. 最终判断
现在真正缺的不是更多实现，而是先把哪些 spec patch / decision patch 冻结下来：第一类是把 `schema_metadata` 从 example 升级为 versioned formal schema；第二类是把 `formula` 定义成可复用的受限 DSL；第三类是补齐 distribution family、`mixture`、`scale` 的参数合同；第四类是把 4 类未闭环 pattern 连同 `target` grammar 写成“可声明、可注入、可验证”的三联体；第五类是把 L2、auto-fix、§2.7 / §2.9、soft-fail 固化为单一 lifecycle contract；第六类是把 `ScenarioContext` 正式化为版本化输入边界。`censoring`、sandbox security、cross-group default semantics 等是紧随其后的 decision patches，其中 `censoring` 可后置，但前述几类 contract 不冻结，继续实现只会扩大返工面，而不会真正减少阻塞墙。
