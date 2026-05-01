# IS-1 + DS-3: Mixture Distribution Sampling & KS Test — Summary of Changes

Co-implements **IS-1** (mixture distribution sampling, formerly stubbed at
`engine/measures.py:360-366` with `NotImplementedError`) and **DS-3** (mixture
KS test, formerly soft-passing at `validation/statistical.py:259-264`).
The two ship together because the sampler and the KS-test mixture CDF must
agree on the same `{"components": [...]}` schema construction.

Adopted decisions follow `docs/stub_analysis/stub_gap_analysis.md` §IS-1 / §DS-3
and `docs/stub_analysis/stub_blocker_decisions.md` §IS-1 / §DS-3 (interpretation
**(a)**: each component carries its own `param_model`; component weights are
constants and auto-normalized to 1.0).

## Schema (the contract added)

```python
{
    "family": "mixture",
    "param_model": {
        "components": [
            {
                "family": <non-mixture supported family>,
                "weight": <positive float>,
                "param_model": {
                    "mu":    {"intercept": <float>, "effects": {<predictor>: {<value>: <float>, ...}}},
                    "sigma": {"intercept": <float>, ...},
                    # ...per-family keys, same shape as a non-mixture stochastic measure
                },
            },
            # ... K components, K >= 1
        ],
    },
}
```

Weights are auto-normalized at sampling and at KS-test time, so `[0.3, 0.2]`
behaves identically to `[0.6, 0.4]`. Nested mixtures are rejected.

## Files changed

### [pipeline/phase_2/types.py](pipeline/phase_2/types.py)

- Added `MixtureComponent(TypedDict)` with fields `family: str`,
  `weight: float`, `param_model: dict[str, Any]`. Inserted next to
  `CensoringSpec` (other config TypedDicts).

### [pipeline/phase_2/engine/measures.py](pipeline/phase_2/engine/measures.py)

- **Refactor** — extracted the family if/elif chain (and the
  `_validate_distribution_params` call) out of `_sample_stochastic` into a new
  `_sample_family(col_name, family, params, n_rows, rng)` helper. This is the
  single dispatch point for all 7 non-mixture families and is reused per
  masked component subset by `_sample_mixture`. Validation runs inside the
  helper so per-component error context (`col_name=f"{col_name}[c{k}]"`) is
  preserved.
- **Refactored** `_sample_stochastic` body — for non-mixture families, computes
  per-row params once via `_compute_per_row_params` then delegates to
  `_sample_family`. For `family == "mixture"`, dispatches to `_sample_mixture`
  (replacing the old `NotImplementedError` block).
- **New** `_sample_mixture(col_name, col_meta, rows, rng, overrides=None)`:
  1. Reads components, normalizes weights.
  2. Per-row component assignment via `rng.choice(K, size=n_rows, p=weights)`.
  3. For each component k: builds minimal `sub_meta = {"param_model": ...}`,
     calls `_compute_per_row_params` against the **full** rows dict (predictor-
     effect masks are derived from `rows[effect_col]` which spans all n_rows;
     pre-masking would break per-row predictor effects), then masks the result
     and dispatches to `_sample_family` on the masked subset.
  4. Defensively initializes the output with `np.zeros` rather than `np.empty`.
- **Autofix interaction** — `overrides` is intentionally not propagated into
  the per-component `_compute_per_row_params` calls. Mixture is opted out of
  the `widen_variance` autofix strategy (see `validation/autofix.py` below).
- Removed the `Raises: NotImplementedError` line from `_sample_stochastic`'s
  docstring.

### [pipeline/phase_2/sdk/validation.py](pipeline/phase_2/sdk/validation.py)

- Added `import numpy as np` to support `np.floating` weight typecheck.
- Extended `validate_param_model` with a dedicated mixture branch (placed
  before the existing `VALIDATED_PARAM_KEYS` block). The branch:
  - Rejects missing / empty / non-list `components`.
  - Rejects non-dict component entries.
  - Rejects unsupported component families and **nested mixtures** (component
    family must be in `SUPPORTED_FAMILIES - {"mixture"}`).
  - Rejects non-numeric weights (accepts `int`, `float`, `np.floating`;
    rejects `bool`) and non-positive weights.
  - Rejects non-dict `param_model`.
  - **Recursively** calls `validate_param_model(f"{name}.components[{i}]", cf,
    sub_pm, columns)` so each component's per-family schema (e.g. Beta's
    `mu`/`sigma` whitelist) is enforced.
  - Returns early before the per-key `validate_param_value` loop, since
    `"components"` does not match the constant/intercept+effects shape.
- All raises use `InvalidParameterError(param_name=..., value=0.0, reason=...)`
  with `components[i].<field>` in the `param_name` for actionable LLM-facing
  error messages.

### [pipeline/phase_2/validation/statistical.py](pipeline/phase_2/validation/statistical.py)

- **New** `_collect_predictor_cols(param_model, columns_meta, out)` — recursive
  helper that walks a param_model (descending into `components` lists for
  mixtures) and collects categorical predictor columns referenced in any
  `effects` block. Replaces the inline loop in `_iter_predictor_cells` (which
  would have crashed on mixture param_models because `param_spec` would be
  the `components` list rather than a dict).
- **New** `_MixtureFrozen` adapter class — exposes `.cdf(x)` so it can be
  passed to `scipy.stats.kstest(sample, dist.cdf)` exactly like a frozen
  scipy distribution. For K components with normalized weights `w_k` and
  frozen scipy distributions `D_k`, `cdf(x) = sum(w_k * D_k.cdf(x))`.
- **New** `_expected_cdf_mixture(params)` — builds an `_MixtureFrozen` from
  a cell-resolved `{"components": [...]}` shape. Returns `None` when any
  component family has no scipy CDF (e.g. poisson) or when the total weight
  is non-positive — preserving the existing per-family soft-pass fallback.
- **Extended** `_expected_cdf` — added `family == "mixture"` branch that
  delegates to `_expected_cdf_mixture`.
- **Extended** `_compute_cell_params` — at function entry, if `param_model`
  has a `components` key, recursively resolves per-cell params for each
  component and returns the shape consumed by `_expected_cdf_mixture`:
  `{"components": [{"family", "weight", "params": <recursive>}, ...]}`.
  Defensively guards `param_spec.get("intercept", 0.0)` against numeric
  scalars (a latent bug surfaced while touching this function). Return type
  widened from `dict[str, float]` to `dict[str, Any]`.
- **Removed** the DS-3 stub block at the old L259-264 of `check_stochastic_ks`.
  The downstream loop now handles mixture transparently:
  `_compute_cell_params` returns the recursive shape →
  `_expected_cdf` dispatches to `_expected_cdf_mixture` →
  `kstest(sample, dist.cdf)` runs against the `_MixtureFrozen.cdf` callable.

### [pipeline/phase_2/validation/autofix.py](pipeline/phase_2/validation/autofix.py)

- Added optional `columns: dict[str, dict[str, Any]] | None = None` kwarg to
  `widen_variance`. When provided and the resolved column has
  `family == "mixture"`, returns `overrides` unchanged with a debug log.
  Default `None` preserves backward compatibility (existing test suite and
  legacy caller bindings keep working).
- Pattern matches `amplify_magnitude`'s `patterns=` precedent — integrators
  bind via `functools.partial(widen_variance, columns=meta["columns"])` when
  wiring the `auto_fix` map. No changes to `generate_with_validation`.
- Documented the limitation in the docstring: mixture has no single sigma to
  widen; per-component widening is out of scope for v1.

## Tests added (61 new, 0 removed; 230 total passing)

### New file [pipeline/phase_2/tests/modular/test_engine_mixture.py](pipeline/phase_2/tests/modular/test_engine_mixture.py) — 18 tests

- `TestTwoComponentMean` — 60% N(0,1) + 40% N(10,1), n=10000 → empirical mean
  ≈ 4.0 within 5%.
- `TestThreeComponentKS` — 3-component mixture; samples pass scipy KS against
  the matching `_MixtureFrozen` CDF.
- `TestWeightNormalization` — `[0.3, 0.2]` and `[0.6, 0.4]` produce identical
  draws under the same seed.
- `TestPredictorEffectsInComponent` — component[0] with region effects; per-
  region empirical means align with the expected mixture mean (0.7·μ_north +
  0.3·20 = 9.5 for north; 2.5 for south).
- `TestSkewedWeights` — weights `[0.999, 0.001]` with n=50 do not crash even
  when component[1]'s mask is empty.
- `TestSingleComponent` — weight `[1.0]` mixture matches the base family
  distribution under KS.
- `TestDispatchThroughSampleStochastic` — confirms the mixture branch is
  reachable via the public `_sample_stochastic` entry point.
- `TestSampleFamilyExtraction` — smoke-tests `_sample_family` dispatch for
  each of the 7 non-mixture families (regression guard for the refactor).
- `TestEdgeCases` — empty rows, missing components, zero weight sum.

### New file [pipeline/phase_2/tests/modular/test_validation_statistical_mixture.py](pipeline/phase_2/tests/modular/test_validation_statistical_mixture.py) — 13 tests

- `TestComputeCellParamsRecursion` — mixture shape, predictor-effect resolution
  per cell.
- `TestMixtureFrozenCDF` — cdf monotone & in [0,1], matches manual weighted
  sum to numerical precision.
- `TestExpectedCdfMixture` — returns `_MixtureFrozen`, dispatches through
  `_expected_cdf("mixture", ...)`, returns `None` for unsupported components /
  empty list / zero-weight, normalizes weights.
- `TestCheckStochasticKsMixture` — KS passes for samples drawn from the
  declared mixture, fails for mismatched distribution, soft-passes when a
  component family has no scipy CDF (e.g. poisson).

### Extended [pipeline/phase_2/tests/modular/test_sdk_validation.py](pipeline/phase_2/tests/modular/test_sdk_validation.py) — 12 new tests

- Replaced the obsolete `test_mixture_not_validated` (which fed a malformed
  component without `param_model` to a now-strict validator) with
  `test_mixture_absent_from_validated_param_keys` (asserting the
  whitelist-exclusion fact only).
- New `TestValidateParamModelMixture` class covering: well-formed acceptance,
  missing components, empty list, non-list, nested mixture, unsupported family,
  non-positive weight (parametrized), non-numeric weight (parametrized),
  numpy float weight, missing `param_model` in component, recursive validation
  of bad component schema, non-dict component.

### Extended [pipeline/phase_2/tests/modular/test_validation_autofix.py](pipeline/phase_2/tests/modular/test_validation_autofix.py) — 3 new tests

- `test_skips_mixture_column_when_columns_provided` — overrides untouched.
- `test_widens_non_mixture_column_when_columns_provided` — non-mixture columns
  still widen when the kwarg is supplied.
- `test_default_columns_none_preserves_legacy_behavior` — legacy calls with
  no `columns=` still widen.

## Verification

```
conda run -n chart pytest pipeline/phase_2/tests/ -x
```

→ **230 passed in 0.69s.** No pre-existing tests removed; the one mixture
test that was rewritten asserts a stronger property than before.

## Known limitations (carried forward)

- **`widen_variance` is a no-op for mixture columns.** The retry loop will
  re-roll seeds on KS failure but will not adapt parameters. Per-component
  sigma widening (which would require extending the `overrides` schema to
  index components) is deferred until a real need surfaces.
- **Per-component overrides not propagated** through `_sample_mixture`. The
  current `overrides["measures"][col]["sigma"]` schema indexes a single sigma
  field; reusing it for mixture would silently apply the same factor to every
  component, which is not meaningful.
- **Cells with any unsupported component family soft-pass** the KS test
  (e.g. a mixture containing a poisson component). This mirrors the existing
  per-family fallback semantics (`_expected_cdf` already returns `None` for
  poisson), and the soft-pass detail string identifies the skip.
