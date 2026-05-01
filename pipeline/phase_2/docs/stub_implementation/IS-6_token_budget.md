# IS-6 (token-budget half): Summary of Changes

Implements the **token-budget half** of IS-6 from
[pipeline/phase_2/docs/stub_analysis/stub_gap_analysis.md §IS-6](../stub_analysis/stub_gap_analysis.md)
per the decisions locked in
[stub_blocker_decisions.md §IS-6](../stub_analysis/stub_blocker_decisions.md).

The multi-error feedback half remains deferred pending an A/B test on
LLM efficacy (per the same decisions doc).

## What this unlocks

The §2.7 retry loop now enforces a per-scenario cumulative token
budget. A runaway scenario whose LLM-generated retries balloon
prompt+completion tokens (verbose tracebacks, looping fixes) is
skipped early with a `token_budget_exceeded` reason instead of always
running to `max_retries=3`. Behavior is fully backwards-compatible —
`token_budget=None` (the default) preserves the current loop, and
providers that don't report token counts degrade gracefully (counts as
0, never trips the budget).

**Out of scope (still pending):** multi-error collection / batched
feedback — gated on the empirical A/B test recorded in
[stub_blocker_decisions.md §IS-6](../stub_analysis/stub_blocker_decisions.md).

## Schemas / contracts added

### `TokenUsage` (NamedTuple)

```python
class TokenUsage(NamedTuple):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
```

Per-call token accounting reported by the LLM provider. Fields mirror
the OpenAI `response.usage` shape; the Gemini-native
`response.usage_metadata` (with `prompt_token_count` /
`candidates_token_count` / `total_token_count`) is normalized into the
same shape inside `_extract_token_usage`.

### `LLMResponse` (NamedTuple)

```python
class LLMResponse(NamedTuple):
    code: str
    token_usage: TokenUsage | None
```

Structured generation result returned by `LLMClient.generate_code(...)`
(replaces the previous raw `str` return). `token_usage=None` indicates
the provider did not report counts — callers must treat that as
"unknown cost" rather than zero cost from a billing perspective, but
the budget guard treats it as 0 (graceful degradation).

### `RetryLoopResult.skipped_reason` (new field)

```python
@dataclass
class RetryLoopResult:
    ...
    skipped_reason: Optional[str] = None
```

Set to `"token_budget_exceeded (used/budget)"` when the loop
short-circuits on the token budget. `None` for successful runs and for
runs that exhausted retries normally. The orchestrator surfaces this
string in `SkipResult.error_log`.

## Files changed

### `pipeline/phase_2/orchestration/llm_client.py`

- New `TokenUsage` and `LLMResponse` NamedTuples.
- New `_extract_token_usage(response, provider)` helper:
  - `gemini-native` → reads `response.usage_metadata`
    (`prompt_token_count` / `candidates_token_count` /
    `total_token_count`).
  - All other providers (OpenAI, Azure, Gemini-via-OpenAI, custom) →
    reads `response.usage` (`prompt_tokens` / `completion_tokens` /
    `total_tokens`).
  - Returns `None` if usage attributes are absent or any access
    raises (older SDKs, mock clients, partial failures).
- New internal `_generate_with_usage(...)` returning
  `(text, TokenUsage | None)`. Public `generate(...)` is now a thin
  wrapper that discards usage (preserving its `str` return).
- `generate_code(...)` now returns `LLMResponse(code, token_usage)`
  instead of a raw `str`.

### `pipeline/phase_2/orchestration/sandbox.py::run_retry_loop` (~L636)

- `llm_generate_fn` signature changed from
  `Callable[[str, str], str]` to
  `Callable[[str, str], LLMResponse]`.
- Two new keyword params, both default-`None` (no behavior change):
  - `token_budget: int | None` — cumulative ceiling on
    `total_tokens` across the initial generation + every retry.
  - `initial_token_usage: TokenUsage | None` — seeds the counter
    with the cost of the orchestrator's initial generation call.
- Loop body now adds `response.token_usage.total_tokens` (or 0) to
  `tokens_used` after each retry call, then short-circuits with a
  `RetryLoopResult(success=False, skipped_reason="token_budget_exceeded
  (used/budget)")` when `tokens_used >= token_budget`.

### `pipeline/phase_2/orchestration/retry_loop.py`

- `_make_generate_fn(...)` now returns
  `Callable[[str, str], LLMResponse]` (was `→ str`). Internally calls
  `llm_client.generate_code(...)` (which now returns `LLMResponse`),
  applies `extract_clean_code` over `response.code`, repackages as
  `LLMResponse(code=cleaned, token_usage=response.token_usage)`.
- `orchestrate(...)` gained a `token_budget: int | None = None` kwarg
  and threads the initial generation's token usage into
  `run_retry_loop` via `initial_token_usage=...`.
- When the loop returns with `result.skipped_reason` set, the
  orchestrator appends that string to `SkipResult.error_log` (existing
  channel; no `SkipResult` shape change required).

### `pipeline/phase_2/types.py`

- Added `skipped_reason: Optional[str] = None` to
  `RetryLoopResult`.

### `pipeline/phase_2/tests/modular/test_retry_loop_token_budget.py` (NEW)

Four tests, exercising `run_retry_loop` directly with a mock
`llm_generate_fn`:

- `test_token_budget_short_circuits_retry_loop` — budget exceeded
  after the first retry call → `skipped_reason` populated, `attempts=1`,
  loop stops well before `max_retries=5`.
- `test_token_budget_none_preserves_baseline_behavior` —
  `token_budget=None` runs all 3 attempts even when each call would
  consume far more tokens than any sane budget; `skipped_reason is None`.
- `test_provider_without_token_counts_degrades_gracefully` —
  `LLMResponse(token_usage=None)` on every call → counter never moves,
  tiny budget=10 never trips, all 3 attempts run.
- `test_initial_token_usage_seeds_counter` — `initial_token_usage`
  alone is enough to trip the budget on the first retry (verifies the
  per-scenario contract: budget covers initial generation + retries).

### `pipeline/phase_2/tests/test_retry_feedback.py`

- Updated the `llm_generate_fn` helper in
  `test_run_retry_loop_passes_accumulated_history_to_llm` to return
  `LLMResponse(code=..., token_usage=None)` instead of a bare string,
  matching the new callable contract. No assertion changes.

## Verification

```bash
conda run -n chart pytest pipeline/phase_2/tests/ -x
# 261 passed in 0.95s
```

The four new token-budget tests pass; all pre-existing modular,
retry-feedback, validation, and engine tests pass unchanged
(`token_budget=None` default propagates through `orchestrate()` →
`run_retry_loop`, so production scenarios see no behavior change).
