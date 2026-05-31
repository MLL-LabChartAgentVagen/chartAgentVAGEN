"""T6 — integration tests for `run_retry_loop`'s sigma calibration path.

These exercise the calibration retry-budget integration (F2) and the
structured-logging contract (F3.2). Each test uses the real
`execute_in_sandbox` + the real `_build_sandbox_namespace` so the
`_TrackingSimulator` populates `raw_declarations`; only the LLM call
and (where needed) `check_structural_residuals` are mocked.

Test matrix:
  1. Calibration never converges → SkipResult with calibration_unconverged
     and the exec-attempt counter stays at 1 (separate budget).
  2. Calibration recovers after one round of feedback → success.
  3. Exec-error budget and calibration budget are independent (F2 explicit).
  4. No structural sigma → calibration check trivially passes, no retries.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest
import pandas as pd

from pipeline.core.llm_client import LLMResponse, TokenUsage
from pipeline.phase_2.orchestration.retry_loop import run_retry_loop
from pipeline.phase_2.types import Check


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Script that builds a tiny structural-measure scenario via the SDK.
# `accepted = applied * 0.5` with declared sigma=5 (deliberately too low
# vs. the empirical residual std, which the mocked validator returns as 337).
_STRUCTURAL_SCRIPT_BAD_SIGMA = """\
from chartagent.synth import FactTableSimulator

def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=400, seed=seed)
    sim.add_category('region', values=['N', 'S'], weights=[0.5, 0.5], group='geo')
    sim.add_measure(
        'applied',
        family='gaussian',
        param_model={'mu': {'intercept': 1000.0}, 'sigma': {'intercept': 100.0}},
    )
    sim.add_measure_structural(
        'accepted',
        formula='applied * 0.5',
        effects={},
        noise={'sigma': 5.0},
    )
    return sim.generate()
"""

# Same scenario but with sigma=50, which matches the empirical residual
# std (gaussian noise sigma=50 → residual_std≈50).
_STRUCTURAL_SCRIPT_GOOD_SIGMA = """\
from chartagent.synth import FactTableSimulator

def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=400, seed=seed)
    sim.add_category('region', values=['N', 'S'], weights=[0.5, 0.5], group='geo')
    sim.add_measure(
        'applied',
        family='gaussian',
        param_model={'mu': {'intercept': 1000.0}, 'sigma': {'intercept': 100.0}},
    )
    sim.add_measure_structural(
        'accepted',
        formula='applied * 0.5',
        effects={},
        noise={'sigma': 50.0},
    )
    return sim.generate()
"""

# Pure stochastic-measure script — no structural measure means no
# calibration failure can ever be raised.
_STOCHASTIC_ONLY_SCRIPT = """\
from chartagent.synth import FactTableSimulator

def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=200, seed=seed)
    sim.add_category('region', values=['N', 'S'], weights=[0.5, 0.5], group='geo')
    sim.add_measure(
        'applied',
        family='gaussian',
        param_model={'mu': {'intercept': 1000.0}, 'sigma': {'intercept': 100.0}},
    )
    return sim.generate()
"""

_SYNTAX_ERROR_SCRIPT = "def build_fact_table(seed=42):\n    this is not python\n"


def _fail_check(name: str = "residual_accepted") -> Check:
    """Mocked check_structural_residuals failure with a 66× ratio."""
    return Check(
        name=name,
        passed=False,
        detail="noise_sigma=5.0000, residual_std=337.6500, ratio=66.5300 (>= 0.2)",
    )


def _pass_check(name: str = "residual_accepted") -> Check:
    """Mocked check_structural_residuals passing case — residual std near declared."""
    return Check(
        name=name,
        passed=True,
        detail="noise_sigma=50.0000, residual_std=50.1200, ratio=0.0024 (< 0.2)",
    )


# ---------------------------------------------------------------------------
# Test 1: Calibration never converges → SkipResult-equivalent
# ---------------------------------------------------------------------------

@pytest.mark.skip(
    reason="M1 研究 baseline：Loop A 校准已禁用 "
    "(retry_loop._CALIBRATION_ENABLED=False)，见 "
    "docs/soft_failure_fix/mechanisms/M1_RESIDUAL_RECONCILIATION.md §8"
)
def test_calibration_failure_triggers_retry_then_skip_if_unconverged():
    """If declared sigma stays wrong across all calibration retries, the
    loop must return success=False with skipped_reason starting with
    "calibration_unconverged" and the exec-attempt counter must stay at 1
    (calibration retries don't consume the exec-error budget)."""
    call_count = {"n": 0}

    def llm_generate_fn(system: str, user: str) -> LLMResponse:
        call_count["n"] += 1
        # Always return the same bad-sigma script — model never learns.
        return LLMResponse(
            code=_STRUCTURAL_SCRIPT_BAD_SIGMA,
            token_usage=TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
        )

    with patch(
        "pipeline.phase_2.validation.statistical.check_structural_residuals",
        return_value=_fail_check(),
    ):
        result = run_retry_loop(
            initial_code=_STRUCTURAL_SCRIPT_BAD_SIGMA,
            llm_generate_fn=llm_generate_fn,
            system_prompt="SYSTEM",
            max_retries=3,
            timeout_seconds=10,
            scenario_id="t1_unconverged",
        )

    assert result.success is False
    assert result.skipped_reason is not None
    assert result.skipped_reason.startswith("calibration_unconverged"), (
        f"unexpected skipped_reason: {result.skipped_reason!r}"
    )
    # F2: calibration retries are independent of the exec-error counter.
    # All retries here are calibration retries, so the exec attempt
    # counter stays at 1.
    assert result.attempts == 1, (
        f"expected exec attempt counter to stay at 1, got {result.attempts}"
    )
    # 3 calibration retries means 3 LLM calls (the initial code is passed
    # in directly — the first LLM call happens only after the first
    # calibration failure).
    assert call_count["n"] == 3, f"expected 3 LLM calls, got {call_count['n']}"
    # History should record 4 sandbox executions: initial + 3 calibration retries.
    assert len(result.history) == 4

    # Sanity: the message should mention the failing measure.
    assert "accepted" in result.skipped_reason


# ---------------------------------------------------------------------------
# Test 2: Calibration recovers after one round of feedback
# ---------------------------------------------------------------------------

@pytest.mark.skip(
    reason="M1 研究 baseline：Loop A 校准已禁用 "
    "(retry_loop._CALIBRATION_ENABLED=False)，见 "
    "docs/soft_failure_fix/mechanisms/M1_RESIDUAL_RECONCILIATION.md §8"
)
def test_calibration_recovers_after_one_round_of_feedback():
    """First exec produces a calibration failure; LLM returns a script
    with corrected sigma; second calibration check passes; loop succeeds."""
    call_count = {"n": 0}

    def llm_generate_fn(system: str, user: str) -> LLMResponse:
        call_count["n"] += 1
        # The LLM responds to the calibration feedback with the good script.
        return LLMResponse(
            code=_STRUCTURAL_SCRIPT_GOOD_SIGMA,
            token_usage=TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
        )

    # First check_structural_residuals call → fail; second → pass.
    check_results = [_fail_check(), _pass_check()]
    with patch(
        "pipeline.phase_2.validation.statistical.check_structural_residuals",
        side_effect=check_results,
    ):
        result = run_retry_loop(
            initial_code=_STRUCTURAL_SCRIPT_BAD_SIGMA,
            llm_generate_fn=llm_generate_fn,
            system_prompt="SYSTEM",
            max_retries=3,
            timeout_seconds=10,
            scenario_id="t2_recovers",
        )

    assert result.success is True, (
        f"expected recovery but got skipped_reason={result.skipped_reason!r}"
    )
    assert result.dataframe is not None and isinstance(result.dataframe, pd.DataFrame)
    assert len(result.dataframe) == 400
    # Exactly one calibration retry was used.
    assert call_count["n"] == 1, f"expected 1 LLM call, got {call_count['n']}"
    # Two sandbox executions: initial (bad sigma) + post-calibration retry (good sigma).
    assert len(result.history) == 2
    # Exec counter stays at 1 — calibration retry did not advance it.
    assert result.attempts == 1


# ---------------------------------------------------------------------------
# Test 3: F2 explicit — exec-error and calibration budgets are independent
# ---------------------------------------------------------------------------

def test_calibration_budget_separate_from_exec_budget():
    """First two LLM responses are SyntaxError scripts (exhausting 2 of 3
    exec-error attempts); third LLM response is the good-sigma script
    which passes calibration on the first try."""
    call_count = {"n": 0}
    responses = [
        # exec-error retry 1
        LLMResponse(code=_SYNTAX_ERROR_SCRIPT, token_usage=TokenUsage(10, 10, 20)),
        # exec-error retry 2
        LLMResponse(code=_STRUCTURAL_SCRIPT_GOOD_SIGMA, token_usage=TokenUsage(10, 10, 20)),
    ]

    def llm_generate_fn(system: str, user: str) -> LLMResponse:
        idx = call_count["n"]
        call_count["n"] += 1
        return responses[idx]

    # Calibration on the third (successful) exec passes immediately.
    with patch(
        "pipeline.phase_2.validation.statistical.check_structural_residuals",
        return_value=_pass_check(),
    ):
        result = run_retry_loop(
            initial_code=_SYNTAX_ERROR_SCRIPT,
            llm_generate_fn=llm_generate_fn,
            system_prompt="SYSTEM",
            max_retries=3,
            timeout_seconds=10,
            scenario_id="t3_independent_budgets",
        )

    assert result.success is True, (
        f"expected success after 2 exec retries; got skipped_reason="
        f"{result.skipped_reason!r}"
    )
    # 3 sandbox attempts (initial broken + 2 retries; last one succeeds).
    assert len(result.history) == 3
    # Exec attempt counter should be 3 (the successful one).
    assert result.attempts == 3
    # Two LLM calls — both on the exec-error path; calibration consumed none.
    assert call_count["n"] == 2


# ---------------------------------------------------------------------------
# Test 4: No structural measure → calibration check is a no-op
# ---------------------------------------------------------------------------

def test_no_calibration_trigger_when_no_structural_sigma():
    """A script with only stochastic measures has no structural sigma to
    calibrate; calibration check trivially passes and no retries occur."""
    call_count = {"n": 0}

    def llm_generate_fn(system: str, user: str) -> LLMResponse:
        # Should never be called.
        call_count["n"] += 1
        raise AssertionError("LLM should not be called for stochastic-only script")

    result = run_retry_loop(
        initial_code=_STOCHASTIC_ONLY_SCRIPT,
        llm_generate_fn=llm_generate_fn,
        system_prompt="SYSTEM",
        max_retries=3,
        timeout_seconds=10,
        scenario_id="t4_no_structural",
    )

    assert result.success is True
    assert result.attempts == 1
    assert len(result.history) == 1
    assert call_count["n"] == 0
    assert result.skipped_reason is None
