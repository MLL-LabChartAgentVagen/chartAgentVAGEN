# `docs/soft_failure_fix/` — 导航

Phase 2 soft-failure 分析、修复、子系统手册、批次实测的合集。本目录覆盖
**机制 1（复合方差）/ 机制 3（稀疏 cell KS）**的根因诊断、修复路径与端到端
验证。

---

## 🚦 你应该从哪进

| 你的场景 | 读这份 |
|---|---|
| 第一次接触、想 catch-up | [ANALYSIS.md](ANALYSIS.md) — 一页综述 |
| **想知道下一步该修什么 / 还有哪些 deferred items** | [**BACKLOG.md**](BACKLOG.md) — **deferred queue + 推荐顺序**（拾起新 session 的入口）|
| 想知道某条 `residual_*` / `ks_*` 失败属哪条机制 | [FAILURE_MECHANISMS.md](FAILURE_MECHANISMS.md) — 三机制 + Path A/B/C + 实测 |
| **想知道 M1 `residual_*` 失败的真因（当前权威）** | [**mechanisms/M1_RESIDUAL_RECONCILIATION.md**](mechanisms/M1_RESIDUAL_RECONCILIATION.md) — pattern 污染（非乘积方差）；calibration 已禁用 |
| 想知道某条 `group_dep_*` / `marginal_*` 失败的根因 | [mechanisms/MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md](mechanisms/MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md) — 小样本 binomial 包络 + Phase A 修复 |
| 想知道某条 `orthogonal_*` 失败的根因 | [mechanisms/MECHANISM_5_ORTHOGONAL_DEGENERACY_DEEP_DIVE.md](mechanisms/MECHANISM_5_ORTHOGONAL_DEGENERACY_DEEP_DIVE.md) — 退化 contingency table + Phase B 修复 |
| 想知道某条 `seasonal_*` 失败的根因 | [mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md](mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md) — 季节振幅 vs baseline_std + Phase D Constraint 17 |
| 想拾起 Phase D.3（realized z << expected z；6dbb/ac54 实测）| [mechanisms/M6_PHASE_D3_REALIZED_Z_GAP.md](mechanisms/M6_PHASE_D3_REALIZED_Z_GAP.md) — **DEFERRED**，等候新 session |
| 看 calibration 历史设计（**已禁用 / 已归档**）| [archive/SIGMA_CALIBRATION.md](archive/SIGMA_CALIBRATION.md) |
| 改 `pipeline/phase_2/validation/statistical.py` 里的 KS 部分 | [subsystems/PATH_D_KS_SPARSE_CELLS.md](subsystems/PATH_D_KS_SPARSE_CELLS.md) |
| 改 `pipeline/phase_2/validation/statistical.py` 里的 group_dep / marginal 阈值 | [mechanisms/MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md §4](mechanisms/MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md#4-解决方案n-aware-wald-95-ci-per-cell-child_level) |
| 改 Stage 2 持久化（`validation_summary.json`）| [subsystems/VALIDATION_PERSISTENCE.md](subsystems/VALIDATION_PERSISTENCE.md) |
| 改 Stage 1 skip 持久化（`skipped.jsonl`）| [subsystems/SKIP_PERSISTENCE.md](subsystems/SKIP_PERSISTENCE.md) |
| 改 `declarations_from_json` / 排查整数分类列 int-key 往返 bug | [subsystems/SERIALIZATION_INT_KEY_ROUNDTRIP.md](subsystems/SERIALIZATION_INT_KEY_ROUNDTRIP.md) |
| 审计 `output/agpds/pingyue-samples-openai-calibrated/` 这份批次 | [validation/OPENAI_VALIDATION.md](validation/OPENAI_VALIDATION.md) |
| 审计某条机制的统计证据 | [mechanisms/](mechanisms/) 下对应深度文档 |

---

## 📂 目录结构

```
docs/soft_failure_fix/
├── README.md                          ← 本文件
├── BACKLOG.md                         📋 入口：deferred queue + 推荐顺序
├── ANALYSIS.md                        🌐 入口：一页综述
├── FAILURE_MECHANISMS.md              🌐 入口：三机制全景
├── GENERATION_FLOW_AND_CELLS.md       📖 背景：什么是 cell（M3 配套）
├── KS_N30_MEASUREMENT_2026-05-31.md   📊 KS n<30 全量普查（实测数据）
├── mechanisms/                        🔬 机制纵深
│   ├── M1_RESIDUAL_RECONCILIATION.md    ★ M1 当前权威：真因=pattern 污染（非乘积方差）
│   ├── M1_RATIO_OPERATOR_STRAGGLER.md   M1 在除法算子上的长尾分支
│   ├── MECHANISM_3_DEEP_DIVE.md         M3 稀疏 cell — 诊断/实测（修复见 PATH_D）
│   ├── MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md  M4 小样本比例漂移误判 — 根因/Phase A/实测
│   ├── MECHANISM_5_ORTHOGONAL_DEGENERACY_DEEP_DIVE.md  M5 正交声明在退化列上误判 — 根因/Phase B/实测
│   ├── MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md  M6 季节振幅未对齐 baseline 噪声 — Constraint 17/实测
│   └── M6_PHASE_D3_REALIZED_Z_GAP.md       M6 子机制：realized z << expected z（Phase D.3 候选，**未修**）
├── subsystems/                        🔧 子系统手册（改代码前读）
│   ├── PATH_D_KS_SPARSE_CELLS.md        KS n<30 + Bonferroni + aggregate（M3 修复）
│   ├── SERIALIZATION_INT_KEY_ROUNDTRIP.md  int-key dict JSON 往返归一修复
│   ├── VALIDATION_PERSISTENCE.md        Stage 2 验证持久化合约
│   └── SKIP_PERSISTENCE.md              Stage 1 skipped.jsonl wiring
├── validation/                        📋 批次实测记录
│   ├── OPENAI_VALIDATION.md             openai-cal end-to-end + Path D rerun
│   └── PINGYUE_OPENAI_CAL_ANALYSIS.md   per-scenario 诊断（M4/M5/M6 起点）
└── archive/                           🗄 历史 / 已 superseded
    ├── MECHANISM_1_DEEP_DIVE.md         M1 旧叙事（乘积方差→校准，已被证伪）
    ├── SIGMA_CALIBRATION.md             Loop A sigma calibration（已禁用）
    ├── 2026-05-14-stage1-sigma-calibration.md   原 TDD 实施 plan
    └── 2026-05-19-session-start-snapshot.md     session 恢复快照
```

---

## 🗺 机制 ↔ 修复 ↔ 验证 一图

```
机制 1 (M1)              residual_* 膨胀（真因 = Phase γ pattern 污染，非乘积方差）
  └─ 真因（当前权威）：mechanisms/M1_RESIDUAL_RECONCILIATION.md
  └─ 真修复：T9 patterns 修复（pipeline.py:287 `patterns=patterns`，让 P3-8 排净 pattern 行）
  └─ 旧叙事（已证伪 / 已归档）：archive/MECHANISM_1_DEEP_DIVE.md + archive/SIGMA_CALIBRATION.md（calibration 已禁用）
  └─ 长尾：mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md（除法算子分支）
  └─ 历史叙事/实测：FAILURE_MECHANISMS.md §2（含更正 banner）

机制 2 (M2a/M2b)         联合分布盲区
  └─ 诊断：FAILURE_MECHANISMS.md §3
  └─ 修复：Path A (prompt Constraint 11/12) + Path B/C (typed exceptions)
  └─ 验证：validation/OPENAI_VALIDATION.md §2 + §5

机制 3 (M3)              稀疏 cell KS 过敏
  └─ 诊断：FAILURE_MECHANISMS.md §4 + mechanisms/MECHANISM_3_DEEP_DIVE.md
  └─ 修复：subsystems/PATH_D_KS_SPARSE_CELLS.md（n<30 skip + Bonferroni + aggregate + Constraint 13）
  └─ 验证：validation/OPENAI_VALIDATION.md §7

机制 4 (M4)              小样本比例漂移误判（group_dep_* / marginal_*）
  └─ 诊断：validation/PINGYUE_OPENAI_CAL_ANALYSIS.md §6 + mechanisms/MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md
  └─ 修复：Phase A — n-aware Wald 95% CI per (cell, child_level) + n<10 skip
  └─ 验证：MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md §5（7 → 0, 13 → 6, 0 regressions）

机制 5 (M5)              正交声明在退化列上误判（orthogonal_*）
  └─ 诊断：validation/PINGYUE_OPENAI_CAL_ANALYSIS.md §4.2 + mechanisms/MECHANISM_5_ORTHOGONAL_DEGENERACY_DEEP_DIVE.md
  └─ 修复：Phase B — strict min(shape)<2 skip（ORTHOGONAL_MIN_DIM=2）
  └─ 验证：MECHANISM_5_ORTHOGONAL_DEGENERACY_DEEP_DIVE.md §5（3 → 0, 6 → 3, 6/10 → 8/10, 0 regressions）

机制 6 (M6)              季节振幅未对齐 baseline 噪声（seasonal_*）
  └─ 诊断：validation/PINGYUE_OPENAI_CAL_ANALYSIS.md §3.1 + mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md
  └─ 修复：Phase D — Constraint 17 prompt（amplitude vs baseline_std）+ validator fail-detail enrichment
  └─ 修复：Phase D.2 — Constraint 17 row-count guardrail sub-clause（避免 anomaly_window × target 0-row → PatternInjectionError）
  └─ 验证（cat-3）：MECHANISM_6 §5（seasonal_* 1 → 0；D.2 进一步把 D 时的 e9c4 hard error 修掉）
  └─ 验证（cat-4 stress test）：MECHANISM_6 §5.5（seasonal_* 8 → 2，passing 1/10 → 6/10，0 PatternInjectionError）

非 M6 长尾（机制 7+ / Phase C/D.3/D.4 等）   待修 queue
  └─ 完整列表 + 推荐顺序：[BACKLOG.md](BACKLOG.md)
  └─ Tier 1 (immediate)：Phase D.3 (realized z << expected z) — 设计完毕
  └─ Tier 2 (mechanism 候选)：M8 (param_model cell mis-fit) / M7 (marginal × group_dep) / M9 (outlier z_score)
  └─ Tier 3 (高成本)：Phase C (reversal_*) / D.4 (其他 pattern row-count) / D.1 (validator 兜底)
  └─ Tier 4 (accepted)：M1 ratio straggler — 不修
```

---

## ⏱ 时间线

| 日期 | 事件 | 关键 commit / doc |
|---|---|---|
| 2026-05-13 | 第一批 `pingyue-samples-openai-v1` 暴露 0/10 passed | — |
| 2026-05-14 | Stage 1 sigma calibration TDD plan 起草 | archive/2026-05-14-... |
| 2026-05-14 | Path A + Path B + Path C 三路修复落地 | (early commits) |
| 2026-05-14 | Loop A in-loop sigma calibration 实现 | `4a1a04d` `eb3619d` `ff9bf09` `0faf87f` |
| 2026-05-19 | `_save_skip_record` wiring 修复（生产从未被调用过的 bug）| `6c2e2bc` |
| 2026-05-20 | `pipeline.py:281` patterns plumbing bug 修复 → M1 真闭合 | `b16525e` |
| 2026-05-20 | Path D 实施（KS n<30 + Bonferroni + aggregate + Constraint 13）| `a7602e6` |
| 2026-05-20 | M1 ratio-operator 长尾在 openai-cal 上识别 | (uncommitted)|
| 2026-05-20 | Path D 在 openai-cal 验证 `ks_*` 39→0 | (uncommitted)|
| 2026-05-21 | Phase A 实施（n-aware Wald CI for group_dep / marginal）| `50098aa` `e9de06f` `c5561be` |
| 2026-05-21 | Phase A 在 openai-cal 验证 `group_dep_*` 6→0, `marginal_*` 1→0, total 13→6, 0 regressions | `MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md` §5 |
| 2026-05-21 | Phase B 实施（`ORTHOGONAL_MIN_DIM=2` strict-degenerate skip）| (Phase B commit) |
| 2026-05-21 | Phase B 在 openai-cal 验证 `orthogonal_*` 3→0, total 6→3, 6/10→8/10 passing, 0 regressions | `MECHANISM_5_ORTHOGONAL_DEGENERACY_DEEP_DIVE.md` §5 |
| 2026-05-21 | Phase D 实施 Task 1（validator detail enrichment：`declared_magnitude` + `required_magnitude_at_threshold`）| `38c99e8` |
| 2026-05-21 | Phase D 实施 Task 2（Constraint 17 — amplitude vs baseline_std）| `4a68905` |
| 2026-05-21 | Phase D LLM regen 在 openai-cal 验证 `seasonal_*` 1→0 ✓（14b7 切到 trend_break），但 LLM regen variance 让 `reversal_*` 1→3（Phase C scope），1 hard PatternInjectionError 暴露 | `pingyue-samples-openai-calibrated-pathD-llm/` |
| 2026-05-21 | MECHANISM_6 首版定稿 | `73767d5` |
| 2026-05-21 | Phase D.2 Constraint 17 row-count guardrail prompt 添加 | `fad9d8b` |
| 2026-05-21 | Phase D.2 tests landed | `a4350b0` |
| 2026-05-21 | Phase D.2 cat-3 LLM regen：e9c4 hard error 1→0 ✓；LLM 在 cat-3 上完全 abandon seasonal_anomaly（10 个 declarations 0 个 seasonal）| `pingyue-samples-openai-calibrated-pathD2-llm/` |
| 2026-05-21 | Phase D.2 cat-4 stress test：8 baseline seasonal failures 中 6 个主动切到 trend_break，`seasonal_*` 8→2，passing 1/10→6/10，0 PatternInjectionError | `pingyue-samples-openai-catagory4-pathD2-llm/` |
| 2026-05-21 | MECHANISM_6 D.2 增量定稿 | (this commit) |
| 2026-05-30 | **M1 真因反转**：代码+git 对账证实 residual validator 减实测因子、乘积方差不进 residual；真因 = Phase γ pattern 污染。Loop A sigma 校准 + Path A 约束 11 **可逆禁用**（建立干净 baseline） | `M1_RESIDUAL_RECONCILIATION.md` |
| 2026-05-31 | `residual_source_dump.py` 确定性诊断锁定机制（合成 + 90-scenario 复核）；整数分类列 group-dep **int-key 往返 bug** 修复 + 回归测试 | `SERIALIZATION_INT_KEY_ROUNDTRIP.md` |
| 2026-05-31 | docs 精简：M1 旧叙事 + calibration 手册归档至 `archive/`，M3 §4 / ANALYSIS 去重，索引刷新 | (this change) |
