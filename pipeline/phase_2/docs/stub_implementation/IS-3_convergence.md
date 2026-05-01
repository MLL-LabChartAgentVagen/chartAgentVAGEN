# IS-3 + DS-2 (`convergence`): Summary of Changes

Implements **IS-3** (`check_convergence` validator) and the
**`convergence` slice of DS-2** (`inject_convergence` injector) from
[pipeline/phase_2/docs/stub_analysis/stub_gap_analysis.md](../stub_analysis/stub_gap_analysis.md)
§§ IS-3 and DS-2.

These two stubs ship as one atomic unit because the injector produces
the very signal the validator checks — IS-3 alone leaves a no-op
`passed=True` stub regardless of what the data shows; DS-2's
`convergence` alone is unverifiable.

Algorithm decisions are locked in
[docs/stub_analysis/stub_blocker_decisions.md §IS-3 / §DS-2](../stub_analysis/stub_blocker_decisions.md):

- **Validator (IS-3):** interpretation **(b)** — variance of *per-entity
  means* decreases between an early period and a late period. Default
  split = temporal median (`tval.quantile(0.5)`); default reduction
  threshold = 30%. Pass condition:
  `(early_var − late_var) / early_var ≥ params.get("reduction", 0.3)`.
- **Injector (DS-2):** pull target rows toward `global_mean` over
  normalized time:
  `factor = clip(norm_t * pull_strength, 0, 1); val = val * (1 − factor) + global_mean * factor`.
  Default `pull_strength = 1.0` (full convergence at `t = tmax`).

This restores `convergence` end-to-end. The matching seasonal_anomaly
pair (IS-4 + the `seasonal_anomaly` slice of DS-2) remains the last
deferred stub in the M1-NC-6 cluster.

**Out of scope (still pending):** `seasonal_anomaly` injector and its
paired validator (IS-4) — they remain in the `NotImplementedError`
branch of [engine/patterns.py](../../engine/patterns.py) and as a
no-op stub in [validation/pattern_checks.py](../../validation/pattern_checks.py).

## Schema (the contract added)

### Pattern declaration

```python
sim.inject_pattern(
    "convergence",
    target="<DataFrame query>",          # row subset the injector blends
                                         # toward global_mean (typically
                                         # spans multiple entities — see
                                         # the note below)
    col="<measure>",                     # measure to blend
    params={
        "reduction": 0.3,                    # OPTIONAL: validator threshold
                                             #   (default 0.3)
        "pull_strength": 1.0,                # OPTIONAL: injector pull
                                             #   magnitude (default 1.0;
                                             #   clipped to [0, 1] after
                                             #   * norm_t)
        "split_point": "YYYY-MM-DD",         # OPTIONAL: validator's
                                             #   early/late split; default
                                             #   = temporal median
        "entity_col": "<categorical>",       # OPTIONAL: validator
                                             #   groupby column; fallback
                                             #   = first dim-group
                                             #   hierarchy root
    },
)
```

All params are optional — `convergence` is the only pattern type with
`PATTERN_REQUIRED_PARAMS["convergence"] == frozenset()`.

**Validator pass condition:** `(early_var − late_var) / early_var ≥
reduction`, where `early_var` and `late_var` are sample variances of
per-entity means computed on each side of the temporal split. Graceful
`Check(passed=False, detail=…)` for: < 2 entities per side, missing
columns, `early_var == 0` or non-finite.

**Injector post-condition:** target rows are blended toward `global_mean`
with a time-graded factor — late rows pull harder than early rows. For
the matching validator to pass, `target` should span multiple entities
(typically a temporal-only or severity-style filter). A single-entity
target collapses to no inter-group variance to compare and the validator
will fail.

## Decision: injector signature

The implementation note in the brief asked for
`inject_convergence(df, pattern, columns, meta)` — four args. The
implementation is **three args, `(df, pattern, columns)`**, matching
`inject_outlier_entity`, `inject_trend_break`, `inject_dominance_shift`,
and `inject_ranking_reversal`. Reasons:

- `inject_patterns` is called from
  [engine/generator.py:98](../../engine/generator.py#L98) and `meta` is
  not in scope at the dispatch site — metadata is built at L106-118,
  *after* pattern injection.
- The convergence algorithm only needs the temporal column, which is
  already discoverable in the `columns` registry by scanning for
  `col_meta["type"] == "temporal"` (the same idiom
  `inject_dominance_shift` uses at
  [engine/patterns.py:289-293](../../engine/patterns.py#L289-L293)).

Plumbing `meta` would have required reordering Phase γ vs the metadata
build, which is out of scope.

## Files changed

### [pipeline/phase_2/validation/pattern_checks.py](../../validation/pattern_checks.py)

- **Replaced stub `check_convergence`** (was L315-338, hard-coded
  `passed=True`) with the variance-of-per-entity-means reduction check
  (L315-401). Reuses existing helpers from IS-2:
  - `_find_temporal_column(meta)` (L94-103)
  - `_resolve_first_dim_root(meta)` (L106-119)
- **Failure modes return `passed=False` with a descriptive `detail`**
  rather than raising — graceful for `ValidationReport` consumers
  (matches `check_dominance_shift` style):
  - Missing `entity_col` or `temporal_col` from metadata
  - Required column missing from DataFrame
  - < 2 entities on either side of the split
  - `early_var == 0` or non-finite (reduction undefined)
- **Uses `pd.to_datetime(..., errors="coerce")`** so unparseable
  temporal cells become `NaT` and are excluded from the split
  comparison instead of crashing the validator.

### [pipeline/phase_2/engine/patterns.py](../../engine/patterns.py)

- **Pulled `"convergence"` out of the `NotImplementedError` tuple** in
  `inject_patterns` (L67-72) and added an explicit dispatch branch at
  L67-68 routing to the new
  `inject_convergence(df, pattern, columns)`. `seasonal_anomaly`
  remains in its own `NotImplementedError` branch (L70-75).
- **Added `inject_convergence`** (L507-637). Algorithm:
    1. Validate `params["pull_strength"] > 0` and finite (default 1.0)
       — else `PatternInjectionError` ("negative would push *away*
       from the mean").
    2. Resolve `temporal_col` from the column registry (mirrors
       `inject_trend_break` / `inject_dominance_shift`). No temporal
       column → `PatternInjectionError`.
    3. `target_mask = df.eval(pattern["target"])`. Empty → typed error
       (mirrors the existing pattern in `inject_outlier_entity`).
    4. Skip-with-warning when `pattern["col"]` is missing from
       `df.columns` (mirrors the `inject_outlier_entity` L126-132
       convention — measures may not be generated yet).
    5. `tval = pd.to_datetime(df[temporal_col], errors="coerce")`,
       drop NaT rows from the target index. All-NaT target subset →
       `PatternInjectionError`.
    6. Compute `tmin`, `tmax`, `span = tmax - tmin`. Zero-span temporal
       column → `PatternInjectionError`.
    7. Compute `global_mean = df[pattern["col"]].mean()`
       (pre-injection, since this function is the only mutator).
    8. Normalize: `norm_t = (tval - tmin) / span` (Series in `[0, 1]`).
    9. For valid target rows:
       `factor = clip(norm_t * pull_strength, 0, 1)`,
       `df[col] = df[col] * (1 − factor) + global_mean * factor`.
       Within-row blend: late rows pull harder than early rows.
   10. `logger.debug(...)` summary.
- **Raises `PatternInjectionError`** for: non-positive `pull_strength`,
  no temporal column, empty `target` subset, all target rows have
  unparseable temporal values, no parseable temporal values overall, or
  zero temporal span.

### [pipeline/phase_2/sdk/relationships.py](../../sdk/relationships.py)

- Added `"convergence"` to `VALID_PATTERN_TYPES` (L29-32).
- Added `"convergence": frozenset()` to `PATTERN_REQUIRED_PARAMS`
  (L51-55) with an inline comment listing the optional params
  (`split_point`, `entity_col`, `reduction`, `pull_strength`) and
  their defaults.
- Updated the `M1-NC-6` TODO comments to drop `"convergence"`, leaving
  only `seasonal_anomaly` as still-deferred.

### [pipeline/phase_2/orchestration/prompt.py](../../orchestration/prompt.py)

- Updated the advertised `PATTERN_TYPES` line (L90) to include
  `"convergence"`.
- Updated the matching `M1-NC-6` TODO comment.
- Added a one-shot example call (after the `dominance_shift` example,
  before `return sim.generate()`) using the hospital scenario:

  ```python
  sim.inject_pattern("convergence",
      target="severity == 'Severe'",
      col="wait_minutes",
      params={"reduction": 0.4})
  ```

  Tells the LLM that severe-case wait times across hospitals become
  more uniform over the observation window — a narrative-coherent
  example that exercises only the `reduction` param (the others all
  have safe defaults).

### [pipeline/phase_2/tests/modular/test_validation_pattern_checks_convergence.py](../../tests/modular/test_validation_pattern_checks_convergence.py)
**(new file)**

`TestCheckConvergence` — 8 stand-alone validator unit tests:

| Test | Fixture / Pattern | Expected |
|------|-------------------|----------|
| `test_convergence_passes_when_late_means_uniform` | Early spread `[2, 5, 8, 11]`, late means all 6.5 | `passed=True`, detail contains `reduction=` |
| `test_stable_spread_fails` | Same `[2, 5, 8, 11]` spread on both sides | `passed=False` (reduction ≈ 0) |
| `test_single_entity_graceful_fail` | Only 1 hospital → 1-entity groupby on each side | `passed=False`, detail mentions `Need >=2 entities` |
| `test_missing_temporal_column_graceful_fail` | Meta has no `time` group | `passed=False`, detail mentions `temporal_col` |
| `test_constant_column_early_var_zero_graceful_fail` | All entities at exactly 5.0 (noise-free) on both sides | `passed=False`, detail mentions `Early-period inter-group variance` |
| `test_custom_split_point_used` | Explicit `split_point="2024-04-15"` between the two periods | `passed=True` |
| `test_custom_reduction_threshold_blocks_pass` | ~50% reduction; `reduction=0.3` passes, `reduction=0.95` fails | both verdicts honored |
| `test_entity_col_fallback_uses_first_dim_root` | Drop `entity_col` from params | `passed=True` (resolves via first dim-group hierarchy root) |

**Note on the constant-column fixture:** the parametric `_build_df`
helper adds σ=0.1 jitter that produces tiny but nonzero per-entity
variance, hiding the `early_var == 0` branch. The test builds a
noise-free DataFrame inline so the zero-variance graceful-fail branch
is exercised directly. (Caught by the first test run — initial draft
relied on the parametric helper and saw `early_var=0.0002` which
flowed into normal `reduction` arithmetic with `passed=False` for the
*wrong* reason.)

### [pipeline/phase_2/tests/modular/test_engine_patterns.py](../../tests/modular/test_engine_patterns.py)

Added `TestInjectConvergence` (7 tests) and `TestConvergenceDeclaration`
(3 tests) at the end of the file, mirroring the `dominance_shift` test
classes already there:

| Test | What it covers |
|------|----------------|
| `test_round_trip_passes_validator` | Full inject → validate cycle. Pre-injection validator fails (stable spread); after `inject_convergence` the validator passes with `reduction=` in detail. |
| `test_late_means_pulled_toward_global_mean` | Direct numeric check: post-injection per-entity late-half means are within 2.0 of the pre-injection global mean (vs pre-injection bases ranging 2-11). |
| `test_empty_target_raises` | `target="value > 99999"` → `PatternInjectionError("zero rows")`. |
| `test_missing_temporal_column_raises` | Column registry has no `temporal` entry → `PatternInjectionError("temporal column")`. |
| `test_zero_temporal_span_raises` | All rows on `2024-01-01` → `PatternInjectionError("zero span")`. |
| `test_negative_pull_strength_raises` | `pull_strength=-0.5` → `PatternInjectionError("pull_strength")`. |
| `test_zero_pull_strength_raises` | `pull_strength=0.0` → `PatternInjectionError("pull_strength")`. |
| `test_valid_declaration_with_no_params_succeeds` | `sim.inject_pattern("convergence", target=…, col=…)` with no params registers a spec with `params == {}`. |
| `test_valid_declaration_with_optional_params_succeeds` | Declaration with `reduction`, `pull_strength`, `split_point` all populated registers them in `params`. |
| `test_sdk_constants_register_convergence` | `"convergence" in VALID_PATTERN_TYPES` and `PATTERN_REQUIRED_PARAMS["convergence"] == frozenset()`. |

The test imports were updated to include `inject_convergence` and
`check_convergence` alongside the existing pattern symbols.

## Verification

```bash
conda run -n chart pytest pipeline/phase_2/tests/ -x
# → 161 passed in 0.55s
```

The round-trip test (`test_round_trip_passes_validator` in
`TestInjectConvergence`) is the load-bearing one: it builds a DataFrame
where the inter-group spread is stable across the temporal split (validator
fails), runs the injector, then asserts
`check_convergence(...).passed is True` with `reduction=` reported in
the detail. End-to-end proof that injector and validator agree on what
`convergence` means.

## Dependency chain status (per stub_gap_analysis §DS-2)

- ✅ **`outlier_entity`, `trend_break`, `ranking_reversal`,
  `dominance_shift`** — fully shipped in prior steps.
- ✅ **`convergence`** — IS-3 validator and DS-2 injector implemented;
  SDK declarations of `convergence` no longer raise
  `ValueError("Unsupported pattern type")` and the engine no longer
  raises `NotImplementedError` for this type.
- ⏳ **`seasonal_anomaly`** — last remaining deferred pattern type.
  Validator stub returns `passed=True`; injector raises
  `NotImplementedError`. Spec still owes the operational definition
  for the `anomaly_window` shape (see `stub_gap_analysis.md` §IS-4).
