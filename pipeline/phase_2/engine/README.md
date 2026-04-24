# M2 — Generation Engine

## What This Module Does

M2 is the deterministic computation core of Phase 2. It takes the decomposed fields of a frozen `DeclarationStore` plus a seed and produces the Master DataFrame by composing a four-stage pipeline `M = τ_post ∘ δ? ∘ γ ∘ β ∘ α(seed)` with a single shared RNG stream. Position in the pipeline: **downstream** of M1 (reads the frozen store via the caller that unpacks it) and **upstream** of M5 (its DataFrame is the input the validator checks). M2 also calls M4's `build_schema_metadata` inline at the tail of `run_pipeline`, so M2's return value already carries the Phase 2 → Phase 3 metadata contract. Boundary: M2 is **stateless** — it mutates no registry, mutates no store, and has no side effects outside the returned `(df, metadata)` tuple. That statelessness is what makes Loop B safe: the validator can re-invoke `run_pipeline` as many times as it likes with incrementing seeds and accumulated overrides without any risk of cross-attempt contamination.

## Internal Structure

```
pipeline/phase_2/engine/
├── __init__.py          # re-exports build_skeleton
├── generator.py         # run_pipeline — the 4-stage orchestrator
├── skeleton.py          # Phase α: non-measure columns (categoricals + temporals)
├── measures.py          # Phase β: stochastic + structural measures, _safe_eval_formula
├── postprocess.py       # τ_post: dict-of-arrays → pd.DataFrame
├── patterns.py          # Phase γ: outlier_entity, trend_break
└── realism.py           # Phase δ: missing values + dirty values
```

**Data flow.** `run_pipeline` builds the full DAG (delegating to `sdk.dag.build_full_dag`), computes the topological order, and creates a single `np.random.default_rng(seed)`. It then: (α) calls `build_skeleton` to populate all non-measure columns into a `dict[str, np.ndarray]`; (β) calls `generate_measures` which mutates that dict in place, filling measure columns in topological order; (τ_post) calls `to_dataframe` to convert the dict to a `pd.DataFrame` with proper dtype casting; (γ) calls `inject_patterns` if any patterns were declared; (δ) calls `inject_realism` if `realism_config` is non-`None`. Finally, it extracts the measure topological sub-order via `extract_measure_sub_dag` and calls M4's `build_schema_metadata` to assemble the 7-key metadata dict, which is returned alongside the DataFrame.

## Key Interfaces

### External-facing: [`run_pipeline`](generator.py) (in `generator.py`)

```python
from pipeline.phase_2.engine.generator import run_pipeline

df, metadata = run_pipeline(
    columns: OrderedDict[str, dict[str, Any]],
    groups: dict[str, DimensionGroup],
    group_dependencies: list[GroupDependency],
    measure_dag: dict[str, list[str]],
    target_rows: int,
    seed: int,
    patterns: list[dict[str, Any]] | None = None,
    realism_config: dict[str, Any] | None = None,
    overrides: dict | None = None,
    orthogonal_pairs: list | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]
```

Returns the DataFrame (column order = `topo_order`, `RangeIndex`, categorical → object, temporal → `datetime64[ns]`, `temporal_derived.is_weekend` → `bool`, other derived → `int64`, measures → `float64`) and the M4 7-key metadata dict. Raises `CyclicDependencyError` if the full DAG contains a cycle; `NotImplementedError` for the `mixture` family, pattern types beyond `outlier_entity` / `trend_break`, and any truthy `censoring` in `realism_config`; `InvalidParameterError` (notably for zero-denominator structural evaluation, with per-row context); `PatternInjectionError` / `DegenerateDistributionError` where relevant.

### Stage entry points (stateless, each advances the shared RNG in sequence)

| Stage | Function | File | Role |
|---|---|---|---|
| α | [`build_skeleton(columns, target_rows, group_dependencies, topo_order, rng)`](skeleton.py) | `skeleton.py` | Populates non-measure columns. Dispatches per column to `sample_independent_root`, `sample_dependent_root` (for roots named in a `GroupDependency`), `sample_child_category`, `sample_temporal_root`, or `derive_temporal_child` (no RNG). |
| β | [`generate_measures(columns, topo_order, rows, rng, overrides=None)`](measures.py) | `measures.py` | Fills measures in topological order. `_sample_stochastic` builds per-row parameters via `intercept + Σ effects` then calls `rng.<family>`; `_eval_structural` evaluates the formula per row via `_safe_eval_formula` + optional gaussian noise. |
| τ_post | [`to_dataframe(rows, topo_order, columns, target_rows)`](postprocess.py) | `postprocess.py` | No RNG. Assembles `pd.DataFrame` with deterministic dtype casting. |
| γ | [`inject_patterns(df, patterns, columns, rng)`](patterns.py) | `patterns.py` | Sequential in declaration order. `inject_outlier_entity` shifts target subset means by `z_score × global_std`; `inject_trend_break` scales post-break values by `1 + magnitude`. Other pattern types raise `NotImplementedError`. |
| δ | [`inject_realism(df, realism_config, columns, rng)`](realism.py) | `realism.py` | Optional. `inject_missing_values` NaN-masks cells at `missing_rate`; `inject_dirty_values` perturbs categorical strings at `dirty_rate` (adjacent-swap / delete / insert). |

### The security-critical helper: [`_safe_eval_formula`](measures.py) (in `measures.py`)

```python
_safe_eval_formula(formula: str, context: dict[str, float]) -> float
```

A restricted AST evaluator. Allowed node types: `ast.Expression`, `ast.BinOp` with `{Add, Sub, Mult, Div, Pow}`, `ast.UnaryOp` with `USub`, `ast.Constant` (int/float), `ast.Num` (legacy compat), `ast.Name` (resolved from `context`). Every other AST node — `Call`, `Subscript`, `Attribute`, `Lambda`, comprehensions, slices, conditional expressions, f-strings, starred expressions — raises `ValueError`. `ZeroDivisionError` from a legitimate `a / 0` is allowed to propagate so the caller (`_eval_structural`) can wrap it with per-row context into an `InvalidParameterError`.

## How It Works

`run_pipeline` executes the following sequence. The order and structure matter — each step depends on guarantees from the previous one.

1. **Default-fill optional inputs** (`patterns ← []`, `orthogonal_pairs ← []`). These defaults let `run_pipeline` be called by callers that don't know or care about patterns, and let the passthrough to `build_schema_metadata` at the end produce the full 7-key shape regardless.

2. **Create the single RNG.** `rng = np.random.default_rng(seed)`. **Why create it once here:** determinism is the core invariant — for a given seed, the entire pipeline's output is bit-identical across runs. That requires every RNG-consuming stage to draw from a single stream in a fixed order. Creating separate RNGs per stage would work for determinism per-seed but would make Loop B's `seed + attempt` trick produce surprising results (changes in one stage would not perturb another).

3. **Build the full DAG and topologically sort it** via `sdk.dag.build_full_dag` + `topological_sort` (Kahn's algorithm with `heapq` for lexicographic tie-breaking). **Why sort once up-front:** every downstream stage iterates `topo_order`. If α generates a child categorical before its parent, sampling fails outright; if β generates a measure before its stochastic predictors, `_compute_per_row_params` reads uninitialized arrays. Computing the order once and threading the list through the stages turns ordering from a pervasive concern into a single-point invariant.

4. **Phase α — skeleton** (`build_skeleton`): iterate `topo_order`, skipping measure columns. Dispatch by role:
   - Root categorical without a dependency → `sample_independent_root` → single `rng.choice(values, size=target_rows, p=weights)`.
   - Root categorical named in a `GroupDependency` → `sample_dependent_root` → per-parent-value block sampling using `conditional_weights`.
   - Non-root categorical → `sample_child_category` → per-parent-value sampling (flat or conditional weights).
   - Temporal root → `sample_temporal_root` → enumerate eligible dates per `freq`, then `rng.integers` to sample indices.
   - Temporal derived → `derive_temporal_child` → **no RNG** (pure function of the source date column).
   
   **Why temporal derived consumes no RNG:** it's a deterministic transform of an already-sampled date (`dayofweek`, `month`, `quarter`, `is_weekend`). Consuming RNG here would change the state visible to β, which would be a surprising coupling.

5. **Phase β — measures** (`generate_measures`): iterate `topo_order`, process only measure columns. For stochastic measures: `_compute_per_row_params` builds per-row `theta = intercept + Σ effects` arrays (and applies multiplicative overrides from Loop B); `_sample_stochastic` clamps sigma/scale/rate to at least 1e-6 and dispatches to `rng.normal|lognormal|gamma|beta|uniform|poisson|exponential`. For structural measures: `_eval_structural` iterates rows, resolves effects, evaluates the formula via `_safe_eval_formula`, and (if declared) adds `rng.normal(0, noise_sigma)`. **Why clamp params rather than validate and raise:** validation already happened at declaration time in M1. A zero sigma here means the LLM's intercept+effects model cancelled out to degeneracy given the realized row — the correct response is to emit a finite distribution (σ=1e-6) that will still fail M5's L2 checks and trigger Loop B, rather than hard-crash generation.

6. **τ_post — DataFrame assembly** (`to_dataframe`): no RNG. Converts `rows` dict to `pd.DataFrame`, casts dtypes per column type, orders columns by `topo_order`, sets a `RangeIndex`. This is the seam between array-land (where α and β live) and pandas-land (where γ, δ, and M5 live). **Why a separate stage rather than inline in β:** patterns and realism need DataFrame features — `df.query(target)`, `df.groupby`, datetime comparisons — that are awkward on raw dicts of arrays. Making τ_post explicit also means swapping it out for, say, a Polars backend would be a single-file change.

7. **Phase γ — patterns** (`inject_patterns`, conditional on non-empty list): sequential in declaration order. Later patterns targeting the same rows overwrite earlier ones — this is a deliberate LIFO semantics so the LLM can think of patterns as layered effects. **Why sequential rather than parallel:** declaration order is the only signal the LLM has about precedence; parallel application would require a combinator model that the current SDK does not offer.

8. **Phase δ — realism** (`inject_realism`, conditional on `realism_config is not None`): missing values first, then dirty values. **Why missing before dirty:** `inject_missing_values` sets cells to NaN with independent per-cell probability; `inject_dirty_values` perturbs categorical strings. Running them in the reverse order would waste work dirtying cells that then get blanked. **Why realism is optional and can be skipped by Loop B:** M5's L2 and L3 checks assume clean data; injecting missingness before validation would pollute KS tests and pattern-detectability checks. The caller (Loop B in `_run_loop_b`) passes `realism_config=None` during the retry loop and re-applies realism only after `report.all_passed` (see M5's `generate_with_validation`).

9. **Build schema metadata.** Extract the measure sub-DAG's topological order via `extract_measure_sub_dag`, then call `build_schema_metadata` with the decomposed fields. This call is inline — not delegated, not optional. **Why inline rather than deferred:** M4 is a pure projection of the declaration state, and shipping `(df, meta)` together lets every caller treat Phase 2 output as a single unit, which is what M5 and Phase 3 expect.

**Loop B re-entry.** `run_pipeline` is re-invoked by `_run_loop_b` with `seed + attempt` and an accumulated `overrides` dict. Overrides come in three shapes: `overrides["measures"][col][param_key]` is a multiplicative scalar applied to the per-row param array in `_compute_per_row_params` (compounds across retries — `widen_variance` doubles sigma after two rounds of 1.2×); `overrides["reshuffle"]: list[str]` triggers `rng.permutation` on named columns after measure generation; `overrides["patterns"][idx]["params"]` is merged by `pipeline._apply_pattern_overrides` *before* `run_pipeline` is called again. **Why overrides rather than declaration mutations:** the frozen `DeclarationStore` is never mutated — auto-fix is a deterministic perturbation layer, so the original declarations remain recoverable from `raw_declarations` for Stage 2 re-execution.

See [`../../../docs/svg/module2_gen_engine.md`](../../../docs/svg/module2_gen_engine.md) for the visual walkthrough.

## Usage Example

**Call site 1 — via the SDK** (the primary path; see [`../sdk/simulator.py`](../sdk/simulator.py) lines 184–197):

```python
from pipeline.phase_2.sdk import FactTableSimulator

sim = FactTableSimulator(target_rows=500, seed=42)
sim.add_category("hospital", ["St. Mary", "General"], [0.6, 0.4], group="entity")
sim.add_temporal("visit_date", start="2024-01-01", end="2024-12-31", freq="D", derive=["month"])
sim.add_measure("wait_minutes", "lognormal", {"mu": 2.5, "sigma": 0.4})

df, metadata = sim.generate()  # → calls run_pipeline under the hood
```

**Call site 2 — direct, with captured raw declarations** (Loop B path and Stage 2 re-execution; pattern from [`../pipeline.py`](../pipeline.py) lines 239–254):

```python
from pipeline.phase_2.engine.generator import run_pipeline

# raw_declarations is the dict captured from a prior sandbox run
# (see M3's _TrackingSimulator._sim_registry)
df, metadata = run_pipeline(
    columns=raw_declarations["columns"],
    groups=raw_declarations["groups"],
    group_dependencies=raw_declarations["group_dependencies"],
    measure_dag=raw_declarations["measure_dag"],
    target_rows=raw_declarations["target_rows"],
    seed=raw_declarations.get("seed", 42),
    patterns=raw_declarations.get("patterns", []),
    realism_config=None,          # validation-before-realism ordering
    overrides=None,               # Loop B supplies on retries
    orthogonal_pairs=raw_declarations.get("orthogonal_pairs", []),
)
```

## Dependencies

**Imported from the rest of `phase_2/`:**

- [`phase_2.sdk.dag`](../sdk/dag.py) — `build_full_dag`, `topological_sort`, `extract_measure_sub_dag`.
- [`phase_2.metadata.builder`](../metadata/builder.py) — `build_schema_metadata` (lazy import at `generator.py` line 106).
- [`phase_2.types`](../types.py) — `DimensionGroup`, `GroupDependency`.
- [`phase_2.exceptions`](../exceptions.py) — `InvalidParameterError`, `PatternInjectionError`, `DegenerateDistributionError`.

**External libraries:** `numpy` (arrays + RNG), `pandas` (DataFrame + datetime), `ast` (for `_safe_eval_formula`), `datetime.date` (temporal enumeration), `collections.OrderedDict`.

**Preconditions.** Inputs came from a frozen `DeclarationStore` (M1 invariant). All declaration-time validation (family whitelist, param_model shape, acyclicity) has already run — M2 does **not** re-validate at runtime beyond defensive clamping.

**Postconditions.** Returns `(pd.DataFrame, dict)` where the DataFrame has `len == target_rows`, `RangeIndex`, column order = `topo_order`, and dtypes per the casting policy above. The metadata dict has exactly 7 keys (see M4). No side effects.

## Testing

Unit and integration tests live in [`../tests/modular/`](../tests/modular/):

```bash
# From repo root, chart conda env active
pytest pipeline/phase_2/tests/modular/test_engine_generator.py -v   # orchestration order
pytest pipeline/phase_2/tests/modular/test_engine_measures.py -v    # _safe_eval_formula + structural guards

# Smoke test end-to-end via the SDK
python -m pipeline.phase_2.tests.demo_end_to_end
```
