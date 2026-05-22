# M6 子机制：realized z << expected z（Phase D.3 候选，**未修**）

> **状态**：Deferred / 等候 future session 拾起。
> **触发批次**：[`pingyue-samples-openai-catagory4-pathD2-llm`](../../../output/agpds/pingyue-samples-openai-catagory4-pathD2-llm) §`agpds_6dbb1c20db` + `agpds_ac54f076fc`。
> **关联主文档**：[MECHANISM_6 §6.3 Phase D.3](MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md#63-phase-dx-树形结构d1--d2--d3--d4) + [§6.4 cat-4 残留](MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md#64-cat-4-残留-2-条-seasonal-failure-的根因realized-z--expected-z)。
> **范围**：仅适用 `seasonal_anomaly` validator + 带 month/quarter effects 的 measure。

---

## 1. TL;DR

Phase D + D.2 让 LLM 在 cat-4 上把 8 个 baseline `seasonal_anomaly` 中的 6 个主动
切到 `trend_break` ✓。**剩下 2 个**（6dbb, ac54）坚持 `seasonal_anomaly` 并按
Constraint 17 公式选了 `magnitude > required`——**但 validator 实测 z 仍 < 1.5
失败**。

根因：**LLM 用「年度均值」当 baseline 算 required magnitude，validator 用「out-of-window
均值」当 baseline 测 z**。当 LLM 自己在 `param_model` 里声明了 month/quarter effects、
且 anomaly_window 恰好落在 effect 把 measure 拉低的月份上，两者会显著背离——LLM 算
出来的 `expected_z` 远大于 validator 测出的 `realized_z`。

Constraint 17 §month/quarter effects 已经提示过"bump |M| 20–30%"，但 LLM 在 6dbb /
ac54 没充分应用。

---

## 2. 具体观测：6dbb + ac54 hand-traced 数据

### 2.1 `agpds_6dbb1c20db::seasonal_feature_adoption_rate`

**LLM 在 D.2 prompt 下选的 declaration**：

```json
{
  "type": "seasonal_anomaly",
  "target": "primary_feature == 'Help Center feature usage'",
  "col": "feature_adoption_rate",
  "params": {
    "anomaly_window": ["2024-03-01", "2024-04-30"],
    "magnitude": 0.45
  }
}
```

**Validator failure detail**（D.2 enriched format）：

```
z=0.639 (window_mean=59.3019, baseline_mean=51.7536, baseline_std=11.8160,
         threshold=1.5, declared_magnitude=0.45,
         required_magnitude_at_threshold>=0.342)
```

**LLM 的脑内推理**（合理重构）：

- declared param_model: `feature_adoption_rate` 大致 mean ≈ 60, noise_sigma ≈ 12
- required magnitude (per Constraint 17): `1.5 × 12 / 60 = 0.3`
- LLM 选 `M = 0.45 > 0.342 = required_magnitude_at_threshold` ✓
- expected z = `0.45 × 51.75 / 11.82 ≈ 1.97` ≥ 1.5 ✓（**用 validator 测的 baseline_mean 反算也是这样**）

**实际 validator 测量**：

- window_mean = 59.30（Mar-Apr 注入后均值）
- baseline_mean = 51.75（其余 10 个月均值）
- baseline_std = 11.82
- realized z = `(59.30 − 51.75) / 11.82 ≈ 0.639` ❌

### 2.2 `agpds_ac54f076fc::seasonal_add_to_cart_rate`

**LLM declaration**：

```json
{
  "type": "seasonal_anomaly",
  "target": "device_type == 'Mobile Web'",
  "col": "add_to_cart_rate",
  "params": {
    "anomaly_window": ["2024-11-20", "2024-12-05"],
    "magnitude": 0.55
  }
}
```

**Validator detail**：

```
z=1.115 (window_mean=13.7264, baseline_mean=11.2535, baseline_std=2.2172,
         threshold=1.5, declared_magnitude=0.55,
         required_magnitude_at_threshold>=0.296)
```

同模式：`M = 0.55 > 0.296 = required`；`expected z ≈ 2.79`；`realized z = 1.115` < 1.5。

---

## 3. 数学解释：为何 expected ≠ realized

### 3.1 LLM 算的 expected_z 隐含假设

LLM 看 Constraint 17 公式 `|M| ≥ 1.5 × σ/μ` 时心里这样跑：

```
window_mean_after_injection ≈ (1 + M) × E[X]
                            = (1 + M) × baseline_mean      ← 隐含假设：in-window 行未注入前 distribution ≡ baseline
```

所以：

```
shift = window_mean − baseline_mean
      ≈ (1 + M) × baseline_mean − baseline_mean
      = M × baseline_mean

expected_z = M × baseline_mean / baseline_std
           = M / CV
```

得到 `M ≥ 1.5 × CV` 的封闭式。

### 3.2 真实数据生成里 in-window baseline ≠ baseline

但 LLM 在 `param_model` 里**自己声明了 month effects**（举 6dbb 推测）：

```python
sim.add_measure("feature_adoption_rate",
    family="lognormal",
    param_model={
        "mu": {
            "intercept": ln(60),      # ≈ 4.09
            "effects": {
                "month": {
                    "Jan": +0.02, "Feb": -0.01, "Mar": -0.08, "Apr": -0.07,    ← Mar-Apr 被拉低
                    "May": +0.05, "Jun": +0.06, ...                              ← May-Jun 被推高
                    "Nov": -0.02, "Dec": +0.03,
                }
            }
        },
        "sigma": {"intercept": 0.20}
    })
```

那么对**未注入前**的 in-window 行（Mar-Apr）：

```
E[X | in_window, pre-injection] = exp(4.09 + month_effect)
                                 ≈ exp(4.09 - 0.075)
                                 ≈ 55.6                  ← 比年度均值 60 低 ~7%
```

对 out-of-window 行（其他 10 个月平均，含 May-Jun 的 +0.05/+0.06）：

```
E[X | out_of_window] ≈ 51.75 (实测 from validator)
```

注入后：

```
window_mean_after_injection = (1 + 0.45) × E[X | in_window, pre]
                            ≈ 1.45 × 55.6
                            ≈ 80.6                       ← 理论值
```

实测 `window_mean = 59.3`，比理论值 80.6 还低——可能因为 LLM 的 month effects 比我推测的更大、或者 `target = 'Help Center feature usage'` filter 再叠了一层效应。

无论如何，**实测 `shift = 59.3 − 51.75 = 7.55`，realized z = 7.55 / 11.82 = 0.639**。LLM 心里算的 shift 是 `0.45 × 51.75 = 23.3`，z = 1.97——**差了 3 倍**。

### 3.3 几何直觉

```
                       ← baseline_mean (51.75) ←
                              │
   in-window pre-injection ──┤
   (Mar-Apr 自带偏低 ~55.6)   │            ↗ window_mean (59.3)
                              │           ╱
                              │     ↗ ↗  ↗
                              │  ↗ ↗  注入 ×1.45
                              │
   out-of-window               ↑
   (51.75)                  validator 测量 shift = 59.3 - 51.75 = 7.55
                                       而非 (1.45 × 51.75) - 51.75 = 23.3
```

LLM 的 mental model 假设 in-window pre 起点和 baseline 一样高（都是 51.75），所以
1.45× 就能跳到 75。但实际 in-window pre 起点已经被 LLM 自己的 month effects 拉
低到 55.6，1.45× 之后只到 80.6（理论）/ 59.3（实测，可能还有 target filter
+ noise + lognormal 多重影响）。

**核心 mismatch**：LLM 算公式时用「年度均值」当 in-window baseline；validator 测量
时用「out-of-window 均值」当 baseline。两个 baseline 不是同一个数。

---

## 4. Constraint 17 已经预警过，但 LLM 没听

Constraint 17 [§month/quarter effects](../../../pipeline/phase_2/orchestration/prompt.py#L141-L145) 写了：

> "If the measure has month/quarter effects, baseline_std is inflated by between-period
> variation — bump |M| another 20–30%, or narrow the `anomaly_window` to a single peak
> season."

按这条建议：

- 6dbb 真正应选 `M = 0.45 × 1.25 = 0.56`（bump 25%）→ window_mean ≈ 1.56 × 55.6 = 86.7
  → shift ≈ 35 → realized z ≈ 35 / 11.82 ≈ 3.0 ✓
- ac54 真正应选 `M = 0.55 × 1.25 = 0.69`→ 但 0.69 > 0.6 → **按 Constraint 17 应改用 trend_break**

**LLM 在 6dbb / ac54 没充分应用 month-effect bump**——它只用了基础公式 `|M| ≥ 1.5
× σ/μ` 选 magnitude，**没读 / 没照做** "bump 20–30%" 这条软建议。

这是 Constraint 17 文本里**软建议** vs 公式型**硬规则** 的 LLM compliance gap。

---

## 5. 候选修复方案（按优先级）

### 5.1 选项 A：prompt 端强化（推荐先试）

把 Constraint 17 里"bump 20–30%"从可选建议**升级为显式公式 + 强制条件**：

```
If your `param_model` declares month/quarter effects whose magnitude (in
log-space for lognormal/gamma, or absolute for gaussian) exceeds 0.05, the
in-window pre-injection mean differs from the year-round baseline_mean by
~exp(effect) − 1 ≈ ±5% or more. Use:

  |M| ≥ 2.5 × baseline_std / |baseline_mean|     (instead of 2.0)

If this pushes |M| > 0.6, switch to `trend_break` per the earlier rule.
```

理由：
- 复用 Constraint 17 现有公式语言（mirror §4.5 文本风格）
- 把"软建议"升级为"硬公式"——LLM 更不可能跳过
- `2.5 × CV` 比 `2.0 × CV` 多 25% buffer，覆盖典型 month-effect 强度

成本：~5-10 行 prompt 文本 + 5 个新单测（mirror D.2 test class）。

### 5.2 选项 B：validator detail 增强（互补于 A）

在 [`pattern_checks.py::check_seasonal_anomaly`](../../../pipeline/phase_2/validation/pattern_checks.py#L503-L517) 的 detail 里多打两个字段：

```python
# After computing window_mean / baseline_mean / z / declared_magnitude
expected_z_naive = declared_magnitude * baseline_mean / baseline_std    # LLM 心里算的
realized_z = z                                                            # validator 实测的
extra += f", expected_z_naive={expected_z_naive:.3f}, realized_z={realized_z:.3f}"
# 若 realized << expected, 说明有 in-window baseline 偏离
if expected_z_naive > 2 * realized_z:
    extra += " (warning: realized z << expected; likely month/quarter effects in measure)"
```

让 Loop B retry 时 LLM 看到具体差距 + 显式 hint。Phase D.2 已经做了同精神的事
（detail 里加 `required_magnitude_at_threshold`），D.3 这里是再加一对字段。

成本：~10 行 validator 代码 + 4 个新单测 in `test_validation_phase_d.py`（mirror Phase D 的 detail enrichment style）。

### 5.3 选项 C：SDK 端 dry-run helper（最重，最后选）

在 `engine/patterns.py::inject_seasonal_anomaly` 前加 `_estimate_z_given_magnitude(df,
target, anomaly_window, magnitude)` helper：实际抽 in-window 行计算 pre-injection
mean、和 out-of-window 比对、给出 `expected_realized_z` 估计；若与 LLM 用 naive
公式算的差 > 2× 则 raise 一个新 `PatternMagnitudeUnderestimatedError`（informational
hard error，包含具体数学）。

成本：~30 行 SDK 代码 + multiple tests + 改 retry_loop 处理新 error 类型。

### 5.4 推荐策略：A + B，跳过 C

- A 单独可能就够（mirror Phase D 主修路径）
- B 补充 retry 反馈，让 LLM 在 A 不够时也能自适应
- C 工程成本高、且 Phase D / D.2 的"教 LLM 自验"哲学反对 SDK 端硬挡。仅当 A+B 仍
  失败时考虑

---

## 6. 实施前的开放问题

新 session 拾起这个工作前需要先回答：

### 6.1 是 LLM 没读到，还是读到了但选择忽略？

把 6dbb / ac54 的实际 SDK script 文件看一下：

```bash
cat output/agpds/pingyue-samples-openai-catagory4-pathD2-llm/scripts/agpds_6dbb1c20db.py
cat output/agpds/pingyue-samples-openai-catagory4-pathD2-llm/scripts/agpds_ac54f076fc.py
```

如果 `param_model` 里 month effects 很小（< 0.05 in log space），那 LLM 选 `M = 0.45`
其实理论 expected_z 也只有 ~1.5，本来就贴线，realized 一抖就失败——这种情况下"bump
20–30%"是合理的 fix。

如果 month effects 很大（> 0.10 in log space），那 LLM 应该早就意识到要 bump，但
没——说明 LLM 在 month effect 量级判断上有缺陷，Phase D.3 需要更精细的指导。

### 6.2 选项 A 的 `2.5 × CV` 系数是否过 conservative？

`2.5 × CV` 比 `2.0 × CV` 多 25%。若实际 month effects 只让 in-window baseline 偏离
~5%，2.5× 已经够 cover；但若偏离 ~15%，可能还不够。

需要 hand-trace 几个 cat-4 / cat-3 上没 fail 的 seasonal_anomaly（cat-3 D.2 上 LLM
abandon 了 seasonal，没参考；可看 cat-4 baseline 的 a713 PASS scenario）。

### 6.3 Phase D.3 单独做 vs 合进 Phase D.x 总修？

- 单独 PR：低 blast radius，易 bisect，符合 D / D.2 的小步演进
- 合进 D.x：和 Phase D.4（其他 pattern types 的 row-count guardrail）一起写，省一轮
  LLM regen

建议单独 PR——MECHANISM_6 §6.3 树形结构允许 D.3 / D.4 各自独立。

---

## 7. 验证流程（拾起时复用）

跟 Phase D.2 验证流程几乎相同：

```bash
cd /home/dingcheng/projects/chartAgentVAGEN

# 1. 编辑 prompt.py 加 Constraint 17 §month-effect-bump 强化（选项 A）
# 2. 加 6 个测试到 test_prompt_constraint_17.py 的新 TestConstraint17MonthEffectBump
# 3. (可选) 编辑 pattern_checks.py 加 expected_z_naive / realized_z 字段（选项 B）
# 4. 加 4 个测试到 test_validation_phase_d.py 的新类

# Commit 1: prompt change
# Commit 2: prompt tests
# Commit 3 (可选): validator detail
# Commit 4 (可选): validator tests

# Stage 1 + 2 重跑 cat-4（D.3 主验证 batch）
PYTHONPATH=. ~/miniconda3/envs/chart/bin/python -m pipeline.agpds_generate \
  --batch-name pingyue-samples-openai-catagory4-pathD3-llm \
  --scenario-source cached_strict --seed 42 --category 4 --count 10 \
  --provider openai

PYTHONPATH=. ~/miniconda3/envs/chart/bin/python -m pipeline.agpds_execute \
  --input-dir  output/agpds/pingyue-samples-openai-catagory4-pathD3-llm \
  --output-dir output/agpds/pingyue-samples-openai-catagory4-pathD3-llm \
  --workers 4

# 验证
jq -r '.[] | "\(.generation_id): all_passed=\(.all_passed) failures=[\([.failures[]?.name] | join(", "))]"' \
  output/agpds/pingyue-samples-openai-catagory4-pathD3-llm/validation_summary.json | sort

# 主目标：cat-4 seasonal_* 2 → 0 (6dbb + ac54 都翻 PASS 或都切到 trend_break)
# 次要目标：passing 6/10 → 7-8/10（视 LLM regen variance）
```

---

## 8. 验收标准（Phase D.3 done 的定义）

- [ ] **cat-4 D.3 上 `seasonal_*` 失败数 ≤ 1**（理想 0；剩 1 条若能 hand-trace 出独立机制可接受）
- [ ] **cat-4 D.3 上 6dbb 或 ac54 的 LLM 行为变化**：
  - either magnitude bumped 20–30% 以上（如 6dbb 从 0.45 → 0.55+），passing
  - or 切到 `trend_break`（如 ac54 因 required > 0.6 触发切换）
- [ ] **cat-3 D.3 上仍 `seasonal_*` 0**（D / D.2 战果不丢）
- [ ] **0 个新 `PatternInjectionError`**（D.2 战果不丢）
- [ ] **新单测全过 + Phase A / B / D / D.2 既有测试全过**
- [ ] **MECHANISM_6 §6.3 把 Phase D.3 从 "candidate" 升级为 "done"**

---

## 9. 关联文件 / 入口

- [pipeline/phase_2/orchestration/prompt.py:131-176](../../../pipeline/phase_2/orchestration/prompt.py) — Constraint 17 全文（D.3 编辑目标）
- [pipeline/phase_2/validation/pattern_checks.py:404-526](../../../pipeline/phase_2/validation/pattern_checks.py) — `check_seasonal_anomaly`（选项 B 编辑目标）
- [pipeline/phase_2/tests/modular/test_prompt_constraint_17.py](../../../pipeline/phase_2/tests/modular/test_prompt_constraint_17.py) — 加新 test class（mirror D.2 模式）
- [pipeline/phase_2/tests/modular/test_validation_phase_d.py](../../../pipeline/phase_2/tests/modular/test_validation_phase_d.py) — 选项 B 测试加在这（mirror Phase D detail tests）
- [output/agpds/pingyue-samples-openai-catagory4-pathD2-llm/](../../../output/agpds/pingyue-samples-openai-catagory4-pathD2-llm/) — D.2 cat-4 batch（D.3 验证基线，有 6dbb + ac54 的实测数据）
- [MECHANISM_6 §6.3](MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md#63-phase-dx-树形结构d1--d2--d3--d4) — D.3 在 D.x 树形结构里的位置
- [MECHANISM_6 §6.4](MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md#64-cat-4-残留-2-条-seasonal-failure-的根因realized-z--expected-z) — 本子机制在主文档中的简要版（本文是它的纵深）

---

## 10. 时间线

| 日期 | 事件 |
|---|---|
| 2026-05-21 | Phase D + D.2 完成；cat-4 stress test 暴露 6dbb + ac54 的"realized z << expected z"模式 |
| 2026-05-21 | 本子机制 doc 起草，记录待新 session 拾起 |
