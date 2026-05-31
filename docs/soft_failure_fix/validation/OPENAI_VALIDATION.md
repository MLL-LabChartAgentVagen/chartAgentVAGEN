# OpenAI End-to-End Validation (gpt-5.5)

> 配套 [SIGMA_CALIBRATION.md §7.4](../archive/SIGMA_CALIBRATION.md#74-openai-端到端验证-path-bc-缺口)
> 留的缺口：Path B/C 的 typed-error 反馈环路在 gemini 上没触发过，需要
> 在原始 production model openai/gpt-5.5 上重跑一遍验证。
>
> 本文档：2026-05-20 跑的 `pingyue-samples-openai-calibrated` 批次结果 +
> 关键发现。

---

## 1. TL;DR

| 指标 | v1 (openai, no fix) | **openai-calibrated** | gemini-cal（对照） |
|---|---:|---:|---:|
| passed | 0/10 | **1/10** | 4/10 |
| total failures | 114 | **54** (-53%) | 18 |
| errored | **2** | **0** ✓ | 0 |
| residual_* count | 15 | **1** (-93%) | 0 |
| residual median ratio | 1.54 | **0.77** | N/A |
| ks_* count | 95 | **39** (-59%) | 11 |
| calibration_unconverged | n/a | **0** | 0 |

**结论**：openai 上**机制 1 基本关闭**（residual 15→1，median ratio 1.54→0.77），
**Path B/C 没在 production 上触发**——但**这是好事**：Path A 约束 12 把
**导致** B/C 触发的 LLM 行为（None 作为类别值、不可行 pattern target）拦在
源头了。Defense in depth 工作正常。

**Path D 验证后续追加（commit `a7602e6`）**：表中 `ks_* 39` 是 Path D
**未应用前**的数字。Path D 在此批 validator-only rerun 中将 `ks_*` 闭合到 0、
passed 提升到 5/10、total failures 降到 13——详 [§7](#7-path-d-实测验证validator-only-rerun-commit-a7602e6)。
此时 openai-cal 上**机制 1 + 机制 3 双关闭**（除 1 条 [ratio-operator
长尾](../mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md)）。

---

## 2. 关键发现：Path B/C 没机会跑

### 2.1 证据

```bash
grep -E "PatternInjectionError|UndefinedEffectError|matched zero|no definition for" \
    /tmp/openai_stage1.log
# (空输出)
```

整个 Stage 1 跑中：
- **0 次** `PatternInjectionError`（Path B 的触发目标）
- **0 次** `UndefinedEffectError`（Path C 的触发目标）
- **0 次** 任何 typed engine exception 进入 Loop A 反馈

### 2.2 为什么没触发：Path A 约束 12 在源头拦住

[orchestration/prompt.py:103-118](../../../pipeline/phase_2/orchestration/prompt.py#L103-L118)
的 HARD CONSTRAINT 12 明确禁止：

> **永远不要**把 Python `None` 或字符串 `"None"` 用作类别值、`parent=`
> 引用、`add_group_dependency` 的 parent/child、effect-map 的 key、或
> pattern `target` 滤波器。

v1 (openai, no fix) 时：
- `agpds_3af92040e6`：LLM 写了 `target="campus == 'UC Berkeley' & race_ethnicity == 'Native American/Alaska Native'"` → 0 行匹配 → `PatternInjectionError`
- `agpds_8180fe4e2c`：`major` 列出现 `None`（条件分布不归一化）→ effect map 查 `None` → `KeyError: 'None'`

openai-calibrated（同 10 scenario，加 Path A 约束）：
- 同样 2 个 gen_id，**都没触发**那两个 bug
- LLM 看到 prompt 里 "Never use Python None ... as effect-map key" 后避开了条件分布触发 None 的写法
- 同样避开了写"罕见 AND 值组合"作 pattern target

### 2.3 含义

| 层 | 在 openai-calibrated 上的实际触发 |
|---|---|
| **Path A**（prompt 约束）| ✓ 实际触发——LLM 写出来的 declarations 不含 None / 0-row pattern |
| **Path B**（PatternInjectionError 详化）| ✗ 没触发——LLM 没写出 0-row pattern |
| **Path C**（UndefinedEffectError 替换 KeyError）| ✗ 没触发——LLM 没写出会漏 effect key 的代码 |
| **Calibration**（in-loop sigma 校准）| ✓ 触发：10 个 scenario 各 1 次 check，其中 `dom_027/k=4` 多 1 次 retry |

**Path B/C 仍然没在 production 上**实际地**做"Loop A 拿 typed feedback 后自修"的端到端
验证**——因为它们的触发条件（错误的 LLM 输出）被 Path A 提前消除了。

---

## 3. 校准（mechanism 1）：openai 上效果

### 3.1 触发率

| scenario | calibration_attempt 次数 |
|---|:-:|
| dom_021/k=3 | 1 |
| dom_022/k=1 | 1 |
| dom_023/k=0 | 1 |
| **dom_024/k=1** | **1**（同 gemini-cal，那次需 3 轮的也是这个） |
| dom_025/k=2 | 1 |
| dom_026/k=5 | 1 |
| **dom_027/k=4** | **2**（openai 上特有，1 次 retry） |
| dom_028/k=7 | 1 |
| dom_029/k=7 | 1 |
| dom_030/k=2 | 1 |

**总计 11 次 check，1 次 retry**。所有 scenario 都 converge（0 calibration_unconverged）。

### 3.2 residual 几乎全清

| | v1 (openai, no fix) | openai-cal |
|---|---|---|
| residual count | 15 | **1** |
| residual ratio max | 66.46× | **0.77×**（刚过阈值 0.2） |
| residual ratio median | 1.54 | **0.77**（only 1 sample） |

剩下的 1 个 residual 失败：`agpds_503613ba96` / `residual_student_faculty_ratio`
（`noise_sigma=4.43, residual_std=7.84, ratio=0.7688`），ratio 比 v1 的 29.6×
（同一 column）好两个数量级——但 empirical 比 declared 大 77%，还差一脚
踩进阈值 0.2 之内。

**根因不在 calibration 算法本身，而在公式有除法算子** `enrollment / faculty`，
除法引入结构方差，不在 LLM 加性 noise sigma 声明范围内——calibration
把 sigma 调到 base 值 55% 后已经到 LLM 心目中的"sensible ceiling"。同
scenario 还有同列 reversal 失败说明公式骨架更基本的问题。详见
[M1_RATIO_OPERATOR_STRAGGLER.md](../mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md)。

---

## 4. openai-cal vs gemini-cal：交叉模型对比

| 指标 | openai-cal | gemini-cal | 解读 |
|---|---:|---:|---|
| passed | 1/10 | 4/10 | gemini 更紧凑写法，碰到稀疏 cell 的 ks 失败少 |
| residual count | 1 | 0 | openai 还差一脚 |
| ks count | 39 | 11 | **openai 更多稀疏 cell 失败** —— 机制 3 范畴 |
| group_dep_* | 7 | 1 | openai 写更复杂的 conditional dependency |
| orthogonal_* | 3 | 0 | openai 多 |
| outlier_* | 0 | 2 | gemini 写 inject_pattern("outlier_entity") 更频繁 |
| seasonal_* | 1 | 2 | 接近 |

**结论**：openai 跟 gemini 在**机制 1（residual）上**表现相当（calibration
让两个 model 都把 residual 干掉），但在**机制 3（ks 稀疏 cell）上**openai
更脆——它写更多分类列、更深 cell crossing。**机制 3 的修复（下一个 plan
的 Path D / bonferroni 校正）会主要让 openai 受益**——✅ 已验证：§7 中
openai-cal `ks_*` 从 39→0（杠杆是 gemini-cal 11→0 的 ~3.5 倍）。

---

## 5. errored 从 2 到 0：是 Path A 的功劳，不是 Path B/C

| gen_id | v1 状态 | openai-cal 状态 | 解释 |
|---|---|---|---|
| `agpds_3af92040e6` | errored (PatternInjectionError) | **soft-failed** (4 check failures) | LLM 重写时避开了 0-row pattern target；residual / orthogonal 类失败但能跑通 |
| `agpds_8180fe4e2c` | errored (KeyError: 'None') | **soft-failed** (2 check failures) | LLM 重写时避开了 None 作为类别值；只剩 2 个小失败 |

**这 2 个 scenario 的修复路径**：

```
v1 (no fix):
  LLM 写出 None 类别值或 0-row pattern → engine 抛 KeyError/PatternInjectionError
  → Loop A 没 typed feedback 能处理 → errored 出 SkipResult

openai-cal:
  Path A 约束 12 + 11 在 prompt 里 → LLM 第一轮就避开 None / 0-row
  → 干净通过 exec → 干净通过 calibration → 干净通过大部分 validator
  → soft-failed 只剩稀疏 cell 类失败
```

Path B/C 的代码完全没参与这次修复。它们是 fallback layer——如果 Path A
没拦住，B/C 会接管。本次跑里 Path A 单独就够。

---

## 6. skipped.jsonl 表现

```bash
ls -la output/agpds/pingyue-samples-openai-calibrated/skipped.jsonl
# (不存在 — 因为 0 个 SkipResult)
```

10 个 scenario 全部走完 Stage 1，0 个 `calibration_unconverged`，0 个
`exec_error`——所以 [SKIP_PERSISTENCE](../subsystems/SKIP_PERSISTENCE.md) wiring 没被
触发。等到第一个真的 unconverged 跑出来才能验证它端到端工作（同 Path B/C
的状态——代码 + 单测 ✓，production trigger 缺）。

---

## 7. Path D 实测验证（validator-only rerun, commit `a7602e6`）

> 配套：[PATH_D_KS_SPARSE_CELLS.md](../subsystems/PATH_D_KS_SPARSE_CELLS.md)（Path D 设计 + gemini V3 实测）。
> 本节是 §4 "Path D 会主要让 openai 受益"预测的兑现记录。

### 7.1 设置

输出目录：`output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation/`

```bash
cp -r output/agpds/pingyue-samples-openai-calibrated/declarations \
      output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation/
cp    output/agpds/pingyue-samples-openai-calibrated/manifest.jsonl \
      output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation/
PYTHONNOUSERSITE=1 PYTHONPATH=. python -m pipeline.agpds_execute \
    --input-dir  output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation \
    --output-dir output/agpds/pingyue-samples-openai-calibrated-pathD-revalidation \
    --workers 4
```

10 份 declarations bit-for-bit identical 复用基线，仅重跑
`run_loop_b_from_declarations`（无 LLM call）。Path D 修改已在 commit
`a7602e6` 进 master → validator 路径走 n<30 skip + Bonferroni α + aggregate
pass-rate。

### 7.2 数据

| 指标 | openai-cal (baseline) | **Path D rerun** | Delta |
|---|---:|---:|---|
| passed | 1/10 | **5/10** | **+4** ✓ |
| total failures | 54 | **13** | **-41 (-76%)** ✓✓ |
| `ks_*` count | 39 | **0** | **-39 (-100%)** ✓✓✓ |
| `residual_*` | 1 | 1 | 0（#4 ratio=0.7688，详 [M1_RATIO_OPERATOR_STRAGGLER.md](../mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md)）|
| `orthogonal_*` | 3 | 3 | 0 |
| `group_dep_*` | 7 | 6 | **-1**（边缘 0.1123 翻 pass，见 §7.3）|
| `reversal_*` | 2 | 1 | **-1**（边缘 +0.46 翻 pass，见 §7.3）|
| `seasonal_*` | 1 | 1 | 0 |
| `marginal_*` | 1 | 1 | 0 |
| regressions | — | **0** | ✓ |

新 pass 的 4 个 scenario：`agpds_3af92040e6`、`agpds_65ef0afda0`、
`agpds_985a1b72e1`、`agpds_d62b18e180`。原本 pass 的 `agpds_8022981cf7` 保持 pass。

与 gemini-cal V3（[PATH_D_KS_SPARSE_CELLS.md §3.2](../subsystems/PATH_D_KS_SPARSE_CELLS.md)）对照：

| 批次 | passed Δ | `ks_*` Δ |
|---|---|---|
| gemini-cal V3 | 4/10 → **5/10** (+1) | 11 → **0** (-100%) |
| **openai-cal** | 1/10 → **5/10** (+4) | 39 → **0** (-100%) |

openai 上 +4 / -39 的杠杆远大于 gemini 的 +1 / -11——印证 §4 中"openai
写更深 cell crossing → Path D 主要让 openai 受益"。

### 7.3 二阶效应：Path D 顺带保护边缘 check

预期 Path D 只闭合 `ks_*`，但实测有两条**边缘**非 KS 失败也翻成 pass：

| Scenario / Check | Baseline | Path D 后 |
|---|---|---|
| `agpds_3af92040e6 / group_dep_aid_program` | `max_dev=0.1123` (> 0.10) | **pass** (< 0.10) |
| `agpds_65ef0afda0 / reversal_grant_funding_citation_count` | `rank_corr=+0.46` (应 < 0) | **pass** (< 0) |

**根因**：基线时 Loop B 因 `ks_*` 大量失败触发 autofix（[validation/autofix.py](../../../pipeline/phase_2/validation/autofix.py)
的 `reshuffle_pair` / `widen_variance`），autofix 修改 df 列序时把这两条
边缘 check 推过线。Path D 下 `ks_*` 不再失败 → Loop B 不动 autofix →
原始（干净）df 保留 → 边缘通过。

**证据**：#4 `agpds_503613ba96` 的 residual 数字
（`noise_sigma=4.4300, residual_std=7.8358, ratio=0.7688`）在两批中
**一字不差**——这条 scenario 同时有 `ks_*` 失败和 residual 失败，但
autofix 不对 residual 操作，所以 df 仍 bit-identical。反过来证明 #3 / #5
的"翻 pass"不是采样波动，而是 Loop B 行为差异导致的有结构差异。

**含义**：Path D 不只直接闭合 `ks_*`，还**间接保护**了边缘 check 不被
Loop B 误触的 autofix 推过线——这是设计意图之外的额外收益。

### 7.4 剩 5 个 soft-fail scenario 全部 M4-family

| Scenario | 剩余失败 | 失败族 |
|---|---|---|
| `agpds_14b7f7487e` | 2× group_dep + 1× seasonal | M4-group / M4-seasonal |
| `agpds_33d84d2c9b` | 1× orthogonal + 1× group_dep | M4-orthogonal / M4-group |
| `agpds_503613ba96` | 1× orthogonal + 1× residual + 1× reversal | M4-orthogonal / **M1 straggler** / M4-reversal |
| `agpds_8180fe4e2c` | 1× orthogonal + 1× group_dep | M4-orthogonal / M4-group |
| `agpds_e9c40d0352` | 1× marginal + 2× group_dep | M4-marginal / M4-group |

5 个 scenario / 13 条 failures，全部落在
[FAILURE_MECHANISMS.md §7.2](../FAILURE_MECHANISMS.md) 标注的"剩余非 KS 类
失败，属机制 4+，单独 plan"范畴。`agpds_503613ba96` 的 residual_* 是
[M1_RATIO_OPERATOR_STRAGGLER.md](../mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md) 描述的 M1
长尾。**机制 3 在 openai-cal 上已闭合**。

---

## 8. 净裁定

| 维度 | 验证状态 |
|---|---|
| **Path A**（prompt 约束）on openai | ✅ 实际 production 验证有效——拦住了 v1 的 2 个 hard errored |
| **Calibration**（in-loop sigma）on openai | ✅ 11 次 check / 1 次 retry / 全部 converge——production 验证通过 |
| **机制 1 关闭** on openai | ⚠️ 主线关闭（residual 15→1, median ratio 1.54→0.77）；剩 1 条 ratio-operator 长尾——[M1_RATIO_OPERATOR_STRAGGLER.md](../mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md) |
| **Path D**（KS 稀疏 cell）on openai | ✅ `ks_*` 39→0 / passed 1→5 / 0 regressions（§7）|
| **机制 3 关闭** on openai | ✅ §7 |
| **Path B**（PatternInjectionError detail）| ⚠ 仅单元测试覆盖；production 没触发（因为 Path A 拦在前面） |
| **Path C**（UndefinedEffectError）| ⚠ 仅单元测试覆盖；production 没触发（因为 Path A 拦在前面） |
| **SKIP_PERSISTENCE wiring** | ⚠ 仅集成测试覆盖；production 没触发（因为 0 SkipResult） |

**Path B/C/skipped.jsonl wiring 仍是 "代码正确但 production 未实际触发"**。
要真正端到端验证它们，需要**故意构造**一个会触发的 scenario（譬如手动写一份
带 0-row pattern 或 None effect-map 的 declarations.json，绕开 LLM，直接喂
给 Stage 1 / Loop A 看 typed feedback 能否让 LLM 自修）。

---

## 9. 配套阅读

- [PATH_D_KS_SPARSE_CELLS.md](../subsystems/PATH_D_KS_SPARSE_CELLS.md) — Path D 设计 + gemini V3 实测
- [M1_RATIO_OPERATOR_STRAGGLER.md](../mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md) — §7.4 剩 1 条 residual 的根因
- [SIGMA_CALIBRATION.md](../archive/SIGMA_CALIBRATION.md) — calibration 设计与 gemini 端验证
- [FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md) — 三机制 + 4-way 实测
- [SKIP_PERSISTENCE.md](../subsystems/SKIP_PERSISTENCE.md) — Stage 1 skip 持久化 wiring
- [2026-05-14-stage1-sigma-calibration.md](../archive/2026-05-14-stage1-sigma-calibration.md) — 原 TDD 实施计划
