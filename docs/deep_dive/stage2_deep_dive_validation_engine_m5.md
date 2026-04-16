# Stage 2 Deep Dive: Validation Engine (M5)

## 1. SUMMARY

The Validation Engine is the terminal quality gate of Phase 2, verifying the Master DataFrame against its declared schema metadata at three levels (structural, statistical, pattern) and auto-fixing failures without LLM involvement. Its most complex aspect is L2 statistical validation, which must enumerate all predictor-cell combinations for each stochastic measure and run per-cell KS tests — a process whose reliability is highly sensitive to sample size yet has no adaptive threshold mechanism. The most significant ambiguity is the auto-fix mutation path: the spec defines fix strategies (`widen_variance`, `amplify_magnitude`, `reshuffle_pair`) that mutate "declaration-level parameters," but never specifies where that mutated state lives, how it reaches the next `build_fn` call, or whether `schema_metadata` is rebuilt to reflect the mutations. Confidence that the spec fully specifies this module: **medium** — the three validation layers and the retry loop structure are well-defined, but fix-strategy internals, two pattern validators (`convergence`, `seasonal_anomaly`), the `dominance_shift` verifier, and the soft-failure contract with Phase 3 are all left as gaps.

---

## 2. PHASE A: INTERNAL SECTION ANALYSIS

### Section 2.9 — Three-Layer Validation

#### 2.1 PURPOSE

This section defines the final quality gate of Phase 2: a deterministic validator (`SchemaAwareValidator`) that checks the Master DataFrame produced by the Generation Engine (M2) against the declarations captured in `schema_metadata` (M4). It operates at three increasingly semantic levels — structural integrity, statistical fidelity, and pattern presence — and includes an auto-fix retry loop that adjusts parameters and re-executes generation without any LLM involvement. Its job is to ensure the output triple `(DataFrame, schema_metadata, ValidationReport)` is trustworthy before handing off to Phase 3.

#### 2.2 KEY MECHANISM

The section defines four distinct subsystems.

**L1 — Structural Validation.** A set of deterministic sanity checks comparing the DataFrame's shape against metadata declarations.

- *Row count*: Checks `len(df)` is within 10% of `meta["total_rows"]`. This is a soft tolerance, not exact equality — acknowledging that pattern injection or realism steps might add/remove rows, though the spec doesn't say they do.
- *Categorical cardinality*: For every categorical column, `nunique()` must exactly equal the declared `cardinality`. This catches columns where a rare category was never sampled.
- *Root marginal weights*: For every root categorical column (no parent), the observed frequencies must be within 0.10 absolute deviation of declared weights, checked per-value with `max()` over all values. This is a fairly tight tolerance at small row counts.
- *Measure finiteness*: Every measure column must have no NaN/null and no infinite values. This catches degenerate distribution parameters (e.g., log of zero, division by zero in structural formulas).
- *Orthogonal independence*: For each declared orthogonal group pair, a chi-squared contingency test is run on the root columns of each group. The check passes if `p_val > 0.05`, meaning we fail to reject independence. This is a standard frequentist test but note the direction: a *high* p-value is a pass.
- *DAG acyclicity*: A redundant double-check that the measure DAG order is acyclic. This should have been enforced at declaration time by M1, so this is a defense-in-depth assertion.

**L2 — Statistical Validation.** This layer checks that generated values actually follow their declared distributions.

- *Stochastic measures — KS test per predictor cell*: For each stochastic measure, the validator iterates over all predictor cells (unique combinations of the categorical predictors referenced in `effects`). For each cell, it filters the DataFrame and runs a one-sample Kolmogorov-Smirnov test against the declared family with the expected parameters (intercept + summed effects). Passes if `p_val > 0.05`. This is the most computationally expensive check — the number of cells is the Cartesian product of all predictor cardinalities.
- *Structural measures — residual check*: The validator re-evaluates the declared formula on the DataFrame to get predicted values, then computes residuals. Two sub-checks: (a) the residual mean must be close to zero (within 0.1× the residual std), and (b) the residual std must be within 20% of the declared `noise_sigma`. This validates both the formula computation and the noise injection.
- *Group dependency — conditional transition*: For each declared `group_dependency`, a cross-tabulation normalized by the `on` column is computed and compared against `conditional_weights`. The maximum absolute deviation across all cells must be under 0.10.

**L3 — Pattern Validation.** Each injected pattern is verified by type-specific logic.

- *outlier_entity*: Computes the z-score of the target subset's mean relative to the global mean and std of the column. Passes if `z >= 2.0`. Note this is lower than the injection z-score of 3.0 from the example — the validation threshold is deliberately relaxed.
- *ranking_reversal*: Groups by the first dimension group's root column, computes means of the two metrics, then checks that their rank correlation is negative. This verifies the reversal actually manifests in aggregated data.
- *trend_break*: Splits the data at the declared break point on the temporal column, computes the before/after means, and checks that the relative change exceeds 15%. Again, a relaxed threshold compared to the injection magnitude.
- *dominance_shift*: Delegates to a `_verify_dominance_change()` method whose internals are not specified — it is a black box in the spec.

**Auto-Fix Loop.** The `generate_with_validation()` wrapper orchestrates retries.

- A dispatch table `AUTO_FIX` maps check-name patterns (with glob wildcards) to fix strategies: `widen_variance` for KS failures, `amplify_magnitude` for outlier/trend failures, `reshuffle_pair` for orthogonality violations.
- On each attempt, the seed is offset (`seed=42 + attempt`), producing a different random realization. Fixes mutate declaration-level parameters before re-generation.
- Maximum 3 retries. If all fail, the last DataFrame and report are returned as a "soft failure" — not an exception, just a report with `all_passed = False`.

#### 2.3 INTERNAL DEPENDENCIES

Section 2.9 is the only section in M5, so there are no intra-module section dependencies. However, the three layers are internally ordered: L1 checks are preconditions for L2 (if cardinality is wrong or values are non-finite, KS tests are meaningless), and L2 is a precondition for L3 (if the underlying distributions are wrong, pattern checks are unreliable). The spec does not explicitly state this ordering or whether validation short-circuits on L1 failure.

#### 2.4 CONSTRAINTS & INVARIANTS

**Explicit constraints:**

- Row count must be within 10% of `total_rows`.
- Categorical cardinality must exactly match declared cardinality.
- Root marginal weight deviation must be < 0.10 (absolute, per-value max).
- All measure values must be finite and non-null.
- Orthogonal root pairs must pass chi-squared at p > 0.05.
- Measure DAG must be acyclic.
- KS test p-value > 0.05 for each stochastic measure per predictor cell.
- Structural residual mean < 0.1 × residual std.
- Structural residual std within 20% of declared `noise_sigma`.
- Group dependency conditional deviation < 0.10.
- Outlier z-score ≥ 2.0.
- Trend break relative change > 15%.
- Ranking reversal requires negative rank correlation.
- Auto-fix loop: max 3 retries, seed offset per attempt.

**Implicit constraints:**

- L1 should logically precede L2/L3 (non-finite values would crash KS tests), but no short-circuit behavior is specified.
- The `match_strategy` function must handle glob matching against check names, but its implementation is unspecified.
- Fix strategies (`widen_variance`, `amplify_magnitude`, `reshuffle_pair`) must mutate the declaration store or parameters in a way that persists into the next `build_fn` call — the mechanism for this mutation is not defined.
- The `eval_formula` function used in L2 structural checks must parse the same formula syntax that M2's engine uses — consistency is assumed but not enforced.
- The `_get_measure_spec` and `iter_predictor_cells` methods must enumerate all unique predictor combinations, but their enumeration strategy is unspecified.
- The `convergence` and `seasonal_anomaly` pattern types (listed in §2.1.2) have no L3 validation logic defined.
- The validator assumes the `meta` dict is well-formed. There is no validation of the metadata itself.

#### 2.5 EDGE CASES

**Small sample sizes per predictor cell.** If a stochastic measure has effects from two predictors with cardinalities 5 and 3, that's 15 cells. With `target_rows=200`, that's ~13 rows per cell on average. KS tests with n=13 have very low statistical power — they'll almost always pass (high p-value) even if the distribution is wrong. Conversely, with `target_rows=3000`, they might spuriously fail for slight deviations. The spec does not adjust thresholds or test selection by sample size.

**Marginal weight tolerance at low row counts.** With 200 rows and 5 categories, the expected count for a 0.15-weight category is 30. Binomial standard deviation is ~5, so a ±0.10 absolute tolerance could be violated by normal sampling variance alone. The auto-fix `reshuffle_pair` wouldn't help here since this is a marginal check, not a pairwise independence check.

**Realism injection interaction.** If `set_realism(missing_rate=0.1, ...)` is active, the measure finiteness check (`notna().all()`) will fail by design — missing values are intentionally injected. The spec does not indicate whether L1 checks run before or after realism injection, or whether the finiteness check is conditional on realism settings.

**Empty target subset for patterns.** If `inject_pattern("outlier_entity", target="hospital == 'Xiehe' & severity == 'Severe'", ...)` matches zero rows (possible at low row counts with rare categories), the z-score computation would divide by zero or operate on an empty series. No guard is specified.

**Multiple fix strategies for the same check.** The `AUTO_FIX` dispatch uses glob patterns (`"ks_*"`, `"outlier_*"`). If a check name matches multiple patterns, the selection behavior is undefined.

**Cumulative fix interference.** Multiple failing checks may trigger conflicting fixes — e.g., `widen_variance` for a KS failure on `wait_minutes` might simultaneously weaken the outlier signal that `amplify_magnitude` is trying to strengthen on the same column. The spec applies fixes independently with no conflict resolution.

**Soft failure semantics.** After 3 retries, the function returns the last `(df, report)` with failures still present. The spec does not define whether Phase 3 should proceed, skip, or degrade gracefully on a soft failure. The stage 2 overview says M5's interface out is a "validated" triple, which implies success, but the code path allows failure.

**`dominance_shift` validation.** The `_verify_dominance_change` method is referenced but never defined. This is a spec gap — there is no way to verify the intended behavior.

**`convergence` and `seasonal_anomaly` patterns.** These are declared as valid pattern types in §2.1.2 but have no corresponding L3 validation branch. Injecting these patterns would produce no validation check — they'd silently pass.

**Ranking reversal — hardcoded group selection.** The L3 code for `ranking_reversal` selects the root column of the *first* dimension group (`list(meta["dimension_groups"].keys())[0]`). This is fragile — dict ordering is insertion-ordered in Python 3.7+, but the "first" group may not be the semantically relevant one. The pattern declaration doesn't specify which group to use for ranking.

---

## 3. PHASE B: INTRA-MODULE DATA FLOW

### 3.1 ASCII Data Flow Diagram

```
                         EXTERNAL INPUTS
                    ┌──────────┐  ┌──────────┐
                    │  Master  │  │  schema_  │
                    │DataFrame │  │ metadata  │
                    │  (M2)    │  │  (M4)     │
                    └────┬─────┘  └─────┬─────┘
                         │              │
                         ▼              ▼
               ┌─────────────────────────────────────────────────┐
               │        generate_with_validation() wrapper       │
               │                                                 │
               │  seed = 42 + attempt                            │
               │         │                                       │
               │         ▼                                       │
               │  ┌─────────────┐                                │
               │  │  build_fn() │──── calls M2.generate() ───┐   │
               │  └──────┬──────┘                             │   │
               │         │ df                                 │   │
               │         ▼                                    │   │
               │  ┌──────────────────────┐                    │   │
               │  │  L1: Structural      │                    │   │
               │  │  ─────────────────── │                    │   │
               │  │  • row_count         │                    │   │
               │  │  • cardinality_*     │                    │   │
               │  │  • marginal_*        │                    │   │
               │  │  • finite_*          │                    │   │
               │  │  • orthogonal_*_*    │                    │   │
               │  │  • measure_dag_acyc  │                    │   │
               │  └──────┬───────────────┘                    │   │
               │         │ List[Check]                        │   │
               │         ▼                                    │   │
               │  ┌──────────────────────┐                    │   │
               │  │  L2: Statistical     │                    │   │
               │  │  ─────────────────── │                    │   │
               │  │  • ks_*_*            │                    │   │
               │  │  • structural_*_res… │                    │   │
               │  │  • group_dep_*       │                    │   │
               │  └──────┬───────────────┘                    │   │
               │         │ List[Check]                        │   │
               │         ▼                                    │   │
               │  ┌──────────────────────┐                    │   │
               │  │  L3: Pattern         │                    │   │
               │  │  ─────────────────── │                    │   │
               │  │  • outlier_*         │                    │   │
               │  │  • reversal_*_*      │                    │   │
               │  │  • trend_*           │                    │   │
               │  │  • dominance         │                    │   │
               │  └──────┬───────────────┘                    │   │
               │         │ List[Check]                        │   │
               │         ▼                                    │   │
               │  ┌──────────────────────┐                    │   │
               │  │  Merge all checks    │                    │   │
               │  │  → ValidationReport  │                    │   │
               │  └──────┬───────────────┘                    │   │
               │         │                                    │   │
               │         ▼                                    │   │
               │     report.all_passed?                       │   │
               │      │            │                          │   │
               │     YES           NO                         │   │
               │      │            │                          │   │
               │      │            ▼                          │   │
               │      │     ┌────────────────┐                │   │
               │      │     │  AUTO_FIX      │                │   │
               │      │     │  dispatch      │                │   │
               │      │     │  ────────────  │                │   │
               │      │     │  match_strategy│                │   │
               │      │     │  → mutate decl │                │   │
               │      │     └───────┬────────┘                │   │
               │      │             │ mutated params          │   │
               │      │             │                         │   │
               │      │             └─────────────────────────┘   │
               │      │                  Loop B (max 3)           │
               │      ▼                                           │
               │   RETURN (df, schema_metadata, ValidationReport) │
               └──────────────────────────────────────────────────┘
                         │
                         ▼
                      PHASE 3
```

### 3.2 Internal State

**Per-pass state (rebuilt each attempt):**

- `df` — the Master DataFrame, freshly generated from `build_fn(seed=42+attempt)`. Discarded and regenerated on retry.
- `checks` — a growing list of `Check` objects (name, passed, detail) produced by L1, L2, and L3 in sequence. These are merged into a single `ValidationReport` at the end of the pass.

**Cross-attempt state (persists across retries):**

- `attempt` counter — integer from 0 to `max_retries - 1`.
- **Mutated declaration parameters** — the most critical piece of cross-attempt state. When `AUTO_FIX` strategies fire, they modify the parameters that `build_fn` will use on the next call. The spec says strategies like `widen_variance(c, factor=1.2)` and `amplify_magnitude(c, factor=1.3)` adjust declaration-level parameters, but never specifies *where* that mutated state lives. It could be the declaration store itself (shared with M1/M4) or a local copy. This is a significant ambiguity.
- The `meta` dict — passed in and used read-only by the validator. It is not clear whether `meta` is rebuilt on each retry (if M4 re-reads the now-mutated declarations) or remains static. The stage 1 module map says metadata is "built once from declaration store," suggesting it is static, which creates a consistency risk if auto-fix mutates declarations.

**Terminal state:**

- The final `(df, report)` tuple from the last attempt, whether all checks passed or not.

### 3.3 Ordering Constraints

**Explicitly stated:**

- The auto-fix loop structure is explicit: generate → validate → fix → re-generate, up to 3 times.
- L1, L2, L3 are presented in that order and numbered accordingly.

**Implied but not stated:**

- **L1 must complete before L2.** L2's KS tests will crash or produce meaningless results if measure values contain NaN/infinity (which L1's finiteness check catches). Similarly, if cardinality is wrong, the predictor-cell enumeration in L2 may reference categories that don't exist in the data.
- **L2 should complete before L3.** Pattern validation (L3) checks for statistical anomalies layered on top of the base distribution. If the base distribution itself is wrong (L2 failure), pattern checks are unreliable — a trend break might appear to pass simply because the underlying distribution was shifted, not because the pattern was properly injected.
- **No short-circuit is specified.** The spec does not say whether validation halts on first L1 failure or runs all three layers unconditionally. Running all layers is useful for collecting all failures for the auto-fix dispatch, but it risks crashes if L1 preconditions are violated. The auto-fix loop implicitly assumes all failures are collected (it iterates `report.failures`), suggesting all layers always run.
- **Fix application order is unspecified.** When multiple checks fail, the spec iterates `report.failures` and applies fixes sequentially. The order of this iteration (and therefore which fix runs first) could matter if fixes interact — e.g., widening variance on a measure before amplifying an outlier on the same measure versus the reverse.
- **Meta dict rebuild timing.** If auto-fix mutates declaration parameters (e.g., noise sigma), the `meta` dict passed to the validator should reflect these changes for L2 structural residual checks. But the calling convention `generate_with_validation(build_fn, meta, ...)` passes `meta` once. Either `meta` is rebuilt inside the loop (not shown in code) or validation runs against stale metadata after fixes.

### 3.4 Cross-Check Against INTERFACE OUT (Stage 2 Overview)

The overview states M5's interface out as:

> "Final validated `(DataFrame, schema_metadata, ValidationReport)` triple — the terminal output of Phase 2, handed to Phase 3."

**MISMATCH 1 — Output arity.** The `generate_with_validation()` code returns `(df, report)` — a pair, not a triple. The `schema_metadata` is an input to the validator, not included in its return value. The metadata must be bundled at a higher call site, or the return signature needs to be `(df, meta, report)`.

**MISMATCH 2 — "Validated" semantics.** The overview says "final validated" which implies all checks passed. But the code path allows soft failure — after 3 retries, it returns the last `(df, report)` regardless of pass/fail status. The overview does not acknowledge this soft-failure path.

**Consistent — Auto-fix → M2 feedback path.** The stage 1 module map describes Loop B as adjusting numeric parameters and re-running `generate()` with a new seed offset. The code confirms this via `build_fn(seed=42+attempt)`. However, the mechanism by which fix strategies propagate their mutations into the next `build_fn` call is not defined in §2.9.

**Consistent — Consumed inputs.** M5 consumes the Master DataFrame from M2 and `schema_metadata` from M4, as the overview states.

**Consistent — ValidationReport structure.** The stage 1 module map describes it as "List of `Check` objects (name, passed, detail)." The code matches, with the addition of `all_passed` and `failures` on the report object.
