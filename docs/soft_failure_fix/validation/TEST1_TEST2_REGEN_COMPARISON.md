# test-1 vs test-2：同场景两次 LLM 重生成的 validation 对比

> 批次实测记录。数据源：
> - [`output/agpds/test-1/validation_summary.json`](../../../output/agpds/test-1/validation_summary.json)
> - [`output/agpds/test-2/validation_summary.json`](../../../output/agpds/test-2/validation_summary.json)
>
> 配套阅读：[FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md)（M1/M2/M3 + Path A/B/C）、
> [mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md](../mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md)（seasonal）、
> [mechanisms/M6_PHASE_D3_REALIZED_Z_GAP.md](../mechanisms/M6_PHASE_D3_REALIZED_Z_GAP.md)（realized z << expected z）、
> [BACKLOG.md](../BACKLOG.md)（deferred queue）。

---

## 0. 一页总结

- **`generation_id` 锚定的是「场景规格」，不是「声明内容」**。`--scenario-source cached_strict`
  让两批跑同 10 个场景 id，但每批 LLM **重新生成** declarations。`diff` 证实：相同 id
  `agpds_503613ba96` 在两批的列名 / group / weights / pattern 全不同（§1）。
- 所以 **test-1 / test-2 是 LLM 对同一批场景的两次独立重生成**，不是同一份声明跑两遍。
  两份 `validation_summary` 必须**对比着读**：哪些失败两次都炸 = 鲁棒机制；哪些只出现一次 =
  LLM regen variance（呼应 [MECHANISM_6 §5.9](../mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md)）。
- **持续失败只有 seasonal 家族**（`14b7f7487e` / `e9c40d0352` 两次都炸）。其余 reversal /
  outlier / ks / convergence 都是单次抽样命中。
- 全部 15 条失败都落在已记录的 M-taxonomy（§3）。**唯一可能被现有文档拎得不够清的点**：
  注入器尊重 pattern `target`，但 `check_seasonal_anomaly` / `check_ranking_reversal` **忽略
  `target`** → 对全窗口 / 全表度量。两条 hand-trace（§5）证明注入完全正确、validator 却因
  测错人群而判 fail——这是 seasonal rate 度量稀释和 `reversal=1.0000` 的直接机械原因。

---

## 1. 关键证据：相同 `generation_id`，不同 declarations

```
$ diff output/agpds/test-1/declarations/agpds_503613ba96.json \
       output/agpds/test-2/declarations/agpds_503613ba96.json
```

实质性差异（节选）：

| 维度 | test-1 | test-2 |
|---|---|---|
| 顶层 group 名 | `organization` | `entity` |
| `college_division` 列 | 存在（parent=`department`，5 值层级）| 不存在（结构重排）|
| 年份 weights | `0.16, 0.15, 0.14, 0.13, 0.12, 0.18, 0.12` | `0.15, 0.15, 0.15, 0.15, 0.10, 0.20, 0.10` |

→ declarations 不同 ⇒ master_table 必然不同 ⇒ 验证结果必然漂移。`generation_id` 是**场景哈希**
（domain / 任务规格），不是声明哈希。

> 含义：跨这两批做"同一份声明跑两遍是否确定性一致"的判断**不成立**。它们是两次 LLM 采样。
> 真正字节一致的可复现性，要在**同 declarations + 同 seed + 同代码**下比（见 MECHANISM_6 §6.7）。

---

## 2. 持续失败 vs regen-variance 对照

| `generation_id` | test-1 | test-2 | 性质 |
|---|---|---|---|
| `14b7f7487e` | `seasonal_hold_fulfillment_rate` ✗ | `seasonal_hold_fulfillment_rate` ✗ + `reversal_*` ✗ | **持续**（seasonal 鲁棒）|
| `e9c40d0352` | `seasonal_attendance_rate` ✗ | `ks_*` ✗ + `seasonal_absentee_count` ✗ + `reversal_*` ✗ | **持续**（seasonal 家族稳定复发；具体 measure 因 regen 而变）|
| `33d84d2c9b` | `residual_enrolled_count` ✗ | ✓ PASS | regen 变异 |
| `503613ba96` | ✓ PASS | `outlier_*` + `reversal_*` + `seasonal_*` + `convergence_*` ✗ | regen 变异 |
| `985a1b72e1` | ✓ PASS | `reversal_salary_job_offers` ✗ | regen 变异 |
| `d62b18e180` | ✓ PASS | `reversal_*` + `convergence_*` ✗ | regen 变异 |
| `3af92040e6` / `65ef0afda0` / `8022981cf7` / `8180fe4e2c` | ✓ | ✓ | 稳定通过 |

- test-1：3 个 scenario fail，共 **3** 条失败。
- test-2：5 个 scenario fail，共 **10** 条失败。
- 跨两批失败族计数：`seasonal` ×5、`reversal` ×5、`convergence` ×2、`ks` ×1、`outlier` ×1、`residual` ×1。

**读法**：`14b7f7487e` / `e9c40d0352` 是真·鲁棒机制（两次都因 seasonal 炸），最该优先收口；
其余是单次 LLM 采样恰好踩到的雷。`503613ba96` 一次全过、一次炸 4 条，是 regen variance
幅度的极端例子。

---

## 3. 失败 → 机制 全映射

| 失败 check（批次）| detail 关键数据 | 机制 | 文档 |
|---|---|---|---|
| `seasonal_hold_fulfillment_rate`(t1,t2)、`seasonal_attendance_rate`(t1) | \|M\|=0.04/0.08 **>** required 0.037/0.029/0.039，z 仍 0.28/1.18/0.75 | **M6 子机制 realized-z<<expected-z** + §5 target 稀释 | [M6_PHASE_D3_REALIZED_Z_GAP.md](../mechanisms/M6_PHASE_D3_REALIZED_Z_GAP.md) |
| `seasonal_undergraduate_enrollment`(t2)、`seasonal_absentee_count`(t2) | M=0.6 **<** required **1.415 / 1.063**（CV≈1）| **M6 主机制**（高 CV 淹没）| [MECHANISM_6 §2](../mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md) |
| `reversal_*` ×5（salary_job_offers / checkout_renewal / course_load_sfr / intervention / attendance_enrollment）| rank_corr = 1.0000 / 0.2571 / 0.2500 | **Phase C**（结构正相关 metric 对）+ §5 target scope mismatch | [FAILURE_MECHANISMS §5](../FAILURE_MECHANISMS.md)、[MECHANISM_6 §5.4](../mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md) |
| `outlier_student_faculty_ratio`(t2) | z=0.856 < 2.0（subset 12.36 vs ref 19.65, ref_std 8.51）| **M9**（声明 z_score ≠ realized；注入用 global_std，validator 用补集 ref_std）| [MECHANISM_6 §6.5](../mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md) |
| `ks_enrollment_count`(t2) | 2/5 cells pass，失败 cell D=0.25–0.33（n=72–133）| **M3 + M8**（漏斗乘积 → cell-level param_model mis-fit）| [MECHANISM_3](../mechanisms/MECHANISM_3_DEEP_DIVE.md)、[MECHANISM_6 §6.5](../mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md) |
| `convergence_course_load`(t2) | reduction=0.144 < 0.4 | convergence 信号弱（pull 不足 / 噪声主导）| — 未单独立机制 |
| `convergence_gpa_change`(t2) | reduction=**−1.071** < 0.35（方差**反增**；var 量级 0.001–0.004）| convergence 被生成噪声主导 | — |
| `residual_enrolled_count`(t1) | "All rows excluded by pattern masks; no residuals to check." | **P3-8 过度排除**（observability artifact，非数据质量）| [statistical.py:502-522](../../../pipeline/phase_2/validation/statistical.py#L502-L522) |

---

## 4. 按家族根因（精简）

- **seasonal_\***（注入 [patterns.py:681](../../../pipeline/phase_2/engine/patterns.py#L681) 乘性
  `df.loc[in_win] *= (1+M)`；validator [pattern_checks.py:469-501](../../../pipeline/phase_2/validation/pattern_checks.py#L469-L501) 测 `z=|w−b|/σ_b`）：
  - **主型**（undergraduate_enrollment / absentee_count）：count/enrollment 度量 CV≈1，required≥1.06/1.42，
    即便完美注入也到不了 z=1.5——声明振幅没对齐 baseline 噪声。
  - **realized-z-gap 型**（hold_fulfillment_rate / attendance_rate）：\|M\| 已超 required，z 却仍不达标。
    §5 证明这一型的实际主因是 **validator 忽略 target 导致的稀释**。
- **reversal_\***（注入 [patterns.py:481-509](../../../pipeline/phase_2/engine/patterns.py#L481-L509)
  只在 target 子集做加性移位；validator [pattern_checks.py:573](../../../pipeline/phase_2/validation/pattern_checks.py#L573)
  `df.groupby(entity_col).mean()` 全表）：根因 1 = LLM 在**结构正相关**的 metric 对上声明 reversal
  （salary = `60000 + major_base + job_offers*4000 − …`，跨 entity 天然 rank_corr=+1）；
  根因 2 = §5 的 target scope mismatch。
- **outlier_\***：注入按 `global_mean + z·global_std` 定子集均值，validator 用**补集** ref_std/ref_mean
  测 z 且阈值 2.0——口径不一致 + ref_std 大（占 mean 43%）。
- **ks_\***：enrollment_count 是漏斗乘积度量，大 n cell 的 realized 分布偏离声明 CDF（M1 投影 + M8）。
- **convergence_\***：信号被生成噪声主导；gpa_change 的方差量级仅 0.001–0.004，pull 压不住噪声 → reduction 反负。
- **residual_\***：T9/P3-8 为避免 pattern 行污染 residual 而排除"pattern 命中列或其公式依赖"的行；
  这里把**全部行**排掉 → 退化成"失败"。是 observability 缺口，t2 重生成后该场景即 PASS。

---

## 5. 开放问题（待裁定）：pattern `target` scope mismatch

注入器只动 pattern 的 `target` 子集，但以下两个 validator **完全不带 `target` 过滤**，对更大的人群度量：

- `check_seasonal_anomaly`：`in_win = (tval>=start)&(tval<=end)`（[pattern_checks.py:469](../../../pipeline/phase_2/validation/pattern_checks.py#L469)）——窗口内**所有行**，不分 target。
- `check_ranking_reversal`：`df.groupby(entity_col)[[m1,m2]].mean()`（[pattern_checks.py:573](../../../pipeline/phase_2/validation/pattern_checks.py#L573)）——**全表**，不分 target。

### 5.1 Hand-trace A — seasonal（`agpds_14b7f7487e`, test-2）

声明：`seasonal_anomaly, target="branch == 'Central Library'", col="hold_fulfillment_rate",
anomaly_window=["2023-11-01","2023-12-31"], magnitude=-0.08`。
master_table：6 个分支、240 行，Central Library 64 行（26.7%）。

| 视角 | window_mean | baseline_mean | baseline_std | z | 判定 |
|---|---:|---:|---:|---:|:-:|
| **validator（全 6 分支）** | 91.43 | 93.25 | 2.41 | **0.752** | ✗ FAIL |
| 反事实（仅 target=Central Library）| 84.53 | 92.02 | 2.78 | **2.69** | ✓ 本应 PASS |

注入**完全正确**：Central Library 窗口内均值从 92.02 → **84.53**（−8.1% = 声明 −0.08）。但
Nov-Dec 2023 窗口共 31 行，其中只有 **7 行是 Central Library**（22.6%），另 24 行是**未被注入**的
其他分支（窗口内均值 93.44 ≈ baseline）。validator 把 −8% 的下沉摊到 31 行里 → window_mean 仅
91.43，z=0.752 不达标。**若 validator 限定到 target，z=2.69 直接通过。**

> 注意：[MECHANISM_6 §3.1](../mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md) 分析的 14b7 是
> **另一次重生成**（checkout_count / target=Children / M=0.35 / CV=0.86），归因于高 CV。本批是
> 同场景的不同声明（hold_fulfillment_rate / Central Library / M=−0.08），target-restricted z=2.69
> 说明**这一份**声明的 binding constraint 是 target 稀释而非 CV。两者并存，但本例稀释占主导。

### 5.2 Hand-trace B — reversal（`agpds_985a1b72e1`, test-2）

声明：`ranking_reversal, target="year == 2023", metrics=["salary","job_offers"], entity_col="major"`。
master_table：1800 行、6 个 major；`salary` 是 `job_offers` 的**结构正函数**。

| 视角 | rank_corr | 判定 |
|---|---:|:-:|
| **validator（全 1800 行）** | **+1.0000** | ✗ FAIL |
| 注入 scope（year==2023，204 行 = 11.3%）| **−1.0000** | ✓ 完美反转 |

注入在它的 target（year==2023）内把 rank_corr 精确做到 **−1.0000**——正是声明意图。但 validator
对全表度量，88.7% 未被反转的行（且 salary 跨 major 天然单调正相关：CS 121.6k / Psychology 48.3k）
压倒性主导 → 全局 rank_corr=+1.0000 = "完全没反转"。

### 5.3 结论性提问

两条 hand-trace 都指向同一事实：**注入完全按声明执行，validator 因度量了 target 以外的人群而判 fail。**
这是 validator 应当按 `target` 过滤的 **bug**，还是"约定 LLM 必须把 pattern 施加于全体人群（不要用
窄 target）"？

- 若判为 **bug**：`check_seasonal_anomaly` / `check_ranking_reversal` 应在度量前对 `pattern["target"]`
  过滤（reversal 还需在 target 内比较 m1/m2 的 entity-mean 排序）。建议作为候选机制
  **"M10: pattern target scope mismatch"** 进 [BACKLOG.md](../BACKLOG.md)，关联 M6 与 Phase C——
  它能一并解释 M6 的部分 realized-z-gap 与 Phase C 的部分 `reversal=1.0000`。
- 若判为 **约定**：应在 prompt（Constraint 17 / Phase C 约束）显式要求 seasonal / reversal pattern
  使用全体 target，并在 SDK 注入处校验 target 覆盖度，否则注入与验证的契约（DS-2 "pairs with"）名不副实。

**本文不改代码，仅记录证据 + 提问，待裁定。**

---

## 6. 结论

- **没有一条失败是生成引擎 bug**。全部是"LLM 声明 ↔ validator 几何"错位，与项目主论点一致。
- **持续失败仅 seasonal 家族**（14b7 / e9c4 两次都炸）→ M6 / D.3 + §5 target 稀释最该优先收口。
- 其余 reversal / outlier / ks / convergence 是单次 regen 命中，分属 Phase C / M9 / M3+M8 /
  convergence，多数已在 [BACKLOG.md](../BACKLOG.md) 排队。
- `residual_enrolled_count`(t1) 是 P3-8 过度排除的 observability artifact，非数据质量问题（t2 已 PASS）。
- §5 的 target scope mismatch 是本次对比新拎出的横切点，证据强（注入正确、target-restricted 反事实通过），
  待裁定 bug / 约定。

---

## 7. 时间线

| 日期 | 事件 |
|---|---|
| 2026-05-31 | test-1 / test-2 两批 batch 产出（同 10 场景两次 LLM 重生成）|
| 2026-05-31 | 对比分析：确认 generation_id=场景锚点；持续失败仅 seasonal；hand-trace 锁定 target scope mismatch（§5）；本文定稿 |

---

## 8. 配套阅读

- [FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md) — M1/M2/M3 + Path A/B/C 全景
- [mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md](../mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md) — seasonal 振幅 vs baseline 噪声
- [mechanisms/M6_PHASE_D3_REALIZED_Z_GAP.md](../mechanisms/M6_PHASE_D3_REALIZED_Z_GAP.md) — realized z << expected z（与 §5 互补）
- [BACKLOG.md](../BACKLOG.md) — deferred queue（候选 M10 入口）
- [validation/PINGYUE_OPENAI_CAL_ANALYSIS.md](PINGYUE_OPENAI_CAL_ANALYSIS.md) — per-scenario 诊断范例
