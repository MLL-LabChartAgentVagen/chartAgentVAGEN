# Stage 3: Implementation Readiness Audit

**System:** AGPDS Phase 2 — Agentic Data Simulator (SDK-Driven)
**Audit Mode:** Adversarial — classify every item as SPEC_READY or NEEDS_CLAR
**Criterion:** Two independent engineers must produce functionally equivalent implementations from the spec alone.

---

## Executive Summary

| Module | Total Items | SPEC_READY | NEEDS_CLAR | Readiness % | Top Blocker |
|---|---|---|---|---|---|
| **M3: LLM Orchestration** | 11 | 5 | 6 | 45% | Sandbox execution semantics (isolation, timeout, state reset) |
| **M1: SDK Surface** | 23 | 12 | 11 | 52% | `mixture` distribution `param_model` schema (unimplementable family) |
| **M2: Generation Engine** | 16 | 8 | 8 | 50% | Formula evaluation mechanism for structural measures |
| **M4: Schema Metadata** | 9 | 6 | 3 | 67% | Lossy projection — metadata omits fields M5 demonstrably needs |
| **M5: Validation Engine** | 21 | 13 | 8 | 62% | M5's actual data source — `schema_metadata` alone or declaration store access |
| **TOTAL** | **80** | **44** | **36** | **55%** | **Enrich `schema_metadata` (P0 — blocks M4 + M5 simultaneously)** |

**Assessment:** The core pipeline (declare → generate → validate) is implementable for the common case demonstrated by the one-shot example. Three P0 blockers must be resolved before implementation begins: (1) the M4/M5 metadata completeness gap, (2) the structural-measure formula evaluator, and (3) the auto-fix mutation semantics in Loop B. Resolving these three enables a functional end-to-end prototype. Remaining items can be stubbed in v1.

### Cross-Module Blockers (Priority-Ordered)

| Priority | Item | Modules Affected | Impact |
|---|---|---|---|
| **P0** | Enrich `schema_metadata` beyond §2.6 example to include all fields M5 needs | M4, M5 | Blocks entire validation engine |
| **P0** | Formula evaluation mechanism for structural measures | M1, M2 | Blocks structural measure generation |
| **P0** | Auto-fix mutation semantics (what gets mutated, declaration store vs. override dict) | M2, M5 | Blocks Loop B implementation |
| **P1** | `mixture` distribution `param_model` schema | M1, M2, M5 | Blocks one of eight distribution families |
| **P1** | Four under-specified pattern types (params + validation) | M1, M2, M5 | Blocks 4 of 6 pattern types |
| **P1** | Sandbox semantics and non-SDK error handling | M3 | Blocks robust retry loop |
| **P2** | Realism injection semantics and validation interaction | M2, M5 | Blocks `set_realism` feature |
| **P2** | Multi-column `on` in group dependency | M1, M2 | Blocks multi-predicate dependencies |
| **P2** | `scale` parameter, `censoring` parameter | M1 | Undocumented API surface |
| **P3** | Negative distribution parameters, per-parent weight coverage, pattern overlap composition | M1, M2 | Edge case robustness |

---

## Module: LLM Orchestration (M3)

### SPEC_READY Items

**1. System prompt template structure**
- What: Role preamble, SDK whitelist, hard constraints, soft guidelines, one-shot example, scenario slot — complete prompt template.
- Evidence: §2.5 provides the complete prompt verbatim, including all nine hard constraints enumerated as binary rules and a full runnable one-shot example.
- Estimated scope: **M**

**2. Hard constraint enumeration (HC1–HC9)**
- What: Nine binary pass/fail rules governing the generated script.
- Evidence: §2.5 lists all nine with unambiguous pass/fail semantics. Each maps to a validatable property of the generated script.
- Estimated scope: **S**

**3. Retry protocol structure**
- What: Append code+traceback, re-prompt, max 3 retries, terminal skip.
- Evidence: §2.7 specifies the six-step pipeline explicitly. The conversation is append-only; the re-prompt text is quoted ("Adjust parameters to resolve the error"); the retry budget is `max_retries=3`; terminal action is "log and skip."
- Estimated scope: **M**

**4. Conversation accumulation model**
- What: Multi-turn, system prompt frozen, user/assistant turns appended per retry.
- Evidence: §2.7 deep-dive §3.2 reconstructs the exact message sequence: `messages[0]` = system prompt, then pairs of assistant (script) + user (code+traceback) per failure. Up to 8 messages at max retries.
- Estimated scope: **S**

**5. Three named exception types consumed from M1**
- What: `CyclicDependencyError`, `UndefinedEffectError`, `NonRootDependencyError` with structured messages.
- Evidence: §2.7 names these with example messages. Sufficient to implement the catch-and-relay logic.
- Estimated scope: **S**

### NEEDS_CLAR Items

**1. Sandbox execution semantics (isolation level, timeout, state reset between retries)**
- Why it blocks: Two engineers could choose `exec()` in-process vs. subprocess vs. container. Without a timeout spec, a malformed script can hang the pipeline. Without explicit state-reset, a partially-populated `FactTableSimulator` from a failed attempt could corrupt the next retry.
- Spec reference: §2.7 step 2 ("Sandbox executes") — no further detail.
- Suggested resolution: Each retry instantiates a fresh `FactTableSimulator` inside a new `exec()` scope with a configurable timeout (default 30s). Document as a TODO.

**2. Handling of non-SDK exceptions (SyntaxError, NameError, TypeError from LLM-generated code)**
- Why it blocks: §2.7 only discusses typed SDK exceptions. A `SyntaxError` in the generated script would not produce a structured SDK error message, yet it is a realistic failure mode. Engineers would diverge on whether to catch all exceptions or only SDK subtypes.
- Spec reference: §2.7 step 4 — only SDK exception classes named.
- Suggested resolution: Catch all `Exception` subclasses during sandbox execution; relay the full traceback regardless of exception type. SDK exceptions get their structured message; others get the raw traceback.

**3. Multiple simultaneous SDK errors (only first surfaces per execution)**
- Why it blocks: Standard Python exception propagation surfaces one error per run. With 3 retries and potentially 4+ independent errors, the budget is systematically insufficient. Engineers must decide whether to implement multi-error collection in M1 or accept the one-at-a-time limitation.
- Spec reference: §2.7 deep-dive §2.7.5 edge case.
- Suggested resolution: Accept one-at-a-time as the default. Document that M1 could optionally collect multiple validation errors into a single compound exception as a future enhancement.

**4. Context window exhaustion strategy**
- Why it blocks: 3 retries accumulate ~4 full scripts + 3 tracebacks on top of a long system prompt with a one-shot example. No truncation or summarization strategy is specified. Engineers would diverge on whether to truncate older failed attempts.
- Spec reference: §2.7 deep-dive §2.7.5.
- Suggested resolution: Keep full history for 3 retries (manageable for most models). Add a token-budget check before each retry; if exceeded, summarize prior failures into a compact error list.

**5. `build_fact_table` function signature as a hard requirement**
- Why it blocks: §2.7's retry protocol and §2.9's `generate_with_validation(build_fn, ...)` both assume the function is named `build_fact_table` with a `seed` parameter, but §2.5's hard constraints do not list this. The LLM could name it differently. Engineers would diverge on whether to enforce the name via parsing or treat it as implicit.
- Spec reference: §2.5 HC6 says "pure, valid Python returning sim.generate()" but does not mandate function name/signature. Deep-dive §2.5.4 flags this as implicit.
- Suggested resolution: Add an explicit hard constraint: "The script must define `def build_fact_table(seed=42):` and return `sim.generate()`." Parse the script AST to verify.

**6. Interaction between Loop A terminal failure and the upstream scenario orchestrator**
- Why it blocks: "Log and skip" implies an outer loop that tolerates per-scenario failures. This outer loop is not specified in Phase 2. Engineers need to know the skip signal's type/format and who receives it.
- Spec reference: §2.7 R2.
- Suggested resolution: Return `None` (or a typed `SkipResult` object) from the M3 entry point. The Phase 1→Phase 2 orchestrator checks for this and continues to the next scenario.

---

## Module: SDK Surface (M1)

### SPEC_READY Items

**1. `FactTableSimulator(target_rows, seed)` constructor**
- What: Two-argument constructor creating empty internal registries.
- Evidence: §2.1 defines the two arguments and their pass-through semantics.
- Estimated scope: **S**

**2. `add_category(name, values, weights, group, parent=None)` — full signature and validation rules**
- What: Categorical column registration with auto-normalization, empty-values rejection, parent validation, flat-list broadcast vs. per-parent dict branching.
- Evidence: §2.1.1 specifies all validation rules. The one-shot example demonstrates both forms.
- Estimated scope: **M**

**3. `add_temporal(name, start, end, freq, derive=[])` — signature and derived feature extraction**
- What: Temporal column with four supported derived features (`day_of_week`, `month`, `quarter`, `is_weekend`).
- Evidence: §2.1.1 specifies derived columns enter the column registry as real columns available as predictors.
- Estimated scope: **S**

**4. `add_measure(name, family, param_model)` — stochastic root measure with intercept+effects param_model**
- What: Stochastic root measure registration. Both "simple" (constant) and "full" (with effects) forms.
- Evidence: §2.1.1 + §2.3 fully specify the `θⱼ = β₀ + Σₘ βₘ(Xₘ)` parameterization. Supported families listed.
- Estimated scope: **M**

**5. `add_measure_structural(name, formula, effects={}, noise={})` — structural measure with DAG edge extraction**
- What: Structural measure registration with formula symbol resolution and DAG edge creation.
- Evidence: §2.1.1 specifies that every symbol in `formula` must resolve. DAG edges extracted from formula references. Example provided.
- Estimated scope: **M**

**6. `declare_orthogonal(group_a, group_b, rationale)` — orthogonal pair registration**
- What: Group-level independence assertion with propagation to all cross-group column pairs.
- Evidence: §2.1.2 specifies the propagation rule and downstream effects. Straightforward list append.
- Estimated scope: **S**

**7. `add_group_dependency(child_root, on, conditional_weights)` — single-column `on` case**
- What: Conditional distribution for a group root column given another root column.
- Evidence: §2.1.2 provides a complete example with `on=["severity"]`. Root-only constraint and DAG requirement are explicit.
- Estimated scope: **M**

**8. `inject_pattern(type, target, col, params)` — for `outlier_entity` and `trend_break` types**
- What: Pattern registration for the two fully-specified pattern types.
- Evidence: §2.1.2 + §2.9 L3 provide both declaration examples and validation logic. Parameter schemas are clear.
- Estimated scope: **S** per type

**9. Declaration-time validation — DAG acyclicity, parent existence, root-only constraint, symbol resolution**
- What: Four declaration-time validators with corresponding typed exceptions.
- Evidence: §2.1.1 and §2.1.2 enumerate these checks. §2.7 names the exception types.
- Estimated scope: **M**

**10. Dimension group abstraction (`dimension_groups` dict structure)**
- What: `{columns, hierarchy}` per group, root-first hierarchy ordering, temporal as special group.
- Evidence: §2.2 specifies the structure. Example shows all cases including temporal group.
- Estimated scope: **S**

**11. Measure DAG topological sort**
- What: `measure_dag_order` as topological sort of edges from structural measure formula references.
- Evidence: §2.3 formalizes the DAG constraint and specifies the sort.
- Estimated scope: **S**

**12. `set_realism(missing_rate, dirty_rate, censoring=None)` — parameter registration (storage only)**
- What: Accept and store realism parameters in the declaration store.
- Evidence: §2.1.2 defines the method signature. Storage is straightforward even if execution semantics need clarification.
- Estimated scope: **S**

### NEEDS_CLAR Items

**1. `mixture` distribution `param_model` schema**
- Why it blocks: Listed as a supported family in §2.1.1 but zero examples of its parameter structure. Engineers cannot implement the sampling logic without knowing how component distributions, mixing weights, and per-component parameters are specified.
- Spec reference: §2.1.1 supported distributions list; deep-dive §2.1.1-5.
- Suggested resolution: Define `param_model` for mixture as `{"components": [{"family": "gaussian", "weight": 0.6, "params": {"mu": {...}, "sigma": {...}}}, ...]}`. Mark as TODO until spec author confirms.

**2. `scale` parameter on `add_measure`**
- Why it blocks: Present in the method signature in §2.5's whitelist but never defined, never used in the one-shot example, and never referenced elsewhere. Two engineers would make incompatible guesses.
- Spec reference: §2.1.1 signature; deep-dive §2.1.1-4.
- Suggested resolution: Accept the parameter in the signature, store it in the column registry, but treat it as a no-op until the spec author clarifies. Log a warning if non-None.

**3. Per-parent conditional weight dict — behavior when a parent value is missing**
- Why it blocks: §2.1.1 shows `...` in the per-parent dict. If a parent value is missing from the dict, engineers diverge between raising an error and falling back to flat-list weights.
- Spec reference: §2.1.1 `add_category` per-parent form; deep-dive §2.1.1-5.
- Suggested resolution: Raise `IncompleteWeightError` at declaration time if the dict doesn't cover every parent value.

**4. Orthogonal + dependency contradiction on the same group pair**
- Why it blocks: Logically contradictory declarations with no specified precedence. Engineers diverge on reject-at-declaration vs. last-write-wins.
- Spec reference: §2.1.2 deep-dive §2.1.2-5; §2.5 HC4 + HC8 interaction.
- Suggested resolution: Raise `ConflictingRelationError` at declaration time.

**5. Multi-column `on` in `add_group_dependency`**
- Why it blocks: The `on` parameter is typed as a list. With multiple columns, the `conditional_weights` dict structure for joint conditioning is never shown.
- Spec reference: §2.1.2; deep-dive §2.1.2-5.
- Suggested resolution: Use tuple keys for multi-column: `{("Mild", "East"): {...}, ...}`. Alternatively, restrict to single-column for v1.

**6. Pattern parameter schemas for `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`**
- Why it blocks: Four pattern types listed in the enum with no declaration examples, incomplete or absent `params` schemas, and (for `convergence`/`seasonal_anomaly`) no L3 validation logic.
- Spec reference: §2.1.2 pattern types list; §2.9 L3.
- Suggested resolution: Implement `outlier_entity` and `trend_break` fully; implement `ranking_reversal` and `dominance_shift` based on §2.9's validation code; stub `convergence` and `seasonal_anomaly` with `NotImplementedError`.

**7. `censoring` parameter semantics in `set_realism`**
- Why it blocks: Defaults to `None`, never elaborated. Engineers cannot implement censoring logic.
- Spec reference: §2.1.2; deep-dive §2.1.2-4.
- Suggested resolution: Accept `censoring` as opaque dict. Implement `missing_rate` and `dirty_rate` only. Stub censoring.

**8. Column name uniqueness enforcement**
- Why it blocks: Implied but no validation rule stated. Engineers diverge between silent overwrite and raising.
- Spec reference: §2.1.1 deep-dive §2.1.1-4 implicit constraints.
- Suggested resolution: Raise `DuplicateColumnError` at declaration time.

**9. Effects referencing columns not yet declared (validation timing)**
- Why it blocks: If a measure's effects reference a categorical column declared later within Step 1, should it fail immediately?
- Spec reference: §2.1.1 deep-dive §3.3 implicit ordering #5.
- Suggested resolution: Validate effect predictor existence at declaration time. Raise `UndefinedPredictorError` if the referenced predictor doesn't exist yet.

**10. Negative distribution parameters from additive effects**
- Why it blocks: `sigma = 0.35 + (-0.5)` yields negative σ, invalid for many distributions. No clamping or validation specified.
- Spec reference: §2.3 deep-dive §2.3-5.
- Suggested resolution: Clamp parameters to valid ranges at generation time (e.g., `sigma = max(sigma, 1e-6)`). Log a warning.

**11. Step 1 / Step 2 ordering enforcement mechanism and `target_rows` validation**
- Why it blocks: §2.5 HC3 mandates ordering but the SDK API has no state-machine to enforce it. Also, `target_rows = 0` or negative is unaddressed.
- Spec reference: §2.5 HC3; deep-dive §3.3 #8; deep-dive §2.1-5.
- Suggested resolution: Add an internal `_phase` flag that transitions on first relationship call. Reject column declarations after transition. Raise `ValueError` in constructor if `target_rows < 1`.

---

## Module: Generation Engine (M2)

### SPEC_READY Items

**1. Four-stage pipeline structure (α → β → γ → δ)**
- What: Skeleton → measures → patterns → realism, with fixed ordering and mathematical composition notation.
- Evidence: §2.8 defines the stages with pseudocode. Stage ordering is explicit.
- Estimated scope: **L**

**2. Stage α — skeleton generation**
- What: Root categoricals from marginal weights, children from conditional weights, temporal uniform sampling, temporal derivation.
- Evidence: §2.4 specifies the per-row algorithm (steps 1–7). §2.8 maps these to `_build_skeleton`.
- Estimated scope: **M**

**3. Stage β — stochastic measure sampling**
- What: `intercept + Σ effects` → distribution draw for all families except `mixture`.
- Evidence: §2.3 provides the mathematical form; §2.8 maps it to `_sample_stochastic`.
- Estimated scope: **M**

**4. Stage β — structural measure evaluation**
- What: Formula + effects + noise computation.
- Evidence: §2.1.1 + §2.3 + §2.8 specify the formula evaluation, effect resolution, and noise addition. Two concrete examples provided.
- Estimated scope: **M**

**5. Pre-flight DAG construction and topological sort**
- What: `_build_full_dag()` → `topological_sort()`. DAG edges from four sources.
- Evidence: §2.8 pseudocode. §2.4 enumerates the four edge sources.
- Estimated scope: **S**

**6. Single RNG stream for determinism**
- What: `rng = np.random.default_rng(self.seed)` passed to every stage.
- Evidence: §2.8 pseudocode. Determinism guarantee is explicit.
- Estimated scope: **S**

**7. Stage γ — pattern injection for `outlier_entity` and `trend_break`**
- What: Post-generation DataFrame-wide pattern application for the two fully-specified types.
- Evidence: §2.9 L3 validation defines expected outcomes, constraining the injection logic.
- Estimated scope: **M**

**8. Return type `Tuple[pd.DataFrame, dict]`**
- What: Master DataFrame + schema metadata dict.
- Evidence: §2.8 pseudocode: `return self._post_process(rows), self._build_schema_metadata()`.
- Estimated scope: **S**

### NEEDS_CLAR Items

**1. Formula evaluation mechanism for structural measures**
- Why it blocks: `_eval_structural` must evaluate formula strings. The spec never states whether this uses Python `eval()`, a restricted parser, or AST-based evaluation. Security implications and allowed operators differ.
- Spec reference: §2.8 deep-dive §2.A.5; §2.1.1 formula semantics.
- Suggested resolution: Use a restricted expression evaluator allowing only arithmetic operators (`+`, `-`, `*`, `/`, `**`), numeric literals, and variable names resolved from the row context and effects dict. No function calls, no attribute access.

**2. `_post_process(rows)` behavior**
- Why it blocks: The spec mentions `τ_post` but never defines what it does. Engineers diverge on dtype enforcement, value clipping, rounding, index assignment.
- Spec reference: §2.8 pseudocode; deep-dive §2.A.4 C8.
- Suggested resolution: Convert to `pd.DataFrame`, assign RangeIndex, cast temporal columns to `datetime64`. No value clipping or rounding.

**3. Pattern composition when targets overlap**
- Why it blocks: Two patterns targeting overlapping rows and the same column have no defined priority or composition rule.
- Spec reference: §2.8 deep-dive §3.3 O3.
- Suggested resolution: Apply patterns in declaration order. Document that overlapping patterns compose by sequential mutation.

**4. Pattern injection on structural measures breaking formula consistency**
- Why it blocks: Injecting an outlier on a structural measure overwrites the formula-derived value. M5's L2 residual check would then fail.
- Spec reference: Deep-dive M2 §2.A.5 and M1 §2.1.2-5.
- Suggested resolution: L2 residual checks should exclude rows matching any pattern's `target` filter for the same `col`.

**5. Realism injection semantics**
- Why it blocks: Which columns get missing values? Can a cell be both missing and dirty? What does "dirty" mean concretely?
- Spec reference: §2.8 stage δ; §2.1.2 `set_realism`.
- Suggested resolution: `missing_rate` applies uniformly (replace with NaN). `dirty_rate` applies to categoricals only (random swap to another valid value). Missing takes precedence over dirty. Censoring is stubbed.

**6. Structural measure with `noise={}` (empty dict) default behavior**
- Why it blocks: Is this zero noise (deterministic) or an error? Affects both generation and L2 validation (divide by zero on `noise_sigma`).
- Spec reference: §2.1.1 defaults; deep-dive M4 §2.5 edge case.
- Suggested resolution: `noise={}` means zero noise. Skip noise draw. L2 residual check uses `residuals.std() < 1e-6` instead of ratio test.

**7. Realism interaction with pattern signals**
- Why it blocks: Realism (stage δ) can inject NaN into pattern-targeted cells, destroying the pattern signal and causing L3 failures.
- Spec reference: Deep-dive M2 §2.A.5.
- Suggested resolution: Realism injection skips cells modified by pattern injection (mark them during stage γ). Or: validate pre-realism, apply realism post-validation.

**8. `_build_schema_metadata()` location — M2 method vs. M4 module**
- Why it blocks: §2.8 shows metadata built inside M2's `generate()`. Stage1 shows M4 as a separate module. Engineers diverge on code organization.
- Spec reference: Deep-dive M2 §3.4; stage1 module map.
- Suggested resolution: Implement M4 as a standalone function `build_schema_metadata(declaration_store) → dict`. `generate()` calls this function. Preserves boundaries while acknowledging co-location.

---

## Module: Schema Metadata (M4)

### SPEC_READY Items

**1. Top-level `schema_metadata` dict structure — 7 keys**
- What: `dimension_groups`, `orthogonal_groups`, `group_dependencies`, `columns`, `measure_dag_order`, `patterns`, `total_rows`.
- Evidence: §2.6 provides a complete JSON example with all seven keys.
- Estimated scope: **M**

**2. `dimension_groups` structure**
- What: `{group_name: {columns: [...], hierarchy: [...]}}` including temporal group distinction.
- Evidence: §2.6 example shows all four groups.
- Estimated scope: **S**

**3. `orthogonal_groups` — 1:1 mapping from declarations**
- What: List of `{group_a, group_b, rationale}`.
- Evidence: §2.6 example. Verbatim passthrough.
- Estimated scope: **S**

**4. `columns` array — type-discriminated descriptors**
- What: Descriptors with `type`, `group`, `parent`, `cardinality`, `family`, `measure_type`, `depends_on`, `derived`.
- Evidence: §2.6 example shows all column types.
- Estimated scope: **S**

**5. `measure_dag_order` — flat topological sort list**
- What: Direct passthrough from M1's computed topological sort.
- Evidence: §2.6 example.
- Estimated scope: **S**

**6. `total_rows` — scalar passthrough**
- What: From constructor argument.
- Evidence: §2.6 example.
- Estimated scope: **S**

### NEEDS_CLAR Items

**1. Lossy projection — `schema_metadata` omits fields M5 demonstrably needs**
- Why it blocks: M5's L1 checks need `values` and `weights`. L2 needs full `param_model`, `formula`, `noise_sigma`, and `conditional_weights`. None appear in the §2.6 example. Two engineers would produce fundamentally different metadata dicts. This is the highest-priority clarification in the entire audit.
- Spec reference: §2.6 example vs. §2.9 validation code; deep-dive M4 MISMATCH 1, 2, 3.
- Suggested resolution: **Enrich `schema_metadata` beyond the example.** Add to categorical columns: `values`, `weights`. Add to stochastic measures: full `param_model`. Add to structural measures: `formula`, `effects`, `noise`. Add to `group_dependencies`: `conditional_weights`. Add to `patterns`: all `params`. The §2.6 example is illustrative, not exhaustive.

**2. Whether M4 needs the generated DataFrame as input**
- Why it blocks: Stage1 lists "Declaration store + generated DataFrame" as input. But no metadata field requires row data. If M4 doesn't need the DataFrame, it can run parallel with M2.
- Spec reference: Stage1 module map; deep-dive M4 §3.4 ordering #1.
- Suggested resolution: M4 does not need the DataFrame. Build from declaration store only. Allow parallel execution with M2.

**3. Metadata internal consistency validation**
- Why it blocks: No self-validation of the metadata dict is specified. Bugs in M4's builder could create inconsistent cross-references.
- Spec reference: Deep-dive M4 §2.4 implicit constraints.
- Suggested resolution: Add `_assert_metadata_consistency(meta)` verifying cross-references before returning.

---

## Module: Validation Engine (M5)

### SPEC_READY Items

**1. L1 — Row count check**
- What: `abs(len(df) - target) / target < 0.1`.
- Evidence: §2.9 L1 pseudocode provides the exact formula.
- Estimated scope: **S**

**2. L1 — Categorical cardinality check**
- What: `nunique` == declared `cardinality`.
- Evidence: §2.9 L1 pseudocode.
- Estimated scope: **S**

**3. L1 — Root marginal weight check**
- What: Max deviation < 0.10 from declared weights.
- Evidence: §2.9 L1 pseudocode. (Contingent on `values`/`weights` being in metadata — see M4 NEEDS_CLAR #1.)
- Estimated scope: **S**

**4. L1 — Measure finiteness check**
- What: `notna().all()` and `isfinite().all()`.
- Evidence: §2.9 L1 pseudocode.
- Estimated scope: **S**

**5. L1 — Orthogonal independence (chi-squared)**
- What: `chi2_contingency` on root pairs, p > 0.05.
- Evidence: §2.9 L1 pseudocode with exact call and threshold.
- Estimated scope: **S**

**6. L1 — Measure DAG acyclicity (double-check)**
- What: Redundant acyclicity verification.
- Evidence: §2.9 L1 pseudocode.
- Estimated scope: **S**

**7. L2 — Stochastic measure KS test per predictor cell**
- What: `kstest` with expected params per categorical context cell.
- Evidence: §2.9 L2 pseudocode. (Contingent on full `param_model` in metadata.)
- Estimated scope: **M**

**8. L2 — Structural measure residual mean and std checks**
- What: `abs(residuals.mean()) < residuals.std() * 0.1` and `abs(residuals.std() - noise_sigma) / noise_sigma < 0.2`.
- Evidence: §2.9 L2 pseudocode with exact thresholds. (Contingent on `formula`/`noise_sigma` in metadata.)
- Estimated scope: **M**

**9. L2 — Group dependency conditional transition check**
- What: Max deviation < 0.10 from declared conditional weights.
- Evidence: §2.9 L2 pseudocode. (Contingent on `conditional_weights` in metadata.)
- Estimated scope: **S**

**10. L3 — Outlier entity validation**
- What: z-score ≥ 2.0.
- Evidence: §2.9 L3 pseudocode.
- Estimated scope: **S**

**11. L3 — Trend break validation**
- What: Magnitude > 15% relative change.
- Evidence: §2.9 L3 pseudocode.
- Estimated scope: **S**

**12. L3 — Ranking reversal validation**
- What: Negative rank correlation between two metrics.
- Evidence: §2.9 L3 pseudocode: `means[m1].rank().corr(means[m2].rank()) < 0`.
- Estimated scope: **S**

**13. `generate_with_validation` wrapper — Loop B structure**
- What: Retry loop with `seed=42+attempt`, max 3 retries, soft failure.
- Evidence: §2.9 pseudocode.
- Estimated scope: **S**

### NEEDS_CLAR Items

**1. M5's actual data source — `schema_metadata` alone or declaration store access**
- Why it blocks: §2.9 pseudocode references `col["values"]`, `col["weights"]`, `col["formula"]`, `col["noise_sigma"]`, `spec.iter_predictor_cells()`, and `dep["conditional_weights"]` — none of which appear in the §2.6 metadata example. Two engineers would build fundamentally different validators.
- Spec reference: Stage1 module map; §2.9 pseudocode; §2.6 example.
- Suggested resolution: Enrich `schema_metadata` to include all referenced fields. M5 should only consume the metadata dict.

**2. L2 structural residual check — divide by zero when `noise_sigma = 0`**
- Why it blocks: Formula `abs(residuals.std() - noise_sigma) / noise_sigma` is undefined when `noise_sigma = 0`.
- Spec reference: §2.9 L2; deep-dive M4 §2.5 edge case.
- Suggested resolution: If `noise_sigma` is 0 or absent, check `residuals.std() < 1e-6` instead.

**3. L2 KS-test predictor cell enumeration (`spec.iter_predictor_cells()`)**
- Why it blocks: Never defined how this iterator is constructed. For measures with multiple predictors, the Cartesian product of predictor values could be large. Handling of small-sample cells is unspecified.
- Spec reference: §2.9 L2 pseudocode.
- Suggested resolution: Iterate over Cartesian product of predictor columns in the measure's `effects`. Skip cells with < 5 rows. Cap tested cells at 100.

**4. L3 — `dominance_shift` validation logic**
- Why it blocks: §2.9 delegates to `self._verify_dominance_change(df, p, meta)` — opaque, no implementation shown.
- Spec reference: §2.9 L3; §2.1.2 pattern types.
- Suggested resolution: Define as rank change of a named entity across a temporal split. Params: `{entity_filter, col, before_rank, after_rank, split_point}`.

**5. L3 — Missing validation for `convergence` and `seasonal_anomaly`**
- Why it blocks: Listed in enum, completely absent from §2.9 validation logic.
- Spec reference: §2.9 L3.
- Suggested resolution: Stub with `Check(..., passed=True, detail="not implemented")`. TODO for full implementation.

**6. Auto-fix strategy implementations (`widen_variance`, `amplify_magnitude`, `reshuffle_pair`)**
- Why it blocks: Dispatch table names three strategies with no implementation. Target parameters and mutation mechanics are unspecified.
- Spec reference: §2.9 auto-fix pseudocode.
- Suggested resolution: `widen_variance`: multiply `sigma` intercept by factor. `amplify_magnitude`: multiply pattern's `z_score`/`magnitude` by factor. `reshuffle_pair`: re-shuffle one root column independently. Mark as TODO for spec review.

**7. Auto-fix mutation target — declaration store vs. override dict vs. seed-only**
- Why it blocks: `strategy(check)` suggests state mutation, but `build_fn(seed=42+attempt)` re-executes the full script, overwriting any mutations. Two engineers produce incompatible implementations.
- Spec reference: §2.9 auto-fix loop; stage1 Loop B.
- Suggested resolution: Auto-fix strategies mutate a **parameter override dict** passed to `generate()`. The `build_fn` in Loop B should be `sim.generate()` (with overrides), not the full `build_fact_table()`.

**8. Validation ordering relative to realism injection**
- Why it blocks: Should validation run pre- or post-realism? L1/L2 test properties realism intentionally degrades. L3 patterns can be corrupted by NaN injection.
- Spec reference: §2.9 says "after the engine produces a Master Table (§2.8)" — which includes realism.
- Suggested resolution: Validate pre-realism. Apply realism only after validation passes.
