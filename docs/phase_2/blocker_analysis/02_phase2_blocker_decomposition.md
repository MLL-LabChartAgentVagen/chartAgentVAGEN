# Phase 2 Blocker Decomposition

**Generated from:** `phase_2.md` (spec), `1_phase2_implementation_task_hierarchy.md` (task hierarchy v2), `2_phase2_gap_analysis.md` (gap analysis v2), `3_phase2_implementation_alignment_map.md` (alignment map v4), `4_phase2_sprint_plan.md` (sprint plan v4), `01_phase2_current_state_map.md` (Stage 1 output)

**Method:** Root-cause blocker decomposition. Each blocker is traced from high-level cause down to concrete implementation consequences, grounded in source document evidence. Where the Stage 1 current-state map conflicts with source documents, the source documents take precedence and corrections are noted.

---

## 1. Executive View

Phase 2's blocked work divides into 35 subtasks (24 BLOCKED + 10 SPEC_INCORRECT + 1 deferred) out of 108 total — roughly one-third of the system. The blockers are **not** scattered across unrelated features. They cluster tightly around **three root problems** that cascade through the architecture:

**The dominant blocker type is missing shared contracts.** The spec defines subsystems (engine, metadata, validator, auto-fix) that must agree on data formats, but never formally defines those formats. The metadata schema in §2.6 is specified by a single JSON example that omits fields the §2.9 validator pseudocode reads. The formula DSL is used in three modules but has no grammar. The distribution parameter schema is used in the SDK, engine, and validator but has no reference table. Each of these is a missing contract between a producer and one or more consumers.

**The second blocker type is unspecified behavioral triples.** Four of six pattern types and four of nine auto-fix failure modes exist as names without co-designed (params, algorithm, validation) specifications. These are not missing documentation — they are missing design decisions that require simultaneous specification of three tightly coupled components.

**The third blocker type is contradictory composed behavior.** The auto-fix pseudocode applies parameter fixes then regenerates from scratch, discarding the fixes. The L2 validator tests post-injection distributions against pre-injection parameters. The L1 finiteness check rejects NaN values that the realism phase deliberately introduces. These are not ambiguities — they are internal contradictions in the spec pseudocode.

**Structural observation:** These three root problems are layered. The missing contracts (type 1) are foundational — they block both the behavioral triples (type 2, which need parameter schemas to specify) and the composed behavior (type 3, which needs a metadata contract to validate against). The contradictory composed behavior (type 3) also depends on type 2, because the L2/pattern oscillation cannot be resolved until pattern injection semantics are defined. This layering means that resolving the ~5 contract-level decisions unblocks roughly 20 subtasks immediately and enables resolution of the remaining ~15.

**Correction to Stage 1:** The Stage 1 current-state map (§4 "Cross-area observations") correctly identifies the dependency chain and the metadata schema as the highest-leverage blocker. However, it frames the blockers as seven parallel items. This decomposition shows they reduce to three root causes with a strict dependency ordering between them, and that several "separate" blockers (A12 cross-group defaults, A13 target grammar, C6 L1/realism conflict) are downstream symptoms of the missing-contracts root cause, not independent blockers.

---

## 2. Major Blockers

### 2.1 Schema Metadata Contract is Undefined

#### A. Blocked capability

The metadata schema (§2.6) is the single shared data contract between the engine (producer), the three-layer validator (consumer), Phase 3 (consumer), and the auto-fix loop (consumer). Its current state — a single JSON example with no formal definition — makes 9+ subtasks unimplementable and produces `KeyError` at runtime for every validator check that references a field the metadata does not emit.

Affected subtasks: 5.1.3, 5.1.4, 5.1.6 (metadata emitter — SPEC_INCORRECT); 8.2.3, 8.2.4 (L1 — SPEC_INCORRECT); 8.3.3, 8.3.4, 8.3.6 (L2 — SPEC_INCORRECT); 8.4.2 (L3 — SPEC_INCORRECT). Indirectly: the entire auto-fix loop (9.3.1) and pipeline orchestrator (11.1.1, 11.1.2) cannot be wired without a functioning validator.

#### B. High-level cause

**Missing shared data contract.** The spec defines the metadata by a single example (§2.6 lines 446–478) rather than a formal schema. The example omits fields that the §2.9 validator pseudocode reads. This is not an incomplete spec — it is two sections of the same spec that contradict each other.

#### C. Exact ambiguity location

The ambiguity lives in the **metadata schema semantics**. Specifically, the §2.6 example is missing:

- `col["values"]` and `col["weights"]` for categorical root columns — read by L1 marginal check (§2.9 line 574–575)
- `col["formula"]` and `col["noise_sigma"]` for structural measures — read by L2 residual checks (§2.9 lines 626, 631)
- `dep["conditional_weights"]` for group dependencies — read by L2 conditional deviation check (§2.9 line 636)
- `col["param_model"]` for stochastic measures — needed by L2 KS test (§2.9 lines 615–616 via `_get_measure_spec`)
- `p["params"]` for patterns — needed by L3 checks that use `z_score`, `break_point`, `magnitude`
- No `schema_version` field — no forward compatibility mechanism
- No required/optional distinction — cannot validate the metadata itself
- No formal types — `cardinality` is int by inspection, `depends_on` is list[str] by inspection, but neither is stated

#### D. Downstream implementation decisions blocked

1. **Metadata builder field list.** The metadata emitter (Module 5) cannot emit the correct fields without knowing what the schema requires. The 3 SPEC_INCORRECT subtasks (5.1.3, 5.1.4, 5.1.6) need a definitive field list.
2. **Validator field access patterns.** Every validator check that reads metadata fields beyond the §2.6 example will `KeyError`. The L1 marginal check, all L2 checks, and the L3 pattern checks depend on fields that do not exist in the example.
3. **Phase 3 consumption contract.** Phase 3 (QA generation, chart extraction) consumes the metadata to reconstruct generation semantics. Without `param_model`, `formula`, or `effects`, it cannot formulate statistically grounded questions.
4. **Auto-fix loop wiring.** The auto-fix loop calls the validator, which depends on the metadata. If the metadata schema is wrong, validation results are meaningless, and auto-fix strategies cannot be correctly targeted.

#### E. Partial implementation still possible

The 4 non-contradictory metadata fields (`dimension_groups`, `orthogonal_groups`, `measure_dag_order`, `total_rows`) are already implemented in Sprint 5. The metadata builder skeleton and the validator framework (`Check`, `ValidationReport`) are implemented. The 4 L1 checks that don't depend on missing fields (row count, cardinality, orthogonal chi-squared, DAG acyclicity) work. The `_max_conditional_deviation` helper works in isolation.

#### F. Minimum decisions needed to unblock

One decision: **define the complete metadata schema formally.** This means specifying, for each metadata section, the exact field names, types, required/optional status, and structure. The gap analysis (finding C13) recommends a Python `TypedDict` or `@dataclass`; the alignment map recommends adding a `schema_version` field. Once defined, all 9 SPEC_INCORRECT subtasks unblock simultaneously.

#### G. Evidence

- §2.6 (spec lines 446–478): metadata example omits `values`, `weights`, `formula`, `noise_sigma`, `conditional_weights`, `param_model`, `params`
- §2.9 (spec lines 574–575, 626, 631, 636): validator reads those missing fields
- Gap analysis findings C3, C8, C9 (three independent reviewers converging), C13 (post-audit structural finding)
- Alignment map Blocker 1: counts 3 SPEC_INCORRECT + 6 downstream = 9+ subtasks
- Sprint plan Blocked Backlog: all 9 subtasks listed under Blocker 1

---

### 2.2 Formula DSL Grammar is Unspecified

#### A. Blocked capability

The `formula` parameter in `add_measure_structural()` is a string containing an arithmetic expression (e.g., `"wait_minutes * 12 + severity_surcharge"`). This string must be parsed and evaluated in three separate modules: SDK validation (1.5.2), engine generation (4.2.5, 4.2.8), and L2 validation (8.3.5). No grammar exists for this language. The entire structural-measure pipeline — from declaration through generation to validation — is inoperable.

Affected subtasks: 1.5.2 (formula symbol resolution), 4.2.5 (structural formula evaluation), 4.2.8 (`eval_formula` safe evaluator), 8.3.5 (L2 residual computation). Additionally, DAG edge type 5 (formula-derived edges) cannot be added until formula variables can be parsed.

#### B. High-level cause

**Missing formal grammar for an expression language.** The spec shows formula examples in §2.1.1 and §2.3 but never defines the language: no operator whitelist, no precedence rules, no variable resolution order, no function whitelist. This is a missing abstraction — the formula string is used as if it were a well-defined DSL, but no DSL definition exists.

#### C. Exact ambiguity location

The ambiguity is in the **DSL / formula model**. The specific unknowns are:

- **Operator whitelist:** Is `**` (power) allowed? `/` (division)? `%`? Unary negation? The examples show `*`, `+`, `-` but never state which others are valid.
- **Function calls:** Can the formula contain `log()`, `abs()`, `max()`? The spec shows only arithmetic operators.
- **Precedence:** Standard mathematical? Python-like? (These differ for `**` and unary operators.)
- **Variable resolution order:** If a measure name and an effect name collide, which is resolved first?
- **Literal numbers:** The examples contain `12`, `0.04`, `9` — but the spec never states that numeric literals are allowed.
- **Whitespace:** Is `"a*12"` equivalent to `"a * 12"`?

#### D. Downstream implementation decisions blocked

1. **Parser design.** Cannot build a tokenizer or AST parser without knowing the token set. A regex-based approach, an AST-walker, and a restricted `eval()` sandbox all require different designs depending on the operator/function set.
2. **DAG edge extraction.** Formula symbol resolution (1.5.2) must parse the formula to discover which measure names are referenced, creating DAG edges. Without a parser, no formula-derived edges exist, and the full DAG (including edge type 5) cannot be constructed.
3. **Safe evaluator security boundary.** The `eval_formula` function (4.2.8) must reject arbitrary code while allowing legitimate formulas. The whitelist of allowed constructs defines the security boundary. No whitelist → no security boundary.
4. **L2 residual validation.** The L2 structural check (8.3.5) reuses `eval_formula` to compute predicted values. Same blocked parser.

#### E. Partial implementation still possible

The `add_measure_structural()` signature, effects validation, noise spec storage, and cycle detection are all implementable without the formula grammar (and are in Sprints 3–4). The formula string itself can be stored as-is. DAG construction for edge types 1–4 works (Sprint 4 scope note documents this). The structural noise sampling (4.2.7) and effect materialization (4.2.6) are formula-independent and implementable.

#### F. Minimum decisions needed to unblock

Define an **operator whitelist + precedence table + variable resolution rule**. The gap analysis (finding A3) recommends a minimal set: `+`, `-`, `*`, `/`, unary `-`, numeric literals, parentheses. If functions are desired, enumerate them. One page of specification unblocks the entire structural-measure pipeline end-to-end across three modules.

#### G. Evidence

- §2.1.1 (spec lines 72–81): formula examples with no grammar
- §2.3 (spec lines 178–182): structural measure description referencing formula
- Gap analysis finding A3 (CRITICAL): explicit enumeration of missing grammar elements
- Alignment map Blocker 2: 4 BLOCKED subtasks across 3 modules
- Sprint plan Sprint 4 scope note: DAG construction scoped to edge types 1–4 because formula edges blocked

---

### 2.3 Distribution Family Parameter Schema is Missing

#### A. Blocked capability

The SDK, engine, and validator all need to know the required parameter keys, valid domains, and scipy mappings for each distribution family. The spec provides parameter examples only for `gaussian` and `lognormal` (`mu`, `sigma`). For the remaining six families (`gamma`, `beta`, `uniform`, `poisson`, `exponential`, `mixture`), no parameter keys are specified. The `mixture` family has zero specification of any kind. This blocks the entire stochastic-measure pipeline.

Affected subtasks: 1.4.3 (param_model full validation), 1.4.4 (mixture sub-spec), 1.5.4 (noise per-family validation), 4.2.1 (stochastic parameter resolution), 4.2.2 (distribution dispatch table), 8.3.1 (L2 KS test), 8.3.2 (`iter_predictor_cells`).

#### B. High-level cause

**Missing parametric reference table.** The spec lists eight family names as strings (§2.1.1 line 94) but only demonstrates two. This is a missing reference table — a lookup from family name to (required keys, valid domains, scipy distribution name) that all three modules share.

#### C. Exact ambiguity location

The ambiguity is in the **SDK API surface** and the **metadata / schema semantics**, specifically:

- **Parameter keys per family:** `gamma` — `shape`/`rate`? `alpha`/`beta`? `k`/`theta`? Six families have no stated keys.
- **Parameter domains:** The intercept+effects model `θ = β₀ + Σβₘ(Xₘ)` can produce negative `sigma` values. No link function or domain clamping is specified (finding A5a).
- **Scipy name mapping:** The validator's KS test (§2.9 line 619) passes `col["family"]` to `scipy.stats.kstest`, but SDK names (`"gaussian"`) don't match scipy names (`"norm"`). No mapping table exists.
- **Mixture:** Entirely unspecified. The `param_model` intercept+effects schema cannot express component distributions, per-component parameters, and mixing weights. No CDF exists in scipy for a user-defined mixture, making the L2 KS test impossible (finding A1b).

#### D. Downstream implementation decisions blocked

1. **SDK validation logic.** The `add_measure()` method (1.4.3) cannot validate that `param_model` contains the correct keys for a given family.
2. **Engine sampling dispatch.** The engine (4.2.1, 4.2.2) must call the correct `np.random.default_rng()` method with the correct positional arguments per family. Without key→argument mapping, dispatch is impossible.
3. **L2 KS test parameterization.** The validator (8.3.1) must construct expected distribution parameters per predictor cell to pass to `scipy.stats.kstest`. Without knowing which parameters a family uses, it cannot construct the CDF.
4. **`iter_predictor_cells` algorithm.** The helper (8.3.2) must compute the cross-product of effect predictor values and resolve per-cell parameters. This depends on knowing which parameter keys exist and how effects compose.
5. **Mixture: binary decision.** If `mixture` is kept, a fundamentally different `param_model` schema is needed. If deferred, the family list should be reduced to 7.

#### E. Partial implementation still possible

For `gaussian` and `lognormal`, the parameter schema is fully exemplified (`mu`, `sigma`). The constant-parameter form of `add_measure()` (1.4.2) works for these two families (Sprint 3). The `scale` parameter is stored with a warning (assumption A2). The measure DAG root registration (1.4.5) is family-independent and works. All effects-structure validation (1.5.3) is family-independent and works.

#### F. Minimum decisions needed to unblock

**Create a distribution reference table:** for each of the 8 (or 7, if mixture is deferred) families, specify (a) required `param_model` keys, (b) valid domains per key, (c) scipy distribution name, (d) mapping from SDK keys to scipy positional args. **Decide on `mixture`:** fully specify a component-list schema, or defer to a future version. One reference table unblocks 7 subtasks across 3 modules.

#### G. Evidence

- §2.1.1 (spec line 94): eight family names listed, only `gaussian`/`lognormal` demonstrated
- Gap analysis findings A1 (CRITICAL: mixture zero-spec), A5 (CRITICAL: missing param keys), A5a (domain validation), A1b (mixture has no scipy CDF)
- Alignment map Blocker 3: 7 BLOCKED subtasks
- Sprint plan Blocker 3 resolution text

---

### 2.4 Pattern Type Behavioral Triples are Unspecified

#### A. Blocked capability

Four of six pattern types (`ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`) exist in the spec as names only. For each, three tightly coupled components are missing: the params schema (what the LLM declares), the injection algorithm (how the engine transforms the DataFrame), and the L3 validation check (how the validator detects the pattern). These three must be co-designed because the injection must produce a statistical signature that the validation can detect, and the params must control both.

Affected subtasks: 1.8.4 (param validation for 4 types), 4.3.3–4.3.6 (injection for 4 types), 8.4.4–8.4.7 (L3 validation for 4 types, including helpers). Total: 9 BLOCKED subtasks.

#### B. High-level cause

**Missing co-designed behavioral specification.** Each pattern type is not one missing spec item but three interdependent ones. The params schema constrains the injection algorithm, which constrains the validation check. Designing any one of the three without the others produces an unvalidatable or undetectable pattern. This is a design decision, not a documentation gap.

#### C. Exact ambiguity location

The ambiguity spans three layers simultaneously:

- **SDK API:** What keys must `params` contain for each type? (finding A8)
- **Engine / execution behavior:** What transformation does each injection apply to the DataFrame? (finding B6)
- **Validator behavior:** What statistical test detects each pattern? (finding C1 for convergence/seasonal_anomaly, C10 for dominance_shift)
- For `dominance_shift` specifically: the L3 validator delegates to `_verify_dominance_change()` (§2.9 line 674), a function that is never defined anywhere in the spec (finding C10).

#### D. Downstream implementation decisions blocked

1. **SDK param validation.** Cannot validate `params` dict for four types without knowing required keys. Currently these are stored as opaque dicts (task 1.8.4 notes this workaround).
2. **Engine injection functions.** Cannot implement `_inject_patterns` for four types without knowing the transformation algorithm.
3. **L3 validation checks.** Cannot implement checks for four types without knowing the detectable statistical signature.
4. **Auto-fix strategy coverage.** The `amplify_magnitude` fix strategy is designed for outlier/trend patterns. Whether it applies to the four unspecified types is unknown (finding C4).
5. **LLM prompt guidance.** The §2.5 prompt soft guidelines cannot advise the LLM on using these pattern types without specifying what params to pass.

#### E. Partial implementation still possible

`outlier_entity` and `trend_break` are fully specified — both have params schemas (in the §2.1.2 examples), injection semantics (inferable from L3 validation code), and L3 validation pseudocode. Their SDK validation (1.8.1–1.8.3, 1.8.5), injection (4.3.1, 4.3.2), and L3 checks (8.4.1, 8.4.3) are all implementable and scheduled in Sprints 4, 6, and 7. The pattern storage infrastructure, target expression handling, and column validation all work for all six types. The `inject_pattern` dispatch framework can be built with only two active branches and four stubs.

#### F. Minimum decisions needed to unblock

For each of the four types, define: **(a)** a `params` schema (required keys with types and domains), **(b)** an injection transformation (deterministic given `(pattern_spec, df, rng)`), and **(c)** an L3 validation check (with a pass/fail threshold). These must be specified as co-designed triples, not independently. The gap analysis recommends worked examples for each type.

#### G. Evidence

- §2.1.2 (spec lines 127–129): six pattern type names; only two have examples
- §2.9 L3 (spec lines 647–676): validation pseudocode for outlier, ranking_reversal, trend_break, dominance_shift — but ranking_reversal hard-codes the first group (C11), dominance_shift delegates to an undefined function (C10), and convergence/seasonal_anomaly have no branch at all (C1)
- Gap analysis findings A8, B6, C1, C10 (three reviewers converging from different angles)
- Alignment map Blocker 4: 9 BLOCKED subtasks across 3 modules

---

### 2.5 Post-Processing Invariant Contract is Missing (L2/Pattern/Realism Contradiction)

#### A. Blocked capability

The §2.8 engine pipeline has four sequential phases: α (skeleton), β (measures), γ (pattern injection), δ (realism injection). The §2.9 validator runs on the final output. This creates two structural contradictions:

1. **L2 vs. Pattern Injection (B2):** L2 tests stochastic distributions against declared parameters. Pattern injection (γ) deliberately distorts distributions. L2 will fail for every pattern-targeted column.
2. **L1 vs. Realism (C6):** L1 asserts `notna().all()` for measures. Realism injection (δ) introduces NaN at `missing_rate`. L1 will always fail when realism is active.

Additionally, the auto-fix pseudocode contains an internal contradiction (B3, B7): fix strategies modify parameters (lines 695–698), but the next iteration calls `build_fn(seed=42+attempt)` (line 691), which re-executes the original LLM script from scratch, discarding all fixes.

Directly affected: 9.3.1 (SPEC_INCORRECT — the retry loop pseudocode). Indirectly degraded: 8.3.1 (L2 KS test), 9.2.1–9.2.3 (fix strategies can't be integration-tested), 4.3.1–4.3.2 (pattern injection interacts with L2), 11.1.1–11.1.2 (orchestrator composes broken loops).

#### B. High-level cause

**Missing execution-model contract for post-processing phases.** The spec defines four engine phases and a post-engine validator but never specifies which validation layers apply to which phase's output. Each phase transforms the data in ways that may violate previous invariants. Without a contract specifying "L2 runs on Phase β output; L3 runs on Phase γ output; L1 adjusts thresholds when Phase δ is active," the validation system is internally inconsistent.

The auto-fix contradiction is a separate but compounding problem: **missing mutation model.** The pseudocode applies fixes then discards them, which is not a design choice but a logical error in the pseudocode itself.

#### C. Exact ambiguity location

The ambiguity spans multiple layers:

- **Execution behavior (§2.8):** What is the invariant contract between engine phases? Which properties established in Phase β are preserved by Phases γ and δ?
- **Validator behavior (§2.9):** Does L2 run on pre-injection or post-injection data? Does L1 adjust for realism-introduced NaN?
- **Auto-fix mutation semantics (§2.9):** Do fix strategies mutate the simulator instance (persistent across retries), post-process the DataFrame (applied after each regeneration), or modify the SDK script source? The pseudocode implies none of these consistently.
- **Exception / retry semantics:** The §2.7/§2.9 loop composition is inferable (sequential, per §2.7 step 3) but never formalized. The total budget (3+3=6) and no-escalation rule are assumptions, not spec statements.

#### D. Downstream implementation decisions blocked

1. **Validator orchestrator design.** The `validate(df, meta)` orchestrator (8.1.3, deferred from Sprint 6) cannot be implemented without knowing whether to pass pre- or post-injection data to L2. This is not a code question but a semantic question.
2. **Auto-fix retry loop implementation.** The retry loop (9.3.1) cannot be implemented as-specified because the pseudocode is self-contradictory. An implementer must choose a mutation model that the spec does not provide.
3. **Fix strategy scope.** `widen_variance` (for KS failures) fights `amplify_magnitude` (for pattern failures) on the same column. Without knowing whether L2 excludes pattern-target rows, the strategy scope is undefined.
4. **Pipeline orchestrator.** The orchestrator (11.1.1) composes the two loops. If the inner loop (§2.9) is broken, the orchestrator is broken.

#### E. Partial implementation still possible

The individual fix strategies can be built and unit-tested as isolated stubs (Sprint 7 does this). The `match_strategy` glob dispatcher works. The validator framework, L1 checks (except finiteness), and L3 checks for outlier/trend work. The §2.7 execution-error loop is independent of this blocker and can be fully implemented. The sequential composition assumption (§2.7 then §2.9, not nested) is well-supported by §2.7 step 3 wording and can be coded.

#### F. Minimum decisions needed to unblock

Three decisions:

1. **Post-processing invariant contract:** Define which validation layers run on which phase output. The cleanest option (per gap analysis B2 recommendation): L2 runs on Phase β output (pre-injection), L3 runs on Phase γ output (post-injection), L1 adjusts finiteness thresholds for Phase δ (realism). This resolves B2, C6, and the L2/L3 oscillation simultaneously.
2. **Auto-fix mutation model:** Define the fix target. The only consistent option (per gap analysis B3, B7): fix strategies mutate the `FactTableSimulator` instance's declarations, and the retry loop calls `sim.generate()` directly — not `build_fn`. This requires the loop to hold a reference to the mutable simulator, not the script.
3. **Soft-fail policy:** Define what happens when auto-fix exhausts retries. Does Phase 3 receive the failed data? Is there a quality threshold? (finding C12)

#### G. Evidence

- §2.9 (spec lines 574–575 vs. 582–584): L1 finiteness check contradicts realism NaN injection
- §2.9 (spec lines 613–621): L2 KS test runs on post-injection data
- §2.8 (spec line 530): Pattern injection modifies data before validation
- §2.9 (spec lines 691–698): Fix strategies applied then discarded by `build_fn` re-execution
- Gap analysis findings B2 (CRITICAL), B3 (CRITICAL), B7 (MODERATE), C5 (MODERATE), C6 (MODERATE)
- Alignment map Blocker 5: 1 SPEC_INCORRECT directly, 8+ degraded indirectly
- Sprint plan: 9.2.1–9.2.3 labeled "isolated stubs"; 9.3.1 in Blocked Backlog

---

### 2.6 Phase 1 → Phase 2 Typed Interface Contract is Missing

#### A. Blocked capability

The Phase 2 pipeline receives a scenario context from Phase 1 and injects it into the LLM prompt (§2.5 `{scenario_context}` placeholder). The working system already passes this as a JSON blob via `json.dumps(scenario, indent=2)`. What's missing is a **typed, validated, versioned contract** defining the required fields, optional fields, types, and serialization format for this interface.

Affected subtasks: 10.1.2 (scenario context injection — BLOCKED), 11.1.1 (pipeline orchestrator — BLOCKED on this plus C5).

#### B. High-level cause

**Missing inter-phase typed contract.** The scenario context is a cross-boundary data structure produced by Phase 1 and consumed by Phase 2. It has a de facto schema (enforced by `ScenarioContextualizer.validate_output()` in Phase 1, which checks for `scenario_title`, `data_context`, `key_entities`, `key_metrics`, `temporal_granularity`, `target_rows`), but no formal typed definition.

**Stage 1 correction:** The Stage 1 current-state map correctly notes (§2J, §2K) that a "working JSON injection path already exists." The alignment map v3 explicitly softened this blocker. This blocker is about **formalization**, not basic capability. It is lower-severity than the metadata schema (Blocker 2.1), formula DSL (Blocker 2.2), or distribution families (Blocker 2.3).

#### C. Exact ambiguity location

The ambiguity is in the **SDK API / inter-phase contract semantics**:

- Which fields are required vs. optional?
- What are the types of each field? (`target_rows`: int? string? Can it be null?)
- What happens if Phase 1 produces extra fields not expected by Phase 2?
- Is there a version field for forward compatibility?
- Should the `ScenarioContext` be a formal Python dataclass, a JSON Schema, or a TypedDict?

#### D. Downstream implementation decisions blocked

1. **Typed scenario context injection.** The prompt template builder (10.1.2) can render `{scenario_context}` from a raw dict, but cannot validate completeness or type-safety without a schema.
2. **Pipeline orchestrator entry point.** The orchestrator (11.1.1) accepts a scenario from Phase 1 and passes it through. Without a typed contract, error handling for malformed scenarios is ad hoc.
3. **Integration testing.** End-to-end tests need a fixture scenario. Without a formal schema, the fixture is a copy of the one-shot example rather than a validated contract.

#### E. Partial implementation still possible

The existing `json.dumps(scenario)` injection path works for the one-shot example and any scenario matching the de facto field set. The prompt template (10.1.1) is implementable. Code extraction and validation (10.2.1, 10.2.2) are implementable. The `LLMClient.generate_code()` integration verification is implementable. Only the formalization subtask (10.1.2) and the downstream orchestrator are blocked.

#### F. Minimum decisions needed to unblock

Define `ScenarioContext` as a typed dataclass (or Pydantic model) with required fields (`scenario_title: str`, `target_rows: int`, `key_entities: list[dict]`, `key_metrics: list[dict]`, `temporal_granularity: dict`), optional fields, and a validation method. The alignment map v4 notes that `audit/5_agpds_pipeline_runner_redesign.md` already contains a `ScenarioContext` / `result_models.py` design that can serve as direct input.

#### G. Evidence

- §2.5 (spec lines 387–389): `{scenario_context}` placeholder with no schema
- Gap analysis finding D1 (post-audit, downgraded from CRITICAL to high-MODERATE)
- Alignment map Blocker 6: 2 BLOCKED subtasks, softened in v3
- Sprint plan Blocker 6 resolution text, including reference to existing `ScenarioContextualizer.validate_output()`

---

### 2.7 Cross-Group Default Semantics are Undefined

#### A. Blocked capability

When two dimension groups have neither a `declare_orthogonal()` nor an `add_group_dependency()` declaration, the spec does not define how their root columns are sampled. §2.2 states cross-group independence is "opt-in, not default" but never specifies the actual default behavior. With N dimension groups, there are O(N²) pairs, and most will have no explicit declaration.

This is not listed as a numbered blocker in the alignment map or sprint plan, but it was flagged as a CRITICAL finding (A12) in the post-audit gap analysis and affects subtask 4.1.1 (sample independent categorical roots — NEEDS_CLARIFICATION with assumption of independent sampling).

#### B. High-level cause

**Missing conceptual model decision.** The spec defines two explicit modes (orthogonal, dependent) but not the default mode. This is a product-semantics question: should the system require exhaustive pairwise declarations (rejecting incomplete scenarios), assume independence as default (contradicting the "opt-in" language), or treat undeclared pairs as "unknown" with some fallback?

#### C. Exact ambiguity location

The ambiguity is in the **conceptual model** (§2.2) and propagates to the **execution behavior** (§2.4 skeleton builder):

- §2.2 (spec line 153): "Cross-group independence is opt-in, not default"
- §2.1.2 prompt hard constraint 4: "at least 1 `declare_orthogonal()`" — but no requirement for exhaustive pairwise declarations
- No definition of behavior for the undeclared case

#### D. Downstream implementation decisions blocked

1. **Skeleton builder sampling logic.** The skeleton builder (4.1.1) must decide whether undeclared pairs are sampled independently, jointly, or rejected. The current assumption (independent sampling) contradicts the "opt-in, not default" language.
2. **Validator orthogonal check scope.** The L1 chi-squared test (8.2.5) only tests declared orthogonal pairs. Should undeclared pairs be tested for independence? For non-independence?
3. **LLM prompt design.** Should the prompt instruct the LLM to declare all pairs, or is partial declaration acceptable?

#### E. Partial implementation still possible

The current assumption (undeclared = independent) allows Sprint 5 to proceed. The assumption is documented. The code can be restructured if the decision changes, since the sampling logic is confined to a single method.

#### F. Minimum decisions needed to unblock

One decision: **define the default cross-group behavior for undeclared pairs.** Options: (a) default to independent (simplest, contradicts "opt-in" language), (b) require the LLM to declare all pairs (cleanest, most constraining), (c) default to "weakly dependent" with a small correlation parameter (complex, not well-motivated).

#### G. Evidence

- §2.2 (spec line 153): "opt-in, not default" language
- Gap analysis finding A12 (CRITICAL, post-audit)
- Alignment map 4.1.1: NEEDS_CLARIFICATION with assumption documented

---

### 2.8 Censoring Schema is Undefined

#### A. Blocked capability

The `censoring` parameter in `set_realism()` appears in the method signature and in the engine pipeline (Phase δ) but has no type annotation, schema, or semantic definition. Left vs. right censoring? Per-column thresholds? Indicator columns? None specified.

Affected subtask: 4.4.3 (censoring injection — BLOCKED).

#### B. High-level cause

**Missing parameter semantics.** This is the simplest blocker — a single API parameter with no definition. It is isolated to the realism injection module and is optional (`censoring=None` default).

#### C. Exact ambiguity location

The ambiguity is in the **SDK API** (§2.1.2 `set_realism` signature) and in the **metadata / schema semantics** (censoring affects the distributional shape of measures, interacting with L2 KS tests and L1 finiteness checks, but no validator adjustments are specified).

#### D. Downstream implementation decisions blocked

1. **Censoring injection logic.** Cannot implement `_inject_realism` censoring without knowing what censoring means.
2. **Metadata representation.** The metadata has no field to record censoring configuration for Phase 3.
3. **Validator adjustment.** L2 KS tests will fail for censored columns because the empirical distribution no longer matches the declared family.

#### E. Partial implementation still possible

Missing value injection (4.4.1) and dirty value injection (4.4.2) are both implementable and scheduled in Sprint 6. The `set_realism()` signature stores `censoring` as an opaque dict (Sprint 4). The `censoring=None` default path works.

#### F. Minimum decisions needed to unblock

Define the censoring dict schema: target column(s), direction (left/right/interval), threshold value(s), and whether a censoring indicator column is added.

#### G. Evidence

- §2.1.2 (spec line 129): `censoring` in signature with no definition
- Gap analysis finding A4 (MODERATE, extended in post-audit to cover metadata and validation cross-section)
- Alignment map Blocker 7: 1 BLOCKED subtask

---

## 3. Blocker Dependency Map

The blockers have a strict dependency structure. Some are root causes; others are downstream symptoms or compound effects.

```
ROOT CAUSES (independent, can be resolved in parallel):
┌─────────────────────────────────┐  ┌──────────────────────────┐  ┌───────────────────────────────┐
│ 2.1 Metadata Schema Contract    │  │ 2.2 Formula DSL Grammar  │  │ 2.3 Distribution Family Params│
│ [9+ subtasks, highest leverage] │  │ [4 subtasks, structural] │  │ [7 subtasks, stochastic]      │
└──────────────┬──────────────────┘  └────────────┬─────────────┘  └──────────────┬────────────────┘
               │                                  │                               │
               │                                  │                               │
               ▼                                  ▼                               ▼
         ┌─────────────────────────────────────────────────────────────────────────────┐
         │                    Validator L2 is fully blocked                            │
         │   (needs metadata fields + formula evaluator + distribution params)         │
         └─────────────────────────────────┬───────────────────────────────────────────┘
                                           │
COMPOUND BLOCKER (depends on 2.1 + 2.4):   │
┌───────────────────────────────────┐      │
│ 2.4 Pattern Type Triples          │      │
│ [9 subtasks, co-design needed]    │──────┤
└──────────────┬────────────────────┘      │
               │                           │
               ▼                           ▼
         ┌─────────────────────────────────────────────────────────────────────────────┐
         │ 2.5 Post-Processing Invariant Contract (L2/Pattern/AutoFix contradiction)  │
         │ Depends on: metadata (2.1) to know what to validate                        │
         │             pattern triples (2.4) to know what distortions L2 must tolerate │
         │ [1 SPEC_INCORRECT direct, 8+ degraded]                                     │
         └─────────────────────────────────┬───────────────────────────────────────────┘
                                           │
INTERFACE BLOCKER (independent):           │
┌───────────────────────────────────┐      │
│ 2.6 Phase 1 Contract              │      │
│ [2 subtasks, formalization only]  │──────┤
└───────────────────────────────────┘      │
                                           ▼
                                    ┌──────────────────────────┐
                                    │ Pipeline Orchestrator     │
                                    │ 11.1.1, 11.1.2 (BLOCKED)│
                                    │ Terminal dependency —     │
                                    │ needs ALL upstream        │
                                    └──────────────────────────┘

ISOLATED BLOCKERS (can be resolved at any time):
┌───────────────────────────────────┐  ┌────────────────────────────────┐
│ 2.7 Cross-Group Default Semantics │  │ 2.8 Censoring Schema           │
│ [0 hard-blocked, 1 assumption]    │  │ [1 subtask, optional feature]  │
└───────────────────────────────────┘  └────────────────────────────────┘
```

**Key structural insight:** Blockers 2.1, 2.2, and 2.3 are independent root causes that can be resolved in parallel. Together they unblock ~20 subtasks immediately. Blocker 2.4 is semi-independent (its params schema needs no upstream resolution, but its L3 validation tests need the metadata schema from 2.1). Blocker 2.5 is the most downstream — it is a compound of 2.1 (metadata contract) + 2.4 (pattern design) + its own pseudocode contradiction. Blocker 2.6 is independent but low-leverage (2 subtasks, partially mitigated by existing infrastructure). Blockers 2.7 and 2.8 are isolated and low-impact.

**The pipeline orchestrator (11.1.1, 11.1.2) is the terminal dependency.** It cannot be wired until all upstream blockers are resolved. This is not itself a "blocker" — it is a consequence of the architecture's deep dependency chain.

---

## 4. Root-Cause Summary

The eight blockers reduce to five root-cause categories.

### Category 1: Missing Shared Data Contracts

**Why it matters:** When multiple subsystems (engine, validator, metadata builder, auto-fix, Phase 3) must agree on a data structure, that structure must be formally defined once. The spec defines these structures by example or not at all, leaving each consumer to reverse-engineer the expected format.

**What it blocks:** Blocker 2.1 (metadata schema), Blocker 2.3 (distribution params), and partially Blocker 2.6 (Phase 1 interface). These are the three highest-leverage blockers, together accounting for 18+ subtasks.

**How serious:** **Critical.** This is the #1 root cause. The metadata schema alone is the single most-connected contract in the system — every validator check, every auto-fix strategy, and Phase 3 consumption all depend on it. Resolving the metadata schema unblocks 9 subtasks immediately. Resolving the distribution reference table unblocks 7 more. These are multiplicative because they feed into the same downstream systems (validator, engine, auto-fix).

### Category 2: Missing Formal Grammar for Expression Language

**Why it matters:** The formula DSL is used in three modules (SDK validation, engine generation, L2 validation) but exists only as example strings. Any system that parses or evaluates untrusted string expressions needs a formal grammar — this is a security boundary, not just a convenience.

**What it blocks:** Blocker 2.2 (formula DSL). 4 subtasks across 3 modules, plus DAG edge type 5.

**How serious:** **Critical but narrow.** The impact is concentrated on the structural-measure pipeline. Resolving it unblocks 4 subtasks and completes the DAG construction. The fix is also narrow — one page of operator/precedence specification.

### Category 3: Missing Co-Designed Behavioral Triples

**Why it matters:** Some features require simultaneous specification of (input schema, transformation algorithm, validation check) because these three components are tightly coupled. Specifying any one without the others produces an inconsistent system. The four unspecified pattern types and the undefined auto-fix strategies for 5 of 9 failure modes fall into this category.

**What it blocks:** Blocker 2.4 (pattern types). 9 subtasks across 3 modules. Additionally, the auto-fix strategy coverage gap (finding C4) means 5+ failure modes have no recovery path.

**How serious:** **Critical for feature completeness, not for the architecture.** The two specified pattern types (`outlier_entity`, `trend_break`) work end-to-end. The system can ship with 2 of 6 pattern types and add the rest when specified. But the missing types are not incrementally addable — each requires coordinated design across SDK, engine, and validator.

### Category 4: Contradictory Execution-Model Semantics

**Why it matters:** When the spec provides pseudocode that contradicts itself (auto-fix applies fixes then discards them) or contains checks that always fail by design (L1 finiteness vs. realism NaN; L2 KS vs. pattern injection), the implementation must choose between following the pseudocode (producing a broken system) or deviating from the spec (producing a correct but non-conforming system).

**What it blocks:** Blocker 2.5 (post-processing invariant contract). 1 SPEC_INCORRECT subtask directly, 8+ degraded indirectly. The auto-fix retry loop is the central affected component.

**How serious:** **Critical for system stability.** Without a post-processing invariant contract, the validation and auto-fix system will oscillate (L2 fixes fight L3 fixes) or be ineffective (fixes discarded on regeneration). This is the only root cause where the spec provides *wrong* guidance rather than *missing* guidance, making it arguably more dangerous — an implementer who follows the pseudocode literally will build a system that cannot converge.

### Category 5: Missing Conceptual-Model Decisions

**Why it matters:** Some blockers are not about implementation details but about product-level semantic choices that the spec doesn't make — what is the default cross-group behavior? What does censoring mean? These are upstream of any code.

**What it blocks:** Blocker 2.7 (cross-group defaults), Blocker 2.8 (censoring). Together: 1 hard-blocked subtask + 1 assumption-based subtask.

**How serious:** **Low.** Both are isolated. Cross-group default has a workable assumption (independent sampling). Censoring is optional (`censoring=None` default). Neither blocks the critical path. But the cross-group default is a conceptual landmine — the "opt-in, not default" language in §2.2 contradicts the only workable assumption (treat undeclared pairs as independent), creating potential semantic drift if the assumption is later rejected.
