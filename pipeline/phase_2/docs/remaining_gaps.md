## 4. Remaining Stubs & Known Limitations

All 36 NEEDS_CLAR items have been resolved. The items below are **intentional stubs** per decisions in `decisions/blocker_resolutions.md` — each requires spec clarification or a design decision before implementation.

### 4.1 Intentional Stubs (5)

#### Mixture Distribution Sampling (P1-1 / M1-NC-1)
- **Location:** `phase_2/engine/measures.py:360-366`
- **Behavior:** `_sample_stochastic()` raises `NotImplementedError` when `family == "mixture"`. Declaration via `add_measure("x", "mixture", {...})` succeeds (family is in `SUPPORTED_FAMILIES`), but `generate()` fails.
- **Blocked on:** The `param_model` schema for mixture distributions (component families, mixing weights, per-component parameters) is not defined in the spec.
- **To unstub:** Define the schema (suggested: `{"components": [{"family": "gaussian", "weight": 0.6, "params": {"mu": {...}, "sigma": {...}}}, ...]}`). Implement weighted-component sampling. Implement the corresponding KS test in `statistical.py`.

#### Dominance Shift Validation (P1-3 / M5-NC-4)
- **Location:** `phase_2/validation/pattern_checks.py:189-213`
- **Behavior:** `check_dominance_shift()` returns `Check(passed=True, detail="dominance_shift validation not yet implemented")`. Patterns can be declared (params validated), but validation always passes.
- **Blocked on:** The validation algorithm is not defined in the spec. The params schema (`entity_filter`, `col`, `split_point`) exists, but the rank-change-across-temporal-split logic is unspecified.
- **To unstub:** Define the algorithm: filter to entity, compute metric rank before/after `split_point`, check rank changed as declared.

#### Convergence Validation (P1-4 / M5-NC-5)
- **Location:** `phase_2/validation/pattern_checks.py:216-239`
- **Behavior:** `check_convergence()` returns `Check(passed=True, detail="convergence validation not yet implemented")`. Declaration succeeds (no required params), validation always passes.
- **Blocked on:** Completely absent from spec §2.9. No params schema, no validation logic, no examples.
- **To unstub:** Requires full spec definition: what converges, over what dimension, what threshold constitutes convergence.

#### Seasonal Anomaly Validation (P1-4 / M5-NC-5)
- **Location:** `phase_2/validation/pattern_checks.py:242-265`
- **Behavior:** Same as convergence — declaration succeeds, validation always passes.
- **Blocked on:** Completely absent from spec. No params, no validation logic.
- **To unstub:** Requires full spec definition: what constitutes a seasonal anomaly, which temporal features to check, detection thresholds.

#### `scale` Kwarg on `add_measure` (M?-NC-scale)
- **Location:** `phase_2/sdk/columns.py:214-215` (`TODO [M?-NC-scale]` marker), mirrored in `phase_2/orchestration/prompt.py`.
- **Behavior:** `add_measure(name, family, param_model)` no longer accepts a `scale` keyword argument. Passing `scale=...` raises `TypeError: add_measure() got an unexpected keyword argument 'scale'`. The prompt no longer advertises the kwarg.
- **History:** Previously accepted but silently no-op (emitted a "stored but has no effect" warning). Removed in round-3 GPT failure fixes (`docs/fixes/GPT_FAILURE_ROUND_3_FIXES.md`) because LLMs treated it as a meaningful knob and burned retry budget tuning a dead parameter — same advertising-a-nonfeature class as `censoring=` and the deferred pattern types removed in round 2.
- **To unstub:** Implement a scaling mechanism (e.g., post-sampling multiplicative scaling of measure values), then restore the `scale` kwarg in `sdk/columns.py` and re-add it to the `add_measure` signature shown in `orchestration/prompt.py`. Grep for `TODO [M?-NC-scale]` to find both sites.

#### ~~Primary-Key Protection in `set_realism` (REM-realism-pk-protection)~~ — RESOLVED 2026-05-07
- **Resolution:** `_primary_key_columns(columns)` helper in `engine/realism.py` identifies categorical roots (`type=='categorical'` AND `parent is None`); `inject_realism` forwards them as `protected_columns=` to `inject_missing_values`, which forces those columns' mask cells to `False` before applying. The xfail decorator on `tests/modular/test_realism.py::TestPrimaryKeyProtection::test_primary_key_categorical_root_never_nulled_at_rate_one` was removed; three complementary tests added (intermediate rate `0.5`, child categorical NOT protected, multiple group roots all protected) plus a regression guard that direct callers of `inject_missing_values` without `protected_columns` keep the all-cells-masked default.
- **Out of scope (separate spec violation, not addressed by this resolution):** `inject_dirty_values` (`engine/realism.py:157`) iterates *all* categorical columns including roots and may character-perturb a PK string ("Xiehe" → "Xeihe") at `dirty_rate>0`. Spec §2.1.1 protects "primary key" without scoping to missing-only, so this is a remaining gap. Tracked for a future round; closing it requires the same skip-set threading into `inject_dirty_values`.

#### M3 Context Window / Multi-Error (M3-NC-3, M3-NC-4)
- **Location (NC-3):** `phase_2/sdk/simulator.py:32-36` — TODO comment noting one-error-at-a-time limitation.
- **Location (NC-4):** No explicit TODO marker in `phase_2/orchestration/sandbox.py`; current behavior is that `history` at `phase_2/orchestration/sandbox.py:703` (and the `prior_failures` slice at `:728`) accumulates every failure and is passed to the LLM without truncation.
- **Behavior:** (NC-3) The sandbox catches one exception per execution; multiple simultaneous SDK errors are surfaced one per retry. (NC-4) Full error history is sent to the LLM without truncation.
- **Status:** Both are functional and acceptable within the default `max_retries=3` budget. These are accepted limitations, not broken functionality.
- **To fix:** NC-3: Collect validation errors into a compound exception in M1. NC-4: Add token counting before each retry; truncate/summarize older failures if budget exceeded.

### 4.2 Dependent Stubs (4)

These exist in other modules as consequences of the 5 intentional stubs above. They resolve automatically when their parent stub is resolved.

#### Censoring Injection (depends on M1-NC-7)
- **Location:** `phase_2/engine/realism.py:59-63`
- **Behavior:** `inject_realism()` raises `NotImplementedError` when `realism_config["censoring"]` is non-None. `set_realism(censoring=...)` accepts and stores the parameter, but the engine-side injection is deferred.
- **Resolves when:** The spec defines what censoring means concretely (which columns, what mechanism).

#### Four Pattern Type Injection (depends on M1-NC-6)
- **Location:** `phase_2/engine/patterns.py:67-71`
- **Behavior:** `inject_patterns()` raises `NotImplementedError` for `ranking_reversal`, `dominance_shift`, `convergence`, and `seasonal_anomaly`.
- **Note:** These are **injection** stubs (M2 — how to modify the DataFrame to create the pattern), separate from the **validation** stubs above (M5 — how to check if the pattern exists). Ranking reversal validation is fully implemented, but ranking reversal injection is still stubbed.
- **Resolves when:** The injection algorithms are defined (how to artificially create each pattern in generated data).

#### Mixture KS Test (depends on P1-1)
- **Location:** `phase_2/validation/statistical.py:259-264`
- **Behavior:** `check_stochastic_ks()` returns `Check(passed=True)` when `family == "mixture"`.
- **Resolves when:** Mixture distribution sampling is implemented.

#### Multi-Column Group Dependency `on` (P2-4 / M1-NC-5)
- **Location:** `phase_2/sdk/relationships.py:126-130`
- **Behavior:** `add_group_dependency()` raises `NotImplementedError` when `len(on) != 1`. Single-column `on` works fully.
- **Blocked on:** The nested `conditional_weights` structure for 2+ conditioning columns is not specified.
- **Resolves when:** The spec defines the multi-column conditional_weights structure (e.g., Cartesian product keys vs. hierarchical nesting).