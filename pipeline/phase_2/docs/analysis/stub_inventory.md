# AGPDS Phase 2 — Stub & Gap Inventory

**Date:** 2026-04-06
**Scanned against:** stage3_readiness_audit.md (80 items), stage4_implementation_anatomy.md (file tree), decisions/blocker_resolutions.md

---

## Summary

| Category | Count |
|---|---|
| SPEC_GAP_STUB | 8 |
| DEFERRED_STUB | 5 |
| NO_OP | 1 |
| PARTIAL | 0 |
| TODO_ENHANCEMENT | 4 |
| MISSING (unexpected) | 4 |

**Total intentional stubs/TODOs:** 18
**Total unexpected gaps:** 4

---

## Stub Registry

### SPEC_GAP_STUB: Mixture distribution sampling

- **Location:** engine/measures.py:299
- **Stage3 Item:** M1-NC-1 — `mixture` distribution `param_model` schema
- **Decision:** P1-1 — STUB
- **Current behavior:** `_sample_stochastic()` raises `NotImplementedError` when `family == "mixture"`. Declaration-time `add_measure("x", "mixture", {...})` succeeds because `"mixture"` is in `SUPPORTED_FAMILIES`.
- **Design rationale:** The spec lists `mixture` as a supported family but provides zero examples of the component structure (`param_model` schema). No engineer can implement sampling without knowing whether components are declared as a list with per-component family, weight, and params.
- **Unstub requirements:** Spec author must define the mixture `param_model` schema (e.g., `{"components": [{"family": "gaussian", "weight": 0.6, "params": {...}}, ...]}`). Then implement weighted component dispatch in `_sample_stochastic`.

---

### SPEC_GAP_STUB: Pattern injection — convergence

- **Location:** engine/patterns.py:68
- **Stage3 Item:** M1-NC-6 — Under-specified pattern type param schemas
- **Decision:** P1-2 — No required params (fully unspecified). Injection raises `NotImplementedError`.
- **Current behavior:** `inject_patterns()` raises `NotImplementedError` for `convergence`. Declaration succeeds with any params.
- **Design rationale:** The spec lists convergence as a pattern type but provides no declaration examples, no param schema, no injection algorithm, and no L3 validation logic. The concept itself is undefined.
- **Unstub requirements:** Spec author must define convergence semantics, required params, injection mechanism, and validation criteria.

---

### SPEC_GAP_STUB: Pattern injection — seasonal_anomaly

- **Location:** engine/patterns.py:68
- **Stage3 Item:** M1-NC-6 — Under-specified pattern type param schemas
- **Decision:** P1-2 — No required params (fully unspecified). Injection raises `NotImplementedError`.
- **Current behavior:** Same as convergence — declaration succeeds, generation raises `NotImplementedError`.
- **Design rationale:** Identical to convergence — listed in the pattern type enum but absent from every other spec section.
- **Unstub requirements:** Spec author must define seasonal anomaly semantics, required params, injection mechanism, and validation criteria.

---

### SPEC_GAP_STUB: Censoring injection

- **Location:** engine/realism.py:60
- **Stage3 Item:** M1-NC-7 — `censoring` parameter semantics in `set_realism`
- **Decision:** P2-6 — ALREADY_IMPLEMENTED (the stub behavior). `set_realism` stores config; `realism.py` raises `NotImplementedError` when `censoring is not None`.
- **Current behavior:** `set_realism(censoring={...})` stores the config. At generation time, `apply_realism()` raises `NotImplementedError` if censoring is non-None. `missing_rate` and `dirty_rate` work correctly.
- **Design rationale:** The `censoring` parameter defaults to `None` and is never elaborated in the spec. The mechanism (left/right/interval censoring?), target columns, and parameterization are all undefined.
- **Unstub requirements:** Spec author must define censoring semantics (type, target columns, mechanism, parameterization).

---

### SPEC_GAP_STUB: check_dominance_shift L3 validation

- **Location:** validation/pattern_checks.py:158–182
- **Stage3 Item:** M5-NC-4 — L3 `dominance_shift` validation logic
- **Decision:** P1-3 — STUB. Return `Check(passed=True, detail="not yet implemented")`.
- **Current behavior:** `check_dominance_shift()` always returns `passed=True`. Wired into `SchemaAwareValidator._run_l3()` dispatch.
- **Design rationale:** The spec delegates to an opaque `_verify_dominance_change()` with no implementation. P1-3 suggests "rank change of entity across temporal split" with params `{entity_filter, col, split_point}`, but this is a suggestion, not binding.
- **Unstub requirements:** Spec author must confirm or define the dominance shift validation algorithm and threshold.

---

### SPEC_GAP_STUB: check_convergence L3 validation

- **Location:** validation/pattern_checks.py:185–208
- **Stage3 Item:** M5-NC-5 — Missing validation for `convergence`
- **Decision:** P1-4 — STUB.
- **Current behavior:** Always returns `passed=True`.
- **Design rationale:** Completely absent from §2.9 validation logic. Cannot validate what has no definition.
- **Unstub requirements:** Spec author must define convergence detection criteria.

---

### SPEC_GAP_STUB: check_seasonal_anomaly L3 validation

- **Location:** validation/pattern_checks.py:211–234
- **Stage3 Item:** M5-NC-5 — Missing validation for `seasonal_anomaly`
- **Decision:** P1-4 — STUB.
- **Current behavior:** Always returns `passed=True`.
- **Design rationale:** Same as convergence — completely absent from spec.
- **Unstub requirements:** Spec author must define seasonal anomaly detection criteria.

---

### SPEC_GAP_STUB: Mixture distribution KS test

- **Location:** validation/statistical.py:241–246
- **Stage3 Item:** M5-SR-7 (L2 KS test — mixture case)
- **Decision:** Follows from P1-1. Cannot validate a distribution that cannot be generated.
- **Current behavior:** Returns `Check(passed=True, detail="mixture distribution KS test not yet implemented")`. In practice unreachable — generation raises `NotImplementedError` first.
- **Design rationale:** The KS test requires the expected CDF. For a mixture, this is a weighted sum of component CDFs, but the component structure is undefined (P1-1).
- **Unstub requirements:** Blocked by P1-1 (mixture sampling). Once the `param_model` schema is defined, implement composite CDF from weighted component distributions.

---

### DEFERRED_STUB: Multi-column `on` in group dependency

- **Location:** sdk/relationships.py:127
- **Stage3 Item:** M1-NC-5
- **Decision:** P2-4 — "Restrict to single-column `on` for v1."
- **Current behavior:** `add_group_dependency()` raises `NotImplementedError` if `len(on) != 1`. Single-column form works fully. `on: list[str]` type preserved for forward compat.
- **Design rationale:** Multi-column conditioning requires tuple-key conditional weights and joint-probability skeleton generation. The spec provides no multi-column example. Explicitly restricted to ship v1.
- **Unstub requirements:** Engineering effort: define tuple-key `conditional_weights`, update skeleton builder for joint conditioning, update metadata and validation.

---

### DEFERRED_STUB: orchestrate() structural stub

- **Location:** orchestration/retry_loop.py (entire file)
- **Stage3 Item:** M3-NC-1 through M3-NC-6
- **Decision:** P1-5 — Sandbox semantics ALREADY_IMPLEMENTED in `sandbox.py`.
- **Current behavior:** Always returns `SkipResult`. The actual retry loop logic lives in `sandbox.py:run_retry_loop()`.
- **Design rationale:** `sandbox.py` contains the complete working implementation (thread-based execution, timeout, error feedback, multi-turn accumulation). `retry_loop.py` was created as the target architecture for a clean M3 extraction, but migration hasn't occurred. The `pipeline.py:run_agentic()` path is non-functional via this entry point.
- **Unstub requirements:** Engineering effort: wire `LLMClient` + `render_system_prompt()` + `code_validator` + `sandbox.run_retry_loop()` into `orchestrate()`, or redirect `pipeline.py` to use `sandbox.py` directly.

---

### DEFERRED_STUB: DeclarationStore integration

- **Location:** types.py:382
- **Stage3 Item:** Cross-module contract (freeze-before-generate)
- **Decision:** Not addressed in blocker_resolutions. Deferred to "migration phase."
- **Current behavior:** `DeclarationStore` class exists with `freeze()` lifecycle, but `FactTableSimulator` uses its own `OrderedDict` registries. The freeze contract is NOT enforced at runtime.
- **Design rationale:** FactTableSimulator was implemented first with raw dicts. DeclarationStore was designed as the future typed interface. P3-6's phase flag provides API-level ordering enforcement as a bridge.
- **Unstub requirements:** Engineering effort: refactor FactTableSimulator to use DeclarationStore internally, call freeze() at generate() start.

---

### DEFERRED_STUB: Pipeline orchestrate() unpacking

- **Location:** pipeline.py:93
- **Stage3 Item:** Downstream of M3 stub
- **Decision:** Implicit from orchestrate() being a stub.
- **Current behavior:** Dead code path. Comment says to unpack `(df, metadata, raw_declarations)` from orchestrate(), but orchestrate() always returns SkipResult.
- **Design rationale:** Forward-looking TODO for when the agentic path is wired.
- **Unstub requirements:** Blocked on orchestrate() implementation.

---

### DEFERRED_STUB: check_ranking_reversal L3 validation

- **Location:** validation/pattern_checks.py:237–260
- **Stage3 Item:** M5-SR-12 — SPEC_READY
- **Decision:** Not explicitly addressed (SPEC_READY item).
- **Current behavior:** Always returns `passed=True`. The TODO in code contains the exact formula: `means[m1].rank().corr(means[m2].rank()) < 0`.
- **Design rationale:** The spec provides the validation algorithm, but the corresponding pattern injection is not implemented (patterns.py raises `NotImplementedError` for `ranking_reversal`). Implementing validation without injection would produce a validator with no data to validate.
- **Unstub requirements:** Engineering effort only — implement per §2.9 L3. Practical only after ranking_reversal injection is also implemented.

---

### NO_OP: `scale` parameter on `add_measure`

- **Location:** sdk/columns.py:244
- **Stage3 Item:** M1-NC-2
- **Decision:** P2-5 — "Keep accepting and storing. Add warning when non-None."
- **Current behavior:** Stored in `col_meta["scale"]`, warning logged. No code reads the value.
- **Design rationale:** Present in §2.5 whitelist but never defined. Storing preserves forward compat; warning prevents confusion.
- **Unstub requirements:** Spec author must define scale semantics.

---

### TODO_ENHANCEMENT: Batch error collection

- **Location:** sdk/simulator.py:32
- **Stage3 Item:** M3-NC-3
- **Decision:** P1-5 — "Accept one-at-a-time. Add TODO comment."
- **Current behavior:** Standard one-exception-per-execution Python behavior.
- **Design rationale:** Multi-error collection requires significant M1 refactor for marginal benefit at default retry counts.
- **Unstub requirements:** Optional: implement compound exception collection in M1 validation.

---

### TODO_ENHANCEMENT: Context window exhaustion strategy

- **Location:** orchestration/sandbox.py:629
- **Stage3 Item:** M3-NC-4
- **Decision:** P1-5 — "Accept full history for 3 retries."
- **Current behavior:** Full error feedback history sent on each retry with no truncation. Manageable for 3 retries.
- **Design rationale:** Token budget is only a concern if max_retries is increased significantly beyond 3.
- **Unstub requirements:** Add token counting before each retry; summarize/truncate when budget exceeded.

---

### TODO_ENHANCEMENT: Stale "BLOCKED — stubs" comment

- **Location:** engine/generator.py:47,87
- **Stage3 Item:** M2-NC-1 (P0-2 was implemented)
- **Decision:** P0-2 — IMPLEMENTED. Comment is stale.
- **Current behavior:** Docstring says "Phase β: generate measures (BLOCKED — stubs)" but the code calls `_measures.generate_measures()` which IS fully implemented (stochastic sampling, structural formula evaluation, parameter overrides — all working).
- **Design rationale:** Comment was written before P0-2 implementation and never cleaned up.
- **Unstub requirements:** Update the comment. No functional change.

---

### TODO_ENHANCEMENT: Stale TODO reference in check_group_dependency_transitions

- **Location:** validation/statistical.py:413
- **Stage3 Item:** M5-SR-9
- **Decision:** Not in blocker_resolutions (SPEC_READY item).
- **Current behavior:** The function IS fully implemented (computes conditional distributions, checks deviation < 0.10). The "TODO" in the docstring is a reference marker, not a real to-do.
- **Design rationale:** Reference label left in place during implementation.
- **Unstub requirements:** Convert to reference comment or remove. No functional change.

---

## Unexpected Gaps

### GAP-1: `ColumnDescriptor` dataclass not implemented

- **Expected by:** stage4 types.py — "ColumnDescriptor — Frozen dataclass with fields: name, type, group, parent, family, param_model, formula, effects, noise, derive, values, weights, scale."
- **Actual:** Not present as a class. The implementation uses `OrderedDict[str, dict[str, Any]]` with raw dicts throughout. `types.py` references `ColumnDescriptor` in comments (lines 6, 371) but never defines it.
- **Impact:** Low — the system works with raw dicts. However, this eliminates static type checking on column metadata, making it easier for subtle key-name bugs to slip through.
- **Recommended action:** Low priority. Could be addressed during the DeclarationStore migration (Finding #12).

---

### GAP-2: M3 orchestration has zero dedicated unit tests

- **Expected by:** stage4 implies test coverage for all modules.
- **Actual:** No `test_orchestration_*.py` files exist. The 5 M3 source files (`prompt.py`, `code_validator.py`, `sandbox.py`, `retry_loop.py`, `llm_client.py`) have zero modular unit tests. `sandbox.py` has partial indirect coverage through end-to-end tests.
- **Impact:** Medium — sandbox.py contains critical retry loop logic (700+ lines) with no isolation testing. prompt.py and code_validator.py have clear testable interfaces. llm_client.py is a pre-existing tested component per CLAUDE.md but its tests are not in this test suite.
- **Recommended action:** Add at minimum:
  - `test_orchestration_prompt.py` — verify `render_system_prompt()` output structure
  - `test_orchestration_code_validator.py` — verify `extract_clean_code()` and `validate_generated_code()` with malformed inputs
  - `test_orchestration_sandbox.py` — verify `execute_in_sandbox()` isolation, timeout, namespace, error handling

---

### GAP-3: `tests/demo_end_to_end.py` missing

- **Expected by:** stage4 file tree — "Runnable demo script: direct SDK usage + sandbox execution, prints output for manual inspection."
- **Actual:** File does not exist.
- **Impact:** Low — `test_end_to_end.py` covers the same scenarios as automated tests. The demo was intended as a human-readable walkthrough, not a test suite.
- **Recommended action:** Low priority. Could be created as a runnable example script if needed for onboarding.

---

### GAP-4: `ValidationError` exception type missing

- **Expected by:** stage4 exceptions.py — lists `ValidationError` alongside the other exception types.
- **Actual:** Not defined in `exceptions.py`. The implementation uses `ValidationReport` (a data structure in `types.py`) instead of a `ValidationError` exception. Validation failures are returned as data, not raised.
- **Impact:** None — the design choice to return failures as data is superior to raising exceptions for validation results (which are expected outcomes, not exceptional conditions). The implementation has richer exception types (`PatternInjectionError`, `InvalidParameterError`, etc.) that cover the actual error cases.
- **Recommended action:** None. This is a deliberate and correct design deviation.

---

## Cross-Module Contract Verification

| Contract | Status | Evidence |
|---|---|---|
| DeclarationStore.freeze() enforced before generate() | **NOT ENFORCED** | DeclarationStore exists but FactTableSimulator uses raw OrderedDicts. Phase flag (P3-6) enforces API ordering as a partial substitute. |
| M4 builds from store only (no DataFrame) | **PASS** | `build_schema_metadata()` accepts groups, columns, orthogonal_pairs, etc. No DataFrame parameter. |
| M5 consumes schema_metadata only (no store) | **PASS** | `SchemaAwareValidator.__init__(meta: dict)` — takes only metadata dict. |
| Loop A exceptions raised by M1, caught by M3 | **PASS** | sandbox.py catches all Exception subclasses during execution, relays traceback. |
| Loop B seed offset implemented | **PASS** | `generate_with_validation()` uses `seed = base_seed + attempt`. |
| Single RNG stream through all stages | **PASS** | `generator.py:run_pipeline` creates `rng = np.random.default_rng(seed)` and passes it to skeleton, measures, patterns, and realism. |
| ParameterOverrides consumed by run_pipeline() | **PASS** | `run_pipeline(..., overrides: dict | None = None)` — consumed in `_sample_stochastic` and `generate_measures`. |
| Validation pre-realism, realism post-validation | **PASS** | `generate_with_validation()` calls `build_fn(seed, overrides)` with `realism_config=None`. Realism applied only after validation passes or exhaustion. |

---

## Test Coverage Summary

| Module | Test Files | Test Functions | Coverage Notes |
|---|---|---|---|
| **M1: SDK** | test_sdk_columns.py, test_sdk_dag.py, test_sdk_groups.py, test_sdk_relationships.py, test_sdk_simulator.py, test_sdk_validation.py | 168 | Comprehensive. All declaration-time validation paths covered. |
| **M2: Engine** | test_engine_generator.py, test_engine_measures.py, test_engine_postprocess.py | 26 | Formula evaluator and sampling well-tested. skeleton.py, patterns.py, realism.py have NO dedicated tests (indirect via e2e). |
| **M3: Orchestration** | NONE | **0** | **5 source files with zero unit tests.** Critical gap — sandbox.py has 700+ lines of retry logic untested in isolation. |
| **M4: Metadata** | test_metadata_builder.py | 5 | Adequate for the single-file module. Covers 7-key structure and enrichment. |
| **M5: Validation** | test_validation_autofix.py, test_validation_pattern.py, test_validation_statistical.py, test_validation_structural.py, test_validation_validator.py | 64 | All L1, L2, L3 checks tested. Stubs verified. Auto-fix strategies covered. |
| **Integration** | test_end_to_end.py | 29 | Full-stack coverage: declaration → generation → patterns → realism → validation → Loop B. |
| **TOTAL** | **16 files** | **292** | M3 is the critical gap. M2 engine sub-modules need dedicated tests. |

---

## Structural Deviations from Stage4

These are intentional implementation differences from the stage4 blueprint that are not bugs:

| Stage4 Expectation | Actual Implementation | Assessment |
|---|---|---|
| `ColumnDescriptor` dataclass in types.py | Raw `dict` in `OrderedDict` | Functional but loses type safety. Deferred to migration. |
| `SDKError` base exception class | `SimulatorError` base class | Same concept, better name. |
| `GroupInfo` dataclass in groups.py | `DimensionGroup` in types.py | Same structure, different name and location. |
| `SandboxExecutor` class in sandbox.py | `execute_in_sandbox()` function + `_SandboxThread` class | Function-based API instead of class-based. Equivalent. |
| `SandboxConfig` dataclass | Config params as function arguments | Simpler, equivalent. |
| `PromptTemplate` class + `assemble_prompt()` in prompt.py | `render_system_prompt()` function only | Simpler interface. Template zones are assembled internally. |
| `SUPPORTED_FAMILIES` and `SUPPORTED_PATTERNS` in prompt.py | In sdk/validation.py and sdk/relationships.py respectively | Moved to declaration-time validation (closer to usage). |
| Full retry loop in retry_loop.py | Full retry loop in sandbox.py, structural stub in retry_loop.py | Architectural debt — logic lives in the wrong file per target architecture. |
| `ValidationError` exception | `ValidationReport` data structure | Better design — validation failures are expected results, not exceptions. |

---

## Conclusion

The system is **ready for the direct SDK path** (no LLM). A developer can manually write declarations, call `sim.generate()`, and receive a validated master table with:
- Full skeleton generation (categorical hierarchies, temporal, group dependencies)
- Complete stochastic and structural measure generation (7 of 8 families; mixture is the exception)
- Pattern injection for `outlier_entity` and `trend_break`
- Realism injection (missing_rate, dirty_rate)
- Three-layer validation (L1 structural, L2 statistical, L3 pattern)
- Loop B auto-fix retry with seed offsets and parameter overrides

The system is **NOT ready for the agentic path** (with LLM). The `orchestrate()` entry point in `retry_loop.py` is a structural stub. However, the underlying components exist:
- `sandbox.py` has a working retry loop with timeout, isolation, and error feedback
- `prompt.py` has system prompt rendering
- `code_validator.py` has AST validation
- `llm_client.py` has a multi-provider LLM client

The gap is wiring these together through `orchestrate()` and connecting `pipeline.py:run_agentic()` to the working sandbox path. This is engineering effort, not a spec gap.

**What blocks full completion:**
1. **Spec gaps** (8 items): mixture distribution, censoring, convergence/seasonal_anomaly (injection + validation), dominance_shift validation. These cannot be resolved without spec author input.
2. **Agentic path wiring** (2 items): orchestrate() stub + pipeline unpacking. Engineering effort only.
3. **Test coverage** (1 critical gap): M3 orchestration has zero unit tests.
