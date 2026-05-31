# AGPDS Phase 2 Soft Failure 分析：根因、修复、效果、未尽事项

> 基于 [FAILURE_MECHANISMS.md](FAILURE_MECHANISMS.md) 与 [pipeline/phase_2/orchestration/calibration.py](../../pipeline/phase_2/orchestration/calibration.py)、[retry_loop.py](../../pipeline/phase_2/orchestration/retry_loop.py) 等代码综合整理。

> **⚠️ 更正（2026-05-31）**：本文写于 sigma calibration 时代。该 calibration 已于 2026-05-30 **禁用**，且 M1 真因已更正为 **Phase γ pattern 污染**（非乘积方差、非「LLM 算不出乘积 σ」）。§0 表「解决方案核心 / 当前效果」、§3.2 算法、§4.x 等涉及 calibration 的叙述均为历史；当前权威说法见 [mechanisms/M1_RESIDUAL_RECONCILIATION.md](mechanisms/M1_RESIDUAL_RECONCILIATION.md)。

---

## 0. 一页内回答全部问题

| 问题 | 回答 |
|---|---|
| **什么是 sigma？** | LLM 在每个 measure 列上声明的 *高斯噪声标准差* `noise={"sigma": σ}`——它代表"这列围绕公式预测值应有的散布"。 |
| **什么是 soft failure？** | Stage 2 validator 跑完后 batch 仍然产出数据，但部分 statistical check 没过（`residual_*`、`ks_*` 等）的"软失败"。区别于让 scenario 直接报错的 *hard failure*。 |
| **根因？** | LLM 把每个 SDK 调用当独立声明写，但引擎把它们作为**联合分布 + 乘法结构**求值。三条机制：复合方差盲区、联合分布盲区、稀疏 cell 脆弱性。 |
| **解决方案核心？** | Loop A 内增加 **LLM-in-the-loop sigma calibration**：exec 成功后 replay → 量 empirical residual std → 反馈给 LLM 重写 sigma。独立 retry budget（≤3 次）。 |
| **当前效果？** | pingyue-samples 10 个 scenario：passed **0/10 → 5/10**（+ Path D）；residual_* 失败 **15 → 0**；ks_* 失败 **76 → 0**（+ Path D）；总失败 93 → 7（-92%）。 |
| **未解决？** | Path B/C 端到端没在 openai 上验证；Constraint 13 (Path D LLM 端) 没在 production LLM 重跑验证；剩 5 个 scenario 因机制 4+（group_dep / seasonal / outlier / reversal）soft-fail，需独立 plan。 |

---

## 1. 背景：什么是 soft failure，sigma 又是什么

### 1.1 AGPDS Phase 2 一句话回顾

Phase 2 是 ChartAgent benchmark 的 *Agentic Data Simulator*：LLM 写一段 `FactTableSimulator` SDK 脚本→生成一份 Master DataFrame + Schema Metadata。两个 validator 把关：

```
LLM 写脚本 ──→ M2 引擎执行 ──→ M5 validator
   ↑ Loop A          (Stage 1)         (Stage 2)
   exec 错误反馈                       residual_* / ks_* / pattern_* ...
   sigma 校准反馈
```

- **Loop A** = LLM-in-the-loop。脚本执行报错 → 把 typed exception 喂回 LLM 重写（≤3 次）。
- **Loop B** = 参数级 autofix。统计 check 不过 → 用 `widen_variance` / `amplify_magnitude` 等微调参数（≤3 次）。

### 1.2 Sigma 是什么

LLM 在 SDK 里这样声明一个 measure：

```python
add_measure_structural(
    name="enrollment_count",
    formula="application_count * acceptance_fraction * major_yield",
    noise={"distribution": "gaussian", "sigma": 5.0},   # ← 这就是 sigma
)
```

`sigma` 是 LLM 对"这个 measure 围绕公式值应该有的噪声标准差"的**预言**。引擎按它生成数据；validator 事后量数据的真实 residual std，跟 LLM 声明的 sigma 比，比值 `ratio = |empirical − declared| / declared` 超 0.2 就报 `residual_<col>` 失败。

### 1.3 Soft failure 是什么

Pingyue-samples baseline 跑出来的样子（[FAILURE_MECHANISMS.md §1](FAILURE_MECHANISMS.md)）：

| 类型 | 例子 | 性质 |
|---|---|---|
| residual_* | `residual_absentee_count: ratio=66.5×` | **soft** — 数据生成完了，但 noise 模型跟事实不符 |
| ks_* | `ks_absentee_count_by_grade_level: D=0.97` | **soft** — 跨 cell 分布对不上 |
| pattern target zero rows | `PatternInjectionError` | **hard** — scenario 直接 errored |
| KeyError: 'None' | `effect map 缺 'None' key` | **hard** — scenario 直接 errored |

Baseline 10/10 全部 fail：0 passed、8 soft-failed、2 errored，total 83 个 check 失败。

---

## 2. 根本原因：LLM 与引擎的认知错位

[FAILURE_MECHANISMS.md §1](FAILURE_MECHANISMS.md) 一句话：

> **LLM 把每个 SDK 调用当成独立声明在写，但引擎把它们作为联合分布 + 乘法结构公式来求值。**

三条机制把这个错位投射成具体失败：

### 2.1 机制 1：复合方差盲区（占比最大）

**触发**：当 measure 公式是多随机变量的**乘积**时，LLM 闭式算不出乘积的标准差。

```
enrollment_count = application_count
                 * acceptance_fraction
                 * major_yield
                 * level_yield
                 * school_enrollment_multiplier
```

LLM 看每个因子单独想"sigma=5 差不多"——但 5 个随机变量相乘的方差是均值和方差的复杂卷积，实际 std 容易到 300+。`residual_absentee_count` 的 ratio 66.5× 不是 bug，是数学。

**为什么 baseline 没踩雷**：早期 legacy 域（Spotify / Netflix / faculty）的公式都是 `random × const + add` 加法主导。Pingyue 教育域的公式是漏斗模型（`P(accept | applied) × P(enroll | accept)`），乘的是条件概率——天然触发机制 1 最坏路径。

### 2.2 机制 2：联合分布盲区

**触发 A**：`inject_pattern("outlier_entity", target="campus=='UC Berkeley' & race=='Native American/Alaska Native'")`。LLM 知道 Berkeley 占 20%、Native American 在国际生中 1%——但没算 `P(both) ≈ 720 × 0.2 × 0.01 × P(International) < 1 行` → `PatternInjectionError: matched zero rows`。

**触发 B**：跨 group 的条件分布未归一化 → sampling 回退出 `None` → effect map 查不到 `'None'` 键 → 裸 `KeyError`。

### 2.3 机制 3：稀疏 cell 脆弱性 (Path D, 2026-05-20 已修)

LLM 喜欢声明多维分类（`tier × program × year × residency`），交叉后 cell 大小 n=5–35。KS 检验在 n<30 时一个 outlier 就能把 D 推到 0.7+。这部分不全是 LLM 的错——给定 `target_rows=300–1000`，多因子设计下 cell 必然稀疏。

修复（详见 [PATH_D_KS_SPARSE_CELLS.md](subsystems/PATH_D_KS_SPARSE_CELLS.md)）：validator 加 `n<30` skip + Bonferroni 校正 + per-measure pass-rate 聚合；prompt 加 HARD CONSTRAINT 13 让 LLM 预谋 cell 密度。实测 `ks_*` 11→0，0 regression。

### 2.4 为什么 Loop B 救不了

Loop B 的四把工具（[autofix.py](../../pipeline/phase_2/validation/autofix.py)）都是**局部参数微调**：

- `widen_variance × 1.2^3 = 1.73×`，对 ratio 66× 杯水车薪
- 公式结构错时，参数 override 救不了

> **Loop B 假设 LLM 把骨架搭对了，只是火候没调准。**这次失败暴露：LLM 连骨架都没搭对——它**误判了变量耦合关系**。骨架错误必须沿 Loop A 修。

---

## 3. 解决方案：三条修复路径 + 一个 calibration 子系统

### 3.1 全景

| 路径 | 治哪条机制 | 治法 | 代码位点 |
|---|---|---|---|
| **A. Prompt 加约束** | 1 + 2 | 让 LLM 在声明时就知道复合方差和 None 陷阱 | [orchestration/prompt.py:103-118](../../pipeline/phase_2/orchestration/prompt.py#L103) |
| **B. PatternInjectionError 详化** | 2 | 写错后给可操作指引 | [engine/patterns.py:47-63](../../pipeline/phase_2/engine/patterns.py#L47) |
| **C. KeyError → UndefinedEffectError** | 2 | 裸异常升级为 typed feedback | [engine/measures.py:245-251](../../pipeline/phase_2/engine/measures.py#L245) |
| **★ Sigma Calibration（核心）** | 1（根） | Loop A 内实测 residual → 反馈给 LLM 重写 sigma | [orchestration/calibration.py](../../pipeline/phase_2/orchestration/calibration.py) + [retry_loop.py](../../pipeline/phase_2/orchestration/retry_loop.py) |

> Path A 是 **预防层**：在 declaration 阶段降低犯错率。
> Path B、C 是 **反馈通道**：把哑错升级成会话，让 Loop A 能修。
> Calibration 是 **根治层**：直接绕过 LLM 算不出乘积 std 的数学障碍。

### 3.2 Sigma Calibration 算法（已禁用，历史）

> calibration 已于 2026-05-30 **禁用**。其算法（Loop A exec 成功后 replay → 量 empirical residual std → 偏差 ≥0.2 则反馈 LLM 重写 sigma，独立 retry budget ≤3、不收敛写 `skipped.jsonl`）与设计决策详见已归档手册 [archive/SIGMA_CALIBRATION.md](archive/SIGMA_CALIBRATION.md)。**为何它实为「掩盖」pattern 污染而非修因，见 [mechanisms/M1_RESIDUAL_RECONCILIATION.md §5](mechanisms/M1_RESIDUAL_RECONCILIATION.md)。**

### 3.3 Path A 不是 calibration 的替代——它降低 calibration 触发频率

Path A 的 hard constraint 11/12（[prompt.py:103-118](../../pipeline/phase_2/orchestration/prompt.py#L103)）告诉 LLM "sigma ≈ 10–30% of range"。实测把 gemini 的 residual ratio median 从 19.25 → 2.49（[FAILURE_MECHANISMS.md §8.2](FAILURE_MECHANISMS.md)）——但**够不到** validator 阈值 0.2。所以 calibration 不可省。

---

## 4. 实际效果

### 4.1 3-way 实测（同 10 scenario，byte-identical）

| 批次 | Path A | 校准 | passed | residual_* | ks_* | total |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| -2 (gemini baseline) | ✗ | ✗ | 0/10 | 18 | 64 | 83 |
| -v2 (gemini +A) | ✓ | ✗ | 0/10 | 15 | 76 | 93 |
| **-v3 (gemini +A+cal)** | ✓ | ✓ | **4/10** ✓ | **0** ✓ | **11** | **18** (-81%) |

**机制 1 关闭**：residual_* 从 15 全砍到 0。10 个 scenario 中 **9 个第一轮 calibration 就过**，只 1 个（dom_024）触发 3 轮收敛。

> **关键 insight**：ks_* 从 76 → 11 同时大降——印证 §2.3 的判断，*ks 失败大多是机制 1 的投影*：sigma 写对了，跨 cell 分布自然就对上了。

### 4.2 7/7 acceptance gates PASS

机制 1 关闭判定的 7 条 gate（residual count = 0、median ratio < 阈值、passed ≥ 任意 + 等）全部通过。详见 [FAILURE_MECHANISMS.md §8](FAILURE_MECHANISMS.md)。

### 4.3 T9 plumbing bug 教训

`patterns=metadata.get("patterns", [])` 在 `agpds_execute` 路径收到空 metadata → patterns=`[]` → `check_structural_residuals` 的 P3-8 pattern-row 排除静默失效 → pattern outlier 行被计入 residual std。一行修复 `patterns=patterns`（commit `b16525e`）。完整 case study 见 [archive/SIGMA_CALIBRATION.md §8](archive/SIGMA_CALIBRATION.md#8-case-studyt9-plumbing-bug)。教训：跨模块「同一个计算」结果不一致时，先验证两端输入字节一致。

> 后记：此 T9 bug 正是后来锁定 **M1 residual 膨胀真因 = pattern 污染**（而非乘积方差）的关键线索，见 [mechanisms/M1_RESIDUAL_RECONCILIATION.md](mechanisms/M1_RESIDUAL_RECONCILIATION.md)。

### 4.4 测试覆盖

baseline 355 → **376 测试**（+21），全部 `pytest pipeline/phase_2/tests/modular -x -q` 通过。具体见 [SIGMA_CALIBRATION.md §5](archive/SIGMA_CALIBRATION.md#5-测试矩阵)：

- `test_calibration.py` (14) — dataclasses、happy path、_extract_declared_sigma 6 edge case、parse RuntimeError
- `test_sandbox_format.py` (2) — feedback 含具体数字、原代码、"Do NOT change" 指令
- `test_retry_loop.py` (4) — 校准失败 → retry → skip_reason 正确；独立 budget；无 structural-sigma 不触发
- `test_pipeline_loop_b_patterns.py` (1) — T9 regression，spy `SchemaAwareValidator.validate`
- `test_engine_measures.py` 扩展 — `UndefinedEffectError` 替换裸 `KeyError`

---

## 5. 未解决问题与下一步

按优先级排：

### 5.1 ~~[中] `_save_skip_record` 未接入~~ ✓ 已修（2026-05-19）

详见 [SKIP_PERSISTENCE.md](subsystems/SKIP_PERSISTENCE.md)。要点：

- `AGPDSPipeline.generate_artifacts()` 签名改为 `Dict[str, Any] | SkipResult`，遇到 SkipResult 时 stamp `generation_id` 后 return（不再 raise）
- `SkipResult` dataclass 加 `generation_id: str = ""` 字段；`_save_skip_record` 签名清理为 2 参
- `run_generation_batch` + `run_scenario_id_generation` 加 `isinstance` 分支写 `skipped.jsonl`；`run_single` 保持 raise 语义
- 新增 `TestRunGenerationBatchPersistsSkipped`（2 个集成测试）——锁死 wiring 不变性。这是当时 T5/T6 漏掉的测试。
- 测试 376 → 378，全部通过。

### 5.2 ~~[中] 机制 3 未修~~ ✓ 已修（2026-05-20，Path D）

详见 [PATH_D_KS_SPARSE_CELLS.md](subsystems/PATH_D_KS_SPARSE_CELLS.md)。要点：

- Validator 端：[`statistical.py::check_stochastic_ks`](../../pipeline/phase_2/validation/statistical.py) 加 `n<30` skip + Bonferroni 校正 (`α = 0.05 / K`) + 聚合成单 Check（pass-rate ≥ 0.9 才算通过）
- Prompt 端：[prompt.py](../../pipeline/phase_2/orchestration/prompt.py) HARD CONSTRAINT 13 — 让 LLM 在声明阶段预谋 cell 密度（target_rows ≥ 30 × cell_count，或 K ≤ 2）
- 实测（pingyue 10 个 scenario, validator-only rerun）：`ks_*` 失败 **11 → 0** (-100%)，passed **4 → 5**，0 regressions
- 测试 378 → 387，全部通过
- LLM 端验证（Constraint 13 实际效果）未跑——见 PATH_D doc §5.5

**剩余 5 个 soft-fail 不在 Path D 范围内**：group_dep_* / seasonal_* / outlier_* / reversal_*（各 1-2 个），是机制 4+，每条需独立修复 plan。

### 5.3 [中] openai 端到端验证 Path B/C 缺口

gemini 的 -v2/-v3 都没触发 `PatternInjectionError`/`UndefinedEffectError`（纯运气）。Path B/C 的代码改动 + 单元测试都对，但**Loop A 拿 typed feedback 后自修**还没在 production 验证。两条路：

1. openai 上重跑 -v3
2. 人造 scenario 强制触发

### 5.4 [低] 剩 6 个仍 soft-fail 的 scenario 逐一分析

passed 4/10 是 stretch 达成，但还剩 6 个有 18 条失败。逐一看失败 check 类型，看是机制 3 还是新机制（避免认为"机制 1 关了就完了"而漏新模式）。

### 5.5 [Nitpicks，来自 final reviewer]

- `retry_loop.py` 的 `# IS-6 token-budget half` 是 sprint-internal jargon → 改功能描述
- `test_sandbox_format.py` empty-failures 断言 `"0" in out or "no" in out.lower()` → 紧到 exact substring
- ~~`_save_skip_record` 的 `skip_result: untyped` → `TYPE_CHECKING` import guard~~（§5.1 修复时已顺手类型化为 `SkipResult`）

---

## 6. 总结：这次修复教了什么

1. **LLM 写 declarative DSL 时会暴露认知-引擎错位**——它在拼乐高，引擎在跑微分方程。修法不是"换模型"，是给 LLM 看到引擎的实际输出（calibration 的本质）。
2. **Path A 这种 prompt heuristic 有上限**——它在加法主导域好使，乘法链域够不着 0.2 阈值。需要**实测反馈**绕过 LLM 的数学盲区。
3. **独立 retry budget** 是干净的设计——把"代码错"和"参数错"分开计预算，避免互相挤兑。
4. **跨模块算同一件事**必须验证输入一致（T9 教训）。两端调同一个函数 ≠ 两端看到同一份数据。
5. **统计量级 > 计数**：v1→v2 总失败数从 114 升到 93 看似改善小，但 residual ratio median 从 19.25 → 2.49 是质变；ks 反向上升是 sigma 调对后的副作用，不是 Path A 失败。

---

## 配套阅读

- [FAILURE_MECHANISMS.md](FAILURE_MECHANISMS.md) — 3 机制 + 修复路径 A/B/C + 3-way/4-way 实测对比
- [SIGMA_CALIBRATION.md](archive/SIGMA_CALIBRATION.md) — calibration 模块技术参考
- [VALIDATION_PERSISTENCE.md](subsystems/VALIDATION_PERSISTENCE.md) — Stage 2 持久化层
- [pipeline/phase_2/INTERFACES.md](../../pipeline/phase_2/INTERFACES.md) — M1–M5 模块契约
