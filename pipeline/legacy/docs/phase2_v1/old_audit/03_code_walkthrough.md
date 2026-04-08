---
title: "AGPDS Code Walkthrough — Module-by-Module Guided Tour"
date: 2026-03-04
modules_covered:
  - pipeline/core/utils.py
  - pipeline/core/llm_client.py
  - pipeline/core/master_table.py
  - scripts/build_domain_pool.py
  - pipeline/phase_0/domain_pool.py
  - pipeline/phase_1/scenario_contextualizer.py
  - pipeline/phase_2/schema_metadata.py
  - pipeline/phase_2/distributions.py
  - pipeline/phase_2/patterns.py
  - pipeline/phase_2/fact_table_simulator.py
  - pipeline/phase_2/sandbox_executor.py
  - pipeline/phase_2/validators.py
  - pipeline/agpds_pipeline.py
  - pipeline/agpds_runner.py
total_sections: 16
---

# AGPDS Code Walkthrough

> A guided tour of every module in the AGPDS pipeline, written for the author
> to return to months later and immediately re-orient. Each section explains
> not just *what* the code does, but *why* it does it that way.

---

## Module 1 — Shared Constants & Helpers (`pipeline/core/utils.py`)

### Purpose in the Pipeline

Provides the 30-category taxonomy list (`META_CATEGORIES`) and lightweight ID-generation / category-lookup helpers used by the CLI runner. Think of this as the "reference card" that the rest of the pipeline imports when it needs to map a numeric `category_id` to a human-readable label.

### Key Design Decisions

#### `META_CATEGORIES` (file:19–50)
- **What:** A flat Python list of 30 strings like `"1 - Media & Entertainment"`.
- **Why a flat list instead of a dict or enum?** Simplicity. The category is selected by 1-based integer index (`META_CATEGORIES[category_id - 1]`), so a list gives O(1) lookup with minimal code. The numeric prefix baked into each string is a display convenience — it lets printed output be self-labelling.
- **Assumption:** `category_id` is always 1–30. The runner's argparse constrains this (`choices=range(1, 31)`), but `get_category_by_id()` at line 69 adds a guard returning `None` for out-of-range inputs. No other module enforces this range.

#### `generate_unique_id()` (file:57–61)
- **What:** Produces IDs like `gen_20260304_194500_a1b2c3`.
- **Why MD5 of `random.random()`?** It's a quick-and-dirty way to get 6 hex chars of uniqueness without importing `uuid`. The timestamp prefix ensures human-sortable chronological ordering; the random suffix prevents collisions when two generations start in the same second.

### Data Structures Explained

| Element | Type | Where Used |
|---------|------|------------|
| `META_CATEGORIES` | `list[str]` of length 30 | `agpds_runner.py:28` for display; `agpds_runner.py:122` for cycling category IDs |

### AGPDS Connection

`META_CATEGORIES` is a **legacy artifact** from the pre-AGPDS `generation_pipeline.py`. In the current AGPDS pipeline, the `category_id` is only used for logging and for cycling through categories in batch mode — it does **not** drive domain selection (that's `DomainSampler`'s job). The spec documents (`phase_0.md`) describe a dynamically generated taxonomy, so this static list is essentially a display label, not a semantic input.

### Gotchas & Subtleties

1. **`category_id` is 1-indexed** — `META_CATEGORIES[0]` corresponds to `category_id=1`. An off-by-one bug here would silently select the wrong category label.
2. **`generate_unique_id` is non-deterministic** — it mixes `datetime.now()` and `random.random()`, so the same script run twice will produce different IDs. This is intentional for uniqueness but means outputs are never bit-for-bit reproducible at the *naming* level, even if the data itself is seed-deterministic.

---

## Module 2 — Unified LLM Client (`pipeline/core/llm_client.py`)

### Purpose in the Pipeline

The single gateway through which every LLM call in the pipeline flows. It abstracts away provider differences (OpenAI, Gemini via OpenAI SDK, Gemini native SDK, Azure) so that callers just write `llm.generate_json(system=..., user=...)` without worrying about parameter naming, token limits, or JSON mode availability.

### Key Design Decisions

#### `ProviderCapabilities` dataclass (file:24–43)
- **What:** A configuration object declaring what each LLM provider supports (temperature? max_tokens? JSON mode?).
- **Why a dataclass instead of ad-hoc if/else?** This is the **Strategy pattern** — each provider's quirks are encoded in data, not in branching logic. Adding a new provider means adding one entry to `PROVIDER_CAPABILITIES` (file:47–81), not modifying control flow. This matters because LLM APIs are a moving target; models like `o1` and `o3` don't support temperature at all (file:86–107), and the `ProviderCapabilities` for those overrides cleanly capture this.

#### `ParameterAdapter.adapt_parameters()` (file:141–184)
- **Inputs:** Raw `messages`, `temperature`, `max_tokens`, `response_format`.
- **Outputs:** `(kwargs, modified_messages)` — a ready-to-use API call dict.
- **Why return modified messages?** Some providers (Gemini) don't support JSON mode natively, so the adapter appends `"Respond with valid JSON only"` to the user message (file:180–182). This lets `generate()` stay generic — it just passes through what the adapter returns.

#### `LLMClient.generate()` (file:287–347)
- **The central dispatch:** Two code paths — `gemini-native` (uses `google.genai` SDK, file:312–330) and everything else (uses OpenAI SDK, file:331–347).
- **Why two paths?** The `google-genai` native SDK uses a fundamentally different API shape (`generate_content` with a flat prompt string) vs. OpenAI's `chat.completions.create` with a messages array. The OpenAI SDK *can* call Gemini via the compatibility endpoint (`generativelanguage.googleapis.com/v1beta/openai/`), but the native SDK offers features the compatibility layer doesn't.
- **Lazy initialization** (`_ensure_client`, file:262–285): The SDK import only happens on first use. This avoids an `ImportError` at import time if the user hasn't installed all SDKs — they only need the one for their chosen provider.

#### `generate_json()` (file:349–369) and `generate_code()` (file:371–392)
- Convenience wrappers. `generate_json` adds `response_format="json"`, strips markdown fences, and `json.loads()` the result. `generate_code` similarly strips ` ```python ``` ` fences.

### Data Structures Explained

| Structure | Fields | Purpose |
|-----------|--------|---------|
| `ProviderCapabilities` | `supports_temperature`, `supports_max_tokens`, `token_param_name`, `requires_json_in_prompt`, etc. | Encodes what API params each provider accepts |
| `PROVIDER_CAPABILITIES` dict | Keys: `"openai"`, `"gemini"`, `"gemini-native"`, `"azure"`, `"custom"` | Provider → capabilities lookup |
| `MODEL_OVERRIDES` dict | Keys: `"o1"`, `"o3"`, `"gpt-5"` | Model-specific overrides (e.g., reasoning models don't support temperature) |

### AGPDS Connection

The LLM client is used in **three** phases:
- **Phase 0:** `DomainPool._generate_topics()` and `_generate_subtopics()` call `llm.generate_json()`.
- **Phase 1:** `ScenarioContextualizer.generate()` calls `llm.generate_json()`.
- **Phase 2a:** `run_with_retries()` calls `llm.generate_code()`.

The spec says *"LLM is called only in Phases 0–2. Phase 3 is entirely deterministic."* The code respects this — no Phase 3 module imports `LLMClient`.

### Gotchas & Subtleties

1. **`generate_code` fence-stripping regex** (file:387–390) requires `\n` after the opening backticks. If the LLM outputs ` ```python def build...` on one line, the fence won't be stripped. [Audit A4-3]
2. **`gemini-native` passes a plain `dict` as `config`** (file:327) — the SDK may expect a typed `GenerateContentConfig`. This works in practice but is technically undocumented behavior.
3. **`supports_max_completion_tokens`** is declared but never actually read by `adapt_parameters()` — the code uses `token_param_name` instead. It's dead code. [Audit A4-4]

---

## Module 3 — MasterTable Wrapper (`pipeline/core/master_table.py`)

### Purpose in the Pipeline

Wraps a `pd.DataFrame` + metadata dict into a `@dataclass` with basic star-schema validation. This is the **handoff container** from Phase 2 to Phase 3 (and to result serialization). Think of it as a "typed envelope" — it ensures the data meets minimum structural requirements before downstream processing.

### Key Design Decisions

#### `MasterTable.__post_init__` → `validate_schema()` (file:21–59)
- **What it checks:** (1) DataFrame not empty, (2) at least one temporal-looking column, (3) at least 2 categorical columns, (4) at least 2 numeric columns.
- **Why warnings instead of errors?** The validation is **soft** — it `logger.warning()`s rather than raising exceptions for insufficient columns (file:44, 52, 57). This is a conscious trade-off: Phase 2's output might technically violate the star-schema ideal (e.g., one numeric column), but crashing the whole pipeline over it would be worse than logging a warning and letting Phase 3 decide what's viable.
- **Temporal detection heuristic** (file:35–39): If no datetime-typed column exists, it falls back to checking column *names* for substrings like `date`, `time`, `year`. This is fragile — a column named `update_count` would match `date` inside `update`. But `FactTableSimulator` always produces a proper datetime column, so in practice this heuristic is only hit with manually-constructed DataFrames.

#### `to_legacy_chart_entry()` (file:76–146)
- **Why it exists:** Bridges AGPDS data into the legacy `generation_pipeline.py` chart format. It's an adapter pattern — the old chart drawing functions expect dicts with keys like `bar_labels`, `bar_data`, `bar_colors`.
- **Current status:** Not called in the AGPDS pipeline. It's a planned Phase 3 bridge or a leftover from the salvage operation.

### AGPDS Connection

`MasterTable` is instantiated at `agpds_pipeline.py:117`:
```python
mt = MasterTable(df, metadata=schema_metadata)
```
But the `mt` object is **never used after construction** — the pipeline returns `df.to_csv()` and `schema_metadata` directly. The `MasterTable` wrapper exists to enforce the validation side-effect in `__post_init__`, but the validated object itself is discarded. This is potentially wasteful but harmless.

### Gotchas & Subtleties

1. **The `mt` variable is created but never referenced again** — validation runs as a side-effect. If you refactor to remove this line, you lose the validation warnings silently.
2. **`from_csv()` strips column name whitespace** (file:67) — a defensive measure against CSVs with trailing spaces in headers, which can cause subtle key-miss bugs downstream.

---

## Module 4 — Build Domain Pool Script (`scripts/build_domain_pool.py`)

### Purpose in the Pipeline

A **one-shot offline script** that must be run before the pipeline can execute. It reads `metadata/taxonomy_seed.json`, invokes `DomainPool.load_or_build()` (which calls the LLM to generate subtopics), and writes `metadata/domain_pool.json`. This is the "pre-bake" step — it's slow (many LLM calls) but only needs to happen once.

### Key Design Decisions

#### `load_api_key()` (file:72–99)
- **Why manual `.env` parsing as fallback?** (file:82–88) If `python-dotenv` isn't installed, the script manually parses `KEY=VALUE` lines from `.env`. This means the script works in minimal environments without extra dependencies.

#### `sys.path.insert(0, str(PROJECT_ROOT))` (file:135)
- **Why?** The script lives in `scripts/`, but it imports from `pipeline.core.llm_client` and `pipeline.phase_0.domain_pool`. Without adding the project root to `sys.path`, Python won't find these packages because `scripts/` is the working directory. This is a common pattern for standalone scripts in a package that isn't installed via `pip install -e .`.

#### `pool_builder.load_or_build(force=args.force)` (file:158–161)
- **Idempotent by default:** Without `--force`, if `domain_pool.json` already exists, the script exits early (file:118–127). With `--force`, it regenerates. This prevents accidental LLM cost from re-running the script.

### AGPDS Connection

Implements the offline portion of **Phase 0: Domain Pool Construction** (`phase_0.md`). The spec describes this as a one-time batch process that produces a cached JSON pool. The script faithfully follows this design — build once, sample many times.

### Gotchas & Subtleties

1. **Default model is `gemini-2.0-flash-lite`** (file:67) — this is the cheapest/fastest Gemini model, appropriate for bulk subtopic generation. The runner's default (`gemini-3.1-pro-preview`) doesn't match and doesn't exist. [Audit A4-1]
2. **The `n_topics` parameter in `load_or_build()` is effectively ignored** when `seed_path` is provided (see `DomainPool._build()` line 256–259) — the script always uses all topics from the seed file.

---

## Module 5 — Domain Pool & Sampler (`pipeline/phase_0/domain_pool.py`)

### Purpose in the Pipeline

Two components in one file:
1. **`DomainPool`** (lines 190–397): The *builder* — calls the LLM to generate topics and subtopics, deduplicates them, and saves the pool as JSON. Used offline by `build_domain_pool.py`.
2. **`DomainSampler`** (lines 404–457): The *runtime consumer* — loads the pre-built pool and provides without-replacement sampling. Used at runtime by `AGPDSPipeline`.

### Key Design Decisions

#### `check_overlap()` with TF-IDF fallback to Jaccard (file:115–183)
- **What:** Detects near-duplicate topics/subtopics by computing pairwise similarity.
- **Why TF-IDF with `char_wb` n-grams?** (file:150–152) Short text like topic names ("ICU bed turnover analytics") has few word tokens. Character n-grams (`ngram_range=(2, 4)`) capture partial word overlaps better than word-level TF-IDF. `char_wb` respects word boundaries, avoiding spurious matches across word interiors.
- **Why Jaccard fallback?** (file:166–183) If `sklearn` isn't installed, the system degrades gracefully to a simpler token-level Jaccard similarity. This keeps the module testable without heavy ML dependencies.
- **[NOTE: spec divergence]** The spec (`phase_0.md §0.4`) calls for embedding similarity via `text-embedding-3-small`. The implementation uses TF-IDF instead — functionally equivalent for deduplication but algorithmically different. This was flagged in audit 02 as P0-3 (PARTIAL).

#### `DomainPool._build()` (file:248–313)
- **Flow:** Load seeds → optionally expand with LLM → dedup topics → for each topic: generate subtopics via LLM → dedup within topic → assign IDs → build output dict.
- **`_compute_diversity()`** (file:360–380): Uses normalized Shannon entropy over complexity tiers. A diversity score of 1.0 means perfect balance across `simple`/`medium`/`complex`; 0.0 means all subtopics are the same tier. This is a simple but effective diversity metric.
- **`_assign_ids()`** (file:353–358): Sequential `dom_001`, `dom_002`, … IDs. These are stable within a single build but will change if the pool is rebuilt with different LLM output.

#### `DomainSampler.sample()` (file:420–452)
- **Without-replacement sampling:** Uses `random.sample()` on candidates not in `used_ids` (file:450).
- **Reset logic** (file:442–448): The comment says "Reset at 80% exhaustion" but the code checks `len(candidates) < n` — effectively 100% exhaustion when `n=1`. This is a known spec divergence. [Audit A3-3]
- **`complexity` filter** (file:436–440): Optional stratification — you can request only `"medium"` domains, for instance.

### Data Structures Explained

#### Domain Pool JSON (`metadata/domain_pool.json`)
```json
{
  "version": "1.0",
  "generated_at": "2026-03-04T01:20:00+00:00",
  "total_domains": 210,
  "diversity_score": 0.97,
  "complexity_distribution": {"simple": 70, "medium": 70, "complex": 70},
  "topic_coverage": {"Healthcare": 7, "Finance": 7, ...},
  "domains": [
    {
      "id": "dom_001",
      "name": "ICU bed turnover analytics",
      "topic": "Healthcare",
      "complexity_tier": "complex",
      "typical_entities_hint": ["hospitals", "ICU units"],
      "typical_metrics_hint": [{"name": "occupancy_rate", "unit": "%"}],
      "temporal_granularity_hint": "daily"
    },
    ...
  ]
}
```

### AGPDS Connection

Implements **Phase 0: Domain Pool Construction** (`phase_0.md §0.1–0.6`). The spec says: *"LLM batch-generates 200+ fine-grained domains across 15+ topics. Embedding-based dedup + complexity balancing → typed JSON pool."* The code produces this pool; the only divergence is the dedup algorithm (TF-IDF vs. embeddings).

### Gotchas & Subtleties

1. **`DomainSampler` and `DomainPool` are decoupled** — the sampler only reads the JSON file; it never calls the LLM. If the pool file is missing, the pipeline crashes with `FileNotFoundError` from `AGPDSPipeline.__init__()`.
2. **`_generate_subtopics()` uses `item.setdefault("topic", topic)`** (file:349) — this ensures every subtopic has its parent topic field even if the LLM omits it, preventing downstream `KeyError`.
3. **The `SEED_TOPICS` constant** (file:29–35) is a hardcoded fallback of 5 topics, used only when no `seed_path` is provided. In production, the seed file has 30 topics, making this constant effectively dead code.

---

## Module 6 — Scenario Contextualizer (`pipeline/phase_1/scenario_contextualizer.py`)

### Purpose in the Pipeline

Bridges the abstract domain sample (from Phase 0) into a concrete, realistic scenario that Phase 2's LLM can use to write a data generation script. The output is a structured dict with specific entities, metrics, temporal ranges, and row counts.

### Key Design Decisions

#### System + User Prompts (file:23–88)
- **`SCENARIO_SYSTEM_PROMPT`** (file:23–43): 8 rules constraining the LLM's output — entity count 3–8, metrics 2–5, target_rows 100–3000, etc. These exact ranges are enforced by `validate_output()`.
- **`SCENARIO_USER_PROMPT_TEMPLATE`** (file:45–88): Includes a **one-shot example** (Shanghai Metro ridership) showing the expected output format. The template uses `{domain_json}` injection — the domain metadata from Phase 0 is serialized as JSON and dropped verbatim into the prompt.
- **Why one-shot instead of zero-shot?** LLMs produce much more reliable structured output when shown a concrete example. The Shanghai Metro example is intentionally detailed (real line names and numbers, specific date range, plausible metric ranges) to set the tone for "realistic, grounded" scenarios. This is the spec's explicit requirement: *"Use real-world names — never generic placeholders."*

#### `ScenarioContextualizer.generate()` (file:131–176)
- **Retry loop** (file:149–161): Up to `max_retries + 1` attempts (default: 3 total). Each attempt calls `llm.generate_json()` and validates.
- **Soft failure** (file:163–176): If all retries fail validation, the last response is returned anyway with a `warnings.warn()`. This prevents a single bad LLM response from crashing a batch of 100 generations. **However**, the caller cannot distinguish soft-failure from success — the returned dict may be missing required fields. [Audit A3-4]

#### `validate_output()` (file:183–252)
- **Static method** — can be called without a `ScenarioContextualizer` instance, making it easy to test.
- **Checks:** Required fields, entity count range, metric count range, granularity enum membership, target_rows numeric and in [100, 3000], non-empty title and context.

#### `deduplicate_scenarios()` (file:268–294)
- **Uses `check_overlap()` from Phase 0** — applies it to `data_context` strings across a batch.
- **[NOTE: spec divergence]** The import at file:283 uses `from phase_0.domain_pool import check_overlap` — this is a **broken import path** that will raise `ModuleNotFoundError`. Should be `from pipeline.phase_0.domain_pool import check_overlap`. [Audit A2-6]
- **Never called** — the function exists but `AGPDSPipeline` never invokes it. It's an unused utility for potential post-batch deduplication.

### Data Structures Explained

#### Scenario Dict (output of `generate()`)
```json
{
  "scenario_title": "2024 H1 Shanghai Metro Ridership & Operations Log",
  "data_context": "Shanghai Transport Commission collected daily ridership...",
  "key_entities": ["Line 1", "Line 2", "Line 8", "Line 9", "Line 10"],
  "key_metrics": [
    {"name": "daily_ridership", "unit": "10k passengers", "range": [5, 120]},
    {"name": "on_time_rate", "unit": "%", "range": [85.0, 99.9]}
  ],
  "temporal_granularity": "daily",
  "target_rows": 900
}
```

#### Diversity Tracker (internal)
```python
{"used_titles": ["title1", ...], "used_contexts": ["context1", ...]}
```
Accumulated across calls to track what's been generated. Currently used for logging only — no dedup logic reads it at runtime.

### AGPDS Connection

Implements **Phase 1: Scenario Contextualization** (`phase_1.md §1.2–1.3`). The spec says: *"Phase 1 deliberately makes zero mention of chart types."* The code is compliant — the word "chart" never appears in the prompts or output schema. This is the *"single most important design decision"* per the spec.

### Gotchas & Subtleties

1. **`temperature=1.0`** (file:153) — higher than the default 0.7, deliberately encouraging creative/diverse scenarios.
2. **The `diversity_tracker` is per-instance** — if you create a new `ScenarioContextualizer` for each call, the tracker resets. `AGPDSPipeline` reuses one instance (file:49), so tracking works within a session but not across separate runs.
3. **`warnings.warn()` on soft failure** (file:165) — these warnings go to stderr and are easy to miss in production logs. Consider structured logging instead.

---

## Module 7 — Schema Metadata TypedDicts (`pipeline/phase_2/schema_metadata.py`)

### Purpose in the Pipeline

Defines the **formal contract** between Phase 2 (data generation) and Phase 3 (view amortization). These `TypedDict` definitions serve as documentation and enable IDE type-checking — they don't enforce types at runtime (Python `TypedDict` is a static-analysis construct only).

### Key Design Decisions

#### Why `TypedDict` instead of `@dataclass`? (file:10–83)
`TypedDict` is used because `SchemaMetadata` is consumed as a plain `dict` everywhere — serialized to JSON, passed as kwargs, merged with overrides in the validator. A `@dataclass` would require `.asdict()` conversions at every boundary. `TypedDict` gives you type safety in the editor without changing the runtime representation.

#### `total=False` on several classes (file:10, 34, 48, 55, 69)
`total=False` means all fields are optional. This is necessary because the metadata is built incrementally — `_build_schema_metadata()` only includes fields that were declared (e.g., if no dependencies exist, `dependencies` is an empty list, not absent — but the TypedDict flexibility allows for future partial emission).

#### `PatternMeta` has both nested and flat fields (file:55–66)
`PatternMeta` defines `params: Optional[dict]` **and** top-level fields like `break_point`, `magnitude`, `z_score`. This dual layout exists because `_build_schema_metadata()` currently flattens params via `dict.update()` (putting them at top level), while the spec intends them nested under `params`. The TypedDict documents both layouts. [Audit A1-2, CRITICAL]

### Data Structures Explained

| TypedDict | Fields | Used By |
|-----------|--------|---------|
| `ColumnMeta` | `name`, `type`, `group`, `parent`, `cardinality`, `declared_dist`, `declared_params` | `_build_schema_metadata()`, validators, Phase 3 |
| `DimensionGroupMeta` | `columns`, `hierarchy` | Phase 3 `ViewEnumerator` |
| `SchemaMetadata` | 8 top-level keys: `dimension_groups`, `orthogonal_groups`, `columns`, `conditionals`, `correlations`, `dependencies`, `patterns`, `total_rows` | The complete Phase 2 → Phase 3 contract |

### AGPDS Connection

Directly implements **§2.3 SchemaMetadata Output Contract** from `phase_2.md`. The spec defines 8 required keys — the TypedDict matches. **[NOTE: spec divergence]** The `columns` entries lack a `role` field (`primary`/`secondary`/`orthogonal`/`temporal`/`measure`) that Phase 3's `ViewEnumerator` expects. [Audit B1, BLOCKER]

---

## Module 8 — Distribution Samplers (`pipeline/phase_2/distributions.py`)

### Purpose in the Pipeline

A unified interface for sampling from 8 named probability distributions. Called by `FactTableSimulator._sample_measures()` and `_apply_conditionals()` to populate measure columns.

### Key Design Decisions

#### Dispatch table pattern (file:163–172)
`_SAMPLERS` maps distribution name → sampler function. `sample_distribution()` at file:51 simply does `_SAMPLERS[dist_name](params, n, rng)`. This is the **table-driven dispatch** pattern — adding a new distribution means writing one function and one dict entry.

#### `_apply_scale()` (file:38–48)
Linear min-max rescaling to a `[low, high]` range. If all values are identical (`raw_max == raw_min`), it returns the midpoint to avoid division by zero. This is important because some distributions (e.g., Poisson with `lam=0`) can produce all-zero arrays.

#### `_sample_mixture()` (file:133–160)
Nested dispatch — each component is sampled by calling back into `_SAMPLERS`. **Nested mixtures are explicitly rejected** (file:153) to prevent infinite recursion.

### AGPDS Connection

Implements the 8 distributions listed in **§2.1.1** of `phase_2.md`. All 8 are present: `gaussian`, `lognormal`, `gamma`, `beta`, `uniform`, `poisson`, `exponential`, `mixture`. [Audit P2-2: COMPLIANT]

### Gotchas & Subtleties

1. **`_validate_positive` checks `<= 0`** (file:21) — this rejects zero, which is correct for `sigma` and `scale` but means you can't have a Poisson with `lam=0` (degenerate case that always returns 0). Edge case but worth knowing.
2. **`lognormal` uses NumPy's parameterization** — `rng.lognormal(mu, sigma)` where `mu` and `sigma` are the mean and std of the *underlying normal*, not the lognormal itself. This catches many people off guard.

---

## Module 9 — Pattern Injection (`pipeline/phase_2/patterns.py`)

### Purpose in the Pipeline

Plants **narrative-driven statistical anomalies** into the DataFrame — the kind of patterns that make interesting chart QA questions ("Why did revenue spike in Q3?"). Each pattern modifies a subset of rows in-place.

### Key Design Decisions

#### 6 pattern handlers, each a standalone function (file:73–304)

| Pattern | What It Does | Key Params |
|---------|-------------|------------|
| `outlier_entity` | Scales filtered entity to `z_score` SDs above the non-target mean | `z_score` |
| `trend_break` | Multiplies values by `(1 + magnitude)` after a date breakpoint | `break_point`, `magnitude` |
| `ranking_reversal` | Boosts entity so its rank on m2 inverts vs its rank on m1 | `metrics: [m1, m2]` |
| `dominance_shift` | Swaps which entity is dominant before/after the temporal midpoint | `magnitude` |
| `convergence` | Linearly reduces the gap between top and bottom entities over time | `convergence_rate` |
| `seasonal_anomaly` | Adds sinusoidal seasonality, then inverts it for the target entity | `amplitude`, `period_days` |

#### `_evaluate_target()` helper (file:63–68)
All patterns that accept a `target` string evaluate it via `df.eval(target)`. This lets LLM-generated code write things like `target="hospital == 'St. Mary's'"` — a pandas query expression. The helper validates that the result is boolean, catching cases where the LLM writes a non-boolean expression.

#### `outlier_entity` baseline calculation (file:98–102)
Statistics (mean, std) are computed from **non-target rows** (`~mask`). This prevents a feedback loop where boosting the target inflates the global mean, reducing the effective z-score.

### AGPDS Connection

Implements the 6 pattern types from **§2.1.1** of `phase_2.md`. All 6 are present. [Audit P2-3: COMPLIANT] Phase 3's `PatternDetector` is designed to detect exactly these 6 patterns for QA generation.

### Gotchas & Subtleties

1. **`ranking_reversal`** (file:189) divides by `means.loc[top_m1_entity, m2]` — if that value is 0 or negative, the `boost_factor` calculation falls through to `2.0`, which may not produce a convincing reversal.
2. **`seasonal_anomaly`** modifies ALL rows (adds seasonal to everyone, file:297), then subtracts 2× the seasonal for the target (file:302). The net effect: non-target entities get `+sin`, target entities get `-sin`. This creates a detectable anti-phase signal.
3. **All patterns operate in-place** on the DataFrame — the returned `df` is the same object. This is fine for the current pipeline but means calling a pattern twice on the same data will compound the effect.

---

## Module 10 — FactTableSimulator SDK (`pipeline/phase_2/fact_table_simulator.py`)

### Purpose in the Pipeline

The **core SDK** that LLM-generated scripts call to declare schemas and generate data. It's a fluent builder API: you chain `.add_category()`, `.add_measure()`, etc., then call `.generate()` to produce `(DataFrame, SchemaMetadata)`.

### Key Design Decisions

#### Two-phase API with freeze guard (file:68–69, 1012–1024)
- **Step 1** methods (`add_category`, `add_measure`, `add_temporal`) declare columns.
- **Step 2** methods (`add_conditional`, `add_dependency`, `add_correlation`, `declare_orthogonal`, `inject_pattern`, `set_realism`) declare relationships.
- Calling a Step 1 method after any Step 2 method raises `RuntimeError`.
- **Why?** The 7-stage engine assumes all columns exist before relationships are applied. Without this guard, an LLM could declare a measure *after* a correlation that references it, causing a `KeyError` during generation.

#### `generate()` — The 7-stage engine (file:496–530)
The stages run in a fixed order, using Greek-letter labels matching the spec:

| Stage | Symbol | Method | Purpose |
|-------|--------|--------|---------|
| 1 | β | `_build_skeleton()` | Cross-join categorical groups, tile to `target_rows`, add temporal |
| 2 | δ | `_sample_measures()` | Sample marginal distributions for each measure |
| 3 | γ | `_apply_conditionals()` | Override measure values per-category |
| 4 | λ | `_apply_dependencies()` | Evaluate `pd.eval()` functional formulas |
| 5 | ψ | `_inject_correlations()` | Gaussian Copula Pearson correlation injection |
| 6 | φ | `_inject_patterns()` | Plant statistical anomalies |
| 7 | ρ | `_inject_realism()` | Missing values, dirty values, censoring |

**Why this order matters:** Correlations (ψ) must come after measures are sampled (δ) and conditionals applied (γ), because the copula operates on the final measure distributions. Patterns (φ) come after correlations because they intentionally disrupt the statistical regularities. Realism (ρ) is last because missing-value injection should affect the final data, not be overwritten by subsequent stages.

#### `_build_skeleton()` cross-join logic (file:536–579)
Groups are cross-joined to create all dimensional combinations. If there are 5 hospitals × 3 departments = 15 combinations, and `target_rows=500`, the skeleton tiles these 15 rows ~34 times, then truncates to exactly 500. The temporal column is sampled independently (random dates, not sequential), which produces a realistic "event log" pattern where not every entity has a record on every date.

#### Gaussian Copula correlation injection (file:756–829)
The algorithm: (1) rank each column → uniform margins, (2) transform to normal via inverse CDF, (3) apply Cholesky decomposition with the target 2×2 correlation matrix, (4) transform back to uniform → back to original marginals via rank-back. This preserves the original marginal distributions while inducing the desired Pearson correlation. **[NOTE: spec divergence]** When `target_r = ±1.0`, the correlation matrix is singular and `np.linalg.cholesky` will fail. [Audit A2-8]

#### `_build_schema_metadata()` (file:917–1006)
Converts internal specs into the `SchemaMetadata` dict. **Key issues:**
- `patterns` are flattened via `pat_entry.update(p["params"])` at line 990 — this can overwrite `type`/`col`/`target` keys. [Audit A1-2, CRITICAL]
- `dependencies` omit `noise_sigma`. [Audit A1-1, WARNING]
- `total_rows` uses `self.target_rows` (declared), not `len(df)` (actual). [Audit A1-3, WARNING]
- `columns` entries lack a `role` field needed by Phase 3. [Audit B1, BLOCKER]

### AGPDS Connection

Implements **Phase 2: Agentic Data Simulator** (`phase_2.md §2.1–2.5`). The SDK API, 7-stage engine, and distribution/pattern support all match the spec. The spec's *"ATOMIC_GRAIN: each row = one indivisible event"* is enforced by the skeleton builder — each row is a unique dimensional combination with independent measure samples.

### Gotchas & Subtleties

1. **`inject_pattern` parameter named `type`** (file:420) shadows Python's built-in `type` function. Safe now but a maintenance hazard. [Audit A2-7]
2. **Child columns are sampled independently of parents** (file:636–643) — `P(department | hospital)` is NOT enforced. The parent link is structural, not statistical. [Audit A2-4]
3. **`add_temporal` normalizes frequency aliases** (file:221–230) — `"daily"` → `"D"`, `"M"` → `"ME"`, etc. This silently handles many LLM hallucinations.

---

## Module 11 — Sandbox Executor (`pipeline/phase_2/sandbox_executor.py`)

### Purpose in the Pipeline

Executes LLM-generated Python scripts in a restricted namespace with timeout protection and retry loop. This is the "jail cell" where untrusted code runs — the sandbox should prevent the LLM from accessing the filesystem, network, or OS.

### Key Design Decisions

#### `_SAFE_BUILTINS` whitelist (file:64–130)
A curated subset of Python builtins available inside the sandbox. Includes constructors (`int`, `list`), math (`abs`, `round`), and iteration (`range`, `zip`, `map`). **[CRITICAL: `__import__` is included]** (file:66) — this completely undermines the sandbox by allowing `__import__("os")`. [Audit A3-1]

#### `SandboxExecutor.execute()` — 4-step process (file:180–323)
1. **Compile** (file:197–206): `compile(script, "<llm_script>", "exec")` — catches `SyntaxError` before execution.
2. **Exec** (file:208–244): `exec(compiled, namespace)` with `SIGALRM` timeout.
3. **Call `build_fact_table()`** (file:246–291): Extracts the function from the namespace and calls `build_fn(seed=seed)`.
4. **Validate return type** (file:293–323): Must be `(DataFrame, dict)`.

**Why separate compile and exec?** SyntaxErrors produce cleaner, more actionable feedback for the LLM than runtime errors buried in a traceback. By catching them early, the error message can say "SyntaxError at line 15" instead of a confusing exec traceback.

#### `PHASE2_SYSTEM_PROMPT` (file:370–428)
The system prompt that instructs the LLM what SDK methods are available and what constraints to follow. It lists all 9 SDK methods, 8 distributions, 6 pattern types, and 7 hard constraints. **This is the correct prompt** — the problem is that `agpds_pipeline.py` overrides it with `_build_phase2_prompt()`. [Audit A2-1]

#### `run_with_retries()` (file:431–502)
The agentic loop: generate code → execute → if failure, format error → generate corrected code → retry. Uses `format_error_feedback()` (file:330–362) to structure the error for LLM self-correction. On retry, the correction prompt includes the full error and asks for the COMPLETE corrected script.

### AGPDS Connection

Implements **§2.4 Execution-Error Feedback Loop** from `phase_2.md`. The spec says `max_retries=3`; the code's default matches (file:435), but `AGPDSPipeline` overrides to 10 (file:107 of `agpds_pipeline.py`). [Audit P2-8: PARTIAL]

### Gotchas & Subtleties

1. **`SIGALRM` is Unix-only** — the sandbox won't work on Windows. There's no fallback mechanism.
2. **`feedback_text` is not initialized before the loop** (file:467) — safe with current control flow but fragile. [Audit A2-2]
3. **The `user_prompt` in `run_with_retries`** wraps its input as `[SCENARIO]\n{scenario_context}\n[AGENT CODE]` (file:462). But `AGPDSPipeline` passes a pre-formatted prompt as `scenario_context`, causing double-wrapping. [Audit A2-3]

---

## Module 12 — Three-Layer Validator (`pipeline/phase_2/validators.py`)

### Purpose in the Pipeline

Post-generation quality assurance. Validates the `(DataFrame, SchemaMetadata)` output against structural, statistical, and pattern expectations — all without LLM calls. Includes an auto-fix loop that mutates metadata parameters and retries.

### Key Design Decisions

#### Three validation layers (file:52–414)
- **L1 Structural** (file:77–163): Row count within 10% of target, categorical cardinality matches, measures are finite, orthogonal group independence via χ² test.
- **L2 Statistical** (file:169–251): Correlation targets within ±0.30 tolerance (wider than expected because pattern injection (φ) runs after correlation injection (ψ) and may distort values), dependency formula residuals, KS distribution test.
- **L3 Pattern** (file:257–414): Each of the 6 pattern types has a custom detection check — e.g., outlier z-score ≥ 2.0, trend break before/after mean shift > 15%, dominance shift before/after midpoint.

#### Auto-fix dispatch (file:596–633)
`AUTO_FIX` maps check-name prefixes to fix strategies. For example, failing `corr_*` checks trigger `_relax_target_r()` (moves `target_r` closer to 0 by 0.05), failing `outlier_*` checks trigger `_amplify_magnitude()` (scales `z_score` by 1.3×). These mutate the metadata dict in-place.

#### `generate_with_validation()` (file:636–679)
The retry loop: call `build_fn(seed=base_seed + attempt)` → validate → if failures, apply auto-fixes → retry with incremented seed. Note: seed increment via `build_fn(seed=...)` only works if `build_fn` recreates the simulator with the new seed — it does NOT work if `build_fn` is `sim.generate()` directly. [Audit A3-6]

### AGPDS Connection

Implements **§2.6 Three-Layer Validation + Auto-Fix** from `phase_2.md`. All three layers are present. The spec says *"Typically converges in 1–2 retries at near-zero cost"* — the auto-fix strategies are lightweight parameter adjustments, confirming this claim.

### Gotchas & Subtleties

1. **L3 pattern checks read `p.get("break_point")`** at file:308 — this requires `break_point` at the top level of the pattern dict. Due to the `dict.update()` flattening in `_build_schema_metadata()`, this actually works. If the bug is fixed to nest params, L3 checks would need updating too.
2. **`_relax_target_r`** parses column names from the check name string (`corr_col_a_col_b`), splitting on `_`. If column names contain underscores, the parsing may fail silently.
3. **`generate_with_validation` is NOT called by the main pipeline** — it's a standalone utility for direct `FactTableSimulator` usage outside the sandbox flow.

---

## Module 13 — Pipeline Orchestrator (`pipeline/agpds_pipeline.py`)

### Purpose in the Pipeline

The central orchestrator that wires Phases 0–2 together into a single `run_single()` call. Takes a `category_id`, samples a domain, generates a scenario, sends it to the sandbox, and returns the result dict.

### Key Design Decisions

#### Constructor: eager domain pool validation (file:31–48)
If `domain_pool.json` doesn't exist, the constructor raises `FileNotFoundError` with a helpful message pointing to `build_domain_pool.py`. This is a **fail-fast** pattern — rather than discovering the missing file mid-generation, the pipeline won't even instantiate.

#### `_build_phase2_prompt()` (file:51–76)
**[CRITICAL BUG]** This method constructs a custom prompt that instructs the LLM to call `simulator.generate_with_validation(target_rows=...)` and `simulator.get_schema_metadata()` — **neither method exists**. The correct call is `sim.generate()`. Additionally, the seed is a hex string from `hashlib.md5(str(datetime.now())...)`, not an integer. [Audit A2-1]

Furthermore, this prompt is passed to `run_with_retries()` as the `scenario_context` argument, which wraps it with `[SCENARIO]...[AGENT CODE]` — causing double-wrapping. [Audit A2-3]

#### `run_single()` flow (file:78–128)
1. Generate unique `generation_id` (file:90)
2. Phase 0: `self.domain_sampler.sample(n=1)` → fallback dict if empty (file:96–97)
3. Phase 1: `self.contextualizer.generate(domain_context)` (file:101)
4. Phase 2: `run_with_retries(self.llm, phase2_user_prompt, max_retries=10)` (file:107)
5. Wrap in `MasterTable` for validation side-effect (file:117)
6. Return result dict with CSV string and metadata (file:121–128)

### AGPDS Connection

This is the **implementation of the AGPDS pipeline flow** described in `data_generation_pipeline.md §3`. Phase 3 is mentioned in the docstring (file:25) but not implemented — the result dict is the handoff point.

### Gotchas & Subtleties

1. **`max_retries=10`** (file:107) — the spec says 3. The extra retries may be intentional for robustness with weaker models.
2. **The `MasterTable(df, metadata=schema_metadata)` at line 117 is only for its validation side-effect** — the `mt` variable is never used afterward. The actual return values are `df.to_csv()` and `schema_metadata` directly.
3. **Fallback domain** (file:97): If `sample()` returns an empty list, a minimal fallback dict is used. This means Phase 1 would receive a domain with no hints — producing a generic scenario.

---

## Module 14 — CLI Runner (`pipeline/agpds_runner.py`)

### Purpose in the Pipeline

The entry point. Parses CLI arguments, initializes the `LLMClient`, creates an `AGPDSRunner`, runs batch generations, and saves results to disk.

### Key Design Decisions

#### `save_results()` — destructive `pop()` (file:51–93)
`result.pop("master_data_csv")` and `result.pop("schema_metadata")` extract data for file writing but **remove it from the in-memory dict**. This means after `save_results()`, the `results` list no longer contains the actual data — only file paths. [Audit A3-2]

#### Category cycling for batch mode (file:122)
When `--category` is not specified, `category_ids = [max(1, (i % 30) + 1) for i in range(args.count)]` — this cycles through categories 1→30→1→… This distributes generations across the taxonomy evenly.

### AGPDS Connection

Implements the CLI interface described in `00_codebase_map.md §Step 3: Entry Point`.

### Gotchas & Subtleties

1. **Default model `gemini-3.1-pro-preview`** (file:105) does not exist. Every invocation without `--model` will fail. [Audit A4-1, CRITICAL]
2. **`run_batch` swallows exceptions** (file:44–47) via `try/except` with `continue` — a failed generation is logged but doesn't stop the batch.

---

## End-to-End Data Journey

Below is a concrete walk-through of ONE execution from CLI invocation to final output files, using representative example values.

### Step 0: CLI Invocation

```bash
python pipeline/agpds_runner.py \
    --provider gemini-native \
    --model gemini-2.0-flash \
    --category 8 \
    --count 1 \
    --output-dir ./output/agpds
```

`main()` at `agpds_runner.py:96`:
- Loads API key from `GEMINI_API_KEY` env var.
- Creates `LLMClient(api_key="AIza...", model="gemini-2.0-flash", provider="gemini-native")`.
- Creates `AGPDSRunner(llm)` → which creates `AGPDSPipeline(llm)`.
- `AGPDSPipeline.__init__` resolves `metadata/domain_pool.json` path and creates:
  - `DomainSampler(pool_path="…/metadata/domain_pool.json")` — loads 210 domains into memory.
  - `ScenarioContextualizer(llm)` with `max_retries=2`.
- `category_ids = [8]` (one generation for category 8 = "Health & Medicine").

### Step 1: Phase 0 — Domain Sampling

`self.domain_sampler.sample(n=1)` at `agpds_pipeline.py:96`.

The sampler filters the 210 domains to exclude any in `used_ids` (empty on first call). `random.sample(candidates, 1)` picks one:

```python
{
    "id": "dom_042",
    "name": "ICU bed turnover analytics",
    "topic": "Healthcare",
    "complexity_tier": "complex",
    "typical_entities_hint": ["hospitals", "ICU units", "bed categories"],
    "typical_metrics_hint": [
        {"name": "occupancy_rate", "unit": "%"},
        {"name": "turnover_count", "unit": "patients/day"}
    ],
    "temporal_granularity_hint": "daily"
}
```

`used_ids` is updated to `{"dom_042"}` — this domain won't be sampled again until reset.

### Step 2: Phase 1 — Scenario Contextualization

`self.contextualizer.generate(domain_context)` at `agpds_pipeline.py:101`.

1. `_build_user_prompt()` serializes the domain metadata as JSON and injects it into `SCENARIO_USER_PROMPT_TEMPLATE`.
2. `llm.generate_json(system=SCENARIO_SYSTEM_PROMPT, user=..., temperature=1.0)` sends the prompt to Gemini.
3. The LLM returns:

```json
{
    "scenario_title": "2024 Q1-Q2 Beijing Tertiary Hospital ICU Utilization Report",
    "data_context": "Beijing Municipal Health Commission compiled daily ICU metrics across 5 major tertiary hospitals to optimize bed allocation during flu season surge periods.",
    "key_entities": ["Peking Union Medical College Hospital", "Beijing Tongren Hospital", "Xuanwu Hospital", "Beijing Children's Hospital", "China-Japan Friendship Hospital"],
    "key_metrics": [
        {"name": "occupancy_rate", "unit": "%", "range": [45.0, 98.0]},
        {"name": "avg_los_hours", "unit": "hours", "range": [24, 720]},
        {"name": "turnover_count", "unit": "patients/day", "range": [1, 15]}
    ],
    "temporal_granularity": "daily",
    "target_rows": 900
}
```

4. `validate_output()` checks: 6 required fields ✓, 5 entities (3–8) ✓, 3 metrics (2–5) ✓, `"daily"` in `VALID_GRANULARITIES` ✓, 900 in [100, 3000] ✓.
5. `_update_tracker()` records the title and context for diversity tracking.

### Step 3: Phase 2a — Code Generation

`_build_phase2_prompt(scenario)` at `agpds_pipeline.py:105` formats the scenario into a user prompt (note: this prompt has bugs — see Audit A2-1 / A2-3).

`run_with_retries(llm, phase2_user_prompt, max_retries=10)` at `sandbox_executor.py:431`:
1. Wraps the prompt: `"[SCENARIO]\n{phase2_user_prompt}\n[AGENT CODE]"`.
2. `llm.generate_code(system=PHASE2_SYSTEM_PROMPT, user=...)` → Gemini returns Python source.

**If the PHASE2_SYSTEM_PROMPT is used correctly** (bypassing the buggy `_build_phase2_prompt`), the LLM produces something like:

```python
def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=900, seed=seed)

    # Step 1: Columns
    sim.add_category("hospital", values=[...], weights=[...], group="entity")
    sim.add_category("icu_type", values=["Medical", "Surgical", "Cardiac"],
                     weights=[0.4, 0.35, 0.25], group="unit", parent=None)
    sim.add_temporal("record_date", start="2024-01-01", end="2024-06-30", freq="daily")
    sim.add_measure("occupancy_rate", dist="beta", params={"alpha": 5, "beta": 2},
                    scale=[45.0, 98.0])
    sim.add_measure("avg_los_hours", dist="lognormal", params={"mu": 4.5, "sigma": 0.8})
    sim.add_measure("turnover_count", dist="poisson", params={"lam": 6})

    # Step 2: Relationships
    sim.declare_orthogonal("entity", "unit", rationale="Hospital identity is independent of ICU type")
    sim.add_conditional("occupancy_rate", on="icu_type", mapping={...})
    sim.add_correlation("occupancy_rate", "avg_los_hours", target_r=0.45)
    sim.inject_pattern("outlier_entity", target="hospital == 'Beijing Children\\'s Hospital'",
                       col="occupancy_rate", params={"z_score": 3.0})
    sim.inject_pattern("trend_break", target=None, col="avg_los_hours",
                       params={"break_point": "2024-03-15", "magnitude": 0.25})

    return sim.generate()
```

### Step 4: Phase 2b — Sandbox Execution

`executor.execute(script, seed=42)` at `sandbox_executor.py:180`:
1. `compile()` succeeds (no syntax errors).
2. `exec()` runs in the restricted namespace — defines `build_fact_table` in the namespace.
3. `build_fn(seed=42)` is called.

### Step 5: Phase 2c — Deterministic Engine

Inside `build_fact_table`, `sim.generate()` executes the 7 stages:

| Stage | What Happens | Example Output |
|-------|-------------|----------------|
| β `_build_skeleton` | 5 hospitals × 3 ICU types = 15 combos → tiled to 900 rows → 181 dates sampled | 900-row DataFrame with `hospital`, `icu_type`, `record_date` |
| δ `_sample_measures` | `occupancy_rate` ← Beta(5,2) scaled to [45,98], `avg_los_hours` ← LogNormal(4.5, 0.8), `turnover_count` ← Poisson(6) | 3 new numeric columns added |
| γ `_apply_conditionals` | `occupancy_rate` re-sampled per `icu_type` with overridden params | Values now differ by ICU type |
| λ `_apply_dependencies` | (none declared in this example) | No change |
| ψ `_inject_correlations` | Gaussian Copula injects r=0.45 between `occupancy_rate` and `avg_los_hours` | Ranks shuffled to achieve target correlation |
| φ `_inject_patterns` | Beijing Children's Hospital `occupancy_rate` boosted to ~3σ above mean; `avg_los_hours` after 2024-03-15 multiplied by 1.25 | Visible anomalies in the data |
| ρ `_inject_realism` | (not called — no `set_realism()` in script) | No change |

`_post_process()` sorts by `record_date`, resets index.

`_build_schema_metadata()` produces the metadata dict with all 8 keys.

**Returns:** `(df, meta)` — a 900×6 DataFrame and the SchemaMetadata dict.

### Step 6: Result Assembly

Back in `AGPDSPipeline.run_single()`:
- `MasterTable(df, metadata=schema_metadata)` — validation runs (warnings if needed), object discarded.
- Returns:
```python
{
    "generation_id": "agpds_20260304_194500_a1b2c3",
    "category_id": 8,
    "domain_context": {"id": "dom_042", ...},
    "scenario": {"scenario_title": "2024 Q1-Q2 Beijing...", ...},
    "master_data_csv": "hospital,icu_type,record_date,...\nPeking Union...",
    "schema_metadata": {"dimension_groups": {...}, "columns": [...], ...}
}
```

### Step 7: Serialization

`runner.save_results(results, "./output/agpds")` at `agpds_runner.py:126`:

| File Written | Content |
|-------------|---------|
| `output/agpds/master_tables/agpds_20260304_194500_a1b2c3.csv` | 900 rows × 6 columns of atomic-grain event data |
| `output/agpds/schemas/agpds_20260304_194500_a1b2c3_metadata.json` | SchemaMetadata with dimension groups, correlations, patterns, etc. |
| `output/agpds/charts.json` | Manifest array with one entry containing `generation_id`, `category_id`, `scenario`, and file paths |

**Note:** `master_data_csv` and `schema_metadata` are `pop()`-ed from the result dict during serialization — they no longer exist in memory after `save_results()` returns.

---

*[WRITE CONFIRMED] /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/audit/03_code_walkthrough.md | 719 lines*
