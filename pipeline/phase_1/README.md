# Phase 1 — Scenario Contextualization

Phase 1 bridges the real world and the simulation engine. It generates no data — it produces **semantic anchors** (scenario contexts) that constrain Phase 2's data generation to be realistic, diverse, and domain-grounded. Given a single domain sample from Phase 0, the module asks an LLM to instantiate a concrete, named scenario (title, business context, entities, metrics with units and ranges, temporal granularity, target row count) and validates the result against a strict schema. A second entry point deduplicates a batch of scenarios via embedding similarity. The authoritative spec is [storyline/data_generation/phase_1.md](../../storyline/data_generation/phase_1.md).

---

## 1. Overview

**What it is.** A thin, LLM-driven contextualization layer. `ScenarioContextualizer.generate(domain_sample)` takes one Phase 0 domain dict, builds a one-shot user prompt, calls the injected LLM, validates the returned JSON against the 6-field scenario schema, and retries on soft failures. `deduplicate_scenarios(scenarios, threshold)` reuses Phase 0's `check_overlap` to drop near-duplicate scenarios across a batch.

**Position in the pipeline.**

```
phase_0  domain_pool.json
   │
   │ DomainSampler.sample()
   ▼
phase_1  ScenarioContextualizer.generate(domain)   ──►  scenario dict
   │                                                         │
   │ (optional) deduplicate_scenarios(scenarios, 0.85)       │
   ▼                                                         ▼
phase_2  SDK-driven data simulator (consumes scenario_title, key_entities, key_metrics, target_rows, …)
```

Phase 1 is stateless apart from an optional in-memory `diversity_tracker` that accumulates titles/contexts across calls. It is invoked at runtime from [agpds_pipeline.py:11](../agpds_pipeline.py#L11) on every row of the benchmark.

**Design constraint (spec §Chart type isolation):** Phase 1 deliberately makes zero mention of chart types. Real data is born from business needs; charts are projections of data. This decoupling is intentional — do not add visualization hints to the prompt or schema.

---

## 2. Architecture Overview

```
pipeline/phase_1/
├── __init__.py                         # Re-exports ScenarioContextualizer, deduplicate_scenarios,
│                                       #   SCENARIO_SYSTEM_PROMPT, VALID_GRANULARITIES
├── scenario_contextualizer.py          # All logic: prompts, class, validator, dedup
└── tests/
    └── test_scenario_contextualizer.py # 18 unit tests (mocked LLM and embeddings)
```

Everything lives in one file ([scenario_contextualizer.py](scenario_contextualizer.py)) — prompt templates, the class, the validator, and the dedup function. There are no cached artifacts on disk and no config files: validation bounds are encoded in the validator, and prompts are Python string constants.

**Dataflow for a single call:**

```
domain_sample (dict)
  │
  ▼
_build_user_prompt  →  SCENARIO_SYSTEM_PROMPT + filled user prompt
  │
  ▼
llm_client.generate_json(system, user, temperature=1.0)       ◄─── retries up to max_retries times
  │
  ▼
validate_output  →  (is_valid, errors)
  │                       │
  │ valid                 │ invalid & retries exhausted
  ▼                       ▼
scenario dict      scenario dict with "_validation_warnings"  (soft failure)
                   OR ValueError                               (hard failure: non-dict response)
```

**Dataflow for a batch:** `deduplicate_scenarios(list_of_scenarios, threshold)` → extracts `data_context` strings → `check_overlap` (OpenAI embeddings, cosine similarity) → drops the **later** scenario of each flagged pair.

---

## 3. Interfaces

### 3.1 `ScenarioContextualizer`

Defined in [scenario_contextualizer.py:100](scenario_contextualizer.py#L100).

```python
class ScenarioContextualizer:
    def __init__(
        self,
        llm_client,
        diversity_tracker: Optional[dict] = None,
        max_retries: int = 2,
    )

    def generate(self, domain_sample: dict) -> dict

    @staticmethod
    def validate_output(response: dict) -> tuple[bool, list[str]]
```

- `llm_client` must expose `generate_json(system, user, temperature)` returning a parsed dict — satisfied by [pipeline/core/llm_client.py:LLMClient](../core/llm_client.py). The LLM is called at `temperature=1.0` ([scenario_contextualizer.py:153](scenario_contextualizer.py#L153)) and no `max_tokens` is set; rely on the client's default.
- `diversity_tracker` is an in-memory dict with keys `used_titles` and `used_contexts` that `generate()` appends to after every successful (or soft-failed) call. Pass the same dict across a batch to accumulate history; leave it `None` for per-call isolation.
- `max_retries` is the number of **additional** attempts after the first — total LLM calls are `max_retries + 1`.
- On hard failure (the LLM returns a non-dict on every attempt), `generate()` raises `ValueError`. On soft failure (the LLM returns a dict but it never passes `validate_output`), it emits a `warnings.warn(...)` and returns the last dict with an extra `_validation_warnings: list[str]` field.
- `validate_output` is a pure function and safe to call without an LLM — use it as a downstream guard.

### 3.2 `deduplicate_scenarios`

Defined in [scenario_contextualizer.py:269](scenario_contextualizer.py#L269).

```python
def deduplicate_scenarios(
    scenarios: list[dict],
    threshold: float = 0.85,
) -> list[dict]
```

- Computes embedding-based cosine similarity on the `data_context` field of each scenario via [pipeline/phase_0/overlap_checker.py](../phase_0/overlap_checker.py) (`text-embedding-3-small`).
- Drops the **later** scenario of each flagged pair (earlier index wins), preserving input order among survivors.
- Scenarios with empty/missing `data_context` contribute empty strings to the embedding call and may cluster together — pre-filter if you care.
- Default threshold `0.85` is looser than Phase 0's `0.80` because scenario contexts are longer and more varied than topic names.

### 3.3 Module constants

- **`SCENARIO_SYSTEM_PROMPT`** ([scenario_contextualizer.py:23](scenario_contextualizer.py#L23)) — the 8-rule system prompt. Re-export it if you need to tweak prompting from a caller without forking the file.
- **`VALID_GRANULARITIES`** ([scenario_contextualizer.py:95](scenario_contextualizer.py#L95)) — `{"hourly", "daily", "weekly", "monthly", "quarterly", "yearly"}`. Use this to keep downstream validators in sync with the phase-1 contract.

### 3.4 Scenario output schema

Every returned scenario dict has exactly these fields (plus optional `_validation_warnings` on soft failure):

| Field | Type | Constraint | Example |
|---|---|---|---|
| `scenario_title` | `str` | non-empty; time period + org + analytical focus | `"2024 H1 Shanghai Metro Ridership & Operations Log"` |
| `data_context` | `str` | non-empty; WHO / WHY / WHEN | `"Shanghai Transport Commission collected daily ridership …"` |
| `temporal_granularity` | `str` | ∈ `VALID_GRANULARITIES` | `"daily"` |
| `key_entities` | `list[str]` | 3–8 real-world names | `["Line 1 (Xinzhuang–Fujin Rd)", "Line 2 (…)", …]` |
| `key_metrics` | `list[dict]` | 2–5 items, each with `name`, `unit`, `range` | `[{"name": "daily_ridership", "unit": "10k passengers", "range": [5, 120]}, …]` |
| `target_rows` | `int \| float` | 100–3000 | `900` |

`validate_output` enforces every constraint above except the inner structure of `key_metrics` items (checked by Phase 2, not here).

---

## 4. Usage Examples

### 4.1 Single scenario from a Phase 0 sample

```python
from pipeline.core.llm_client import LLMClient
from pipeline.phase_0 import DomainSampler
from pipeline.phase_1 import ScenarioContextualizer

llm = LLMClient(api_key="...", model="gemini-2.5-pro")
sampler = DomainSampler("pipeline/phase_0/domain_pool.json")
ctx = ScenarioContextualizer(llm)

domain = sampler.sample(n=1, complexity="medium")[0]
scenario = ctx.generate(domain)

print(scenario["scenario_title"])
print(scenario["key_metrics"])
```

### 4.2 Batch with shared diversity tracking and dedup

```python
from pipeline.phase_1 import ScenarioContextualizer, deduplicate_scenarios

tracker = {"used_titles": [], "used_contexts": []}
ctx = ScenarioContextualizer(llm, diversity_tracker=tracker, max_retries=2)

scenarios = [ctx.generate(d) for d in sampler.sample(n=20, complexity="medium")]
scenarios = deduplicate_scenarios(scenarios, threshold=0.85)

print(f"Kept {len(scenarios)} scenarios after dedup")
print(f"Accumulated titles: {len(tracker['used_titles'])}")
```

### 4.3 Validating an external scenario without an LLM

```python
from pipeline.phase_1 import ScenarioContextualizer

ok, errors = ScenarioContextualizer.validate_output(candidate_dict)
if not ok:
    raise ValueError(errors)
```

### 4.4 Bulk generation for replayable benchmarks

For large benchmark runs, pre-generate scenarios once and replay them without calling the LLM on every record:

```bash
# Build ~900 scenarios (300 domains × K=3), written to
# pipeline/phase_1/scenario_pool.jsonl
python pipeline/phase_1/build_scenario_pool.py

# Smaller pool (one scenario per domain, ~300 total)
python pipeline/phase_1/build_scenario_pool.py --scenarios-per-domain 1
```

The build script ([build_scenario_pool.py](build_scenario_pool.py)) is resume-safe: rerunning without `--force` skips `(domain_id, k)` pairs already present in the JSONL. Dedup runs once at the end via `deduplicate_scenarios` at `threshold=0.85`.

Then switch the runtime orchestrator into cached mode:

```python
from pipeline.agpds_pipeline import AGPDSPipeline

pipe = AGPDSPipeline(llm, scenario_source="cached")
# Cache hit  → random.choice over the K pre-generated scenarios
# Cache miss → logged warning + live LLM call (safe default)

# Fail loud on miss (for strict reproducibility)
pipe = AGPDSPipeline(llm, scenario_source="cached_strict")
```

Envelope format (one JSON object per line in `scenario_pool.jsonl`):

```json
{
  "domain_id": "dom_027",
  "k": 0,
  "category_id": 3,
  "generated_at": "2026-04-24T12:00:00Z",
  "scenario": { "scenario_title": "...", "data_context": "...", "key_metrics": [...], ... }
}
```

---

## 5. Dependencies & Environment

**Python:** 3.10+ (repo-wide convention).

**Third-party libraries:** none directly — the module only imports `json`, `typing`, and `warnings` from the stdlib. All external I/O is delegated:

| Capability | Delegated to |
|---|---|
| LLM chat completions | injected `llm_client` (see [pipeline/core/llm_client.py](../core/llm_client.py)) |
| Embedding similarity | [pipeline/phase_0/overlap_checker.py](../phase_0/overlap_checker.py) via `check_overlap` (OpenAI `text-embedding-3-small`) |

**Internal dependencies:**

- [pipeline/phase_0/domain_pool.py](../phase_0/domain_pool.py) — `check_overlap` (imported lazily inside `deduplicate_scenarios`) and `DomainSampler` (consumed upstream by callers).
- [pipeline/core/llm_client.py](../core/llm_client.py) — the canonical `generate_json(system, user, temperature)` implementation expected by `ScenarioContextualizer`.

**Environment variables:** Phase 1 itself reads no env vars. The two it depends on transitively:

- `OPENAI_API_KEY` — **required** whenever `deduplicate_scenarios` is called (embeddings go through the OpenAI SDK regardless of which generation LLM you picked).
- `GEMINI_API_KEY` / provider key — required by whichever `LLMClient` you pass in.

**Files on disk:** none written or read by Phase 1. Scenarios are returned as Python dicts; persistence is the caller's responsibility.

---

## 6. Development Conventions

**Run the tests.** From the repo root:

```bash
python -m pipeline.phase_1.tests.test_scenario_contextualizer
```

18 tests cover prompt injection (no stray `{…}` placeholders, every domain field present), schema validation (each required field individually, bounds for entities/metrics/target_rows, all six granularities, empty strings, non-dict inputs), retry behavior (success on attempt 1, success on attempt 2, soft failure with warnings, hard failure via `ValueError`, `max_retries=0` honored), diversity-tracker accumulation, and `deduplicate_scenarios` edge cases. All tests are offline — LLM and embedding calls are mocked via `unittest.mock`.

**Extending the schema.** Schema bounds (`3–8` entities, `2–5` metrics, `100–3000` rows, the six granularities) appear in three places that must be kept in sync: (a) `SCENARIO_SYSTEM_PROMPT`, (b) `validate_output`, and (c) the one-shot example in `SCENARIO_USER_PROMPT_TEMPLATE`. Changing a bound in isolation will silently let the LLM emit values the validator then rejects (triggering retries and wasted tokens). Update all three together.

**Tweaking prompts.** Import `SCENARIO_SYSTEM_PROMPT` and wrap it rather than editing the file when experimenting — the prompt is a public export precisely to enable this. Prompt edits must preserve the "strictly valid JSON with no additional commentary" clause and the one-shot example structure, both relied on by `llm_client.generate_json` for JSON extraction.

**Integration contract.** `agpds_pipeline.py` instantiates `ScenarioContextualizer` once per run and calls `generate()` per row. Do not cache scenarios across runs unless you also deduplicate — the LLM is invoked at `temperature=1.0` and will happily produce near-duplicates within the same topic. Use `deduplicate_scenarios` post-hoc or seed the `diversity_tracker` and reference `used_titles`/`used_contexts` in future prompt engineering.

**Acceptance gates** (from spec §1.2–§1.3):

- Output parses as JSON and has all six required fields.
- `key_entities`: 3–8 items, real-world names (no `"Group A"`-style placeholders) — enforced by the prompt, not the validator.
- `key_metrics`: 2–5 items, each with scientifically correct unit and realistic range.
- `temporal_granularity` ∈ `VALID_GRANULARITIES`.
- `target_rows` ∈ `[100, 3000]`.
- Scenario-level dedup at cosine similarity ≥ 0.85 on `data_context`.
