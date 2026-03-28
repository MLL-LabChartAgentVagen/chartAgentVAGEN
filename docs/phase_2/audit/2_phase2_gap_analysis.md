# Phase 2 Spec — Exhaustive Gap & Issue Analysis

**Document:** AGPDS Phase 2: Agentic Data Simulator (SDK-Driven), §2.1–§2.10
**Analysis date:** 2026-03-15
**Method:** Three independent expert reviewers, followed by unified synthesis.
**Patch version:** v2 — Post-Audit (2026-03-19)

---

## Reviewer A — SDK API Designer

Focus: API surface completeness, type safety, edge cases in method signatures, missing validation rules, ambiguous parameter semantics.

---

### Finding A1: `mixture` distribution family is name-only — zero specification

- **Severity:** CRITICAL
- **Spec location:** §2.1.1, supported distributions list (line 94); §2.5, prompt SUPPORTED DISTRIBUTIONS line
- **Issue:** The string `"mixture"` appears in the supported distributions list alongside seven fully-specified families, but nowhere in the spec is its `param_model` schema defined. A mixture distribution fundamentally differs from the other seven — it requires specifying component distributions, per-component parameters, and mixing weights. The current `param_model` schema (intercept + effects) cannot express this. There is no example, no parameter contract, and no validation rule.
- **Impact:** The LLM may emit `family="mixture"` in generated code. The SDK has no schema to validate or sample from it. This causes either a silent runtime crash (unimplemented dispatch) or requires implementers to invent an undocumented schema, creating divergence between spec and code.
- **Recommendation:** The spec should either (a) fully define the mixture `param_model` schema — e.g., `{"components": [{"family": "gaussian", "params": {"mu": ..., "sigma": ...}, "weight": 0.6}, ...]}` — with intercept+effects allowed inside each component, or (b) remove `"mixture"` from the supported list and defer it to a future version.

---

### Finding A2: `scale` parameter on `add_measure()` is undefined

- **Severity:** MODERATE
- **Spec location:** §2.1.1, `add_measure(name, family, param_model, scale=None)` signature (line 51); §2.5, prompt SDK reference (line 287)
- **Issue:** The `scale` parameter appears in both the method signature and the LLM prompt, but is never defined anywhere in the spec. There is no description, no example usage, no explanation of how `scale` interacts with `param_model`, and no indication of which distributions it applies to. Is it a post-sampling multiplier? A parameter override? A clipping bound?
- **Impact:** The LLM may pass a `scale` value that the engine has no defined way to interpret. Implementers must guess or ignore the parameter. Either path creates spec-code divergence.
- **Recommendation:** The spec should define `scale` explicitly — e.g., "a post-sampling affine transform `scale * sampled_value`, useful for unit conversion" — or remove it from the signature. If retained, specify its interaction with each distribution family and with the intercept+effects model.

---

### Finding A3: Formula DSL for `add_measure_structural()` is unspecified

- **Severity:** CRITICAL
- **Spec location:** §2.1.1, `add_measure_structural` description (lines 72–81); §2.3, Structural Measure section (lines 178–182)
- **Issue:** The `formula` parameter is a string containing an arithmetic expression (e.g., `"wait_minutes * 12 + severity_surcharge"`), but the spec defines no formal grammar. Specifically missing:
  - **Allowed operators:** Is `**` (power) allowed? `/` (division)? `%` (modulo)? Unary negation? Function calls like `log()`, `max()`, `abs()`?
  - **Precedence rules:** Standard mathematical? Python-like?
  - **Variable resolution order:** Are measure names resolved before effect names? What happens if a measure and an effect share a name?
  - **Literal numbers:** Can the formula contain numeric literals (e.g., `"12"`)? The examples suggest yes, but this is not stated.
  - **Whitespace / formatting rules:** Is `"wait_minutes*12"` equivalent to `"wait_minutes * 12"`?
- **Impact:** Without a grammar, the safe expression evaluator (§4.2.4 in the task hierarchy) cannot be implemented unambiguously. The LLM may generate formulas with constructs the evaluator rejects (e.g., `log(wait_minutes)` or `wait_minutes ** 2`). Silent parse failures corrupt data.
- **Recommendation:** The spec should provide a BNF-style grammar or at minimum an exhaustive operator whitelist. Suggested minimal set: `+`, `-`, `*`, `/`, unary `-`, numeric literals, parentheses. If mathematical functions are desired, enumerate them explicitly (e.g., `log`, `exp`, `abs`, `min`, `max`).

---

### Finding A4: `censoring` parameter in `set_realism()` is undefined — including cross-section impact on metadata and validation

- **Severity:** MODERATE
- **Spec location:** §2.1.2, `set_realism(missing_rate, dirty_rate, censoring)` (line 129); §2.8 code block (line 533); §2.6 metadata schema; §2.9 L1/L2 validators
- **Issue:** The `censoring` parameter appears in the method signature and in the engine pipeline (`δ` phase), but has no type annotation, no schema definition, no example, and no explanation of its semantics. Left vs. right censoring? Per-column thresholds? Indicator columns? None of this is specified.

  **Extended scope (post-audit):** Beyond the missing semantic definition, censoring has unaddressed cross-section effects on two downstream subsystems:
  1. **Metadata (§2.6):** The schema metadata has no field to record censoring configuration. Phase 3 cannot reconstruct which columns were censored, the direction, or the threshold — information needed for accurate QA generation (e.g., "Why does the cost distribution appear truncated?").
  2. **Validation (§2.9):** Censored values change the distributional shape of affected measure columns. L2 KS tests will fail for censored columns because the empirical distribution no longer matches the declared family. L1 finiteness checks may also interact with censoring if censored values are replaced with sentinels (e.g., `NaN` or a cap value). No validator adjustment for censoring is specified.

- **Impact:** Cannot implement `_inject_realism` censoring logic. The LLM prompt (§2.5) mentions `censoring=None` in the soft guidelines, so the LLM may attempt to use it with invented semantics. Even if implemented, the metadata and validator are blind to censoring effects.
- **Recommendation:** Define the schema — e.g., `censoring={"col_name": {"type": "right", "threshold": 500}}` — with at minimum: target column(s), censoring direction (left/right/interval), threshold value(s), and whether a censoring indicator column is added. Additionally: (a) add a `censoring` field to the §2.6 metadata schema recording the active configuration, and (b) specify L2 validation behavior for censored columns (e.g., exclude censored rows from KS tests, or skip L2 for censored columns).

---

### Finding A5: Required `param_model` keys per distribution family are unspecified

- **Severity:** CRITICAL
- **Spec location:** §2.1.1, `add_measure` (lines 51–70); §2.3, general formula (line 176)
- **Issue:** The spec shows `param_model` examples only for `lognormal` (keys: `mu`, `sigma`) and `gaussian` (keys: `mu`, `sigma`). For the remaining six families, the required parameter keys are never stated:
  - `gamma` — `shape`/`rate`? `alpha`/`beta`? `k`/`theta`?
  - `beta` — `alpha`/`beta`? `a`/`b`?
  - `uniform` — `low`/`high`?
  - `poisson` — `lambda`? `mu`?
  - `exponential` — `lambda`? `rate`? `scale`?
  - `mixture` — (entirely unspecified, see A1)
- **Impact:** The LLM has no guidance on which keys to use. The SDK validation layer cannot verify correctness. Implementers must choose a naming convention that may mismatch LLM-generated code.
- **Recommendation:** Add a distribution reference table specifying, for each family: required `param_model` keys, their domains (e.g., `sigma > 0`), and whether each key supports the intercept+effects form. Example: `| gamma | shape (>0), rate (>0) | Both support intercept+effects |`.

---

### Finding A6: Per-parent dict `weights` — incomplete parent key coverage is unspecified

- **Severity:** MODERATE
- **Spec location:** §2.1.1, per-parent conditional weights (lines 32–37)
- **Issue:** The spec shows `weights={"Xiehe": [...], "Huashan": [...], ...}` with an ellipsis. It does not state what happens if the dict omits some parent values. Must every parent value be present as a key? Can a partial dict be provided, with missing parents falling back to a default? If so, what is the default?
- **Impact:** The LLM may generate a per-parent dict that covers only some parents. The engine either crashes (KeyError), silently uses zero-vectors (degenerate sampling), or requires undefined fallback logic.
- **Recommendation:** The spec should state: "When `weights` is a dict, it MUST contain a key for every value in the parent column. Missing keys raise `ValueError`." Alternatively, define a `"_default"` fallback key.

---

### Finding A7: `add_group_dependency` with multiple `on` columns — conditional weights schema is ambiguous

- **Severity:** MODERATE
- **Spec location:** §2.1.2, `add_group_dependency(child_root, on, conditional_weights)` (lines 106–117)
- **Issue:** The `on` parameter is `list[str]`, implying multi-column conditioning (e.g., `on=["severity", "age_group"]`). However, the `conditional_weights` example (lines 109–114) shows only single-column conditioning — outer keys are values of one column. The spec never defines the schema for multi-column conditioning. Would keys be tuples? Nested dicts? Cross-product strings?
- **Impact:** Multi-column `on` lists are syntactically accepted but semantically undefined. The engine cannot construct the conditional distribution, and validation cannot check it.
- **Recommendation:** Either (a) restrict `on` to a single column (change type to `str`) since the root-only constraint already limits the number of viable parents, or (b) define the multi-column schema explicitly — e.g., `conditional_weights={("Severe","Old"): {"Insurance": 0.9, ...}}`.

---

### Finding A8: `inject_pattern` `params` schema is incomplete for 4 of 6 pattern types

- **Severity:** CRITICAL
- **Spec location:** §2.1.2, pattern types (lines 119–128)
- **Issue:** Only two pattern types have their `params` keys shown by example:
  - `outlier_entity`: `{"z_score": 3.0}` (line 124)
  - `trend_break`: `{"break_point": "2024-03-15", "magnitude": 0.4}` (line 427)

  The remaining four — `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly` — have zero `params` specification. What keys does each require?
  - `ranking_reversal`: which two metrics? A `metrics` key is implied by the L3 validation code (`p["metrics"]`, line 656) but never declared in the API.
  - `dominance_shift`: time split point? Which column? What magnitude?
  - `convergence`: convergence rate? Target variance? Time window?
  - `seasonal_anomaly`: which season? Anomaly magnitude? Which temporal feature?
- **Impact:** The LLM prompt lists all six types (§2.5, line 304–305) so the LLM will attempt to use them. Without `params` specs, generated code will pass arbitrary dicts that the engine cannot interpret. This is a blocking gap for 4 of 6 pattern injection implementations.
- **Recommendation:** For each pattern type, add a `params` specification table: required keys, types, defaults, and a usage example. At minimum:
  - `ranking_reversal`: `{"metrics": ["m1", "m2"]}`
  - `dominance_shift`: `{"col": "...", "split_point": "...", "new_dominant": "..."}`
  - `convergence`: `{"col": "...", "window": "late_half", "target_cv": 0.05}`
  - `seasonal_anomaly`: `{"col": "...", "season_filter": "month == 12", "magnitude": 0.3}`

---

### Finding A9: No explicit handling of single-value categorical columns

- **Severity:** MINOR
- **Spec location:** §2.1.1, `add_category` (lines 16–39)
- **Issue:** The spec says "rejects empty values" but does not address single-value categories (e.g., `values=["A"], weights=[1.0]`). A single-value category is statistically degenerate — it has zero variance and will cause chi-squared tests to produce undefined results. Should the SDK allow it?
- **Impact:** Edge case that could produce division-by-zero in chi-squared validation or misleading cardinality checks. Low probability in practice since the LLM is unlikely to produce single-value categories, but no guard exists.
- **Recommendation:** Add a validation rule: `len(values) >= 2` for categorical columns used as dimension group members. Alternatively, document that single-value categoricals are permitted but excluded from chi-squared tests.

---

### Finding A10: Temporal column has no explicit `group` parameter

- **Severity:** MINOR
- **Spec location:** §2.1.1, `add_temporal(name, start, end, freq, derive=[])` (line 41); §2.2, "Temporal as dimension group" (line 146)
- **Issue:** The `add_temporal` signature lacks a `group` parameter, yet §2.2 states temporal columns form a special dimension group. The group name is implicitly `"time"` based on the §2.6 metadata example, but this is never stated as a rule. Can the user name the temporal group? What if two temporal columns are declared (e.g., `start_date` and `end_date`)?
- **Impact:** Ambiguity about group naming; potential collision if user declares a categorical group named `"time"`. Multiple temporal column handling is undefined.
- **Recommendation:** Either (a) add an explicit `group` parameter defaulting to `"time"`, or (b) state that exactly one `add_temporal` call is allowed and it auto-creates a group named `"time"`. Also state that the name `"time"` is reserved and cannot be used by `add_category`.

---

### Finding A11: `add_measure` does not show how temporal predictors enter the effects model — missing examples and encoding detail

- **Severity:** MODERATE (downgraded from "missing semantics" to "missing examples/encoding detail")
- **Spec location:** §2.1.1, `add_measure` param_model (lines 51–70); §2.1.1, derived temporal columns "available as predictors for measures" (line 49)
- **Issue:** §2.1.1 states derived temporal columns (e.g., `month`, `day_of_week`) are "available as predictors for measures," but the `param_model` effects examples only show categorical predictors. Temporal derived columns like `month` are categorical-like (finite set of values), but `day_of_week` or `is_weekend` have different cardinalities. The spec does not show how these would appear in the intercept+effects schema. Can `month` appear in `effects` with 12 keys? Can `is_weekend` appear with `True`/`False` keys?

  **Post-audit clarification:** The underlying mechanism (intercept + effects) is already defined and naturally extends to temporal predictors, since derived temporal columns are finite-valued and categorical-like. The gap is specifically the absence of worked examples and the missing specification of encoding details (value sets for each derived column type), not a fundamental semantic omission.

- **Impact:** Implementers and the LLM lack guidance on temporal predictor syntax. If the engine expects categorical-style effect entries for temporal derived columns, the validation rules need to know the derived column's value set to verify completeness.
- **Recommendation:** Add an example showing a temporal predictor in `param_model`, e.g., `"effects": {"month": {"1": 0.1, "2": -0.05, ...}}`, and state the value set for each derived column type (month: 1–12, day_of_week: 0–6 or Mon–Sun, quarter: 1–4, is_weekend: True/False).

---

### Finding A12: Undeclared cross-group default semantics are undefined

- **Severity:** CRITICAL
- **Spec location:** §2.2, "Cross-group dependency" paragraph (line 153); §2.1.2, `declare_orthogonal` and `add_group_dependency`
- **Issue:** The spec defines two explicit cross-group relationship modes: `declare_orthogonal()` (independent) and `add_group_dependency()` (dependent). It states that cross-group independence is "opt-in, not default" (§2.2), but never defines what happens when two groups have **neither** an orthogonal declaration **nor** a group dependency declaration. This is the most common case — with N groups, there are O(N²) pairs, and most will have no explicit declaration.

  Concretely: if groups `"entity"` and `"payment"` have no `declare_orthogonal()` and no `add_group_dependency()`, how are their root columns sampled? Independently (contradicting "opt-in, not default")? Rejected as invalid (requiring the LLM to declare every pair)? Treated as "unknown" with some fallback?

- **Impact:** This is the #1 semantic ambiguity for the generation engine. The sampling algorithm (§2.4) must know whether to sample two roots independently or jointly, and the validator (§2.9 L1 orthogonal check) must know which pairs to test. Without a default, different implementations will produce different joint distributions for undeclared pairs. The LLM prompt's hard constraint 4 requires "at least 1 `declare_orthogonal()`" but does not require exhaustive pairwise declarations.
- **Recommendation:** The spec should state one of: (a) "Undeclared pairs default to independent sampling but are not subject to L1 orthogonality checks" (pragmatic), (b) "All cross-group pairs must have an explicit declaration — the SDK raises `UndeclaredRelationshipError` for any unspecified pair" (strict), or (c) "Undeclared pairs default to independent and are validated as orthogonal" (maximally constrained). Option (a) is recommended as the most practical default.

---

### Finding A13: Target-expression grammar for `inject_pattern` is undefined

- **Severity:** CRITICAL
- **Spec location:** §2.1.2, `inject_pattern(type, target, col, params)` (lines 119–128); §2.9 L3, `df.query(p["target"])` (lines 649, 662)
- **Issue:** The `target` parameter is a string filter expression passed directly to `df.query()` in the L3 validator (and presumably in the injection engine). The spec shows two examples:
  - `"hospital == 'Xiehe' & severity == 'Severe'"` (line 124)
  - `"hospital == 'Huashan'"` (line 427)

  But no formal grammar is defined. Specifically missing:
  - **Allowed operators:** Are `|` (or), `~` (not), `!=`, `<`, `>`, `>=`, `<=` permitted?
  - **Allowed column types:** Can the target reference measure columns (e.g., `"wait_minutes > 30"`)? Temporal columns? Derived columns?
  - **Quoting rules:** Must string values use single quotes? What about values containing quotes?
  - **Security boundary:** Since `target` is passed to `df.query()`, which uses `eval()` internally, arbitrary Python expressions could be injected (e.g., `"__import__('os').system('rm -rf /')")`. Is the target string sanitized?

- **Impact:** Without a grammar, the injection engine and L3 validator cannot safely parse or execute target expressions. The security exposure via `df.query(eval())` is a code execution risk if the LLM generates adversarial or malformed targets. This overlaps with but is distinct from A14 (security model) — A14 covers the broader sandbox; this covers the specific `target` expression attack surface.
- **Recommendation:** Define a restricted target grammar: (a) allowed operators: `==`, `!=`, `&`, `|`, comparison operators for numeric columns; (b) column references restricted to declared categorical and temporal columns only; (c) values restricted to declared categorical values or date literals; (d) implementation should use a safe parser (not raw `df.query()`), or sanitize against the declared schema before passing to `query()`.

---

### Finding A14: No security/sandbox policy for LLM-generated code

- **Severity:** CRITICAL
- **Spec location:** §2.5, "Output must be pure, valid Python returning sim.generate()" (hard constraint 6); §2.7, execution-error feedback loop (lines 489–498)
- **Issue:** The LLM generates a Python script (§2.5) which is executed in a sandbox (§2.7). The spec requires "pure, valid Python" but defines no security policy for this execution:
  - **Import restrictions:** Can the LLM import arbitrary modules? The one-shot example imports only `from chartagent.synth import FactTableSimulator`, but no whitelist restricts other imports.
  - **System access:** No restrictions on file I/O, network access, or subprocess execution within the generated script.
  - **Resource limits:** No timeout, memory cap, or CPU limit for `build_fact_table()` execution.
  - **SDK method whitelist enforcement:** The prompt lists available methods, but nothing prevents the LLM from calling undocumented internal methods or monkey-patching the SDK.

- **Impact:** A compromised or confused LLM could generate code that escapes the intended SDK surface — reading files, making network calls, or entering infinite loops. Even without malice, the LLM may import `numpy` or `pandas` directly to construct data outside the SDK, bypassing all validation guarantees.
- **Recommendation:** The spec should define: (a) an import whitelist (only `chartagent.synth` and standard-library modules needed by the SDK), (b) an execution sandbox (e.g., RestrictedPython, subprocess with resource limits, or container isolation), (c) a timeout budget for `build_fact_table()` execution, and (d) post-execution verification that the generated code only calls whitelisted SDK methods (static analysis or runtime interception).

---

### Finding A15: SDK API contract gaps — duplicate column names, mutability after declaration, reserved words

- **Severity:** MODERATE
- **Spec location:** §2.1.1 (all `add_*` methods); §2.1.2 (relationship declarations)
- **Issue:** The SDK API lacks specification for several contract-level behaviors:
  1. **Duplicate column names:** What happens if the LLM calls `add_category("hospital", ...)` twice? Is it an error, a silent overwrite, or an append? The spec never states uniqueness constraints on column names.
  2. **Mutability after declaration:** Can the LLM modify a column's properties after declaration (e.g., call `add_category("hospital", ...)` with different weights after already declaring it)? Is the simulator's state append-only or mutable?
  3. **Reserved words:** Column names like `"index"`, `"values"`, `"count"` would conflict with pandas DataFrame attributes. The spec defines no reserved-name list or validation.

- **Impact:** Duplicate names silently corrupt the DAG or metadata. Mutable declarations make the generation order ambiguous ("which version of `hospital` is canonical?"). Reserved-name collisions cause runtime `AttributeError` in downstream pandas operations.
- **Recommendation:** The spec should state: (a) column names must be unique across all `add_*` calls — duplicates raise `DuplicateColumnError`; (b) declarations are append-only and immutable once registered; (c) provide a reserved-name list (at minimum: `index`, `values`, `columns`, `count`, `query`, `copy`) or validate that column names are valid Python identifiers not in `dir(pd.DataFrame)`.

---

## Reviewer B — Engine & Execution Architect

Focus: Generation algorithm correctness, DAG construction, row-level sampling semantics, pattern injection mechanics, determinism guarantees.

---

### Finding B1: Temporal sampling for non-daily frequencies is unspecified

- **Severity:** MODERATE
- **Spec location:** §2.1.1, `add_temporal` `freq` parameter (line 41); §2.4, Step 1 line 3: `visit_date_i ~ Uniform(start, end)` (line 247)
- **Issue:** The spec's only temporal sampling example uses `freq="daily"` with uniform random dates. The `freq` parameter implies other granularities (weekly, monthly, quarterly per §1.3.2 in the task hierarchy), but their sampling semantics are undefined:
  - `freq="weekly"`: Are sampled values week-start dates (Mondays)? Random dates snapped to weeks?
  - `freq="monthly"`: First of the month? Random day within each month?
  - Does `freq` affect the number of unique temporal values? Does it change the uniform distribution?
  - Does `freq` affect derived columns? (e.g., `day_of_week` is constant if dates are all Mondays)
- **Impact:** Ambiguous temporal sampling produces inconsistent datasets across implementations. Derived columns may become degenerate (zero variance) depending on frequency interpretation.
- **Recommendation:** Define sampling semantics for each supported frequency: `daily` = uniform random over all dates in [start, end]; `weekly` = uniform over week-start dates; `monthly` = uniform over month-start dates. Also specify whether `freq` affects the uniform distribution or merely post-hoc rounding.

---

### Finding B2: Pattern injection (Phase γ) conflicts with L2 statistical validation — and the broader post-processing contract question

- **Severity:** CRITICAL
- **Spec location:** §2.8, Phase γ (line 529); §2.9 L2, KS test (lines 614–621); §2.9 L3, pattern validation (lines 647–676)
- **Issue:** The generation pipeline applies pattern injection *after* measure generation (Phase β → Phase γ). The L2 validator then tests the *final* DataFrame (post-injection) against the *declared* distribution parameters. Pattern injection deliberately distorts the distribution:
  - `outlier_entity` shifts the mean of a subset, which inflates the variance of the full column and skews the conditional distribution, causing KS test failures.
  - `trend_break` creates a bimodal distribution in the affected column (before/after), which will fail KS tests for any unimodal declared family.

  The spec provides no mechanism to exclude pattern-affected rows from L2 tests, no adjustment to expected parameters post-injection, and no ordering rule for L2-before-L3 vs. L3-before-L2.

  **Generalized framing (post-audit):** This is an instance of a broader unresolved contract question: **should post-processing steps (pattern injection γ, realism injection δ) be allowed to violate properties validated by earlier layers?** The pipeline is ordered α → β → γ → δ → validate(L1, L2, L3), but validation runs against *declared* properties that pre-date γ and δ. The spec never states which invariants each post-processing step is permitted to break, nor how validation should adapt. B2's L2-vs-pattern conflict and C6's L1-vs-realism conflict are both symptoms of this missing contract.

- **Impact:** L2 and L3 are structurally contradictory for any column with injected patterns. The auto-fix loop for `ks_*` failures (`widen_variance`) will fight the auto-fix for `outlier_*` failures (`amplify_magnitude`), creating oscillation. In the worst case, validation never converges.
- **Recommendation:** The spec should define a **post-processing invariant contract** specifying, for each post-processing phase, which validation layers apply to the pre- vs. post-processed data. Concretely: (a) L2 statistical tests run on the pre-injection DataFrame (Phase β output) and L3 on the post-injection DataFrame (Phase γ output), or (b) L2 thresholds are relaxed for columns that are also pattern targets, with pattern-target rows excluded from statistical tests. Option (a) is cleanest architecturally and also resolves C6 (L1 runs pre-realism, separate realism-rate check runs post-realism).

---

### Finding B3: Auto-fix loop may undo injected patterns

- **Severity:** CRITICAL
- **Spec location:** §2.9, Auto-Fix Loop (lines 679–699)
- **Issue:** The auto-fix strategies operate on the `Check` object, but the code regenerates the *entire* DataFrame on each retry (`df = build_fn(seed=42 + attempt)`, line 691). The fix strategies (`widen_variance`, `amplify_magnitude`, `reshuffle_pair`) are called but their effect is unclear — they appear to modify parameters, but the regeneration uses `build_fn` which re-runs the full SDK script from scratch. Modifications made by auto-fix strategies are lost on the next `build_fn` call unless they mutate the simulator's internal state.
  
  Additionally, `reshuffle_pair` (for orthogonal failures) randomly permutes a column, which could destroy patterns injected in Phase γ. If `hospital` is reshuffled to fix an orthogonal failure, then `target="hospital == 'Xiehe'"` now points to different rows, potentially invalidating L3 checks.
- **Impact:** Auto-fix may be entirely ineffective (parameters mutated then overwritten) or destructive (reshuffling breaks patterns). The retry loop may consume all attempts with no actual improvement.
- **Recommendation:** Clarify the auto-fix mutation model: do strategies mutate the `FactTableSimulator` instance's declarations (persistent across retries), or do they post-process the DataFrame (applied after each regeneration)? If the former, `build_fn` must be a closure over the mutable simulator. If the latter, define the application order: pattern injection → auto-fix adjustments → validation. Also, `reshuffle_pair` should exclude pattern-target columns.

---

### Finding B4: Full DAG construction algorithm is not specified for the general case

- **Severity:** MODERATE
- **Spec location:** §2.4, "The Full Generation DAG" (lines 213–237); §2.8, `_build_full_dag()` (line 515)
- **Issue:** The spec shows a concrete DAG for the hospital example but does not specify the general construction algorithm. Specifically:
  - How are stochastic measures' categorical predictor dependencies represented in the DAG? In the example, `wait_minutes` depends on `severity` and `hospital` (categorical predictors in its `param_model`), creating edges from those categoricals to the measure. This implicit edge-creation rule from `param_model.effects` keys is never stated as a general algorithm.
  - How are structural measures' effects-dict dependencies represented? `cost` depends on `severity` via `severity_surcharge`, but the DAG diagram shows this as `cost ← severity`. The resolution rule (effect name → categorical column lookup) is not formalized.
  - What happens if a structural measure's formula references a temporal derived column (e.g., `formula="wait_minutes * month_factor"`)? Does this create an edge from `month` to the measure?
- **Impact:** Without a general edge-construction algorithm, `_build_full_dag()` is ambiguous to implement. Different interpretations produce different topological orders, which may cause measures to be sampled before their predictor columns exist.
- **Recommendation:** Formalize the edge rules as an algorithm:
  1. For each `add_category` with `parent`, add edge `parent → child`.
  2. For each `add_group_dependency`, add edge `on_col → child_root`.
  3. For each `add_temporal` derived column, add edge `temporal_root → derived`.
  4. For each `add_measure`, for each predictor column in `param_model.effects`, add edge `predictor → measure`.
  5. For each `add_measure_structural`, for each measure referenced in `formula`, add edge `upstream_measure → this_measure`; for each effect, resolve to a categorical column and add edge `categorical → this_measure`.

---

### Finding B5: Stochastic measures with temporal predictors — missing examples and encoding detail

- **Severity:** MODERATE (downgraded from "no generation semantics" to "missing examples/encoding detail")
- **Spec location:** §2.1.1, line 49: "available as predictors for measures"; §2.3, general formula (line 176); §2.4, Layer 2 (lines 228–236)
- **Issue:** The spec states derived temporal columns are "available as predictors" and the general param formula is θⱼ = β₀ + Σₘ βₘ(Xₘ) where Xₘ can be any categorical-like column. The generation algorithm (§2.4) generates non-measure columns first (including temporal derivations in Layer 1), then measures in Layer 2. This ordering *supports* temporal predictors in principle.

  **Post-audit clarification:** The generation semantics are not architecturally incomplete — the intercept + effects model and the DAG ordering already handle temporal predictors correctly in principle. The gap is specifically:
  - No worked example shows temporal effects in `param_model` (e.g., `"effects": {"month": {"1": 0.1, ...}}`).
  - The DAG diagram (§2.4) does not show edges from temporal derived columns to measures, even though such edges would be needed for correct topological ordering.
  - The encoding conventions (e.g., month values as strings `"1"`–`"12"` vs. integers) are unspecified.
  - The L2 KS test (`iter_predictor_cells`) would need to enumerate month × severity × hospital cells, producing very sparse cells with unreliable test statistics — but this is a cell-sparsity concern (see C2), not a semantic gap.

- **Impact:** The feature is implied as available but lacks worked examples, DAG representation, and encoding detail. Implementers may omit it or implement it with inconsistent encoding.
- **Recommendation:** Either (a) add an explicit example of temporal effects in a stochastic measure, show the DAG edges, and specify encoding conventions for each derived column type, or (b) state that temporal derived columns are available as predictors but their effect entries are optional/advanced and L2 validation is marginal-only when temporal predictors are present.

---

### Finding B6: Pattern injection mechanics are unspecified for 4 of 6 types

- **Severity:** CRITICAL
- **Spec location:** §2.8, Phase γ `_inject_patterns` (line 529); §2.1.2, pattern types (line 127)
- **Issue:** The spec provides injection examples only for `outlier_entity` (implied: shift target subset mean) and `trend_break` (implied: scale values after break point). The remaining four types lack any injection algorithm:
  - `ranking_reversal`: How is the reversal injected? Swap means of two measures across entities? Selectively inflate/deflate?
  - `dominance_shift`: What is shifted? Category proportions over time? Measure values?
  - `convergence`: How is convergence achieved? Variance reduction over time? Mean compression?
  - `seasonal_anomaly`: How is the anomaly created? Additive shift to specific seasonal periods?
- **Impact:** Directly blocks implementation of 4 of 6 pattern types. Combined with A8 (missing params schema), these four patterns are entirely opaque — neither their input contract nor their transformation algorithm is defined.
- **Recommendation:** For each pattern type, specify: (a) the transformation applied to the DataFrame, (b) the expected statistical signature (for L3 validation), and (c) a worked example. The injection algorithm should be deterministic given `(pattern_spec, df, rng)`.

---

### Finding B7: Seed increment strategy in auto-fix loop may not actually fix failures

- **Severity:** MODERATE
- **Spec location:** §2.9, `generate_with_validation`, line 691: `df = build_fn(seed=42 + attempt)`
- **Issue:** The auto-fix loop increments the seed on each retry, producing a different random draw. But if the failure is structural (e.g., KS test fails because declared parameters are marginally compatible with the family), a different seed produces a statistically equivalent dataset. The `widen_variance` fix modifies parameters, but as noted in B3, the `build_fn` call may overwrite these modifications.
  
  More fundamentally: the auto-fix strategies modify `Check` objects or pattern specs, but the regeneration calls `build_fn(seed=42+attempt)` which constructs a *new* simulator from the LLM's original code. Unless `build_fn` is somehow parameterized to accept modifications, the fixes are discarded.
- **Impact:** The auto-fix loop may be a no-op — running 3 identical simulations with different seeds, never actually applying the parameter adjustments. This wastes compute and always soft-fails.
- **Recommendation:** Define the mutation target explicitly. The auto-fix should either: (a) mutate the `FactTableSimulator` instance before calling `generate()` again (not re-running `build_fn`), or (b) modify the SDK script source code and re-execute. Option (a) is simpler and aligns with the "no LLM re-call" principle.

---

### Finding B8: Topological sort tie-breaking is unspecified, undermining determinism claim

- **Severity:** MODERATE
- **Spec location:** §2.8, `topological_sort(full_dag)` (line 517); §2.8, "fully deterministic, DAG-ordered pipeline" (line 509); §2.8, "bit-for-bit reproducible" (line 510)
- **Issue:** The spec claims the generation pipeline is "fully deterministic" and "bit-for-bit reproducible" given the same seed. However, topological sort of a DAG is not unique — when multiple columns have no ordering constraint between them (e.g., two independent root categoricals), the sort order depends on implementation-specific tie-breaking. Different valid topological orderings produce different RNG consumption sequences, yielding different output DataFrames even with the same seed.

  For example, if `hospital` and `severity` are both independent roots, sorting them as `[hospital, severity, ...]` vs. `[severity, hospital, ...]` changes which column consumes which RNG draws. The spec's determinism guarantee requires a canonical tie-breaking rule, but none is stated.

- **Impact:** Two correct implementations of the spec may produce different DataFrames from the same seed, violating the "bit-for-bit reproducible" claim. This undermines cross-implementation testing and makes regression testing unreliable.
- **Recommendation:** Specify a deterministic tie-breaking rule for topological sort — e.g., "when multiple columns are eligible for the next position, choose the one with the lexicographically smallest name." This ensures a single canonical ordering for any valid DAG.

---

### Finding B9: Formula evaluation behavior under NaN/realism is undefined

- **Severity:** MODERATE
- **Spec location:** §2.1.1, `add_measure_structural` formula (lines 72–81); §2.8, Phase δ realism injection (lines 532–534); §2.8, Phase β `_eval_structural` (line 525)
- **Issue:** Structural measure formulas reference upstream measures by name (e.g., `"wait_minutes * 12 + severity_surcharge"`). If realism injection (`set_realism(missing_rate=...)`) introduces `NaN` values into upstream measure columns, the formula evaluation will propagate `NaN` into all downstream structural measures. The spec does not address:
  - **Evaluation order vs. realism order:** Realism is Phase δ (after measures), so NaN injection doesn't affect formula evaluation during Phase β. But if a future refactoring or an implementer reorders phases, NaN propagation becomes a silent corruption vector.
  - **Explicit contract:** The spec never states "formula evaluation operates on pre-realism data" as a hard invariant.
  - **Post-realism structural consistency:** After Phase δ injects NaN into `wait_minutes`, the `cost` column (computed from `wait_minutes`) retains its pre-realism value. This creates an inconsistency: `cost` is defined but `wait_minutes` is missing for the same row.

- **Impact:** Without an explicit contract, implementers may inadvertently reorder phases and corrupt structural measures. Even with correct ordering, the row-level inconsistency (missing upstream, present downstream) could confuse Phase 3 QA generation.
- **Recommendation:** The spec should: (a) state explicitly that formula evaluation (Phase β) precedes realism injection (Phase δ) as a hard invariant, and (b) specify whether realism injection should cascade to downstream structural measures (i.e., if `wait_minutes` is NaN'd, should `cost` also be NaN'd for that row?). Cascading NaN is more realistic; preserving computed values is simpler.

---

### Finding B10: Contradictory declaration handling is partially but not fully covered

- **Severity:** MODERATE
- **Spec location:** §2.7, execution-error feedback loop (lines 489–498); §2.1.1–§2.1.2, all declaration methods
- **Issue:** §2.7 shows that some contradictory declarations are caught by typed exceptions (e.g., `CyclicDependencyError`, `UndefinedEffectError`, `NonRootDependencyError`). However, several classes of contradictory declarations are not covered:
  - **Declaring a column both orthogonal and dependent:** Calling `declare_orthogonal("entity", "patient")` and then `add_group_dependency("hospital", on=["severity"])`. The spec does not state whether this is an error or whether the dependency overrides the orthogonality.
  - **Conflicting per-parent weights and group dependency:** If `payment_method` has a group dependency on `severity`, but the LLM also declares `payment_method` with flat weights — which takes precedence?
  - **Measure referenced before declaration:** The spec states structural measures "may only reference measures declared before them" (§2.3), but no exception type is shown for this specific violation.

  Note: this is narrower than a blanket "no conflict detection" — §2.7's existing exception types handle many cases (cycles, undefined effects, non-root dependencies). The gap is specifically the cases listed above.

- **Impact:** The LLM may generate declarations that are locally valid but globally contradictory. Without exception types for these cases, the engine silently chooses one interpretation, producing data that doesn't match the LLM's intent.
- **Recommendation:** Add exception types for: (a) `OrthogonalDependencyConflictError` when a group pair has both declarations, (b) `WeightOverrideConflictError` when flat weights conflict with a group dependency, and (c) `ForwardReferenceError` when a structural measure references an undeclared or later-declared measure. These should trigger the §2.7 feedback loop.

---

## Reviewer C — Validation & Integration Specialist

Focus: Validator correctness, auto-fix convergence, schema metadata completeness for Phase 3, error feedback loop robustness.

---

### Finding C1: L3 validation logic is missing for `convergence` and `seasonal_anomaly`

- **Severity:** CRITICAL
- **Spec location:** §2.9 L3, `_L3_pattern` code block (lines 646–676)
- **Issue:** The L3 pseudocode has explicit branches for `outlier_entity`, `ranking_reversal`, `trend_break`, and `dominance_shift` — but has **no branch** for `convergence` or `seasonal_anomaly`. These two pattern types are listed as supported (§2.1.2) and appear in the LLM prompt (§2.5), but the validator silently ignores them. Any `convergence` or `seasonal_anomaly` pattern in the metadata will produce zero checks — they are injected but never validated.

  **Audit confirmation:** This gap was independently confirmed by Audit Stage A (§2.9_absent_convergence_seasonal): 2 of the 6 declared pattern types have zero L3 validation pseudocode, making the "three-layer validation guarantee" incomplete for these types.

- **Impact:** Patterns are injected (Phase γ) but never verified (L3), defeating the three-layer validation guarantee. The LLM may inject broken convergence/seasonal patterns that corrupt the data with no detection.
- **Recommendation:** Add L3 validation branches for both types. Suggested:
  - `convergence`: Split data into early/late halves by temporal column; compute inter-group variance of `col` in each half; assert late variance < early variance × threshold.
  - `seasonal_anomaly`: Compute `col` mean for the anomaly season vs. other seasons; assert `|season_mean - other_mean| / other_std > threshold`.

---

### Finding C2: L2 KS test cell sparsity — no minimum sample size guard

- **Severity:** MODERATE (downgraded from CRITICAL — the issue is real but represents a statistical-power concern, not a structural impossibility or blocking internal inconsistency)
- **Spec location:** §2.9 L2, KS test loop (lines 614–621)
- **Issue:** The L2 validator iterates over all predictor cells via `iter_predictor_cells()` and runs a KS test per cell. For the one-shot example, `severity` (3 values) × `hospital` (5 values) = 15 cells. With 500 total rows and non-uniform weights (e.g., `Severe` at 0.15, `Zhongshan` at 0.15), the cell `(Severe, Zhongshan)` expects only `500 × 0.15 × 0.15 ≈ 11 rows`. A KS test with n=11 has very low statistical power — it will almost always pass (p > 0.05), even for badly mis-specified distributions.
  
  Worse, if temporal predictors are added (Finding B5), the cross-product explodes: 3 × 5 × 12 months = 180 cells with ~2.8 rows per cell — statistically meaningless.
  
  The spec provides no minimum sample size threshold below which the KS test is skipped or replaced with a less granular test.
- **Impact:** L2 validation is unreliable for sparse cells (false passes) and fragile for dense cells (false failures due to multiple testing). Neither direction is controlled.
- **Recommendation:** Add a minimum sample size guard (e.g., `if len(subset) < 30: skip or use marginal test`). Also consider Bonferroni correction or false discovery rate control since the number of simultaneous tests scales with the cross-product of predictor cardinalities.

---

### Finding C3: Schema metadata missing critical fields for Phase 3 reconstruction

- **Severity:** CRITICAL
- **Spec location:** §2.6, schema_metadata JSON (lines 446–478)
- **Issue:** The schema metadata is the "contract between Phase 2 and Phase 3" (line 443), but it omits several fields that Phase 3 needs:
  1. **Stochastic measure `param_model`**: The metadata records `family` but not the full `param_model` (intercept, effects). Phase 3 QA generation needs to know *what* distribution parameters were used to formulate statistically grounded questions (e.g., "Which hospital has the highest expected wait time?").
  2. **Structural measure `formula` and `effects`**: The metadata records `depends_on` but not the actual formula or effect values. Phase 3 cannot reconstruct causal semantics (e.g., "How does cost relate to wait_minutes?") without the formula.
  3. **Structural measure `noise` spec**: The metadata lacks `noise_sigma`, but the L2 validator references `col["noise_sigma"]` (line 631). This field is required for validation but absent from the metadata example.
  4. **Categorical `values` and `weights`**: The metadata records `cardinality` but not the actual value labels or weight vectors. L1 validation references `col["values"]` and `col["weights"]` (line 575) which are absent from the §2.6 example.
  5. **Group dependency `conditional_weights`**: The metadata records `child_root` and `on` but not the actual weight table. L2 validation references `dep["conditional_weights"]` (line 636) which is absent.
  6. **Pattern `params`**: The metadata records `type`, `target`, `col` but not `params` (e.g., `z_score`, `break_point`, `magnitude`). L3 validation needs these.
- **Impact:** The §2.6 metadata example is internally inconsistent with the §2.9 validation code — the validator references fields that the metadata doesn't contain. More importantly, Phase 3 receives an incomplete contract that prevents reconstruction of generation semantics.
- **Recommendation:** Extend the metadata schema to include all fields referenced by the validator. At minimum add: `values`, `weights` for categoricals; `param_model` for stochastic measures; `formula`, `effects`, `noise_sigma` for structural measures; `conditional_weights` for group dependencies; `params` for patterns.

---

### Finding C4: Auto-fix strategies cover only 4 of the 9+ possible failure modes

- **Severity:** MODERATE
- **Spec location:** §2.9, AUTO_FIX dict (lines 682–687)
- **Issue:** The AUTO_FIX table maps: `ks_*` → `widen_variance`, `outlier_*` → `amplify_magnitude`, `trend_*` → `amplify_magnitude`, `orthogonal_*` → `reshuffle_pair`. The following failure modes have **no auto-fix strategy**:
  - `row_count` (L1) — target rows mismatch
  - `cardinality_*` (L1) — missing categorical values
  - `marginal_*` (L1) — root weight deviation > 0.10
  - `finite_*` (L1) — NaN/Inf in measures
  - `structural_*_residual_mean` (L2) — formula residual bias
  - `structural_*_residual_std` (L2) — noise sigma mismatch
  - `group_dep_*` (L2) — conditional transition deviation
  - `reversal_*` (L3) — ranking reversal not achieved
  - `dominance` (L3) — dominance shift not achieved

  When these checks fail, `match_strategy` returns `None` and the failure persists across all retries.
- **Impact:** The auto-fix loop silently ignores the majority of failure types. The soft-fail return (line 699) means corrupted data passes through to Phase 3 with failed validation checks.
- **Recommendation:** For each uncovered failure mode, add either: (a) an auto-fix strategy, or (b) explicit documentation that it cannot be auto-fixed and must escalate to the LLM re-call loop (§2.7). Suggested additions:
  - `marginal_*` → resample from corrected weights
  - `structural_*` → adjust noise sigma or formula coefficients
  - `group_dep_*` → resample dependent column from corrected conditionals
  - `row_count` → regenerate with adjusted target
  - `cardinality_*` → ensure at least one instance of each category value

---

### Finding C5: The §2.7 error loop and §2.9 auto-fix loop relationship is ambiguous

- **Severity:** MODERATE (downgraded from CRITICAL — the composition is inferable from §2.7 step 3's sequential wording, and is a retry-composition gap rather than a structural impossibility)
- **Spec location:** §2.7, steps 1–6 (lines 489–498); §2.9, `generate_with_validation` (lines 689–699)
- **Issue:** There are two distinct retry loops in the spec:
  1. **§2.7 Execution-Error Loop**: catches SDK exceptions (CyclicDependencyError, etc.), feeds traceback to LLM, retries code generation. `max_retries=3`.
  2. **§2.9 Auto-Fix Loop**: catches validation failures (L1/L2/L3), applies parameter adjustments, re-runs `generate()`. `max_retries=3`.

  The spec never defines their composition:
  - Are they nested (outer = §2.7, inner = §2.9)?
  - Are they sequential (§2.7 runs until code executes, then §2.9 runs on the output)?
  - Can a §2.9 failure escalate to §2.7 (e.g., persistent L2 failure triggers LLM re-call)?
  - Total worst-case attempts: 3 × 3 = 9 LLM calls? Or 3 + 3 = 6?
  
  §2.7 step 3 says "SUCCESS → proceed to ... Validation (§2.9)," suggesting sequential composition, but this is buried in a bullet list and not formalized.
- **Impact:** Without explicit composition rules, implementers may nest them (creating 9 LLM calls max) or implement them as a single flat loop (losing the distinction between code errors and statistical errors). The retry budget and escalation policy are undefined.
- **Recommendation:** Add a dedicated subsection defining the pipeline composition:
  1. §2.7 loop runs until code *executes* without SDK exceptions (max 3 LLM retries).
  2. On successful execution, §2.9 loop runs on the output (max 3 regeneration retries, no LLM calls).
  3. If §2.9 exhausts retries, soft-fail (do not escalate to §2.7).
  4. Total budget: at most 3 LLM calls + 3 engine re-runs = 6 attempts.

---

### Finding C6: L1 validation `finite_*` check conflicts with realism injection

- **Severity:** MODERATE
- **Spec location:** §2.9 L1, measure finite/non-null check (lines 579–584); §2.8, Phase δ realism injection (lines 532–534); §2.1.2, `set_realism(missing_rate, ...)` (line 129)
- **Issue:** L1 validates that all measure values are finite and non-null: `df[col].notna().all() and np.isfinite(df[col]).all()`. But Phase δ (realism injection) introduces `NaN` values at `missing_rate` frequency. Validation runs *after* realism injection (since it validates the final DataFrame), so any `missing_rate > 0` will deterministically fail the `finite_*` check.
- **Impact:** `set_realism(missing_rate=0.05, ...)` makes L1 validation always fail for every measure column. The auto-fix table has no strategy for `finite_*` failures, so the failure persists to soft-fail.
- **Recommendation:** The spec should state: "When realism is active, L1 `finite_*` checks are adjusted to verify `non_null_rate >= (1 - missing_rate - tolerance)` rather than strict non-null." Alternatively, L1 finite checks should run *before* realism injection, and a separate L1 check verifies that missing rate matches the declared rate.

---

### Finding C7: `_get_measure_spec()` and `iter_predictor_cells()` are referenced but undefined

- **Severity:** MODERATE
- **Spec location:** §2.9 L2, lines 615–616: `spec = self._get_measure_spec(col["name"])` and `spec.iter_predictor_cells()`
- **Issue:** The L2 validation code references `_get_measure_spec()` which returns an object with an `iter_predictor_cells()` method. Neither method is defined anywhere in the spec. The implementer must infer:
  - What does `_get_measure_spec` return? A measure declaration object? A dict?
  - What does `iter_predictor_cells` yield? The signature `(group_filter, expected_params)` is implied by usage, but the algorithm for computing the cross-product of effects, constructing the filter string, and computing concrete parameter values from intercept+effects is non-trivial and unspecified.
- **Impact:** This is core to L2 validation correctness. An incorrect `iter_predictor_cells` implementation (e.g., wrong cross-product enumeration, wrong parameter computation) silently passes or fails valid data.
- **Recommendation:** Specify `iter_predictor_cells` as a formal algorithm:
  1. Collect all predictor columns from the measure's `param_model` effects.
  2. Compute the Cartesian product of their value sets.
  3. For each cell, compute concrete params: for each distribution parameter, apply `intercept + Σ effects[col][value]`.
  4. Construct a pandas query string for the cell filter.
  5. Yield `(filter_string, concrete_params_tuple)`.

---

### Finding C8: L2 validation for structural measures references `col["formula"]` and `col["noise_sigma"]` not present in metadata

- **Severity:** CRITICAL (overlaps with C3)
- **Spec location:** §2.9 L2, lines 626–631; §2.6, columns metadata (lines 466–468)
- **Issue:** The structural measure residual check calls `eval_formula(col["formula"], df)` and checks `col["noise_sigma"]`. But the §2.6 metadata example for structural measures shows only: `{"name": "cost", "type": "measure", "measure_type": "structural", "depends_on": ["wait_minutes"]}`. There is no `formula` key, no `noise_sigma` key, and no `effects` key. The validator code will raise `KeyError` at runtime.
- **Impact:** L2 validation for structural measures is broken as specified — the metadata contract does not contain the fields the validator reads. This is a blocking internal inconsistency.
- **Recommendation:** (Same as C3) Add `formula`, `effects`, and `noise_sigma` to the structural measure metadata schema. The columns entry should look like: `{"name": "cost", "type": "measure", "measure_type": "structural", "depends_on": ["wait_minutes"], "formula": "wait_minutes * 12 + severity_surcharge", "effects": {...}, "noise_sigma": 30}`.

---

### Finding C9: L1 marginal weight validation references `col["values"]` and `col["weights"]` not in metadata

- **Severity:** CRITICAL (overlaps with C3)
- **Spec location:** §2.9 L1, lines 572–577; §2.6, categorical column metadata (lines 461–464)
- **Issue:** The marginal weight check iterates `zip(col["values"], col["weights"])`, but the §2.6 metadata for categoricals only contains `name`, `group`, `parent`, `type`, and `cardinality`. There are no `values` or `weights` keys. The validator will raise `KeyError`.
- **Impact:** L1 marginal validation is broken as specified. Root categorical weight drift cannot be detected.
- **Recommendation:** Add `"values": ["Xiehe", ...]` and `"weights": [0.25, ...]` to the categorical column metadata entries.

---

### Finding C10: `dominance_shift` L3 validation delegates to `_verify_dominance_change` with no specification

- **Severity:** MODERATE
- **Spec location:** §2.9 L3, lines 672–674
- **Issue:** The L3 code for `dominance_shift` simply calls `self._verify_dominance_change(df, p, meta)` with no definition. Unlike the other L3 checks which have inline logic, this is a black box. What does "dominance change" mean? Which column is examined? Over what time split? How is "dominant" defined (mode? highest mean?)?
- **Impact:** Cannot implement L3 validation for `dominance_shift` without inventing semantics.
- **Recommendation:** Inline the validation logic or define the method. Suggested: split data at temporal midpoint, compute the mode of a categorical column (or the highest-mean entity for a measure) in each half, assert they differ.

---

### Finding C11: L3 `ranking_reversal` hard-codes first dimension group as grouping axis

- **Severity:** MODERATE
- **Spec location:** §2.9 L3, lines 657–658: `root = meta["dimension_groups"][list(meta["dimension_groups"].keys())[0]]["hierarchy"][0]`
- **Issue:** The ranking reversal check groups by the root of the *first* dimension group in the metadata dict. Dictionary ordering is insertion-order in Python 3.7+, but the "first" group is arbitrary — it depends on the order the LLM declared groups. The pattern spec provides no `group` or `dimension` parameter to specify which axis the reversal should be computed over.
- **Impact:** The reversal check may compute ranks over the wrong dimension (e.g., over `severity` instead of `hospital`), producing false passes or false failures.
- **Recommendation:** The `ranking_reversal` pattern `params` should include a `group_by` key specifying which column to group by. The L3 code should use `p["params"]["group_by"]` instead of hard-coding the first group.

---

### Finding C12: Soft-fail behavior at end of auto-fix loop is undefined for downstream

- **Severity:** MODERATE
- **Spec location:** §2.9, line 699: `return df, report  # soft failure after max retries`
- **Issue:** When the auto-fix loop exhausts all retries, it returns the last `(df, report)` with `report.all_passed == False`. The spec does not define what happens next:
  - Does Phase 3 receive this DataFrame despite validation failures?
  - Is the scenario logged and skipped (as in §2.7 step 6)?
  - Is there a quality threshold (e.g., "if >80% of checks pass, proceed")?
  - Which specific failure types are acceptable for soft-fail vs. which should block?
- **Impact:** Without a policy, the pipeline may silently pass corrupted data to Phase 3, where it generates misleading charts and QA pairs.
- **Recommendation:** Define a soft-fail policy: (a) if any L1 check fails, the scenario is skipped (structural corruption is unrecoverable); (b) if only L2/L3 checks fail, the data proceeds with a quality flag; (c) the validation report is included in the metadata for Phase 3 to inspect.

---

### Finding C13: No formal metadata schema definition or versioning

- **Severity:** CRITICAL
- **Spec location:** §2.6, schema_metadata JSON (lines 446–478); §2.9, all validator methods; Phase 3 contract
- **Issue:** The §2.6 metadata is shown by a single JSON example, but there is no formal schema definition (e.g., JSON Schema, TypedDict, dataclass). This causes multiple problems:
  1. **No required-vs-optional distinction:** Which fields are mandatory? Can `orthogonal_groups` be empty? Can `patterns` be omitted?
  2. **No type annotations:** What type is `cardinality`? Integer? What type is `depends_on`? List of strings? The example implies these, but they are not stated.
  3. **No versioning:** The metadata is the contract between Phase 2 (producer) and Phase 3 + the validator (consumers). If the schema evolves (e.g., new fields per C3), there is no version field to detect mismatches. A Phase 3 implementation expecting v2 metadata receiving v1 metadata will fail with cryptic `KeyError`s.
  4. **No validation of the metadata itself:** The validator checks the DataFrame, but nothing validates that the metadata is well-formed before the validator consumes it.

  This compounds C3/C8/C9: those findings identify specific missing fields, but this finding addresses the structural absence of a schema contract.

- **Impact:** Every subsystem consuming metadata (validator, Phase 3, QA generator) must reverse-engineer the expected structure from the example. Schema drift between producers and consumers will cause silent failures or runtime crashes.
- **Recommendation:** Define the metadata schema formally — either as a JSON Schema document, a Python `TypedDict`/`@dataclass`, or at minimum a complete field table with types, required/optional status, and descriptions. Add a `"schema_version"` field (e.g., `"schema_version": "2.0"`) to enable forward compatibility.

---

### Finding C14: §2.10 lacks measurable success criteria

- **Severity:** MINOR
- **Spec location:** §2.10, "Design Advantages" (lines 710–720)
- **Issue:** §2.10 lists six downstream affordances of the atomic-grain fact table (distribution charts, aggregation charts, drill-down charts, relationship charts, multi-view dashboards, causal reasoning QA) and presents the mathematical view-extraction formula. However, none of these affordances has a measurable success criterion:
  - How many chart types should the Master Table support? All six? A minimum subset?
  - What counts as a "successful" drill-down chart? That the hierarchy has non-degenerate conditional distributions?
  - What does "causal reasoning QA" require in terms of measure DAG depth?
  - Is there an integration test that verifies these affordances end-to-end?

- **Impact:** §2.10 reads as a design rationale section, not a testable specification. Without measurable criteria, there is no way to verify that a correct Phase 2 implementation actually delivers the claimed downstream flexibility.
- **Recommendation:** Add at least one measurable criterion per affordance — e.g., "The Master Table must support at least 4 of the 6 listed chart families given any scenario with ≥2 dimension groups and ≥2 measures" — or convert §2.10 into an integration test specification with concrete assertions.

---

---

## Unified Findings Summary

| ID | Title | Severity | Spec § | Reviewer |
|----|-------|----------|--------|----------|
| A1 | `mixture` distribution family is name-only | CRITICAL | §2.1.1 | A |
| A2 | `scale` parameter on `add_measure()` undefined | MODERATE | §2.1.1 | A |
| A3 | Formula DSL is unspecified (operators, grammar, resolution) | CRITICAL | §2.1.1, §2.3 | A |
| A4 | `censoring` parameter in `set_realism()` undefined — incl. metadata/validation cross-section | MODERATE | §2.1.2, §2.6, §2.9 | A |
| A5 | Required `param_model` keys per distribution family unspecified | CRITICAL | §2.1.1, §2.3 | A |
| A6 | Per-parent dict missing-key behavior undefined | MODERATE | §2.1.1 | A |
| A7 | Multi-column `on` in `add_group_dependency` — schema ambiguous | MODERATE | §2.1.2 | A |
| A8 | `inject_pattern` `params` schema missing for 4 of 6 types | CRITICAL | §2.1.2 | A |
| A9 | Single-value categorical edge case unaddressed | MINOR | §2.1.1 | A |
| A10 | Temporal column has no explicit `group` parameter | MINOR | §2.1.1, §2.2 | A |
| A11 | Temporal predictors in `param_model` effects — missing examples/encoding detail | MODERATE | §2.1.1 | A |
| A12 | Undeclared cross-group default semantics undefined | CRITICAL | §2.2, §2.1.2 | A (post-audit) |
| A13 | Target-expression grammar for `inject_pattern` undefined | CRITICAL | §2.1.2, §2.9 | A (post-audit) |
| A14 | No security/sandbox policy for LLM-generated code | CRITICAL | §2.5, §2.7 | A (post-audit) |
| A15 | SDK API contract gaps (duplicates, mutability, reserved words) | MODERATE | §2.1.1, §2.1.2 | A (post-audit) |
| B1 | Non-daily temporal sampling semantics unspecified | MODERATE | §2.1.1, §2.4 | B |
| B2 | Pattern injection (γ) conflicts with L2 statistical validation — and post-processing contract | CRITICAL | §2.8, §2.9 | B |
| B3 | Auto-fix loop may undo injected patterns | CRITICAL | §2.9 | B |
| B4 | Full DAG construction algorithm not generalized | MODERATE | §2.4, §2.8 | B |
| B5 | Temporal predictors in stochastic measures — missing examples/encoding detail | MODERATE | §2.1.1, §2.3, §2.4 | B |
| B6 | Pattern injection mechanics unspecified for 4 of 6 types | CRITICAL | §2.8, §2.1.2 | B |
| B7 | Auto-fix seed increment doesn't actually apply parameter fixes | MODERATE | §2.9 | B |
| B8 | Topo-sort tie-breaking undermines determinism claim | MODERATE | §2.8 | B (post-audit) |
| B9 | Formula evaluation behavior under NaN/realism undefined | MODERATE | §2.1.1, §2.8 | B (post-audit) |
| B10 | Contradictory declaration handling (partial coverage) | MODERATE | §2.7, §2.1 | B (post-audit) |
| C1 | L3 validation missing for `convergence` and `seasonal_anomaly` | CRITICAL | §2.9 | C |
| C2 | L2 KS test — no minimum sample size guard | MODERATE | §2.9 | C |
| C3 | Schema metadata missing critical fields for Phase 3 | CRITICAL | §2.6 | C |
| C4 | Auto-fix strategies cover only 4 of 9+ failure modes | MODERATE | §2.9 | C |
| C5 | §2.7 and §2.9 loop composition is ambiguous | MODERATE | §2.7, §2.9 | C |
| C6 | L1 `finite_*` check conflicts with realism `missing_rate` | MODERATE | §2.9, §2.8 | C |
| C7 | `_get_measure_spec` and `iter_predictor_cells` are undefined | MODERATE | §2.9 | C |
| C8 | L2 structural validation references fields absent from metadata | CRITICAL | §2.9, §2.6 | C |
| C9 | L1 marginal validation references fields absent from metadata | CRITICAL | §2.9, §2.6 | C |
| C10 | `dominance_shift` L3 validation logic is a black box | MODERATE | §2.9 | C |
| C11 | L3 `ranking_reversal` hard-codes first dimension group | MODERATE | §2.9 | C |
| C12 | Soft-fail policy for downstream pipeline undefined | MODERATE | §2.9 | C |
| C13 | No formal metadata schema or versioning | CRITICAL | §2.6, §2.9 | C (post-audit) |
| C14 | §2.10 lacks measurable success criteria | MINOR | §2.10 | C (post-audit) |

---

### Cross-Reviewer Conflicts

**Conflict 1: Pattern completeness — A8 + B6 + C1 (agreement, not conflict)**
All three reviewers independently flagged the same root problem from different angles: A8 (params schema missing), B6 (injection algorithm missing), C1 (validation logic missing). These are three facets of one issue: 4 of 6 pattern types are specified in name only. No conflict — this is reinforcing convergence on a CRITICAL gap.

**Conflict 2: Temporal predictors — A11 vs. B5 (tension on resolution)**
Reviewer A recommends adding temporal predictor examples to the API docs. Reviewer B goes further, arguing the generation semantics and DAG representation are incomplete. The tension is whether this is an API documentation gap (A's view) or an architectural gap (B's view). **Post-audit resolution:** Both findings have been downgraded to "missing examples/encoding detail" — the underlying mechanism (intercept + effects, DAG ordering) is already sound. B5 provides the broader framing (DAG edges, encoding conventions), and A11 follows naturally as the API-facing worked example.

**Conflict 3: Auto-fix effectiveness — B3 + B7 vs. C4 (scope disagreement)**
Reviewers B3/B7 argue the auto-fix *mechanism* is broken (fixes are discarded on regeneration). Reviewer C4 argues the auto-fix *coverage* is incomplete (too few strategies). These are complementary, not contradictory — but they imply different priorities. **Resolution:** B3/B7 must be resolved first (fix the mechanism), then C4 (expand coverage). A broken mechanism cannot be improved by adding more strategies.

**Conflict 4: Metadata completeness — C3 vs. C8 vs. C9 vs. C13 (overlap)**
These four findings describe the same root cause (metadata schema is incomplete and lacks formal definition) surfaced via different symptoms (Phase 3 reconstruction, L2 KeyError, L1 KeyError, no versioning). They are not in conflict but should be resolved as a single metadata schema overhaul (C13 provides the structural fix; C3/C8/C9 provide the specific field requirements).

---

### Priority Implementation Blockers

These are the top 5 CRITICAL items that must be resolved before coding begins, ordered by dependency chain (resolving item N unblocks items below it).

**1. Schema Metadata Completeness and Formal Definition (C3 + C8 + C9 + C13)**
The metadata is the contract between *every* subsystem: the engine writes it, the validator reads it, Phase 3 consumes it. The current §2.6 example is internally inconsistent with the §2.9 validator code — the validator references `col["values"]`, `col["weights"]`, `col["formula"]`, `col["noise_sigma"]`, and `dep["conditional_weights"]`, none of which appear in the metadata. C13 adds that the metadata lacks any formal schema or versioning, making drift inevitable. **Resolve first:** define the complete, formally typed metadata schema with versioning, then all downstream implementations (validator, Phase 3) have a stable contract.

**2. Pattern Type Full Specification (A8 + B6 + C1)**
Four of six pattern types (`ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`) are specified in name only. Their params schema (A8), injection algorithm (B6), and validation logic (C1) are all missing. These three layers must be co-designed — the injection algorithm must produce a statistical signature that the validation logic can detect, and the params schema must capture the knobs for both. **Resolve second:** define each pattern type as a triple of (params schema, injection algorithm, validation check).

**3. Cross-Group Default Semantics and Target-Expression Grammar (A12 + A13)**
Two new CRITICAL findings from the post-audit. A12 (undeclared cross-group default) blocks the sampling algorithm for any scenario with 3+ dimension groups where not all pairs are explicitly declared. A13 (target grammar) blocks safe execution of pattern injection and L3 validation. **Resolve third:** these are prerequisite to safe pattern injection and correct generation.

**4. L2 Validation vs. Pattern Injection + Post-Processing Contract (B2 + B3)**
The L2 KS test runs on post-injection data against pre-injection distribution parameters. This is a structural contradiction: patterns deliberately distort the distribution, causing KS failures, which trigger auto-fixes that fight the patterns. B2's generalized framing (post-processing invariant contract) also resolves C6. **Resolve fourth** (after patterns are fully specified): define whether L2 runs pre- or post-injection, and whether pattern-target rows are excluded from statistical tests.

**5. Distribution Parameter Schema + Security Model (A5 + A1 + A14)**
The SDK cannot validate `param_model` for 6 of 8 supported families because the required parameter keys are never specified. The `mixture` family has zero specification. A14 adds that the execution environment for LLM-generated code has no security policy. **Resolve fifth:** create a distribution reference table and define the execution sandbox.

---

## Patch Log (v2 — Post-Audit)

| Finding ID | Change Type | Description |
|---|---|---|
| C.phantom_A12 | REMOVED | Deleted original finding A12 (return type for `sim.generate()`). The return type is defined in §2.8 pseudocode `-> Tuple[pd.DataFrame, dict]`; this was not a genuine gap. |
| C.phantom_B8 | REMOVED | Deleted original finding B8 (row-level vs. vectorized generation ambiguity). This is normal abstraction layering (conceptual vs. implementation), not a spec gap. |
| C.phantom_B5_A11 | DOWNGRADED | Downgraded B5 from "no generation semantics" to "missing examples/encoding detail." The intercept+effects model and DAG ordering already support temporal predictors; the gap is worked examples and encoding conventions, not architecture. Similarly downgraded A11's framing. |
| C.severity_C5 | DOWNGRADED | Downgraded C5 from CRITICAL to MODERATE. The sequential composition is inferable from §2.7 step 3; this is a retry-composition gap, not a structural impossibility. |
| C.severity_C2 | DOWNGRADED | Downgraded C2 from CRITICAL to MODERATE. The cell-sparsity issue is a real statistical-power concern but not a blocking internal inconsistency. |
| C.severity_D1 | NOTED | D1 downgrade from CRITICAL to high-MODERATE applies to the addendum document, not this file. No change here. |
| C.missed_cross_group_default | ADDED | New finding A12: Undeclared cross-group default semantics undefined (CRITICAL). When two groups have neither `declare_orthogonal` nor `add_group_dependency`, sampling behavior is ambiguous. |
| C.missed_target_expr | ADDED | New finding A13: Target-expression grammar for `inject_pattern` undefined (CRITICAL). The `target` string has no formal grammar, and `df.query()` usage creates a security surface. |
| C.missed_security_model | ADDED | New finding A14: No security/sandbox policy for LLM-generated code (CRITICAL). No import whitelist, resource limits, or execution sandbox specified. |
| C.missed_SDK_contract | ADDED | New finding A15: SDK API contract gaps — duplicate names, mutability, reserved words (MODERATE). |
| C.missed_topo_sort_stability | ADDED | New finding B8: Topo-sort tie-breaking undermines determinism claim (MODERATE). No canonical tie-breaking rule for topological sort. |
| C.missed_formula_NaN | ADDED | New finding B9: Formula evaluation behavior under NaN/realism undefined (MODERATE). Phase ordering and post-realism structural consistency unspecified. |
| C.missed_contradictory_declarations | ADDED | New finding B10: Contradictory declaration handling — partial coverage (MODERATE). Narrower than a blanket gap; §2.7 handles some conflicts, but orthogonal+dependency conflicts and weight overrides are uncovered. |
| C.missed_metadata_schema | ADDED | New finding C13: No formal metadata schema or versioning (CRITICAL). §2.6 defined by example only; no types, no required/optional, no version field. |
| C.missed_2.10_criteria | ADDED | New finding C14: §2.10 lacks measurable success criteria (MINOR). Design advantages listed but not testable. |
| C.missed_censoring_cross_section | EXTENDED | Extended A4 to cover censoring cross-section impact on metadata (§2.6) and validation (§2.9 L2 KS test, L1 finiteness). |
| C.missed_realism_marginals_contract | GENERALIZED | Generalized B2 to frame the broader post-processing contract question: should γ/δ phases be allowed to violate pre-validated properties? Links B2 and C6 as symptoms of same missing contract. |
| A.§2.9_absent_convergence_seasonal | CONFIRMED | C1 already captures this finding (2 of 6 pattern types have no L3 validation). Added audit-confirmation note to C1 body text. |
| — | UPDATED | Unified Findings Summary table updated: removed A12/B8 rows; added A12–A15, B8–B10, C13–C14 rows; updated severity for C2/C5; updated titles for A4/A11/B2/B5. |
| — | UPDATED | Cross-Reviewer Conflicts section updated: Conflict 2 reflects post-audit downgrade consensus; Conflict 4 expanded to include C13. |
| — | UPDATED | Priority Implementation Blockers reordered: #1 now includes C13; new #3 for A12+A13; renumbered #4/#5 accordingly. |
