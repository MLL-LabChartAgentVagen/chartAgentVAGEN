# Stage 1 Skip Persistence — `skipped.jsonl` wiring

> Companion to [VALIDATION_PERSISTENCE.md](VALIDATION_PERSISTENCE.md): that doc covers Stage 2 (Loop B soft-failure reports); this doc covers Stage 1 (Loop A skipped scenarios) — the symmetric persistence channel for scenarios that don't survive to Stage 2 at all.
>
> Tracked as [ANALYSIS.md §5.1](../ANALYSIS.md#5-未解决问题与下一步); landed 2026-05-19 (commits TBD).

---

## 1. TL;DR

| Before | After |
|---|---|
| `_save_skip_record` written 2026-05-14 but never called from production | Called from both `run_generation_batch` and `run_scenario_id_generation` |
| `generate_artifacts` raised `RuntimeError` on SkipResult; `except Exception` swallowed it into a log string | `generate_artifacts` returns `SkipResult` typed; batch runner branches on it and persists |
| `skipped.jsonl` never appeared in any batch directory | One JSON line per skipped scenario, with `generation_id` / `scenario_id` / `skip_reason` / `error_log` / `timestamp` |
| `_save_skip_record(output_dir, sr, gen_id)` — 3 args | `_save_skip_record(output_dir, sr)` — 2 args, gen_id read from `SkipResult.generation_id` |
| 376 tests | **378 tests** (+2 integration tests that would have caught the wiring gap) |

---

## 2. 前因后果

### 2.1 `_save_skip_record` 当时为什么被写

[2026-05-14-stage1-sigma-calibration.md](../archive/2026-05-14-stage1-sigma-calibration.md) 实施计划的 T5 任务（在 calibration 接入 retry_loop 的 T6 之前）写道：

> "New `_save_skip_record(output_dir, skip_result, gen_id, scenario_id)`; call when LLM returns `SkipResult`"

动机三条：

1. **可观测性**：T6 引入新失败种类 `skip_reason="calibration_unconverged"`（"代码跑通了，但 sigma 校不准"），跟原来的 `"exec_error"`（"代码跑不通"）行为本质不同，需要在 batch 输出里分开追踪。
2. **监控/复跑入口**：`skipped.jsonl` 是 batch 目录下唯一**机器可读**的跳过记录——便于 `grep skip_reason` 统计 calibration 收敛率，或写脚本批量复跑特定 reason 的 scenario。
3. **跟 Stage 2 持久化对偶**：commit `6893a36` 已让 Stage 2 写 `validation_summary.json` + per-scenario report；Stage 1 skip 没落盘是观测缺口。

### 2.2 commit 时间线

| 日期 | commit | 事件 |
|---|---|---|
| 2026-03-28 | `a542719` | `generate_artifacts` 初版写好 |
| **2026-04-22** | `d70f2d1` | 在 `generate_artifacts` 加 `if isinstance(loop_a, SkipResult): raise RuntimeError(...)`——*calibration 工作开始之前*。当时 SkipResult 只用于 exec-error，所有调用方把它当 fatal error 处理。`run_generation_batch` 的 `except Exception` 也是同期定的——批量跑时一个 scenario 报错不能中断别人，所以宽口径吞掉。 |
| **2026-05-14 T5** | `6c2e2bc` | `_save_skip_record` 函数 + `SkipResult.skip_reason` 字段 + 单元测试。**没有改任何调用链上游**。 |
| **2026-05-14 T6** | `4a1a04d` | calibration 接入 retry_loop，现在 SkipResult 会带 `skip_reason="calibration_unconverged"`。**也没回头改 `generate_artifacts` 的 raise-path**。 |
| **2026-05-19** | 本次 | 接入 `_save_skip_record` 到生产路径。 |

---

## 3. 未修复时的问题

### 3.1 调用链

```
run_generation_batch (agpds_generate.py:148-157)
    │
    ├─ try:
    │     stage1 = pipeline.generate_artifacts(category_id=...)  ── ① 内部 raise
    │     entry = _save_stage1_artifacts(...)
    │
    └─ except Exception as exc:                                   ── ② 宽口径吞
          _log(f"ERROR: Stage 1 failed ...")
          continue
```

`generate_artifacts` 内部（[agpds_pipeline.py:308-311](../../../pipeline/agpds_pipeline.py#L308)）：

```python
loop_a = run_loop_a(...)
if isinstance(loop_a, SkipResult):
    raise RuntimeError(
        f"Loop A exhausted all retries: {'; '.join(loop_a.error_log)}"
    )
```

### 3.2 信息损耗路径

1. **typed → string**：`generate_artifacts` 把 `SkipResult(scenario_id, error_log, skip_reason)` 退化成 `"Loop A exhausted all retries: ..."` 字符串塞进 `RuntimeError`。typed 字段 `skip_reason`、单独的 `scenario_id` 全丢了。
2. **string → log**：`run_generation_batch` 的 `except Exception` 把这条 RuntimeError 兜底，只 `_log(f"ERROR: Stage 1 failed for category {category_id}: {exc}")`。
3. **log → /dev/null**：log 里只剩 `ERROR: ... Loop A exhausted all retries: ...` 一行字符串。要想知道是 exec_error 还是 calibration_unconverged，得 regex log；要想知道是哪个 scenario_id，得 grep 上下文行。
4. **`skipped.jsonl` 文件从不出现**在任何 batch 目录里。`_save_skip_record` 在 production 永远不被调用——是 dead code。

### 3.3 为什么单元测试没抓到

`test_calibration.py::TestSaveSkipRecord`（commit `6c2e2bc` 引入）的形式是：

```python
def test_appends_jsonl_with_skip_metadata(self, tmp_path):
    sr = SkipResult(scenario_id="dom_001/k=2", ..., skip_reason="calibration_unconverged")
    _save_skip_record(str(tmp_path), sr, gen_id="agpds_abc123")
    assert (tmp_path / "skipped.jsonl").exists()
```

它**直接调函数**验证落盘逻辑，**完全绕过调用链**——没有覆盖 `run_generation_batch → generate_artifacts → run_loop_a → SkipResult` 这条真实路径。是典型的 **TDD 边界遗漏**：T5 把 helper 和单测做完，T6 把 retry_loop 改完，但没人去回头检查"中间 `generate_artifacts` 的 raise 是否需要换成持久化"。

---

## 4. 修复方案

### 4.1 三个设计决策

| 决策 | 备选 | 选择理由 |
|---|---|---|
| **只改 `generate_artifacts`，不改 `execute_artifact`** | 两个都改，对称设计 | `execute_artifact`（Stage 2 SkipResult）只被 `run_single` 调用，不在 batch 持久化关键路径上。Loop B exhaustion 不需要 `skipped.jsonl` 落地。最小改动面。 |
| **`run_single` 保持 raise RuntimeError** | run_single 也返回 SkipResult | `run_single` 的契约是"给我一个完整 bundle"，skip = 失败；它的调用方 `agpds_runner.py` 也没 SkipResult 处理逻辑。在 run_single 里把 SkipResult 转回 RuntimeError，保留 in-process 路径的旧异常语义。 |
| **`SkipResult.generation_id` 加字段 + `_save_skip_record` 签名清理为 2 参** | 保持 3 参，gen_id 单独传 | `gen_id` 已经在 `SkipResult` 里就是把"属于 SkipResult 的元数据"放到 SkipResult 里——更干净，避免"同一信息在 dataclass 和 参数里都有"的冗余。代价是同步更新 `TestSaveSkipRecord` 的两次调用，可接受。 |

### 4.2 改动一览

| 文件 | 变化 | 内容 |
|---|---|---|
| [exceptions.py](../../../pipeline/phase_2/exceptions.py) | +7 行 | `SkipResult` dataclass 加 `generation_id: str = ""` 字段 + 文档 |
| [agpds_pipeline.py](../../../pipeline/agpds_pipeline.py) | +20/-4 行 | `generate_artifacts` 签名 `Dict \| SkipResult`，SkipResult 路径 `loop_a.generation_id = gen_id` 后 `return loop_a`；`run_single` 加 `isinstance(stage1, SkipResult)` guard 转 RuntimeError |
| [agpds_generate.py](../../../pipeline/agpds_generate.py) | +24/-4 行 | 加 `SkipResult` import；`_save_skip_record` 签名清理为 `(output_dir, skip_result)`；`run_scenario_id_generation` + `run_generation_batch` 在 `generate_artifacts` 后加 `isinstance` 分支 → 写 `skipped.jsonl` + log `SKIP` + `continue`/`return []` |
| [test_calibration.py](../../../pipeline/phase_2/tests/modular/test_calibration.py) | +62/-3 行 | 更新 `TestSaveSkipRecord` 用新签名；新增 `TestRunGenerationBatchPersistsSkipped`（2 个集成测试，覆盖 batch + scenario_id 两条路径） |
| [ANALYSIS.md](../ANALYSIS.md) | §5.1 | 状态翻成"已修" |

### 4.3 关键代码片段

**`AGPDSPipeline.generate_artifacts`**（[agpds_pipeline.py:273-340](../../../pipeline/agpds_pipeline.py#L273)）：

```python
def generate_artifacts(self, *, ...) -> Dict[str, Any] | SkipResult:
    ...
    loop_a = run_loop_a(...)
    if isinstance(loop_a, SkipResult):
        loop_a.generation_id = gen_id
        logger.info(
            f"[{gen_id}] Loop A skipped (reason={loop_a.skip_reason!r}); "
            f"returning SkipResult to caller for persistence."
        )
        return loop_a
    ...
```

**`run_generation_batch` 的分支**（[agpds_generate.py:153-167](../../../pipeline/agpds_generate.py#L153)）：

```python
stage1 = pipeline.generate_artifacts(category_id=category_id)
if isinstance(stage1, SkipResult):
    _save_skip_record(output_dir, stage1)
    _log(
        f"  -> SKIP {stage1.scenario_id} "
        f"(reason={stage1.skip_reason}, gen_id={stage1.generation_id})"
    )
    continue
entry = _save_stage1_artifacts(output_dir, stage1, model, provider)
```

**`_save_skip_record` 清理后的签名**（[agpds_generate.py:92-113](../../../pipeline/agpds_generate.py#L92)）：

```python
def _save_skip_record(
    output_dir: str,
    skip_result: SkipResult,
) -> None:
    record = {
        "generation_id": skip_result.generation_id,
        "scenario_id": skip_result.scenario_id,
        "skip_reason": skip_result.skip_reason,
        "error_log": list(skip_result.error_log),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    ...
```

### 4.4 新增的集成测试

这是本次修复**最有价值**的部分——锁死 wiring。`TestRunGenerationBatchPersistsSkipped` mock 掉 `generate_artifacts` 直接返回 SkipResult，断言 `skipped.jsonl` 实际出现在 batch 目录里：

```python
def test_run_generation_batch_writes_skipped_jsonl_on_loop_a_skip(self, tmp_path):
    fake_pipeline = Mock()
    fake_pipeline.generate_artifacts.return_value = SkipResult(
        scenario_id="scn_42",
        generation_id="agpds_xyz",
        error_log=["calibration ratio 28.7x after 3 retries"],
        skip_reason="calibration_unconverged",
    )
    produced = run_generation_batch(
        fake_pipeline, [1], str(tmp_path), "gemini", "google",
    )
    assert produced == []
    skip_file = tmp_path / "skipped.jsonl"
    assert skip_file.exists()
    rec = json.loads(skip_file.read_text().splitlines()[0])
    assert rec["generation_id"] == "agpds_xyz"
    assert rec["skip_reason"] == "calibration_unconverged"
```

类似 fixture 给 `run_scenario_id_generation` 一份。**早一天写上这种测试，wiring 缺口就不会潜伏 5 天**——5 月 14 日 T5/T6 完工到 5 月 19 日修复之间。

---

## 5. 落盘格式

`output/agpds/<batch>/skipped.jsonl`，每行一个 JSON 对象：

```json
{
  "generation_id": "agpds_xyz",
  "scenario_id": "scn_42",
  "skip_reason": "calibration_unconverged",
  "error_log": [
    "Attempt 1: calibration ratio 28.7x",
    "Attempt 2: calibration ratio 12.4x",
    "Attempt 3: calibration ratio 5.9x"
  ],
  "timestamp": "2026-05-19T22:14:33"
}
```

**字段语义**：

| 字段 | 来源 | 用途 |
|---|---|---|
| `generation_id` | `AGPDSPipeline.generate_artifacts` stamp | 跟 success path 的 `manifest.jsonl` / `scripts/<gen_id>.py` / `declarations/<gen_id>.json` 用同一 ID — 失败的也保留路径定位能力 |
| `scenario_id` | `SkipResult.scenario_id`（来自 `run_loop_a`） | 复跑入口：`pipeline/agpds_generate.py --scenario-id <id>` |
| `skip_reason` | `"exec_error"` 或 `"calibration_unconverged"` | 区分代码错 vs 校准错；监控统计的主要分组键 |
| `error_log` | `SkipResult.error_log`，每次 retry 一条 | 失败诊断；包含 Loop A 内部 typed exception 的渲染输出 |
| `timestamp` | 写盘时刻 ISO8601 秒级 | 跨 batch 时间序列分析；用 ISO 是为了 `sort` 直接生效 |

---

## 6. 验证

```bash
# 1. 全模块测试集（regression safety）
pytest pipeline/phase_2/tests/modular -x -q
# 378 passed (was 376)

# 2. 本次新加的 2 个集成测试
pytest pipeline/phase_2/tests/modular/test_calibration.py::TestRunGenerationBatchPersistsSkipped -v
# 2 passed

# 3. pipeline 层 callers
pytest pipeline/tests -x -q --ignore=pipeline/tests/test_pipeline_e2e.py
# 12 passed

# 4. Acceptance gates
grep -rn '_save_skip_record(' pipeline/ | grep -v 'def _save_skip_record'
# 全部 2 参形式，无遗留 3 参

grep -rn 'raise RuntimeError.*Loop A exhausted' pipeline/
# 仅 agpds_pipeline.py:404 (run_single，按计划保留)
```

---

## 7. 当前状态

| 项 | 状态 |
|---|:-:|
| `_save_skip_record` 函数定义 | ✅ 存在并被生产代码调用 |
| `SkipResult.generation_id` 字段 | ✅ 加入并由 `generate_artifacts` stamp |
| `generate_artifacts` 返回 SkipResult（不再 raise） | ✅ |
| `run_generation_batch` 写 `skipped.jsonl` | ✅ 有集成测试覆盖 |
| `run_scenario_id_generation` 写 `skipped.jsonl` | ✅ 有集成测试覆盖 |
| `run_single` 旧 raise 语义 | ✅ 保留（in-process 调用方契约不变） |
| `execute_artifact`（Stage 2 SkipResult） | ⏸ 未改（不在 batch 持久化路径上） |
| 测试套件 | ✅ 378/378 pass |
| 在真实失败 scenario 上 smoke test | ⏸ 待做（mock 集成测试已覆盖 wiring 不变性；real-data smoke 需要一个能触发 `calibration_unconverged` 的 scenario） |

---

## 8. 教训

1. **TDD 锁单元、不锁 wiring**。T5 的 `TestSaveSkipRecord` 验证了函数本身，但绕过了调用链——所以 helper 是 dead code 这件事 5 天没被发现。新加的 `TestRunGenerationBatchPersistsSkipped` 是补这一层的：mock 上游，断言下游副作用。
2. **宽口径 `except` 是观测的敌人**。原代码 `except Exception` 把 typed SkipResult 退化成 log 字符串，丢掉了 reason / scenario_id 等字段。修复的本质是让 typed value 直接走到 persistence layer，不经过 string-roundtrip。
3. **TDD 任务序列里"上游消费方"经常被遗忘**。本次 T5 / T6 完成后，理想的 T7 应该是"接入 `_save_skip_record` 并 end-to-end 测一遍"——但实施计划里没有，所以没人去做。下次写实施计划时，"helper 上线"和"helper 被生产代码消费"应该是两个独立 task。
4. **冗余参数是被动迁移的信号**。原 `_save_skip_record(output_dir, sr, gen_id)` 把 `gen_id` 单独传，是 SkipResult 当时没 `generation_id` 字段的历史遗留。这次顺手清理，让 dataclass 自包含——少一个被动同步的参数。

---

## 9. 配套阅读

- [ANALYSIS.md](../ANALYSIS.md) §5.1 — 之前的 known-issue 标注（现已标记为已修）
- [VALIDATION_PERSISTENCE.md](VALIDATION_PERSISTENCE.md) — Stage 2 的对偶持久化层
- [SIGMA_CALIBRATION.md](../archive/SIGMA_CALIBRATION.md) — calibration 模块技术参考（`skip_reason="calibration_unconverged"` 的来源）
- [2026-05-14-stage1-sigma-calibration.md](../archive/2026-05-14-stage1-sigma-calibration.md) — calibration 原实施计划（T5/T6 出处）
