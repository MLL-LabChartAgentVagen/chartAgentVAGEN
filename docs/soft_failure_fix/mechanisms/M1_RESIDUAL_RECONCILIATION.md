# M1 Residual 对账：乘积方差不进 residual，真因是 Phase γ pattern 污染

> **日期**：2026-05-30 ｜ **触发**：用户在审视 [AUDIT_2026-05-28 §2 (F1)](../AUDIT_2026-05-28.md) 时提出「把单变量 noise 的 std clip 到单变量的 1%，加上现有 M1 缓解手段，是否足以解决 M1」。
>
> 为回答这个问题做了一次代码 + git 对账，结论**纠正了 [MECHANISM_1_DEEP_DIVE](../archive/MECHANISM_1_DEEP_DIVE.md) 与 AUDIT §2 对 M1 真因的描述**：M1 的 `residual_*` 失败**不可能**来自「乘性公式的乘积方差」，因为 residual validator 在构造上就把乘积方差减掉了。真正能让 `residual_std >> σ` 的当前代码路径与 σ 无关。
>
> 本文记录「理解的更正」；不改任何 `pipeline/` 代码。

---

## 1. 结论速览

| 命题 | 置信度 | 依据 |
|---|---|---|
| residual validator 用「实测因子列」重算公式，乘积方差被减掉 | **确定** | 代码 + git（§2） |
| 因此干净测度（依赖未被 pattern/reshuffle 改动）`residual ≈ 自身 N(0,σ)`，ratio ≈ 0，与乘性嵌套深度无关 | **确定** | 数学（§2） |
| 真实批次里 `residual_std >> σ` 只能来自 Phase β 之后对列的改动：① Phase γ pattern 注入；② Loop B reshuffle | **确定**（穷举代码路径） | §3 |
| 这个膨胀量 **σ 无关**；deep dive 表里 ratio 随 σ 塌缩、residual_std 固定，正是其特征 | **确定**（自洽 + 佐证） | §4 |
| 历史 66×/9742× 具体走 pattern 哪个泄漏点（`except:pass` / target-eval 错位 / reshuffle） | **推断**（artifact 已删，未实测锁定） | §6 caveat |
| 1% noise clip 作为 M1 修复 = 错的杠杆 | **确定** | §5 |
| Loop A sigma 校准在掩盖 pattern 污染，而非修因 | **推断**（强） | §5 |

---

## 2. 数学 + git：乘积方差进不了 residual

### 2.1 validator 怎么算 residual

[`check_structural_residuals`](../../../pipeline/phase_2/validation/statistical.py#L525-L570) 逐行重算公式预测值，用的是 **df 里已存储的实测上游列**：

```python
for i, (idx, row) in enumerate(work_df.iterrows()):
    context = {}
    for other_col, other_info in columns_meta.items():
        if other_info.get("type") == "measure" and other_col != col_name:
            if other_col in work_df.columns:
                context[other_col] = float(row[other_col])   # 实测 per-row 值
    if effects_spec:
        context.update(_resolve_effects(col_meta, dict(row), columns_meta))
    predicted[i] = _safe_eval_formula(formula, context)

observed = work_df[col_name].values.astype(float)
residuals = observed - predicted
```

生成侧 [`_eval_structural`](../../../pipeline/phase_2/engine/measures.py#L241-L281) 消费上游也是读同一批存储列（`rows[sym][i]`，[measures.py:255-257](../../../pipeline/phase_2/engine/measures.py#L255-L257)），且 noise 在 return 前就加进存储值（[measures.py:276-279](../../../pipeline/phase_2/engine/measures.py#L276-L279)）。`to_dataframe` 对 measure 列只做 float64 透传、无 round/clip（[postprocess.py:55-74](../../../pipeline/phase_2/engine/postprocess.py#L55)）。

### 2.2 推论

设结构测度 `Z = f(A, B, …)`，A/B/… 都是物化的测度列。生成时：

```
df[Z] = f(A_realized, B_realized, …) + N(0, σ_Z)
```

validator 重算 `predicted = f(A_realized, B_realized, …)`（同一批列），于是：

```
residual = df[Z] − predicted = N(0, σ_Z)   ⇒  residual_std ≈ σ_Z  ⇒  ratio ≈ 0
```

**`Var(XY)=Var(X)Var(Y)+Var(X)E[Y]²+Var(Y)E[X]²` 的放大只进「列 Z 本身的方差」，被 `predicted` 完全减掉，不进 residual。** 嵌套多深都一样——链式上游的存储值都被逐层减掉。

### 2.3 git：这不是"旧 validator"

`git log -L 525,550:…/statistical.py` 显示：这段「用实测因子重算」的循环体**自第一版 `0e696e0`（2026-04-07）起就是现在这样**，从未用过参数期望/均值。时间线：

| commit | 日期 | 内容 |
|---|---|---|
| `0e696e0` | 2026-04-07 | phase 0-2：residual 减实测因子（**从这版起**） |
| `eb47cb9` | 2026-04-16 | 加 P3-8 pattern 行排除 |
| `006db6a` | 2026-05-14 | scaffold sigma 校准（**晚 5 周**） |

所以「validator 曾用期望算 residual、后来改成减实测因子」的解释被排除。校准是建在一个**本就把乘积方差减干净**的 validator 之上的。

---

## 3. 真正能让 residual 膨胀的两条路径（σ 无关）

[`run_pipeline`](../../../pipeline/phase_2/engine/generator.py#L87-L98) 的顺序：

```
Phase β 生成测度(互相消费 post-noise 值) → to_dataframe → Phase γ inject_patterns(df) → Phase δ realism
```

validator 跑在 **post-pattern、pre-realism** 的 df 上。能造成 `observed ≠ f(当前列) + noise` 的只有 Phase β 之后对列的改动：

1. **Phase γ pattern 注入**（[generator.py:96-98](../../../pipeline/phase_2/engine/generator.py#L96)）。下游 `Z` 在 Phase β 用 `M_preβ` 算好；Phase γ 把 `M` 列改成 `M_postpattern`；validator 重算 `predicted = f(M_postpattern)`，于是 `residual = f(M_preβ) − f(M_postpattern) + noise` = pattern 偏移 × 下游系数。这正是 [statistical.py:497-501](../../../pipeline/phase_2/validation/statistical.py#L497) 注释自述的 "downstream values were computed from pre-pattern upstream values"。pingyue scenario 的 `seasonal_anomaly` / `ranking_reversal` 等都是 pattern。
2. **Loop B reshuffle override**（[measures.py:512-516](../../../pipeline/phase_2/engine/measures.py#L512)，仅 Loop B，默认不触发）。

P3-8 试图把 pattern 命中的行排除，但有泄漏点：
- `df.eval(p["target"])` 包在 `except: pass` 里（[statistical.py:512-515](../../../pipeline/phase_2/validation/statistical.py#L512)）——target 表达式一坏就**静默不排除**；
- `_get_formula_measure_deps` 只抓**直接**依赖（[statistical.py:445-452](../../../pipeline/phase_2/validation/statistical.py#L445)）——本场景恰好够（pattern 污染只传一跳：下游读的是冻结的上游存储值），但任何"非行命中"式的列改动（全局/乘性 shift）都不会被行掩码覆盖。

---

## 4. 为什么 deep dive 的数据反而佐证本结论

[MECHANISM_1_DEEP_DIVE §1](../archive/MECHANISM_1_DEEP_DIVE.md) 表：

| 维度 | baseline | pathA | calibrated |
|---|:-:|:-:|:-:|
| `residual_*` ratio max | 9742× | 28.74× | 0 |

pathA 只改 prompt（让 σ 变大），calibrated 把 σ 校到 ≈ residual_std。若 `residual_std = 自身 noise`，则 ratio 在所有批次都该 ≈ 0。事实是 **ratio 随 σ 增大而塌缩、residual_std 像是固定的**——这正是「residual_std 是个 **σ 无关的结构残差**」的特征。校准"生效"的真相：把声明 σ 抬到 ≈ 那个固定残差，使 `|residual_std − σ|/σ < 0.2`。**这是用大 noise 把 pattern 污染掩盖过去，不是消除它。**

---

## 5. 三个杠杆的定性

| 杠杆 | 判定 |
|---|---|
| **1% noise clip**（用户提案） | **错的杠杆**。residual 本就 ≈ σ；clip 只压已经正确的项，对 σ 无关的结构残差毫无作用，且与校准方向（把 σ 抬大）直接冲突。可作独立 noise 卫生策略（限制 LLM 声明的加性 noise 不盖过 signal），但**不记 M1 账**。 |
| **Loop A sigma 校准** | **前提存疑（强推断）**。为「乘积方差膨胀 residual」而建，但该 validator 产生不了这种膨胀。它真正触发时极可能在追 pattern 污染，而其"修法"是膨胀 σ 去吞被污染行——掩盖而非修因。 |
| **真正的 M1 杠杆** | P3-8 pattern 排除的完整性 + 那个 `except: pass` 静默跳过 + residual 口径（是否该在 pre-pattern df 上算结构残差），全部**与 σ 无关**。 |

---

## 6. 实测确认（2026-05-30，已锁定）

机制已用确定性诊断 [`pipeline/phase_2/analysis/residual_source_dump.py`](../../../pipeline/phase_2/analysis/residual_source_dump.py) 锁死——零 LLM、可复现。

**合成 case**（`enrollment = applied*accept_frac*yield_rate`，声明 σ=5，outlier pattern 打在 enrollment 上）三实验：

| 实验 | residual_std | 说明 |
|---|---:|---|
| ① 无 pattern | **5.01** | ≈σ；同时 enrollment **列** std=127 —— 乘积方差只进列、不进 residual |
| ② pattern + P3-8 ON（T9 修复） | **5.07** | 202 行被排除 → residual 干净，validator PASS |
| ③ pattern + P3-8 OFF（模拟 T9 bug） | **641.7** | =127×σ，validator FAIL —— 复现 66×/9742× 量级，**纯 pattern 行污染、σ 无关** |

**真实 batch 复核**（`--declarations`）：

- `output/agpds/smoke-test-batch-1` 里正是 deep dive §3.1 的案例 `agpds_e9c40d0352::absentee_count`（文档归因为「乘积方差 743、28.74×」）。现行代码 + T9 修复下：**P3-8 ON → residual_std=23.6 ≈ σ(24)**（本应 PASS，无需校准）；P3-8 OFF → 62.6（121 行 pattern 污染）。
- `output/agpds/ks-measure-n90`（90 scenario）：几乎**每个**结构测度都是 `P3-8 ON ≈ σ`、`OFF 膨胀`（如 lifetime_value σ=5000 ON=5065/OFF=10608；ticket_revenue σ=15000 ON=13993/OFF=60179；operating_income σ=8 ON=8.05/OFF=22）。

**结论（锁定）**：M1 的 `residual_*` 膨胀 = Phase γ pattern 行被计入 residual（σ 无关），由 P3-8 排除消除；**乘积方差从不进 residual**。历史 66×/9742× 是 T9 bug（`patterns=[]` → P3-8 失效）的产物，**不是**乘积方差，也**不需要** sigma 校准来"修"——T9 修复本身就让 residual ≈ σ。

> 旁注：ks-measure-n90 里有 2 个 scenario `run_pipeline` 直接失败（`'obs_bias'/'phase_adj' in formula has no definition for 'None'`）——与本机制无关，已查清为 JSON 往返把整数分类列的 dict 键 stringify 导致依赖列全-None，并已修复，详见 [subsystems/SERIALIZATION_INT_KEY_ROUNDTRIP.md](../subsystems/SERIALIZATION_INT_KEY_ROUNDTRIP.md)。

---

## 7. Cross-link

- [MECHANISM_1_DEEP_DIVE.md](../archive/MECHANISM_1_DEEP_DIVE.md)：M1 原始深挖（其「乘积方差进 residual」前提见本文更正）
- [M1_RATIO_OPERATOR_STRAGGLER.md](M1_RATIO_OPERATOR_STRAGGLER.md)：ratio 算子子类（`Var(A/B)` 的结构下限同样 σ 无关，与本文同源）
- [../AUDIT_2026-05-28.md](../AUDIT_2026-05-28.md) §2 / §7：本文更正其 F1 真因表与 clip 选项

---

## 8. 研究 baseline 回退（2026-05-30，可逆）

为在干净 baseline 上研究 M1 真实行为，**有意地、可逆地**撤下两层「防 66×」的掩盖措施，**保留 T9 真修复**（`patterns=patterns`）。目的：验证「光靠 T9 修复让 P3-8 正确排除 pattern 行后，residual 是否就已 ≈ σ、M1 是否自然消失」。

### 撤下了什么

| 措施 | 改动 | 文件 |
|---|---|---|
| Loop A sigma 校准 | 模块标志 `_CALIBRATION_ENABLED = False` + `if result.success:` 块内早返回；`calibration.py` 本体未删 | [retry_loop.py](../../../pipeline/phase_2/orchestration/retry_loop.py)（常量 ~L39、gate ~L263） |
| Path A 约束 11（NOISE CALIBRATION，σ=range 10-30%） | `SYSTEM_PROMPT_TEMPLATE` 里该段 7 行字符串字面量整体注释 | [prompt.py:106-112](../../../pipeline/phase_2/orchestration/prompt.py#L106) |

### 保留 / 未动
- **T9 `patterns=patterns`**（[pipeline.py:287](../../../pipeline/phase_2/pipeline.py#L287)）——真修复，保留。
- 任何 validator（`check_structural_residuals` 等）未动——目的是让 `residual_*` 失败在 Stage 2 真实浮现。
- realism 仍禁用（既有，与本回退无关）。

### 受影响测试（skip 不删）
- [test_retry_loop.py](../../../pipeline/phase_2/tests/modular/test_retry_loop.py)：`test_calibration_failure_triggers_retry_then_skip_if_unconverged`、`test_calibration_recovers_after_one_round_of_feedback` 标 `@pytest.mark.skip`（断言校准触发，已不成立）。
- 其余校准测试（直接调用 `check_sigma_calibration` 的单元测试、批持久化的 mock 测试）不受影响，保持绿。

### 预期行为（非回归）
关校准 + 撤约束 11 后，σ 偏小的 scenario 会在 Stage 2 重新出现 `residual_*` 失败——**这正是研究信号，不是 bug**。

### 一行恢复
1. `retry_loop.py`：`_CALIBRATION_ENABLED = True`；
2. `prompt.py`：取消约束 11 那 7 行注释；
3. 去掉上述两个测试的 `@pytest.mark.skip`。
