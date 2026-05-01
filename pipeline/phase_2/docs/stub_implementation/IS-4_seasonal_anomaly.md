# IS-4 + DS-2 (`seasonal_anomaly`): Summary of Changes

Implements **IS-4** (`check_seasonal_anomaly` validator) and the
**`seasonal_anomaly` slice of DS-2** (`inject_seasonal_anomaly`
injector) from
[pipeline/phase_2/docs/stub_analysis/stub_gap_analysis.md](../stub_analysis/stub_gap_analysis.md)
§§ IS-4 and DS-2.

These two stubs ship as one atomic unit because the injector produces
the very signal the validator checks — IS-4 alone leaves a no-op
`passed=True` stub regardless of what the data shows; DS-2's
`seasonal_anomaly` alone is unverifiable.

After this change **all 6 spec pattern types** ride the full SDK gate →
injector → validator → prompt path. `seasonal_anomaly` was the last
deferred stub in the M1-NC-6 cluster; with it shipped, the
`NotImplementedError` branch in `inject_patterns` is gone and the M1-NC-6
TODO comments across the four files are deleted.

Algorithm decisions are locked in
[docs/stub_analysis/stub_blocker_decisions.md §IS-4 / §DS-2](../stub_analysis/stub_blocker_decisions.md):

- **Validator (IS-4):** interpretation **(a)** — window-vs-baseline
  z-score. Compute window mean/baseline mean+std on `pattern["col"]`
  using rows in/out of `params["anomaly_window"]`. Pass when
  `z = |window_mean − baseline_mean| / baseline_std ≥
  params.get("z_threshold", 1.5)`.
- **Injector (DS-2):** scale `pattern["col"]` values inside the
  anomaly window by `(1 + magnitude)` — mirrors `inject_trend_break`
  with a finite `[start, end]` mask instead of a single break point.
- **Params contract:** `anomaly_window` and `magnitude` are
  **SDK-required at declaration time** (`PATTERN_REQUIRED_PARAMS`).
  The validator additionally keeps a defensive "last 10% of temporal
  range" fallback for `anomaly_window` so it remains usable if the
  SDK gate is ever bypassed (e.g. patterns synthesised in a test
  without going through `sim.inject_pattern`).

## Schema (the contract added)

### Pattern declaration

```python
sim.inject_pattern(
    "seasonal_anomaly",
    target="<DataFrame query>",          # row subset whose in-window
                                         # values get scaled by
                                         # (1 + magnitude)
    col="<measure>",                     # measure to perturb
    params={
        "anomaly_window": [               # REQUIRED: [start, end]
            "YYYY-MM-DD", "YYYY-MM-DD",   #   date pair (inclusive)
        ],
        "magnitude": 0.5,                 # REQUIRED: multiplicative
                                          #   shift inside the window
        "z_threshold": 1.5,               # OPTIONAL: validator
                                          #   threshold (default 1.5)
    },
)
```

**Validator pass condition:**
`z = |window_mean − baseline_mean| / baseline_std ≥ z_threshold`,
where `window_mean` is the mean of `pattern["col"]` over rows whose
temporal value is inside `anomaly_window` and `baseline_mean` /
`baseline_std` are computed on rows outside the window. Graceful
`Check(passed=False, detail=…)` for: missing temporal/measure column,
empty window subset, baseline subset of size < 2, zero or
non-finite `baseline_std`, or unparseable temporal values when the
defensive fallback is used.

**Injector post-condition:** target rows whose temporal value falls in
`[anomaly_window[0], anomaly_window[1]]` are multiplicatively scaled by
`(1 + magnitude)`. Out-of-window target rows and all non-target rows
are left untouched.

## Files changed

### [pipeline/phase_2/sdk/relationships.py](../../sdk/relationships.py)

- Added `"seasonal_anomaly"` to `VALID_PATTERN_TYPES` (L29-32).
- Added
  `"seasonal_anomaly": frozenset({"anomaly_window", "magnitude"})`
  to `PATTERN_REQUIRED_PARAMS` (L57) with an inline comment recording
  the optional `z_threshold` and the defensive validator fallback.
- Deleted the `M1-NC-6` TODO comments above both blocks — no remaining
  deferred pattern types.

### [pipeline/phase_2/validation/pattern_checks.py](../../validation/pattern_checks.py)

- **Replaced stub `check_seasonal_anomaly`** (was L404-427, hard-coded
  `passed=True`) with the window-vs-baseline z-score validator
  (L404-513). Reuses existing helpers:
  - `_find_temporal_column(meta)` (L94-103)
- **Failure modes return `passed=False` with a descriptive `detail`**
  rather than raising — graceful for `ValidationReport` consumers
  (matches `check_convergence` / `check_dominance_shift` style):
  - Missing `temporal_col` from metadata
  - Required column missing from DataFrame
  - Defensive fallback hit but temporal column has no parseable values
  - `anomaly_window` matches no rows
  - Baseline subset (`len < 2`)
  - `baseline_std == 0` or non-finite (z-score undefined)
- **Defensive last-10% fallback for `anomaly_window`:** when
  `params["anomaly_window"]` is missing or malformed, the validator
  uses `[tmin + 0.9 * (tmax − tmin), tmax]`. Under normal flow this
  branch is unreachable — the SDK gate (`PATTERN_REQUIRED_PARAMS`)
  guarantees `anomaly_window` is present.
- **Uses `pd.to_datetime(..., errors="coerce")`** so unparseable
  temporal cells become `NaT` and are excluded from the in/out-window
  partition instead of crashing the validator.

### [pipeline/phase_2/engine/patterns.py](../../engine/patterns.py)

- **Replaced the `seasonal_anomaly` `NotImplementedError` branch** in
  `inject_patterns` (was L70-75) with an explicit dispatch routing to
  `inject_seasonal_anomaly(df, pattern, columns)`. After this edit
  `inject_patterns` covers all 6 spec types and has no
  `NotImplementedError` branches.
- **Added `inject_seasonal_anomaly`** at the end of the file. Signature
  `(df, pattern, columns)` mirrors all sibling injectors. Algorithm:
    1. Read `params["anomaly_window"]` and `params["magnitude"]`
       directly (SDK gate guarantees both).
    2. Resolve `temporal_col` from the column registry by scanning for
       `col_meta["type"] == "temporal"` (mirrors `inject_trend_break`
       L193-197). No temporal column → `PatternInjectionError`.
    3. `target_mask = df.eval(pattern["target"])`. Empty →
       `PatternInjectionError("zero rows")`.
    4. Skip-with-warning when `pattern["col"]` is missing from
       `df.columns` (measures may not be generated yet — same idiom
       as the other injectors).
    5. Parse `win_start`, `win_end` via `pd.to_datetime`; build
       `in_win = target_mask & (temporal >= win_start) & (temporal
       <= win_end)`. Empty → `PatternInjectionError("anomaly_window
       matches no target rows")`.
    6. `df.loc[in_win, col] = df.loc[in_win, col] * (1 + magnitude)`.
    7. `logger.debug(...)` summary.
- **Raises `PatternInjectionError`** for: no temporal column, empty
  `target` subset, or `anomaly_window` matching no target rows.

### [pipeline/phase_2/orchestration/prompt.py](../../orchestration/prompt.py)

- Updated the advertised `PATTERN_TYPES` line (L88) to include
  `"seasonal_anomaly"` — list now contains all 6 spec types.
- Deleted the `M1-NC-6` TODO comment that previously gated this entry.
- Added a one-shot example call (after the `convergence` example,
  before `return sim.generate()`) using the hospital scenario:

  ```python
  sim.inject_pattern("seasonal_anomaly",
      target="severity == 'Severe'",
      col="wait_minutes",
      params={"anomaly_window": ["2024-05-15", "2024-06-30"],
              "magnitude": 0.5})
  ```

  Tells the LLM that severe-case wait times spike during a
  late-spring/early-summer window — a narrative-coherent example
  that exercises both required params and leaves `z_threshold` at
  its default.

### [pipeline/phase_2/tests/modular/test_validation_pattern_checks_seasonal_anomaly.py](../../tests/modular/test_validation_pattern_checks_seasonal_anomaly.py)
**(new file)**

`TestCheckSeasonalAnomaly` — 8 stand-alone validator unit tests:

| Test | Fixture / Pattern | Expected |
|------|-------------------|----------|
| `test_anomalous_window_passes` | Window mean 10 vs baseline 5, σ=1 → z ≫ 1.5 | `passed=True`, detail contains `z=` |
| `test_stable_window_fails` | Window mean ≈ baseline mean | `passed=False` (z ≈ 0) |
| `test_empty_window_graceful_fail` | `anomaly_window=["2030-01-01", "2030-01-31"]` outside the data | `passed=False`, detail contains `matches no rows` |
| `test_missing_temporal_column_graceful_fail` | Meta has no `time` group | `passed=False`, detail mentions `temporal_col` |
| `test_constant_column_graceful_fail` | All values 5.0 → `baseline_std == 0` | `passed=False`, detail contains `Baseline std` |
| `test_custom_z_threshold_blocks_pass` | Modest shift (window=7, baseline=5); `z_threshold=1.5` passes, `z_threshold=50` fails | both verdicts honored |
| `test_default_window_uses_last_10_percent` | No `anomaly_window` in params; spike the trailing 10% of dates | `passed=True` (defensive fallback exercised) |
| `test_baseline_too_small_graceful_fail` | Window covers all but 1 row → baseline len < 2 | `passed=False`, detail contains `baseline rows` |

### [pipeline/phase_2/tests/modular/test_engine_patterns.py](../../tests/modular/test_engine_patterns.py)

Added `TestInjectSeasonalAnomaly` (5 tests),
`TestSeasonalAnomalyDeclaration` (4 tests), and
`TestAllSixPatternsIntegration` (1 test) at the end of the file,
mirroring the `convergence` test classes already there:

| Test | What it covers |
|------|----------------|
| `test_round_trip_passes_validator` | Full inject → validate cycle. Pre-injection validator fails (no anomaly); after `inject_seasonal_anomaly` the validator passes. |
| `test_out_of_window_values_unchanged` | Pre-window rows are byte-identical before/after injection (only in-window rows mutate). |
| `test_empty_target_raises` | `target="value > 99999"` → `PatternInjectionError("zero rows")`. |
| `test_window_matches_no_rows_raises` | `anomaly_window=["2030-…", "2030-…"]` → `PatternInjectionError("anomaly_window")`. |
| `test_missing_temporal_column_raises` | Column registry has no `temporal` entry → `PatternInjectionError("temporal column")`. |
| `test_valid_declaration_succeeds` | `sim.inject_pattern("seasonal_anomaly", …, anomaly_window=…, magnitude=…)` registers a spec with both params populated. |
| `test_missing_anomaly_window_raises` | Declaration without `anomaly_window` → `ValueError("anomaly_window")`. |
| `test_missing_magnitude_raises` | Declaration without `magnitude` → `ValueError("magnitude")`. |
| `test_sdk_constants_register_seasonal_anomaly` | `"seasonal_anomaly" in VALID_PATTERN_TYPES` and `PATTERN_REQUIRED_PARAMS["seasonal_anomaly"] == frozenset({"anomaly_window", "magnitude"})`. |
| `test_all_six_patterns_dispatch_without_error` (`TestAllSixPatternsIntegration`) | Builds a single pattern list with **all 6 types** (`outlier_entity`, `trend_break`, `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`) and calls `inject_patterns(df, patterns, columns, rng)`. Asserts dispatch coverage — no `NotImplementedError`, no `ValueError("Unknown pattern type")`. |

Test imports were updated to include `inject_patterns`,
`inject_seasonal_anomaly`, and `check_seasonal_anomaly` alongside the
existing pattern symbols.

## Verification

```bash
conda run -n chart pytest pipeline/phase_2/tests/ -x
# → 179 passed in 0.64s
```

The round-trip test (`test_round_trip_passes_validator` in
`TestInjectSeasonalAnomaly`) is the load-bearing one: it builds a
DataFrame whose May–Jun window mean ≈ baseline (validator fails), runs
the injector, then asserts `check_seasonal_anomaly(...).passed is True`.
End-to-end proof that injector and validator agree on what
`seasonal_anomaly` means.

The integration test (`test_all_six_patterns_dispatch_without_error`)
is the closure proof that this change retires the M1-NC-6 cluster: a
single `inject_patterns` call with all 6 types completes without
raising.

## Cleanup verification

```bash
grep -nE "M1-NC-6|seasonal_anomaly.*not yet implemented" \
  pipeline/phase_2/{sdk,validation,engine,orchestration}/*.py
# → no matches

grep -n "NotImplementedError" pipeline/phase_2/engine/patterns.py
# → no matches (the only remaining NotImplementedError in
#   sdk/relationships.py is for multi-column add_group_dependency,
#   unrelated to pattern injection)
```

## Dependency chain status (per stub_gap_analysis §DS-2)

- ✅ **`outlier_entity`, `trend_break`, `ranking_reversal`,
  `dominance_shift`, `convergence`** — shipped in prior steps.
- ✅ **`seasonal_anomaly`** — IS-4 validator and DS-2 injector
  implemented; SDK declarations of `seasonal_anomaly` no longer raise
  `ValueError("Unsupported pattern type")` and the engine no longer
  raises `NotImplementedError` for this type.

**M1-NC-6 cluster is fully resolved.** All 6 spec pattern types ship
end-to-end.
