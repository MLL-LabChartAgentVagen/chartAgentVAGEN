# Stage 2 Deep Dive: Schema Metadata (M4)

## 1. SUMMARY

Module M4 (Schema Metadata) is responsible for building the `schema_metadata` dictionary — a structured, machine-readable contract that encodes the semantics of the generated fact table for consumption by the Validation Engine (M5) and Phase 3 (view extraction and QA generation). Its only section (§2.6) is moderate in complexity on its own but raises the most significant ambiguity in the entire module: the example metadata performs a **lossy projection** of the declaration store, dropping categorical weights, distribution parameters, formula definitions, and noise specifications — yet M5's validation checks demonstrably require all of these fields. This creates an unresolved tension: either the §2.6 example is illustrative rather than exhaustive, or M5 must access the declaration store directly, contradicting the module map's stated interface. Confidence that the spec fully specifies this module is **medium** — the metadata *structure* is clear, but the *completeness* of its fields relative to downstream consumer needs is ambiguous and the single example leaves multiple field-inclusion questions unanswered.

---

## 2. PHASE A: INTERNAL SECTION ANALYSIS

### Section 2.6 — Schema Metadata Output

#### 2.1 PURPOSE

Section 2.6 defines the exact structure of the `schema_metadata` dictionary — the contract that bridges Phase 2's generated data with Phase 3's view extraction and QA generation. It solves the problem of making the *semantics* of the generated table machine-readable: downstream consumers need to know not just the column names in a DataFrame, but which columns form hierarchies, which are orthogonal, what the measure DAG looks like, and what patterns were injected. Without this metadata, Phase 3 would have to reverse-engineer the table's structure from raw data.

#### 2.2 KEY MECHANISM

The mechanism is a structured dictionary with seven top-level keys. Walking through each:

**`dimension_groups`** — A dict keyed by group name. Each value contains `columns` (all columns in the group, including derived temporals) and `hierarchy` (the ordered chain from root to deepest child). For the temporal group, `hierarchy` contains only the declared root temporal column, not derived features, even though `columns` includes them. This distinction matters: hierarchy defines the sampling chain, while columns enumerates everything available as a predictor.

```python
"entity": {"columns": ["hospital", "department"], "hierarchy": ["hospital", "department"]}
"time":   {"columns": ["visit_date", "day_of_week", "month"], "hierarchy": ["visit_date"]}
```

**`orthogonal_groups`** — A list of `{group_a, group_b, rationale}` objects, directly mirroring each `declare_orthogonal()` call. This is consumed by M5 for chi-squared independence checks (L1) and by Phase 3 for "Orthogonal Contrast" dashboard enumeration.

**`group_dependencies`** — A list of `{child_root, on}` objects corresponding to `add_group_dependency()` calls. Notably, the `conditional_weights` themselves are **not** included in the example output — only the structural edge (`child_root` depends on `on`). This is a significant detail: Phase 3 knows *that* a dependency exists but not the exact weight table. M5, however, needs the weights for L2 validation (conditional transition deviation check in §2.9), which means M5 must source weights from somewhere other than this dictionary, or the example is incomplete.

**`columns`** — A list of typed column descriptors. Each entry carries different fields depending on type:

- *Categorical*: `name`, `group`, `parent` (null for roots), `type: "categorical"`, `cardinality`.
- *Temporal*: `name`, `group`, `type: "temporal"`, `derived` (list of derived feature names).
- *Measure*: `name`, `type: "measure"`, `measure_type` ("stochastic" or "structural"), and conditionally `family` (for stochastic) or `depends_on` (for structural).

This is a flattened registry — all column types in one list, discriminated by the `type` field.

**`measure_dag_order`** — A flat list giving the topological sort of the measure sub-DAG. In the example: `["wait_minutes", "cost", "satisfaction"]`. This is used by M2 for generation sequencing and by Phase 3 for causal reasoning QA.

**`patterns`** — A list of pattern descriptors, each carrying `type`, `target` (filter expression), `col`, and type-specific params (e.g., `break_point` for trend breaks). These are consumed by M5 for L3 pattern validation and by Phase 3 for crafting "hard questions" about injected anomalies.

**`total_rows`** — The declared `target_rows` value. Used by M5's L1 check (row count within 10% of target).

#### 2.3 INTERNAL DEPENDENCIES

Section 2.6 is the only section in M4, so there are no intra-module dependencies. However, it depends on inputs from outside the module boundary:

- The declaration store from M1 (column registry, group graph, orthogonal pairs, dependency list, pattern list) provides all the structural information.
- The stage2_overview states M4 also receives the "generated DataFrame" as input, but §2.6 itself shows no field that requires the actual row data — every field can be derived from declarations alone. The `total_rows` comes from the constructor argument, not from `len(df)`. This is a subtle tension: M4 may receive the DataFrame but not actually need it for metadata construction.

#### 2.4 CONSTRAINTS & INVARIANTS

**Explicit:**

- Every column in the DataFrame must appear in the `columns` list (completeness).
- `measure_dag_order` must be a valid topological sort of the measure dependency graph.
- `orthogonal_groups` entries must reference valid group names from `dimension_groups`.
- `group_dependencies` entries reference root columns only.
- `total_rows` matches the declared `target_rows`.

**Implicit:**

- **Column-group consistency**: Every column listed in a `dimension_groups` entry must also appear in the `columns` array with a matching `group` field, and vice versa. The spec does not state this cross-referencing rule explicitly.
- **Hierarchy ordering**: The `hierarchy` list within each dimension group is implicitly root-first (root at index 0, deepest child last). This is assumed by M5, which reads `hierarchy[0]` as the root for chi-squared tests, but never stated as a formal requirement.
- **Derived temporal exclusion from hierarchy**: The example shows `"time": {"columns": [..., "day_of_week", "month"], "hierarchy": ["visit_date"]}`, implying derived columns are in `columns` but not `hierarchy`. This rule is demonstrated but not stated.
- **No duplicate column names**: Implied by the flat list structure and the fact that columns are referenced by name throughout.
- **Pattern `col` must reference a measure**: Every pattern's `col` field must name a column that appears in `columns` with `type: "measure"`. Not stated.
- **`depends_on` completeness**: For structural measures, `depends_on` should list all upstream measure dependencies. Whether it also includes categorical effect dependencies is ambiguous — the example only shows measure-to-measure edges.
- **Missing fields in `columns` for categorical entries**: The example omits `values` and `weights` from categorical column descriptors (only `cardinality` is present). Yet M5's L1 validation checks marginal weights against declared weights. Either M5 sources weights from the declaration store directly (not via `schema_metadata`), or `schema_metadata` needs additional fields not shown.

#### 2.5 EDGE CASES

**Single-column dimension groups:** A group with exactly one column (e.g., `"patient": {"columns": ["severity"], "hierarchy": ["severity"]}`). This works fine — `hierarchy` has one element, which is both root and leaf. The example includes this case.

**No orthogonal declarations:** The spec requires at least one `declare_orthogonal()` in the generated script (§2.5 hard constraint #4), so `orthogonal_groups` should never be empty. But if validation is applied to metadata *before* confirming hard constraints, an empty list is possible. The metadata schema doesn't enforce non-emptiness.

**No group dependencies:** Entirely valid. The `group_dependencies` list can be empty if all non-orthogonal groups simply use their marginal weights.

**No patterns beyond the minimum two:** The hard constraint requires ≥2 patterns, but the metadata schema itself places no minimum.

**Structural measure with no noise:** §2.1 shows `noise={}` as default. If a structural measure has no noise term, `noise_sigma` would be 0 or absent. M5's L2 residual std check (`abs(residuals.std() - col["noise_sigma"]) / col["noise_sigma"] < 0.2`) would divide by zero. The metadata doesn't carry `noise_sigma` in the example `columns` array at all — this is either sourced from elsewhere or is an omission.

**Measure with zero effects (constant parameters):** A stochastic measure with `param_model={"mu": 36.5, "sigma": 0.8}` (the simple form). The `columns` entry would have `family` and `measure_type` but no `depends_on`. The KS-test in L2 would run on the marginal distribution only (`group_filter` = None). This works but is not explicitly illustrated in the metadata example.

**Mixture distributions:** Listed as supported but no example of how mixture parameters map into `param_model` or how they appear in `columns` metadata (e.g., does `family: "mixture"` suffice, or do component families need to be listed?).

**Large hierarchies (3+ levels):** The example shows 2-level hierarchies (`hospital → department`). A 3-level hierarchy like `hospital → department → ward` should produce `"hierarchy": ["hospital", "department", "ward"]`. The metadata structure supports this, but neither validation behavior nor generation ordering for deep hierarchies is detailed in §2.6.

**Conflicting metadata fields:** What if `dimension_groups["entity"]["columns"]` lists a column that doesn't appear in `columns`? No reconciliation or validation of metadata internal consistency is specified — M4 is assumed to build it correctly from the declaration store.

---

## 3. PHASE B: INTRA-MODULE DATA FLOW

### 3.1 ASCII Data Flow Diagram

M4 contains only a single section (§2.6), so the intra-module diagram is degenerate — there are no internal section-to-section flows. The interesting structure is what flows *into* and *out of* the single node, and how the node transforms its inputs.

```
                    ┌─────────────────────────────────────────┐
                    │              MODULE M4                   │
                    │                                         │
  Declaration Store │    ┌──────────────────────────────┐     │
  (from M1)        │    │                              │     │
  ─────────────────┼───►│     §2.6: Schema Metadata    │     │
                   │    │          Builder              │     │
  Master DataFrame │    │                              │     │
  (from M2)        │    └──────────────┬───────────────┘     │
  ─ ─ ─ ─ ─ ─ ─ ─┼─ ─►               │                     │
  (possibly unused)│                   │                     │
                   │                   │ schema_metadata      │
                   │                   │ dict                 │
                   └───────────────────┼─────────────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  M5: Validation  │
                              │  Phase 3         │
                              └─────────────────┘
```

### 3.2 Input Decomposition

The declaration store is not a single blob — it is a collection of internal registries populated by M1. Mapping each registry to the metadata key it populates:

```
Declaration Store Registries          schema_metadata Keys
─────────────────────────────         ─────────────────────────────

Column Registry ──────────────────►   "columns"
  (name, type, group, parent,             (flattened, type-discriminated
   family, param_model, formula,           descriptors with cardinality,
   effects, noise, values, weights)        family, depends_on)

Dimension-Group Graph ────────────►   "dimension_groups"
  (group name → {columns,                 (verbatim structure)
   hierarchy order})

Orthogonal-Pair List ─────────────►   "orthogonal_groups"
  (group_a, group_b, rationale)           (direct 1:1 mapping)

Group-Dependency List ────────────►   "group_dependencies"
  (child_root, on,                        (child_root, on only —
   conditional_weights)                    weights DROPPED)

Pattern List ─────────────────────►   "patterns"
  (type, target, col, params)             (near-verbatim, selective
                                           param surfacing)

Constructor Argument ─────────────►   "total_rows"
  (target_rows)                           (scalar passthrough)

Measure DAG Edges ────────────────►   "measure_dag_order"
  (topological sort of measure             (flat ordered list)
   dependency graph)
```

### 3.3 Internal State

Because M4 has a single section, the "internal state" is simply the `schema_metadata` dict itself, assembled in one pass. There is no accumulation across sections. However, the *construction process* implicitly has intermediate state worth noting:

**Measure DAG resolution:** To produce `measure_dag_order`, M4 must perform (or re-use) a topological sort of the measure dependency edges. This requires traversing the column registry, identifying structural measures, extracting their `depends_on` edges, and sorting. The sorted order is an intermediate artifact that becomes the final list value.

**Cardinality computation:** For categorical columns, `cardinality` is the length of the `values` list. This is a trivial derivation from the column registry, but it is a transformation — the raw declaration carries the full value list, while the metadata carries only the count.

**Field projection / lossy compression:** The most important characteristic of M4's internal logic is that it is a **lossy projection**. The declaration store contains strictly more information than `schema_metadata`. Key information dropped:

- Categorical `values` and `weights` (only `cardinality` survives)
- Stochastic `param_model` details (only `family` survives)
- Structural `formula`, `effects`, `noise` (only `depends_on` survives)
- `conditional_weights` from group dependencies (only the edge survives)
- Pattern `params` are partially surfaced (e.g., `break_point` shown, but `z_score` and `magnitude` absent from the example)

This means **M5 cannot perform all its validation checks using `schema_metadata` alone** — it must also have access to the full declaration store or a richer metadata variant.

### 3.4 Ordering Constraints

**Explicit:** The stage1_module_map states M4 is sequential after M1 — all declarations must be finalized before metadata is built. M4 and M2 may execute in parallel since both read the same frozen declaration store.

**Implicit but unstated:**

1. **M4 does not depend on M2's output for its core function.** Every field in the §2.6 example can be derived from the declaration store alone. The stage1_module_map lists "Declaration store + generated DataFrame" as M4's primary input, and the stage2_overview says M4 receives "the raw material for schema metadata" from M2. But the example metadata contains no field that requires actual row data (no computed statistics, no observed distributions, no actual row count — `total_rows` is the *declared* target, not `len(df)`). This suggests M4 could run before or in parallel with M2, not after it.

2. **M4 must complete before M5 begins.** M5 requires `schema_metadata` as its expected-value contract. This is explicit in the module map but worth restating: M4 is on the critical path to validation.

3. **Metadata must be built exactly once per successful script execution.** There is no mechanism for M4 to re-run. In Loop B (M5 → M2 auto-fix retries), M2 regenerates the DataFrame but the declarations haven't changed, so `schema_metadata` should remain identical. This is implicit — the spec never states that metadata is invariant across Loop B retries, but it follows logically from the fact that auto-fix only mutates generation parameters, not declarations.

### 3.5 Cross-Check Against INTERFACE OUT (stage2_overview)

The stage2_overview states:

> **INTERFACE OUT:** `schema_metadata` dict with keys: `dimension_groups`, `orthogonal_groups`, `group_dependencies`, `columns` (typed descriptors with `measure_type`, `depends_on`, `family`, `cardinality`), `measure_dag_order`, `patterns`, `total_rows`. Consumed by M5 for validation and by Phase 3 for view extraction and QA generation.

**Cross-check results:**

| Overview Claim | §2.6 Example | Status |
|---|---|---|
| `dimension_groups` key exists | Yes | MATCH |
| `orthogonal_groups` key exists | Yes | MATCH |
| `group_dependencies` key exists | Yes | MATCH |
| `columns` with `measure_type` | Yes (`"stochastic"`, `"structural"`) | MATCH |
| `columns` with `depends_on` | Yes (structural measures only) | MATCH |
| `columns` with `family` | Yes (stochastic measures only) | MATCH |
| `columns` with `cardinality` | Yes (categorical columns only) | MATCH |
| `measure_dag_order` key exists | Yes | MATCH |
| `patterns` key exists | Yes | MATCH |
| `total_rows` key exists | Yes | MATCH |
| Consumed by M5 | Partial — see mismatches below | PARTIAL MATCH |
| Consumed by Phase 3 | Stated but not verifiable within Phase 2 spec | ASSUMED MATCH |

### 3.6 MISMATCHES

**MISMATCH 1 — M5 needs data not present in `schema_metadata`.**
M5's L1 validation checks marginal weights against declared weights (`col["values"]`, `col["weights"]`). M5's L2 validation checks stochastic measures against their full conditional distribution (`spec.iter_predictor_cells()` returning expected parameters per group filter) and structural measures against `col["noise_sigma"]` and `col["formula"]`. None of these fields appear in the `schema_metadata` `columns` array as shown in §2.6. Either:
- (a) `schema_metadata` is richer than the example shows and the example is illustrative, not exhaustive, or
- (b) M5 accesses the declaration store directly, making the stage1_module_map's claim that M5's input is "Master DataFrame + `schema_metadata`" incomplete.

**MISMATCH 2 — `conditional_weights` omitted from `group_dependencies`.**
M5's L2 checks conditional transition deviation against declared weights. The `group_dependencies` entries in §2.6 carry only `{child_root, on}` — no weights. Same resolution options as Mismatch 1.

**MISMATCH 3 — Pattern `params` inconsistently surfaced.**
The `patterns` list in §2.6 includes `break_point` for trend breaks but omits `z_score` for outlier patterns and `magnitude` for trend breaks. M5's L3 validation uses `z_score` thresholds and magnitude checks. Either the example is incomplete or M5 sources pattern params from elsewhere.

**OBSERVATION (not a mismatch) — M4 may not need the DataFrame.**
The stage1_module_map lists "Declaration store + generated DataFrame" as M4's input, but no metadata field in §2.6 requires row-level data. If this is intentional, M4 could be moved earlier in the pipeline (parallel with M2 rather than after it). If it's an oversight and some fields should reflect actual data properties (e.g., actual row count rather than target), the spec should clarify.
