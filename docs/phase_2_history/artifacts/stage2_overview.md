# Stage 2: Section-Level Index Overview

**Purpose:** Cross-module coherence anchor for per-module deep-dive sessions.
**Order:** Pipeline execution order (M3 → M1 → M2 ∥ M4 → M5).

---

### Module: LLM Orchestration (M3)
**Sections:** 2.5, 2.7

- **Section 2.5 — LLM Code Generation Prompt**
  - ROLE IN MODULE: Defines the complete system prompt template (SDK method whitelist, hard constraints, soft guidelines, one-shot example) that the LLM receives to produce a `build_fact_table()` script.
  - INTERFACE OUT: Executable Python string containing a `build_fact_table(seed) → (DataFrame, metadata)` function, passed to M1 for sandbox execution.

- **Section 2.7 — Execution-Error Feedback Loop**
  - ROLE IN MODULE: Defines the retry protocol — catch typed SDK exceptions, append code + traceback to LLM conversation, re-prompt up to `max_retries=3`.
  - INTERFACE OUT: On success, the same Python script artifact as §2.5 (now error-free). On terminal failure, a logged skip signal. Consumes `Exception` objects from M1.

---

### Module: SDK Surface (M1)
**Sections:** 2.1, 2.1.1, 2.1.2, 2.2, 2.3

- **Section 2.1 — The `FactTableSimulator` SDK (overview)**
  - ROLE IN MODULE: Introduces the SDK class and its dual purpose — schema definition and DGP specification in a single pass.
  - INTERFACE OUT: The `FactTableSimulator(target_rows, seed)` constructor; entry point that M3's generated script instantiates.

- **Section 2.1.1 — Column Declarations (Step 1)**
  - ROLE IN MODULE: Defines the four `add_*()` method signatures (`add_category`, `add_temporal`, `add_measure`, `add_measure_structural`) and their validation rules (auto-normalization, parent existence, DAG acyclicity, supported distribution families).
  - INTERFACE OUT: Populates the internal column registry — a list of typed column descriptors (name, type, group, parent, family, param_model, formula, effects, noise). Consumed by M2 for generation order and by M4 for the `columns` array in `schema_metadata`.

- **Section 2.1.2 — Relationship & Pattern Declarations (Step 2)**
  - ROLE IN MODULE: Defines `declare_orthogonal()`, `add_group_dependency()`, `inject_pattern()`, and `set_realism()` — the inter-column and inter-group relationship API.
  - INTERFACE OUT: Populates three internal registries: orthogonal-pair list, group-dependency list (with `conditional_weights`), and pattern list (type, target, col, params). All three propagate into `schema_metadata` fields consumed by M4 and M5.

- **Section 2.2 — Dimension Groups and Cross-Group Relations**
  - ROLE IN MODULE: Specifies the dimension-group abstraction — within-group hierarchy via `parent`, cross-group orthogonality propagation, root-only DAG constraint for cross-group dependencies, temporal as a special group.
  - INTERFACE OUT: The `dimension_groups` dict structure (group name → `{columns, hierarchy}`) that M4 emits verbatim into `schema_metadata["dimension_groups"]`.

- **Section 2.3 — Closed-Form Measure Declaration**
  - ROLE IN MODULE: Formalizes the two measure types (stochastic: intercept + effects → distribution sample; structural: formula + effects + noise → deterministic computation) and the measure DAG constraint.
  - INTERFACE OUT: The measure DAG edge set and topological order (`measure_dag_order`), consumed by M2 for generation sequencing and by M4 for `schema_metadata["measure_dag_order"]`.

---

### Module: Generation Engine (M2)
**Sections:** 2.4, 2.8

- **Section 2.4 — DAG-Ordered Event-Level Row Generation**
  - ROLE IN MODULE: Specifies the conceptual generation algorithm — full DAG across all column types, topological layering (independent roots → dependent non-measures → stochastic measures → structural measures → pattern injection → realism), and the `target_rows` contract inherited from Phase 1.
  - INTERFACE OUT: Internal only. Defines the algorithm that §2.8 implements; no artifact crosses the module boundary from this section alone.

- **Section 2.8 — Deterministic Engine Execution**
  - ROLE IN MODULE: Implements `FactTableSimulator.generate()` — the four-stage deterministic pipeline (α: skeleton, β: measures, γ: patterns, δ: realism) that materializes the Master DataFrame from declarations + seed.
  - INTERFACE OUT: `Tuple[pd.DataFrame, dict]` — the Master DataFrame (one row per atomic event, all columns populated) and the raw material for schema metadata. DataFrame goes to M5; metadata dict goes to M4.

---

### Module: Schema Metadata (M4)
**Sections:** 2.6

- **Section 2.6 — Schema Metadata Output**
  - ROLE IN MODULE: Defines the exact structure of the `schema_metadata` dict — the contract between Phase 2 and Phase 3.
  - INTERFACE OUT: `schema_metadata` dict with keys: `dimension_groups`, `orthogonal_groups`, `group_dependencies`, `columns` (typed descriptors with `measure_type`, `depends_on`, `family`, `cardinality`), `measure_dag_order`, `patterns`, `total_rows`. Consumed by M5 for validation and by Phase 3 for view extraction and QA generation.

---

### Module: Validation Engine (M5)
**Sections:** 2.9

- **Section 2.9 — Three-Layer Validation**
  - ROLE IN MODULE: Implements `SchemaAwareValidator` with three check layers and the auto-fix retry loop.
    - **L1 (Structural):** Row count, categorical cardinality, root marginal weights, measure finiteness, orthogonal independence (χ²), DAG acyclicity.
    - **L2 (Statistical):** Stochastic measures → KS-test per predictor cell; structural measures → residual mean/std check; group dependencies → conditional transition deviation.
    - **L3 (Pattern):** Per-pattern type verification (outlier z-score, ranking correlation sign, trend break magnitude, dominance shift).
    - **Auto-fix loop:** `AUTO_FIX` dispatch table (`widen_variance`, `amplify_magnitude`, `reshuffle_pair`) + `generate_with_validation()` wrapper, `max_retries=3`.
  - INTERFACE OUT: Final validated `(DataFrame, schema_metadata, ValidationReport)` triple — the terminal output of Phase 2, handed to Phase 3.
