# Phase 2 Test-Robustness Audit — 2026-05-07

## Purpose

The user has been incrementally adding tests as `pipeline/phase_2/` was built out, and is no longer confident the suite faithfully covers Phase 2 functionality as described in [`storyline/data_generation/phase_2.md`](../../../storyline/data_generation/phase_2.md). This document records every distinct corner-cutting finding turned up by a harsh, evidence-based audit, the spec contract each finding violates, and the concrete fix that will close it.

The goal is **harshest-attitude** scrutiny: tolerance abuse, mocked-away difficulty, happy-path bias, oracle reuse, uncontrolled randomness, and silent stubs are all flagged.

## Methodology

1. **Three parallel Explore audits** with disjoint file partitions:
   - Agent A — large patterns / multi-parent / SDK validation (3 files, ~2.1k lines).
   - Agent B — L3 stubs newly-implemented + mixture + multi-parent skeleton (6 files, ~1.1k lines).
   - Agent C — validator / autofix / sandbox / realism / metadata / SDK columns / DAG (7 files, ~1.2k lines).
2. **Direct verification** — re-read the highest-severity findings against `pipeline/phase_2/` source so claims are grounded in the *active* implementation (the audit was originally run against an outdated `phase_2_new` directory before being re-targeted).
3. **Baseline pytest** — `274 passed, 3 warnings in 1.54s` against the chart conda env; this is the green floor every fix must preserve.

## Severity convention

- **CRITICAL** — spec promise has no enforcement at all (test cannot fail / test mocks away the path under test / test relies on uncontrolled randomness so any-impl-passes).
- **HIGH** — spec promise has tolerance abuse (asserts a property weaker than spec) or oracle-reuse (validator and injector share the same code path so injector bugs are masked).
- **MEDIUM** — spec promise has missing edge / boundary / negative case but the happy path is covered.

## Findings (verified, with reasons)

Each finding cites the active test file (line numbers verified via `Read` against `pipeline/phase_2/tests/`), the spec section it violates, and the concrete fix that closes it.

### CRITICAL findings

#### T1.1 — `SchemaAwareValidator.validate` never runs unmocked

- **File:** [`tests/modular/test_validation_validator.py`](../tests/modular/test_validation_validator.py) lines 19-22, 53-55, 95.
- **Spec promise:** §2.6 — three-layer validator must "check correctness at three levels" against a real DataFrame. The orchestrator is the single entry point external code uses (`validation/validator.py:48`).
- **What's there:** Every test in this file `@patch`es L1/L3 check functions (`check_row_count`, `check_categorical_cardinality`, `check_orthogonal_independence`, `check_measure_dag_acyclic`, `check_outlier_entity`, `check_trend_break`). Tests verify the orchestrator *calls* the mocks, not that real checks *work end-to-end* on a real DataFrame.
- **Why it's a corner cut:** A bug in `_run_l1` / `_run_l2` / `_run_l3` — wrong args, wrong order, swallowed exception, missed marginal_weights / measure_finiteness call (added later at `validator.py:172-175`) — would slip through every existing test.
- **Fix:** Add `test_validates_real_dataframe_end_to_end_passes` and `test_validates_real_dataframe_catches_cardinality_mismatch` that build (a) a clean seeded DataFrame matching its metadata, expecting `report.all_passed`, and (b) a DataFrame whose `hospital` column has 2 unique values when meta declares cardinality=5, expecting `cardinality_hospital` failure with extracted detail. No `@patch` anywhere.

#### T1.2 — `run_pipeline` determinism never tested unmocked

- **File:** [`tests/modular/test_engine_generator.py`](../tests/modular/test_engine_generator.py) lines 19-24.
- **Spec promise:** §2.5 — *"Given the same `seed`, output is bit-for-bit reproducible."* Stage chain is `M = τ_post ∘ ρ ∘ φ ∘ ψ ∘ λ ∘ γ ∘ δ ∘ β(seed)`.
- **What's there:** The only `run_pipeline` test `@patch`es `_postprocess.to_dataframe`, `_measures.generate_measures`, `_skeleton.build_skeleton`, `_dag.topological_sort`, `_dag.build_full_dag`, `metadata.builder.build_schema_metadata` — i.e. the entire pipeline. Test only verifies *call order*, not output equality.
- **Why it's a corner cut:** Loop B (`generate_with_validation`) explicitly relies on deterministic re-execution with overrides. If `np.random.default_rng(seed)` were ever moved out of `run_pipeline` (e.g., into a stage that re-seeds), every existing test would still pass while the autofix loop silently broke.
- **Fix:** New file `tests/modular/test_engine_determinism.py` with stage-by-stage tests:
  - `build_skeleton` twice with `np.random.default_rng(42)` → same `dict[str, np.ndarray]` (np.array_equal per key).
  - `generate_measures` twice with same seed/rows → same arrays.
  - `inject_patterns` twice → `pd.testing.assert_frame_equal`.
  - `inject_realism` twice → `assert_frame_equal`.
  - `run_pipeline` end-to-end twice with seed=42 → `assert_frame_equal` on the full output (no mocks).

#### T1.3 — Chi² independence test relies on uncontrolled `np.random`

- **File:** [`tests/modular/test_validation_structural.py`](../tests/modular/test_validation_structural.py) lines 65-85.
- **Spec promise:** §2.6 L1 — *"Chi-squared test on root-level cross-group pairs; flags warning if p < 0.05."* Production threshold is `p > 0.05` ([`validation/structural.py:170`](../validation/structural.py#L170)).
- **What's there:** `test_independent_features` (line 65) builds 400-row data via bare `np.random.choice(...)` with no seed. Code comment at line 83-84: *"Random failures are possible but extremely rare."*
- **Why it's a corner cut:** The test is structurally flaky — every CI run rolls dice. No companion test exercises the failure side (`p ≤ 0.05` on dependent data), so the failing branch at `validation/structural.py:170` is unverified. The detail-string `"χ² p={p_val:.4f}"` is also never parsed-and-asserted, so the threshold semantic is invisible to tests.
- **Fix:** Replace with two seeded tests: `test_passes_for_seeded_independent_data` (seeded RNG, extract `p` from detail, assert `> 0.05`) and `test_fails_for_seeded_dependent_data` (hand-constructed strongly-dependent contingency, assert `not passed` and extracted `p ≤ 0.05`).

#### T1.4 — Auto-fix "healing" never verified end-to-end

- **File:** [`tests/modular/test_validation_autofix.py`](../tests/modular/test_validation_autofix.py) lines 192-260, 262-297.
- **Spec promise:** §2.6 — *"Auto-fix applies targeted parameter adjustments — correlation relaxation, variance widening, pattern amplification — and re-runs the engine. Typically converges in 1–2 retries at near-zero cost."*
- **What's there:** `test_non_mixture_widens_through_raw_widen_variance` verifies that `seen_overrides[2]["measures"]["revenue"]["sigma"] == pytest.approx(1.44)` — i.e., the override factor *compounds* (1.2 → 1.44). But `_StubKSFailingValidator` always returns failure; there is no test where the override actually CHANGES build_fn's output enough that attempt 2's validator now PASSES.
- **Why it's a corner cut:** The whole point of Loop B is that override→regen→pass. If `widen_variance` had a sign bug (e.g., divided sigma instead of multiplying), the existing test would pass because it's testing only override-dict accumulation, not the closed loop.
- **Fix:** Add `test_widen_variance_actually_heals_ks_failure_on_retry` with stateful `build_fn`: attempt 1 builds a constant-column DataFrame (KS auto-fails); attempt 2 inspects `overrides["measures"]["revenue"]["sigma"]`, sigma-scales by it, and emits well-fitted `rng.normal(100, 10*sigma_factor, ...)` data; uses *real* `SchemaAwareValidator` (no monkeypatch); asserts `report.all_passed` AND `state["attempt"] == 2`.

#### T1.5 — `declare_orthogonal` propagation to children NEVER positively asserted

- **File:** [`tests/modular/test_sdk_relationships_multi_parent.py`](../tests/modular/test_sdk_relationships_multi_parent.py) lines 398-444.
- **Spec promise:** §2.1.2 — *"If Group A ⊥ Group B, then **all cross-group pairs are automatically independent** — no need to enumerate."* Spec literally enumerates: `hospital ⊥ severity, hospital ⊥ acuity_level, department ⊥ severity, department ⊥ acuity_level, ward ⊥ severity, ward ⊥ acuity_level`.
- **What's there:** The only declare_orthogonal coverage in this file checks **conflict detection** — that declaring orthogonal *after* a multi-parent dependency raises. There is no positive test verifying that, after a successful `declare_orthogonal("entity", "patient")` with `entity = [hospital, department, ward]` and `patient = [severity, acuity_level]`, the generated DataFrame actually exhibits independence at child cross-pairs.
- **Why it's a corner cut:** A latent bug where the engine wires orthogonal at the root level but neglects to thread it through `sample_child_category` would never be caught. The spec's headline guarantee — `O(n²)` elimination — has zero test enforcement.
- **Fix:** New `TestDeclareOrthogonalChildPropagation` in this file: build entity (hospital→department) and patient (severity→acuity_level) groups, declare orthogonal, run `FactTableSimulator(target_rows=3000, seed=42).generate()`, then for each of the 4 cross pairs `{hospital, department} × {severity, acuity_level}` run `scipy.stats.chi2_contingency(pd.crosstab(df[a], df[b]))` and assert `p > 0.05`.

#### T1.6 — `TestAllSixPatternsIntegration` cannot fail; ranking_reversal oracle reuse

- **File:** [`tests/modular/test_engine_patterns.py`](../tests/modular/test_engine_patterns.py) lines 967-973 and 97-112.
- **Spec promise:** §2.6 L3 — quantitative thresholds: outlier `z >= 2.0`, ranking_reversal `rank.corr() < 0`, trend_break `|after-before|/before > 0.15`.
- **What's there (a):** `TestAllSixPatternsIntegration` injects all six pattern types, then asserts only `result is not None and len(result) == len(df)`. Comment at lines 967-973 admits "no value-level assertions."
- **What's there (b):** `TestInjectRankingReversal` (lines 97-112) calls `check_ranking_reversal` from the validator. Both injector and validator compute `rank().corr()` on the same column path — if the injector silently flips ranks for only 2 of 5 entities, the validator would also silently see "corr<0 holds" because they're operating on the same reduction.
- **Why it's a corner cut (a):** The integration test cannot detect a regression where a pattern injector is a no-op; it would still return a DataFrame of the same length. The test reads as "smoke test that nothing crashed."
- **Why it's a corner cut (b):** Oracle reuse — the test essentially says "the validator agrees with itself on what the injector wrote."
- **Fix (a):** Replace the existing integration test with a sequence of per-pattern assertions: for each pattern type, inject in isolation, run the corresponding L3 check from `pattern_checks.py`, assert `passed=True`; then a composition test that confirms a pre-injection L3 check fails on the baseline and a post-injection L3 check passes (so the *pattern*, not chance, is what flipped the verdict).
- **Fix (b):** In `TestInjectRankingReversal`, compute the rank-correlation oracle independently from the injection — e.g., `pre_corr = pre_means[m1].rank().corr(pre_means[m2].rank())` and `post_corr = post_means[m1].rank().corr(post_means[m2].rank())` — then assert `pre_corr > 0` AND `post_corr < 0`. This separates "injector did the rank-flip" from "validator agreed."

#### T1.7 — Sandbox security: zero malicious-payload tests

- **File:** [`tests/modular/test_engine_measures.py`](../tests/modular/test_engine_measures.py) — covers only `test_division_by_zero_raises` and `test_normal_division_works`.
- **Spec promise:** §2.1.1 — *"Formula parsed in isolated sandbox; restricted to basic math ops."* P0-2 in `decisions/blocker_resolutions.md` mandates "Restricted AST-based evaluator."
- **What's there:** `_safe_eval_formula` is implemented at [`engine/measures.py:41-107`](../engine/measures.py#L41) with a strict allow-list (`Expression`, `BinOp` with `+,-,*,/,**`, `UnaryOp(USub)`, `Constant`, `Num`, `Name`). But no test exercises **any** of the rejected paths.
- **Why it's a corner cut:** The full menu of classic AST-based sandbox escapes is unattested:
  - `__import__('os').system('...')` — `Call` node (rejected by walker, untested).
  - `eval('1+1')` — `Call` (untested).
  - `open('/etc/passwd')` — `Call` (untested).
  - `().__class__.__bases__[0].__subclasses__()` — `Attribute` chain + `Subscript` + `Call` (untested).
  - `lambda x: x + 1` — `Lambda` (untested).
  - `(x := 5)` — `NamedExpr` (untested).
  - `[x for x in range(10)]` — `ListComp` (untested).
  - Disallowed binops `//`, `%`, `|`, `&`, `^` (only the allowed five are tested).
  - String constants `'malicious'` (untested — the walker rejects non-numeric `Constant`).
- **Fix:** Add `class TestSafeEvalFormulaSecurityPayloads` in `test_engine_measures.py` — parametrized tests over each malicious payload, asserting `pytest.raises((ValueError, NameError))` with a `match=` against the specific guardrail message (`Disallowed AST node`, `Non-numeric constant`, `Disallowed binary operator`, `Undefined symbol`).

#### T1.8 — Schema metadata contract: keys-only checked, internal structure free-form

- **File:** [`tests/modular/test_metadata_builder.py`](../tests/modular/test_metadata_builder.py).
- **Spec promise:** §2.3 — exact-shape contract. `dimension_groups[g]` has `{"columns", "hierarchy"}` with `hierarchy` an *ordered list* (root first). `orthogonal_groups[i]` is exactly `{"group_a", "group_b", "rationale"}`. `group_dependencies[i].on` is an ordered list. `columns[name]` has type-discriminated descriptor.
- **What's there:** `test_builder_outputs_all_seven_keys` asserts top-level set equality (line 82), but no test verifies internal shape: `dimension_groups[g].hierarchy` could be a `set` or dict and the test would pass.
- **Why it's a corner cut:** The metadata is the *contract* between Phase 2 and Phase 3 (View Extraction reads `hierarchy` order to enumerate drill-downs). A silent migration of `hierarchy` from list to dict would not register.
- **Fix:** Add three tests:
  - `test_dimension_groups_hierarchy_is_ordered_list_root_first` — verify `isinstance(g["hierarchy"], list)` AND `g["hierarchy"][0] == g["root"]` per group.
  - `test_orthogonal_groups_entry_keys_exactly_three` — assert `set(entry.keys()) == {"group_a","group_b","rationale"}` per entry.
  - `test_group_dependencies_on_is_ordered_list_of_strings` — assert `isinstance(dep["on"], list)` AND each element is `str`.

#### T1.9 — SDK declaration safeguards: incomplete coverage of spec §2.1.1

- **File:** [`tests/modular/test_sdk_columns.py`](../tests/modular/test_sdk_columns.py) (208 lines).
- **Spec promise:** §2.1.1 lists 8 safeguards — auto-normalize weights / reject empty values / parent in same group / type-check `dist` / block zero variance / block negative scale / validate date parsing / validate frequency string.
- **What's there (verified during read of test file):**

  | Safeguard | Tested? |
  |-----------|---------|
  | `add_category` empty values rejected | YES |
  | `add_category` weights auto-normalize / sum-to-1 | **NO** |
  | `add_category` parent in same group | partial (verified parent existence, not group identity) |
  | `add_measure` rejects unknown family ("not_a_distribution") | **NO** |
  | `add_measure` rejects sigma=0 | **NO** |
  | `add_temporal` rejects unparseable date | YES |
  | `add_temporal` rejects unsupported freq | **NO** (only "INVALID" — needs parametrize) |

- **Why it's a corner cut:** Each missing safeguard is a path where a malformed LLM script would be silently accepted, defer the failure to runtime in `_sample_stochastic` (worst-case during `generate()`), and waste a retry attempt that should have been a fast declaration-time rejection.
- **Fix:** Add tests `test_add_measure_rejects_unknown_family`, `test_add_measure_rejects_zero_sigma`, `test_add_temporal_rejects_unsupported_freq`, `test_add_category_rejects_weights_summing_to_zero` (or auto-normalizes — match implementation behavior), `test_add_category_rejects_parent_from_different_group`.

#### T1.10 — Realism: no PK protection, no missing_rate=1.0 boundary

- **File:** [`tests/modular/test_realism.py`](../tests/modular/test_realism.py) (219 lines — covers censoring/missing/dirty mechanics).
- **Spec promise:** §2.1.1 — *"`set_realism` protects primary key; enforces rate bounds."*
- **What's there:** Tests verify censoring/missing/dirty mechanics (interval/right/left censoring, ordering across the three injectors). No test verifies PK protection. No test pushes rates to boundaries (0.0, 1.0).
- **Why it's a corner cut:** A regression where `inject_missing_values` no longer skips primary-key columns would corrupt the analytical foundation downstream and would not be caught.
- **Fix:** Add `test_primary_key_never_nulled_by_missing` (build df with categorical root column, set `missing_rate=1.0`, assert `df[root].isna().sum() == 0` while `df[measure].isna().sum() ≈ N`) and `test_missing_rate_one_nulls_all_measure_cells` (boundary).

### HIGH findings

#### T2.1 — Dominance shift validates magnitude, not direction

- **File:** [`tests/modular/test_validation_pattern_checks_dominance.py`](../tests/modular/test_validation_pattern_checks_dominance.py) lines 82-86.
- **Spec promise:** §2.6 L3 — *"rank changed as declared"*. Direction matters: a pattern targeting "Xiehe goes from rank 5 → rank 1" must reject the case where Xiehe stays at rank 5 OR moves rank 5 → rank 1 from below.
- **What's there:** Test asserts `delta=4 > threshold=1` — purely magnitude.
- **Fix:** Add `test_rank_change_in_wrong_direction_fails` — declare pattern expecting upward rank movement, supply data where target moves *down*, assert `not passed`.

#### T2.2 — Convergence: no boundary cases (divergence, threshold)

- **File:** [`tests/modular/test_validation_pattern_checks_convergence.py`](../tests/modular/test_validation_pattern_checks_convergence.py) lines 64-73.
- **Spec promise:** §2.6 L3 — variance reduction must exceed threshold.
- **What's there:** Test only happy case where late_means are identical (reduction ≈ 1.0).
- **Fix:** Add `test_divergence_negative_reduction_fails` (late variance > early variance → reduction < 0 → fail) and `test_threshold_boundary_passes_at_0_3` (exact boundary).

#### T2.3 — Mixture: only mean tested, not component proportions; only one weight config

- **Files:**
  - [`tests/modular/test_engine_mixture.py`](../tests/modular/test_engine_mixture.py) lines 50-63 (TwoComponentMean), 66-89 (ThreeComponentKS).
  - [`tests/modular/test_validation_statistical_mixture.py`](../tests/modular/test_validation_statistical_mixture.py) lines 181-195.
- **Spec promise:** §2.1 — *"weighted-component sampling per `param_model` `{"components":[{"family":"gaussian","weight":w,"params":{...}},...]}`"*. KS test must extract p-value and check `p > 0.05`.
- **What's there:**
  - `TestTwoComponentMean` verifies the weighted mean to ±5% (10k samples). Component *proportion* (which rows landed in which component, vs the declared weight) is never asserted.
  - `TestThreeComponentKS` uses a single weight configuration `(0.4, 0.3, 0.3)`; no parametrized robustness check.
  - Mixture KS test asserts `c.passed`; never extracts the p-value to confirm `p > 0.05` semantic.
- **Fix:** Add `test_two_component_proportions_match_weights_within_ci` (binomial 95% CI on observed mixture-component count vs declared weight). Parametrize the 3-component KS test with at least 2 additional weight configs (`[0.1,0.1,0.8]`, `[0.33,0.33,0.34]`). Add p-value extraction to the mixture KS test.

#### T2.4 — Skeleton multi-parent: no completeness check, no renormalization test

- **File:** [`tests/modular/test_engine_skeleton_multi_parent.py`](../tests/modular/test_engine_skeleton_multi_parent.py).
- **Spec promise:** §2.1.2 — child sampled conditionally on multiple parents; safeguard requires *param completeness* across every parent combination.
- **What's there:** Two-parent and three-parent happy paths tested; deviation tolerance is 0.025 (loose). No test exercises the case where a parent combination's conditional weights are missing.
- **Fix:** Add `test_incomplete_conditional_weights_raises_or_renormalizes` — declare 2×2 parent combinations but only supply weights for 3 of 4; assert either `KeyError`/`InvalidParameterError` at declaration time or graceful renormalization with a warning, matching whichever the implementation actually does.

#### T2.5 — Measure DAG: cycle test uses pre-formed cycle; no diamond

- **File:** [`tests/modular/test_sdk_dag.py`](../tests/modular/test_sdk_dag.py) lines 61-65, 94-186.
- **Spec promise:** §2.1.1 — DAG must be acyclic. Test should reflect realistic incremental construction (3 `add_measure_structural` calls with the third closing a cycle).
- **What's there:** `test_cycle_detection` hands `topological_sort()` a pre-formed cycle dict; the *incremental* path that the SDK actually runs (caller adds measures one at a time, validator detects cycle on the last addition) is not exercised. No diamond test (X→{Y,Z}; Y→W, Z→W).
- **Fix:** Add `test_cycle_detection_incremental_add_measure_structural` (build via three real `add_measure_structural` calls) and `test_diamond_dependency_resolved` (assert topological order respects `index(W) < index(Y), index(Z) < index(X)`).

## Out of scope (with reasons)

These findings surfaced in the audit but are deliberately deferred:

- **`add_correlation` / Gaussian Copula spec drift** — initially flagged as "undocumented drift" but verification found this is **an explicit design decision**, documented in [`docs/deep_dive/stage2_deep_dive_sdk_surface_m1.md`](deep_dive/stage2_deep_dive_sdk_surface_m1.md) and the project README: *"No separate `add_correlation()` API exists. This is a deliberate design decision to keep measure semantics self-contained and verifiable."* No fix required — the audit's expectation was wrong, not the codebase.
- **Self-correction loop end-to-end** — initially flagged as missing but [`tests/test_retry_feedback.py`](../tests/test_retry_feedback.py) (read in full, 229 lines) already covers this rigorously, including `result.attempts == 3` boundary, prior-failure history threading, and `format_error_feedback` hint injection.
- **`max_retries=3` boundary** — covered by `test_retry_feedback.py:139-145`.
- **L3 dominance/convergence/seasonal_anomaly implementation** — these were stubbed in the old `phase_2_new` directory but are now fully implemented in `pipeline/phase_2/validation/pattern_checks.py` (lines 205-470). Test files exist; T2.1 and T2.2 strengthen them.
- **Boundary-precision pattern thresholds** (z=1.99 vs z=2.01; trend Δ=14% vs 16%) — listed by Agent A as MEDIUM. Deferred unless T1/T2 reveal further pattern-validation regressions.
- **Multi-parent deviation 0.10 boundary; oracle CDF boundary; predictor effect parametrizations** — Agent B MEDIUM findings. Deferred for the same reason.
- **Auto-fix `relax_target_r`** — only relevant if `add_correlation` were implemented; with the design decision above, this is moot.

## Execution order

Tier 1 (CRITICAL — close every spec-promise gap with no enforcement):

1. T1.3 chi² seeded — smallest, replaces a known flake.
2. T1.1 validator real-E2E.
3. T1.7 sandbox security payloads.
4. T1.10 realism PK protection.
5. T1.8 metadata internal structure.
6. T1.4 autofix healing roundtrip.
7. T1.2 stage determinism (new file).
8. T1.5 orthogonal child-pair propagation.
9. T1.6 pattern integration replacement + ranking_reversal oracle separation.
10. T1.9 SDK safeguards.

Tier 2 (HIGH — close remaining tolerance/completeness gaps):

11. T2.1 dominance direction.
12. T2.2 convergence boundary.
13. T2.3 mixture proportions + KS p-value.
14. T2.4 skeleton multi-parent completeness.
15. T2.5 DAG diamond + incremental cycle.

## Verification

After each tier, run from the project root with the `chart` conda env:

```bash
/home/dingcheng/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/ -q --tb=short
```

After T1.3 (chi² seeded), run a 50× flake loop to confirm seeding eliminated the random-failure path:

```bash
for i in $(seq 1 50); do
  /home/dingcheng/miniconda3/envs/chart/bin/python -m pytest \
    pipeline/phase_2/tests/modular/test_validation_structural.py::TestCheckOrthogonalIndependence \
    -q 2>&1 | tail -1
done
```

The baseline (pre-changes) is `274 passed, 3 warnings in 1.54s`. Final post-T2 expectation: ~310-330 passed, same 3 warnings, 0 failures, 0 flakes across 50 runs of the chi² test.

## Files touched

**Strengthened (existing):**

- [`tests/modular/test_validation_validator.py`](../tests/modular/test_validation_validator.py) — T1.1
- [`tests/modular/test_validation_structural.py`](../tests/modular/test_validation_structural.py) — T1.3
- [`tests/modular/test_validation_autofix.py`](../tests/modular/test_validation_autofix.py) — T1.4
- [`tests/modular/test_sdk_relationships_multi_parent.py`](../tests/modular/test_sdk_relationships_multi_parent.py) — T1.5
- [`tests/modular/test_engine_patterns.py`](../tests/modular/test_engine_patterns.py) — T1.6
- [`tests/modular/test_engine_measures.py`](../tests/modular/test_engine_measures.py) — T1.7
- [`tests/modular/test_metadata_builder.py`](../tests/modular/test_metadata_builder.py) — T1.8
- [`tests/modular/test_sdk_columns.py`](../tests/modular/test_sdk_columns.py) — T1.9
- [`tests/modular/test_realism.py`](../tests/modular/test_realism.py) — T1.10
- [`tests/modular/test_validation_pattern_checks_dominance.py`](../tests/modular/test_validation_pattern_checks_dominance.py) — T2.1
- [`tests/modular/test_validation_pattern_checks_convergence.py`](../tests/modular/test_validation_pattern_checks_convergence.py) — T2.2
- [`tests/modular/test_engine_mixture.py`](../tests/modular/test_engine_mixture.py) — T2.3
- [`tests/modular/test_validation_statistical_mixture.py`](../tests/modular/test_validation_statistical_mixture.py) — T2.3
- [`tests/modular/test_engine_skeleton_multi_parent.py`](../tests/modular/test_engine_skeleton_multi_parent.py) — T2.4
- [`tests/modular/test_sdk_dag.py`](../tests/modular/test_sdk_dag.py) — T2.5

**New file:**

- [`tests/modular/test_engine_determinism.py`](../tests/modular/test_engine_determinism.py) — T1.2

**No source-code changes.** Spec drift is documented (already documented for `add_correlation` in `docs/deep_dive/`), not patched.
