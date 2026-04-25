# Stage 4: Phase 2 Implementation Anatomy

**System:** AGPDS Phase 2 — Agentic Data Simulator (SDK-Driven)  
**Mode:** Architect — translating analysis into implementation blueprint  
**Prerequisite documents:** phase_2.md (spec), stage1_module_map.md, stage2_deep_dive_*.md, stage3_readiness_audit.md

---

## 1. Implementation Order

Modules are ordered by dependency depth — each module's prerequisites must be buildable (not necessarily complete) before work begins. Within each module, the recommended first file is the one with the fewest NEEDS_CLAR items, allowing early test-writing and integration scaffolding.

### Build Sequence

| Order | Module / Component | Prerequisites | Readiness (Stage 3) | First File to Implement | Rationale |
|-------|-------------------|---------------|---------------------|------------------------|-----------|
| **0** | `types.py` + `exceptions.py` | None | 100% (pure data definitions) | `types.py` | Every other module imports these. Zero ambiguity — all fields are enumerated in the deep-dives. |
| **1** | **M1: SDK Surface** (`sdk/`) | Shared types | 52% (12/23 SPEC_READY) | `dag.py` | DAG construction and topological sort are fully specified with zero NEEDS_CLAR. Provides the graph engine that `columns.py`, `relationships.py`, and M2 all depend on. Follow with `validation.py` → `groups.py` → `columns.py` → `relationships.py` → `simulator.py`. |
| **2** | **M4: Schema Metadata** (`metadata/`) | M1 types + DeclarationStore | 67% (6/9 SPEC_READY) | `builder.py` (only file) | Highest readiness of any module. The P0 enrichment decision (include all fields M5 needs) must be made up front, but once decided, implementation is a single-pass projection. Build this before M5 so the validator has its contract. |
| **3** | **M2: Generation Engine** (`engine/`) | M1 (frozen store), M4 (builder) | 50% (8/16 SPEC_READY) | `skeleton.py` | Skeleton generation (stage α) is fully specified — root categoricals, conditional children, temporal sampling. Zero NEEDS_CLAR. Follow with `postprocess.py` → `measures.py` (P0 formula evaluator needed here) → `patterns.py` → `realism.py` → `generator.py`. |
| **4** | **M5: Validation Engine** (`validation/`) | M2 (DataFrame), M4 (metadata) | 62% (13/21 SPEC_READY) | `structural.py` | All six L1 checks have exact pseudocode. Zero NEEDS_CLAR in L1 (contingent on M4 enrichment being resolved). Follow with `statistical.py` → `pattern_checks.py` → `autofix.py` (P0 mutation semantics needed here) → `validator.py`. |
| **5** | **M3: LLM Orchestration** (`orchestration/`) | M1 (for sandbox execution) | 45% (5/11 SPEC_READY) | `prompt.py` | The prompt template is fully specified verbatim in §2.5 — zero NEEDS_CLAR. Follow with `retry_loop.py` → `sandbox.py` (most NEEDS_CLAR items). |
| **6** | `pipeline.py` | All modules | N/A (integration wiring) | `pipeline.py` (only file) | Wires Loop A (M3↔M1) and Loop B (M5→M2). Build last since it depends on all module interfaces being stable. |

### P0 Blockers — Resolve Before Coding Begins

These three decisions must be locked before any implementation work starts, as they have cascading effects across multiple modules:

| # | Blocker | Decision Needed | Modules Affected | Suggested Resolution (from Stage 3) |
|---|---------|----------------|-----------------|--------------------------------------|
| **P0-1** | Enrich `schema_metadata` beyond §2.6 example | Which fields to include in the metadata dict | M4, M5 | Include all fields M5 references: `values`/`weights` on categoricals, full `param_model` on stochastic measures, `formula`/`effects`/`noise` on structural measures, `conditional_weights` on group dependencies, all `params` on patterns. Treat §2.6 example as illustrative, not exhaustive. |
| **P0-2** | Formula evaluation mechanism | How `_eval_structural` evaluates formula strings | M1 (validation), M2 (generation) | Restricted AST-based evaluator: `ast.parse(formula, mode='eval')`, walk the tree, allow only arithmetic operators (`+`, `-`, `*`, `/`, `**`), numeric literals, and variable names. No function calls, no attribute access. |
| **P0-3** | Auto-fix mutation semantics | What Loop B strategies mutate and how `generate()` is re-invoked | M2, M5 | Strategies mutate a `ParameterOverrides` dict (not the frozen `DeclarationStore`). The generate function accepts overrides: `run_pipeline(store, seed, overrides)`. Overrides are consulted at draw time for sigma scaling, pattern magnitude, etc. |

### Dependency Graph (Visual)

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

---

## 2. File Tree

```
phase_2_new/
│
├── pyproject.toml                          # Package config, dependencies (numpy, pandas, scipy)
├── README.md                               # Project overview + build order reference
│
├── phase_2/                                # Package root (flat layout — no src/ wrapper)
│   ├── __init__.py                         # Package root; re-exports pipeline entry point
│   │
│   ├── types.py                            # §2.1, §2.1.1, §2.1.2 — shared dataclasses:
│   │                                       #   ColumnDescriptor, PatternSpec, RealismConfig,
│   │                                       #   GroupDependency, OrthogonalPair, DeclarationStore
│   │
│   ├── exceptions.py                       # §2.7 — CyclicDependencyError, UndefinedEffectError,
│   │                                       #   NonRootDependencyError, DuplicateColumnError,
│   │                                       #   UndefinedPredictorError, ValidationError
│   │
│   ├── pipeline.py                         # Top-level Phase 2 orchestrator: M3 → M1 → M2 ∥ M4 → M5
│   │                                       #   Wires Loop A (M3↔M1) and Loop B (M5→M2)
│   │                                       #   Implements §2.7 outer loop + §2.9 inner loop nesting
│   │
│   ├── orchestration/                      # ── M3: LLM Orchestration (§2.5, §2.7) ──
│   │   ├── __init__.py
│   │   ├── prompt.py                       # §2.5 — prompt template assembly:
│   │   │                                   #   role preamble, SDK whitelist, HC1–HC9,
│   │   │                                   #   soft guidelines, one-shot example, scenario slot
│   │   ├── code_validator.py               # §2.5 — LLM-generated code validation (Sprint 8):
│   │   │                                   #   extract_clean_code(): strip markdown fences from
│   │   │                                   #     raw LLM responses (subtask 10.2.1)
│   │   │                                   #   validate_generated_code(): AST-level structural check
│   │   │                                   #     that build_fact_table() def + .generate() call exist
│   │   │                                   #     (subtask 10.2.2)
│   │   │                                   #   CodeValidationResult dataclass for structured results
│   │   ├── sandbox.py                      # §2.7 — sandbox execution of build_fact_table()  ⚠️
│   │   │                                   #   TODO: isolation level (exec vs subprocess),
│   │   │                                   #         timeout (default 30s), state reset
│   │   │                                   #   TODO: non-SDK exception handling (SyntaxError, etc.)
│   │   └── retry_loop.py                   # §2.7 — feedback loop: append code+traceback,
│   │                                       #   re-prompt, max_retries=3, terminal skip signal
│   │                                       #   ⚠️ TODO: context window exhaustion strategy
│   │                                       #   ⚠️ TODO: Loop A ↔ Loop B failure boundary
│   │
│   ├── sdk/                                # ── M1: SDK Surface (§2.1–§2.3) ──
│   │   ├── __init__.py                     # Re-exports FactTableSimulator
│   │   ├── simulator.py                    # §2.1 — FactTableSimulator(target_rows, seed):
│   │   │                                   #   constructor, _phase flag, generate() delegation,
│   │   │                                   #   declaration store lifecycle (accumulating → frozen)
│   │   ├── columns.py                      # §2.1.1 — add_category(), add_temporal(),
│   │   │                                   #   add_measure(), add_measure_structural()
│   │   │                                   #   All declaration-time validation: auto-normalize,
│   │   │                                   #   parent existence, DAG acyclicity, family check
│   │   │                                   #   ⚠️ TODO: mixture param_model schema
│   │   │                                   #   ⚠️ TODO: scale parameter on add_measure
│   │   ├── relationships.py                # §2.1.2 — declare_orthogonal(), add_group_dependency(),
│   │   │                                   #   inject_pattern(), set_realism()
│   │   │                                   #   ⚠️ TODO: multi-column `on` in group dependency
│   │   │                                   #   ⚠️ TODO: censoring parameter semantics
│   │   │                                   #   ⚠️ TODO: 4 under-specified pattern type param schemas
│   │   │                                   #          (dominance_shift, convergence, seasonal_anomaly,
│   │   │                                   #           ranking_reversal partial)
│   │   ├── groups.py                       # §2.2 — dimension group graph construction:
│   │   │                                   #   group registry, hierarchy tracking, temporal special case
│   │   ├── dag.py                          # §2.3 — measure DAG edge extraction from formulas,
│   │   │                                   #   full-column DAG construction (_build_full_dag),
│   │   │                                   #   topological sort, acyclicity check
│   │   └── validation.py                   # §2.1.1, §2.1.2 — declaration-time validation rules:
│   │                                       #   name uniqueness, parent-same-group, root-only deps,
│   │                                       #   effect predictor existence, per-parent weight coverage
│   │                                       #   ⚠️ TODO: per-parent weight dict missing parent values
│   │                                       #   ⚠️ TODO: negative distribution parameter clamping
│   │
│   ├── engine/                             # ── M2: Generation Engine (§2.4, §2.8) ──
│   │   ├── __init__.py
│   │   ├── generator.py                    # §2.8 — generate() pipeline orchestrator:
│   │   │                                   #   pre-flight DAG build, RNG init, stage dispatch,
│   │   │                                   #   return Tuple[DataFrame, dict]
│   │   ├── skeleton.py                     # §2.8 stage α — _build_skeleton():
│   │   │                                   #   root categoricals, conditional children,
│   │   │                                   #   cross-group dependents, temporal sampling + derivation
│   │   ├── measures.py                     # §2.8 stage β — _sample_stochastic(), _eval_structural()
│   │   │                                   #   Stochastic: intercept + Σ effects → family draw
│   │   │                                   #   Structural: formula eval + effects + noise
│   │   │                                   #   ⚠️ TODO: formula evaluation mechanism (P0)
│   │   │                                   #   ⚠️ TODO: mixture distribution sampling
│   │   │                                   #   ⚠️ TODO: noise={} default → zero noise
│   │   │                                   #   ⚠️ TODO: negative parameter clamping at draw time
│   │   ├── patterns.py                     # §2.8 stage γ — _inject_patterns():
│   │   │                                   #   outlier_entity, trend_break (fully specified)
│   │   │                                   #   ⚠️ TODO: pattern composition on overlap (P3)
│   │   │                                   #   ⚠️ TODO: pattern on structural measures → L2 exclusion
│   │   │                                   #   ⚠️ TODO: dominance_shift, convergence,
│   │   │                                   #           seasonal_anomaly, ranking_reversal (P1)
│   │   ├── realism.py                      # §2.8 stage δ — _inject_realism():
│   │   │                                   #   ⚠️ TODO: missing_rate semantics (uniform NaN)
│   │   │                                   #   ⚠️ TODO: dirty_rate semantics (categoricals only?)
│   │   │                                   #   ⚠️ TODO: missing vs dirty precedence
│   │   │                                   #   ⚠️ TODO: realism interaction with pattern cells
│   │   │                                   #   ⚠️ TODO: censoring stub
│   │   └── postprocess.py                  # §2.8 — _post_process():
│   │                                       #   ⚠️ TODO: exact behavior (DataFrame conversion,
│   │                                       #           RangeIndex, datetime64 cast)
│   │
│   ├── metadata/                           # ── M4: Schema Metadata (§2.6) ──
│   │   ├── __init__.py
│   │   └── builder.py                      # §2.6 — build_schema_metadata(declaration_store) → dict
│   │                                       #   7 top-level keys: dimension_groups, orthogonal_groups,
│   │                                       #   group_dependencies, columns, measure_dag_order,
│   │                                       #   patterns, total_rows
│   │                                       #   ⚠️ TODO: ENRICH beyond §2.6 example (P0):
│   │                                       #     add values/weights to categoricals,
│   │                                       #     full param_model to stochastic measures,
│   │                                       #     formula/effects/noise to structural measures,
│   │                                       #     conditional_weights to group_dependencies,
│   │                                       #     full params to patterns
│   │                                       #   ⚠️ TODO: internal consistency validation
│   │
│   └── validation/                         # ── M5: Validation Engine (§2.9) ──
│       ├── __init__.py
│       ├── validator.py                    # §2.9 — SchemaAwareValidator: orchestrates L1/L2/L3,
│       │                                   #   collects Check objects, dispatches auto-fix
│       ├── structural.py                   # §2.9 L1 — row count, cardinality, marginal weights,
│       │                                   #   measure finiteness, orthogonal χ², DAG acyclicity
│       ├── statistical.py                  # §2.9 L2 — KS-test per predictor cell (stochastic),
│       │                                   #   residual mean/std check (structural),
│       │                                   #   conditional transition deviation (group deps)
│       │                                   #   ⚠️ TODO: iter_predictor_cells() enumeration
│       │                                   #   ⚠️ TODO: noise_sigma=0 divide-by-zero guard
│       ├── pattern_checks.py               # §2.9 L3 — outlier z-score, trend break magnitude,
│       │                                   #   ranking reversal correlation
│       │                                   #   ⚠️ TODO: dominance_shift validation logic
│       │                                   #   ⚠️ TODO: convergence, seasonal_anomaly stubs
│       └── autofix.py                      # §2.9 — generate_with_validation() Loop B wrapper:
│                                           #   AUTO_FIX dispatch (widen_variance, amplify_magnitude,
│                                           #   reshuffle_pair), seed=base+attempt, max 3 retries
│                                           #   ⚠️ TODO: mutation target — override dict vs. store (P0)
│                                           #   ⚠️ TODO: validation pre- vs. post-realism ordering
│
└── tests/
    ├── __init__.py
    ├── demo_end_to_end.py                  # Runnable demo script: direct SDK usage + sandbox
    │                                       #   execution, prints output for manual inspection
    ├── test_end_to_end.py                  # End-to-end integration: full stack from declaration
    │                                       #   → DAG → skeleton → postprocess → patterns → realism
    │                                       #   → validation, using the public SDK API
    └── modular/                            # ── Fine-grained per-file unit tests ──
        ├── __init__.py
        ├── test_sdk_columns.py             # M1 — add_category, add_temporal, add_measure,
        │                                   #   add_measure_structural + declaration-time validation
        ├── test_sdk_dag.py                 # M1 — topological_sort, acyclicity check, edge extraction
        ├── test_sdk_groups.py              # M1 — register_categorical_column, group registry,
        │                                   #   hierarchy tracking
        ├── test_sdk_relationships.py       # M1 — declare_orthogonal, add_group_dependency,
        │                                   #   inject_pattern, set_realism
        ├── test_sdk_validation.py          # M1 — validate_column_name, uniqueness, parent checks,
        │                                   #   effect predictor existence
        ├── test_engine_generator.py        # M2 — run_pipeline orchestrator, stage dispatch,
        │                                   #   determinism
        ├── test_engine_postprocess.py      # M2 — to_dataframe, DataFrame assembly from column arrays
        ├── test_metadata_builder.py        # M4 — build_schema_metadata output shape, enrichment
        │                                   #   completeness
        ├── test_validation_structural.py   # M5 L1 — check_row_count, cardinality, marginal weights,
        │                                   #   finiteness checks
        ├── test_validation_pattern.py      # M5 L3 — check_outlier_entity, trend break magnitude,
        │                                   #   ranking reversal correlation
        ├── test_validation_autofix.py      # M5 — match_strategy, Loop B auto-fix routines
        │                                   #   (widen_variance, amplify_magnitude, reshuffle_pair)
        └── test_validation_validator.py    # M5 — SchemaAwareValidator orchestration logic,
                                            #   L1/L2/L3 dispatch, Check collection
```

### ⚠️ NEEDS_CLAR Distribution

| Module Dir | Files with ⚠️ | TODO Count |
|---|---|---|
| `orchestration/` | `sandbox.py`, `retry_loop.py` | 6 |
| `sdk/` | `columns.py`, `relationships.py`, `validation.py` | 11 |
| `engine/` | `measures.py`, `patterns.py`, `realism.py`, `postprocess.py` | 8 |
| `metadata/` | `builder.py` | 3 |
| `validation/` | `statistical.py`, `pattern_checks.py`, `autofix.py` | 8 |

---

## 3. Per-Module Explanations

---

### Shared Infrastructure — `phase_2/`

**Purpose:** Three files at the package root provide cross-cutting definitions that every module imports. They contain no business logic — only data structures, exception types, and the top-level pipeline wiring.

#### `types.py`
- **Implements:** §2.1, §2.1.1, §2.1.2, §2.2
- **Key classes/functions:**
  - `ColumnDescriptor` — Frozen dataclass with fields: `name`, `type` (categorical / temporal / measure), `group`, `parent`, `family`, `param_model`, `formula`, `effects`, `noise`, `derive`, `values`, `weights`, `scale`. Not every field is populated for every column type; unused fields default to `None`. This is the canonical per-column record that flows from M1 into M2 and M4.
  - `PatternSpec` — Dataclass: `type` (str enum), `target` (filter expression string), `col` (column name), `params` (dict).
  - `OrthogonalPair` — Dataclass: `group_a`, `group_b`, `rationale`.
  - `GroupDependency` — Dataclass: `child_root`, `on` (list of root column names), `conditional_weights` (nested dict).
  - `RealismConfig` — Optional dataclass: `missing_rate`, `dirty_rate`, `censoring`.
  - `DeclarationStore` — The compound container holding: `column_registry: list[ColumnDescriptor]`, `group_graph: dict[str, GroupInfo]`, `measure_dag_edges: set[tuple[str, str]]`, `orthogonal_pairs: list[OrthogonalPair]`, `group_deps: list[GroupDependency]`, `pattern_list: list[PatternSpec]`, `realism_config: RealismConfig | None`, `target_rows: int`, `seed: int`. Exposes a `freeze()` method that transitions it from mutable to read-only. This is the single artifact that crosses the M1 boundary into M2 and M4.
  - `Check` — Validation result record: `name`, `passed` (bool), `detail` (str | None). Used by M5.
  - `ValidationReport` — List of `Check` objects plus aggregate pass/fail.
- **Internal data flow:** Pure data definitions — no logic, no imports from other `phase_2` modules. Every other module imports from here.

#### `exceptions.py`
- **Implements:** §2.7 (exception types consumed by M3's retry loop)
- **Key classes:**
  - `SDKError` — Base class for all typed SDK exceptions. Carries a structured `message` string.
  - `CyclicDependencyError(SDKError)` — Raised by DAG validation when a cycle is detected.
  - `UndefinedEffectError(SDKError)` — Raised when a formula or `param_model` references an undefined symbol.
  - `NonRootDependencyError(SDKError)` — Raised when `add_group_dependency` targets a non-root column.
  - `DuplicateColumnError(SDKError)` — Raised on duplicate `name` (suggested resolution from Stage 3).
  - `UndefinedPredictorError(SDKError)` — Raised when an effects key references a not-yet-declared column.
  - `SkipResult` — Sentinel returned by M3 when all retries are exhausted. Not an exception — a typed return value that the pipeline orchestrator checks.
- **Internal data flow:** No dependencies. Imported by `sdk/` (raises), `orchestration/` (catches), and `pipeline.py` (checks `SkipResult`).

#### `pipeline.py`
- **Implements:** Stage 1 module interaction chain — the top-level Phase 2 orchestrator
- **Key functions:**
  - `run_phase2(scenario_context: dict) → tuple[pd.DataFrame, dict, ValidationReport] | SkipResult` — The entry point. Wires: (1) M3's `orchestrate()` to produce a validated script or `SkipResult`, (2) on success, executes the script to populate the `DeclarationStore` in M1, (3) calls M4's `build_schema_metadata()` (can run in parallel with M2 since both read the frozen store), (4) calls M2's `generate()` to produce the DataFrame, (5) passes both to M5's `generate_with_validation()` which wraps Loop B.
  - `_run_loop_a(scenario_context) → Callable | SkipResult` — Delegates to M3. Returns the `build_fact_table` callable or `SkipResult`.
  - `_run_loop_b(build_fn, declaration_store, schema_metadata) → tuple[DataFrame, ValidationReport]` — Delegates to M5's auto-fix wrapper. Handles the nested loop relationship: Loop A is outer (with LLM), Loop B is inner (no LLM).
- **Internal data flow:** Imports from `orchestration`, `sdk`, `engine`, `metadata`, and `validation`. This is the only file that knows about all five modules simultaneously.

**Module integration points:**
- Receives `scenario_context` dict from Phase 1 (external).
- Produces `(DataFrame, schema_metadata, ValidationReport)` for Phase 3 (external).

---

### Module: LLM Orchestration (M3) — `phase_2/orchestration/`

**Purpose:** M3 is the entry point of Phase 2. It translates a Phase 1 scenario context into a valid, executable `build_fact_table()` Python script by prompting an LLM and iterating through an error-feedback retry loop. Its only stateful artifact is the LLM conversation history, which grows with each retry as failed scripts and their tracebacks are appended. M3 makes the only LLM calls in the entire Phase 2 pipeline — everything downstream is pure computation.

**Files:**

#### `prompt.py`
- **Implements:** §2.5
- **Key classes/functions:**
  - `PromptTemplate` — Stores the five prompt zones as composable string segments: role preamble, SDK method whitelist (Step 1 + Step 2 blocks), hard constraints (HC1–HC9), soft guidelines, and the one-shot example.
  - `assemble_prompt(scenario_context: dict) → list[dict]` — Takes the Phase 1 scenario dict (title, entities, metrics, temporal grain, `target_rows`, complexity tier), serializes it into the `[SCENARIO]` block format, fills the `{scenario_context}` slot, and returns the initial message list (`messages[0]` = system prompt with all five zones). This is the immutable foundation of the conversation that persists across retries.
  - `SUPPORTED_FAMILIES: list[str]` — The eight distribution family names: `gaussian`, `lognormal`, `gamma`, `beta`, `uniform`, `poisson`, `exponential`, `mixture`.
  - `SUPPORTED_PATTERNS: list[str]` — The six pattern types: `outlier_entity`, `trend_break`, `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`.
- **Internal data flow:** `assemble_prompt()` is called once by `retry_loop.py` to initialize the conversation. The output is a `list[dict]` (messages array) passed by reference — `retry_loop.py` appends to it.
- **NEEDS_CLAR items:** None in this file — the prompt template is fully specified in §2.5.

#### `sandbox.py`
- **Implements:** §2.7 step 2
- **Key classes/functions:**
  - `SandboxExecutor` — Encapsulates the execution environment for LLM-generated scripts.
    - `execute(script: str, sdk_module) → DeclarationStore` — Runs the script in a controlled scope. On success, returns the frozen `DeclarationStore` from the `FactTableSimulator` instance the script created. On exception, re-raises so the retry loop can catch it.
    - `_create_exec_scope(sdk_module) → dict` — Builds the namespace dict for `exec()`, injecting the `FactTableSimulator` class and any other allowed imports.
  - `SandboxConfig` — Dataclass: `timeout_seconds` (default 30), `isolation_level` (enum: `EXEC_IN_PROCESS` | `SUBPROCESS`).
- **Internal data flow:** Called by `retry_loop.py` on each attempt. Imports `FactTableSimulator` from `sdk/` and makes it available inside the exec scope. Returns to `retry_loop.py` either a `DeclarationStore` or raises an `Exception`.
- **NEEDS_CLAR items:**
  - TODO: Isolation level — `exec()` in-process vs. subprocess vs. container. Suggested default: `exec()` in a fresh namespace with configurable timeout.
  - TODO: State reset between retries — each execution must instantiate a fresh `FactTableSimulator`. The exec scope is rebuilt per attempt.
  - TODO: Timeout mechanism — use `signal.alarm` (Unix) or `threading.Timer` for the configurable timeout.
  - TODO: Non-SDK exception handling — catch all `Exception` subclasses; relay full traceback regardless of type.

#### `retry_loop.py`
- **Implements:** §2.7
- **Key classes/functions:**
  - `orchestrate(scenario_context: dict, llm_client, sandbox: SandboxExecutor, max_retries: int = 3) → DeclarationStore | SkipResult` — The Loop A driver. Steps: (1) call `assemble_prompt()` to build initial messages, (2) for each attempt: call `llm_client` to generate a script, append the assistant message, call `sandbox.execute()`, on success return the `DeclarationStore`, on exception append a user message with code + traceback and the re-prompt text "Adjust parameters to resolve the error", (3) after exhausting retries, return `SkipResult` with logged failure details.
  - `_extract_script(llm_response) → str` — Parses the LLM's response to extract the Python code block.
  - `_format_error_feedback(script: str, exception: Exception) → str` — Formats the code + traceback into the user-turn message for the next retry.
- **Internal data flow:** Consumes `prompt.py`'s `assemble_prompt()` output as the conversation seed. Calls `sandbox.py`'s `execute()` per attempt. The conversation history (`list[dict]`) accumulates in-place: system message (frozen) + pairs of (assistant: script, user: code+traceback) per failure. Up to 8 messages at max retries.
- **NEEDS_CLAR items:**
  - TODO: Context window exhaustion strategy — keep full history for 3 retries (fits most models); add token-budget check before each retry.
  - TODO: `build_fact_table` function signature enforcement — parse AST to verify name and `seed` parameter.
  - TODO: Loop A ↔ Loop B failure boundary — if Loop B exhausts retries, this does not re-enter Loop A (confirmed by Stage 1 module map).
  - TODO: Skip signal format — return `SkipResult(scenario_id, error_log)`.

**Module integration points:**
- Receives `scenario_context` dict from Phase 1 (via `pipeline.py`).
- Receives `Exception` objects from M1 (SDK) during sandbox execution.
- Produces frozen `DeclarationStore` for M1/M2/M4 on success, or `SkipResult` on terminal failure.

---

### Module: SDK Surface (M1) — `phase_2/sdk/`

**Purpose:** M1 provides the strongly-typed, builder-pattern API that the LLM-generated script calls. It accepts column declarations, dimension-group structures, measure definitions, and relationship/pattern declarations, validating each incrementally, and accumulates them into a coherent `DeclarationStore`. The store transitions through three lifecycle phases: accumulating (during method calls), frozen (after the last call returns and before `generate()` begins), and consumed (read by M2, M4, M5). M1's validation is the primary defense against semantic errors in LLM-generated code, and its typed exceptions are the feedback signal for Loop A.

**Files:**

#### `simulator.py`
- **Implements:** §2.1
- **Key classes/functions:**
  - `FactTableSimulator` — The public-facing SDK class.
    - `__init__(self, target_rows: int, seed: int)` — Validates `target_rows >= 1`, stores `seed`, initializes an empty `DeclarationStore` in accumulating mode. Creates internal `_phase` flag set to `STEP_1`.
    - `generate(self) → tuple[pd.DataFrame, dict]` — Freezes the declaration store, delegates to `engine.generator.run_pipeline()` for the DataFrame and `metadata.builder.build_schema_metadata()` for the dict. This is the boundary where M1 ends and M2+M4 begin.
    - `_get_store(self) → DeclarationStore` — Internal accessor for the mutable store, used by `columns.py` and `relationships.py`.
  - The class itself is thin — all method logic lives in `columns.py` and `relationships.py`, which are mixed in or called as delegates.
- **Internal data flow:** Constructor creates the `DeclarationStore`. Step 1 methods (in `columns.py`) and Step 2 methods (in `relationships.py`) mutate it. `generate()` freezes it and passes it downstream.
- **NEEDS_CLAR items:**
  - TODO: `target_rows = 0` or negative — raise `ValueError` in constructor.
  - TODO: Multiple `generate()` calls on same instance — disallow; raise after first call.

#### `columns.py`
- **Implements:** §2.1.1
- **Key functions (attached to `FactTableSimulator` via delegation or mixin):**
  - `add_category(name, values, weights, group, parent=None)` — Validates: non-empty `values`, unique column name, if `parent` then parent exists in same group, auto-normalizes weights (flat list or per-parent dict). Appends a `ColumnDescriptor(type="categorical")` to `column_registry`. Updates `group_graph` with group membership and hierarchy pointers.
  - `add_temporal(name, start, end, freq, derive=[])` — Validates: `start < end`, `freq` is supported. Creates the root temporal `ColumnDescriptor` plus one `ColumnDescriptor` per derived feature (`day_of_week`, `month`, `quarter`, `is_weekend`). All enter the column registry and the temporal group. Derived columns have `type="temporal"` and `derived=True`.
  - `add_measure(name, family, param_model, scale=None)` — Validates: `family` in `SUPPORTED_FAMILIES`, all effect predictor columns exist in registry, all symbolic effects have numeric definitions. Creates a `ColumnDescriptor(type="measure", measure_type="stochastic")`. No DAG edges (root measure).
  - `add_measure_structural(name, formula, effects={}, noise={})` — Validates: every symbol in `formula` resolves to a declared measure or an effects key, no self-reference, DAG acyclicity after adding edges. Creates `ColumnDescriptor(type="measure", measure_type="structural")`. Adds edges to `measure_dag_edges`.
  - `_validate_phase_step1(self)` — Checks that `_phase` is `STEP_1`; raises if Step 2 methods have already been called.
- **Internal data flow:** Each method reads and mutates the `DeclarationStore` via `simulator._get_store()`. `add_category` → `group_graph` + `column_registry`. `add_measure_structural` → `column_registry` + `measure_dag_edges`. Validation uses `dag.py` for acyclicity checks.
- **NEEDS_CLAR items:**
  - TODO: `mixture` distribution `param_model` schema — unspecified how component distributions and mixing weights are expressed. Stub: accept but log warning; defer to future spec.
  - TODO: `scale` parameter on `add_measure` — undocumented. Accept and store; do not use in generation until clarified.
  - TODO: Per-parent weight dict missing a parent value — raise `ValueError` requiring complete coverage.
  - TODO: Effects referencing not-yet-declared columns — validate at declaration time; raise `UndefinedPredictorError`.

#### `relationships.py`
- **Implements:** §2.1.2
- **Key functions:**
  - `declare_orthogonal(group_a, group_b, rationale)` — Validates: both groups exist in `group_graph`, groups are distinct. Appends an `OrthogonalPair` to the store.
  - `add_group_dependency(child_root, on, conditional_weights)` — Validates: `child_root` and all columns in `on` are roots (`parent=None`), no cycle in the root-level dependency DAG, `conditional_weights` keys cover all values of the `on` column(s). Appends a `GroupDependency` to the store. Adds edges to the full-column DAG (from each `on` column to `child_root`).
  - `inject_pattern(type, target, col, **params)` — Validates: `type` in `SUPPORTED_PATTERNS`, `col` exists in column registry as a measure. Appends a `PatternSpec` to the store.
  - `set_realism(missing_rate=0.0, dirty_rate=0.0, censoring=None)` — Stores a `RealismConfig` singleton. Overwrites if called multiple times.
  - `_validate_phase_step2(self)` — Transitions `_phase` from `STEP_1` to `STEP_2` on first call. Subsequent Step 1 method calls are rejected.
- **Internal data flow:** Each method reads and mutates the `DeclarationStore`. The `_phase` flag transition happens on the first call to any Step 2 method. `add_group_dependency` also uses `dag.py` for root-DAG acyclicity.
- **NEEDS_CLAR items:**
  - TODO: Multi-column `on` in `add_group_dependency` — the nested `conditional_weights` structure for 2+ conditioning roots is unspecified. Stub: support single-column only; raise `NotImplementedError` for multi-column.
  - TODO: `censoring` parameter semantics — accept and store; stub in engine. Only `missing_rate` and `dirty_rate` are implemented.
  - TODO: Four under-specified pattern type param schemas — `dominance_shift`, `convergence`, `seasonal_anomaly` have no defined params. `ranking_reversal` is partial. Accept any `params` dict; validate only `outlier_entity` and `trend_break` params.
  - TODO: `target` filter string syntax — no formal grammar specified. Implement a simple evaluator supporting `column == "value"` with `and`/`or`.

#### `groups.py`
- **Implements:** §2.2
- **Key classes/functions:**
  - `GroupInfo` — Dataclass: `name`, `root` (column name), `columns` (list), `hierarchy` (list, root-first).
  - `build_group_graph(column_registry) → dict[str, GroupInfo]` — Constructs the group graph from the column registry. For each group, identifies the root (the column with `parent=None`), builds the hierarchy chain by following parent pointers, and collects all member columns. Temporal groups get special treatment: `hierarchy` contains only the root date column, not derived features.
  - `get_roots(group_graph) → list[str]` — Returns root column names across all groups. Used by `relationships.py` for root-only validation.
- **Internal data flow:** Called incrementally by `columns.py` (each `add_category`/`add_temporal` call updates the group graph). Also called by `dag.py` to identify hierarchy edges for the full-column DAG.
- **NEEDS_CLAR items:** None — group structure is well-specified in §2.2.

#### `dag.py`
- **Implements:** §2.3, plus the unified full-column DAG from §2.4
- **Key functions:**
  - `add_measure_edge(edges: set, upstream: str, downstream: str)` — Adds a directed edge and checks for immediate cycle.
  - `topological_sort(edges: set, nodes: list) → list[str]` — Kahn's algorithm. Raises `CyclicDependencyError` if cycle detected.
  - `build_full_dag(declaration_store) → tuple[dict, list[str]]` — Assembles the unified DAG from four edge sources: (1) within-group hierarchy (`parent` → child), (2) cross-group root dependencies, (3) temporal derivation (root → derived features), (4) measure formula references. Returns the adjacency dict and the topological order. Used by M2's pre-flight step and by M1 for incremental validation.
  - `is_acyclic(order: list) → bool` — Simple check used by M5's L1 redundant acyclicity test.
- **Internal data flow:** `columns.py` calls `add_measure_edge()` during `add_measure_structural()`. `relationships.py` calls `add_measure_edge()` for root-DAG edges during `add_group_dependency()`. `generator.py` (M2) calls `build_full_dag()` at pre-flight time.
- **NEEDS_CLAR items:** None — DAG construction and topological sort are well-specified.

#### `validation.py`
- **Implements:** §2.1.1, §2.1.2 validation rules consolidated
- **Key functions:**
  - `validate_column_name(name, registry) → None | raises DuplicateColumnError` — Enforces uniqueness.
  - `validate_parent(parent, group, registry) → None | raises SDKError` — Checks existence and same-group membership.
  - `validate_weights(values, weights, parent_values=None) → list[float]` — Auto-normalizes. Raises on empty values. For per-parent dicts, validates coverage of all parent values.
  - `validate_family(family) → None | raises ValueError` — Checks against `SUPPORTED_FAMILIES`.
  - `validate_effects_predictors(effects, registry) → None | raises UndefinedPredictorError` — Checks that all effect keys reference existing columns.
  - `validate_formula_symbols(formula, registry, effects) → set[str]` — Parses formula to extract variable names, verifies each resolves to a declared measure or effects key, returns the set of upstream measure dependencies.
  - `validate_root_only(col_name, registry) → None | raises NonRootDependencyError` — Checks `parent=None`.
- **Internal data flow:** Called by `columns.py` and `relationships.py` during every declaration method. Pure validation — no state mutation.
- **NEEDS_CLAR items:**
  - TODO: Per-parent weight dict with missing parent values — raise `ValueError` requiring complete coverage of every parent value.
  - TODO: Negative distribution parameters from additive effects — cannot validate at declaration time (depends on runtime context). Defer to generation-time clamping in M2.
  - TODO: `target` filter string validation for `inject_pattern` — validate syntax at declaration time with a simple parser.

**Module integration points:**
- Receives executable Python script from M3 (via sandbox execution).
- Produces frozen `DeclarationStore` for M2 (generation) and M4 (metadata).
- Produces typed `Exception` objects back to M3 (Loop A feedback).

---

### Module: Generation Engine (M2) — `phase_2/engine/`

**Purpose:** M2 is the deterministic computation core. It takes a frozen `DeclarationStore` and a seed integer and produces a Master DataFrame through a four-stage pipeline: skeleton (α), measures (β), patterns (γ), and realism (δ). The pipeline maintains a single `numpy.random.Generator` stream whose sequential consumption order is the sole guarantor of bit-for-bit reproducibility. No LLM calls occur in this module. M2 is subject to re-execution by Loop B (M5 auto-fix), where the seed is offset by the attempt number.

**Files:**

#### `generator.py`
- **Implements:** §2.8 — pipeline orchestrator
- **Key classes/functions:**
  - `run_pipeline(store: DeclarationStore, seed: int, overrides: ParameterOverrides = None) → tuple[pd.DataFrame, dict]` — The `generate()` entry point. Steps: (1) pre-flight: call `dag.build_full_dag(store)` to get `topo_order`, (2) init `rng = np.random.default_rng(seed)`, (3) call `skeleton.build_skeleton(store, topo_order, rng)` → partial row dict, (4) call `measures.generate_measures(store, topo_order, rows, rng, overrides)` → full row dict, (5) call `patterns.inject_patterns(store, rows, rng, overrides)` → modified rows, (6) if `store.realism_config`: call `realism.inject_realism(store, rows, rng)` → degraded rows, (7) call `postprocess.to_dataframe(rows)` → `pd.DataFrame`, (8) call `metadata.builder.build_schema_metadata(store)` → dict, (9) return tuple.
  - The single `rng` object is passed by reference through all stages — this is the critical invariant for determinism.
  - The optional `overrides` parameter is the mechanism by which Loop B's auto-fix strategies take effect without mutating the frozen store.
- **Internal data flow:** Calls into `skeleton.py`, `measures.py`, `patterns.py`, `realism.py`, `postprocess.py` sequentially. Also calls `dag.py` (from M1) for pre-flight DAG construction and `metadata/builder.py` (M4) for the metadata dict.
- **NEEDS_CLAR items:** None in this file — the pipeline structure is fully specified.

#### `skeleton.py`
- **Implements:** §2.8 stage α
- **Key functions:**
  - `build_skeleton(store: DeclarationStore, topo_order: list[str], rng) → dict[str, np.ndarray]` — Iterates `topo_order`, skipping measure columns. For each non-measure column, dispatches to the appropriate sampler:
    - Root categoricals → `_sample_root_categorical(col, target_rows, rng)` — draws from marginal weights using `rng.choice()`.
    - Child categoricals → `_sample_child_categorical(col, parent_values, rng)` — per-row conditional draw based on parent column's value. Handles both flat-broadcast and per-parent-dict weight variants.
    - Cross-group root dependents → `_sample_dependent_root(col, dep, upstream_values, rng)` — draws from `conditional_weights` keyed by upstream root's value.
    - Temporal root → `_sample_temporal(col, target_rows, rng)` — uniform sampling within `[start, end]` at declared `freq`.
    - Temporal derived → `_derive_temporal(col, root_dates)` — deterministic extraction (`DOW()`, `MONTH()`, `QUARTER()`, `IS_WEEKEND()`). No RNG consumption.
  - Returns a dict mapping column name → numpy array of length `target_rows`.
- **Internal data flow:** Reads `store.column_registry`, `store.group_deps`, and `store.group_graph`. Outputs feed directly into `measures.py`.
- **NEEDS_CLAR items:** None — skeleton generation is well-specified in §2.4 and §2.8.

#### `measures.py`
- **Implements:** §2.8 stage β, §2.3
- **Key functions:**
  - `generate_measures(store, topo_order, rows, rng, overrides=None) → dict[str, np.ndarray]` — Iterates `topo_order`, processing only measure columns. Dispatches based on `measure_type`:
    - `_sample_stochastic(col: ColumnDescriptor, rows, rng, overrides) → np.ndarray` — For each row: computes each distribution parameter as `intercept + Σ effects[predictor_col][row_value]`, applies any `overrides` scaling, then draws from the named family. Uses `rng` for the draw. Supported families dispatch to: `rng.normal()`, `rng.lognormal()`, `rng.gamma()`, `rng.beta()`, `rng.uniform()`, `rng.poisson()`, `rng.exponential()`.
    - `_eval_structural(col: ColumnDescriptor, rows, rng, overrides) → np.ndarray` — Evaluates the formula string with variable bindings from the row context (upstream measure values + resolved effects). Adds noise drawn from the declared noise family/params if `noise != {}`.
    - `_resolve_effects(effects_dict, rows, col_names) → np.ndarray` — Vectorized effect resolution: for each row, looks up the categorical context and sums the matching effect offsets.
    - `_clamp_params(params, family) → dict` — Runtime clamping to valid ranges (e.g., `sigma = max(sigma, 1e-6)` for gaussian). Logs a warning on clamp.
    - `_evaluate_formula(formula: str, bindings: dict) → float | np.ndarray` — The restricted AST-based expression evaluator. Parses via `ast.parse(formula, mode='eval')`, walks the tree accepting only `BinOp` (`+`, `-`, `*`, `/`, `Pow`), `UnaryOp` (`-`), `Num`/`Constant`, and `Name` nodes. `Name` nodes resolve from `bindings`. All other AST node types raise `ValueError`.
- **Internal data flow:** Reads `rows` (from skeleton), reads `store.column_registry` for descriptors. Mutates `rows` dict in place, adding measure columns. The `rng` advances by one draw per stochastic measure per row, plus one noise draw per structural measure per row (if noise is specified).
- **NEEDS_CLAR items:**
  - TODO (P0): Formula evaluation mechanism — implement via `_evaluate_formula()` using restricted AST walker as described above.
  - TODO: `mixture` distribution — stub: raise `NotImplementedError("mixture family not yet specified")`.
  - TODO: `noise={}` default — treat as zero noise; skip noise draw; no RNG consumption for this column.
  - TODO: Negative parameter clamping — `_clamp_params()` handles this at draw time with per-family valid ranges.

#### `patterns.py`
- **Implements:** §2.8 stage γ
- **Key functions:**
  - `inject_patterns(store, rows: dict, rng, overrides=None) → dict` — Iterates `store.pattern_list` in declaration order. For each pattern, calls the type-specific injector. Returns the modified rows dict. Also returns a `pattern_mask: dict[str, np.ndarray[bool]]` indicating which cells were modified by patterns (for realism exclusion and L2 residual exclusion).
  - `_inject_outlier_entity(pattern, rows, rng) → np.ndarray[bool]` — Parses `target` filter, selects matching rows, scales the `col` values to achieve the declared `z_score` relative to the overall column distribution. Returns the modified-cell mask.
  - `_inject_trend_break(pattern, rows, rng) → np.ndarray[bool]` — Splits rows by the temporal `break_point`, applies a magnitude shift to post-break values in the `col` column.
  - `_parse_target_filter(target: str, rows) → np.ndarray[bool]` — Evaluates the filter expression against row values. Returns a boolean mask. Supports `column == "value"` with `and`/`or` connectors.
- **Internal data flow:** Reads `store.pattern_list` and mutates `rows` in place. The `pattern_mask` output flows to `realism.py` (to skip pattern cells) and to M5 (for L2 residual exclusion).
- **NEEDS_CLAR items:**
  - TODO: Pattern composition when targets overlap — apply in declaration order; sequential mutation.
  - TODO: Pattern injection on structural measures — mark pattern-modified cells so M5's L2 residual check excludes them.
  - TODO: `dominance_shift` injector — stub with TODO. Suggested params: `{entity_filter, col, before_rank, after_rank, split_point}`.
  - TODO: `convergence` injector — stub.
  - TODO: `seasonal_anomaly` injector — stub.
  - TODO: `ranking_reversal` injector — partially specified. Implement basic version.

#### `realism.py`
- **Implements:** §2.8 stage δ
- **Key functions:**
  - `inject_realism(store, rows: dict, rng, pattern_mask=None) → dict` — Applies realism degradation based on `store.realism_config`. Processes `missing_rate` first (precedence), then `dirty_rate`. Skips cells in `pattern_mask`.
  - `_inject_missing(rows, rate, rng, protected_cells=None) → dict` — For each column, randomly selects `rate` fraction of rows and replaces values with `np.nan`. Skips cells in `protected_cells`.
  - `_inject_dirty(rows, rate, rng, column_registry, protected_cells=None) → dict` — For categorical columns only, randomly swaps values to another valid value from the column's `values` list.
- **Internal data flow:** Reads `store.realism_config` and `store.column_registry`. Mutates `rows` in place. Consumes `rng` for random cell selection.
- **NEEDS_CLAR items:**
  - TODO: Which columns get `missing_rate` — all columns uniformly.
  - TODO: `dirty_rate` applies to categoricals only.
  - TODO: Missing vs. dirty precedence — missing takes precedence.
  - TODO: Realism interaction with pattern cells — skip pattern-modified cells.
  - TODO: `censoring` — stub as no-op.
  - TODO: Validation timing — validate pre-realism, apply realism post-validation (architectural decision in `generator.py` / `autofix.py`).

#### `postprocess.py`
- **Implements:** §2.8 `_post_process` / `τ_post`
- **Key functions:**
  - `to_dataframe(rows: dict, topo_order: list[str]) → pd.DataFrame` — Converts the column-name → numpy-array dict into a `pd.DataFrame`. Assigns a `RangeIndex`. Casts temporal columns to `datetime64[ns]`. Preserves column order matching `topo_order`.
- **Internal data flow:** Pure transformation; no state mutation beyond DataFrame construction.
- **NEEDS_CLAR items:**
  - TODO: Exact post-processing behavior — DataFrame conversion, RangeIndex, datetime64 cast. No value clipping or rounding.

**Module integration points:**
- Receives frozen `DeclarationStore` + `seed` from M1 (via `pipeline.py`).
- Produces Master DataFrame (`pd.DataFrame`) for M5.
- Calls M4's `build_schema_metadata()` for the metadata dict.
- Subject to re-execution by M5's Loop B with seed offset `seed + attempt` and parameter overrides.

---

### Module: Schema Metadata (M4) — `phase_2/metadata/`

**Purpose:** M4 builds the `schema_metadata` dictionary — a structured, machine-readable contract that encodes the semantics of the generated fact table. It is a single-pass projection from the `DeclarationStore` into a standardized dict with seven top-level keys. M4 is implemented as a standalone function (not a class) per the Stage 3 suggested resolution, called by `generator.py` during the `generate()` return path. It does not need the generated DataFrame — only the frozen declaration store — so it can conceptually run in parallel with M2's data generation stages.

**Files:**

#### `builder.py`
- **Implements:** §2.6
- **Key functions:**
  - `build_schema_metadata(store: DeclarationStore) → dict` — The sole public function. Assembles the seven-key dict:
    - `"dimension_groups"` → from `store.group_graph`: `{group_name: {columns: [...], hierarchy: [...]}}`. Temporal hierarchy includes only the root date column; `columns` includes derived features.
    - `"orthogonal_groups"` → direct passthrough from `store.orthogonal_pairs`: list of `{group_a, group_b, rationale}`.
    - `"group_dependencies"` → from `store.group_deps`. **Enriched:** includes `conditional_weights` (not just the edge).
    - `"columns"` → flattened from `store.column_registry`. Type-discriminated descriptors. **Enriched** beyond §2.6 example: categoricals include `values`, `weights`, `cardinality`; stochastic measures include full `param_model`, `family`; structural measures include `formula`, `effects`, `noise`, `depends_on`.
    - `"measure_dag_order"` → topological sort of `store.measure_dag_edges`.
    - `"patterns"` → from `store.pattern_list`. **Enriched:** includes all `params`.
    - `"total_rows"` → `store.target_rows`.
  - `_assert_metadata_consistency(meta: dict) → None | raises ValueError` — Post-build self-validation: every column in `dimension_groups` appears in `columns` with matching `group`, every `measure_dag_order` entry exists in `columns`, every pattern `col` is a measure, every `orthogonal_groups` entry references valid groups.
- **Internal data flow:** Reads `store` (all registries). Performs one topological sort for `measure_dag_order` (or re-uses the one computed by `dag.py`). Returns the assembled dict.
- **NEEDS_CLAR items:**
  - TODO (P0): Enrich `schema_metadata` beyond §2.6 example — add `values`/`weights` to categoricals, full `param_model` to stochastic measures, `formula`/`effects`/`noise` to structural measures, `conditional_weights` to group dependencies, all `params` to patterns.
  - TODO: Whether M4 needs the generated DataFrame — resolved: no.
  - TODO: Internal consistency validation — implement `_assert_metadata_consistency()`.

**Module integration points:**
- Receives frozen `DeclarationStore` from M1 (via `generator.py`).
- Produces `schema_metadata` dict consumed by M5 (validation) and Phase 3 (view extraction, QA generation).

---

### Module: Validation Engine (M5) — `phase_2/validation/`

**Purpose:** M5 is the terminal module of Phase 2. It verifies the generated Master DataFrame against its declarations at three levels (structural, statistical, pattern) and implements the auto-fix retry loop (Loop B) that re-executes M2 with seed offsets when checks fail. M5 makes no LLM calls — all fixes are parameter adjustments. Its output is the final validated triple `(DataFrame, schema_metadata, ValidationReport)` handed to Phase 3.

**Files:**

#### `validator.py`
- **Implements:** §2.9 — `SchemaAwareValidator` orchestrator
- **Key classes/functions:**
  - `SchemaAwareValidator` — Stateless orchestrator that runs all three check layers.
    - `validate(df: pd.DataFrame, meta: dict) → ValidationReport` — Calls `_L1_structural(df, meta)`, `_L2_statistical(df, meta)`, `_L3_pattern(df, meta)`. Collects all `Check` objects into a `ValidationReport`. Returns the report.
  - The validator consumes only `schema_metadata` (enriched per M4's P0 resolution) — it does not access the `DeclarationStore` directly. This preserves the module boundary.
- **Internal data flow:** Delegates to `structural.py`, `statistical.py`, `pattern_checks.py`. Aggregates results.
- **NEEDS_CLAR items:** None in this file — the three-layer structure is well-specified.

#### `structural.py`
- **Implements:** §2.9 L1
- **Key functions:**
  - `check_row_count(df, meta) → Check` — `abs(len(df) - meta["total_rows"]) / meta["total_rows"] < 0.1`.
  - `check_cardinality(df, meta) → list[Check]` — For each categorical column: `df[col].nunique() == col["cardinality"]`.
  - `check_marginal_weights(df, meta) → list[Check]` — For each root categorical: max deviation from declared `weights` < 0.10. Requires `values` and `weights` in enriched metadata.
  - `check_measure_finiteness(df, meta) → list[Check]` — `notna().all()` and `isfinite().all()` per measure column.
  - `check_orthogonal_independence(df, meta) → list[Check]` — `chi2_contingency` on root column pairs from `orthogonal_groups`. Pass if p > 0.05.
  - `check_dag_acyclicity(meta) → Check` — Redundant acyclicity verification of `measure_dag_order`.
- **Internal data flow:** Reads `df` and `meta`. Returns `list[Check]`. All checks are independent.
- **NEEDS_CLAR items:** None — all L1 checks have exact pseudocode in §2.9.

#### `statistical.py`
- **Implements:** §2.9 L2
- **Key functions:**
  - `check_stochastic_ks(df, meta) → list[Check]` — For each stochastic measure: iterates predictor cells (Cartesian product of effect predictor values), filters rows, reconstructs expected distribution parameters (`intercept + Σ effects`), runs `scipy.stats.kstest`. Pass if p > 0.05.
  - `check_structural_residuals(df, meta, pattern_mask=None) → list[Check]` — For each structural measure: evaluates the formula on actual upstream values, computes residuals, checks `abs(residuals.mean()) < residuals.std() * 0.1` and (if `noise_sigma > 0`) `abs(residuals.std() - noise_sigma) / noise_sigma < 0.2`. Excludes rows in `pattern_mask` for the corresponding column. Requires `formula`, `effects`, `noise` in enriched metadata.
  - `check_group_dependency_transitions(df, meta) → list[Check]` — For each group dependency: cross-tabulates child root vs. conditioning root, computes observed conditional distributions, checks max deviation from declared `conditional_weights` < 0.10.
  - `_iter_predictor_cells(col_meta, meta) → Iterator` — Generates the Cartesian product of predictor column values from the measure's effects keys. Skips cells with < 5 rows. Caps at 100 tested cells.
- **Internal data flow:** Reads `df` and `meta` (enriched). Uses the formula evaluator from `engine/measures.py` for structural residual computation (shared utility).
- **NEEDS_CLAR items:**
  - TODO: `iter_predictor_cells()` construction — Cartesian product of effect predictors. Skip < 5 rows. Cap at 100.
  - TODO: `noise_sigma = 0` divide-by-zero guard — check `residuals.std() < 1e-6` instead.

#### `pattern_checks.py`
- **Implements:** §2.9 L3
- **Key functions:**
  - `check_patterns(df, meta) → list[Check]` — Dispatches per pattern type:
    - `_verify_outlier_entity(df, pattern, meta) → Check` — Filters target rows, computes z-score. Pass if z-score ≥ 2.0.
    - `_verify_trend_break(df, pattern, meta) → Check` — Splits by `break_point`, checks magnitude > 15% relative change.
    - `_verify_ranking_reversal(df, pattern, meta) → Check` — Groups by entity, checks `rank_corr < 0`.
    - `_verify_dominance_shift(df, pattern, meta) → Check` — Stub.
    - `_verify_convergence(df, pattern, meta) → Check` — Stub: `Check(passed=True, detail="not implemented")`.
    - `_verify_seasonal_anomaly(df, pattern, meta) → Check` — Stub: `Check(passed=True, detail="not implemented")`.
- **Internal data flow:** Reads `df` and `meta["patterns"]`. Each check is independent.
- **NEEDS_CLAR items:**
  - TODO: `dominance_shift` validation — rank change of named entity across temporal split.
  - TODO: `convergence` and `seasonal_anomaly` — stub with passing checks.

#### `autofix.py`
- **Implements:** §2.9 auto-fix loop (Loop B)
- **Key classes/functions:**
  - `generate_with_validation(generate_fn, store, meta, base_seed: int, max_retries: int = 3) → tuple[pd.DataFrame, ValidationReport]` — Loop B wrapper. For each attempt: (1) call `generate_fn(store, seed=base_seed + attempt, overrides=overrides)` to produce a DataFrame (pre-realism), (2) call `SchemaAwareValidator.validate(df, meta)`, (3) if all checks pass, apply realism (if configured) and return, (4) if failures exist, dispatch auto-fix strategies, update `overrides`, retry. After exhausting retries, return best result with partial failures logged.
  - `AUTO_FIX: dict[str, Callable]` — Dispatch table mapping check name prefixes to strategies:
    - `"marginal_"` / `"ks_"` → `widen_variance` — multiplies relevant `sigma` intercept by a factor (e.g., 1.5×).
    - `"outlier_"` / `"trend_"` → `amplify_magnitude` — multiplies pattern's `z_score` or `magnitude` param by a factor.
    - `"orthogonal_"` → `reshuffle_pair` — re-shuffles one root column independently (different seed produces different shuffle).
  - `ParameterOverrides` — A dict-like structure that holds mutation deltas. Passed to `run_pipeline()` alongside the store so that the original `DeclarationStore` is not mutated. Keys are `(column_name, param_name)` tuples; values are multiplicative factors.
- **Internal data flow:** Calls `engine.generator.run_pipeline()` (via `generate_fn`) per attempt. Calls `validator.validate()` per attempt. Mutation deltas accumulate in `ParameterOverrides` across retries.
- **NEEDS_CLAR items:**
  - TODO (P0): Mutation target — frozen store is read-only. All mutations go through `ParameterOverrides`.
  - TODO: Validation ordering — validate pre-realism; apply realism post-validation as final step.
  - TODO: Strategy implementations — `widen_variance`, `amplify_magnitude`, `reshuffle_pair` with simple multiplicative factors.

**Module integration points:**
- Receives Master DataFrame from M2 and `schema_metadata` from M4.
- Produces final validated `(DataFrame, schema_metadata, ValidationReport)` triple for Phase 3.
- Feeds back into M2 via Loop B: re-executes `run_pipeline()` with seed offset + parameter overrides.
