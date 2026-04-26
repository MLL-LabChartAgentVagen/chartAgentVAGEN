# GPT-5.4 Failure Round 4: Yearly-Grain Idiom + Strict `param_model` Key Schema + Targeted Hints

## Why

[output/log/gpt_failure_DEBUG.txt](../../../../output/log/gpt_failure_DEBUG.txt) showed both Stage 1 generations exhausting all 5 Loop A retries — `Stage 1 complete: 0/2 generations saved.` The runs were on category 3 (Education & Academia) with two yearly-grain scenarios (UCLA Admissions 2019–2024, a yearly-census scenario). Each run hit the same two failure classes in lockstep, which is the signature of an SDK contract gap rather than LLM noise.

### 1. Yearly temporal grain has no idiom in the prompt

[pipeline/phase_2/sdk/columns.py:162-175](../../sdk/columns.py#L162-L175) rejects `derive=['year']` (whitelist is `{day_of_week, is_weekend, month, quarter}`) and `freq='YS'` (whitelist excludes year-start). Neither limit is documented in the system prompt — the `add_temporal` line only listed `D / W-MON..W-SUN / MS`. With nowhere else to model an annual cycle, GPT cycled through:

| Attempt | Symptom |
|---|---|
| 1 | `ValueError: Invalid derive features ['year']` |
| 2 | `UndefinedEffectError: 'quarter' in formula has no definition` (LLM dropped `derive=['year']` and reached for `quarter` instead — but at yearly grain there's nothing to derive) |
| 3 | `UndefinedEffectError: 'month' in formula has no definition` (same maneuver, different symbol) |

The retry feedback was correct but the LLM had no way to escape the trap because the prompt offered no alternative for yearly data.

### 2. Beta `param_model` silently swallows wrong keys

[pipeline/phase_2/sdk/validation.py:42-45](../../sdk/validation.py#L42-L45) only enforced required keys for `gaussian` and `lognormal`. Other families validated the *structure* of each key but never the *names*. The Beta sampler at [engine/measures.py:380-394](../../engine/measures.py#L380-L394) reads only `mu`/`sigma` (with defaults `0`/`1`), so when the LLM provided the canonical-statistics `{"alpha": ..., "beta": ...}` (no Beta example exists in the prompt), both keys were silently dropped, `mu` defaulted to `0.0`, and the round-3 distribution guard fired:

> `InvalidParameterError: Parameter 'mu' has invalid value 0.0: Measure 'acceptance_rate' (family='beta'): parameter 'mu' must be > 0 for all rows, got 0.0 at row 0. Raise the intercept or effect values so every row has a positive mu.`

The hint says *"raise the intercept"* — useless when the real fix is *"rename the keys"*. Same advertising-a-nonfeature failure-mode class as `scale=` and `censoring=` (round 3): the SDK accepts something that has no effect.

### Independence from documented stubs

These two gaps are not covered by the 10 entries in [pipeline/phase_2/docs/remaining_gaps.md](../remaining_gaps.md). The closest tangential overlap is IS-5 (`scale` removal) — same category of bug (silent acceptance of an unknown identifier), different surface.

## Conceptual fix

Three independent threads, each closing a different feedback-loop gap:

1. **Teach the LLM the missing idiom up front** — for cases where the SDK genuinely cannot model the requested grain (yearly), the prompt must state the alternative *before* the LLM attempts the unsupported pattern. Static prompt guidance beats post-hoc retry feedback because the retry happens after token spend.
2. **Convert silent acceptance into a loud failure at declaration time** — extending `VALIDATED_PARAM_KEYS` to every non-stubbed family and adding an unknown-key check turns *"alpha was silently ignored, mu defaulted to 0.0, sampler crashed"* into *"alpha is not a recognized key for family 'beta'; expected mu, sigma."* The error now names the actual fix instead of describing a downstream symptom. Matches the round-3 IS-5 fail-loud philosophy.
3. **Inject targeted corrective hints for residual idiom mismatches** — when the LLM ignores the prompt or learns something contradictory from prior knowledge, the sandbox formatter pattern-matches the exception message and surfaces a concrete remediation. Scoped narrowly so broad predicates can't mask real diagnostic signal.

The first thread alone reduces token spend; the second alone reduces retry-loop dead-ends; the third alone catches stragglers. All three together produce 2/2 saved on the same scenario class that previously saved 0/2.

## Summary of changes

### Modified files

- **[pipeline/phase_2/orchestration/prompt.py](../../orchestration/prompt.py)** — three insertions in `_SYSTEM_PROMPT_TEMPLATE`:
  - Documented the supported `derive` features and noted that `'year'` and `freq='YS'` are unsupported.
  - Added a per-family `param_model` key reference under `add_measure`, explicitly stating Beta uses `mu`/`sigma` (NumPy α/β shape parameters), not `alpha`/`beta`.
  - Added a `YEARLY-GRAIN HANDLING` block recommending `add_category("year", values=[...], group="calendar")` (NOT `group="time"` — that name is reserved for `add_temporal` columns) and noting that `trend_break` patterns require an actual temporal column, so yearly-categorical data should use two `outlier_entity` patterns.

- **[pipeline/phase_2/sdk/validation.py](../../sdk/validation.py)** — `param_model` key contract:
  - Extended `VALIDATED_PARAM_KEYS` from `{gaussian, lognormal}` to every non-stubbed family. Beta/gamma/uniform → `{mu, sigma}`; poisson/exponential → `{mu}`. Mixture is intentionally absent (IS-1).
  - Added an unknown-key check inside `validate_param_model`. The unknown-key check fires *before* the missing-required check so that a misnamed-key case like `{"alpha","beta"}` produces *"alpha not recognized; expected mu, sigma"* rather than *"mu and sigma missing"* — the former is more actionable because it tells the LLM to drop the bad keys, not just add new ones.
  - Reuses the existing `InvalidParameterError` from [pipeline/phase_2/exceptions.py:134](../../exceptions.py#L134); no new exception class.

- **[pipeline/phase_2/orchestration/sandbox.py](../../orchestration/sandbox.py)** — targeted hint section in `format_error_feedback`:
  - New module-level `_TARGETED_HINTS: list[tuple[predicate, hint_text]]` with three entries: `derive=['year']` rejection, `freq='YS'` rejection, and `'time' is reserved` group-name rejection. All three point to the categorical-year idiom or the alternative group name.
  - `hint_section` is matched once per call (first hit wins) and inserted between the `=== TRACEBACK ===` and `=== INSTRUCTION ===` blocks so the LLM sees it just before the action prompt.
  - Backward-compatible: when no predicate matches, `hint_section` is empty and the feedback string layout is unchanged.

### New tests (+11 cases)

- **[pipeline/phase_2/tests/modular/test_sdk_validation.py](../../tests/modular/test_sdk_validation.py)** — new `TestValidateParamModelKeySchema` class with 7 cases:
  - Beta with `{"alpha", "beta"}` raises and the message names `alpha`, `beta` (the family), `mu`, `sigma`.
  - Beta with scalar `{"mu", "sigma"}` accepted.
  - Beta with intercept+effects `{"mu", "sigma"}` accepted.
  - Poisson with `{"mu", "sigma"}` raises (sigma not in poisson's allowed set).
  - Exponential with `{"mu", "sigma"}` raises (same).
  - Gaussian with extra key `{"mu", "sigma", "rate"}` raises (back-compat: pre-existing schema also gains unknown-key rejection).
  - Mixture with `{"components": [...]}` does NOT raise (intentionally absent from `VALIDATED_PARAM_KEYS` until IS-1 lands).

- **[pipeline/phase_2/tests/test_retry_feedback.py](../../tests/test_retry_feedback.py)** — 4 new cases for the HINT section:
  - `derive=['year']` error gets a HINT containing `add_category('year'`, ordered above the INSTRUCTION block.
  - `freq='YS'` error gets the same HINT.
  - `'time' is reserved` error gets a HINT mentioning `calendar` and `reserved`.
  - Generic `RuntimeError` does NOT get a HINT section (negative test — predicates must stay scoped).

### Behavioral diff visible to the LLM

Before:
```
ERROR: ValueError: Invalid derive features ['year'] for column 'application_year'.
       Supported: ['day_of_week', 'is_weekend', 'month', 'quarter']

(after retry pivots away from year)
ERROR: UndefinedEffectError: 'quarter' in formula has no definition for ...

(after retry pivots away from quarter)
ERROR: InvalidParameterError: Parameter 'mu' has invalid value 0.0:
       Measure 'acceptance_rate' (family='beta') ... got 0.0 at row 0.
       Raise the intercept or effect values so every row has a positive mu.
```

After:
```
(prompt now contains, before any LLM call:)
  YEARLY-GRAIN HANDLING:
  For yearly data ... declare year as a categorical column under a NEW group
  (NOT 'time' — that name is reserved for add_temporal columns):
    sim.add_category("year", values=[2019, ...], weights=[...], group="calendar")
  ...
  add_measure ... param_model keys per family ...
    gaussian / lognormal / gamma / beta / uniform → {"mu": ..., "sigma": ...}
    NOTE: Beta uses mu/sigma (NumPy α/β shape params), NOT alpha/beta.

(if the LLM still uses alpha/beta for Beta:)
ERROR: InvalidParameterError: Parameter 'alpha' has invalid value 0.0:
       unrecognized param key 'alpha' for family 'beta'.
       Expected keys: ['mu', 'sigma'].
       Common confusion: Beta uses mu/sigma, not alpha/beta.

(if the LLM uses derive=['year'] anyway:)
ERROR: ValueError: Invalid derive features ['year'] ...

=== HINT ===
HINT: For yearly-grain data, do NOT call add_temporal. The SDK does not
support freq='YS' or derive=['year']. Declare year as a categorical column
instead: add_category('year', values=[2019, 2020, ...], group='time').
Reference 'year' in measure effects like any other categorical.

=== INSTRUCTION ===
The script above raised an error during sandbox execution. ...
```

Each layer (prompt → strict validator → targeted hint) closes a different escape route.

## Verification

```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate chart
cd /home/dingcheng/projects/chartAgentVAGEN

# Unit tests
pytest pipeline/phase_2/tests/ -q
# → 96 passed (was 85 in round 3, +11 new)

# Strict-key validation correctness
python -c "
from pipeline.phase_2.sdk.validation import validate_param_model, VALIDATED_PARAM_KEYS
assert set(VALIDATED_PARAM_KEYS) == {'gaussian','lognormal','gamma','beta','uniform','poisson','exponential'}
try:
    validate_param_model('m', 'beta', {'alpha': 1.0, 'beta': 1.0}, {})
    print('FAIL'); raise SystemExit(1)
except Exception as e:
    assert 'alpha' in str(e) and 'mu' in str(e) and 'sigma' in str(e)
print('OK')
"

# Prompt truthfulness
python -c "
from pipeline.phase_2.orchestration.prompt import _SYSTEM_PROMPT_TEMPLATE as P
assert 'YEARLY-GRAIN HANDLING' in P
assert \"group='time'\" not in P  # we recommend 'calendar'
assert 'mu/sigma' in P and 'alpha/beta' in P
assert \"derive ⊆ {'day_of_week', 'is_weekend', 'month', 'quarter'}\" in P
print('OK')
"

# End-to-end smoke test
python -m pipeline.agpds_generate --provider openai --category 3 --count 2 \
    --output-dir ./output/agpds --batch-name smoke-test-fixes-v2
# → Stage 1 complete: 2/2 generations saved.
#   (was 0/2 in gpt_failure_DEBUG.txt)
```

The two generations in the v2 smoke test landed on retry #3 and retry #5 — both within the 5-retry budget. Pre-fix, the same scenario class exhausted all 5 retries on every run.

## Out of scope (intentionally NOT included)

- Adding `'year'` to `TEMPORAL_DERIVE_WHITELIST` — would require new derivation logic in the engine and changes the `time` group semantics; the categorical-year idiom is sufficient.
- Adding `'YS'` to `valid_freqs` — same reason.
- Aliasing `alpha`/`beta` → `mu`/`sigma` in the Beta sampler — rejected per the round-3 fail-loud philosophy. Silent aliasing trains the LLM to keep using the wrong names.
- New `UnknownParameterKeyError` exception class — reusing `InvalidParameterError` keeps the diff small and matches existing call patterns.
