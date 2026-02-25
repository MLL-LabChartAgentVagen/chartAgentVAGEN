## PHASE 2: Agentic Data Simulator (SDK-Driven)

> **Core Contribution:** Replace fragile JSON-based DGP specifications with **Code-as-DGP** — the LLM writes executable Python scripts calling a type-safe SDK. Schema definition, distribution control, inter-column relationships, and pattern injection are unified in a single code pass. Errors surface as native Python exceptions for self-correction. A three-layer validator then ensures structural, statistical, and pattern-level correctness — all without additional LLM calls.

---

### 2.1 The `FactTableSimulator` SDK

The SDK encapsulates all statistical machinery behind a minimal, strongly-typed API. The LLM assembles building blocks within a whitelist of safe operations, simultaneously accomplishing:

1. **Schema Definition** — each `add_*()` call declares a column and its generation rule.
2. **Data Generation Program (DGP)** — distributions, relationships, patterns, and realism specified as code.

#### 2.1.1 Core API

**Step 1 — Declare all columns first:**

| API Method | Function | Safeguard |
|------------|----------|-----------|
| `add_category(name, values, weights, group, parent)` | Declare categorical column. `group` assigns it to a named dimension group. Optional `parent` links to a parent column within the same group for hierarchy. | Auto-normalizes weights; rejects empty values; validates parent exists in same group. |
| `add_measure(name, dist, params)` | Declare numerical column with a named distribution. | Type-checks `dist`; blocks degenerate params (zero variance, negative scale). |
| `add_temporal(name, start, end, freq)` | Declare temporal dimension column. | Validates date parsing and frequency string. |

**Step 2 — Declare relationships and patterns (after all columns):**

| API Method | Function | Safeguard |
|------------|----------|-----------|
| `add_conditional(measure, on, mapping)` | Declare that a measure's distribution parameters vary by a categorical column: $P(\text{measure} \mid \text{on})$. | Validates `on` is categorical and `measure` exists; checks param completeness for all categories. |
| `add_dependency(target, formula, noise_sigma)` | Define deterministic functional dependency: `target = f(other_cols) + noise`. | Formula parsed in isolated sandbox; restricted to basic math ops. |
| `add_correlation(col_a, col_b, target_r)` | Inject Pearson correlation between two measures via Gaussian Copula. | Validates PSD; raises `ValueError` if target infeasible given marginals. |
| `declare_orthogonal(group_a, group_b, rationale)` | Declare two dimension groups as statistically independent. Propagates to all cross-group column pairs. | Validates both groups exist and contain categorical columns. See §2.1.2. |
| `inject_pattern(type, target, col, params)` | Plant a narrative-driven statistical anomaly. | Clamps physical bounds; validates `target` filter is non-empty. |
| `set_realism(missing_rate, dirty_rate, censoring)` | Simulate data imperfections. | Protects primary key; enforces rate bounds. |

**Supported distributions:** `"gaussian"`, `"lognormal"`, `"gamma"`, `"beta"`, `"uniform"`, `"poisson"`, `"exponential"`, `"mixture"`

**Pattern types:** `"outlier_entity"`, `"trend_break"`, `"ranking_reversal"`, `"dominance_shift"`, `"convergence"`, `"seasonal_anomaly"`

---

#### 2.1.2 Dimension Groups, Hierarchy, and Orthogonality

**Dimension groups** are the central structural abstraction. Each categorical column belongs to exactly one named group. Columns within a group form a hierarchy via `parent`; columns across groups can be declared independent via `declare_orthogonal()`.

**Within-group hierarchy (via `parent`):**

```
Group "entity":   hospital ← department ← ward
Group "patient":  severity ← acuity_level
Group "payment":  payment_method
```

Each group has a **root** column (no parent). Child columns represent drill-down within the same semantic dimension. The engine samples children conditionally on their parent — `P(department | hospital)` follows the declared weights *within* the parent context.

**Cross-group orthogonality (via `declare_orthogonal()`):**

Independence is a property between *entire dimension groups*, not individual columns. If Group A ⊥ Group B, then **all cross-group pairs are automatically independent** — no need to enumerate.

```python
# "entity" group and "patient" group are independent:
sim.declare_orthogonal("entity", "patient",
    rationale="Severity distribution does not depend on which hospital")
# This automatically implies:
#   hospital ⊥ severity,  hospital ⊥ acuity_level,
#   department ⊥ severity, department ⊥ acuity_level,
#   ward ⊥ severity,      ward ⊥ acuity_level

# NOTE: "entity" is NOT declared orthogonal to "payment"
#        (some departments may favor certain payment methods)
```

**What `declare_orthogonal()` does:**

1. **Generation:** Ensures $P(A,B) \approx P(A) \cdot P(B)$ for all cross-group column pairs via independent sampling.
2. **Validation (L1):** Chi-squared test on root-level cross-group pairs; flags warning if $p < 0.05$.
3. **View Extraction (Phase 3):** Enables "Orthogonal Contrast" dashboards — slicing the same metric by two independent dimensions.

> **Design principle:** Dimension groups with automatic orthogonality propagation eliminate $O(n^2)$ pairwise declarations. They also prevent logical contradictions (e.g., declaring `hospital ⊥ severity` while `department ⊥̸ severity` when `department` is a child of `hospital`).

---

### 2.2 LLM Code Generation Prompt

```text
SYSTEM:
You are an expert Data Scientist Agent. Build an Atomic-Grain Fact Table
using the `FactTableSimulator` Python SDK.

INPUT:
1. Scenario Context: real-world setting with entities, metrics, and temporal grain.
2. SDK Reference: you may ONLY use the methods listed below.

AVAILABLE SDK METHODS (declare columns FIRST, then relationships):
  # --- Step 1: Column declarations ---
  sim.add_category(name, values, weights, group, parent=None)
  sim.add_temporal(name, start, end, freq)
  sim.add_measure(name, dist, params)

  # --- Step 2: Relationships & patterns ---
  sim.add_conditional(measure, on, mapping)              # P(measure | category)
  sim.add_dependency(target, formula, noise_sigma)        # target = f(cols) + noise
  sim.add_correlation(col_a, col_b, target_r)
  sim.declare_orthogonal(group_a, group_b, rationale)     # group-level independence
  sim.inject_pattern(type, target, col, params)           # type: see PATTERN_TYPES
  sim.set_realism(missing_rate, dirty_rate, censoring=None)

SUPPORTED DISTRIBUTIONS: "gaussian", "lognormal", "gamma", "beta", "uniform",
                         "poisson", "exponential", "mixture"

PATTERN_TYPES: "outlier_entity", "trend_break", "ranking_reversal",
               "dominance_shift", "convergence", "seasonal_anomaly"

HARD CONSTRAINTS — the script MUST satisfy ALL:
1. ATOMIC_GRAIN: each row = one indivisible event.
2. At least 2 dimension groups, each with ≥1 categorical column, plus ≥2 measures.
3. All column declarations (Step 1) BEFORE any relationship declarations (Step 2).
4. At least 1 declare_orthogonal() between genuinely independent groups.
5. At least 1 add_correlation() and 2 inject_pattern() calls.
6. Output must be pure, valid Python returning sim.generate().

SOFT GUIDELINES — include when naturally fitting the domain:
- Temporal dimension (if data has a time component).
- Within-group hierarchy via parent (e.g., region → city → district).
- 3+ measures (enables richer chart coverage).
- Conditional distributions via add_conditional() when measures logically
  vary by category (e.g., wait time differs by severity).
- Numerical correlation pairs (at least 1 positive or negative).

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

    # Dimension group "patient": severity (standalone)
    sim.add_category("severity",
        values=["Mild", "Moderate", "Severe"],
        weights=[0.50, 0.35, 0.15],
        group="patient")

    # Dimension group "payment": payment_method (standalone)
    sim.add_category("payment_method",
        values=["Insurance", "Self-pay", "Government"],
        weights=[0.60, 0.30, 0.10],
        group="payment")

    sim.add_temporal("visit_date",
        start="2024-01-01", end="2024-06-30", freq="daily")

    sim.add_measure("wait_minutes",
        dist="lognormal", params={"mu": 3.0, "sigma": 0.5})

    sim.add_measure("cost",
        dist="lognormal", params={"mu": 6.0, "sigma": 0.8})

    sim.add_measure("satisfaction",
        dist="beta", params={"alpha": 5, "beta": 2}, scale=[1, 10])

    # ========== Step 2: Relationships & patterns ==========

    # Conditional distribution: wait_minutes varies by severity
    sim.add_conditional("wait_minutes", on="severity", mapping={
        "Mild":     {"mu": 2.5, "sigma": 0.4},
        "Moderate": {"mu": 3.0, "sigma": 0.5},
        "Severe":   {"mu": 3.8, "sigma": 0.6}
    })

    # Functional dependency
    sim.add_dependency("cost",
        formula="wait_minutes * 12 + severity_base",
        noise_sigma=30)

    # Correlations
    sim.add_correlation("wait_minutes", "satisfaction", target_r=-0.55)

    # Group-level orthogonal declarations
    sim.declare_orthogonal("entity", "patient",
        rationale="Severity distribution is independent of hospital/department")
    sim.declare_orthogonal("entity", "payment",
        rationale="Payment method is independent of which hospital/department")
    # NOTE: "patient" × "payment" NOT declared orthogonal
    #        (severe cases more likely to use insurance)

    # Pattern injection
    sim.inject_pattern("outlier_entity",
        target="hospital == 'Xiehe' & severity == 'Severe'",
        col="wait_minutes", params={"z_score": 3.0})

    sim.inject_pattern("ranking_reversal",
        target=None, col=None,
        params={"metrics": ["wait_minutes", "satisfaction"],
                "description": "Xiehe has longest wait but highest satisfaction"})

    sim.inject_pattern("trend_break",
        target="hospital == 'Huashan'",
        col="wait_minutes",
        params={"break_point": "2024-03-15", "magnitude": 0.4})

    # Realism
    sim.set_realism(missing_rate=0.03, dirty_rate=0.02,
                    censoring={"col": "cost", "type": "right", "threshold": 5000})

    return sim.generate()
```

=== YOUR TASK ===
[SCENARIO]
{scenario_context}
[AGENT CODE]
```

---

### 2.3 Schema Metadata Output

The SDK returns both the Master DataFrame and structured **Schema Metadata** — the contract between Phase 2 and Phase 3:

```python
schema_metadata = {
    "dimension_groups": {
        "entity":  {"columns": ["hospital", "department"], "hierarchy": ["hospital", "department"]},
        "patient": {"columns": ["severity"], "hierarchy": ["severity"]},
        "payment": {"columns": ["payment_method"], "hierarchy": ["payment_method"]}
    },
    "orthogonal_groups": [
        {"group_a": "entity", "group_b": "patient",
         "rationale": "severity is independent of hospital/department"},
        {"group_a": "entity", "group_b": "payment",
         "rationale": "payment method is independent of hospital/department"}
    ],
    "columns": [
        {"name": "hospital",       "group": "entity",  "parent": null,       "type": "categorical", "cardinality": 5},
        {"name": "department",     "group": "entity",  "parent": "hospital", "type": "categorical", "cardinality": 4},
        {"name": "severity",       "group": "patient", "parent": null,       "type": "categorical", "cardinality": 3},
        {"name": "payment_method", "group": "payment", "parent": null,       "type": "categorical", "cardinality": 3},
        {"name": "visit_date",     "type": "temporal"},
        {"name": "wait_minutes",   "type": "measure"},
        {"name": "cost",           "type": "measure"},
        {"name": "satisfaction",   "type": "measure"}
    ],
    "conditionals": [
        {"measure": "wait_minutes", "on": "severity",
         "mapping": {"Mild": {"mu": 2.5}, "Moderate": {"mu": 3.0}, "Severe": {"mu": 3.8}}}
    ],
    "correlations": [
        {"col_a": "wait_minutes", "col_b": "satisfaction", "target_r": -0.55}
    ],
    "dependencies": [
        {"target": "cost", "formula": "wait_minutes * 12 + severity_base"}
    ],
    "patterns": [
        {"type": "outlier_entity", "target": "hospital=='Xiehe' & severity=='Severe'",
         "col": "wait_minutes"},
        {"type": "ranking_reversal", "metrics": ["wait_minutes", "satisfaction"]},
        {"type": "trend_break", "target": "hospital=='Huashan'",
         "col": "wait_minutes", "break_point": "2024-03-15"}
    ],
    "total_rows": 500
}
```

> View Extraction uses dimension groups and orthogonal declarations to enumerate legal chart mappings and compose multi-view dashboards; QA generation uses patterns and conditionals to craft hard questions; the dependency graph enables causal reasoning QA.

---

### 2.4 Execution-Error Feedback Loop

Any mathematical or structural error in the LLM's script triggers an informative `Exception` from the SDK, enabling **native code-level self-correction**:

```
1. LLM outputs Python script.
2. Sandbox executes build_fact_table().
3. SUCCESS → proceed to Deterministic Engine (§2.5) + Validation (§2.6).
4. FAILURE → SDK raises typed exception, e.g.:
   "ValueError: Cannot achieve target_r=-0.8 between wait_minutes (σ=12.3)
    and satisfaction (σ=1.1). Consider increasing variance or relaxing target."
5. Code + traceback fed back to LLM: "Adjust parameters to resolve the error."
6. Retry (max_retries=3). If all fail → log and skip.
```

> Unlike JSON-config validation that catches only *syntactic* errors, code execution catches *semantic* impossibilities (infeasible correlations, empty filters, degenerate distributions). The LLM receives the exact constraint violation for targeted repair.

---

### 2.5 Deterministic Engine Execution

`FactTableSimulator.generate()` runs a **fully deterministic pipeline** converting declarations into a Master DataFrame. Given the same `seed`, output is bit-for-bit reproducible. **No LLM calls.**

```python
class FactTableSimulator:
    def generate(self) -> Tuple[pd.DataFrame, dict]:
        rng = np.random.default_rng(self.seed)

        # β — Dimensional Skeleton: build group hierarchies,
        #     cross-join orthogonal groups, repeat to target_rows
        rows = self._build_skeleton(rng)

        # δ — Marginal Distributions: sample each add_measure()
        for col, spec in self._measure_specs.items():
            rows[col] = self._sample_distribution(spec, rows, rng)

        # γ — Conditional Overrides: apply add_conditional() mappings
        #     to adjust measure params per categorical value
        for cond in self._conditional_specs:
            rows = self._apply_conditional(cond, rows, rng)

        # λ — Functional Dependencies: evaluate add_dependency() formulas
        for dep in self._dependency_specs:
            rows[dep.target] = self._eval_dependency(dep, rows, rng)

        # ψ — Correlation Injection: Gaussian Copula on add_correlation() pairs
        rows = self._inject_correlations(rows, rng)

        # φ — Pattern Injection: outlier scaling, trend breaks, etc.
        rows = self._inject_patterns(rows, rng)

        # ρ — Realism: missing data, dirty values, censoring
        rows = self._inject_realism(rows, rng)

        return self._post_process(rows), self._build_schema_metadata(rows)
```

**Pipeline composition:**

$$M = \tau_{\text{post}} \circ \rho \circ \phi \circ \psi \circ \lambda \circ \gamma \circ \delta \circ \beta(\text{seed})$$

> Each step is a deterministic function of `(declarations, seed)`. The LLM's contribution ends at writing the SDK script — `generate()` onward is pure computation.

---

### 2.6 Three-Layer Validation

After the engine produces a Master Table (§2.5), a deterministic validator checks correctness at three levels. **No LLM calls** — failures are auto-fixed by adjusting parameters and re-executing.

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

        return checks
```

#### L2: Statistical Validation

```python
    def _L2_statistical(self, df, meta):
        checks = []

        # Correlation targets
        for corr in meta["correlations"]:
            actual_r = df[corr["col_a"]].corr(df[corr["col_b"]])
            checks.append(Check(f"corr_{corr['col_a']}_{corr['col_b']}",
                passed=abs(actual_r - corr["target_r"]) < 0.15,
                detail=f"target={corr['target_r']}, actual={actual_r:.3f}"))

        # Functional dependency residuals
        for dep in meta.get("dependencies", []):
            predicted = eval_formula(dep["formula"], df)
            residual_std = (df[dep["target"]] - predicted).std()
            checks.append(Check(f"dep_{dep['target']}",
                passed=residual_std < df[dep["target"]].std() * 0.5))

        # Distribution shape (KS test against declared distribution)
        for col in meta["columns"]:
            if col["type"] == "measure" and col.get("declared_dist"):
                clean = df[col["name"]].dropna()
                _, p_val = scipy.stats.kstest(
                    clean, col["declared_dist"], args=col["declared_params"])
                checks.append(Check(f"ks_{col['name']}",
                    passed=p_val > 0.05))

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
    "corr_*":       lambda c: relax_target_r(c, step=0.05),
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

> Three-layer validation runs in milliseconds. Auto-fix applies targeted parameter adjustments — correlation relaxation, variance widening, pattern amplification — and re-runs the engine. Typically converges in 1–2 retries at near-zero cost.

---

### 2.7 Design Advantages

The atomic-grain fact table with dimension groups provides maximum downstream flexibility:

- **Distribution charts** (histogram, box, violin) use raw rows directly.
- **Aggregation charts** (bar, pie, line) apply `GROUP BY` on hierarchy roots.
- **Drill-down charts** (grouped/stacked bar, treemap) exploit within-group hierarchy.
- **Relationship charts** (scatter, bubble) leverage row-level correlations.
- **Multi-view dashboards** slice the same Master Table along orthogonal groups.

$$\text{View}_{\text{chart}} = \sigma_{\text{filter}} \circ \gamma_{\text{agg}} \circ \pi_{\text{cols}}(M)$$

where $\sigma$ = row selection, $\gamma$ = group-by aggregation, $\pi$ = column projection.
