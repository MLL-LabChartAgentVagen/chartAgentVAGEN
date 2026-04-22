# Split Pipeline: Generate Scripts, Execute Independently

## What this change is about

Previously, every run of `pipeline/agpds_runner.py` went end-to-end: Phase 0 (domain) → Phase 1 (scenario) → **Phase 2 Loop A (LLM → sandbox validation)** → **Phase 2 Loop B (deterministic generation + validation + auto-fix)** → save CSV/schema/chart. Every run burned LLM tokens, even when you only wanted to re-produce a dataset from a script that had already succeeded.

Phase 2 is naturally two-phase: **Loop A is expensive and non-deterministic** (LLM calls, retries, prompt drift); **Loop B is cheap and deterministic** (given `raw_declarations`, it is a pure function). This change separates them into two CLI commands so you can:

- Generate N scripts once, save them to disk.
- Re-execute those saved scripts independently (in parallel, on demand, without the LLM).
- Inspect or hand-edit the saved `.py` files before replay.
- Get byte-identical CSVs on re-run (same seed → same output).

The end-to-end `agpds_runner.py` still works as before — it now internally chains the two new stages.

## Summary of changes

### New files

- **[pipeline/agpds_generate.py](agpds_generate.py)** — Stage 1 CLI. Runs Phase 0 + Phase 1 + Phase 2 Loop A only. Persists `scripts/{id}.py`, `declarations/{id}.json`, and appends to `manifest.jsonl`.
- **[pipeline/agpds_execute.py](agpds_execute.py)** — Stage 2 CLI. Reads saved declarations and runs Phase 2 Loop B with `ProcessPoolExecutor`. No LLM calls.
- **[pipeline/phase_2/serialization.py](phase_2/serialization.py)** — `declarations_to_json` / `declarations_from_json` helpers that handle the dataclass objects (`DimensionGroup`, `GroupDependency`, `OrthogonalPair`) inside `raw_declarations`.

### Modified files

- **[pipeline/phase_2/types.py](phase_2/types.py)** — added `source_code: Optional[str]` field to `SandboxResult` and `RetryLoopResult` so the successful LLM script is no longer discarded at the end of the retry loop.
- **[pipeline/phase_2/orchestration/sandbox.py](phase_2/orchestration/sandbox.py)** — `execute_in_sandbox()` and `run_retry_loop()` now populate `source_code` on their result objects.
- **[pipeline/phase_2/orchestration/retry_loop.py](phase_2/orchestration/retry_loop.py)** — `orchestrate()` now returns a 4-tuple `(df, metadata, raw_declarations, source_code)`.
- **[pipeline/phase_2/pipeline.py](phase_2/pipeline.py)** — added two public functions:
  - `run_loop_a(scenario_context, ...) → (df, metadata, raw_declarations, source_code) | SkipResult`
  - `run_loop_b_from_declarations(raw_declarations, ...) → (df, metadata, ValidationReport) | SkipResult`
  
  `run_phase2()` is now a thin wrapper that calls both — backward-compatible.
- **[pipeline/agpds_pipeline.py](agpds_pipeline.py)** — added `generate_artifacts()` (Stage 1) and `execute_artifact()` (Stage 2) methods. `run_single()` now chains them; external behavior is unchanged.
- **[pipeline/agpds_runner.py](agpds_runner.py)** — factored the per-result file-saving block out of `save_results()` into a module-level `save_single_result()` function so Stage 2 workers can reuse the exact same output format.

### Output layout (unchanged)

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

## Usage

### Split workflow (recommended)

```bash
# Stage 1 — burn LLM tokens once, save N scripts
python -m pipeline.agpds_generate --provider gemini --count 10
python -m pipeline.agpds_generate --provider openai --count 5 --category 3

# Stage 2 — replay saved scripts (no LLM)
python -m pipeline.agpds_execute --workers 4            # execute all saved declarations
python -m pipeline.agpds_execute --workers 1            # sequential
python -m pipeline.agpds_execute --ids agpds_20260420_202948_4ba639   # subset by id
python -m pipeline.agpds_execute --ids id1,id2,id3 --workers 2        # multi subset
```

### End-to-end (one command, like before)

```bash
python -m pipeline.agpds_runner --provider gemini --count 1 --category 1
python -m pipeline.agpds_runner --provider openai --count 5
```

### Configuration

Model / provider resolution priority (all three CLIs): **CLI flag → `.env` → hardcoded fallback**.

`.env` keys:
```
OPENAI_API_KEY=...
GEMINI_API_KEY=...
OPENAI_MODEL=gpt-5.4            # optional
GEMINI_MODEL=gemini-3.1-pro-preview   # optional
LLM_PROVIDER=openai             # optional; overrides the CLI default
```

### Common CLI flags

| Flag | `agpds_generate` | `agpds_execute` | `agpds_runner` |
|---|---|---|---|
| `--api-key` | yes | — | yes |
| `--model` | yes | — | yes |
| `--provider` | yes | — | yes |
| `--category` | yes | — | yes |
| `--count` | yes | — | yes |
| `--output-dir` | yes | yes | yes |
| `--input-dir` | — | yes | — |
| `--workers` | — | yes | — |
| `--ids` | — | yes | — |

### Programmatic entry points

```python
from pipeline.phase_2.pipeline import run_loop_a, run_loop_b_from_declarations
from pipeline.phase_2.serialization import declarations_to_json, declarations_from_json

# Stage 1 — returns (df, metadata, raw_declarations, source_code) or SkipResult
loop_a = run_loop_a(scenario_context, api_key=..., model=..., provider=...)

# Persist
import json
with open("decl.json", "w") as f:
    json.dump(declarations_to_json(loop_a[2]), f)
with open("script.py", "w") as f:
    f.write(loop_a[3])

# Stage 2 — reads declarations, runs Loop B, returns (df, metadata, ValidationReport) or SkipResult
with open("decl.json") as f:
    raw_declarations = declarations_from_json(json.load(f))
df, metadata, report = run_loop_b_from_declarations(raw_declarations)
```

## Guarantees

- **Determinism**: a given `declarations/{id}.json` always produces the same CSV (same seed, same logic).
- **Backward compatibility**: `agpds_runner.py` produces identical outputs to the pre-split version.
- **Parallel safety**: `agpds_execute.py` workers share no state; `raw_declarations` round-trips through JSON on the disk boundary, so there are no pickling hazards.
