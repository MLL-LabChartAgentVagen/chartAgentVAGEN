"""
Loop A retry orchestration.

Drives the LLM → sandbox → validate retry loop.

Implements: §2.7 Loop A
"""
from __future__ import annotations

import logging
from typing import Any, Callable

from ..exceptions import SkipResult
from .code_validator import extract_clean_code
from .llm_client import LLMClient, LLMResponse
from .prompt import render_system_prompt
from .sandbox import run_retry_loop

logger = logging.getLogger(__name__)


_CODE_GEN_MAX_TOKENS: int = 32768


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


def _format_scenario_context(scenario_context: dict[str, Any]) -> str:
    """Serialize scenario_context dict into the [SCENARIO] block text for the prompt.

    Produces a multi-line key: value string. The result is injected into the
    {scenario_context} placeholder in the §2.5 system prompt template.
    """
    lines = []
    for key, value in scenario_context.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def orchestrate(
    scenario_context: dict[str, Any],
    llm_client: LLMClient,
    max_retries: int = 3,
    token_budget: int | None = None,
) -> Any | SkipResult:
    """Execute Loop A: LLM generation → sandbox execution → validation.

    Implements §2.7 Loop A:
      1. Render the §2.5 system prompt with the scenario context.
      2. Call LLMClient.generate_code() for the initial script.
      3. Delegate the full retry loop (execute → error-feedback → re-prompt)
         to sandbox.run_retry_loop().
      4. On success return (df, metadata, raw_declarations) triple.
         raw_declarations carries live simulator registries (columns, groups,
         group_dependencies, measure_dag, target_rows, patterns, seed) captured
         via _TrackingSimulator in the sandbox. Falls back to metadata when the
         simulator instance is not available (e.g. custom sandbox namespace).
      5. On exhaustion return SkipResult.

    Args:
        scenario_context: Context dict for LLM prompt assembly. Must contain
            at minimum the keys used in Phase 1 scenario output.
        llm_client: Configured LLMClient instance.
        max_retries: Maximum retry attempts before returning SkipResult.

    Returns:
        (DataFrame, metadata, raw_declarations) triple on success, or SkipResult
        if all retries are exhausted.
    """
    scenario_id = scenario_context.get("scenario_id", "unknown")

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
    # sandbox.run_retry_loop calls it as: llm_generate_fn(system_prompt, feedback_prompt)
    result = run_retry_loop(
        initial_code=initial_response.code,
        llm_generate_fn=generate_fn,
        system_prompt=system_prompt,
        max_retries=max_retries,
        token_budget=token_budget,
        initial_token_usage=initial_response.token_usage,
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
