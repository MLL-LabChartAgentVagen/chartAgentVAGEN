# Fix: Structural Measure Residual Validation Ignores Upstream Pattern Dependencies

## Context

When running `pipeline/agpds_runner.py`, Phase 2 validation consistently produces false warnings like:

```
residual_total_watch_hours: noise_sigma=15.0000, residual_std=37.7170, ratio=1.5145 (>= 0.2)
residual_engagement_roi: noise_sigma=0.2000, residual_std=2.4767, ratio=11.3833 (>= 0.2)
```

The residual_std is 2.5x–12x larger than noise_sigma, which should not happen if only Gaussian noise is present.

## Root Cause

The bug is in `check_structural_residuals()` at `/home/dingcheng/projects/implementation/phase_2_new/phase_2/validation/statistical.py:356-366`.

**Pipeline execution order:**
1. **Phase β** — all measures computed from formulas. E.g. `cost = wait_minutes * 12 + surcharge + noise(30)`, using original `wait_minutes` values.
2. **Phase γ** — patterns modify specific columns in the DataFrame. E.g. `outlier_entity` shifts `wait_minutes` for certain rows by adding z_score × std.
3. **Validation** — `check_structural_residuals` reads upstream values from the **post-pattern** DataFrame to compute predictions.

**The mismatch:** When validating `cost`, the validator reads pattern-modified `wait_minutes` from the DataFrame, but `cost` was computed from **pre-pattern** `wait_minutes`. The residual becomes:

```
residual = (wait_minutes_original - wait_minutes_modified) * 12 + noise(30)
```

The pattern-induced `(original - modified) * 12` term dwarfs the declared noise.

**The current pattern exclusion** (line 360) only filters rows where `p["col"] == col_name` — i.e., patterns targeting the column being validated. It does NOT filter rows where patterns modified **upstream formula dependencies**.

## Fix

### Step 1: Add helper `_get_formula_measure_deps` (~line 316 in statistical.py)

Extracts measure column names directly referenced in a structural formula, reusing existing `extract_formula_symbols` from `phase_2/sdk/validation.py:554`.

```python
def _get_formula_measure_deps(formula, col_name, columns_meta) -> set[str]:
    # Parse formula identifiers, filter to measure-type columns in columns_meta
    # Exclude col_name itself
```

### Step 2: Expand pattern exclusion mask (lines 356-366 in statistical.py)

Change from:
```python
if p.get("col") == col_name:
```

To:
```python
formula_deps = _get_formula_measure_deps(formula, col_name, columns_meta)
affected_cols = {col_name} | formula_deps
# ...
if p.get("col") in affected_cols:
```

This excludes rows where patterns modified ANY column the formula directly references.

### Step 3: Update docstring (line 331)

Note that upstream pattern dependencies are now excluded.

### Step 4: Add tests in `tests/modular/test_validation_statistical.py`

- Test upstream-dependency pattern exclusion (pattern on `wait_minutes` excluded when validating `cost = wait_minutes * 12`)
- Test helper function for various cases (measure deps, non-measures, self-exclusion, empty deps)

## Files to Modify

| File | Change |
|------|--------|
| `phase_2/validation/statistical.py` | Add `_get_formula_measure_deps`; modify pattern exclusion in `check_structural_residuals`; update docstring |
| `tests/modular/test_validation_statistical.py` | Add upstream-dependency exclusion test + helper function tests |

## Why Transitive Dependencies Are NOT Needed

If `total_cost` depends on `cost` which depends on `wait_minutes`, and a pattern modifies `wait_minutes`: the DataFrame's `cost` column still holds pre-pattern values (patterns only modify explicitly targeted columns). So reading `cost` from the DataFrame when validating `total_cost` gives correct values. Only **direct** formula references to pattern-modified columns cause the bug.

## Verification

```bash
cd /home/dingcheng/projects/implementation/phase_2_new
python -m pytest tests/modular/test_validation_statistical.py -v
```
