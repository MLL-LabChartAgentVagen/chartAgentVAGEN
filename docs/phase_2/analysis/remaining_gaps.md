# AGPDS Phase 2 — Remaining Gaps Reference

**Date:** 2026-04-07
**Status after this session:** ranking_reversal validation implemented, DeclarationStore.freeze() integrated. This document captures everything that remains.
**Updated 2026-04-07:** Structural/packaging gaps 2.1, 2.2, 2.3, and 2.5 resolved.

---

## 1. Remaining Intentional Stubs (5)

These are stubbed per explicit decisions in `decisions/blocker_resolutions.md`. Each requires either spec clarification or a design decision before implementation.

### 1.1 Mixture Distribution Sampling (P1-1 / M1-NC-1)

- **Location:** `phase_2/engine/measures.py:298-303`
- **What:** `_sample_stochastic()` raises `NotImplementedError` when `family == "mixture"`.
- **Why stubbed:** The `param_model` schema for mixture distributions (component families, mixing weights, per-component parameters) is not defined in the spec. Zero examples exist.
- **Current behavior:** `add_measure("x", "mixture", {...})` succeeds at declaration time (family is in `SUPPORTED_FAMILIES`). Calling `generate()` with a mixture measure raises `NotImplementedError`.
- **Related stub:** Mixture KS test in `validation/statistical.py:259-264` returns `passed=True` with "mixture distribution KS test not yet implemented".
- **To unstub:** Define the param_model schema (suggested: `{"components": [{"family": "gaussian", "weight": 0.6, "params": {"mu": {...}, "sigma": {...}}}, ...]}`). Implement weighted-component sampling in `_sample_stochastic`. Implement the corresponding KS test decomposition in `statistical.py`.
- **Decision ref:** blocker_resolutions.md P1-1

### 1.2 Dominance Shift Validation (P1-3 / M5-NC-4)

- **Location:** `phase_2/validation/pattern_checks.py:167-191`
- **What:** `check_dominance_shift()` returns `Check(passed=True, detail="dominance_shift validation not yet implemented")`.
- **Why stubbed:** The validation logic is opaque in the spec — `self._verify_dominance_change(df, p, meta)` is named but never defined. The params schema (`entity_filter`, `col`, `split_point`) is specified in `PATTERN_REQUIRED_PARAMS` (relationships.py:37), but the actual rank-change-across-temporal-split algorithm is not specified.
- **Current behavior:** Dominance shift patterns can be declared (params validated at declaration time), but validation always passes.
- **To unstub:** Define the algorithm: filter to entity, compute metric rank before/after `split_point`, check that rank changed as declared. Requires spec author input on what "dominance" means quantitatively.
- **Decision ref:** blocker_resolutions.md P1-3

### 1.3 Convergence Validation (P1-4 / M5-NC-5)

- **Location:** `phase_2/validation/pattern_checks.py:194-217`
- **What:** `check_convergence()` returns `Check(passed=True, detail="convergence validation not yet implemented")`.
- **Why stubbed:** Completely absent from the spec's §2.9 validation section. No params schema, no validation logic, no examples. Listed in the pattern type enum but never elaborated.
- **Current behavior:** Convergence patterns can be declared (no required params per `PATTERN_REQUIRED_PARAMS`), but validation always passes.
- **To unstub:** Requires full spec definition: what converges, over what dimension, what threshold constitutes convergence.
- **Decision ref:** blocker_resolutions.md P1-4

### 1.4 Seasonal Anomaly Validation (P1-4 / M5-NC-5)

- **Location:** `phase_2/validation/pattern_checks.py:220-243`
- **What:** `check_seasonal_anomaly()` returns `Check(passed=True, detail="seasonal_anomaly validation not yet implemented")`.
- **Why stubbed:** Same as convergence — completely absent from spec. No params, no validation logic.
- **Current behavior:** Same as convergence — declaration succeeds, validation always passes.
- **To unstub:** Requires full spec definition: what constitutes a seasonal anomaly, which temporal features to check, detection thresholds.
- **Decision ref:** blocker_resolutions.md P1-4

### 1.5 M3 Context Window / Multi-Error (M3-NC-3, M3-NC-4)

- **Location (NC-3):** `phase_2/sdk/simulator.py:32-36` — TODO comment noting one-error-at-a-time limitation.
- **Location (NC-4):** `phase_2/orchestration/retry_loop.py:656-660` — TODO comment noting no token-budget check.
- **What:** (NC-3) The sandbox catches one exception per execution; multiple simultaneous SDK errors are surfaced one per retry. (NC-4) Full error history is sent to the LLM without truncation.
- **Why accepted:** Both are acceptable for the default `max_retries=3`. NC-3 would require M1 to implement multi-error collection. NC-4 would require token counting and history summarization.
- **Current behavior:** Both are functional — they work correctly within the 3-retry budget. They're accepted limitations, not broken functionality.
- **To fix:** NC-3: Collect validation errors into a compound exception in M1. NC-4: Add token counting before each retry; truncate/summarize older failures if budget exceeded.
- **Decision ref:** blocker_resolutions.md P1-5

---

## 2. Structural / Packaging Gaps (Not in 80-Item Audit)

These are infrastructure issues discovered during the post-audit codebase scan. None block the core SDK or agentic paths, but they affect package quality.

### ~~2.1 `pyproject.toml` Has Empty Dependencies~~ — RESOLVED

- **Location:** `pyproject.toml`
- **Resolution:** Added `numpy>=1.24`, `pandas>=2.0`, `scipy>=1.10` to `dependencies`.

### ~~2.2 `run_phase2` Not Re-exported from `phase_2/__init__.py`~~ — RESOLVED

- **Location:** `phase_2/__init__.py`
- **Resolution:** Added `from phase_2.pipeline import run_phase2` and `"run_phase2"` to `__all__`. `from phase_2 import run_phase2` now works.

### ~~2.3 `FactTableSimulator` Not Re-exported from `phase_2/sdk/__init__.py`~~ — RESOLVED

- **Location:** `phase_2/sdk/__init__.py`
- **Resolution:** Added `from phase_2.sdk.simulator import FactTableSimulator` and `__all__ = ["FactTableSimulator"]`. `from phase_2.sdk import FactTableSimulator` now works.

### 2.4 `ColumnDescriptor` Type Not Defined

- **Location:** `phase_2/types.py` — absent
- **Problem:** Stage4 specifies a `ColumnDescriptor` dataclass as the canonical per-column record flowing from M1 into M2 and M4. The codebase uses `OrderedDict[str, dict[str, Any]]` instead. A TODO at types.py:371 says: "Will be progressively migrated to typed ColumnDescriptor list in future batches."
- **Impact:** Low — functionally correct, but no compile-time type safety on column metadata. All column metadata is untyped dicts.
- **Fix (future):** Define `ColumnDescriptor` dataclass with discriminated union fields (`type`, `group`, `parent`, `family`, `param_model`, `formula`, `effects`, `noise`, `derive`, `values`, `weights`, `scale`). Migrate `OrderedDict[str, dict]` to `list[ColumnDescriptor]`. This is a large refactor affecting M1, M2, M4, and M5.

### ~~2.5 Outdated Comments in `generator.py`~~ — RESOLVED

- **Location:** `phase_2/engine/generator.py`
- **Resolution:** Removed "(BLOCKED — stubs)" from both the docstring (line 47) and inline comment (line 87).

---

## 3. Additional Stubs Related to Known Items

These are stubs in OTHER modules that are consequences of the 5 intentional stubs above. They don't represent independent gaps — they'll be resolved when the parent stub is resolved.

### 3.1 Censoring Injection (Related to M1-NC-7)

- **Location:** `phase_2/engine/realism.py:59-63`
- **What:** `inject_realism()` raises `NotImplementedError` when `realism_config["censoring"]` is non-None.
- **Parent:** `set_realism(censoring=...)` accepts and stores the parameter (M1-NC-7 decision P2-6), but the engine-side injection logic is deferred.
- **Resolves when:** The spec defines what censoring means concretely (which columns, what mechanism).

### 3.2 Four Pattern Type Injection (Related to M1-NC-6)

- **Location:** `phase_2/engine/patterns.py:61-71`
- **What:** `inject_patterns()` raises `NotImplementedError` for `ranking_reversal`, `dominance_shift`, `convergence`, and `seasonal_anomaly`.
- **Note:** These are **injection** stubs (M2 — how to modify the DataFrame to create the pattern), separate from the **validation** stubs (M5 — how to check if the pattern exists). Ranking reversal validation is now implemented, but ranking reversal injection is still stubbed.
- **Resolves when:** The injection algorithms are defined (how to artificially create each pattern in generated data).

### 3.3 Mixture KS Test (Related to M1-NC-1)

- **Location:** `phase_2/validation/statistical.py:259-264`
- **What:** `check_stochastic_ks()` returns `Check(passed=True)` when `family == "mixture"`.
- **Parent:** Can't validate mixture distribution fit without knowing the component structure.
- **Resolves when:** Mixture distribution sampling (stub 1.1) is implemented.

---

## 4. Test Coverage Gaps

### 4.1 Tests Added (525 → 587, +62 tests)

Three new test files were written after the initial audit:

| File | Tests | What it covers |
|---|---|---|
| `tests/test_module_s2e.py` | 23 | Per-module start-to-end (no internal mocking): M1 SDK lifecycle, M2 engine stages, M4 metadata builder, M5 validator with real checks, cross-module boundary contracts |
| `tests/test_validation_failures.py` | 17 | L1/L3 failure detection on real DataFrames; pattern injection → validation roundtrips; realism → validation roundtrips |
| `tests/test_integration_advanced.py` | 22 | Auto-fix roundtrip with real `build_fn`; agentic path (sandbox, code_validator, error feedback); edge cases (target_rows=1, 20 categories, zero-noise measures); negative cases |

**Key coverage gaps closed:**
- Validator now proven to catch real violations (not just call the right functions)
- Engine now proven to work with manually constructed column dicts (no SDK wrapper)
- Metadata builder now proven to produce all 7 keys with enrichment fields
- `orthogonal_pairs` bug verified fixed via `test_orthogonal_pairs_in_raw_declarations`
- `ParameterOverrides` dict proven to actually change generation behavior

### 4.2 Remaining Coverage Gaps

| Module | File | Status | Notes |
|---|---|---|---|
| Prompt template | `orchestration/prompt.py` | **Not tested** | `render_system_prompt()` has zero test coverage — not called in any test |
| Full orchestrate() loop | `orchestration/retry_loop.py` | **No S2E test** | Existing tests mock the LLM. No test exercises the full loop (mock LLM → real sandbox → real validation) |
| Loop A in pipeline | `pipeline.py` (`_run_loop_a`) | **Not testable without LLM** | Requires a mocked LLM to test without real API calls |

Modules now sufficiently covered (were gaps before):

| Module | File | How covered now |
|---|---|---|
| Skeleton generation | `engine/skeleton.py` | `TestEngineStartToEnd` in `test_module_s2e.py` |
| Pattern injection | `engine/patterns.py` | `test_patterns_applied` in `test_module_s2e.py`; `TestPatternInjectionRoundtrip` in `test_validation_failures.py` |
| Realism injection | `engine/realism.py` | `test_realism_injects_nan` in `test_module_s2e.py`; `TestRealismValidationRoundtrip` in `test_validation_failures.py` |
| Code validator | `orchestration/code_validator.py` | `TestAgenticPath` in `test_integration_advanced.py` (real, not mocked) |
| Sandbox execution | `orchestration/sandbox.py` | `TestAgenticPath` + `TestBoundaryContracts` in `test_integration_advanced.py` and `test_module_s2e.py` |
| Generator orchestrator | `engine/generator.py` | `TestEngineStartToEnd` + `TestAutoFixRoundtrip` (7 real-input tests) |
| Metadata builder | `metadata/builder.py` | `TestMetadataStartToEnd` (2 tests with real SDK registries) |
| Validator orchestrator | `validation/validator.py` | `TestValidationStartToEnd` (5 tests with real checks, no mocking) |

---

## 5. Summary: What Remains

| Category | Count | Effort | Blocks Usage? |
|---|---|---|---|
| Intentional stubs (spec gaps) | 5 | Requires spec input | No — stubs return safe defaults |
| ~~Packaging gaps (quick fixes)~~ | ~~3 (#2.1-2.3)~~ **RESOLVED** | — | — |
| ~~Outdated comments~~ | ~~1 (#2.5)~~ **RESOLVED** | — | — |
| Deferred type migration | 1 (#2.4) | Large refactor | No — dicts work correctly |
| Related downstream stubs | 3 (#3.1-3.3) | Resolved by parent stubs | No |
| Remaining test gaps | 3 modules | Low–Medium | No — functional paths proven by S2E tests |

**Both the Direct SDK path and Agentic path are fully functional.** The remaining items are either blocked on spec input (stubs), packaging polish (quick fixes), or test hardening for the LLM-coupled orchestration path (which requires a mocked LLM to test without real API calls).
