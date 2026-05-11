"""
Loop A retry orchestration.

Drives the LLM → sandbox → validate retry loop. Owns ``run_retry_loop``
(the §2.7 step-1..5 driver, relocated from sandbox.py in Sprint D.2)
and the higher-level ``orchestrate`` entry point that wires it to
prompt rendering and SkipResult mapping.

Implements: §2.7 Loop A
"""
from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Callable

from pipeline.core.llm_client import LLMClient, LLMResponse, TokenUsage
from pipeline.phase_1 import ScenarioContext

from ..exceptions import InvalidParameterError, SkipResult
from ..types import RetryLoopResult, SandboxResult
from .code_check import extract_clean_code
from .prompt import render_system_prompt
from .sandbox import (
    DEFAULT_TIMEOUT_SECONDS,
    _build_sandbox_namespace,
    execute_in_sandbox,
    format_error_feedback,
)

logger = logging.getLogger(__name__)


_CODE_GEN_MAX_TOKENS: int = 32768
DEFAULT_MAX_RETRIES: int = 3


def _make_generate_fn(
    llm_client: LLMClient,
) -> Callable[[str, str], LLMResponse]:
    """Return a generate callable that applies robust fence extraction.

    Wraps LLMClient.generate_code() with two improvements over the base call:
      1. max_tokens=32768 — prevents truncation mid-bracket for large scripts.
         Sized for reasoning models (gpt-5.x, o1, o3) where this budget covers
         both reasoning tokens and visible output; non-reasoning models are
         billed per token used, so the headroom is free.
      2. extract_clean_code() — handles LLM responses where prose precedes the
         code block, which defeats generate_code()'s ^-anchored fence regex.

    Returns an ``LLMResponse`` so the retry loop can apply a token budget.
    """
    _call_count = 0

    def _generate(system: str, user: str) -> LLMResponse:
        nonlocal _call_count
        _call_count += 1
        logger.info(
            "=== LLM CALL #%d (user prompt %d chars) ===",
            _call_count, len(user),
        )
        response = llm_client.generate_code(
            system, user, max_tokens=_CODE_GEN_MAX_TOKENS
        )
        raw = response.code
        logger.info(
            "=== LLM RAW RESPONSE (call #%d, %d chars) ===\n%s\n=== END RAW RESPONSE ===",
            _call_count, len(raw), raw,
        )
        cleaned = extract_clean_code(raw)
        if cleaned != raw:
            logger.info(
                "=== AFTER extract_clean_code (call #%d, %d chars) ===\n%s\n=== END CLEANED ===",
                _call_count, len(cleaned), cleaned,
            )
        return LLMResponse(code=cleaned, token_usage=response.token_usage)

    return _generate


def _format_scenario_context(scenario_context: ScenarioContext) -> str:
    """Serialize a ScenarioContext into the [SCENARIO] block text for the prompt.

    Produces a multi-line ``key: value`` string from
    ``dataclasses.asdict(scenario_context)`` so the rendered fields exactly
    match the writer's JSONL surface. The result is injected into the
    ``{scenario_context}`` placeholder in the §2.5 system prompt template.
    """
    return "\n".join(f"{k}: {v}" for k, v in asdict(scenario_context).items())


def run_retry_loop(
    initial_code: str,
    llm_generate_fn: Callable[[str, str], "LLMResponse"],
    system_prompt: str,
    max_retries: int = DEFAULT_MAX_RETRIES,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    sandbox_namespace_factory: Callable[[], dict[str, Any]] | None = None,
    # IS-6 token-budget half: cumulative-across-retries token guard.
    # ``token_budget=None`` disables enforcement (no behavior change).
    # ``initial_token_usage`` seeds the counter with the cost of the
    # initial generation call, which happened in the orchestrator.
    token_budget: int | None = None,
    initial_token_usage: "TokenUsage | None" = None,
    seed: int = 42,
) -> RetryLoopResult:
    """Execute the §2.7 error feedback retry loop.

    [Subtask 7.1.3]

    Algorithm:

    1. Execute *initial_code* in the sandbox.
    2. On success → return the result immediately (attempt 1).
    3. On failure → format error feedback, call *llm_generate_fn* with
       ``(system_prompt, feedback_prompt)`` to obtain new code.
    4. Repeat from step 1 with the new code, up to *max_retries* total
       attempts.
    5. On exhaustion → log the failure and return an unsuccessful
       :class:`RetryLoopResult` with the full attempt history.

    This loop implements **only** the §2.7 execution-error path.  It
    does not invoke §2.9 validation — that responsibility belongs to
    the pipeline orchestrator (11.1.x, currently BLOCKED per C5).

    Args:
        initial_code: First LLM-generated Python code string.
        llm_generate_fn: Callable ``(system_prompt, user_prompt) -> LLMResponse``
            that calls the LLM and returns a structured response carrying
            the corrected code and optional token usage.  Typically
            ``LLMClient.generate_code`` (partially applied).
        system_prompt: The system prompt for retry LLM calls.
        max_retries: Maximum total attempts (default 3).  Must be > 0.
        timeout_seconds: Per-attempt execution timeout in seconds.
        sandbox_namespace_factory: Optional factory for sandbox
            namespaces.  Called once per attempt.  If ``None``, uses
            :func:`_build_sandbox_namespace`.
        token_budget: Optional cumulative-across-retries token ceiling
            (IS-6 token-budget half).  When set, the loop accumulates
            ``response.token_usage.total_tokens`` after each LLM call
            and short-circuits with
            ``RetryLoopResult(success=False, skipped_reason="token_budget_exceeded (used/budget)")``
            once ``tokens_used >= token_budget``.  ``None`` (default)
            disables enforcement — identical to the pre-IS-6 behavior.
        initial_token_usage: Optional ``TokenUsage`` seeding the
            cumulative counter with the cost of the orchestrator's
            initial-generation call (the call that produced
            *initial_code*).  Required for the budget to be genuinely
            per-scenario rather than per-retry-loop.  ``None`` (default)
            seeds the counter at 0.  Providers that do not report token
            counts surface ``None`` here and the budget never trips
            (graceful degradation).

    Returns:
        :class:`RetryLoopResult` with the outcome and full history.
        ``skipped_reason`` is set to ``"token_budget_exceeded ..."``
        when the loop short-circuits on the budget; ``None`` otherwise.

    Raises:
        InvalidParameterError: If *initial_code*, *system_prompt*, or
            *max_retries* fail validation.
    """
    # ===== Input Validation =====

    # Validate initial_code
    if initial_code is None or (isinstance(initial_code, str) and len(initial_code.strip()) == 0):
        raise InvalidParameterError(
            param_name="initial_code",
            value=0.0,
            reason="initial_code must be a non-empty string",
        )

    # Validate system_prompt
    if system_prompt is None or (isinstance(system_prompt, str) and len(system_prompt.strip()) == 0):
        raise InvalidParameterError(
            param_name="system_prompt",
            value=0.0,
            reason="system_prompt must be a non-empty string",
        )

    # Validate max_retries is a positive integer
    if not isinstance(max_retries, int) or max_retries <= 0:
        raise InvalidParameterError(
            param_name="max_retries",
            value=float(max_retries) if isinstance(max_retries, (int, float)) else 0.0,
            reason="max_retries must be a positive integer",
        )

    # Validate timeout_seconds is positive
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        raise InvalidParameterError(
            param_name="timeout_seconds",
            value=float(timeout_seconds) if isinstance(timeout_seconds, (int, float)) else 0.0,
            reason="timeout_seconds must be a positive number",
        )

    # ===== Retry Loop =====

    current_code = initial_code
    history: list[SandboxResult] = []

    # Resolve the namespace factory — default to the module-level builder
    ns_factory = sandbox_namespace_factory or _build_sandbox_namespace

    # Cumulative token counter for the IS-6 token budget. Seed with the
    # initial-generation usage so the budget is genuinely per-scenario.
    tokens_used: int = (
        initial_token_usage.total_tokens if initial_token_usage is not None else 0
    )

    for attempt in range(1, max_retries + 1):

        logger.debug(
            "§2.7 retry loop: attempt %d/%d", attempt, max_retries
        )

        # Execute the current code in a fresh sandbox namespace so that
        # each attempt starts from a clean state
        sandbox_ns = ns_factory()
        result = execute_in_sandbox(
            source_code=current_code,
            timeout_seconds=timeout_seconds,
            sandbox_namespace=sandbox_ns,
            seed=seed,
        )
        history.append(result)

        # ===== Early Exit on Success =====

        if result.success:
            logger.debug(
                "§2.7 retry loop: succeeded on attempt %d", attempt
            )
            return RetryLoopResult(
                success=True,
                dataframe=result.dataframe,
                metadata=result.metadata,
                raw_declarations=result.raw_declarations,
                source_code=result.source_code or current_code,
                attempts=attempt,
                history=history,
            )

        # ===== Prepare Feedback for Next Attempt =====

        # Don't call the LLM after the final failed attempt — there is
        # no subsequent attempt to use the new code
        if attempt < max_retries:
            # Build prior-failures list: every failed attempt except the current
            # one (whose exception is already shown in the ERROR/TRACEBACK sections).
            prior_failures = [h for h in history[:-1] if not h.success]

            # Format the §2.7 step-5 error feedback payload
            feedback_prompt = format_error_feedback(
                original_code=current_code,
                exception=result.exception or RuntimeError("Unknown sandbox failure"),
                traceback_str=result.traceback_str or "No traceback available.",
                prior_failures=prior_failures,
            )

            logger.debug(
                "§2.7 retry loop: calling LLM for corrected code "
                "(attempt %d failed with %s)",
                attempt,
                type(result.exception).__name__ if result.exception else "unknown",
            )

            # Call the LLM to generate corrected code.  The LLM
            # receives the system prompt and the error feedback as the
            # user prompt. The callable returns an ``LLMResponse``
            # carrying optional token usage; we add the usage to the
            # cumulative counter and trip the budget if exceeded.
            try:
                response = llm_generate_fn(system_prompt, feedback_prompt)
                current_code = response.code
                if response.token_usage is not None:
                    tokens_used += response.token_usage.total_tokens
            except Exception as llm_exc:
                # If the LLM call itself fails, log and continue to the
                # next iteration with the same (broken) code — degraded
                # mode that avoids crashing the entire pipeline
                logger.debug(
                    "§2.7 retry loop: LLM call failed on attempt %d: %s",
                    attempt,
                    llm_exc,
                )

            # Token-budget guard: cumulative across the initial
            # generation + every retry call. ``None`` disables.
            if token_budget is not None and tokens_used >= token_budget:
                logger.debug(
                    "§2.7 retry loop: token budget exceeded after attempt %d "
                    "(%d/%d) — short-circuiting",
                    attempt, tokens_used, token_budget,
                )
                return RetryLoopResult(
                    success=False,
                    attempts=attempt,
                    history=history,
                    skipped_reason=(
                        f"token_budget_exceeded ({tokens_used}/{token_budget})"
                    ),
                )

    # ===== Exhaustion =====

    logger.debug(
        "§2.7 retry loop: all %d attempts exhausted — returning failure",
        max_retries,
    )

    return RetryLoopResult(
        success=False,
        attempts=max_retries,
        history=history,
    )


def orchestrate(
    scenario_context: ScenarioContext,
    scenario_id: str,
    llm_client: LLMClient,
    max_retries: int = 3,
    token_budget: int | None = None,
    seed: int = 42,
) -> Any | SkipResult:
    """Execute Loop A: LLM generation → sandbox execution → validation.

    Implements §2.7 Loop A:
      1. Render the §2.5 system prompt with the scenario context.
      2. Call LLMClient.generate_code() for the initial script.
      3. Delegate the full retry loop (execute → error-feedback → re-prompt)
         to :func:`run_retry_loop` (defined above).
      4. On success return (df, metadata, raw_declarations) triple.
         raw_declarations carries live simulator registries (columns, groups,
         group_dependencies, measure_dag, target_rows, patterns, seed) captured
         via _TrackingSimulator in the sandbox. Falls back to metadata when the
         simulator instance is not available (e.g. custom sandbox namespace).
      5. On exhaustion return SkipResult.

    Args:
        scenario_context: Typed Phase 1 output for prompt assembly.
        scenario_id: Caller-supplied identifier (e.g. ``"dom_001/k=1"``)
            propagated into log lines and SkipResult.
        llm_client: Configured LLMClient instance.
        max_retries: Maximum retry attempts before returning SkipResult.

    Returns:
        (DataFrame, metadata, raw_declarations) triple on success, or SkipResult
        if all retries are exhausted.
    """
    # ===== Step 1: Render system prompt =====
    scenario_str = _format_scenario_context(scenario_context)
    system_prompt = render_system_prompt(scenario_str)

    # ===== Step 2: Initial LLM code generation =====
    logger.debug(
        "orchestrate(): calling LLMClient.generate_code() for initial script "
        "(scenario_id=%s)", scenario_id
    )
    # Use the robust wrapper: higher token budget + prose-aware fence extraction.
    generate_fn = _make_generate_fn(llm_client)
    try:
        initial_response = generate_fn(system_prompt, scenario_str)
    except Exception as exc:
        logger.debug(
            "orchestrate(): initial LLM call failed (scenario_id=%s): %s",
            scenario_id, exc,
        )
        return SkipResult(
            scenario_id=scenario_id,
            error_log=[f"Initial LLM call failed: {exc}"],
        )

    # ===== Step 3: Retry loop (execute → error-feedback → re-prompt) =====
    # generate_fn is passed as the callable for retry calls.
    # run_retry_loop calls it as: llm_generate_fn(system_prompt, feedback_prompt)
    result = run_retry_loop(
        initial_code=initial_response.code,
        llm_generate_fn=generate_fn,
        system_prompt=system_prompt,
        max_retries=max_retries,
        token_budget=token_budget,
        initial_token_usage=initial_response.token_usage,
        seed=seed,
    )

    # ===== Step 4: Map result to pipeline contract =====
    if not result.success:
        error_log = [
            str(attempt.exception) if attempt.exception else "Unknown sandbox failure"
            for attempt in result.history
            if not attempt.success
        ]
        if result.skipped_reason:
            error_log.append(result.skipped_reason)
        logger.debug(
            "orchestrate(): loop exited without success (scenario_id=%s, "
            "attempts=%d, skipped_reason=%s)",
            scenario_id, result.attempts, result.skipped_reason,
        )
        return SkipResult(
            scenario_id=scenario_id,
            error_log=error_log or ["All retries exhausted without success."],
        )

    # Success — return the 4-tuple expected by pipeline._run_loop_a.
    # raw_declarations carries live simulator registries when available,
    # falling back to metadata for backward compatibility.
    # source_code is the LLM-generated script string that produced this result.
    return (
        result.dataframe,
        result.metadata,
        result.raw_declarations or result.metadata,
        result.source_code or "",
    )
