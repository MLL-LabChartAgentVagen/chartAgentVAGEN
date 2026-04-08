# Subtask 2: Domain Pool + Scenario Contextualization — Walkthrough

## What Changed

Implemented Phases 0 and 1 of the AGPDS pipeline, replacing the flat `META_CATEGORIES` list with a structured domain taxonomy and scenario generation system.

### Phase 0 — Domain Pool ([domain_pool.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_0/domain_pool.py))

| Component | Purpose |
|-----------|---------|
| `SEED_TOPICS` | 5 starter industry topics |
| `DomainPool` | LLM-driven taxonomy builder with caching to `domain_pool.json` |
| `DomainSampler` | Stratified without-replacement sampler with 80% exhaustion reset |
| `check_overlap` | TF-IDF char-ngram cosine similarity dedup (Jaccard fallback) |

**Key design**: `check_overlap` uses `sklearn.TfidfVectorizer` with `char_wb` n-grams (2–4) for accurate short-text similarity. This avoids OpenAI embedding API costs while maintaining quality overlap detection.

### Phase 1 — Scenario Contextualizer ([scenario_contextualizer.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_1/scenario_contextualizer.py))

| Component | Purpose |
|-----------|---------|
| `ScenarioContextualizer` | Generates scenario JSON from domain samples (refactored from `NodeA_TopicAgent`) |
| `deduplicate_scenarios` | Reuses `check_overlap` on `data_context` fields |
| `validate_output` | Field checks: types, ranges (target_rows 100–3000), granularity enum, entity/metric counts |

**What was reused from `NodeA_TopicAgent`**: prompt builder + diversity tracker pattern, LLM retry loop, state mutation architecture. **What was replaced**: input/output schemas, validation logic, all prompt content.

---

## Test Results

### Phase 0 — 7/7 passed
| # | Test | Status |
|---|------|--------|
| 1 | Seed topics ≥ 5 | ✓ |
| 2 | `check_overlap` detects similar items | ✓ |
| 3 | `check_overlap` allows distinct items | ✓ |
| 4 | Pool JSON schema (version, IDs, tiers) | ✓ |
| 5 | `DomainSampler` — no repeats | ✓ |
| 6 | `DomainSampler` — complexity filter | ✓ |
| 7 | `DomainSampler` — exhaustion reset | ✓ |

### Phase 1 — 5/5 passed
| # | Test | Status |
|---|------|--------|
| 1 | Prompt contains domain metadata | ✓ |
| 2 | Valid scenario passes validation | ✓ |
| 3 | Invalid scenarios detected (6 cases) | ✓ |
| 4 | `deduplicate_scenarios` removes near-dupes | ✓ |
| 5 | Diversity tracker accumulates state | ✓ |

### Regression — all passed
- `phase_2.tests.test_fact_table_simulator` ✓
- `phase_2.tests.test_validators` ✓

---

## File Tree

```
pipeline/
├── phase_0/
│   ├── __init__.py
│   ├── domain_pool.py
│   └── tests/
│       ├── __init__.py
│       └── test_domain_pool.py
├── phase_1/
│   ├── __init__.py
│   ├── scenario_contextualizer.py
│   └── tests/
│       ├── __init__.py
│       └── test_scenario_contextualizer.py
└── core/
    └── llm_client.py  (unchanged)
```
