# Atomic-Grain Programmatic Data Synthesis for Chart Understanding Benchmarks

> **Abstract:** This proposal elevates chart QA benchmark construction from loose prompt engineering to a rigorous **Formal Framework** unifying three interlocking contributions: (1) a **Type-Safe SDK** (Code-as-DGP) that replaces fragile LLM-generated JSON with executable Python programs for atomic-grain fact table synthesis; (2) **Table Amortization** — deterministic SQL projection from a single Master Table to 10–30+ logically coherent multi-chart tasks with guaranteed cross-chart arithmetic consistency; and (3) a **Complete Operator Algebra** formalizing all chart QA as compositions of Set and Scalar operators, enabling systematic, multi-hop, cross-chart question generation.

The framework is divided into four parts:

1. **Operator Algebra** — Formal definitions for single-chart query operators and their composition.
2. **Agentic Data Simulator** — SDK-driven atomic-grain data synthesis with dimension groups, orthogonality, and pattern injection.
3. **Table Amortization & View Extraction** — One Master Table → many chart views via deterministic SQL projection and multi-chart dashboard composition.
4. **Rule-Based QA Generation** — Systematic intra-view, inter-view, and pattern-triggered question generation with difficulty tiering.

---

## Part 1: The Operator Algebra (Formalizing Chart QA Logic)

In database concepts, all chart QA operations map to transformations on **Sets** or **Scalars**. To construct complex questions, we define a set of **Complete** and **Orthogonal** operators.

Let a query *Q* act on a Table *T* to produce a Result *R*.

### 1.1 Set Operators (One-Order): *T → T'*

These operators transform the shape of the data (rows/columns) but preserve its dimensional nature.

| Operator | Symbol | SQL Concept | DSL Operation |
|---|---|---|---|
| **Projection** | π | `SELECT col1, col2` | `Project(columns=[c1, c2])` |
| **Selection** | σ | `WHERE value > threshold` | `Filter(condition)` |
| **Grouping** | γ | `GROUP BY category` | `GroupBy(dim)` |
| **Sorting** | τ | `ORDER BY val ASC/DESC` | `Sort(col, direction)` |
| **Slicing** | λ | `LIMIT k` | `Limit(k)` |

### 1.2 Scalar Operators (Zero-Order): *T → s*

These operators collapse a column of data into a single value, typically used for **Answer** generation.

**Aggregation (Σ)** — Statistical features:

- *Basic:* `Sum`, `Avg`, `Count`
- *Distribution:* `Max`, `Min`, `Median`, `StdDev` (Volatility), `Skew` (Distribution shape)

**Positioning (Ψ)** — Value retrieval based on index/location:

- `ValueAt(index)` — e.g., first, last, *k*-th
- `ArgMax` / `ArgMin` — Returns the Index/Category associated with the max/min value (equivalent to a Subquery)

**Arithmetic (Δ)** — Mathematical operations:

- `Add`, `Sub`, `Mult`, `Div`, `Ratio` (Percentage share)

### 1.3 Composition Logic: The Syntax Tree

Three core structures define how operators are combined:

#### A. Sequential Composition (Pipeline / Nested Logic)

- **Logic:** *Op₂(Op₁(T))*
- **DB Mapping:** Subquery
- **Example:** *"What is the exact sales value of the top-performing product?"*
- **Formula:** `ValueAt(Limit(Sort(T)), col='Sales')`
- **Human Path:** Find table → Sort by Sales → Take Top 1 → Read Sales Value

#### B. Parallel Composition (Binary Logic)

- **Logic:** *Op(R₁, R₂) where R₁ = f(T), R₂ = g(T)*
- **DB Mapping:** Join / Self-Join / CTE Calculation
- **Example:** *"How much more did Product A sell compared to Product B?"*
- **Formula:** `Sub( ValueAt(Filter(T, 'A')), ValueAt(Filter(T, 'B')) )`

#### C. Conditional Composition (Predicate Logic)

- **Logic:** *If P(T) then ... else ...*
- **DB Mapping:** `HAVING` / `CASE WHEN`
- **Example:** *"Did any month exceed 1 million in sales?"*
- **Formula:** `Exists(Filter(T, Sales > 1M))`

> **Connection to QA Generation (Part 4):** Every question generated in Phase 3 is a composition of these operators. Easy questions use a single operator; Hard/Very Hard questions chain 3–5 operators via Sequential or Parallel composition. This algebra provides the formal backbone for systematic difficulty tiering.

---

## Part 2: Agentic Data Simulator (SDK-Driven Atomic-Grain Synthesis)

> **Paradigm shift:** From **LLM-as-Data-Generator** to **LLM-as-Data-Programmer**. The LLM writes executable Python scripts calling a type-safe SDK — not fragile JSON configs or raw numbers. Schema definition and Data Generation Program (DGP) are unified in a single code pass.

### 2.1 The 4-Phase Pipeline

The framework operates through four phases:

```
 Phase 0: Domain Pool Construction (one-time, cached)
     → 200+ fine-grained domains across 15+ topics
 Phase 1: Scenario Contextualization
     → Domain → realistic entities, metrics, temporal grain
 Phase 2: Agentic Data Simulator (SDK-Driven)
     → LLM writes Python SDK script → Master Fact Table + Schema Metadata
 Phase 3: View Amortization & QA Instantiation (fully deterministic)
     → SQL projection → chart views → multi-tier QA with reasoning chains
```

> **LLM usage:** Called only in Phases 0–2. Phase 3 is entirely deterministic — no LLM calls, no randomness beyond the fixed seed.

### 2.2 The `FactTableSimulator` SDK

The SDK encapsulates all statistical machinery behind a minimal, strongly-typed API. The LLM assembles building blocks within a whitelist of safe operations:

**Step 1 — Declare columns:**

| API Method | Function |
|------------|----------|
| `add_category(name, values, weights, group, parent)` | Categorical column. `group` assigns a dimension group; `parent` creates hierarchy. |
| `add_measure(name, dist, params)` | Numerical column with a named distribution. |
| `add_temporal(name, start, end, freq)` | Temporal dimension column. |

**Step 2 — Declare relationships and patterns:**

| API Method | Function |
|------------|----------|
| `add_conditional(measure, on, mapping)` | Measure distribution varies by category: $P(\text{measure} \mid \text{category})$. |
| `add_dependency(target, formula, noise_sigma)` | Functional dependency: `target = f(cols) + noise`. |
| `add_correlation(col_a, col_b, target_r)` | Inject Pearson correlation via Gaussian Copula. |
| `declare_orthogonal(group_a, group_b, rationale)` | Declare two dimension groups as statistically independent. |
| `inject_pattern(type, target, col, params)` | Plant a narrative-driven statistical anomaly. |
| `set_realism(missing_rate, dirty_rate, censoring)` | Simulate data imperfections. |

**Supported distributions:** `gaussian`, `lognormal`, `gamma`, `beta`, `uniform`, `poisson`, `exponential`, `mixture`

**Pattern types:** `outlier_entity`, `trend_break`, `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`

### 2.3 Dimension Groups, Hierarchy & Orthogonality

**Dimension groups** are the central structural abstraction. Each categorical column belongs to exactly one named group. Columns within a group form a hierarchy via `parent`; columns across groups can be declared independent via `declare_orthogonal()`.

```
Group "entity":   hospital ← department ← ward
Group "patient":  severity ← acuity_level
Group "payment":  payment_method
```

**Cross-group orthogonality:** Independence is declared between *entire groups*, not individual columns. If Group A ⊥ Group B, then **all cross-group column pairs are automatically independent**.

```python
sim.declare_orthogonal("entity", "patient",
    rationale="Severity distribution is independent of hospital")
# Automatically implies: hospital ⊥ severity, department ⊥ severity, etc.
```

**What orthogonality enables:**

1. **Generation:** Ensures $P(A,B) \approx P(A) \cdot P(B)$ via independent sampling.
2. **Validation:** Chi-squared test on root-level cross-group pairs.
3. **Multi-chart dashboards (Part 3):** "Orthogonal Contrast" — slicing the same metric by two independent dimensions.

### 2.4 Execution-Error Feedback Loop

Unlike JSON-config validation that catches only *syntactic* errors, code execution catches *semantic* impossibilities:

```
1. LLM outputs Python SDK script.
2. Sandbox executes build_fact_table().
3. SUCCESS → deterministic engine + three-layer validation.
4. FAILURE → SDK raises typed exception with targeted repair advice.
5. Code + traceback fed back to LLM for self-correction (max 3 retries).
```

### 2.5 Three-Layer Validation (No LLM Re-Call)

After engine execution, a deterministic validator checks correctness at three levels:

| Layer | What It Checks | Example |
|-------|---------------|---------|
| **L1: Structural** | Row count, cardinality, finiteness, orthogonal independence (χ²) | `χ² p > 0.05` for declared orthogonal pairs |
| **L2: Statistical** | Correlation targets (±0.15), dependency residuals, KS distribution tests | `target_r = −0.55, actual_r = −0.52` ✓ |
| **L3: Pattern** | Outlier z-scores, ranking reversals, trend break magnitudes | Outlier z ≥ 2.0 ✓ |

Auto-fix adjusts parameters (relaxing correlation, widening variance, amplifying patterns) and re-runs. Typically converges in 1–2 retries at near-zero cost.

---

## Part 3: Table Amortization & View Extraction

> **Core value:** 1 LLM call → 1 Python script → 1 Master Table → **10–30+ logically coherent tasks**. All derived charts share the same ground-truth arithmetic by construction.

### 3.1 View Extraction via SQL Operators

Every chart view is a deterministic projection from the Master Table using the Operator Algebra (Part 1):

$$\text{View}_{\text{chart}} = \sigma_{\text{filter}} \circ \gamma_{\text{agg}} \circ \pi_{\text{cols}}(M)$$

The `ViewEnumerator` uses Schema Metadata (column roles, dimension groups, orthogonal pairs) to enumerate all feasible `(chart_type, column_binding)` pairs across **6 families, 16 chart types**. Each feasible view is **scored** by suitability using a Chart Selection Guide encoding practitioner knowledge.

### 3.2 Chart Type Coverage

| Family | Chart Types | Key Data Requirement |
|--------|-------------|---------------------|
| **Comparison** | bar, grouped bar | Categorical × Measure aggregation |
| **Trend** | line, area | Temporal × Measure series |
| **Distribution** | histogram, box, violin | Raw measure rows (≥ 100) |
| **Composition** | pie, donut, stacked bar, treemap | Part-of-whole proportions |
| **Relationship** | scatter, bubble, heatmap, radar | Multi-measure correlation |
| **Flow** | waterfall, funnel | Ordered stages with sequential values |

### 3.3 Multi-Chart Dashboard Composition

Single-chart understanding is a solved problem for frontier VLMs. The real evaluation frontier is **cross-chart reasoning**. The `DashboardComposer` constructs k=2,3,4 chart dashboards using 7 inter-chart relationship types:

| Relationship | Definition | DGP Requirement |
|-------------|------------|-----------------|
| **Drill-down** | Same metric, different aggregation granularity | None |
| **Orthogonal Slice** | Same metric, independent dimension groups | None (uses `declare_orthogonal`) |
| **Comparative** | Same schema, different temporal/entity slices | None |
| **Dual-Metric** | Same entities, different measures | None |
| **Part-Whole** | Composition chart + totals chart | None |
| **Associative** | Correlated measures visible across charts | Requires `add_correlation()` |
| **Causal Chain** | Directional dependency across 3+ variables | Requires `add_dependency()` |

> **Key insight:** 5 of 7 relationship types require **zero** special DGP treatment — they emerge naturally from a well-designed schema with orthogonal dimensions and multiple measures.

---

## Part 4: Rule-Based QA Generation

### 4.1 Intra-View QA (Single Chart)

Systematic template-based generation covering 8 question types:

| QA Type | Applicable Charts | Difficulty |
|---------|-------------------|------------|
| Value Retrieval | All | Easy |
| Extremum | Bar, Line, Scatter | Easy |
| Comparison | Bar, Grouped Bar, Line | Medium |
| Trend | Line, Area | Medium |
| Distribution | Histogram, Box, Violin | Medium |
| Proportion | Pie, Donut, Stacked Bar, Treemap | Medium |
| Correlation | Scatter, Bubble, Heatmap | Hard |
| Anomaly Detection | All (if pattern present) | Hard |

### 4.2 Inter-View QA (Cross-Chart)

The unique strength of Table Amortization — only possible because all charts derive from the same Master Table:

| QA Type | Required Relationship | Difficulty |
|---------|----------------------|------------|
| Ranking Consistency | Dual-Metric, Associative | Hard |
| Conditional Lookup | Any k ≥ 2 | Hard |
| Trend Divergence | Comparative, Dual-Metric | Hard |
| Drill-down Verification | Drill-down | Hard |
| Orthogonal Reasoning | Orthogonal Slice | Very Hard |
| Causal Inference | Causal Chain (k=3) | Very Hard |
| Holistic Synthesis | Full Dashboard (k=4) | Very Hard |

### 4.3 Pattern-Triggered QA

The `PatternDetector` scans each view for statistical patterns injected during Phase 2 (`outlier_entity`, `trend_break`, `ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`). Detected patterns trigger specialized hard questions testing genuine visual reasoning — not template fill-in.

### 4.4 Difficulty Distribution

| Difficulty | Proportion | Reasoning Steps |
|------------|-----------|-----------------|
| Easy | 25% | 1 (single-step lookup) |
| Medium | 35% | 2 (aggregation/comparison within one chart) |
| Hard | 25% | 3–4 (multi-step, cross-chart, or pattern detection) |
| Very Hard | 15% | 5+ (multi-chart synthesis, causal reasoning) |

---

## Summary

| Layer | Core Idea | Key Mechanism |
|---|---|---|
| **Operator Algebra** | Replaces simple text generation with formal logic | `Projection`, `Selection`, `Aggregation`, `Composition` |
| **Agentic Data Simulator** | LLM writes executable SDK scripts, not JSON; code-level error correction | Type-safe SDK, Dimension Groups, Orthogonal Declarations, Pattern Injection |
| **Table Amortization** | One Master Table serves 10–30+ tasks with guaranteed arithmetic consistency | Deterministic SQL projection, 16 chart types × 7 inter-chart relationships |
| **Rule-Based QA** | Systematic QA from template + pattern detection, no LLM in the loop | Intra-view, Inter-view, Pattern-triggered, 4-tier difficulty |

### Comparison with Prior Work

| Dimension | ChartQA | PlotQA | ChartBench | **Ours** |
|-----------|---------|--------|------------|----------|
| Data source | Web-crawled | Templates | Hybrid | **LLM-authored simulator programs** |
| Data depth | Surface aggregates | Aggregates | Aggregates | **Atomic-grain fact tables** |
| Distribution control | None | Uniform/Normal | Semi-fixed | **SDK-controlled: mixtures, copulas, conditional** |
| Cross-chart consistency | None | None | None | **Guaranteed (shared Master Table)** |
| Error correction | Manual | None | Heuristic | **Code Execution Feedback Loop** |
| Multi-chart reasoning | None | None | Limited | **Dashboard-level cross-chart QA** |
| Reproducibility | ✗ | ✓ | Partial | **✓ (SDK + seed)** |