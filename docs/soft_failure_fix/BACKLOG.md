# `docs/soft_failure_fix/` — Backlog / Deferred Queue

> **目的**：把分散在各 mechanism doc 里的 deferred items / candidates / accepted-no-fix
> 一站式列出，并给出**推荐执行顺序**。新 session 拿起这份就知道下一步该做什么。
>
> **维护**：每完成一个 item 立即从本文标记 ✓ 或移到 §7 "已完成 / 归档"。新发现的
> deferred item 立即追加到对应 Tier。
>
> **最后更新**：2026-05-21（Phase D.2 完成后）

---

## 0. TL;DR — 推荐顺序

```
Tier 1 (immediate):
  ① Phase D.3  ──────────── M6 子机制 realized z << expected z
                            设计已完成 (M6_PHASE_D3_REALIZED_Z_GAP.md)

Tier 2 (按证据强度):
  ② M8: param_model cell-level mis-fit (4 batch 失败，证据最强)
  ③ M7: marginal × group_dep induced shift (1 batch 失败，机理最清晰)
  ④ M9: outlier_entity z_score declared vs realized

Tier 3 (高成本 / 低紧迫):
  ⑤ Phase C: reversal_* on funnel pairs
  ⑥ Phase D.4: row-count guardrail 泛化到其他 4 个 pattern types
  ⑦ Phase D.1: validator-side underspecified-magnitude soft-skip

Tier 4 (accepted, 不修):
  ⑧ M1 ratio operator straggler
```

---

## 1. Status 标签解释

| 标签 | 含义 |
|---|---|
| **Deferred** | 已设计 / 已 hand-trace，等候拾起即可实施 |
| **Candidate** | 假设 + 部分证据，需先做 1-2 个 hand-trace 才能升级为 Deferred |
| **Accepted** | 已识别，决定不修（成本-收益不划算 或 等待 sample 累积） |
| **Backstop** | 上游修复失败时的兜底，平时不启动 |

---

## 2. Tier 1 — 立即可做

### ① Phase D.3：realized z << expected z 修复

| 字段 | 内容 |
|---|---|
| **Status** | Deferred — 完整设计文档已写 |
| **主文档** | [`mechanisms/M6_PHASE_D3_REALIZED_Z_GAP.md`](mechanisms/M6_PHASE_D3_REALIZED_Z_GAP.md)（10 节，含数学、候选方案、验收标准、reproducible 验证流程）|
| **关联** | [MECHANISM_6 §6.3](mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md#63-phase-dx-树形结构d1--d2--d3--d4) + [§6.4](mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md#64-cat-4-残留-2-条-seasonal-failure-的根因realized-z--expected-z) |
| **暴露 failure** | 2 条 seasonal_*（cat-4 pathD2-llm: `agpds_6dbb1c20db` `feature_adoption_rate` + `agpds_ac54f076fc` `add_to_cart_rate`）|
| **根因 1 句** | LLM 用「年度均值」算 required magnitude，validator 用「out-of-window 均值」测 z；当 measure 自带 month/quarter effects 把 in-window pre-injection 均值拉低，realized z 远小于 expected z |
| **修复方案** | 选项 A (prompt) + B (validator detail)，跳 C (SDK dry-run)，详 [M6_PHASE_D3_REALIZED_Z_GAP §5](mechanisms/M6_PHASE_D3_REALIZED_Z_GAP.md#5-候选修复方案按优先级) |
| **工程成本** | LOW (~30 行 prompt + ~10 行 validator + ~10 个测试) |
| **执行前需读** | 该文档全集 + 看 6dbb / ac54 实际 script 的 `param_model` 量级（回答 §6.1 开放问题）|
| **拾起 prompt** | 见 prior chat session 的"为新 session 设计的 prompt"——含 5 个 catch-up 文件 + 4-commit 粒度 + 8 个 acceptance checkbox |

---

## 3. Tier 2 — 按证据强度排序的 mechanism 候选

### ② M8：`param_model` cell-level mis-fit

| 字段 | 内容 |
|---|---|
| **Status** | Candidate — 跨 2 batch 共 4 条失败，证据最强 |
| **主文档** | 待写 `mechanisms/MECHANISM_8_PARAM_MODEL_CELL_LEVEL_MISFIT.md`（暂在 [MECHANISM_6 §6.5](mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md#65-未来候选-mechanism7-cat-3--cat-4-d2-共有的新失败族) 里有摘要）|
| **暴露 failure** | 4 条 ks_*：cat-3 8022 `ks_withdrawal_rate` (n=42, D=0.46), cat-4 1f66 `ks_supplier_lead_time`, cat-4 6dbb `ks_feature_adoption_rate` (n=110, D=0.17), cat-4 9ec5 `ks_total_assets` |
| **根因假设** | LLM 写的 `param_model`（lognormal/gamma/gaussian params）在 cross-classification 某些 cell 上和 realized sample 分布对不齐。Path D 的 Bonferroni-修正 KS 在 n≥30 cell 上**正确**触发 |
| **不是 Path D bug 的证据** | 失败 cell **不是稀疏的**（n=42/70/110+），Path D 的 ≥30 floor + Bonferroni α 工作正确；这是 LLM **真错** |
| **候选修复方向** | (a) prompt: 加 Constraint 教 LLM "param_model 必须在每个 cross-classification cell 上 self-consistent"; (b) validator detail: 加 `expected_quantile` vs `realized_quantile` 字段帮 LLM 在 retry 时看到差距 |
| **工程成本** | MEDIUM (写 MECHANISM_8 doc + prompt 或 validator + tests + LLM regen) |
| **执行前需做** | hand-trace 4 个 case 的实际 `param_model` 声明 vs realized cell distribution，确认根因 |

### ③ M7：marginal × group_dep 链 induced shift

| 字段 | 内容 |
|---|---|
| **Status** | Candidate — 1 batch 证据，但机理特别清晰 |
| **主文档** | 待写 `mechanisms/MECHANISM_7_MARGINAL_GROUP_DEP_SHIFT.md` |
| **暴露 failure** | 1 条：cat-3 e9c4 `marginal_weights_grade_band`（declared `[E=0.36, M=0.22, H=0.42]`，n=420 上 dev=0.216, Wald thresh=0.147）|
| **根因假设** | LLM 在某列声明了 marginal weights，然后又用 `add_group_dependency` 把这列做了 child；conditional_weights 的不均匀让 induced marginal 偏离 declared marginal。LLM 没意识到这个反推。Phase A 的 Wald CI 在 n=420 上**正确**触发 |
| **不是 Phase A bug 的证据** | n=420 远超 Phase A 的 n=10 skip 阈值；Wald thresh=0.147，但 dev=0.216 真大，应该报 |
| **候选修复方向** | prompt: 加 Constraint "若一列同时是 add_category(weights=...) 和 add_group_dependency 的 child，必须验证 conditional_weights × parent_marginal 反推后的 marginal 与 add_category 声明的一致" |
| **工程成本** | MEDIUM (写 MECHANISM_7 doc + prompt Constraint + tests + LLM regen) |
| **执行前需做** | 读 e9c4 declaration，确认 `grade_band` 是否被 `add_group_dependency` 链化；如有，列出反推链路 |

### ④ M9：`outlier_entity` z_score declared vs realized 不匹配

| 字段 | 内容 |
|---|---|
| **Status** | Candidate — 3 case 但根因待 hand-trace 验证 |
| **主文档** | 待写 `mechanisms/MECHANISM_9_OUTLIER_Z_SCORE_MISMATCH.md` |
| **暴露 failure** | cat-3 D.2 上 3 条：33d8 `outlier_yield_rate`, 8022 `outlier_withdrawal_rate` (z=1.7242, subset_mean=11.0116, ref_mean=5.8447, ref_std=2.9967), 503613 `outlier_student_faculty_ratio` |
| **根因假设（待确认）** | LLM 声明 `inject_pattern("outlier_entity", target=..., params={"z_score": X})`，但 X 与 realized 子集均值差距没对齐。可能是：(a) LLM 选的 target 子集行数太少不稳定；(b) X 和 measure scale 不匹配；(c) `set_realism(censoring=...)` 把 outlier 截断了 |
| **不是 validator bug 的证据** | `check_outlier_entity` 的 z 计算是直接的 `(subset_mean - ref_mean) / ref_std`；validator 工作正确 |
| **候选修复方向** | 待 hand-trace 后定 |
| **工程成本** | MEDIUM (先 hand-trace ~1h，再决定 prompt 或 validator) |
| **执行前需做** | **必须**先 hand-trace 3 个 case 的实际 declaration + master_table，分类根因（a/b/c 中哪一个），再设计修复 |

---

## 4. Tier 3 — 高成本 / 低紧迫

### ⑤ Phase C：`reversal_*` 在天然正相关 funnel pair 上声明

| 字段 | 内容 |
|---|---|
| **Status** | Candidate — 早期已探索（PINGYUE §8.3），未实施 |
| **主文档** | [`validation/PINGYUE_OPENAI_CAL_ANALYSIS.md §8.3`](validation/PINGYUE_OPENAI_CAL_ANALYSIS.md#83-phase-creversal-系统性追根) + [MECHANISM_4 §6.4](mechanisms/MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md#64-仍未修) + [MECHANISM_5 §6.5](mechanisms/MECHANISM_5_ORTHOGONAL_DEGENERACY_DEEP_DIVE.md#65-仍未修) |
| **暴露 failure** | 1 条 cat-3 baseline (503613 `reversal_course_load_student_faculty_ratio`) + 3 条 cat-3 D rerun variance + 0 条 cat-4 D.2（regen 把它清掉了）|
| **根因** | LLM 在 admission/checkout/research 这种**结构性正相关**的 funnel 双 metric 上声明 `ranking_reversal`，但 measure formula 没真正实现负相关。也与 M1 ratio straggler 同源（公式骨架共享上游变量）|
| **候选修复方向** | (a) prompt Constraint：声明 ranking_reversal 时必须证明 metric 对**不**在同一 funnel；(b) validator skip：当 reversal 失败且两 metric 公式共享上游变量时 detail enrichment；(c) 跟 M1 一起治（让 LLM 重写公式骨架）|
| **工程成本** | HIGH (需要 LLM 重写 formula；可能涉及多个 prompt constraint) |
| **何时启动** | cat-4 D.2 上 reversal_* 自然降到 0，紧迫性下降；建议**M8/M7/M9 之后再做** |

### ⑥ Phase D.4：row-count guardrail 泛化到其他 4 个 pattern types

| 字段 | 内容 |
|---|---|
| **Status** | Deferred — proactive coverage，无具体 trigger |
| **主文档** | [MECHANISM_6 §6.3](mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md#63-phase-dx-树形结构d1--d2--d3--d4) |
| **暴露 failure** | 0（预防性）— 但 `outlier_entity` (engine/patterns.py:48), `trend_break` (348), `dominance_shift` (357/464), `ranking_reversal` (464) 共享同样的 `len(in_window)==0` → `PatternInjectionError` 失败模式 |
| **候选修复方向** | mirror D.2 row-count guardrail，写一个泛化的 Constraint（"任何 `inject_pattern` 的 target × time-window 组合必须 expected_rows ≥ 5"）|
| **工程成本** | MEDIUM (4 个 sub-clause + 测试 + LLM regen) |
| **何时启动** | 出现 outlier/trend_break/dominance/reversal 任一的 `PatternInjectionError` 真实案例之后 |

### ⑦ Phase D.1：validator-side underspecified-magnitude soft-skip

| 字段 | 内容 |
|---|---|
| **Status** | Backstop — 仅当 D.3 失败时启动 |
| **主文档** | [MECHANISM_6 §6.3](mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md#phase-d1validator-side-underspecified-skip-兜底-仍-deferred) |
| **逻辑** | 当 `declared_magnitude < 2 × baseline_std / |baseline_mean|` 时 validator 主动 `passed=True` + `detail="skipped (underspecified per Constraint 17)"` |
| **工程成本** | LOW (~10 行 validator) |
| **何时启动** | D.3 跑完后 cat-4 仍有 ≥1 条 seasonal_* fail，说明 LLM 系统性不照 Constraint 17 magnitude 公式——再加 validator 兜底 |
| **风险** | "silently pass on LLM mistake" 违反 transparency；只在 prompt-side 路彻底失败时才用 |

---

## 5. Tier 4 — Accepted（不修）

### ⑧ M1 ratio operator straggler

| 字段 | 内容 |
|---|---|
| **Status** | Accepted — 已识别 / 不修 |
| **主文档** | [`mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md`](mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md) |
| **失败模式** | LLM 公式里有 `enrollment / faculty` 除法算子，除法引入的结构方差不在 LLM noise sigma 声明范围内，Loop A calibration 校到 sensible ceiling 后仍残留 ~0.77 ratio |
| **暴露 failure** | 1 条 cat-3 baseline (`agpds_503613ba96::residual_student_faculty_ratio`)；cat-3 D.2 上 LLM 自修了公式，**已自然消失** |
| **不修的理由** | 单条长尾，与 Phase C reversal 同源；若 production 出现率 > 30% 或单 scenario 多条 ratio measure 同时残留再升级 |
| **升级条件** | 见 [M1_RATIO_OPERATOR_STRAGGLER §7](mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md) |

---

## 6. 决策原则速查

下次拾起新 deferred 时按这个流程做分类：

```
                       新观测到一类失败
                              │
                              ▼
              是已有 mechanism 的换皮吗？
                ┌─────────────┴─────────────┐
                ▼ yes                       ▼ no
        归入现有 MECHANISM doc       新 mechanism 候选
        (e.g., MECHANISM_6 §6.x)              │
                                              ▼
                              跨 ≥2 batch 重现 OR 单 batch ≥3 case?
                                ┌─────────────┴─────────────┐
                                ▼ yes                       ▼ no
                       升级 Candidate → Deferred       保持 "可能机制"
                       写 MECHANISM_N_DEEP_DIVE        留待样本累积
                                │
                                ▼
                       hand-trace 根因 → 候选修复 → BACKLOG.md 加 Tier 1
```

修复路径的责任分层（mirror Phase A/B/D 经验）：

| 失败根因层 | 修复路径 | 例子 |
|---|---|---|
| validator 在统计学没 power 的 regime 上误报 | validator-side skip / 阈值 | Phase A Wald, Phase B degen-skip, Path D KS<30 |
| LLM 缺乏 validator 验证规则的认知 | prompt-side Constraint | Phase D Constraint 17, D.2 row-count |
| LLM 公式骨架本身错（formula sign/上游共享）| LLM 重写公式（最重）| Phase C, M1 ratio straggler |
| LLM 跨多个 declaration 间的一致性漏洞 | prompt-side Constraint + validator detail 互补 | M7 marginal×group_dep, M8 param_model cell |

---

## 7. 已完成 / 归档

| 日期 | 事件 | 主 commit/doc |
|---|---|---|
| 2026-05-14 | Phase A 雏形 + Loop A in-loop sigma calibration | `4a1a04d` 系列 |
| 2026-05-20 | Path D 实施（KS n<30 + Bonferroni + aggregate + Constraint 13）| `a7602e6` |
| 2026-05-21 | Phase A 实施完成（n-aware Wald CI）| `50098aa` `e9de06f` `c5561be` |
| 2026-05-21 | Phase B 实施完成（ORTHOGONAL_MIN_DIM=2 strict-degenerate skip）| `1719856` |
| 2026-05-21 | Phase D 实施完成（Constraint 17 + validator detail）| `38c99e8` `4a68905` |
| 2026-05-21 | Phase D.2 实施完成（row-count guardrail）| `fad9d8b` `a4350b0` |
| 2026-05-21 | **本 BACKLOG.md 起草** | (this commit) |
