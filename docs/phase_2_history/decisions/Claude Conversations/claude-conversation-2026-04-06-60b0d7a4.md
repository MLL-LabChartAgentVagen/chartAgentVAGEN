# Claude Conversation Log

Session ID: 60b0d7a4-331f-42e8-9cfd-fd5390f0f666
Date: 2026-04-06 01:02:02

---

## 👤 User

Analyze the three P0 blockers against the current codebase.

The P0 blockers from stage3 are:
- P0-1: Enrich schema_metadata beyond §2.6 example (M4 + M5)
- P0-2: Formula evaluation mechanism for structural measures (M1 + M2)
- P0-3: Auto-fix mutation semantics (M2 + M5)

For each P0, read the stage3 entry, the stage4 entry, and then read the actual source files:
- P0-1: ../phase_2/metadata/builder.py, ../phase_2/validation/structural.py, ../phase_2/validation/statistical.py, ../phase_2/validation/pattern_checks.py
- P0-2: ../phase_2/engine/measures.py, ../phase_2/sdk/validation.py
- P0-3: ../phase_2/validation/autofix.py, ../phase_2/engine/generator.py

Report what exists, what's missing, and whether stage3's suggested resolution is still correct.

---

## 🤖 Claude

I'll start by reading all the reference documents and source files in parallel.

---

## 🤖 Claude

Let me read stage4 in parts and all source files in parallel.

---

## 🤖 Claude

Now let me check if there are additional L1 checks (marginal weights, measure finiteness) that I might have missed, and look at the validator orchestrator.

---

## 🤖 Claude

Let me also check if there's a `generate_with_validation` function anywhere, and check the types file for the override mechanism.

---

## 🤖 Claude

Now I have a complete picture. Here's the P0 gap analysis:

---

## P0 Gap Analysis

---

### P0-1: Enrich `schema_metadata` beyond §2.6 example (M4 + M5)

**Current code state:**

[builder.py](../phase_2/metadata/builder.py) is **substantially implemented** and already addresses the P0-1 enrichment. The `_build_columns_metadata()` function (lines 114–175) emits enriched type-discriminated descriptors:
- Categoricals: `values`, `weights`, `cardinality`, `group`, `parent`
- Temporals: `start`, `end`, `freq`, `derive`, `group`
- Stochastic measures: `family`, `param_model` (deep-copied)
- Structural measures: `formula`, `effects`, `noise`
- Group dependencies: `conditional_weights` (via `dep.to_metadata()`)
- Patterns: `type`, `target`, `col`, `params`

A `_assert_metadata_consistency()` function (lines 194–252) does cross-reference validation (warns, doesn't raise).

**M5 consumers — current state:**
- [structural.py](../phase_2/validation/structural.py): L1 checks are **implemented** — row count, cardinality, orthogonal chi-squared, DAG acyclicity. However, **two L1 checks are missing**: marginal weight check and measure finiteness check. No function exists for either.
- [statistical.py](../phase_2/validation/statistical.py): L2 checks are **stubs** (all raise `NotImplementedError`). The helper `max_conditional_deviation()` is implemented, but `check_stochastic_ks`, `check_structural_residuals`, and `check_group_dependency_transitions` are all blocked stubs.
- [pattern_checks.py](../phase_2/validation/pattern_checks.py): L3 checks for `outlier_entity` and `trend_break` are **fully implemented**. No checks for `ranking_reversal`, `dominance_shift`, `convergence`, or `seasonal_anomaly`.
- [validator.py](../phase_2/validation/validator.py): Orchestrator calls L1 and L3 but **skips L2 entirely** (commented as "stubs pending Blockers 2 & 3").

**Gap:**

1. **M4 builder is done.** The enrichment decision from stage3 has already been implemented. The metadata dict includes all fields M5 needs.
2. **M5 has two missing L1 checks**: `check_marginal_weights` (root column observed vs. declared weight deviation < 0.10) and `check_measure_finiteness` (`notna().all()` and `isfinite().all()`). These are spec-ready and should have been implemented but weren't.
3. **L2 checks remain fully blocked** — the stubs correctly identify they depend on measure generation (P0-2) and auto-fix (P0-3).
4. **`_assert_metadata_consistency` uses warnings, not raises** — stage3 item M4-NEEDS_CLAR-3 suggested validation. The current implementation logs warnings but doesn't fail, which is a design choice, not a gap.

**Stage3 suggestion assessment:**

The suggestion to "enrich `schema_metadata`" is **already implemented**. The M4 side of P0-1 is resolved. The M5 side has partial gaps (two missing L1 checks) that are spec-ready and don't require a decision — they just need to be coded.

**Preliminary decision: Accept (already implemented for M4). Note M5 gaps for implementation phase.**

---

### P0-2: Formula evaluation mechanism for structural measures (M1 + M2)

**Current code state:**

- [measures.py](../phase_2/engine/measures.py): **Fully stubbed.** `generate_measures()` (lines 19–63) iterates topo order but generates nothing — logs debug messages and returns rows unchanged. `_sample_stochastic()` and `_eval_structural()` both raise `NotImplementedError`. There is **no formula evaluation logic at all**.
- [sdk/validation.py](../phase_2/sdk/validation.py): Formula **symbol extraction** exists (`extract_formula_symbols()` at line 554 using regex `[a-zA-Z_][a-zA-Z0-9_]*`), and structural effects validation exists (`validate_structural_effects()` at line 467). But these are declaration-time checks — they don't evaluate formulas.
- [generator.py](../phase_2/engine/generator.py): `run_pipeline()` calls `_measures.generate_measures()` which is the stub above. The pipeline accepts an `overrides` parameter and passes it through, which is good scaffolding for P0-3.

**Gap:**

This is the **largest unresolved P0**. Everything needed for stage β is missing:
1. **Formula evaluator**: No AST-based or restricted evaluator exists. The regex-based symbol extractor in `sdk/validation.py` is for declaration-time validation only.
2. **Stochastic sampling**: No distribution-family dispatch (`gaussian` → `rng.normal()`, etc.). No intercept+effects→parameter computation.
3. **Structural computation**: No formula string evaluation against row context. No effects overlay. No noise addition.
4. **Mixture distribution**: No schema or sampling logic at all.
5. **Negative parameter clamping**: No guard against computed σ < 0.

**Stage3 suggestion assessment:**

The suggestion — "restricted AST-based evaluator: `ast.parse(formula, mode='eval')`, walk the tree, allow only arithmetic operators, numeric literals, and variable names" — is **correct and sufficient**. The codebase has no competing approach. The symbol extractor in `sdk/validation.py` already uses regex for declaration-time extraction, so the runtime evaluator should use `ast` for safe evaluation (consistent with stage4's recommendation).

**Preliminary decision: Accept.** Implement a restricted `ast`-based evaluator in `measures.py`. Also implement stochastic sampling (all families except `mixture`, which is P1). Use `ast.parse(formula, mode='eval')` → walk tree → allow `BinOp` (`Add`, `Sub`, `Mult`, `Div`, `Pow`), `UnaryOp` (`USub`), `Constant` (numeric), and `Name` (resolved from row context + effects). No `Call`, `Attribute`, `Subscript`.

---

### P0-3: Auto-fix mutation semantics (M2 + M5)

**Current code state:**

- [autofix.py](../phase_2/validation/autofix.py): Three strategy functions exist and are **partially implemented**:
  - `widen_variance(check, params, factor)` — multiplies `sigma` or `scale` by a factor. Works on a plain params dict, returns a new dict. **Implemented but isolated** — operates on a params dict, not connected to the pipeline.
  - `amplify_magnitude(check, pattern_spec, factor)` — multiplies `z_score` or `magnitude` by a factor. Deep-copies the pattern spec. **Implemented but isolated.**
  - `reshuffle_pair(check, df, column, rng)` — permutes a column in the DataFrame. **Implemented but isolated.**
  - `match_strategy(check_name, auto_fix)` — glob-based dispatch. **Implemented.**
- **Missing entirely:** The `generate_with_validation()` Loop B wrapper function. No grep hits anywhere in the codebase. The retry loop (seed=base+attempt, max 3 retries) that invokes validation, dispatches auto-fix, and re-invokes generation **does not exist**.
- [generator.py](../phase_2/engine/generator.py): `run_pipeline()` accepts an `overrides` parameter and passes it to `generate_measures()`, but `generate_measures()` ignores it (stub). There is **no `ParameterOverrides` type** — `overrides` is just `dict | None`.

**Gap:**

1. **No `generate_with_validation()` function**: The Loop B retry wrapper is completely absent. This is the core orchestration piece that ties validation failures to auto-fix strategies to re-generation.
2. **No override mechanism in generation**: `run_pipeline()` accepts `overrides` but nothing consumes them. The strategy functions produce modified params/specs, but there's no pathway to feed those back into re-generation.
3. **Strategy functions are isolated**: `widen_variance` returns a new params dict, `amplify_magnitude` returns a new pattern spec, and `reshuffle_pair` returns a modified DataFrame. These are correctly pure, but the **glue** that maps Check failures → strategy dispatch → override accumulation → re-invocation is missing.
4. **No `ParameterOverrides` type**: Stage4 suggested a typed override dict, but none exists in `types.py`.

**Stage3 suggestion assessment:**

The suggestion — "strategies mutate a `ParameterOverrides` dict, not the frozen `DeclarationStore`; `build_fn` in Loop B should be `sim.generate()` with overrides" — is **correct and consistent with the existing scaffolding**. The `overrides` parameter in `run_pipeline()` already anticipates this pattern. The strategy functions already return new dicts rather than mutating in place.

However, stage3 underspecified the **mapping from Check failures to override targets**. For example, when `widen_variance` returns `{"sigma": 4.2}`, where does that go? Which measure? The `check.name` (e.g., `"ks_revenue"`) needs to map back to a column name and parameter path. This mapping logic is not specified.

**Preliminary decision: Modify.** Accept the override-dict approach, but add:
- A `ParameterOverrides` dataclass or typed dict in `types.py` with clear structure: `{column_name: {param_key: new_value}}` for measures, `{pattern_index: new_pattern_spec}` for patterns.
- The `generate_with_validation()` function in `autofix.py` implementing: validate → on failure, dispatch strategy → accumulate overrides → re-invoke `run_pipeline(store, seed=base+attempt, overrides)` → max 3 attempts.
- The override consumption path in `measures.py` (once P0-2 is implemented): before drawing from a distribution, check if overrides has a replacement param value for this column.

---

## Summary

| P0 | Status | Decision |
|----|--------|----------|
| **P0-1** (metadata enrichment) | M4 builder: **done**. M5 consumers: 2 missing L1 checks, L2 fully stubbed | **Accept** — already implemented for M4. Code the 2 missing L1 checks. L2 unblocks after P0-2. |
| **P0-2** (formula evaluator) | **Not started.** All of stage β is stubbed. | **Accept** — restricted `ast`-based evaluator + stochastic family dispatch. Largest implementation task. |
| **P0-3** (auto-fix mutation) | Strategy functions exist but isolated. `generate_with_validation()` Loop B wrapper is **missing**. No override consumption path. | **Modify** — accept override-dict approach but define `ParameterOverrides` type and the Check→override mapping glue. |

P0 gap analysis complete. Send 'Phase B' when ready, or ask questions about any P0 finding.

---

## 👤 User

Phase B

---

## 🤖 Claude

I need to read all remaining source files that the P1/P2/P3 items touch. Let me do this in parallel.

---

## 🤖 Claude

Let me check two more things — the `_phase` flag and the code validator.

---

## 🤖 Claude

Now let me check the types and exceptions files for completeness.

---

## 🤖 Claude

Now I have everything. Here's the complete P1/P2/P3 analysis.

---

## P1/P2/P3 Gap Analysis

---

## P1 Items

### P1 Cluster 1: `mixture` distribution `param_model` schema

**M1-NEEDS_CLAR-1: `mixture` distribution `param_model` schema**
- **Current code state:** `"mixture"` is in the `SUPPORTED_FAMILIES` frozenset in [sdk/validation.py:31](../phase_2/sdk/validation.py#L31), but it has no entry in `VALIDATED_PARAM_KEYS` (only `gaussian` and `lognormal` do). This means `add_measure` accepts `family="mixture"` without any param_model validation. On the generation side, `_sample_stochastic` in [engine/measures.py](../phase_2/engine/measures.py) is a stub — no sampling logic exists for any family, including mixture.
- **Decision:** Stub with NotImplementedError. Accept the declaration (store the param_model), but raise `NotImplementedError("mixture distribution sampling not yet implemented")` at generation time. Define the expected schema as a TODO comment per stage3's suggestion: `{"components": [{"family": "gaussian", "weight": 0.6, "params": {...}}, ...]}`.
- **Rationale:** No spec confirmation of the component schema exists; implementing now risks wasted work.
- **Files affected:** [engine/measures.py](../phase_2/engine/measures.py) (generation-time guard), [sdk/validation.py](../phase_2/sdk/validation.py) (TODO comment documenting expected schema)

---

### P1 Cluster 2: Under-specified pattern types (params + validation)

**M1-NEEDS_CLAR-6: Pattern parameter schemas for `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`**
- **Current code state:** [sdk/relationships.py:27-36](../phase_2/sdk/relationships.py#L27-L36) lists all six types in `VALID_PATTERN_TYPES` but only defines `PATTERN_REQUIRED_PARAMS` for `outlier_entity` and `trend_break`. The four under-specified types are accepted at declaration time with **no params validation**.
- **Decision:** Modify. For `ranking_reversal` and `dominance_shift`, add required params based on §2.9 L3 validation code. For `ranking_reversal`: `{"metrics": [str, str], "entity_col": str}`. For `dominance_shift`: `{"entity_filter": str, "col": str, "split_point": str}`. For `convergence` and `seasonal_anomaly`: accept any params, stub both injection and validation.
- **Rationale:** `ranking_reversal` has L3 validation pseudocode in §2.9 that constrains its params. `dominance_shift` has a partial spec. The other two have nothing.
- **Files affected:** [sdk/relationships.py](../phase_2/sdk/relationships.py) (param schemas), [engine/patterns.py](../phase_2/engine/patterns.py) (injection stubs already raise NotImplementedError — correct), [validation/pattern_checks.py](../phase_2/validation/pattern_checks.py) (add L3 checks for ranking_reversal/dominance_shift)

**M5-NEEDS_CLAR-4: L3 `dominance_shift` validation logic**
- **Current code state:** No `check_dominance_shift` function exists in [pattern_checks.py](../phase_2/validation/pattern_checks.py). The validator orchestrator silently skips unknown pattern types.
- **Decision:** Stub with `Check(passed=True, detail="dominance_shift validation not yet implemented")`. Define expected params as TODO.
- **Rationale:** §2.9 delegates to an opaque `_verify_dominance_change()` with no body shown.
- **Files affected:** [validation/pattern_checks.py](../phase_2/validation/pattern_checks.py)

**M5-NEEDS_CLAR-5: Missing validation for `convergence` and `seasonal_anomaly`**
- **Current code state:** No functions for either in [pattern_checks.py](../phase_2/validation/pattern_checks.py). Silently skipped.
- **Decision:** Accept stage3 suggestion. Stub both as `Check(passed=True, detail="not implemented")`.
- **Rationale:** Completely absent from §2.9 validation logic.
- **Files affected:** [validation/pattern_checks.py](../phase_2/validation/pattern_checks.py), [validation/validator.py](../phase_2/validation/validator.py) (dispatch these in `_run_l3`)

---

### P1 Cluster 3: Sandbox semantics and non-SDK error handling

**M3-NEEDS_CLAR-1: Sandbox execution semantics (isolation, timeout, state reset)**
- **Current code state:** **Already implemented** in [orchestration/sandbox.py](../phase_2/orchestration/sandbox.py). Uses `exec()` in a daemon thread with configurable timeout (default 30s). Each retry in `run_retry_loop` calls `ns_factory()` to create a **fresh namespace** per attempt (line 637), achieving state reset. Restricted `__builtins__` allowlist blocks `__import__`, `eval`, `exec`, `open`.
- **Decision:** Accept — already resolved as stage3 suggested.
- **Rationale:** Code matches the suggested resolution exactly.
- **Files affected:** None (implemented)

**M3-NEEDS_CLAR-2: Handling of non-SDK exceptions (SyntaxError, NameError, etc.)**
- **Current code state:** **Already implemented.** `_SandboxThread.run()` catches `Exception` (all subclasses) at [sandbox.py:219](../phase_2/orchestration/sandbox.py#L219) and captures both the exception and formatted traceback. `format_error_feedback()` relays the full traceback regardless of exception type.
- **Decision:** Accept — already resolved.
- **Rationale:** Catches `Exception` broadly, exactly as stage3 suggested.
- **Files affected:** None (implemented)

**M3-NEEDS_CLAR-3: Multiple simultaneous SDK errors**
- **Current code state:** Standard Python exception propagation (one per run). No multi-error collection exists.
- **Decision:** Accept stage3 suggestion. Accept one-at-a-time as the default. Document as a future enhancement.
- **Rationale:** Building multi-error collection is non-trivial and the 3-retry budget is workable.
- **Files affected:** None (document only, as TODO comment in [sdk/simulator.py](../phase_2/sdk/simulator.py))

**M3-NEEDS_CLAR-4: Context window exhaustion strategy**
- **Current code state:** `run_retry_loop` in [sandbox.py](../phase_2/orchestration/sandbox.py) accumulates full history but only passes the most recent error feedback to the LLM (line 682). No token-budget check exists.
- **Decision:** Accept stage3 suggestion. Keep full history for 3 retries. Add a TODO for token-budget check before retry when model token limits are known.
- **Rationale:** 3 retries × (script + traceback) is manageable for current model context windows.
- **Files affected:** None (document only)

**M3-NEEDS_CLAR-5: `build_fact_table` function signature enforcement**
- **Current code state:** **Already implemented** via two mechanisms: (1) [code_validator.py](../phase_2/orchestration/code_validator.py) uses AST visitors to verify `def build_fact_table(...)` exists and `.generate()` is called. (2) [sandbox.py:209-214](../phase_2/orchestration/sandbox.py#L209-L214) retrieves `build_fact_table` from namespace and raises `RuntimeError` if missing.
- **Decision:** Accept — already resolved. Both AST-level pre-validation and runtime enforcement exist.
- **Rationale:** Two-layer enforcement exceeds the stage3 suggestion.
- **Files affected:** None (implemented)

**M3-NEEDS_CLAR-6: Loop A terminal failure → upstream signal**
- **Current code state:** [retry_loop.py:15-50](../phase_2/orchestration/retry_loop.py#L15-L50) defines `orchestrate()` which returns `SkipResult` on failure. `SkipResult` is defined in [exceptions.py](../phase_2/exceptions.py) with `scenario_id` and `error_log` fields. `RetryLoopResult` (from `sandbox.py`) has `success=False` with full history on exhaustion.
- **Decision:** Accept — already resolved. `SkipResult` type exists. The orchestrator stub returns it correctly.
- **Rationale:** Matches stage3's suggestion of a typed skip signal.
- **Files affected:** None (implemented)

---

## P2 Items

### P2 Cluster 1: Realism injection semantics and validation interaction

**M2-NEEDS_CLAR-5: Realism injection semantics**
- **Current code state:** **Already implemented** in [engine/realism.py](../phase_2/engine/realism.py). `missing_rate` applies uniformly via `rng.random() < missing_rate` → NaN mask. `dirty_rate` applies to **categorical columns only** via `perturb_string()` (character-level swap/delete/insert). Missing runs first, then dirty (avoids perturbing cells that will be NaN'd). Censoring raises `NotImplementedError`.
- **Decision:** Accept — already resolved exactly per stage3 suggestion.
- **Rationale:** Missing takes precedence (runs first), dirty is categoricals-only, censoring is stubbed.
- **Files affected:** None (implemented)

**M2-NEEDS_CLAR-7: Realism interaction with pattern signals**
- **Current code state:** In [generator.py](../phase_2/engine/generator.py), patterns (stage γ) run at line 94, then realism (stage δ) at line 99. **No mechanism exists** to protect pattern-modified cells from realism injection.
- **Decision:** Modify stage3 suggestion. Instead of cell-marking during stage γ, use the simpler approach: validate pre-realism. The pipeline already applies patterns before realism. If validation runs before realism (per M5-NEEDS_CLAR-8 below), pattern signals are preserved for validation, and realism can safely corrupt them afterward since it's post-validation.
- **Rationale:** Cell-marking adds complexity. Pre-realism validation achieves the same protection.
- **Files affected:** [validation/autofix.py](../phase_2/validation/autofix.py) (Loop B must validate pre-realism), [engine/generator.py](../phase_2/engine/generator.py) (pipeline ordering is already correct — γ then δ)

**M5-NEEDS_CLAR-8: Validation ordering relative to realism**
- **Current code state:** No `generate_with_validation()` exists yet (P0-3 gap). The pipeline in [generator.py](../phase_2/engine/generator.py) runs patterns then realism, but validation is not called from within the generator.
- **Decision:** Accept stage3 suggestion. Validate **pre-realism**. The Loop B wrapper (`generate_with_validation`) should invoke `run_pipeline` with `realism_config=None`, validate the clean DataFrame, and only apply realism after validation passes.
- **Rationale:** L1/L2/L3 test properties that realism intentionally degrades. Validating post-realism would cause systematic false failures.
- **Files affected:** [validation/autofix.py](../phase_2/validation/autofix.py) (Loop B implementation)

---

### P2 Cluster 2: Multi-column `on` in group dependency

**M1-NEEDS_CLAR-5: Multi-column `on`**
- **Current code state:** `add_group_dependency` in [sdk/relationships.py:96-196](../phase_2/sdk/relationships.py#L96-L196) accepts `on: list[str]` but only uses `on[0]` throughout (lines 132, 139, 143, 152, 165). The DAG acyclicity check at line 139 only passes `on[0]`. Multi-column conditioning is structurally unsupported.
- **Decision:** Accept stage3 alternative: restrict to single-column `on` for v1. Add validation: `if len(on) != 1: raise NotImplementedError("Multi-column 'on' is not supported in v1")`. Keep the `list` type for forward compatibility.
- **Rationale:** The `conditional_weights` dict structure for joint conditioning (tuple keys) is unspecified. Single-column covers the demonstrated use case.
- **Files affected:** [sdk/relationships.py](../phase_2/sdk/relationships.py) (add len check)

---

### P2 Cluster 3: Undocumented parameters (`scale`, `censoring`)

**M1-NEEDS_CLAR-2: `scale` parameter on `add_measure`**
- **Current code state:** `add_measure` in [sdk/columns.py:214-250](../phase_2/sdk/columns.py#L214-L250) accepts `scale: Optional[float] = None` and stores it in `col_meta["scale"]` only when non-None (line 242-243). No code anywhere reads or uses it. The prompt template in [prompt.py:51](../phase_2/orchestration/prompt.py#L51) lists `scale=None` in the SDK method signature.
- **Decision:** Accept stage3 suggestion. Keep accepting and storing. Treat as no-op. Add a `logger.warning` if non-None.
- **Rationale:** Present in the API surface but never defined. Storing preserves forward compatibility.
- **Files affected:** [sdk/columns.py](../phase_2/sdk/columns.py) (add warning)

**M1-NEEDS_CLAR-7: `censoring` parameter in `set_realism`**
- **Current code state:** `set_realism` in [sdk/relationships.py:260-299](../phase_2/sdk/relationships.py#L260-L299) accepts `censoring: Optional[dict] = None` and stores it. [engine/realism.py:58-62](../phase_2/engine/realism.py#L58-L62) raises `NotImplementedError` when `censoring is not None`.
- **Decision:** Accept — already resolved. Accept and store the opaque dict, raise at generation time. This is exactly the stage3 suggestion.
- **Rationale:** Already implemented as suggested.
- **Files affected:** None (implemented)

---

## P3 Items

### P3 Cluster 1: Negative distribution parameters from additive effects

**M1-NEEDS_CLAR-10: Negative distribution parameters**
- **Current code state:** No clamping exists anywhere. `_sample_stochastic` in [engine/measures.py](../phase_2/engine/measures.py) is a stub. `validate_param_model` in [sdk/validation.py](../phase_2/sdk/validation.py) validates structure but not numeric ranges of computed parameters.
- **Decision:** Accept stage3 suggestion. Clamp at generation time (not declaration time) when computing `θⱼ = β₀ + Σₘ βₘ(Xₘ)`. E.g., `sigma = max(sigma, 1e-6)`. Log a warning when clamping activates.
- **Rationale:** Effects are additive per-cell, so clamping must be per-row at draw time, not at declaration.
- **Files affected:** [engine/measures.py](../phase_2/engine/measures.py) (implement inside `_sample_stochastic` when P0-2 is resolved)

### P3 Cluster 2: Per-parent weight coverage + orthogonal/dependency contradiction + column uniqueness + effects timing + step ordering

**M1-NEEDS_CLAR-3: Per-parent conditional weight dict — missing parent values**
- **Current code state:** **Already implemented.** [sdk/validation.py:166-223](../phase_2/sdk/validation.py#L166-L223) `validate_and_normalize_dict_weights` checks `missing_keys = parent_values - provided_keys` and raises `ValueError` (lines 200-206). Same check exists in `add_group_dependency` at [sdk/relationships.py:150-158](../phase_2/sdk/relationships.py#L150-L158).
- **Decision:** Accept — already resolved. Raises at declaration time when parent values are missing.
- **Rationale:** Both `add_category` (per-parent weights) and `add_group_dependency` enforce complete coverage.
- **Files affected:** None (implemented)

**M1-NEEDS_CLAR-4: Orthogonal + dependency contradiction**
- **Current code state:** **Already implemented.** [sdk/relationships.py:306-342](../phase_2/sdk/relationships.py#L306-L342) has `_check_orthogonal_conflict` (called from `add_group_dependency`) and `_check_dependency_conflict` (called from `declare_orthogonal`). Both raise `ValueError` for contradictory declarations.
- **Decision:** Accept — already resolved. Bidirectional conflict detection at declaration time.
- **Rationale:** Stage3 suggested `ConflictingRelationError`; the code uses `ValueError` which is functionally equivalent.
- **Files affected:** None (implemented)

**M1-NEEDS_CLAR-8: Column name uniqueness enforcement**
- **Current code state:** **Already implemented.** [sdk/validation.py:57-71](../phase_2/sdk/validation.py#L57-L71) `validate_column_name` raises `DuplicateColumnError`. Called by all four `add_*` functions in [sdk/columns.py](../phase_2/sdk/columns.py).
- **Decision:** Accept — already resolved.
- **Files affected:** None (implemented)

**M1-NEEDS_CLAR-9: Effects referencing columns not yet declared**
- **Current code state:** **Already implemented.** `validate_effects_in_param` in [sdk/validation.py:402-460](../phase_2/sdk/validation.py#L402-L460) checks `if col_name not in columns` and raises `UndefinedEffectError`. Since columns are in an `OrderedDict`, only previously-declared columns exist at validation time.
- **Decision:** Accept — already resolved. Validates at declaration time as stage3 suggested.
- **Files affected:** None (implemented)

**M1-NEEDS_CLAR-11: Step 1/Step 2 ordering enforcement + `target_rows` validation**
- **Current code state:** `target_rows` validation is **implemented** — [simulator.py:38](../phase_2/sdk/simulator.py#L38) raises `ValueError` if `target_rows <= 0`. However, there is **no `_phase` flag** for step ordering. No grep hits for `_phase` or `_frozen` in simulator.py. Nothing prevents calling `add_category` after `declare_orthogonal`.
- **Decision:** Modify. Add an internal `_phase` enum (`"declaring"` / `"relating"`) to `FactTableSimulator`. Transition on first call to any Step 2 method. Reject Step 1 calls after transition with a clear error message.
- **Rationale:** Without enforcement, LLM-generated scripts could violate HC3 silently, leading to subtle ordering bugs.
- **Files affected:** [sdk/simulator.py](../phase_2/sdk/simulator.py) (add `_phase` flag and transition logic)

### P3 Cluster 3: Pattern overlap composition + structural measure interaction

**M2-NEEDS_CLAR-3: Pattern composition when targets overlap**
- **Current code state:** [engine/patterns.py:29-82](../phase_2/engine/patterns.py#L29-L82) `inject_patterns` iterates patterns in list order and applies them sequentially. Two overlapping patterns compose by sequential mutation — exactly the stage3 suggestion. No explicit handling or documentation of this behavior.
- **Decision:** Accept — already resolved implicitly. Declaration order = application order. Add a brief comment documenting this.
- **Rationale:** Sequential mutation in declaration order is the simplest correct approach.
- **Files affected:** [engine/patterns.py](../phase_2/engine/patterns.py) (documentation comment only)

**M2-NEEDS_CLAR-4: Pattern injection on structural measures breaking L2 residual check**
- **Current code state:** L2 `check_structural_residuals` is a stub (raises `NotImplementedError`). No exclusion logic exists.
- **Decision:** Accept stage3 suggestion. When L2 residual checks are implemented, exclude rows matching any pattern's `target` filter for the same `col`. Implement as part of the L2 residual check (not in the pattern injector).
- **Rationale:** Pattern injection legitimately overrides formula-derived values. The residual check must account for this.
- **Files affected:** [validation/statistical.py](../phase_2/validation/statistical.py) (implement when L2 is unblocked)

### Remaining unclustered items

**M2-NEEDS_CLAR-2: `_post_process(rows)` behavior**
- **Current code state:** **Already implemented** in [engine/postprocess.py](../phase_2/engine/postprocess.py). Converts to DataFrame, assigns RangeIndex, casts temporal → `datetime64`, temporal_derived → `int64`/`bool`, categorical → `object`. No value clipping or rounding.
- **Decision:** Accept — already resolved per stage3 suggestion.
- **Files affected:** None (implemented)

**M2-NEEDS_CLAR-6: Structural measure `noise={}` default**
- **Current code state:** `add_measure_structural` in [sdk/columns.py:276](../phase_2/sdk/columns.py#L276) defaults `noise` to `{}`. The generation stub doesn't use it yet. No L2 residual check exists to hit the divide-by-zero case.
- **Decision:** Accept stage3 suggestion. `noise={}` means zero noise (deterministic formula). Skip noise draw. L2 residual check uses `residuals.std() < 1e-6` when `noise_sigma` is 0 or absent.
- **Rationale:** Consistent with the mathematical interpretation (no noise term).
- **Files affected:** [engine/measures.py](../phase_2/engine/measures.py) (handle in `_eval_structural` when P0-2 is resolved), [validation/statistical.py](../phase_2/validation/statistical.py) (guard in residual check when L2 is implemented)

**M2-NEEDS_CLAR-8: `_build_schema_metadata()` location — M2 vs M4**
- **Current code state:** **Already resolved.** M4 is a standalone module at [metadata/builder.py](../phase_2/metadata/builder.py). `generator.py` calls `build_schema_metadata()` from M4 at [generator.py:102](../phase_2/engine/generator.py#L102). Clean module boundary.
- **Decision:** Accept — already resolved per stage3 suggestion.
- **Files affected:** None (implemented)

**M4-NEEDS_CLAR-2: Whether M4 needs the generated DataFrame**
- **Current code state:** `build_schema_metadata()` in [metadata/builder.py](../phase_2/metadata/builder.py) takes only declaration-store data (groups, columns, orthogonal_pairs, etc.). No DataFrame parameter. Can run in parallel with M2.
- **Decision:** Accept — already resolved. M4 does not need the DataFrame.
- **Files affected:** None (implemented)

**M4-NEEDS_CLAR-3: Metadata internal consistency validation**
- **Current code state:** **Already implemented.** `_assert_metadata_consistency()` at [builder.py:194-252](../phase_2/metadata/builder.py#L194-L252) checks cross-references (dim group columns, DAG order, pattern cols, orthogonal groups). Uses `logger.warning` rather than raising.
- **Decision:** Accept — already resolved. Warning-level (not raising) is appropriate since these are defense-in-depth checks.
- **Files affected:** None (implemented)

**M5-NEEDS_CLAR-1: M5's actual data source**
- **Current code state:** Resolved by P0-1. M4 emits enriched metadata with all fields M5 references. M5 consumes only the metadata dict.
- **Decision:** Accept — resolved by P0-1.
- **Files affected:** None (resolved)

**M5-NEEDS_CLAR-2: L2 structural residual — divide by zero when `noise_sigma = 0`**
- **Current code state:** `check_structural_residuals` is a stub (raises `NotImplementedError`).
- **Decision:** Accept stage3 suggestion. When implemented: if `noise_sigma` is 0 or absent, check `residuals.std() < 1e-6` instead of the ratio test.
- **Rationale:** Mathematical guard for the deterministic-formula case.
- **Files affected:** [validation/statistical.py](../phase_2/validation/statistical.py) (implement when L2 is unblocked)

**M5-NEEDS_CLAR-3: L2 KS-test predictor cell enumeration**
- **Current code state:** `check_stochastic_ks` is a stub (raises `NotImplementedError`). No `iter_predictor_cells` function exists anywhere.
- **Decision:** Accept stage3 suggestion. Iterate Cartesian product of predictor columns in the measure's `effects`. Skip cells with < 5 rows. Cap tested cells at 100.
- **Rationale:** Small-sample cells produce unreliable KS tests; capping prevents combinatorial explosion.
- **Files affected:** [validation/statistical.py](../phase_2/validation/statistical.py) (implement when L2 is unblocked)

---

## Summary Table

| Priority | Item | Status | Decision |
|----------|------|--------|----------|
| **P1** | Mixture param_model schema | Accepted at declaration, no generation | Stub generation with NotImplementedError |
| **P1** | 4 under-specified pattern params | Accepted without validation | Add param schemas for ranking_reversal/dominance_shift; stub convergence/seasonal_anomaly |
| **P1** | dominance_shift L3 validation | Missing | Stub as Check(passed=True) |
| **P1** | convergence/seasonal_anomaly L3 | Missing | Stub as Check(passed=True) |
| **P1** | Sandbox semantics (6 items) | 4 already implemented, 2 accept-as-is | Accept — mostly resolved |
| **P2** | Realism semantics | Implemented | Accept |
| **P2** | Realism × pattern interaction | No protection mechanism | Validate pre-realism (resolves interaction) |
| **P2** | Validation vs realism ordering | No Loop B yet | Validate pre-realism |
| **P2** | Multi-column `on` | `on[0]` only used | Restrict to single-column for v1 |
| **P2** | `scale` parameter | Stored, unused | Accept + log warning |
| **P2** | `censoring` parameter | Stub (NotImplementedError) | Accept — already resolved |
| **P3** | Negative distribution params | No clamping | Clamp at generation time |
| **P3** | Per-parent weight coverage | Implemented | Accept — already resolved |
| **P3** | Orthogonal+dependency conflict | Implemented | Accept — already resolved |
| **P3** | Column uniqueness | Implemented | Accept — already resolved |
| **P3** | Effects timing | Implemented | Accept — already resolved |
| **P3** | Step 1/2 ordering | **Not implemented** (no `_phase` flag) | Modify — add phase enforcement |
| **P3** | Pattern overlap composition | Implicit sequential order | Accept — add comment |
| **P3** | Pattern on structural L2 | L2 is stub | Exclude pattern rows when L2 implemented |
| **P3** | `_post_process` behavior | Implemented | Accept |
| **P3** | `noise={}` default | Not yet used | Zero noise, guard in L2 |
| **P3** | Schema metadata location | M4 standalone | Accept — already resolved |
| **P3** | M4 needs DataFrame? | No — declaration only | Accept — already resolved |
| **P3** | Metadata consistency check | Implemented (warnings) | Accept |
| **P3** | M5 data source | Resolved by P0-1 | Accept |
| **P3** | L2 noise_sigma=0 guard | L2 is stub | Guard when implemented |
| **P3** | L2 predictor cell enumeration | L2 is stub | Cartesian product, skip <5 rows, cap 100 |

**Key finding:** 15 of 33 non-P0 items are **already implemented** in the current codebase. The remaining items are either stubs awaiting P0-2 unblock (L2 checks, measure generation) or minor additions (phase flag, param schemas, warning logs).

P1/P2/P3 analysis complete. Send 'Phase C' when ready, or ask questions about any decision.

---

## 👤 User

Phase C

---

## 🤖 Claude

Writing the binding decision document now.

---

## 🤖 Claude

Decision document written to [blocker_resolutions.md](blocker_resolutions.md).

**Summary of what's in the document:**

- **36 NEEDS_CLAR items** analyzed across 5 modules
- **15 items** found to be **ALREADY_IMPLEMENTED** in the current codebase (no work needed beyond verification)
- **3 P0 decisions** locked:
  - P0-1: M4 metadata enrichment is done; 2 missing L1 checks noted for implementation
  - P0-2: Restricted `ast`-based formula evaluator + full stochastic family dispatch — the largest task
  - P0-3: Parameter override dict approach for Loop B, with `generate_with_validation()` wrapper
- **6 P1 items**: mixture stub, pattern param schemas for 4 types, 3 L3 validation stubs, sandbox items (mostly done)
- **6 P2 items**: realism (done), validation ordering (pre-realism via P0-3), multi-column `on` restricted to single, scale warning, censoring (done)
- **16 P3 items**: 10 already implemented, phase flag enforcement needed, rest deferred to L2 implementation
- **Implementation order** at the bottom, sequenced by dependencies

The implementation engineer can now consume this as a fixed directive. Each item has an ID, status, decision, affected files, and test criteria.

---

