"""
Test suite for agpds.code_validator — Sprint 8, Subtasks 10.2.1, 10.2.2.

Covers:
  - extract_clean_code() fence stripping (10.2.1)
  - validate_generated_code() AST-level structural checks (10.2.2)
  - CodeValidationResult dataclass contract
"""
from __future__ import annotations

import pytest

from agpds.code_validator import (
    CodeValidationResult,
    extract_clean_code,
    validate_generated_code,
)
from agpds.exceptions import InvalidParameterError


# =========================================================================
# Code Snippets Used Across Tests
# =========================================================================

# Minimal code that satisfies both §2.5 structural requirements
VALID_MINIMAL = "def build_fact_table():\n    return sim.generate()"

# Full-featured code matching the one-shot example structure
VALID_FULL = """\
from chartagent.synth import FactTableSimulator

def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=500, seed=seed)
    sim.add_category("hospital",
        values=["A", "B"], weights=[0.5, 0.5], group="entity")
    sim.add_measure("wait", family="gaussian",
        param_model={"mu": 10, "sigma": 1})
    return sim.generate()
"""

# Code with build_fact_table but no .generate() call
NO_GENERATE = """\
def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=500, seed=seed)
    return (sim.dataframe, sim.metadata)
"""

# Code with .generate() but no build_fact_table
NO_BUILD_FN = """\
def create_table(seed=42):
    sim = FactTableSimulator(target_rows=500, seed=seed)
    return sim.generate()
"""

# Valid Python missing both required elements
MISSING_BOTH = "x = 1\ny = 2"

# Syntactically invalid Python
SYNTAX_ERROR_CODE = "def build_fact_table(:\n    return"

# .generate() nested inside build_fact_table body
NESTED_GENERATE = """\
def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=500, seed=seed)
    result = sim.generate()
    return result
"""


# =========================================================================
# 1. Contract Tests — extract_clean_code (10.2.1)
# =========================================================================


class TestExtractCleanCodeContract:
    """Contract table rows from Message 1 for extract_clean_code."""

    # [Subtask 10.2.1] — fenced python code
    def test_strips_python_fence(self) -> None:
        """Contract row: '```python\\ncode\\n```' → 'code'."""
        raw = "```python\nx = 1\n```"
        assert extract_clean_code(raw) == "x = 1"

    # [Subtask 10.2.1] — generic fence
    def test_strips_generic_fence(self) -> None:
        """Contract row: '```\\ncode\\n```' → 'code'."""
        raw = "```\nx = 1\n```"
        assert extract_clean_code(raw) == "x = 1"

    # [Subtask 10.2.1] — bare code passthrough
    def test_bare_code_returned_unchanged(self) -> None:
        """Contract row: 'bare code' → 'bare code'."""
        assert extract_clean_code("bare code") == "bare code"

    # [Subtask 10.2.1] — empty string raises
    def test_empty_string_raises(self) -> None:
        """Contract row: '' → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            extract_clean_code("")

    # [Subtask 10.2.1] — None raises
    def test_none_raises(self) -> None:
        """Contract row: None → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            extract_clean_code(None)  # type: ignore[arg-type]

    # [Subtask 10.2.1] — empty body inside fence
    def test_fenced_empty_body_returns_empty_string(self) -> None:
        """Contract row: '```python\\n```' → '' (empty after strip)."""
        raw = "```python\n```"
        assert extract_clean_code(raw) == ""

    # [Subtask 10.2.1] — surrounding prose extracted
    def test_extracts_code_from_surrounding_prose(self) -> None:
        """Contract row: 'text before\\n```python\\ncode\\n```\\ntext after' → 'code'."""
        raw = "Here is the code:\n```python\nresult = compute()\n```\nHope that helps!"
        assert extract_clean_code(raw) == "result = compute()"


# =========================================================================
# 1. Contract Tests — validate_generated_code (10.2.2)
# =========================================================================


class TestValidateGeneratedCodeContract:
    """Contract table rows from Message 1 for validate_generated_code."""

    # [Subtask 10.2.2] — valid code with both elements
    def test_valid_code_passes_all_checks(self) -> None:
        """Contract row: code with build_fact_table and .generate() → all True."""
        result = validate_generated_code(VALID_FULL)
        assert result.is_valid is True
        assert result.has_build_fact_table is True
        assert result.has_generate_call is True
        assert result.errors == []

    # [Subtask 10.2.2] — missing build_fact_table
    def test_no_build_function_fails(self) -> None:
        """Contract row: code without def build_fact_table → is_valid=False."""
        result = validate_generated_code(NO_BUILD_FN)
        assert result.is_valid is False
        assert result.has_build_fact_table is False
        assert any("build_fact_table" in e for e in result.errors)

    # [Subtask 10.2.2] — missing .generate()
    def test_no_generate_call_fails(self) -> None:
        """Contract row: code with build_fact_table but no .generate() → is_valid=False."""
        result = validate_generated_code(NO_GENERATE)
        assert result.is_valid is False
        assert result.has_generate_call is False
        assert any("generate" in e for e in result.errors)

    # [Subtask 10.2.2] — minimal valid code
    def test_minimal_valid_code(self) -> None:
        """Contract row: 'def build_fact_table(): return sim.generate()' → is_valid=True."""
        result = validate_generated_code(VALID_MINIMAL)
        assert result.is_valid is True

    # [Subtask 10.2.2] — syntax error
    def test_syntax_error_fails(self) -> None:
        """Contract row: 'invalid python {{{{' → is_valid=False, errors has syntax description."""
        result = validate_generated_code(SYNTAX_ERROR_CODE)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("SyntaxError" in e for e in result.errors)

    # [Subtask 10.2.2] — empty string raises
    def test_empty_string_raises(self) -> None:
        """Contract row: '' → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            validate_generated_code("")

    # [Subtask 10.2.2] — None raises
    def test_none_raises(self) -> None:
        """Contract row: None → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            validate_generated_code(None)  # type: ignore[arg-type]

    # [Subtask 10.2.2] — wrong type raises TypeError
    def test_integer_raises_type_error(self) -> None:
        """Contract row: 42 → TypeError."""
        with pytest.raises(TypeError):
            validate_generated_code(42)  # type: ignore[arg-type]

    # [Subtask 10.2.2] — missing both elements
    def test_missing_both_elements(self) -> None:
        """Contract row: 'x = 1\\ny = 2' → both False."""
        result = validate_generated_code(MISSING_BOTH)
        assert result.is_valid is False
        assert result.has_build_fact_table is False
        assert result.has_generate_call is False

    # [Subtask 10.2.2] — nested generate inside build_fact_table
    def test_nested_generate_inside_build_fn(self) -> None:
        """Contract row: .generate() call inside build_fact_table body → is_valid=True."""
        result = validate_generated_code(NESTED_GENERATE)
        assert result.is_valid is True
        assert result.has_generate_call is True
        assert result.has_build_fact_table is True


# =========================================================================
# 2. Input Validation Tests
# =========================================================================


class TestExtractCleanCodeInputValidation:
    """Exhaustive input validation for extract_clean_code."""

    # [Subtask 10.2.1] — non-string types
    @pytest.mark.parametrize("bad_input", [42, 3.14, [], {}, True, b"bytes"])
    def test_non_string_type_raises(self, bad_input: object) -> None:
        with pytest.raises(InvalidParameterError):
            extract_clean_code(bad_input)  # type: ignore[arg-type]

    # [Subtask 10.2.1] — whitespace-only
    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            extract_clean_code("   \n\t  ")


class TestValidateGeneratedCodeInputValidation:
    """Exhaustive input validation for validate_generated_code."""

    # [Subtask 10.2.2] — wrong types: list, dict, float, bool, bytes
    @pytest.mark.parametrize("bad_input,expected_exc", [
        ([], TypeError),
        ({}, TypeError),
        (3.14, TypeError),
        (True, TypeError),
        (b"code", TypeError),
    ])
    def test_non_string_type_raises(
        self, bad_input: object, expected_exc: type
    ) -> None:
        with pytest.raises(expected_exc):
            validate_generated_code(bad_input)  # type: ignore[arg-type]

    # [Subtask 10.2.2] — whitespace-only string
    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            validate_generated_code("   \n\t  ")


# =========================================================================
# 3. Output Correctness Tests
# =========================================================================


class TestCodeValidationResultDataclass:
    """Verify the CodeValidationResult dataclass contract."""

    # [Subtask 10.2.2] — frozen dataclass is immutable
    def test_result_is_frozen(self) -> None:
        result = validate_generated_code(VALID_MINIMAL)
        with pytest.raises(AttributeError):
            result.is_valid = False  # type: ignore[misc]

    # [Subtask 10.2.2] — errors is a list of strings
    def test_errors_are_strings(self) -> None:
        result = validate_generated_code(MISSING_BOTH)
        assert isinstance(result.errors, list)
        for err in result.errors:
            assert isinstance(err, str)

    # [Subtask 10.2.2] — valid code produces zero errors
    def test_valid_code_has_empty_errors(self) -> None:
        result = validate_generated_code(VALID_MINIMAL)
        assert len(result.errors) == 0

    # [Subtask 10.2.2] — syntax error prevents structural checks
    def test_syntax_error_blocks_structural_checks(self) -> None:
        result = validate_generated_code("def (invalid")
        assert result.is_valid is False
        # When syntax fails, structural flags stay False (never checked)
        assert result.has_build_fact_table is False
        assert result.has_generate_call is False


class TestExtractCleanCodeOutputCorrectness:
    """Verify output properties of extract_clean_code."""

    # [Subtask 10.2.1] — return type is always str
    def test_return_type_is_str(self) -> None:
        assert isinstance(extract_clean_code("x = 1"), str)

    # [Subtask 10.2.1] — multiline code preserved
    def test_multiline_code_preserved(self) -> None:
        raw = "```python\ndef foo():\n    return 1\n```"
        result = extract_clean_code(raw)
        assert "def foo():" in result
        assert "return 1" in result

    # [Subtask 10.2.1] — leading/trailing whitespace stripped
    def test_leading_trailing_whitespace_stripped(self) -> None:
        result = extract_clean_code("  \n  x = 1  \n  ")
        assert result == "x = 1"

    # [Subtask 10.2.1] — multiple fenced blocks: first one wins
    def test_multiple_fenced_blocks_extracts_first(self) -> None:
        raw = "```python\nfirst\n```\n```python\nsecond\n```"
        result = extract_clean_code(raw)
        assert result == "first"

    # [Subtask 10.2.1] — fence with extra whitespace on fence line
    def test_fence_with_trailing_spaces(self) -> None:
        raw = "```python   \nx = 1\n```"
        result = extract_clean_code(raw)
        assert result == "x = 1"


# =========================================================================
# 4. State Transition Tests
# =========================================================================
# Both functions are pure (no mutable state). No state transition tests needed.


# =========================================================================
# 5. Integration Tests
# =========================================================================


class TestCodeValidatorIntegrationWithExceptions:
    """Verify integration with Sprint 1 exception hierarchy."""

    # [Subtask 10.2.1, 6.1.4] — InvalidParameterError inherits from SimulatorError
    def test_extract_exception_is_simulator_error(self) -> None:
        from agpds.exceptions import SimulatorError

        with pytest.raises(SimulatorError):
            extract_clean_code("")

    # [Subtask 10.2.2, 6.1.4] — InvalidParameterError inherits from SimulatorError
    def test_validate_exception_is_simulator_error(self) -> None:
        from agpds.exceptions import SimulatorError

        with pytest.raises(SimulatorError):
            validate_generated_code("")


class TestExtractThenValidatePipeline:
    """Integration: extract_clean_code → validate_generated_code pipeline."""

    # [Subtask 10.2.1 + 10.2.2] — full pipeline: fenced valid code
    def test_extract_and_validate_fenced_valid_code(self) -> None:
        raw = f"```python\n{VALID_MINIMAL}\n```"
        extracted = extract_clean_code(raw)
        result = validate_generated_code(extracted)
        assert result.is_valid is True

    # [Subtask 10.2.1 + 10.2.2] — full pipeline: fenced invalid code
    def test_extract_and_validate_fenced_invalid_code(self) -> None:
        raw = "```python\nx = 1\n```"
        extracted = extract_clean_code(raw)
        result = validate_generated_code(extracted)
        assert result.is_valid is False

    # [Subtask 10.2.1 + 10.2.2] — bare valid code
    def test_extract_and_validate_bare_valid_code(self) -> None:
        extracted = extract_clean_code(VALID_FULL)
        result = validate_generated_code(extracted)
        assert result.is_valid is True
