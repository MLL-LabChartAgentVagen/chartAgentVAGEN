# Anatomy Summary vs Implementation Drift Report

**Source document:** `docs/artifacts/stage5_anatomy_summary.md`
**Methodology:** Audit of SVG flow diagram guides (`docs/svg/module[1-5]_*.md`) against implementation code in `phase_2/`
**Date:** 2026-04-15

---

## 1. Systematic Drift Patterns

Four recurring patterns account for most discrepancies.

### Pattern A: `store`-based API replaced by decomposed parameters

The anatomy describes M2 engine functions accepting a `DeclarationStore` object. The implementation decomposed the store into individual parameters (`columns`, `groups`, `group_dependencies`, `measure_dag`, `target_rows`, `seed`, etc.). This affects every public function in `phase_2/engine/`.

### Pattern B: Functions referenced in anatomy that do not exist

Several function and class names in the anatomy were never implemented or were replaced during development. These references produce dead links when tracing from documentation to code.

### Pattern C: Functions that exist under different names

Some functions were implemented with different naming conventions (e.g., public vs private, different verb choices) than what the anatomy specified.

### Pattern D: Features described but never implemented

Certain cross-cutting features described in the anatomy (notably `pattern_mask` cell protection and the `AUTO_FIX` dispatch dict) do not exist in the codebase.

---

## 2. Shared Infrastructure

| Anatomy Claim | Actual Code | Severity | Anatomy Location | Code Location |
|---|---|---|---|---|
| `DeclarationStore` field `column_registry` | Field is named `columns` | warning | Line 202 | `types.py` `DeclarationStore.__init__` |
| `DeclarationStore` field `group_graph` | Field is named `groups` | warning | Line 202 | `types.py` `DeclarationStore.__init__` |
| `DeclarationStore` field `group_deps` | Field is named `group_dependencies` | warning | Line 200–202 | `types.py` `DeclarationStore.__init__` |
| `DeclarationStore` field `pattern_list` | Field is named `patterns` | warning | Line 202 | `types.py` `DeclarationStore.__init__` |

---

## 3. Module 1: SDK Surface (`phase_2/sdk/`)

| Anatomy Claim | Actual Code | Severity | Anatomy Location | Code Location |
|---|---|---|---|---|
| `groups.py` provides `build_group_graph()` | Function does not exist. Group registration is done incrementally via `register_categorical_column()` and `register_temporal_group()` | error | Line 329 | `sdk/groups.py` |
| `groups.py` provides class `GroupInfo` | Class is named `DimensionGroup` | error | Line 329 | `types.py:28` |
| `dag.py` provides `add_measure_edge()` | Function does not exist. DAG edge addition is inline in `columns.py` `add_measure_structural()` | error | Line 336 | `sdk/dag.py` |
| `dag.py` provides `is_acyclic()` | Function is named `detect_cycle_in_adjacency()` | error | Line 339 | `sdk/dag.py:33` |
| `groups.py` provides `get_roots()` | Function exists and name matches | info | Line 330 | `sdk/groups.py` |

---

## 4. Module 2: Generation Engine (`phase_2/engine/`)

| Anatomy Claim | Actual Code | Severity | Anatomy Location | Code Location |
|---|---|---|---|---|
| `run_pipeline(store, seed, overrides=None, orthogonal_pairs=None)` — 4 params | Actual: `run_pipeline(columns, groups, group_dependencies, measure_dag, target_rows, seed, patterns, realism_config, overrides, orthogonal_pairs)` — 10 params [Pattern A] | error | Line 370 | `engine/generator.py:27-38` |
| `build_skeleton(store, topo_order, rng) -> dict[str, np.ndarray]` | Actual: `build_skeleton(columns, target_rows, group_dependencies, topo_order, rng)` — 5 params [Pattern A] | error | Line 378 | `engine/skeleton.py:31` |
| `generate_measures(store, topo_order, rows, rng, overrides=None)` | Actual: `generate_measures(columns, topo_order, rows, rng, overrides=None)` — `columns` not `store` [Pattern A] | error | Line 390 | `engine/measures.py:413` |
| `inject_patterns(store, rows, rng, overrides=None) -> dict` returning `rows` + `pattern_mask` | Actual: `inject_patterns(df, patterns, columns, rng) -> pd.DataFrame` — takes DataFrame, returns DataFrame, no `pattern_mask` [Patterns A + D] | error | Line 401 | `engine/patterns.py:29` |
| `inject_realism(store, rows, rng, pattern_mask=None)` with pattern cell protection | Actual: `inject_realism(df, realism_config, columns, rng)` — no `pattern_mask`, no cell protection [Patterns A + D] | error | Line 412 | `engine/realism.py:25` |
| `to_dataframe(rows, topo_order) -> pd.DataFrame` — 2 params | Actual: `to_dataframe(rows, topo_order, columns, target_rows)` — 4 params | error | Line 420 | `engine/postprocess.py:19` |
| Private helpers: `_sample_root_categorical()`, `_sample_child_categorical()` | Actual names: `sample_independent_root()`, `sample_dependent_root()`, `sample_child_category()` (public, no underscore) [Pattern C] | warning | Line 379-381 | `engine/skeleton.py:109, 134, 182` |
| `_resolve_effects` as standalone helper | Exists at `engine/measures.py:112` but structural eval inlines the resolution | warning | Line 393 | `engine/measures.py:112` |
| `_clamp_params` as standalone helper | Does not exist. Clamping is inline in `_compute_per_row_params` | warning | Line 394 | `engine/measures.py:392-402` |
| `_evaluate_formula` as standalone helper | Named `_safe_eval_formula` | warning | Line 395 | `engine/measures.py:39` |
| `_parse_target_filter` in patterns.py | Does not exist. Target parsing uses `df.eval()` directly | warning | Line 404 | `engine/patterns.py` |
| Pattern `pattern_mask` returned from `inject_patterns` and consumed by `inject_realism` and M5 L2 | Not implemented. No `pattern_mask` exists anywhere in the engine [Pattern D] | error | Lines 401, 406, 412 | — |

---

## 5. Module 3: LLM Orchestration (`phase_2/orchestration/`)

| Anatomy Claim | Actual Code | Severity | Anatomy Location | Code Location |
|---|---|---|---|---|
| `PromptTemplate` class in `prompt.py` | Class does not exist. Module has a constant `SYSTEM_PROMPT_TEMPLATE` and function `render_system_prompt()` [Pattern B] | error | Line 243 | `orchestration/prompt.py` |
| `assemble_prompt(scenario_context: dict) -> list[dict]` | Actual: `render_system_prompt(scenario_context: str) -> str` — different name, param type (`str` not `dict`), return type (`str` not `list[dict]`) [Pattern C] | error | Line 244 | `orchestration/prompt.py:208` |
| `SUPPORTED_FAMILIES: list[str]` and `SUPPORTED_PATTERNS: list[str]` as named constants | Inline string literals within `SYSTEM_PROMPT_TEMPLATE`, not standalone variables [Pattern C] | warning | Lines 245-246 | `orchestration/prompt.py` |
| `SandboxExecutor` class with `execute(script, sdk_module) -> DeclarationStore` | Class does not exist. Actual function: `execute_in_sandbox(source_code, timeout_seconds, sandbox_namespace) -> SandboxResult` [Pattern B] | error | Lines 252-253 | `orchestration/sandbox.py:236` |
| `SandboxConfig` dataclass with `timeout_seconds` and `isolation_level` | Does not exist. Timeout is a plain `int` parameter [Pattern B] | error | Line 255 | — |
| `orchestrate() -> DeclarationStore \| SkipResult` | Actual: `orchestrate() -> (pd.DataFrame, dict, dict) \| SkipResult` — returns 3-tuple, not `DeclarationStore` | error | Line 262 | `orchestration/retry_loop.py:70-74` |
| `_extract_script(llm_response) -> str` in `retry_loop.py` | Does not exist in retry_loop.py. Equivalent: `extract_clean_code(raw_response: str) -> str` in `code_validator.py` [Patterns B + C] | error | Line 263 | `orchestration/code_validator.py:76` |
| `_format_error_feedback(script, exception) -> str` in `retry_loop.py` | Actual: `format_error_feedback(original_code, exception, traceback_str) -> str` — public function in `sandbox.py`, not `retry_loop.py`, with 3 params not 2 [Patterns B + C] | error | Line 264 | `orchestration/sandbox.py:473` |

---

## 6. Module 4: Schema Metadata (`phase_2/metadata/`)

| Anatomy Claim | Actual Code | Severity | Anatomy Location | Code Location |
|---|---|---|---|---|
| `build_schema_metadata(store) -> dict` takes `store` object | Actual takes unpacked registries: `build_schema_metadata(groups, orthogonal_pairs, target_rows, measure_dag_order, columns, group_dependencies, patterns)` [Pattern A] | warning | Line 440 | `metadata/builder.py:23-31` |
| Post-build `_assert_metadata_consistency()` raises `ValueError` | Actual implementation only logs `logger.warning()`, never raises | warning | Line 448 | `metadata/builder.py:194` |

Module 4 has the smallest drift. The 7-key output structure matches the anatomy exactly.

---

## 7. Module 5: Validation Engine (`phase_2/validation/`)

| Anatomy Claim | Actual Code | Severity | Anatomy Location | Code Location |
|---|---|---|---|---|
| `SchemaAwareValidator.validate(df, meta) -> ValidationReport` | Actual: `SchemaAwareValidator(meta).validate(df, patterns=None)` — `meta` is a constructor arg, `patterns` is the second arg to `validate()` | error | Line 467 | `validation/validator.py` |
| `check_cardinality(df, meta)` | Actual: `check_categorical_cardinality(df, meta)` [Pattern C] | error | Line 475 | `validation/structural.py:52` |
| `check_dag_acyclicity(meta)` | Actual: `check_measure_dag_acyclic(meta)` [Pattern C] | error | Line 479 | `validation/structural.py:181` |
| `check_stochastic_ks(df, meta)` — 2 params | Actual: `check_stochastic_ks(df, col_name, meta, patterns)` — 4 params | error | Line 485 | `validation/statistical.py` |
| `check_structural_residuals(df, meta, pattern_mask=None)` | Actual: `check_structural_residuals(df, col_name, meta, patterns)` — no `pattern_mask`, has `col_name` and `patterns` [Pattern D] | error | Line 486 | `validation/statistical.py` |
| `_iter_predictor_cells(col_meta, meta)` — 2 params | Actual: `_iter_predictor_cells(df, col_name, col_meta, columns_meta, min_rows=5, max_cells=100)` — 6 params | warning | Line 488 | `validation/statistical.py` |
| `check_patterns(df, meta) -> list[Check]` dispatcher in `pattern_checks.py` | Function does not exist. Dispatch is in `validator.py`'s `_run_l3()` method [Pattern B] | error | Line 494 | `validation/validator.py` |
| `check_outlier_entity(df, pattern, meta)` — 3 params | Actual: `check_outlier_entity(df, pattern)` — 2 params | warning | Line 495 | `validation/pattern_checks.py` |
| `AUTO_FIX: dict[str, Callable]` dispatch table in `autofix.py` | No such named dict. Strategies are standalone functions (`widen_variance`, `amplify_magnitude`, `reshuffle_pair`); dispatch is parameter-driven via `match_strategy()` using `fnmatch` [Pattern D] | error | Lines 507-510 | `validation/autofix.py` |
| `ParameterOverrides` is a `Dict-like structure` | Actual: plain `dict` with nested keys, not a custom class | warning | Line 511 | `validation/autofix.py` |

---

## 8. Summary Counts

| Module | Errors | Warnings | Total |
|---|---|---|---|
| Shared infra | 0 | 4 | 4 |
| M1: SDK Surface | 4 | 0 | 4 |
| M2: Generation Engine | 8 | 5 | 13 |
| M3: LLM Orchestration | 8 | 1 | 9 |
| M4: Schema Metadata | 0 | 2 | 2 |
| M5: Validation Engine | 7 | 3 | 10 |
| **Total** | **27** | **15** | **42** |

M2 and M3 have the highest drift counts. M4 is nearly aligned.

---

## 9. Recommendations

1. **Keep this drift document as the canonical record.** The anatomy summary retains value as a conceptual design document showing the original spec intent. Rewriting it to match the implementation would destroy that history.

2. **Add a disclaimer header to stage5_anatomy_summary.md** stating it reflects the original spec design and linking to this document for implementation-accurate details.

3. **Treat the SVG flow diagram guides as the implementation-accurate reference.** The audit confirmed they overwhelmingly document the actual code correctly (with minor issues documented separately in the per-module audit findings).

---

## 10. Reconciliation Log

| Date | Scope | Notes |
|------|-------|-------|
| 2026-04-15 | Initial drift snapshot | This report. Compared anatomy claim vs. implementation across 5 modules; identified 42 drift items. |
| 2026-04-22 | Round-3 API surface | `scale=None` removed from `add_measure` signature and `ColumnDescriptor` field list — see `../fixes/GPT_FAILURE_ROUND_3_FIXES.md` and `stage5_anatomy_summary.md` reconciliation log. (This drift report itself is a 2026-04-15 snapshot; it does *not* reflect this change.) |
| 2026-05-07 | Stub workflow shipped | All 9 documented Phase 2 stubs (IS-1..IS-4, IS-6 token half, DS-1..DS-4) shipped between 2026-04-22 and 2026-05-07. Adversarial audit (`../POST_STUB_AUDIT_FINDINGS.md`: H1, M1–M5, L1–L5) closed in commits `6f64495`, `893e7e9`, `72ddb0f`, `2dbec22`. The "anatomy-claim" entries in §1–§7 above that referenced stubs (e.g. mixture sampling, four pattern injectors, censoring, multi-column `on`, dominance/convergence/seasonal validators) describe the pre-resolution state and are now stale; current state is in `stage5_anatomy_summary.md §3` (module descriptions) and `../remaining_gaps.md §4`. Per-stub records: `../stub_implementation/`. This drift report itself is preserved as a historical snapshot. |
