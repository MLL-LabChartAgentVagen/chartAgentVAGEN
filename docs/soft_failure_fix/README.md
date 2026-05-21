# `docs/soft_failure_fix/` — 导航

Phase 2 soft-failure 分析、修复、子系统手册、批次实测的合集。本目录覆盖
**机制 1（复合方差）/ 机制 3（稀疏 cell KS）**的根因诊断、修复路径与端到端
验证。

---

## 🚦 你应该从哪进

| 你的场景 | 读这份 |
|---|---|
| 第一次接触、想 catch-up | [ANALYSIS.md](ANALYSIS.md) — 一页综述 |
| 想知道某条 `residual_*` / `ks_*` 失败属哪条机制 | [FAILURE_MECHANISMS.md](FAILURE_MECHANISMS.md) — 三机制 + Path A/B/C + 实测 |
| 想知道某条 `group_dep_*` / `marginal_*` 失败的根因 | [mechanisms/MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md](mechanisms/MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md) — 小样本 binomial 包络 + Phase A 修复 |
| 改 `pipeline/phase_2/orchestration/calibration.py` | [subsystems/SIGMA_CALIBRATION.md](subsystems/SIGMA_CALIBRATION.md) |
| 改 `pipeline/phase_2/validation/statistical.py` 里的 KS 部分 | [subsystems/PATH_D_KS_SPARSE_CELLS.md](subsystems/PATH_D_KS_SPARSE_CELLS.md) |
| 改 `pipeline/phase_2/validation/statistical.py` 里的 group_dep / marginal 阈值 | [mechanisms/MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md §4](mechanisms/MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md#4-解决方案n-aware-wald-95-ci-per-cell-child_level) |
| 改 Stage 2 持久化（`validation_summary.json`）| [subsystems/VALIDATION_PERSISTENCE.md](subsystems/VALIDATION_PERSISTENCE.md) |
| 改 Stage 1 skip 持久化（`skipped.jsonl`）| [subsystems/SKIP_PERSISTENCE.md](subsystems/SKIP_PERSISTENCE.md) |
| 审计 `output/agpds/pingyue-samples-openai-calibrated/` 这份批次 | [validation/OPENAI_VALIDATION.md](validation/OPENAI_VALIDATION.md) |
| 审计某条机制的统计证据 | [mechanisms/](mechanisms/) 下对应深度文档 |

---

## 📂 目录结构

```
docs/soft_failure_fix/
├── README.md                          ← 本文件
├── ANALYSIS.md                        🌐 入口：一页综述
├── FAILURE_MECHANISMS.md              🌐 入口：三机制全景
├── mechanisms/                        🔬 机制纵深
│   ├── MECHANISM_1_DEEP_DIVE.md         M1 复合方差 — 根因/算法/实测
│   ├── MECHANISM_3_DEEP_DIVE.md         M3 稀疏 cell — 根因/Path D/实测
│   ├── MECHANISM_4_PROPORTION_DRIFT_DEEP_DIVE.md  M4 小样本比例漂移误判 — 根因/Phase A/实测
│   └── M1_RATIO_OPERATOR_STRAGGLER.md   M1 在除法算子上的长尾分支
├── subsystems/                        🔧 子系统手册（改代码前读）
│   ├── SIGMA_CALIBRATION.md             Loop A in-loop sigma calibration
│   ├── PATH_D_KS_SPARSE_CELLS.md        KS n<30 + Bonferroni + aggregate
│   ├── VALIDATION_PERSISTENCE.md        Stage 2 验证持久化合约
│   └── SKIP_PERSISTENCE.md              Stage 1 skipped.jsonl wiring
├── validation/                        📋 批次实测记录
│   └── OPENAI_VALIDATION.md             openai-cal end-to-end + Path D rerun
└── archive/                           🗄 历史 / 已 superseded
    ├── 2026-05-14-stage1-sigma-calibration.md   原 TDD 实施 plan
    └── 2026-05-19-session-start-snapshot.md     session 恢复快照
```

---

## 🗺 机制 ↔ 修复 ↔ 验证 一图

```
机制 1 (M1)              复合方差盲区
  └─ 诊断：FAILURE_MECHANISMS.md §2 + mechanisms/MECHANISM_1_DEEP_DIVE.md
  └─ 修复：subsystems/SIGMA_CALIBRATION.md（Loop A in-loop sigma calibration）
  └─ 长尾：mechanisms/M1_RATIO_OPERATOR_STRAGGLER.md（除法算子分支）
  └─ 验证：validation/OPENAI_VALIDATION.md §3

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

非 M4 长尾（机制 5+）    orthogonal / seasonal / outlier / reversal
  └─ 当前状态：未归类 / 未修（Phase B/C/D 待启）
  └─ 见 FAILURE_MECHANISMS.md §7.2 / validation/OPENAI_VALIDATION.md §7.4
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
