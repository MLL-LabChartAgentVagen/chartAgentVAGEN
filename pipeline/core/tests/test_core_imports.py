"""
Smoke tests for pipeline/core/ surface.

Run from the pipeline/ directory:
    python -m core.tests.test_core_imports
"""


def test_utils():
    from core.utils import META_CATEGORIES, get_category_by_id
    assert len(META_CATEGORIES) == 30, f"Expected 30 categories, got {len(META_CATEGORIES)}"
    assert get_category_by_id(1) == "1 - Media & Entertainment"
    assert get_category_by_id(0) is None
    assert get_category_by_id(31) is None
    print("✓ utils OK")


def test_llm_client():
    from core.llm_client import (
        LLMClient, ParameterAdapter,
        ProviderCapabilities, get_provider_capabilities,
        PROVIDER_CAPABILITIES, MODEL_OVERRIDES,
    )
    # Check provider capabilities lookup
    caps = get_provider_capabilities("openai", "gpt-4")
    assert caps.supports_temperature is True
    assert caps.token_param_name == "max_completion_tokens"

    # Reasoning model override
    caps_o1 = get_provider_capabilities("openai", "o1-preview")
    assert caps_o1.supports_temperature is False
    assert caps_o1.is_reasoning_model is True

    # ParameterAdapter smoke test
    adapter = ParameterAdapter("openai", "gpt-4")
    msgs = [{"role": "user", "content": "hello"}]
    kwargs, modified = adapter.adapt_parameters(msgs, temperature=0.5, max_tokens=1024)
    assert kwargs["model"] == "gpt-4"
    assert kwargs["temperature"] == 0.5
    assert "max_completion_tokens" in kwargs
    print("✓ llm_client OK")


if __name__ == "__main__":
    test_utils()
    test_llm_client()
    print("\n🎉 core/ smoke tests passed!")
