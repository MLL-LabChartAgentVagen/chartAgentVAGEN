# Stage 1: Module Map & Interactions

**System:** AGPDS Phase 2 — Agentic Data Simulator (SDK-Driven)

---

## Module Inventory

| # | Module Name | Spec Sections | Single Responsibility | Primary Input | Primary Output |
|---|---|---|---|---|---|
| M1 | **SDK Surface** | 2.1, 2.1.1, 2.1.2, 2.2, 2.3 | Provide a type-safe API that accepts column declarations, dimension-group structures, measure definitions, relationship/pattern declarations, and validates them into a coherent internal data model. | `add_*()` / `declare_*()` / `inject_*()` calls from LLM-generated Python script | Validated declaration store (column registry, dimension-group graph, measure DAG edges, pattern list) |
| M2 | **Generation Engine** | 2.4, 2.8 | Execute a fully deterministic, DAG-ordered pipeline that converts the validated declaration store into an atomic-grain Master DataFrame, row by row. | Declaration store + `seed` integer | Master DataFrame (`pd.DataFrame`) |
| M3 | **LLM Orchestration** | 2.5, 2.7 | Prompt the LLM to emit a valid SDK script for a given scenario, execute it in a sandbox, and feed typed exceptions back for self-correction up to a retry limit. | Scenario context (from Phase 1) + SDK reference | Executable Python script (or failure after max retries) |
| M4 | **Schema Metadata** | 2.6 | Build and emit the structured metadata contract that downstream phases consume to understand the generated table's semantics. | Declaration store + generated DataFrame | `schema_metadata` dict (groups, hierarchies, orthogonality, DAG order, patterns) |
| M5 | **Validation Engine** | 2.9 | Verify the generated DataFrame against its declarations at three levels (structural, statistical, pattern) and auto-fix failures without LLM calls. | Master DataFrame + `schema_metadata` | Validation report (pass/fail per check) + optionally corrected DataFrame |

**Unmapped section:** 2.10 (Design Advantages) is a rationale/justification section, not an implementable module.

---

## Module Interaction Chain

### Directed Dependencies

1. **Phase 1 → M3 (LLM Orchestration)** — Scenario context dict (title, entities, metrics, temporal grain, `target_rows`, complexity tier). **Sequential:** Phase 1 completes fully; its output is a static input to Phase 2.

2. **M3 (LLM Orchestration) → M1 (SDK Surface)** — Executable Python script (a `build_fact_table()` function containing `add_*()` / `declare_*()` / `inject_*()` calls). **Synchronous:** M3 invokes the script in a sandbox; the SDK methods execute within that call, and the orchestrator blocks until execution either succeeds or raises.

3. **M1 (SDK Surface) → M3 (LLM Orchestration)** *(feedback)* — Typed `Exception` with structured error message (e.g., `CyclicDependencyError`, `UndefinedEffectError`). **Synchronous:** the exception propagates up the call stack; M3 catches it and re-prompts the LLM with the traceback.

4. **M1 (SDK Surface) → M2 (Generation Engine)** — Validated declaration store (column registry, dimension-group graph with hierarchy pointers, measure DAG edges, pattern list, realism config) plus `seed`. **Sequential:** all `add_*()` calls have completed and passed internal validation before `generate()` begins.

5. **M1 (SDK Surface) → M4 (Schema Metadata)** — The same declaration store. **Sequential:** the metadata builder reads the finalized declarations; it does not need the generated rows, only the structural definitions.

6. **M2 (Generation Engine) → M5 (Validation Engine)** — Master DataFrame (`pd.DataFrame`, one row per atomic event). **Sequential:** the full DataFrame must be materialized before any validation check can run.

7. **M4 (Schema Metadata) → M5 (Validation Engine)** — `schema_metadata` dict (groups, hierarchies, orthogonal pairs, DAG order, pattern specs, `total_rows`). **Sequential:** the validator uses metadata as the expected-value contract against which the DataFrame is checked.

8. **M5 (Validation Engine) → M2 (Generation Engine)** *(feedback)* — Adjusted parameter set + re-execution signal (auto-fix strategies mutate declaration-level parameters, then `build_fn(seed=42+attempt)` is called again). **Sequential per retry:** a full validation pass completes, failures are collected, fixes are applied, then an entire new generation pass runs.

### Structural Roles

- **Entry point:** M3 (LLM Orchestration) — first module to execute in Phase 2, receiving scenario context from Phase 1.
- **Exit point:** M5 (Validation Engine) — its output (validated Master DataFrame + `schema_metadata` + validation report) is the final deliverable of Phase 2, consumed by Phase 3.

### Feedback Loops

**Loop A — Code-level self-correction (M3 ↔ M1).** Triggered when the SDK raises a typed exception during script execution (cyclic dependency, undefined effect, non-root cross-group dependency, etc.). The orchestrator appends code + traceback to the LLM conversation and re-prompts. Runs up to 3 retries; involves an LLM call per iteration. Fixes *semantic authoring errors* in the script itself.

**Loop B — Statistical auto-fix (M5 → M2).** Triggered when the generated DataFrame fails one or more L1/L2/L3 validation checks (KS-test failure, outlier z-score too low, orthogonality violation, etc.). Auto-fix strategies adjust numeric parameters and re-run `generate()` with a new seed offset. Runs up to 3 retries; involves *no* LLM calls. Fixes *statistical sampling variance* in an otherwise correct script.

The two loops are nested: Loop A is the outer loop (get a valid script), Loop B is the inner loop (get a valid realization from that script). Loop B only executes after Loop A has succeeded.

### Execution Order (Linear Pipeline with Conditional Backward Edges)

```
Phase 1 ──► M3 ──► M1 ──► M2 + M4 ──► M5 ──► Phase 3
              ▲      │                    │
              └──────┘                    │
              Loop A                      │
              (max 3, with LLM)           │
                                   ┌──────┘
                                   ▼
                                  M2 (re-run)
                                  Loop B
                                  (max 3, no LLM)
```

M2 and M4 read the same declaration store after M1 succeeds and may execute in parallel. They converge at M5, which requires both outputs.

---

## Module Boundary Diagram

```
                        ┌─────────────────────────────────────────────────────────┐
                        │                      PHASE 2                            │
                        │                                                         │
  ┌──────────┐          │  ┌───────────────────┐                                  │
  │          │ scenario  │  │                   │  Python script                   │
  │ PHASE 1  │─context──►│  │  M3: LLM         │─────────────────────┐            │
  │          │  dict     │  │  Orchestration    │                     │            │
  └──────────┘          │  │                   │◄────────────┐       │            │
                        │  └───────────────────┘  typed      │       │            │
                        │                         exception  │       ▼            │
                        │                         (Loop A)   │  ┌────────────┐    │
                        │                                    │  │            │    │
                        │                                    └──│  M1: SDK   │    │
                        │                                       │  Surface   │    │
                        │                                       │            │    │
                        │                                       └─────┬──────┘    │
                        │                                             │           │
                        │                              declaration store           │
                        │                           (validated, frozen)            │
                        │                                             │           │
                        │                            ┌────────────────┼────────┐  │
                        │                            │                │        │  │
                        │                            ▼                ▼        │  │
                        │                    ┌──────────────┐  ┌───────────┐   │  │
                        │                    │              │  │           │   │  │
                        │                    │  M2: Gen     │  │  M4:      │   │  │
                        │                    │  Engine      │  │  Schema   │   │  │
                        │                    │              │  │  Metadata │   │  │
                        │                    └──────┬───────┘  └─────┬─────┘   │  │
                        │                           │                │         │  │
                        │                    Master DataFrame   metadata dict  │  │
                        │                           │                │         │  │
                        │                           ▼                ▼         │  │
                        │                    ┌────────────────────────────┐     │  │
                        │                    │                            │     │  │
                        │                    │  M5: Validation Engine     │     │  │
                        │                    │                            │     │  │
                        │                    │  L1: Structural checks     │     │  │
                        │                    │  L2: Statistical checks    │     │  │
                        │                    │  L3: Pattern checks        │     │  │
                        │                    │  Auto-fix loop (Loop B)  ──┼──►M2│  │
                        │                    │                            │  re-run│
                        │                    └──────────┬─────────────────┘     │  │
                        │                               │                      │  │
                        └───────────────────────────────┼──────────────────────┘  │
                                                        │                         │
                                                        ▼                         │
                                              ┌──────────────────┐                │
                                              │    PHASE 3       │                │
                                              │                  │                │
                                              │  Receives:       │                │
                                              │  • Master DF     │                │
                                              │  • metadata dict │                │
                                              │  • val. report   │                │
                                              └──────────────────┘                │
                                                                                  │
                        └─────────────────────────────────────────────────────────┘
```

### Legend

| Arrow Label | Data Type | Mutability |
|---|---|---|
| scenario context dict | `dict` (title, entities, metrics, temporal grain, `target_rows`) | Read-only by M3 |
| Python script | String (source code of `build_fact_table()`) | Regenerated on each Loop A retry |
| typed exception | `Exception` subclass with structured message | Consumed by M3 for re-prompting |
| declaration store | Internal registries (column list, group graph, DAG edges, patterns) | Frozen after M1 succeeds |
| Master DataFrame | `pd.DataFrame` (one row per atomic event) | Regenerated on each Loop B retry |
| metadata dict | `schema_metadata` dict | Built once from declaration store |
| validation report | List of `Check` objects (name, passed, detail) | Produced fresh each validation pass |
