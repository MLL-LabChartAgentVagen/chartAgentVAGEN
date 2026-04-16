# Module 5: Validation Engine — SVG Flow Diagram Guide

**SVG file:** `module5_validation_engine.svg`
**Source of truth:** `docs/artifacts/stage5_anatomy_summary.md` — Module: Validation Engine (M5)
**Implementation:** `phase_2/validation/`

---

## SVG Section Map

The SVG is divided into two columns:

- **Left column** (x=18..560): The main data flow — inputs → build_fn → L1 → L2 → L3 → merge → decision → return
- **Right column** (x=572..852): Supporting detail — M2 Generation Engine reference box and AUTO_FIX dispatch

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   ┌──────────────────┐      ┌──────────────────────┐                │
│   │  1a. INPUT 1     │      │  1b. INPUT 2         │                │
│   │  Master DataFrame│      │  schema_metadata     │                │
│   └────────┬─────────┘      └──────────┬───────────┘                │
│            └──────────┬────────────────┘                            │
│                       ▼                                             │
│   ┌─────────────────────────────────────────────────────────┐       │
│   │  2. generate_with_validation()  WRAPPER                 │       │
│   │                                                         │       │
│   │   seed = 42 + attempt                                   │       │
│   │                                                         │       │
│   │   ┌──────────────────┐      ┌───────────────────┐       │       │
│   │   │  3. build_fn()   │◄────►│  M2 Gen Engine    │       │       │
│   │   └────────┬─────────┘      └───────────────────┘       │       │
│   │            │ df                                         │       │
│   │   ┌────────┴─────────┐                                  │       │
│   │   │  4. L1 STRUCTURAL│                                  │       │
│   │   └────────┬─────────┘                                  │       │
│   │            │ List[Check]                                │       │
│   │   ┌────────┴─────────┐                                  │       │
│   │   │  5. L2 STATISTIC │                                  │       │
│   │   └────────┬─────────┘                                  │       │
│   │            │ List[Check]                                │       │
│   │   ┌────────┴─────────┐                                  │       │
│   │   │  6. L3 PATTERN   │                                  │       │
│   │   └────────┬─────────┘                                  │       │
│   │            │ List[Check]                                │       │
│   │   ┌────────┴─────────┐                                  │       │
│   │   │  7. MERGE →      │                                  │       │
│   │   │  ValidationReport│                                  │       │
│   │   └────────┬─────────┘                                  │       │
│   │            │                                            │       │
│   │   ┌────────┴─────────┐      ┌───────────────────┐       │       │
│   │   │  8. all_passed?  │─NO──►│  9. AUTO_FIX      │       │       │
│   │   └────────┬─────────┘      │     dispatch      │       │       │
│   │       YES  │                └───────┬───────────┘       │       │
│   │            ▼                     Loop B ──────► build_fn│       │
│   │   ┌──────────────────┐                                  │       │
│   │   │ 10. RETURN       │                                  │       │
│   │   └────────┬─────────┘                                  │       │
│   └────────────┼────────────────────────────────────────────┘       │
│                ▼                                                    │
│   ┌──────────────────┐                                              │
│   │ 11. PHASE 3      │                                              │
│   └──────────────────┘                                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. EXTERNAL INPUTS

**SVG region:** Top row (y=54..144), two side-by-side boxes

**What it represents:** The two external data sources entering Module 5 from upstream modules. These feed every validation layer inside the wrapper.

### 1a. INPUT 1 — Master DataFrame (from M2)

**SVG region:** Left box (x=18..408, y=54..144), purple border

**Responsible file:** `phase_2/engine/generator.py` → `run_pipeline()` (producer); `phase_2/pipeline.py` → `_run_loop_b()` (passthrough)

| | Detail |
|---|---|
| **Input** | `df: pd.DataFrame` — all generated rows and columns from the full §2.8 pipeline (stages α → Post) |
| **Output** | Same DataFrame, passed into `build_fn()` initial call and ultimately into all three validation layers |
| **Data flow** | `pipeline._run_loop_b(df, metadata, raw_declarations, ...)` → `build_fn(seed, overrides)` → `run_pipeline(...)` → `df` |

### 1b. INPUT 2 — schema_metadata dict (from M4)

**SVG region:** Right box (x=426..852, y=54..144), yellow border

**Responsible file:** `phase_2/metadata/builder.py` → `build_schema_metadata()` (producer); `phase_2/pipeline.py` → `_run_loop_b()` (passthrough)

| | Detail |
|---|---|
| **Input** | `metadata: dict[str, Any]` — fully structured metadata built by §2.6, containing `columns`, `dimension_groups`, `measure_dag_order`, `orthogonal_groups`, `group_dependencies`, `patterns`, `target_rows` |
| **Output** | Same dict, stored as `SchemaAwareValidator.meta` and used to parameterize every check in L1, L2, and L3 |
| **Data flow** | `pipeline._run_loop_b(df, metadata, ...)` → `generate_with_validation(meta=metadata, ...)` → `SchemaAwareValidator(meta)` |

**SVG arrows:** Two vertical arrows (y=144→162) flow from both input boxes down into the wrapper.

---

## 2. generate_with_validation() WRAPPER

**SVG region:** Large bounding box (x=18..852, y=162..806), grey border

**What it represents:** The outer retry orchestrator (Loop B). Contains all validation logic, the build_fn closure, and the auto-fix dispatch. Retries up to 3 times (configurable via `max_attempts`), returning on the first pass or after exhausting attempts.

**Responsible file:** `phase_2/validation/autofix.py` → `generate_with_validation()`

| | Detail |
|---|---|
| **Input** | `build_fn: Callable[[int, ParameterOverrides \| None], tuple[pd.DataFrame, dict]]`, `meta: dict`, `patterns: list[dict]`, `base_seed: int = 42`, `max_attempts: int = 3`, `auto_fix: dict \| None`, `realism_config: dict \| None` |
| **Output** | `tuple[pd.DataFrame, dict, ValidationReport]` |
| **Data flow** | `pipeline._run_loop_b()` → `generate_with_validation(build_fn, meta, patterns, ...)` |

**Seed note** (y=196..212): `seed = 42 + attempt` where `attempt ∈ {0, 1, 2, 3}`. Each retry uses a different random seed to vary the generation output.

**Call order:**
```
pipeline._run_loop_b(df, metadata, raw_declarations, max_retries, auto_fix, realism_config)
  ├─ defines build_fn(seed, overrides) closure
  └─ autofix.generate_with_validation(build_fn, meta, patterns, base_seed, max_attempts, auto_fix, realism_config)
       └─ for attempt in range(max_attempts):
            seed = base_seed + attempt
            df, meta = build_fn(seed, overrides)
            report = SchemaAwareValidator(meta).validate(df, patterns)
            ...
```

---

## 3. build_fn() CLOSURE

**SVG region:** Left column (x=30..520, y=224..296), blue border. Right column (x=572..832, y=224..296), dashed grey border (M2 reference).

**What it represents:** A closure defined inside `_run_loop_b()` that wraps M2's `run_pipeline()`. Each call generates a fresh candidate DataFrame with a new seed and optional parameter overrides from auto-fix.

**Responsible files:**
- `phase_2/pipeline.py` → `_run_loop_b()` (defines the closure)
- `phase_2/engine/generator.py` → `run_pipeline()` (called by the closure)

| | Detail |
|---|---|
| **Input** | `seed: int`, `overrides: ParameterOverrides \| None` |
| **Output** | `tuple[pd.DataFrame, dict[str, Any]]` — generated DataFrame and updated metadata |
| **Data flow** | `build_fn(seed, overrides)` → `_apply_pattern_overrides(patterns, overrides)` → `run_pipeline(columns, groups, ..., seed, patterns, realism_config=None, overrides)` → `(df, meta)` |

**SVG arrows between build_fn and M2 Gen Engine:**
- **→ calls** (solid blue, left-to-right at y=251): build_fn invokes M2
- **← df** (solid blue, right-to-left at y=269): M2 returns the generated DataFrame

**The M2 reference box** (dashed border) shows the full §2.8 pipeline stages: Pre-flight → α → β → γ → δ → Post.

**Call order:**
```
build_fn(seed, overrides)
  ├─ pipeline._apply_pattern_overrides(patterns, overrides) → effective_patterns
  └─ generator.run_pipeline(
         columns, groups, group_dependencies, measure_dag,
         target_rows, seed, patterns=effective_patterns,
         realism_config=None, overrides=overrides, orthogonal_pairs
     ) → (df, meta)
```

**Key detail:** `realism_config=None` is always passed — realism injection happens *after* validation passes (validation-before-realism ordering, enforced by the wrapper in step 10).

---

## 4. L1: STRUCTURAL CHECKS

**SVG region:** Left column (x=30..560, y=312..422), amber/orange border

**What it represents:** The first validation layer — checks data shape and declared structural constraints. These are fast, deterministic checks that catch fundamental generation errors.

**Responsible files:**
- `phase_2/validation/validator.py` → `SchemaAwareValidator._run_l1()` (dispatcher)
- `phase_2/validation/structural.py` (all 6 check functions)

| | Detail |
|---|---|
| **Input** | `df: pd.DataFrame` (from build_fn), `self.meta: dict` (from constructor) |
| **Output** | `list[Check]` — one or more Check objects per check function |
| **Data flow** | `validator.validate(df, patterns)` → `self._run_l1(df)` → calls each L1 function → `report.add_checks(l1_checks)` |

**The 6 structural checks** (shown as bullet items in SVG):

| SVG label | Check function | Signature | Returns | Pass criterion |
|-----------|---------------|-----------|---------|----------------|
| `row_count` | `check_row_count(df, meta)` | `(DataFrame, dict) → Check` | Single `Check` | `\|actual - target\| / target < 0.1` |
| `cardinality_*` | `check_categorical_cardinality(df, meta)` | `(DataFrame, dict) → list[Check]` | One `Check` per categorical column | `nunique() == declared_cardinality` |
| `marginal_*` | `check_marginal_weights(df, meta)` | `(DataFrame, dict) → list[Check]` | One `Check` per root categorical with weights | `max_absolute_deviation < 0.10` |
| `finite_*` | `check_measure_finiteness(df, meta)` | `(DataFrame, dict) → list[Check]` | One `Check` per measure column | `na_count == 0 and inf_count == 0` |
| `orthogonal_*_*` | `check_orthogonal_independence(df, meta)` | `(DataFrame, dict) → list[Check]` | One `Check` per orthogonal pair | `chi2_contingency p_value > 0.05` |
| `measure_dag_acyc` | `check_measure_dag_acyclic(meta)` | `(dict,) → Check` | Single `Check` | `len(set(dag_order)) == len(dag_order)` |

**Call order:**
```
SchemaAwareValidator._run_l1(df)
  ├─ structural.check_row_count(df, self.meta)                 → Check
  ├─ structural.check_categorical_cardinality(df, self.meta)   → list[Check]
  ├─ structural.check_orthogonal_independence(df, self.meta)   → list[Check]
  ├─ structural.check_measure_dag_acyclic(self.meta)           → Check
  ├─ structural.check_marginal_weights(df, self.meta)          → list[Check]
  └─ structural.check_measure_finiteness(df, self.meta)        → list[Check]
  → list[Check] (all concatenated)
```

**SVG arrow:** Downward arrow at y=422→436 labeled `List[Check]` flows into L2.

---

## 5. L2: STATISTICAL CHECKS

**SVG region:** Left column (x=30..560, y=436..504), teal/cyan border

**What it represents:** The second validation layer — checks distributional fit and inter-column relationships using statistical tests. These are computationally heavier than L1 and require the full metadata parameter models.

**Responsible files:**
- `phase_2/validation/validator.py` → `SchemaAwareValidator._run_l2()` (dispatcher)
- `phase_2/validation/statistical.py` (check functions + helpers)
- `phase_2/engine/measures.py` → `_safe_eval_formula()`, `_resolve_effects()` (used by residual check)
- `phase_2/sdk/validation.py` → `extract_formula_symbols()` (used by `_get_formula_measure_deps()`)

| | Detail |
|---|---|
| **Input** | `df: pd.DataFrame`, `patterns: list[dict] \| None`, `self.meta: dict` |
| **Output** | `list[Check]` — variable count depending on measure columns and group dependencies |
| **Data flow** | `validator.validate(df, patterns)` → `self._run_l2(df, patterns)` → dispatches per measure type → `report.add_checks(l2_checks)` |

**The 3 check families** (shown as bullet items in SVG):

| SVG label | Check function | Dispatch condition | Returns | Pass criterion |
|-----------|---------------|--------------------|---------|----------------|
| `ks_*_*` | `check_stochastic_ks(df, col_name, meta, patterns)` | `measure_type == "stochastic"` | `list[Check]`, one per predictor cell | `kstest p_value > 0.05` |
| `structural_*_residual` | `check_structural_residuals(df, col_name, meta, patterns)` | `measure_type == "structural"` | Single `Check` | Deterministic: `residual_std < 1e-6`; noisy: `\|std - sigma\| / sigma < 0.2` |
| `group_dep_*` | `check_group_dependency_transitions(df, meta)` | Always (for each group dependency) | `list[Check]`, one per dependency | `max_conditional_deviation < 0.10` |

**KS test internal pipeline** (`check_stochastic_ks`):
```
check_stochastic_ks(df, col_name, meta, patterns)
  ├─ Exclude pattern-targeted rows: df.eval(p["target"]) for patterns on this column
  ├─ _iter_predictor_cells(work_df, col_name, col_meta, columns_meta)
  │    ├─ Identify categorical columns from param_model.effects
  │    ├─ itertools.product(*value_sets) → Cartesian product of predictor values
  │    ├─ Filter df for each cell (min 5 rows, max 100 cells, largest first)
  │    └─ → list[(predictor_values_dict, cell_df)]
  │
  └─ For each (predictor_values, cell_df):
       ├─ _compute_cell_params(col_meta, predictor_values, columns_meta)
       │    └─ theta = intercept + sum(effects for cell values) per param key
       ├─ _expected_cdf(family, params) → scipy frozen distribution
       │    └─ Supports: gaussian, lognormal, exponential, gamma, beta, uniform
       │       (poisson, mixture → None, skipped)
       └─ scipy.stats.kstest(sample, dist.cdf) → (stat, p_value)
```

**Structural residual internal pipeline** (`check_structural_residuals`):
```
check_structural_residuals(df, col_name, meta, patterns)
  ├─ _get_formula_measure_deps(formula, col_name, columns_meta) → dep_measures
  │    └─ sdk.validation.extract_formula_symbols(formula) → filter to measure cols
  ├─ Exclude pattern-targeted rows on this col AND upstream formula deps (P3-8)
  ├─ For each row in work_df:
  │    ├─ measures._resolve_effects(col_meta, row, columns_meta) → resolved effects
  │    └─ measures._safe_eval_formula(formula, context) → predicted value
  ├─ residuals = observed - predicted
  └─ noise_sigma == 0? → std < 1e-6 : |std - sigma| / sigma < 0.2
```

**Call order:**
```
SchemaAwareValidator._run_l2(df, patterns)
  ├─ For each measure column in meta["columns"]:
  │    ├─ measure_type == "structural":
  │    │    └─ statistical.check_structural_residuals(df, col, self.meta, patterns) → Check
  │    └─ measure_type == "stochastic":
  │         └─ statistical.check_stochastic_ks(df, col, self.meta, patterns) → list[Check]
  │
  └─ statistical.check_group_dependency_transitions(df, self.meta) → list[Check]
  → list[Check] (all concatenated)
```

**SVG arrow:** Downward arrow at y=504→518 labeled `List[Check]` flows into L3.

---

## 6. L3: PATTERN CHECKS

**SVG region:** Left column (x=30..560, y=518..598), purple border

**What it represents:** The third validation layer — checks that injected patterns (outliers, trends, reversals, etc.) are detectable in the generated data. Only runs if `patterns` is non-empty.

**Responsible files:**
- `phase_2/validation/validator.py` → `SchemaAwareValidator._run_l3()` (dispatcher)
- `phase_2/validation/pattern_checks.py` (all check functions)

| | Detail |
|---|---|
| **Input** | `df: pd.DataFrame`, `patterns: list[dict[str, Any]]`, `self.meta: dict` |
| **Output** | `list[Check]` — one Check per pattern in the spec list |
| **Data flow** | `validator.validate(df, patterns)` → `self._run_l3(df, patterns)` (only if patterns truthy) → `report.add_checks(l3_checks)` |

**The 4 check types + 3 stubs** (shown as bullet items in SVG):

| SVG label | Check function | Signature | Pass criterion | Status |
|-----------|---------------|-----------|----------------|--------|
| `outlier_*` | `check_outlier_entity(df, pattern)` | `(DataFrame, dict) → Check` | `z = \|subset_mean - ref_mean\| / ref_std >= 2.0` | Implemented |
| `reversal_*_*` | `check_ranking_reversal(df, pattern, meta)` | `(DataFrame, dict, dict) → Check` | Spearman rank correlation `< 0` | Implemented |
| `trend_*` | `check_trend_break(df, pattern, meta)` | `(DataFrame, dict, dict) → Check` | `\|after_mean - before_mean\| / \|before_mean\| > 0.15` | Implemented |
| `dominance` | `check_dominance_shift(df, pattern, meta)` | `(DataFrame, dict, dict) → Check` | — | Stub (returns passed=True) |
| — | `check_convergence(df, pattern, meta)` | `(DataFrame, dict, dict) → Check` | — | Stub (returns passed=True) |
| — | `check_seasonal_anomaly(df, pattern, meta)` | `(DataFrame, dict, dict) → Check` | — | Stub (returns passed=True) |

**L3 dispatch logic** (in `_run_l3`):
```
SchemaAwareValidator._run_l3(df, patterns)
  └─ For each pattern in patterns:
       ├─ type == "outlier_entity"    → pattern_checks.check_outlier_entity(df, pattern)
       ├─ type == "trend_break"       → pattern_checks.check_trend_break(df, pattern, self.meta)
       ├─ type == "dominance_shift"   → pattern_checks.check_dominance_shift(df, pattern, self.meta)
       ├─ type == "convergence"       → pattern_checks.check_convergence(df, pattern, self.meta)
       ├─ type == "seasonal_anomaly"  → pattern_checks.check_seasonal_anomaly(df, pattern, self.meta)
       ├─ type == "ranking_reversal"  → pattern_checks.check_ranking_reversal(df, pattern, self.meta)
       └─ else                        → skipped (logged at DEBUG)
  → list[Check]
```

**Outlier entity internal detail:**
- Uses **complement statistics** (non-target rows) as the reference distribution, not global stats — avoids the pattern injection inflating the reference and reducing the z-score.
- Fallback to global stats only when complement has < 2 rows.

**Ranking reversal internal detail:**
- Entity column resolved from `params["entity_col"]` or falls back to `dim_groups[first_key]["hierarchy"][0]`.
- Computes per-entity means of two metrics via `df.groupby(entity_col)[[m1, m2]].mean()`.
- Spearman rank correlation: `means[m1].rank().corr(means[m2].rank())`.

**SVG arrow:** Downward arrow at y=598→612 labeled `List[Check]` flows into Merge.

---

## 7. MERGE → ValidationReport

**SVG region:** Left column (x=30..560, y=612..668), green border

**What it represents:** The aggregation of all L1, L2, and L3 check results into a single `ValidationReport` object. This is not a separate function — it's the accumulation pattern inside `SchemaAwareValidator.validate()`.

**Responsible file:** `phase_2/validation/validator.py` → `SchemaAwareValidator.validate()`

| | Detail |
|---|---|
| **Input** | Three `list[Check]` results from `_run_l1()`, `_run_l2()`, `_run_l3()` |
| **Output** | `ValidationReport` with all checks concatenated |
| **Data flow** | `report = ValidationReport()` → `report.add_checks(l1)` → `report.add_checks(l2)` → `report.add_checks(l3)` |

**ValidationReport** (from `phase_2/types.py`):
```python
@dataclass
class ValidationReport:
    checks: list[Check] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:          # all(c.passed for c in self.checks)
        ...
    @property
    def failures(self) -> list[Check]:     # [c for c in self.checks if not c.passed]
        ...
    def add_checks(self, new: list[Check]) -> None:
        self.checks.extend(new)
```

**Check** (from `phase_2/types.py`):
```python
@dataclass
class Check:
    name: str                              # e.g. "row_count", "ks_revenue", "outlier_wait_minutes"
    passed: bool
    detail: Optional[str] = None           # e.g. "χ² p=0.34"
```

**SVG arrow:** Downward arrow at y=668→682 flows into the decision diamond.

---

## 8. DECISION: report.all_passed?

**SVG region:** Left column (x=30..560, y=682..736), grey border

**What it represents:** The branching point inside the `generate_with_validation()` loop. If all checks passed, flow exits to RETURN. If any check failed and attempts remain, flow goes to AUTO_FIX.

**Responsible file:** `phase_2/validation/autofix.py` → `generate_with_validation()` (lines 272–280)

| | Detail |
|---|---|
| **Input** | `report: ValidationReport` from `SchemaAwareValidator.validate()` |
| **Output** | Branch decision: YES → break loop → RETURN; NO → accumulate overrides → loop back |
| **Data flow** | `if report.all_passed: break` (YES path) / `for check in report.failures: ...` (NO path) |

**SVG labels:**
- **YES ✓** (left side, y=725): green arrow downward to RETURN box (y=736→752)
- **NO ✗** (right side, y=725): red arrow rightward to AUTO_FIX box (y=709→572)

---

## 9. AUTO_FIX DISPATCH

**SVG region:** Right column (x=572..832, y=682..792), red/pink border

**What it represents:** The auto-fix strategy matching and parameter override accumulation. When validation fails, each failed check is matched against a strategy map using glob patterns. Matched strategies mutate the `overrides` dict, which is passed to `build_fn()` on the next retry.

**Responsible file:** `phase_2/validation/autofix.py`

| | Detail |
|---|---|
| **Input** | `report.failures: list[Check]`, `auto_fix: dict[str, Callable]`, `overrides: ParameterOverrides` |
| **Output** | Mutated `overrides: ParameterOverrides` dict, then loop back to `build_fn()` |
| **Data flow** | `for check in report.failures:` → `match_strategy(check.name, auto_fix)` → `strategy(check, overrides)` → `overrides` updated |

**The 4 steps** (shown as numbered items in SVG):

| Step | Action | Implementation |
|------|--------|----------------|
| 1 | Identify failed check(s) in report | `report.failures` property → `list[Check]` |
| 2 | match_strategy → map to fix action | `autofix.match_strategy(check.name, auto_fix)` → `fnmatch.fnmatch(name, glob)` |
| 3 | Mutate decl (adjust param values) | Strategy callable mutates `overrides` dict |
| 4 | Loop B → new seed + mutated decl | `build_fn(base_seed + attempt, overrides)` on next iteration |

**Three fix strategies:**

| Strategy | Function | Effect | Compounding |
|----------|----------|--------|-------------|
| `widen_variance` | `widen_variance(check, overrides, factor=1.2)` | `overrides["measures"][col]["sigma"] *= 1.2` | 1.2 → 1.44 → 1.728 across retries |
| `amplify_magnitude` | `amplify_magnitude(check, overrides, patterns, factor=1.3)` | `overrides["patterns"][idx]["params"]["z_score"] *= 1.3` | 1.3 → 1.69 → 2.197 across retries |
| `reshuffle_pair` | `reshuffle_pair(check, overrides)` | `overrides["reshuffle"].append(col)` | Column added once (idempotent append) |

**Strategy matching detail:**
```
autofix.match_strategy(check_name, auto_fix)
  └─ for glob_pattern, strategy_fn in auto_fix.items():
       if fnmatch.fnmatch(check_name, glob_pattern):
           return strategy_fn      ← first match wins
  └─ return None                   ← no match, no override for this failure
```

**Loop B arc:** The SVG shows a dashed red arc (y=737) from the AUTO_FIX right edge → up the right margin → back to `build_fn()` level at y=200. This represents `generate_with_validation()` continuing the `for attempt in range(max_attempts)` loop with updated overrides and a new seed.

---

## 10. RETURN

**SVG region:** Left column (x=30..560, y=752..804), green border

**What it represents:** The output of `generate_with_validation()` — either on first `all_passed=True` or after exhausting all retry attempts (may still contain failures).

**Responsible file:** `phase_2/validation/autofix.py` → `generate_with_validation()` (lines 282–289)

| | Detail |
|---|---|
| **Input** | Final `df`, `meta`, `report` from the last attempt |
| **Output** | `tuple[pd.DataFrame, dict[str, Any], ValidationReport]` |
| **Data flow** | Loop exits → optional realism injection → return `(df, meta, report)` |

**Post-validation realism injection:**
```
if realism_config is not None and df is not None:
    from phase_2.engine.realism import inject_realism
    realism_rng = np.random.default_rng(base_seed + max_attempts)
    df = inject_realism(df, realism_config, columns_meta, realism_rng)
return df, meta, report
```

**Key detail:** Realism is applied *after* all validation completes — the validation checks run against the "clean" DataFrame, and realism noise is layered on only at the end. This is the "validation-before-realism" ordering enforced by passing `realism_config=None` to `build_fn()`.

**SVG arrow:** Downward arrow at y=806→822 flows to PHASE 3.

---

## 11. PHASE 3

**SVG region:** Center box (x=168..558, y=822..872), blue border

**What it represents:** The downstream consumer of the validated output. Phase 3 receives the validated `(df, schema_metadata, ValidationReport)` tuple for chart generation and annotation.

**Responsible file:** Phase 3 pipeline (downstream, outside M5 scope)

| | Detail |
|---|---|
| **Input** | `(df, schema_metadata, ValidationReport)` from RETURN |
| **Output** | Chart generation pipeline (outside Module 5 scope) |
| **Data flow** | `pipeline.run_phase2()` returns the tuple → Phase 3 caller |

---

## Complete File Responsibility Map

| SVG Section | Primary File | Supporting Files |
|---|---|---|
| 1a. INPUT 1 (DataFrame) | `pipeline.py` | `engine/generator.py` |
| 1b. INPUT 2 (schema_metadata) | `pipeline.py` | `metadata/builder.py` |
| 2. generate_with_validation() wrapper | `validation/autofix.py` | `pipeline.py` |
| 3. build_fn() closure | `pipeline.py` | `engine/generator.py` |
| 4. L1 Structural Checks | `validation/structural.py` | `validation/validator.py`, `types.py` |
| 5. L2 Statistical Checks | `validation/statistical.py` | `validation/validator.py`, `engine/measures.py`, `sdk/validation.py`, `types.py` |
| 6. L3 Pattern Checks | `validation/pattern_checks.py` | `validation/validator.py`, `types.py` |
| 7. Merge → ValidationReport | `validation/validator.py` | `types.py` |
| 8. Decision (all_passed?) | `validation/autofix.py` | `types.py` |
| 9. AUTO_FIX dispatch | `validation/autofix.py` | — |
| 10. RETURN | `validation/autofix.py` | `engine/realism.py` |
| 11. PHASE 3 | *(downstream)* | `pipeline.py` |

---

## End-to-End Call Trace

```
pipeline.run_phase2(scenario_context, max_loop_b_retries, auto_fix, realism_config)
│
├─ pipeline._run_loop_a(...) → (df, metadata, raw_declarations)  [Loop A — M3]
│
└─ pipeline._run_loop_b(df, metadata, raw_declarations, max_retries, auto_fix, realism_config)
    │
    ├─ Extracts: columns, groups, group_dependencies, measure_dag, target_rows,
    │            patterns, base_seed, orthogonal_pairs from raw_declarations
    │
    ├─ Defines build_fn(seed, overrides):
    │    ├─ pipeline._apply_pattern_overrides(patterns, overrides) → effective_patterns
    │    └─ generator.run_pipeline(columns, groups, ..., seed, effective_patterns,
    │           realism_config=None, overrides, orthogonal_pairs) → (df, meta)
    │
    └─ autofix.generate_with_validation(build_fn, meta, patterns, base_seed, max_attempts, auto_fix, realism_config)
        │
        ├─ overrides = {}
        │
        └─ for attempt in range(max_attempts):                                ← LOOP B
            │
            ├─ seed = base_seed + attempt
            ├─ df, meta = build_fn(seed, overrides)                           ← Section 3
            │    └─ generator.run_pipeline(...) → (df, meta)                  ← M2
            │
            ├─ report = SchemaAwareValidator(meta).validate(df, patterns)     ← Sections 4–7
            │    │
            │    ├─ _run_l1(df)                                               ← Section 4
            │    │    ├─ structural.check_row_count(df, meta)
            │    │    ├─ structural.check_categorical_cardinality(df, meta)
            │    │    ├─ structural.check_orthogonal_independence(df, meta)
            │    │    ├─ structural.check_measure_dag_acyclic(meta)
            │    │    ├─ structural.check_marginal_weights(df, meta)
            │    │    └─ structural.check_measure_finiteness(df, meta)
            │    │
            │    ├─ _run_l2(df, patterns)                                     ← Section 5
            │    │    ├─ For each measure col:
            │    │    │    ├─ structural → statistical.check_structural_residuals(df, col, meta, patterns)
            │    │    │    │    ├─ _get_formula_measure_deps(formula, col, columns_meta)
            │    │    │    │    │    └─ sdk.validation.extract_formula_symbols(formula)
            │    │    │    │    ├─ engine.measures._resolve_effects(col_meta, row, columns_meta)
            │    │    │    │    └─ engine.measures._safe_eval_formula(formula, context)
            │    │    │    └─ stochastic → statistical.check_stochastic_ks(df, col, meta, patterns)
            │    │    │         ├─ _iter_predictor_cells(df, col, col_meta, columns_meta)
            │    │    │         ├─ _compute_cell_params(col_meta, predictor_vals, columns_meta)
            │    │    │         ├─ _expected_cdf(family, params) → scipy frozen dist
            │    │    │         └─ scipy.stats.kstest(sample, dist.cdf)
            │    │    └─ statistical.check_group_dependency_transitions(df, meta)
            │    │         └─ max_conditional_deviation(observed, declared)
            │    │
            │    └─ _run_l3(df, patterns)  [if patterns]                      ← Section 6
            │         └─ For each pattern:
            │              ├─ outlier_entity    → pattern_checks.check_outlier_entity(df, pattern)
            │              ├─ trend_break       → pattern_checks.check_trend_break(df, pattern, meta)
            │              │                        └─ _find_temporal_column(meta)
            │              ├─ ranking_reversal  → pattern_checks.check_ranking_reversal(df, pattern, meta)
            │              ├─ dominance_shift   → pattern_checks.check_dominance_shift(...)   [stub]
            │              ├─ convergence       → pattern_checks.check_convergence(...)        [stub]
            │              └─ seasonal_anomaly  → pattern_checks.check_seasonal_anomaly(...)   [stub]
            │
            ├─ report.all_passed?                                             ← Section 8
            │    ├─ YES → break                                               ← → Section 10
            │    └─ NO  → auto-fix dispatch                                   ← Section 9
            │
            └─ for check in report.failures:                                  ← Section 9
                 ├─ autofix.match_strategy(check.name, auto_fix)
                 │    └─ fnmatch.fnmatch(check.name, glob_pattern)
                 └─ strategy(check, overrides) → mutated overrides
                      ├─ widen_variance     → overrides["measures"][col]["sigma"] *= 1.2
                      ├─ amplify_magnitude  → overrides["patterns"][idx]["params"]["z_score"] *= 1.3
                      └─ reshuffle_pair     → overrides["reshuffle"].append(col)
                 [loop continues with new seed + updated overrides]

        ├─ [post-loop] realism_config? → engine.realism.inject_realism(df, ...)  ← Section 10
        └─ return (df, meta, report)                                             ← Section 10
             └─ pipeline._run_loop_b() returns to pipeline.run_phase2()          ← Section 11
```
