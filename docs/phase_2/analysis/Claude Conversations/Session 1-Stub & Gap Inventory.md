# Claude Conversation Log

Session ID: d0028eb1-e67c-492b-844c-f386b3794287
Date: 2026-04-06 19:09:24

---

## 👤 User

inventory

Scan the entire ../phase_2/ codebase for all stubs, TODOs, NotImplementedError,
no-ops, and missing functionality. Cover every file in every module:
- Shared: types.py, exceptions.py, pipeline.py
- M1 sdk/: simulator.py, columns.py, relationships.py, groups.py, dag.py, validation.py
- M2 engine/: generator.py, skeleton.py, measures.py, patterns.py, realism.py, postprocess.py
- M3 orchestration/: prompt.py, code_validator.py, sandbox.py, retry_loop.py, llm_client.py
- M4 metadata/: builder.py
- M5 validation/: validator.py, structural.py, statistical.py, pattern_checks.py, autofix.py

---

## 🤖 Claude

Running Phase A — Automated Scan across the entire `../phase_2/` directory.

---

## 🤖 Claude

Let me also check for `logger.warning` patterns and get a complete file listing to verify all expected files exist.

---

## 🤖 Claude

Now let me read the key stub/warning locations with context to properly classify each finding.

---

## 🤖 Claude

Now let me read the remaining key files with stubs — the validation pattern_checks, statistical stubs, the pipeline TODO, and the columns.py scale warning.

---

## 🤖 Claude

Let me also read the types.py TODO, sandbox.py context marker, and engine pattern/measures warnings for full context.

---

## 🤖 Claude

Now I have all the raw data. Here are the findings grouped by module:

---

## Phase A — Raw Scan Results

### Shared (types.py, exceptions.py, pipeline.py)

| # | File | Line | Type | Code |
|---|---|---|---|---|
| 1 | [types.py:382](../phase_2/types.py#L382) | 382 | TODO | `TODO [Cross-module contract]: Integrate DeclarationStore into FactTableSimulator and call freeze() at the start of generate().` |
| 2 | [pipeline.py:93](../phase_2/pipeline.py#L93) | 93 | TODO | `TODO: When orchestrate() is fully implemented, unpack the triple` — currently unreachable (orchestrate always returns SkipResult) |

### M1: SDK Surface (sdk/)

| # | File | Line | Type | Code |
|---|---|---|---|---|
| 3 | [simulator.py:32](../phase_2/sdk/simulator.py#L32) | 32 | TODO | `TODO [M3-NC-3]: The sandbox currently catches one error at a time.` — batch error collection enhancement |
| 4 | [columns.py:244](../phase_2/sdk/columns.py#L244) | 244 | NO_OP/warning | `scale` parameter stored but `has no effect in the current implementation` |
| 5 | [relationships.py:127](../phase_2/sdk/relationships.py#L127) | 127 | NotImplementedError | `Multi-column 'on' is not supported in v1.` [P2-4] |

### M2: Generation Engine (engine/)

| # | File | Line | Type | Code |
|---|---|---|---|---|
| 6 | [generator.py:47,87](../phase_2/engine/generator.py#L47) | 47,87 | STUB comment | Phase β: Measure generation marked `BLOCKED — stubs` in docstring (but code does call `generate_measures`) |
| 7 | [measures.py:299](../phase_2/engine/measures.py#L299) | 299 | NotImplementedError | `mixture distribution sampling not yet implemented` [M1-NC-1 / P1-1] |
| 8 | [measures.py:397](../phase_2/engine/measures.py#L397) | 397 | warning | `Clamped %s.%s: %d values clamped to 1e-6` — operational, not a stub |
| 9 | [patterns.py:68](../phase_2/engine/patterns.py#L68) | 68 | NotImplementedError | Pattern types `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly` injection not implemented [M1-NC-6] |
| 10 | [patterns.py:127](../phase_2/engine/patterns.py#L127) | 127 | warning | `inject_outlier_entity: column not in DataFrame` — operational skip |
| 11 | [patterns.py:219](../phase_2/engine/patterns.py#L219) | 219 | warning | `inject_trend_break: column not in DataFrame` — operational skip |
| 12 | [realism.py:60](../phase_2/engine/realism.py#L60) | 60 | NotImplementedError | `Censoring injection not yet implemented` [M1-NC-7] |
| 13 | [skeleton.py:95](../phase_2/engine/skeleton.py#L95) | 95 | warning | `unknown column type` — defensive fallback, not a stub |

### M3: LLM Orchestration (orchestration/)

| # | File | Line | Type | Code |
|---|---|---|---|---|
| 14 | [retry_loop.py](../phase_2/orchestration/retry_loop.py) | entire file | STUB | `orchestrate()` is a structural stub — always returns `SkipResult`. Full Loop A logic not wired. |
| 15 | [sandbox.py:629](../phase_2/orchestration/sandbox.py#L629) | 629 | TODO | `TODO [M3-NC-4]: Context window exhaustion` — no truncation of error feedback history for high retry counts |
| 16 | [sandbox.py:545](../phase_2/orchestration/sandbox.py#L545) | 545 | comment | `phase_2.simulator not yet existing` — namespace factory depends on simulator import |

### M4: Schema Metadata (metadata/)

| # | File | Line | Type | Code |
|---|---|---|---|---|
| 17 | [builder.py:218,227,238,248](../phase_2/metadata/builder.py#L218) | 218–248 | warning | 4 consistency warnings for missing columns/measures/patterns/groups — operational logging, not stubs |

### M5: Validation Engine (validation/)

| # | File | Line | Type | Code |
|---|---|---|---|---|
| 18 | [pattern_checks.py:158](../phase_2/validation/pattern_checks.py#L158) | 158–182 | STUB | `check_dominance_shift()` always returns `passed=True` [M5-NC-4 / P1-3] |
| 19 | [pattern_checks.py:185](../phase_2/validation/pattern_checks.py#L185) | 185–208 | STUB | `check_convergence()` always returns `passed=True` [M5-NC-5 / P1-4] |
| 20 | [pattern_checks.py:211](../phase_2/validation/pattern_checks.py#L211) | 211–234 | STUB | `check_seasonal_anomaly()` always returns `passed=True` [M5-NC-5 / P1-4] |
| 21 | [pattern_checks.py:237](../phase_2/validation/pattern_checks.py#L237) | 237–260 | STUB | `check_ranking_reversal()` always returns `passed=True` [M5 SPEC_READY #12] |
| 22 | [statistical.py:241](../phase_2/validation/statistical.py#L241) | 241–246 | STUB | Mixture distribution KS test — returns `passed=True`, `not yet implemented` |
| 23 | [statistical.py:413](../phase_2/validation/statistical.py#L413) | 413 | TODO | `TODO [M5 SPEC_READY #9]: L2 group dependency conditional transition check` — function body exists but TODO comment remains |

---

## Summary by Type

| Type | Count |
|---|---|
| **NotImplementedError** (raises on hit) | 4 — relationships multi-col `on`, mixture sampling, pattern injection (4 types), censoring |
| **Structural stub** (returns default) | 1 — `orchestrate()` in retry_loop.py |
| **Validation stubs** (always passed=True) | 5 — dominance_shift, convergence, seasonal_anomaly, ranking_reversal, mixture KS |
| **NO_OP parameter** | 1 — `scale` in columns.py |
| **TODO comments** | 8 — DeclarationStore integration, pipeline unpack, batch errors, context window, pattern_checks (4), statistical |
| **Operational warnings** (not stubs) | 7 — clamping, missing columns, metadata consistency, unknown column type |

---

Raw scan complete. Found **19 stubs/TODOs** across **12 files** (plus 7 operational warnings that are normal defensive logging, not gaps). Send 'Phase B' to classify and explain each, or ask about specific findings.

---

## 👤 User

Phase B

---

## 🤖 Claude

Reading the reference documents to trace each finding to its source decision.

---

## 🤖 Claude

Now I have the full reference documents. Let me classify each finding from Phase A.

---

## Phase B — Classification and Design Rationale

### SPEC_GAP_STUB — Cannot unstub without spec author input (8)

---

**1. Mixture distribution sampling**
- **Location:** [measures.py:299](../phase_2/engine/measures.py#L299)
- **Stage3 Item:** M1-NC-1 — `mixture` distribution `param_model` schema
- **Decision:** P1-1 — STUB. Raise `NotImplementedError` at generation time.
- **Current behavior:** `add_measure(name, "mixture", {...})` succeeds at declaration time (family is in `SUPPORTED_FAMILIES`). Calling `generate()` raises `NotImplementedError` with a hint about expected schema.
- **Design rationale:** The spec lists `mixture` as a supported family but provides zero examples of its parameter structure (component distributions, mixing weights, per-component params). No engineer can implement sampling without knowing the schema.
- **Unstub requirements:** Spec author must define the `param_model` schema for mixture (e.g., `{"components": [{"family": "gaussian", "weight": 0.6, "params": {...}}, ...]}`). Then implement multi-component weighted sampling in `_sample_stochastic`.

---

**2. Censoring injection**
- **Location:** [realism.py:60](../phase_2/engine/realism.py#L60)
- **Stage3 Item:** M1-NC-7 — `censoring` parameter semantics in `set_realism`
- **Decision:** P2-6 — ALREADY_IMPLEMENTED (storage). Raises `NotImplementedError` when `censoring is not None`.
- **Current behavior:** `set_realism(censoring={...})` stores the dict. At generation time in `apply_realism`, if censoring is non-None, raises `NotImplementedError`.
- **Design rationale:** Censoring defaults to `None` and is never elaborated in the spec. The parameter type, allowed values, and what "censoring" means concretely are all undefined. `missing_rate` and `dirty_rate` are implemented.
- **Unstub requirements:** Spec author must define censoring semantics (e.g., right-censoring with threshold? Interval censoring? Which columns?).

---

**3. Convergence pattern injection**
- **Location:** [patterns.py:68](../phase_2/engine/patterns.py#L68)
- **Stage3 Item:** M1-NC-6 — Under-specified pattern type param schemas
- **Decision:** P1-2 — No required params defined for convergence (fully unspecified).
- **Current behavior:** `inject_pattern("convergence", ...)` succeeds at declaration time (any params accepted). At generation time, raises `NotImplementedError`.
- **Design rationale:** The spec lists convergence as a pattern type but provides no declaration examples, no param schema, and no §2.9 L3 validation logic. Completely absent from spec beyond the enum entry.
- **Unstub requirements:** Spec author must define what convergence means (metric, time horizon, threshold?), its required params, injection algorithm, and validation criteria.

---

**4. Seasonal anomaly pattern injection**
- **Location:** [patterns.py:68](../phase_2/engine/patterns.py#L68)
- **Stage3 Item:** M1-NC-6 — Under-specified pattern type param schemas
- **Decision:** P1-2 — No required params defined for seasonal_anomaly (fully unspecified).
- **Current behavior:** Same as convergence — declaration succeeds, generation raises `NotImplementedError`.
- **Design rationale:** Identical to convergence — listed in enum, zero specification beyond that.
- **Unstub requirements:** Spec author must define seasonal anomaly semantics, required params, injection algorithm, and validation criteria.

---

**5. Dominance shift validation**
- **Location:** [pattern_checks.py:158](../phase_2/validation/pattern_checks.py#L158)
- **Stage3 Item:** M5-NC-4 — L3 `dominance_shift` validation logic
- **Decision:** P1-3 — STUB. Return `Check(passed=True, detail="not yet implemented")`.
- **Current behavior:** Always returns `passed=True`. The check name `dominance_{col}` is correctly formatted but performs no actual validation.
- **Design rationale:** §2.9 delegates to an opaque `_verify_dominance_change(df, p, meta)` with no implementation shown. P1-2 defined required params (`entity_filter`, `col`, `split_point`) but the validation algorithm itself is not specified.
- **Unstub requirements:** Spec author must define the validation algorithm (e.g., rank change of entity across temporal split, threshold for "significant" shift). Engineering effort to implement once defined.

---

**6. Convergence validation**
- **Location:** [pattern_checks.py:185](../phase_2/validation/pattern_checks.py#L185)
- **Stage3 Item:** M5-NC-5 — Missing validation for `convergence` and `seasonal_anomaly`
- **Decision:** P1-4 — STUB. Return `Check(passed=True)`.
- **Current behavior:** Always returns `passed=True` with "not yet implemented" detail.
- **Design rationale:** Completely absent from §2.9 validation logic. Cannot validate what has no definition.
- **Unstub requirements:** Spec author must define convergence validation criteria. Blocked by the injection stub (finding #3) — no injected data to validate.

---

**7. Seasonal anomaly validation**
- **Location:** [pattern_checks.py:211](../phase_2/validation/pattern_checks.py#L211)
- **Stage3 Item:** M5-NC-5
- **Decision:** P1-4 — STUB.
- **Current behavior:** Same as convergence — always `passed=True`.
- **Design rationale:** Same as convergence — completely absent from spec.
- **Unstub requirements:** Spec author must define seasonal anomaly validation. Blocked by injection stub (finding #4).

---

**8. Mixture distribution KS test**
- **Location:** [statistical.py:241](../phase_2/validation/statistical.py#L241)
- **Stage3 Item:** M5-SR-7 (mixture-specific case of L2 KS test)
- **Decision:** Derived from P1-1 — if generation is stubbed, validation must also be stubbed.
- **Current behavior:** When `family == "mixture"`, returns `Check(passed=True, detail="mixture distribution KS test not yet implemented")`.
- **Design rationale:** Cannot compute expected CDF for a mixture without knowing the component structure. Depends entirely on P1-1 being resolved first.
- **Unstub requirements:** Blocked by P1-1 (mixture generation). Once the param_model schema is defined, implement composite CDF from weighted component CDFs and run standard KS test.

---

### DEFERRED_STUB — Could be implemented with engineering effort (5)

---

**9. Multi-column `on` in group dependency**
- **Location:** [relationships.py:127](../phase_2/sdk/relationships.py#L127)
- **Stage3 Item:** M1-NC-5 — Multi-column `on` in `add_group_dependency`
- **Decision:** P2-4 — Restrict to single-column `on` for v1. Raise `NotImplementedError` for `len(on) != 1`.
- **Current behavior:** `add_group_dependency(child, on=["a", "b"], ...)` raises `NotImplementedError`. Single-column form works fully. Parameter type remains `list[str]` for forward compatibility.
- **Design rationale:** Multi-column `on` requires tuple keys for `conditional_weights` and joint conditioning in generation. The spec never shows the multi-column dict structure. Explicitly restricted to v1 to ship the single-column case.
- **Unstub requirements:** Engineering effort — define tuple key structure `{("Mild", "East"): {...}}`, update skeleton generation for joint conditioning, update validation for multi-column conditional weight checks.

---

**10. `orchestrate()` structural stub**
- **Location:** [retry_loop.py](../phase_2/orchestration/retry_loop.py) (entire file)
- **Stage3 Item:** M3-NC-1 through M3-NC-6 (Sandbox semantics)
- **Decision:** P1-5 — M3-NC-1,2,5,6 are ALREADY_IMPLEMENTED in `sandbox.py`. The `orchestrate()` wrapper is a structural stub pending LLM client integration.
- **Current behavior:** Always returns `SkipResult(scenario_id, error_log=["orchestrate() not yet implemented"])`. The actual retry loop logic is fully implemented in `sandbox.py:exec_with_retries()`.
- **Design rationale:** The full Loop A exists in sandbox.py (thread-based execution, timeout, namespace isolation, error feedback). retry_loop.py was designed as the higher-level abstraction that wires LLM prompting → sandbox execution → validation. Without an LLM client wired in, there's no prompt-response cycle to orchestrate.
- **Unstub requirements:** Wire `LLMClient.generate_code()` into orchestrate(). Connect `prompt.py:assemble_prompt()` for system/user message construction. Route sandbox execution through `sandbox.py:exec_with_retries()`. Implement error feedback formatting. The pipeline.py TODO (finding #16) resolves automatically when this is done.

---

**11. Ranking reversal pattern injection**
- **Location:** [patterns.py:68](../phase_2/engine/patterns.py#L68)
- **Stage3 Item:** M1-NC-6 (subset)
- **Decision:** P1-2 — Required params defined: `frozenset({"metrics", "entity_col"})`. Injection raises `NotImplementedError`.
- **Current behavior:** Declaration succeeds with required param validation. Generation raises `NotImplementedError`.
- **Design rationale:** Unlike convergence/seasonal_anomaly, the spec provides the validation algorithm (§2.9 L3: negative rank correlation). P1-2 defined required params. The injection algorithm (how to make two metrics have reversed rankings for an entity) is inferrable but was not prioritized.
- **Unstub requirements:** Engineering effort — implement injection that re-orders entity metric values to produce negative rank correlation. Moderate complexity.

---

**12. Dominance shift pattern injection**
- **Location:** [patterns.py:68](../phase_2/engine/patterns.py#L68)
- **Stage3 Item:** M1-NC-6 (subset)
- **Decision:** P1-2 — Required params defined: `frozenset({"entity_filter", "col", "split_point"})`. Injection raises `NotImplementedError`.
- **Current behavior:** Same as ranking_reversal — declaration with param validation succeeds, generation raises `NotImplementedError`.
- **Design rationale:** Required params are defined. The injection algorithm (shift an entity's rank across a temporal split) is partially inferrable from the validation side, but the validation itself is also stubbed (finding #5). Both sides need work.
- **Unstub requirements:** Engineering effort — implement injection that modifies entity values to produce a rank change across the split_point. Somewhat coupled to finding #5 (validation stub).

---

**13. DeclarationStore integration**
- **Location:** [types.py:382](../phase_2/types.py#L382)
- **Stage3 Item:** Cross-module contract (related to M1-NC-11)
- **Decision:** Not directly addressed — `DeclarationStore` class exists with `freeze()` semantics, but integration with `FactTableSimulator` was explicitly deferred to "the migration phase."
- **Current behavior:** `DeclarationStore` is defined with accumulating→frozen lifecycle. `FactTableSimulator` uses its own `OrderedDict` registries directly. The freeze-before-generate contract is NOT enforced at runtime.
- **Design rationale:** The phase flag (P3-6) provides Step1/Step2 ordering enforcement at the API level. `DeclarationStore` is a deeper refactor toward typed column descriptors. It was deemed lower priority than shipping the functional pipeline.
- **Unstub requirements:** Engineering effort — wire `DeclarationStore` into `FactTableSimulator.__init__()`, delegate all add_* methods to the store, call `freeze()` at the start of `generate()`. Medium refactor.

---

### NO_OP — Parameter accepted but intentionally unused (1)

---

**14. `scale` parameter on `add_measure`**
- **Location:** [columns.py:244](../phase_2/sdk/columns.py#L244)
- **Stage3 Item:** M1-NC-2 — `scale` parameter
- **Decision:** P2-5 — Keep accepting and storing. Log warning when non-None.
- **Current behavior:** `add_measure(name, family, pm, scale=2.0)` succeeds. `col_meta["scale"]` stores `2.0`. A warning is logged: "has no effect in the current implementation."
- **Design rationale:** The `scale` parameter appears in §2.5's SDK whitelist but is never defined, used in the one-shot example, or referenced elsewhere. Accepting it preserves API compatibility for LLM-generated scripts that might include it; the warning alerts human users.
- **Unstub requirements:** Spec author must clarify what `scale` does. Possible interpretations: post-sampling multiplier? Variance scaling? Once defined, apply in `_sample_stochastic` after sampling.

---

### PARTIAL — Implemented with known limitations (1)

---

**15. Ranking reversal validation**
- **Location:** [pattern_checks.py:237](../phase_2/validation/pattern_checks.py#L237)
- **Stage3 Item:** M5-SR-12 — L3 ranking reversal validation (SPEC_READY)
- **Decision:** No specific entry — the spec provides the algorithm: `means[m1].rank().corr(means[m2].rank()) < 0`.
- **Current behavior:** Always returns `Check(passed=True, detail="ranking_reversal validation not yet implemented")`. The TODO in code references the exact algorithm

---

## 🤖 Claude

Let me check whether the group dependency transitions and ranking reversal functions are actually implemented.

---

## 🤖 Claude

Now I have both reference documents. Let me classify each finding.

---

## Phase B — Classification and Design Rationale

### SPEC_GAP_STUB — Cannot unstub without spec author input (8 items)

---

**1. Mixture distribution sampling**
- **Location:** [measures.py:299](../phase_2/engine/measures.py#L299)
- **Stage3 Item:** M1-NC-1 — `mixture` distribution `param_model` schema
- **Decision:** P1-1 — STUB. Accept `family="mixture"` at declaration time. Raise `NotImplementedError` at generation time.
- **Current behavior:** `_sample_stochastic()` raises `NotImplementedError` when `family == "mixture"`. Declaration succeeds because `"mixture"` is in `SUPPORTED_FAMILIES`.
- **Design rationale:** The spec lists `mixture` as a supported family but provides zero examples of how component distributions, mixing weights, and per-component parameters are structured in `param_model`. No engineer can implement sampling without knowing the schema.
- **Unstub requirements:** Spec author must define `param_model` for mixture (e.g., `{"components": [{"family": "gaussian", "weight": 0.6, "params": {...}}, ...]}`). Then implement sampling as weighted component dispatch.

---

**2. Censoring injection**
- **Location:** [realism.py:60](../phase_2/engine/realism.py#L60)
- **Stage3 Item:** M1-NC-7 — `censoring` parameter semantics in `set_realism`
- **Decision:** P2-6 — ALREADY_IMPLEMENTED (the stub behavior). `set_realism` stores `censoring`; `realism.py` raises `NotImplementedError` when `censoring is not None`.
- **Current behavior:** If user passes `censoring={...}` to `set_realism`, the config is stored. At generation time, `apply_realism()` raises `NotImplementedError`.
- **Design rationale:** The `censoring` parameter defaults to `None` and is never elaborated anywhere in the spec. The mechanism (truncation? right-censoring? interval censoring?) and which columns it applies to are undefined.
- **Unstub requirements:** Spec author must define censoring mechanism, target columns, and parameterization.

---

**3. Convergence pattern injection**
- **Location:** [patterns.py:68](../phase_2/engine/patterns.py#L68)
- **Stage3 Item:** M1-NC-6 — Pattern parameter schemas for under-specified types
- **Decision:** P1-2 — No required params defined for `convergence` (fully unspecified).
- **Current behavior:** `inject_patterns()` raises `NotImplementedError` for `convergence` type.
- **Design rationale:** Convergence has no declaration examples, no param schema, and no L3 validation logic in the spec. The concept (metrics converging toward a common value over time?) is not even informally described.
- **Unstub requirements:** Spec author must define convergence semantics, required params, injection mechanism, and validation criteria.

---

**4. Seasonal anomaly pattern injection**
- **Location:** [patterns.py:68](../phase_2/engine/patterns.py#L68)
- **Stage3 Item:** M1-NC-6 — Pattern parameter schemas for under-specified types
- **Decision:** P1-2 — No required params defined for `seasonal_anomaly` (fully unspecified).
- **Current behavior:** `inject_patterns()` raises `NotImplementedError` for `seasonal_anomaly` type.
- **Design rationale:** Same as convergence — no examples, no params, no validation logic. The concept (unusual spikes during specific seasonal periods?) is undefined.
- **Unstub requirements:** Spec author must define seasonal anomaly semantics, required params, injection mechanism, and validation criteria.

---

**5. Dominance shift L3 validation**
- **Location:** [pattern_checks.py:158–182](../phase_2/validation/pattern_checks.py#L158)
- **Stage3 Item:** M5-NC-4 — `dominance_shift` validation logic
- **Decision:** P1-3 — STUB. Return `Check(passed=True, detail="not yet implemented")`.
- **Current behavior:** `check_dominance_shift()` always returns `passed=True`. No actual validation is performed.
- **Design rationale:** The spec delegates to `_verify_dominance_change()` which is opaque — no implementation shown. P1-3 suggests defining it as "rank change of entity across temporal split" with params `{entity_filter, col, split_point}`, but this is a suggestion, not a binding spec definition.
- **Unstub requirements:** Spec author must confirm the suggested definition (rank change across temporal split) or provide an alternative. Then implement rank computation and threshold check.

---

**6. Convergence L3 validation**
- **Location:** [pattern_checks.py:185–208](../phase_2/validation/pattern_checks.py#L185)
- **Stage3 Item:** M5-NC-5 — Missing validation for `convergence`
- **Decision:** P1-4 — STUB. Return `Check(passed=True)`.
- **Current behavior:** `check_convergence()` always returns `passed=True`.
- **Design rationale:** Completely absent from §2.9 validation logic. Cannot implement what isn't defined.
- **Unstub requirements:** Spec author must define convergence detection criteria (metric similarity over time? variance reduction? target threshold?).

---

**7. Seasonal anomaly L3 validation**
- **Location:** [pattern_checks.py:211–234](../phase_2/validation/pattern_checks.py#L211)
- **Stage3 Item:** M5-NC-5 — Missing validation for `seasonal_anomaly`
- **Decision:** P1-4 — STUB. Return `Check(passed=True)`.
- **Current behavior:** `check_seasonal_anomaly()` always returns `passed=True`.
- **Design rationale:** Same as convergence — completely absent from §2.9.
- **Unstub requirements:** Spec author must define seasonal anomaly detection criteria.

---

**8. Mixture distribution KS test**
- **Location:** [statistical.py:241–246](../phase_2/validation/statistical.py#L241)
- **Stage3 Item:** M5-SR-7 (L2 KS test — SPEC_READY for non-mixture families)
- **Decision:** Follows from P1-1. Can't test distribution fit when sampling is stubbed.
- **Current behavior:** Returns `Check(passed=True, detail="mixture distribution KS test not yet implemented")`.
- **Design rationale:** The KS test requires knowing the expected CDF. For a mixture distribution, the CDF is a weighted sum of component CDFs. Since the mixture `param_model` schema is undefined (P1-1), the expected CDF cannot be constructed.
- **Unstub requirements:** Depends on P1-1 (mixture schema). Once sampling is implemented, implement KS test using composite CDF from weighted component distributions.

---

### DEFERRED_STUB — Implementable with engineering effort alone (7 items)

---

**9. Multi-column `on` in group dependency**
- **Location:** [relationships.py:127](../phase_2/sdk/relationships.py#L127)
- **Stage3 Item:** M1-NC-5
- **Decision:** P2-4 — "Restrict to single-column `on` for v1." Keep `on: list[str]` type for forward compat.
- **Current behavior:** `add_group_dependency()` raises `NotImplementedError` if `len(on) != 1`.
- **Design rationale:** Multi-column conditioning (e.g., `on=["severity", "region"]`) requires tuple-key conditional weights and Cartesian product skeleton generation. The spec shows no multi-column example, so the v1 restriction avoids under-specified behavior while preserving the API shape.
- **Unstub requirements:** Engineering effort: implement tuple-key `conditional_weights` (e.g., `{("Mild", "East"): {...}}`), update skeleton builder to handle joint conditioning. No spec clarification needed — the P2-4 decision already suggests the approach.

---

**10. `orchestrate()` structural stub (Loop A)**
- **Location:** [retry_loop.py](../phase_2/orchestration/retry_loop.py) (entire file)
- **Stage3 Item:** M3-NC-1 through M3-NC-6
- **Decision:** P1-5 — The full retry logic already exists in `sandbox.py`. `retry_loop.py` is the target architecture location.
- **Current behavior:** `orchestrate()` logs a warning and returns `SkipResult` immediately. No LLM call, no sandbox execution, no retries.
- **Design rationale:** `sandbox.py` contains the complete retry loop (`run_with_retries`) with isolation, timeout, error feedback, and multi-turn conversation accumulation. `retry_loop.py` is the future clean extraction point. The stub exists so `pipeline.py` can import from the target module path.
- **Unstub requirements:** Wire together: LLM client (`llm_client.py`), prompt assembly (`prompt.py`), code validation (`code_validator.py`), and sandbox execution (`sandbox.py`). Migrate logic from `sandbox.py:run_with_retries` into `orchestrate()`.

---

**11. Pipeline orchestrate() unpacking**
- **Location:** [pipeline.py:93](../phase_2/pipeline.py#L93)
- **Stage3 Item:** Downstream of M3-NC-6 (Loop A terminal failure)
- **Decision:** Follows from orchestrate() being a stub — this code path is unreachable.
- **Current behavior:** Comment says to unpack `(df, metadata, raw_declarations)` when orchestrate is implemented. Currently unreachable because orchestrate always returns `SkipResult`.
- **Design rationale:** The pipeline's agentic path (`run_agentic`) calls orchestrate() and checks for SkipResult. Until orchestrate is real, the success path is dead code.
- **Unstub requirements:** Blocked by item #10. Once orchestrate() returns actual results, unpack the triple and return it.

---

**12. DeclarationStore freeze-before-generate contract**
- **Location:** [types.py:382](../phase_2/types.py#L382)
- **Stage3 Item:** Cross-module contract (not a specific stage3 item)
- **Decision:** Not directly addressed in `blocker_resolutions.md`. Types.py NOTE says "deferred to the migration phase."
- **Current behavior:** `DeclarationStore` class exists with `freeze()` method and lifecycle enforcement. But `FactTableSimulator` uses its own `OrderedDict` registries directly, not `DeclarationStore`. The freeze contract is not enforced at runtime.
- **Design rationale:** DeclarationStore was designed as the future single source of truth. The current implementation uses parallel OrderedDict registries for pragmatic reasons — migrating would be a cross-cutting refactor touching every SDK method.
- **Unstub requirements:** Engineering effort: refactor `FactTableSimulator` to use `DeclarationStore` internally, call `freeze()` at the start of `generate()`, remove duplicate OrderedDict registries.

---

**13. Ranking reversal pattern injection**
- **Location:** [patterns.py:68](../phase_2/engine/patterns.py#L68)
- **Stage3 Item:** M1-NC-6 — Pattern parameter schemas
- **Decision:** P1-2 — Required params defined: `frozenset({"metrics", "entity_col"})`. But injection logic not implemented.
- **Current behavior:** `inject_patterns()` raises `NotImplementedError` for `ranking_reversal`.
- **Design rationale:** The param schema is defined (P1-2) and the validation logic is specified (M5-SR-12: negative rank correlation). However, the injection mechanism (how to manipulate values so that entity rankings reverse) was not prioritized for v1.
- **Unstub requirements:** Engineering effort: implement injection that ensures `means[m1].rank().corr(means[m2].rank()) < 0` for the target subset. The validation spec (§2.9 L3) constrains the expected outcome.

---

**14. Dominance shift pattern injection**
- **Location:** [patterns.py:68](../phase_2/engine/patterns.py#L68)
- **Stage3 Item:** M1-NC-6 — Pattern parameter schemas
- **Decision:** P1-2 — Required params defined: `frozenset({"entity_filter", "col", "split_point"})`. Injection logic not implemented.
- **Current behavior:** `inject_patterns()` raises `NotImplementedError` for `dominance_shift`.
- **Design rationale:** Params are defined but the injection mechanism (how to make an entity's rank change across a temporal split) requires both the generation logic and a clear definition of "dominance" — which P1-3 suggests as rank change but doesn't confirm.
- **Unstub requirements:** Engineering effort: implement rank manipulation across temporal split. Partially depends on spec confirmation of dominance definition (borderline SPEC_GAP).

---

**15. Ranking reversal L3 validation**
- **Location:** [pattern_checks.py:237–260](../phase_2/validation/pattern_checks.py#L237)
- **Stage3 Item:** M5-SR-12 — SPEC_READY. `means[m1].rank().corr(means[m2].rank()) < 0`.
- **Decision:** Not directly addressed in blocker_resolutions (it's SPEC_READY).
- **Current behavior:** `check_ranking_reversal()` always returns `passed=True`. The validation logic is not implemented despite being SPEC_READY.
- **Design rationale:** Since ranking_reversal *injection* is not implemented (item #13), there is no data to validate against. The stub avoids false failures when injection is deferred. However, the spec provides the exact formula for the check.
- **Unstub requirements:** Engineering effort only — implement `means[m1].rank().corr(means[m2].rank()) < 0` per §2.9 L3. Sensible to implement alongside the injection side (item #13).

---

### NO_OP — Parameter accepted but intentionally unused (1 item)

---

**16. `scale` parameter on `add_measure`**
- **Location:** [columns.py:244](../phase_2/sdk/columns.py#L244)
- **Stage3 Item:** M1-NC-2
- **Decision:** P2-5 — "Keep accepting and storing. Add a warning when non-None."
- **Current behavior:** `add_measure()` accepts `scale`, stores it in `col_meta["scale"]`, logs a warning. No code path reads or uses the stored value.
- **Design rationale:** `scale` appears in the §2.5 whitelist method signature but is never defined, never used in the one-shot example, and never referenced in any formula or validation logic. Storing it preserves forward compatibility; the warning prevents user confusion.
- **Unstub requirements:** Spec author must define scale semantics (post-sampling multiplier? unit conversion? variance scaling?). Then wire into `_sample_stochastic` or `_eval_structural`.

---

### TODO_ENHANCEMENT — Future improvements, not missing requirements (3 items)

---

**17. Batch error collection**
- **Location:** [simulator.py:32](../phase_2/sdk/simulator.py#L32)
- **Stage3 Item:** M3-NC-3 — Multiple simultaneous SDK errors
- **Decision:** P1-5 — "Accept one-at-a-time. Add TODO comment in `sdk/simulator.py`."
- **Current behavior:** Standard Python exception propagation surfaces one error per sandbox execution. With 3 retries and potentially 4+ independent errors, the retry budget may be systematically insufficient for complex scripts.
- **Design rationale:** The one-at-a-time limitation is inherent to Python's exception model. Collecting multiple validation errors into a compound exception would require M1 to run all validators in a try/catch-continue pattern — a significant API change for marginal benefit at default retry counts.
- **Unstub requirements:** Optional enhancement: implement multi-error collection in M1 validation (catch-continue pattern), aggregate into a compound exception, relay as batch feedback to the LLM.

---

**18. Context window exhaustion strategy**
- **Location:** [sandbox.py:629](../phase_2/orchestration/sandbox.py#L629)
- **Stage3 Item:** M3-NC-4
- **Decision:** P1-5 — "Accept full history for 3 retries. Add TODO comment for token-budget check."
- **Current behavior:** Full error feedback history is sent on each retry with no truncation. At `max_retries=3`, this accumulates up to ~4 scripts + 3 tracebacks on top of the system prompt.
- **Design rationale:** For the default `max_retries=3`, context exhaustion is unlikely with modern LLM context windows (128K+). The TODO is a safety net for users who increase `max_retries` significantly.
- **Unstub requirements:** Add token-count estimation before each retry. If budget exceeded, summarize earlier feedback payloads. Requires a tokenizer or heuristic word-count proxy.

---

**19. Stale "BLOCKED — stubs" comment in generator.py**
- **Location:** [generator.py

---

## 🤖 Claude

Now I have everything needed. Classifying each finding with its trace to the source decision.

---

## Phase B — Classification and Design Rationale

### SPEC_GAP_STUB (7) — Cannot unstub without spec author input

---

**1. Mixture distribution sampling**
- **Location:** [measures.py:299](../phase_2/engine/measures.py#L299)
- **Stage3 Item:** M1-NC-1 — `mixture` distribution `param_model` schema
- **Decision:** P1-1 — "STUB. Raise `NotImplementedError`."
- **Current behavior:** `_sample_stochastic()` raises `NotImplementedError` when `family == "mixture"`. Declaration-time `add_measure("x", "mixture", {...})` succeeds (family is in `SUPPORTED_FAMILIES`), but generation fails.
- **Design rationale:** The spec lists `mixture` as a supported family but provides zero examples of its component structure. The expected schema `{"components": [{"family": str, "weight": float, "params": {...}}, ...]}` is suggested but unconfirmed. Without a canonical param_model, there's no way to implement sampling or validation.
- **Unstub requirements:** Spec author must define the mixture param_model schema (component structure, mixing weight normalization, per-component parameter resolution with effects).

---

**2. Pattern injection — 4 deferred types**
- **Location:** [patterns.py:68](../phase_2/engine/patterns.py#L68)
- **Stage3 Item:** M1-NC-6 — Under-specified pattern type param schemas
- **Decision:** P1-2 — "Add required params for `ranking_reversal` and `dominance_shift`. Stub all four in engine."
- **Current behavior:** Raises `NotImplementedError` for `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`. The two types `outlier_entity` and `trend_break` are fully implemented.
- **Design rationale:** `ranking_reversal` and `dominance_shift` have required params defined at declaration time (P1-2), but the spec provides no injection algorithm — what does it mean to "inject" a ranking reversal into the data? For `convergence` and `seasonal_anomaly`, even the parameter schemas are unspecified.
- **Unstub requirements:** Spec author must define the injection algorithm for each type (how to mutate the DataFrame to produce the desired statistical signal). Engineering effort alone is insufficient.

---

**3. Censoring injection**
- **Location:** [realism.py:60](../phase_2/engine/realism.py#L60)
- **Stage3 Item:** M1-NC-7 — `censoring` parameter semantics in `set_realism`
- **Decision:** P2-6 — "ALREADY_IMPLEMENTED. `set_realism` stores censoring. `realism.py` raises `NotImplementedError`."
- **Current behavior:** If user calls `set_realism(censoring={...})`, the config is stored, but `apply_realism()` raises `NotImplementedError` when it encounters a non-None `censoring` value. `missing_rate` and `dirty_rate` work correctly.
- **Design rationale:** The spec mentions censoring as a parameter but never defines what it means. Left/right/interval censoring? Which columns? What distribution truncation mechanism? None of this is specified.
- **Unstub requirements:** Spec author must define censoring semantics (type, target columns, mechanism).

---

**4. `check_dominance_shift` validation stub**
- **Location:** [pattern_checks.py:158](../phase_2/validation/pattern_checks.py#L158)
- **Stage3 Item:** M5-NC-4 — L3 `dominance_shift` validation logic
- **Decision:** P1-3 — "STUB. Return `Check(passed=True)`."
- **Current behavior:** Always returns `passed=True` with detail "dominance_shift validation not yet implemented". Wired into `SchemaAwareValidator._run_l3()` dispatch.
- **Design rationale:** The spec delegates to `self._verify_dominance_change(df, p, meta)` — an opaque reference with no implementation. The suggested definition (rank change of entity across temporal split) is too vague for two engineers to produce equivalent implementations.
- **Unstub requirements:** Spec author must define the statistical test (what metric, what threshold, what temporal split logic).

---

**5. `check_convergence` validation stub**
- **Location:** [pattern_checks.py:185](../phase_2/validation/pattern_checks.py#L185)
- **Stage3 Item:** M5-NC-5 — Missing validation for `convergence`
- **Decision:** P1-4 — "STUB."
- **Current behavior:** Always returns `passed=True` with detail "convergence validation not yet implemented".
- **Design rationale:** Completely absent from §2.9 validation logic. The pattern type is listed in the enum but has no validation pseudocode, no parameters, no thresholds.
- **Unstub requirements:** Spec author must define what "convergence" means statistically and how to validate it.

---

**6. `check_seasonal_anomaly` validation stub**
- **Location:** [pattern_checks.py:211](../phase_2/validation/pattern_checks.py#L211)
- **Stage3 Item:** M5-NC-5 — Missing validation for `seasonal_anomaly`
- **Decision:** P1-4 — "STUB."
- **Current behavior:** Always returns `passed=True` with detail "seasonal_anomaly validation not yet implemented".
- **Design rationale:** Same as convergence — completely absent from §2.9. No parameter schema, no validation logic.
- **Unstub requirements:** Spec author must define seasonal anomaly detection and validation criteria.

---

**7. Mixture distribution KS test**
- **Location:** [statistical.py:241](../phase_2/validation/statistical.py#L241)
- **Stage3 Item:** Linked to M1-NC-1 (P1-1) — mirrors the generation stub
- **Decision:** Implicit from P1-1 — can't validate what can't be generated.
- **Current behavior:** Returns `passed=True` with detail "mixture distribution KS test not yet implemented". In practice, this code path is unreachable because generation raises `NotImplementedError` first.
- **Design rationale:** The KS test requires knowing the theoretical CDF of the mixture. Without the param_model schema, there's no reference distribution to test against.
- **Unstub requirements:** Requires mixture generation to be implemented first, then construct composite CDF from components for the KS test.

---

### DEFERRED_STUB (5) — Could be implemented with engineering effort alone

---

**8. Multi-column `on` in group dependency**
- **Location:** [relationships.py:127](../phase_2/sdk/relationships.py#L127)
- **Stage3 Item:** M1-NC-5
- **Decision:** P2-4 — "Restrict to single-column `on` for v1. Keep `on: list[str]` for forward compat."
- **Current behavior:** Raises `NotImplementedError` with clear message when `len(on) != 1`. Single-column dependencies work fully.
- **Design rationale:** The conditional_weights dict structure for joint conditioning (tuple keys) was proposed but adds complexity to skeleton generation, metadata building, and validation. Deferred to v2 as a scope decision.
- **Unstub requirements:** Engineering effort — define tuple-keyed conditional_weights, implement joint conditioning in `build_skeleton`, update metadata builder and group dependency validation.

---

**9. `orchestrate()` structural stub**
- **Location:** [retry_loop.py](../phase_2/orchestration/retry_loop.py) (entire file)
- **Stage3 Item:** M3-NC-1 through M3-NC-6
- **Decision:** P1-5 — Sandbox semantics are ALREADY_IMPLEMENTED in `sandbox.py`. The `retry_loop.py` is a structural stub for the extracted entry point.
- **Current behavior:** Always returns `SkipResult`. Logs a warning. The agentic pipeline path (`pipeline.py:run_agentic()`) is non-functional via this entry point.
- **Design rationale:** The full retry logic (LLM → sandbox → validate) already exists in `sandbox.py:run_with_retries()`. The `retry_loop.py` was created as the target architecture for a clean M3 extraction, but the migration hasn't occurred. The LLM client (`llm_client.py`) exists but isn't wired in.
- **Unstub requirements:** Engineering effort — wire `LLMClient` + `assemble_prompt()` + `code_validator` + `sandbox.run_with_retries()` into orchestrate(). Migrate retry logic from sandbox.py.

---

**10. DeclarationStore integration into FactTableSimulator**
- **Location:** [types.py:382](../phase_2/types.py#L382)
- **Stage3 Item:** Cross-module contract (freeze-before-generate)
- **Decision:** Not explicitly in blocker_resolutions; noted as a deferred migration.
- **Current behavior:** `DeclarationStore` class exists with `freeze()` method, but `FactTableSimulator` uses its own `OrderedDict` registries directly. The freeze-before-generate contract is NOT enforced at runtime.
- **Design rationale:** The DeclarationStore was designed as the future typed interface, but FactTableSimulator was implemented first with raw dicts. The migration was explicitly deferred to avoid destabilizing working code.
- **Unstub requirements:** Engineering effort — wire DeclarationStore into FactTableSimulator.__init__, call freeze() at the start of generate(), update all internal registry access to go through the store.

---

**11. Pipeline orchestrate() unpacking**
- **Location:** [pipeline.py:93](../phase_2/pipeline.py#L93)
- **Stage3 Item:** Depends on Finding #9 (orchestrate stub)
- **Decision:** Implicit from P1-5.
- **Current behavior:** Dead code path — the comment describes unpacking `(df, metadata, raw_declarations)` from orchestrate(), but orchestrate() always returns SkipResult, so the `if isinstance(result, SkipResult)` guard catches everything.
- **Design rationale:** The TODO is forward-looking. Once orchestrate() is implemented, this path will need to unpack the triple and return it to the caller.
- **Unstub requirements:** Blocked on Finding #9. Once orchestrate() returns real results, uncomment the unpacking.

---

**12. `check_ranking_reversal` validation stub**
- **Location:** [pattern_checks.py:237](../phase_2/validation/pattern_checks.py#L237)
- **Stage3 Item:** M5 SPEC_READY #12 — L3 ranking reversal validation
- **Decision:** Not explicitly stubbed in blocker_resolutions (this is SPEC_READY).
- **Current behavior:** Always returns `passed=True`. The TODO comment contains the exact algorithm: `means[m1].rank().corr(means[m2].rank()) < 0`.
- **Design rationale:** Although the validation spec is clear, the corresponding pattern *injection* (Finding #2) raises `NotImplementedError`. Implementing validation for an uninjectable pattern would produce a validator with no data to validate against. The implementation was likely deferred because the injection side is blocked.
- **Unstub requirements:** Engineering effort only — the algorithm is specified in the TODO comment. However, practically useful only after ranking_reversal injection is implemented.

---

### NO_OP (1) — Parameter accepted but intentionally unused

---

**13. `scale` parameter on `add_measure`**
- **Location:** [columns.py:244](../phase_2/sdk/columns.py#L244)
- **Stage3 Item:** M1-NC-2
- **Decision:** P2-5 — "Keep accepting and storing. Add a warning when non-None."
- **Current behavior:** `scale` is stored in `col_meta["scale"]` but no code reads it. A warning is logged: "has no effect in the current implementation."
- **Design rationale:** The `scale` parameter appears in the §2.5 whitelist method signature but is never defined, used, or referenced elsewhere in the spec. Removing it would break forward compatibility; ignoring it silently would confuse users. The warning is the compromise.
- **Unstub requirements:** Spec author must define what `scale` does — post-sampling multiplier? parameter scaling? units conversion?

---

### TODO_ENHANCEMENT (4) — Future improvements, not missing requirements

---

**14. Batch error collection**
- **Location:** [simulator.py:32](../phase_2/sdk/simulator.py#L32)
- **Stage3 Item:** M3-NC-3
- **Decision:** P1-5 — "Accept one-at-a-time. Add TODO comment."
- **Current behavior:** Standard Python exception propagation surfaces one error per sandbox execution. With 3 retries, up to 3 independent errors can be surfaced (one per attempt).
- **Design rationale:** Implementing multi-error collection would require M1 to catch all validation errors in a single pass and relay them as a batch. This is a nice-to-have optimization that reduces retry iterations but isn't required for correctness.
- **Unstub requirements:** Engineering effort — implement compound exception collection in M1 validation, relay batch in sandbox error feedback.

---

**15. Context window exhaustion strategy**
- **Location:** [sandbox.py:629](../phase_2/orchestration/sandbox.py#L629)
- **Stage3 Item:** M3-NC-4
- **Decision:** P1-5 — "Accept full history for 3 retries. Add TODO comment for token-budget check."
- **Current behavior:** Full error feedback history is sent to the LLM on each retry with no truncation. At max_retries=3, this produces ~8 messages, which is manageable for modern LLMs.
- **Design rationale:** Token budget is only a concern if max_retries is increased significantly. For the default of 3, the full history fits comfortably in context.
- **Unstub requirements:** Engineering effort — add token counting before each retry, implement summarization/truncation when budget exceeded.

---

**16. Stale "BLOCKED — stubs" comment in generator.py**
- **Location:** [generator.py:47,87](../phase_2/engine/generator.py#L47)
- **Stage3 Item:** M2-NC-1 (P0-2: formula evaluation mechanism)
- **Decision:** P0-2 — was implemented. The comment is stale.
- **Current behavior:** The docstring says "Phase β: generate measures (BLOCKED — stubs)" and the inline comment says "Phase β: Measure generation (BLOCKED — stubs)", but the code actually calls `_measures.generate_measures()` which IS fully implemented (stochastic sampling, structural formula evaluation, parameter overrides — all working).
- **Design rationale:** These comments were written before P0-2 was implemented and weren't cleaned up afterward.
- **Unstub requirements:** Just update the comments. No functional change needed.

---

**17. Stale TODO reference in `check_group_dependency_transitions`**
- **Location:** [statistical.py:413](../phase_2/validation/statistical.py#L413)
- **Stage3 Item:** M5 SPEC_READY #9
- **Decision:** Not in blocker_resolutions (SPEC_READY item).
- **Current behavior:** The function IS fully implemented — it computes observed conditional distributions, checks max deviation < 0.10, and returns proper Check results. The "TODO" in the docstring is a reference marker, not an actual to-do.
- **Design rationale:** The TODO was likely written as a tracking label during implementation and left in place.
- **Unstub requirements:** Remove or convert the TODO to a reference comment (e.g., "Implements M5 SPEC_READY #9").

---

## Classification Summary

| Category | Count | Items |
|---|---|---|
| **SPEC_GAP_STUB** | 7 | mixture sampling, 4 pattern injections, censoring, dominance_shift validation, convergence validation, seasonal_anomaly validation, mixture KS test |
| **DEFERRED_STUB** | 5 | multi-column `on`, orchestrate() stub, DeclarationStore integration, pipeline unpacking, ranking_reversal validation |
| **NO_OP** | 1 | `scale` parameter |
| **PARTIAL** | 0 | — |
| **TODO_ENHANCEMENT** | 4 | batch errors, context window, stale generator comment, stale statistical TODO |

Classification complete. **7 SPEC_GAP_STUB, 5 DEFERRED_STUB, 1 NO_OP, 0 PARTIAL, 4 TODO_ENHANCEMENT.** Send 'Phase C' to scan for unexpected gaps beyond stubs.

---

## 👤 User

Phase C

---

## 🤖 Claude

Starting Phase C — Missing Functionality Scan. I need to check the stage4 file tree, cross-module contracts, and test coverage.

---

## 🤖 Claude

Good. Now let me verify the cross-module contracts and check for missing test files.

---

## 🤖 Claude

Now let me verify the remaining contracts — `overrides` param in `run_pipeline`, the `validate` method signature, and check for `ParameterOverrides` usage.

---

## 🤖 Claude

Let me verify the metadata enrichment contract and check for the demo file.

---

## 🤖 Claude

Now let me get per-module test counts.

---

## 🤖 Claude

Let me verify the types.py dataclass inventory against what stage4 expects, and count tests per module.

---

## 🤖 Claude

Let me check a few more stage4 expectations against actual implementation.

---

## 🤖 Claude

Now I have all the data needed. Let me write the comprehensive `stub_inventory.md`.

---

## 🤖 Claude

Stub inventory written to [stub_inventory.md](stub_inventory.md). Here's the bottom line:

**Classified: 18 intentional stubs/TODOs + 4 unexpected gaps across 12 files.**

| Category | Count | Key Items |
|---|---|---|
| SPEC_GAP_STUB | 8 | mixture sampling, censoring, convergence/seasonal_anomaly (injection + validation), dominance_shift validation, mixture KS test |
| DEFERRED_STUB | 5 | multi-column `on`, orchestrate() stub, DeclarationStore integration, pipeline unpacking, ranking_reversal validation |
| NO_OP | 1 | `scale` parameter |
| TODO_ENHANCEMENT | 4 | batch errors, context window, 2 stale comments |

**Unexpected gaps found:**
1. **`ColumnDescriptor` dataclass never defined** — stage4 specified it; implementation uses raw dicts
2. **M3 orchestration has ZERO unit tests** — 5 source files (700+ lines in sandbox.py alone), zero dedicated tests
3. **`tests/demo_end_to_end.py` missing** — expected by stage4 file tree
4. **`ValidationError` exception missing** — replaced by `ValidationReport` data structure (better design)

**Cross-module contracts: 7 of 8 PASS.** The one failure is `DeclarationStore.freeze()` not being enforced at runtime (deferred).

**System readiness:**
- **Direct SDK path: YES** — fully functional for 7/8 distribution families
- **Agentic path: NO** — orchestrate() is a stub, but all underlying components exist and work

Review before proceeding to LLM integration or completeness certification.

---

