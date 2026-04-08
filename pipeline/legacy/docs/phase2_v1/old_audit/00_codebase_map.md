---
title: "AGPDS Codebase Reconnaissance"
date: 2026-03-04
generated_by: "Cursor Agent — Phase 0"
---

# AGPDS Codebase Reconnaissance

---

## Step 1 — File Tree

All files matching `*.py`, `*.json`, `*.yaml`, `*.md` in the project root, **excluding** `node_modules/` and `skills/` vendor trees. Grouped by directory.

### `/` (root)
```
./README.md
./package.json
./package-lock.json
./test_pipeline_e2e.py
```

### `audit/`
```
./audit/00_codebase_map.md            ← this file
```

### `metadata/`
```
./metadata/taxonomy_seed.json
./metadata/domain_pool.json           (generated artifact — not in VCS by default)
```

### `output/agpds/schemas/`
```
./output/agpds/schemas/agpds_20260301_170952_b4d610_metadata.json
```

### `pipeline/`
```
./pipeline/agpds_pipeline.py
./pipeline/agpds_runner.py
./pipeline/chart_qa_pipeline.py
./pipeline/diversity_checker.py
./pipeline/evaluation_pipeline.py
./pipeline/evaluation_runner.py
./pipeline/generation_pipeline.py
./pipeline/generation_runner.py
./pipeline/test_answer_extraction.py
./pipeline/test_diversity_100.json
./pipeline/PIPELINE_DOCUMENTATION.md
```

### `pipeline/adapters/`
```
./pipeline/adapters/__init__.py
./pipeline/adapters/basic_operators.py
```

### `pipeline/core/`
```
./pipeline/core/__init__.py
./pipeline/core/basic_operators.py
./pipeline/core/llm_client.py
./pipeline/core/master_table.py
./pipeline/core/pipeline_runner.py
./pipeline/core/schema_mapper.py
./pipeline/core/topic_agent.py
./pipeline/core/utils.py
```

### `pipeline/core/tests/`
```
./pipeline/core/tests/__init__.py
./pipeline/core/tests/test_core_imports.py
```

### `pipeline/data_files/`
```
./pipeline/data_files/bar__meta_qa_data.json
```

### `pipeline/phase_0/`
```
./pipeline/phase_0/__init__.py
./pipeline/phase_0/domain_pool.py
```

### `pipeline/phase_0/tests/`
```
./pipeline/phase_0/tests/__init__.py
./pipeline/phase_0/tests/test_domain_pool.py
```

### `pipeline/phase_1/`
```
./pipeline/phase_1/__init__.py
./pipeline/phase_1/scenario_contextualizer.py
```

### `pipeline/phase_1/tests/`
```
./pipeline/phase_1/tests/__init__.py
./pipeline/phase_1/tests/test_scenario_contextualizer.py
```

### `pipeline/phase_2/`
```
./pipeline/phase_2/__init__.py
./pipeline/phase_2/distributions.py
./pipeline/phase_2/fact_table_simulator.py
./pipeline/phase_2/patterns.py
./pipeline/phase_2/sandbox_executor.py
./pipeline/phase_2/schema_metadata.py
./pipeline/phase_2/validators.py
```

### `pipeline/phase_2/tests/`
```
./pipeline/phase_2/tests/__init__.py
./pipeline/phase_2/tests/test_fact_table_simulator.py
./pipeline/phase_2/tests/test_sandbox_executor.py
./pipeline/phase_2/tests/test_validators.py
```

### `pipeline/results/`
```
./pipeline/results/evaluation_results_gemini_3_16000.json
./pipeline/results/evaluation_results_gemini_3_8000.json
./pipeline/results/evaluation_results_gemini_budget4000.json
./pipeline/results/evaluation_results_gpt5_2.json
```

### `pipeline/schemas/`
```
./pipeline/schemas/__init__.py
./pipeline/schemas/master_table.py
```

### `results/`
```
./results/evaluation_results_gemini.json
./results/evaluation_results_gpt4omini.json
./results/evaluation_results.json
```

### `scripts/`
```
./scripts/build_domain_pool.py
./scripts/convert_to_sft.py
./scripts/validate_sft_data.py
```

### `slides/`
```
./slides/create_agpds_presentation.py
```

### `storyline/`
```
./storyline/chartagent_proposal.md
```

### `storyline/data_generation/`
```
./storyline/data_generation/chart_type_registry.md
./storyline/data_generation/data_generation_pipeline.md
./storyline/data_generation/phase_0.md
./storyline/data_generation/phase_1.md
./storyline/data_generation/phase_2.md
./storyline/data_generation/phase_3.md
```

### `templates/`
```
./templates/chart_generator.py
./templates/operator.py
./templates/parser.py
./templates/question_generator.py
./templates/run_draw.py
```

### `utils/`
```
./utils/json_util.py
./utils/logger.py
./utils/logging_utils.py
./utils/masks/bar_mask.py
./utils/masks/mask_generator.py
./utils/parser.py
```

---

## Step 2 — Module Role Table

> Only `.py` files that are part of the AGPDS project (not vendor/skills/node_modules). Tests and `__init__.py` stubs are listed compactly.

| File Path | Role (1 sentence) | Key Classes / Functions | External Imports |
|---|---|---|---|
| `pipeline/agpds_pipeline.py` | Main orchestrator for the 4-phase AGPDS pipeline (Phases 0–2 implemented). | `AGPDSPipeline`, `run_single`, `_build_phase2_prompt` | `pipeline.core.master_table`, `pipeline.phase_0.domain_pool`, `pipeline.phase_1.scenario_contextualizer`, `pipeline.phase_2.sandbox_executor` |
| `pipeline/agpds_runner.py` | CLI entry point — wraps `AGPDSPipeline` for batch execution and artifact I/O. | `AGPDSRunner`, `run_single`, `run_batch`, `save_results`, `main` | `pipeline.core.llm_client`, `pipeline.core.utils`, `pipeline.agpds_pipeline`, `argparse` |
| `pipeline/phase_0/domain_pool.py` | Phase 0: LLM-driven domain taxonomy builder (`DomainPool`) and stratified sampler (`DomainSampler`). | `DomainPool`, `DomainSampler`, `check_overlap`, `_check_overlap_tfidf`, `_check_overlap_jaccard` | `numpy`, `sklearn` (optional), `json`, `pathlib`, `dataclasses` |
| `pipeline/phase_1/scenario_contextualizer.py` | Phase 1: LLM-driven scenario context generator bridging domain samples to Phase 2 SDK scripts. | `ScenarioContextualizer`, `deduplicate_scenarios`, `validate_output`, `_build_user_prompt` | `json`, `typing` |
| `pipeline/phase_2/fact_table_simulator.py` | Phase 2 core SDK: type-safe builder API + deterministic 7-stage generation engine producing `(DataFrame, SchemaMetadata)`. | `FactTableSimulator`, `add_category`, `add_measure`, `add_temporal`, `add_conditional`, `add_dependency`, `add_correlation`, `declare_orthogonal`, `inject_pattern`, `set_realism`, `generate` | `numpy`, `pandas`, `scipy.stats`, `.distributions`, `.patterns`, `.schema_metadata` |
| `pipeline/phase_2/sandbox_executor.py` | Phase 2 sandbox: executes LLM-generated `build_fact_table()` scripts in a restricted namespace with timeout and retry loop. | `SandboxExecutor`, `ExecutionResult`, `run_with_retries`, `format_error_feedback`, `PHASE2_SYSTEM_PROMPT` | `numpy`, `pandas`, `signal`, `traceback`, `.fact_table_simulator`, `.schema_metadata` |
| `pipeline/phase_2/distributions.py` | Unified sampler for 8 named distributions used by `FactTableSimulator.add_measure()`. | `sample_distribution`, `SUPPORTED_DISTS`, `_sample_gaussian`, `_sample_lognormal`, `_sample_mixture`, etc. | `numpy` |
| `pipeline/phase_2/patterns.py` | Six pattern injection handlers (outlier, trend_break, ranking_reversal, dominance_shift, convergence, seasonal_anomaly) for planting statistical anomalies in the DataFrame. | `inject_pattern`, `PATTERN_TYPES`, `_inject_outlier_entity`, `_inject_trend_break`, `_inject_ranking_reversal`, `_inject_dominance_shift`, `_inject_convergence`, `_inject_seasonal_anomaly` | `numpy`, `pandas` |
| `pipeline/phase_2/validators.py` | Three-layer (structural / statistical / pattern) validator with auto-fix loop; no LLM calls. | `SchemaAwareValidator`, `ValidationReport`, `Check`, `FixAction`, `apply_fixes`, `generate_with_validation` | `numpy`, `pandas`, `scipy.stats` |
| `pipeline/phase_2/schema_metadata.py` | TypedDict definitions forming the Phase 2 → Phase 3 contract. | `SchemaMetadata`, `ColumnMeta`, `DimensionGroupMeta`, `OrthogonalPair`, `ConditionalMeta`, `CorrelationMeta`, `DependencyMeta`, `PatternMeta` | `typing` |
| `pipeline/core/llm_client.py` | Unified multi-provider LLM client (OpenAI / Gemini / Gemini-native / Azure) with automatic parameter adaptation. | `LLMClient`, `GeminiClient`, `ParameterAdapter`, `ProviderCapabilities`, `generate`, `generate_json`, `generate_code` | `openai` (optional), `google.genai` (optional), `json`, `re` |
| `pipeline/core/master_table.py` | Star-schema validated wrapper around a pandas DataFrame with legacy chart adapter. | `MasterTable`, `validate_schema`, `from_csv`, `to_csv`, `to_legacy_chart_entry` | `pandas`, `io`, `dataclasses` |
| `pipeline/core/utils.py` | Shared constants (30-element `META_CATEGORIES` taxonomy) and ID/category helpers. | `META_CATEGORIES`, `generate_unique_id`, `validate_category`, `get_category_by_id`, `print_available_categories` | `json`, `hashlib`, `random`, `datetime` |
| `pipeline/core/basic_operators.py` | Salvaged relational adapters for chart construction operators (legacy path). | (various chart operator classes) | `pandas`, `numpy` |
| `pipeline/core/topic_agent.py` | Salvaged `NodeA_TopicAgent` — LLM topic generation logic (legacy; superseded by `ScenarioContextualizer`). | `NodeA_TopicAgent` | `pipeline.core.llm_client` |
| `pipeline/core/schema_mapper.py` | Salvaged `NodeC_SchemaMapper` — maps master data to chart schema (legacy Phase 3 stub). | `NodeC_SchemaMapper` | `pipeline.core.master_table` |
| `pipeline/core/pipeline_runner.py` | Salvaged pipeline runner from earlier generation pipeline iteration (legacy). | (runner logic) | internal |
| `pipeline/adapters/basic_operators.py` | Older copy of relational adapter operators (pre-refactor version). | (chart operator classes) | `pandas`, `numpy` |
| `pipeline/generation_pipeline.py` | Original monolithic generation pipeline (pre-AGPDS, legacy); contains full chart QA generation system. | `GenerationPipeline`, `NodeA-D`, chart drawers, evaluators | `openai`, `pandas`, `matplotlib`, `PIL` |
| `pipeline/chart_qa_pipeline.py` | Thin runner that wires `GenerationPipeline` for QA chart generation tasks. | `ChartQAPipeline` | `pipeline.generation_pipeline` |
| `pipeline/evaluation_pipeline.py` | Evaluation runner for scoring model answers against ground-truth. | `EvaluationPipeline` | `pandas`, LLM client |
| `pipeline/diversity_checker.py` | Checks topical diversity in a batch of generated samples. | `DiversityChecker` | `sklearn`, `numpy` |
| `pipeline/schemas/master_table.py` | Pydantic/dataclass schema definition for the master table (registry version). | `MasterTableSchema` | `dataclasses` |
| `scripts/build_domain_pool.py` | One-shot offline script; reads `taxonomy_seed.json`, calls `DomainPool.load_or_build()`, writes `domain_pool.json`. | `main`, `load_api_key`, `parse_args` | `pipeline.core.llm_client`, `pipeline.phase_0.domain_pool`, `argparse`, `pathlib` |
| `scripts/convert_to_sft.py` | Post-pipeline script: converts QA JSON data to ms-swift multimodal SFT JSONL format with CoT formatting and train/val split. | `load_qa_data`, `convert_entry`, `format_assistant_response`, `write_jsonl`, `main` | `json`, `pathlib`, `argparse`, `random` |
| `scripts/validate_sft_data.py` | Validates an SFT JSONL file for schema correctness. | `main` (likely) | `json`, `argparse` |
| `test_pipeline_e2e.py` | End-to-end integration test for the full pipeline. | test functions | `pipeline.*` |
| `templates/chart_generator.py` | Template/stub for a chart generation module. | template code | varies |
| `templates/operator.py` | Template/stub for a chart operator module. | template code | varies |
| `templates/parser.py` | Template for a chart data parser. | template code | varies |
| `templates/question_generator.py` | Template for the QA question generator. | template code | varies |
| `templates/run_draw.py` | Template runner for drawing chart images. | template code | varies |
| `utils/json_util.py` | JSON utility helpers (safe load, pretty-print, etc.). | utility functions | `json` |
| `utils/logger.py` | Configures project-wide structured logging. | `setup_logger` | `logging` |
| `utils/logging_utils.py` | Additional logging helpers (e.g., timed context managers). | utility functions | `logging` |
| `utils/masks/bar_mask.py` | Generates binary mask images for bar chart regions. | `BarMask` | `PIL`, `numpy` |
| `utils/masks/mask_generator.py` | Dispatcher for mask generation across chart types. | `MaskGenerator` | `PIL` |
| `utils/parser.py` | Parses LLM output strings (answer extraction, JSON extraction). | parsing functions | `re`, `json` |
| `slides/create_agpds_presentation.py` | Creates a slide deck (PPTX) summarising the AGPDS framework. | `main` | `python-pptx` |

---

## Step 3 — Data Flow Sketch

### Entry Point

**CLI:** `python pipeline/agpds_runner.py --provider gemini --model gemini-... --category N --count K --output-dir ./output/agpds`

**Pre-requisite (one time):** `python scripts/build_domain_pool.py`
→ reads `metadata/taxonomy_seed.json` → calls `DomainPool.load_or_build()` → writes `metadata/domain_pool.json`

---

### End-to-End Pipeline

```
[0] SETUP
    agpds_runner.py: main()
      │ argparse → api_key, model, provider, category_ids, output_dir
      │ LLMClient(api_key, model, provider)           ← pipeline/core/llm_client.py
      │ AGPDSRunner(llm_client)
      │   └─ AGPDSPipeline(llm_client)               ← pipeline/agpds_pipeline.py
      │         DomainSampler(pool_path="metadata/domain_pool.json")
      │         ScenarioContextualizer(llm_client)
      │
      ▼

[1] PHASE 0 — DOMAIN SAMPLING
    Input:  metadata/domain_pool.json  (pre-built JSON; list of domain dicts)
    Module: pipeline/phase_0/domain_pool.py  →  DomainSampler.sample(n=1)
    Logic:  Stratified without-replacement sampling from pool["domains"].
            Resets at 80% exhaustion.
    Output: domain_context dict → {
              "id": "dom_042",
              "name": "ICU bed turnover analytics",
              "topic": "Healthcare",
              "complexity_tier": "complex",
              "typical_entities_hint": [...],
              "typical_metrics_hint": [...],
              "temporal_granularity_hint": "daily"
            }

      ▼

[2] PHASE 1 — SCENARIO CONTEXTUALIZATION
    Input:  domain_context dict (from Phase 0)
    Module: pipeline/phase_1/scenario_contextualizer.py  →  ScenarioContextualizer.generate(domain_sample)
    Logic:  Builds a one-shot user prompt injecting domain metadata.
            Calls LLMClient.generate_json(system=SCENARIO_SYSTEM_PROMPT, user=..., temperature=1.0).
            Validates output (required fields, entity count 3–8, metric count 2–5, target_rows 100–3000).
            Retries up to max_retries on validation failure; soft-fails with warning.
            Updates diversity_tracker (used_titles, used_contexts).
    Output: scenario dict → {
              "scenario_title": "2024 H1 Shanghai Metro Ridership Log",
              "data_context": "...",
              "key_entities": ["Line 1", "Line 2", ...],
              "key_metrics": [{"name": "daily_ridership", "unit": "10k passengers", "range": [5, 120]}, ...],
              "temporal_granularity": "daily",
              "target_rows": 900
            }

      ▼

[3] PHASE 2a — LLM CODE GENERATION
    Input:  scenario dict (from Phase 1), serialized as JSON into a prompt
    Module: pipeline/agpds_pipeline.py  →  _build_phase2_prompt(scenario)
            pipeline/phase_2/sandbox_executor.py  →  run_with_retries(llm, phase2_user_prompt, max_retries=10)
    Logic:  Sends PHASE2_SYSTEM_PROMPT + scenario-enriched user prompt to LLMClient.generate_code().
            Receives a Python source string defining `def build_fact_table(seed=42): ...`.
    Output: Python source code string

      ▼

[3] PHASE 2b — SANDBOX EXECUTION
    Input:  Python source string
    Module: pipeline/phase_2/sandbox_executor.py  →  SandboxExecutor.execute(script, seed)
    Logic:  compile() → exec() in restricted namespace (FactTableSimulator, np, pd, math, datetime only).
            Calls build_fact_table(seed=seed).
            Validates return type: must be (pd.DataFrame, dict).
            On error: formats structured feedback → LLM retry (up to max_retries).
            Timeout: SIGALRM (30s per execution step).
    Output: ExecutionResult(success=True, df=pd.DataFrame, schema_metadata=dict)

      ▼

[3] PHASE 2c — DETERMINISTIC ENGINE (inside FactTableSimulator.generate())
    Input:  FactTableSimulator declarations (categories, measures, temporal, relationships, patterns)
    Module: pipeline/phase_2/fact_table_simulator.py  →  generate()
    Stages:
      β  _build_skeleton(rng)         → builds dimensional cross-join DataFrame
      δ  _sample_measures(df, rng)    → samples marginal distributions
      γ  _apply_conditionals(df, rng) → applies per-category distribution overrides
      λ  _apply_dependencies(df, rng) → evaluates pd.eval() functional formulas
      ψ  _inject_correlations(df, rng)→ Gaussian Copula Pearson correlation injection
      φ  _inject_patterns(df, rng)    → plants narrative-driven statistical anomalies
      ρ  _inject_realism(df, rng)     → missing values, dirty values, censoring
    Output: (pd.DataFrame, schema_metadata dict)
    Supporting modules:
      - pipeline/phase_2/distributions.py  (8 named distribution samplers)
      - pipeline/phase_2/patterns.py       (6 pattern injection handlers)
      - pipeline/phase_2/schema_metadata.py (TypedDict contract definitions)

      ▼

[4] MASTER TABLE WRAPPING
    Input:  (pd.DataFrame, schema_metadata dict)
    Module: pipeline/core/master_table.py  →  MasterTable(df, metadata=schema_metadata)
    Logic:  Star-schema validation (temporal backbone check, categorical column count ≥2, numeric ≥2).
            Logs warnings only; does not raise on soft violations.
    Output: MasterTable dataclass (df + metadata)
            (Note: Phase 3 View Amortization is specified in design docs but not yet implemented in code.)

      ▼

[5] RESULT SERIALIZATION
    Module: pipeline/agpds_runner.py  →  AGPDSRunner.save_results(results, output_dir)
    Outputs:
      - output/agpds/master_tables/<generation_id>.csv       (DataFrame as CSV)
      - output/agpds/schemas/<generation_id>_metadata.json   (SchemaMetadata JSON)
      - output/agpds/charts.json                             (manifest with paths + scenario metadata)
```

### Key Intermediate Data Structures

| Structure | Type | Produced by | Consumed by |
|---|---|---|---|
| `domain_pool.json` | JSON file (dict with `domains: [...]`) | `DomainPool.load_or_build()` | `DomainSampler.__init__()` |
| `domain_context` | `dict` | `DomainSampler.sample()` | `ScenarioContextualizer.generate()` |
| `scenario` | `dict` (6 required fields) | `ScenarioContextualizer.generate()` | `AGPDSPipeline._build_phase2_prompt()` |
| `phase2_user_prompt` | `str` | `_build_phase2_prompt()` | `run_with_retries()` |
| `script` | `str` (Python source) | `LLMClient.generate_code()` | `SandboxExecutor.execute()` |
| `ExecutionResult` | `@dataclass` | `SandboxExecutor.execute()` | `AGPDSPipeline.run_single()` |
| `df` | `pd.DataFrame` | `FactTableSimulator.generate()` | `MasterTable`, CSV writer |
| `schema_metadata` | `dict` (SchemaMetadata TypedDict) | `FactTableSimulator._build_schema_metadata()` | `MasterTable`, JSON writer, Phase 3 (planned) |
| `MasterTable` | `@dataclass` wrapping `pd.DataFrame` | `AGPDSPipeline.run_single()` | Phase 3 (planned) |
| Final `results` list | `list[dict]` | `AGPDSRunner.run_batch()` | `save_results()` |

### Final Output Format and Destination

| Artifact | Format | Path |
|---|---|---|
| Master data (one per generation) | CSV | `output/agpds/master_tables/<gen_id>.csv` |
| Schema metadata (one per generation) | JSON | `output/agpds/schemas/<gen_id>_metadata.json` |
| Generation manifest | JSON array | `output/agpds/charts.json` |

---

## Step 4 — Framework Markdown Inventory

All AGPDS framework markdown files found in the project (excluding `skills/` vendor and `node_modules/`):

| Filename | Path | Description |
|---|---|---|
| `README.md` | `./README.md` | Top-level project README describing the ChartAgentVAGEN repository. |
| `PIPELINE_DOCUMENTATION.md` | `./pipeline/PIPELINE_DOCUMENTATION.md` | Developer documentation for the pipeline module structure and usage. |
| `data_generation_pipeline.md` | `./storyline/data_generation/data_generation_pipeline.md` | Master design document describing the AGPDS paradigm ("LLM-as-Data-Programmer"), design philosophy, 4-phase pipeline overview, Table Amortization principle, and comparison with ChartQA/PlotQA/ChartBench. |
| `phase_0.md` | `./storyline/data_generation/phase_0.md` | Specification for Phase 0 Domain Pool Construction: seed taxonomy, topic/sub-topic LLM prompts, overlap-detection algorithm, JSON output schema (§0.1–0.6), and `DomainSampler` interface. |
| `phase_1.md` | `./storyline/data_generation/phase_1.md` | Specification for Phase 1 Scenario Contextualization: domain sampling, the one-shot scenario instantiation prompt, and scenario-level deduplication strategy. |
| `phase_2.md` | `./storyline/data_generation/phase_2.md` | Core technical specification for Phase 2 Agentic Data Simulator: full `FactTableSimulator` SDK API (§2.1), dimension groups and orthogonality (§2.1.2), LLM code-generation prompt with one-shot example (§2.2), SchemaMetadata output contract (§2.3), execution-error feedback loop (§2.4), deterministic engine stages (§2.5), and three-layer validation + auto-fix (§2.6). |
| `phase_3.md` | `./storyline/data_generation/phase_3.md` | Specification for Phase 3 View Amortization & QA Instantiation: View Extraction Engine with 16 chart type rules, Chart Selection Guide, automated ViewEnumerator, multi-chart Dashboard composition (7 relationship types, 8 composition patterns), and Rule-Based QA generation (intra-view templates, inter-view cross-chart QA, pattern-triggered hard questions). |
| `chart_type_registry.md` | `./storyline/data_generation/chart_type_registry.md` | Meta-configuration layer defining 6 chart families and 16 chart types with structural requirements and QA capabilities. |
| `chartagent_proposal.md` | `./storyline/chartagent_proposal.md` | High-level project proposal document for the ChartAgent research direction. |

---

*[WRITE CONFIRMED] /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/audit/00_codebase_map.md*
