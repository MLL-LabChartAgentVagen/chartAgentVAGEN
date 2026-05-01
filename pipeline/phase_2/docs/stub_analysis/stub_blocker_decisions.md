# Stub Blocker Decisions

**Status:** All proposed solutions in `stub_gap_analysis.md` adopted as-is.
**Date:** 2026-04-30
**Source analysis:** [stub_analysis/stub_gap_analysis.md](stub_analysis/stub_gap_analysis.md) (full reasoning, alternatives considered, line-level code excerpts)
**Adversarial review:** [stub_analysis/stub_review.md](stub_analysis/stub_review.md) (issues flagged in the analysis — consult before implementation)
**Sibling decision record:** [phase_2_spec_decisions.md](phase_2_spec_decisions.md) (parallel summary; cross-checked, kept consistent on factual specifics)

## Purpose

`stub_gap_analysis.md` enumerated 10 stubs (IS-1 … IS-6, DS-1 … DS-4) and
for each one paired a *blocker question* with a *proposed solution*. The
Phase C table at the end of that document compresses every blocker to a
single line, which is enough to plan but not enough to execute or
re-load context months later.

This document records the **adopted decisions** with the schema,
formula, code-span, and dependency context preserved inline, so it can
be read standalone. When something is unclear here, fall back to the
matching section of `stub_gap_analysis.md`.

The decisions split three ways:
- **Seven stubs** require a spec extension to be merged into
  [phase_2.md](phase_2.md) before implementation can land. Those spec
  extensions consolidate into 4 themes (see §4).
- **One stub** (IS-5) requires only a docs-strip — no behavioral
  decision.
- **One stub** (IS-6) is gated on an empirical A/B test, not on the
  spec.
- **One stub** (DS-3) inherits its decision from another stub (IS-1).

---

## §1 Quick-reference matrix

| Stub  | Decision (one line) | Scope | Spec change required | Tier |
|-------|---------------------|-------|----------------------|------|
| IS-1  | Implement mixture sampling using component-`param_model` schema (interpretation a) | Medium (~170 LOC) | Theme 1 (mixture schema) | 5 |
| IS-2  | Implement `dominance_shift` validator as rank-reversal across temporal split | Small (~110 LOC) | Theme 2 (op defs) | 4 |
| IS-3  | Implement `convergence` validator as group-mean variance reduction | Small (~90 LOC) | Theme 2 (op defs) | 4 |
| IS-4  | Implement `seasonal_anomaly` validator as window-vs-baseline z-score | Small (~95 LOC) | Theme 2 (op defs) | 4 |
| IS-5  | **Do not restore** `scale=` kwarg — strip vestigial signature from spec | Trivial (docs only) | None (docs strip only) | 1 |
| IS-6  | Defer; if shipped, token-budget half goes first | Large (~340 LOC combined) | Empirical (A/B test) | 7 |
| DS-1  | Implement censoring as per-column NaN-marker injection | Small (~110 LOC) | Theme 3 (censoring schema) | 2 |
| DS-2  | Implement 4 pattern injectors; `ranking_reversal` first | Large (~430 LOC) | Theme 2 (op defs, paired) | 3 (rank rev) / 4 (rest) |
| DS-3  | Implement mixture KS test using `_MixtureFrozen` adapter | Small (~130 LOC) | Inherits IS-1 (Theme 1) | 5 |
| DS-4  | Implement multi-column `conditional_weights` as nested dict (interp. a) | Medium (~190 LOC) | Theme 4 (nested weights) | 6 |

Tier numbers refer to the recommended sequencing in §5.

---

## §2 Independent stubs (IS-1 … IS-6)

### [IS-1] Mixture distribution sampling

**Decision:** Adopt interpretation **(a)** — each mixture component
carries its own `param_model` (intercept + effects); component weights
are constants and auto-normalized to sum to 1.0.

#### Blocker resolved
- How does mixture interact with predictor effects? Three readings:
  (a) each component carries its own `param_model` with
  `intercept + effects`, weights are constants;
  (b) component params are constants but weights vary by predictor;
  (c) both vary.
- Are component families restricted to continuous-only, or is mixed-type
  mixture (e.g. gaussian + poisson) allowed?

#### Why this answer
Interpretation (a) is the minimal extension of the existing
`param_model` shape used by every non-mixture stochastic measure — the
existing `_compute_per_row_params` helper at
[engine/measures.py:406](../../engine/measures.py#L406) is reused
per-component without modification. Interpretations (b) and (c) require
new mechanics (predictor-varying weights) with no narrative use case.
Component families are unrestricted by this decision; mixed-type
mixtures fall through to "no expected CDF" in the KS test (handled
gracefully by DS-3).

#### Specifics locked in
```
# Mixture param_model schema
{
    "components": [
        {"family": str, "weight": float, "param_model": {...}},
        ...
    ]
}
```
- Each component's `param_model` follows the same intercept+effects
  shape as a non-mixture stochastic measure.
- Weights are auto-normalized to sum to 1.0 (e.g. `[0.3, 0.2]` →
  `[0.6, 0.4]`).
- Sampling: pick component index per row using normalized weights, then
  delegate per-row params to `_compute_per_row_params`.
- **New type** added to `types.py`:
  ```python
  class MixtureComponent(TypedDict):
      family: str
      weight: float
      param_model: dict[str, Any]
  ```
- **Autofix decision (paired with DS-3):** the existing `ks_*` autofix
  strategy (`widen_variance`) indexes a single `sigma` field per
  measure, so it doesn't naturally apply to mixtures (each component
  has its own `sigma`). **Adopt interpretation (a) — opt mixture out
  of `widen_variance`** (simplest path; refuses to autofix and
  surfaces the validation failure). Interpretations (b) widen the
  dominant-weight component and (c) widen all proportionally are
  rejected for added complexity with no narrative justification.

#### Files affected
- Stub site: [engine/measures.py:360-366](../../engine/measures.py#L360-L366) (replace `NotImplementedError`)
- Dispatch: [engine/measures.py:329](../../engine/measures.py#L329) (`_sample_stochastic` — add `family == "mixture"` branch)
- Schema validation: [sdk/columns.py](../../sdk/columns.py) (`validate_param_model` — add mixture schema validator)
- Reused: [engine/measures.py:406](../../engine/measures.py#L406) (`_compute_per_row_params` — call per-component, no edits)
- New type: `types.py` (`MixtureComponent` TypedDict)
- Autofix: `validation/autofix.py` (or wherever `widen_variance` lives) — add `family == "mixture"` opt-out

#### Dependencies
- **Blocks:** DS-3 (KS test cannot validate what cannot be sampled).
- **Blocked by:** Spec Theme 1 (mixture `param_model` schema).
- **Co-implement with:** DS-3. Sampler and CDF must agree on the same
  schema; ship in one PR.

#### Scope
**Medium.** Sampler ~50 LOC + validator schema ~30 LOC + type defs
~10 LOC + tests ~80 LOC ≈ **170 LOC**. Pairs with DS-3 to ~300 LOC
combined.

#### Spec change required
Theme 1 (see §4.1). The spec must publish the mixture component schema,
the auto-normalization rule, and clarify the family-restriction
position (none — KS test degrades gracefully on mixed-type).

#### Verification
- 2-component gaussian mixture, weights `[0.6, 0.4]`, disparate means →
  empirical mean ≈ weighted mean of component means within 5%.
- 3-component mixture with constant per-component params → samples pass
  scipy mixture-CDF KS test.
- Mixture with predictor-varying components → per predictor cell,
  samples match expected mixture distribution.
- Weight normalization: `[0.3, 0.2]` produces same draws as `[0.6, 0.4]`.
- Validator rejects empty/malformed `components` list with clear error.

---

### [IS-2] Dominance shift validation

**Decision:** Adopt interpretation **(a)** — rank reversal of a target
entity across a temporal split. Default minimum rank change is 1 and is
configurable via `params["rank_change"]`.

#### Blocker resolved
- Operational definition of "dominance shift". Candidates:
  (a) rank reversal of target entity across temporal split (target
  moves from #1 to #N or vice versa);
  (b) mean/sum crossover (entity A > B before, A < B after);
  (c) market-share crossover.
  Source TODO points to (a).
- Pass threshold — minimum rank change required (default 1?
  configurable via `params.rank_change`?).

#### Why this answer
The TODO comment in the existing stub already pointed at (a). The shape
mirrors `check_trend_break`, the closest implemented analog (also a
temporal-split pattern check at ~80 LOC). Interpretations (b) and (c)
collapse to special cases of (a) at rank 1, so (a) is strictly more
general at no extra cost.

#### Specifics locked in
```
# Pass condition
|rank_after - rank_before| >= params.get("rank_change", 1)
```
- Helper `_resolve_first_dim_root` extracts entity column from filter
  spec.
- Reuses `_find_temporal_column` already at
  [validation/pattern_checks.py:94](../../validation/pattern_checks.py#L94).

#### Files affected
- Stub site: [validation/pattern_checks.py:189-213](../../validation/pattern_checks.py#L189-L213) (replace hard-coded `passed=True`).
- Dispatch: `validation/validator.py` already routes `"dominance_shift"`
  type — only the function body changes.

#### Dependencies
- **Blocks:** Nothing directly.
- **Blocked by:** Spec Theme 2 (op def + params contract); DS-2 for
  end-to-end exercise (injector and validator must share the same op
  def).

#### Scope
**Small.** Function body ≈ 45 LOC + helper ≈ 8 LOC + tests ≈ 60 LOC
≈ **110 LOC**.

#### Spec change required
Theme 2 (see §4.2). The spec must publish the rank-reversal formula,
the `params["rank_change"]` default, and the "missing temporal column"
failure mode.

#### Verification
- Inject synthetic before/after means where target rank shifts 1 → 3 →
  `passed=True`.
- Stable rank across split → `passed=False`.
- Missing `entity_filter` / `split_point` → `passed=False` with clear
  detail.
- Target entity absent on one side of the split → `passed=False`.
- Missing temporal column → `passed=False`.

---

### [IS-3] Convergence validation

**Decision:** Adopt interpretation **(b)** — variance of group means
decreases over time. Split point is optional; defaults to the temporal
median (`tval.quantile(0.5)`). Default reduction threshold is 30%,
configurable via `params["reduction"]`.

#### Blocker resolved
- Operational definition. Candidates:
  (a) variance of `pattern["col"]` decreases over time globally;
  (b) variance of group means decreases over time (groups becoming
  homogeneous);
  (c) specific pair of entities' means approach monotonically.
  Chart-storytelling intent points to (b).
- Comparison reference — early-half vs late-half? Sliding window?
  Default to single midpoint split.
- Threshold for "convergence happened". Reasonable default:
  `late_var <= early_var × (1 - 0.3)` (30% reduction).

#### Why this answer
Interpretation (b) is what most narrative charts mean by "groups
converge over time" and is what DS-2's `convergence` injector
naturally produces (pull target toward global mean over normalized
time). The midpoint split mirrors IS-2's split logic and reuses the
same helpers. Interpretation (a) is too generic (passes for any
high-variance dataset that settles); (c) requires entity pair
specification with no narrative use case.

#### Specifics locked in
```python
# Pass condition
reduction = (early_var - late_var) / early_var
reduction >= params.get("reduction", 0.3)

# Split point: optional, defaults to temporal median
sp = pd.to_datetime(params["split_point"]) if params.get("split_point") else tval.quantile(0.5)
```
- Optional `params["split_point"]`; default is `tval.quantile(0.5)`
  (temporal median of the data, not arithmetic midpoint of
  `[tmin, tmax]`).
- Optional `params["entity_col"]`; falls back to first dim-group
  hierarchy root via `_resolve_first_dim_root` (helper added in IS-2).
- Edge: each side must have ≥ 2 entities, else `passed=False`.
- Edge: `early_var == 0` → `passed=False`.

#### Files affected
- Stub site: [validation/pattern_checks.py:216-239](../../validation/pattern_checks.py#L216-L239) (replace hard-coded `passed=True`).
- Reuses helpers from IS-2 (`_find_temporal_column`,
  `_resolve_first_dim_root`).

#### Dependencies
- **Blocks:** Nothing directly.
- **Blocked by:** Spec Theme 2 (more critical than IS-2 because the
  spec offers zero algorithmic guidance for convergence); DS-2 for
  end-to-end exercise.

#### Scope
**Small.** Body ≈ 40 LOC + tests ≈ 50 LOC ≈ **90 LOC**.

#### Spec change required
Theme 2 (see §4.2). The spec must publish the variance-reduction
formula, the 30% default threshold, and the "single entity / constant
column" graceful-fail behavior.

#### Verification
- Late-period group means uniform, early-period spread → `passed=True`.
- Stable group spread across periods → `passed=False`.
- Single entity (only one group) → graceful fail with detail.
- Missing temporal column → graceful fail.
- Constant column (`early_var == 0`) → graceful fail.

---

### [IS-4] Seasonal anomaly validation

**Decision:** Adopt interpretation **(a)** — window-vs-baseline z-score.
`anomaly_window=[start, end]` is **optional**; when omitted, defaults
to the last 10% of the temporal range (`[tmin + (tmax - tmin) * 0.9, tmax]`).
Default threshold `z >= 1.5`, configurable via `params["z_threshold"]`.

#### Blocker resolved
- Operational definition. Candidates:
  (a) values inside an explicit `anomaly_window` deviate from
  out-of-window baseline;
  (b) STL decomposition with residual outliers;
  (c) period-aware z-score on detrended series.
  (a) is simplest and matches narrative-driven framing.
- Params contract — `anomaly_window=[start, end]` required, or
  inferable (e.g. last 10% of temporal range)?
- Pass threshold — reasonable default `z >= 1.5`.

#### Why this answer
Narrative charts call out specific anomaly windows ("sales spiked
during the 2024 holiday season"); they don't decompose seasonality
algorithmically. (a) mirrors `check_outlier_entity` (~70 LOC) — same
shape, time-window mask instead of entity mask. (b) and (c) require
seasonal-period inference machinery the codebase doesn't have. The
narrative-driven framing usually carries an explicit window, but a
"last 10%" fallback is provided as a sensible default for the case
where the LLM declares a `seasonal_anomaly` pattern without naming a
specific window — keeps the validator usable in that path rather than
hard-failing.

#### Specifics locked in
```python
# Pass condition
z = |window_mean - baseline_mean| / baseline_std
z >= params.get("z_threshold", 1.5)

# Window: optional, defaults to last 10% of temporal range
window = params.get("anomaly_window")
if window:
    win_start, win_end = pd.to_datetime(window[0]), pd.to_datetime(window[1])
else:
    tmin, tmax = tval.min(), tval.max()
    win_start, win_end = tmin + (tmax - tmin) * 0.9, tmax
```
- `anomaly_window=[start, end]` is **optional**; default is the last
  10% of the temporal range.
- Reuses `_find_temporal_column`.
- Edges: empty window, `len(baseline) < 2`, `baseline_std == 0` → all
  return `passed=False` with a clear `detail`.

#### Files affected
- Stub site: [validation/pattern_checks.py:242-265](../../validation/pattern_checks.py#L242-L265) (replace hard-coded `passed=True`).

#### Dependencies
- **Blocks:** Nothing directly.
- **Blocked by:** Spec Theme 2 (op def + `anomaly_window` params
  contract); DS-2 for end-to-end exercise.

#### Scope
**Small.** Body ≈ 45 LOC + tests ≈ 50 LOC ≈ **95 LOC**.

#### Spec change required
Theme 2 (see §4.2). The spec must publish the z-score formula, the
`anomaly_window` shape (`[start, end]`, optional with last-10%
fallback), and the 1.5 default threshold.

#### Verification
- Window with elevated mean → `passed=True`.
- Stable window mean ≈ baseline → `passed=False`.
- Empty window → graceful fail.
- Missing temporal column → graceful fail.
- Constant column → graceful fail.

---

### [IS-5] `scale=` kwarg on `add_measure`

**Decision:** **Do not restore the kwarg.** Strip the vestigial
`scale=None` signature from `phase_2.md` §2.1.1 (around L51) and
§2.5 (around L287) so the spec, prompt, and SDK are consistent.

#### Blocker resolved
- The spec gives no behavioral content for `scale=`; any meaning would
  be a new proposal, not a reading. Two candidates:
  (a) per-family enum hint (`scale="log"` → mu is log-scale);
  (b) post-sampling transform.
  Neither is supported by spec prose; both are fresh design.
- Architectural: does restoring `scale` actually pull weight, given
  that lognormal already encodes log-scale via family choice?

#### Why this answer
There is no behavioral claim to lock in — the spec never described what
`scale` does. The current state (kwarg absent from SDK; raises
`TypeError` if passed) is the safest configuration. Restoring would
require defining new behavior with no narrative motivation, doubling
the spec surface around stochastic distributions, and creating
redundancy with family choice (lognormal already encodes log-scale).
The vestigial signature line in the spec is a pure documentation bug.

#### Specifics locked in
N/A — no schema or algorithm. The action is removing two lines from
`phase_2.md`.

#### Files affected
- Spec strip: `phase_2.md` §2.1.1 (around L51) and §2.5 (around L287).
- No code changes.
- SDK already correct: [sdk/columns.py:214-250](../../sdk/columns.py#L214-L250) (kwarg already removed; raises `TypeError` on use).
- Prompt already correct: [orchestration/prompt.py:53-54](../../orchestration/prompt.py#L53-L54) (no longer documents `scale`).

#### Dependencies
- **Blocks:** Nothing.
- **Blocked by:** Nothing — purely a docs-alignment task.

#### Scope
**Trivial.** Two-line spec edit.

#### Spec change required
None beyond removing the vestigial signature (this *is* the change).
Does not consume any of the 4 Theme-level spec extensions.

#### Verification
- Existing `test_add_measure_rejects_scale_kwarg` continues to verify
  `TypeError`.
- Add a docs-audit test asserting that prompt and spec §2.5 advertise
  the same arg list.

---

### [IS-6] M3 multi-error feedback + token budget

**Decision:** **Defer.** If shipped, ship the token-budget half first
(smaller blast radius, no SDK refactor). Multi-error collection waits
on an A/B test of LLM efficacy.

#### Blocker resolved
- Architectural: does multi-error feedback help or confuse the LLM?
  Empirical question — smaller models often degrade; capable models
  benefit. Needs A/B test.
- Architectural: is token budget per-attempt or per-scenario?
  Per-scenario is more useful but requires cumulative tracking.
- Operational: how does the budget read token counts from `LLMClient`?
  Current interface varies per provider.

#### Why this answer
Both sub-features are pure operational optimizations not in spec —
nothing else in the inventory blocks on them. Multi-error feedback may
actively harm weaker LLMs by overloading the prompt; without an A/B
test we'd be guessing. Token budget is a cleaner standalone change
(one counter around the retry loop, graceful degradation when the
client doesn't expose token counts) and can ship independently.
Sequencing: token-budget can land any time; multi-error waits.

#### Specifics locked in (if/when implemented)
- **Multi-error collection:** opt-in `ValidationContext(accumulate=True)`
  that accumulates errors instead of raising; collects all validation
  errors in one pass for batched LLM feedback. `accumulate=False`
  preserves current raise-on-first behavior for backward compat.
- **Token budget granularity: per-scenario, cumulative across retries.**
  The counter lives around the retry loop and accumulates
  `response.token_usage.total_tokens` after each attempt; skips when
  the cumulative total exceeds `token_budget`. *Not* per-attempt —
  per-attempt would defeat the purpose (no protection against runaway
  scenarios). `token_budget=None` means no enforcement (default).
- Graceful degradation: when `LLMClient` doesn't expose token counts
  (mock client, older provider), the counter treats each call as 0
  tokens and the budget never trips.
- New types: `MultiValidationError(list[Exception])` exception;
  structured `LLMResponse(NamedTuple)` carrying
  `TokenUsage(NamedTuple)` (replaces current raw-string return).

#### Files affected
- TODO comment site: [sdk/simulator.py:32-36](../../sdk/simulator.py#L32-L36) (capability absence, not `NotImplementedError`).
- Retry loop: [orchestration/sandbox.py:~657](../../orchestration/sandbox.py#L657) (`run_with_retries`).
- New: `sdk/validation.py::ValidationContext`, `exceptions.py::MultiValidationError`.
- Modified: `orchestration/llm_client.py::LLMClient.generate_code` (return structured `LLMResponse` with `token_usage`).
- Refactored: ~10 raise sites in `sdk/*.py` (convert to `ctx.report(exc)`).

#### Dependencies
- **Blocks:** Nothing.
- **Blocked by:** A/B test on multi-error efficacy (multi-error half
  only); `LLMClient` API exposing token counts (token-budget half).

#### Scope
**Large.** Multi-error ≈ 240 LOC; token budget ≈ 100 LOC; combined
≈ **340 LOC**. Can ship as separate PRs.

#### Spec change required
None (operational optimization, not spec). The decision blocker is
**empirical**, not a spec gap.

#### Verification
- Multi-error: script with 3 simultaneous SDK errors → one retry
  attempt with 3 errors in feedback (vs. current 3 attempts).
- Multi-error: script with 1 error → identical behavior to current
  (backward compat).
- Token budget: retry loop terminates early when budget hit; returns
  `SkipResult` with `token_budget_exceeded` reason.
- Token budget: `None` default → no behavior change.
- Provider compat: mock `LLMClient` with no token counts → budget
  degrades gracefully (counts as 0).

---

## §3 Dependent stubs (DS-1 … DS-4)

### [DS-1] Censoring injection

**Decision:** Adopt the per-column dict schema (interpretation a) with
NaN-replacement marker (interpretation a). Censoring runs *before*
missing-value injection, so missing-rate is computed against the
post-censor distribution.

#### Blocker resolved
- Schema for the `censoring` config. Most natural extension is
  per-column dict
  `{col: {"type": "right"|"left"|"interval", "threshold": ...}}`,
  but the spec doesn't define this shape.
- Marker semantics. Three options:
  (a) replace censored values with NaN (loses censoring info, simple);
  (b) sibling indicator column `<col>_censored` (preserves info but
  doubles column count);
  (c) sentinel value (fragile, family-dependent).
  Phase 3 view extraction needs to know.
- Ordering with missing-value injection — censoring before or after?

#### Why this answer
Per-column dict mirrors the existing `missing_rates` shape — same
keying convention, same validation pattern in `set_realism`. NaN
replacement (a) is the only marker that keeps Phase 3 view extraction
working without new column-discovery logic. "Censoring before missing"
keeps semantics composable: a column at 20% missing rate after
right-censoring has 20% missing among the *remaining* values, not
among the original.

#### Specifics locked in
```python
censoring_config = {
    "wait_minutes": {"type": "right", "threshold": 100.0},
    "cost":         {"type": "left",  "threshold": 50.0},
    "score":        {"type": "interval", "low": 0.0, "high": 10.0},
}
```
- `"right"`: values > threshold become NaN.
- `"left"`: values < threshold become NaN.
- `"interval"`: values outside `[low, high]` become NaN.
- Missing column → warn and skip, no NaN injection elsewhere.
- Empty config `{}` → no-op.
- Unknown `type` → `ValueError`.
- **New type** added to `types.py`:
  ```python
  class CensoringSpec(TypedDict, total=False):
      type: Literal["right", "left", "interval"]
      threshold: float   # right / left
      low: float         # interval
      high: float        # interval
  ```

#### Files affected
- Stub site: [engine/realism.py:57-63](../../engine/realism.py#L57-L63) (replace `NotImplementedError` block with `inject_censoring`).
- SDK validation: [sdk/relationships.py](../../sdk/relationships.py) (`set_realism` already accepts `censoring=None`; upgrade param validation to enforce schema).
- Prompt: [orchestration/prompt.py:70-71](../../orchestration/prompt.py#L70-L71) (currently omits `censoring=` kwarg with TODO; re-advertise after implementation).
- New type: `types.py` (`CensoringSpec` TypedDict).
- Update One-Shot Example to demonstrate censoring.

#### Dependencies
- **Blocks:** Nothing (leaf stub).
- **Blocked by:** Spec Theme 3 (censoring schema + marker semantics).
- **Co-implement with:** prompt + One-Shot Example update (restoration
  requires all three to land together).

#### Scope
**Small.** Body ≈ 35 LOC + schema validation ≈ 20 LOC + optional
TypedDict ≈ 5 LOC + tests ≈ 50 LOC ≈ **110 LOC**. Comparable to
`inject_dirty_values` (~60 LOC).

#### Spec change required
Theme 3 (see §4.3). The spec must publish the per-column dict schema,
the three censoring types (right/left/interval), the NaN-marker rule,
and the "censoring before missing" ordering.

#### Verification
- Right-censoring: values above threshold become NaN; others unchanged.
- Left-censoring: symmetric.
- Interval: only out-of-range values become NaN.
- Missing column: warns and skips, no NaN injected anywhere.
- Empty config: no-op.
- Unknown `type`: `ValueError` with clear message.
- Order: missing_rate computed against post-censor distribution
  (verified by row-count math).

---

### [DS-2] 4 pattern type injection

**Decision:** Implement four injectors mirroring `inject_outlier_entity`
/ `inject_trend_break`. Sequence within DS-2:
**`ranking_reversal` first** (validator already exists, lowest-effort
win), then `dominance_shift`, `convergence`, `seasonal_anomaly` paired
with their IS-2/3/4 validators.

#### Blocker resolved
- Operational injection algorithm for each of the four types
  (`ranking_reversal`, `dominance_shift`, `convergence`,
  `seasonal_anomaly`). Each must align with the corresponding L3
  validator (IS-2/3/4).
- Roadmap: ship all four at once, or incrementally? `ranking_reversal`
  already has a working validator; `seasonal_anomaly` and
  `dominance_shift` are mechanically similar to `trend_break`;
  `convergence` is the most novel.
- For `ranking_reversal`, the spec only covers the verifier — injector
  contract is missing.

#### Why this answer
Each injector pairs naturally with a validator and implements the
inverse operation: the injector creates the post-condition, the
validator confirms it. Four shapes mirror the two existing implemented
patterns (`outlier_entity`, `trend_break`) at ~70-80 LOC each.
Sequencing `ranking_reversal` first is a shape-driven choice — its
validator (`check_ranking_reversal`) is the only one of the four that
already exists; only the injector is missing.

#### Specifics locked in

**`ranking_reversal`** — Reverse rank order at entity-mean level.
1. Group target rows by `entity_col`.
2. Rank entities ascending by `mean(m1)`.
3. Compute desired `mean(m2)` by reversing `rank_m1`.
4. Per entity, additively shift `m2` values so entity mean lands at
   the desired position.
   Pairs naturally with `check_ranking_reversal` (Spearman corr < 0).

**`dominance_shift`** — Shift target subset post-`split_point` so
`target_entity`'s mean exceeds peers'.
- Resolve `temporal_col` (mirror `inject_trend_break`).
- Compute `peer_max` and `peer_std` from non-target rows post-split.
- `shift = peer_max + magnitude * peer_std - df.loc[post_split, col].mean()`
- `df.loc[post_split, col] += shift`

**`convergence`** — Pull target rows toward `global_mean` as time
progresses; magnitude grows linearly with normalized time.
```
for each target row:
    factor = (t - tmin)/(tmax - tmin) * pull
df[col] = df[col] * (1 - factor) + global_mean * factor
```

**`seasonal_anomaly`** — Scale target values inside `anomaly_window`
by `(1 + magnitude)`; mirrors `inject_trend_break` with a finite
`[start, end]` window.
```
in_win = target_mask & (temporal in [win_start, win_end])
df.loc[in_win, col] *= (1 + magnitude)
```

**Per-type required-params (extends `PATTERN_REQUIRED_PARAMS`):**
```python
"ranking_reversal":  frozenset({"metrics"}),
"dominance_shift":   frozenset({"entity_filter", "split_point"}),
"convergence":       frozenset(),
"seasonal_anomaly":  frozenset({"anomaly_window", "magnitude"}),
```

#### Files affected
- Stub site: [engine/patterns.py:61-71](../../engine/patterns.py#L61-L71) (4-way `NotImplementedError` branch — replace with explicit dispatch).
- SDK gate: [sdk/relationships.py:29](../../sdk/relationships.py#L29) (`VALID_PATTERN_TYPES` — add 4 type names back).
- SDK gate: [sdk/relationships.py:39](../../sdk/relationships.py#L39) (`PATTERN_REQUIRED_PARAMS` — add 4 entries above).
- Prompt: [orchestration/prompt.py:72](../../orchestration/prompt.py#L72) (currently advertises only 2 types — re-advertise all 6).
- One-Shot Example: add an entry per new type.

#### Dependencies
- **Blocks:** End-to-end exercise of IS-2, IS-3, IS-4. Removes silent
  failure when the LLM picks an unimplementable pattern type.
- **Blocked by:** Spec Theme 2 (op definitions for each pattern).
  `ranking_reversal` could be derived from the existing verifier
  contract.
- **Co-implement with:** IS-2, IS-3, IS-4 (each `(injector, validator)`
  pair must share the same operational definition); prompt + SDK gate.

#### Scope
**Large.** Per-injector body ≈ 50–80 LOC × 4 ≈ 250 LOC +
`relationships.py` and `prompt.py` updates ≈ 30 LOC + tests ≈ 150 LOC
≈ **430 LOC** total.

#### Spec change required
Theme 2 (see §4.2) — paired with IS-2/3/4. The spec must publish each
injection algorithm alongside its validator op definition.

#### Verification
- Per type: declaration with valid params succeeds; `inject_*`
  produces a post-condition that the matching L3 validator passes
  (round-trip).
- Per type: declaration with missing required param raises
  `ValueError` with type-specific detail.
- Edge: empty target subset → `PatternInjectionError`.
- Edge: missing temporal column for time-dependent types → graceful
  error.
- Roundtrip integration: a script using all 4 new types runs end-to-end
  without crashing; L3 validator returns 4 passing checks.

---

### [DS-3] Mixture KS test

**Decision:** Co-implement with IS-1 using a small `_MixtureFrozen`
adapter. **No independent decision** — the schema is whatever IS-1
locks in (interpretation a, components carry their own `param_model`).

#### Blocker resolved
- Same as IS-1 — mixture `param_model` schema must be settled first.
  Independent implementation is impossible.
- Operational: scipy doesn't have a native mixture frozen-dist; use a
  small `_MixtureFrozen` adapter exposing only `.cdf()`.

#### Why this answer
The KS test must consume the same schema the sampler produces, so
sampling and CDF construction must agree on a single source of truth.
Shipping IS-1 alone would leave its samples unverifiable; shipping
DS-3 alone has nothing to verify. Pairing forces the schema to round-
trip in tests immediately. The `_MixtureFrozen` adapter exists because
scipy's `kstest` consumes any object with `.cdf()` — the minimal
interface to satisfy that contract.

#### Specifics locked in
```python
class _MixtureFrozen:
    """scipy frozen-dist-like adapter: exposes .cdf() for kstest."""
    def __init__(self, components: list[tuple[float, Any]]):
        self.components = components  # list of (weight, frozen_dist)

    def cdf(self, x: np.ndarray) -> np.ndarray:
        return sum(w * d.cdf(x) for w, d in self.components)
```
- `_expected_cdf` gains an explicit `"mixture"` branch (currently falls
  through to `return None`).
- `_compute_cell_params` walks the components list to compute per-cell
  params for each component.
- `check_stochastic_ks` drops its early-return special case — the
  predictor-cell loop now handles mixtures via the standard path.
- Component with unsupported family (e.g. mixed-type with poisson
  inside) → returns `None`, predictor cell skipped (graceful).

#### Files affected
- Stub site: [validation/statistical.py:259-264](../../validation/statistical.py#L259-L264) (replace hard-coded `passed=True`).
- CDF: [validation/statistical.py:130-166](../../validation/statistical.py#L130-L166) (`_expected_cdf` — add mixture branch; remove implicit fall-through).
- Cell params: [validation/statistical.py:169-203](../../validation/statistical.py#L169-L203) (`_compute_cell_params` — walk components).

#### Dependencies
- **Blocks:** Nothing (leaf in the dependency chain).
- **Blocked by:** IS-1 (cannot test what cannot be sampled); spec
  Theme 1 (mixture schema).
- **Co-implement with:** IS-1 — single PR.

#### Scope
**Small.** `_MixtureFrozen` ≈ 15 LOC + `_expected_cdf_mixture` ≈ 20
LOC + cell param walk ≈ 25 LOC + tests ≈ 70 LOC ≈ **130 LOC**.

#### Spec change required
Inherits Theme 1 from IS-1. No additional spec content beyond the
mixture schema.

#### Verification
- 2-component gaussian mixture sampled from IS-1 → KS test passes.
- Mismatched mixture (samples from different params than declared) →
  KS test fails.
- Single-component mixture (`weight=1.0`) → behaves identically to
  non-mixture KS test.
- Component with unsupported family (e.g. poisson inside continuous
  mixture) → returns `None`, predictor cell skipped.
- Auto-normalization: components with weights `[0.3, 0.2]` tested with
  effective `[0.6, 0.4]`.

---

### [DS-4] Multi-column group dependency `on=[...]`

**Decision:** Adopt interpretation **(a)** — nested-dict
`conditional_weights` with nesting depth equal to `len(on)`. Full
Cartesian coverage required. No soft cap on combinations (LLM
responsibility).

#### Blocker resolved
- `conditional_weights` structure for multi-column `on`. Reasonable
  choices:
  (a) nested dict keyed by parent value sequence
  (`{"Mild": {"Xiehe": {"Insurance": 0.8}}}`);
  (b) tuple-keyed flat dict
  (`{("Mild", "Xiehe"): {"Insurance": 0.8}}`).
  Nested is JSON-serializable, natural extension of single-column.
- Must Cartesian product be fully covered, or is partial coverage
  allowed (with fallback)? Single-column case requires full coverage.
- Operational: N-way cardinality blow-up — for `on=[a, b, c]` with
  cardinalities 5×4×3, the LLM must declare 60 inner weight dicts.
  Should there be a soft cap?

#### Why this answer
Nested dict (a) is JSON-serializable (tuple keys are not), reads
naturally as a decision tree, and degenerates correctly to the
single-column case at depth 1 (backward compat). Full coverage matches
the existing single-column rule — no special "missing combination"
logic to invent. No soft cap because the LLM is responsible for
declaring sensible cardinalities; failures fall through to validation
as `ValueError` with the missing key path.

#### Specifics locked in
```python
# Nesting depth = len(on)
# Example for on=["severity", "hospital"]:
conditional_weights = {
    "Mild": {
        "Xiehe": {"Insurance": 0.8, "Self-Pay": 0.2},
        "Mayo":  {"Insurance": 0.7, "Self-Pay": 0.3},
    },
    "Moderate": {
        "Xiehe": {"Insurance": 0.6, "Self-Pay": 0.4},
        "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5},
    },
}
```
- Validation: recursive helper
  `_validate_and_normalize_nested_weights` walks the nested dict and
  enforces full Cartesian coverage.
- Sampling: extend lookup from flat `cw[parent_val]` to N-deep walk.
- L2 deviation comparison: walk N-deep nested dicts.
- Backward compat: depth=1 must produce the same normalized output as
  before.

#### Files affected
- Stub site: [sdk/relationships.py:123-132](../../sdk/relationships.py#L123-L132) (replace `len(on) != 1` `NotImplementedError`).
- Validation: [sdk/relationships.py:101-213](../../sdk/relationships.py#L101-L213) (`add_group_dependency`).
- Engine: [engine/generator.py](../../engine/generator.py) (group-dep sampling step).
- L2 deviation: [validation/statistical.py:24-55](../../validation/statistical.py#L24-L55) (`max_conditional_deviation`).

#### Dependencies
- **Blocks:** Nothing in inventory.
- **Blocked by:** Spec Theme 4 (nested vs tuple, normalization,
  coverage rule).

#### Scope
**Medium.** Nested-weight walk ≈ 50 LOC + engine sampler extension
≈ 30 LOC + L2 deviation walk ≈ 30 LOC + tests ≈ 80 LOC ≈ **190 LOC**.
About 2× the single-column footprint; recursion replaces flat 2-level
dict logic in three call sites.

#### Spec change required
Theme 4 (see §4.4). The spec must publish the nested-dict shape, full
Cartesian coverage requirement, and missing-combination error mode.

#### Verification
- 2-parent dependency with full Cartesian coverage → declaration
  succeeds; engine sampling reproduces the declared conditional
  within 10% deviation.
- Missing combination (one parent value absent at depth 1) →
  `ValueError` listing the missing key path.
- Missing inner combination (one child value missing at leaf) →
  `ValueError` with the full path.
- Existing single-column tests still pass (backward compat: depth=1
  case must produce the same normalized output as before).
- L2 group-dep deviation check correctly identifies divergent
  observations on multi-parent specs.

---

## §4 Spec extensions consolidated

Nine of the ten stubs depend on changes to `phase_2.md`. They cluster
into four themes. Updating `phase_2.md` along these four axes is the
recommended first action after this decision record is approved —
each theme unblocks multiple downstream stubs.

### §4.1 Theme 1 — Mixture `param_model` schema

**Unblocks:** IS-1 (sampler), DS-3 (KS test).

**Spec content to publish:**
- Component structure:
  ```
  {"family": str, "weight": float, "param_model": {...}}
  ```
- Each component's `param_model` follows the same intercept+effects
  shape as a non-mixture stochastic measure.
- Weights are auto-normalized to sum to 1.0.
- No restriction on mixed-type families; the KS test degrades
  gracefully (skips the predictor cell) when a component's family
  isn't supported by the standard `_expected_cdf` path.

**Suggested insertion point:** `phase_2.md` §2.1 (stochastic measures),
as a sub-section after the existing per-family `param_model` shapes.

### §4.2 Theme 2 — Pattern op definitions

**Unblocks:** IS-2, IS-3, IS-4 (validators), 3 of the 4 DS-2 sub-features
(injectors for `dominance_shift`, `convergence`, `seasonal_anomaly`).
The 4th DS-2 sub-feature (`ranking_reversal` injector) inherits its
contract from the existing verifier.

**Spec content to publish — for each of `dominance_shift`,
`convergence`, `seasonal_anomaly`:**
- The validator pass condition (formula + threshold default).
- The matching injection algorithm (sketched in §3 above).
- The required `params` keys.
- Graceful-fail behavior on missing temporal column / single entity /
  constant column.

Specifics:
- **`dominance_shift`** — `|rank_after - rank_before| >= rank_change` with default `rank_change=1`. Injector: shift target post-split to exceed peers.
- **`convergence`** — `(early_var - late_var) / early_var >= reduction` with default `reduction=0.3`. Injector: pull target toward `global_mean` over normalized time.
- **`seasonal_anomaly`** — `|window_mean - baseline_mean| / baseline_std >= z_threshold` with default `z_threshold=1.5`. Injector: scale target values inside `anomaly_window` by `(1 + magnitude)`. `anomaly_window=[start, end]` is mandatory.

**Suggested insertion point:** `phase_2.md` §2.3 (patterns), expanding
the existing two pattern types to six.

### §4.3 Theme 3 — Censoring config schema + marker semantics

**Unblocks:** DS-1.

**Spec content to publish:**
- Per-column dict schema:
  ```python
  {col: {"type": "right" | "left" | "interval", ...}}
  ```
  with `threshold` (right/left) or `low`/`high` (interval).
- Marker rule: censored values are replaced with NaN. (Phase 3 view
  extraction uses this.)
- Ordering: censoring runs **before** missing-value injection; the
  missing rate is computed against the post-censor distribution.
- Unknown `type` → `ValueError`.

**Suggested insertion point:** `phase_2.md` §2.4 (realism), as a
sub-section alongside `missing_rates`.

### §4.4 Theme 4 — Multi-column `conditional_weights` nesting rule

**Unblocks:** DS-4.

**Spec content to publish:**
- Nesting structure: nested dict with depth equal to `len(on)`. Tuple
  keys are not allowed (not JSON-serializable).
- Full Cartesian coverage required across all parent value
  combinations.
- Normalization: per innermost dict (same rule as single-column case).
- Missing combination → `ValueError` listing the missing key path.

**Suggested insertion point:** `phase_2.md` §2.2 (group dependencies),
extending the existing single-column `conditional_weights` rule.

---

## §5 Implementation sequencing

Tier numbers match the table in §1. Each tier names what to ship and
why that order minimizes risk and maximizes time-to-value.

| Tier | What ships | Size | Why this order |
|------|-----------|------|----------------|
| 1 | IS-5 docs cleanup | Trivial | No spec gate; closes a vestigial spec line that already disagrees with prompt and SDK. Pure win. |
| 2 | DS-1 censoring | Small (~110 LOC) | Leaf stub; the only blocker is Theme 3, which is schema-only — spec it once and ship. |
| 3 | DS-2 `ranking_reversal` only | Small (~110 LOC slice of DS-2) | Validator already exists. Lowest-effort win in the DS-2 cluster: only needs an injector + SDK gate update + prompt update. |
| 4 | IS-3 + IS-4 + IS-2 + remaining DS-2 injectors | Medium-Large | Pair each validator with its injector once Theme 2 lands. Within tier, IS-3 first (most novel, biggest spec gap to close), then IS-4 (mirrors `outlier_entity`), then IS-2 (mirrors `trend_break`). |
| 5 | IS-1 + DS-3 (paired) | Medium (~300 LOC) | Highest spec dependency (Theme 1). Sampler and CDF must agree on the same schema; co-implement in one PR. |
| 6 | DS-4 multi-column `on` | Medium (~190 LOC) | Independent. Ship when LLM workflows demand multi-parent dependencies — until then, single-column case is unaffected. |
| 7 | IS-6 (multi-error + token-budget) | Large (~340 LOC combined) | Pure optimization, not in spec. Defer until retry-loop overhead is measured to be a real bottleneck. If forced, ship token-budget half first. |

**Recommended pre-tier-1 step:** merge all 4 spec themes into
`phase_2.md` in one editing pass. Tiers 1–6 are bottlenecked on this.
Tier 1 (IS-5 docs strip) can run in parallel with the spec editing
since it removes content rather than adding it.

---

## §6 Cross-references

- [stub_analysis/stub_gap_analysis.md](stub_analysis/stub_gap_analysis.md) — full per-stub
  analysis with rejected interpretations, line-level code excerpts,
  and full reasoning traces.
- [stub_analysis/stub_review.md](stub_analysis/stub_review.md) — adversarial review of the
  analysis. Consult before implementation; some decisions may need
  adjustment based on issues flagged there.
- [phase_2_spec_decisions.md](phase_2_spec_decisions.md) — sibling
  decision record (parallel summary, cross-checked for consistency
  on factual specifics).
- [phase_2.md](phase_2.md) — the spec. Destination for the four
  spec extensions in §4.
- [stage5_anatomy_summary.md](stage5_anatomy_summary.md) — current
  implementation state (file tree, existing analog patterns).
- [../../README.md](../../README.md) — module-level overview.
