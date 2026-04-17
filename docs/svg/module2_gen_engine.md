# Module 2: Generation Engine — SVG Flow Diagram Guide

**SVG file:** `module2_gen_engine.svg`
**Source of truth:** `docs/artifacts/stage5_anatomy_summary.md` — Module: Generation Engine (M2)
**Implementation:** `phase_2/engine/`

---

## SVG Section Map

The SVG uses two parallel vertical flows through a single-column pipeline:

- **Left flow** (x≈260): Data — rows dict through α/β, then DataFrame through τ_post/γ/δ
- **Right flow** (x≈600): RNG — a single `np.random.Generator` object threaded α→β→γ→δ (bypassing τ_post)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  EXTERNAL INPUTS  —  from M1 Frozen Declaration Store       │   │
│   └──────────────────────────┬──────────────────────────────────┘   │
│                              │                                      │
│   ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┴─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐   │
│   │  §2.4 CONCEPTUAL ALGORITHM  ⟨ no runtime artifact ⟩        │   │
│   └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┬─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘   │
│                         «implements»                                │
│   ┌═════════════════════════════════════════════════════════════┐   │
│   ║  §2.8  generate()  Pipeline                                ║   │
│   ║                                                             ║   │
│   ║  ┌─────────────────────────────────────────────────────┐    ║   │
│   ║  │  PRE-FLIGHT         rng: CREATES                    │    ║   │
│   ║  └────────────┬──────────────────────────┬─────────────┘    ║   │
│   ║          topo_order                    rng (initial)        ║   │
│   ║               │                          │                  ║   │
│   ║  ┌────────────▼──────────────────────────▼─────────────┐    ║   │
│   ║  │  STAGE α — build_skeleton()         rng: USES ✓     │    ║   │
│   ║  └────────────┬──────────────────────────┬─────────────┘    ║   │
│   ║          rows (partial)            rng (advanced by α)     ║   │
│   ║               │                          │                  ║   │
│   ║  ┌────────────▼──────────────────────────▼─────────────┐    ║   │
│   ║  │  STAGE β — Measure generation       rng: USES ✓     │    ║   │
│   ║  └────────────┬──────────────────────────┬─────────────┘    ║   │
│   ║          rows (complete)           rng (advanced by β)     ║   │
│   ║               │                          ┊ (bypasses)      ║   │
│   ║  ┌────────────▼─────────────────────────────────────────┐   ║   │
│   ║  │  τ_post — to_dataframe(rows)        rng: NOT USED ✗  │   ║   │
│   ║  └────────────┬─────────────────────────────────────────┘   ║   │
│   ║          df : pd.DataFrame         rng (state from β)      ║   │
│   ║               │                          │                  ║   │
│   ║  ┌────────────▼──────────────────────────▼─────────────┐    ║   │
│   ║  │  STAGE γ — inject_patterns(df)      rng: PASSED ⚠   │    ║   │
│   ║  └────────────┬──────────────────────────┬─────────────┘    ║   │
│   ║          df (patterns injected)    rng (from β)            ║   │
│   ║               │                          │                  ║   │
│   ║  ┌ ─ ─ ─ ─ ─ ▼ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─▼ ─ ─ ─ ─ ─ ─┐   ║   │
│   ║  │  STAGE δ — inject_realism(df) ⟨optional⟩ rng: USES ✓│   ║   │
│   ║  └ ─ ─ ─ ─ ─ ┬ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┬─ ─ ─ ─ ─ ─ ┘   ║   │
│   ║          df (with imperfections)     rng ──┤ (terminated)  ║   │
│   ║               │                                             ║   │
│   ║  ┌────────────▼────────────────────────────────────────┐    ║   │
│   ║  │  METADATA — build_schema_metadata()                  │    ║   │
│   ║  └────────────┬────────────────────────────────────────┘    ║   │
│   ║               │                                             ║   │
│   ╚═══════════════╪═════════════════════════════════════════════╝   │
│                   │                                                 │
│   ┌───────────────▼──────────────┐  ┌──────────────────────────┐   │
│   │  MODULE OUTPUTS              │  │  FEEDBACK INPUT ⟵ M5     │   │
│   │  → M5: DataFrame             │  │  Loop B: adjusted params │◄──┤
│   │  → M4: schema_metadata       │  │  + new seed              │   │
│   └──────────────────────────────┘  └──────────────────────────┘   │
│                                                        ▲           │
│                                    Loop B ─────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. EXTERNAL INPUTS

**SVG region:** Top box (y=54..162), light blue fill `#f0f4ff`, dark blue stroke `#1a4fa0`

**What it represents:** The frozen declaration state from M1 that enters Module 2. These inputs are produced by `FactTableSimulator.generate()` after freezing the `DeclarationStore`.

**Responsible file:** `phase_2/engine/generator.py` — received as parameters to `run_pipeline()`

| | Detail |
|---|---|
| **Input** | 6 artifacts from M1's frozen `DeclarationStore` |
| **Output** | Same values, passed into §2.8 pipeline as `run_pipeline()` parameters |
| **Data flow** | `FactTableSimulator.generate()` freezes store → extracts fields → calls `run_pipeline(...)` |

**The 6 input artifacts** (shown as two columns of bullet points in SVG):

| Artifact | Parameter in `run_pipeline()` | Type |
|----------|-------------------------------|------|
| columns | `columns` | `OrderedDict[str, dict[str, Any]]` |
| dimension-group graph | `groups` | `dict[str, DimensionGroup]` |
| measure DAG edges + measure_dag_order | `measure_dag` | `dict[str, list[str]]` |
| pattern list | `patterns` | `list[dict[str, Any]] \| None` |
| realism config | `realism_config` | `dict[str, Any] \| None` |
| seed (integer) — source of rng | `seed` | `int` |

Additional parameters not shown in SVG but present in signature: `target_rows: int`, `overrides: dict | None`, `orthogonal_pairs: list | None`.

---

## 2. §2.4 CONCEPTUAL ALGORITHM

**SVG region:** Dashed-border box (y=182..278), gray fill `#fafafa`, stroke-dasharray 7,3

**What it represents:** An architectural specification — not a runtime artifact. Describes the unified generation DAG concept, topological layer assignment, and the row generation algorithm contract. The `«implements»` arrow (y=278..304) connects this spec to the §2.8 pipeline that realizes it.

**Responsible file:** No single file — this is the design contract implemented collectively by `sdk/dag.py` (DAG construction) and `engine/generator.py` (pipeline orchestration).

| | Detail |
|---|---|
| **Input** | N/A — architectural spec |
| **Output** | N/A — no runtime artifact |
| **Key concepts** | Full generation DAG (all column types unified); topological layer assignment; per-row loop + post-generation passes; `target_rows` contract from Phase 1 / M3 |

**SVG content (4 bullets):**
1. Full generation DAG (all column types unified) → `dag.build_full_dag()`
2. Topological layer assignment for all columns → `dag.topological_sort()`
3. Row generation algorithm — per-row loop + post-generation passes → `skeleton.build_skeleton()` + `measures.generate_measures()`
4. `target_rows` contract received from Phase 1 / M3 → `run_pipeline(target_rows=...)`

---

## 3. PRE-FLIGHT

**SVG region:** First box inside §2.8 pipeline (y=336..404), light blue fill `#f0f4ff`, stroke `#1a4fa0`. RNG badge: amber `#fff8e6` — **"rng: CREATES"**.

**What it represents:** The initialization phase — builds the unified generation DAG from all declaration sources, computes the deterministic topological order, and creates the seeded RNG object.

**Responsible files:**
- `phase_2/engine/generator.py` — `run_pipeline()` lines 74–80
- `phase_2/sdk/dag.py` — `build_full_dag()`, `topological_sort()`

| | Detail |
|---|---|
| **Input** | `columns`, `groups`, `group_dependencies`, `measure_dag`, `seed` (from external inputs) |
| **Output** | `topo_order: list[str]` + `rng: np.random.Generator` (seeded, ready for first draw) |
| **Data flow** | `run_pipeline()` → `_dag.build_full_dag()` → `_dag.topological_sort()` |

**SVG content (3 lines mapped to code):**

| SVG line | Implementation |
|----------|----------------|
| `decl store ──► _build_full_dag() ──► topo_sort() ──► topo_order` | `full_dag = _dag.build_full_dag(columns, groups, group_dependencies, measure_dag)` then `topo_order = _dag.topological_sort(full_dag)` |
| `seed ──► np.random.default_rng(seed) ──► rng` | `rng = np.random.default_rng(seed)` (generator.py:74) |
| Output: `topo_order + rng object` | These two values flow into Stage α |

**Call order:**
```
run_pipeline(columns, groups, group_dependencies, measure_dag, seed, ...)
  ├─ np.random.default_rng(seed) → rng                               # line 74
  ├─ _dag.build_full_dag(columns, groups, group_dependencies, measure_dag)
  │    └─ Merges 5 edge sources into unified adjacency dict:
  │         1. Within-group hierarchy (parent → child)
  │         2. Cross-group root dependencies (parent_root → child_root)
  │         3. Temporal derivation (temporal_root → derived)
  │         4. Measure predictor references (categorical → measure)
  │         5. Measure-measure DAG (upstream → downstream)
  │    └─ Returns: full_dag: dict[str, list[str]]
  └─ _dag.topological_sort(full_dag)
       └─ Kahn's algorithm with min-heap (lexicographic tie-breaking)
       └─ Returns: topo_order: list[str]
       └─ Raises: CyclicDependencyError if graph contains cycle
```

**Transfer zone (y=404..430):** Two parallel arrows flow into Stage α:
- Left (x=260, solid black): `topo_order`
- Right (x=600, amber dashed): `rng` with label "(state: initial)"

---

## 4. STAGE α — SKELETON

**SVG region:** Green box (y=430..526), fill `#f4faf4`, stroke `#1a6e3a`. RNG badge: **"rng: USES ✓"**.

**What it represents:** Phase α generates all non-measure columns (categorical roots, cross-group dependent roots, child categories, temporal roots, temporal derivations) by iterating the topological order and dispatching to the appropriate sampler.

**Responsible file:** `phase_2/engine/skeleton.py` — `build_skeleton()` (lines 31–102)

| | Detail |
|---|---|
| **Input** | `columns: dict`, `target_rows: int`, `group_dependencies: list[GroupDependency]`, `topo_order: list[str]`, `rng: np.random.Generator` |
| **Output** | `rows: dict[str, np.ndarray]` — all non-measure columns filled, each array of length `target_rows` |
| **Data flow** | `run_pipeline()` → `_skeleton.build_skeleton(columns, target_rows, group_dependencies, topo_order, rng)` (generator.py:83–85) |

**SVG content (5 lines) mapped to dispatch logic:**

| SVG description | Function | Lines | RNG usage |
|----------------|----------|-------|-----------|
| root categorical → sample from weights | `sample_independent_root(col_name, col_meta, target_rows, rng)` | 109–131 | `rng.choice(values_arr, size=target_rows, p=weights_arr)` |
| cross-group dep → sample \| upstream root | `sample_dependent_root(col_name, col_meta, dep, rows, target_rows, rng)` | 134–179 | `rng.choice(child_arr, size=n_matching, p=weights_for_parent)` per parent value |
| child categorical → sample \| parent value | `sample_child_category(col_name, col_meta, rows, target_rows, rng)` | 182–230 | `rng.choice()` — flat or conditional weights |
| temporal root → sample in [start, end] | `sample_temporal_root(col_name, col_meta, target_rows, rng)` | 237–289 | `rng.integers(0, len(dates_as_dt64), size=target_rows)` |
| temporal derived → extract from root (no rng) | `derive_temporal_child(col_name, col_meta, rows)` | 343–378 | None — deterministic extraction |

**Call order:**
```
_skeleton.build_skeleton(columns, target_rows, group_dependencies, topo_order, rng)
  │
  └─ For each col_name in topo_order:
     │
     ├─ if type=="categorical" and parent is None:
     │  ├─ _get_dependency_for_root(col_name, group_dependencies) → dep | None
     │  ├─ if dep is None:
     │  │  └─ sample_independent_root(col_name, col_meta, target_rows, rng)
     │  │     └─ rng.choice(values_arr, size=target_rows, p=weights_arr)
     │  └─ else:
     │     └─ sample_dependent_root(col_name, col_meta, dep, rows, target_rows, rng)
     │        └─ For each parent_val in dep.conditional_weights:
     │             mask = parent_values == parent_val
     │             rng.choice(child_arr, size=n_matching, p=normalized_weights)
     │
     ├─ elif type=="categorical" and parent is not None:
     │  └─ sample_child_category(col_name, col_meta, rows, target_rows, rng)
     │     ├─ flat weights path: rng.choice(child_arr, size=target_rows, p=weights_arr)
     │     └─ conditional path: per parent_val → rng.choice(...)
     │
     ├─ elif type=="temporal":
     │  └─ sample_temporal_root(col_name, col_meta, target_rows, rng)
     │     ├─ Parse start/end dates (ISO string or date object)
     │     ├─ Dispatch by freq:
     │     │  ├─ "D"/"daily" → enumerate_daily_dates(start, end)
     │     │  ├─ "W-*"/"weekly" → enumerate_period_dates(start, end, snap_weekday=0)
     │     │  └─ "MS"/"monthly" → enumerate_monthly_dates(start, end)
     │     ├─ dates_as_dt64 = np.array(eligible_dates, dtype="datetime64[D]")
     │     ├─ indices = rng.integers(0, len(dates_as_dt64), size=target_rows)
     │     └─ result = dates_as_dt64[indices].astype("datetime64[ns]")
     │
     ├─ elif type=="temporal_derived":
     │  └─ derive_temporal_child(col_name, col_meta, rows)
     │     ├─ parent = col_meta["source"] or col_meta["parent"]
     │     ├─ dt_index = pd.DatetimeIndex(rows[parent])
     │     └─ Dispatch by derivation:
     │        ├─ "day_of_week" → dt_index.dayofweek → int64
     │        ├─ "month" → dt_index.month → int64
     │        ├─ "quarter" → dt_index.quarter → int64
     │        └─ "is_weekend" → (dayofweek >= 5) → bool
     │
     └─ elif type=="measure": skip (handled in Stage β)

  └─ Return rows: dict[str, np.ndarray]
```

**Helper functions:**
- `_get_dependency_for_root(col_name, group_dependencies)` (lines 385–396): Looks up `GroupDependency` where `dep.child_root == col_name`
- `enumerate_daily_dates(start, end)` (lines 292–298): All dates in `[start, end]` inclusive
- `enumerate_period_dates(start, end, snap_weekday)` (lines 301–315): All dates matching a specific weekday
- `enumerate_monthly_dates(start, end)` (lines 318–340): All 1st-of-month dates

**Transfer zone (y=526..552):**
- Left: `rows` "(partial — non-measure cols filled)"
- Right: `rng` "(state: advanced by α)"

---

## 5. STAGE β — MEASURE GENERATION

**SVG region:** Orange box (y=552..640), fill `#fffaf2`, stroke `#a05c00`. RNG badge: **"rng: USES ✓"**.

**What it represents:** Phase β generates all measure columns in topological order, dispatching each to either stochastic sampling (distribution family + per-row parameters) or structural formula evaluation (restricted AST + optional noise).

**Responsible file:** `phase_2/engine/measures.py` — `generate_measures()` (lines 413–464)

| | Detail |
|---|---|
| **Input** | `columns: dict`, `topo_order: list[str]`, `rows: dict[str, np.ndarray]`, `rng: np.random.Generator`, `overrides: dict \| None` |
| **Output** | `rows: dict[str, np.ndarray]` — updated in place with measure columns populated |
| **Data flow** | `run_pipeline()` → `_measures.generate_measures(columns, topo_order, rows, rng, overrides)` (generator.py:88–90) |

**SVG content mapped to dispatch:**

| SVG description | Function | Lines |
|----------------|----------|-------|
| stochastic → `_sample_stochastic(col, rows, rng)` | `_sample_stochastic(col_name, col_meta, rows, rng, overrides)` | 266–336 |
| `params = intercept + Σ effects → draw from family(params) [rng]` | `_compute_per_row_params()` (339–406) then family dispatch (320–336) | |
| structural → `_eval_structural(col, rows, rng)` | `_eval_structural(col_name, col_meta, rows, rng, columns, overrides)` | 179–259 |
| `evaluate formula with upstream values → add noise term [rng]` | `_safe_eval_formula()` (39–105) + `rng.normal(0, sigma)` noise (254–257) | |

**Call order:**
```
_measures.generate_measures(columns, topo_order, rows, rng, overrides)
  │
  ├─ For each col_name in topo_order where type=="measure":
  │  │
  │  ├─ if measure_type=="stochastic":
  │  │  └─ _sample_stochastic(col_name, col_meta, rows, rng, overrides)
  │  │     ├─ _compute_per_row_params(col_name, col_meta, rows, n_rows, overrides)
  │  │     │  └─ For each (param_key, value) in param_model:
  │  │     │     ├─ scalar → np.full(n_rows, float(value))
  │  │     │     └─ dict → intercept + Σ effects per row
  │  │     │        ├─ theta = np.full(n_rows, intercept)
  │  │     │        └─ For each (effect_col, effect_map):
  │  │     │             mask = rows[effect_col] == cat_val
  │  │     │             theta[mask] += effect_value
  │  │     │  ├─ Apply overrides: theta *= float(col_overrides[param_key])
  │  │     │  └─ Clamp: sigma/scale ≥ 1e-6, rate ≥ 1e-6  (P3-1)
  │  │     │
  │  │     └─ Dispatch by family:
  │  │        ├─ "gaussian"    → rng.normal(mu, sigma)
  │  │        ├─ "lognormal"   → rng.lognormal(mu, sigma)
  │  │        ├─ "gamma"       → rng.gamma(shape=mu, scale=sigma)
  │  │        ├─ "beta"        → rng.beta(mu, sigma)
  │  │        ├─ "uniform"     → rng.uniform(mu, sigma)
  │  │        ├─ "poisson"     → rng.poisson(mu).astype(float64)
  │  │        ├─ "exponential" → rng.exponential(1.0 / rate)
  │  │        └─ "mixture"     → NotImplementedError (P1-1 deferred)
  │  │
  │  └─ elif measure_type=="structural":
  │     └─ _eval_structural(col_name, col_meta, rows, rng, columns, overrides)
  │        ├─ Pre-compute effect_col_map: effect_name → (cat_col, val_map)
  │        ├─ Extract formula_symbols via ast.walk()
  │        ├─ measure_symbols = formula_symbols − effect_names
  │        │
  │        ├─ For each row i:
  │        │  ├─ Resolve effects: context[effect_name] = val_map[rows[cat_col][i]]
  │        │  ├─ Add measure refs: context[sym] = float(rows[sym][i])
  │        │  └─ values[i] = _safe_eval_formula(formula, context)
  │        │     └─ Restricted AST walker: +, −, ×, ÷, ** only
  │        │        Allowed nodes: Expression, BinOp, UnaryOp(USub), Constant, Name
  │        │
  │        └─ Apply noise (P3-10): values += rng.normal(0, sigma, size=n_rows)
  │
  └─ Handle reshuffle overrides (P0-3):
     └─ For each col in overrides["reshuffle"]:
          rows[col] = rng.permutation(rows[col])

  └─ Return rows (updated with measures)
```

**Transfer zone (y=640..662):**
- Left: `rows` "(complete — all cols populated)"
- Right: `rng` "(state: advanced by β — bypasses τ_post)"

---

## 6. τ_post — POST-PROCESSING (DataFrame assembly)

**SVG region:** Purple box (y=662..720), fill `#f8f4ff`, stroke `#5c2d91`. RNG badge: **"rng: NOT USED ✗"** (gray).

**What it represents:** Converts the `rows` dict of numpy arrays into a typed `pd.DataFrame`. This runs **between** Stage β and Stage γ (generator.py:93), so that subsequent stages (pattern injection, realism injection) operate on a DataFrame rather than a raw dict. Metadata assembly occurs later, after all pipeline stages complete.

**Responsible file:** `phase_2/engine/postprocess.py` — `to_dataframe()` (lines 19–82)

| | Detail |
|---|---|
| **Input** | `rows: dict[str, np.ndarray]`, `topo_order: list[str]`, `columns: dict`, `target_rows: int` |
| **Output** | `df: pd.DataFrame` (typed, column-ordered) |
| **Data flow** | `run_pipeline()` → `_postprocess.to_dataframe(rows, topo_order, columns, target_rows)` (generator.py:93) |

**Call order:**
```
_postprocess.to_dataframe(rows, topo_order, columns, target_rows)
  ├─ ordered_cols = [col for col in topo_order if col in rows]
  ├─ df = pd.DataFrame({col: rows[col] for col in ordered_cols}, index=range(target_rows))
  └─ For each col_name in ordered_cols:
     ├─ categorical  → df[col].astype(object)
     ├─ temporal     → pd.to_datetime(df[col])
     ├─ temporal_derived:
     │  ├─ "is_weekend" → df[col].astype(bool)
     │  └─ others       → df[col].astype(np.int64)
     └─ measure      → (already float64 from numpy)
  └─ Return df: pd.DataFrame
```

**Transfer zone (y=720..742):**
- Left: `df : pd.DataFrame` "(typed, column-ordered)"
- Right: `rng` "(state: advanced by β — rng bypasses τ_post)"

---

## 7. STAGE γ — PATTERN INJECTION

**SVG region:** Teal box (y=742..810), fill `#f0fafa`, stroke `#1a5c6e`. RNG badge: **"rng: PASSED ⚠"** — rng is accepted in the function signature but not consumed by current pattern implementations (`outlier_entity` and `trend_break` are deterministic). Reserved for future pattern types.

**What it represents:** Phase γ applies declared analytical patterns (outlier entities, trend breaks) to the fully populated DataFrame. Patterns compose by sequential mutation — later patterns overwrite earlier ones on overlapping cells.

**Responsible file:** `phase_2/engine/patterns.py` — `inject_patterns()` (lines 29–86)

| | Detail |
|---|---|
| **Input** | `df: pd.DataFrame`, `patterns: list[dict[str, Any]]`, `columns: dict`, `rng: np.random.Generator` |
| **Output** | `df: pd.DataFrame` with pattern transformations applied |
| **Data flow** | `run_pipeline()` → `_patterns_mod.inject_patterns(df, patterns, columns, rng)` (generator.py:97–98, conditional on `if patterns`) |

**Pattern type dispatch:**

| Pattern type | Function | Lines | Status |
|-------------|----------|-------|--------|
| `outlier_entity` | `inject_outlier_entity(df, pattern)` | 89–157 | Implemented |
| `trend_break` | `inject_trend_break(df, pattern, columns)` | 160–241 | Implemented |
| `ranking_reversal` | — | — | Deferred (M1-NC-6) |
| `dominance_shift` | — | — | Deferred (M1-NC-6) |
| `convergence` | — | — | Deferred (M1-NC-6) |
| `seasonal_anomaly` | — | — | Deferred (M1-NC-6) |

**Call order:**
```
_patterns_mod.inject_patterns(df, patterns, columns, rng)
  │
  └─ For each pattern in patterns:
     │
     ├─ if type=="outlier_entity":
     │  └─ inject_outlier_entity(df, pattern)
     │     ├─ target_mask = df.eval(pattern["target"])
     │     ├─ global_mean = df[col].mean()
     │     ├─ global_std = df[col].std()
     │     ├─ desired_mean = global_mean + z_score × global_std
     │     ├─ shift = desired_mean − current_subset_mean
     │     └─ df.loc[target_idx, col] += shift
     │
     └─ elif type=="trend_break":
        └─ inject_trend_break(df, pattern, columns)
           ├─ temporal_col = first col where type=="temporal"
           ├─ break_point = pd.to_datetime(pattern["params"]["break_point"])
           ├─ post_break_mask = target_mask & (temporal_values >= break_point)
           └─ df.loc[post_break_idx, col] *= (1.0 + magnitude)

  └─ Return df
```

**Transfer zone (y=810..832):**
- Left: `df` "(patterns injected)"
- Right: `rng` "(state: from β — current pattern types are deterministic)"

---

## 8. STAGE δ — REALISM INJECTION (optional)

**SVG region:** Dashed-border gray box (y=832..898), fill `#f8f8f8`, stroke `#666666`, stroke-dasharray 7,3 — **dashed border indicates optional stage**. Label: "⟨ optional: only runs if realism_config is set ⟩". RNG badge: **"rng: USES ✓"**.

**What it represents:** Phase δ injects controlled imperfections — missing values (NaN) and dirty values (character-level perturbations on categoricals). Only runs if `realism_config` is provided.

**Responsible file:** `phase_2/engine/realism.py` — `inject_realism()` (lines 25–65)

| | Detail |
|---|---|
| **Input** | `df: pd.DataFrame`, `realism_config: dict[str, Any]`, `columns: dict`, `rng: np.random.Generator` |
| **Output** | `df: pd.DataFrame` with controlled imperfections |
| **Data flow** | `run_pipeline()` → `_realism_mod.inject_realism(df, realism_config, columns, rng)` (generator.py:102–103, conditional on `if realism_config is not None`) |

**Call order:**
```
_realism_mod.inject_realism(df, realism_config, columns, rng)
  │
  ├─ missing_rate = realism_config.get("missing_rate", 0.0)
  ├─ dirty_rate = realism_config.get("dirty_rate", 0.0)
  │
  ├─ if missing_rate > 0:
  │  └─ inject_missing_values(df, missing_rate, rng)         [lines 68–100]
  │     ├─ mask = rng.random(size=df.shape) < missing_rate
  │     └─ df = df.mask(mask)
  │
  ├─ if dirty_rate > 0:
  │  └─ inject_dirty_values(df, columns, dirty_rate, rng)    [lines 103–164]
  │     └─ For each categorical column:
  │        ├─ selection_mask = rng.random(size=n_valid) < dirty_rate
  │        └─ For each selected cell:
  │             perturb_string(original, rng)                 [lines 167–205]
  │               ├─ type 0: swap adjacent chars   (rng.integers)
  │               ├─ type 1: delete one char       (rng.integers)
  │               └─ type 2: insert random letter  (rng.integers × 2)
  │
  └─ if censoring is not None:
     └─ NotImplementedError (M1-NC-7 deferred)

  └─ Return df
```

**RNG termination (y=898..916):** The SVG shows the rng flow ending with a T-cap symbol after Stage δ. This marks the boundary: all stochastic operations are complete. Metadata assembly is purely deterministic.

---

## 9. MODULE OUTPUTS + FEEDBACK INPUT

**SVG region:** Two side-by-side boxes (y=959..1021):
- **Left (x=18..486):** Green box, "MODULE OUTPUTS"
- **Right (x=498..854):** Red dashed-border box, "FEEDBACK INPUT ⟵ M5 Validation"
- **Right margin (x=854..866):** Red dashed feedback arc looping from y=990 back up to y=614

**What it represents:** The two outputs of Module 2 and the feedback loop from M5 Validation.

**Responsible file:** `phase_2/engine/generator.py` — `run_pipeline()` return (line 133)

### Module Outputs

| Output | Type | Consumer |
|--------|------|----------|
| Master DataFrame | `pd.DataFrame` | → M5 Validation Engine |
| schema_metadata | `dict[str, Any]` (7 keys) | → M4 Schema Meta / M5 |

### Feedback Input (Loop B)

| | Detail |
|---|---|
| **Source** | M5 Validation Engine (via `pipeline._run_loop_b()`) |
| **Mechanism** | Loop B — max 3 retries: adjusted params + new seed |
| **Seed formula** | `seed on attempt k = 42 + k` → triggers full re-run of §2.8 |
| **Override path** | `overrides` parameter in `run_pipeline()` → flows to `_compute_per_row_params()` (multiplicative scaling) and `generate_measures()` (reshuffle) |

The feedback arc in the SVG (right margin, red dashed, labeled "Loop B — max 3 retries") shows that M5 validation failures trigger a complete re-execution of the §2.8 pipeline with a new seed and parameter overrides, bypassing M3 (no LLM involvement in Loop B).

---

## Complete File Responsibility Map

| SVG Section | Primary File | Supporting Files |
|---|---|---|
| 1. External Inputs | `engine/generator.py` | `types.py` (`DimensionGroup`, `GroupDependency`) |
| 2. §2.4 Conceptual Algorithm | — (architectural spec) | `sdk/dag.py`, `engine/generator.py` |
| 3. Pre-flight | `engine/generator.py` | `sdk/dag.py` (`build_full_dag`, `topological_sort`) |
| 4. Stage α — Skeleton | `engine/skeleton.py` | `types.py` (`GroupDependency`), `exceptions.py` |
| 5. Stage β — Measures | `engine/measures.py` | `exceptions.py` |
| 6. τ_post — Post-processing | `engine/postprocess.py` | — |
| 7. Stage γ — Patterns | `engine/patterns.py` | `exceptions.py` (`PatternInjectionError`, `DegenerateDistributionError`) |
| 8. Stage δ — Realism | `engine/realism.py` | `exceptions.py` |
| 9. Module Outputs | `engine/generator.py` | `metadata/builder.py`, `sdk/dag.py` (`extract_measure_sub_dag`), `types.py` (`OrthogonalPair`) |
| 9. Feedback Input | `pipeline.py` | `engine/generator.py` (re-invoked with `overrides`) |

---

## End-to-End Call Trace

```
engine.generator.run_pipeline(
    columns, groups, group_dependencies, measure_dag,
    target_rows, seed, patterns, realism_config, overrides, orthogonal_pairs
)
│
├─ rng = np.random.default_rng(seed)                                    # PRE-FLIGHT
│
├─ full_dag = sdk.dag.build_full_dag(                                   # PRE-FLIGHT
│      columns, groups, group_dependencies, measure_dag)
│    └─ Merges 5 edge sources → unified adjacency dict
│
├─ topo_order = sdk.dag.topological_sort(full_dag)                      # PRE-FLIGHT
│    └─ Kahn's algorithm, lexicographic tie-breaking
│    └─ Raises CyclicDependencyError on cycle
│
├─ rows = engine.skeleton.build_skeleton(                               # STAGE α
│      columns, target_rows, group_dependencies, topo_order, rng)
│    │
│    └─ For each col_name in topo_order:
│       ├─ type=="categorical", parent is None, no dep:
│       │  └─ sample_independent_root()    → rng.choice()
│       ├─ type=="categorical", parent is None, has dep:
│       │  └─ sample_dependent_root()      → rng.choice() per parent_val
│       ├─ type=="categorical", parent exists:
│       │  └─ sample_child_category()      → rng.choice() (flat or conditional)
│       ├─ type=="temporal":
│       │  └─ sample_temporal_root()       → rng.integers()
│       │     ├─ "daily"   → enumerate_daily_dates()
│       │     ├─ "weekly"  → enumerate_period_dates()
│       │     └─ "monthly" → enumerate_monthly_dates()
│       ├─ type=="temporal_derived":
│       │  └─ derive_temporal_child()      → deterministic (no rng)
│       └─ type=="measure": skip
│
├─ rows = engine.measures.generate_measures(                            # STAGE β
│      columns, topo_order, rows, rng, overrides)
│    │
│    ├─ For each measure in topo_order:
│    │  ├─ measure_type=="stochastic":
│    │  │  └─ _sample_stochastic(col_name, col_meta, rows, rng, overrides)
│    │  │     ├─ _compute_per_row_params()
│    │  │     │  └─ intercept + Σ effects → theta per row
│    │  │     │  └─ Apply overrides (multiplicative), clamp (P3-1)
│    │  │     └─ Family dispatch → rng.normal / rng.lognormal / rng.gamma /
│    │  │                          rng.beta / rng.uniform / rng.poisson /
│    │  │                          rng.exponential
│    │  │
│    │  └─ measure_type=="structural":
│    │     └─ _eval_structural(col_name, col_meta, rows, rng, columns, overrides)
│    │        ├─ Pre-compute effect_col_map
│    │        ├─ Per row: resolve effects + measure refs → context
│    │        ├─ _safe_eval_formula(formula, context) → restricted AST eval
│    │        └─ Noise: values += rng.normal(0, sigma)
│    │
│    └─ Reshuffle overrides: rng.permutation() per flagged column
│
├─ df = engine.postprocess.to_dataframe(                                # POST (τ_post)
│      rows, topo_order, columns, target_rows)
│    └─ DataFrame assembly + dtype casting
│
├─ if patterns:                                                         # STAGE γ
│  └─ df = engine.patterns.inject_patterns(df, patterns, columns, rng)
│     ├─ "outlier_entity" → inject_outlier_entity()
│     │    └─ mean-shift by z_score × global_std
│     └─ "trend_break" → inject_trend_break()
│          └─ scale post-break values by (1 + magnitude)
│
├─ if realism_config is not None:                                       # STAGE δ
│  └─ df = engine.realism.inject_realism(df, realism_config, columns, rng)
│     ├─ inject_missing_values()  → rng.random() < missing_rate → df.mask()
│     └─ inject_dirty_values()    → rng.random() < dirty_rate
│        └─ perturb_string() per selected cell → rng.integers()
│
│  ─── rng terminated here ───  (Post is deterministic)
│
├─ measure_order = sdk.dag.extract_measure_sub_dag(full_dag, measure_names)
│
├─ metadata = metadata.builder.build_schema_metadata(                   # METADATA
│      groups, orthogonal_pairs, target_rows, measure_order,
│      columns, group_dependencies, patterns)
│    └─ 7-key dict: dimension_groups, orthogonal_groups,
│       group_dependencies, columns, measure_dag_order, patterns, total_rows
│
└─ return (df, metadata)
     │
     ├─ df         → M5 Validation Engine
     └─ metadata   → M4 Schema Meta / M5
          │
          └─ [Loop B on M5 failure]:
               seed' = 42 + k
               overrides' = M5 parameter adjustments
               → re-invoke run_pipeline(..., seed=seed', overrides=overrides')
```
