# Phase 2 阻塞项分解

**生成来源：** `phase_2.md`（spec）、`1_phase2_implementation_task_hierarchy.md`（task hierarchy v2）、`2_phase2_gap_analysis.md`（gap analysis v2）、`3_phase2_implementation_alignment_map.md`（alignment map v4）、`4_phase2_sprint_plan.md`（sprint plan v4）、`01_phase2_current_state_map.md`（Stage 1 输出）

**方法：** 根因级阻塞分解。每个 blocker 都从高层原因一路追踪到具体的实现后果，并以源文档证据为依据。当 Stage 1 当前状态图与源文档冲突时，以源文档为准，并在文中注明修正。

---

## 1. 执行视图

Phase 2 的受阻工作在 108 个总子任务中占 35 个（24 个 BLOCKED + 10 个 SPEC_INCORRECT + 1 个 deferred），大约占整个系统的三分之一。这些 blocker **并不是** 零散分布在互不相关的功能上。它们高度集中在 **三个根问题** 周围，并沿架构向下游级联传播：

**主导性的 blocker 类型是共享契约缺失。** spec 定义了多个必须就数据格式达成一致的子系统（engine、metadata、validator、auto-fix），但从未正式定义这些格式。§2.6 中的 metadata schema 仅由一个 JSON 示例给出，而这个示例遗漏了 §2.9 validator 伪代码会读取的字段。Formula DSL 在三个模块中被使用，却没有 grammar。分布参数 schema 同时被 SDK、engine 和 validator 使用，却没有参考表。这些本质上都是生产者与一个或多个消费者之间缺失的契约。

**第二类 blocker 是行为三元组未指定。** 6 种 pattern 类型中的 4 种，以及 9 种 auto-fix 失败模式中的 4 种，都只以名称形式存在，没有经过协同设计的（params、algorithm、validation）规范。这里缺的不是文档，而是需要同时定义三个紧密耦合组件的设计决策。

**第三类 blocker 是组合行为自相矛盾。** Auto-fix 的伪代码先应用参数修复，再从头重新生成，从而丢弃修复。L2 validator 会拿注入后的分布去对照注入前的参数。L1 的有限性检查会拒绝 realism 阶段故意引入的 NaN。这些不是模糊点，而是 spec 伪代码内部的矛盾。

**结构性观察：** 这三个根问题是分层的。缺失契约（类型 1）是基础层，它既阻塞行为三元组（类型 2，它们需要参数 schema 才能定义），也阻塞组合行为（类型 3，它需要 metadata 契约才能据此验证）。矛盾的组合行为（类型 3）还依赖类型 2，因为在 pattern injection 语义明确之前，L2/pattern 振荡问题无法解决。这种分层关系意味着，只要解决大约 5 个契约级决策，就能立刻解锁约 20 个子任务，并为剩余约 15 个任务的解决创造条件。

**对 Stage 1 的修正：** Stage 1 当前状态图（§4 “Cross-area observations”）正确识别了依赖链和 metadata schema 是杠杆最高的 blocker。但它将这些 blocker 呈现为 7 个并行项。本分解表明，它们实际上可以收束为 3 个根因，并且彼此之间存在严格的依赖顺序；此外，一些看起来“独立”的 blocker（A12 跨组默认值、A13 target grammar、C6 L1/realism 冲突）其实是共享契约缺失这一根因的下游症状，而不是独立 blocker。

---

## 2. 主要阻塞项

### 2.1 Schema 元数据契约未定义

#### A. 被阻塞的能力

Metadata schema（§2.6）是 engine（生产者）、三层 validator（消费者）、Phase 3（消费者）和 auto-fix loop（消费者）之间唯一共享的数据契约。它当前的状态是只有一个 JSON 示例、没有正式定义，这使得 9 个以上子任务无法实现，并会让每一个引用 metadata 未输出字段的 validator 检查在运行时抛出 `KeyError`。

受影响的子任务：5.1.3、5.1.4、5.1.6（metadata emitter — SPEC_INCORRECT）；8.2.3、8.2.4（L1 — SPEC_INCORRECT）；8.3.3、8.3.4、8.3.6（L2 — SPEC_INCORRECT）；8.4.2（L3 — SPEC_INCORRECT）。间接受影响的还有：整个 auto-fix loop（9.3.1）以及 pipeline orchestrator（11.1.1、11.1.2），因为没有一个能正常工作的 validator，它们就无法接线。

#### B. 高层原因

**共享数据契约缺失。** spec 通过单个示例（§2.6 lines 446–478）而不是正式 schema 来定义 metadata。这个示例遗漏了 §2.9 validator 伪代码会读取的字段。这不是规范不完整，而是同一份规范中两个章节彼此冲突。

#### C. 歧义的精确位置

歧义位于 **metadata schema 语义**。具体来说，§2.6 的示例缺少：

- 分类根列所需的 `col["values"]` 和 `col["weights"]` —— L1 边际检查会读取它们（§2.9 line 574–575）
- 结构 measure 所需的 `col["formula"]` 和 `col["noise_sigma"]` —— L2 残差检查会读取它们（§2.9 lines 626、631）
- group dependency 所需的 `dep["conditional_weights"]` —— L2 条件偏差检查会读取它（§2.9 line 636）
- 随机 measure 所需的 `col["param_model"]` —— L2 的 KS 检验需要它（§2.9 lines 615–616，通过 `_get_measure_spec`）
- pattern 所需的 `p["params"]` —— 使用 `z_score`、`break_point`、`magnitude` 的 L3 检查需要它
- 缺少 `schema_version` 字段 —— 没有前向兼容机制
- 缺少 required/optional 区分 —— 无法校验 metadata 本身
- 缺少正式类型 —— 只能通过猜测认为 `cardinality` 是 int、`depends_on` 是 list[str]，但规范并未声明

#### D. 被阻塞的下游实现决策

1. **Metadata builder 的字段清单。** Module 5 的 metadata emitter 不知道 schema 实际要求什么字段，因此无法正确输出字段。3 个 SPEC_INCORRECT 子任务（5.1.3、5.1.4、5.1.6）都需要一个明确字段列表。
2. **Validator 的字段访问模式。** 每个读取超出 §2.6 示例字段的 validator 检查都会触发 `KeyError`。L1 边际检查、所有 L2 检查和 L3 pattern 检查都依赖这些并不存在于示例中的字段。
3. **Phase 3 的消费契约。** Phase 3（QA 生成、图表提取）需要消费 metadata 以重建生成语义。没有 `param_model`、`formula` 或 `effects`，它就无法形成具有统计依据的问题。
4. **Auto-fix loop 的接线。** Auto-fix loop 会调用 validator，而 validator 依赖 metadata。如果 metadata schema 错了，那么验证结果就没有意义，auto-fix 策略也无法被正确定位。

#### E. 仍可进行的部分实现

4 个不存在冲突的 metadata 字段（`dimension_groups`、`orthogonal_groups`、`measure_dag_order`、`total_rows`）已经在 Sprint 5 中完成。Metadata builder 的骨架和 validator framework（`Check`、`ValidationReport`）也已实现。4 个不依赖缺失字段的 L1 检查（行数、基数、orthogonal 卡方检验、DAG 无环性）可以工作。`_max_conditional_deviation` helper 也能独立工作。

#### F. 解锁所需的最小决策

一个决策即可：**正式定义完整的 metadata schema。** 也就是为每个 metadata 区块明确字段名、类型、required/optional 状态以及内部结构。Gap analysis（finding C13）建议使用 Python `TypedDict` 或 `@dataclass`；alignment map 建议增加 `schema_version` 字段。一旦定义完成，全部 9 个 SPEC_INCORRECT 子任务可以同时解锁。

#### G. 证据

- §2.6（spec lines 446–478）：metadata 示例遗漏 `values`、`weights`、`formula`、`noise_sigma`、`conditional_weights`、`param_model`、`params`
- §2.9（spec lines 574–575、626、631、636）：validator 会读取这些缺失字段
- Gap analysis findings C3、C8、C9（三位独立审阅者得出一致结论），以及 C13（审计后的结构性发现）
- Alignment map 的 Blocker 1：统计为 3 个 SPEC_INCORRECT + 6 个下游子任务 = 9 个以上子任务
- Sprint plan 的 Blocked Backlog：上述 9 个子任务均列在 Blocker 1 下

---

### 2.2 Formula DSL Grammar 未指定

#### A. 被阻塞的能力

`add_measure_structural()` 中的 `formula` 参数是一个包含算术表达式的字符串（例如 `"wait_minutes * 12 + severity_surcharge"`）。这个字符串必须在三个不同模块中被解析和求值：SDK 校验（1.5.2）、engine 生成（4.2.5、4.2.8）以及 L2 验证（8.3.5）。当前并不存在这一语言的 grammar。因此，整个 structural-measure pipeline —— 从声明、生成到验证 —— 都无法运行。

受影响的子任务：1.5.2（formula 符号解析）、4.2.5（结构公式求值）、4.2.8（`eval_formula` 安全求值器）、8.3.5（L2 残差计算）。此外，在能够解析 formula 变量之前，DAG 边类型 5（formula-derived edges）也无法加入。

#### B. 高层原因

**表达式语言缺少正式 grammar。** spec 在 §2.1.1 和 §2.3 中给出了 formula 示例，但从未定义这门语言：没有 operator 白名单、没有优先级规则、没有变量解析顺序、没有函数白名单。这是一个抽象层缺失问题 —— formula 字符串被当作定义完备的 DSL 来使用，但 DSL 的定义本身并不存在。

#### C. 歧义的精确位置

歧义位于 **DSL / formula model**。具体未知点包括：

- **Operator 白名单：** 是否允许 `**`（幂）？`/`（除法）？`%`？一元负号？示例里只出现了 `*`、`+`、`-`，但从未说明其他操作符是否有效。
- **函数调用：** formula 是否可以包含 `log()`、`abs()`、`max()`？spec 只展示了算术运算符。
- **优先级：** 是标准数学优先级，还是 Python 风格？（对 `**` 和一元操作符而言二者并不相同。）
- **变量解析顺序：** 如果某个 measure 名称与 effect 名称冲突，哪个优先解析？
- **数字字面量：** 示例中有 `12`、`0.04`、`9`，但 spec 从未明确声明允许使用数字字面量。
- **空白：** `"a*12"` 是否等价于 `"a * 12"`？

#### D. 被阻塞的下游实现决策

1. **Parser 设计。** 在不知道 token 集合的情况下，无法构建 tokenizer 或 AST parser。无论是 regex 方案、AST walker，还是受限的 `eval()` sandbox，其设计都取决于 operator/function 集合。
2. **DAG 边提取。** Formula 符号解析（1.5.2）必须先解析 formula，找出其中引用了哪些 measure 名称，并据此创建 DAG 边。没有 parser，就没有 formula-derived edges，也就无法构建包含边类型 5 的完整 DAG。
3. **安全求值器的安全边界。** `eval_formula`（4.2.8）必须在允许合法 formula 的同时拒绝任意代码。允许哪些构造，本身就定义了安全边界。没有白名单，就没有安全边界。
4. **L2 残差验证。** L2 的结构检查（8.3.5）需要复用 `eval_formula` 计算预测值，因此同样会被 parser 问题阻塞。

#### E. 仍可进行的部分实现

在没有 formula grammar 的情况下，`add_measure_structural()` 的签名、effects 校验、noise 规范存储和 cycle detection 都可以实现（并且已在 Sprints 3–4 中完成）。Formula 字符串本身也可以按原样存储。边类型 1–4 的 DAG 构建已经可行（Sprint 4 的范围说明已明确这一点）。结构噪声采样（4.2.7）和 effect 物化（4.2.6）也独立于 formula。

#### F. 解锁所需的最小决策

定义一个 **operator 白名单 + precedence table + 变量解析规则**。Gap analysis（finding A3）建议最小集合为：`+`、`-`、`*`、`/`、一元 `-`、数字字面量和括号。如果需要函数，也应枚举允许的函数。一页规格就能端到端解锁三个模块中的整个 structural-measure pipeline。

#### G. 证据

- §2.1.1（spec lines 72–81）：给出 formula 示例，但没有 grammar
- §2.3（spec lines 178–182）：结构 measure 描述中引用了 formula
- Gap analysis finding A3（CRITICAL）：明确列出了缺失的 grammar 要素
- Alignment map 的 Blocker 2：跨 3 个模块共 4 个 BLOCKED 子任务
- Sprint plan 的 Sprint 4 范围说明：DAG 构建只做到边类型 1–4，因为 formula edges 被阻塞

---

### 2.3 分布族参数 Schema 缺失

#### A. 被阻塞的能力

SDK、engine 和 validator 都必须知道每个分布族的必需参数 key、合法取值域以及 scipy 映射。spec 只为 `gaussian` 和 `lognormal` 给出了参数示例（`mu`、`sigma`）。对于剩余 6 个族（`gamma`、`beta`、`uniform`、`poisson`、`exponential`、`mixture`），参数 key 均未指定。而 `mixture` 族更是完全没有任何形式的规范。这会阻塞整个随机 measure pipeline。

受影响的子任务：1.4.3（`param_model` 完整校验）、1.4.4（`mixture` 子规范）、1.5.4（按 family 的 noise 校验）、4.2.1（随机参数解析）、4.2.2（分布分发表）、8.3.1（L2 KS 检验）、8.3.2（`iter_predictor_cells`）。

#### B. 高层原因

**参数参考表缺失。** spec 只在 §2.1.1 line 94 中把 8 个 family 名称列成字符串，却只示范了其中两个。这本质上是一个参考表缺失问题 —— 需要有一个从 family 名称映射到（required keys、valid domains、scipy 分布名）的查找表，供三个模块共享。

#### C. 歧义的精确位置

歧义位于 **SDK API 表面** 和 **metadata / schema 语义**，具体包括：

- **各 family 的参数 key：** 例如 `gamma` 应该是 `shape`/`rate`，还是 `alpha`/`beta`，或者 `k`/`theta`？6 个 family 都没有明示 key。
- **参数取值域：** intercept+effects 模型 `θ = β₀ + Σβₘ(Xₘ)` 可能产生负的 `sigma` 值。spec 没有规定 link function，也没有规定 domain clamping（finding A5a）。
- **Scipy 名称映射：** validator 的 KS 检验（§2.9 line 619）会把 `col["family"]` 传给 `scipy.stats.kstest`，但 SDK 名称（如 `"gaussian"`）与 scipy 名称（如 `"norm"`）不匹配。没有映射表。
- **Mixture：** 完全未定义。`param_model` 的 intercept+effects schema 无法表达组件分布、按组件区分的参数和 mixing weights。scipy 也没有通用用户自定义 mixture 的 CDF，因此 L2 KS 检验无法实现（finding A1b）。

#### D. 被阻塞的下游实现决策

1. **SDK 校验逻辑。** `add_measure()`（1.4.3）无法校验某个 family 对应的 `param_model` 是否包含正确的 key。
2. **Engine 采样分发。** engine（4.2.1、4.2.2）必须用正确的 positional arguments 调用 `np.random.default_rng()` 的对应方法。没有 key→argument 映射，分发无法实现。
3. **L2 KS 检验参数化。** validator（8.3.1）必须为每个 predictor cell 构造期望分布参数，再传给 `scipy.stats.kstest`。如果连 family 使用哪些参数都不知道，就无法构造 CDF。
4. **`iter_predictor_cells` 算法。** 该 helper（8.3.2）必须计算 effect predictor 值的笛卡尔积，并为每个 cell 解析对应参数。它同样依赖于参数 key 的定义以及 effects 的组合方式。
5. **Mixture：二选一决策。** 如果保留 `mixture`，就必须设计一个根本不同的 `param_model` schema。如果延期它，则 family 列表应缩减为 7 个。

#### E. 仍可进行的部分实现

对于 `gaussian` 和 `lognormal`，参数 schema 已由示例完整展示（`mu`、`sigma`）。针对这两个 family 的常量参数形式 `add_measure()`（1.4.2）可以工作（Sprint 3 已完成）。`scale` 参数已在 warning 下被存储（假设 A2）。Measure DAG 根注册（1.4.5）与 family 无关，因此可行。所有 effects 结构校验（1.5.3）也与 family 无关。

#### F. 解锁所需的最小决策

**创建一个分布参考表：** 对 8 个 family（或在 `mixture` 延后的情况下对 7 个 family）分别明确：（a）必需的 `param_model` key；（b）每个 key 的合法取值域；（c）对应的 scipy 分布名；（d）从 SDK key 到 scipy positional args 的映射。**同时就 `mixture` 做出决策：** 要么完整定义组件列表 schema，要么将其延期到未来版本。一个参考表即可解锁 3 个模块中的 7 个子任务。

#### G. 证据

- §2.1.1（spec line 94）：列出了 8 个 family 名称，但只展示了 `gaussian`/`lognormal`
- Gap analysis findings A1（CRITICAL：`mixture` 零规范）、A5（CRITICAL：参数 key 缺失）、A5a（取值域校验）、A1b（`mixture` 没有 scipy CDF）
- Alignment map 的 Blocker 3：7 个 BLOCKED 子任务
- Sprint plan 中关于 Blocker 3 的解决文字

---

### 2.4 Pattern 类型的行为三元组未指定

#### A. 被阻塞的能力

6 种 pattern 类型中的 4 种（`ranking_reversal`、`dominance_shift`、`convergence`、`seasonal_anomaly`）在 spec 中只有名称。对每一种来说，都缺失三个紧密耦合的组件：params schema（LLM 声明什么）、注入算法（engine 如何变换 DataFrame）以及 L3 验证检查（validator 如何检测该 pattern）。这三者必须协同设计，因为注入必须产生 validator 能检测到的统计特征，而 params 又必须同时控制注入与验证。

受影响的子任务：1.8.4（4 种类型的参数校验）、4.3.3–4.3.6（4 种类型的注入）、8.4.4–8.4.7（4 种类型的 L3 验证，包括 helpers）。合计 9 个 BLOCKED 子任务。

#### B. 高层原因

**缺少经过协同设计的行为规范。** 每一种 pattern 类型缺的不是 1 个规范点，而是 3 个彼此相互依赖的规范点。Params schema 会约束注入算法，而注入算法又会约束验证检查。只设计其中任意一个，而不同时设计另外两个，都会得到一个无法验证或无法检测的 pattern。这是设计决策缺失，而非文档缺口。

#### C. 歧义的精确位置

歧义同时跨越三个层面：

- **SDK API：** 每种类型的 `params` 必须包含哪些 key？（finding A8）
- **Engine / 执行行为：** 每种注入会对 DataFrame 执行什么样的变换？（finding B6）
- **Validator 行为：** 哪种统计检验用于检测该 pattern？（`convergence`/`seasonal_anomaly` 对应 finding C1，`dominance_shift` 对应 C10）
- 对于 `dominance_shift` 而言，L3 validator 会委托 `_verify_dominance_change()`（§2.9 line 674），但这个函数在 spec 的任何地方都没有定义（finding C10）。

#### D. 被阻塞的下游实现决策

1. **SDK 参数校验。** 在不知道必需 key 的前提下，无法对 4 种类型的 `params` dict 做校验。目前只能把它们作为 opaque dict 存储（任务 1.8.4 已注明这一权宜方案）。
2. **Engine 注入函数。** 不知道具体变换算法，就无法为 4 种类型实现 `_inject_patterns`。
3. **L3 验证检查。** 不知道目标统计特征，就无法为 4 种类型实现检查。
4. **Auto-fix 策略覆盖范围。** `amplify_magnitude` 修复策略是为 outlier/trend pattern 设计的。它是否适用于这 4 种未定义类型，目前未知（finding C4）。
5. **LLM prompt 指导。** §2.5 中的 prompt 软指导无法指导 LLM 如何使用这些 pattern 类型，因为连应传入哪些 params 都没有定义。

#### E. 仍可进行的部分实现

`outlier_entity` 和 `trend_break` 已经被完整定义 —— 二者都有 params schema（见 §2.1.2 示例）、注入语义（可从 L3 验证代码推断）以及 L3 验证伪代码。因此，它们的 SDK 校验（1.8.1–1.8.3、1.8.5）、注入（4.3.1、4.3.2）和 L3 检查（8.4.1、8.4.3）都可以实现，并已被排入 Sprints 4、6 和 7。Pattern 存储基础设施、target expression 处理以及列校验对全部 6 种类型都适用。`inject_pattern` 的分发框架也可以在只有两个 active branch、四个 stub 的前提下搭建完成。

#### F. 解锁所需的最小决策

对于这 4 种类型中的每一种，都要定义：**（a）** 一个 `params` schema（required keys 及其类型、取值域）；**（b）** 一个注入变换（给定 `(pattern_spec, df, rng)` 时保持确定性）；**（c）** 一个 L3 验证检查（包含通过/失败阈值）。这些必须作为协同设计的三元组一起指定，而不是分别独立定义。Gap analysis 建议为每种类型都提供 worked example。

#### G. 证据

- §2.1.2（spec lines 127–129）：列出了 6 种 pattern 类型名称；只有 2 种有示例
- §2.9 L3（spec lines 647–676）：为 outlier、ranking_reversal、trend_break、dominance_shift 给出了验证伪代码；但 `ranking_reversal` 会硬编码第一个 group（C11），`dominance_shift` 委托给未定义函数（C10），而 `convergence`/`seasonal_anomaly` 则完全没有分支（C1）
- Gap analysis findings A8、B6、C1、C10（三位审阅者从不同角度得出了收敛结论）
- Alignment map 的 Blocker 4：跨 3 个模块共 9 个 BLOCKED 子任务

---

### 2.5 后处理不变量契约缺失（L2/Pattern/Realism 矛盾）

#### A. 被阻塞的能力

§2.8 中的 engine pipeline 包含 4 个顺序阶段：α（skeleton）、β（measures）、γ（pattern injection）、δ（realism injection）。§2.9 中的 validator 运行在最终输出上。这会带来两个结构性矛盾：

1. **L2 vs. Pattern Injection（B2）：** L2 用声明参数校验随机分布。Pattern injection（γ）会故意扭曲分布。因此，L2 会在每一个被 pattern 命中的列上失败。
2. **L1 vs. Realism（C6）：** L1 断言 measure 必须满足 `notna().all()`。Realism injection（δ）会按 `missing_rate` 引入 NaN。只要 realism 开启，L1 就一定失败。

此外，auto-fix 伪代码本身还包含内部矛盾（B3、B7）：修复策略会修改参数（lines 695–698），但下一轮迭代又调用 `build_fn(seed=42+attempt)`（line 691），这会从头重新执行原始 LLM 脚本，从而丢弃所有修复。

直接受影响：9.3.1（SPEC_INCORRECT —— 重试循环伪代码）。间接受劣化：8.3.1（L2 KS 检验）、9.2.1–9.2.3（修复策略无法做集成测试）、4.3.1–4.3.2（pattern injection 与 L2 相互作用）、11.1.1–11.1.2（编排器会组合两个有问题的循环）。

#### B. 高层原因

**后处理阶段缺少执行模型契约。** spec 定义了 4 个 engine 阶段和一个后置 validator，但从未说明每一层验证应该应用于哪个阶段的输出。每个阶段都会以可能破坏前序不变量的方式变换数据。如果没有一个契约明确规定“L2 在 Phase β 输出上运行；L3 在 Phase γ 输出上运行；当 Phase δ 开启时 L1 要调整阈值”，那么整个验证系统在内部就是不一致的。

Auto-fix 的矛盾则是另一个会叠加影响的问题：**缺少 mutation model。** 伪代码先应用修复，又立刻丢弃修复，这不是一种设计选择，而是伪代码自身的逻辑错误。

#### C. 歧义的精确位置

歧义横跨多个层面：

- **执行行为（§2.8）：** engine 各阶段之间的不变量契约是什么？Phase β 中建立的哪些性质会被 Phases γ 和 δ 保留？
- **Validator 行为（§2.9）：** L2 运行在注入前数据还是注入后数据上？L1 是否会对 realism 引入的 NaN 做调整？
- **Auto-fix 的 mutation 语义（§2.9）：** 修复策略是修改 simulator 实例（可跨重试持久化）、修改生成后的 DataFrame（每次重生成后重新应用），还是修改 SDK 脚本源码？伪代码没有以一致方式支持任何一种。
- **异常 / 重试语义：** §2.7/§2.9 的循环组合虽然可以从上下文推断出来（顺序式，见 §2.7 step 3），但从未被正式定义。总预算（3+3=6）和 no-escalation 规则都只是推断，而非 spec 明文。

#### D. 被阻塞的下游实现决策

1. **Validator 编排器设计。** `validate(df, meta)` 编排器（8.1.3，已从 Sprint 6 延后）在不知道 L2 应该拿注入前还是注入后数据的情况下无法实现。这不是代码问题，而是语义问题。
2. **Auto-fix 重试循环实现。** 重试循环（9.3.1）无法按 spec 原样实现，因为伪代码自相矛盾。实现者必须自行选择一个 spec 没有提供的 mutation model。
3. **修复策略作用域。** `widen_variance`（针对 KS 失败）与 `amplify_magnitude`（针对 pattern 失败）可能会在同一列上彼此对抗。如果不知道 L2 是否排除 pattern-target 行，那么修复策略的作用域就是未定义的。
4. **Pipeline orchestrator。** 编排器（11.1.1）会组合两个循环。如果内部循环（§2.9）有问题，编排器也必然有问题。

#### E. 仍可进行的部分实现

单个修复策略可以先作为独立 stub 构建并做单元测试（Sprint 7 已这样做）。`match_strategy` 的 glob 分发器已经可用。Validator framework、L1 检查（除有限性外）以及 outlier/trend 的 L3 检查都可以工作。§2.7 的执行错误循环独立于这一 blocker，因此可以完整实现。至于顺序式组合假设（先 §2.7，后 §2.9，而非嵌套），也受到 §2.7 step 3 语义的较强支持，因此可以编码。

#### F. 解锁所需的最小决策

需要三个决策：

1. **后处理不变量契约：** 明确每一层验证运行在哪个阶段输出上。最干净的方案（依据 gap analysis 的 B2 建议）是：L2 在 Phase β 输出上运行（注入前），L3 在 Phase γ 输出上运行（注入后），而当 Phase δ（realism）激活时，L1 需要调整有限性阈值。这样可同时解决 B2、C6 以及 L2/L3 振荡。
2. **Auto-fix mutation model：** 明确修复目标。唯一一致的方案（依据 gap analysis 的 B3、B7）是：修复策略直接修改 `FactTableSimulator` 实例中的声明，而重试循环直接调用 `sim.generate()`，而不是 `build_fn`。这要求循环持有可变 simulator 的引用，而不是脚本。
3. **Soft-fail 策略：** 明确 auto-fix 重试耗尽后应如何处理。Phase 3 是否接收失败数据？是否存在质量阈值？（finding C12）

#### G. 证据

- §2.9（spec lines 574–575 vs. 582–584）：L1 有限性检查与 realism NaN 注入相冲突
- §2.9（spec lines 613–621）：L2 KS 检验运行在注入后数据上
- §2.8（spec line 530）：Pattern injection 会在验证前修改数据
- §2.9（spec lines 691–698）：先应用修复策略，再因 `build_fn` 重新执行而丢弃修复
- Gap analysis findings B2（CRITICAL）、B3（CRITICAL）、B7（MODERATE）、C5（MODERATE）、C6（MODERATE）
- Alignment map 的 Blocker 5：直接影响 1 个 SPEC_INCORRECT 子任务，间接劣化 8 个以上
- Sprint plan：9.2.1–9.2.3 被标记为 “isolated stubs”；9.3.1 位于 Blocked Backlog

---

### 2.6 Phase 1 → Phase 2 的类型化接口契约缺失

#### A. 被阻塞的能力

Phase 2 pipeline 从 Phase 1 接收场景上下文，并将其注入 LLM prompt（§2.5 中的 `{scenario_context}` 占位符）。当前工作系统已经能通过 `json.dumps(scenario, indent=2)` 传入这一 JSON blob。真正缺失的是一个 **带类型、可校验、可版本化的契约**，用于定义这一接口的 required 字段、optional 字段、类型以及序列化格式。

受影响的子任务：10.1.2（场景上下文注入 — BLOCKED）、11.1.1（pipeline orchestrator —— 同时还受 C5 阻塞）。

#### B. 高层原因

**跨 Phase 的类型化契约缺失。** 场景上下文是一个跨边界数据结构，由 Phase 1 生成、由 Phase 2 消费。它已经有一个事实上的 schema（由 Phase 1 中的 `ScenarioContextualizer.validate_output()` 强制执行，它会检查 `scenario_title`、`data_context`、`key_entities`、`key_metrics`、`temporal_granularity`、`target_rows`），但没有正式的类型定义。

**对 Stage 1 的修正：** Stage 1 当前状态图正确指出（§2J、§2K）“一个可工作的 JSON 注入路径已经存在”。Alignment map v3 也明确降低了这一 blocker 的严重级别。这个 blocker 关乎的是 **形式化**，而不是基础能力。它的严重性低于 metadata schema（Blocker 2.1）、formula DSL（Blocker 2.2）或 distribution families（Blocker 2.3）。

#### C. 歧义的精确位置

歧义位于 **SDK API / 跨 Phase 契约语义**：

- 哪些字段是 required，哪些是 optional？
- 各字段的类型是什么？（例如 `target_rows`：是 int，还是 string？能否为 null？）
- 如果 Phase 1 生成了 Phase 2 未预期的额外字段，会发生什么？
- 是否存在用于前向兼容的版本字段？
- `ScenarioContext` 应该建模为正式 Python dataclass、JSON Schema，还是 TypedDict？

#### D. 被阻塞的下游实现决策

1. **类型化场景上下文注入。** Prompt 模板构建器（10.1.2）可以直接从原始 dict 渲染 `{scenario_context}`，但没有 schema 就无法保证完整性或类型安全。
2. **Pipeline orchestrator 的入口。** 编排器（11.1.1）会接受 Phase 1 的 scenario 并继续透传。没有类型契约，针对 malformed scenario 的错误处理就只能是临时性的。
3. **集成测试。** 端到端测试需要 fixture scenario。没有正式 schema，fixture 就只能是对 one-shot 示例的复制，而不是一个已校验契约。

#### E. 仍可进行的部分实现

现有的 `json.dumps(scenario)` 注入路径对 one-shot 示例以及任何符合事实字段集合的 scenario 都有效。Prompt 模板（10.1.1）可以实现。代码提取与校验（10.2.1、10.2.2）也可实现。`LLMClient.generate_code()` 的集成验证同样可行。真正被阻塞的只有形式化子任务（10.1.2）和下游编排器。

#### F. 解锁所需的最小决策

将 `ScenarioContext` 定义为一个类型化 dataclass（或 Pydantic model），其中包含 required 字段（`scenario_title: str`、`target_rows: int`、`key_entities: list[dict]`、`key_metrics: list[dict]`、`temporal_granularity: dict`）、optional 字段以及校验方法。Alignment map v4 指出，`audit/5_agpds_pipeline_runner_redesign.md` 中已经包含可直接借用的 `ScenarioContext` / `result_models.py` 设计。

#### G. 证据

- §2.5（spec lines 387–389）：`{scenario_context}` 占位符没有 schema
- Gap analysis finding D1（审计后从 CRITICAL 降为 high-MODERATE）
- Alignment map 的 Blocker 6：2 个 BLOCKED 子任务，且在 v3 中已被弱化
- Sprint plan 中 Blocker 6 的解决说明，其中提到了现有 `ScenarioContextualizer.validate_output()`

---

### 2.7 跨组默认语义未定义

#### A. 被阻塞的能力

当两个 dimension group 既没有 `declare_orthogonal()`，也没有 `add_group_dependency()` 声明时，spec 没有定义它们的根列应如何采样。§2.2 表示跨组独立性是 “opt-in, not default”，却从未说明真正的默认行为。对于 N 个 dimension group，会存在 O(N²) 对组合，而其中大多数不会有显式声明。

这一问题并未在 alignment map 或 sprint plan 中被列为编号 blocker，但它在审计后的 gap analysis 中被标记为一个 CRITICAL finding（A12），并会影响子任务 4.1.1（采样独立分类根 —— 当前以假设独立采样的形式标记为 NEEDS_CLARIFICATION）。

#### B. 高层原因

**概念模型决策缺失。** spec 定义了两种显式模式（orthogonal、dependent），却没有定义默认模式。这是一个产品语义问题：系统是否应该要求穷举所有 pairwise 声明（从而拒绝不完整场景）？是否应把独立性当作默认值（这又与 “opt-in” 表述冲突）？还是应该把未声明 pair 视为 “unknown” 并提供某种 fallback？

#### C. 歧义的精确位置

歧义位于 **概念模型**（§2.2），并向 **执行行为**（§2.4 skeleton builder）传播：

- §2.2（spec line 153）：“Cross-group independence is opt-in, not default”
- §2.1.2 的 prompt hard constraint 4：“at least 1 `declare_orthogonal()`” —— 但没有要求穷举所有 pairwise 声明
- 完全没有定义 undeclared 情况下的行为

#### D. 被阻塞的下游实现决策

1. **Skeleton builder 的采样逻辑。** Skeleton builder（4.1.1）必须决定 undeclared pair 应按独立、联合还是直接拒绝来处理。当前采用的独立采样假设与 “opt-in, not default” 表述相冲突。
2. **Validator 的 orthogonal 检查范围。** L1 的卡方检验（8.2.5）目前只检查显式声明为 orthogonal 的 pair。对于 undeclared pair，是否也应检验独立性？还是应该检验非独立性？
3. **LLM prompt 设计。** Prompt 是否应要求 LLM 声明所有 pair，还是允许部分声明？

#### E. 仍可进行的部分实现

当前采用的假设（undeclared = independent）足以让 Sprint 5 继续推进。这个假设已经被记录下来。如果未来决策变化，代码仍然可以重构，因为相关采样逻辑集中在一个单独方法里。

#### F. 解锁所需的最小决策

只需要一个决策：**定义 undeclared pair 的默认跨组行为。** 可选方案包括：（a）默认独立（最简单，但与 “opt-in” 表述冲突）；（b）要求 LLM 声明所有 pair（最干净，但约束最强）；（c）默认 “弱依赖”，附带一个小相关参数（复杂，而且缺乏动机）。

#### G. 证据

- §2.2（spec line 153）：出现 “opt-in, not default” 表述
- Gap analysis finding A12（CRITICAL，审计后提出）
- Alignment map 4.1.1：记录为 NEEDS_CLARIFICATION，并附带该假设

---

### 2.8 删失 Schema 未定义

#### A. 被阻塞的能力

`set_realism()` 中的 `censoring` 参数出现在方法签名中，也出现在 engine pipeline（Phase δ）中，但没有类型注解、schema 或语义定义。是左删失还是右删失？按列阈值吗？是否需要额外的 indicator 列？都没有说明。

受影响的子任务：4.4.3（删失注入 —— BLOCKED）。

#### B. 高层原因

**参数语义缺失。** 这是最简单的 blocker —— 只是一个没有定义的 API 参数。它仅局限于 realism injection 模块，并且还是可选的（默认值为 `censoring=None`）。

#### C. 歧义的精确位置

歧义位于 **SDK API**（§2.1.2 中 `set_realism` 的签名）以及 **metadata / schema 语义**（删失会改变 measure 的分布形状，并与 L2 KS 检验和 L1 有限性检查产生交互，但 validator 层面并没有给出相应调整）。

#### D. 被阻塞的下游实现决策

1. **删失注入逻辑。** 在不知道 “删失” 的具体含义之前，无法实现 `_inject_realism` 中的删失处理。
2. **Metadata 表达。** Metadata 没有字段用于记录删失配置，因而 Phase 3 无法消费它。
3. **Validator 调整。** 对被删失列而言，L2 KS 检验会失败，因为经验分布已不再与声明的 family 一致。

#### E. 仍可进行的部分实现

缺失值注入（4.4.1）和脏值注入（4.4.2）都可实现，并已排入 Sprint 6。`set_realism()` 的签名会把 `censoring` 作为 opaque dict 存储（Sprint 4 已完成）。默认路径 `censoring=None` 也可正常工作。

#### F. 解锁所需的最小决策

定义删失 dict 的 schema：目标列、方向（left/right/interval）、阈值，以及是否会额外加入删失 indicator 列。

#### G. 证据

- §2.1.2（spec line 129）：签名里有 `censoring`，但没有定义
- Gap analysis finding A4（MODERATE，且在审计后扩展到 metadata 与 validation 的交叉影响）
- Alignment map 的 Blocker 7：1 个 BLOCKED 子任务

---

## 3. Blocker 依赖图

这些 blocker 具有严格的依赖结构。有些是根因，有些则是下游症状或复合效应。

```
ROOT CAUSES (independent, can be resolved in parallel):
┌─────────────────────────────────┐  ┌──────────────────────────┐  ┌───────────────────────────────┐
│ 2.1 Metadata Schema Contract    │  │ 2.2 Formula DSL Grammar  │  │ 2.3 Distribution Family Params│
│ [9+ subtasks, highest leverage] │  │ [4 subtasks, structural] │  │ [7 subtasks, stochastic]      │
└──────────────┬──────────────────┘  └────────────┬─────────────┘  └──────────────┬────────────────┘
               │                                  │                               │
               │                                  │                               │
               ▼                                  ▼                               ▼
         ┌─────────────────────────────────────────────────────────────────────────────┐
         │                    Validator L2 is fully blocked                            │
         │   (needs metadata fields + formula evaluator + distribution params)         │
         └─────────────────────────────────┬───────────────────────────────────────────┘
                                           │
COMPOUND BLOCKER (depends on 2.1 + 2.4):   │
┌───────────────────────────────────┐      │
│ 2.4 Pattern Type Triples          │      │
│ [9 subtasks, co-design needed]    │──────┤
└──────────────┬────────────────────┘      │
               │                           │
               ▼                           ▼
         ┌─────────────────────────────────────────────────────────────────────────────┐
         │ 2.5 Post-Processing Invariant Contract (L2/Pattern/AutoFix contradiction)  │
         │ Depends on: metadata (2.1) to know what to validate                        │
         │             pattern triples (2.4) to know what distortions L2 must tolerate │
         │ [1 SPEC_INCORRECT direct, 8+ degraded]                                     │
         └─────────────────────────────────┬───────────────────────────────────────────┘
                                           │
INTERFACE BLOCKER (independent):           │
┌───────────────────────────────────┐      │
│ 2.6 Phase 1 Contract              │      │
│ [2 subtasks, formalization only]  │──────┤
└───────────────────────────────────┘      │
                                           ▼
                                    ┌──────────────────────────┐
                                    │ Pipeline Orchestrator     │
                                    │ 11.1.1, 11.1.2 (BLOCKED)│
                                    │ Terminal dependency —     │
                                    │ needs ALL upstream        │
                                    └──────────────────────────┘

ISOLATED BLOCKERS (can be resolved at any time):
┌───────────────────────────────────┐  ┌────────────────────────────────┐
│ 2.7 Cross-Group Default Semantics │  │ 2.8 Censoring Schema           │
│ [0 hard-blocked, 1 assumption]    │  │ [1 subtask, optional feature]  │
└───────────────────────────────────┘  └────────────────────────────────┘
```

**关键结构性洞察：** 2.1、2.2 和 2.3 这三个 blocker 是彼此独立的根因，因此可以并行解决。三者合起来可以立刻解锁大约 20 个子任务。2.4 具有半独立性（其 params schema 不依赖上游，但其 L3 验证检验需要来自 2.1 的 metadata schema）。2.5 则最下游 —— 它是 2.1（metadata 契约）+ 2.4（pattern 设计）+ 自身伪代码矛盾的复合问题。2.6 独立但杠杆较低（只影响 2 个子任务，且已有现有基础设施缓解）。2.7 和 2.8 则是孤立、低影响的问题。

**Pipeline orchestrator（11.1.1、11.1.2）是终端依赖。** 在所有上游 blocker 解决前，它都无法接线。这本身不是一个 “blocker”，而是架构深层依赖链的结果。

---

## 4. 根因总结

这 8 个 blocker 最终可以归约为 5 类根因。

### 类别 1：共享数据契约缺失

**Why it matters：** 当多个子系统（engine、validator、metadata builder、auto-fix、Phase 3）必须对同一个数据结构达成一致时，这个结构就必须被正式定义一次。spec 却是通过示例，甚至完全不定义，来给出这些结构，导致每个消费者都只能反向推断期望格式。

**What it blocks：** Blocker 2.1（metadata schema）、Blocker 2.3（distribution params），以及部分 Blocker 2.6（Phase 1 接口）。这是三个杠杆最高的 blocker，总共涉及 18 个以上子任务。

**How serious：** **Critical。** 这是头号根因。仅 metadata schema 就是整个系统中连接度最高的契约 —— 每个 validator 检查、每个 auto-fix 策略以及 Phase 3 的消费都依赖它。解决 metadata schema 可立刻解锁 9 个子任务；解决分布参考表还能再解锁 7 个。这两者具有乘数效应，因为它们共同流向同一批下游系统（validator、engine、auto-fix）。

### 类别 2：表达式语言缺少正式 Grammar

**Why it matters：** Formula DSL 在三个模块中被使用（SDK 校验、engine 生成、L2 验证），却只以示例字符串形式存在。任何会解析或执行不受信任字符串表达式的系统，都必须有正式 grammar —— 这不仅仅是便利性问题，更是安全边界问题。

**What it blocks：** Blocker 2.2（formula DSL）。跨 3 个模块的 4 个子任务，以及 DAG 边类型 5。

**How serious：** **Critical，但范围较窄。** 它的影响高度集中在 structural-measure pipeline 上。解决后可解锁 4 个子任务并补齐 DAG 构建。修复本身也很集中 —— 一页 operator/precedence 规格即可。

### 类别 3：缺少协同设计的行为三元组

**Why it matters：** 有些功能必须同时指定（输入 schema、变换算法、验证检查），因为这三者彼此紧密耦合。只定义其中之一而不定义另外两个，就会得到一个内部不一致的系统。4 种未定义的 pattern 类型，以及 9 种失败模式中有 5 种没有 auto-fix 策略，都属于这一类。

**What it blocks：** Blocker 2.4（pattern types）。跨 3 个模块的 9 个子任务。此外，auto-fix 策略覆盖不足（finding C4）意味着 5 种以上失败模式没有恢复路径。

**How serious：** **对功能完整性是 Critical，但对架构本身不是。** 已定义的两种 pattern 类型（`outlier_entity`、`trend_break`）已经可以端到端工作。系统可以先以 6 种中的 2 种模式上线，再在未来补充其余类型。但缺失的那些类型不能被“顺手增量补上” —— 每一种都需要 SDK、engine 和 validator 的协同设计。

### 类别 4：执行模型语义自相矛盾

**Why it matters：** 如果 spec 提供的伪代码本身互相冲突（auto-fix 先应用修复再丢弃修复），或者包含按设计永远会失败的检查（L1 finite vs. realism NaN；L2 KS vs. pattern injection），那么实现者就只能二选一：要么照着伪代码做，得到一个错误系统；要么偏离 spec，得到一个正确但不符合原文的系统。

**What it blocks：** Blocker 2.5（后处理不变量契约）。直接影响 1 个 SPEC_INCORRECT 子任务，并间接劣化 8 个以上任务。Auto-fix 重试循环是受影响的核心组件。

**How serious：** **对系统稳定性是 Critical。** 没有后处理不变量契约，验证和 auto-fix 系统就会出现振荡（L2 修复与 L3 修复互相打架），或者根本无效（修复在重生成时被丢弃）。这是唯一一个 spec 提供的是 *错误指导* 而不是 *缺少指导* 的根因，因此可能更危险 —— 如果实现者严格按伪代码来实现，就会构建出一个无法收敛的系统。

### 类别 5：概念模型决策缺失

**Why it matters：** 有些 blocker 与其说是实现细节问题，不如说是产品语义选择没有被做出 —— 跨组默认行为是什么？删失到底是什么意思？这些都位于代码实现之前。

**What it blocks：** Blocker 2.7（跨组默认值）、Blocker 2.8（删失）。合计：1 个硬阻塞子任务 + 1 个依赖假设的子任务。

**How serious：** **Low。** 二者都很孤立。跨组默认值已有一个可工作的假设（独立采样）。删失也是可选特性（默认 `censoring=None`）。它们都不阻塞关键路径。但跨组默认值是一个概念层地雷 —— §2.2 中 “opt-in, not default” 的表述与唯一可工作的假设（将 undeclared pair 视为独立）相冲突，如果未来否定这一假设，就会造成语义漂移。
