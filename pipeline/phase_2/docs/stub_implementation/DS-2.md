# DS-2 (partial): `ranking_reversal` Pattern Injection — Summary of Changes

Implements the `ranking_reversal` slice of DS-2 from
`pipeline/phase_2/docs/artifacts/stub_gap_analysis.md` (§DS-2). This is
the lowest-effort win in the DS-2 cluster: the L3 validator
`check_ranking_reversal` was already fully implemented in
[validation/pattern_checks.py](../../validation/pattern_checks.py#L268-L346),
so only the injection side, the SDK gate, and the prompt gate needed
work. Reverses the "double-gated out" pattern that hid `ranking_reversal`
during the M1-NC-6 freeze.

**Out of scope (still pending):** `dominance_shift`, `convergence`,
`seasonal_anomaly` injectors — they remain in the
`NotImplementedError` branch of
[engine/patterns.py](../../engine/patterns.py) and require spec
decisions on injection algorithm + params contract (per stub_gap_analysis
§DS-2 blocking questions).

## Schema (the contract added)

```python
sim.inject_pattern(
    "ranking_reversal",
    target="<DataFrame query>",      # row subset to operate on
    col="<measure>",                 # SDK requires a valid measure column;
                                     # by convention pass metrics[0]
    params={
        "metrics": ["<m1>", "<m2>"],     # REQUIRED: length-2 list
        "entity_col": "<categorical>",   # OPTIONAL: falls back to the
                                         # first categorical root in the
                                         # column registry
    },
)
```

**Operational contract (paired with `check_ranking_reversal`):** within
the target subset, the per-entity means of `m1` and `m2` end up with
**negative** Spearman rank correlation (entity with the highest mean(m1)
gets the lowest mean(m2), and vice versa).

## Files changed

### [pipeline/phase_2/sdk/relationships.py](../../sdk/relationships.py)

- Added `"ranking_reversal"` to `VALID_PATTERN_TYPES` (L29-31).
- Added `"ranking_reversal": frozenset({"metrics"})` to
  `PATTERN_REQUIRED_PARAMS` (L39-46). `entity_col` stays optional —
  the engine resolves a fallback at injection time.
- Updated the `M1-NC-6` TODO comments to drop `ranking_reversal` from
  the deferred list (now lists only the three remaining patterns).

### [pipeline/phase_2/engine/patterns.py](../../engine/patterns.py)

- Removed `"ranking_reversal"` from the `NotImplementedError` tuple
  (L62-65) and added an explicit dispatch branch at L61 routing to the
  new `inject_ranking_reversal(df, pattern, columns)`.
- Added `inject_ranking_reversal` (L245+). Algorithm — operates at the
  entity-mean level, not row-pairs, so it reliably triggers
  `check_ranking_reversal` (Spearman corr < 0):
    1. Validate `params["metrics"]` is a length-2 sequence — else
       `PatternInjectionError`.
    2. Resolve `entity_col`: prefer `params["entity_col"]`; else fall
       back to the first column in `columns` whose `type ==
       "categorical"` and `parent is None` (operational equivalent of
       the validator's "first dimension group root" fallback at
       [validation/pattern_checks.py:300-309](../../validation/pattern_checks.py#L300-L309)).
       No such column → `PatternInjectionError`.
    3. `target_mask = df.eval(pattern["target"])`. Empty → typed error
       (mirrors the existing pattern in `inject_outlier_entity` /
       `inject_trend_break`).
    4. Skip-with-warning when any of `m1`, `m2`, `entity_col` is missing
       from `df.columns` (mirrors the `inject_outlier_entity` L126-132
       convention — measures may not be generated yet).
    5. Compute per-entity means of m1 and m2 over the target subset.
       `< 2` distinct entities → `PatternInjectionError` (rank
       correlation undefined).
    6. Rank entities ascending by `mean(m1)` (`method="first"` for
       deterministic tie-breaking), then pair against m2 means sorted
       descending — entity with smallest m1 rank gets the largest
       desired m2.
    7. Apply additive per-entity shift on m2:
       `df.loc[rows_e, m2] += (desired - current_mean)`. Within-entity
       variance is preserved; only the entity mean moves.
    8. `logger.debug(...)` summary.

### [pipeline/phase_2/orchestration/prompt.py](../../orchestration/prompt.py)

- Updated the `M1-NC-6` TODO comment and changed the advertised
  `PATTERN_TYPES` line at L88-90 from
  `"outlier_entity", "trend_break"` to
  `"outlier_entity", "trend_break", "ranking_reversal"`.
- Added a one-shot example after the existing `trend_break` injection
  (L217-221) using the hospital scenario:
  ```python
  sim.inject_pattern("ranking_reversal",
      target="severity == 'Severe'",
      col="wait_minutes",
      params={"metrics": ["wait_minutes", "satisfaction"],
              "entity_col": "hospital"})
  ```
  Tells the LLM that hospitals with the longest severe-case waits
  end up with the lowest satisfaction — a narrative-coherent example.

### [pipeline/phase_2/tests/modular/test_engine_patterns.py](../../tests/modular/test_engine_patterns.py) (new)

First test file for engine pattern injection (only validation tests
existed before, all of which mock the L3 checks). Mirrors the style of
[test_realism.py](../../tests/modular/test_realism.py): plain pytest
classes, fixtures via inline `pd.DataFrame(...)`.

`ranking_reversal` test classes (11 cases):

- **`TestInjectRankingReversal`** (8) — round-trip via
  `check_ranking_reversal` on a fixture deliberately seeded with
  positive pre-injection rank correlation (asserts the pre-condition,
  then asserts validator passes post-injection); explicit `entity_col`
  fallback when omitted; fallback skips temporal / measure columns and
  picks the first categorical root; empty target → `PatternInjectionError`;
  single-entity target → `PatternInjectionError`; missing metric column
  → warn-and-skip via `caplog`; malformed `metrics` length → typed
  error; no categorical root in registry → typed error.
- **`TestRankingReversalDeclaration`** (3) — SDK-level declaration:
  succeeds with all params; succeeds without optional `entity_col`;
  raises `ValueError(match="metrics")` when `metrics` is missing.

## Verification

```bash
conda run -n chart pytest pipeline/phase_2/tests/ -x
# → 143 passed in 0.55s
```

The round-trip test (`test_round_trip_passes_validator`) is the load-
bearing one: it builds a DataFrame where `pre_corr > 0` (validator
would fail), runs the injector, then asserts
`check_ranking_reversal(...).passed is True` with `rank_corr` reported
as `< 0`. This is the end-to-end proof that injector and validator
agree on what `ranking_reversal` means.

## Dependency chain status (per stub_gap_analysis §DS-2)

- ✅ **Unblocks `check_ranking_reversal`.** The validator was fully
  implemented but unreachable; SDK declarations of `ranking_reversal`
  no longer raise `ValueError("Unsupported pattern type")` and the
  engine no longer raises `NotImplementedError` for this type.
- ⏳ **`dominance_shift`, `convergence`, `seasonal_anomaly`** still
  blocked on spec extension for the injection algorithm + params
  contract.
