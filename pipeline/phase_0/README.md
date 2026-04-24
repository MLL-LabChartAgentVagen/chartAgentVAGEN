# Phase 0 — Domain Pool Construction

Phase 0 is the run-once, offline stage of the AGPDS data-generation pipeline. It builds a cached taxonomy of 300 fine-grained analytical domains (30 seed topics × 10 sub-topics each), deduplicates them via embedding-based overlap checks, and exposes a stratified `DomainSampler` that every downstream phase draws from. The authoritative spec is [storyline/data_generation/phase_0.md](../../storyline/data_generation/phase_0.md).

---

## 1. Overview

**What it is.** A one-shot taxonomy builder plus a lightweight sampler. `DomainPool` calls an LLM to generate sub-topics for each seed topic, runs a cosine-similarity overlap check to drop near-duplicates, assigns stable IDs, and persists the result to [domain_pool.json](domain_pool.json). `DomainSampler` then reads that file and serves domains without replacement to Phase 1 and beyond.

**Position in the pipeline.**

```
phase_0  (run once, offline)                 → domain_pool.json
  │                                               │
  │     DomainSampler.sample(n, complexity, …)    │
  ▼                                               ▼
phase_1  scenario_contextualizer  ──►  phase_2  data simulator  ──►  downstream
```

Phase 0 runs once. Subsequent pipeline invocations ([agpds_pipeline.py](../agpds_pipeline.py)) load the cached pool and refuse to proceed if it is missing.

---

## 2. Architecture Overview

```
pipeline/phase_0/
├── __init__.py              # Re-exports DomainPool, DomainSampler, check_overlap, SEED_TOPICS
├── domain_pool.py           # DomainPool orchestrator + DomainSampler + LLM prompts
├── overlap_checker.py       # OpenAI-embedding cosine-similarity deduplication
├── build_domain_pool.py     # CLI entry point (one-shot build)
├── taxonomy_seed.json       # 30 seed topics (input)
├── domain_pool.json         # Compiled 300-domain pool (cached output)
└── tests/
    └── test_domain_pool.py  # 7 unit tests — no LLM calls
```

**Dataflow:**

```
taxonomy_seed.json
  │  (30 topics)
  ▼
DomainPool._build
  ├─► _generate_subtopics   (LLM call, per topic)
  ├─► check_overlap          (embeddings, threshold 0.80, within-topic dedup)
  ├─► _assign_ids            (dom_001 … dom_300)
  └─► _compute_diversity     (normalized entropy over complexity tiers)
  │
  ▼
domain_pool.json  ◄───  DomainSampler.sample()  ───►  phase_1 / phase_2
```

See spec §0.1–§0.6 in [phase_0.md](../../storyline/data_generation/phase_0.md) for the underlying rationale.

---

## 3. Interfaces

### 3.1 `DomainPool`

Defined in [domain_pool.py:127](domain_pool.py#L127). Orchestrates the full build.

```python
class DomainPool:
    def __init__(
        self,
        llm_client,
        pool_path: str = "domain_pool.json",
        seed_path: Optional[str] = None,
    )

    def load_or_build(
        self,
        n_topics: int = 30,
        subtopics_per_topic: int = 7,
        overlap_threshold: float = 0.80,
        force: bool = False,
    ) -> dict
```

- `llm_client` must expose `generate_json(system, user, temperature, max_tokens)` — satisfied by [pipeline/core/llm_client.py:LLMClient](../core/llm_client.py).
- When `seed_path` is supplied, `n_topics` is ignored and every entry in `taxonomy_seed.json` is used as a topic.
- `load_or_build` is idempotent: it returns the cached pool if the file exists and passes `_validate_pool`, and only rebuilds when `force=True` or the file is missing/invalid.

**Returned dict (also the on-disk schema):**

| Key | Type | Notes |
|---|---|---|
| `version` | `str` | Currently `"1.0"`. |
| `generated_at` | `str` | ISO-8601 UTC timestamp. |
| `total_domains` | `int` | Number of entries in `domains`. |
| `diversity_score` | `float` | Normalized entropy over `complexity_tier` (0–1). |
| `complexity_distribution` | `dict[str, int]` | Counts per tier. |
| `topic_coverage` | `dict[str, int]` | Counts per topic. |
| `domains` | `list[dict]` | See §3.4. |

### 3.2 `DomainSampler`

Defined in [domain_pool.py:343](domain_pool.py#L343). Stratified, without-replacement sampler.

```python
class DomainSampler:
    def __init__(self, pool_path: str)

    def sample(
        self,
        n: int = 1,
        complexity: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> list[dict]

    def reset(self) -> None
```

- `complexity` ∈ `{"simple", "medium", "complex"}`; `topic` is matched against the `topic` field verbatim (e.g. `"Media & Entertainment"`).
- State auto-resets when `len(used_ids) ≥ 0.8 × total_pool_size` **or** when the filtered candidate set is smaller than `n`.
- Sampling uses `random.sample` against the un-used, filter-matching subset. The caller is responsible for seeding `random` if reproducibility is required.

### 3.3 `check_overlap`

Defined in [overlap_checker.py:30](overlap_checker.py#L30).

```python
def check_overlap(
    items: list[str],
    model: str = "text-embedding-3-small",
    threshold: float = 0.80,
) -> list[tuple[str, str, float]]
```

Fetches OpenAI embeddings for `items`, computes the pairwise cosine-similarity matrix (via `sklearn` when available, otherwise a numpy fallback), and returns every upper-triangular pair whose similarity is ≥ `threshold`. An empty list means "no overlap, good to go." `DomainPool._build` drops the **second** item of each flagged pair before persisting.

Note: [domain_pool.py](domain_pool.py) also re-exports a thin wrapper `check_overlap(items, threshold=0.80)` that forwards to this function with the default model.

### 3.4 Domain record schema

Each entry in `domains` has exactly these fields:

| Field | Type | Example |
|---|---|---|
| `id` | `str` | `"dom_001"` |
| `name` | `str` | `"Streaming service monthly active user growth"` |
| `topic` | `str` | `"Media & Entertainment"` |
| `complexity_tier` | `"simple" \| "medium" \| "complex"` | `"simple"` |
| `typical_entities_hint` | `list[str]` | `["streaming service", "subscription tier"]` |
| `typical_metrics_hint` | `list[{"name": str, "unit": str}]` | `[{"name": "active_users", "unit": "count"}]` |
| `temporal_granularity_hint` | `"hourly" \| "daily" \| "weekly" \| "monthly" \| "quarterly" \| "yearly"` | `"monthly"` |

---

## 4. Usage Examples

### 4.1 Build the pool (one-shot)

Run from the repo root:

```bash
export GEMINI_API_KEY=...      # or OPENAI_API_KEY — used as the generation LLM
export OPENAI_API_KEY=...      # always required: embeddings use text-embedding-3-small

python pipeline/phase_0/build_domain_pool.py \
    --subtopics-per-topic 10 \
    --model gemini-2.5-pro
```

CLI flags (see [build_domain_pool.py:48](build_domain_pool.py#L48)):

| Flag | Default | Purpose |
|---|---|---|
| `--force` | off | Regenerate even if `domain_pool.json` already exists. |
| `--subtopics-per-topic N` | `10` | Sub-topics generated per seed topic. |
| `--model MODEL` | `gemini-2.5-pro` | Generation LLM passed to `LLMClient`. |

The script logs to stdout and prints a summary block (total domains, diversity score, complexity distribution) on success.

### 4.2 Sample from the pool

```python
from pipeline.phase_0 import DomainSampler

sampler = DomainSampler("pipeline/phase_0/domain_pool.json")

# 5 medium-complexity domains from anywhere in the pool
batch = sampler.sample(n=5, complexity="medium")

# 3 domains restricted to one topic
media_batch = sampler.sample(n=3, topic="Media & Entertainment")

# Manually restart if you need to iterate the pool again
sampler.reset()
```

### 4.3 Ad-hoc overlap check

```python
from pipeline.phase_0 import check_overlap

candidates = ["Retail sales trend", "E-commerce sales trend", "Air traffic density"]
overlaps = check_overlap(candidates, threshold=0.80)
# -> [("Retail sales trend", "E-commerce sales trend", 0.87)]
```

---

## 5. Dependencies & Environment

**Python:** 3.10+ (repo-wide convention — PEP 604 union syntax is used throughout).

**Third-party libraries:**

| Package | Required for | Notes |
|---|---|---|
| `numpy` | Core | Array operations, cosine fallback. |
| `openai` | Embeddings (always) and optionally generation | `text-embedding-3-small` is hard-coded in `overlap_checker.py`. |
| `scikit-learn` | Optional | Used for `cosine_similarity` when importable; numpy fallback otherwise. |
| `python-dotenv` | Optional | Auto-loads `.env` in `build_domain_pool.py`; a minimal parser runs if missing. |

**Internal dependencies:**

- [pipeline/core/llm_client.py](../core/llm_client.py) — `LLMClient` is constructed by `build_domain_pool.py` and passed into `DomainPool`. Phase 0 does not import any other pipeline module.

**Environment variables:**

- `OPENAI_API_KEY` — **always required**: embeddings go through the OpenAI SDK regardless of which generation LLM you pick.
- `GEMINI_API_KEY` — required when using a Gemini generation model (the CLI default).
- Either may be declared in a repo-root `.env`; `build_domain_pool.py` will pick it up.

**Files on disk:**

- [taxonomy_seed.json](taxonomy_seed.json) — ships with the repo; the seed list the CLI expects.
- [domain_pool.json](domain_pool.json) — the cached build artifact. Do not hand-edit; rebuild with `--force` if you need to regenerate.

---

## 6. Development Conventions

**Run the tests.** From the `pipeline/` directory:

```bash
cd pipeline
python -m phase_0.tests.test_domain_pool
```

The 7 tests cover seed validation, overlap detection (mocked embeddings), schema validation against `domain_pool.json`, sampler without-replacement behaviour, complexity filtering, and exhaustion reset. No network calls and no LLM key required.

**Regenerate the pool.** The only supported way to mutate `domain_pool.json` is to rebuild it:

```bash
python pipeline/phase_0/build_domain_pool.py --force
```

**Extend the taxonomy.** Add entries to [taxonomy_seed.json](taxonomy_seed.json) (shape: `{"domains": [{"id": ..., "tier": "<topic name>"}, ...]}`) and rebuild. `DomainPool._build` enforces mutual non-overlap across topics and within each topic's sub-topic list using `overlap_threshold` (default 0.80); the second item of any flagged pair is dropped.

**Integration contract.** Phase 1 and later phases depend on `DomainSampler.sample()` only. `DomainPool`, the LLM prompts, and the CLI are offline concerns — do **not** import them from runtime code. The canonical integration site is [pipeline/agpds_pipeline.py:9](../agpds_pipeline.py#L9), which loads `domain_pool.json` at startup and fails with a build-script hint if it is missing.

**Acceptance gates** (from spec §0.4):

- Pool size ≥ 200 domains (current cached pool: 300).
- No pair with cosine similarity ≥ 0.80 after dedup.
- Complexity tiers roughly equally distributed (`diversity_score` close to 1).
- All six temporal granularities (`hourly`…`yearly`) represented.
