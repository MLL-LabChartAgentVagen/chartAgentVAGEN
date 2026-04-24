# M5 — Validation Engine

## What This Module Does

M5 is the terminal Phase 2 module. It consumes the DataFrame produced by M2 and the 7-key `schema_metadata` produced by M4, runs three layers of checks against them, and drives Loop B — the auto-fix retry loop that re-invokes M2 with parameter overrides until the checks pass or the attempt budget is exhausted. Position in the pipeline: **downstream** of both M2 (DataFrame) and M4 (metadata); **upstream** of Phase 3 only indirectly — Phase 3 consumes the `(df, metadata, ValidationReport)` triple that M5 produces, routed through `pipeline._run_loop_b`. Boundary: M5 never mutates declarations and never mutates the DataFrame it validates; on failure it either returns a report with `all_passed=False` (the single-call path) or accumulates a `ParameterOverrides` dict that the next M2 invocation consumes (the Loop B path). Realism injection is deferred until after Loop B passes — so the validator always sees clean data.

## Internal Structure

```
pipeline/phase_2/validation/
├── __init__.py              # re-exports SchemaAwareValidator
├── validator.py             # SchemaAwareValidator — L1/L2/L3 orchestrator
├── structural.py            # L1: row count, cardinality, weights, finiteness, χ², DAG acyclicity
├── statistical.py           # L2: KS tests, residual analysis, conditional transitions
├── pattern_checks.py        # L3: outlier/trend/reversal + 3 stubs
└── autofix.py               # Loop B driver + 3 override strategies
```

**Data flow.** `SchemaAwareValidator(meta).validate(df, patterns)` creates a fresh `ValidationReport`, runs `_run_l1 → _run_l2 → _run_l3` in sequence, and appends each layer's `Check` objects into the report's accumulating list. `_run_l3` is conditional on `patterns` being truthy; `_run_l2` dispatches per measure column based on `measure_type` ("structural" vs "stochastic"). When called inside Loop B, `generate_with_validation` supplies a `build_fn(seed, overrides)` closure (which wraps `run_pipeline`), loops up to `max_attempts` times with `base_seed + attempt`, matches each failure's `Check.name` against the caller's `auto_fix` glob-pattern map, and calls the matched strategy to mutate the `ParameterOverrides` dict. Realism is applied only after the loop terminates with `all_passed` (or after exhaustion).

## Key Interfaces

### External-facing (1): [`SchemaAwareValidator`](validator.py) (in `validator.py`)

```python
from pipeline.phase_2.validation import SchemaAwareValidator

validator = SchemaAwareValidator(meta: dict[str, Any])
report: ValidationReport = validator.validate(
    df: pd.DataFrame,
    patterns: list[dict[str, Any]] | None = None,
)
```

`meta` is the 7-key dict from M4 (stored as an immutable reference on `self.meta`). `validate()` returns a `ValidationReport` with `report.checks: list[Check]`, `report.all_passed: bool` (vacuously True for an empty report), and `report.failures: list[Check]` (fresh list each call). `Check(name, passed, detail=None)`. L3 is skipped when `patterns` is falsy; exceptions inside L2/L3 checks are caught and converted into failed `Check` entries (rather than propagating), so one broken check never masks others.

### External-facing (2): [`generate_with_validation`](autofix.py) (in `autofix.py`)

```python
from pipeline.phase_2.validation.autofix import generate_with_validation

df, meta, report = generate_with_validation(
    build_fn: Callable[[int, ParameterOverrides | None], tuple[pd.DataFrame, dict]],
    meta: dict[str, Any],
    patterns: list[dict[str, Any]],
    base_seed: int = 42,
    max_attempts: int = 3,
    auto_fix: dict[str, Any] | None = None,
    realism_config: dict[str, Any] | None = None,
) -> tuple[pd.DataFrame, dict, ValidationReport]
```

The Loop B driver. `build_fn` is typically a closure over M2's `run_pipeline`. `auto_fix` is a dict of `glob_pattern → strategy_callable` (e.g. `{"ks_*": widen_variance, "outlier_*": amplify_magnitude, "orthogonal_*": reshuffle_pair}`); if `auto_fix is None`, the loop still validates but no overrides accumulate, so subsequent attempts only differ by seed.

### Per-layer checks (module-level functions)

- **L1 structural** ([`structural.py`](structural.py)) — `check_row_count(df, meta)`, `check_categorical_cardinality(df, meta)`, `check_marginal_weights(df, meta)`, `check_measure_finiteness(df, meta)`, `check_orthogonal_independence(df, meta)`, `check_measure_dag_acyclic(meta)`.
- **L2 statistical** ([`statistical.py`](statistical.py)) — `check_stochastic_ks(df, col_name, meta, patterns=None)`, `check_structural_residuals(df, col_name, meta, patterns=None)`, `check_group_dependency_transitions(df, meta)`.
- **L3 pattern** ([`pattern_checks.py`](pattern_checks.py)) — `check_outlier_entity(df, pattern)`, `check_trend_break(df, pattern, meta)`, `check_ranking_reversal(df, pattern, meta)`, plus stubs `check_dominance_shift`, `check_convergence`, `check_seasonal_anomaly` (all three currently return `Check(passed=True, detail="... not yet implemented")`).

### Loop B strategies ([`autofix.py`](autofix.py))

- `match_strategy(check_name, auto_fix) -> Callable | None` — `fnmatch`-based dispatch; returns the first matching strategy or `None`.
- `widen_variance(check, overrides, factor=1.2)` — multiplies `overrides["measures"][col]["sigma"]`; compounds across retries (1.2 → 1.44 → 1.728).
- `amplify_magnitude(check, overrides, patterns=None, factor=1.3)` — multiplies `overrides["patterns"][idx]["params"]["z_score"]` or `["magnitude"]` for the pattern matching the failed check's column.
- `reshuffle_pair(check, overrides)` — appends a column name to `overrides["reshuffle"]` (idempotent); M2 calls `rng.permutation` on flagged columns after measure generation.

## How It Works

### Why three layers, in this order

The L1/L2/L3 design is a **cost-vs-fidelity gradient**: cheap structural invariants first, expensive distributional checks second, narrative-specific checks last. Each layer assumes the previous one's invariants hold, so a cascading failure model is avoided.

- **L1 — structural** runs deterministic, near-O(n) checks. Row count is a simple arithmetic test. `check_categorical_cardinality` validates `df[col].nunique() == meta["columns"][col]["cardinality"]`. `check_marginal_weights` compares observed value frequencies of each root categorical against declared weights with max-deviation threshold 0.10. `check_measure_finiteness` verifies `notna().all() and isfinite().all()` per measure. `check_orthogonal_independence` runs `scipy.stats.chi2_contingency(root_a, root_b)` and passes if `p > 0.05`. `check_measure_dag_acyclic` is a redundant defense-in-depth check on `meta["measure_dag_order"]`. **Why first:** these are failure modes that invalidate every subsequent check — if the row count is off by 50% or a measure is full of NaN, running a KS test is meaningless. Running them first also gives Loop B's strategy matcher cheap signals to act on before burning budget on heavier checks.
- **L2 — statistical** validates **distributional fit**. `check_stochastic_ks` enumerates predictor cells (Cartesian product of categoricals named in `param_model.effects`), reconstructs the expected parameters per cell (`intercept + Σ effects`), and runs `scipy.stats.kstest` against the declared family; passes if `p > 0.05`. Cell enumeration is bounded (`min_rows=5`, `max_cells=100`) to keep runtime predictable on high-cardinality declarations. `check_structural_residuals` recomputes the formula from actual upstream values (reusing `engine.measures._safe_eval_formula` and `_resolve_effects` to guarantee semantic parity with M2), then tests whether `residuals.std()` matches declared noise (ratio within 0.2 for noisy measures; below 1e-6 for deterministic ones). `check_group_dependency_transitions` computes the observed conditional distribution of each child root given its parent values and compares to declared `conditional_weights` with max-deviation 0.10. **Why second:** these are **probabilistic** — they can fail by chance on small samples. Running them after L1 means every L2 failure is explainable in terms of the declared distribution, not an artifact of broken cardinality or missing-data pollution.
- **L3 — pattern** validates that the **injected narrative is actually detectable**. `check_outlier_entity` uses complement statistics (mean/std computed from rows *not* in the pattern target) to avoid circular contamination, and passes if the target subset's z-score ≥ 2.0. `check_trend_break` locates the temporal column, partitions target rows at `break_point`, and checks relative magnitude change > 15%. `check_ranking_reversal` computes Spearman rank correlation between the two named metrics and passes if negative. **Why last:** patterns are the layer the LLM most often gets wrong — a declared `outlier_entity` with `z_score=3.0` that the engine implements correctly can still fail the L3 check because the population std happened to be small. This is precisely what Loop B's `amplify_magnitude` is designed to fix.

**Why exception-safe check execution.** Both `_run_l2` and `_run_l3` wrap each check in `try/except`, converting any exception into a failed `Check` with the error message in `detail`. This is deliberate: a scipy numerical edge case in `check_stochastic_ks` for one measure must not block checking the other measures, and Loop B needs a stable report structure to match failures against strategies.

### The auto-fix loop (Loop B)

`generate_with_validation` implements the retry loop with three key design decisions:

1. **Strategies accumulate overrides, they don't replace declarations.** `widen_variance` multiplies the current sigma factor, so two retries with 1.2× compound to 1.44×. The frozen `DeclarationStore` is never touched. **Why accumulation rather than replacement:** it means a partial fix on attempt 2 composes with another partial fix on attempt 3, rather than clobbering it. It also keeps Loop B deterministic in the sense that the same sequence of failures produces the same override trajectory.
2. **Seed increments every attempt** (`seed = base_seed + attempt`). **Why:** different draws from the same RNG family can pass a KS test when the first draw failed, even with identical parameters. Incrementing the seed is what makes `reshuffle_pair` (which only flags a column) actually produce a different permutation — the engine's `rng.permutation` consumes the advanced seed.
3. **Validation runs pre-realism; realism is applied only after pass (or after exhaustion).** `build_fn` is constructed in `pipeline._run_loop_b` with `realism_config=None` forced. **Why:** `inject_realism` injects NaN and string perturbations, which would fail `check_measure_finiteness` and skew KS tests. Re-applying realism after validation means the validator always sees the clean signal; the downstream consumer then gets realism as a post-processing layer.

**Why no built-in default strategy map.** If `auto_fix is None`, the loop short-circuits the match/apply step — each attempt only differs by seed. **Reason:** the pattern-to-strategy mapping is an **integration decision** that depends on how aggressive the caller wants to be. Shipping a default would both hide the mechanism and risk surprising regressions when the defaults change. Big README §9 documents the recommended map (`marginal_*`/`ks_*` → `widen_variance`; `outlier_*`/`trend_*` → `amplify_magnitude`; `orthogonal_*` → `reshuffle_pair`) as an integrator's recipe rather than a guarantee.

**Why typed `Check.name` conventions.** Check names follow `<kind>_<column>` patterns (`row_count`, `cardinality_<col>`, `ks_<col>`, `outlier_<col>`, `trend_<col>`). That predictable shape is what `match_strategy` exploits via `fnmatch` globs, and what `_extract_col_from_check_name` uses to identify which measure to widen. String-matching on human-readable `Check.detail` would be brittle (the detail text changes with each improvement); the name conventions are the stable contract.

See [`../../../docs/svg/module5_validation_engine.md`](../../../docs/svg/module5_validation_engine.md) for the visual walkthrough.

## Usage Example

**One-shot validation** (the path a Phase 3 tool would take when inspecting an already-generated scenario):

```python
from pipeline.phase_2.validation import SchemaAwareValidator

# df and meta came from phase_2 generation (sim.generate() or run_pipeline)
validator = SchemaAwareValidator(meta)
report = validator.validate(df, patterns=meta.get("patterns"))

if not report.all_passed:
    for check in report.failures:
        print(f"FAIL {check.name}: {check.detail}")
```

**Loop B — validation-driven regeneration** (the Phase 2 production path; closure pattern from [`../pipeline.py`](../pipeline.py) lines 239–264):

```python
from pipeline.phase_2.engine.generator import run_pipeline
from pipeline.phase_2.validation.autofix import (
    generate_with_validation, widen_variance, amplify_magnitude, reshuffle_pair,
)

# raw_declarations came from M3's _TrackingSimulator._sim_registry
def build_fn(seed, overrides):
    return run_pipeline(
        columns=raw_declarations["columns"],
        groups=raw_declarations["groups"],
        group_dependencies=raw_declarations["group_dependencies"],
        measure_dag=raw_declarations["measure_dag"],
        target_rows=raw_declarations["target_rows"],
        seed=seed,
        patterns=raw_declarations.get("patterns", []),
        realism_config=None,           # validation-before-realism
        overrides=overrides,
        orthogonal_pairs=raw_declarations.get("orthogonal_pairs", []),
    )

auto_fix = {
    "ks_*":           widen_variance,
    "marginal_*":     widen_variance,
    "outlier_*":      amplify_magnitude,
    "trend_*":        amplify_magnitude,
    "orthogonal_*":   reshuffle_pair,
}

df, meta, report = generate_with_validation(
    build_fn=build_fn,
    meta=metadata_from_loop_a,
    patterns=raw_declarations.get("patterns", []),
    base_seed=raw_declarations.get("seed", 42),
    max_attempts=3,
    auto_fix=auto_fix,
    realism_config={"missing_rate": 0.02},  # applied post-validation
)
```

## Dependencies

**Imported from the rest of `phase_2/`:**

- [`phase_2.types`](../types.py) — `Check`, `ValidationReport`, `ParameterOverrides`.
- [`phase_2.engine.measures`](../engine/measures.py) — `_safe_eval_formula`, `_resolve_effects` (reused by `check_structural_residuals` to guarantee the validator's residual computation matches what the engine produced).
- [`phase_2.engine.realism`](../engine/realism.py) — `inject_realism`, applied by `generate_with_validation` post-validation when `realism_config` is provided.
- [`phase_2.sdk.validation`](../sdk/validation.py) — `extract_formula_symbols` (used internally by L2 to identify formula-dependency columns for exclusion).
- [`phase_2.exceptions`](../exceptions.py) — `PatternInjectionError`.

**External libraries:** `pandas`, `numpy`, `scipy.stats` (`chi2_contingency`, `kstest`, and distribution objects `norm`/`lognorm`/`expon`/`gamma`/`beta`/`uniform`), `fnmatch`, `itertools.product`, `logging`.

**Preconditions.** `df` is the DataFrame returned by M2 (has `len == meta["total_rows"]` and column order matching `meta["measure_dag_order"]` ∪ declared columns). `meta` is the 7-key dict from M4. `patterns` has the same shape as the list stored in `meta["patterns"]`.

**Postconditions.** `validate()` returns a `ValidationReport` whose `checks` list is freshly allocated and can be mutated safely; `generate_with_validation` returns `(df, meta, report)` where `df` has had realism injected iff `realism_config` was non-`None` and the pre-realism report passed. Neither path mutates inputs.

## Testing

```bash
# From repo root, chart conda env active
pytest pipeline/phase_2/tests/modular/test_validation_validator.py -v    # orchestrator + L3 exception safety
pytest pipeline/phase_2/tests/modular/test_validation_structural.py -v   # L1 checks
pytest pipeline/phase_2/tests/modular/test_validation_autofix.py -v      # strategy matchers + override accumulation
```
