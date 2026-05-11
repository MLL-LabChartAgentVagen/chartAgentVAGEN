# Blocker Resolutions — AGPDS Phase 2

> **STATUS (2026-05-07):** All P0/P1/P2 blockers resolved. The "Decision" entries below remain authoritative for *what* shipped; the per-stub implementation walkthroughs in [`../stub_implementation/`](../stub_implementation/) document *how* it shipped, and [`../POST_STUB_AUDIT_FINDINGS.md`](../POST_STUB_AUDIT_FINDINGS.md) records the post-implementation adversarial audit (H1, M1–M5, L1–L5 — all closed). Body text below is preserved as the historical decision record from 2026-04-05; it describes the pre-resolution code state and is no longer current. For the current state see [`../remaining_gaps.md`](../remaining_gaps.md).

**Date:** 2026-04-05
**Author:** Decision Architect (Claude)
**Source documents:** stage3_readiness_audit.md, stage4_implementation_anatomy.md
**Ground truth:** Current codebase state as of this date

---

## How to Read This Document

Each entry follows this format:

- **ID**: Stage3 module + item number (e.g., M1-NC-1 = M1 NEEDS_CLAR item 1)
- **Status**: `ALREADY_IMPLEMENTED` | `DECIDE` | `STUB`
- **Decision**: The binding implementation directive
- **Files**: Which source files to modify
- **Test criteria**: What a correct implementation must satisfy (when applicable)

Items marked `ALREADY_IMPLEMENTED` require no further work unless noted. The implementer should verify the listed behavior still holds before moving on.

---

## P0 Blockers

These three decisions must be locked before any implementation work starts. They have cascading effects across multiple modules.

---

### P0-1: Enrich `schema_metadata` beyond section 2.6 example  <!-- ✅ RESOLVED 2026-04-22 → 2026-05-07 -->

**Modules:** M4, M5
**Stage3 refs:** M4-NC-1 (lossy projection), M5-NC-1 (M5 data source)
**Status:** ALREADY_IMPLEMENTED (M4 side). DECIDE (M5 gaps).

#### M4 Builder — ALREADY_IMPLEMENTED

`metadata/builder.py` already emits the enriched schema with all 7 top-level keys and type-discriminated column descriptors:

| Column type | Enriched fields present |
|---|---|
| categorical | `values`, `weights`, `cardinality`, `group`, `parent` |
| temporal | `start`, `end`, `freq`, `derive`, `group` |
| temporal_derived | `derivation`, `source`, `group` |
| stochastic measure | `family`, `param_model` (deep-copied) |
| structural measure | `formula`, `effects`, `noise` |

Group dependencies include `conditional_weights`. Patterns include full `params`. Internal consistency check (`_assert_metadata_consistency`) runs post-build with warning-level logging.

**Verification:** Confirm `_build_columns_metadata()` emits the fields listed above. Confirm `_assert_metadata_consistency()` runs without warnings on the one-shot example scenario.

#### M5 Validation Gaps — DECIDE

Two L1 checks are missing from `validation/structural.py`. These are SPEC_READY and do not require a decision, but are noted here because they were discovered during P0-1 gap analysis:

**Missing L1 check: `check_marginal_weights`**
- Implement in `validation/structural.py`
- For each root categorical column in metadata, compute observed value frequencies from the DataFrame
- Check: `max(abs(observed_freq - declared_weight)) < 0.10` per value
- Return one `Check` per root categorical column
- Wire into `SchemaAwareValidator._run_l1()`

**Missing L1 check: `check_measure_finiteness`**
- Implement in `validation/structural.py`
- For each measure column in metadata, check: `df[col].notna().all() and np.isfinite(df[col]).all()`
- Return one `Check` per measure column
- Wire into `SchemaAwareValidator._run_l1()`

**Test criteria:**
- `check_marginal_weights` returns passing Check when observed frequencies match declared weights within 0.10
- `check_marginal_weights` returns failing Check when deviation exceeds 0.10
- `check_measure_finiteness` returns failing Check when column contains NaN or Inf
- `check_measure_finiteness` returns passing Check on a clean float column

---

### P0-2: Formula evaluation mechanism for structural measures  <!-- ✅ RESOLVED — 受限 AST walker shipped -->

**Modules:** M1 (validation), M2 (generation)
**Stage3 refs:** M2-NC-1 (formula evaluation mechanism)
**Status:** DECIDE

The entire stage beta (measure generation) is stubbed. This is the largest implementation task.

#### Decision: Restricted AST-based evaluator

Implement a safe formula evaluator in `engine/measures.py` using Python's `ast` module:

```
ast.parse(formula, mode='eval') -> walk tree
```

**Allowed AST nodes:**
- `ast.Expression` (top-level wrapper)
- `ast.BinOp` with operators: `Add`, `Sub`, `Mult`, `Div`, `Pow`
- `ast.UnaryOp` with operator: `USub` (negation)
- `ast.Constant` where value is `int` or `float`
- `ast.Name` where `id` resolves to a known variable (row context or effects dict)

**Rejected AST nodes (raise `ValueError`):**
- `ast.Call` (no function calls)
- `ast.Attribute` (no attribute access)
- `ast.Subscript` (no indexing)
- `ast.Lambda`, `ast.IfExp`, `ast.Compare`
- Everything else not in the allowed list

**Variable resolution order:**
1. Effects dict (categorical effect values resolved for current row's predictor values)
2. Row context (other measure values from `rows` dict, already computed per topo order)
3. If unresolved: raise `ValueError(f"Undefined symbol '{name}' in formula")`

**Implementation structure in `engine/measures.py`:**

1. `_safe_eval_formula(formula: str, context: dict[str, float]) -> float`
   - Parse formula with `ast.parse(formula, mode='eval')`
   - Walk tree recursively, evaluating allowed nodes
   - Return scalar float result

2. `_resolve_effects(col_meta: dict, row: dict[str, Any], columns: dict) -> dict[str, float]`
   - For each effect name in `col_meta["effects"]`, look up the row's value for the corresponding categorical predictor column, then look up the numeric effect for that categorical value
   - Return `{effect_name: resolved_numeric_value}`

3. `_eval_structural(col_name, col_meta, rows, rng, overrides) -> np.ndarray`
   - For each row index:
     - Build context = {measure_name: rows[measure_name][i] for deps} + resolved effects
     - `base_value = _safe_eval_formula(col_meta["formula"], context)`
     - If `noise` is non-empty: add `rng.normal(0, noise["sigma"])` (or family-appropriate draw)
     - If `noise` is empty `{}`: no noise (deterministic)
   - Return ndarray of results

4. `_sample_stochastic(col_name, col_meta, rows, rng, overrides) -> np.ndarray`
   - Compute per-row parameters: for each param key, `theta = intercept + sum(effects)`
   - Clamp to valid ranges (P3 item): `sigma = max(sigma, 1e-6)`, `rate = max(rate, 1e-6)`
   - Dispatch by family:
     - `gaussian`: `rng.normal(mu, sigma)`
     - `lognormal`: `rng.lognormal(mu, sigma)`
     - `gamma`: `rng.gamma(shape=mu, scale=sigma)` (using mu as shape, sigma as scale)
     - `beta`: `rng.beta(mu, sigma)` (using mu as a, sigma as b)
     - `uniform`: `rng.uniform(mu, sigma)` (using mu as low, sigma as high)
     - `poisson`: `rng.poisson(mu)`
     - `exponential`: `rng.exponential(1/mu)` (rate parameterization)
     - `mixture`: raise `NotImplementedError` (P1 item)
   - If `overrides` contains this column, apply overridden param values before dispatch
   - Return ndarray of results

5. `generate_measures(columns, topo_order, rows, rng, overrides) -> dict`
   - Replace the current no-op stub
   - Iterate topo_order, skip non-measure columns
   - Dispatch to `_sample_stochastic` or `_eval_structural` based on `measure_type`
   - Store result in `rows[col_name]`

**Files:**
- `engine/measures.py` — all five functions above
- `sdk/validation.py` — no changes needed (declaration-time symbol extraction already works)

**Test criteria:**
- `_safe_eval_formula("a * 2 + b", {"a": 3.0, "b": 1.0})` returns `7.0`
- `_safe_eval_formula("a ** 2", {"a": 3.0})` returns `9.0`
- `_safe_eval_formula("import os", {})` raises `ValueError`
- `_safe_eval_formula("foo(a)", {"a": 1})` raises `ValueError` (no function calls)
- `_eval_structural` produces correct formula+effects+noise values for the one-shot example (`cost = wait_minutes * 12 + severity_surcharge`)
- `_sample_stochastic` produces values from the correct distribution family (verify via KS test with known parameters)
- `generate_measures` populates all measure columns in topo order
- Full pipeline `run_pipeline` returns a DataFrame with non-null measure columns

---

### P0-3: Auto-fix mutation semantics  <!-- ✅ RESOLVED — Loop B shipped; mixture opt-out auto-binding M1 (`893e7e9`) -->

**Modules:** M2, M5
**Stage3 refs:** M5-NC-6 (strategy implementations), M5-NC-7 (mutation target)
**Status:** DECIDE

#### Decision: Parameter override dict, not declaration store mutation

**Override type:** Define a simple type alias (not a new class) in `types.py`:

```python
# Parameter overrides for Loop B auto-fix
# Structure: {"measures": {col_name: {param_key: new_value}}, "patterns": {index: new_spec}}
ParameterOverrides = dict[str, Any]
```

**`generate_with_validation()` function in `validation/autofix.py`:**

```
def generate_with_validation(
    build_fn: Callable[[int, ParameterOverrides | None], tuple[pd.DataFrame, dict]],
    meta: dict[str, Any],
    patterns: list[dict[str, Any]],
    base_seed: int = 42,
    max_attempts: int = 3,
    auto_fix: dict[str, Any] | None = None,
) -> tuple[pd.DataFrame, dict, ValidationReport]:
```

**Algorithm:**
1. `overrides = {}`
2. For `attempt` in `range(max_attempts)`:
   a. `seed = base_seed + attempt`
   b. `df, meta = build_fn(seed, overrides)`  (this calls `run_pipeline` with `realism_config=None`)
   c. `report = SchemaAwareValidator(meta).validate(df, patterns)`
   d. If `report.all_passed`: apply realism (if configured), return `(df, meta, report)`
   e. For each failing check in `report.failures`:
      - `strategy = match_strategy(check.name, auto_fix)` (existing glob matcher)
      - If strategy found: `overrides = strategy(check, overrides)` (accumulate)
3. On exhaustion: apply realism to last df, return `(df, meta, report)` with failures

**Strategy-to-override mapping:**

Each strategy function must be updated to produce override entries rather than returning isolated dicts:

- `widen_variance(check, overrides)`:
  - Extract column name from `check.name` (e.g., `"ks_revenue"` -> `"revenue"`)
  - Set `overrides["measures"]["revenue"]["sigma"] *= factor`

- `amplify_magnitude(check, overrides)`:
  - Extract pattern index from `check.name` (e.g., `"outlier_wait_minutes"` -> find pattern with `col="wait_minutes"`)
  - Set `overrides["patterns"][idx]["params"]["z_score"] *= factor`

- `reshuffle_pair(check, overrides)`:
  - This strategy operates on the DataFrame directly, not via overrides
  - Apply as a post-generation transform: `overrides["reshuffle"] = [column_name]`
  - `run_pipeline` caller checks for `overrides["reshuffle"]` after generation

**Validation ordering:** Validate **pre-realism**. The `build_fn` callable must invoke `run_pipeline` with `realism_config=None`. Realism is applied only after validation passes (or after exhaustion).

**Override consumption in `engine/measures.py`:**
- In `_sample_stochastic`: before computing `theta`, check `if overrides and col_name in overrides.get("measures", {})`, and apply overridden values
- In `generate_measures`: after all measures, check `if overrides and "reshuffle" in overrides`, and apply column permutation

**Files:**
- `types.py` — add `ParameterOverrides` type alias
- `validation/autofix.py` — add `generate_with_validation()`, update existing strategy function signatures
- `engine/measures.py` — add override consumption (as part of P0-2 implementation)
- `engine/generator.py` — no changes needed (already accepts `overrides` param)

**Test criteria:**
- `generate_with_validation` returns on first attempt when all checks pass
- `generate_with_validation` increments seed on retry (`base_seed + attempt`)
- `widen_variance` increases sigma in overrides dict
- `amplify_magnitude` increases z_score in overrides dict
- After 3 failed attempts, function returns the last result with failures
- Validation runs pre-realism (measure finiteness check passes before NaN injection)

---

## P1 Items

---

### P1-1: `mixture` distribution `param_model` schema  <!-- ✅ RESOLVED (IS-1) — see ../stub_implementation/IS-1_DS-3_mixture.md -->

**ID:** M1-NC-1
**Status:** STUB

**Decision:** Accept `family="mixture"` at declaration time (already accepted — in `SUPPORTED_FAMILIES`). Do not add param_model validation for mixture. At generation time in `_sample_stochastic`, raise:

```python
raise NotImplementedError(
    "mixture distribution sampling not yet implemented. "
    "Expected param_model schema: {'components': [{'family': str, 'weight': float, 'params': {...}}, ...]}"
)
```

**Files:** `engine/measures.py`
**Test criteria:** `add_measure(name, "mixture", {...})` succeeds. Calling `generate()` with a mixture measure raises `NotImplementedError`.

---

### P1-2: Under-specified pattern type param schemas  <!-- ✅ RESOLVED (DS-2 + IS-2/IS-3/IS-4) — see ../stub_implementation/DS-2.md & IS-{2,3,4}_*.md -->

**ID:** M1-NC-6
**Status:** DECIDE

**Decision:** Add required params for two types. Stub two types.

Add to `PATTERN_REQUIRED_PARAMS` in `sdk/relationships.py`:

```python
PATTERN_REQUIRED_PARAMS = {
    "outlier_entity": frozenset({"z_score"}),
    "trend_break": frozenset({"break_point", "magnitude"}),
    "ranking_reversal": frozenset({"metrics", "entity_col"}),
    "dominance_shift": frozenset({"entity_filter", "col", "split_point"}),
    # convergence: no required params (fully unspecified)
    # seasonal_anomaly: no required params (fully unspecified)
}
```

Pattern injection in `engine/patterns.py` already raises `NotImplementedError` for all four types — this is correct and should remain.

**Files:** `sdk/relationships.py`
**Test criteria:**
- `inject_pattern("ranking_reversal", ...)` without `metrics` raises `ValueError`
- `inject_pattern("dominance_shift", ...)` without `entity_filter` raises `ValueError`
- `inject_pattern("convergence", ...)` with any params succeeds
- `inject_pattern("seasonal_anomaly", ...)` with any params succeeds

---

### P1-3: `dominance_shift` L3 validation  <!-- ✅ RESOLVED (IS-2) — see ../stub_implementation/IS-2_dominance_shift.md, ../fixes/H1_TEMPORAL_COERCION_ASYMMETRY.md, ../fixes/M2_M3_DEFENSIVE_GUARDS.md -->

**ID:** M5-NC-4
**Status:** STUB

**Decision:** Add stub function in `validation/pattern_checks.py`:

```python
def check_dominance_shift(df, pattern, meta):
    # TODO: Define as rank change of entity across temporal split
    # Expected params: entity_filter, col, split_point
    return Check(
        name=f"dominance_{pattern['col']}",
        passed=True,
        detail="dominance_shift validation not yet implemented",
    )
```

Wire into `SchemaAwareValidator._run_l3()` dispatch.

**Files:** `validation/pattern_checks.py`, `validation/validator.py`
**Test criteria:** Pattern type `dominance_shift` produces a Check with `passed=True` and "not yet implemented" detail.

---

### P1-4: `convergence` and `seasonal_anomaly` L3 validation  <!-- ✅ RESOLVED (IS-3, IS-4) — see ../stub_implementation/IS-3_convergence.md, IS-4_seasonal_anomaly.md -->

**ID:** M5-NC-5
**Status:** STUB

**Decision:** Add stub functions in `validation/pattern_checks.py`:

```python
def check_convergence(df, pattern, meta):
    return Check(name=f"convergence_{pattern['col']}", passed=True,
                 detail="convergence validation not yet implemented")

def check_seasonal_anomaly(df, pattern, meta):
    return Check(name=f"seasonal_{pattern['col']}", passed=True,
                 detail="seasonal_anomaly validation not yet implemented")
```

Wire into `SchemaAwareValidator._run_l3()` dispatch.

**Files:** `validation/pattern_checks.py`, `validation/validator.py`
**Test criteria:** Both produce Check with `passed=True`.

---

### P1-5: Sandbox semantics (M3, 6 items)  <!-- ✅ RESOLVED — token budget half (IS-6) shipped; multi-error half deferred per spec_decisions §IS-6 -->

**IDs:** M3-NC-1 through M3-NC-6
**Status:** ALREADY_IMPLEMENTED (4 of 6), accept-as-is (2 of 6)

| Item | Status | Notes |
|---|---|---|
| M3-NC-1: Sandbox isolation/timeout/reset | ALREADY_IMPLEMENTED | `exec()` in daemon thread, 30s timeout, fresh namespace per attempt |
| M3-NC-2: Non-SDK exception handling | ALREADY_IMPLEMENTED | Catches `Exception`, relays full traceback |
| M3-NC-3: Multiple simultaneous errors | Accept one-at-a-time | Add TODO comment in `sdk/simulator.py` |
| M3-NC-4: Context window exhaustion | Accept full history for 3 retries | Add TODO comment for token-budget check |
| M3-NC-5: `build_fact_table` signature enforcement | ALREADY_IMPLEMENTED | AST validation + runtime namespace check |
| M3-NC-6: Loop A terminal failure signal | ALREADY_IMPLEMENTED | `SkipResult` type with `scenario_id` and `error_log` |

**Files:** None required (documentation TODOs only)
**Test criteria:** Existing tests cover M3-NC-1, 2, 5, 6. No new tests needed.

---

## P2 Items

---

### P2-1: Realism injection semantics

**ID:** M2-NC-5
**Status:** ALREADY_IMPLEMENTED

`engine/realism.py` implements:
- `missing_rate`: uniform NaN injection via random mask
- `dirty_rate`: categorical-only character perturbation (swap/delete/insert)
- Missing runs before dirty (missing takes precedence)
- `censoring`: raises `NotImplementedError`

**Files:** None
**Test criteria:** Existing tests cover this.

---

### P2-2: Realism interaction with pattern signals

**ID:** M2-NC-7
**Status:** DECIDE (resolved by validation ordering)

**Decision:** No cell-marking mechanism needed. Validation runs pre-realism (see P2-3 below). Pattern signals are intact during validation. Realism can safely corrupt them afterward since validation has already passed.

The pipeline ordering in `engine/generator.py` (patterns at stage gamma, realism at stage delta) is already correct. The key is that `generate_with_validation()` (P0-3) invokes the pipeline with `realism_config=None` and applies realism only post-validation.

**Files:** None (resolved by P0-3 implementation)
**Test criteria:** Covered by P0-3 test criteria (validation pre-realism).

---

### P2-3: Validation ordering relative to realism

**ID:** M5-NC-8
**Status:** DECIDE (resolved by P0-3)

**Decision:** Validate **pre-realism**. The `generate_with_validation()` Loop B wrapper invokes `run_pipeline` with `realism_config=None`. Realism is applied only after all validation passes (or after retry exhaustion). This prevents L1/L2/L3 false failures caused by intentional data degradation.

**Files:** `validation/autofix.py` (part of P0-3)
**Test criteria:** Covered by P0-3 test criteria.

---

### P2-4: Multi-column `on` in group dependency  <!-- ✅ RESOLVED (DS-4) — N-deep nested dict; see ../stub_implementation/DS-4.md -->

**ID:** M1-NC-5
**Status:** DECIDE

**Decision:** Restrict to single-column `on` for v1. Add validation at the top of `add_group_dependency` in `sdk/relationships.py`:

```python
if len(on) != 1:
    raise NotImplementedError(
        f"Multi-column 'on' is not supported in v1. "
        f"Got on={on} (length {len(on)}). Use a single column."
    )
```

Keep the `on: list[str]` parameter type for forward compatibility.

**Files:** `sdk/relationships.py`
**Test criteria:**
- `add_group_dependency(child, on=["col_a"], ...)` succeeds
- `add_group_dependency(child, on=["col_a", "col_b"], ...)` raises `NotImplementedError`
- `add_group_dependency(child, on=[], ...)` raises `ValueError`

---

### P2-5: `scale` parameter on `add_measure`  <!-- ⛔ NOT restored (IS-5 — doc-only; passing `scale=…` raises TypeError); see ../remaining_gaps.md §4.2, ../fixes/PROMPT_TRUTH_AND_DIVZERO_GUARD.md -->

**ID:** M1-NC-2
**Status:** DECIDE

**Decision:** Keep accepting and storing. Add a warning when non-None. In `sdk/columns.py`, after storing `scale`:

```python
if scale is not None:
    col_meta["scale"] = scale
    logger.warning(
        "add_measure: 'scale' parameter (%.4f) for '%s' is stored but "
        "has no effect in the current implementation.",
        scale, name,
    )
```

**Files:** `sdk/columns.py`
**Test criteria:** `add_measure(name, family, pm, scale=2.0)` succeeds and logs a warning. `col_meta["scale"]` equals `2.0`.

---

### P2-6: `censoring` parameter in `set_realism`  <!-- ✅ RESOLVED (DS-1) — see ../stub_implementation/DS-1.md -->

**ID:** M1-NC-7
**Status:** ALREADY_IMPLEMENTED

`set_realism` stores `censoring` in the config dict. `engine/realism.py` raises `NotImplementedError` when `censoring is not None`.

**Files:** None
**Test criteria:** Existing tests cover this.

---

## P3 Items

---

### P3-1: Negative distribution parameters from additive effects

**ID:** M1-NC-10
**Status:** DECIDE (deferred to P0-2 implementation)

**Decision:** Clamp at generation time in `_sample_stochastic` (P0-2), not at declaration time. After computing `theta = intercept + sum(effects)` for each row:

```python
# Clamp to valid domain
if param_key == "sigma" or param_key == "scale":
    theta = max(theta, 1e-6)
    if theta != original_theta:
        logger.warning("Clamped %s.%s from %.6f to %.6f", col_name, param_key, original_theta, theta)
elif param_key == "rate":
    theta = max(theta, 1e-6)
```

**Files:** `engine/measures.py` (implement within P0-2)
**Test criteria:** `sigma = 0.35 + (-0.5)` produces `sigma = 1e-6` (clamped) with a warning logged.

---

### P3-2: Per-parent conditional weight coverage

**ID:** M1-NC-3
**Status:** ALREADY_IMPLEMENTED

`sdk/validation.py:validate_and_normalize_dict_weights` and `sdk/relationships.py:add_group_dependency` both check for missing parent-value keys and raise `ValueError`.

**Files:** None
**Test criteria:** Existing tests cover this.

---

### P3-3: Orthogonal + dependency contradiction

**ID:** M1-NC-4
**Status:** ALREADY_IMPLEMENTED

`sdk/relationships.py` has bidirectional conflict detection:
- `_check_orthogonal_conflict` called from `add_group_dependency`
- `_check_dependency_conflict` called from `declare_orthogonal`

Both raise `ValueError` on contradictory declarations.

**Files:** None
**Test criteria:** Existing tests cover this.

---

### P3-4: Column name uniqueness enforcement

**ID:** M1-NC-8
**Status:** ALREADY_IMPLEMENTED

`sdk/validation.py:validate_column_name` raises `DuplicateColumnError`. Called by all `add_*` functions.

**Files:** None
**Test criteria:** Existing tests cover this.

---

### P3-5: Effects referencing undeclared columns

**ID:** M1-NC-9
**Status:** ALREADY_IMPLEMENTED

`sdk/validation.py:validate_effects_in_param` raises `UndefinedEffectError` when an effect references a column not yet in the `OrderedDict`.

**Files:** None
**Test criteria:** Existing tests cover this.

---

### P3-6: Step 1 / Step 2 ordering enforcement

**ID:** M1-NC-11
**Status:** DECIDE

**Decision (part a — phase flag):** Add an internal phase state to `FactTableSimulator` in `sdk/simulator.py`:

```python
# In __init__:
self._phase: str = "declaring"  # "declaring" or "relating"

# Transition method:
def _ensure_relating_phase(self) -> None:
    self._phase = "relating"

def _ensure_declaring_phase(self) -> None:
    if self._phase == "relating":
        raise InvalidParameterError(
            param_name="phase",
            value=0.0,
            reason="Column declarations (Step 1) must come before relationship "
                   "declarations (Step 2). A Step 2 method has already been called."
        )
```

- Call `_ensure_declaring_phase()` at the start of `add_category`, `add_temporal`, `add_measure`, `add_measure_structural`
- Call `_ensure_relating_phase()` at the start of `declare_orthogonal`, `add_group_dependency`, `inject_pattern`, `set_realism`

**Decision (part b — target_rows):** Already implemented. `simulator.py:38` raises `ValueError` for `target_rows <= 0`.

**Files:** `sdk/simulator.py`
**Test criteria:**
- Calling `add_category` after `declare_orthogonal` raises `InvalidParameterError`
- Calling `add_category` then `declare_orthogonal` then `add_category` raises
- Normal flow (all Step 1 then all Step 2) succeeds
- `FactTableSimulator(target_rows=0)` raises `ValueError`
- `FactTableSimulator(target_rows=-5)` raises `ValueError`

---

### P3-7: Pattern composition when targets overlap

**ID:** M2-NC-3
**Status:** ALREADY_IMPLEMENTED (implicit)

`engine/patterns.py:inject_patterns` applies patterns in declaration (list) order. Sequential mutation means the second pattern overwrites the first on overlapping cells. This is correct.

**Decision:** Add a documentation comment at the top of `inject_patterns`:

```python
# Pattern composition: patterns are applied in declaration order.
# Overlapping targets compose by sequential mutation — later patterns
# overwrite earlier ones on the same cells.
```

**Files:** `engine/patterns.py` (comment only)
**Test criteria:** None (documentation).

---

### P3-8: Pattern injection on structural measures breaking L2 residual check

**ID:** M2-NC-4
**Status:** DECIDE (deferred to L2 implementation)

**Decision:** When `check_structural_residuals` is implemented in `validation/statistical.py`, exclude rows matching any pattern's `target` filter for the same `col`. Implementation:

```python
# In check_structural_residuals:
pattern_mask = pd.Series(False, index=df.index)
for p in patterns:
    if p["col"] == col_name:
        pattern_mask |= df.eval(p["target"])
clean_df = df[~pattern_mask]
# Compute residuals on clean_df only
```

**Files:** `validation/statistical.py` (when L2 is implemented)
**Test criteria:** L2 residual check passes when pattern-modified rows are present (they're excluded from the residual computation).

---

### P3-9: `_post_process(rows)` behavior

**ID:** M2-NC-2
**Status:** ALREADY_IMPLEMENTED

`engine/postprocess.py:to_dataframe` converts to DataFrame with RangeIndex, casts temporal to `datetime64`, temporal_derived to `int64`/`bool`, categorical to `object`. No value clipping or rounding.

**Files:** None
**Test criteria:** Existing tests cover this.

---

### P3-10: Structural measure `noise={}` default

**ID:** M2-NC-6
**Status:** DECIDE (deferred to P0-2 implementation)

**Decision:** `noise={}` means zero noise (deterministic formula output). In `_eval_structural` (P0-2):

```python
noise_config = col_meta.get("noise", {})
if noise_config:
    sigma = noise_config.get("sigma", 0.0)
    if sigma > 0:
        values += rng.normal(0, sigma, size=len(values))
# else: no noise added
```

In `check_structural_residuals` (when L2 is implemented):
```python
noise_sigma = col_meta.get("noise", {}).get("sigma", 0.0)
if noise_sigma == 0 or not noise_sigma:
    # Deterministic formula — residuals should be near-zero
    passed = residuals.std() < 1e-6
else:
    passed = abs(residuals.std() - noise_sigma) / noise_sigma < 0.2
```

**Files:** `engine/measures.py` (P0-2), `validation/statistical.py` (L2 implementation)
**Test criteria:**
- Structural measure with `noise={}` produces exact formula values (residual std < 1e-6)
- Structural measure with `noise={"family": "gaussian", "sigma": 30}` produces noisy values

---

### P3-11: `_build_schema_metadata()` location

**ID:** M2-NC-8
**Status:** ALREADY_IMPLEMENTED

M4 is a standalone module at `metadata/builder.py`. `engine/generator.py:run_pipeline` imports and calls `build_schema_metadata` from M4. Clean module boundary preserved.

**Files:** None
**Test criteria:** N/A.

---

### P3-12: M4 DataFrame dependency

**ID:** M4-NC-2
**Status:** ALREADY_IMPLEMENTED

`build_schema_metadata()` accepts only declaration-store data (groups, columns, orthogonal_pairs, etc.). No DataFrame parameter. M4 can execute in parallel with M2.

**Files:** None
**Test criteria:** N/A.

---

### P3-13: Metadata internal consistency validation

**ID:** M4-NC-3
**Status:** ALREADY_IMPLEMENTED

`_assert_metadata_consistency()` checks four cross-reference conditions with warning-level logging. Defense-in-depth, not hard failure.

**Files:** None
**Test criteria:** N/A.

---

### P3-14: M5 data source

**ID:** M5-NC-1
**Status:** ALREADY_IMPLEMENTED (by P0-1)

M5 consumes only the enriched `schema_metadata` dict from M4. No direct access to declaration store needed.

**Files:** None
**Test criteria:** N/A.

---

### P3-15: L2 structural residual divide-by-zero guard

**ID:** M5-NC-2
**Status:** DECIDE (deferred to L2 implementation)

**Decision:** Same as P3-10 validation side. When `noise_sigma` is 0 or absent, check `residuals.std() < 1e-6` instead of the ratio test. See P3-10 for code.

**Files:** `validation/statistical.py`
**Test criteria:** L2 residual check on a zero-noise structural measure passes when formula is computed correctly.

---

### P3-16: L2 KS-test predictor cell enumeration

**ID:** M5-NC-3
**Status:** DECIDE (deferred to L2 implementation)

**Decision:** Implement `iter_predictor_cells` as:

1. For a stochastic measure, identify all categorical columns referenced in `param_model[*]["effects"]`
2. Compute Cartesian product of those columns' value sets
3. For each cell in the product, filter DataFrame rows matching all predictor values
4. Skip cells with fewer than 5 rows (unreliable KS test)
5. Cap at 100 tested cells (sorted by cell size descending — test largest cells first)
6. Run `scipy.stats.kstest` per cell with expected distribution parameters

**Files:** `validation/statistical.py`
**Test criteria:**
- Predictor cell enumeration skips cells with < 5 rows
- Caps at 100 cells
- KS test passes for data generated from the declared distribution

---

## Implementation Order Notes

Based on dependency analysis, implement in this order:

1. **P0-1 M5 gaps** (2 missing L1 checks) — no dependencies, quick win
2. **P0-2** (formula evaluator + stochastic sampling) — largest task, unblocks L2 and Loop B
3. **P1-1** (mixture stub) — trivial, do alongside P0-2
4. **P1-2** (pattern param schemas) — trivial declaration-time addition
5. **P1-3, P1-4** (L3 validation stubs) — trivial, wire into validator
6. **P2-4** (multi-column on restriction) — one-line guard
7. **P2-5** (scale warning) — one-line warning
8. **P3-6** (phase flag) — small addition to simulator
9. **P3-7** (pattern overlap comment) — documentation only
10. **P0-3** (auto-fix Loop B) — depends on P0-2 being complete
11. **L2 checks** (P3-8, P3-10, P3-15, P3-16) — depend on P0-2 and P0-3

Items marked ALREADY_IMPLEMENTED need only verification, not implementation.
