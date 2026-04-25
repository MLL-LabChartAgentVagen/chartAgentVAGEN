# Phase 2 跨模块数据流追踪

本文档沿**流水线执行顺序**（M3→M1→M2∥M4→M5），横向追踪每条模块间数据传递的发送方接口、接收方接口、数据类型、可变性、传递机制和实现状态。同时追踪两条反馈回路和 NEEDS_CLAR 跨模块阻塞传播链。

**阅读前提：** 已完成全部 6 份 S1 模块画像的精读。

---

## 一、正向流水线（执行顺序视角）

### 1.1 Phase 1 → M3：场景上下文传入

| 维度 | 详情 |
|---|---|
| **发送方** | Phase 1（Phase 2 外部系统） |
| **接收方** | M3 — `render_system_prompt(scenario_context: str) -> str` 📍 `prompt.py:207` |
| **数据类型** | `str`（场景描述字符串，包含 title, entities, metrics, temporal grain, target_rows） |
| **可变性** | Read-only——注入 prompt 模板后不再修改 |
| **传递机制** | 函数调用参数。`str.replace("{scenario_context}", scenario_context)` 📍 `prompt.py:252-253` 一次性替换 |
| **实现状态** | ✅ SPEC_READY |

**规范偏差：** §2.5 描述 Phase 1 输出为 `dict`（含 title, entities, metrics 等字段），但 M3 的 `render_system_prompt()` 接收 `str` 而非 `dict`。dict→str 的序列化由调用方负责，Phase 2 代码中未定义此转换。

**渲染后流向：** 渲染完成的 system prompt 字符串被传递给 `run_retry_loop()` 📍 `sandbox.py:536` 的 `system_prompt` 参数，在每次 LLM 调用中作为**不变的系统消息**重复使用。

---

### 1.2 M3 → M1：Python 脚本传递与执行

| 维度 | 详情 |
|---|---|
| **发送方** | M3 — LLM 生成的 Python 源码字符串（经 `extract_clean_code()` 📍 `code_validator.py:76` 清洗） |
| **接收方** | M1 — `FactTableSimulator` 类的方法，在 sandbox `exec()` 内被脚本调用 |
| **数据类型** | `str`（Python 源码），内含 `build_fact_table()` 函数定义 |
| **可变性** | 每次 Loop A 迭代重新生成（旧脚本丢弃） |
| **传递机制** | **间接调用**——非函数传参，而是 `exec()` 执行 |
| **实现状态** | ✅ SPEC_READY |

**执行链（4 步）：**

1. **Namespace 构建** 📍 `sandbox.py:117-175` — `_build_sandbox_namespace()` 创建受限全局命名空间：
   - 注入 `_SAFE_BUILTINS`（屏蔽 `__import__/eval/exec/open`）📍 `sandbox.py:55-110`
   - 预注入 `FactTableSimulator` 类 📍 `sandbox.py:139-140`
   - 安装 `_restricted_import()` 📍 `sandbox.py:144-161`，仅允许 SDK 路径

2. **编译执行** 📍 `sandbox.py:200-206` — `_SandboxThread.run()` 中 `compile()` + `exec()`。脚本中的 `sim = FactTableSimulator(target_rows, seed)` 和所有 `add_*/declare_*/inject_*` 调用**同步触发 M1 声明时验证**。

3. **触发生成** 📍 `sandbox.py:209-217` — sandbox 从 namespace 取出 `build_fact_table` 函数并调用 `build_fn()`（内部调用 `sim.generate()`）。

4. **结果验证** 📍 `sandbox.py:350-430` — `execute_in_sandbox()` 验证返回值为 `(DataFrame, dict)` 二元组，包装为 `SandboxResult`。

**关键特征：** M3→M1 不是典型的函数调用传参——M3 传递的是**源码文本**，M1 被动接收的是**方法调用序列**。两者通过 `exec()` 的 namespace 间接耦合。

---

### 1.3 M1 → M2 / M4：声明存储分发

这是最关键的模块边界——M1 将声明存储一次性分发给生成和元数据两条路径。

#### 1.3a M1 → M2：声明存储 → 生成引擎

| 维度 | 详情 |
|---|---|
| **发送方** | M1 — `FactTableSimulator.generate()` 📍 `simulator.py:130-141` |
| **接收方** | M2 — `run_pipeline()` 📍 `generator.py:27-37` |
| **数据类型** | 8 个解包参数 |
| **可变性** | 语义冻结——声明完成后不应修改（但 `DeclarationStore.freeze()` **未被显式调用**） |
| **传递机制** | 同步函数调用，关键字参数，**共享对象引用**（无防御性拷贝） |
| **实现状态** | ✅ SPEC_READY |

**数据分解：**

| 参数名 | 类型 | 发送方位置 | 接收方位置 |
|---|---|---|---|
| `columns` | `OrderedDict[str, dict]` | `simulator.py:132` `self._columns` | `generator.py:28` |
| `groups` | `dict[str, DimensionGroup]` | `simulator.py:133` `self._groups` | `generator.py:29` |
| `group_dependencies` | `list[GroupDependency]` | `simulator.py:134` | `generator.py:30` |
| `measure_dag` | `dict[str, list[str]]` | `simulator.py:135` | `generator.py:31` |
| `target_rows` | `int` | `simulator.py:136` `self.target_rows` | `generator.py:32` |
| `seed` | `int` | `simulator.py:137` `self.seed` | `generator.py:33` |
| `patterns` | `list[dict] \| None` | `simulator.py:138` `self._patterns` | `generator.py:34` |
| `realism_config` | `dict \| None` | `simulator.py:139` | `generator.py:35` |

**规范偏差：**
- Stage4 设计传递单一 `DeclarationStore` 对象，实际传递**解包的 8 个独立参数**。
- `DeclarationStore.freeze()` 📍 `types.py:397-401` 已定义但 `generate()` **未调用**——冻结是隐式约定而非强制保护。
- `generate()` 不传递 `overrides`（M2 签名中有但 M1 不提供）——仅在 Loop B 重试时由外部注入。

#### 1.3b M1 → M4：声明存储 → 元数据构建

| 维度 | 详情 |
|---|---|
| **发送方** | **M2 内部**——`run_pipeline()` 📍 `generator.py:102-126` |
| **接收方** | M4 — `build_schema_metadata()` 📍 `builder.py:23-31` |
| **数据类型** | 7 个参数 |
| **可变性** | 只读——M4 对所有返回值做防御性拷贝 |
| **传递机制** | 函数调用，关键字参数 |
| **实现状态** | ⚠️ 接口就位但存在数据丢失 |

**重大发现——M4 并非由 M1 直接调用，而是被 M2 的 `run_pipeline()` 在 return path 上调用：**

```python
# generator.py:118-126
metadata = _build_meta(
    groups=groups,
    orthogonal_pairs=[],  # ← 硬编码空列表！
    target_rows=target_rows,
    measure_dag_order=list(measure_order),
    columns=columns,
    group_dependencies=group_dependencies,
    patterns=patterns,
)
```

**`orthogonal_pairs` 数据丢失的影响链：**

| 影响点 | 后果 |
|---|---|
| `schema_metadata["orthogonal_groups"]` | 始终为 `[]` |
| M5 `check_orthogonal_independence()` | 遍历为空 → **跳过所有 χ² 检验** |
| Phase 3 | 无法得知哪些组被声明为正交 |

**原因：** `run_pipeline()` 签名 📍 `generator.py:27-37` 不包含 `orthogonal_pairs` 参数（它不影响 M2 的行生成逻辑，属于纯元数据），但 M4 在 M2 内部被调用时需要它。M1 的 `_build_schema_metadata()` 📍 `simulator.py:143-152` 正确传递了 `orthogonal_pairs`，但该方法是**死代码**——`generate()` 从未调用它。

---

### 1.4 M2∥M4 并行点分析

| 维度 | 规范设计 | 代码实际 |
|---|---|---|
| **执行时序** | M2∥M4 并行——M4 不需要 DataFrame | M4 在 M2 的 return path **串行执行** 📍 `generator.py:102` |
| **数据来源** | 各自从 DeclarationStore 读取 | **共享同一批对象引用**（M1 传入 `run_pipeline()` 的参数） |
| **独立性** | 完全独立——M4 只需声明结构 | 实际也独立——M4 不读 `df`，只读 `groups/columns/deps/patterns` |
| **可并行化改造** | ✅ 设计支持 | ❌ 代码未实现（但因共享引用而非拷贝，改造成本低） |

**数据安全性：** M2 传给 M4 的参数是与 M2 自身使用的**完全相同的对象引用**。但不存在竞态风险——M4 的 `build_schema_metadata()` 对所有集合做防御性拷贝（`list()`, `dict()`, `_deep_copy_param_model()`），返回的 metadata dict 与源数据完全解耦 📍 `builder.py:59-102`。

---

### 1.5 M2 内部四阶段数据变换

虽非模块间传递，但理解 M2 内部数据形态变化对追踪 M2→M5 输出至关重要。

| 阶段 | 输入数据形态 | 输出数据形态 | 代码位置 | 状态 |
|---|---|---|---|---|
| **Pre-flight** | columns, groups, deps, dag | `topo_order: list[str]` | `generator.py:73-76` | ✅ |
| **α Skeleton** | columns, target_rows, deps, topo_order, rng | `rows: dict[str, np.ndarray]`（仅非度量列） | `skeleton.py:31` | ✅ |
| **β Measures** | columns, topo_order, rows, rng, overrides | `rows: dict[str, np.ndarray]`（**stub: 原样返回**） | `measures.py:19` | ⛔ |
| **τ_post** | rows, topo_order, columns, target_rows | `df: pd.DataFrame` | `postprocess.py:19` | ✅ |
| **γ Patterns** | df, patterns, columns, rng | `df: pd.DataFrame`（in-place 修改） | `patterns.py:29` | ✅ 2/6 类型 |
| **δ Realism** | df, realism_config, columns, rng | `df: pd.DataFrame`（in-place 修改） | `realism.py:25` | ⚠️ 部分 |

**数据形态切换点：** `dict[str, np.ndarray]` → `pd.DataFrame` 发生在 β 和 γ 之间（τ_post）。α/β 操作列式 numpy 数组（高效批量采样），γ/δ 需要 DataFrame（`df.eval()` 和 `df.loc[]` 做子集操作）。规范数学表达 `M = τ_post ∘ δ ∘ γ ∘ β ∘ α(seed)` 中 τ_post 在最外层，但代码将它提前到 γ 之前——功能等价但数据结构在中间切换。

**单一 RNG 线性消耗：** `rng = np.random.default_rng(seed)` 📍 `generator.py:70` 按引用传入每个阶段，消耗顺序：α（大量 `rng.choice`）→ β（stub，不消耗）→ γ（当前两种注入均为确定性数学运算，不消耗）→ δ（`rng.random()` 用于 missing/dirty mask）。

---

### 1.6 M2 + M4 → M5：DataFrame + metadata 汇合

| 维度 | 详情 |
|---|---|
| **发送方** | M2 输出 `df: pd.DataFrame`，M4（经由 M2）输出 `metadata: dict` |
| **接收方** | M5 — `SchemaAwareValidator.__init__(meta)` 📍 `validator.py:40-46` + `validate(df, patterns)` 📍 `validator.py:48-83` |
| **数据类型** | `pd.DataFrame` + `dict[str, Any]`（7-key metadata）+ `list[dict]`（patterns，可选） |
| **可变性** | DataFrame 是 M2 最终输出（γ/δ 已 in-place 修改完毕）；metadata 是防御性拷贝（不可变语义） |
| **传递机制** | ⚠️ **当前无自动传递管道** |
| **实现状态** | ⚠️ 组件各自就绪，管道缺失 |

**管道断裂追踪：**

```
run_pipeline() 返回 (df, metadata)           📍 generator.py:133
  ↓
FactTableSimulator.generate() 透传返回       📍 simulator.py:141
  ↓
_SandboxThread.run() 存入 self.result        📍 sandbox.py:217
  ↓
execute_in_sandbox() 包装为 SandboxResult     📍 sandbox.py:426-430
  ↓
run_retry_loop() 包装为 RetryLoopResult       📍 sandbox.py:651-657
  ↓
⛔ 到此为止。没有代码将 DataFrame + metadata 传给 SchemaAwareValidator。
```

`generate_with_validation()` 应承担此桥接角色（stage4 设计签名：`generate_with_validation(generate_fn, store, meta, base_seed, max_retries=3)`），但**尚未实现**。

**M5 的接口设计是正确的：** `SchemaAwareValidator(meta)` 构造时持有 `meta` 的不可变引用，`validate(df, patterns)` 接收 DataFrame 和可选 patterns。M5 **不直接访问 DeclarationStore**，仅通过 metadata dict 间接读取声明——模块边界清晰。

---

### 1.7 M5 → Phase 3：验证后输出

| 维度 | 详情 |
|---|---|
| **发送方** | M5 — `validate()` 📍 `validator.py:48-83` 返回 `ValidationReport` |
| **接收方** | Phase 3（外部系统） |
| **数据类型** | 三元组 `(DataFrame, schema_metadata, ValidationReport)` |
| **传递机制** | ⚠️ Pipeline 层尚未实现 |
| **实现状态** | ⚠️ 数据结构就绪，输出管道缺失 |

`ValidationReport` 📍 `types.py:253-306` 包含 `checks: list[Check]`、`all_passed: bool`、`failures: list[Check]`。Phase 3 应接收验证后的三元组，但当前无 pipeline 代码组装此最终产出。

---

### 1.8 正向流水线状态矩阵

| # | 传递 | 发送方接口 | 接收方接口 | 数据类型 | 机制 | 状态 |
|---|---|---|---|---|---|---|
| 1 | Phase 1 → M3 | (外部) | `prompt.py:207` | `str` | 函数调用 | ✅ |
| 2 | M3 → M1 | `sandbox.py:638-642` | (exec 内 SDK 方法) | `str`→方法调用 | `exec()` | ✅ |
| 3 | M1 → M3 | `exceptions.py:52-126` | `sandbox.py:219-223` | `Exception` | 异常冒泡 | ✅ |
| 4 | M1 → M2 | `simulator.py:130-141` | `generator.py:27-37` | 8 个解包参数 | 函数调用 | ✅ |
| 5 | M1 → M4 | `generator.py:118-126` | `builder.py:23-31` | 7 个参数 | 函数调用（M2内） | ⚠️ `orthogonal_pairs=[]` |
| 6 | M2 → M5 | `generator.py:133` | `validator.py:48` | `DataFrame` | **管道缺失** | ⚠️ |
| 7 | M4 → M5 | `generator.py:133` | `validator.py:40` | `dict` | **管道缺失** | ⚠️ |
| 8 | M5 → M2 | `autofix.py:46-158` | `generator.py:36` overrides | 调整后参数 | **循环缺失** | ⚠️ |
| 9 | M5 → Phase 3 | `validator.py:83` | (外部) | `ValidationReport` | **管道缺失** | ⚠️ |

---

## 二、反馈回路

### 2.1 Loop A：代码级自我修正（M3 ↔ M1）

Loop A 是**外层循环**——M1 声明时验证失败时触发，LLM 重新生成脚本修正语义错误。Loop B 仅在 Loop A 成功后才进入。

#### 异常抛出路径

```
LLM 脚本 (exec 内)
  ├─ sim.add_category(...)   ← M1 验证逻辑触发
  │     └─ 验证失败 → raise SimulatorError 子类
  ▼
_SandboxThread.run()         📍 sandbox.py:200-223
  except Exception as exc:   📍 sandbox.py:219（通杀捕获，不区分 SDK/非 SDK）
    self.exception = exc     📍 sandbox.py:222
    self.traceback_str = traceback.format_exc()  📍 sandbox.py:223
  ▼
execute_in_sandbox()         📍 sandbox.py:225-430
  return SandboxResult(success=False, exception, traceback_str)  📍 sandbox.py:344-348
  ▼
run_retry_loop()             📍 sandbox.py:629-704
  result.success == False → 进入反馈准备  📍 sandbox.py:663
```

**9 种可抛出的 SDK 异常：**

| 异常类 | 触发文件 | 异常定义位置 | 结构化字段 |
|---|---|---|---|
| `CyclicDependencyError` | `sdk/dag.py` | `exceptions.py:52-74` | `cycle_path: list[str]` |
| `UndefinedEffectError` | `sdk/validation.py` | `exceptions.py:77-100` | `effect_name, missing_value` |
| `NonRootDependencyError` | `sdk/validation.py` | `exceptions.py:103-126` | `column_name` |
| `InvalidParameterError` | `sdk/validation.py` 等 | `exceptions.py:134-159` | `param_name, value, reason` |
| `DuplicateColumnError` | `sdk/validation.py` | `exceptions.py:162-182` | `column_name` |
| `EmptyValuesError` | `sdk/columns.py` | `exceptions.py:185-203` | `column_name` |
| `WeightLengthMismatchError` | `sdk/validation.py` | `exceptions.py:206-228` | `column_name, n_values, n_weights` |
| `ParentNotFoundError` | `sdk/validation.py` | `exceptions.py:254-276` | `child_name, parent_name, group` |
| `DuplicateGroupRootError` | `sdk/columns.py` | `exceptions.py:279-304` | `group_name, existing_root, attempted_root` |

全部继承 `SimulatorError` 📍 `exceptions.py:39-47`，携带精确的错误定位信息。

#### 反馈格式化与 LLM 重新提示

**Step 1 — 格式化：** `format_error_feedback()` 📍 `sandbox.py:445-529` 组装四段式反馈：

```
=== ORIGINAL CODE ===
{失败的脚本全文}

=== ERROR ===
Exception: CyclicDependencyError: Measure 'cost' → 'satisfaction' → 'cost' forms a cycle.

=== TRACEBACK ===
{完整 traceback}

=== INSTRUCTION ===
The script above raised an error during sandbox execution. Adjust parameters to resolve the error. Return only the corrected Python script.
```

`_FIX_INSTRUCTION` 📍 `sandbox.py:438-442` 匹配 §2.7 step 5 措辞。

**Step 2 — LLM 调用：** 📍 `sandbox.py:682`

```python
current_code = llm_generate_fn(system_prompt, feedback_prompt)
```

`llm_generate_fn` 是注入的 callable，接收 `(system_prompt, user_prompt)` 返回新脚本。

**Step 3 — 全新 namespace 重新执行：** 📍 `sandbox.py:637`

```python
sandbox_ns = ns_factory()   # ← 全新 exec() 命名空间，前次 SDK 状态不污染
```

#### max_retries 计数器

| 常量/变量 | 值 | 位置 |
|---|---|---|
| `DEFAULT_MAX_RETRIES` | `3` | `sandbox.py:48` |
| 循环控制 | `for attempt in range(1, max_retries + 1)` | `sandbox.py:629` |
| 最后一次保护 | `if attempt < max_retries`——最后一次失败不调 LLM | `sandbox.py:663` |
| 执行历史 | `history: list[SandboxResult]` | `sandbox.py:624` |

#### Loop A 路径实现状态

| 路径 | 状态 | 位置 |
|---|---|---|
| M1 异常抛出（全部 9 种） | ✅ SPEC_READY | `exceptions.py`, `sdk/*.py` |
| 沙箱捕获 + SandboxResult 包装 | ✅ SPEC_READY | `sandbox.py:219-348` |
| 四段式反馈格式化 | ✅ SPEC_READY | `sandbox.py:445-529` |
| LLM 调用 callable 接口 | ✅ 就绪 | `sandbox.py:682` |
| namespace 状态重置 | ✅ SPEC_READY | `sandbox.py:637` |
| 重试循环框架 | ✅ SPEC_READY | `sandbox.py:629-704` |
| **对话累积（append-only 多轮）** | ⚠️ **未实现** | §2.7 要求 LLM 看到全部历史，代码仅传最近一次失败 |
| **`orchestrate()` 高层入口** | ⚠️ **stub** | `retry_loop.py:20-50` 仅返回 SkipResult |
| **`SkipResult` vs `RetryLoopResult` 统一** | ⚠️ **未统一** | 两种返回类型共存 |

**对话累积偏差：** 规范 §2.7 要求 append-only 对话——LLM 每次能看到**所有**先前失败尝试。当前 `run_retry_loop()` 每次只传最近一次失败的 feedback，不累积历史。这意味着 LLM 可能在 attempt 3 重蹈 attempt 1 的覆辙。`retry_loop.py` 中设计了完整对话管理的 `orchestrate()`，但该函数是 stub。

---

### 2.2 Loop B：统计自动修复（M5 → M2）

Loop B 是**内层循环**——生成的 DataFrame 通过 M5 验证失败时，通过参数调整 + 新 seed 重新执行 M2，无需 LLM 参与。

#### AUTO_FIX 分发表

**匹配器：** `match_strategy(check_name, auto_fix)` 📍 `autofix.py:25-43` 使用 `fnmatch.fnmatch` 按声明顺序匹配第一个 glob 模式，返回策略函数。

**设计中的分发映射（stage4 规划，未编码）：**

| Glob Pattern | 策略函数 | 目标失败检查 |
|---|---|---|
| `ks_*` | `widen_variance` | L2 KS 检验失败 |
| `orthogonal_*` | `reshuffle_pair` | L1 正交独立性失败 |
| `outlier_*` | `amplify_magnitude` | L3 outlier entity 失败 |
| `trend_*` | `amplify_magnitude` | L3 trend break 失败 |

#### 三个已实现的策略函数

**a) `widen_variance`** 📍 `autofix.py:46-82` — 放大方差

- 输入：`Check` + `params: dict[str, float]` + `factor=1.2`
- 操作：`params["sigma"]` 或 `params["scale"]` 乘以 factor
- 输出：新 `dict`（不修改原始）
- 适用：KS 检验失败 → σ 太小 → 放大方差

**b) `amplify_magnitude`** 📍 `autofix.py:85-123` — 放大模式幅度

- 输入：`Check` + `pattern_spec: dict` + `factor=1.3`
- 操作：`pattern_spec["params"]["z_score"]` 或 `["magnitude"]` 乘以 factor
- 输出：`copy.deepcopy` 后的新 pattern spec
- 适用：L3 outlier/trend 失败 → 信号不足 → 放大注入

**c) `reshuffle_pair`** 📍 `autofix.py:126-158` — 打乱列破坏虚假相关

- 输入：`Check` + `df: DataFrame` + `column: str` + `rng`
- 操作：`rng.permutation()` 打乱指定列
- 输出：`df.copy()` 后的新 DataFrame
- 适用：χ² 失败 → 直接打乱列值
- 特殊性：直接操作 DataFrame 而非"修改参数→重新生成"

三个策略均为**纯函数**——接收旧参数/数据，返回新参数/数据，不修改外部状态。

#### 重新调用 generate() 的设计路径

```
M5 validate() → 失败
   ↓
match_strategy(check.name, AUTO_FIX)  ← ✅ 已实现
   ↓
strategy_fn(check, params/pattern/df)  ← ✅ 三个策略已实现
   ↓
ParameterOverrides 聚合               ← ❌ 未实现
   ↓
run_pipeline(seed=base_seed+attempt,   ← ✅ 签名就绪
             overrides=overrides)
  └─ generate_measures(overrides=...)  ← ✅ 签名就绪（stub 不消耗）
   ↓
M5 再次 validate()                    ← ✅ 可调用
   ↓
重复最多 3 次
```

#### Loop B 已就绪 vs 缺失组件

| 组件 | 状态 | 位置 |
|---|---|---|
| M5 `validate()` 返回 `ValidationReport` | ✅（L1 部分 + L3 部分） | `validator.py:48-83` |
| `report.all_passed` / `report.failures` | ✅ | `types.py:269-292` |
| `match_strategy()` glob 匹配 | ✅ | `autofix.py:25-43` |
| 三个策略函数 | ✅ 纯函数就绪 | `autofix.py:46-158` |
| `run_pipeline(overrides=...)` 签名 | ✅ 参数已声明 | `generator.py:36` |
| `generate_measures(overrides=...)` 签名 | ✅ 签名已声明（stub 不用） | `measures.py:24` |
| **`generate_with_validation()` 循环** | **❌ 未实现** | Stage4 设计签名在 autofix.py |
| **`AUTO_FIX` 默认分发表实例化** | **❌ 未编码** | — |
| **`ParameterOverrides` 数据结构** | **❌ 未定义** | — |
| **seed 偏移逻辑** | **❌ 未编码** | — |
| **策略输出 → overrides 格式适配** | **❌ 未编码** | — |
| L2 统计验证（KS/residual/transition） | ⛔ stub | `statistical.py:55-102` |

---

### 2.3 嵌套关系

```
┌─── Loop A (外层，max 3，含 LLM 调用) ────────────────────────────────────┐
│                                                                            │
│  M3 渲染 prompt → LLM 生成脚本 → Sandbox exec → M1 声明时验证             │
│    成功 ↓                                     失败 → 异常 → 反馈 → LLM    │
│                                                                            │
│  M1.generate() → M2 run_pipeline() → (df, metadata)                       │
│                                                                            │
│  ┌─── Loop B (内层，max 3，无 LLM 调用) ──────────────────────┐           │
│  │                                                              │           │
│  │  M5 validate(df, patterns) → ValidationReport               │           │
│  │    全通过 → 返回 (df, metadata, report)                      │           │
│  │    失败 → match_strategy → 策略调参                          │           │
│  │         → run_pipeline(seed+attempt, overrides) → M5 再验证  │           │
│  │                                                              │           │
│  └──────────────────────────────────────────────────────────────┘           │
│                                                                            │
│  Loop B 产出 (df, metadata, report) → Phase 3                             │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

**关键约束：**
1. Loop B **仅在 Loop A 成功后**执行。M1 验证失败时异常回传 M3 走 Loop A。
2. Loop B 不修改声明（store 只读），仅通过 `overrides` 调整参数。因此 M4 的 metadata **不需要在 Loop B 中重建**——声明未变，元数据不变。
3. **当前实际行为：** 由于 Loop B 循环框架未实现且度量生成为 stub，`generate()` 总是"成功"返回仅含 skeleton 列的 DataFrame。整个 Loop B 路径事实上不可触发。

---

## 三、NEEDS_CLAR 跨模块阻塞图

数据来源：`stage3_readiness_audit.md` Cross-Module Blockers 表。对每个 P0/P1 阻塞项，追踪源头文件 → 受影响文件 → 解除后修改范围。

### P0-1：Enrich `schema_metadata`（M4 + M5）

**阻塞描述：** §2.6 metadata 示例是 lossy projection，缺少 M5 校验所需的完整字段。

**源头：** 📍 `metadata/builder.py:114-175` — `_build_columns_metadata()`

**当前状态：已解决。** M4 的 builder 已包含全部 enriched 字段——docstring 标注 "Enriched beyond §2.6 example"：
- categorical 列: `values`, `weights`, `cardinality` 📍 `builder.py:138-143`
- stochastic measure: 完整 `param_model`（deepcopy）📍 `builder.py:157-165`
- structural measure: `formula`, `effects`, `noise` 📍 `builder.py:166-171`
- `group_dependencies`: 含 `conditional_weights` 📍 `builder.py:70-75`
- `patterns`: 含完整 `params` 📍 `builder.py:88-100`

**下游受益/残余阻塞：**

| M5 检查函数 | 需要的 enriched 字段 | M4 是否提供 | M5 函数状态 |
|---|---|---|---|
| `check_marginal_weights` | `values`, `weights` | ✅ | ❌ 函数未编写 |
| `check_measure_finiteness` | `type == "measure"` | ✅ | ❌ 函数未编写 |
| `check_stochastic_ks` | `param_model` | ✅ | ⛔ stub |
| `check_structural_residuals` | `formula`, `noise` | ✅ | ⛔ stub |
| `check_group_dependency_transitions` | `conditional_weights` | ✅ | ⛔ stub |
| `check_outlier_entity` | pattern `params` | ✅（直接从 pattern 读） | ✅ 已工作 |
| `check_trend_break` | `dimension_groups["time"]` | ✅ | ✅ 已工作 |

**解除后需修改：** `structural.py`（2 个新函数）、`statistical.py`（3 个 stub → 实现）、`validator.py`（注册 L2 调用）

---

### P0-2：Formula Evaluation Mechanism（M1 + M2）

**阻塞描述：** 结构性度量的公式字符串运行时求值器未定义。

**源头：** 📍 `engine/measures.py:84-99` — `_eval_structural()` → `raise NotImplementedError`

**传播路径：**

```
M1 (声明时)                  M2 (生成时)                     M5 (校验时)
columns.py:253-321           measures.py:84-99                statistical.py:72-86
extract_formula_symbols ✅    _eval_structural ❌               check_structural_residuals ❌
符号提取+DAG 边 ✅             运行时公式求值 ❌                  需公式求值计算预测值 ❌
```

**受影响文件：**

| 文件 | 当前状态 | 解除后需修改 |
|---|---|---|
| `engine/measures.py` | `_eval_structural()` NotImplementedError | 实现 `_evaluate_formula()` 受限 AST walker |
| `engine/measures.py` | `_sample_stochastic()` NotImplementedError | 实现 θⱼ=β₀+Σβₘ(Xₘ) 参数计算 + 分布采样 |
| `validation/statistical.py` | `check_structural_residuals()` NotImplementedError | 调用同一求值器计算预测值 |
| 可能新增 | — | `engine/formula_evaluator.py`（共享求值器，M2 和 M5 共用） |

**Stage3 建议：** 受限 AST 表达式求值器，仅允许 `+`/`-`/`*`/`/`/`**`、数字字面量和变量名。无函数调用，无属性访问。

---

### P0-3：Auto-fix Mutation Semantics（M2 + M5）

**阻塞描述：** Loop B auto-fix 调整参数时，冻结的 store 如何接受变更？

**源头：** 📍 `validation/autofix.py` — 三个策略函数产出新参数，但无消费者。

**传播路径：**

```
autofix.py:46-158          generator.py:36              measures.py:24
(策略产出新参数)              (overrides 签名就绪)           (overrides 签名就绪，stub不用)
       ✅                          ✅                           ✅

         ↓ 缺失环节 ↓

generate_with_validation()  →  ParameterOverrides 聚合  →  overrides 消费逻辑
         ❌                          ❌                          ❌
```

**设计决策（已确认）：** DeclarationStore **只读不变**——所有 auto-fix 变异走 `overrides` 叠加层。M4 metadata 不需重建。

**解除后需修改：** `autofix.py`（循环框架 + 分发表）、可能新增 `ParameterOverrides` 类、`measures.py`（overrides 消费逻辑）

---

### P1-1：`mixture` 分布 `param_model` Schema（M1 + M2 + M5）

**传播：**

```
M1 sdk/validation.py:274-287    →  M2 engine/measures.py:66-81    →  M5 validation/statistical.py:55-69
SUPPORTED_FAMILIES 含 "mixture"    _sample_stochastic() stub          check_stochastic_ks() stub
param_model 不验证 ⚠️               不区分 family ❌                     需重构理论分布 ❌
```

**解除后需修改：** `validation.py`（参数验证）、`measures.py`（采样）、`statistical.py`（KS test）

---

### P1-2：4 种欠规范 Pattern 类型（M1 + M2 + M5）

**传播：**

| 类型 | M1 `relationships.py` | M2 `patterns.py` | M5 `pattern_checks.py` |
|---|---|---|---|
| `ranking_reversal` | ⚠️ 无参数校验 | ❌ 无注入代码 | ❌ 静默跳过 |
| `dominance_shift` | ⚠️ 无参数校验 | ❌ 无注入代码 | ❌ 静默跳过 |
| `convergence` | ⚠️ 无参数校验 | ❌ 无注入代码 | ❌ 静默跳过 |
| `seasonal_anomaly` | ⚠️ 无参数校验 | ❌ 无注入代码 | ❌ 静默跳过 |

**解除后需修改：** `relationships.py`（参数 schema）、`patterns.py`（注入算法）、`pattern_checks.py`（验证）、`validator.py:_run_l3`（注册）

---

### P1-3：Sandbox 语义（M3 内部闭合）

**当前状态：大部分已解决。** `exec()` in-process ✅、守护线程+timeout ✅、全新 namespace ✅、通杀捕获 ✅。残余：对话累积未实现。

---

### 跨模块阻塞传播总图

```
P0-1 (Metadata Enrichment)          P0-2 (Formula Evaluator)           P0-3 (Auto-fix Semantics)
  │                                    │                                   │
  ├─ builder.py ✅ 已解决              ├─ columns.py ✅ 符号提取           ├─ autofix.py ✅ 策略函数
  │                                    ├─ measures.py ❌ _eval_structural  ├─ autofix.py ❌ 循环框架
  ├─ structural.py ❌ marginal/finite  ├─ measures.py ❌ _sample_stoch.    ├─ measures.py ❌ overrides消费
  ├─ statistical.py ❌ 全部 stub       ├─ statistical.py ❌ residuals      │
  └─ validator.py ⚠️ 缺 L2 调用        └─ (需共享 formula evaluator)       └─ (需 ParameterOverrides)
                                             │
                 ┌───────────────────────────┘
                 ▼
         P0-2 和 P0-3 在 measures.py 交汇：
         _sample_stochastic() 和 _eval_structural() 需要同时：
         (a) 公式/分布求值能力 ← P0-2
         (b) overrides 叠加逻辑 ← P0-3

P1-1 (mixture schema)               P1-2 (4 种 Pattern)
  │                                    │
  ├─ validation.py ⚠️ 无验证           ├─ relationships.py ⚠️ 无参数校验
  ├─ measures.py ❌ stub               ├─ patterns.py ❌ 无注入代码
  └─ statistical.py ❌ stub            ├─ pattern_checks.py ❌ 无验证
                                       └─ validator.py ⚠️ 静默跳过
```

**解除优先级建议：**
1. **P0-1** 已解除（M4 enrichment 已实现）→ 只需补齐 M5 函数
2. **P0-2** 优先——实现公式求值器，解锁 Stage β 全部度量生成
3. **P0-3** 其次——需 P0-2 完成后才有可测试的 Loop B 端到端路径
4. **P1-1/P1-2** 可并行推进——独立于 P0 阻塞链

---

## 四、数据生命周期总结

| 数据对象 | 创建模块 | 消费模块 | 可变性 | 代码位置 | 实现状态 |
|---|---|---|---|---|---|
| `scenario_context` (str) | Phase 1 | M3 | Read-only | `prompt.py:207` 接收 | ✅ |
| `system_prompt` (str) | M3 | M3 (内部 retry loop) | Frozen | `prompt.py:252` 渲染 → `sandbox.py:682` 每次传入 | ✅ |
| LLM 脚本 (str) | M3 (LLM) | M1 (via exec) | Per-attempt regenerated | `sandbox.py:638-642` exec | ✅ |
| `FactTableSimulator` 实例 | M1 (exec 内) | M1 (exec 内) | Accumulating→frozen | `simulator.py:28-51` 构造 | ✅ |
| `columns` (OrderedDict) | M1 | M2, M4 | Frozen after generate() | `simulator.py:132` → `generator.py:28` | ✅ |
| `groups` (dict[str, DimensionGroup]) | M1 | M2, M4 | Frozen after generate() | `simulator.py:133` → `generator.py:29` | ✅ |
| `group_dependencies` (list) | M1 | M2, M4 | Frozen | `simulator.py:134` → `generator.py:30` | ✅ |
| `measure_dag` (dict) | M1 | M2 | Frozen | `simulator.py:135` → `generator.py:31` | ✅ |
| `orthogonal_pairs` (list) | M1 | M4 | Frozen | `simulator.py:_orthogonal_pairs` → **丢失**（`generator.py:120` 硬编码 `[]`） | ⚠️ |
| `patterns` (list[dict]) | M1 | M2 (γ注入), M4, M5 (L3) | Frozen | `simulator.py:138` → `generator.py:34/92` | ✅ |
| `realism_config` (dict) | M1 | M2 (δ注入) | Frozen | `simulator.py:139` → `generator.py:35/97` | ⚠️ 部分 |
| `topo_order` (list[str]) | M2 (pre-flight) | M2 (α/β/metadata) | Computed once | `generator.py:76` | ✅ |
| `rng` (np.random.Generator) | M2 | M2 (α/β/γ/δ) | Progressive consumption | `generator.py:70` → 各阶段按引用传递 | ✅ |
| `rows` (dict[str, ndarray]) | M2 (α) | M2 (β, τ_post) | Mutated in-place per stage | `skeleton.py:31` → `measures.py:19` → `postprocess.py:19` | ✅/⛔ |
| `df` (pd.DataFrame) | M2 (τ_post) | M2 (γ/δ), M5, Phase 3 | In-place modified by γ/δ | `postprocess.py:19` → `generator.py:89` | ✅ |
| `schema_metadata` (dict) | M4 (via M2) | M5, Phase 3 | Defensively copied, immutable | `builder.py:23` → `generator.py:118` | ✅（⚠️ orthogonal 空） |
| `SandboxResult` | M3 | M3 (retry loop) | Per-attempt | `sandbox.py:344/426` | ✅ |
| `RetryLoopResult` | M3 | Pipeline | Final | `sandbox.py:651/700` | ✅ |
| `ValidationReport` | M5 | Loop B, Phase 3 | Additive (add_checks) | `validator.py:62-76` | ✅ |
| `Check` | M5 (L1/L2/L3) | M5 (report), Loop B (strategy match) | Immutable | `structural.py` / `pattern_checks.py` | ✅ 部分 |
| `overrides` (dict) | Loop B (策略) | M2 (re-run) | Per-retry computed | `autofix.py` → `generator.py:36` | ⚠️ 签名就绪，消费缺失 |
| `SkipResult` | M3 | Pipeline | Terminal sentinel | `exceptions.py:372-387` | ⚠️ 与 RetryLoopResult 未统一 |
| typed Exception | M1 | M3 (feedback loop) | Per-attempt | `exceptions.py:52-304` → `sandbox.py:219` | ✅ |
| feedback_prompt (str) | M3 | LLM (external) | Per-attempt | `sandbox.py:509-521` 组装 → `sandbox.py:682` 传出 | ✅ |

---

## 五、关键发现汇总

### 已实现的完整路径

1. **Phase 1 → M3 → M1 → M2(skeleton only) → (df, metadata) → sandbox → RetryLoopResult**
   从场景上下文到骨架 DataFrame 的端到端路径可运行，但仅生成非度量列。

2. **Loop A 异常反馈链：** M1 抛出 → sandbox 捕获 → 格式化 → LLM 重新生成 → 全新 namespace 重试。
   核心路径完整，仅对话累积缺失。

3. **M4 metadata enrichment：** 超越 §2.6 示例，包含 M5 所需的全部字段。

### 管道断裂点

| # | 断裂点 | 影响 | 修复复杂度 |
|---|---|---|---|
| 1 | `orthogonal_pairs=[]` 硬编码 📍 `generator.py:120` | M4 metadata 丢失正交信息 → M5 χ² 跳过 | 低——`run_pipeline()` 加参数 |
| 2 | M2→M5 无自动管道 | 生成后不自动验证 | 中——实现 `generate_with_validation()` |
| 3 | Loop B 循环框架缺失 | 验证失败无法自动修复 | 中——实现循环+分发表+overrides |
| 4 | 对话累积缺失 | LLM 可能重复先前错误 | 低——`run_retry_loop` 维护 `messages` 列表 |
| 5 | Stage β 度量生成 stub | 无度量列 → L2/L3 不可测 | 高——P0-2 公式求值器 |
| 6 | `SkipResult` vs `RetryLoopResult` | 两种终端失败表示共存 | 低——统一返回类型 |

### NEEDS_CLAR 阻塞解除建议

```
已解除:  P0-1 (metadata enrichment) ✅
待解除:  P0-2 (formula evaluator) → 解锁度量生成 + L2 校验
         P0-3 (auto-fix semantics) → 解锁 Loop B 端到端（依赖 P0-2）
         P1-1 (mixture schema) → 解锁第 8 种分布族
         P1-2 (4 种 pattern) → 解锁 4/6 模式注入+验证
```
