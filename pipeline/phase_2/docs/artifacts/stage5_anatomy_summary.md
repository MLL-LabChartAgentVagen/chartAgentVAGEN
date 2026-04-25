# Stage 5: Phase 2 Implementation Summary

**System:** AGPDS Phase 2 — Agentic Data Simulator (SDK-Driven)
**Source:** `stage4_implementation_anatomy.md` (blueprint), post-implementation state
**Status:** All 36 NEEDS_CLAR items resolved. Remaining stubs documented in `docs/gaps.md`.

**Reconciliation log:**
- 2026-04-15 — updated to match actual implementation per `anatomy_implementation_drift.md`.
- 2026-04-22 — reconciled post-round-3 API surface: removed stale `scale` from the `ColumnDescriptor` field list (§Shared Infrastructure → `types.py`) and the `scale=None` kwarg from the `add_measure` signature (§M1 → `columns.py`) to match the round-3 `scale` kwarg removal; added the corresponding stub entry to §4.1. See `docs/fixes/GPT_FAILURE_ROUND_3_FIXES.md`.

**Doc role:** This file tracks the *current* Phase 2 implementation. Despite §9.1 of `anatomy_implementation_drift.md` recommending the anatomy be preserved as the original spec-design record, the 2026-04-15 reconciliation cycle converted it to an implementation-tracking reference, and subsequent reconciliations (see log above) have extended that pattern. For original spec-design intent, consult the *anatomy-claim* column of `anatomy_implementation_drift.md` §1–§7 — that column records what the anatomy said *before* the 2026-04-15 reconciliation and is the only remaining record of the original spec-design wording. Note that the drift report itself is a 2026-04-15 snapshot; it does not reflect the 2026-04-22 round-3 changes.

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
│   │   ├── prompt.py                   # §2.5 — SYSTEM_PROMPT_TEMPLATE constant,
│   │   │                               #   render_system_prompt(scenario_context: str) -> str
│   │   ├── sandbox.py                  # §2.7 — execute_in_sandbox(), run_retry_loop(),
│   │   │                               #   format_error_feedback(), SandboxResult,
│   │   │                               #   _TrackingSimulator, _build_sandbox_namespace()
│   │   ├── retry_loop.py              # §2.7 — orchestrate() -> (df, meta, raw_decl)|SkipResult,
│   │   │                               #   _format_scenario_context, _make_generate_fn
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
│   │   ├── groups.py                   # §2.2 — dimension group incremental registration:
│   │   │                               #   register_categorical_column, register_temporal_group,
│   │   │                               #   get_roots, is_group_root, get_group_for_column
│   │   ├── dag.py                      # §2.3 — detect_cycle_in_adjacency, check_measure_dag_acyclic,
│   │   │                               #   build_full_dag, extract_measure_sub_dag,
│   │   │                               #   topological sort (Kahn's)
│   │   └── validation.py               # §2.1.1, §2.1.2 — declaration-time validation rules:
│   │                                   #   name uniqueness, parent-same-group, root-only deps,
│   │                                   #   effect predictor existence, per-parent weight coverage,
│   │                                   #   formula symbol resolution
│   │
│   ├── engine/                         # ── M2: Generation Engine (§2.4, §2.8) ──
│   │   ├── __init__.py
│   │   ├── generator.py                # §2.8 — run_pipeline() orchestrator:
│   │   │                               #   takes decomposed store fields (columns, groups,
│   │   │                               #   group_dependencies, measure_dag, etc.),
│   │   │                               #   pre-flight DAG build, RNG init, stage dispatch,
│   │   │                               #   accepts overrides dict for Loop B auto-fix
│   │   ├── skeleton.py                 # §2.8 stage α — build_skeleton():
│   │   │                               #   sample_independent_root, sample_dependent_root,
│   │   │                               #   sample_child_category, temporal sampling + derivation
│   │   ├── measures.py                 # §2.8 stage β — _sample_stochastic(), _eval_structural()
│   │   │                               #   Stochastic: intercept + Σ effects → family draw
│   │   │                               #     (7 families: gaussian, lognormal, gamma, beta,
│   │   │                               #      uniform, poisson, exponential)
│   │   │                               #   Structural: _safe_eval_formula (restricted AST) + noise
│   │   │                               #   Per-row param computation: _compute_per_row_params
│   │   ├── patterns.py                 # §2.8 stage γ — inject_patterns():
│   │   │                               #   outlier_entity, trend_break (fully implemented)
│   │   │                               #   Pattern overlap: sequential mutation in declaration order
│   │   │                               #   Target parsing via df.eval()
│   │   ├── realism.py                  # §2.8 stage δ — inject_realism():
│   │   │                               #   inject_missing_values (all columns, NaN),
│   │   │                               #   inject_dirty_values (categoricals)
│   │   └── postprocess.py              # §2.8 — to_dataframe():
│   │                                   #   dict → pd.DataFrame, RangeIndex, datetime64 cast,
│   │                                   #   column order matches topo_order
│   │
│   ├── metadata/                       # ── M4: Schema Metadata (§2.6) ──
│   │   ├── __init__.py
│   │   └── builder.py                  # §2.6 — build_schema_metadata(unpacked registries) → dict
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
│       ├── validator.py                # §2.9 — SchemaAwareValidator(meta).validate(df, patterns):
│       │                               #   orchestrates L1/L2/L3, _run_l3 dispatches pattern checks
│       ├── structural.py               # §2.9 L1 — row count, check_categorical_cardinality,
│       │                               #   marginal weights, measure finiteness, orthogonal χ²,
│       │                               #   check_measure_dag_acyclic
│       ├── statistical.py              # §2.9 L2 — KS-test per predictor cell (stochastic),
│       │                               #   residual mean/std check (structural),
│       │                               #   conditional transition deviation (group deps)
│       │                               #   Predictor cell enumeration: Cartesian product,
│       │                               #   skip < 5 rows, cap at 100 cells
│       ├── pattern_checks.py           # §2.9 L3 — outlier z-score, trend break magnitude,
│       │                               #   ranking reversal correlation (fully implemented)
│       │                               #   dominance_shift, convergence, seasonal_anomaly (stubs)
│       └── autofix.py                  # §2.9 — generate_with_validation() Loop B wrapper:
│                                       #   match_strategy() fnmatch dispatch to widen_variance,
│                                       #   amplify_magnitude, reshuffle_pair; seed=base+attempt,
│                                       #   max 3 retries; overrides dict (frozen store untouched)
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
  - `ColumnDescriptor` — Frozen dataclass with fields: `name`, `type` (categorical / temporal / measure), `group`, `parent`, `family`, `param_model`, `formula`, `effects`, `noise`, `derive`, `values`, `weights`. Not all fields are populated for every column type; unused fields default to `None`. This is the canonical single-column representation flowing from M1 into M2 and M4. (The former `scale` field was removed in round-3 alongside the `add_measure(..., scale=...)` kwarg — see §4.1 "`scale` Kwarg on `add_measure`".)
  - `PatternSpec` — Dataclass: `type` (str enum), `target` (filter expression string), `col` (column name), `params` (dict).
  - `OrthogonalPair` — Dataclass: `group_a`, `group_b`, `rationale`.
  - `GroupDependency` — Dataclass: `child_root`, `on` (list of root column names), `conditional_weights` (nested dict).
  - `RealismConfig` — Optional dataclass: `missing_rate`, `dirty_rate`, `censoring`.
  - `DeclarationStore` — Composite container holding: `columns`, `groups`, `measure_dag`, `orthogonal_pairs`, `group_dependencies`, `patterns`, `realism_config`, `target_rows`, `seed`. Exposes `freeze()` to transition from mutable to read-only, and `_check_mutable()` to enforce the freeze contract. This is the sole artifact crossing the M1 boundary into M2 and M4.
  - `Check` — Validation result record: `name`, `passed` (bool), `detail` (str | None). Used by M5.
  - `ValidationReport` — List of `Check` objects with aggregated pass/fail result.
  - `ParameterOverrides` — Conceptual name for the plain `dict` used as Loop B auto-fix mutation deltas (e.g., `overrides["measures"][col]["sigma"]`). Not a custom class — a regular nested dict.
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
  - `SkipResult` — Sentinel dataclass (not an exception) with fields `scenario_id: str` and `error_log: list[str]`, produced by M3 when all retries are exhausted. Checked by `pipeline.py`.
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
  - `SYSTEM_PROMPT_TEMPLATE: str` — Module-level constant containing the full system prompt as a single template string with 5 composable regions: role preamble, SDK method whitelist (Step 1 + Step 2 blocks), hard constraints (HC1–HC9), soft guidelines, and one-shot example. Contains a `{scenario_context}` slot for substitution. Lists 8 supported distribution families (`gaussian`, `lognormal`, `gamma`, `beta`, `uniform`, `poisson`, `exponential`, `mixture`) and 6 pattern types (`outlier_entity`, `trend_break`, `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`) as inline string literals within the template.
  - `render_system_prompt(scenario_context: str) → str` — Performs `SYSTEM_PROMPT_TEMPLATE.replace("{scenario_context}", scenario_context)` to produce the final system prompt string.
- **Data flow:** `render_system_prompt()` is called by `retry_loop.py` to produce the system prompt string. The scenario context is pre-formatted by `retry_loop._format_scenario_context()`.

#### `sandbox.py`
- **Spec ref:** §2.7 step 2
- **Key classes / functions:**
  - `SandboxResult` — Dataclass: `success` (bool), `dataframe`, `metadata`, `raw_declarations`, `exception`, `traceback_str`.
  - `execute_in_sandbox(source_code: str, timeout_seconds: int, sandbox_namespace: dict) → SandboxResult` — Compiles and executes the script in a controlled scope via `exec()`. On success, returns `SandboxResult(success=True, ...)` with the DataFrame and metadata from the script's `FactTableSimulator` instance. On failure, returns `SandboxResult(success=False, exception=..., traceback_str=...)`.
  - `_TrackingSimulator` — Subclass of `FactTableSimulator` that registers instances so the sandbox can recover the simulator's internal state after execution.
  - `_build_sandbox_namespace() → dict` — Builds the namespace dict for `exec()`, injecting `_TrackingSimulator`, safe builtins, and allowed imports.
  - `run_retry_loop(initial_code, generate_fn, system_prompt, max_retries, timeout_seconds=30, sandbox_namespace_factory=None) → SandboxResult | SkipResult` — Executes the full retry loop: compile, execute, on failure format error feedback and re-prompt via `generate_fn`.
  - `format_error_feedback(original_code: str, exception: Exception, traceback_str: str) → str` — Formats code + traceback into the feedback message for the next retry.
- **Data flow:** `run_retry_loop()` is called by `retry_loop.orchestrate()`. Each attempt calls `execute_in_sandbox()` with a fresh namespace. On failure, `format_error_feedback()` produces the error context for the LLM re-prompt.
- **Implementation decisions:** In-process `exec()` with fresh namespace per attempt. Configurable timeout as a plain `int` parameter. Catches all `Exception` subclasses and captures full traceback.

#### `retry_loop.py`
- **Spec ref:** §2.7
- **Key classes / functions:**
  - `orchestrate(scenario_context: dict, llm_client: LLMClient, max_retries: int = 3) → (pd.DataFrame, dict, dict) | SkipResult` — Loop A driver. Steps: (1) call `_format_scenario_context()` then `render_system_prompt()` to build the system prompt; (2) call `_make_generate_fn(llm_client)` to create the code generation closure; (3) generate initial code via `llm_client.generate_code()` then `extract_clean_code()`; (4) delegate the full retry loop to `sandbox.run_retry_loop()`; (5) on success return `(df, metadata, raw_declarations)` triple; (6) on retry exhaustion, return `SkipResult(scenario_id=..., error_log=...)`.
  - `_format_scenario_context(scenario_context: dict) → str` — Serializes the scenario dict into a string for prompt injection.
  - `_make_generate_fn(llm_client) → Callable` — Creates a closure that calls `llm_client.generate_code()` then `extract_clean_code()` on each retry.
- **Data flow:** Seeds with `prompt.py`'s `render_system_prompt()` output. Delegates retry execution to `sandbox.run_retry_loop()`. Each retry sends `(system_prompt, error_feedback)` as two messages to the LLM — no accumulating conversation history.

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
- Produces `(pd.DataFrame, dict, dict)` triple on success, or `SkipResult` on terminal failure.

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
  - `add_measure(name, family, param_model)` — Validates: `family` in `SUPPORTED_FAMILIES`, all effect predictor columns exist, all symbolic effects have numeric definitions. Creates `ColumnDescriptor(type="measure", measure_type="stochastic")`. No DAG edges (root measure). (A `scale=None` kwarg existed previously but was removed in round-3 — passing it now raises `TypeError`; see §4.1.)
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
  - `DimensionGroup` — Dataclass (defined in `types.py`): `name`, `root` (column name), `columns` (list), `hierarchy` (list, root-first order).
  - `register_categorical_column(groups, name, group, parent, columns)` — Incrementally registers a categorical column into its dimension group. Creates the group if it doesn't exist, tracks root and hierarchy.
  - `register_temporal_group(groups, name, group, derived_names)` — Registers a temporal group with its root date column and derived features. `hierarchy` contains only the root date column, not derived features.
  - `get_roots(groups) → list[str]` — Returns root column names for each group. Used by `relationships.py` for root-only validation.
  - `is_group_root(column_name, columns, groups) → bool` — Checks if a column is the root of its group.
  - `get_group_for_column(column_name, columns) → str | None` — Returns the group name for a column, or None.
- **Data flow:** Called incrementally by `columns.py` (each `add_category` calls `register_categorical_column`, each `add_temporal` calls `register_temporal_group`). Also called by `dag.py` to identify hierarchy edges in the full column DAG.

#### `dag.py`
- **Spec ref:** §2.3, §2.4
- **Key functions:**
  - `detect_cycle_in_adjacency(adjacency: dict) → list | None` — Detects cycles in a directed graph. Returns the cycle path if found, `None` if acyclic.
  - `check_measure_dag_acyclic(measure_dag: dict) → None | raises CyclicDependencyError` — Validates that the measure DAG has no cycles.
  - `topological_sort(edges: set, nodes: list) → list[str]` — Kahn's algorithm; raises `CyclicDependencyError` on cycle detection.
  - `build_full_dag(columns, groups, group_dependencies, measure_dag) → tuple[dict, list[str]]` — Aggregates edges from 5 sources into a unified DAG: (1) intra-group hierarchy (`parent` → child); (2) cross-group root dependencies; (3) temporal derivation (root → derived features); (4) measure predictor refs; (5) measure-measure DAG. Returns adjacency list and topological order. Used by both M2's pre-flight and M1's incremental validation.
  - `extract_measure_sub_dag(full_dag: dict, measure_names: set[str]) → tuple[dict, list[str]]` — Extracts the measure-only sub-DAG and its topological order.
- **Data flow:** `columns.py` adds measure DAG edges inline in `add_measure_structural()` (no separate `add_measure_edge` function); `relationships.py` calls `check_measure_dag_acyclic()` for root DAG edges in `add_group_dependency()`; `generator.py` (M2) calls `build_full_dag()` during pre-flight.

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

**Purpose:** M2 is the deterministic computation core. It receives decomposed declaration store fields (columns, groups, group_dependencies, measure_dag, etc.) and a seed integer and generates the main DataFrame through a four-stage pipeline: skeleton (α), measures (β), patterns (γ), and realism (δ). The pipeline maintains a single `numpy.random.Generator` stream throughout; its sequential consumption is the sole guarantee of bit-for-bit reproducibility. No LLM calls occur within this module. M2 is re-executed during Loop B (M5 auto-fix) with a per-attempt seed offset.

**Files:**

#### `generator.py`
- **Spec ref:** §2.8 — pipeline orchestrator
- **Key functions:**
  - `run_pipeline(columns, groups, group_dependencies, measure_dag, target_rows, seed, patterns=None, realism_config=None, overrides=None, orthogonal_pairs=None) → tuple[pd.DataFrame, dict]` — Entry point. Takes 10 decomposed parameters (not a `DeclarationStore`). Steps: (1) pre-flight: call `dag.build_full_dag(columns, groups, group_dependencies, measure_dag)` to get `topo_order`; (2) init `rng = np.random.default_rng(seed)`; (3) `skeleton.build_skeleton()` → partial row dict; (4) `measures.generate_measures()` → full row dict; (5) `postprocess.to_dataframe()` → `pd.DataFrame`; (6) `patterns.inject_patterns()` → mutated DataFrame; (7) if `realism_config` exists, `realism.inject_realism()`; (8) `metadata.builder.build_schema_metadata()` → metadata dict; (9) return tuple.
  - The single `rng` object is passed by reference to all stages — this is the critical determinism invariant.
  - The optional `overrides` parameter lets Loop B auto-fix strategies take effect without modifying the frozen store.
- **Data flow:** Calls `skeleton.py`, `measures.py`, `postprocess.py`, `patterns.py`, `realism.py` in sequence. Also calls `dag.py` (M1) for pre-flight DAG construction and `metadata/builder.py` (M4) for metadata generation.

#### `skeleton.py`
- **Spec ref:** §2.8 stage α
- **Key functions:**
  - `build_skeleton(columns, target_rows, group_dependencies, topo_order, rng) → dict[str, np.ndarray]` — Iterates `topo_order`, skipping measure columns. Dispatches each non-measure column to its sampler:
    - Root categorical → `sample_independent_root()` — `rng.choice()` by marginal weights.
    - Child categorical → `sample_child_category()` — Row-wise conditional sampling from parent values. Supports flat broadcast and per-parent dict weight forms.
    - Cross-group dependent root → `sample_dependent_root()` — Samples from `conditional_weights` based on upstream root column values.
    - Temporal root → `sample_temporal_root()` — Uniform sampling within `[start, end]` at declared `freq`.
    - Temporal derived → `derive_temporal_child()` — Deterministic extraction (`DOW()`, `MONTH()`, `QUARTER()`, `IS_WEEKEND()`), no RNG consumption.
  - Returns column name → numpy array dict, each array length `target_rows`.
- **Data flow:** Reads `columns`, `group_dependencies`. Output passes directly to `measures.py`.

#### `measures.py`
- **Spec ref:** §2.8 stage β, §2.3
- **Key functions:**
  - `generate_measures(columns, topo_order, rows, rng, overrides=None) → dict[str, np.ndarray]` — Iterates `topo_order`, processing only measure columns, dispatching by `measure_type`:
    - `_sample_stochastic(col_name, col_meta, rows, rng, overrides=None) → np.ndarray` — Per-row parameter computation via `_compute_per_row_params()` (`intercept + Σ effects`), applies any `overrides` scaling, then samples from the specified family via `rng`. Dispatches to: `rng.normal()`, `rng.lognormal()`, `rng.gamma()`, `rng.beta()`, `rng.uniform()`, `rng.poisson()`, `rng.exponential()`.
    - `_eval_structural(col_name, col_meta, rows, rng, overrides=None) → np.ndarray` — Evaluates formula string with variable bindings from row context (upstream measure values + resolved effects); adds noise if `noise != {}`.
    - `_resolve_effects(effects_dict, rows) → np.ndarray` — Vectorized effect resolution: per-row categorical context lookup and summation.
    - `_compute_per_row_params(col_meta, rows, overrides) → dict` — Computes distribution parameters per row, including inline clamping to legal intervals (e.g., `sigma = max(sigma, 1e-6)` for gaussian).
    - `_safe_eval_formula(formula, bindings) → float | np.ndarray` — Restricted AST formula evaluator. Parses via `ast.parse(formula, mode='eval')`, walks the tree accepting only `BinOp` (`+`, `-`, `*`, `/`, `Pow`), `UnaryOp` (`-`), `Constant` (int/float), and `Name` nodes. All other AST node types raise `ValueError`.
- **Data flow:** Reads skeleton-stage `rows` and `columns`. Modifies `rows` dict in-place, adding measure columns. `rng` advances one step per stochastic measure per row; structural measures with noise consume additional RNG.

#### `patterns.py`
- **Spec ref:** §2.8 stage γ
- **Key functions:**
  - `inject_patterns(df, patterns, columns, rng) → pd.DataFrame` — Iterates `patterns` list in declaration order. Calls type-specific injectors. Returns modified DataFrame.
  - `inject_outlier_entity(df, pattern) → pd.DataFrame` — Parses `target` filter via `df.eval()`, selects matching rows, scales `col` values to declared `z_score`.
  - `inject_trend_break(df, pattern, columns) → pd.DataFrame` — Splits rows by temporal `break_point`, applies magnitude shift to `col` values after the break.
  - Target parsing uses `df.eval()` directly (no separate `_parse_target_filter` function).
  - Pattern overlap: sequential mutation in declaration order.
- **Data flow:** Reads `patterns` list and mutates `df` in-place.

#### `realism.py`
- **Spec ref:** §2.8 stage δ
- **Key functions:**
  - `inject_realism(df, realism_config, columns, rng) → pd.DataFrame` — Applies realism degradation per `realism_config`. Processes `missing_rate` first (higher precedence), then `dirty_rate`.
  - `inject_missing_values(df, rate, rng) → pd.DataFrame` — For each column, randomly selects `rate` proportion of rows and replaces with `np.nan`.
  - `inject_dirty_values(df, rate, columns, rng) → pd.DataFrame` — Categorical columns only: randomly replaces values with another valid value from the column's `values` list.
- **Data flow:** Reads `realism_config` and `columns`, mutates `df` in-place. Random cell selection consumes `rng`.

#### `postprocess.py`
- **Spec ref:** §2.8 `_post_process` / `τ_post`
- **Key functions:**
  - `to_dataframe(rows, topo_order, columns, target_rows) → pd.DataFrame` — Converts column name → numpy array dict to `pd.DataFrame`, assigns `RangeIndex`, casts temporal columns to `datetime64[ns]`, maintains column order consistent with `topo_order`.
- **Data flow:** Pure conversion; no additional state modification beyond DataFrame construction.

**Module integration points:**
- Receives decomposed store fields + `seed` from M1 via `pipeline.py`.
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
  - `build_schema_metadata(groups, orthogonal_pairs, target_rows, measure_dag_order, columns, group_dependencies, patterns) → dict` — The sole public function. Takes unpacked store registries (not a `DeclarationStore` object). Assembles a 7-key dictionary:
    - `"dimension_groups"` — From `groups`: `{group_name: {columns: [...], hierarchy: [...]}}` via `DimensionGroup.to_metadata()`. Temporal groups have `hierarchy` containing only the root date column, while `columns` includes derived features.
    - `"orthogonal_groups"` — From `orthogonal_pairs` via `OrthogonalPair.to_metadata()`: `{group_a, group_b, rationale}` list.
    - `"group_dependencies"` — From `group_dependencies` via `GroupDependency.to_metadata()`. Enriched: includes `conditional_weights`, not just dependency edges.
    - `"columns"` — Flattened from `columns` via `_build_columns_metadata()`. Type-discriminated descriptor array. Enriched: categoricals include `values`, `weights`, `cardinality`; stochastic measures include full `param_model` and `family`; structural measures include `formula`, `effects`, `noise`, `depends_on`.
    - `"measure_dag_order"` — Passed in directly (pre-computed by `dag.extract_measure_sub_dag()`).
    - `"patterns"` — From `patterns`. Enriched: includes full `params`.
    - `"total_rows"` — From `target_rows`.
  - `_build_columns_metadata(columns) → list[dict]` — Builds type-discriminated column descriptors with defensive deep-copying of mutable fields.
  - `_deep_copy_param_model(param_model) → dict` — Defensive copy of nested param_model dicts.
  - `_assert_metadata_consistency(meta) → None` — Post-build self-check via `logger.warning()` (does not raise): every column in `dimension_groups` must appear in `columns` with matching `group`; every entry in `measure_dag_order` must exist in `columns`; every pattern's `col` must be a measure column; every `orthogonal_groups` entry must reference valid group names.
- **Data flow:** Reads unpacked registries passed as parameters. Returns the assembled dict.

**Module integration points:**
- Receives unpacked store registries from M1 via `generator.py`.
- Produces `schema_metadata` dict for M5 (validation) and Phase 3 (view extraction, QA generation).

---

### Module: Validation Engine (M5) — `phase_2/validation/`

**Purpose:** M5 is Phase 2's terminal module. It validates the generated main DataFrame against declarations at 3 levels (structural, statistical, pattern), and implements the auto-fix retry loop (Loop B); when checks fail, it re-executes M2 with a different seed offset. M5 makes no LLM calls — all fixes are parameter adjustments. Its final output is the validated triple for Phase 3: `(DataFrame, schema_metadata, ValidationReport)`.

**Files:**

#### `validator.py`
- **Spec ref:** §2.9 — `SchemaAwareValidator` orchestrator
- **Key classes / functions:**
  - `SchemaAwareValidator(meta)` — Constructor receives `schema_metadata`. Orchestrates all 3 check levels.
    - `validate(df, patterns=None) → ValidationReport` — Sequentially calls `_run_l1(df)`, `_run_l2(df)`, `_run_l3(df)`, aggregates all `Check` objects into a `ValidationReport`. `patterns` is optional (for L3 pattern-aware checks).
  - L3 dispatch is handled by `_run_l3()` directly (no separate `check_patterns` dispatcher function). `_run_l3()` dispatches to individual check functions based on pattern type.
  - The validator consumes only `schema_metadata` (requiring it to be enriched per M4's P0 decision), not the `DeclarationStore` directly. This preserves module boundaries.
- **Data flow:** Delegates to `structural.py`, `statistical.py`, `pattern_checks.py`, then aggregates results.

#### `structural.py`
- **Spec ref:** §2.9 L1
- **Key functions:**
  - `check_row_count(df, meta) → Check` — `abs(len(df) - meta["total_rows"]) / meta["total_rows"] < 0.1`.
  - `check_categorical_cardinality(df, meta) → list[Check]` — Per categorical column: `df[col].nunique() == col["cardinality"]`.
  - `check_marginal_weights(df, meta) → list[Check]` — Per root categorical: max deviation from declared `weights` < 0.10.
  - `check_measure_finiteness(df, meta) → list[Check]` — Per measure column: `notna().all()` and `isfinite().all()`.
  - `check_orthogonal_independence(df, meta) → list[Check]` — Per `orthogonal_groups` root column pair: `chi2_contingency`, pass if p > 0.05.
  - `check_measure_dag_acyclic(meta) → Check` — Redundant acyclicity verification on `measure_dag_order`.
- **Data flow:** Reads `df` and `meta`, returns `list[Check]`. All checks are independent.

#### `statistical.py`
- **Spec ref:** §2.9 L2
- **Key functions:**
  - `check_stochastic_ks(df, col_name, meta, patterns) → list[Check]` — Per stochastic measure: iterates predictor cells via `_iter_predictor_cells()` (Cartesian product of effect predictor values), filters matching rows, reconstructs expected distribution parameters (`intercept + Σ effects`), runs `scipy.stats.kstest`. Pass if p > 0.05.
  - `check_structural_residuals(df, col_name, meta, patterns) → Check` — Per structural measure: recomputes formula from actual upstream values (using `engine/measures._safe_eval_formula`), gets residuals, checks `abs(residuals.mean()) < residuals.std() * 0.1`, and (if `noise_sigma > 0`) `abs(residuals.std() - noise_sigma) / noise_sigma < 0.2`. Zero-noise guard: checks `residuals.std() < 1e-6` when `noise_sigma == 0`.
  - `check_group_dependency_transitions(df, meta) → list[Check]` — Per group dependency: computes observed conditional distribution via `df.groupby`, checks max absolute deviation < 0.10 against declared `conditional_weights`.
  - `_iter_predictor_cells(df, col_name, col_meta, columns_meta, min_rows=5, max_cells=100) �� Iterator` — Cartesian product of effect predictor column values. Skips cells with < `min_rows` rows; caps at `max_cells` tested.
- **Data flow:** Reads enriched `df` and `meta`. Structural residual computation reuses `engine/measures.py`'s `_safe_eval_formula` and `_resolve_effects` as shared utilities. Uses `sdk/validation.py`'s `extract_formula_symbols` for symbol extraction.

#### `pattern_checks.py`
- **Spec ref:** §2.9 L3
- **Key functions:** (dispatched by `validator._run_l3()`, not a `check_patterns` dispatcher)
  - `check_outlier_entity(df, pattern) → Check` ��� Filters target rows, computes z-score. Pass if z-score ≥ 2.0.
  - `check_trend_break(df, pattern, meta) → Check` — Splits by `break_point`, checks relative change magnitude > 15%.
  - `check_ranking_reversal(df, pattern, meta) → Check` — Groups by entity, computes rank correlation. Pass if `rank_corr < 0`.
  - `check_dominance_shift(df, pattern, meta) → Check` — Stub: returns `Check(passed=True, detail="not yet implemented")`.
  - `check_convergence(df, pattern, meta) → Check` — Stub: returns `Check(passed=True, detail="not yet implemented")`.
  - `check_seasonal_anomaly(df, pattern, meta) → Check` — Stub: returns `Check(passed=True, detail="not yet implemented")`.
- **Data flow:** Reads `df` and pattern dicts. All checks are independent.

#### `autofix.py`
- **Spec ref:** §2.9 auto-fix loop (Loop B)
- **Key classes / functions:**
  - `generate_with_validation(build_fn, meta, patterns, base_seed=42, max_attempts=3) → tuple[pd.DataFrame, ValidationReport]` — Loop B wrapper. `build_fn` is a `Callable[[int, ParameterOverrides | None], tuple[pd.DataFrame, dict]]` closure over the store. Per attempt in `range(max_attempts)`: (1) call `build_fn(base_seed + attempt, overrides)` to produce DataFrame (pre-realism); (2) call `SchemaAwareValidator(meta).validate(df, patterns)`; (3) if all pass, apply realism if needed and return; (4) if failures exist, dispatch auto-fix strategies via `match_strategy()`, update `overrides`, continue. On retry exhaustion, return best result with partial failures logged.
  - `match_strategy(check_name) → Callable | None` — Uses `fnmatch` to match check names against glob patterns and dispatch to the appropriate strategy function:
    - `"marginal_*"` / `"ks_*"` → `widen_variance` — Multiplies relevant `sigma` intercept by a factor (e.g., 1.2×).
    - `"outlier_*"` / `"trend_*"` → `amplify_magnitude` — Multiplies pattern `z_score` or `magnitude` parameter by a factor (e.g., 1.3×).
    - `"orthogonal_*"` → `reshuffle_pair` — Appends column to reshuffle list (idempotent; different seed yields different shuffle).
  - `widen_variance(check, overrides, factor=1.2)`, `amplify_magnitude(check, overrides, patterns=None, factor=1.3)`, `reshuffle_pair(check, overrides)` — Standalone strategy functions. All mutate the `overrides` dict in-place.
  - Overrides are a plain `dict` with nested keys (e.g., `overrides["measures"][col]["sigma"]`), not a custom class. Passed alongside store to `run_pipeline()`, avoiding direct modification of the frozen `DeclarationStore`. Deltas accumulate across retries.
- **Data flow:** Each attempt calls `engine.generator.run_pipeline()` (via `generate_fn`) and `validator.validate()`. Mutation deltas accumulate in `overrides` dict across retries. Validation runs pre-realism; realism is applied only after validation passes.

**Module integration points:**
- Receives the main DataFrame from M2, `schema_metadata` from M4.
- Produces the final validated `(DataFrame, schema_metadata, ValidationReport)` triple for Phase 3.
- Feeds back to M2 via Loop B: re-executes `run_pipeline()` with seed offset and parameter overrides.

---

## 4. Remaining Stubs & Known Limitations

All 36 NEEDS_CLAR items have been resolved. The items below are **intentional stubs** per decisions in `decisions/blocker_resolutions.md` — each requires spec clarification or a design decision before implementation.

### 4.1 Intentional Stubs (6)

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

#### `scale` Kwarg on `add_measure` (M?-NC-scale)
- **Location:** `phase_2/sdk/columns.py:214-215` (`TODO [M?-NC-scale]` marker), mirrored in `phase_2/orchestration/prompt.py`.
- **Behavior:** `add_measure(name, family, param_model)` no longer accepts a `scale` keyword argument. Passing `scale=...` raises `TypeError: add_measure() got an unexpected keyword argument 'scale'`. The prompt no longer advertises the kwarg.
- **History:** Previously accepted but silently no-op (emitted a "stored but has no effect" warning). Removed in round-3 GPT failure fixes (`docs/fixes/GPT_FAILURE_ROUND_3_FIXES.md`) because LLMs treated it as a meaningful knob and burned retry budget tuning a dead parameter — same advertising-a-nonfeature class as `censoring=` and the deferred pattern types removed in round 2.
- **To unstub:** Implement a scaling mechanism (e.g., post-sampling multiplicative scaling of measure values), then restore the `scale` kwarg in `sdk/columns.py` and re-add it to the `add_measure` signature shown in `orchestration/prompt.py`. Grep for `TODO [M?-NC-scale]` to find both sites.

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
