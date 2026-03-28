# Phase 2 Current State Map

**Generated from:** `phase_2.md` (spec), `1_phase2_implementation_task_hierarchy.md` (task hierarchy v2), `2_phase2_gap_analysis.md` (gap analysis v2), `3_phase2_implementation_alignment_map.md` (alignment map v4), `4_phase2_sprint_plan.md` (sprint plan v4)

---

## 1. Phase 2 objective

Phase 2 replaces JSON-based data-generating-process specifications with **Code-as-DGP** — an LLM writes executable Python scripts calling a type-safe SDK (`FactTableSimulator`). Each measure is declared as a closed-form data-generating program in a single SDK call, all inter-column dependencies form an explicit DAG, and a DAG-ordered deterministic engine executes event-level row generation. A three-layer validator (structural, statistical, pattern) ensures correctness without additional LLM calls. The output is an atomic-grain fact table (the "Master Table") paired with schema metadata — the contract consumed by Phase 3 for view extraction and QA generation.

The system has three major subsystems that execute sequentially: (1) the LLM generates an SDK script from a scenario context, (2) a deterministic engine executes the script to produce data, and (3) a validator checks the output and auto-fixes failures without LLM re-calls. An execution-error feedback loop (§2.7) wraps step 1–2, and a validation auto-fix loop (§2.9) wraps step 2–3.

---

## 2. Major functional areas

### 2A. SDK Declaration API

- **Purpose:** Provide a type-safe, strongly-validated surface for the LLM to declare table schema, distributions, dependencies, patterns, and realism config. All declarations are append-only and validated at registration time to fail fast on structural errors before any generation occurs.
- **Included capabilities:**
  - `add_category()` — categorical column declaration with within-group hierarchy, auto-normalization, per-parent conditional weights (§2.1.1, §2.2)
  - `add_temporal()` — temporal column with derived calendar features (§2.1.1, §2.2)
  - `add_measure()` — stochastic root measure with param_model (intercept + effects) across 8 distribution families (§2.1.1, §2.3)
  - `add_measure_structural()` — derived measure via formula + effects + noise, creating DAG edges (§2.1.1, §2.3)
  - `declare_orthogonal()` — cross-group independence declaration (§2.1.2, §2.2)
  - `add_group_dependency()` — cross-group root-level conditional dependency (§2.1.2, §2.2)
  - `inject_pattern()` — 6 pattern types for narrative-driven anomalies (§2.1.2)
  - `set_realism()` — missing values, dirty values, censoring (§2.1.2)
- **Dependencies:** Dimension Group Model (data structures). Custom Exception Hierarchy (typed errors at validation time).
- **Main source basis:** §2.1.1, §2.1.2, §2.2, §2.3; task hierarchy sections 1.1–1.9.

### 2B. Dimension Group Model

- **Purpose:** Internal data structures representing groups, within-group hierarchies, cross-group orthogonality, and cross-group dependencies. This is the structural backbone that the SDK API populates and that the engine and metadata builder read.
- **Included capabilities:**
  - `DimensionGroup` dataclass — root, columns, hierarchy ordering (§2.2)
  - `OrthogonalPair` dataclass — order-independent group pair with rationale (§2.2)
  - `GroupDependency` dataclass — child_root, on, conditional_weights (§2.2)
- **Dependencies:** None (foundation layer).
- **Main source basis:** §2.2; task hierarchy section 2.

### 2C. DAG Construction & Topological Sort

- **Purpose:** Merge all column types (categorical, temporal, measure) and all dependency edges (within-group hierarchy, cross-group dependency, temporal derivation, effects predictor→measure, formula measure→structural measure) into a single directed acyclic graph, then compute a generation order via topological sort.
- **Included capabilities:**
  - `_build_full_dag()` — constructs full generation DAG from all registries (§2.4, §2.8)
  - `topological_sort()` — computes generation order; raises `CyclicDependencyError` on cycles (§2.4, §2.8)
  - Measure sub-DAG extraction — for measure-only topological order (§2.3, §2.6)
- **Dependencies:** SDK Declaration API (all registries must be populated). Dimension Group Model (group hierarchies provide edges).
- **Main source basis:** §2.4, §2.8; task hierarchy section 3.

### 2D. Deterministic Engine (`generate()`)

- **Purpose:** Execute the DAG-ordered, fully deterministic pipeline that converts declarations into a Master DataFrame. Given the same seed, output is bit-for-bit reproducible. No LLM calls.
- **Included capabilities:**
  - Phase α — Skeleton builder: sample independent roots, cross-group dependent roots, within-group children, temporal root, temporal derivations (§2.4 Step 1, §2.8)
  - Phase β — Measure generation: stochastic parameter resolution + domain validation + sampling dispatch for 8 families; structural formula evaluation + effect materialization + noise sampling; safe expression evaluator (§2.3, §2.4 Step 2, §2.8)
  - Phase γ — Pattern injection: 6 pattern type transformations applied post-generation (§2.8)
  - Phase δ — Realism injection: missing values, dirty values, censoring (§2.8)
  - Post-processing: DataFrame assembly, dtype casting (§2.8)
  - Determinism verification: bit-for-bit reproducibility with same seed (§2.8)
- **Dependencies:** DAG Construction (topological order drives generation sequence). SDK Declaration API (all declarations read by engine). Custom Exception Hierarchy (domain validation errors).
- **Main source basis:** §2.4, §2.8; task hierarchy section 4.

### 2E. Schema Metadata Builder

- **Purpose:** Produce the structured metadata dict that serves as the contract between Phase 2 (producer) and Phase 3 + the validator (consumers). Contains dimension groups, orthogonal declarations, group dependencies, per-column metadata, measure DAG order, patterns, and total rows.
- **Included capabilities:**
  - Emit `dimension_groups`, `orthogonal_groups`, `group_dependencies`, `columns`, `measure_dag_order`, `patterns`, `total_rows` blocks (§2.6)
- **Dependencies:** All SDK registries (reads every internal data structure). DAG Construction (measure_dag_order from topological sort).
- **Main source basis:** §2.6; task hierarchy section 5.

### 2F. Custom Exception Hierarchy

- **Purpose:** Provide typed, descriptive exceptions that enable the LLM self-correction loop (§2.7). Exception messages contain the exact constraint violation for targeted repair.
- **Included capabilities:**
  - `CyclicDependencyError` — cycle path in message (§2.7)
  - `UndefinedEffectError` — effect name + missing key (§2.7)
  - `NonRootDependencyError` — non-root column name (§2.7)
  - `InvalidParameterError` — degenerate/invalid distribution parameters (§2.7, inferred)
- **Dependencies:** None (foundation layer).
- **Main source basis:** §2.7; task hierarchy section 6.

### 2G. Execution-Error Feedback Loop (§2.7 Loop)

- **Purpose:** Execute LLM-generated code in a sandbox, catch SDK exceptions, format error feedback, and retry LLM code generation up to 3 times. This is the code-level self-correction mechanism.
- **Included capabilities:**
  - Sandbox executor — run `build_fact_table()`, capture exceptions + tracebacks (§2.7 steps 1–2)
  - Error feedback formatter — 4-component payload: code, exception class, traceback, fix instruction (§2.7 step 5)
  - Retry loop with max_retries=3 (§2.7 step 6)
- **Dependencies:** Custom Exception Hierarchy (exceptions to catch). LLM Code-Generation Prompt (produces the code to execute). Existing `LLMClient` infrastructure (provides `generate_code()` with fence stripping and provider adaptation).
- **Main source basis:** §2.7; task hierarchy section 7.

### 2H. Three-Layer Validator

- **Purpose:** After the engine produces a Master Table, deterministically check correctness at three levels — structural (L1), statistical (L2), and pattern (L3) — without LLM calls.
- **Included capabilities:**
  - Validator framework: `Check` dataclass, `ValidationReport` aggregator, `validate(df, meta)` orchestrator (§2.9)
  - L1 Structural: row count, categorical cardinality, root marginal weights, measure finiteness, orthogonal independence (chi-squared), DAG acyclicity (§2.9)
  - L2 Statistical: KS test per predictor cell for stochastic measures, structural residual mean/std checks, group dependency conditional deviation, helpers (`iter_predictor_cells`, `_max_conditional_deviation`, `eval_formula`) (§2.9)
  - L3 Pattern: outlier entity z-score, ranking reversal rank correlation, trend break magnitude, dominance shift, convergence, seasonal anomaly (§2.9)
- **Dependencies:** Schema Metadata Builder (validator reads metadata). Deterministic Engine (produces the DataFrame to validate). Formula DSL (L2 residual checks reuse `eval_formula`).
- **Main source basis:** §2.9; task hierarchy section 8.

### 2I. Auto-Fix Loop

- **Purpose:** When validation fails, automatically adjust parameters and re-generate without LLM re-calls. Matches failure check names to fix strategies via glob patterns.
- **Included capabilities:**
  - `match_strategy()` — glob-based dispatch from check name to fix function (§2.9)
  - `widen_variance()` — scale sigma/scale upward by factor 1.2 for KS failures (§2.9)
  - `amplify_magnitude()` — scale pattern magnitude by factor 1.3 for outlier/trend failures (§2.9)
  - `reshuffle_pair()` — permute one column of a pair to destroy spurious correlation for orthogonal failures (§2.9)
  - `generate_with_validation()` — outer retry loop, max_retries=3, seed increment (§2.9)
- **Dependencies:** Three-Layer Validator (produces the failure report). Deterministic Engine (re-generation target). Schema Metadata Builder (metadata contract).
- **Main source basis:** §2.9; task hierarchy section 9.

### 2J. LLM Code-Generation Prompt & Integration

- **Purpose:** Construct the system prompt that instructs the LLM to produce a valid SDK script, inject the scenario context from Phase 1, and parse/validate the LLM response.
- **Included capabilities:**
  - System prompt template — SDK reference, hard constraints, soft guidelines, one-shot example, scenario placeholder (§2.5)
  - Scenario context injection — Phase 1 → Phase 2 typed contract (§2.5)
  - Response parsing — extract Python code, validate contains `build_fact_table` and `sim.generate()` (§2.5)
- **Dependencies:** Phase 1 output (scenario context). Existing `LLMClient` infrastructure (fence stripping, provider adaptation).
- **Main source basis:** §2.5; task hierarchy section 10.

### 2K. End-to-End Pipeline Orchestrator

- **Purpose:** Compose all subsystems into a single pipeline: prompt construction → LLM call → code extraction → sandbox execution → engine generate → three-layer validation → return. Branch to §2.7 loop on execution errors; branch to §2.9 auto-fix loop on validation failures.
- **Included capabilities:**
  - Stage ordering and branch behavior (§2.7 + §2.8 + §2.9)
  - §2.7 execution-error loop driver
  - §2.9 validation loop driver
  - Sequential composition of both loops
  - Budget enforcement (max 3 LLM calls + 3 engine re-runs = 6 total)
- **Dependencies:** All other functional areas. Phase 1 interface contract. Resolved loop composition semantics.
- **Main source basis:** §2.7, §2.8, §2.9; task hierarchy sections 11, 12.

---

## 3. Status after Sprint 8

### 2A. SDK Declaration API

- **Status: Partially developed**
- **Already covered by Sprint 8:**
  - Constructor + registries (Sprint 1: 1.1.1, 1.1.2)
  - `add_category()` — all 6 subtasks including edge cases, per-parent weights, group registry (Sprint 2: 1.2.1–1.2.6)
  - `add_temporal()` — all 4 subtasks including derive whitelist, temporal group registration (Sprint 2: 1.3.1–1.3.4)
  - `add_measure()` — family validation, constant param_model, DAG root registration (Sprint 3: 1.4.1, 1.4.2, 1.4.5). `scale` parameter accepted and stored with warning.
  - `add_measure_structural()` — signature validation, effects dict validation, cycle detection (Sprint 3: 1.5.1, 1.5.3, 1.5.5)
  - `declare_orthogonal()` — all 3 subtasks including conflict check (Sprint 3: 1.6.1–1.6.3)
  - `add_group_dependency()` — root-only constraint, conditional weights validation (single-column `on`), root DAG acyclicity, conflict with orthogonal (Sprint 3–4: 1.7.1–1.7.4)
  - `inject_pattern()` — type validation, target storage, column validation, store pattern (Sprint 4: 1.8.1–1.8.3, 1.8.5). Only outlier_entity and trend_break have param validation.
  - `set_realism()` — signature and rate validation; censoring accepted as opaque dict (Sprint 4: 1.9.1)
- **Still missing:**
  - `param_model` intercept+effects full validation for 6 of 8 distribution families (1.4.3 — BLOCKED on A5/A5a)
  - `mixture` family sub-spec (1.4.4 — BLOCKED on A1)
  - Formula symbol resolution & DAG edge creation (1.5.2 — BLOCKED on A3)
  - Noise spec per-family param validation (1.5.4 — BLOCKED on A5/A1a)
  - Pattern param validation for 4 of 6 pattern types (1.8.4 — BLOCKED on A8)
- **Blocked / unclear points:**
  - Blocker 2 (A3): Formula DSL grammar undefined — blocks formula symbol resolution entirely
  - Blocker 3 (A5, A1): Distribution family parameter keys unspecified for 6 of 8 families; mixture has zero specification
  - Blocker 4 (A8): Pattern params schema missing for ranking_reversal, dominance_shift, convergence, seasonal_anomaly
  - Multiple NEEDS_CLARIFICATION assumptions locked: A9 (min 2 values), A6 (complete parent keys), A7 (single-column `on`), A10 (single temporal, "time" reserved), A2 (`scale` stored/ignored)
- **Evidence:** Sprint plan Sprints 1–4 cover 36 of 41 subtasks in Module 1; alignment map shows 5 BLOCKED subtasks in 1.4.3, 1.4.4, 1.5.2, 1.5.4, 1.8.4.

### 2B. Dimension Group Model

- **Status: Developed**
- **Already covered by Sprint 8:** All 3 subtasks completed in Sprint 1 (2.1.1, 2.2.1, 2.2.2).
- **Still missing:** Nothing.
- **Blocked / unclear points:** None.
- **Evidence:** Alignment map shows all 3 subtasks as SPEC_READY. Sprint plan Sprint 1 includes all three.

### 2C. DAG Construction & Topological Sort

- **Status: Partially developed**
- **Already covered by Sprint 8:**
  - `_build_full_dag()` implemented for edge types 1–4: parent→child, on→child_root, temporal_root→derived, effects predictor→measure (Sprint 4: 3.1.1)
  - `topological_sort()` implemented for pre-formula-edge DAG with lexicographic tie-breaking assumption (Sprint 4: 3.1.2)
  - Measure sub-DAG extraction (Sprint 4: 3.2.1)
- **Still missing:**
  - Edge type 5: formula measure-ref→structural measure edges. These cannot be added until the formula DSL grammar is defined (Blocker 2).
- **Blocked / unclear points:**
  - Blocker 2 (A3): Formula-derived DAG edges require a parser that doesn't exist yet.
  - NEEDS_CLARIFICATION: B4 (general edge-construction algorithm inferred, not formalized), B8 (topo-sort tie-breaking assumed lexicographic, not spec-defined), B5 (temporal predictor edges included under rule 4 by assumption).
- **Evidence:** Sprint plan Sprint 4 scope note explicitly states "structural measure formula edges are not yet available." Alignment map marks 3.1.1 and 3.1.2 as NEEDS_CLARIFICATION.

### 2D. Deterministic Engine (`generate()`)

- **Status: Partially developed**
- **Already covered by Sprint 8:**
  - Phase α skeleton builder — all 5 subtasks: independent roots, cross-group dependent roots, within-group children, temporal root, temporal derivations (Sprint 5: 4.1.1–4.1.5)
  - Phase γ partial — outlier entity injection and trend break injection (Sprint 6: 4.3.1, 4.3.2)
  - Phase δ partial — missing value injection and dirty value injection (Sprint 6: 4.4.1, 4.4.2)
  - Post-processing — DataFrame assembly & dtype casting (Sprint 5: 4.5.1)
- **Still missing:**
  - Phase β — ALL measure generation subtasks (4.2.1–4.2.4 stochastic parameter resolution, domain validation, sampling dispatch, distribution dispatch table; 4.2.5–4.2.8 structural formula evaluation, effect materialization, noise sampling, safe expression evaluator). ALL BLOCKED.
  - Phase γ — 4 of 6 pattern injection types: ranking_reversal, dominance_shift, convergence, seasonal_anomaly (4.3.3–4.3.6). ALL BLOCKED.
  - Phase δ — censoring injection (4.4.3). BLOCKED.
  - Determinism verification (4.6.1) — not scheduled in Sprints 1–8; depends on measure generation existing.
- **Blocked / unclear points:**
  - Blocker 2 (A3): Blocks all structural measure generation (formula evaluation, safe expression evaluator)
  - Blocker 3 (A5, A1): Blocks all stochastic measure generation (parameter resolution, sampling dispatch for 6 of 8 families)
  - Blocker 4 (A8, B6): Blocks 4 of 6 pattern injection types
  - Blocker 7 (A4): Blocks censoring injection
  - B2: Pattern injection vs. L2 validation conflict acknowledged but deferred as "validator issue"
- **Evidence:** Sprint plan shows 4.2.x entirely in Blocked Backlog (Blockers 2 and 3). Sprint plan shows 4.3.3–4.3.6 in Blocked Backlog (Blocker 4). Alignment map confirms all 4 subtasks in 4.2 as BLOCKED, 4 of 6 in 4.3 as BLOCKED.

### 2E. Schema Metadata Builder

- **Status: Partially developed**
- **Already covered by Sprint 8:**
  - `dimension_groups` block (Sprint 5: 5.1.1)
  - `orthogonal_groups` block (Sprint 5: 5.1.2)
  - `measure_dag_order` block (Sprint 5: 5.1.5)
  - `total_rows` block (Sprint 5: 5.1.7)
- **Still missing:**
  - `group_dependencies` block — must include `conditional_weights` which §2.6 example omits (5.1.3 — SPEC_INCORRECT)
  - `columns` block — must include `values`, `weights`, `formula`, `noise_sigma`, `param_model`, `scale`, per-parent conditional weights, which §2.6 example omits (5.1.4 — SPEC_INCORRECT)
  - `patterns` block — must include `params` which §2.6 example omits (5.1.6 — SPEC_INCORRECT)
- **Blocked / unclear points:**
  - Blocker 1 (C3, C8, C9, C13): The §2.6 metadata schema is defined by example only and is internally inconsistent with §2.9 validator code. The validator reads fields (`col["values"]`, `col["weights"]`, `col["formula"]`, `col["noise_sigma"]`, `dep["conditional_weights"]`, `p["metrics"]`) that the metadata example doesn't emit. No formal schema, no types, no versioning.
  - 3 of 7 subtasks are SPEC_INCORRECT — they have specification but that specification contradicts the validator's expectations.
- **Evidence:** Alignment map shows 5.1.3, 5.1.4, 5.1.6 as SPEC_INCORRECT. Sprint plan places all three in Blocked Backlog under Blocker 1. Sprint 5 covers only the 4 non-contradictory fields.

### 2F. Custom Exception Hierarchy

- **Status: Developed**
- **Already covered by Sprint 8:** All 4 subtasks completed in Sprint 1 (6.1.1–6.1.4, including proactive `InvalidParameterError`).
- **Still missing:** Nothing within current scope.
- **Blocked / unclear points:** A5a (which parameter domains trigger `InvalidParameterError`) is a NEEDS_CLARIFICATION; the exception class itself exists but its triggering conditions depend on Blocker 3 resolution.
- **Evidence:** Sprint plan Sprint 1 includes all 4 subtasks. Alignment map shows 3 SPEC_READY + 1 NEEDS_CLARIFICATION.

### 2G. Execution-Error Feedback Loop

- **Status: Partially developed**
- **Already covered by Sprint 8:**
  - Sandbox executor (Sprint 8: 7.1.1) — with NEEDS_CLARIFICATION on security policy
  - Error feedback formatter (Sprint 8: 7.1.2)
  - Retry loop with max_retries=3 (Sprint 8: 7.1.3) — with assumption of sequential composition with §2.9 loop
- **Still missing:** Security hardening (import whitelist, resource limits, timeout) — deferred until spec defines policy.
- **Blocked / unclear points:**
  - A14: No security/sandbox policy specified (CRITICAL gap finding, but subtask proceeds with basic execution)
  - C5: Loop composition with §2.9 is assumed sequential, not formally specified
- **Evidence:** Sprint plan Sprint 8 covers all 3 subtasks. Alignment map shows 1 SPEC_READY + 2 NEEDS_CLARIFICATION.

### 2H. Three-Layer Validator

- **Status: Partially developed**
- **Already covered by Sprint 8:**
  - Framework: `Check` dataclass, `ValidationReport` aggregator (Sprint 6: 8.1.1, 8.1.2)
  - L1: row count, categorical cardinality, orthogonal independence (chi-squared), DAG acyclicity re-check (Sprint 6: 8.2.1, 8.2.2, 8.2.5, 8.2.6)
  - L3 (partial): outlier entity z-score check, trend break magnitude check (Sprint 7: 8.4.1, 8.4.3)
  - L2 helper: `_max_conditional_deviation()` (Sprint 7: 8.3.7)
- **Still missing:**
  - Validator orchestrator `validate(df, meta)` (8.1.3 — DEFERRED, depends on B2/C6 resolution)
  - L1: root marginal weights check (8.2.3 — SPEC_INCORRECT, needs `col["values"]`/`col["weights"]`), measure finiteness check (8.2.4 — SPEC_INCORRECT, conflicts with realism NaN)
  - L2: ALL substantive checks — KS test per predictor cell (8.3.1 — BLOCKED), `iter_predictor_cells` (8.3.2 — BLOCKED), structural residual mean (8.3.3 — SPEC_INCORRECT), structural residual std (8.3.4 — SPEC_INCORRECT), `eval_formula` for L2 (8.3.5 — BLOCKED), group dep conditional deviation (8.3.6 — SPEC_INCORRECT)
  - L3: ranking reversal check (8.4.2 — SPEC_INCORRECT), dominance shift check + helper (8.4.4, 8.4.5 — BLOCKED), convergence validation (8.4.6 — BLOCKED), seasonal anomaly validation (8.4.7 — BLOCKED)
- **Blocked / unclear points:**
  - Blocker 1 (C3, C8, C9): Metadata missing fields the validator reads → 5 SPEC_INCORRECT subtasks
  - Blocker 2 (A3): `eval_formula` for L2 residual computation blocked
  - Blocker 3 (A5, A1, C7): KS test blocked (no family→scipy mapping, no `iter_predictor_cells` algorithm, mixture has no CDF)
  - Blocker 4 (C1, C10, B6): 4 L3 validation branches for underspecified pattern types are blocked
  - Blocker 5 (B2): L2 runs on post-injection data against pre-injection parameters — structural contradiction
  - C6: L1 finiteness check conflicts with realism NaN injection
  - C11: Ranking reversal hard-codes first dimension group
- **Evidence:** Alignment map: 23 subtasks across Modules 8; only 9 are in Sprints 1–8. Sprint plan Blocked Backlog lists 2 SPEC_INCORRECT in 8.2, 3 BLOCKED + 3 SPEC_INCORRECT in 8.3, 4 BLOCKED + 1 SPEC_INCORRECT in 8.4. Module 8.3 (L2) has zero SPEC_READY subtasks.

### 2I. Auto-Fix Loop

- **Status: Partially developed (stubs only)**
- **Already covered by Sprint 8:**
  - `match_strategy()` glob matcher (Sprint 7: 9.1.1)
  - `widen_variance()` as isolated stub (Sprint 7: 9.2.1)
  - `amplify_magnitude()` as isolated stub (Sprint 7: 9.2.2)
  - `reshuffle_pair()` as isolated stub (Sprint 7: 9.2.3)
- **Still missing:**
  - `generate_with_validation()` retry loop (9.3.1 — SPEC_INCORRECT: pseudocode applies fixes then discards them on re-generation)
  - Integration-level testing of all three fix strategies (deferred until B2/B3 resolve)
  - No-LLM-escalation boundary enforcement (9.3.2 — task hierarchy defines it, but depends on 9.3.1)
- **Blocked / unclear points:**
  - Blocker 5 (B2, B3, B7): The auto-fix mutation model is undefined — do fixes mutate the simulator instance or the script? The pseudocode's `build_fn(seed=42+attempt)` discards all fixes. L2 and pattern fixes oscillate. This is a SPEC_INCORRECT contradiction, not merely missing spec.
  - C5: Composition of §2.7 and §2.9 loops is undefined
  - C4: Only 4 of 9+ failure modes have fix strategies; no strategies for row_count, cardinality, marginal weights, finite, structural residuals
- **Evidence:** Sprint plan Sprint 7 explicitly labels 9.2.1–9.2.3 as "isolated stubs." Alignment map marks 9.3.1 as SPEC_INCORRECT. Sprint plan Blocked Backlog lists 9.3.1 under Blocker 5.

### 2J. LLM Code-Generation Prompt & Integration

- **Status: Partially developed**
- **Already covered by Sprint 8:**
  - System prompt construction (Sprint 8: 10.1.1)
  - Integration verification of `LLMClient.generate_code()` fence stripping (Sprint 8: 10.2.1)
  - Code validation for `build_fact_table` + `generate()` (Sprint 8: 10.2.2)
- **Still missing:**
  - Scenario context injection with typed contract (10.1.2 — BLOCKED on D1)
- **Blocked / unclear points:**
  - Blocker 6 (D1): No formal typed schema for Phase 1 → Phase 2 scenario context. A working JSON injection path already exists (`json.dumps(scenario)` → `LLMClient`), but the typed contract (required/optional fields, validation, versioning) is undefined. The blocker is on formalization, not basic capability.
- **Evidence:** Sprint plan Sprint 8 covers 3 of 4 subtasks. 10.1.2 is in Blocked Backlog under Blocker 6. Alignment map v3 notes existing `ScenarioContextualizer.validate_output()` as de facto starting point.

### 2K. End-to-End Pipeline Orchestrator

- **Status: Not developed**
- **Already covered by Sprint 8:** Nothing. Both subtasks are BLOCKED.
- **Still missing:**
  - Full pipeline orchestration: prompt → execute → validate → return (11.1.1)
  - Loop wiring: §2.7 + §2.9 composition (11.1.2)
  - Integration test: §2.10 downstream affordance verification (12.1.1)
- **Blocked / unclear points:**
  - Blocker Composite (C5 + D1): Both loop composition semantics AND Phase 1 typed contract must be resolved. The orchestrator is the terminal dependency — it cannot be wired until virtually all upstream blockers resolve.
  - Blocker 5 (B2, B3): Auto-fix loop is SPEC_INCORRECT; orchestrator cannot compose a broken loop.
  - Architecture reference exists in `audit/5_agpds_pipeline_runner_redesign.md` (per alignment map v4 annotation) but is not part of the 5 spec documents.
- **Evidence:** Sprint plan places both 11.1.1 and 11.1.2 in Blocked Backlog under "Blocker Composite." Alignment map confirms both as BLOCKED. Critical path diagram shows a "[BLOCKED WALL]" after Sprint 8.

---

## 4. Cross-area observations

### Key architectural dependencies

The dependency chain is strict and deep. The three foundation layers (Dimension Group Model → SDK Declaration API → DAG Construction) feed into the Deterministic Engine, which feeds into the Schema Metadata Builder and Three-Layer Validator, which feed into the Auto-Fix Loop, which together with the Execution-Error Feedback Loop feed into the Pipeline Orchestrator. This chain means that blockers in the middle layers (engine, metadata, validator) have cascading downstream impact.

The Schema Metadata Builder (2E) is the single shared contract between the engine (producer), the validator (consumer), and Phase 3 (consumer). Its SPEC_INCORRECT status is the highest-leverage blocker — resolving it simultaneously unblocks 9+ validator subtasks and enables the auto-fix loop and orchestrator path.

### Main concentration of incomplete work

The **Deterministic Engine Phase β** (measure generation) is entirely unimplemented. All 8 subtasks for stochastic and structural measure generation are BLOCKED across two independent blockers (A3 formula DSL, A5 distribution families). This is the core data-generating capability of the entire system — without it, the engine produces skeleton-only DataFrames with zero measure columns.

The **Three-Layer Validator L2** (statistical validation) is the most blocked module in the entire system. Of 7 subtasks, 3 are BLOCKED, 3 are SPEC_INCORRECT, and only 1 is SPEC_READY (the `_max_conditional_deviation` helper). L2 depends on Blockers 1, 2, 3, and 5 simultaneously. It is also the module with the most compounding issues: KS test failures interact with pattern injection (B2), mixture distributions have no scipy CDF (A1b), cell sparsity degrades test power (C2), and the metadata doesn't emit the fields the validator reads (C8/C9).

### Main concentration of blocked work

By blocker, the blocked backlog distributes as follows (from alignment map and sprint plan):

- **Blocker 1 (Metadata Schema):** 9+ subtasks across Modules 5, 8. Highest leverage — resolves SPEC_INCORRECT contradictions.
- **Blocker 2 (Formula DSL):** 4 subtasks across Modules 1, 4, 8. Blocks the entire structural measure pipeline end-to-end.
- **Blocker 3 (Distribution Families):** 7 subtasks across Modules 1, 4, 8. Blocks the entire stochastic measure pipeline.
- **Blocker 4 (Pattern Types):** 9 subtasks across Modules 1, 4, 8. Blocks 4 of 6 pattern injection + validation types.
- **Blocker 5 (L2/Pattern + Auto-Fix Model):** 1 SPEC_INCORRECT subtask directly (9.3.1), but degrades 8+ indirectly. The composed system would oscillate between L2 and L3 fixes.
- **Blocker 6 (Phase 1 Contract):** 2 subtasks (10.1.2, 11.1.1). Softened by existing JSON injection path but blocks formalization.
- **Blocker 7 (Censoring):** 1 subtask (4.4.3). Isolated and low priority.

Total: 24 BLOCKED + 10 SPEC_INCORRECT + 1 deferred NEEDS_CLARIFICATION = **35 subtasks** beyond Sprint 8's reach.

### Document conflicts or ambiguity

1. **§2.6 metadata vs. §2.9 validator code** (C3, C8, C9): The metadata example omits fields the validator pseudocode reads. This is the most consequential internal contradiction — it makes the validator unimplementable against the metadata contract.

2. **§2.9 auto-fix pseudocode self-contradiction** (B3, B7): The pseudocode applies fix strategies (lines 695–698) then calls `build_fn(seed=42+attempt)` (line 691) which re-runs the original LLM script from scratch, discarding all fixes. The fixes and the regeneration are contradictory within the same code block.

3. **§2.8 Phase γ vs. §2.9 L2** (B2): Pattern injection deliberately distorts distributions after measure generation. L2 then tests the distorted distributions against the original declared parameters. These two design decisions are structurally incompatible without a pre/post-injection validation boundary.

4. **§2.9 L1 finiteness vs. §2.8 Phase δ realism** (C6): L1 asserts `notna().all()` for measures. Phase δ deliberately introduces NaN at `missing_rate`. Contradictory by design when realism is active.

5. **Cross-group default semantics** (A12): §2.2 says independence is "opt-in, not default" but never defines the actual default. This affects every scenario with 3+ dimension groups.

---

## 5. Compact evidence table

| Functional area | Status after Sprint 8 | Why | Main source |
|---|---|---|---|
| 2A. SDK Declaration API | Partially developed | 36 of 41 subtasks in Sprints 1–4; 5 BLOCKED on formula DSL (A3), distribution families (A5/A1), pattern params (A8) | Alignment map §1.2–1.9; Sprint plan Sprints 1–4 |
| 2B. Dimension Group Model | Developed | All 3 subtasks completed Sprint 1 | Alignment map §2; Sprint plan Sprint 1 |
| 2C. DAG Construction | Partially developed | Edge types 1–4 built; type 5 (formula) blocked on A3 | Sprint plan Sprint 4 scope note; Alignment map §3 |
| 2D. Deterministic Engine | Partially developed | Phase α complete; Phase β entirely BLOCKED (A3, A5); Phase γ 2/6; Phase δ 2/3 | Alignment map §4.2 (all BLOCKED); Sprint plan Sprints 5–6 |
| 2E. Schema Metadata Builder | Partially developed | 4 of 7 fields emitted; 3 SPEC_INCORRECT (metadata/validator contradiction C3/C8/C9) | Alignment map §5; Blocker 1 in sprint plan |
| 2F. Custom Exception Hierarchy | Developed | All 4 subtasks completed Sprint 1 | Alignment map §6; Sprint plan Sprint 1 |
| 2G. Execution-Error Feedback Loop | Partially developed | All 3 subtasks in Sprint 8; security policy deferred (A14) | Alignment map §7; Sprint plan Sprint 8 |
| 2H. Three-Layer Validator | Partially developed | 9 of 23 subtasks done; L2 has 0 substantive checks (all BLOCKED/SPEC_INCORRECT); L3 missing 5 of 7 | Alignment map §8; Blocked Backlog Blockers 1–4 |
| 2I. Auto-Fix Loop | Partially developed (stubs) | 4 of 5 subtasks as isolated stubs; retry loop is SPEC_INCORRECT (B3/B7); integration deferred | Alignment map §9; Sprint 7 dependency note |
| 2J. LLM Prompt & Integration | Partially developed | 3 of 4 subtasks in Sprint 8; scenario injection blocked on D1 (typed contract formalization) | Alignment map §10; Blocker 6 |
| 2K. Pipeline Orchestrator | Not developed | Both subtasks BLOCKED on C5 + D1; terminal dependency on all upstream | Alignment map §11; Blocker Composite |
