# Module 4: Schema Metadata — SVG Flow Diagram Guide

**SVG file:** `module4_schema_metadata.svg`
**Source of truth:** `docs/artifacts/stage5_anatomy_summary.md` — Module: Schema Metadata (M4)
**Implementation:** `phase_2/metadata/`

---

## SVG Section Map

The SVG is a single-column vertical flow (no left/right split at the top level). Internally, the main processing box (§2.6) has a left/right split separating required vs. optional inputs.

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   ┌──────────────────────┐    ┌───────────────────────┐             │
│   │  1. INPUT 1           │    │  2. INPUT 2           │             │
│   │  M1 Declaration Store │    │  M2 Master DataFrame  │             │
│   │  (required, solid)    │    │  (optional, dashed)   │             │
│   └──────────┬───────────┘    └───────────┬───────────┘             │
│              │ (solid arrow)              │ (dashed arrow)          │
│              ▼                            ▼                         │
│   ┌──────────────────────────────────────────────────────┐          │
│   │  3. §2.6 SCHEMA METADATA BUILDER                     │          │
│   │                                                       │          │
│   │   ┌─────────────────┐ │ ┌─────────────────┐          │          │
│   │   │ Left: From Decl │ │ │ Right: From DF  │          │          │
│   │   │ Store (required) │ │ │ (optional)      │          │          │
│   │   └─────────────────┘ │ └─────────────────┘          │          │
│   │                                                       │          │
│   │   Output: schema_metadata (dict) → M5 Validation      │          │
│   └──────────────────────┬───────────────────────────────┘          │
│                          │                                          │
│                          ▼                                          │
│   ┌──────────────────────────────────────────────────────┐          │
│   │  4. schema_metadata DICT — 7 top-level keys           │          │
│   │     (reference table: key → value type / shape)       │          │
│   └──────────────────────┬───────────────────────────────┘          │
│                          │                                          │
│                          ▼                                          │
│   ┌──────────────────────────────────────────────────────┐          │
│   │  5. M5: VALIDATION ENGINE (Phase 3)                   │          │
│   └──────────────────────────────────────────────────────┘          │
│                                                                     │
│   ┌──────────────────────────────────────────────────────┐          │
│   │  6. LEGEND / FOOTER                                   │          │
│   └──────────────────────────────────────────────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. INPUT 1 — M1 Declaration Store (required)

**SVG region:** Left input box (x=18..432, y=54..168), solid border `#1a4fa0`

**What it represents:** The frozen `DeclarationStore` produced by Module 1 (SDK). This is the primary and always-consumed input to Module 4. It carries all column, group, relationship, pattern, and realism declarations accumulated during the SDK session.

**Responsible file:** `phase_2/types.py` → `DeclarationStore`

| | Detail |
|---|---|
| **Input** | `DeclarationStore` instance (frozen), containing 9 registries listed in the SVG box |
| **Output** | Individual registries unpacked and passed as arguments to `build_schema_metadata()` |
| **Data flow** | `DeclarationStore` → `FactTableSimulator.generate()` → `run_pipeline(columns, groups, ...)` → `build_schema_metadata(groups, orthogonal_pairs, ...)` |

**The 9 registries shown in SVG:**

| Registry | Type | Source attribute |
|---|---|---|
| `columns[]` | `OrderedDict[str, dict[str, Any]]` | `DeclarationStore.columns` |
| `orthogonal_pairs[]` | `list[OrthogonalPair]` | `DeclarationStore.orthogonal_pairs` |
| `groups{}` | `dict[str, DimensionGroup]` | `DeclarationStore.groups` |
| `group_dependencies[]` | `list[GroupDependency]` | `DeclarationStore.group_dependencies` |
| `measure_dag` | `dict[str, list[str]]` | `DeclarationStore.measure_dag` |
| `measure_dag_order[]` | `list[str]` | Computed at call time via `dag.extract_measure_sub_dag()` |
| `patterns[]` | `list[dict[str, Any]]` | `DeclarationStore.patterns` |
| `realism_config?` | `Optional[dict[str, Any]]` | `DeclarationStore.realism_config` |
| `target_rows` | `int` | `DeclarationStore.target_rows` |

**Call order:**
```
FactTableSimulator.generate()
  └─ engine.generator.run_pipeline(
         columns=store.columns,
         groups=store.groups,
         group_dependencies=store.group_dependencies,
         measure_dag=store.measure_dag,
         target_rows=store.target_rows,
         seed=store.seed,
         patterns=store.patterns,
         orthogonal_pairs=store.orthogonal_pairs,
     )
```

---

## 2. INPUT 2 — M2 Master DataFrame (optional)

**SVG region:** Right input box (x=444..852, y=54..168), dashed border `#888`

**What it represents:** The `pd.DataFrame` produced by Module 2 (Engine). This input is optional — the SVG marks it with a dashed border and notes "declaration store alone is usually sufficient." In the current implementation, `build_schema_metadata()` does **not** accept a DataFrame parameter; empirical stats enrichment is a documented future extension.

**Responsible file:** `phase_2/engine/generator.py` → `run_pipeline()` (produces the DataFrame)

| | Detail |
|---|---|
| **Input** | `pd.DataFrame` with all generated rows + columns from M2 pipeline |
| **Output** | Not currently consumed by `build_schema_metadata()` |
| **Data flow** | `run_pipeline()` produces `(df, metadata)` — the `df` flows to M5 alongside `metadata`, but does not feed back into the metadata builder |

**SVG content describes potential enrichment:**
- Per-column stats: min, max, mean, nunique, null_rate
- Row count: actual vs. target_rows cross-check
- Value ranges: used to tighten M5 L2 statistical thresholds

**SVG note:** "M2 also calls `_build_schema_metadata()` internally (Post stage). M4 may reuse or rebuild that raw dict with additional DataFrame enrichment."

**Connector between inputs (y≈179):** The SVG labels the two arrows: "solid = required, dashed = optional" — reinforcing that only the Declaration Store is consumed in the current implementation.

---

## 3. §2.6 Schema Metadata Builder

**SVG region:** Main processing box (x=18..852, y=186..440), solid border `#1a5c6e` (2px)

**What it represents:** The core metadata assembly function. Transforms internal SDK representation (DeclarationStore registries) into the external contract format (`schema_metadata` dict with 7 keys). Internally divided by a vertical line at x=470 separating required (left) from optional (right) data sources.

**Responsible file:** `phase_2/metadata/builder.py`

| | Detail |
|---|---|
| **Input** | `groups: dict[str, DimensionGroup]`, `orthogonal_pairs: list[OrthogonalPair]`, `target_rows: int`, `measure_dag_order: list[str]`, `columns: OrderedDict[str, dict] | None`, `group_dependencies: list[GroupDependency] | None`, `patterns: list[dict] | None` |
| **Output** | `dict[str, Any]` — the `schema_metadata` dict with 7 top-level keys |
| **Data flow** | `run_pipeline()` (line 118) → `build_schema_metadata()` → returns `metadata` as second element of the `(df, metadata)` tuple |

### Left Half — From Declaration Store (required)

**SVG region:** Left of vertical divider (x=18..470, y=214..370)

The SVG shows 7 labeled subsections corresponding to data extracted from the Declaration Store:

| SVG Badge | Description | Builder code |
|---|---|---|
| "per column" | name, type, role, group, parent, family, param_model, formula? | `_build_columns_metadata(columns)` → key 4: `columns` |
| "group structure" | dimension groups: root col, member cols, group type | `group.to_metadata()` → key 1: `dimension_groups` |
| "measure DAG" | topo order, dependency edges, formula map | `list(measure_dag_order)` → key 5: `measure_dag_order` |
| "pattern catalog" | pattern type, target column, parameters per entry | List comprehension → key 6: `patterns` |
| "constraints" | orthogonal pairs, cross-group dependencies | `pair.to_metadata()` / `dep.to_metadata()` → keys 2, 3 |
| "realism config" | missing_rate, dirty_rate, censored_rate | Not serialized into metadata (consumed by engine only) |
| "target_rows" | expected row count | Direct assignment → key 7: `total_rows` |

**SVG annotation (y≈384):** "→ all fields serialized into schema_metadata dict keys"

### Right Half — From Master DataFrame (optional)

**SVG region:** Right of vertical divider (x=470..852, y=214..370)

| SVG Badge | Description | Current status |
|---|---|---|
| "per-col stats" | min, max, mean, nunique, null_rate | Not implemented — future enrichment |
| "row count" | actual vs target_rows cross-check | Not implemented |
| "value ranges" | used to tighten M5 L2 statistical thresholds | Not implemented |

**SVG notes (y≈332..401):**
- "Enriches `df_stats` key of schema_metadata dict when present; key is absent if DataFrame unused"
- "Note: M2 also calls `_build_schema_metadata()` internally (Post stage). M4 may reuse or rebuild that raw dict with additional DataFrame enrichment."

### Internal Call Order

```
build_schema_metadata(groups, orthogonal_pairs, target_rows, measure_dag_order,
                      columns, group_dependencies, patterns)        [builder.py:23]
  │
  ├─ Key 1: dimension_groups
  │   └─ for group_name, group in groups.items():
  │       └─ group.to_metadata()                                    [types.py:59]
  │            └─ returns {"columns": list(...), "hierarchy": list(...)}
  │
  ├─ Key 2: orthogonal_groups
  │   └─ [pair.to_metadata() for pair in orthogonal_pairs]          [types.py:139]
  │        └─ returns {"group_a": ..., "group_b": ..., "rationale": ...}
  │
  ├─ Key 3: group_dependencies
  │   └─ [dep.to_metadata() for dep in group_dependencies]          [types.py:203]
  │        └─ returns {"child_root": ..., "on": [...], "conditional_weights": {...}}
  │
  ├─ Key 4: columns
  │   └─ _build_columns_metadata(columns)                           [builder.py:114]
  │        └─ for col_name, col_meta in columns.items():
  │             ├─ categorical → {type, values, weights, cardinality, group, parent}
  │             ├─ temporal → {type, start, end, freq, derive, group}
  │             ├─ temporal_derived → {type, derivation, source, group}
  │             ├─ measure/stochastic → {type, measure_type, family, param_model}
  │             │   └─ _deep_copy_param_model(pm)                   [builder.py:178]
  │             └─ measure/structural → {type, measure_type, formula, effects, noise}
  │
  ├─ Key 5: measure_dag_order
  │   └─ list(measure_dag_order)                                    [builder.py:85]
  │
  ├─ Key 6: patterns
  │   └─ [{type, target, col, params} for p in patterns]            [builder.py:88]
  │
  ├─ Key 7: total_rows
  │   └─ target_rows (direct assignment)                            [builder.py:102]
  │
  └─ _assert_metadata_consistency(metadata)                         [builder.py:194]
       ├─ Check: dimension_groups columns ⊆ columns metadata        [builder.py:215]
       ├─ Check: measure_dag_order entries ∈ columns                 [builder.py:225]
       ├─ Check: pattern cols are measures                           [builder.py:234]
       └─ Check: orthogonal_groups reference valid groups            [builder.py:244]
```

**SVG output annotation (y≈412..428):** "Output: schema_metadata (dict) — passed to M5 Validation"

---

## 4. schema_metadata Dict Structure

**SVG region:** Reference table box (x=80..790, y=458..596), solid border `#8B7000` (gold)

**What it represents:** A compact specification of the 7 top-level keys in the output dictionary, showing exact key names and value type/shape. This is a documentation reference, not a processing step.

**Responsible file:** `phase_2/metadata/builder.py` → `build_schema_metadata()` return value

| Key | Value Type / Shape | Builder line |
|---|---|---|
| `dimension_groups` | `{ group_name: {columns: [...], hierarchy: [...]} }` | 60–63 |
| `orthogonal_groups` | `[ {group_a, group_b, rationale} ... ]` | 66–68 |
| `group_dependencies` | `[ {child_root, on, conditional_weights} ... ]` | 71–76 |
| `columns` | `{ col_name: {type, values?, weights?, family?, param_model?, formula?, effects?, noise?} }` | 79–82 |
| `measure_dag_order` | `[ measure_name ... ]` (topological sort of measure dependency graph) | 85 |
| `patterns` | `[ {type, target, col, params} ... ]` | 88–99 |
| `total_rows` | `int` (declared `target_rows` from §2.1 Constructor) | 102 |

### Column Descriptor Type Discrimination

The `columns` key contains type-discriminated descriptors built by `_build_columns_metadata()` (builder.py:114–175):

| Column type | Descriptor fields | Deep-copied? |
|---|---|---|
| `categorical` | type, values, weights, cardinality, group, parent | values list copied |
| `temporal` | type, start, end, freq, derive, group | derive list copied |
| `temporal_derived` | type, derivation, source, group | — |
| `measure` (stochastic) | type, measure_type, family, param_model | param_model deep-copied via `_deep_copy_param_model()` |
| `measure` (structural) | type, measure_type, formula, effects, noise | effects and noise dict-copied |

**Design decision — defensive copying:** All nested dicts (param_model, effects, noise, conditional_weights) are deep-copied to prevent downstream mutation of the returned metadata from corrupting the source column registry. `_deep_copy_param_model()` (builder.py:178–191) handles both scalar and intercept+effects forms.

---

## 5. M5 Validation Engine (Output Destination)

**SVG region:** Bottom box (x=268..602, y=614..666), solid border `#a01a1a` (red)

**What it represents:** The downstream consumer of the `schema_metadata` dict. Module 5 receives this dict alongside the Master DataFrame from M2 and uses it to drive three layers of validation checks.

**Responsible files:**
- `phase_2/validation/validator.py` — `SchemaAwareValidator(meta).validate(df, patterns)`
- `phase_2/validation/structural.py` — L1 checks (cardinality, weights, finiteness)
- `phase_2/validation/statistical.py` — L2 checks (KS-test, residuals, dependency transitions)
- `phase_2/validation/pattern_checks.py` — L3 checks (outlier z-score, trend break, ranking reversal)

| | Detail |
|---|---|
| **Input** | `schema_metadata: dict` (from §2.6) + `df: pd.DataFrame` (from M2) |
| **Output** | `ValidationReport` containing `Check` objects |
| **Data flow** | `run_pipeline()` returns `(df, metadata)` → `pipeline._run_loop_b()` passes both to `generate_with_validation()` → `SchemaAwareValidator(metadata).validate(df, patterns)` |

**SVG body text:**
- "Receives schema_metadata alongside Master DataFrame from M2"
- "Uses dict to drive L1 structural, L2 statistical, L3 pattern checks"

**How M5 uses each metadata key:**

| Metadata key | M5 usage |
|---|---|
| `dimension_groups` | L1: cardinality checks, hierarchy validation |
| `orthogonal_groups` | L1: χ² independence test between declared-orthogonal groups |
| `group_dependencies` | L2: conditional transition deviation checks |
| `columns` | L1: marginal weight checks, measure finiteness; L2: KS-test parameterization |
| `measure_dag_order` | L1: DAG acyclicity verification; L2: processing order for residual checks |
| `patterns` | L3: pattern-specific checks (outlier z-score, trend break, ranking reversal) |
| `total_rows` | L1: row count check |

---

## 6. Legend / Footer

**SVG region:** Bottom bar (x=18..852, y=678..714), light gray border

**What it represents:** Symbol key and one-line flow summary.

**Symbols:**
- Solid arrow (dark blue `#1a4fa0`): required input
- Dashed arrow (gray `#888`): optional input (possibly unused)
- Dashed box border: optional / conditional component
- Note: "7 keys match implementation in `metadata/builder.py`"

**Flow summary:** "M1 decl store → §2.6 assembles schema_metadata dict (7 keys) → M5 Validation (alongside M2 DataFrame)"

---

## Complete File Responsibility Map

| SVG Section | Primary File | Supporting Files |
|---|---|---|
| 1. INPUT 1 — M1 Declaration Store | `types.py` (`DeclarationStore`) | `sdk/simulator.py`, `sdk/columns.py`, `sdk/relationships.py` |
| 2. INPUT 2 — M2 Master DataFrame | `engine/generator.py` (`run_pipeline`) | `engine/skeleton.py`, `engine/measures.py`, `engine/postprocess.py` |
| 3. §2.6 Schema Metadata Builder | `metadata/builder.py` | `types.py` (`DimensionGroup.to_metadata`, `OrthogonalPair.to_metadata`, `GroupDependency.to_metadata`) |
| 4. schema_metadata dict structure | `metadata/builder.py` | — |
| 5. M5 Validation Engine | `validation/validator.py` | `validation/structural.py`, `validation/statistical.py`, `validation/pattern_checks.py` |
| 6. Legend / Footer | — | — |

---

## End-to-End Call Trace

```
engine.generator.run_pipeline(columns, groups, group_dependencies,
                              measure_dag, target_rows, seed,
                              patterns, realism_config, overrides,
                              orthogonal_pairs)
│
├─ [Phases α–δ: skeleton → measures → patterns → realism → df]
│
├─ Compute measure_dag_order for metadata:
│   ├─ measure_names = {col for col in columns if type == "measure"}
│   └─ dag.extract_measure_sub_dag(full_dag, measure_names)         [sdk/dag.py:158]
│       └─ topological_sort(measure_adjacency)                       [sdk/dag.py:105]
│            └─ returns measure_order: list[str]
│
└─ metadata.builder.build_schema_metadata(                           [metadata/builder.py:23]
       groups, orthogonal_pairs, target_rows,
       measure_dag_order, columns, group_dependencies, patterns)
    │
    ├─ Key 1: dimension_groups
    │   └─ groups[name].to_metadata()                                [types.py:59]
    │        └─ {"columns": list(self.columns), "hierarchy": list(self.hierarchy)}
    │
    ├─ Key 2: orthogonal_groups
    │   └─ pair.to_metadata()                                        [types.py:139]
    │        └─ {"group_a": ..., "group_b": ..., "rationale": ...}
    │
    ├─ Key 3: group_dependencies
    │   └─ dep.to_metadata()                                         [types.py:203]
    │        └─ {"child_root": ..., "on": list(...), "conditional_weights": {k: dict(v)}}
    │
    ├─ Key 4: columns
    │   └─ _build_columns_metadata(columns)                          [builder.py:114]
    │        └─ for each column, type-discriminated enrichment:
    │             ├─ "categorical" → {type, values, weights, cardinality, group, parent}
    │             ├─ "temporal"    → {type, start, end, freq, derive, group}
    │             ├─ "temporal_derived" → {type, derivation, source, group}
    │             ├─ "measure" stochastic:
    │             │   ├─ {type, measure_type, family, param_model}
    │             │   └─ _deep_copy_param_model(pm)                  [builder.py:178]
    │             │        └─ nested dict copy, handles intercept+effects form
    │             └─ "measure" structural:
    │                 └─ {type, measure_type, formula, effects (copied), noise (copied)}
    │
    ├─ Key 5: measure_dag_order → list(measure_dag_order)            [builder.py:85]
    │
    ├─ Key 6: patterns → [{type, target, col, params} ...]           [builder.py:88]
    │
    ├─ Key 7: total_rows → target_rows                               [builder.py:102]
    │
    └─ _assert_metadata_consistency(metadata)                        [builder.py:194]
         ├─ dim_groups columns ⊆ columns metadata?                   [builder.py:215]
         │    └─ warning if column in group not found in columns dict
         ├─ measure_dag_order ⊆ columns?                             [builder.py:225]
         │    └─ warning if measure name not found in columns dict
         ├─ pattern cols are measures?                                [builder.py:234]
         │    └─ warning if pattern.col is not type=="measure"
         └─ orthogonal_groups ⊆ dimension_groups?                    [builder.py:244]
              └─ warning if group_a or group_b not in dim_groups

→ returns metadata: dict[str, Any] (7 keys)
→ run_pipeline() returns (df, metadata)
    └─ pipeline._run_loop_b() receives metadata
         └─ validation.generate_with_validation(build_fn, metadata)
              └─ SchemaAwareValidator(metadata).validate(df, patterns)
                   ├─ structural.run_l1_checks(df, metadata)
                   ├─ statistical.run_l2_checks(df, metadata)
                   └─ pattern_checks.run_l3_checks(df, metadata)
```
