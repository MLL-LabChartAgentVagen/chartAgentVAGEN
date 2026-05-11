# DS-1: Censoring Injection — Summary of Changes

Implements DS-1 from `pipeline/phase_2/docs/artifacts/stub_gap_analysis.md`:
per-column censoring (right / left / interval) with NaN as the marker, run
**before** missing/dirty injection so `missing_rate` is computed against
the post-censor distribution. Re-advertises the `censoring=` kwarg to the LLM
(reverses the "double-gated out" pattern that hid it during the M1-NC-7 freeze).

## Schema (the contract added)

```python
censoring = {
    "<col>": {"type": "right",    "threshold": <float>},          # values > threshold -> NaN
    "<col>": {"type": "left",     "threshold": <float>},          # values < threshold -> NaN
    "<col>": {"type": "interval", "low": <float>, "high": <float>}, # outside [low, high] -> NaN
}
```

## Files changed

### [pipeline/phase_2/types.py](pipeline/phase_2/types.py)

- Extended typing imports to include `Literal, TypedDict`.
- Added new `CensoringSpec(TypedDict, total=False)` after `RealismConfig`,
  with fields `type` (Literal["right", "left", "interval"]), `threshold`,
  `low`, `high`. `total=False` because the required keys vary by `type`.

### [pipeline/phase_2/engine/realism.py](pipeline/phase_2/engine/realism.py)

- Added `inject_censoring(df, censoring_config, rng) -> pd.DataFrame`. Mirrors
  the function shape of `inject_missing_values`: early return on empty config,
  per-column loop, `df.loc[mask, col] = np.nan`, `logger.debug` summary.
  Right → `df[col] > threshold`; left → `df[col] < threshold`;
  interval → `(df[col] < low) | (df[col] > high)`.
- Missing columns trigger `logger.warning(...)` and skip (no error).
- Unknown `type` raises `ValueError`.
- Deleted the `NotImplementedError` branch in `inject_realism` and reordered
  the body so censoring runs **first**, then missing, then dirty. Updated the
  function docstring to reflect the new order and `[Subtask 4.4.3]` reference.

### [pipeline/phase_2/sdk/relationships.py](pipeline/phase_2/sdk/relationships.py)

- Added schema validation in `set_realism` for the `censoring` kwarg
  (only when not `None`). Validates: top-level dict, per-column dict,
  required `type` key, `type ∈ {right, left, interval}`, `threshold`
  required for right/left, `low` + `high` required for interval. Uses the
  existing `raise ValueError(f"...")` guard-clause style.
- Updated docstring for the `censoring` arg from "placeholder" to a pointer
  at `engine.realism.inject_censoring`.

### [pipeline/phase_2/orchestration/prompt.py](pipeline/phase_2/orchestration/prompt.py)

- Replaced the `# TODO [M1-NC-7]: censoring kwarg deferred ...` comment and
  the `sim.set_realism(missing_rate, dirty_rate)` advertisement at L70-71 with
  a re-advertised signature plus a two-line schema hint visible to the LLM:

  ```text
    sim.set_realism(missing_rate, dirty_rate, censoring=None)    # optional
        # censoring={"col": {"type": "right"|"left"|"interval", "threshold": float}}
        # interval form: {"col": {"type": "interval", "low": float, "high": float}}
  ```

### [pipeline/phase_2/tests/modular/test_realism.py](pipeline/phase_2/tests/modular/test_realism.py) (new)

Three test classes, 20 cases total:

- **`TestInjectCensoring`** (7) — right/left/interval mask correctness,
  missing-column warn-and-skip via `caplog`, empty-config no-op, unknown
  type ValueError, and a multi-column independent-censor case.
- **`TestInjectRealismOrdering`** (3) — censoring runs even when
  `missing_rate=0`; censored cells survive through the missing pipeline
  (row-count math: all-100 cells > threshold → all NaN regardless of
  `missing_rate`); back-compat for configs without a `censoring` key.
- **`TestSetRealismCensoringValidation`** (10) — accepts valid right/left/
  interval; rejects non-dict top-level, non-dict per-column, missing
  `type`, unknown `type`, right/left without `threshold`, interval missing
  `low`/`high`.

## Verification

```bash
conda run -n chart pytest pipeline/phase_2/tests/ -x
# → 116 passed in 0.47s   (96 pre-existing + 20 new)
```

## Out of scope

- Phase 3 view-extraction awareness of censored cells. The proposal selects
  marker option (a) NaN — indistinguishable from regular missing data
  downstream — by design; DS-1's blocking-questions section flags this for
  future spec work.
- Updating the One-Shot Example in `prompt.py` (~L115-216) to demonstrate
  `set_realism(censoring=...)`. The example does not exercise realism today,
  so adding censoring to it would be a larger pedagogical change.
