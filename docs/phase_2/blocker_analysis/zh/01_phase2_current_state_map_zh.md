# Phase 2 当前状态图

**生成来源：** `phase_2.md`（spec）、`1_phase2_implementation_task_hierarchy.md`（task hierarchy v2）、`2_phase2_gap_analysis.md`（gap analysis v2）、`3_phase2_implementation_alignment_map.md`（alignment map v4）、`4_phase2_sprint_plan.md`（sprint plan v4）

---

## 1. Phase 2 目标

Phase 2 用 **代码即 DGP（Code-as-DGP）** 替代基于 JSON 的数据生成过程规范。由 LLM 编写可执行的 Python 脚本，调用类型安全的 SDK（`FactTableSimulator`）。每个 measure 都通过一次 SDK 调用声明为闭式数据生成程序，所有列间依赖形成显式 DAG，并由按 DAG 顺序执行的确定性引擎完成事件级行生成。一个三层验证器（结构、统计、模式）在无需额外 LLM 调用的前提下保证正确性。输出是原子粒度事实表（“主表”，即 Master Table）及其配套的 schema 元数据，这一契约会被 Phase 3 用于视图提取和 QA 生成。

系统包含三个按顺序执行的主要子系统：（1）LLM 根据场景上下文生成 SDK 脚本；（2）确定性引擎执行脚本以产出数据；（3）验证器检查输出，并在无需重新调用 LLM 的情况下自动修复失败。一个执行错误反馈循环（§2.7）包裹步骤 1–2，一个验证自动修复循环（§2.9）包裹步骤 2–3。

---

## 2. 主要功能区域

### 2A. SDK 声明 API

- **Purpose：** 为 LLM 提供一个类型安全、强校验的接口表面，用于声明表 schema、分布、依赖、模式和 realism 配置。所有声明都采用只追加（append-only）方式，并在注册时完成校验，以便在任何生成发生前就能因结构错误快速失败。
- **Included capabilities：**
  - `add_category()` — 声明分类列，支持组内层级、自动归一化、按父节点条件权重（§2.1.1、§2.2）
  - `add_temporal()` — 声明时间列，支持派生日历特征（§2.1.1、§2.2）
  - `add_measure()` — 声明随机根 measure，使用覆盖 8 个分布族的 `param_model`（intercept + effects）（§2.1.1、§2.3）
  - `add_measure_structural()` — 通过 formula + effects + noise 声明派生 measure，并创建 DAG 边（§2.1.1、§2.3）
  - `declare_orthogonal()` — 声明跨组独立性（§2.1.2、§2.2）
  - `add_group_dependency()` — 声明跨组根级条件依赖（§2.1.2、§2.2）
  - `inject_pattern()` — 6 种 pattern 类型，用于叙事驱动的异常（§2.1.2）
  - `set_realism()` — 缺失值、脏值、删失（§2.1.2）
- **Dependencies：** Dimension Group Model（数据结构）。Custom Exception Hierarchy（校验阶段的类型化错误）。
- **Main source basis：** §2.1.1、§2.1.2、§2.2、§2.3；task hierarchy 第 1.1–1.9 节。

### 2B. Dimension Group Model

- **Purpose：** 用于表示分组、组内层级、跨组正交性和跨组依赖的内部数据结构。这是 SDK API 写入、而引擎与元数据构建器读取的结构骨架。
- **Included capabilities：**
  - `DimensionGroup` dataclass — root、columns、hierarchy ordering（§2.2）
  - `OrthogonalPair` dataclass — 与顺序无关的 group pair 及其 rationale（§2.2）
  - `GroupDependency` dataclass — `child_root`、`on`、`conditional_weights`（§2.2）
- **Dependencies：** 无（基础层）。
- **Main source basis：** §2.2；task hierarchy 第 2 节。

### 2C. DAG 构建与拓扑排序

- **Purpose：** 将所有列类型（categorical、temporal、measure）和所有依赖边（组内层级、跨组依赖、时间派生、effects predictor→measure、formula measure→structural measure）合并为单一有向无环图，然后通过拓扑排序计算生成顺序。
- **Included capabilities：**
  - `_build_full_dag()` — 从所有 registry 构建完整生成 DAG（§2.4、§2.8）
  - `topological_sort()` — 计算生成顺序；若存在环则抛出 `CyclicDependencyError`（§2.4、§2.8）
  - Measure 子 DAG 提取 — 用于 measure 专用拓扑顺序（§2.3、§2.6）
- **Dependencies：** SDK 声明 API（所有 registry 必须先填充完成）。Dimension Group Model（组层级提供边）。
- **Main source basis：** §2.4、§2.8；task hierarchy 第 3 节。

### 2D. 确定性引擎（`generate()`）

- **Purpose：** 执行按 DAG 排序、完全确定性的 pipeline，将声明转换为主 DataFrame。给定相同 seed，输出按位可复现。不调用 LLM。
- **Included capabilities：**
  - Phase α — Skeleton builder：采样独立根、跨组依赖根、组内子列、时间根、时间派生列（§2.4 Step 1、§2.8）
  - Phase β — Measure generation：随机参数解析 + 域校验 + 面向 8 个分布族的采样分发；结构公式求值 + effect 物化 + noise 采样；安全表达式求值器（§2.3、§2.4 Step 2、§2.8）
  - Phase γ — Pattern injection：生成后应用 6 种 pattern 类型变换（§2.8）
  - Phase δ — Realism injection：缺失值、脏值、删失（§2.8）
  - Post-processing：DataFrame 组装、dtype 转换（§2.8）
  - 确定性验证：相同 seed 下按位可复现（§2.8）
- **Dependencies：** DAG 构建（拓扑顺序驱动生成序列）。SDK 声明 API（引擎读取所有声明）。Custom Exception Hierarchy（域校验错误）。
- **Main source basis：** §2.4、§2.8；task hierarchy 第 4 节。

### 2E. Schema 元数据构建器

- **Purpose：** 生成结构化元数据 dict，作为 Phase 2（生产者）与 Phase 3 + validator（消费者）之间的契约。内容包含 dimension groups、orthogonal 声明、group dependencies、逐列元数据、measure DAG 顺序、patterns 和总行数。
- **Included capabilities：**
  - 输出 `dimension_groups`、`orthogonal_groups`、`group_dependencies`、`columns`、`measure_dag_order`、`patterns`、`total_rows` 这些区块（§2.6）
- **Dependencies：** 所有 SDK registry（读取全部内部数据结构）。DAG 构建（`measure_dag_order` 来自拓扑排序）。
- **Main source basis：** §2.6；task hierarchy 第 5 节。

### 2F. 自定义异常层级

- **Purpose：** 提供带类型、可描述的异常，以支持 LLM 自纠循环（§2.7）。异常消息包含精确的约束违规内容，便于定向修复。
- **Included capabilities：**
  - `CyclicDependencyError` — 消息中包含环路径（§2.7）
  - `UndefinedEffectError` — effect 名称 + 缺失 key（§2.7）
  - `NonRootDependencyError` — 非根列名称（§2.7）
  - `InvalidParameterError` — 退化/非法的分布参数（§2.7，推断）
- **Dependencies：** 无（基础层）。
- **Main source basis：** §2.7；task hierarchy 第 6 节。

### 2G. 执行错误反馈循环（§2.7 Loop）

- **Purpose：** 在 sandbox 中执行 LLM 生成的代码，捕获 SDK 异常，格式化错误反馈，并最多重试 3 次 LLM 代码生成。这是代码级自纠机制。
- **Included capabilities：**
  - Sandbox executor — 运行 `build_fact_table()`，捕获异常和 traceback（§2.7 steps 1–2）
  - 错误反馈格式化器 — 4 组件载荷：代码、异常类、traceback、修复指令（§2.7 step 5）
  - `max_retries=3` 的重试循环（§2.7 step 6）
- **Dependencies：** Custom Exception Hierarchy（需要捕获的异常）。LLM 代码生成 prompt（负责产出待执行代码）。现有 `LLMClient` 基础设施（提供带 fence stripping 和 provider adaptation 的 `generate_code()`）。
- **Main source basis：** §2.7；task hierarchy 第 7 节。

### 2H. 三层验证器

- **Purpose：** 在引擎产出主表后，以确定性方式在三个层面检查正确性：结构层（L1）、统计层（L2）和模式层（L3），无需 LLM 调用。
- **Included capabilities：**
  - Validator framework：`Check` dataclass、`ValidationReport` 聚合器、`validate(df, meta)` 编排器（§2.9）
  - L1 结构层：行数、分类基数、根边际权重、measure 有限性、orthogonal 独立性（卡方检验）、DAG 无环性（§2.9）
  - L2 统计层：针对随机 measure 的每个 predictor cell 的 KS 检验、结构残差均值/标准差检查、group dependency 条件偏差、辅助函数（`iter_predictor_cells`、`_max_conditional_deviation`、`eval_formula`）（§2.9）
  - L3 模式层：离群实体 z-score、排名逆转秩相关、趋势断裂幅度、主导权转移、收敛、季节异常（§2.9）
- **Dependencies：** Schema 元数据构建器（validator 读取 metadata）。确定性引擎（产出待验证的 DataFrame）。Formula DSL（L2 残差检查复用 `eval_formula`）。
- **Main source basis：** §2.9；task hierarchy 第 8 节。

### 2I. 自动修复循环

- **Purpose：** 当验证失败时，自动调整参数并重新生成，而不重新调用 LLM。通过 glob 模式将失败检查名称映射到修复策略。
- **Included capabilities：**
  - `match_strategy()` — 基于 glob 的分发，从检查名映射到修复函数（§2.9）
  - `widen_variance()` — 针对 KS 失败，将 sigma/scale 按 1.2 倍放大（§2.9）
  - `amplify_magnitude()` — 针对离群点/趋势失败，将 pattern 幅度按 1.3 倍放大（§2.9）
  - `reshuffle_pair()` — 通过打乱一对列中的一列，破坏伪相关以修复 orthogonal 失败（§2.9）
  - `generate_with_validation()` — 外层重试循环，`max_retries=3`，并递增 seed（§2.9）
- **Dependencies：** 三层验证器（产出失败报告）。确定性引擎（重生成目标）。Schema 元数据构建器（metadata 契约）。
- **Main source basis：** §2.9；task hierarchy 第 9 节。

### 2J. LLM 代码生成 Prompt 与集成

- **Purpose：** 构建 system prompt，指导 LLM 生成合法的 SDK 脚本，注入来自 Phase 1 的场景上下文，并解析/校验 LLM 响应。
- **Included capabilities：**
  - System prompt 模板 — SDK 参考、硬约束、软指导、one-shot 示例、场景占位符（§2.5）
  - 场景上下文注入 — Phase 1 → Phase 2 的类型化契约（§2.5）
  - 响应解析 — 提取 Python 代码，并验证其包含 `build_fact_table` 和 `sim.generate()`（§2.5）
- **Dependencies：** Phase 1 输出（场景上下文）。现有 `LLMClient` 基础设施（fence stripping、provider adaptation）。
- **Main source basis：** §2.5；task hierarchy 第 10 节。

### 2K. 端到端 pipeline 编排器

- **Purpose：** 将所有子系统组合成单一 pipeline：prompt 构建 → LLM 调用 → 代码提取 → sandbox 执行 → 引擎生成 → 三层验证 → 返回结果。执行错误时转入 §2.7 循环；验证失败时转入 §2.9 自动修复循环。
- **Included capabilities：**
  - 阶段顺序与分支行为（§2.7 + §2.8 + §2.9）
  - §2.7 执行错误循环驱动器
  - §2.9 验证循环驱动器
  - 两个循环的顺序组合
  - 预算约束（最多 3 次 LLM 调用 + 3 次引擎重跑 = 共 6 次）
- **Dependencies：** 所有其他功能区域。Phase 1 接口契约。已解析的循环组合语义。
- **Main source basis：** §2.7、§2.8、§2.9；task hierarchy 第 11、12 节。

---

## 3. Sprint 8 之后的状态

### 2A. SDK 声明 API

- **Status：部分开发完成**
- **Sprint 8 已覆盖：**
  - 构造函数 + registries（Sprint 1：1.1.1、1.1.2）
  - `add_category()` — 包含边界情况、按父节点权重、group registry 在内的全部 6 个子任务（Sprint 2：1.2.1–1.2.6）
  - `add_temporal()` — 包含 derive 白名单、temporal group 注册在内的全部 4 个子任务（Sprint 2：1.3.1–1.3.4）
  - `add_measure()` — family 校验、常量 `param_model`、DAG 根注册（Sprint 3：1.4.1、1.4.2、1.4.5）。`scale` 参数已接受并存储，同时发出 warning。
  - `add_measure_structural()` — 签名校验、effects dict 校验、环检测（Sprint 3：1.5.1、1.5.3、1.5.5）
  - `declare_orthogonal()` — 包含冲突检查在内的全部 3 个子任务（Sprint 3：1.6.1–1.6.3）
  - `add_group_dependency()` — 仅根节点约束、条件权重校验（单列 `on`）、根 DAG 无环性、与 orthogonal 的冲突检查（Sprint 3–4：1.7.1–1.7.4）
  - `inject_pattern()` — 类型校验、目标存储、列校验、pattern 存储（Sprint 4：1.8.1–1.8.3、1.8.5）。目前只有 outlier_entity 和 trend_break 具备参数校验。
  - `set_realism()` — 签名和 rate 校验；删失被作为 opaque dict 接受（Sprint 4：1.9.1）
- **仍缺失：**
  - 面向 8 个分布族中 6 个的 `param_model` intercept+effects 完整校验（1.4.3 — 受 A5/A5a 阻塞）
  - `mixture` family 的子规范（1.4.4 — 受 A1 阻塞）
  - Formula 符号解析与 DAG 边创建（1.5.2 — 受 A3 阻塞）
  - 按 family 的 noise 规范参数校验（1.5.4 — 受 A5/A1a 阻塞）
  - 面向 6 类 pattern 中 4 类的参数校验（1.8.4 — 受 A8 阻塞）
- **阻塞 / 不清晰点：**
  - Blocker 2（A3）：Formula DSL grammar 未定义，完全阻塞 formula 符号解析
  - Blocker 3（A5、A1）：8 个分布族中 6 个的参数 key 未指定；`mixture` 完全没有规范
  - Blocker 4（A8）：`ranking_reversal`、`dominance_shift`、`convergence`、`seasonal_anomaly` 的 pattern 参数 schema 缺失
  - 多个 NEEDS_CLARIFICATION 假设已锁定：A9（至少 2 个值）、A6（完整父键）、A7（单列 `on`）、A10（单一时间列，保留名 `"time"`）、A2（`scale` 存储/忽略）
- **Evidence：** Sprint plan 的 Sprints 1–4 覆盖了 Module 1 中 41 个子任务里的 36 个；alignment map 显示 1.4.3、1.4.4、1.5.2、1.5.4、1.8.4 中有 5 个 BLOCKED 子任务。

### 2B. Dimension Group Model

- **Status：已开发完成**
- **Sprint 8 已覆盖：** Sprint 1 中已完成全部 3 个子任务（2.1.1、2.2.1、2.2.2）。
- **仍缺失：** 无。
- **阻塞 / 不清晰点：** 无。
- **Evidence：** Alignment map 将全部 3 个子任务标记为 SPEC_READY。Sprint plan 的 Sprint 1 包含这三项。

### 2C. DAG 构建与拓扑排序

- **Status：部分开发完成**
- **Sprint 8 已覆盖：**
  - `_build_full_dag()` 已实现边类型 1–4：parent→child、on→child_root、temporal_root→derived、effects predictor→measure（Sprint 4：3.1.1）
  - `topological_sort()` 已针对 formula 边加入前的 DAG 实现，并采用字典序 tie-breaking 假设（Sprint 4：3.1.2）
  - Measure 子 DAG 提取（Sprint 4：3.2.1）
- **仍缺失：**
  - 边类型 5：formula 中 measure 引用 → structural measure 边。在定义 Formula DSL grammar 之前无法加入这些边（Blocker 2）。
- **阻塞 / 不清晰点：**
  - Blocker 2（A3）：由 formula 派生的 DAG 边需要一个目前尚不存在的 parser。
  - NEEDS_CLARIFICATION：B4（通用边构建算法为推断所得，并未形式化）、B8（topo-sort 的 tie-breaking 被假定为字典序，但 spec 未定义）、B5（在规则 4 下假定 temporal predictor 边被纳入）。
- **Evidence：** Sprint plan 的 Sprint 4 范围说明明确写明“structural measure formula edges are not yet available”。Alignment map 将 3.1.1 和 3.1.2 标记为 NEEDS_CLARIFICATION。

### 2D. 确定性引擎（`generate()`）

- **Status：部分开发完成**
- **Sprint 8 已覆盖：**
  - Phase α skeleton builder — 5 个子任务全部完成：独立根、跨组依赖根、组内子列、时间根、时间派生（Sprint 5：4.1.1–4.1.5）
  - Phase γ 部分完成 — outlier entity 注入与 trend break 注入（Sprint 6：4.3.1、4.3.2）
  - Phase δ 部分完成 — 缺失值注入与脏值注入（Sprint 6：4.4.1、4.4.2）
  - Post-processing — DataFrame 组装与 dtype 转换（Sprint 5：4.5.1）
- **仍缺失：**
  - Phase β — 所有 measure 生成子任务（4.2.1–4.2.4：随机参数解析、域校验、采样分发、分布分发表；4.2.5–4.2.8：结构公式求值、effect 物化、noise 采样、安全表达式求值器）。全部 BLOCKED。
  - Phase γ — 6 类 pattern 注入中的 4 类：`ranking_reversal`、`dominance_shift`、`convergence`、`seasonal_anomaly`（4.3.3–4.3.6）。全部 BLOCKED。
  - Phase δ — 删失注入（4.4.3）。BLOCKED。
  - 确定性验证（4.6.1）— 未排入 Sprints 1–8；依赖 measure generation 的存在。
- **阻塞 / 不清晰点：**
  - Blocker 2（A3）：阻塞全部 structural measure 生成（formula 求值、安全表达式求值器）
  - Blocker 3（A5、A1）：阻塞全部随机 measure 生成（面向 8 个族中 6 个的参数解析与采样分发）
  - Blocker 4（A8、B6）：阻塞 6 类 pattern 注入中的 4 类
  - Blocker 7（A4）：阻塞删失注入
  - B2：Pattern 注入与 L2 验证的冲突已被承认，但被延期为“validator 问题”
- **Evidence：** Sprint plan 显示 4.2.x 全部位于 Blocked Backlog（Blockers 2 和 3）。Sprint plan 显示 4.3.3–4.3.6 位于 Blocked Backlog（Blocker 4）。Alignment map 确认 4.2 中全部 4 个子任务均为 BLOCKED，4.3 中 6 个子任务里有 4 个为 BLOCKED。

### 2E. Schema 元数据构建器

- **Status：部分开发完成**
- **Sprint 8 已覆盖：**
  - `dimension_groups` 区块（Sprint 5：5.1.1）
  - `orthogonal_groups` 区块（Sprint 5：5.1.2）
  - `measure_dag_order` 区块（Sprint 5：5.1.5）
  - `total_rows` 区块（Sprint 5：5.1.7）
- **仍缺失：**
  - `group_dependencies` 区块 — 必须包含 `conditional_weights`，但 §2.6 示例未给出（5.1.3 — SPEC_INCORRECT）
  - `columns` 区块 — 必须包含 `values`、`weights`、`formula`、`noise_sigma`、`param_model`、`scale`、按父节点条件权重等字段，但 §2.6 示例未给出（5.1.4 — SPEC_INCORRECT）
  - `patterns` 区块 — 必须包含 `params`，但 §2.6 示例未给出（5.1.6 — SPEC_INCORRECT）
- **阻塞 / 不清晰点：**
  - Blocker 1（C3、C8、C9、C13）：§2.6 元数据 schema 仅通过示例定义，且与 §2.9 validator 代码内部不一致。validator 会读取元数据示例未输出的字段（`col["values"]`、`col["weights"]`、`col["formula"]`、`col["noise_sigma"]`、`dep["conditional_weights"]`、`p["metrics"]`）。没有正式 schema，没有类型，也没有版本机制。
  - 7 个子任务中有 3 个是 SPEC_INCORRECT —— 有规范，但该规范与 validator 的预期相矛盾。
- **Evidence：** Alignment map 将 5.1.3、5.1.4、5.1.6 标记为 SPEC_INCORRECT。Sprint plan 将这三项全部放入 Blocker 1 下的 Blocked Backlog。Sprint 5 仅覆盖 4 个无冲突字段。

### 2F. 自定义异常层级

- **Status：已开发完成**
- **Sprint 8 已覆盖：** Sprint 1 中已完成全部 4 个子任务（6.1.1–6.1.4，包括前置性的 `InvalidParameterError`）。
- **仍缺失：** 当前范围内无。
- **阻塞 / 不清晰点：** A5a（哪些参数域违规会触发 `InvalidParameterError`）仍是 NEEDS_CLARIFICATION；异常类本身已存在，但其触发条件依赖 Blocker 3 的解决。
- **Evidence：** Sprint plan 的 Sprint 1 包含全部 4 个子任务。Alignment map 显示 3 个 SPEC_READY + 1 个 NEEDS_CLARIFICATION。

### 2G. 执行错误反馈循环

- **Status：部分开发完成**
- **Sprint 8 已覆盖：**
  - Sandbox executor（Sprint 8：7.1.1）— 带有关于安全策略的 NEEDS_CLARIFICATION
  - 错误反馈格式化器（Sprint 8：7.1.2）
  - `max_retries=3` 的重试循环（Sprint 8：7.1.3）— 基于与 §2.9 循环顺序组合的假设
- **仍缺失：** 安全加固（import 白名单、资源限制、超时）— 延后至 spec 明确定义策略后处理。
- **阻塞 / 不清晰点：**
  - A14：未指定安全/sandbox 策略（CRITICAL gap，但该子任务仍可先做基础执行）
  - C5：与 §2.9 的循环组合被假定为顺序式，而非正式规定
- **Evidence：** Sprint plan 的 Sprint 8 覆盖全部 3 个子任务。Alignment map 显示 1 个 SPEC_READY + 2 个 NEEDS_CLARIFICATION。

### 2H. 三层验证器

- **Status：部分开发完成**
- **Sprint 8 已覆盖：**
  - Framework：`Check` dataclass、`ValidationReport` 聚合器（Sprint 6：8.1.1、8.1.2）
  - L1：行数、分类基数、orthogonal 独立性（卡方检验）、DAG 无环性复查（Sprint 6：8.2.1、8.2.2、8.2.5、8.2.6）
  - L3（部分）：离群实体 z-score 检查、趋势断裂幅度检查（Sprint 7：8.4.1、8.4.3）
  - L2 helper：`_max_conditional_deviation()`（Sprint 7：8.3.7）
- **仍缺失：**
  - Validator 编排器 `validate(df, meta)`（8.1.3 — DEFERRED，依赖 B2/C6 的解决）
  - L1：根边际权重检查（8.2.3 — SPEC_INCORRECT，需要 `col["values"]`/`col["weights"]`）、measure 有限性检查（8.2.4 — SPEC_INCORRECT，与 realism NaN 冲突）
  - L2：全部实质性检查 — 每个 predictor cell 的 KS 检验（8.3.1 — BLOCKED）、`iter_predictor_cells`（8.3.2 — BLOCKED）、结构残差均值（8.3.3 — SPEC_INCORRECT）、结构残差标准差（8.3.4 — SPEC_INCORRECT）、L2 用 `eval_formula`（8.3.5 — BLOCKED）、group dependency 条件偏差（8.3.6 — SPEC_INCORRECT）
  - L3：排名逆转检查（8.4.2 — SPEC_INCORRECT）、主导权转移检查与 helper（8.4.4、8.4.5 — BLOCKED）、收敛验证（8.4.6 — BLOCKED）、季节异常验证（8.4.7 — BLOCKED）
- **阻塞 / 不清晰点：**
  - Blocker 1（C3、C8、C9）：元数据缺失 validator 所读取的字段 → 导致 5 个 SPEC_INCORRECT 子任务
  - Blocker 2（A3）：用于 L2 残差计算的 `eval_formula` 被阻塞
  - Blocker 3（A5、A1、C7）：KS 检验被阻塞（没有 family→scipy 的映射，没有 `iter_predictor_cells` 算法，`mixture` 没有 CDF）
  - Blocker 4（C1、C10、B6）：4 个定义不足的 pattern 类型的 L3 分支均被阻塞
  - Blocker 5（B2）：L2 在注入后数据上运行，却拿注入前参数做对照 —— 结构性矛盾
  - C6：L1 有限性检查与 realism 的 NaN 注入冲突
  - C11：排名逆转逻辑硬编码使用第一个 dimension group
- **Evidence：** Alignment map：Module 8 共 23 个子任务；其中只有 9 个进入 Sprints 1–8。Sprint plan 的 Blocked Backlog 在 8.2 中列出 2 个 SPEC_INCORRECT，在 8.3 中列出 3 个 BLOCKED + 3 个 SPEC_INCORRECT，在 8.4 中列出 4 个 BLOCKED + 1 个 SPEC_INCORRECT。Module 8.3（L2）没有任何 SPEC_READY 子任务。

### 2I. 自动修复循环

- **Status：部分开发完成（仅 stubs）**
- **Sprint 8 已覆盖：**
  - `match_strategy()` glob 匹配器（Sprint 7：9.1.1）
  - `widen_variance()` 作为独立 stub（Sprint 7：9.2.1）
  - `amplify_magnitude()` 作为独立 stub（Sprint 7：9.2.2）
  - `reshuffle_pair()` 作为独立 stub（Sprint 7：9.2.3）
- **仍缺失：**
  - `generate_with_validation()` 重试循环（9.3.1 — SPEC_INCORRECT：伪代码会先应用修复，再在重生成时丢弃修复）
  - 三种修复策略的集成级测试（延期，直到 B2/B3 解决）
  - 无 LLM 升级边界约束（9.3.2 — task hierarchy 已定义，但依赖 9.3.1）
- **阻塞 / 不清晰点：**
  - Blocker 5（B2、B3、B7）：自动修复的 mutation model 未定义 —— 修复应修改 simulator 实例还是脚本？伪代码中的 `build_fn(seed=42+attempt)` 会丢弃所有修复。这是 SPEC_INCORRECT 的矛盾，不只是规范缺失。
  - C5：§2.7 与 §2.9 两个循环的组合方式未定义
  - C4：9 种以上失败模式中只有 4 种有修复策略；row_count、cardinality、marginal weights、finite、structural residuals 都没有策略
- **Evidence：** Sprint plan 的 Sprint 7 明确将 9.2.1–9.2.3 标为“isolated stubs”。Alignment map 将 9.3.1 标记为 SPEC_INCORRECT。Sprint plan 的 Blocked Backlog 将 9.3.1 列在 Blocker 5 下。

### 2J. LLM 代码生成 Prompt 与集成

- **Status：部分开发完成**
- **Sprint 8 已覆盖：**
  - System prompt 构建（Sprint 8：10.1.1）
  - `LLMClient.generate_code()` 的 fence stripping 集成验证（Sprint 8：10.2.1）
  - 针对 `build_fact_table` + `generate()` 的代码校验（Sprint 8：10.2.2）
- **仍缺失：**
  - 带类型契约的场景上下文注入（10.1.2 — 受 D1 阻塞）
- **阻塞 / 不清晰点：**
  - Blocker 6（D1）：Phase 1 → Phase 2 的场景上下文没有正式类型 schema。现有系统已具备可工作的 JSON 注入路径（`json.dumps(scenario)` → `LLMClient`），但所需的类型化契约（必填/选填字段、校验、版本化）尚未定义。阻塞点在形式化，而非基础能力。
- **Evidence：** Sprint plan 的 Sprint 8 覆盖了 4 个子任务中的 3 个。10.1.2 位于 Blocker 6 下的 Blocked Backlog。Alignment map v3 指出已有 `ScenarioContextualizer.validate_output()` 可作为事实上的起点。

### 2K. 端到端 pipeline 编排器

- **Status：尚未开发**
- **Sprint 8 已覆盖：** 无。两个子任务都处于 BLOCKED。
- **仍缺失：**
  - 完整 pipeline 编排：prompt → execute → validate → return（11.1.1）
  - 循环连接：§2.7 + §2.9 的组合（11.1.2）
  - 集成测试：§2.10 下游可用性验证（12.1.1）
- **阻塞 / 不清晰点：**
  - 复合阻塞（C5 + D1）：循环组合语义和 Phase 1 类型化契约都必须先解决。编排器处于终端依赖位置 —— 在几乎所有上游阻塞解决前都无法接线。
  - Blocker 5（B2、B3）：自动修复循环本身是 SPEC_INCORRECT；编排器无法组合一个错误的循环。
  - 架构参考已存在于 `audit/5_agpds_pipeline_runner_redesign.md`（见 alignment map v4 注记），但它不属于这 5 份 spec 文档的一部分。
- **Evidence：** Sprint plan 将 11.1.1 和 11.1.2 都放在“Blocker Composite”下的 Blocked Backlog。Alignment map 确认二者均为 BLOCKED。关键路径图显示 Sprint 8 之后有一道 “[BLOCKED WALL]”。

---

## 4. 跨区域观察

### 关键架构依赖

依赖链条既严格又很深。三层基础层（Dimension Group Model → SDK 声明 API → DAG 构建）向确定性引擎供给输入；确定性引擎再向 Schema 元数据构建器与三层验证器供给输入；这两者再向自动修复循环供给输入；自动修复循环再与执行错误反馈循环一起向 pipeline 编排器供给输入。这条链意味着中间层（引擎、元数据、validator）上的阻塞会向下游级联放大。

Schema 元数据构建器（2E）是引擎（生产者）、validator（消费者）和 Phase 3（消费者）之间唯一共享的契约。它处于 SPEC_INCORRECT 状态，是杠杆效应最高的阻塞点 —— 一旦解决，就能同时解锁 9 个以上 validator 子任务，并打通自动修复循环和编排器路径。

### 未完成工作的主要集中区

**确定性引擎的 Phase β**（measure 生成）完全未实现。围绕随机与结构 measure 生成的全部 8 个子任务都分别被两类独立阻塞（A3 formula DSL、A5 分布族）卡住。这是整个系统的核心数据生成能力 —— 没有它，引擎只能产出不含任何 measure 列的 skeleton-only DataFrame。

**三层验证器的 L2**（统计验证）是整个系统中阻塞最严重的模块。7 个子任务中，3 个 BLOCKED，3 个 SPEC_INCORRECT，只有 1 个 SPEC_READY（`_max_conditional_deviation` helper）。L2 同时依赖 Blockers 1、2、3 和 5。它也是复合问题最多的模块：KS test 失败会与 pattern injection（B2）交互；`mixture` 分布没有 scipy CDF（A1b）；cell 稀疏性会削弱检验能力（C2）；而 metadata 又没有输出 validator 所读取的字段（C8/C9）。

### 被阻塞工作的主要集中区

按 blocker 分类，blocked backlog 的分布如下（来自 alignment map 和 sprint plan）：

- **Blocker 1（Metadata Schema）：** 涉及 Modules 5、8 中 9 个以上子任务。杠杆最高 —— 解决后可消除 SPEC_INCORRECT 型矛盾。
- **Blocker 2（Formula DSL）：** 涉及 Modules 1、4、8 中 4 个子任务。会端到端阻塞整个 structural measure pipeline。
- **Blocker 3（Distribution Families）：** 涉及 Modules 1、4、8 中 7 个子任务。会阻塞整个随机 measure pipeline。
- **Blocker 4（Pattern Types）：** 涉及 Modules 1、4、8 中 9 个子任务。会阻塞 6 类 pattern 注入/验证中的 4 类。
- **Blocker 5（L2/Pattern + Auto-Fix Model）：** 直接只有 1 个 SPEC_INCORRECT 子任务（9.3.1），但会间接劣化 8 个以上任务。组合后的系统会在 L2 与 L3 修复之间来回振荡。
- **Blocker 6（Phase 1 Contract）：** 2 个子任务（10.1.2、11.1.1）。由于现有 JSON 注入路径的存在，影响有所缓和，但仍阻碍形式化。
- **Blocker 7（Censoring）：** 1 个子任务（4.4.3）。范围孤立，优先级低。

总计：24 个 BLOCKED + 10 个 SPEC_INCORRECT + 1 个延后的 NEEDS_CLARIFICATION = **35 个子任务**，超出 Sprint 8 的覆盖范围。

### 文档冲突或歧义

1. **§2.6 metadata vs. §2.9 validator 代码**（C3、C8、C9）：metadata 示例遗漏了 validator 伪代码所读取的字段。这是影响最大的内部矛盾 —— 它使 validator 无法针对 metadata 契约完成实现。
2. **§2.9 auto-fix 伪代码的自相矛盾**（B3、B7）：伪代码先应用修复策略（lines 695–698），随后又调用 `build_fn(seed=42+attempt)`（line 691）从头重新执行原始 LLM 脚本，从而丢弃全部修复。同一段代码块中的修复与重生成逻辑彼此冲突。
3. **§2.8 Phase γ vs. §2.9 L2**（B2）：Pattern injection 在 measure generation 之后故意扭曲分布。随后 L2 又拿这些被扭曲后的分布去对照原始声明参数做检验。如果没有一个注入前/注入后的验证边界，这两个设计决策在结构上并不兼容。
4. **§2.9 L1 有限性 vs. §2.8 Phase δ realism**（C6）：L1 断言 measure 必须满足 `notna().all()`。Phase δ 却会按 `missing_rate` 故意引入 NaN。当 realism 启用时，这在设计上就是冲突的。
5. **跨组默认语义**（A12）：§2.2 说独立性是“opt-in, not default”，但从未定义真正的默认行为。这会影响所有包含 3 个以上 dimension group 的场景。

---

## 5. 精简证据表


| Functional area                   | Sprint 8 之后的状态 | 原因                                                                                                              | 主要来源                                                   |
| --------------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| 2A. SDK Declaration API           | 部分开发完成         | Sprints 1–4 中完成 41 个子任务里的 36 个；剩余 5 个因 formula DSL（A3）、distribution families（A5/A1）、pattern params（A8）而 BLOCKED | Alignment map §1.2–1.9；Sprint plan Sprints 1–4         |
| 2B. Dimension Group Model         | 已开发完成          | 全部 3 个子任务在 Sprint 1 完成                                                                                          | Alignment map §2；Sprint plan Sprint 1                  |
| 2C. DAG Construction              | 部分开发完成         | 已构建边类型 1–4；类型 5（formula）受 A3 阻塞                                                                                 | Sprint plan Sprint 4 范围说明；Alignment map §3             |
| 2D. Deterministic Engine          | 部分开发完成         | Phase α 完成；Phase β 全部 BLOCKED（A3、A5）；Phase γ 完成 2/6；Phase δ 完成 2/3                                              | Alignment map §4.2（全部 BLOCKED）；Sprint plan Sprints 5–6 |
| 2E. Schema Metadata Builder       | 部分开发完成         | 7 个字段中已输出 4 个；其中 3 个是 SPEC_INCORRECT（metadata/validator 矛盾 C3/C8/C9）                                            | Alignment map §5；Sprint plan 中的 Blocker 1              |
| 2F. Custom Exception Hierarchy    | 已开发完成          | 全部 4 个子任务在 Sprint 1 完成                                                                                          | Alignment map §6；Sprint plan Sprint 1                  |
| 2G. Execution-Error Feedback Loop | 部分开发完成         | 全部 3 个子任务进入 Sprint 8；安全策略（A14）被延期                                                                               | Alignment map §7；Sprint plan Sprint 8                  |
| 2H. Three-Layer Validator         | 部分开发完成         | 23 个子任务中完成 9 个；L2 没有任何实质检查（全部 BLOCKED/SPEC_INCORRECT）；L3 缺少 7 个子任务中的 5 个                                        | Alignment map §8；Blocked Backlog Blockers 1–4          |
| 2I. Auto-Fix Loop                 | 部分开发完成（stubs）  | 5 个子任务中 4 个是独立 stubs；重试循环是 SPEC_INCORRECT（B3/B7）；集成延期                                                           | Alignment map §9；Sprint 7 依赖说明                         |
| 2J. LLM Prompt & Integration      | 部分开发完成         | 4 个子任务中 3 个进入 Sprint 8；场景注入因 D1（类型契约形式化）被阻塞                                                                     | Alignment map §10；Blocker 6                            |
| 2K. Pipeline Orchestrator         | 尚未开发           | 两个子任务都因 C5 + D1 BLOCKED；终端依赖于全部上游                                                                               | Alignment map §11；Blocker Composite                    |


