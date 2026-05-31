# 2026-05-19 Session Start — Soft Failure Fix 进度快照

> 本文档是 2026-05-19 session 开始时 Claude 对 `docs/soft_failure_fix/` 全部文档的整理摘要——**修复 `_save_skip_record` wiring 之前**的状态快照。保留作为历史参考。
>
> 当前最新状态请看 [ANALYSIS.md](../ANALYSIS.md)。本次 session 内 §5.1（`_save_skip_record` 未接入）已修复，详见 [SKIP_PERSISTENCE.md](../subsystems/SKIP_PERSISTENCE.md)。

---

## 文件作用矩阵

| 文件 | 类型 | 角色 | 你现在该读它当作 |
|---|---|---|---|
| [ANALYSIS.md](../ANALYSIS.md) | 综述 | **唯一的入口文档**——一页内回答 "sigma 是什么 / soft failure 是什么 / 根因 / 修法 / 当前效果 / 未尽事项" | **catch-up 就读这一份** |
| [FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md) | 诊断 | 三条根因机制（复合方差盲区 / 联合分布盲区 / 稀疏 cell 脆弱性）+ Path A/B/C 修复路径 + 3-way/4-way 实测对比表 | 想深挖某条机制的统计证据时翻 |
| [SIGMA_CALIBRATION.md](../archive/SIGMA_CALIBRATION.md) | 技术参考 | calibration 子系统模块手册：架构图、算法、独立 retry budget 设计、T9 plumbing bug case study | 改 [calibration.py](../../../pipeline/phase_2/orchestration/calibration.py) 或 [retry_loop.py](../../../pipeline/phase_2/orchestration/retry_loop.py) 前翻 |
| [VALIDATION_PERSISTENCE.md](../subsystems/VALIDATION_PERSISTENCE.md) | 技术参考 | Stage 2 / Loop B 的持久化层——`validation_summary.json` + per-scenario report 的写盘合约 | 跟 §5.1 (`_save_skip_record` 接入) 直接相关 |
| [2026-05-14-stage1-sigma-calibration.md](2026-05-14-stage1-sigma-calibration.md) | 实施计划 | TDD 任务清单——calibration 模块当时是按这份 plan 拆 task 实施的，每个 task 有 checkbox | 历史档案；calibration 已实现，不用再读 |

---

## 已完成（按 ANALYSIS.md §0 + §5）

- 机制 1（复合方差盲区）根治：Loop A 内 LLM-in-the-loop sigma calibration（[calibration.py](../../../pipeline/phase_2/orchestration/calibration.py) + [retry_loop.py:200-510](../../../pipeline/phase_2/orchestration/retry_loop.py#L200)）
- Path A prompt 约束（[prompt.py:103-118](../../../pipeline/phase_2/orchestration/prompt.py#L103)）
- Path B `PatternInjectionError` 详化（[engine/patterns.py:47-63](../../../pipeline/phase_2/engine/patterns.py#L47)）
- Path C `KeyError → UndefinedEffectError`（[engine/measures.py:245-251](../../../pipeline/phase_2/engine/measures.py#L245)）
- T9 plumbing bug：[pipeline.py:281](../../../pipeline/phase_2/pipeline.py#L281) `patterns=patterns`（commit `b16525e`）
- 测试 355 → 376

**效果**：pingyue-samples 10 个：passed 0→4，residual_* 15→0，ks_* 76→11，total -81%

---

## 未完成（按优先级）

1. **[中] `_save_skip_record` 未接入**——函数和测试都在（[agpds_generate.py:88](../../../pipeline/agpds_generate.py#L88)），但 `generate_artifacts()` 拿到 `SkipResult` 只 `raise`，被 `run_generation_batch` 的 `except` 吞掉 → `skipped.jsonl` 实际没写盘。约 10 行修复。
2. **[中] 机制 3 未修**——剩 11 个 `ks_*` 是稀疏 cell 上 KS 过敏，不是机制 1 的尾巴。需 Path D（bonferroni 校正 / `n<30` skip KS），需要单独 plan。
3. **[中] Path B/C 在 openai 上端到端没验证**——gemini 跑没触发到这两条；要么 openai 重跑 -v3，要么人造 scenario 强触发。
4. **[低] 剩 6 个 soft-fail scenario 逐条剖析**——确认是机制 3 还是新模式。
5. **[Nitpicks]** `retry_loop.py` 里 `# IS-6 token-budget half` jargon 注释、`test_sandbox_format.py` empty-failures 断言收紧、`_save_skip_record` typing。

---

## Session 进展（2026-05-19）

| 项 | 状态 | 备注 |
|---|---|---|
| 1. `_save_skip_record` 未接入 | ✅ 已修 | 详见 [SKIP_PERSISTENCE.md](../subsystems/SKIP_PERSISTENCE.md)；测试 376 → 378 |
| 2. 机制 3（稀疏 cell + KS 过敏） | ⏸ 未动 | 需要 Path D 单独 plan |
| 3. Path B/C openai 端到端验证 | ⏸ 未动 | 需要 production 重跑 |
| 4. 剩 6 个 soft-fail 逐条剖析 | ⏸ 未动 | |
| 5. Nitpicks | 部分 | 5 里的 `_save_skip_record` typing 在 §1 修复时顺手清理；其余未动 |

本 session 还产出：

- [MECHANISM_1_DEEP_DIVE.md](../archive/MECHANISM_1_DEEP_DIVE.md) — 机制 1 根因 → 算法 → 实测的完整串联（含 pathA / pathA-calibrated 真实数据）
- [SKIP_PERSISTENCE.md](../subsystems/SKIP_PERSISTENCE.md) — `_save_skip_record` wiring 修复的前因后果 / 方案 / 结果
