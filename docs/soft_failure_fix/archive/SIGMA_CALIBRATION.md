# Stage 1 Sigma Calibration（已归档：calibration 现已禁用）

> **⚠️ 已归档（2026-05-31）/ 已禁用（2026-05-30）**：本文记录的 Loop A sigma calibration 在 2026-05-30 已被**可逆禁用**（`retry_loop._CALIBRATION_ENABLED=False`）。后续调查表明它是在**掩盖** Phase γ pattern 污染（residual 真因与 σ 无关），而非修因——当前权威说法见 [../mechanisms/M1_RESIDUAL_RECONCILIATION.md](../mechanisms/M1_RESIDUAL_RECONCILIATION.md)。本文保留作历史/再启用参考。
>
> Loop A LLM-in-the-loop sigma calibration—~~机制 1（复合方差盲区）的最终修复~~。
> 实测：pingyue-samples 10 个 scenario，passed 0/10 → 4/10，residual_* 失败 15 → 0。

## 1. 一句话总结

Loop A 在每次 LLM exec 成功后，用 engine 重放 declarations、量 empirical
residual std，若与 LLM 声明的 sigma 偏差 ≥ 0.2 则把 suggested sigma 反馈给
LLM 重写。独立 calibration retry budget（≤3 次）；耗尽则
`SkipResult(skip_reason="calibration_unconverged")`。

## 2. 为什么存在

LLM 系统性低估**乘法链** structural measure 的 residual std。详细机制
分析见 [FAILURE_MECHANISMS.md §2 + §2.5](../FAILURE_MECHANISMS.md#2-机制-1--复合方差盲区)。

修复路径分两层：

- **Path A（heuristic prompt）**：在 [orchestration/prompt.py:103-118](../../../pipeline/phase_2/orchestration/prompt.py#L103-L118)
  加 HARD CONSTRAINT 11/12，让 LLM 主动用 "sigma ≈ 10–30% of range" 的规则。
  实测效果：pingyue-samples-gemini-baseline → pingyue-samples-gemini-pathA，
  residual ratio median 19.25 → 2.49（详 [FAILURE_MECHANISMS.md §8.2](../FAILURE_MECHANISMS.md#82-residual_-偏差幅度最关键指标)）。
- **校准（本文档）**：heuristic 在乘法链里**够不到** validator 阈值 0.2——
  LLM 闭式算不出乘积 std。校准用**实测反馈**绕过这个数学障碍：让 LLM 看到
  engine 实际产出的 std，按建议值重写 sigma。

## 3. 架构图

```
┌─────────────────────────────────────────────────────────┐
│ Loop A (orchestration/retry_loop.py::run_retry_loop)    │
│                                                          │
│   while True:                                            │
│     ┌──────────────────────────────────┐                │
│     │ execute_in_sandbox(current_code) │                │
│     └────────────┬─────────────────────┘                │
│                  │                                       │
│      ┌───────────┴───────────┐                          │
│      │ result.success?       │                          │
│      └───┬──────────────┬────┘                          │
│       no │           yes│                               │
│          │              │                               │
│          ▼              ▼                               │
│  ┌────────────┐   ┌─────────────────────────────────┐  │
│  │ exec retry │   │ check_sigma_calibration(        │  │
│  │ budget     │   │   raw_declarations,             │  │
│  │ (≤3)       │   │   threshold=0.2,                │  │
│  └────────────┘   │ )                               │  │
│                   │ ─ run_pipeline(realism=None)    │  │
│                   │ ─ per structural measure:       │  │
│                   │     check_structural_residuals  │  │
│                   │ ─ collect CalibrationFailure[]  │  │
│                   └──────────┬──────────────────────┘  │
│                              │                          │
│                  ┌───────────┴──────────┐               │
│                  │ cal_result.passed?   │               │
│                  └──┬──────────────┬────┘               │
│               yes  │           no │                     │
│                    ▼              ▼                     │
│            ┌───────────┐  ┌─────────────────────┐      │
│            │ return    │  │ cal budget remains? │      │
│            │ success   │  └──┬──────────────┬───┘      │
│            └───────────┘  yes│           no │           │
│                              ▼              ▼           │
│                ┌────────────────────────┐ ┌──────────┐  │
│                │ format_calibration_    │ │ return   │  │
│                │ feedback(failures) →   │ │ Skipped  │  │
│                │ LLM rewrite → continue │ │ Result(  │  │
│                │ (attempt -= 1)         │ │ skip_    │  │
│                └────────────────────────┘ │ reason=  │  │
│                                           │ "cal_    │  │
│                                           │ unconv") │  │
│                                           └──────────┘  │
└─────────────────────────────────────────────────────────┘

Independent budgets: exec_attempts (default 3) 与 calibration_attempts (default 3)
互不消耗。最坏 6 次 LLM call/scenario。
```

## 4. 关键文件与锚点

| 文件 | 函数/类 | 行 | 用途 |
|---|---|---:|---|
| [orchestration/calibration.py](../../../pipeline/phase_2/orchestration/calibration.py) | `check_sigma_calibration` | 全文件 | 主入口；replay + 量 residual + 出 CalibrationResult |
| [orchestration/calibration.py](../../../pipeline/phase_2/orchestration/calibration.py) | `CalibrationFailure`, `CalibrationResult` | 顶部 | dataclass 返回类型 |
| [orchestration/calibration.py](../../../pipeline/phase_2/orchestration/calibration.py) | `_extract_declared_sigma` | private | 解析 `col_spec["noise"]["sigma"]` |
| [orchestration/calibration.py](../../../pipeline/phase_2/orchestration/calibration.py) | `_parse_residual_std_from_detail` | private | **raises RuntimeError on malformed**（F1 hotfix） |
| [orchestration/sandbox.py](../../../pipeline/phase_2/orchestration/sandbox.py) | `format_calibration_feedback` | 末尾 | LLM 反馈模板，签名对齐 `format_error_feedback` |
| [orchestration/retry_loop.py](../../../pipeline/phase_2/orchestration/retry_loop.py) | `run_retry_loop` | L:200–510 | 集成点；独立 exec/cal budget |
| [orchestration/retry_loop.py](../../../pipeline/phase_2/orchestration/retry_loop.py) | `orchestrate` | L:319+ | 把 `skipped_reason="calibration_unconverged"` 映射到 `SkipResult.skip_reason` |
| [validation/statistical.py](../../../pipeline/phase_2/validation/statistical.py) | `check_structural_residuals` | L:368 | 复用的 residual 算法；calibration 跟 validator 共用 |
| [exceptions.py](../../../pipeline/phase_2/exceptions.py) | `SkipResult.skip_reason` | L:344-365 | 新字段：`"exec_error"` (默认) 或 `"calibration_unconverged"` |
| [../agpds_generate.py](../../../pipeline/agpds_generate.py) | `_save_skip_record`, `SKIPPED_FILENAME` | L:88+ | 写 `skipped.jsonl`（**当前未接入 SkipResult 路径，见 §7 gap 1**） |
| [pipeline.py](../../../pipeline/phase_2/pipeline.py) | `_run_loop_b` L:281 | L:281 | **T9 修复点**：`patterns=patterns`（用 raw_declarations，**不要**用 `metadata.get(...)`） |

## 5. 测试矩阵

每个文件锁定的行为：

| 测试文件 | 测试数 | 锁定行为 |
|---|---:|---|
| [tests/modular/test_calibration.py](../../../pipeline/phase_2/tests/modular/test_calibration.py) | 14 | dataclasses 默认 / happy path / mocked failure dispatch / `_extract_declared_sigma` 6 个 edge case / `_parse_residual_std_from_detail` 抛 RuntimeError / v1 stochastic-skip 契约 / `SkipResult.skip_reason` / `_save_skip_record` 持久化 |
| [tests/modular/test_sandbox_format.py](../../../pipeline/phase_2/tests/modular/test_sandbox_format.py) | 2 | `format_calibration_feedback` 含具体数字、原代码、"Do NOT change" 指令；空 failures 走中性消息 |
| [tests/modular/test_retry_loop.py](../../../pipeline/phase_2/tests/modular/test_retry_loop.py) | 4 | 校准失败 → retry → skip_reason 正确；校准 1 轮后收敛；F2 独立 budget（mock exec error 2 次 + 1 次校准失败仍能用满 cal budget）；无 structural-sigma 不触发校准 |
| [tests/modular/test_pipeline_loop_b_patterns.py](../../../pipeline/phase_2/tests/modular/test_pipeline_loop_b_patterns.py) | 1 | **T9 regression**：spy `SchemaAwareValidator.validate`，断言收到的 patterns 非空且 type 正确 |
| [tests/modular/test_engine_measures.py](../../../pipeline/phase_2/tests/modular/test_engine_measures.py) | 扩展 | `UndefinedEffectError` 替换裸 `KeyError`（机制 2 修复，T1-T9 之前的 Path C） |

测试总数从 baseline 355 → **376**（+21）。全部 `pytest pipeline/phase_2/tests/modular -x -q` 通过。

## 6. 生产验证

详细 3-way 对照见 [FAILURE_MECHANISMS.md §8](../FAILURE_MECHANISMS.md#8-实测数据3-way-对照)。摘要：

| 指标 | -2 (gemini, 无 A) | -v2 (gemini, +A) | **-v3 (gemini, +A+cal, T9 修复后)** |
|---|---:|---:|---:|
| passed | 0/10 | 0/10 | **4/10** ✓ |
| total failures | 83 | 93 | **18** (-81%) |
| residual_* count | 18 | 15 | **0** ✓ |
| residual median ratio | 19.25 | 2.49 | **N/A**（空集） |
| ks_* count | 64 | 76 | **11** |

**7/7 acceptance gates PASS。机制 1 关闭。**

## 7. 已知 gap 与未来工作

按优先级排：

### 7.1 `_save_skip_record` 未接入（中优先级，要用 skipped.jsonl 前必修）

函数和测试都在（[agpds_generate.py L:88](../../../pipeline/agpds_generate.py#L88)、
`test_calibration.py::TestSaveSkipRecord`），但 `agpds_generate.py` 在
`generate_artifacts()` 拿到 SkipResult 时只 `raise RuntimeError(...)` →
`run_generation_batch()` 的 `except Exception` 把它吞进 log 字符串。
所以 `output/agpds/<batch>/skipped.jsonl` **当前不会被实际写**。

**修法**：在 [agpds_generate.py::run_generation_batch](../../../pipeline/agpds_generate.py)
或上游 `AGPDSPipeline.generate_artifacts` 里 isinstance(result, SkipResult)
分支调 `_save_skip_record(batch_dir, result, gen_id)`。约 10 行。

### 7.2 Nitpicks（来自 final reviewer）

- [retry_loop.py](../../../pipeline/phase_2/orchestration/retry_loop.py) 的 `# IS-6 token-budget half`
  是 sprint-internal jargon，会 rot——改成功能描述
- [test_sandbox_format.py](../../../pipeline/phase_2/tests/modular/test_sandbox_format.py) empty-failures
  断言用 `"0" in out or "no" in out.lower()`，可以更紧（断 exact substring）
- `_save_skip_record` 的 `skip_result: untyped` 用 `TYPE_CHECKING` import
  guard 替代行内注释更干净

### 7.3 机制 3 未修

剩余 11 个 `ks_*` 失败 + 零星 `outlier_*`/`seasonal_*` 是稀疏 cell 上 KS
检验过敏的真实表现，不是机制 1。修法是 bonferroni 校正或 cell-size
threshold（Path D，之前显式拒过）。需要单独 plan。

### 7.4 openai 端到端验证 Path B/C 缺口

gemini 的 -v2/-v3 都没触发 `PatternInjectionError`/`UndefinedEffectError`
（Path B/C 的目标错误模式）——纯运气。Path B/C 的代码改动 + 单元测试都对，
但**端到端"Loop A 拿 typed feedback 后自修"** 还没在 production 验证过。
要么在 openai 上重跑，要么人造 scenario 强制触发。

## 8. Case study：T9 plumbing bug

> **教训**：两个模块算同一个东西时，必须验证它们看到的是同一份输入。

### 现象

T8 production run 报 -v3 0/10 passed、residual median 6.76、max 54.75。
看起来 calibration 没起作用——但 Loop A 的 `calibration_attempt` log 显示
10 个 scenario 里 9 个**第一轮就通过**校准检查。Loop A 说 "passed"，
Stage 2 validator 说 "ratio=1.12 FAIL"。同样的 `check_structural_residuals`
函数，结果不同。

### 排查路径

1. **手动 replay**：用 [engine/generator.py::run_pipeline](../../../pipeline/phase_2/engine/generator.py)
   在 disk-loaded declarations 上重放 → `residual_std=5.27`（与 Loop A
   校准一致）。
2. **复刻 Stage 2**：调 [pipeline.py::run_loop_b_from_declarations](../../../pipeline/phase_2/pipeline.py)
   → `residual_std=9.54`（与保存的 Stage 2 报告一致）。
3. **二分**：直接调 `SchemaAwareValidator.validate(df, patterns=disk_decls["patterns"])`
   → 5.27。调 `SchemaAwareValidator.validate(df, patterns=[])` → 9.54。
4. **定位**：[pipeline.py:281](../../../pipeline/phase_2/pipeline.py#L281) `patterns=metadata.get("patterns", [])`。
   `agpds_execute.py:95` 调 `run_loop_b_from_declarations(raw_declarations, max_retries=3)`
   不传 metadata → 默认 `{}` → patterns=`[]`。
5. **机制**：`check_structural_residuals` 有 P3-8 pattern-row 排除逻辑——
   patterns 非空时把 `inject_pattern("outlier_entity", ...)` 命中的行从
   residual 计算里**剔除**；patterns 空时它们**全部计入** → outlier 行的
   `actual - predicted` 巨大 → residual_std 爆涨。

### 修复

```python
# pipeline.py:281
# 改前
patterns=metadata.get("patterns", []),

# 改后
patterns=patterns,  # local var from raw_declarations.get("patterns", [])
```

一行修改。Regression test 在 [test_pipeline_loop_b_patterns.py](../../../pipeline/phase_2/tests/modular/test_pipeline_loop_b_patterns.py)：
spy `SchemaAwareValidator.validate`，断言收到的 patterns 列表非空且 type
正确（`outlier_entity`）。

### 教训

- **Loop A 的 calibration 用 `raw_declarations.get("patterns", [])`**——
  正确。
- **Stage 2 的 validator 用 `metadata.get("patterns", [])`**——
  错误的来源，因为 `metadata` 在 `agpds_execute.py` 调用路径下默认是空 `{}`。
- 两侧都调 `check_structural_residuals`，但传入的 patterns 不同 → 同一份
  df、同一个 sigma 算出不同 residual std。
- **debug 模式**：当跨模块的"同一个计算"产生不同结果，**别先怀疑算法**——
  先验证两边的输入是否字节一致。

## 9. 配套阅读

- [FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md) — 3 机制（复合方差盲区 / 联合分布盲区 / 稀疏 cell 脆弱性）、修复路径 A/B/C、3-way + 4-way 实测对比
- [VALIDATION_PERSISTENCE.md](../subsystems/VALIDATION_PERSISTENCE.md) — Stage 2 持久化层（`validation/{gen_id}_report.json` + `validation_summary.json`）
- [INTERFACES.md](../../../pipeline/phase_2/INTERFACES.md) — M1–M5 模块契约
- [README.md](../../../pipeline/phase_2/README.md) — Phase 2 总览

本目录其他：
- [2026-05-14-stage1-sigma-calibration.md](2026-05-14-stage1-sigma-calibration.md) — TDD-style 实施计划（35 个 step）

历史 plan（执行调度 + amendments）位于本机 `~/.claude/plans/pipeline-agpds-execute-py-soft-warning-temporal-rivest.md`（仓库外，不入版本控制）。
