# Spec Alignment Analysis & Robust Validation Tests

## Background

The user wants to know (1) whether [validators.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py) aligns with the Three-Layer Validation spec in [phase_2.md](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/storyline/data_generation/phase_2.md) §2.6, and (2) robust local tests that exercise every validation check for correctness.

## Spec Alignment Analysis

### Spec source: [phase_2.md §2.6](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/storyline/data_generation/phase_2.md#L353-L486)
### Implementation: [validators.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py)

---

### L1: Structural Validation — Alignment Verdict: ✅ Aligned (with minor differences)

| Spec Requirement | Implementation | Aligned? | Notes |
|---|---|---|---|
| Row count within 10% of `total_rows` | Lines 82–89: `row_diff < 0.1` | ✅ | Implementation uses `.get("total_rows", len(df))` — safe fallback |
| Categorical cardinality matches declaration | Lines 92–108: iterates `columns`, type==`categorical` | ✅ | Adds `exists_` check if column missing — extra robustness vs spec |
| Measure columns: all finite and non-null | Lines 111–132: `finite_` checks | ⚠️ **Partial** | **Spec requires `notna().all()` (zero nulls) AND `isfinite().all()`.** Implementation allows nulls — it `dropna()` first and only checks `isfinite` on non-null values. This is a deliberate relaxation because `set_realism(missing_rate)` injects nulls. |
| Orthogonal group independence (χ² on root pairs) | Lines 134–161: chi-square test | ✅ | Threshold p>0.05 matches spec |

### L2: Statistical Validation — Alignment Verdict: ⚠️ Mostly Aligned (1 tolerance deviation)

| Spec Requirement | Implementation | Aligned? | Notes |
|---|---|---|---|
| Correlation targets: `abs(actual_r - target_r) < 0.15` | Lines 189–194: tolerance is **0.30** | ⚠️ **Relaxed** | Spec says `< 0.15`, implementation uses `< 0.30`. Code comment explains: pattern injection (φ) runs AFTER correlation (ψ) and may modify values. This is a **deliberate design trade-off**, not a bug. |
| Dependency residual: `residual_std < target_std * 0.5` | Lines 196–218 | ✅ | Matches spec |
| KS test: `p > 0.05` | Lines 220–249: threshold is **0.01** | ⚠️ **Relaxed** | Spec says `> 0.05`, implementation uses `> 0.01`. Another deliberate relaxation. |

### L3: Pattern Validation — Alignment Verdict: ⚠️ Partially Aligned (2 missing checks in spec, 3 extra in impl)

| Spec Requirement | Implementation | Aligned? | Notes |
|---|---|---|---|
| `outlier_entity`: z ≥ 2.0 | Lines 266–283 | ✅ | Matches spec |
| `ranking_reversal`: rank_corr < 0 | Lines 285–304 | ✅ | Matches spec |
| `trend_break`: shift > 15% | Lines 306–334 | ✅ | Implementation adds [target](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#490-515) filter support — extra robustness |
| `dominance_shift` | Lines 336–357 | ✅ | Spec says `self._verify_dominance_change()` — impl inlines the logic |
| `convergence` | Lines 359–381 | ⚙️ **Extra** | **Not in spec's L3 code** (spec §2.6 only shows 4 pattern checks). Implementation adds it. |
| `seasonal_anomaly` | Lines 383–412 | ⚙️ **Extra** | **Not in spec's L3 code**. Implementation adds it. |

### Auto-Fix Loop — Alignment Verdict: ✅ Aligned (with enhancements)

| Spec Requirement | Implementation | Aligned? | Notes |
|---|---|---|---|
| Auto-fix strategies: `corr_*`, `ks_*`, `outlier_*`, `trend_*`, `orthogonal_*` | Lines 596–606 | ✅ | Implementation adds `reversal_*`, `dominance_*`, `convergence_*`, `seasonal_*` — extra patterns |
| [generate_with_validation](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#636-680): max_retries, seed increment | Lines 636–679 | ✅ | Implementation is more sophisticated with [_merge_overrides](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#682-702) for accumulating fixes |

---

### Summary of Misalignments

> [!IMPORTANT]
> **None of the misalignments are bugs.** They are deliberate relaxations/enhancements:
> 1. **Correlation tolerance 0.30 vs 0.15** — Because pattern injection (φ) modifies values after correlation injection (ψ)
> 2. **KS threshold 0.01 vs 0.05** — More permissive to avoid false negatives on complex distributions
> 3. **Null tolerance in L1** — Because `set_realism(missing_rate)` intentionally introduces nulls
> 4. **Extra L3 patterns** (`convergence`, `seasonal_anomaly`) — Implementation extends spec to cover all 6 pattern types

> [!NOTE]
> **[phase_3.md](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/storyline/data_generation/phase_3.md) is NOT the validation spec.** Phase 3 covers View Extraction, Dashboard Composition, and QA Generation. The Three-Layer Validation lives in [phase_2.md](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/storyline/data_generation/phase_2.md) §2.6. The user referenced [phase_3.md](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/storyline/data_generation/phase_3.md) but the validation logic belongs to Phase 2.

---

## Proposed Changes

### Test Suite

#### [NEW] [test_validation_spec.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/tests/test_validation_spec.py)

A comprehensive, spec-aligned test suite covering **every validation check** with deterministic synthetic data (no LLM required). Tests use pure `pandas`/`numpy` — no `FactTableSimulator` dependency, so they test the validator in isolation.

**Test categories:**

**L1 Structural (6 tests):**
1. `test_row_count_pass` — exactly at target
2. `test_row_count_fail` — >10% off
3. `test_cardinality_pass` — matches declared
4. `test_cardinality_fail` — mismatch
5. `test_finite_measures_pass` — all finite
6. `test_finite_measures_fail_inf` — infinite values detected
7. `test_orthogonal_pass` — independent categoricals (χ² p>0.05)
8. `test_orthogonal_fail` — correlated categoricals (χ² p<0.05)

**L2 Statistical (6 tests):**
9. `test_correlation_within_tolerance` — actual r within 0.30
10. `test_correlation_outside_tolerance` — actual r outside 0.30
11. `test_dependency_residual_pass` — residual_std < target_std * 0.5
12. `test_dependency_residual_fail` — residual too large
13. `test_ks_pass` — samples from matching distribution
14. `test_ks_fail` — samples from wrong distribution

**L3 Pattern (6 tests):**
15. `test_outlier_entity_detected` — z ≥ 2.0
16. `test_outlier_entity_not_detected` — z < 2.0
17. `test_ranking_reversal_detected` — negative rank correlation
18. `test_trend_break_detected` — >15% shift at break point
19. `test_dominance_shift_detected` — leader changes mid-period
20. `test_convergence_detected` — gap narrows over time

**Auto-Fix (3 tests):**
21. `test_relax_target_r` — [_relax_target_r](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#490-515) mutates meta correctly
22. `test_widen_variance` — [_widen_variance](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#517-539) mutates meta correctly
23. `test_apply_fixes_integration` — [apply_fixes](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#617-634) dispatches to correct strategies

**Edge Cases (2 tests):**
24. `test_empty_dataframe` — validator handles gracefully
25. `test_missing_columns` — missing columns don't crash validator

---

## Verification Plan

### Automated Tests

Run the new test suite from the project root:

```bash
cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN
python -m pipeline.phase_2.tests.test_validation_spec
```

Expected output: All tests pass with `✓` markers, final summary line showing total passed count.

### Existing Test Continuity

Verify existing tests still pass:

```bash
cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN
python -m pipeline.phase_2.tests.test_validators
```

Expected output: `All 8 tests passed! ✓`
