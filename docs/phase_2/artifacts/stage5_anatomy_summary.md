# Stage 5: Phase 2 Implementation Summary

**System:** AGPDS Phase 2 — Agentic Data Simulator (SDK-Driven)
**Source:** `stage4_implementation_anatomy.md` (blueprint), post-implementation state
**Status:** All 36 NEEDS_CLAR items resolved. Remaining stubs documented in `docs/gaps.md`.

---

## 1. Dependency Graph

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
phase_2/
│
├── pyproject.toml
├── README.md
│
├── phase_2/
│   ├── __init__.py                     # Package root; re-exports pipeline entry point
│   │
│   ├── types.py                        # §2.1, §2.1.1, §2.1.2 — shared dataclasses:
│   │                                   #   ColumnDescriptor, PatternSpec, RealismConfig,
│   │                                   #   GroupDependency, OrthogonalPair, DeclarationStore,
│   │                                   #   Check, ValidationReport, ParameterOverrides
│   │
│   ├── exceptions.py                   # §2.7 — CyclicDependencyError, UndefinedEffectError,
│   │                                   #   NonRootDependencyError, DuplicateColumnError,
│   │                                   #   UndefinedPredictorError, SkipResult
│   │
│   ├── pipeline.py                     # Top-level Phase 2 orchestrator: M3 → M1 → M2 ∥ M4 → M5
│   │                                   #   Wires Loop A (M3↔M1) and Loop B (M5→M2)
│   │
│   ├── orchestration/                  # ── M3: LLM Orchestration (§2.5, §2.7) ──
│   │   ├── __init__.py
│   │   ├── prompt.py                   # §2.5 — prompt template assembly:
│   │   │                               #   role preamble, SDK whitelist, HC1–HC9,
│   │   │                               #   soft guidelines, one-shot example, scenario slot
│   │   ├── sandbox.py                  # §2.7 — sandbox execution of build_fact_table()
│   │   │                               #   In-process exec() with fresh namespace per attempt,
│   │   │                               #   configurable timeout, full traceback capture
│   │   ├── retry_loop.py              # §2.7 — feedback loop: append code+traceback,
│   │   │                               #   re-prompt, max_retries=3, SkipResult on exhaustion
│   │   ├── code_validator.py           # §2.5 — AST-level structural validation of LLM code:
│   │   │                               #   extract_clean_code() for fence-stripping,
│   │   │                               #   validate_generated_code() for build_fact_table +
│   │   │                               #   .generate() call detection
│   │   └── llm_client.py              # Multi-provider LLM client with parameter adaptation:
│   │                                   #   OpenAI, Gemini, Gemini Native, Azure OpenAI, Custom
│   │
│   ├── sdk/                            # ── M1: SDK Surface (§2.1–§2.3) ──
│   │   ├── __init__.py                 # Re-exports FactTableSimulator
│   │   ├── simulator.py                # §2.1 — FactTableSimulator(target_rows, seed):
│   │   │                               #   constructor, phase lifecycle, generate() delegation,
│   │   │                               #   DeclarationStore freeze before pipeline execution
│   │   ├── columns.py                  # §2.1.1 — add_category(), add_temporal(),
│   │   │                               #   add_measure(), add_measure_structural()
│   │   │                               #   Declaration-time validation: auto-normalize,
│   │   │                               #   parent existence, DAG acyclicity, family check
│   │   ├── relationships.py            # §2.1.2 — declare_orthogonal(), add_group_dependency(),
│   │   │                               #   inject_pattern(), set_realism()
│   │   │                               #   Phase step enforcement, pattern param validation
│   │   ├── groups.py                   # §2.2 — dimension group graph construction:
│   │   │                               #   group registry, hierarchy tracking, temporal special case
│   │   ├── dag.py                      # §2.3 — measure DAG edge extraction from formulas,
│   │   │                               #   full-column DAG construction (_build_full_dag),
│   │   │                               #   topological sort (Kahn's), acyclicity check
│   │   └── validation.py               # §2.1.1, §2.1.2 — declaration-time validation rules:
│   │                                   #   name uniqueness, parent-same-group, root-only deps,
│   │                                   #   effect predictor existence, per-parent weight coverage,
│   │                                   #   formula symbol resolution
│   │
│   ├── engine/                         # ── M2: Generation Engine (§2.4, §2.8) ──
│   │   ├── __init__.py
│   │   ├── generator.py                # §2.8 — generate() pipeline orchestrator:
│   │   │                               #   pre-flight DAG build, RNG init, stage dispatch,
│   │   │                               #   accepts ParameterOverrides for Loop B auto-fix
│   │   ├── skeleton.py                 # §2.8 stage α — _build_skeleton():
│   │   │                               #   root categoricals, conditional children,
│   │   │                               #   cross-group dependents, temporal sampling + derivation
│   │   ├── measures.py                 # §2.8 stage β — _sample_stochastic(), _eval_structural()
│   │   │                               #   Stochastic: intercept + Σ effects → family draw
│   │   │                               #     (7 families: gaussian, lognormal, gamma, beta,
│   │   │                               #      uniform, poisson, exponential)
│   │   │                               #   Structural: restricted AST formula eval + effects + noise
│   │   │                               #   Runtime parameter clamping to legal intervals
│   │   ├── patterns.py                 # §2.8 stage γ — _inject_patterns():
│   │   │                               #   outlier_entity, trend_break (fully implemented)
│   │   │                               #   Pattern overlap: sequential mutation in declaration order
│   │   │                               #   Returns pattern_mask for realism + L2 exclusion
│   │   ├── realism.py                  # §2.8 stage δ — _inject_realism():
│   │   │                               #   missing_rate (all columns, NaN), dirty_rate (categoricals)
│   │   │                               #   Missing takes precedence; pattern cells are protected
│   │   └── postprocess.py              # §2.8 — to_dataframe():
│   │                                   #   dict → pd.DataFrame, RangeIndex, datetime64 cast,
│   │                                   #   column order matches topo_order
│   │
│   ├── metadata/                       # ── M4: Schema Metadata (§2.6) ──
│   │   ├── __init__.py
│   │   └── builder.py                  # §2.6 — build_schema_metadata(store) → dict
│   │                                   #   7 top-level keys: dimension_groups, orthogonal_groups,
│   │                                   #   group_dependencies, columns, measure_dag_order,
│   │                                   #   patterns, total_rows
│   │                                   #   Enriched: values/weights on categoricals, full param_model
│   │                                   #   on stochastic, formula/effects/noise on structural,
│   │                                   #   conditional_weights on deps, full params on patterns
│   │                                   #   Post-build self-check: _assert_metadata_consistency()
│   │
│   └── validation/                     # ── M5: Validation Engine (§2.9) ──
│       ├── __init__.py
│       ├── validator.py                # §2.9 — SchemaAwareValidator: orchestrates L1/L2/L3,
│       │                               #   collects Check objects, dispatches auto-fix
│       ├── structural.py               # §2.9 L1 — row count, cardinality, marginal weights,
│       │                               #   measure finiteness, orthogonal χ², DAG acyclicity
│       ├── statistical.py              # §2.9 L2 — KS-test per predictor cell (stochastic),
│       │                               #   residual mean/std check (structural),
│       │                               #   conditional transition deviation (group deps)
│       │                               #   Predictor cell enumeration: Cartesian product,
│       │                               #   skip < 5 rows, cap at 100 cells
│       ├── pattern_checks.py           # §2.9 L3 — outlier z-score, trend break magnitude,
│       │                               #   ranking reversal correlation (fully implemented)
│       │                               #   dominance_shift, convergence, seasonal_anomaly (stubs)
│       └── autofix.py                  # §2.9 — generate_with_validation() Loop B wrapper:
│                                       #   AUTO_FIX dispatch (widen_variance, amplify_magnitude,
│                                       #   reshuffle_pair), seed=base+attempt, max 3 retries
│                                       #   Mutations via ParameterOverrides (frozen store untouched)
│                                       #   Validation runs pre-realism; realism applied post-pass
│
└── tests/
    ├── __init__.py
    ├── test_end_to_end.py              # Full pipeline integration with Loop A + Loop B
    ├── test_integration_advanced.py    # Advanced integration scenarios
    ├── test_module_s2e.py              # Module-level scenario-to-execution tests
    ├── test_validation_failures.py     # Validation failure path coverage
    └── modular/
        ├── __init__.py
        ├── test_pipeline.py
        ├── test_engine_generator.py
        ├── test_engine_skeleton.py
        ├── test_engine_patterns.py
        ├── test_engine_measures.py      # P0-2: formula evaluator + stochastic distribution tests
        ├── test_engine_realism.py
        ├── test_engine_postprocess.py
        ├── test_orchestration_prompt.py
        ├── test_orchestration_sandbox.py
        ├── test_orchestration_retry_loop.py
        ├── test_orchestration_code_validator.py
        ├── test_orchestration_llm_client.py
        ├── test_sdk_simulator.py
        ├── test_sdk_columns.py
        ├── test_sdk_relationships.py
        ├── test_sdk_groups.py
        ├── test_sdk_dag.py
        ├── test_sdk_validation.py
        ├── test_metadata_builder.py
        ├── test_validation_validator.py
        ├── test_validation_structural.py  # P0-1: marginal weights + measure finiteness tests
        ├── test_validation_statistical.py
        ├── test_validation_pattern.py
        └── test_validation_autofix.py
```

---

## 3. Per-Module Explanations

---

### Shared Infrastructure — `phase_2/`

**Purpose:** The 3 root-level files provide cross-cutting definitions imported by all modules. They contain no business logic — only data structures, exception types, and top-level pipeline wiring.

#### `types.py`
- **Spec ref:** §2.1, §2.1.1, §2.1.2, §2.2
- **Key classes:**
  - `ColumnDescriptor` — Frozen dataclass with fields: `name`, `type` (categorical / temporal / measure), `group`, `parent`, `family`, `param_model`, `formula`, `effects`, `noise`, `derive`, `values`, `weights`, `scale`. Not all fields are populated for every column type; unused fields default to `None`. This is the canonical single-column representation flowing from M1 into M2 and M4.
  - `PatternSpec` — Dataclass: `type` (str enum), `target` (filter expression string), `col` (column name), `params` (dict).
  - `OrthogonalPair` — Dataclass: `group_a`, `group_b`, `rationale`.
  - `GroupDependency` — Dataclass: `child_root`, `on` (list of root column names), `conditional_weights` (nested dict).
  - `RealismConfig` — Optional dataclass: `missing_rate`, `dirty_rate`, `censoring`.
  - `DeclarationStore` — Composite container holding: `column_registry`, `group_graph`, `measure_dag_edges`, `orthogonal_pairs`, `group_deps`, `pattern_list`, `realism_config`, `target_rows`, `seed`. Exposes `freeze()` to transition from mutable to read-only, and `_check_mutable()` to enforce the freeze contract. This is the sole artifact crossing the M1 boundary into M2 and M4.
  - `Check` — Validation result record: `name`, `passed` (bool), `detail` (str | None). Used by M5.
  - `ValidationReport` — List of `Check` objects with aggregated pass/fail result.
  - `ParameterOverrides` — Dict-like structure for Loop B auto-fix mutation deltas, keyed by `(column_name, param_name)` tuples with multiplicative factor values.
- **Data flow:** Pure data definitions — no logic, no imports from other `phase_2` modules. All other modules import from here.

#### `exceptions.py`
- **Spec ref:** §2.7
- **Key classes:**
  - `SDKError` — Base class for all typed SDK exceptions, carrying a structured `message` string.
  - `CyclicDependencyError(SDKError)` — Raised when DAG validation detects a cycle.
  - `UndefinedEffectError(SDKError)` — Raised when a formula or `param_model` references an undefined symbol.
  - `NonRootDependencyError(SDKError)` — Raised when `add_group_dependency` targets a non-root column.
  - `DuplicateColumnError(SDKError)` — Raised on duplicate `name`.
  - `UndefinedPredictorError(SDKError)` — Raised when effects keys reference undeclared columns.
  - `SkipResult` — Sentinel return value (not an exception) produced by M3 when all retries are exhausted. Checked by `pipeline.py`.
- **Data flow:** No dependencies. Raised by `sdk/`, caught by `orchestration/`, `SkipResult` checked by `pipeline.py`.

#### `pipeline.py`
- **Spec ref:** Stage 1 module interaction chain — Phase 2 top-level orchestrator
- **Key functions:**
  - `run_phase2(scenario_context: dict) → tuple[pd.DataFrame, dict, ValidationReport] | SkipResult` — Entry point. Wires: (1) call M3's `orchestrate()` to produce a validated script or `SkipResult`; (2) on success, execute the script to populate a `DeclarationStore` in M1; (3) call M4's `build_schema_metadata()` (conceptually parallel with M2 since both only read the frozen store); (4) call M2's `generate()` to produce the DataFrame; (5) pass both to M5's `generate_with_validation()` which wraps Loop B.
  - `_run_loop_a(scenario_context) → Callable | SkipResult` — Delegates to M3. Returns the `build_fact_table` callable, or `SkipResult`.
  - `_run_loop_b(build_fn, declaration_store, schema_metadata) → tuple[DataFrame, ValidationReport]` — Delegates to M5's auto-fix wrapper. Loop A is outer (involves LLM), Loop B is inner (no LLM).
- **Data flow:** Imports `orchestration`, `sdk`, `engine`, `metadata`, `validation`. This is the only file that knows about all 5 modules.

**Module integration points:**
- Receives `scenario_context` dict from Phase 1 (external).
- Produces `(DataFrame, schema_metadata, ValidationReport)` for Phase 3 (external).

---

### Module: LLM Orchestration (M3) — `phase_2/orchestration/`

**Purpose:** M3 is the Phase 2 entry module. It prompts an LLM and iterates in an error-feedback retry loop, transforming a Phase 1 scenario context into a valid, executable `build_fact_table()` Python script. Its only stateful artifact is the LLM conversation history; each retry appends the failed script and its traceback. M3 is the only module in the entire Phase 2 pipeline where LLM calls occur — all downstream steps are pure computation.

**Files:**

#### `prompt.py`
- **Spec ref:** §2.5
- **Key classes / functions:**
  - `PromptTemplate` — Stores the 5 prompt regions as composable string fragments: role preamble, SDK method whitelist (Step 1 + Step 2 blocks), hard constraints (HC1–HC9), soft guidelines, and one-shot example.
  - `assemble_prompt(scenario_context: dict) → list[dict]` — Receives the Phase 1 scenario dict (title, entities, metrics, temporal grain, `target_rows`, complexity tier), serializes it into the `[SCENARIO]` block format, fills the `{scenario_context}` slot, and returns the initial message list (`messages[0]` = system prompt with all 5 regions). This is the immutable conversation base persisting across retries.
  - `SUPPORTED_FAMILIES: list[str]` — 8 distribution family names: `gaussian`, `lognormal`, `gamma`, `beta`, `uniform`, `poisson`, `exponential`, `mixture`.
  - `SUPPORTED_PATTERNS: list[str]` — 6 pattern types: `outlier_entity`, `trend_break`, `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`.
- **Data flow:** `assemble_prompt()` is called once by `retry_loop.py` to seed the conversation. Its output (`list[dict]`) is passed by reference and appended in-place by `retry_loop.py`.

#### `sandbox.py`
- **Spec ref:** §2.7 step 2
- **Key classes / functions:**
  - `SandboxExecutor` — Wraps the execution environment for LLM-generated scripts.
    - `execute(script: str, sdk_module) → DeclarationStore` — Executes the script in a controlled scope. On success, returns the frozen `DeclarationStore` from the script's `FactTableSimulator` instance. On failure, re-raises the exception for the retry loop to catch.
    - `_create_exec_scope(sdk_module) → dict` — Builds the namespace dict for `exec()`, injecting the `FactTableSimulator` class and other allowed imports.
  - `SandboxConfig` — Dataclass: `timeout_seconds` (default 30), `isolation_level` (enum: `EXEC_IN_PROCESS` | `SUBPROCESS`).
- **Data flow:** Called by `retry_loop.py` on each attempt. Imports `FactTableSimulator` from `sdk/` and exposes it in the `exec` scope. Returns either a `DeclarationStore` or a raised `Exception`.
- **Implementation decisions:** In-process `exec()` with fresh namespace per attempt. Configurable timeout. Catches all `Exception` subclasses and feeds back full traceback regardless of exception type.

#### `retry_loop.py`
- **Spec ref:** §2.7
- **Key classes / functions:**
  - `orchestrate(scenario_context: dict, llm_client, sandbox: SandboxExecutor, max_retries: int = 3) → DeclarationStore | SkipResult` — Loop A driver. Steps: (1) call `assemble_prompt()` to build initial messages; (2) for each attempt, call `llm_client` to generate a script, append assistant message, execute `sandbox.execute()`; on success return `DeclarationStore`; on exception, append a user message containing code + traceback with re-prompt text `"Adjust parameters to resolve the error"`; (3) on retry exhaustion, return `SkipResult` with recorded failure details.
  - `_extract_script(llm_response) → str` — Parses the Python code block from the LLM response.
  - `_format_error_feedback(script: str, exception: Exception) → str` — Formats code + traceback into the user-turn message for the next retry.
- **Data flow:** Seeds with `prompt.py`'s `assemble_prompt()` output. Calls `sandbox.py`'s `execute()` each attempt. Conversation history (`list[dict]`) accumulates in-place: system message (frozen) + one pair per failure (assistant: script, user: code + traceback). Up to 8 messages at max retries.

#### `code_validator.py`
- **Spec ref:** §2.5 hard requirements
- **Key classes / functions:**
  - `CodeValidationResult` — Frozen dataclass: `is_valid`, `has_build_fact_table`, `has_generate_call`, `errors`.
  - `extract_clean_code(raw_response: str) → str` — Strips markdown code fences from raw LLM responses.
  - `validate_generated_code(code: str) → CodeValidationResult` — AST-level structural validation that: (a) a `def build_fact_table(...)` function exists, and (b) a `.generate()` method call exists.
- **Data flow:** Called by the retry loop to pre-validate LLM output before sandbox execution.

#### `llm_client.py`
- **Spec ref:** External LLM integration
- **Key classes / functions:**
  - `ProviderCapabilities` — Dataclass defining what parameters each provider supports (temperature, max_tokens, response_format, etc.).
  - `PROVIDER_CAPABILITIES` — Registry for OpenAI, Gemini, Gemini Native, Azure OpenAI providers.
  - Multi-provider parameter adaptation for generating `build_fact_table()` scripts.
- **Data flow:** Called by `retry_loop.py` to make LLM API calls. Abstracts provider differences so the rest of M3 is provider-agnostic.

**Module integration points:**
- Receives `scenario_context` dict from Phase 1 via `pipeline.py`.
- Receives `Exception` objects from M1 (SDK) during sandbox execution.
- Produces a frozen `DeclarationStore` for M1/M2/M4 on success, or `SkipResult` on terminal failure.

---

### Module: SDK Surface (M1) — `phase_2/sdk/`

**Purpose:** M1 provides the strongly-typed, builder-pattern API called by LLM-generated scripts. It accepts column declarations, dimension group structures, measure definitions, and relationship/pattern declarations, validates each incrementally, and accumulates them into a consistent `DeclarationStore`. The store goes through 3 lifecycle phases: accumulating (during method calls), frozen (after `generate()` begins), consumed (read by M2, M4, M5). M1's validation is the first line of defense against semantic errors in LLM-generated code; its typed exceptions are Loop A's feedback signal.

**Files:**

#### `simulator.py`
- **Spec ref:** §2.1
- **Key classes / functions:**
  - `FactTableSimulator` — The external-facing SDK class.
    - `__init__(self, target_rows: int, seed: int)` — Validates `target_rows >= 1`, saves `seed`, initializes an empty `DeclarationStore` in accumulating mode. Creates an internal `_phase` flag starting at `STEP_1`.
    - `generate(self) → tuple[pd.DataFrame, dict]` — Freezes the declaration store via `self._store.freeze()`, then delegates to `engine.generator.run_pipeline()` for DataFrame generation and `metadata.builder.build_schema_metadata()` for the metadata dict. This is the boundary where M1 ends and M2 + M4 begin.
  - The class itself is thin — method logic lives in `columns.py` and `relationships.py`, attached via delegation. All mutation methods call `_store._check_mutable()` to enforce the freeze contract.
- **Data flow:** Constructor creates `DeclarationStore`. Step 1 methods (in `columns.py`) and Step 2 methods (in `relationships.py`) mutate it. `generate()` freezes it and passes it downstream.

#### `columns.py`
- **Spec ref:** §2.1.1
- **Key functions (delegated from `FactTableSimulator`):**
  - `add_category(name, values, weights, group, parent=None)` — Validates: `values` non-empty, column name unique, parent exists and in same group if specified, auto-normalizes weights (flat list or per-parent dict with full parent coverage). Appends `ColumnDescriptor(type="categorical")` and updates `group_graph`.
  - `add_temporal(name, start, end, freq, derive=[])` — Validates: `start < end`, `freq` is supported. Creates root temporal `ColumnDescriptor` plus one per derived feature (`day_of_week`, `month`, `quarter`, `is_weekend`). Derived columns have `type="temporal"`, `derived=True`.
  - `add_measure(name, family, param_model, scale=None)` — Validates: `family` in `SUPPORTED_FAMILIES`, all effect predictor columns exist, all symbolic effects have numeric definitions. Creates `ColumnDescriptor(type="measure", measure_type="stochastic")`. No DAG edges (root measure).
  - `add_measure_structural(name, formula, effects={}, noise={})` — Validates: every formula symbol resolves to a declared measure or effects key, no self-reference, DAG remains acyclic after adding edges. Creates `ColumnDescriptor(type="measure", measure_type="structural")` and adds edges to `measure_dag_edges`.
  - `_validate_phase_step1(self)` — Checks `_phase` is still `STEP_1`; raises if Step 2 methods have been called.
- **Data flow:** Each method reads and modifies `DeclarationStore` via `simulator._get_store()`. `add_category` modifies `group_graph` + `column_registry`. `add_measure_structural` modifies `column_registry` + `measure_dag_edges`. Acyclicity validation calls `dag.py`.

#### `relationships.py`
- **Spec ref:** §2.1.2
- **Key functions:**
  - `declare_orthogonal(group_a, group_b, rationale)` — Validates: both groups exist in `group_graph` and are different. Appends an `OrthogonalPair`.
  - `add_group_dependency(child_root, on, conditional_weights)` — Validates: `child_root` and all `on` columns are roots (`parent=None`), root-level dependency DAG remains acyclic, `conditional_weights` keys cover all values of the `on` column. Single-column `on` only (multi-column raises `NotImplementedError`). Appends a `GroupDependency` and adds edges from each `on` column to `child_root` in the full column DAG.
  - `inject_pattern(type, target, col, **params)` — Validates: `type` in `SUPPORTED_PATTERNS`, `col` exists and is a measure column, required params present for `outlier_entity` and `trend_break`. Appends a `PatternSpec`.
  - `set_realism(missing_rate=0.0, dirty_rate=0.0, censoring=None)` — Stores a `RealismConfig` singleton. Overwrites on repeat calls.
  - `_validate_phase_step2(self)` — On first call, transitions `_phase` from `STEP_1` to `STEP_2`. Rejects Step 1 methods thereafter.
- **Data flow:** Each method reads and modifies `DeclarationStore`. First call to any Step 2 method triggers the `_phase` transition. `add_group_dependency` also calls `dag.py` for root-level dependency DAG acyclicity check.

#### `groups.py`
- **Spec ref:** §2.2
- **Key classes / functions:**
  - `GroupInfo` — Dataclass: `name`, `root` (column name), `columns` (list), `hierarchy` (list, root-first order).
  - `build_group_graph(column_registry) → dict[str, GroupInfo]` — Builds the group graph from the column registry. For each group, identifies the root (`parent=None`), traces the hierarchy chain via parent pointers, and collects all group members. Temporal groups get special treatment: `hierarchy` contains only the root date column, not derived features.
  - `get_roots(group_graph) → list[str]` — Returns root column names for each group. Used by `relationships.py` for root-only validation.
- **Data flow:** Called incrementally by `columns.py` (each `add_category` / `add_temporal` updates the group graph). Also called by `dag.py` to identify hierarchy edges in the full column DAG.

#### `dag.py`
- **Spec ref:** §2.3, §2.4
- **Key functions:**
  - `add_measure_edge(edges: set, upstream: str, downstream: str)` — Adds a directed edge and immediately checks for cycles.
  - `topological_sort(edges: set, nodes: list) → list[str]` — Kahn's algorithm; raises `CyclicDependencyError` on cycle detection.
  - `build_full_dag(declaration_store) → tuple[dict, list[str]]` — Aggregates edges from 4 sources into a unified DAG: (1) intra-group hierarchy (`parent` → child); (2) cross-group root dependencies; (3) temporal derivation (root → derived features); (4) measure formula references. Returns adjacency list and topological order. Used by both M2's pre-flight and M1's incremental validation.
  - `is_acyclic(order: list) → bool` — Simple check function for M5's L1 redundant acyclicity verification.
- **Data flow:** `columns.py` calls `add_measure_edge()` in `add_measure_structural()`; `relationships.py` calls it for root DAG edges in `add_group_dependency()`; `generator.py` (M2) calls `build_full_dag()` during pre-flight.

#### `validation.py`
- **Spec ref:** §2.1.1, §2.1.2 validation rules centralized
- **Key functions:**
  - `validate_column_name(name, registry) → None | raises DuplicateColumnError` — Enforces column name uniqueness.
  - `validate_parent(parent, group, registry) → None | raises SDKError` — Checks parent exists and belongs to same group.
  - `validate_weights(values, weights, parent_values=None) → list[float]` — Auto-normalizes; raises on empty `values`. For per-parent dict form, validates full parent value coverage.
  - `validate_family(family) → None | raises ValueError` — Checks membership in `SUPPORTED_FAMILIES`.
  - `validate_effects_predictors(effects, registry) → None | raises UndefinedPredictorError` — Checks all effect keys reference existing columns.
  - `validate_formula_symbols(formula, registry, effects) → set[str]` — Parses formula, extracts variable names, verifies each resolves to a declared measure or effects key, returns upstream measure dependency set.
  - `validate_root_only(col_name, registry) → None | raises NonRootDependencyError` — Checks `parent=None`.
- **Data flow:** Called by `columns.py` and `relationships.py` within each declaration method. Pure validation layer — no state mutation.

**Module integration points:**
- Receives executable Python scripts from M3 via sandbox execution.
- Produces a frozen `DeclarationStore` for M2 (generation) and M4 (metadata).
- Produces typed `Exception` objects back to M3 (as Loop A feedback).

---

### Module: Generation Engine (M2) — `phase_2/engine/`

**Purpose:** M2 is the deterministic computation core. It receives a frozen `DeclarationStore` and a seed integer and generates the main DataFrame through a four-stage pipeline: skeleton (α), measures (β), patterns (γ), and realism (δ). The pipeline maintains a single `numpy.random.Generator` stream throughout; its sequential consumption is the sole guarantee of bit-for-bit reproducibility. No LLM calls occur within this module. M2 is re-executed during Loop B (M5 auto-fix) with a per-attempt seed offset.

**Files:**

#### `generator.py`
- **Spec ref:** §2.8 — pipeline orchestrator
- **Key functions:**
  - `run_pipeline(store, seed, overrides=None, orthogonal_pairs=None) → tuple[pd.DataFrame, dict]` — Entry point for `generate()`. Steps: (1) pre-flight: call `dag.build_full_dag(store)` to get `topo_order`; (2) init `rng = np.random.default_rng(seed)`; (3) `skeleton.build_skeleton()` → partial row dict; (4) `measures.generate_measures()` → full row dict; (5) `patterns.inject_patterns()` → mutated rows + pattern_mask; (6) if `store.realism_config` exists, `realism.inject_realism()` with pattern_mask protection; (7) `postprocess.to_dataframe()` → `pd.DataFrame`; (8) `metadata.builder.build_schema_metadata()` → metadata dict; (9) return tuple.
  - The single `rng` object is passed by reference to all stages — this is the critical determinism invariant.
  - The optional `overrides` parameter lets Loop B auto-fix strategies take effect without modifying the frozen store.
- **Data flow:** Calls `skeleton.py`, `measures.py`, `patterns.py`, `realism.py`, `postprocess.py` in sequence. Also calls `dag.py` (M1) for pre-flight DAG construction and `metadata/builder.py` (M4) for metadata generation.

#### `skeleton.py`
- **Spec ref:** §2.8 stage α
- **Key functions:**
  - `build_skeleton(store, topo_order, rng) → dict[str, np.ndarray]` — Iterates `topo_order`, skipping measure columns. Dispatches each non-measure column to its sampler:
    - Root categorical → `_sample_root_categorical()` — `rng.choice()` by marginal weights.
    - Child categorical → `_sample_child_categorical()` — Row-wise conditional sampling from parent values. Supports flat broadcast and per-parent dict weight forms.
    - Cross-group dependent root → `_sample_dependent_root()` — Samples from `conditional_weights` based on upstream root column values.
    - Temporal root → `_sample_temporal()` — Uniform sampling within `[start, end]` at declared `freq`.
    - Temporal derived → `_derive_temporal()` — Deterministic extraction (`DOW()`, `MONTH()`, `QUARTER()`, `IS_WEEKEND()`), no RNG consumption.
  - Returns column name → numpy array dict, each array length `target_rows`.
- **Data flow:** Reads `store.column_registry`, `store.group_deps`, `store.group_graph`. Output passes directly to `measures.py`.

#### `measures.py`
- **Spec ref:** §2.8 stage β, §2.3
- **Key functions:**
  - `generate_measures(store, topo_order, rows, rng, overrides=None) → dict[str, np.ndarray]` — Iterates `topo_order`, processing only measure columns, dispatching by `measure_type`:
    - `_sample_stochastic(col, rows, rng, overrides) → np.ndarray` — Per-row: computes each distribution parameter as `intercept + Σ effects[predictor_col][row_value]`, applies any `overrides` scaling, then samples from the specified family via `rng`. Dispatches to: `rng.normal()`, `rng.lognormal()`, `rng.gamma()`, `rng.beta()`, `rng.uniform()`, `rng.poisson()`, `rng.exponential()`.
    - `_eval_structural(col, rows, rng, overrides) → np.ndarray` — Evaluates formula string with variable bindings from row context (upstream measure values + resolved effects); adds noise if `noise != {}`.
    - `_resolve_effects(effects_dict, rows, col_names) → np.ndarray` — Vectorized effect resolution: per-row categorical context lookup and summation.
    - `_clamp_params(params, family) → dict` — Runtime parameter clamping to legal intervals (e.g., `sigma = max(sigma, 1e-6)` for gaussian), with warnings on clamp.
    - `_evaluate_formula(formula, bindings) → float | np.ndarray` — Restricted AST formula evaluator. Parses via `ast.parse(formula, mode='eval')`, walks the tree accepting only `BinOp` (`+`, `-`, `*`, `/`, `Pow`), `UnaryOp` (`-`), `Constant` (int/float), and `Name` nodes. All other AST node types raise `ValueError`.
- **Data flow:** Reads skeleton-stage `rows` and `store.column_registry`. Modifies `rows` dict in-place, adding measure columns. `rng` advances one step per stochastic measure per row; structural measures with noise consume additional RNG.

#### `patterns.py`
- **Spec ref:** §2.8 stage γ
- **Key functions:**
  - `inject_patterns(store, rows, rng, overrides=None) → dict` — Iterates `store.pattern_list` in declaration order. Calls type-specific injectors. Returns modified `rows` dict plus `pattern_mask: dict[str, np.ndarray[bool]]` marking which cells were modified by patterns, for `realism.py` protection and M5 L2 residual exclusion.
  - `_inject_outlier_entity(pattern, rows, rng) → np.ndarray[bool]` — Parses `target` filter, selects matching rows, scales `col` values to declared `z_score`. Returns modification mask.
  - `_inject_trend_break(pattern, rows, rng) → np.ndarray[bool]` — Splits rows by temporal `break_point`, applies magnitude shift to `col` values after the break.
  - `_parse_target_filter(target, rows) → np.ndarray[bool]` — Evaluates filter expression against row values, returning boolean mask. Supports `column == "value"` with `and` / `or`.
  - Pattern overlap: sequential mutation in declaration order.
  - Structural measure pattern cells are marked for M5 L2 residual exclusion.
- **Data flow:** Reads `store.pattern_list` and mutates `rows` in-place. `pattern_mask` output flows to `realism.py` (skip pattern cells) and M5 (L2 residual exclusion).

#### `realism.py`
- **Spec ref:** §2.8 stage δ
- **Key functions:**
  - `inject_realism(store, rows, rng, pattern_mask=None) → dict` — Applies realism degradation per `store.realism_config`. Processes `missing_rate` first (higher precedence), then `dirty_rate`. All cells in `pattern_mask` are skipped.
  - `_inject_missing(rows, rate, rng, protected_cells=None) → dict` — For each column, randomly selects `rate` proportion of rows and replaces with `np.nan`. Protected cells are skipped.
  - `_inject_dirty(rows, rate, rng, column_registry, protected_cells=None) → dict` — Categorical columns only: randomly replaces values with another valid value from the column's `values` list.
- **Data flow:** Reads `store.realism_config` and `store.column_registry`, mutates `rows` in-place. Random cell selection consumes `rng`.

#### `postprocess.py`
- **Spec ref:** §2.8 `_post_process` / `τ_post`
- **Key functions:**
  - `to_dataframe(rows, topo_order) → pd.DataFrame` — Converts column name → numpy array dict to `pd.DataFrame`, assigns `RangeIndex`, casts temporal columns to `datetime64[ns]`, maintains column order consistent with `topo_order`.
- **Data flow:** Pure conversion; no additional state modification beyond DataFrame construction.

**Module integration points:**
- Receives frozen `DeclarationStore` + `seed` from M1 via `pipeline.py`.
- Produces the main DataFrame (`pd.DataFrame`) for M5.
- Calls M4's `build_schema_metadata()` to generate the metadata dict.
- Re-executed during M5's Loop B with `seed + attempt` offset and parameter overrides.

---

### Module: Schema Metadata (M4) — `phase_2/metadata/`

**Purpose:** M4 builds the `schema_metadata` dictionary — a structured, machine-readable contract encoding the semantics of the generated fact table. It is a single-pass projection from `DeclarationStore` to a normalized dict with 7 top-level keys. Implemented as a standalone function (not a class), called by `generator.py` on the `generate()` return path. It requires only the frozen declaration store (no DataFrame dependency), so it is conceptually parallelizable with M2's data generation.

**Files:**

#### `builder.py`
- **Spec ref:** §2.6
- **Key functions:**
  - `build_schema_metadata(store) → dict` — The sole public function. Assembles a 7-key dictionary:
    - `"dimension_groups"` — From `store.group_graph`: `{group_name: {columns: [...], hierarchy: [...]}}`. Temporal groups have `hierarchy` containing only the root date column, while `columns` includes derived features.
    - `"orthogonal_groups"` — Pass-through from `store.orthogonal_pairs`: `{group_a, group_b, rationale}` list.
    - `"group_dependencies"` — From `store.group_deps`. Enriched: includes `conditional_weights`, not just dependency edges.
    - `"columns"` — Flattened from `store.column_registry`. Type-discriminated descriptor array. Enriched: categoricals include `values`, `weights`, `cardinality`; stochastic measures include full `param_model` and `family`; structural measures include `formula`, `effects`, `noise`, `depends_on`.
    - `"measure_dag_order"` — Topological sort of `store.measure_dag_edges`.
    - `"patterns"` — From `store.pattern_list`. Enriched: includes full `params`.
    - `"total_rows"` — `store.target_rows`.
  - `_assert_metadata_consistency(meta) → None | raises ValueError` — Post-build self-check: every column in `dimension_groups` must appear in `columns` with matching `group`; every entry in `measure_dag_order` must exist in `columns`; every pattern's `col` must be a measure column; every `orthogonal_groups` entry must reference valid group names.
- **Data flow:** Reads all registries from `store`. Performs one topological sort for `measure_dag_order` (or reuses `dag.py`'s cached order), then returns the assembled dict.

**Module integration points:**
- Receives the frozen `DeclarationStore` from M1 via `generator.py`.
- Produces `schema_metadata` dict for M5 (validation) and Phase 3 (view extraction, QA generation).

---

### Module: Validation Engine (M5) — `phase_2/validation/`

**Purpose:** M5 is Phase 2's terminal module. It validates the generated main DataFrame against declarations at 3 levels (structural, statistical, pattern), and implements the auto-fix retry loop (Loop B); when checks fail, it re-executes M2 with a different seed offset. M5 makes no LLM calls — all fixes are parameter adjustments. Its final output is the validated triple for Phase 3: `(DataFrame, schema_metadata, ValidationReport)`.

**Files:**

#### `validator.py`
- **Spec ref:** §2.9 — `SchemaAwareValidator` orchestrator
- **Key classes / functions:**
  - `SchemaAwareValidator` — Stateless orchestrator running all 3 check levels.
    - `validate(df, meta) → ValidationReport` — Sequentially calls `_run_l1(df, meta)`, `_run_l2(df, meta)`, `_run_l3(df, meta)`, aggregates all `Check` objects into a `ValidationReport`.
  - The validator consumes only `schema_metadata` (requiring it to be enriched per M4's P0 decision), not the `DeclarationStore` directly. This preserves module boundaries.
- **Data flow:** Delegates to `structural.py`, `statistical.py`, `pattern_checks.py`, then aggregates results.

#### `structural.py`
- **Spec ref:** §2.9 L1
- **Key functions:**
  - `check_row_count(df, meta) → Check` — `abs(len(df) - meta["total_rows"]) / meta["total_rows"] < 0.1`.
  - `check_cardinality(df, meta) → list[Check]` — Per categorical column: `df[col].nunique() == col["cardinality"]`.
  - `check_marginal_weights(df, meta) → list[Check]` — Per root categorical: max deviation from declared `weights` < 0.10.
  - `check_measure_finiteness(df, meta) → list[Check]` — Per measure column: `notna().all()` and `isfinite().all()`.
  - `check_orthogonal_independence(df, meta) → list[Check]` — Per `orthogonal_groups` root column pair: `chi2_contingency`, pass if p > 0.05.
  - `check_dag_acyclicity(meta) → Check` — Redundant acyclicity verification on `measure_dag_order`.
- **Data flow:** Reads `df` and `meta`, returns `list[Check]`. All checks are independent.

#### `statistical.py`
- **Spec ref:** §2.9 L2
- **Key functions:**
  - `check_stochastic_ks(df, meta) → list[Check]` — Per stochastic measure: iterates predictor cells (Cartesian product of effect predictor values), filters matching rows, reconstructs expected distribution parameters (`intercept + Σ effects`), runs `scipy.stats.kstest`. Pass if p > 0.05.
  - `check_structural_residuals(df, meta, pattern_mask=None) → list[Check]` — Per structural measure: recomputes formula from actual upstream values, gets residuals, checks `abs(residuals.mean()) < residuals.std() * 0.1`, and (if `noise_sigma > 0`) `abs(residuals.std() - noise_sigma) / noise_sigma < 0.2`. Excludes `pattern_mask` rows. Zero-noise guard: checks `residuals.std() < 1e-6` when `noise_sigma == 0`.
  - `check_group_dependency_transitions(df, meta) → list[Check]` — Per group dependency: computes observed conditional distribution via `df.groupby`, checks max absolute deviation < 0.10 against declared `conditional_weights`.
  - `_iter_predictor_cells(col_meta, meta) → Iterator` — Cartesian product of effect predictor column values. Skips cells with < 5 rows; caps at 100 cells tested.
- **Data flow:** Reads enriched `df` and `meta`. Structural residual computation reuses `engine/measures.py`'s formula evaluator as a shared utility.

#### `pattern_checks.py`
- **Spec ref:** §2.9 L3
- **Key functions:**
  - `check_patterns(df, meta) → list[Check]` — Dispatches by pattern type:
    - `check_outlier_entity(df, pattern, meta) → Check` — Filters target rows, computes z-score. Pass if z-score ≥ 2.0.
    - `check_trend_break(df, pattern, meta) → Check` — Splits by `break_point`, checks relative change magnitude > 15%.
    - `check_ranking_reversal(df, pattern, meta) → Check` — Groups by entity, computes rank correlation. Pass if `rank_corr < 0`.
    - `check_dominance_shift(df, pattern, meta) → Check` — Stub: returns `Check(passed=True, detail="not yet implemented")`.
    - `check_convergence(df, pattern, meta) → Check` — Stub: returns `Check(passed=True, detail="not yet implemented")`.
    - `check_seasonal_anomaly(df, pattern, meta) → Check` — Stub: returns `Check(passed=True, detail="not yet implemented")`.
- **Data flow:** Reads `df` and `meta["patterns"]`. All checks are independent.

#### `autofix.py`
- **Spec ref:** §2.9 auto-fix loop (Loop B)
- **Key classes / functions:**
  - `generate_with_validation(generate_fn, store, meta, base_seed, max_retries=3) → tuple[pd.DataFrame, ValidationReport]` — Loop B wrapper. Per attempt: (1) call `generate_fn(store, seed=base_seed + attempt, overrides=overrides)` to produce DataFrame (pre-realism); (2) call `SchemaAwareValidator.validate(df, meta)`; (3) if all pass, apply realism if needed and return; (4) if failures exist, dispatch auto-fix strategies, update `overrides`, continue. On retry exhaustion, return best result with partial failures logged.
  - `AUTO_FIX: dict[str, Callable]` — Dispatch table mapping check name prefixes to strategies:
    - `"marginal_"` / `"ks_"` → `widen_variance` — Multiplies relevant `sigma` intercept by a factor (e.g., 1.5×).
    - `"outlier_"` / `"trend_"` → `amplify_magnitude` — Multiplies pattern `z_score` or `magnitude` parameter by a factor.
    - `"orthogonal_"` → `reshuffle_pair` — Independently reshuffles a root column (different seed yields different shuffle).
  - `ParameterOverrides` — Dict-like structure holding mutation deltas. Passed alongside store to `run_pipeline()`, avoiding direct modification of the frozen `DeclarationStore`. Deltas accumulate across retries.
- **Data flow:** Each attempt calls `engine.generator.run_pipeline()` (via `generate_fn`) and `validator.validate()`. Mutation deltas accumulate in `ParameterOverrides` across retries. Validation runs pre-realism; realism is applied only after validation passes.

**Module integration points:**
- Receives the main DataFrame from M2, `schema_metadata` from M4.
- Produces the final validated `(DataFrame, schema_metadata, ValidationReport)` triple for Phase 3.
- Feeds back to M2 via Loop B: re-executes `run_pipeline()` with seed offset and parameter overrides.

---

## 4. Remaining Stubs & Known Limitations

All 36 NEEDS_CLAR items have been resolved. The items below are **intentional stubs** per decisions in `decisions/blocker_resolutions.md` — each requires spec clarification or a design decision before implementation.

### 4.1 Intentional Stubs (5)

#### Mixture Distribution Sampling (P1-1 / M1-NC-1)
- **Location:** `phase_2/engine/measures.py:297-303`
- **Behavior:** `_sample_stochastic()` raises `NotImplementedError` when `family == "mixture"`. Declaration via `add_measure("x", "mixture", {...})` succeeds (family is in `SUPPORTED_FAMILIES`), but `generate()` fails.
- **Blocked on:** The `param_model` schema for mixture distributions (component families, mixing weights, per-component parameters) is not defined in the spec.
- **To unstub:** Define the schema (suggested: `{"components": [{"family": "gaussian", "weight": 0.6, "params": {"mu": {...}, "sigma": {...}}}, ...]}`). Implement weighted-component sampling. Implement the corresponding KS test in `statistical.py`.

#### Dominance Shift Validation (P1-3 / M5-NC-4)
- **Location:** `phase_2/validation/pattern_checks.py:189-213`
- **Behavior:** `check_dominance_shift()` returns `Check(passed=True, detail="dominance_shift validation not yet implemented")`. Patterns can be declared (params validated), but validation always passes.
- **Blocked on:** The validation algorithm is not defined in the spec. The params schema (`entity_filter`, `col`, `split_point`) exists, but the rank-change-across-temporal-split logic is unspecified.
- **To unstub:** Define the algorithm: filter to entity, compute metric rank before/after `split_point`, check rank changed as declared.

#### Convergence Validation (P1-4 / M5-NC-5)
- **Location:** `phase_2/validation/pattern_checks.py:216-239`
- **Behavior:** `check_convergence()` returns `Check(passed=True, detail="convergence validation not yet implemented")`. Declaration succeeds (no required params), validation always passes.
- **Blocked on:** Completely absent from spec §2.9. No params schema, no validation logic, no examples.
- **To unstub:** Requires full spec definition: what converges, over what dimension, what threshold constitutes convergence.

#### Seasonal Anomaly Validation (P1-4 / M5-NC-5)
- **Location:** `phase_2/validation/pattern_checks.py:242-265`
- **Behavior:** Same as convergence — declaration succeeds, validation always passes.
- **Blocked on:** Completely absent from spec. No params, no validation logic.
- **To unstub:** Requires full spec definition: what constitutes a seasonal anomaly, which temporal features to check, detection thresholds.

#### M3 Context Window / Multi-Error (M3-NC-3, M3-NC-4)
- **Location (NC-3):** `phase_2/sdk/simulator.py:32-36` — TODO comment noting one-error-at-a-time limitation.
- **Location (NC-4):** `phase_2/orchestration/sandbox.py:657` — TODO comment noting no token-budget check.
- **Behavior:** (NC-3) The sandbox catches one exception per execution; multiple simultaneous SDK errors are surfaced one per retry. (NC-4) Full error history is sent to the LLM without truncation.
- **Status:** Both are functional and acceptable within the default `max_retries=3` budget. These are accepted limitations, not broken functionality.
- **To fix:** NC-3: Collect validation errors into a compound exception in M1. NC-4: Add token counting before each retry; truncate/summarize older failures if budget exceeded.

### 4.2 Dependent Stubs (4)

These exist in other modules as consequences of the 5 intentional stubs above. They resolve automatically when their parent stub is resolved.

#### Censoring Injection (depends on M1-NC-7)
- **Location:** `phase_2/engine/realism.py:59-62`
- **Behavior:** `inject_realism()` raises `NotImplementedError` when `realism_config["censoring"]` is non-None. `set_realism(censoring=...)` accepts and stores the parameter, but the engine-side injection is deferred.
- **Resolves when:** The spec defines what censoring means concretely (which columns, what mechanism).

#### Four Pattern Type Injection (depends on M1-NC-6)
- **Location:** `phase_2/engine/patterns.py:67-70`
- **Behavior:** `inject_patterns()` raises `NotImplementedError` for `ranking_reversal`, `dominance_shift`, `convergence`, and `seasonal_anomaly`.
- **Note:** These are **injection** stubs (M2 — how to modify the DataFrame to create the pattern), separate from the **validation** stubs above (M5 — how to check if the pattern exists). Ranking reversal validation is fully implemented, but ranking reversal injection is still stubbed.
- **Resolves when:** The injection algorithms are defined (how to artificially create each pattern in generated data).

#### Mixture KS Test (depends on P1-1)
- **Location:** `phase_2/validation/statistical.py:259-264`
- **Behavior:** `check_stochastic_ks()` returns `Check(passed=True)` when `family == "mixture"`.
- **Resolves when:** Mixture distribution sampling is implemented.

#### Multi-Column Group Dependency `on` (P2-4 / M1-NC-5)
- **Location:** `phase_2/sdk/relationships.py:126-130`
- **Behavior:** `add_group_dependency()` raises `NotImplementedError` when `len(on) != 1`. Single-column `on` works fully.
- **Blocked on:** The nested `conditional_weights` structure for 2+ conditioning columns is not specified.
- **Resolves when:** The spec defines the multi-column conditional_weights structure (e.g., Cartesian product keys vs. hierarchical nesting).
