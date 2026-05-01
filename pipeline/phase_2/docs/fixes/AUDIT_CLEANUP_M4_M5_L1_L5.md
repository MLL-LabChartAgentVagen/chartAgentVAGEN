# Audit Cleanup — M4, M5, L1, L2, L3, L4, L5

This commit closes the remaining open findings from
[POST_STUB_AUDIT_FINDINGS.md](../POST_STUB_AUDIT_FINDINGS.md). Each
item is small in isolation but they all stem from the same pattern
diagnosed in the audit doc: **small unauthorized additions or small
documentation lags from the stub workflow**. Bundled into one commit
because the individual fixes are too small to ship alone, and they
are all of the same shape (close out audit drift).

## Fixes

### M4 — Mixture validator now accepts `np.integer` weights

**Code change:** [sdk/validation.py L370](../../sdk/validation.py#L370)
- `isinstance(w, (int, float, np.floating))` →
  `isinstance(w, (int, float, np.floating, np.integer))`.

**Test:** New `test_numpy_integer_weight_accepted` in
[test_sdk_validation.py](../../tests/modular/test_sdk_validation.py)
mirrors the existing `test_numpy_float_weight_accepted`. Verifies
`np.int64(1)` and `np.int32(2)` are both accepted as weights without
raising.

**Why:** Prior contract was asymmetric — sampler at
[engine/measures.py:448](../../engine/measures.py#L448)
(`np.array(..., dtype=float)`) accepted `np.integer`, validator
rejected it. LLM emits Python literals so the bug rarely fired in
practice, but the contract drift was real.

### M5 — IS-6 `run_retry_loop` docstring + `_extract_token_usage` unit tests

**Doc change:** [sandbox.py:675-705](../../orchestration/sandbox.py#L675-L705)
`Args:` block now documents `token_budget` and `initial_token_usage`,
and the `Returns:` block documents the `RetryLoopResult.skipped_reason`
field semantics.

**Tests added:** Three unit tests in
[test_retry_loop_token_budget.py](../../tests/modular/test_retry_loop_token_budget.py)
locking in the `_extract_token_usage`'s `except Exception: return None`
fallback contract for three realistic SDK-glitch shapes:
- OpenAI-shape `response.usage` access raises (e.g. partial response).
- OpenAI-shape `response.usage.prompt_tokens` descriptor raises.
- Gemini-native `response.usage_metadata.prompt_token_count` raises.

All three return `None` cleanly so the budget treats the call as 0
tokens (graceful degradation). Pre-existing integration tests covered
the happy paths; this fills the missing exception-path coverage.

### L1 — `check_seasonal_anomaly` switched from `ddof=0` to default `ddof=1`

**Code change:** [pattern_checks.py:489](../../validation/pattern_checks.py#L489)
- `baseline_vals.std(ddof=0)` → `baseline_vals.std()`.

**Why:** `ddof=0` (population std) was inconsistent with the file's
established convention — every other `.std()` call in the same file
([L62, L66](../../validation/pattern_checks.py#L62)) uses the pandas
default of `ddof=1` (unbiased sample std). No rationale for `ddof=0`
was recorded in the IS-4 implementation summary or the decisions doc;
this looked like unintentional drift, not a deliberate choice.

The numeric impact is tiny (factor of `sqrt(n/(n-1))` on the
denominator), but the inconsistency-within-file was the real concern.

**Verification:** All 8 existing
`test_validation_pattern_checks_seasonal_anomaly.py` tests pass with
the change — no fixture relied on the specific ddof=0 value.

### L2 — `GroupDependency` docstring updated for DS-4 contract

**Doc change:** [types.py:189-200](../../types.py#L189-L200) `Attributes:`
block. Removed "Currently restricted to single-column conditioning per
assumption A7 (Sprint 3)"; replaced with a description of both
single- and multi-column conditioning that documents the full
Cartesian coverage requirement at every nesting level.

### L3 — `DS-4.md` deepcopy rationale reworded

**Doc change:** [DS-4.md L97-100](../stub_implementation/DS-4.md#L97-L100).
Old: "previous shape was correct only for depth-2 dicts" (misleading,
implied depth-3 was previously broken when depth-3 didn't exist
pre-DS-4). New: "the previous shallow form was correct for the only
shape that existed pre-DS-4 (depth-2: one parent level + leaf);
deepcopy is required for the new depth ≥ 3 shapes DS-4 enables."

### L4 — `DS-4.md` line span for `_check_dependency_conflict` corrected

**Doc change:** [DS-4.md L45](../stub_implementation/DS-4.md#L45).
`~L385-410` → `L372-395` to match the live source.

### L5 — `stub_blocker_decisions.md` §IS-4 contradiction reconciled

**Doc change:** [stub_blocker_decisions.md §IS-4](../stub_analysis/stub_blocker_decisions.md).
Old wording ("`anomaly_window` is **optional**") contradicted §4.2
Theme 2 ("mandatory"). The IS-4 implementation chose **mandatory at
the SDK gate** + defensive last-10% fallback in the validator (for
out-of-gate use only). The §IS-4 section now matches that choice and
explicitly notes the resolved contradiction. This is the only finding
in this batch that was **pre-existing** (the contradiction lived in
the decisions doc input to the stub workflow, not introduced by any
stub implementation).

## Verification

```bash
conda run -n chart pytest pipeline/phase_2/tests/
# 274 passed in 0.96s  (was 270 before; +4 from M4 [1 test] + M5 [3 tests])
```

## Pattern observation (from the audit doc, reaffirmed by this batch)

Every stub-introduced finding in this batch is either a **small
unauthorized addition** (L1's ddof choice) or a **small documentation
lag** (M5 docstring, L2 stale docstring, L3 misleading framing, L4
line drift). M4 is a contract asymmetry between two co-implemented
files that the unit tests didn't catch because they tested each side
in isolation. L5 alone predates the stub workflow.

For future stub work: the cheapest preventatives would be (a) a
"docstring scan" against the diff before merging (catches L2/L3/L4-style
drift), and (b) a "cross-file isinstance / type-check parity"
checklist (catches M4-style asymmetries).
