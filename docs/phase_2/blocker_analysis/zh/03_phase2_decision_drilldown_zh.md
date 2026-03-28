# Phase 2 决策深挖

**生成自：** `phase_2.md`（规格）、`1_phase2_implementation_task_hierarchy.md`（任务层级 v2）、`2_phase2_gap_analysis.md`（差距分析 v2）、`3_phase2_implementation_alignment_map.md`（对齐映射 v4）、`4_phase2_sprint_plan.md`（冲刺计划 v4）、`01_phase2_current_state_map.md`（Stage 1 输出）、`02_phase2_blocker_decomposition.md`（Stage 2 输出）

**方法：** 按 blocker 逐项进行决策深挖。每个 blocker 都从系统级原因 → 抽象级缺口 → 架构级后果 → 仍然不安全或未定义的具体实现决策进行追踪。源文档具有最高权威性；Stage 2 的结论被用作起始上下文，但凡与源证据不一致之处，均以源证据为准并加以修正。

---

## 1. 总体诊断

### 1.1 Phase 2 的 blocker 揭示了什么

Phase 2 规格描述的是一个包含 **五个彼此不同的执行关注点** 的系统，即声明、生成、元数据发出、验证与自动修复。这五者必须共享形式化契约，才能正确组合。规格通过散文说明、伪代码示例和一个 one-shot 场景来定义这些关注点，但**从未形式化定义将它们绑定在一起的共享数据结构**。结果是：每个关注点单独来看都自洽，但它们组合起来时却没有定义。

这不是缺少功能，也不是 API 设计不完整的问题。这是**缺少中间抽象**的问题，也就是“产品做什么”和“代码必须长什么样”之间缺了一层。规格从产品级概念（例如“验证器检查统计正确性”）直接跳到伪代码（例如 `scipy.stats.kstest(data, family, params)`），却从未正式定义两端共同依赖的共享数据模型（例如 `family` 在 scipy 中映射到什么、每个 family 对应哪些 `params`、哪些元数据字段把这些参数传给验证器）。

### 1.2 哪些缺失决策是基础性的

有三个决策位于依赖图的根部。一旦解决，它们将立即解锁约 34 个受阻子任务中的 20 个：

1. **元数据 schema**（Blocker 1）: 它是系统中每个生产者与消费者之间唯一的共享契约。每一项验证器检查、每一种 auto-fix 策略，以及 Phase 3 的消费逻辑，都依赖于规格 §2.6 示例未发出的元数据字段。这是杠杆效应最大的单一决策。

2. **分布 family 参考表**（Blocker 3）: 它是 SDK、引擎的采样分发逻辑以及验证器 KS 检验构造之间的参数契约。没有它，整个随机型 measure pipeline 都无法运行。

3. **公式 DSL 语法**（Blocker 2）: 它是 SDK 的符号解析器、引擎的安全求值器以及验证器残差计算之间的表达式语言契约。没有它，整个结构型 measure pipeline 都无法运行。

这三项彼此独立，可以并行解决。

### 1.3 哪些缺失决策是次级的

剩余决策要么依赖上述三项基础决策，要么彼此隔离：

- **Pattern type 行为三元组**（Blocker 4）: 部分依赖元数据 schema（以便 L3 验证访问 pattern 元数据），属于一个需要共同设计 params、注入和验证的设计任务。
- **后处理不变量契约**（Blocker 5）: 同时依赖元数据 schema 与 pattern type 的解析；它还包含 auto-fix 变异模型问题，这更像是规格内部的矛盾，而不是缺失契约。
- **Phase 1 接口契约**（Blocker 6）: 相对独立，但杠杆效应较低；现有 JSON 注入路径已在一定程度上缓解该问题。
- **跨组默认语义**（Blocker 7）与 **censoring schema**（Blocker 8）: 相互独立、影响较低，可机会式解决。

### 1.4 对前一阶段分析的修正

Stage 2 的 blocker 分解正确识别了三类根因：缺失契约、缺失行为三元组、以及组合行为存在矛盾，并正确建立了依赖顺序。但它把元数据 schema、公式 DSL 和分布 family 三个 blocker 都归为“缺失共享数据契约”的实例。本次深挖进一步细化这一框架：这三个 blocker 实际上源于**三种不同的缺失抽象**，分别是实体模型、表达式模型和参数模型，它们各自带来的架构后果也不同。把它们混在一起，会掩盖这样一个事实：元数据 schema 问题本质上是**声明模型 / 实体模型**的缺口，公式 DSL 问题是**表达式模型**的缺口，而分布 family 问题是**参数分发模型**的缺口。每一个都需要不同类型的设计工作。

---

## 2. 按 Blocker 深挖

### 2.1 Schema 元数据契约（Findings C3, C8, C9, C13, C3a, A2a）

#### A. 系统级原因

Phase 2 系统是一个**生产者-消费者 pipeline**：引擎生成 `(DataFrame, metadata)` 元组，而验证器、auto-fix 循环和 Phase 3 都消费元数据，以理解 DataFrame 的结构。元数据是向下游传达生成语义的**唯一**通道。规格把元数据视为一种输出格式（§2.6），而不是契约。它提供的是一个 JSON 示例，而不是 schema 定义；而且该示例与验证器伪代码是彼此独立编写的。结果是，同一系统的两半对绑定它们的数据结构有不同理解。

这里缺失的核心心智模型是：**元数据不是“可有可无的输出”，而是对“实际生成了什么”的形式化说明，下游消费者必须据此进行验证。** 如果元数据不完整，每个消费者就都得从 DataFrame 本身逆向推导生成语义，这与确定性声明式 pipeline 的目标相违背。

#### B. 抽象级缺口

**实体模型 / 声明模型。** 元数据 schema 是内部声明模型的序列化形式。规格通过 SDK API 定义内部模型（即 `add_category`、`add_measure` 等存储什么），并展示了一个局部序列化形式（§2.6 示例），但从未定义内部状态与序列化后元数据之间的完整映射。这意味着实体模型，即“什么字段描述一个分类列？一个随机型 measure？一个结构型 measure？一个 group dependency？一个 pattern？”只是在零散的 API 签名之间被隐式表达，却从未被统一为单一的类型化 schema。

更准确地说，缺口位于**元数据模型**，也就是对 metadata dict 内容的正式定义：逐字段列出类型、必填 / 选填属性，以及各字段的语义含义。由于缺少这层模型，验证器、auto-fix 循环与 Phase 3 都无法针对稳定接口进行编码。

#### C. 架构级后果

元数据 schema 的缺口让三组组件之间的边界变得模糊：

1. **引擎 → 验证器：** 验证器伪代码（§2.9）会读取 `col["values"]`、`col["weights"]`、`col["formula"]`、`col["noise_sigma"]`、`col["param_model"]`、`dep["conditional_weights"]`、`p["params"]`，但这些字段都没有出现在 §2.6 的元数据示例中。引擎没有发出消费者读取的内容，因此从引擎到验证器的数据流是断裂的。

2. **引擎 → Phase 3：** Phase 3 消费元数据，以重建生成语义，从而支持 QA 与图表提取。若元数据中没有 `param_model`、`formula` 或 `effects`，Phase 3 就无法构造具有统计依据的问题。Phase 2 → Phase 3 的边界因此未定义。

3. **验证器 → Auto-Fix 循环：** Auto-fix 循环根据失败的 `Check` 分发修复策略。诸如 `widen_variance` 之类的修复策略需要访问 measure 的参数规格，才知道应该放大什么。如果元数据不携带 `param_model`，修复策略就没有可变异的目标，只能直接探入 simulator 的内部状态。这会让 auto-fix 循环与 simulator 的私有 API 紧耦合。

此外，缺少 `schema_version` 字段意味着系统没有前向兼容机制。一旦新增字段（为解决 C3/C8/C9 等问题这是必然的），现有消费者将无法检测这种变化。

#### D. 被阻塞的实现级决策

1. **元数据构建器字段列表（Module 5，子任务 5.1.3、5.1.4、5.1.6）:** `_build_schema_metadata()` 方法在不知道需要发出哪些字段之前无法完成。这三个 `SPEC_INCORRECT` 子任务都需要针对每种列类型给出明确、带类型的字段规格。

2. **将元数据 schema 表达为 Python 类型：** 元数据应该是 `TypedDict`、`@dataclass`、Pydantic `BaseModel`，还是由 JSON Schema 校验的普通 `dict`？这会影响序列化格式、边界校验方式，以及消费者能否获得 IDE 自动补全和类型检查。

3. **逐列元数据结构：** 一个分类列条目应包含哪些 key？（示例里有 `name`、`group`、`parent`、`type`、`cardinality`；而验证器需要 `values`、`weights`，但示例缺失。）一个随机型 measure 条目应包含哪些 key？（示例里有 `name`、`type`、`measure_type`、`family`；但所需的 `param_model`、`scale` 缺失。）一个结构型 measure 条目应包含哪些 key？（示例里有 `name`、`depends_on`；但所需的 `formula`、`effects`、`noise_sigma` 缺失。）

4. **Group dependency 元数据结构：** §2.6 示例中只有 `{"child_root", "on"}`，但验证器读取的是 `dep["conditional_weights"]`。是否必须添加该字段？它的精确结构是什么，是否应与 `GroupDependency` dataclass 匹配？

5. **Pattern 元数据结构：** §2.6 示例中只有 `{"type", "target", "col"}`，但验证器会读取 `p["params"]["z_score"]`、`p["params"]["break_point"]` 等。是否必须序列化完整 `params` dict？

6. **验证器字段访问模式：** 每个从元数据读取内容的验证器子任务（8.2.3、8.2.4、8.3.1、8.3.3、8.3.4、8.3.6、8.4.x）都必须知道精确的字段名与类型。没有 schema，每一次字段访问都可能触发 `KeyError`。

7. **Schema 版本化：** 是否应存在 `"schema_version": "2.0"` 字段？验证器收到旧版本元数据时应如何处理？

#### E. 可行的解释 / 决策选项

**Option 1: 扩展 §2.6 示例，使其包含验证器所需的全部字段。** 将元数据定义为带文档字段表的普通 `dict`。这是最小改动，能保留现有架构，并解锁全部 9 个以上子任务。风险在于，长期缺少机器可读 schema 时，schema 漂移仍会发生。

**Option 2: 将元数据定义为带类型的 Python 模型（dataclass 或 Pydantic）。** 创建 `SchemaMetadata` 类，并为每个部分构建嵌套模型（`DimensionGroupMeta`、`ColumnMeta`、`PatternMeta` 等）。这可提供编译期类型检查、IDE 支持和自动校验。代价是更高的前期设计成本，以及元数据模型与 Python 实现之间的耦合。

**Option 3: 先定义一个 JSON Schema 文档，再从中自动生成 Python 模型。** 这既提供语言无关的 schema（适用于可能不是 Python 的 Phase 3），也提供 Python 类型模型。前期成本最高，但长期稳定性最好。

这三种选项都要求完成同一项核心工作：列出每个字段、字段类型以及其必填 / 选填属性。差别仅在实现载体。

#### F. 建议的澄清优先级

**首先决定：** 完整的逐字段元数据规格，也就是各列类型、group dependency 与 pattern 分别拥有哪些字段、字段类型是什么、哪些必填、哪些选填。这是整个 blocker 集合中杠杆效应最高的单项决策。它将直接解锁 9 个 `SPEC_INCORRECT` 子任务，并间接启用 auto-fix 循环与 pipeline orchestrator。

**第二决定：** 表示形式（带文档 schema 的普通 dict，还是带类型的 Python 模型）。这可以并行决定，但紧急性较低。只要有字段表，普通 dict 已足以推进实现；类型模型则是更优的工程化方案，但不是前置条件。

**可以延后：** Schema 版本化。这对 Phase 3 集成重要，但不是 Phase 2 实现的先决条件。

**为什么按这个顺序：** 下游每个模块都会消费元数据。在元数据 schema 被定义之前，验证器对每个 metadata 未发出的字段都会报 `KeyError`，而 auto-fix 循环也没有可传给验证器的元数据。字段规格是那个可以“一次性解锁一切”的最小工作单元。

#### G. 证据

- §2.6（规格）：带 7 个顶层 key 的元数据示例，但逐列条目中缺失 `values`、`weights`、`param_model`、`formula`、`effects`、`noise_sigma`
- §2.9（规格）：验证器伪代码读取 `col["values"]`（第 574 行）、`col["weights"]`（第 575 行）、`col["formula"]`（第 626 行）、`col["noise_sigma"]`（第 631 行）、`dep["conditional_weights"]`（第 636 行）、`spec.iter_predictor_cells()`（第 616 行）
- 差距分析 findings C3（三位评审）、C8、C9、C13（审计后结构问题）、C3a、A2a
- 对齐映射 Blocker 1：3 个 `SPEC_INCORRECT` + 6 个下游任务 = 9 个以上子任务
- 任务层级 5.1.3、5.1.4、5.1.6：元数据发出相关的 `SPEC_INCORRECT` 子任务

---

### 2.2 公式 DSL 语法（Finding A3）

#### A. 系统级原因

结构型 measure 子系统建立在这样一种思路上：派生 measure 由字符串公式定义（例如 `"wait_minutes * 12 + severity_surcharge"`）。这个公式字符串在代码生成时由 LLM 写出，在声明时由 SDK 校验，在生成时由引擎求值，在检查时又由验证器重新求值。三个独立消费者必须对该字符串含义达成一致，但这个字符串所属的语言却从未被定义。

这里缺失的核心心智模型是：**公式是一种嵌入在 Python 字符串中的小型语言（DSL），而任何 DSL 都需要形式化语法。** 规格把公式视为不言自明的算术表达式，但它实际上是一个安全边界（求值器必须拒绝任意代码）、一个依赖提取目标（DAG 构建器必须解析变量引用），也是一个可复现性契约（验证器必须与引擎得出完全相同的求值结果）。没有语法定义，这三件事一件都实现不了。

#### B. 抽象级缺口

**公式 / 表达式模型。** 规格在声明、生成和验证三个角色中都使用了公式字符串，却没有定义公式语言本身。这里缺失的抽象是表达式模型：正式规定哪些 token 合法（操作符、变量、字面量、函数）、它们如何组合（优先级、结合性）、变量如何解析（measure 名称 vs. effect 名称，冲突如何处理），以及求值语义是什么（向量化 NumPy？逐元素 Python？）。

这与元数据缺口（实体模型）和分布缺口（参数模型）不同。公式 DSL 的问题在于**表达式模型**，也就是嵌入式语言的语法与语义。

#### C. 架构级后果

1. **SDK → DAG 构建器边界：** `add_measure_structural()` 必须解析公式以提取变量引用，并将其转化为 DAG 边（边类型 5：公式 measure→结构型 measure）。没有解析器，DAG 构建就不完整，完整 DAG 无法包含由公式派生的边，拓扑排序也可能给出错误生成顺序，例如先生成结构型 measure，再生成它所依赖的上游 measure。Sprint 4 通过将 DAG 构建范围暂时限制在边类型 1–4 来绕开这个问题，但这只是临时措施。

2. **引擎求值器安全边界：** `eval_formula()` 函数（4.2.8）必须在安全沙箱中求值由 LLM 编写的不受信任字符串。没有操作符白名单，就没有明确的安全边界。直接用 Python `eval()` 而不加限制会允许任意代码执行；使用 `ast.literal_eval()` 又会拒绝所有算术。任何中间方案都需要先知道究竟允许哪些 AST 节点类型，而这又需要先有语法定义。

3. **引擎 ↔ 验证器求值一致性：** 引擎在 `_eval_structural()` 中对公式求值以生成数据；验证器则在 `eval_formula()` 中重新求值该公式，以计算残差检查中的期望值。如果这两次求值采用不同实现（例如一个用 `ast` 解析，另一个用正则替换），它们在边界情况上就可能产生偏差（操作符优先级、NaN 处理等）。共享语法是保证求值一致性的前提。

4. **LLM 输出校验：** LLM 可能生成求值器不接受的公式结构（例如 `log(wait_minutes)`、`wait_minutes ** 2`、`max(cost, 100)`）。没有语法定义，SDK 就无法在声明时校验公式，错误只能在生成阶段更深的位置暴露出来，更难诊断，也更昂贵。

#### D. 被阻塞的实现级决策

1. **Tokenizer / Parser 设计（子任务 1.5.2）:** 无论采用基于正则的 tokenizer、递归下降 parser、Python `ast` walker，还是受限 `eval()` 沙箱，都依赖 token 集的定义。若不知道是否允许 `log()` 之类的函数，或是否仅支持基础算术（`+`、`-`、`*`、`/`），parser 就无法动工。

2. **AST / DSL 表示形式：** 解析后的公式应表示为 Python `ast.Expression` 节点树（复用 Python 内建 parser）、自定义 AST dataclass 层级，还是简单的后缀 token 列表？表示形式决定了引擎的求值策略，以及 DAG 构建器提取边的算法。

3. **变量解析顺序（子任务 1.5.2）:** 如果公式中出现 `"severity_surcharge"`，它是 effect 名称还是 measure 名称？在 one-shot 示例里，`severity_surcharge` 是结构型 measure 的 `effects` dict 中声明的 effect，而不是独立的 measure 列。但如果某个 measure 和某个 effect 同名该怎么办？解析顺序（先看 measure？先看 effect？冲突时报错？）是影响正确性的语义决策。

4. **数值字面量和常量处理：** 示例中有 `12`、`0.04`、`9` 这样的字面量。它们总是浮点数吗？允许负数吗？允许科学计数法（`1e-3`）吗？

5. **操作符白名单与优先级表（子任务 4.2.8）:** 安全求值器必须对白名单中的 AST 节点类型放行。这既是安全决策（哪些操作是安全的），也是功能决策（LLM 可以使用哪些操作）。示例展示了 `*`、`+`、`-`，但从未展示 `**`、`/`、`%` 或函数调用。

6. **DAG 边提取算法（子任务 1.5.2）:** 为了把边类型 5 加入 DAG，构建器必须解析公式并识别哪些 token 是 measure 名称。这要求先有 token 语法，以区分 measure 名称、操作符、字面量和 effect 名称。

7. **L2 残差计算（子任务 8.3.5）:** 验证器的 L2 结构型检查必须在生成数据上对公式求值，再用实际列减去期望值，并检验残差统计量。这复用了同一个 `eval_formula()`，因此同样受制于 parser、安全边界和语法定义。

#### E. 可行的解释 / 决策选项

**Option 1: 最小算术 DSL。** 操作符仅限 `+`、`-`、`*`、`/`、一元 `-`。操作数为数值字面量（整数与浮点数，可为负数）、已声明的 measure 名称以及已声明的 effect 名称。支持使用括号分组。不允许函数调用。

**Option 2: 受限 Python 表达式子集。** 允许 Python 算术表达式的一个安全子集，通过 `ast.parse(..., mode="eval")` 解析，再对白名单 AST 节点求值。这能让语法定义更紧凑，但需要明确列出允许的节点类型（例如 `BinOp`、`UnaryOp`、`Name`、`Constant`）以及禁止的节点类型（例如 `Call`、`Attribute`、`Subscript`、`Lambda`）。

**Option 3: 扩展 DSL，支持一小组数学函数。** 在 Option 1 或 2 基础上额外支持 `log()`、`exp()`、`clip()` 等函数。它更有表达能力，但会扩大安全面，也会让声明时校验、引擎求值和验证器求值都更复杂。

#### F. 建议的澄清优先级

**首先决定：** 操作符白名单、是否支持函数调用，以及变量解析顺序。这三项就足以让 parser / evaluator / DAG 边提取实现起来。最小可用决策是：仅支持基础算术，不支持函数，若 measure 与 effect 同名则直接报错。

**第二决定：** 表示形式（直接用 Python `ast`，还是自定义 AST）。这属于实现偏好，但必须与操作符集合保持一致。

**可以延后：** 更高级的函数支持（例如 `log`、`exp`）以及更复杂的常量形式。只要先把最小 DSL 明确下来，结构型 pipeline 就能落地。

**为什么按这个顺序：** 安全边界与语义边界必须先定下来，否则任何代码实现都可能在安全性或一致性上返工。最小 DSL 的定义足以让三个消费者共享同一语言，从而解锁大部分实现工作。

#### G. 证据

- §2.1.1（规格）：结构型 measure 示例使用字符串公式 `wait_minutes * 12 + severity_surcharge`
- §2.3（规格）：将结构型 measure 描述为“由其他 measures + categorical effects + noise 确定性计算”
- §2.8（规格）：引擎在 `_eval_structural()` 中求值公式
- §2.9（规格）：验证器在 `eval_formula()` 中重新计算结构型 measure 的预测值
- 差距分析 finding A3：公式 DSL 缺少正式语法，导致安全求值、DAG 构建和残差验证都受阻
- 任务层级 1.5.2、4.2.8、8.3.5：分别对应 parser、求值器与 L2 结构型残差检查

---

### 2.3 分布 Family 参考表（Findings A1, A5, A6, A7, A8, A9, A10, A11）

#### A. 系统级原因

随机型 measure 子系统依赖于一组命名分布 family（`"gaussian"`、`"lognormal"`、`"gamma"`、`"beta"`、`"uniform"`、`"poisson"`、`"exponential"`、`"mixture"`）。LLM 在声明 measure 时只写 family 名与 `param_model`；引擎随后必须据此进行采样，验证器则必须据此构造 KS 检验或其他分布检验。但规格只列出了 family 名称，并只通过示例演示了其中两个。它从未系统定义 family 名称与参数键、NumPy 采样 API 以及验证器所需参数之间的映射关系。

这里缺失的核心心智模型是：**family 列表本身不是契约，family→参数→采样器→验证器 的映射表才是契约。** 没有这个映射，SDK 不能验证 `param_model` 键是否正确，引擎不能知道如何调用 NumPy，验证器也不知道向 scipy 传什么参数。

#### B. 抽象级缺口

**参数模型 / 分发模型。** 缺失的抽象是一张参数参考表，明确规定每个 family：

- 需要哪些参数键；
- 这些参数键在声明层是如何表达的（例如 `mu` / `sigma`）；
- 引擎采样时如何映射到 NumPy / 自定义采样函数；
- 验证器做统计检验时如何映射到 scipy 参数格式或替代校验方式。

这是一种参数模型缺口，而不是实体模型或表达式模型缺口。

#### C. 架构级后果

1. **SDK 声明校验缺失：** `add_measure()` 无法判断某个 `family="gamma"` 是否应该包含 `shape` 与 `scale`、还是 `alpha` 与 `beta`、还是 `k` 与 `theta`。没有参考表，SDK 既不能拒绝无效参数，也不能为缺失参数提供精确错误信息。

2. **引擎采样分发缺失：** `_sample_stochastic()` 必须根据 family 名调度到具体采样器。没有 family→采样函数 映射，分发逻辑只能为示例中的 `gaussian` / `lognormal` 特判，其他 family 无法实现。

3. **验证器分布检验缺失：** §2.9 中的 KS 检验伪代码使用 `scipy.stats.kstest(subset[col["name"]], col["family"], args=expected_params)`。但 scipy 的分布名与参数顺序未必与规格中的 family 名和 `param_model` 一致。若不定义参考表，验证器就无法构造正确 `args`。

4. **Auto-fix 策略无法泛化：** `widen_variance` 这类策略必须知道不同 family 中“方差”由哪个参数控制。对 `gaussian` 来说是 `sigma`；对 `lognormal` 也是 `sigma`；对 `gamma` 则可能是 `shape` 与 `scale` 的组合。没有参考表，修复策略就无法跨 family 泛化。

#### D. 被阻塞的实现级决策

1. **Family 参数键定义（子任务 1.4.3、1.5.4）:** 每个 family 到底接受哪些参数键？
2. **`param_model` 结构约束：** 某些参数是否允许使用 `intercept + effects`，而另一些参数必须是常量？`mixture` 的 `param_model` 结构是否完全不同？
3. **采样器映射（子任务 4.2.1、4.2.2）:** 每个 family 对应哪个 NumPy 或自定义采样函数？参数顺序如何映射？
4. **验证器映射（子任务 8.3.1、8.3.2）:** scipy 的分布名、参数顺序、以及对 `mixture` 的替代检验方案是什么？
5. **错误消息设计：** 当用户为 `beta` 漏掉参数，SDK 应报什么错？是否列出期望键集合？

#### E. 可行的解释 / 决策选项

**Option 1: 为全部 8 个 family 建立完整参考表。** 每一行包含：family 名、声明参数键、采样器实现、验证器实现 / 参数映射。这是最完整也最直接的方案。

**Option 2: 先将 family 范围收缩到示例中真正演示过的分布（例如 `gaussian`、`lognormal`），其余标记为 `NotImplementedError`。** 这能加速实现，但会偏离规格列出的能力范围。

**Option 3: 保留 8 个 family，但将 `mixture` 与少数复杂 family 推迟到第二阶段。** 这是一种折中方案，先确保大多数常见分布可用，再单独为特殊 family 设计更复杂的参数结构。

#### F. 建议的澄清优先级

**首先决定：** 7 个常规 family（除 `mixture` 外）的参数键与采样 / 验证映射。它们构成随机型 pipeline 的主体。

**第二决定：** `mixture` 的表示方式，是统一的复合 schema，还是暂时推迟。

**可以延后：** 更细致的 auto-fix 参数变异策略。只要先有参考表，auto-fix 的泛化逻辑之后可以逐步细化。

**为什么按这个顺序：** 参数键与采样 / 验证映射是 SDK、引擎与验证器共同依赖的最小闭环。一旦它存在，绝大多数随机型 measure 就能声明、采样并验证。

#### G. 证据

- §2.1.1（规格）：列出 8 个支持的分布，但只示例 `gaussian` 与 `lognormal`
- §2.3（规格）：定义随机型 measure 为条件分布，但未给出 family 参考表
- §2.8（规格）：引擎需在 `_sample_stochastic()` 中按 family 采样
- §2.9（规格）：验证器需在 L2 中按 family 构造 KS 检验
- 差距分析 findings A1、A5、A6、A7、A8、A9、A10、A11：集中指出 family→参数 / 采样 / 验证映射缺失
- 对齐映射中的 Blocker 3：显示该问题直接阻塞多个 SDK、引擎与验证器子任务

---

### 2.4 Pattern Type 行为三元组（Findings B1, B4, C1, C2, C7）

#### A. 系统级原因

规格列出了 6 种 pattern type：`"outlier_entity"`、`"trend_break"`、`"ranking_reversal"`、`"dominance_shift"`、`"convergence"`、`"seasonal_anomaly"`。但除了个别示例外，规格既没有系统定义每种 pattern 所需的 `params`，也没有定义注入算法，更没有定义对应的 L3 验证逻辑。也就是说，pattern type 名称存在，但“声明什么、注入什么、如何验证”这三者并没有被一体化设计。

这里缺失的核心心智模型是：**每个 pattern type 都必须是一个“行为三元组”**，即：

1. 一个参数 schema；
2. 一个注入算法；
3. 一个验证准则。

如果缺一，pattern type 就只是标签，不是可执行能力。

#### B. 抽象级缺口

**行为三元组模型。** 与前面几个 blocker 不同，这里缺失的不是单一数据契约，而是一个三元耦合抽象：`(params schema, injection semantics, validation semantics)`。pattern type 的实现无法只补其中一部分，因为三者必须共同设计，才能保证注入后可以被验证，而且验证指标确实对应注入意图。

#### C. 架构级后果

1. **SDK → 引擎：** `inject_pattern()` 目前只能记录 pattern 声明，但引擎的 `_inject_patterns()` 无法为未定义的 pattern type 执行任何确定性变换。

2. **引擎 → 验证器：** 即便引擎用某种“临时算法”注入了 pattern，若验证器没有匹配的 L3 检查，系统也无法证明该 pattern 成功植入。

3. **LLM 提示词可信度：** 提示词要求“至少 2 次 `inject_pattern()` 调用”，但如果 pattern type 中有大部分没有落地行为三元组，LLM 生成的代码就会名义上满足硬约束，实际上却无法执行或验证。

#### D. 被阻塞的实现级决策

1. **每个 pattern type 的参数字段定义。**
2. **每个 pattern type 的注入算法。**
3. **每个 pattern type 的 L3 验证指标与阈值。**
4. **元数据表示：** `params` 是否原样存储？是否需要额外归档注入后的实际效果值？
5. **Auto-fix 策略：** pattern 失败时应该放大什么参数？是 `magnitude`、`z_score`，还是别的字段？

#### E. 可行的解释 / 决策选项

**Option 1: 一次性为 6 个 pattern type 全部设计完整三元组。** 这是与规格最一致的方案，但需要集中设计工作。

**Option 2: 先只正式支持示例中出现或最容易定义的 pattern（例如 `outlier_entity`、`trend_break`），其余抛出 `NotImplementedError`。** 这更容易落地，但会与“支持的 pattern types”列表存在偏差。

**Option 3: 把复杂 pattern（例如 `convergence`、`dominance_shift`）先降级为模板化算法和弱验证。** 这是一种中间路线，可以先保证端到端可用，再逐步提高行为精度。

#### F. 建议的澄清优先级

**首先决定：** 是否当前版本真的要完整支持全部 6 个 pattern type。如果是，就必须为 6 个 pattern 各自设计三元组；如果不是，就应在规格和实现中明确 defer 哪些类型。

**第二决定：** 每个 pattern type 的参数 schema 与 L3 判定标准，因为这两项将约束注入算法的设计空间。

**为什么按这个顺序：** 若支持范围本身不明确，后续所有实现都可能返工。先定范围，再定参数与验证，再落算法，是最稳妥的顺序。

#### G. 证据

- §2.1.2（规格）：列出 6 个 `PATTERN_TYPES`
- §2.5（规格提示词）：要求至少 2 次 `inject_pattern()` 调用
- §2.8（规格）：引擎需在 `_inject_patterns()` 中执行 pattern 注入
- §2.9（规格）：L3 只对部分 pattern 给出示例验证逻辑
- 差距分析 findings B1、B4、C1、C2、C7：指出 pattern 参数、注入、验证三者未闭环

---

### 2.5 后处理不变量契约（Findings B2, B3, B7, C5, C6）

#### A. 系统级原因

规格将引擎描述为四阶段 pipeline：α（骨架构建）、β（measure 生成）、γ（pattern 注入）、δ（realism 注入）。随后又定义了三层验证 L1 / L2 / L3，以及一个 auto-fix 循环。但规格没有说明：每一层验证应该针对哪一个阶段输出执行，或者 pattern / realism 注入后，哪些统计性质应该被保留、哪些应被允许偏离。换句话说，缺少的是跨阶段不变量契约。

这里缺失的核心心智模型是：**多阶段执行模型必须配套“每个阶段结束后系统仍保证什么”的不变量说明。** 没有这层说明，验证器与 auto-fix 循环就会在相互冲突的目标上工作。

#### B. 抽象级缺口

**执行模型 / 阶段不变量模型。** 缺失的不是某个字段或某个函数，而是关于 α、β、γ、δ 与 L1、L2、L3 之间映射关系的正式说明。也就是说，哪些验证针对 pre-pattern 数据，哪些针对 post-pattern 数据，哪些必须容忍 realism 带来的 NaN / dirty 值。

#### C. 架构级后果

1. **L1 与 realism 冲突：** L1 要求所有 measure 列 finite 且 non-null，而 δ realism 注入可能显式引入 missing data。若 L1 在 realism 之后运行，它就会把 realism 视为失败。

2. **L2 与 pattern 冲突：** L2 要求随机型 measure 符合声明的条件分布，但 γ 的 pattern 注入（例如 outlier、trend break）本来就会让局部数据偏离原始分布。若 L2 在 pattern 之后运行，就会把成功注入的 pattern 视为统计错误。

3. **Auto-fix 循环内部矛盾：** 规格中的 auto-fix 伪代码在策略执行后重新调用 `build_fn(seed=42 + attempt)`。如果修复策略修改的是当前 simulator 实例状态，而 `build_fn` 每次都重新构造新实例，那么修复就会被丢弃。

4. **Pipeline orchestrator 语义不清：** §2.7 的错误反馈循环与 §2.9 的 auto-fix 循环之间如何组合没有明说。是先做代码级重试，再做参数级 auto-fix？还是二者交替？预算如何叠加？

#### D. 被阻塞的实现级决策

1. **验证阶段归属：** L1、L2、L3 分别作用于 α / β / γ / δ 的哪个输出？
2. **Realism 与结构检查的兼容规则：** finite / non-null 检查是否应在 realism 之前进行，或在 realism 之后改为“缺失率不超过阈值”？
3. **Auto-fix 变异模型：** 修复策略是修改 simulator 实例并调用 `sim.generate()`，还是修改 `build_fn` 所依赖的外部 spec，再重建 simulator？
4. **重试循环组合：** §2.7 与 §2.9 的循环是串行组合，还是嵌套组合，还是共享预算？

#### E. 可行的解释 / 决策选项

**Option A: 按阶段分离验证。** 让 L1 / L2 在 Phase β 输出上运行，L3 在 γ 之后运行，而 realism 专门有自己的后置检查。这样统计正确性与 pattern 成功性不会互相打架。

**Option B: 所有验证都对最终输出运行。** 这最接近“最终数据必须自洽”的直觉，但会让 L2 与 L3、L1 与 realism 发生根本冲突。

**Option C: 将 pattern 与 realism 看作“允许偏离”的后处理，并在验证器中硬编码豁免规则。** 这能在一个验证入口中完成所有检查，但规则会变得复杂且不透明。

关于 auto-fix：

**Option X: 修复策略修改 simulator 实例状态，再调用 `sim.generate()`。** 这是唯一能真正保留修复效果的方式。

**Option Y: 修复策略修改可序列化的 spec，对 `build_fn` 的输入进行变更，然后重建 simulator。**

**Option Z: 保持当前伪代码，接受修复策略只做“建议”而不生效。** 这显然不成立。

#### F. 建议的澄清优先级

**首先决定：** 验证阶段归属。Option A（按阶段分离）最干净，也与差距分析（B2）建议一致。它要求引擎暴露 Phase β 输出，这只是一个较小的 API 变化。

**第二决定：** Auto-fix 变异模型（Option X vs. Y vs. Z）。这会解决伪代码矛盾，并决定重试循环调用什么。Option X（修改实例并调用 `sim.generate()`）是唯一功能上正确的方案，也与差距分析（B3、B7）一致。

**第三决定：** 循环组合语义。顺序式解释（先 §2.7，后 §2.9，不升级，预算总计 6）与 §2.7 第 3 步的措辞一致，可作为合理落地方案。

**可以延后：** soft-fail 契约（Phase 3 如何处理失败数据）、`reshuffle_pair` 的 pattern 列排除规则，以及 auto-fix 策略覆盖范围扩展（finding C4）。

**为什么按这个顺序：** 验证阶段归属是最关键的架构决策，它决定 L2 与 L3 能否共存而不震荡，进一步决定 auto-fix 循环能否收敛，也决定 pipeline orchestrator 能否产出可用结果。变异模型排第二，因为它决定重试循环的实现方式。循环组合排第三，因为它大体可以从规格推导出来，风险较低。

#### G. 证据

- §2.8（规格）：四阶段引擎 pipeline（α、β、γ、δ），但没有跨阶段不变量契约
- §2.9（规格第 574–575 行 vs. 582–584 行）：L1 的 finite 检查与 realism 的 NaN 注入相矛盾
- §2.9（规格第 613–621 行）：L2 对 post-injection 数据做 KS 检验，但参数来自 pre-injection 规格
- §2.9（规格第 691–698 行）：修复策略应用后又被 `build_fn` 重建覆盖掉
- §2.7 第 3 步：`"SUCCESS → proceed to ... Validation (§2.9)"`，暗示顺序式组合
- 差距分析 findings B2（CRITICAL）、B3（CRITICAL）、B7（MODERATE）、C5（MODERATE）、C6（MODERATE）
- 对齐映射 Blocker 5：直接 1 个 `SPEC_INCORRECT`，并间接劣化 8 个以上任务
- 任务层级 9.3.1（`SPEC_INCORRECT`）、11.1.1–11.1.2（`BLOCKED`）

---

### 2.6 Phase 1 → Phase 2 接口契约（Finding D1）

#### A. 系统级原因

Phase 2 从 Phase 1 接收场景上下文，并用它填充 LLM 提示词（§2.5 中的 `{scenario_context}` 占位符）。当前工作系统已通过 `json.dumps(scenario, indent=2)` 以 JSON blob 的方式传递该上下文。缺少的是一个带类型、可校验、可版本化的正式契约，也就是明确定义场景必须包含哪些字段、这些字段的类型是什么、以及如何校验完整性。

这里缺失的心智模型并不是不存在，而是**只完成了部分形式化**：场景上下文本质上是一个**跨阶段边界对象**，应在接口处被定义，而不是从实现中逆推出。事实上，一个事实上的 schema 已经存在（由 Phase 1 中的 `ScenarioContextualizer.validate_output()` 强制），只是没有被表达为正式类型。

#### B. 抽象级缺口

**跨阶段契约 / 声明模型。** 缺失的抽象是**带类型的场景上下文 schema**，也就是将 `ScenarioContext` 正式定义为一个数据结构，列出必填字段、选填字段、字段类型与校验规则。这是发生在跨阶段边界上的声明模型缺口。

需要注意的是，Stage 2 的 blocker 分解正确指出：这是一个“形式化 blocker”，而不是“能力 blocker”。基本注入路径已经可用，剩余缺口是接口带类型完整性的问题。

#### C. 架构级后果

1. **提示词模板构建器（Module 10）：** 提示词模板（10.1.1）可以从原始 dict 渲染 `{scenario_context}`，但没有 schema 就无法验证完整性。若 Phase 1 生成的场景缺少 `target_rows`，提示词会畸形，LLM 会生成错误代码。

2. **Pipeline orchestrator 入口（Module 11）：** orchestrator 接收来自 Phase 1 的 scenario 并将其传给 prompt builder。没有带类型契约时，针对畸形 scenario 的错误处理只能是临时性的（捕捉 `KeyError`），而不能在入口统一校验。

3. **集成测试：** 端到端测试需要场景 fixture。没有正式 schema 时，fixture 只是对 one-shot 示例的复制，而不是根据契约校验过的场景对象。

#### D. 被阻塞的实现级决策

1. **`ScenarioContext` 类设计。** 是 dataclass、Pydantic model 还是 `TypedDict`？字段名、字段类型、必填 / 选填属性如何定义？

2. **必填字段。** 来自 `ScenarioContextualizer.validate_output()` 的事实字段集为：`scenario_title: str`、`data_context: str`、`key_entities: list[dict]`、`key_metrics: list[dict]`、`temporal_granularity: dict`、`target_rows: int`。这些是否都必填？是否还有额外字段？

3. **序列化格式。** 继续使用 JSON（当前做法）？dataclass-to-dict？还是 Pydantic `.model_dump()`？提示词模板需要一个字符串表示。

4. **版本字段。** `ScenarioContext` 是否应包含 `version` 字段，以支持 Phase 1 与 Phase 2 之间的前向兼容？

#### E. 可行的解释 / 决策选项

**Option 1: 将事实上的 schema 正式化为一个 Pydantic `BaseModel`。** 以 `ScenarioContextualizer.validate_output()` 中的 6 个字段为起点，添加类型、校验逻辑，以及一个可选 `version` 字段。这是把现有可用接口正式化的最小改动。

**Option 2: 与 pipeline redesign audit 中的 `result_models.py` 设计共同设计。** 对齐映射 v4 指出，`audit/5_agpds_pipeline_runner_redesign.md` 已包含一个 `ScenarioContext` 设计，可以直接作为起点。

**Option 3: 推迟形式化，继续使用原始 dict 接口。** 接受 `json.dumps` 路径对 Phase 2 已“足够可用”，等到 Phase 3 集成时再正式化。

#### F. 建议的澄清优先级

**首先决定：** 必填字段列表与类型。这个决策很小，可以通过检查现有 `ScenarioContextualizer.validate_output()` 代码与 §2.5 提示词模板快速完成。

**可以延后：** 版本化、序列化格式，以及 Pydantic vs. dataclass。这些是工程质量决策，不是正确性决策。

**为什么：** 这个 blocker 只影响 2 个子任务（10.1.2、11.1.1），且已有一定缓解。它不应在三大基础 blocker 之前占用决策带宽。

#### G. 证据

- §2.5（规格第 387–389 行）：`{scenario_context}` 占位符，但无 schema
- 对齐映射 Blocker 6：2 个 `BLOCKED` 子任务，在 v3 中已被弱化
- 对齐映射 v4 注释：引用 `audit/5_agpds_pipeline_runner_redesign.md` 中的设计
- 任务层级 10.1.2（`BLOCKED`）、11.1.1（被此项与 C5 共同阻塞）
- 现有代码：`ScenarioContextualizer.validate_output()` 已强制一套事实字段集

---

### 2.7 跨组默认语义（Finding A12）

#### A. 系统级原因

当两个维度组既没有 `declare_orthogonal()`，也没有 `add_group_dependency()` 声明时，规格并未定义它们的根列应如何相对采样。§2.2 说跨组独立性是“opt-in, not default”，却没有说明真正的默认行为。对于 N 个维度组，会有 O(N²) 个成对关系，而 LLM 只被要求至少声明一次 `declare_orthogonal()`，这意味着大多数组对都不会有显式声明。

这里不稳定的核心心智模型是：**“opt-in, not default” 暗示存在某种非独立的默认行为，但规格从未定义这种默认行为。** 最自然的实现方式（把未声明组对都视为独立）又会直接与“not default”这句话相冲突。

#### B. 抽象级缺口

**依赖模型 / 执行模型。** 缺失的抽象是**默认跨组采样策略**，也就是当两个组之间没有显式声明时，骨架构建器应如何采样它们的根列。这是依赖模型上的缺口：规格定义了两种显式模式（正交、依赖），却没有定义隐式模式。

#### C. 架构级后果

骨架构建器（4.1.1）在生成时必须决定如何对未声明的组对进行采样。当前假设是最简单的做法：每个组独立调用 `rng.choice` 进行采样。这个假设已被记录下来，但风险在于若后续决策否定它，采样算法就必须修改。

验证器的正交检查（8.2.5）只检查已声明正交的组对。如果未声明组对被默认当作独立，系统却没有验证这项假设；如果未声明组对不应独立，系统也没有检查来捕捉该依赖。

#### D. 被阻塞的实现级决策

1. **骨架构建器采样逻辑（子任务 4.1.1）:** 独立采样？从隐式联合分布中采样？还是如果组对未全部声明就拒绝该场景？
2. **验证器对未声明组对的覆盖：** L1 是否应增加未声明组对检查？如果增加，应验证什么？
3. **LLM 提示词引导：** 是否应要求 LLM 声明所有组对？是否应对未声明组对发出警告？

#### E. 可行的解释 / 决策选项

**Option 1: 默认独立。** 未声明组对都独立采样。虽然这与“opt-in, not default”的措辞不一致，但它是最简单、最可预测的行为。规格中的表述可能更像一种愿景，而不是强制语义。

**Option 2: 要求穷尽声明。** LLM 必须将每一对组都声明为正交或依赖。若存在未声明组对，SDK 拒绝该场景。这在语义上最干净，但对 LLM 约束最强。

**Option 3: 默认“弱相关”。** 用一个小而未参数化的相关性来处理未声明组对。它更符合“not default”的措辞，但由于难以验证、难以解释，基本不可取。

#### F. 建议的澄清优先级

**可以延后。** 当前假设（Option 1: 默认独立）已经文档化，并且局限于单个方法。没有硬阻塞子任务依赖该决策。如果后续改变，影响范围也主要局限在 `_build_skeleton`，以及可能新增一个 L1 检查。

#### G. 证据

- §2.2（规格第 153 行）：`"Cross-group independence is opt-in, not default"`
- §2.1.2 提示词硬约束 4：只要求“至少 1 个 `declare_orthogonal()`”，而非穷尽声明
- 差距分析 finding A12（CRITICAL，审计后发现）
- 对齐映射 4.1.1：`NEEDS_CLARIFICATION`，并附带已记录假设

---

### 2.8 Censoring Schema（Finding A4）

#### A. 系统级原因

`set_realism()` 中的 `censoring` 参数既出现在方法签名中，也出现在引擎 pipeline 中，但没有类型注解、schema 或语义定义。这是最简单的 blocker：一个 API 参数出现了，但没有定义。

#### B. 抽象级缺口

**声明模型 / 元数据模型。** 缺失的抽象是 censoring 规格 schema，也就是 `censoring` dict 到底包含什么。这是 realism 子系统声明模型中的一个局部缺口。

#### C. 架构级后果

影响被限制在 realism 注入模块（Phase δ）。元数据中没有字段向 Phase 3 记录 censoring；验证器也没有针对被 censor 的列做调整（L2 的 KS 检验在被 censor 的分布上会失败）。

#### D. 被阻塞的实现级决策

1. **Censoring dict schema。** 目标列、方向（left / right / interval）、阈值，以及是否创建指示列。
2. **Censoring 的元数据表示。**
3. **L2 对被 censor 列的调整。**

#### E. 可行的解释 / 决策选项

**Option 1: 最小 censoring schema。** `{"columns": ["cost"], "direction": "right", "threshold": 10000}`。右 censoring 会将高于阈值的值裁剪到阈值；左 censoring 裁剪低于阈值的值；区间 censoring 同时裁剪两端。可选地添加一个 indicator 列标记被 censor 的行。

**Option 2: 完全延后。** `censoring=None` 的默认路径本身可用。由于 censoring 是可选能力，可把其规格推迟到未来版本。

#### F. 建议的澄清优先级

**可以延后。** 只有 1 个子任务（4.4.3）被阻塞，而且 censoring 本身是可选项。应在三大基础 blocker 之后机会式解决。

#### G. 证据

- §2.1.2（规格第 129 行）：签名中出现 `censoring`，但无定义
- 差距分析 finding A4（MODERATE）
- 对齐映射 Blocker 7：1 个 `BLOCKED` 子任务

---

## 3. 跨 Blocker 综合

### 3.1 共享同一缺失抽象的 blocker

**声明模型 / 实体模型** 支撑了三个 blocker：

- Blocker 1（元数据 schema）：声明模型的序列化形式
- Blocker 3（分布 family）：声明模型中的参数化部分
- Blocker 8（censoring schema）：realism 声明模型的一个局部角落

这三者共享同一个根因：规格定义了 LLM 写什么（SDK API 表面），但没有定义系统记录什么（内部数据模型）或向下游传达什么（元数据模型）。一旦声明模型，即“每种实体类型由哪些字段描述，以及这些字段如何序列化”被解决，这三项就会一起被解决。

**表达式模型** 是 Blocker 2（公式 DSL）特有的问题，其他 blocker 不共享这类抽象缺口。

**执行模型** 支撑两个 blocker：

- Blocker 5（后处理不变量契约）：多阶段 pipeline 的执行模型
- Blocker 7（跨组默认语义）：骨架构建器的执行模型

**行为三元组模型** 是 Blocker 4（pattern type）特有的问题。这是一个独特的缺口，需要同时设计三个紧耦合抽象。

### 3.2 哪些决策能解锁最多实现工作

按下游子任务数量排序：

1. **元数据 schema 字段规格**：直接解锁 9 个 `SPEC_INCORRECT` 子任务（5.1.3、5.1.4、5.1.6、8.2.3、8.2.4、8.3.3、8.3.4、8.3.6、8.4.2）；并间接启用 auto-fix 重试循环（9.3.1）与 pipeline orchestrator（11.1.1、11.1.2）。**约可启用 12 个子任务。**

2. **分布 family 参考表**：直接解锁 7 个 `BLOCKED` 子任务（1.4.3、1.4.4/延后、1.5.4、4.2.1、4.2.2、8.3.1、8.3.2）。**可启用 7 个子任务。**

3. **公式 DSL 操作符白名单**：直接解锁 4 个 `BLOCKED` 子任务（1.5.2、4.2.5/4.2.8、8.3.5），并启用 DAG 的边类型 5。**可启用 4 个以上子任务。**

4. **验证阶段归属**：直接解锁 1 个 `SPEC_INCORRECT` 子任务（9.3.1），并解决 8 个以上任务的劣化问题。它启用 auto-fix 循环与 pipeline orchestrator。**约解锁 9 个子任务**（与元数据有重叠）。

5. **Pattern type 三元组**：直接解锁 9 个 `BLOCKED` 子任务。**可启用 9 个子任务**，但都集中在同一功能切片中。

### 3.3 哪些 blocker 来自系统模型不完整，哪些属于硬编码工作

**系统模型不完整（系统设计尚未完成）：**

- Blocker 1（元数据 schema）：元数据契约从未被正式设计
- Blocker 2（公式 DSL）：表达式语言从未被正式规定
- Blocker 3（分布 family）：参数参考表从未建立
- Blocker 5（后处理不变量）：多阶段执行模型从未被形式化
- Blocker 7（跨组默认值）：依赖模型存在未定义情形

**硬编码工作（设计清晰，但实现并不简单）：**

- Blocker 4（pattern type）：设计工作本身具有创造性（发明注入算法与验证检查），而不仅仅是把既有概念形式化
- Blocker 8（censoring）：规模较小，但仍需要一个关于语义的设计决策

前一组（5 个 blocker）才是真正应集中澄清的地方。这些不是编码瓶颈，而是设计规格瓶颈。工程师无法单靠写代码解决它们，必须由规格作者或架构师做出决策。后一组（2 个 blocker）则可以由工程师在不偏离规格精神的前提下做设计决策并落地。

---

## 4. 最终结论

### 最深层的几个根问题

Phase 2 规格从概念上看架构良好（声明式 SDK、确定性引擎、三层验证所组成的生产者-消费者 pipeline），但**尚未完成从产品概念到实现代码之间的中间设计层**。具体来说：

1. **声明模型是隐式的。** SDK API 定义了 LLM 会写什么，元数据示例展示了部分序列化结果，但规范化的数据模型，即“哪些字段描述每种实体类型”，却散落在 API 签名、伪代码示例和推断之中。系统没有一个单一真相源来回答“系统如何描述一个随机型 measure？”或“系统如何描述一个 group dependency？”

2. **执行模型缺少跨阶段不变量契约。** 引擎的四个阶段（α、β、γ、δ）与验证器的三层（L1、L2、L3）是分别设计的。规格没有说明哪一层验证适用于哪一阶段输出，因此出现结构性矛盾（L2 vs. pattern，L1 vs. realism）。

3. **参数分发表从未被系统整理成表。** 规格列出了 8 个分布 family 名，但只演示了其中两个。family 名 → 参数键 → numpy 采样 → scipy 验证的映射，本应是原始规格的一张基础参考表。

### 最重要的未决策

按优先级排序：

1. **元数据 schema 字段规格**：每种实体类型有哪些字段、字段类型是什么。（约 1 天设计工作，解锁约 12 个子任务）
2. **分布 family 参考表**：7 行 × 4 列的查找表。（约 2 小时设计工作，解锁 7 个子任务）
3. **公式 DSL 操作符白名单与优先级**：一页左右的语法说明。（约 1 小时设计工作，解锁 4 个子任务）
4. **验证阶段归属**：L2 在 Phase β 输出上运行，还是在注入之后运行？一个架构决策即可。（约 30 分钟决策时间，可解锁 auto-fix 循环）
5. **Auto-fix 变异模型**：应修改 simulator 实例并调用 `generate()`，而不是重新跑 `build_fn`。这是一次伪代码修正。（约 30 分钟决策时间，可修复重试循环）

### 从当前歧义走向可实现清晰度的最短路径

**Step 1（可并行，约 1 天）：** 同时解决 Blocker 1、2、3。它们彼此独立，合计可解锁约 23 个子任务。Blocker 1 需要一张元数据字段表。Blocker 2 需要一个操作符白名单。Blocker 3 需要一张分布参考表。这三项都是文档设计工作，而不是编码工作。

**Step 2（约 2 小时）：** 解决 Blocker 5，并决定：(a) L2 运行在 Phase β 输出上（注入前）；(b) auto-fix 修改 simulator 实例并通过 `sim.generate()` 重试；(c) 循环顺序为串行组合，预算 3+3=6。这三项决策可解决 auto-fix 与 pipeline orchestrator 路径上的所有 `SPEC_INCORRECT` 与劣化子任务。

**Step 3（范围决策）：** 决定现在是否为 4 个未明确的 pattern type 制定完整规格。若现在做，需预留约 1 天共同设计这 4 个 pattern 的（params、injection、validation）三元组；若延后，则加上 `NotImplementedError` stub 并继续推进。

**Step 4（低优先级）：** 将 `ScenarioContext` 正式化为带类型 dataclass；确定跨组默认语义；定义 censoring schema。这些都可以机会式完成。

完成 Step 1 与 Step 2 之后，系统将从 34 个受阻子任务降至大约 9 个（如果 pattern type 延后）或 0 个（如果所有 blocker 都被解决）。从当前歧义状态走向实现就绪清晰度的关键路径，大约只需要 **1–2 天的设计规格工作**，而不是编码工作。
