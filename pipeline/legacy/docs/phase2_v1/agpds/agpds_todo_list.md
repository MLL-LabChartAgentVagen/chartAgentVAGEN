---
title: "AGPDS Gap Assessment & Refactoring TODO List"
date: "2026-02-25"
source_spec:
  - storyline/chartagent_proposal.md
  - storyline/data_generation/data_generation_pipeline.md
  - storyline/data_generation/chart_type_registry.md
  - storyline/data_generation/phase_0.md
  - storyline/data_generation/phase_1.md
  - storyline/data_generation/phase_2.md
  - storyline/data_generation/phase_3.md
current_codebase:
  - pipeline/generation_pipeline.py
  - pipeline/generation_runner.py
  - pipeline/adapters/basic_operators.py
  - pipeline/schemas/master_table.py
  - metadata/metadata.py
  - main.py
---

# AGPDS Gap Assessment & Refactoring TODO List

## Structural Diff: AGPDS Specification vs. Current Implementation

| Dimension | AGPDS Requires | Current Implementation Has | Gap Severity |
|-----------|---------------|---------------------------|--------------|
| **Pipeline phases** | 4 phases (0–3) with strict sequential boundaries | 3 effective nodes (A→B→C) + optional Node D; no Phase 0 domain pool | Critical |
| **Domain management** | Phase 0: 200+ cached domains with Topic→Sub-topic taxonomy, embedding-based dedup, complexity tiers | `META_CATEGORIES` list of 30 flat category strings (line 44–75 of `generation_pipeline.py`) | Critical |
| **Scenario generation** | Phase 1: structured JSON with `scenario_title`, `data_context`, `key_entities`, `key_metrics`, `temporal_granularity`, `target_rows` | Node A outputs `semantic_concept`, `topic_description`, `suggested_entities`, `suggested_metrics`, `domain_context` — close but not aligned to AGPDS schema | High |
| **Data generation paradigm** | Phase 2: LLM writes Python SDK script (`FactTableSimulator`) → deterministic engine executes → atomic-grain fact table | Node B: LLM generates raw CSV data directly (LLM-as-Data-Generator paradigm) | Critical |
| **SDK** | `FactTableSimulator` with `add_category()`, `add_measure()`, `add_temporal()`, `add_conditional()`, `add_dependency()`, `add_correlation()`, `declare_orthogonal()`, `inject_pattern()`, `set_realism()` | No SDK exists. No `FactTableSimulator` class. | Critical |
| **Data granularity** | Atomic-grain: each row = one indivisible event (100–3000 rows) | Aggregated: 15–25 rows of pre-summarized data | Critical |
| **Schema metadata** | Rich structured metadata: dimension_groups, orthogonal_groups, correlations, dependencies, patterns, conditionals | `MasterTable.metadata` is an opaque dict; no dimension groups, no orthogonality, no patterns | Critical |
| **Chart type registry** | 6 families, 16 chart types with `row_range`, `required_columns`, `data_patterns`, `qa_capabilities` | `ChartType` Enum with 6 types (bar, scatter, pie, histogram, line, heatmap); flat `CHART_SCHEMAS` without families or capabilities | High |
| **View extraction** | Deterministic SQL projection: `ViewEnumerator`, `VIEW_EXTRACTION_RULES`, `CHART_SELECTION_GUIDE`, suitability scoring | `_adapter_*` methods on `NodeC_SchemaMapper` with ad-hoc relational transforms per chart type | High |
| **Multi-chart dashboards** | `DashboardComposer` with 7 inter-chart relationship types, k=2,3,4 composition patterns | No dashboard composition. Each chart type is generated independently. | Critical |
| **Validation** | Three-layer validation (Structural / Statistical / Pattern) with auto-fix loop | `validate_master_table()` and per-chart `validate_*_schema()` — schema-level only, no statistical or pattern validation | High |
| **Error feedback loop** | Execution-Error Feedback: typed SDK exceptions → LLM self-correction (max 3 retries) | No error feedback loop for data generation | High |
| **QA generation** | Intra-view (8 types), Inter-view (7 types), Pattern-triggered QA with difficulty tiering | Node D generates captions only (`ground_truth_caption`). No structured QA generation. | Critical |
| **Overlap detection** | Embedding-based cosine similarity dedup for topics/subtopics/scenarios | String substring matching for concept diversity (`NodeA_TopicAgent.validate_output` line 720–724) | Medium |
| **Determinism** | Phase 3 is fully deterministic with fixed seed. Reproducibility guaranteed. | No seed management. LLM calls used throughout. | High |
| **Operator algebra** | Formal operator algebra: Set operators (π, σ, γ, τ, λ) + Scalar operators (Σ, Ψ, Δ) with composition logic | `basic_operators.py` implements Filter, Project, GroupBy, Aggregate, Sort, Limit, Chain — partial set coverage, no scalar operators, no composition algebra | Medium |
| **Anti-pattern: chart-type binding** | Phase 1 prohibits any mention of chart types | Current Node A suggests 8–12 entities and 2–3 metrics — chart-type agnostic, but Node C's `PROMPT_NODE_C_SCHEMA_MAPPER` binds all 6 types simultaneously | Medium |

---

## Prioritized TODO List

| ID | Component | Gap | Action | Priority | Effort |
|----|-----------|-----|--------|----------|--------|
| TODO-001 | `pipeline/` [NEW] `fact_table_simulator.py` | No `FactTableSimulator` SDK exists — the core technical contribution of AGPDS | **Create** the `FactTableSimulator` class with all 9 API methods: `add_category()`, `add_measure()`, `add_temporal()`, `add_conditional()`, `add_dependency()`, `add_correlation()`, `declare_orthogonal()`, `inject_pattern()`, `set_realism()`, and the deterministic `generate()` engine | Critical | XL |
| TODO-002 | `pipeline/` [NEW] `domain_pool.py` | No Phase 0 domain pool construction; current `META_CATEGORIES` is a flat list of 30 strings | **Create** a Domain Pool module with: Topic/Sub-topic taxonomy, LLM-batch generation prompts, embedding-based overlap detection (`check_overlap()`), `DomainSampler` class, typed JSON output schema | Critical | L |
| TODO-003 | `pipeline/generation_pipeline.py` → `NodeB_DataFabricator` | Node B uses LLM-as-Data-Generator (generates raw CSV). AGPDS requires LLM-as-Data-Programmer (generates SDK scripts) | **Rewrite** Node B to prompt the LLM for a Python script calling `FactTableSimulator` SDK, then execute in sandbox. Replace CSV generation prompt (`PROMPT_NODE_B_DATA_FABRICATOR`) with the code-generation prompt from `phase_2.md` §2.2 | Critical | L |
| TODO-004 | `pipeline/` [NEW] `schema_metadata.py` | No structured Schema Metadata (`dimension_groups`, `orthogonal_groups`, `correlations`, `patterns`, etc.) | **Create** a Schema Metadata dataclass/TypedDict matching the spec in `phase_2.md` §2.3 — must be the contract between Phase 2 and Phase 3 | Critical | M |
| TODO-005 | `pipeline/` [NEW] `view_enumerator.py` | No automated view enumeration or scoring | **Create** `ViewEnumerator` class with `enumerate()` method, `VIEW_EXTRACTION_RULES` for 16 chart types, `CHART_SELECTION_GUIDE`, suitability scoring logic, and `ViewSpec` dataclass | Critical | XL |
| TODO-006 | `pipeline/` [NEW] `dashboard_composer.py` | No multi-chart dashboard composition | **Create** `DashboardComposer` class implementing 7 inter-chart relationship types and 8 composition patterns for k=2,3,4 dashboards | Critical | L |
| TODO-007 | `pipeline/` [NEW] `qa_generator.py` | No structured QA generation; only captions exist | **Create** rule-based QA generation with: `INTRA_VIEW_TEMPLATES` (8 types), `INTER_VIEW_TEMPLATES` (7 types), `PatternDetector` class, difficulty tiering (Easy/Medium/Hard/Very Hard) | Critical | XL |
| TODO-008 | `pipeline/` [NEW] `validators.py` | No three-layer validation | **Create** `SchemaAwareValidator` with `_L1_structural()`, `_L2_statistical()`, `_L3_pattern()` methods and auto-fix loop matching `phase_2.md` §2.6 | Critical | L |
| TODO-009 | `pipeline/generation_pipeline.py` → `ChartType` Enum | Only 6 chart types (bar, scatter, pie, histogram, line, heatmap). AGPDS specifies 16 types across 6 families | **Extend** with: `grouped_bar_chart`, `area_chart`, `box_plot`, `violin_plot`, `donut_chart`, `stacked_bar_chart`, `treemap`, `bubble_chart`, `radar_chart`, `waterfall_chart`, `funnel_chart`. Add `family` attribute to each type. | High | M |
| TODO-010 | `pipeline/generation_pipeline.py` → `CHART_SCHEMAS` | Flat chart schema definitions with no registry-level metadata (no `row_range`, `data_patterns`, `qa_capabilities`) | **Replace** with `CHART_TYPE_REGISTRY` from `chart_type_registry.md`, adding family, row_range, required_columns, optional_features, data_patterns, qa_capabilities per type | High | M |
| TODO-011 | `pipeline/generation_pipeline.py` → `NodeA_TopicAgent` | Output schema diverges from AGPDS Phase 1 spec. Missing `scenario_title`, `temporal_granularity`, `target_rows` fields. | **Refactor** Node A output to match Phase 1 JSON schema: `scenario_title`, `data_context`, `key_entities`, `key_metrics`, `temporal_granularity`, `target_rows` | High | S |
| TODO-012 | `pipeline/generation_pipeline.py` → `PROMPT_NODE_A_TOPIC_AGENT` | Prompt references flat META_CATEGORIES and lacks structured domain metadata input | **Rewrite** prompt to accept sampled domain metadata (from Phase 0 pool) as structured JSON input, following `phase_1.md` §1.2 prompt templates | High | S |
| TODO-013 | `pipeline/generation_pipeline.py` → `PROMPT_NODE_B_DATA_FABRICATOR` | Prompt asks LLM to generate CSV rows directly | **Replace** with SDK code-generation prompt from `phase_2.md` §2.2, including SDK method reference, hard constraints, and one-shot example | High | M |
| TODO-014 | `pipeline/generation_pipeline.py` → `META_CATEGORIES` | 30 flat category strings vs. AGPDS's 200+ two-level taxonomy (Topic → Sub-topic) with complexity tiers | **Replace** with Phase 0 domain pool integration; deprecate the static list | High | S |
| TODO-015 | `pipeline/generation_pipeline.py` → `MasterDataRecord` | Flat record with entities, primary/secondary/tertiary values — aggregated grain | **Delete** or deprecate. Replace with atomic-grain `pd.DataFrame` + `SchemaMetadata` output from `FactTableSimulator.generate()` | High | S |
| TODO-016 | `pipeline/generation_pipeline.py` → `PipelineState` | State schema does not accommodate Schema Metadata, multi-chart views, or QA pairs | **Extend** with `schema_metadata: dict`, `views: list[ViewSpec]`, `dashboards: list[Dashboard]`, `qa_pairs: list[QAPair]` | High | S |
| TODO-017 | `pipeline/generation_pipeline.py` → `NodeC_SchemaMapper` | Monolithic mapper with per-chart `_adapter_*` methods + legacy `transform_to_*` + LLM fallback | **Refactor** into `ViewEnumerator` + `extract_view()` pattern; deprecate all `_adapter_*` and `transform_to_*` methods | High | L |
| TODO-018 | `pipeline/generation_pipeline.py` → `NodeD (PROMPT_NODE_D_RL_CAPTIONER)` | Generates captions only. AGPDS Phase 3 generates structured QA (intra-view + inter-view + pattern-triggered) | **Replace** with rule-based QA generation module (TODO-007). Deprecate LLM captioning in Phase 3. | High | M |
| TODO-019 | `pipeline/adapters/basic_operators.py` | Missing operators: no Scalar operators (Aggregation subtypes, Positioning, Arithmetic), no composition algebra | **Extend** with ValueAt, ArgMax/ArgMin, Add/Sub/Mult/Div/Ratio operators. Add Sequential, Parallel, and Conditional composition. | Medium | M |
| TODO-020 | `pipeline/schemas/master_table.py` → `MasterTable` | Validates "Star Schema" constraints but lacks dimension group awareness, orthogonality tracking, or pattern metadata | **Extend** to hold and validate dimension_groups, orthogonal_groups, and injected patterns from Schema Metadata | Medium | M |
| TODO-021 | `pipeline/generation_pipeline.py` → `NodeA_TopicAgent.validate_output()` | Uses substring matching for concept dedup (line 720–724). AGPDS requires embedding-based cosine similarity dedup. | **Replace** with `check_overlap()` function using text-embedding-3-small model and threshold-based cosine similarity | Medium | S |
| TODO-022 | `pipeline/` [NEW] `sandbox_executor.py` | No sandbox for executing LLM-generated Python scripts | **Create** a sandboxed Python executor that runs `build_fact_table()` scripts, captures exceptions, and routes tracebacks back to LLM | Medium | M |
| TODO-023 | `pipeline/generation_pipeline.py` → All `validate_*_schema()` methods | 6 separate validator methods in NodeC do schema-level checks only | **Consolidate** into `SchemaAwareValidator` (TODO-008). Deprecate per-chart-type validators. | Medium | S |
| TODO-024 | `pipeline/` [NEW] `chart_renderer.py` | No unified chart rendering module. Chart rendering is in `chartGenerators/` (per-type subdirectories) | **Create** a unified `render_chart(view, view_spec)` function that dispatches to matplotlib/plotly based on `ViewSpec.chart_type`. Must handle all 16 chart types. | Medium | L |
| TODO-025 | `pipeline/generation_pipeline.py` → `CHART_SCHEMAS` keys | Literal string keys: `"bar_data"`, `"scatter_x_data"`, etc. AGPDS uses `ViewSpec`-based column bindings (`{cat}`, `{measure}`) | **Refactor** chart data schemas to use generic column-role bindings from `VIEW_EXTRACTION_RULES` instead of chart-specific key names | Medium | M |
| TODO-026 | `pipeline/generation_runner.py` → `ChartAgentPipelineRunner` | Runner orchestrates Node A→B→C→D sequentially; no Phase 0 bootstrap or seed management | **Refactor** to orchestrate 4-phase pipeline, with Phase 0 bootstrap (idempotent/cached), seed propagation, and batch control | Medium | M |
| TODO-027 | `pipeline/generation_pipeline.py` → Color palettes | 7 hardcoded color palette arrays in prompt | **Move** color assignment to chart rendering layer; remove from LLM prompt (anti-pattern: LLM should not decide colors in AGPDS) | Low | XS |
| TODO-028 | `pipeline/generation_pipeline.py` → Naming conventions | Nodes named A/B/C/D; AGPDS uses functional names (domain pool, scenario contextualization, agentic data simulator, view amortization) | **Rename** classes: `NodeA_TopicAgent` → `ScenarioContextualizer`, `NodeB_DataFabricator` → `AgenticDataSimulator`, `NodeC_SchemaMapper` → `ViewAmortizationEngine` | Low | XS |
| TODO-029 | `pipeline/` directory structure | All pipeline logic in a single 2158-line file (`generation_pipeline.py`) with 7 sections | **Split** into separate modules per AGPDS phase: `phase_0/`, `phase_1/`, `phase_2/`, `phase_3/`, `core/` (LLM client, utilities) | Low | M |
| TODO-030 | `pipeline/generation_pipeline.py` → `PROMPT_NODE_D_RL_CAPTIONER` | Caption prompt produces only `ground_truth_caption`. AGPDS requires reasoning chains with each QA pair. | **Delete** or repurpose. Reasoning chains should be produced by the deterministic QA generator (TODO-007), not by LLM. | Low | XS |
| TODO-031 | `pipeline/generation_pipeline.py` → Reproducibility | No seed parameter, no bit-for-bit reproducibility guarantees | **Add** `seed` parameter to pipeline entry point; propagate to `FactTableSimulator`, view extraction, and QA generation | Low | S |

---

## Summary

**Total divergences identified:** 31

**Breakdown by priority:**

| Priority | Count | Key Theme |
|----------|-------|-----------|
| Critical | 8 | Missing core AGPDS modules: SDK, domain pool, view enumerator, dashboard composer, QA generator, validator, schema metadata, Phase 2 rewrite |
| High | 10 | Chart type expansion (6→16), prompt rewrites, state schema, Node refactoring, data granularity |
| Medium | 9 | Operator algebra extension, sandbox executor, naming standardization, MasterTable enhancement |
| Low | 4 | Cosmetic renames, directory restructure, reproducibility, deprecated prompt cleanup |

**Estimated total effort:** ~8–10 engineering-weeks for full AGPDS conformance.

The single highest-impact item is **TODO-001** (FactTableSimulator SDK): it is the foundation upon which TODO-003 (Node B rewrite), TODO-004 (Schema Metadata), TODO-005 (View Enumeration), and TODO-008 (Validation) all depend. Implementing TODO-001 first unblocks the entire downstream chain.
