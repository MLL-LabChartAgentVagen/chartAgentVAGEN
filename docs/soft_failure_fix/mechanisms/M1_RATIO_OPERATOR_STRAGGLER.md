# M1 长尾残留：ratio operator 引入的结构方差

> Status: 已识别 / 未修 — 2026-05-20
> Trigger scenario: `agpds_503613ba96` / column `student_faculty_ratio`
> Discovery batch: `output/agpds/pingyue-samples-openai-calibrated/`
> 配套阅读：[FAILURE_MECHANISMS.md §2 + §7.1](../FAILURE_MECHANISMS.md)、[MECHANISM_1_DEEP_DIVE.md](MECHANISM_1_DEEP_DIVE.md)、[SIGMA_CALIBRATION.md](../subsystems/SIGMA_CALIBRATION.md)、[OPENAI_VALIDATION.md §3.2](../validation/OPENAI_VALIDATION.md)

---

## 1. TL;DR

openai-calibrated 批次（10 scenarios，Path A + Loop A sigma calibration 全开）跑完后，机制 1 残留 **1 条** `residual_*` 失败：

```
agpds_503613ba96 / residual_student_faculty_ratio:
   noise_sigma=4.4300, residual_std=7.8358, ratio=0.7688  (threshold 0.2)
```

**根因**：LLM 写的结构公式里有 `undergraduate_enrollment / tenure_track_faculty_count` 这个**除法算子**。除法的结果自带结构方差（≈ `(A/B)² × ((σ_A/A)² + (σ_B/B)²)`），不属 LLM 用 `noise={"sigma": X}` 声明的加性噪声范围。Calibration 只能调加性 sigma，对结构方差无能为力——LLM 把 sigma 从 ~1.15 调到 4.43 已经到了"合理上限"（base 值 8.0 的 55%，再高就压过 signal），最后停在 ratio=0.77。

这是 **机制 1 同源的"除法算子分支"**——[FAILURE_MECHANISMS.md §2](../FAILURE_MECHANISMS.md) 的复合方差盲区原本是为**乘法链** (A × B × C) 立的论；本案说明同一个机制在 **ratio operator** (A / B) 上有未覆盖分支。

---

## 2. 数据演变

以 `agpds_503613ba96 / student_faculty_ratio` 为对象：

| 阶段 | declared σ | empirical residual std | ratio | 状态 |
|---|---:|---:|---:|---|
| v1（openai，no Path A，no calibration）| 1.15 \* | 35.2 \* | 29.6× | 严重失败 |
| openai-calibrated（calibration 收敛后）| 4.43 | 7.84 | **0.77** | 边缘失败（> 0.2 阈值）|

\* v1 具体数字来自 [FAILURE_MECHANISMS.md §2](../FAILURE_MECHANISMS.md) 表（同一 column）。

Calibration 已经把 sigma 提升 **3.85×**，把 ratio 改善 **38×**——但还差最后一脚踩进阈值 0.2。

> **ratio 的定义**（[statistical.py::check_structural_residuals](../../../pipeline/phase_2/validation/statistical.py)）：
> `ratio = |residual_std − noise_sigma| / noise_sigma`
> ratio=0.77 ⟹ empirical 比 declared 大 77%（不是 23%）。

---

## 3. 根因：除法算子的结构方差

scenario 的相关公式（[declarations/agpds_503613ba96.json](../../../output/agpds/pingyue-samples-openai-calibrated/declarations/agpds_503613ba96.json)）：

```python
# 目标列
student_faculty_ratio = (
    8.0
    + 0.42 * (undergraduate_enrollment / tenure_track_faculty_count)
    + ratio_department_adj + ratio_level_adj + ratio_quarter_adj
)
noise: gaussian(sigma=4.43)   # ← calibration 后

# 同 scenario 的 course_load（在 §4 用）
course_load = (
    2.05
    + 0.00042 * undergraduate_enrollment
    - 0.010 * tenure_track_faculty_count
    + rank_load_adj + level_load_adj + quarter_load_adj + department_load_adj
)
noise: gaussian(sigma=0.55)
```

### 方差传播

令 `R = E / F`，E（enrollment）和 F（faculty）都是上游 stochastic measure：

$$
\mathrm{Var}(R) \;\approx\; \left(\frac{E}{F}\right)^2 \cdot \left(\frac{\sigma_E^2}{E^2} + \frac{\sigma_F^2}{F^2}\right)
$$

这部分方差**不在 LLM 的 `noise={"sigma":...}` 声明里**——它来自 measure DAG 上游 column 的本征 stochastic。Validator 测的 `residual_std`：

```
residual_var ≈ noise_sigma²  +  (0.42)² × Var(E/F)  +  effect_term_var
```

LLM 把 sigma 调到 4.43 时 sigma² = 19.6；empirical residual² = 61.4。**差的 41.8 ≈ 由 `0.42 × E/F` 贡献的结构方差**——calibration 无法靠改 sigma 把它吃掉，因为它压根不在 calibration 控制范围内。

### 与 §2 乘法链的同构

| 算子 | 公式形态 | 方差表达 | LLM 易错 | doc 状态 |
|---|---|---|---|---|
| **乘法链** | `A × B × C × ...` | `Var ∝ Π(μ²) × Σ(σ²/μ²)` | ✓ | [FAILURE_MECHANISMS.md §2](../FAILURE_MECHANISMS.md) 原始关注点 |
| **除法算子** | `A / B` | `Var ≈ (A/B)² × ((σ_A/A)² + (σ_B/B)²)` | ✓ | **本 doc 新覆盖** |
| **复合（链 + 除）**| `A × B / C` 等 | 更复杂 | 应同发病 | 本批未踩到 |

Calibration 在乘法链上**有效**（参见 [SIGMA_CALIBRATION.md](../subsystems/SIGMA_CALIBRATION.md)），因为乘法链的方差量级随 sigma 单调；LLM 把 sigma 调高就能覆盖。**除法引入的方差有一个由上游 stochastic 决定的硬下界**——LLM 即使把 sigma 调到与之相当也只是把信号噪声化，无法消除该结构项。

---

## 4. 配套观察：同列 reversal 失败说明形成更深 bug

同 scenario 还有一条 reversal 失败：

```
reversal_course_load_student_faculty_ratio: rank_corr=0.2857 (expected <0)
```

Validator 期望 `course_load` 与 `student_faculty_ratio` **负相关**（领域直觉：师生比涨 → 资源紧张 → 课业负担涨；或反向解读）。但 LLM 写的两条公式：

- `course_load        = ... + 0.00042 × enrollment − 0.010 × faculty + ...`
- `student_faculty_ratio = ... + 0.42 × (enrollment / faculty) + ...`

**共享 `enrollment` 在分子、`faculty` 让自身变小（一个减、一个分母）**——所以两条会**结构性正相关**，秩相关 +0.29 是必然的。

含义：`student_faculty_ratio` 的公式不仅 sigma 没调对（M1 残留），**公式骨架本身**也有问题——

1. 除法算子让 sigma calibration 进不去（M1 同源分支，**本 doc 主题**）
2. 共享上游变量导致 reversal 跟 `course_load` 同向（结构 bug，属 [M4-reversal 范畴](../FAILURE_MECHANISMS.md)）

**单修 sigma 修不了 reversal；但修 reversal（让 LLM 重写公式结构）会同时改善 residual。** 两个失败有同一个 root：`student_faculty_ratio` 这条公式的因果模型 LLM 没写对。

---

## 5. 为什么 calibration 卡在 0.77 不继续

Calibration 重试预算 3 轮（[retry_loop.py:234](../../../pipeline/phase_2/orchestration/retry_loop.py#L234)），可能的收敛轨迹：

```
round 0: sigma = 1.15  → empirical residual ≈ 35  → ratio = 29×  (declared = 3% of empirical)
round 1: feedback "suggested ~35" → LLM 写 sigma ∈ [3, 5]  → ratio ≈ 1-2×
round 2: feedback "suggested ~7-8" → LLM 写 sigma = 4.43  → ratio = 0.77  (LLM 收手)
round 3: budget 用尽，进入 Stage 2 报失败
```

**LLM 不敢继续往上调的原因**：sigma = 4.43 已经是 base 8.0 的 55%，再高（如 7.84）会让 noise std ≈ base，破坏 signal-to-noise——LLM 的 prompt（含约束 11"sigma ~10–30% of dynamic range"）和它的训练分布都认为这种 noise 量级"不像真实数据"。

**根本上**：除法算子的结构方差永远 > 0，再多重试也无法靠加性 sigma 归零它——除非把 sigma 调到与 ratio 整体量级相当，但那时数据就没意义了。所以提高 calibration retry budget（如 3→5）几乎没收益。

---

## 6. 为什么这是长尾而非常见 mode

| 域类型 | 公式典型 | 含 ratio 算子？ | M1 发病 |
|---|---|---|---|
| Spotify/Netflix（加法域）| `A + B × const` | ❌ | ❌ 几乎不 |
| funnel/conversion（乘法域）| `A × B × C × D` | ❌ | ✓ 严重（已被 calibration 关闭）|
| **rate / per-X measure（混合域）**| `... + α × (A/B) + ...` | **✓** | ⚠ **本 doc 描述的长尾** |

pingyue 10 个 scenario 里 ratio 算子只出现在 1 个 (#4 student_faculty_ratio)，所以本批发病率 1/10。

**若以后大量产生"率值 / per-unit measure"——cost_per_student, faculty_per_dept, hours_per_capita, revenue_per_user, infection_rate, conversion_rate 等——这个分支会从长尾变成常规失败 mode**。

---

## 7. 修复选项

| 方案 | 投入 | 收益 | 副作用 |
|---|---|---|---|
| **A.** Prompt 新增 Constraint 14：声明含 `/` 的 structural 公式时，sigma 须含 ratio 方差项的估算（与现 Constraint 11 同位） | 改 [prompt.py](../../../pipeline/phase_2/orchestration/prompt.py) ~10 行 | 直接关闭该长尾 | LLM 认知负担 ↑；多个除法链时可能 over-claim sigma |
| **B.** Validator 侧 ratio-aware：解析公式 AST，检测除法 → 自动套 propagation 公式算 expected sigma 上界，用上界做 ratio 判定 | 改 [statistical.py::check_structural_residuals](../../../pipeline/phase_2/validation/statistical.py) + 新加 formula AST 解析（~50–80 行）| 严格闭合 | AST 解析复杂度上升；`A * B / C` 等组合需 ad-hoc |
| **C.** 文档化，接受为已知长尾（**本 doc 本身**）| 0 代码 | 0 修复 | 留给以后 ratio measure 增多再 revisit |
| **D.** 提高 calibration retry budget (3 → 5) | 改 [retry_loop.py:234](../../../pipeline/phase_2/orchestration/retry_loop.py#L234) 1 行 | ≈ 0（§5 已说明）| 浪费 token |

D 已分析过无效，排除。A 是最低成本路径，B 是最严格，C（本 doc）是当前默认。

---

## 8. 当前决策：C（文档化，暂不修）

理由：

1. **影响范围有限**：当前域里 ratio operator 出现率 1/10，不是 production 阻塞项。
2. **同 scenario 的 reversal 失败说明根更深**：单修 sigma 不足以让 #4 全 pass（A 方案修不了 reversal）；要根治得让 LLM 重写公式结构。
3. **M1 主线已闭合**：openai-calibrated 把 `residual_*` 15→1（93% 减），剩 1 条是**已知机制的已知分支**，不是新机制。
4. **Path D 已经把 ks 39→0**（[OPENAI_VALIDATION.md](../validation/OPENAI_VALIDATION.md) + 配套 rerun 数据），主要交付目标已达到。

### 升级为 A/B 的触发条件

回头做 A 或 B，触发条件之一：

- ratio operator 在新批次里出现率 > 30%
- 单 scenario 多条 measure 走 ratio operator → 同时出现多条 residual_*
- 下游 chart QA 任务对 `*_ratio` / `*_per_*` 类 measure 的精度敏感
- 域漂移到金融/医疗/广告等"率值密集"领域

---

## 9. 验证 / 复现

```bash
# 1. 看 baseline 与 Path D rerun 两批的 #4 residual 数字
jq '.[] | select(.generation_id == "agpds_503613ba96") | .failures' \
   output/agpds/pingyue-samples-openai-calibrated/validation_summary.json
jq '.[] | select(.generation_id == "agpds_503613ba96") | .failures' \
   output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation/validation_summary.json
# 两份输出里 residual_student_faculty_ratio 数字一字不差
# (noise_sigma=4.4300, residual_std=7.8358, ratio=0.7688)
# → 说明 run_loop_b_from_declarations 在固定 seed 下 df bit-identical
# → 残留是公式结构性的，不是采样波动

# 2. 看 LLM 写的公式
jq '.columns[] | select(.name == "student_faculty_ratio")' \
   output/agpds/pingyue-samples-openai-calibrated/declarations/agpds_503613ba96.json

# 3. 看相关的 reversal 配套失败（同列）
jq '.[] | select(.generation_id == "agpds_503613ba96") | .failures[] | select(.name | startswith("reversal_"))' \
   output/agpds/pingyue-samples-openai-calibrated/validation_summary.json
```

---

## 10. 相关

- [FAILURE_MECHANISMS.md §2](../FAILURE_MECHANISMS.md) — 机制 1 总论（乘法链版本）
- [MECHANISM_1_DEEP_DIVE.md](MECHANISM_1_DEEP_DIVE.md) — 机制 1 的细化
- [SIGMA_CALIBRATION.md](../subsystems/SIGMA_CALIBRATION.md) — calibration 设计与 gemini 端验证
- [OPENAI_VALIDATION.md §3.2](../validation/OPENAI_VALIDATION.md) — 本批生产数据（包含对本 doc 的引用）
- [PATH_D_KS_SPARSE_CELLS.md](../subsystems/PATH_D_KS_SPARSE_CELLS.md) — 机制 3（同期完成的兄弟 fix）
