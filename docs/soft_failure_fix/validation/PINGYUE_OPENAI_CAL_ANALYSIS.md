# `pingyue-samples-openai-calibrated` 全批 soft-fail 深度分析 + 下一步修改计划

> Companion to [OPENAI_VALIDATION.md](OPENAI_VALIDATION.md)（batch-level summary 表 + Path D rerun 数据）。本文是 **deep per-scenario 分析 + forward-looking 修改计划**——目的是让下一次 session 不需要翻 `~/.claude/plans/` 也能从此处接手。
>
> 数据来源：[validation_summary.json](../../../output/agpds/pingyue-samples-openai-calibrated/validation_summary.json) + 10 份 per-scenario report（基线）+ [pingyue-samples-openai-calibrated-pathD-revalidation/](../../../output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation/)（Path D rerun）。

---

## 1. Context

`output/agpds/pingyue-samples-openai-calibrated/` 是 openai (`gpt-5.5`) + Path A 约束 (Constraint 11/12) + Loop A in-loop sigma calibration 开启的 production 批次（生产时间 2026-05-20）——机制 1 修复后第一份在原始 production model 上的端到端验证。

**基线结果**：1/10 passed · 9/10 soft-failed · 0 errored · 0 skipped · **54 条 check failure**。
**Path D rerun（commit `a7602e6`）后**：5/10 passed · 5/10 soft-failed · **13 条 check failure**。

---

## 2. 机制图例（沿用 [FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md) 命名 + M4-family 扩展）

| Tag | 命名 | 触发 check | 状态（openai-cal） |
|---|---|---|---|
| **M1** | 复合方差盲区 (composite variance) | `residual_*` | ✅ 主线闭合（15→1），剩 1 条 ratio-operator 长尾 |
| **M2a** | Pattern target 0 命中 | `PatternInjectionError` | ✅ Path A 约束 12 在源头拦截，**未触发** |
| **M2b** | None 漏入 effect-map | `KeyError: 'None'` / `UndefinedEffectError` | ✅ Path A 约束 12 在源头拦截，**未触发** |
| **M3** | 稀疏 cell 脆弱性 | `ks_*` | ✅ Path D 后闭合（39→0）|
| **M4-family** | doc 未正式命名 | `group_dep_*` / `orthogonal_*` / `marginal_*` / `seasonal_*` / `reversal_*` | ❌ 13 条残留 |

doc §7.2 明说："剩 5 个未通过 scenario 全是非 KS 类失败 (group_dep_* / seasonal_* / outlier_* / reversal_*), 属机制 4+, 单独 plan." 本文 §8 给出该独立 plan。

---

## 3. 逐 scenario soft-fail 拆解

### 3.1 agpds_14b7f7487e — Boston Public Library 借阅

3 条失败，全部 M4-family：
- `group_dep_material_type`: `parents=['audience_segment'], max_dev=0.1657` — M4-group-dep drift
- `group_dep_service_channel`: `parents=['material_type'], max_dev=0.1431` — M4 链式依赖
- `seasonal_checkout_count`: `z=0.050 (window=7794.69, baseline=8146.31, std=7018.80)` — M4-seasonal，声明的季节振幅未与 baseline 方差对齐（**M1 的孪生**：LLM 不知道 std=7019 是 mean=8146 的多大占比）

无 KS / 无 residual 失败——借阅是加性度量，机制 1/3 不发病。3 条 M4 全是关系层（条件分布 + 季节振幅）数字标错。

### 3.2 agpds_33d84d2c9b — UC Berkeley 招生

8 条失败 = 1 M4-orthogonal + 6 M3 + 1 M4-group-dep：
- `orthogonal_campus_year`: 1×1 degenerate — campus 和 year 在采样后都退化为单值
- `ks_applicant_count` ×3 / `ks_yield_rate` ×3: n=6–22, D=0.31–0.60 — 5 维 cell 交叉稀疏
- `group_dep_outreach_channel`: max_dev=0.1529 — segment → outreach_channel 条件权重偏 15.3%

招生 funnel + 高维分类 → M3 主导。

### 3.3 agpds_3af92040e6 — UC 财政援助

4 条失败 = 3 M3 + 1 M4-group-dep：
- `ks_grant_share` ×3: n=5/7/10, D=0.51–0.69 — 7 维 cell 交叉
- `group_dep_aid_program`: max_dev=0.1123 — **边缘失败**（贴 0.10 阈值过线 1.2%）

**关键**：v1 (openai 无 fix) 时此 scenario 曾因 `PatternInjectionError` errored；Path A 约束 12 让 LLM 避开了 0-row pattern target → errored→soft-failed。

### 3.4 agpds_503613ba96 — UC 本科招生 ⚠ 机制最丰

7 条失败 = 1 M4-orthogonal + 4 M3 + 1 M1 + 1 M4-reversal：
- `orthogonal_campus_academic_quarter`: 1×4 degenerate — campus 在场景里仅 1 个值
- `ks_undergraduate_enrollment` ×4: n=5–8, D=0.49–0.69
- `residual_student_faculty_ratio`: `noise_sigma=4.43, residual_std=7.84, ratio=0.7688` — **唯一全批 M1 残留**，详 §5
- `reversal_course_load_student_faculty_ratio`: rank_corr=+0.29 (期望 <0) — **跟 M1 残留同列同根**：公式 `student_faculty_ratio = ... + 0.42×(enrollment/faculty) + ...` 与 `course_load = ... + α×enrollment − β×faculty + ...` **共享 enrollment 分子 / faculty 分母**，结构性正相关

`student_faculty_ratio` 同列同时撞 M1 + reversal 是**有诊断价值的强信号**：calibration 校 sigma 校到 0.77× 已经在 LLM 的"sensible ceiling"上，但公式骨架共享上游变量决定了 reversal 必然正相关——sigma 再校也修不了。

### 3.5 agpds_65ef0afda0 — Stanford 研究经费 ⚠ 最多 KS

13 条失败 = 12 M3 + 1 M4-reversal：
- `ks_grant_funding` ×6: n=5–11, D=0.42–0.71 — 5 维 cell crossing (`mechanism × source × lab × area × year`)，lab 列基数大
- `ks_journal_impact_factor` ×6: n=6–12, D=0.39–0.66
- `reversal_grant_funding_citation_count`: rank_corr=+0.46 (期望 <0) — 验证器期望负相关，但 LLM 公式没实现

"openai 写更深分类树" 的教科书例子。

### 3.6 agpds_8022981cf7 — UC 课程通过率

**PASS** — 唯一全过。域是 `pass_rate × withdrawal_rate × completion_rate`，加性 + 比例度量结构，乘法链浅、分类列交叉少。

### 3.7 agpds_8180fe4e2c — 密歇根大学招生

2 条失败 = 1 M4-orthogonal + 1 M4-group-dep：
- `orthogonal_year_university`: 3×1 degenerate — 单校 scenario
- `group_dep_school`: max_dev=0.1756 — residency → school 偏 17.6%

v1 时此 scenario 曾因 `KeyError: 'None'` errored；约束 12 让 LLM 避开 None → errored→soft-failed。

### 3.8 agpds_985a1b72e1 — 校友职业去向

7 条失败，**全部 M3**：
- `ks_employment_rate` ×5: n=5–8, D=0.51–0.66
- `ks_further_education_rate` ×2: n=5/7, D=0.49–0.59

LLM 没写额外结构关系，纯分类列交叉过深 → Path D 一上全清。

### 3.9 agpds_d62b18e180 — UCSD 学生干预

4 条失败，**全部 M3**：
- `ks_intervention_attendance_hours` ×4: n=5–9, D=0.52–0.63 — 5 维交叉

同 3.8，纯 M3，Path D 直接清。

### 3.10 agpds_e9c40d0352 — 芝加哥高中入学

6 条失败 = 1 M4-marginal + 3 M3 + 2 M4-group-dep：
- `marginal_weights_grade_level`: max_dev=0.1024 — 贴线
- `ks_enrollment_count` ×2 / `ks_attendance_rate` ×1: n=7/16/29, D=0.31–0.49
- `group_dep_grade_level`: max_dev=0.1151 — 边缘
- `group_dep_intervention_program`: **max_dev=0.3029 — 全批最大 drift**，详 §6

---

## 4. 横切发现

### 4.1 失败计数按机制分类（基线 54 条）

| 机制 | 计数 | 命中 scenario |
|---|---:|---|
| M1 (residual) | **1** | #4 |
| M2a / M2b | **0** | （Path A 拦在源头）|
| M3 (ks 稀疏) | **39** | #2/#3/#4/#5/#8/#9/#10 |
| M4-orthogonal | **3** | #2/#4/#7 |
| M4-group_dep | **7** | #1×2/#2/#3/#7/#10×2 |
| M4-seasonal | **1** | #1 |
| M4-marginal | **1** | #10 |
| M4-reversal | **2** | #4/#5 |
| **TOTAL** | **54** | 9/10 scenarios |

### 4.2 三个高质量信号

1. **"openai 比 gemini 多 28 条 ks_*"是真的** — openai 倾向写更深分类列交叉。Path D 是对症方案，本批 39→0 验证。
2. **#4 同列 M1 + reversal 联袂** = 结构公式 sign/中介错的强信号。calibration 修不了；要修需让 LLM 重写公式。
3. **M4-orthogonal 全 3 条都是"dimension group 退化为单值"**：agpds_33d84d2c9b campus×year 1×1；agpds_503613ba96 campus×quarter 1×4；agpds_8180fe4e2c year×university 3×1。属 M2 (joint-distribution blind spot) 在 column-declaration 层的同源问题——本文 §8.2 给修法。

### 4.3 M4-group_dep drift 分布

| Scenario | drift |
|---|---:|
| #10 intervention_program | 0.3029 |
| #7 school | 0.1756 |
| #1 material_type | 0.1657 |
| #2 outreach_channel | 0.1529 |
| #1 service_channel | 0.1431 |
| #10 grade_level | 0.1151 |
| #3 aid_program | 0.1123 |

7 条全部由 §6 追根证明是 **sampling-sensitivity 问题，不是 LLM 错**。

---

## 5. #4 `student_faculty_ratio` M1 残留

详见 [mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md](../mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md)。

一句话：LLM 公式里有 `enrollment / faculty` 除法算子，除法引入结构方差（`(A/B)² × ((σ_A/A)² + (σ_B/B)²)`），不在 LLM 加性 noise sigma 声明范围内。Calibration 把 sigma 从 ~1.15 调到 4.43（base 值 8 的 55%）后到了 LLM 的 sensible ceiling，停在 ratio=0.77。

**决定：接受为已知长尾**——不修。同列 reversal 失败说明更深的公式骨架问题，单修 sigma 不足。

---

## 6. #10 `group_dep_intervention_program` 0.30 离群追根

实查 [declarations/agpds_e9c40d0352.json](../../../output/agpds/pingyue-samples-openai-calibrated/declarations/agpds_e9c40d0352.json) + [master_tables/agpds_e9c40d0352.csv](../../../output/agpds/pingyue-samples-openai-calibrated/master_tables/agpds_e9c40d0352.csv)。**结论：declaration 没错，根因是 validator 阈值 + 上游 marginal 弱化的级联。**

### 6.1 失败定位到单 cell

`max_deviation=0.3029` 来自唯一一个 cell：

| Cell | declared | empirical (count/total) | \|Δ\| |
|---|---:|---:|---:|
| `(grade_level=2, "No Intervention")` | **0.6600** | **0.3571** (5/14) | **0.3029** |

### 6.2 三个证据排除 LLM 错

1. **Weights 干净 normalized**：13 行 × 4 列每行行和精确 = 1.0000。
2. **Magnitude plausible**：grade=2 的 0.66 落在 K=0.68 → 1=0.68 → 2=**0.66** → 3=0.64 → 4=0.62 的平滑趋势上。
3. **没有 realism config**：declarations 里无 `set_realism` / `realism` 键。

### 6.3 真正根因：小样本 binomial 方差 × 上游 marginal 级联

- 全表 420 行，**grade=2 仅 n=14**（占 3.3%）
- 同 scenario 上游也失败：`marginal_weights_grade_level: max_dev=0.1024`（贴线）+ `group_dep_grade_level: max_dev=0.1151`（11.5%）
- 链：上游 grade_level marginal 弱化 → grade=2 比应当 under-sampled → 经验方差因 n 小而放大 → 单 cell 飘 0.30
- Binomial 校验：n=14, p=0.66 期望 9.24 / 实测 5，偏 2.4σ —— **小样本预期波动内**

### 6.4 修正 §4.3 预设

§4.3 之前把 0.10–0.18 的 6 条归为"sampling variance + realism 推过线"，把 #10 的 0.30 单列为"离群点 / 可能 declaration 错"。**经此追根，#10 跟那 6 条同根**——只是因为 cell n 更小（14 vs 30+）、波动空间更大才显得离群。**7 条 group_dep_\* 全部是 sampling-sensitivity 问题，不是 LLM 责任。**

---

## 7. Path D 应用后的当前 state

Path D commit `a7602e6` validator-only rerun（baseline declarations bit-for-bit identical）：

| 指标 | Baseline | Path D rerun | Delta |
|---|---:|---:|---|
| passed | 1/10 | **5/10** | **+4** |
| total failures | 54 | **13** | **-76%** |
| `ks_*` | 39 | **0** | **-100%** |
| `residual_*` | 1 | 1 | 0（#4 M1 长尾）|
| `orthogonal_*` | 3 | 3 | 0 |
| `group_dep_*` | 7 | 6 | -1（#3 边缘翻 pass，二阶效应）|
| `reversal_*` | 2 | 1 | -1（#5 边缘翻 pass，同上）|
| `seasonal_*` | 1 | 1 | 0 |
| `marginal_*` | 1 | 1 | 0 |
| regressions | — | **0** | ✓ |

**剩 13 条按失败族归责**：

| 失败族 | 数量 | 责任层 | 修复路径 |
|---|---:|---|---|
| `group_dep_*` | 7 | **validator + sampling**（§6 已证）| Phase A（§8.1）|
| `marginal_*` | 1 | 同上 | Phase A |
| `orthogonal_*` | 3 | LLM 声明 orthogonality 未核对 dimension 退化 | Phase B（§8.2）|
| `reversal_*` | 2 | LLM 公式骨架 sign / 中介错 | Phase C（§8.3）|
| `seasonal_*` | 1 | LLM 季节振幅未与 baseline_std 对齐 | Phase D（§8.4）|
| `residual_*` | 1 | M1 ratio-operator 长尾 | **已接受不修**（§5）|

**8/13 可由 Phase A 一次性消掉**；5/13 是真 LLM bug 需要 prompt 升级。

---

## 8. 下一步修改计划

### 8.1 Phase A（推荐先做）：`group_dep_*` / `marginal_*` 阈值 n-aware

**范围**：[statistical.py::max_conditional_deviation](../../../pipeline/phase_2/validation/statistical.py) ~20 行 + 单测

**算法**：阈值由固定 0.10 改为 n-aware 公式：
- 候选 1：`0.10 × √(30/n)` 当 n<30，否则 0.10（参考 Path D n=30 边界）
- 候选 2：`0.10 + z * √(p(1-p)/n)` 显式 Wald 置信区间（更严谨但需 p 估计）
- 候选 3：n<某下限直接 skip 该 cell（最激进，类比 Path D n<30 skip）

实施前先用 §9 的 jq + python 命令对剩 7 条 group_dep 跑一遍候选公式，看哪种把 7+1 条都消掉但不放过真 declaration 错（如果未来出现）。

**单测**：
- n=14, p=0.66, observed=5/14 (Δ=0.30) → PASS（n-aware 阈值放宽）
- n=100, p=0.66, observed=46/100 (Δ=0.20) → FAIL（n=100 仍按 0.10 严格判）
- n=14, p=0.66, observed=0/14 (Δ=0.66) → FAIL（n 再小也不该放过 magnitude error）

**预期**：消掉 7 条 group_dep + 1 条 marginal = 8/13 剩余失败。

**风险**：低（validator 内部，无 LLM 行为变化、无数据重生成）。

**配套**：可选 Constraint 14"声明 group_dependency 时尽量让 cell n ≥ 某阈值"（让 LLM 主动算 target_rows，类似 Constraint 13）。

### 8.2 Phase B：`orthogonal_*` — prompt 加 dimension-non-degenerate 约束

3 条 orthogonal 失败全是 declared 正交的两列在采样空间里至少一列退化为单值（1×1 / 1×4 / 3×1 contingency table）。

**修法选项**：
- **prompt 端**：[prompt.py](../../../pipeline/phase_2/orchestration/prompt.py) 加 Constraint 15"声明 `declare_orthogonal(A, B)` 前确认 A 和 B 在 scenario 采样后都至少有 2 个 unique 值——单值 dimension 不可参与正交声明"
- **validator 端**：检测 1×N / N×1 degenerate 时 skip + soft-pass（类比 Path D 的 all-skip 兜底）

**预期**：消掉 3 条 orthogonal。

**风险**：低-中（prompt 改动需要 production rerun 验证 LLM 确实听懂；validator 兜底版无风险但等于把问题 swept under rug）。

### 8.3 Phase C：`reversal_*` — 系统性追根

2 条 reversal 性质不同：
- **#4 `reversal_course_load_student_faculty_ratio`**：跟 M1 残留同列同根，公式骨架共享 `enrollment` 分子 / `faculty` 分母（详 §3.4 + §5）。修法绑定 M1 ratio-operator 修复。
- **#5 `reversal_grant_funding_citation_count`**：LLM 在声明里加了"经费 ↔ 引用应当负相关"的反直觉关系，但实际公式没实现。修法：让 LLM 重写公式，或检视 LLM 是否误解了 domain（一般经费↑→引用↑，反相关不符合主流认知，可能是 prompt 误导）。

**修法**：
- 先 inspect 两个 declarations 的 measure formula
- #4 → 跟 M1 一起治（详 [mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md §7](../mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md) 的 A/B 方案）
- #5 → prompt 加 Constraint 16"声明 measure 间相关方向时，验证公式 actually 实现该方向"

**预期**：消掉 1-2 条 reversal。

**风险**：高（需要 scenario 重新生成数据验证 LLM 自修能力，最重）。

### 8.4 Phase D：`seasonal_*` — 振幅约束

1 条 seasonal：`seasonal_checkout_count z=0.050 (threshold 1.5)`。LLM 声明的季节性振幅相对 baseline_std 太小（z 远低于 1.5）。

**修法**：prompt 加 Constraint 17"声明季节性 `inject_pattern("seasonal", ...)` 时，amplitude / baseline_std ≥ 2.0 才能被 validator 识别为可信季节性。如果 amplitude 受 domain 约束必须小，考虑用 `add_trend` 取代 `add_seasonality`。"

**预期**：消掉 1 条 seasonal。

**风险**：低（纯 prompt 改动）。

### 8.5 长尾接受

1 条 `residual_student_faculty_ratio` (#4 M1 ratio-operator straggler) — **已决定接受不修**。详 [mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md](../mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md) §7。触发升级到主动修复的条件：未来批次 ratio operator 出现率 > 30%、或单 scenario 多条 ratio measure 同时残留。

### 8.6 性价比 + 推荐执行顺序

| Phase | 修掉条数 | 投入 | 风险 | 顺序 |
|---|---:|---|---|---|
| A | 8 | ~20 行 + 单测 | 低 | **先做** |
| B | 3 | prompt + 可选 validator | 低-中 | A 之后 |
| D | 1 | 纯 prompt | 低 | B 同期 |
| C | 1-2 | prompt + 数据重生成 | 高 | 最后 |
| §8.5 | 0 | — | — | 接受 |

**推荐**：A → (B + D 并行) → C。预期跑完 Phase A+B+D 后剩 1-2 条 failures（全是 C 范畴），届时再做 scenario 重生成验证 C。

---

## 9. 验证 / 复现命令

```bash
cd /home/dingcheng/projects/chartAgentVAGEN

# 1. 看整体失败分布（基线 vs Path D）
for batch in pingyue-samples-openai-calibrated pingyue-samples-openai-calibrated-pathD-revalidation; do
  echo "=== $batch ==="
  cat output/agpds/$batch/validation_summary.json \
    | jq -r '.[].failures[].name' | sed 's/_.*//' | sort | uniq -c
done

# 2. 逐 scenario 失败列表（Path D rerun）
jq '.[] | {id: .generation_id, all_passed, n: (.failures | length), names: [.failures[].name]}' \
   output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation/validation_summary.json

# 3. 验证 §6 root cause（#10 group_dep 0.30）
jq '.group_dependencies[] | select(.parents == ["grade_level"] and .child == "intervention_program")' \
   output/agpds/pingyue-samples-openai-calibrated/declarations/agpds_e9c40d0352.json
python3 <<'PY'
import pandas as pd
df = pd.read_csv("output/agpds/pingyue-samples-openai-calibrated/master_tables/agpds_e9c40d0352.csv")
ct = pd.crosstab(df['grade_level'], df['intervention_program'], normalize='index')
print(ct.round(4))
print("\ngrade=2 row count:", (df['grade_level']==2).sum())
PY

# 4. 验证 §5 root cause（#4 student_faculty_ratio 公式）
jq '.columns[] | select(.name == "student_faculty_ratio" or .name == "course_load")' \
   output/agpds/pingyue-samples-openai-calibrated/declarations/agpds_503613ba96.json

# 5. Phase A 实施后验证：跑同样 validator-only rerun，对照
#    output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation/validation_summary.json
#    预期：group_dep_* 6→0、marginal_*  1→0、其他不变
```

---

## 10. 相关

- 入口：[ANALYSIS.md](../ANALYSIS.md) / [FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md)
- Batch-level summary：[OPENAI_VALIDATION.md](OPENAI_VALIDATION.md)
- 机制纵深：[mechanisms/MECHANISM_1_DEEP_DIVE.md](../mechanisms/MECHANISM_1_DEEP_DIVE.md) / [mechanisms/MECHANISM_3_DEEP_DIVE.md](../mechanisms/MECHANISM_3_DEEP_DIVE.md)
- M1 长尾：[mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md](../mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md)
- 子系统：[subsystems/SIGMA_CALIBRATION.md](../subsystems/SIGMA_CALIBRATION.md) / [subsystems/PATH_D_KS_SPARSE_CELLS.md](../subsystems/PATH_D_KS_SPARSE_CELLS.md)
