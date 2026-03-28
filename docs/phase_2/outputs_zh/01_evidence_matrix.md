# Phase 2 多文档证据矩阵

## 1. 文档角色摘要
| 文档 | 主要角色 | 可回答的问题 | 不应回答的问题 |
|---|---|---|---|
| `phase_2/.cursor/rules/phase2-workflow.mdc` | 工作流约束与输出纪律 | 哪些文件可作为权威内容来源；状态标签如何区分；每阶段如何读写；聊天回复范围 | 不负责定义 Phase 2 领域语义，不负责补充规格缺口 |
| `phase_2/prompts/01_build_evidence_matrix.md` | Stage 1 任务书与输出格式契约 | Stage 1 要抽取哪些证据、输出结构必须是什么、哪些内容禁止进入本阶段 | 不负责定义 SDK、验证器、冲突结论或修复方案 |
| `phase_2/spec/phase_2.md` | 基础规格与 Phase 2 正式语义源 | SDK API、生成主流程、metadata 示例、L1 / L2 / L3 验证、auto-fix、LLM prompt / hard constraints | 不负责把所有示例提升为正式参数表；不负责实现优先级、准备度统计、冲刺排期 |
| `phase_2/spec/1_phase2_implementation_task_hierarchy.md` | 实现合同与完成条件分解 | `generate()` 顶层合同、模块拆分、完成条件、跨模块依赖、哪些点被标为实现设计选择 / 待澄清 / 阻塞 | 不负责给出多文档冲突的最终裁决，不负责冲刺排期 |
| `phase_2/spec/2_phase2_gap_analysis.md` | 审计式缺口与问题列表 | 各 finding 的 spec 位置、issue、impact、recommendation；跨 reviewer synthesis；优先 blocker 顺序 | 不负责定义正式实现合同，不负责给出子任务准备度总表 |
| `phase_2/spec/3_phase2_implementation_alignment_map.md` | 子任务 × finding 对齐与准备度地图 | 108 个子任务的 `SPEC_READY / NEEDS_CLARIFICATION / BLOCKED / SPEC_INCORRECT` 分布；关键 blocker 与直阻链条；准备度边界修正 | 不负责新增规格语义，不负责给出 Stage 1 之外的结论 |
| `phase_2/spec/4_phase2_sprint_plan.md` | Sprint 1–8 排期与阻塞墙描述 | 8 个冲刺范围、73 个可排期子任务、34 个 blocked / spec_incorrect、Sprint 9+ 集成顺序 | 不负责证明某 blocker 已被解决，不负责替代 gap analysis |

说明：
- 内容权威源仅限 5 个 `phase_2/spec/*.md` 文档；规则文件与阶段 prompt 只约束流程与输出形式。
- 更正：文档文本常写作 `docs/phase2/...`，但当前工作区实际路径为 `phase_2/...`；本矩阵按源文档内容抽取，按实际工作区路径落盘。

## 2. 基础规格关键事实 (`phase_2.md`)
| 主题 | 原始定义 / 关键源细节 | 受影响模块 | 备注 |
|---|---|---|---|
| SDK 总体定位 | `FactTableSimulator` 以最小、强类型 API 同时承担 schema 声明与数据生成程序；LLM 只在白名单 API 内写代码 | SDK 核心类、Prompt、Orchestrator | 文档明确把“代码即 DGP（Code-as-DGP）”作为 Phase 2 核心贡献 |
| Step 顺序 | `add_*()` 列声明先于 relationship / pattern 声明；Prompt 硬约束 3 再次要求 Step 1 before Step 2 | SDK API、Prompt 校验 | 这是显式顺序约束，不是示例习惯 |
| `add_category` | `add_category(name, values, weights, group, parent=None)`；根 / 全局权重或按父级划分的 dict；自动归一化；拒绝空值；`parent` 必须存在且属于同一 `group` | 维度组、Skeleton builder、Metadata | 示例展示 flat list 与 per-parent dict 两种形式，但未给完整性规则表 |
| `add_temporal` | `add_temporal(name, start, end, freq, derive=[])`；`derive` 示例为 `day_of_week / month / quarter / is_weekend`；派生列自动可用作 measure predictor | Temporal group、Skeleton builder、Measure `param_model` | 只展示 `daily` 示例；未给 `freq` 白名单或非 `daily` 采样语义表 |
| `add_measure` | `add_measure(name, family, param_model, scale=None)`；定义为 stochastic root measure；不能依赖其他 measure；支持常量参数与 `intercept + effects` | Stochastic measure、L2 KS、Metadata | 示例只完整展示 `gaussian / lognormal`；`scale` 只出现在签名与 prompt 中 |
| `add_measure_structural` | `add_measure_structural(name, formula, effects={}, noise={})`；`formula` 引用之前声明的 measure 与命名 effect；会在 measure DAG 中创建边 | Structural measure、Formula evaluator、L2 residual | 示例给出 `cost = wait_minutes * 12 + severity_surcharge + noise`，但无正式 grammar |
| 支持的分布 | `"gaussian"`, `"lognormal"`, `"gamma"`, `"beta"`, `"uniform"`, `"poisson"`, `"exponential"`, `"mixture"` | Sampling dispatch、L2 KS、Noise spec | 文档提供 family 名称列表，但未给各 family 参数键表 |
| 维度组 | 每个 categorical 列属于一个命名 `group`；组内层级由 `parent` 表达；`time` 是特殊的 dimension group | Group registry、Metadata、View extraction | `time` 组在 metadata 示例中出现 |
| `declare_orthogonal` | 在 `group` 级声明独立性，自动传播到全部 cross-group root pairs；Generation / L1 / Phase 3 都依赖它 | Cross-group semantics、L1、Phase 3 | 文档明确声明的是 group independence，不是 column pair independence |
| `add_group_dependency` | 只允许 group root 之间的 cross-group dependency；`child_root` 的条件分布依赖 `on` 中的 root columns；root-level graph 必须是 DAG | Cross-group root DAG、Skeleton builder、Metadata、L2 | 示例只展示 `on=["severity"]` 的单列条件 |
| `inject_pattern` | `inject_pattern(type, target, col, params)`；pattern types 为 `outlier_entity / trend_break / ranking_reversal / dominance_shift / convergence / seasonal_anomaly` | Pattern injection、L3、Metadata | 仅 `outlier_entity` 与 `trend_break` 有完整示例参数 |
| `set_realism` | `set_realism(missing_rate, dirty_rate, censoring)`；用于缺失值、脏值、`censoring` 注入 | Realism injection、L1 / L2、Metadata | `censoring` 只出现在签名 / 管线中，未给 schema |
| Measure DAG 约束 | Structural measures 只能引用之前声明的 measures；所有 measure dependencies 必须是 DAG；引擎用 topological sort 执行 | DAG builder、Structural eval、Validation | 规格明确约束 measure graph 为 DAG |
| `generate()` 主流程 | `generate()`：pre-flight `_build_full_dag` → `topological_sort` → α skeleton → β measures → γ patterns → δ realism → `_post_process` + `_build_schema_metadata` | Engine、Metadata、Validator 接口 | `δ` 为可选；相同 `seed` 应逐 bit 可复现 |
| 事件级生成模型 | `target_rows` 来自 Phase 1；不物化完整 cross-product；每一行是一个 atomic event；典型规模 `200–500 / 500–1000 / 1000–3000` | Engine α、Prompt、Phase 1 接口 | 硬约束 1 与此一致：each row = one indivisible event |
| 元数据输出定义 | SDK 返回 `(Master DataFrame, schema_metadata)`；示例 key 包括 `dimension_groups / orthogonal_groups / group_dependencies / columns / measure_dag_order / patterns / total_rows` | Metadata builder、Validator、Phase 3 | 文档称其为 Phase 2→3 contract，但只给了 JSON example |
| 执行错误反馈循环 | LLM 输出代码 → sandbox 执行 → 成功后进入 engine + validation；失败时抛出 typed exception 并回喂 LLM；`max_retries=3`；全部失败则 log and skip | Sandbox、Exception hierarchy、Prompt integration | 例外包括 `CyclicDependencyError / UndefinedEffectError / NonRootDependencyError` |
| L1 验证 | row_count 在 10% 以内；categorical cardinality；root marginal weights；measure finite / non-null；orthogonal chi-squared；measure DAG 无环 | Validator L1、Metadata | 直接读取 `meta["columns"]`、`meta["orthogonal_groups"]` 等字段 |
| L2 验证 | stochastic measures 做 predictor-cell KS；structural measures 做 residual mean / std；group dependency 做 observed vs declared transition deviation | Validator L2、Metadata、Sampling / Formula | 直接使用 `_get_measure_spec()`、`iter_predictor_cells()`、`eval_formula()` |
| L3 验证 | outlier entity z-score、ranking reversal 的 rank corr < 0、trend break 的 before / after 差异、dominance shift 委托 `_verify_dominance_change` | Validator L3、Pattern params | 代码块未展示 `convergence` 与 `seasonal_anomaly` 的 L3 |
| 自动修复循环 | `AUTO_FIX` 将 `ks_* / outlier_* / trend_* / orthogonal_*` 映射到 `widen_variance / amplify_magnitude / reshuffle_pair`；`max_retries=3`；超过最大重试次数后软失败 | Auto-fix、Validation loop、Orchestrator | 文档在 auto-fix 段明确写明“无 LLM 调用” |
| Prompt / 硬约束 | 至少 2 个 dimension groups；每组至少 1 个 categorical；至少 2 个 measures；至少 1 个 `declare_orthogonal()`；至少 1 个 structural measure；至少 2 次 `inject_pattern()`；`sim.generate()` 返回 | Prompt integration、Static checks、Pipeline | 硬约束直接限制脚本生成范围 |
| 示例存在但正式契约未表格化的位置 | `gaussian / lognormal` 有完整示例，但其余 distribution family 无参数键表；`outlier_entity / trend_break` 有 `params` 示例，其余 4 个 pattern 仅有名称；`formula` 仅有字符串例子；`censoring` 仅在签名中出现 | 缺口主题：distribution / pattern / formula / realism | 这是来自基础规格文本本身的可观察事实，不等于本阶段下结论 |

## 3. 实现合同关键事实 (`task hierarchy`)
| 主题 | 合同 / 完成条件 / 依赖 | 相关任务 | 备注 |
|---|---|---|---|
| `generate()` 顶层公开合同 | `generate(self) -> Tuple[pd.DataFrame, dict]`；完成条件要求返回 2-tuple，第二项至少含 `dimension_groups / columns / measure_dag_order / patterns / total_rows` | 1.1.3 | 这是 task hierarchy 对公共 API 的显式合同锚点 |
| 构造器与内部注册表 | `__init__(target_rows, seed)` 后 `_columns / _groups / _orthogonal_pairs / _group_dependencies / _patterns / _realism_config / _measure_dag` 均存在且为空 | 1.1.1, 1.1.2 | 用于后续 metadata builder、DAG builder、validator |
| `add_category` 完成条件 | 空 `values` 必须报错；flat 权重自动归一；per-parent dict 中每个向量独立归一；`parent` 必须存在且同组；group registry 记录 root / columns | 1.2.1–1.2.5 | 1.2.1 与 1.2.6 被标为 `NEEDS_CLARIFICATION` 的部分来自显式规格外的推断 |
| `add_temporal` 合同 | 日期可解析；`derive` 仅允许白名单；temporal group 需要注册 root 与派生 children | 1.3.1–1.3.4 | 1.3.2 仅存储 `freq`，非 `daily` 采样语义留给 engine |
| `add_measure` 合同 | `family` 必须来自支持列表；常量 `param_model` 与 `intercept + effects` 均要可存取；stochastic measure 作为 measure DAG root node 注册 | 1.4.1–1.4.5 | 1.4.2 被标为 `Implementation Design Choice`：内部 canonical representation 非规格要求 |
| `add_measure_structural` 合同 | 保存 `formula / effects / noise`；解析 symbol；measure refs 形成 DAG edge；undefined symbol 报错；检测 cycle 时抛 `CyclicDependencyError` | 1.5.1–1.5.5 | 公式求值与 grammar 缺口直接影响 1.5.2 / 1.5.5 下游 |
| `declare_orthogonal` / `add_group_dependency` 合同 | `group` 必须已存在；orthogonal pair 与顺序无关；group dependency 只允许 root；root-level graph 必须是 DAG | 1.6.1–1.7.4 | 互斥检查在 task hierarchy 中被标为 `NEEDS_CLARIFICATION`，不是已定规格 |
| `inject_pattern` 合同 | `type` 必须在白名单；`target` 按字符串存储；`col` 需引用已声明列；目前只有两类 pattern 有显式参数校验合同 | 1.8.1–1.8.5 | 1.8.2 / 1.8.4 直接暴露 target grammar 与 4 类 pattern 缺口 |
| `set_realism` 合同 | `missing_rate / dirty_rate / censoring` 存入 `_realism_config`；rate ∈ [0,1] | 1.9.1 | `censoring` schema 在 hierarchy 中也未被规格化 |
| 跨章节依赖图 | 20 条有向依赖边，覆盖 registry → DAG → engine phases → metadata → validator → auto-fix → full orchestrator | Cross-Section Dependency Map | 明确依赖例如 `1.5.2 → 1.5.5`、`5.1.x → 8.x → 9.3.1 → 11.1.1` |
| 设计选择而非规格要求 | `DimensionGroup / OrthogonalPair / GroupDependency` 的具体 class 结构、内部 canonical 参数表示、`networkx`、dtype policy、markdown fence extraction 都被标为实现设计选择 | 1.4.2, 2.1.1, 2.2.1, 2.2.2, 3.1.1, 4.5.1, 10.2.1 | 这些点在 Stage 1 中必须与正式规格要求分开记录 |
| 暴露 spec gap 的完成条件 | `mixture` 需要子规格；formula evaluator 需要 grammar；多列 `on` 需要 schema；4 类 pattern 需要 `params / injection / L3`；L1 与 realism 的兼容要单独定义；auto-fix 不能升级为 LLM recall | 1.4.4, 1.5.2, 1.7.2, 1.8.4, 8.2.7, 9.3.2 | 这些任务在 hierarchy 中直接把“做不下去的点”落到了完成条件层面 |
| Orchestrator 顺序合同 | Prompt → LLM → code extraction → sandbox execution → engine generate → three-layer validation → return；执行错误走 §2.7；验证失败走 §2.9；两条 loop 按顺序组合，不互相升级 | 11.1.1–11.1.5 | hierarchy 把“总尝试预算至多 6 次”写进 11.1.5 完成条件 |
| §2.10 下游可用性验证 | 输出需支撑 distribution / aggregation / drill-down / relationship 等下游 chart affordances 的最小验证 | 12.1.1 | 这是 hierarchy 新增的覆盖项，不是基础规格中的排期信息 |

## 4. 差距分析关键事实
| 发现 ID / 主题 | 严重级别 | 问题 | 影响 | 建议 | 备注 |
|---|---|---|---|---|---|
| A1 / `mixture` family 仅有名称 | CRITICAL | §2.1.1、§2.5 仅把 `mixture` 列入支持的分布，但未定义 `param_model`、component schema、weights | LLM 可能输出 `family="mixture"`，SDK 无法验证 / 采样，导致崩溃或实现分叉 | 要么完整定义 `mixture` schema，要么从支持列表移除 / 延期 | 与 Blocker 3 直接相关 |
| A3 / Formula DSL 未定义 | CRITICAL | §2.1.1、§2.3 只给 `formula` 字符串示例，未定义 operators、precedence、literal、function calls、symbol resolution | 无法安全实现 structural evaluator，也无法稳定做 L2 residual validation | 提供 grammar 或至少 operator whitelist | 对应 Blocker 2 |
| A5 / 分布参数键未定义 | CRITICAL | §2.1.1、§2.3 仅示例 `mu / sigma`，其余 `gamma / beta / uniform / poisson / exponential` 无 required keys / domain | SDK 不能校验 `param_model`；engine 不能 dispatch；L2 不能构造 expected params | 给每个 family 建参数参考表与 domain 约束 | Blocker 3 核心 |
| A8 / 4 类 pattern 只有名字没有 `params` schema | CRITICAL | §2.1.2 对 `ranking_reversal / dominance_shift / convergence / seasonal_anomaly` 未定义 `params` 键 | LLM 会输出任意 dict，engine / L3 无法理解 | 为每类 pattern 增加 `params` 规格表 | 与 B6 / C1 构成同一主题三面 |
| A12 / 未声明的 cross-group 默认语义缺失 | CRITICAL | §2.2 说 independence 是 opt-in，不是 default，但未定义既非 orthogonal 又非 dependency 的 pair 如何采样 | 生成算法对大多数 group pair 无默认规则，validator 也无法判断 | 显式给出 undeclared pair 默认行为 | post-audit 新增 finding，进入优先 blocker |
| A13 / Pattern `target` 表达式 grammar 缺失 | CRITICAL | §2.1.2、§2.9 使用 `df.query(target)`，但未定义允许的运算符、列类型、引用规则或安全边界 | pattern injection 与 L3 都存在执行 / 安全不确定性 | 定义受限 grammar，避免直接裸用 `df.query()` | 与安全模型主题相邻但不相同 |
| A14 / LLM 生成代码无 security / sandbox policy | CRITICAL | §2.5、§2.7 只要求 pure valid Python，但没有 import / resource / time limit policy | sandbox 可执行边界不明确，存在代码执行风险 | 定义 import whitelist、资源限制与执行边界 | 影响 Module 7、11 |
| B2 / Pattern 注入与 L2 统计验证冲突 | CRITICAL | §2.8 的 γ 会改变分布，§2.9 的 L2 又对 post-injection 数据按 pre-injection 声明做 KS | 正常 pattern 会触发 KS failure，造成 validator 与 pattern 互相打架 | 明确 L2 在 pre / post-injection 的位置或排除 pattern-target rows | Priority blocker 4 的组成部分之一 |
| B3 / Auto-fix 可能撤销 pattern | CRITICAL | §2.9 的 auto-fix 会 `widen_variance / amplify_magnitude / reshuffle`，但未定义如何保持已注入的 pattern 语义 | 修复动作可能把叙事 pattern 弱化或抵消 | 先定义 mutation model，再扩展 fix strategy | 与 B7 / C5 一起进入 Blocker 5 |
| B6 / 4 类 pattern 注入机制缺失 | CRITICAL | §2.8 对 `ranking_reversal / dominance_shift / convergence / seasonal_anomaly` 无 injection algorithm | 4 / 6 pattern 无法在 engine γ 实现 | 把每类 pattern 定义成 `params + injection + validation` 三联体 | 与 A8 / C1 互相强化 |
| C1 / L3 缺 `convergence` 与 `seasonal_anomaly` | CRITICAL | §2.9 的 L3 代码块只覆盖 4 类 pattern，缺少后两类 | 2 个 pattern 类型无法闭环验证 | 为缺失 pattern 提供对应 L3 逻辑 | 与 A8 / B6 同主题 |
| C3 / 元数据缺少 Phase 3 关键字段 | CRITICAL | §2.6 的 metadata 示例不足以支撑 Phase 3 与 validator：缺少更多 pattern / measure / conditional 信息 | Phase 3 无法可靠重建 schema、drill-down、pattern 语义 | 正式扩充 metadata schema | Priority blocker #1 组成部分 |
| C8 / L2 structural 校验读取了 metadata 中不存在字段 | CRITICAL | §2.9 的 L2 用到 `col["formula"]`、`col["noise_sigma"]`，但 §2.6 的 `columns` 示例未提供 | 按规格实现会直接 `KeyError`，L2 结构化校验不可运行 | 在 metadata 中补充 structural measure 所需字段 | 与 C3 / C13 一起指向 metadata schema overhaul |
| C9 / L1 marginal 校验读取了 metadata 中不存在字段 | CRITICAL | §2.9 的 L1 用到 `col["values"]`、`col["weights"]`，但 §2.6 的 categorical metadata 未提供 | root marginal validation 按规格不可运行 | 在 metadata 中补充 categorical `values / weights` | 直接对应 Alignment Map 的 `SPEC_INCORRECT` |
| C13 / 无正式 metadata schema 与 versioning | CRITICAL | §2.6 仅有 JSON example，无 required / optional / type / version 定义 | Producer / consumer 漂移会导致 validator / Phase 3 运行时失败 | 以 JSON Schema / TypedDict / dataclass 等方式正式化 metadata，并加入 version | 被纳入 Priority blocker #1 |
| A2 / `scale` 参数未定义 | MODERATE | §2.1.1、§2.5 出现 `scale=None`，但无行为说明 | engine / L2 / metadata 都不知该如何解释 `scale` | 明确定义为后处理缩放或从签名中移除 | 影响 Blocker 1 / 3 的字段完整性 |
| A4 / `censoring` 未定义且影响 metadata / validation | MODERATE | §2.1.2、§2.6、§2.9 没有 `censoring` schema，也没定义其对 metadata 与 L2 / L1 的影响 | realism 无法完整实现；validator 也不知道是否跳过 censored rows | 定义 target / direction / threshold / schema，并补 metadata / validator 规则 | 与 Blocker 7 直接相关 |
| A7 / `add_group_dependency` 多列 `on` 模式不明确 | MODERATE | §2.1.2 的 `on` 类型是 `list[str]`，但例子只展示单列条件，未定义多列权重结构 | `on=["a","b"]` 时无法建模 / 验证条件分布 | 限制为单列或正式定义 tuple / nested schema | 影响 1.7.2 / 4.1.2 |
| B1 / 非 `daily` temporal 采样语义缺失 | MODERATE | §2.1.1、§2.4 只示例 `daily` | `weekly / monthly` 等频率无法一致实现 | 定义非 `daily` 采样语义或明确不支持 | 影响 1.3.2 / 4.1.4 |
| B4 / Full DAG 构造算法未泛化 | MODERATE | §2.4 只给一个完整示例，没有完整 edge construction algorithm | 不同实现会给出不同 topo order 与 DAG 结构 | 明确所有 edge rules | 影响 3.1.1 |
| B7 / Auto-fix 的 `seed` 递增不等于真正应用修复 | MODERATE | §2.9 伪代码先 `strategy(check)` 再 `build_fn(seed=42+attempt)`，导致 fix 被丢弃 | auto-fix loop 内部自相矛盾 | 让 fix 作用于 simulator state，而不是被重建覆盖 | Alignment Map 将 9.3.1 标成 `SPEC_INCORRECT` |
| B8 / Topological sort tie-break 未定义 | MODERATE | §2.8 宣称逐 bit 可复现，但 topo sort 并非唯一，未定义 canonical tie-break | 同一 `seed` 也可能因实现差异而改变 RNG 消耗顺序 | 指定稳定 tie-break 规则 | 导致 3.1.2 从 `SPEC_READY` 下调 |
| C5 / §2.7 与 §2.9 的 loop 组合存在歧义 | MODERATE | 一个处理执行错误、一个处理验证失败，但规范未明说嵌套 / 顺序 / 升级关系 | Orchestrator 无法稳定定义重试预算与分支行为 | 明确顺序组合与预算边界 | 影响 11.1.1 / 11.1.2 |
| C6 / L1 `finite_*` 与 `missing_rate` 冲突 | MODERATE | §2.8 的 realism 可注入 `NaN`，§2.9 的 L1 又要求所有 measure 非空且有限 | realism 一开启就可能触发结构校验失败 | 定义面向 realism 场景的 L1 处理策略 | 影响 8.2.4 / 8.1.3 |
| C7 / `_get_measure_spec` 与 `iter_predictor_cells` 未定义 | MODERATE | §2.9 的 L2 直接调用 helper，但规范未定义 helper 接口与输出 | stochastic L2 无法按规格实现 | 正式定义 helper contract | 影响 8.3.1 / 8.3.2 |
| C10 / `dominance_shift` 的 L3 是黑盒 | MODERATE | §2.9 直接委托 `_verify_dominance_change`，无语义定义 | `dominance_shift` 无法实现 / 测试 | 内联或正式定义 dominance logic | 与 Pattern Blocker 相关 |
| C11 / `ranking_reversal` 绑定“第一个 group” | MODERATE | §2.9 用 metadata 中第一个 `group` 作为 `group-by` 轴，而非由 pattern 参数指定 | 即便实现也可能按错误维度计算 ranking reversal | 在 pattern params 中增加 `group_by` | 目前被 Alignment Map 记为 `SPEC_INCORRECT` |
| C12 / soft-fail 下游策略未定义 | MODERATE | §2.9 在达到最大重试次数后 `return df, report`，但未说是否可进入 Phase 3、何种失败可接受 | 下游可能接收带已知缺陷的数据 | 定义 downstream soft-fail policy | 属于 orchestration-semantic issue |
| 跨 reviewer 综合 | SYNTHESIS | 文档明确保留 4 组 synthesis：A8 + B6 + C1 是同一 pattern 主题三面；A11 vs B5 从“架构缺口”降为“示例 / 编码细节缺口”；B3 / B7 优先于 C4；C3 / C8 / C9 / C13 是 metadata 同根问题 | 为后续 blocker 建模提供结构化证据 | 本阶段仅保留冲突与合流，不裁决实现方案 | 来源：Gap Analysis 的 Cross-Reviewer Conflicts |
| 优先 blocker 顺序 | PRIORITY | Gap Analysis 给出优先顺序：1 元数据 schema；2 完整 pattern specification；3 cross-group 默认规则 + target grammar；4 L2 与 pattern + post-processing contract；5 distribution parameter schema + security model | 后续任何 completion / blocker 评估都需对齐此顺序 | 本阶段仅记录顺序，不开展解法设计 | 与 Alignment Map 的 blocker 链不同，需并存保留 |

## 5. 对齐图关键事实
| 项目 | 数值 / 内容 | 在上下文中的含义 | 备注 |
|---|---|---|---|
| 子任务总数 | `108` | Alignment Map 的工作粒度基准数 | 不能与 Sprint 计划中的 73 个可排期子任务混同 |
| 准备度计数 | `SPEC_READY 41 / NEEDS_CLARIFICATION 33 / BLOCKED 24 / SPEC_INCORRECT 10` | 给出全量准备度分布 | 原文同时给出 `38% / 31% / 22% / 9%` |
| 排期规则 | `SPEC_INCORRECT` 与 `BLOCKED` 具有同等 planning weight | 这不是实现类别统计，而是排期决策规则 | 文档明确要求二者都必须先由上游解决 |
| 关键路径 Blocker 1 | 元数据 schema 完整性：阻塞 `5.1.3 / 5.1.4 / 5.1.6 → 8.2.3 / 8.2.4 / 8.3.1 / 8.3.3 / 8.3.4 / 8.3.6 → 9.3.1 → 11.1.1` | Metadata 是 validator 与 Phase 3 的共享合同中心 | 计数写为 `9 subtasks`，另有更多间接依赖 |
| 关键路径 Blocker 2 | Formula DSL grammar：阻塞 `1.5.2 / 4.2.3 / 4.2.4 / 8.3.5` | Structural measure 从声明到 L2 residual 的全链条都依赖公式 grammar | 对应 Gap Analysis A3 |
| 关键路径 Blocker 3 | Distribution family parameter specification：阻塞 `1.4.3 / 1.4.4 / 1.5.4 / 4.2.1 / 4.2.2 / 8.3.1 / 8.3.2` | Stochastic measure 声明、采样、L2 全部依赖 family 参数表 | 包含 `mixture` 子问题 |
| 关键路径 Blocker 4 | Pattern type full specification：阻塞 `1.8.4 / 4.3.3 / 4.3.4 / 4.3.5 / 4.3.6 / 8.4.4 / 8.4.5 / (8.4.6) / (8.4.7)` | 4 类 pattern 在 SDK、engine、L3 三层都未闭环 | 对应 A8 + B6 + C1 |
| 关键路径 Blocker 5 | L2 vs pattern injection + auto-fix mutation model：直接卡住 `9.3.1`，并劣化 `8.3.1 / 9.2.1 / 9.2.2 / 9.2.3 / 4.3.1 / 4.3.2 / 11.1.1 / 11.1.2` | 不是单点缺失，而是组合系统振荡 / 修复丢失问题 | `9.3.1` 被标为 `SPEC_INCORRECT` |
| 关键路径 Blocker 6 | Phase 1 → Phase 2 接口合同：阻塞 `10.1.2 / 11.1.1` | Prompt 注入与 pipeline entry point 缺少 typed scenario contract | 文档注明基础 JSON 注入路径已存在，但 typed contract 未正式化 |
| 关键路径 Blocker 7 | `Censoring` schema：阻塞 `4.4.3` | 该 blocker 相对孤立，影响 realism 子模块 | 可机会性后置 |
| 最优解决顺序 | `1 → 2 → 3 → 6 → 4 → 5 → 7` | Alignment Map 给出的依赖深度优先顺序 | 与 Gap Analysis 的优先级顺序不同，必须并存记录 |
| 边界判断变化 | `1.6.3 / 1.7.4` 降为 `NEEDS_CLARIFICATION`；`3.1.2` 因 tie-break 降级；`4.1.1` 因 undeclared cross-group default 降级；`7.1.1` 因 security policy 降级；`8.1.3` 因 B2 / C6 交互降级；`10.2.1` 因 fence stripping 非规格要求降级 | 这些 patch log 变化定义了“什么算规格明确、什么只算实现便利” | `1.5.3 / 4.1.3 / 8.2.6` 被明确保留为 `SPEC_READY` |
| 现有基础设施假设 | `LLMClient.generate_code()` 已提供 fence stripping；`adapt_parameters()` 已处理 provider adaptation；`utils.py` 仅提供 orchestration helpers | Alignment Map 把这些列为“已有能力，Phase 2 需复用而非重写” | 影响 Module 7 / 10 / 11 的边界划分 |

## 6. Sprint 计划关键事实
| 项目 | 数值 / 内容 | 含义 | 备注 |
|---|---|---|---|
| Sprint 总数 | `8` | Sprint 1–8 覆盖“所有可排期实现项” | 来源为 Sprint Plan v4 |
| Sprint 1 | Foundation：constructor、internal registries、data classes、exception hierarchy；`9` 个子任务 | 提供零外部依赖的 SDK 基础设施 | 含 `6.1.4` 的 assumption-backed error type |
| Sprint 2 | Column declarations：`add_category + add_temporal`；`10` 个子任务 | 完成 categorical / temporal 基础声明层 | 包含若干 assumption-backed 断言 |
| Sprint 3 | Measure + Relationship API：`add_measure` 非阻塞路径、`add_measure_structural` 非阻塞路径、`declare_orthogonal`、`add_group_dependency`；`12` 个子任务 | 完成“可声明”的 SDK 主体 | 明确回避被 blocker 卡住的 family / formula / pattern 全规格 |
| Sprint 4 | Pattern / Realism stubs + DAG：`inject_pattern` 两类、`set_realism`、pre-formula-edge DAG；`9` 个子任务 | 打通完整声明相位，并开启生成相位准备 | scope note 明确不含 formula-derived edges |
| Sprint 5 | Engine α + post-processing + ready metadata；`10` 个子任务 | 第一次产出 skeleton-only DataFrame | 不包含 measure generation |
| Sprint 6 | 指定 pattern 的注入、non-censoring realism、validator framework 的 ready 部分与 L1 ready checks；`10` 个子任务 | 第一次开始对生成结果做质量验证 | `8.1.3` 被明确延后 |
| Sprint 7 | L3 指定 pattern 校验 + auto-fix isolated stubs + `_max_conditional_deviation`；`7` 个子任务 | 完成已正式指定部分的 L3 / auto-fix 外壳 | `9.2.1–9.2.3` 只做 isolated stub，不做集成证明 |
| Sprint 8 | 集成现有 `LLMClient` + sandbox error feedback loop；`6` 个子任务 | 完成 prompt / render / sandbox / feedback 侧，而非重新实现 LLM plumbing | 可与 Sprint 2–7 并行，只依赖 Sprint 1 |
| 已排期可实现子任务 | `73 = 40 SPEC_READY + 33 NEEDS_CLARIFICATION` | Sprint 1–8 累计可排期子任务数 | 来自 Sprint Summary，本阶段无需重算 |
| Blocked / spec_incorrect / deferred | `34` 个 distinct blocked backlog subtasks = `24 BLOCKED + 10 SPEC_INCORRECT`；另有 `1` 个 deferred `NEEDS_CLARIFICATION`（`8.1.3`） | Sprint 1–8 结束后的阻塞墙 | 文档专门说明是 distinct count，不要重复统计 |
| Sprint 8 之后的阻塞墙 | “After Sprint 8 completes, all 73 implementable subtasks are done.” 其余需等待 Blockers 1–6，Blocker 7 可插入任意 Sprint | 明确 Sprint 1–8 的边界不是“全部完成”，而是“先做能做的” | 这是后续 completion assessment 的基线 |
| Sprint 9+ 集成顺序 | Sprint 9：metadata + validator `SPEC_INCORRECT` + deferred `8.1.3`；Sprint 10：formula DSL；Sprint 11：distribution families；Sprint 12：剩余 4 类 pattern；Sprint 13：auto-fix retry loop + pipeline orchestrator + typed scenario injection；Blocker 7 可插入任一 Sprint | 给出 blocker 解决后的集成顺序 | 这是 Sprint Plan 的后续顺序，不是 Stage 1 结论 |
| 并行化说明 | Sprint 8 仅依赖 Sprint 1，可由第二位工程师并行开发 | 影响后续责任切分证据 | 仍需在阻塞墙前合流到 orchestrator |

## 7. 统一问题主题索引
| 主题 | 基础规格证据 | 审计证据 | 任务 / 合同证据 | 准备度 / Sprint 证据 |
|---|---|---|---|---|
| 元数据 schema | §2.6 仅给 JSON example，称其为 Phase 2→3 contract | C3 / C8 / C9 / C13 指出字段缺失、validator `KeyError`、无 schema / versioning | 5.1.3 / 5.1.4 / 5.1.6 与 8.2.3 / 8.3.3 / 8.3.4 / 8.3.6 直接读取不存在字段 | Blocker 1；Sprint 9 优先收敛 |
| Formula DSL | §2.1.1 / §2.3 只有 `formula` 字符串示例 | A3 指出 operators / precedence / symbol resolution 均未定义 | 1.5.2、4.2.3、4.2.4、8.3.5 直接依赖 grammar | Blocker 2；Sprint 10 |
| 分布族参数 | 支持 8 个 `family`，但仅示例 `mu / sigma` | A1 / A5 指出 `mixture` 与其余 family 参数键未规格化 | 1.4.3 / 1.4.4 / 1.5.4 / 4.2.1 / 4.2.2 / 8.3.1 / 8.3.2 依赖 family 参数表 | Blocker 3；Sprint 11 |
| Pattern 类型规格 | §2.1.2 列出 6 类 pattern，但只示例 2 类 `params` | A8 / B6 / C1 指出 4 类缺 `params + injection + L3` | 1.8.4 / 4.3.3–4.3.6 / 8.4.4–8.4.7 无法闭环 | Blocker 4；Sprint 12 |
| Auto-fix 变异模型 | §2.9 给出 strategy map 与 retry loop，但未定义 mutation target | B3 / B7 指出 fix 可能被重建覆盖，且会与 pattern 互相干扰 | 9.2.x 只能做 isolated stubs；9.3.1 标为 `SPEC_INCORRECT` | Blocker 5；Sprint 13 前不得宣称集成闭环 |
| Validator ↔ metadata 合同 | L1 / L2 / L3 直接从 `meta` 取字段 | C8 / C9 显示 validator code 读取了 example 中没有的字段 | hierarchy 在 8.x 完成条件中直接引用这些字段 | Alignment Map 把 Module 5 与 8.x 关联成同一 blocker 链 |
| Phase 1 → Phase 2 typed contract | §2.4 说 `target_rows` 继承自 Phase 1；§2.5 依赖 `scenario_context` 注入 | D1 被 Alignment / Sprint 引为 blocker：缺正式 typed scenario contract | 10.1.2 / 11.1.1 需要 prompt 注入与 pipeline entry | Blocker 6；Sprint 13 |
| Orchestrator / 阶段顺序 | §2.7 执行错误 loop；§2.8 engine；§2.9 validation / auto-fix | C5 指出两个 loop 的组合关系不明确 | 11.1.1–11.1.5 把顺序、预算、边界写成合同 | Sprint 8 只完成 sandbox / feedback，完整 orchestrator 进入阻塞墙 |
| Realism / validation 冲突 | §2.8 的 δ 注入 `missing / dirty / censoring`；§2.9 的 L1 要求 finite / non-null | A4 / C6 指出 `censoring` 与 `missing` 会穿透 metadata / L1 / L2 语义 | 1.9.1、4.4.1、4.4.3、8.2.4、8.1.3 都显式受影响 | Blocker 7 + deferred `8.1.3` |
| Soft-fail 下游策略 | §2.9 在达到最大重试次数后 `return df, report` | C12 指出未定义何种失败可继续下游 | 11.1.x 的 orchestrator 无法确定 soft-fail branch | 需在 blocker 解决后进入后续阶段评估 |
| Cross-group 默认语义 | §2.2 说 independence 是 opt-in，不是 default | A12 指出 undeclared pair 无默认语义 | 4.1.1、3.1.2 的合同边界受此影响 | Alignment Map 将相关任务从 `SPEC_READY` 下调 |
| Target expression grammar / security | §2.1.2 的 pattern `target` 与 §2.9 的 `df.query()` 形成隐式 contract | A13 与 A14 分别指出 grammar 缺失与 sandbox policy 缺失 | 1.8.2 仅能存储 target string；7.1.1 因 security policy 降级 | 影响 Blocker 3 / 6 之外的执行边界判断 |

## 8. 与后续完成度评估直接相关的数字池
- 权威内容源文件数：`5`
- Stage 1 读取文件总数：`7`
- Sprint 总数：`8`
- 可排期子任务总数：`73`
- `SPEC_READY` 子任务数：`41`
- `NEEDS_CLARIFICATION` 子任务数：`33`
- `BLOCKED` 子任务数：`24`
- `SPEC_INCORRECT` 子任务数：`10`
- Alignment Map 百分比分布：`38% / 31% / 22% / 9%`
- Blocked backlog distinct subtasks：`34`
- Deferred `NEEDS_CLARIFICATION` 子任务：`1`（`8.1.3`）
- Critical Path Blocker 1 直接计数：`9 subtasks`
- Critical Path Blocker 2 直接计数：`4 subtasks`
- Critical Path Blocker 3 直接计数：`7 subtasks`
- Critical Path Blocker 4 直接计数：`9 subtasks`
- Critical Path Blocker 6 直接计数：`2 subtasks`
- `max_retries`（§2.7 执行错误 loop）：`3`
- `max_retries`（§2.9 auto-fix loop）：`3`
- hierarchy 中 worst-case total attempts：`6`
- `target_rows` 典型范围：`200–500 / 500–1000 / 1000–3000`
- L1 行数容差：`10%`
- L1 / L2 的 root marginal 与 conditional deviation 阈值：`0.10`
- Chi-squared 与 KS 判定阈值：`p > 0.05`
- L3 outlier z-score 阈值：`>= 2.0`
- L3 trend break 相对变化阈值：`> 0.15`
- L2 residual mean 条件：`abs(mean) < std * 0.1`
- L2 residual std 条件：`relative error < 0.2`
- 硬约束：至少 `2` 个 dimension groups、至少 `2` 个 measures、至少 `1` 个 `declare_orthogonal()`、至少 `1` 个 structural measure、至少 `2` 次 `inject_pattern()`
- 跨章节依赖图边数：`20`

## 9. 与后续阻塞项解决直接相关的证据池
- `metadata` 示例缺 `values / weights / conditional_weights / param_model / formula / noise_sigma / pattern params`，但 validator 直接读取这些字段。标签：`incomplete contract`
- `formula` 只以字符串示例出现，没有 grammar、operator whitelist、precedence、symbol resolution 规则。标签：`missing definition`
- 支持的分布包含 `mixture`，但没有 component / weight / `param_model` 契约；其余多个 family 也缺参数键表。标签：`missing definition`
- 6 类 pattern 中仅 2 类有 `params` 示例，另外 4 类在 API、engine、L3 三层都不完整。标签：`missing definition`
- `generate_with_validation()` 先应用 fix strategy，再用新的 `build_fn(seed=...)` 重建，形成“修了但没留住”的伪代码冲突。标签：`conflict`
- §2.2 声称 cross-group independence 是 opt-in，但未给 undeclared pair 默认采样语义。标签：`orchestration-semantic issue`
- §2.8 允许 `missing_rate` / `censoring` realism，§2.9 的 L1 又要求 measure finite / non-null。标签：`conflict`
- γ pattern 注入会改变分布，而 L2 仍按声明分布做 KS；pattern 与 statistical validation 的顺序合同未定。标签：`conflict`
- `target` 交给 `df.query()`，但没有 target grammar，也没有安全边界。标签：`missing definition`
- §2.7 的执行错误 loop 与 §2.9 的 validation loop 的顺序、嵌套、升级关系未正式定义。标签：`orchestration-semantic issue`
- soft-fail `return df, report` 后是否允许进入 Phase 3、哪些失败可接受，规范未定义。标签：`orchestration-semantic issue`
- Phase 1→2 只存在 one-shot example 与现有 JSON 注入路径，没有正式 typed `ScenarioContext` 合同。标签：`incomplete contract`
- `ranking_reversal` 当前 L3 绑定 metadata 中“第一个 group”，而非 pattern 自身显式参数。标签：`missing validation`
- `dominance_shift` 仅委托 `_verify_dominance_change` 黑盒 helper，未给语义。标签：`missing validation`

## 10. 证据完整性检查
- 已明确建立：
  - Phase 2 的正式内容权威源是 5 个 `phase_2/spec/*.md` 文档，workflow / prompt 只定义阶段纪律。
  - 基础规格已明确 SDK API 名称、主流程 α / β / γ / δ、metadata 示例、L1 / L2 / L3 框架、auto-fix 外壳、prompt 硬约束。
  - Task hierarchy 已把 public API、完成条件、跨章节依赖、design-choice 边界写成实现合同。
  - Alignment Map 已给出 108 个子任务的全量准备度分布，以及 7 个关键 blocker 链。
  - Sprint Plan 已给出 Sprint 1–8 的范围、73 个可排期子任务、34 个 blocked / spec_incorrect，以及 Sprint 9+ 集成顺序。
- 仍然存在歧义：
  - formula grammar、distribution 参数键表、4 类 pattern 的 `params / injection / L3`、undeclared cross-group default、target grammar、security policy、`censoring` schema、soft-fail downstream policy、typed `ScenarioContext`。
  - `scale`、非 `daily` temporal 语义、多列 `on` schema、topological sort tie-break、dirty value 语义等仍只到 `NEEDS_CLARIFICATION` 层。
  - Gap Analysis 与 Alignment Map 的 blocker 排序不完全相同：前者给“问题优先级”，后者给“依赖深度顺序”；后续阶段必须并存引用，不可互相覆盖。
- 下一阶段必须谨慎跟踪：
  - 不要把 `SPEC_INCORRECT` 当作比 `BLOCKED` 更轻；源文档明确要求同等 planning weight。
  - 不要把 `108` 总子任务与 `73` 可排期子任务混算。
  - 不要把 `docs/phase2/...` 逻辑路径与当前工作区 `phase_2/...` 实际路径混淆。
  - 不要把基础规格中的示例自动提升为完整契约；也不要把 task hierarchy 的实现设计选择误写成基础规格要求。
  - 不要在下一阶段提前输出修复方案；Stage 1 只建立证据池与边界。
