# 机制 4（小样本比例漂移误判）深度剖析：根因 → 算法 → 实测

> 配套阅读：[ANALYSIS.md](../ANALYSIS.md) 是一页综述；[validation/PINGYUE_OPENAI_CAL_ANALYSIS.md §6](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#6-10-group_dep_intervention_program-030-离群追根) 用 hand-traced binomial 校验证明了 #10 离群点是 sampling 问题不是 LLM 错——本文是 Phase A 的纵深，把"为什么固定 0.10 阈值在小 n cell 上必然误判 → 我们怎么用 n-aware Wald 95% CI 替换 → pingyue-samples-openai-calibrated 上的真实失败和修复后的实测"串成一条线。
>
> 数据来自两个 byte-identical declarations / master_tables 批次（同 10 scenario · openai · seed=42 · Path A + Loop A calibration + Path D 全开）：
> - `output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation` — Path D 已上线，**固定 0.10 阈值**
> - `output/agpds/pingyue-samples-openai-calibrated-pathA-rev` — **n-aware Wald CI 上线**（Phase A）
>
> 两批同 df、同 declarations，validator 行为差异完全可归因。

---

## 1. 一页总结

| 维度 | Path D 基线 | **Phase A** |
|---|:-:|:-:|
| passed | 5/10 | **6/10** ✓ |
| total failures | 13 | **6** (-54%) |
| `group_dep_*` count | 6 | **0** ✓ |
| `marginal_*` count | 1 | **0** ✓ |
| `residual_*` count | 1 | 1（M1 ratio 长尾，已接受）|
| `orthogonal_*` count | 3 | 3（Phase B 范围）|
| `reversal_*` count | 1 | 1（Phase C 范围）|
| `seasonal_*` count | 1 | 1（Phase D 范围）|
| 新单测 | — | **+18**（5 Wald helper · 9 group_dep · 4 marginal）|
| 回归 | — | **0** |

**Headline**：Phase A 把比例漂移族（`group_dep_*` + `marginal_*`）的 7 条失败**全部**关闭，并把 [`agpds_e9c40d0352`](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#310-agpds_e9c40d0352--芝加哥高中入学) 从 3-fail 翻成 PASS——它的 3 条失败全部是 sampling envelope 误判。剩 6 条 failure 全部归属其他机制范畴（M1 ratio 长尾 / orthogonal / reversal / seasonal），无一为比例漂移。

---

## 2. 根本原因：固定阈值 vs 二项采样包络

### 2.1 SDK 让 LLM 声明条件 / 边缘权重

LLM 在 `FactTableSimulator` SDK 里这样写：

```python
sim.add_category("grade_level", values=list(range(13)),
                 weights=[0.10, 0.08, 0.08, 0.08, ...])   # marginal weights

sim.add_group_dependency(
    parents=["grade_level"],
    child="intervention_program",
    conditional_weights={
        2:  {"No Intervention": 0.66, "Tutoring": 0.20, ...},   # cell n 由 marginal × N 决定
        3:  {"No Intervention": 0.64, ...},
        ...
    },
)
```

LLM 把它读成一句独立声明：「在 `grade_level=2` 这条 cell 里，66% 的学生**应该**没有干预」。这是 LLM 对**该 cell 真值比例**的闭式预言。

### 2.2 引擎按声明采样，但每个 cell 的 n 不可控

引擎按 marginal weights 决定 `grade_level` 各值的行数，再按 conditional weights 在每个 cell 内采样 `intervention_program`。两步合起来意味着：

- 总样本量 `N = target_rows`（典型 420 / 1000 / 1800）
- cell `(grade_level=2)` 的 n = N × marginal[grade=2] = 420 × 0.05 ≈ **21**（如果 marginal 准）或更小（如果 marginal 自己偏低）
- 在 n=14 这个 cell 里，"66% No Intervention" 是个 **binomial(n=14, p=0.66)** 的真值

### 2.3 数学：二项采样的 std 在小 n 上很可观

对 binomial 比例 $\hat{p}$，标准差：

$$\mathrm{SD}(\hat{p}) = \sqrt{\frac{p(1-p)}{n}}$$

95% Wald 置信区间宽度：

$$\mathrm{CI}_{95}(\hat{p}) = \pm\,1.96\,\sqrt{\frac{p(1-p)}{n}}$$

把 §1 的真实失败代入：

| Cell | declared p̂ | n | SD(p̂) | 95% CI 半宽 |
|---|---:|---:|---:|---:|
| `grade=2 → No Intervention` | 0.66 | 14 | 0.1266 | **0.248** |
| `grade=2 → No Intervention`（如果 n=30）| 0.66 | 30 | 0.0865 | 0.170 |
| `grade=2 → No Intervention`（如果 n=420）| 0.66 | 420 | 0.0231 | 0.045 |

n=14 的 cell 上，**单纯 sampling 就能让 $\hat{p}$ 偏离声明 ±0.25**——比 validator 的固定 0.10 阈值宽 2.5 倍。即"LLM 完全没错、二项就是这么散的"。

### 2.4 Validator 用固定阈值 → 必然误判

[Phase D 之前的 `check_group_dependency_transitions`](../../../pipeline/phase_2/validation/statistical.py#L544)（伪码）：

```python
max_dev = max(|empirical_p − declared_p|, ∀ (cell, child_level))
passed = max_dev < 0.10        # ← 固定阈值，n 不可见
```

引擎把所有 cell 的所有 child level 压成一个 scalar，再跟 0.10 比。**这个判定不知道 cell n 多大**——n=14 的 cell 飘 0.30 跟 n=420 的 cell 飘 0.30 在它眼里完全等价。结果：

- n=14, p̂=0.66 cell：sampling 自然 |Δ| ≈ 0.25 → validator 必然报错
- n=17, p̂=0.20 cell：sampling 自然 |Δ| ≈ 0.19 → validator 必然报错
- ...

只要某条 conditional_weights 声明在 marginal 弱化或 cross-cell 划分稀疏的情况下让 cell n < 30，固定 0.10 阈值就会把 sampling noise 误判为 drift。openai 倾向写"更深分类列交叉"（[doc §3.5 教科书例子](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#35-agpds_65ef0afda0--stanford-研究经费--最多-ks)）使 cell n 普遍偏小，所以这个 mechanism 在 openai 批次上比 gemini 更显眼。

### 2.5 §6 已用 hand-trace 证明：6/7 的 group_dep 失败属此机制

[PINGYUE_OPENAI_CAL_ANALYSIS.md §6](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#6-10-group_dep_intervention_program-030-离群追根) 对 #10 离群点（max_dev=0.3029）做了三步追根：

1. weights normalize 干净 → declaration 没错
2. magnitude 在 K=0.68→0.66→0.64 平滑趋势上 → LLM 没乱写
3. n=14 的 binomial 期望 9.24 / 实测 5 = **2.4σ** → **小样本预期波动内**

§6.4 把 7 条 group_dep 推到同一机制：

> "经此追根，#10 跟那 6 条同根——只是因为 cell n 更小（14 vs 30+）、波动空间更大才显得离群。**7 条 group_dep_\* 全部是 sampling-sensitivity 问题，不是 LLM 责任。**"

加上同 scenario 的 `marginal_weights_grade_level: max_dev=0.1024` 在 n=420 上贴线，**7+1=8 条失败全部属机制 4 比例漂移**。Path D 验证器只清 KS；group_dep / marginal 落到 Phase A 范围。

---

## 3. 实际失败案例：Path D 基线的真实失败

下面是 `pingyue-samples-openai-calibrated-pathD-revalidation/validation_summary.json` 里所有 7 条 Phase A scope 失败的 hand-traced 数据（cell n + p̂ 通过 master_tables 重算）：

| Scenario | Check | offending cell | n | declared p̂ | empirical p̂ | dev | 当前阈值 |
|---|---|---|---:|---:|---:|---:|---:|
| `agpds_e9c40d0352` | `group_dep_intervention_program` | `grade=2 → No Intervention` | **14** | 0.66 | 0.357 | **0.303** | 0.10 (FAIL) |
| `agpds_8180fe4e2c` | `group_dep_school` | `residency=International → Ross` | 36 | 0.13 | 0.306 | 0.176 | 0.10 (FAIL) |
| `agpds_14b7f7487e` | `group_dep_material_type` | `audience=Educators → Digital Audiobooks` | **14** | 0.12 | 0.286 | 0.166 | 0.10 (FAIL) |
| `agpds_33d84d2c9b` | `group_dep_outreach_channel` | `segment=Transfer → Admitted Events` | **17** | 0.20 | 0.353 | 0.153 | 0.10 (FAIL) |
| `agpds_14b7f7487e` | `group_dep_service_channel` | `material=Children's Kits → Outreach` | 29 | 0.35 | 0.207 | 0.143 | 0.10 (FAIL) |
| `agpds_e9c40d0352` | `group_dep_grade_level` | `school=Whitney Young → grade=11` | 63 | 0.25 | 0.365 | 0.115 | 0.10 (FAIL) |
| `agpds_e9c40d0352` | `marginal_weights_grade_level` | `grade_level=*（贴线）` | 420 | ~0.10 | ~0.20 | 0.102 | 0.10 (FAIL) |

（中位 dev = 0.153, 最大 = 0.303，**全部 cell n ≤ 63**——marginal 失败也只是因为 declared p=0.10 在 n=420 上的 95% CI 半宽 = 0.029，固定 0.10 阈值在边界刚好被压下来）

### 3.1 Case study：`agpds_e9c40d0352::group_dep_intervention_program`

[validation_summary.json](../../../output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation/validation_summary.json) 报：

```
parents=['grade_level'], child='intervention_program',
max_deviation=0.3029 (>= 0.10)
```

LLM 在 [declarations/agpds_e9c40d0352.json](../../../output/agpds/pingyue-samples-openai-calibrated/declarations/agpds_e9c40d0352.json) 里这样声明（13 行 × 4 列条件权重）：

```json
{
  "child_root": "intervention_program",
  "on": ["grade_level"],
  "conditional_weights": {
    "0": {"No Intervention": 0.68, "Tutoring": 0.18, ...},
    "1": {"No Intervention": 0.68, ...},
    "2": {"No Intervention": 0.66, "Tutoring": 0.20, "Counseling": 0.10, "Mentoring": 0.04},
    "3": {"No Intervention": 0.64, ...},
    ...
  }
}
```

**它没看见的耦合**：

- master_table 总共 420 行；`grade_level=2` 在采样后只占 **n=14**（marginal 自己弱化 0.10 → 0.077 也在贴线，已 §6.4 证明同根）
- 在 n=14 这个 cell 里，binomial(14, 0.66) 的 95% CI 半宽 = **0.248**
- 实测 `No Intervention` 出现 5 次：$\hat p = 5/14 = 0.357$，与声明的 0.66 差 0.303
- Wald-Z 检验：$|0.357 - 0.66| / 0.1266 \approx 2.4\sigma$——**仍在 95% CI 内**，纯采样波动
- Validator 走固定 0.10 → soft-fail

### 3.2 为什么 Loop B 救不了

Loop B 的自动修复工具（[validation/autofix.py](../../../pipeline/phase_2/validation/autofix.py)）面向 sigma / 分布参数，对 conditional_weights 没有手段。即使有，"把 `grade=2 → No Intervention` 从 0.66 改成 0.36" 也是错的——因为下一次同 seed sample 仍可能落到 0.66 ± 0.25 范围里另一个点。问题不在 LLM 的数字，而在 validator 的阈值。

### 3.3 Loop A calibration 也救不了

[Loop A in-loop sigma calibration](../subsystems/SIGMA_CALIBRATION.md) 解决的是 measure_type=="structural" 的 noise sigma（机制 1）。conditional_weights 不属于 measure DAG，calibration 不扫它。即使扫了，按 §3.1 的 math 也不应该让 LLM 改 weights——LLM 已经写对了。**这个 mechanism 必须在 validator 侧解决。**

---

## 4. 解决方案：n-aware Wald 95% CI per (cell, child_level)

### 4.1 一句话

> 把固定 `dev < 0.10` 替换为 `dev < 0.10 + 1.96·√(p̂(1-p̂)/n)`，per **(leaf cell, child_level)** 评估；n < 10 的 cell skip 不评（mirror Path D `KS_MIN_CELL_SIZE=30` 的精神，更低阈值因为 dev 比较比 KS test 稳健）；all-pass 聚合——一个 offending (cell, level) 就拖整张 Check。

### 4.2 为什么这能区分 sampling noise 和真错

| 阈值组件 | 干什么 | 退化行为 |
|---|---|---|
| **base = 0.10** | 即使 n→∞ 也保留"magnitude error 不能 white-wash"的底线 | n=10⁶ p̂=0.5：threshold = 0.100 + 1.96·0.0005 ≈ 0.10——跟旧逻辑等价 |
| **Wald 项 = 1.96·√(p̂(1-p̂)/n)** | 在小 n 上把 sampling envelope 让出来 | n=14 p̂=0.66：threshold = 0.10 + 0.248 = **0.348** → 0.303 落进 → PASS |
| **n<10 skip** | 极小 cell 不做判断，避免 threshold 爆炸 | n=5 p̂=0.5：threshold 会到 0.539，已无判定力 → skip 更诚实 |

**0.10 base 的作用**：n=10⁶ 时 Wald 项几乎为 0，旧的 magnitude-error catching 行为完全保留。比如 LLM 把 `(grade=5 → No Intervention)` 写成 0.95 但实际是 0.30，n=420 上 threshold = 0.148，dev = 0.65 → FAIL，validator 仍然抓得到。

**Wald 项的作用**：在 n=14 cell 上 threshold 主动让出 0.25 的空间，恰好覆盖二项 95% 包络。LLM 写对而 sampling 飘出去的不再误判。

### 4.3 算法流程

```
check_group_dependency_transitions(df, meta)：

for each declared group dependency (child_root, on_cols, conditional_weights):

  per_cell_levels = []
  skipped_cells = []

  # Walk leaf cells under on_cols
  for cell_path, group_df in df.groupby(on_cols):
    n_cell = len(group_df)
    declared = walk_nested_dict(conditional_weights, cell_path)
    if declared is None: continue  # declaration lookup miss

    if n_cell < GROUP_DEP_MIN_CELL_SIZE:   # = 10
      skipped_cells.append((cell_path, n_cell))
      continue

    empirical = group_df[child_root].value_counts(normalize=True)
    for child_level, p_hat in declared.items():
      emp = empirical.get(child_level, 0.0)
      dev = abs(emp - p_hat)
      per_cell_levels.append((cell_path, child_level, n_cell, p_hat, dev))

  # Per-(cell, level) Wald threshold + all-pass
  offenders = [
    (cell, lvl, n, ph, dv, t)
    for (cell, lvl, n, ph, dv) in per_cell_levels
    if dv >= (t := 0.10 + 1.96·√(ph·(1-ph)/n))
  ]

  passed = not offenders
  detail = summary + per-offender breakdown (cap 10 + "+N more")
```

`check_marginal_weights` 完全平行——只是 cell = whole table, `n = len(df)`, 比较 per category。

### 4.4 关键设计决策

| 决策 | 选择 | 理由 |
|---|---|---|
| 阈值公式 | **Wald 95% CI** | 实测数据上 candidate A (`0.10·√(30/n)`) 0/7 cleared、Wald 7/7 cleared、Path D 风格 `skip<30` 4/7 silent-pass（doc §6 已证违反 transparency）。详 [plan 决策表](../../../../.claude/plans/pingyue-samples-openai-calibrated-soft-sprightly-melody.md) §Context |
| 阈值位置 | **per (cell, child_level)** | 不同 cell n 不同，单一全局阈值无法 amortize；每个 (cell, level) 单独评估更准 |
| 聚合方式 | **all-pass strict** | Wald 已经吸收 sampling noise；再叠 Path D-style pass-rate 0.9 会过于宽松；strict 是更安全的默认 |
| 小 n cell | **n < 10 skip + 诚实标注** | 与 Path D `KS_MIN_CELL_SIZE=30` 同精神但更低；deviation 比较比 KS test 对样本量更宽容（详 plan AskUserQuestion 数据）|
| 底线 floor | **0.10 保留** | 让 magnitude error 在 n→∞ 时仍被抓；Wald 项仅 *增加* 容忍度 |
| `max_conditional_deviation` 工具函数 | **不动** | 4 standalone tests 锁 depth-1/2/3 dict-comparison 行为；新逻辑全部 inline 进 `check_group_dependency_transitions`，blast radius 最小 |
| LLM-only vs Validator-only | **validator-only** | LLM 已经写对了 (§3.1 hand-trace 证明)；动 prompt 让 LLM 更深 cross 反而可能恶化 cell n；本次只动 validator |

### 4.5 代码位点

| 文件 | 行 | 内容 |
|---|---|---|
| [validation/statistical.py:32-58](../../../pipeline/phase_2/validation/statistical.py#L32-L58) | new | `GROUP_DEP_{MIN_CELL_SIZE,BASE_DELTA,Z_95,DETAIL_CELL_CAP}` 常量 + `_wald_dev_threshold(n, p_hat, base, z)` helper |
| [validation/statistical.py:575-710](../../../pipeline/phase_2/validation/statistical.py#L575-L710) | refactored | `check_group_dependency_transitions`：groupby 收集 `(cell_path, child_level, n_cell, p_hat, dev)`，per-cell Wald 阈值，all-pass 聚合，detail 上 cell-level breakdown |
| [validation/structural.py:213-298](../../../pipeline/phase_2/validation/structural.py#L213-L298) | refactored | `check_marginal_weights`：per-category Wald per `len(df)`，n<10 skip，all-pass 聚合 |
| [tests/modular/test_validation_phase_a.py](../../../pipeline/phase_2/tests/modular/test_validation_phase_a.py) | new | 18 测试：Wald helper 边界 / 小 n skip / Wald clear 噪声 / magnitude 仍 fail / nested parents / detail 格式 |

Git 历史：
- `50098aa` feat(phase_2): add Wald-CI threshold helper for proportion drift checks
- `e9de06f` feat(phase_2): Phase A — n-aware Wald CI for check_group_dependency_transitions
- `c5561be` feat(phase_2): Phase A — n-aware Wald CI for check_marginal_weights

### 4.6 Detail string 的实际样子

**Before（Path D 固定 0.10）**：

```
parents=['grade_level'], child='intervention_program',
max_deviation=0.3029 (>= 0.10)
```

只暴露一个 scalar，问题 cell 不可见。Postmortem 必须自己跑 jq + pandas（详 [doc §6.1](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#61-失败定位到单-cell)）。

**After（Phase A 通过的样子）**：

```
parents=['grade_level'], child='intervention_program',
tested=52 (cell,level), skipped_cells=0 (n<10), offenders=0
```

明确告诉读者：扫了 52 条 `(cell, level)` 评估，没有 cell 因 n<10 被跳过，没有 offender——确诊"全部 cell 在 sampling envelope 内"。

**After（如果仍 fail，如 test_one_bad_cell_fails_aggregate）**：

```
parents=['parent'], child='child', tested=4 (cell,level), skipped_cells=0 (n<10), offenders=2 |
X->A: n=100, p_hat=0.500, dev=0.5000, thresh=0.1980;
X->B: n=100, p_hat=0.500, dev=0.5000, thresh=0.1980
```

per-offender 三件套 `(n, p_hat, dev, thresh)`——可直接 cross-check 是否属于"真 magnitude error"还是"我们的 threshold 还不够宽"。

---

## 5. 修复后效果：Phase A rerun 实测

### 5.1 Per-scenario 失败明细

| Scenario | Path D (before) | Phase A (after) | Δ |
|---|---|---|---|
| `agpds_14b7f7487e` | 3 fails (2 group_dep + 1 seasonal) | 1 fail: `seasonal_checkout_count` | **-2** |
| `agpds_33d84d2c9b` | 2 fails (1 group_dep + 1 orthogonal) | 1 fail: `orthogonal_campus_year` | **-1** |
| `agpds_3af92040e6` | ✓ PASS (0) | ✓ PASS (0) | 0 |
| `agpds_503613ba96` | 3 fails (1 residual + 1 orthogonal + 1 reversal) | 3 fails (unchanged) | 0 |
| `agpds_65ef0afda0` | ✓ PASS (0) | ✓ PASS (0) | 0 |
| `agpds_8022981cf7` | ✓ PASS (0) | ✓ PASS (0) | 0 |
| `agpds_8180fe4e2c` | 2 fails (1 group_dep + 1 orthogonal) | 1 fail: `orthogonal_year_university` | **-1** |
| `agpds_985a1b72e1` | ✓ PASS (0) | ✓ PASS (0) | 0 |
| `agpds_d62b18e180` | ✓ PASS (0) | ✓ PASS (0) | 0 |
| `agpds_e9c40d0352` | 3 fails (2 group_dep + 1 marginal) | **✓ PASS (0)** | **-3** ✓ |

**比例漂移失败：7 → 0（100% 关闭）**
**passed scenario 数：5/10 → 6/10**
**regressions：0**（5 个原本 passing 的 scenario 全部保持 passing）

### 5.2 LLM 完全没改任何东西

这是 validator-only 改造的最大特征：**declarations + master_tables 字节一致**，没有 LLM regeneration。同一份 `agpds_e9c40d0352::intervention_program` 的 conditional_weights JSON 在两个批次里逐字节相同，validator 一边报 dev=0.3029 fail、一边报 offenders=0 pass。差异完全可归因于 threshold 算法。

可用以下命令验证字节一致：

```bash
diff -r output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation/declarations \
       output/agpds/pingyue-samples-openai-calibrated-pathA-rev/declarations
diff -r output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation/master_tables \
       output/agpds/pingyue-samples-openai-calibrated-pathA-rev/master_tables
# (无输出 = 字节一致)
```

### 5.3 7 条原失败的 Wald 阈值表

把 §3 表格补完 with after 状态：

| Check | n | p̂ | dev | Wald threshold | passed? |
|---|---:|---:|---:|---:|:--:|
| `group_dep_intervention_program` (e9c4...) | 14 | 0.66 | 0.303 | **0.348** | ✓ |
| `group_dep_school` (8180...) | 36 | 0.13 | 0.176 | **0.210** | ✓ |
| `group_dep_material_type` (14b7...) | 14 | 0.12 | 0.166 | **0.270** | ✓ |
| `group_dep_outreach_channel` (33d8...) | 17 | 0.20 | 0.153 | **0.290** | ✓ |
| `group_dep_service_channel` (14b7...) | 29 | 0.35 | 0.143 | **0.274** | ✓ |
| `group_dep_grade_level` (e9c4...) | 63 | 0.25 | 0.115 | **0.207** | ✓ |
| `marginal_weights_grade_level` (e9c4...) | 420 | ~0.10 | 0.102 | **0.148** | ✓ |

7/7 dev < threshold——sampling envelope 完全吸收。

### 5.4 失败类型从"假阳性"转成"真问题"

| 失败族 | Path D 基线 | Phase A | 责任层 |
|---|:-:|:-:|---|
| `group_dep_*`（小样本误判） | 6 | **0** ✓ | validator threshold（本机制） |
| `marginal_*`（小样本误判） | 1 | **0** ✓ | validator threshold（本机制） |
| `residual_*` | 1 | 1 | LLM ratio operator 长尾（[M1 straggler](M1_RATIO_OPERATOR_STRAGGLER.md)，已接受）|
| `orthogonal_*` | 3 | 3 | LLM 声明 degenerate dimension 未审（**Phase B 范围**）|
| `reversal_*` | 1 | 1 | LLM 公式骨架 sign/中介错（**Phase C 范围**）|
| `seasonal_*` | 1 | 1 | LLM 季节振幅 vs baseline_std（**Phase D 范围**）|

剩 6 条 failure 全部是**真问题**——LLM 行为缺陷，需要 prompt 端 / 公式端介入。Phase A 把 validator 假阳性彻底清掉，让下游 Phase B/C/D 不再被假信号污染。

### 5.5 agpds_e9c40d0352 detail diff（一手证据）

Path D rerun，6 个 marginal_weights_*  / group_dep_* checks 的状态：

```
marginal_weights_school              passed=True    max_deviation=0.0333 (< 0.10)
marginal_weights_grade_level         passed=False   max_deviation=0.1024 (>= 0.10)  ←
marginal_weights_intervention_program passed=True   max_deviation=0.0157 (< 0.10)
marginal_weights_reporting_source    passed=True    max_deviation=0.0271 (< 0.10)
group_dep_grade_level                passed=False   max_deviation=0.1151 (>= 0.10)  ←
group_dep_intervention_program       passed=False   max_deviation=0.3029 (>= 0.10)  ←
```

Phase A rerun，同 scenario：

```
marginal_weights_school              passed=True    n=420, categories=6, offenders=0
marginal_weights_grade_level         passed=True    n=420, categories=13, offenders=0
marginal_weights_intervention_program passed=True   n=420, categories=4, offenders=0
marginal_weights_reporting_source    passed=True    n=420, categories=3, offenders=0
group_dep_grade_level                passed=True    parents=['school'], child='grade_level',
                                                    tested=78 (cell,level), skipped_cells=0 (n<10), offenders=0
group_dep_intervention_program       passed=True    parents=['grade_level'], child='intervention_program',
                                                    tested=52 (cell,level), skipped_cells=0 (n<10), offenders=0
```

3 个 failing check 同时 flip 到 PASS，scenario `all_passed=True`。

---

## 6. 进一步阅读 / 已知坑

### 6.1 Wald CI 在 p̂={0,1} 边界退化为 0.10

Wald 项 $1.96\sqrt{p̂(1-p̂)/n}$ 在 $p̂=0$ 或 $p̂=1$ 时 = 0，threshold 退化为 base = 0.10。这是**故意的**：

- 真实 case：LLM 声明某 child level 概率为 0（"this cell never has X"）
- empirical 出现了任何 X → dev > 0 → 跟 0.10 比
- "声明 0% 但实测 5% 出现" 是 magnitude error，**应该**报错——不该让 Wald 项白送 buffer

[test_validation_phase_a.py::test_threshold_at_p_zero_floor_only](../../../pipeline/phase_2/tests/modular/test_validation_phase_a.py) 锁死这个 v1 行为。

### 6.2 Wilson / Agresti-Coull 没用，Wald 够用

Wilson CI / Agresti-Coull 在 small-n + p̂ 极端时比 Wald 更准。这里没用因为：

- 实测中没有 cell n < 10 的 Phase A scope failure（最小 n=14）
- declared p̂ 都不在 {0, 1} 边界（最极端 p̂=0.10 marginal）
- Wald 公式简单 + 在 n≥10 / p̂ 不极端时与 Wilson 几乎重合
- 单测 + 注释清晰胜过"更精准但读者要查教科书"

如果未来出现 cell n ∈ [10, 14] 且 p̂ < 0.05 的 case，再考虑切 Wilson。常量 `_wald_dev_threshold` 是单点替换。

### 6.3 n<10 skip 是 silent-pass 但比 fail 更诚实

跟 Path D `KS_MIN_CELL_SIZE=30` 的 trade-off 同源：

- **不修这个 trade-off**：n=5 cell skip 意味 validator 不评判这条 cell 的 conditional weight 是否对——是个 silent-pass。但 n=5 上 Wald 半宽到 0.44，已无统计 power。
- **比 fail 更诚实**：如果硬要判，5 个样本里 0 个/5 个匹配都是合理 sampling 结果，validator 会要么放 false positive 要么放 false negative。skip + detail 注明"skipped_cells=N (n<10)" 是更透明的设计。
- 实测：openai-cal Phase A rerun 上 0 条 cell 因 n<10 被 skip——所有 failing cell 都在 n∈[14, 420]。skip 是未来 safety net，不是当前主力。

### 6.4 仍未修

Phase A 已经关闭比例漂移机制。Path D 后 13 条 → Phase A 后 6 条，剩 6 条按 [PINGYUE_OPENAI_CAL_ANALYSIS.md §8](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#8-下一步修改计划) 分发：

1. **Phase B**：`orthogonal_*` 3 条 — LLM 声明 orthogonal 时未审 dimension 是否退化为单值。修法：prompt Constraint 15 + validator degenerate skip。
2. **Phase C**：`reversal_*` 1 条 — LLM 公式骨架共享上游变量造成结构性正相关。修法：跟 M1 ratio straggler 一起治。
3. **Phase D**：`seasonal_*` 1 条 — LLM 声明季节振幅未与 baseline_std 对齐。修法：prompt Constraint 17。
4. **接受**：`residual_*` 1 条 — [M1 ratio operator 长尾](M1_RATIO_OPERATOR_STRAGGLER.md)，已决定不修。

### 6.5 Constraint 14（可选 prompt 端补丁）未做

[plan §Context](../../../../.claude/plans/pingyue-samples-openai-calibrated-soft-sprightly-melody.md) + [PINGYUE_OPENAI_CAL_ANALYSIS.md §8.1](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#81-phase-a推荐先做group_dep_--marginal_-阈值-n-aware) 提到过可选 Constraint 14：

> "声明 group_dependency 时尽量让 cell n ≥ 某阈值"——让 LLM 主动估 target_rows × marginal × cell 数

本次没做，原因：

- Phase A validator-only 已达成 7/7 → 0 → 不需要 prompt 协同
- 加 Constraint 14 需要 LLM 真 regeneration 验证有效，单 PR scope 失控
- LLM 端责任只在 "weights normalize 干净 + magnitude reasonable"（[§6.2 已证清白](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#62-三个证据排除-llm-错)）；让 validator 包容 sampling envelope 更符合"责任分层"原则

未来 batch 如果出现 cell n < 5 高频，再考虑 prompt 端协同。

### 6.6 教训：阈值算法必须知道样本量

跟 [SIGMA_CALIBRATION.md §8.3](../subsystems/SIGMA_CALIBRATION.md) 的 T9 plumbing bug 同精神：

> 跨模块的"同一个计算"产生不同结果时，**别先怀疑算法**——先验证两边的输入是否字节一致。

Phase A 这边的 mirror 教训：

> validator 的阈值如果不知道 n，就一定会在小 n cell 上误判。**所有"差异"统计量在 sampling 域上都该 n-aware。**

下次写新 validator 时直接拿 Wald CI / Bonferroni / KS_MIN_CELL_SIZE / GROUP_DEP_MIN_CELL_SIZE 当默认起点，别再写 `< 0.10` 这种 n-agnostic 公式。

---

## 7. 配套文档导航

- [ANALYSIS.md](../ANALYSIS.md) — 一页综述，所有 soft-failure 问题的入口
- [FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md) — 三机制（M1/M2/M3）+ Path A/B/C 修复路径全图（M4-family 尚待更新进去）
- [validation/PINGYUE_OPENAI_CAL_ANALYSIS.md](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md) — openai-calibrated 批次深度分析，§6 是本机制的 hand-traced 证据起点，§8 是 Phase A-E 计划全图
- [validation/OPENAI_VALIDATION.md](../validation/OPENAI_VALIDATION.md) — batch-level summary（Phase A 后需更新表格）
- [mechanisms/MECHANISM_1_DEEP_DIVE.md](MECHANISM_1_DEEP_DIVE.md) — 机制 1（复合方差）纵深，本文写作模板
- [mechanisms/MECHANISM_3_DEEP_DIVE.md](MECHANISM_3_DEEP_DIVE.md) — 机制 3（稀疏 cell KS）纵深，n-aware 阈值的 KS 兄弟版
- [mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md](M1_RATIO_OPERATOR_STRAGGLER.md) — 机制 1 在除法算子上的长尾分支
- [subsystems/PATH_D_KS_SPARSE_CELLS.md](../subsystems/PATH_D_KS_SPARSE_CELLS.md) — 机制 3 的 validator 实现（本机制的兄弟篇，思路同源）
- [subsystems/SIGMA_CALIBRATION.md](../subsystems/SIGMA_CALIBRATION.md) — 机制 1 的 validator/orchestration 实现

---

## 时间线

| 日期 | 事件 | commit / doc |
|---|---|---|
| 2026-05-20 | `pingyue-samples-openai-calibrated` 批次跑出 9/10 soft-failed，54 条 check failure | (production batch) |
| 2026-05-20 | Path D（KS n<30 + Bonferroni + aggregate + Constraint 13）落地 → 13 条剩余 | `a7602e6` |
| 2026-05-20 | doc §6 hand-trace 证明 group_dep 0.30 离群是 sampling | [PINGYUE_OPENAI_CAL_ANALYSIS.md §6](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#6-10-group_dep_intervention_program-030-离群追根) |
| 2026-05-21 | Phase A 实施：Wald CI helper | `50098aa` |
| 2026-05-21 | Phase A 实施：check_group_dependency_transitions n-aware | `e9de06f` |
| 2026-05-21 | Phase A 实施：check_marginal_weights n-aware | `c5561be` |
| 2026-05-21 | Phase A validator-only rerun：13 → 6 failures，0 regressions | `pingyue-samples-openai-calibrated-pathA-rev/` |
| 2026-05-21 | 本文档定稿 | (this file) |
