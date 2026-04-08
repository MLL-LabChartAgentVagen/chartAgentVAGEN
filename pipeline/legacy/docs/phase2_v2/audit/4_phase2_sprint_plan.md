# Phase 2 — Sprint Plan

**Source:** Implementation Alignment Map (Stage 3)
**Rules applied:** Only SPEC_READY and NEEDS_CLARIFICATION subtasks are scheduled. BLOCKED and SPEC_INCORRECT subtasks go to the Blocked Backlog. Sprints respect dependency order. Max 12 subtasks per sprint.

**Patch version:** v4 — Orchestrator Cross-Ref (2026-03-25)

---

## Sprint 1: Foundation — Data Structures, Constructor, Exception Hierarchy

**Deliverable:** All core data classes instantiate correctly. All custom exceptions raise with descriptive messages. The `FactTableSimulator` constructor initializes with empty, typed registries. This sprint has zero external dependencies and produces the foundation every subsequent sprint builds on.

**Subtasks (9):**

| ID | Description | Readiness | Assumption |
|----|-------------|-----------|------------|
| 1.1.1 | `__init__(target_rows, seed)` constructor | SPEC_READY | — |
| 1.1.2 | Internal registry data structures | SPEC_READY | — |
| 2.1.1 | `DimensionGroup` data class | SPEC_READY | — |
| 2.2.1 | `OrthogonalPair` data class | SPEC_READY | — |
| 2.2.2 | `GroupDependency` data class | SPEC_READY | — |
| 6.1.1 | `CyclicDependencyError` | SPEC_READY | — |
| 6.1.2 | `UndefinedEffectError` | SPEC_READY | — |
| 6.1.3 | `NonRootDependencyError` | SPEC_READY | — |
| 6.1.4 | Additional validation errors (`InvalidParameterError`, etc.) | NEEDS_CLAR. | Assume: add `InvalidParameterError` for computed params outside domain (σ<0, shape<0). Covers A5a proactively. |

**Assumptions carried:** [A5a] `InvalidParameterError` exception type is invented ahead of spec clarification on parameter domain validation.

**Exit gate:** `pytest` passes for: all data classes instantiate with correct fields; `CyclicDependencyError("A → B → A")` contains cycle path in `str(e)`; `UndefinedEffectError` and `NonRootDependencyError` produce messages matching §2.7 examples; `FactTableSimulator(500, 42)` has empty registries and correct attributes.

---

## Sprint 2: Column Declaration API — `add_category()` + `add_temporal()`

**Deliverable:** The two column-declaration methods pass all unit tests including edge cases. Dimension groups are correctly created and maintained. This sprint produces the categorical/temporal foundation that measure declarations and relationship declarations require.

**Depends on:** Sprint 1 (constructor, `DimensionGroup`, registries)

**Subtasks (10):**

| ID | Description | Readiness | Assumption |
|----|-------------|-----------|------------|
| 1.2.1 | `add_category` signature & parameter validation | NEEDS_CLAR. | Assume `len(values) >= 2` required; single-value categoricals rejected. |
| 1.2.2 | Weight auto-normalization | SPEC_READY | — |
| 1.2.3 | Per-parent conditional weights (dict form) | NEEDS_CLAR. | Assume all parent values MUST be present as dict keys; missing keys raise `ValueError`. |
| 1.2.4 | Parent existence & same-group validation | SPEC_READY | — |
| 1.2.5 | Group registry update | SPEC_READY | — |
| 1.2.6 | Reject duplicate group root | SPEC_READY | — |
| 1.3.1 | `add_temporal` signature & date parsing | SPEC_READY | — |
| 1.3.2 | Frequency validation | NEEDS_CLAR. | Spec only demonstrates `freq="daily"`; no whitelist defined. Accept any string at declaration time; sampling semantics deferred to engine sprint (4.1.4). |
| 1.3.3 | Derive whitelist validation | SPEC_READY | — |
| 1.3.4 | Temporal group registration | NEEDS_CLAR. | Assume: auto-creates group named `"time"`; only one `add_temporal` call allowed; `"time"` is reserved and cannot be used by `add_category`. |

**Assumptions carried:** [A9] `len(values) >= 2`. [A6] Per-parent dict must cover all parent values. [B1] No frequency whitelist; only `"daily"` has defined sampling. [A10] Single temporal column; group auto-named `"time"`.

**Exit gate:**

*Spec-backed assertions* (directly traceable to spec text):
- `add_category("x", [], [], "g")` raises empty-values error (§2.1.1: "rejects empty values").
- Auto-normalization produces weights summing to 1.0 (§2.1.1: "Auto-normalized").
- Parent in wrong group raises (§2.1.1: "validates parent exists in same group").
- `add_temporal` with inverted dates raises.
- `derive=["fiscal_year"]` raises; `derive=["quarter", "is_weekend"]` accepted (§2.1.1 whitelist).
- Group `"time"` created with correct root and derived children (§2.2).

*Assumption-backed assertions* (proceeding under documented assumption, not explicit spec):
- `add_category` with `values=["A"], weights=[1.0]` raises single-value error [A9 assumption].
- Per-parent dict missing a parent key raises `ValueError` [A6 assumption].
- Duplicate root in same group raises [§2.2 singular "a root" — strong inference].
- Second `add_temporal` call raises [A10 assumption].

---

## Sprint 3: Measure Declarations + Relationship API

**Deliverable:** `add_measure()` (non-blocked paths), `add_measure_structural()` (non-blocked paths), `declare_orthogonal()`, and `add_group_dependency()` pass unit tests. The measure DAG tracks root nodes and detects cycles. Orthogonal/dependency mutual exclusion enforced. This sprint completes the *declarable* portion of the SDK (minus blocked features).

**Depends on:** Sprint 2 (categories must exist for effects validation and group root lookups)

**Subtasks (12):**

| ID | Description | Readiness | Assumption |
|----|-------------|-----------|------------|
| 1.4.1 | `add_measure` signature & family validation | NEEDS_CLAR. | `scale` parameter: accept and store; ignore in generation; log warning if non-None. |
| 1.4.2 | `param_model` constant-parameter form | NEEDS_CLAR. | For `gaussian`/`lognormal`: accept `mu`/`sigma`. For other families: store raw dict keys without family-specific validation until A5 is resolved. Document assumption. |
| 1.4.5 | Register as DAG root node | SPEC_READY | — |
| 1.5.1 | `add_measure_structural` signature validation | SPEC_READY | — |
| 1.5.3 | Effects dictionary validation | SPEC_READY | — |
| 1.5.5 | Cycle detection on measure DAG | SPEC_READY | — |
| 1.6.1 | `declare_orthogonal` signature & group existence | SPEC_READY | — |
| 1.6.2 | Store orthogonal pair (order-independent) | SPEC_READY | — |
| 1.6.3 | Conflict check: orthogonal vs dependency | NEEDS_CLAR. | Mutual exclusion inferred from §2.2, not explicitly stated. |
| 1.7.1 | `add_group_dependency` root-only constraint | SPEC_READY | — |
| 1.7.2 | Conditional weights validation | NEEDS_CLAR. | Assume `on` restricted to single column; raise if `len(on) > 1`. |
| 1.7.3 | Root-level DAG acyclicity check | SPEC_READY | — |

**Assumptions carried:** [A2] `scale` stored but ignored. [A5] Only `gaussian`/`lognormal` param keys validated; others stored raw. [A7] `on` restricted to single column.

**Exit gate:** `add_measure("m", "weibull", ...)` raises unsupported family. Constant `param_model` stored as intercept-only. `add_measure` with `scale=100` stores it and logs warning. `add_measure_structural` with cycle raises `CyclicDependencyError`. Effects referencing undeclared categorical raises. `declare_orthogonal("entity", "entity", ...)` raises self-orthogonal error. Orthogonal after dependency raises conflict. `add_group_dependency` with non-root column raises `NonRootDependencyError`. `on=["a","b"]` raises multi-column error. Bidirectional root dependencies raise `CyclicDependencyError`.

---

## Sprint 4: Pattern/Realism Stubs + DAG Construction

**Deliverable:** `inject_pattern()` validates and stores patterns for the two specified types (outlier_entity, trend_break). `set_realism()` stores config. The pre-formula-edge generation DAG is constructible from categorical, temporal, group-dependency, and effects-predictor declarations, and produces correct topological orderings for this subset. This sprint closes the *declaration phase* of the SDK and opens the *generation phase*.

> **Scope note (3.1.2):** At this sprint, structural measure formula edges are not yet available — the formula DSL is blocked (A3 / Blocker 2). The DAG constructed here includes edge types 1–4 (parent→child, on→child_root, temporal_root→derived, effects predictor→measure) but NOT edge type 5 (formula measure ref→structural). Full DAG construction, including formula-derived edges, will be completed when Blocker 2 resolves.

**Depends on:** Sprint 3 (all declaration methods, measure DAG, group dependencies)

**Subtasks (9):**

| ID | Description | Readiness | Assumption |
|----|-------------|-----------|------------|
| 1.7.4 | `add_group_dependency` conflict check with orthogonal | NEEDS_CLAR. | Mutual exclusion inferred from §2.2, not explicitly stated. |
| 1.8.1 | `inject_pattern` signature & type validation | SPEC_READY | — |
| 1.8.2 | Target expression storage | NEEDS_CLAR. | Assume: store target string as-is; no declaration-time parsing. Runtime evaluation via `df.query()`. |
| 1.8.3 | Column validation (must be declared measure) | NEEDS_CLAR. | Restriction to measure columns is strong inference, not explicitly stated. |
| 1.8.5 | Store pattern | SPEC_READY | — |
| 1.9.1 | `set_realism` signature & validation | NEEDS_CLAR. | `missing_rate`/`dirty_rate` validated as [0,1]. `censoring` accepted as opaque dict; deferred to engine. |
| 3.1.1 | `_build_full_dag()` — merge all column types | NEEDS_CLAR. | Assume 5 edge rules: (1) parent→child, (2) on→child_root, (3) temporal_root→derived, (4) effects predictor→measure, (5) formula measure ref→structural + effect_col→structural. Rule 5 deferred until Blocker 2 resolves. |
| 3.1.2 | `topological_sort()` — pre-formula-edge DAG | NEEDS_CLAR. | Standard algorithm; cycle → `CyclicDependencyError`. Scoped to the pre-formula DAG available at this sprint. Tie-breaking rule for determinism is unspecified; assume lexicographic. |
| 3.2.1 | Extract measure-only sub-DAG | SPEC_READY | — |

**Assumptions carried:** [A4] `censoring` stored as opaque dict. [B4, B5] DAG construction uses 5 assumed edge rules, with rule 5 deferred.

**Exit gate:** `inject_pattern("unknown_type", ...)` raises. Pattern appended to internal list. `set_realism(1.5, 0.0)` raises. Pre-formula DAG for the one-shot example produces correct node set and edge set for edge types 1–4 (categorical hierarchies, group dependencies, temporal derivations, effects predictors). Topological sort places `hospital` before `department`, `severity` before `payment_method` (group dep edge). Measure sub-DAG order = `[wait_minutes, cost, satisfaction]` (the measure DAG edges are from `add_measure_structural` symbol resolution, which uses formula parsing — these edges are registered at declaration time via 1.5.2 when it unblocks; for now, test with manually registered edges). Cycle in DAG raises `CyclicDependencyError`.

---

## Sprint 5: Engine Phase α (Skeleton) + Post-Processing + Metadata (Ready Fields)

**Deliverable:** The engine generates skeleton-only DataFrames — categorical roots, dependent roots, child categories, temporal roots, and derived temporal columns — for the one-shot example scenario. Post-processing produces a valid `pd.DataFrame`. Schema metadata emitter produces all non-INCORRECT fields. This is the first sprint that produces *actual data*.

> **Scope note:** This sprint produces skeleton DataFrames (non-measure columns only). Measure generation requires Blockers 2 and 3 to resolve. Specific dtype policies (e.g., `category` vs. `object`, `datetime64[ns]` vs. `datetime64[s]`) are implementation design choices not prescribed by the spec.

**Depends on:** Sprint 4 (DAG construction, topological order)

**Subtasks (10):**

| ID | Description | Readiness | Assumption |
|----|-------------|-----------|------------|
| 4.1.1 | Sample independent categorical roots | NEEDS_CLAR. | Undeclared cross-group default behavior undefined; assume independent sampling. |
| 4.1.2 | Sample cross-group dependent roots | NEEDS_CLAR. | Single-column `on` is clear; multi-column `on` rejected. |
| 4.1.3 | Sample within-group child categories | SPEC_READY | — |
| 4.1.4 | Sample temporal root | NEEDS_CLAR. | Assume: `weekly` → uniform over Monday dates; `monthly` → uniform over 1st-of-month dates. `daily` = uniform random dates. |
| 4.1.5 | Derive temporal children | NEEDS_CLAR. | Assume: `day_of_week` → 0–6, `month` → 1–12, `quarter` → 1–4, `is_weekend` → bool. |
| 4.5.1 | DataFrame assembly & dtype casting | NEEDS_CLAR. | Dtype policy is an implementation choice. |
| 5.1.1 | Emit `dimension_groups` metadata | SPEC_READY | — |
| 5.1.2 | Emit `orthogonal_groups` metadata | SPEC_READY | — |
| 5.1.5 | Emit `measure_dag_order` metadata | SPEC_READY | — |
| 5.1.7 | Emit `total_rows` metadata | SPEC_READY | — |

**Assumptions carried:** [B1] Non-daily temporal sampling = snap-to-period-start + uniform. [A11] Derived column value sets as specified above.

**Exit gate:** For the one-shot example with `seed=42`: skeleton DataFrame has 500 rows. `hospital` frequencies within ±0.05 of declared weights. `payment_method` conditional on `severity=="Severe"` ≈ `{Insurance:0.80, ...}`. `department` sampled conditionally on `hospital`. All dates in [2024-01-01, 2024-06-30]. `day_of_week` for known dates is correct. Result is a valid `pd.DataFrame`. Metadata `dimension_groups` matches §2.6 example structure.

---

## Sprint 6: Pattern Injection (Specified Types) + Realism (Non-Censoring) + Validator Framework + L1 Ready Checks

**Deliverable:** Outlier entity and trend break patterns are injected into generated DataFrames. Missing-value and dirty-value realism injection works. The `SchemaAwareValidator` framework is operational (minus the orchestrator — deferred) with all SPEC_READY L1 checks passing. This is the first sprint that validates output quality.

> **Deferral note (8.1.3):** The `validate(df, meta)` orchestrator is NEEDS_CLARIFICATION — its correct behavior depends on unresolved upstream issues: whether L2 runs on pre- or post-injection data (B2) and whether L1 finiteness checks are adjusted for realism (C6). It is deferred until these dependencies are resolved, likely as part of the post-blocker integration sprints. L1 checks can be tested individually without the orchestrator.

**Depends on:** Sprint 5 (engine produces skeleton DataFrames; metadata is partially emittable)

**Subtasks (10):**

| ID | Description | Readiness | Assumption |
|----|-------------|-----------|------------|
| 4.3.1 | Outlier entity injection | NEEDS_CLAR. | Implement: shift target subset mean to z_score × global_std. L2/pattern conflict (B2) is a validator issue, not an engine issue. |
| 4.3.2 | Trend break injection | NEEDS_CLAR. | Implement: scale values after `break_point` by `(1 + magnitude)`. Same B2 assumption. |
| 4.4.1 | Missing value injection | NEEDS_CLAR. | Implement NaN injection at `missing_rate`. L1 `finite_*` conflict (C6) is a validator issue. |
| 4.4.2 | Dirty value injection | NEEDS_CLAR. | Assume: character-level perturbation of categorical values (swap, delete, insert). |
| 8.1.1 | `Check` data class | SPEC_READY | — |
| 8.1.2 | `ValidationReport` aggregator | SPEC_READY | — |
| 8.2.1 | Row count check | SPEC_READY | — |
| 8.2.2 | Categorical cardinality check | SPEC_READY | — |
| 8.2.5 | Orthogonal independence (chi-squared) | SPEC_READY | — |
| 8.2.6 | Measure DAG acyclicity re-check | SPEC_READY | — |

**Assumptions carried:** [B2] Pattern injection implemented as specified; L2 conflict deferred. [C6] Realism NaN injection implemented; L1 conflict deferred. [—] Dirty values = character-level perturbations.

**Exit gate:** After outlier injection on `hospital=='Xiehe' & severity=='Severe'` with `z_score=3.0`: target subset mean z-score ≥ 3.0. After trend break injection on `hospital=='Huashan'` with `break_point=2024-03-15, magnitude=0.4`: `|mean_after - mean_before| / mean_before > 0.15`. Missing injection at rate 0.05: `df.isna().sum().sum() / df.size ≈ 0.05`. `ValidationReport` correctly aggregates `all_passed` and `failures`. Row count, cardinality, chi-squared, and acyclicity checks produce correct pass/fail on known-good and known-bad DataFrames.

---

## Sprint 7: L3 Pattern Validation (Specified) + Auto-Fix Strategies (Isolated Stubs) + L2 Helper

**Deliverable:** L3 validation correctly detects outlier entities and trend breaks. The auto-fix dispatch and three specified strategies are implemented as **isolated stubs** — each strategy's unit-level input→output contract is verified, but integration-level behavior (persistent mutation, retry interaction with L2) is deferred. The `_max_conditional_deviation` helper is ready for L2 when metadata blockers resolve. This sprint completes the *specified* validation and auto-fix components.

> **Dependency note (9.2.1–9.2.3):** The three fix strategies depend on unresolved B2/B3 findings. The auto-fix mutation model (B3: do strategies mutate the simulator instance or post-process the DataFrame?) and the L2/pattern conflict (B2: does widening variance fight pattern injection?) are both undefined. These strategies are built and unit-tested as isolated stubs — verifying that calling the function produces the expected parameter change on a mock input — but cannot be integration-tested in the retry loop until B2/B3 resolve.

**Depends on:** Sprint 6 (validator framework, L1 checks, pattern injection)

**Subtasks (7):**

| ID | Description | Readiness | Assumption |
|----|-------------|-----------|------------|
| 8.4.1 | Outlier entity z-score check | SPEC_READY | — |
| 8.4.3 | Trend break magnitude check | SPEC_READY | — |
| 8.3.7 | `_max_conditional_deviation()` helper | SPEC_READY | — |
| 9.1.1 | `match_strategy()` glob-based matcher | SPEC_READY | — |
| 9.2.1 | `widen_variance(check, factor=1.2)` — **isolated stub** | NEEDS_CLAR. | Assume: mutates sigma param by factor. B2/B3 dependency — cannot integration-test until mutation model is defined. |
| 9.2.2 | `amplify_magnitude(check, factor=1.3)` — **isolated stub** | NEEDS_CLAR. | Assume: mutates pattern spec magnitude by factor. Same B2/B3 dependency. |
| 9.2.3 | `reshuffle_pair(check)` — **isolated stub** | NEEDS_CLAR. | Assume: only reshuffle columns NOT referenced in any pattern `target` expression. Same B2/B3 dependency. |

**Assumptions carried:** [B7] Fix strategies mutate the simulator instance, not the script (assumed for stub design, pending B3 resolution). [B3] `reshuffle_pair` excludes pattern-target columns. [B2/B3] All three strategies are isolated stubs; integration behavior deferred.

**Exit gate:** L3 outlier check: z-score ≥ 2.0 on injected data → passes; z-score < 2.0 → fails. L3 trend check: 20% shift → passes; 10% shift → fails. `match_strategy("ks_wait_minutes_marginal", AUTO_FIX)` returns `widen_variance`. Stub-level unit tests: `widen_variance` applied to a mock param dict with sigma=0.35 produces sigma=0.42; `amplify_magnitude` applied to a mock pattern spec with z_score=3.0 produces z_score=3.9; `reshuffle_pair` applied to a mock column pair produces a permuted column. No assertions about downstream validation improvement, p-value changes, or persistent retry behavior — these depend on B2/B3 resolution.

---

## Sprint 8: Integrate Existing `LLMClient` Capabilities + Sandbox Error Feedback Loop

**Deliverable:** The prompt template renders correctly with scenario context. `LLMClient.generate_code()` is wired into the sandbox execution path, and its fence-stripping + provider-adaptation capabilities are verified via integration / contract tests. The error feedback loop catches SDK exceptions and retries LLM code generation up to 3 times. This sprint is *independent* of the engine path (Sprints 5–7) and could be parallelized, but is sequenced last because the pipeline orchestrator (blocked) needs everything.

> **Infrastructure note (v3):** Code fence stripping and multi-provider parameter adaptation are **already implemented** in `pipeline/core/llm_client.py` (`LLMClient.generate_code()`, `adapt_parameters()`). This sprint focuses on **integration verification and contract testing** of these existing capabilities within the Phase 2 sandbox context, not on reimplementing LLM plumbing from scratch. **Forward ref (v4):** Sprint 8 构建的 sandbox 反馈闭环将在后续编排重构中封装为 `Phase2Service`（参见 `audit/5_agpds_pipeline_runner_redesign.md`）。

**Depends on:** Sprint 1 (exception types for the error loop to catch). Does NOT depend on Sprints 2–7.

**Subtasks (6):**

| ID | Description | Readiness | Assumption |
|----|-------------|-----------|------------|
| 10.1.1 | System prompt construction | SPEC_READY | — |
| 10.2.1 | Integration verification: confirm `LLMClient.generate_code()` produces valid, fence-free Python for Phase 2 scripts | NEEDS_CLAR. | Reuses existing fence stripping in `LLMClient.generate_code()`. Subtask is a contract test, not a from-scratch implementation. |
| 10.2.2 | Validate code contains `build_fact_table` and `generate()` | NEEDS_CLAR. | Assume: `build_fact_table` returns `Tuple[DataFrame, dict]` per §2.8 type hint. |
| 7.1.1 | Execute LLM script in sandbox | NEEDS_CLAR. | Execution flow is clear; security policy (imports, resource limits) is unspecified. LLM request plumbing is delegated to `LLMClient` — this subtask covers only `exec()` namespace, timeout, and error capture. |
| 7.1.2 | Format error feedback for LLM | SPEC_READY | — |
| 7.1.3 | Retry loop with max_retries=3 | NEEDS_CLAR. | Assume: §2.7 loop is sequential with (not nested inside) §2.9 loop. §2.7 retries until code *executes*; then §2.9 handles statistical quality. |

**Assumptions carried:** [A12] Return type is `Tuple[DataFrame, dict]`. [C5] §2.7 and §2.9 loops compose sequentially, not nested.

**Exit gate:**

*Spec-conformance tests* (directly traceable to §2.5 and §2.7):
- Prompt template with `{scenario_context}` replaced by one-shot example produces string matching §2.5 structure.
- Validation rejects code without `sim.generate()` (§2.5 constraint 6).
- Sandbox execution catches `CyclicDependencyError` and returns traceback string (§2.7 steps 3–4).
- Error feedback payload contains original code, exception class, traceback, and fix instruction (§2.7 step 5).
- Retry loop stops after 3 failures (§2.7 step 6: `max_retries=3`).
- Successful 2nd attempt returns result without hitting attempt 3.

*Integration verification for `LLMClient` (v3)* (confirm existing capabilities work in Phase 2 context):
- Calling `LLMClient.generate_code()` with a Phase 2 system prompt returns fence-free Python (verifies existing fence-stripping behavior).
- `LLMClient.adapt_parameters()` with `response_format='code'` produces provider-appropriate request kwargs (verifies existing provider adaptation).

*Robustness helpers* (implementation choices, not spec requirements):
- Code extraction handles bare code (no fences) gracefully — already guaranteed by `generate_code()` passthrough.

---
---

## Blocked Backlog

All BLOCKED and SPEC_INCORRECT subtasks, grouped by the blocker they depend on.

> **Planning note:** SPEC_INCORRECT items carry equal planning weight to BLOCKED items — both require upstream resolution before correct implementation can proceed.

### Blocker 1: Schema Metadata Completeness (C3 + C8 + C9 + C3a + A2a)

*Resolution needed: Define complete metadata schema including `values`/`weights` for categoricals, `conditional_weights` for child categoricals and group deps, `param_model` for stochastic measures, `formula`/`effects`/`noise_sigma` for structural measures, `scale`, and pattern `params`.*

| Subtask | Description | Status | Finding(s) |
|---------|-------------|--------|------------|
| 5.1.3 | Emit `group_dependencies` with `conditional_weights` | SPEC_INCORRECT | C3, C9 |
| 5.1.4 | Emit `columns` with all validator-required fields | SPEC_INCORRECT | C3, C8, C9, C3a, A2a |
| 5.1.6 | Emit `patterns` with `params` | SPEC_INCORRECT | C3 |
| 8.2.3 | Root marginal weights check (needs `col["values"]`/`col["weights"]`) | SPEC_INCORRECT | C9 |
| 8.2.4 | Measure finite/non-null check (conflicts with realism NaN) | SPEC_INCORRECT | C6 |
| 8.3.3 | Structural residual mean (needs `col["formula"]`) | SPEC_INCORRECT | C8 |
| 8.3.4 | Structural residual std (needs `col["noise_sigma"]`) | SPEC_INCORRECT | C8 |
| 8.3.6 | Group dep conditional deviation (needs `dep["conditional_weights"]`) | SPEC_INCORRECT | C3 |
| 8.4.2 | Ranking reversal check (hard-codes first group) | SPEC_INCORRECT | C11 |

### Blocker 2: Formula DSL Grammar (A3)

*Resolution needed: Define operator whitelist, precedence rules, variable resolution order, and allowed constructs for the formula string in `add_measure_structural()`.*

| Subtask | Description | Status | Finding(s) |
|---------|-------------|--------|------------|
| 1.5.2 | Formula symbol resolution & DAG edge creation | BLOCKED | A3 |
| 4.2.3 | `_eval_structural()` — structural derived measure | BLOCKED | A3 |
| 4.2.4 | `eval_formula()` safe expression evaluator | BLOCKED | A3 |
| 8.3.5 | `eval_formula()` for L2 residual computation | BLOCKED | A3 |

### Blocker 3: Distribution Family Parameter Specification (A5 + A5a + A1 + A1b)

*Resolution needed: Create parameter reference table (family → required keys → valid domains → scipy name mapping). Decide on mixture: specify or defer. Define parameter domain validation or link functions.*

| Subtask | Description | Status | Finding(s) |
|---------|-------------|--------|------------|
| 1.4.3 | `param_model` intercept+effects form (full validation) | BLOCKED | A5, A5a |
| 1.4.4 | Mixture family sub-spec | BLOCKED | A1 |
| 1.5.4 | Noise spec validation (per-family params) | BLOCKED | A5, A1a |
| 4.2.1 | `_sample_stochastic()` — 6 of 8 families | BLOCKED | A5, A5a |
| 4.2.2 | Distribution dispatch table — all 8 families | BLOCKED | A5, A1 |
| 8.3.1 | L2 KS test per predictor cell | BLOCKED | A1b, C2, B2, A5, A2a |
| 8.3.2 | `iter_predictor_cells()` helper | BLOCKED | C7, A5 |

### Blocker 4: Pattern Type Full Specification (A8 + B6 + C1)

*Resolution needed: For each of `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`: define params schema, injection algorithm, and L3 validation logic as a co-designed triple.*

| Subtask | Description | Status | Finding(s) |
|---------|-------------|--------|------------|
| 1.8.4 | Pattern-type-specific param validation (4 types) | BLOCKED | A8 |
| 4.3.3 | Ranking reversal injection | BLOCKED | B6, A8 |
| 4.3.4 | Dominance shift injection | BLOCKED | B6, A8 |
| 4.3.5 | Convergence injection | BLOCKED | B6, A8 |
| 4.3.6 | Seasonal anomaly injection | BLOCKED | B6, A8 |
| 8.4.4 | Dominance shift L3 check | BLOCKED | C10, B6, A8 |
| 8.4.5 | `_verify_dominance_change()` helper | BLOCKED | C10 |
| (8.4.6) | Convergence L3 validation | BLOCKED | C1 |
| (8.4.7) | Seasonal anomaly L3 validation | BLOCKED | C1 |

### Blocker 5: L2 vs. Pattern Injection + Auto-Fix Mutation Model (B2 + B3 + B7 + C5)

*Resolution needed: (a) Define whether L2 runs pre- or post-injection, or excludes pattern-target rows. (b) Redefine auto-fix to mutate simulator instance, not re-run `build_fn`. (c) Define §2.7/§2.9 loop composition. Note: 9.2.1–9.2.3 (built as isolated stubs in Sprint 7) cannot be integration-tested until this blocker resolves.*

| Subtask | Description | Status | Finding(s) |
|---------|-------------|--------|------------|
| 9.3.1 | `generate_with_validation()` retry loop | SPEC_INCORRECT | B7, B3, C5 |

### Blocker 6: Phase 1 → Phase 2 Interface Contract (D1)

*Resolution needed: Formalize `ScenarioContext` as a typed dataclass with required/optional fields, serialization format, and versioning. **Current state (v3):** A working JSON injection path already exists (`json.dumps(scenario, indent=2)` → `run_with_retries()`), and `ScenarioContextualizer.validate_output()` enforces a de facto field set. This blocker applies to **typed interface completeness and stable orchestration**, not to basic injection capability. **Design ref (v4):** `ScenarioContext` typed schema 已在 `audit/5_agpds_pipeline_runner_redesign.md` 的 `result_models.py` 中规划。*

| Subtask | Description | Status | Finding(s) |
|---------|-------------|--------|------------|
| 10.1.2 | Scenario context injection into prompt | BLOCKED | D1 |

### Blocker 7: Censoring Schema (A4)

*Resolution needed: Define censoring dict schema — target columns, direction (left/right), thresholds, indicator columns.*

| Subtask | Description | Status | Finding(s) |
|---------|-------------|--------|------------|
| 4.4.3 | Censoring injection | BLOCKED | A4 |

### Blocker Composite: Pipeline Orchestrator (C5 + D1)

*Resolution needed: Resolve both Blocker 5 (loop composition) and Blocker 6 (Phase 1 typed contract formalization) before the orchestrator can reach a fully validated state. **Note (v3):** The D1 component blocks typed-contract completeness, not basic scenario injection — a working JSON injection path already exists. **Architecture ref (v4):** Orchestrator 架构（`AGPDSPipeline` 职责边界、`GenerationResult` 返回模型）已在 `audit/5_agpds_pipeline_runner_redesign.md` 中定义。*

| Subtask | Description | Status | Finding(s) |
|---------|-------------|--------|------------|
| 11.1.1 | Full pipeline orchestration | BLOCKED | C5, D1 |
| 11.1.2 | Wire §2.7 + §2.9 loops | BLOCKED | C5 |

### Deferred (NEEDS_CLARIFICATION, awaiting upstream resolution)

| Subtask | Description | Readiness | Dependency |
|---------|-------------|-----------|------------|
| 8.1.3 | `validate(df, meta)` orchestrator | NEEDS_CLAR. | Depends on B2 (L2 pre/post injection) and C6 (L1 finiteness vs. realism). Deferred from Sprint 6. |

---
---

## Sprint Summary

| Sprint | Theme | Subtasks | SPEC_READY | NEEDS_CLAR. | Deliverable |
|--------|-------|----------|------------|-------------|-------------|
| 1 | Foundation | 9 | 8 | 1 | Data classes + exceptions + constructor |
| 2 | Column Declarations | 10 | 6 | 4 | `add_category` + `add_temporal` tested |
| 3 | Measure + Relationship API | 12 | 7 | 5 | `add_measure` + structural + orthogonal + group dep |
| 4 | Pattern/Realism Stubs + DAG | 9 | 3 | 6 | Full declaration API + pre-formula DAG construction |
| 5 | Engine α + Post-Processing + Metadata | 10 | 4 | 6 | Skeleton-only DataFrames + metadata |
| 6 | Injection + Validator L1 | 10 | 6 | 4 | Pattern/realism injection + L1 validation |
| 7 | L3 + Auto-Fix (Isolated Stubs) | 7 | 4 | 3 | L3 validates patterns + fix strategy stubs |
| 8 | Integrate `LLMClient` + Error Loop | 6 | 2 | 4 | Integration verification of existing `LLMClient` capabilities + sandbox retry mechanics |
| **Totals** | | **73** | **40** | **33** | |

**Blocked backlog:** 34 distinct subtasks (24 BLOCKED + 10 SPEC_INCORRECT), plus 1 deferred NEEDS_CLARIFICATION (8.1.3).

**Parallelization opportunity:** Sprint 8 (Integrate `LLMClient` + Error Loop) depends only on Sprint 1 (exception types). It can be developed in parallel with Sprints 2–7 by a second engineer, merging at the pipeline orchestrator (which is blocked regardless).

**Existing infrastructure note (v3):** `pipeline/core/utils.py` provides `META_CATEGORIES`, `get_category_by_id()`, and `generate_unique_id()` — these are orchestration-level helpers already consumed by `agpds_pipeline.py`. No new sprint is needed for category routing or ID generation; they are referenced as pre-existing in orchestrator assumptions.

---

## Critical Path

```
Sprint 1 ──→ Sprint 2 ──→ Sprint 3 ──→ Sprint 4 ──→ Sprint 5 ──→ Sprint 6 ──→ Sprint 7
   │                                                                                 │
   └──────────────────→ Sprint 8 (parallel) ─────────────────────────────────────────┘
                                                                                     │
                                                                              [BLOCKED WALL]
                                                                                     │
                                                                    Resolve Blockers 1–6
                                                                                     │
                                                                              Sprint 9+: Unblocked
                                                                              subtasks integrated
```

After Sprint 8 completes, **all 73 implementable subtasks are done.** The remaining 34 subtasks (plus 1 deferred) await spec clarifications on 7 blockers. When blockers resolve, they can be integrated in roughly this order:

1. **Blocker 1 resolved** → Sprint 9: Complete metadata emitter + all SPEC_INCORRECT validator checks + deferred 8.1.3 orchestrator (10 subtasks + 1 deferred)
2. **Blocker 2 resolved** → Sprint 10: Formula DSL parser + structural measure engine + L2 residual checks + complete full DAG with formula edges (4 subtasks + DAG update)
3. **Blocker 3 resolved** → Sprint 11: Full distribution dispatch + KS tests + `iter_predictor_cells` (7 subtasks)
4. **Blocker 4 resolved** → Sprint 12: Remaining 4 pattern types across SDK + engine + L3 (9 subtasks)
5. **Blockers 5+6 resolved** → Sprint 13: Auto-fix retry loop (integrate 9.2.x stubs) + pipeline orchestrator + typed scenario injection formalization (4 subtasks; basic JSON injection path already exists). 实施参照 `audit/5_agpds_pipeline_runner_redesign.md` 迁移步骤 Step 1–4。
6. **Blocker 7 resolved** → fold into any sprint: censoring injection (1 subtask)

---

## Patch Log (v4 — Orchestrator Cross-Ref)

| Finding ID | Change Type | Description |
|---|---|---|
| D.sprint4_ordering | SCOPED | Sprint 4: Scoped 3.1.2 (topological sort) to pre-formula-edge DAG only. Added scope note explaining that formula-derived edges (edge type 5) are unavailable until Blocker 2 resolves. Updated 3.1.2 readiness to NEEDS_CLAR. Updated exit gate to reference pre-formula DAG and edge types 1–4. Updated Sprint Summary deliverable to "pre-formula DAG construction." |
| D.gate_sprint5 | MODIFIED | Sprint 5: Renamed deliverable from "correctly-typed DataFrames" to "skeleton-only DataFrames." Added scope note about skeleton-only scope and dtype policy as implementation choice. Removed dtype assertions (`category`, `datetime64[ns]`, `float64`) from exit gate; replaced with "Result is a valid `pd.DataFrame`." Updated 4.1.1, 4.1.2, 4.5.1 readiness from SPEC_READY to NEEDS_CLAR. to match alignment map v2. |
| D.sprint6_metadata_dep | MODIFIED | Sprint 6: Removed 8.1.3 (`validate(df, meta)` orchestrator) from subtask list — depends on unresolved B2/C6 interactions. Added deferral note. Reduced subtask count from 11 to 10, SPEC_READY from 7 to 6. Moved 8.1.3 to new "Deferred" section in Blocked Backlog. |
| D.sprint7 + E.propagation_B2_B3 | MODIFIED | Sprint 7: Marked 9.2.1–9.2.3 as "isolated stubs" in both subtask descriptions and deliverable. Added dependency note about B2/B3 blocking integration-level testing. Updated Blocker 5 description to note 9.2.x stubs await integration. Fixed header subtask count from (8) to (7) to match actual row count. |
| D.gate_sprint7 | MODIFIED | Sprint 7 exit gate: Removed claims about `reshuffle_pair` producing p-value > 0.05, `widen_variance`/`amplify_magnitude` persisting across retries, and downstream validation improvement. Replaced with stub-level unit test assertions (input→output on mock data) and explicit caveat that integration behavior is deferred. |
| D.gate_sprint2 | MODIFIED | Sprint 2 exit gate: Split into "Spec-backed assertions" (directly traceable to spec text with § references) and "Assumption-backed assertions" (proceeding under documented assumption). |
| D.gate_sprint8 | MODIFIED | Sprint 8 exit gate: Split into "Spec-conformance tests" (traceable to §2.5 and §2.7) and "Robustness helpers" (implementation choices like fence extraction). Removed 10.2.1 from SPEC_READY; updated to NEEDS_CLAR. Removed 7.1.1 from SPEC_READY; updated to NEEDS_CLAR. |
| E.numerical | CORRECTED | Blocked backlog count: Changed from "37 subtasks (25 BLOCKED + 11 SPEC_INCORRECT + 1 counted in both†)" to "34 distinct subtasks (24 BLOCKED + 10 SPEC_INCORRECT)." Updated Sprint Summary totals from 74→73 subtasks (reflecting 8.1.3 deferral). Corrected Sprint 3 SR from 8→7, NC from 4→5 (1.6.3 downgraded). Corrected Sprint 4 SR from 6→3, NC from 3→6 (1.7.4, 1.8.2, 1.8.3, 3.1.2 readiness changes). Corrected Sprint 5 SR from 8→4, NC from 2→6 (4.1.1, 4.1.2, 4.5.1 readiness changes). Corrected Sprint 8 SR from 4→2, NC from 2→4 (10.2.1, 7.1.1 readiness changes). Updated overall totals to 40 SR + 33 NC = 73. Updated post-sprint-8 text from "74 implementable" to "73 implementable" and "37 subtasks" to "34 subtasks (plus 1 deferred)." Updated Sprint 9 count to include deferred 8.1.3. |
| F.sprint8_reframe | MODIFIED (v3) | Sprint 8 theme reframed from "LLM Prompt Integration + Error Feedback Loop" to "Integrate Existing `LLMClient` Capabilities + Sandbox Error Feedback Loop." Added infrastructure note clarifying that code fence stripping and provider adaptation are pre-existing in `LLMClient`. Subtask 10.2.1 description reframed to "integration verification / contract test." Subtask 7.1.1 note clarified: LLM plumbing delegated to `LLMClient`. Exit gate adds `LLMClient` integration verification section. Sprint Summary theme updated. No readiness category changes; subtask counts unchanged. |
| F.blocker6_soften | MODIFIED (v3) | Blocker 6 resolution text softened: blocker applies to "typed interface completeness and stable orchestration," not basic injection capability. Added current-state note about existing `json.dumps(scenario)` path and `ScenarioContextualizer.validate_output()` de facto contract. |
| F.blocker_composite | ANNOTATED (v3) | Blocker Composite note softened: D1 component blocks typed-contract completeness, not basic scenario injection. |
| F.sprint13_soften | ANNOTATED (v3) | Post-blocker Sprint 13 description: added note that basic JSON injection path already exists. |
| F.utils_infra | ADDED (v3) | Existing infrastructure note added to Sprint Summary section: `utils.py` category helpers and ID generation are pre-existing orchestration-level capabilities; no new sprint needed. |
| F.statistics_verified | VERIFIED (v3) | All readiness counts verified unchanged. No readiness category changes in v3 — only description and context updates. Alignment map totals (108 = 41 SR + 33 NC + 24 BL + 10 SI) and sprint plan totals (73 scheduled + 34 blocked + 1 deferred) remain correct. |
| G.blocker6_xref | ANNOTATED (v4) | Blocker 6 resolution 增加交叉引用至 `audit/5_agpds_pipeline_runner_redesign.md` 的 `ScenarioContext` / `result_models.py` 设计。 |
| G.blocker_composite_xref | ANNOTATED (v4) | Blocker Composite 增加 orchestrator 架构引用至 `audit/5`（`AGPDSPipeline` 职责边界、`GenerationResult`）。 |
| G.sprint13_xref | ANNOTATED (v4) | Sprint 13 增加迁移步骤引用：参照 `audit/5` Step 1–4。 |
| G.sprint8_phase2svc | ANNOTATED (v4) | Sprint 8 infrastructure note 增加 `Phase2Service` forward-reference（参见 `audit/5`）。 |
| G.statistics_verified | VERIFIED (v4) | 无 readiness 变更，统计数字不变。所有改动仅为交叉引用注释。 |
