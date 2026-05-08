# Stage 2 Deep Dive: SDK Surface (M1)

## 1. SUMMARY

The SDK Surface module provides a type-safe, builder-pattern API (`FactTableSimulator`) that accepts column declarations, dimension-group structures, measure definitions, and relationship/pattern declarations from LLM-generated Python scripts, validating them into a coherent internal data model (the "declaration store") consumed by the Generation Engine (M2), Schema Metadata (M4), and — on failure — fed back as typed exceptions to LLM Orchestration (M3). Its most complex section is **§2.1.1 (Column Declarations)**, because it carries the heaviest validation burden — four distinct method signatures, nested conditional-weight structures, formula symbol resolution, DAG edge extraction, and distribution-family dispatch — all of which must be validated at declaration time. The most significant ambiguity is the **`mixture` distribution family**: it is listed as a supported family but its `param_model` structure is never defined, making it unimplementable from the spec alone. Confidence that the spec fully specifies this module: **medium** — the core abstractions and constraints are well-defined, but several parameter structures (`mixture`, `scale`, multi-column `on` in group dependencies, four of six pattern types) lack concrete schemas, and the boundary between declaration-time and generation-time validation is not always explicit.

---

## 2. PHASE A: INTERNAL SECTION ANALYSIS

---

### Section 2.1 — The `FactTableSimulator` SDK (Overview)

#### 2.1-1. PURPOSE
This section introduces the SDK's dual-purpose design philosophy: every `add_*()` call simultaneously defines a column's schema (name, type, group membership) and its complete data-generating program (distribution, dependencies, effects). It establishes the `FactTableSimulator(target_rows, seed)` constructor as the single entry point that all downstream generation hangs from.

#### 2.1-2. KEY MECHANISM
The core abstraction is a **builder pattern** — the LLM-generated script instantiates `FactTableSimulator`, then issues a sequence of declarative method calls that populate internal registries. The constructor accepts two arguments:

- **`target_rows`**: inherited from Phase 1's scenario context, governs how many atomic event rows the engine will later produce.
- **`seed`**: integer for deterministic reproducibility; passed through to `np.random.default_rng` at generation time.

The SDK exposes no `.generate()` logic in this section — it purely frames the "declare-then-generate" two-phase contract. The object accumulates state through method calls (§2.1.1 and §2.1.2), then `.generate()` (implemented in M2/§2.8) materializes the DataFrame.

#### 2.1-3. INTERNAL DEPENDENCIES
None — this is the root section. All other sections in M1 depend on the constructor and the builder-pattern contract established here.

#### 2.1-4. CONSTRAINTS & INVARIANTS

**Explicit:**
- Schema definition and DGP specification happen in a single pass (one method call per column).
- The SDK "encapsulates all statistical machinery behind a minimal, strongly-typed API."

**Implicit:**
- `target_rows` must be a positive integer (the spec never states a minimum, but the generation algorithm assumes ≥1 row).
- `seed` must be an integer (implied by its pass-through to `np.random.default_rng`).
- The object must be mutable during declaration and effectively frozen before `.generate()` — no declarations after generation begins.

#### 2.1-5. EDGE CASES
- **`target_rows = 0` or negative**: Unaddressed. The generation engine (§2.4/§2.8) assumes a positive count.
- **Multiple `generate()` calls on the same instance**: The spec doesn't say whether this is allowed or whether the object is single-use.
- **No declarations before `generate()`**: The spec doesn't specify what happens if `.generate()` is called on a bare constructor with zero columns declared.
- **`seed` collision across retries**: Loop B increments seed by attempt number (`seed=42+attempt`), but this is defined in M5, not here. The SDK itself doesn't constrain seed values.

---

### Section 2.1.1 — Column Declarations (Step 1)

#### 2.1.1-1. PURPOSE
Defines the four `add_*()` method signatures that populate the SDK's internal column registry. This section specifies everything needed to declare categorical hierarchies, temporal dimensions, stochastic root measures, and structural derived measures — including validation rules that fire at declaration time.

#### 2.1.1-2. KEY MECHANISM

**`add_category(name, values, weights, group, parent=None)`**

Registers a categorical column. The key branching logic:
- If `parent=None`, this is a **group root**. `weights` is a flat list defining the marginal distribution P(col).
- If `parent` is specified, this is a **child** in a within-group hierarchy. `weights` can be either:
  - A flat list → same conditional distribution for every parent value (broadcast).
  - A dict mapping each parent value to a weight vector → per-parent conditional P(child | parent).

Validation at declaration time: auto-normalizes weights (so they sum to 1), rejects empty `values` lists, validates that `parent` exists and belongs to the same group.

**`add_temporal(name, start, end, freq, derive=[])`**

Registers a temporal column. The `derive` parameter triggers automatic extraction of calendar features (`day_of_week`, `month`, `quarter`, `is_weekend`). These derived columns become available as predictors in measure `param_model` effects — they are real columns in the registry, not computed on-the-fly.

**`add_measure(name, family, param_model)`**

Registers a **stochastic root measure** — a DAG root node with no incoming measure edges. `param_model` is a nested dict where each distribution parameter (e.g., `mu`, `sigma`) has:
- An `intercept` (base value).
- An `effects` dict mapping categorical column names to value→offset dicts.

At generation time, a parameter is computed as: θⱼ = β₀ + Σₘ βₘ(Xₘ). The `family` string selects the distribution.

> **Note (IS-5):** A `scale=None` kwarg appeared in earlier drafts of the spec but was removed in round-3. The spec never gave `scale` semantics; passing `scale=…` now raises `TypeError`. See `../remaining_gaps.md §4.2`.

**`add_measure_structural(name, formula, effects={}, noise={})`**

Registers a **structural (derived) measure**. The `formula` string references other measure columns by name and named effect placeholders. `effects` maps each placeholder to a categorical-value→numeric dict. `noise` specifies an optional additive error term with its own family and parameters. This call creates directed edges in the measure DAG (from each referenced measure to this one).

The critical invariant: every symbol in `formula` must resolve — either to a previously declared measure column or to a key in `effects`. No undefined terms allowed.

#### 2.1.1-3. INTERNAL DEPENDENCIES
- Depends on §2.1 for the `FactTableSimulator` instance.
- `add_category` with `parent` depends on a prior `add_category` call for that parent within the same group.
- `add_measure_structural` depends on prior `add_measure` or `add_measure_structural` calls for any measure referenced in `formula`.

#### 2.1.1-4. CONSTRAINTS & INVARIANTS

**Explicit:**
- Weights are auto-normalized.
- Empty `values` lists are rejected.
- `parent` must exist in the same group.
- DAG acyclicity: structural measures can only reference previously declared measures.
- Supported distribution families: `gaussian`, `lognormal`, `gamma`, `beta`, `uniform`, `poisson`, `exponential`, `mixture`.
- Every symbolic effect in `param_model` or `formula` must have an explicit numeric definition.
- Derived temporal features are limited to: `day_of_week`, `month`, `quarter`, `is_weekend`.

**Implicit:**
- Column names must be unique across the entire SDK instance (otherwise formula references and effect keys would be ambiguous).
- `values` list entries must be unique within a single `add_category` call (otherwise weight assignment is ambiguous).
- Per-parent conditional weight dicts must cover every parent value (the spec shows `...` ellipsis, never specifies what happens if a parent value is missing from the dict).
- The `mixture` family's `param_model` structure is never defined — it's unclear how component distributions and mixing weights are specified.
- `scale` parameter on `add_measure` is undocumented beyond its presence in the signature.
- `noise={}` (empty dict) on `add_measure_structural` presumably means zero noise, but this isn't stated.

#### 2.1.1-5. EDGE CASES
- **Single-value categorical**: `values=["Only"]` with `weights=[1.0]` — a degenerate constant column. Valid? The spec doesn't forbid it, but it would make orthogonality tests undefined (zero variance).
- **`mixture` distribution**: No parameter structure is defined. How are components specified? This is a gap.
- **Self-referencing `formula`**: e.g., `formula="cost * 2"` where `name="cost"`. The DAG acyclicity constraint should catch this, but the spec doesn't explicitly list self-reference as a checked case.
- **Temporal `derive` with conflicting freq**: If `freq="monthly"`, deriving `day_of_week` is meaningless. Not addressed.
- **Deeply nested hierarchy**: The spec shows 2-level hierarchies (hospital → department). There's no stated depth limit, but validation and generation logic only demonstrate single-parent chains.
- **Effects referencing non-existent columns**: e.g., `effects` in `param_model` naming a column that hasn't been declared yet. Declaration-time validation should catch this, but the timing constraint (must reference already-declared columns?) is only explicit for measures, not for effect predictors.
- **Per-parent weight dict missing a parent value**: If hospital has 5 values but the per-parent dict only covers 3, the behavior is undefined.

---

### Section 2.1.2 — Relationship & Pattern Declarations (Step 2)

#### 2.1.2-1. PURPOSE
Defines the inter-column and inter-group relationship API — the methods that establish statistical dependencies, independence guarantees, and narrative-driven anomaly patterns on top of the columns declared in §2.1.1. This is "Step 2" in the mandatory declare-columns-first-then-relationships ordering.

#### 2.1.2-2. KEY MECHANISM

**`declare_orthogonal(group_a, group_b, rationale)`**

Registers a statistical independence assertion between two entire dimension groups. The `rationale` string is metadata for downstream consumers (Phase 3 QA generation). The key propagation rule: if Group A ⊥ Group B, then *all* cross-group column pairs are independent — no O(n²) enumeration needed. This populates the `orthogonal_groups` list in schema metadata.

Downstream effects: generation uses P(A,B) = P(A) · P(B) (independent sampling); L1 validation runs χ² tests on root-level cross-group pairs; Phase 3 uses it for "Orthogonal Contrast" dashboards.

**`add_group_dependency(child_root, on, conditional_weights)`**

Registers a conditional distribution for a group root column given other group root columns. The `conditional_weights` is a nested dict: outer keys are values of the `on` column(s), inner keys are values of `child_root`, values are probabilities.

The **root-only constraint** is critical: both `child_root` and every column in `on` must be root columns (no parent). This keeps the cross-group dependency model flat and DAG-verifiable. The root-level dependency graph must itself be acyclic.

**`inject_pattern(type, target, col, params)`**

Registers a statistical anomaly pattern. `target` is a pandas query-style filter string. `type` selects from a fixed set of pattern types. `params` varies by type (e.g., `z_score` for outliers, `break_point` + `magnitude` for trend breaks). These are stored and later consumed by the generation engine (§2.8, stage γ) and validated by L3 checks (§2.9).

Pattern types: `outlier_entity`, `trend_break`, `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`.

**`set_realism(missing_rate, dirty_rate, censoring=None)`**

Optional. Registers data imperfection parameters. `missing_rate` and `dirty_rate` are presumably floats in [0,1]. `censoring` is unspecified beyond the parameter name.

#### 2.1.2-3. INTERNAL DEPENDENCIES
- All four methods depend on §2.1.1's column registry existing and being populated — they reference column names, group names, and group roots.
- `declare_orthogonal` references groups defined via `add_category` calls.
- `add_group_dependency` references root columns (validated as having `parent=None`).
- `inject_pattern` references column names and uses filter expressions that depend on known column values.

#### 2.1.2-4. CONSTRAINTS & INVARIANTS

**Explicit:**
- All Step 1 declarations must precede all Step 2 declarations (hard ordering from §2.5 prompt constraint #3).
- Cross-group dependencies are restricted to root columns only.
- Root-level dependency graph must be a DAG.
- Pattern types are drawn from a fixed enum.

**Implicit:**
- `declare_orthogonal` and `add_group_dependency` for the same pair of groups would be contradictory. The spec never explicitly forbids this or specifies which takes precedence.
- `inject_pattern` target strings must be valid pandas query syntax referencing declared columns and values. No validation of the target string is specified.
- For `add_group_dependency` with `on` containing multiple columns, the `conditional_weights` dict must be keyed on the Cartesian product of values of all `on` columns — the spec only shows single-column examples.
- `set_realism` can presumably be called at most once. Multiple calls aren't addressed.
- `convergence` and `seasonal_anomaly` pattern types are listed but never shown with example parameters or validation logic.

#### 2.1.2-5. EDGE CASES
- **Orthogonal + dependency contradiction**: Declaring `declare_orthogonal("A", "B")` and then `add_group_dependency(child_root_in_B, on=[root_in_A], ...)` — which wins? Not addressed.
- **Multi-column `on` in group dependency**: `on=["severity", "region"]` — the conditional_weights structure for joint conditioning is unspecified.
- **Pattern targeting zero rows**: `target="hospital == 'NonExistent'"` would match no rows. No error handling specified.
- **Pattern targeting nearly all rows**: An outlier pattern targeting 90% of rows would break the z-score semantics.
- **Patterns on structural measures**: Injecting an outlier on `cost` (structural) after it's computed from `wait_minutes` could break the formula relationship. The spec doesn't clarify whether pattern injection respects DAG constraints.
- **`convergence` and `seasonal_anomaly`**: No parameter schemas, no examples, no validation logic defined in §2.9. These are listed but not specified.
- **Duplicate pattern declarations**: Two `inject_pattern` calls with the same type/target/col — additive? Override? Not specified.

---

### Section 2.2 — Dimension Groups and Cross-Group Relations

#### 2.2-1. PURPOSE
Formalizes the **dimension group** abstraction as the unifying structural concept for organizing categorical and temporal columns. This section elevates the implicit grouping from §2.1.1's `group` parameter into an explicit first-class concept with rules for within-group hierarchy, cross-group orthogonality propagation, and temporal group treatment.

#### 2.2-2. KEY MECHANISM

A **dimension group** is a named container of columns with two structural properties:

1. **Hierarchy** (within-group): Each group has exactly one root column (`parent=None`). Child columns form a tree under the root, with conditional sampling: P(child | parent). The hierarchy is a tree, not a DAG — each column has at most one parent.

2. **Cross-group relations** (between groups): Two groups are either:
   - **Orthogonal** (explicitly declared via `declare_orthogonal`) → all cross-group pairs are independent.
   - **Dependent** (via `add_group_dependency`) → root columns have conditional distributions.
   - **Unspecified** → the default state; not orthogonal, not explicitly dependent. The spec says orthogonality is "opt-in, not default."

**Temporal as a special group**: The temporal column declared via `add_temporal` is the root of the `time` group. Derived calendar features (`day_of_week`, `month`, etc.) are child-like entities in this group, though they're derived by extraction rather than conditional sampling.

The output data structure is the `dimension_groups` dict:
```
{"group_name": {"columns": [...], "hierarchy": [...]}}
```
where `hierarchy` lists columns in root-first order.

#### 2.2-3. INTERNAL DEPENDENCIES
- Depends entirely on §2.1.1 (column declarations provide group membership and parent pointers).
- Depends on §2.1.2 for `declare_orthogonal` and `add_group_dependency` to define cross-group relations.
- This section is more of a **conceptual unification** than a new mechanism — it describes the abstraction that §2.1.1 and §2.1.2 jointly create.

#### 2.2-4. CONSTRAINTS & INVARIANTS

**Explicit:**
- Each categorical column belongs to exactly one group.
- Each group has exactly one root column.
- Cross-group dependencies are only between root columns.
- Root-level dependency graph must be a DAG.
- Orthogonality propagates to all cross-group column pairs.

**Implicit:**
- Every group must have at least one column (a group with zero columns is structurally impossible given the API, but what about a group name referenced in `declare_orthogonal` that has no columns?).
- The temporal group is implicitly named — the spec uses `"time"` in the metadata example but doesn't say whether the user controls this name or it's auto-assigned.
- Within-group hierarchies must be trees (single parent), not DAGs (multiple parents). This is implied by the `parent` singular parameter but not explicitly stated as a constraint.
- A group can have multiple leaf columns but only one root. The spec doesn't address whether a group can have multiple independent root columns (it cannot, given "each group has a root column" — singular).

#### 2.2-5. EDGE CASES
- **Group with only a root, no children**: Perfectly valid (e.g., `"patient": {"severity"}`), but the hierarchy is trivially flat.
- **Multiple groups with the same name**: Not addressed — presumably rejected, but no validation rule stated.
- **Temporal group naming**: If the user manually creates a group called `"time"` with categorical columns, does this conflict with the auto-created temporal group?
- **Orphan columns**: A categorical column whose declared `group` doesn't match any other column's group is a valid singleton group. The spec doesn't distinguish this from an error.
- **Forest within a group**: Could a group have columns A (root), B (parent=A), and C (parent=A) — two children of the same root? Yes, this is a valid tree. But could it also have D with no parent in the same group? That would create two roots, violating the single-root invariant.

---

### Section 2.3 — Closed-Form Measure Declaration

#### 2.3-1. PURPOSE
Formalizes the mathematical semantics of the two measure types and establishes the measure DAG as a first-class constraint. This section is the theoretical backbone for §2.1.1's `add_measure` and `add_measure_structural` — it explains *why* the closed-form approach was chosen and exactly how inter-measure relationships work without a separate correlation API.

#### 2.3-2. KEY MECHANISM

**Stochastic root measure** (mathematical form):

Y | X₁, …, Xₖ ~ D(θ₁, θ₂, …) where each parameter θⱼ = β₀ + Σₘ βₘ(Xₘ).

The Xₘ are categorical predictors (not other measures). This is a generalized linear model-style parameterization applied to any supported distribution family.

**Structural (derived) measure** (mathematical form):

Y = f(upstream measures) + g(categorical effects) + ε

where f is the `formula`, g maps categorical columns to numeric offsets, and ε is drawn from the `noise` distribution.

**Inter-measure correlation** arises through two mechanisms only:
1. **Direct structural dependency**: `cost = f(wait_minutes)` → measures are correlated because one is computed from the other.
2. **Shared predictors**: Two stochastic measures that both condition on `severity` will be marginally correlated even though they're conditionally independent given severity.

No separate `add_correlation()` API exists. This is a deliberate design decision to keep measure semantics self-contained and verifiable.

**Measure DAG**: All measure-to-measure dependencies form a DAG. Structural measures may only reference measures declared before them. Generation order is determined by topological sort of this DAG. The DAG edges come exclusively from `add_measure_structural` formula references.

#### 2.3-3. INTERNAL DEPENDENCIES
- Depends on §2.1.1 for the `add_measure` and `add_measure_structural` API definitions.
- Depends on §2.2 for the understanding that categorical predictors in `effects` come from dimension groups.
- The measure DAG concept feeds forward to M2 (generation order) and M4 (metadata output).

#### 2.3-4. CONSTRAINTS & INVARIANTS

**Explicit:**
- All measure dependencies must form a DAG.
- Structural measures may only reference measures declared before them.
- Stochastic measures are root nodes — they cannot depend on other measures.
- Every symbol in a formula or param_model must be numerically defined.

**Implicit:**
- The additive effects model (θⱼ = β₀ + Σₘ βₘ(Xₘ)) assumes **no interaction terms**. There's no way to specify that the effect of hospital on μ differs by severity level — effects are purely additive on the parameter scale.
- For distributions with constrained parameter spaces (e.g., σ > 0 for lognormal, α, β > 0 for gamma/beta), the additive effects model could produce invalid parameters. E.g., `sigma_intercept=0.35` with a large negative effect could yield σ < 0. No clamping or validation is specified.
- The `formula` string in structural measures is essentially a Python expression evaluated at runtime. The spec doesn't constrain which operations are allowed — just references to measures and named effects.
- Whether derived temporal columns (e.g., `month`) can be used as effects predictors in measures is implied (they're "available as predictors") but the mechanism by which they appear in the effects dict isn't shown with an example.

#### 2.3-5. EDGE CASES
- **Negative distribution parameters from additive effects**: `sigma = 0.35 + (-0.5)` → negative sigma. No guard specified.
- **Empty effects**: A stochastic measure with `param_model={"mu": 36.5, "sigma": 0.8}` (constant parameters, no effects dict) — the spec shows this as the "simple" case, so it's valid.
- **Circular structural formulas via indirect reference**: A → B → A is caught by DAG acyclicity, but what about A → B and B → A declared in sequence? The second declaration should fail because A is already declared and B references A, but then if B tries to reference A… actually, the "only reference previously declared measures" rule prevents this: B can reference A (declared before it), but A was declared first and couldn't have referenced B (not yet declared). The constraint is sufficient.
- **Structural measure with no formula referencing other measures**: e.g., `formula="severity_surcharge"` with only effects and no measure references. This is technically a stochastic-like measure declared as structural. The spec doesn't forbid it, but it arguably should be `add_measure` instead.
- **Long formula chains**: A DAG with depth 10+ (M1 → M2 → M3 → … → M10). No depth limit stated. Numeric precision and error propagation could become issues.
- **Measure depending on a temporal derived column**: Using `month` as a predictor in a stochastic measure's effects — this creates a generation ordering dependency (temporal must be generated before the measure). Valid, but the full DAG must account for it.

---

## 3. PHASE B: INTRA-MODULE DATA FLOW

---

### 3.1 ASCII Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SDK Surface (M1)                                 │
│                                                                         │
│  ┌───────────────┐                                                      │
│  │  §2.1         │                                                      │
│  │  Constructor   │──── FactTableSimulator(target_rows, seed) ────┐     │
│  │               │      (empty instance w/ config)                │     │
│  └───────────────┘                                                │     │
│                                                                   ▼     │
│  ┌───────────────┐    column descriptors    ┌──────────────────────┐    │
│  │  §2.1.1       │─────────────────────────►│                      │    │
│  │  Column Decls  │    (name, type, group,   │  INTERNAL STATE:     │    │
│  │               │     parent, family,       │  Declaration Store   │    │
│  │  add_category │     param_model, formula, │                      │    │
│  │  add_temporal │     effects, noise)       │  • column_registry[] │    │
│  │  add_measure  │                           │  • group_graph{}     │    │
│  │  add_measure_ │                           │  • measure_dag_edges │    │
│  │   structural  │                           │  • pattern_list[]    │    │
│  └───────────────┘                           │  • orthogonal_pairs[]│    │
│         │                                    │  • group_deps[]      │    │
│         │ column registry                    │  • realism_config?   │    │
│         │ must exist before                  │                      │    │
│         ▼                                    └──────────┬───────────┘    │
│  ┌───────────────┐    orthogonal pairs,                 │               │
│  │  §2.1.2       │    group dependencies,               │               │
│  │  Relationship │    pattern specs,          ──────────┘               │
│  │  & Pattern    │────realism config ────────►  (appended to            │
│  │  Declarations │                              Declaration Store)      │
│  │               │                                                      │
│  │  declare_orth │                                                      │
│  │  add_group_dep│                                                      │
│  │  inject_patt  │                                                      │
│  │  set_realism  │                                                      │
│  └───────────────┘                                                      │
│                                                                         │
│  ┌───────────────┐    (no new data produced;                            │
│  │  §2.2         │     conceptual lens over                             │
│  │  Dimension    │     column_registry and                              │
│  │  Groups       │     group_graph)                                     │
│  └───────────────┘                                                      │
│                                                                         │
│  ┌───────────────┐    measure_dag_edges                                 │
│  │  §2.3         │───► measure_dag_order[]                              │
│  │  Closed-Form  │    (topological sort of                              │
│  │  Measures     │     edges accumulated                                │
│  │               │     from §2.1.1 structural                           │
│  │               │     declarations)                                    │
│  └───────────────┘                                                      │
│                                                                         │
│  ════════════════════════════════════════════════════════════════════    │
│                     FROZEN DECLARATION STORE                            │
│                          (output boundary)                              │
│                                                                         │
│    ──► M2 (Generation Engine): full declaration store + seed            │
│    ──► M4 (Schema Metadata):  full declaration store                    │
│    ──► M3 (LLM Orchestration): typed Exceptions on validation failure   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Internal State — The Declaration Store

The SDK Surface accumulates a single compound data structure across sections. Its components and their sources:

| State Component | Populated By | Contents |
|---|---|---|
| **`column_registry`** | §2.1.1 | Ordered list of typed column descriptors. Each entry carries: `name`, `type` (categorical / temporal / measure), `group`, `parent`, `family`, `param_model`, `formula`, `effects`, `noise`, `derive`, `values`, `weights`, `scale`. Not every field is populated for every type. |
| **`group_graph`** | §2.1.1 (implicitly) + §2.2 (conceptually) | Dict mapping group name → `{root, columns[], hierarchy[]}`. Built incrementally: each `add_category` and `add_temporal` call appends to the group's column list and updates hierarchy pointers. |
| **`measure_dag_edges`** | §2.1.1 (`add_measure_structural`) + §2.3 (formalized) | Set of directed edges `(upstream_measure, downstream_measure)` extracted from `formula` symbol references. Topologically sorted to produce `measure_dag_order`. |
| **`orthogonal_pairs`** | §2.1.2 (`declare_orthogonal`) | List of `{group_a, group_b, rationale}` tuples. |
| **`group_deps`** | §2.1.2 (`add_group_dependency`) | List of `{child_root, on[], conditional_weights{}}` entries. |
| **`pattern_list`** | §2.1.2 (`inject_pattern`) | List of `{type, target, col, params}` entries. |
| **`realism_config`** | §2.1.2 (`set_realism`) | Optional `{missing_rate, dirty_rate, censoring}` singleton (or null). |

The store transitions through three lifecycle phases:

1. **Accumulating** — during Step 1 and Step 2 method calls. Validation fires incrementally (parent existence, DAG acyclicity, root-only constraint for group deps).
2. **Frozen** — after the last SDK method call returns and before `.generate()` is invoked. The spec implies this transition but doesn't define an explicit `freeze()` or `finalize()` call. The boundary is implicit: the `build_fact_table()` function ends with `return sim.generate()`, so the declaration phase ends when control passes to `generate()`.
3. **Consumed** — M2 reads it for generation, M4 reads it for metadata assembly, M5 reads the metadata derivative for validation.

---

### 3.3 Ordering Constraints

#### Explicitly Stated

1. **Step 1 before Step 2**: All column declarations (`add_category`, `add_temporal`, `add_measure`, `add_measure_structural`) must precede all relationship/pattern declarations (`declare_orthogonal`, `add_group_dependency`, `inject_pattern`, `set_realism`). This is hard constraint #3 from the LLM prompt in §2.5.

2. **Parent before child** (within `add_category`): A child column's `parent` must reference an already-declared column in the same group. This imposes root-first declaration order within each group's hierarchy.

3. **Upstream measure before downstream** (within `add_measure_structural`): A structural measure's `formula` may only reference previously declared measures. This forces declaration order to match topological order of the measure DAG.

#### Implicitly Required But Not Stated

4. **Group existence before cross-group relations**: `declare_orthogonal(group_a, group_b)` requires both groups to have at least one column already declared. This is logically necessary (you can't reference a group that doesn't exist) but no explicit validation rule is stated for it.

5. **Predictor columns before measures that reference them**: If `add_measure("wait_minutes", ..., effects={"severity": {...}})` references `severity` as a predictor, `severity` must already be in the column registry. The spec says effects predictors must be defined, but whether this is checked at declaration time or deferred to generation time is ambiguous.

6. **`add_group_dependency` columns must be roots**: The `child_root` and all columns in `on` must have `parent=None`. This is explicitly stated as a constraint, but the validation *timing* (at declaration time vs. at generation time) is not specified. Given that M1's role is declaration-time validation, it should fire here.

7. **`inject_pattern` column must exist**: The `col` parameter must name a declared column. The `target` filter string references column names and values. Both depend on Step 1 being complete, which is guaranteed by the Step 1 → Step 2 ordering, but no explicit validation of the filter string's syntactic correctness is specified.

8. **No mixing of Step 1 and Step 2 calls**: The LLM prompt enforces a clean partition, but the SDK itself doesn't describe a mechanism that enforces this (e.g., a state-machine transition that rejects `add_category` after `declare_orthogonal`). This is enforced by convention (the generated script structure) rather than by API mechanics.

---

### 3.4 Cross-Check Against Stage 2 Overview INTERFACE OUT

#### §2.1 — INTERFACE OUT: "`FactTableSimulator(target_rows, seed)` constructor; entry point that M3's generated script instantiates."
**Status: CONSISTENT.** The constructor is the sole entry point, and M3 produces the script that calls it.

#### §2.1.1 — INTERFACE OUT: "Populates the internal column registry — a list of typed column descriptors (name, type, group, parent, family, param_model, formula, effects, noise). Consumed by M2 for generation order and by M4 for the `columns` array in `schema_metadata`."
**Status: CONSISTENT, with a minor omission.** The overview lists `(name, type, group, parent, family, param_model, formula, effects, noise)` as the descriptor fields. Analysis adds `values`, `weights`, `derive`, `scale`, and `measure_type` (stochastic vs. structural) as additional fields that must be present in the registry for downstream consumers to function. The overview's list is representative but not exhaustive.

#### §2.1.2 — INTERFACE OUT: "Populates three internal registries: orthogonal-pair list, group-dependency list (with `conditional_weights`), and pattern list (type, target, col, params). All three propagate into `schema_metadata` fields consumed by M4 and M5."
**Status: CONSISTENT, with a minor omission — MISMATCH flagged.** The overview lists three registries but omits `realism_config` as a fourth. `set_realism()` is defined in §2.1.2 and its output must persist in the declaration store for M2's δ stage.

#### §2.2 — INTERFACE OUT: "The `dimension_groups` dict structure (group name → `{columns, hierarchy}`) that M4 emits verbatim into `schema_metadata["dimension_groups"]`."
**Status: CONSISTENT.** This is a conceptual lens over data already accumulated in §2.1.1, materialized as a dict structure that M4 emits.

#### §2.3 — INTERFACE OUT: "The measure DAG edge set and topological order (`measure_dag_order`), consumed by M2 for generation sequencing and by M4 for `schema_metadata["measure_dag_order"]`."
**Status: CONSISTENT.** The DAG edges are accumulated during §2.1.1's `add_measure_structural` calls; §2.3 formalizes the topological sort.

#### Summary of Mismatches

| Section | Finding | Severity |
|---|---|---|
| §2.1.1 | Overview's descriptor field list is incomplete (missing `values`, `weights`, `derive`, `scale`, `measure_type`) | Minor — representative vs. exhaustive listing |
| §2.1.2 | Overview lists three internal registries; `realism_config` is a fourth | Minor — `set_realism` is marked optional, but it is still a distinct registry item |

No major mismatches found. The overview is accurate at the level of abstraction it targets.
