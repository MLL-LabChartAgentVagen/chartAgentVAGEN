# Validation soft-warning persistence (Stage 2 / Loop B)

Phase 2 Loop B (`generate_with_validation`) is deterministic and does not call
the LLM: after a validation failure it adjusts engine parameters (`widen_variance`,
`reshuffle_pair`, `amplify_magnitude`) and retries up to three times. If the
final attempt still fails, the scenario is **soft-failed**: the produced
`(DataFrame, schema_metadata, ValidationReport)` is kept, not discarded.

Previously, those soft warnings only surfaced through `logger.warning(...)` in
[agpds_pipeline.py:362](../agpds_pipeline.py#L362) — once a batch finished,
nothing on disk recorded which scenarios had passed validation and which had
shipped with a red flag. This doc describes the persistence layer added to
close that gap.

---

## 1. What `agpds_execute.py` now persists

For every scenario whose worker returns `status == "ok"`, Stage 2 writes
three artifacts beyond the existing CSV / schema / chart files:

| Path (under `--output-dir`)             | Content                                             | Granularity        |
|-----------------------------------------|-----------------------------------------------------|--------------------|
| `validation/{gen_id}_report.json`       | Full `ValidationReport` — **all checks**, passed and failed (via `dataclasses.asdict`). | per scenario       |
| `charts/{gen_id}.json` (existing file)  | Adds the `validation_report_path` key cross-referencing the per-scenario report. | per scenario       |
| `validation_summary.json`               | Array of `{generation_id, all_passed, failures: [{name, detail}, …]}`, one entry per scenario that ran. | per batch          |

Soft-failed scenarios are **never dropped**: their CSV, schema, chart record,
and validation report are all written. The soft-fail status is now recoverable
from disk by checking `all_passed` in either the per-scenario report
(`any(not c["passed"] for c in r["checks"])`) or the batch summary.

`ValidationReport`/`Check` are plain `@dataclass` objects (defined in
[types.py:235](phase_2/types.py#L235)), so no custom serializer is needed —
`dataclasses.asdict` covers them.

---

## 2. Output layout (Stage 2)

```
output/agpds/<batch>/
├── declarations/{gen_id}.json
├── manifest.jsonl
├── master_tables/{gen_id}.csv
├── schemas/{gen_id}_metadata.json
├── charts/{gen_id}.json                  ← now includes "validation_report_path"
├── scenarios/{gen_id}_scenario.json
├── validation/{gen_id}_report.json       ← new — full ValidationReport
├── charts.json                           ← unchanged batch index
└── validation_summary.json               ← new — batch-level red-flag list
```

---

## 3. Console summary

The final summary line is now three-way and the per-scenario follow-ups
distinguish soft-fail from worker error:

```
[hh:mm:ss] Stage 2 complete: P passed / S soft-failed / E errored.
[hh:mm:ss] Wrote batch index: …/charts.json
[hh:mm:ss] Wrote validation summary: …/validation_summary.json
[hh:mm:ss]   ~ {gen_id}: N check failure(s)   ← soft-failed (data written, red flag)
[hh:mm:ss]   ! {gen_id}: {ExceptionType}: …    ← errored (worker raised, no data)
```

Counts are defined as:
- `passed`      = `status == "ok"` and `validation_passed`
- `soft_failed` = `status == "ok"` and not `validation_passed`
- `errored`     = `status != "ok"` (Loop B exhausted or worker crash)

Previously, the `failed` count only included `errored`; soft-failed scenarios
were silently counted as `succeeded`.

---

## 4. How to consume the artifacts

### 4.1 Read one scenario's full report

```python
import json
gen_id = "agpds_20260425_213836_ad209e"
with open(f"output/agpds/<batch>/validation/{gen_id}_report.json") as f:
    report = json.load(f)
# report = {"checks": [{"name": ..., "passed": bool, "detail": str|None}, ...]}
passed = [c for c in report["checks"] if c["passed"]]
failed = [c for c in report["checks"] if not c["passed"]]
```

`check.name` carries the implicit level:
- `row_count`, `cardinality_*`, `column_*` — L1 structural
- `ks_*`, `residual_*`, `marginal_*`, `group_dep_*` — L2 statistical
- `outlier_*`, `trend_*`, `seasonal_*`, `convergence_*`, `dominance_*` — L3 pattern

### 4.2 Find all red-flagged scenarios in a batch

```python
import json
with open("output/agpds/<batch>/validation_summary.json") as f:
    summary = json.load(f)
flagged = [e for e in summary if not e["all_passed"]]
for e in flagged:
    print(e["generation_id"], len(e["failures"]))
```

### 4.3 Navigate from chart record to its report

```python
with open("output/agpds/<batch>/charts/agpds_….json") as f:
    chart = json.load(f)
report_path = chart["validation_report_path"]   # "validation/agpds_….json"
```

Phase 3 consumers should treat `all_passed == False` scenarios as candidates
for filtering, down-weighting, or quarantining (e.g., excluding views whose
target column appears in a failed `ks_*` or `residual_*` check).

---

## 5. Determinism

Loop B is deterministic per `(declarations, base_seed)`, and `json.dump(...,
indent=2)` produces a fixed byte layout. Re-running
`python -m pipeline.agpds_execute` on the same input produces **byte-identical**
`validation/{gen_id}_report.json` files (verified by `diff -r` on a
5-scenario batch).

---

## 6. Files touched

| File                                                    | Change                                                                 |
|---------------------------------------------------------|------------------------------------------------------------------------|
| [agpds_runner.py:91-101](../agpds_runner.py#L91-L101)   | `_ensure_output_dirs` creates `validation/` and returns 5-tuple        |
| [agpds_runner.py:67](../agpds_runner.py#L67)            | `AGPDSRunner.save_results` destructures the new tuple (unused locally) |
| [agpds_runner.py:121-172](../agpds_runner.py#L121-L172) | `save_single_result` serialises `validation_report` via `asdict`, adds `validation_report_path` to result, excludes `validation_report` from `chart_record` |
| [agpds_execute.py:108-127](../agpds_execute.py#L108-L127) | `_execute_one` passes `val_report` into the save payload and returns `validation_failures` for the batch summary |
| [agpds_execute.py:192-225](../agpds_execute.py#L192-L225) | `main()` writes `validation_summary.json` and prints the 3-way + per-soft-fail summary |

No changes were required in
[phase_2/types.py](types.py),
[phase_2/validation/validator.py](validation/validator.py), or
[phase_2/validation/autofix.py](validation/autofix.py) — the existing dataclass
shapes were already sufficient.

---

## 7. Non-goals

- **Not changed**: Loop B retry semantics (`max_attempts=3`, the four override
  channels, mixture opt-out for `widen_variance`). Soft-failure is still
  defined by the validator, not by this persistence layer.
- **Not changed**: `charts.json` schema. Phase 3 consumers that already read
  the batch index will see new per-record fields (`validation_report_path`)
  but no removed fields.
- **No new dependencies.** Uses only `dataclasses.asdict`, which is already
  used in [serialization.py:35-37](serialization.py#L35-L37) for declarations
  export.
