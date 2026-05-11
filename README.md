# ChartAgent — Atomic-Grain Chart Understanding Benchmark

ChartAgent generates chart-understanding benchmark data with **Code-as-DGP**: an LLM writes a single Python script against the `FactTableSimulator` SDK to synthesize a Master Fact Table; deterministic SQL projection (**Table Amortization**) is intended to yield 10–30+ multi-chart QA tasks per table with cross-chart arithmetic consistency.

The pipeline is split into four phases. The LLM participates only in Phases 0–2; Phase 3 is fully deterministic. The authoritative spec lives in [storyline/data_generation/](storyline/data_generation/) and is the source of truth for any design question.

---

## Pipeline at a glance

| Phase | What it does | Where | Implementation status |
|---|---|---|---|
| **0 — Domain Pool** | 200+ fine-grained sub-topics, embedding-deduped, complexity-balanced. Built once offline, cached as JSON. | [pipeline/phase_0/](pipeline/phase_0/) | shipped |
| **1 — Scenario Context** | Sample one domain → realistic `ScenarioContext` (entities, metrics with units/ranges, tier-aware `target_rows`). No chart-type binding here. | [pipeline/phase_1/](pipeline/phase_1/) | shipped |
| **2 — Agentic Data Simulator (AGPDS)** | LLM writes a `FactTableSimulator` script → `(Master DataFrame, Schema Metadata)`. Execution-error feedback + three-layer validator with auto-fix. | [pipeline/phase_2/](pipeline/phase_2/) | shipped |
| **3 — View Extraction & QA** | SQL projection enumerates `(chart_type, column_binding)` views; operator-algebra pipelines build single- and multi-chart questions. | — | **not yet implemented in `pipeline/`** — see [storyline/data_generation/phase_3.md](storyline/data_generation/phase_3.md) for the spec. |

Schema Metadata (the dict returned by `FactTableSimulator.generate()`) is the Phase 2 ↔ Phase 3 contract.

---

## Repository layout

```
chartAgentVAGEN/
├── README.md
├── storyline/data_generation/        # canonical spec for all four phases
├── pipeline/                         # Phase 0–2 implementation
│   ├── __init__.py                   # exports AGPDSPipeline
│   ├── agpds_pipeline.py             # AGPDSPipeline (four-phase orchestrator)
│   ├── agpds_runner.py               # single-shot CLI (LLM + execute, one process)
│   ├── agpds_generate.py             # Stage 1 CLI: LLM → declarations on disk
│   ├── agpds_execute.py              # Stage 2 CLI: declarations → CSV / schema / charts
│   ├── core/                         # llm_client.py, ids.py, utils.py (META_CATEGORIES)
│   ├── phase_0/                      # DomainPool / DomainSampler + build_domain_pool.py
│   ├── phase_1/                      # ScenarioContextualizer + build_scenario_pool.py
│   └── phase_2/                      # SDK + engine + orchestration + validation + metadata
│       ├── README.md                 # phase-2 detail
│       └── INTERFACES.md             # M1–M5 module contracts
├── docs/phase_2_history/             # archived Phase 2 design notes (read-only)
└── requirements.txt
```

---

## Setup

1. Create a conda env (the project's dev workflow uses one named `chart`) and install dependencies:

   ```bash
   conda create -n chart python=3.11 -y
   conda activate chart
   pip install -r requirements.txt
   ```

2. Configure LLM credentials. Either export them or drop them in a `.env` file in the repo root (auto-loaded via `python-dotenv`):

   ```bash
   # .env
   LLM_PROVIDER=gemini            # or "openai" / "azure" / "auto"
   GEMINI_API_KEY=...
   GEMINI_MODEL=gemini-2.5-pro    # optional; sane default is used otherwise
   # OPENAI_API_KEY=...
   # OPENAI_MODEL=gpt-4o-mini
   ```

3. Run the tests to confirm the install:

   ```bash
   pytest pipeline/
   ```

---

## Offline builds (run once, cached)

Both build steps are idempotent and write deterministic artifacts that every later invocation reads from disk.

```bash
# Phase 0 — build the domain pool (LLM-driven, then embedding-dedup).
python -m pipeline.phase_0.build_domain_pool
# → pipeline/phase_0/domain_pool.json

# Phase 1 — build the scenario pool over all cached domains.
python -m pipeline.phase_1.build_scenario_pool
# → pipeline/phase_1/scenario_pool.jsonl
```

After these complete, the runtime CLIs below can run in fully cached mode without any further LLM calls in Phases 0 or 1.

---

## Running the pipeline — two-stage cached flow (canonical)

The canonical workflow splits LLM work (**Stage 1**) from deterministic replay (**Stage 2**) so that scientific results can be re-derived from declarations alone.

### Stage 1 — `pipeline.agpds_generate`

The LLM writes simulator scripts against `FactTableSimulator`, the sandbox validates them, and successful declarations are persisted. Each invocation produces a `batch_<timestamp>_<hash>/` folder containing `scenarios/`, `scripts/`, `declarations/`, and a `manifest.jsonl`.

```bash
python -m pipeline.agpds_generate \
    --scenario-source cached \
    --scenario-pool-path pipeline/phase_1/scenario_pool.jsonl \
    --count 4 \
    --seed 42 \
    --output-dir ./output/agpds \
    --batch-name demo_run
```

### Stage 2 — `pipeline.agpds_execute`

Deterministic replay of saved declarations. Runs Phase 2 Loop B (generation + validation + auto-fix) without ever calling the LLM, parallelisable across declarations.

```bash
python -m pipeline.agpds_execute \
    --input-dir ./output/agpds/demo_run \
    --output-dir ./output/agpds/demo_run \
    --workers 4
```

Stage 2 writes the final `master_table.csv`, schema metadata JSON, and a charts bundle per generation alongside the existing declarations.

### Single-shot alternative — `pipeline.agpds_runner`

When a separate Stage 1 / Stage 2 split isn't needed (e.g. ad-hoc smoke runs), `agpds_runner` does both in one process:

```bash
python -m pipeline.agpds_runner --category 5 --count 1 --seed 42
```

The `--category` flag is an integer in `1..30` and maps to the 30-entry `META_CATEGORIES` taxonomy in [pipeline/core/utils.py](pipeline/core/utils.py) via `get_category_by_id`. Omit `--category` to draw from the cached scenario pool instead (`--scenario-source cached`).

---

## Programmatic surface

`AGPDSPipeline` is the only intentional re-export at the package root (per the surface declared in [pipeline/__init__.py](pipeline/__init__.py)). Everything else is addressed via fully-qualified subpackage paths.

```python
from pipeline import AGPDSPipeline

pipeline = AGPDSPipeline(seed=42)
result = pipeline.run_single(scenario_id="dom_001/k=1")  # k is 1-based
# result fields: generation_id, master_table_path, schema_path, charts_path, ...
```

**Determinism contract.** `(AGPDSPipeline(seed=S).run_single(scenario_id=ID))` is byte-deterministic: the `generation_id` and `master_table.csv` produced are bit-for-bit identical across runs. The wire format for `scenario_id` is `"dom_NNN/k=N"` (1-based `k`), constructed and parsed via [pipeline/core/ids.py](pipeline/core/ids.py). Passing both `scenario_id=` and a live `scenario_source` raises `ValueError`.

---

## Deeper reading

- Phase 0 detail: [pipeline/phase_0/README.md](pipeline/phase_0/README.md)
- Phase 1 detail: [pipeline/phase_1/README.md](pipeline/phase_1/README.md)
- Phase 2 detail: [pipeline/phase_2/README.md](pipeline/phase_2/README.md) and module contracts in [pipeline/phase_2/INTERFACES.md](pipeline/phase_2/INTERFACES.md)
- Canonical spec (start here for design questions): [storyline/data_generation/data_generation_pipeline.md](storyline/data_generation/data_generation_pipeline.md)
- Project conventions: [CLAUDE.md](CLAUDE.md)
- Phase 2 design history (read-only archive): [docs/phase_2_history/](docs/phase_2_history/)
