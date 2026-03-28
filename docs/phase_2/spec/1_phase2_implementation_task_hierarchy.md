# Phase 2: Agentic Data Simulator — Implementation Task Hierarchy

**Patch version:** v2 — Post-Audit (2026-03-20)

---

## 1. `FactTableSimulator` Core SDK Class — §2.1, §2.8

The top-level orchestrator class that holds all declarations, builds the DAG, and exposes `generate()`.

### 1.1 Class Skeleton & Constructor

#### 1.1.1 `__init__(self, target_rows, seed)` constructor
- **Section:** §2.8 code block (`FactTableSimulator.generate()`) and §2.5 one-shot example (`FactTableSimulator(target_rows=500, seed=42)`)
- **Input:** `target_rows: int`, `seed: int`
- **Output:** Initialized instance with empty registries for columns, groups, relationships, patterns, realism config; stored `seed` and `target_rows`.
- **Done:** `sim = FactTableSimulator(target_rows=500, seed=42)` succeeds; `sim.target_rows == 500`; `sim.seed == 42`; all internal registries are empty collections.

#### 1.1.2 Internal registry data structures
- **Section:** §2.1.1 (all `add_*` methods imply storage), §2.2 (dimension groups), §2.6 (schema metadata output requires all of these to be queryable)
- **Input:** N/A (design-time decision)
- **Output:** Defined attributes: `_columns: OrderedDict`, `_groups: dict[str, GroupDef]`, `_orthogonal_pairs: list`, `_group_dependencies: list`, `_patterns: list`, `_realism_config: Optional[dict]`, `_measure_dag: dict`.
- **Done:** All registries exist after `__init__`; each is typed and empty; no `AttributeError` on access.

#### 1.1.3 `generate()` public API return type contract
- **Section:** §2.8 code: `def generate(self) -> Tuple[pd.DataFrame, dict]`
- **Input:** A fully configured `FactTableSimulator` instance.
- **Output:** `Tuple[pd.DataFrame, dict]` — the first element is the Master DataFrame, the second is the schema metadata dict (per §2.6).
- **Done:** `result = sim.generate()` returns a 2-tuple; `isinstance(result[0], pd.DataFrame)` is `True`; `isinstance(result[1], dict)` is `True`; `result[1]` contains at minimum the keys defined in §2.6 (`dimension_groups`, `columns`, `measure_dag_order`, `patterns`, `total_rows`).
- **Added by:** coverage_4_generate_contract

---

### 1.2 `add_category()` — §2.1.1, §2.2

#### 1.2.1 Signature & parameter validation
- **Spec status:** NEEDS_CLARIFICATION — duplicate column name rejection is inferred from DAG semantics, not explicitly stated in §2.1.1.
- **Section:** §2.1.1 paragraph 1 signature: `add_category(name, values, weights, group, parent=None)`
- **Input:** `name: str`, `values: list[str]`, `weights: list[float] | dict[str, list[float]]`, `group: str`, `parent: Optional[str]`
- **Output:** Raises `ValueError` for: empty `values`, `len(values) != len(weights)` (flat case). Duplicate column `name` handling requires spec clarification (currently assumed to raise `ValueError`).
- **Done:** `add_category("x", values=[], weights=[], group="g")` raises `ValueError("empty values")`; `add_category("x", values=["a"], weights=[0.5, 0.5], group="g")` raises length-mismatch error.

#### 1.2.2 Weight auto-normalization
- **Section:** §2.1.1 last line before `add_temporal`: "Auto-normalized"
- **Input:** `weights=[1, 2, 3]`
- **Output:** Stored weights sum to 1.0: `[1/6, 2/6, 3/6]`.
- **Done:** After `add_category("c", ["a","b","c"], [1,2,3], "g")`, internal stored weights `pytest.approx([1/6, 1/3, 1/2])`.

#### 1.2.3 Per-parent conditional weights (dict form)
- **Section:** §2.1.1 code block with `weights={"Xiehe": [...], "Huashan": [...]}` and §2.2 paragraph "Within-group hierarchy"
- **Input:** `weights` as `dict[str, list[float]]` where each key is a parent value.
- **Output:** Stored per-parent weight vectors; each vector auto-normalized independently; raises `ValueError` if any parent key is not a value of the declared parent column; raises `ValueError` if any vector length ≠ `len(values)`.
- **Done:** Passing `weights={"Xiehe": [1,1,1,1]}` when parent col `hospital` has value `"Xiehe"` succeeds and normalizes to `[0.25]*4`; passing `weights={"UNKNOWN": [1,1]}` raises `ValueError`.

#### 1.2.4 Parent existence & same-group validation
- **Section:** §2.1.1 final line: "validates parent exists in same group"
- **Input:** `parent="hospital"` when `hospital` was declared in group `"entity"`.
- **Output:** Succeeds if parent column exists and belongs to same `group`; raises `ValueError` otherwise.
- **Done:** `add_category("dept", ..., group="entity", parent="hospital")` succeeds after `hospital` is in group `"entity"`; `add_category("dept", ..., group="OTHER", parent="hospital")` raises `ValueError`.

#### 1.2.5 Group registry update
- **Section:** §2.2 — "Each categorical column belongs to exactly one named group."
- **Input:** A valid `add_category` call.
- **Output:** `_groups[group]` is created or updated; column appended to group's column list; if `parent is None`, column is recorded as group root.
- **Done:** After adding `hospital` (root) and `department` (child), `_groups["entity"].root == "hospital"` and `_groups["entity"].columns == ["hospital", "department"]`.

#### 1.2.6 Reject duplicate group root
- **Spec status:** NEEDS_CLARIFICATION — §2.2 states "each group has **a** root column" (singular), strongly implying uniqueness, but no explicit rejection rule is stated.
- **Section:** §2.2 — "Each group has a root column (no parent)."
- **Input:** Two `add_category` calls to same group both with `parent=None`.
- **Output:** Raises `ValueError` — a group cannot have two roots (assumed behavior pending clarification).
- **Done:** Second root-level `add_category` into same group raises.

---

### 1.3 `add_temporal()` — §2.1.1, §2.2

#### 1.3.1 Signature & date parsing
- **Section:** §2.1.1 `add_temporal(name, start, end, freq, derive=[])`
- **Input:** `name: str`, `start/end: str` (ISO-8601 dates), `freq: str`, `derive: list[str]`
- **Output:** Parsed `start`/`end` as `datetime`; raises `ValueError` if `end <= start` or unparseable dates.
- **Done:** `add_temporal("d", "2024-01-01", "2024-06-30", "daily")` stores parsed datetimes; `add_temporal("d", "2024-06-30", "2024-01-01", "daily")` raises.

#### 1.3.2 Frequency storage
- **Section:** §2.1.1 example uses `freq="daily"`; §2.5 prompt references "temporal grain"
- **Input:** `freq` string.
- **Output:** Stored as-is. The spec does not define a frequency whitelist — only `"daily"` is demonstrated. Non-daily frequencies are accepted for storage but may not be supported by the generation engine (see §4.1.4).
- **Done:** `freq="daily"` stored; any non-empty string stored without error at declaration time.

#### 1.3.3 Derive whitelist validation
- **Section:** §2.1.1 — "Derived columns (day_of_week, month, quarter, is_weekend)"
- **Input:** `derive=["day_of_week", "month"]`
- **Output:** Only whitelisted tokens accepted. Raises `ValueError` for unknown derivation.
- **Done:** `derive=["quarter", "is_weekend"]` accepted; `derive=["fiscal_year"]` raises.

#### 1.3.4 Temporal group registration
- **Section:** §2.2 — "Temporal as dimension group: root is the declared temporal column; derived calendar levels are automatically extracted"
- **Input:** A valid `add_temporal` call.
- **Output:** A new dimension group (named `"time"` or user-specified) created; temporal column is root; derived columns registered as group members (`columns`) with a DAG dependency on the root (`parent`), but **not** listed in `hierarchy` (§2.6: hierarchy is root-only for the temporal group).
- **Done:** `_groups["time"].root == "visit_date"` and `"day_of_week" in _groups["time"].columns`.

---

### 1.4 `add_measure()` (Stochastic Root) — §2.1.1, §2.3

#### 1.4.1 Signature & family validation
- **Section:** §2.1.1 `add_measure(name, family, param_model, scale=None)`; §2.1.1 supported distributions list.
- **Input:** `family: str` from `{"gaussian", "lognormal", "gamma", "beta", "uniform", "poisson", "exponential", "mixture"}`.
- **Output:** Raises `ValueError` for unsupported family string.
- **Done:** `family="lognormal"` accepted; `family="weibull"` raises.

#### 1.4.2 `param_model` constant-parameter form
- **Spec status:** Implementation Design Choice — the canonical internal representation (intercept-only model) is not specified by the spec. The spec shows only the external dict format; internal storage is an implementation decision.
- **Section:** §2.1.1 "Simple: constant parameters" code block: `param_model={"mu": 36.5, "sigma": 0.8}`
- **Input:** Dict where each value is a scalar float.
- **Output:** Stored internally (representation is an implementation choice).
- **Done:** After adding, the measure's param spec is queryable and produces correct parameter values when resolved against any categorical context.

#### 1.4.3 `param_model` intercept+effects form
- **Section:** §2.1.1 "Full: parameters vary by categorical predictors" code block; §2.3 equation θⱼ = β₀ + Σₘ βₘ(Xₘ)
- **Input:** Dict where values are `{"intercept": float, "effects": {col_name: {val: float, ...}}}`.
- **Output:** Validated that every referenced column (`severity`, `hospital`) has been declared as a categorical; every effect key matches a declared value of that column.
- **Done:** Referencing undeclared column `"region"` in effects raises `ValueError("Unknown predictor column: region")`; referencing value `"Critical"` for `severity` when `severity.values = ["Mild","Moderate","Severe"]` raises.

#### 1.4.4 Mixture family sub-spec
- **Section:** §2.1.1 supported distributions includes `"mixture"`.
- **Input:** `family="mixture"` with `param_model` containing component specs.
- **Output:** Parsed and stored. (Spec does not detail mixture schema — implementation must define sub-component format.)
- **Done:** A mixture of two Gaussians can be declared and stored without error.

#### 1.4.5 Register as DAG root node
- **Section:** §2.1.1 table: "DAG role: Root (no incoming measure edges)"; §2.3 "Measure DAG Constraint"
- **Input:** A valid `add_measure` call.
- **Output:** Measure added to `_measure_dag` as a node with no incoming edges.
- **Done:** `_measure_dag` contains `"wait_minutes"` with `in_edges == []`.

---

### 1.5 `add_measure_structural()` (Derived) — §2.1.1, §2.3

#### 1.5.1 Signature validation
- **Section:** §2.1.1 `add_measure_structural(name, formula, effects={}, noise={})`
- **Input:** `name: str`, `formula: str`, `effects: dict`, `noise: dict`.
- **Output:** Stored structural measure definition with all fields (formula, effects, noise) preserved and queryable.
- **Done:** After `add_measure_structural("cost", formula="wait_minutes * 12 + severity_surcharge", effects={...}, noise={...})`: the internal registry contains an entry for `"cost"` with the original formula string, the effects dict, and the noise spec all retrievable; `"cost"` appears in `_columns`.

#### 1.5.2 Formula symbol resolution & DAG edge creation
- **Section:** §2.1.1 — "The formula references previously declared measure columns by name"; §2.3 — "Structural measures may only reference measures declared before them"
- **Input:** `formula="wait_minutes * 12 + severity_surcharge"`
- **Output:** Parse formula; identify all symbols; each symbol must resolve to either a declared measure column or a key in `effects`. Creates DAG edges from referenced measures → this measure. Raises `ValueError` for undefined symbols.
- **Done:** Formula referencing undeclared measure `"temperature"` raises `ValueError("Undefined symbol: temperature")`; formula referencing `"wait_minutes"` (already declared) creates edge `wait_minutes → cost`.

#### 1.5.3 Effects dictionary validation
- **Section:** §2.1.1 code block: `effects={"severity_surcharge": {"Mild": 50, ...}}`
- **Input:** `effects` dict mapping effect names to `{categorical_value: numeric}`.
- **Output:** Each effect name must appear in `formula`; the keys of the inner dict must match the values of some declared categorical column. Raises if not.
- **Done:** Effect `"severity_surcharge"` with keys `["Mild","Moderate","Severe"]` validated against column `severity`; missing key `"Severe"` raises.

#### 1.5.4 Noise spec validation
- **Section:** §2.1.1 code block: `noise={"family": "gaussian", "sigma": 30}`
- **Input:** `noise` dict with `family` and distribution-specific params.
- **Output:** `family` validated against supported distributions; required params for that family checked.
- **Done:** `noise={"family": "gaussian", "sigma": 30}` accepted; `noise={"family": "gaussian"}` (missing sigma) raises.

#### 1.5.5 Cycle detection on measure DAG
- **Section:** §2.3 — "All measure dependencies must form a DAG"; §2.5 constraint 7
- **Input:** New structural measure whose formula references create a cycle.
- **Output:** Raises `CyclicDependencyError`.
- **Done:** If `A → B` exists and new measure `B → A` is attempted, raises `CyclicDependencyError`.

---

### 1.6 `declare_orthogonal()` — §2.1.2, §2.2

#### 1.6.1 Signature & group existence validation
- **Section:** §2.1.2 `declare_orthogonal(group_a, group_b, rationale)`
- **Input:** `group_a: str`, `group_b: str`, `rationale: str`.
- **Output:** Raises `ValueError` if either group has not been populated by at least one `add_category`. Raises if same group declared orthogonal to itself.
- **Done:** `declare_orthogonal("entity", "NONEXISTENT", "...")` raises.

#### 1.6.2 Store orthogonal pair
- **Section:** §2.2 — "Independence is declared between entire groups"
- **Input:** Valid group pair.
- **Output:** Pair stored in `_orthogonal_pairs`; order-independent (A,B == B,A).
- **Done:** After declaration, `("entity","patient")` in orthogonal pairs regardless of argument order.

#### 1.6.3 Conflict check with `add_group_dependency`
- **Spec status:** NEEDS_CLARIFICATION — mutual exclusion of orthogonal and dependent declarations for the same group pair is inferred from semantics, not explicitly stated in §2.1.2 or §2.2.
- **Section:** §2.2 — orthogonal vs dependent are mutually exclusive for a pair (inferred).
- **Input:** Declaring orthogonal on a pair that already has a group dependency.
- **Output:** Raises `ValueError` — cannot be both orthogonal and dependent (assumed behavior pending clarification).
- **Done:** After `add_group_dependency("payment_method", on=["severity"], ...)`, calling `declare_orthogonal("payment","patient",...)` raises.

---

### 1.7 `add_group_dependency()` — §2.1.2, §2.2

#### 1.7.1 Signature & root-only constraint
- **Section:** §2.1.2 `add_group_dependency(child_root, on, conditional_weights)`; §2.2 "Root-only constraint"
- **Input:** `child_root: str`, `on: list[str]`, `conditional_weights: dict`.
- **Output:** Raises `NonRootDependencyError` if `child_root` or any `on` column is not a group root.
- **Done:** `add_group_dependency("department", on=["severity"], ...)` raises because `department` is not a root.

#### 1.7.2 Conditional weights validation
- **Section:** §2.1.2 code block — keys are parent-column values, inner dict keys are child-column values.
- **Input:** `conditional_weights` dict.
- **Output:** Every outer key must be a value of the `on` column; every inner key must be a value of `child_root` column; inner weights auto-normalized per row. Raises on mismatch.
- **Done:** Missing outer key `"Severe"` raises; inner dict missing value `"Government"` raises.

#### 1.7.3 Root-level DAG acyclicity check
- **Section:** §2.2 — "root-level dependency graph must be a DAG"
- **Input:** New dependency edge.
- **Output:** Raises `CyclicDependencyError` if adding this edge creates a cycle in the root-level dependency DAG.
- **Done:** If `A` depends on `B` and then `B` depends on `A` is attempted, raises.

#### 1.7.4 Conflict check with orthogonal declarations
- **Spec status:** NEEDS_CLARIFICATION — inverse of §1.6.3; mutual exclusion is inferred from semantics, not explicitly stated.
- **Section:** Implied inverse of §1.6.3.
- **Input:** Adding dependency between groups already declared orthogonal.
- **Output:** Raises `ValueError` (assumed behavior pending clarification).
- **Done:** After `declare_orthogonal("payment","patient",...)`, calling `add_group_dependency("payment_method", on=["severity"], ...)` raises.

---

### 1.8 `inject_pattern()` — §2.1.2

#### 1.8.1 Signature & type validation
- **Section:** §2.1.2 `inject_pattern(type, target, col, params)`; pattern types list.
- **Input:** `type: str` from `{"outlier_entity", "trend_break", "ranking_reversal", "dominance_shift", "convergence", "seasonal_anomaly"}`.
- **Output:** Raises `ValueError` for unknown type.
- **Done:** `type="outlier_entity"` accepted; `type="unknown_pattern"` raises.

#### 1.8.2 Target expression storage
- **Section:** §2.1.2 code block: `target="hospital == 'Xiehe' & severity == 'Severe'"`
- **Input:** `target` string.
- **Output:** Stored as-is for later execution during Phase γ injection and L3 validation. No declaration-time parsing or column validation is performed — the spec does not define a target-expression grammar, and validation occurs implicitly at execution time via `df.query(target)`.
- **Done:** Any non-empty target string is accepted and stored.

#### 1.8.3 Column validation
- **Section:** §2.1.2 code block: `col="wait_minutes"`
- **Input:** `col` string.
- **Output:** Must reference a declared measure column. Raises otherwise.
- **Done:** `col="nonexistent_col"` raises.

#### 1.8.4 Pattern-type-specific param validation
- **Section:** §2.1.2 examples: `outlier_entity` needs `z_score`; `trend_break` needs `break_point` and `magnitude`.
- **Input:** `params` dict.
- **Output:** Validates required keys for the two fully specified pattern types only: `outlier_entity` requires `z_score`; `trend_break` requires `break_point` and `magnitude`. The remaining four types (`ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`) have no spec-defined `params` schema — their params are stored as-is without key validation.
- **Done:** `inject_pattern("trend_break", ..., params={"z_score": 3})` raises because `break_point` and `magnitude` are required; `inject_pattern("convergence", ..., params={"anything": 1})` stores without error.

#### 1.8.5 Store pattern
- **Section:** §2.1.2 — patterns are stored for later injection in §2.8 step γ.
- **Input:** Valid pattern spec.
- **Output:** Appended to `_patterns` list.
- **Done:** `len(sim._patterns)` increments by 1.

---

### 1.9 `set_realism()` — §2.1.2

#### 1.9.1 Signature & validation
- **Section:** §2.1.2 `set_realism(missing_rate, dirty_rate, censoring=None)`
- **Input:** `missing_rate: float`, `dirty_rate: float`, `censoring: Optional[dict]`.
- **Output:** Rates validated as ∈ [0, 1]. Stored in `_realism_config`.
- **Done:** `set_realism(0.05, 0.02)` stores config; `set_realism(1.5, 0.0)` raises.

---

## 2. Dimension Group Model — §2.2

Internal data structures representing groups, hierarchies, and cross-group relations.

### 2.1 `DimensionGroup` data class

#### 2.1.1 Define `DimensionGroup`
- **Spec status:** Implementation Design Choice — the specific class structure (dataclass, namedtuple, plain dict) is not prescribed by the spec. The semantic fields are derived from §2.2 and anchored to the §2.6 metadata output format.
- **Section:** §2.2 entire section; §2.6 metadata `dimension_groups` key.
- **Input:** N/A (data class definition).
- **Output:** Fields: `name: str`, `root: str`, `columns: list[str]`, `hierarchy: list[str]` (root-first ordering).
- **Done:** Instantiable; `group.root` returns root column name; `group.hierarchy` returns ordered list; serialization to `{"columns": [...], "hierarchy": [...]}` matches the §2.6 metadata structure.

### 2.2 Cross-group relation stores

#### 2.2.1 `OrthogonalPair` data class
- **Spec status:** Implementation Design Choice — class vs. tuple vs. dict is an implementation decision. Semantic fields are specified.
- **Section:** §2.2 — "orthogonal declarations"
- **Input:** N/A.
- **Output:** Fields: `group_a: str`, `group_b: str`, `rationale: str`. Equality is order-independent.
- **Done:** `OrthogonalPair("a","b","r") == OrthogonalPair("b","a","r")`.

#### 2.2.2 `GroupDependency` data class
- **Spec status:** Implementation Design Choice — class vs. tuple vs. dict is an implementation decision. Semantic fields are specified.
- **Section:** §2.2 — "Cross-group dependency"
- **Input:** N/A.
- **Output:** Fields: `child_root: str`, `on: list[str]`, `conditional_weights: dict`.
- **Done:** Instantiable and serializable to the §2.6 metadata format.

---

## 3. DAG Construction & Topological Sort — §2.4, §2.3

### 3.1 Full generation DAG builder

#### 3.1.1 `_build_full_dag()` — merge all column types into one DAG
- **Spec status:** Implementation Design Choice — the spec requires a DAG structure but does not prescribe a specific library (e.g., `networkx.DiGraph` is one option, not a requirement). Any directed graph representation that supports topological sort is acceptable.
- **Section:** §2.4 "All columns — categorical, temporal, and measure — form a single DAG"; §2.8 code: `full_dag = self._build_full_dag()`
- **Input:** All registered columns, group hierarchies, group dependencies, temporal derivations, measure DAG edges.
- **Output:** A directed graph containing every declared column as a node and every dependency as a directed edge.
- **Done:** For the one-shot example, the graph has nodes `{hospital, department, severity, payment_method, visit_date, day_of_week, month, wait_minutes, cost, satisfaction}` and edges matching §2.4 diagram.

#### 3.1.2 `topological_sort()` — compute generation order
- **Section:** §2.4 "The engine generates columns in topological order"; §2.8 `topo_order = topological_sort(full_dag)`
- **Input:** A DAG (from 3.1.1).
- **Output:** A list of column names in valid topological order. Raises `CyclicDependencyError` if cycle detected.
- **Done:** For the one-shot example, `hospital` appears before `department`; `wait_minutes` appears before `cost` and `satisfaction`.

### 3.2 Measure sub-DAG extraction

#### 3.2.1 Extract measure-only sub-DAG
- **Section:** §2.3 "Measure DAG Constraint"; §2.4 Step 2 "Generate measures (topological order of measure DAG)"
- **Input:** Full DAG, list of measure column names.
- **Output:** Sub-graph containing only measure nodes and measure→measure edges; its own topological order.
- **Done:** For the example, order is `[wait_minutes, cost, satisfaction]` matching §2.6 `measure_dag_order`.

---

## 4. Deterministic Engine (`generate()`) — §2.8

### 4.1 Phase α — Skeleton builder (`_build_skeleton`)

#### 4.1.1 Sample independent categorical roots
- **Section:** §2.4 Row Generation Algorithm Step 1 lines 1–3: roots sampled from `Cat(weights)`.
- **Input:** Root categorical columns, their weights, `target_rows`, `rng`.
- **Output:** Numpy array of length `target_rows` for each root column, sampled per declared marginal weights.
- **Done:** For `hospital` with `weights=[0.25,0.20,0.20,0.20,0.15]`, after 10,000 rows, observed frequencies within ±0.03 of declared weights (statistical test).

#### 4.1.2 Sample cross-group dependent roots
- **Section:** §2.4 Step 1 line 4: `payment_method_i ~ Cat(weights[severity_i])`.
- **Input:** Root column, its `GroupDependency` spec, already-sampled parent root column values, `rng`.
- **Output:** Array sampled row-by-row from conditional weights conditioned on the parent root's realized value.
- **Done:** For rows where `severity == "Severe"`, `payment_method` distribution approximately matches `{"Insurance":0.80, "Self-pay":0.10, "Government":0.10}`.

#### 4.1.3 Sample within-group child categories
- **Section:** §2.4 Step 1 line 5: `department_i ~ Cat(weights | hospital_i)`.
- **Input:** Child column, parent column values, per-parent or flat weights, `rng`.
- **Output:** Array sampled conditionally on parent.
- **Done:** For flat weights, marginal distribution of child matches declared weights regardless of parent.

#### 4.1.4 Sample temporal root
- **Section:** §2.4 Step 1 line 3: `visit_date_i ~ Uniform(start, end)`.
- **Input:** Temporal column spec (start, end, freq), `target_rows`, `rng`.
- **Output:** Array of datetime values within `[start, end]`.
- **Done:** All dates ≥ `start` and ≤ `end`; for `freq="daily"`, dates are date-only (no sub-day precision).

#### 4.1.5 Derive temporal features
- **Section:** §2.4 Step 1 lines 6–7: `day_of_week = DOW(visit_date)`.
- **Input:** Temporal root array, `derive` list.
- **Output:** One array per derived column. `day_of_week` ∈ {0..6} or named days; `month` ∈ {1..12}; `quarter` ∈ {1..4}; `is_weekend` ∈ {True, False}.
- **Done:** `day_of_week` for `2024-01-01` (Monday) == correct weekday value.

### 4.2 Phase β — Measure generation

#### 4.2.1 Stochastic parameter resolution
- **Section:** §2.3 "Stochastic Root Measure" formula: θⱼ = β₀ + Σₘ βₘ(Xₘ)
- **Input:** Measure spec `param_model`, all previously generated categorical columns in `rows`.
- **Output:** For each row, compute context-dependent parameter values by applying intercept + effects for every distribution parameter.
- **Done:** For `wait_minutes` with `severity="Severe"`, `hospital="Xiehe"`: μ = 2.8+0.9+0.2 = 3.9, σ = 0.35+0.10 = 0.45. Per-row parameter arrays have correct values for each categorical context.
- **Split from:** original 4.2.1 (granularity_4.2.1)

#### 4.2.2 Stochastic family-specific parameter domain validation
- **Section:** §2.3 — distribution parameters must be valid for the chosen family.
- **Input:** Resolved per-row parameter values, `family` string.
- **Output:** Validates that computed parameters fall within valid domains for the family (e.g., σ > 0 for gaussian/lognormal, shape > 0 for gamma). Raises descriptive error if any row produces an invalid parameter.
- **Done:** Computed σ = −0.15 for a specific predictor cell raises; all-positive σ values pass.
- **Split from:** original 4.2.1 (granularity_4.2.1)

#### 4.2.3 Stochastic sampling dispatch
- **Section:** §2.8 code block: `self._sample_stochastic(col, rows, rng)`.
- **Input:** Validated per-row parameters, `family` string, `rng`.
- **Output:** Numpy array of length `target_rows`, each element sampled from the declared family with its row-specific parameters.
- **Done:** Sampled values for `LogNormal(3.9, 0.45)` rows have `mean(log(x))` ≈ 3.9 ± tolerance.
- **Split from:** original 4.2.1 (granularity_4.2.1)

#### 4.2.4 Distribution dispatch table
- **Section:** §2.1.1 supported distributions list.
- **Input:** `family` string and computed params.
- **Output:** Correct `numpy.random.Generator` method call for each of the 8 supported families.
- **Done:** Each of `gaussian`, `lognormal`, `gamma`, `beta`, `uniform`, `poisson`, `exponential`, `mixture` dispatches to the correct sampling function; unknown family raises `ValueError`.

#### 4.2.5 Structural formula evaluation
- **Section:** §2.3 "Structural (Derived) Measure"; §2.1.1 — "Every symbol must have an explicit numeric definition"
- **Input:** Formula string, all upstream measure columns in `rows`.
- **Output:** Numpy array of the deterministic formula component, with all measure-name symbols resolved to their column arrays.
- **Done:** For formula `"wait_minutes * 12 + severity_surcharge"`, the measure-symbol portion `wait_minutes * 12` evaluates correctly for each row.
- **Split from:** original 4.2.3 (granularity_4.2.3)

#### 4.2.6 Structural effect materialization
- **Section:** §2.1.1 code block: `effects={"severity_surcharge": {"Mild": 50, ...}}`
- **Input:** Effects dict, categorical column arrays from `rows`.
- **Output:** For each effect name in the formula, produces a numpy array mapping each row's categorical value to its numeric effect value.
- **Done:** Rows with `severity="Severe"` get `severity_surcharge=500`; rows with `severity="Mild"` get `50`.
- **Split from:** original 4.2.3 (granularity_4.2.3)

#### 4.2.7 Structural noise sampling
- **Section:** §2.1.1 code block: `noise={"family": "gaussian", "sigma": 30}`
- **Input:** Noise spec dict, `rng`.
- **Output:** Numpy array of noise values sampled from the declared noise distribution.
- **Done:** For `noise={"family": "gaussian", "sigma": 30}`, sampled noise has `std ≈ 30 ± tolerance`.
- **Split from:** original 4.2.3 (granularity_4.2.3)

#### 4.2.8 `eval_formula()` safe expression evaluator
- **Section:** §2.1.1 — "Every symbol must have an explicit numeric definition"
- **Input:** Formula string, row data dict, effects dict.
- **Output:** Numpy array of evaluated formula results. Must be sandboxed (no `exec`/`eval` on arbitrary code); only arithmetic operators and declared symbols allowed.
- **Done:** `eval_formula("a * 12 + b", {"a": np.array([1,2]), "b": np.array([3,4])})` returns `[15, 28]`; formula `"import os"` raises.

### 4.3 Phase γ — Pattern injection (`_inject_patterns`)

#### 4.3.1 Outlier entity injection
- **Section:** §2.1.2 `outlier_entity` example; §2.9 L3 validation code for `outlier_entity`.
- **Input:** DataFrame, pattern spec with `target`, `col`, `params.z_score`.
- **Output:** Rows matching `target` filter have `col` values shifted so that `|group_mean - global_mean| / global_std >= z_score`.
- **Done:** After injection, the z-score of the target subset's mean is ≥ `params.z_score`.

#### 4.3.2 Trend break injection
- **Section:** §2.1.2 `trend_break` example; §2.9 L3 code for `trend_break`.
- **Input:** DataFrame, pattern spec with `target`, `col`, `params.break_point`, `params.magnitude`.
- **Output:** Rows matching `target` AND after `break_point` have `col` scaled by `(1 + magnitude)` or equivalent shift.
- **Done:** `|mean_after - mean_before| / mean_before > 0.15` (per L3 check).

#### 4.3.3 Ranking reversal injection
- **Section:** §2.9 L3 code for `ranking_reversal`.
- **Input:** DataFrame, pattern spec with `metrics: [m1, m2]`.
- **Output:** Grouped by root entity, rank correlation of `m1` and `m2` becomes negative.
- **Done:** `means[m1].rank().corr(means[m2].rank()) < 0`.

#### 4.3.4 Dominance shift injection
- **Section:** §2.9 L3 code — delegates to `_verify_dominance_change`.
- **Input:** DataFrame, pattern spec.
- **Output:** The dominant category in `col` changes between time periods.
- **Done:** L3 `_verify_dominance_change` returns `True`.

#### 4.3.5 Convergence injection
- **Section:** §2.1.2 pattern types list: `"convergence"`.
- **Input:** DataFrame, pattern spec.
- **Output:** Variance of `col` across categories decreases over time.
- **Done:** Late-period inter-group variance < early-period inter-group variance.

#### 4.3.6 Seasonal anomaly injection
- **Section:** §2.1.2 pattern types list: `"seasonal_anomaly"`.
- **Input:** DataFrame, pattern spec.
- **Output:** Specific seasonal period has anomalous mean for `col`.
- **Done:** Seasonal subset mean deviates significantly from overall mean.

### 4.4 Phase δ — Realism injection (`_inject_realism`)

#### 4.4.1 Missing value injection
- **Section:** §2.1.2 `set_realism(missing_rate, dirty_rate, censoring)`; §2.8 code block.
- **Input:** DataFrame, `missing_rate` float.
- **Output:** Approximately `missing_rate` fraction of cells set to `NaN`, distributed across eligible columns.
- **Done:** `df.isna().sum().sum() / df.size` ≈ `missing_rate` ± tolerance.

#### 4.4.2 Dirty value injection
- **Section:** §2.1.2 `dirty_rate`.
- **Input:** DataFrame, `dirty_rate` float.
- **Output:** Approximately `dirty_rate` fraction of categorical cells replaced with typos/variants.
- **Done:** Dirty values detectable (not in original `values` list) at approximately the declared rate.

#### 4.4.3 Censoring injection
- **Section:** §2.1.2 `censoring` parameter.
- **Input:** DataFrame, `censoring` dict.
- **Output:** Measure values clipped or flagged per censoring rules.
- **Done:** No measure values exceed censoring bounds.

### 4.5 Post-processing (`_post_process`)

#### 4.5.1 DataFrame assembly & dtype casting
- **Spec status:** Implementation Design Choice — the spec does not prescribe pandas dtypes. The requirement is a correct `pd.DataFrame`; specific dtype policies (e.g., `category` vs. `object`, `datetime64[ns]` vs. `datetime64[s]`) are implementation decisions.
- **Section:** §2.8 `return self._post_process(rows), self._build_schema_metadata()`
- **Input:** `rows` dict of column arrays.
- **Output:** `pd.DataFrame` with appropriate dtypes for each column type.
- **Done:** Result is a valid `pd.DataFrame`; categorical columns have string-typed values; temporal columns are datetime-compatible; measure columns are numeric.

### 4.6 Determinism verification

#### 4.6.1 Bit-for-bit reproducibility with same seed
- **Section:** §2.8 — "Given the same `seed`, output is bit-for-bit reproducible."
- **Input:** A configured `FactTableSimulator` instance, called with `generate()` twice using the same seed.
- **Output:** Both calls produce identical DataFrames (element-wise equality for all columns, all rows).
- **Done:** `df1 = sim.generate(seed=42)[0]`; `df2 = sim.generate(seed=42)[0]`; `df1.equals(df2)` is `True`.
- **Added by:** coverage_3_reproducibility

---

## 5. Schema Metadata Builder — §2.6

### 5.1 `_build_schema_metadata()`

#### 5.1.1 Emit `dimension_groups` block
- **Section:** §2.6 JSON `"dimension_groups"` key.
- **Input:** Internal `_groups` registry.
- **Output:** Dict mapping group name → `{"columns": [...], "hierarchy": [...]}`.
- **Done:** Output matches §2.6 example structure for the one-shot scenario.

#### 5.1.2 Emit `orthogonal_groups` block
- **Section:** §2.6 JSON `"orthogonal_groups"` key.
- **Input:** `_orthogonal_pairs`.
- **Output:** List of `{"group_a": ..., "group_b": ..., "rationale": ...}`.
- **Done:** Serialization round-trips correctly.

#### 5.1.3 Emit `group_dependencies` block
- **Section:** §2.6 JSON `"group_dependencies"` key.
- **Input:** `_group_dependencies`.
- **Output:** List of `{"child_root": str, "on": list[str], "conditional_weights": dict}`.
- **Done:** Output is a list of dicts; each dict has exactly the keys `child_root` (str), `on` (list of str), and `conditional_weights` (dict matching the declared conditional weights structure); structure matches §2.6 example.

#### 5.1.4 Emit `columns` block
- **Section:** §2.6 JSON `"columns"` key — detailed per-column metadata.
- **Input:** All registered columns.
- **Output:** List of dicts with keys: `name`, `group`, `parent`, `type` (`categorical`|`temporal`|`measure`), `cardinality` (categoricals), `derived` (temporals), `measure_type`, `family`, `depends_on` (structural measures).
- **Done:** Each column in the one-shot example produces correct metadata dict.

#### 5.1.5 Emit `measure_dag_order`
- **Section:** §2.6 JSON `"measure_dag_order"` key.
- **Input:** Topological sort of measure sub-DAG.
- **Output:** List of measure names in topological order.
- **Done:** `["wait_minutes", "cost", "satisfaction"]` for the example.

#### 5.1.6 Emit `patterns` block
- **Section:** §2.6 JSON `"patterns"` key.
- **Input:** `_patterns` list.
- **Output:** Serialized pattern specs including `type`, `target`, `col`, and type-specific params.
- **Done:** Output matches §2.6 example.

#### 5.1.7 Emit `total_rows`
- **Section:** §2.6 JSON `"total_rows"` key.
- **Input:** `target_rows`.
- **Output:** `{"total_rows": target_rows}`.
- **Done:** `meta["total_rows"] == 500` for the example.

---

## 6. Custom Exception Hierarchy — §2.7

### 6.1 Define typed exceptions

#### 6.1.1 Core SDK exception classes
- **Section:** §2.7 examples: `CyclicDependencyError`, `UndefinedEffectError`, `NonRootDependencyError`.
- **Input:** Various error contexts (cycle path, effect name + missing value, column name).
- **Output:** Three exception classes, each with human-readable messages:
  - `CyclicDependencyError`: `str(e)` contains the cycle path (e.g., `"Measure 'cost' → 'satisfaction' → 'cost' forms a cycle."`).
  - `UndefinedEffectError`: `str(e)` names the effect and the missing key (e.g., `"'severity_surcharge' in formula has no definition for 'Severe'."`).
  - `NonRootDependencyError`: `str(e)` names the non-root column (e.g., `"'department' is not a group root"`).
- **Done:** All three classes are instantiable; each produces a message matching the §2.7 examples; all inherit from a common `SimulatorError` base (or `ValueError`).

#### 6.1.2 Additional validation errors
- **Section:** §2.7 — "degenerate distributions" mentioned.
- **Input:** Various invalid states.
- **Output:** Descriptive exceptions covering: degenerate distribution params (e.g., `sigma=0`), empty values, weight-length mismatches.
- **Done:** Each invalid state produces a uniquely identifiable exception type or message.

---

## 7. Execution-Error Feedback Loop — §2.7

### 7.1 Sandbox executor

#### 7.1.1 Execute LLM-generated script in sandbox
- **Section:** §2.7 steps 1–2: "LLM outputs Python script → Sandbox executes `build_fact_table()`"
- **Input:** Python source code string.
- **Output:** Either `(DataFrame, schema_metadata)` on success, or a captured exception + traceback on failure.
- **Done:** Valid script returns tuple; script with `CyclicDependencyError` returns that exception and full traceback string.

#### 7.1.2 Format error feedback for LLM
- **Section:** §2.7 step 5: "Code + traceback fed back to LLM: 'Adjust parameters to resolve the error.'"
- **Input:** Exception object, original code string, traceback string.
- **Output:** Formatted prompt containing four components: (1) the original source code, (2) the exception class name, (3) the full traceback string, and (4) a natural-language instruction to fix the error (per §2.7 step 5 wording).
- **Done:** Output string contains all four components; the instruction text directs the LLM to adjust parameters to resolve the specific error.

#### 7.1.3 Retry loop with max_retries
- **Section:** §2.7 step 6: "Retry (max_retries=3). If all fail → log and skip."
- **Input:** Initial code, max_retries=3.
- **Output:** Iterates up to 3 times; on success returns result; on exhaustion logs failure and returns `None` or sentinel.
- **Done:** Counter increments per attempt; stops after 3 failures; successful 2nd attempt returns result.

---

## 8. Three-Layer Validator (`SchemaAwareValidator`) — §2.9

### 8.1 Validator framework

#### 8.1.1 `Check` data class
- **Section:** §2.9 L1 code: `Check(name, passed=...)`.
- **Input:** N/A.
- **Output:** Fields: `name: str`, `passed: bool`, `detail: Optional[str]`.
- **Done:** Instantiable; `check.passed` returns bool.

#### 8.1.2 `ValidationReport` aggregator
- **Section:** §2.9 auto-fix loop: `report.all_passed`, `report.failures`.
- **Input:** List of `Check` objects.
- **Output:** `all_passed: bool`, `failures: list[Check]` (where `passed==False`).
- **Done:** Report with one failure has `all_passed == False`; `failures` contains exactly that check.

#### 8.1.3 `validate(df, meta)` orchestrator
- **Section:** §2.9 — calls L1, L2, L3 sequentially.
- **Input:** `df: pd.DataFrame`, `meta: dict` (schema metadata).
- **Output:** `ValidationReport` combining all checks from all three layers.
- **Done:** Returns report containing checks from all layers.

### 8.2 L1: Structural Validation — §2.9 L1 code block

#### 8.2.1 Row count check
- **Section:** §2.9 L1: `abs(len(df) - target) / target < 0.1`
- **Input:** DataFrame, `meta["total_rows"]`.
- **Output:** `Check("row_count", passed=...)`.
- **Done:** 500-row target, 480-row df → passes; 400-row df → fails.

#### 8.2.2 Categorical cardinality check
- **Section:** §2.9 L1: `actual == col["cardinality"]`
- **Input:** DataFrame, categorical column metadata.
- **Output:** One `Check` per categorical column.
- **Done:** Column with declared cardinality 5 but only 4 unique values → fails.

#### 8.2.3 Root marginal weights check
- **Section:** §2.9 L1: `max_dev < 0.10` for root categoricals.
- **Input:** DataFrame, root categorical metadata with `values` and `weights`.
- **Output:** One `Check` per root categorical.
- **Done:** Observed frequency deviating by 0.12 from declared weight → fails.

#### 8.2.4 Measure finite/non-null check
- **Section:** §2.9 L1: `notna().all() and isfinite().all()`.
- **Input:** DataFrame, measure column metadata.
- **Output:** One `Check` per measure column.
- **Done:** Column with one `NaN` → fails (unless realism is active — see 8.2.7).

#### 8.2.5 Orthogonal independence check (chi-squared)
- **Section:** §2.9 L1: `chi2_contingency` on root cross-group pairs, `p_val > 0.05`.
- **Input:** DataFrame, `meta["orthogonal_groups"]`, group hierarchies.
- **Output:** One `Check` per orthogonal pair.
- **Done:** Truly independent columns → p > 0.05 → passes; correlated columns → fails.

#### 8.2.6 Measure DAG acyclicity re-check
- **Section:** §2.9 L1: `is_acyclic(meta.get("measure_dag_order", []))`.
- **Input:** `meta["measure_dag_order"]`.
- **Output:** `Check("measure_dag_acyclic", ...)`.
- **Done:** Always passes if metadata was correctly generated; serves as defense-in-depth.

#### 8.2.7 L1 finiteness check semantics under realism injection
- **Section:** §2.9 L1 `finite_*` check vs. §2.8 Phase δ `_inject_realism` with `missing_rate > 0`.
- **Input:** DataFrame with realism-injected `NaN` values, `_realism_config`.
- **Output:** Resolves the conflict between L1's strict `notna().all()` assertion and realism injection's deliberate NaN introduction. When `_realism_config` is active with `missing_rate > 0`, the `finite_*` check must be adjusted — either by (a) checking `non_null_rate >= (1 - missing_rate - tolerance)` instead of strict non-null, or (b) running the check on the pre-realism DataFrame.
- **Done:** With `missing_rate=0.05`, L1 does not spuriously fail `finite_*` checks for measure columns; without realism, strict `notna().all()` still applies.
- **Added by:** coverage_5_L1_realism_conflict

### 8.3 L2: Statistical Validation — §2.9 L2 code block

#### 8.3.1 Stochastic measure KS-test per predictor cell
- **Section:** §2.9 L2: `kstest(subset[col], family, args=expected_params)` with `p_val > 0.05`.
- **Input:** DataFrame, stochastic measure specs.
- **Output:** One `Check` per (measure, predictor-cell) combination.
- **Done:** Data actually sampled from `LogNormal(3.9, 0.45)` passes KS test against those params.

#### 8.3.2 `iter_predictor_cells()` helper
- **Section:** §2.9 L2 code: `spec.iter_predictor_cells()` yields `(group_filter, expected_params)`.
- **Input:** Measure spec with `param_model`.
- **Output:** Iterator over all categorical cross-product cells; for each, computes concrete params via intercept + effects formula.
- **Done:** For `wait_minutes` with `severity` × `hospital` effects, yields 5×3=15 cells, each with correct `(mu, sigma)`.

#### 8.3.3 Structural measure residual validation
- **Section:** §2.9 L2: `abs(residuals.mean()) < residuals.std() * 0.1` (residual mean check) and `abs(residuals.std() - col["noise_sigma"]) / col["noise_sigma"] < 0.2` (residual std check).
- **Input:** DataFrame, structural measure formula, declared noise sigma.
- **Output:** Two `Check` objects per structural measure: one for residual mean (should be near 0), one for residual std vs. declared sigma.
- **Done:** Formula `cost = wm*12 + surcharge + noise(0,30)`: residual mean near 0 → mean check passes; observed residual std = 28, declared sigma = 30, `|28-30|/30 = 0.067 < 0.2` → std check passes.

#### 8.3.4 `eval_formula()` for L2 residual computation
- **Section:** §2.9 L2 code: `predicted = eval_formula(col["formula"], df)`.
- **Input:** Same as §4.2.8 but operating on full DataFrame.
- **Output:** Series of predicted values (deterministic portion only).
- **Done:** Reuses the same safe evaluator from §4.2.8.

#### 8.3.5 Group dependency conditional deviation check
- **Section:** §2.9 L2: `max_dev < 0.10` on conditional transition matrix vs declared weights.
- **Input:** DataFrame, `meta["group_dependencies"]`.
- **Output:** One `Check` per group dependency.
- **Done:** Observed conditional distribution deviating > 0.10 from declared → fails.

#### 8.3.6 `_max_conditional_deviation()` helper
- **Section:** §2.9 L2 code: `self._max_conditional_deviation(observed, dep["conditional_weights"])`.
- **Input:** Observed crosstab (normalized), declared conditional weights dict.
- **Output:** Maximum absolute deviation across all cells.
- **Done:** Perfect match → 0.0; one cell off by 0.12 → returns 0.12.

### 8.4 L3: Pattern Validation — §2.9 L3 code block

#### 8.4.1 Outlier entity z-score check
- **Section:** §2.9 L3: `z >= 2.0`.
- **Input:** DataFrame, pattern spec.
- **Output:** `Check("outlier_...", passed=z>=2.0)`.
- **Done:** Target subset mean shifted by 2.5 std → passes.

#### 8.4.2 Ranking reversal check
- **Section:** §2.9 L3: `means[m1].rank().corr(means[m2].rank()) < 0`.
- **Input:** DataFrame, pattern spec with `metrics`.
- **Output:** `Check` on rank correlation sign.
- **Done:** Negative Spearman correlation → passes.

#### 8.4.3 Trend break magnitude check
- **Section:** §2.9 L3: `abs(after - before) / before > 0.15`.
- **Input:** DataFrame, pattern spec with `break_point` and `col`.
- **Output:** `Check` on before/after mean difference.
- **Done:** 20% shift → passes; 10% shift → fails.

#### 8.4.4 Dominance shift check
- **Section:** §2.9 L3: delegates to `_verify_dominance_change`.
- **Input:** DataFrame, pattern spec, meta.
- **Output:** `Check("dominance", ...)`.
- **Done:** Dominant category differs before/after time split → passes.

#### 8.4.5 `_verify_dominance_change()` helper
- **Section:** §2.9 L3 code references it.
- **Input:** DataFrame, pattern spec, meta.
- **Output:** `bool` — `True` if the dominant category changed.
- **Done:** Returns `True` when top-ranked category in early period differs from top-ranked in late period.

---

## 9. Auto-Fix Loop — §2.9 "Auto-Fix Loop" section

### 9.1 Strategy dispatch

#### 9.1.1 `match_strategy(check_name, AUTO_FIX)` — glob-based matcher
- **Section:** §2.9 auto-fix code: `match_strategy(check.name, AUTO_FIX)`.
- **Input:** `check.name: str` (e.g., `"ks_wait_minutes_marginal"`), `AUTO_FIX` dict with glob keys (`"ks_*"`, `"outlier_*"`, etc.).
- **Output:** The matching lambda/function, or `None` if no match.
- **Done:** `"ks_wait_minutes_marginal"` matches `"ks_*"` → returns `widen_variance`.

### 9.2 Fix strategies

#### 9.2.1 `widen_variance(check, factor=1.2)`
- **Section:** §2.9: `"ks_*": lambda c: widen_variance(c, factor=1.2)`
- **Input:** Failing check context (measure name, current params).
- **Output:** Adjusts sigma/scale parameter upward by `factor`.
- **Done:** sigma goes from 0.35 → 0.42 after one application.

#### 9.2.2 `amplify_magnitude(check, factor=1.3)`
- **Section:** §2.9: `"outlier_*"` and `"trend_*"` both map to `amplify_magnitude`.
- **Input:** Failing check context (pattern spec).
- **Output:** Scales the pattern's magnitude/z_score param by `factor`.
- **Done:** z_score goes from 3.0 → 3.9 after one application.

#### 9.2.3 `reshuffle_pair(check)`
- **Section:** §2.9: `"orthogonal_*": lambda c: reshuffle_pair(c)`
- **Input:** Failing check context (column pair that failed chi-squared).
- **Output:** Randomly permutes one column of the pair to destroy spurious correlation.
- **Done:** After reshuffle, `chi2_contingency` p-value > 0.05.

### 9.3 `generate_with_validation()` retry loop

#### 9.3.1 Implement the outer retry loop
- **Section:** §2.9 `generate_with_validation` function.
- **Input:** `build_fn` (the `FactTableSimulator.generate` callable), `meta`, `max_retries=3`.
- **Output:** `(df, report)` tuple. On first all-pass → early return. On failure → apply auto-fixes, increment seed (`seed=42+attempt` per §2.9 pseudocode), retry. After exhaustion → soft-fail return.
- **Done:** With a deliberately bad config, runs exactly `max_retries` attempts; with a good config, returns on attempt 1.

#### 9.3.2 Auto-fix must not escalate to LLM
- **Section:** §2.9 — "No LLM calls" in the auto-fix loop; §2.7 step 3 — "SUCCESS → proceed to ... Validation (§2.9)"
- **Input:** Any §2.9 auto-fix iteration.
- **Output:** The auto-fix loop is self-contained: it may re-run `generate()`, apply fix strategies, and increment the seed, but it must **never** trigger the §2.7 LLM re-call loop. If all auto-fix retries are exhausted, the result is a soft-fail return — not an escalation to LLM code regeneration.
- **Done:** Validation failure after 3 auto-fix retries returns `(df, report)` with `report.all_passed == False`; no LLM API call is made during or after the auto-fix loop; the §2.7 loop's retry counter is not modified.
- **Added by:** coverage_6_no_LLM_boundary

---

## 10. LLM Code-Generation Prompt & Integration — §2.5

### 10.1 Prompt template

#### 10.1.1 System prompt construction
- **Section:** §2.5 full prompt template.
- **Input:** N/A (static template string).
- **Output:** String containing SYSTEM block, SDK reference, hard constraints, soft guidelines, one-shot example, and `{scenario_context}` placeholder.
- **Done:** Template string matches §2.5 verbatim; `{scenario_context}` placeholder present.

#### 10.1.2 Scenario context injection
- **Section:** §2.5 `=== YOUR TASK ===` block: `{scenario_context}`.
- **Input:** Scenario context dict from Phase 1 (title, target_rows, entities, metrics, temporal).
- **Output:** Formatted string inserted into the prompt template.
- **Done:** Rendered prompt contains correct title, target_rows, entities, metrics, temporal values from input.

### 10.2 Response parsing

#### 10.2.1 Extract Python code from LLM response
- **Section:** §2.5 constraint 6 — "Output must be pure, valid Python returning `sim.generate()`."
- **Input:** Raw LLM response string.
- **Output:** Clean Python source code string. The spec states the output is "pure, valid Python" — extraction of markdown fences is an implementation convenience, not a spec requirement.
- **Done:** Valid Python code is extracted from the response and available as a string for sandbox execution.

#### 10.2.2 Validate code contains `build_fact_table` and `sim.generate()`
- **Section:** §2.5 constraint 6: "Output must be pure, valid Python returning sim.generate()"
- **Input:** Extracted Python code.
- **Output:** Boolean validation; raises if `sim.generate()` not found.
- **Done:** Code without `generate()` call is rejected.

---

## 11. End-to-End Pipeline Orchestrator — §2.7, §2.8, §2.9

### 11.1 Full Phase 2 pipeline

#### 11.1.1 Stage ordering and branch behavior
- **Section:** §2.7 steps 1–6 (feedback loop) + §2.8 (engine) + §2.9 (validation).
- **Input:** Scenario context from Phase 1.
- **Output:** `(pd.DataFrame, schema_metadata)` or failure sentinel.
- **Done:** Pipeline executes stages in order: prompt construction (§2.5) → LLM call → code extraction (§10.2) → sandbox execution (§7.1) → engine generate (§2.8) → three-layer validation (§2.9) → return. On code execution failure, branches to §2.7 feedback loop. On validation failure, branches to §2.9 auto-fix loop. On full success, returns `(DataFrame, metadata)`. On all-retries-exhausted, returns failure sentinel with logged diagnostics.

#### 11.1.2 Execution-error loop driver (§2.7)
- **Section:** §2.7 — "Retry (max_retries=3). If all fail → log and skip."
- **Input:** LLM-generated code, max_retries=3.
- **Output:** Iterates: execute code → if SDK exception, format error feedback (§7.1.2), re-call LLM, retry. On success, pass result to validation stage. On exhaustion, return failure sentinel.
- **Done:** SDK exception triggers LLM re-call with traceback; success exits loop; 3 consecutive failures return failure.

#### 11.1.3 Validation loop driver (§2.9)
- **Section:** §2.9 `generate_with_validation` — auto-fix loop with max_retries=3.
- **Input:** Successfully executed `(DataFrame, metadata)` from §11.1.2.
- **Output:** Iterates: validate → if failures, apply auto-fix strategies, re-generate with incremented seed, retry. On all-pass, return result. On exhaustion, soft-fail return.
- **Done:** Validation failure triggers auto-fix + re-generate; all-pass exits loop; 3 consecutive failures return soft-fail `(df, report)`.

#### 11.1.4 Sequential composition of §2.7 and §2.9 loops
- **Section:** §2.7 step 3: "SUCCESS → proceed to Deterministic Engine (§2.8) + Validation (§2.9)."
- **Input:** N/A (composition logic).
- **Output:** The two loops compose sequentially: §2.7 runs first until code executes without SDK exceptions, then §2.9 runs on the output until validation passes or retries exhaust. §2.9 failures do **not** escalate back to §2.7.
- **Done:** A script that executes but fails L2 validation triggers the §2.9 auto-fix loop (not the §2.7 LLM re-call loop); a script that raises `CyclicDependencyError` triggers §2.7 (not §2.9).

#### 11.1.5 Budget enforcement and escalation policy
- **Section:** §2.7 (max_retries=3) + §2.9 (max_retries=3).
- **Input:** N/A (policy).
- **Output:** Total worst-case budget: at most 3 LLM calls (§2.7) + 3 engine re-runs (§2.9) = 6 total attempts. No cross-loop escalation. If §2.9 exhausts retries, the pipeline soft-fails — it does not re-enter §2.7.
- **Done:** Total attempt count across both loops never exceeds 6; no §2.9 failure triggers a §2.7 retry.

---

## 12. Integration & Coverage Tests

### 12.1 §2.10 downstream affordance verification

#### 12.1.1 Output schema supports downstream chart types
- **Section:** §2.10 — "The atomic-grain fact table with dimension groups and closed-form measures provides maximum downstream flexibility"; lists 6 chart families.
- **Input:** A `(DataFrame, schema_metadata)` produced by the full pipeline for any scenario with ≥2 dimension groups and ≥2 measures.
- **Output:** The output supports at minimum: (a) distribution charts via raw rows, (b) aggregation charts via GROUP BY on hierarchy roots, (c) drill-down charts via within-group hierarchy, (d) relationship charts via row-level structural dependencies. The metadata contains sufficient information to determine which chart types are feasible.
- **Done:** For the one-shot example: `schema_metadata["dimension_groups"]` contains ≥2 groups; `schema_metadata["measure_dag_order"]` contains ≥2 measures; at least one measure has `measure_type == "structural"` with `depends_on` non-empty (enabling scatter/relationship charts); at least one group has a hierarchy depth ≥2 (enabling drill-down charts).
- **Added by:** coverage_2_§2.10

---

## Cross-Section Dependency Map

The following directed edges represent implementation-order dependencies between tasks. An edge `A → B` means "A must be completed before B can be implemented."

| # | From | To | Rationale |
|---|------|----|-----------|
| 1 | 1.2.4 | 1.2.5 | Parent validation must pass before group registry is updated |
| 2 | 1.2.3 | 1.2.4 | Per-parent weight keys validated against parent column values (requires parent to exist) |
| 3 | 1.2.5 | 1.4.3 | `param_model` effects reference categorical columns registered via group registry |
| 4 | 1.4.5 | 1.5.2 | Formula symbol resolution looks up measures in the measure DAG (requires measures registered as root nodes) |
| 5 | 1.5.2 | 1.5.5 | Cycle detection operates on DAG edges created during formula resolution |
| 6 | 1.2.6 | 1.7.1 | Root-only constraint check requires knowing which columns are group roots |
| 7 | 1.6.2 | 1.7.4 | Dependency conflict check reads the orthogonal pair store |
| 8 | 1.7.2 | 1.6.3 | Orthogonal conflict check reads the group dependency store |
| 9 | 1.2–1.9 | 3.1.1 | DAG builder reads all registered columns, groups, hierarchies, dependencies, temporal derivations |
| 10 | 3.1.1 | 3.1.2 | Topological sort requires the constructed DAG |
| 11 | 3.1.1 | 3.2.1 | Measure sub-DAG is extracted from the full DAG |
| 12 | 3.1.2 | 4.1.1 | Skeleton builder uses topological order to determine generation sequence |
| 13 | 3.2.1 | 4.2.1 | Measure generation follows measure DAG topological order |
| 14 | 4.2.1–4.2.7 | 4.3.1–4.3.6 | Pattern injection operates on the post-measure-generation DataFrame |
| 15 | 4.3.1–4.3.6 | 4.4.1–4.4.3 | Realism injection operates on the post-pattern-injection DataFrame |
| 16 | 1.1.2 | 5.1.1–5.1.7 | Metadata builder reads all internal registries |
| 17 | 4.2.8 | 8.3.4 | L2 residual computation reuses the engine's safe formula evaluator |
| 18 | 8.1.3 | 9.3.1 | Retry loop calls the validator orchestrator |
| 19 | 9.1.1 + 9.2.1–9.2.3 | 9.3.1 | Retry loop dispatches to strategy matcher and fix functions |
| 20 | 7.1.1–7.1.3 + 9.3.1 + 10.1–10.2 | 11.1.1 | End-to-end orchestrator composes all subsystems |

---

## Patch Log (v2 — Post-Audit)

| Finding ID | Change Type | Description |
|---|---|---|
| coverage_4_generate_contract | ADDED | New leaf task 1.1.3: test `generate()` public API returns `Tuple[pd.DataFrame, dict]`. |
| coverage_3_reproducibility | ADDED | New leaf task 4.6.1: verify bit-for-bit reproducibility with same seed. |
| coverage_5_L1_realism_conflict | ADDED | New leaf task 8.2.7: resolve L1 finiteness check semantics under realism injection. |
| coverage_6_no_LLM_boundary | ADDED | New leaf task 9.3.2: auto-fix validation loop must not escalate to LLM. |
| coverage_2_§2.10 | ADDED | New section 12 with leaf task 12.1.1: integration test verifying §2.10 downstream affordances. |
| phantom_1.3.2_freq_whitelist | MODIFIED | Task 1.3.2: removed the `"daily"`, `"weekly"`, `"monthly"` whitelist. Spec only demonstrates `"daily"`; no frequency whitelist is defined. Retitled to "Frequency storage." |
| phantom_1.8.2_target_parsing | MODIFIED | Task 1.8.2: removed declaration-time target-expression parsing and column validation. Target strings are stored as-is; execution-time `df.query()` provides implicit validation. Retitled to "Target expression storage." |
| phantom_1.8.4_all_params | MODIFIED | Task 1.8.4: scoped required-key validation to the 2 pattern types with spec-defined params (`outlier_entity`, `trend_break`). The remaining 4 types store params without key validation. |
| phantom_10.2.1_fence_extraction | MODIFIED | Task 10.2.1: removed markdown-fence extraction as a spec requirement. Spec says "pure, valid Python"; fence handling is an implementation convenience. |
| phantom_1.2.1_dup_col | RELABELED | Task 1.2.1: added `NEEDS_CLARIFICATION` annotation — duplicate column name rejection is inferred, not explicitly stated. |
| phantom_1.2.6_dup_root | RELABELED | Task 1.2.6: added `NEEDS_CLARIFICATION` annotation — singular "a root" is strong inference but not an explicit rejection rule. |
| phantom_1.4.2_canonical_repr | RELABELED | Task 1.4.2: added `Implementation Design Choice` annotation — canonical internal representation is not prescribed by the spec. |
| phantom_1.6.3_1.7.4_mutual_excl | RELABELED | Tasks 1.6.3 and 1.7.4: added `NEEDS_CLARIFICATION` annotation — mutual exclusion of orthogonal and dependent is semantically inferred, not explicitly stated. |
| phantom_2.1.1_2.2.1_2.2.2_classes | RELABELED | Tasks 2.1.1, 2.2.1, 2.2.2: added `Implementation Design Choice` annotation — class structure is not prescribed by spec. Also removed invented `group_type` field from 2.1.1 (not in §2.2 or §2.6). |
| phantom_3.1.1_networkx | RELABELED | Task 3.1.1: added `Implementation Design Choice` annotation — `networkx` is one valid choice, not a spec requirement. |
| phantom_4.5.1_dtypes | RELABELED | Task 4.5.1: added `Implementation Design Choice` annotation — specific dtype policies are not prescribed by spec. |
| granularity_6.1.1-3 | MERGED | Merged old 6.1.1/6.1.2/6.1.3 into single task 6.1.1 covering all three core exception classes. Old 6.1.4 renumbered to 6.1.2. |
| granularity_8.3.3-4 | MERGED | Merged old 8.3.3/8.3.4 into single task 8.3.3 (structural measure residual validation). Old 8.3.5→8.3.4, 8.3.6→8.3.5, 8.3.7→8.3.6. |
| granularity_11.1.1 | PROMOTED | Old 11.1.1 promoted from leaf to parent node (section 11.1). New 11.1.1 is "Stage ordering and branch behavior." |
| granularity_11.1.2 | DECOMPOSED | Old 11.1.2 decomposed into four sub-tasks: 11.1.2 (§2.7 driver), 11.1.3 (§2.9 driver), 11.1.4 (sequential composition), 11.1.5 (budget enforcement). |
| granularity_4.2.1 | SPLIT | Old 4.2.1 split into three tasks: 4.2.1 (parameter resolution), 4.2.2 (domain validation), 4.2.3 (sampling dispatch). Old 4.2.2 renumbered to 4.2.4. |
| granularity_4.2.3 | SPLIT | Old 4.2.3 split into three tasks: 4.2.5 (formula evaluation), 4.2.6 (effect materialization), 4.2.7 (noise sampling). Old 4.2.4 renumbered to 4.2.8. |
| done_1.5.1 | REWRITTEN | Task 1.5.1 done condition: expanded from "No error on valid call" to assert that all fields (formula, effects, noise) are stored and queryable. |
| done_2.1.1 | REWRITTEN | Task 2.1.1 done condition: anchored to §2.6 metadata output format; removed invented `group_type` field; added serialization assertion. |
| done_5.1.3 | REWRITTEN | Task 5.1.3 done condition: added exact-structure assertion with specific key names and types matching §2.6. |
| done_7.1.2 | REWRITTEN | Task 7.1.2 done condition: adopted four-component payload assertion (code, exception class, traceback, instruction). |
| done_11.1.1 | REWRITTEN | Task 11.1.1 done condition: adopted stage-ordering and branch-behavior assertion covering the full pipeline flow. |
| all_20_dependencies | ADDED | New "Cross-Section Dependency Map" section with 20 directed dependency edges between task hierarchy sections. |
