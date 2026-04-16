# Module 1: SDK Surface — SVG Flow Diagram Guide

**SVG file:** `module1_sdk_surface.svg`
**Source of truth:** `docs/artifacts/stage5_anatomy_summary.md` — Module: SDK Surface (M1)
**Implementation:** `phase_2/sdk/`

---

## SVG Section Map

The SVG is divided into two columns plus a bottom output zone:

- **Left column** (x=18..240): SDK method boxes — the public API surface
- **Middle zone** (x=240..460): Arrow legend and connecting arrows
- **Right column** (x=462..852): Declaration Store — the internal state accumulator
- **Bottom zone** (y=720..836): Frozen store boundary and downstream consumer boxes

```
┌──────────────────────────────────────────────────────────────────────┐
│                      Module 1: SDK Surface (M1)                      │
│                                                                      │
│  LEFT COLUMN                ARROWS           RIGHT COLUMN            │
│                                                                      │
│  ┌─────────────┐                          ┌────────────────────────┐ │
│  │ 1. §2.1     │─────── write ──────────►│                        │ │
│  │ Constructor  │                          │  5. DECLARATION STORE  │ │
│  └─────────────┘                          │     (internal state)   │ │
│                                            │                        │ │
│  ┌─────────────┐                          │  • columns[]            │ │
│  │ 2. §2.1.1   │─────── write ──────────►│  • groups{}             │ │
│  │ Column Decls │                          │  • measure_dag          │ │
│  └──────┬──────┘                          │  • patterns[]           │ │
│         │ ordering                        │  • orthogonal_pairs[]  │ │
│         ▼                                  │  • group_dependencies[] │ │
│  ┌─────────────┐                          │  • realism_config?     │ │
│  │ 3. §2.1.2   │─────── write ──────────►│                        │ │
│  │ Rel & Patt   │                          │  measure_dag_order[]   │ │
│  └─────────────┘                 ◄── read ─┤  (computed by §2.3)   │ │
│                                            └────────────────────────┘ │
│  ┌─────────────┐                                                     │
│  │ 4a. §2.2    │◄──────── read (conceptual lens) ──────┘            │
│  │ Dim Groups  │                                                     │
│  └─────────────┘                                                     │
│                                                                      │
│  ┌─────────────┐                                                     │
│  │ 4b. §2.3    │── reads dag_edges ──► writes dag_order[] ──►       │
│  │ Closed-Form │                                                     │
│  └─────────────┘                                                     │
│                                                                      │
│  ════════════════════════════════════════════════════════════════     │
│  6. FROZEN DECLARATION STORE — output boundary                       │
│  ════════════════════════════════════════════════════════════════     │
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐                │
│  │7a. → M2  │    │7b. → M4  │    │7c. → M3          │                │
│  │Gen Engine │    │Schema    │    │typed Exceptions   │                │
│  └──────────┘    └──────────┘    └──────────────────┘                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 1. §2.1 Constructor

**SVG region:** Left column, top box (y=56..138), blue header

**What it represents:** The entry point for LLM-generated scripts. Creates an empty `FactTableSimulator` instance with configuration parameters, initializing an empty `DeclarationStore`.

**Responsible file:** `phase_2/sdk/simulator.py`

| | Detail |
|---|---|
| **Input** | `target_rows: int`, `seed: int = 42` |
| **Output** | A new `FactTableSimulator` instance with an empty, mutable `DeclarationStore` |
| **Store fields written** | `target_rows`, `seed` (stored on the `DeclarationStore`); all registries initialized empty |

**Call order:**
```
FactTableSimulator.__init__(target_rows, seed)
  ├─ validates target_rows >= 1
  ├─ DeclarationStore(target_rows, seed)          [from phase_2/types.py]
  │    └─ initializes: columns={}, groups={}, orthogonal_pairs=[],
  │       group_dependencies=[], patterns=[], realism_config=None,
  │       measure_dag={}, _frozen=False
  └─ sets internal _phase = STEP_1 (declaring phase)
```

**SVG arrow:** Solid arrow from Constructor box → Declaration Store, labeled "empty instance / config".

---

## 2. §2.1.1 Column Declarations

**SVG region:** Left column, second box (y=148..310), blue header

**What it represents:** The four Step 1 methods that populate the column registry, group graph, and measure DAG edges. These are the primary data-producing methods of M1.

**Responsible files:**
- `phase_2/sdk/simulator.py` — thin delegation shell (phase enforcement + forwarding)
- `phase_2/sdk/columns.py` — actual declaration logic
- `phase_2/sdk/validation.py` — declaration-time validation rules
- `phase_2/sdk/groups.py` — group registry updates
- `phase_2/sdk/dag.py` — measure DAG acyclicity checks

| | Detail |
|---|---|
| **Input** | Column descriptors: `name`, `type`, `group`, `parent`, `family`, `param_model`, `formula`, `effects`, `noise` |
| **Output** | Entries appended to `columns`, `groups`, and `measure_dag` registries in the Declaration Store |
| **Store fields written** | `columns` (all 4 methods), `groups` (add_category, add_temporal), `measure_dag` (add_measure_structural) |

**SVG arrow:** Solid arrow from Column Decls box → Declaration Store, labeled "column descriptors". Also a note "(also writes measure_dag via add_measure_structural)".

### 2a. `add_category()`

```
simulator.add_category(name, values, weights, group, parent=None)
  └─ simulator._ensure_declaring_phase()
       └─ columns.add_category(self._columns, self._groups, name, values, weights, group, parent)
            ├─ validation.validate_column_name(name, columns)          → raises DuplicateColumnError
            ├─ validation.validate_parent(parent, group, columns)      → raises SDKError  [if parent]
            ├─ validation.validate_and_normalize_flat_weights(...)     → normalized list   [if list]
            │   OR validation.validate_and_normalize_dict_weights(...) → normalized dict   [if dict]
            ├─ columns[name] = col_meta                                ← MUTATES columns
            └─ groups.register_categorical_column(groups, group, name, is_root=(parent is None))
                 ├─ groups[group_name] = DimensionGroup(...)           ← MUTATES groups (if new)
                 └─ group.columns.append(name)                        ← MUTATES groups
```

### 2b. `add_temporal()`

```
simulator.add_temporal(name, start, end, freq, derive=None)
  └─ simulator._ensure_declaring_phase()
       └─ columns.add_temporal(self._columns, self._groups, name, start, end, freq, derive)
            ├─ validation.validate_column_name(name, columns)
            ├─ columns._parse_iso_date(start, "start")
            ├─ columns._parse_iso_date(end, "end")
            ├─ columns[name] = col_meta (type="temporal")             ← MUTATES columns
            ├─ for each derived in derive:
            │    └─ columns[derived_name] = col_meta (type="temporal_derived")  ← MUTATES columns
            └─ groups.register_temporal_group(groups, "time", name, derived_col_names)
                 └─ groups["time"] = DimensionGroup(...)              ← MUTATES groups
```

### 2c. `add_measure()`

```
simulator.add_measure(name, family, param_model, scale=None)
  └─ simulator._ensure_declaring_phase()
       └─ columns.add_measure(self._columns, name, family, param_model, scale)
            ├─ validation.validate_column_name(name, columns)
            ├─ validation.validate_family(family)                     → raises ValueError
            ├─ validation.validate_param_model(name, family, param_model, columns)
            │    └─ for each param key:
            │         └─ validation.validate_param_value(name, family, key, value, columns)
            │              └─ validation.validate_effects_in_param(...)  [if effects dict]
            └─ columns[name] = col_meta (type="measure", measure_type="stochastic")  ← MUTATES columns
```

### 2d. `add_measure_structural()`

```
simulator.add_measure_structural(name, formula, effects=None, noise=None)
  └─ simulator._ensure_declaring_phase()
       └─ columns.add_measure_structural(self._columns, self._measure_dag, name, formula, effects, noise)
            ├─ validation.validate_column_name(name, columns)
            ├─ validation.extract_formula_symbols(formula)                    → set[str]
            ├─ validation.validate_structural_effects(name, formula, effects, columns)  [if effects]
            ├─ dag.check_measure_dag_acyclic(measure_dag, name, measure_deps)
            │    ├─ builds tentative adjacency with new edges
            │    └─ dag.detect_cycle_in_adjacency(tentative)                  → raises CyclicDependencyError
            ├─ columns[name] = col_meta (type="measure", measure_type="structural")  ← MUTATES columns
            └─ measure_dag[dep].append(name) for each upstream dep            ← MUTATES measure_dag
```

---

## 3. §2.1.2 Relationship & Pattern Declarations

**SVG region:** Left column, third box (y=320..468), amber/orange header

**What it represents:** The four Step 2 methods that add cross-column relationships, patterns, and realism configuration. These require the column registry to already be populated (ordering constraint).

**Responsible files:**
- `phase_2/sdk/simulator.py` — phase enforcement + forwarding
- `phase_2/sdk/relationships.py` — declaration logic
- `phase_2/sdk/validation.py` — weight normalization
- `phase_2/sdk/groups.py` — root column lookups
- `phase_2/sdk/dag.py` — root-level DAG acyclicity

| | Detail |
|---|---|
| **Input** | Orthogonal pairs, group dependencies with conditional weights, pattern specs, realism config |
| **Output** | Entries appended to `orthogonal_pairs`, `group_dependencies`, `patterns`, `realism_config` |
| **Store fields written** | `orthogonal_pairs` (declare_orthogonal), `group_dependencies` (add_group_dependency), `patterns` (inject_pattern), `realism_config` (set_realism) |

**SVG arrow:** Solid arrow from Relationship box → Declaration Store, labeled "orth pairs, group deps, patterns, realism config".

**Ordering constraint** (shown as annotation between sections 2 and 3 in SVG): §2.1.1 must complete before §2.1.2 is callable. In the implementation, the first call to any Step 2 method triggers `_ensure_relating_phase()`, which transitions `_phase` from `STEP_1` to `STEP_2`, permanently blocking further Step 1 calls.

### 3a. `declare_orthogonal()`

```
simulator.declare_orthogonal(group_a, group_b, rationale="")
  └─ simulator._ensure_relating_phase()
       └─ relationships.declare_orthogonal(self._groups, self._orthogonal_pairs,
                                           self._group_dependencies, self._columns,
                                           group_a, group_b, rationale)
            ├─ validates group_a and group_b exist in groups dict
            ├─ relationships._check_dependency_conflict(group_a, group_b, group_dependencies, columns)
            │    ├─ groups.get_group_for_column(dep.child_root, columns)   [for each existing dep]
            │    └─ groups.get_group_for_column(dep.on[0], columns)
            ├─ checks for duplicate orthogonal pair
            └─ orthogonal_pairs.append(OrthogonalPair(group_a, group_b, rationale))  ← MUTATES
```

### 3b. `add_group_dependency()`

```
simulator.add_group_dependency(child_root, on, conditional_weights)
  └─ simulator._ensure_relating_phase()
       └─ relationships.add_group_dependency(self._columns, self._groups,
                                             self._group_dependencies, self._orthogonal_pairs,
                                             child_root, on, conditional_weights)
            ├─ validates len(on) == 1 (single-column restriction)
            ├─ groups.is_group_root(child_root, columns, groups)       → validates is root
            ├─ groups.is_group_root(on[0], columns, groups)            → validates is root
            ├─ groups.get_group_for_column(child_root, columns)        → child_group
            ├─ groups.get_group_for_column(on[0], columns)             → parent_group
            ├─ relationships._check_orthogonal_conflict(child_group, parent_group, orthogonal_pairs)
            ├─ dag.check_root_dag_acyclic(group_dependencies, child_root, on[0])
            │    ├─ builds adjacency from existing deps + proposed edge
            │    └─ dag.detect_cycle_in_adjacency(adjacency)           → raises CyclicDependencyError
            ├─ validates conditional_weights coverage per parent value
            │    └─ validation.normalize_weight_dict_values(label, weight_map)  [per parent value]
            └─ group_dependencies.append(GroupDependency(child_root, on, conditional_weights))  ← MUTATES
```

### 3c. `inject_pattern()`

```
simulator.inject_pattern(type, target, col, params=None, **extra_params)
  └─ simulator._ensure_relating_phase()
       └─ relationships.inject_pattern(self._columns, self._patterns,
                                       type, target, col, **merged_params)
            ├─ validates type in VALID_PATTERN_TYPES
            ├─ validates col exists in columns and is type="measure"
            ├─ validates required params per pattern type (e.g., z_score for outlier_entity)
            └─ patterns.append({type, target, col, params})            ← MUTATES
```

### 3d. `set_realism()`

```
simulator.set_realism(missing_rate=0.0, dirty_rate=0.0, censoring=None)
  └─ simulator._ensure_relating_phase()
       └─ relationships.set_realism([], missing_rate, dirty_rate, censoring)
            ├─ validates missing_rate in [0.0, 1.0]
            ├─ validates dirty_rate in [0.0, 1.0]
            └─ returns config dict  → assigned to simulator._realism_config   ← MUTATES (on simulator)
```

---

## 4a. §2.2 Dimension Groups (read-only lens)

**SVG region:** Left column, dashed-border box (y=480..572)

**What it represents:** A conceptual abstraction over `columns` and `groups` — not a distinct computation, but a logical view that reveals the dimension-group structure. The dashed border in the SVG indicates it produces no new data.

**Responsible file:** `phase_2/sdk/groups.py`

| | Detail |
|---|---|
| **Input** | Reads `columns` and `groups` from Declaration Store |
| **Output** | No new fields written — exposes the existing group structure as a read-only view |
| **Store fields read** | `columns` (via `get_group_for_column`, `is_group_root`), `groups` (via `get_roots`) |

**SVG arrow:** Dashed read arrow from Declaration Store (at `columns` + `groups` rows) bending down to the §2.2 box, labeled "reads columns + groups".

**Key functions (query-only, no mutations):**
```
groups.get_roots(groups)                                → list[str]  (root column per group)
groups.is_group_root(column_name, columns, groups)      → bool
groups.get_group_for_column(column_name, columns)       → str | None
```

These functions are called by `relationships.py` (sections 3a, 3b) during declaration-time validation, not as a standalone step. §2.2 is conceptual, not procedural.

---

## 4b. §2.3 Closed-Form Measures (DAG computation)

**SVG region:** Left column, purple-header box (y=582..700)

**What it represents:** The topological sort of `measure_dag` into `measure_dag_order[]`. This is the only section that both reads from and writes back to the Declaration Store. The resulting order determines M2's measure generation sequence.

**Responsible file:** `phase_2/sdk/dag.py`

| | Detail |
|---|---|
| **Input** | Reads `measure_dag` from Declaration Store (accumulated by §2.1.1 `add_measure_structural`) |
| **Output** | `measure_dag_order[]` — topological sort written back to Declaration Store |
| **Store fields read** | `measure_dag` (edges), `columns` (to identify measure nodes) |
| **Store fields written** | The sorted order is computed on-demand by `topological_sort()` rather than stored as a separate field; it is consumed by `build_full_dag()` during M2 pre-flight |

**SVG arrows:**
- Dashed read arrow from Declaration Store (`measure_dag` row) → §2.3 box, labeled "reads measure_dag"
- Solid purple write-back arrow from §2.3 box → Declaration Store (`measure_dag_order[]` row), labeled "writes measure_dag_order[]"

**Call order (at generation time, triggered by M2 pre-flight):**
```
dag.build_full_dag(columns, groups, group_dependencies, measure_dag)
  ├─ collects edges from 5 sources:
  │    1. intra-group hierarchy:    parent → child
  │    2. cross-group dependencies: parent_root → child_root
  │    3. temporal derivation:      root → derived features
  │    4. measure predictor refs:   predictor_col → measure
  │    5. measure-measure DAG:      upstream → downstream
  ├─ dag.detect_cycle_in_adjacency(adjacency)       → raises CyclicDependencyError
  └─ returns full adjacency dict

dag.topological_sort(adjacency)
  ├─ Kahn's algorithm with lexicographic tie-breaking (heapq)
  └─ returns ordered list of all column names

dag.extract_measure_sub_dag(full_dag, measure_names)
  └─ returns (measure-only adjacency, measure topo order)
```

**Note:** The incremental acyclicity checks in sections 2d and 3b (`check_measure_dag_acyclic`, `check_root_dag_acyclic`) are called during declaration time. The full DAG build and topological sort happen later at generation time (M2 pre-flight).

---

## 5. Declaration Store (internal state)

**SVG region:** Right column, large green-bordered box (x=462..852, y=56..700)

**What it represents:** The central mutable data structure that accumulates all declarations. Every SDK method writes to one or more of its registries. After all declarations complete, it is frozen and becomes the immutable contract consumed by M2, M4, and M5.

**Responsible file:** `phase_2/types.py` — `DeclarationStore` class

| | Detail |
|---|---|
| **Input** | Written to by all §2.1–§2.1.2 methods |
| **Output** | Read by §2.2 (groups), §2.3 (DAG); consumed by M2, M4, M5 after freeze |

**Registry fields** (shown as bullet list in SVG):

| Field | Written by | Read by |
|---|---|---|
| `columns: OrderedDict` | §2.1.1 (all 4 methods) | §2.1.2 (validation), §2.2, §2.3, M2, M4 |
| `groups: dict[str, DimensionGroup]` | §2.1.1 (add_category, add_temporal) | §2.1.2 (validation), §2.2, M2, M4 |
| `measure_dag: dict[str, list[str]]` | §2.1.1 (add_measure_structural) | §2.3, M2 pre-flight |
| `patterns: list[dict]` | §2.1.2 (inject_pattern) | M2 stage gamma, M4, M5 L3 |
| `orthogonal_pairs: list[OrthogonalPair]` | §2.1.2 (declare_orthogonal) | M4, M5 L1 |
| `group_dependencies: list[GroupDependency]` | §2.1.2 (add_group_dependency) | M2 stage alpha, M4, M5 L2 |
| `realism_config: dict | None` | §2.1.2 (set_realism) | M2 stage delta, M4 |
| `target_rows: int` | §2.1 (Constructor) | M2, M4, M5 L1 |
| `seed: int` | §2.1 (Constructor) | M2 (RNG initialization) |

**SVG annotations inside the store box:**
- **Lifecycle & Dependencies** section (y=330..560): Documents the ordering of steps 1–5
- **Downstream Consumers** section (y=578..650): Lists M2, M4, M3 with what each receives
- **Ordering constraint** note (y=668..696): "§2.1.1 must complete before §2.1.2 is callable"
- **Highlighted rows**: `columns` and `groups` highlighted blue (§2.2 reads), `measure_dag` highlighted amber (§2.3 reads), `measure_dag_order` highlighted purple (§2.3 writes)

**Lifecycle phases:**
```
1. ACCUMULATING  (§2.1 → §2.1.1 → §2.1.2)
   └─ _frozen = False; all mutation methods allowed within their phase
   └─ _check_mutable() called before every write; passes

2. FROZEN  (after generate() calls store.freeze())
   └─ _frozen = True; _check_mutable() raises RuntimeError
   └─ store is immutable; passed to M2, M4

3. CONSUMED  (by M2 Gen Engine, M4 Schema Metadata, M5 Validation Engine)
   └─ read-only access to all registries
```

---

## 6. Frozen Declaration Store (output boundary)

**SVG region:** Full-width bar (x=18..852, y=720..766), blue border with dashed separator

**What it represents:** The conceptual boundary where the mutable store becomes immutable. This is triggered by `FactTableSimulator.generate()`, which calls `store.freeze()` before passing the store downstream.

**Responsible file:** `phase_2/sdk/simulator.py` → `generate()`

| | Detail |
|---|---|
| **Input** | Fully populated `DeclarationStore` from all §2.1–§2.3 steps |
| **Output** | Same store, now immutable (`_frozen = True`) |
| **Trigger** | `FactTableSimulator.generate()` |

**Call order:**
```
simulator.generate()
  ├─ self._store.freeze()                         ← sets _frozen = True
  └─ engine.generator.run_pipeline(
       columns=self._columns,
       groups=self._groups,
       group_dependencies=self._group_dependencies,
       measure_dag=self._measure_dag,
       target_rows=self._store.target_rows,
       seed=self._store.seed,
       patterns=self._patterns,
       realism_config=self._realism_config,
       orthogonal_pairs=self._orthogonal_pairs,
     )
     └─ returns (df: pd.DataFrame, metadata: dict)
```

**SVG label:** "FROZEN DECLARATION STORE — output boundary" with subtitle "All declarations sealed after §2.1 → §2.3 complete; store is now immutable".

---

## 7a/7b/7c. Downstream Consumer Boxes

**SVG region:** Three boxes at the bottom (y=784..836), each receiving an arrow from the frozen store bar

### 7a. M2: Generation Engine

**SVG region:** Bottom-left green box (x=18..288)

| | Detail |
|---|---|
| **Receives** | Full declaration store + seed |
| **Purpose** | Generates the main DataFrame through the 4-stage pipeline (alpha → beta → gamma → delta → Post) |
| **Implementation** | `phase_2/engine/generator.py` → `run_pipeline()` |

### 7b. M4: Schema Metadata

**SVG region:** Bottom-center amber box (x=300..570)

| | Detail |
|---|---|
| **Receives** | Full declaration store |
| **Purpose** | Builds the 7-key `schema_metadata` dict from store registries |
| **Implementation** | `phase_2/metadata/builder.py` → `build_schema_metadata()` |

### 7c. M3: LLM Orchestration

**SVG region:** Bottom-right red box (x=582..852)

| | Detail |
|---|---|
| **Receives** | Typed `Exception` objects on validation failure |
| **Purpose** | Feeds SDK validation errors back into Loop A for LLM self-correction |
| **Exception types** | `DuplicateColumnError`, `CyclicDependencyError`, `UndefinedEffectError`, `NonRootDependencyError`, `UndefinedPredictorError` (from `phase_2/exceptions.py`) |

---

## Complete File Responsibility Map

| SVG Section | Primary File | Supporting Files |
|---|---|---|
| 1. §2.1 Constructor | `sdk/simulator.py` | `types.py` (DeclarationStore) |
| 2. §2.1.1 Column Declarations | `sdk/columns.py` | `sdk/validation.py`, `sdk/groups.py`, `sdk/dag.py` |
| 3. §2.1.2 Relationship & Pattern Decls | `sdk/relationships.py` | `sdk/validation.py`, `sdk/groups.py`, `sdk/dag.py` |
| 4a. §2.2 Dimension Groups | `sdk/groups.py` | — |
| 4b. §2.3 Closed-Form Measures | `sdk/dag.py` | — |
| 5. Declaration Store | `types.py` | — |
| 6. Frozen Store boundary | `sdk/simulator.py` | `types.py` (freeze) |
| 7a. → M2 Gen Engine | `engine/generator.py` | — |
| 7b. → M4 Schema Metadata | `metadata/builder.py` | — |
| 7c. → M3 (Exceptions) | `exceptions.py` | `sdk/validation.py`, `sdk/dag.py` |

---

## End-to-End Call Trace

```
[LLM-generated script calls M1 SDK via sandbox]

FactTableSimulator(target_rows=1000, seed=42)                  ← §2.1 Constructor
│
├─ DeclarationStore(target_rows=1000, seed=42)                 ← empty store created
│
│  ═══ STEP 1: Column Declarations (§2.1.1) ═══
│
├─ .add_category("hospital", [...], [...], "entity")
│   └─ simulator._ensure_declaring_phase()
│       └─ columns.add_category(self._columns, self._groups, ...)
│            ├─ validation.validate_column_name()
│            ├─ validation.validate_and_normalize_flat_weights()
│            ├─ columns["hospital"] = col_meta                 ← MUTATES columns
│            └─ groups.register_categorical_column()           ← MUTATES groups
│
├─ .add_category("department", [...], {...}, "entity", parent="hospital")
│   └─ [same chain, with validate_parent + dict weight normalization]
│
├─ .add_temporal("visit_date", "2023-01-01", "2024-12-31", "D", derive=["month", "day_of_week"])
│   └─ columns.add_temporal(...)
│        ├─ columns["visit_date"] = col_meta                   ← MUTATES columns
│        ├─ columns["month"] = col_meta (temporal_derived)     ← MUTATES columns
│        ├─ columns["day_of_week"] = col_meta                  ← MUTATES columns
│        └─ groups.register_temporal_group()                   ← MUTATES groups
│
├─ .add_measure("wait_minutes", "lognormal", {mu: ..., sigma: ...})
│   └─ columns.add_measure(...)
│        ├─ validation.validate_family("lognormal")
│        ├─ validation.validate_param_model(...)
│        └─ columns["wait_minutes"] = col_meta                 ← MUTATES columns
│
├─ .add_measure_structural("cost", "wait_minutes * 2.5", effects={...}, noise={...})
│   └─ columns.add_measure_structural(...)
│        ├─ validation.extract_formula_symbols("wait_minutes * 2.5")  → {"wait_minutes"}
│        ├─ dag.check_measure_dag_acyclic(measure_dag, "cost", ["wait_minutes"])
│        ├─ columns["cost"] = col_meta                         ← MUTATES columns
│        └─ measure_dag["wait_minutes"].append("cost")         ← MUTATES measure_dag
│
│  ═══ STEP 2: Relationship & Pattern Declarations (§2.1.2) ═══
│  [first Step 2 call transitions _phase from STEP_1 → STEP_2]
│
├─ .declare_orthogonal("entity", "time", "No causal link")
│   └─ simulator._ensure_relating_phase()                      ← phase transition
│       └─ relationships.declare_orthogonal(...)
│            ├─ relationships._check_dependency_conflict(...)
│            └─ orthogonal_pairs.append(OrthogonalPair(...))   ← MUTATES orthogonal_pairs
│
├─ .inject_pattern("outlier_entity", 'hospital == "St. Mary"', "wait_minutes", z_score=3.0)
│   └─ relationships.inject_pattern(...)
│        └─ patterns.append({type, target, col, params})       ← MUTATES patterns
│
├─ .set_realism(missing_rate=0.02, dirty_rate=0.01)
│   └─ relationships.set_realism(...)
│        └─ returns config dict → self._realism_config =       ← MUTATES realism_config
│
│  ═══ GENERATION (§2.1 generate → freeze → M2/M4) ═══
│
└─ .generate()
     ├─ self._store.freeze()                                   ← _frozen = True
     └─ engine.generator.run_pipeline(
          columns, groups, group_dependencies, measure_dag,
          target_rows, seed, patterns, realism_config,
          orthogonal_pairs
        )
        ├─ dag.build_full_dag(...)                             ← §2.3 full DAG assembly
        │    └─ dag.topological_sort(adjacency)                ← measure_dag_order computed
        ├─ [M2 pipeline: alpha → beta → gamma → delta → Post]
        ├─ metadata.builder.build_schema_metadata(...)         ← M4 metadata assembly
        └─ returns (df: pd.DataFrame, metadata: dict)
```
