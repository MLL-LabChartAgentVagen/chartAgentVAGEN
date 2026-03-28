"""
Test suite for agpds.prompt — Sprint 8, Subtask 10.1.1.

Covers:
  - SYSTEM_PROMPT_TEMPLATE constant structure (§2.5 compliance)
  - render_system_prompt() contract tests, input validation, output
    correctness, and idempotency.
"""
from __future__ import annotations

import pytest

from agpds.exceptions import InvalidParameterError
from agpds.prompt import SYSTEM_PROMPT_TEMPLATE, render_system_prompt


# =========================================================================
# Fixtures & Constants
# =========================================================================

VALID_SCENARIO = (
    "Title: 2024 Beijing Retail Sales\n"
    "target_rows: 1000\n"
    "Entities: [Store_A, Store_B, Store_C]\n"
    "Metrics: revenue (CNY), footfall (count)\n"
    "Temporal: daily, 2024-01 to 2024-12"
)

MINIMAL_SCENARIO = "Title: Test"

# Sections that §2.5 requires to appear in the template
REQUIRED_SECTIONS = [
    "SYSTEM:",
    "AVAILABLE SDK METHODS",
    "HARD CONSTRAINTS",
    "SOFT GUIDELINES",
    "=== ONE-SHOT EXAMPLE ===",
    "def build_fact_table",
    "sim.generate()",
    "=== YOUR TASK ===",
    "[AGENT CODE]",
]

# Hard constraint numbers 1–9 must all appear
HARD_CONSTRAINT_PREFIXES = [f"{i}." for i in range(1, 10)]

# FIX: [self-review item 4] — exhaustive list of §2.5 verbatim phrases
# for stronger template fidelity verification
SDK_METHOD_SIGNATURES = [
    "sim.add_category(name, values, weights, group, parent=None)",
    "sim.add_temporal(name, start, end, freq, derive=[])",
    "sim.add_measure(name, family, param_model, scale=None)",
    "sim.add_measure_structural(name, formula, effects={}, noise={})",
    "sim.declare_orthogonal(group_a, group_b, rationale)",
    "sim.add_group_dependency(child_root, on, conditional_weights)",
    "sim.inject_pattern(type, target, col, params)",
    "sim.set_realism(missing_rate, dirty_rate, censoring=None)",
]

ONE_SHOT_KEY_LINES = [
    "from chartagent.synth import FactTableSimulator",
    "sim = FactTableSimulator(target_rows=500, seed=seed)",
    "return sim.generate()",
    'group="entity"',
    'family="lognormal"',
    '"intercept": 2.8',
    '"severity_surcharge"',
    "declare_orthogonal",
    "add_group_dependency",
    "inject_pattern",
]


# =========================================================================
# 1. Contract Tests
# =========================================================================


class TestRenderSystemPromptContract:
    """Contract table rows from Message 1 for render_system_prompt."""

    # [Subtask 10.1.1] — valid scenario, rich content
    def test_valid_scenario_returns_string_with_all_sections(self) -> None:
        """Contract row: render_system_prompt(valid_ctx) → string with all §2.5 sections."""
        rendered = render_system_prompt(VALID_SCENARIO)

        for section in REQUIRED_SECTIONS:
            assert section in rendered, (
                f"Rendered prompt missing required §2.5 section: '{section}'"
            )

    # [Subtask 10.1.1] — valid scenario, placeholder replaced
    def test_valid_scenario_replaces_placeholder(self) -> None:
        """Contract row: {scenario_context} is no longer present in result."""
        rendered = render_system_prompt(VALID_SCENARIO)
        assert "{scenario_context}" not in rendered

    # [Subtask 10.1.1] — valid scenario, injected content present
    def test_valid_scenario_contains_injected_context(self) -> None:
        """Contract row: result contains the injected scenario text."""
        rendered = render_system_prompt(VALID_SCENARIO)
        assert "2024 Beijing Retail Sales" in rendered
        assert "target_rows: 1000" in rendered

    # [Subtask 10.1.1] — empty string raises
    def test_empty_string_raises_invalid_parameter_error(self) -> None:
        """Contract row: render_system_prompt('') → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            render_system_prompt("")

    # [Subtask 10.1.1] — None raises
    def test_none_raises_invalid_parameter_error(self) -> None:
        """Contract row: render_system_prompt(None) → InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            render_system_prompt(None)  # type: ignore[arg-type]

    # [Subtask 10.1.1] — minimal scenario
    def test_minimal_scenario_appears_in_task_section(self) -> None:
        """Contract row: render('Title: Test') → result contains 'Title: Test' in YOUR TASK section."""
        rendered = render_system_prompt(MINIMAL_SCENARIO)
        # Locate the YOUR TASK section and verify the context is there
        task_pos = rendered.index("=== YOUR TASK ===")
        after_task = rendered[task_pos:]
        assert "Title: Test" in after_task

    # [Subtask 10.1.1] — idempotency
    def test_idempotency_same_input_produces_identical_output(self) -> None:
        """Contract row: same input called twice → identical strings."""
        r1 = render_system_prompt(VALID_SCENARIO)
        r2 = render_system_prompt(VALID_SCENARIO)
        assert r1 == r2


class TestSystemPromptTemplateConstant:
    """Contract table rows for the static SYSTEM_PROMPT_TEMPLATE constant."""

    # [Subtask 10.1.1] — template contains all §2.5 sections
    def test_template_contains_all_required_sections(self) -> None:
        """Contract row: SYSTEM_PROMPT_TEMPLATE contains SYSTEM, SDK ref, constraints, example, task."""
        for section in REQUIRED_SECTIONS:
            assert section in SYSTEM_PROMPT_TEMPLATE, (
                f"Template missing §2.5 section: '{section}'"
            )

    # [Subtask 10.1.1] — exactly one placeholder
    def test_template_has_exactly_one_scenario_placeholder(self) -> None:
        """Contract row: template.count('{scenario_context}') == 1."""
        count = SYSTEM_PROMPT_TEMPLATE.count("{scenario_context}")
        assert count == 1, f"Expected 1 placeholder, found {count}"

    # [Subtask 10.1.1] — all 9 hard constraints present
    def test_template_contains_all_nine_hard_constraints(self) -> None:
        """Verify that HARD CONSTRAINTS items 1 through 9 appear."""
        for prefix in HARD_CONSTRAINT_PREFIXES:
            assert prefix in SYSTEM_PROMPT_TEMPLATE, (
                f"Template missing hard constraint '{prefix}'"
            )

    # FIX: [self-review item 4] — verify all SDK method signatures verbatim
    def test_template_contains_all_sdk_method_signatures(self) -> None:
        """Verify each SDK method signature from §2.5 appears verbatim."""
        for sig in SDK_METHOD_SIGNATURES:
            assert sig in SYSTEM_PROMPT_TEMPLATE, (
                f"Template missing SDK method signature: '{sig}'"
            )

    # FIX: [self-review item 4] — verify one-shot example key lines
    def test_template_one_shot_example_key_lines(self) -> None:
        """Verify key lines from the §2.5 one-shot example appear."""
        for line in ONE_SHOT_KEY_LINES:
            assert line in SYSTEM_PROMPT_TEMPLATE, (
                f"Template missing one-shot line: '{line}'"
            )

    # FIX: [self-review item 4] — verify structural ordering of sections
    def test_template_section_ordering(self) -> None:
        """Verify §2.5 sections appear in correct order."""
        t = SYSTEM_PROMPT_TEMPLATE
        # Use rindex for [AGENT CODE] because it appears twice: once in
        # the one-shot example and once in the YOUR TASK section; we
        # care about the final occurrence (the user's task section)
        positions = [
            t.index("SYSTEM:"),
            t.index("AVAILABLE SDK METHODS"),
            t.index("HARD CONSTRAINTS"),
            t.index("SOFT GUIDELINES"),
            t.index("=== ONE-SHOT EXAMPLE ==="),
            t.index("=== YOUR TASK ==="),
            t.rindex("[AGENT CODE]"),
        ]
        assert positions == sorted(positions), (
            "Template sections are out of order relative to §2.5"
        )


# =========================================================================
# 2. Input Validation Tests
# =========================================================================


class TestRenderSystemPromptInputValidation:
    """Exhaustive input validation for render_system_prompt."""

    # [Subtask 10.1.1] — whitespace-only string treated as empty
    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(InvalidParameterError):
            render_system_prompt("   \n\t  ")

    # [Subtask 10.1.1] — wrong type: integer
    @pytest.mark.parametrize("bad_input", [42, 3.14, [], {}, True])
    def test_non_string_type_raises(self, bad_input: object) -> None:
        with pytest.raises(InvalidParameterError):
            render_system_prompt(bad_input)  # type: ignore[arg-type]


# =========================================================================
# 3. Output Correctness Tests
# =========================================================================


class TestRenderSystemPromptOutputCorrectness:
    """Verify return value properties."""

    # [Subtask 10.1.1] — return type is always str
    def test_return_type_is_str(self) -> None:
        result = render_system_prompt(VALID_SCENARIO)
        assert isinstance(result, str)

    # [Subtask 10.1.1] — rendered is longer than original template because
    # the scenario context replaces the short placeholder
    def test_rendered_length_exceeds_scenario_context_length(self) -> None:
        rendered = render_system_prompt(VALID_SCENARIO)
        assert len(rendered) > len(VALID_SCENARIO)

    # [Subtask 10.1.1] — literal braces in the Python example code survive
    def test_literal_braces_preserved_in_one_shot_example(self) -> None:
        rendered = render_system_prompt(VALID_SCENARIO)
        assert "{intercept, effects}" in rendered
        assert "effects={}" in rendered

    # [Subtask 10.1.1] — supported distributions list present
    def test_supported_distributions_listed(self) -> None:
        rendered = render_system_prompt(MINIMAL_SCENARIO)
        for dist in ("gaussian", "lognormal", "gamma", "beta",
                     "uniform", "poisson", "exponential", "mixture"):
            assert dist in rendered, f"Missing distribution '{dist}'"

    # [Subtask 10.1.1] — pattern types present
    def test_pattern_types_listed(self) -> None:
        rendered = render_system_prompt(MINIMAL_SCENARIO)
        for pt in ("outlier_entity", "trend_break", "ranking_reversal",
                    "dominance_shift", "convergence", "seasonal_anomaly"):
            assert pt in rendered, f"Missing pattern type '{pt}'"

    # [Subtask 10.1.1] — scenario context with special characters
    def test_scenario_with_special_characters(self) -> None:
        ctx = "Title: Test {with} $pecial & <chars>"
        rendered = render_system_prompt(ctx)
        assert "Test {with} $pecial & <chars>" in rendered

    # [Subtask 10.1.1] — one-shot example contains full hospital example
    def test_one_shot_example_contains_hospital_scenario(self) -> None:
        rendered = render_system_prompt(MINIMAL_SCENARIO)
        assert "2024 Shanghai Emergency Records" in rendered
        assert "Xiehe" in rendered
        assert "wait_minutes" in rendered


# =========================================================================
# 4. State Transition Tests
# =========================================================================
# render_system_prompt is a pure function with no state. The template
# constant is module-level and immutable. No state tests needed.


# =========================================================================
# 5. Integration Tests
# =========================================================================


class TestPromptIntegrationWithExceptions:
    """Verify that InvalidParameterError from Sprint 1 is correctly raised."""

    # [Subtask 10.1.1, 6.1.4] — integration: prompt → exceptions
    def test_raised_exception_is_from_sprint1_hierarchy(self) -> None:
        from agpds.exceptions import SimulatorError

        with pytest.raises(SimulatorError):
            render_system_prompt("")

    # [Subtask 10.1.1, 6.1.4] — exception carries param_name attribute
    def test_exception_carries_param_name(self) -> None:
        with pytest.raises(InvalidParameterError) as exc_info:
            render_system_prompt("")
        assert exc_info.value.param_name == "scenario_context"


# FIX: [self-review item 3] — LLMClient integration verification tests
class TestLLMClientFenceStrippingEquivalence:
    """Verify that extract_clean_code is behaviorally equivalent to
    LLMClient.generate_code fence-stripping (exit gate items 7-8)."""

    # [Subtask 10.2.1] — fence-stripping regex equivalence
    @pytest.mark.parametrize("raw,expected", [
        ("bare code", "bare code"),
        ("```python\nx = 1\n```", "x = 1"),
        ("```\nx = 1\n```", "x = 1"),
        ("```python  \nx = 1\n```", "x = 1"),
    ])
    def test_extract_matches_llm_client_stripping(
        self, raw: str, expected: str
    ) -> None:
        """Verify extract_clean_code produces same result as LLMClient regex."""
        import re
        from agpds.code_validator import extract_clean_code

        # LLMClient.generate_code regex (from uploaded llm_client.py)
        llm_cleaned = raw.strip()
        llm_cleaned = re.sub(
            r"^```(?:python)?[ \t]*\n?", "", llm_cleaned, count=1
        )
        llm_cleaned = re.sub(r"\n```\s*$", "", llm_cleaned, count=1)
        llm_cleaned = llm_cleaned.strip()

        # Our extract_clean_code
        ecv_cleaned = extract_clean_code(raw)

        assert ecv_cleaned == llm_cleaned, (
            f"Behavioral divergence: LLM={repr(llm_cleaned)}, "
            f"extract={repr(ecv_cleaned)}"
        )
