# Prompt Truth + ZeroDivision Guard

## Why

### 1. The prompt was lying to the LLM

The AGPDS system prompt in [pipeline/phase_2/orchestration/prompt.py](../pipeline/phase_2/orchestration/prompt.py) advertised six `PATTERN_TYPES` and a `censoring=None` kwarg on `set_realism()`:

```
PATTERN_TYPES: "outlier_entity", "trend_break", "ranking_reversal",
               "dominance_shift", "convergence", "seasonal_anomaly"
sim.set_realism(missing_rate, dirty_rate, censoring=None)
```

But the engine implemented only **two** of those patterns and **no** censoring. [pipeline/phase_2/engine/patterns.py](../pipeline/phase_2/engine/patterns.py) raises `NotImplementedError("...not yet implemented. See stage3 item M1-NC-6.")` for the other four, and [pipeline/phase_2/engine/realism.py](../pipeline/phase_2/engine/realism.py) raises the same for censoring (`M1-NC-7`).

This silent mismatch was invisible under Gemini-3.1-pro-preview because Gemini copies the one-shot example almost literally and the example only uses `outlier_entity` + `trend_break` with no realism call. It broke spectacularly under GPT-5.4, which treats the documented API as a menu to explore: it would pick `seasonal_anomaly`, add `censoring`, and hit `NotImplementedError` walls. The accumulated-failure feedback loop couldn't help — the LLM was being told *by the system prompt itself* to use features that didn't exist.

Evidence: [output/log/gpt_failire_2.txt](../output/log/gpt_failire_2.txt) shows **3 of 5** retry failures caused by the unimplemented features; a 4th was missing params for `ranking_reversal`.

### 2. A bare `ZeroDivisionError` gave the LLM nothing to fix

The 5th retry failure was `float division by zero` — Python's stock message with no row, no column, no formula text. It came from [engine/measures.py:30](../pipeline/phase_2/engine/measures.py#L30), which maps `ast.Div` to `lambda a, b: a / b` with no guard. When the LLM writes e.g. `formula="profit / revenue"` and some row has `revenue == 0`, the error message that reaches the retry prompt is just `"float division by zero"`. The LLM cannot reliably fix a denominator it cannot locate.

### Fix strategy

Two independent but complementary changes:

1. **Truth-in-advertising**: shrink the prompt and the SDK allowlist to the features the engine actually implements, with `TODO [M1-NC-6]` / `TODO [M1-NC-7]` markers so restoration is trivial when those stage-3 items land.
2. **Structured error on divide-by-zero**: wrap the per-row formula evaluator's call site, catch `ZeroDivisionError`, and re-raise as `InvalidParameterError` carrying the column name, formula text, row index, the list of zero-valued symbols in the context, and a concrete fix hint (`'a / max(b, 1e-6)'`). This message then flows through the existing `format_error_feedback()` path so the LLM sees actionable context on the next retry.

## Summary of changes

### Modified files

- **[pipeline/phase_2/orchestration/prompt.py](../pipeline/phase_2/orchestration/prompt.py)**
  - `set_realism(missing_rate, dirty_rate, censoring=None)` → `set_realism(missing_rate, dirty_rate)`. Preceded by `# TODO [M1-NC-7]` comment.
  - `PATTERN_TYPES` list shrunk from 6 entries to `"outlier_entity", "trend_break"`. Preceded by `# TODO [M1-NC-6]` comment listing the four deferred types.
- **[pipeline/phase_2/sdk/relationships.py](../pipeline/phase_2/sdk/relationships.py)**
  - `VALID_PATTERN_TYPES` shrunk to `frozenset({"outlier_entity", "trend_break"})`.
  - `PATTERN_REQUIRED_PARAMS` dict narrowed to the same two types. A `TODO` comment in-line preserves the old entries verbatim so re-enabling is a single uncomment.
- **[pipeline/phase_2/engine/measures.py](../pipeline/phase_2/engine/measures.py)**
  - Added `from ..exceptions import InvalidParameterError`.
  - Wrapped the per-row `_safe_eval_formula(...)` call in `_eval_structural` with a `try/except ZeroDivisionError` that re-raises as:
    ```python
    InvalidParameterError(
        param_name="formula", value=0.0,
        reason=(
            f"Structural measure '{col_name}': formula '{formula}' "
            f"divided by zero at row {i}. Zero-valued symbols in context: {zero_vars}. "
            f"Guard against zero in your effects or floor the denominator "
            f"(e.g., 'a / max(b, 1e-6)')."
        ),
    ) from None
    ```
  - `from None` suppresses the raw Python exception chain so the sandbox reports the clean structured message.

### New files

- **[pipeline/phase_2/tests/modular/test_engine_measures.py](../pipeline/phase_2/tests/modular/test_engine_measures.py)** — 5 tests:
  - Low-level `_safe_eval_formula` still raises `ZeroDivisionError` at the primitive layer (unchanged contract).
  - Normal division works.
  - Per-row `_eval_structural` converts `ZeroDivisionError` to `InvalidParameterError` with column name, formula, row index, zero-valued symbols, and the hint string.
  - Happy path with non-zero denominators returns correct values.
  - Empty rows returns empty array (guard doesn't break the early-exit path).

### Behavioral diff visible to the LLM

Before:
```
ERROR: Pattern type 'seasonal_anomaly' injection not yet implemented. See stage3 item M1-NC-6.
ERROR: Censoring injection not yet implemented. See stage3 item M1-NC-7.
ERROR: float division by zero
```

After (for the same degenerate scripts):
```
ERROR: Unsupported pattern type 'seasonal_anomaly'. Supported: ['outlier_entity', 'trend_break']
ERROR: set_realism() got an unexpected keyword argument 'censoring'
ERROR: Structural measure 'profit_margin': formula 'profit / revenue' divided by zero at row 1.
       Zero-valued symbols in context: ['revenue']. Guard against zero in your effects or
       floor the denominator (e.g., 'a / max(b, 1e-6)').
```

Each message now points the LLM at a specific, fixable action.

## Verification

```bash
source /home/dingcheng/miniconda3/etc/profile.d/conda.sh && conda activate chart
cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN

# Unit tests
pytest pipeline/phase_2/tests -v                     # → 73 passed (was 68, +5 new)

# Prompt truthfulness
python -c "
from pipeline.phase_2.orchestration.prompt import SYSTEM_PROMPT_TEMPLATE
for f in ('seasonal_anomaly','ranking_reversal','dominance_shift','convergence','censoring'):
    assert f not in SYSTEM_PROMPT_TEMPLATE
print('OK')
"

# SDK allowlist
python -c "
from pipeline.phase_2.sdk.relationships import VALID_PATTERN_TYPES, PATTERN_REQUIRED_PARAMS
assert VALID_PATTERN_TYPES == {'outlier_entity', 'trend_break'}
assert set(PATTERN_REQUIRED_PARAMS.keys()) == {'outlier_entity', 'trend_break'}
print('OK')
"

# Deferred pattern rejected at declaration (not at late injection time)
python -c "
from pipeline.phase_2.sdk.simulator import FactTableSimulator
sim = FactTableSimulator(target_rows=50)
sim.add_category('g', ['a','b'], [0.5,0.5], 'grp')
sim.add_measure('m', 'gaussian', {'mu':{'intercept':0}, 'sigma':{'intercept':1.0}})
try:
    sim.inject_pattern('seasonal_anomaly', target='g==\"a\"', col='m', params={})
except ValueError as e:
    assert 'Unsupported' in str(e)
    print('OK')
"

# End-to-end Gemini regression (must still succeed)
python -m pipeline.agpds_generate --provider gemini --count 1 --category 1
```

All pass: **73 pytest cases, all three smoke checks, Gemini E2E regression produces a valid script and declarations file**.

## Restoration path (when M1-NC-6 / M1-NC-7 land)

Each change is pinned to one of two TODO markers. To restore a deferred feature:

1. Implement the injection / validation logic in `engine/patterns.py` or `engine/realism.py`.
2. Grep for the relevant TODO (`M1-NC-6` or `M1-NC-7`).
3. Add the pattern name back to `VALID_PATTERN_TYPES` and (if needed) `PATTERN_REQUIRED_PARAMS` in `sdk/relationships.py` — the comment preserves the old entries verbatim.
4. Restore the corresponding line in `orchestration/prompt.py`.

No coordination across files beyond those TODO markers is required.

## Out of scope

- **Actually implementing the M1-NC-6 patterns and M1-NC-7 censoring.** Those remain on the stage-3 backlog; this change is the cheap win until they land.
- **Guards for other division-by-zero sites.** The Explore audit confirmed `measures._safe_eval_formula` was the only unguarded path: `patterns.inject_outlier_entity` already raises `DegenerateDistributionError` on `global_std == 0.0`, `measures._sample_stochastic` clamps exponential `mu` to `1e-6`, and `skeleton` weight sums are already rejected at SDK declaration time by `sdk/validation.py::validate_and_normalize_flat_weights` / `validate_and_normalize_dict_weights`.
