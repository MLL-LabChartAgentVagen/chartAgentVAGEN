---
title: "AGPDS Specification Alignment Audit"
date: 2026-03-04
compliance_summary:
  COMPLIANT: 14
  PARTIAL: 10
  MISSING: 2
  DEFERRED: 7  # Phase 3
  UNVERIFIABLE: 1
phase3_readiness_verdict: "BLOCKED (Phase 2 Component Failures)"
---

# AGPDS Spec Alignment Audit

> **Scope:** Compare every spec-defined requirement in the AGPDS framework markdowns against the current implementation across `pipeline/`. No code was executed.
>
> **Spec Sources:** `chartagent_proposal.md`, `data_generation_pipeline.md`, `phase_0.md`, `phase_1.md`, `phase_2.md`, `phase_3.md`, `chart_type_registry.md`
>
> **Implementation Source:** `00_codebase_map.md` file tree + source files.

---

## Check 1 — Framework Design Extraction

### 1.1 Officially Named Pipeline Stages

1. **Phase 0: Domain Pool Construction** — One-time, cached. LLM batch-generates 200+ fine-grained domains across 15+ topics. Embedding-based dedup + complexity balancing → typed JSON pool. [Source: `data_generation_pipeline.md` § 3, `phase_0.md` § Title]
2. **Phase 1: Scenario Contextualization** — Samples a domain from the Phase 0 pool; LLM instantiates a concrete, realistic scenario (entities, metrics, temporal grain, target volume). [Source: `data_generation_pipeline.md` § 3, `phase_1.md` § Title]
3. **Phase 2: Agentic Data Simulator (SDK-Driven)** — LLM writes Python SDK script → Master Fact Table + Schema Metadata. Includes three sub-phases:
   - **Phase 2a:** LLM Code Generation [Source: `00_codebase_map.md` § Data Flow [3]]
   - **Phase 2b:** Sandbox Execution [Source: `00_codebase_map.md` § Data Flow [3]]
   - **Phase 2c:** Deterministic Engine (`FactTableSimulator.generate()`) [Source: `00_codebase_map.md` § Data Flow [3]]
4. **Phase 3: View Amortization & QA Instantiation** — Deterministic SQL projection → chart views → multi-tier QA with reasoning chains. **Entirely deterministic — no LLM calls.** [Source: `data_generation_pipeline.md` § 3, `phase_3.md` § Title]

### 1.2 Atomic Grain Concept

> *"Atomic event records (each row = one transaction/visit/reading) preserving full dimensional hierarchy and long-tail statistics."* [Source: `data_generation_pipeline.md` § 1, Principle 1 — "Generative Fact Tables"]

> *"Every row is an indivisible event record."* [Source: `data_generation_pipeline.md` § 7, Core Contribution 1]

> *"ATOMIC_GRAIN: each row = one indivisible event."* [Source: `phase_2.md` § 2.2, HARD CONSTRAINTS item 1]

**Definition:** One atomic unit = one row in the Master Table representing a single, indivisible real-world event (e.g., one hospital visit, one delivery, one sensor reading). All chart views are derived downstream via SQL projection — never fabricated by the LLM.

### 1.3 Required Input/Output Contracts per Stage

| Stage | Input | Output |
|-------|-------|--------|
| **Phase 0** | `metadata/taxonomy_seed.json` (seed topics) | `metadata/domain_pool.json` — JSON with `domains: [...]`, each domain having: `id`, `name`, `topic`, `complexity_tier`, `typical_entities_hint`, `typical_metrics_hint`, `temporal_granularity_hint` [Source: `phase_0.md` § 0.5] |
| **Phase 1** | `domain_context` dict (one sampled domain from Phase 0) | `scenario` dict with 6 required fields: `scenario_title`, `data_context`, `key_entities` (3–8), `key_metrics` (2–5 with name/unit/range), `temporal_granularity`, `target_rows` (100–3000) [Source: `phase_1.md` § 1.2] |
| **Phase 2** | `scenario` dict (from Phase 1) | `(pd.DataFrame, SchemaMetadata dict)` — SchemaMetadata contains: `dimension_groups`, `orthogonal_groups`, `columns`, `conditionals`, `correlations`, `dependencies`, `patterns`, `total_rows` [Source: `phase_2.md` § 2.3] |
| **Phase 3** | `Master Table` + `SchemaMetadata` | `{chart_image(s), question, answer, reasoning_chain, difficulty} × N` — 10–30+ tasks per Master Table [Source: `phase_3.md` § 3.5] |

### 1.4 Explicitly Stated Design Constraints / Anti-Patterns

1. **"LLM is called only in Phases 0–2. Phase 3 is entirely deterministic."** [Source: `data_generation_pipeline.md` § 3, note below diagram]
2. **"Phase 1 deliberately makes zero mention of chart types."** Premature chart-type binding causes template-hijacked schemas — "the single most important design decision." [Source: `phase_1.md` § end note]
3. **All column declarations (Step 1) BEFORE any relationship declarations (Step 2).** [Source: `phase_2.md` § 2.2, HARD CONSTRAINT 3]
4. **At least 2 dimension groups, ≥1 categorical column each, plus ≥2 measures.** [Source: `phase_2.md` § 2.2, HARD CONSTRAINT 2]
5. **At least 1 `declare_orthogonal()`, 1 `add_correlation()`, and 2 `inject_pattern()`.** [Source: `phase_2.md` § 2.2, HARD CONSTRAINTS 4–5]
6. **Max retries = 3 for execution-error feedback loop.** [Source: `phase_2.md` § 2.4, item 6: "max_retries=3"]
7. **Three-layer validation auto-fix: "Typically converges in 1–2 retries at near-zero cost."** [Source: `phase_2.md` § 2.6, closing note]
8. **`DomainSampler` resets at 80% exhaustion.** [Source: `phase_0.md` § 0.6, docstring: "Resets at 80% exhaustion"]
9. **Child columns sampled conditionally on parent**: *"P(department | hospital) follows the declared weights within the parent context."* [Source: `phase_2.md` § 2.1.2]
10. **Pattern params should be nested under `params` key**, not flattened. [Source: `phase_2.md` § 2.3, `SchemaMetadata` example; `schema_metadata.py` `PatternMeta.params: Optional[dict]`]

---

## Check 2 — Stage-by-Stage Compliance Matrix

### Phase 0: Domain Pool Construction

| # | Spec Requirement | Implementation Location | Status | Gap Description |
|---|-----------------|-------------------------|--------|-----------------|
| P0-1 | LLM batch-generates topics via Topic Generation Prompt [§0.2] | `domain_pool.py:DomainPool._generate_topics()` (lines 132–166) | ✅ COMPLIANT | System + user prompt structure matches spec |
| P0-2 | LLM generates sub-topics via Sub-topic Generation Prompt [§0.3] | `domain_pool.py:DomainPool._generate_subtopics()` (lines 168–216) | ✅ COMPLIANT | Sub-topic prompt includes complexity tiers |
| P0-3 | `check_overlap()` for embedding-based deduplication [§0.4] | `domain_pool.py:check_overlap()` (lines 460+) | ⚠️ PARTIAL | Spec requires embedding similarity via `text-embedding-3-small`; implementation uses TF-IDF with Jaccard fallback (no embedding API call). Functionally equivalent but algorithmically different. **[POSSIBLY INTENTIONAL]** |
| P0-4 | Output schema with `version`, `generated_at`, `total_domains`, `diversity_score`, `complexity_distribution`, `topic_coverage`, `domains[]` [§0.5] | `domain_pool.py:DomainPool._save_pool()` | ⚠️ PARTIAL | `diversity_score` and `topic_coverage` fields not observed in output builder — only `domains` list is saved. Missing top-level metadata. |
| P0-5 | `DomainSampler` with stratified without-replacement sampling, reset at 80% exhaustion [§0.6] | `domain_pool.py:DomainSampler.sample()` (lines 442–448) | ⚠️ PARTIAL | Reset threshold is `len(candidates) < n` (100% exhaustion), not 80%. **Already flagged in correctness audit as A3-3.** |
| P0-6 | Pool of 200+ fine-grained domains across 15+ topics | `metadata/taxonomy_seed.json` + `DomainPool.load_or_build()` | 🔍 UNVERIFIABLE | Depends on runtime LLM output and existing `domain_pool.json` |

### Phase 1: Scenario Contextualization

| # | Spec Requirement | Implementation Location | Status | Gap Description |
|---|-----------------|-------------------------|--------|-----------------|
| P1-1 | Input: domain sample from Phase 0 pool | `agpds_pipeline.py:run_single()` line 95 → `self.domain_sampler.sample(n=1)` | ✅ COMPLIANT | Correctly samples and passes to contextualizer |
| P1-2 | System prompt matching spec [§1.2] — 8 rules including entity count 3–8, metrics 2–5, target_rows 100–3000 | `scenario_contextualizer.py:SCENARIO_SYSTEM_PROMPT` | ✅ COMPLIANT | Prompt structure and constraints match |
| P1-3 | User prompt with one-shot example injecting domain metadata [§1.2] | `scenario_contextualizer.py:_build_user_prompt()` | ✅ COMPLIANT | One-shot example and `{domain_json}` injection present |
| P1-4 | Output validation: required fields, entity count 3–8, metric count 2–5, target_rows 100–3000 | `scenario_contextualizer.py:validate_output()` | ✅ COMPLIANT | All range checks present |
| P1-5 | `deduplicate_scenarios()` using `check_overlap` [§1.3] | `scenario_contextualizer.py:deduplicate_scenarios()` line 283 | ⚠️ PARTIAL | Import path is `from phase_0.domain_pool import check_overlap` — wrong path; will raise `ModuleNotFoundError`. **Already flagged as A2-6.** Additionally, function is defined but never called in the pipeline orchestrator. |
| P1-6 | Phase 1 makes "zero mention of chart types" [§ end note] | `scenario_contextualizer.py` | ✅ COMPLIANT | No chart type references in Phase 1 code |

### Phase 2: Agentic Data Simulator

| # | Spec Requirement | Implementation Location | Status | Gap Description |
|---|-----------------|-------------------------|--------|-----------------|
| P2-1 | `FactTableSimulator` SDK with `add_category`, `add_measure`, `add_temporal`, `add_conditional`, `add_dependency`, `add_correlation`, `declare_orthogonal`, `inject_pattern`, `set_realism` [§2.1.1] | `fact_table_simulator.py` | ✅ COMPLIANT | All 9 API methods present with correct signatures |
| P2-2 | Supported distributions: 8 named types [§2.1.1] | `distributions.py:SUPPORTED_DISTS` | ✅ COMPLIANT | All 8 distributions implemented |
| P2-3 | Pattern types: 6 named patterns [§2.1.1] | `patterns.py:PATTERN_TYPES` | ✅ COMPLIANT | All 6 pattern types implemented |
| P2-4 | Dimension groups with within-group hierarchy via `parent` [§2.1.2] | `fact_table_simulator.py:add_category(parent=...)` | ⚠️ PARTIAL | Parent parameter accepted and stored, but child sampling is independent of parent — hierarchy not enforced at generation time. **Already flagged as A2-4.** Spec says: *"P(department \| hospital) follows the declared weights within the parent context."* |
| P2-5 | Cross-group orthogonality via `declare_orthogonal()` propagating to all column pairs [§2.1.2] | `fact_table_simulator.py:declare_orthogonal()` + `_build_skeleton()` | ✅ COMPLIANT | Group-level independence declaration and cross-join sampling |
| P2-6 | LLM Code Generation Prompt [§2.2] — system prompt with SDK methods, hard constraints, one-shot example | `sandbox_executor.py:PHASE2_SYSTEM_PROMPT` | ⚠️ PARTIAL | `PHASE2_SYSTEM_PROMPT` exists in sandbox_executor but `agpds_pipeline.py:_build_phase2_prompt()` overrides it with a custom prompt referencing non-existent methods. **Already flagged as A2-1 (CRITICAL).** |
| P2-7 | Spec prompt says `return sim.generate()` [§2.2] | `agpds_pipeline.py:_build_phase2_prompt()` lines 72–73 | ❌ MISSING | Prompt instructs `simulator.generate_with_validation()` and `simulator.get_schema_metadata()` — neither exists. **Already flagged as A2-1.** |
| P2-8 | Execution-Error Feedback Loop: max_retries=3 [§2.4] | `agpds_pipeline.py:run_single()` line 107: `max_retries=10` | ⚠️ PARTIAL | Spec says 3 retries; implementation uses 10. **[POSSIBLY INTENTIONAL]** — more retries may be deliberate for robustness. |
| P2-9 | `SchemaMetadata` output contract [§2.3] — 8 top-level keys | `schema_metadata.py:SchemaMetadata` TypedDict + `fact_table_simulator.py:_build_schema_metadata()` | ⚠️ PARTIAL | (a) `noise_sigma` dropped from `dependencies` [A1-1]; (b) pattern params flattened via `dict.update` instead of nested [A1-2 CRITICAL]; (c) `total_rows` uses declared target, not actual [A1-3]. |
| P2-10 | 7-stage deterministic engine: β→δ→γ→λ→ψ→φ→ρ [§2.5] | `fact_table_simulator.py:generate()` lines 496–530 | ✅ COMPLIANT | All 7 stages present in correct order |
| P2-11 | Three-layer validation: L1 Structural, L2 Statistical, L3 Pattern [§2.6] | `validators.py:SchemaAwareValidator._L1_structural`, `_L2_statistical`, `_L3_pattern` | ✅ COMPLIANT | All three layers implemented |
| P2-12 | Auto-fix loop: `generate_with_validation(build_fn, meta, max_retries=3)` [§2.6] | `validators.py:generate_with_validation()` | ⚠️ PARTIAL | Function exists but has signature `(build_fn, max_retries, base_seed)` — no `meta` parameter. Auto-fix mutates via `apply_fixes(report, meta)` which requires `meta` to be passed separately. Seed increment vs FactTableSimulator self.seed mismatch. **Already flagged as A3-6.** |
| P2-13 | Sandbox restricts imports to safe modules [§2.4] | `sandbox_executor.py:_SAFE_BUILTINS` line 65 | ❌ MISSING | `__import__` included unrestricted — bypasses sandbox. **Already flagged as A3-1 (CRITICAL).** |
| P2-14 | Prompt format: `[SCENARIO]\n{scenario_context}\n[AGENT CODE]` [§2.2] | `sandbox_executor.py:run_with_retries()` constructs this; but `agpds_pipeline.py` passes pre-formatted prompt as `scenario_context` | ⚠️ PARTIAL | Double-wrapping issue — custom prompt from `_build_phase2_prompt()` gets wrapped again. **Already flagged as A2-3.** |

### Phase 3: View Amortization & QA Instantiation

> **Scope Note:** Phase 3 implementation is delegated to a teammate and is considered **OUT OF SCOPE** for the current developer's review. These items are marked as deferred.

| # | Spec Requirement | Implementation Location | Status | Gap Description |
|---|-----------------|-------------------------|--------|-----------------|
| P3-1 | `ViewEnumerator` — enumerate all `(chart_type, column_binding)` pairs [§3.1.4] | N/A | ⏭️ DEFERRED | Out of scope; delegated to teammate |
| P3-2 | `VIEW_EXTRACTION_RULES` for 16 chart types [§3.1.2] | N/A | ⏭️ DEFERRED | Out of scope; delegated to teammate |
| P3-3 | `CHART_SELECTION_GUIDE` — scoring by analytical intent [§3.1.3] | N/A | ⏭️ DEFERRED | Out of scope; delegated to teammate |
| P3-4 | `DashboardComposer` — multi-chart composition (k=2,3,4) [§3.2] | N/A | ⏭️ DEFERRED | Out of scope; delegated to teammate |
| P3-5 | Rule-based QA generation: Intra-View templates [§3.3.1] | N/A | ⏭️ DEFERRED | Out of scope; delegated to teammate |
| P3-6 | Inter-View QA templates [§3.3.2] | N/A | ⏭️ DEFERRED | Out of scope; delegated to teammate |
| P3-7 | `PatternDetector` — pattern-triggered QA [§3.3.3] | N/A | ⏭️ DEFERRED | Out of scope; delegated to teammate |

### Cross-Cutting

| # | Spec Requirement | Implementation Location | Status | Gap Description |
|---|-----------------|-------------------------|--------|-----------------|
| CC-1 | `MasterTable` wrapping: star-schema validation | `pipeline/core/master_table.py:MasterTable` | ✅ COMPLIANT | Wraps DataFrame + metadata with validation |
| CC-2 | CLI entry point with model/provider/category args | `agpds_runner.py:main()` | ⚠️ PARTIAL | Default model `gemini-3.1-pro-preview` does not exist. **Already flagged as A4-1 (CRITICAL).** |
| CC-3 | Result serialization: CSV + JSON metadata + manifest | `agpds_runner.py:save_results()` | ✅ COMPLIANT | All three artifacts produced |

---

## Check 3 — Atomic Grain Integrity

### 3a. Decomposition at Spec-Defined Grain Level

**Spec requirement:** *"Each row = one indivisible event"* [Source: `phase_2.md` § 2.2, HARD CONSTRAINT 1]

**Implementation:** `FactTableSimulator._build_skeleton()` (lines 536–579) builds the dimensional cross-join and tiles to `target_rows`. Each row represents one combination of categorical × temporal values with independent measure samples.

**Verdict: ✅ COMPLIANT** — The skeleton builder produces atomic-grain rows. Each row is a unique dimensional combination with independent measure sampling. No pre-aggregation occurs.

### 3b. Multi-Grain Conflation Points

1. **`_apply_conditionals()` operates per-category group** — correctly preserves grain by overwriting measure values per-row based on the matching category. ✅ No grain conflation.

2. **`_build_phase2_prompt()` prompt (lines 65–73)** instructs the LLM to call `generate_with_validation(target_rows=...)` — this does not match any existing API. If the LLM were to follow these instructions, it would fail outright (no grain issue, just total failure). ⚠️ **Execution-blocking, not grain-conflating.**

3. **`_inject_correlations()` via Gaussian Copula** operates on the full DataFrame column-wise. This is correct — correlation injection preserves individual row identity. ✅

4. **`_inject_patterns()` operates on filtered subsets** and modifies in-place — grain preserved. ✅

### 3c. Programmatic Synthesis Step Match

**Spec:** *"The LLM writes executable Python scripts calling a type-safe SDK. Schema definition and DGP are unified in a single code pass."* [Source: `phase_2.md` § Title, `chartagent_proposal.md` § 2.2]

**Implementation:** The LLM generates a `build_fact_table(seed=...)` function that calls `FactTableSimulator` methods and returns `sim.generate()`. This is executed in `SandboxExecutor.execute()`.

**Verdict: ✅ COMPLIANT at the architectural level**, but the orchestrator-level prompt (`_build_phase2_prompt`) instructs the wrong API calls, making the pipeline non-functional end-to-end (see A2-1).

---

## Check 4 — Naming & Structural Conventions

### 4a. Terminology Deviations

| Spec Term | Implementation Term | Deviation | Severity |
|-----------|-------------------|-----------|----------|
| `FactTableSimulator` | `FactTableSimulator` | ✅ Match | — |
| `DomainPool` | `DomainPool` | ✅ Match | — |
| `DomainSampler` | `DomainSampler` | ✅ Match | — |
| `ScenarioContextualizer` | `ScenarioContextualizer` | ✅ Match | — |
| `SandboxExecutor` | `SandboxExecutor` | ✅ Match | — |
| `SchemaAwareValidator` | `SchemaAwareValidator` | ✅ Match | — |
| `generate_with_validation()` | `generate_with_validation()` | ✅ Match | — |
| `SchemaMetadata` | `SchemaMetadata` (TypedDict) | ✅ Match | — |
| `ExecutionResult` | `ExecutionResult` | ✅ Match | — |
| `ValidationReport` | `ValidationReport` | ✅ Match | — |
| `inject_pattern(type=...)` param | `inject_pattern(type=...)` | ⚠️ Shadows built-in `type` | NOTE (A2-7) |
| `ViewEnumerator` [§3.1.4] | *Out of Scope* | ⏭️ DEFERRED | Phase 3 (Teammate) |
| `DashboardComposer` [§3.2.4] | *Out of Scope* | ⏭️ DEFERRED | Phase 3 (Teammate) |
| `PatternDetector` [§3.3.3] | *Out of Scope* | ⏭️ DEFERRED | Phase 3 (Teammate) |
| `ViewSpec` [§3.1] | *Out of Scope* | ⏭️ DEFERRED | Phase 3 (Teammate) |
| `QAPair` [§3.3] | *Out of Scope* | ⏭️ DEFERRED | Phase 3 (Teammate) |

### 4b. Directory Structure

**Spec-implied structure** (from phase numbering):

| Expected | Actual | Status |
|----------|--------|--------|
| `pipeline/phase_0/` | `pipeline/phase_0/` | ✅ |
| `pipeline/phase_1/` | `pipeline/phase_1/` | ✅ |
| `pipeline/phase_2/` | `pipeline/phase_2/` | ✅ |
| `pipeline/phase_3/` | *Does not exist* | ⏭️ DEFERRED (Out of scope) |
| `metadata/domain_pool.json` | `metadata/domain_pool.json` | ✅ |
| `metadata/taxonomy_seed.json` | `metadata/taxonomy_seed.json` | ✅ |
| `pipeline/agpds_pipeline.py` (orchestrator) | Present | ✅ |
| `pipeline/agpds_runner.py` (CLI) | Present | ✅ |

**Legacy modules still present:** `pipeline/core/topic_agent.py`, `pipeline/core/schema_mapper.py`, `pipeline/core/pipeline_runner.py`, `pipeline/core/basic_operators.py`, `pipeline/adapters/basic_operators.py`, `pipeline/generation_pipeline.py`, `pipeline/chart_qa_pipeline.py`. These are superseded by AGPDS but not removed. **[POSSIBLY INTENTIONAL — kept as reference.]**

---

## Check 5 — Phase 3 Readiness Gate

### 5a. Required Phase 3 Inputs (from spec)

Phase 3 requires the following inputs [Source: `phase_3.md` § 3.5]:

| # | Required Input | Source Spec |
|---|---------------|-------------|
| R1 | `Master Table` (pd.DataFrame, N rows × C columns) | `phase_3.md` § 3.5, line 1 |
| R2 | `schema_metadata["dimension_groups"]` — dict of group name → `{columns, hierarchy}` | `phase_3.md` § 3.1.4 `_group_columns_by_role()` |
| R3 | `schema_metadata["orthogonal_groups"]` — list of `{group_a, group_b, rationale}` | `phase_3.md` § 3.2.3 "Orthogonal Contrast" |
| R4 | `schema_metadata["columns"]` — list with `name`, `type` (`categorical`/`temporal`/`measure`), `group`, `parent`, `cardinality` | `phase_3.md` § 3.1.4 `_group_columns_by_role()`, § 3.1.2 column bindings |
| R5 | `schema_metadata["columns"][*]["role"]` — column role for binding (`primary`, `secondary`, `orthogonal`, `temporal`, `measure`) | `phase_3.md` § 3.1.4 `_group_columns_by_role()`: `groups[col["role"]]` |
| R6 | `schema_metadata["correlations"]` — list of `{col_a, col_b, target_r}` | `phase_3.md` § 3.2.2 "Associative" relationship |
| R7 | `schema_metadata["dependencies"]` — list of `{target, formula}` | `phase_3.md` § 3.2.2 "Causal Chain" relationship |
| R8 | `schema_metadata["patterns"]` — list with `type`, `target`, `col`, pattern-specific params | `phase_3.md` § 3.3.3 `PatternDetector` |
| R9 | `schema_metadata["conditionals"]` | `phase_3.md` § 3.3 (implicit via QA templates) |
| R10 | `schema_metadata["total_rows"]` | `phase_3.md` § 3.1.2 constraint checking |

### 5b. Per-Field Production Status

| # | Required Field | Produced by Phase 0–2? | Blocker? |
|---|---------------|----------------------|----------|
| R1 | Master Table DataFrame | ✅ Yes — `FactTableSimulator.generate()` returns `(df, meta)` | — |
| R2 | `dimension_groups` | ✅ Yes — `_build_schema_metadata()` lines 920–939 | — |
| R3 | `orthogonal_groups` | ✅ Yes — `_build_schema_metadata()` lines 994–999 | — |
| R4 | `columns` with name/type/group/parent/cardinality | ✅ Yes — lines 941–962. Categorical, temporal, measure all present | — |
| R5 | `columns[*]["role"]` (primary/secondary/orthogonal/measure/temporal) | ❌ **NOT PRODUCED** | **BLOCKER** — `_build_schema_metadata()` emits `"type"` (categorical/temporal/measure) but not `"role"` (primary/secondary/orthogonal). Phase 3's `_group_columns_by_role()` reads `col["role"]`, which does not exist in current output. |
| R6 | `correlations` | ✅ Yes — lines 970–974 | — |
| R7 | `dependencies` | ⚠️ Partial — `noise_sigma` dropped [A1-1]. Phase 3 `_build_causal_chain()` reads only `target` + `formula`, so this is non-blocking. | — |
| R8 | `patterns` | ⚠️ Partial — params flattened via `dict.update` [A1-2]. Phase 3 `PatternDetector._generate_pattern_qa()` reads both top-level and `params`-nested keys (line 811: `pattern.get("break_point", pattern.get("params", {}).get("break_point"))`), so the spec-bridging code already handles both layouts. | Non-blocking (fragile) |
| R9 | `conditionals` | ✅ Yes — lines 964–968 | — |
| R10 | `total_rows` | ⚠️ Partial — uses declared target, not actual [A1-3] | Non-blocking |

### 5c. Final Verdict

## ❌ BLOCKED — Phase 2 Output Contract Violations

> **Note:** The actual implementation of Phase 3 is out of scope for the current developer and will be handled by a teammate. However, Phase 2 is currently **BLOCKED** from successfully handing off its data to Phase 3 due to the following pipeline and output contract violations:

**Critical Contract Blockers:**

| # | Blocker | Impact | Fix Required |
|---|---------|--------|-------------|
| B1 | **`columns[*]["role"]` field not produced** | Phase 3's `ViewEnumerator` will crash, as it expects the `"role"` key (`primary`/`secondary`/`orthogonal`/`temporal`/`measure`) on each column entry to match spec. Current implementation emits `"type"` only. | Add role assignment logic to `_build_schema_metadata()`: root columns in groups → `primary`; non-root → `secondary`; columns in orthogonal group counterparts → `orthogonal`; temporal → `temporal`; measure → `measure`. |
| B2 | **Pipeline prompt references non-existent methods** | LLM-generated scripts fail at execution, meaning no Master Table or `SchemaMetadata` is produced to be handed off to Phase 3. | Rewrite prompt in `_build_phase2_prompt` to use correct SDK API (`sim.generate()`). |
| B3 | **Pattern `params` flattening** | Can corrupt `type`/`col`/`target` keys in the SchemaMetadata, passing malformed and untrustworthy configuration to Phase 3. | Fix merging logic: `pat_entry["params"] = dict(p["params"])`. |

**Non-Critical Issues for Phase 3 Readiness (fix recommended but not blocking):**

- `noise_sigma` missing from dependencies metadata (A1-1)
- `total_rows` reflects target, not actual (A1-3)
- `deduplicate_scenarios()` broken import path (A2-6)
- `DomainSampler` 80% threshold not enforced (A3-3)
- `__import__` sandbox bypass (A3-1) — security issue, not a Phase 3 contract issue

---

## Appendix — Compliance Summary

| Status | Count | Description |
|--------|-------|-------------|
| ✅ COMPLIANT | 14 | Spec requirement fully met |
| ⚠️ PARTIAL | 10 | Implemented but with deviations from spec |
| ❌ MISSING | 2 | Phase 2 spec requirement not implemented |
| ⏭️ DEFERRED | 7 | Out of scope for current developer (Phase 3) |
| 🔍 UNVERIFIABLE | 1 | Depends on runtime conditions |

---

*[WRITE CONFIRMED] /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/audit/02_spec_alignment.md | 220 lines*
