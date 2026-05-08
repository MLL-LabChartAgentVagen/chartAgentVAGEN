"""
Test suite for Phase 1: Scenario Contextualization — STRICT edition.

Tests:
 1.  Prompt — domain metadata fields serialized into user prompt
 2.  Prompt — {domain_json} placeholder is replaced; no unreplaced braces left
 3.  Prompt — one-shot example and system prompt constant integrity
 4.  Validation — valid scenario passes (happy path, all 6 fields)
 5.  Validation — each of the 6 required fields individually missing
 6.  Validation — empty and whitespace-only scenario_title / data_context
 7.  Validation — non-dict and None inputs
 8.  Validation — key_entities count boundary values (2→fail, 3→pass, 8→pass, 9→fail)
 9.  Validation — key_metrics count boundary values (1→fail, 2→pass, 5→pass, 6→fail)
10.  Validation — target_rows boundaries (99→fail, 100→pass, 3000→pass, 3001→fail)
11.  Validation — target_rows type: float passes, string fails
12.  Validation — all 6 valid temporal_granularity values pass; invalid value fails
13.  generate() — LLM called exactly once on first-attempt success
14.  generate() — retry succeeds on second attempt (first invalid, second valid)
15.  generate() — soft failure: dict response with _validation_warnings after all retries
16.  generate() — hard failure: ValueError raised when non-dict persists after retries
17.  generate() — max_retries=0 limits LLM calls to exactly 1
17.  Diversity tracker — accumulates titles/contexts; skips blank fields
18.  deduplicate_scenario_records — scope and domain protection

All tests are isolated — no LLM calls, no embedding model calls.

Run:
    python -m pipeline.phase_1.tests.test_scenario_contextualizer
"""

import sys
import json
import warnings
from unittest.mock import patch, call


# ================================================================
# Shared fixtures
# ================================================================

VALID_SCENARIO = {
    "scenario_title": "2024 H1 Shanghai Metro Ridership & Operations Log",
    "data_context": (
        "Shanghai Transport Commission collected daily ridership and "
        "operational performance data across core metro lines over "
        "January–June 2024 to optimize peak-hour scheduling."
    ),
    "temporal_granularity": "daily",
    "key_entities": [
        "Line 1 (Xinzhuang–Fujin Rd)",
        "Line 2 (Pudong Intl Airport–East Xujing)",
        "Line 8 (Shiguang Rd–Shendu Hwy)",
        "Line 9 (Songjiang South–Caolu)",
        "Line 10 (Hongqiao Airport–New Jiangwan City)",
    ],
    "key_metrics": [
        {"name": "daily_ridership", "unit": "10k passengers", "range": [5, 120]},
        {"name": "on_time_rate", "unit": "%", "range": [85.0, 99.9]},
        {"name": "equipment_failures", "unit": "count", "range": [0, 5]},
    ],
    "target_rows": 900,
}

DOMAIN_SAMPLE = {
    "id": "dom_001",
    "name": "Urban rail transit scheduling",
    "topic": "Transportation & Logistics",
    "complexity_tier": "complex",
    "typical_entities_hint": ["metro lines", "stations", "time slots"],
    "typical_metrics_hint": [
        {"name": "ridership", "unit": "10k passengers"},
        {"name": "on_time_rate", "unit": "%"},
    ],
    "temporal_granularity_hint": "daily",
}


class DummyLLM:
    """LLM stub that always returns an empty dict (never called in prompt tests)."""
    def generate_json(self, **kwargs):
        return {}


def _make_llm_sequence(*responses):
    """Return a mock LLM that yields responses in order, then repeats the last."""
    idx = [0]
    class SequenceLLM:
        def generate_json(self, **kwargs):
            r = responses[min(idx[0], len(responses) - 1)]
            idx[0] += 1
            return r
    return SequenceLLM(), idx


def _make_counting_llm(response):
    """Return (llm, call_counter) where call_counter[0] is incremented per call."""
    count = [0]
    class CountingLLM:
        def generate_json(self, **kwargs):
            count[0] += 1
            return response
    return CountingLLM(), count


# ================================================================
# Import under test
# ================================================================

try:
    from pipeline.phase_1.scenario_contextualizer import (
        ScenarioContextualizer,
        deduplicate_scenario_records,
        SCENARIO_SYSTEM_PROMPT,
        SCENARIO_USER_PROMPT_TEMPLATE,
        VALID_GRANULARITIES,
    )
except ImportError:
    # Fallback: run from pipeline/ directory
    from phase_1.scenario_contextualizer import (
        ScenarioContextualizer,
        deduplicate_scenario_records,
        SCENARIO_SYSTEM_PROMPT,
        SCENARIO_USER_PROMPT_TEMPLATE,
        VALID_GRANULARITIES,
    )


# ================================================================
# Test 1: User prompt contains all domain metadata fields
# ================================================================
print("=" * 60)
print("Test 1: User prompt contains all domain metadata fields")
print("=" * 60)

try:
    ctx = ScenarioContextualizer(DummyLLM())
    user_prompt = ctx._build_user_prompt(DOMAIN_SAMPLE)

    assert "Urban rail transit scheduling" in user_prompt, "domain name missing"
    assert "Transportation & Logistics" in user_prompt, "topic missing"
    assert "complex" in user_prompt, "complexity_tier missing"
    assert "metro lines" in user_prompt, "typical_entities_hint missing"
    assert "ridership" in user_prompt, "typical_metrics_hint name missing"
    assert "10k passengers" in user_prompt, "typical_metrics_hint unit missing"
    assert "daily" in user_prompt, "temporal_granularity_hint missing"

    print(f"  ✓ All 7 domain metadata fields present in user prompt")
    print(f"  ✓ Prompt length: {len(user_prompt)} chars")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 2: Placeholder {domain_json} is replaced; no unresolved braces
# ================================================================
print("=" * 60)
print("Test 2: {domain_json} placeholder replaced; no unresolved braces")
print("=" * 60)

try:
    ctx = ScenarioContextualizer(DummyLLM())
    user_prompt = ctx._build_user_prompt(DOMAIN_SAMPLE)

    # The literal placeholder must NOT appear in the rendered prompt
    assert "{domain_json}" not in user_prompt, (
        "Literal '{domain_json}' still present — format() failed"
    )

    # The serialized JSON must be valid (parse the injected portion)
    domain_json_str = json.dumps(DOMAIN_SAMPLE, indent=2, ensure_ascii=False)
    assert domain_json_str in user_prompt, "Serialized domain JSON not found in prompt"

    # Verify the injected JSON is syntactically valid by re-parsing it
    parsed = json.loads(domain_json_str)
    assert parsed["name"] == DOMAIN_SAMPLE["name"]

    print(f"  ✓ {{domain_json}} placeholder is fully replaced")
    print(f"  ✓ Injected domain JSON is valid and parseable")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 3: System prompt and user prompt template integrity
# ================================================================
print("=" * 60)
print("Test 3: System prompt and user prompt template integrity")
print("=" * 60)

try:
    # System prompt must be a non-empty string
    assert isinstance(SCENARIO_SYSTEM_PROMPT, str), "SCENARIO_SYSTEM_PROMPT is not str"
    assert len(SCENARIO_SYSTEM_PROMPT.strip()) > 50, (
        f"System prompt suspiciously short: {len(SCENARIO_SYSTEM_PROMPT)} chars"
    )

    # The 8 required rules must be present in the system prompt
    for rule_fragment in [
        "scenario_title",
        "data_context",
        "key_entities",
        "key_metrics",
        "temporal_granularity",
        "target_rows",
        "100-3000",
        "Output strictly valid JSON",
    ]:
        assert rule_fragment in SCENARIO_SYSTEM_PROMPT, (
            f"Rule fragment missing from system prompt: '{rule_fragment}'"
        )

    # User prompt template must contain the {domain_json} placeholder
    assert isinstance(SCENARIO_USER_PROMPT_TEMPLATE, str)
    assert "{domain_json}" in SCENARIO_USER_PROMPT_TEMPLATE, (
        "Template missing '{domain_json}' placeholder"
    )

    # One-shot example must be present
    assert "ONE-SHOT EXAMPLE" in SCENARIO_USER_PROMPT_TEMPLATE, (
        "One-shot example section missing"
    )
    assert "Shanghai Metro" in SCENARIO_USER_PROMPT_TEMPLATE, (
        "One-shot example content missing"
    )
    assert "YOUR TASK" in SCENARIO_USER_PROMPT_TEMPLATE, (
        "Task instruction section missing"
    )

    print(f"  ✓ System prompt: {len(SCENARIO_SYSTEM_PROMPT)} chars, all 8 rule "
          f"fragments present")
    print(f"  ✓ User prompt template: placeholder, one-shot, and task sections intact")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 4: validate_output — valid scenario passes (happy path)
# ================================================================
print("=" * 60)
print("Test 4: validate_output — valid scenario passes (happy path)")
print("=" * 60)

try:
    is_valid, errors = ScenarioContextualizer.validate_output(VALID_SCENARIO)

    assert is_valid, f"Expected valid, got errors: {errors}"
    assert errors == [], f"Expected empty errors list, got: {errors}"

    print(f"  ✓ Valid scenario passes with zero errors")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 5: validate_output — each of the 6 required fields missing
# ================================================================
print("=" * 60)
print("Test 5: validate_output — each required field missing individually")
print("=" * 60)

try:
    required_fields = [
        "scenario_title", "data_context", "key_entities",
        "key_metrics", "temporal_granularity", "target_rows",
    ]

    for field in required_fields:
        truncated = {k: v for k, v in VALID_SCENARIO.items() if k != field}
        is_valid, errors = ScenarioContextualizer.validate_output(truncated)
        assert not is_valid, f"Expected invalid when '{field}' is missing, got valid"
        assert any(field in e for e in errors), (
            f"Error message does not mention missing field '{field}': {errors}"
        )
        print(f"  ✓ Missing '{field}' → invalid, error mentions field name")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 6: validate_output — empty / whitespace-only title and context
# ================================================================
print("=" * 60)
print("Test 6: validate_output — empty/whitespace scenario_title and data_context")
print("=" * 60)

try:
    # Empty string title
    bad = {**VALID_SCENARIO, "scenario_title": ""}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid, "Empty scenario_title should be invalid"
    assert any("scenario_title" in e for e in errors)
    print(f"  ✓ scenario_title='' → invalid")

    # Whitespace-only title
    bad = {**VALID_SCENARIO, "scenario_title": "   "}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid, "Whitespace-only scenario_title should be invalid"
    print(f"  ✓ scenario_title='   ' → invalid")

    # Empty string context
    bad = {**VALID_SCENARIO, "data_context": ""}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid, "Empty data_context should be invalid"
    assert any("data_context" in e for e in errors)
    print(f"  ✓ data_context='' → invalid")

    # Whitespace-only context
    bad = {**VALID_SCENARIO, "data_context": "\t\n  "}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid, "Whitespace-only data_context should be invalid"
    print(f"  ✓ data_context='\\t\\n  ' → invalid")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 7: validate_output — non-dict and None inputs
# ================================================================
print("=" * 60)
print("Test 7: validate_output — non-dict and None inputs")
print("=" * 60)

try:
    for bad_input, label in [
        ("not a dict", "string"),
        (["list", "of", "items"], "list"),
        (42, "int"),
        (None, "None"),
        (True, "bool"),
    ]:
        is_valid, errors = ScenarioContextualizer.validate_output(bad_input)
        assert not is_valid, f"Expected invalid for {label} input, got valid"
        assert len(errors) > 0, f"Expected error message for {label} input"
        print(f"  ✓ Input={label!r} → invalid: {errors[0]}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 8: validate_output — key_entities count boundary values
# ================================================================
print("=" * 60)
print("Test 8: validate_output — key_entities count boundaries (2,3,8,9)")
print("=" * 60)

try:
    def make_entities(n):
        return [f"Entity_{i}" for i in range(n)]

    # Below min: 2 entities → invalid
    bad = {**VALID_SCENARIO, "key_entities": make_entities(2)}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid, "2 entities should be invalid (min=3)"
    assert any("key_entities" in e for e in errors)
    print(f"  ✓ key_entities count=2 → invalid (min is 3)")

    # Exactly at min: 3 entities → valid
    ok = {**VALID_SCENARIO, "key_entities": make_entities(3)}
    is_valid, errors = ScenarioContextualizer.validate_output(ok)
    assert is_valid, f"3 entities should be valid, got errors: {errors}"
    print(f"  ✓ key_entities count=3 → valid (at min boundary)")

    # Exactly at max: 8 entities → valid
    ok = {**VALID_SCENARIO, "key_entities": make_entities(8)}
    is_valid, errors = ScenarioContextualizer.validate_output(ok)
    assert is_valid, f"8 entities should be valid, got errors: {errors}"
    print(f"  ✓ key_entities count=8 → valid (at max boundary)")

    # Above max: 9 entities → invalid
    bad = {**VALID_SCENARIO, "key_entities": make_entities(9)}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid, "9 entities should be invalid (max=8)"
    assert any("key_entities" in e for e in errors)
    print(f"  ✓ key_entities count=9 → invalid (max is 8)")

    # Non-list key_entities
    bad = {**VALID_SCENARIO, "key_entities": "not a list"}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid
    print(f"  ✓ key_entities=string → invalid (must be list)")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 9: validate_output — key_metrics count boundary values
# ================================================================
print("=" * 60)
print("Test 9: validate_output — key_metrics count boundaries (1,2,5,6)")
print("=" * 60)

try:
    def make_metrics(n):
        return [{"name": f"metric_{i}", "unit": "unit"} for i in range(n)]

    # Below min: 1 metric → invalid
    bad = {**VALID_SCENARIO, "key_metrics": make_metrics(1)}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid, "1 metric should be invalid (min=2)"
    assert any("key_metrics" in e for e in errors)
    print(f"  ✓ key_metrics count=1 → invalid (min is 2)")

    # Exactly at min: 2 metrics → valid
    ok = {**VALID_SCENARIO, "key_metrics": make_metrics(2)}
    is_valid, errors = ScenarioContextualizer.validate_output(ok)
    assert is_valid, f"2 metrics should be valid, got errors: {errors}"
    print(f"  ✓ key_metrics count=2 → valid (at min boundary)")

    # Exactly at max: 5 metrics → valid
    ok = {**VALID_SCENARIO, "key_metrics": make_metrics(5)}
    is_valid, errors = ScenarioContextualizer.validate_output(ok)
    assert is_valid, f"5 metrics should be valid, got errors: {errors}"
    print(f"  ✓ key_metrics count=5 → valid (at max boundary)")

    # Above max: 6 metrics → invalid
    bad = {**VALID_SCENARIO, "key_metrics": make_metrics(6)}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid, "6 metrics should be invalid (max=5)"
    assert any("key_metrics" in e for e in errors)
    print(f"  ✓ key_metrics count=6 → invalid (max is 5)")

    # Non-list key_metrics
    bad = {**VALID_SCENARIO, "key_metrics": {"name": "m", "unit": "u"}}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid
    print(f"  ✓ key_metrics=dict → invalid (must be list)")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 10: validate_output — target_rows boundary values
# ================================================================
print("=" * 60)
print("Test 10: validate_output — target_rows boundaries (99,100,3000,3001)")
print("=" * 60)

try:
    # Just below min: 99 → invalid
    bad = {**VALID_SCENARIO, "target_rows": 99}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid, "target_rows=99 should be invalid (min=100)"
    assert any("target_rows" in e for e in errors)
    print(f"  ✓ target_rows=99 → invalid (min is 100)")

    # Exactly at min: 100 → valid
    ok = {**VALID_SCENARIO, "target_rows": 100}
    is_valid, errors = ScenarioContextualizer.validate_output(ok)
    assert is_valid, f"target_rows=100 should be valid, got errors: {errors}"
    print(f"  ✓ target_rows=100 → valid (at min boundary)")

    # Exactly at max: 3000 → valid
    ok = {**VALID_SCENARIO, "target_rows": 3000}
    is_valid, errors = ScenarioContextualizer.validate_output(ok)
    assert is_valid, f"target_rows=3000 should be valid, got errors: {errors}"
    print(f"  ✓ target_rows=3000 → valid (at max boundary)")

    # Just above max: 3001 → invalid
    bad = {**VALID_SCENARIO, "target_rows": 3001}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid, "target_rows=3001 should be invalid (max=3000)"
    assert any("target_rows" in e for e in errors)
    print(f"  ✓ target_rows=3001 → invalid (max is 3000)")

    # Float in valid range → valid (isinstance float check)
    ok = {**VALID_SCENARIO, "target_rows": 500.0}
    is_valid, errors = ScenarioContextualizer.validate_output(ok)
    assert is_valid, f"target_rows=500.0 (float) should be valid, got errors: {errors}"
    print(f"  ✓ target_rows=500.0 (float) → valid")

    # String type → invalid
    bad = {**VALID_SCENARIO, "target_rows": "900"}
    is_valid, errors = ScenarioContextualizer.validate_output(bad)
    assert not is_valid, "target_rows='900' (str) should be invalid"
    assert any("target_rows" in e for e in errors)
    print(f"  ✓ target_rows='900' (str) → invalid (must be numeric)")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 11: validate_output — temporal_granularity values
# ================================================================
print("=" * 60)
print("Test 11: validate_output — all 6 valid granularities + invalid")
print("=" * 60)

try:
    valid_granularities = ["hourly", "daily", "weekly", "monthly", "quarterly", "yearly"]

    # Verify VALID_GRANULARITIES constant matches the spec exactly
    assert VALID_GRANULARITIES == set(valid_granularities), (
        f"VALID_GRANULARITIES mismatch: {VALID_GRANULARITIES} vs {set(valid_granularities)}"
    )

    for granularity in valid_granularities:
        ok = {**VALID_SCENARIO, "temporal_granularity": granularity}
        is_valid, errors = ScenarioContextualizer.validate_output(ok)
        assert is_valid, (
            f"'{granularity}' should be valid granularity, got errors: {errors}"
        )
        print(f"  ✓ '{granularity}' → valid")

    # Invalid values
    for invalid_gran in ["biweekly", "annual", "realtime", "DAILY", "", None]:
        bad = {**VALID_SCENARIO, "temporal_granularity": invalid_gran}
        is_valid, errors = ScenarioContextualizer.validate_output(bad)
        assert not is_valid, (
            f"'{invalid_gran}' should be invalid granularity, got valid"
        )
    print(f"  ✓ Invalid granularities (biweekly, annual, DAILY, '', None) → all invalid")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 12: generate() — LLM called exactly once on first success
# ================================================================
print("=" * 60)
print("Test 12: generate() — LLM called exactly once on first-attempt success")
print("=" * 60)

try:
    llm, count = _make_counting_llm(VALID_SCENARIO.copy())
    ctx = ScenarioContextualizer(llm, max_retries=2)

    result = ctx.generate(DOMAIN_SAMPLE)

    assert result == VALID_SCENARIO, f"Unexpected result: {result}"
    assert count[0] == 1, f"Expected 1 LLM call, got {count[0]}"
    assert "_validation_warnings" not in result, (
        "No warnings expected on successful first attempt"
    )
    print(f"  ✓ Result matches valid scenario")
    print(f"  ✓ Exactly 1 LLM call made (no unnecessary retries)")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 13: generate() — retry: first invalid, second valid
# ================================================================
print("=" * 60)
print("Test 13: generate() — retry succeeds on second attempt")
print("=" * 60)

try:
    # First response: invalid (missing temporal_granularity)
    invalid_first = {k: v for k, v in VALID_SCENARIO.items()
                     if k != "temporal_granularity"}
    llm, idx = _make_llm_sequence(invalid_first, VALID_SCENARIO.copy())
    ctx = ScenarioContextualizer(llm, max_retries=1)

    result = ctx.generate(DOMAIN_SAMPLE)

    assert idx[0] == 2, f"Expected 2 LLM calls (1 retry), got {idx[0]}"
    assert result.get("temporal_granularity") == "daily", (
        "Second (valid) response should be returned"
    )
    assert "_validation_warnings" not in result, (
        "No warnings expected — second attempt succeeded"
    )
    print(f"  ✓ LLM called twice (1 retry)")
    print(f"  ✓ Second (valid) response returned, no warnings")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 14: generate() — soft failure returns dict with _validation_warnings
# ================================================================
print("=" * 60)
print("Test 14: generate() — soft failure: dict with _validation_warnings")
print("=" * 60)

try:
    # LLM always returns an invalid-but-dict response (target_rows out of range)
    always_invalid_dict = {**VALID_SCENARIO, "target_rows": 9999}
    llm, count = _make_counting_llm(always_invalid_dict)
    ctx = ScenarioContextualizer(llm, max_retries=2)

    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        result = ctx.generate(DOMAIN_SAMPLE)

    # Should return a dict (soft failure)
    assert isinstance(result, dict), f"Expected dict soft-failure, got {type(result)}"

    # _validation_warnings key must be present
    assert "_validation_warnings" in result, (
        "Expected '_validation_warnings' in soft-failure result"
    )
    assert isinstance(result["_validation_warnings"], list)
    assert len(result["_validation_warnings"]) > 0, "Warning list should not be empty"

    # A Python warning should have been issued
    assert len(caught_warnings) > 0, "Expected at least one Python warning to be issued"

    # LLM should have been called max_retries+1 times
    assert count[0] == 3, (
        f"Expected 3 LLM calls (max_retries=2), got {count[0]}"
    )

    print(f"  ✓ Soft failure returned dict with _validation_warnings")
    print(f"  ✓ {len(result['_validation_warnings'])} warning(s): "
          f"{result['_validation_warnings']}")
    print(f"  ✓ Python warnings.warn() called: {len(caught_warnings)} warning(s)")
    print(f"  ✓ LLM called exactly 3 times (max_retries=2)")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 15: generate() — hard failure: ValueError when non-dict persists
# ================================================================
print("=" * 60)
print("Test 15: generate() — hard failure: ValueError on non-dict response")
print("=" * 60)

try:
    # LLM always returns a plain string (not a dict)
    llm, count = _make_counting_llm("I cannot generate a valid scenario.")
    ctx = ScenarioContextualizer(llm, max_retries=1)

    raised = False
    try:
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            ctx.generate(DOMAIN_SAMPLE)
    except ValueError as ve:
        raised = True
        error_msg = str(ve)
        assert "attempts" in error_msg.lower() or "failed" in error_msg.lower(), (
            f"ValueError message should describe retry exhaustion: {error_msg}"
        )
        print(f"  ✓ ValueError raised: {error_msg[:80]}...")

    assert raised, "Expected ValueError when all retries return non-dict"

    # LLM should have been called max_retries+1 times
    assert count[0] == 2, (
        f"Expected 2 LLM calls (max_retries=1), got {count[0]}"
    )
    print(f"  ✓ LLM called exactly 2 times before hard failure")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 16: generate() — max_retries=0 means exactly 1 LLM call
# ================================================================
print("=" * 60)
print("Test 16: generate() — max_retries=0 limits LLM calls to exactly 1")
print("=" * 60)

try:
    # Successful on first call
    llm_ok, count_ok = _make_counting_llm(VALID_SCENARIO.copy())
    ctx_ok = ScenarioContextualizer(llm_ok, max_retries=0)
    result = ctx_ok.generate(DOMAIN_SAMPLE)
    assert count_ok[0] == 1, f"Expected 1 call, got {count_ok[0]}"
    assert "_validation_warnings" not in result
    print(f"  ✓ max_retries=0 with valid response: 1 call, success")

    # Invalid on only call → soft failure (1 call, no retry)
    always_invalid_dict = {**VALID_SCENARIO, "target_rows": 5}
    llm_bad, count_bad = _make_counting_llm(always_invalid_dict)
    ctx_bad = ScenarioContextualizer(llm_bad, max_retries=0)
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        result_bad = ctx_bad.generate(DOMAIN_SAMPLE)
    assert count_bad[0] == 1, (
        f"max_retries=0 should make exactly 1 call, got {count_bad[0]}"
    )
    assert "_validation_warnings" in result_bad, "Soft failure expected"
    print(f"  ✓ max_retries=0 with invalid response: 1 call, soft failure")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 17: Diversity tracker — accumulation and empty-field protection
# ================================================================
print("=" * 60)
print("Test 17: Diversity tracker — accumulation and empty-field skipping")
print("=" * 60)

try:
    # --- 17a: Default tracker starts empty ---
    ctx = ScenarioContextualizer(DummyLLM())
    assert ctx.diversity_tracker == {"used_titles": [], "used_contexts": []}, (
        f"Default tracker should be empty, got: {ctx.diversity_tracker}"
    )
    print(f"  ✓ Default tracker initializes empty")

    # --- 17b: External tracker shared correctly ---
    shared_tracker = {"used_titles": [], "used_contexts": []}
    llm1, _ = _make_counting_llm(VALID_SCENARIO.copy())
    ctx1 = ScenarioContextualizer(llm1, diversity_tracker=shared_tracker)
    ctx1.generate(DOMAIN_SAMPLE)

    assert len(shared_tracker["used_titles"]) == 1
    assert shared_tracker["used_titles"][0] == VALID_SCENARIO["scenario_title"]
    assert len(shared_tracker["used_contexts"]) == 1
    print(f"  ✓ After 1 generation: 1 title, 1 context in shared tracker")

    # --- 17c: Tracker accumulates across multiple generate() calls ---
    llm2, _ = _make_counting_llm(VALID_SCENARIO.copy())
    ctx2 = ScenarioContextualizer(llm2, diversity_tracker=shared_tracker)
    ctx2.generate(DOMAIN_SAMPLE)

    assert len(shared_tracker["used_titles"]) == 2, (
        f"Expected 2 titles after 2 generates, got {len(shared_tracker['used_titles'])}"
    )
    print(f"  ✓ After 2 generations: 2 titles accumulated in shared tracker")

    # --- 17d: Empty title/context fields are NOT added to tracker ---
    scenario_no_title = {**VALID_SCENARIO, "scenario_title": "", "data_context": ""}
    tracker_isolated = {"used_titles": [], "used_contexts": []}
    ctx3 = ScenarioContextualizer(DummyLLM(), diversity_tracker=tracker_isolated)
    ctx3._update_tracker(scenario_no_title)
    assert len(tracker_isolated["used_titles"]) == 0, (
        "Empty title should NOT be added to tracker"
    )
    assert len(tracker_isolated["used_contexts"]) == 0, (
        "Empty context should NOT be added to tracker"
    )
    print(f"  ✓ Empty title/context fields skipped by tracker")

    # --- 17e: Soft failure also updates tracker (valid dict response) ---
    tracker_soft = {"used_titles": [], "used_contexts": []}
    always_invalid = {**VALID_SCENARIO, "target_rows": 50000}
    llm_soft, count_soft = _make_counting_llm(always_invalid)
    ctx_soft = ScenarioContextualizer(
        llm_soft, diversity_tracker=tracker_soft, max_retries=0
    )
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        ctx_soft.generate(DOMAIN_SAMPLE)

    assert len(tracker_soft["used_titles"]) == 1, (
        "Soft failure should still update tracker with the title"
    )
    print(f"  ✓ Soft failure still adds title/context to tracker")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Test 18: deduplicate_scenario_records — scope and domain protection
# ================================================================
print("=" * 60)
print("Test 18: deduplicate_scenario_records — scope and domain protection")
print("=" * 60)

try:
    try:
        import pipeline.phase_1.scenario_contextualizer as _sc_module
        patch_target = "pipeline.phase_1.scenario_contextualizer._overlap_index_pairs"
    except ImportError:
        import phase_1.scenario_contextualizer as _sc_module
        patch_target = "phase_1.scenario_contextualizer._overlap_index_pairs"

    def make_record(domain_id, k, category_id, context):
        return {
            "domain_id": domain_id,
            "k": k,
            "category_id": category_id,
            "scenario": {"data_context": context},
        }

    CAT_A0 = make_record("dom_a", 0, 1, "Hospital ER wait time log.")
    CAT_A1 = make_record("dom_a", 1, 1, "Hospital ER waiting delay log.")
    CAT_B0 = make_record("dom_b", 0, 2, "Clinic triage delay log.")

    # --- 19a: Same category near-duplicates drop the later record.
    with patch(patch_target, return_value=[(0, 1, 0.93)]):
        result = deduplicate_scenario_records(
            [CAT_A0, CAT_A1, CAT_B0],
            threshold=0.85,
            scope="category",
            min_per_domain=1,
        )
    assert result == [CAT_A0, CAT_B0], (
        "Category-scope dedup should drop later near-duplicates within a category"
    )
    print(f"  ✓ Same category near-duplicates: later record dropped")

    # --- 19b: Different categories are deduped independently.
    with patch(patch_target, return_value=[]):
        result = deduplicate_scenario_records(
            [CAT_A0, CAT_B0],
            threshold=0.85,
            scope="category",
            min_per_domain=1,
        )
    assert result == [CAT_A0, CAT_B0], (
        "Category-scope dedup must not compare records from different categories"
    )
    print(f"  ✓ Cross-category records are kept")

    # --- 19c: Domain coverage is protected by min_per_domain=1.
    DOM_A0 = make_record("dom_a", 0, 1, "Hospital emergency queue log.")
    DOM_B0 = make_record("dom_b", 0, 1, "Clinic urgent-care queue log.")
    with patch(patch_target, return_value=[(0, 1, 0.94)]):
        result = deduplicate_scenario_records(
            [DOM_A0, DOM_B0],
            threshold=0.85,
            scope="category",
            min_per_domain=1,
        )
    assert result == [DOM_A0, DOM_B0], (
        "min_per_domain=1 should prevent deleting a domain's only scenario"
    )
    print(f"  ✓ Domain coverage protected when each domain has one record")

    # --- 19d: Scope='domain' compares only records inside each domain bucket.
    DOM_A1 = make_record("dom_a", 1, 1, "Hospital emergency queue operations.")
    with patch(patch_target, return_value=[(0, 1, 0.91)]):
        result = deduplicate_scenario_records(
            [DOM_A0, DOM_A1, DOM_B0],
            threshold=0.85,
            scope="domain",
            min_per_domain=1,
        )
    assert result == [DOM_A0, DOM_B0], (
        "Domain-scope dedup should drop only duplicates within the same domain"
    )
    print(f"  ✓ Domain scope only dedups inside domain buckets")

    # --- 19e: Scope='global' can compare all records, subject to domain protection.
    with patch(patch_target, return_value=[(0, 1, 0.96)]):
        result = deduplicate_scenario_records(
            [CAT_A0, CAT_A1, CAT_B0],
            threshold=0.85,
            scope="global",
            min_per_domain=1,
        )
    assert result == [CAT_A0, CAT_B0], (
        "Global-scope dedup should compare the whole record list"
    )
    print(f"  ✓ Global scope compares the whole pool")

    # --- 19f: Invalid scope is rejected.
    raised = False
    try:
        deduplicate_scenario_records([CAT_A0], scope="bad-scope")
    except ValueError as ve:
        raised = True
        assert "scope" in str(ve)
    assert raised, "Invalid dedup scope should raise ValueError"
    print(f"  ✓ Invalid scope rejected")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ================================================================
# Summary
# ================================================================
print("=" * 60)
print("All 19 tests passed! ✓")
print("=" * 60)
