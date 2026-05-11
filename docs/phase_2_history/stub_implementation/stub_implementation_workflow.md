# Stub Implementation Workflow

Each step is one Claude Code conversation. Run in order. Every step leaves the
codebase green — you can stop after any step.

References (read all three before any step):
- Analysis: `pipeline/phase_2/docs/stub_analysis/stub_gap_analysis.md`
- Adopted decisions (authoritative): `pipeline/phase_2/docs/stub_analysis/stub_blocker_decisions.md`
- Adversarial review (issues to consult before implementing): `pipeline/phase_2/docs/stub_analysis/stub_review.md`

Note: line ranges in the analysis (e.g. `~L57-63`) were captured 2026-04-30
and may have drifted. Verify with grep before editing.

---

## Already shipped (verified in current source; do NOT re-run)

- **IS-5 (was Step 0)** — `scale=` stripped from spec. `grep scale phase_2.md` returns no matches.
- **DS-1 (was Step 1)** — `inject_censoring` at `engine/realism.py:64+`; `CensoringSpec` at `types.py:364`; full `set_realism` schema validation at `sdk/relationships.py:315-345`; prompt advertises schema at `orchestration/prompt.py:70-72`.
- **DS-2 `ranking_reversal` (was Step 2)** — in `VALID_PATTERN_TYPES`; `inject_ranking_reversal` at `engine/patterns.py:374`; prompt example at `orchestration/prompt.py:217`.
- **IS-2 + `dominance_shift` (was Step 3)** — `check_dominance_shift` fully implemented at `validation/pattern_checks.py:205+`; `inject_dominance_shift` at `engine/patterns.py:245`; in `VALID_PATTERN_TYPES`; prompt example at `orchestration/prompt.py:223`.

The first active step is **Step 4** (IS-3 + convergence). Step numbers below
are preserved (4, 5, 6, 7, 8a, 8b) so they stay aligned with the analysis
tier numbers.

---

## Step 4: IS-3 + convergence injector

**Plan mode:** Yes — same multi-file pattern as the shipped IS-2 work.

```
Implement IS-3 (convergence validation) and the convergence injector from DS-2
per the solution proposals in
pipeline/phase_2/docs/stub_analysis/stub_gap_analysis.md sections [IS-3] and [DS-2],
and the adopted decisions in
pipeline/phase_2/docs/stub_analysis/stub_blocker_decisions.md §IS-3 and §DS-2.

These must ship together.

Summary of changes:

1. In `pipeline/phase_2/validation/pattern_checks.py`:
   - Replace the `check_convergence` stub at ~L315 (verify with grep — line
     numbers in the analysis may have drifted).
   - Algorithm (interpretation (b) from the analysis): resolve entity_col
     and temporal_col, split at params["split_point"] or temporal median,
     compute per-entity mean of pattern["col"] on each side, compare
     variance-of-means: reduction = (early_var - late_var) / early_var.
     Pass if reduction >= params.get("reduction", 0.3).
   - Reuse `_find_temporal_column` and `_resolve_first_dim_root`.
     `_resolve_first_dim_root` already exists from the IS-2 work
     (verify at validation/pattern_checks.py:~L109) — do NOT redefine.

2. In `pipeline/phase_2/engine/patterns.py`:
   - Add `inject_convergence(df, pattern, columns, meta)`.
     Algorithm: resolve temporal_col, normalize time to [0, 1], for each
     target row compute factor = normalized_time * pull_strength, blend
     df[col] toward global_mean: val = val * (1 - factor) + global_mean * factor.
     This creates increasing homogeneity over time.
   - Update dispatch in `inject_patterns` — currently the
     NotImplementedError block covers ("convergence", "seasonal_anomaly");
     route "convergence" to the new function and leave seasonal_anomaly in
     the NotImplementedError branch (Step 5 finishes that one).

3. In `pipeline/phase_2/sdk/relationships.py`:
   - Add `"convergence"` to `VALID_PATTERN_TYPES`.
   - Add `"convergence": frozenset()` to `PATTERN_REQUIRED_PARAMS`
     (all params optional: split_point, entity_col, reduction threshold).

4. In `pipeline/phase_2/orchestration/prompt.py`:
   - Add `"convergence"` to the advertised pattern types list.
   - Add a usage example next to the existing ranking_reversal /
     dominance_shift examples.

5. Tests:
   - Round-trip: inject → validate → passes.
   - Stable group spread across periods → validator returns passed=False.
   - Single entity (only one group) → graceful fail with detail.
   - Missing temporal column → graceful fail.
   - Constant column (early_var == 0) → graceful fail.

Run `conda run -n chart pytest pipeline/phase_2/tests/ -x`.
```

---

## Step 5: IS-4 + seasonal_anomaly injector

**Plan mode:** Yes — completes DS-2.

```
Implement IS-4 (seasonal_anomaly validation) and the seasonal_anomaly injector
from DS-2 per the solution proposals in
pipeline/phase_2/docs/stub_analysis/stub_gap_analysis.md sections [IS-4] and [DS-2],
and the adopted decisions in
pipeline/phase_2/docs/stub_analysis/stub_blocker_decisions.md §IS-4 and §DS-2.

These must ship together. After this step, all 4 deferred pattern types are
restored and DS-2 is fully resolved.

Note the params contract (resolves an apparent contradiction between blocker
doc §IS-4 and §4.2):
- The SDK gate (PATTERN_REQUIRED_PARAMS) marks `anomaly_window` REQUIRED at
  declaration time — `frozenset({"anomaly_window", "magnitude"})`.
- The validator's "default to last 10% of temporal range" fallback is
  defensive only; under normal flow the SDK gate guarantees `anomaly_window`
  is present.

Summary of changes:

1. In `pipeline/phase_2/validation/pattern_checks.py`:
   - Replace the `check_seasonal_anomaly` stub at ~L341 (verify with grep).
   - Algorithm (interpretation (a) from the analysis): resolve temporal_col,
     determine anomaly_window from params["anomaly_window"] or default to
     last 10% of temporal range, compute baseline mean+std from
     out-of-window rows, z = |window_mean - baseline_mean| / baseline_std,
     pass if z >= params.get("z_threshold", 1.5).
   - Reuse `_find_temporal_column`.

2. In `pipeline/phase_2/engine/patterns.py`:
   - Add `inject_seasonal_anomaly(df, pattern, columns, meta)`.
     Algorithm: resolve temporal_col, identify rows in
     params["anomaly_window"], scale target values by (1 + magnitude).
     Mirror `inject_trend_break`'s structure.
   - Update dispatch in `inject_patterns`. After this step the
     NotImplementedError branch for ("convergence", "seasonal_anomaly")
     should be fully replaced with explicit dispatch to all 4 new injectors.

3. In `pipeline/phase_2/sdk/relationships.py`:
   - Add `"seasonal_anomaly"` to `VALID_PATTERN_TYPES`.
   - Add `"seasonal_anomaly": frozenset({"anomaly_window", "magnitude"})`
     to `PATTERN_REQUIRED_PARAMS`.

4. In `pipeline/phase_2/orchestration/prompt.py`:
   - Add `"seasonal_anomaly"` to the advertised pattern types list.
   - Add a usage example.
   - Verify that all 6 pattern types are now listed (outlier_entity,
     trend_break, ranking_reversal, dominance_shift, convergence,
     seasonal_anomaly).

5. Tests:
   - Round-trip: inject → validate → passes.
   - Stable window mean ≈ baseline → passed=False.
   - Empty window → graceful fail.
   - Missing temporal column → graceful fail.
   - Constant column → graceful fail.
   - Integration: all 6 pattern types declared in one script → no errors.

Run `conda run -n chart pytest pipeline/phase_2/tests/ -x`.
```

---

## Step 6: IS-1 + DS-3 — Mixture sampling + KS test

**Plan mode:** Yes — refactors existing sampler code, touches 4+ files,
tightly coupled pair.

```
Implement IS-1 (mixture distribution sampling) and DS-3 (mixture KS test)
per the solution proposals in
pipeline/phase_2/docs/stub_analysis/stub_gap_analysis.md sections [IS-1] and [DS-3],
and the adopted decisions in
pipeline/phase_2/docs/stub_analysis/stub_blocker_decisions.md §IS-1 and §DS-3.

These must ship together — the sampler and the KS test must agree on the
mixture CDF construction.

Summary of changes:

1. In `pipeline/phase_2/types.py`:
   - Add `MixtureComponent(TypedDict)` with fields: `family: str`,
     `weight: float`, `param_model: dict[str, Any]`.

2. In `pipeline/phase_2/engine/measures.py`:
   - Refactor `_sample_stochastic` (~L387-403): extract the family-dispatch
     logic into a reusable `_sample_family(family, params, n_rows, rng)`
     helper. The existing if/elif chain for gaussian/lognormal/gamma/etc
     moves into this helper.
   - Add `_sample_mixture(col_name, col_meta, rows, rng, overrides)`.
     Algorithm: extract components list + weights from param_model,
     normalize weights, assign per-row component via rng.choice, for each
     component call `_compute_per_row_params` + `_sample_family` on the
     masked subset.
   - Replace the NotImplementedError block at ~L360-366 with a dispatch
     to `_sample_mixture`.
   - Caveat (from stub_review.md §IS-1 issue #2): when constructing
     per-component sub_meta for `_compute_per_row_params`, verify whether
     the helper requires `measure_type: "stochastic"` and/or `name`. The
     minimal `{family, param_model}` shape may be insufficient — match
     the full col_meta keys if needed.

3. In `pipeline/phase_2/sdk/validation.py` (validate_param_model lives here,
   line ~311):
   - Extend `validate_param_model` to handle `family == "mixture"`:
     validate `components` is a non-empty list, each component has `family`
     (in SUPPORTED_DISTRIBUTIONS minus "mixture"), `weight` (positive float),
     and `param_model` (validated recursively per component family).

4. In `pipeline/phase_2/validation/statistical.py`:
   - Replace the DS-3 stub at ~L259-264 in `check_stochastic_ks`.
   - Build a mixture CDF: for each component, build the per-family CDF
     (reusing existing `_expected_cdf` logic), then combine as
     cdf_mixture(x) = sum(weight_k * cdf_k(x)). Use a `_MixtureFrozen`
     adapter wrapping scipy distributions.
   - Run KS test against the mixture CDF.

5. Autofix decision: opt mixture out of the `widen_variance` strategy
   (simplest — add `if family == "mixture": return overrides` early exit
   in the widen_variance strategy). Document this as a known limitation.
   The autofix opt-out inflates effective scope beyond the ~300 LOC pair
   estimate. Plan accordingly.

6. Tests:
   - 2-component gaussian mixture with weights [0.6, 0.4] and disparate
     means → empirical mean ≈ weighted mean within 5%.
   - 3-component mixture → samples pass scipy mixture-CDF KS test.
   - Weight normalization: [0.3, 0.2] auto-normalized to [0.6, 0.4].
   - Invalid mixture param_model (missing components, empty list, nested
     mixture) → raises with clear message.
   - KS test passes for correctly sampled mixture, fails for wrong
     distribution.
   - Existing non-mixture sampling tests still pass.

Run `conda run -n chart pytest pipeline/phase_2/tests/ -x`.
```

---

## Step 7: DS-4 — Multi-column group dependency

**Plan mode:** Yes — touches SDK, engine sampler, and validation across 3+ files.

```
Implement DS-4 (multi-column group dependency) per the solution proposal in
pipeline/phase_2/docs/stub_analysis/stub_gap_analysis.md section [DS-4]
and the adopted decisions in
pipeline/phase_2/docs/stub_analysis/stub_blocker_decisions.md §DS-4.

Summary of changes:

1. In `pipeline/phase_2/sdk/relationships.py::add_group_dependency` (~L101-213):
   - Remove the `len(on) != 1` NotImplementedError guard (~L126-130).
   - Add `_validate_and_normalize_nested_weights(on, conditional_weights,
     columns)` that recursively walks the nested dict: depth == len(on),
     each level's keys must cover all values of the corresponding `on[i]`
     column, leaf level is {child_val: weight} dicts that get normalized.
   - Call `dag.check_root_dag_acyclic` once per parent in `on` (already
     handles single edges; call in a loop).
   - Validate no orthogonal conflicts between child_root and any parent
     in `on`.

2. In `pipeline/phase_2/engine/generator.py` (group-dep sampling step):
   - Extend the flat `cw[parent_val]` lookup to an N-deep walk:
     for each row, walk `on[0] → on[1] → ... → on[N-1]` through the
     nested dict to reach the leaf `{child_val: weight}`, then sample.
   - The analysis provides a `_sample_multi_parent_dep` helper for this.

3. In `pipeline/phase_2/validation/statistical.py::max_conditional_deviation`
   (~L24-55):
   - Extend the deviation comparison to walk N-deep nested dicts. For each
     unique combination of parent values, compare observed vs declared
     child distribution.

4. Tests:
   - 2-parent dependency with full Cartesian coverage → declaration
     succeeds; engine sampling reproduces declared conditional within
     10% deviation.
   - Missing combination at depth 1 → ValueError listing the missing key.
   - Missing inner combination at a leaf → ValueError with full path.
   - Existing single-column group-dep tests still pass (backward compat:
     depth=1 must produce identical results).
   - L2 group-dep deviation check correctly identifies divergent
     observations on multi-parent specs.

Run `conda run -n chart pytest pipeline/phase_2/tests/ -x`.
```

---

## Step 8: IS-6 — Multi-error + token budget (defer)

**Plan mode:** Yes — large refactor, many files.

Only implement when retry-loop overhead is measured to be a real bottleneck.
Ship the two sub-features as separate conversations if you proceed.

### Step 8a: Token budget (smaller, ship first)

```
Implement the token-budget half of IS-6 per the solution proposal in
pipeline/phase_2/docs/stub_analysis/stub_gap_analysis.md section [IS-6]
and the adopted decisions in
pipeline/phase_2/docs/stub_analysis/stub_blocker_decisions.md §IS-6.

Summary of changes:

1. In `pipeline/phase_2/orchestration/llm_client.py`:
   - Add `TokenUsage(NamedTuple)` with fields: `prompt_tokens: int`,
     `completion_tokens: int`, `total_tokens: int`.
   - Add `LLMResponse(NamedTuple)` with fields: `code: str`,
     `token_usage: TokenUsage | None`.
   - Update `LLMClient.generate_code` to return `LLMResponse` instead of
     a raw string. Extract token counts from each provider's response
     (OpenAI: response.usage, Gemini: response.usage_metadata). Return
     `token_usage=None` if provider doesn't report counts.

2. In `pipeline/phase_2/orchestration/sandbox.py::run_with_retries` (~L689):
   - Add `token_budget: int | None = None` parameter.
   - Track cumulative `tokens_used` across attempts.
   - After each LLM call, add response token usage to cumulative total.
   - If `token_budget` is set and `tokens_used >= token_budget`, return
     early with `SkipResult` and reason `"token_budget_exceeded"`.
   - Default `None` → no behavior change (backward compat).

3. Tests:
   - Mock LLMClient returning known token counts → retry loop terminates
     early when budget hit.
   - `token_budget=None` → identical behavior to current.
   - Provider returning no token counts → budget degrades gracefully
     (counts as 0, never triggers early exit).

Run `conda run -n chart pytest pipeline/phase_2/tests/ -x`.
```

### Step 8b: Multi-error collection

```
Implement the multi-error half of IS-6 per the solution proposal in
pipeline/phase_2/docs/stub_analysis/stub_gap_analysis.md section [IS-6]
and the adopted decisions in
pipeline/phase_2/docs/stub_analysis/stub_blocker_decisions.md §IS-6.

Summary of changes:

1. In `pipeline/phase_2/exceptions.py`:
   - Add `MultiValidationError(Exception)` that wraps a `list[Exception]`
     and formats all errors in its string representation.

2. In `pipeline/phase_2/sdk/validation.py`:
   - Add `ValidationContext` class with `accumulate: bool`, `errors: list`,
     `report(exc)` method (appends if accumulating, raises if not),
     and `raise_if_any()` that raises `MultiValidationError` if errors
     collected.

3. In `pipeline/phase_2/sdk/columns.py`, `sdk/relationships.py`,
   `sdk/dag.py`, `sdk/validation.py`:
   - At each `raise` site (~10 total), convert to `ctx.report(exc)` when
     a ValidationContext is active. When no context is provided, preserve
     current raise-on-first behavior (backward compat).

4. In `pipeline/phase_2/orchestration/sandbox.py`:
   - Add `multi_error: bool = False` parameter to `run_with_retries`.
   - When enabled, pass a `ValidationContext(accumulate=True)` into the
     sandbox execution, catch `MultiValidationError`, and format all
     errors into the feedback message for the LLM.
   - `multi_error=False` (default) → identical behavior to current.

5. Tests:
   - Script with 3 simultaneous SDK errors + multi_error=True → one retry
     attempt with all 3 errors in feedback.
   - Script with 1 error + multi_error=True → identical to current.
   - multi_error=False → identical behavior (backward compat).

Run `conda run -n chart pytest pipeline/phase_2/tests/ -x`.
```
