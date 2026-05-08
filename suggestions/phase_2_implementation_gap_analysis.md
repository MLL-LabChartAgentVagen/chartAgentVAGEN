# Phase 2 Implementation — Gap Analysis vs `phase_2_latest.md`

**Compares:** working implementation at [pipeline/phase_2/](../pipeline/phase_2/) vs spec at [suggestions/phase_2_latest.md](phase_2_latest.md)
**Date:** 2026-05-07
**Method:** module-by-module read of `sdk/`, `engine/`, `validation/`, `metadata/`, `orchestration/`, plus targeted verification of the most load-bearing claims.

---

## TL;DR

**You have one real gap and zero migration backlog.**

All 11 conceptual changes from the spec update — closed-form measures, the unified DAG, root-only cross-group dependencies, per-cell KS validation, structural residual mean+std, the four-stage engine, the rewritten metadata contract — are already implemented and aligned. The only divergence is the deliberate omission of the `scale` kwarg on `add_measure`, which is gated behind a TODO with a clear rationale.

---

## Verification Method

For each of the 11 areas in [phase_2_diff_analysis.md](phase_2_diff_analysis.md), I checked:

- **Removed APIs:** absent from the SDK surface and not referenced anywhere in `pipeline/phase_2/`
- **New APIs:** present with matching signatures and the new validation invariants
- **Engine pipeline:** module call order matches `α → β → γ → δ?` with realism gated on `realism_config is not None`
- **Validation:** every check listed in §2.9 has a corresponding implementation; obsolete checks are absent
- **Metadata schema:** every key listed in §2.6 is emitted; obsolete keys are absent

Spot-checks were done by reading specific call sites (engine entry point, KS test cells, residual checks, exception class definitions) rather than relying on agent summary alone.

---

## Area-by-Area Audit

### 1. Removed APIs ✅

| Spec says | Code state |
|---|---|
| `add_conditional` removed | Not defined anywhere; no callers |
| `add_dependency` removed | Not defined anywhere; no callers |
| `add_correlation` removed | Not defined anywhere; no callers |

[sdk/simulator.py](../pipeline/phase_2/sdk/simulator.py) exposes only the latest API surface.

### 2. New / changed APIs ✅ (with one deliberate omission)

| API | Status | Location |
|---|---|---|
| `add_measure(name, family, param_model, scale=None)` | ⚠️ **`scale` kwarg deliberately absent** — see "Only Real Gap" below | [sdk/simulator.py:109-117](../pipeline/phase_2/sdk/simulator.py#L109-L117), [sdk/columns.py:218-250](../pipeline/phase_2/sdk/columns.py#L218-L250) |
| `add_measure_structural(name, formula, effects, noise)` | ✅ present, validates symbol resolution and DAG acyclicity at declaration time | [sdk/columns.py:253-321](../pipeline/phase_2/sdk/columns.py#L253-L321) |
| `add_group_dependency(child_root, on, conditional_weights)` | ✅ root-only check raises `NonRootDependencyError`; root-DAG acyclicity check present; multi-column `on` supported via nested dicts | [sdk/relationships.py:117-215](../pipeline/phase_2/sdk/relationships.py#L117-L215) |
| `add_temporal(..., derive=[])` | ✅ derive list validated against `TEMPORAL_DERIVE_WHITELIST`; derived columns auto-registered with `type: "temporal_derived"` | [sdk/columns.py:124-211](../pipeline/phase_2/sdk/columns.py#L124-L211) |
| `add_category` per-parent dict-of-lists weights | ✅ both flat list and `{parent_value: [...]}` accepted | [sdk/columns.py:38-121](../pipeline/phase_2/sdk/columns.py#L38-L121) |

Param-model schema check (`{intercept, effects: {predictor: {level: β}}}`) lives in [sdk/validation.py:502-556](../pipeline/phase_2/sdk/validation.py#L502-L556).

### 3. Engine pipeline — single full-DAG topological executor ✅

[engine/generator.py](../pipeline/phase_2/engine/generator.py) runs in this exact order:

```
73-74  → init RNG
77-80  → build_full_dag → topological_sort
82-85  → α: build_skeleton (non-measure cols, in topo order)
87-90  → β: generate_measures (DAG-ordered, stochastic + structural)
92-93  → post-process to DataFrame
95-98  → γ: inject_patterns (only if patterns list non-empty)
100-103 → δ?: inject_realism (only if realism_config is not None)
```

Realism gating is correct (latest spec mandates optional). The 7-stage original pipeline (β/δ/γ/λ/ψ/φ/ρ) has been fully collapsed.

### 4. Event-level row generation ✅

[engine/skeleton.py](../pipeline/phase_2/engine/skeleton.py) samples `target_rows` rows independently. Roots use vectorized `rng.choice(size=target_rows)`; dependent roots are sampled row-by-row conditional on parents. **No cross-product cube is materialized.**

### 5. Specific exception types ✅

| Exception | File |
|---|---|
| `CyclicDependencyError` (with `cycle_path` formatting) | [exceptions.py:52-74](../pipeline/phase_2/exceptions.py#L52-L74) |
| `UndefinedEffectError` | [exceptions.py:77-100](../pipeline/phase_2/exceptions.py#L77-L100) |
| `NonRootDependencyError` | [exceptions.py:103-126](../pipeline/phase_2/exceptions.py#L103-L126) |

Plus extras (`DuplicateColumnError`, `EmptyValuesError`, `WeightLengthMismatchError`, `ParentNotFoundError`, `DuplicateGroupRootError`, `PatternInjectionError`, `UndefinedPredictorError`) — defensible additions, not divergences.

### 6. L1 structural validation ✅

All checks from §2.9 present in [validation/structural.py](../pipeline/phase_2/validation/structural.py):

| Check | Lines |
|---|---|
| Row count within 10% | 23-49 |
| Categorical cardinality matches declaration | 52-111 |
| Categorical-root marginal weight deviation < 10% | 213-266 (correctly skips non-root via `if col.get("parent") is not None: continue`) |
| Measure finiteness and non-null | 269-315 |
| Orthogonal independence (chi² on root pairs) | 114-178 |
| Measure DAG acyclicity (defense-in-depth) | 181-210 |

### 7. L2 statistical validation ✅ (full rewrite landed)

[validation/statistical.py](../pipeline/phase_2/validation/statistical.py):

- **Stochastic measures: per-predictor-cell KS test** (lines 318-419) — Cartesian product of predictor levels, KS per cell with computed `(intercept + effects)` parameters, threshold p > 0.05. Pattern-target rows excluded from cells. Mixture distributions handled via custom CDF (lines 171-253).
- **Structural measures: residual mean ≈ 0 AND std ≈ noise_sigma ±20%** (lines 454-570). Correctly excludes both pattern-target rows and any row touched by an upstream pattern.
- **Group dependency: conditional-transition vs declared weights, max deviation < 10%** (lines 573-653). Multi-column `on` supported via nested-dict deviation walker.

Obsolete checks confirmed absent:
- ❌ no Pearson `target_r` test
- ❌ no single-std dependency residual test (replaced by mean+std pair)

### 8. L3 pattern validation ✅

All six pattern types validated in [validation/pattern_checks.py](../pipeline/phase_2/validation/pattern_checks.py):

| Pattern | Lines |
|---|---|
| `outlier_entity` | 23-120 |
| `trend_break` | 122-202 |
| `dominance_shift` | 205-313 |
| `convergence` | 315-402 |
| `seasonal_anomaly` | 404-512 |
| `ranking_reversal` | 514-588 |

### 9. Auto-fix ✅

[validation/autofix.py](../pipeline/phase_2/validation/autofix.py): `widen_variance` (mixture-aware skip), `amplify_magnitude`, `reshuffle_pair`. **`corr_*` strategy correctly removed.** Auto-fix is opt-in (`auto_fix: dict | None = None`).

### 10. Schema metadata output ✅

[metadata/builder.py:23-111](../pipeline/phase_2/metadata/builder.py#L23-L111) emits exactly the keys §2.6 specifies:

- ✅ `dimension_groups` (with `time` group containing derived children)
- ✅ `orthogonal_groups`
- ✅ `group_dependencies` (with `conditional_weights`)
- ✅ `columns` (per-column type discriminators include `measure_type`/`family`/`depends_on` for measures, `derive` for temporal, `derivation`/`source` for `temporal_derived`)
- ✅ `measure_dag_order`
- ✅ `patterns`
- ✅ `total_rows`

Obsolete keys confirmed absent: ❌ `conditionals`, ❌ `correlations`, ❌ `dependencies` (the old shape; `group_dependencies` is the new one).

### 11. LLM prompt ✅

[orchestration/prompt.py:35-212](../pipeline/phase_2/orchestration/prompt.py#L35-L212) is a verbatim port of §2.5 with the new hard constraints:

- ≥1 `add_measure_structural()` and ≥2 `inject_pattern()` (replaces old "≥1 `add_correlation()`")
- Acyclic measure DAG required
- Root-only cross-group dependencies required
- Every symbol in `param_model`/`formula` must have an explicit numeric definition
- No `add_correlation` in the AVAILABLE SDK METHODS list

---

## The Only Real Gap

### `scale` kwarg on `add_measure`

**Spec contract:** §2.5 prompt and §2.1.1 list `add_measure(name, family, param_model, scale=None)`.

**Code state:** [sdk/columns.py:214-215](../pipeline/phase_2/sdk/columns.py#L214-L215) carries this TODO:

> ```python
> # TODO [M?-NC-scale]: restore `scale` kwarg when a scaling implementation lands.
> # Previously `scale` was accepted but silently no-op, which misled LLMs into
> # ...
> ```

The kwarg was deliberately removed because the previous implementation accepted it but did nothing with it — a worse failure mode than a clean reject.

**Important context:** in the latest spec's one-shot example, `satisfaction` (the original `scale=[1,10]` use case) has been redesigned as a structural measure — `add_measure_structural("satisfaction", formula="9 - 0.04*wait_minutes + severity_adj", noise={...})`. The spec **lists** `scale=None` in the signature but **never demonstrates** it. The agent has no in-prompt example pulling them toward the parameter.

### Two ways to close this gap

**Option A — implement `scale` (full alignment with the documented signature).**

- Add `scale: Optional[Tuple[float, float]] = None` to `add_measure`
- In the engine, after sampling, apply `min-max` rescale to the declared `[lo, hi]` interval (or apply the rescale that was originally intended for beta-distributed measures)
- Update L2 stochastic-KS to test the *post-scaled* sample against the *post-scaled* expected distribution
- Useful when an LLM wants to declare e.g. `family="beta", scale=[1, 10]` for a satisfaction-on-1-to-10 measure without going structural

**Option B — strike `scale` from the prompt (cleaner alignment with current code).** ⭐ Recommended

- Update the AVAILABLE SDK METHODS block in [orchestration/prompt.py](../pipeline/phase_2/orchestration/prompt.py) to read `sim.add_measure(name, family, param_model)` (no `scale=None`)
- Update §2.1.1 of [phase_2_latest.md](phase_2_latest.md) accordingly (or note the omission)
- Remove the TODO in [sdk/columns.py:214-215](../pipeline/phase_2/sdk/columns.py#L214-L215) since the divergence is resolved
- Rationale: the latest spec's example doesn't use `scale`, beta scaling can be expressed as a simple structural measure (`y = a + (b-a) * raw_beta`), and a kwarg with no example is exactly what produces the original "silent no-op" failure mode

Either is fine — they just need to agree.

---

## What's *Not* a Gap (worth recording)

These are things I checked because they're easy to miss but are correctly handled:

- **Realism is gated** on `realism_config is not None` ([engine/generator.py:101](../pipeline/phase_2/engine/generator.py#L101)) — matches the `δ?` superscript in the pipeline composition.
- **Pattern-target row exclusion** in L2 stochastic-KS and structural-residual checks — without this, injected outliers would fail their own KS/residual gates.
- **Mixture distribution handling** in L2 KS and auto-fix — `widen_variance` correctly skips mixtures (no single sigma to widen).
- **Per-parent conditional weights in L1** — categorical-marginal check correctly applies only to roots, since child marginals depend on the parent distribution.
- **Multi-column `add_group_dependency`** — `on` can be a list, and the conditional-transition check walks nested observed/expected dicts.
- **DAG acyclicity** is enforced at *declaration time* (in `add_measure_structural` and `add_group_dependency`), not just at validation time — so the `CyclicDependencyError` surfaces in the LLM-feedback loop, exactly as §2.7 promises.

---

## Recommended Next Action

1. **Pick A or B** for the `scale` reconciliation. B is the lower-effort, higher-cohesion choice.
2. **No other migration work is required.** The implementation is at parity with `phase_2_latest.md`.
3. Optional: snapshot this audit as a "last-known-good" marker in [pipeline/phase_2/docs/](../pipeline/phase_2/docs/) so future spec updates can diff against it.
