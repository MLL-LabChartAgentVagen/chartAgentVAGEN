# Mental model analysis of LLM framework design

**Created:** 3/19/2026 11:33:44  
**Updated:** 3/19/2026 11:43:46  
**Exported:** 3/19/2026 11:45:38  
**Link:** [https://claude.ai/chat/f771718d-38df-4468-aa6f-34059baf725e](https://claude.ai/chat/f771718d-38df-4468-aa6f-34059baf725e)  

## Prompt:
2026/3/19 11:33:45

> File: phase_2.md

<role>
You are a senior ML systems architect with deep expertise in LLM pipeline design, 
agentic SDK patterns, and synthetic data generation. You excel at explaining 
complex distributed systems using precise analogies and layered mental models.
</role>
<objective>
Help me build a complete, accurate mental model of the framework design document 
below, so I can implement Phase 2 in Python without conceptual blind spots.
</objective>
<framework_design>
phase_2.md attached
</framework_design>
---
Execute the following 4-phase analysis in strict sequence. Do not skip ahead.
## Phase 1 — Structural Extraction (No interpretation yet)
Read the document and output ONLY:
1. A bullet list of every named component/module/agent/class mentioned
2. A bullet list of every data flow or handoff described (A → B → C format)
3. A bullet list of every design decision or constraint stated explicitly
Do not explain or interpret anything in Phase 1. Extract only.
---
## Phase 2 — Architecture Map
Using only what you extracted in Phase 1, produce:
**2a. One-paragraph plain-English summary** of what this system does end-to-end 
(write as if explaining to a software engineer who has never seen this doc)
**2b. Component relationship diagram** using ASCII or a structured list showing:
- Which components own which responsibilities
- Which components call/depend on other components  
- Where data enters and exits the system
**2c. The critical path** — trace the single most important execution flow 
through the system from trigger to final output, step by step.
---
## Phase 3 — Concept Deep Dives
First, identify the 3–5 concepts in this framework that are most likely to cause 
implementation confusion or bugs if misunderstood. List them with one sentence 
explaining WHY each is a risk.
Then, for EACH identified concept:
**Concept name:**  
**What it is** (precise technical definition, 2–3 sentences)  
**Why it exists** (the design problem it solves)  
**Concrete analogy** (map it to a familiar system: databases, web servers, assembly lines, etc.)  
**Common misunderstanding** (what a developer might wrongly assume)  
**Python implementation hint** (1–2 sentences on how this typically manifests in code)  
---
## Phase 4 — Verification & Gap Check
4a. List any design decisions the document leaves ambiguous or underspecified 
    (things I will need to decide myself during implementation)
4b. List any external dependencies, libraries, or APIs implied but not named 
    that I should identify before starting Phase 2 implementation
4c. Write 3 comprehension-check questions for me to answer back to you — 
    if I can answer all 3 correctly, I have understood the framework well enough 
    to begin coding.



## Response:
2026/3/19 11:36:43

````plaintext
Thought process: Thinking about extracting and analyzing a framework design document through four sequential analytical phases.

Let me read the uploaded document first.
````

````plaintext
View: Reading the Phase 2 design document
````

````plaintext
Thought process: Recognized incomplete document and prepared to retrieve remainder.

The file was truncated. Let me view the rest.
````

````plaintext
View: Reading truncated portion of the document
````

````plaintext
Thought process: Commenced document review of remaining section.

Let me also read the truncated portion from lines 324-396.
````

````plaintext
View: Reading remaining truncated lines
````

````plaintext
Thought process: Assembled framework document for structured four-phase analysis.

Good, now I have the full document. Let me produce the 4-phase analysis.
````

Now I have the complete document. Let me execute the four-phase analysis.

---

# Phase 1 — Structural Extraction

## 1.1 Named Components / Modules / Agents / Classes

- `FactTableSimulator` — the core SDK class
- `SchemaAwareValidator` — three-layer validation class
- `Check` — individual validation result object
- `add_category()` method
- `add_temporal()` method
- `add_measure()` method (stochastic root)
- `add_measure_structural()` method (structural/derived)
- `declare_orthogonal()` method
- `add_group_dependency()` method
- `inject_pattern()` method
- `set_realism()` method
- `generate()` method (deterministic engine)
- Dimension Groups (named structural abstraction)
- Measure DAG (directed acyclic graph of measure dependencies)
- Full Generation DAG (unified DAG over all column types)
- Schema Metadata (output contract dict)
- Execution-Error Feedback Loop
- Auto-Fix Loop (parameter adjustment without LLM)
- LLM Code Generation Prompt (the system/few-shot template)
- `generate_with_validation()` function
- `AUTO_FIX` dispatch table
- L1 Structural Validation layer
- L2 Statistical Validation layer
- L3 Pattern Validation layer

## 1.2 Data Flows / Handoffs

- Phase 1 Scenario Context → LLM Code Generation Prompt → LLM → Python SDK script
- LLM SDK script → Sandbox execution → `build_fact_table()` call
- `build_fact_table()` → `FactTableSimulator` (column declarations → relationship declarations)
- `FactTableSimulator.generate()` pipeline: α (skeleton/non-measure columns) → β (measures in topo order) → γ (pattern injection) → δ? (optional realism) → `_post_process()` → `(DataFrame, schema_metadata)`
- Within α: independent roots → cross-group dependent roots → within-group children → temporal derivations (all in topological order)
- Within β: stochastic root measures → structural measures (topological order of measure sub-DAG)
- Execution failure → typed SDK exception → traceback fed back to LLM → retry (max 3)
- `(DataFrame, schema_metadata)` → `SchemaAwareValidator.validate()` → L1 → L2 → L3 → validation report
- Validation failure → `AUTO_FIX` dispatch → parameter adjustment → re-execute `build_fn` → re-validate (max 3 retries)
- Schema Metadata → Phase 3 (view extraction, QA generation)

## 1.3 Design Decisions / Constraints

- **Code-as-DGP**: LLM writes executable Python calling a type-safe SDK, replacing JSON-based DGP specs
- **Closed-form declaration**: each measure declared exactly once as a complete data-generating program; no incremental patching
- **All column declarations (Step 1) must precede all relationship declarations (Step 2)**
- **Atomic grain**: each row = one indivisible event; no cross-product materialization
- **Event-level generation**: rows generated as independent atomic events, not via cube expansion
- **DAG constraint on measures**: all measure dependencies must be acyclic; structural measures may only reference previously declared measures; generation order resolved by topological sort
- **Root-only cross-group dependency**: `add_group_dependency()` restricted to group root columns (no parent); root-level dependency graph must be acyclic
- **Orthogonality propagates at group level**: declaring two groups orthogonal makes all cross-group column pairs independent
- **Cross-group independence is opt-in, not default**
- **Each categorical column belongs to exactly one dimension group**
- **Temporal columns are a special dimension group**; derived columns extracted automatically
- **Supported distributions**: gaussian, lognormal, gamma, beta, uniform, poisson, exponential, mixture
- **Pattern types**: outlier_entity, trend_break, ranking_reversal, dominance_shift, convergence, seasonal_anomaly
- **Deterministic engine**: `generate()` is fully deterministic given `(declarations, seed)` — no LLM calls
- **Three-layer validation without LLM calls**: L1 structural, L2 statistical, L3 pattern
- **Auto-fix loop**: validation failures trigger parameter adjustments and re-execution, not LLM re-calls (max 3 retries)
- **Execution-error feedback loop**: SDK raises typed exceptions; code + traceback fed back to LLM for repair (max 3 retries)
- **Hard constraints on LLM output**: ≥2 dimension groups each with ≥1 categorical, ≥2 measures, ≥1 orthogonal declaration, ≥1 structural measure, ≥2 pattern injections, pure valid Python, acyclic DAGs, every symbolic effect must have explicit numeric definition
- **Weights auto-normalized; empty values rejected; parent existence validated**
- **`param_model` uses intercept + sum-of-effects model**: θⱼ = β₀ + Σ βₘ(Xₘ)
- **Schema metadata is the contract between Phase 2 and Phase 3**
- **Bit-for-bit reproducibility** given same seed

---

# Phase 2 — Architecture Map

## 2a. One-Paragraph Summary

This system is a synthetic tabular data generation framework where an LLM writes a Python script that calls a type-safe SDK (`FactTableSimulator`) to declare columns, distributions, inter-column dependencies, and statistical patterns — all as code rather than JSON configuration. The SDK internally builds a unified directed acyclic graph over all declared columns (categorical hierarchies, temporal derivations, stochastic measures, structural/derived measures), then a deterministic engine walks that DAG in topological order to generate each row as an independent atomic event: first sampling categorical and temporal columns from roots down through hierarchies and cross-group dependencies, then sampling stochastic measures from parameterized distributions whose parameters are conditioned on categorical context, then computing structural measures via formulas that reference upstream measures, and finally injecting narrative-driven anomaly patterns and optional data imperfections. The resulting DataFrame plus a structured schema metadata dictionary are then passed through a three-layer deterministic validator (structural integrity, statistical fidelity, pattern presence) with an auto-fix retry loop — and if the LLM's original script had execution errors, a separate feedback loop sends the typed exception back to the LLM for targeted repair. The schema metadata serves as the contract for downstream phases (view extraction, QA generation).

## 2b. Component Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL INPUTS                                 │
│  Phase 1 Scenario Context ──┐                                       │
│  (domain, entities, metrics, │                                       │
│   target_rows, temporal)     │                                       │
└──────────────────────────────┼──────────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  LLM CODE GENERATION                                                 │
│  ┌───────────────────────────────┐                                   │
│  │  System Prompt + Few-Shot     │                                   │
│  │  (SDK reference, constraints, │──► LLM ──► Python SDK Script      │
│  │   scenario context)           │          (build_fact_table())      │
│  └───────────────────────────────┘                                   │
│                                           │                          │
│         ┌──── on exception ◄──────────────┤                          │
│         │   (typed error + traceback)      │                          │
│         │   max 3 retries                  ▼                         │
│         │                      ┌──────────────────┐                  │
│         └─────────────────────►│ Sandbox Execution │                 │
│                                └────────┬─────────┘                  │
└─────────────────────────────────────────┼────────────────────────────┘
                                          ▼
┌──────────────────────────────────────────────────────────────────────┐
│  FactTableSimulator SDK                                              │
│                                                                      │
│  ┌─ Declaration Registry ──────────────────────────────────────┐     │
│  │  add_category()  ─┐                                         │     │
│  │  add_temporal()   ├─► Internal Column & Dependency Store     │     │
│  │  add_measure()    │   (groups, hierarchies, param_models,    │     │
│  │  add_measure_     │    formulas, patterns, orthogonality)    │     │
│  │    structural()   │                                         │     │
│  │  declare_         │                                         │     │
│  │    orthogonal()   │                                         │     │
│  │  add_group_       │                                         │     │
│  │    dependency()  ─┘                                         │     │
│  │  inject_pattern()                                           │     │
│  │  set_realism()                                              │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                         │                                            │
│                         ▼  generate()                                │
│  ┌─ Deterministic Engine (§2.8) ───────────────────────────────┐     │
│  │  _build_full_dag() → topological_sort()                     │     │
│  │                                                             │     │
│  │  α  _build_skeleton()     roots → deps → children → derive  │     │
│  │  β  _sample_stochastic()  stochastic roots (topo order)     │     │
│  │     _eval_structural()    structural measures (topo order)  │     │
│  │  γ  _inject_patterns()    outliers, trend breaks, etc.      │     │
│  │  δ? _inject_realism()     missing, dirty, censoring         │     │
│  │  → _post_process()                                          │     │
│  └──────────────────────────┬──────────────────────────────────┘     │
│                             │                                        │
│                             ▼                                        │
│              (pd.DataFrame, schema_metadata: dict)                   │
└─────────────────────────────┼────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  SchemaAwareValidator                                                │
│                                                                      │
│  L1: Structural   (row count, cardinality, marginals, finiteness,   │
│                    orthogonality chi², DAG acyclicity)                │
│  L2: Statistical  (KS test on stochastic, residual check on         │
│                    structural, conditional transition on group deps) │
│  L3: Pattern      (outlier z-score, ranking reversal, trend break,  │
│                    dominance shift)                                  │
│                              │                                       │
│         ┌── all passed? ─────┤                                       │
│         │                    │ no                                     │
│         ▼ yes                ▼                                       │
│   FINAL OUTPUT         AUTO_FIX dispatch                             │
│                        (widen variance, amplify, reshuffle)          │
│                        → re-execute build_fn (max 3 retries)        │
└─────────────────────────────┼────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  EXTERNAL OUTPUTS                                                    │
│  • Master DataFrame (atomic-grain fact table)                        │
│  • Schema Metadata → Phase 3 (view extraction, QA generation)        │
└──────────────────────────────────────────────────────────────────────┘
```

## 2c. Critical Path

The single most important execution flow from trigger to final output:

1. **Phase 1 scenario context arrives** (domain, entities, metrics, temporal grain, target_rows)
2. **LLM receives prompt** (system prompt with SDK reference + hard constraints + few-shot example + scenario context)
3. **LLM generates a Python script** containing a `build_fact_table()` function that calls `FactTableSimulator` SDK methods in the required order: column declarations first, then relationships/patterns
4. **Sandbox executes** the script. If it raises a typed exception → error + traceback sent back to LLM → retry up to 3 times
5. **`FactTableSimulator.generate()`** runs:
   - Builds full generation DAG from all declarations; computes topological order
   - **α**: Generates non-measure columns row-by-row in topo order (independent roots → cross-group dependent roots → within-group children → temporal derivations)
   - **β**: Generates measures in topo order (stochastic roots sampled from parameterized distributions → structural measures computed via formula + noise)
   - **γ**: Injects declared patterns onto the full DataFrame
   - **δ?**: Optionally injects realism imperfections
6. **Returns** `(DataFrame, schema_metadata)`
7. **`SchemaAwareValidator`** runs L1 → L2 → L3 checks against the schema metadata
8. If failures → **AUTO_FIX** adjusts parameters and re-executes `build_fn` with a new seed (up to 3 retries)
9. **Final output**: validated Master DataFrame + schema_metadata dict handed to Phase 3

---

# Phase 3 — Concept Deep Dives

## Risk-Ranked Concepts

1. **The Full Generation DAG vs. the Measure sub-DAG** — Two overlapping DAGs govern generation order; confusing which DAG applies where causes incorrect topological ordering or missed dependencies.
2. **Stochastic vs. Structural measure distinction** — The boundary determines whether a column is sampled or computed; getting it wrong produces values with wrong statistical properties and breaks validation.
3. **Dimension Groups and the root-only cross-group constraint** — The group abstraction controls what dependencies are legal; misunderstanding "root" causes illegal dependency declarations that should throw exceptions.
4. **The intercept + sum-of-effects param_model** — The parameter computation model is the core of conditional distribution specification; implementing it incorrectly silently produces wrong distributions.
5. **Two separate retry loops (execution-error vs. validation auto-fix)** — These loops have different triggers, different fix strategies, and different scopes; conflating them creates a tangled control flow.

---

### Concept 1: Full Generation DAG vs. Measure Sub-DAG

**What it is:** The system maintains two DAG views. The *full generation DAG* includes every column (categorical roots, categorical children via `parent`, temporal derivations, cross-group dependencies via `add_group_dependency`, stochastic measures, structural measures). The *measure sub-DAG* is a subset containing only measure columns and their inter-measure edges (structural → stochastic references). Both are resolved via topological sort, but the full DAG governs the overall column generation order while the measure sub-DAG determines only the ordering within step β.

**Why it exists:** Categorical columns and temporal derivations must exist before any measure can reference them as predictors. Meanwhile, structural measures must wait for their upstream measures. A single unified DAG captures both kinds of dependency, ensuring that when you generate column X, every column X depends on already has a value.

**Concrete analogy:** Think of a build system like Make. The full DAG is the complete dependency graph of all build targets (libraries, objects, executables). The measure sub-DAG is like looking at just the executables and their link-time dependencies on each other — a useful subview, but compilation still needs the full graph to decide when to build each `.o` file.

**Common misunderstanding:** A developer might assume the measure DAG is the *only* DAG and process categorical columns in declaration order rather than topological order. This fails when a categorical column has a cross-group dependency on another categorical (e.g., `payment_method` depends on `severity`): if `severity` hasn't been generated yet, sampling `payment_method` conditionally is impossible.

**Python implementation hint:** Build one `networkx.DiGraph` from all column declarations and dependency edges. Call `nx.topological_sort()` once. During generation, iterate that single order; branch on column type (categorical/temporal/stochastic/structural) to dispatch to the right sampling function.

---

### Concept 2: Stochastic vs. Structural Measure Distinction

**What it is:** A *stochastic root measure* is sampled directly from a named distribution whose parameters are functions of categorical context only — it has no incoming edges from other measures in the DAG. A *structural (derived) measure* is computed deterministically from a formula that references other measures plus categorical effects, with optional additive noise. The distinction is binary: if a measure's value depends on any other measure column, it's structural; otherwise, it's stochastic.

**Why it exists:** The previous design allowed incremental patching (add distribution, then add dependency, then add correlation), causing the declared and actual distributions to diverge. By making each measure self-contained, you get a single source of truth: stochastic measures can be validated with a KS test against their declared distribution, while structural measures are validated by checking that residuals (actual − formula prediction) match the declared noise distribution.

**Concrete analogy:** In a spreadsheet, a stochastic measure is like a cell with `=RANDBETWEEN(...)` — its value comes from nowhere but a random generator and some parameters. A structural measure is like a cell with `=A1 * 12 + B1 + RANDBETWEEN(...)` — it's a formula referencing other cells, plus some jitter.

**Common misunderstanding:** Assuming that because both types can be "influenced by categorical context," they work the same way internally. They don't: stochastic measures use the `param_model` (intercept + effects → distribution parameters → sample), while structural measures use a `formula` string + `effects` dict + `noise` spec (evaluate expression → add categorical surcharges → add noise). Using `param_model` for a structural measure or `formula` for a stochastic one is a type error.

**Python implementation hint:** Implement `_sample_stochastic()` and `_eval_structural()` as completely separate code paths. The stochastic path resolves the param_model to concrete parameter values then calls `rng.lognormal(mu, sigma)` etc. The structural path evaluates a symbolic expression over the current row's already-generated measure values, adds resolved categorical effects, then adds a noise draw.

---

### Concept 3: Dimension Groups and Root-Only Cross-Group Constraint

**What it is:** A *dimension group* is a named collection of categorical columns that form an internal hierarchy via `parent` pointers. Each group has exactly one *root column* (the one with `parent=None`). Cross-group statistical relationships (`declare_orthogonal`, `add_group_dependency`) are only expressed between group root columns — never between non-root (child) columns.

**Why it exists:** Without this constraint, the cross-group dependency graph could become arbitrarily complex (any column could depend on any other column in any other group), making it impossible to guarantee acyclicity or reason about independence. Restricting to roots keeps the cross-group graph small and manageable while still covering realistic scenarios (e.g., patient severity affects payment method, but you don't need department-level payment variation).

**Concrete analogy:** Think of countries and their embassies. Each country (group) has a president (root) and ministers (children). International treaties (cross-group dependencies) are negotiated only between presidents. Ministers inherit the treaty's effects through their own internal chain of command — you don't need every minister talking to every other country's minister.

**Common misunderstanding:** Thinking that `add_group_dependency("department", on=["severity"], ...)` is valid because `department` is a categorical column. It's not — `department` has `parent="hospital"`, making it a non-root, and the SDK should raise a `NonRootDependencyError`. Only `hospital` (the root of the "entity" group) can participate in cross-group dependencies.

**Python implementation hint:** When processing `add_group_dependency()`, immediately check `self._columns[child_root].parent is None` and `all(self._columns[col].parent is None for col in on)`. Raise a descriptive exception on violation. Store the root-level dependency graph separately and validate acyclicity on it.

---

### Concept 4: Intercept + Sum-of-Effects `param_model`

**What it is:** For stochastic measures, each distribution parameter (e.g., μ, σ) is computed as: `θ = intercept + Σ effect_value(predictor_column, current_row_value)`. The `param_model` dict maps parameter names to either a scalar (constant, no effects) or a dict with `"intercept"` and `"effects"` keys. The effects dict maps categorical column names to dicts mapping category values to additive offsets. For a given row, you look up the row's value for each predictor column and sum all the offsets.

**Why it exists:** It provides a compact, declarative way to express how distribution parameters vary by categorical context without requiring the LLM to write sampling code. It's essentially a generalized linear model parameterization — expressive enough for realistic conditional distributions, simple enough to validate against.

**Concrete analogy:** It's like a restaurant bill calculator: base price (intercept) + toppings surcharges (effects). If you order a pizza (intercept = $10) with mushrooms (+$2) at the downtown location (+$1), the price parameter is $13. Each "topping" is an independent additive modifier keyed to a categorical choice.

**Common misunderstanding:** Assuming effects are multiplicative, or that a missing category value in the effects dict means zero effect. The doc states every symbolic effect must have an explicit numeric definition — if `severity` has values `["Mild", "Moderate", "Severe"]` but the effects dict only defines `Mild` and `Moderate`, that's an `UndefinedEffectError` for any row where `severity == "Severe"`.

**Python implementation hint:** Implement a `resolve_param(param_spec, row)` function. If `param_spec` is a number, return it directly. Otherwise, start with `param_spec["intercept"]`, iterate over `param_spec["effects"].items()`, look up `row[col_name]` in the effect dict, and accumulate. Raise an explicit error if a lookup misses.

---

### Concept 5: Two Separate Retry Loops

**What it is:** The system has two distinct retry mechanisms at different stages. The *execution-error feedback loop* (§2.7) handles errors when the LLM's generated script fails to execute at all (syntax errors, cyclic dependencies, undefined effects, non-root dependency violations). The *auto-fix validation loop* (§2.9) handles cases where the script executes successfully and produces a DataFrame, but the data fails statistical or pattern validation checks. The first loop involves the LLM (sends traceback back for repair). The second loop never calls the LLM — it programmatically adjusts parameters (widen variance, amplify magnitudes, reshuffle pairs) and re-runs the deterministic engine.

**Why it exists:** These are fundamentally different failure modes. Execution errors are *semantic bugs in the LLM's code* — only the LLM can fix them (e.g., resolving a cyclic dependency requires restructuring the measure declarations). Validation failures are *statistical drift* — the code is logically correct but the random sample didn't meet tight tolerances, so a deterministic parameter tweak and re-roll suffices.

**Concrete analogy:** Think of a car factory. The execution-error loop is like the design engineer reviewing blueprints that can't be assembled (bolts don't fit the holes) — you need the engineer to redraw. The auto-fix loop is like the quality inspector on the assembly line finding a paint thickness slightly out of spec — the line worker just adjusts the nozzle pressure and resprays, no engineer needed.

**Common misunderstanding:** Nesting one loop inside the other, or using the auto-fix loop's parameter tweaks when the script has a structural error. The two loops are sequential: the execution-error loop runs first to get a valid, runnable script; only then does the auto-fix validation loop run on the script's output.

**Python implementation hint:** Structure as two separate `for attempt in range(max_retries)` loops at different call sites. The outer orchestrator first retries LLM code generation on execution failure (catching exceptions from `exec()`), and only after a successful execution passes `(build_fn, meta)` to `generate_with_validation()` which handles the statistical retry loop internally.

---

# Phase 4 — Verification & Gap Check

## 4a. Ambiguous / Underspecified Design Decisions

1. **Formula evaluation for structural measures** — The doc shows formulas like `"wait_minutes * 12 + severity_surcharge"` as strings but doesn't specify the expression evaluation mechanism. You'll need to decide: safe `eval()` with a restricted namespace? A mini expression parser? `pandas.eval()`? `sympy`? This has security and correctness implications.

2. **`mixture` distribution specification** — Listed as a supported family but no `param_model` example is given. You need to define how a mixture's component distributions, weights, and per-component parameters are specified in the `param_model` dict.

3. **Pattern injection mechanics** — Only `outlier_entity` has a clear implementation (z-score scaling). The doc names six pattern types but only partially specifies implementation for a few. `convergence`, `seasonal_anomaly`, and `dominance_shift` verification/injection logic are left for you to design.

4. **`set_realism()` implementation details** — Missing rate, dirty rate, and censoring are mentioned but mechanisms (MCAR vs. MAR? what constitutes "dirty"? censoring model?) are unspecified.

5. **Cross-group dependency on multiple `on` columns** — The signature is `on=["severity"]` (a list), implying multi-column conditioning is possible, but the example only shows single-column conditioning. How to structure `conditional_weights` for a joint condition (e.g., `on=["severity", "region"]`) is unstated.

6. **Auto-fix parameter propagation** — The `AUTO_FIX` dispatch adjusts parameters, but how those adjusted parameters flow back into the next `build_fn(seed=42+attempt)` call isn't fully specified. Are adjustments applied to the meta dict that `build_fn` reads? Or does `build_fn` itself get patched?

7. **Temporal sampling distribution** — The example shows `Uniform(start, end)` for `visit_date`, but the doc doesn't specify whether this is always uniform or whether temporal columns can have non-uniform sampling (e.g., higher density on weekdays).

8. **`scale` parameter on `add_measure()`** — Listed in the signature but never explained or used in any example.

## 4b. External Dependencies / Libraries / APIs to Identify

- **NumPy** (`np.random.default_rng`, distribution sampling, `np.isfinite`)
- **pandas** (DataFrame construction, `crosstab`, `groupby`, `value_counts`, `query`)
- **SciPy** (`scipy.stats.chi2_contingency` for L1 orthogonality, `scipy.stats.kstest` for L2)
- **A graph library** for DAG construction and topological sort (likely `networkx` or a custom implementation)
- **A safe expression evaluator** for structural measure formulas (needs to be chosen)
- **An LLM API client** (for generating the SDK script and handling the execution-error feedback loop — likely OpenAI/Anthropic/Google Gemini API based on your pipeline)
- **A sandboxed Python executor** for running LLM-generated code safely (e.g., `subprocess`, `RestrictedPython`, Docker, or a code sandbox service)
- **Matching/glob library** for `AUTO_FIX` dispatch pattern matching (`fnmatch` or similar for `"ks_*"`, `"outlier_*"` patterns)

## 4c. Comprehension-Check Questions

**Q1.** Suppose the LLM writes a script that declares `add_measure("cost", family="gaussian", param_model={...})` followed by `add_measure_structural("profit", formula="revenue - cost", ...)`. Later, it also writes `add_measure_structural("revenue", formula="cost * 1.3 + markup", ...)`. What specific error does the system produce, at which stage (execution or validation), and why?

**Q2.** A developer implements the generation engine so that for each row, it generates `payment_method` *before* `severity`. Both are group root columns, but `add_group_dependency("payment_method", on=["severity"], ...)` has been declared. What breaks, and what is the correct way to determine generation order for these two columns?

**Q3.** After `generate()` succeeds, the L2 validator runs a KS test on the `wait_minutes` column and it fails (p < 0.05). The auto-fix loop applies `widen_variance(factor=1.2)` and re-executes. Explain: does the LLM get called again? What changes between retry 1 and retry 2? What happens if all 3 retries fail?



## Prompt:
2026/3/19 11:43:03

Where does this framework design the distribution of data (in the master table and schema) and modify them? If some of the tests in validation fail, it would mean the distribution data is bad, as it should not happen, right?



## Response:
2026/3/19 11:43:46

````plaintext
Thought process: Disentangled distribution specification from post-generation modifications and statistical realities.

Felix is asking a nuanced question about the validation philosophy. Let me think about this carefully.

His question has two parts:
1. Where does the framework design/specify distributions and where does it modify them?
2. If validation fails, does that mean the distribution specifications are bad (i.e., it "shouldn't happen")?

This is actually a subtle point. Let me trace through the framework:

**Where distributions are designed/specified:**
- The LLM writes the SDK script with `param_model` dicts specifying distribution families and parameters
- These are the "declared" distributions — the ground truth specification

**Where distributions get modified:**
- Pattern injection (γ step) deliberately distorts the data post-generation — outliers, trend breaks, etc.


- Realism injection (δ step) adds missing data and corrupts values
- The auto-fix loop then adjusts parameters like variance and magnitude to compensate

**The key insight about validation failures:**
Validation failures don't necessarily mean the distribution spec itself is flawed. They can arise from sampling variance—a finite sample might just fail a KS test by chance even with correct parameters—or from the pattern injection step deliberately introducing anomalies that pull the data away from the declared distribution.

Cross-group dependencies and shared predictors also create marginal distributions that may not perfectly align with the conditional specs in practice. So Felix's concern about structural issues is valid for L1 checks, but L2 and L3 failures are statistically inevitable given finite samples and post-hoc modifications. The auto-fix loop exists because these failures are expected, not because the spec is broken.

The distributions themselves get defined in the LLM's script but then get modified during...

Now I see the distinction: pattern injection changes the actual data after generation, while auto-fix adjusts the parameters themselves and regenerates from scratch. These are two completely different intervention points.
````

Great question — it gets at something subtle about the framework's philosophy. Let me trace both parts.

## Where distributions are specified vs. modified

There are really three distinct sites:

**Site 1 — The LLM's SDK script (specification).** This is where distributions are *designed*. The `param_model` in `add_measure()` and the `formula`/`noise` in `add_measure_structural()` constitute the declared ground truth. At this point, no data exists yet — it's purely a blueprint.

**Site 2 — The deterministic engine's γ step (post-generation modification of *data*).** After steps α and β faithfully sample from the declared distributions, `_inject_patterns()` deliberately *mutates the DataFrame*. An `outlier_entity` pattern scales up values for a filtered subset; a `trend_break` shifts the mean after a breakpoint. This is intentional distortion — the spec said "LogNormal(μ, σ)" but pattern injection then pushes certain rows away from that distribution on purpose.

**Site 3 — The auto-fix loop (modification of *parameters*).** When validation fails, `widen_variance(factor=1.2)` or `amplify_magnitude(factor=1.3)` adjusts the generation parameters and re-rolls. This modifies the specification itself to make the next sample more likely to pass.

## Why validation failures are not necessarily "bad data"

Your intuition is right for **L1 (structural)** — those failures genuinely *should not happen* if the engine is implemented correctly. If row count is wrong or cardinality doesn't match, that's a bug. These are deterministic properties.

But for **L2 (statistical) and L3 (pattern)**, failures are *expected to occur sometimes*, for two reasons:

**Reason 1 — Finite sampling variance.** The framework generates only 200–3,000 rows. A KS test on `wait_minutes` compares the empirical distribution against the declared LogNormal. Even when the sampling code is perfectly correct, a finite sample can fail a KS test at p < 0.05 purely by chance — that's literally what the 5% false-rejection rate of the test means. The spec is fine, the sample just got unlucky. The auto-fix response (widen variance, re-roll with a new seed) is exactly the right reaction: nudge the parameters slightly to give the test more room, and try again.

**Reason 2 — Pattern injection creates deliberate spec violations.** This is the more interesting one. Step β generates `wait_minutes` faithfully from LogNormal(μ, σ). Then step γ comes along and scales up all `wait_minutes` values where `hospital == 'Xiehe' & severity == 'Severe'` by a z-score of 3.0. Now the overall distribution of `wait_minutes` no longer matches the declared LogNormal — *by design*. The L3 validator checks that the pattern *is* present (z ≥ 2.0), but the L2 validator might simultaneously flag that the KS test fails because the injected outliers distorted the distribution tail.

So there's an inherent tension in the design:

```
L2 says: "wait_minutes doesn't match its declared LogNormal"  ← true
L3 says: "the outlier pattern is successfully present"         ← also true
Both are correct — they're measuring different things.
```

The auto-fix loop resolves this pragmatically rather than analytically: widen the variance slightly so the LogNormal's tails are fat enough to "absorb" the injected outliers, re-generate, and check again. It's a heuristic convergence strategy, not a proof of correctness.

## The mental model to carry into implementation

Think of it in three layers of "truth":

1. **Declared truth** — what the LLM specified (the param_model, the formula)
2. **Generated truth** — what the engine sampled (faithful to declared truth)
3. **Final truth** — what exists after pattern + realism injection (deliberately deviates from declared truth)

Validation compares **final truth** against **declared truth**, knowing they won't perfectly agree. The tolerances (p > 0.05, deviation < 0.10, z ≥ 2.0) are chosen to accept reasonable deviations while catching egregious failures. And the auto-fix loop is a safety net for cases where finite sampling or pattern injection pushed things just past those tolerances — not evidence that something is fundamentally wrong with the spec.

Does this clarify the relationship, or do you want to dig into how the auto-fix parameter adjustments actually propagate back into the regeneration step? That part of the doc is one of the gaps I flagged — it's underspecified.





---
Powered by [Claude Exporter](https://www.ai-chat-exporter.net)