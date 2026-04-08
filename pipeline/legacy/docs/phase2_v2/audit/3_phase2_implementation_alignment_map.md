# Phase 2 — Implementation Alignment Map

Cross-references every atomic subtask (Stage 1) against every finding (Stage 2 + Addendum).

**Patch version:** v4 — Orchestrator Cross-Ref (2026-03-25)

**Legend:**
- **SPEC_READY** — Sufficient detail to implement and test. No gaps.
- **NEEDS_CLARIFICATION** — Ambiguous but not contradictory. Proceed with documented assumption.
- **BLOCKED** — CRITICAL gap prevents correct implementation.
- **SPEC_INCORRECT** — Internal contradiction between spec sections. Carries equal planning weight to BLOCKED — implementation cannot proceed correctly until the contradiction is resolved.

---

### Existing Core Infrastructure Assumptions (v3)

The following capabilities are **already implemented** in the codebase and must be reused — not reimplemented — by Phase 2 modules:

| Module | Provides | Consumed by |
|--------|----------|-------------|
| `pipeline/core/llm_client.py` — `LLMClient` | Multi-provider parameter adaptation (`adapt_parameters()`, `ProviderCapabilities`); JSON response parsing (`generate_json()`); Python code generation with automatic fence stripping (`generate_code()`); provider auto-detection and model-specific overrides (`MODEL_OVERRIDES`). | Module 7 (sandbox executor calls `generate_code()`), Module 10 (prompt integration uses `generate_code()`/`generate_json()`). |
| `pipeline/core/utils.py` | `META_CATEGORIES` (30-category taxonomy list); `get_category_by_id()` for category→label lookup; `generate_unique_id()` for generation tracking IDs. | Pipeline orchestrator (category routing, generation ID assignment). These are **orchestration helpers only** — they do not participate in Phase 2 SDK semantics or FactTableSimulator logic. |

**Implications for Module 7, 10, and 11:**

- **Code extraction (10.2.1):** `LLMClient.generate_code()` already strips markdown fences (```` ```python...``` ````). Subtask 10.2.1 becomes an **integration verification** task, not a from-scratch implementation.
- **Provider compatibility:** JSON mode negotiation, temperature clamping, and token parameter naming are handled by `ParameterAdapter`. Phase 2 code must not re-implement these.
- **Sandbox execution (7.1.1):** `LLMClient` is responsible for LLM request/response plumbing; the sandbox executor (`SandboxExecutor`) is responsible for `exec()` security policy and timeout. These are separate concerns.
- **Scenario injection (10.1.2):** A working JSON injection path already exists (`json.dumps(scenario, indent=2)` → `run_with_retries()`). The D1 blocker applies to the **typed contract formalization**, not to the basic injection capability.

---

### Module 1: `FactTableSimulator` Core SDK Class (§2.1, §2.8)

#### 1.1 Class Skeleton & Constructor

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 1.1.1 | `__init__(target_rows, seed)` constructor | SPEC_READY | — | Spec provides signature and example. |
| 1.1.2 | Internal registry data structures | SPEC_READY | — | Design-time decision; shape is implied by the full set of `add_*` methods. |

#### 1.2 `add_category()`

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 1.2.1 | Signature & parameter validation | NEEDS_CLARIFICATION | A9 | Assume `len(values) >= 2` required. Single-value categoricals cause degenerate chi-squared; spec says "rejects empty" but is silent on single-value. |
| 1.2.2 | Weight auto-normalization | SPEC_READY | — | "Auto-normalized" is explicit. |
| 1.2.3 | Per-parent conditional weights (dict form) | NEEDS_CLARIFICATION | A6 | Assume all parent values MUST be present as keys; missing keys raise `ValueError`. Spec shows ellipsis `...` but never states completeness requirement. |
| 1.2.4 | Parent existence & same-group validation | SPEC_READY | — | "validates parent exists in same group" is explicit. |
| 1.2.5 | Group registry update | SPEC_READY | — | Group semantics in §2.2 are clear. |
| 1.2.6 | Reject duplicate group root | SPEC_READY | — | "Each group has a root column (no parent)" is unambiguous. |

#### 1.3 `add_temporal()`

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 1.3.1 | Signature & date parsing | NEEDS_CLARIFICATION | — | ISO-8601 parsing is clear from the example (SPEC_READY). However, the range validation rule (`end > start`) is inferred from common sense, not explicitly stated — this portion is NEEDS_CLARIFICATION. Assume: `end <= start` raises `ValueError`. |
| 1.3.2 | Frequency validation | NEEDS_CLARIFICATION | B1 | Spec does not define a frequency whitelist — only `"daily"` is demonstrated. Sampling semantics for non-daily freqs are undefined. Assume: accept any freq string at declaration time; only `"daily"` is supported by the generation engine. |
| 1.3.3 | Derive whitelist validation | SPEC_READY | — | Whitelist `{day_of_week, month, quarter, is_weekend}` is explicit in §2.1.1. |
| 1.3.4 | Temporal group registration | NEEDS_CLARIFICATION | A10 | Assume group auto-named `"time"`; only one `add_temporal` call permitted; `"time"` reserved. Spec never states these rules explicitly. |

#### 1.4 `add_measure()` (Stochastic Root)

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 1.4.1 | Signature & family validation | NEEDS_CLARIFICATION | A2 | `scale` parameter is accepted but has no defined semantics. Assume: store it; ignore it in generation until spec clarifies. Log a warning if non-None. |
| 1.4.2 | `param_model` constant-parameter form | NEEDS_CLARIFICATION | A5 | Spec only shows `mu`/`sigma` examples. Assume: for `gaussian` and `lognormal` accept `mu`/`sigma`; for other families, define a canonical mapping (see A5 recommendation). Must document assumed key names. |
| 1.4.3 | `param_model` intercept+effects form | BLOCKED | A5, A5a | Cannot validate param_model keys without knowing which keys each family requires. Cannot guard against negative computed sigma without defined parameter domains. The additive model `θ = β₀ + Σβₘ` can produce invalid values (σ < 0) with no specified link function or domain check. |
| 1.4.4 | Mixture family sub-spec | BLOCKED | A1 | Zero specification: no param_model schema, no component structure, no mixing weights format. Cannot implement parsing, storage, or validation. |
| 1.4.5 | Register as DAG root node | SPEC_READY | — | DAG root semantics are clear from §2.3 table. |

#### 1.5 `add_measure_structural()` (Derived)

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 1.5.1 | Signature validation | SPEC_READY | — | Signature is explicit. |
| 1.5.2 | Formula symbol resolution & DAG edge creation | BLOCKED | A3 | No grammar defined for formula DSL. Cannot implement a safe expression evaluator without knowing allowed operators, precedence, function calls, or variable resolution rules. |
| 1.5.3 | Effects dictionary validation | SPEC_READY | — | §2.7 `UndefinedEffectError` example explicitly requires full coverage of effect keys against declared categorical values. The one-shot example fully illustrates the schema; validation rules are spec-backed. |
| 1.5.4 | Noise spec validation | BLOCKED | A5, A1a | Noise accepts a `family` key, but required params per family are unspecified (A5). Mixture noise is unguarded (A1a). Cannot validate `noise={"family": "gamma", ...}` without knowing required keys for gamma. |
| 1.5.5 | Cycle detection on measure DAG | SPEC_READY | — | "Must form a DAG" + topological sort are well-defined. |

#### 1.6 `declare_orthogonal()`

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 1.6.1 | Signature & group existence validation | SPEC_READY | — | Semantics are explicit. |
| 1.6.2 | Store orthogonal pair | SPEC_READY | — | Clear from §2.2. |
| 1.6.3 | Conflict check with `add_group_dependency` | NEEDS_CLARIFICATION | — | Mutual exclusivity is inferred from §2.2 structure ("independent OR dependent") but never explicitly stated as a validation rule. Assume: declaring a group pair as both orthogonal and dependent raises `ValueError`. |

#### 1.7 `add_group_dependency()`

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 1.7.1 | Signature & root-only constraint | SPEC_READY | — | Root-only constraint is explicit in §2.1.2 and §2.2. |
| 1.7.2 | Conditional weights validation | NEEDS_CLARIFICATION | A7 | Assume `on` is restricted to a single column (all examples show single-column `on`). Multi-column `on` has undefined weights schema. Treat `on: list[str]` as single-element list; raise if `len(on) > 1` until spec clarifies. |
| 1.7.3 | Root-level DAG acyclicity check | SPEC_READY | — | DAG constraint is explicit. |
| 1.7.4 | Conflict check with orthogonal | NEEDS_CLARIFICATION | — | Symmetric with 1.6.3. Mutual exclusion is inferred from semantics, not explicitly stated. Assume: adding dependency between groups already declared orthogonal raises `ValueError`. |

#### 1.8 `inject_pattern()`

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 1.8.1 | Signature & type validation | SPEC_READY | — | Type whitelist is explicit. |
| 1.8.2 | Target expression validation | NEEDS_CLARIFICATION | A3 | Target uses pandas query syntax; spec shows examples but no grammar. Assume: store target string as-is at declaration time; delegate to `df.query()` at runtime. No declaration-time parsing or column validation — the spec defines no target grammar. |
| 1.8.3 | Column validation | NEEDS_CLARIFICATION | — | The spec examples only show measure columns as the `col` argument, and the semantics (shifting distributions, computing z-scores) only make sense for measures. However, the restriction to measure columns is not explicitly stated in the `inject_pattern` API description. Assume: `col` must reference a declared measure column. |
| 1.8.4 | Pattern-type-specific param validation | BLOCKED | A8 | Only `outlier_entity` (`z_score`) and `trend_break` (`break_point`, `magnitude`) have specified params. For `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly` — zero param schema. Cannot validate what is not defined. |
| 1.8.5 | Store pattern | SPEC_READY | — | Append to list; trivial. |

#### 1.9 `set_realism()`

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 1.9.1 | Signature & validation | NEEDS_CLARIFICATION | A4 | `missing_rate` and `dirty_rate` are clear (floats in [0,1]). `censoring` has no schema — assume: accept and store any dict; defer interpretation to Phase δ engine. Log warning that censoring semantics are unspecified. |

---

### Module 2: Dimension Group Model (§2.2)

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 2.1.1 | Define `DimensionGroup` data class | SPEC_READY | — | Fields are fully inferrable from §2.2. |
| 2.2.1 | `OrthogonalPair` data class | SPEC_READY | — | Straightforward from §2.2. |
| 2.2.2 | `GroupDependency` data class | SPEC_READY | — | Fields explicit in §2.1.2 signature. |

---

### Module 3: DAG Construction & Topological Sort (§2.4, §2.3)

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 3.1.1 | `_build_full_dag()` — merge all column types | NEEDS_CLARIFICATION | B4, B5 | Spec shows one example but no general edge-construction algorithm. Assume 5 edge rules: (1) parent→child in groups, (2) on→child_root for group deps, (3) temporal_root→derived, (4) predictor_col→stochastic_measure for each effects key, (5) upstream_measure→structural_measure for formula refs + effect_col→structural_measure for each resolved effect. Temporal predictor edges (B5) included under rule 4. |
| 3.1.2 | `topological_sort()` | NEEDS_CLARIFICATION | — | Standard algorithm; cycle → `CyclicDependencyError`. However, topological sort is not unique — when multiple columns have no ordering constraint, tie-breaking determines RNG consumption order. The spec claims "bit-for-bit reproducible" (§2.8) but defines no canonical tie-breaking rule. Assume: lexicographic tie-breaking on column name. |
| 3.2.1 | Extract measure-only sub-DAG | SPEC_READY | — | Filter full DAG to measure nodes; well-defined. |

---

### Module 4: Deterministic Engine — `generate()` (§2.8)

#### 4.1 Phase α — Skeleton Builder

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 4.1.1 | Sample independent categorical roots | NEEDS_CLARIFICATION | — | `Cat(weights)` sampling is clear for declared-orthogonal or single-group scenarios. However, when two groups have neither `declare_orthogonal()` nor `add_group_dependency()`, the spec does not define whether their roots are sampled independently or jointly. §2.2 states cross-group independence is "opt-in, not default" but never specifies the default behavior. Assume: undeclared pairs default to independent sampling. |
| 4.1.2 | Sample cross-group dependent roots | NEEDS_CLARIFICATION | — | Conditional weights per-row for single-column `on` is clear from §2.4 Step 1 line 4 (SPEC_READY). However, the multi-column `on` case (e.g., `on=["severity", "age_group"]`) has no defined weights schema — the spec only shows single-column conditioning. Assume: reject `len(on) > 1` at execution time until spec clarifies. |
| 4.1.3 | Sample within-group child categories | SPEC_READY | — | Per-parent or flat weights; thoroughly specified in §2.1.1 with worked examples and §2.4 Step 1 line 5. |
| 4.1.4 | Sample temporal root | NEEDS_CLARIFICATION | B1 | Only `freq="daily"` has defined sampling (uniform dates). Assume: `weekly` = uniform over Monday dates; `monthly` = uniform over 1st-of-month dates. Document assumption. |
| 4.1.5 | Derive temporal children | NEEDS_CLARIFICATION | A11 | Derivation logic (`DOW`, `MONTH`, etc.) is clear, but the derived columns' value sets are not explicitly stated. Assume: `day_of_week` → 0–6, `month` → 1–12, `quarter` → 1–4, `is_weekend` → bool. These implicit types determine whether temporal derivations can appear as effects in `param_model`. |

#### 4.2 Phase β — Measure Generation

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 4.2.1 | `_sample_stochastic()` — stochastic root measure | BLOCKED | A5, A5a | Cannot implement sampling dispatch for 6 of 8 families without knowing their parameter names. The intercept+effects computation can produce invalid domains (e.g., sigma < 0) with no link function or clamping rule. For `gaussian` and `lognormal` the examples are sufficient; for all others, blocked. |
| 4.2.2 | Distribution dispatch table | BLOCKED | A5, A1 | Requires knowing (family → numpy/scipy method → parameter mapping) for all 8 families. Only 2 are exemplified. `mixture` has no sampling algorithm. |
| 4.2.3 | `_eval_structural()` — structural derived measure | BLOCKED | A3 | Depends on `eval_formula()` which requires a formula DSL grammar. |
| 4.2.4 | `eval_formula()` safe expression evaluator | BLOCKED | A3 | No operator whitelist, no precedence rules, no variable resolution order. Cannot build a parser. |

#### 4.3 Phase γ — Pattern Injection

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 4.3.1 | Outlier entity injection | NEEDS_CLARIFICATION | B2 | Injection algorithm is inferrable from L3 check (shift subset mean to z_score × global_std). But post-injection data will fail L2 KS tests for the same column. Assume: implement injection as specified; L2/γ conflict is a validation-layer issue (B2), not an engine issue. |
| 4.3.2 | Trend break injection | NEEDS_CLARIFICATION | B2 | Same L2 conflict as 4.3.1. Injection mechanic is inferrable: scale values after `break_point` by `(1 + magnitude)`. |
| 4.3.3 | Ranking reversal injection | BLOCKED | B6, A8 | No injection algorithm. No params schema (`metrics` key is only implied by L3 code, never declared in API). Cannot implement. |
| 4.3.4 | Dominance shift injection | BLOCKED | B6, A8 | No injection algorithm, no params schema, no definition of "dominance." |
| 4.3.5 | Convergence injection | BLOCKED | B6, A8 | No injection algorithm, no params schema, no convergence definition. |
| 4.3.6 | Seasonal anomaly injection | BLOCKED | B6, A8 | No injection algorithm, no params schema, no season specification. |

#### 4.4 Phase δ — Realism Injection

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 4.4.1 | Missing value injection | NEEDS_CLARIFICATION | C6 | Injection itself is clear (set NaN at `missing_rate`). But injected NaNs will fail L1 `finite_*` checks. Assume: implement as specified; validator must be adjusted (C6 is a validator issue). |
| 4.4.2 | Dirty value injection | NEEDS_CLARIFICATION | — | Spec says "dirty_rate" but doesn't define dirty-value generation strategy (typos? case changes? truncation?). Assume: randomly perturb categorical values via character-level edits (swap, delete, insert). |
| 4.4.3 | Censoring injection | BLOCKED | A4 | No schema for `censoring`: no direction (left/right), no thresholds, no target columns, no indicator column semantics. |

#### 4.5 Post-Processing

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 4.5.1 | DataFrame assembly & dtype casting | NEEDS_CLARIFICATION | — | The spec does not prescribe specific pandas dtypes (e.g., whether categoricals should use `pd.CategoricalDtype`, whether temporals should be `datetime64[ns]` vs. `datetime64[s]`). Dtype policy is an implementation design choice. Assume: use sensible defaults (string-typed categoricals, datetime-compatible temporals, float64 measures). |

---

### Module 5: Schema Metadata Builder (§2.6)

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 5.1.1 | Emit `dimension_groups` block | SPEC_READY | — | Structure shown in §2.6 example. |
| 5.1.2 | Emit `orthogonal_groups` block | SPEC_READY | — | Structure shown in §2.6 example. |
| 5.1.3 | Emit `group_dependencies` block | SPEC_INCORRECT | C3, C9 | §2.6 example omits `conditional_weights` from group_dependencies, but §2.9 L2 code (line 636) reads `dep["conditional_weights"]`. Metadata is incomplete relative to validator's expectations. Must emit `conditional_weights` in metadata to avoid L2 `KeyError`. |
| 5.1.4 | Emit `columns` block | SPEC_INCORRECT | C3, C8, C9, C3a, A2a | §2.6 example omits fields the validator reads: `values`/`weights` for categoricals (L1 line 575), `formula`/`noise_sigma` for structural measures (L2 lines 626–631), `param_model` for stochastic measures (L2 `_get_measure_spec`), per-parent `conditional_weights` for child categoricals (needed by Phase 3 for drill-down), and `scale` for stochastic measures (needed by L2 KS test adjustment and Phase 3). The metadata schema as written is internally inconsistent with the validator pseudocode. |
| 5.1.5 | Emit `measure_dag_order` | SPEC_READY | — | Topological sort output; clear. |
| 5.1.6 | Emit `patterns` block | SPEC_INCORRECT | C3 | §2.6 example omits pattern `params` (e.g., `z_score`, `magnitude`), but L3 code reads `p["col"]`, `p["target"]`, `p["metrics"]`, `p["break_point"]`. Validator will `KeyError` without them. |
| 5.1.7 | Emit `total_rows` | SPEC_READY | — | Trivial. |

---

### Module 6: Custom Exception Hierarchy (§2.7)

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 6.1.1 | `CyclicDependencyError` | SPEC_READY | — | Example message provided in §2.7. |
| 6.1.2 | `UndefinedEffectError` | SPEC_READY | — | Example message provided. |
| 6.1.3 | `NonRootDependencyError` | SPEC_READY | — | Example message provided. |
| 6.1.4 | Additional validation errors | NEEDS_CLARIFICATION | A5a | "Degenerate distributions" mentioned but not enumerated. Assume: add `InvalidParameterError` for computed params outside domain (σ < 0, shape < 0, etc.). Covers the A5a addendum finding. |

---

### Module 7: Execution-Error Feedback Loop (§2.7)

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 7.1.1 | Execute LLM script in sandbox | NEEDS_CLARIFICATION | — | Execute + catch exception pattern is standard; §2.7 steps are clear for the execution flow. However, the spec defines no sandbox security policy — no import whitelist, no resource limits, no timeout. Assume: implement basic execution with exception capture; defer security hardening until spec defines the policy. **Infrastructure note (v3):** LLM request/response plumbing (provider adaptation, fence stripping) is delegated to `LLMClient`; this subtask covers only `exec()` namespace, timeout, and error capture — not LLM call mechanics. |
| 7.1.2 | Format error feedback for LLM | SPEC_READY | — | "Code + traceback fed back to LLM" is sufficient to implement. §2.7 step 5 describes the four-component payload. |
| 7.1.3 | Retry loop with max_retries=3 | NEEDS_CLARIFICATION | C5 | §2.7 retry loop is for execution errors (SDK exceptions). Spec does not explicitly state this loop is *separate from and upstream of* the §2.9 validation loop. Assume: sequential composition — §2.7 retries until code executes, then §2.9 retries for statistical quality. Not nested. |

---

### Module 8: Three-Layer Validator (§2.9)

#### 8.1 Validator Framework

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 8.1.1 | `Check` data class | SPEC_READY | — | Fields clear from pseudocode. |
| 8.1.2 | `ValidationReport` aggregator | SPEC_READY | — | `all_passed` and `failures` are clear. |
| 8.1.3 | `validate(df, meta)` orchestrator | NEEDS_CLARIFICATION | B2, C6 | The orchestrator calls L1 → L2 → L3 sequentially and combines checks. The call sequence itself is straightforward. However, its correct behavior depends on unresolved upstream issues: (a) whether L2 runs on pre- or post-injection data (B2), and (b) whether L1 finiteness checks are adjusted for realism injection (C6). Assume: call all three layers on the final DataFrame; handle L2/pattern and L1/realism conflicts via the documented assumptions in those subtasks. |

#### 8.2 L1: Structural Validation

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 8.2.1 | Row count check | SPEC_READY | — | `abs(len(df) - target) / target < 0.1`; explicit. |
| 8.2.2 | Categorical cardinality check | SPEC_READY | — | `nunique() == cardinality`; explicit. |
| 8.2.3 | Root marginal weights check | SPEC_INCORRECT | C9 | Code reads `col["values"]` and `col["weights"]` which do not exist in §2.6 metadata. Implementation must *extend* metadata (fix 5.1.4 first) or this check raises `KeyError`. |
| 8.2.4 | Measure finite/non-null check | SPEC_INCORRECT | C6 | Check requires `notna().all()` but Phase δ realism injection introduces NaN at `missing_rate`. When realism is active, this check always fails. No conditional logic or adjusted threshold is specified. |
| 8.2.5 | Orthogonal independence (chi-squared) | SPEC_READY | — | Pseudocode is complete and correct. |
| 8.2.6 | Measure DAG acyclicity re-check | SPEC_READY | — | Pseudocode is explicit and complete; defense-in-depth check with straightforward implementation. |

#### 8.3 L2: Statistical Validation

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 8.3.1 | KS test per predictor cell | BLOCKED | A1b, C2, B2, A5, A2a | Multiple compounding issues: (1) `scipy.stats.kstest` cannot accept `"mixture"` — no scipy CDF exists (A1b). (2) No minimum sample size guard — cells with <30 rows produce unreliable tests (C2). (3) Pattern injection distorts the distribution post-generation, causing KS failures on pattern-target columns (B2). (4) The SDK-to-scipy family name mapping (`"gaussian"` → `"norm"`, `"lognormal"` → `"lognorm"`) is unstated (A5). (5) If `scale` is used, KS test compares scaled data against unscaled declared parameters — always fails (A2a). Any one of these blocks a correct implementation; together they are compounding. |
| 8.3.2 | `iter_predictor_cells()` helper | BLOCKED | C7, A5 | Method is referenced but never defined. The algorithm for computing the cross-product of effect predictor values and constructing concrete parameters per cell is non-trivial and unspecified. Also depends on knowing parameter keys per family (A5). |
| 8.3.3 | Structural residual mean check | SPEC_INCORRECT | C8 | Code reads `col["formula"]` which is absent from §2.6 structural measure metadata. `KeyError` at runtime. |
| 8.3.4 | Structural residual std check | SPEC_INCORRECT | C8 | Code reads `col["noise_sigma"]` which is absent from §2.6 metadata. `KeyError` at runtime. |
| 8.3.5 | `eval_formula()` for L2 residuals | BLOCKED | A3 | Same formula DSL gap as 4.2.4. Shared implementation, shared blocker. |
| 8.3.6 | Group dep conditional deviation | SPEC_INCORRECT | C3 | Code reads `dep["conditional_weights"]` which is absent from §2.6 `group_dependencies` example. `KeyError` at runtime. |
| 8.3.7 | `_max_conditional_deviation()` | SPEC_READY | — | Algorithm is inferrable: max absolute difference across all cells between observed and declared weights. |

#### 8.4 L3: Pattern Validation

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 8.4.1 | Outlier entity z-score check | SPEC_READY | — | Pseudocode is complete: `z >= 2.0`. |
| 8.4.2 | Ranking reversal check | SPEC_INCORRECT | C11 | Hard-codes `list(meta["dimension_groups"].keys())[0]` as grouping axis. The "first" group is arbitrary (insertion order). No `group_by` param in pattern spec. Result: reversal may be checked on wrong dimension. |
| 8.4.3 | Trend break magnitude check | SPEC_READY | — | Pseudocode is complete: `abs(after-before)/before > 0.15`. |
| 8.4.4 | Dominance shift check | BLOCKED | C10, B6, A8 | Delegates to `_verify_dominance_change` which is never defined. No params schema, no injection algorithm, no validation logic. |
| 8.4.5 | `_verify_dominance_change()` | BLOCKED | C10 | Black box — no definition anywhere in spec. |

**L3 missing branches:**

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| (8.4.6) | Convergence validation | BLOCKED | C1 | No L3 branch exists for `convergence` in the pseudocode. Pattern is injected but never validated. |
| (8.4.7) | Seasonal anomaly validation | BLOCKED | C1 | No L3 branch exists for `seasonal_anomaly`. Pattern is injected but never validated. |

---

### Module 9: Auto-Fix Loop (§2.9)

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 9.1.1 | `match_strategy()` glob matcher | SPEC_READY | — | Glob matching on check names; standard. |
| 9.2.1 | `widen_variance()` | NEEDS_CLARIFICATION | B7, B2/B3 | The strategy modifies a parameter, but `build_fn(seed=42+attempt)` re-runs the original script from scratch. Assume: fix strategies mutate the `FactTableSimulator` instance (not the script), and the retry loop calls `sim.generate()` directly instead of re-running `build_fn`. This contradicts the pseudocode but is the only way fixes can persist. **Dependency note:** Cannot be fully implemented or integration-tested until the auto-fix mutation model (B3) and L2/pattern conflict (B2) are resolved — the mutation target and the interaction with pattern-injected distributions are both undefined. |
| 9.2.2 | `amplify_magnitude()` | NEEDS_CLARIFICATION | B7, B3, B2/B3 | Same mutation-model ambiguity as 9.2.1. Additionally, amplifying outlier magnitude may worsen L2 KS failures on the same column. Assume: mutate pattern spec on the simulator instance. **Dependency note:** Same B2/B3 dependency as 9.2.1 — cannot be fully validated until mutation model and L2/pattern conflict are resolved. |
| 9.2.3 | `reshuffle_pair()` | NEEDS_CLARIFICATION | B3, B2/B3 | Reshuffling a column may destroy injected patterns whose `target` references that column. Assume: only reshuffle columns that are not referenced in any pattern `target` expression. **Dependency note:** Same B2/B3 dependency — reshuffling interacts with pattern injection semantics. |
| 9.3.1 | `generate_with_validation()` retry loop | SPEC_INCORRECT | B7, B3, C5 | The pseudocode calls `build_fn(seed=42+attempt)` after applying fix strategies, which discards all fixes. This is an internal contradiction: the fix strategies are applied (lines 695–698) but the next iteration regenerates from the original script (line 691). Additionally, composition with §2.7 loop is undefined (C5). |

---

### Module 10: LLM Code-Generation Prompt & Integration (§2.5)

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 10.1.1 | System prompt construction | SPEC_READY | — | Prompt template is provided verbatim in §2.5. |
| 10.1.2 | Scenario context injection | BLOCKED | D1 | No formal typed schema for the Phase 1 → Phase 2 scenario context. Required fields, types, and serialization format are not formally defined. The one-shot example shows *one* format but does not guarantee Phase 1 produces it. **Infrastructure note (v3):** A working JSON injection path already exists (`json.dumps(scenario, indent=2)` fed to `run_with_retries()` via `LLMClient.generate_code()`). The blocker applies to **typed contract formalization** (defining `ScenarioContext` as a typed dataclass with required/optional fields and versioning), not to the basic injection capability itself. |
| 10.2.1 | Extract Python code block | NEEDS_CLARIFICATION | — | The spec states output is "pure, valid Python" (§2.5 constraint 6), which implies no markdown fences. **Infrastructure note (v3):** `LLMClient.generate_code()` already performs defensive fence stripping (removes ```` ```python ````/```` ``` ```` markers). This subtask is an **integration verification / contract test** — confirm that `generate_code()` output is syntactically valid Python and contains the expected `build_fact_table` definition, not a from-scratch extraction implementation. |
| 10.2.2 | Validate code contains `generate()` | NEEDS_CLARIFICATION | A12 | Spec says "returning sim.generate()" but the return type (tuple vs. single value) is ambiguous between §2.5 and §2.8. Assume: `build_fact_table` returns whatever `sim.generate()` returns, which is `Tuple[DataFrame, dict]` per §2.8 type hint. |

---

### Module 11: End-to-End Pipeline Orchestrator (§2.7 + §2.8 + §2.9)

| Subtask | Description | Readiness | Finding(s) | Notes / Assumptions |
|---------|-------------|-----------|------------|---------------------|
| 11.1.1 | Full pipeline: prompt → execute → validate → return | BLOCKED | C5, D1 | Two compounding blockers: (1) Loop composition between §2.7 (execution errors) and §2.9 (validation auto-fix) is undefined — cannot wire the pipeline without knowing the nesting/sequencing relationship (C5). (2) Input contract from Phase 1 is undefined (D1). **Architecture ref (v4):** Orchestrator 架构（职责拆分、`GenerationResult` 返回模型、`Phase2Service` 封装）已在 `audit/5_agpds_pipeline_runner_redesign.md` 中定义；实现时参照该草案的 `AGPDSPipeline` 设计边界。 |
| 11.1.2 | Wire §2.7 loop with §2.9 loop | BLOCKED | C5 | Same as above. Are loops nested (max 9 attempts), sequential (max 6 attempts), or with escalation? Undefined. |

---
---

## Readiness Summary

| Module | Total Subtasks | SPEC_READY | NEEDS_CLARIFICATION | BLOCKED | SPEC_INCORRECT |
|--------|---------------|------------|---------------------|---------|----------------|
| 1.1 Constructor | 2 | 2 | 0 | 0 | 0 |
| 1.2 `add_category` | 6 | 4 | 2 | 0 | 0 |
| 1.3 `add_temporal` | 4 | 1 | 3 | 0 | 0 |
| 1.4 `add_measure` | 5 | 1 | 2 | 2 | 0 |
| 1.5 `add_measure_structural` | 5 | 3 | 0 | 2 | 0 |
| 1.6 `declare_orthogonal` | 3 | 2 | 1 | 0 | 0 |
| 1.7 `add_group_dependency` | 4 | 2 | 2 | 0 | 0 |
| 1.8 `inject_pattern` | 5 | 2 | 2 | 1 | 0 |
| 1.9 `set_realism` | 1 | 0 | 1 | 0 | 0 |
| 2. Dimension Group Model | 3 | 3 | 0 | 0 | 0 |
| 3. DAG Construction | 3 | 1 | 2 | 0 | 0 |
| 4.1 Skeleton Builder | 5 | 1 | 4 | 0 | 0 |
| 4.2 Measure Generation | 4 | 0 | 0 | 4 | 0 |
| 4.3 Pattern Injection | 6 | 0 | 2 | 4 | 0 |
| 4.4 Realism Injection | 3 | 0 | 2 | 1 | 0 |
| 4.5 Post-Processing | 1 | 0 | 1 | 0 | 0 |
| 5. Schema Metadata | 7 | 4 | 0 | 0 | 3 |
| 6. Exception Hierarchy | 4 | 3 | 1 | 0 | 0 |
| 7. Error Feedback Loop | 3 | 1 | 2 | 0 | 0 |
| 8.1 Validator Framework | 3 | 2 | 1 | 0 | 0 |
| 8.2 L1 Validation | 6 | 4 | 0 | 0 | 2 |
| 8.3 L2 Validation | 7 | 1 | 0 | 3 | 3 |
| 8.4 L3 Validation | 7 | 2 | 0 | 4 | 1 |
| 9. Auto-Fix Loop | 5 | 1 | 3 | 0 | 1† |
| 10. Prompt & Integration | 4 | 1 | 2 | 1 | 0 |
| 11. Pipeline Orchestrator | 2 | 0 | 0 | 2 | 0 |
| **TOTAL** | **108** | **41** | **33** | **24** | **10†** |

> †Note: Subtask 9.3.1 is counted as SPEC_INCORRECT (not BLOCKED) because the spec *provides* pseudocode but that pseudocode contains an internal contradiction (fixes applied then discarded on re-generation).

> **Planning note on SPEC_INCORRECT:** Items marked SPEC_INCORRECT carry equal planning weight to BLOCKED items. Both categories represent subtasks that cannot be correctly implemented as-is — BLOCKED items lack specification entirely, while SPEC_INCORRECT items have conflicting specifications. For sprint planning purposes, treat both as requiring upstream resolution before implementation can proceed. The distinction matters for *how* to resolve them (add missing spec vs. reconcile contradictory spec) but not for *whether* to resolve them before coding.

**Percentage breakdown:**
- **SPEC_READY: 38%** (41 subtasks) — can begin implementation immediately
- **NEEDS_CLARIFICATION: 31%** (33 subtasks) — can proceed with documented assumptions
- **BLOCKED: 22%** (24 subtasks) — cannot implement until spec gaps are resolved
- **SPEC_INCORRECT: 9%** (10 subtasks) — spec contains internal contradictions; must be corrected before implementation

---

## Critical Path Blockers (Ordered)

These are ordered by **dependency depth**: resolving blocker N unblocks subtasks that in turn unblock downstream modules. The `→` notation shows the unblock chain.

---

### 1. Schema Metadata Completeness (C3 + C8 + C9 + C3a + A2a)

**Blocks:** 5.1.3, 5.1.4, 5.1.6 → 8.2.3, 8.2.4, 8.3.1, 8.3.3, 8.3.4, 8.3.6 → 9.3.1 → 11.1.1
**Count:** 3 SPEC_INCORRECT + 6 downstream dependents = **9 subtasks** (plus additional indirect dependents)

The metadata schema is the single shared contract. The validator reads fields the metadata doesn't emit — including `values`/`weights` for categoricals, `formula`/`noise_sigma` for structural measures, `conditional_weights` for group dependencies, `param_model` for stochastic measures, per-parent conditional weights for child categoricals (C3a), and `scale` for stochastic measures (A2a). Fix the metadata schema *first* because every validator subtask and the entire auto-fix loop depend on it. Without this, there is no testable validator, and without a validator, the pipeline orchestrator cannot be wired.

**Resolution:** Define the complete metadata schema once; all dependent subtasks unblock simultaneously.

---

### 2. Formula DSL Grammar (A3)

**Blocks:** 1.5.2, 4.2.3, 4.2.4, 8.3.5
**Count:** 4 BLOCKED subtasks across 3 modules (SDK validation, engine generation, L2 validation)

The formula appears in `add_measure_structural` (declaration), `_eval_structural` (generation), and `eval_formula` in L2 (validation). All three share the same parser. Without a grammar, no parser can be built, and the entire structural-measure pipeline — from declaration to validation — is inoperable.

**Resolution:** Define operator whitelist + precedence + variable resolution rules. Unblocks the structural measure pipeline end-to-end.

---

### 3. Distribution Family Parameter Specification (A5 + A5a + A1 + A1b)

**Blocks:** 1.4.3, 1.4.4, 1.5.4, 4.2.1, 4.2.2, 8.3.1, 8.3.2
**Count:** 7 BLOCKED subtasks across 3 modules (SDK validation, engine sampling, L2 validation)

Without knowing parameter keys per family, the SDK cannot validate `param_model`, the engine cannot dispatch to the correct sampling function, and L2 cannot construct expected parameters. The `mixture` sub-problem (A1, A1b) adds: no schema, no sampling, and no KS test path.

**Resolution:** Create a family reference table (keys, domains, scipy mapping). Decide on `mixture`: fully specify or defer. Address A5a by requiring computed-parameter domain checks. Unblocks the entire stochastic-measure pipeline.

---

### 4. Pattern Type Full Specification (A8 + B6 + C1)

**Blocks:** 1.8.4, 4.3.3, 4.3.4, 4.3.5, 4.3.6, 8.4.4, 8.4.5, (8.4.6), (8.4.7)
**Count:** 9 BLOCKED subtasks across 3 modules (SDK validation, engine injection, L3 validation)

Four of six pattern types are name-only. Params, injection, and validation are all undefined. These must be co-designed as triples of (params_schema, injection_algorithm, validation_check) to ensure the injected statistical signature is detectable by the corresponding L3 test.

**Resolution:** For each of `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`: define the params schema, injection transformation, and L3 validation logic.

---

### 5. L2 vs. Pattern Injection Conflict + Auto-Fix Mutation Model (B2 + B3 + B7)

**Blocks (directly):** 9.3.1 (SPEC_INCORRECT)
**Degrades (indirectly):** 8.3.1, 9.2.1, 9.2.2, 9.2.3, 4.3.1, 4.3.2, 11.1.1, 11.1.2

This is not a *blocker* in the hard sense — the individual components can be built — but the composed system will oscillate: L2 fails because patterns distort distributions → auto-fix widens variance → pattern signal weakens → L3 fails → auto-fix amplifies pattern → L2 fails again. The auto-fix pseudocode also discards fixes on re-generation (B7). Note: 9.2.1–9.2.3 are flagged as dependent on B2/B3 resolution — their fix strategies cannot be integration-tested until the mutation model is defined.

**Resolution:** (a) Run L2 on pre-injection data or exclude pattern-target rows from KS tests. (b) Redefine the retry loop to mutate the simulator instance rather than re-running `build_fn`.

---

### 6. Phase 1 → Phase 2 Interface Contract (D1)

**Blocks:** 10.1.2, 11.1.1
**Count:** 2 BLOCKED subtasks + all downstream pipeline execution

Without a typed scenario context schema, the prompt template cannot be reliably populated for **stable, production-grade orchestration**. The pipeline orchestrator cannot reach a fully validated state.

**Current state (v3):** A working JSON injection path already exists — `agpds_pipeline.py` serializes the Phase 1 scenario via `json.dumps(scenario, indent=2)` and feeds it to Phase 2's `run_with_retries()`. The blocker applies to **typed interface completeness** (formally defining `ScenarioContext` as a typed dataclass with required/optional fields, validation, and versioning), not to the basic injection capability.

**Resolution:** Define `ScenarioContext` as a typed dataclass with required/optional fields, serialization format, and a versioning contract between phases. Existing `ScenarioContextualizer.validate_output()` in `pipeline/phase_1/scenario_contextualizer.py` already enforces a de facto field set (`scenario_title`, `data_context`, `key_entities`, `key_metrics`, `temporal_granularity`, `target_rows`) that can serve as the starting point for formalization. **Design ref (v4):** `ScenarioContext` 的归属位置与字段规划已在 `audit/5_agpds_pipeline_runner_redesign.md` 的 `result_models.py` 设计中给出，可作为 D1 解决路径的直接输入。

---

### 7. Censoring Schema (A4)

**Blocks:** 4.4.3
**Count:** 1 BLOCKED subtask

Isolated to the realism injection module. Lower priority since realism is optional (`censoring=None` default).

**Resolution:** Define the censoring dict schema (target column, direction, threshold).

---

### Dependency Graph of Blockers

```
Blocker 1 (Metadata Schema)
   └─→ unblocks Validator (L1, L2, L3) and Auto-Fix loop
        └─→ unblocks Pipeline Orchestrator (Module 11)

Blocker 2 (Formula DSL)
   └─→ unblocks Structural Measures (SDK + Engine + L2)
        └─→ feeds into Pipeline Orchestrator

Blocker 3 (Distribution Families)
   └─→ unblocks Stochastic Measures (SDK + Engine + L2)
        └─→ feeds into Pipeline Orchestrator

Blocker 4 (Pattern Types)
   └─→ unblocks Pattern Injection (Engine) + L3 Validation
        └─→ requires Blocker 5 (L2/Pattern conflict) to be co-resolved

Blocker 5 (L2/Pattern + Auto-Fix Model)
   └─→ requires Blocker 1 (metadata) + Blocker 4 (patterns) resolved first
        └─→ unblocks stable end-to-end validation
        └─→ unblocks integration testing of 9.2.1–9.2.3 fix strategies

Blocker 6 (Phase 1 Contract)
   └─→ unblocks Prompt Integration + Pipeline entry point

Blocker 7 (Censoring)
   └─→ isolated; resolve opportunistically
```

**Optimal resolution order:** 1 → 2 → 3 → 6 → 4 → 5 → 7

Resolve metadata (1), formula DSL (2), and distribution families (3) first — these are independent and together unblock 20 subtasks. Then resolve the Phase 1 contract (6) to enable pipeline integration. Then co-resolve pattern types (4) with the L2/auto-fix conflict (5), since the pattern injection/validation design directly determines how L2 must be adjusted and how 9.2.x fix strategies interact with patterns. Censoring (7) can be deferred.

---

## Patch Log (v4 — Orchestrator Cross-Ref)

| Finding ID | Change Type | Description |
|---|---|---|
| D.relabel_1.6.3_1.7.4 | DOWNGRADED | 1.6.3: SPEC_READY → NEEDS_CLARIFICATION. Mutual exclusion of orthogonal and dependent declarations is inferred from §2.2 semantics, not explicitly stated as a validation rule. |
| D.relabel_1.6.3_1.7.4 | DOWNGRADED | 1.7.4: SPEC_READY → NEEDS_CLARIFICATION. Symmetric with 1.6.3; same justification. |
| D.relabel_3.1.2 | DOWNGRADED | 3.1.2: SPEC_READY → NEEDS_CLARIFICATION. Topological sort stability is ambiguous — no canonical tie-breaking rule is specified, undermining the "bit-for-bit reproducible" claim. |
| D.relabel_4.1.1 | DOWNGRADED | 4.1.1: SPEC_READY → NEEDS_CLARIFICATION. Undeclared cross-group default behavior (when two groups have neither orthogonal nor dependency declaration) is undefined. |
| D.relabel_4.5.1 | DOWNGRADED | 4.5.1: SPEC_READY → NEEDS_CLARIFICATION. Dtype policy is an implementation design choice not specified by the spec. |
| D.relabel_7.1.1 | DOWNGRADED | 7.1.1: SPEC_READY → NEEDS_CLARIFICATION. Sandbox execution flow is clear but security policy (imports, resource limits, timeout) is unspecified. |
| D.relabel_8.1.3 | DOWNGRADED | 8.1.3: SPEC_READY → NEEDS_CLARIFICATION. Validator orchestrator depends on unresolved L2/pattern (B2) and L1/realism (C6) interactions. |
| D.relabel_10.2.1 | DOWNGRADED | 10.2.1: SPEC_READY → NEEDS_CLARIFICATION. Spec says "pure, valid Python" — fence extraction is a defensive implementation choice, not a spec requirement. |
| D.relabel_1.3.1 | DOWNGRADED (partial) | 1.3.1: SPEC_READY → NEEDS_CLARIFICATION. ISO parsing remains defensible (SPEC_READY), but range validation (`end > start`) is inferred, not stated. Overall label becomes NEEDS_CLARIFICATION. |
| D.relabel_1.8.3 | DOWNGRADED (partial) | 1.8.3: SPEC_READY → NEEDS_CLARIFICATION. Restriction to measure columns is strong inference from usage context but not explicitly stated in the API description. |
| D.relabel_4.1.2 | DOWNGRADED (partial) | 4.1.2: SPEC_READY → NEEDS_CLARIFICATION. Single-column `on` is clear (SPEC_READY), but multi-column `on` case has undefined weights schema. Overall label becomes NEEDS_CLARIFICATION. |
| D.relabel_1.5.3 | KEPT | 1.5.3: Confirmed SPEC_READY. §2.7 `UndefinedEffectError` example explicitly requires full coverage — GPT's downgrade rejected. |
| D.relabel_4.1.3 | KEPT | 4.1.3: Confirmed SPEC_READY. Within-group child sampling is thoroughly specified with worked examples — GPT's downgrade rejected. |
| D.relabel_8.2.6 | KEPT | 8.2.6: Confirmed SPEC_READY. Pseudocode is explicit and complete — GPT's downgrade rejected. |
| E.propagation_B2_B3 | ANNOTATED | 9.2.1, 9.2.2, 9.2.3: Added **Dependency note** flagging that these cannot be fully implemented or integration-tested until B2/B3 (L2/pattern conflict + mutation model) are resolved. |
| E.propagation_metadata | CLARIFIED | Added planning note in legend and summary: SPEC_INCORRECT carries equal planning weight to BLOCKED. Both require upstream resolution before correct implementation. |
| E.numerical | CORRECTED | Readiness Summary: recounted all subtask totals. Original claimed 111 total (50 SR + 22 NC + 25 BL + 11 SI); actual pre-patch count was 108 (52 SR + 22 NC + 24 BL + 10 SI). Per-module corrections: 1.5 was listed as 2 SR + 3 BL (should be 3 SR + 2 BL); Module 5 was listed as 3 SR + 4 SI (should be 4 SR + 3 SI); Module 9 total listed as 4 (should be 5). Post-patch totals reflect both corrected counts and applied readiness changes: 108 total (41 SR + 33 NC + 24 BL + 10 SI). Percentages recalculated to sum to 100%. |
| E.numerical | CORRECTED | Critical Path Blocker 1: subtask count updated from "4 SPEC_INCORRECT + 6 downstream = 10" to "3 SPEC_INCORRECT + 6 downstream = 9+" (Module 5 has 3 SI, not 4). |
| E.numerical | CORRECTED | Critical Path summary: unblock count updated from "21 subtasks" to "20 subtasks" to match corrected totals. |
| F.infra_section | ADDED (v3) | New "Existing Core Infrastructure Assumptions" section added after Legend. Declares `LLMClient` (code fence stripping, provider adaptation, JSON mode) and `utils.py` (category helpers, ID generation) as pre-existing, reusable capabilities. |
| F.10.2.1_reframe | MODIFIED (v3) | 10.2.1 description reframed from "defensive fence extraction" to "integration verification / contract test — confirm `LLMClient.generate_code()` output validity." Readiness unchanged (NEEDS_CLARIFICATION). |
| F.10.1.2_soften | MODIFIED (v3) | 10.1.2 (D1) description softened: blocker now applies to "typed contract formalization," not basic injection capability. Added note about existing `json.dumps(scenario)` injection path. Status unchanged (BLOCKED). |
| F.7.1.1_boundary | ANNOTATED (v3) | 7.1.1 notes clarified: LLM plumbing delegated to `LLMClient`; sandbox subtask covers only `exec()` namespace, timeout, and error capture. |
| F.blocker6_soften | MODIFIED (v3) | Blocker 6 description softened: blocker applies to typed interface completeness, not basic injection capability. Added reference to `ScenarioContextualizer.validate_output()` as de facto contract starting point. |
| G.blocker6_xref | ANNOTATED (v4) | Blocker 6 resolution 增加交叉引用至 `audit/5_agpds_pipeline_runner_redesign.md` 的 `ScenarioContext` / `result_models.py` 设计。 |
| G.module11_xref | ANNOTATED (v4) | Module 11 (11.1.1) 增加架构参考引用至 `audit/5` 的 orchestrator 设计（`AGPDSPipeline` 职责边界、`GenerationResult`、`Phase2Service`）。 |
