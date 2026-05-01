# IS-2 + DS-2 (`dominance_shift`): Summary of Changes

Implements **IS-2** (`check_dominance_shift` validator) and the
**`dominance_shift` slice of DS-2** (`inject_dominance_shift` injector)
from
[pipeline/phase_2/docs/artifacts/stub_analysis/stub_gap_analysis.md](../artifacts/stub_analysis/stub_gap_analysis.md)
§§ IS-2 and DS-2.

These two stubs ship as one atomic unit because the injector produces
the very signal the validator checks — IS-2 alone leaves a no-op
`passed=True` stub regardless of what the data shows; DS-2's
`dominance_shift` alone is unverifiable.

Algorithm decisions are locked in
[docs/artifacts/phase_2_spec_decisions.md §IS-2 / §DS-2](../artifacts/phase_2_spec_decisions.md):

- **Validator (IS-2):** target entity's `|rank_after − rank_before| ≥ rank_change`,
  ranks computed by **descending** mean of `pattern["col"]` (largest
  mean = rank 1, matching `check_ranking_reversal`).
- **Injector (DS-2):** post-`split_point` additive shift on target rows
  so the target entity's mean exceeds peer max + magnitude × peer std.

This restores `dominance_shift` end-to-end and unwinds the
"triple-gated out" defensive pattern (SDK, engine, prompt) that hid it
during the M1-NC-6 freeze.

**Out of scope (still pending):** `convergence`, `seasonal_anomaly`
injectors and their paired validators (IS-3, IS-4) — they remain in
the `NotImplementedError` branch of
[engine/patterns.py](../../engine/patterns.py) and need spec
extensions for their operational definitions.

## Schemas (the contracts added)

### Pattern declaration

```python
sim.inject_pattern(
    "dominance_shift",
    target="<DataFrame query>",          # row subset the injector mutates
                                         # (typically the target entity)
    col="<measure>",                     # measure to shift
    params={
        "entity_filter": "<entity value>",   # REQUIRED: target entity name,
                                             #   used by the validator's
                                             #   groupby lookup
        "split_point": "YYYY-MM-DD",         # REQUIRED: temporal split
        "entity_col": "<categorical>",       # OPTIONAL: groupby column;
                                             #   fallback = first dim-group
                                             #   hierarchy root
        "rank_change": 1,                    # OPTIONAL: validator threshold
                                             #   (default 1)
        "magnitude": 1.0,                    # OPTIONAL: injector gap size in
                                             #   units of peer_std (default 1.0)
    },
)
```

**Validator pass condition:** `|rank_after − rank_before| ≥ rank_change`,
where ranks are computed by descending mean of `pattern["col"]` per
side of `split_point`, grouping by `entity_col`.

**Injector post-condition:** post-split target rows are additively
shifted so the target entity's post-split mean ≥ peer_max + max(magnitude
· peer_std, positive_floor). Pre-split target rows are **not** mutated,
so the per-side group means diverge across the split and the validator
detects a rank change.

## Files changed

### [pipeline/phase_2/validation/pattern_checks.py](../../validation/pattern_checks.py)

- **Added module-level helper `_resolve_first_dim_root(meta)`** (L106-119)
  factoring the entity-col fallback that previously lived inline in
  `check_ranking_reversal`. IS-3 and IS-4 will reuse this helper when
  those stubs land.
- **Refactored `check_ranking_reversal`** to call
  `_resolve_first_dim_root(meta)` instead of inlining the
  `dim_groups → first → hierarchy[0]` walk — single source of truth.
- **Replaced stub `check_dominance_shift`** (was L189-213, hard-coded
  `passed=True`) with the rank-change algorithm (L207-309). Failure
  modes return `passed=False` with a descriptive `detail` rather than
  raising — graceful for `ValidationReport` consumers, and the L3
  dispatcher in `validator.py` already wraps raises into failed checks
  anyway.

### [pipeline/phase_2/engine/patterns.py](../../engine/patterns.py)

- **Pulled `"dominance_shift"` out of the `NotImplementedError` tuple**
  in `inject_patterns` and added an explicit dispatch branch routing
  to the new `inject_dominance_shift(df, pattern, columns)` (L61-69).
  `convergence` and `seasonal_anomaly` remain deferred.
- **Added `inject_dominance_shift`** (L246-368). Algorithm:
    1. Resolve `temporal_col` from the column registry (mirrors
       `inject_trend_break`).
    2. Evaluate `pattern["target"]` mask → target entity rows.
       (`params["entity_filter"]` is the entity *name* the validator
       looks up; the `target` expression is the engine's row selector
       — both reference the same entity but live in different positions
       because the engine needs `df.eval()`-compatible syntax and the
       validator needs a groupby key.)
    3. Compute peer rows = `(NOT target) AND (temporal ≥ split_point)`;
       derive `peer_max` and `peer_std` on `pattern["col"]`.
    4. Compute `desired_mean = peer_max + max(magnitude × peer_std,
       positive_floor)`. The floor (`max(|peer_max| × 0.1, 1.0)` when
       peer_std ≤ 0 or NaN; `1e-9` otherwise) guarantees target
       dominance even with zero-variance peers or `magnitude=0`.
    5. Additive shift on post-split target rows so their mean lands at
       `desired_mean`. Pre-split target rows are untouched — this is
       what creates the rank divergence the validator detects.
- **Raises `PatternInjectionError`** for: no temporal column, empty
  `target` subset, empty post-split target subset, empty peer set
  post-split (matches `inject_outlier_entity` / `inject_trend_break`
  style).

### [pipeline/phase_2/sdk/relationships.py](../../sdk/relationships.py)

- Added `"dominance_shift"` to `VALID_PATTERN_TYPES` (L31).
- Added `"dominance_shift": frozenset({"entity_filter", "split_point"})`
  to `PATTERN_REQUIRED_PARAMS` (L51) with an inline comment listing
  the optional params (`entity_col`, `rank_change`, `magnitude`).
- Updated the `M1-NC-6` TODO comments to drop `"dominance_shift"`,
  leaving only `convergence` / `seasonal_anomaly` as still-deferred.

### [pipeline/phase_2/orchestration/prompt.py](../../orchestration/prompt.py)

- Updated the advertised `PATTERN_TYPES` line (L90) to include
  `"dominance_shift"`.
- Updated the matching `M1-NC-6` TODO comment.
- Added a one-shot example call (after the `ranking_reversal` example,
  before `return sim.generate()`) demonstrating the full param shape so
  the LLM has a concrete reference for `entity_filter` + `split_point`.

### [pipeline/phase_2/tests/modular/test_validation_pattern_checks_dominance.py](../../tests/modular/test_validation_pattern_checks_dominance.py)
**(new file)**

`TestCheckDominanceShift` — 8 stand-alone validator unit tests:

| Test | Fixture / Pattern | Expected |
|------|-------------------|----------|
| `test_rank_shift_passes` | Target pre-mean=5 (rank 5), post-mean=20 (rank 1) | `passed=True`, `delta=4` |
| `test_stable_rank_fails` | Target mean=15 on both sides (stable rank 1, distinctly above peers' 10) | `passed=False`, `delta=0` |
| `test_missing_entity_filter_fails` | Drop `entity_filter` from params | `passed=False`, detail mentions `entity_filter` |
| `test_missing_split_point_fails` | Drop `split_point` from params | `passed=False`, detail mentions `split_point` |
| `test_target_absent_pre_split_fails` | Drop all pre-split target rows | `passed=False`, detail mentions target name |
| `test_missing_temporal_column_fails` | Meta has no `time` group | `passed=False`, detail mentions `temporal_col` |
| `test_entity_col_fallback_uses_first_dim_root` | Drop `entity_col` from params | `passed=True` (resolves via first dim-group hierarchy root) |
| `test_custom_rank_change_threshold_blocks_pass` | delta=4 but `rank_change=5` | `passed=False` |

**Note on the stable-rank fixture:** an earlier draft used target mean
≈ peer mean (both ≈ 10), but with 5 hospitals all at the same mean and
small per-side noise the ranks become noise-driven and produce flaky
deltas. The fix is to give the target a distinctly different stable
mean (15 vs peers' 10) so the rank is genuinely unchanged across
the split (delta=0) — a real stable-rank scenario, not noise masking
as stability.

### [pipeline/phase_2/tests/modular/test_engine_patterns.py](../../tests/modular/test_engine_patterns.py)

Added `TestInjectDominanceShift` (6 tests) and
`TestDominanceShiftDeclaration` (2 tests) at the end of the file,
mirroring the `ranking_reversal` test classes already there:

| Test | What it covers |
|------|----------------|
| `test_round_trip_passes_validator` | Full inject → validate cycle. Pre-injection validator fails (stable rank); after `inject_dominance_shift` the validator passes. |
| `test_pre_split_values_unchanged` | Asserts pre-split target rows are bitwise unchanged (only post-split target gets shifted). |
| `test_post_split_target_exceeds_peer_max` | Direct numeric check: post-split target mean > post-split peer max. |
| `test_empty_target_raises` | `target="hospital == 'NonexistentHospital'"` → `PatternInjectionError`. |
| `test_empty_post_split_target_raises` | Drop post-split target rows but keep pre-split → `PatternInjectionError("No target rows…")`. |
| `test_no_temporal_column_raises` | Column registry has no `temporal` entry → `PatternInjectionError`. |
| `test_valid_declaration_succeeds` | `sim.inject_pattern("dominance_shift", …)` registers a spec with the expected `params` dict. |
| `test_missing_required_params_raises` | Omit both `entity_filter` and `split_point` → `ValueError`. |

The test imports were updated to include
`inject_dominance_shift` and `check_dominance_shift` alongside the
existing `ranking_reversal` symbols.

## Verification

```bash
conda run -n chart pytest pipeline/phase_2/tests/ -x
```

Result: **143 passed in 0.52s** (16 new + 127 regression). Existing
`ranking_reversal` tests still pass after the
`check_ranking_reversal` refactor to use `_resolve_first_dim_root`.

## Integration points (no code changes needed)

- **`validation/validator.py:203-204`** already routes
  `pattern_type == "dominance_shift"` to
  `_l3.check_dominance_shift(df, pattern, self.meta)`, so no dispatch
  edit is required there.
- **`engine/generator.py:98`** calls `inject_patterns(df, patterns, columns, rng)`
  unchanged — the new dispatch branch is internal to `inject_patterns`.

## Why this slice landed before IS-3 / IS-4

`dominance_shift` is the closest mechanical analog to `trend_break`
(both split at a temporal `split_point` and shift target values on one
side), so the injector reuses the temporal-column-walk pattern from
`inject_trend_break` with minimal new infrastructure. The shared
helper `_resolve_first_dim_root` was added here precisely because IS-3
(`check_convergence`) and IS-4 (`check_seasonal_anomaly`) will also
need it — adding it once now prevents three near-identical inline
copies once those stubs ship.
