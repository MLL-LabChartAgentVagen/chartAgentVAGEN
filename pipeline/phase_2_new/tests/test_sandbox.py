"""
Test suite for agpds.sandbox — Sprint 8, Subtasks 7.1.1, 7.1.2, 7.1.3.

Covers:
  - execute_in_sandbox() contract, input validation, result validation (7.1.1)
  - format_error_feedback() contract, input validation, content checks (7.1.2)
  - run_retry_loop() contract, retry semantics, early exit, exhaustion (7.1.3)
  - SandboxResult / RetryLoopResult dataclass contracts
"""
from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import pytest

from agpds.exceptions import (
    CyclicDependencyError,
    InvalidParameterError,
    NonRootDependencyError,
    SimulatorError,
    UndefinedEffectError,
)
from agpds.sandbox import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT_SECONDS,
    RetryLoopResult,
    SandboxResult,
    execute_in_sandbox,
    format_error_feedback,
    run_retry_loop,
)


# =========================================================================
# Fixtures & Helpers
# =========================================================================

def _permissive_ns() -> dict[str, Any]:
    """Build a sandbox namespace with full builtins for test scripts.

    Production uses a restricted namespace, but tests need full builtins
    so that hand-crafted test scripts (which import pandas, raise SDK
    exceptions, etc.) can execute.
    """
    ns: dict[str, Any] = {"__builtins__": __builtins__}
    return ns


# Pre-built script strings used across test classes

VALID_SCRIPT = (
    "import pandas as pd\n"
    "def build_fact_table(seed=42):\n"
    "    df = pd.DataFrame({'x': [1, 2, 3]})\n"
    "    meta = {'columns': ['x']}\n"
    "    return (df, meta)\n"
)

CYCLIC_DEP_SCRIPT = (
    "from agpds.exceptions import CyclicDependencyError\n"
    "def build_fact_table(seed=42):\n"
    "    raise CyclicDependencyError(['cost', 'satisfaction', 'cost'])\n"
)

UNDEFINED_EFFECT_SCRIPT = (
    "from agpds.exceptions import UndefinedEffectError\n"
    "def build_fact_table(seed=42):\n"
    "    raise UndefinedEffectError('severity_surcharge', 'Severe')\n"
)

NON_ROOT_DEP_SCRIPT = (
    "from agpds.exceptions import NonRootDependencyError\n"
    "def build_fact_table(seed=42):\n"
    "    raise NonRootDependencyError('department')\n"
)

GENERIC_ERROR_SCRIPT = (
    "def build_fact_table(seed=42):\n"
    "    raise RuntimeError('something broke')\n"
)

SYNTAX_ERROR_SCRIPT = "def build_fact_table(:\n    return"

NO_BUILD_FN_SCRIPT = "x = 1\ny = 2\n"

RETURNS_WRONG_TYPE_SCRIPT = (
    "def build_fact_table(seed=42):\n"
    "    return 'not a tuple'\n"
)

RETURNS_NONE_SCRIPT = (
    "def build_fact_table(seed=42):\n"
    "    return None\n"
)

RETURNS_DF_ONLY_SCRIPT = (
    "import pandas as pd\n"
    "def build_fact_table(seed=42):\n"
    "    return pd.DataFrame({'x': [1]})\n"
)

INFINITE_LOOP_SCRIPT = (
    "def build_fact_table(seed=42):\n"
    "    while True:\n"
    "        pass\n"
)


# =========================================================================
# 1. Contract Tests — execute_in_sandbox (7.1.1)
# =========================================================================


class TestExecuteInSandboxContract:
    """Contract table rows from Message 1 for execute_in_sandbox."""

    # [Subtask 7.1.1] — valid script returns success
    def test_valid_script_returns_success(self) -> None:
        """Contract row: valid script → SandboxResult(success=True, dataframe, metadata)."""
        result = execute_in_sandbox(VALID_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.success is True
        assert isinstance(result.dataframe, pd.DataFrame)
        assert isinstance(result.metadata, dict)
        assert result.exception is None
        assert result.traceback_str is None

    # [Subtask 7.1.1] — CyclicDependencyError captured
    def test_cyclic_dependency_error_captured(self) -> None:
        """Contract row: script raising CyclicDependencyError → captured."""
        result = execute_in_sandbox(CYCLIC_DEP_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.success is False
        assert isinstance(result.exception, CyclicDependencyError)
        assert "CyclicDependencyError" in result.traceback_str

    # [Subtask 7.1.1] — UndefinedEffectError captured
    def test_undefined_effect_error_captured(self) -> None:
        """Contract row: script raising UndefinedEffectError → captured."""
        result = execute_in_sandbox(UNDEFINED_EFFECT_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.success is False
        assert isinstance(result.exception, UndefinedEffectError)
        assert "UndefinedEffectError" in result.traceback_str

    # [Subtask 7.1.1] — NonRootDependencyError captured
    def test_non_root_dependency_error_captured(self) -> None:
        """Contract row: script raising NonRootDependencyError → captured."""
        result = execute_in_sandbox(NON_ROOT_DEP_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.success is False
        assert isinstance(result.exception, NonRootDependencyError)

    # [Subtask 7.1.1] — generic RuntimeError captured
    def test_generic_runtime_error_captured(self) -> None:
        """Contract row: script raising RuntimeError → captured."""
        result = execute_in_sandbox(GENERIC_ERROR_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.success is False
        assert isinstance(result.exception, RuntimeError)

    # [Subtask 7.1.1] — syntax error captured
    def test_syntax_error_captured(self) -> None:
        """Contract row: code with syntax error → success=False, SyntaxError."""
        result = execute_in_sandbox(SYNTAX_ERROR_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.success is False
        assert isinstance(result.exception, SyntaxError)

    # [Subtask 7.1.1] — no build_fact_table defined
    def test_no_build_function_fails(self) -> None:
        """Contract row: valid Python but no build_fact_table → failure."""
        result = execute_in_sandbox(NO_BUILD_FN_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.success is False
        assert result.exception is not None
        assert "build_fact_table" in str(result.exception)

    # [Subtask 7.1.1] — returns wrong type (string)
    def test_returns_wrong_type_fails(self) -> None:
        """Contract row: build_fact_table returns a string → failure."""
        result = execute_in_sandbox(RETURNS_WRONG_TYPE_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.success is False
        assert isinstance(result.exception, TypeError)

    # [Subtask 7.1.1] — returns None
    def test_returns_none_fails(self) -> None:
        """Contract row: build_fact_table returns None → failure."""
        result = execute_in_sandbox(RETURNS_NONE_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.success is False
        assert isinstance(result.exception, TypeError)
        assert "None" in str(result.exception)

    # [Subtask 7.1.1] — returns DataFrame only (not a tuple)
    def test_returns_df_only_fails(self) -> None:
        """Contract row: returns DataFrame instead of tuple → failure."""
        result = execute_in_sandbox(RETURNS_DF_ONLY_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.success is False
        assert isinstance(result.exception, TypeError)

    # [Subtask 7.1.1] — empty string raises
    def test_empty_string_raises(self) -> None:
        """Contract row: '' → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            execute_in_sandbox("")

    # [Subtask 7.1.1] — None raises
    def test_none_raises(self) -> None:
        """Contract row: None → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            execute_in_sandbox(None)  # type: ignore[arg-type]

    # [Subtask 7.1.1] — infinite loop with short timeout
    def test_infinite_loop_times_out(self) -> None:
        """Contract row: infinite loop with timeout=1 → timeout failure."""
        result = execute_in_sandbox(
            INFINITE_LOOP_SCRIPT,
            timeout_seconds=1,
            sandbox_namespace=_permissive_ns(),
        )
        assert result.success is False
        assert isinstance(result.exception, TimeoutError)

    # [Subtask 7.1.1] — zero timeout raises
    def test_zero_timeout_raises(self) -> None:
        """Contract row: timeout_seconds=0 → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            execute_in_sandbox(VALID_SCRIPT, timeout_seconds=0)

    # [Subtask 7.1.1] — negative timeout raises
    def test_negative_timeout_raises(self) -> None:
        """Contract row: timeout_seconds=-1 → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            execute_in_sandbox(VALID_SCRIPT, timeout_seconds=-1)


# =========================================================================
# 1. Contract Tests — format_error_feedback (7.1.2)
# =========================================================================


class TestFormatErrorFeedbackContract:
    """Contract table rows from Message 1 for format_error_feedback."""

    # [Subtask 7.1.2] — valid inputs produce four-component payload
    def test_valid_inputs_contain_all_four_components(self) -> None:
        """Contract row: valid (code, exc, tb) → string with code, class, tb, instruction."""
        exc = CyclicDependencyError(["cost", "satisfaction", "cost"])
        feedback = format_error_feedback("my code", exc, "Traceback (most recent)...")

        # Component 1: original code
        assert "my code" in feedback
        # Component 2: exception class name
        assert "CyclicDependencyError" in feedback
        # Component 3: traceback
        assert "Traceback (most recent)" in feedback
        # Component 4: fix instruction
        assert "Adjust parameters to resolve the error" in feedback

    # [Subtask 7.1.2] — UndefinedEffectError carries class name
    def test_undefined_effect_error_class_name(self) -> None:
        """Contract row: UndefinedEffectError → result contains class name and message."""
        exc = UndefinedEffectError("severity_surcharge", "Severe")
        feedback = format_error_feedback("code", exc, "tb")
        assert "UndefinedEffectError" in feedback
        assert "severity_surcharge" in feedback

    # [Subtask 7.1.2] — empty code raises
    def test_empty_code_raises(self) -> None:
        """Contract row: '' code → InvalidParameterError."""
        exc = RuntimeError("x")
        with pytest.raises(InvalidParameterError):
            format_error_feedback("", exc, "tb")

    # [Subtask 7.1.2] — empty traceback raises
    def test_empty_traceback_raises(self) -> None:
        """Contract row: '' traceback → InvalidParameterError."""
        exc = RuntimeError("x")
        with pytest.raises(InvalidParameterError):
            format_error_feedback("code", exc, "")

    # [Subtask 7.1.2] — None code raises
    def test_none_code_raises(self) -> None:
        """Contract row: None code → InvalidParameterError."""
        exc = RuntimeError("x")
        with pytest.raises(InvalidParameterError):
            format_error_feedback(None, exc, "tb")  # type: ignore[arg-type]

    # [Subtask 7.1.2] — None exception raises
    def test_none_exception_raises(self) -> None:
        """Contract row: None exception → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            format_error_feedback("code", None, "tb")  # type: ignore[arg-type]

    # [Subtask 7.1.2] — verify all 4 section headers present
    def test_all_four_section_headers_present(self) -> None:
        """Contract row: any valid inputs → all 4 §2.7 components present."""
        exc = ValueError("test")
        feedback = format_error_feedback("code_here", exc, "tb_here")
        assert "=== ORIGINAL CODE ===" in feedback
        assert "=== ERROR ===" in feedback
        assert "=== TRACEBACK ===" in feedback
        assert "=== INSTRUCTION ===" in feedback


# =========================================================================
# 1. Contract Tests — run_retry_loop (7.1.3)
# =========================================================================


class TestRunRetryLoopContract:
    """Contract table rows from Message 1 for run_retry_loop."""

    # [Subtask 7.1.3] — success on first attempt
    def test_success_on_first_attempt(self) -> None:
        """Contract row: valid code → success=True, attempts=1."""
        call_log: list[str] = []

        def mock_llm(sys_p: str, user_p: str) -> str:
            call_log.append("called")
            return "x"

        result = run_retry_loop(
            VALID_SCRIPT, mock_llm, "system",
            max_retries=3,
            sandbox_namespace_factory=_permissive_ns,
        )
        assert result.success is True
        assert result.attempts == 1
        assert isinstance(result.dataframe, pd.DataFrame)
        assert isinstance(result.metadata, dict)

    # [Subtask 7.1.3] — first fails, second succeeds
    def test_retry_succeeds_on_second_attempt(self) -> None:
        """Contract row: bad code → LLM returns fixed code → success on attempt 2."""
        def mock_llm(sys_p: str, user_p: str) -> str:
            return VALID_SCRIPT

        bad = "def build_fact_table(): raise ValueError('oops')"
        result = run_retry_loop(
            bad, mock_llm, "system",
            max_retries=3,
            sandbox_namespace_factory=_permissive_ns,
        )
        assert result.success is True
        assert result.attempts == 2
        assert result.history[0].success is False
        assert result.history[1].success is True

    # [Subtask 7.1.3] — all 3 attempts fail
    def test_all_attempts_exhausted(self) -> None:
        """Contract row: 3 failures → success=False, attempts=3."""
        def mock_llm(sys_p: str, user_p: str) -> str:
            return "def build_fact_table(): raise ValueError('bad')"

        bad = "def build_fact_table(): raise ValueError('bad')"
        result = run_retry_loop(
            bad, mock_llm, "system",
            max_retries=3,
            sandbox_namespace_factory=_permissive_ns,
        )
        assert result.success is False
        assert result.attempts == 3
        assert len(result.history) == 3
        assert all(not h.success for h in result.history)

    # [Subtask 7.1.3] — fails twice, succeeds on third
    def test_succeeds_on_third_attempt(self) -> None:
        """Contract row: fails twice, succeeds third → attempts=3, success=True."""
        attempt_counter = {"n": 0}

        def mock_llm(sys_p: str, user_p: str) -> str:
            attempt_counter["n"] += 1
            if attempt_counter["n"] >= 2:
                return VALID_SCRIPT
            return "def build_fact_table(): raise ValueError('retry me')"

        bad = "def build_fact_table(): raise ValueError('initial')"
        result = run_retry_loop(
            bad, mock_llm, "system",
            max_retries=3,
            sandbox_namespace_factory=_permissive_ns,
        )
        assert result.success is True
        assert result.attempts == 3

    # [Subtask 7.1.3] — LLM called with feedback content
    def test_llm_receives_error_feedback(self) -> None:
        """Contract row: first attempt fails → llm_generate_fn receives error feedback."""
        captured_prompts: list[tuple[str, str]] = []

        def mock_llm(sys_p: str, user_p: str) -> str:
            captured_prompts.append((sys_p, user_p))
            return VALID_SCRIPT

        bad = "def build_fact_table(): raise ValueError('test error')"
        run_retry_loop(
            bad, mock_llm, "my_system_prompt",
            max_retries=3,
            sandbox_namespace_factory=_permissive_ns,
        )
        assert len(captured_prompts) == 1
        sys_p, user_p = captured_prompts[0]
        # System prompt forwarded verbatim
        assert sys_p == "my_system_prompt"
        # User prompt contains error feedback with the four components
        assert "def build_fact_table" in user_p
        assert "ValueError" in user_p
        assert "Adjust parameters" in user_p

    # [Subtask 7.1.3] — verify attempt counter on 3 failures
    def test_attempt_counter_equals_max_retries(self) -> None:
        """Contract row: 3 failures → attempts == 3, len(history) == 3."""
        def mock_llm(sys_p: str, user_p: str) -> str:
            return "def build_fact_table(): raise ValueError('bad')"

        bad = "def build_fact_table(): raise ValueError('bad')"
        result = run_retry_loop(
            bad, mock_llm, "system",
            max_retries=3,
            sandbox_namespace_factory=_permissive_ns,
        )
        assert result.attempts == 3
        assert len(result.history) == 3

    # [Subtask 7.1.3] — early exit: LLM never called on first-attempt success
    def test_llm_not_called_on_immediate_success(self) -> None:
        """Contract row: success on attempt 1 → LLM generate function never called."""
        call_count = {"n": 0}

        def mock_llm(sys_p: str, user_p: str) -> str:
            call_count["n"] += 1
            return "x"

        run_retry_loop(
            VALID_SCRIPT, mock_llm, "system",
            max_retries=3,
            sandbox_namespace_factory=_permissive_ns,
        )
        assert call_count["n"] == 0

    # [Subtask 7.1.3] — empty initial_code raises
    def test_empty_initial_code_raises(self) -> None:
        """Contract row: '' initial code → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            run_retry_loop("", lambda s, u: "x", "system")

    # [Subtask 7.1.3] — empty system_prompt raises
    def test_empty_system_prompt_raises(self) -> None:
        """Contract row: '' system prompt → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            run_retry_loop("code", lambda s, u: "x", "")

    # [Subtask 7.1.3] — zero max_retries raises
    def test_zero_max_retries_raises(self) -> None:
        """Contract row: max_retries=0 → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            run_retry_loop("code", lambda s, u: "x", "system", max_retries=0)

    # [Subtask 7.1.3] — negative max_retries raises
    def test_negative_max_retries_raises(self) -> None:
        """Contract row: max_retries=-1 → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            run_retry_loop("code", lambda s, u: "x", "system", max_retries=-1)

    # [Subtask 7.1.3] — logging on exhaustion
    def test_logging_on_exhaustion(self, caplog: pytest.LogCaptureFixture) -> None:
        """Contract row: all retries fail → DEBUG log indicating exhaustion."""
        def mock_llm(sys_p: str, user_p: str) -> str:
            return "def build_fact_table(): raise ValueError('bad')"

        bad = "def build_fact_table(): raise ValueError('bad')"
        with caplog.at_level(logging.DEBUG, logger="agpds.sandbox"):
            run_retry_loop(
                bad, mock_llm, "system",
                max_retries=3,
                sandbox_namespace_factory=_permissive_ns,
            )
        assert any("exhausted" in record.message for record in caplog.records)

    # [Subtask 7.1.3] — no §2.9 invocation (verify retry loop does not
    # call any validation or auto-fix)
    def test_no_validation_loop_invoked(self) -> None:
        """Contract row: no §2.9 invocation — only sandbox + LLM calls."""
        result = run_retry_loop(
            VALID_SCRIPT, lambda s, u: "x", "system",
            max_retries=3,
            sandbox_namespace_factory=_permissive_ns,
        )
        # RetryLoopResult should not have any validation report
        assert not hasattr(result, "validation_report")
        assert not hasattr(result, "checks")


# =========================================================================
# 2. Input Validation Tests
# =========================================================================


class TestExecuteInSandboxInputValidation:
    """Exhaustive input validation for execute_in_sandbox."""

    # [Subtask 7.1.1] — non-string source_code types
    @pytest.mark.parametrize("bad_input", [42, 3.14, [], {}, True, b"code"])
    def test_non_string_source_code_raises(self, bad_input: object) -> None:
        with pytest.raises(InvalidParameterError):
            execute_in_sandbox(bad_input)  # type: ignore[arg-type]

    # [Subtask 7.1.1] — whitespace-only source_code
    def test_whitespace_only_source_code_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            execute_in_sandbox("   \n\t  ")

    # [Subtask 7.1.1] — None source_code
    def test_none_source_code_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            execute_in_sandbox(None)  # type: ignore[arg-type]

    # [Subtask 7.1.1] — non-numeric timeout
    @pytest.mark.parametrize("bad_timeout", ["fast", None, [], {}])
    def test_non_numeric_timeout_raises(self, bad_timeout: object) -> None:
        with pytest.raises(InvalidParameterError):
            execute_in_sandbox(VALID_SCRIPT, timeout_seconds=bad_timeout)  # type: ignore[arg-type]


class TestFormatErrorFeedbackInputValidation:
    """Exhaustive input validation for format_error_feedback."""

    # [Subtask 7.1.2] — whitespace-only code
    def test_whitespace_only_code_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            format_error_feedback("   ", RuntimeError("x"), "tb")

    # [Subtask 7.1.2] — whitespace-only traceback
    def test_whitespace_only_traceback_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            format_error_feedback("code", RuntimeError("x"), "   ")

    # [Subtask 7.1.2] — None traceback
    def test_none_traceback_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            format_error_feedback("code", RuntimeError("x"), None)  # type: ignore[arg-type]


class TestRunRetryLoopInputValidation:
    """Exhaustive input validation for run_retry_loop."""

    # [Subtask 7.1.3] — None initial_code
    def test_none_initial_code_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            run_retry_loop(None, lambda s, u: "x", "system")  # type: ignore[arg-type]

    # [Subtask 7.1.3] — None system_prompt
    def test_none_system_prompt_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            run_retry_loop("code", lambda s, u: "x", None)  # type: ignore[arg-type]

    # [Subtask 7.1.3] — float max_retries
    def test_float_max_retries_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            run_retry_loop("code", lambda s, u: "x", "sys", max_retries=2.5)  # type: ignore[arg-type]

    # [Subtask 7.1.3] — negative timeout_seconds
    def test_negative_timeout_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            run_retry_loop(
                "code", lambda s, u: "x", "sys",
                max_retries=3, timeout_seconds=-5,
            )

    # [Subtask 7.1.3] — whitespace-only initial_code
    def test_whitespace_only_initial_code_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            run_retry_loop("   ", lambda s, u: "x", "system")

    # [Subtask 7.1.3] — whitespace-only system_prompt
    def test_whitespace_only_system_prompt_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            run_retry_loop("code", lambda s, u: "x", "   ")


# =========================================================================
# 3. Output Correctness Tests
# =========================================================================


class TestSandboxResultDataclass:
    """Verify SandboxResult field types and semantics."""

    # [Subtask 7.1.1] — success result fields
    def test_success_result_field_types(self) -> None:
        result = execute_in_sandbox(VALID_SCRIPT, sandbox_namespace=_permissive_ns())
        assert isinstance(result, SandboxResult)
        assert isinstance(result.success, bool)
        assert isinstance(result.dataframe, pd.DataFrame)
        assert isinstance(result.metadata, dict)
        assert result.exception is None
        assert result.traceback_str is None

    # [Subtask 7.1.1] — failure result fields
    def test_failure_result_field_types(self) -> None:
        result = execute_in_sandbox(GENERIC_ERROR_SCRIPT, sandbox_namespace=_permissive_ns())
        assert isinstance(result, SandboxResult)
        assert result.success is False
        assert result.dataframe is None
        assert result.metadata is None
        assert isinstance(result.exception, Exception)
        assert isinstance(result.traceback_str, str)

    # [Subtask 7.1.1] — dataframe content matches what script produced
    def test_dataframe_content_matches_script_output(self) -> None:
        result = execute_in_sandbox(VALID_SCRIPT, sandbox_namespace=_permissive_ns())
        assert list(result.dataframe.columns) == ["x"]
        assert list(result.dataframe["x"]) == [1, 2, 3]

    # [Subtask 7.1.1] — metadata content matches what script produced
    def test_metadata_content_matches_script_output(self) -> None:
        result = execute_in_sandbox(VALID_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.metadata == {"columns": ["x"]}


class TestRetryLoopResultDataclass:
    """Verify RetryLoopResult field types and semantics."""

    # [Subtask 7.1.3] — success result
    def test_success_result_fields(self) -> None:
        result = run_retry_loop(
            VALID_SCRIPT, lambda s, u: "x", "system",
            max_retries=3, sandbox_namespace_factory=_permissive_ns,
        )
        assert isinstance(result, RetryLoopResult)
        assert result.success is True
        assert result.attempts == 1
        assert isinstance(result.history, list)
        assert len(result.history) == 1
        assert result.history[0].success is True

    # [Subtask 7.1.3] — failure result
    def test_failure_result_fields(self) -> None:
        def mock_llm(s: str, u: str) -> str:
            return "def build_fact_table(): raise ValueError('bad')"

        result = run_retry_loop(
            "def build_fact_table(): raise ValueError('bad')",
            mock_llm, "system",
            max_retries=2, sandbox_namespace_factory=_permissive_ns,
        )
        assert isinstance(result, RetryLoopResult)
        assert result.success is False
        assert result.dataframe is None
        assert result.metadata is None
        assert result.attempts == 2
        assert len(result.history) == 2


class TestFormatErrorFeedbackOutputCorrectness:
    """Verify output content of format_error_feedback."""

    # [Subtask 7.1.2] — exception message included
    def test_exception_message_included(self) -> None:
        exc = CyclicDependencyError(["a", "b", "a"])
        feedback = format_error_feedback("code", exc, "tb")
        assert str(exc) in feedback

    # [Subtask 7.1.2] — various exception classes formatted correctly
    @pytest.mark.parametrize("exc,expected_class", [
        (ValueError("test"), "ValueError"),
        (TypeError("test"), "TypeError"),
        (RuntimeError("test"), "RuntimeError"),
        (CyclicDependencyError(["a", "b"]), "CyclicDependencyError"),
        (NonRootDependencyError("col"), "NonRootDependencyError"),
    ])
    def test_exception_class_name_in_output(
        self, exc: Exception, expected_class: str
    ) -> None:
        feedback = format_error_feedback("code", exc, "traceback text")
        assert expected_class in feedback

    # [Subtask 7.1.2] — output is a string
    def test_return_type_is_str(self) -> None:
        feedback = format_error_feedback("code", ValueError("x"), "tb")
        assert isinstance(feedback, str)

    # [Subtask 7.1.2] — long code and traceback preserved
    def test_long_content_preserved(self) -> None:
        long_code = "x = 1\n" * 500
        long_tb = "line 1\nline 2\n" * 200
        feedback = format_error_feedback(long_code, ValueError("x"), long_tb)
        assert long_code in feedback
        assert long_tb in feedback


# =========================================================================
# 4. State Transition Tests
# =========================================================================


class TestSandboxNamespaceIsolation:
    """Verify that sandbox executions do not leak state between calls."""

    # [Subtask 7.1.1] — sequential calls use independent namespaces
    def test_sequential_executions_have_independent_state(self) -> None:
        script_set = "def build_fact_table():\n    global _leaked\n    _leaked = 42\n    raise ValueError('done')"
        script_read = (
            "import pandas as pd\n"
            "def build_fact_table():\n"
            "    val = globals().get('_leaked', 'clean')\n"
            "    return (pd.DataFrame({'state': [val]}), {'clean': True})\n"
        )
        # First call sets a global
        execute_in_sandbox(script_set, sandbox_namespace=_permissive_ns())
        # Second call in a fresh namespace should not see it
        result = execute_in_sandbox(script_read, sandbox_namespace=_permissive_ns())
        assert result.success is True
        assert result.dataframe["state"].iloc[0] == "clean"


class TestRetryLoopStateTransitions:
    """Verify state transitions during the retry loop."""

    # [Subtask 7.1.3] — history accumulates in order
    def test_history_accumulates_in_attempt_order(self) -> None:
        attempts_seen: list[int] = []

        def mock_llm(sys_p: str, user_p: str) -> str:
            attempts_seen.append(len(attempts_seen) + 1)
            return "def build_fact_table(): raise ValueError('still bad')"

        bad = "def build_fact_table(): raise ValueError('initial')"
        result = run_retry_loop(
            bad, mock_llm, "system",
            max_retries=3, sandbox_namespace_factory=_permissive_ns,
        )
        # History has 3 entries, one per attempt
        assert len(result.history) == 3
        # All failed
        for h in result.history:
            assert h.success is False

    # [Subtask 7.1.3] — each attempt gets fresh namespace
    def test_each_attempt_gets_fresh_namespace(self) -> None:
        factory_calls = {"count": 0}

        def counting_factory() -> dict[str, Any]:
            factory_calls["count"] += 1
            return _permissive_ns()

        def mock_llm(sys_p: str, user_p: str) -> str:
            return "def build_fact_table(): raise ValueError('bad')"

        bad = "def build_fact_table(): raise ValueError('bad')"
        run_retry_loop(
            bad, mock_llm, "system",
            max_retries=3, sandbox_namespace_factory=counting_factory,
        )
        # Factory called once per attempt
        assert factory_calls["count"] == 3


# =========================================================================
# 5. Integration Tests
# =========================================================================


class TestSandboxIntegrationWithSprintOneExceptions:
    """Verify sandbox correctly catches and preserves Sprint 1 exception types."""

    # [Subtask 7.1.1, 6.1.1] — CyclicDependencyError preserves cycle_path
    def test_cyclic_error_preserves_cycle_path(self) -> None:
        result = execute_in_sandbox(CYCLIC_DEP_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.exception.cycle_path == ["cost", "satisfaction", "cost"]

    # [Subtask 7.1.1, 6.1.2] — UndefinedEffectError preserves fields
    def test_undefined_effect_preserves_fields(self) -> None:
        result = execute_in_sandbox(UNDEFINED_EFFECT_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.exception.effect_name == "severity_surcharge"
        assert result.exception.missing_value == "Severe"

    # [Subtask 7.1.1, 6.1.3] — NonRootDependencyError preserves column_name
    def test_non_root_dep_preserves_column(self) -> None:
        result = execute_in_sandbox(NON_ROOT_DEP_SCRIPT, sandbox_namespace=_permissive_ns())
        assert result.exception.column_name == "department"

    # [Subtask 7.1.1] — SimulatorError base class is catchable
    def test_sdk_exceptions_are_simulator_errors(self) -> None:
        result = execute_in_sandbox(CYCLIC_DEP_SCRIPT, sandbox_namespace=_permissive_ns())
        assert isinstance(result.exception, SimulatorError)


class TestRetryLoopIntegrationWithFeedbackFormatter:
    """Verify that run_retry_loop correctly feeds format_error_feedback output to the LLM."""

    # [Subtask 7.1.2 + 7.1.3] — feedback prompt structure
    def test_feedback_prompt_has_four_sections(self) -> None:
        captured: list[str] = []

        def mock_llm(sys_p: str, user_p: str) -> str:
            captured.append(user_p)
            return VALID_SCRIPT

        bad = "def build_fact_table(): raise ValueError('broken')"
        run_retry_loop(
            bad, mock_llm, "system",
            max_retries=3, sandbox_namespace_factory=_permissive_ns,
        )
        assert len(captured) == 1
        feedback = captured[0]
        assert "=== ORIGINAL CODE ===" in feedback
        assert "=== ERROR ===" in feedback
        assert "=== TRACEBACK ===" in feedback
        assert "=== INSTRUCTION ===" in feedback

    # [Subtask 7.1.3] — retry with max_retries=1 means exactly 1 attempt
    def test_max_retries_one_means_single_attempt(self) -> None:
        result = run_retry_loop(
            "def build_fact_table(): raise ValueError('bad')",
            lambda s, u: "x",
            "system",
            max_retries=1,
            sandbox_namespace_factory=_permissive_ns,
        )
        assert result.attempts == 1
        assert result.success is False

    # [Subtask 7.1.3] — LLM failure is handled gracefully
    def test_llm_call_failure_does_not_crash_loop(self) -> None:
        def broken_llm(sys_p: str, user_p: str) -> str:
            raise ConnectionError("LLM unavailable")

        bad = "def build_fact_table(): raise ValueError('bad')"
        result = run_retry_loop(
            bad, broken_llm, "system",
            max_retries=3, sandbox_namespace_factory=_permissive_ns,
        )
        # Should exhaust retries gracefully, not raise
        assert result.success is False
        assert result.attempts == 3


class TestDefaultConstants:
    """Verify module-level constants match §2.7 spec values."""

    # [Subtask 7.1.3] — default max retries is 3
    def test_default_max_retries_is_three(self) -> None:
        assert DEFAULT_MAX_RETRIES == 3

    # [Subtask 7.1.1] — default timeout is 30 seconds
    def test_default_timeout_is_thirty(self) -> None:
        assert DEFAULT_TIMEOUT_SECONDS == 30
