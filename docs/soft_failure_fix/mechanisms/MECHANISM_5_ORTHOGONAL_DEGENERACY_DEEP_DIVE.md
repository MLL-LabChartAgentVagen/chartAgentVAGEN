# 机制 5（正交声明在退化列上误判）深度剖析：根因 → 算法 → 实测

> 配套阅读：[ANALYSIS.md](../ANALYSIS.md) 是一页综述；
> [validation/PINGYUE_OPENAI_CAL_ANALYSIS.md §4.2 + §8.2](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#42-三个高质量信号)
> 给出 3 条 `orthogonal_*` 失败的原始分布与 Phase B/prompt-Constraint-15 修复路径。本文是 Phase B 的纵深：
> 把"为什么 declare_orthogonal 在采样后会落到 1×N / N×1 / 1×1 contingency
> table → chi² 数学上判不了 → 我们怎么用 `ORTHOGONAL_MIN_DIM` skip 替换 →
> pingyue-samples-openai-calibrated 上的真实失败和修复后的实测"串成一条线。
>
> 数据来自两个 declarations 一致的批次（同 10 scenario · openai · seed=42
> · Path A + Loop A calibration + Path D + Phase A 全开）：
> - `output/agpds/pingyue-samples-openai-calibrated-pathA-rev` — Phase A 已上线，**正交退化仍 hard-fail**
> - `output/agpds/pingyue-samples-openai-calibrated-pathB-rev` — **Phase B 已上线**（degenerate skip）
>
> 两批同 declarations、同 seed=42（Loop B 内有 stochastic noise，**行数 + scenario ID 一致**，validator 行为差异完全可归因）。

---

## 1. 一页总结

| 维度 | Phase A 基线 | **Phase B** |
|---|:-:|:-:|
| passed | 6/10 | **8/10** ✓ |
| total failures | 6 | **3** (-50%) |
| `orthogonal_*` count | 3 | **0** ✓ |
| `residual_*` count | 1 | 1（M1 ratio 长尾，已接受）|
| `reversal_*` count | 1 | 1（Phase C 范围）|
| `seasonal_*` count | 1 | 1（Phase D 范围）|
| 新单测 | — | **+8**（5 degenerate-skip · 2 chi² unchanged · 1 constant）|
| 既有单测调整 | — | **1**（`test_degenerate_contingency_table` flipped）|
| 回归 | — | **0** |

**Headline**：Phase B 把 `orthogonal_*` 失败族**全部**关闭，并把
[`agpds_33d84d2c9b`](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#32-agpds_33d84d2c9b--uc-berkeley-招生)
与 [`agpds_8180fe4e2c`](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#37-agpds_8180fe4e2c--密歇根大学招生)
从 fail 翻成 PASS——它们各自只剩的 1 条失败是正交退化误判。剩 3 条 failure
（1 residual + 1 reversal + 1 seasonal）全部归属其他机制范畴，无一为正交退化。

---

## 2. 根本原因：declare_orthogonal × 上游采样的级联

### 2.1 LLM 让 SDK 声明跨维独立

LLM 在 `FactTableSimulator` SDK 里这样写：

```python
sim.add_category("campus", values=["Berkeley", "Davis", "Irvine", ...])
sim.add_category("academic_quarter", values=["Q1", "Q2", "Q3", "Q4"])

sim.declare_orthogonal("campus", "academic_quarter")
# 含义：随机抽到任一 (campus, quarter) 组合的概率 = P(campus) × P(quarter)
```

LLM 把它读成"这两个维度在数据生成时彼此独立"。Validator 负责的事是数据生成
完成后，**用 χ² 检验 contingency table 是否还能拒绝独立假设** —— 如果不能
（p > 0.05），那 LLM 写的 orthogonality 站得住脚。

### 2.2 引擎按声明采样，但单个维度可能塌缩

引擎按各列声明采样。若 scenario 把 campus 限定为单值（"University of
California, Berkeley"，3 条失败的 [`agpds_33d84d2c9b`](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#32-agpds_33d84d2c9b--uc-berkeley-招生)
是 single-campus scenario），或上游 group_dependency 让 `university` 在
某 segment 下退化（[`agpds_8180fe4e2c`](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#37-agpds_8180fe4e2c--密歇根大学招生)
是 single-university），最终 master_table 的 `pd.crosstab(root_a, root_b)`
就成了 1×N / N×1 / 1×1。

### 2.3 数学：chi² 在 min(shape)<2 时数学上不可用

chi² test 的 degrees of freedom：

$$\mathrm{dof} = (r-1)(c-1)$$

当 `r=1` 或 `c=1` 时 `dof=0`，chi² 统计量没有可比的分布——p-value 在多数
SciPy 实现里要么 NaN、要么 0（取决于内部 fall-back）。把 1×N table 喂给
[`scipy.stats.chi2_contingency`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html)
拿到的 p 值**不是**"是否独立"的合理量度，因为这个问题在退化 marginal 下
没意义——其中一个变量是常数，谈不上"它跟另一个变量有没有关联"。

### 2.4 Validator 原行为 = hard-fail 退化表

[Phase B 之前的 `check_orthogonal_independence`](../../../pipeline/phase_2/validation/structural.py#L161-L172)：

```python
if ct.shape[0] < 2 or ct.shape[1] < 2:
    checks.append(Check(
        name=f"orthogonal_{root_a}_{root_b}",
        passed=False,
        detail=f"Degenerate contingency table shape={ct.shape}; chi-squared requires at least 2×2.",
    ))
    continue
```

意图是好的：识别 chi² 数学上跑不动的情况、不让 SciPy 抛 ValueError。但行
为是 hard-fail——validator 把"我没办法判定 orthogonality"翻译成了"orthogonality
不成立"。在 pingyue-samples-openai-calibrated 这种 single-campus / single-
university scenario 里，LLM 写的 `declare_orthogonal(campus, year)` **不是
错的**：scenario 本身就让 campus 是单值，independence 在退化空间里既不能
被证伪也不能被证实。但 validator 一刀切判负。

### 2.5 3 条失败全是这个机制

[PINGYUE_OPENAI_CAL_ANALYSIS.md §4.2](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#42-三个高质量信号) 已经诊断：

> "M4-orthogonal 全 3 条都是'dimension group 退化为单值'：agpds_33d84d2c9b
> campus×year 1×1；agpds_503613ba96 campus×quarter 1×4；agpds_8180fe4e2c
> year×university 3×1。属 M2 (joint-distribution blind spot) 在
> column-declaration 层的同源问题。"

所以 3 条失败**全部**归到本机制，validator 把统计学不可判定误读成
LLM 错——本质和 Phase A 的小样本比例漂移误判同精神（"validator 不了解
sample geometry，会在数学上没 power 的 regime 上误判"）。

---

## 3. 实际失败案例：Phase A 基线的真实失败

下面是 `pingyue-samples-openai-calibrated-pathA-rev/validation_summary.json`
里全部 3 条 `orthogonal_*` 失败的 hand-traced 数据：

| Scenario | Check | offending shape | 退化原因 | 原 detail |
|---|---|:-:|---|---|
| `agpds_33d84d2c9b` | `orthogonal_campus_year` | **(1, 1)** | scenario 限定 single campus + single year | `Degenerate contingency table shape=(1, 1); chi-squared requires at least 2×2.` |
| `agpds_503613ba96` | `orthogonal_campus_academic_quarter` | **(1, 4)** | scenario 限定 single campus（UC Berkeley）| `Degenerate contingency table shape=(1, 4); chi-squared requires at least 2×2.` |
| `agpds_8180fe4e2c` | `orthogonal_year_university` | **(3, 1)** | scenario 是单一 University of Michigan | `Degenerate contingency table shape=(3, 1); chi-squared requires at least 2×2.` |

### 3.1 Case study：`agpds_33d84d2c9b::orthogonal_campus_year`

scenario `agpds_33d84d2c9b` 是 UC Berkeley 招生 funnel：scenario metadata
限定 `campus="University of California, Berkeley"`（单值），year 列在
采样中也塌缩为单值（某些 cell 只跑了一年）。两个 root 都退化到 1 → chi²
的 `dof = (1-1)(1-1) = 0` → 数学上判不了。

旧逻辑判 fail；但 LLM 写 `declare_orthogonal(campus, year)` 时并没有错：
single-campus scenario 不需要 across-campus orthogonality；single-year cell
里 year 也谈不上 across-year 关联。这条声明在原始空间里是 vacuously true。

### 3.2 为什么 prompt 端 Constraint 15 救不了

[PINGYUE §8.2](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#82-phase-b-orthogonal_-)
列了 prompt-端选项：让 LLM "声明 `declare_orthogonal(A, B)` 前确认 A 和 B
在 scenario 采样后都至少有 2 个 unique 值"。问题是：

- LLM **不知道** scenario 采样后会出什么 shape——target_rows、marginal、上游
  group_dependency 的级联会让 cell n 不可预测
- 单 campus / 单 university 的 scenario 在 [Phase 0 / Phase 1 阶段](../../../pipeline/phase_1)
  就被 cached 下来了，LLM 在 Phase 2 写 declarations 时已经无法改 scenario 限
  定
- 因此 LLM 仍可能"诚实地"声明 `declare_orthogonal(campus, year)` 而后采样
  退化——这是 scenario shape 决定的，不是 LLM declaration 错误

**结论**：必须在 validator 侧解决，prompt 端不充分。

---

## 4. 解决方案：strict min(shape)<2 skip

### 4.1 一句话

> 把 hard-fail 替换为 `passed=True` + `detail = "skipped (degenerate shape=(R,C); chi² requires >=2x2)"`，threshold = `ORTHOGONAL_MIN_DIM = 2`。chi² 数学跑不动的 regime 主动让出判定权，shape 信息保留给 postmortem。

### 4.2 为什么 strict literal 而不是 textbook expected_count<5

| 候选 | 范围 | Phase B 选用 |
|---|---|:-:|
| **strict `min(shape) < 2`** | 只 skip chi² 数学上 dof=0 的情况 | ✓ |
| **textbook `min(expected) < 5`** | 还 skip 期望计数太低的 2×2 表（chi² 教科书 validity rule）| ✗（暂留）|

理由：
1. **实测覆盖**：3 条 pingyue 失败全部是 min(shape)<2 命中，没有 ≥2×2 但
   expected_count<5 的边界 case。strict 已经够清掉 3/3。
2. **mirror Phase A 保守取舍**：Phase A 选 `n<10` 而不是 `n<30`，理由是更
   严格的阈值会 silent-pass 更多 cell，违反 transparency；同精神在
   orthogonal 这里就是只 skip 数学上完全没意义的 dof=0 case。
3. **可拓展点**：常量 `ORTHOGONAL_MIN_DIM` 是单点替换；将来如果出现 ≥2×2
   但 cell 期望 <5 的 false-positive case，可以加 expected-count 二阶判定。
4. **Constraint 15（可选 prompt 补丁）暂留**：[plan §Context 决策表](../../../../.claude/plans/pingyue-samples-openai-calibrated-soft-declarative-mountain.md)
   说明：Phase B validator-only 已达成 3/3 → 0；加 Constraint 15 需要 LLM
   regeneration 验证，单 PR scope 失控。Phase A 同精神（[MECHANISM_4 §6.5](MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md#65-constraint-14可选-prompt-端补丁未做)）。

### 4.3 算法流程

```
check_orthogonal_independence(df, meta):

for each declared (group_a, group_b) in meta.orthogonal_groups:

  root_a = group_a.hierarchy[0]
  root_b = group_b.hierarchy[0]
  ct = pd.crosstab(df[root_a], df[root_b])

  if min(ct.shape) < ORTHOGONAL_MIN_DIM:
    yield Check(
      name=f"orthogonal_{root_a}_{root_b}",
      passed=True,                          # ← Phase B：fail → skip-pass
      detail=f"skipped (degenerate shape={ct.shape}; chi² requires >=2x2)",
    )
    continue

  # 正常 chi² 路径 (≥2×2) 完全未动
  _, p_val, _, _ = scipy.stats.chi2_contingency(ct)
  yield Check(
    name=f"orthogonal_{root_a}_{root_b}",
    passed=bool(p_val > 0.05),
    detail=f"χ² p={p_val:.4f} (>0.05 = independent)",
  )
```

### 4.4 关键设计决策

| 决策 | 选择 | 理由 |
|---|---|---|
| 阈值类型 | **strict `min(shape) < ORTHOGONAL_MIN_DIM=2`** | 详 §4.2，conservative + mirror Phase A `n<10` 精神 |
| Skip 表达 | **`passed=True` + detail 标注** | 与 Phase A `skipped_cells=N (n<10)` 同 vocab；postmortem 仍能从 detail 找到 shape |
| LLM-only vs Validator-only | **validator-only** | LLM 不能预测采样退化（§3.2 已证）；Constraint 15 暂留 |
| `check_orthogonal_independence` 函数其它分支 | **不动** | `min(shape) ≥ 2` 路径走原 chi²，单测锁 |
| `ORTHOGONAL_MIN_DIM` 位置 | **`structural.py` module top** | 与 `GROUP_DEP_*` 常量摆同高度，单点替换 |
| 既有测试 `test_degenerate_contingency_table` | **flip assertion** | 行为变更必须有测试反映；docstring 注明 Phase B 改造 |

### 4.5 代码位点

| 文件 | 行 | 内容 |
|---|---|---|
| [validation/structural.py:27-33](../../../pipeline/phase_2/validation/structural.py#L27-L33) | new | `ORTHOGONAL_MIN_DIM = 2` 常量 + 注释 |
| [validation/structural.py:160-172](../../../pipeline/phase_2/validation/structural.py#L160-L172) | flipped | `check_orthogonal_independence` 的 degenerate 分支从 `passed=False` 改为 `passed=True` + 新 detail string |
| [tests/modular/test_validation_phase_b.py](../../../pipeline/phase_2/tests/modular/test_validation_phase_b.py) | new | 8 测试：3 退化形状 / 2 detail 内容 / 2 chi² 路径不变 / 1 常量 |
| [tests/modular/test_validation_structural.py:129-149](../../../pipeline/phase_2/tests/modular/test_validation_structural.py#L129-L149) | flipped | `test_degenerate_contingency_table_soft_passes`（原 `test_degenerate_contingency_table`）现锁 `passed=True` + skipped detail |

### 4.6 Detail string 的实际样子

**Before（Phase A 时代）**：

```
Degenerate contingency table shape=(1, 4); chi-squared requires at least 2×2.
```

postmortem 读到：这是 fail。需要进一步 jq + master_table 才知道是不是
LLM 真错。

**After（Phase B 跳过）**：

```
skipped (degenerate shape=(1, 4); chi² requires >=2x2)
```

postmortem 读到：validator 主动跳过、退化 shape 已记录、可以直接判断
"原因是 scenario shape，不是 LLM 错"。

---

## 5. 修复后效果：Phase B rerun 实测

### 5.1 Per-scenario 失败明细

| Scenario | Phase A (before) | **Phase B** (after) | Δ |
|---|---|---|---|
| `agpds_14b7f7487e` | 1 fail: `seasonal_checkout_count` | 1 fail: `seasonal_checkout_count` | 0 |
| `agpds_33d84d2c9b` | 1 fail: `orthogonal_campus_year` | **✓ PASS (0)** | **-1** ✓ |
| `agpds_3af92040e6` | ✓ PASS (0) | ✓ PASS (0) | 0 |
| `agpds_503613ba96` | 3 fails (residual + reversal + orthogonal) | **2 fails** (residual + reversal) | **-1** |
| `agpds_65ef0afda0` | ✓ PASS (0) | ✓ PASS (0) | 0 |
| `agpds_8022981cf7` | ✓ PASS (0) | ✓ PASS (0) | 0 |
| `agpds_8180fe4e2c` | 1 fail: `orthogonal_year_university` | **✓ PASS (0)** | **-1** ✓ |
| `agpds_985a1b72e1` | ✓ PASS (0) | ✓ PASS (0) | 0 |
| `agpds_d62b18e180` | ✓ PASS (0) | ✓ PASS (0) | 0 |
| `agpds_e9c40d0352` | ✓ PASS (0) | ✓ PASS (0) | 0 |

**正交退化失败：3 → 0（100% 关闭）**
**passed scenario 数：6/10 → 8/10**
**regressions：0**（6 个原 passing scenario 全部保持 passing）

### 5.2 同 declarations + 同 seed → 同行数 + 同 scenario 对齐

这是 validator-only 改造的关键证据。Phase B 在 `output/agpds/pingyue-
samples-openai-calibrated-pathB-rev` rerun 与 pathA-rev：

- declarations 同源（都从 `output/agpds/pingyue-samples-openai-calibrated/declarations/` 读出）
- 行数一致：`agpds_33d84d2c9b` 720 rows、`agpds_503613ba96` 720 rows、
  `agpds_8180fe4e2c` 240 rows，跨两批完全一致
- scenario IDs 完全对齐
- validator-side 仅改了 `check_orthogonal_independence` 的 degenerate 分支

可用以下命令验证：

```bash
# 行数对齐
for f in agpds_33d84d2c9b agpds_503613ba96 agpds_8180fe4e2c; do
  a=$(wc -l < output/agpds/pingyue-samples-openai-calibrated-pathA-rev/master_tables/$f.csv)
  b=$(wc -l < output/agpds/pingyue-samples-openai-calibrated-pathB-rev/master_tables/$f.csv)
  echo "$f: A=$a, B=$b, equal=$([ "$a" = "$b" ] && echo yes || echo no)"
done
# 期望: 全部 equal=yes

# scenario IDs 对齐
diff <(jq -r '.[].generation_id' output/agpds/pingyue-samples-openai-calibrated-pathA-rev/validation_summary.json | sort) \
     <(jq -r '.[].generation_id' output/agpds/pingyue-samples-openai-calibrated-pathB-rev/validation_summary.json | sort)
# 期望: 无输出
```

> **注意 Loop B 非完全 bit-determinstic**：Phase A doc
> [MECHANISM_4 §5.2](MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md#52-llm-完全没改任何东西)
> 声称 master_table "字节一致"——实测当前 pipeline 下，Loop B re-execution
> 在同 seed 下会有 stochastic noise（cell-level value 不一致、但 row count
> 与失败族归属保持一致）。这不影响 Phase B "validator-only" 的本质：本次未触
> 任何数据生成代码，validator 行为差异是 deviation 的唯一原因。

### 5.3 3 条原失败的 Phase B 处理表

| Check | shape | Phase A detail | **Phase B detail** | passed? |
|---|---|---|---|:--:|
| `orthogonal_campus_year` (33d8...) | (1, 1) | `Degenerate contingency table...` | `skipped (degenerate shape=(1, 1); chi² requires >=2x2)` | ✓ |
| `orthogonal_campus_academic_quarter` (5036...) | (1, 4) | `Degenerate contingency table...` | `skipped (degenerate shape=(1, 4); chi² requires >=2x2)` | ✓ |
| `orthogonal_year_university` (8180...) | (3, 1) | `Degenerate contingency table...` | `skipped (degenerate shape=(3, 1); chi² requires >=2x2)` | ✓ |

3/3 在 Phase B 下从 hard-fail 翻为 skip-pass。chi² 路径完全未跑（因为 dof=0
本来也跑不动），shape 信息保留在 detail 里。

### 5.4 失败类型从"假阳性"转成"真问题"

| 失败族 | Phase A 基线 | Phase B | 责任层 |
|---|:-:|:-:|---|
| `orthogonal_*`（退化误判） | 3 | **0** ✓ | validator threshold（本机制） |
| `residual_*` | 1 | 1 | LLM ratio operator 长尾（[M1 straggler](M1_RATIO_OPERATOR_STRAGGLER.md)，已接受）|
| `reversal_*` | 1 | 1 | LLM 公式骨架 sign/中介错（**Phase C 范围**）|
| `seasonal_*` | 1 | 1 | LLM 季节振幅 vs baseline_std（**Phase D 范围**）|

剩 3 条 failure 全部是**真问题**——LLM 行为缺陷，需要 prompt 端 / 公式端
介入。Phase B 把 validator 假阳性彻底清掉，让下游 Phase C/D 不再被假信号
污染。

### 5.5 agpds_503613ba96 detail diff（一手证据）

Phase A rerun，`agpds_503613ba96` 的 3 条 failure：

```
residual_student_faculty_ratio        passed=False  noise_sigma=4.4300, residual_std=7.8358, ratio=0.7688 (>= 0.2)
reversal_course_load_student_faculty_ratio  passed=False  rank_corr=+0.29 (期望 <0)
orthogonal_campus_academic_quarter    passed=False  Degenerate contingency table shape=(1, 4); ...
```

Phase B rerun，同 scenario：

```
residual_student_faculty_ratio        passed=False  (unchanged — M1 长尾，已接受)
reversal_course_load_student_faculty_ratio  passed=False  (unchanged — Phase C 范围)
orthogonal_campus_academic_quarter    passed=True   skipped (degenerate shape=(1, 4); chi² requires >=2x2)
```

只有正交退化分支 flip 到 PASS；其它 2 条非 Phase B 范畴 failure 保持 fail。
scenario `all_passed=False` (3 → 2)。

---

## 6. 进一步阅读 / 已知坑

### 6.1 ≥2×2 但 expected_count < 5 的灰区暂未处理

Phase B 只 skip dof=0 的退化表。如果 contingency table 是 2×2 但某 cell
expected count = 1（典型 case：稀有 outcome × 稀有 predictor），chi² 教
科书 validity 失效。Phase B 不动这种 case 因为：

- 实测：pingyue-samples-openai-calibrated 的 3 条 orthogonal 失败全部
  min(shape)<2 命中，没有 borderline ≥2×2 expected<5 的 case
- 增加 expected-count 判定会让 detail 更复杂、且 scipy 已经在某些边界
  warning（不抛错）
- 若未来出现：再扩 `_orthogonal_thresholds` 即可，单点替换

未来触发条件：production batch 出现 `orthogonal_*` 失败的 contingency
shape 为 2×2 / 2×N（≥2×2 但稀疏），手 trace 显示 LLM declaration 正确
但 chi² p 值不稳。

### 6.2 Constraint 15（可选 prompt 端补丁）暂未做

跟 Phase A 的 Constraint 14 同精神（[MECHANISM_4 §6.5](MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md#65-constraint-14可选-prompt-端补丁未做)）：
让 LLM 在声明 `declare_orthogonal(A, B)` 前确认 A、B 在 scenario 采样
后都有 ≥2 unique values。本次没做，原因：

- Phase B validator-only 已达成 3/3 → 0 → 不需要 prompt 协同
- LLM 在 Phase 2 阶段看不到下游 sampling 结果——scenario 单值限定 + 上游
  group_dep 级联决定 unique-value count，LLM 无法预测
- 加 Constraint 15 需要 LLM regeneration 验证，单 PR scope 失控

未来触发条件：production batch 出现 `orthogonal_*` 失败率 > 20% 且
mechanism 仍是退化（不是 LLM 真的写错独立性）；说明 LLM 系统性在
single-value scenario 上滥发 `declare_orthogonal`，可在 prompt 端拦下。

### 6.3 silent-pass + transparency

跟 [Path D KS_MIN_CELL_SIZE=30](../subsystems/PATH_D_KS_SPARSE_CELLS.md#21-关键设计决策) 与
[Phase A GROUP_DEP_MIN_CELL_SIZE=10](MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md#43-算法流程) 同精神：

- skip 是 silent-pass，validator 不评判该 orthogonal 声明对错
- 但 detail string 保留 shape (e.g., `(1, 4)`)，让 postmortem 读者一眼
  看到原因
- 比 fail 更诚实：在统计学没 power 的 regime 上 fail 会污染下游分析
  对"validator 假阳性 vs 真 LLM 错"的判断

### 6.4 Loop B 非完全 bit-deterministic 是本次的发现

Phase A doc 声称 master_tables "字节一致"，本次 Phase B 实测发现 Loop B
re-execution 在同 seed 下会产生 cell-value 级别的 stochastic noise（行数、
scenario IDs 一致）。可能原因：

- 多线程 worker 执行顺序非确定（`--workers 4`）
- numpy / scipy default_rng 与全局状态的 fall-back 路径在不同环境略有
  差异
- SDK 内 `add_measure_structural` 或 `inject_pattern` 中存在未完全
  seed-fed 的 stochastic 步骤

Phase B 的 validator-only 本质不受影响——因为：
- 行数对齐 + scenario IDs 对齐 → 同一 scenario 在两批跑出"统计意义上
  同一份数据"
- 失败族归属与计数对齐 → 没有数据生成层逻辑变化
- 触动代码仅在 `structural.py` validator 内

**未来：**Phase 2 的 reproducibility audit 应当成为独立 plan——跨 batch
比较 master_table 应该是 row-by-row 等价，不应有 cell-value drift。如果
出现，那是另一个机制。

### 6.5 仍未修

Phase B 已经关闭正交退化机制。Phase A 后 6 条 → Phase B 后 3 条，剩 3 条
按 [PINGYUE_OPENAI_CAL_ANALYSIS.md §8](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#8-下一步修改计划) 分发：

1. **Phase C**：`reversal_*` 1 条（agpds_503613ba96）— LLM 公式骨架共享上
   游变量造成结构性正相关。修法：跟 M1 ratio straggler 一起治。
2. **Phase D**：`seasonal_*` 1 条（agpds_14b7f7487e）— LLM 声明季节振幅
   未与 baseline_std 对齐。修法：prompt Constraint 17。
3. **接受**：`residual_*` 1 条（agpds_503613ba96）— [M1 ratio operator 长
   尾](M1_RATIO_OPERATOR_STRAGGLER.md)，已决定不修。

### 6.6 教训：数学上没 power 的 regime 一定要主动让出判定权

跟 [Phase A §6.6 教训](MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md#66-教训阈值算法必须知道样本量)
同精神：

> validator 的阈值如果不知道 sample geometry，就一定会在数学上没意义的
> regime 上误判。

Phase B 这边的 mirror 教训：

> chi² test 的 dof=0 是数学上 hard-zero，不是"差点能跑就当跑了"。**所有
> requires-≥2 假设的统计量在低于阈值时都该 silent-pass**，不要把
> "无法判定"翻译成"判定为否"。

下次写新 validator 时直接拿 `min(shape) ≥ 2`、`Bonferroni K`、
`KS_MIN_CELL_SIZE`、`GROUP_DEP_MIN_CELL_SIZE`、`ORTHOGONAL_MIN_DIM` 当默认
起点，别再用 hard-fail 兜底"unsupported regime"。

---

## 7. 配套文档导航

- [ANALYSIS.md](../ANALYSIS.md) — 一页综述，所有 soft-failure 问题的入口
- [FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md) — 三机制（M1/M2/M3）+ Path A/B/C 修复路径全图（M4/M5 尚待 backport）
- [validation/PINGYUE_OPENAI_CAL_ANALYSIS.md](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md) — openai-calibrated 批次深度分析，§4.2 是本机制的发现起点，§8.2 是 Phase B 计划
- [mechanisms/MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md](MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md) — Phase A（小样本比例漂移）纵深，本文写作模板
- [mechanisms/MECHANISM_1_DEEP_DIVE.md](MECHANISM_1_DEEP_DIVE.md) — 机制 1（复合方差）纵深
- [mechanisms/MECHANISM_3_DEEP_DIVE.md](MECHANISM_3_DEEP_DIVE.md) — 机制 3（稀疏 cell KS）纵深，n-aware 阈值的 KS 兄弟版
- [mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md](M1_RATIO_OPERATOR_STRAGGLER.md) — 机制 1 在除法算子上的长尾分支
- [subsystems/PATH_D_KS_SPARSE_CELLS.md](../subsystems/PATH_D_KS_SPARSE_CELLS.md) — 机制 3 的 validator 实现（本机制的兄弟篇，思路同源）
- [subsystems/SIGMA_CALIBRATION.md](../subsystems/SIGMA_CALIBRATION.md) — 机制 1 的 validator/orchestration 实现

---

## 时间线

| 日期 | 事件 | commit / doc |
|---|---|---|
| 2026-05-20 | `pingyue-samples-openai-calibrated` 批次跑出 9/10 soft-failed，3 条 orthogonal_* 在内 | (production batch) |
| 2026-05-21 | Phase A 实施完成 → 6/10 passing，3 orthogonal_* 残留 | `c5561be` `e9de06f` `50098aa` |
| 2026-05-21 | doc §4.2 诊断 orthogonal 全 3 条是退化 contingency table | [PINGYUE_OPENAI_CAL_ANALYSIS.md §4.2](../validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#42-三个高质量信号) |
| 2026-05-21 | Phase B 实施：`ORTHOGONAL_MIN_DIM` + degenerate skip | (this commit) |
| 2026-05-21 | Phase B validator-only rerun：6 → 3 failures，0 regressions，8/10 passing | `pingyue-samples-openai-calibrated-pathB-rev/` |
| 2026-05-21 | 本文档定稿 | (this file) |
