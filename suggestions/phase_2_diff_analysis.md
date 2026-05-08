# Phase 2 Specification — Conceptual Diff Analysis

**Compares:** `phase_2.md` (original) vs `phase_2_latest.md` (mentor's update)
**Date:** 2026-05-07

---

## TL;DR — The Single Big Idea

The mentor reframed measures from **"declare-then-patch"** to **"closed-form, DAG-ordered."**

In the original, a measure's final DGP was the *result* of chaining:

```
add_measure(...)  →  add_conditional(...)  →  add_dependency(...)  →  add_correlation(...)
```

Each call mutated the prior declaration, so the **declared** distribution and the **actual** generated distribution could silently diverge after successive overrides — and validation couldn't tell which "ground truth" to test against.

In the update, **every measure is declared exactly once as a complete data-generating program**, and its generative role falls into one of two crisp categories:

| Type | API | DAG Role | Generation |
|---|---|---|---|
| **Stochastic root** | `add_measure(name, family, param_model)` | No incoming measure edges | Sampled from a parameterized distribution |
| **Structural derived** | `add_measure_structural(name, formula, effects, noise)` | Has incoming measure edges | Deterministically computed + noise |

All inter-measure relationships flow through this DAG. There is no separate `add_correlation()` — correlation **emerges** from either (a) structural formulas or (b) shared categorical predictors.

---

## 1. API Surface Changes

### Removed
| Removed Method | Rationale |
|---|---|
| `add_conditional(measure, on, mapping)` | Subsumed: conditioning is now expressed inside `param_model={"intercept", "effects": {predictor: {level: β}}}` of the *same* `add_measure` call. |
| `add_dependency(target, formula, noise_sigma)` | Renamed/upgraded to `add_measure_structural(...)`. |
| `add_correlation(col_a, col_b, target_r)` | Eliminated. Inter-measure correlation now emerges from structural formulas or shared predictors. No more Gaussian-Copula post-hoc injection. |

### Added
| New Method | Purpose |
|---|---|
| `add_measure_structural(name, formula, effects, noise)` | Closed-form derived measure that creates explicit edges in the measure DAG. |
| `add_group_dependency(child_root, on, conditional_weights)` | Models cross-group dependency between **root** columns (e.g., `payment_method` ⟸ `severity`). The root-level cross-group graph must be acyclic. |

### Changed signatures
| Method | Original | Updated |
|---|---|---|
| `add_measure` | `add_measure(name, dist, params)` — flat params | `add_measure(name, family, param_model, scale=None)` — `param_model` uses `{intercept, effects}` schema with categorical predictors. |
| `add_temporal` | `add_temporal(name, start, end, freq)` | `add_temporal(name, start, end, freq, derive=[])` — calendar features (`day_of_week`, `month`, `quarter`, `is_weekend`) auto-extracted as predictors. |
| `add_category` (with `parent`) | `weights` is a flat list (same for all parents) | `weights` may be flat list **or** dict-of-lists `{parent_value: [...]}` for per-parent conditionals. |

---

## 2. Conceptual Model Shift

### Old model — incremental override
```
declare marginal  →  override params per category  →  override target by formula  →  inject Pearson correlation
```
Each step *modifies* the measure's DGP. Verification semantics ambiguous after step 2+.

### New model — closed-form + DAG
```
each measure is one closed-form declaration
   ↓
all dependencies form an explicit DAG (categoricals + measures)
   ↓
engine runs topological sort, generates row-by-row in DAG order
```

**Three direct consequences:**

1. **No drift between declaration and generation.** The validator tests the *exact* spec the agent declared.
2. **Inter-measure correlation is structural, not retrofitted.** Either a formula creates it (`cost = 12·wait_minutes + …`) or shared predictors create it (two measures both varying with `severity`).
3. **Cyclic dependencies are caught upfront** as `CyclicDependencyError`, before generation begins.

---

## 3. Cross-Group Semantics — From Implicit to Explicit DAG

| Aspect | Original | Latest |
|---|---|---|
| Default cross-group relation | Implicit independence (only `declare_orthogonal` was modeled) | **Opt-in independence**. Non-orthogonal pairs may carry explicit `add_group_dependency`. |
| Where dependencies are allowed | Not formally restricted | **Root columns only** (no parent), and the root-level cross-group graph must be acyclic. |
| Temporal column | Standalone, not a group | A first-class **dimension group** ("time"), with `derive=[…]` adding child calendar levels. |

This eliminates a hidden class of bugs: under the old spec, two non-orthogonal groups had no formal relationship — the LLM might *assume* dependency that the engine never modeled.

---

## 4. Generation Pipeline — Reorganized

### Original (7 stages)
```
M = τ_post ∘ ρ ∘ φ ∘ ψ ∘ λ ∘ γ ∘ δ ∘ β(seed)
    └ skeleton β → marginal δ → conditional override γ → dependency λ →
      correlation copula ψ → patterns φ → realism ρ → post-process
```

### Latest (4 stages, optional realism)
```
M = τ_post ∘ δ? ∘ γ ∘ β ∘ α(seed)
    └ α: non-measure cols (cat roots, child cats, temporal + derived)
      β: measures in topological order (stochastic then structural per DAG)
      γ: pattern injection
      δ?: realism (optional — only when set_realism() called)
```

**Key engine-level changes:**

- **Single full-DAG topological sort** drives generation order, mixing categoricals, temporal, and measures. The original engine had implicit phase ordering with the measure layer split across `δ`, `γ`, `λ`, `ψ`.
- **Event-level (atomic) row generation** is now stated explicitly: the engine does **not** materialize a categorical cross-product cube. Each row is sampled independently as one event. This is described in detail in the new §2.4.
- **Realism is optional** (the `?` superscript on `δ`). Original had it always-on.

---

## 5. Schema Metadata — Output Contract Changes

| Field | Original | Latest |
|---|---|---|
| `dimension_groups` | Excludes temporal | Includes a `"time"` group with `derived` children |
| `orthogonal_groups` | Present | Present (unchanged shape) |
| `group_dependencies` | — | **Added.** Lists `{child_root, on, conditional_weights}` |
| `conditionals` | Present | **Removed** (folded into measure declarations) |
| `correlations` | Present | **Removed** (no `add_correlation` API) |
| `dependencies` | Present | **Removed** (replaced by `depends_on` on each structural measure) |
| Per-column entry for measures | `{type: "measure"}` only | Adds `measure_type: "stochastic" \| "structural"`, `family`, `depends_on` |
| `measure_dag_order` | — | **Added.** Topological order of measures, used by Phase 3 for causal-reasoning QA |

> **Phase 3 implication:** the View Extractor and QA generator now have access to an explicit causal DAG over measures — a richer input than the old correlation+dependency lists.

---

## 6. Validation Layer Differences

### L1: Structural
- **Added:** Categorical-root marginal-weight check (max deviation < 10% from declared `weights`).
- **Added:** Measure-DAG acyclicity check (defensive; SDK should reject cycles at declaration time).

### L2: Statistical — fundamental rewrite
| Original | Latest |
|---|---|
| Pearson correlation vs `target_r` (`abs(actual - target) < 0.15`) | **Removed.** No `target_r` to test against. |
| Functional-dependency residual std as fraction of target std | Replaced by **two checks per structural measure**: residual **mean** ≈ 0, residual **std** ≈ declared `noise_sigma` (within 20%). |
| KS test against declared distribution **at marginal level** | KS test **per predictor cell**: each combination of categorical predictor levels is checked against its own conditional `(intercept + effects)` parameters. |
| — | **Added:** Group-dependency conditional-transition check — observed `crosstab(parent_root, child_root, normalize="index")` vs declared `conditional_weights` (max deviation < 10%). |

The change from marginal-KS to per-cell-KS is significant: it catches param-effect bugs that average out marginally but are wrong in specific subpopulations.

### L3: Pattern
- Effectively unchanged in form. The pattern types and tests are identical.

### Auto-fix
- `corr_*` strategy **removed** (no correlation API to fix).
- Otherwise the same set of strategies (`ks_*`, `outlier_*`, `trend_*`, `orthogonal_*`).

---

## 7. Error Surface (LLM Feedback Loop)

The update introduces more specific exception types, which give the agent sharper repair signals:

| Original example | Latest examples |
|---|---|
| `ValueError: Cannot achieve target_r=… given marginals` | `CyclicDependencyError: cost → satisfaction → cost` |
| | `UndefinedEffectError: 'severity_surcharge' has no definition for 'Severe'` |
| | `NonRootDependencyError: 'department' is not a group root` |

These map 1:1 to the new structural invariants (acyclic DAG, complete effect tables, root-only cross-group deps).

---

## 8. LLM Prompt — Hard Constraint Changes

| Original constraint | Latest constraint |
|---|---|
| ≥1 `add_correlation()` | **Removed.** |
| ≥2 `inject_pattern()` | Kept, plus **≥1 `add_measure_structural()`** to force inter-measure dependency through the DAG. |
| — | **Added:** measure DAG must be acyclic. |
| — | **Added:** cross-group deps only between roots; root DAG acyclic. |
| — | **Added:** every symbol in `param_model`/`formula` must have an explicit numeric definition (no undefined effects). |

Soft guidelines also shift: from "include numerical correlation pairs" → "use per-parent conditional weights" and "use `add_group_dependency()` when groups aren't independent."

---

## 9. New Material with No Original Counterpart

Three sections in the latest spec are entirely new conceptual additions:

| § | Section | What it adds |
|---|---|---|
| §2.2 | Dimension Groups and Cross-Group Relations | Promotes dimension groups to first-class abstraction unifying categorical, temporal, and dependency semantics. |
| §2.3 | Closed-Form Measure Declaration | Formal definition of stochastic vs structural measures and the rule that inter-measure correlation comes only from (a) structural formulas or (b) shared predictors. |
| §2.4 | DAG-Ordered Event-Level Row Generation | Step-by-step per-row algorithm with explicit topological layers; explicit ban on cross-product materialization; complexity-tier table mapping Phase-1 scenarios to `target_rows`. |

The `target_rows` complexity tier table (Simple 200–500 / Medium 500–1000 / Complex 1000–3000) is a new contract point with Phase 1.

---

## 10. Implementation Impact Checklist

If you've already started building against `phase_2.md`, these are the load-bearing changes to migrate:

1. **Delete** `add_conditional`, `add_dependency`, `add_correlation` and their engine stages (`γ` conditional override, `λ` dependency, `ψ` copula).
2. **Refactor** `add_measure` to accept `param_model = {intercept, effects: {predictor: {level: β}}}` shape.
3. **Add** `add_measure_structural` — formula parser, effect-table validator, noise spec.
4. **Add** `add_group_dependency` and root-only / acyclicity guards.
5. **Add** `derive=[]` to `add_temporal` and emit derived calendar columns into the column registry.
6. **Allow** dict-of-lists weights on child `add_category`.
7. **Replace** the multi-stage engine with a single full-DAG topological executor; ensure realism stage is gated on `set_realism()` having been called.
8. **Switch** L2 validation to per-cell KS for stochastic measures and residual mean+std for structural measures; add group-dependency transition check; drop correlation checks.
9. **Add** L1 marginal-weight check on categorical roots and DAG-acyclicity assertion.
10. **Update** schema-metadata builder: drop `conditionals`/`correlations`/`dependencies`, add `group_dependencies`, `measure_type`/`family`/`depends_on` per measure column, `measure_dag_order`, and the `time` dimension group.
11. **Update** typed exceptions: add `CyclicDependencyError`, `UndefinedEffectError`, `NonRootDependencyError`.
12. **Update** the LLM prompt template with the new hard constraints and one-shot example.

---

## 11. What Did *Not* Change

For continuity, these aspects are stable across both specs:

- The dimension-group / orthogonality propagation principle and its three uses (generation, L1 validation, Phase-3 view extraction).
- Pattern types and L3 pattern-validation logic.
- The auto-fix loop architecture (per-failure strategy lookup, max 3 retries, soft failure).
- The "no LLM call after script execution" principle for the engine and validator.
- Determinism guarantee: same `seed` → bit-for-bit reproducible output.
- The Phase-2 → Phase-3 contract through schema metadata (the *shape* of the contract changes, but the role does not).
- The atomic-grain hard constraint (one row = one indivisible event).
