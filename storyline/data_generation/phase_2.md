## PHASE 2: Agentic Data Simulator (SDK-Driven)

> **Core Contribution:** Replace fragile JSON-based DGP specifications with **Code-as-DGP** — the LLM writes executable Python scripts calling a type-safe SDK. Each measure is declared as a **closed-form data-generating program** in a single call — not incrementally patched. All inter-column dependencies form an explicit DAG. A DAG-ordered engine executes event-level row generation, and a three-layer validator ensures structural, statistical, and pattern-level correctness — all without additional LLM calls.

---

### 2.1 The `FactTableSimulator` SDK

The SDK encapsulates all statistical machinery behind a minimal, strongly-typed API. The LLM assembles building blocks within a whitelist of safe operations, simultaneously accomplishing:

1. **Schema Definition** — each `add_*()` call declares a column and its complete generation rule.
2. **Data Generation Program (DGP)** — distributions, dependencies, and patterns specified as code.

#### 2.1.1 Column Declarations (Step 1)

**`add_category(name, values, weights, group, parent=None)`** — Categorical column belonging to a named dimension group.

```python
# Root category
sim.add_category("hospital",
    values=["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],
    weights=[0.25, 0.20, 0.20, 0.20, 0.15],
    group="entity")

# Child category: same weights for all parents (default, simplest)
sim.add_category("department",
    values=["Internal", "Surgery", "Pediatrics", "Emergency"],
    weights=[0.35, 0.25, 0.15, 0.25],
    group="entity", parent="hospital")
```

When a flat list is used with `parent`, the same weights apply for every parent value. For finer control, pass a per-parent dict — the engine then samples $P(\text{department} \mid \text{hospital})$ using parent-specific vectors:

```python
# Optional: per-parent conditional weights for realism
weights={"Xiehe": [0.30, 0.25, 0.15, 0.30], "Huashan": [0.35, 0.20, 0.20, 0.25], ...}
```

Auto-normalized; rejects empty values; validates parent exists in same group.

**`add_temporal(name, start, end, freq, derive=[])`** — Temporal column with optional derived calendar features.

```python
sim.add_temporal("visit_date",
    start="2024-01-01", end="2024-06-30", freq="daily",
    derive=["day_of_week", "month"])
```

Derived columns (`day_of_week`, `month`, `quarter`, `is_weekend`) are automatically extracted and available as predictors for measures.

**`add_measure(name, family, param_model, scale=None)`** — **Stochastic root measure.** Sampled from a named distribution. Parameters may vary by categorical context, but the measure does **not** depend on any other measure — it is a root node in the measure DAG.

```python
# Simple: constant parameters
sim.add_measure("temperature", family="gaussian",
    param_model={"mu": 36.5, "sigma": 0.8})

# Full: parameters vary by categorical predictors
sim.add_measure("wait_minutes", family="lognormal",
    param_model={
        "mu": {"intercept": 2.8, "effects": {
            "severity": {"Mild": 0.0, "Moderate": 0.4, "Severe": 0.9},
            "hospital": {"Xiehe": 0.2, "Huashan": -0.1, "Ruijin": 0.0,
                         "Tongren": 0.1, "Zhongshan": -0.1}
        }},
        "sigma": {"intercept": 0.35, "effects": {
            "severity": {"Mild": 0.0, "Moderate": 0.05, "Severe": 0.10}
        }}
    })
```

**`add_measure_structural(name, formula, effects={}, noise={})`** — **Structural (derived) measure.** Computed from other measures and categorical effects via formula. Creates directed edges in the measure DAG.

```python
sim.add_measure_structural("cost",
    formula="wait_minutes * 12 + severity_surcharge",
    effects={"severity_surcharge": {"Mild": 50, "Moderate": 200, "Severe": 500}},
    noise={"family": "gaussian", "sigma": 30})
```

The formula references previously declared measure columns by name and named effects. Every symbol must have an explicit numeric definition — no undefined terms.

**The one key difference between the two measure types:**

| | `add_measure` (Stochastic) | `add_measure_structural` (Structural) |
|---|---|---|
| **How generated** | **Randomly sampled** from a distribution | **Deterministically computed** from a formula + noise |
| **Can reference other measures?** | **No** — this is a root node | **Yes** — creates DAG edges |
| **DAG role** | Root (no incoming measure edges) | Non-root (depends on upstream measures) |
| **Example** | `wait_minutes ~ LogNormal(μ, σ)` | `cost = 12 × wait_minutes + surcharge + ε` |

Both can be influenced by categorical context. The distinction is simple: **if the value depends on another measure, it's structural; otherwise, it's stochastic.**

**Supported distributions:** `"gaussian"`, `"lognormal"`, `"gamma"`, `"beta"`, `"uniform"`, `"poisson"`, `"exponential"`, `"mixture"`

#### 2.1.2 Relationship & Pattern Declarations (Step 2)

**`declare_orthogonal(group_a, group_b, rationale)`** — Declare two dimension groups as statistically independent. Propagates to all cross-group column pairs.

```python
sim.declare_orthogonal("entity", "patient",
    rationale="Severity distribution is independent of hospital/department")
# Automatically implies: hospital ⊥ severity, department ⊥ severity, etc.
```

**`add_group_dependency(child_root, on, conditional_weights)`** — Declare that a group **root** column's distribution is conditional on **root** columns from other groups. Cross-group dependencies are **only allowed between group root columns**, and the root-level dependency graph must be a DAG.

```python
sim.add_group_dependency("payment_method", on=["severity"],
    conditional_weights={
        "Mild":     {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},
        "Moderate": {"Insurance": 0.65, "Self-pay": 0.25, "Government": 0.10},
        "Severe":   {"Insurance": 0.80, "Self-pay": 0.10, "Government": 0.10}
    })
```

> **Root-only constraint:** Cross-group dependencies are restricted to root columns (no parent). This keeps the dependency model simple while covering realistic scenarios (e.g., severe patients prefer insurance). The root-level graph must be acyclic.

**`inject_pattern(type, target, col, params)`** — Plant a narrative-driven statistical anomaly.

```python
sim.inject_pattern("outlier_entity",
    target="hospital == 'Xiehe' & severity == 'Severe'",
    col="wait_minutes", params={"z_score": 3.0})
```

**Pattern types:** `"outlier_entity"`, `"trend_break"`, `"ranking_reversal"`, `"dominance_shift"`, `"convergence"`, `"seasonal_anomaly"`

**`set_realism(missing_rate, dirty_rate, censoring)`** — **Optional.** Simulate data imperfections.

---

### 2.2 Dimension Groups and Cross-Group Relations

**Dimension groups** are the central structural abstraction. Each categorical column belongs to exactly one named group. Columns within a group form a hierarchy via `parent`; columns across groups are related via `declare_orthogonal()` (independent) or `add_group_dependency()` (dependent).

```
Group "entity":   hospital ← department ← ward
Group "patient":  severity ← acuity_level
Group "payment":  payment_method
Group "time":     visit_date → [day_of_week, month]  (derived)
```

**Within-group hierarchy:** Each group has a **root** column (no parent). Child columns are sampled conditionally on their parent: $P(\text{department} \mid \text{hospital})$ uses per-parent weight vectors.

**Temporal as dimension group:** Temporal columns are a special dimension group. The root is the declared temporal column; derived calendar levels are automatically extracted via `derive` and available as predictors.

**Cross-group orthogonality:** Independence is declared between *entire groups*, not individual columns. If Group A ⊥ Group B, then all cross-group pairs are automatically independent — no need to enumerate.

**Cross-group dependency:** Cross-group independence is **opt-in, not default**. When two groups are not declared orthogonal, their root-level relationship can be specified via `add_group_dependency()`. The root-level dependency graph must be a DAG.

**What `declare_orthogonal()` enables:**

1. **Generation:** $P(A,B) \approx P(A) \cdot P(B)$ via independent sampling.
2. **Validation (L1):** Chi-squared test on root-level cross-group pairs.
3. **View Extraction (Phase 3):** "Orthogonal Contrast" dashboards — slicing the same metric by two independent dimensions.

> **Design principle:** Dimension groups unify categorical, temporal, and cross-group semantics into a single abstraction. Orthogonality propagation eliminates $O(n^2)$ pairwise declarations. Root-level DAG constraint prevents logical contradictions while keeping the dependency model simple.

---

### 2.3 Closed-Form Measure Declaration

Every measure is declared exactly once as a complete data-generating program.

#### Stochastic Root Measure

Randomly sampled from a distribution whose parameters depend on categorical context. Concrete example:

$$\text{wait\_minutes} \mid \text{severity}, \text{hospital} \;\sim\; \text{LogNormal}(\mu,\; \sigma)$$

where each parameter is **intercept + sum of effects**:

$$\mu = \underbrace{2.8}_{\text{intercept}} + \underbrace{0.9}_{\text{severity=Severe}} + \underbrace{0.2}_{\text{hospital=Xiehe}} = 3.9, \quad \sigma = 0.35 + 0.10 = 0.45$$

In general: $Y \mid X_1, \ldots, X_k \sim \mathcal{D}(\theta_1, \theta_2, \ldots)$ where $\theta_j = \beta_0 + \sum_m \beta_m(X_m)$.

#### Structural (Derived) Measure

Deterministically computed from other measures + categorical effects + noise. Concrete example:

$$\text{cost} = \underbrace{12 \times \text{wait\_minutes}}_{\text{formula on measures}} + \underbrace{\text{surcharge}(\text{severity})}_{\text{categorical effect}} + \underbrace{\epsilon}_{\text{noise} \sim \mathcal{N}(0, 30^2)}$$

#### How Inter-Measure Relationships Work

Inter-measure relationships are expressed through two mechanisms — no separate correlation API is needed:

1. **Structural dependency:** A structural measure directly references another measure in its formula (e.g., `cost = f(wait_minutes)`), creating a directed edge in the measure DAG. This naturally produces correlation.
2. **Shared predictors:** Two stochastic measures that depend on the same categorical predictors (e.g., both vary by `severity`) are marginally correlated through their shared conditioning, even though they are conditionally independent given the predictors.

#### Measure DAG Constraint

All measure dependencies must form a **directed acyclic graph (DAG)**. Structural measures may only reference measures declared before them. The engine resolves generation order via topological sort.

> **Why closed-form?** In previous designs, a measure's final DGP resulted from chaining `add_measure()` → `add_conditional()` → `add_dependency()` → `add_correlation()`. The declared distribution and the actual generated distribution could diverge after successive overrides. Closed-form declaration ensures each measure's statistical semantics are self-contained, verifiable, and aligned with validation.

---

### 2.4 DAG-Ordered Event-Level Row Generation

> This section describes the **core generation mechanism** — how each row of the Master Table is produced.

**`target_rows`** is inherited from Phase 1's scenario context, which determines it based on the domain's complexity tier, temporal span, and entity count (see §1.2):

| Complexity Tier | Typical `target_rows` | Rationale |
|----------------|----------------------|-----------|
| Simple | 200–500 | Few entities, 1–2 metrics, short time span |
| Medium | 500–1000 | Multiple entity types, 2–3 metrics |
| Complex | 1000–3000 | Nested hierarchies, 3+ interdependent metrics |

The engine does **not** materialize a full categorical cross-product. Each row is generated as an **independent atomic event**.

#### The Full Generation DAG

All columns — categorical, temporal, and measure — form a single DAG. The engine generates columns in topological order:

```
Topological Generation Order:

Layer 0 — Independent roots:
  hospital, severity, visit_date

Layer 1 — Dependent non-measure columns:
  payment_method       ← P(payment | severity)          [cross-group root dep]
  department           ← P(dept | hospital)              [within-group hierarchy]
  day_of_week, month   ← derived from visit_date         [temporal derivation]

Layer 2 — Stochastic root measures:
  wait_minutes         ← severity, hospital
                         ~ LogNormal(μ(severity, hospital), σ(severity))

Layer 3 — Structural measures:
  cost                 ← wait_minutes, severity
                         = wait_minutes × 12 + surcharge(severity) + ε
  satisfaction         ← wait_minutes, severity
                         = 9 − 0.04 × wait_minutes + adj(severity) + ε
```

#### Row Generation Algorithm

For each of the `target_rows` rows:

```
Step 1: Generate all non-measure columns (topological order)
  1. hospital_i       ~ Cat([0.25, 0.20, ...])                 // independent root
  2. severity_i       ~ Cat([0.50, 0.35, 0.15])                // independent root
  3. visit_date_i     ~ Uniform(2024-01-01, 2024-06-30)        // independent root
  4. payment_method_i ~ Cat(weights[severity_i])                // root dep ← severity
  5. department_i     ~ Cat(weights | hospital_i)                // child ← hospital
  6. day_of_week_i    = DOW(visit_date_i)                       // temporal derived
  7. month_i          = MONTH(visit_date_i)                     // temporal derived

Step 2: Generate measures (topological order of measure DAG)
  8. wait_minutes_i   ~ LogNormal(μ(severity_i, hospital_i),
                                   σ(severity_i))              // stochastic root
  9. cost_i           = wait_minutes_i × 12
                        + surcharge(severity_i) + ε₁           // structural
 10. satisfaction_i   = 9 − 0.04 × wait_minutes_i
                        + adj(severity_i) + ε₂                 // structural

Step 3: Post-generation adjustments (applied to full DataFrame)
 11. Pattern injection (outliers, trend breaks, etc.)
 12. Realism injection (optional)
```

> **Why event-level?** Generating rows as atomic events (rather than materializing a cross-product cube and repeating) produces realistic cell-occupancy distributions and is consistent with the hard constraint that each row represents one indivisible event.

---

### 2.5 LLM Code Generation Prompt

````text
SYSTEM:
You are an expert Data Scientist Agent. Build an Atomic-Grain Fact Table
using the `FactTableSimulator` Python SDK.

INPUT:
1. Scenario Context: real-world setting with entities, metrics, temporal grain,
   and target_rows (from Phase 1).
2. SDK Reference: you may ONLY use the methods listed below.

AVAILABLE SDK METHODS (declare columns FIRST, then relationships):
  # --- Step 1: Column declarations ---
  sim.add_category(name, values, weights, group, parent=None)
      # weights: list (root/global) or dict-of-lists (per-parent conditional)
  sim.add_temporal(name, start, end, freq, derive=[])
  sim.add_measure(name, family, param_model, scale=None)
      # Stochastic ROOT measure: param_model uses {intercept, effects}
      # Does NOT depend on any other measure
  sim.add_measure_structural(name, formula, effects={}, noise={})
      # Structural DERIVED measure: formula references other measures
      # Creates edges in the measure DAG

  # --- Step 2: Relationships & patterns ---
  sim.declare_orthogonal(group_a, group_b, rationale)
  sim.add_group_dependency(child_root, on, conditional_weights)
      # Cross-group dependency between ROOT columns only; must be DAG
  sim.inject_pattern(type, target, col, params)
  sim.set_realism(missing_rate, dirty_rate, censoring=None)    # optional

SUPPORTED DISTRIBUTIONS: "gaussian", "lognormal", "gamma", "beta", "uniform",
                         "poisson", "exponential", "mixture"

PATTERN_TYPES: "outlier_entity", "trend_break", "ranking_reversal",
               "dominance_shift", "convergence", "seasonal_anomaly"

HARD CONSTRAINTS — the script MUST satisfy ALL:
1. ATOMIC_GRAIN: each row = one indivisible event.
2. At least 2 dimension groups, each with ≥1 categorical column, plus ≥2 measures.
3. All column declarations (Step 1) BEFORE any relationship declarations (Step 2).
4. At least 1 declare_orthogonal() between genuinely independent groups.
5. At least 1 add_measure_structural() creating inter-measure dependency,
   and at least 2 inject_pattern() calls.
6. Output must be pure, valid Python returning sim.generate().
7. All measure dependencies must be acyclic (DAG). No circular or
   self-referential dependency is allowed.
8. Cross-group dependencies only between group ROOT columns; root DAG must be acyclic.
9. Every symbolic effect in param_model or formula must have an explicit
   numeric definition. No undefined symbols.

SOFT GUIDELINES — include when naturally fitting the domain:
- Temporal dimension with derive (if data has a time component).
- Within-group hierarchy via parent with per-parent conditional weights.
- 3+ measures (enables richer chart coverage).
- add_group_dependency() when groups are not genuinely independent.
- set_realism() for data imperfections (missing values, dirty entries).

=== ONE-SHOT EXAMPLE ===
[SCENARIO]
Title: 2024 Shanghai Emergency Records
target_rows: 500
Entities: [Xiehe, Huashan, Ruijin, Tongren, Zhongshan]
Metrics: wait_minutes (min), cost (CNY), satisfaction (1-10)
Temporal: daily, 2024-01 to 2024-06

[AGENT CODE]
```python
from chartagent.synth import FactTableSimulator

def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=500, seed=seed)

    # ========== Step 1: Declare all columns ==========

    # Dimension group "entity": hospital → department
    sim.add_category("hospital",
        values=["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],
        weights=[0.25, 0.20, 0.20, 0.20, 0.15],
        group="entity")

    sim.add_category("department",
        values=["Internal", "Surgery", "Pediatrics", "Emergency"],
        weights=[0.35, 0.25, 0.15, 0.25],
        group="entity", parent="hospital")

    # Dimension group "patient": severity
    sim.add_category("severity",
        values=["Mild", "Moderate", "Severe"],
        weights=[0.50, 0.35, 0.15],
        group="patient")

    # Dimension group "payment": payment_method
    sim.add_category("payment_method",
        values=["Insurance", "Self-pay", "Government"],
        weights=[0.60, 0.30, 0.10],
        group="payment")

    # Temporal dimension with derived calendar levels
    sim.add_temporal("visit_date",
        start="2024-01-01", end="2024-06-30", freq="daily",
        derive=["day_of_week", "month"])

    # Stochastic root measure: wait_minutes varies by severity and hospital
    sim.add_measure("wait_minutes",
        family="lognormal",
        param_model={
            "mu": {
                "intercept": 2.8,
                "effects": {
                    "severity": {"Mild": 0.0, "Moderate": 0.4, "Severe": 0.9},
                    "hospital": {"Xiehe": 0.2, "Huashan": -0.1, "Ruijin": 0.0,
                                 "Tongren": 0.1, "Zhongshan": -0.1}
                }
            },
            "sigma": {
                "intercept": 0.35,
                "effects": {
                    "severity": {"Mild": 0.0, "Moderate": 0.05, "Severe": 0.10}
                }
            }
        })

    # Structural measure: cost ← wait_minutes, severity
    sim.add_measure_structural("cost",
        formula="wait_minutes * 12 + severity_surcharge",
        effects={"severity_surcharge": {"Mild": 50, "Moderate": 200, "Severe": 500}},
        noise={"family": "gaussian", "sigma": 30})

    # Structural measure: satisfaction ← wait_minutes, severity
    sim.add_measure_structural("satisfaction",
        formula="9 - 0.04 * wait_minutes + severity_adj",
        effects={"severity_adj": {"Mild": 0.5, "Moderate": 0.0, "Severe": -1.5}},
        noise={"family": "gaussian", "sigma": 0.6})

    # ========== Step 2: Relationships & patterns ==========

    # Group-level orthogonal declaration
    sim.declare_orthogonal("entity", "patient",
        rationale="Severity distribution is independent of hospital/department")

    # Cross-group dependency: payment root depends on patient root
    sim.add_group_dependency("payment_method", on=["severity"],
        conditional_weights={
            "Mild":     {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},
            "Moderate": {"Insurance": 0.65, "Self-pay": 0.25, "Government": 0.10},
            "Severe":   {"Insurance": 0.80, "Self-pay": 0.10, "Government": 0.10}
        })

    # Pattern injection
    sim.inject_pattern("outlier_entity",
        target="hospital == 'Xiehe' & severity == 'Severe'",
        col="wait_minutes", params={"z_score": 3.0})

    sim.inject_pattern("trend_break",
        target="hospital == 'Huashan'",
        col="wait_minutes",
        params={"break_point": "2024-03-15", "magnitude": 0.4})

    return sim.generate()
```

=== YOUR TASK ===
[SCENARIO]
{scenario_context}

[AGENT CODE]
````

---

### 2.6 Schema Metadata Output

The SDK returns both the Master DataFrame and structured **Schema Metadata** — the contract between Phase 2 and Phase 3:

```python
schema_metadata = {
    "dimension_groups": {
        "entity":  {"columns": ["hospital", "department"], "hierarchy": ["hospital", "department"]},
        "patient": {"columns": ["severity"], "hierarchy": ["severity"]},
        "payment": {"columns": ["payment_method"], "hierarchy": ["payment_method"]},
        "time":    {"columns": ["visit_date", "day_of_week", "month"], "hierarchy": ["visit_date"]}
    },
    "orthogonal_groups": [
        {"group_a": "entity", "group_b": "patient",
         "rationale": "severity is independent of hospital/department"}
    ],
    "group_dependencies": [
        {"child_root": "payment_method", "on": ["severity"]}
    ],
    "columns": [
        {"name": "hospital",       "group": "entity",  "parent": null,       "type": "categorical", "cardinality": 5},
        {"name": "department",     "group": "entity",  "parent": "hospital", "type": "categorical", "cardinality": 4},
        {"name": "severity",       "group": "patient", "parent": null,       "type": "categorical", "cardinality": 3},
        {"name": "payment_method", "group": "payment", "parent": null,       "type": "categorical", "cardinality": 3},
        {"name": "visit_date",     "group": "time",    "type": "temporal",  "derived": ["day_of_week", "month"]},
        {"name": "wait_minutes",   "type": "measure",  "measure_type": "stochastic", "family": "lognormal"},
        {"name": "cost",           "type": "measure",  "measure_type": "structural", "depends_on": ["wait_minutes"]},
        {"name": "satisfaction",   "type": "measure",  "measure_type": "structural", "depends_on": ["wait_minutes"]}
    ],
    "measure_dag_order": ["wait_minutes", "cost", "satisfaction"],
    "patterns": [
        {"type": "outlier_entity", "target": "hospital=='Xiehe' & severity=='Severe'",
         "col": "wait_minutes"},
        {"type": "trend_break", "target": "hospital=='Huashan'",
         "col": "wait_minutes", "break_point": "2024-03-15"}
    ],
    "total_rows": 500
}
```

> View Extraction uses dimension groups and orthogonal declarations to enumerate legal chart mappings; QA generation uses patterns and the measure DAG to craft hard questions; the dependency graph enables causal reasoning QA.

---

### 2.7 Execution-Error Feedback Loop

Any mathematical or structural error in the LLM's script triggers an informative `Exception` from the SDK, enabling **native code-level self-correction**:

```
1. LLM outputs Python script.
2. Sandbox executes build_fact_table().
3. SUCCESS → proceed to Deterministic Engine (§2.8) + Validation (§2.9).
4. FAILURE → SDK raises typed exception, e.g.:
   "CyclicDependencyError: Measure 'cost' → 'satisfaction' → 'cost' forms a cycle."
   "UndefinedEffectError: 'severity_surcharge' in formula has no definition for 'Severe'."
   "NonRootDependencyError: 'department' is not a group root; cannot use in add_group_dependency."
5. Code + traceback fed back to LLM: "Adjust parameters to resolve the error."
6. Retry (max_retries=3). If all fail → log and skip.
```

> Unlike JSON-config validation that catches only *syntactic* errors, code execution catches *semantic* impossibilities — cyclic dependencies, incomplete effect tables, non-root cross-group dependencies, degenerate distributions. The LLM receives the exact constraint violation for targeted repair.

---

### 2.8 Deterministic Engine Execution

`FactTableSimulator.generate()` runs a **fully deterministic, DAG-ordered pipeline** converting declarations into a Master DataFrame. Given the same `seed`, output is bit-for-bit reproducible. **No LLM calls.**

```python
class FactTableSimulator:
    def generate(self) -> Tuple[pd.DataFrame, dict]:
        rng = np.random.default_rng(self.seed)

        # Pre-flight: build and validate full generation DAG
        full_dag = self._build_full_dag()      # all columns in one DAG
        topo_order = topological_sort(full_dag)

        # α — Non-measure columns: sample roots, drill down, derive temporal
        #     All in topological order of the full DAG
        rows = self._build_skeleton(topo_order, rng)

        # β — Measures: generate in topological order of measure sub-DAG
        for col in topo_order:
            if self._is_stochastic(col):
                rows[col] = self._sample_stochastic(col, rows, rng)
            elif self._is_structural(col):
                rows[col] = self._eval_structural(col, rows, rng)

        # γ — Pattern Injection: outlier scaling, trend breaks, etc.
        rows = self._inject_patterns(rows, rng)

        # δ — Realism (optional): missing data, dirty values, censoring
        if self._has_realism:
            rows = self._inject_realism(rows, rng)

        return self._post_process(rows), self._build_schema_metadata()
```

**Pipeline composition:**

$$M = \tau_{\text{post}} \circ \delta^{?} \circ \gamma \circ \beta \circ \alpha(\text{seed})$$

> Each step is a deterministic function of `(declarations, seed)`. The LLM's contribution ends at writing the SDK script — `generate()` onward is pure computation. The superscript $?$ on $\delta$ indicates that realism injection is optional.

---

### 2.9 Three-Layer Validation

After the engine produces a Master Table (§2.8), a deterministic validator checks correctness at three levels. **No LLM calls** — failures are auto-fixed by adjusting parameters and re-executing.

#### L1: Structural Validation

```python
class SchemaAwareValidator:
    def _L1_structural(self, df, meta):
        checks = []

        # Row count within 10% of target
        target = meta["total_rows"]
        checks.append(Check("row_count",
            passed=abs(len(df) - target) / target < 0.1))

        # Categorical cardinality matches declaration
        for col in meta["columns"]:
            if col["type"] == "categorical":
                actual = df[col["name"]].nunique()
                checks.append(Check(f"cardinality_{col['name']}",
                    passed=actual == col["cardinality"]))

        # Categorical root marginal weights match declaration
        for col in meta["columns"]:
            if col["type"] == "categorical" and col.get("parent") is None:
                observed = df[col["name"]].value_counts(normalize=True)
                max_dev = max(abs(observed[v] - w)
                    for v, w in zip(col["values"], col["weights"]))
                checks.append(Check(f"marginal_{col['name']}",
                    passed=max_dev < 0.10))

        # Measure columns: finite and non-null
        for col in meta["columns"]:
            if col["type"] == "measure":
                checks.append(Check(f"finite_{col['name']}",
                    passed=df[col["name"]].notna().all()
                           and np.isfinite(df[col["name"]]).all()))

        # Orthogonal group independence (chi-squared on root pairs)
        for pair in meta["orthogonal_groups"]:
            ga = meta["dimension_groups"][pair["group_a"]]
            gb = meta["dimension_groups"][pair["group_b"]]
            root_a, root_b = ga["hierarchy"][0], gb["hierarchy"][0]
            ct = pd.crosstab(df[root_a], df[root_b])
            _, p_val, _, _ = scipy.stats.chi2_contingency(ct)
            checks.append(Check(f"orthogonal_{root_a}_{root_b}",
                passed=p_val > 0.05,
                detail=f"χ² p={p_val:.4f} (>0.05 = independent)"))

        # Measure DAG acyclicity (pre-validated, but double-check)
        checks.append(Check("measure_dag_acyclic",
            passed=is_acyclic(meta.get("measure_dag_order", []))))

        return checks
```

#### L2: Statistical Validation

Validation is **aligned with the measure's declaration type** — stochastic measures are tested against their conditional distribution at the declared predictor level; structural measures are tested against their formula residuals.

```python
    def _L2_statistical(self, df, meta):
        checks = []

        # Stochastic measures: conditional distribution test
        for col in meta["columns"]:
            if col.get("measure_type") == "stochastic":
                spec = self._get_measure_spec(col["name"])
                for group_filter, expected_params in spec.iter_predictor_cells():
                    subset = df.query(group_filter) if group_filter else df
                    _, p_val = scipy.stats.kstest(
                        subset[col["name"]], col["family"], args=expected_params)
                    checks.append(Check(f"ks_{col['name']}_{group_filter or 'marginal'}",
                        passed=p_val > 0.05))

        # Structural measures: residual check
        for col in meta["columns"]:
            if col.get("measure_type") == "structural":
                predicted = eval_formula(col["formula"], df)
                residuals = df[col["name"]] - predicted
                checks.append(Check(f"structural_{col['name']}_residual_mean",
                    passed=abs(residuals.mean()) < residuals.std() * 0.1))
                checks.append(Check(f"structural_{col['name']}_residual_std",
                    passed=abs(residuals.std() - col["noise_sigma"]) / col["noise_sigma"] < 0.2))

        # Group dependency: conditional transition vs declared weights
        for dep in meta.get("group_dependencies", []):
            observed = pd.crosstab(df[dep["on"][0]], df[dep["child_root"]], normalize="index")
            max_dev = self._max_conditional_deviation(observed, dep["conditional_weights"])
            checks.append(Check(f"group_dep_{dep['child_root']}",
                passed=max_dev < 0.10,
                detail=f"max deviation from declared transition: {max_dev:.3f}"))

        return checks
```

#### L3: Pattern Validation

```python
    def _L3_pattern(self, df, meta):
        checks = []
        for p in meta["patterns"]:
            if p["type"] == "outlier_entity":
                z = abs(df.query(p["target"])[p["col"]].mean()
                        - df[p["col"]].mean()) / df[p["col"]].std()
                checks.append(Check(f"outlier_{p['col']}", passed=z >= 2.0))

            elif p["type"] == "ranking_reversal":
                m1, m2 = p["metrics"]
                root = meta["dimension_groups"][
                    list(meta["dimension_groups"].keys())[0]]["hierarchy"][0]
                means = df.groupby(root)[[m1, m2]].mean()
                checks.append(Check(f"reversal_{m1}_{m2}",
                    passed=means[m1].rank().corr(means[m2].rank()) < 0))

            elif p["type"] == "trend_break":
                bp = pd.to_datetime(p["break_point"])
                tc = [c["name"] for c in meta["columns"]
                      if c["type"] == "temporal"][0]
                before = df[df[tc] < bp][p["col"]].mean()
                after = df[df[tc] >= bp][p["col"]].mean()
                checks.append(Check(f"trend_{p['col']}",
                    passed=abs(after - before) / before > 0.15))

            elif p["type"] == "dominance_shift":
                checks.append(Check("dominance",
                    passed=self._verify_dominance_change(df, p, meta)))

        return checks
```

#### Auto-Fix Loop (No LLM Re-Call)

```python
AUTO_FIX = {
    "ks_*":         lambda c: widen_variance(c, factor=1.2),
    "outlier_*":    lambda c: amplify_magnitude(c, factor=1.3),
    "trend_*":      lambda c: amplify_magnitude(c, factor=1.3),
    "orthogonal_*": lambda c: reshuffle_pair(c),
}

def generate_with_validation(build_fn, meta, max_retries=3):
    for attempt in range(max_retries):
        df = build_fn(seed=42 + attempt)
        report = SchemaAwareValidator().validate(df, meta)
        if report.all_passed:
            return df, report
        for check in report.failures:
            strategy = match_strategy(check.name, AUTO_FIX)
            if strategy:
                strategy(check)
    return df, report  # soft failure after max retries
```

> Three-layer validation runs in milliseconds. Validation is aligned with declaration level: stochastic measures are tested against their conditional distribution, structural measures against both residual mean and variance, categorical roots against declared marginal weights.

---

### 2.10 Design Advantages

The atomic-grain fact table with dimension groups and closed-form measures provides maximum downstream flexibility:

- **Distribution charts** (histogram, box, violin) use raw rows directly.
- **Aggregation charts** (bar, pie, line) apply `GROUP BY` on hierarchy roots.
- **Drill-down charts** (grouped/stacked bar, treemap) exploit within-group hierarchy with per-parent conditionals.
- **Relationship charts** (scatter, bubble) leverage row-level structural dependencies.
- **Multi-view dashboards** slice the same Master Table along orthogonal groups.
- **Causal reasoning QA** exploits the explicit measure DAG.

$$\text{View}_{\text{chart}} = \sigma_{\text{filter}} \circ \gamma_{\text{agg}} \circ \pi_{\text{cols}}(M)$$

where $\sigma$ = row selection, $\gamma$ = group-by aggregation, $\pi$ = column projection.
