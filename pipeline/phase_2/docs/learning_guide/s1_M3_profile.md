# M3: LLM Orchestration — 模块画像

## 一句话职责

为给定场景提示 LLM 生成合法的 SDK 脚本，在沙箱中执行该脚本，并将类型化异常反馈给 LLM 进行自我修正，最多重试 3 次。

## 实现状态：5/11（45%）

## 在流水线中的位置

```
Phase 1 ──► 【M3: LLM Orchestration】──► M1 ──► M2 + M4 ──► M5 ──► Phase 3
                 ▲           │
                 └───────────┘
                 Loop A (max 3, with LLM)
```

- **上游：** Phase 1（提供 `scenario_context` dict：title, entities, metrics, temporal grain, target_rows, complexity tier）
- **下游：** M1 SDK Surface（通过 sandbox 执行 LLM 脚本，M1 的 `add_*()` / `declare_*()` / `inject_*()` 方法在脚本内被调用）
- **反馈来源：** M1 的 typed exceptions（`CyclicDependencyError`, `UndefinedEffectError`, `NonRootDependencyError`）
- **涉及依赖编号：** 1 (Phase 1→M3), 2 (M3→M1), 3 (M1→M3 feedback)

## 构建顺序中的位置

第 6 步（最后），前置依赖：types, M1, M4, M2, M5（全部）。

M3 是流水线**入口**但构建顺序**终点**——因为理解它需要先理解它调用的所有下游模块。

---

## 已实现功能详解（SPEC_READY）

### SR-1: System Prompt Template Structure（系统提示模板结构）

**规范定义（§2.5）：** 完整的 LLM 系统提示模板，包含五个区域——角色前言、SDK 方法白名单（Step 1 列声明 + Step 2 关系/模式）、九条硬约束、软指引、one-shot 完整示例（上海急诊场景）、和 `{scenario_context}` 占位符。这是 LLM 行为的**唯一约束机制**。

**代码实现：**
- 📍 [prompt.py:35-200](phase_2/orchestration/prompt.py#L35-L200) — `SYSTEM_PROMPT_TEMPLATE: Final[str]`
- 模板以 `Final[str]` 模块级常量存储，使用字符串拼接而非多行 raw string
- 五个区域清晰对应：
  - 角色前言（L37-43）："You are an expert Data Scientist Agent..."
  - SDK 白名单（L45-63）：Step 1 四个方法 + Step 2 四个方法，含内联签名注释
  - 支持的分布族和模式类型（L64-68）：8 种 families, 6 种 patterns
  - HC1-HC9（L70-82）：见 SR-2
  - 软指引（L84-89）：temporal derivation, hierarchy, 3+ measures 等
  - One-shot 示例（L91-193）：完整的上海急诊 `build_fact_table(seed=42)` 函数
  - 任务插槽（L195-199）：`{scenario_context}` 占位符
- 📍 [prompt.py:32-33](phase_2/orchestration/prompt.py#L32-L33) — `_CODE_FENCE` / `_CODE_FENCE_PY` 辅助常量，避免 f-string 内嵌 markdown 围栏提前关闭
- 📍 [prompt.py:207-262](phase_2/orchestration/prompt.py#L207-L262) — `render_system_prompt(scenario_context: str) -> str`
  - 使用 `str.replace("{scenario_context}", scenario_context)` 注入场景
  - **不使用 `str.format()`**——因为模板内含大量 Python dict 字面量的 `{}`，`format()` 会误解析
  - 输入验证：拒绝 `None` 和空字符串，抛 `InvalidParameterError`

💡 **为什么这样设计？** 选择 `str.replace()` 而非 `str.format()` 或 Jinja2，是因为 §2.5 的 one-shot 示例中到处是 Python 字典字面量 `{"Mild": 0.0, "Moderate": 0.4, ...}`——这些花括号会被 `str.format()` 当作模板变量。用 `str.replace()` 只替换唯一的 `{scenario_context}` 占位符，零歧义。

**规范偏差：**
- stage4 描述了一个 `PromptTemplate` 类和 `assemble_prompt(scenario_context: dict) → list[dict]` 接口（接收 dict，返回消息数组）。实际实现更简单：`render_system_prompt(scenario_context: str) -> str`（接收字符串，返回字符串）。消息格式化（string → `[{"role": "system", "content": ...}]`）需在调用方完成。

---

### SR-2: Hard Constraint Enumeration (HC1–HC9)（硬约束枚举）

**规范定义（§2.5）：** 九条二值通过/失败规则，共同保证 LLM 脚本在结构上不被 M1 拒绝。

**代码实现：**
- 📍 [prompt.py:70-82](phase_2/orchestration/prompt.py#L70-L82) — 嵌入 `SYSTEM_PROMPT_TEMPLATE` 字符串

| HC | 行号 | 约束内容 | 保护的属性 |
|---|---|---|---|
| HC1 | L71 | `ATOMIC_GRAIN: each row = one indivisible event` | 语义粒度 |
| HC2 | L72 | `≥2 dimension groups, each ≥1 categorical, plus ≥2 measures` | 结构最小丰富度 |
| HC3 | L73 | `All column declarations (Step 1) BEFORE any relationship declarations (Step 2)` | SDK 内部阶段排序 |
| HC4 | L74 | `≥1 declare_orthogonal() between genuinely independent groups` | 正交声明存在性 |
| HC5 | L75-76 | `≥1 add_measure_structural() + ≥2 inject_pattern()` | 结构性度量 + 模式注入 |
| HC6 | L77 | `Pure, valid Python returning sim.generate()` | 输出格式 |
| HC7 | L78-79 | `Measure dependencies must be acyclic (DAG)` | 度量 DAG 无环 |
| HC8 | L80 | `Cross-group deps only between root columns; root DAG acyclic` | 根级 DAG 约束 |
| HC9 | L81-82 | `Every symbolic effect must have explicit numeric definition` | 符号完备性 |

这些约束分为三类：语义（HC1）、结构最小值（HC2/4/5）、图约束（HC7/8）、排序（HC3）、格式（HC6）、完备性（HC9）。其中 HC7/HC8/HC9 在 M1 中有运行时验证对应（`CyclicDependencyError`、`NonRootDependencyError`、`UndefinedEffectError`）。

**规范偏差：** 无。

---

### SR-3: Retry Protocol Structure（重试协议结构）

**规范定义（§2.7）：** 六步流水线——(1) LLM 生成脚本 (2) sandbox 执行 (3) 成功则通过 (4) 失败则捕获 typed exception (5) 追加 code+traceback 到对话 + 重新提示 (6) 超过 `max_retries=3` 则 log and skip。

**代码实现：**
- 📍 [sandbox.py:536-704](phase_2/orchestration/sandbox.py#L536-L704) — `run_retry_loop()`

算法核心（简化伪代码）：

```python
# L623-704
current_code = initial_code
history = []

for attempt in range(1, max_retries + 1):     # L629
    sandbox_ns = ns_factory()                  # L637 — 全新 namespace（状态重置）
    result = execute_in_sandbox(current_code,   # L638
                                timeout, sandbox_ns)
    history.append(result)                     # L643

    if result.success:                         # L647 — 成功，提前退出
        return RetryLoopResult(success=True, dataframe, metadata, attempts)

    if attempt < max_retries:                  # L663 — 非最后一次，准备反馈
        feedback = format_error_feedback(       # L665
            current_code, result.exception, result.traceback_str)
        current_code = llm_generate_fn(         # L682
            system_prompt, feedback)

return RetryLoopResult(success=False, ...)     # L700 — 预算耗尽
```

关键参数：
- `DEFAULT_MAX_RETRIES = 3` → 📍 [sandbox.py:48](phase_2/orchestration/sandbox.py#L48)
- `DEFAULT_TIMEOUT_SECONDS = 30` → 📍 [sandbox.py:47](phase_2/orchestration/sandbox.py#L47)
- `_FIX_INSTRUCTION` → 📍 [sandbox.py:438-442](phase_2/orchestration/sandbox.py#L438-L442)："Adjust parameters to resolve the error."（匹配 §2.7 step 5 措辞）

💡 **为什么最后一次失败不调 LLM？** L663 的 `if attempt < max_retries` 保护——最后一次 sandbox 失败后没有下一次迭代来使用新代码，调 LLM 只浪费 token。

**规范偏差：**
- §2.7 terminal action 是 "log and skip"，代码返回 `RetryLoopResult(success=False)` 而非 `SkipResult`。`SkipResult` 存在于 `exceptions.py:372-387`，但仅在 stub 版 `retry_loop.py:orchestrate()` 中使用。两种返回类型尚未统一。

---

### SR-4: Conversation Accumulation Model（对话累积模型）

**规范定义（§2.7, deep-dive §3.2）：** 多轮、append-only 对话。`messages[0]` = system prompt（冻结），每次失败追加 `(assistant: script, user: code+traceback)` 对。max retries 时对话达 8 条消息。LLM 能看到**所有**先前失败尝试和 traceback。

**代码实现：**
- 📍 [sandbox.py:622-704](phase_2/orchestration/sandbox.py#L622-L704) — `run_retry_loop()` 内部

当前实现维护 `history: list[SandboxResult]`（L624）记录执行结果，但**不维护 LLM 对话历史**。每次 LLM 调用仅接收：
- `system_prompt`（冻结，同一字符串每次传入）
- `feedback_prompt`（仅**最近一次**失败的 code + traceback + fix instruction）

先前失败的历史**不会累积传递**给 LLM。

**规范偏差（重大）：**

| 维度 | §2.7 规范 | 实际代码 |
|---|---|---|
| 对话模型 | Append-only `list[dict]`，消息逐次增长 | 无状态，每次 LLM 调用只看当前失败 |
| LLM 可见历史 | 所有先前失败尝试 + traceback | 仅最近一次 |
| 最大消息数 | 8 条（1 system + 3×2 user/assistant + 1 final） | 始终 2 条（system + feedback） |
| 多轮学习能力 | LLM 可避免重复先前错误 | LLM 可能重蹈覆辙 |

stage4 中 `retry_loop.py` 的 `orchestrate()` 函数描述了完整的对话管理（"conversation history accumulates in-place"），但该函数目前是 stub。完整对话累积尚待实现。

---

### SR-5: Three Named Exception Types Consumed from M1（三个命名异常类型）

**规范定义（§2.7）：** M1 抛出 `CyclicDependencyError`、`UndefinedEffectError`、`NonRootDependencyError`，带结构化消息，M3 捕获后追加到 LLM 对话中。

**代码实现：**

**定义侧（M1 exceptions.py）：**

| 异常类 | 位置 | 构造参数 | 消息格式 |
|---|---|---|---|
| `CyclicDependencyError` | 📍 [exceptions.py:52-74](phase_2/exceptions.py#L52-L74) | `cycle_path: list[str]` | `"Measure 'cost' → 'satisfaction' → 'cost' forms a cycle."` |
| `UndefinedEffectError` | 📍 [exceptions.py:77-100](phase_2/exceptions.py#L77-L100) | `effect_name: str, missing_value: str` | `"'severity_surcharge' in formula has no definition for 'Severe'."` |
| `NonRootDependencyError` | 📍 [exceptions.py:103-126](phase_2/exceptions.py#L103-L126) | `column_name: str` | `"'department' is not a group root; cannot use in add_group_dependency."` |

三者均继承 `SimulatorError`，各自存储结构化字段（`cycle_path` / `effect_name` + `missing_value` / `column_name`）供 feedback formatter 编程访问。

**捕获侧（M3 sandbox.py）：**

- 📍 [sandbox.py:219-223](phase_2/orchestration/sandbox.py#L219-L223) — `_SandboxThread.run()` 中的 `except Exception as exc`

捕获**所有** `Exception` 子类，不区分 SDK 异常和非 SDK 异常。异常对象存入 `self.exception`，traceback 格式化为字符串存入 `self.traceback_str`。

**反馈格式化（M3 sandbox.py）：**

- 📍 [sandbox.py:445-529](phase_2/orchestration/sandbox.py#L445-L529) — `format_error_feedback(original_code, exception, traceback_str) -> str`

组装四段式反馈：`=== ORIGINAL CODE ===` → `=== ERROR ===`（异常类名 + 消息）→ `=== TRACEBACK ===` → `=== INSTRUCTION ===`（"Adjust parameters to resolve the error."）。清晰的节标题让 LLM 能无歧义地解析每个组件。

💡 **为什么消息要结构化？** 结构化错误消息（如 "Measure 'cost' → 'satisfaction' → 'cost' forms a cycle"）比裸 traceback 信息密度高得多。LLM 能从中直接读出环路路径并删除一条边。这是 Loop A 自我修正能力的核心——错误消息的质量直接决定 LLM 修正成功率。

**规范偏差：** 无。异常定义与 §2.7 示例格式精确匹配。

---

## 接口契约（已实现的）

### 入口：`render_system_prompt(scenario_context) -> str`

- **契约：** 接收非空场景字符串 → 返回完整 system prompt 字符串（scenario 已注入）
- **调用时机：** 每个场景执行一次，在 retry loop 启动前
- 📍 [prompt.py:207](phase_2/orchestration/prompt.py#L207) — `def render_system_prompt(scenario_context: str) -> str`

### 核心：`execute_in_sandbox(source_code, timeout, namespace?) -> SandboxResult`

- **契约：** 接收 Python 源码字符串 → 在受限 `exec()` 中编译执行 → 返回 `SandboxResult`（success + DataFrame/metadata 或 exception/traceback）
- **调用时机：** retry loop 每次迭代调用一次
- 📍 [sandbox.py:225](phase_2/orchestration/sandbox.py#L225) — `def execute_in_sandbox(source_code: str, timeout_seconds: int = 30, sandbox_namespace: dict | None = None) -> SandboxResult`

### 核心：`format_error_feedback(original_code, exception, traceback_str) -> str`

- **契约：** 接收失败代码 + 异常 + traceback → 返回四段式反馈字符串
- **调用时机：** 每次 sandbox 执行失败后、下一次 LLM 调用前
- 📍 [sandbox.py:445](phase_2/orchestration/sandbox.py#L445) — `def format_error_feedback(original_code: str, exception: Exception, traceback_str: str) -> str`

### 驱动：`run_retry_loop(initial_code, llm_generate_fn, system_prompt, ...) -> RetryLoopResult`

- **契约：** 接收初始代码 + LLM 调用函数 + system prompt → 驱动完整 §2.7 重试循环 → 返回 `RetryLoopResult`（成功含 DataFrame/metadata，失败含完整 history）
- **调用时机：** 由 pipeline 为每个场景调用一次
- 📍 [sandbox.py:536](phase_2/orchestration/sandbox.py#L536) — `def run_retry_loop(initial_code: str, llm_generate_fn: Callable, system_prompt: str, max_retries: int = 3, timeout_seconds: int = 30, sandbox_namespace_factory: Callable | None = None) -> RetryLoopResult`

### 辅助：`extract_clean_code(raw_response) -> str`

- **契约：** 接收 LLM 原始响应（可能含 markdown 围栏和散文）→ 返回净 Python 源码
- 📍 [code_validator.py:76](phase_2/orchestration/code_validator.py#L76) — `def extract_clean_code(raw_response: str) -> str`

### 辅助：`validate_generated_code(source_code) -> CodeValidationResult`

- **契约：** 接收 Python 源码 → AST 三重检查（语法 + `build_fact_table` 定义 + `.generate()` 调用）→ 返回 `CodeValidationResult`
- 📍 [code_validator.py:195](phase_2/orchestration/code_validator.py#L195) — `def validate_generated_code(source_code: str) -> CodeValidationResult`

---

## 关键约束与不变量

1. **Prompt 不可变性：** `SYSTEM_PROMPT_TEMPLATE` 是 `Final[str]`，运行时不可修改。每个场景的 prompt 由 `render_system_prompt()` 一次性渲染。
2. **每次执行全新 namespace：** `run_retry_loop` 每次迭代调用 `ns_factory()` 创建新的 `exec()` 命名空间，确保前次失败的部分 SDK 状态不污染下次尝试。
3. **受限 builtins：** `_SAFE_BUILTINS` 白名单排除 `__import__`、`eval`、`exec`、`open`，LLM 脚本只能使用预注入的 `FactTableSimulator` 和基本内置函数。
4. **超时保护：** 守护线程 + `join(timeout=30s)` 防止 LLM 生成的无限循环脚本挂起 pipeline。
5. **重试预算固定：** `max_retries=3`，不根据错误类型或数量动态调整。
6. **返回值验证：** `execute_in_sandbox` 验证 `build_fact_table()` 返回 `(DataFrame, dict)` 二元组，不合规则包装为失败 `SandboxResult`。

---

## 反馈回路参与

### Loop A：Code-Level Self-Correction（M3 ↔ M1）

**触发条件：** M1 SDK 在 sandbox 执行 LLM 脚本时抛出 typed exception（`CyclicDependencyError` / `UndefinedEffectError` / `NonRootDependencyError` 或其他 `Exception`）。

**M3 的角色：**
1. `_SandboxThread.run()` 捕获异常 → 📍 [sandbox.py:219-223](phase_2/orchestration/sandbox.py#L219-L223)
2. `execute_in_sandbox()` 包装为 `SandboxResult(success=False, exception, traceback_str)` → 📍 [sandbox.py:338-348](phase_2/orchestration/sandbox.py#L338-L348)
3. `run_retry_loop()` 检测失败 → 调用 `format_error_feedback()` 组装反馈 → 📍 [sandbox.py:665-669](phase_2/orchestration/sandbox.py#L665-L669)
4. 调用 `llm_generate_fn(system_prompt, feedback_prompt)` 获取修正代码 → 📍 [sandbox.py:682](phase_2/orchestration/sandbox.py#L682)
5. 下一迭代在全新 namespace 中执行修正代码

**代码路径：** `run_retry_loop` → `execute_in_sandbox` → `_SandboxThread.run()` → M1 raises → catch → `format_error_feedback` → `llm_generate_fn` → loop back

**状态：** 基本流程 SPEC_READY 已实现。对话累积（append-only 多轮）尚未实现（见 SR-4 偏差）。

---

## TODO 地图（NEEDS_CLAR）

### NC-1: Sandbox Execution Semantics（P1）

- **阻塞原因：** 隔离级别（`exec()` vs subprocess vs container）、超时机制、状态重置未被规范明确定义
- **代码当前状态：** **大部分已实现。** `exec()` in-process（[sandbox.py:206](phase_2/orchestration/sandbox.py#L206)），`threading.Thread` + `join(timeout=30s)`（[sandbox.py:313](phase_2/orchestration/sandbox.py#L313)），每次创建全新 namespace（[sandbox.py:637](phase_2/orchestration/sandbox.py#L637)）。stage4 TODO 注释仍在但功能实质就绪。
- **影响下游：** M3 自身 robust retry
- **stage3 建议：** 每次 retry 在新 `exec()` scope 中 instantiate 全新 `FactTableSimulator`，可配置 timeout，默认 30s → **已采纳**

### NC-2: Handling of Non-SDK Exceptions（P1）

- **阻塞原因：** §2.7 只讨论 typed SDK exceptions，`SyntaxError` / `NameError` 等非 SDK 异常处理未定义
- **代码当前状态：** **已实现。** `except Exception as exc`（[sandbox.py:219](phase_2/orchestration/sandbox.py#L219)）捕获所有异常，统一格式化 traceback。stage4 TODO 注释仍在但实际代码已覆盖。
- **影响下游：** M3 自身
- **stage3 建议：** 捕获所有 `Exception`，SDK 异常走结构化消息、其他走 raw traceback → **已采纳**

### NC-3: Multiple Simultaneous SDK Errors（P2）

- **阻塞原因：** 标准 Python 每次只抛一个异常，3 次 retry 对 3+ 独立错误可能不够
- **代码当前状态：** **未处理。** 无多错误收集机制，无 TODO 注释，无 stub。接受 one-at-a-time 限制。
- **影响下游：** M3 自身
- **stage3 建议：** 接受 one-at-a-time 为默认，M1 可选实现复合异常作为未来增强

### NC-4: Context Window Exhaustion Strategy（P2）

- **阻塞原因：** 3 轮重试累积 ~4 脚本 + 3 traceback，无截断/摘要策略
- **代码当前状态：** **未实现。** 无 token 计数或截断逻辑。stage4 在 retry_loop.py 注释了 TODO（[retry_loop.py:327](phase_2/orchestration/retry_loop.py)）但无代码。当前实现因不累积对话（SR-4 偏差），此问题实际被"绕过"——每次 LLM 调用只发两条消息，不会膨胀。
- **影响下游：** M3 自身
- **stage3 建议：** 3 次重试保留完整历史（大多数模型可承受），加 token-budget 检查

### NC-5: `build_fact_table` Function Signature Enforcement（P1）

- **阻塞原因：** §2.7 和 §2.9 假设函数名 `build_fact_table` + `seed` 参数，但 §2.5 HC 未列出此约束
- **代码当前状态：** **部分实现。** 函数名检查已有——sandbox 执行后检查 `namespace.get("build_fact_table")`（[sandbox.py:209-214](phase_2/orchestration/sandbox.py#L209-L214)），code_validator 做 AST 级 `def build_fact_table(...)` 检测（[code_validator.py:271-280](phase_2/orchestration/code_validator.py#L271-L280)）。但 `seed` 参数的存在性和默认值**不检查**。
- **影响下游：** M3, M5（`generate_with_validation(build_fn, ...)` 假设 seed 参数）
- **stage3 建议：** 添加显式硬约束 + AST 解析验证函数名和签名

### NC-6: Loop A Terminal Failure ↔ Upstream Orchestrator（P2）

- **阻塞原因：** "Log and skip" 意味着外层循环容忍单场景失败，但外层循环未在 Phase 2 规范中定义
- **代码当前状态：** **Stub。** `retry_loop.py:orchestrate()` 函数存在但是纯 stub（[retry_loop.py:20-50](phase_2/orchestration/retry_loop.py#L20-L50)），仅 log warning 并立即返回 `SkipResult`。`SkipResult` 已定义（[exceptions.py:372-387](phase_2/exceptions.py#L372-L387)）但 `run_retry_loop` 返回的是 `RetryLoopResult` 而非 `SkipResult`，两种返回类型尚未统一。
- **影响下游：** Pipeline 层
- **stage3 建议：** M3 入口返回 `None` 或 typed `SkipResult`，Pipeline orchestrator 检查并继续下个场景

---

## 实现细节（规范未覆盖的辅助代码）

| 代码位置 | 名称 | 用途 |
|---|---|---|
| 📍 [sandbox.py:55-110](phase_2/orchestration/sandbox.py#L55-L110) | `_SAFE_BUILTINS` | 受限 `__builtins__` 白名单，屏蔽 `__import__`/`eval`/`exec`/`open`/`compile` 等危险原语，保留构造器、类型转换、集合操作、常用异常类 |
| 📍 [sandbox.py:117-175](phase_2/orchestration/sandbox.py#L117-L175) | `_build_sandbox_namespace()` | 构建 `exec()` 全局命名空间：注入 `FactTableSimulator` + 自定义 `_restricted_import`（仅允许 SDK 别名路径） |
| 📍 [sandbox.py:144-161](phase_2/orchestration/sandbox.py#L144-L161) | `_restricted_import()` | Import 门控函数，仅允许 `chartagent.synth`、`phase_2.sdk.simulator` 等已知路径 |
| 📍 [sandbox.py:180-223](phase_2/orchestration/sandbox.py#L180-L223) | `_SandboxThread` | 守护线程类，`compile()` + `exec()` LLM 脚本后调用 `build_fact_table()`，异常和 traceback 存入实例属性 |
| 📍 [sandbox.py:350-430](phase_2/orchestration/sandbox.py#L350-L430) | `execute_in_sandbox()` 返回值验证段 | 验证 `build_fact_table()` 返回值为 `(DataFrame, dict)` 二元组：检查 None、非 tuple、长度不为 2、元素类型不匹配，每种情况格式化为结构化错误 |
| 📍 [code_validator.py:36-53](phase_2/orchestration/code_validator.py#L36-L53) | `CodeValidationResult` | frozen dataclass：`is_valid`, `has_build_fact_table`, `has_generate_call`, `errors: list[str]` |
| 📍 [code_validator.py:62-73](phase_2/orchestration/code_validator.py#L62-L73) | 围栏正则 | `_FENCED_BLOCK_RE`、`_LEADING_FENCE_RE`、`_TRAILING_FENCE_RE`——从 LLM 响应剥离 markdown 代码围栏 |
| 📍 [code_validator.py:76-152](phase_2/orchestration/code_validator.py#L76-L152) | `extract_clean_code()` | 三级优先策略提取净代码：完整围栏块 → 首尾围栏 → 裸代码 |
| 📍 [code_validator.py:159-193](phase_2/orchestration/code_validator.py#L159-L193) | `_GenerateCallVisitor` / `_BuildFactTableVisitor` | AST 访问器：检测 `.generate()` 方法调用和 `def build_fact_table()` 函数定义 |
| 📍 [code_validator.py:195-309](phase_2/orchestration/code_validator.py#L195-L309) | `validate_generated_code()` | AST 三重检查（语法 → 函数定义 → generate 调用），一次性收集所有错误 |
| 📍 [types.py:413-431](phase_2/types.py#L413-L431) | `SandboxResult` | dataclass：`success`, `dataframe`, `metadata`, `exception`, `traceback_str` |
| 📍 [types.py:433-448](phase_2/types.py#L433-L448) | `RetryLoopResult` | dataclass：`success`, `dataframe`, `metadata`, `attempts`, `history: list[SandboxResult]` |
| 📍 [exceptions.py:372-387](phase_2/exceptions.py#L372-L387) | `SkipResult` | sentinel dataclass（非异常）：`scenario_id`, `error_log`——pipeline 通过 `isinstance()` 检查跳过信号 |
| 📍 [retry_loop.py:20-50](phase_2/orchestration/retry_loop.py#L20-L50) | `orchestrate()` stub | 目标架构入口，当前仅 log warning 并返回 SkipResult，待集成 prompt + validator + sandbox |
