# M1 — SDK Surface

## What This Module Does

M1 is the strongly-typed, builder-pattern API that LLM-generated scripts call to describe a fact table. Each declaration call is validated incrementally and mutates a shared `DeclarationStore` held by the `FactTableSimulator` instance. Position in the pipeline: **upstream** of M2 (generation engine) and M4 (schema metadata), **downstream** of M3 (LLM orchestration executes the script inside a sandbox). Boundary: M1 never touches data values — only declarations. On `generate()` the store is frozen and handed off to M2, which in turn calls M4 inline; on any declaration failure, a typed exception propagates back to M3 for Loop A retry feedback.

## Internal Structure

```
pipeline/phase_2/sdk/
├── __init__.py          # re-exports FactTableSimulator
├── simulator.py         # FactTableSimulator — thin delegation shell + phase guard
├── columns.py           # Step 1: add_category / add_temporal / add_measure / add_measure_structural
├── relationships.py     # Step 2: declare_orthogonal / add_group_dependency / inject_pattern / set_realism
├── groups.py            # DimensionGroup registry: register, hierarchy lookup, temporal special case
├── dag.py               # graph algorithms + full-DAG assembly from 5 edge sources
└── validation.py        # declaration-time validators (family, param_model, weights, formulas)
```

**Data flow.** The caller holds a `FactTableSimulator` and invokes Step 1 methods to populate columns, then Step 2 methods to declare relationships. `simulator.py` methods are almost pure forwarding: they enforce the declaring-vs-relating phase guard, call `store._check_mutable()`, and delegate to the stateless functions in `columns.py` / `relationships.py`. Those helpers validate inputs via `validation.py`, update `groups.py`'s registry, and run incremental acyclicity checks via `dag.py`. Nothing is computed at declaration time beyond validation and registry updates — the unified DAG and measure order are only built later, during M2 pre-flight.

## Key Interfaces

### External-facing: `FactTableSimulator` (in [`simulator.py`](simulator.py))

```python
from pipeline.phase_2.sdk import FactTableSimulator

sim = FactTableSimulator(target_rows: int, seed: int = 42)
```

Raises `TypeError` if `target_rows` or `seed` is not an `int` (bools rejected), `ValueError` if `target_rows <= 0`. Initializes an empty `DeclarationStore` and sets internal phase to `"declaring"`.

**Step 1 — column declarations** (must all complete before any Step 2 call; mixing raises `InvalidParameterError`):

| Method | Signature | Behavior |
|---|---|---|
| `add_category` | `(name, values: list[str], weights: list[float] \| dict[str, list[float]], group: str, parent: str \| None = None) -> None` | Declares a categorical dimension column. Accepts either a flat weights list (for roots) or a per-parent-value dict (for children). Weights are auto-normalized to sum to 1.0. Raises `DuplicateColumnError`, `EmptyValuesError`, `ParentNotFoundError`, `WeightLengthMismatchError`, `DuplicateGroupRootError`. |
| `add_temporal` | `(name, start: str, end: str, freq: str, derive: list[str] \| None = None) -> None` | Declares a temporal root column + one derived column per entry in `derive`. `start`/`end` are ISO-8601 date strings; `freq` is one of `"D"`, `"W-MON"`–`"W-SUN"`, `"MS"`; `derive` values are whitelisted to `{"day_of_week", "month", "quarter", "is_weekend"}`. All temporal columns auto-join the reserved `"time"` group. |
| `add_measure` | `(name, family: str, param_model: dict[str, Any]) -> None` | Declares a stochastic measure. `family` ∈ `{gaussian, lognormal, gamma, beta, uniform, poisson, exponential, mixture}`. `param_model` accepts either numeric scalars or `{intercept, effects}` dicts where `effects` keys are declared categorical columns. Raises `InvalidParameterError`, `UndefinedEffectError`. The `scale=...` kwarg was removed — passing it now raises `TypeError`. |
| `add_measure_structural` | `(name, formula: str, effects: dict[str, dict[str, float]] \| None = None, noise: dict[str, Any] \| None = None) -> None` | Declares a formula-based measure. Every identifier symbol in `formula` must resolve to a declared measure or to a key in `effects`. Measure-to-measure dependencies update the measure DAG; incremental acyclicity is enforced via `dag.check_measure_dag_acyclic`. Raises `CyclicDependencyError`, `UndefinedEffectError`. |

**Step 2 — relationships and patterns** (first Step 2 call flips phase `declaring → relating`; further Step 1 calls rejected):

| Method | Signature | Behavior |
|---|---|---|
| `declare_orthogonal` | `(group_a: str, group_b: str, rationale: str = "") -> None` | Declares two dimension groups statistically independent. Both groups must exist; must not be the same; must not already have a declared dependency (mutual exclusion). |
| `add_group_dependency` | `(child_root: str, on: list[str], conditional_weights: dict[str, dict[str, float]]) -> None` | Declares a cross-group root-level dependency. `len(on) == 1` required (multi-column raises `NotImplementedError`). Both `child_root` and `on[0]` must be roots of their groups. `conditional_weights` must cover every parent value and every child value; vectors are normalized per row. Raises `NonRootDependencyError`, `CyclicDependencyError`, `ValueError`. |
| `inject_pattern` | `(type: str, target: str, col: str, params: dict \| None = None, **extra_params) -> None` | Declares a narrative pattern. Currently `VALID_PATTERN_TYPES = {"outlier_entity", "trend_break"}`; other types in the spec raise `ValueError`. `target` is a DataFrame query expression; `col` must be a declared measure column. Accepts both `params={...}` and kwargs styles (kwargs merged over `params`). Required params: `outlier_entity` needs `z_score`; `trend_break` needs `break_point` and `magnitude`. |
| `set_realism` | `(missing_rate: float = 0.0, dirty_rate: float = 0.0, censoring: dict \| None = None) -> None` | Configures post-generation data-quality degradation. Rates must be in `[0.0, 1.0]`. `censoring` is accepted for forward-compatibility but raises `NotImplementedError` at engine time. |

**Terminal:**

```python
df, schema_metadata = sim.generate()  # returns (pd.DataFrame, dict[str, Any])
```

Calls `store.freeze()` before running M2; any declaration method called after `generate()` raises `RuntimeError` from `DeclarationStore._check_mutable`.

### Internal-facing (stateless module-level functions)

All of these accept explicit registry parameters — no hidden `self` — so tests can exercise them directly and a future alternate frontend could reuse them.

- [`columns.py`](columns.py): `add_category`, `add_temporal`, `add_measure`, `add_measure_structural`, `_parse_iso_date`.
- [`relationships.py`](relationships.py): `declare_orthogonal`, `add_group_dependency`, `inject_pattern`, `set_realism`, plus module-level constants `VALID_PATTERN_TYPES` and `PATTERN_REQUIRED_PARAMS` and private conflict checkers.
- [`groups.py`](groups.py): `register_categorical_column`, `register_temporal_group`, `get_roots`, `is_group_root`, `get_group_for_column`.
- [`dag.py`](dag.py): `detect_cycle_in_adjacency` (Kahn + DFS path extraction), `topological_sort` (Kahn with `heapq` lexicographic tie-break, raises `CyclicDependencyError`), `extract_measure_sub_dag`, `build_full_dag` (5 edge sources), `collect_stochastic_predictor_cols`, `collect_structural_predictor_cols`, `check_measure_dag_acyclic`, `check_root_dag_acyclic`.
- [`validation.py`](validation.py): `validate_column_name`, `validate_parent`, `validate_and_normalize_flat_weights`, `validate_and_normalize_dict_weights`, `normalize_weight_dict_values`, `validate_family`, `validate_param_model`, `validate_param_value`, `validate_effects_in_param`, `validate_structural_effects`, `extract_formula_symbols`, `validate_root_only`, plus whitelists (`SUPPORTED_FAMILIES`, `TEMPORAL_DERIVE_WHITELIST`, `VALIDATED_PARAM_KEYS`).

## How It Works

Execution order, with the WHY of each choice:

1. **Construction.** `FactTableSimulator.__init__` creates an empty `DeclarationStore(target_rows, seed)` and aliases each registry attribute (`_columns`, `_groups`, `_measure_dag`, etc.) onto `self` so Step 1/Step 2 helpers can mutate shared dict/list references. `_realism_config` is a property rather than a raw alias because `set_realism` reassigns it (doesn't mutate in place), and a stale alias would silently drop writes.
2. **Step 1 calls.** Each method calls `store._check_mutable()` (guards against post-`generate()` mutation) then `_ensure_declaring_phase()`, then forwards to the stateless function in [`columns.py`](columns.py). These helpers validate inputs, then mutate the registries directly. **Why stateless module-level helpers instead of methods:** tests can exercise validation without standing up a simulator, and if a future non-LLM frontend needs to reuse the same validation, it can call them without inheriting from `FactTableSimulator`.
3. **Phase transition.** The first Step 2 call hits `_ensure_relating_phase()`, which flips `self._phase` from `"declaring"` to `"relating"`. This is one-way — subsequent Step 1 calls raise `InvalidParameterError` through `_ensure_declaring_phase()`. **Why enforce ordering:** Step 2 registries reference columns and groups declared in Step 1 (e.g. `declare_orthogonal("geo", "time")` assumes both groups exist; `add_group_dependency(child_root, ...)` assumes `child_root` is a registered root). Allowing the caller to interleave creates states where validators can't give a useful error at the point of the mistake.
4. **Step 2 calls.** Declared relationships are checked against existing state: `declare_orthogonal` refuses to declare groups already tied by a `group_dependency`, and vice versa (mutual exclusion — a pair can't both be independent *and* have a conditional relationship). `add_group_dependency` enforces root-only (`NonRootDependencyError`) and runs `check_root_dag_acyclic` before appending.
5. **Incremental acyclicity.** Every structural addition (`add_measure_structural`, `add_group_dependency`) runs a full cycle check on a tentative adjacency before mutating the registry. **Why check early instead of at `generate()`:** the caller's stack frame, with the offending identifier, is still on screen when the exception fires. Deferring catches would point the LLM at the wrong edit.
6. **`generate()`.** Calls `self._store.freeze()` (sets `_frozen = True`; subsequent `_check_mutable()` raises `RuntimeError`), then invokes `engine.generator.run_pipeline` with the decomposed registry fields. **Why freeze on `generate()` and not at construction:** callers (tests, debugging) can still inspect `sim._columns`, `sim._measure_dag`, etc., before committing. Freezing at construction would force an awkward setter pattern.
7. **Full DAG assembly (inside `run_pipeline`).** `dag.build_full_dag` assembles edges from **five sources** — (1) within-group hierarchy (categorical `parent → child`), (2) cross-group root dependencies (`on[0] → child_root`), (3) temporal derivation (`root → derived features`), (4) measure predictor references (any categorical column named in a stochastic `param_model.effects` or a structural `effects` dict becomes an edge `predictor → measure`), (5) measure-to-measure edges from `measure_dag`. Edges are deduplicated, then a final `detect_cycle_in_adjacency` runs as defense-in-depth. **Why five sources rather than a single edge type:** each relationship has genuinely different origin and semantics; conflating them would require callers to understand a synthetic edge model. The five-source decomposition is how the big README documents the DAG contract.
8. **Topological sort.** `dag.topological_sort` uses Kahn's algorithm with a `heapq` min-heap for lexicographic tie-breaking — determinism across runs matters because M2 consumes a single shared RNG in the same order the topo sort visits columns.

See [`../../../docs/svg/module1_sdk_surface.md`](../../../docs/svg/module1_sdk_surface.md) for the visual walkthrough.

## Usage Example

Minimal script based on [`tests/demo_end_to_end.py`](../tests/demo_end_to_end.py), extended to exercise Step 2:

```python
from pipeline.phase_2.sdk import FactTableSimulator

sim = FactTableSimulator(target_rows=500, seed=42)

# Step 1: column declarations
sim.add_category(
    "hospital", ["St. Mary", "General"], [0.6, 0.4],
    group="entity",
)
sim.add_temporal(
    "visit_date", start="2024-01-01", end="2024-12-31",
    freq="D", derive=["month", "day_of_week"],
)
sim.add_measure(
    "wait_minutes", "lognormal",
    {"mu": 2.5, "sigma": 0.4},
)

# Step 2: relationships + patterns
sim.declare_orthogonal("entity", "time", rationale="no seasonal admission bias")
sim.inject_pattern(
    type="outlier_entity",
    target="hospital == 'St. Mary'",
    col="wait_minutes",
    z_score=3.0,
)
sim.set_realism(missing_rate=0.02)

df, meta = sim.generate()
print(df.shape, list(meta.keys()))
# (500, 5) ['dimension_groups', 'orthogonal_groups', 'group_dependencies',
#          'columns', 'measure_dag_order', 'patterns', 'total_rows']
```

For an end-to-end sandbox invocation (the path M3 uses), see [`tests/demo_end_to_end.py`](../tests/demo_end_to_end.py).

## Dependencies

**Imported from the rest of `phase_2/`:**

- [`phase_2.types`](../types.py) — `DeclarationStore`, `DimensionGroup`, `OrthogonalPair`, `GroupDependency`.
- [`phase_2.exceptions`](../exceptions.py) — `InvalidParameterError`, `DuplicateColumnError`, `DuplicateGroupRootError`, `EmptyValuesError`, `WeightLengthMismatchError`, `ParentNotFoundError`, `NonRootDependencyError`, `CyclicDependencyError`, `UndefinedEffectError`, and peers.
- [`phase_2.engine.generator`](../engine/generator.py) — `run_pipeline`, called from `FactTableSimulator.generate()`.
- [`phase_2.metadata.builder`](../metadata/builder.py) — called indirectly by `run_pipeline`, which produces the metadata dict returned from `generate()`.

**External libraries:** `pandas` (typing only — the DataFrame is materialized by M2), `collections.OrderedDict`, `datetime.date`, `heapq`, `re`, `logging`.

**Preconditions.** A caller has imported `from pipeline.phase_2.sdk import FactTableSimulator` (run from the repo root — `conftest.py` puts the repo root on `sys.path` so `pipeline.*` resolves). If invoked inside the M3 sandbox, `FactTableSimulator` is pre-injected as `_TrackingSimulator` so M3 can recover raw declarations after `generate()`, and a restricted `__import__` also resolves the `phase_2.sdk` alias.

**Postconditions.** `generate()` returns `(pd.DataFrame, dict)` where the dict has the 7 keys produced by M4. After `generate()`, the `DeclarationStore` is immutable — any further declaration method raises `RuntimeError`.

## Testing

Unit tests live in [`../tests/modular/`](../tests/modular/):

```bash
# From repo root
pytest pipeline/phase_2/tests/modular/test_sdk_columns.py
pytest pipeline/phase_2/tests/modular/test_sdk_dag.py
pytest pipeline/phase_2/tests/modular/test_sdk_validation.py

# End-to-end smoke demo (direct SDK + sandbox)
python -m pipeline.phase_2.tests.demo_end_to_end

# Loop A retry-feedback integration
pytest pipeline/phase_2/tests/test_retry_feedback.py
```
