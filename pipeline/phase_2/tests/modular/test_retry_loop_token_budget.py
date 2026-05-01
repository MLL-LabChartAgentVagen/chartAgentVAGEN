"""IS-6 token-budget half: retry loop early-exit on cumulative token cost.

Covers the three test criteria from
``stub_blocker_decisions.md §IS-6 — Verification``:

1. Retry loop terminates early when budget hit; reports
   ``token_budget_exceeded`` reason.
2. ``token_budget=None`` default → no behavior change.
3. Provider returning ``token_usage=None`` → counter degrades to 0,
   budget never trips.
"""
from __future__ import annotations

from pipeline.phase_2.orchestration.llm_client import LLMResponse, TokenUsage
from pipeline.phase_2.orchestration.sandbox import run_retry_loop


_BROKEN_INITIAL = (
    "def build_fact_table():\n"
    "    raise ValueError('bug_initial')\n"
)


def _broken_retry_code(call_index: int) -> str:
    """Each retry returns a distinct still-failing script."""
    return (
        "def build_fact_table():\n"
        f"    raise ValueError('bug_retry_{call_index}')\n"
    )


def test_token_budget_short_circuits_retry_loop():
    """Budget exceeded → loop returns early with token_budget_exceeded reason."""
    call_count = {"n": 0}

    def llm_generate_fn(system: str, user: str) -> LLMResponse:
        call_count["n"] += 1
        return LLMResponse(
            code=_broken_retry_code(call_count["n"]),
            # Each retry costs 100 tokens; cumulative trips at 150 budget after one retry.
            token_usage=TokenUsage(
                prompt_tokens=50, completion_tokens=50, total_tokens=100
            ),
        )

    result = run_retry_loop(
        initial_code=_BROKEN_INITIAL,
        llm_generate_fn=llm_generate_fn,
        system_prompt="SYSTEM",
        max_retries=5,
        timeout_seconds=5,
        token_budget=100,
    )

    assert result.success is False
    assert result.skipped_reason is not None
    assert result.skipped_reason.startswith("token_budget_exceeded")
    # Sandbox attempt 1 fails → LLM call (100 tokens) → budget tripped.
    assert result.attempts == 1
    assert call_count["n"] == 1
    # max_retries=5 was the cap; budget short-circuited well before that.
    assert len(result.history) == 1


def test_token_budget_none_preserves_baseline_behavior():
    """token_budget=None → identical behavior to the existing retry loop."""
    call_count = {"n": 0}

    def llm_generate_fn(system: str, user: str) -> LLMResponse:
        call_count["n"] += 1
        return LLMResponse(
            code=_broken_retry_code(call_count["n"]),
            token_usage=TokenUsage(
                prompt_tokens=10_000, completion_tokens=10_000, total_tokens=20_000
            ),
        )

    result = run_retry_loop(
        initial_code=_BROKEN_INITIAL,
        llm_generate_fn=llm_generate_fn,
        system_prompt="SYSTEM",
        max_retries=3,
        timeout_seconds=5,
        token_budget=None,
    )

    assert result.success is False
    assert result.skipped_reason is None
    # Baseline shape: 3 attempts (initial + 2 retries).
    assert result.attempts == 3
    assert len(result.history) == 3


def test_provider_without_token_counts_degrades_gracefully():
    """token_usage=None on every call → counter stays at 0, budget never trips."""
    call_count = {"n": 0}

    def llm_generate_fn(system: str, user: str) -> LLMResponse:
        call_count["n"] += 1
        return LLMResponse(
            code=_broken_retry_code(call_count["n"]),
            token_usage=None,
        )

    # Tiny budget that would trip immediately if any usage were counted.
    result = run_retry_loop(
        initial_code=_BROKEN_INITIAL,
        llm_generate_fn=llm_generate_fn,
        system_prompt="SYSTEM",
        max_retries=3,
        timeout_seconds=5,
        token_budget=10,
    )

    assert result.success is False
    assert result.skipped_reason is None
    assert result.attempts == 3


def test_initial_token_usage_seeds_counter():
    """Cumulative budget includes the orchestrator's initial-generation cost."""
    def llm_generate_fn(system: str, user: str) -> LLMResponse:
        return LLMResponse(
            code=_broken_retry_code(1),
            token_usage=TokenUsage(0, 0, 0),
        )

    # Initial generation already consumed 200 tokens; budget=150 → first
    # retry call is allowed but budget trips immediately afterwards.
    result = run_retry_loop(
        initial_code=_BROKEN_INITIAL,
        llm_generate_fn=llm_generate_fn,
        system_prompt="SYSTEM",
        max_retries=5,
        timeout_seconds=5,
        token_budget=150,
        initial_token_usage=TokenUsage(100, 100, 200),
    )

    assert result.success is False
    assert result.skipped_reason is not None
    assert "token_budget_exceeded" in result.skipped_reason
    # Initial-generation cost (200) already exceeds budget (150).
    # First sandbox attempt fails, LLM gets called once (adding 0), and
    # the cumulative count (200 ≥ 150) trips immediately afterwards.
    assert result.attempts == 1
