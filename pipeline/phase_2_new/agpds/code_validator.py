"""
Sprint 8 — LLM-generated code validation.

Subtask IDs covered: 10.2.1, 10.2.2

This module provides two public functions:

- ``extract_clean_code`` strips markdown code fences from raw LLM
  responses, matching the fence-stripping semantics already present in
  ``LLMClient.generate_code()`` (subtask 10.2.1).  This standalone
  utility covers the case where a raw response string has already been
  captured (e.g. during a retry iteration) and needs re-cleaning without
  making another LLM call.

- ``validate_generated_code`` performs AST-level structural validation
  that the extracted code satisfies the two §2.5 hard requirements:
  (a) a ``def build_fact_table(...)`` function definition exists, and
  (b) a ``.generate()`` method call exists (subtask 10.2.2).
"""
from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass, field

from agpds.exceptions import InvalidParameterError

logger: logging.Logger = logging.getLogger(__name__)


# =============================================================================
# Data Model
# =============================================================================

@dataclass(frozen=True)
class CodeValidationResult:
    """Result of validating LLM-generated Python code.

    [Subtask 10.2.2]

    Attributes:
        is_valid: ``True`` only when *all* structural checks pass.
        has_build_fact_table: ``True`` if a top-level
            ``def build_fact_table(...)`` is found.
        has_generate_call: ``True`` if a ``.generate()`` attribute call
            is found anywhere in the AST.
        errors: Human-readable descriptions of each failed check.
    """
    is_valid: bool
    has_build_fact_table: bool
    has_generate_call: bool
    errors: list[str] = field(default_factory=list)


# =============================================================================
# Fence-Stripping (10.2.1)
# =============================================================================

# Regex that matches a fenced code block, optionally preceded / followed
# by prose.  Captures the code body inside the outermost fence pair.
_FENCED_BLOCK_RE: re.Pattern[str] = re.compile(
    r"```(?:python)?[ \t]*\n(.*?)```",
    re.DOTALL,
)

# Simpler patterns for leading/trailing fences when there is no prose
_LEADING_FENCE_RE: re.Pattern[str] = re.compile(
    r"^```(?:python)?[ \t]*\n?",
)
_TRAILING_FENCE_RE: re.Pattern[str] = re.compile(
    r"\n?```\s*$",
)


def extract_clean_code(raw_response: str) -> str:
    """Extract clean Python source code from a raw LLM response string.

    [Subtask 10.2.1]

    Handles three cases in priority order:

    1. **Fenced block with surrounding prose** — extracts the content
       between the first matched ````` ``` ````` pair.
    2. **Response is itself a fenced block** (starts with fence) —
       strips leading and trailing fences.
    3. **Bare code** — returns the input unchanged (minus whitespace
       trimming).

    This mirrors the stripping logic in ``LLMClient.generate_code()``
    so that already-captured responses can be re-cleaned without an
    additional LLM round-trip.

    Args:
        raw_response: Raw text returned by the LLM.

    Returns:
        Clean Python source code string (may be empty if the fenced
        block was empty).

    Raises:
        InvalidParameterError: If *raw_response* is ``None`` or not a
            string.
    """
    # ===== Input Validation =====

    # Reject None outright — caller must provide a string
    if raw_response is None:
        raise InvalidParameterError(
            param_name="raw_response",
            value=0.0,
            reason="raw_response must not be None",
        )

    # Reject non-string types so callers get a clear error instead of
    # an AttributeError deep inside regex machinery
    if not isinstance(raw_response, str):
        raise InvalidParameterError(
            param_name="raw_response",
            value=0.0,
            reason=f"raw_response must be a str, got {type(raw_response).__name__}",
        )

    # Reject empty string — there is no code to extract
    if len(raw_response.strip()) == 0:
        raise InvalidParameterError(
            param_name="raw_response",
            value=0.0,
            reason="raw_response must be a non-empty string",
        )

    # ===== Extraction =====

    # Try to find a fenced code block inside surrounding prose first,
    # because the LLM may emit explanatory text around the code
    fenced_match = _FENCED_BLOCK_RE.search(raw_response)
    if fenced_match:
        extracted = fenced_match.group(1)
        logger.debug("Extracted fenced code block (%d chars)", len(extracted))
        return extracted.strip()

    # If the response starts with a fence but the full-block regex did
    # not match (e.g. trailing fence is missing), strip leading fence
    cleaned = raw_response.strip()
    cleaned = _LEADING_FENCE_RE.sub("", cleaned, count=1)
    cleaned = _TRAILING_FENCE_RE.sub("", cleaned, count=1)

    logger.debug(
        "Fence-stripped code via leading/trailing removal (%d chars)",
        len(cleaned),
    )
    return cleaned.strip()


# =============================================================================
# AST Validation (10.2.2)
# =============================================================================

class _GenerateCallVisitor(ast.NodeVisitor):
    """AST visitor that detects ``.generate()`` method calls.

    Walks the full tree and sets ``found`` to ``True`` when it encounters
    an ``ast.Call`` whose ``func`` is an ``ast.Attribute`` with
    ``attr == "generate"``.
    """

    def __init__(self) -> None:
        self.found: bool = False

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802 — ast naming convention
        # Check if the call target is an attribute access named "generate"
        if isinstance(node.func, ast.Attribute) and node.func.attr == "generate":
            self.found = True
        # Continue walking child nodes in case generate() is nested
        self.generic_visit(node)


class _BuildFactTableVisitor(ast.NodeVisitor):
    """AST visitor that detects a top-level ``def build_fact_table(...)``."""

    def __init__(self) -> None:
        self.found: bool = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        # Only match functions named build_fact_table at any nesting depth
        if node.name == "build_fact_table":
            self.found = True
        # Continue walking to catch nested definitions (unlikely but safe)
        self.generic_visit(node)

    # Also handle async defs, though unlikely for SDK scripts
    visit_AsyncFunctionDef = visit_FunctionDef


def validate_generated_code(source_code: str) -> CodeValidationResult:
    """Validate that LLM-generated code meets §2.5 structural requirements.

    [Subtask 10.2.2]

    Performs three checks in order:

    1. **Syntax** — the code must be parseable by ``ast.parse``.
    2. **Function definition** — a ``def build_fact_table(...)`` must exist.
    3. **Generate call** — a ``.generate()`` method call must exist.

    All checks are executed even if earlier ones fail, so the caller
    receives a complete error list in one pass.

    Args:
        source_code: Python source code string to validate.

    Returns:
        A :class:`CodeValidationResult` summarising pass / fail status.

    Raises:
        InvalidParameterError: If *source_code* is ``None`` or empty.
        TypeError: If *source_code* is a non-string, non-None type.
            (FIX: [self-review item 5] — documented asymmetry with
            extract_clean_code which raises InvalidParameterError for
            the same case; this uses TypeError per the locked contract
            table.)
    """
    # ===== Input Validation =====

    # Reject None with the typed exception the contract specifies
    if source_code is None:
        raise InvalidParameterError(
            param_name="source_code",
            value=0.0,
            reason="source_code must not be None",
        )

    # Reject non-string types with TypeError per the locked contract table
    # FIX: [self-review item 5] — asymmetry documented; TypeError is
    # intentional here per Message 1 contract row "validate_generated_code(42)"
    if not isinstance(source_code, str):
        raise TypeError(
            f"source_code must be a str, got {type(source_code).__name__}"
        )

    # Reject empty string — no code means nothing to validate
    if len(source_code.strip()) == 0:
        raise InvalidParameterError(
            param_name="source_code",
            value=0.0,
            reason="source_code must be a non-empty string",
        )

    # ===== Phase 1: Syntax Check =====

    errors: list[str] = []
    tree: ast.Module | None = None

    # Parse the source to build an AST; SyntaxError means the LLM
    # produced unparseable code, which we report without re-raising
    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        errors.append(
            f"SyntaxError at line {exc.lineno}: {exc.msg}"
        )
        logger.debug("Code failed syntax check: %s", exc.msg)

    # ===== Phase 2: Structural Checks (only if syntax passed) =====

    has_build_fn = False
    has_generate = False

    if tree is not None:
        # Walk AST for build_fact_table function definition
        fn_visitor = _BuildFactTableVisitor()
        fn_visitor.visit(tree)
        has_build_fn = fn_visitor.found

        # Report missing build_fact_table as an error
        if not has_build_fn:
            errors.append(
                "Missing required function: 'def build_fact_table(...)'. "
                "§2.5 requires the script to define this function."
            )

        # Walk AST for .generate() call
        gen_visitor = _GenerateCallVisitor()
        gen_visitor.visit(tree)
        has_generate = gen_visitor.found

        # Report missing .generate() as an error
        if not has_generate:
            errors.append(
                "Missing required call: '.generate()'. "
                "§2.5 constraint 6 requires the script to call sim.generate()."
            )

    # ===== Build Result =====

    is_valid = len(errors) == 0

    logger.debug(
        "Code validation result: valid=%s, has_build_fn=%s, has_generate=%s, "
        "error_count=%d",
        is_valid, has_build_fn, has_generate, len(errors),
    )

    return CodeValidationResult(
        is_valid=is_valid,
        has_build_fact_table=has_build_fn,
        has_generate_call=has_generate,
        errors=errors,
    )
