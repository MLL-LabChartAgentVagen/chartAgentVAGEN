# Stage 2 Deep Dive: Generation Engine (M2)

**Module Sections:** 2.4, 2.8
**Pipeline Position:** Receives frozen declaration store + seed from M1; outputs Master DataFrame to M5 and metadata material to M4. Subject to Loop B re-execution from M5.

---

## 1. SUMMARY

The Generation Engine converts a validated, frozen declaration store and a seed integer into a deterministic, bit-for-bit reproducible Master DataFrame via a four-stage pipeline (skeleton → measures → patterns → realism). Its most complex section is §2.8 (Deterministic Engine Execution), because it must correctly implement the unified full-column DAG traversal, dispatch between four column types with distinct sampling/evaluation semantics, and maintain a single RNG stream whose consumption order is the sole guarantor of reproducibility. The most significant ambiguity is the **routing of schema metadata**: the stage1_module_map shows M4 reading declarations directly from M1, while §2.8's code returns a metadata dict as part of its output tuple ostensibly destined for M4 — the spec does not fully reconcile whether M4 is an independent consumer of M1 or a downstream consumer of M2. **Confidence that the spec fully specifies this module: medium.** The four-stage pipeline and DAG-ordering logic are well-defined, but several implementation-critical details are left open — formula evaluation mechanism, pattern composition semantics when targets overlap, realism interaction rules, post-processing behavior, and the structural-measure noise default.

---

## 2. PHASE A: INTERNAL SECTION ANALYSIS

### Section 2.4 — DAG-Ordered Event-Level Row Generation

#### 2.A.1 PURPOSE

This section defines the **conceptual generation algorithm** — the logical model for how each row of the Master DataFrame is produced. It establishes that all columns (categorical, temporal, and measure) form a single unified DAG, that rows are generated as independent atomic events rather than from a materialized cross-product, and that `target_rows` is inherited from Phase 1. It is the architectural blueprint that §2.8 implements concretely.

#### 2.A.2 KEY MECHANISM

The mechanism has three layers:

**Layer 1 — The Full Generation DAG.** All columns — not just measures — are placed into a single directed acyclic graph. Edges arise from four sources: within-group hierarchy (`parent`), cross-group root dependencies (`add_group_dependency`), temporal derivation (`derive`), and measure references (both stochastic effects and structural formulas). The engine resolves this into a topological order, which dictates the generation sequence. The spec illustrates this with a concrete layering:

- **Layer 0** — Independent roots: columns with no incoming edges (e.g., `hospital`, `severity`, `visit_date`).
- **Layer 1** — Dependent non-measure columns: categorical children sampled conditionally on parents, temporal derivations extracted deterministically, and cross-group root dependents sampled from conditional weight tables.
- **Layer 2** — Stochastic root measures: sampled from parameterized distributions where parameters are functions of already-generated categorical columns.
- **Layer 3** — Structural measures: evaluated in measure-DAG topological order, referencing upstream measures and categorical effects.

**Layer 2 — Row Generation Algorithm.** For each of the `target_rows` rows, the algorithm walks the topological order: first all non-measure columns (Step 1), then all measures in measure-DAG order (Step 2). After the full DataFrame is assembled, post-generation passes apply pattern injection and optional realism injection (Step 3). The per-row loop produces independent atomic events — there is no inter-row dependency during generation, only intra-row dependency along DAG edges.

**Layer 3 — `target_rows` contract.** The section specifies a complexity-tier table mapping scenario complexity to row counts (Simple: 200–500, Medium: 500–1000, Complex: 1000–3000). This value originates from Phase 1 and is passed through unchanged.

#### 2.A.3 INTERNAL DEPENDENCIES

- **Depends on §2.8:** Section 2.4 is purely conceptual — it defines no executable code. It provides the algorithm that §2.8's `generate()` method implements. Without §2.8, this section has no runtime manifestation.
- **Receives from M1 (external):** The column registry, dimension-group graph, measure DAG edges, and pattern list must already be validated and frozen before this algorithm can execute.

#### 2.A.4 CONSTRAINTS & INVARIANTS

**Explicit:**

- **C1 — Atomic grain:** Each row represents one indivisible event. No row is a pre-aggregated summary.
- **C2 — No cross-product materialization:** The engine does not build a full dimensional cross-product and then sample into it. Rows are generated independently.
- **C3 — DAG ordering:** All columns are generated in topological order of the full DAG. A column is never generated before its parents/dependencies.
- **C4 — `target_rows` inheritance:** The value comes from Phase 1's scenario context; M2 does not determine or modify it.
- **C5 — Post-generation ordering:** Pattern injection and realism injection happen *after* the full DataFrame is materialized, not during per-row generation.

**Implicit:**

- **C6 — Row independence:** Since each row is an independent atomic event, there is no mechanism for inter-row correlation beyond what emerges from shared categorical conditioning and post-hoc pattern injection. Time-series autocorrelation is not modeled at the per-row level.
- **C7 — Exact row count:** The algorithm iterates `target_rows` times, implying the output DataFrame has exactly `target_rows` rows (before any potential filtering by realism/censoring). Yet §2.9's L1 validation allows a 10% tolerance, suggesting some process may alter the count.
- **C8 — Measure parameters depend only on non-measure columns:** The topological layering places all non-measure columns before all measures. Stochastic measures reference categorical predictors (already generated); structural measures reference upstream measures. No measure can influence the sampling of a categorical or temporal column.

#### 2.A.5 EDGE CASES

- **Single-column DAG:** If there is only one independent root and no children, the "DAG" is trivial. The spec doesn't discuss degenerate scenarios but the algorithm handles them by default (topological sort of a single node is that node).
- **Zero patterns / zero realism:** Steps 3.11 and 3.12 become no-ops. The spec handles this via optionality but doesn't state behavior explicitly.
- **`target_rows` at boundary of tiers:** The tier table gives ranges (e.g., 200–500). What determines the exact value within a range? This is a Phase 1 concern, but M2 receives it as a single integer — no ambiguity at M2's boundary.
- **Very large structural measure chains:** If structural measures form a long chain (A → B → C → D → ...), the topological sort handles it, but numerical error could accumulate through successive formula evaluations plus noise injections. The spec does not address floating-point stability.
- **Temporal-only predictor effects:** The spec shows categorical columns as predictors for stochastic measures. Can temporal-derived columns (e.g., `month`, `day_of_week`) appear in a measure's `effects`? The one-shot example does not include this, but §2.1 states derived columns are "available as predictors for measures," implying yes. The generation algorithm in §2.4 places temporal derivations in Layer 1 (before measures), so they would be available. However, the `param_model` effect structure assumes discrete categories — temporal derived columns like `month` are categorical, so this works, but continuous temporal values (the raw date) would not fit the effect model without discretization.
- **Pattern injection on structural measures:** Patterns target a column (`col`). If a structural measure is targeted by an outlier pattern, the injected value may break the deterministic formula relationship, causing §2.9 L2 residual checks to fail. The spec does not discuss ordering or priority between pattern injection and structural-formula consistency.

---

### Section 2.8 — Deterministic Engine Execution

#### 2.A.1 PURPOSE

This section provides the **concrete implementation** of the generation algorithm described in §2.4. It specifies the `FactTableSimulator.generate()` method as a four-stage deterministic pipeline (α, β, γ, δ) that converts the frozen declaration store plus a seed into a Master DataFrame and raw schema metadata. It is the only section in M2 that produces an artifact crossing the module boundary.

#### 2.A.2 KEY MECHANISM

The `generate()` method is structured as a pipeline of four composable stages, expressed mathematically as:

$$M = \tau_{\text{post}} \circ \delta^{?} \circ \gamma \circ \beta \circ \alpha(\text{seed})$$

**Pre-flight: DAG construction and validation.** Before any generation, the method calls `_build_full_dag()` to assemble the unified DAG across all column types, then computes `topological_sort(full_dag)` to produce the master generation order. This is a redundant safety check — M1 already validated acyclicity — but ensures the engine never operates on an invalid graph.

**Stage α — Skeleton (`_build_skeleton`).** Generates all non-measure columns in topological order. This encompasses:

- Independent root categoricals: sampled from declared marginal weights.
- Dependent categoricals (children): sampled from per-parent conditional weight vectors.
- Cross-group root dependents: sampled from conditional weight tables keyed by upstream root values.
- Temporal root: sampled uniformly within `[start, end]` at declared frequency.
- Temporal derived columns: deterministically extracted (e.g., `DOW()`, `MONTH()`).

The output is a partially populated row dict (or DataFrame) with all non-measure columns filled.

**Stage β — Measures.** Iterates over columns in topological order, handling only measure columns:

- `_sample_stochastic(col, rows, rng)`: Computes each distribution parameter as `intercept + Σ effects(predictor_value)` for the current row's categorical context, then draws from the named distribution family.
- `_eval_structural(col, rows, rng)`: Evaluates the declared formula referencing upstream measure values and named effects from the current row's context, then adds noise drawn from the declared noise distribution.

The `rng` argument is the seeded `numpy.random.Generator`, ensuring determinism.

**Stage γ — Pattern injection (`_inject_patterns`).** Operates on the complete DataFrame (not per-row). For each declared pattern, selects the target subset via the `target` filter expression, then applies the pattern-specific transformation (e.g., scaling values to achieve a target z-score for outliers, shifting values after a breakpoint for trend breaks).

**Stage δ — Realism injection (optional).** If `set_realism()` was called, introduces missing values, dirty entries, and censoring. The `?` superscript indicates this stage is skipped when no realism config exists.

**Post-processing (`_post_process`).** The spec mentions this as `τ_post` but does not detail what it does. Presumably it converts the internal row representation to a `pd.DataFrame` and performs any final type casting.

**Return value:** `Tuple[pd.DataFrame, dict]` — the Master DataFrame and the raw material for schema metadata. The metadata is built by `_build_schema_metadata()`, a separate method that reads the declaration store (not the generated data).

#### 2.A.3 INTERNAL DEPENDENCIES

- **Depends on §2.4:** The algorithm implemented here is the one specified in §2.4. Every design decision (DAG ordering, event-level generation, post-generation pattern injection) comes from §2.4.
- **Receives from M1 (external):** The frozen declaration store (column registry, dimension-group graph, measure DAG edges, pattern list, realism config) and the `seed` integer.

#### 2.A.4 CONSTRAINTS & INVARIANTS

**Explicit:**

- **C1 — Determinism:** Given the same `seed` and declarations, output is bit-for-bit reproducible. The `rng` is initialized once from `self.seed` and consumed sequentially.
- **C2 — No LLM calls:** The entire `generate()` pipeline is pure computation. The LLM's contribution ended when the SDK script was written.
- **C3 — Stage ordering is fixed:** α → β → γ → δ. Stages cannot be reordered or interleaved.
- **C4 — Full DAG topological sort:** Both the skeleton (α) and measures (β) follow the same `topo_order` list. The code iterates `topo_order` once, dispatching each column to the appropriate handler based on type.

**Implicit:**

- **C5 — Single RNG stream:** The code creates one `rng` and passes it to every stage. This means the order of random draws is fixed by the topological order. Adding or removing a column changes all downstream random draws — the determinism guarantee is global, not per-column.
- **C6 — Pattern injection sees the full DataFrame:** γ cannot apply patterns during per-row generation because patterns like `trend_break` need temporal context across rows. This is why patterns are a post-generation pass.
- **C7 — `_build_schema_metadata()` reads declarations, not data:** The metadata dict is built from the declaration store, not from the generated DataFrame. This means metadata describes the *intended* structure, not the *realized* structure (e.g., if realism injection removes some category values via censoring, metadata still lists them).
- **C8 — `_post_process` is unspecified:** The spec does not detail what post-processing occurs. At minimum it must convert to `pd.DataFrame`, but it may also enforce dtype constraints, clip values, or round.

#### 2.A.5 EDGE CASES

- **Empty pattern list:** Stage γ becomes a no-op. The code likely iterates an empty list, which is safe but unspecified.
- **Structural measure with no noise:** If `noise={}` is passed to `add_measure_structural`, `_eval_structural` presumably adds zero noise. The spec doesn't explicitly state the default — is it zero noise or is `noise` required?
- **Seed collision in auto-fix loop:** §2.9 re-runs generation with `seed=42+attempt`. If the original seed is 42, retries use 43, 44, 45. But if the user's scenario specifies a different seed, the auto-fix offset is applied to that base seed. The spec hardcodes `42` in the example, which may be a simplification.
- **Formula evaluation safety:** `_eval_structural` must evaluate a formula string. The spec doesn't specify the evaluation mechanism. If it uses Python's `eval()`, there are security implications (though the script is already LLM-generated and sandboxed). If it uses a restricted expression parser, the set of allowed operations matters — the spec says "formula references previously declared measure columns by name and named effects" but doesn't enumerate allowed operators beyond basic arithmetic shown in examples (`*`, `+`, `-`).
- **Pattern injection on columns modified by realism:** If γ injects a pattern (e.g., outlier) and then δ introduces missing values in the same column, the pattern signal may be degraded. The spec's stage ordering (γ before δ) means patterns are injected first, then realism can corrupt them. This could cause L3 validation failures.
- **Interaction between `_build_schema_metadata()` and the generated DataFrame:** The method is called after `_post_process(rows)` in the return statement, but it reads declarations, not `rows`. If post-processing alters the schema (e.g., adds a column), metadata would be inconsistent. The spec implies post-processing is lightweight, but this is not guaranteed.
- **Very large `target_rows`:** The algorithm is O(target_rows × num_columns) for the main loop, plus whatever pattern injection costs (which may involve DataFrame-wide operations). For the specified range (200–3000), this is trivially fast, but the spec doesn't set an upper bound.

---

## 3. PHASE B: INTRA-MODULE DATA FLOW

### 3.1 ASCII Data Flow Diagram

```
                    ┌─────────────────────────────────────────┐
                    │         EXTERNAL INPUTS TO M2           │
                    │                                         │
                    │  From M1 (frozen declaration store):    │
                    │   • column registry                     │
                    │   • dimension-group graph               │
                    │   • measure DAG edges                   │
                    │   • pattern list                        │
                    │   • realism config                      │
                    │   • seed (integer)                      │
                    └──────────────────┬──────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    §2.4 — Conceptual Algorithm                      │
│                                                                     │
│  Defines:                                                           │
│   • Full generation DAG (all column types unified)                  │
│   • Topological layer assignment                                    │
│   • Row generation algorithm (per-row loop + post-gen passes)       │
│   • target_rows contract (from Phase 1)                             │
│                                                                     │
│  Produces no runtime artifact — purely architectural spec           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                       «implements»
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    §2.8 — generate() Pipeline                       │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Pre-flight                                                │      │
│  │  declaration store ──► _build_full_dag() ──► topo_sort()  │      │
│  │                                                │          │      │
│  │                                         topo_order        │      │
│  │                                                │          │      │
│  │  seed ──► np.random.default_rng(seed) ──► rng  │          │      │
│  └────────────────────────────────────────────┬───┘          │      │
│                                               │              │      │
│                                               ▼              │      │
│  ┌───────────────────────────────────────────────────┐       │      │
│  │ Stage α: _build_skeleton(topo_order, rng)         │       │      │
│  │                                                   │       │      │
│  │  Inputs: topo_order, rng, declaration store       │       │      │
│  │  Process: for each non-measure col in order:      │       │      │
│  │    • root categorical → sample from weights       │       │      │
│  │    • child categorical → sample | parent value    │       │      │
│  │    • cross-group dep → sample | upstream root     │       │      │
│  │    • temporal root → sample in [start, end]       │       │      │
│  │    • temporal derived → extract from root         │       │      │
│  │  Output: rows with all non-measure cols filled    │       │      │
│  └────────────────────┬──────────────────────────────┘       │      │
│                       │                                      │      │
│                  rows (partial)                               │      │
│                       │                                      │      │
│                       ▼                                      │      │
│  ┌───────────────────────────────────────────────────┐       │      │
│  │ Stage β: Measure generation loop                  │       │      │
│  │                                                   │       │      │
│  │  Inputs: topo_order, rows, rng, declarations      │       │      │
│  │  Process: for each measure col in topo_order:     │       │      │
│  │    • stochastic → _sample_stochastic(col,rows,rng)│       │      │
│  │    •   params = intercept + Σ effects             │       │      │
│  │    •   draw from family(params) via rng           │       │      │
│  │    • structural → _eval_structural(col,rows,rng)  │       │      │
│  │    •   evaluate formula with upstream values      │       │      │
│  │    •   add noise drawn via rng                    │       │      │
│  │  Output: rows now fully populated                 │       │      │
│  └────────────────────┬──────────────────────────────┘       │      │
│                       │                                      │      │
│                  rows (complete DataFrame)                    │      │
│                       │                                      │      │
│                       ▼                                      │      │
│  ┌───────────────────────────────────────────────────┐       │      │
│  │ Stage γ: _inject_patterns(rows, rng)              │       │      │
│  │                                                   │       │      │
│  │  Inputs: full DataFrame, pattern list, rng        │       │      │
│  │  Process: for each pattern:                       │       │      │
│  │    • filter rows by target expression             │       │      │
│  │    • apply pattern transformation to col          │       │      │
│  │  Output: DataFrame with patterns injected         │       │      │
│  └────────────────────┬──────────────────────────────┘       │      │
│                       │                                      │      │
│                       ▼                                      │      │
│  ┌───────────────────────────────────────────────────┐       │      │
│  │ Stage δ (optional): _inject_realism(rows, rng)    │       │      │
│  │                                                   │       │      │
│  │  Inputs: DataFrame, realism config, rng           │       │      │
│  │  Process: inject missing, dirty, censored values  │       │      │
│  │  Output: DataFrame with imperfections             │       │      │
│  └────────────────────┬──────────────────────────────┘       │      │
│                       │                                      │      │
│                       ▼                                      │      │
│  ┌───────────────────────────────────────────────────┐       │      │
│  │ Post: _post_process(rows)                         │       │      │
│  │     + _build_schema_metadata()                    │       │      │
│  │                                                   │       │      │
│  │  _post_process: rows → pd.DataFrame               │       │      │
│  │  _build_schema_metadata: declarations → dict      │       │      │
│  └────────────────────┬──────────────────────────────┘       │      │
│                       │                                      │      │
└───────────────────────┼──────────────────────────────────────┘      │
                        │                                             │
                        ▼                                             │
         ┌──────────────────────────────────┐                         │
         │       MODULE OUTPUTS             │                         │
         │                                  │                         │
         │  → M5: Master DataFrame          │                         │
         │        (pd.DataFrame)            │                         │
         │                                  │                         │
         │  → M4: schema_metadata raw       │                         │
         │        material (dict)           │                         │
         └──────────────────────────────────┘                         │
                                                                      │
         ┌──────────────────────────────────┐                         │
         │       FEEDBACK INPUT             │                         │
         │                                  │                         │
         │  ← M5: re-execution signal       │◄─── Loop B (max 3)     │
         │    (adjusted params + new seed)  │                         │
         └──────────────────────────────────┘
```

### 3.2 Internal State Accumulation

M2 is a stateless pipeline in the sense that it does not maintain persistent state across invocations — each call to `generate()` builds everything from scratch. However, *within* a single invocation, state accumulates through the four stages in a strictly linear fashion:

| Stage | State After Completion | What Accumulated |
|-------|----------------------|------------------|
| Pre-flight | `topo_order` (list), `rng` (Generator) | The generation plan and randomness source are fixed. |
| α (skeleton) | `rows` partially populated: all non-measure columns filled for all `target_rows` rows | Categorical context is now available. Every row has its dimensional identity. The `rng` has advanced by the number of random draws needed for categorical and temporal sampling. |
| β (measures) | `rows` fully populated: all columns filled | Measure values exist for every row. The `rng` has advanced further by one draw per stochastic measure per row, plus one noise draw per structural measure per row. |
| γ (patterns) | `rows` modified in-place at targeted subsets | Specific cells have been scaled, shifted, or otherwise transformed. The `rng` may have advanced if pattern injection uses randomness (not fully specified). |
| δ (realism) | `rows` modified with NaN/dirty/censored values | Some cells that previously held clean values now hold missing markers, dirty strings, or censored bounds. |

The critical observation is that **the `rng` is the implicit state thread** tying all stages together. Because a single `numpy.random.Generator` is consumed sequentially, the random state after stage α determines the exact draws in stage β, and so on. This is what makes the pipeline deterministic for a given seed, but also means that any change to declarations (adding/removing a column) alters the entire downstream random sequence.

### 3.3 Ordering Constraints

**Explicitly stated:**

- α before β: Non-measure columns must exist before measures can reference categorical predictors.
- β before γ: Measure values must exist before patterns can modify them.
- γ before δ: Patterns are injected into clean data; realism degrades it afterward.
- Within α: columns generated in topological order of the full DAG.
- Within β: measures generated in topological order of the measure sub-DAG.

**Implied but not explicitly stated:**

- **O1 — Pre-flight before everything:** `_build_full_dag()` and `topological_sort()` must complete before α begins. The code shows this, but the spec doesn't call it out as a named constraint.
- **O2 — `_build_schema_metadata()` is order-independent of `_post_process`.** The metadata method reads declarations, not generated data, so it could run at any point after M1 freezes the declaration store. The spec places it at the return statement, but this is a code-organization choice, not a data dependency.
- **O3 — Pattern injection order across multiple patterns is unspecified.** If two patterns target overlapping rows and the same column, the final value depends on application order. The spec iterates the pattern list but doesn't define priority or composition semantics.
- **O4 — Realism injection order across imperfection types is unspecified.** If `missing_rate` and `dirty_rate` both apply to the same column, does a cell get set to missing *or* dirty, or could both apply? The spec doesn't define interaction semantics.
- **O5 — The single `topo_order` list serves double duty.** The code iterates it for α (skipping measures) and for β (processing only measures). Whether this is one pass with type-dispatch or two passes is an implementation choice left open.

### 3.4 Cross-Check Against INTERFACE OUT

**§2.4 — overview states:** *"Internal only. No artifact crosses the module boundary."*
**Status: ✅ CONSISTENT.** Phase A confirms §2.4 is a conceptual specification with no runtime output.

**§2.8 — overview states:** *"`Tuple[pd.DataFrame, dict]` — Master DataFrame goes to M5; metadata dict goes to M4."*
**Status: ⚠️ CONSISTENT WITH AMBIGUITY.**

The output shape matches. However, the **metadata routing** is ambiguous:

- The stage1_module_map draws a direct arrow from **M1 → M4** (declaration store), stating M4 "reads the finalized declarations; it does not need the generated rows."
- The stage2_overview draws an arrow from **M2 → M4** (metadata dict), as part of §2.8's return tuple.

These two statements are not contradictory if M4 receives input from *both* M1 and M2, or if `_build_schema_metadata()` within M2 is effectively the M4 logic co-located in M2's code. But the spec does not explicitly reconcile this. The most coherent reading is that the "M1 → M4" arrow represents M4 accessing the same declaration store that M2 also accesses (since both live on the same `FactTableSimulator` instance), and `_build_schema_metadata()` is where M4's work actually happens, making M4 less of an independent module and more of a build step within M2's return path.

All other boundary shapes — DataFrame structure, Loop B feedback path, seed offset convention — match across all three reference documents.
