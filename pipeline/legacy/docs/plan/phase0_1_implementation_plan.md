# Subtask 2: Domain Pool + Scenario Contextualization (Phases 0–1)

## Goal

Replace the flat `META_CATEGORIES` list with a two-level domain taxonomy (Phase 0) and a structured scenario generation prompt (Phase 1). This produces the semantic anchors that constrain Phase 2's data generation to be realistic, diverse, and domain-grounded.

## Dependencies

- **Salvaged [LLMClient](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/generation_pipeline.py#1856-2054)** — already extracted to [llm_client.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/core/llm_client.py) (Priority 1 component)
- **[NodeA_TopicAgent](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/generation_pipeline.py#626-800) skeleton** — architecture pattern (prompt builder + diversity tracker + validator + state updater) from [generation_pipeline.py#L626-L799](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/generation_pipeline.py#L626-L799)
- **Spec references**: [phase_0.md](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/storyline/data_generation/phase_0.md), [phase_1.md](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/storyline/data_generation/phase_1.md)

---

## Proposed Changes

### Phase 0: Domain Pool (`pipeline/phase_0/`)

#### [NEW] [\_\_init\_\_.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_0/__init__.py)

Package init exporting `DomainPool`, `DomainSampler`, `check_overlap`.

#### [NEW] [domain_pool.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_0/domain_pool.py)

The core Phase 0 module. Components:

1. **`SEED_TOPICS`** — hardcoded list of 5 starter topics (Healthcare, Finance, Retail & E-Commerce, Transportation & Logistics, Energy & Utilities) per spec §0.1.

2. **`DomainPool` class** — orchestrator that builds and caches the full domain taxonomy:
   - [__init__(llm_client, pool_path="domain_pool.json")](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/core/llm_client.py#136-140) — stores pool path
   - `load_or_build(n_topics=20, subtopics_per_topic=10)` → `dict` — if `pool_path` exists and is valid, load from cache (idempotent). Otherwise, calls LLM to generate topics then sub-topics, runs overlap detection, assigns `dom_XXX` IDs, and writes the output JSON artifact
   - `_generate_topics(n, existing)` → `list[str]` — calls `LLMClient.generate_json()` with the Topic Generation Prompt (spec §0.2)
   - `_generate_subtopics(topic, n, existing)` → `list[dict]` — calls `LLMClient.generate_json()` with the Sub-topic Generation Prompt (spec §0.3). Each sub-topic has: [name](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/sandbox_executor.py#156-179), `topic`, `complexity_tier`, `typical_entities_hint`, `typical_metrics_hint`, `temporal_granularity_hint`
   - `_assign_ids(domains)` → `list[dict]` — adds `"id": "dom_001"` etc.

3. **`check_overlap(items, threshold=0.80)`** → `list[tuple[str, str, float]]` — embedding-based cosine similarity deduplication (spec §0.4). Implementation options:
   - **Primary**: Use `sentence-transformers` locally (`all-MiniLM-L6-v2`) for fast, free embeddings
   - **Fallback**: If unavailable, use token-overlap Jaccard similarity as a lightweight substitute
   
   > [!IMPORTANT]
   > The spec references `text-embedding-3-small` (OpenAI), but this requires an API call per overlap check. I'll default to local `sentence-transformers` to avoid API costs and latency. If you prefer OpenAI embeddings, let me know.

4. **`DomainSampler` class** — stratified without-replacement sampler (spec §0.6):
   - [__init__(pool_path)](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/core/llm_client.py#136-140) — loads the cached JSON pool
   - [sample(n=1, complexity=None)](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/distributions.py#105-109) → `list[dict]` — samples without replacement, filtered by `complexity_tier`. Resets at 80% exhaustion

5. **Output JSON schema** — matches spec §0.5: `version`, `generated_at`, `total_domains`, `diversity_score`, `complexity_distribution`, `topic_coverage`, `domains[]`

---

### Phase 1: Scenario Contextualization (`pipeline/phase_1/`)

#### [NEW] [\_\_init\_\_.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_1/__init__.py)

Package init exporting `ScenarioContextualizer`, `deduplicate_scenarios`.

#### [NEW] [scenario_contextualizer.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_1/scenario_contextualizer.py)

Refactored from [NodeA_TopicAgent](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/generation_pipeline.py#626-800) skeleton. Keeps orchestration (prompt builder + diversity tracker + validator + LLM call + retry), replaces content.

1. **`SCENARIO_SYSTEM_PROMPT`** — adapted from spec §1.2 (the "Data Simulator Architect" system prompt)
2. **`SCENARIO_USER_PROMPT_TEMPLATE`** — domain metadata injection + one-shot example from spec §1.2

3. **`ScenarioContextualizer` class** — refactored from [NodeA_TopicAgent](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/generation_pipeline.py#626-800):
   - [__init__(llm_client, diversity_tracker=None)](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/core/llm_client.py#136-140) — mirrors NodeA constructor
   - **Reused from NodeA**: prompt construction pattern, diversity tracker dict, LLM retry loop, state mutation flow
   - **Replaced from NodeA**:
     - Input: `domain_sample: dict` (from `DomainSampler`) instead of `category_id + category_name`
     - Output: AGPDS scenario JSON (`scenario_title`, `data_context`, `key_entities`, `key_metrics`, `temporal_granularity`, `target_rows`) instead of NodeA's `semantic_concept` format
     - Validation: structured field checks instead of substring dedup
   - [generate(domain_sample)](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/generation_pipeline.py#1963-2031) → `dict` — builds prompts, calls `LLMClient.generate_json()`, validates output, updates diversity tracker
   - [validate_output(response)](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/generation_pipeline.py#689-727) → `tuple[bool, list[str]]` — checks required fields, value ranges (`target_rows` 100-3000, `temporal_granularity` ∈ valid set, `key_entities` list length 3-8, `key_metrics` list length 2-5)

4. **`deduplicate_scenarios(scenarios, threshold=0.85)`** → `list[dict]` — reuses `check_overlap` from Phase 0 on `data_context` fields (spec §1.3)

---

### Tests

#### [NEW] [test_domain_pool.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_0/tests/test_domain_pool.py)

| # | Test | Description |
|---|------|-------------|
| 1 | Seed topics present | `SEED_TOPICS` has ≥5 entries |
| 2 | `check_overlap` detects dupes | Passes known-similar strings, verifies high cosine similarity |
| 3 | `check_overlap` allows distinct | Passes dissimilar strings, verifies no overlaps returned |
| 4 | Domain pool JSON schema | Load a mini pool JSON, verify output schema (version, domains[], IDs) |
| 5 | `DomainSampler` basic | Sample 3 domains, verify no repeats, correct structure |
| 6 | `DomainSampler` complexity filter | Sample with `complexity="complex"`, verify all returned are complex |
| 7 | `DomainSampler` exhaustion reset | Exhaust 80%+ of pool, verify reset and continued sampling |

> [!NOTE]
> Tests 1-7 use a pre-built mini pool JSON fixture (no LLM calls). LLM-dependent pool building is tested via a mock or a separate integration test.

#### [NEW] [test_scenario_contextualizer.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_1/tests/test_scenario_contextualizer.py)

| # | Test | Description |
|---|------|-------------|
| 1 | Prompt construction | Verify system/user prompts contain domain metadata |
| 2 | Output validation (valid) | Pass a well-formed scenario dict, verify passes |
| 3 | Output validation (invalid) | Missing fields, out-of-range values — verify errors |
| 4 | `deduplicate_scenarios` | Pass near-duplicate `data_context` strings, verify dedup |
| 5 | Diversity tracker update | After [generate()](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/generation_pipeline.py#1963-2031), verify tracker records used scenario titles |

---

## File Tree Summary

```
pipeline/
├── phase_0/
│   ├── __init__.py
│   ├── domain_pool.py          # DomainPool, DomainSampler, check_overlap
│   └── tests/
│       └── test_domain_pool.py  # 7 tests
├── phase_1/
│   ├── __init__.py
│   ├── scenario_contextualizer.py  # ScenarioContextualizer, deduplicate_scenarios
│   └── tests/
│       └── test_scenario_contextualizer.py  # 5 tests
└── core/
    └── llm_client.py            # (existing, no changes)
```

---

## Verification Plan

### Automated Tests
```bash
conda activate chart
cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline
python -m phase_0.tests.test_domain_pool
python -m phase_1.tests.test_scenario_contextualizer
```

### Regression
```bash
python -m phase_2.tests.test_fact_table_simulator
python -m phase_2.tests.test_sandbox_executor
python -m phase_2.tests.test_validators
```

### Manual Verification
- Inspect the generated `domain_pool.json` artifact for realistic domain coverage
- Verify scenario JSON outputs are grounded in domain metadata
