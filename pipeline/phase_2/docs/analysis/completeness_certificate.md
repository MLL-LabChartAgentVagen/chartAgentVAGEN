# AGPDS Phase 2 — Completeness Certificate

> **STATUS (2026-05-07):** This certificate is the 2026-04-07 snapshot. Of the 6 STUBBED items reported below, 5 of the 6 (IS-1..IS-4 plus the ranking_reversal-validation gap) have shipped between 2026-04-22 and 2026-05-07; the remaining one (IS-5 `scale` kwarg) was intentionally not restored. See [`../remaining_gaps.md`](../remaining_gaps.md) for current state, [`../stub_implementation/`](../stub_implementation/) for per-stub records, and [`../POST_STUB_AUDIT_FINDINGS.md`](../POST_STUB_AUDIT_FINDINGS.md) for the post-implementation audit. Inline ✅ RESOLVED markers below.

## Audit Date: 2026-04-07
## Audited Against: stage3_readiness_audit.md (80 items)

---

## Summary

| Status | SPEC_READY (of 44) | NEEDS_CLAR (of 36) | Total (of 80) |
|---|---|---|---|
| DONE | 43 | 31 | 74 |
| STUBBED | 1 | 5 | 6 |
| MISSING | 0 | 0 | 0 |
| REGRESSED | 0 | 0 | 0 |

**92.5% fully implemented. 7.5% intentionally stubbed (5 per decision, 1 unexpected).**

> ✅ As of 2026-05-07: 5 of the 6 STUBBED items above are now DONE (IS-1..IS-4, plus ranking_reversal validation). The 1 remaining (IS-5 `scale` kwarg) was intentionally not restored — see `../remaining_gaps.md §4.2`.

---

## System Readiness

### Direct SDK Path (no LLM)

**YES** — A developer can write declarations manually, call `generate()`, and get a validated master table.

Evidence:
- All 23 M1 SDK methods are implemented: `add_category`, `add_temporal`, `add_measure`, `add_measure_structural`, `declare_orthogonal`, `add_group_dependency`, `inject_pattern`, `set_realism` (simulator.py, columns.py, relationships.py)
- Declaration-time validation is complete: DAG acyclicity, parent existence, root-only constraints, symbol resolution, column uniqueness, weight coverage, orthogonal/dependency conflict detection (validation.py, dag.py)
- Generation engine produces full DataFrames through all four stages: skeleton → measures → patterns → realism (generator.py, skeleton.py, measures.py, patterns.py, realism.py)
- Schema metadata builder emits enriched metadata with all fields M5 needs (metadata/builder.py)
- Validation engine runs L1 (6 checks), L2 (3 checks), L3 (2 fully implemented + 4 stubbed) (validation/*.py)
- Loop B (`generate_with_validation`) retries with seed offset and ParameterOverrides (autofix.py)
- One limitation: `mixture` distribution raises `NotImplementedError` at generation time. All other 7 families work.

### Agentic Path (with LLM)

**YES** — The pipeline can accept a scenario context, prompt an LLM, execute the generated script, and produce a validated master table.

Evidence:
- System prompt template is verbatim from spec §2.5 with HC1–HC9 (prompt.py)
- LLM client supports OpenAI, Gemini, Azure providers; `generate_code()` strips fences (llm_client.py)
- LLM client integrated into retry loop via `_make_generate_fn()` wrapper (retry_loop.py)
- Sandbox executes scripts in daemon thread with timeout and fresh namespace per attempt (sandbox.py)
- `build_fact_table` signature enforced via AST validation + runtime check (code_validator.py, sandbox.py)
- Retry protocol: max 3 retries, conversation accumulation, error feedback formatting (retry_loop.py)
- Terminal failure returns `SkipResult` sentinel (types.py, retry_loop.py)
- Pipeline wires Loop A (M3→M1) and Loop B (M5→M2) end-to-end (pipeline.py)

---

## Per-Module Detail

### M3: LLM Orchestration (11 items)

| # | Item | Stage3 Status | Impl Status | Evidence |
|---|---|---|---|---|
| SR-1 | System prompt template structure | SPEC_READY | DONE | prompt.py:35-201 — Full template: role preamble, SDK whitelist, HC1–HC9, soft guidelines, one-shot example, scenario slot |
| SR-2 | Hard constraint enumeration (HC1–HC9) | SPEC_READY | DONE | prompt.py:71-83 — All 9 constraints listed verbatim |
| SR-3 | Retry protocol structure | SPEC_READY | DONE | retry_loop.py:562-738 — Append code+traceback, re-prompt, max_retries=3, terminal skip via SkipResult |
| SR-4 | Conversation accumulation model | SPEC_READY | DONE | retry_loop.py:650-738 — Multi-turn history list, system prompt frozen, user feedback appended per retry |
| SR-5 | Three named exception types from M1 | SPEC_READY | DONE | exceptions.py:52-127 — CyclicDependencyError, UndefinedEffectError, NonRootDependencyError with structured messages |
| NC-1 | Sandbox execution semantics | NEEDS_CLAR | DONE | sandbox.py:191-235 — exec() in daemon thread, configurable timeout, fresh namespace per attempt via _build_sandbox_namespace() |
| NC-2 | Non-SDK exception handling | NEEDS_CLAR | DONE | sandbox.py:230-234 — Broad `except Exception` captures all exception types uniformly |
| NC-3 | Multiple simultaneous SDK errors | NEEDS_CLAR | STUBBED | Decision P1-5: Accept one-at-a-time. Single exception per sandbox execution. TODO noted |
| NC-4 | Context window exhaustion strategy | NEEDS_CLAR | STUBBED | Decision P1-5: Accept full history for 3 retries. TODO at retry_loop.py:656-660 for token-budget check |
| NC-5 | `build_fact_table` signature enforcement | NEEDS_CLAR | DONE | code_validator.py:178-189 — AST visitor checks function name. sandbox.py:220-225 — Runtime namespace check |
| NC-6 | Loop A terminal failure signal | NEEDS_CLAR | DONE | types.py:372-388 — SkipResult dataclass. retry_loop.py:734-738 — Returned on exhaustion |

**LLM Client Integration:** DONE — retry_loop.py:25-55 wraps `LLMClient.generate_code()` via `_make_generate_fn()`. `orchestrate()` accepts `llm_client` as required parameter and creates the generate function.

### M1: SDK Surface (23 items)

| # | Item | Stage3 Status | Impl Status | Evidence |
|---|---|---|---|---|
| SR-1 | `FactTableSimulator(target_rows, seed)` constructor | SPEC_READY | DONE | simulator.py:38-49 — Two-arg constructor, type/value validation, empty registries |
| SR-2 | `add_category(name, values, weights, group, parent)` | SPEC_READY | DONE | columns.py:38-122 — Uniqueness, empty rejection, parent validation, flat vs per-parent dict, auto-normalization |
| SR-3 | `add_temporal(name, start, end, freq, derive)` | SPEC_READY | DONE | columns.py:124-211 — ISO-8601 parsing, freq validation, derive whitelist, temporal group registration |
| SR-4 | `add_measure(name, family, param_model)` | SPEC_READY | DONE | columns.py:214-256 — Family validation, param_model validation, scale warning |
| SR-5 | `add_measure_structural(name, formula, effects, noise)` | SPEC_READY | DONE | columns.py:258-327 — Symbol extraction, effects validation, DAG acyclicity check, edge registration |
| SR-6 | `declare_orthogonal(group_a, group_b, rationale)` | SPEC_READY | DONE | relationships.py:43-97 — Group existence validation, dependency conflict check, duplicate prevention |
| SR-7 | `add_group_dependency(child_root, on, conditional_weights)` | SPEC_READY | DONE | relationships.py:99-212 — Single-column restriction, root validation, orthogonal conflict, weight normalization |
| SR-8 | `inject_pattern(type, target, col, params)` | SPEC_READY | DONE | relationships.py:214-273 — Type validation, target column validation, required params per PATTERN_REQUIRED_PARAMS |
| SR-9 | Declaration-time validation (4 validators) | SPEC_READY | DONE | validation.py + dag.py — DAG acyclicity (dag.py:379-452), parent existence (validation.py:78-106), root-only (relationships.py:132-143), symbol resolution (validation.py:467-548) |
| SR-10 | Dimension group abstraction | SPEC_READY | DONE | types.py:28-81 + groups.py — DimensionGroup dataclass, root-first hierarchy, temporal special case |
| SR-11 | Measure DAG topological sort | SPEC_READY | DONE | dag.py:105-156 — Kahn's algorithm with min-heap for deterministic tie-breaking |
| SR-12 | `set_realism(missing_rate, dirty_rate, censoring)` | SPEC_READY | DONE | relationships.py:275-314 — Rate validation [0,1], censoring stored, realism config dict returned |
| NC-1 | `mixture` distribution param_model | NEEDS_CLAR | STUBBED | validation.py:30-33 "mixture" in SUPPORTED_FAMILIES. measures.py:298-303 raises NotImplementedError at generation time. Per decision P1-1. |
| NC-2 | `scale` parameter on add_measure | NEEDS_CLAR | DONE | columns.py:242-248 — Accepted, stored in metadata, warning logged if non-None. Per decision P2-5. |
| NC-3 | Per-parent weight dict coverage | NEEDS_CLAR | DONE | validation.py:199-213 — Raises ValueError for missing parent value keys. Per decision P3-2. |
| NC-4 | Orthogonal + dependency contradiction | NEEDS_CLAR | DONE | relationships.py:321-358 — Bidirectional conflict detection, ValueError raised. Per decision P3-3. |
| NC-5 | Multi-column `on` restriction | NEEDS_CLAR | DONE | relationships.py:122-130 — `len(on) != 1` raises NotImplementedError. Per decision P2-4. |
| NC-6 | Pattern param schemas (4 types) | NEEDS_CLAR | DONE | relationships.py:32-40 — PATTERN_REQUIRED_PARAMS: ranking_reversal={metrics,entity_col}, dominance_shift={entity_filter,col,split_point}. Per decision P1-2. |
| NC-7 | `censoring` parameter semantics | NEEDS_CLAR | DONE | relationships.py:303-307 stored. realism.py raises NotImplementedError when non-None. Per decision P2-6. |
| NC-8 | Column name uniqueness | NEEDS_CLAR | DONE | validation.py:57-72 — validate_column_name raises DuplicateColumnError. Per decision P3-4. |
| NC-9 | Effects referencing undeclared columns | NEEDS_CLAR | DONE | validation.py:402-461 — validate_effects_in_param raises UndefinedEffectError. Per decision P3-5. |
| NC-10 | Negative distribution parameters | NEEDS_CLAR | DONE | measures.py:391-404 — Clamping at generation time: sigma/scale → max(val, 1e-6), warning logged. Per decision P3-1. |
| NC-11 | Step 1/Step 2 ordering enforcement | NEEDS_CLAR | DONE | simulator.py:58-71 — _phase flag, _ensure_declaring_phase raises InvalidParameterError after transition. Per decision P3-6. |

### M2: Generation Engine (16 items)

| # | Item | Stage3 Status | Impl Status | Evidence |
|---|---|---|---|---|
| SR-1 | Four-stage pipeline (α→β→γ→δ) | SPEC_READY | DONE | generator.py:27-133 — Fixed ordering: skeleton(31-85), measures(87-90), patterns(95-98), realism(100-103) |
| SR-2 | Stage α — skeleton generation | SPEC_READY | DONE | skeleton.py:31-102 — Root/dependent/child samplers with topo order, marginal and conditional weights |
| SR-3 | Stage β — stochastic measure sampling | SPEC_READY | DONE | measures.py:266-336 — Intercept+effects computation, dispatch to 7 families (gaussian, lognormal, gamma, beta, uniform, poisson, exponential) |
| SR-4 | Stage β — structural measure evaluation | SPEC_READY | DONE | measures.py:179-259 — Effects resolution, context building, formula eval via _safe_eval_formula, optional noise |
| SR-5 | Pre-flight DAG construction + topo sort | SPEC_READY | DONE | generator.py:77-80 — _dag.build_full_dag() + _dag.topological_sort() before skeleton phase |
| SR-6 | Single RNG stream for determinism | SPEC_READY | DONE | generator.py:74 — `rng = np.random.default_rng(seed)` passed to all stages |
| SR-7 | Stage γ — pattern injection (outlier, trend_break) | SPEC_READY | DONE | patterns.py:29-86 — inject_patterns iterates declaration order, dispatches to inject_outlier_entity/inject_trend_break |
| SR-8 | Return type Tuple[DataFrame, dict] | SPEC_READY | DONE | generator.py:38,133 — Returns (df, metadata) |
| NC-1 | Formula evaluation mechanism | NEEDS_CLAR | DONE | measures.py:39-105 — Restricted AST walker: Expression, BinOp, UnaryOp, Constant, Name. Rejects Call/Attribute/etc. Per decision P0-2. |
| NC-2 | `_post_process(rows)` behavior | NEEDS_CLAR | DONE | postprocess.py:19-82 — DataFrame with RangeIndex, datetime64 cast, int64/bool for derived, object for categorical. Per decision P3-9. |
| NC-3 | Pattern composition on overlap | NEEDS_CLAR | DONE | patterns.py:39-41 — Documentation comment: sequential mutation in declaration order. Per decision P3-7. |
| NC-4 | Pattern on structural → L2 exclusion | NEEDS_CLAR | DONE | statistical.py:356-366, 236-246 — Pattern mask exclusion implemented in both check_structural_residuals and check_stochastic_ks. Per decision P3-8. |
| NC-5 | Realism injection semantics | NEEDS_CLAR | DONE | realism.py:25-65 — missing_rate→NaN first, dirty_rate→categorical swap second, censoring→NotImplementedError. Per decision P2-1. |
| NC-6 | Structural noise={} default | NEEDS_CLAR | DONE | measures.py:206,254-257 — Empty dict is falsy, no noise added. Per decision P3-10. |
| NC-7 | Realism interaction with patterns | NEEDS_CLAR | DONE | generator.py:95-103 — Patterns (γ) before realism (δ). Validation pre-realism makes cell-marking unnecessary. Per decision P2-2. |
| NC-8 | _build_schema_metadata() location | NEEDS_CLAR | DONE | generator.py:106 imports from phase_2.metadata.builder. Standalone M4 module. Per decision P3-11. |

### M4: Schema Metadata (9 items)

| # | Item | Stage3 Status | Impl Status | Evidence |
|---|---|---|---|---|
| SR-1 | Top-level dict — 7 keys | SPEC_READY | DONE | builder.py:57-111 — dimension_groups, orthogonal_groups, group_dependencies, columns, measure_dag_order, patterns, total_rows |
| SR-2 | `dimension_groups` structure | SPEC_READY | DONE | builder.py:60-63 — DimensionGroup.to_metadata() produces {columns, hierarchy} |
| SR-3 | `orthogonal_groups` 1:1 mapping | SPEC_READY | DONE | builder.py:66-68 — OrthogonalPair.to_metadata() produces {group_a, group_b, rationale} |
| SR-4 | `columns` array — type-discriminated | SPEC_READY | DONE | builder.py:78-82,114-175 — categorical (values, weights, cardinality), temporal (start, end, freq, derive), stochastic (family, param_model), structural (formula, effects, noise) |
| SR-5 | `measure_dag_order` flat list | SPEC_READY | DONE | builder.py:84-85 — Defensive copy: list(measure_dag_order) |
| SR-6 | `total_rows` scalar | SPEC_READY | DONE | builder.py:101-102 — Direct assignment |
| NC-1 | Lossy projection enrichment | NEEDS_CLAR | DONE | builder.py:114-175 — Enriched: categorical values/weights (139-140), param_model deep-copied (165), formula/effects/noise (167-171), conditional_weights via GroupDependency.to_metadata() (73), pattern params (94). Per decision P0-1. |
| NC-2 | M4 DataFrame dependency | NEEDS_CLAR | DONE | builder.py:23-31 — Signature takes no DataFrame. Builds from declaration store data only. Per decision P3-12. |
| NC-3 | Metadata consistency validation | NEEDS_CLAR | DONE | builder.py:104-105,194-252 — _assert_metadata_consistency checks 4 cross-references with warning-level logging. Per decision P3-13. |

### M5: Validation Engine (21 items)

| # | Item | Stage3 Status | Impl Status | Evidence |
|---|---|---|---|---|
| SR-1 | L1 — Row count check | SPEC_READY | DONE | structural.py:23-49 — deviation < 0.1 |
| SR-2 | L1 — Categorical cardinality | SPEC_READY | DONE | structural.py:52-111 — nunique == declared |
| SR-3 | L1 — Root marginal weight check | SPEC_READY | DONE | structural.py:213-266 — max deviation < 0.10 per root categorical |
| SR-4 | L1 — Measure finiteness | SPEC_READY | DONE | structural.py:269-315 — na_count == 0 and inf_count == 0 |
| SR-5 | L1 — Orthogonal independence (chi2) | SPEC_READY | DONE | structural.py:114-178 — chi2_contingency, p > 0.05 on root pairs |
| SR-6 | L1 — Measure DAG acyclicity | SPEC_READY | DONE | structural.py:181-210 — Verifies no duplicate nodes in measure_dag_order |
| SR-7 | L2 — Stochastic KS test | SPEC_READY | DONE | statistical.py:206-314 — _iter_predictor_cells with Cartesian product, min 5 rows, max 100 cells, kstest p > 0.05 |
| SR-8 | L2 — Structural residual check | SPEC_READY | DONE | statistical.py:317-422 — noise_sigma=0 guard (residual_std < 1e-6), else ratio < 0.2 |
| SR-9 | L2 — Group dependency transition | SPEC_READY | DONE | statistical.py:425-489 — Conditional distribution deviation < 0.10 |
| SR-10 | L3 — Outlier entity validation | SPEC_READY | DONE | pattern_checks.py:23-69 — z-score >= 2.0 |
| SR-11 | L3 — Trend break validation | SPEC_READY | DONE | pattern_checks.py:84-164 — Magnitude ratio > 0.15 |
| SR-12 | L3 — Ranking reversal validation | SPEC_READY | ✅ DONE (was STUBBED 2026-04-07) | pattern_checks.py — `check_ranking_reversal` shipped (Spearman ρ < 0); paired injector `inject_ranking_reversal` shipped (DS-2). |
| SR-13 | Loop B `generate_with_validation` | SPEC_READY | DONE | autofix.py:214-289 — seed=base_seed+attempt, max 3, ParameterOverrides, validate pre-realism |
| NC-1 | M5 data source (metadata only) | NEEDS_CLAR | DONE | validator.py:40-46 — Constructor takes `meta: dict[str, Any]` only, no store. Per decision P3-14. |
| NC-2 | L2 residual divide-by-zero guard | NEEDS_CLAR | DONE | statistical.py:402-420 — noise_sigma==0 → residual_std < 1e-6. Per decision P3-15. |
| NC-3 | L2 KS predictor cell enumeration | NEEDS_CLAR | DONE | statistical.py:58-127 — _iter_predictor_cells: Cartesian product, min_rows=5, max_cells=100. Per decision P3-16. |
| NC-4 | L3 — `dominance_shift` validation | NEEDS_CLAR | ✅ DONE (was STUBBED 2026-04-07) | pattern_checks.py — `check_dominance_shift` shipped (IS-2 + DS-2 injector). See `../stub_implementation/IS-2_dominance_shift.md`. |
| NC-5 | L3 — `convergence` + `seasonal_anomaly` | NEEDS_CLAR | ✅ DONE (was STUBBED 2026-04-07) | pattern_checks.py — `check_convergence` (IS-3) and `check_seasonal_anomaly` (IS-4) shipped along with paired injectors (DS-2). |
| NC-6 | Auto-fix strategies (3 types) | NEEDS_CLAR | DONE | autofix.py:76-207 — widen_variance, amplify_magnitude, reshuffle_pair all implemented with ParameterOverrides accumulation. Per decision P0-3. |
| NC-7 | Auto-fix mutation target | NEEDS_CLAR | DONE | autofix.py:19,255,261,280 — Strategies return ParameterOverrides dict, passed to build_fn. Per decision P0-3. |
| NC-8 | Validation ordering (pre-realism) | NEEDS_CLAR | DONE | autofix.py:263,283-287 — Validation loop runs with realism_config=None; realism applied post-validation. Per decision P2-3. |

---

## Cross-Module Contracts

| Contract | Status | Evidence |
|---|---|---|
| DeclarationStore.freeze() enforced before generate() | **NOT YET** | types.py:377-383 — DeclarationStore exists with freeze() method, but FactTableSimulator uses its own OrderedDict registries directly. Integration deferred per TODO. |
| M4 builds from store only (no DataFrame) | VERIFIED | builder.py:23-31 — No DataFrame parameter in signature |
| M5 consumes schema_metadata only (no store) | VERIFIED | validator.py:40-46 — Constructor takes only `meta: dict` |
| Loop A exceptions raised by M1, caught by M3 | VERIFIED | sandbox.py:230-234 — `except Exception` captures all SDK errors. retry_loop.py:127-149 — SkipResult on failure |
| Loop B seed offset implemented | VERIFIED | autofix.py:260 — `seed = base_seed + attempt`. Line 285 — Separate realism RNG |
| Single RNG stream through all stages | VERIFIED | generator.py:74 — Single `default_rng(seed)` passed to skeleton, measures, patterns, realism |
| ParameterOverrides consumed by run_pipeline() | VERIFIED | generator.py:36 accepts `overrides`. pipeline.py:116-147 merges pattern overrides. measures.py consumes at draw time |
| Validation pre-realism, realism post-validation | VERIFIED | pipeline.py:200 — `realism_config=None` during Loop B. autofix.py:283-287 — Realism applied only post-validation |

---

## Items Requiring Attention

### 1. Ranking Reversal Validation — ✅ RESOLVED 2026-04-22 → 2026-05-07

- **Item:** M5 SPEC_READY #12 — L3 ranking reversal
- **Resolution:** `check_ranking_reversal` shipped per the SPEC_READY pseudocode (Spearman ρ < 0). Paired injector `inject_ranking_reversal` also shipped as part of DS-2.
- Original concern (preserved for record): "This item has clear pseudocode in the spec (`means[m1].rank().corr(means[m2].rank()) < 0`) and is classified SPEC_READY, yet it is stubbed with `passed=True`. No entry in `blocker_resolutions.md` authorizes this stub."

### 2. DeclarationStore.freeze() Integration — Deferred

- **Item:** Cross-module contract #1
- **Location:** types.py:377-383
- **Issue:** `DeclarationStore` class exists with `freeze()` method, but `FactTableSimulator` uses its own `OrderedDict` registries and does not integrate `DeclarationStore`. The freeze-before-generate contract is not enforced at runtime.
- **Impact:** Medium — Callers can theoretically mutate declarations after `generate()` starts. In practice, the current code flow makes this unlikely.
- **Recommended action:** Migrate `FactTableSimulator` to use `DeclarationStore` internally and call `freeze()` at the start of `generate()`.

### 3. ColumnDescriptor Type — Not Yet Used

- **Item:** types.py expected type
- **Location:** types.py:371-372
- **Issue:** The spec lists `ColumnDescriptor` as a shared type, but the current implementation uses plain `dict[str, Any]` for column metadata throughout. A TODO note says: "Will be progressively migrated to typed ColumnDescriptor list in future batches."
- **Impact:** Low — dictionaries work correctly; typing is a code quality concern, not a functional gap.
- **Recommended action:** Deferred to future migration.

---

## Conclusion

The AGPDS Phase 2 implementation is **substantially complete**: 74 of 80 items (92.5%) are fully implemented, and the remaining 6 are intentionally stubbed per design decisions (5) or have an unexpectedly stubbed but low-impact gap (1).

**Direct SDK path: READY.** All declaration, generation, and validation capabilities work end-to-end. The 5 intentional stubs (`mixture` sampling, `dominance_shift`/`convergence`/`seasonal_anomaly` validation, multi-error aggregation, context window truncation) are correctly placed with clear TODO markers and do not block the primary use case.

**Agentic path: READY.** LLM client integration is complete. The full pipeline (prompt → LLM → sandbox → validate → retry/skip) is wired and functional. The `SkipResult` sentinel correctly propagates terminal failures.

**One unexpected gap** requires attention: ranking reversal validation (M5 SR-12) is stubbed despite having complete pseudocode in the spec. This is a ~15-line implementation that should be completed.

**One architectural debt** is documented: `DeclarationStore.freeze()` is defined but not integrated into `FactTableSimulator`. This should be addressed in a future migration phase to enforce immutability at runtime.
