# AGPDS Phase 2 — Stub Gap Analysis

## Context

This document analyzes every intentional and dependent stub remaining in the
AGPDS Phase 2 codebase, after the Sprint 6 closeout that left the inventory
recorded in `stage5_anatomy_summary.md` §4 /
`pipeline/phase_2/docs/remaining_gaps.md`.

The goal is to drive a focused decision about which stubs to close, in what
order, and with what spec input — by establishing for each one (a) what the
code currently does, (b) what the spec actually says, (c) where the gap is,
(d) what blocks closing it, and (e) what a concrete implementation would
look like.

### Scope

10 stubs: 6 intentional (IS-1..IS-6) + 4 dependent (DS-1..DS-4).

For each stub, this document records — in three phases of analysis:

**Phase A — Inventory confirmation and code reading**
1. Verbatim code span at the actual current location (line numbers
   verified against live source).
2. All sections of `phase_2.md` that reference the feature.
3. Tests in `pipeline/phase_2/tests/` (root + `modular/`) that
   exercise, skip, or reference the stub.
4. Dependent stubs (children that depend on this stub being filled
   first).

**Phase B — Gap analysis**
5. Role in pipeline — where it sits in the §2.8 / §2.9 execution flow,
   what consumes it, what it consumes.
6. Gap analysis — what spec defines, what spec is silent on, what the
   implementation gap is.
7. Dependency chain — what this stub blocks (children), what blocks it
   (parents and spec decisions), and what it must be implemented
   alongside.

**Phase C — Solution proposal**
8. Blocking questions — only genuinely unanswerable ones (spec or
   architectural).
9. Proposed solution — function signatures, implementation sketch,
   integration points, new types if any.
10. Test criteria — what tests must verify.
11. Estimated scope — trivial / small / medium / large, justified by
    comparison to an existing analog.

### Sources read

- `pipeline/phase_2/engine/measures.py`, `engine/realism.py`,
  `engine/patterns.py`
- `pipeline/phase_2/validation/pattern_checks.py`,
  `validation/statistical.py`
- `pipeline/phase_2/sdk/columns.py`, `sdk/simulator.py`,
  `sdk/relationships.py`
- `pipeline/phase_2/orchestration/prompt.py`,
  `orchestration/sandbox.py`
- `pipeline/phase_2/pipeline.py`
- `pipeline/phase_2/docs/artifacts/phase_2.md`
- All test files under `pipeline/phase_2/tests/` and `tests/modular/`

---

# Intentional stubs (6)

## [IS-1] Mixture distribution sampling

### Code span
```python
# pipeline/phase_2/engine/measures.py:360-366
if family == "mixture":
    raise NotImplementedError(
        "mixture distribution sampling not yet implemented. "
        "Expected param_model schema: {'components': [{'family': str, "
        "'weight': float, 'params': {...}}, ...]}"
    )
```
(Note: CLAUDE.md lists `~L297-303`; actual location is L360-366 in the current
source — line numbers have drifted post-implementation.)

### Spec references
- §2.1.1 (L51–94): `add_measure()` declaration lists `"mixture"` as a supported
  distribution alongside `gaussian`, `lognormal`, `gamma`, `beta`, `uniform`,
  `poisson`, `exponential` (`SUPPORTED_DISTRIBUTIONS`, L94).
- §2.3 (L162–196): Closed-form measure declaration — defines how stochastic
  root measures are sampled from family-distributed parameters that depend on
  categorical context. Mixture is implicitly covered but no per-family
  parameter schema is given.
- §2.5 (L302): LLM Code Generation Prompt's allowed-distributions list
  includes `"mixture"`.

### Existing tests
- (none found)

### Dependent stubs
- DS-3: Mixture KS test — `pipeline/phase_2/validation/statistical.py:259-264`

### Role in pipeline
Sits in §2.8 step β (measure generation) inside `_sample_stochastic` at
[engine/measures.py:329-378](pipeline/phase_2/engine/measures.py#L329-L378).
Upstream: receives per-row predictor values built by α-step plus `col_meta`
with `family="mixture"`. Downstream: outputs the sampled column, which is
consumed by structural measures referencing it, by the L2 KS validator
(where DS-3 also stubs out), and ultimately by Phase 3 view extraction.
Triggered when an LLM script declares `sim.add_measure(name, "mixture",
param_model)` and the engine reaches the column's topological position.

### Gap analysis
- **Spec defines:** `"mixture"` is in `SUPPORTED_DISTRIBUTIONS` (§2.1.1 L94,
  §2.5 L302). §2.3 sketches the general parameter pattern as
  `intercept + sum(effects)` for stochastic measures.
- **Spec is silent on:** the parameter schema for mixture — there is no
  `components: [{family, weight, params}]` schema in §2.1.1 or §2.3, no
  example anywhere in §2.5 or the One-Shot Example, and no rule for how
  mixture interacts with predictor effects (do components share predictors,
  do weights vary by predictor, etc.).
- **Implementation gap:** the sampler raises `NotImplementedError`. Even
  the schema suggested in the error message
  (`{components: [{family, weight, params}]}`) is the *implementation's
  guess*, not a spec-defined contract. Filling this stub requires (a) a
  spec extension defining the mixture schema, (b) a sampler implementation,
  and (c) a matching CDF builder for L2 (DS-3).

### Dependency chain
- **Blocks:** DS-3 (mixture KS test). Without a sampling algorithm there
  is no distribution to test against; without a defined component schema
  `_expected_cdf` has no shape to build.
- **Blocked by:** spec extension defining the mixture `param_model` schema.
  This is a **spec gap**, not just a code gap.
- **Co-dependent with:** DS-3. The two must be implemented together so the
  CDF used by the validator agrees with the sampler. Independent
  implementations would diverge.

### Blocking questions
- **Spec:** how does mixture interact with predictor effects? Three
  plausible interpretations: (a) each component carries its own
  `param_model` with `intercept + effects`, weights are constants;
  (b) component params are constants, but mixture weights vary by
  predictor; (c) both vary. (a) is the closest analog to existing
  patterns; (b)/(c) are richer but harder to validate.
- **Spec:** are component families restricted to continuous-only, or is a
  mixed-type mixture (e.g., gaussian + poisson) allowed? Affects KS
  testability.

### Proposed solution
Pick interpretation (a). Refactor the existing dispatch in
`_sample_stochastic` to extract a reusable `_sample_family` helper, then
add `_sample_mixture` that loops over components.

```python
# pipeline/phase_2/engine/measures.py — replace the NotImplementedError
# block at L360-366 with a dispatch to _sample_mixture.

def _sample_family(
    family: str,
    params: dict[str, np.ndarray],
    n_rows: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Family-dispatch helper extracted from _sample_stochastic L387-403."""
    mu = params.get("mu", np.zeros(n_rows))
    sigma = params.get("sigma", np.ones(n_rows))
    if family == "gaussian":
        return rng.normal(mu, sigma)
    elif family == "lognormal":
        return rng.lognormal(mu, sigma)
    # ... gamma, beta, uniform, poisson, exponential
    else:
        raise ValueError(f"Unknown distribution family: '{family}'")


def _sample_mixture(
    col_name: str,
    col_meta: dict[str, Any],
    rows: dict[str, np.ndarray],
    rng: np.random.Generator,
    overrides: dict | None = None,
) -> np.ndarray:
    """Sample from a mixture distribution.

    Schema (per blocking-question decision (a)):
        param_model = {
            "components": [
                {"family": str, "weight": float, "param_model": {...}},
                ...
            ]
        }
    Each component's `param_model` follows the same intercept+effects
    shape as a non-mixture stochastic measure. Weights are auto-normalized.
    """
    components = col_meta["param_model"]["components"]
    weights = np.array([c["weight"] for c in components], dtype=float)
    weights = weights / weights.sum()

    n_rows = next(iter(rows.values())).shape[0] if rows else 0
    if n_rows == 0:
        return np.array([], dtype=np.float64)

    # Per-row component assignment
    component_idx = rng.choice(len(components), size=n_rows, p=weights)

    out = np.empty(n_rows, dtype=np.float64)
    for k, comp in enumerate(components):
        mask = component_idx == k
        if not mask.any():
            continue
        sub_meta = {"family": comp["family"], "param_model": comp["param_model"]}
        sub_params = _compute_per_row_params(
            f"{col_name}[c{k}]", sub_meta, rows, n_rows, overrides,
        )
        sub_params_masked = {p: arr[mask] for p, arr in sub_params.items()}
        out[mask] = _sample_family(comp["family"], sub_params_masked, int(mask.sum()), rng)
    return out
```

**Integration points:**
- `_sample_stochastic` ([engine/measures.py:329](pipeline/phase_2/engine/measures.py#L329))
  dispatches to `_sample_mixture` when `family == "mixture"`.
- `_compute_per_row_params` ([engine/measures.py:406](pipeline/phase_2/engine/measures.py#L406))
  reused per-component (already handles intercept+effects).
- `sdk/columns.py::validate_param_model` must learn the mixture schema
  (validate `components` list, per-component `family`, `weight`,
  `param_model`).
- `sdk/relationships.py` — none (mixture is declaration-time, not
  pattern-time).

**New types:** `MixtureComponent(TypedDict)` in `types.py`:

```python
class MixtureComponent(TypedDict):
    family: str
    weight: float
    param_model: dict[str, Any]
```

### Test criteria
- 2-component gaussian mixture with weights `[0.6, 0.4]` and disparate
  means → empirical mean ≈ weighted mean of component means within 5%.
- 3-component mixture with constant per-component params → samples pass a
  scipy mixture-CDF KS test.
- Mixture with predictor-varying components → per predictor cell, samples
  match expected mixture distribution.
- Weight normalization: `[0.3, 0.2]` is auto-normalized to `[0.6, 0.4]`.
- Validator-side: `_validate_param_model("mixture", {})` raises
  `InvalidParameterError` with a clear message about `components` shape.

### Estimated scope
**Medium (80–200 LOC).** Sampler ~50 LOC + validator schema ~30 LOC +
type defs ~10 LOC + tests ~80 LOC ≈ 170 LOC. Comparable analog: the
existing `_sample_stochastic` + `_compute_per_row_params` is ~150 LOC.

**Autofix caveat (effective scope inflator).** The existing `ks_*`
auto-fix strategy (`widen_variance`) indexes a single `sigma` field per
measure — it does not naturally apply to mixture distributions, where
each component has its own `sigma`. Co-implementing IS-1 + DS-3 also
requires deciding whether to (a) opt mixture out of `widen_variance`
(simplest), (b) widen the dominant-weight component, or (c) widen all
components proportionally. Whichever is chosen, the autofix-side change
is ~20-40 additional LOC plus tests, pushing the IS-1 + DS-3 + autofix
combined surface above the ~300 LOC pair estimate.

---

## [IS-2] Dominance shift validation

### Code span
```python
# pipeline/phase_2/validation/pattern_checks.py:189-213
def check_dominance_shift(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Dominance shift validation (stub).

    [P1-3]

    TODO [M5-NC-4 / P1-3]: Define as rank change of entity across temporal
    split. Expected params: entity_filter, col, split_point.

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "col" key.
        meta: Schema metadata.

    Returns:
        Check named "dominance_{col}" with passed=True (not yet implemented).
    """
    return Check(
        name=f"dominance_{pattern['col']}",
        passed=True,
        detail="dominance_shift validation not yet implemented",
    )
```

### Spec references
- §2.1.2 (L127): `"dominance_shift"` listed in `PATTERN_TYPES` for
  `inject_pattern()`.
- §2.5 (L305): LLM prompt's allowed-pattern-types list includes
  `"dominance_shift"`.
- §2.9 L3 (L672–674): Pseudocode sketch shows
  `elif p["type"] == "dominance_shift": self._verify_dominance_change(df, p, meta)`
  but the verifier body is not specified.

### Existing tests
- (none found)

### Dependent stubs
- (none directly; but cannot be exercised end-to-end without DS-2 — pattern
  injection of `dominance_shift` raises `NotImplementedError`.)

### Role in pipeline
Sits in §2.9 L3 pattern validation, invoked by the validator after engine
generation and pattern injection. Upstream: the generated DataFrame plus a
pattern dict with `type=="dominance_shift"`. Downstream: returns a `Check`
consumed by `ValidationReport`; failures would route to `AUTO_FIX` but no
`dominance_*` strategy exists. Currently the function returns
`passed=True` unconditionally, so dominance_shift patterns silently "pass"
validation regardless of what the data shows.

### Gap analysis
- **Spec defines:** §2.1.2 L127 lists `"dominance_shift"` in PATTERN_TYPES;
  §2.5 L305 lists it in the prompt; §2.9 L3 (L672–674) sketches the
  call-surface as `elif p["type"] == "dominance_shift":
  self._verify_dominance_change(df, p, meta)`.
- **Spec is silent on:** the algorithm body of `_verify_dominance_change` —
  no operational definition (rank-change of an entity across a temporal
  split? share crossover? top-k change?), no params contract beyond what
  the source TODO speculates (`entity_filter, col, split_point`), no pass
  threshold, no example in §2.6 patterns metadata.
- **Implementation gap:** stub returns hard-coded `passed=True`. Spec
  defines the call surface but not the algorithm. A real implementation
  must (a) define the params contract, (b) split data by `split_point`,
  (c) compute a dominance/rank metric, (d) define a pass threshold. None
  of (a)–(d) is in the spec.

### Dependency chain
- **Blocks:** nothing directly (it's a leaf validation stub).
- **Blocked by:** spec extension defining what "dominance shift" means
  quantitatively + params contract; **DS-2** (pattern injection for
  dominance_shift) for end-to-end exercise — without injection there is no
  signal to verify.
- **Co-dependent with:** DS-2 — injector and validator must share the same
  operational definition.

### Blocking questions
- **Spec:** operational definition of "dominance shift". Three plausible
  candidates: (a) rank reversal of a target entity across a temporal
  split (target moves from #1 to #N or vice versa); (b) mean/sum
  crossover (entity A > B before split, A < B after); (c) market-share
  crossover. The source TODO ("rank change of entity across temporal
  split") points to (a).
- **Spec:** pass threshold — minimum rank change required (default 1?
  configurable via `params.rank_change`?).

### Proposed solution
Pick interpretation (a). Mirror `check_trend_break` (also a temporal
before/after pattern). Reuse `_find_temporal_column` already in
[validation/pattern_checks.py:94](pipeline/phase_2/validation/pattern_checks.py#L94)
and the entity-col fallback from
[`check_ranking_reversal`](pipeline/phase_2/validation/pattern_checks.py#L268-L316).

```python
# pipeline/phase_2/validation/pattern_checks.py — replace stub at L189-213.

def check_dominance_shift(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Dominance shift — target entity's rank changes across split.

    Algorithm (interpretation (a)):
      1. Resolve entity_col (param or first dim-group root).
      2. Resolve temporal_col from meta.
      3. Split data at params["split_point"].
      4. Per side, group by entity_col, compute mean of pattern["col"].
      5. Pass if |rank_after - rank_before| of params["entity_filter"]
         >= params.get("rank_change", 1).
    """
    col = pattern["col"]
    params = pattern.get("params", {})
    target_entity = params.get("entity_filter")
    split_point = params.get("split_point")
    rank_threshold = params.get("rank_change", 1)
    name = f"dominance_{col}"

    if not target_entity or not split_point:
        return Check(name=name, passed=False,
                     detail="Missing entity_filter or split_point in params.")

    entity_col = params.get("entity_col") or _resolve_first_dim_root(meta)
    temporal_col = _find_temporal_column(meta)
    if entity_col is None or temporal_col is None:
        return Check(name=name, passed=False,
                     detail=f"Missing entity_col={entity_col!r} or temporal_col={temporal_col!r}.")

    sp = pd.to_datetime(split_point)
    tval = pd.to_datetime(df[temporal_col], errors="coerce")
    before_means = df[tval < sp].groupby(entity_col)[col].mean()
    after_means = df[tval >= sp].groupby(entity_col)[col].mean()

    if target_entity not in before_means.index or target_entity not in after_means.index:
        return Check(name=name, passed=False,
                     detail=f"Target entity {target_entity!r} missing on one side of split.")

    rank_before = before_means.rank(ascending=False)[target_entity]
    rank_after = after_means.rank(ascending=False)[target_entity]
    delta = abs(rank_after - rank_before)
    passed = bool(delta >= rank_threshold)
    return Check(
        name=name, passed=passed,
        detail=f"rank_before={int(rank_before)}, rank_after={int(rank_after)}, delta={int(delta)} (threshold={rank_threshold})",
    )


def _resolve_first_dim_root(meta: dict[str, Any]) -> Optional[str]:
    """Factor of the entity-col fallback in check_ranking_reversal."""
    dim_groups = meta.get("dimension_groups", {})
    if not dim_groups:
        return None
    first = dim_groups[next(iter(dim_groups))]
    hierarchy = first.get("hierarchy", [])
    return hierarchy[0] if hierarchy else None
```

**Integration points:**
- Validator dispatch in
  [validation/validator.py](pipeline/phase_2/validation/validator.py)
  already routes pattern type `"dominance_shift"` to this function — only
  the body changes.
- Reuses `_find_temporal_column`; adds the small `_resolve_first_dim_root`
  helper used here and in IS-3/IS-4.

**New types:** none.

### Test criteria
- Inject synthetic before/after means where target rank shifts 1→3 →
  passed=True.
- Stable rank across split → passed=False.
- Missing `entity_filter` / `split_point` → passed=False with clear
  detail.
- Target entity absent on one side → passed=False.
- Missing temporal column → passed=False.

### Estimated scope
**Small (20–80 LOC).** Function body ≈ 45 LOC + helper ≈ 8 LOC + tests
≈ 60 LOC ≈ 110 LOC total (just over the small bucket but well under
medium). Analog: `check_trend_break` is ~80 LOC of body.

---

## [IS-3] Convergence validation

### Code span
```python
# pipeline/phase_2/validation/pattern_checks.py:216-239
def check_convergence(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Convergence validation (stub).

    TODO [M5-NC-5 / P1-4]: Convergence validation not yet specified.

    [P1-4]

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "col" key.
        meta: Schema metadata.

    Returns:
        Check named "convergence_{col}" with passed=True (not yet implemented).
    """
    return Check(
        name=f"convergence_{pattern['col']}",
        passed=True,
        detail="convergence validation not yet implemented",
    )
```

### Spec references
- §2.1.2 (L127): `"convergence"` listed in `PATTERN_TYPES`.
- §2.5 (L305): LLM prompt's allowed-pattern-types list includes
  `"convergence"`.
- §2.9 L3 (L644–677): No pseudocode or algorithm — convergence validation is
  absent from the L3 pattern-validation pseudo-code.

### Existing tests
- (none found)

### Dependent stubs
- (none directly; same DS-2 chain as IS-2.)

### Role in pipeline
Same architectural position as IS-2 — §2.9 L3 pattern validation invoked
post-engine, post-pattern-injection. Upstream: pattern dict with
`type=="convergence"`. Downstream: a `Check` for `ValidationReport`;
`AUTO_FIX` has no `convergence_*` entry. Currently returns `passed=True`
unconditionally.

### Gap analysis
- **Spec defines:** §2.1.2 L127 lists `"convergence"` in PATTERN_TYPES;
  §2.5 L305 lists it in the prompt.
- **Spec is silent on:** **everything else.** Unlike `dominance_shift`,
  §2.9 L3 has *no* pseudocode branch for convergence — it does not even
  appear in the verification sketch. There is no params contract, no
  algorithm, no validation criterion, no example in §2.6. Convergence has
  the thinnest spec coverage of any stub in the inventory.
- **Implementation gap:** stub returns `passed=True`. Both injection
  (DS-2) and validation (IS-3) need a formal definition of "convergence"
  — e.g., variance reduction over time within a group, mean alignment
  between groups, rank rapprochement. The spec offers no anchor.

### Dependency chain
- **Blocks:** nothing directly.
- **Blocked by:** spec extension formally defining convergence (more
  critical here than for IS-2 because the spec offers zero algorithmic
  guidance); **DS-2** for end-to-end exercise.
- **Co-dependent with:** DS-2 — injector and validator must share the same
  operational definition.

### Blocking questions
- **Spec:** operational definition. Candidates: (a) variance of
  `pattern["col"]` decreases over time globally; (b) variance of group
  means decreases over time (groups becoming homogeneous);
  (c) a specific pair of entities' means approach each other monotonically.
  Chart-storytelling intent (groups becoming similar) points to (b).
- **Spec:** comparison reference — early-half vs late-half? Sliding
  window? Default to a single midpoint split.
- **Spec:** threshold for "convergence happened". Reasonable default:
  `late_var <= early_var × (1 - 0.3)` (30% reduction).

### Proposed solution
Pick interpretation (b). Mirror `check_dominance_shift` for split-based
temporal logic. Reuse `_find_temporal_column` and `_resolve_first_dim_root`.

```python
# pipeline/phase_2/validation/pattern_checks.py — replace stub at L216-239.

def check_convergence(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Convergence — variance of group means decreases over time.

    Algorithm (interpretation (b)):
      1. Resolve entity_col and temporal_col.
      2. Split at params["split_point"] or temporal median.
      3. Per side, compute per-entity mean of pattern["col"].
      4. Compare variance-of-means: reduction = (early_var - late_var) / early_var.
      5. Pass if reduction >= params.get("reduction", 0.3).
    """
    col = pattern["col"]
    params = pattern.get("params", {})
    threshold = params.get("reduction", 0.3)
    name = f"convergence_{col}"

    entity_col = params.get("entity_col") or _resolve_first_dim_root(meta)
    temporal_col = _find_temporal_column(meta)
    if entity_col is None or temporal_col is None:
        return Check(name=name, passed=False,
                     detail=f"Missing entity_col={entity_col!r} or temporal_col={temporal_col!r}.")

    tval = pd.to_datetime(df[temporal_col], errors="coerce")
    sp = pd.to_datetime(params["split_point"]) if params.get("split_point") else tval.quantile(0.5)
    early_means = df[tval < sp].groupby(entity_col)[col].mean()
    late_means = df[tval >= sp].groupby(entity_col)[col].mean()

    if len(early_means) < 2 or len(late_means) < 2:
        return Check(name=name, passed=False,
                     detail=f"Need >=2 entities per side, got early={len(early_means)}, late={len(late_means)}.")

    early_var = float(early_means.var())
    late_var = float(late_means.var())
    if early_var == 0:
        return Check(name=name, passed=False, detail="Early-period inter-group variance is 0.")

    reduction = (early_var - late_var) / early_var
    passed = bool(reduction >= threshold)
    return Check(
        name=name, passed=passed,
        detail=f"early_var={early_var:.4f}, late_var={late_var:.4f}, reduction={reduction:.3f} (threshold={threshold})",
    )
```

**Integration points:**
- Same dispatch wiring as IS-2; only body changes.
- Reuses `_find_temporal_column` and `_resolve_first_dim_root`.

**New types:** none.

### Test criteria
- Late-period group means uniform, early-period spread → passed=True.
- Stable group spread across periods → passed=False.
- Single entity (only one group) → graceful fail with detail.
- Missing temporal column → graceful fail.
- Constant column (early_var == 0) → graceful fail.

### Estimated scope
**Small (20–80 LOC).** Body ≈ 40 LOC + tests ≈ 50 LOC ≈ 90 LOC. Analog:
`check_ranking_reversal` body is ~80 LOC.

---

## [IS-4] Seasonal anomaly validation

### Code span
```python
# pipeline/phase_2/validation/pattern_checks.py:242-265
def check_seasonal_anomaly(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Seasonal anomaly validation (stub).

    TODO [M5-NC-5 / P1-4]: Seasonal anomaly validation not yet specified.

    [P1-4]

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "col" key.
        meta: Schema metadata.

    Returns:
        Check named "seasonal_{col}" with passed=True (not yet implemented).
    """
    return Check(
        name=f"seasonal_{pattern['col']}",
        passed=True,
        detail="seasonal_anomaly validation not yet implemented",
    )
```

### Spec references
- §2.1.2 (L127): `"seasonal_anomaly"` listed in `PATTERN_TYPES`.
- §2.5 (L305): LLM prompt's allowed-pattern-types list includes
  `"seasonal_anomaly"`.
- §2.9 L3 (L644–677): No pseudocode or algorithm — absent from L3
  pattern-validation pseudo-code.

### Existing tests
- (none found)

### Dependent stubs
- (none directly; same DS-2 chain as IS-2.)

### Role in pipeline
Same as IS-2/IS-3 — §2.9 L3 pattern validation post-engine and
post-pattern-injection. Particular note: the check only makes sense in
scenarios where `add_temporal()` was called, so it has an implicit
dependency on a temporal column being present in the schema metadata.

### Gap analysis
- **Spec defines:** §2.1.2 L127 lists `"seasonal_anomaly"` in
  PATTERN_TYPES; §2.5 L305 lists it in the prompt.
- **Spec is silent on:** §2.9 L3 has no pseudocode for seasonal_anomaly.
  No params contract (period? anomaly window? magnitude threshold?), no
  detection method (residuals from STL? z-score on detrended series?), no
  rule for resolving the temporal column when the scenario has more than
  one. Spec also doesn't require a temporal column to be present when
  seasonal_anomaly is declared — declaration would succeed in a
  temporal-free scenario but the check would be meaningless.
- **Implementation gap:** stub returns `passed=True`. Implementation needs
  (a) period inference or declaration, (b) anomaly window contract,
  (c) detection metric, (d) pass threshold, (e) a precondition check that
  a temporal column exists. (a)–(d) require spec input.

### Dependency chain
- **Blocks:** nothing directly.
- **Blocked by:** spec extension defining seasonal_anomaly + params +
  temporal-dependency contract; **DS-2** for the injection side; presence
  of `add_temporal` in the scenario for the check to be exercisable.
- **Co-dependent with:** DS-2 — injector and validator must share the same
  operational definition.

### Blocking questions
- **Spec:** operational definition of "seasonal anomaly". Candidates:
  (a) values inside an explicit `anomaly_window` deviate from the
  out-of-window baseline; (b) STL decomposition with residual outliers;
  (c) period-aware z-score on detrended series. (a) is simplest and
  matches the narrative-driven framing of `inject_pattern`.
- **Spec:** params contract — `anomaly_window=[start, end]` required, or
  inferable (e.g., last 10% of temporal range)?
- **Spec:** pass threshold — reasonable default is z ≥ 1.5.

### Proposed solution
Pick interpretation (a). Mirror `check_outlier_entity` for the
window-vs-baseline z-score logic; reuse `_find_temporal_column`.

```python
# pipeline/phase_2/validation/pattern_checks.py — replace stub at L242-265.

def check_seasonal_anomaly(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Seasonal anomaly — anomaly_window mean deviates from baseline.

    Algorithm (interpretation (a)):
      1. Resolve temporal_col.
      2. Get anomaly_window=[start, end] from params, or default to
         last 10% of temporal range.
      3. Compute baseline mean+std from out-of-window rows.
      4. z = |window_mean - baseline_mean| / baseline_std.
      5. Pass if z >= params.get("z_threshold", 1.5).
    """
    col = pattern["col"]
    params = pattern.get("params", {})
    z_threshold = params.get("z_threshold", 1.5)
    name = f"seasonal_{col}"

    temporal_col = _find_temporal_column(meta)
    if temporal_col is None:
        return Check(name=name, passed=False, detail="No temporal column.")

    tval = pd.to_datetime(df[temporal_col], errors="coerce")
    window = params.get("anomaly_window")
    if window:
        win_start, win_end = pd.to_datetime(window[0]), pd.to_datetime(window[1])
    else:
        tmin, tmax = tval.min(), tval.max()
        win_start, win_end = tmin + (tmax - tmin) * 0.9, tmax

    in_window = (tval >= win_start) & (tval <= win_end)
    win_vals = df.loc[in_window, col]
    base_vals = df.loc[~in_window, col]

    if len(win_vals) == 0 or len(base_vals) < 2:
        return Check(name=name, passed=False,
                     detail=f"Insufficient rows: window={len(win_vals)}, baseline={len(base_vals)}.")

    base_mean, base_std = float(base_vals.mean()), float(base_vals.std())
    if base_std == 0:
        return Check(name=name, passed=False, detail="Baseline std is 0.")

    win_mean = float(win_vals.mean())
    z = abs(win_mean - base_mean) / base_std
    passed = bool(z >= z_threshold)
    return Check(
        name=name, passed=passed,
        detail=f"win_mean={win_mean:.4f}, base_mean={base_mean:.4f}, z={z:.3f} (threshold={z_threshold})",
    )
```

**Integration points:**
- Same dispatch wiring as IS-2/IS-3; only body changes.
- Reuses `_find_temporal_column`.

**New types:** none.

### Test criteria
- Window with elevated mean → passed=True.
- Stable window mean ≈ baseline → passed=False.
- Empty window → graceful fail.
- Missing temporal column → graceful fail.
- Constant column → graceful fail.

### Estimated scope
**Small (20–80 LOC).** Body ≈ 45 LOC + tests ≈ 50 LOC ≈ 95 LOC. Analog:
`check_outlier_entity` body is ~70 LOC.

---

## [IS-5] `scale` kwarg on `add_measure`

### Code span (sdk — kwarg removed)
```python
# pipeline/phase_2/sdk/columns.py:214-250
# TODO [M?-NC-scale]: restore `scale` kwarg when a scaling implementation lands.
# Previously `scale` was accepted but silently no-op, which misled LLMs into
# tuning a knob that did nothing. Removed so Python raises a clear TypeError
# if callers still pass it.
def add_measure(
    columns: OrderedDict[str, dict[str, Any]],
    name: str,
    family: str,
    param_model: dict[str, Any],
) -> None:
    """Declare a stochastic measure column.

    [Subtask 1.4.1–1.4.3]

    Args:
        columns: Column registry (mutated in place).
        name: Measure column name.
        family: Distribution family string.
        param_model: Distribution parameters dict.
    """
    _val.validate_column_name(name, columns)
    _val.validate_family(family)
    _val.validate_param_model(name, family, param_model, columns)

    col_meta: dict[str, Any] = {
        "type": "measure",
        "measure_type": "stochastic",
        "family": family,
        "param_model": dict(param_model),
    }

    columns[name] = col_meta

    logger.debug(
        "add_measure: stochastic '%s' (family='%s') registered.",
        name, family,
    )
```

### Code span (orchestration — prompt no longer documents `scale`)
```python
# pipeline/phase_2/orchestration/prompt.py:53-54
# TODO [M?-NC-scale]: re-add `scale=None` kwarg when sdk/columns.py::add_measure implements it.
"  sim.add_measure(name, family, param_model)\n"
# (Lines L55-60 below describe param_model schema per family — unrelated to scale.)
```

### Spec references
- §2.1.1 (L51): Lists `add_measure(name, family, param_model, scale=None)`
  in the signature line. The surrounding prose ("Stochastic root measure.
  Sampled from a named distribution. Parameters may vary by categorical
  context …") describes the method but **does not explain what `scale=`
  means**. There is no log/linear/post-transform interpretation anywhere
  in §2.1.1 or §2.3 — the kwarg is signature-only, semantics-empty.
- §2.5 (L287): Prompt template's AVAILABLE SDK METHODS section shows
  `sim.add_measure(name, family, param_model, scale=None)` — same
  signature line, no behavioral description. Live `prompt.py` (L53-54)
  no longer emits the `scale` kwarg.
- **Spec/prompt/SDK status:** spec retains a vestigial signature line
  with no semantics; live prompt and live SDK have both removed it. There
  is no behavioral *claim* in the spec that the SDK contradicts — only a
  ghost kwarg with empty semantics.

### Existing tests
- `tests/modular/test_sdk_columns.py::TestAddMeasure::test_add_measure_rejects_scale_kwarg` —
  Verifies that passing `scale=` raises `TypeError` (intentional: the absent
  kwarg surfaces a clean error to the LLM retry loop).
- `tests/modular/test_sdk_columns.py::TestAddMeasure::test_add_stochastic_measure` —
  Confirms `scale` is not stored in column metadata.

### Dependent stubs
- (none)

### Role in pipeline
Was meant to be a §2.1.1 declaration-step parameter on stochastic
measures, but the spec only lists the kwarg in the signature without ever
documenting its semantics. Currently NOT in the live SDK: `add_measure`
rejects the kwarg with `TypeError`, and the live
[orchestration/prompt.py](pipeline/phase_2/orchestration/prompt.py) at
L53-54 omits `scale=None` from the LLM-facing API documentation. Spec
§2.5 L287 still shows the kwarg in the signature line. Net effect:
**spec, prompt, and SDK have all converged on omitting any behavior for
`scale`** — but the spec retains a vestigial signature line as the only
remaining mention of the parameter. This is closer to a "ghost kwarg"
than a competing claim across the three documents.

### Gap analysis
- **Spec defines:** §2.1.1 L51 lists `add_measure(name, family,
  param_model, scale=None)`; §2.5 L287 documents the same in the prompt
  template. Spec presents `scale` as a generic optional hint without
  operational semantics or examples — there is no use of `scale != None`
  anywhere in the spec.
- **Spec is silent on:** what `scale` actually does — whether it's a
  per-family enum hint (e.g., `"log_scale"` for lognormal `mu`
  interpretation), a post-sampling transform, or a notation aid. The
  pre-removal implementation accepted the kwarg but never read it, so the
  feature has never had behavior in any version.
- **Implementation gap:** kwarg removed and surfaced as a clear
  `TypeError` so accidental LLM usage fails fast (good defensive choice).
  To restore: (a) decide what `scale` means, (b) wire it through
  `_compute_per_row_params` to interpret `mu`/`sigma` accordingly,
  (c) update §2.1.1 with examples, (d) re-add to `prompt.py:53-54`. Until
  (a) is settled, the absence-with-TypeError is correct behavior.

### Dependency chain
- **Blocks:** nothing else in the inventory.
- **Blocked by:** spec **addition** (not extension) defining what
  `scale=` should mean. The spec contains no behavioral claim today —
  this is a request to add semantics, not to clarify existing ones.
- **Co-dependent with:** the three vestigial mentions — spec §2.1.1 L51
  signature, spec §2.5 L287 signature, and (if restored) live
  `prompt.py:53-54` — which must be aligned together.

### Blocking questions
- **Spec (proposal, not interpretation):** since the spec gives no
  behavioral content for `scale=`, *any* meaning would be a new
  proposal, not a reading of existing text. Two candidate proposals:
  (a) per-family enum hint (`scale="log"` → mu is log-scale;
  `scale="linear"` → mu is on natural scale); (b) post-sampling transform
  applied to sampled values. Neither is supported by spec prose; both are
  fresh design.
- **Architectural:** does restoring `scale` actually pull weight, given
  that lognormal already encodes log-scale via its family choice and
  gaussian/gamma/beta have their own natural scales? Risk of restoring a
  parameter that adds confusion without behavior.

### Proposed solution
**Recommended: do not restore the kwarg.** Since the spec never said
what `scale` did, removing it from the spec costs nothing — there is no
behavioral claim to lose. Strip `scale=None` from §2.1.1 L51 and
§2.5 L287, leaving spec, prompt, and SDK consistently omitting the
kwarg. The current "absent + TypeError" is the safest state and aligns
with the M?-NC-scale TODO that says "restore when a scaling
implementation lands" (i.e., implementation should drive the spec, not
the other way around).

If a restoration is forced, the minimal safe path is interpretation (a)
as a per-family hint:

```python
# sdk/columns.py::add_measure — minimal restoration sketch
def add_measure(
    columns: OrderedDict[str, dict[str, Any]],
    name: str,
    family: str,
    param_model: dict[str, Any],
    scale: Optional[str] = None,  # one of "linear", "log", or None
) -> None:
    if scale is not None and scale not in ("linear", "log"):
        raise ValueError(f"scale must be 'linear', 'log', or None; got {scale!r}.")
    # Most families ignore scale (already encode it); only lognormal /
    # exponential interpret it as a hint about whether mu is on the log
    # scale or natural scale.
    col_meta["scale"] = scale
```

But behavior wiring (consuming `scale` in `_compute_per_row_params` and
in `_expected_cdf` for L2) is non-trivial — and the spec gives no
example, so each family's interpretation is undocumented.

**Integration points (if restored):**
- `sdk/columns.py::add_measure` — re-add kwarg + validation.
- `engine/measures.py::_compute_per_row_params` — interpret hint per
  family (most ignore it).
- `validation/statistical.py::_expected_cdf` — match the sampling
  interpretation so KS test stays consistent.
- `orchestration/prompt.py:53-54` — re-add `scale=None` documentation.

**New types:** none.

### Test criteria
- **If kept absent (recommended):** existing
  `test_add_measure_rejects_scale_kwarg` continues to verify the
  TypeError; add a docs/spec audit test asserting that `prompt.py` and
  spec (§2.5) both document the same arg list.
- **If restored:** round-trip test that `scale="log"` + lognormal `mu`
  matches a non-scaled gaussian over `log(samples)`; rejection test for
  `scale="invalid"`.

### Estimated scope
**Trivial (<20 LOC) for the recommended path** — strip `scale=None` from
spec L51 and §2.5 L287 (docs-only). **Small (20–80 LOC) for restoration
as enum hint** — kwarg + validation + per-family wiring + tests.

---

## [IS-6] M3 multi-error + token budget

### Code span (sdk/simulator.py — capability absence, not raise-stub)
```python
# pipeline/phase_2/sdk/simulator.py:32-36
# TODO [M3-NC-3]: The sandbox currently catches one error at a time.
# Multiple simultaneous SDK validation errors (e.g. two bad effects +
# a cycle) are surfaced one per retry attempt. A future enhancement
# could collect all validation errors in a single pass and relay them
# as a batch to reduce retry iterations.
```

### Code span (orchestration/sandbox.py — referenced location, retry attempt)
```python
# pipeline/phase_2/orchestration/sandbox.py:~657
# (Sandbox attempt loop — single-error capture, no token-budget tracker.
#  No NotImplementedError; the "stub" is the absence of a multi-error
#  collector and a token-budget guard around the retry loop.)
```
(Note: this is documented as a *capability gap*, not a `NotImplementedError`
block. The TODO above is the only on-source marker.)

### Spec references
- §2.7 (L485–503): Execution-Error Feedback Loop describes step 4
  ("FAILURE → SDK raises typed exception") and step 5 ("Code + traceback fed
  back to LLM"). Currently surfaces errors one per retry; multi-error batching
  is mentioned as the M3 enhancement.
- (No token-budget mechanism is documented in the spec — this is an
  implementation-side guardrail rather than a spec feature.)

### Existing tests
- `tests/test_retry_feedback.py` — exercises single-error retry feedback;
  no test verifies multi-error collection (feature not yet present).
- (no token-budget tests found)

### Dependent stubs
- (none)

### Role in pipeline
Sits in Loop A (§2.7), specifically in
[orchestration/sandbox.py](pipeline/phase_2/orchestration/sandbox.py)
inside `run_with_retries` around L689 (the retry loop). Upstream: a
sandbox failure (typed exception from SDK or runtime). Downstream: the
exception/traceback is fed back to the LLM and a retry follows, capped at
`max_retries=3`. Currently surfaces ONE error per attempt; if the LLM
script has 3 simultaneous errors (cycle + bad effect + non-root dep) it
takes 3 attempts to find them all. There is also no token budget — a
script with verbose tracebacks could blow up retry context.

### Gap analysis
- **Spec defines:** §2.7 L485-503 documents the feedback loop with
  examples of typed exceptions; step 4 says "SDK raises typed exception"
  (singular); step 6 says "Retry (max_retries=3). If all fail → log and
  skip."
- **Spec is silent on:** error batching is not in §2.7 — multi-error
  collection is an implementation-side optimization. Token budgeting is
  entirely absent from the spec — also operational, not a spec feature.
- **Implementation gap:** there's no `NotImplementedError` marker — this
  is a **capability absence**, not a stub raising. Two distinct
  sub-features:
  (1) **Multi-error collection** — requires SDK validators to keep going
  past the first error (catch-all + accumulate), then surface a list. A
  substantial refactor across `sdk/columns.py`, `sdk/relationships.py`,
  and internal validation helpers, since each currently raises on first
  failure.
  (2) **Token budget** — needs a tracker around the retry loop counting
  prompt + completion tokens per attempt and a guard that skips early
  when the budget is exceeded; intersects with the `LLMClient` interface
  to obtain token counts.

### Dependency chain
- **Blocks:** nothing in the inventory (this is purely an optimization).
- **Blocked by:** architectural decision (does multi-error mode confuse
  the LLM, or help it?); `LLMClient` API exposing token counts (currently
  varies per provider).
- **Co-dependent with:** nothing in the inventory; the two sub-features
  (multi-error and token budget) are independent and could ship
  separately.

### Blocking questions
- **Architectural:** does multi-error feedback help or confuse the LLM?
  Empirical question — small/older models often degrade with multi-error
  prompts; capable models tend to benefit. Needs an A/B test before
  committing the feature as default-on.
- **Architectural:** is the token budget per-attempt or per-scenario?
  Per-scenario is more useful but requires the retry loop to thread a
  cumulative tracker.
- **Operational:** how does the budget read token counts from
  `LLMClient`? The current `LLMClient` interface varies per provider —
  may need a thin `TokenUsage` adapter.

### Proposed solution
Two independent sub-features; ship separately. Recommend shipping (2)
token budget first — smaller blast radius, no SDK refactor needed.

**(1) Multi-error collection.** Add an opt-in `ValidationContext` that
SDK validators call instead of bare `raise`:

```python
# pipeline/phase_2/sdk/validation.py — new helper

class ValidationContext:
    """Context for collecting validation errors instead of raising.

    Used by sdk validators when sandbox.run_with_retries opts into
    multi-error mode. Falls back to raise-on-first when not opted in,
    preserving current behavior.
    """
    def __init__(self, accumulate: bool = False):
        self.accumulate = accumulate
        self.errors: list[Exception] = []

    def report(self, exc: Exception) -> None:
        if self.accumulate:
            self.errors.append(exc)
        else:
            raise exc

    def raise_if_any(self) -> None:
        if self.errors:
            raise MultiValidationError(self.errors)


# orchestration/sandbox.py::run_with_retries — opt-in flag
def run_with_retries(
    initial_code: str,
    ...,
    multi_error: bool = False,
) -> RetryLoopResult:
    for attempt in range(1, max_retries + 1):
        ctx = ValidationContext(accumulate=multi_error)
        result = execute_in_sandbox(current_code, ..., validation_ctx=ctx)
        if result.success:
            return ...
        # Surface ALL collected errors at once
        all_errors = ctx.errors or [result.exception]
        feedback = format_multi_error_feedback(all_errors)
        current_code = llm_generate_fn(system_prompt, feedback)
```

**(2) Token budget.** Plumb a counter into the retry loop:

```python
# orchestration/sandbox.py::run_with_retries — token-budget guard

def run_with_retries(
    initial_code: str,
    llm_generate_fn: Callable[[str, str], LLMResponse],
    ...,
    token_budget: int | None = None,
) -> RetryLoopResult:
    tokens_used = 0
    for attempt in range(1, max_retries + 1):
        ...
        if isinstance(response, LLMResponse) and response.token_usage:
            tokens_used += response.token_usage.total_tokens
        if token_budget and tokens_used >= token_budget:
            return RetryLoopResult(
                success=False,
                history=history,
                skipped_reason=f"token_budget_exceeded ({tokens_used}/{token_budget})",
            )
```

**Integration points:**
- `sdk/columns.py`, `sdk/relationships.py`, `sdk/dag.py`, `sdk/validation.py`
  — convert each `raise` site to `ctx.report(exc)` (multi-error only;
  ~10 raise sites).
- `orchestration/sandbox.py::run_with_retries` (~L689) — add `multi_error`
  and `token_budget` flags.
- `orchestration/llm_client.py::LLMClient.generate_code` — return a
  structured `LLMResponse` carrying `token_usage` (currently returns a
  raw string).
- `exceptions.py` — add `MultiValidationError(list[Exception])`.

**New types:**
- `ValidationContext` in `sdk/validation.py`.
- `MultiValidationError` in `exceptions.py`.
- `LLMResponse(NamedTuple)` and `TokenUsage(NamedTuple)` in
  `orchestration/llm_client.py`.

### Test criteria
- **Multi-error:** script with 3 simultaneous SDK errors → one retry
  attempt with 3 errors in feedback (vs current 3 attempts).
- **Multi-error:** script with 1 error → identical behavior to current
  (backward compat).
- **Token budget:** retry loop terminates early when budget hit; returns
  `SkipResult` with a `token_budget_exceeded` reason.
- **Token budget:** `None` default → no behavior change.
- **Provider compat:** mock `LLMClient` that returns no token counts
  → budget feature degrades gracefully (counts as 0).

### Estimated scope
**Large (200+ LOC).** Multi-error alone touches ~10 raise sites in
`sdk/*.py` (~10 LOC × 10 = 100 LOC), plus `ValidationContext` + new
exception (~30 LOC), plus sandbox plumbing (~30 LOC), plus tests (~80
LOC) ≈ 240 LOC. Token budget adds ~60 LOC + LLMClient response refactor
+ tests ≈ 100 LOC. Combined ≈ 340 LOC. The two halves can ship as
separate PRs.

---

# Dependent stubs (4)

## [DS-1] Censoring injection

### Code span
```python
# pipeline/phase_2/engine/realism.py:57-63
censoring = realism_config.get("censoring")
if censoring is not None:
    # TODO [M1-NC-7]: Censoring injection deferred.
    raise NotImplementedError(
        "Censoring injection not yet implemented. "
        "See stage3 item M1-NC-7."
    )
```

### Spec references
- §2.1.2 (L129): `set_realism(missing_rate, dirty_rate, censoring)` declares
  censoring as an optional realism-config key.
- §2.8 (L532–534): Deterministic engine execution plan shows δ (realism) as
  the final optional pipeline stage; censoring is one of the three components
  alongside missing values and dirty values.

### Existing tests
- (none found)

### Dependent stubs
- (none — DS-1 is itself a leaf dependent stub; parent is the spec definition.)

### Role in pipeline
Sits in §2.8 step δ (realism, optional) — runs *after* pattern injection,
on the full DataFrame. Upstream: the `realism_config` dict from
`set_realism(censoring=...)`. Downstream: writes to the Master DataFrame
returned to Phase 3. Triggered only if `censoring is not None`; otherwise
the realism stage proceeds with missing/dirty injection only.

**Prompt-side gating (important):** while
[sdk/relationships.py::set_realism](pipeline/phase_2/sdk/relationships.py#L281)
still accepts `censoring=None`, the live LLM prompt at
[orchestration/prompt.py:70-71](pipeline/phase_2/orchestration/prompt.py#L70-L71)
no longer advertises the kwarg — it now reads
`sim.set_realism(missing_rate, dirty_rate)` with a TODO comment marking
`censoring=` as deferred. This is the same "double-gated out" pattern as
the 4 deferred patterns in DS-2: SDK accepts it (so old scripts don't
crash on import), but the LLM never sees it in normal flow. In effect
the engine's `NotImplementedError` branch is unreachable from any
prompt-driven generation today.

### Gap analysis
- **Spec defines:** §2.1.2 L129 declares `set_realism(missing_rate,
  dirty_rate, censoring)` with `censoring` as an optional parameter; §2.8
  L532-534 includes "censoring" in the comment listing what δ does.
- **Spec is silent on:** the censoring schema — no parameter shape
  (right-censor at value? left? interval? per-column or global?
  threshold or rate?), no example, no algorithm. Missing/dirty have
  rate-based parameter contracts; censoring has none.
- **Implementation gap:** raises `NotImplementedError` if any non-None
  censoring is passed. To implement: (a) define the censoring config
  schema (likely a list of `{col, type: right|left|interval, threshold,
  ...}`), (b) implement the DataFrame transform that masks values beyond
  thresholds with a censoring marker (NaN? sentinel? separate indicator
  column?), (c) decide interaction with missing-value injection
  (precedence). All three require spec input.

### Dependency chain
- **Blocks:** nothing — DS-1 is a leaf.
- **Blocked by:** spec extension defining censoring's parameter schema
  and marker semantics; decision on whether censoring produces a separate
  indicator column (Phase 3 view extraction needs to know).
- **Co-dependent with:** missing-value injection ordering (whether
  censored cells can also be NaN'd) — but missing injection itself is
  already implemented, not another stub. Also co-dependent with
  `prompt.py:70-71` and the One-Shot Example, which today omit `censoring=`
  and must be updated together with any restoration. Restoration cost is
  thus **(a) define spec schema + (b) implement engine + (c) re-advertise
  in prompt + (d) update One-Shot Example**, not just (a)+(b).

### Blocking questions
- **Spec:** schema for the `censoring` config. Most natural extension of
  the existing `set_realism(missing_rate, dirty_rate, censoring)`
  signature is a per-column dict
  `{col: {"type": "right"|"left"|"interval", "threshold": ...}}`, but
  spec doesn't define this shape.
- **Spec:** marker semantics. Three options: (a) replace censored values
  with NaN (loses censoring info, simple), (b) sibling indicator column
  `<col>_censored` (preserves info but doubles column count and changes
  schema), (c) sentinel value (e.g., `inf` / `-inf` — fragile, family-
  dependent). Phase 3 view extraction needs to know which it is.
- **Spec:** ordering with missing-value injection — censoring before or
  after? If after, censored cells could already be NaN'd. If before,
  the missing-rate denominator differs.

### Proposed solution
Pick schema (a) per-column dict, marker (a) NaN replacement, ordering
"censoring before missing" (so missing-rate is computed against the
post-censor distribution). Mirror `inject_missing_values` /
`inject_dirty_values` structurally.

```python
# pipeline/phase_2/engine/realism.py — replace NotImplementedError block at L57-63.

def inject_censoring(
    df: pd.DataFrame,
    censoring_config: dict[str, dict[str, Any]],
    rng: np.random.Generator,  # unused but kept for signature symmetry
) -> pd.DataFrame:
    """Inject censoring on declared measure columns.

    Schema:
        censoring_config = {
            "wait_minutes": {"type": "right", "threshold": 100.0},
            "cost":         {"type": "left",  "threshold": 50.0},
            "score":        {"type": "interval", "low": 0.0, "high": 10.0},
        }

    For "right": values > threshold become NaN.
    For "left":  values < threshold become NaN.
    For "interval": values outside [low, high] become NaN.
    """
    if not censoring_config:
        return df

    total_censored = 0
    for col, spec in censoring_config.items():
        if col not in df.columns:
            logger.warning(
                "inject_censoring: column '%s' not in DataFrame; skipping.", col,
            )
            continue
        c_type = spec["type"]
        if c_type == "right":
            mask = df[col] > spec["threshold"]
        elif c_type == "left":
            mask = df[col] < spec["threshold"]
        elif c_type == "interval":
            mask = (df[col] < spec["low"]) | (df[col] > spec["high"])
        else:
            raise ValueError(
                f"Unknown censoring type '{c_type}' for column '{col}'. "
                f"Expected one of: right, left, interval."
            )
        df.loc[mask, col] = np.nan
        total_censored += int(mask.sum())

    logger.debug(
        "inject_censoring: censored %d cells across %d columns.",
        total_censored, len(censoring_config),
    )
    return df


# In inject_realism, replace the NotImplementedError branch with:
censoring = realism_config.get("censoring")
if censoring:
    df = inject_censoring(df, censoring, rng)
# (Run BEFORE missing/dirty so missing-rate is on the post-censor distribution.)
```

**Integration points:**
- `engine/realism.py::inject_realism` ([L25-65](pipeline/phase_2/engine/realism.py#L25-L65))
  — replace NotImplementedError branch and reorder so censoring runs
  first.
- `sdk/relationships.py::set_realism` already accepts `censoring` —
  upgrade param-validation to assert the new schema (per-column dict
  with `type` ∈ {right, left, interval} and `threshold` or `low`/`high`).

**New types:** optional `CensoringSpec(TypedDict)` in `types.py`:

```python
class CensoringSpec(TypedDict, total=False):
    type: Literal["right", "left", "interval"]
    threshold: float
    low: float
    high: float
```

### Test criteria
- Right-censoring: values above threshold become NaN, others unchanged.
- Left-censoring: symmetric.
- Interval: only out-of-range values are NaN'd.
- Missing column: warns and skips, no NaN injected anywhere.
- Empty config (`{}`): no-op.
- Unknown `type`: ValueError with clear message.
- Order: missing_rate computed against post-censor distribution
  (verified by row-count math).

### Estimated scope
**Small (20–80 LOC).** Body ≈ 35 LOC + schema validation in
`set_realism` ≈ 20 LOC + optional TypedDict ≈ 5 LOC + tests ≈ 50 LOC ≈
110 LOC total. Analog: `inject_missing_values` is ~30 LOC,
`inject_dirty_values` is ~60 LOC.

---

## [DS-2] 4 pattern type injection

### Code span
```python
# pipeline/phase_2/engine/patterns.py:61-71
elif pattern_type in (
    "ranking_reversal",
    "dominance_shift",
    "convergence",
    "seasonal_anomaly",
):
    # TODO [M1-NC-6]: Pattern injection for these types is deferred.
    raise NotImplementedError(
        f"Pattern type '{pattern_type}' injection not yet implemented. "
        f"See stage3 item M1-NC-6."
    )
```

### Spec references
- §2.1.2 (L119–127): `inject_pattern(type, target, col, params)` declares six
  pattern types: `outlier_entity`, `trend_break`, `ranking_reversal`,
  `dominance_shift`, `convergence`, `seasonal_anomaly`. Currently only the
  first two have concrete injection algorithms.
- §2.8 (L529–530): γ (pattern injection) is stage 3 of deterministic engine
  execution — applies declared patterns to post-measure DataFrame.
- §2.9 (L644–676): L3 pattern-validation pseudo-code references
  `outlier_entity`, `ranking_reversal`, `trend_break`, `dominance_shift`
  (convergence and seasonal_anomaly are not in the L3 sketch).

### Existing tests
- `tests/modular/test_validation_validator.py::test_validates_l3_layer_with_patterns` —
  L3 checks executed when only the *implemented* pattern types
  (`outlier_entity`, `trend_break`) are provided.
- `tests/modular/test_validation_autofix.py::TestAmplifyMagnitude::test_amplifies_z_score_on_matching_pattern` —
  Auto-fix amplification for outlier z_score (implemented type only).
- `tests/modular/test_validation_autofix.py::TestAmplifyMagnitude::test_amplifies_magnitude_on_matching_pattern` —
  Auto-fix amplification for trend_break magnitude.
- `tests/modular/test_validation_autofix.py::TestAmplifyMagnitude::test_skips_non_matching_patterns` —
  Auto-fix only updates matching pattern columns.
- (No tests exercise injection of the 4 deferred pattern types.)

### Dependent stubs
- IS-2: Dominance shift validation — `validation/pattern_checks.py:189-213`
- IS-3: Convergence validation — `validation/pattern_checks.py:216-239`
- IS-4: Seasonal anomaly validation — `validation/pattern_checks.py:242-265`
  (These three L3 checks cannot be exercised end-to-end until DS-2 lands —
  injection is what produces the data they would validate.)

### Role in pipeline
Sits in §2.8 step γ (pattern injection), in
[engine/patterns.py](pipeline/phase_2/engine/patterns.py)::`inject_patterns`.
Receives the post-measure DataFrame and a patterns list, dispatches per
`pattern_type`. Upstream: pattern specs from `sim.inject_pattern(type,
target, col, params)`. Downstream: mutated DataFrame consumed by realism
(δ) and validation (§2.9 L3). **The current SDK and prompt are both gated
to 2 types only** —
[sdk/relationships.py:29](pipeline/phase_2/sdk/relationships.py#L29)
`VALID_PATTERN_TYPES = {"outlier_entity", "trend_break"}` and
[orchestration/prompt.py:72](pipeline/phase_2/orchestration/prompt.py#L72)
advertises only those 2 — so the engine's `NotImplementedError` branch
for the 4 deferred types is currently **dead defensive code**. The spec
text (§2.5 L304-305) is the only document that still lists all 6.

### Gap analysis
- **Spec defines:** §2.1.2 L119-127 lists all 6 PATTERN_TYPES; §2.5
  L304-305 lists all 6 in the spec's prompt template; §2.8 step γ states
  patterns are applied; §2.9 L3 has a partial verification sketch only
  for `dominance_shift` (and no injection algorithm anywhere).
- **Spec is silent on:** the injection algorithm for any of the four
  types. For `ranking_reversal` the L3 verifier metric is sketched (rank
  correlation between two metrics in §2.9 L655-661), but nothing about
  how to *induce* the reversal. For `dominance_shift`, `convergence`,
  `seasonal_anomaly` the spec says only that they are valid type names.
  No params, no algorithm, no example.
- **Implementation gap:** the 4 types are **double-gated out** at
  declaration time (SDK rejects with ValueError) AND at the prompt level
  (LLM never sees them) — so the engine's `NotImplementedError` cannot
  actually be reached. Restoring them requires (a) updating
  `VALID_PATTERN_TYPES` and `PATTERN_REQUIRED_PARAMS`, (b) updating
  `prompt.py:72` (and the One-Shot example), (c) implementing four
  independent injection algorithms in `engine/patterns.py`, and (d)
  ensuring matching L3 validators (IS-2/3/4) ship together. Note: the
  `ranking_reversal` validator
  ([validation/pattern_checks.py::check_ranking_reversal](pipeline/phase_2/validation/pattern_checks.py))
  is already fully implemented but currently unreachable.

### Dependency chain
- **Blocks (when implemented):** end-to-end exercise of IS-2
  (dominance_shift validation), IS-3 (convergence validation), IS-4
  (seasonal_anomaly validation); also removes the silent failure mode
  where the LLM picks a valid-by-declaration but unimplementable pattern
  type.
- **Blocked by:** spec extension for each of the four pattern types
  (params contract + injection algorithm + matching validation algorithm
  where applicable); `ranking_reversal` has partial spec coverage
  (verifier defined, injector not) so a decision is needed about whether
  to spec the injector too.
- **Co-dependent with:** IS-2, IS-3, IS-4 — each `(injector, validator)`
  pair must share the same operational definition. Also co-dependent with
  `prompt.py:72` and `VALID_PATTERN_TYPES` — these are currently gated to
  the 2 implemented types, so any new injector must ship together with a
  prompt-and-SDK gate update.

### Blocking questions
- **Spec:** operational injection algorithm for each of the four types.
  Each must align with the corresponding L3 validator (IS-2/IS-3/IS-4)
  + the existing `check_ranking_reversal`. Without these definitions
  there are too many degrees of freedom.
- **Roadmap:** ship all four at once, or incrementally? `ranking_reversal`
  already has a working validator and is the easiest first target;
  `seasonal_anomaly` (window-spike) and `dominance_shift` (post-split
  shift) are mechanically similar to `trend_break`; `convergence` is the
  most novel.
- **Spec:** for `ranking_reversal`, the spec only covers the verifier —
  the injector contract is missing.

### Proposed solution
Per-type sketches, each mirroring `inject_outlier_entity` /
`inject_trend_break` patterns. Each function follows the same
boilerplate: `target_mask = df.eval(pattern["target"])`, validate
non-empty, raise `PatternInjectionError` on degeneracy, log on success.

```python
# pipeline/phase_2/engine/patterns.py — replace the 4-way NotImplementedError
# branch at L61-71 with explicit dispatch.

def inject_ranking_reversal(df, pattern, columns, meta):
    """Reverse rank order between two metrics at the *entity-mean* level.

    The verifier (check_ranking_reversal) groups by entity, takes per-
    entity means of m1 and m2, and checks rank correlation < 0. To
    reliably trigger that, the injector must operate at the entity-mean
    level — a row-level pairing of high-m1 with low-m2 is a heuristic
    that may not always shift group means (especially when entities have
    similar m1 distributions). The reliable algorithm:
      1. Group target rows by entity_col.
      2. Rank entities ascending by mean(m1) → rank_m1.
      3. Compute desired mean(m2) per entity by *reversing* rank_m1
         relative to the global mean(m2) distribution.
      4. Per entity, additively shift m2 values so the entity mean lands
         at the desired position (preserving within-entity variance).
    Pairs naturally with check_ranking_reversal (Spearman corr < 0).
    """
    m1, m2 = pattern["params"]["metrics"]
    entity_col = pattern["params"].get("entity_col") or _resolve_first_dim_root(meta)
    target_mask = df.eval(pattern["target"])
    if target_mask.sum() < 2 or entity_col is None:
        raise PatternInjectionError(pattern_type="ranking_reversal", ...)
    target_df = df.loc[target_mask]
    entity_means_m1 = target_df.groupby(entity_col)[m1].mean()
    entity_means_m2 = target_df.groupby(entity_col)[m2].mean()
    # Rank reverse: entity with highest m1 gets lowest m2 mean target
    rank_m1 = entity_means_m1.rank(ascending=True)
    sorted_m2 = entity_means_m2.sort_values(ascending=False).values
    desired_m2 = pd.Series(sorted_m2, index=rank_m1.sort_values().index)
    # Apply additive per-entity shift
    for entity, desired in desired_m2.items():
        rows_e = target_mask & (df[entity_col] == entity)
        shift = desired - df.loc[rows_e, m2].mean()
        df.loc[rows_e, m2] = df.loc[rows_e, m2] + shift
    return df


def inject_dominance_shift(df, pattern, columns):
    """Shift target subset's pattern["col"] post-split_point so the
    target_entity's mean exceeds its peers'."""
    # Resolve temporal_col (mirror inject_trend_break L189-194)
    # Compute peer_max from non-target rows (post-split)
    # post_split = target_mask & (temporal >= split_point)
    # shift = peer_max + magnitude * peer_std - df.loc[post_split, col].mean()
    # df.loc[post_split, col] += shift
    return df


def inject_convergence(df, pattern, columns):
    """Pull target rows toward global_mean as time progresses; magnitude
    grows linearly with normalized time within the target window."""
    # tval = pd.to_datetime(df[temporal_col])
    # tmin, tmax = tval.min(), tval.max()
    # for each target row: factor = (t - tmin)/(tmax - tmin) * pull
    # df[col] = df[col] * (1 - factor) + global_mean * factor
    return df


def inject_seasonal_anomaly(df, pattern, columns):
    """Scale target values inside anomaly_window by (1 + magnitude).
    Mirror inject_trend_break (L160-241) but with a finite [start, end]
    window instead of a half-line break_point."""
    win_start, win_end = pattern["params"]["anomaly_window"]
    magnitude = pattern["params"]["magnitude"]
    # in_win = target_mask & (temporal in [win_start, win_end])
    # df.loc[in_win, col] *= (1 + magnitude)
    return df


# Update inject_patterns dispatch at L52-78:
elif pattern_type == "ranking_reversal":
    df = inject_ranking_reversal(df, pattern, columns)
elif pattern_type == "dominance_shift":
    df = inject_dominance_shift(df, pattern, columns)
elif pattern_type == "convergence":
    df = inject_convergence(df, pattern, columns)
elif pattern_type == "seasonal_anomaly":
    df = inject_seasonal_anomaly(df, pattern, columns)
```

**Integration points:**
- `engine/patterns.py::inject_patterns` ([L29-86](pipeline/phase_2/engine/patterns.py#L29-L86))
  — replace the 4-way NotImplementedError branch with explicit dispatch
  to each new injector.
- `sdk/relationships.py::VALID_PATTERN_TYPES` ([L29](pipeline/phase_2/sdk/relationships.py#L29))
  — add the 4 names back.
- `sdk/relationships.py::PATTERN_REQUIRED_PARAMS` ([L39](pipeline/phase_2/sdk/relationships.py#L39))
  — add per-type required-params entries:
  ```
  "ranking_reversal":  frozenset({"metrics"})            # plus optional "entity_col"
  "dominance_shift":   frozenset({"entity_filter", "split_point"})
  "convergence":       frozenset()                        # all params optional
  "seasonal_anomaly":  frozenset({"anomaly_window", "magnitude"})
  ```
- `orchestration/prompt.py:72,190+` — re-advertise the types and add
  matching entries to the One-Shot example.

**New types:** none.

### Test criteria
- Per type: declaration with valid params succeeds; `inject_*` produces a
  post-condition that the matching L3 validator passes (round-trip).
- Per type: declaration with missing required param raises ValueError
  with type-specific detail.
- Edge: empty target subset → `PatternInjectionError` (mirror existing
  outlier behavior).
- Edge: missing temporal column for time-dependent types → graceful
  error (mirror `inject_trend_break` L195-202).
- Roundtrip integration: a script using all 4 new types runs Loop A end
  to end without crashing; L3 validator returns 4 passing checks.

### Estimated scope
**Large (200+ LOC).** Per-injector body ≈ 50–80 LOC × 4 ≈ 250 LOC,
plus relationships.py + prompt.py updates ≈ 30 LOC, plus tests
(unit + roundtrip) ≈ 150 LOC ≈ 430 LOC total. Comparable to
`inject_outlier_entity` + `inject_trend_break` combined (~150 LOC), ×2
for four injectors plus integration glue.

---

## [DS-3] Mixture KS test

### Code span
```python
# pipeline/phase_2/validation/statistical.py:259-264
if family == "mixture":
    return [Check(
        name=f"ks_{col_name}",
        passed=True,
        detail="mixture distribution KS test not yet implemented",
    )]
```

### Spec references
- §2.1.1 (L94): `"mixture"` is in `SUPPORTED_DISTRIBUTIONS`.
- §2.5 (L302): LLM prompt's allowed-distributions list includes `"mixture"`.
- §2.9 L2 (L206–314): Stub is part of `check_stochastic_ks()`. Predictor-cell
  enumeration (L212–221) and CDF construction via `_expected_cdf()`
  (L130–166) are described, but `_expected_cdf()` returns `None` for
  `family == "mixture"` (L165) — no component schema is defined.

### Existing tests
- (none found)

### Dependent stubs
- (none — DS-3 is a leaf; parent is IS-1.)

### Role in pipeline
Sits in §2.9 L2 statistical validation, in
[validation/statistical.py](pipeline/phase_2/validation/statistical.py)::`check_stochastic_ks`.
Called per-stochastic-measure after engine generation. Upstream: the
generated DataFrame, `col_meta` with `family="mixture"`, and the patterns
list (rows in pattern targets are excluded). Downstream: a list of
`Check` objects fed to `ValidationReport`. `AUTO_FIX` has a `ks_*`
strategy (`widen_variance`) but it doesn't naturally apply to mixture
(no single variance to widen).

### Gap analysis
- **Spec defines:** §2.9 L2 sketches KS testing for stochastic measures:
  `kstest(subset, family, args=expected_params)` over predictor cells
  (L618-621). §2.1.1 lists `mixture` in supported families.
- **Spec is silent on:** how to construct an expected CDF for a mixture
  given predictor-cell parameters. The L2 example uses
  `args=expected_params` which assumes a closed-form CDF; mixture
  requires a weighted sum of component CDFs, but how component params
  depend on predictors is undefined (because IS-1's `param_model` schema
  is undefined).
- **Implementation gap:** returns a hard-coded `passed=True` Check.
  Cannot be implemented until IS-1's mixture `param_model` schema is
  defined. Concretely: `_expected_cdf` at
  [validation/statistical.py:130-166](pipeline/phase_2/validation/statistical.py#L130-L166)
  has no explicit `mixture` branch — the function falls through to the
  bare `return None` on L166 for any unrecognized family — so mixture
  ends up returning `None`, but via fall-through, not a dedicated branch.
  The gap is at both the CDF-construction and kstest-orchestration
  levels.

### Dependency chain
- **Blocks:** nothing further.
- **Blocked by:** **IS-1** (cannot test what cannot be sampled); spec
  extension defining the mixture `param_model` schema (same blocker as
  IS-1).
- **Co-dependent with:** IS-1 — must be co-implemented to ensure the CDF
  used here matches the sampler used there. CLAUDE.md formally pairs
  them as parent-child.

### Blocking questions
- **Same as IS-1** — the mixture `param_model` schema must be settled
  first. Independent implementation impossible.
- **Operational:** scipy doesn't have a native mixture frozen-dist; use
  a small `_MixtureFrozen` adapter exposing only `.cdf()` (sufficient
  for `kstest(args=...)`).

### Proposed solution
Builds on IS-1's interpretation (a). Extend `_expected_cdf` and the
predictor-cell param walk to handle mixtures.

```python
# pipeline/phase_2/validation/statistical.py — extend _expected_cdf
# (currently L130-166; mixture branch returns None).

class _MixtureFrozen:
    """scipy frozen-dist-like adapter: exposes .cdf() for kstest.

    For a mixture of K components with weights w_k and frozen scipy
    distributions D_k, mixture.cdf(x) = sum(w_k * D_k.cdf(x)).
    """
    def __init__(self, components: list[tuple[float, Any]]):
        self.components = components  # list of (weight, frozen_dist)

    def cdf(self, x: np.ndarray) -> np.ndarray:
        return sum(w * d.cdf(x) for w, d in self.components)


def _expected_cdf_mixture(params: dict[str, Any]) -> Optional[_MixtureFrozen]:
    """Build a mixture frozen-dist from per-cell mixture params.

    Schema (from IS-1): params = {"components": [{family, weight, params}, ...]}
    """
    components = params.get("components")
    if not components:
        return None
    frozen = []
    total_weight = 0.0
    for comp in components:
        sub = _expected_cdf(comp["family"], comp["params"])
        if sub is None:
            return None  # one unsupported component → skip the whole test
        frozen.append((comp["weight"], sub))
        total_weight += comp["weight"]
    if total_weight <= 0:
        return None
    # Auto-normalize
    return _MixtureFrozen([(w / total_weight, d) for w, d in frozen])


# In _expected_cdf, replace the implicit `return None` for mixture with:
elif family == "mixture":
    return _expected_cdf_mixture(params)


# In check_stochastic_ks (L259-264), drop the early-return special case
# entirely — the predictor-cell loop will now construct mixture CDFs
# via the standard path.
```

For per-cell param computation, extend `_compute_cell_params` (L169-203)
to walk the components list:

```python
def _compute_cell_params(col_meta, predictor_values, columns_meta):
    """Return either a flat {param_key: theta} dict (non-mixture) or
    a {"components": [{family, weight, params}, ...]} dict (mixture)."""
    if col_meta.get("family") == "mixture":
        return {
            "components": [
                {
                    "family": comp["family"],
                    "weight": comp["weight"],
                    "params": _compute_cell_params_for_subspec(
                        comp, predictor_values, columns_meta,
                    ),
                }
                for comp in col_meta["param_model"]["components"]
            ]
        }
    # ... existing flat-params branch
```

**Integration points:**
- `validation/statistical.py::_expected_cdf` ([L130-166](pipeline/phase_2/validation/statistical.py#L130-L166))
  — add mixture branch.
- `validation/statistical.py::check_stochastic_ks` ([L259-264](pipeline/phase_2/validation/statistical.py#L259-L264))
  — drop the mixture early-return; the predictor-cell loop now handles
  it through the standard path.
- `validation/statistical.py::_compute_cell_params` ([L169-203](pipeline/phase_2/validation/statistical.py#L169-L203))
  — branch on `family == "mixture"` to walk components.

**New types:** `_MixtureFrozen` (private adapter in
`validation/statistical.py`).

### Test criteria
- 2-component gaussian mixture sampled from IS-1 → KS test passes.
- Mismatched mixture (samples drawn from different params than declared)
  → KS test fails.
- Single-component mixture (weight=1.0) → behaves identically to a
  non-mixture KS test on that family.
- Component with unsupported family (e.g., poisson) → returns None and
  the predictor cell is skipped with the existing "CDF not available"
  detail.
- Auto-normalization: components with weights `[0.3, 0.2]` are tested
  with effective `[0.6, 0.4]`.

### Estimated scope
**Small (20–80 LOC).** `_MixtureFrozen` ≈ 15 LOC + `_expected_cdf_mixture`
≈ 20 LOC + cell param walk ≈ 25 LOC + tests ≈ 70 LOC ≈ 130 LOC.
**Cannot ship before IS-1.**

---

## [DS-4] Multi-column group dependency `on`

### Code span
```python
# pipeline/phase_2/sdk/relationships.py:123-132
# P2-4: Restrict to single-column `on` for v1
if not on:
    raise ValueError(
        f"'on' must contain at least one column, got empty list."
    )
if len(on) != 1:
    raise NotImplementedError(
        f"Multi-column 'on' is not supported in v1. "
        f"Got on={on} (length {len(on)}). Use a single column."
    )
```

### Spec references
- §2.1.2 (L106–117): `add_group_dependency()` signature — `on` is a list
  parameter; nested `conditional_weights` keyed on parent values is
  documented. Spec does not explicitly restrict `on` length, but multi-column
  is deferred (`P2-4` marker in code).
- §2.2 (L133–160): Dimension Groups and Cross-Group Relations — root-level
  dependency graph and conditional weights; all spec examples use a
  single-column `on`.

### Existing tests
- (No test exercises multi-column `on`; it is blocked by the
  `NotImplementedError`.)
- `tests/modular/test_sdk_dag.py` covers single-column `on` scenarios.

### Dependent stubs
- (none — DS-4 is a leaf; parent is the spec of nested `conditional_weights`.)

### Role in pipeline
Sits in §2.1.2 / §2.2 — SDK declaration step. `add_group_dependency(child_root,
on, conditional_weights)` accepts `on` as a list (always has) but
enforces `len(on) == 1` with a `NotImplementedError`. Downstream consumer
would be the engine generator α-step, which would compute
`P(child | a, b)` via a nested conditional table. Currently a script
with multi-column `on` crashes at declaration time, before the engine
ever runs.

### Gap analysis
- **Spec defines:** §2.1.2 L106-117 declares `on` as a list parameter
  (multi-column is implied by the type); §2.2 L150 — "the root-level
  dependency graph must be a DAG"; the spec example uses single-column
  `on=["severity"]` but does NOT explicitly forbid multi-column.
- **Spec is silent on:** the `conditional_weights` structure for
  multi-column `on`. With single-column `on=["severity"]`, weights are
  keyed by parent value: `{"Mild": {...}, "Moderate": {...}}`. With
  `on=["severity", "hospital"]`, the spec doesn't say whether it's
  nested (`{"Mild": {"Xiehe": {...}}}`), tuple-keyed
  (`{("Mild", "Xiehe"): {...}}`), or a flat Cartesian map. No example
  exists.
- **Implementation gap:** raises `NotImplementedError` when
  `len(on) != 1`. To implement: (a) define the multi-key
  `conditional_weights` structure (nested dicts is the most natural
  fit), (b) extend declaration validation in `add_group_dependency` to
  walk the nested dict and check coverage of the Cartesian product,
  (c) extend the engine sampling step to evaluate the nested
  conditional, (d) extend the root DAG acyclicity check to handle
  multi-parent edges.

### Dependency chain
- **Blocks:** nothing in the inventory.
- **Blocked by:** spec extension clarifying the nested-vs-tuple weight
  schema, normalization rule, and how missing combinations are handled.
- **Co-dependent with:** nothing in the inventory.

### Blocking questions
- **Spec:** `conditional_weights` structure for multi-column `on`. Two
  reasonable choices: (a) nested dict keyed by parent value sequence
  (`{"Mild": {"Xiehe": {"Insurance": 0.8, ...}}}`), (b) tuple-keyed flat
  dict (`{("Mild", "Xiehe"): {"Insurance": 0.8, ...}}`). Nested is
  JSON-serializable and a natural extension of the single-column case.
- **Spec:** must the Cartesian product be fully covered, or is partial
  coverage allowed (with a default fallback)? Single-column case
  requires full coverage — extending the same rule is cleanest.
- **Operational:** N-way cardinality blow-up — for `on=[a, b, c]` with
  cardinalities 5×4×3, the LLM must declare 60 inner weight dicts.
  Should there be a soft cap to avoid prompt overflow?

### Proposed solution
Pick (a) nested dict, require full Cartesian coverage (matches existing
single-column rule), no soft cap (LLM responsibility — surface a clear
error if blow-up is excessive).

```python
# pipeline/phase_2/sdk/relationships.py — replace the
# NotImplementedError block at L123-132.

def add_group_dependency(
    columns: OrderedDict[str, dict[str, Any]],
    groups: dict[str, DimensionGroup],
    group_dependencies: list[GroupDependency],
    orthogonal_pairs: list[OrthogonalPair],
    child_root: str,
    on: list[str],
    conditional_weights: dict[Any, Any],  # nesting depth = len(on)
) -> None:
    if not on:
        raise ValueError("'on' must contain at least one column.")

    # Existing: validate child_root + each parent is a group root
    if child_root not in columns:
        raise ValueError(f"Column '{child_root}' not found in registry.")
    if not _groups.is_group_root(child_root, columns, groups):
        raise NonRootDependencyError(column_name=child_root)
    for parent_col in on:
        if parent_col not in columns:
            raise ValueError(f"Column '{parent_col}' not found in registry.")
        if not _groups.is_group_root(parent_col, columns, groups):
            raise NonRootDependencyError(column_name=parent_col)

    # Existing: orthogonal-conflict check, run for each parent
    child_group = _groups.get_group_for_column(child_root, columns)
    for parent_col in on:
        parent_group = _groups.get_group_for_column(parent_col, columns)
        if child_group and parent_group:
            _check_orthogonal_conflict(child_group, parent_group, orthogonal_pairs)

    # Existing: root DAG acyclicity, run for each parent edge
    for parent_col in on:
        _dag.check_root_dag_acyclic(group_dependencies, child_root, parent_col)

    # Validate + normalize nested weights
    parent_value_sets = [columns[p]["values"] for p in on]
    child_values = columns[child_root]["values"]
    normalized_cw = _validate_and_normalize_nested_weights(
        conditional_weights, parent_value_sets, child_values, depth=len(on),
        path=[],
    )

    dep = GroupDependency(
        child_root=child_root, on=list(on),
        conditional_weights=normalized_cw,
    )
    group_dependencies.append(dep)


def _validate_and_normalize_nested_weights(
    cw: dict, parent_value_sets: list[list[Any]],
    child_values: list[Any], depth: int, path: list[Any],
) -> dict:
    """Recursively validate that cw covers the Cartesian product of
    parent_value_sets and that leaves cover child_values.
    """
    if depth == 0:
        # Leaf: cw is {child_val: weight}
        provided = set(cw.keys())
        expected = set(child_values)
        missing = expected - provided
        if missing:
            raise ValueError(
                f"conditional_weights{path} missing child values: {sorted(missing)}."
            )
        extra = provided - expected
        if extra:
            raise ValueError(
                f"conditional_weights{path} contains keys not in child values: {sorted(extra)}."
            )
        return _val.normalize_weight_dict_values(
            label=f"conditional_weights{path}", weights=cw,
        )
    # Recursive level: cw is {parent_val: <nested>}
    expected = set(parent_value_sets[0])
    provided = set(cw.keys())
    missing = expected - provided
    if missing:
        raise ValueError(
            f"conditional_weights{path} missing parent values at depth "
            f"{len(path)}: {sorted(missing)}."
        )
    return {
        k: _validate_and_normalize_nested_weights(
            v, parent_value_sets[1:], child_values,
            depth - 1, path + [k],
        )
        for k, v in cw.items()
    }
```

Engine side (extending the existing single-parent group-dep sampler):

```python
# pipeline/phase_2/engine/generator.py (or wherever group deps are sampled)

def _sample_group_dep(
    dep: GroupDependency, rows: dict[str, np.ndarray],
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample child_root values per row given multi-parent conditional weights."""
    cw = dep.conditional_weights
    n_rows = len(next(iter(rows.values())))
    parent_arrays = [rows[p] for p in dep.on]

    out = np.empty(n_rows, dtype=object)
    for i in range(n_rows):
        node = cw
        for parent_arr in parent_arrays:
            node = node[parent_arr[i]]  # walk N levels deep
        # node is now {child_val: weight}
        child_vals = list(node.keys())
        weights = np.fromiter(node.values(), dtype=float)
        out[i] = rng.choice(child_vals, p=weights / weights.sum())
    return out
```

Validation side: extend `max_conditional_deviation` to recursively walk
the same nested structure.

**Integration points:**
- `sdk/relationships.py::add_group_dependency` ([L101-213](pipeline/phase_2/sdk/relationships.py#L101-L213))
  — replace the `len(on) != 1` NotImplementedError; add
  `_validate_and_normalize_nested_weights`.
- `sdk/dag.py::check_root_dag_acyclic` — already handles single-parent
  edges; called once per parent in `on`.
- `engine/generator.py` — extend the group-dep sampling step from a
  flat `cw[parent_val]` lookup to N-deep walk.
- `validation/statistical.py::max_conditional_deviation` ([L24-55](pipeline/phase_2/validation/statistical.py#L24-L55))
  — extend deviation comparison to walk N-deep nested dicts.

**New types:** none (continues using `dict[Any, Any]`; `GroupDependency`
already accepts `on: list[str]`).

### Test criteria
- 2-parent dependency with full Cartesian coverage → declaration
  succeeds; engine sampling reproduces declared conditional within 10%
  deviation.
- Missing combination (one parent value absent at depth 1) → ValueError
  listing the missing key path.
- Missing inner combination (one child value missing at a leaf) →
  ValueError with full path.
- Existing single-column tests still pass (backward compat: depth=1
  case must produce the same normalized output as before).
- L2 group-dep deviation check correctly identifies divergent
  observations on multi-parent specs.

### Estimated scope
**Medium (80–200 LOC).** Nested-weight walk ≈ 50 LOC + engine sampler
extension ≈ 30 LOC + validation deviation walk ≈ 30 LOC + tests ≈ 80
LOC ≈ 190 LOC total. About 2× the single-column footprint; recursion
replaces flat 2-level dict logic in three call sites.

---

# Phase A summary

- **Confirmed stubs:** all 10 inventory entries (IS-1..IS-6, DS-1..DS-4)
  exist as described, though IS-1 line range drifted from `~L297-303`
  (CLAUDE.md) to `L360-366` (actual).
- **Stubs with no test coverage at all:** IS-1, IS-2, IS-3, IS-4, DS-1,
  DS-3, DS-4 (7 of 10).
- **Stubs with explicit "rejection" tests:** IS-5
  (`test_add_measure_rejects_scale_kwarg`).
- **Stubs with implicit coverage via "implemented-types-only" tests:**
  DS-2 (validator/auto-fix tests run, but only on `outlier_entity` /
  `trend_break`).
- **Spec absent or thin:** IS-3 (convergence) and IS-4 (seasonal_anomaly)
  appear in `inject_pattern` PATTERN_TYPES but have no L3 validation
  pseudo-code in §2.9; convergence has no defined algorithm at all.
- **Cross-stub dependency chains identified:**
  - IS-1 → DS-3 (mixture KS test depends on mixture sampling)
  - DS-2 → IS-2, IS-3, IS-4 (pattern validation cannot be exercised
    end-to-end until pattern injection is implemented)
- **"Double-gated out" defensive pattern (cross-cutting).** Three stubs
  follow the same SDK-accepted-but-prompt-omitted pattern: **IS-5**
  (`scale=` removed from `add_measure` signature in
  `prompt.py:53-54`), **DS-1** (`censoring=` removed from `set_realism`
  signature in `prompt.py:70-71`), and **DS-2** (4 pattern types removed
  from `prompt.py:89` PATTERN_TYPES list and from `VALID_PATTERN_TYPES`
  in `sdk/relationships.py:29`). All three were defensively removed to
  prevent LLMs from spending retry budget tuning dead parameters. Any
  restoration requires updating all three sites plus the One-Shot
  Example, not just the engine-side stub.

---

# Phase B summary

- **Spec gaps dominate over code gaps, with caveats.** 6-7 of 10 stubs
  are blocked at least partially by missing spec definitions. Two
  exceptions: **IS-6** is purely operational (multi-error / token
  budget — explicitly noted as not a spec feature), and **DS-2's
  `ranking_reversal` injector** could derive its contract from the
  existing verifier (already specified in §2.9 L655-661), so it is not
  strictly spec-blocked.
  - IS-3 (convergence) and IS-4 (seasonal_anomaly) have the thinnest
    spec coverage — neither has any pseudocode in §2.9 L3.
  - IS-5 (`scale`) is a vestigial signature line in spec with no
    behavioral content; spec/prompt/SDK have all converged on omission.
- **Two clean co-dependent pairs:** `(IS-1, DS-3)` for mixture
  sampling/validation and `(DS-2, [IS-2, IS-3, IS-4])` for pattern
  injection/validation. Each pair must share an operational definition;
  implementing one side without the other produces silent drift.
- **DS-2 is the most consequential pattern-related stub.** The 4
  deferred pattern types are double-gated out (SDK rejects + prompt
  doesn't advertise); restoring them requires touching all of
  `engine/patterns.py`, `sdk/relationships.py`, `prompt.py` plus IS-2/3/4
  validators. The engine's `NotImplementedError` branch for the 4 types
  is currently dead defensive code.
- **`check_ranking_reversal` is fully implemented but unreachable** —
  the validator is ready, but the SDK won't accept the type and there's
  no injector. A shovel-ready first step.
- **IS-6 stands apart.** Pure capability gap, no `NotImplementedError`,
  two independent sub-features (multi-error collection + token budget)
  that could ship separately. Both are operational optimizations not in
  spec.
- **Leaf stubs (DS-1, DS-4):** isolated; only blocked by spec decisions
  about parameter schemas (censoring config, multi-column
  conditional_weights nesting).

---

# Phase C summary

| Stub  | Recommendation | Scope | Critical blocker |
|-------|----------------|-------|------------------|
| IS-1  | Implement w/ component-`param_model` schema (interp. (a)) | Medium | Spec decision on mixture schema |
| IS-2  | Implement as rank-change-across-split (interp. (a)) | Small | Spec decision on dominance metric |
| IS-3  | Implement as group-mean variance reduction (interp. (b)) | Small | Spec decision on convergence metric |
| IS-4  | Implement as window-vs-baseline z-score (interp. (a)) | Small | Spec decision on seasonal definition |
| IS-5  | **Do not restore** — strip vestigial signature from spec | Trivial | None (already correct state) |
| IS-6  | Defer; ship token-budget half first if needed | Large | A/B test on multi-error feedback efficacy |
| DS-1  | Implement as per-column NaN-marker censoring | Small | Spec decision on schema + marker |
| DS-2  | Implement 4 injectors; `ranking_reversal` first | Large | Spec decision on each injection algorithm |
| DS-3  | Implement after IS-1; `_MixtureFrozen` adapter | Small | IS-1 ships first |
| DS-4  | Implement w/ nested-dict `conditional_weights` (a) | Medium | Spec decision on weight nesting |

**Total estimated scope** (if everything ships): roughly 1.5k LOC of
implementation + tests, dominated by IS-6 (~340 LOC) and DS-2
(~430 LOC). IS-1+DS-3 are tightly coupled (~300 LOC together).

**Recommended sequencing** if reducing risk + time-to-value:

1. **IS-5 docs cleanup (trivial).** Strip the vestigial `scale=None`
   signature line from spec §2.1.1 L51 and §2.5 L287 to match the
   prompt and SDK, both of which already omit it. No code changes.
2. **DS-1 censoring (small).** Leaf stub, isolated, decision is
   schema-only — spec it once and ship.
3. **`ranking_reversal` reactivation (small).** Validator already
   exists; only need an injector + SDK gate update + prompt update.
   Lowest-effort win in the DS-2 cluster.
4. **IS-3, IS-4, IS-2 + remaining DS-2 injectors (medium-large).** Pair
   each validator with its injector once spec lands.
5. **IS-1 + DS-3 (medium, paired).** Highest spec dependency; do
   together.
6. **DS-4 multi-column on (medium).** Independent; ship when LLM
   workflows demand multi-parent dependencies.
7. **IS-6 (large).** Optimization; defer until retry-loop overhead is
   measured to be a real bottleneck.

**Common-cause spec extensions needed** (to unblock the largest
fraction of stubs):
- Mixture `param_model` schema (unblocks IS-1 + DS-3).
- Operational definitions of `dominance_shift`, `convergence`,
  `seasonal_anomaly` injection + validation (unblocks IS-2/3/4 + 3 of
  the 4 DS-2 sub-features).
- Censoring config schema + marker semantics (unblocks DS-1).
- Multi-column `conditional_weights` nesting rule (unblocks DS-4).

Stub gap analysis complete.
