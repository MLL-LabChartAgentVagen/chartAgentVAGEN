"""Tests for cumulative-failure feedback in the §2.7 retry loop.

Covers:
  - format_error_feedback(): backward-compat path (no prior failures)
  - format_error_feedback(): emits PRIOR FAILED ATTEMPTS section with history
  - run_retry_loop(): threads history into the prompt the LLM receives
"""
from __future__ import annotations

from pipeline.phase_2.orchestration.sandbox import (
    format_error_feedback,
    run_retry_loop,
)
from pipeline.phase_2.types import SandboxResult


# ---------------------------------------------------------------------------
# format_error_feedback — backward compatibility (no prior failures)
# ---------------------------------------------------------------------------

def test_format_error_feedback_no_history_omits_prior_section():
    out = format_error_feedback(
        original_code="x = 1",
        exception=ValueError("boom"),
        traceback_str="Traceback ...",
    )
    assert "PRIOR FAILED ATTEMPTS" not in out
    assert "=== ORIGINAL CODE ===" in out
    assert "x = 1" in out
    assert "Exception: ValueError: boom" in out
    assert "=== TRACEBACK ===" in out
    assert "Traceback ..." in out
    assert "=== INSTRUCTION ===" in out
    # Original instruction wording (not the with-history variant)
    assert "Adjust parameters to resolve the error" in out


def test_format_error_feedback_empty_history_treated_as_no_history():
    out_empty = format_error_feedback(
        original_code="x = 1",
        exception=ValueError("boom"),
        traceback_str="tb",
        prior_failures=[],
    )
    assert "PRIOR FAILED ATTEMPTS" not in out_empty


# ---------------------------------------------------------------------------
# format_error_feedback — with history
# ---------------------------------------------------------------------------

def test_format_error_feedback_with_history_lists_all_priors_in_order():
    priors = [
        SandboxResult(success=False, exception=ValueError("first bug"), traceback_str="tb1"),
        SandboxResult(success=False, exception=RuntimeError("second bug"), traceback_str="tb2"),
    ]
    out = format_error_feedback(
        original_code="x = 1",
        exception=KeyError("third bug"),
        traceback_str="tb3",
        prior_failures=priors,
    )

    # Header present
    assert "PRIOR FAILED ATTEMPTS" in out

    # All three errors present (current + 2 prior)
    assert "first bug" in out
    assert "second bug" in out
    assert "third bug" in out

    # Prior errors are numbered 1 and 2; the current error appears in ERROR
    assert "Attempt 1: ValueError: first bug" in out
    assert "Attempt 2: RuntimeError: second bug" in out
    assert "Exception: KeyError: 'third bug'" in out  # KeyError reprs the message

    # Order: priors come before ORIGINAL CODE; current error after
    assert out.index("PRIOR FAILED ATTEMPTS") < out.index("=== ORIGINAL CODE ===")
    assert out.index("first bug") < out.index("=== ORIGINAL CODE ===")
    assert out.index("=== ERROR ===") < out.index("third bug")

    # Stronger instruction is used when priors are present
    assert "avoiding every error listed under PRIOR FAILED ATTEMPTS" in out


def test_format_error_feedback_skips_prior_entries_without_exception():
    # SandboxResult with exception=None should be filtered out.
    priors = [
        SandboxResult(success=False, exception=None, traceback_str="tb"),
        SandboxResult(success=False, exception=ValueError("real bug"), traceback_str="tb"),
    ]
    out = format_error_feedback(
        original_code="x=1",
        exception=KeyError("now"),
        traceback_str="tb",
        prior_failures=priors,
    )
    # Only the real one is listed; numbering starts at 1 for the surviving entry.
    assert "Attempt 1: ValueError: real bug" in out
    assert "Attempt 2:" not in out


# ---------------------------------------------------------------------------
# run_retry_loop — history actually reaches the LLM
# ---------------------------------------------------------------------------

def test_run_retry_loop_passes_accumulated_history_to_llm():
    """Simulate 3 distinct sandbox failures and verify each LLM call sees
    every prior error in its prompt."""

    received_prompts: list[str] = []
    fail_count = {"n": 0}

    def llm_generate_fn(system: str, user: str) -> str:
        # Capture what the LLM would see, then return a script that still fails
        # (so the loop keeps going through max_retries).
        received_prompts.append(user)
        fail_count["n"] += 1
        # Each retry's "fixed" code raises a distinct exception, simulating the
        # GPT 5.2 whack-a-mole pattern.
        return (
            "def build_fact_table():\n"
            f"    raise ValueError('bug_after_retry_{fail_count['n']}')\n"
        )

    initial_code = (
        "def build_fact_table():\n"
        "    raise ValueError('bug_attempt_1')\n"
    )

    result = run_retry_loop(
        initial_code=initial_code,
        llm_generate_fn=llm_generate_fn,
        system_prompt="SYSTEM",
        max_retries=3,
        timeout_seconds=5,
    )

    # All 3 attempts failed by design
    assert result.success is False
    assert result.attempts == 3
    assert len(result.history) == 3

    # The LLM was called twice (once after attempt 1, once after attempt 2).
    # No call after attempt 3 (final attempt — see "if attempt < max_retries").
    assert len(received_prompts) == 2

    prompt_after_attempt_1 = received_prompts[0]
    prompt_after_attempt_2 = received_prompts[1]

    # First retry prompt: only the *current* error visible, no priors yet.
    assert "PRIOR FAILED ATTEMPTS" not in prompt_after_attempt_1
    assert "bug_attempt_1" in prompt_after_attempt_1

    # Second retry prompt: prior section present, lists the attempt-1 error,
    # current error is the one from the script the LLM returned after retry 1.
    assert "PRIOR FAILED ATTEMPTS" in prompt_after_attempt_2
    assert "Attempt 1: ValueError: bug_attempt_1" in prompt_after_attempt_2
    assert "bug_after_retry_1" in prompt_after_attempt_2


# ---------------------------------------------------------------------------
# format_error_feedback — targeted hint section for known-class errors
# ---------------------------------------------------------------------------

def test_format_error_feedback_hint_for_year_derive_error():
    """When add_temporal rejects derive=['year'], the formatter must inject
    a HINT pointing the LLM toward the categorical-year idiom — the raw
    'Supported: [...]' message alone has historically not been enough to
    break the LLM out of the year-grain trap."""
    out = format_error_feedback(
        original_code="sim.add_temporal('y', '2019', '2024', 'YS', derive=['year'])",
        exception=ValueError(
            "Invalid derive features ['year'] for column 'application_year'. "
            "Supported: ['day_of_week', 'is_weekend', 'month', 'quarter']"
        ),
        traceback_str="Traceback ...",
    )
    assert "=== HINT ===" in out
    assert "add_category('year'" in out
    # Hint sits above the INSTRUCTION block so the LLM weights it last.
    assert out.index("=== HINT ===") < out.index("=== INSTRUCTION ===")


def test_format_error_feedback_hint_for_freq_ys_error():
    """If derive=['year'] is dropped but freq='YS' remains, the same hint
    fires — same root cause (yearly grain), same remediation."""
    out = format_error_feedback(
        original_code="sim.add_temporal('y', '2019', '2024', 'YS')",
        exception=ValueError(
            "Unsupported freq 'YS' for temporal column 'y'. "
            "Supported: ['D', 'MS', 'W-FRI', ...]"
        ),
        traceback_str="tb",
    )
    assert "=== HINT ===" in out
    assert "add_category('year'" in out


def test_format_error_feedback_no_hint_for_unrelated_error():
    """Hints are scoped — a generic error does NOT get a HINT section.
    Broad predicates here would mask real diagnostic signal."""
    out = format_error_feedback(
        original_code="x = 1",
        exception=RuntimeError("something else entirely"),
        traceback_str="tb",
    )
    assert "=== HINT ===" not in out


def test_format_error_feedback_hint_for_reserved_time_group():
    """When the LLM follows the YEARLY-GRAIN advice but uses group='time'
    (reserved for add_temporal), surface a hint pointing to a different
    group name like 'calendar'."""
    out = format_error_feedback(
        original_code="sim.add_category('year', values=[2019, 2020], group='time')",
        exception=ValueError(
            "Group name 'time' is reserved for temporal columns. "
            "Use a different group name."
        ),
        traceback_str="tb",
    )
    assert "=== HINT ===" in out
    assert "calendar" in out
    assert "reserved" in out
