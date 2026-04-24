# Phase 2 — Agentic Data Simulator (SDK-Driven)

Phase 2 turns a Phase 1 scenario context (domain title, entities, metrics, temporal grain, `target_rows`) into a validated atomic-grain Master DataFrame plus a 7-key schema-metadata dict and a layered validation report, by having an LLM write a single executable Python script against a type-safe SDK. The LLM's contribution ends at producing the script; everything downstream — row generation, metadata construction, validation, auto-fix — is pure computation with a single `numpy.random.Generator` keyed by `seed`.

## What's new since Phase 1 (paradigm shift)

Phase 1 emitted a JSON DGP spec whose declared distribution could diverge from the generated distribution after successive overrides (`add_measure` → `add_conditional` → `add_dependency` → `add_correlation`). Phase 2 replaces that with **Code-as-DGP**: the LLM writes a single executable Python script calling `FactTableSimulator`, where every measure is declared once as a complete data-generating program. Semantics are self-contained and aligned with validation by construction.

## The three pillars

- **Closed-form DGP declaration** via a type-safe SDK — each measure declared once as a complete data-generating program. See §6 Key concepts and §9 M1.
- **DAG-ordered event-level generation** — a single DAG over categoricals, temporals, and measures, executed in topological order with a single RNG stream (bit-identical CSVs for a given seed). See §6 Key concepts and §9 M2.
- **Three-layer validation with no additional LLM calls** — L1 structural, L2 statistical, L3 pattern, plus a deterministic auto-fix loop. See §6 Key concepts and §9 M5.

## Dataflow one-liner

```
scenario_context → M3 (LLM) → M1 (SDK) → M2 ∥ M4 → M5 → (DataFrame, schema_metadata, ValidationReport)
```

Quick start is in §3; module internals are in §9.

---

## 2. Installation and dependencies

Phase 2 ships as a package inside the larger `chartAgentVAGEN` repo (at [pipeline/phase_2/](../../pipeline/phase_2/)). There is no `pyproject.toml` and no `setup.py`: Phase 2 is not installed as a distributable package. You clone the repo, install a handful of runtime dependencies, and run the CLIs from the repo root. Imports like `from pipeline.phase_2.pipeline import run_loop_a` resolve because [conftest.py](../../conftest.py) at the repo root adds the repo root to `sys.path`.

### Python version

Python **3.10 or newer**. Phase 2 uses PEP 604 `X | Y` union syntax (e.g., `llm_client: LLMClient | None`) and parameterized builtins (`dict[str, Any]`, `list[str]`) throughout.

### Install runtime dependencies

From the repo root:

```bash
pip install -r requirements.txt
```

[requirements.txt](../../requirements.txt) pins the broader `chartAgentVAGEN` project's dependencies. Of these, Phase 2 itself only imports `numpy`, `pandas`, and `scipy`; the rest (matplotlib, pillow, opencv-python, scikit-learn, scikit-image, statsmodels, seaborn) are used by other parts of the repo and do not affect Phase 2 correctness.

### LLM provider SDKs

Stage 1 (`agpds_generate`) and the end-to-end runner (`agpds_runner`) need one of the following provider SDKs, depending on which `--provider` value you use. Stage 2 (`agpds_execute`) needs none — it makes no LLM calls. The SDKs are imported lazily inside `pipeline/phase_2/orchestration/llm_client.py`, so missing packages only fail when you try to use that provider:

| `--provider` | Package | Install |
|---|---|---|
| `openai` | [openai](https://pypi.org/project/openai/) | `pip install openai` |
| `gemini` | [openai](https://pypi.org/project/openai/) (Gemini's OpenAI-compatible endpoint at `https://generativelanguage.googleapis.com/v1beta/openai/`) | `pip install openai` |
| `gemini-native` | [google-genai](https://pypi.org/project/google-genai/) | `pip install google-genai` |
| `azure` | [openai](https://pypi.org/project/openai/) | `pip install openai` |

`python-dotenv` is imported inside a `try / except ImportError` guard in `agpds_generate` and `agpds_runner` (the two LLM-bound CLIs); install it (`pip install python-dotenv`) if you want `.env` files to be loaded automatically, otherwise export environment variables yourself. `agpds_execute` makes no LLM calls, needs no API key, and does not load `.env`.

### `.env` setup (API keys and default models)

Create a `.env` file at the repo root (or export these as environment variables before running). Only the key matching your active provider is required:

```dotenv
# API keys — at least one of the two must be set (matched to your --provider)
OPENAI_API_KEY=sk-...                       # used by --provider openai | azure
GEMINI_API_KEY=...                          # used by --provider gemini | gemini-native

# Optional model overrides (if unset, the CLI falls back to hardcoded defaults below)
OPENAI_MODEL=gpt-4o-mini                    # default fallback for openai / azure
GEMINI_MODEL=gemini-3.1-pro-preview         # default fallback for gemini / gemini-native

# Optional default provider (if unset, defaults to "gemini")
LLM_PROVIDER=gemini
```

Resolution priority for provider, model, and API key (implemented identically in all three CLIs):

1. **CLI flag** (`--provider`, `--model`, `--api-key`) if passed.
2. **`.env` / environment variable** (`LLM_PROVIDER`, `OPENAI_MODEL` / `GEMINI_MODEL`, `OPENAI_API_KEY` / `GEMINI_API_KEY`).
3. **Hardcoded fallback:** provider → `"gemini"`; model → `gpt-4o-mini` (for `openai` / `azure`) or `gemini-3.1-pro-preview` (for `gemini` / `gemini-native`). There is no fallback for the API key — an unset key is a fatal error.

See §3 for how each CLI consumes these settings.

---

## 3. Quick start / how to run

Phase 2 exposes three command-line entry points plus a programmatic API. All commands run from the repo root.

### Mental model

Phase 2 has a natural cost seam: Loop A (LLM, expensive, non-deterministic) and Loop B (pure compute, cheap, deterministic). The two CLIs make that seam explicit so you can burn LLM tokens once and replay the deterministic half as many times as you want (byte-identical CSVs per seed). The `agpds_runner` end-to-end CLI still works; it chains the two stages internally.

### Split workflow (recommended)

**Stage 1** — generate and persist N validated LLM scripts:

```bash
python -m pipeline.agpds_generate --provider gemini --count 10
python -m pipeline.agpds_generate --provider openai --count 5 --category 3
```

This writes per successful generation:

- `output/agpds/scripts/{gen_id}.py` — the validated LLM-generated `build_fact_table()` source.
- `output/agpds/declarations/{gen_id}.json` — the replayable declaration set (via [serialization.declarations_to_json](../../pipeline/phase_2/serialization.py)).
- one line appended to `output/agpds/manifest.jsonl` — the per-generation index.

**Stage 2** — replay saved declarations deterministically (no LLM calls):

```bash
python -m pipeline.agpds_execute --workers 4            # execute every saved declaration
python -m pipeline.agpds_execute --workers 1            # sequential
python -m pipeline.agpds_execute --ids agpds_20260420_202948_4ba639
python -m pipeline.agpds_execute --ids id1,id2,id3 --workers 2
```

Stage 2 writes final CSVs + schemas + chart records under `output/agpds/master_tables/`, `schemas/`, `charts/`. See §10 for the full layout.

### End-to-end (backward-compatible)

One command that internally runs Phase 0 (domain) + Phase 1 (scenario) + Phase 2 Loop A + Phase 2 Loop B and saves the same output set as the runner-based version:

```bash
python -m pipeline.agpds_runner --provider gemini --count 1 --category 1
python -m pipeline.agpds_runner --provider openai --count 5
```

Output is bit-identical to chaining `agpds_generate` + `agpds_execute`; the runner is purely a convenience wrapper.

### `.env` configuration and resolution priority

`agpds_generate` and `agpds_runner` load `.env` if `python-dotenv` is available (`agpds_execute` skips this — it makes no LLM calls) and then resolve provider, API key, and model in this order:

1. CLI flag (`--provider`, `--api-key`, `--model`).
2. `.env` / environment variable.
3. Hardcoded fallback.

```dotenv
OPENAI_API_KEY=...
GEMINI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini                    # optional
GEMINI_MODEL=gemini-3.1-pro-preview         # optional
LLM_PROVIDER=gemini                         # optional; sets default provider
```

See §2 for the full resolution rules and the behavior when a required key is missing.

### CLI flag reference

| Flag | Type / choices | Default | `agpds_generate` | `agpds_execute` | `agpds_runner` | Description |
|---|---|---|---|---|---|---|
| `--api-key` | str | — | ✓ | — | ✓ | LLM API key. Overrides `OPENAI_API_KEY` / `GEMINI_API_KEY`. |
| `--model` | str | — (→ `.env` → hardcoded) | ✓ | — | ✓ | Model name. Overrides `OPENAI_MODEL` / `GEMINI_MODEL`. |
| `--provider` | `openai \| gemini \| gemini-native \| azure \| auto` | — (→ `LLM_PROVIDER` → `gemini`) | ✓ | — | ✓ | LLM provider. |
| `--category` | int (1–30) | — (random) | ✓ | — | ✓ | Restrict to a specific meta-category. Without it, categories are sampled uniformly at random. |
| `--count` | int | `1` | ✓ | — | ✓ | Number of generations to run. |
| `--output-dir` | path | `./output/agpds` | ✓ | ✓ | ✓ | Root directory for outputs (scripts, declarations, master tables, schemas, charts). |
| `--input-dir` | path | `./output/agpds` | — | ✓ | — | Directory holding `declarations/` (and optional `manifest.jsonl`). |
| `--workers` | int | `1` | — | ✓ | — | Parallel workers (`ProcessPoolExecutor`); `<= 1` runs sequentially. |
| `--ids` | str (comma-separated) | — (all) | — | ✓ | — | Subset of `generation_id` values to execute. |

### Programmatic API

For in-process use (tests, notebooks, or custom orchestration), call the same Loop A + Loop B functions the CLIs call:

```python
import json
from pipeline.phase_2.pipeline import run_loop_a, run_loop_b_from_declarations
from pipeline.phase_2.serialization import declarations_to_json, declarations_from_json

# Stage 1 — Loop A only. Returns (df, metadata, raw_declarations, source_code) or SkipResult.
loop_a = run_loop_a(
    scenario_context,
    api_key="...",
    model="gemini-3.1-pro-preview",
    provider="gemini",
)

# Persist the two Stage 1 artifacts.
with open("decl.json", "w") as f:
    json.dump(declarations_to_json(loop_a[2]), f)
with open("script.py", "w") as f:
    f.write(loop_a[3])

# Stage 2 — Loop B only. Pure function of raw_declarations + seed.
# Returns (df, metadata, ValidationReport) or SkipResult.
with open("decl.json") as f:
    raw_declarations = declarations_from_json(json.load(f))
df, metadata, report = run_loop_b_from_declarations(raw_declarations)
```

For a single-call end-to-end equivalent, use [`run_phase2`](../../pipeline/phase_2/pipeline.py); see §8 for the full signature.

---

## 4. Architecture overview

### Module inventory

| # | Module | Single responsibility | Primary input | Primary output |
|---|---|---|---|---|
| **M1** | [SDK Surface](../../pipeline/phase_2/sdk/) | Accept `add_*()` / `declare_*()` / `inject_*()` calls from the LLM script and accumulate a validated `DeclarationStore`. | SDK method calls from the LLM-generated `build_fact_table()` script | Frozen `DeclarationStore` (column registry, group graph, measure DAG, patterns) |
| **M2** | [Generation Engine](../../pipeline/phase_2/engine/) | Execute a deterministic, DAG-ordered pipeline that converts declarations + `seed` into an atomic-grain `pd.DataFrame`. | Declaration store fields + `seed` | `pd.DataFrame` (one row per atomic event) |
| **M3** | [LLM Orchestration](../../pipeline/phase_2/orchestration/) | Prompt the LLM, execute the resulting script in a sandbox, feed typed exceptions back for up to 3 retries. | Scenario context dict + SDK reference | Executable Python script (or `SkipResult`) |
| **M4** | [Schema Metadata](../../pipeline/phase_2/metadata/) | Project the frozen `DeclarationStore` into the 7-key `schema_metadata` dict consumed by M5 and Phase 3. | Declaration store | `schema_metadata` dict |
| **M5** | [Validation Engine](../../pipeline/phase_2/validation/) | Validate the generated DataFrame at three layers and, on failure, auto-fix and re-execute M2 without calling the LLM. | DataFrame + `schema_metadata` | `ValidationReport` (optionally with corrected DataFrame) |

Spec §2.10 (Design Advantages) is rationale-only — it has no corresponding implementation module.

### Implementation-level dependency graph

```
                    types.py + exceptions.py
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
              M1: SDK Surface      (used by all)
                    │
          ┌─────────┼──────────┐
          ▼         ▼          ▼
    M4: Metadata  M2: Engine  M3: Orchestration
          │         │
          └────┬────┘
               ▼
         M5: Validation
               │
               ▼
          pipeline.py
```

### Execution order

```
scenario_context → M3 → M1 → M2 ∥ M4 → M5 → (df, schema_metadata, ValidationReport)
```

M2 and M4 are **logically parallel** (both read the frozen store and do not depend on each other) but **currently serialized** in the implementation — `metadata.builder.build_schema_metadata()` is called from the tail of `engine.generator.run_pipeline`. Treat the `∥` above as a conceptual annotation, not a threading claim. See §8 for why.

### Feedback loops at a glance

- **Loop A (outer)** — `M3 ↔ M1`, with LLM. Typed SDK exception → re-prompt the LLM with code + traceback. Fixes *semantic authoring errors*. `max_retries=3`.
- **Loop B (inner)** — `M5 → M2`, no LLM. L1/L2/L3 failure → apply an auto-fix strategy + re-execute M2 with `seed + attempt`. Fixes *statistical sampling variance*. Default `max_retries=2` (i.e., 3 attempts).

See §8 for the mechanism and the Stage 1 / Stage 2 split.

### Pipeline architecture

![Pipeline architecture — Stage 1 (Loop A, LLM-bound) and Stage 2 (Loop B, deterministic) with the disk boundary](../artifacts/phase2_pipeline_module_split.svg)

For the package tree see §5; for control-flow narrative see §8; for per-module internals see §9.

---

## 5. Codebase directory structure

Phase 2 lives at [pipeline/phase_2/](../../pipeline/phase_2/). The CLI runners live one level up at [pipeline/](../../pipeline/). The trees below cover only Phase 2–relevant paths — other directories in the parent `chartAgentVAGEN` repo (chart generators, storyline, etc.) are out of scope.

### Repo-root landmarks

```
chartAgentVAGEN/
├── README.md                    # this file
├── requirements.txt             # runtime dependencies (see §2)
├── conftest.py                  # makes `pipeline.*` imports resolve from any cwd
├── LICENSE
├── pipeline/                    # all pipeline code (runners + Phase 0/1/2)
├── docs/                        # docs, diagrams, and working drafts
│   ├── artifacts/               # source-of-truth documents for this README
│   │   ├── phase_2.md           # Phase 2 spec (§2.1–§2.10)
│   │   ├── PIPELINE_SPLIT.md    # Stage 1/2 split design
│   │   ├── stage1_module_map.md
│   │   ├── stage2_overview.md
│   │   ├── stage5_anatomy_summary.md
│   │   ├── phase2_pipeline_module_split.svg   # embedded in §4
│   │   └── phase2_pipeline_modules.svg
│   ├── svg/                     # per-module SVGs embedded in §9
│   │   ├── module1_sdk_surface.{md,svg}
│   │   ├── module2_gen_engine.{md,svg}
│   │   ├── module3_llm_orchestration.{md,svg}
│   │   ├── module4_schema_metadata.{md,svg}
│   │   └── module5_validation_engine.{md,svg}
│   └── readme-workflow/         # README drafting workspace
└── output/                      # generated artifacts (created at runtime; see §10)
```

### CLI runners — [pipeline/](../../pipeline/)

```
pipeline/
├── agpds_generate.py            # Stage 1 CLI (Loop A; writes scripts/ + declarations/ + manifest.jsonl)
├── agpds_execute.py             # Stage 2 CLI (Loop B; reads declarations/, writes master_tables/ + schemas/ + charts/)
├── agpds_runner.py              # End-to-end CLI (chains Stage 1 + Stage 2, backward-compatible)
├── agpds_pipeline.py            # AGPDSPipeline helper class: generate_artifacts() / execute_artifact() / run_single()
├── core/                        # shared infrastructure for all Phases
│   ├── llm_client.py            # multi-provider LLM client (mirror of phase_2/orchestration/llm_client.py)
│   ├── master_table.py
│   ├── utils.py                 # META_CATEGORIES, shared helpers
│   └── tests/
├── phase_0/                     # domain pool construction (taxonomy_seed.json, domain_pool.json)
│   ├── build_domain_pool.py
│   ├── domain_pool.py
│   ├── overlap_checker.py
│   └── tests/
├── phase_1/                     # scenario contextualization
│   ├── scenario_contextualizer.py
│   └── tests/
├── phase_2/                     # Phase 2 package — documented below
├── adapters/                    # adapter layer (legacy glue code)
├── legacy/                      # pre-split pipeline code kept for reference
├── evaluation_pipeline.py       # downstream evaluation harness
├── evaluation_runner.py
├── results/                     # evaluation result cache
└── schemas/                     # JSON schemas used by downstream phases
```

### Phase 2 package — [pipeline/phase_2/](../../pipeline/phase_2/)

```
pipeline/phase_2/
├── __init__.py
├── types.py                     # cross-module dataclasses (see §7)
├── exceptions.py                # typed SDK exceptions + SkipResult sentinel (see §7)
├── pipeline.py                  # top-level orchestrator: run_phase2, run_loop_a,
│                                #   run_loop_b_from_declarations (see §8, §9)
├── serialization.py             # declarations_to_json / declarations_from_json —
│                                #   Stage 1 ↔ Stage 2 disk boundary (see §7)
│
├── sdk/                         # M1 — SDK Surface (§9 M1)
│   ├── __init__.py
│   ├── simulator.py             # FactTableSimulator class; phase lifecycle; generate()
│   ├── columns.py               # add_category, add_temporal, add_measure, add_measure_structural
│   ├── relationships.py         # declare_orthogonal, add_group_dependency, inject_pattern, set_realism
│   ├── groups.py                # DimensionGroup registration helpers
│   ├── dag.py                   # build_full_dag, topological_sort, check_measure_dag_acyclic
│   └── validation.py            # declaration-time validation rules (name uniqueness, predictors, etc.)
│
├── engine/                      # M2 — Generation Engine (§9 M2)
│   ├── __init__.py
│   ├── generator.py             # run_pipeline (α → β → γ → δ → τ_post)
│   ├── skeleton.py              # α — non-measure column sampling
│   ├── measures.py              # β — stochastic + structural measures; _safe_eval_formula
│   ├── patterns.py              # γ — inject_patterns (outlier_entity, trend_break)
│   ├── realism.py               # δ — inject_missing_values, inject_dirty_values
│   └── postprocess.py           # τ_post — dict-of-arrays → pd.DataFrame
│
├── orchestration/               # M3 — LLM Orchestration (§9 M3)
│   ├── __init__.py
│   ├── prompt.py                # SYSTEM_PROMPT_TEMPLATE + render_system_prompt
│   ├── sandbox.py               # execute_in_sandbox, run_retry_loop, format_error_feedback,
│   │                            #   _TrackingSimulator
│   ├── retry_loop.py            # orchestrate (Loop A driver)
│   ├── code_validator.py        # extract_clean_code, validate_generated_code
│   └── llm_client.py            # multi-provider LLMClient (OpenAI / Gemini / Gemini Native / Azure)
│
├── metadata/                    # M4 — Schema Metadata (§9 M4)
│   ├── __init__.py
│   └── builder.py               # build_schema_metadata (7-key dict)
│
├── validation/                  # M5 — Validation Engine (§9 M5)
│   ├── __init__.py
│   ├── validator.py             # SchemaAwareValidator.validate (L1 → L2 → L3)
│   ├── structural.py            # L1 checks (row count, cardinality, marginal weights, etc.)
│   ├── statistical.py           # L2 checks (KS, structural residuals, group-dep transitions)
│   ├── pattern_checks.py        # L3 checks (outlier, trend_break, ranking_reversal; stubs)
│   └── autofix.py               # generate_with_validation (Loop B driver); strategies
│
├── tests/                       # see §11 for the tests tree and run command
└── docs/                        # Phase 2–local docs workspace
```

`pipeline/phase_2/` has no `pyproject.toml` or `README.md` of its own — this repo-root README is the single documentation entry point. See §2 for why there is no separate install target.

---

## 6. Key concepts

The five concepts below are the design decisions that make the rest of the pipeline possible. Each one leads with *why*.

### Closed-form DGP declaration

Each measure is declared exactly once as a complete data-generating program — either a stochastic root (distribution family + intercept-plus-effects parameter map) or a structural derivative (formula over upstream measures + categorical effects + noise). No incremental patching.

> **Why closed-form?** In previous designs, a measure's final DGP resulted from chaining `add_measure()` → `add_conditional()` → `add_dependency()` → `add_correlation()`. The declared distribution and the actual generated distribution could diverge after successive overrides. Closed-form declaration ensures each measure's statistical semantics are self-contained, verifiable, and aligned with validation. (Source: `docs/artifacts/phase_2.md` §2.3.)

The operational payoff: L2 validation can test each measure against *exactly* the distribution it declared, with no hidden override layer.

### DAG-ordered generation

All columns — categoricals, temporals, and measures — participate in a single DAG. The engine resolves generation order by topological sort.

The DAG is not an optimization: it is the *only* correct order. A structural measure that references `wait_minutes` cannot be sampled before `wait_minutes` exists. A child categorical like `department` conditioned on `hospital` cannot be sampled before `hospital`. Making the full order explicit lets the engine compose a single RNG stream across all columns, which is the determinism invariant.

A typical layering (from `phase_2.md` §2.4):

```
Layer 0 — Independent roots:           hospital, severity, visit_date
Layer 1 — Dependent non-measures:      payment_method ← P(payment | severity)
                                       department     ← P(dept | hospital)
                                       day_of_week, month ← derived from visit_date
Layer 2 — Stochastic root measures:    wait_minutes ~ LogNormal(μ(severity, hospital), σ(severity))
Layer 3 — Structural measures:         cost, satisfaction = f(wait_minutes, severity) + ε
```

See §9 M2 for `build_full_dag` / `topological_sort`.

### Dimension groups and cross-group orthogonality

Each categorical column belongs to exactly one named *dimension group*. Within a group, columns form a parent→child hierarchy (sampled conditionally). Across groups, relationships are either declared orthogonal (statistically independent) or declared via a cross-group dependency **restricted to root columns only**.

> **Design principle.** Dimension groups unify categorical, temporal, and cross-group semantics into a single abstraction. Orthogonality propagation eliminates O(n²) pairwise declarations — declaring `entity ⊥ patient` implies `hospital ⊥ severity`, `department ⊥ severity`, and so on. Restricting cross-group dependencies to roots prevents logical contradictions (e.g., a hospital-specific ward depending on severity) while keeping the dependency model simple. (Source: `phase_2.md` §2.2.)

### Three-layer validation (L1 / L2 / L3)

L1, L2, and L3 exist because they each check a different class of claim — they are not redundancy:

- **L1 — Structural.** Row count, categorical cardinality, root-marginal weight deviation, measure finiteness (`notna` + `isfinite`), cross-group chi-squared independence, measure-DAG acyclicity. What it catches: schema-level inconsistencies that indicate the declarations and the data do not line up at all.
- **L2 — Statistical.** Per-stochastic-measure KS-test over predictor-cell Cartesian products, per-structural-measure residual mean/std check, per-group-dependency conditional-transition deviation. What it catches: the data matches the declared *shape* but not the declared *distribution*.
- **L3 — Pattern.** Outlier z-score, trend-break magnitude, ranking-reversal rank correlation. What it catches: declared narrative anomalies did not actually materialize with the declared strength.

> **Why three layers, not one.** Validation runs in milliseconds, aligned with declaration level: L1 against schema, L2 against conditional distributions, L3 against declared anomalies. (Source: `phase_2.md` §2.9 closing blockquote.)

The layering also cleanly separates which loop fixes what: **semantic authoring errors** (a cycle, an undefined effect, a non-root dependency) are caught by M1 at declaration time and fixed by Loop A (re-prompt the LLM); **statistical sampling variance** (a KS p-value just under threshold, a marginal weight off by 12%) is caught by M5 and fixed by Loop B (adjust parameters and re-run M2 with a different seed).

### Atomic-grain contract

Each row represents one indivisible event. The engine does **not** materialize a cross-product cube over categoricals and then repeat.

> **Why event-level?** Generating rows as atomic events (rather than materializing a cross-product cube and repeating) produces realistic cell-occupancy distributions and is consistent with the hard constraint that each row represents one indivisible event. (Source: `phase_2.md` §2.4.)

### Design payoff

The atomic-grain fact table + dimension groups + closed-form measures combination supports the full range of downstream chart families from a single master table: distribution charts use raw rows; aggregation charts apply `GROUP BY` on hierarchy roots; drill-down charts exploit within-group parent→child structure; relationship charts leverage structural dependencies; multi-view dashboards slice along orthogonal groups; causal-reasoning QA exploits the measure DAG. Concretely:

$$\text{View}_{\text{chart}} = \sigma_{\text{filter}} \circ \gamma_{\text{agg}} \circ \pi_{\text{cols}}(M)$$

where σ = row selection, γ = group-by aggregation, π = column projection, and M is the Master Table.

---

## 7. Shared infrastructure

Three files at the root of the Phase 2 package carry cross-cutting definitions imported by every module. They contain data structures and cross-module contracts — no business logic.

### `types.py` — dataclasses and cross-module types

Grouped by consumer:

**Declaration-side (M1 → M2/M4):**

- `DimensionGroup(name, root, columns, hierarchy)` — within-group hierarchy; temporal groups carry derived features in `columns` but only the root in `hierarchy`.
- `OrthogonalPair(group_a, group_b, rationale)` — order-independent equality/hash (frozenset of group names).
- `GroupDependency(child_root, on, conditional_weights)` — root-only cross-group dependency with per-parent child-weight table.
- `PatternSpec(type, target, col, params)` — narrative anomaly spec.
- `RealismConfig(missing_rate, dirty_rate, censoring)` — optional post-generation degradation.
- `DeclarationStore` — composite container holding all of the above plus `columns`, `measure_dag`, `target_rows`, `seed`. Exposes `freeze()` (idempotent; transitions accumulating→frozen) and `_check_mutable()` (raises `RuntimeError` after freeze). This is the sole artifact crossing the M1 boundary into M2 and M4.

**Validation-side (M5):**

- `Check(name, passed, detail=None)` — single check result.
- `ValidationReport(checks)` — aggregator with `.all_passed` and `.failures` properties. Empty report is vacuously all-passed.
- `ParameterOverrides` — conceptual name for the plain nested `dict` used by Loop B (`overrides["measures"][col]["sigma"]`, `overrides["patterns"][idx]["params"]`, `overrides["reshuffle"]: list[str]`). Not a custom class.

**Stage 1 → Stage 2 handoff:**

- `SandboxResult(success, dataframe, metadata, raw_declarations, source_code, exception, traceback_str)` — result of a single sandbox attempt.
- `RetryLoopResult(success, dataframe, metadata, raw_declarations, source_code, attempts, history)` — result of the full Loop A retry loop.

Both carry a `source_code: Optional[str]` field. This is what lets Stage 1 persist the validated LLM script to `scripts/{id}.py` — without it, the successful script would be discarded at the end of the retry loop and Stage 2 would have no replay source.

The `raw_declarations` dict captured by `_TrackingSimulator` carries eight top-level keys — the seven listed above in §7 (`columns`, `groups`, `group_dependencies`, `measure_dag`, `target_rows`, `patterns`, `seed`) plus `orthogonal_pairs`. [serialization.py](../../pipeline/phase_2/serialization.py) round-trips all eight across the Stage 1 ↔ Stage 2 disk boundary.

### `exceptions.py` — typed SDK exceptions + `SkipResult` sentinel

All SDK exceptions inherit from `SimulatorError(Exception)`, enabling both narrow and broad `except` clauses. The §2.7 feedback loop relies on the narrow types:

| Exception | Raised when |
|---|---|
| `CyclicDependencyError(cycle_path)` | Cycle in the measure DAG or root-level cross-group DAG. Message includes the arrow-joined cycle path. |
| `UndefinedEffectError(effect_name, missing_value)` | An effect map is missing a definition for one of its parent categorical's values. |
| `NonRootDependencyError(column_name)` | `add_group_dependency` targets a non-root column. |
| `InvalidParameterError(param_name, value, reason)` | Computed distribution parameter outside its valid domain (e.g., `sigma < 0`). |
| `DuplicateColumnError(column_name)` | Column name registered twice. |
| `EmptyValuesError(column_name)` | `add_category` called with empty `values`. |
| `WeightLengthMismatchError(column_name, n_values, n_weights)` | `values` and `weights` lists differ in length. |
| `DegenerateDistributionError(column_name, detail)` | Distribution params collapse to a point mass or all-zero weights. |
| `ParentNotFoundError(child, parent, group)` | Parent column not found or in a different group. |
| `DuplicateGroupRootError(group_name, existing_root, attempted_root)` | Second root column attempted on a group that already has one. |
| `UndefinedPredictorError(predictor_name, context)` | Effect key references an undeclared column. |
| `PatternInjectionError(pattern_type, detail)` | Generation-time pattern injection failed (e.g., zero matching rows). |

`SkipResult(scenario_id, error_log)` is **not** an exception: it is a typed sentinel dataclass returned by M3 when all retries are exhausted. `pipeline.py` checks for it via `isinstance` and skips the scenario gracefully.

### `serialization.py` — Stage 1 ↔ Stage 2 disk boundary

```python
declarations_to_json(raw_declarations: dict[str, Any]) -> dict[str, Any]
declarations_from_json(d: dict[str, Any]) -> dict[str, Any]
```

`raw_declarations` is the dict captured from the `_TrackingSimulator` registry (columns, groups, group_dependencies, orthogonal_pairs, measure_dag, patterns, target_rows, seed). It contains dataclass instances (`DimensionGroup`, `GroupDependency`, `OrthogonalPair`) that `json.dumps` cannot handle directly; these helpers round-trip them via `dataclasses.asdict` and the matching constructors. This is the enabler for the Stage 1 → Stage 2 split (see §8): Stage 1 writes the JSON to disk, Stage 2 workers read it back without needing a shared Python process or pickle compatibility.

`pipeline.py`'s public API is documented in §9 (top-level orchestrator).

---

## 8. Pipeline control flow

Phase 2 is naturally two-phase: Loop A is LLM-bound, expensive, and non-deterministic; Loop B is deterministic and cheap (given `raw_declarations`, it is a pure function of seed and overrides). The split CLI (`agpds_generate` / `agpds_execute`) makes that cost asymmetry explicit — burn LLM tokens once to produce a validated script + declarations, then replay Stage 2 as often as you like with no further LLM calls and byte-identical CSVs per seed. The end-to-end runner (`agpds_runner`) still exists and internally chains the two stages.

### Loop A — code-level self-correction

**Mechanism.** M3 renders the §2.5 system prompt with the scenario context, asks the LLM for a `build_fact_table()` script, and calls `sandbox.execute_in_sandbox` in a fresh namespace. On typed exception, `format_error_feedback` assembles a feedback string containing the original code, the exception class + message, the traceback, and — when earlier attempts exist — a compact `PRIOR FAILED ATTEMPTS` section listing class + message (tracebacks omitted to save tokens) so the LLM does not reintroduce previously-fixed errors. The next LLM call is strictly two messages (system prompt + current-feedback user message); there is no accumulated chat history beyond what the feedback string carries.

**Catches.** *Semantic authoring errors* — cyclic DAGs, undefined effects, non-root cross-group dependencies, duplicate columns, degenerate distributions.

**Budget.** `max_retries=3` by default. On exhaustion: returns `SkipResult`.

See §9 M3 for `run_retry_loop` / `orchestrate`.

### Loop B — statistical auto-fix

**Mechanism.** M5 runs `SchemaAwareValidator(meta).validate(df, patterns)` pre-realism. On failure, it dispatches auto-fix strategies (`widen_variance`, `amplify_magnitude`, `reshuffle_pair`) via `fnmatch`-matched glob patterns on check names, accumulates deltas into a plain `overrides: dict`, and re-executes M2 with `seed = base_seed + attempt`. Validation runs on pre-realism data; realism degradation (missing/dirty values) is applied *only* after validation passes, so realism noise never causes a validation failure.

**Catches.** *Statistical sampling variance* — a KS p-value just under threshold, a marginal weight off by more than 10%, an orthogonality chi-squared failure.

**Budget.** `run_phase2` default `max_loop_b_retries=2` (i.e., `max_attempts = retries + 1 = 3` passes through `generate_with_validation`). No LLM calls.

> **KNOWN INCONSISTENCY (open).** The CLI path overrides both loops' budgets: [agpds_pipeline.py](../../pipeline/agpds_pipeline.py) lines 110 and 149 pass Loop A `max_retries=5` and Loop B `max_retries=3`, and [agpds_execute.py](../../pipeline/agpds_execute.py) line 79 also passes Loop B `max_retries=3`. So the end-to-end CLI effectively runs 5 / 3, not the programmatic-API defaults 3 / 2. Open question: unify the defaults, or keep them deliberately divergent and document the CLI override here.

See §9 M5 for `generate_with_validation`.

### Nesting

Loop A is outer (get a valid script); Loop B is inner (get a valid realization from that script). Loop B runs only after Loop A succeeds.

### Stage 1 ↔ Stage 2 disk boundary

The boundary is `output/agpds/declarations/{id}.json`. Stage 1 persists three artifacts per successful generation: `scripts/{id}.py` (the LLM source), `declarations/{id}.json` (via `serialization.declarations_to_json`), and appends one line to `manifest.jsonl`. Stage 2 reads the manifest to enumerate replay targets and calls `serialization.declarations_from_json` to rehydrate each. See §10 for the full output tree.

### Public API

The functions below live in [pipeline/phase_2/pipeline.py](../../pipeline/phase_2/pipeline.py) and are the programmatic surface for Loop A + Loop B orchestration:

```python
run_phase2(
    scenario_context: dict[str, Any],
    max_loop_a_retries: int = 3,
    max_loop_b_retries: int = 2,
    auto_fix: dict[str, Any] | None = None,
    realism_config: dict[str, Any] | None = None,
    llm_client: LLMClient | None = None,
    api_key: str | None = None,
    model: str = "gemini-2.0-flash-lite",
    provider: str = "auto",
) -> tuple[pd.DataFrame, dict[str, Any], ValidationReport] | SkipResult

run_loop_a(
    scenario_context: dict[str, Any],
    max_retries: int = 3,
    llm_client: LLMClient | None = None,
    api_key: str | None = None,
    model: str = "gemini-2.0-flash-lite",
    provider: str = "auto",
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any], str] | SkipResult

run_loop_b_from_declarations(
    raw_declarations: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    max_retries: int = 2,
    auto_fix: dict[str, Any] | None = None,
    realism_config: dict[str, Any] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any], ValidationReport] | SkipResult
```

`run_phase2` is a thin wrapper chaining both loops (backward-compatible). `run_loop_a` returns a 4-tuple `(df, metadata, raw_declarations, source_code)` on success — the 4th element is the validated LLM script string, suitable for persisting as `scripts/{id}.py`. `run_loop_b_from_declarations` takes the rehydrated declarations as its first argument and drives Loop B with no LLM involvement. These are the public functions behind `agpds_pipeline.generate_artifacts` (Stage 1) and `agpds_pipeline.execute_artifact` (Stage 2); `agpds_runner.run_single` chains them.

### Guarantees

- **Determinism.** Given a `declarations/{id}.json`, Stage 2 always produces the same CSV — same seed, same logic, same row order.
- **Parallel safety.** `agpds_execute.py` workers share no in-process state. `raw_declarations` round-trips through JSON at the disk boundary, so there are no pickling hazards.
- **Backward compatibility.** `agpds_runner.py` produces identical outputs to the pre-split version.

### M2/M4 parallel vs. serial

Stage-1 module-map diagrams show `M2 ∥ M4` because both read the frozen store and neither depends on the other. In the current implementation they are serialized: `metadata.builder.build_schema_metadata` is invoked from the tail of `engine.generator.run_pipeline`. Treat `M2 ∥ M4` as a logical annotation about the dependency graph, not as a multi-threading claim.

### Deterministic engine composition

Once Loop A has produced a valid script and M1 has frozen the declaration store, the engine is:

$$M = \tau_{\text{post}} \circ \delta^{?} \circ \gamma \circ \beta \circ \alpha(\text{seed})$$

See §9 M2 for stage mapping (α skeleton, β measures, γ patterns, δ realism, τ_post DataFrame assembly) and §4 for the canonical pipeline-split SVG.

---

## 9. Per-module detail

### Top-level orchestrator — [pipeline/phase_2/pipeline.py](../../pipeline/phase_2/pipeline.py)

**Intent.** The only file that imports from all five modules. It wires Loop A (M3↔M1) and Loop B (M5→M2) into a single call.

**Public functions.**

- `run_phase2(...)` — full Loop A + Loop B; backward-compatible with the pre-split runner.
- `run_loop_a(...)` — Stage 1 only; returns the 4-tuple `(df, metadata, raw_declarations, source_code)`.
- `run_loop_b_from_declarations(raw_declarations, ...)` — Stage 2 only; pure function of the declarations.

Full signatures are in §8.

**Private helpers.**

- `_run_loop_a(scenario_context, max_retries, llm_client)` — delegates to `orchestration.retry_loop.orchestrate`.
- `_apply_pattern_overrides(patterns, overrides)` — merges `overrides["patterns"][idx]["params"]` into a deep-copied pattern list before each Loop B rebuild.
- `_run_loop_b(df, metadata, raw_declarations, max_retries, auto_fix, realism_config)` — builds the per-attempt `build_fn` closure over the declaration fields and delegates to `validation.autofix.generate_with_validation`.

**Integration.** Imports `orchestration`, `engine`, `validation`; transitively depends on `sdk` and `metadata` through M2. It is the only file in the package aware of all five modules.

### Module READMEs

Each module has its own README with detailed interfaces, design walkthrough, and usage examples.

| Module | Location | Responsibility |
|--------|----------|----------------|
| M1: SDK Surface | [`pipeline/phase_2/sdk/README.md`](../../pipeline/phase_2/sdk/README.md) | Type-safe declaration API for LLM-generated scripts |
| M2: Generation Engine | [`pipeline/phase_2/engine/README.md`](../../pipeline/phase_2/engine/README.md) | DAG-ordered deterministic data generation |
| M3: LLM Orchestration | [`pipeline/phase_2/orchestration/README.md`](../../pipeline/phase_2/orchestration/README.md) | Prompt assembly, sandbox execution, retry loop |
| M4: Schema Metadata | [`pipeline/phase_2/metadata/README.md`](../../pipeline/phase_2/metadata/README.md) | 7-key metadata contract consumed by M5 and Phase 3 |
| M5: Validation Engine | [`pipeline/phase_2/validation/README.md`](../../pipeline/phase_2/validation/README.md) | Three-layer validation with auto-fix retry loop |

### Known stubs and limitations

**Intentional stubs (6) — each requires a spec decision before implementation:**

| Stub | Location | Behavior today | To unstub |
|---|---|---|---|
| `mixture` sampling | `engine/measures.py` `_sample_stochastic` | Declaration succeeds; `generate()` raises `NotImplementedError` | Define the mixture `param_model` schema; implement weighted-component sampling + matching KS test |
| `dominance_shift` validation | `validation/pattern_checks.py` | Declaration succeeds; validation always passes | Define the rank-change-across-temporal-split algorithm |
| `convergence` validation | `validation/pattern_checks.py` | Declaration succeeds; validation always passes | Requires full spec: what converges, over what dimension, threshold |
| `seasonal_anomaly` validation | `validation/pattern_checks.py` | Declaration succeeds; validation always passes | Requires full spec: which temporal features, detection thresholds |
| `scale` kwarg on `add_measure` | `sdk/columns.py` | Removed round-3; passing `scale=...` now raises `TypeError` | Implement a post-sampling multiplicative scaling mechanism, then restore the kwarg in `sdk/columns.py` and `orchestration/prompt.py` |
| M3 multi-error + token budget | `sdk/simulator.py`, `orchestration/sandbox.py` | One exception per attempt; full error history sent to LLM with no truncation | Collect validation errors into a compound exception; add token counting + older-failure summarization |

**Dependent stubs (4) — auto-resolve when their parent stub lands:**

| Stub | Location | Behavior today | Parent |
|---|---|---|---|
| `censoring` injection | `engine/realism.py` | Stored in `RealismConfig`; engine raises `NotImplementedError` if non-None | Spec definition of censoring |
| `ranking_reversal` / `dominance_shift` / `convergence` / `seasonal_anomaly` *injection* | `engine/patterns.py` | `inject_patterns` raises `NotImplementedError` for these four types | Spec of how to artificially create each pattern in generated data |
| Mixture KS test | `validation/statistical.py` | Returns `Check(passed=True)` for `family == "mixture"` | Parent: `mixture` sampling |
| Multi-column group-dependency `on` | `sdk/relationships.py` | `add_group_dependency` raises `NotImplementedError` unless `len(on) == 1` | Spec of nested `conditional_weights` for 2+ conditioning columns |

---

## 10. Output layout and pipeline output

### On-disk output layout

```
output/agpds/
├── scenarios/        # Phase 1 scenarios (existed before)
├── scripts/          # NEW: LLM source .py files (Stage 1)
├── declarations/     # NEW: raw_declarations JSON (Stage 1)
├── manifest.jsonl    # NEW: per-generation index (Stage 1)
├── master_tables/    # final CSVs (Stage 2 or runner)
├── schemas/          # schema metadata JSON (Stage 2 or runner)
├── charts/           # chart record JSON (Stage 2 or runner)
└── charts.json       # combined bundle (runner only)
```

Directory-by-directory:

- **`scenarios/`** — Phase 1 scenario dicts (one per scenario); input to Stage 1.
- **`scripts/{id}.py`** — the exact LLM-generated `build_fact_table()` source that passed Loop A. Hand-editable; replayable via `agpds_execute.py --ids {id}`.
- **`declarations/{id}.json`** — the `raw_declarations` dict serialized via `serialization.declarations_to_json`. This is the Stage 1 → Stage 2 contract; Stage 2 workers read it and call `declarations_from_json` to rehydrate. See §7.
- **`manifest.jsonl`** — one line per successful Stage 1 generation (one JSON object per line). `agpds_execute` enumerates replay targets from this.
- **`master_tables/{id}.csv`** — final generated DataFrame written by Stage 2 or by the end-to-end runner.
- **`schemas/{id}_metadata.json`** — the 7-key `schema_metadata` dict (see below).
- **`charts/{id}.json`** / **`charts.json`** — Phase 3 outputs (only produced by `agpds_runner.py`, which invokes downstream chart synthesis). Listed here because they appear in the tree; not within Phase 2's scope.

### Programmatic return values

| Function | Return on success | On exhaustion |
|---|---|---|
| `run_phase2(scenario_context, ...)` | `tuple[pd.DataFrame, dict, ValidationReport]` | `SkipResult` |
| `run_loop_a(scenario_context, ...)` | `tuple[pd.DataFrame, dict, dict, str]` — 4-tuple adding `raw_declarations` and `source_code` | `SkipResult` |
| `run_loop_b_from_declarations(raw_declarations, ...)` | `tuple[pd.DataFrame, dict, ValidationReport]` | `SkipResult` |

The `SkipResult` return from `run_loop_b_from_declarations` is an edge-case path, not a retry-exhaustion path — Loop B returns it only when `generate_with_validation` produced no DataFrame at all (see [pipeline.py](../../pipeline/phase_2/pipeline.py) lines 266–270). When Loop B finishes all attempts with failing checks but a DataFrame in hand, it still returns the tuple — the `ValidationReport.all_passed` field is `False` but the caller receives the DataFrame.

### `schema_metadata` reference — 7 top-level keys

| Key | Type | Contents |
|---|---|---|
| `dimension_groups` | `dict[str, {"columns": list[str], "hierarchy": list[str]}]` | Per-group column list + drill-down hierarchy. Temporal groups have derived features in `columns` but only the root in `hierarchy`. |
| `orthogonal_groups` | `list[{group_a, group_b, rationale}]` | Declared pairwise group independence. |
| `group_dependencies` | `list[{child_root, on, conditional_weights}]` | Root-level cross-group deps with full `conditional_weights`. |
| `columns` | `dict[str, dict]` | Type-discriminated descriptors, keyed by column name (see §9 M4 for fields per type). |
| `measure_dag_order` | `list[str]` | Topological order of measure columns. |
| `patterns` | `list[{type, target, col, params}]` | Injected pattern specs with full params. |
| `total_rows` | `int` | `target_rows` inherited from the scenario context. |

### Validation report

`ValidationReport(checks: list[Check])` with:

- `.all_passed: bool` — `True` iff every `check.passed`. Empty report is vacuously `True`.
- `.failures: list[Check]` — filtered list of failing checks.

Check-name prefixes the reader may encounter (see §9 M5): `row_count`, `cardinality_*`, `marginal_*`, `finite_*`, `orthogonal_*`, `measure_dag_acyclic`, `ks_*`, `structural_*_residual_mean`, `structural_*_residual_std`, `group_dep_*`, `outlier_*`, `trend_*`, `reversal_*`, `dominance`, `convergence`, `seasonal`.

### Determinism

Given a `declarations/{id}.json` file, Stage 2 always produces the same CSV — same seed, same logic, same row order. `agpds_execute.py` worker processes share no Python state; `raw_declarations` round-trips through JSON at the disk boundary, so there are no pickling hazards.

---

## 11. Testing

Phase 2 tests live in [pipeline/phase_2/tests/](../../pipeline/phase_2/tests/). The repo-root [conftest.py](../../conftest.py) injects the repo root into `sys.path`, so `pytest` resolves `pipeline.*` imports without needing the project to be pip-installed.

### Run command

From the repo root:

```bash
pytest pipeline/phase_2/tests/
```

Run a single file or directory by passing it as an argument, e.g. `pytest pipeline/phase_2/tests/modular/test_sdk_dag.py`.

### Tests tree

```
pipeline/phase_2/tests/
├── __init__.py
├── demo_end_to_end.py           # Runnable smoke demo (not a pytest test file)
├── test_retry_feedback.py       # Loop A — retry-loop error-feedback behavior
└── modular/
    ├── __init__.py
    ├── test_sdk_columns.py          # M1 — add_category / add_temporal / add_measure /
    │                                #        add_measure_structural declaration tests
    ├── test_sdk_dag.py              # M1 — detect_cycle_in_adjacency, topological_sort,
    │                                #        build_full_dag
    ├── test_sdk_validation.py       # M1 — declaration-time validation rules
    ├── test_engine_generator.py     # M2 — run_pipeline orchestration
    ├── test_engine_measures.py      # M2 — _safe_eval_formula + stochastic distribution sampling
    ├── test_metadata_builder.py     # M4 — build_schema_metadata (7 keys, deep-copy, self-check)
    ├── test_validation_structural.py # M5 — L1 checks (marginal weights, measure finiteness, etc.)
    ├── test_validation_validator.py  # M5 — SchemaAwareValidator orchestration
    └── test_validation_autofix.py    # M5 — Loop B auto-fix strategies and generate_with_validation
```

### Coverage by module

| Module | Direct test file(s) | Tested via integration / demo only |
|---|---|---|
| M1 SDK Surface | `test_sdk_columns.py`, `test_sdk_dag.py`, `test_sdk_validation.py` | `simulator.py`, `relationships.py`, `groups.py` |
| M2 Generation Engine | `test_engine_generator.py`, `test_engine_measures.py` | `skeleton.py`, `patterns.py`, `realism.py`, `postprocess.py` |
| M3 LLM Orchestration | `test_retry_feedback.py` (retry-feedback), `demo_end_to_end.py` (Loop A end-to-end smoke) | `prompt.py`, `sandbox.py`, `retry_loop.py`, `code_validator.py`, `llm_client.py` |
| M4 Schema Metadata | `test_metadata_builder.py` | — |
| M5 Validation Engine | `test_validation_validator.py`, `test_validation_structural.py`, `test_validation_autofix.py` | `statistical.py`, `pattern_checks.py` |

### Demo entry point

`pipeline/phase_2/tests/demo_end_to_end.py` runs the full pipeline against a canned scenario and is useful as a first-run smoke test for new contributors. It is deliberately *not* a pytest test file — it is a standalone script that expects a working LLM API key in the environment.

### Notes

- There is no dedicated pytest configuration (no `pytest.ini`, no `[tool.pytest.ini_options]`). The `conftest.py` is the only pytest hook and only handles `sys.path` resolution.
- Test dependencies (pytest, pytest-mock if used) are not pinned in `requirements.txt`. Install them explicitly: `pip install pytest`.
- Modules listed under "Tested via integration / demo only" above do not have direct unit-test files today; the closest coverage comes from `demo_end_to_end.py` and the integration paths exercised by `test_retry_feedback.py`. Filling these gaps is tracked in the §9 "Known stubs and limitations" table where relevant.
