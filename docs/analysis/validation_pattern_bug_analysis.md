# Validation Bug Analysis: Pattern-Aware L2/L3 Checks

**Date:** 2026-04-08
**Discovered via:** `scripts/agentic_smoke_test.py` smoke run (30 checks, 5 failures)
**Fixed in:** `phase_2/validation/statistical.py`, `phase_2/validation/pattern_checks.py`, `phase_2/validation/validator.py`

---

## Background

The Phase 2 pipeline has two post-generation stages that interact:

1. **Pattern injection** (`engine/patterns.py`) — deliberately mutates measure values in a target subset of rows to embed a detectable signal (e.g. outlier shift, trend break).
2. **Validation** (`validation/statistical.py`, `validation/pattern_checks.py`) — checks whether the generated data matches the declared statistical properties.

The bug: validation checks were not accounting for the fact that pattern injection had already altered the data, causing them to flag their own injected mutations as failures.

---

## Root Cause 1: `check_stochastic_ks` tested pattern-mutated rows

### Location
`phase_2/validation/statistical.py` — `check_stochastic_ks()`

### What happened
The KS test enumerates predictor cells (Cartesian product of categorical columns referenced in `param_model` effects) and for each cell runs `scipy.stats.kstest` against the declared distribution's CDF. It operated on the full DataFrame, including rows that had been mutated by pattern injection.

### Concrete example (smoke test)
The LLM-generated script declared `revenue` as `lognormal(mu=4.5 + effects, sigma=0.25 + effects)` and injected two patterns:

- `outlier_entity` on `store_location == 'London' & product_tier == 'Premium'`: shifts all matching rows by `+3.5 × global_std`
- `trend_break` on `store_location == 'Manchester'`: multiplies all post-2025-02-15 Manchester rows by `1.6`

The KS test then tested cells `London×Premium`, `Manchester×Premium`, `Manchester×Standard`, and `Manchester×Budget` against the original lognormal parameters — parameters that described the pre-mutation distribution. The mutated values had no chance of fitting, producing large D-statistics and p-values of 0.0000.

### Why `check_structural_residuals` did not have this bug
`check_structural_residuals` already excluded pattern-targeted rows (P3-8, added as part of the blocker resolutions). The same logic was never applied to `check_stochastic_ks`.

### Fix
Added a `patterns` parameter to `check_stochastic_ks`. Before cell enumeration, rows matching any pattern target on the same column are excluded from `work_df`:

```python
work_df = df
if patterns:
    pattern_mask = pd.Series(False, index=df.index)
    for p in patterns:
        if p.get("col") == col_name:
            try:
                pattern_mask |= df.eval(p["target"])
            except Exception:
                pass
    work_df = df[~pattern_mask]
```

`_iter_predictor_cells` and the KS sampling both operate on `work_df`. The call site in `validator.py` (`_run_l2`) was updated to pass `patterns=patterns`.

### Side effect: check count drop (30 → 26)
After exclusion, 4 predictor cells had zero rows left (all their rows were pattern targets) and fell below the `min_rows=5` threshold, so no Check was emitted for them:

| Dropped cell | Pattern responsible |
|---|---|
| `London × Premium` | `outlier_entity` target `store_location == 'London' & product_tier == 'Premium'` |
| `Manchester × Premium` | `trend_break` target `store_location == 'Manchester'` |
| `Manchester × Standard` | same |
| `Manchester × Budget` | same |

This is correct behaviour — there is nothing to test after excluding all rows in a cell.

---

## Root Cause 2: `check_trend_break` measured the global column, not the target subset

### Location
`phase_2/validation/pattern_checks.py` — `check_trend_break()`

### What happened
`inject_trend_break` multiplies values by `(1 + magnitude)` only within the pattern's `target` subset after the break point. The check should therefore measure the before/after change within that same subset. Instead, `check_trend_break` split the **entire DataFrame** at `break_point` and compared global before/after column means.

### Concrete example (smoke test)
The pattern was declared as:

```python
sim.inject_pattern("trend_break",
    target="store_location == 'Manchester'",
    col="revenue",
    params={"break_point": "2025-02-15", "magnitude": 0.6})
```

Manchester rows are ~35% of the total (300 rows × 0.35 ≈ 105 rows). The 60% revenue bump on Manchester post-Feb-15 was diluted by the unchanged London and Bristol rows, producing a global ratio of only `0.094` — below the `0.15` pass threshold. The check reported:

```
FAIL: trend_revenue — before_mean=151.3981, after_mean=165.6112, ratio=0.0939 (<= 0.15)
```

### Fix
Filter to the pattern's `target` rows before computing the temporal split:

```python
target_expr = pattern.get("target")
if target_expr:
    target_mask = df.eval(target_expr)
    work_df = df[target_mask]
else:
    work_df = df

temporal_values = pd.to_datetime(work_df[temporal_col], errors="coerce")
before_values = work_df.loc[temporal_values < break_point_dt, col]
after_values  = work_df.loc[temporal_values >= break_point_dt, col]
```

With this fix, the ratio is computed only over Manchester rows, where the signal is at full strength.

---

## Invariant violated (and now restored)

> A validation check for property P must be evaluated on the same population of rows that was used when generating data to satisfy P.

Pattern injection changes the population for which the original distributional declaration holds. Both checks were violating this invariant by testing the full post-injection DataFrame against pre-injection parameters.

---

## Files changed

| File | Change |
|---|---|
| `phase_2/validation/statistical.py` | Added `patterns` param to `check_stochastic_ks`; exclude pattern-targeted rows before KS testing |
| `phase_2/validation/validator.py` | Pass `patterns=patterns` to `check_stochastic_ks` in `_run_l2` |
| `phase_2/validation/pattern_checks.py` | Filter `check_trend_break` to pattern target rows before before/after split |
