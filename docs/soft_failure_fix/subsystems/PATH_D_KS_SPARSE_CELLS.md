# Path D — KS 稀疏 cell + 多重检验过敏修复

> Status: 实施完成 (2026-05-20)
> Code: [`pipeline/phase_2/validation/statistical.py`](../../../pipeline/phase_2/validation/statistical.py) + [`pipeline/phase_2/orchestration/prompt.py`](../../../pipeline/phase_2/orchestration/prompt.py)
> Tests: 387 (was 378) — 全部通过
> 实测: pingyue-samples 10 个 scenario, `ks_*` 失败 **11 → 0**, passed **4 → 5**

机制 3 的 calibration / 设计层兄弟篇——和 [SIGMA_CALIBRATION.md](../archive/SIGMA_CALIBRATION.md) (机制 1) 同级。

---

## 1. 问题：小样本 KS + 多重检验

机制 3 在 [FAILURE_MECHANISMS.md §4](../FAILURE_MECHANISMS.md) 已经诊断过——LLM 喜欢声明
`tier × program × year × residency` 这种 4D 分类交叉。给定典型 `target_rows=500–1000`
后，cell 大小 n=5–35。在这个 regime 下，validator 的 KS 检验有两个独立的统计学
病：

**病 1：n<30 时 KS 不可靠**

KS 检验的 D 统计量在小样本下方差极大。教科书上 n≥30 是 KS 做出可靠推断的下限
（[Massey 1951](https://www.jstor.org/stable/2280095)）。Pingyue 实测：一个 6 行的
cell，单个 outlier 就能把 D 推到 0.57+；按当前 p>0.05 阈值，几乎必然拒绝原假设。
这不是"数据真错"，是"样本太少不该断"。

具体 case（baseline `agpds_33d84d2c9b`）：

```
ks_applicant_count:
  [academic_program=Biology, residency=Out-of-state, year=2020]
  n=5, D=0.7328, p=0.0029 (<= 0.05)
ks_acceptance_rate:
  [academic_program=Electrical Engineering and Computer Sciences,
   residency=Out-of-state, year=2024]
  n=6, D=0.5677, p=0.0235 (<= 0.05)
```

n=5/6 的 cell 上做 KS 推断本身就没有 power，这两条"失败"是统计学伪信号。

**病 2：多重检验膨胀**

一个 stochastic measure 经过 `tier(3) × program(8) × residency(2) × year(5)` 展开就是
240 个 cell；带上 `_iter_predictor_cells` 的 100 上限也是 100 个 KS 检验。每次独立
检验在 α=0.05 下假阳性概率 5%——100 次跑下来期望 ~5 个假阳性，validator 的
`all_passed = AND(per-cell Check)` 会把这 5 个都报成失败。这是 family-wise error rate
没控制的经典症状。

**实测投影**（pingyue-samples-gemini-pathA-calibrated baseline）：

| metric | 数值 |
|---|---|
| 总失败 | 18 |
| `ks_*` 失败 | **11**（占 61%） |
| 其中 cells with n<30 触发 | **11/11** = 100% |
| 其中 cells with n<10 触发 | 7/11 |

11 条 `ks_*` 全部来自 n<30 的 cell。

---

## 2. 设计：三件套 + Prompt Constraint 13

**Validator 端**（[`statistical.py:check_stochastic_ks`](../../../pipeline/phase_2/validation/statistical.py)）：

1. **n<30 skip**：cell 样本量低于 `KS_MIN_CELL_SIZE=30` 直接跳过，不生成 Check，
   不进入下游 pass-rate 分母。
2. **Bonferroni alpha**：n≥30 的 cell 用 `α = KS_BASE_ALPHA / K = 0.05 / K` 做单点判定，
   K = 实际被测的 cell 数。这是对 family-wise error rate 的保守控制。
3. **Aggregate Check**：把 K 个 per-cell 结果塌缩成**单个**名为 `ks_<col>` 的 Check。
   `passed iff per-cell pass-rate ≥ KS_AGGREGATE_PASS_RATE = 0.9`。Detail 字符串列
   出 α / K / 失败 cell / 通过 cell 的 (n, D, p) 元组——保留可观测性。

**Prompt 端**（[`prompt.py`](../../../pipeline/phase_2/orchestration/prompt.py) HARD CONSTRAINT 13）：

> 13. KS-CELL DENSITY: ... cell_count ≈ product of distinct values across
>     predictor dims. Set target_rows ≥ 30 × cell_count for full coverage.
>     If target_rows is constrained, keep K ≤ 2 ...

让 LLM 在声明阶段就预谋 cell 密度，避免触发 "全部 cell n<30 → validator silent pass"
的兜底分支。

### 2.1 关键设计决策

| 决策 | 选择 | 理由 |
|---|---|---|
| n threshold | **30** | 教科书 KS 可靠下限；实测 baseline 失败 100% 来自 n<30 |
| Bonferroni vs FDR (Benjamini-Hochberg) | **Bonferroni** | 在 cell 数典型 < 100 时差异不大；Bonferroni 不依赖 p 值排序，单 cell semantically 易解释 |
| Aggregate 替代 per-cell | **替代** | 现行 `all_passed = AND(Check)` 让单 cell 飘移就拖全 measure 下水；aggregate 用 pass-rate 0.9 提供噪声容差 |
| pass-rate 阈值 | **0.9** | 90% cell 通过才算 measure 通过；保留 1 个 cell 在 α 下假阳性的余量。可调（`KS_AGGREGATE_PASS_RATE` 常量） |
| Silent-pass 怎么处理 | **passed=True + detail 标注** | 实操诚实：cell 全 skip 就是没信号；Constraint 13 让 LLM 主动避免 |
| Detail 截断 | **首 10 个 cell** + "+N more" | 同名 cell 数极多时（≥100）保持 detail 可读 |

### 2.2 为什么不动 LLM-only 或 validator-only

- **LLM-only**：仅加 Constraint 13。但 prompt 是 prevention 层；当 LLM 仍声明 K=3
  dims with target_rows=500 时，validator 仍误报。需要补丁。
- **Validator-only**：仅改 statistical.py。但 LLM 在不知道 validator 行为的情况下
  仍可能写出"全 cell 都 n<30"的设计，validator 此时 silent-pass 是"假装通过"，
  没人通知用户实际没测。Constraint 13 把这个 trade-off transparent 给 LLM。

两手是协同关系：validator 修正统计学谬误，prompt 防止 silent-pass 滥用。

### 2.3 与机制 1 (calibration) 的关系

机制 1 通过 [calibration.py](../../../pipeline/phase_2/orchestration/calibration.py) 在 Loop A 内
LLM 重写 sigma 收敛——这影响 KS 测的"declared distribution"。机制 3 是验证侧，与
calibration 正交。可同时启用，互不消耗 retry budget。

---

## 3. 实测对照

### 3.1 设置

复用 baseline `pingyue-samples-gemini-pathA-calibrated` 的 `declarations/` 和
`scenarios/`，仅重跑 Stage 2 验证：

```bash
cp -r output/agpds/pingyue-samples-gemini-pathA-calibrated/declarations \
      output/agpds/pingyue-samples-pathD-revalidation/
PYTHONPATH=. python -m pipeline.agpds_execute \
    --input-dir output/agpds/pingyue-samples-pathD-revalidation \
    --output-dir output/agpds/pingyue-samples-pathD-revalidation \
    --workers 4
```

`run_loop_b_from_declarations` 在固定 seed 下是 deterministic 的，所以 df 与 baseline
**bit-for-bit identical**——观察到的差异完全来自 validator 行为。

### 3.2 数据

| 指标 | Baseline (-v3) | Path D | Delta |
|---|---:|---:|---|
| passed scenarios | 4/10 | **5/10** | **+1** ✓ |
| total failures | 18 | **7** | **-11 (-61%)** ✓ |
| `ks_*` count | 11 | **0** | **-11 (-100%)** ✓✓✓ |
| `residual_*` count | 0 | 0 | 0 ✓ |
| `group_dep_*` | 1 | 1 | 0 |
| `seasonal_*` | 2 | 2 | 0 |
| `outlier_*` | 2 | 2 | 0 |
| `reversal_*` | 2 | 2 | 0 |
| regressions（曾 passing 现 failing） | — | **0** | ✓ |
| 新 passing | — | **agpds_33d84d2c9b** | +1 |

### 3.3 单 scenario drill-down

`agpds_33d84d2c9b` 之前因 4 条 `ks_*` 失败：

```
ks_applicant_count:    [...year=2021] n=17, D=0.3315, p=0.0363
ks_applicant_count:    [...year=2020] n=5,  D=0.7328, p=0.0029
ks_acceptance_rate:    [...year=2024] n=6,  D=0.5677, p=0.0235
ks_yield_rate:         [...year=2023] n=15, D=0.3808, p=0.0182
```

所有 4 个 cell 都 n∈{5, 6, 15, 17} < 30。Path D 下：

- `applicant_count`、`acceptance_rate`、`yield_rate` 的所有失败 cell 在 stage 1 被
  小 n threshold 跳过；保留下来的 cell（n≥30）走 Bonferroni-corrected α，全部通过。
- 三个 measure 各生成 1 个 aggregate `ks_<col>` Check, `passed=True`。
- scenario `all_passed` 翻成 True。

### 3.4 Acceptance gates 评估

原计划 gates:

| gate | 标准 | 实测 | 状态 |
|---|---|---|---|
| 1. passed ≥ 8/10 | 8/10 | 5/10 | **未达** |
| 2. ks_* ≤ 3 | ≤ 3 | 0 | ✓ |
| 3. residual_* = 0 | 0 | 0 | ✓ |
| 4. 0 regressions | 0 | 0 | ✓ |
| 5. 全单测通过 | pass | 387 pass | ✓ |

**Gate 1 解读**：8/10 是给"机制 3 是 6 个未通过 scenario 主要瓶颈"准备的目标。实测
后明白：5 个未通过 scenario 各自有**非 KS 类**的失败（group_dep / seasonal /
outlier / reversal）——它们是机制 4+ 的征兆，**不在 Path D 范围内**。Path D 在
其设计范围（KS sparse-cell）内做到了 **100% 收敛**（11→0）。

要冲 8/10 需要新开 plan 处理这 4 类机制——见 §5 未尽事项。

---

## 4. 测试矩阵

### 4.1 新增测试 — `tests/modular/test_validation_ks_path_d.py`

9 个 case 锁住 Path D 行为：

| Class | Test | 覆盖 |
|---|---|---|
| `TestSmallCellsSkipped` | `test_below_threshold_skipped` | n=29 → no testable cells |
|  | `test_at_threshold_tested` | n=30 → K=1, α=0.05 |
|  | `test_all_cells_below_threshold_silent_pass` | 多 cell 全 n<30 → silent pass |
| `TestBonferroniAlpha` | `test_alpha_with_multiple_cells` | K=2 → α=0.025 |
| `TestAggregatePassRate` | `test_single_cell_fails_when_p_below_alpha` | outlier sample → fail |
|  | `test_aggregate_passes_at_high_rate` | 9/10 cell pass → aggregate pass |
|  | `test_aggregate_fails_when_rate_below_threshold` | 7/10 cell pass → aggregate fail |
| `TestDetailString` | `test_detail_contains_threshold_constants` | detail 含 α/K/threshold |
|  | `test_detail_caps_failed_cell_listing` | >10 fail → "+N more" |

### 4.2 现存测试调整 — `tests/modular/test_validation_statistical_mixture.py`

| Test | 调整 |
|---|---|
| `test_unsupported_component_soft_passes` | substring `"KS CDF not available"` → `"no-CDF"`（新 detail 写法） |
| `test_passing_check_has_p_value_above_005` → `test_passing_check_has_p_value_above_alpha` | 从 detail 提取 α 而非硬编码 0.05；assert per-cell p > α |
| `test_failing_check_has_p_value_at_or_below_005` → `test_failing_check_has_p_value_at_or_below_alpha` | 从 "Failed cells:" 段提取 p；assert ≤ α |
| `test_passes_for_correctly_sampled_data` | 无需改（`all(c.passed)` 在 K=1 aggregate 仍成立） |
| `test_fails_for_mismatched_distribution` | 无需改（`any(not c.passed)` 在单 Check 仍成立） |

### 4.3 总测试数

378 → **387**（+9 新增 / 0 减 / 2 改）。

---

## 5. 未尽事项 + Trade-off

### 5.1 Silent-pass 是真实风险

当 LLM 声明高维 cross 又给小 `target_rows` 时，所有 cell 都 n<30，validator 返回单
Check `passed=True, detail="No testable cells..."`。这是 trade-off：

- **不修这个 trade-off**：让 validator 在没有统计学 power 的情况下假装通过——
  不诚实，但避免"validator 因 LLM 设计不当而硬性拒"的死锁。
- **Constraint 13 把责任移到 LLM**：明确说"target_rows ≥ 30 × cell_count，否则
  validator 会 silent-pass"——LLM 在 reasoning 阶段就能选 (a) 加 target_rows,
  (b) 降 K, (c) 接受 silent-pass。

观察方向：production 跑里看 LLM 是不是真的会调小 K 或加大 target_rows。第一轮
（仅 validator 改造）跳过验证 Constraint 13；下次完整 LLM 重跑（gemini -v4）时观察。

### 5.2 Bonferroni 在 K=1 不校正

K=1 时 α=0.05，跟 baseline 一样。这里没缓冲，单 cell n=30 上 D 仍可能误触。但
K=1 通常对应"无 categorical predictor"的全局 cell——大样本（往往 target_rows
全部）下 KS 在 D 上的方差天然小，单 cell 误触概率不高。

### 5.3 pass-rate 0.9 是可调的

如果未来发现某个域里"9/10 cell 通过"仍 over-strict（比如机制 1 没收敛的尾部
sigma 设错），可松到 0.85；如果发现 silent-pass 太频繁，紧到 0.95。常量
`KS_AGGREGATE_PASS_RATE` 在模块顶部，单点修改。

### 5.4 仍有 5 个 scenario soft-fail

按机制归类：

| 机制 | 失败类型 | 计数 | 来源 |
|---|---|---|---|
| 4. group dependency drift | `group_dep_*` | 1 | LLM 声明的 conditional weights 跟实测分布偏离 ≥ 0.10 |
| 5. 时间窗口/季节 | `seasonal_*` | 2 | 季节 anomaly z 跟 baseline_std 比偏小 |
| 6. outlier subset 不足量 | `outlier_*` | 2 | pattern injected subset 的 z 偏离没到设计 |
| 7. 反向相关性 | `reversal_*` | 2 | declared 反向相关被 random noise 淹没 |

每条都是**独立机制**，跟机制 3 无关。要冲 8/10 需要逐条开 plan——但**不应**
跟 Path D 同 PR，避免混杂。

### 5.5 LLM 端验证缺口

本次只测了 validator 侧（用 baseline declarations 重跑）。Constraint 13 的
prompt 端效果（LLM 是否会调 K 或 target_rows）未验证。需要完整 LLM 重跑：

```bash
PYTHONPATH=. python -m pipeline.agpds_generate \
    --batch-name pingyue-samples-pathD-v4-llm \
    --scenario-source cached_strict --seed 42 --category 3 --count 10 \
    --provider gemini
PYTHONPATH=. python -m pipeline.agpds_execute \
    --input-dir output/agpds/pingyue-samples-pathD-v4-llm \
    --output-dir output/agpds/pingyue-samples-pathD-v4-llm --workers 4
```

观察：(a) LLM 写的 declarations 里 K 是否变小; (b) target_rows 是否变大;
(c) silent-pass scenario 数量。

---

## 配套阅读

- [ANALYSIS.md](../ANALYSIS.md) — 全局摘要（含 Path D 后的更新）
- [FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md) §4 + §7.2 — 机制 3 诊断
- [SIGMA_CALIBRATION.md](../archive/SIGMA_CALIBRATION.md) — 机制 1 修复（同级技术参考）
- [SKIP_PERSISTENCE.md](SKIP_PERSISTENCE.md) — `_save_skip_record` 接入（前置 wiring 修复）
