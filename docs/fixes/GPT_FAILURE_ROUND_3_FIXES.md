# GPT-5.4 Failure Round 3: Distribution Guards + Formula Hints + `scale` Removal + Single-Root Rule

## Why

Even after the round-2 fix (prompt shrink + structural-formula ZeroDivision guard), [output/log/gpt_failure_3.txt](../output/log/gpt_failure_3.txt) showed GPT-5.4 still exhausting all 5 Loop A retries on a new set of errors:

- Run 1 (University admissions): two-root group; invented `derive=['year']`; `month`/`quarter` in structural formula without being declared; `a <= 0`.
- Run 2 (Book sales): `'month' in formula has no definition`; **`a <= 0` four times in a row** — cryptic enough that GPT couldn't triangulate a fix even with accumulated feedback history.

Four distinct root causes, each converting to an actionable fix:

### 1. Bare numpy distribution errors (`a <= 0`)

[engine/measures.py:342-350](../pipeline/phase_2/engine/measures.py#L342-L350) dispatched directly to `rng.beta(mu, sigma)`, `rng.gamma(shape=mu, scale=sigma)`, `rng.poisson(mu)` etc. When GPT modeled a rate-like measure with a 0-intercept (e.g., `add_measure("return_rate", "beta", {"mu": {"intercept": 0.0}, ...})`), numpy raised `ValueError: a <= 0` with **no column name, family, parameter name, or row index**. The retry feedback received five words; GPT had nothing to act on.

Same failure-mode family as the `ZeroDivisionError` we fixed in round 2 for structural formulas — this is the stochastic sampling equivalent.

### 2. Terse `UndefinedEffectError` for temporal-derive symbols

When GPT wrote `formula="base + 0.2 * month"` without declaring `derive=['month']` on the temporal column, [sdk/validation.py:422](../pipeline/phase_2/sdk/validation.py#L422) returned only `'month' in formula has no definition for '(column not declared)'`. The message correctly identified the problem but didn't state the fix (*"declare it on the temporal column with `add_temporal(..., derive=['month'])`"*). GPT's next retry typically either deleted the formula reference (breaking the structural-dependency requirement) or renamed the symbol and hit another undefined-symbol loop.

### 3. Prompt advertised `scale=` as a knob; SDK silently no-oped it

[orchestration/prompt.py](../pipeline/phase_2/orchestration/prompt.py) documented:
```
sim.add_measure(name, family, param_model, scale=None)
```
but [sdk/columns.py:244-248](../pipeline/phase_2/sdk/columns.py#L244-L248) logged `"'scale' parameter is stored but has no effect in the current implementation."` GPT saw `scale=100.0` as a meaningful scaling knob and tuned it, burning effort on a dead parameter. Same advertising-a-nonfeature class as `censoring=` and the deferred pattern types we removed in round 2.

### 4. No HARD CONSTRAINT telling the LLM each group has exactly one root

The SDK enforces one root per dimension group (via `sdk/groups.py`), but **the prompt never stated this rule**. GPT inferred the API from the one-shot example and got caught by surprise with `Group 'applicant' already has root column 'residency'. Cannot add 'applicant_segment' as a second root.` — correct SDK behavior, but the LLM had no prior signal to avoid it.

## Fix strategy

Four narrow, independent changes. Each closes a feedback-loop gap either by converting a cryptic error into structured actionable context or by deleting an illusory capability from the advertised surface.

## Summary of changes

### Modified files

- **[pipeline/phase_2/engine/measures.py](../pipeline/phase_2/engine/measures.py)**
  - New `_validate_distribution_params(col_name, family, mu, sigma)` helper that raises `InvalidParameterError` with **column name, family, parameter name, first bad row index, and a concrete fix hint** before control reaches the numpy call.
  - Called from `_sample_stochastic` immediately before the family dispatch.
  - Covers only the conditions that actually fire (the existing P3-1 clamp at lines 475-484 already floors `sigma`/`scale`/`rate` to `1e-6`, making those branches dead):
    - `beta`, `gamma`: `mu > 0`
    - `poisson`: `mu >= 0`

- **[pipeline/phase_2/sdk/validation.py](../pipeline/phase_2/sdk/validation.py)**
  - New `TEMPORAL_DERIVE_NAMES = frozenset({"day_of_week", "is_weekend", "month", "quarter"})`.
  - `validate_effects_in_param` appends a hint to the `UndefinedEffectError` message when the undeclared symbol is a known temporal-derive name:
    > `(hint: 'month' is a temporal derive feature — declare it on the temporal column with \`add_temporal(..., derive=['month'])\` before referencing it in a formula)`

- **[pipeline/phase_2/sdk/columns.py](../pipeline/phase_2/sdk/columns.py)** + **[pipeline/phase_2/sdk/simulator.py](../pipeline/phase_2/sdk/simulator.py)**
  - Removed the silently-no-op `scale` kwarg from `add_measure`. Passing it now raises a clean `TypeError: add_measure() got an unexpected keyword argument 'scale'`, which the retry loop can explain.
  - `TODO [M?-NC-scale]` marker preserves the restoration path.

- **[pipeline/phase_2/orchestration/prompt.py](../pipeline/phase_2/orchestration/prompt.py)**
  - Stripped `scale=None` from the `add_measure` signature shown to the LLM.
  - Added **HARD CONSTRAINT #10**:
    > *"Each dimension group has EXACTLY ONE root column (no parent). Additional columns in the same group must use `parent=...` to make them children of the root."*

### New tests (+12 cases)

- **[pipeline/phase_2/tests/modular/test_engine_measures.py](../pipeline/phase_2/tests/modular/test_engine_measures.py)** — new `TestDistributionParamGuards` class with 6 cases: beta with `mu=0`, gamma with `mu=0`, lognormal `sigma=0` silent-clamp regression, poisson with negative `mu`, beta happy path, gaussian untouched.
- **[pipeline/phase_2/tests/modular/test_sdk_validation.py](../pipeline/phase_2/tests/modular/test_sdk_validation.py)** — new `TestUndefinedEffectHints` class with 5 cases (parametrized over `month`/`quarter`/`day_of_week`/`is_weekend` — each gets the hint — plus one negative case for unknown symbols that should NOT get the hint).
- **[pipeline/phase_2/tests/modular/test_sdk_columns.py](../pipeline/phase_2/tests/modular/test_sdk_columns.py)** — rewrote existing `test_add_stochastic_measure` to drop the removed `scale` arg; added a new `test_add_measure_rejects_scale_kwarg` asserting the `TypeError`.

### Behavioral diff visible to the LLM

Before:
```
ERROR: a <= 0
ERROR: 'month' in formula has no definition for '(column not declared)'.
WARNING: add_measure: 'scale' parameter (100.0000) for 'return_rate' is stored
         but has no effect in the current implementation.
ERROR: Group 'applicant' already has root column 'residency'. Cannot add
       'applicant_segment' as a second root.
```

After (for the same degenerate scripts):
```
ERROR: InvalidParameterError: Parameter 'mu' has invalid value 0.0: Measure
       'return_rate' (family='beta'): parameter 'mu' must be > 0 for all rows,
       got 0.0 at row 0. Raise the intercept or effect values so every row has
       a positive mu.
ERROR: UndefinedEffectError: 'month' in formula has no definition for
       '(column not declared) (hint: 'month' is a temporal derive feature —
       declare it on the temporal column with `add_temporal(..., derive=['month'])`
       before referencing it in a formula)'.
(no warning — `scale` kwarg is gone; if passed:)
ERROR: TypeError: FactTableSimulator.add_measure() got an unexpected keyword
       argument 'scale'
(and the prompt itself now states HARD CONSTRAINT #10 up front, so the
 two-roots-per-group path shouldn't be taken in the first place.)
```

Every message now points the LLM at a specific, fixable action.

## Verification

```bash
source /home/dingcheng/miniconda3/etc/profile.d/conda.sh && conda activate chart
cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN

# Unit tests
pytest pipeline/phase_2/tests -v                       # → 85 passed (was 73, +12 new)

# Prompt truthfulness
python -c "
from pipeline.phase_2.orchestration.prompt import SYSTEM_PROMPT_TEMPLATE
for f in ('seasonal_anomaly','ranking_reversal','dominance_shift','convergence','censoring'):
    assert f not in SYSTEM_PROMPT_TEMPLATE
assert 'scale=None' not in SYSTEM_PROMPT_TEMPLATE
assert 'EXACTLY ONE root column' in SYSTEM_PROMPT_TEMPLATE
print('OK')
"

# Beta with mu=0 → structured error
python -c "
import numpy as np
from pipeline.phase_2.engine.measures import _sample_stochastic
from pipeline.phase_2.exceptions import InvalidParameterError
col_meta = {'type':'measure','measure_type':'stochastic','family':'beta',
            'param_model':{'mu':{'intercept':0.0},'sigma':{'intercept':2.0}}}
try:
    _sample_stochastic('accept_rate', col_meta,
                       {'_dummy': np.arange(3)}, np.random.default_rng(0))
except InvalidParameterError as e:
    assert 'accept_rate' in str(e) and 'beta' in str(e) and 'mu' in str(e)
    print('OK')
"

# Temporal-derive hint
python -c "
from pipeline.phase_2.sdk.validation import validate_effects_in_param
from pipeline.phase_2.exceptions import UndefinedEffectError
try:
    validate_effects_in_param('m','mu',{'month':{'x':1.0}},columns={})
except UndefinedEffectError as e:
    assert 'derive' in str(e) and 'add_temporal' in str(e)
    print('OK')
"

# scale= rejected at add_measure
python -c "
from pipeline.phase_2.sdk.simulator import FactTableSimulator
sim = FactTableSimulator(target_rows=50)
sim.add_category('g',['a','b'],[0.5,0.5],'grp')
try:
    sim.add_measure('m','gaussian',{'mu':{'intercept':0},'sigma':{'intercept':1}},scale=100.0)
except TypeError as e:
    assert 'scale' in str(e); print('OK')
"

# Gemini E2E regression
python -m pipeline.agpds_generate --provider gemini --count 1 --category 1
```

All gates pass: **85 pytest cases, 4 smoke checks, Gemini E2E regression produces valid artifacts**.

## Restoration path (when the deferred features land)

Each change pins a `TODO` marker in-line so restoration is a single grep-and-uncomment:

- **`scale` kwarg** → `TODO [M?-NC-scale]` in [sdk/columns.py](../pipeline/phase_2/sdk/columns.py) + the same marker in [orchestration/prompt.py](../pipeline/phase_2/orchestration/prompt.py). When a scaling implementation lands, re-add the parameter to both files and delete the markers.
- **Dead sigma branches in the distribution guard** → the docstring of `_validate_distribution_params` documents why they were omitted (existing P3-1 clamp). If the clamp is ever removed, restore the branches.
- **Temporal-derive hint** → if new derive features are added to `add_temporal(derive=[...])`, extend `TEMPORAL_DERIVE_NAMES` in [sdk/validation.py](../pipeline/phase_2/sdk/validation.py).

## Out of scope

- **Implementing the `scale` kwarg.** Still deferred; the TODO marker preserves the path.
- **Richer param guards** (uniform `high > low`, gaussian `sigma >= 0` where numpy itself doesn't raise). The guard covers the families the error log shows in practice; extending for correctness-not-symptom is fine but not urgent.
- **Rewriting `UndefinedEffectError` as a structured dataclass.** The existing class is fine; we're only enriching its `missing_value` message string.
- **Teaching group-root rules via one-shot example edits.** HARD CONSTRAINT #10 + the existing `DuplicateGroupRootError` is sufficient; the example's existing structure already follows the rule.
