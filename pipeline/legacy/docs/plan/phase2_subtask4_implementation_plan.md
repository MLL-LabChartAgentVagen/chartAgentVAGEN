# Subtask 4: Three-Layer Validation + Auto-Fix

## Current State

[validators.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py) already exists (425 lines) with functional L1/L2/L3 validation. However, 5 gaps remain vs. the [phase_2.md §2.6](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/storyline/data_generation/phase_2.md) spec:

| # | Gap | Severity |
|---|-----|----------|
| 1 | **Auto-fix functions are placeholders** — [_relax_target_r](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#354-357), [_widen_variance](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#359-362), [_amplify_magnitude](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#364-367), [_reshuffle_pair](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#369-372) just append text to `check.detail` instead of mutating generation parameters | Critical |
| 2 | **L3 missing 3 pattern types** — [dominance_shift](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/patterns.py#184-221), [convergence](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/patterns.py#223-258), [seasonal_anomaly](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/patterns.py#260-294) have no L3 validation checks | High |
| 3 | **KS test limited to [gaussian](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/distributions.py#87-91) only** — L247 has `if scipy_name in ("norm",)`, skipping lognormal, gamma, beta, uniform, exponential | Medium |
| 4 | **[generate_with_validation()](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#392-425) doesn't use auto-fix results** — it increments seed but never feeds fix suggestions back into the `build_fn` | High |
| 5 | **No integration with [SandboxExecutor](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/sandbox_executor.py#133-324)** — need a combined loop: sandbox retries (execution errors) → then validation retries (statistical failures) | Medium |

> [!IMPORTANT]
> The existing L1/L2/L3 validation logic is **correct and tested** (Test 9 in [test_fact_table_simulator.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/tests/test_fact_table_simulator.py)). This subtask does NOT rewrite the validator — it fills the gaps listed above.

---

## Proposed Changes

### Phase 2 Module

#### [MODIFY] [validators.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py)

**Gap 1: Real auto-fix functions** (replacing placeholder stubs at lines 354–371)

Auto-fix functions now return a `dict` of parameter adjustments that [generate_with_validation()](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#392-425) can apply. The key insight: auto-fix doesn't mutate the DataFrame — it mutates the **SDK declarations** (stored in [SchemaMetadata](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/schema_metadata.py#69-84)) so the next [generate()](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/fact_table_simulator.py#485-520) call produces a better result.

| Fix Function | What It Does |
|-------------|-------------|
| [_relax_target_r](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#354-357) | Moves [target_r](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#354-357) closer to 0 by `step` (e.g., -0.55 → -0.50) |
| [_widen_variance](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#359-362) | Multiplies distribution `sigma`/[scale](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/distributions.py#38-49) by `factor` |
| [_amplify_magnitude](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#364-367) | Increases pattern `z_score`/[magnitude](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#364-367) by `factor` |
| [_reshuffle_pair](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#369-372) | Returns a flag requesting re-shuffle (seed increment handles this) |

Each function returns a `FixAction` dataclass:
```python
@dataclass
class FixAction:
    """Describes a parameter adjustment to apply before the next retry."""
    target_key: str       # path in SchemaMetadata, e.g. "correlations[0].target_r"
    adjustment: str       # human-readable description
    apply: Callable[[dict], dict]  # function that mutates meta dict in-place
```

**Gap 2: L3 validation for missing patterns** (extending [_L3_pattern](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#268-348) at lines 268–347)

| Pattern | Validation Check |
|---------|-----------------|
| [dominance_shift](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/patterns.py#184-221) | Before/after temporal midpoint: dominant entity on [col](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/fact_table_simulator.py#1027-1035) changes |
| [convergence](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/patterns.py#223-258) | Gap between top-2 entity means on [col](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/fact_table_simulator.py#1027-1035) shrinks across temporal bins |
| [seasonal_anomaly](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/patterns.py#260-294) | Target entity's seasonal correlation with overall pattern is negative |

**Gap 3: Extended KS test** (modifying L247)

Expand the `scipy_map` dispatch to properly test [lognormal](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/distributions.py#93-97), [gamma](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/distributions.py#99-103), [beta](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/distributions.py#105-109), [uniform](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/distributions.py#111-119), and [exponential](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/distributions.py#127-131) with correct parameter mapping.

**Gap 4: [generate_with_validation()](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#392-425) applies fixes** (rewriting lines 392–424)

```python
def generate_with_validation(
    build_fn: Callable,
    meta: dict,                  # NEW: mutable metadata dict
    max_retries: int = 3,
    base_seed: int = 42,
) -> tuple[pd.DataFrame, ValidationReport, dict]:
    """
    1. Call build_fn(seed, meta) → (df, meta)
    2. Validate → report
    3. If failed: apply FixActions to meta, increment seed, retry
    4. Return (df, report, final_meta)
    """
```

---

#### [MODIFY] [\_\_init\_\_.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/__init__.py)

Add `FixAction` to exports if it's used externally (minor).

---

#### [NEW] [tests/test_validators.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/tests/test_validators.py)

Dedicated test suite for validator improvements:

| # | Test | Description |
|---|------|-------------|
| 1 | L3 dominance_shift | Verify dominance_shift pattern is detected |
| 2 | L3 convergence | Verify convergence pattern is detected |
| 3 | L3 seasonal_anomaly | Verify seasonal_anomaly pattern is detected |
| 4 | KS test multi-distribution | Verify KS test runs for lognormal, gamma, beta, uniform, exponential |
| 5 | Auto-fix relaxes correlation | Verify [_relax_target_r](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#354-357) actually modifies `meta["correlations"][i]["target_r"]` |
| 6 | Auto-fix amplifies pattern | Verify [_amplify_magnitude](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#364-367) increases pattern params |
| 7 | [generate_with_validation()](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#392-425) converges | A build_fn that initially fails then passes after fix applied |

---

## Verification Plan

### Automated Tests

```bash
conda activate chart
cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline

# New validator tests
python -m phase_2.tests.test_validators

# Existing tests must still pass (regression)
python -m phase_2.tests.test_fact_table_simulator
```

### Regression Check

Test 9 in [test_fact_table_simulator.py](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/tests/test_fact_table_simulator.py) uses [SchemaAwareValidator](file:///home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline/phase_2/validators.py#50-348) — it must continue to pass without modification.
