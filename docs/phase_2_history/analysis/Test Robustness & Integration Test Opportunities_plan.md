# Analysis: Test Robustness & Integration Test Opportunities

## Context

We have 525 unit tests passing across 27 test files. The question: are these tests robust enough to prove the modules are correct? This analysis identifies where unit tests pass but the integrated system could still fail, and catalogs every integration/E2E test opportunity.

## Current State Assessment

**The test suite is heavily unit-tested but dangerously weak on integration.** Most tests mock downstream modules, so they prove orchestration logic but not data contract correctness.

### Mock vs Real Test Ratio

| Module | Tests | % Mocked | Real Integration? |
|---|---|---|---|
| engine/generator.py | 10 | 80% (8 mock, 2 real seed tests) | Minimal |
| engine/skeleton.py | 42 | 0% — all real | Good unit, no downstream |
| engine/patterns.py | 16 | 20% (dispatcher mocked) | Injection real, no validation roundtrip |
| engine/realism.py | 18 | 0% — all real | Good unit, no validation roundtrip |
| engine/measures.py | 14 | 0% — all real | Good unit, never consumed by generator |
| validation/validator.py | 17 | 95% (all L1/L2/L3 mocked) | Orchestration only |
| validation/structural.py | 13 | 0% — all real | Good unit |
| validation/statistical.py | 16 | 0% — all real | Good unit |
| pipeline.py | 21 | 100% — all mocked | None |
| orchestration/sandbox.py | 23 | 30% (retry mocks LLM) | Sandbox real |
| orchestration/llm_client.py | 23 | 30% (generate mocks SDK) | Init/adapter real |
| test_end_to_end.py | 29 | 10% — mostly real | Best coverage |

### What test_end_to_end.py Already Covers

The E2E file has 29 tests covering:
- SDK declarations → run_pipeline → DataFrame output (happy path)
- Categorical, hierarchical, temporal column generation
- Stochastic and structural measure generation
- Pattern injection (outlier, trend_break) on generated data
- Realism injection (missing, dirty)
- Orthogonal independence (chi-squared statistical test)
- Group dependency conditional distribution
- Loop B retry with seed offset
- Auto-fix override accumulation
- Full medical scenario end-to-end

**But all E2E tests expect success.** No test verifies failure detection, error recovery, or auto-fix actually fixing anything.

---

## Gap 1: Module Boundary Contract Tests (5 boundaries)

These are the seams where unit tests pass but integration could fail.

### 1A. M1→M2 (SDK → Engine)

**What crosses:** `columns: OrderedDict`, `groups: dict[str, DimensionGroup]`, `measure_dag`, `group_dependencies`, `patterns`, `orthogonal_pairs`

**Risk:** SDK builds column descriptors with specific keys (`type`, `values`, `weights`, `parent`, `family`, `param_model`, etc.). Engine's skeleton/measures/patterns modules assume these keys exist. No test verifies a malformed column descriptor causes a clear error rather than silent garbage.

**Test opportunity:**
- Verify engine rejects/handles missing required keys in column descriptors
- Verify engine handles empty groups, empty columns, empty measure_dag gracefully
- Verify SDK's exact output structure is consumed by engine without KeyError

### 1B. M2→M4 (Engine → Metadata Builder)

**What crosses:** `columns`, `groups`, `orthogonal_pairs`, `measure_dag_order`, `group_dependencies`, `patterns`, `target_rows`

**Risk:** Builder's `columns` parameter is optional (`None` defaults to `{}`). If engine ever passes `None`, metadata silently has empty columns and validator silently skips all L2 checks.

**Test opportunity:**
- Verify builder output is consumable by validator without KeyError
- Verify all enrichment fields (values, weights, param_model, formula, effects, noise) survive the engine→builder→validator chain

### 1C. M4→M5 (Metadata → Validation)

**What crosses:** 7-key metadata dict consumed by `SchemaAwareValidator(meta)`

**Risk:** Validator reads `meta["total_rows"]`, `meta["columns"]`, `meta["dimension_groups"]`, etc. If any key is missing, behavior is undefined (KeyError or silent skip). L2 checks silently return empty list if `meta["columns"]` is None or not a dict (validator.py:108).

**Test opportunity:**
- Verify metadata from real `build_schema_metadata()` has all fields validator needs
- Verify missing/None `columns` in metadata causes predictable behavior
- Verify each L1/L2/L3 check works with real (not mocked) metadata from the builder

### 1D. M5→M2 (Validation → Engine via Loop B auto-fix)

**What crosses:** `ParameterOverrides` dict with structure `{"measures": {col: {param: value}}, "patterns": {idx: patch}}`

**Risk:** Auto-fix strategies produce override dicts. Engine's `_sample_stochastic` must consume `overrides["measures"][col_name]`. No test verifies the override dict structure produced by strategies is what the engine actually reads.

**Test opportunity:**
- Verify `widen_variance` output is consumed by `_sample_stochastic` and changes sigma
- Verify `amplify_magnitude` output is consumed by `_apply_pattern_overrides` and changes z_score
- Verify the full loop: validation fails → auto-fix → re-generate → validation passes

### 1E. M3→Pipeline (Sandbox → Loop B) — **BUG FOUND**

**What crosses:** `raw_declarations` dict extracted from sandbox's `_TrackingSimulator`

**BUG:** `sandbox.py:434-442` extracts 7 fields but **omits `orthogonal_pairs`**. `pipeline.py:180-202` builds `run_pipeline()` call without `orthogonal_pairs`. On Loop B retry, orthogonal independence constraints are silently dropped.

**Evidence:**
- sandbox.py:434-442: `raw_declarations` has no `"orthogonal_pairs"` key
- pipeline.py:192-202: `run_pipeline()` call has no `orthogonal_pairs=` argument
- Result: Loop B retries produce data without orthogonal constraints from Loop A

**Test opportunity:**
- Verify raw_declarations includes orthogonal_pairs
- Verify Loop B build_fn passes orthogonal_pairs to run_pipeline

---

## Gap 2: Validation Failure Detection Tests

No test currently verifies that the validator actually CATCHES problems.

### 2A. L1 Failure Detection

**Untested scenarios:**
- Row count mismatch (e.g., engine produces 90 rows when target is 100)
- Cardinality violation (column has unexpected values)
- Marginal weight deviation > 0.10
- Measure with NaN or Inf values
- Orthogonal groups that are NOT independent (chi-squared fails)
- Cyclic measure DAG

**Test opportunity:** For each L1 check, construct a DataFrame that intentionally violates the constraint and verify the check returns `passed=False`.

### 2B. L2 Failure Detection

**Untested scenarios:**
- Stochastic measure drawn from wrong distribution (KS test fails)
- Structural measure residuals outside tolerance
- Group dependency conditional distribution mismatched

**Test opportunity:** Generate data with wrong parameters, verify L2 detects the discrepancy.

### 2C. L3 Failure Detection

**Untested scenarios:**
- Outlier entity with z-score < 2.0 (too weak to detect)
- Trend break with magnitude < 15% (too small)
- Ranking reversal with positive correlation (no reversal)

**Test opportunity:** Inject weak/absent patterns, verify L3 returns `passed=False`.

---

## Gap 3: Roundtrip Tests (Inject → Detect)

### 3A. Pattern Injection → Validation Roundtrip

**Current state:** Pattern injection tested in isolation (test_engine_patterns.py). Pattern validation tested in isolation (test_validation_pattern.py). Never tested together.

**Test opportunity:**
- Generate data → inject outlier_entity → validate with check_outlier_entity → verify passed=True
- Generate data → inject trend_break → validate with check_trend_break → verify passed=True
- Generate data → do NOT inject pattern → validate → verify passed=False

### 3B. Realism → Validation Roundtrip

**Current state:** Realism injection tested in isolation. Never validated that realistic data still passes structural checks.

**Test opportunity:**
- Generate → inject realism (missing_rate=0.05) → run L1 checks → do they still pass?
- Generate → inject realism (missing_rate=1.0) → run L1 measure finiteness → should fail

### 3C. Auto-fix Loop Roundtrip

**Current state:** Auto-fix strategies tested in isolation. `generate_with_validation` tested with fake metadata. Never tested with a REAL validation failure that auto-fix actually resolves.

**Test opportunity:**
- Construct scenario where initial generation fails KS test (wrong sigma)
- Verify widen_variance strategy increases sigma in overrides
- Verify re-generation with overrides produces data that passes KS test

---

## Gap 4: Agentic Path Tests

### 4A. LLM Code → Sandbox → Validation

**Current state:** sandbox tests use hardcoded scripts. Never tests that the kind of code an LLM would generate actually works in the sandbox.

**Test opportunity:**
- Execute the one-shot example from the prompt template in the sandbox
- Verify it produces a valid (DataFrame, dict) tuple
- Verify the output passes validation

### 4B. Error Feedback → Fix Cycle

**Current state:** format_error_feedback tested for structure. Never tested that the feedback actually contains enough information to fix the issue.

**Test opportunity:**
- Generate code with a known bug → sandbox fails → format feedback → verify feedback contains the error context that would help an LLM fix it

---

## Gap 5: Edge Case / Negative Tests

### 5A. Empty Schema

- SDK with 0 columns → generate() → what happens?
- SDK with only temporal columns, no measures → generate() → valid but empty measures?

### 5B. Extreme Parameters

- target_rows=1 (single row)
- target_rows=100000 (large scale)
- missing_rate=1.0 (all NaN)
- dirty_rate=1.0 (all perturbed)
- z_score=0.0 (no outlier shift)
- magnitude=0.0 (no trend break)

### 5C. Concurrent Constraints

- Orthogonal groups + group dependency on same pair (should be caught at SDK time but is it?)
- Multiple patterns on same column (composition order)
- Structural measure depending on measure that depends on it (cycle)

---

## Gap 6: Per-Module Start-to-End Tests (No Internal Mocking)

Current unit tests test individual functions within each module. Per-module S2E tests treat each module as a **black box** — real inputs in, real outputs verified, zero internal mocking. This catches bugs where internal functions work individually but the module's overall orchestration is broken.

### 6A. M1 SDK Module S2E

Test the full FactTableSimulator lifecycle without mocking engine internals.

**Tests:**
- `test_sdk_minimal_schema` — add_category + add_measure + generate() → valid DataFrame with correct columns, types, row count
- `test_sdk_full_schema` — all declaration types (categorical hierarchy, temporal+derivation, stochastic measure, structural measure, orthogonal, group_dependency, pattern, realism) → generate() → DataFrame + metadata both correct
- `test_sdk_phase_enforcement_through_generate` — Step 1 → Step 2 → generate → freeze enforced
- `test_sdk_validation_errors_raised_correctly` — duplicate column, cyclic DAG, undeclared effect → correct exception types with structured messages

### 6B. M2 Engine Module S2E

Test `run_pipeline()` with real column dicts (no SDK wrapper), verifying every stage fires correctly.

**Tests:**
- `test_engine_categorical_only` — 2 categorical columns → DataFrame with correct values/weights distribution
- `test_engine_with_hierarchy` — parent+child categorical → child values conditional on parent
- `test_engine_with_temporal` — temporal + derived columns → datetime + int/bool types
- `test_engine_with_stochastic_measure` — gaussian measure with effects → correct parameter computation (KS test)
- `test_engine_with_structural_measure` — formula-based measure → correct formula evaluation
- `test_engine_with_patterns` — outlier + trend_break injected → detectable in output
- `test_engine_with_realism` — missing_rate + dirty_rate applied → NaN count matches rate
- `test_engine_full_pipeline` — all stages together → complete DataFrame + metadata

### 6C. M4 Metadata Module S2E

Test `build_schema_metadata()` with real SDK-produced data structures.

**Tests:**
- `test_metadata_from_real_sdk_declarations` — FactTableSimulator declarations → extract registries → build_schema_metadata → verify all 7 keys, all enrichment fields (values, weights, param_model, formula, effects, noise, conditional_weights, pattern params)
- `test_metadata_consistency_passes_on_valid_input` — no warnings logged for well-formed input
- `test_metadata_consumed_by_validator_without_error` — build metadata → pass to SchemaAwareValidator → validate() runs without KeyError

### 6D. M5 Validation Module S2E

Test `SchemaAwareValidator.validate()` with real metadata and real DataFrames (not mocked check functions).

**Tests:**
- `test_validator_passes_on_clean_generated_data` — real run_pipeline output → all L1/L2/L3 pass
- `test_validator_catches_row_count_mismatch` — tamper df to have wrong row count → L1 fails
- `test_validator_catches_cardinality_violation` — inject extra category value → L1 fails
- `test_validator_catches_weight_deviation` — skew distribution → L1 fails
- `test_validator_catches_measure_nan` — inject NaN → L1 finiteness fails
- `test_validator_detects_injected_outlier` — inject pattern → L3 passes
- `test_validator_detects_injected_trend_break` — inject pattern → L3 passes
- `test_validator_rejects_absent_pattern` — no injection → L3 fails

### 6E. M5 Auto-fix Loop S2E

Test `generate_with_validation()` with a real build_fn (not mocked).

**Tests:**
- `test_autofix_passes_on_first_attempt` — clean data → 1 attempt, all pass
- `test_autofix_retries_with_seed_offset` — construct scenario where seed=42 fails but seed=43 passes
- `test_autofix_applies_widen_variance` — construct scenario where initial sigma is too tight → widen_variance increases it → retry passes

### 6F. M3 Orchestration Module S2E

Test the orchestration chain with real prompt rendering, real code validation, real sandbox (mock only the LLM).

**Tests:**
- `test_orchestration_prompt_to_sandbox` — render_system_prompt → generate code (hardcoded valid code) → execute_in_sandbox → returns valid result
- `test_orchestration_code_validation_rejects_bad_code` — validate_generated_code on code missing build_fact_table → CodeValidationResult.is_valid=False
- `test_orchestration_retry_loop_with_real_sandbox` — initial bad code → sandbox fails → format_error_feedback → mock LLM returns good code → sandbox succeeds → RetryLoopResult.success=True

### 6G. Pipeline Module S2E

Test `run_phase2()` or `_run_loop_b()` with real engine + real validation (mock only LLM).

**Tests:**
- `test_pipeline_loop_b_real_generation` — real raw_declarations → real run_pipeline → real validation → passes
- `test_pipeline_loop_b_with_real_autofix` — scenario where first attempt fails validation → auto-fix → retry → passes
- `test_pipeline_full_direct_sdk_path` — FactTableSimulator → generate → validate → complete result (no LLM, no sandbox)

---

## Summary: Recommended Test Categories

| Category | Tests Needed | Priority | Proves |
|---|---|---|---|
| **Per-module start-to-end** | ~30 | **HIGHEST** | Each module works as a complete unit |
| **Module boundary contracts** | ~10 | HIGH | Data structures match across boundaries |
| **Validation failure detection** | ~12 | HIGH | Validator catches real problems |
| **Inject → detect roundtrips** | ~8 | HIGH | Patterns/realism work end-to-end |
| **Auto-fix loop roundtrip** | ~3 | MEDIUM | Loop B actually fixes issues |
| **Agentic path** | ~3 | MEDIUM | LLM code → sandbox → validation works |
| **Edge cases / negative** | ~8 | LOW | System handles extremes gracefully |
| **Bug fix: orthogonal_pairs** | 1 fix + 1 test | **CRITICAL** | Loop B preserves constraints |
| **Total** | **~75** | | |

Note: Some per-module S2E tests overlap with boundary contract and roundtrip tests. When combined, the actual unique test count is likely ~60-65.
