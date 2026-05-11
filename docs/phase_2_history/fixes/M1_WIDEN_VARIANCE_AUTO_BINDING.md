# M1 — Mixture `widen_variance` Opt-Out Auto-Binding

## Why

### The bug

The mixture opt-out branch in `widen_variance` at
[validation/autofix.py:112-120](../../validation/autofix.py#L112-L120)
fires only when the function is called with a `columns=` kwarg
holding the column registry. The function's docstring (pre-fix)
advised callers to wire `auto_fix` via:

```python
from functools import partial
auto_fix = {"ks_*": partial(widen_variance, columns=meta["columns"]), ...}
```

That advice was structurally unreachable from the natural call chain:

- [pipeline.py:27, 76, 138, 262](../../pipeline.py#L27) accepts user
  `auto_fix` (default `None`) and forwards it through three layers
  to `generate_with_validation`.
- `meta` is BUILT inside `generate_with_validation` at
  [autofix.py:282](../../validation/autofix.py#L282)
  (`df, meta = build_fn(...)`). It does not exist at any
  `pipeline.py` entry point — there is no caller in the pipeline
  who has a `meta` to bind into the partial.
- The natural caller wiring `auto_fix={"ks_*": widen_variance}` (raw
  callable) therefore invokes `widen_variance(check, overrides)` with
  `columns=None`. The mixture opt-out at L112 sees `columns is None`
  and falls through, writing
  `overrides["measures"][col]["sigma"]` for the mixture column.
- `_sample_mixture` at
  [engine/measures.py:440](../../engine/measures.py#L440) then
  silently `del overrides`. The retry loop spins for `max_attempts`
  attempts without changing any mixture parameter.

Net effect: any pipeline using the natural wiring on a script with
mixture columns burns 3 retry attempts on KS failures without any
remediation. Not a crash — a hard-to-diagnose latency/cost sink.

### Root cause

The mixture opt-out was added by IS-1+DS-3 (Step 6 of the stub
workflow). The implementer added the `columns=None` kwarg to
`widen_variance` and the per-family branch at L112-120, but did
NOT update `pipeline.py` or `generate_with_validation`'s dispatch
to ensure the kwarg actually got bound at runtime. The unit tests
([test_validation_autofix.py:71-100](../../tests/modular/test_validation_autofix.py#L71-L100))
verified the function-level contract by passing `columns=` directly,
which masked the integration gap.

The bug was introduced wholesale by the mixture stub — it could not
have existed before mixture sampling was implemented (there was
nothing to opt out from).

### Fix strategy

Three options were considered (recorded in
[POST_STUB_AUDIT_FINDINGS.md](../POST_STUB_AUDIT_FINDINGS.md)):

1. **Bind the partial in `pipeline.py`.** Infeasible — `meta` does
   not exist at any pipeline.py entry; it is built inside the retry
   loop.
2. **Expand the strategy contract** so all strategies receive `meta`
   as a kwarg. Invasive — would break user-supplied custom strategies
   with the existing 2-arg signature.
3. **Inject `columns` at the dispatch site, scoped to widen_variance.**
   Selected. The `meta` variable IS in scope at the dispatch loop.
   A new helper `_call_strategy` introspects each strategy: when the
   underlying callable is `widen_variance` (raw or as an unbound
   `functools.partial`), it injects `columns=meta["columns"]`
   automatically. Other strategies and explicit partials with
   `columns` already bound pass through unchanged.

The fix preserves backward compatibility for every existing call site
and every user-supplied custom strategy. It moves the responsibility
for "knowing about the mixture opt-out" out of pipeline-level wiring
and into the dispatch helper, where `meta` is naturally available.

## Summary of changes

### Modified files

- **[pipeline/phase_2/validation/autofix.py](../../validation/autofix.py)**
  - Added `import functools`.
  - **New `_call_strategy(strategy, check, overrides, meta)` helper**
    above `generate_with_validation`. Auto-injects
    `columns=meta.get("columns")` when the underlying strategy is
    `widen_variance` and the caller did not already bind `columns`
    via `functools.partial`. Custom strategies pass through unchanged.
  - **Dispatch loop at L297-304** (formerly L297-301): replaced the
    direct `strategy(check, overrides)` call with
    `_call_strategy(strategy, check, overrides, meta)`. Added a
    one-line comment explaining the auto-binding intent (M1).
  - **Updated `widen_variance` docstring** to document the
    auto-binding behavior. Removed the "Wire via partial" advice
    (no longer required for the natural use case) and replaced it
    with the explicit-partial-still-respected note.
  - `widen_variance`'s public signature is unchanged.

### Test additions

- **[pipeline/phase_2/tests/modular/test_validation_autofix.py](../../tests/modular/test_validation_autofix.py)**
  - Added `import copy`, `from functools import partial`, `import
    pandas as pd`, `import pytest`. Imported `ValidationReport` from
    types and `generate_with_validation` from autofix.
  - Added `_StubKSFailingValidator` (always reports a single failing
    `ks_revenue` check) and `_make_meta_with_family(family)` helper.
  - Appended **`TestGenerateWithValidationMixtureOptOut`** with three
    integration tests:
    - `test_mixture_optout_fires_through_raw_widen_variance` — the
      load-bearing regression. Pre-fix this test FAILED because
      `widen_variance` wrote `sigma=1.2` to overrides for the mixture
      column on every retry. Post-fix, the dispatch helper injects
      `columns=meta["columns"]`, the opt-out fires, and `overrides`
      stays empty across all 3 attempts.
    - `test_non_mixture_widens_through_raw_widen_variance` —
      sanity guard. Auto-binding does not break the legitimate-widening
      path: gaussian columns still see sigma compound 1.2 → 1.44.
    - `test_explicit_partial_binding_is_respected` — sanity guard.
      When a caller explicitly wires `partial(widen_variance,
      columns=<custom>)`, the dispatch must NOT override their
      binding even if `meta["columns"]` would have produced a
      different decision.
  - The existing `TestWidenVariance` direct-callable suite (6 tests
    at L40-100) is untouched and still passes — `widen_variance`'s
    signature is unchanged.

## Verification

```bash
conda run -n chart pytest \
  pipeline/phase_2/tests/modular/test_validation_autofix.py::TestGenerateWithValidationMixtureOptOut -v
# 3 passed

conda run -n chart pytest pipeline/phase_2/tests/
# 270 passed in 1.00s  (was 267 before; +3 from this fix)
```

TDD trace:

1. **RED.** New test class committed first; the load-bearing
   regression `test_mixture_optout_fires_through_raw_widen_variance`
   failed with: `AssertionError: Mixture opt-out should have fired
   and prevented any sigma override; got {'measures': {'revenue':
   {'sigma': 1.2}}}`. The two sanity guards passed pre-fix (they
   verify paths that already worked).
2. **GREEN.** Added the `_call_strategy` helper, the `import
   functools` line, and updated the dispatch loop. All 3 new tests
   pass. The 6 pre-existing `TestWidenVariance` direct-callable tests
   still pass (no signature change).
3. **Regression sweep.** Full phase-2 suite: 270/270 green; no
   pre-existing test broke.
