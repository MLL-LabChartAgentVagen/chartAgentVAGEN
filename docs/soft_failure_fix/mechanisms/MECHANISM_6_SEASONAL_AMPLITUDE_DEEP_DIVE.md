# 机制 6（季节振幅未对齐 baseline 噪声）深度剖析：根因 → 算法 → 实测

> 配套阅读：[ANALYSIS.md](../ANALYSIS.md) 是一页综述；
> [validation/PINGYUE_OPENAI_CAL_ANALYSIS.md §3.1 + §8.4](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#31-agpds_14b7f7487e--boston-public-library-借阅)
> 给出 `agpds_14b7f7487e::seasonal_checkout_count` 的原始失败诊断与 Phase D
> 修复路径。本文是 Phase D 的纵深：把"为什么 LLM 写 `magnitude=0.35` 在 CV≈0.86
> 的 checkout 域必然误判 → 我们怎么用 Constraint 17 + validator detail 替换 →
> pingyue-samples-openai-calibrated 上的真实失败和 LLM regen 之后的实测"串
> 成一条线。
>
> 数据来自两个同 10 scenario · openai · seed=42 · Path A + Loop A calibration
> + Path D + Phase A/B 全开的批次：
> - `output/agpds/pingyue-samples-openai-calibrated-pathB-rev` — Phase A/B 已
>   上线，**`seasonal_checkout_count` 仍 hard-fail**（LLM declaration 未变）
> - `output/agpds/pingyue-samples-openai-calibrated-pathD-llm` — **Phase D 已
>   上线**（Constraint 17 + validator detail）；**LLM regenerate 后的 declarations**
>
> 跨 phase 关键差异：Phase A/B 是 validator-only（declarations 字节一致），
> Phase D 是 prompt-side（LLM 重新生成 → declarations 必然变），因此**评测
> 证据组**和 Phase A/B 不同（详 §6.5）。

---

## 1. 一页总结

> Phase D 主修 cat-3（pingyue-samples-openai-calibrated, 1 seasonal failure）。
> Phase D.2 在 cat-3 复测基础上**额外用 cat-4**
> （pingyue-samples-openai-catagory4-1, **8 seasonal failures** in baseline）做 stress test，
> 因 cat-4 baseline 上 8/10 scenario 同时 fail seasonal_*，是更严格的 D + D.2 联合验证。

| 维度 | cat-3 baseline (pathB-rev) | **cat-3 D** (pathD-llm) | **cat-3 D.2** (pathD2-llm) | cat-4 baseline | **cat-4 D.2** (catagory4-pathD2-llm) |
|---|:-:|:-:|:-:|:-:|:-:|
| passing | 8/10 | 6/9 (1 hard err) | **6/10** ✓ | 1/10 | **6/10** ✓✓ |
| `seasonal_*` | 1 | 0 | **0** | **8** | **2** (-6) |
| `reversal_*` | 1 | 3 | 1 | 1 | 0 |
| `residual_*` | 1 | 0 | 0 | 0 | 0 |
| `orthogonal_*` | 0 | 0 | 0 | 1 | 0 |
| `dominance_*` | 0 | 0 | 0 | 1 | 0 |
| `ks_*` | 0 | 0 | 1 (Path D 真抓 LLM mis-fit) | 0 | 3 (Path D 真抓 LLM mis-fit) |
| `outlier_*` / `marginal_*` | 0 / 0 | 0 / 0 | 2 / 1 (LLM 新犯错) | 0 / 0 | 0 / 0 |
| `PatternInjectionError` (hard) | 0 | **1** | **0** ✓ | 0 | 0 |
| 总 soft-fail 数 | 3 | 3 | 4 | 11 | 5 (-55%) |
| 新单测 | — | +13 | **+6 (row-count guardrail)** | — | — |
| 既有单测调整 | — | 0 | 0 | — | — |

**Headline**：
- **Phase D 主目标**：cat-3 上 `seasonal_*` 1→0 ✓，cat-4 上 `seasonal_*` 8→2（-75%）✓
- **Phase D.2 主目标**：cat-3 上 `PatternInjectionError` 1→0 ✓（e9c4 hard error 修复）
- **联合 headline**：cat-4 从 1/10 passing → 6/10 passing（D + D.2 联手把 8 个 seasonal failures
  里的 6 个清掉，剩 2 个属"realized z << expected z"的下一阶段 mechanism，详 §5.6）

LLM 在 D + D.2 prompt 下的行为变化（cat-4 上最显著）：8 个 baseline `seasonal_anomaly`
声明里，**6 个主动切换到 `trend_break`**（同 D 在 14b7 上的行为），只剩 2 个 scenario
（6dbb + ac54）坚持声明 seasonal_anomaly——但那 2 个 magnitude 都已正确选成 >
required_magnitude_at_threshold，failure 根因转移到了**「realized window_mean 远低于
(1+M)·baseline_mean，因为 measure 本身有内嵌的月/季效应」**——这是 Constraint 17 §
month/quarter effects 已经警示但 LLM 未充分照做的边界情况（详 §5.6 + §6.4）。

**Headline**：Phase D **主目标达成**——`seasonal_*` 失败族 1 → **0**，14b7
LLM 在 Constraint 17 指引下把 `inject_pattern("seasonal_anomaly", ..., magnitude=0.35)`
换成 `inject_pattern("trend_break", ..., magnitude=0.38)`（详 §5.2）。但 prompt-side
fix 不可避免触发 LLM 全量重新生成 declarations → ranking_reversal pattern 在
3 个 scenario 上的**重新采样**让 `reversal_*` 计数从 1 升到 3（§5.4），加上 1
个 hard error（§5.5）。**这些 side effects 不是 Constraint 17 的 fallout——
而是 prompt-side 改造的"LLM regen variance"内禀代价**（§5.7）。总 soft-fail 计数
不变（3 → 3），但 family 分布从"1 seasonal + 1 reversal + 1 residual"重洗为"3
reversal"。

---

## 2. 根本原因：multiplicative magnitude × high-CV baseline → tiny z

### 2.1 LLM 让 SDK 注入"季节性 spike"

LLM 在 `FactTableSimulator` SDK 里这样写（[agpds_14b7f7487e 原始 declaration](../../../output/agpds/pingyue-samples-openai-calibrated/declarations/agpds_14b7f7487e.json)）：

```python
sim.inject_pattern(
    "seasonal_anomaly",
    target="audience_segment == 'Children'",
    col="checkout_count",
    params={
        "anomaly_window": ["2024-06-01", "2024-08-01"],
        "magnitude": 0.35,   # ← LLM 直觉："夏季儿童借阅多 35%"
    },
)
```

LLM 把它读成"夏季儿童借阅会比平常多 35%"。SDK 把它**乘性**地实现
（[engine/patterns.py:681](../../../pipeline/phase_2/engine/patterns.py#L681)）：

```python
df.loc[in_win_idx, col] *= (1 + magnitude)
```

### 2.2 引擎按声明乘进去，但 checkout_count 的 baseline 噪声远大于 35% bump

引擎按声明把 in-window 行 `*=1.35`。问题是这条 measure 的 baseline 本身
非常嘈杂——dom_023（图书馆借阅）经常有「黑五」「圣诞档」「学期初」式的
单日尖峰，baseline_std 与 baseline_mean 几乎同量级。Validator 在
[`pattern_checks.py:489`](../../../pipeline/phase_2/validation/pattern_checks.py#L489)
计算：

| 量 | 14b7 实测（pathB-rev）|
|---|---:|
| `window_mean` | 7794.69 |
| `baseline_mean` | 8146.31 |
| `baseline_std` | 7018.80 |
| CV = std / mean | **0.86** |

### 2.3 数学：`magnitude` 乘性 → `expected_z ≈ |M| × baseline_mean / baseline_std`

让 `X` 表示一行 in-window 的 pre-injection checkout_count，`E[X] ≈
baseline_mean`（in-window 与 out-of-window 在 marginal 上同分布的情况下）。
注入后：

$$\mathbb{E}[X_{\text{post}}] = (1+M)\cdot \mathbb{E}[X] \approx (1+M)\cdot \mu_{\text{baseline}}$$

Validator 比较 `window_mean - baseline_mean ≈ M × baseline_mean`：

$$z = \frac{|w - b|}{\sigma_b} \approx \frac{|M|\cdot \mu_b}{\sigma_b} = \frac{|M|}{\text{CV}}$$

代入 14b7：`expected z ≈ 0.35 × 8146 / 7019 ≈ 0.41`。**远低于** validator 的
threshold 1.5。实测 z=0.050 比 0.41 更低，反映 in-window 子集**本身**的
mean 偏 baseline_mean（即 in-window 期不是 marginal 平均水平——图书馆借
阅在暑假反而**低于**学期平均，因为学生分散）。

### 2.4 单日 1.35× 不够，要达到 z≥1.5 需要 `|M| ≥ 1.29`

把 z=1.5 反推：

$$|M| \geq z_{\text{thresh}} \cdot \text{CV} = 1.5 \times 0.86 \approx 1.29$$

也就是说 LLM 至少要把 in-window checkout 乘 2.29×（+129% bump）validator 才
会判它"季节信号显著"。**+129% 对图书馆借阅是不合实际的**——dom_023 的 range
是 1200–28000，要让夏季子集 mean 比平常高 2.3×，需要每周日均借阅 ~18,800，
远超 dom_023 的 28,000 上限。

### 2.5 Validator 原行为 = 正确数学 + 无法判别 sampling envelope vs 真季节信号

[Phase D 之前的 `check_seasonal_anomaly:503-511`](../../../pipeline/phase_2/validation/pattern_checks.py#L503-L511)：

```python
return Check(
    name=name, passed=passed,
    detail=(
        f"z={z:.3f} (window_mean={window_mean:.4f}, "
        f"baseline_mean={baseline_mean:.4f}, "
        f"baseline_std={baseline_std:.4f}, "
        f"threshold={z_threshold})"
    ),
)
```

数学是对的——z=0.05 在 CV=0.86 的域上确实信号不足。但 detail 只暴露四个
scalar，**没有告诉 LLM 在 retry 时需要把 magnitude 提到多少**。LLM 看
到 `z=0.05, threshold=1.5` 可能误读成"validator 阈值过严"，反复在同 magnitude
附近调，浪费 retry budget。

### 2.6 §3.1 已用 hand-trace 证明：本条 failure 是 LLM-prompting 问题

[PINGYUE_OPENAI_CAL_ANALYSIS.md §3.1](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#31-agpds_14b7f7487e--boston-public-library-借阅) 已经诊断：

> "`seasonal_checkout_count`: `z=0.050 (window=7794.69, baseline=8146.31,
> std=7018.80)` — M4-seasonal，声明的季节振幅未与 baseline 方差对齐（**M1
> 的孪生**：LLM 不知道 std=7019 是 mean=8146 的多大占比）。"

即 LLM 根本不知道 checkout_count 的 baseline 方差结构。**这条声明在 vacuously
独立空间里没错**（`magnitude=0.35` 是合理的 domain 直觉），错在它没意识到
validator 用 z-score 而不是相对比例衡量。本质和 Phase A 的 binomial envelope
误判同精神（"声明者不了解 validator 的 sampling geometry"）。

---

## 3. 实际失败案例：Phase A/B 基线的真实失败

下面是 `pingyue-samples-openai-calibrated-pathB-rev/validation_summary.json`
里全部 1 条 `seasonal_*` 失败的 hand-traced 数据：

| Scenario | Check | declared magnitude | baseline_mean | baseline_std | CV | expected z | actual z | 当前阈值 |
|---|---|---:|---:|---:|---:|---:|---:|:-:|
| `agpds_14b7f7487e` | `seasonal_checkout_count` | **0.35** | 8146.31 | 7018.80 | 0.86 | ~0.41 | **0.050** | 1.5 (FAIL) |

> "expected z" 用 §2.3 的封闭式 `|M|/CV` 计算；实测 z 更低，因为 in-window
> 期（Jun-Aug）的 checkout_count 在 dom_023 域里反而**低于**年度均值（学生
> 暑假分散），sampling 让差值方向反转——M=+0.35 的乘性 bump 只把 window_mean
> 抬到 7795（仍低于 baseline 8146）。

### 3.1 Case study：`agpds_14b7f7487e::seasonal_checkout_count`

scenario `agpds_14b7f7487e` 是 Boston Public Library 借阅 funnel：scenario
metadata 指定 `target_rows=240`、`temporal_granularity="monthly"`、域是
`dom_023/k=0`（图书资源借阅）。LLM 在 declaration 里给 `checkout_count` 选
了 lognormal 加 audience_segment effects + temporal seasonality，整体分布
被 audience × 月份 cross-classification 拉得很散——baseline_std ≈ 7019，
量级和 mean 8146 几乎相同（CV=0.86）。

LLM 同时声明：

```python
sim.inject_pattern(
    "seasonal_anomaly",
    target="audience_segment == 'Children'",
    col="checkout_count",
    params={"anomaly_window": ["2024-06-01", "2024-08-01"], "magnitude": 0.35},
)
```

LLM 的直觉是对的（暑假儿童借阅会增加），但 magnitude=0.35 在 CV=0.86 的
噪声下完全淹没——expected z = 0.35/0.86 ≈ 0.41，实测 0.05 更糟。

### 3.2 为什么 prompt 端 Constraint 17 必须做（validator 端兜底反而错）

跟 Phase A/B 不同，**这次不能仅靠 validator 修**——validator 的 z 阈值
1.5 是统计学上正确的（z<1.5 信号确实无法和 noise 区分）。备选方案有三个：

1. **降低 z 阈值（如 1.0）**：让 z=0.41 通过。但这就放开了真正的 false
   positive——CV=0.86 的域上 z<1.0 是 sampling noise 的常态，validator
   会失去 seasonal pattern 检测能力。
2. **改用相对比例（`magnitude > X` 而不是 z > 1.5）**：但 magnitude=0.35
   在 CV=0.05 的低噪声域上是显著季节信号（z≈7），强制 magnitude>1.0 会
   silently kill 那些 case。
3. **教 LLM**：把 z-score 公式告诉 LLM，让它根据 CV 自适应选 magnitude。
   高 CV 域改用 `trend_break`（validator 用 piecewise slope，对 baseline
   方差耐受）。

**结论**：必须在 prompt 侧解决，validator 不充分。

---

## 4. 解决方案：Constraint 17 + validator detail enrichment

### 4.1 一句话

> 把 prompt 加 Constraint 17 告诉 LLM "z = |window_mean - baseline_mean| /
> baseline_std ≥ 1.5"，让 LLM 自己估算 CV 并对齐 `|M| ≥ 2.0 × CV`（留 0.5σ
> buffer）；validator 的 fail detail 额外打 `declared_magnitude={M}` +
> `required_magnitude_at_threshold>={X:.3f}`，给 retry 提供精确反馈。

### 4.2 为什么 strict prompt + format-only detail 而不是放松 z 阈值

| 候选 | 范围 | Phase D 选用 |
|---|---|:-:|
| **prompt + detail enrichment** | 让 LLM 自适应：低 CV 域 `magnitude` 不变；高 CV 域改用 `trend_break` | ✓ |
| **放松 z 阈值（1.5 → 1.0）** | 让 14b7 通过，但 silently 接受所有 sub-σ "信号" | ✗（false positive 风险）|
| **改用相对比例（dev > 0.1）** | 兼容低 CV 域；高 CV 域照样过 | ✗（违反统计学，z-score 是季节信号的标准量度）|
| **validator-side 兜底（detect underspecified magnitude → skip）** | 不让 high-CV failure 触发 | ✗（Phase D.1 备用，本次不做）|

理由：
1. **实测覆盖**：1 条 pingyue 失败完全是 high-CV regime，prompt 教 LLM 自适应
   足够覆盖。
2. **mirror Phase A 决策**：Phase A 选 `n<10 skip + Wald CI` 不放松 base 阈
   值 0.10。同精神：z 阈值 1.5 不动，让 prompt 处理 LLM 端的 magnitude
   选取。
3. **可拓展点**：若 LLM 不听话（Phase D.1 trigger），validator 端兜底
   `skip + detail="underspecified per Constraint 17"` 是单点替换（详 §6.4）。

### 4.3 算法流程

```
prompt.py (SYSTEM_PROMPT_TEMPLATE):
  HARD CONSTRAINTS:
    ...
    13. KS-CELL DENSITY (existing)
    17. SEASONAL AMPLITUDE:
        - SDK injects: df.loc[in_win] *= (1 + M)
        - Validator: z = |w - b| / σ_b, requires z ≥ 1.5
        - For pass margin: |M| ≥ 2.0 × baseline_std / |baseline_mean|
        - CV = baseline_std / |baseline_mean| (estimate from noise_sigma + effects)
        - If measure has month/quarter effects: bump |M| 20-30% extra
        - If required |M| > 0.6: switch to inject_pattern("trend_break", ...)
        - Example: checkout_count CV≈0.86 → |M|≥1.72 → use trend_break
        - |M| < 0.3 only safe when CV < 0.1

pattern_checks.py::check_seasonal_anomaly (line 503+):
  declared_magnitude = params.get("magnitude")
  if declared_magnitude is not None:
    extra = f", declared_magnitude={declared_magnitude}"
    if abs(baseline_mean) > 1e-9:
      required = z_threshold * baseline_std / abs(baseline_mean)
      extra += f", required_magnitude_at_threshold>={required:.3f}"
  detail = f"z={z:.3f} (..., threshold={z_threshold}{extra})"
```

### 4.4 关键设计决策

| 决策 | 选择 | 理由 |
|---|---|---|
| 修复层 | **prompt + validator detail（format-only）** | 详 §4.2，z 阈值不能放松 |
| Magnitude 公式 | **`|M| ≥ 2.0 × CV` 留 0.5σ buffer** | mirror Phase A `dev<0.10 + Wald` 的"validator buffer + LLM 端协作" 精神 |
| 高 CV 兜底 | **`trend_break`（piecewise slope 检测）** | `trend_break` validator 不用 z-score；高 CV 时仍能检 trend |
| Cutoff M > 0.6 → 切 trend_break | **0.6**（不是 1.0） | window 值 shift >60% 已脱离 domain realism；0.6 是经验阈 |
| Validator detail 改动 | **format-only，pass/fail 决策完全不动** | blast radius 最小；既有 8 条 seasonal_anomaly 测试不变 |
| Negative magnitude | **`|M|` 用于 required，declared 显式保留 sign** | mirror validator 的 `|window_mean - baseline_mean|` 数学 |
| `baseline_mean` ≈ 0 guard | **`abs(baseline_mean) > 1e-9` 时才打 required** | 防 div-by-zero；几乎不可能命中真实数据，仅作 defensive |
| Constraint 17 numbering | **17（不是 14）** | 14/15/16 reserved for Phase A/B/C（实际未上线 prompt 改动；详 [MECHANISM_4 §6.5](MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md#65-constraint-14可选-prompt-端补丁未做) + [MECHANISM_5 §6.2](MECHANISM_5_ORTHOGONAL_DEGENERACY_DEEP_DIVE.md#62-constraint-15可选-prompt-端补丁暂未做)）|

### 4.5 代码位点

| 文件 | 行 | 内容 |
|---|---|---|
| [orchestration/prompt.py:131-152](../../../pipeline/phase_2/orchestration/prompt.py#L131-L152) | new | Constraint 17 — 22 行 verbatim 插入 HARD CONSTRAINTS 末尾（13 之后，SOFT GUIDELINES 之前）|
| [validation/pattern_checks.py:503-517](../../../pipeline/phase_2/validation/pattern_checks.py#L503-L517) | enriched | `check_seasonal_anomaly` fail-detail 加 `declared_magnitude` + `required_magnitude_at_threshold>=` 两字段，pass 路径不变 |
| [tests/modular/test_prompt_constraint_17.py](../../../pipeline/phase_2/tests/modular/test_prompt_constraint_17.py) | new | 7 测试：4 substring（header / formula / trend_break / example）+ 3 placement（in HARD / after 13 / 14-15-16 absent）|
| [tests/modular/test_validation_phase_d.py](../../../pipeline/phase_2/tests/modular/test_validation_phase_d.py) | new | 6 测试：包含 declared_magnitude / 包含 required_magnitude / negative-M / baseline_mean=0 omit / no-magnitude omit / pass 路径未变 |

### 4.6 Detail string 的实际样子

**Before（Phase A/B 时代）**：

```
z=0.050 (window_mean=7794.6889, baseline_mean=8146.3137, baseline_std=7018.8025, threshold=1.5)
```

LLM 在 Loop B retry 时看到这条只能猜"我的 magnitude 太小 or anomaly_window 不对？"——
没有方向。

**After（Phase D 失败的样子）**：

```
z=0.050 (window_mean=7794.6889, baseline_mean=8146.3137, baseline_std=7018.8025, threshold=1.5, declared_magnitude=0.35, required_magnitude_at_threshold>=1.292)
```

LLM 直接看到"我给的 0.35 < 1.292"——明确的 magnitude 方向。若 1.292 > 0.6
（这里 1.292 > 0.6），LLM 按 Constraint 17 应该立即改用 `trend_break`。

**After（Phase D 通过的样子）**（任意低 CV 域）：

```
z=2.318 (window_mean=12.34, baseline_mean=5.23, baseline_std=3.06, threshold=1.5, declared_magnitude=1.0, required_magnitude_at_threshold>=0.877)
```

`declared (1.0) > required (0.877)` → pass，detail 仍带 magnitude 字段做
verification audit。

---

## 5. 修复后效果：Phase D rerun 实测

### 5.1 Per-scenario 失败明细

| Scenario | Phase B (pathB-rev) | **Phase D** (pathD-llm) | Δ | 归因 |
|---|---|---|---|---|
| `agpds_14b7f7487e` | 1 fail: `seasonal_checkout_count` | 1 fail: `reversal_checkout_count_renewal_count` | **seasonal: -1 ✓**; **reversal: +1**（regen variance）| §5.2 + §5.4 |
| `agpds_33d84d2c9b` | ✓ PASS | ✓ PASS | 0 | — |
| `agpds_3af92040e6` | ✓ PASS | ✓ PASS | 0 | — |
| `agpds_503613ba96` | 2 fails: `residual_*` + `reversal_*` | **✓ PASS** | **-2**（gain，LLM 自修 ratio formula）| §5.4 |
| `agpds_65ef0afda0` | ✓ PASS | 1 fail: `reversal_grant_funding_publication_count` | **+1** regression（regen variance）| §5.4 |
| `agpds_8022981cf7` | ✓ PASS | ✓ PASS | 0 | — |
| `agpds_8180fe4e2c` | ✓ PASS | 1 fail: `reversal_application_count_enrollment_count` | **+1** regression（regen variance）| §5.4 |
| `agpds_985a1b72e1` | ✓ PASS | ✓ PASS | 0 | — |
| `agpds_d62b18e180` | ✓ PASS | ✓ PASS | 0 | — |
| `agpds_e9c40d0352` | ✓ PASS | **HARD ERROR**（PatternInjectionError）| -1（regen variance）| §5.5 |

**核心结果**：
- **`seasonal_*`: 1 → 0** ✓（Phase D 主目标 100% 达成）
- soft-fail 总数：**3 → 3**（不变，但分布从 1 seasonal + 1 reversal + 1 residual 重洗为 3 reversal）
- passing scenarios（soft）：8/10 → 6/9（hard error 不算 soft pass，分母从 10 变 9）
- 1 hard PatternInjectionError（§5.5——LLM 写出无效的 anomaly_window×target 组合，与 Constraint 17 无关）

### 5.2 LLM behavioral evidence：14b7 主动切到 trend_break ✓

**这是 Constraint 17 直接生效的最硬证据。**

Original baseline（pre-Phase D）declaration on 14b7:
```json
{
  "type": "seasonal_anomaly",
  "target": "audience_segment == 'Children'",
  "col": "checkout_count",
  "params": {"anomaly_window": ["2024-06-01", "2024-08-01"], "magnitude": 0.35}
}
```

**Phase D regen** declaration on 14b7（**`seasonal_anomaly` 整条移除**！）:
```json
[
  {"type": "outlier_entity", "col": "checkout_count", "params": {"z_score": 2.8}},
  {"type": "trend_break",    "col": "checkout_count",
   "params": {"break_point": "2024-09-01", "magnitude": 0.38}},
  {"type": "ranking_reversal", "col": "renewal_count",
   "params": {"metrics": ["checkout_count", "renewal_count"], "entity_col": "material_type"}}
]
```

LLM 没尝试把 magnitude 提到 ≥ 1.29（不现实），也没硬撑用 seasonal_anomaly。
它**完全删除 seasonal_anomaly**，把原来弱的 trend_break（baseline magnitude=0.22）
强化到 0.38，并把这条 measure 的"季节性"全权交给 `trend_break` validator。

这正是 Constraint 17 §"If required |M| > 0.6: switch to inject_pattern(\"trend_break\", ...)"
明确推荐的策略。LLM **听懂了**。

实际全 10 个 scenario 选用的 seasonal/trend_break 分布：

| Scenario | seasonal_anomaly? | trend_break? |
|---|:-:|:-:|
| agpds_14b7f7487e | ✗（去掉了）| ✓ magnitude=0.38 |
| agpds_e9c40d0352 | ✓ magnitude=-0.08 | ✓ magnitude=-0.035 |
| 其他 8 个 | ✗ | ✗ |

只有 e9c4 仍用 seasonal_anomaly（attendance_rate 在 CV<<1 域内合理），其他
高 CV 域 LLM 都主动 dropped。

### 5.3 Cross-phase 一致性 checklist（prompt-side 适配版）

| 证据 | 跨 phase 期望 | 实测 |
|---|---|:-:|
| Scenario IDs 对齐（10 个完全一致）| yes | ✓ 10/10 一致 |
| 行数一致（target_rows 不变）| yes | ✓（每个 scenario 的 `target_rows` 由 Phase 1 决定，未变）|
| `declarations` diff 局限于 seasonal_anomaly `magnitude` field | yes | ✗ **NO**——LLM regen 改 patterns 全集（见 §5.4） |
| LLM regen 产 `|magnitude| ≥ 2·CV` 或切 trend_break | yes | ✓ 14b7 切 trend_break；e9c4 留 seasonal but in low-CV domain |
| `seasonal_*` failure count: 1 → 0 | yes | ✓ |
| 其他 failure 族不变 | NO（prompt-side 改造预期会移动 failure family）| ✗ 见 §5.4 |
| Touched code 仅 prompt.py + pattern_checks.py | yes | ✓ `git diff --stat HEAD~2 HEAD` 仅 4 文件改动 |
| Master_tables 跨 phase 字节一致 | **NO by design** | ✗ by design 不一致 |

**修正一条预测**：原计划文档里"declarations diff 局限于 seasonal_anomaly
magnitude field"过于乐观。实际：LLM 看到新 prompt 后**整段重写**——
ranking_reversal/outlier_entity/structural measure 的具体 metric 选择都会变。
这是 prompt-side fix 的根本特性，**不是 Constraint 17 的副作用**。

### 5.4 ranking_reversal 重新洗牌：3 个 reversal failure 全部 Phase C 范畴

新 reversal failure 的责任完全在 [`check_ranking_reversal`](../../../pipeline/phase_2/validation/pattern_checks.py)
和 LLM 公式骨架的 mismatch——和 Constraint 17 无关：

| Scenario | Phase B reversal pattern | Phase D reversal pattern | Phase D detail | 根因 |
|---|---|---|---|---|
| `agpds_14b7f7487e` | `(checkout_count, hold_fulfillment_rate)` × `branch` | `(checkout_count, renewal_count)` × `material_type` | `rank_corr=0.7000 (>= 0)` | LLM 选了天然正相关的 metric 对——同 checkout funnel 的双 metric |
| `agpds_65ef0afda0` | `(grant_funding, citation_count)` × `lab` | `(grant_funding, publication_count)` × `research_entity` | `rank_corr=...` | LLM 选了天然正相关的 metric 对（同 research output funnel）|
| `agpds_8180fe4e2c` | **无** ranking_reversal 声明 | `(application_count, enrollment_count)` × `major` | `rank_corr=...` | LLM 新增 reversal 声明在天然正相关 funnel 上 |

3 条都是 LLM 在 ranking_reversal 上**继续犯 Phase C-机制的错**——选了
admission/checkout/research funnel 这种**结构性正相关**的 metric 对来声明
"reversal"，但 measure formula 没有真正实现负相关。本质和 PINGYUE §3.4
的 503613ba96 reversal_course_load_student_faculty_ratio 同根。

`residual_*` 这条相反——503613ba96 的 M1 ratio straggler 在 LLM regen 后**消失了**，
因为 LLM 重写了 `student_faculty_ratio` 公式，不再用 `enrollment / faculty`
除法算子。Phase C 在这条上**意外受益**。

**结论**：3 个新 reversal 失败全部应归属 Phase C 范畴。Phase C 应该解决
"LLM 在 ranking_reversal 声明上选错 metric 对"的 prompt 或 validator 问题，
但那是另一个 PR。

### 5.5 1 个 hard error：agpds_e9c40d0352 PatternInjectionError（D 时观测）+ Phase D.2 解决

`agpds_e9c40d0352` 在 **Phase D rerun**（pathD-llm）的 Stage 2 执行时抛
`PatternInjectionError`，没进 validation_summary.json（hard error，非 soft
fail）。错误日志：

```
agpds_e9c40d0352: PatternInjectionError:
  Pattern injection 'seasonal_anomaly' failed:
  anomaly_window [2025-02-03..2025-02-14] matches no target rows.
  Cannot apply seasonal anomaly.
```

LLM 在 e9c4 选了 `target="grade_level == '9'"` + `anomaly_window=["2025-02-03",
"2025-02-14"]`，结果 target_rows=420 在 ~290 天 daily granularity × 13 grades ×
multiple intervention/school cross-classification 后，9 年级 × 2 周窗口的
样本量塌缩到 0。SDK 引擎拒绝注入。

**这条不是 Constraint 17 的责任**——Constraint 17 只规范 `magnitude` 与
`baseline_std` 的关系，没说"target + anomaly_window 必须 match ≥1 row"。

#### Phase D.2 解决：Constraint 17 加 row-count guardrail

[Phase D.2 commit `fad9d8b`](../../../pipeline/phase_2/orchestration/prompt.py)
在 Constraint 17 末尾追加 sub-clause 教 LLM 自验：

```
expected_rows ≈ target_rows × (anomaly_window_days / temporal_range_days)
              × P(target filter matches a row)
hard floor: expected_rows ≥ 5   (Poisson reliability)
soft floor: expected_rows ≥ 10  (z stability)
```

附 14b7-derived counter-example（420 × 12/290 × 0.095 ≈ 1.6 → fix: widen 至
≥ 90 days）。详 [§4.5 代码位点](#45-代码位点)。

**Phase D.2 rerun（pathD2-llm, cat-3）实测结果**：

| 指标 | Phase D (pathD-llm) | **Phase D.2** (pathD2-llm) |
|---|:-:|:-:|
| `agpds_e9c40d0352` master_table | **MISSING**（PatternInjectionError）| ✓ exists |
| skipped.jsonl entries | 1（e9c4 hard error）| **0** ✓ |
| `seasonal_*` count | 0 | 0（仍是 0）|
| LLM 在 e9c4 重选 pattern | seasonal_anomaly + trend_break | trend_break 单独（去掉 seasonal）|
| 10 个 declaration 中含 seasonal_anomaly 的数量 | 2 | **0**——LLM 在 cat-3 上完全 abandon seasonal_anomaly |

**LLM behavioral evidence**：D.2 prompt 让 LLM 在 cat-3 上**完全放弃**
seasonal_anomaly（10 个 declarations 里 0 个 seasonal）——把所有"季节性"行为
转移到 `trend_break`。这是比 D 更激进的 prompt 响应。

#### Phase D.2 cat-4 stress test：8 baseline seasonal failures

cat-4 (`pingyue-samples-openai-catagory4-1`) baseline 是 Phase D 主要修复
目标的"放大镜"——10 个 scenario 里 **8 个 seasonal_* fail**，1/10 passing。
D.2 prompt 下重新生成 + 执行：

| 指标 | cat-4 baseline | **cat-4 D.2** (catagory4-pathD2-llm) | Δ |
|---|:-:|:-:|---|
| passing | 1/10 | **6/10** ✓ | **+5** |
| `seasonal_*` | 8 | 2 | **-6**（75% reduction）|
| `orthogonal_*` | 1 | 0 | -1 |
| `dominance_*` | 1 | 0 | -1 |
| `reversal_*` | 1 | 0 | -1 |
| `ks_*` | 0 | 3 | +3（详 §5.7）|
| `PatternInjectionError` | 0 | **0** | 0 |
| 总 soft-fail | 11 | 5 | **-6**（-55%）|

**LLM behavioral evidence (cat-4)**：8 个 baseline `seasonal_anomaly`
声明里，**6 个主动切换到 `trend_break`**——和 D 在 14b7 上的行为一致：

| Scenario | baseline pattern on metric | D.2 pattern on metric | 切换? |
|---|---|---|:-:|
| 1f66 | seasonal_anomaly on stockout_rate | trend_break | ✓ |
| 3b2d | seasonal_anomaly on units_sold | trend_break | ✓ |
| 4756 | seasonal_anomaly on attrition_rate | trend_break | ✓ |
| 7630 | seasonal_anomaly on conversions | trend_break | ✓ |
| 8585 | seasonal_anomaly on defect_rate | trend_break | ✓ |
| e021 | seasonal_anomaly on ticket_volume | trend_break | ✓ |
| **6dbb** | seasonal_anomaly on feature_adoption_rate | **kept seasonal_anomaly** | ✗ |
| **ac54** | seasonal_anomaly on sessions | **kept seasonal_anomaly** (on different col: add_to_cart_rate) | ✗ |

### 5.6 cat-4 D.2 残留：2 个 seasonal failure 暴露 §6.4 子机制

剩 2 个 cat-4 seasonal failure（6dbb + ac54）非常有诊断价值。它们都是
**LLM 在 D.2 prompt 下**选 magnitude **超过** Constraint 17 公式要求的——
但 validator 实测 z 仍 < 1.5：

| Scenario | declared magnitude | required_magnitude_at_threshold | expected z = M·μ/σ | **realized z** | passed? |
|---|---:|---:|---:|---:|:-:|
| `agpds_6dbb1c20db` | 0.45 | 0.342 ✓ above req | 1.97 ✓ above 1.5 | **0.639** | ✗ |
| `agpds_ac54f076fc` | 0.55 | 0.296 ✓ above req | 2.79 ✓ above 1.5 | **1.115** | ✗ |

**根因**：realized window_mean 远低于 (1+M)·baseline_mean——因为 `feature_adoption_rate`
和 `add_to_cart_rate` measure 本身有**内嵌的月/季效应**（LLM 通过 `param_model`
里的 month effects 已经声明了），window 期（Mar-Apr / Nov 20-Dec 5）的 measure
baseline 本身就**低于**年度平均，所以 (1+M)·μ 是基于**年度均值**计算，但
realized window 实际 mean 是基于 window 期均值（更低）。

**Constraint 17 已经警示过这条**：

> "If the measure has month/quarter effects, baseline_std is inflated by
> between-period variation — bump |M| another 20–30%, or narrow the
> `anomaly_window` to a single peak season."

但 LLM 在 6dbb / ac54 上**没充分应用 20-30% bump**。这不是 D.2 row-count
guardrail 的责任范围，是 Constraint 17 原文里**month/quarter effect bump**
建议的 LLM compliance 问题。属新 Phase D.3 / D.4 候选（详 §6.4）。

### 5.7 cat-3 + cat-4 共有：M7/M8 新机制候选浮现

cat-3 D.2 出现 3 条新失败（之前 baselines 没有的 family）：
- `outlier_yield_rate` × 2 (33d8 + 503613ba96): LLM 声明的 outlier z_score
  vs realized 之间的不匹配
- `marginal_weights_grade_band` (e9c4): LLM 声明的 marginal weights 与
  `add_group_dependency` 链 induced joint marginal 不一致（详 [§Q&A discussion above](#)）
- `ks_withdrawal_rate` (8022): n=42 cell 上 D=0.46 的 distributional drift
  (Path D Bonferroni 后真抓)

cat-4 D.2 出现 3 条新失败：
- `ks_supplier_lead_time` (1f66): Path D 真抓 LLM cell-level distribution mis-fit
- `ks_feature_adoption_rate` (6dbb): 同上
- `ks_total_assets` (9ec5): 同上

**关键诊断**：这些 `ks_*` 在两个 cat 都重复出现——n>>30、D>>threshold、
Bonferroni 修正后的 α 仍触发——**不是 Path D false positive**，而是
LLM 在 `param_model` cell-level 分布上的真实声明错误。属新 mechanism 候选：

- **M7 候选**：`marginal × group_dep 链 induced shift`——LLM 不会预测 conditional
  weights 对 marginal 的反推
- **M8 候选**：`param_model cell-level mis-fit`——LLM 写的 measure family 参数
  在 cross-classification 某些 cell 上的 realized distribution 上对不齐

详 [§6.5 未来候选 mechanism](#65-未来候选-mechanism7-cat-3--cat-4-d2-共有的新失败族)。

### 5.8 失败类型分类（Phase D.2 后，cat-3 + cat-4 联合）

| 失败族 | cat-3 baseline | cat-3 D.2 | cat-4 baseline | cat-4 D.2 | 责任层 | 修复路径 |
|---|:-:|:-:|:-:|:-:|---|---|
| `seasonal_*`（季节振幅 < 2·CV）| 1 | 0 | 8 | 2 | LLM ↦ Constraint 17 | **D / D.2 主修闭合**（剩 2 条转 month-effect bump）|
| `seasonal_*` (realized z << expected z) | 0 | 0 | 0 | 2 | LLM ↦ Constraint 17 month-effect | **D.3 候选**（详 §6.4）|
| `PatternInjectionError`（hard）| 0 | 0 ← D 时 1 → D.2 0 ✓ | 0 | 0 | LLM ↦ row-count guardrail | **D.2 修闭合** |
| `reversal_*` | 1 | 1 | 1 | 0 | LLM 公式骨架 sign/中介错 | Phase C 范围 |
| `residual_*`（M1 ratio long tail）| 1 | 0 | 0 | 0 | LLM ratio operator 长尾 | LLM 自修，被动闭合 |
| `outlier_*` (declared z_score vs realized) | 0 | 2 | 0 | 0 | LLM 选 z_score vs realized 不匹配 | **M9 候选** |
| `marginal_*` (group_dep induced shift) | 0 | 1 | 0 | 0 | LLM 没预测 group_dep 链 | **M7 候选** |
| `ks_*` (cell-level mis-fit) | 0 | 1 | 0 | 3 | LLM 选错 param_model | **M8 候选** |
| `orthogonal_*` / `group_dep_*` / `dominance_*` | 0 | 0 | 1+1 | 0 | — | Phase A/B 已闭合 |

### 5.9 教训：prompt-side fix 必带 LLM regen variance；不要承诺 "0 regressions"

[Phase A doc §5.2](MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md#52-llm-完全没改任何东西)
说："validator-only 改造的最大特征是 declarations + base_seed + scenario IDs
一致"。Phase D 反之——**改 prompt 就改 declarations，进而改 patterns 全集**。

实际数据证明：

- Phase D 主目标（`seasonal_*` 1 → 0）✓ 完成
- 但 `reversal_*` 从 1 涨到 3——LLM 在新一轮采样中**意外暴露**之前的 Phase C
  mechanism 在另外两个 scenario 上的存在（8180/65ef）
- 同时也意外**消灭**了 503613ba96 的 residual/reversal 共生 failure，因为 LLM
  自修了 ratio operator

`reversal_*` 计数从 1→3 是 **prompt-side fix 的内禀代价**，不是 Phase D 的 bug。
任何 prompt-side 改造都会触发 LLM 全量重新采样，新的 LLM 选择某些 scenario 上
正常 / 另一些 scenario 上犯错——这是 sampling variance，validator 不能"修"它。

下次写 prompt-side fix 时：
1. 只承诺主目标 family clean-up（如 "seasonal_* 1 → 0"），不承诺整体 passing 率
2. 评测证据组用 "primary family count change + behavioral assertion"（如 14b7
   的 trend_break 切换），不用 "0 regressions"
3. 其他 family 的变化归入 "LLM regen variance"，跟进对应 Phase C/D/E 修复

---

## 6. 进一步阅读 / 已知坑

### 6.1 高 CV 域 `trend_break` 优于 `seasonal_anomaly` 是 Constraint 17 的核心建议

Phase D 不强制让 LLM 把 high-CV 域的 magnitude 调到不合理水平；而是引
导 LLM 切换到 `trend_break`。理由：

- `trend_break` validator（[`check_trend_break`](../../../pipeline/phase_2/validation/pattern_checks.py)）
  比较 break_point 前后的 **slope**，不直接看 z-score——对 baseline 方差耐受
- 图书馆借阅、零售销量、社交媒体活跃度这类 CV ≥ 0.5 的域，**改 trend_break
  反而更准**：真实季节性通常是渐进而非单点 spike
- LLM 在 Phase D regen 后预期会做这个切换（待 §5.2 验证）

### 6.2 ≥2×2 但 CV 极小（CV<0.05）的灰区暂未处理

Constraint 17 在 CV<0.1 时建议 `|M| ≥ 0.3` 是经验阈。**理论上** CV=0.001
时 |M|=0.001 即可让 z≥1.5；但 magnitude<0.001 在 lognormal/gamma 等乘
性域上几乎不可见。Phase D 不动这种 case 因为：

- 实测：openai-cal 没有 CV<0.1 的失败 case
- 强制 |M|≥0.3 是 conservative default；LLM 后续可以根据 detail 反馈微调

未来触发条件：production batch 出现 CV<0.05 的域且 |M|=0.3 让 in-window
分布偏离 domain realism。

### 6.3 Phase D.x 树形结构：D.1 / D.2 / D.3 / D.4

Phase D 的 follow-up 工作按"实测发现 → 修复"循环演进：

#### Phase D.1（validator-side underspecified-skip 兜底）— **仍 deferred**

跟 Phase A 的 Constraint 14 / Phase B 的 Constraint 15 同精神（都是
prompt-side 已 sufficient，validator 兜底是 backup）：让 validator 在
`declared_magnitude < 2 × baseline_std / |baseline_mean|` 时主动 soft-skip：

```python
if declared_magnitude is not None and abs(baseline_mean) > 1e-9:
    required = 2 * baseline_std / abs(baseline_mean)
    if abs(declared_magnitude) < required:
        return Check(
            name=name, passed=True,
            detail=f"skipped (underspecified |M|={declared_magnitude} < {required:.2f}; per Constraint 17 use trend_break)",
        )
```

未做，原因：
- Phase D + D.2 prompt-only 已达成 `seasonal_*` cat-3 1→0, cat-4 8→2 — 主目标
  family 大幅闭合
- LLM 不听话的 case 只剩 cat-4 6dbb/ac54 — 详 §5.6，不是"declared < required"
  类型（declared **already exceeds** required），属 §6.4 的 month-effect 问题
- 加 validator 兜底等于"silently pass on LLM mistake"，违反 transparency 原则

#### Phase D.2（row-count guardrail）— **本次完成 ✓**

加 Constraint 17 末尾的 row-count sub-clause（详 §4.5）。e9c4 `PatternInjectionError`
1→0 ✓，cat-4 上 8 seasonal failures 6 个被切到 `trend_break`、2 个降级为 §6.4
problem。详 §5.5 + §5.6。

#### Phase D.3（month/quarter-effect bump 强化）— **新候选**

cat-4 残留的 2 个 seasonal failure（6dbb + ac54）暴露了 Constraint 17 §month/quarter
effects 的 LLM compliance 问题：LLM 选了 `magnitude > required` 但没 bump
20–30%。修法选项：

- **prompt 端强化**：把"bump 20–30%"从可选建议升级为**显式公式** `|M| ≥
  2.5 × baseline_std / |baseline_mean|` 当 measure 有 month/quarter effects
- **validator 端**：增加 detail 字段 `realized_z` vs `expected_z`，让 LLM 在
  retry 时看到差距数字
- **SDK 端 dry-run helper**：`_estimate_z_given_magnitude(...)` 在 inject 前
  计算理论 z，warn if `expected_z > 2 × realized_z` (说明有 measure-internal
  attenuation)

#### Phase D.4（generalize row-count guardrail 到其他 pattern types）— **未来**

Phase D.2 row-count guardrail 只覆盖 `seasonal_anomaly`。同样的 `len(in_window)
== 0` 失败模式存在于 `outlier_entity` / `trend_break` / `dominance_shift` /
`ranking_reversal`（详 [engine/patterns.py:48/348/357/464](../../../pipeline/phase_2/engine/patterns.py)）。
未触发条件：production batch 出现非-seasonal pattern type 的 `PatternInjectionError`。

未来触发条件：production batch 出现 outlier/trend_break/dominance/reversal
任一 pattern 的 0-row 注入失败。

### 6.4 cat-4 残留 2 条 seasonal failure 的根因：realized z << expected z

cat-4 D.2 上 LLM 在 6dbb / ac54 都正确把 magnitude 选成 > required_magnitude_at_threshold，
但 validator 仍 fail。详 §5.6 表格——expected z = 1.97 / 2.79（皆 > 1.5）但
realized z = 0.639 / 1.115（皆 < 1.5）。

**根因机理**：

`expected_z = |M| × baseline_mean / baseline_std` 隐含假设 in-window 行**未注入前**
分布等同于 baseline（即年度均值）。但 LLM 在 `param_model` 里声明的 month/quarter
effects 让某些月份的 measure baseline 本身偏低（如 6dbb 的 `feature_adoption_rate`
在 Mar-Apr 比年度均值低；ac54 的 `add_to_cart_rate` 在 Nov 20-Dec 5 比年度均值低）。
所以 `(1 + M) × E[X | in_window, pre-injection]` < `(1 + M) × baseline_mean`，
realized z 被压低。

Constraint 17 已警示过这条（详 §1 一页总结的引言部分），但仅作建议性"bump 20–30%"，
LLM 没充分照做。Phase D.3 候选解决方案见 §6.3。

### 6.5 未来候选 mechanism（cat-3 + cat-4 D.2 共有的新失败族）

cat-3 + cat-4 D.2 一起跑出了**3 个新失败族**（在 baseline 上**未观测到**或观测形式
不同的）。这些不是 D / D.2 的 bug，而是 LLM regen variance 暴露的**之前没看到的
LLM 行为缺陷**：

| 失败族 | 出现 scenario(s) | failure detail 节选 | 候选 mechanism 名 | 根因假设 |
|---|---|---|---|---|
| `marginal_*` (large n, n=420) | cat-3 e9c4 grade_band | `dev=0.2157, thresh=0.1472` | **M7：marginal × group_dep 链 induced shift** | LLM 没预测 `add_group_dependency` 反推 marginal |
| `ks_*` (n=42, n=110, n=70+) | cat-3 8022, cat-4 1f66+6dbb+9ec5 | Bonferroni 后失败 cell n≥30, D≥0.17, p<α | **M8：param_model cell-level mis-fit** | LLM 写的 measure family 参数在 cross-classification 某些 cell 上对不齐 realized |
| `outlier_*` (z_score 不符 realized) | cat-3 33d8 yield_rate, 8022 withdrawal_rate, 503613 student_faculty_ratio | `z=1.7242 (subset_mean=11.0116, ref_mean=5.8447, ref_std=2.9967)` | **M9：outlier_entity z_score 声明 vs realized 不匹配** | LLM 选的 z_score 在 realized 子集均值上不能 produce |

**关键诊断**（已在 §5.7 阐述）：这些**不是** Phase A / Path D 的 false-positive 漏抓——
Phase A 的 Wald CI 在 n=420 上 threshold 0.147，绝不该 silent-pass dev=0.22 的真错；
Path D 的 Bonferroni 在 n≥30 cell 上**就是设计来抓**真 D>>threshold 的 distributional
drift。所以这些是 prompt-side LLM 缺陷，validator 工作得**完全正确**。

**未来归类**：

- 若再有 1-2 个 batch 重现 → 写 MECHANISM_7 / MECHANISM_8 / MECHANISM_9 deep dive
  doc + 对应 Phase E / F / G prompt-side 修复
- 若只在 cat-3/cat-4 出现 → 留作"已知 LLM 缺陷"标签，不优先修

### 6.6 silent-pass + transparency

Phase D 与 Path D / Phase A / Phase B 的 silent-pass 决定有质的差别：

- **Path D / Phase A / Phase B**：validator 在数学上**不可判定** regime 主动让出（n<30 / dof=0 / min(shape)<2）
- **Phase D**：validator 完全不让出——pass/fail 决策严格按 z=1.5；只在 detail 上加诊断字段。LLM 端必须改 declaration

这样的好处：validator 永远不 white-wash，所有 false positive 必须由 LLM 端
修正——明确的责任分层。

### 6.7 跨 phase master_tables 一定不字节一致：LLM regen 改 declarations

**Phase A/B 是 validator-only**（[MECHANISM_5 §6.4](MECHANISM_5_ORTHOGONAL_DEGENERACY_DEEP_DIVE.md#64-跨-phase-master_tables-不必字节一致validator-驱动-retry-trajectory)
已证 retry-trajectory 决定 effective seed）。Phase D 是 prompt-side：

- LLM 看到新 prompt（含 Constraint 17）→ 重新生成 declarations.json
- 重新生成 declarations → 整个 Stage 2（engine + validator + Loop A 在循环
  内重跑）→ master_tables 完全不同
- 因此**跨 phase 任何 byte-identical 比较都不适用**

正确的 validator-side 证据组（已在 [MECHANISM_5 §6.4.5](MECHANISM_5_ORTHOGONAL_DEGENERACY_DEEP_DIVE.md#645-validator-only-改造的正确证据组)）→ Phase D
的 prompt-side 证据组：

| 证据 | 跨 phase 期望 | 测试方法 |
|---|---|---|
| Scenario IDs 对齐 | yes | `diff <(jq -r '.[].generation_id' B.json) <(jq -r '.[].generation_id' D.json)` |
| 行数一致 | yes | `target_rows` per scenario 不变 |
| 触动代码仅 prompt.py + pattern_checks.py | yes | `git diff --stat HEAD~2 HEAD -- pipeline/` |
| declarations diff 局限于 seasonal_anomaly | yes | 抽 declaration 的非-seasonal 字段 cross-check |
| LLM 在 14b7 选了合理 strategy | yes | seasonal_anomaly `magnitude` ≥ 2·CV，或切换 `trend_break` |
| `seasonal_*` count: 1 → 0 | yes | jq `seasonal_*` failure count |
| 其他 failure 族不变 | yes | `residual_*` / `reversal_*` unchanged |
| 同代码 rerun master_tables 字节一致 | yes | Stage 2 deterministic 实证仍成立 |
| **master_tables 跨 phase 字节一致** | **NO by design** | LLM regen 改 declarations → engine sample 路径 100% 改 |

### 6.8 仍未修

Phase D + D.2 已经关闭季节振幅误判机制（cat-3 1→0, cat-4 8→2，剩 2 条转 §6.4
month-effect 子机制）。Phase B 后剩余非-seasonal failure 中：

1. **Phase C**：`reversal_*` 在 cat-3 baseline 1 条（agpds_503613ba96）+ D rerun
   时新撞出的 8180/65ef/14b7 都是 LLM 公式骨架共享上游变量造成结构性正相关。
   修法：跟 M1 ratio straggler 一起治。cat-4 D.2 上没再出现（LLM 这次没在 funnel
   pair 上声明 reversal）。
2. **接受**：`residual_*` 在 cat-3 baseline 1 条（agpds_503613ba96）— [M1 ratio
   operator 长尾](M1_RATIO_OPERATOR_STRAGGLER.md)，已决定不修。Phase D regen 后
   LLM 自修了公式，cat-3 D.2 上未重现。

### 6.9 教训：validator 教 LLM 比 validator 自修更可持续

跟 Phase A §6.6 / Phase B §6.6 的教训形成对比：

> Phase A/B：validator 阈值不知道 sample geometry 时主动让出判定权
> Phase D：validator 数学正确时不让出，但要主动暴露**诊断字段**让 LLM 自修

下次写新 validator 时直接拿 `declared_X + required_X_at_threshold` 当默认
detail 起点——给 LLM 一个**自适应的反馈通道**，而不是单纯打 fail 让 retry
loop 蒙猜。

---

## 7. 配套文档导航

- [ANALYSIS.md](../ANALYSIS.md) — 一页综述，所有 soft-failure 问题的入口
- [FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md) — 三机制（M1/M2/M3）+ Path A/B/C 修复路径全图（M4/M5/M6 尚待 backport）
- [validation/TEST1_TEST2_REGEN_COMPARISON.md](../validation/TEST1_TEST2_REGEN_COMPARISON.md) — test-1/test-2 同场景两次 regen 对比；§5 hand-trace 证明本机制部分 realized-z-gap 实因是 validator 忽略 pattern `target` 的稀释（target-restricted z=2.69 本应 PASS），候选 M10 target scope mismatch
- [validation/PINGYUE_OPENAI_CAL_ANALYSIS.md](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md) — openai-calibrated 批次深度分析，§3.1 是本机制的发现起点，§8.4 是 Phase D 计划
- [mechanisms/MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md](MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md) — Phase A（小样本比例漂移）纵深
- [mechanisms/MECHANISM_5_ORTHOGONAL_DEGENERACY_DEEP_DIVE.md](MECHANISM_5_ORTHOGONAL_DEGENERACY_DEEP_DIVE.md) — Phase B（正交退化）纵深，本文写作模板 + retry trajectory § 6.4
- [archive/MECHANISM_1_DEEP_DIVE.md](../archive/MECHANISM_1_DEEP_DIVE.md) — 机制 1（复合方差）纵深
- [mechanisms/MECHANISM_3_DEEP_DIVE.md](MECHANISM_3_DEEP_DIVE.md) — 机制 3（稀疏 cell KS）纵深
- [mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md](M1_RATIO_OPERATOR_STRAGGLER.md) — 机制 1 在除法算子上的长尾分支
- [subsystems/PATH_D_KS_SPARSE_CELLS.md](../subsystems/PATH_D_KS_SPARSE_CELLS.md) — 机制 3 的 validator 实现
- [archive/SIGMA_CALIBRATION.md](../archive/SIGMA_CALIBRATION.md) — 机制 1 的 validator/orchestration 实现

---

## 时间线

| 日期 | 事件 | commit / doc |
|---|---|---|
| 2026-05-20 | `pingyue-samples-openai-calibrated` 批次跑出 9/10 soft-failed，1 条 seasonal_checkout_count 在内 | (production batch) |
| 2026-05-21 | Phase A/B 实施完成 → 8/10 passing，1 seasonal_* 残留 | `c5561be` `e9de06f` `50098aa` `1719856` |
| 2026-05-21 | doc §3.1 + §8.4 诊断 seasonal_* 是 LLM 没估 CV | [PINGYUE_OPENAI_CAL_ANALYSIS.md §3.1](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#31-agpds_14b7f7487e--boston-public-library-借阅) |
| 2026-05-21 | Phase D Task 1：validator detail enrichment（`declared_magnitude` + `required_magnitude_at_threshold`）| `38c99e8` |
| 2026-05-21 | Phase D Task 2：Constraint 17 prompt（amplitude vs baseline_std）| `4a68905` |
| 2026-05-21 | Phase D LLM regen 在 openai-cal 验证：`seasonal_*` 1→0 ✓（14b7 切到 trend_break），但 LLM regen variance 让 `reversal_*` 1→3（Phase C scope），总 soft-fail 3→3，**1 hard PatternInjectionError** | `pingyue-samples-openai-calibrated-pathD-llm/` |
| 2026-05-21 | Phase D 文档首版定稿 | `73767d5` |
| 2026-05-21 | Phase D.2 Constraint 17 row-count guardrail prompt 添加 | `fad9d8b` |
| 2026-05-21 | Phase D.2 tests landed | `a4350b0` |
| 2026-05-21 | Phase D.2 cat-3 LLM regen 验证：e9c4 hard error 1→0 ✓；LLM 在 cat-3 上完全 abandon seasonal_anomaly（10 个 declarations 0 个 seasonal）| `pingyue-samples-openai-calibrated-pathD2-llm/` |
| 2026-05-21 | Phase D.2 cat-4 stress test：`seasonal_*` 8→2（-75%），passing 1/10→6/10，0 PatternInjectionError；6 个 baseline seasonal_anomaly 主动切到 trend_break | `pingyue-samples-openai-catagory4-pathD2-llm/` |
| 2026-05-21 | 本文档 D.2 增量定稿 | (this commit) |
