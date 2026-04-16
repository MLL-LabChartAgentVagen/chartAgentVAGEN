# AGPDS Phase 2 — Remaining Gaps Reference

**Date:** 2026-04-07
**Status after this session:** ranking_reversal validation implemented, DeclarationStore.freeze() integrated. This document captures everything that remains.
**Updated 2026-04-07:** Structural/packaging gaps resolved.
**Updated 2026-04-15:** Fixed stale line numbers (stubs 1.2–1.4), corrected file reference (stub 1.5b), added uncovered multi-column `on` stub (2.4), renumbered sections, removed residual TODO from statistical.py.

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

- **Location:** `phase_2/validation/pattern_checks.py:189-213`
- **What:** `check_dominance_shift()` returns `Check(passed=True, detail="dominance_shift validation not yet implemented")`.
- **Why stubbed:** The validation logic is opaque in the spec — `self._verify_dominance_change(df, p, meta)` is named but never defined. The params schema (`entity_filter`, `col`, `split_point`) is specified in `PATTERN_REQUIRED_PARAMS` (relationships.py:37), but the actual rank-change-across-temporal-split algorithm is not specified.
- **Current behavior:** Dominance shift patterns can be declared (params validated at declaration time), but validation always passes.
- **To unstub:** Define the algorithm: filter to entity, compute metric rank before/after `split_point`, check that rank changed as declared. Requires spec author input on what "dominance" means quantitatively.
- **Decision ref:** blocker_resolutions.md P1-3

### 1.3 Convergence Validation (P1-4 / M5-NC-5)

- **Location:** `phase_2/validation/pattern_checks.py:216-239`
- **What:** `check_convergence()` returns `Check(passed=True, detail="convergence validation not yet implemented")`.
- **Why stubbed:** Completely absent from the spec's §2.9 validation section. No params schema, no validation logic, no examples. Listed in the pattern type enum but never elaborated.
- **Current behavior:** Convergence patterns can be declared (no required params per `PATTERN_REQUIRED_PARAMS`), but validation always passes.
- **To unstub:** Requires full spec definition: what converges, over what dimension, what threshold constitutes convergence.
- **Decision ref:** blocker_resolutions.md P1-4

### 1.4 Seasonal Anomaly Validation (P1-4 / M5-NC-5)

- **Location:** `phase_2/validation/pattern_checks.py:242-265`
- **What:** `check_seasonal_anomaly()` returns `Check(passed=True, detail="seasonal_anomaly validation not yet implemented")`.
- **Why stubbed:** Same as convergence — completely absent from spec. No params, no validation logic.
- **Current behavior:** Same as convergence — declaration succeeds, validation always passes.
- **To unstub:** Requires full spec definition: what constitutes a seasonal anomaly, which temporal features to check, detection thresholds.
- **Decision ref:** blocker_resolutions.md P1-4

### 1.5 M3 Context Window / Multi-Error (M3-NC-3, M3-NC-4)

- **Location (NC-3):** `phase_2/sdk/simulator.py:32-36` — TODO comment noting one-error-at-a-time limitation.
- **Location (NC-4):** `phase_2/orchestration/sandbox.py:657` — TODO comment noting no token-budget check.
- **What:** (NC-3) The sandbox catches one exception per execution; multiple simultaneous SDK errors are surfaced one per retry. (NC-4) Full error history is sent to the LLM without truncation.
- **Why accepted:** Both are acceptable for the default `max_retries=3`. NC-3 would require M1 to implement multi-error collection. NC-4 would require token counting and history summarization.
- **Current behavior:** Both are functional — they work correctly within the 3-retry budget. They're accepted limitations, not broken functionality.
- **To fix:** NC-3: Collect validation errors into a compound exception in M1. NC-4: Add token counting before each retry; truncate/summarize older failures if budget exceeded.
- **Decision ref:** blocker_resolutions.md P1-5

---



## 2. Additional Stubs Related to Known Items

These are stubs in OTHER modules that are consequences of the 5 intentional stubs above. They don't represent independent gaps — they'll be resolved when the parent stub is resolved.

### 2.1 Censoring Injection (Related to M1-NC-7)

- **Location:** `phase_2/engine/realism.py:59-63`
- **What:** `inject_realism()` raises `NotImplementedError` when `realism_config["censoring"]` is non-None.
- **Parent:** `set_realism(censoring=...)` accepts and stores the parameter (M1-NC-7 decision P2-6), but the engine-side injection logic is deferred.
- **Resolves when:** The spec defines what censoring means concretely (which columns, what mechanism).

### 2.2 Four Pattern Type Injection (Related to M1-NC-6)

- **Location:** `phase_2/engine/patterns.py:61-71`
- **What:** `inject_patterns()` raises `NotImplementedError` for `ranking_reversal`, `dominance_shift`, `convergence`, and `seasonal_anomaly`.
- **Note:** These are **injection** stubs (M2 — how to modify the DataFrame to create the pattern), separate from the **validation** stubs (M5 — how to check if the pattern exists). Ranking reversal validation is now implemented, but ranking reversal injection is still stubbed.
- **Resolves when:** The injection algorithms are defined (how to artificially create each pattern in generated data).

### 2.3 Mixture KS Test (Related to M1-NC-1)

- **Location:** `phase_2/validation/statistical.py:259-264`
- **What:** `check_stochastic_ks()` returns `Check(passed=True)` when `family == "mixture"`.
- **Parent:** Can't validate mixture distribution fit without knowing the component structure.
- **Resolves when:** Mixture distribution sampling (stub 1.1) is implemented.

### 2.4 Multi-Column Group Dependency `on` (P2-4 / M1-NC-5)

- **Location:** `phase_2/sdk/relationships.py:126-130`
- **What:** `add_group_dependency()` raises `NotImplementedError` when `len(on) != 1`.
- **Parent:** Decision P2-4 restricts to single-column `on` for v1 because the nested `conditional_weights` structure for 2+ conditioning columns is not specified.
- **Current behavior:** `add_group_dependency(child_root="x", on=["a", "b"], ...)` raises `NotImplementedError` with a clear message. Single-column `on` works fully.
- **Resolves when:** The spec defines the nested `conditional_weights` structure for multi-column conditioning (e.g., Cartesian product keys vs. hierarchical nesting).
- **Decision ref:** blocker_resolutions.md P2-4

---