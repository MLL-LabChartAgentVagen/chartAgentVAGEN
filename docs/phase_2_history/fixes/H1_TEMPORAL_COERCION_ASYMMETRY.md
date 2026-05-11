# H1 — Temporal-Coercion Asymmetry in Pattern Injectors

## Why

### The bug

Three of four temporal-aware pattern injectors in
[engine/patterns.py](../../engine/patterns.py) called
`pd.to_datetime(df[temporal_col])` without `errors="coerce"`:

- `inject_trend_break` (L226)
- `inject_dominance_shift` (L322)
- `inject_seasonal_anomaly` (L706)

Meanwhile every matching validator in
[validation/pattern_checks.py](../../validation/pattern_checks.py)
**did** coerce
([L167, L284, L362, L449](../../validation/pattern_checks.py#L167)),
and the fourth injector
[`inject_convergence` at L582-592](../../engine/patterns.py#L582-L592)
did the right thing too — coerce, build a `valid_mask = tval.notna()`,
exclude NaT rows from the target subset, and raise
`PatternInjectionError` with a clear detail when the entire target
subset becomes NaT.

A scenario whose generated DataFrame had any unparseable temporal cell
would crash at one of the three buggy injectors with a stock pandas
`DateParseError`. The §2.7 retry loop would then misattribute that
crash to "bad pattern config" and ask the LLM to fix the pattern,
when the actual problem was upstream data generation. The matching
validator, run on the same DataFrame, would have returned
`Check(passed=False, detail=...)` cleanly — an obvious asymmetry.

The bug was latent in current pipelines (the engine generates clean
ISO dates upstream from `add_temporal(start, end, freq)`), but a real
production hazard once the LLM begins producing scenarios with messy
temporal data, multi-format strings, or any pattern that mixes
parseable and unparseable cells.

### Root cause

`inject_trend_break` predates the stub-implementation workflow and
was written before the temporal-coercion convention was established
at the validator layer. It used the un-coerced
`pd.to_datetime(df[temporal_col])` call as the first temporal
injector in the file.

When IS-2 added `inject_dominance_shift` and IS-4 added
`inject_seasonal_anomaly`, both summaries explicitly say the
algorithm "mirrors `inject_trend_break`":

- [IS-2_dominance_shift.md L93-95](../stub_implementation/IS-2_dominance_shift.md#L93-L95)
  — "Algorithm: 1. Resolve `temporal_col` from the column registry
  (mirrors `inject_trend_break`)."
- [IS-4_seasonal_anomaly.md L29-30](../stub_implementation/IS-4_seasonal_anomaly.md#L29-L30)
  — "scale `pattern["col"]` values inside the anomaly window by
  `(1 + magnitude)` — mirrors `inject_trend_break` with a finite
  `[start, end]` mask".

The implementers copied the structure verbatim and inherited the
sloppiness. IS-3 (`inject_convergence`) broke the chain because its
shape is different (normalized time, no split point) — the implementer
wrote new temporal handling and applied the coerce convention they had
learned from the validator layer.

The `mirrors inject_trend_break` template silently propagated the
original gap. The Decisions doc never specified temporal-robustness
as a contract requirement, so each implementer made an independent
choice and the two who copied trend_break inherited its sloppiness.

### Fix strategy

Align all three buggy injectors to the
[`inject_convergence` canonical pattern](../../engine/patterns.py#L582-L592):

1. Replace `pd.to_datetime(df[temporal_col])` with
   `pd.to_datetime(df[temporal_col], errors="coerce")`.
2. Compute `valid_mask = temporal_values.notna()`.
3. Raise `PatternInjectionError(pattern_type="<this_pattern>",
   detail="All target rows have unparseable temporal values in column
   '<col>'.")` when `target_mask & valid_mask` is empty (defensive
   raise mirrors convergence's L585-592).
4. AND `valid_mask` into every downstream boolean mask that compares
   against `temporal_values`, so NaT rows are naturally excluded from
   the mutation target.

For DataFrames with all-valid temporal cells (every existing test
fixture), the behavior is bit-identical: `pd.to_datetime(...,
errors="coerce")` returns the same Series as `pd.to_datetime(...)`
when there are no errors, `valid_mask` is all-True, and the AND-in
is identity.

## Summary of changes

### Modified files

- **[pipeline/phase_2/engine/patterns.py](../../engine/patterns.py)**
  - **`inject_trend_break` (L226)** — added `errors="coerce"`,
    `valid_mask = temporal_values.notna()`, all-NaT defensive raise,
    AND-in `valid_mask` to `post_break_mask`.
  - **`inject_dominance_shift` (L322)** — same treatment;
    `post_split_mask` now `valid_mask & (temporal_values >= sp)`.
    The existing downstream "no post-split target rows" raise still
    fires for the empty-but-not-all-NaT case (different failure mode,
    different message).
  - **`inject_seasonal_anomaly` (L706)** — same treatment; `in_win`
    now ANDs `valid_mask` alongside the window comparisons.
  - `inject_convergence` was the reference and is unchanged.

### Test additions

- **[pipeline/phase_2/tests/modular/test_engine_patterns.py](../../tests/modular/test_engine_patterns.py)**
  - Added `inject_trend_break` to the top-of-file import block (was
    not previously imported because no test exercised it directly).
  - Appended `TestTemporalCoercionRobustness` class with a single
    shared `_build_garbled_temporal_df()` fixture (10 rows: 8
    parseable ISO dates + 2 unparseable strings `"not-a-date"` and
    `"BAD"`) and 6 tests:
    - `test_inject_trend_break_skips_nat_rows` — NaT rows untouched,
      valid post-break rows mutated as expected.
    - `test_inject_dominance_shift_skips_nat_rows` — NaT row untouched.
    - `test_inject_seasonal_anomaly_skips_nat_rows` — NaT rows
      untouched, in-window valid row mutated.
    - `test_all_nat_target_raises` — parametrized over the three
      injectors. Builds a DataFrame whose every temporal cell is
      unparseable and asserts each injector raises
      `PatternInjectionError` matching `"unparseable temporal"`.

## Verification

```bash
conda run -n chart pytest pipeline/phase_2/tests/modular/test_engine_patterns.py::TestTemporalCoercionRobustness -v
# 6 passed

conda run -n chart pytest pipeline/phase_2/tests/
# 267 passed in 0.96s  (was 261 before; +6 from this fix)
```

TDD trace:

1. **RED.** New test class committed first; all 6 tests failed with
   `pandas._libs.tslibs.parsing.DateParseError: Unknown datetime
   string format, unable to parse: not-a-date` raised at the
   un-coerced `pd.to_datetime` call site in each injector.
2. **GREEN site 1.** After patching `inject_trend_break` — 2/6 pass.
3. **GREEN site 2.** After patching `inject_dominance_shift` — 4/6 pass.
4. **GREEN site 3.** After patching `inject_seasonal_anomaly` — 6/6 pass.
5. **Regression sweep.** Full phase-2 suite: 267/267 green; no
   pre-existing test broke.

## Commit

`6f64495` — `Fix temporal-coercion asymmetry in 3 pattern injectors`
on branch `dingc`.
