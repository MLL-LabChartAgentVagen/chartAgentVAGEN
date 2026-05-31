# 机制 1（复合方差盲区）深度剖析：根因 → 算法 → 实测

> **🗄 已归档（2026-05-31）**：本文叙事已被证伪、所述 calibration 亦已禁用，当前权威 M1 说法见 [../mechanisms/M1_RESIDUAL_RECONCILIATION.md](../mechanisms/M1_RESIDUAL_RECONCILIATION.md)。保留作历史投资记录。
>
> **⚠️ 更正（2026-05-30）**：本文「validator sees residual_std ≈ 乘积方差 / 66×」这一前提，与现行（且自第一版 `0e696e0` 起就存在的）residual 实现冲突——validator 用**实测因子列**重算公式，乘积方差被减掉，进不了 residual。M1 `residual_*` 失败的真因是 **Phase γ pattern 污染 + P3-8 排除泄漏**（σ 无关），sigma 校准只是用大 noise 掩盖它。详见 [../mechanisms/M1_RESIDUAL_RECONCILIATION.md](../mechanisms/M1_RESIDUAL_RECONCILIATION.md)。以下原文保留作历史。
>
> **已实测锁定（2026-05-30）**：确定性诊断 [`residual_source_dump.py`](../../../pipeline/phase_2/analysis/residual_source_dump.py) 证实——合成 case 里 residual_std 仅在 P3-8 被绕过时膨胀到 127×σ，P3-8 在位则 ≈σ；而**本文 §3.1 的案例 `agpds_e9c40d0352::absentee_count`**（这里归因为「乘积方差 743、28.74×」）在现行代码 + T9 修复下 residual_std=23.6 ≈ σ(24)，本应 PASS。即历史 66×/9742× 是 T9 bug（P3-8 失效）的产物，乘积方差从不进 residual，**也不需要 sigma 校准来修**。
>
> 配套阅读：[ANALYSIS.md](../ANALYSIS.md) 是一页综述；本文档是机制 1 的纵深，把"为什么 LLM 算不对乘积 sigma → 我们怎么用 calibration 绕过 → pingyue-samples 上的真实失败和修复后的实测"串成一条线。
>
> 数据来自三个 byte-identical 批次（同 10 scenario · gemini · seed=42）：
> - `output/agpds/pingyue-samples-gemini-baseline` — Loop A 无 Path A、无 calibration
> - `output/agpds/pingyue-samples-gemini-pathA` — +Path A prompt 约束，无 calibration
> - `output/agpds/pingyue-samples-gemini-pathA-calibrated` — +Path A +Loop A calibration

---

## 1. 一页总结

| 维度 | baseline | pathA | **pathA-calibrated** |
|---|:-:|:-:|:-:|
| passed | 0/10 | 0/10 | **4/10** ✓ |
| total failures | 83 | 93 | **18** (-81%) |
| `residual_*` count | 18 | 15 | **0** ✓ |
| `residual_*` ratio median | 19.25× | 2.49× | **0** ✓ |
| `residual_*` ratio max | 9742× | 28.74× | **0** ✓ |
| `ks_*` count | 64 | 76 | **11** (-86%) |

**Headline**：机制 1 的修复直接关掉 18 个 `residual_*` 失败和 53 个 `ks_*` 失败——后者是因为 sigma 写对了，跨 cell 分布自然就对上了，不是单独修了 KS。

---

## 2. 根本原因：LLM 视角 vs 引擎视角

### 2.1 SDK 是声明式 DSL，每次调用看起来是独立的

LLM 在 `FactTableSimulator` SDK 里这样写一个 measure：

```python
sim.add_measure_structural(
    name="enrollment_count",
    formula="application_count * acceptance_fraction * major_yield",
    noise={"family": "gaussian", "sigma": 5.0},   # ← LLM 在这里给出 sigma
)
```

LLM 把它读成一句独立声明：「`enrollment_count` 在公式预测值附近以 σ=5 的高斯散布抖动」。每个 measure 的 sigma 是 LLM 对"这列围绕公式值应该有多大噪声标准差"的**闭式预言**。

### 2.2 引擎把这些独立声明拼成一个联合分布 + 乘法结构

引擎跑的不是 LLM 想象中的"在公式值上加 N(0, σ²)"，而是：

```
generate(enrollment_count_i) = (application_count_i × acceptance_fraction_i × major_yield_i)
                             + N(0, σ²)
```

其中 `application_count_i`、`acceptance_fraction_i`、`major_yield_i` 三个因子**自己也是随机变量**——是上游 stochastic measure 的独立采样。

公式的输出 = 三个随机变量乘积 + 一个相对小的高斯加性噪声。**乘积本身的方差远大于 σ²**。

### 2.3 数学：乘积方差是均值和方差的复杂卷积

对两个独立非负随机变量 $X, Y$：

$$\mathrm{Var}(XY) = \mathrm{Var}(X)\mathrm{Var}(Y) + \mathrm{Var}(X)E[Y]^2 + \mathrm{Var}(Y)E[X]^2$$

对 $n$ 个因子的乘积，方差会随因子数指数增长。例如：

- `application_count ~ N(2000, 500²)`
- `acceptance_fraction ~ Beta(α, β)`, E=0.3, Var≈0.01
- `major_yield ~ Beta(α, β)`, E=0.7, Var≈0.05

乘积的 $\mathrm{Var}$ 量级约几千的平方，std ≈ 几百。LLM 写的 `σ=5` 描述的只是"加性噪声"那一项的标准差。Validator 量的是**整体 residual std**——把它除以 `σ=5`，ratio 可以轻松到 60×、500×、甚至 9742×。

### 2.4 LLM 为什么算不出来

三层认知障碍叠加：

1. **闭式不可行**：5 个非独立随机变量乘积的 std 没有简单闭式。LLM 不会执行符号运算。
2. **联合分布不可见**：LLM 看一句 SDK 调用，看不到上游因子的分布形状、参数；它只能猜「sigma=5 大概差不多」。
3. **prompt 指引也只能给 heuristic**：Path A 的 hard constraint 11/12（[prompt.py:103-118](../../../pipeline/phase_2/orchestration/prompt.py#L103)）让 LLM 用「σ ≈ 10–30% of range」的规则。**实测把 ratio median 从 19.25 → 2.49**，是质变；**但够不到 validator 阈值 0.2**——heuristic 的上限就是这里。

> Path A 像是教 LLM "更负责任地猜"；calibration 是让 LLM "看着引擎的真实输出回填"。两者互补，calibration 不可省。

---

## 3. 实际失败案例：pathA batch 的真实 residual_* 失败

下面是 `pingyue-samples-gemini-pathA/validation_summary.json` 里所有 15 条 `residual_*` 失败，按 ratio 排序：

| Scenario | Column | declared σ | empirical σ | ratio |
|---|---|---:|---:|---:|
| `agpds_e9c40d0352` | `absentee_count` | 25.00 | 743.62 | **28.74×** |
| `agpds_8022981cf7` | `pass_rate` | 5.00 | 102.13 | **19.43×** |
| `agpds_d62b18e180` | `gpa_change` | 0.30 | 2.97 | 8.90× |
| `agpds_503613ba96` | `undergraduate_enrollment` | 400.00 | 2394.17 | 4.99× |
| `agpds_d62b18e180` | `course_failure_rate` | 5.00 | 29.03 | 4.81× |
| `agpds_14b7f7487e` | `renewal_count` | 1200.00 | 5585.96 | 3.65× |
| `agpds_d62b18e180` | `credits_completed` | 3.00 | 11.74 | 2.91× |
| `agpds_8022981cf7` | `course_completion_rate` | 2.50 | 8.72 | 2.49× |
| `agpds_14b7f7487e` | `hold_fulfillment_rate` | 4.00 | 8.94 | 1.23× |
| `agpds_3af92040e6` | `total_aid_disbursed` | 75 000 000 | 133 520 182 | 0.78× |
| ... | ... | ... | ... | ... |

（median ratio = 2.49, max = 28.74）

### 3.1 Case study：`agpds_e9c40d0352::absentee_count`

LLM 在脚本里这样声明（[scripts/agpds_e9c40d0352.py:97-101](../../../output/agpds/pingyue-samples-gemini-pathA/scripts/agpds_e9c40d0352.py)）：

```python
sim.add_measure_structural(
    "absentee_count",
    formula="enrollment_count * (100 - attendance_rate) / 100",
    effects={},
    noise={"family": "gaussian", "sigma": 25}   # ~12% of dynamic range (~200)
)
```

LLM 的推理（注释暴露了）：「`absentee_count` 量级大约 0–200，sigma=25 ≈ 12% range，符合 Path A 给的 10–30% 规则」。

**它没看见的耦合**：

- `enrollment_count` 自己是个 structural 公式，是 4–5 个 yield 的乘积，本身的 std 已经几百
- `attendance_rate` 是个 stochastic measure，也有自己的 std
- 公式 `enrollment_count × (100 - attendance_rate) / 100` 等价于「一个 std 几百的量 × 一个 0–1 比例」——比例的随机抖动会被几百的 magnitude 放大
- 引擎跑出来的 `residual_std` = **743.62**，ratio = **(743.62 - 25)/25 = 28.74×**

Validator 报 `residual_absentee_count: noise_sigma=25.0000, residual_std=743.6242, ratio=28.7449 (>= 0.2)`，scenario soft-fail。

### 3.2 Loop B 救不了的原因

Loop B 的四把工具（[validation/autofix.py](../../../pipeline/phase_2/validation/autofix.py)）都是**局部参数微调**：

- `widen_variance` 一次系数 ×1.2，3 轮上限 `1.2³ = 1.728×`——对 ratio 28× 杯水车薪
- `amplify_magnitude`、`reshuffle_pair` 改的不是 sigma 字段
- 假设是 *"骨架对、火候没调准"*——但这次 LLM 连骨架都没搭对（声明了一个 1–2 个数量级偏离实际的 sigma），骨架错必须沿 Loop A 改。

---

## 4. 解决方案：Loop A 内 LLM-in-the-loop sigma calibration

### 4.1 一句话

> Loop A 在每次 LLM exec 成功后，**用引擎重放 declarations、量 empirical residual std**，若与 LLM 声明的 sigma 偏差 ≥ 0.2，把 `(declared, empirical, suggested)` 三元组反馈给 LLM 重写 sigma。独立 calibration retry budget（≤3 次）；耗尽则写 `SkipResult(skip_reason="calibration_unconverged")`。

### 4.2 为什么这能绕过数学障碍

LLM 算不出乘积 std，但**引擎能算**——只要把声明 replay 一遍，跑完所有上游 stochastic + structural 的真实 sample 路径，乘积的 empirical std 就是地面真相。把这个真相塞回 prompt，LLM 不再"闭式猜"，而是"按经验值复读"。这是绕开 §2.4 三层认知障碍的最短路径。

### 4.3 算法流程

```
Loop A
┌─ execute_in_sandbox(current_code) ─────────────────────┐
│                                                          │
│   if not result.success:                                 │
│     exec_attempts++ ; feedback ← typed exception         │
│     continue  (exec budget ≤ 3)                          │
│                                                          │
│   # exec 成功后进入 calibration 阶段                       │
│   cal = check_sigma_calibration(                         │
│       raw_declarations,                                  │
│       threshold=0.2,                                     │
│   )                                                      │
│   # 内部 4 步：                                           │
│   #  1. run_pipeline(realism_config=None)  full-N replay │
│   #  2. for each structural measure with declared sigma: │
│   #       check_structural_residuals(df, col, schema)    │
│   #       → empirical_std (parse from detail string)     │
│   #  3. ratio = |emp - decl| / decl                      │
│   #  4. ratio ≥ 0.2 → CalibrationFailure(...)            │
│                                                          │
│   if cal.passed:                                         │
│     return RetryLoopResult(success=True, ...)            │
│                                                          │
│   if calibration_attempts_used < calibration_max (=3):   │
│     calibration_attempts_used += 1                       │
│     feedback ← format_calibration_feedback(              │
│         original_code, cal.failures                      │
│     )                                                    │
│     current_code ← llm.generate(feedback)                │
│     continue   # 注意：不消耗 exec budget                  │
│                                                          │
│   else:                                                  │
│     return RetryLoopResult(                              │
│       success=False,                                     │
│       skipped_reason="calibration_unconverged (...)",    │
│     )                                                    │
└──────────────────────────────────────────────────────────┘
```

### 4.4 关键设计决策

| 决策 | 理由 |
|---|---|
| **独立 retry budget（exec ≤3, calibration ≤3）** | "代码错"和"参数错"是不同问题，不该挤兑预算。最坏 6 次 LLM call/scenario。 |
| **复用 validator 算法** | calibration 调的是 Stage 2 同一个 [`check_structural_residuals`](../../../pipeline/phase_2/validation/statistical.py#L368)。保证 Loop A 过关的 sigma 在 Stage 2 一定过关——*前提是两边输入字节一致*（这正是 T9 plumbing bug 的来源，见 §6.3）。 |
| **`realism_config=None` 重放** | Stage 2 validator 跑的就是 pre-realism df；calibration 必须跟它一致，否则量出来的 std 不是 validator 会量的那个。 |
| **`suggested_sigma = empirical_std`** | 不引入额外的 heuristic（乘 1.1、加 buffer）；让 LLM 看到引擎的真实值，自己决定写多少。实测大部分情况 LLM 直接 round 到附近整数。 |
| **`_parse_residual_std_from_detail` raise on malformed** | 一旦 validator detail 格式变了，calibration 必须立即报错而不是静默返回 `passed=True`（F1 hotfix，[calibration.py:96-106](../../../pipeline/phase_2/orchestration/calibration.py#L96)）。 |
| **不收敛 → SkipResult，不 raise** | 写 `output/agpds/<batch>/skipped.jsonl` 而不是污染 batch；下游 Stage 3 不消费 skipped 的 scenario。 |

### 4.5 代码位点

| 文件 | 行 | 内容 |
|---|---|---|
| [orchestration/calibration.py](../../../pipeline/phase_2/orchestration/calibration.py) | 1–106 | `check_sigma_calibration` + `CalibrationFailure`/`CalibrationResult` dataclasses + 两个 helper |
| [orchestration/sandbox.py](../../../pipeline/phase_2/orchestration/sandbox.py) | 631–674 | `format_calibration_feedback`：把失败列表渲染成 LLM-readable prompt |
| [orchestration/retry_loop.py](../../../pipeline/phase_2/orchestration/retry_loop.py) | 234–340 | Loop A 主循环里 `if result.success:` 分支插入 calibration check + 独立预算 |
| [exceptions.py](../../../pipeline/phase_2/exceptions.py) | `SkipResult` | 加 `skip_reason: str = "exec_error"` 字段 |
| [agpds_generate.py](../../../pipeline/agpds_generate.py) | `_save_skip_record` | 写 `skipped.jsonl`（**注意**：函数已实现但还没在 `run_generation_batch` 里调起来，见 [ANALYSIS.md §5.1](../ANALYSIS.md#51)） |

### 4.6 Feedback prompt 的实际样子

[`format_calibration_feedback`](../../../pipeline/phase_2/orchestration/sandbox.py#L631) 渲染出来类似：

```
Your script executed successfully, but the declared noise sigma is
mis-calibrated for 2 measure(s):

  - Measure `absentee_count`: declared sigma=25.0000, empirical residual
    std=743.6242, ratio=28.745 (threshold=0.2). Suggested sigma ≈ 743.6242.
  - Measure `pass_rate`: declared sigma=5.0000, empirical residual
    std=102.1300, ratio=19.426 (threshold=0.2). Suggested sigma ≈ 102.1300.

Action: rewrite the script with sigma values close to the suggested
empirical residual std (within ±10%). Do NOT change measure formulas,
categorical structure, patterns, or seeds — ONLY adjust sigma in
`noise=` / `noise_sigma=` arguments.

Original code:
```python
... (LLM 上一轮的完整脚本) ...
```
```

显式约束「只改 sigma，别改公式 / 类别 / patterns / seed」——避免 LLM 借机重写引发新失败。

---

## 5. 修复后效果：pathA-calibrated 的实测

### 5.1 Per-scenario 失败明细

| Scenario | pathA (before) | pathA-calibrated (after) |
|---|---|---|
| `agpds_14b7f7487e` | 10 fails (incl. 2 residual_*) | 2 fails: `group_dep_primary_audience`, `seasonal_checkout_count` |
| `agpds_33d84d2c9b` | 11 fails (incl. 1 residual_*) | 4 fails: 4× `ks_*` |
| `agpds_3af92040e6` | 12 fails (incl. 1 residual_*) | **✓ PASS** |
| `agpds_503613ba96` | 8 fails (incl. 1 residual_*) | **✓ PASS** |
| `agpds_65ef0afda0` | 15 fails | 1 fail: `reversal_grant_funding_publication_count` |
| `agpds_8022981cf7` | 5 fails (incl. 2 residual_*) | 2 fails: `outlier_*`, `reversal_*` |
| `agpds_8180fe4e2c` | 4 fails | **✓ PASS** |
| `agpds_985a1b72e1` | 9 fails | 7 fails: 6× `ks_*` on `average_salary`/`employment_rate`, 1× `outlier_*` |
| `agpds_d62b18e180` | 7 fails (incl. 4 residual_*) | **✓ PASS** |
| `agpds_e9c40d0352` | 12 fails (incl. 1 residual_*) | 2 fails: `ks_attendance_rate`, `seasonal_attendance_rate` |

**residual_* 失败数：15 → 0**（100% 关闭）。
**passed scenario 数：0/10 → 4/10**。

### 5.2 LLM 实际写的 sigma 修正

以 `agpds_e9c40d0352::absentee_count` 为例（calibration 触发前后同 scenario 同 seed）：

**Before（[pathA scripts](../../../output/agpds/pingyue-samples-gemini-pathA/scripts/agpds_e9c40d0352.py#L97-L101)）：**

```python
sim.add_measure_structural("absentee_count",
    formula="enrollment_count * (100 - attendance_rate) / 100",
    effects={},
    noise={"family": "gaussian", "sigma": 25})  # ~12% of dynamic range (~200)
```

**After（[pathA-calibrated scripts](../../../output/agpds/pingyue-samples-gemini-pathA-calibrated/scripts/agpds_e9c40d0352.py#L111-L116)）：**

```python
# Measure 3: absentee_count (Structural Derived)
# Dynamic range: ~10 to 180 (Range = 170). Target noise sigma ~ 10-30% -> 20.0
sim.add_measure_structural("absentee_count",
    formula="enrollment_count * (100 - attendance_rate) / 100",
    effects={},
    noise={"family": "gaussian", "sigma": 20.0})
```

注：这个 scenario 在 calibrated batch 里其实并没有完全采纳 calibration 的建议（建议是 743，LLM 仍写了 20）——但这次 LLM 重新评估了 dynamic range（从 0–200 改成 10–180，更现实），同时其他乘法链 measure 的 sigma 大幅上调；最终引擎 replay 里 absentee_count 的 ratio 降到了 < 0.2。这说明 calibration feedback 不是机械替换 sigma，而是触发了 LLM 对**整条公式链的散布尺度**重新建模。

### 5.3 ks_* 的旁路下降（76 → 11）

这是机制 1 修复的副产品。`ks_*` check 比较的是**跨 cell 的经验分布**——sigma 写得太小时，引擎产出的实际 std 远超声明，每个 cell 的样本看起来都像 outlier 堆叠，跨 cell 的 KS 统计量自然爆炸。sigma 写对了，cell 内分布也对了，KS 自然过了。剩下的 11 个 `ks_*` 是机制 3（稀疏 cell 上 KS 过敏），跟机制 1 无关。

### 5.4 失败类型从"量级错"转成"结构错"

| 失败类型 | pathA (15+76+...=93) | pathA-calibrated (18) |
|---|:-:|:-:|
| `residual_*`（量级错） | 15 | **0** |
| `ks_*`（跨 cell 分布） | 76 | 11 |
| `orthogonal_*`、`marginal_*` | 2 | 0 |
| `group_dep_*`、`seasonal_*`、`outlier_*`、`reversal_*`（pattern 注入相关） | 0 | 7 |

calibrated batch 剩下的 18 个失败**几乎全部是 pattern injection / 稀疏 cell**——也就是机制 2 和机制 3 的领地，机制 1 已经清空。

---

## 6. 进一步阅读 / 已知坑

### 6.1 Path A 的上限

Path A（prompt heuristic）能把 ratio median 从 19.25 → 2.49，但摸不到 0.2 阈值。Calibration 是补足这 2.49 → 0 的最后一公里。Path A 不可省的理由是：它把**第一轮**生成质量提升了，减少了 calibration 的触发频率（很多 scenario 第一轮就直接过；触发 calibration 的也大多 1 轮就收敛）。

### 6.2 stochastic measure 不参与 calibration（v1 设计契约）

`check_sigma_calibration` 只检查 `measure_type=="structural"` 的列（[calibration.py:55-58](../../../pipeline/phase_2/orchestration/calibration.py#L55)）。Stochastic measure 自己就是 source distribution，sigma 是参数本身（不是 residual），不存在「量出来对不对」的问题。`test_calibration.py::TestStochasticMeasuresSkipped` 锁死这个 v1 契约；v2 如果要扩展会显式 break 这个 test。

### 6.3 T9 plumbing bug：跨模块"同一个计算"必须输入一致

实施过程中踩了个一阶坑：T8 production rerun 报 calibration 0/10、residual median 6.76——看起来 calibration 失败。二分定位发现 [pipeline.py:281](../../../pipeline/phase_2/pipeline.py#L281) 的 `patterns=metadata.get("patterns", [])` 在 agpds_execute.py 调用路径里收到空 metadata → patterns=`[]` → `check_structural_residuals` 的 P3-8 pattern-row 排除逻辑静默失效 → pattern-injected outlier 行被计入 residual std，膨胀 ratio。

修复一行：`patterns=patterns`（commit `b16525e`）。

教训写进 [SIGMA_CALIBRATION.md §8.3](SIGMA_CALIBRATION.md)：

> 跨模块的"同一个计算"产生不同结果时，**别先怀疑算法**——先验证两边的输入是否字节一致。

### 6.4 还没修的

机制 1 已经关闭，但 [ANALYSIS.md §5](../ANALYSIS.md#5-未解决问题与下一步) 列了三件后续：

1. `_save_skip_record` 函数已写好但还没在 `run_generation_batch` 里调 → `skipped.jsonl` 实际未写
2. 机制 3（稀疏 cell + KS 过敏）的 11 个剩余 `ks_*` 失败
3. Path B/C 在 openai 上的端到端验证缺口

---

## 7. 配套文档导航

- [ANALYSIS.md](../ANALYSIS.md) — 一页综述，所有 soft-failure 问题的入口
- [FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md) — 三机制 + Path A/B/C 修复路径全图
- [SIGMA_CALIBRATION.md](SIGMA_CALIBRATION.md) — calibration 模块技术参考（架构图、retry budget、T9 case study）
- [2026-05-14-stage1-sigma-calibration.md](2026-05-14-stage1-sigma-calibration.md) — TDD 实施计划（历史档案）
- [VALIDATION_PERSISTENCE.md](../subsystems/VALIDATION_PERSISTENCE.md) — Stage 2 持久化层（report 落盘合约）
